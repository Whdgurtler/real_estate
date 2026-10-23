import time
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import create_app


class PropertyApiTests(unittest.TestCase):
    def setUp(self):
        self.application = create_app("sqlite://")
        self.client = TestClient(self.application)

    def tearDown(self):
        self.client.close()
        self.application.state.engine.dispose()

    def test_creates_property_with_metric_evidence_and_unknown_voucher_count(self):
        response = self.client.post(
            "/api/properties",
            json={
                "address": "101 Main Street",
                "city": "Little Rock",
                "state": "ar",
                "source_type": "tax_sale",
                "source_name": "County tax sale",
                "asking_price": 80_000,
                "annual_property_tax": 1_200,
                "source_metadata": {
                    "tax": {
                        "source_name": "County assessor record",
                        "source_url": "https://county.example/taxes",
                        "confidence": "official_record",
                    }
                },
                "pha_program_status": "unknown",
                "voucher_waitlist_status": "open",
            },
        )

        self.assertEqual(response.status_code, 201)
        created = response.json()
        self.assertEqual(created["state"], "AR")
        self.assertIsNone(created["open_voucher_count"])
        evidence = {item["metric"]: item for item in created["evidence"]}
        self.assertEqual(evidence["asking_price"]["source_name"], "County tax sale")
        self.assertEqual(evidence["annual_property_tax"]["source_name"], "County assessor record")
        self.assertEqual(evidence["annual_property_tax"]["confidence"], "official_record")
        summary = self.client.get("/api/portfolio/summary").json()
        self.assertEqual(summary["property_count"], 1)
        self.assertEqual(summary["voucher_counts_unknown"], 1)

    def test_csv_import_normalizes_blank_optional_values_and_is_atomic_on_invalid_row(self):
        imported = self.client.post(
            "/api/properties/import",
            content="address,city,state,asking_price,county_fips\n"
            "22 Oak Street,Dayton,OH,75000,\n",
            headers={"Content-Type": "text/csv"},
        )
        self.assertEqual(imported.status_code, 200)
        self.assertEqual(imported.json()["imported"], 1)

        rejected = self.client.post(
            "/api/properties/import",
            content="address,city,state,asking_price\n"
            "valid row,Dayton,OH,75000\n"
            "bad row,Dayton,Ohio,-10\n",
            headers={"Content-Type": "text/csv"},
        )
        self.assertEqual(rejected.status_code, 422)
        self.assertEqual(self.client.get("/api/portfolio/summary").json()["property_count"], 1)

    def test_nearby_search_uses_coordinates_and_radius(self):
        for address, latitude, longitude in (
            ("Near", 34.74, -92.28),
            ("Far", 36.16, -86.78),
        ):
            response = self.client.post(
                "/api/properties",
                json={
                    "address": address,
                    "city": "Test city",
                    "state": "AR",
                    "latitude": latitude,
                    "longitude": longitude,
                },
            )
            self.assertEqual(response.status_code, 201)

        result = self.client.get(
            "/api/properties/nearby",
            params={"latitude": 34.74, "longitude": -92.28, "radius_km": 10},
        )

        self.assertEqual(result.status_code, 200)
        self.assertEqual([row["property"]["address"] for row in result.json()], ["Near"])
        self.assertEqual(result.json()[0]["distance_km"], 0)

    def test_census_enrichment_persists_annualized_growth_and_official_evidence(self):
        created = self.client.post(
            "/api/properties",
            json={
                "address": "10 River Road",
                "city": "Little Rock",
                "state": "AR",
                "county_fips": "05119",
            },
        ).json()
        census_result = {
            "county_name": "Pulaski County, Arkansas",
            "county_fips": "05119",
            "population_current": 400,
            "population_previous": 380,
            "population_growth_percent": 1.03,
            "population_change_percent": 5.26,
            "period_years": 5,
            "current_year": 2024,
            "previous_year": 2019,
            "source_name": "U.S. Census Bureau ACS",
            "source_url": "https://api.census.gov/test",
        }
        with patch("app.main.fetch_acs_population", new=AsyncMock(return_value=census_result)):
            response = self.client.post(f"/api/properties/{created['id']}/enrich/census")

        self.assertEqual(response.status_code, 200)
        enriched = response.json()
        self.assertEqual(enriched["population_growth_percent"], 1.03)
        self.assertEqual(enriched["population_data_year"], 2024)
        self.assertTrue(
            any(
                item["metric"] == "population_growth_percent"
                and item["confidence"] == "official_estimate"
                for item in enriched["evidence"]
            )
        )

    def test_underwriting_endpoint_accepts_custom_operating_and_score_assumptions(self):
        created = self.client.post(
            "/api/properties",
            json={
                "address": "14 Oak Street",
                "city": "Dayton",
                "state": "OH",
                "asking_price": 100_000,
                "annual_property_tax": 1_000,
                "annual_insurance_estimate": 900,
                "expected_market_rent_monthly": 1_500,
                "population_growth_percent": 1,
            },
        ).json()

        response = self.client.post(
            f"/api/properties/{created['id']}/underwriting",
            json={
                "vacancy_rate_percent": 7,
                "maintenance_rate_percent": 9,
                "management_rate_percent": 8,
                "yield_weight": 0.8,
                "growth_weight": 0.2,
                "safety_weight": 0,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["assumptions"]["vacancy_rate_percent"], 7)
        self.assertEqual(response.json()["score"]["weights"]["yield"], 0.8)

    def test_property_update_preserves_omitted_values_and_appends_new_evidence(self):
        created = self.client.post(
            "/api/properties",
            json={
                "address": "10 Oak Street",
                "city": "Dayton",
                "state": "OH",
                "asking_price": 70_000,
                "population_current": 12_000,
                "source_metadata": {
                    "tax": {
                        "source_name": "County assessor",
                        "source_url": "https://county.example/assessor",
                        "confidence": "official_record",
                    }
                },
            },
        ).json()

        response = self.client.put(
            f"/api/properties/{created['id']}",
            json={
                "address": "12 Oak Street",
                "city": "Dayton",
                "state": "OH",
                "asking_price": 75_000,
            },
        )

        self.assertEqual(response.status_code, 200)
        updated = response.json()
        self.assertEqual(updated["address"], "12 Oak Street")
        self.assertEqual(updated["asking_price"], 75_000)
        self.assertEqual(updated["population_current"], 12_000)
        self.assertEqual(updated["source_metadata"]["tax"]["source_name"], "County assessor")


class DataFeedApiTests(unittest.TestCase):
    def setUp(self):
        self.env_patch = patch.dict(
            "os.environ",
            {
                "DAILY_SYNC_ENABLED": "true",
                "DAILY_SYNC_TIME": "02:00",
                "DAILY_SYNC_TIMEZONE": "America/Chicago",
            },
        )
        self.env_patch.start()
        self.application = create_app("sqlite://")
        self.client = TestClient(self.application)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.application.state.engine.dispose()
        self.env_patch.stop()

    def test_feed_can_be_created_paused_listed_and_removed(self):
        created = self.client.post(
            "/api/data-feeds",
            json={
                "name": "County tax-sale parcels",
                "connector": "socrata",
                "source_type": "tax_sale",
                "domain": "data.county.gov",
                "dataset_id": "abcd-1234",
                "record_id_field": "parcel_id",
                "field_mapping": {
                    "address": "situs_address",
                    "city": "city",
                    "state": "state",
                    "asking_price": "opening_bid",
                },
            },
        )

        self.assertEqual(created.status_code, 201)
        feed = created.json()
        self.assertEqual(feed["source_type"], "tax_sale")
        self.assertEqual(feed["source_url"], "https://data.county.gov/d/abcd-1234")
        self.assertEqual(self.client.get("/api/data-feeds").json()[0]["id"], feed["id"])

        paused = self.client.patch(
            f"/api/data-feeds/{feed['id']}",
            json={"enabled": False},
        )
        self.assertEqual(paused.status_code, 200)
        self.assertFalse(paused.json()["enabled"])

        removed = self.client.delete(f"/api/data-feeds/{feed['id']}")
        self.assertEqual(removed.status_code, 204)
        self.assertEqual(self.client.get("/api/data-feeds").json(), [])

    def test_feed_requires_location_identity_and_public_https_endpoints(self):
        missing_location = self.client.post(
            "/api/data-feeds",
            json={
                "name": "Incomplete source",
                "connector": "socrata",
                "source_type": "other",
                "domain": "data.county.gov",
                "dataset_id": "abcd-1234",
                "field_mapping": {"address": "address", "state": "state"},
            },
        )
        self.assertEqual(missing_location.status_code, 422)

        private_endpoint = self.client.post(
            "/api/data-feeds",
            json={
                "name": "Private JSON endpoint",
                "connector": "json_api",
                "source_type": "other",
                "query_url": "https://127.0.0.1/data",
                "field_mapping": {
                    "address": "address",
                    "city": "city",
                    "state": "state",
                },
            },
        )
        self.assertEqual(private_endpoint.status_code, 422)

    def test_sync_status_exposes_scheduler_configuration(self):
        response = self.client.get("/api/sync/status")
        self.assertEqual(response.status_code, 200)
        status = response.json()
        self.assertTrue(status["enabled"])
        self.assertEqual(status["daily_time"], "02:00")
        self.assertEqual(status["timezone"], "America/Chicago")
        self.assertIsNotNone(status["next_run_at"])

    def test_priority_county_directory_lists_county_sources_and_feed_configuration(self):
        national = self.client.get("/api/jurisdictions")
        self.assertEqual(national.status_code, 200)
        national_data = national.json()
        self.assertEqual(national_data["county_equivalent_count"], 599)
        self.assertEqual(
            {state: sum(row["state"] == state for row in national_data["jurisdictions"]) for state in ("AL", "AR", "OH", "MO", "TX")},
            {"AL": 67, "AR": 75, "OH": 88, "MO": 115, "TX": 254},
        )
        mobile = next(
            row for row in national_data["jurisdictions"] if row["county_fips"] == "01097"
        )
        self.assertEqual(
            mobile["sources"]["assessor"]["endpoint_status"],
            "terms_review_required",
        )
        alabama_counties = [
            row for row in national_data["jurisdictions"] if row["state"] == "AL"
        ]
        self.assertEqual(len(alabama_counties), 67)
        transcript_urls = [
            row["sources"]["tax_sale"]["source_url"] for row in alabama_counties
        ]
        self.assertEqual(sum(url.endswith(".PDF") for url in transcript_urls), 66)
        jefferson_alabama = next(
            row for row in alabama_counties if row["county_fips"] == "01073"
        )
        self.assertIn(
            "tax-delinquent-property-and-land-sales",
            jefferson_alabama["sources"]["tax_sale"]["source_url"],
        )
        jefferson = next(
            row for row in national_data["jurisdictions"] if row["county_fips"] == "01073"
        )
        self.assertEqual(
            jefferson["sources"]["assessor"]["endpoint_record_count"],
            410119,
        )
        ohio_counties = [
            row for row in national_data["jurisdictions"] if row["state"] == "OH"
        ]
        self.assertEqual(len(ohio_counties), 88)
        franklin = next(
            row
            for row in ohio_counties
            if row["county_fips"] == "39049"
        )
        self.assertEqual(
            franklin["sources"]["assessor"]["endpoint_record_count"],
            494902,
        )
        self.assertTrue(
            all(
                row["sources"]["assessor"]["endpoint_scope"] == "Ohio statewide"
                for row in ohio_counties
                if row["county_fips"] != "39049"
            )
        )
        dallas = next(
            row for row in national_data["jurisdictions"] if row["county_fips"] == "48113"
        )
        self.assertEqual(
            dallas["sources"]["code_enforcement"]["endpoint_status"],
            "historical_not_daily",
        )
        harris = next(
            row for row in national_data["jurisdictions"] if row["county_fips"] == "48201"
        )
        self.assertEqual(
            harris["sources"]["assessor"]["endpoint_record_count"],
            1551736,
        )
        cincinnati = next(
            row for row in national_data["jurisdictions"] if row["county_fips"] == "39061"
        )
        self.assertEqual(
            cincinnati["sources"]["code_enforcement"]["endpoint_record_count"],
            771669,
        )
        self.assertEqual(
            len(cincinnati["sources"]["code_enforcement"]["additional_endpoints"]),
            1,
        )

        texas = self.client.get("/api/jurisdictions?state=tx")
        self.assertEqual(texas.status_code, 200)
        texas_data = texas.json()
        self.assertEqual(texas_data["county_equivalent_count"], 254)
        harris = next(
            row for row in texas_data["jurisdictions"] if row["county_fips"] == "48201"
        )
        self.assertEqual(harris["county"], "Harris County")
        self.assertEqual(
            harris["sources"]["foreclosure"]["status"], "needs_feed_verification"
        )
        texas_feed = self.client.post(
            "/api/data-feeds",
            json={
                "name": "Harris County pre-foreclosure notices",
                "connector": "json_api",
                "source_category": "pre_foreclosure",
                "source_type": "pre_foreclosure",
                "county_fips": "48201",
                "query_url": "https://data.county.gov/notices",
                "field_mapping": {
                    "address": "address",
                    "city": "city",
                    "state": "state",
                },
            },
        )
        self.assertEqual(texas_feed.status_code, 201)
        harris = next(
            row
            for row in self.client.get("/api/jurisdictions?state=TX").json()[
                "jurisdictions"
            ]
            if row["county_fips"] == "48201"
        )
        self.assertEqual(
            harris["sources"]["pre_foreclosure"]["status"], "feed_configured"
        )

        missouri = self.client.get("/api/jurisdictions?state=mo")
        self.assertEqual(missouri.status_code, 200)
        st_louis_county = next(
            row
            for row in missouri.json()["jurisdictions"]
            if row["county_fips"] == "29189"
        )
        self.assertEqual(
            st_louis_county["sources"]["assessor"]["endpoint_record_count"],
            400796,
        )
        st_louis_city = next(
            row
            for row in missouri.json()["jurisdictions"]
            if row["county_fips"] == "29510"
        )
        self.assertEqual(st_louis_city["county"], "St. Louis city")
        self.assertEqual(st_louis_city["sources"]["code_enforcement"]["status"], "municipal_scope")
        self.assertEqual(
            st_louis_city["sources"]["foreclosure"]["status"], "needs_feed_verification"
        )
        self.assertEqual(
            st_louis_city["sources"]["pre_foreclosure"]["status"],
            "needs_feed_verification",
        )

        feed = self.client.post(
            "/api/data-feeds",
            json={
                "name": "Pulaski County assessor parcels",
                "connector": "socrata",
                "source_category": "assessor",
                "source_type": "other",
                "county_fips": "05119",
                "domain": "data.county.gov",
                "dataset_id": "abcd-1234",
                "field_mapping": {
                    "address": "address",
                    "city": "city",
                    "state": "state",
                },
            },
        )
        self.assertEqual(feed.status_code, 201)
        self.assertEqual(feed.json()["county_fips"], "05119")

        updated = self.client.get("/api/jurisdictions?state=AR").json()
        pulaski = next(row for row in updated["jurisdictions"] if row["county_fips"] == "05119")
        assessor = pulaski["sources"]["assessor"]
        self.assertEqual(assessor["status"], "feed_configured")
        self.assertEqual(assessor["feeds"][0]["name"], "Pulaski County assessor parcels")

        for category, source_type in (
            ("foreclosure", "foreclosure"),
            ("pre_foreclosure", "pre_foreclosure"),
        ):
            with self.subTest(category=category):
                configured = self.client.post(
                    "/api/data-feeds",
                    json={
                        "name": f"Pulaski County {category}",
                        "connector": "json_api",
                        "source_category": category,
                        "source_type": source_type,
                        "county_fips": "05119",
                        "query_url": "https://data.county.gov/foreclosure",
                        "field_mapping": {
                            "address": "address",
                            "city": "city",
                            "state": "state",
                        },
                    },
                )
                self.assertEqual(configured.status_code, 201)
                self.assertEqual(configured.json()["source_category"], category)
                self.assertEqual(configured.json()["source_type"], source_type)

        updated = self.client.get("/api/jurisdictions?state=AR").json()
        pulaski = next(row for row in updated["jurisdictions"] if row["county_fips"] == "05119")
        for category in ("foreclosure", "pre_foreclosure"):
            with self.subTest(category=category):
                self.assertEqual(pulaski["sources"][category]["status"], "feed_configured")

        invalid_county = self.client.post(
            "/api/data-feeds",
            json={
                "name": "Unknown county source",
                "connector": "socrata",
                "source_category": "assessor",
                "source_type": "other",
                "county_fips": "05120",
                "domain": "data.county.gov",
                "dataset_id": "efgh-5678",
                "field_mapping": {
                    "address": "address",
                    "city": "city",
                    "state": "state",
                },
            },
        )
        self.assertEqual(invalid_county.status_code, 422)

    def test_run_now_executes_and_persists_source_status(self):
        with patch.dict("os.environ", {"HUD_API_KEY": ""}):
            queued = self.client.post("/api/sync/run")
            self.assertEqual(queued.status_code, 202)
            run_id = queued.json()["run_id"]
            completed = None
            for _ in range(40):
                status = self.client.get("/api/sync/status").json()
                completed = next(
                    (run for run in status["runs"] if run["id"] == run_id),
                    None,
                )
                if completed and completed["status"] not in {"queued", "running"}:
                    break
                time.sleep(0.05)

        self.assertIsNotNone(completed)
        self.assertEqual(completed["status"], "success")
        results = {result["source_id"]: result for result in completed["source_results"]}
        self.assertEqual(results["census_acs"]["status"], "skipped")
        self.assertEqual(results["hud_fmr"]["status"], "skipped")


if __name__ == "__main__":
    unittest.main()
