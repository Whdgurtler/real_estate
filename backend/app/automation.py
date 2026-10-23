import asyncio
import hashlib
import ipaddress
import logging
import os
import re
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from .models import DataEvidence, DataFeed, DataFeedRecord, Property, SyncRun, utc_now
from .schemas import DataFeedCreate, PropertyCreate
from .sources import fetch_acs_population


LOGGER = logging.getLogger(__name__)
HUD_FMR_ENDPOINT = "https://www.huduser.gov/hudapi/public/fmr"
MAX_RESPONSE_BYTES = 10_000_000
MAX_AUTOMATED_COUNTIES = 1000
MAX_HUD_ZIP_BEDROOM_GROUPS = 500
STATE_FIPS = {"AL": "01", "AR": "05", "MO": "29", "OH": "39", "TX": "48"}
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
EVIDENCE_METRICS = frozenset(METRIC_SOURCE_GROUPS)
INTEGER_FIELDS = frozenset(
    {
        "bedrooms",
        "square_feet",
        "year_built",
        "open_voucher_count",
        "population_current",
        "population_previous",
    }
)
NUMERIC_FIELDS = frozenset(
    {
        "latitude",
        "longitude",
        "asking_price",
        "estimated_repairs",
        "bathrooms",
        "annual_property_tax",
        "assessed_value",
        "tax_rate_percent",
        "annual_insurance_estimate",
        "expected_market_rent_monthly",
        "hud_fmr_monthly",
        "pha_payment_standard_monthly",
        "population_growth_percent",
        "violent_crime_rate_per_100k",
    }
)
def data_feed_source_url(feed: DataFeed | dict) -> str:
    connector = feed.connector if isinstance(feed, DataFeed) else feed["connector"]
    config = feed.config if isinstance(feed, DataFeed) else feed.get("config", feed)
    if connector == "socrata":
        return f"https://{config['domain']}/d/{config['dataset_id']}"
    if connector == "arcgis":
        return config["query_url"]
    return config["query_url"]


def serialize_data_feed(feed: DataFeed) -> dict:
    config = dict(feed.config or {})
    return {
        "id": feed.id,
        "name": feed.name,
        "connector": feed.connector,
        "target": config.get("target", "property_leads"),
        "source_category": feed.source_category,
        "source_type": feed.source_type,
        "county_fips": feed.county_fips,
        "enabled": feed.enabled,
        "source_url": data_feed_source_url(feed),
        "field_mapping": config.get("field_mapping", {}),
        "max_records": config.get("max_records", 1000),
        "created_at": feed.created_at,
        "updated_at": feed.updated_at,
    }


def data_feed_config(data: DataFeedCreate) -> dict:
    return data.model_dump(
        exclude={
            "name",
            "connector",
            "source_category",
            "source_type",
            "county_fips",
            "enabled",
            "confidence",
        },
        mode="json",
    ) | {"confidence": data.confidence}


def schedule_settings() -> tuple[bool, str, str]:
    enabled_value = os.getenv("DAILY_SYNC_ENABLED", "true").strip().lower()
    if enabled_value not in {"true", "1", "yes", "false", "0", "no"}:
        raise ValueError("DAILY_SYNC_ENABLED must be true or false")
    enabled = enabled_value in {"true", "1", "yes"}
    daily_time = os.getenv("DAILY_SYNC_TIME", "02:00").strip()
    try:
        datetime.strptime(daily_time, "%H:%M")
    except ValueError as error:
        raise ValueError("DAILY_SYNC_TIME must use 24-hour HH:MM format") from error
    timezone_name = os.getenv("DAILY_SYNC_TIMEZONE", "America/Chicago").strip()
    try:
        ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as error:
        raise ValueError(f"Unknown DAILY_SYNC_TIMEZONE: {timezone_name}") from error
    return enabled, daily_time, timezone_name


def create_sync_scheduler(
    session_factory: sessionmaker,
    enabled: bool,
    daily_time: str,
    timezone_name: str,
) -> BackgroundScheduler:
    timezone_info = ZoneInfo(timezone_name)
    scheduler = BackgroundScheduler(timezone=timezone_info)
    if enabled:
        hour, minute = (int(part) for part in daily_time.split(":"))
        scheduler.add_job(
            run_scheduled_sync,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone_info),
            args=[session_factory, timezone_name],
            id="daily-property-data-sync",
            name="Daily property data sync",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
    return scheduler


def create_sync_run(
    session_factory: sessionmaker,
    trigger: str,
    scheduled_date: date | None = None,
) -> int | None:
    session = session_factory()
    try:
        active_run = (
            session.query(SyncRun)
            .filter(SyncRun.active_slot == "property-data-sync")
            .first()
        )
        if active_run is not None:
            started_at = active_run.started_at
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
            if utc_now() - started_at > timedelta(hours=6):
                active_run.status = "failed"
                active_run.error = "Sync was marked failed after exceeding the six-hour execution limit."
                active_run.completed_at = utc_now()
                active_run.active_slot = None
                session.commit()
        run = SyncRun(
            trigger=trigger,
            status="queued",
            scheduled_date=scheduled_date,
            active_slot="property-data-sync",
            started_at=utc_now(),
            source_results=[],
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        return run.id
    except IntegrityError:
        session.rollback()
        return None
    finally:
        session.close()


def run_scheduled_sync(session_factory: sessionmaker, timezone_name: str) -> None:
    run_date = datetime.now(ZoneInfo(timezone_name)).date()
    run_id = create_sync_run(session_factory, "scheduled", run_date)
    if run_id is None:
        LOGGER.info("Daily sync for %s was already claimed or another sync is active", run_date)
        return
    execute_sync_job(session_factory, run_id)


def enqueue_manual_sync(
    scheduler: BackgroundScheduler,
    session_factory: sessionmaker,
) -> int | None:
    run_id = create_sync_run(session_factory, "manual")
    if run_id is None:
        return None
    try:
        scheduler.add_job(
            execute_sync_job,
            trigger="date",
            run_date=datetime.now(timezone.utc) + timedelta(seconds=1),
            args=[session_factory, run_id],
            id=f"manual-property-data-sync-{run_id}",
            name=f"Manual property data sync {run_id}",
            max_instances=1,
        )
    except Exception:
        mark_sync_run_failed(session_factory, run_id, "Could not queue the sync executor.")
        raise
    return run_id


def mark_sync_run_failed(session_factory: sessionmaker, run_id: int, message: str) -> None:
    session = session_factory()
    try:
        run = session.get(SyncRun, run_id)
        if run is not None:
            run.status = "failed"
            run.error = message
            run.completed_at = utc_now()
            run.active_slot = None
            session.commit()
    finally:
        session.close()


def execute_sync_job(session_factory: sessionmaker, run_id: int) -> None:
    session = session_factory()
    try:
        run = session.get(SyncRun, run_id)
        if run is None or run.status != "queued":
            return
        run.status = "running"
        session.commit()
    finally:
        session.close()

    try:
        source_results = asyncio.run(sync_all_sources(session_factory))
        errors = [
            item.get("error")
            for item in source_results
            if item.get("status") == "failed" and item.get("error")
        ]
        failed_count = sum(item.get("status") == "failed" for item in source_results)
        partial_count = sum(item.get("status") == "partial" for item in source_results)
        session = session_factory()
        try:
            run = session.get(SyncRun, run_id)
            if run is not None:
                run.source_results = source_results
                run.error = "\n".join(errors)[:5000] or None
                run.status = (
                    "failed"
                    if source_results and failed_count == len(source_results)
                    else "partial"
                    if failed_count or partial_count
                    else "success"
                )
                run.completed_at = utc_now()
                run.active_slot = None
                session.commit()
        finally:
            session.close()
    except Exception as error:
        LOGGER.exception("Property data sync %s failed", run_id)
        mark_sync_run_failed(session_factory, run_id, str(error)[:5000])


async def sync_all_sources(session_factory: sessionmaker) -> list[dict]:
    session = session_factory()
    try:
        feeds = [
            {
                "id": feed.id,
                "name": feed.name,
                "connector": feed.connector,
                "source_category": feed.source_category,
                "county_fips": feed.county_fips,
                "source_type": feed.source_type,
                "config": dict(feed.config or {}),
            }
            for feed in session.query(DataFeed).filter(DataFeed.enabled.is_(True)).all()
        ]
    finally:
        session.close()

    results = []
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        follow_redirects=False,
        headers={"User-Agent": "Groundwork-Property-Data/1.0"},
    ) as client:
        for feed in feeds:
            try:
                results.append(await sync_configured_feed(session_factory, client, feed))
            except Exception as error:
                LOGGER.exception("Data feed %s (%s) failed", feed["id"], feed["name"])
                results.append(
                    {
                        "source_id": feed["id"],
                        "source_name": feed["name"],
                        "source_category": feed["source_category"],
                        "county_fips": feed["county_fips"],
                        "status": "failed",
                        "inserted": 0,
                        "updated": 0,
                        "skipped": 0,
                        "error": str(error)[:1000],
                    }
                )
        try:
            results.append(await sync_census_population(session_factory, client))
        except Exception as error:
            LOGGER.exception("Scheduled Census enrichment failed")
            results.append(
                {
                    "source_id": "census_acs",
                    "source_name": "U.S. Census Bureau ACS",
                    "status": "failed",
                    "inserted": 0,
                    "updated": 0,
                    "skipped": 0,
                    "error": str(error)[:1000],
                }
            )
        try:
            results.append(await sync_hud_fmr(session_factory, client))
        except Exception as error:
            LOGGER.exception("Scheduled HUD Fair Market Rent enrichment failed")
            results.append(
                {
                    "source_id": "hud_fmr",
                    "source_name": "HUD Fair Market Rents",
                    "status": "failed",
                    "inserted": 0,
                    "updated": 0,
                    "skipped": 0,
                    "error": str(error)[:1000],
                }
            )
    return results


async def sync_configured_feed(
    session_factory: sessionmaker,
    client: httpx.AsyncClient,
    feed: dict,
) -> dict:
    records = await fetch_feed_records(client, feed)
    source_url = data_feed_source_url(feed)
    if feed["config"].get("target") == "property_enrichment":
        return sync_property_enrichment_feed(
            session_factory,
            feed,
            source_url,
            records,
        )
    session = session_factory()
    inserted = updated = skipped = 0
    warnings = []
    try:
        config = feed["config"]
        for index, row in enumerate(records):
            try:
                data = normalize_feed_record(row, feed)
                external_value = (
                    _lookup_source_field(row, config.get("record_id_field"))
                    if config.get("record_id_field")
                    else None
                )
                stable_value = (
                    str(external_value)
                    if external_value not in (None, "")
                    else "|".join(
                        [
                            data.address.casefold(),
                            data.city.casefold(),
                            data.state,
                        ]
                    )
                )
                external_key = hashlib.sha256(stable_value.encode("utf-8")).hexdigest()
                linked_record = (
                    session.query(DataFeedRecord)
                    .filter(
                        DataFeedRecord.data_feed_id == feed["id"],
                        DataFeedRecord.external_key == external_key,
                    )
                    .first()
                )
                property_record = (
                    session.get(Property, linked_record.property_id)
                    if linked_record is not None
                    else None
                )
                scoped_county_fips = feed.get("county_fips")
                if (
                    property_record is not None
                    and scoped_county_fips
                    and property_record.county_fips
                    and property_record.county_fips != scoped_county_fips
                ):
                    raise ValueError(
                        "matched property county FIPS does not match this feed's county scope"
                    )
                is_new_property = property_record is None
                if property_record is None:
                    property_record = (
                        session.query(Property)
                        .filter(
                            func.lower(Property.address) == data.address.casefold(),
                            func.lower(Property.city) == data.city.casefold(),
                            Property.state == data.state,
                        )
                        .first()
                    )
                    is_new_property = property_record is None
                values = data.model_dump(
                    exclude={"source_name", "source_url", "source_metadata"}
                )
                if is_new_property:
                    property_record = Property(**values)
                    property_record.source_name = feed["name"]
                    property_record.source_url = source_url
                    session.add(property_record)
                    session.flush()
                    inserted += 1
                else:
                    updated_fields = False
                    for field, value in values.items():
                        if value is None:
                            continue
                        previous_value = getattr(property_record, field)
                        can_update = (
                            field in {"address", "city", "state", "source_type"}
                            or previous_value is None
                            or linked_record is not None
                        )
                        if not can_update:
                            continue
                        if field in EVIDENCE_METRICS:
                            _record_metric(
                                property_record,
                                field,
                                value,
                                feed["name"],
                                source_url,
                                config.get("confidence", "official_record"),
                            )
                        elif previous_value != value:
                            setattr(property_record, field, value)
                        updated_fields = updated_fields or previous_value != value
                    if updated_fields:
                        property_record.updated_at = utc_now()
                        updated += 1

                for field, value in values.items():
                    if field in EVIDENCE_METRICS and value is not None:
                        current_value = getattr(property_record, field)
                        if current_value == value:
                            _record_metric(
                                property_record,
                                field,
                                value,
                                feed["name"],
                                source_url,
                                config.get("confidence", "official_record"),
                            )

                if linked_record is None:
                    session.add(
                        DataFeedRecord(
                            data_feed_id=feed["id"],
                            property_id=property_record.id,
                            external_key=external_key,
                        )
                    )
                else:
                    linked_record.last_seen_at = utc_now()
            except (ValueError, TypeError, KeyError) as error:
                skipped += 1
                if len(warnings) < 10:
                    warnings.append(f"Record {index + 1}: {error}")
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    return {
        "source_id": feed["id"],
        "source_name": feed["name"],
        "source_category": feed.get("source_category", "other"),
        "county_fips": feed.get("county_fips"),
        "status": "partial" if skipped else "success",
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "warnings": warnings,
    }


def sync_property_enrichment_feed(
    session_factory: sessionmaker,
    feed: dict,
    source_url: str,
    records: list[dict],
) -> dict:
    config = feed["config"]
    session = session_factory()
    updated = skipped = 0
    warnings = []
    try:
        for index, row in enumerate(records):
            try:
                values = {}
                for property_field, source_field in config["field_mapping"].items():
                    raw_value = _lookup_source_field(row, source_field)
                    if raw_value is not None:
                        value = _coerce_property_value(property_field, raw_value)
                        if value is not None:
                            values[property_field] = value
                county_fips = values.get("county_fips")
                if county_fips is None:
                    county_fips = feed.get("county_fips")
                if county_fips is not None:
                    county_fips = re.sub(r"\D", "", str(county_fips)).zfill(5)
                    if not re.fullmatch(r"\d{5}", county_fips):
                        raise ValueError("county_fips must contain five digits")
                zip_code = values.get("zip_code")
                if zip_code is not None:
                    zip_match = re.match(r"^\d{5}", str(zip_code))
                    if not zip_match:
                        raise ValueError("zip_code must begin with five digits")
                    zip_code = zip_match.group(0)
                state = values.get("state")
                if state is not None:
                    state = str(state).strip().upper()
                    if not re.fullmatch(r"[A-Z]{2}", state):
                        raise ValueError("state must be a two-letter abbreviation")
                if county_fips and state and STATE_FIPS.get(state) != county_fips[:2]:
                    raise ValueError("county FIPS state prefix does not match the record's state")
                if county_fips:
                    matches = (
                        session.query(Property)
                        .filter(Property.county_fips == county_fips)
                        .all()
                    )
                else:
                    matches = []
                if not matches and zip_code and state:
                    matches = (
                        session.query(Property)
                        .filter(Property.zip_code.like(f"{zip_code}%"), Property.state == state)
                        .all()
                    )
                if not matches:
                    county = values.get("county")
                    if not county or not state:
                        if not county_fips and not (zip_code and state):
                            raise ValueError(
                                "Map county_fips, zip_code plus state, or county plus state to match properties"
                            )
                        matches = []
                    else:
                        matches = (
                            session.query(Property)
                            .filter(
                                func.lower(Property.county) == str(county).casefold(),
                                Property.state == state,
                            )
                            .all()
                        )
                metric_fields = set(config["field_mapping"]) - {
                    "county_fips",
                    "zip_code",
                    "state",
                    "county",
                }
                if not matches:
                    skipped += 1
                    if len(warnings) < 10:
                        warnings.append(f"Record {index + 1}: no properties matched its geography")
                    continue
                for property_record in matches:
                    property_changed = False
                    for metric in metric_fields:
                        value = values.get(metric)
                        if value is None:
                            continue
                        previous_value = getattr(property_record, metric)
                        source_metadata = property_record.source_metadata or {}
                        group = METRIC_SOURCE_GROUPS[metric]
                        owned_by_feed = (
                            (source_metadata.get(group) or {}).get("source_name")
                            == feed["name"]
                        )
                        if previous_value is None or owned_by_feed or previous_value == value:
                            property_changed = _record_metric(
                                property_record,
                                metric,
                                value,
                                feed["name"],
                                source_url,
                                config.get("confidence", "official_record"),
                            ) or property_changed
                    if property_changed:
                        property_record.updated_at = utc_now()
                        updated += 1
            except (ValueError, TypeError, KeyError) as error:
                skipped += 1
                if len(warnings) < 10:
                    warnings.append(f"Record {index + 1}: {error}")
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    return {
        "source_id": feed["id"],
        "source_name": feed["name"],
        "source_category": feed.get("source_category", "other"),
        "county_fips": feed.get("county_fips"),
        "status": "partial" if skipped else "success",
        "inserted": 0,
        "updated": updated,
        "skipped": skipped,
        "warnings": warnings,
    }


async def fetch_feed_records(client: httpx.AsyncClient, feed: dict) -> list[dict]:
    connector = feed["connector"]
    config = feed["config"]
    limit = int(config.get("max_records", 1000))
    if connector == "socrata":
        base_url = f"https://{config['domain']}/resource/{config['dataset_id']}.json"
        headers = {}
        app_token = os.getenv("SOCRATA_APP_TOKEN")
        if app_token:
            headers["X-App-Token"] = app_token
        return await _fetch_socrata_records(
            client,
            base_url,
            config.get("where"),
            limit,
            headers,
            config.get("field_mapping"),
            config.get("record_id_field"),
        )
    if connector == "arcgis":
        return await _fetch_arcgis_records(client, config, limit)
    if connector == "json_api":
        return await _fetch_json_api_records(client, config, limit)
    raise ValueError(f"Unsupported data feed connector: {connector}")


async def _fetch_socrata_records(
    client: httpx.AsyncClient,
    url: str,
    where: str | None,
    max_records: int,
    headers: dict[str, str] | None = None,
    field_mapping: dict | None = None,
    record_id_field: str | None = None,
) -> list[dict]:
    if not isinstance(field_mapping, dict) or not field_mapping:
        raise ValueError("Socrata feeds require mapped source fields")
    mapped_fields = list(field_mapping.values())
    if not all(isinstance(field, str) and field for field in mapped_fields):
        raise ValueError("Socrata field mappings must contain non-empty source field names")
    source_fields = list(dict.fromkeys(mapped_fields))
    if record_id_field and record_id_field not in source_fields:
        source_fields.append(record_id_field)

    _validate_remote_url(url)
    records = []
    offset = 0
    while len(records) < max_records:
        page_limit = min(500, max_records - len(records))
        params = {
            "$limit": page_limit,
            "$offset": offset,
            "$select": ",".join(source_fields),
        }
        if where:
            params["$where"] = where
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        _check_response_size(response)
        page = response.json()
        if not isinstance(page, list):
            raise ValueError("Socrata response was not a JSON record array")
        records.extend(
            {
                field: value
                for field, value in item.items()
                if field in source_fields
            }
            for item in page
            if isinstance(item, dict)
        )
        if len(page) < page_limit:
            break
        offset += len(page)
    return records[:max_records]


async def _fetch_arcgis_records(
    client: httpx.AsyncClient,
    config: dict,
    max_records: int,
) -> list[dict]:
    field_mapping = config.get("field_mapping")
    if not isinstance(field_mapping, dict) or not field_mapping:
        raise ValueError("ArcGIS feeds require mapped source fields")
    mapped_fields = list(field_mapping.values())
    if not all(isinstance(field, str) and field for field in mapped_fields):
        raise ValueError("ArcGIS field mappings must contain non-empty source field names")
    source_fields = list(dict.fromkeys(mapped_fields))
    record_id_field = config.get("record_id_field")
    if record_id_field and record_id_field not in source_fields:
        source_fields.append(record_id_field)
    if not all(isinstance(field, str) and field for field in source_fields):
        raise ValueError("ArcGIS field mappings must contain non-empty source field names")

    base_url = config["query_url"].rstrip("/")
    url = base_url if base_url.endswith("/query") else f"{base_url}/query"
    _validate_remote_url(url)
    records = []
    offset = 0
    while len(records) < max_records:
        page_limit = min(1000, max_records - len(records))
        params = {
            "where": config.get("where") or "1=1",
            "outFields": ",".join(source_fields),
            "returnGeometry": "false",
            "f": "json",
            "resultRecordCount": page_limit,
            "resultOffset": offset,
        }
        response = await client.get(url, params=params)
        response.raise_for_status()
        _check_response_size(response)
        payload = response.json()
        if payload.get("error"):
            raise ValueError(f"ArcGIS returned an error: {payload['error']}")
        features = payload.get("features")
        if not isinstance(features, list):
            raise ValueError("ArcGIS response did not include a feature array")
        page = []
        for item in features:
            if not isinstance(item, dict):
                continue
            attributes = item.get("attributes", item)
            if isinstance(attributes, dict):
                page.append(
                    {
                        field: value
                        for field, value in attributes.items()
                        if field in source_fields
                    }
                )
        records.extend(page)
        if not payload.get("exceededTransferLimit") and len(features) < page_limit:
            break
        if not features:
            break
        offset += len(features)
    return records[:max_records]


async def _fetch_json_api_records(
    client: httpx.AsyncClient,
    config: dict,
    max_records: int,
) -> list[dict]:
    url = config["query_url"]
    _validate_remote_url(url)
    headers = {}
    auth_env_var = config.get("auth_env_var")
    if auth_env_var:
        token = os.getenv(auth_env_var)
        if not token:
            raise ValueError(f"Required API credential environment variable {auth_env_var} is not set")
    base_params = dict(config.get("query_params") or {})
    if auth_env_var:
        query_auth_param = config.get("auth_query_param")
        if query_auth_param:
            base_params[query_auth_param] = os.getenv(auth_env_var)
        else:
            headers["Authorization"] = f"Bearer {os.getenv(auth_env_var)}"
    records = []
    offset = 0
    while len(records) < max_records:
        page_limit = min(500, max_records - len(records))
        params = dict(base_params)
        params["limit"] = page_limit
        params["offset"] = offset
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        _check_response_size(response)
        payload = response.json()
        rows = _records_at_path(payload, config.get("records_path"))
        if not isinstance(rows, list):
            raise ValueError("JSON API response did not contain a record array")
        page = [row for row in rows if isinstance(row, dict)]
        records.extend(page)
        if len(page) < page_limit:
            break
        offset += len(page)
    return records[:max_records]


def _records_at_path(payload, path: str | None):
    if not path:
        return payload
    value = payload
    for segment in path.split("."):
        if isinstance(value, dict):
            value = value.get(segment)
        elif isinstance(value, list) and segment.isdigit():
            index = int(segment)
            value = value[index] if index < len(value) else None
        else:
            return None
    return value


def _check_response_size(response: httpx.Response) -> None:
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise ValueError("Source response exceeded the 10 MB page limit")


def _validate_remote_url(url: str) -> None:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if (
        parsed.scheme != "https"
        or not hostname
        or parsed.username
        or parsed.password
        or parsed.fragment
        or hostname == "localhost"
        or hostname.endswith(".localhost")
        or hostname.endswith(".local")
    ):
        raise ValueError("Configured source URL must be public HTTPS without credentials or fragments")
    if parsed.port not in (None, 443):
        raise ValueError("Configured source URL must use the standard HTTPS port")
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return
    if not ip.is_global:
        raise ValueError("Configured source URL must not use a private or non-routable IP address")


def normalize_feed_record(row: dict, feed: dict) -> PropertyCreate:
    config = feed["config"]
    fields = {}
    for property_field, source_field in config["field_mapping"].items():
        raw_value = _lookup_source_field(row, source_field)
        if raw_value is None:
            continue
        value = _coerce_property_value(property_field, raw_value)
        if value is not None:
            fields[property_field] = value
    if "county_fips" in fields:
        fields["county_fips"] = re.sub(r"\D", "", str(fields["county_fips"])).zfill(5)
    scoped_county_fips = feed.get("county_fips")
    if scoped_county_fips:
        if fields.get("county_fips") and fields["county_fips"] != scoped_county_fips:
            raise ValueError("record county FIPS does not match this feed's county scope")
        fields["county_fips"] = scoped_county_fips
    if (
        fields.get("county_fips")
        and fields.get("state")
        and STATE_FIPS.get(str(fields["state"]).upper()) != fields["county_fips"][:2]
    ):
        raise ValueError("county FIPS state prefix does not match the record's state")
    fields.update(
        {
            "source_type": feed["source_type"],
            "source_name": feed["name"],
            "source_url": data_feed_source_url(feed),
        }
    )
    return PropertyCreate.model_validate(fields)


def _lookup_source_field(row: dict, path: str | None):
    if not path:
        return None
    value = row
    for part in path.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def _coerce_property_value(field: str, value):
    if field == "county_fips" and isinstance(value, (int, float)):
        if float(value).is_integer():
            value = str(int(value))
    if field == "zip_code" and isinstance(value, (int, float)):
        if float(value).is_integer():
            value = str(int(value))
    if isinstance(value, str):
        value = value.strip()
        if field == "county_fips" and re.fullmatch(r"\d+\.0", value):
            value = value[:-2]
        if field == "zip_code" and re.fullmatch(r"\d+\.0", value):
            value = value[:-2]
        if not value or value.casefold() in {"null", "none", "n/a", "na", "-"}:
            return None
    if field in INTEGER_FIELDS or field in NUMERIC_FIELDS:
        if isinstance(value, bool):
            raise ValueError(f"{field} must be numeric")
        if isinstance(value, str):
            cleaned = value.replace(",", "").replace("$", "").replace("%", "").strip()
        else:
            cleaned = value
        number = float(cleaned)
        if field in INTEGER_FIELDS:
            if not number.is_integer():
                raise ValueError(f"{field} must be a whole number")
            return int(number)
        return number
    if field == "county_fips":
        return str(value).strip()
    return str(value).strip() if isinstance(value, str) else value


async def sync_census_population(
    session_factory: sessionmaker,
    client: httpx.AsyncClient,
) -> dict:
    session = session_factory()
    try:
        property_rows = (
            session.query(Property.id, Property.county_fips)
            .filter(Property.county_fips.isnot(None))
            .all()
        )
    finally:
        session.close()
    groups: dict[str, list[int]] = {}
    for property_id, fips in property_rows:
        if isinstance(fips, str) and re.fullmatch(r"\d{5}", fips):
            groups.setdefault(fips, []).append(property_id)
    if not groups:
        return {
            "source_id": "census_acs",
            "source_name": "U.S. Census Bureau ACS",
            "status": "skipped",
            "inserted": 0,
            "updated": 0,
            "skipped": len(property_rows),
            "message": "No properties have a valid five-digit county FIPS code.",
        }

    county_codes = list(groups)[:MAX_AUTOMATED_COUNTIES]
    semaphore = asyncio.Semaphore(6)

    async def fetch_county(fips):
        async with semaphore:
            try:
                result = await fetch_acs_population(
                    fips[:2],
                    fips[2:],
                    client=client,
                )
                return fips, result, None
            except Exception as error:
                return fips, None, str(error)[:500]

    fetched = await asyncio.gather(*(fetch_county(fips) for fips in county_codes))
    updated = skipped = 0
    errors = []
    session = session_factory()
    try:
        for fips, result, error in fetched:
            if error:
                errors.append(f"{fips}: {error}")
                skipped += len(groups[fips])
                continue
            for property_id in groups[fips]:
                property_record = session.get(Property, property_id)
                if property_record is None:
                    continue
                changed = False
                for metric in (
                    "population_current",
                    "population_previous",
                    "population_growth_percent",
                ):
                    changed = _record_metric(
                        property_record,
                        metric,
                        result[metric],
                        result["source_name"],
                        result["source_url"],
                        "official_estimate",
                    ) or changed
                property_record.population_data_year = result["current_year"]
                property_record.county = (
                    property_record.county
                    or result["county_name"].rsplit(", ", 1)[0]
                )
                if changed:
                    property_record.updated_at = utc_now()
                    updated += 1
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    if len(groups) > MAX_AUTOMATED_COUNTIES:
        errors.append(
            f"Only the first {MAX_AUTOMATED_COUNTIES} distinct counties were refreshed this run."
        )
    return {
        "source_id": "census_acs",
        "source_name": "U.S. Census Bureau ACS",
        "status": "partial" if errors else "success",
        "inserted": 0,
        "updated": updated,
        "skipped": skipped + max(0, len(groups) - MAX_AUTOMATED_COUNTIES),
        "warnings": errors[:10],
    }


async def sync_hud_fmr(
    session_factory: sessionmaker,
    client: httpx.AsyncClient,
) -> dict:
    api_key = os.getenv("HUD_API_KEY")
    if not api_key:
        return {
            "source_id": "hud_fmr",
            "source_name": "HUD Fair Market Rents",
            "status": "skipped",
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "message": "Set HUD_API_KEY to enable daily HUD FMR enrichment.",
        }
    try:
        year = int(os.getenv("HUD_FMR_YEAR", str(datetime.now().year)))
    except ValueError as error:
        raise ValueError("HUD_FMR_YEAR must be a four-digit year") from error
    session = session_factory()
    try:
        property_rows = (
            session.query(Property.id, Property.zip_code, Property.bedrooms)
            .filter(Property.zip_code.isnot(None), Property.bedrooms.isnot(None))
            .all()
        )
    finally:
        session.close()
    groups: dict[tuple[str, int], list[int]] = {}
    for property_id, zip_code, bedrooms in property_rows:
        if isinstance(zip_code, str) and re.fullmatch(r"\d{5}", zip_code[:5]):
            groups.setdefault((zip_code[:5], bedrooms), []).append(property_id)
    if not groups:
        return {
            "source_id": "hud_fmr",
            "source_name": "HUD Fair Market Rents",
            "status": "skipped",
            "inserted": 0,
            "updated": 0,
            "skipped": len(property_rows),
            "message": "No properties have both a five-digit ZIP code and a bedroom count.",
        }

    keys = list(groups)[:MAX_HUD_ZIP_BEDROOM_GROUPS]
    semaphore = asyncio.Semaphore(4)

    async def fetch_fmr(zip_code, bedrooms):
        async with semaphore:
            try:
                amount = await fetch_hud_fmr(
                    zip_code,
                    bedrooms,
                    year,
                    api_key,
                    client,
                )
                return (zip_code, bedrooms), amount, None
            except Exception as error:
                return (zip_code, bedrooms), None, str(error)[:500]

    fetched = await asyncio.gather(
        *(fetch_fmr(zip_code, bedrooms) for zip_code, bedrooms in keys)
    )
    updated = skipped = 0
    errors = []
    session = session_factory()
    try:
        for key, amount, error in fetched:
            if error:
                errors.append(f"{key[0]}/{key[1]} bedrooms: {error}")
                skipped += len(groups[key])
                continue
            source_url = (
                f"{HUD_FMR_ENDPOINT}?year={year}&zip_code={key[0]}"
            )
            for property_id in groups[key]:
                property_record = session.get(Property, property_id)
                if property_record is not None and _record_metric(
                    property_record,
                    "hud_fmr_monthly",
                    amount,
                    "HUD Fair Market Rents Data API",
                    source_url,
                    "official_estimate",
                ):
                    property_record.updated_at = utc_now()
                    updated += 1
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    if len(groups) > MAX_HUD_ZIP_BEDROOM_GROUPS:
        errors.append(
            f"Only the first {MAX_HUD_ZIP_BEDROOM_GROUPS} ZIP/bedroom groups were refreshed this run."
        )
    return {
        "source_id": "hud_fmr",
        "source_name": "HUD Fair Market Rents",
        "status": "partial" if errors else "success",
        "inserted": 0,
        "updated": updated,
        "skipped": skipped + max(0, len(groups) - MAX_HUD_ZIP_BEDROOM_GROUPS),
        "warnings": errors[:10],
    }


async def fetch_hud_fmr(
    zip_code: str,
    bedrooms: int,
    year: int,
    api_key: str,
    client: httpx.AsyncClient,
) -> float:
    response = await client.get(
        HUD_FMR_ENDPOINT,
        params={"year": year, "zip_code": zip_code},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    response.raise_for_status()
    _check_response_size(response)
    payload = response.json()
    basic_data = payload.get("data", {}).get("basicdata", {})
    if not isinstance(basic_data, dict):
        raise ValueError("HUD FMR response did not contain basicdata")
    field = f"fmr_{bedrooms}"
    amount = basic_data.get(field)
    if amount is None:
        raise ValueError(f"HUD FMR response has no {field} estimate")
    try:
        amount = float(amount)
    except (TypeError, ValueError) as error:
        raise ValueError(f"HUD FMR returned an invalid {field} estimate") from error
    if amount < 0:
        raise ValueError(f"HUD FMR returned a negative {field} estimate")
    return amount


def _record_metric(
    property_record: Property,
    metric: str,
    value,
    source_name: str,
    source_url: str | None,
    confidence: str,
) -> bool:
    previous_value = getattr(property_record, metric)
    metadata = dict(property_record.source_metadata or {})
    group = METRIC_SOURCE_GROUPS[metric]
    previous_source = metadata.get(group) or {}
    source_changed = previous_source.get("source_name") != source_name
    if previous_value == value and not source_changed:
        return False
    setattr(property_record, metric, value)
    metadata[group] = {
        "source_name": source_name,
        "source_url": source_url,
        "confidence": confidence,
    }
    property_record.source_metadata = metadata
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
    return previous_value != value
