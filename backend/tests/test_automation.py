import asyncio
import os
import unittest
from datetime import date
from unittest.mock import patch

import httpx
from sqlalchemy.orm import Session

from app.automation import (
    MAX_AUTOMATED_COUNTIES,
    create_sync_run,
    data_feed_config,
    execute_sync_job,
    fetch_hud_fmr,
    fetch_feed_records,
    schedule_settings,
    sync_configured_feed,
)
from app.db import Base, create_database, create_session_factory
from app.models import DataEvidence, DataFeed, DataFeedRecord, Property, SyncRun
from app.jurisdictions import county_jurisdictions
from app.schemas import DataFeedCreate


class DataAutomationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_database("sqlite://")
        Base.metadata.create_all(bind=self.engine)
        self.session_factory = create_session_factory(self.engine)

    def tearDown(self):
        self.engine.dispose()

    def test_daily_population_refresh_limit_covers_all_priority_counties(self):
        self.assertGreaterEqual(MAX_AUTOMATED_COUNTIES, len(county_jurisdictions()))

    def test_configured_feed_upserts_repeated_records_and_keeps_changed_evidence(self):
        data = DataFeedCreate(
            name="County code violations",
            connector="socrata",
            source_type="code_enforcement",
            domain="data.county.gov",
            dataset_id="abcd-1234",
            record_id_field="case_id",
            field_mapping={
                "address": "address",
                "city": "city",
                "state": "state",
                "asking_price": "estimated_value",
            },
        )
        session = self.session_factory()
        stored_feed = DataFeed(
            name=data.name,
            connector=data.connector,
            source_type=data.source_type,
            config=data_feed_config(data),
        )
        session.add(stored_feed)
        session.commit()
        feed = {
            "id": stored_feed.id,
            "name": stored_feed.name,
            "connector": stored_feed.connector,
            "source_type": stored_feed.source_type,
            "config": stored_feed.config,
        }
        session.close()
        upstream_value = {"asking_price": "80,000"}

        def handler(request):
            self.assertEqual(request.url.host, "data.county.gov")
            return httpx.Response(
                200,
                json=[
                    {
                        "case_id": "case-17",
                        "address": "17 Oak Street",
                        "city": "Dayton",
                        "state": "OH",
                        "estimated_value": upstream_value["asking_price"],
                    }
                ],
            )

        async def sync_once():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                return await sync_configured_feed(self.session_factory, client, feed)

        first = asyncio.run(sync_once())
        self.assertEqual(first["inserted"], 1)
        self.assertEqual(first["status"], "success")

        second = asyncio.run(sync_once())
        self.assertEqual(second["inserted"], 0)
        self.assertEqual(second["updated"], 0)

        upstream_value["asking_price"] = "85,000"
        third = asyncio.run(sync_once())
        self.assertEqual(third["updated"], 1)

        session = self.session_factory()
        properties = session.query(Property).all()
        evidence = session.query(DataEvidence).filter_by(metric="asking_price").all()
        links = session.query(DataFeedRecord).all()
        self.assertEqual(len(properties), 1)
        self.assertEqual(properties[0].asking_price, 85000)
        self.assertEqual(len(evidence), 2)
        self.assertEqual(len(links), 1)
        self.assertEqual(evidence[-1].source_name, "County code violations")
        session.close()

    def test_hud_fmr_adapter_uses_bearer_key_and_bedroom_specific_estimate(self):
        def handler(request):
            self.assertEqual(request.url.path, "/hudapi/public/fmr")
            self.assertEqual(request.url.params["year"], "2026")
            self.assertEqual(request.url.params["zip_code"], "72201")
            self.assertEqual(request.headers["Authorization"], "Bearer test-hud-key")
            return httpx.Response(
                200,
                json={"data": {"basicdata": {"fmr_2": "1325"}}},
            )

        async def run():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                return await fetch_hud_fmr(
                    "72201",
                    2,
                    2026,
                    "test-hud-key",
                    client,
                )

        self.assertEqual(asyncio.run(run()), 1325)

    def test_enrichment_feed_updates_existing_county_properties_without_creating_leads(self):
        data = DataFeedCreate(
            name="County crime rate",
            connector="socrata",
            target="property_enrichment",
            source_type="other",
            domain="data.county.gov",
            dataset_id="crime-123",
            field_mapping={
                "county_fips": "county_fips",
                "violent_crime_rate_per_100k": "violent_rate",
            },
        )
        session = self.session_factory()
        property_record = Property(
            address="101 Oak Street",
            city="Little Rock",
            state="AR",
            county_fips="05119",
            source_type="conventional",
        )
        stored_feed = DataFeed(
            name=data.name,
            connector=data.connector,
            source_type=data.source_type,
            config=data_feed_config(data),
        )
        session.add_all([property_record, stored_feed])
        session.commit()
        feed = {
            "id": stored_feed.id,
            "name": stored_feed.name,
            "connector": stored_feed.connector,
            "source_type": stored_feed.source_type,
            "config": stored_feed.config,
        }
        session.close()

        def handler(request):
            return httpx.Response(
                200,
                json=[
                    {"county_fips": "05119", "violent_rate": "220.5"},
                    {"county_fips": "99999", "violent_rate": "300"},
                ],
            )

        async def sync_once():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                return await sync_configured_feed(self.session_factory, client, feed)

        result = asyncio.run(sync_once())
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["skipped"], 1)

        session = self.session_factory()
        self.assertEqual(session.query(Property).count(), 1)
        saved = session.query(Property).one()
        self.assertEqual(saved.violent_crime_rate_per_100k, 220.5)
        self.assertEqual(
            session.query(DataEvidence).filter_by(metric="violent_crime_rate_per_100k").count(),
            1,
        )
        session.close()

    def test_json_api_credential_is_injected_from_environment_not_feed_config(self):
        def handler(request):
            self.assertEqual(request.url.params["api_key"], "test-only-key")
            self.assertEqual(request.url.params["state"], "Arkansas")
            self.assertNotIn("Authorization", request.headers)
            return httpx.Response(200, json={"results": [{"record_id": "1"}]})

        feed = {
            "connector": "json_api",
            "config": {
                "query_url": "https://provider.example/api/parcels",
                "auth_env_var": "TEST_SOURCE_API_KEY",
                "auth_query_param": "api_key",
                "query_params": {"state": "Arkansas"},
                "records_path": "results",
                "max_records": 100,
            },
        }

        async def run():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                return await fetch_feed_records(client, feed)

        with patch.dict(os.environ, {"TEST_SOURCE_API_KEY": "test-only-key"}):
            self.assertEqual(asyncio.run(run()), [{"record_id": "1"}])

    def test_arcgis_requests_only_mapped_fields_and_record_id(self):
        def handler(request):
            self.assertEqual(
                request.url.params["outFields"],
                "SITE_ADDRESS,ASSESSED_VALUE,PARCEL_ID",
            )
            return httpx.Response(
                200,
                json={
                    "features": [
                        {
                            "attributes": {
                                "SITE_ADDRESS": "1 Main Street",
                                "ASSESSED_VALUE": 125000,
                                "PARCEL_ID": "parcel-1",
                                "CONFIDENTIAL_NOTES": "must not be fetched",
                            }
                        }
                    ]
                },
            )

        feed = {
            "connector": "arcgis",
            "config": {
                "query_url": "https://services.example/FeatureServer/0",
                "field_mapping": {
                    "address": "SITE_ADDRESS",
                    "assessed_value": "ASSESSED_VALUE",
                },
                "record_id_field": "PARCEL_ID",
                "max_records": 1,
            },
        }

        async def run():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                return await fetch_feed_records(client, feed)

        records = asyncio.run(run())
        self.assertEqual(
            records,
            [
                {
                    "SITE_ADDRESS": "1 Main Street",
                    "ASSESSED_VALUE": 125000,
                    "PARCEL_ID": "parcel-1",
                }
            ],
        )

    def test_socrata_requests_only_mapped_fields_and_record_id(self):
        def handler(request):
            self.assertEqual(
                request.url.params["$select"],
                "address,city,state,case_id",
            )
            return httpx.Response(
                200,
                json=[
                    {
                        "address": "1 Main Street",
                        "city": "Dallas",
                        "state": "TX",
                        "case_id": "case-1",
                        "private_note": "must not be fetched",
                    }
                ],
            )

        feed = {
            "connector": "socrata",
            "config": {
                "domain": "data.example.gov",
                "dataset_id": "abcd-1234",
                "field_mapping": {
                    "address": "address",
                    "city": "city",
                    "state": "state",
                },
                "record_id_field": "case_id",
                "max_records": 1,
            },
        }

        async def run():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                return await fetch_feed_records(client, feed)

        records = asyncio.run(run())
        self.assertEqual(
            records,
            [
                {
                    "address": "1 Main Street",
                    "city": "Dallas",
                    "state": "TX",
                    "case_id": "case-1",
                }
            ],
        )

    def test_executor_persists_failure_message(self):
        run_id = create_sync_run(self.session_factory, "manual")
        with patch(
            "app.automation.sync_all_sources",
            side_effect=RuntimeError("provider failed"),
        ):
            execute_sync_job(self.session_factory, run_id)

        session = self.session_factory()
        run = session.get(SyncRun, run_id)
        self.assertEqual(run.status, "failed")
        self.assertIn("provider failed", run.error)
        self.assertIsNone(run.active_slot)
        session.close()

    def test_daily_schedule_is_configurable_and_invalid_time_is_reported(self):
        with patch.dict(
            os.environ,
            {
                "DAILY_SYNC_ENABLED": "true",
                "DAILY_SYNC_TIME": "01:45",
                "DAILY_SYNC_TIMEZONE": "UTC",
            },
        ):
            self.assertEqual(schedule_settings(), (True, "01:45", "UTC"))

        with patch.dict(os.environ, {"DAILY_SYNC_TIME": "25:00"}):
            with self.assertRaisesRegex(ValueError, "HH:MM"):
                schedule_settings()

    def test_database_allows_only_one_active_sync_run(self):
        first_id = create_sync_run(self.session_factory, "manual")
        second_id = create_sync_run(self.session_factory, "manual")
        self.assertIsNotNone(first_id)
        self.assertIsNone(second_id)
        session: Session = self.session_factory()
        run = session.get(SyncRun, first_id)
        self.assertEqual(run.status, "queued")
        self.assertEqual(run.active_slot, "property-data-sync")
        session.close()

    def test_scheduled_date_cannot_be_claimed_twice_after_run_finishes(self):
        run_date = date(2026, 10, 19)
        run_id = create_sync_run(self.session_factory, "scheduled", run_date)
        session = self.session_factory()
        run = session.get(SyncRun, run_id)
        run.status = "success"
        run.active_slot = None
        session.commit()
        session.close()

        self.assertIsNone(create_sync_run(self.session_factory, "scheduled", run_date))


if __name__ == "__main__":
    unittest.main()
