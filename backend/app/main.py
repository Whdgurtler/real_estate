import csv
import io
from pathlib import Path

import httpx
from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import Base, create_database, create_session_factory
from .models import DataEvidence, Property, utc_now
from .schemas import PropertyCreate, PropertyRead, UnderwritingAssumptions
from .sources import fetch_acs_population, source_catalog
from .underwriting import analyze_property


EVIDENCE_METRICS = {
    "asking_price",
    "estimated_repairs",
    "annual_property_tax",
    "assessed_value",
    "tax_rate_percent",
    "annual_insurance_estimate",
    "expected_market_rent_monthly",
    "hud_fmr_monthly",
    "pha_payment_standard_monthly",
    "pha_program_status",
    "voucher_waitlist_status",
    "open_voucher_count",
    "population_growth_percent",
    "violent_crime_rate_per_100k",
}
MAX_IMPORT_BYTES = 5_000_000
MAX_IMPORT_ROWS = 5_000


def _record_evidence(property_record, values, source_name, source_url, confidence="user_provided"):
    if not source_name:
        source_name = "User-provided"
    for metric in EVIDENCE_METRICS:
        value = values.get(metric)
        if value is None:
            continue
        property_record.evidence.append(
            DataEvidence(
                metric=metric,
                value=str(value),
                source_name=source_name,
                source_url=source_url,
                confidence=confidence,
                observed_at=utc_now(),
            )
        )


def create_app(database_url: str | None = None):
    engine = create_database(database_url)
    Base.metadata.create_all(bind=engine)
    session_factory = create_session_factory(engine)

    application = FastAPI(
        title="Property Acquisition & Underwriting",
        version="0.1.0",
        description="A source-aware workspace for property leads and rental underwriting.",
    )
    application.state.engine = engine
    application.state.session_factory = session_factory

    origins = [
        origin.strip()
        for origin in __import__("os").getenv(
            "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )

    def get_db(request: Request):
        session = request.app.state.session_factory()
        try:
            yield session
        finally:
            session.close()

    @application.get("/api/health")
    def health():
        return {"status": "ok"}

    @application.get("/api/data-sources")
    def data_sources():
        return source_catalog()

    @application.get("/api/properties", response_model=list[PropertyRead])
    def list_properties(
        state: str | None = Query(default=None, min_length=2, max_length=2),
        source_type: str | None = None,
        search: str | None = Query(default=None, max_length=200),
        limit: int = Query(default=250, ge=1, le=1000),
        offset: int = Query(default=0, ge=0),
        db: Session = Depends(get_db),
    ):
        query = db.query(Property)
        if state:
            query = query.filter(Property.state == state.strip().upper())
        if source_type:
            query = query.filter(Property.source_type == source_type)
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                Property.address.ilike(pattern)
                | Property.city.ilike(pattern)
                | Property.county.ilike(pattern)
                | Property.zip_code.ilike(pattern)
            )
        return query.order_by(Property.updated_at.desc(), Property.id.desc()).offset(offset).limit(limit).all()

    @application.post("/api/properties", response_model=PropertyRead, status_code=201)
    def create_property(data: PropertyCreate, db: Session = Depends(get_db)):
        values = data.model_dump()
        property_record = Property(**values)
        _record_evidence(property_record, values, data.source_name, data.source_url)
        db.add(property_record)
        db.commit()
        db.refresh(property_record)
        return property_record

    @application.get("/api/properties/{property_id}", response_model=PropertyRead)
    def get_property(property_id: int, db: Session = Depends(get_db)):
        property_record = db.get(Property, property_id)
        if property_record is None:
            raise HTTPException(status_code=404, detail="Property not found")
        return property_record

    @application.post("/api/properties/import")
    async def import_properties(request: Request, db: Session = Depends(get_db)):
        body = await request.body()
        if not body:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        if len(body) > MAX_IMPORT_BYTES:
            raise HTTPException(status_code=413, detail="CSV import exceeds the 5 MB limit")
        try:
            text = body.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from error

        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise HTTPException(status_code=400, detail="CSV header row is required")

        rows = []
        errors = []
        for line_number, row in enumerate(reader, start=2):
            if len(rows) >= MAX_IMPORT_ROWS:
                raise HTTPException(status_code=413, detail=f"CSV import exceeds {MAX_IMPORT_ROWS} rows")
            if not any(value and value.strip() for value in row.values() if isinstance(value, str)):
                continue
            try:
                rows.append(PropertyCreate.model_validate(row))
            except Exception as error:
                errors.append({"line": line_number, "error": str(error)})
        if errors:
            raise HTTPException(status_code=422, detail={"message": "CSV validation failed", "rows": errors})
        if not rows:
            raise HTTPException(status_code=400, detail="CSV contains no property rows")

        created = []
        for data in rows:
            values = data.model_dump()
            property_record = Property(**values)
            _record_evidence(property_record, values, data.source_name, data.source_url)
            db.add(property_record)
            created.append(property_record)
        db.commit()
        return {"imported": len(created), "property_ids": [item.id for item in created]}

    @application.post("/api/properties/{property_id}/underwriting")
    def get_underwriting(
        property_id: int,
        assumptions: UnderwritingAssumptions = Body(default=UnderwritingAssumptions()),
        db: Session = Depends(get_db),
    ):
        property_record = db.get(Property, property_id)
        if property_record is None:
            raise HTTPException(status_code=404, detail="Property not found")
        return analyze_property(property_record, assumptions)

    @application.post("/api/properties/{property_id}/enrich/census", response_model=PropertyRead)
    async def enrich_census(property_id: int, db: Session = Depends(get_db)):
        property_record = db.get(Property, property_id)
        if property_record is None:
            raise HTTPException(status_code=404, detail="Property not found")
        if not property_record.county_fips:
            raise HTTPException(
                status_code=422,
                detail="A five-digit county FIPS code is required before Census enrichment.",
            )
        try:
            result = await fetch_acs_population(
                state_fips=property_record.county_fips[:2],
                county_fips=property_record.county_fips[2:],
            )
        except (httpx.HTTPError, ValueError) as error:
            raise HTTPException(
                status_code=502,
                detail=f"Census ACS enrichment failed: {error}",
            ) from error

        property_record.county = property_record.county or result["county_name"].rsplit(", ", 1)[0]
        property_record.population_current = result["population_current"]
        property_record.population_previous = result["population_previous"]
        property_record.population_growth_percent = result["population_growth_percent"]
        property_record.population_data_year = result["current_year"]
        property_record.updated_at = utc_now()
        evidence_values = {
            "population_growth_percent": result["population_growth_percent"],
            "population_current": result["population_current"],
            "population_previous": result["population_previous"],
        }
        _record_evidence(
            property_record,
            evidence_values,
            result["source_name"],
            result["source_url"],
            confidence="official_estimate",
        )
        db.commit()
        db.refresh(property_record)
        return property_record

    @application.get("/api/portfolio/summary")
    def portfolio_summary(db: Session = Depends(get_db)):
        properties = db.query(Property).all()
        by_state = {}
        by_source_type = {}
        for item in properties:
            by_state[item.state] = by_state.get(item.state, 0) + 1
            by_source_type[item.source_type] = by_source_type.get(item.source_type, 0) + 1
        return {
            "property_count": len(properties),
            "states": by_state,
            "lead_types": by_source_type,
            "insurance_missing": sum(item.annual_insurance_estimate is None for item in properties),
            "voucher_counts_unknown": sum(item.open_voucher_count is None for item in properties),
        }

    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend_dist.is_dir():
        application.mount(
            "/assets",
            StaticFiles(directory=frontend_dist / "assets"),
            name="assets",
        )

        @application.get("/", include_in_schema=False)
        def frontend():
            return FileResponse(frontend_dist / "index.html")

    else:

        @application.get("/", include_in_schema=False)
        def api_info():
            return {
                "name": "Property Acquisition & Underwriting",
                "api_docs": "/docs",
                "frontend": "Run the frontend Vite development server from the frontend directory.",
            }

    return application


app = create_app()
