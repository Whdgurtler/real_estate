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
            "availability": "automated_daily",
            "access": "Public API; daily refresh for saved properties with a valid county FIPS code.",
            "url": "https://api.census.gov/data.html",
        },
        {
            "id": "fbi_cde",
            "name": "FBI Crime Data Explorer",
            "category": "crime",
            "availability": "agency_mapping_required",
            "access": "Official UCR/NIBRS data is reported by law-enforcement agency, not by property neighborhood. API key and verified ORI-to-market mapping are required; do not treat an agency rate as a block-level rate.",
            "url": "https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi",
        },
        {
            "id": "hud_fmr",
            "name": "HUD Fair Market Rents",
            "category": "rental_assistance",
            "availability": "automated_with_api_key",
            "access": "Daily API enrichment is enabled with HUD_API_KEY for saved properties with a ZIP code and bedroom count. FMR is a screening benchmark, not a PHA payment standard or rent approval.",
            "url": "https://www.huduser.gov/portal/dataset/fmr-api.html",
        },
        {
            "id": "hud_pha",
            "name": "HUD Public Housing Agency directory",
            "category": "rental_assistance",
            "availability": "jurisdiction_verification",
            "access": "Verify coverage, payment standards, and waitlist status with the administering PHA. Open-voucher counts are not consistently published and remain unknown unless a source reports them.",
            "url": "https://www.hud.gov/program_offices/public_indian_housing/pha/contacts",
        },
        {
            "id": "county_records",
            "name": "County assessor, tax-sale, code-enforcement, and foreclosure records",
            "category": "property_leads",
            "availability": "configurable_daily_feed",
            "access": "The five-state priority directory lists 599 Census county-equivalents in AL, AR, MO, OH, and TX. It includes assessor, tax-sale, code-enforcement, foreclosure, and pre-foreclosure discovery links. Configure Socrata, ArcGIS, or JSON API feeds by county/category only after verifying an authorized local endpoint; code enforcement is frequently municipal.",
            "url": "https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt",
        },
        {
            "id": "alabama_assessor_directory",
            "name": "Alabama Department of Revenue county assessment records",
            "category": "assessor",
            "availability": "county_office_directory",
            "access": "Official county-by-county assessor/revenue offices and assessment record portals.",
            "url": "https://www.revenue.alabama.gov/property-tax/county-offices-appraisal-assessment-records/",
        },
        {
            "id": "arkansas_county_directory",
            "name": "Association of Arkansas Counties",
            "category": "assessor",
            "availability": "county_office_directory",
            "access": "County profiles link county government websites and local elected-office contacts; property feed/API access must be confirmed with each jurisdiction.",
            "url": "https://www.arcounties.org/counties/",
        },
        {
            "id": "ohio_auditor_directory",
            "name": "County Auditors' Association of Ohio",
            "category": "assessor",
            "availability": "county_office_directory",
            "access": "County auditor directory links county-specific auditor pages and local sites; feeds remain county-specific.",
            "url": "https://caao.org/auditors-directory/",
        },
        {
            "id": "missouri_assessor_directory",
            "name": "Missouri State Tax Commission Assessor Directory",
            "category": "assessor",
            "availability": "state_directory",
            "access": "Official statewide assessor directory; verify the current portal and machine-readable data endpoint for each county.",
            "url": "https://stc.mo.gov/assessor/assessor-directory/",
        },
        {
            "id": "regrid_parcels",
            "name": "Regrid nationwide parcel API",
            "category": "assessor_parcel",
            "availability": "commercial_subscription",
            "access": "Nationwide parcel boundaries and property attributes are available under provider terms. Subscription credentials and licensing are required; configure an authorized JSON API feed after confirming its schema and permitted use.",
            "url": "https://regrid.com/api",
        },
        {
            "id": "tax_sale_provider",
            "name": "TaxLienSimple tax-sale data API",
            "category": "property_leads",
            "availability": "provider_api_key_required",
            "access": "Optional commercial inventory. Parcel API requires a subscription/API key; its documented feed omits owner contact details and does not replace title or lien review. Configure as a JSON API feed using a server-side auth environment variable.",
            "url": "https://taxliensimple.com/data-api",
        },
        {
            "id": "insurance",
            "name": "Property insurance",
            "category": "operating_cost",
            "availability": "quote_or_csv",
            "access": "No comprehensive public national property-level quote API was identified. Use a dated insurer/broker quote or attributed CSV estimate; the system will not fabricate an insurance premium.",
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
    period_years = current_year - previous_year
    population_change_percent = (current_population - previous_population) / previous_population * 100
    return {
        "county_name": county_name,
        "county_fips": f"{state_fips}{county_fips}",
        "population_current": current_population,
        "population_previous": previous_population,
        "population_growth_percent": round(
            ((current_population / previous_population) ** (1 / period_years) - 1) * 100,
            2,
        ),
        "population_change_percent": round(population_change_percent, 2),
        "period_years": period_years,
        "current_year": current_year,
        "previous_year": previous_year,
        "source_name": "U.S. Census Bureau American Community Survey 5-year estimates",
        "source_url": (
            f"{ACS_BASE}/{current_year}/acs/acs5?"
            f"{urlencode({'get': 'NAME,B01003_001E', 'for': f'county:{county_fips}', 'in': f'state:{state_fips}'})}"
        ),
    }
