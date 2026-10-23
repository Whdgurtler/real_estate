import asyncio
import unittest

import httpx

from app.sources import fetch_acs_population


class CensusSourceTests(unittest.TestCase):
    def test_fetches_two_acs_vintages_and_returns_growth_with_provenance(self):
        def handler(request):
            year = request.url.path.split("/")[2]
            population = 100 if year == "2019" else 110
            return httpx.Response(
                200,
                json=[
                    ["NAME", "B01003_001E", "state", "county"],
                    ["Pulaski County, Arkansas", str(population), "05", "119"],
                ],
            )

        async def run():
            async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
                return await fetch_acs_population("05", "119", client=client, current_year=2024)

        result = asyncio.run(run())
        self.assertEqual(result["county_fips"], "05119")
        self.assertEqual(result["population_current"], 110)
        self.assertEqual(result["population_previous"], 100)
        self.assertEqual(result["population_growth_percent"], 1.92)
        self.assertEqual(result["population_change_percent"], 10)
        self.assertEqual(result["current_year"], 2024)
        self.assertIn("api.census.gov", result["source_url"])

    def test_rejects_invalid_fips_without_making_a_request(self):
        with self.assertRaisesRegex(ValueError, "FIPS"):
            asyncio.run(fetch_acs_population("5", "119"))


if __name__ == "__main__":
    unittest.main()
