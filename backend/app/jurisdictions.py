from pathlib import Path
from urllib.parse import quote, quote_plus


PRIORITY_STATES = {
    "AR": {"name": "Arkansas", "fips": "05"},
    "AL": {"name": "Alabama", "fips": "01"},
    "OH": {"name": "Ohio", "fips": "39"},
    "MO": {"name": "Missouri", "fips": "29"},
    "TX": {"name": "Texas", "fips": "48"},
}

COUNTY_SOURCE_DIRECTORIES = {
    "AL": {
        "assessor": (
            "Alabama Department of Revenue county appraisal and assessment records",
            "https://www.revenue.alabama.gov/property-tax/county-offices-appraisal-assessment-records/",
            "The state directory has a county-specific section and links to local assessment portals; confirm access and whether a documented export/API exists.",
            "directory_found",
        ),
        "tax_sale": (
            "Alabama Department of Revenue weekly tax-delinquent property transcripts",
            "https://www.revenue.alabama.gov/property-tax/tax-delinquent-property-and-land-sales/",
            "The Department of Revenue publishes state-held tax-delinquent property transcripts for all 67 counties as 68 PDFs; Jefferson is split into Birmingham and Bessemer. The page says transcripts are updated weekly and explicitly says they do not contain physical addresses. These are state-inventory properties, not upcoming county auction calendars; PDF parsing and parcel-address matching are required.",
            "needs_feed_verification",
        ),
        "code_enforcement": (
            "Alabama Department of Revenue county offices directory",
            "https://www.revenue.alabama.gov/property-tax/county-offices-appraisal-assessment-records/",
            "Code enforcement is typically a city or municipal service. Confirm the enforcing city/agency for each property; this county assessor directory is only a county starting point.",
            "municipal_scope",
        ),
        "foreclosure": (
            "Alabama Public Notice | Alabama Press Association",
            "https://www.alabamapublicnotices.com/",
            "The site offers a Foreclosures category and county search and says it receives newspaper uploads daily from participating newspapers. Complete county coverage is unverified. Its Terms prohibit scraping, spidering, automated collection, and commercial exploitation; do not ingest without written authorization. Foreclosure-sale notices are not pre-foreclosure notices.",
            "needs_feed_verification",
        ),
        "pre_foreclosure": (
            "Alabama Public Notice and county offices",
            "https://www.alabamapublicnotices.com/",
            "No complete statewide pre-foreclosure/default-notice feed was verified. Foreclosure-sale notices are not evidence of earlier default. The public-notice site's Terms prohibit scraping and automated commercial collection; verify county probate/recording sources and permitted access independently.",
            "needs_feed_verification",
        ),
    },
    "AR": {
        "assessor": (
            "Association of Arkansas Counties county directory",
            "https://www.arcounties.org/counties/",
            "The directory links county profile pages with official county contacts and websites. County assessor websites and data feeds are managed locally.",
            "directory_found",
        ),
        "tax_sale": (
            "Arkansas Commissioner of State Lands public auction catalog",
            "https://cosl.org/Home/Contents",
            "The Commissioner of State Lands handles tax-delinquent property certified to the state. The public auction catalog and post-auction list are statewide. On 2026-10-19, the post-auction list reported 3,036 parcels in 53 of 75 counties, with ongoing bids in 40 counties; the 2026-11-10 catalog download contained no parcel rows. The JSON grid route is undocumented, the listings lack situs addresses, and no commercial scraping terms were found. This source is verified for discovery, not ready for automated ingestion.",
            "needs_feed_verification",
        ),
        "code_enforcement": (
            "Association of Arkansas Counties county directory",
            "https://www.arcounties.org/counties/",
            "Code enforcement and building inspections may be provided by cities rather than counties. Identify the relevant city/town office for each property.",
            "municipal_scope",
        ),
        "foreclosure": (
            "Arkansas Press Association public notices",
            "https://www.arkansaspublicnotices.com/",
            "The statewide search offers a Foreclosure category and says newspapers upload notices daily, but not all newspapers must upload and its database is not the official publication. Terms restrict use to personal, non-commercial purposes and prohibit copying or replication; do not ingest for this commercial platform without written permission. Verify any county source independently.",
            "needs_feed_verification",
        ),
        "pre_foreclosure": (
            "Arkansas Judiciary and county offices",
            "https://arcourts.gov/",
            "No complete statewide pre-foreclosure feed was verified. Arkansas Public Notices contains newspaper legal notices but is not a substitute for official publication and its terms prohibit commercial copying; verify county recorder/court sources and access rights independently.",
            "needs_feed_verification",
        ),
    },
    "OH": {
        "assessor": (
            "County Auditors' Association of Ohio directory",
            "https://caao.org/auditors-directory/",
            "The association directory has a page for each county auditor and links to local auditor websites; assessors and parcel systems are county-operated.",
            "directory_found",
        ),
        "tax_sale": (
            "County Treasurers Association of Ohio directory",
            "https://www.ohiocountytreasurers.org/aws/CTAO/pt/sp/layout_directory-treasurer?get_content_from_session=1",
            "The association's June 1, 2026 PDF directory lists treasurer profiles for all 88 Ohio counties, but only 48 entries include a website field. A 2026-10-19 link check reached 41 of those websites: 39 returned HTTP 200 to HEAD, while GET confirmed Ashtabula and Franklin despite HEAD 405/403. Greene, Lawrence, Licking, Montgomery, and Portage returned 403; Fairfield DNS did not resolve; Monroe returned 404. These are office contacts, not tax-sale calendars or machine-readable feeds; verify each county's sale postings, coverage, and access terms.",
            "needs_feed_verification",
        ),
        "code_enforcement": (
            "County Auditors' Association of Ohio directory",
            "https://caao.org/auditors-directory/",
            "Code enforcement is usually a municipal building/zoning responsibility, not a county-auditor function. Locate the city/town enforcing authority.",
            "municipal_scope",
        ),
        "foreclosure": (
            "Public Notices Ohio | Ohio News Media Association",
            "https://www.publicnoticesohio.com/",
            "The site has Foreclosure and Sheriff's Sales searches and says newspapers upload notices daily, but also says its goal is to carry every Ohio public notice in the future; completeness is not established. Its Terms limit use to personal, non-commercial use. The State-contracted Realauction portal at https://franklin.sheriffsaleauction.ohio.gov/ showed a selector for 87 other county portals; a Franklin jump from Medina resolved, but this does not establish all destinations are active feeds. The Franklin User Agreement limits licensed information use to purchasing property and prohibits use, alteration, sale, or distribution without express written consent. Do not ingest without written authorization and county-specific terms review. The Buckeye State Sheriffs' Association says it has no foreclosure or sheriff-sale information.",
            "needs_feed_verification",
        ),
        "pre_foreclosure": (
            "Buckeye State Sheriffs' Association county contact directory",
            "https://buckeyesheriffs.org/contact-your-sheriff/",
            "The association's map is a contact directory only. Its homepage says each local sheriff exclusively operates their office and the association has no process-server, foreclosure, or sheriff-sale information. Verify county court filings and permitted access directly; no complete statewide pre-foreclosure feed was verified.",
            "needs_feed_verification",
        ),
    },
    "MO": {
        "assessor": (
            "Missouri State Tax Commission assessor directory",
            "https://stc.mo.gov/assessor/assessor-directory/",
            "The State Tax Commission publishes the assessor directory; use the Missouri Association of Counties directory to locate county offices. Verify each county portal's current URL and data access.",
            "directory_found",
        ),
        "tax_sale": (
            "Missouri Association of Counties county office directory",
            "https://www.mocounties.com/member-counties",
            "Real-property tax sales are administered by county collectors. The county-specific directory profile lists local offices and is not a sale calendar. The Missouri Press Association public-notice site has a Tax Sale category, but it is not a verified complete collector calendar or machine-readable feed. Its Terms permit personal, non-commercial page viewing only and prohibit scraping, automation, and commercial reuse; verify each county collector's official sale list.",
            "needs_feed_verification",
        ),
        "code_enforcement": (
            "Missouri Association of Counties member-county directory",
            "https://www.mocounties.com/member-counties",
            "Code enforcement is generally administered by cities or other local authorities. Identify the enforcing municipality and its records portal.",
            "municipal_scope",
        ),
        "foreclosure": (
            "Missouri Association of Counties county office directory",
            "https://www.mocounties.com/member-counties",
            "Sheriff and court foreclosure sales are locally administered. The county-specific directory profile lists local offices but is not a sale calendar. Missouri Public Notices offers Foreclosure and Sheriff's Sales searches; its Terms disclaim responsibility for timely publication, permit personal, non-commercial page viewing only, and prohibit scraping, automation, and commercial reuse. Verify each county's official sale source.",
            "needs_feed_verification",
        ),
        "pre_foreclosure": (
            "Missouri Association of Counties county office directory",
            "https://www.mocounties.com/member-counties",
            "No complete statewide pre-foreclosure/default-notice feed was verified. County profiles provide recorder and circuit-clerk contacts, not a public default-notice feed; verify the county record type, notice coverage, and permitted access.",
            "needs_feed_verification",
        ),
    },
    "TX": {
        "assessor": (
            "Texas Comptroller taxing-unit county reference",
            "https://comptroller.texas.gov/taxes/property-tax/county-directory/",
            "This is a county/taxing-unit reference, not a verified appraisal-district feed. Use the county-specific search to locate the local appraisal district and verify its public-record access and feed availability.",
            "needs_feed_verification",
        ),
        "tax_sale": (
            "Texas Association of Counties",
            "https://www.county.org/",
            "Delinquent-property sales are handled locally by county officials. Texas Public Notices is a statewide newspaper-notice search, not a tax-auction calendar; its filter exposed 249 named counties plus Unknown on 2026-10-19, omitting Glasscock, King, Loving, McMullen, and Terrell. Its Terms prohibit scraping, all automated collection, and commercial reuse, with stated liquidated damages. Verify the county's official sale source.",
            "needs_feed_verification",
        ),
        "code_enforcement": (
            "Texas Municipal League",
            "https://www.tml.org/",
            "Code enforcement is generally a city/municipal responsibility. Use the county-specific city search to identify the enforcing office and its records portal.",
            "municipal_scope",
        ),
        "foreclosure": (
            "Texas Public Notices and local trustee/sheriff offices",
            "https://www.county.org/",
            "Texas Public Notices provides a statewide newspaper-notice search and a county filter, but Glasscock, King, Loving, McMullen, and Terrell were absent from its selector on 2026-10-19; this does not prove complete sale coverage. Its Terms limit use to personal, non-commercial use and prohibit automated collection, scraping, and database reuse; do not ingest without written authorization. Confirm each county's official trustee, sheriff, or constable sale source.",
            "needs_feed_verification",
        ),
        "pre_foreclosure": (
            "Texas Association of Counties and local recording offices",
            "https://www.county.org/",
            "Pre-foreclosure/default notices are not a unified county feed. Identify the relevant county recording/court source and verify notice coverage and permitted access.",
            "needs_feed_verification",
        ),
    },
}

ALABAMA_TAX_TRANSCRIPT_CODES = {
    "AUTAUGA": "04",
    "BALDWIN": "05",
    "BARBOUR": "06",
    "BIBB": "07",
    "BLOUNT": "08",
    "BULLOCK": "09",
    "BUTLER": "10",
    "CALHOUN": "11",
    "CHAMBERS": "12",
    "CHEROKEE": "13",
    "CHILTON": "14",
    "CHOCTAW": "15",
    "CLARKE": "16",
    "CLAY": "17",
    "CLEBURNE": "18",
    "COFFEE": "19",
    "COLBERT": "20",
    "CONECUH": "21",
    "COOSA": "22",
    "COVINGTON": "23",
    "CRENSHAW": "24",
    "CULLMAN": "25",
    "DALE": "26",
    "DALLAS": "27",
    "DEKALB": "28",
    "ELMORE": "29",
    "ESCAMBIA": "30",
    "ETOWAH": "31",
    "FAYETTE": "32",
    "FRANKLIN": "33",
    "GENEVA": "34",
    "GREENE": "35",
    "HALE": "36",
    "HENRY": "37",
    "HOUSTON": "38",
    "JACKSON": "39",
    "LAMAR": "40",
    "LAUDERDALE": "41",
    "LAWRENCE": "42",
    "LEE": "43",
    "LIMESTONE": "44",
    "LOWNDES": "45",
    "MACON": "46",
    "MADISON": "47",
    "MARENGO": "48",
    "MARION": "49",
    "MARSHALL": "50",
    "MONROE": "51",
    "MORGAN": "52",
    "PERRY": "53",
    "PICKENS": "54",
    "PIKE": "55",
    "RANDOLPH": "56",
    "RUSSELL": "57",
    "SHELBY": "58",
    "ST. CLAIR": "59",
    "SUMTER": "60",
    "TALLADEGA": "61",
    "TALLAPOOSA": "62",
    "TUSCALOOSA": "63",
    "WALKER": "64",
    "WASHINGTON": "65",
    "WILCOX": "66",
    "WINSTON": "67",
    "MOBILE": "02",
    "MONTGOMERY": "03",
}

TESTED_PUBLIC_ENDPOINTS_BY_FIPS = {
    "01073": {
        "assessor": {
            "endpoint_url": (
                "https://jccgis.jccal.org/server/rest/services/Basemap/Parcels/"
                "MapServer/0"
            ),
            "endpoint_info_url": (
                "https://www.arcgis.com/home/item.html?"
                "id=ac6ec7f4f83d4715a45acc8990b8b8c8"
            ),
            "endpoint_status": "freshness_review_required",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 410119,
            "endpoint_scope": "Jefferson County",
            "endpoint_note": (
                "The official county parcel MapServer and a one-record query through "
                "this application's connector responded; the count-only query returned "
                "410,119 parcels. The county says the layer is generated nightly from "
                "Addressing, Tax Assessor, and Board of Equalization data; it includes "
                "address, city, state, and AssdValue fields. Its text MaintDate field's "
                "maximum observed value was September 9, 2026, and is not documented as "
                "a source-update cursor. The publisher disclaims accuracy warranties. "
                "This is a parcel inventory, not a distressed-lead feed; the current "
                "5,000-record connector cap and lack of incremental cursor prevent a "
                "complete daily county sync."
            ),
        }
    },
    "01097": {
        "assessor": {
            "endpoint_url": (
                "https://services8.arcgis.com/HND1NcQt6vgOGn1z/arcgis/rest/services/"
                "MCRC_Public_Parcels/FeatureServer/0"
            ),
            "endpoint_info_url": (
                "https://www.arcgis.com/home/item.html?"
                "id=07c93ca64bbf4fb8a8d49b7ea80ef067"
            ),
            "endpoint_status": "terms_review_required",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 214040,
            "endpoint_scope": "Mobile County",
            "endpoint_note": (
                "The direct ArcGIS layer and a one-record query through this application's "
                "connector responded; the count-only query returned 214,040 parcels. The "
                "publisher identifies this as tax-purpose parcel data. The tested layer has "
                "situs address, city, and state fields, but no assessed-value field. An "
                "explicit commercial-use license and daily publication cadence were not "
                "confirmed, so do not enable it as a production feed yet."
            ),
        }
    },
    "05007": {
        "assessor": {
            "endpoint_url": (
                "https://services1.arcgis.com/G4bYaaas92zuKaUR/arcgis/rest/services/"
                "Benton_County_Parcels/FeatureServer/0"
            ),
            "endpoint_info_url": (
                "https://www.arcgis.com/home/item.html?"
                "id=5572f2d79d094386a5f6e5160d6a78ca"
            ),
            "endpoint_status": "restricted_planning",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 174765,
            "endpoint_scope": "Benton County",
            "endpoint_note": (
                "The direct ArcGIS layer and a one-record query through this application's "
                "connector responded; the count-only query returned 174,765 parcels. The "
                "publisher says it is used exclusively for GIS operations for its member "
                "cities and is updated monthly. Do not use it commercially without written "
                "authorization. It includes assessment values but no situs city/state fields."
            ),
        }
    },
    "48113": {
        "code_enforcement": {
            "endpoint_url": (
                "https://www.dallasopendata.com/resource/xrzj-c8ez.json"
            ),
            "endpoint_info_url": (
                "https://www.dallasopendata.com/api/views/xrzj-c8ez.json"
            ),
            "endpoint_status": "historical_not_daily",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 135257,
            "endpoint_scope": "City of Dallas only",
            "endpoint_note": (
                "The public Socrata API and a one-record query through this application's "
                "connector responded; the count query returned 135,257 records. The "
                "publisher describes these as residential code-violation points from "
                "January 2015 through June 2017; the dataset was last updated in 2018. It "
                "is historical, covers only the City of Dallas, and lacks mapped city/state "
                "fields, so it is not a current daily lead feed."
            ),
        }
    },
    "48201": {
        "assessor": {
            "endpoint_url": (
                "https://www.gis.hctx.net/arcgishcpid/rest/services/HCAD/Parcels/"
                "MapServer/0"
            ),
            "endpoint_info_url": (
                "https://www.arcgis.com/home/item.html?"
                "id=c00366c724dc47e3a550fa494d214463"
            ),
            "endpoint_status": "volume_and_schema_review_required",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 1551736,
            "endpoint_scope": "Harris County",
            "endpoint_note": (
                "The official Harris County GIS MapServer and a one-record query through "
                "this application's connector responded; the count-only query returned "
                "1,551,736 parcels. The ArcGIS item says the data is updated bi-weekly and "
                "is for locating properties, not an official tax designation. It includes "
                "appraised-value and tax-value fields, but site address components must be "
                "combined and there is no site-state field. The layer caps responses at "
                "2,000 records; the current connector has no incremental cursor and cannot "
                "safely backfill this dataset daily."
            ),
        }
    },
    "39049": {
        "assessor": {
            "endpoint_url": (
                "https://gis.franklincountyohio.gov/hosting/rest/services/"
                "ParcelFeatures/Parcel_Features/MapServer/0"
            ),
            "endpoint_info_url": (
                "https://www.arcgis.com/home/item.html?"
                "id=3b1c75018fca40c8b24083fd48197e74"
            ),
            "endpoint_status": "cadence_and_schema_review_required",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 494902,
            "endpoint_scope": "Franklin County",
            "endpoint_note": (
                "The official Franklin County Auditor layer and a one-record query "
                "through this application's connector responded; the count-only query "
                "returned 494,902 parcels. The item describes county parcel boundaries "
                "and attributes and recommends the Auditor's direct-download site for "
                "the full dataset. Fields include SITEADDRESS, ZIPCD, and TOTVALUEBASE, "
                "but no site-city field or refresh cadence is documented. The publisher "
                "says the Auditor's primary information source should be consulted and "
                "disclaims legal responsibility. The layer caps responses at 3,000 "
                "records; the current connector lacks a full-inventory backfill and "
                "incremental cursor, so this is not a daily feed or acquisition-lead list."
            ),
        }
    },
    "39061": {
        "code_enforcement": {
            "endpoint_url": "https://data.cincinnati-oh.gov/resource/cncm-znd6.json",
            "endpoint_info_url": (
                "https://data.cincinnati-oh.gov/api/views/cncm-znd6.json"
            ),
            "endpoint_status": "schema_and_delta_review_required",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 771669,
            "endpoint_scope": "City of Cincinnati",
            "endpoint_note": (
                "The public Socrata API and a one-record query through this application's "
                "connector responded; the catalog count was 771,669 and the dataset was "
                "updated October 19, 2026. The City describes complaints, inspections, and "
                "violations across residential and commercial properties. The layer has "
                "full_address and city/county fields but no separate city/state fields; "
                "Socrata metadata declares the dataset Public Domain. "
                "Daily ingestion also requires a source-update cursor; the current 5,000 "
                "record cap cannot backfill this dataset."
            ),
            "additional_endpoints": [
                {
                    "name": "Cincinnati Private Lot Abatement Program",
                    "url": "https://data.cincinnati-oh.gov/resource/pk9w-99n6.json",
                    "info_url": (
                        "https://data.cincinnati-oh.gov/api/views/pk9w-99n6.json"
                    ),
                    "last_verified": "2026-10-19",
                    "record_count": 23901,
                    "scope": "City of Cincinnati",
                    "note": (
                        "The public API and a one-record query through the application "
                        "connector responded. The dataset was updated October 19, 2026 and "
                        "covers private lots in the city's abatement program. It exposes a "
                        "full address and coordinates but no separate city/state fields; "
                        "daily incremental ingestion is not implemented."
                    ),
                }
            ],
        }
    },
    "29189": {
        "assessor": {
            "endpoint_url": (
                "https://services2.arcgis.com/w657bnjzrjguNyOy/arcgis/rest/services/"
                "STLCO_STC_Parcels_Revised/FeatureServer/0"
            ),
            "endpoint_info_url": (
                "https://www.arcgis.com/home/item.html?"
                "id=06d43012de4a484ab004f5b34ea0e8e8"
            ),
            "endpoint_status": "historical_not_daily",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 400796,
            "endpoint_scope": "St. Louis County",
            "endpoint_note": (
                "The public St. Louis County GIS layer and a one-record query through "
                "this application's connector responded; the count-only query returned "
                "400,796 parcels. It is attributed to the County Assessor and has address, "
                "ZIP, municipality, and TOTASSMT fields, but no state field. A maximum "
                "TAXYR aggregate returned 2023; the publisher provides no refresh cadence "
                "and advises validating the primary source before business decisions. "
                "The layer caps responses at 2,000 records, and the current connector "
                "lacks a full-inventory backfill and incremental cursor."
            ),
        }
    },
    "29095": {
        "code_enforcement": {
            "endpoint_url": "https://data.kcmo.org/resource/vq3e-m9ge.json",
            "endpoint_info_url": "https://data.kcmo.org/api/views/vq3e-m9ge.json",
            "endpoint_status": "freshness_review_required",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 174999,
            "endpoint_scope": "Kansas City, Missouri only",
            "endpoint_note": (
                "The public Socrata API and a one-record query through this application's "
                "connector responded; the catalog count was 174,999. The City of Kansas "
                "City Neighborhood Preservation Division publishes street address, case "
                "status, and violation dates. The dataset was last updated April 30, 2026; "
                "the portal declares it Public Domain U.S. Government, but daily freshness "
                "is not documented. It is city-scoped, does not cover all "
                "of Jackson County, and has no separate city/state fields. An aggregate "
                "date check found one future-dated record and 35 records with no date."
            ),
        }
    },
    "48329": {
        "code_enforcement": {
            "endpoint_url": (
                "https://services.arcgis.com/0H6bQdxd9223gQB5/arcgis/rest/services/"
                "Inspections/FeatureServer/0"
            ),
            "endpoint_status": "historical_not_daily",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 293437,
            "endpoint_scope": "City of Midland only",
            "endpoint_note": (
                "The City of Midland GIS ArcGIS layer identifies these as code-enforcement "
                "inspection work orders. The direct service and one-record query through the "
                "application connector responded; the count-only query returned 293,437. "
                "The latest last_edited_date returned by a maximum-date query was March 4, "
                "2026. The layer has addresses but no separate city/state fields, and the "
                "current 5,000-record cap cannot backfill it."
            ),
        }
    },
}

TESTED_STATEWIDE_ENDPOINTS = {
    "OH": {
        "assessor": {
            "endpoint_url": (
                "https://services2.arcgis.com/MlJ0G8iWUyC7jAmu/arcgis/rest/services/"
                "OhioStatewidePacels_full_view/FeatureServer/0"
            ),
            "endpoint_info_url": (
                "https://www.arcgis.com/home/item.html?"
                "id=26ab5fad8d5d4258a7492a14de83bc0e"
            ),
            "endpoint_status": "cadence_and_schema_review_required",
            "endpoint_last_verified": "2026-10-19",
            "endpoint_record_count": 6313610,
            "endpoint_scope": "Ohio statewide",
            "endpoint_note": (
                "The direct ArcGIS layer and a one-record query through this application's "
                "connector responded; the count-only query returned 6,313,610 parcels and "
                "the layer has a county field. The item describes a public view of "
                "county-maintained parcel records, but its snippet says it was updated "
                "January 21, 2024. The tested layer has situs address and county but no "
                "assessed-value or situs-city field; CAMA data is related separately. This "
                "is not a verified daily incremental feed or a complete underwriting source."
            ),
        }
    }
}


def county_jurisdictions():
    """Return Census county equivalents in the five launch states."""
    try:
        with open(
            Path(__file__).parent / "data" / "priority_counties.csv",
            encoding="utf-8",
        ) as source:
            header = source.readline().strip()
            if header != "state,state_name,county,county_fips":
                raise ValueError("County registry CSV has an invalid header.")
            counties = []
            for line_number, line in enumerate(source, start=2):
                values = line.rstrip("\r\n").split(",", 3)
                if len(values) != 4 or values[0] not in PRIORITY_STATES:
                    raise ValueError(f"County registry CSV is invalid at line {line_number}.")
                state, state_name, county, county_fips = values
                if len(county_fips) != 5 or not county_fips.isdigit():
                    raise ValueError(f"County FIPS is invalid at line {line_number}.")
                counties.append(
                    {
                        "state": state,
                        "state_name": state_name,
                        "county": county,
                        "county_fips": county_fips,
                    }
                )
    except OSError as error:
        raise RuntimeError("Priority-county registry could not be read.") from error
    return counties


def county_source_links(
    state: str,
    county: str,
    county_fips: str | None = None,
) -> dict[str, dict[str, str]]:
    state_name = PRIORITY_STATES[state]["name"]
    county_name = county.removesuffix(" County").removesuffix(" city")
    search_terms = {
        "assessor": f'"{county_name}" "{state_name}" county assessor parcel property search',
        "tax_sale": f'"{county_name}" "{state_name}" county official tax sale auction property',
        "code_enforcement": (
            f'"{county_name}" "{state_name}" county city code enforcement property violations'
        ),
        "foreclosure": (
            f'"{county_name}" "{state_name}" county official foreclosure sheriff sale auction'
        ),
        "pre_foreclosure": (
            f'"{county_name}" "{state_name}" county official lis pendens foreclosure notice records'
        ),
    }
    county_profiles = {
        "AL": {
            "assessor": (
                "https://www.revenue.alabama.gov/property-tax/"
                f"county-offices-appraisal-assessment-records/#{quote(county_name, safe='')}"
            ),
        },
        "AR": {
            "assessor": (
                "https://www.arcounties.org/counties/"
                f"{county_name.lower().replace(' ', '-').replace('.', '')}/"
            ),
            "tax_sale": "https://cosl.org/Home/Contents",
            "foreclosure": "https://www.arkansaspublicnotices.com/",
        },
        "MO": {
            "tax_sale": "https://www.mopublicnotices.com/",
            "foreclosure": "https://www.mopublicnotices.com/",
            "pre_foreclosure": "https://www.courts.mo.gov/",
        },
        "OH": {
            "assessor": (
                "https://caao.org/auditors-directory/name/"
                f"{county_name.lower().replace(' ', '-')}-county/"
            ),
            "foreclosure": "https://www.publicnoticesohio.com/",
        },
        "TX": {
            "tax_sale": "https://www.texaspublicnotices.com/",
            "foreclosure": "https://www.texaspublicnotices.com/",
        },
    }
    sources = {}
    missouri_county_profile_url = None
    if state == "MO":
        if county_fips == "29510" or county.lower().endswith(" city"):
            missouri_county_profile_url = "https://www.stlouis-mo.gov/"
        elif county_name == "Platte":
            missouri_county_profile_url = "https://www.co.platte.mo.us/"
        else:
            county_slug = county_name.lower().replace(".", "").replace(" ", "-")
            missouri_county_profile_url = (
                f"https://www.mocounties.com/{county_slug}-county"
            )
    for category, (directory_name, directory_url, note, status) in COUNTY_SOURCE_DIRECTORIES[
        state
    ].items():
        source_url = county_profiles.get(state, {}).get(category, directory_url)
        if (
            state == "MO"
            and category in {"tax_sale", "foreclosure", "pre_foreclosure"}
            and missouri_county_profile_url
        ):
            directory_url = missouri_county_profile_url
        if state == "AL" and category == "tax_sale":
            transcript_code = ALABAMA_TAX_TRANSCRIPT_CODES.get(county_name.upper())
            if transcript_code:
                source_url = (
                    "https://www.revenue.alabama.gov/wp-content/uploads/"
                    f"property-tax-transcripts/WWW_TRANS_{transcript_code}.PDF"
                )
        if state == "AL" and county_name == "Autauga":
            if category == "tax_sale":
                directory_name = "Autauga County Revenue Commissioner tax collection information"
                directory_url = "https://autauga.capturecama.com/collection"
                note += (
                    " Autauga County's official Collection Info page says county tax sales "
                    "are held annually for unpaid taxes, with properties advertised in the "
                    "Prattville Progress for three weeks before the sale date and an in-person "
                    "public-outcry auction (usually 10 a.m.) in commission chambers. The page "
                    "does not post a current sale date or list, and no machine-readable feed "
                    "or automated-access authorization was verified. The Alabama DOR eBuy "
                    "filter returned no Autauga state-property auctions on 2026-10-19, but "
                    "eBuy's FAQ says it is not for delinquent county property-tax sales; this "
                    "does not establish county-sale inventory."
                )
            elif category == "foreclosure":
                directory_name = "Autauga County Sheriff's Office"
                directory_url = "https://www.autaugasheriff.org/"
                note += (
                    " The official Sheriff's Office site was reachable, but its public page "
                    "exposed contact and recent-news navigation rather than a verifiable "
                    "foreclosure or sheriff-sale list. No county-specific sale feed was "
                    "verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Autauga County Probate Office online records"
                directory_url = "https://www.ingprobate.com/Autauga_Probate/default.aspx"
                note += (
                    " The official Probate Office links to this portal's Land Records and "
                    "Probate Case Records searches, but no lis-pendens/default index or feed "
                    "was verified. Its Terms and Conditions prohibit automated access, "
                    "monitoring, data extraction/scraping, and automated interactions; do not "
                    "automate this source."
                )
        if state == "AL" and county_name == "Baldwin":
            if category == "tax_sale":
                directory_name = "Baldwin County Revenue Commission tax-lien auction"
                directory_url = (
                    "https://baldwincountyal.gov/government/"
                    "revenue-commission/tax-lien-auction"
                )
                note += (
                    " Baldwin County's official tax-lien auction page says the annual "
                    "auction window is March 1 through June 15 and promises a county property "
                    "list by March 31 with owner, PPIN/parcel, description, appraised value, "
                    "tax district, and delinquent charges. The page still describes the 2025 "
                    "tax-year auction, held online through GovEase beginning March 24, 2026; "
                    "that sale date is past, and no 2026 tax-year sale schedule or current "
                    "list/export/feed was verified on 2026-10-19. GovEase requires bidder "
                    "registration and a deposit; data reuse and automated-access permission "
                    "were not established. The Alabama DOR transcript remains a separate "
                    "state-held inventory, not this county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Baldwin County Sheriff's Office sale notices"
                directory_url = "https://sheriff.baldwincountyal.gov/"
                note += (
                    " An official Sheriff's Office notice dated September 28, 2026, set an "
                    "October 15, 2026 execution sale for a box trailer under a District Court "
                    "judgment; this is a personal-property execution sale, not a real-estate "
                    "foreclosure. No residential foreclosure list or complete county sale feed "
                    "was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Baldwin County Probate Office Recording Division"
                directory_url = (
                    "https://baldwincountyal.gov/government/probate-office/recording"
                )
                note += (
                    " The official Recording Division page says its website offers searchable "
                    "grantor/grantee and reception-number lookup for deed and mortgage indexes "
                    "from 1899 to present, with document viewing/printing. This is a public "
                    "records search, not a verified lis-pendens/default list; no export/API or "
                    "automated-access authorization was established."
                )
        if state == "AL" and county_name == "Barbour":
            if category == "tax_sale":
                directory_name = "Barbour County Revenue Commissioner portal"
                directory_url = "https://barbour.capturecama.com/"
                note += (
                    " The official county Revenue Commissioner portal exposes Delinquent, "
                    "Redemption, and Insolvent searches. Its Collection Info page describes "
                    "tax collection and delinquency but does not publish an upcoming tax-sale "
                    "date or sale list. No machine-readable auction feed or automated-access "
                    "authorization was verified; the Alabama DOR transcript is separate "
                    "state-held inventory, not a county sale calendar."
                )
            elif category == "foreclosure":
                directory_name = "Barbour County Sheriff's Office"
                directory_url = "https://barbourcountysheriff.org/"
                note += (
                    " The Sheriff's Office website and its public services page were reachable, "
                    "but no real-estate foreclosure or sheriff-sale calendar/list was verified. "
                    "No county-specific sale feed was found."
                )
            elif category == "pre_foreclosure":
                directory_name = "Barbour County Probate Office"
                directory_url = "https://www.barbourcountyal.gov/172/Probate-Office"
                note += (
                    " The official Probate Office page describes online access to office "
                    "services, and its online-services portal advertises land-record and "
                    "probate-case searches. No lis-pendens/default index, pre-foreclosure "
                    "feed, export/API, or automated-access authorization was verified."
                )
        if state == "AL" and county_name == "Bibb":
            if category == "tax_sale":
                directory_name = "Bibb County Tax Assessor/Collector contact"
                directory_url = "https://bibbal.com/"
                note += (
                    " The official County Commission home page lists the Tax Assessor/"
                    "Collector contact but does not publish a county tax-sale date or list. "
                    "The Alabama DOR transcript is state-held inventory, not a local auction "
                    "calendar. No county-specific sale feed, current sale list, or automated-"
                    "access authorization was verified."
                )
            elif category == "foreclosure":
                directory_name = "Bibb County Sheriff's Office contact"
                directory_url = "https://bibbal.com/"
                note += (
                    " The official County Commission home page lists the County Sheriff and "
                    "office contact but no real-estate foreclosure or sheriff-sale calendar/"
                    "list. No county-specific sale feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Bibb County Probate Office"
                directory_url = "https://bibbal.com/the-probate-office/"
                note += (
                    " The official Probate Office page links to online records for 1996 to "
                    "present and a separate historical-record service for 1819 to 1995. These "
                    "are records searches, not a verified lis-pendens/default list; no "
                    "pre-foreclosure feed, export/API, or automated-access authorization was "
                    "verified."
                )
        if state == "AL" and county_name == "Blount":
            if category == "tax_sale":
                directory_name = "Blount County Revenue Commission tax-lien auction"
                directory_url = (
                    "https://www.blountrevenue.com/home/property/tax-lien-auction/"
                )
                note += (
                    " The official Revenue Commission page says the 2026 online auction "
                    "was scheduled for March 24, 2026 at 9 a.m. CST, and links to an ALTAGS "
                    "current delinquent-parcel list at "
                    "https://altags.com/blount_license/Delinquent.aspx. The auction date is "
                    "past and no later schedule was posted. No documented download/API, "
                    "complete daily-feed behavior, or automated/commercial-use authorization "
                    "was verified; the Alabama DOR transcript is separate state-held "
                    "inventory, not this county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Blount County Sheriff's Office"
                directory_url = "https://www.blountalsheriff.org/"
                note += (
                    " The official County Commission site links to this Sheriff's Office "
                    "site, but it did not load during verification (transport-level failure/"
                    "timeout). No real-estate foreclosure or sheriff-sale calendar/list was "
                    "verified, and no county-specific sale feed was found."
                )
            elif category == "pre_foreclosure":
                directory_name = "Blount County Probate Office recording and public records"
                directory_url = (
                    "https://www.blountcountyalprobate.com/home/"
                    "recording-public-records-and-forms/"
                )
                note += (
                    " The official Probate Office page links to an ALTAGS online records "
                    "search and county property-tax records. These are public-record searches, "
                    "not a verified lis-pendens/default list or pre-foreclosure feed; no "
                    "export/API or automated-access authorization was verified."
                )
        if state == "AL" and county_name == "Bullock":
            if category == "tax_sale":
                directory_name = "Bullock County Revenue Commissioner tax-sale notice"
                directory_url = "https://bullockcountyalrev.com/faq"
                note += (
                    " The official Revenue Commissioner FAQ, signed September 22, 2023, "
                    "declares a sale for collecting delinquent property taxes beginning with "
                    "the 2023-2024 tax year. It publishes no current sale date or parcel list; "
                    "no machine-readable list, export/API, or automated-access authorization "
                    "was verified. The Alabama DOR transcript is state-held inventory, not a "
                    "local auction list."
                )
            elif category == "foreclosure":
                directory_name = "Bullock County Sheriff's Office"
                directory_url = "https://bullockal.com/sheriff/"
                note += (
                    " The official County Sheriff's Office page lists contact details and a "
                    "permit application, but no real-estate foreclosure or sheriff-sale "
                    "calendar/list. No county-specific sale feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Bullock County Probate online-services portal"
                directory_url = (
                    "https://www.ingprobate.com/bullock_probate/default.aspx"
                )
                note += (
                    " The official online-services portal's legal disclaimer prohibits "
                    "automated systems including bots, spiders, scrapers, and offline readers, "
                    "as well as data extraction and automated navigation/clicks. Treat this as "
                    "manual-only; no lis-pendens/default index, pre-foreclosure feed, export/API, "
                    "or automated-access authorization was verified."
                )
        if state == "AL" and county_name == "Butler":
            if category == "tax_sale":
                directory_name = "Butler County Revenue Commission tax-lien auction"
                directory_url = "https://www.butlercogov.com/revenue-commission"
                note += (
                    " The official Revenue Commission page links to GovEase and posts a "
                    "public notice dated August 26, 2020 declaring a tax-lien auction and "
                    "sale method for delinquent taxes beginning with tax year 2020-2021. "
                    "The page publishes no current auction date or county parcel list; no "
                    "machine-readable feed, export/API, or automated/commercial-use "
                    "authorization was verified. The Alabama DOR transcript is state-held "
                    "inventory, not this county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Butler County Sheriff's-branded foreclosure search"
                directory_url = "https://web.butlersheriff.org:8443/search.aspx"
                note += (
                    " The interactive search page displays sale dates and supports searches "
                    "by case number, property street name, defendant, ZIP code, and date "
                    "range. On 2026-10-19 it showed the next non-tax sale as October 22, 2026 "
                    "and the next tax sale as October 29, 2026. The official County Sheriff "
                    "page is contact-only and does not link to this search portal; no "
                    "completeness, export/API, terms, or automated/commercial-use "
                    "authorization was verified. Treat as manual research only."
                )
            elif category == "pre_foreclosure":
                directory_name = "Butler County Probate online-services portal"
                directory_url = "https://www.ingprobate.com/butler_probate/"
                note += (
                    " The official online-services portal's legal disclaimer prohibits "
                    "automated systems including bots, spiders, scrapers, and offline readers, "
                    "as well as data extraction and automated navigation/clicks. Treat this as "
                    "manual-only; no lis-pendens/default index, pre-foreclosure feed, export/API, "
                    "or automated-access authorization was verified."
                )
        if state == "AL" and county_name == "Calhoun":
            if category == "tax_sale":
                directory_name = "Calhoun County Revenue Commission tax-lien auction"
                directory_url = "https://www.calhouncounty.org/revenue/"
                note += (
                    " The official Revenue Commission page says the county's tax-lien "
                    "auction format took effect with the 2018 tax collection year and links "
                    "a delinquent-property listing at "
                    "https://altags.com/calhoun_revenue/Delinquent.aspx. That ALTAGS list "
                    "was not accessed; its current inventory, completeness as an upcoming "
                    "auction list, format, terms, and automated-use authorization were not "
                    "verified. The Revenue page provides no current sale date or complete "
                    "auction schedule, and the Alabama DOR transcript is state-held inventory, "
                    "not the county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Calhoun County Sheriff's Office property sales"
                directory_url = "https://www.calcoso.org/sale-of-property/"
                note += (
                    " The official Sheriff's Office page describes court-ordered sales of "
                    "property that is seized or levied upon and says notices are often "
                    "published in local newspapers or posted at the courthouse/Sheriff's "
                    "Office. It publishes no current sale date or list; no machine-readable "
                    "feed or automated/commercial-use authorization was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Calhoun County Probate Office public records"
                directory_url = "https://www.calhouncounty.org/probate/"
                note += (
                    " The official Probate Office page directs the public to "
                    "https://probate.calhouncounty.org for records; that portal redirected "
                    "to a sign-in requiring cookies. No unauthenticated lis-pendens/default "
                    "index, pre-foreclosure feed, export/API, or automated-access "
                    "authorization was verified."
                )
        if state == "AL" and county_name == "Chambers":
            if category == "tax_sale":
                directory_name = "Chambers County Revenue Commissioner tax-sale notices"
                directory_url = (
                    "https://www.chamberscountyrevenue.com/home/news/"
                )
                note += (
                    " The official Revenue Commission News page announced a 2024 tax-sale "
                    "auction for April 28, 2025, a date that is past. It links to the "
                    "delinquent real-property list at "
                    "https://www.ingproperty.com/Chambers_Revenue/Delinquent.aspx, but the "
                    "list was not accessed; its currentness, completeness as an upcoming "
                    "auction list, format, terms, and automated/commercial-use authorization "
                    "were not verified. No later sale date or machine-readable feed/export/API "
                    "was verified. The Alabama DOR transcript is state-held inventory, not "
                    "the county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Chambers County Sheriff's Department"
                directory_url = (
                    "https://www.chamberscountyal.gov/departments/"
                    "sheriffs-department"
                )
                note += (
                    " The official County Sheriff's Department page describes the office's "
                    "public-information app but publishes no property-sale or foreclosure "
                    "calendar/list. No county-specific sale feed, export/API, or "
                    "automated-access authorization was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Chambers County Probate Office recording and public records"
                directory_url = (
                    "https://www.chamberscountyal.gov/departments/"
                    "probate-office/recording-public-records"
                )
                note += (
                    " The official Recording & Public Records page lists forms, including a "
                    "real-estate sales validation form, but no public record search or "
                    "lis-pendens/default index. No pre-foreclosure feed, export/API, or "
                    "automated-access authorization was verified."
                )
        if state == "AL" and county_name == "Cherokee":
            if category == "tax_sale":
                directory_name = "Cherokee County Revenue Commission tax-lien auction FAQ"
                directory_url = (
                    "https://cherokeepropertytax.com/online-tax-lien-sale-faq/"
                )
                note += (
                    " The official County Commission Revenue page links to this county "
                    "Revenue Commission site. Its FAQ says the annual auction uses GovEase, "
                    "the available-property list is to be posted by March 1, and the list "
                    "includes owner, property description, delinquent years, and balances. "
                    "The posted 2026 auction date was April 30, 2026, now past; the sale "
                    "process page links a 2025 process PDF, and no 2027 date or current "
                    "auction list was found. The homepage's latest linked item is a "
                    "2025-2026 Insolvent Property Listing PDF, not verified as the auction "
                    "list. No machine-readable feed, export/API, or automated/commercial-use "
                    "authorization was verified. The Alabama DOR transcript is state-held "
                    "inventory, not the county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Cherokee County Sheriff's Office Auctions & Sales candidate"
                directory_url = (
                    "https://www.cherokeecountyalsheriff.com/auctions-and-sales"
                )
                note += (
                    " A Sheriff's-branded Auctions & Sales page was surfaced in search, "
                    "but direct HTTP/HTTPS requests failed at the transport level and the "
                    "County Commission pages checked do not link to it; its official "
                    "status and contents could not be verified. No accessible current "
                    "real-estate foreclosure/sheriff-sale list, machine-readable feed, or "
                    "automated/commercial-use authorization was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Cherokee County Probate Office public-records portal"
                directory_url = "https://cherokeecounty-al.gov/probate-office/"
                note += (
                    " The official Probate Office page links to the CountyGovServices "
                    "records portal. Its guest route presents Terms of Service requiring "
                    "acceptance; the terms say index searches are free and document views "
                    "cost $0.25 per page plus a payment fee. No terms were accepted or "
                    "search performed; no lis-pendens/default index, pre-foreclosure feed, "
                    "export/API, or automated-access authorization was verified."
                )
        if state == "AL" and county_name == "Chilton":
            if category == "tax_sale":
                directory_name = "Chilton County Revenue Commissioner tax-sale notices"
                directory_url = (
                    "https://www.chiltoncountyrevenue.com/home/news/main/"
                )
                note += (
                    " The official Revenue Commissioner website's site map has no "
                    "tax-sale page. Its Real Property page links to an online tax search "
                    "and payment service, not an auction list. The News page says to check "
                    "back for current items and links only to a 2024 archive; no current "
                    "sale date or parcel list was found. No machine-readable feed, "
                    "export/API, or automated/commercial-use authorization was verified. "
                    "The Alabama DOR transcript is state-held inventory, not the county "
                    "auction list."
                )
            elif category == "foreclosure":
                directory_name = "Chilton County Sheriff's Department"
                directory_url = "https://www.chiltoncountyso.org/"
                note += (
                    " The official County Commission site links to the Sheriff's "
                    "Department at this URL, but direct navigation redirected to HTTPS "
                    "and timed out. No accessible real-estate foreclosure or sheriff-sale "
                    "calendar/list, machine-readable feed, export/API, or automated/"
                    "commercial-use authorization was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Chilton County Probate Office public records"
                directory_url = "https://chiltoncounty.org/probate-office/"
                note += (
                    " The official Probate Office page says public probate, assessor, "
                    "and collector records are available in-office and lists real-estate "
                    "recording, judgments, and liens, but no online lis-pendens/default "
                    "index. The County Commission Public Records page requires requests "
                    "on its standard form in person with proof of Alabama residency; fees "
                    "may apply. The Commission's Terms of Service prohibit robots, "
                    "spiders, and automated monitoring/copying. No pre-foreclosure feed, "
                    "export/API, or automated-access authorization was verified."
                )
        if state == "AL" and county_name == "Choctaw":
            if category == "tax_sale":
                directory_name = "Choctaw County Revenue Commissioner"
                directory_url = (
                    "https://www.choctawcountyal.org/revenue-commissioner/"
                )
                note += (
                    " Search results identify this as the official County Revenue "
                    "Commissioner page, but direct browser and HTTP requests to the "
                    "county site failed at the transport level, so the page contents "
                    "and current sale information could not be verified. No current "
                    "county sale date, parcel list, machine-readable feed, export/API, "
                    "or automated/commercial-use authorization was verified. The "
                    "Alabama DOR Choctaw transcript is state-held inventory, not a "
                    "county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Choctaw County Sheriff's Office site (candidate)"
                directory_url = "http://www.choctawso.com/"
                note += (
                    " The HTTP homepage identifies itself as the Choctaw County "
                    "Sheriff's Office and offers general news, inmate, and wanted "
                    "information, but its accessible navigation has no sale or "
                    "foreclosure calendar/list. HTTPS requests failed, and a link "
                    "from the County Commission site could not be verified because "
                    "the county website was unavailable. No machine-readable feed, "
                    "export/API, or automated/commercial-use authorization was "
                    "verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Choctaw County Probate Judge"
                directory_url = "https://www.choctawcountyal.org/probate-judge/"
                note += (
                    " Direct requests to the official County Probate Judge page "
                    "failed at the transport level. A county-labelled ING Probate "
                    "portal at https://www.ingprobate.com/choctaw_probate/ surfaced "
                    "in search and offers Land Records and Probate Case Records, but "
                    "the official county page could not be loaded to confirm the "
                    "portal relationship. Its Terms and Conditions and automated-use "
                    "permissions were not verified. No lis-pendens/default index, "
                    "pre-foreclosure feed, or export/API was verified."
                )
        if state == "AL" and county_name == "Clarke":
            if category == "tax_sale":
                directory_name = "Clarke County Revenue Commissioner tax-lien auction"
                directory_url = (
                    "https://clarkecountyal.com/revenue-commissioner-clarke-co/"
                )
                note += (
                    " The official Revenue Commissioner page says the county "
                    "converted to the Tax Lien Auction process and links a Tax Lien "
                    "Legal Notice dated 2022-08-06. It also links an online tax "
                    "search/payment service, not a current auction list. The page "
                    "publishes no current auction date or parcel list. No "
                    "machine-readable feed, export/API, or automated/commercial-use "
                    "authorization was verified. The Alabama DOR transcript is "
                    "state-held inventory, not the county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Clarke County Sheriff's Department"
                directory_url = (
                    "https://clarkecountyal.com/sheriffs-department/"
                )
                note += (
                    " The official Sheriff's Department page describes county "
                    "duties, including serving subpoenas and warrants, but publishes "
                    "no real-estate foreclosure or sheriff-sale calendar/list. No "
                    "machine-readable feed, export/API, or automated/commercial-use "
                    "authorization was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Clarke County Probate Court public-records portal"
                directory_url = "https://clarkecountyal.com/probate/"
                note += (
                    " The official Probate Court page links a public-records search "
                    "portal and says an account is required; creating an account and "
                    "accessing documents are free. The page does not identify a "
                    "lis-pendens/default index, and portal terms or automated-use "
                    "authorization were not verified. No pre-foreclosure feed or "
                    "export/API was verified."
                )
        if state == "AL" and county_name == "Clay":
            if category == "tax_sale":
                directory_name = "Clay County Revenue Commissioner tax-sale information"
                directory_url = "https://www.claycountyrevenue.com/home/news/"
                note += (
                    " The official News page declares a Tax Lien Auction for "
                    "delinquent taxes beginning with tax years 2023-2024 and links "
                    "a 29-page Tax Lien Sale List. The linked list is for tax year "
                    "2024, with the sale scheduled for May 1, 2025; it is historical "
                    "and no newer 2025 tax-year list or current sale date was "
                    "verified as of 2026-10-19. The county's online tax search is "
                    "for assessment, records, and payment, not a current auction "
                    "feed. No machine-readable feed, export/API, or explicit "
                    "automated/commercial-use authorization was verified."
                )
            elif category == "foreclosure":
                directory_name = "Clay County Sheriff's Office"
                directory_url = "http://clayso.net/"
                note += (
                    " The Sheriff's Office site identifies the county office; the "
                    "accessible homepage reviewed contains detention/PREA "
                    "information, not a real-estate foreclosure or sheriff-sale "
                    "calendar/list. No structured feed, export/API, or "
                    "automated/commercial-use authorization was verified. HTTPS "
                    "could not be reached during this check."
                )
            elif category == "pre_foreclosure":
                directory_name = "Clay County Probate Office online services"
                directory_url = "https://www.ingprobate.com/clay_probate/"
                note += (
                    " The portal's legal disclaimer identifies the Clay County "
                    "Commission and Clay Judge of Probate, and expressly prohibits "
                    "automated systems, bots, spiders, scrapers, offline readers, "
                    "and automated interaction. No lis-pendens/default index or "
                    "pre-foreclosure feed was identified; do not automate this "
                    "portal without separate written authorization."
                )
        if state == "AL" and county_name == "Cleburne":
            if category == "tax_sale":
                directory_name = (
                    "Cleburne County Revenue Commissioner 2025 tax-year lien-sale list"
                )
                directory_url = (
                    "https://cleburnecountyal.com/wp-content/uploads/2026/04/"
                    "3advertisement-for-tax-saleTAXPAYERS_2.pdf"
                )
                note += (
                    " The official Revenue Commissioner PDF is a three-page "
                    "Tax Lien Auction Listing for the 2025 tax year. It states the "
                    "auction was scheduled for May 5, 2026, at 10:00 a.m., and "
                    "describes the Citizen Access portal, courthouse, and Revenue "
                    "Commissioner's office as listing locations. The sale date is "
                    "past as of 2026-10-19; no 2026 tax-year list or upcoming sale "
                    "date was verified. No recurring machine-readable feed, "
                    "export/API, or automated/commercial-use authorization was "
                    "verified. The Alabama DOR transcript is state-held inventory, "
                    "not the county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Cleburne County Sheriff's Office"
                directory_url = "https://cleburnecountyal.com/sheriffs-office/"
                note += (
                    " The official County Sheriff's Office page describes its "
                    "duties, including service of legal documents and eviction "
                    "notices, but publishes no real-estate foreclosure or "
                    "sheriff-sale calendar/list. No structured feed, export/API, "
                    "or automated/commercial-use authorization was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Cleburne County Probate Office online services"
                directory_url = "https://www.ingprobate.com/Cleburne_Probate/"
                note += (
                    " The portal advertises Land Records and Probate Case Records; "
                    "its legal disclaimer identifies the Cleburne County Commission "
                    "and Probate Judge and expressly prohibits automated systems, "
                    "bots, spiders, scrapers, offline readers, and automated "
                    "interaction. No lis-pendens/default index or pre-foreclosure "
                    "feed was identified. Do not automate this portal without "
                    "separate written authorization."
                )
        if state == "AL" and county_name == "Coffee":
            if category == "tax_sale":
                directory_name = "Coffee County Revenue Commissioner tax-sale information"
                directory_url = "https://www.coffeecountyrevenue.com/news.html"
                note += (
                    " The county Revenue Commissioner's News page states that "
                    "annual sales are held on the first or second Monday in April "
                    "in Enterprise and the first or second Tuesday in April in "
                    "Elba, at 10:00 a.m. It describes March newspaper advertising "
                    "and bidding registration but gives no year-specific date or "
                    "current parcel list. No machine-readable feed, export/API, or "
                    "explicit automated/commercial-use authorization was verified. "
                    "The Alabama DOR transcript is state-held inventory, not the "
                    "county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Coffee County Sheriff's Office"
                directory_url = "https://www.coffeeso.us/"
                note += (
                    " The official Sheriff's Office homepage identifies the "
                    "office, but no real-estate foreclosure or sheriff-sale "
                    "calendar/list was visible in the page reviewed. No structured "
                    "feed, export/API, or automated/commercial-use authorization "
                    "was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Coffee County Probate online records"
                directory_url = "https://www.ingprobate.com/Coffee_Probate/"
                note += (
                    " The portal's legal disclaimer identifies the Coffee County "
                    "Commission and Probate Judge and expressly prohibits automated "
                    "systems, bots, spiders, scrapers, offline readers, and "
                    "automated interaction. No lis-pendens/default index or "
                    "pre-foreclosure feed was identified. Do not automate this "
                    "portal without separate written authorization."
                )
        if state == "AL" and county_name == "Colbert":
            if category == "tax_sale":
                directory_name = "Colbert County Revenue Commissioner"
                directory_url = "https://revenuecommissioner.com/"
                note += (
                    " The official Colbert County departments directory links to "
                    "this Revenue Commissioner site. The fetched site response "
                    "identifies itself as the Colbert County official site but "
                    "exposed no current tax-sale date, parcel list, or feed. No "
                    "machine-readable feed, export/API, or explicit "
                    "automated/commercial-use authorization was verified. The "
                    "Alabama DOR transcript is state-held inventory, not the "
                    "county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Colbert County departments directory and Sheriff's Office"
                directory_url = "https://www.colbertcounty.org/departments.html"
                note += (
                    " The County's official Departments page links to the "
                    "Sheriff's Office at colbertsheriff.net, but direct HTTP and "
                    "HTTPS requests to that linked host failed at the "
                    "transport level. No real-estate foreclosure/sheriff-sale "
                    "calendar, list, or feed was verified. No automated or "
                    "commercial-use permission was established."
                )
            elif category == "pre_foreclosure":
                directory_name = "Colbert County Probate Judge public records"
                directory_url = (
                    "https://www.colbertprobatejudge.org/home/records/"
                )
                note += (
                    " The official Probate Judge records page says the record "
                    "room records and indexes deeds, mortgages, judgments, and "
                    "liens and offers public viewing stations in the courthouse; "
                    "no online lis-pendens/default index or pre-foreclosure feed "
                    "was identified. The related Colbert online-services portal "
                    "at altags.com identifies the County Commission and Probate "
                    "Judge in its legal disclaimer and expressly prohibits "
                    "automated systems, scraping, offline readers, and automated "
                    "interaction. Do not automate that portal without separate "
                    "written authorization."
                )
        if state == "AL" and county_name == "Conecuh":
            if category == "tax_sale":
                directory_name = "Conecuh County Revenue Commissioner online services"
                directory_url = (
                    "https://www.altags.com/Conecuh_Revenue/Default.aspx"
                )
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Conecuh online portal for appraisal and assessment; its "
                    "property-search page exposes tax-year and parcel search "
                    "fields, not a tax-sale list. The portal's legal disclaimer "
                    "identifies the Conecuh County Commission and Revenue "
                    "Commissioner and expressly prohibits automated systems, "
                    "scraping, offline readers, and automated interaction. No "
                    "current county auction date/list, sale feed, export/API, or "
                    "automated/commercial-use authorization was verified. The "
                    "Alabama DOR transcript is state-held inventory, not the "
                    "county auction list."
                )
            elif category == "foreclosure":
                directory_name = "Alabama Secretary of State Conecuh County Sheriff contact"
                directory_url = "https://www.sos.alabama.gov/node/1250"
                note += (
                    " The official Secretary of State contact page lists the "
                    "Conecuh County Sheriff's physical address but no online "
                    "foreclosure/sheriff-sale calendar or feed. No official "
                    "county sheriff sale source, export/API, or automated-use "
                    "authorization was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Conecuh County Probate online services"
                directory_url = (
                    "https://www.ingprobate.com/Conecuh_Probate/Default.aspx"
                )
                note += (
                    " The portal's legal disclaimer identifies the Conecuh "
                    "County Commission and Probate Judge and expressly prohibits "
                    "automated systems, bots, spiders, scrapers, offline readers, "
                    "and automated interaction. No lis-pendens/default index or "
                    "pre-foreclosure feed was identified. Do not automate this "
                    "portal without separate written authorization."
                )
        if state == "AL" and county_name == "Coosa":
            if category == "tax_sale":
                directory_name = "Coosa County Citizen Access property-tax portal"
                directory_url = "https://coosa.capturecama.com/"
                note += (
                    " The Alabama DOR county-office directory links this "
                    "Citizen Access portal for appraisal and assessment; the "
                    "portal returned only its landing-page title on retrieval, "
                    "and no tax-sale notice/list was verified. Search results "
                    "also surfaced a Coosa County Revenue Commissioner page at "
                    "https://www.coosacountyal.com/revenue-commissioner, but "
                    "direct HTTP and HTTPS retrievals failed, so its contents and "
                    "any current sale date remain unverified. No local "
                    "machine-readable sale feed, export/API, or explicit "
                    "automated/commercial-use authorization was verified. The "
                    "Alabama DOR transcript is state-held inventory, not the "
                    "county auction list."
                )
            elif category == "foreclosure":
                note += (
                    " No official Coosa County Sheriff's website or "
                    "real-estate foreclosure/sheriff-sale calendar/list was "
                    "verified. No county-specific feed, export/API, or "
                    "automated/commercial-use authorization was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Coosa County Probate online services"
                directory_url = (
                    "https://www.ingprobate.com/Coosa_Probate/Default.aspx"
                )
                note += (
                    " The portal's legal disclaimer identifies the Coosa County "
                    "Commission and Probate Judge and expressly prohibits "
                    "automated systems, bots, spiders, scrapers, offline readers, "
                    "and automated interaction. No lis-pendens/default index or "
                    "pre-foreclosure feed was identified. Do not automate this "
                    "portal without separate written authorization."
                )
        if state == "AL" and county_name == "Covington":
            if category == "tax_sale":
                directory_name = "Covington County Revenue Commissioner tax-lien auction"
                directory_url = (
                    "https://www.covingtoncountyal.gov/207/Revenue-Commissioner"
                )
                note += (
                    " The official Revenue Commissioner page declares the county "
                    "will conduct Tax Lien Auctions for delinquent taxes from tax "
                    "years 2023-2024 forward and links a delinquent-property list "
                    "through an AlertCenter notice. That linked notice returned "
                    "HTTP 404 on 2026-10-19, so no current sale list/date was "
                    "verified. The linked ALTAGS property-tax portal's legal "
                    "disclaimer identifies the County Commission and Revenue "
                    "Commissioner and expressly prohibits automated systems, "
                    "scraping, offline readers, and automated interaction. No "
                    "current machine-readable sale feed, export/API, or "
                    "automated/commercial-use authorization was verified. The "
                    "Alabama DOR transcript is state-held inventory, not the "
                    "county auction list."
                )
            elif category == "foreclosure":
                note += (
                    " No official county sheriff-sale or real-estate foreclosure "
                    "calendar/list, feed, export/API, or automated-use permission "
                    "was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Covington County Probate online services"
                directory_url = "https://www.ingprobate.com/Covington_Probate/"
                note += (
                    " The official County Recording page describes public "
                    "deeds, mortgages, and other recorded instruments and links "
                    "this probate portal. Its legal disclaimer identifies the "
                    "County Commission and Probate Judge and expressly prohibits "
                    "automated systems, bots, spiders, scrapers, offline readers, "
                    "and automated interaction. No lis-pendens/default index or "
                    "pre-foreclosure feed was identified; do not automate this "
                    "portal without separate written authorization."
                )
        if state == "AL" and county_name == "Crenshaw":
            if category == "assessor":
                directory_name = "Crenshaw County Revenue Commissioner property records"
                directory_url = (
                    "https://crenshawcountyalonline.com/#/RevenueCommissioner"
                )
                note += (
                    " The official county Revenue Commissioner page describes "
                    "property assessment and tax records and links the county's "
                    "Tax Search & Pay service and property maps. The tax-search "
                    "page warns its data may be slightly dated and presents an "
                    "interactive reCAPTCHA-gated search, not a documented "
                    "machine-readable feed. No export/API or explicit "
                    "automated/commercial-use permission was verified."
                )
            elif category == "tax_sale":
                directory_name = "Crenshaw County Revenue Commissioner tax-sale schedule"
                directory_url = (
                    "https://crenshawcountyalonline.com/"
                    "#/RevenueCommissioner/News"
                )
                note += (
                    " The official Revenue Commissioner News page says court "
                    "notices are mailed in March, delinquent-property ads run "
                    "for three consecutive weeks in April, and the tax sale is "
                    "in May with the date announced each year. No current "
                    "year-specific sale date/list or machine-readable feed, "
                    "export/API, or automated/commercial-use permission was "
                    "verified on 2026-10-19. The Alabama DOR transcript is "
                    "state-held inventory, not the county auction calendar."
                )
            elif category == "code_enforcement":
                directory_name = "Crenshaw County Commission building-code information"
                directory_url = "https://crenshawcountyalonline.com/#/CountyCommission"
                note += (
                    " The official County Commission page links a Building "
                    "Code Permit Letter, but no property-level violation, "
                    "abatement, or code-enforcement list/feed was identified. "
                    "Code enforcement may be municipal and must be confirmed "
                    "for the property's address. No machine-readable export or "
                    "automated-use permission was verified."
                )
            elif category == "foreclosure":
                note += (
                    " The official county Home, Notices, County Commission, and "
                    "Links pages checked did not expose a sheriff-sale or "
                    "foreclosure calendar/list. No county-specific official "
                    "sale feed, export/API, or automated-use permission was "
                    "verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Crenshaw County Probate records and Syscon PSEARCH"
                directory_url = "https://crenshawcountyalonline.com/#/"
                note += (
                    " The official county home page links online Probate "
                    "Records to http://www.syscononline.com/remote, which "
                    "redirects to Syscon PSEARCH. The PSEARCH information page "
                    "listed only Calhoun County under Alabama, not Crenshaw, "
                    "and says actual documents require registration and fees. "
                    "Syscon's terms prohibit data mining, robots or similar "
                    "extraction, and copying or retransmission without a "
                    "written license. No Crenshaw lis-pendens/default index "
                    "or authorized pre-foreclosure feed was identified; do not "
                    "automate without written authorization."
                )
        if state == "AL" and county_name == "Cullman":
            if category == "assessor":
                directory_name = "Cullman County Revenue Commissioner property search"
                directory_url = "https://cullmanrevenuecommissioner.com/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Revenue Commissioner's official website and a Cullman "
                    "parcel viewer. The county site links online property "
                    "search, maps/GIS, and a tax calculator; these are "
                    "interactive lookup tools, not a documented assessor "
                    "feed/export/API. No automated or commercial-use "
                    "permission was verified."
                )
            elif category == "tax_sale":
                directory_name = "Cullman County Revenue Commissioner delinquent parcels"
                directory_url = (
                    "https://cullmanproperty.countygovservices.com/"
                    "Property/DelinquentParcels"
                )
                note += (
                    " The Revenue Commissioner's official site links this "
                    "Tax Lien Parcels page. On 2026-10-19 it displayed "
                    "\"The Delinquent Parcels listing is currently disabled.\" "
                    "No current sale list/date, machine-readable feed, "
                    "export/API, or automated/commercial-use authorization "
                    "was verified. The Alabama DOR transcript is state-held "
                    "inventory, not a county auction calendar."
                )
            elif category == "code_enforcement":
                directory_name = "Cullman County Sales Tax/Revenue Enforcement Department"
                directory_url = "https://co.cullman.al.us/sales-tax.html"
                note += (
                    " The County's official page says its Solid Waste Officer "
                    "enforces county solid-waste laws, including illegal "
                    "dumping and littering. This is not a property-level "
                    "building-code or open-violations list/feed; municipal "
                    "code enforcement must be verified for each address. No "
                    "machine-readable export or automated-use permission "
                    "was verified."
                )
            elif category == "foreclosure":
                note += (
                    " The Cullman County Sheriff's official site did not "
                    "expose a real-estate sale/foreclosure calendar in its "
                    "navigation. Google search surfaced Cullman Times public "
                    "notices labeled Mortgage Foreclosure Sale, but direct "
                    "retrieval of its marketplace returned HTTP 403 and its "
                    "coverage/automation terms were not verified. Treat this "
                    "as discovery only; no county-specific authorized feed "
                    "was established."
                )
            elif category == "pre_foreclosure":
                directory_name = "Cullman County Probate online services"
                directory_url = "https://www.ingprobate.com/Cullman_Probate/"
                note += (
                    " The portal's legal disclaimer identifies the Cullman "
                    "County Commission and Probate Judge and expressly "
                    "prohibits automated systems, bots, spiders, scrapers, "
                    "offline readers, and automated interaction. No "
                    "lis-pendens/default index or pre-foreclosure feed was "
                    "identified; do not automate this portal without separate "
                    "written authorization."
                )
        if state == "AL" and county_name == "Dale":
            if category == "assessor":
                directory_name = "Dale County Revenue Commissioner property-tax information"
                directory_url = (
                    "https://www.dalecountyrevenue.com/"
                    "home/homenew/property-tax/"
                )
                note += (
                    " The Alabama DOR county-office directory links Dale's "
                    "Public GIS and a separate ALTAGS Business Personal Property "
                    "Return portal that requires a BPP location number and "
                    "access code; that is not an open real-estate assessment "
                    "feed. The official Revenue Commissioner property-tax page "
                    "links View & Pay to ALTAGS, whose legal disclaimer "
                    "expressly prohibits bots, scrapers, offline readers, and "
                    "automated interaction. No documented assessment "
                    "feed/export/API or automated-use permission was verified."
                )
            elif category == "tax_sale":
                directory_name = "Dale County Revenue Commissioner tax-lien auction"
                directory_url = (
                    "https://www.dalecountyrevenue.com/"
                    "home/homenew/property-tax/deliquent-property-taxes/"
                )
                note += (
                    " The official Revenue Commissioner page says the annual "
                    "online auction for 2025 ad valorem taxes was April 14, "
                    "2026; registration opened March 13 and First Right claims "
                    "ran March 13-April 9. The date is past. Its current-list "
                    "link, https://altags.com/dale_revenue/delinquent.aspx, "
                    "displayed \"DELINQUENT LIST UNAVAILABLE\" on 2026-10-19. "
                    "The ALTAGS legal disclaimer prohibits bots, scraping, "
                    "offline readers, and automated interaction. No 2027 "
                    "sale date/list, machine-readable feed, export/API, or "
                    "automated/commercial-use authorization was verified. The "
                    "Alabama DOR transcript is state-held inventory, not the "
                    "county auction calendar."
                )
            elif category == "code_enforcement":
                note += (
                    " No Dale County property-level code-enforcement or "
                    "open-violation list/feed was identified. Building and "
                    "code enforcement may be municipal; the responsible "
                    "provider must be confirmed for each property address."
                )
            elif category == "foreclosure":
                note += (
                    " A Google-indexed result identifies http://daleso.com "
                    "as the Dale County Sheriff's Office, but direct HTTP "
                    "retrieval returned no usable content and the browser "
                    "request timed out. No official county sheriff-sale or "
                    "foreclosure calendar/list, feed, or automated-use "
                    "authorization was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Dale County Probate online services"
                directory_url = "https://www.ingprobate.com/Dale_Probate/"
                note += (
                    " The portal's legal disclaimer identifies the Dale "
                    "County Probate Judge and expressly prohibits automated "
                    "systems, bots, spiders, scrapers, offline readers, and "
                    "automated interaction. No lis-pendens/default index or "
                    "pre-foreclosure feed was identified; do not automate "
                    "this portal without separate written authorization."
                )
        if state == "AL" and county_name == "Dallas":
            if category == "assessor":
                directory_name = "Dallas County Tax Assessor and parcel viewer"
                directory_url = (
                    "https://www.dallascounty-al.org/County-Departments/"
                    "Tax-Assessor/Assessor-Department"
                )
                source_url = (
                    "https://dallascountyal.maps.arcgis.com/apps/"
                    "webappviewer/index.html?id="
                    "747eebce86fe460a88a0dbb29f828560"
                )
                note += (
                    " The Alabama DOR county-office directory identifies the "
                    "Dallas County Tax Assessor and links the county's Parcel "
                    "Viewer and Citizen Access Portal. The official Assessor "
                    "Department page provides property-tax guidance; the "
                    "public ArcGIS map and Citizen Access portal are "
                    "interactive lookup tools, not a documented assessment "
                    "feed/export/API. No automated or commercial-use "
                    "authorization was verified."
                )
            elif category == "tax_sale":
                directory_name = "Dallas County Tax Collector collection portal"
                directory_url = "https://dallas.capturecama.com/collection"
                note += (
                    " The official County directory lists the Tax Collector "
                    "at 334-874-2519. The County advertised a tax-lien "
                    "presentation for April 15, 2026, now past; it is not an "
                    "auction date. The direct collection route rendered only "
                    "the generic Citizen Access Portal shell, with no current "
                    "sale list or date. The Alabama DOR transcript is "
                    "state-held delinquent inventory, not the county auction "
                    "calendar. No current sale date/list, documented "
                    "feed/export/API, or automated/commercial-use "
                    "authorization was verified."
                )
            elif category == "code_enforcement":
                directory_name = "Dallas County offices and code-enforcement contacts"
                directory_url = (
                    "https://www.dallascounty-al.org/Find-It-Here/"
                    "County-and-State-Offices"
                )
                note += (
                    " The official County office directory lists county "
                    "contacts but no property-level code-enforcement or "
                    "open-violation list/feed. Code enforcement may be "
                    "municipal and must be confirmed for each property "
                    "address. No countywide export/API or automated-use "
                    "permission was verified."
                )
            elif category == "foreclosure":
                directory_name = "Dallas County public notices and Sheriff contacts"
                directory_url = "https://www.dallascounty-al.org/Public-notices"
                note += (
                    " The official County and State Offices directory lists "
                    "the Sheriff's Department at 334-874-2530, but no sale "
                    "calendar; the County Public Notices page exposed no "
                    "current real-estate sale list in direct retrieval. The "
                    "statewide Alabama Public Notice search relies on "
                    "participating newspapers, so county coverage is not "
                    "complete; its Terms prohibit scraping and automated "
                    "commercial collection. No Dallas-specific authorized "
                    "foreclosure/sheriff-sale feed, export/API, or "
                    "automated-use permission was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Dallas County Probate recording records"
                directory_url = "https://www.ingprobate.com/Dallas_Probate/"
                note += (
                    " The official County Probate Services page says the "
                    "Recording Office handles real-estate records, deeds, "
                    "and liens. The Dallas Probate portal's legal disclaimer "
                    "identifies the Dallas County Commission and Probate "
                    "Judge and expressly prohibits bots, scrapers, offline "
                    "readers, and automated interaction. No lis-pendens/"
                    "default index or pre-foreclosure feed was identified; "
                    "do not automate this portal without separate written "
                    "authorization."
                )
        if state == "AL" and county_name == "DeKalb":
            if category == "assessor":
                directory_name = "DeKalb County Revenue Commissioner appraisal records"
                directory_url = "https://revenue-dekalbco-al.us/appraisal/"
                source_url = "https://isv.kcsgis.com/al.dekalb_revenue/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "official Revenue Commissioner site and this ISV3 Online "
                    "Record Search for appraisal and assessment records. The "
                    "Revenue Commission's Taxes page also links an AssuranceWeb "
                    "property-tax search by owner, PIN, parcel, account, or "
                    "address and warns not to use the results for future-year "
                    "tax calculations. These are interactive lookup portals, "
                    "not documented assessment feeds/export/APIs; no "
                    "automated or commercial-use authorization was verified."
                )
            elif category == "tax_sale":
                directory_name = "DeKalb County Revenue Commissioner tax-lien sale"
                directory_url = "https://revenue-dekalbco-al.us/taxes/"
                note += (
                    " The official Revenue Commission Taxes page says DeKalb "
                    "changed to tax-lien auctions in 2019 for delinquent 2018 "
                    "taxes and that unpaid property is auctioned in April or "
                    "May with a three-year right of redemption. It publishes "
                    "no current year-specific sale date or auction list; its "
                    "AssuranceWeb tax-record search is not a sale list. The "
                    "Alabama DOR transcript is state-held delinquent inventory, "
                    "not the county auction calendar. No documented "
                    "machine-readable sale feed/export/API or "
                    "automated/commercial-use authorization was verified."
                )
            elif category == "code_enforcement":
                directory_name = "DeKalb County Commission and municipal offices"
                directory_url = "https://dekalbcountyal.us/"
                note += (
                    " The official County site pages checked expose no "
                    "countywide property-level code-enforcement or "
                    "open-violation list/feed. Code enforcement may be "
                    "municipal and must be confirmed for each property "
                    "address. No countywide export/API or automated-use "
                    "permission was verified."
                )
            elif category == "foreclosure":
                directory_name = "DeKalb County Sheriff's Office"
                directory_url = "https://www.dekalbcountysheriff.org/"
                note += (
                    " The official Sheriff's site has general calendar and "
                    "service navigation but no identified real-estate "
                    "foreclosure/sheriff-sale calendar or list. The statewide "
                    "Alabama Public Notice search relies on participating "
                    "newspapers, so county coverage is not complete; its "
                    "Terms prohibit scraping and automated commercial "
                    "collection. No county-specific authorized sale feed, "
                    "export/API, or automated-use permission was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "DeKalb County Probate Records portal"
                directory_url = (
                    "https://services.revenue-dekalbco-al.us/ProbateRecords"
                )
                note += (
                    " The official Probate Judge website's Links page lists "
                    "this Probate Records portal. Direct retrieval returned "
                    "only the generic page title; no public lis-pendens/default "
                    "index or pre-foreclosure feed, documented export/API, or "
                    "automated-access authorization was verified."
                )
        if state == "AL" and county_name == "Elmore":
            if category == "assessor":
                directory_name = "Elmore County appraisal and assessment records"
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Elmore"
                )
                source_url = "https://elmorerevenuecommissioner.net/"
                note += (
                    " The Alabama DOR county-office directory identifies "
                    "the Elmore County Revenue Commissioner and links its "
                    "Citizen Access Portal for appraisal and assessment "
                    "records. The portal home and DelqSearch route returned "
                    "only the generic Citizen Access Portal shell in direct "
                    "retrieval; they are not documented feed/export/APIs. "
                    "No automated or commercial-use authorization was "
                    "verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Elmore County Revenue Commissioner delinquent-property search"
                )
                directory_url = "https://elmorerevenuecommissioner.net/DelqSearch"
                note += (
                    " The official Elmore Citizen Access Portal's "
                    "DelqSearch route rendered only the generic portal shell; "
                    "no current county auction date, sale list, documented "
                    "feed/export/API, or automated/commercial-use "
                    "authorization was verified. The linked Alabama DOR "
                    "Elmore transcript is weekly state-held delinquent "
                    "inventory, not a local auction calendar, and the DOR "
                    "says its transcripts lack physical addresses."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Elmore County planning and municipal code-enforcement contacts"
                )
                directory_url = "https://www.elmoreco.org/service-directory"
                source_url = directory_url
                note += (
                    " The official County Directory & FAQs page says rural "
                    "Elmore County has no zoning restrictions or building "
                    "permit requirements; properties in a municipal "
                    "planning jurisdiction should be checked with that "
                    "city's planning department. No countywide property-level "
                    "code-enforcement/open-violation feed or documented "
                    "export/API was identified. Verify the provider for each "
                    "property's municipality; no automated-use permission "
                    "was verified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Elmore County Sheriff's Office and foreclosure-sale sources"
                )
                directory_url = "https://www.elmoreso.com/departments-services"
                note += (
                    " The official Sheriff's site describes law-enforcement "
                    "responsibility for unincorporated areas and general "
                    "services; its Departments & Services page and site "
                    "search exposed no real-estate foreclosure/sheriff-sale "
                    "calendar, list, or feed. The statewide Alabama Public "
                    "Notice search depends on participating newspapers, so "
                    "coverage is incomplete/unverified; its Terms prohibit "
                    "scraping, spidering, automated collection, and "
                    "commercial exploitation. No county-specific authorized "
                    "foreclosure feed or automation permission was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Elmore County Probate recording and property-activity alerts"
                )
                directory_url = (
                    "https://www.elmoreco.org/elmore-county-recording"
                )
                source_url = "https://www.ingprobate.com/Elmore_Probate/"
                note += (
                    " The official Probate Recording page says it indexes "
                    "and preserves permanent public documents, including "
                    "real-estate records, and links this Public Records "
                    "Search. The County's 2026 REAACT notice describes free "
                    "near-real-time email alerts for recorded deeds, "
                    "mortgages, or other designated land records matching a "
                    "registered name; this is not an address-specific "
                    "foreclosure/default feed. The portal's legal disclaimer "
                    "expressly prohibits automated systems, bots, spiders, "
                    "scrapers, offline readers, and automated interaction. "
                    "No lis-pendens/default index, authorized bulk feed, or "
                    "automated-use permission was verified."
                )
        if state == "AL" and county_name == "Escambia":
            if category == "assessor":
                directory_name = (
                    "Escambia County Tax Assessor property assessment records"
                )
                directory_url = (
                    "https://www.escambiacountyal.gov/government/"
                    "tax_assessor/index.php"
                )
                source_url = "https://www.alabamagis.com/escambia/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "official County Tax Assessor page and Public GIS site. "
                    "The Assessor page says the office maintains county "
                    "property records and a CAMA sales inventory, and "
                    "provides valuation and tax-calculation information. "
                    "Direct retrieval of the GIS route returned only its "
                    "welcome page; no documented assessment feed/export/API, "
                    "publication cadence, or automated/commercial-use "
                    "authorization was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Escambia County Tax Collector delinquent taxes and "
                    "tax-lien sales"
                )
                directory_url = (
                    "https://www.escambiacountyal.gov/government/"
                    "tax_collector/delinquent_taxes.php"
                )
                note += (
                    " The official Tax Collector page declares tax-lien "
                    "auctions for delinquent tax years 2020-2021 forward and "
                    "says the TAX LIEN SALE LIST is available only April-May; "
                    "it was not available on the 2026-10-19 check. The linked "
                    "Tax Lien Report says it is not updated daily and its "
                    "total due is not the actual lien-purchase amount; its "
                    "PDF route returned HTTP 404. The County Assessor page "
                    "says unpaid property is auctioned in May with a "
                    "three-year redemption, but no 2027 sale date or current "
                    "county auction list was verified. The DOR Escambia "
                    "transcript is dated "
                    "2026-10-19 and contains state-held delinquent inventory "
                    "with parcel/legal descriptions rather than situs street "
                    "addresses; it is not the county auction calendar. No "
                    "documented machine-readable feed or automated/"
                    "commercial-use authorization was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Escambia County government and municipal "
                    "code-enforcement contacts"
                )
                directory_url = "https://www.escambiacountyal.gov/"
                source_url = directory_url
                note += (
                    " The County pages and department listings checked "
                    "expose no countywide property-level code-enforcement "
                    "or open-violation list/feed. The responsible provider "
                    "must be confirmed for each property's municipality or "
                    "unincorporated jurisdiction. No countywide export/API "
                    "or automated-use permission was verified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Escambia County Sheriff's Office and foreclosure-sale sources"
                )
                directory_url = "https://www.escambiacountysheriffal.org/"
                note += (
                    " The official County site links this Sheriff's Office; "
                    "the Sheriff's site and a site-restricted search exposed "
                    "no real-estate foreclosure/sheriff-sale calendar, list, "
                    "or feed. The statewide Alabama Public Notice search "
                    "depends on participating newspapers, so coverage is "
                    "incomplete/unverified; its Terms prohibit scraping, "
                    "spidering, automated collection, and commercial "
                    "exploitation. No county-specific authorized foreclosure "
                    "feed or automation permission was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Escambia County Probate Judge and online public records"
                )
                directory_url = (
                    "https://www.escambiacountyal.gov/courts___legal/"
                    "judge_of_probate/index.php"
                )
                source_url = (
                    "https://ingprobate.com/Escambia_Probate/"
                    "ProbateDefault.aspx"
                )
                note += (
                    " The official Probate Judge page links the online "
                    "Probate Records portal. Its legal disclaimer expressly "
                    "prohibits automated systems, bots, spiders, scrapers, "
                    "offline readers, and automated interaction. No public "
                    "lis-pendens/default index, pre-foreclosure feed, "
                    "documented export/API, or permitted automated access "
                    "was identified."
                )
        if state == "AL" and county_name == "Etowah":
            if category == "assessor":
                directory_name = (
                    "Etowah County Revenue Commissioner appraisal and "
                    "assessment records"
                )
                directory_url = "https://etowahcounty.org/revenue-commissioner/"
                source_url = "https://etowahcounty.org/department/appraisal/"
                note += (
                    " The official Revenue Commissioner page lists Appraisal, "
                    "Assessing & Collections, and Mapping departments. The "
                    "Appraisal page says deeds, sales, appraisals, and "
                    "building/septic permits are collected daily for its "
                    "valuation process; this is not a public daily feed. The "
                    "Assessing page exposed 2026 value notices and a 2024 "
                    "personal delinquent-tax CSV, not a bulk real-property "
                    "assessment feed. No documented property-record "
                    "export/API, publication cadence, or automated/"
                    "commercial-use authorization was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Etowah County Assessing & Collections tax-lien auction"
                )
                directory_url = "https://etowahcounty.org/department/assessing/"
                note += (
                    " The County page states the 2026 tax-lien auction was "
                    "May 4, 2026 at 9:00 a.m. via GovEase; this date is past "
                    "as of the 2026-10-19 check, and no 2027 date is posted. "
                    "Its linked Delinquent Parcel Search returned only a "
                    "generic AssuranceGov shell, not a current list. A "
                    "separate older About Collections page still shows "
                    "2024 auction information. The DOR Etowah transcript is "
                    "weekly state-held delinquent inventory, not the county "
                    "auction calendar, and DOR says transcripts lack "
                    "physical addresses. No current county sale list, "
                    "documented feed/export/API, or automated/commercial-use "
                    "authorization was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Etowah County code-enforcement and municipal contacts"
                )
                directory_url = "https://etowahcounty.org/"
                source_url = directory_url
                note += (
                    " The County website searches for code enforcement and "
                    "building code and the department pages reviewed exposed "
                    "no countywide property-level code-enforcement or "
                    "open-violation list/feed. Verify the responsible "
                    "provider by each property's municipality; no documented "
                    "county export/API, publication cadence, or "
                    "automated-use permission was identified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Etowah County Sheriff's Office Civil Service Division"
                )
                directory_url = (
                    "https://www.etowahcountysheriff.com/upages.php?id=41"
                )
                note += (
                    " An indexed official Sheriff's Office result identifies "
                    "the Civil Service Division as conducting Sheriff's "
                    "sales, but direct retrieval of that page timed out on "
                    "the 2026-10-19 check; no current sale list, calendar, "
                    "feed, or export/API was verified. The statewide Alabama "
                    "Public Notice search depends on participating "
                    "newspapers and its Terms prohibit scraping, automated "
                    "collection, and commercial exploitation. No authorized "
                    "county foreclosure feed or automated-use permission "
                    "was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Etowah County Probate Judge deed and real-estate records"
                )
                directory_url = "https://etowahcounty.org/deeds-and-records/"
                source_url = "https://etowahprobate.assurancegov.com/"
                note += (
                    " The official Deeds and Records page lists lis pendens "
                    "among recordable instruments but warns that online data "
                    "may contain omissions and is not official; it links an "
                    "AssuranceGov records portal that redirects to sign-in. "
                    "No public lis-pendens/default index, pre-foreclosure "
                    "feed, bulk export/API, or authorized automated access "
                    "was verified."
                )
        if state == "AL" and county_name == "Fayette":
            if category == "assessor":
                directory_name = (
                    "Fayette County Revenue Commissioner and public GIS"
                )
                directory_url = (
                    "https://www.fayetteco.net/home/departments/"
                    "revenue-commissioner/"
                )
                source_url = "https://www.alabamagis.com/Fayette/"
                note += (
                    " The official County Revenue Commissioner page "
                    "describes property-tax administration and links the "
                    "public GIS; the Alabama DOR county-office directory "
                    "also lists this GIS. Direct retrieval redirected to "
                    "the Fayette County GIS welcome page, not a documented "
                    "parcel feed/API. No assessment export, publication "
                    "cadence, or automated/commercial-use authorization was "
                    "verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Fayette County Revenue Commissioner tax-sale information"
                )
                directory_url = (
                    "https://www.fayetteco.net/home/departments/"
                    "revenue-commissioner/"
                )
                note += (
                    " The official County Revenue Commissioner page "
                    "provides tax-office contacts and a public GIS link but "
                    "no current tax-sale date or sale list; a site-restricted "
                    "search also exposed no county tax-sale calendar or "
                    "feed. The DOR Fayette transcript is weekly state-held "
                    "delinquent inventory, not the local auction calendar, "
                    "and DOR says transcripts lack physical addresses. A "
                    "similarly named Fayette County Tax Sales site resolved "
                    "to Fayette County, Georgia and was excluded. No current "
                    "Alabama county list/date, documented feed/export/API, "
                    "or automated-use permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Fayette County and municipal building/code contacts"
                )
                directory_url = (
                    "https://www.fayetteco.net/home/government/"
                    "local-government/"
                )
                source_url = "https://www.fayetteco.net/home/about/faqs/"
                note += (
                    " The County FAQ states there are no building or "
                    "permitting requirements in Fayette County, while cities "
                    "and towns may have their own requirements. The County "
                    "lists Berry, Belk, Glen Allen, and Fayette as local "
                    "governments; verify the provider by property "
                    "municipality. No countywide property-level "
                    "code-enforcement/open-violation feed or documented "
                    "municipal export/API or automated-use permission was "
                    "verified."
                )
            elif category == "foreclosure":
                directory_name = "Fayette County Sheriff's Office (Alabama)"
                directory_url = "https://www.fayetteso.com/"
                note += (
                    " The official Sheriff's Office home and navigation "
                    "expose general office, inmate, contact, and community "
                    "information, but no real-estate foreclosure/sheriff-sale "
                    "calendar, list, or feed. The statewide Alabama Public "
                    "Notice search depends on participating newspapers and "
                    "its Terms prohibit scraping, automated collection, and "
                    "commercial exploitation. No county-specific authorized "
                    "foreclosure feed or automated-use permission was "
                    "verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Fayette County Probate Office online record search"
                )
                directory_url = (
                    "https://www.fayetteco.net/home/departments/"
                    "probate-office/online-record-search/"
                )
                source_url = "https://www.ingprobate.com/fayette_probate/"
                note += (
                    " The official Probate Office page links the online "
                    "record search for land and probate records. The portal's "
                    "terms expressly prohibit automated systems, bots, "
                    "spiders, scrapers, offline readers, and automated "
                    "interactions. No public lis-pendens/default index, "
                    "authorized pre-foreclosure feed, bulk export/API, or "
                    "permitted automated access was verified."
                )
        if state == "AL" and county_name == "Franklin":
            if category == "assessor":
                directory_name = "Franklin County Revenue Commissioner"
                directory_url = "https://franklincountyrevenue.com/"
                source_url = (
                    "https://franklinproperty.countygovservices.com/"
                    "Property/Search"
                )
                note += (
                    " The County website links the Revenue Commissioner's "
                    "official site, which links Property Search & Pay and "
                    "County Maps; the Alabama DOR county-office directory "
                    "also lists the Franklin County GIS. Direct retrieval of "
                    "the property-search and GIS routes returned only their "
                    "generic portal shells/titles. No documented assessment "
                    "export/API, update cadence, or automated/commercial-use "
                    "authorization was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Franklin County Revenue Commissioner tax-sale lien"
                )
                directory_url = "https://franklincountyrevenue.com/"
                note += (
                    " The official Revenue Commissioner home page has a Tax "
                    "Sale Lien section whose View News link goes to the "
                    "general GovEase homepage, not a Franklin County event "
                    "or sale list. No current auction date/list, county "
                    "calendar, documented feed/export/API, or automation "
                    "permission was verified. The DOR Franklin transcript is "
                    "weekly state-held delinquent inventory, not the local "
                    "auction calendar, and DOR says transcripts lack "
                    "physical addresses."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Franklin County government departments and municipal contacts"
                )
                directory_url = "https://franklincountyal.org/departments/"
                source_url = directory_url
                note += (
                    " The official County Departments page lists County "
                    "offices but no building-code or code-enforcement "
                    "department. No countywide property-level "
                    "code-enforcement/open-violation list/feed, documented "
                    "export/API, publication cadence, or automated-use "
                    "permission was identified. Verify the local provider "
                    "for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = "Franklin County Sheriff's Office"
                directory_url = "https://www.franklinsheriff.org/"
                note += (
                    " The official County Departments page links the "
                    "Sheriff's Office site, but direct requests timed out on "
                    "the 2026-10-19 check and a site-restricted search "
                    "exposed no foreclosure/sheriff-sale list or calendar. "
                    "The statewide Alabama Public Notice search depends on "
                    "participating newspapers and its Terms prohibit "
                    "scraping, automated collection, and commercial "
                    "exploitation. No county-specific authorized foreclosure "
                    "feed or automated-use permission was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Franklin County Probate Judge land records"
                directory_url = "https://franklincountyal.org/departments/"
                source_url = "https://www.ingprobate.com/Franklin_Probate/"
                note += (
                    " The official County Departments page links this "
                    "Probate Records portal. Its landing page offers Land "
                    "Records, Probate Case Records, Record Account Login, "
                    "and an R.E.A.A.C.T. option, but the public lis-pendens/"
                    "default search scope and any bulk delivery are "
                    "unverified. The portal's legal disclaimer expressly "
                    "prohibits automated systems, bots, spiders, scrapers, "
                    "offline readers, and automated interactions. No "
                    "authorized pre-foreclosure feed, bulk export/API, or "
                    "permitted automated access was verified."
                )
        if state == "AL" and county_name == "Geneva":
            if category == "assessor":
                directory_name = (
                    "Geneva County Revenue Commissioner and public GIS"
                )
                directory_url = "https://genevacountyal.gov/revenue/"
                source_url = "https://www.alabamagis.com/Geneva/"
                note += (
                    " The official County Revenue page and Alabama DOR "
                    "county-office directory link the Geneva public GIS. "
                    "The GIS root redirected to a generic welcome page, and "
                    "the County-linked Frameset route returned HTTP 503 on "
                    "the 2026-10-19 check. No documented assessment "
                    "export/API, publication cadence, or automated/"
                    "commercial-use authorization was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Geneva County Revenue Commissioner tax-sale information"
                )
                directory_url = (
                    "https://genevacountyal.gov/revenue-tax-sale-info/"
                )
                note += (
                    " The official County Tax Sale Information page says "
                    "properties will be posted there when available, but "
                    "the page contains only an announcement that the 2018 "
                    "sale was postponed to May 7, 2019 and has a 2019 "
                    "copyright. No current county sale list/date, feed/API, "
                    "or automated-use permission was verified. The DOR "
                    "Geneva transcript is weekly state-held delinquent "
                    "inventory, not the local auction calendar, and DOR "
                    "says transcripts lack physical addresses."
                )
            elif category == "code_enforcement":
                directory_name = "City of Geneva Building Department"
                directory_url = (
                    "https://www.genevaal.gov/building-department"
                )
                source_url = directory_url
                note += (
                    " This is the City of Geneva, not a countywide "
                    "department. The City's page describes construction "
                    "permit/inspection work and floodplain-management "
                    "enforcement, but publishes no property-level "
                    "violation list or daily feed. No countywide "
                    "code-enforcement feed, documented export/API, or "
                    "automated-use permission was verified; confirm each "
                    "property's municipality and provider."
                )
            elif category == "foreclosure":
                directory_name = "Geneva County Sheriff's Office"
                directory_url = "https://genevacountyal.gov/sheriff/"
                note += (
                    " The official County Sheriff's page is a title-only "
                    "landing page and exposes no foreclosure/sheriff-sale "
                    "list or calendar. The statewide Alabama Public Notice "
                    "search depends on participating newspapers and its "
                    "Terms prohibit scraping, automated collection, and "
                    "commercial exploitation. Search results also surfaced "
                    "commercial foreclosure listings, but no official "
                    "docket/notice verification, complete daily interface, "
                    "or automation permission was established; treat them "
                    "as unverified manual leads only."
                )
            elif category == "pre_foreclosure":
                directory_name = "Geneva County Probate Office online records"
                directory_url = "https://genevacountyal.gov/probate/"
                source_url = "https://www.ingprobate.com/Geneva_Probate/"
                note += (
                    " The official County Probate page links this online "
                    "records portal. Its legal disclaimer expressly "
                    "prohibits automated systems, bots, spiders, scrapers, "
                    "offline readers, and automated interactions. No "
                    "public lis-pendens/default index, authorized "
                    "pre-foreclosure feed, bulk export/API, or permitted "
                    "automated access was verified. Commercial "
                    "pre-foreclosure listings surfaced in search but were "
                    "not verified against official records and are not "
                    "configured as feeds."
                )
        if state == "AL" and county_name == "Greene":
            if category == "assessor":
                directory_name = (
                    "Greene County Revenue Commissioner and parcel viewer"
                )
                source_url = (
                    "https://experience.arcgis.com/experience/"
                    "c4dc2ec2622a42f88610d370f32ea0f8/"
                )
                note += (
                    " The DOR county-office directory links Greene County's "
                    "public GIS. Its former County-owned ArcGIS app states "
                    "that it is inactive as of October 2026 and directs users "
                    "to this new Parcel Viewer; ArcGIS metadata identifies "
                    "the new public app owner as GreeneCountyAL. No "
                    "documented assessment export/API, update cadence, or "
                    "permission for daily/commercial ingestion was verified."
                )
            elif category == "tax_sale":
                directory_name = "Greene County Commission tax information"
                directory_url = (
                    "https://greenecountycommission.com/taxinformation/"
                )
                note += (
                    " The official County Commission tax-information page "
                    "says only 'Information coming soon!' and its sitemap "
                    "shows a 2021 last-modified date. No current County "
                    "auction date/list, bidder instructions, county-specific "
                    "feed/export/API, or automated-use permission was "
                    "verified. The DOR Greene transcript is weekly "
                    "state-held delinquent inventory, not the local auction "
                    "calendar, and DOR says transcripts lack physical "
                    "addresses. Generic search results for Greene County "
                    "also included out-of-state jurisdictions and were "
                    "excluded."
                )
            elif category == "code_enforcement":
                directory_name = "Greene County Commission contact directory"
                directory_url = "https://greenecountycommission.com/directory/"
                source_url = directory_url
                note += (
                    " The County Commission contact directory is a manual "
                    "discovery link only. No current County or municipal "
                    "property-level code-enforcement provider, open-violation "
                    "list/feed, documented export/API, or automated-use "
                    "permission was verified. Confirm the responsible "
                    "jurisdiction and provider by property municipality."
                )
            elif category == "foreclosure":
                directory_name = "Greene County Sheriff's Office"
                directory_url = "https://www.gcsoal.org/"
                note += (
                    " The official Sheriff's website returned a React app "
                    "shell; a site-restricted search exposed no indexed "
                    "foreclosure/sheriff-sale list or calendar. The "
                    "statewide Alabama Public Notice search depends on "
                    "participating newspapers and its Terms prohibit "
                    "scraping, automated collection, and commercial "
                    "exploitation. No county-specific authorized "
                    "foreclosure feed or automated-use permission was "
                    "verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Greene County Probate online records"
                directory_url = "https://www.ingprobate.com/Greene_Probate/"
                source_url = directory_url
                note += (
                    " The Greene County online Probate Records portal's "
                    "legal disclaimer expressly prohibits automated "
                    "systems, bots, spiders, scrapers, offline readers, "
                    "data extraction, and automated interactions. No "
                    "public lis-pendens/default index, authorized "
                    "pre-foreclosure feed, bulk export/API, or permitted "
                    "automated access was verified."
                )
        if state == "AL" and county_name == "Hale":
            if category == "assessor":
                directory_name = "Hale County Tax Assessor and public GIS"
                source_url = (
                    "https://hcal.maps.arcgis.com/apps/webappviewer/"
                    "index.html?id=096bf46a286340ffa7f5e5b78fb2800c"
                )
                note += (
                    " The Alabama DOR directory links this public GIS and "
                    "an IngProperty Citizen Access route. The GIS loads an "
                    "ArcGIS Web App whose public item metadata names "
                    "HaleCounty as owner. The linked IngProperty route "
                    "presents a Business Personal Property return login "
                    "requiring a BPPIN/access code, not a public residential "
                    "parcel search; that portal's legal disclaimer prohibits "
                    "automated access and extraction. No documented "
                    "real-property export/API, update cadence, or permission "
                    "for daily/commercial GIS ingestion was verified."
                )
            elif category == "tax_sale":
                directory_name = "Hale County tax-lien sale notice"
                directory_url = (
                    "https://www.halecountyal.gov/"
                    "notice-sale-tax-liens-collecting-delinquent-property-tax"
                )
                note += (
                    " Google indexed this official County page as a notice "
                    "for a delinquent-property Tax Lien Auction and Sale "
                    "under Alabama Code 40-10-180(b), but requests to the "
                    "County host timed out on the 2026-10-19 check. No "
                    "current sale date/list, bidder instructions, feed/API, "
                    "or automated-use permission could be verified. The "
                    "DOR Hale transcript is weekly state-held delinquent "
                    "inventory, not the local auction calendar, and DOR "
                    "says transcripts lack physical addresses."
                )
            elif category == "code_enforcement":
                directory_name = "Hale County and municipal code contacts"
                directory_url = "https://www.halecountyal.gov/"
                source_url = directory_url
                note += (
                    " The official County host timed out during this check. "
                    "No County or municipal property-level "
                    "code-enforcement provider, open-violation list/feed, "
                    "documented export/API, or automated-use permission "
                    "could be verified. Confirm the responsible jurisdiction "
                    "and provider by property municipality."
                )
            elif category == "foreclosure":
                directory_name = "Hale County Sheriff's Office"
                directory_url = "https://www.halecoso.com/"
                note += (
                    " The Alabama Sheriffs Association directory lists this "
                    "as Hale County Sheriff's Office's website, but direct "
                    "requests failed at the DNS/TLS transport layer and a "
                    "site-restricted search exposed no indexed sale list or "
                    "calendar. The statewide Alabama Public Notice search "
                    "depends on participating newspapers and its Terms "
                    "prohibit scraping, automated collection, and commercial "
                    "exploitation. No county-specific authorized "
                    "foreclosure feed or automated-use permission was "
                    "verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Hale County Probate Judge online records"
                directory_url = (
                    "https://www.halecountyal.gov/probate-judge"
                )
                source_url = "https://www.altags.com/Hale_Probate/"
                note += (
                    " The County Probate Judge page is listed on the "
                    "official County site, whose host timed out during this "
                    "check. The linked Hale Probate online-records portal's "
                    "legal disclaimer expressly prohibits automated "
                    "systems, bots, spiders, scrapers, offline readers, "
                    "data extraction, and automated interactions. No public "
                    "lis-pendens/default index, authorized pre-foreclosure "
                    "feed, bulk export/API, or permitted automated access "
                    "was verified."
                )
        if state == "AL" and county_name == "Henry":
            if category == "assessor":
                directory_name = (
                    "Henry County Revenue Commissioner and public GIS"
                )
                source_url = "https://henry.capturecama.com/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Henry County public GIS and CaptureCAMA online record "
                    "search. The GIS resolves to a Henry County public-map "
                    "welcome page; the CaptureCAMA root returns a generic "
                    "Citizen Access Portal shell. No documented assessment "
                    "export/API, update cadence, or authorization for "
                    "daily/commercial access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Henry County Revenue Commissioner delinquent search"
                )
                directory_url = (
                    "https://henry.capturecama.com/DelqSearch"
                )
                note += (
                    " The county Revenue Commissioner portal exposes a "
                    "Delinquent Search, but direct retrieval returned only "
                    "the generic Citizen Access Portal shell. No current "
                    "Henry County tax-sale date, auction list, documented "
                    "feed/export/API, or automated-use permission was "
                    "verified. The DOR Henry transcript is weekly "
                    "state-held delinquent inventory, not the local auction "
                    "calendar, and DOR says transcripts lack physical "
                    "addresses."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Henry County and municipal code-enforcement contacts"
                )
                directory_url = "https://www.henrycountyal.com/"
                source_url = directory_url
                note += (
                    " The official County website identifies County "
                    "departments but no property-level code-enforcement "
                    "office or countywide open-violation list/feed. No "
                    "documented export/API, publication cadence, or "
                    "automated-use permission was verified. Confirm the "
                    "responsible provider by each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = "Henry County public notices and Sheriff's Department"
                directory_url = (
                    "https://www.henrycountyal.com/public-notice"
                )
                note += (
                    " The official County public-notice page returned "
                    "commission-meeting information, not a foreclosure or "
                    "sheriff-sale calendar/list. County search results "
                    "identify a Sheriff's Department but no county-specific "
                    "sale feed was verified. Statewide Alabama Public "
                    "Notice coverage depends on participating newspapers; "
                    "its Terms prohibit scraping, automated collection, "
                    "and commercial exploitation. No authorized daily "
                    "foreclosure source was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Henry County Probate and land records"
                directory_url = (
                    "https://www.henrycountyal.com/records-deeds"
                )
                source_url = "https://www.ingprobate.com/Henry_Probate/"
                note += (
                    " The official County Records & Deeds page describes "
                    "recorded land documents and links the Henry Probate "
                    "online-services portal. Its legal disclaimer expressly "
                    "prohibits automated systems, bots, spiders, scrapers, "
                    "offline readers, data extraction, and automated "
                    "interactions. No public lis-pendens/default index, "
                    "authorized pre-foreclosure feed, bulk export/API, or "
                    "permitted automated access was verified."
                )
        if state == "AL" and county_name == "Houston":
            if category == "assessor":
                directory_name = (
                    "Houston County Revenue Commissioner property search and GIS"
                )
                directory_url = "https://houstoncountyal.gov/revenue/"
                source_url = (
                    "https://www.ingproperty.com/Houston_Revenue/property.aspx"
                )
                note += (
                    " The official County Revenue page links a public "
                    "property-record search and the Houston County GIS "
                    "(https://isv.kcsgis.com/al.houston_revenue/). The "
                    "property portal exposes tax-year and parcel/address/"
                    "owner searches, and the GIS returned a Houston County "
                    "ISV3 shell. No documented bulk assessment export/API, "
                    "update cadence, or authorization for daily/commercial "
                    "automated access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Houston County Revenue Commissioner tax-sale page"
                )
                directory_url = (
                    "https://houstoncountyal.gov/revenue/tax_sale"
                )
                note += (
                    " The official County page announces its annual "
                    "GovEase tax-lien auction beginning May 4, 2026 and "
                    "links an updated XLSX parcel list for 2025 taxes "
                    "(https://houstoncountyal.gov/files/revenue/"
                    "2026_tax_lien_auction_parcels_for_2025_tax_year_"
                    "update_04302026_73842.xlsx; updated April 30, 2026); "
                    "the sale date is past and no 2027 date was listed. "
                    "The XLSX request redirects to an external host. No "
                    "documented recurring feed/API or permission for "
                    "daily/commercial automated ingestion was verified. "
                    "The DOR Houston transcript "
                    "(https://www.revenue.alabama.gov/wp-content/uploads/"
                    "property-tax-transcripts/WWW_TRANS_38.PDF) is separate "
                    "weekly state-held delinquent inventory, not the "
                    "county auction calendar, and DOR says transcripts "
                    "lack physical addresses."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Houston County departments and municipal code contacts"
                )
                directory_url = "https://houstoncountyal.gov/departments/"
                source_url = directory_url
                note += (
                    " The official County Departments directory lists "
                    "county services but no property-level code-enforcement "
                    "office or countywide open-violation list/feed. No "
                    "documented export/API, publication cadence, or "
                    "automated-use permission was verified. Identify and "
                    "verify the responsible provider by each property's "
                    "municipality."
                )
            elif category == "foreclosure":
                directory_name = "Houston County Sheriff's Office"
                directory_url = "https://houstoncosoal.gov/"
                note += (
                    " The County links this as the Sheriff's Office; its "
                    "official homepage provides general office information "
                    "but no real-estate foreclosure/sheriff-sale calendar "
                    "or list. A site-restricted search also exposed no "
                    "indexed sale notice. Statewide Alabama Public Notice "
                    "coverage depends on participating newspapers and its "
                    "Terms prohibit scraping, automated collection, and "
                    "commercial exploitation. No county-specific authorized "
                    "foreclosure feed or daily-use permission was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Houston County Probate recording information"
                directory_url = (
                    "https://houstoncountyal.gov/probate/recording_guidelines/"
                )
                source_url = "https://www.ingprobate.com/Houston_Probate/"
                note += (
                    " The official County Probate recording-guidelines page "
                    "describes document recording, not a searchable "
                    "pre-foreclosure list. The Houston-labeled online "
                    "Probate portal's legal disclaimer identifies the "
                    "Houston County Commission and Judge of Probate and "
                    "expressly prohibits automated systems, bots, spiders, "
                    "scrapers, offline readers, data extraction, and "
                    "automated interactions. No public lis-pendens/default "
                    "index, authorized pre-foreclosure feed, bulk export/API, "
                    "or permitted automated access was verified."
                )
        if state == "AL" and county_name == "Jackson":
            if category == "assessor":
                directory_name = "Jackson County Revenue Commissioner property search"
                directory_url = (
                    "https://www.jacksoncountyal.gov/245/"
                    "Revenue-Commissioner/revenuecommissioner"
                )
                source_url = (
                    "https://jacksonproperty.countygovservices.com/Property/Search"
                )
                note += (
                    " The official County Revenue Commissioner page links "
                    "this online property-tax search and identifies the "
                    "Revenue Commissioner as responsible for appraising "
                    "real property. The search returns a Jackson County "
                    "property-tax portal shell. No documented bulk "
                    "assessment export/API, update cadence, or permission "
                    "for daily/commercial automated access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Jackson County Revenue Commissioner tax-sale schedule"
                )
                directory_url = (
                    "https://www.jacksoncountyal.gov/245/"
                    "Revenue-Commissioner/revenuecommissioner"
                )
                note += (
                    " The official Revenue Commissioner page gives the "
                    "annual timetable: delinquency in January, newspaper "
                    "advertising in March, and tax sale in April. It does "
                    "not provide a current year-specific date or parcel "
                    "auction list; no machine-readable feed/export/API or "
                    "automated-use permission was verified. The DOR Jackson "
                    "transcript is weekly state-held delinquent inventory, "
                    "not the county auction calendar, and DOR says "
                    "transcripts lack physical addresses."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Jackson County and municipal code-enforcement contacts"
                )
                directory_url = "https://www.jacksoncountyal.gov/"
                source_url = directory_url
                note += (
                    " The official County pages reviewed did not identify "
                    "a countywide property-level code-enforcement office "
                    "or open-violation list/feed. No provider-specific "
                    "export/API, publication cadence, or automated-use "
                    "permission was verified. Confirm the responsible "
                    "provider by each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = "Jackson County Sheriff's Office"
                directory_url = "https://www.jacksoncountysheriffal.org/"
                note += (
                    " The Sheriff's website is reachable and contains "
                    "general county/office information, but the retrieved "
                    "public page exposed no real-estate foreclosure or "
                    "sheriff-sale list/calendar. Statewide Alabama Public "
                    "Notice coverage depends on participating newspapers "
                    "and its Terms prohibit scraping, automated collection, "
                    "and commercial exploitation. No county-specific "
                    "authorized foreclosure feed or automated-use "
                    "permission was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Jackson County Probate and land records"
                directory_url = (
                    "https://www.jacksoncountyal.gov/245/"
                    "Revenue-Commissioner/revenuecommissioner"
                )
                note += (
                    " The official Revenue Commissioner page says new "
                    "property deeds must be recorded in Probate Court, but "
                    "no public lis-pendens/default index, online pre-"
                    "foreclosure search, authorized feed, bulk export/API, "
                    "or permitted automated access was verified. The "
                    "statewide Alabama Public Notice database is limited "
                    "to participating newspapers and its Terms prohibit "
                    "automated/commercial collection."
                )
        if state == "AL" and county_name == "Jefferson":
            if category == "tax_sale":
                directory_name = (
                    "Alabama DOR Jefferson County delinquent-property transcripts"
                )
                note += (
                    " Jefferson County's state-held transcript inventory is "
                    "split between Birmingham and Bessemer PDFs. The "
                    "official County site at https://www.jccal.org/ returned "
                    "HTTP 403 during this check, so no local county auction "
                    "date, sale list, or bidder instructions could be "
                    "verified. The DOR transcripts are weekly state-held "
                    "inventory, not an upcoming county auction calendar, "
                    "and DOR says they lack physical addresses."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Jefferson County and municipal code-enforcement contacts"
                )
                directory_url = "https://www.jccal.org/"
                source_url = directory_url
                note += (
                    " The official County website returned HTTP 403 during "
                    "this check. No countywide property-level "
                    "code-enforcement provider, open-violation list/feed, "
                    "documented export/API, or automated-use permission "
                    "could be verified. Confirm the provider by the "
                    "property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Jefferson County Sheriff's Office and public notices"
                )
                directory_url = "https://www.jccal.org/"
                note += (
                    " The official County website returned HTTP 403, so a "
                    "county-specific Sheriff's sale calendar/list could not "
                    "be inspected. Statewide Alabama Public Notice coverage "
                    "depends on participating newspapers and its Terms "
                    "prohibit scraping, automated collection, and commercial "
                    "exploitation. No county-specific authorized foreclosure "
                    "feed or automated-use permission was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Jefferson County Probate and land records"
                directory_url = "https://www.jccal.org/"
                note += (
                    " The official County website returned HTTP 403 during "
                    "this check. No public lis-pendens/default index, "
                    "online pre-foreclosure source, authorized feed, bulk "
                    "export/API, or permitted automated access was verified. "
                    "Statewide Alabama Public Notice is limited to "
                    "participating newspapers and prohibits automated/"
                    "commercial collection."
                )
        if state == "AL" and county_name == "Lamar":
            if category == "assessor":
                directory_name = "Lamar County Revenue Commissioner and public GIS"
                source_url = "https://www.alabamagis.com/lamar/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Lamar County public GIS. Direct retrieval redirects to "
                    "the Lamar County Alabama Public GIS welcome page, not "
                    "a documented parcel-data export/API. No assessment "
                    "update cadence or authorization for daily/commercial "
                    "automated access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Lamar County Revenue Commissioner county-office listing"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Lamar"
                )
                note += (
                    " The DOR county-office listing provides the County "
                    "Revenue Commissioner contact and public GIS link, but "
                    "no Lamar-specific upcoming auction date, parcel list, "
                    "or sale calendar was verified. The DOR Lamar transcript "
                    "is weekly state-held delinquent inventory, not the "
                    "local auction calendar, and DOR says transcripts lack "
                    "physical addresses. No county-specific machine-readable "
                    "feed or automated-use permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Lamar County and municipal code-enforcement contacts"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Lamar"
                )
                source_url = directory_url
                note += (
                    " No Lamar County or municipal property-level "
                    "code-enforcement provider, open-violation list/feed, "
                    "documented export/API, or automated-use permission "
                    "was verified. Confirm the responsible provider by "
                    "each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association county directory"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                note += (
                    " The statewide Sheriff's Association directory is a "
                    "manual office-discovery starting point; no verified "
                    "Lamar-specific sheriff-sale/foreclosure calendar, "
                    "complete notice feed, or county-authorized automated "
                    "source was established. Alabama Public Notice coverage "
                    "depends on participating newspapers and its Terms "
                    "prohibit scraping, automated collection, and commercial "
                    "exploitation."
                )
            elif category == "pre_foreclosure":
                directory_name = "Lamar County Probate online records"
                directory_url = (
                    "https://www.ingprobate.com/Lamar_Probate/"
                )
                source_url = directory_url
                note += (
                    " The Lamar-labeled online Probate portal's legal "
                    "disclaimer identifies the County Commission and Judge "
                    "of Probate and expressly prohibits automated systems, "
                    "bots, spiders, scrapers, offline readers, data "
                    "extraction, and automated interactions. No public "
                    "lis-pendens/default index, authorized pre-foreclosure "
                    "feed, bulk export/API, or permitted automated access "
                    "was verified."
                )
        if state == "AL" and county_name == "Lauderdale":
            if category == "assessor":
                directory_name = (
                    "Lauderdale County Revenue Commissioner property search"
                )
                directory_url = (
                    "https://www.lauderdalecountyal.gov/Default.asp"
                )
                source_url = "https://altags.com/lauderdale_revenue/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "County website and this online appraisal/assessment "
                    "portal. The portal's legal disclaimer identifies the "
                    "Lauderdale Revenue Commission and expressly prohibits "
                    "automated systems, bots, spiders, scrapers, offline "
                    "readers, data extraction, and automated interaction. "
                    "No authorized bulk export/API, update cadence, or "
                    "daily/commercial access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Lauderdale County Revenue Commissioner county-office listing"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Lauderdale"
                )
                note += (
                    " The County homepage returned a general news/calendar "
                    "landing page; no current Lauderdale tax-sale date or "
                    "parcel auction list was verified. The DOR Lauderdale "
                    "transcript is weekly state-held delinquent inventory, "
                    "not the local auction calendar, and DOR says transcripts "
                    "lack physical addresses. The linked Revenue portal's "
                    "terms prohibit automated extraction. No county-specific "
                    "recurring feed or automated-use permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Lauderdale County and municipal code-enforcement contacts"
                )
                directory_url = (
                    "https://www.lauderdalecountyal.gov/home/departments/"
                )
                source_url = directory_url
                note += (
                    " The official County Departments page returned only "
                    "site-map/copyright information and no property-level "
                    "code-enforcement provider or countywide open-violation "
                    "feed. No documented export/API, update cadence, or "
                    "automated-use permission was verified. Confirm the "
                    "provider by each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and Lauderdale Sheriff's Office"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                note += (
                    " The possible Lauderdale Sheriff's website "
                    "(https://www.lauderdalecountysheriff.com/) redirects to "
                    "a GoDaddy parking page, so its ownership and any sale "
                    "information could not be verified. The statewide "
                    "Alabama Public Notice database depends on participating "
                    "newspapers and its Terms prohibit scraping, automated "
                    "collection, and commercial exploitation. No "
                    "county-specific authorized foreclosure feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Lauderdale County Probate online records"
                directory_url = (
                    "https://www.ingprobate.com/Lauderdale_Probate/"
                )
                source_url = directory_url
                note += (
                    " The Lauderdale-labeled Probate portal's legal "
                    "disclaimer identifies the County Commission and Judge "
                    "of Probate and expressly prohibits automated systems, "
                    "bots, spiders, scrapers, offline readers, data "
                    "extraction, and automated interactions. No public "
                    "lis-pendens/default index, authorized pre-foreclosure "
                    "feed, bulk export/API, or permitted automated access "
                    "was verified."
                )
        if state == "AL" and county_name == "Lawrence":
            if category == "assessor":
                directory_name = (
                    "Lawrence County Revenue Commissioner and Mapping & Appraisal"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Lawrence"
                )
                source_url = "https://www.lawrencecountyrevenue.com/#/"
                note += (
                    " The official Alabama DOR county-office directory "
                    "links the Lawrence County Revenue Commissioner's "
                    "website. The County Mapping and Appraisal page describes "
                    "property mapping, ownership records, and assessments; "
                    "the Revenue site returned an application shell rather "
                    "than documented parcel data. No bulk assessment "
                    "export/API, update cadence, or permission for "
                    "daily/commercial automated access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Lawrence County Revenue Commissioner tax information"
                )
                directory_url = (
                    "https://lawrencecountyal.org/revenue-commissioner/"
                )
                note += (
                    " The official County Revenue Commissioner page "
                    "describes assessment, tax collection, and ownership "
                    "records but provides no current tax-sale date or parcel "
                    "auction list. The DOR Lawrence transcript is weekly "
                    "state-held delinquent inventory, not the local auction "
                    "calendar, and DOR says transcripts lack physical "
                    "addresses. No county-specific recurring feed or "
                    "automated-use permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Lawrence County departments and municipal "
                    "code-enforcement contacts"
                )
                directory_url = "https://lawrencecountyal.org/departments/"
                source_url = directory_url
                note += (
                    " The official County Department Directory and "
                    "department pages reviewed did not identify a "
                    "property-level code-enforcement office or countywide "
                    "open-violation list/feed. No documented export/API, "
                    "update cadence, or automated-use permission was "
                    "verified. Confirm the responsible provider by each "
                    "property's municipality."
                )
            elif category == "foreclosure":
                directory_name = "Lawrence County Sheriff's Department"
                directory_url = "https://lawrencecountyal.org/sherriff-dept/"
                note += (
                    " The official Sheriff's Department page contains "
                    "general public-safety information, not a foreclosure "
                    "or sheriff-sale calendar/list. Statewide Alabama "
                    "Public Notice coverage depends on participating "
                    "newspapers and its Terms prohibit scraping, automated "
                    "collection, and commercial exploitation. No "
                    "county-specific authorized foreclosure feed or "
                    "automated-use permission was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Lawrence County Probate Judge and records"
                directory_url = "https://lawrencecountyal.org/probate-judge/"
                source_url = "https://www.ingprobate.com/Lawrence_Probate/"
                note += (
                    " The Lawrence-labeled Probate portal's legal disclaimer "
                    "identifies the Lawrence County Commission and Judge of "
                    "Probate and expressly prohibits automated systems, "
                    "bots, spiders, scrapers, offline readers, data "
                    "extraction, and automated interactions. No public "
                    "lis-pendens/default index, authorized pre-foreclosure "
                    "feed, bulk export/API, or permitted automated access "
                    "was verified."
                )
        if state == "AL" and county_name == "Lee":
            if category == "assessor":
                directory_name = (
                    "Lee County Revenue Commissioner property records and GIS"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Lee"
                )
                source_url = "https://www.altags.com/lee_license/default.aspx"
                note += (
                    " The official Alabama DOR county-office directory "
                    "links the Lee County Revenue Commissioner's website, "
                    "public GIS, and this appraisal/assessment record-search "
                    "portal. The portal's legal disclaimer identifies the "
                    "Lee County Revenue Commissioner and expressly prohibits "
                    "automated systems, scraping, data extraction, and "
                    "automated interactions. The GIS is an interactive "
                    "public map with an accuracy disclaimer; no documented "
                    "bulk export/API, update cadence, or automated-use "
                    "permission was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Lee County Revenue Commissioner property-tax information"
                )
                directory_url = (
                    "https://www.leecountyrevenuecommissioner.com/"
                    "home/property-tax/"
                )
                note += (
                    " The official Revenue Commissioner property-tax page "
                    "describes mapping, appraisal, assessment, and "
                    "collections but provides no current Lee County "
                    "tax-sale date or parcel auction list. The DOR Lee "
                    "transcript is weekly state-held delinquent inventory, "
                    "not the local auction calendar, and DOR says transcripts "
                    "lack physical addresses. The linked assessment portal "
                    "prohibits automation; no county-specific recurring "
                    "feed or automated-use permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Lee County municipalities and Planning Commission"
                )
                directory_url = "https://www.leecountyal.gov/"
                source_url = "https://leecountyplanning.com/"
                note += (
                    " The County's official site links its municipality "
                    "directory and Lee County Planning Commission. The "
                    "Planning Commission site provides planning/zoning "
                    "information, not a property-level code-enforcement "
                    "office or open-violation list/feed. No documented "
                    "export/API, publication cadence, or automated-use "
                    "permission was verified. Confirm the enforcing "
                    "municipality for each property."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Lee County Sheriff's Office and Alabama Sheriffs Association"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                note += (
                    " The official County site links the Lee County "
                    "Sheriff's Office at https://www.leecountysheriff.org/, "
                    "but that domain failed DNS resolution during this check. "
                    "The Sheriff's Association directory is a manual "
                    "discovery starting point, not a sale feed. Statewide "
                    "Alabama Public Notice coverage depends on participating "
                    "newspapers and its Terms prohibit scraping, automated "
                    "collection, and commercial exploitation. No "
                    "county-specific authorized foreclosure feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Lee County Probate Court recording division"
                directory_url = (
                    "https://www.leecountyal.gov/government/"
                    "probate_judge/recording/index.php"
                )
                source_url = directory_url
                note += (
                    " The official Probate recording page says real-estate "
                    "documents can be viewed at public stations in the "
                    "Probate Office and copies requested by mail or in "
                    "person; it does not link an online search or "
                    "pre-foreclosure index. The standard Lee-labeled "
                    "InG Probate route returned 404. Alabama Public Notice "
                    "covers participating newspapers only and its Terms "
                    "prohibit automated/commercial collection. No public "
                    "lis-pendens/default feed, authorized bulk export/API, "
                    "or permitted automated access was verified."
                )
        if state == "AL" and county_name == "Limestone":
            if category == "assessor":
                directory_name = (
                    "Limestone County Citizen Access Portal for assessment records"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Limestone"
                )
                source_url = "https://www.limestonerevenue.net/"
                note += (
                    " The official Alabama DOR county-office directory links "
                    "the Limestone County Citizen Access Portal for appraisal "
                    "and assessment records. The portal is a JavaScript-only "
                    "application shell; no documented bulk assessment "
                    "export/API, update cadence, or authorization for "
                    "daily/commercial automated access was verified. Its "
                    "robots.txt does not disallow crawlers, which is not "
                    "permission to extract data."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Limestone County Citizen Access Portal and DOR "
                    "delinquent-property transcript"
                )
                directory_url = "https://www.limestonerevenue.net/"
                note += (
                    " The County portal is an appraisal/assessment record "
                    "search; no current Limestone County tax-sale date or "
                    "parcel auction list was identified. The DOR Limestone "
                    "transcript is weekly state-held delinquent inventory, "
                    "not the local auction calendar, and DOR says transcripts "
                    "lack physical addresses. No county-specific recurring "
                    "feed, documented export/API, or automated-use permission "
                    "was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Limestone County departments and municipal "
                    "code-enforcement contacts"
                )
                directory_url = "https://www.limestonecounty-al.gov/Home"
                source_url = directory_url
                note += (
                    " The County's redesigned homepage and Departments page "
                    "reviewed did not identify a property-level "
                    "code-enforcement office or countywide open-violation "
                    "list/feed. No documented export/API, update cadence, or "
                    "automated-use permission was verified. Confirm the "
                    "responsible provider by each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and Limestone County "
                    "Sheriff's Office discovery"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                note += (
                    " The Sheriff's Association directory is a manual "
                    "office-discovery starting point; no Limestone County "
                    "sheriff-sale calendar, complete notice feed, or "
                    "county-authorized automated source was established. "
                    "Statewide Alabama Public Notice coverage depends on "
                    "participating newspapers and its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. No "
                    "authorized daily foreclosure feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Limestone County Probate online records"
                directory_url = (
                    "https://www.ingprobate.com/Limestone_Probate/"
                )
                source_url = directory_url
                note += (
                    " The Limestone-labeled Probate portal's legal "
                    "disclaimer identifies the County Commission and Judge "
                    "of Probate and expressly prohibits automated systems, "
                    "bots, spiders, scrapers, offline readers, data "
                    "extraction, and automated interactions. No public "
                    "lis-pendens/default index, authorized pre-foreclosure "
                    "feed, bulk export/API, or permitted automated access "
                    "was verified."
                )
        if state == "AL" and county_name == "Lowndes":
            if category == "assessor":
                directory_name = (
                    "Lowndes County Tax Assessor public GIS"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Lowndes"
                )
                source_url = "https://www.alabamagis.com/lowndes/"
                note += (
                    " The official Alabama DOR county-office directory "
                    "identifies the County Tax Assessor and links this "
                    "Lowndes County public GIS. The GIS disclaimer says its "
                    "data may change, accuracy is not guaranteed, and the "
                    "maps are for tax purposes rather than official ownership "
                    "records. No documented bulk assessment export/API, "
                    "update cadence, or permission for automated/commercial "
                    "access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Alabama DOR Lowndes County delinquent-property transcript"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "tax-delinquent-property-and-land-sales/"
                )
                note += (
                    " The DOR county-office listing and Lowndes GIS expose "
                    "no current County tax-sale date or parcel auction list. "
                    "The DOR Lowndes transcript is weekly state-held "
                    "delinquent inventory, not the local auction calendar, "
                    "and DOR says transcripts lack physical addresses. No "
                    "county-specific recurring feed or automated-use "
                    "permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Lowndes County and municipal code-enforcement contacts"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Lowndes"
                )
                source_url = directory_url
                note += (
                    " The DOR county-office listing identifies the Tax "
                    "Assessor and GIS only; no County property-level "
                    "code-enforcement provider or countywide open-violation "
                    "list/feed was verified. No documented export/API, update "
                    "cadence, or automated-use permission was identified. "
                    "Confirm the responsible provider by each property's "
                    "municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and Lowndes County "
                    "Sheriff's Office discovery"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                note += (
                    " The Sheriff's Association directory is a manual "
                    "office-discovery starting point; no Lowndes County "
                    "sheriff-sale calendar, complete notice feed, or "
                    "county-authorized automated source was established. "
                    "Statewide Alabama Public Notice coverage depends on "
                    "participating newspapers and its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. No "
                    "authorized daily foreclosure feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Lowndes County Probate online records"
                directory_url = (
                    "https://www.ingprobate.com/Lowndes_Probate/"
                )
                source_url = directory_url
                note += (
                    " The Lowndes-labeled Probate portal's legal disclaimer "
                    "identifies the County Commission and Judge of Probate "
                    "and expressly prohibits automated systems, bots, "
                    "spiders, scrapers, offline readers, data extraction, "
                    "and automated interactions. No public "
                    "lis-pendens/default index, authorized pre-foreclosure "
                    "feed, bulk export/API, or permitted automated access "
                    "was verified."
                )
        if state == "AL" and county_name == "Macon":
            if category == "assessor":
                directory_name = (
                    "Macon County Revenue Commissioner property search and GIS"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Macon"
                )
                source_url = "https://macon.capturecama.com/"
                note += (
                    " The official DOR county-office directory links this "
                    "Citizen Access Portal and the Macon County ArcGIS public "
                    "map. The County Revenue Commissioner describes its new "
                    "portal as a way to pay taxes and access tax information; "
                    "the portal returned a JavaScript application shell. No "
                    "documented bulk assessment export/API, update cadence, "
                    "or authorization for daily/commercial automated access "
                    "was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Macon County Revenue Commission tax-lien sale list "
                    "and auction notice"
                )
                directory_url = (
                    "https://maconcountyal.com/2025-tax-lien-list/"
                )
                note += (
                    " The official County site publishes a revised 2026 "
                    "tax-lien list for 2025 delinquent taxes (the site's "
                    "published record was modified April 8, 2026; the PDF is "
                    "https://maconcountyal.com/wp-content/uploads/2025/04/"
                    "Tax-Lien-Sale-Newspaper-List-2026-Revised.pdf). It lists "
                    "account/parcel identifiers, owners, legal descriptions, "
                    "and amounts due. The official 2026 flyer "
                    "(https://maconcountyal.com/macon-county-online-tax-lien-"
                    "auction/) schedules the online GovEase auction for May "
                    "12, 2026 at 10:00 a.m.; registration ended May 8, 2026. "
                    "That sale date has passed and no later sale/list was "
                    "verified. The annual PDF is a static snapshot, not a "
                    "daily feed; no documented recurring API or written "
                    "automated/commercial-use authorization was verified."
                    " The DOR Macon transcript remains separate weekly "
                    "state-held delinquent inventory, not the local auction "
                    "calendar, and DOR says transcripts lack physical "
                    "addresses."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Macon County Revenue Commission and municipal "
                    "code-enforcement contacts"
                )
                directory_url = "https://maconcountyal.com/"
                source_url = directory_url
                note += (
                    " The official County website reviewed is the Revenue "
                    "Commission site and its published pages cover property "
                    "taxes and tax liens, not code enforcement. No "
                    "property-level County code-enforcement office or "
                    "countywide open-violation list/feed was identified. No "
                    "documented export/API, cadence, or automated-use "
                    "permission was verified. Confirm the responsible "
                    "provider by each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and Macon County "
                    "Sheriff's Office discovery"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                note += (
                    " The Sheriff's Association directory is a manual "
                    "office-discovery starting point; no Macon County "
                    "sheriff-sale calendar, complete notice feed, or "
                    "county-authorized automated source was established. "
                    "Statewide Alabama Public Notice coverage depends on "
                    "participating newspapers and its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. No "
                    "authorized daily foreclosure feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Macon County Probate online records"
                directory_url = "https://www.ingprobate.com/Macon_Probate/"
                source_url = directory_url
                note += (
                    " The Macon-labeled Probate portal redirects to an "
                    "InG/ALTaGS portal whose legal disclaimer identifies the "
                    "Macon County Commission and Judge of Probate and "
                    "expressly prohibits automated systems, bots, spiders, "
                    "scrapers, offline readers, data extraction, and "
                    "automated interactions. No public lis-pendens/default "
                    "index, authorized pre-foreclosure feed, bulk export/API, "
                    "or permitted automated access was verified."
                )
        if state == "AL" and county_name == "Madison":
            if category == "assessor":
                directory_name = (
                    "Madison County property search and mapping portal"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Madison"
                )
                source_url = (
                    "https://madisonproperty.countygovservices.com/"
                    "Property/Property/Search"
                )
                note += (
                    " The official DOR county-office directory links this "
                    "property-record search and the Madison County ISV3 "
                    "mapping portal. The retrieved search page displayed a "
                    "2025 valuation-protest notice, not a documented bulk "
                    "data export. The County website returned HTTP 403; no "
                    "bulk assessment export/API, update cadence, or "
                    "permission for automated/commercial use was verified. "
                    "The portal's robots.txt and terms-of-use routes returned "
                    "404, which does not grant automated-access permission."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Alabama DOR Madison County delinquent-property transcript"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "tax-delinquent-property-and-land-sales/"
                )
                note += (
                    " The County website and Tax Assessor page returned "
                    "HTTP 403, so a current Madison County tax-sale date or "
                    "auction list could not be inspected. The DOR Madison "
                    "transcript is weekly state-held delinquent inventory, "
                    "not the local auction calendar, and DOR says transcripts "
                    "lack physical addresses. No county-specific recurring "
                    "feed or automated-use permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Madison County and municipal code-enforcement contacts"
                )
                directory_url = "https://www.madisoncountyal.gov/"
                source_url = directory_url
                note += (
                    " The official County homepage and Tax Assessor page "
                    "returned HTTP 403 during this check. No countywide "
                    "property-level code-enforcement provider or open-"
                    "violation list/feed could be verified. No documented "
                    "export/API, publication cadence, or automated-use "
                    "permission was identified. Confirm the responsible "
                    "provider by each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Madison County Sheriff's Office discovery and "
                    "Alabama Sheriffs Association"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                note += (
                    " The official County website returned HTTP 403, so a "
                    "Madison County sheriff-sale calendar or list could not "
                    "be inspected. The Sheriff's Association directory is a "
                    "manual office-discovery starting point, not a sale feed. "
                    "Statewide Alabama Public Notice coverage depends on "
                    "participating newspapers and its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. No "
                    "authorized county-specific foreclosure feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Madison County Probate and recording records"
                directory_url = "https://www.madisoncountyal.gov/"
                source_url = directory_url
                note += (
                    " The official County website returned HTTP 403, and "
                    "the tested Madison-labeled InG Probate route returned "
                    "404. No public lis-pendens/default index, online "
                    "pre-foreclosure search, authorized bulk export/API, or "
                    "permitted automated access was verified. Statewide "
                    "Alabama Public Notice coverage is limited to "
                    "participating newspapers and its Terms prohibit "
                    "automated/commercial collection."
                )
        if state == "AL" and county_name == "Marengo":
            if category == "assessor":
                directory_name = (
                    "Marengo County public GIS and assessment-record search"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Marengo"
                )
                source_url = "https://marengo.alabamagis.com/Marengo/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "County website, public GIS, and an appraisal/assessment "
                    "record-search route at "
                    "https://altags.com/marengo_revenue/bpplogin.aspx. That "
                    "search route requires a business personal property "
                    "location number and access code; it is not a public "
                    "residential parcel feed. The County GIS page links this "
                    "Marengo-specific public map, which returned a GIS "
                    "welcome page; the older DOR-linked "
                    "https://www.alabamagis.com/marengo/ route returned "
                    "HTTP 503. No documented residential bulk export/API, "
                    "update cadence, or authorization for daily/commercial "
                    "automated access was verified."
                )
            elif category == "tax_sale":
                directory_name = "Marengo County Revenue Commission tax-lien sale"
                directory_url = (
                    "https://www.marengocountyal.com/home/revenue/"
                    "tax-lien-information/"
                )
                note += (
                    " The official County Tax Lien Information page states "
                    "that the annual auction for unpaid 2025 ad valorem "
                    "property taxes was scheduled for Tuesday, May 5, 2026 "
                    "at 8:30 a.m. on GovEase; that date has passed and no "
                    "later or next-year sale date was verified. The County's "
                    "Tax Lien Auction FAQ says the auction is held once per "
                    "year between March 1 and June 15 and that sale lists "
                    "appear at least 30 days beforehand on GovEase and the "
                    "County website. The County page also directs users to "
                    "the current delinquent-property list at "
                    "https://www.altags.com/marengo_revenue/default.aspx; "
                    "the portal's legal disclaimer expressly prohibits "
                    "automated systems, bots, scrapers, data extraction, and "
                    "automated interaction. No permitted recurring API or "
                    "daily/commercial access was verified. The DOR Marengo "
                    "transcript remains weekly state-held delinquent "
                    "inventory, not the local auction calendar, and DOR "
                    "says transcripts lack physical addresses."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Marengo County and municipal code-enforcement contacts"
                )
                directory_url = "https://www.marengocountyal.com/"
                source_url = directory_url
                note += (
                    " The reviewed official County home, Revenue, and "
                    "Probate pages provide tax, GIS, and probate information "
                    "but did not identify a countywide property-level "
                    "code-enforcement provider or open-violation list/feed. "
                    "No documented export/API, publication cadence, or "
                    "automated-use permission was verified. Confirm the "
                    "responsible provider by each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Marengo County Sheriff-sale and foreclosure discovery"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The tested County /home/sheriff/ route redirected to "
                    "the general homepage and exposed no sheriff-sale "
                    "calendar or list. The Alabama Sheriffs Association "
                    "directory is a manual office-discovery aid, not a sale "
                    "feed. Statewide Alabama Public Notice coverage depends "
                    "on participating newspapers, and its Terms prohibit "
                    "scraping, automated collection, and commercial "
                    "exploitation. No authorized county foreclosure feed "
                    "was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Marengo County Probate Judge and recording information"
                )
                directory_url = (
                    "https://www.marengocountyal.com/home/probate/"
                    "office-of-the-probate-judge/welcome-to-the-probate-office/"
                )
                source_url = directory_url
                note += (
                    " The official Probate Judge page describes probate "
                    "court and recording services but does not expose a "
                    "public lis-pendens/default search. The tested Marengo-"
                    "labeled InG Probate route returned 404. No public "
                    "county lis-pendens/default index, authorized bulk "
                    "export/API, or permitted automated pre-foreclosure "
                    "source was verified."
                )
        if state == "AL" and county_name == "Marion":
            if category == "assessor":
                directory_name = "Marion County public GIS and property-tax office"
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Marion"
                )
                source_url = "https://marion.alabamagis.com/marion/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "County website and public GIS. The County Property Tax "
                    "Office page provides tax-office information and payment "
                    "links; the County-linked GIS route redirected to this "
                    "Marion-specific public GIS welcome page. No documented "
                    "residential parcel export/API, update cadence, or "
                    "authorization for daily/commercial automated access "
                    "was verified."
                )
            elif category == "tax_sale":
                directory_name = "Marion County Property Tax Office delinquent list"
                directory_url = (
                    "https://www.marioncountyal.org/home/departments/"
                    "revenue-commissioner/tax-commission/property-tax-office/"
                )
                note += (
                    " The official County Property Tax Office page links a "
                    "delinquent-property list at "
                    "https://www.ingproperty.com/Marion_Revenue/Delinquent.aspx; "
                    "the tested endpoint displayed 'DELINQUENT LIST "
                    "UNAVAILABLE'. The County pages reviewed did not provide "
                    "a current tax-sale date or auction list. The DOR Marion "
                    "transcript is weekly state-held delinquent inventory, "
                    "not the local auction calendar, and DOR says transcripts "
                    "lack physical addresses. No authorized recurring "
                    "county tax-sale feed or automated-use permission was "
                    "verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Marion County departments and municipal code enforcement"
                )
                directory_url = (
                    "https://www.marioncountyal.org/home/departments/"
                )
                source_url = directory_url
                note += (
                    " The official County departments listing and "
                    "department pages reviewed did not identify a "
                    "countywide property-level code-enforcement provider or "
                    "open-violation list/feed. No documented export/API, "
                    "publication cadence, or automated-use permission was "
                    "verified. Confirm the responsible provider by each "
                    "property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Marion County Sheriff's Office Civil Process"
                )
                directory_url = "https://www.marionsoal.com/civil-process"
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The official Sheriff's Civil Process page describes "
                    "service of court papers, including writs and executions, "
                    "but publishes no real-estate sale calendar or list. "
                    "Statewide Alabama Public Notice coverage depends on "
                    "participating newspapers, and its Terms prohibit "
                    "scraping, automated collection, and commercial "
                    "exploitation. No authorized county foreclosure feed "
                    "was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Marion County Probate online public records"
                directory_url = (
                    "https://www.marioncountyal.org/home/departments/"
                    "probate-office/public-records/"
                )
                source_url = (
                    "https://www.ingprobate.com/Marion_Probate/default.aspx"
                )
                note += (
                    " The official County Public Records page links an "
                    "online recorded-documents portal. Its legal disclaimer "
                    "expressly prohibits automated systems, bots, scrapers, "
                    "data extraction, and automated interaction. A specific "
                    "public lis-pendens/default index, permitted bulk "
                    "export/API, or authorized automated pre-foreclosure "
                    "source was not verified."
                )
        if state == "AL" and county_name == "Marshall":
            if category == "assessor":
                directory_name = (
                    "Marshall County Revenue Commissioner property search"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Marshall"
                )
                source_url = (
                    "https://marshall.countygovservices.com/property/"
                    "Property/Search"
                )
                note += (
                    " The official DOR county-office directory links the "
                    "Marshall Revenue Commissioner. Its official "
                    "GIS-and-property-search page links this CountyGovServices "
                    "property-tax search and the "
                    "https://isv.kcsgis.com/al.marshall_revenue/ ISV3 map; "
                    "both returned public application/map shells. The "
                    "Revenue Commissioner says it maps and values County "
                    "parcels, but the site states its information is for tax "
                    "purposes only. No documented residential bulk "
                    "export/API, update cadence, or authorization for "
                    "daily/commercial automated access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Marshall County Revenue Commissioner tax-lien sale information"
                )
                directory_url = (
                    "https://marshallrc.org/property-tax-information/"
                )
                note += (
                    " The official Revenue Commissioner property-tax page "
                    "says delinquent notices are mailed in January, notices "
                    "advising owners of the next tax-lien auction are mailed "
                    "in March, and the annual sale is normally held the first "
                    "Tuesday in May. This is a general schedule, not an "
                    "event-specific notice or parcel sale list; no dated "
                    "2026 auction notice or current county sale list was "
                    "verified, and the usual May window had passed by this "
                    "2026-10-19 check. The DOR Marshall transcript is weekly "
                    "state-held delinquent inventory, not the local auction "
                    "calendar, and DOR says transcripts lack physical "
                    "addresses. No authorized recurring county tax-sale "
                    "feed or automated-use permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Marshall County License Inspection and Solid Waste"
                )
                directory_url = (
                    "https://www.marshallal.gov/departments/solidwaste/"
                    "solidwaste.html"
                )
                source_url = directory_url
                note += (
                    " The County department page identifies a License "
                    "Inspection/Solid Waste office and says it is responsible "
                    "for license inspection; it publishes no property-level "
                    "code-enforcement provider or open-violation list/feed. "
                    "No documented export/API, publication cadence, or "
                    "automated-use permission was verified. Confirm the "
                    "responsible provider by each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Marshall County Sheriff's Office calendar and Court Division"
                )
                directory_url = "https://www.marshallso.org/calendar"
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The official Sheriff's calendar currently says there "
                    "are no items available. Its Court Division page describes "
                    "serving writs of execution and evictions but exposes no "
                    "real-estate sale calendar/list. Statewide Alabama Public "
                    "Notice coverage depends on participating newspapers, "
                    "and its Terms prohibit scraping, automated collection, "
                    "and commercial exploitation. No authorized county "
                    "foreclosure feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Marshall County Probate Judge and deed-record lookup"
                )
                directory_url = (
                    "https://www.marshallal.gov/departments/probate/"
                    "probate.html"
                )
                source_url = "https://www.ingprobate.com/Marshall_Probate/"
                note += (
                    " The official County website links a Probate deed "
                    "lookup/online records portal. Its legal disclaimer "
                    "expressly prohibits automated systems, bots, scrapers, "
                    "data extraction, and automated interaction. A specific "
                    "public lis-pendens/default index, permitted bulk "
                    "export/API, or authorized automated pre-foreclosure "
                    "source was not verified."
                )
        if state == "AL" and county_name == "Mobile":
            if category == "assessor":
                directory_name = (
                    "Mobile County Revenue Commissioner property search"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Mobile"
                )
                source_url = "https://esearch.mobilecopropertytax.com/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Mobile County Property Tax website and Citizen Access "
                    "Portal. The County website links this property search "
                    "and an interactive map; the search displays 2026 values "
                    "and says records are for appraisal use, not legal use "
                    "or conveyance. Its Terms restrict commercial endeavors "
                    "unless specifically approved and prohibit unauthorized "
                    "data scrubbing. No written approval, documented bulk "
                    "export/API, or daily automated-use permission was "
                    "verified."
                )
            elif category == "tax_sale":
                directory_name = "Mobile County Revenue Commissioner tax-lien auction"
                directory_url = "https://mobilecopropertytax.com/taxliensale/"
                note += (
                    " The official Tax Sale FAQ lists the 2025 tax-lien "
                    "auction for Monday, May 11, 2026, starting at 8:30 a.m. "
                    "CDT on GovEase; that sale has passed. The County said "
                    "the list would be available by March 30, 2026. Its "
                    "official 2025 auction workbook was last modified March "
                    "31, 2026 and contains 10,506 data rows; the final "
                    "Call News delinquency CSV was last modified April 16, "
                    "2026 and contains 8,963 data rows. These are dated "
                    "annual-sale snapshots, not a daily feed; no next sale "
                    "date/list or automated commercial-use permission was "
                    "verified. The DOR Mobile transcript is separate weekly "
                    "state-held delinquent inventory, not the local auction "
                    "calendar, and DOR says transcripts lack physical "
                    "addresses."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Mobile County Environmental Enforcement and Inspection Services"
                )
                directory_url = (
                    "https://www.mobilecountyal.gov/government/departments/"
                    "environmental-enforcement/"
                )
                source_url = directory_url
                note += (
                    " Environmental Enforcement handles the County Junk "
                    "Control Ordinance and State litter laws in unincorporated "
                    "Mobile County; separate Inspection Services regulates "
                    "construction, demolition, alteration, and repair under "
                    "building codes in unincorporated areas. The reviewed "
                    "pages publish no searchable property-level violation "
                    "list/feed or bulk export/API. The County offers a public "
                    "records-request form for manual requests; no daily "
                    "automated-access authorization was verified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Mobile County Sheriff's Office Civil Division and sale notices"
                )
                directory_url = (
                    "https://www.mobileso.com/civil-division-central-records/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The official Sheriff's Office says Alabama foreclosures "
                    "are non-judicial and the Sheriff becomes involved only "
                    "after an ejectment order; court-ordered Sheriff's Sale "
                    "notices are advertised in local newspapers and at "
                    "https://www.alabamalegals.com/. The cited Alabama Legals "
                    "site failed HTTPS retrieval and its HTTP route returned "
                    "404 in this check. Statewide Alabama Public Notice "
                    "coverage depends on participating newspapers, and its "
                    "Terms prohibit scraping, automated collection, and "
                    "commercial exploitation. No authorized county-specific "
                    "foreclosure feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Mobile County Probate Court real-property records search"
                )
                directory_url = (
                    "https://probate.mobilecountyal.gov/public-records/"
                    "records-search"
                )
                source_url = (
                    "https://benchmark.probate.mobilecountyal.gov/"
                    "LandmarkWeb/Account/LogOn/"
                )
                note += (
                    " The official Probate Court says its Landmark WEB "
                    "system indexes real-property records from 1813 to the "
                    "present. Index search requires registration; document "
                    "images cost $0.10 per page or a $125 monthly subscription. "
                    "The County says online records are a courtesy and not "
                    "official court records. No documented bulk export/API, "
                    "automated-access authorization, or dedicated public "
                    "lis-pendens/default feed was verified."
                )
        if state == "AL" and county_name == "Monroe":
            if category == "assessor":
                directory_name = (
                    "Monroe County public GIS and appraisal/assessment portal"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Monroe"
                )
                source_url = (
                    "https://monroe.capturecama.com/CAPortal_MainPage.aspx"
                )
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Monroe County public GIS and Citizen Access Portal at "
                    "https://monroe.capturecama.com/. Both County-specific "
                    "routes returned only the generic Citizen Access Portal "
                    "application shell. No documented residential data "
                    "export/API, update cadence, or authorization for "
                    "daily/commercial automated access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Monroe County tax-sale source directory and DOR transcript"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Monroe"
                )
                note += (
                    " The reviewed DOR County-office entry links appraisal "
                    "and GIS portals but no Monroe County tax-sale calendar "
                    "or auction list. The DOR Monroe transcript is weekly "
                    "state-held delinquent inventory, not the local auction "
                    "calendar, and DOR says transcripts lack physical "
                    "addresses. No county-specific sale date, recurring "
                    "feed, or automated-use permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Monroe County and municipal code-enforcement discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Monroe"
                )
                source_url = directory_url
                note += (
                    " The reviewed DOR County-office entry and linked "
                    "CaptureCAMA portals are for property assessment/GIS and "
                    "do not identify a code-enforcement provider or "
                    "property-level open-violation feed. No Countywide "
                    "export/API, update cadence, or automated-use permission "
                    "was verified. Confirm the responsible provider by each "
                    "property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and statewide notice search"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " No Monroe County sheriff-sale calendar or "
                    "county-authorized foreclosure notice feed was verified. "
                    "The Sheriffs Association page is a manual office-"
                    "discovery directory, not a sales feed. Statewide Alabama "
                    "Public Notice has participating-newspaper coverage "
                    "only, and its Terms prohibit scraping, automated "
                    "collection, and commercial exploitation. No authorized "
                    "daily source was established."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Monroe County License Commissioner online portal "
                    "(not land records)"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Monroe"
                )
                source_url = "https://www.ingprobate.com/Monroe_Probate/"
                note += (
                    " The tested Monroe-labeled InG route identifies the "
                    "Monroe County License Commissioner, not a Probate "
                    "land-records or pre-foreclosure search. Its disclaimer "
                    "expressly prohibits automated systems, bots, scrapers, "
                    "and data extraction. No verified public lis-pendens/"
                    "default index, county recording source, bulk export/API, "
                    "or authorized pre-foreclosure feed was identified."
                )
        if state == "AL" and county_name == "Montgomery":
            if category == "assessor":
                directory_name = (
                    "Montgomery County Revenue Commissioner appraisal and "
                    "assessment portal"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Montgomery"
                )
                source_url = "https://montgomery.capturecama.com/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "official County website at https://www.mc-ala.org/ and "
                    "the Citizen Access Portal at "
                    "https://montgomery.capturecama.com/. The County website "
                    "redirected to https://www.montgomerycountyal.gov/ and "
                    "returned HTTP 403; the CaptureCAMA route returned only "
                    "the generic Citizen Access Portal application shell. "
                    "No documented parcel export/API, update cadence, or "
                    "authorization for daily/commercial automated access "
                    "was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Montgomery County tax-sale discovery and DOR transcript"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Montgomery"
                )
                note += (
                    " The DOR Montgomery County entry links the County "
                    "website, which redirected to "
                    "https://www.montgomerycountyal.gov/ and returned HTTP "
                    "403; no local tax-sale calendar, parcel list, sale "
                    "platform, or next auction date could be verified. The "
                    "DOR Montgomery transcript is weekly state-held "
                    "delinquent inventory, not a local auction calendar, "
                    "and DOR transcripts lack physical addresses. No "
                    "recurring county feed or automated-use permission was "
                    "verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Montgomery County and municipal code-enforcement "
                    "discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Montgomery"
                )
                source_url = directory_url
                note += (
                    " The DOR County-office entry and linked assessment "
                    "portal do not identify a code-enforcement provider or "
                    "property-level violation feed, and the official County "
                    "website returned HTTP 403 after redirect. No "
                    "countywide violation export/API, update cadence, or "
                    "automated-use permission was verified. Confirm the "
                    "responsible provider for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and statewide notice search"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " No Montgomery County sheriff-sale calendar or "
                    "county-authorized foreclosure notice feed was verified. "
                    "The Sheriffs Association page is a manual office-"
                    "discovery directory, not a sales feed. Statewide "
                    "Alabama Public Notice has participating-newspaper "
                    "coverage only, and its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. No "
                    "authorized daily source was established."
                )
            elif category == "pre_foreclosure":
                directory_name = "Montgomery County Probate online portal"
                directory_url = (
                    "https://www.ingprobate.com/Montgomery_Probate/"
                )
                source_url = directory_url
                note += (
                    " The tested Montgomery County Probate portal's legal "
                    "disclaimer identifies the County Commission and Judge "
                    "of Probate, but no public lis-pendens/default index or "
                    "specific pre-foreclosure search was documented. Its "
                    "terms expressly prohibit automated systems, bots, "
                    "spiders, scrapers, offline readers, data extraction, "
                    "and automated interactions. No bulk export/API or "
                    "authorized daily pre-foreclosure feed was verified."
                )
        if state == "AL" and county_name == "Morgan":
            if category == "assessor":
                directory_name = (
                    "Morgan County Revenue Commissioner property records"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Morgan"
                )
                source_url = (
                    "https://morgan.capturecama.com/CA_ParcelSearch.aspx"
                )
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Morgan County Revenue Commissioner's website at "
                    "https://www.morgancountyrevenue.com/. Its property-"
                    "search page describes tax/appraisal records as "
                    "uploaded frequently but warns they may lag; it links "
                    "the real-property search, business-personal-property "
                    "portal, and GIS. Both direct Citizen Access routes "
                    "returned only the generic application shell, while "
                    "http://isv.kcsgis.com/al.morgan_revenue/ returned an "
                    "interactive ISV3 shell. No documented residential "
                    "bulk export/API, reliable update cadence, or "
                    "daily/commercial automation permission was verified. "
                    "CaptureCAMA's robots.txt allows crawling but does not "
                    "grant data-extraction authorization."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Morgan County Revenue Commissioner annual tax-lien sale"
                )
                directory_url = (
                    "https://www.morgancountyrevenue.com/tax-sale"
                )
                note += (
                    " The official Revenue Commissioner page says "
                    "delinquent property is auctioned each May and lists "
                    "the 2026 sale for Tuesday, May 12, 2026 at 10:00 AM "
                    "online; that date has passed. Its linked official "
                    "four-page PDF "
                    "(https://www.morgancountyrevenue.com/images/stories/"
                    "PDFS/Final_1stADFile_750Parcels.pdf) contains 750 "
                    "parcel entries and is a dated sale-list snapshot, "
                    "not a daily feed. The notice explains that this is a "
                    "tax-lien auction, not a purchase of the property. "
                    "The County site's robots.txt disallows /images/, "
                    "which contains the list; do not automate access "
                    "without permission. The next sale date and an "
                    "authorized machine-readable sale feed were not "
                    "verified. The DOR Morgan transcript remains weekly "
                    "state-held delinquent inventory, not the local "
                    "auction calendar, and DOR transcripts lack physical "
                    "addresses."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Morgan County Commission and municipal code-enforcement "
                    "discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Morgan"
                )
                source_url = directory_url
                note += (
                    " The Morgan County Revenue Commissioner site links "
                    "http://www.co.morgan.al.us/ as the County Commission "
                    "website, but the link timed out on both HTTP and "
                    "HTTPS during verification. The reviewed Revenue and "
                    "DOR pages do not identify a county code-enforcement "
                    "provider or property-level violation feed. No "
                    "countywide export/API, update cadence, or automated-"
                    "use permission was verified; confirm the responsible "
                    "provider for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and statewide notice search"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " No Morgan County sheriff-sale calendar or "
                    "county-authorized foreclosure notice feed was verified. "
                    "The Sheriffs Association page is a manual office-"
                    "discovery directory, not a sales feed. Statewide "
                    "Alabama Public Notice has participating-newspaper "
                    "coverage only, and its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. No "
                    "authorized daily source was established."
                )
            elif category == "pre_foreclosure":
                directory_name = "Morgan County Probate Judge records website"
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Morgan"
                )
                source_url = "http://www.morgancountyprobate.com/"
                note += (
                    " The Morgan County Revenue Commissioner links this "
                    "Probate Judge website. Its public page says document "
                    "searches require a username and password; no open "
                    "lis-pendens/default index, public pre-foreclosure "
                    "search, bulk export/API, or permission for automated "
                    "access was documented. The tested Morgan-labeled InG "
                    "portal route returned HTTP 404. No authorized daily "
                    "pre-foreclosure feed was verified."
                )
        if state == "AL" and county_name == "Perry":
            if category == "assessor":
                directory_name = "Perry County public GIS"
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Perry"
                )
                source_url = "https://perry.alabamagis.com/perry/"
                note += (
                    " The Alabama DOR county-office directory links Perry "
                    "County's Public GIS at "
                    "https://www.alabamagis.com/perry/, which redirects to "
                    "https://perry.alabamagis.com/perry/ and displays a "
                    "GIS welcome page. A direct HTTP request returned an "
                    "empty response body, consistent with a client-rendered "
                    "viewer; no residential assessment export/API, parcel "
                    "download, update cadence, or automated-use permission "
                    "was documented."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Perry County DOR delinquent-land inventory and sale "
                    "discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "tax-delinquent-property-and-land-sales/"
                )
                note += (
                    " The DOR tax-delinquent page links the Perry County "
                    "transcript (WWW_TRANS_53.PDF), generated "
                    "2026-10-19. This one-page weekly state inventory lists "
                    "delinquent land and parcel/account identifiers, not "
                    "physical addresses or a local auction calendar. The "
                    "DOR county-office entry links only the public GIS; no "
                    "Perry-specific auction date, sale list, platform, "
                    "recurring local feed, or automated-use permission was "
                    "verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Perry County and municipal code-enforcement discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Perry"
                )
                source_url = directory_url
                note += (
                    " The DOR county-office entry links a property GIS but "
                    "does not identify a code-enforcement provider or "
                    "property-level violation feed. No Countywide or "
                    "municipal export/API, update cadence, or permission "
                    "for automated access was verified; identify the "
                    "responsible provider for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and statewide notice search"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " No Perry County sheriff-sale calendar or "
                    "county-authorized foreclosure notice feed was verified. "
                    "The Sheriffs Association page is a manual office-"
                    "discovery directory, not a sales feed. Statewide "
                    "Alabama Public Notice has participating-newspaper "
                    "coverage only, and its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. No "
                    "authorized daily source was established."
                )
            elif category == "pre_foreclosure":
                directory_name = "Perry County Probate online portal"
                directory_url = (
                    "https://www.ingprobate.com/Perry_Probate/"
                )
                source_url = directory_url
                note += (
                    " The tested Perry Probate portal's legal disclaimer "
                    "identifies the Perry County Commission and Perry "
                    "Probate Judge, but no public lis-pendens/default index "
                    "or specific pre-foreclosure search was documented. "
                    "Its terms expressly prohibit automated systems, bots, "
                    "spiders, scrapers, offline readers, data extraction, "
                    "and automated interactions. No bulk export/API or "
                    "authorized daily pre-foreclosure feed was verified."
                )
        if state == "AL" and county_name == "Pickens":
            if category == "assessor":
                directory_name = (
                    "Pickens County tax portal and public GIS"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Pickens"
                )
                source_url = "https://taxes.pickensalabama.com/#/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Pickens County tax website at "
                    "https://taxes.pickensalabama.com/#/ and Public GIS at "
                    "https://www.alabamagis.com/pickens/. The tax website "
                    "rendered only a Loading screen and accessibility link; "
                    "its robots.txt route returned the same app shell. The "
                    "GIS link redirects to "
                    "https://pickens.alabamagis.com/pickens/ and displays "
                    "a welcome page. No accessible residential parcel "
                    "search, bulk export/API, update cadence, or "
                    "automated-use permission was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Pickens County DOR delinquent-land inventory and sale "
                    "discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "tax-delinquent-property-and-land-sales/"
                )
                note += (
                    " The DOR tax-delinquent page links Pickens County to "
                    "WWW_TRANS_54.PDF, generated 2026-10-19. The one-page "
                    "transcript contains only the report header and no "
                    "parcel/owner rows in the retrieved snapshot; it is a "
                    "weekly state inventory, not a local auction calendar. "
                    "The DOR-linked County tax site rendered only a Loading "
                    "screen. No Pickens-specific sale date, parcel list, "
                    "platform, recurring feed, or automated-use permission "
                    "was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Pickens County and municipal code-enforcement discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Pickens"
                )
                source_url = directory_url
                note += (
                    " The DOR county-office entry and linked County tax/GIS "
                    "sites do not identify a code-enforcement provider or "
                    "property-level violation feed; the County tax site "
                    "rendered only a Loading screen. No countywide or "
                    "municipal export/API, update cadence, or automated-use "
                    "permission was verified. Confirm the responsible "
                    "provider for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and statewide notice search"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " No Pickens County sheriff-sale calendar or "
                    "county-authorized foreclosure notice feed was verified. "
                    "The Sheriffs Association page is a manual office-"
                    "discovery directory, not a sales feed. Statewide "
                    "Alabama Public Notice has participating-newspaper "
                    "coverage only, and its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. No "
                    "authorized daily source was established."
                )
            elif category == "pre_foreclosure":
                directory_name = "Pickens County Probate online portal"
                directory_url = (
                    "https://www.ingprobate.com/Pickens_Probate/"
                )
                source_url = directory_url
                note += (
                    " The tested Pickens Probate portal's legal disclaimer "
                    "identifies the Pickens County Commission and Pickens "
                    "Judge of Probate, but no public lis-pendens/default "
                    "index or specific pre-foreclosure search was "
                    "documented. Its terms expressly prohibit automated "
                    "systems, bots, spiders, scrapers, offline readers, data "
                    "extraction, and automated interactions. No bulk "
                    "export/API or authorized daily pre-foreclosure feed "
                    "was verified."
                )
        if state == "AL" and county_name == "Randolph":
            if category == "assessor":
                directory_name = "Randolph County DOR-linked public GIS"
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Randolph"
                )
                source_url = "https://isv.kcsgis.com/al.randolph_revenue/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Randolph County Public GIS at "
                    "https://isv.kcsgis.com/al.randolph_revenue/. That "
                    "County-specific route returned HTTP 404 during "
                    "verification. No alternate public residential "
                    "assessment search, export/API, update cadence, or "
                    "automated-use permission was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Randolph County DOR delinquent-land inventory and sale "
                    "discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "tax-delinquent-property-and-land-sales/"
                )
                note += (
                    " The DOR tax-delinquent page links Randolph County "
                    "to WWW_TRANS_56.PDF, generated 2026-10-19. This "
                    "one-page weekly state inventory lists delinquent-land "
                    "owners and parcel/account identifiers, not physical "
                    "addresses or the local auction calendar. The DOR "
                    "county-office entry links only the Public GIS route, "
                    "which returned HTTP 404. No Randolph-specific auction "
                    "date, sale list, platform, recurring local feed, or "
                    "automated-use permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Randolph County and municipal code-enforcement "
                    "discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Randolph"
                )
                source_url = directory_url
                note += (
                    " The DOR county-office entry links a Public GIS route "
                    "that returned HTTP 404 and does not identify a "
                    "code-enforcement provider or property-level violation "
                    "feed. No countywide or municipal export/API, update "
                    "cadence, or automated-use permission was verified. "
                    "Confirm the responsible provider for each property's "
                    "municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and statewide notice search"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " No Randolph County sheriff-sale calendar or "
                    "county-authorized foreclosure notice feed was "
                    "verified. The Sheriffs Association page is a manual "
                    "office-discovery directory, not a sales feed. "
                    "Statewide Alabama Public Notice has participating-"
                    "newspaper coverage only, and its Terms prohibit "
                    "scraping, automated collection, and commercial "
                    "exploitation. No authorized daily source was "
                    "established."
                )
            elif category == "pre_foreclosure":
                directory_name = "Randolph County Probate online portal"
                directory_url = "https://www.ingprobate.com/Randolph_Probate/"
                source_url = directory_url
                note += (
                    " The tested Randolph Probate portal's legal "
                    "disclaimer identifies the Randolph County Commission "
                    "and Randolph Judge of Probate, but no public "
                    "lis-pendens/default index or specific pre-foreclosure "
                    "search was documented. Its terms expressly prohibit "
                    "automated systems, bots, spiders, scrapers, offline "
                    "readers, data extraction, and automated interactions. "
                    "No bulk export/API or authorized daily "
                    "pre-foreclosure feed was verified."
                )
        if state == "AL" and county_name == "Pike":
            if category == "assessor":
                directory_name = (
                    "Pike County Revenue Commissioner property-tax search"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Pike"
                )
                source_url = (
                    "https://www.pikerevenue.com/home/taxpayer-search-and-pay/"
                )
                note += (
                    " The Alabama DOR county-office directory links Pike "
                    "County's Revenue Commissioner website, Public GIS, "
                    "and an Altags appraisal/assessment route. The County "
                    "Taxpayer Search & Pay page warns that information may "
                    "be slightly dated but exposes no embedded public "
                    "search form or data endpoint in its retrieved HTML. "
                    "The Altags route is a business-personal-property "
                    "return portal requiring a BPP location number and "
                    "access code, not a residential parcel search; its "
                    "legal disclaimer expressly prohibits automated "
                    "systems, scraping, and data extraction. The GIS route "
                    "redirects to a welcome page. No residential bulk "
                    "export/API, reliable update cadence, or authorized "
                    "daily/commercial access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Pike County Revenue Commissioner delinquent-tax "
                    "method notice"
                )
                directory_url = (
                    "https://www.pikerevenue.com/home/news/main/"
                    "?pg=News&action=view&aid=30"
                )
                note += (
                    " The official County Revenue Commissioner notice "
                    "states that Pike selected the tax-lien auction method "
                    "for 2020-2021 and future years unless changed; it "
                    "does not provide an event-specific sale date, parcel "
                    "list, or auction platform. The DOR Pike transcript is "
                    "weekly state-held delinquent-land inventory, not the "
                    "local auction calendar, and DOR transcripts lack "
                    "physical addresses. The County's attempted tax-sale "
                    "routes returned the generic homepage. No current "
                    "Pike sale schedule, recurring local feed, or "
                    "automated-use authorization was verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Pike County and municipal code-enforcement discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Pike"
                )
                source_url = directory_url
                note += (
                    " The DOR county-office entry and linked Revenue "
                    "Commissioner pages cover property tax, assessment, "
                    "and GIS but do not identify a code-enforcement "
                    "provider or property-level violation feed. No "
                    "countywide or municipal export/API, update cadence, "
                    "or automated-use permission was verified. Confirm "
                    "the responsible provider for each property's "
                    "municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and statewide notice search"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " No Pike County sheriff-sale calendar or "
                    "county-authorized foreclosure notice feed was "
                    "verified. The Sheriffs Association page is a manual "
                    "office-discovery directory, not a sales feed. "
                    "Statewide Alabama Public Notice has participating-"
                    "newspaper coverage only, and its Terms prohibit "
                    "scraping, automated collection, and commercial "
                    "exploitation. No authorized daily source was "
                    "established."
                )
            elif category == "pre_foreclosure":
                directory_name = "Pike County Probate source discovery"
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Pike"
                )
                source_url = "https://www.ingprobate.com/Pike_Probate/"
                note += (
                    " The tested Pike-labeled InG Probate route returned "
                    "HTTP 404, and the DOR county-office entry does not "
                    "link a Probate land-record search. No verified public "
                    "lis-pendens/default index, recording search, bulk "
                    "export/API, or permitted pre-foreclosure source was "
                    "identified. No authorized daily feed was verified."
                )
        if state == "AL" and county_name == "Russell":
            if category == "assessor":
                directory_name = (
                    "Russell County Revenue Commissioner assessment portals"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Russell"
                )
                source_url = "https://russell.capturecama.com/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Russell County Revenue Commissioner's website, "
                    "Citizen Access Portal, and Public GIS. The Revenue "
                    "site rendered only a Loading screen; CaptureCAMA "
                    "returned the generic Citizen Access Portal shell. "
                    "The GIS link redirects to "
                    "https://russell.alabamagis.com/russell/ and displays "
                    "a welcome page. No accessible residential parcel "
                    "export/API, update cadence, or authorization for "
                    "daily/commercial automated access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Russell County tax-sale discovery and DOR transcript"
                )
                directory_url = (
                    "https://www.russellcountyrevenuecommissioner.com/#/"
                )
                note += (
                    " The DOR-linked Russell County Revenue Commissioner "
                    "site rendered only a Loading screen; no local "
                    "tax-sale date, parcel list, or auction platform could "
                    "be verified. The DOR Russell transcript "
                    "(WWW_TRANS_57.PDF), generated 2026-10-19, is a "
                    "10-page weekly state-held delinquent-land inventory, "
                    "not the local auction calendar, and DOR transcripts "
                    "lack physical addresses. No recurring local sale "
                    "feed or automated-use permission was established."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Russell County and municipal code-enforcement "
                    "discovery"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Russell"
                )
                source_url = directory_url
                note += (
                    " The DOR county-office entry and linked assessment/GIS "
                    "portals do not identify a code-enforcement provider or "
                    "property-level violation feed; the Revenue site "
                    "rendered only a Loading screen. No countywide or "
                    "municipal export/API, update cadence, or permission "
                    "for automated access was verified. Confirm the "
                    "responsible provider for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and statewide notice search"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " No Russell County sheriff-sale calendar or "
                    "county-authorized foreclosure notice feed was "
                    "verified. The Sheriffs Association page is a manual "
                    "office-discovery directory, not a sales feed. "
                    "Statewide Alabama Public Notice has participating-"
                    "newspaper coverage only, and its Terms prohibit "
                    "scraping, automated collection, and commercial "
                    "exploitation. No authorized daily source was "
                    "established."
                )
            elif category == "pre_foreclosure":
                directory_name = "Russell County Probate online portal"
                directory_url = (
                    "https://www.ingprobate.com/Russell_Probate/"
                )
                source_url = directory_url
                note += (
                    " The tested Russell Probate portal's legal "
                    "disclaimer identifies the Russell County Commission "
                    "and Russell County Judge of Probate, but no public "
                    "lis-pendens/default index or specific pre-foreclosure "
                    "search was documented. Its terms expressly prohibit "
                    "automated systems, bots, spiders, scrapers, offline "
                    "readers, data extraction, and automated interactions. "
                    "No bulk export/API or authorized daily "
                    "pre-foreclosure feed was verified."
                )
        if state == "AL" and county_name == "Shelby":
            if category == "assessor":
                directory_name = (
                    "Shelby County Citizen Access Portal and GIS"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Shelby"
                )
                source_url = "https://ptc.shelbyal.com/"
                note += (
                    " The Alabama DOR county-office directory links the "
                    "Shelby County website, mapping site, and Citizen "
                    "Access Portal. The County Property Tax Commissioner "
                    "and online-payment routes redirect to "
                    "https://ptc.shelbyal.com/, which returned only the "
                    "generic Citizen Access Portal shell. The County map "
                    "site is an interactive viewer; its HTML5 route "
                    "reported an unsupported-browser message. No "
                    "documented residential bulk export/API, update "
                    "cadence, or authorization for daily/commercial "
                    "automated access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Shelby County Property Tax Commissioner and DOR "
                    "transcript"
                )
                directory_url = (
                    "https://www.shelbyal.com/490/Property-Tax-Commissioner"
                )
                note += (
                    " The County Property Tax Commissioner page redirects "
                    "to the generic Citizen Access Portal shell; no local "
                    "tax-sale date, parcel list, or auction platform was "
                    "visible or verified. The DOR Shelby transcript "
                    "(WWW_TRANS_58.PDF), generated 2026-10-19, is an "
                    "11-page weekly state-held delinquent-land inventory, "
                    "not the local auction calendar, and DOR transcripts "
                    "lack physical addresses. No recurring local sale "
                    "feed or automated-use permission was established."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Shelby County Development Services permits and "
                    "inspections"
                )
                directory_url = (
                    "https://www.shelbyal.com/236/Permits-and-Inspections"
                )
                source_url = directory_url
                note += (
                    " The County Development Services page describes "
                    "building permits and inspections, and the County "
                    "publishes adopted construction codes, but these pages "
                    "do not expose a searchable property-level violation "
                    "or code-enforcement case feed. The pages do not "
                    "establish coverage of municipal jurisdictions. No "
                    "bulk export/API, update cadence, or automated-use "
                    "permission was verified; confirm the responsible "
                    "provider for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = "Shelby County Sheriff's Office services"
                directory_url = "https://www.shelbyso.com/101/Services"
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The official Sheriff's Office Services page did not "
                    "expose a civil-process foreclosure-sale calendar or "
                    "county-authorized notice feed. The Alabama Sheriffs "
                    "Association directory is a manual office-discovery "
                    "resource, not a sales feed. Statewide Alabama Public "
                    "Notice has participating-newspaper coverage only, "
                    "and its Terms prohibit scraping, automated "
                    "collection, and commercial exploitation. No "
                    "authorized Shelby daily foreclosure source was "
                    "verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Shelby County Probate ROAM public records search"
                directory_url = (
                    "https://probaterecords.shelbyal.com/shelby/search.do"
                )
                source_url = directory_url
                note += (
                    " The County Probate Office links the ROAM public "
                    "records search, whose disclaimer requires acceptance "
                    "of its Terms of Use. The disclaimer says the Records "
                    "Room is the complete official repository and warns "
                    "that some older mortgage cancellations are available "
                    "only in physical books, not as electronic images. No "
                    "specific lis-pendens/default feed, bulk export/API, "
                    "or explicit permission for automated access was "
                    "verified. The public search is a manual discovery "
                    "source, not an authorized daily pre-foreclosure feed."
                )
        if state == "AL" and county_name == "St. Clair":
            if category == "assessor":
                directory_name = (
                    "St. Clair County property-tax search and mapping"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#St.%20Clair"
                )
                source_url = (
                    "https://www.ingproperty.com/StClair_Revenue/property.aspx"
                )
                note += (
                    " The County's Search & Pay Property Tax page links "
                    "this public search, which offers tax-year filters "
                    "through 2027 and name, address, parcel, PPIN, account, "
                    "subdivision, and receipt search types. The DOR-linked "
                    "BPP portal is for business personal-property returns "
                    "and requires a BPP location number/access code. "
                    "IngProperty's legal disclaimer expressly prohibits "
                    "automated systems, bots, spiders, scrapers, offline "
                    "readers, data extraction, and automated interactions. "
                    "No bulk parcel export/API, update cadence, or "
                    "authorization for daily/commercial automation was "
                    "verified; treat the property search as manual-only."
                )
            elif category == "tax_sale":
                directory_name = (
                    "St. Clair County annual tax-lien auction and delinquent "
                    "list"
                )
                directory_url = (
                    "https://www.stclairco.com/418/Tax-Lien-Auction"
                )
                note += (
                    " The official County page says the online GovEase "
                    "tax-lien auction is held annually, typically during "
                    "the first week of May, and links a Current Delinquent "
                    "List at "
                    "https://www.ingproperty.com/StClair_Revenue/"
                    "Delinquent.aspx. Its 2026 flyer scheduled the sale "
                    "for Tuesday, May 5, 2026 at 9:00 AM; that date has "
                    "passed, and no 2027 date was posted. IngProperty's "
                    "terms expressly prohibit automated systems, bots, "
                    "scraping, and data extraction, so the delinquent list "
                    "is manual-only absent written permission. The DOR "
                    "St. Clair transcript is weekly state-held inventory, "
                    "not the County auction calendar, and lacks physical "
                    "addresses. No authorized daily sale feed was "
                    "verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "St. Clair County code-enforcement source discovery"
                )
                directory_url = "https://www.stclairco.com/SiteMap"
                source_url = directory_url
                note += (
                    " The reviewed County sitemap and DOR county-office "
                    "entry did not identify a code-enforcement provider "
                    "or property-level violation feed. The County's "
                    "mapping link is an ArcGIS organization page, not a "
                    "documented enforcement data service. No countywide "
                    "or municipal export/API, update cadence, or "
                    "automated-use permission was verified; confirm the "
                    "provider for each property's jurisdiction."
                )
            elif category == "foreclosure":
                directory_name = (
                    "St. Clair County Sheriff's Civil Process and statewide "
                    "notices"
                )
                directory_url = (
                    "https://www.stclairsheriff.org/civil-process"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The Sheriff's Civil Process page confirms the Civil "
                    "Division conducts sheriff's sales but publishes no "
                    "searchable sale calendar/list or county-authorized "
                    "feed. The Sheriff's public-records request process "
                    "requires Alabama residency and a specific existing "
                    "record, so it is not a recurring feed. Statewide "
                    "Alabama Public Notice has participating-newspaper "
                    "coverage only, and its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. "
                    "No authorized daily foreclosure source was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "St. Clair County Probate Office"
                directory_url = (
                    "https://www.stclairco.com/232/Probate-Office"
                )
                source_url = directory_url
                note += (
                    " The County Probate Office page provides office "
                    "information but no public land-record or "
                    "lis-pendens/default search. The tested "
                    "StClair_Probate InG route returned HTTP 404; the "
                    "County's recording-related page describes plat "
                    "filing, not a searchable document index. No public "
                    "pre-foreclosure source, bulk export/API, or "
                    "authorized automated access was verified."
                )
        if state == "AL" and county_name == "Sumter":
            if category == "assessor":
                directory_name = (
                    "Sumter County Tax Assessor, Citizen Access Portal, and GIS"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/#Sumter"
                )
                source_url = (
                    "https://sumter.capturecama.com/CAPortal_MainPage.aspx"
                )
                note += (
                    " The Alabama DOR county-office listing links this "
                    "Citizen Access Portal and the Sumter Public GIS. The "
                    "portal rendered only its 'Citizen Access Portal' title; "
                    "the GIS redirected to a welcome page. The County Tax "
                    "Assessor page provides office information but no "
                    "additional parcel-search link. No working parcel "
                    "results, bulk export/API, update cadence, or "
                    "authorization for daily/commercial automation was "
                    "verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Sumter County Tax Collector and Alabama DOR delinquent "
                    "land inventory"
                )
                directory_url = "https://sumtercountyal.com/tax-collector/"
                note += (
                    " The County Tax Collector page provides office contact "
                    "information but no current tax-sale date, list, or "
                    "auction platform. The linked DOR Sumter transcript "
                    "(WWW_TRANS_60.PDF), generated 2026-10-19, is a "
                    "one-page weekly state-held delinquent-land inventory, "
                    "not the County auction calendar, and lacks physical "
                    "addresses. No recurring local sale feed or "
                    "authorization for automated use was verified; contact "
                    "the County for current sale details."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Sumter County code-enforcement source discovery"
                )
                directory_url = "https://sumtercountyal.com/"
                source_url = directory_url
                note += (
                    " The official County site navigation and reviewed "
                    "department pages did not identify a code-enforcement "
                    "provider or property-level violation feed. Countywide "
                    "and municipal exports/APIs, update cadence, and "
                    "automated-use permission were not verified; confirm "
                    "the responsible provider for each property's "
                    "municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Sumter County Sheriff's Office and statewide notices"
                )
                directory_url = "https://sumtercountyal.com/sheriffjail/"
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The official Sheriff/Jail page identifies the "
                    "Sheriff but provides no civil-process sale calendar, "
                    "foreclosure list, or feed. Statewide Alabama Public "
                    "Notice has participating-newspaper coverage only; its "
                    "Terms prohibit scraping, automated collection, and "
                    "commercial exploitation. No authorized daily "
                    "foreclosure source was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Sumter County Judge of Probate"
                directory_url = (
                    "https://sumtercountyal.com/judge-of-probate/"
                )
                source_url = directory_url
                note += (
                    " The official Judge of Probate page provides office "
                    "contact information but no electronic land-record "
                    "search, lis-pendens/default index, or pre-foreclosure "
                    "feed. No public bulk export/API or permission for "
                    "automated access was verified; treat this as manual "
                    "office discovery only."
                )
        if state == "AL" and county_name == "Talladega":
            if category == "assessor":
                directory_name = (
                    "Talladega County Appraisal and Mapping Department"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Talladega"
                )
                source_url = (
                    "https://www.talladegacountyal.org/departments/"
                    "appraisal/index.php"
                )
                note += (
                    " The DOR county-office entry links the County website "
                    "and Revenue Commissioner page. The County Appraisal "
                    "and Mapping page confirms responsibility for "
                    "residential/commercial valuation and mapping but "
                    "provides no public parcel-search link or downloadable "
                    "dataset. A tested candidate legacy GIS route at "
                    "https://www.alabamagis.com/Talladega returned HTTP 404. "
                    "No working parcel export/API, update cadence, or "
                    "authorization for daily/commercial automation was "
                    "verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Talladega County Revenue Commissioner and Alabama DOR "
                    "delinquent-land inventory"
                )
                directory_url = (
                    "https://www.talladegacountyal.org/government/"
                    "revenue_commission.php"
                )
                note += (
                    " The official Revenue Commissioner page describes "
                    "assessment and tax collection duties but publishes no "
                    "current tax-sale date, list, or auction platform. The "
                    "DOR Talladega transcript (WWW_TRANS_61.PDF), generated "
                    "2026-10-19, is weekly state-held delinquent-land "
                    "inventory, not the County auction calendar, and lacks "
                    "physical addresses. No recurring local sale feed or "
                    "authorization for automated use was verified; contact "
                    "the Revenue Commissioner's Office for current sale "
                    "details."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Talladega County Permits, Building, and Development"
                )
                directory_url = (
                    "https://www.talladegacountyal.org/departments/"
                    "highway/permits_and_zoning.php"
                )
                source_url = directory_url
                note += (
                    " The County's Permits, Building, and Development page "
                    "does not expose a searchable property-level code "
                    "violation feed or enforcement case data. No countywide "
                    "or municipal provider, export/API, update cadence, or "
                    "automated-use permission was verified; confirm the "
                    "responsible provider for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = "Talladega County Sheriff's Office"
                directory_url = (
                    "https://www.talladegacountyal.org/government/sheriff.php"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The County Sheriff page is an office biography and "
                    "publishes no civil-process sale calendar, foreclosure "
                    "list, or feed. Statewide Alabama Public Notice has "
                    "participating-newspaper coverage only; its Terms "
                    "prohibit scraping, automated collection, and "
                    "commercial exploitation. No authorized daily "
                    "foreclosure source was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Talladega County Probate Office"
                directory_url = (
                    "https://www.talladegacountyal.org/departments/"
                    "probate_office/index.php"
                )
                source_url = directory_url
                note += (
                    " The official Probate Office page confirms its "
                    "Recording Division records deeds, mortgages, "
                    "judgments, and liens, but provides no public online "
                    "record search, lis-pendens/default index, or "
                    "pre-foreclosure feed. No bulk export/API or permission "
                    "for automated access was verified; use as manual "
                    "office discovery only."
                )
        if state == "AL" and county_name == "Tallapoosa":
            if category == "assessor":
                directory_name = (
                    "Tallapoosa County Revenue Commission property-tax portal"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Tallapoosa"
                )
                source_url = (
                    "https://altags.com/Tallapoosa_Revenue/default.aspx"
                )
                note += (
                    " The DOR listing links the County tax website, a Public "
                    "GIS page, and an Altags appraisal/assessment route. The "
                    "GIS redirects to a welcome page. The County's property "
                    "tax page describes payments and assessments and says "
                    "county tax records may be researched online, but no "
                    "residential parcel export/API or update cadence was "
                    "verified. The public Altags application expressly "
                    "prohibits automated systems, bots, spiders, scrapers, "
                    "offline readers, data extraction, automated logins, "
                    "and automated interactions. The DOR-linked BPP route "
                    "requires a BPP location number/access code and is not "
                    "a residential parcel search. No authorization for "
                    "daily/commercial automation was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Tallapoosa County annual online tax-lien auction"
                )
                directory_url = "https://tallaco.com/resources/taxes/"
                note += (
                    " The County Taxes FAQ, last modified 2024-12-05, says "
                    "the tax-lien auction is online-only and conducted once "
                    "per year; participants are responsible for their own "
                    "research. Its registration/bidding link is the generic "
                    "GovEase homepage, not a Tallapoosa auction listing. "
                    "The linked delinquent-taxpayer page "
                    "(https://www.tallapoosapropertytax.com/Default.asp?"
                    "ID=308&pg=Home) redirects to the general Revenue "
                    "Commission homepage and exposed no current delinquent "
                    "list or sale date. The DOR Tallapoosa transcript "
                    "(WWW_TRANS_62.PDF), generated 2026-10-19, is a "
                    "one-page weekly state-held delinquent-land inventory, "
                    "not the County auction calendar, and lacks physical "
                    "addresses. No authorized daily sale feed was verified."
                )
            elif category == "code_enforcement":
                directory_name = "Tallapoosa County Building Department"
                directory_url = "https://tallaco.com/departments/building/"
                source_url = directory_url
                note += (
                    " The County Building Department issues residential "
                    "and commercial permits and enforces adopted building, "
                    "plumbing, electrical, and mechanical codes through "
                    "inspections. Its public page offers permit packets "
                    "and a worksheet but no searchable property-level "
                    "violation/inspection case data or open enforcement "
                    "feed. No export/API, update cadence, or permission "
                    "for daily/commercial automation was verified; "
                    "municipal code-enforcement providers remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Tallapoosa County Sheriff's Office and statewide notices"
                )
                directory_url = "https://tallaco.com/departments/sheriff/"
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The County Sheriff's public department page provides "
                    "general office and public-safety information but no "
                    "civil-process sale calendar, searchable foreclosure "
                    "list, or sale feed. Statewide Alabama Public Notice "
                    "has participating-newspaper coverage only, and its "
                    "Terms prohibit scraping, automated collection, and "
                    "commercial exploitation. No authorized daily "
                    "foreclosure source was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Tallapoosa County Probate Office real-estate records"
                )
                directory_url = (
                    "https://tallaco.com/departments/probate-office/"
                    "real-estate/"
                )
                source_url = (
                    "https://tallapoosaprobate.countygovservices.com/"
                )
                note += (
                    " The County's Real Estate page says the index includes "
                    "deeds, mortgages, judgments, and liens, with computer "
                    "indexes beginning in October 1985; earlier records are "
                    "in books/microfilm. The County Probate Office's "
                    "Real Estate link leads to this CountyGovServices "
                    "portal, which redirects unauthenticated visitors to "
                    "sign-in. No anonymous public lis-pendens/default index, "
                    "bulk export/API, portal terms permitting automation, "
                    "or authorized daily access was verified; treat it as "
                    "manual/authenticated office discovery only."
                )
        if state == "AL" and county_name == "Tuscaloosa":
            if category == "assessor":
                directory_name = "Tuscaloosa County Tax Assessor"
                directory_url = "https://www.tuscco.com/tax-assessor/"
                source_url = (
                    "https://altags.com/Tuscaloosa_Revenue/default.aspx"
                )
                note += (
                    " The Alabama DOR directory links the County Tax "
                    "Assessor page, Public GIS, and this AlTags assessment "
                    "portal. The GIS route at "
                    "https://www.alabamagis.com/Tuscaloosa redirects to a "
                    "welcome page. The AlTags legal disclaimer prohibits "
                    "automated systems, bots, spiders, scrapers, offline "
                    "readers, data extraction, automated logins, and "
                    "interactions. No authorized residential-parcel "
                    "export/API or daily/commercial access was verified; "
                    "treat assessment lookup as manual-only."
                )
            elif category == "tax_sale":
                directory_name = "Tuscaloosa County Tax Lien Sale"
                directory_url = (
                    "https://www.tuscco.com/tax-collector/tax-lien-sale/"
                )
                source_url = (
                    "https://www.tuscco.com/wp-content/uploads/2026/06/"
                    "Copy-of-List-for-IT-2025-Tax-Year-Prop-did-not-sell-"
                    "002.pdf"
                )
                note += (
                    " The County Tax Lien Sale page links to generic "
                    "GovEase and still says properties would be published "
                    "in April 2022; no current sale date or county-specific "
                    "auction listing was found. The Tax Collector site "
                    "links a one-page 2025 tax-year 'parcels for sale "
                    "after tax sale' PDF, created June 18, 2026; it is a "
                    "post-sale unsold-property list, not an upcoming "
                    "auction calendar. The DOR Tuscaloosa transcript "
                    "(WWW_TRANS_63.PDF), generated 2026-10-19, is a "
                    "one-page weekly state-held delinquent-land inventory, "
                    "not the local auction calendar, and lacks physical "
                    "addresses. No recurring local feed, API, update "
                    "cadence, or permission for daily/commercial "
                    "automation was verified; use manual review only."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Tuscaloosa County Public Works Environmental Services"
                )
                directory_url = (
                    "https://www.tuscco.com/public-works/environmental/"
                )
                source_url = directory_url
                note += (
                    " The County's published Environmental and "
                    "Subdivision Regulation pages describe stormwater, "
                    "environmental planning, and development requirements "
                    "but expose no property-level building/code violation "
                    "or enforcement-case feed. No countywide or municipal "
                    "provider, export/API, update cadence, or permission "
                    "for automated use was verified; confirm the code "
                    "authority for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Tuscaloosa County Sheriff's Office and Alabama notices"
                )
                directory_url = (
                    "https://www.tuscco.com/county-officials/sheriff/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The County Sheriff page links to the Tuscaloosa "
                    "Sheriff's Office site, whose current sitemap exposes "
                    "no civil-process sale calendar, foreclosure list, or "
                    "feed. Alabama Public Notice covers participating "
                    "newspapers only; its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. "
                    "No authorized county foreclosure notice feed or "
                    "daily source was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Tuscaloosa County Probate Records and Recordings"
                )
                directory_url = (
                    "https://www.tuscco.com/probate/records-and-recordings/"
                )
                source_url = "https://probate.tuscco.com/ProbateWeb/"
                note += (
                    " The County Records and Recordings page's Search "
                    "Probate Records button routes to ProbateWeb and a "
                    "Microsoft B2C sign-up/sign-in flow; anonymous search "
                    "was not available. No public lis-pendens/default "
                    "index, bulk export/API, automation permission, or "
                    "authorized daily pre-foreclosure feed was verified; "
                    "use manual/authenticated research only."
                )
        if state == "AL" and county_name == "Walker":
            if category == "assessor":
                directory_name = "Walker County Revenue Commissioner property search"
                directory_url = "https://www.walkercountyrevenue.com/"
                source_url = "https://www.walkercountyrevenue.com/#/property"
                note += (
                    " The County Revenue Commissioner site offers an "
                    "online property-tax search/view/pay service, and the "
                    "County Commission sitemap links directly to this "
                    "property-search route. The County Maps site and DOR "
                    "Public GIS route both resolve to an Alabamagis welcome "
                    "page. The property search is an interactive lookup; "
                    "no parcel bulk export/API, update cadence, or "
                    "permission for daily/commercial automation was "
                    "verified."
                )
            elif category == "tax_sale":
                directory_name = "Walker County 2026 tax-lien auction"
                directory_url = (
                    "https://www.walkercountyrevenue.com/tax-sale/"
                )
                source_url = directory_url
                note += (
                    " The County Revenue Commissioner states that the "
                    "2026 tax-lien auction will be held May 3, 2027 at "
                    "8:30 a.m. on GovEase; the delinquent-property list is "
                    "scheduled for April 2, 2027, at least 30 days before "
                    "the auction. The GovEase link is generic and the "
                    "2027 parcel list was not yet posted. The DOR Walker "
                    "transcript (WWW_TRANS_64.PDF), generated 2026-10-19, "
                    "is a one-page weekly state-held delinquent-land "
                    "inventory, not the County auction calendar, and "
                    "lacks physical addresses. No machine-readable list "
                    "feed, API, update cadence, or permission for "
                    "daily/commercial automation was verified."
                )
            elif category == "code_enforcement":
                directory_name = "Walker County Engineering Department"
                directory_url = (
                    "https://www.walkercountyal.us/administrator/engineering/"
                )
                source_url = directory_url
                note += (
                    " County Engineering states that the County has no "
                    "general building regulations or permit requirement "
                    "outside municipalities, with a limited zoning "
                    "exception near the County airport; environmental "
                    "matters are under the County Health Department. No "
                    "countywide property-level code-enforcement feed was "
                    "identified. Municipal and environmental enforcement "
                    "providers, exports/APIs, update cadence, and "
                    "automation permission remain unverified."
                )
            elif category == "foreclosure":
                directory_name = "Walker County Sheriff's Office"
                directory_url = "https://walkercountysheriff.com/index.html"
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The County Commission links to this Sheriff's "
                    "Office site; its sitemap, last modified in 2017, "
                    "lists general services but no civil-process sale "
                    "calendar or foreclosure list. Statewide Alabama "
                    "Public Notice covers participating newspapers only; "
                    "its Terms prohibit scraping, automated collection, "
                    "and commercial exploitation. No current, authorized "
                    "Walker foreclosure feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Walker County Probate recorded documents"
                directory_url = "https://www.walkercountyprobate.com/records/"
                source_url = "https://ingprobate.com/Walker_Probate/"
                note += (
                    " The County Probate Records page links to the InG "
                    "portal to look up recorded Walker County documents. "
                    "Its legal disclaimer expressly prohibits automated "
                    "systems, bots, spiders, scrapers, offline readers, "
                    "data extraction, automated account creation/logins, "
                    "and interactions. No lis-pendens/default index, "
                    "bulk export/API, or authorized pre-foreclosure feed "
                    "was verified; use the portal for manual research only."
                )
        if state == "AL" and county_name == "Washington":
            if category == "assessor":
                directory_name = (
                    "Washington County Revenue Commissioner and Public GIS"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Washington"
                )
                source_url = "https://www.alabamagis.com/Washington/"
                note += (
                    " The Alabama DOR county-office directory lists the "
                    "Revenue Commissioner and links the Public GIS route, "
                    "but no County Revenue website or residential "
                    "assessment search link. GIS resolves to a welcome page; the "
                    "tested candidate AlTags route "
                    "https://altags.com/Washington_Revenue/default.aspx "
                    "returned HTTP 404. No working parcel results, bulk "
                    "export/API, update cadence, or permission for "
                    "daily/commercial automation was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Washington County Revenue Commissioner and DOR transcript"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Washington"
                )
                source_url = (
                    "https://www.revenue.alabama.gov/wp-content/uploads/"
                    "property-tax-transcripts/WWW_TRANS_65.PDF"
                )
                note += (
                    " The DOR county-office entry links no County "
                    "Revenue/property-tax website, current auction date, "
                    "delinquent sale list, or auction platform. The "
                    "Washington transcript (WWW_TRANS_65.PDF), generated "
                    "2026-10-19, is a one-page weekly state-held "
                    "delinquent-land inventory, not the County auction "
                    "calendar, and lacks physical addresses. No recurring "
                    "local sale feed, list cadence, API, or permission for "
                    "daily/commercial automation was verified; contact "
                    "the Revenue Commissioner's Office for sale details."
                )
            elif category == "code_enforcement":
                directory_name = "Washington County code-enforcement discovery"
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Washington"
                )
                source_url = directory_url
                note += (
                    " The reviewed State and County office pages identify "
                    "no countywide property-level code-enforcement "
                    "provider, violation search, or case feed. No "
                    "municipal provider, export/API, update cadence, or "
                    "permission for automated access was verified; check "
                    "the authority for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Washington County Sheriff's Office and Alabama notices"
                )
                directory_url = "https://www.washingtoncountysheriff.org/"
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " The Sheriff's current website and sitemap expose "
                    "public-safety news but no civil-process sale calendar, "
                    "foreclosure list, or feed. Alabama Public Notice "
                    "covers participating newspapers only; its Terms "
                    "prohibit scraping, automated collection, and "
                    "commercial exploitation. No authorized county "
                    "foreclosure notice feed or daily source was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Washington County Probate Office records"
                directory_url = "https://washprobate.com/"
                source_url = (
                    "https://ingprobate.com/washington_probate/default.aspx"
                )
                note += (
                    " The County Probate Office page links to an online "
                    "records search through this InG portal. Its legal "
                    "disclaimer prohibits automated systems, bots, "
                    "spiders, scrapers, offline readers, data extraction, "
                    "automated logins, and interactions. No dedicated "
                    "lis-pendens/default feed, bulk export/API, or "
                    "authorized daily access was verified; use manual "
                    "records research only."
                )
        if state == "AL" and county_name == "Wilcox":
            if category == "assessor":
                directory_name = (
                    "Wilcox County Citizen Access Portal and Public GIS"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Wilcox"
                )
                source_url = (
                    "https://wilcox.capturecama.com/CAPortal_MainPage.aspx"
                )
                note += (
                    " The DOR directory links this Citizen Access Portal "
                    "for appraisal/assessment records and the County's "
                    "Public GIS route. The portal rendered only its "
                    "'Citizen Access Portal' title, while GIS resolves to "
                    "a welcome page. No working parcel results, bulk "
                    "export/API, update cadence, or permission for "
                    "daily/commercial automation was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Wilcox County Revenue Commissioner and DOR transcript"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Wilcox"
                )
                source_url = (
                    "https://www.revenue.alabama.gov/wp-content/uploads/"
                    "property-tax-transcripts/WWW_TRANS_66.PDF"
                )
                note += (
                    " The DOR entry identifies the County Tax Assessor "
                    "and Tax Collector and links the assessment portal, "
                    "but publishes no County sale date, delinquent parcel "
                    "list, or auction platform. The Wilcox transcript "
                    "(WWW_TRANS_66.PDF), generated 2026-10-19, is a "
                    "one-page weekly state-held delinquent-land inventory, "
                    "not the County auction calendar, and lacks physical "
                    "addresses. No recurring local sale feed, list "
                    "cadence, API, or permission for daily/commercial "
                    "automation was verified."
                )
            elif category == "code_enforcement":
                directory_name = "Wilcox County code-enforcement discovery"
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Wilcox"
                )
                source_url = directory_url
                note += (
                    " The reviewed State and County office/assessment "
                    "pages identify no countywide property-level "
                    "code-enforcement provider, violation search, or case "
                    "feed. No municipal provider, export/API, update "
                    "cadence, or permission for automated access was "
                    "verified; confirm the authority for each property's "
                    "municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and statewide notices"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " No Wilcox County Sheriff's sale calendar, "
                    "foreclosure list, or county-authorized notice feed "
                    "was verified. The Alabama Sheriffs Association "
                    "directory is manual office discovery, not a sales "
                    "feed. Alabama Public Notice covers participating "
                    "newspapers only; its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. "
                    "No authorized daily foreclosure source was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Wilcox County Probate records portal"
                directory_url = "https://ingprobate.com/Wilcox_Probate/"
                source_url = directory_url
                note += (
                    " The portal's legal disclaimer identifies the "
                    "Wilcox County Commission and Judge of Probate, but "
                    "expressly prohibits automated systems, bots, "
                    "spiders, scrapers, offline readers, data extraction, "
                    "automated logins, and interactions. No dedicated "
                    "lis-pendens/default feed, bulk export/API, or "
                    "authorized pre-foreclosure automation was verified; "
                    "use manual records research only."
                )
        if state == "AR" and county_name == "Arkansas":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Arkansas County"
                directory_url = "https://www.arcounties.org/counties/arkansas/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Arkansas&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. It is an interactive third-party portal, not "
                    "a documented daily feed. The vendor's terms describe "
                    "parcel data as assessor working papers and restrict "
                    "copying/reproducing proprietary material without "
                    "express written consent. No feed/API, refresh "
                    "cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office says it processes delinquent "
                    "property taxes certified to the State, conducts "
                    "public auctions, and links its public auction "
                    "catalog here. This is a state-held tax-sale source, "
                    "not an Arkansas County auction calendar. The "
                    "retrieval did not expose an Arkansas County-specific "
                    "current sale date/list or a machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Arkansas County"
                directory_url = "https://www.arcounties.org/counties/arkansas/"
                source_url = directory_url
                note += (
                    " The County profile lists County offices but no "
                    "code-enforcement agency or property-level case "
                    "portal. Enforcement may be municipal; no countywide "
                    "violation feed was identified. Municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Arkansas County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/arkansas/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists County Sheriff "
                    "contacts but no sale calendar or foreclosure feed. "
                    "Arkansas Public Notices offers newspaper foreclosure "
                    "notices searchable by county, but is not the official "
                    "publication, does not include notices from every "
                    "newspaper, and its Terms limit use to personal, "
                    "non-commercial purposes and prohibit copying or "
                    "replication. Written permission is required before "
                    "commercial ingestion; no County-authorized daily "
                    "sale feed was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Arkansas County Circuit Clerk and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/arkansas/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The County profile lists a Circuit Clerk contact. "
                    "The official statewide Case Search page returned "
                    "general navigation tips in this check; no "
                    "Arkansas County-specific default/lis-pendens feed, "
                    "bulk export/API, update cadence, or permission for "
                    "daily automated access was verified. Use the Clerk "
                    "for manual records guidance; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Ashley":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Ashley County"
                directory_url = "https://www.arcounties.org/counties/ashley/"
                source_url = directory_url
                note += (
                    " The County profile lists Assessor and Collector "
                    "contacts. ARCountyData's current county selector "
                    "lists 35 counties and excludes Ashley; the tested "
                    "Ashley county route redirected to the generic "
                    "homepage. No other county-specific parcel search, "
                    "export/API, update cadence, or permission for daily "
                    "automation was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose an Ashley County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Ashley County"
                directory_url = "https://www.arcounties.org/counties/ashley/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Ashley County office contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/ashley/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " No Ashley County Sheriff's sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper foreclosure "
                    "notices searchable by county, but is not the official "
                    "publication, does not include notices from every "
                    "newspaper, and its Terms limit use to personal, "
                    "non-commercial purposes and prohibit copying or "
                    "replication. Written permission is required before "
                    "commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Ashley County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/ashley/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no "
                    "Ashley County-specific default/lis-pendens feed, "
                    "bulk export/API, update cadence, or permission for "
                    "daily automated access was verified. County-level "
                    "filing coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Baxter":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Baxter County"
                directory_url = "https://www.arcounties.org/counties/baxter/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Baxter&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Baxter County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Baxter County"
                directory_url = "https://www.arcounties.org/counties/baxter/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Baxter County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/baxter/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Baxter County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/baxter/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Baxter "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Benton":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Benton County"
                directory_url = "https://www.arcounties.org/counties/benton/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Benton&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Benton County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Benton County"
                directory_url = "https://www.arcounties.org/counties/benton/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Benton County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/benton/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Benton County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/benton/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Benton "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Boone":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Boone County"
                directory_url = "https://www.arcounties.org/counties/boone/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Boone&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Boone County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Boone County"
                directory_url = "https://www.arcounties.org/counties/boone/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Boone County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/boone/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Boone County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/boone/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Boone "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Bradley":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Bradley County"
                directory_url = "https://www.arcounties.org/counties/bradley/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Bradley&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Bradley County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Bradley County"
                directory_url = "https://www.arcounties.org/counties/bradley/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Bradley County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/bradley/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Bradley County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/bradley/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Bradley "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Calhoun":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Calhoun County"
                directory_url = "https://www.arcounties.org/counties/calhoun/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Calhoun&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Calhoun County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Calhoun County"
                directory_url = "https://www.arcounties.org/counties/calhoun/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Calhoun County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/calhoun/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Calhoun County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/calhoun/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Calhoun "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Carroll":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Carroll County"
                directory_url = "https://www.arcounties.org/counties/carroll/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Carroll&s=R"
                )
                note += (
                    " The county-specific ARCountyData page shows a "
                    "Paid Users Login button and no free public-search "
                    "interface. It reports 27,095 parcels and Collector "
                    "Data last updated 2024-12-13; the vendor says "
                    "assessor data is updated at least monthly, but no "
                    "assessor-data date is displayed. Its linked County "
                    "website did not resolve in this check. The vendor's "
                    "terms restrict copying/reproducing proprietary "
                    "material without express written consent. No "
                    "public export/API, current assessor data date, or "
                    "permission for commercial daily ingestion was "
                    "verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Carroll County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Carroll County"
                directory_url = "https://www.arcounties.org/counties/carroll/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Carroll County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/carroll/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Carroll County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/carroll/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Carroll "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Chicot":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Chicot County"
                directory_url = "https://www.arcounties.org/counties/chicot/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Chicot&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Chicot County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Chicot County"
                directory_url = "https://www.arcounties.org/counties/chicot/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Chicot County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/chicot/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Chicot County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/chicot/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Chicot "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Clark":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Clark County"
                directory_url = "https://www.arcounties.org/counties/clark/"
                source_url = directory_url
                note += (
                    " The County profile lists Assessor and Collector "
                    "contacts. The county-specific ARCountyData page at "
                    "https://www.arcountydata.com/county.asp?county=Clark&s=R "
                    "is labeled Search Tax Records / Receipts and says "
                    "the Collector sponsors a free public search; it is "
                    "not an Assessor valuation/parcel search. No separate "
                    "county assessor search, export/API, update cadence, "
                    "or permission for daily automated access was "
                    "verified. The Collector search is interactive and "
                    "does not establish an authorized daily feed."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Clark County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Clark County"
                directory_url = "https://www.arcounties.org/counties/clark/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Clark County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/clark/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Clark County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/clark/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Clark "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Clay":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Clay County"
                directory_url = "https://www.arcounties.org/counties/clay/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Clay&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Clay County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Clay County"
                directory_url = "https://www.arcounties.org/counties/clay/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Clay County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/clay/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Clay County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/clay/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Clay "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Cleburne":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Cleburne County"
                directory_url = "https://www.arcounties.org/counties/cleburne/"
                source_url = "https://www.cleburnecountyar.com/"
                note += (
                    " The Association profile links this County website, "
                    "but the tested site returned only a Wix shell with "
                    "no assessor search or data links visible. The "
                    "county-specific ARCountyData page is labeled Search "
                    "Tax Records / Receipts and identifies a free "
                    "Collector-sponsored search, not assessor valuation "
                    "data. No county-specific assessor search, export/"
                    "API, update cadence, or permission for daily "
                    "automated access was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Cleburne County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Cleburne County official website"
                directory_url = "https://www.arcounties.org/counties/cleburne/"
                source_url = "https://www.cleburnecountyar.com/"
                note += (
                    " The tested County website returned a Wix shell "
                    "without code-enforcement links or property-level "
                    "records. No countywide violation feed was "
                    "identified; municipal providers, export/API, update "
                    "cadence, and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Cleburne County offices and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/cleburne/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The County website retrieval exposed no Sheriff "
                    "sale calendar or foreclosure list. Arkansas Public "
                    "Notices offers newspaper foreclosure notices "
                    "searchable by county, but is not the official "
                    "publication, does not include notices from every "
                    "newspaper, and its Terms limit use to personal, "
                    "non-commercial purposes and prohibit copying or "
                    "replication. Written permission is required before "
                    "commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Cleburne County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/cleburne/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Cleburne "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Cleveland":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Cleveland County"
                directory_url = "https://www.arcounties.org/counties/cleveland/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Cleveland&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Cleveland County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Cleveland County"
                directory_url = "https://www.arcounties.org/counties/cleveland/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Cleveland County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/cleveland/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Cleveland County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/cleveland/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Cleveland "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Columbia":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Columbia County"
                directory_url = "https://www.arcounties.org/counties/columbia/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Columbia&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Columbia County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Columbia County"
                directory_url = "https://www.arcounties.org/counties/columbia/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Columbia County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/columbia/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Columbia County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/columbia/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Columbia "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Conway":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Conway County"
                directory_url = "https://www.arcounties.org/counties/conway/"
                source_url = directory_url
                note += (
                    " The Association profile is a County office "
                    "directory. ARCountyData's current selector lists "
                    "35 counties and excludes Conway; the tested "
                    "Conway-specific route redirected to the generic "
                    "homepage. No Conway assessor parcel search, "
                    "export/API, update cadence, or permission for daily "
                    "automation was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Conway County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Conway County"
                directory_url = "https://www.arcounties.org/counties/conway/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Conway County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/conway/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Conway County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/conway/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Conway "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Craighead":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Craighead County"
                directory_url = "https://www.arcounties.org/counties/craighead/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Craighead&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Craighead County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Craighead County"
                directory_url = "https://www.arcounties.org/counties/craighead/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Craighead County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/craighead/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Craighead County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/craighead/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Craighead "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Crittenden":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Crittenden County"
                directory_url = "https://www.arcounties.org/counties/crittenden/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Crittenden&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Crittenden County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Crittenden County"
                directory_url = "https://www.arcounties.org/counties/crittenden/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Crittenden County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/crittenden/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Crittenden County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/crittenden/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Crittenden "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Sebastian":
            if category == "assessor":
                directory_name = (
                    "Sebastian County Assessor and ARCountyData records"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/sebastian/"
                )
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Sebastian&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public real-estate search. "
                    "It is an interactive third-party portal, not a "
                    "documented daily feed; no machine-readable "
                    "feed/API, update cadence, or authorization for "
                    "daily commercial extraction was identified. "
                    "ARCountyData's Terms reserve rights over "
                    "proprietary website material and require express "
                    "written consent for its reproduction; confirm "
                    "permission before automated reuse."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Sebastian County-specific "
                    "current State Land Office sale list or "
                    "machine-readable feed; update cadence and "
                    "permission for daily/commercial automation were "
                    "not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Sebastian County official departments"
                directory_url = "https://www.sebastiancountyar.gov/"
                source_url = "https://www.sebastiancountyar.gov/"
                note += (
                    " The official County site provides departments and "
                    "calendar information but no property-level "
                    "countywide code-enforcement service/feed was "
                    "identified. Municipal providers, export/API, "
                    "update cadence, and permission for automated "
                    "access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Sebastian County Commissioner's Sale calendar"
                )
                directory_url = "https://www.sebastiancountyar.gov/"
                source_url = (
                    "https://www.sebastiancountyar.gov/Home/County-Calendar"
                )
                note += (
                    " The official County calendar currently lists "
                    "Commissioner's Sale events with court case numbers, "
                    "dates, and linked legal descriptions/common "
                    "addresses. A sale-title/calendar entry alone does "
                    "not establish that each event is a mortgage "
                    "foreclosure or tax sale; verify each linked notice. "
                    "No bulk API/export, daily update cadence, or "
                    "permission for automated commercial extraction was "
                    "identified. Arkansas Public Notices is an "
                    "additional newspaper source, but its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication; written "
                    "permission is required for commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Sebastian County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/sebastian/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no "
                    "Sebastian County-specific default/lis-pendens "
                    "feed, bulk export/API, update cadence, or "
                    "permission for daily automated access was "
                    "verified. County-level filing coverage remains "
                    "unconfirmed; Commissioner's Sale events are not "
                    "pre-foreclosure records."
                )
        if state == "MO" and county_name == "Boone":
            if category == "assessor":
                directory_name = "Boone County Assessor real-property search"
                directory_url = "https://www.boonemo.gov/assessor/"
                source_url = (
                    "https://report.boonemo.gov/mrcjava/servlet/"
                    "AS00_MP.I00240s"
                )
                note += (
                    " The official Assessor site links to this live "
                    "real-property search and a County Parcel Viewer. "
                    "The County's Website Terms limit Site materials to "
                    "personal, informational, non-commercial use and "
                    "require prior written consent for copying, "
                    "reproduction, or distribution. No public bulk "
                    "export/API or written authorization for daily "
                    "commercial extraction was identified. The Assessor "
                    "explains that market value, assessment class, and "
                    "local tax rates determine tax amounts; final rates "
                    "are not set until October 31."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Boone County Collector and Missouri Public Notices"
                )
                directory_url = "https://www.boonemo.gov/collector/"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The official Collector page says primary tax "
                    "records are held for public use in the Collector's "
                    "office but does not provide a delinquent-tax-sale "
                    "calendar or parcel list. The statewide Missouri "
                    "Press Association search offers a Tax Sale "
                    "category, but no current Boone-specific sale list, "
                    "date, or complete feed was verified. Its terms "
                    "limit viewing to personal, non-commercial use and "
                    "prohibit scraping and automation; use manual "
                    "research only unless written authorization is "
                    "obtained."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Boone County Resource Management Planning Division"
                )
                directory_url = (
                    "https://www.boonemo.gov/resource-management/"
                    "planning-zoning/"
                )
                source_url = directory_url
                note += (
                    " The Planning Division states that it investigates "
                    "zoning complaints in unincorporated Boone County. "
                    "The Building Inspections page links to a building-"
                    "permit search, but that endpoint redirected to a "
                    "login and is not a public violation list. No "
                    "property-level complaint/violation feed, bulk "
                    "export/API, update cadence, or daily-access "
                    "authorization was verified. Columbia and other "
                    "municipal jurisdictions require separate source "
                    "checks."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Boone County Sheriff's Office and Missouri Public Notices"
                )
                directory_url = "https://www.boonemo.gov/sheriff/"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The official Sheriff's public page reviewed did "
                    "not expose a real-estate foreclosure/sheriff-sale "
                    "calendar or parcel list. The statewide Missouri "
                    "Press Association search offers Foreclosure and "
                    "Sheriff's Sales categories, but no current "
                    "Boone-specific sale list or complete feed was "
                    "verified. Its terms prohibit scraping and "
                    "automation and limit viewing to personal, "
                    "non-commercial use; use manual research only unless "
                    "written authorization is obtained."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Boone County Circuit Court Clerk and Missouri Courts Case.net"
                )
                directory_url = "https://www.courts.mo.gov/hosted/circuit13/"
                source_url = (
                    "https://www.courts.mo.gov/cnet/cases/newHeader.do"
                )
                note += (
                    " The official Circuit Court Clerk page and Missouri "
                    "Case.net both returned HTTP 403 in this check. No "
                    "Boone-specific bulk default/lis-pendens feed, "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified."
                )
        if state == "MO" and county_name == "Bollinger":
            if category == "assessor":
                directory_name = (
                    "Bollinger County Assessor and Vanguard property search"
                )
                directory_url = "https://www.mocounties.com/bollinger-county"
                source_url = (
                    "https://bollinger.missouriassessors.com/search.php"
                )
                note += (
                    " The assessor search identifies Bollinger County "
                    "and includes an as-is public-information disclaimer; "
                    "its unfiltered response showed an adjoining "
                    "jurisdiction notice rather than a current parcel "
                    "result. Vanguard's linked Terms prohibit data mining, "
                    "robots, screen scraping, and commercial use without "
                    "express written consent. No bulk export/API or "
                    "authorization for daily commercial extraction was "
                    "verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Bollinger County Collector tax-payment portal and "
                    "Missouri Public Notices"
                )
                directory_url = "https://bollingermo.devnetwedge.com/"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The DEVNET page is a tax-payment site with "
                    "transaction and delinquent-account limitations; it "
                    "does not expose a delinquent tax-sale calendar or "
                    "parcel list. The statewide Missouri Press "
                    "Association search offers a Tax Sale category, but "
                    "no current Bollinger-specific list, sale date, "
                    "complete feed, or collector authorization for "
                    "automation was verified. Its terms limit viewing "
                    "to personal, non-commercial use and prohibit "
                    "scraping and automation; use manual research only "
                    "unless written authorization is obtained."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Missouri Association of Counties Bollinger County profile"
                )
                directory_url = "https://www.mocounties.com/bollinger-county"
                source_url = directory_url
                note += (
                    " The Association profile lists county office "
                    "contacts, not a code-enforcement service. No "
                    "countywide property-level violation portal, feed, "
                    "export/API, update cadence, or automated-access "
                    "permission was verified. Municipal providers remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Bollinger County office directory and Missouri Public Notices"
                )
                directory_url = "https://www.mocounties.com/bollinger-county"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The Association profile is an office directory, "
                    "not a foreclosure or sheriff-sale calendar. The "
                    "statewide Missouri Press Association search offers "
                    "Foreclosure and Sheriff's Sales categories, but no "
                    "current Bollinger-specific sale list or complete "
                    "feed was verified. Its terms prohibit scraping and "
                    "automation and limit viewing to personal, "
                    "non-commercial use; use manual research only unless "
                    "written authorization is obtained."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Bollinger County office directory and Missouri Courts Case.net"
                )
                directory_url = "https://www.mocounties.com/bollinger-county"
                source_url = (
                    "https://www.courts.mo.gov/cnet/cases/newHeader.do"
                )
                note += (
                    " The county office profile is not a "
                    "property-default or lis-pendens index. Missouri "
                    "Case.net returned HTTP 403 in this check. No "
                    "Bollinger-specific bulk pre-foreclosure feed, "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified."
                )
        if state == "MO" and county_name == "Benton":
            if category == "assessor":
                directory_name = (
                    "Benton County office directory and Missouri assessor directory"
                )
                directory_url = "https://www.mocounties.com/benton-county"
                source_url = (
                    "https://stc.mo.gov/assessor/assessor-directory/"
                )
                note += (
                    " The Missouri Association of Counties profile lists "
                    "the Assessor's contact but no parcel-search portal. "
                    "The State Tax Commission directory displayed a "
                    "2013 date. The candidate benton.missouriassessors.com "
                    "root returned an Admin page and its /search.php "
                    "endpoint returned HTTP 404; no current Benton "
                    "parcel search, export/API, or permission for daily "
                    "commercial extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Benton County Collector contact and Missouri Public Notices"
                )
                directory_url = "https://www.mocounties.com/benton-county"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The Association profile lists the Collector's "
                    "contact but is not a delinquent-tax-sale calendar "
                    "or parcel list. The statewide Missouri Press "
                    "Association search offers a Tax Sale category, but "
                    "no current Benton-specific list, sale date, complete "
                    "feed, or permission for automated collection was "
                    "verified. Its terms limit viewing to personal, "
                    "non-commercial use and prohibit scraping and "
                    "automation; use manual research only unless written "
                    "authorization is obtained."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Missouri Association of Counties Benton County profile"
                )
                directory_url = "https://www.mocounties.com/benton-county"
                source_url = directory_url
                note += (
                    " The Association profile is a county-office "
                    "directory; no countywide property-level "
                    "code-enforcement service, violation feed, "
                    "export/API, update cadence, or automated-access "
                    "permission was verified. Municipal providers remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Benton County office directory and Missouri Public Notices"
                )
                directory_url = "https://www.mocounties.com/benton-county"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The Association profile is an office directory, "
                    "not a foreclosure or sheriff-sale calendar. The "
                    "statewide Missouri Press Association search offers "
                    "Foreclosure and Sheriff's Sales categories, but no "
                    "current Benton-specific sale list or complete feed "
                    "was verified. Its terms prohibit scraping and "
                    "automation and limit viewing to personal, "
                    "non-commercial use; use manual research only unless "
                    "written authorization is obtained."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Benton County Clerk contact and Missouri Courts Case.net"
                )
                directory_url = "https://www.mocounties.com/benton-county"
                source_url = (
                    "https://www.courts.mo.gov/cnet/cases/newHeader.do"
                )
                note += (
                    " The Association profile lists the County Clerk "
                    "contact but is not a property-default or "
                    "lis-pendens index. Missouri Case.net returned HTTP "
                    "403 in this check. No Benton-specific bulk "
                    "pre-foreclosure feed, export/API, update cadence, "
                    "or permission for daily automated access was "
                    "verified."
                )
        if state == "MO" and county_name == "Bates":
            if category == "assessor":
                directory_name = (
                    "Bates County office directory and Missouri assessor directory"
                )
                directory_url = "https://www.mocounties.com/bates-county"
                source_url = (
                    "https://stc.mo.gov/assessor/assessor-directory/"
                )
                note += (
                    " The county profile lists local offices but does not "
                    "provide an Assessor property-search link. The State "
                    "Tax Commission directory displayed a 2013 date. The "
                    "candidate bates.missouriassessors.com root returned "
                    "an Admin page and its /search.php endpoint returned "
                    "HTTP 404; no current Bates parcel search, "
                    "export/API, or daily-extraction authorization was "
                    "verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Bates County office directory and Missouri Public Notices"
                )
                directory_url = "https://www.mocounties.com/bates-county"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The county profile is an office directory, not a "
                    "delinquent-tax-sale calendar or parcel list. The "
                    "statewide Missouri Press Association search offers "
                    "a Tax Sale category, but no current Bates-specific "
                    "list, sale date, complete feed, or collector "
                    "authorization for automation was verified. Its "
                    "terms limit viewing to personal, non-commercial "
                    "use and prohibit scraping and automation; use "
                    "manual research only unless written authorization "
                    "is obtained."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Missouri Association of Counties Bates County profile"
                )
                directory_url = "https://www.mocounties.com/bates-county"
                source_url = directory_url
                note += (
                    " The county profile is a contact directory; no "
                    "countywide property-level code-enforcement service, "
                    "violation feed, export/API, update cadence, or "
                    "automated-access permission was verified. Municipal "
                    "providers remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Bates County Sheriff contact and Missouri Public Notices"
                )
                directory_url = "https://www.mocounties.com/bates-county"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The county profile lists the Sheriff and Circuit "
                    "Clerk contacts but is not a sale calendar. The "
                    "statewide Missouri Press Association search offers "
                    "Foreclosure and Sheriff's Sales categories, but no "
                    "current Bates-specific sale list or complete feed "
                    "was verified. Its terms prohibit scraping and "
                    "automation and limit viewing to personal, "
                    "non-commercial use; use manual research only unless "
                    "written authorization is obtained."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Bates County Circuit Clerk contact and Missouri Courts Case.net"
                )
                directory_url = "https://www.mocounties.com/bates-county"
                source_url = (
                    "https://www.courts.mo.gov/cnet/cases/newHeader.do"
                )
                note += (
                    " The county profile lists the Circuit Clerk contact "
                    "but is not a property-default or lis-pendens index. "
                    "Missouri Case.net returned HTTP 403 in this check. "
                    "No Bates-specific bulk pre-foreclosure feed, "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified."
                )
        if state == "MO" and county_name == "Barton":
            if category == "assessor":
                directory_name = (
                    "Barton County Assessor and Vanguard property search"
                )
                directory_url = "https://www.mocounties.com/barton-county"
                source_url = "https://barton.missouriassessors.com/search.php"
                note += (
                    " The assessor portal identifies the Barton County "
                    "Assessor and provides an interactive property "
                    "search, but its search response warns that property "
                    "information is supplied as-is. Vanguard's linked "
                    "Terms prohibit data mining, robots, screen scraping, "
                    "and commercial use without express written consent. "
                    "No bulk export/API or authorization for daily "
                    "commercial extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Barton County office directory and Missouri Public Notices"
                )
                directory_url = "https://www.mocounties.com/barton-county"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The county-office directory is not a delinquent "
                    "tax-sale calendar or parcel list. The statewide "
                    "Missouri Press Association search offers a Tax Sale "
                    "category, but no current Barton-specific list, sale "
                    "date, complete feed, or collector authorization for "
                    "automation was verified. The site's terms limit "
                    "viewing to personal, non-commercial use and prohibit "
                    "scraping and automation; use manual research only "
                    "unless written authorization is obtained."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Missouri Association of Counties Barton County profile"
                )
                directory_url = "https://www.mocounties.com/barton-county"
                source_url = directory_url
                note += (
                    " The Association profile is a county-office "
                    "directory; no countywide property-level "
                    "code-enforcement service, violation feed, "
                    "export/API, update cadence, or automated-access "
                    "permission was verified. Municipal providers remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Barton County Sheriff contact and Missouri Public Notices"
                )
                directory_url = "https://www.mocounties.com/barton-county"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The county-office directory is not a foreclosure "
                    "or sheriff-sale calendar. The statewide Missouri "
                    "Press Association search offers Foreclosure and "
                    "Sheriff's Sales categories, but no current "
                    "Barton-specific sale list or complete feed was "
                    "verified. Its terms prohibit scraping and automation "
                    "and limit viewing to personal, non-commercial use; "
                    "use manual research only unless written "
                    "authorization is obtained."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Barton County office directory and Missouri Courts Case.net"
                )
                directory_url = "https://www.mocounties.com/barton-county"
                source_url = (
                    "https://www.courts.mo.gov/cnet/cases/newHeader.do"
                )
                note += (
                    " The county-office directory is not a "
                    "property-default or lis-pendens index. Missouri "
                    "Case.net returned HTTP 403 in this check. No "
                    "Barton-specific bulk pre-foreclosure feed, "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified."
                )
        if state == "MO" and county_name == "Barry":
            if category == "assessor":
                directory_name = (
                    "Missouri State Tax Commission assessor directory"
                )
                directory_url = (
                    "https://stc.mo.gov/assessor/assessor-directory/"
                )
                source_url = directory_url
                note += (
                    " The State Tax Commission page is an office "
                    "directory, displayed a 2013 date, and did not "
                    "provide a current Barry County parcel-search link. "
                    "The candidate "
                    "barry.missouriassessors.com/search.php returned "
                    "subdivision/township records for Foster County, "
                    "North Dakota, not Barry County, Missouri, and is "
                    "not a valid Barry parcel source. No current "
                    "Barry-specific assessor portal, export/API, or "
                    "permission for daily commercial extraction was "
                    "verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Barry County office directory and Missouri Public Notices"
                )
                directory_url = "https://www.mocounties.com/barry-county"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The Association profile is a county-office "
                    "directory, not a delinquent-tax-sale calendar or "
                    "parcel list. The statewide Missouri Press "
                    "Association search offers a Tax Sale category, but "
                    "no current Barry-specific list, sale date, complete "
                    "feed, or collector authorization for automation was "
                    "verified. The site's terms limit viewing to "
                    "personal, non-commercial use and prohibit scraping "
                    "and automation; use manual research only unless "
                    "written authorization is obtained."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Missouri Association of Counties Barry County profile"
                )
                directory_url = "https://www.mocounties.com/barry-county"
                source_url = directory_url
                note += (
                    " The Association profile is a contact directory; "
                    "no countywide property-level code-enforcement "
                    "service, violation feed, export/API, update cadence, "
                    "or automated-access permission was verified. "
                    "Municipal code-enforcement providers remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Barry County Sheriff contact and Missouri Public Notices"
                )
                directory_url = "https://www.mocounties.com/barry-county"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The Association profile lists the Sheriff and "
                    "Circuit Clerk contacts but is not a sale calendar. "
                    "The statewide Missouri Press Association search "
                    "offers Foreclosure and Sheriff's Sales categories, "
                    "but no current Barry-specific sale list or complete "
                    "feed was verified. Its terms prohibit scraping and "
                    "automation and limit viewing to personal, "
                    "non-commercial use; use manual research only unless "
                    "written authorization is obtained."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Barry County Circuit Clerk contact and Missouri Courts Case.net"
                )
                directory_url = "https://www.mocounties.com/barry-county"
                source_url = (
                    "https://www.courts.mo.gov/cnet/cases/newHeader.do"
                )
                note += (
                    " The Association profile lists the Circuit Clerk "
                    "contact but is not a property-default or "
                    "lis-pendens index. Missouri Case.net returned HTTP "
                    "403 in this check. No Barry-specific bulk "
                    "pre-foreclosure feed, export/API, update cadence, "
                    "or permission for daily automated access was "
                    "verified."
                )
        if state == "MO" and county_name == "Audrain":
            if category == "assessor":
                directory_name = "Audrain County Assessor and property search"
                directory_url = "https://www.audraincounty.org/assessor/"
                source_url = "https://audrain.missouriassessors.com/search.php"
                note += (
                    " The official County website links to the Vanguard "
                    "E-File and Property Search and a separate GIS mapping "
                    "tool. The real-estate search is live, but Vanguard's "
                    "Terms prohibit data mining, robots, screen scraping, "
                    "and commercial use without express written consent. "
                    "No bulk export/API or authorization for daily "
                    "commercial extraction was verified. The County GIS "
                    "page also disclaims accuracy/completeness warranties."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Audrain County tax payment information and Missouri "
                    "Public Notices"
                )
                directory_url = (
                    "https://www.audraincounty.org/pay-county-taxes-online"
                )
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The official County page describes the DEVNET portal "
                    "as a method to pay county taxes; it does not provide "
                    "a delinquent tax-sale list or calendar. The statewide "
                    "Missouri Press Association public-notice search has "
                    "Audrain County and a Tax Sale category, but no current "
                    "Audrain-specific parcel list, sale date, or complete "
                    "feed was verified. Its terms limit viewing to "
                    "personal, non-commercial use and prohibit scraping "
                    "and automation; use manual research only unless "
                    "written authorization is obtained."
                )
            elif category == "code_enforcement":
                directory_name = "Audrain County Commission"
                directory_url = (
                    "https://www.audraincounty.org/county-commission/"
                )
                source_url = directory_url
                note += (
                    " The official County pages reviewed did not expose "
                    "a countywide property-level code-enforcement "
                    "service or violation feed. No export/API, update "
                    "cadence, or automated-access permission was "
                    "verified. Municipal providers, including Mexico and "
                    "Vandalia, remain unverified."
                )
            elif category == "foreclosure":
                directory_name = "Audrain County Sheriff"
                directory_url = "https://www.audraincounty.org/sheriff/"
                source_url = "https://www.mopublicnotices.com/"
                note += (
                    " The official County Sheriff page links to the "
                    "Sheriff's website; the public home page reviewed "
                    "shows general department information, not a "
                    "foreclosure/sheriff-sale calendar or parcel list. "
                    "The statewide Missouri Press Association notice "
                    "search has Audrain County and Foreclosure/Sheriff "
                    "Sales categories, but no current county-specific "
                    "sale list or complete feed was verified. Its terms "
                    "prohibit scraping and automation and limit viewing "
                    "to personal, non-commercial use; use manual research "
                    "only unless written authorization is obtained."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Audrain County Clerk and Missouri Courts Case.net"
                )
                directory_url = (
                    "https://www.audraincounty.org/county-clerk/"
                )
                source_url = (
                    "https://www.courts.mo.gov/cnet/cases/newHeader.do"
                )
                note += (
                    " The County Clerk page reviewed concerns election "
                    "administration, not property defaults or lis-pendens "
                    "filings. Missouri Case.net returned HTTP 403 in this "
                    "check. No Audrain-specific bulk pre-foreclosure "
                    "feed, export/API, update cadence, or permission for "
                    "daily automated access was verified."
                )
        if state == "MO" and county_name == "Atchison":
            if category == "assessor":
                directory_name = (
                    "Missouri Association of Counties Atchison office directory"
                )
                directory_url = "https://www.mocounties.com/atchison-county"
                source_url = directory_url
                note += (
                    " The Association profile lists the County Assessor's "
                    "mailing address and phone number but no property "
                    "search portal or data export. The Missouri State Tax "
                    "Commission assessor-directory page displayed a "
                    "2013 date, and the candidate "
                    "atchison.missouriassessors.com/search.php endpoint "
                    "returned HTTP 404; no current county parcel search, "
                    "machine-readable feed/API, or daily-extraction "
                    "permission was verified. "
                    "atchisoncounty.org is the Atchison County "
                    "Development Corporation, not a County Assessor site."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Missouri Press Association Public Notices — "
                    "Atchison County search"
                )
                directory_url = "https://www.mopublicnotices.com/"
                source_url = directory_url
                note += (
                    " The statewide search identifies itself as a "
                    "Missouri Press Association public-notice compilation; "
                    "its search controls include Atchison County and a "
                    "Tax Sale category. No current Atchison-specific "
                    "parcel list, sale date, collector calendar, or "
                    "complete feed was verified. The site's terms limit "
                    "viewing to personal, non-commercial use and prohibit "
                    "scraping and automation; use manual research only "
                    "unless written authorization is obtained."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Missouri Association of Counties Atchison office directory"
                )
                directory_url = "https://www.mocounties.com/atchison-county"
                source_url = directory_url
                note += (
                    " The Association profile is a county-office contact "
                    "directory, not a code-enforcement service. No "
                    "countywide property-level violation portal, feed, "
                    "export/API, update cadence, or automated-access "
                    "permission was verified. Municipal code-enforcement "
                    "providers remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Missouri Press Association Public Notices — "
                    "Atchison County search"
                )
                directory_url = "https://www.mopublicnotices.com/"
                source_url = directory_url
                note += (
                    " The statewide search has Atchison County and "
                    "Foreclosure/Sheriff Sales categories, but no "
                    "current Atchison-specific foreclosure or sheriff-sale "
                    "calendar, parcel list, or complete feed was verified. "
                    "The site's terms limit viewing to personal, "
                    "non-commercial use and prohibit scraping and "
                    "automation; use manual research only unless written "
                    "authorization is obtained."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Missouri Courts Case.net and Atchison County "
                    "Circuit Clerk contact"
                )
                directory_url = "https://www.mocounties.com/atchison-county"
                source_url = (
                    "https://www.courts.mo.gov/cnet/cases/newHeader.do"
                )
                note += (
                    " The statewide Missouri Case.net search returned "
                    "HTTP 403 in this check. The Association profile lists "
                    "the County Clerk contact but is not a default or "
                    "lis-pendens index. No Atchison-specific bulk "
                    "pre-foreclosure feed, export/API, update cadence, or "
                    "permission for daily automated access was verified."
                )
        if state == "MO" and county_name == "Andrew":
            if category == "assessor":
                directory_name = "Andrew County Assessor"
                directory_url = "https://andrewcounty.org/offices/assessor/"
                source_url = directory_url
                note += (
                    " The official Assessor page describes assessment "
                    "responsibilities and map sales but exposes no "
                    "parcel-search portal or export. The Collector's "
                    "Devnet Wedge site is for tax payments/viewing tax "
                    "information, not a verified Assessor parcel feed. "
                    "No machine-readable assessment feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = "Andrew County Collector tax auction"
                directory_url = (
                    "https://andrewcounty.org/offices/collector/tax-auction/"
                )
                source_url = (
                    "https://andrewcounty.org/wp-content/uploads/"
                    "Tax-Sale-7-15-2025.pdf"
                )
                note += (
                    " The official Collector page says the delinquent "
                    "tax sale is annual, on the fourth Monday in August, "
                    "and the list is published in a local newspaper for "
                    "three consecutive weeks. The currently linked "
                    "parcel list is dated 2025-07-15, not a current "
                    "2026 list. No daily feed/API, ongoing list cadence, "
                    "or permission for automated extraction was "
                    "identified."
                )
            elif category == "code_enforcement":
                directory_name = "Andrew County official offices"
                directory_url = "https://andrewcounty.org/offices/"
                source_url = "https://andrewcounty.org/"
                note += (
                    " The County website and official office pages "
                    "reviewed did not expose a property-level "
                    "code-enforcement service or violation feed. No "
                    "countywide code feed, export/API, update cadence, "
                    "or permission for automated access was identified; "
                    "municipal providers remain unverified."
                )
            elif category == "foreclosure":
                directory_name = "Andrew County Sheriff"
                directory_url = "https://andrewcounty.org/offices/sheriff/"
                source_url = directory_url
                note += (
                    " The County Sheriff page links to a separate "
                    "Sheriff website, but that linked site failed to "
                    "load in this check. No County foreclosure/sheriff "
                    "sale calendar, parcel list, feed/API, or daily "
                    "update schedule was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Missouri Courts Case.net and Andrew County Circuit Clerk"
                )
                directory_url = "https://www.mocounties.com/andrew-county"
                source_url = (
                    "https://www.courts.mo.gov/cnet/cases/newHeader.do"
                )
                note += (
                    " The statewide Missouri Case.net search returned "
                    "HTTP 403 in this check. No Andrew County-specific "
                    "bulk default/lis-pendens feed, export/API, update "
                    "cadence, or permission for daily automated access "
                    "was verified. The Missouri Association of Counties "
                    "profile lists the Circuit Clerk as an office "
                    "contact, not a pre-foreclosure data service."
                )
        if state == "MO" and county_name == "Adair":
            if category == "assessor":
                directory_name = "Adair County Assessor and real-estate search"
                directory_url = (
                    "https://adaircountymissouri.com/departments/assessor/"
                )
                source_url = (
                    "https://adair.missouriassessors.com/search.php"
                )
                note += (
                    " The official County Assessor page links to a "
                    "Vanguard Appraisals real-estate search and a "
                    "personal-property search. The portal is interactive "
                    "and disclaims data warranties; its Terms explicitly "
                    "prohibit data mining, robots, screen scraping, and "
                    "commercial use without express written consent. No "
                    "daily feed/API or extraction authorization was "
                    "verified; do not automate collection absent written "
                    "permission."
                )
            elif category == "tax_sale":
                directory_name = "Adair County Collector of Revenue"
                directory_url = (
                    "https://adaircountymissouri.com/departments/collector/"
                )
                source_url = directory_url
                note += (
                    " The official Collector page says the office "
                    "collects current and delinquent real-estate and "
                    "personal-property taxes, but it does not expose a "
                    "tax-sale calendar, parcel list, feed/API, or daily "
                    "update schedule. No county-specific automated "
                    "tax-sale source or permission was verified."
                )
            elif category == "code_enforcement":
                directory_name = "Adair County Commission"
                directory_url = (
                    "https://adaircountymissouri.com/departments/commission/"
                )
                source_url = (
                    "https://adaircountymissouri.com/wp-content/uploads/"
                    "2026/09/Resolution-2026-1.pdf"
                )
                note += (
                    " The County's September 2026 resolution says the "
                    "County currently has no zoning regulations for "
                    "large-scale facilities and states an intent to "
                    "review standards. This does not establish that all "
                    "code enforcement is absent. No property-level "
                    "countywide code-violation feed, export/API, update "
                    "cadence, or permission for automated access was "
                    "identified; city enforcement providers remain "
                    "separate and unverified."
                )
            elif category == "foreclosure":
                directory_name = "Adair County Sheriff"
                directory_url = (
                    "https://adaircountymissouri.com/departments/sheriff/"
                )
                source_url = directory_url
                note += (
                    " The official Sheriff page directs users to the "
                    "office's Facebook page; it exposes no foreclosure "
                    "or sheriff-sale calendar, parcel list, feed/API, or "
                    "daily update schedule. No county-authorized "
                    "automated foreclosure source or reuse permission "
                    "was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Missouri Courts Case.net and Adair County Circuit Clerk"
                )
                directory_url = "https://www.mocounties.com/adair-county"
                source_url = (
                    "https://www.courts.mo.gov/cnet/cases/newHeader.do"
                )
                note += (
                    " The statewide Missouri Case.net search is a "
                    "case-by-case court lookup; the courts site returned "
                    "HTTP 403 in this check. No Adair County-specific "
                    "bulk default/lis-pendens feed, export/API, update "
                    "cadence, or permission for daily automated access "
                    "was verified. The Missouri Association of Counties "
                    "profile lists the Circuit Clerk as an office "
                    "contact, not a pre-foreclosure data service."
                )
        if state == "AR" and county_name == "Washington":
            if category == "assessor":
                directory_name = (
                    "Washington County Assessor contacts and official website"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/washington/"
                )
                source_url = "https://www.washingtoncountyar.gov/"
                note += (
                    " The Association profile identifies the County and "
                    "links to its official website, but that site returned "
                    "HTTP 403 in this check. The county-specific "
                    "ARCountyData URL redirected to the generic welcome "
                    "page, not County parcel records. No verified "
                    "Assessor property-search portal, feed/API, current "
                    "update cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Washington County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Washington County official website and jurisdiction profile"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/washington/"
                )
                source_url = "https://www.washingtoncountyar.gov/"
                note += (
                    " The official County website returned HTTP 403 in "
                    "this check, so its code-enforcement services and "
                    "records could not be verified. No countywide "
                    "property-level violation feed was established; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Washington County offices and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/washington/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The official County website returned HTTP 403 in "
                    "this check; no Sheriff sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Washington County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/washington/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no "
                    "Washington County-specific default/lis-pendens "
                    "feed, bulk export/API, update cadence, or "
                    "permission for daily automated access was "
                    "verified. County-level filing coverage remains "
                    "unconfirmed; foreclosure-sale notices are not "
                    "pre-foreclosure records."
                )
        if state == "AR" and county_name == "White":
            if category == "assessor":
                directory_name = "White County Assessor and ARCountyData search"
                directory_url = "https://www.arcounties.org/counties/white/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=White&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public real-estate search. "
                    "It is an interactive third-party portal, not a "
                    "documented daily feed; no machine-readable "
                    "feed/API, update cadence, or authorization for "
                    "daily commercial extraction was identified. The "
                    "official County website returned HTTP 403 in this "
                    "check. ARCountyData's Terms reserve rights over "
                    "proprietary website material and require express "
                    "written consent for its reproduction; confirm "
                    "permission before automated reuse."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a White County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "White County official website"
                directory_url = "https://www.whitecountyar.org/"
                source_url = directory_url
                note += (
                    " The official County website returned HTTP 403 in "
                    "this check, so property-level code-enforcement "
                    "services and records could not be verified. No "
                    "countywide violation feed was established; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "White County offices and Arkansas Public Notices"
                )
                directory_url = "https://www.whitecountyar.org/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The official County website returned HTTP 403 in "
                    "this check; no Sheriff sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "White County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/white/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no White "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Woodruff":
            if category == "assessor":
                directory_name = (
                    "Woodruff County Assessor contacts and county records"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/woodruff/"
                )
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Woodruff&s=R"
                )
                note += (
                    " The county-specific ARCountyData URL exposes a "
                    "free County Clerk marriage-record search, not "
                    "Assessor parcel data. The official State directory "
                    "entry linked from the County profile returned only "
                    "a County address. No verified Assessor "
                    "property-search portal, feed/API, update cadence, "
                    "or permission for daily commercial extraction was "
                    "identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Woodruff County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Woodruff County official directory entry"
                directory_url = (
                    "https://portal.arkansas.gov/counties/woodruff/"
                )
                source_url = directory_url
                note += (
                    " The State directory entry returned only the "
                    "County address, not County services or "
                    "property-level code-enforcement records. No "
                    "countywide violation feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Woodruff County offices and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/woodruff/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " No County Sheriff sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Woodruff County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/woodruff/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no "
                    "Woodruff County-specific default/lis-pendens "
                    "feed, bulk export/API, update cadence, or "
                    "permission for daily automated access was "
                    "verified. County-level filing coverage remains "
                    "unconfirmed; foreclosure-sale notices are not "
                    "pre-foreclosure records."
                )
        if state == "AR" and county_name == "Yell":
            if category == "assessor":
                directory_name = (
                    "Yell County Assessor contacts and ARCountyData records"
                )
                directory_url = "https://www.arcounties.org/counties/yell/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Yell&s=R"
                )
                note += (
                    " The county-specific ARCountyData page returned a "
                    "general property-tax estimate and Assessor duties, "
                    "but no county-specific Assessor search or parcel "
                    "records. No verified Assessor property-search "
                    "portal, feed/API, update cadence, or permission for "
                    "daily commercial extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Yell County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Yell County"
                directory_url = "https://www.arcounties.org/counties/yell/"
                source_url = directory_url
                note += (
                    " The Association profile provides County "
                    "background and contacts, not a property-level "
                    "code-enforcement service. No countywide violation "
                    "feed was identified; municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Yell County offices and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/yell/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " No County Sheriff sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Yell County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/yell/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Yell "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Stone":
            if category == "assessor":
                directory_name = (
                    "Stone County Assessor contacts and ARCountyData search"
                )
                directory_url = "https://www.arcounties.org/counties/stone/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Stone&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public real-estate search. "
                    "It is an interactive third-party portal, not a "
                    "documented daily feed; no machine-readable "
                    "feed/API, update cadence, or authorization for "
                    "daily commercial extraction was identified. "
                    "ARCountyData's Terms reserve rights over "
                    "proprietary website material and require express "
                    "written consent for its reproduction; confirm "
                    "permission before automated reuse."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Stone County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Stone County"
                directory_url = "https://www.arcounties.org/counties/stone/"
                source_url = directory_url
                note += (
                    " The Association profile provides County "
                    "background and contact information, not a "
                    "property-level code-enforcement service. No "
                    "countywide violation feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Stone County offices and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/stone/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " No County Sheriff sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Stone County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/stone/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Stone "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Union":
            if category == "assessor":
                directory_name = (
                    "Union County Assessor contacts and ARCountyData records"
                )
                directory_url = "https://www.arcounties.org/counties/union/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Union&s=R"
                )
                note += (
                    " The county-specific ARCountyData page exposed no "
                    "Assessor search or parcel records; its metadata "
                    "showed Collector data last updated 2019-03-07. The "
                    "linked County website contains County history, not "
                    "an Assessor property search. No verified Assessor "
                    "property-search portal, feed/API, current update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Union County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Union County official website"
                directory_url = "https://www.unioncountyar.com/"
                source_url = directory_url
                note += (
                    " The linked County website returned historical "
                    "County information, not property-level "
                    "code-enforcement services or records. No "
                    "countywide violation feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Union County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/union/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists the County Sheriff "
                    "and contact details but no sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Union County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/union/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Union "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Van Buren":
            if category == "assessor":
                directory_name = (
                    "Van Buren County Assessor contacts and ARCountyData search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/van-buren/"
                )
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Van%20Buren&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public real-estate search. "
                    "It is an interactive third-party portal, not a "
                    "documented daily feed; no machine-readable "
                    "feed/API, update cadence, or authorization for "
                    "daily commercial extraction was identified. "
                    "ARCountyData's Terms reserve rights over "
                    "proprietary website material and require express "
                    "written consent for its reproduction; confirm "
                    "permission before automated reuse."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Van Buren County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Van Buren County official website"
                directory_url = "https://www.vanburencountyar.gov/"
                source_url = directory_url
                note += (
                    " The official County website returned general "
                    "community information, not property-level "
                    "code-enforcement services or records. No "
                    "countywide violation feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Van Buren County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/van-buren/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists the County Sheriff "
                    "and contact details but no sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Van Buren County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/van-buren/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Van "
                    "Buren County-specific default/lis-pendens feed, "
                    "bulk export/API, update cadence, or permission for "
                    "daily automated access was verified. County-level "
                    "filing coverage remains unconfirmed; "
                    "foreclosure-sale notices are not pre-foreclosure "
                    "records."
                )
        if state == "AR" and county_name == "Sevier":
            if category == "assessor":
                directory_name = (
                    "Sevier County Assessor contacts and ARCountyData records"
                )
                directory_url = "https://www.arcounties.org/counties/sevier/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Sevier&s=R"
                )
                note += (
                    " The county-specific ARCountyData page exposed no "
                    "Assessor search or parcel records; its metadata "
                    "showed Collector data last updated 2023-12-14. The "
                    "official County website currently returns a "
                    "courthouse-closure page with 2024 dates, not "
                    "Assessor records. No verified Assessor "
                    "property-search portal, feed/API, current update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Sevier County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Sevier County official website"
                directory_url = "https://www.seviercountyar.org/"
                source_url = directory_url
                note += (
                    " The official County website returned only a "
                    "courthouse-closure page with 2024 dates in this "
                    "check, not a property-level code-enforcement "
                    "service. No countywide violation feed was "
                    "identified; municipal providers, export/API, "
                    "update cadence, and permission for automated "
                    "access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Sevier County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/sevier/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile identifies the County "
                    "government but no Sheriff sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Sevier County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/sevier/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Sevier "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Sharp":
            if category == "assessor":
                directory_name = (
                    "Sharp County Assessor contacts and ARCountyData records"
                )
                directory_url = "https://www.arcounties.org/counties/sharp/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Sharp&s=R"
                )
                note += (
                    " The Association profile identifies the County "
                    "government. The county-specific ARCountyData page "
                    "returned a general property-tax estimate and "
                    "Assessor duties, but no county-specific Assessor "
                    "search or parcel records. No verified Assessor "
                    "property-search portal, feed/API, update cadence, "
                    "or permission for daily commercial extraction was "
                    "identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Sharp County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Sharp County"
                directory_url = "https://www.arcounties.org/counties/sharp/"
                source_url = directory_url
                note += (
                    " The Association profile provides County "
                    "background/contact information, not a "
                    "property-level code-enforcement service. No "
                    "countywide violation feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Sharp County offices and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/sharp/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " No County Sheriff sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Sharp County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/sharp/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Sharp "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "St. Francis":
            if category == "assessor":
                directory_name = "St. Francis County Assessor and ARCountyData"
                directory_url = (
                    "https://stfranciscountyar.gov/departments/assessor/"
                )
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=St.%20Francis&s=R"
                )
                note += (
                    " The County Assessor department page identifies "
                    "the Assessor, and the county-specific ARCountyData "
                    "page says the Assessor sponsors a free public "
                    "real-estate search. This is an interactive "
                    "third-party portal, not a documented daily feed; "
                    "no machine-readable feed/API, update cadence, or "
                    "authorization for daily commercial extraction was "
                    "identified. ARCountyData's Terms reserve rights "
                    "over proprietary website material and require "
                    "express written consent for its reproduction; "
                    "confirm permission before automated reuse."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a St. Francis "
                    "County-specific current sale date/list or "
                    "machine-readable feed; update cadence and "
                    "permission for daily/commercial automation were "
                    "not verified."
                )
            elif category == "code_enforcement":
                directory_name = "St. Francis County official departments"
                directory_url = "https://stfranciscountyar.gov/"
                source_url = directory_url
                note += (
                    " The official County site returned general "
                    "County Judge welcome content in this check, not a "
                    "property-level county code-enforcement service. "
                    "No countywide violation feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "St. Francis County offices and Arkansas Public Notices"
                )
                directory_url = "https://stfranciscountyar.gov/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The County site did not expose a Sheriff sale "
                    "calendar or County-authorized foreclosure feed in "
                    "this check. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by "
                    "county, but is not the official publication, does "
                    "not include notices from every newspaper, and its "
                    "Terms limit use to personal, non-commercial "
                    "purposes and prohibit copying or replication. "
                    "Written permission is required before commercial "
                    "ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "St. Francis County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://stfranciscountyar.gov/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no St. "
                    "Francis County-specific default/lis-pendens feed, "
                    "bulk export/API, update cadence, or permission for "
                    "daily automated access was verified. County-level "
                    "filing coverage remains unconfirmed; "
                    "foreclosure-sale notices are not pre-foreclosure "
                    "records."
                )
        if state == "AR" and county_name == "Searcy":
            if category == "assessor":
                directory_name = (
                    "Searcy County Assessor and ARCountyData records"
                )
                directory_url = "https://www.arcounties.org/counties/searcy/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Searcy&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public real-estate search. "
                    "It is an interactive third-party portal, not a "
                    "documented daily feed; no machine-readable "
                    "feed/API, update cadence, or authorization for "
                    "daily commercial extraction was identified. The "
                    "official CountyService.net assessment workflow "
                    "states that only people who assessed in Searcy "
                    "County the prior year can assess online; that "
                    "workflow is not a parcel-valuation search. "
                    "ARCountyData's Terms reserve rights over "
                    "proprietary website material and require express "
                    "written consent for its reproduction; confirm "
                    "permission before automated reuse."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Searcy County Collector and Arkansas Commissioner of State Lands"
                )
                directory_url = "https://www.arcounties.org/counties/searcy/"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. Searcy "
                    "County's linked tax-payment portal currently says "
                    "online payments are not accepted and directs users "
                    "to contact the Collector; no Searcy-specific "
                    "current sale date/list or machine-readable feed, "
                    "update cadence, or permission for daily/commercial "
                    "automation was verified."
                )
            elif category == "code_enforcement":
                directory_name = "Searcy County official website"
                directory_url = "https://searcyco.org/"
                source_url = directory_url
                note += (
                    " The official County website returned general "
                    "welcome and governance content, not property-level "
                    "code-enforcement services or records. No "
                    "countywide violation feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Searcy County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/searcy/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists the County Sheriff "
                    "and contact details but no sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Searcy County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/searcy/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Searcy "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Scott":
            if category == "assessor":
                directory_name = "Scott County Assessor and CountyService.net"
                directory_url = (
                    "https://scottcountyar.com/assessor/assessor.cshtml"
                )
                source_url = "https://countyservice.net/assess?name=Scott"
                note += (
                    " The official County Assessor page links to "
                    "CountyService.net and says \"Assess Online.\" The "
                    "portal states that online assessment is unavailable "
                    "for people who did not assess in Scott County the "
                    "prior year and directs them to attend in person; "
                    "this is an annual assessment workflow, not a "
                    "parcel-valuation search. No property search "
                    "feed/API, daily update cadence, or authorization "
                    "for commercial extraction was verified. "
                    "CountyService.net's Terms require express written "
                    "consent to reproduce copyrighted/proprietary "
                    "material."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Scott County Collector and Arkansas Commissioner of State Lands"
                )
                directory_url = (
                    "https://scottcountyar.com/collector/tax_collector.cshtml"
                )
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The County Collector page says delinquent "
                    "information is published in the local newspaper "
                    "in late November or early December, and real "
                    "estate remaining unpaid for two years is forwarded "
                    "to the State Land Office for eventual public sale. "
                    "The State catalog is statewide; no Scott-specific "
                    "current sale date/list or machine-readable feed, "
                    "update cadence, or permission for daily/commercial "
                    "automation was verified."
                )
            elif category == "code_enforcement":
                directory_name = "Scott County official services"
                directory_url = "https://scottcountyar.com/welcome"
                source_url = directory_url
                note += (
                    " The County website provides general County "
                    "information but no property-level code-enforcement "
                    "service or violation data in this check. No "
                    "countywide code feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Scott County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/scott/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists the County Sheriff "
                    "and contact details but no sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Scott County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/scott/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Scott "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Saline":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Saline County"
                directory_url = "https://www.arcounties.org/counties/saline/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Saline&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public real-estate search. "
                    "It is an interactive third-party portal, not a "
                    "documented daily feed; no machine-readable "
                    "feed/API, update cadence, or authorization for "
                    "daily commercial extraction was identified. "
                    "ARCountyData's Terms reserve rights over "
                    "proprietary website material and require express "
                    "written consent for its reproduction; confirm "
                    "permission before automated reuse."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Saline County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Saline County official website"
                directory_url = "https://www.salinecounty.org/"
                source_url = directory_url
                note += (
                    " The County website returned only a template "
                    "instruction to copy and paste a link, not County "
                    "services or records. No property-level county "
                    "code-enforcement service/feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Saline County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/saline/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists the County Sheriff "
                    "and contact details but no sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Saline County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/saline/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Saline "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Randolph":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Randolph County"
                directory_url = "https://www.arcounties.org/counties/randolph/"
                source_url = directory_url
                note += (
                    " The Association profile lists the County Assessor "
                    "and office contact. The county-specific ARCountyData "
                    "URL redirected to the site's generic welcome page, "
                    "not Randolph County parcel records. No verified "
                    "Assessor property-search portal, feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Randolph County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Randolph County"
                directory_url = "https://www.arcounties.org/counties/randolph/"
                source_url = "https://portal.arkansas.gov/counties/randolph/"
                note += (
                    " The County profile lists offices and contact "
                    "details, while the state directory page returned "
                    "only a county address. Neither page exposes a "
                    "property-level code-enforcement service. No "
                    "countywide violation feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Randolph County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/randolph/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists the County Sheriff "
                    "and contact details but no sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Randolph County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/randolph/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Randolph "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Pulaski":
            if category == "assessor":
                directory_name = (
                    "Pulaski County Assessor contact and ARCountyData search"
                )
                directory_url = "https://www.arcounties.org/counties/pulaski/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Pulaski&s=R"
                )
                note += (
                    " The Association profile lists the County Assessor "
                    "and office contact. The county-specific ARCountyData "
                    "page says the Assessor sponsors a free public "
                    "real-estate search; it is an interactive "
                    "third-party portal, not a documented daily feed. "
                    "No machine-readable feed/API, update cadence, or "
                    "authorization for daily commercial extraction was "
                    "identified. ARCountyData's Terms reserve rights "
                    "over proprietary website material and require "
                    "express written consent for its reproduction; "
                    "confirm permission before automated reuse."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Pulaski County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Pulaski County official departments"
                directory_url = "https://www.pulaskicounty.net/departments"
                source_url = directory_url
                note += (
                    " The official County departments page returned "
                    "general department and tax-payment content, not a "
                    "property-level code-enforcement service. No "
                    "countywide violation feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Pulaski County Sheriff and Arkansas Public Notices"
                )
                directory_url = "https://pcso.org/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists the County Sheriff, "
                    "and the linked Pulaski County Sheriff's Office site "
                    "is an official agency page; no sale calendar or "
                    "County-authorized foreclosure feed was identified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Pulaski County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/pulaski/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Pulaski "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Prairie":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Prairie County"
                directory_url = "https://www.arcounties.org/counties/prairie/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Prairie&s=R"
                )
                note += (
                    " The Association profile lists the County Assessor "
                    "and office contact, but not a parcel-data service. "
                    "The county-specific ARCountyData page is explicitly "
                    "a free Collector tax-record/receipt search, not an "
                    "Assessor valuation search. No verified Assessor "
                    "property portal, feed/API, update cadence, or "
                    "permission for daily commercial extraction was "
                    "identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Prairie County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Prairie County"
                directory_url = "https://www.arcounties.org/counties/prairie/"
                source_url = directory_url
                note += (
                    " The Association profile lists county offices and "
                    "contacts, not a property-level code-enforcement "
                    "service. No countywide violation feed was "
                    "identified; municipal providers, export/API, "
                    "update cadence, and permission for automated "
                    "access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Prairie County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/prairie/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists the County Sheriff "
                    "and contact details but no sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Prairie County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/prairie/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Prairie "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Pope":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Pope County"
                directory_url = "https://www.arcounties.org/counties/pope/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Pope&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public real-estate search. "
                    "It is an interactive third-party portal; no "
                    "machine-readable feed/API, update cadence, or "
                    "authorization for daily commercial extraction was "
                    "identified. ARCountyData's Terms reserve rights "
                    "over proprietary website material and require "
                    "express written consent for its reproduction; "
                    "confirm permission before automated reuse."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Pope County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Pope County"
                directory_url = "https://www.arcounties.org/counties/pope/"
                source_url = "https://www.popecountyar.gov/"
                note += (
                    " The Association profile links to the County's "
                    "official website, which resolved but exposed only "
                    "agenda-deadline and budget/quorum-court content in "
                    "this check. No property-level county code "
                    "enforcement service/feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Pope County offices and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/pope/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The County website retrieval did not establish a "
                    "Sheriff sale calendar or County-authorized "
                    "foreclosure feed. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Pope County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/pope/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Pope "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Polk":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Polk County"
                directory_url = "https://www.arcounties.org/counties/polk/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Polk&s=R"
                )
                note += (
                    " The Association profile provides County background "
                    "and an address but no Assessor contact or parcel "
                    "records. The county-specific ARCountyData page is "
                    "explicitly a free Collector tax-record/receipt "
                    "search, not an Assessor valuation search. No "
                    "verified Assessor property portal, feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Polk County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Polk County"
                directory_url = "https://www.arcounties.org/counties/polk/"
                source_url = directory_url
                note += (
                    " The County profile is a background and contact "
                    "page, not a property-level code-enforcement service. "
                    "No countywide violation feed was identified; "
                    "municipal providers, export/API, update cadence, "
                    "and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Polk County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/polk/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Polk County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/polk/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Polk "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Poinsett":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Poinsett County"
                directory_url = "https://www.arcounties.org/counties/poinsett/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Poinsett&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Poinsett County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Poinsett County official website"
                directory_url = "https://www.poinsettar.gov/"
                source_url = directory_url
                note += (
                    " The Association-listed County website returned "
                    "only a template instruction to copy/paste a link, "
                    "not usable County services or records. No "
                    "property-level code-enforcement service or feed "
                    "was identified; countywide coverage, municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Poinsett County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/poinsett/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Poinsett County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/poinsett/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Poinsett "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Pike":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Pike County"
                directory_url = "https://www.arcounties.org/counties/pike/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Pike&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Pike County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Pike County official website"
                directory_url = "https://pikecountyar.org/"
                source_url = directory_url
                note += (
                    " The official County website returned general "
                    "county history and stated that quick links provide "
                    "official contacts and other links; no property-level "
                    "code-enforcement service or feed was exposed. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Pike County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/pike/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Pike County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/pike/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Pike "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Phillips":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Phillips County"
                directory_url = "https://www.arcounties.org/counties/phillips/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Phillips&s=R"
                )
                note += (
                    " The Association profile lists the County Assessor "
                    "contact but is an office directory, not parcel "
                    "records. The county-specific ARCountyData page is "
                    "explicitly a free Collector tax-record/receipt "
                    "search, not an Assessor valuation search. No "
                    "verified Assessor property portal, feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Phillips County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Phillips County"
                directory_url = "https://www.arcounties.org/counties/phillips/"
                source_url = directory_url
                note += (
                    " The Association profile is an office-contact and "
                    "county-background page, not a property-level "
                    "code-enforcement service. No countywide violation "
                    "feed was identified; municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Phillips County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/phillips/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Phillips County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/phillips/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Phillips "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Perry":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Perry County"
                directory_url = "https://www.arcounties.org/counties/perry/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Perry&s=R"
                )
                note += (
                    " The Association profile lists the County Assessor "
                    "contact but is an office directory, not parcel "
                    "records. The county-specific ARCountyData page is "
                    "explicitly a free Collector tax-record/receipt "
                    "search, not an Assessor valuation search. No "
                    "verified Assessor property portal, feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Perry County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Perry County official website"
                directory_url = "https://perrycoarkansas.org/"
                source_url = directory_url
                note += (
                    " The official County website returned a County "
                    "Judge message and a general description of county "
                    "government functions, not a property-level "
                    "code-enforcement service. No countywide violation "
                    "feed was identified; municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Perry County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/perry/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Perry County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/perry/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Perry "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Ouachita":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Ouachita County"
                directory_url = "https://www.arcounties.org/counties/ouachita/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Ouachita&s=R"
                )
                note += (
                    " The Association profile lists the County Assessor "
                    "contact but is an office directory, not parcel "
                    "records. The county-specific ARCountyData page is "
                    "explicitly a free Collector tax-record/receipt "
                    "search, not an Assessor valuation search. No "
                    "verified Assessor property portal, feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose an Ouachita County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Ouachita County"
                directory_url = (
                    "https://www.arcounties.org/counties/ouachita/"
                )
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Ouachita County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/ouachita/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Ouachita County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/ouachita/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Ouachita "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Newton":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Newton County"
                directory_url = "https://www.arcounties.org/counties/newton/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Newton&s=R"
                )
                note += (
                    " The county-specific ARCountyData page returned "
                    "general Arkansas homestead-tax information and "
                    "Assessor-office background, but no Assessor-sponsored "
                    "search or parcel results. The Association profile "
                    "provides County background and an address, not "
                    "property records. No verified property-search "
                    "portal, feed/API, refresh cadence, or permission for "
                    "daily commercial extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Newton County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Newton County"
                directory_url = "https://www.arcounties.org/counties/newton/"
                source_url = directory_url
                note += (
                    " The County profile provides background and an "
                    "address, not a property-level code-enforcement "
                    "service. No countywide violation feed was "
                    "identified; municipal providers, export/API, "
                    "update cadence, and permission for automated access "
                    "remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Newton County profile and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/newton/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile exposes no Sheriff sale "
                    "calendar or County-authorized foreclosure feed. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Newton County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/newton/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Newton "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Nevada":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Nevada County"
                directory_url = "https://www.arcounties.org/counties/nevada/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Nevada&s=R"
                )
                note += (
                    " The Association profile lists the County Assessor "
                    "contact but is an office directory, not parcel "
                    "records. The county-specific ARCountyData page is "
                    "explicitly a free Collector tax-record/receipt "
                    "search, not an Assessor valuation search. No "
                    "verified Assessor property portal, feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Nevada County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Nevada County"
                directory_url = "https://www.arcounties.org/counties/nevada/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Nevada County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/nevada/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Nevada County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/nevada/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Nevada "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Montgomery":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Montgomery County"
                directory_url = "https://www.arcounties.org/counties/montgomery/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Montgomery&s=R"
                )
                note += (
                    " The Association profile provides County background "
                    "and an address but no Assessor contact or parcel "
                    "records. The county-specific ARCountyData page is "
                    "explicitly a free Collector tax-record/receipt "
                    "search, not an Assessor valuation search. No "
                    "verified Assessor property portal, feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Montgomery "
                    "County-specific current sale date/list or "
                    "machine-readable feed; update cadence and "
                    "permission for daily/commercial automation were "
                    "not verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Association of Arkansas Counties | Montgomery County"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/montgomery/"
                )
                source_url = directory_url
                note += (
                    " The County profile is a county-background page, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Montgomery County profile and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/montgomery/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile exposes no Sheriff sale "
                    "calendar or County-authorized foreclosure feed. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Montgomery County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/montgomery/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Montgomery "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Monroe":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Monroe County"
                directory_url = "https://www.arcounties.org/counties/monroe/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Monroe&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Monroe County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Monroe County"
                directory_url = "https://www.arcounties.org/counties/monroe/"
                source_url = directory_url
                note += (
                    " The County profile provides general County "
                    "background and contact information, not a "
                    "property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Monroe County profile and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/monroe/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile provides no Sheriff sale "
                    "calendar or County-authorized foreclosure feed. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Monroe County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/monroe/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Monroe "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Mississippi":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Mississippi County"
                directory_url = "https://www.arcounties.org/counties/mississippi/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Mississippi&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Mississippi "
                    "County-specific current sale date/list or "
                    "machine-readable feed; update cadence and "
                    "permission for daily/commercial automation were "
                    "not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Mississippi County"
                directory_url = (
                    "https://www.arcounties.org/counties/mississippi/"
                )
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Mississippi County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/mississippi/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Mississippi County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/mississippi/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no "
                    "Mississippi County-specific default/lis-pendens "
                    "feed, bulk export/API, update cadence, or permission "
                    "for daily automated access was verified. "
                    "County-level filing coverage remains unconfirmed; "
                    "foreclosure-sale notices are not pre-foreclosure "
                    "records."
                )
        if state == "AR" and county_name == "Miller":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Miller County"
                directory_url = "https://www.arcounties.org/counties/miller/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Miller&s=R"
                )
                note += (
                    " The Association profile lists the County Assessor "
                    "contact but is an office directory, not parcel "
                    "records. The county-specific ARCountyData page is "
                    "explicitly a free Collector tax-record/receipt "
                    "search, not an Assessor valuation search. No "
                    "verified Assessor property portal, feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Miller County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Miller County"
                directory_url = "https://www.arcounties.org/counties/miller/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Miller County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/miller/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Miller County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/miller/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Miller "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Marion":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Marion County"
                directory_url = "https://www.arcounties.org/counties/marion/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Marion&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Marion County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Marion County"
                directory_url = "https://www.arcounties.org/counties/marion/"
                source_url = directory_url
                note += (
                    " The Association profile lists the County domain, "
                    "but that County website returned HTTP 403 in this "
                    "check. The Association page is an office directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Marion County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/marion/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Marion County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/marion/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Marion "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Madison":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Madison County"
                directory_url = "https://www.arcounties.org/counties/madison/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Madison&s=R"
                )
                note += (
                    " The Association profile links the County website "
                    "but is not parcel records. The county-specific "
                    "ARCountyData URL redirected to its generic welcome "
                    "page; no Madison-specific property search was "
                    "exposed. No verified Assessor portal, feed/API, "
                    "update cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Madison County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Madison County official website"
                directory_url = "https://madisoncountyar.gov/"
                source_url = directory_url
                note += (
                    " The Association-listed domain redirects to this "
                    "County website, which returned only an alert "
                    "placeholder in this check. No property-level "
                    "code-enforcement service or feed was identified; "
                    "countywide coverage, municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Madison County profile and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/madison/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile and County website "
                    "exposed no Sheriff sale calendar or "
                    "County-authorized foreclosure feed. Arkansas Public "
                    "Notices offers newspaper foreclosure notices "
                    "searchable by county, but is not the official "
                    "publication, does not include notices from every "
                    "newspaper, and its Terms limit use to personal, "
                    "non-commercial purposes and prohibit copying or "
                    "replication. Written permission is required before "
                    "commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Madison County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/madison/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Madison "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Lonoke":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Lonoke County"
                directory_url = "https://www.arcounties.org/counties/lonoke/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Lonoke&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Lonoke County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Lonoke County"
                directory_url = "https://www.arcounties.org/counties/lonoke/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Lonoke County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/lonoke/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Lonoke County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/lonoke/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Lonoke "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Logan":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Logan County"
                directory_url = "https://www.arcounties.org/counties/logan/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Logan&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Logan County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Logan County official website"
                directory_url = "https://logancountyark.org/"
                source_url = directory_url
                note += (
                    " The County website returned addresses for the "
                    "Paris and Booneville courthouses only; no "
                    "property-level code-enforcement service or feed "
                    "was identified. Countywide coverage, municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Logan County profile and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/logan/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile exposes no Sheriff sale "
                    "calendar or County-authorized foreclosure feed. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Logan County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/logan/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Logan "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Little River":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Little River County"
                directory_url = "https://www.arcounties.org/counties/little-river/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Little%20River&s=R"
                )
                note += (
                    " The Association profile lists the County Assessor "
                    "contact but is an office directory, not parcel "
                    "records. The county-specific ARCountyData page is "
                    "explicitly a free Collector tax-record/receipt "
                    "search, not an Assessor valuation search. No "
                    "verified Assessor property portal, feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Little River "
                    "County-specific current sale date/list or "
                    "machine-readable feed; update cadence and "
                    "permission for daily/commercial automation were "
                    "not verified."
                )
            elif category == "code_enforcement":
                directory_name = (
                    "Association of Arkansas Counties | Little River County"
                )
                directory_url = "https://www.arcounties.org/counties/little-river/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Little River County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/little-river/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Little River County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/little-river/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Little "
                    "River County-specific default/lis-pendens feed, "
                    "bulk export/API, update cadence, or permission for "
                    "daily automated access was verified. County-level "
                    "filing coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Lincoln":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Lincoln County"
                directory_url = "https://www.arcounties.org/counties/lincoln/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Lincoln&s=R"
                )
                note += (
                    " The Association profile provides County background "
                    "and an address but no Assessor contact or parcel "
                    "records. The county-specific ARCountyData URL "
                    "redirected to its generic welcome page; no "
                    "Lincoln-specific property search was exposed. No "
                    "verified Assessor portal, feed/API, update cadence, "
                    "or permission for daily commercial extraction was "
                    "identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Lincoln County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Lincoln County"
                directory_url = "https://www.arcounties.org/counties/lincoln/"
                source_url = directory_url
                note += (
                    " The County profile is a county-background page, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Lincoln County profile and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/lincoln/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile exposes no Sheriff sale "
                    "calendar or County-authorized foreclosure feed. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Lincoln County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/lincoln/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Lincoln "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Lee":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Lee County"
                directory_url = "https://www.arcounties.org/counties/lee/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Lee&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Lee County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Lee County"
                directory_url = "https://www.arcounties.org/counties/lee/"
                source_url = directory_url
                note += (
                    " The County profile is a county-background and "
                    "contact page, not a property-level code-enforcement "
                    "service. No countywide violation feed was "
                    "identified; municipal providers, export/API, "
                    "update cadence, and permission for automated access "
                    "remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Lee County profile and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/lee/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile exposes no Sheriff sale "
                    "calendar or County-authorized foreclosure feed. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Lee County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/lee/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Lee "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Lawrence":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Lawrence County"
                directory_url = "https://www.arcounties.org/counties/lawrence/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Lawrence&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Lawrence County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Lawrence County official website"
                directory_url = "https://www.lawrencecountyarkansas.com/"
                source_url = directory_url
                note += (
                    " The Association-listed County website returned a "
                    "message that it is undergoing changes; no "
                    "property-level code-enforcement service or feed "
                    "was identified. Countywide coverage, municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Lawrence County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/lawrence/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Lawrence County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/lawrence/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Lawrence "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Lafayette":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Lafayette County"
                directory_url = "https://www.arcounties.org/counties/lafayette/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Lafayette&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Lafayette County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Arkansas State Portal | Lafayette County"
                directory_url = "https://portal.arkansas.gov/counties/lafayette/"
                source_url = directory_url
                note += (
                    " The Association-listed County URL redirects to "
                    "this State Portal page, which returned only the "
                    "courthouse location in this check. No property-level "
                    "code-enforcement service or feed was identified; "
                    "countywide coverage, municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Lafayette County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/lafayette/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists the Sheriff and "
                    "contact details but no sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Lafayette County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/lafayette/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Lafayette "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Johnson":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Johnson County"
                directory_url = "https://www.arcounties.org/counties/johnson/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Johnson&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Johnson County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Johnson County"
                directory_url = "https://www.arcounties.org/counties/johnson/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Johnson County profile and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/johnson/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile provides County contact "
                    "information but no sale calendar or County-authorized "
                    "foreclosure feed was verified. Arkansas Public "
                    "Notices offers newspaper foreclosure notices "
                    "searchable by county, but is not the official "
                    "publication, does not include notices from every "
                    "newspaper, and its Terms limit use to personal, "
                    "non-commercial purposes and prohibit copying or "
                    "replication. Written permission is required before "
                    "commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Johnson County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/johnson/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Johnson "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Jefferson":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Jefferson County"
                directory_url = "https://www.arcounties.org/counties/jefferson/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Jefferson&s=R"
                )
                note += (
                    " The county-specific ARCountyData page is explicitly "
                    "a free County Clerk marriage-record search, not "
                    "Assessor valuation data. The Association profile "
                    "lists the Assessor office contact but is not parcel "
                    "records. No verified property assessment search, "
                    "Assessor feed/API, update cadence, or permission for "
                    "daily commercial extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Jefferson County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Jefferson County"
                directory_url = "https://www.arcounties.org/counties/jefferson/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Jefferson County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/jefferson/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Jefferson County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/jefferson/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Jefferson "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Jackson":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Jackson County"
                directory_url = "https://www.arcounties.org/counties/jackson/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Jackson&s=R"
                )
                note += (
                    " The county-specific ARCountyData page is explicitly "
                    "a free County Clerk marriage-record search, not "
                    "Assessor valuation data. The County website provides "
                    "general county and tourism information but no "
                    "property assessment search. No verified Assessor "
                    "portal, feed/API, update cadence, or permission for "
                    "daily commercial extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Jackson County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Jackson County official website"
                directory_url = "https://jacksoncountyar.com/"
                source_url = directory_url
                note += (
                    " The official County site returned general history "
                    "and community information; no property-level "
                    "code-enforcement service or feed was identified. "
                    "Countywide coverage, municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Jackson County profile and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/jackson/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile exposes no Sheriff sale "
                    "calendar or County-authorized foreclosure feed. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Jackson County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/jackson/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Jackson "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Izard":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Izard County"
                directory_url = "https://www.arcounties.org/counties/izard/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Izard&s=R"
                )
                note += (
                    " The county-specific ARCountyData page shows an "
                    "empty property-search area with a paid-user login, "
                    "not a public Assessor search. It reports 32,120 "
                    "parcels, Assessor data last updated 10/20/2022, and "
                    "Collector data last updated 1/27/2022. The linked "
                    "County website could not be retrieved. The displayed "
                    "data dates are stale; no verified current Assessor "
                    "portal, feed/API, refresh cadence, or permission for "
                    "daily commercial extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose an Izard County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Izard County official website"
                directory_url = "https://izardcountyar.org/"
                source_url = directory_url
                note += (
                    " The Association-linked County website could not "
                    "be retrieved in this check. No property-level "
                    "code-enforcement service or feed was verified; "
                    "countywide coverage, municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Izard County profile and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/izard/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile exposes no Sheriff sale "
                    "calendar or County-authorized foreclosure feed. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Izard County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/izard/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Izard "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Independence":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Independence County"
                directory_url = "https://www.arcounties.org/counties/independence/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Independence&s=R"
                )
                note += (
                    " The Association profile lists the County Assessor "
                    "contact but is an office directory, not parcel "
                    "records. The county-specific ARCountyData URL "
                    "redirected to its generic welcome page; no "
                    "Independence-specific property search was exposed. "
                    "No verified Assessor portal, feed/API, update "
                    "cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose an Independence "
                    "County-specific current sale date/list or "
                    "machine-readable feed; update cadence and "
                    "permission for daily/commercial automation were "
                    "not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Independence County"
                directory_url = "https://www.arcounties.org/counties/independence/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Independence County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/independence/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Independence County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/independence/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no "
                    "Independence County-specific default/lis-pendens "
                    "feed, bulk export/API, update cadence, or permission "
                    "for daily automated access was verified. "
                    "County-level filing coverage remains unconfirmed; "
                    "foreclosure-sale notices are not pre-foreclosure "
                    "records."
                )
        if state == "AR" and county_name == "Howard":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Howard County"
                directory_url = "https://www.arcounties.org/counties/howard/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Howard&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Howard County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Howard County"
                directory_url = "https://www.arcounties.org/counties/howard/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Howard County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/howard/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Howard County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/howard/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Howard "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Hot Spring":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Hot Spring County"
                directory_url = "https://www.arcounties.org/counties/hot-spring/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Hot%20Spring&s=R"
                )
                note += (
                    " The county-specific ARCountyData page is explicitly "
                    "a free County Clerk marriage-record search, not "
                    "Assessor valuation data. The Association profile and "
                    "linked County website provide background information "
                    "but no property assessment search. No verified "
                    "Assessor portal, feed/API, update cadence, or "
                    "permission for daily commercial extraction was "
                    "identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Hot Spring "
                    "County-specific current sale date/list or "
                    "machine-readable feed; update cadence and "
                    "permission for daily/commercial automation were "
                    "not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Hot Spring County official website"
                directory_url = "https://hotspringcounty.org/"
                source_url = directory_url
                note += (
                    " The linked County website returned county-history "
                    "information only; no property-level "
                    "code-enforcement service or feed was identified. "
                    "Countywide coverage, municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Hot Spring County profile and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/hot-spring/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile exposes no Sheriff sale "
                    "calendar or County-authorized foreclosure feed. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Hot Spring County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/hot-spring/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Hot Spring "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Hempstead":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Hempstead County"
                directory_url = "https://www.arcounties.org/counties/hempstead/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Hempstead&s=R"
                )
                note += (
                    " The county-specific ARCountyData page explicitly "
                    "labels its free search as Collector tax records and "
                    "receipts, not Assessor valuation data. The "
                    "Association profile lists a county address but "
                    "links to garlandcounty.org, which resolves to a "
                    "Garland County resources page rather than a "
                    "Hempstead County site. No verified Hempstead "
                    "Assessor portal, feed/API, update cadence, or "
                    "permission for daily commercial extraction was "
                    "identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Hempstead "
                    "County-specific current sale date/list or "
                    "machine-readable feed; update cadence and "
                    "permission for daily/commercial automation were "
                    "not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Hempstead County"
                directory_url = "https://www.arcounties.org/counties/hempstead/"
                source_url = directory_url
                note += (
                    " The County profile is a directory/background page, "
                    "not a property-level code-enforcement service, and "
                    "its website link resolves to Garland County rather "
                    "than Hempstead County. No countywide violation "
                    "feed was identified; municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Hempstead County profile and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/hempstead/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile exposes no Hempstead "
                    "Sheriff sale calendar or County-authorized "
                    "foreclosure feed and its website link is for "
                    "Garland County. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Hempstead County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/hempstead/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Hempstead "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Greene":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Greene County"
                directory_url = "https://www.arcounties.org/counties/greene/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Greene&s=R"
                )
                note += (
                    " The ARCountyData county-specific page returned "
                    "general Arkansas homestead-tax information and "
                    "Assessor-office background, but no Assessor-sponsored "
                    "search or parcel results. The County website's "
                    "tax-information page provides due-date and "
                    "partial-payment guidance, not parcel assessment "
                    "records. No verified property-search portal, "
                    "feed/API, refresh cadence, or permission for daily "
                    "commercial extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Greene County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Greene County official website"
                directory_url = "https://greenecounty.arkansas.gov/"
                source_url = directory_url
                note += (
                    " The County website returned general county and "
                    "tax-payment information; no property-level "
                    "code-enforcement service or feed was identified. "
                    "Countywide coverage, municipal providers, "
                    "export/API, update cadence, and permission for "
                    "automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Greene County offices and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/greene/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile and County website "
                    "provided no Sheriff sale calendar or "
                    "County-authorized foreclosure feed. Arkansas Public "
                    "Notices offers newspaper foreclosure notices "
                    "searchable by county, but is not the official "
                    "publication, does not include notices from every "
                    "newspaper, and its Terms limit use to personal, "
                    "non-commercial purposes and prohibit copying or "
                    "replication. Written permission is required before "
                    "commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Greene County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/greene/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Greene "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Grant":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Grant County"
                directory_url = "https://www.arcounties.org/counties/grant/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Grant&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Grant County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Grant County official website"
                directory_url = "https://grantcountyar.com/"
                source_url = directory_url
                note += (
                    " The Association-listed official County website "
                    "returned a county-history introduction; no "
                    "property-level code-enforcement service or feed "
                    "was identified. Countywide coverage, municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Grant County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/grant/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Grant County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/grant/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Grant "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Garland":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Garland County"
                directory_url = "https://www.arcounties.org/counties/garland/"
                source_url = directory_url
                note += (
                    " The Association profile lists the County Assessor "
                    "contact but is an office directory, not parcel "
                    "records. The county-specific ARCountyData URL "
                    "redirected to its generic welcome page; no "
                    "Garland-specific property search was exposed. No "
                    "verified Assessor portal, feed/API, update cadence, "
                    "or permission for daily commercial extraction was "
                    "identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Garland County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Garland County"
                directory_url = "https://www.arcounties.org/counties/garland/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Garland County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/garland/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Garland County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/garland/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Garland "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Fulton":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Fulton County"
                directory_url = "https://www.arcounties.org/counties/fulton/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Fulton&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Fulton County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Fulton County official website"
                directory_url = "https://www.fultoncountyar.gov/"
                source_url = directory_url
                note += (
                    " The Association lists this County domain, but it "
                    "could not be retrieved in this check. No "
                    "property-level code-enforcement service or feed "
                    "was verified; countywide coverage, municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Fulton County offices and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/fulton/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile provides County contact "
                    "information but no Sheriff sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Fulton County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/fulton/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Fulton "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Franklin":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Franklin County"
                directory_url = "https://www.arcounties.org/counties/franklin/"
                source_url = directory_url
                note += (
                    " The Association profile lists the County Assessor "
                    "contact but is an office directory, not parcel "
                    "records. The county-specific ARCountyData URL "
                    "redirected to its generic welcome page; no "
                    "Franklin-specific property search was exposed. No "
                    "verified Assessor portal, feed/API, update cadence, "
                    "or permission for daily commercial extraction was "
                    "identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Franklin County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Franklin County"
                directory_url = "https://www.arcounties.org/counties/franklin/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Franklin County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/franklin/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Franklin County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/franklin/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Franklin "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Faulkner":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Faulkner County"
                directory_url = "https://www.arcounties.org/counties/faulkner/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Faulkner&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Faulkner County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Faulkner County official website"
                directory_url = "https://www.faulknercountyar.gov/"
                source_url = directory_url
                note += (
                    " The official County site redirected from the "
                    "Association-listed domain and returned only a "
                    "courthouse-closure announcement in this check; no "
                    "property-level code-enforcement service or feed "
                    "was identified. Countywide coverage, municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Faulkner County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/faulkner/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists the Sheriff and "
                    "contact details but no sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Faulkner County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/faulkner/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Faulkner "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Drew":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Drew County"
                directory_url = "https://www.arcounties.org/counties/drew/"
                source_url = directory_url
                note += (
                    " The Association profile provides county background "
                    "and an address but no Assessor contact or parcel "
                    "records. The county-specific ARCountyData URL "
                    "redirected to its generic welcome page; no "
                    "Drew-specific property search was exposed. No "
                    "verified Assessor portal, feed/API, update cadence, "
                    "or permission for daily commercial extraction was "
                    "identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Drew County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Drew County"
                directory_url = "https://www.arcounties.org/counties/drew/"
                source_url = directory_url
                note += (
                    " The County profile is a county-background page, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Drew County offices and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/drew/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile exposed no County Sheriff "
                    "sale calendar or County-authorized foreclosure feed. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Drew County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/drew/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Drew "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Cross":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Cross County"
                directory_url = "https://www.arcounties.org/counties/cross/"
                source_url = directory_url
                note += (
                    " The Association profile lists the County Assessor "
                    "contact and county website, but is an office "
                    "directory, not parcel records. The county-specific "
                    "ARCountyData URL redirected to its generic welcome "
                    "page; no Cross-specific property search was exposed. "
                    "The listed county website could not be retrieved "
                    "during this check. No verified Assessor feed/API, "
                    "update cadence, or permission for daily commercial "
                    "extraction was identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Cross County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Cross County"
                directory_url = "https://www.arcounties.org/counties/cross/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified. "
                    "The linked County website could not be retrieved "
                    "during this check."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Cross County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/cross/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Cross County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/cross/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Cross "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Crawford":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Crawford County"
                directory_url = "https://www.arcounties.org/counties/crawford/"
                source_url = directory_url
                note += (
                    " The Association profile lists the County Assessor "
                    "contact but is an office directory, not parcel "
                    "records. The county-specific ARCountyData page is "
                    "explicitly a Collector tax-record/receipt search, "
                    "not an Assessor valuation search. No verified "
                    "Assessor property portal, feed/API, update cadence, "
                    "or permission for daily commercial extraction was "
                    "identified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Crawford County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Crawford County"
                directory_url = "https://www.arcounties.org/counties/crawford/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Crawford County offices and Arkansas Public Notices"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/crawford/"
                )
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile is an office directory; "
                    "no Crawford County Sheriff sale calendar or "
                    "County-authorized foreclosure feed was verified. "
                    "Arkansas Public Notices offers newspaper "
                    "foreclosure notices searchable by county, but is "
                    "not the official publication, does not include "
                    "notices from every newspaper, and its Terms limit "
                    "use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written "
                    "permission is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Crawford County offices and Arkansas Judiciary Case Search"
                )
                directory_url = (
                    "https://www.arcounties.org/counties/crawford/"
                )
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Crawford "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Dallas":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Dallas County"
                directory_url = "https://www.arcounties.org/counties/dallas/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Dallas&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Dallas County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Dallas County"
                directory_url = "https://www.arcounties.org/counties/dallas/"
                source_url = directory_url
                note += (
                    " The County profile provides an overview and "
                    "contact but no property-level code-enforcement "
                    "service. No countywide violation feed was "
                    "identified; municipal providers, export/API, update "
                    "cadence, and permission for automated access remain "
                    "unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Dallas County offices and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/dallas/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile provides no Sheriff sale "
                    "calendar or foreclosure feed. Arkansas Public "
                    "Notices offers newspaper foreclosure notices "
                    "searchable by county, but is not the official "
                    "publication, does not include notices from every "
                    "newspaper, and its Terms limit use to personal, "
                    "non-commercial purposes and prohibit copying or "
                    "replication. Written permission is required before "
                    "commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Dallas County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/dallas/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Dallas "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AR" and county_name == "Desha":
            if category == "assessor":
                directory_name = "Association of Arkansas Counties | Desha County"
                directory_url = "https://www.arcounties.org/counties/desha/"
                source_url = (
                    "https://www.arcountydata.com/county.asp?"
                    "county=Desha&s=R"
                )
                note += (
                    " The county-specific ARCountyData page says the "
                    "Assessor sponsors a free public property-record "
                    "search. This is an interactive third-party portal, "
                    "not a documented daily feed. The vendor's terms "
                    "describe parcel data as assessor working papers and "
                    "restrict copying/reproducing proprietary material "
                    "without express written consent. No feed/API, "
                    "refresh cadence, or permission for commercial daily "
                    "extraction was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Arkansas Commissioner of State Lands real-estate sales"
                )
                directory_url = "https://cosl.org/Home/RealEstate"
                source_url = "https://cosl.org/Home/Contents"
                note += (
                    " The State Land Office conducts public auctions of "
                    "delinquent property certified to the State and "
                    "publishes a statewide auction catalog. The "
                    "retrieval did not expose a Desha County-specific "
                    "current sale date/list or machine-readable feed; "
                    "update cadence and permission for daily/commercial "
                    "automation were not verified."
                )
            elif category == "code_enforcement":
                directory_name = "Association of Arkansas Counties | Desha County"
                directory_url = "https://www.arcounties.org/counties/desha/"
                source_url = directory_url
                note += (
                    " The County profile is an office-contact directory, "
                    "not a property-level code-enforcement service. No "
                    "countywide violation feed was identified; municipal "
                    "providers, export/API, update cadence, and "
                    "permission for automated access remain unverified."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Desha County Sheriff contacts and Arkansas Public Notices"
                )
                directory_url = "https://www.arcounties.org/counties/desha/"
                source_url = "https://www.arkansaspublicnotices.com/"
                note += (
                    " The Association profile lists Sheriff contacts but "
                    "no sale calendar or County-authorized foreclosure "
                    "feed was verified. Arkansas Public Notices offers "
                    "newspaper foreclosure notices searchable by county, "
                    "but is not the official publication, does not "
                    "include notices from every newspaper, and its Terms "
                    "limit use to personal, non-commercial purposes and "
                    "prohibit copying or replication. Written permission "
                    "is required before commercial ingestion."
                )
            elif category == "pre_foreclosure":
                directory_name = (
                    "Desha County offices and Arkansas Judiciary Case Search"
                )
                directory_url = "https://www.arcounties.org/counties/desha/"
                source_url = "https://caseinfo.arcourts.gov/opad"
                note += (
                    " The official statewide Case Search page returned "
                    "general navigation tips in this check; no Desha "
                    "County-specific default/lis-pendens feed, bulk "
                    "export/API, update cadence, or permission for daily "
                    "automated access was verified. County-level filing "
                    "coverage remains unconfirmed; foreclosure-sale "
                    "notices are not pre-foreclosure records."
                )
        if state == "AL" and county_name == "Winston":
            if category == "assessor":
                directory_name = "Winston County ISV3 Public GIS"
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Winston"
                )
                source_url = "https://isv.kcsgis.com/al.winston_revenue/"
                note += (
                    " The DOR county-office directory links this ISV3 "
                    "Public GIS route for the Revenue Commissioner. The "
                    "tested page rendered only the 'Winston County ISV3' "
                    "shell; no parcel results, bulk export/API, update "
                    "cadence, or permission for daily/commercial "
                    "automation was verified."
                )
            elif category == "tax_sale":
                directory_name = (
                    "Winston County Revenue Commissioner and DOR transcript"
                )
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Winston"
                )
                source_url = (
                    "https://www.revenue.alabama.gov/wp-content/uploads/"
                    "property-tax-transcripts/WWW_TRANS_67.PDF"
                )
                note += (
                    " The DOR county-office entry provides the Revenue "
                    "Commissioner's office contact and GIS link, but no "
                    "County sale date, delinquent parcel list, or auction "
                    "platform. The Winston transcript (WWW_TRANS_67.PDF), "
                    "generated 2026-10-19, is a one-page weekly "
                    "state-held delinquent-land inventory, not the County "
                    "auction calendar, and lacks physical addresses. No "
                    "recurring local sale feed, list cadence, API, or "
                    "permission for daily/commercial automation was "
                    "verified."
                )
            elif category == "code_enforcement":
                directory_name = "Winston County code-enforcement discovery"
                directory_url = (
                    "https://www.revenue.alabama.gov/property-tax/"
                    "county-offices-appraisal-assessment-records/"
                    "#Winston"
                )
                source_url = directory_url
                note += (
                    " The reviewed County and State office pages identify "
                    "no countywide property-level code-enforcement "
                    "provider, violation search, or case feed. No "
                    "municipal provider, export/API, update cadence, or "
                    "permission for automated access was verified; check "
                    "the authority for each property's municipality."
                )
            elif category == "foreclosure":
                directory_name = (
                    "Alabama Sheriffs Association and statewide notices"
                )
                directory_url = (
                    "https://www.alabamasheriffs.com/sheriffsdirectory/"
                )
                source_url = "https://www.alabamapublicnotices.com/"
                note += (
                    " No Winston County Sheriff's sale calendar, "
                    "foreclosure list, or county-authorized notice feed "
                    "was verified. The Alabama Sheriffs Association "
                    "directory is manual office discovery, not a sales "
                    "feed. Alabama Public Notice covers participating "
                    "newspapers only; its Terms prohibit scraping, "
                    "automated collection, and commercial exploitation. "
                    "No authorized daily foreclosure source was verified."
                )
            elif category == "pre_foreclosure":
                directory_name = "Winston County Probate records and portal"
                directory_url = "https://www.winstoncountyprobate.org/"
                source_url = "https://ingprobate.com/Winston_Probate/"
                note += (
                    " The County Probate Office site lists a Records "
                    "Department, but its direct records route redirected "
                    "to the County homepage. The InG portal legal "
                    "disclaimer identifies the Winston County Probate "
                    "Judge and prohibits automated systems, bots, "
                    "spiders, scrapers, offline readers, data extraction, "
                    "automated logins, and interactions. No dedicated "
                    "lis-pendens/default feed, bulk export/API, or "
                    "authorized daily access was verified; use manual "
                    "records research only."
                )
        sources[category] = {
            "status": status,
            "directory_name": directory_name,
            "directory_url": directory_url,
            "source_url": source_url,
            "search_url": (
                "https://www.google.com/search?q=" + quote_plus(search_terms[category])
            ),
            "note": note,
        }
    tested_endpoints = dict(TESTED_STATEWIDE_ENDPOINTS.get(state, {}))
    if county_fips:
        tested_endpoints.update(TESTED_PUBLIC_ENDPOINTS_BY_FIPS.get(county_fips, {}))
    for category, endpoint in tested_endpoints.items():
        sources[category].update(endpoint)
        sources[category]["status"] = "endpoint_tested"
    return sources
