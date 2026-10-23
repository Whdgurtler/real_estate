import csv
import io
import json
import math
import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import ValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from .automation import (
    create_sync_scheduler,
    data_feed_config,
    enqueue_manual_sync,
    schedule_settings,
    serialize_data_feed,
)
from .db import Base, create_database, create_session_factory, ensure_postgis
from .jurisdictions import (
    PRIORITY_STATES,
    county_jurisdictions,
    county_source_links,
)
from .models import DataEvidence, DataFeed, DataFeedRecord, Property, SyncRun, utc_now
from .schemas import (
    PRIORITY_COUNTY_FIPS,
    DataFeedCreate,
    DataFeedEnabledUpdate,
    PropertyCreate,
    PropertyRead,
    UnderwritingAssumptions,
)
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
    "population_current",
    "population_previous",
    "violent_crime_rate_per_100k",
}
METRIC_SOURCE_GROUPS = {
    "asking_price": "property",
    "estimated_repairs": "property",
    "annual_property_tax": "tax",
    "assessed_value": "tax",
    "tax_rate_percent": "tax",
    "annual_insurance_estimate": "insurance",
    "expected_market_rent_monthly": "market_rent",
    "hud_fmr_monthly": "hud_fmr",
    "pha_payment_standard_monthly": "pha",
    "pha_program_status": "pha",
    "voucher_waitlist_status": "pha",
    "open_voucher_count": "pha",
    "population_growth_percent": "neighborhood",
    "population_current": "neighborhood",
    "population_previous": "neighborhood",
    "violent_crime_rate_per_100k": "neighborhood",
}
MAX_IMPORT_BYTES = 5_000_000
MAX_IMPORT_ROWS = 5_000


def _record_evidence(property_record, values, source_name, source_url, confidence="user_provided"):
    source_metadata = values.get("source_metadata") or {}
    for metric in EVIDENCE_METRICS:
        value = values.get(metric)
        if value is None:
            continue
        group = METRIC_SOURCE_GROUPS[metric]
        metric_source = source_metadata.get(group)
        if confidence != "user_provided":
            evidence_source_name = source_name or "External source"
            evidence_source_url = source_url
            evidence_confidence = confidence
        elif metric_source:
            evidence_source_name = metric_source["source_name"]
            evidence_source_url = metric_source.get("source_url")
            evidence_confidence = metric_source.get("confidence", "user_provided")
        elif group == "property" and source_name:
            evidence_source_name = source_name
            evidence_source_url = source_url
            evidence_confidence = "user_provided"
        else:
            evidence_source_name = "User-provided (source not specified)"
            evidence_source_url = None
            evidence_confidence = "user_provided"
        property_record.evidence.append(
            DataEvidence(
                metric=metric,
                value=str(value),
                source_name=evidence_source_name,
                source_url=evidence_source_url,
                confidence=evidence_confidence,
                observed_at=utc_now(),
            )
        )


def create_app(database_url: str | None = None):
    engine = create_database(database_url)
    Base.metadata.create_all(bind=engine)
    ensure_postgis(engine)
    session_factory = create_session_factory(engine)
    daily_sync_enabled, daily_sync_time, daily_sync_timezone = schedule_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        scheduler = create_sync_scheduler(
            session_factory,
            daily_sync_enabled,
            daily_sync_time,
            daily_sync_timezone,
        )
        scheduler.start()
        application.state.sync_scheduler = scheduler
        try:
            yield
        finally:
            scheduler.shutdown(wait=False)

    application = FastAPI(
        title="Property Acquisition & Underwriting",
        version="0.1.0",
        description="A source-aware workspace for property leads and rental underwriting.",
        lifespan=lifespan,
    )
    application.state.engine = engine
    application.state.session_factory = session_factory
    application.state.daily_sync_enabled = daily_sync_enabled
    application.state.daily_sync_time = daily_sync_time
    application.state.daily_sync_timezone = daily_sync_timezone

    origins = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
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

    @application.get("/api/data-feeds")
    def list_data_feeds(db: Session = Depends(get_db)):
        feeds = db.query(DataFeed).order_by(DataFeed.created_at.desc(), DataFeed.id.desc()).all()
        return [serialize_data_feed(feed) for feed in feeds]

    @application.get("/api/jurisdictions")
    def list_priority_jurisdictions(
        state: str | None = Query(default=None, min_length=2, max_length=2),
        db: Session = Depends(get_db),
    ):
        normalized_state = state.strip().upper() if state else None
        if normalized_state and normalized_state not in PRIORITY_STATES:
            raise HTTPException(
                status_code=422,
                detail="State must be one of the priority states: AR, AL, OH, MO, TX.",
            )
        county_rows = county_jurisdictions()
        if normalized_state:
            county_rows = [
                row for row in county_rows if row["state"] == normalized_state
            ]
        scoped_feeds = (
            db.query(DataFeed)
            .filter(DataFeed.county_fips.isnot(None))
            .all()
        )
        feeds_by_county = {}
        for feed in scoped_feeds:
            feeds_by_county.setdefault(feed.county_fips, []).append(
                {
                    "id": feed.id,
                    "name": feed.name,
                    "category": feed.source_category,
                    "enabled": feed.enabled,
                }
            )
        for county in county_rows:
            configured = feeds_by_county.get(county["county_fips"], [])
            county["sources"] = county_source_links(
                county["state"],
                county["county"],
                county["county_fips"],
            )
            for category, source in county["sources"].items():
                matches = [feed for feed in configured if feed["category"] == category]
                source["feeds"] = matches
                source["configured"] = any(feed["enabled"] for feed in matches)
                if matches and not source["configured"]:
                    source["status"] = "feed_paused"
                elif source["configured"]:
                    source["status"] = "feed_configured"
        return {
            "county_equivalent_count": len(county_rows),
            "jurisdictions": county_rows,
        }

    @application.post("/api/data-feeds", status_code=201)
    def create_data_feed(data: DataFeedCreate, db: Session = Depends(get_db)):
        feed = DataFeed(
            name=data.name,
            connector=data.connector,
            source_category=data.source_category,
            source_type=data.source_type,
            county_fips=data.county_fips,
            config=data_feed_config(data),
            enabled=data.enabled,
        )
        db.add(feed)
        db.commit()
        db.refresh(feed)
        return serialize_data_feed(feed)

    @application.patch("/api/data-feeds/{feed_id}")
    def update_data_feed(
        feed_id: int,
        data: DataFeedEnabledUpdate,
        db: Session = Depends(get_db),
    ):
        feed = db.get(DataFeed, feed_id)
        if feed is None:
            raise HTTPException(status_code=404, detail="Data feed not found")
        feed.enabled = data.enabled
        feed.updated_at = utc_now()
        db.commit()
        db.refresh(feed)
        return serialize_data_feed(feed)

    @application.delete("/api/data-feeds/{feed_id}", status_code=204)
    def delete_data_feed(feed_id: int, db: Session = Depends(get_db)):
        feed = db.get(DataFeed, feed_id)
        if feed is None:
            raise HTTPException(status_code=404, detail="Data feed not found")
        db.query(DataFeedRecord).filter(DataFeedRecord.data_feed_id == feed_id).delete(
            synchronize_session=False
        )
        db.delete(feed)
        db.commit()
        return None

    @application.get("/api/sync/status")
    def sync_status(request: Request, db: Session = Depends(get_db)):
        scheduler = getattr(request.app.state, "sync_scheduler", None)
        job = scheduler.get_job("daily-property-data-sync") if scheduler else None
        runs = db.query(SyncRun).order_by(SyncRun.started_at.desc(), SyncRun.id.desc()).limit(20)
        return {
            "enabled": request.app.state.daily_sync_enabled,
            "daily_time": request.app.state.daily_sync_time,
            "timezone": request.app.state.daily_sync_timezone,
            "next_run_at": job.next_run_time.isoformat() if job and job.next_run_time else None,
            "runs": [
                {
                    "id": run.id,
                    "trigger": run.trigger,
                    "status": run.status,
                    "scheduled_date": run.scheduled_date.isoformat() if run.scheduled_date else None,
                    "started_at": run.started_at.isoformat(),
                    "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                    "source_results": run.source_results or [],
                    "error": run.error,
                }
                for run in runs
            ],
        }

    @application.post("/api/sync/run", status_code=202)
    def run_sync_now(request: Request):
        scheduler = getattr(request.app.state, "sync_scheduler", None)
        if scheduler is None or not scheduler.running:
            raise HTTPException(status_code=503, detail="The sync executor is not running.")
        run_id = enqueue_manual_sync(scheduler, request.app.state.session_factory)
        if run_id is None:
            raise HTTPException(
                status_code=409,
                detail="A property data sync is already queued or running.",
            )
        return {"run_id": run_id, "status": "queued"}

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

    @application.get("/api/properties/nearby")
    def nearby_properties(
        latitude: float = Query(ge=-90, le=90),
        longitude: float = Query(ge=-180, le=180),
        radius_km: float = Query(default=25, gt=0, le=500),
        limit: int = Query(default=100, ge=1, le=500),
        db: Session = Depends(get_db),
    ):
        if db.bind.dialect.name == "postgresql":
            rows = db.execute(
                text(
                    """
                    SELECT id,
                        ST_Distance(
                            location::geography,
                            ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography
                        ) / 1000 AS distance_km
                    FROM properties
                    WHERE location IS NOT NULL
                      AND ST_DWithin(
                          location::geography,
                          ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
                          :radius_meters
                      )
                    ORDER BY distance_km
                    LIMIT :limit
                    """
                ),
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius_meters": radius_km * 1000,
                    "limit": limit,
                },
            ).all()
            distances = {row.id: row.distance_km for row in rows}
            property_rows = (
                db.query(Property).filter(Property.id.in_(distances)).all()
                if distances
                else []
            )
        else:
            def distance_km(property_record):
                lat1, lat2 = math.radians(latitude), math.radians(property_record.latitude)
                lat_delta = lat2 - lat1
                lon_delta = math.radians(property_record.longitude - longitude)
                haversine = (
                    math.sin(lat_delta / 2) ** 2
                    + math.cos(lat1)
                    * math.cos(lat2)
                    * math.sin(lon_delta / 2) ** 2
                )
                return 6371 * 2 * math.asin(math.sqrt(haversine))

            distances = {}
            property_rows = []
            candidates = (
                db.query(Property)
                .filter(Property.latitude.is_not(None), Property.longitude.is_not(None))
                .all()
            )
            for property_record in candidates:
                distance = distance_km(property_record)
                if distance <= radius_km:
                    distances[property_record.id] = distance
                    property_rows.append(property_record)
            property_rows.sort(key=lambda item: distances[item.id])
            property_rows = property_rows[:limit]

        property_rows.sort(key=lambda item: distances[item.id])
        return [
            {"property": item, "distance_km": round(distances[item.id], 2)}
            for item in property_rows
        ]

    @application.get("/api/properties/{property_id}", response_model=PropertyRead)
    def get_property(property_id: int, db: Session = Depends(get_db)):
        property_record = db.get(Property, property_id)
        if property_record is None:
            raise HTTPException(status_code=404, detail="Property not found")
        return property_record

    @application.put("/api/properties/{property_id}", response_model=PropertyRead)
    def update_property(
        property_id: int,
        data: PropertyCreate,
        db: Session = Depends(get_db),
    ):
        property_record = db.get(Property, property_id)
        if property_record is None:
            raise HTTPException(status_code=404, detail="Property not found")
        values = data.model_dump(exclude_unset=True)
        for key, value in values.items():
            setattr(property_record, key, value)
        property_record.updated_at = utc_now()
        _record_evidence(property_record, values, data.source_name, data.source_url)
        db.commit()
        db.refresh(property_record)
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
            if line_number - 1 > MAX_IMPORT_ROWS:
                raise HTTPException(status_code=413, detail=f"CSV import exceeds {MAX_IMPORT_ROWS} rows")
            if not any(value and value.strip() for value in row.values() if isinstance(value, str)):
                continue
            try:
                normalized = {
                    key: value.strip() if isinstance(value, str) else value
                    for key, value in row.items()
                    if key is not None
                }
                normalized = {
                    key: None if value == "" else value
                    for key, value in normalized.items()
                }
                if normalized.get("source_metadata") is not None:
                    normalized["source_metadata"] = json.loads(normalized["source_metadata"])
                else:
                    normalized.pop("source_metadata", None)
                rows.append(PropertyCreate.model_validate(normalized))
            except (ValidationError, json.JSONDecodeError) as error:
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
