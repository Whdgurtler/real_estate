import os
import re
from urllib.parse import urlencode

import httpx


ACS_BASE = "https://api.census.gov/data"


def source_catalog():
    return [
        {
            "id": "census_acs",
            "name": "U.S. Census Bureau ACS",
            "category": "population",
            "availability": "live",
            "access": "Public API; county FIPS required.",
            "url": "https://api.census.gov/data.html",
        },
        {
            "id": "fbi_cde",
            "name": "FBI Crime Data Explorer",
            "category": "crime",
            "availability": "import_or_api_key",
            "access": "Official source; API access and geographic coverage must be verified for the requested area.",
            "url": "https://cde.ucr.cjis.gov/",
        },
        {
            "id": "hud_fmr",
            "name": "HUD Fair Market Rents",
            "category": "rental_assistance",
            "availability": "official_dataset",
            "access": "Use published HUD datasets; area, bedroom count, and data year matter.",
            "url": "https://www.huduser.gov/portal/datasets/fmr.html",
        },
        {
            "id": "hud_pha",
            "name": "HUD Public Housing Agency directory",
            "category": "rental_assistance",
            "availability": "official_dataset",
            "access": "Verify the administering agency and jurisdiction; waitlist and open-voucher counts may not be published.",
            "url": "https://www.hud.gov/program_offices/public_indian_housing/pha/contacts",
        },
        {
            "id": "county_records",
            "name": "County assessor, tax-sale, and code-enforcement records",
            "category": "property_leads",
            "availability": "jurisdiction_specific",
            "access": "Add an official source URL or import a county-provided CSV; county formats and publication vary.",
            "url": None,
        },
        {
            "id": "insurance",
            "name": "Property insurance",
            "category": "operating_cost",
            "availability": "quote_or_user_estimate",
            "access": "No comprehensive public national quote source; enter a dated insurer quote or clearly labeled assumption.",
            "url": None,
        },
    ]


async def _fetch_population(client: httpx.AsyncClient, year: int, state_fips: str, county_fips: str):
    params = {
        "get": "NAME,B01003_001E",
        "for": f"county:{county_fips}",
        "in": f"state:{state_fips}",
    }
    response = await client.get(f"{ACS_BASE}/{year}/acs/acs5", params=params)
    response.raise_for_status()
    rows = response.json()
    if not isinstance(rows, list) or len(rows) < 2 or len(rows[1]) < 2:
        raise ValueError(f"Census ACS returned no population estimate for county FIPS {state_fips}{county_fips}")
    try:
        return str(rows[1][0]), int(rows[1][1])
    except (TypeError, ValueError, IndexError) as error:
        raise ValueError(f"Census ACS returned an invalid population estimate for {year}") from error


async def fetch_acs_population(
    state_fips: str,
    county_fips: str,
    client: httpx.AsyncClient | None = None,
    current_year: int | None = None,
):
    if not re.fullmatch(r"\d{2}", state_fips) or not re.fullmatch(r"\d{3}", county_fips):
        raise ValueError("State FIPS must contain 2 digits and county FIPS must contain 3 digits")

    current_year = current_year or int(os.getenv("CENSUS_ACS_YEAR", "2024"))
    previous_year = current_year - 5
    owns_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=20)
    try:
        county_name, current_population = await _fetch_population(
            client, current_year, state_fips, county_fips
        )
        _, previous_population = await _fetch_population(
            client, previous_year, state_fips, county_fips
        )
    finally:
        if owns_client:
            await client.aclose()

    if previous_population <= 0:
        raise ValueError("Census ACS prior population is not positive; growth cannot be calculated")
    return {
        "county_name": county_name,
        "county_fips": f"{state_fips}{county_fips}",
        "population_current": current_population,
        "population_previous": previous_population,
        "population_growth_percent": round(
            (current_population - previous_population) / previous_population * 100,
            2,
        ),
        "current_year": current_year,
        "previous_year": previous_year,
        "source_name": "U.S. Census Bureau American Community Survey 5-year estimates",
        "source_url": (
            f"{ACS_BASE}/{current_year}/acs/acs5?"
            f"{urlencode({'get': 'NAME,B01003_001E', 'for': f'county:{county_fips}', 'in': f'state:{state_fips}'})}"
        ),
    }
