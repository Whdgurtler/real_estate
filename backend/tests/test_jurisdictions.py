import unittest

from app.jurisdictions import (
    ALABAMA_TAX_TRANSCRIPT_CODES,
    county_jurisdictions,
    county_source_links,
)


class PriorityJurisdictionDirectoryTests(unittest.TestCase):
    def test_census_registry_covers_all_priority_county_equivalents(self):
        counties = county_jurisdictions()
        counts = {
            state: sum(county["state"] == state for county in counties)
            for state in ("AL", "AR", "OH", "MO", "TX")
        }

        self.assertEqual(
            counts, {"AL": 67, "AR": 75, "OH": 88, "MO": 115, "TX": 254}
        )
        self.assertEqual(len(counties), 599)
        fips_codes = [county["county_fips"] for county in counties]
        self.assertEqual(len(fips_codes), len(set(fips_codes)))
        self.assertEqual(
            next(county for county in counties if county["county_fips"] == "29510")[
                "county"
            ],
            "St. Louis city",
        )

    def test_every_county_has_source_discovery_links_for_all_requested_categories(self):
        for county in county_jurisdictions():
            with self.subTest(county=county["county_fips"]):
                sources = county_source_links(county["state"], county["county"])
                self.assertEqual(
                    set(sources),
                    {
                        "assessor",
                        "tax_sale",
                        "code_enforcement",
                        "foreclosure",
                        "pre_foreclosure",
                    },
                )
                for source in sources.values():
                    self.assertTrue(
                        source["directory_url"].startswith("https://")
                        or source["directory_url"]
                        in {"http://www.choctawso.com/", "http://clayso.net/"}
                    )
                    self.assertTrue(source["search_url"].startswith("https://www.google.com/"))
                    self.assertTrue(source["note"])
                self.assertEqual(sources["code_enforcement"]["status"], "municipal_scope")
                self.assertEqual(sources["foreclosure"]["status"], "needs_feed_verification")
                self.assertEqual(
                    sources["pre_foreclosure"]["status"], "needs_feed_verification"
                )

    def test_county_source_links_use_state_and_county_specific_paths_when_available(self):
        arkansas = county_source_links("AR", "Pulaski County")
        ohio = county_source_links("OH", "Franklin County")
        alabama = county_source_links("AL", "Jefferson County")
        texas = county_source_links("TX", "Harris County")

        self.assertEqual(
            arkansas["tax_sale"]["source_url"],
            "https://cosl.org/Home/Contents",
        )
        self.assertIn("3,036 parcels in 53 of 75 counties", arkansas["tax_sale"]["note"])
        self.assertEqual(
            arkansas["foreclosure"]["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn(
            "personal, non-commercial purposes",
            arkansas["foreclosure"]["note"],
        )
        self.assertEqual(
            arkansas["assessor"]["source_url"],
            "https://www.arcountydata.com/county.asp?county=Pulaski&s=R",
        )
        self.assertEqual(
            arkansas["assessor"]["directory_url"],
            "https://www.arcounties.org/counties/pulaski/",
        )
        autauga_tax_sale = county_source_links("AL", "Autauga County")[
            "tax_sale"
        ]
        self.assertEqual(
            autauga_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_04.PDF",
        )
        self.assertEqual(
            autauga_tax_sale["directory_url"],
            "https://autauga.capturecama.com/collection",
        )
        self.assertIn("updated weekly", autauga_tax_sale["note"])
        self.assertIn("Prattville Progress for three weeks", autauga_tax_sale["note"])
        self.assertIn("does not post a current sale date or list", autauga_tax_sale["note"])
        self.assertIn(
            "eBuy's FAQ says it is not for delinquent county property-tax sales",
            autauga_tax_sale["note"],
        )
        autauga_foreclosure = county_source_links("AL", "Autauga County")[
            "foreclosure"
        ]
        self.assertEqual(
            autauga_foreclosure["directory_url"],
            "https://www.autaugasheriff.org/",
        )
        self.assertIn(
            "rather than a verifiable foreclosure or sheriff-sale list",
            autauga_foreclosure["note"],
        )
        autauga_pre_foreclosure = county_source_links("AL", "Autauga County")[
            "pre_foreclosure"
        ]
        self.assertEqual(
            autauga_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Autauga_Probate/default.aspx",
        )
        self.assertIn(
            "Terms and Conditions prohibit automated access",
            autauga_pre_foreclosure["note"],
        )
        baldwin_tax_sale = county_source_links("AL", "Baldwin County")["tax_sale"]
        self.assertEqual(
            baldwin_tax_sale["directory_url"],
            "https://baldwincountyal.gov/government/"
            "revenue-commission/tax-lien-auction",
        )
        self.assertIn("tax-year auction", baldwin_tax_sale["note"])
        self.assertIn("held online through GovEase beginning March 24, 2026", baldwin_tax_sale["note"])
        self.assertIn("no 2026 tax-year sale schedule", baldwin_tax_sale["note"])
        baldwin_foreclosure = county_source_links("AL", "Baldwin County")[
            "foreclosure"
        ]
        self.assertEqual(
            baldwin_foreclosure["directory_url"],
            "https://sheriff.baldwincountyal.gov/",
        )
        self.assertIn("personal-property execution sale", baldwin_foreclosure["note"])
        baldwin_pre_foreclosure = county_source_links("AL", "Baldwin County")[
            "pre_foreclosure"
        ]
        self.assertEqual(
            baldwin_pre_foreclosure["directory_url"],
            "https://baldwincountyal.gov/government/probate-office/recording",
        )
        self.assertIn("from 1899 to present", baldwin_pre_foreclosure["note"])
        barbour_tax_sale = county_source_links("AL", "Barbour County")["tax_sale"]
        self.assertEqual(
            barbour_tax_sale["directory_url"],
            "https://barbour.capturecama.com/",
        )
        self.assertIn(
            "does not publish an upcoming tax-sale date or sale list",
            barbour_tax_sale["note"],
        )
        barbour_foreclosure = county_source_links("AL", "Barbour County")[
            "foreclosure"
        ]
        self.assertEqual(
            barbour_foreclosure["directory_url"],
            "https://barbourcountysheriff.org/",
        )
        self.assertIn(
            "no real-estate foreclosure or sheriff-sale calendar/list was verified",
            barbour_foreclosure["note"],
        )
        barbour_pre_foreclosure = county_source_links("AL", "Barbour County")[
            "pre_foreclosure"
        ]
        self.assertEqual(
            barbour_pre_foreclosure["directory_url"],
            "https://www.barbourcountyal.gov/172/Probate-Office",
        )
        self.assertIn(
            "No lis-pendens/default index",
            barbour_pre_foreclosure["note"],
        )
        bibb_tax_sale = county_source_links("AL", "Bibb County")["tax_sale"]
        self.assertEqual(bibb_tax_sale["directory_url"], "https://bibbal.com/")
        self.assertEqual(
            bibb_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_07.PDF",
        )
        self.assertIn(
            "does not publish a county tax-sale date or list",
            bibb_tax_sale["note"],
        )
        bibb_foreclosure = county_source_links("AL", "Bibb County")["foreclosure"]
        self.assertEqual(bibb_foreclosure["directory_url"], "https://bibbal.com/")
        self.assertIn(
            "no real-estate foreclosure or sheriff-sale calendar/list",
            bibb_foreclosure["note"],
        )
        bibb_pre_foreclosure = county_source_links("AL", "Bibb County")[
            "pre_foreclosure"
        ]
        self.assertEqual(
            bibb_pre_foreclosure["directory_url"],
            "https://bibbal.com/the-probate-office/",
        )
        self.assertIn(
            "online records for 1996 to present",
            bibb_pre_foreclosure["note"],
        )
        blount_tax_sale = county_source_links("AL", "Blount County")["tax_sale"]
        self.assertEqual(
            blount_tax_sale["directory_url"],
            "https://www.blountrevenue.com/home/property/tax-lien-auction/",
        )
        self.assertEqual(
            blount_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_08.PDF",
        )
        self.assertIn("scheduled for March 24, 2026", blount_tax_sale["note"])
        self.assertIn("https://altags.com/blount_license/Delinquent.aspx", blount_tax_sale["note"])
        self.assertIn(
            "automated/commercial-use authorization was verified",
            blount_tax_sale["note"],
        )
        blount_foreclosure = county_source_links("AL", "Blount County")[
            "foreclosure"
        ]
        self.assertEqual(
            blount_foreclosure["directory_url"],
            "https://www.blountalsheriff.org/",
        )
        self.assertIn("did not load during verification", blount_foreclosure["note"])
        self.assertIn(
            "No real-estate foreclosure or sheriff-sale calendar/list was verified",
            blount_foreclosure["note"],
        )
        blount_pre_foreclosure = county_source_links("AL", "Blount County")[
            "pre_foreclosure"
        ]
        self.assertEqual(
            blount_pre_foreclosure["directory_url"],
            "https://www.blountcountyalprobate.com/home/"
            "recording-public-records-and-forms/",
        )
        self.assertIn(
            "not a verified lis-pendens/default list",
            blount_pre_foreclosure["note"],
        )
        bullock_tax_sale = county_source_links("AL", "Bullock County")["tax_sale"]
        self.assertEqual(
            bullock_tax_sale["directory_url"],
            "https://bullockcountyalrev.com/faq",
        )
        self.assertEqual(
            bullock_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_09.PDF",
        )
        self.assertIn(
            "beginning with the 2023-2024 tax year",
            bullock_tax_sale["note"],
        )
        self.assertIn(
            "publishes no current sale date or parcel list",
            bullock_tax_sale["note"],
        )
        bullock_foreclosure = county_source_links("AL", "Bullock County")[
            "foreclosure"
        ]
        self.assertEqual(
            bullock_foreclosure["directory_url"],
            "https://bullockal.com/sheriff/",
        )
        self.assertIn(
            "no real-estate foreclosure or sheriff-sale calendar/list",
            bullock_foreclosure["note"],
        )
        bullock_pre_foreclosure = county_source_links("AL", "Bullock County")[
            "pre_foreclosure"
        ]
        self.assertEqual(
            bullock_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/bullock_probate/default.aspx",
        )
        self.assertIn(
            "prohibits automated systems",
            bullock_pre_foreclosure["note"],
        )
        butler_tax_sale = county_source_links("AL", "Butler County")["tax_sale"]
        self.assertEqual(
            butler_tax_sale["directory_url"],
            "https://www.butlercogov.com/revenue-commission",
        )
        self.assertEqual(
            butler_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_10.PDF",
        )
        self.assertIn("August 26, 2020", butler_tax_sale["note"])
        self.assertIn("publishes no current auction date", butler_tax_sale["note"])
        butler_foreclosure = county_source_links("AL", "Butler County")[
            "foreclosure"
        ]
        self.assertEqual(
            butler_foreclosure["directory_url"],
            "https://web.butlersheriff.org:8443/search.aspx",
        )
        self.assertIn("the next tax sale as October 29, 2026", butler_foreclosure["note"])
        self.assertIn(
            "Treat as manual research only",
            butler_foreclosure["note"],
        )
        butler_pre_foreclosure = county_source_links("AL", "Butler County")[
            "pre_foreclosure"
        ]
        self.assertEqual(
            butler_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/butler_probate/",
        )
        self.assertIn(
            "prohibits automated systems",
            butler_pre_foreclosure["note"],
        )
        calhoun_tax_sale = county_source_links("AL", "Calhoun County")["tax_sale"]
        self.assertEqual(
            calhoun_tax_sale["directory_url"],
            "https://www.calhouncounty.org/revenue/",
        )
        self.assertEqual(
            calhoun_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_11.PDF",
        )
        self.assertIn(
            "https://altags.com/calhoun_revenue/Delinquent.aspx",
            calhoun_tax_sale["note"],
        )
        self.assertIn(
            "was not accessed; its current inventory",
            calhoun_tax_sale["note"],
        )
        calhoun_foreclosure = county_source_links("AL", "Calhoun County")[
            "foreclosure"
        ]
        self.assertEqual(
            calhoun_foreclosure["directory_url"],
            "https://www.calcoso.org/sale-of-property/",
        )
        self.assertIn(
            "publishes no current sale date or list",
            calhoun_foreclosure["note"],
        )
        calhoun_pre_foreclosure = county_source_links("AL", "Calhoun County")[
            "pre_foreclosure"
        ]
        self.assertEqual(
            calhoun_pre_foreclosure["directory_url"],
            "https://www.calhouncounty.org/probate/",
        )
        self.assertIn(
            "redirected to a sign-in requiring cookies",
            calhoun_pre_foreclosure["note"],
        )
        chambers_tax_sale = county_source_links("AL", "Chambers County")[
            "tax_sale"
        ]
        self.assertEqual(
            chambers_tax_sale["directory_url"],
            "https://www.chamberscountyrevenue.com/home/news/",
        )
        self.assertEqual(
            chambers_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_12.PDF",
        )
        self.assertIn("April 28, 2025", chambers_tax_sale["note"])
        self.assertIn(
            "https://www.ingproperty.com/Chambers_Revenue/Delinquent.aspx",
            chambers_tax_sale["note"],
        )
        chambers_foreclosure = county_source_links("AL", "Chambers County")[
            "foreclosure"
        ]
        self.assertEqual(
            chambers_foreclosure["directory_url"],
            "https://www.chamberscountyal.gov/departments/"
            "sheriffs-department",
        )
        self.assertIn(
            "publishes no property-sale or foreclosure calendar/list",
            chambers_foreclosure["note"],
        )
        chambers_pre_foreclosure = county_source_links("AL", "Chambers County")[
            "pre_foreclosure"
        ]
        self.assertEqual(
            chambers_pre_foreclosure["directory_url"],
            "https://www.chamberscountyal.gov/departments/"
            "probate-office/recording-public-records",
        )
        self.assertIn(
            "no public record search or lis-pendens/default index",
            chambers_pre_foreclosure["note"],
        )
        cherokee_tax_sale = county_source_links("AL", "Cherokee County")[
            "tax_sale"
        ]
        self.assertEqual(
            cherokee_tax_sale["directory_url"],
            "https://cherokeepropertytax.com/online-tax-lien-sale-faq/",
        )
        self.assertEqual(
            cherokee_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_13.PDF",
        )
        self.assertIn("April 30, 2026", cherokee_tax_sale["note"])
        self.assertIn("no 2027 date or current auction list was found", cherokee_tax_sale["note"])
        self.assertIn(
            "not verified as the auction list",
            cherokee_tax_sale["note"],
        )
        cherokee_foreclosure = county_source_links("AL", "Cherokee County")[
            "foreclosure"
        ]
        self.assertEqual(
            cherokee_foreclosure["directory_url"],
            "https://www.cherokeecountyalsheriff.com/auctions-and-sales",
        )
        self.assertIn(
            "direct HTTP/HTTPS requests failed at the transport level",
            cherokee_foreclosure["note"],
        )
        self.assertIn(
            "official status and contents could not be verified",
            cherokee_foreclosure["note"],
        )
        cherokee_pre_foreclosure = county_source_links(
            "AL", "Cherokee County"
        )["pre_foreclosure"]
        self.assertEqual(
            cherokee_pre_foreclosure["directory_url"],
            "https://cherokeecounty-al.gov/probate-office/",
        )
        self.assertIn(
            "Terms of Service requiring acceptance",
            cherokee_pre_foreclosure["note"],
        )
        self.assertIn(
            "$0.25 per page",
            cherokee_pre_foreclosure["note"],
        )
        self.assertIn(
            "no lis-pendens/default index",
            cherokee_pre_foreclosure["note"],
        )
        chilton_tax_sale = county_source_links("AL", "Chilton County")[
            "tax_sale"
        ]
        self.assertEqual(
            chilton_tax_sale["directory_url"],
            "https://www.chiltoncountyrevenue.com/home/news/main/",
        )
        self.assertEqual(
            chilton_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_14.PDF",
        )
        self.assertIn("no current sale date or parcel list was found", chilton_tax_sale["note"])
        self.assertIn(
            "No machine-readable feed",
            chilton_tax_sale["note"],
        )
        chilton_foreclosure = county_source_links("AL", "Chilton County")[
            "foreclosure"
        ]
        self.assertEqual(
            chilton_foreclosure["directory_url"],
            "https://www.chiltoncountyso.org/",
        )
        self.assertIn(
            "direct navigation redirected to HTTPS and timed out",
            chilton_foreclosure["note"],
        )
        chilton_pre_foreclosure = county_source_links(
            "AL", "Chilton County"
        )["pre_foreclosure"]
        self.assertEqual(
            chilton_pre_foreclosure["directory_url"],
            "https://chiltoncounty.org/probate-office/",
        )
        self.assertIn(
            "requests on its standard form in person",
            chilton_pre_foreclosure["note"],
        )
        self.assertIn(
            "prohibit robots, spiders, and automated monitoring/copying",
            chilton_pre_foreclosure["note"],
        )
        choctaw_tax_sale = county_source_links("AL", "Choctaw County")[
            "tax_sale"
        ]
        self.assertEqual(
            choctaw_tax_sale["directory_url"],
            "https://www.choctawcountyal.org/revenue-commissioner/",
        )
        self.assertEqual(
            choctaw_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_15.PDF",
        )
        self.assertIn(
            "current sale information could not be verified",
            choctaw_tax_sale["note"],
        )
        choctaw_foreclosure = county_source_links("AL", "Choctaw County")[
            "foreclosure"
        ]
        self.assertEqual(
            choctaw_foreclosure["directory_url"],
            "http://www.choctawso.com/",
        )
        self.assertIn(
            "no sale or foreclosure calendar/list",
            choctaw_foreclosure["note"],
        )
        choctaw_pre_foreclosure = county_source_links(
            "AL", "Choctaw County"
        )["pre_foreclosure"]
        self.assertEqual(
            choctaw_pre_foreclosure["directory_url"],
            "https://www.choctawcountyal.org/probate-judge/",
        )
        self.assertIn(
            "could not be loaded to confirm the portal relationship",
            choctaw_pre_foreclosure["note"],
        )
        self.assertIn(
            "automated-use permissions were not verified",
            choctaw_pre_foreclosure["note"],
        )
        clarke_tax_sale = county_source_links("AL", "Clarke County")[
            "tax_sale"
        ]
        self.assertEqual(
            clarke_tax_sale["directory_url"],
            "https://clarkecountyal.com/revenue-commissioner-clarke-co/",
        )
        self.assertEqual(
            clarke_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_16.PDF",
        )
        self.assertIn("Tax Lien Legal Notice dated 2022-08-06", clarke_tax_sale["note"])
        self.assertIn(
            "publishes no current auction date or parcel list",
            clarke_tax_sale["note"],
        )
        clarke_foreclosure = county_source_links("AL", "Clarke County")[
            "foreclosure"
        ]
        self.assertEqual(
            clarke_foreclosure["directory_url"],
            "https://clarkecountyal.com/sheriffs-department/",
        )
        self.assertIn(
            "no real-estate foreclosure or sheriff-sale calendar/list",
            clarke_foreclosure["note"],
        )
        clarke_pre_foreclosure = county_source_links(
            "AL", "Clarke County"
        )["pre_foreclosure"]
        self.assertEqual(
            clarke_pre_foreclosure["directory_url"],
            "https://clarkecountyal.com/probate/",
        )
        self.assertIn("an account is required", clarke_pre_foreclosure["note"])
        self.assertIn(
            "does not identify a lis-pendens/default index",
            clarke_pre_foreclosure["note"],
        )
        clay_tax_sale = county_source_links("AL", "Clay County")["tax_sale"]
        self.assertEqual(
            clay_tax_sale["directory_url"],
            "https://www.claycountyrevenue.com/home/news/",
        )
        self.assertEqual(
            clay_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_17.PDF",
        )
        self.assertIn("tax year 2024", clay_tax_sale["note"])
        self.assertIn("May 1, 2025", clay_tax_sale["note"])
        self.assertIn("no newer 2025 tax-year list", clay_tax_sale["note"])
        clay_foreclosure = county_source_links("AL", "Clay County")[
            "foreclosure"
        ]
        self.assertEqual(clay_foreclosure["directory_url"], "http://clayso.net/")
        self.assertIn(
            "not a real-estate foreclosure or sheriff-sale calendar/list",
            clay_foreclosure["note"],
        )
        clay_pre_foreclosure = county_source_links(
            "AL", "Clay County"
        )["pre_foreclosure"]
        self.assertEqual(
            clay_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/clay_probate/",
        )
        self.assertIn("expressly prohibits", clay_pre_foreclosure["note"])
        self.assertIn("scrapers", clay_pre_foreclosure["note"])
        cleburne_tax_sale = county_source_links("AL", "Cleburne County")[
            "tax_sale"
        ]
        self.assertEqual(
            cleburne_tax_sale["directory_url"],
            "https://cleburnecountyal.com/wp-content/uploads/2026/04/"
            "3advertisement-for-tax-saleTAXPAYERS_2.pdf",
        )
        self.assertEqual(
            cleburne_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_18.PDF",
        )
        self.assertIn("2025 tax year", cleburne_tax_sale["note"])
        self.assertIn("May 5, 2026", cleburne_tax_sale["note"])
        self.assertIn(
            "no 2026 tax-year list or upcoming sale date",
            cleburne_tax_sale["note"],
        )
        cleburne_foreclosure = county_source_links("AL", "Cleburne County")[
            "foreclosure"
        ]
        self.assertEqual(
            cleburne_foreclosure["directory_url"],
            "https://cleburnecountyal.com/sheriffs-office/",
        )
        self.assertIn(
            "no real-estate foreclosure or sheriff-sale calendar/list",
            cleburne_foreclosure["note"],
        )
        cleburne_pre_foreclosure = county_source_links(
            "AL", "Cleburne County"
        )["pre_foreclosure"]
        self.assertEqual(
            cleburne_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Cleburne_Probate/",
        )
        self.assertIn("expressly prohibits", cleburne_pre_foreclosure["note"])
        self.assertIn("offline readers", cleburne_pre_foreclosure["note"])
        coffee_tax_sale = county_source_links("AL", "Coffee County")["tax_sale"]
        self.assertEqual(
            coffee_tax_sale["directory_url"],
            "https://www.coffeecountyrevenue.com/news.html",
        )
        self.assertEqual(
            coffee_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_19.PDF",
        )
        self.assertIn("first or second Monday in April", coffee_tax_sale["note"])
        self.assertIn("no year-specific date or current parcel list", coffee_tax_sale["note"])
        coffee_foreclosure = county_source_links("AL", "Coffee County")[
            "foreclosure"
        ]
        self.assertEqual(
            coffee_foreclosure["directory_url"],
            "https://www.coffeeso.us/",
        )
        self.assertIn(
            "no real-estate foreclosure or sheriff-sale calendar/list",
            coffee_foreclosure["note"],
        )
        coffee_pre_foreclosure = county_source_links(
            "AL", "Coffee County"
        )["pre_foreclosure"]
        self.assertEqual(
            coffee_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Coffee_Probate/",
        )
        self.assertIn("expressly prohibits", coffee_pre_foreclosure["note"])
        self.assertIn("offline readers", coffee_pre_foreclosure["note"])
        colbert_tax_sale = county_source_links("AL", "Colbert County")[
            "tax_sale"
        ]
        self.assertEqual(
            colbert_tax_sale["directory_url"],
            "https://revenuecommissioner.com/",
        )
        self.assertEqual(
            colbert_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_20.PDF",
        )
        self.assertIn("no current tax-sale date, parcel list, or feed", colbert_tax_sale["note"])
        colbert_foreclosure = county_source_links("AL", "Colbert County")[
            "foreclosure"
        ]
        self.assertEqual(
            colbert_foreclosure["directory_url"],
            "https://www.colbertcounty.org/departments.html",
        )
        self.assertIn("failed at the transport level", colbert_foreclosure["note"])
        colbert_pre_foreclosure = county_source_links(
            "AL", "Colbert County"
        )["pre_foreclosure"]
        self.assertEqual(
            colbert_pre_foreclosure["directory_url"],
            "https://www.colbertprobatejudge.org/home/records/",
        )
        self.assertIn("expressly prohibits", colbert_pre_foreclosure["note"])
        self.assertIn("no online lis-pendens/default index", colbert_pre_foreclosure["note"])
        conecuh_tax_sale = county_source_links("AL", "Conecuh County")[
            "tax_sale"
        ]
        self.assertEqual(
            conecuh_tax_sale["directory_url"],
            "https://www.altags.com/Conecuh_Revenue/Default.aspx",
        )
        self.assertEqual(
            conecuh_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_21.PDF",
        )
        self.assertIn("not a tax-sale list", conecuh_tax_sale["note"])
        self.assertIn("No current county auction date/list", conecuh_tax_sale["note"])
        self.assertIn("expressly prohibits automated systems", conecuh_tax_sale["note"])
        conecuh_foreclosure = county_source_links("AL", "Conecuh County")[
            "foreclosure"
        ]
        self.assertEqual(
            conecuh_foreclosure["directory_url"],
            "https://www.sos.alabama.gov/node/1250",
        )
        self.assertIn(
            "no online foreclosure/sheriff-sale calendar",
            conecuh_foreclosure["note"],
        )
        conecuh_pre_foreclosure = county_source_links(
            "AL", "Conecuh County"
        )["pre_foreclosure"]
        self.assertEqual(
            conecuh_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Conecuh_Probate/Default.aspx",
        )
        self.assertIn("expressly prohibits automated systems", conecuh_pre_foreclosure["note"])
        coosa_tax_sale = county_source_links("AL", "Coosa County")["tax_sale"]
        self.assertEqual(
            coosa_tax_sale["directory_url"],
            "https://coosa.capturecama.com/",
        )
        self.assertEqual(
            coosa_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_22.PDF",
        )
        self.assertIn("no tax-sale notice/list was verified", coosa_tax_sale["note"])
        self.assertIn("direct HTTP and HTTPS retrievals failed", coosa_tax_sale["note"])
        coosa_foreclosure = county_source_links("AL", "Coosa County")[
            "foreclosure"
        ]
        self.assertIn(
            "No official Coosa County Sheriff's website",
            coosa_foreclosure["note"],
        )
        coosa_pre_foreclosure = county_source_links(
            "AL", "Coosa County"
        )["pre_foreclosure"]
        self.assertEqual(
            coosa_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Coosa_Probate/Default.aspx",
        )
        self.assertIn("expressly prohibits automated systems", coosa_pre_foreclosure["note"])
        covington_tax_sale = county_source_links("AL", "Covington County")[
            "tax_sale"
        ]
        self.assertEqual(
            covington_tax_sale["directory_url"],
            "https://www.covingtoncountyal.gov/207/Revenue-Commissioner",
        )
        self.assertEqual(
            covington_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_23.PDF",
        )
        self.assertIn("tax years 2023-2024 forward", covington_tax_sale["note"])
        self.assertIn("returned HTTP 404", covington_tax_sale["note"])
        self.assertIn(
            "no current sale list/date was verified",
            covington_tax_sale["note"],
        )
        covington_foreclosure = county_source_links(
            "AL", "Covington County"
        )["foreclosure"]
        self.assertIn(
            "No official county sheriff-sale or real-estate foreclosure",
            covington_foreclosure["note"],
        )
        covington_pre_foreclosure = county_source_links(
            "AL", "Covington County"
        )["pre_foreclosure"]
        self.assertEqual(
            covington_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Covington_Probate/",
        )
        self.assertIn(
            "expressly prohibits automated systems",
            covington_pre_foreclosure["note"],
        )
        crenshaw_assessor = county_source_links("AL", "Crenshaw County")[
            "assessor"
        ]
        self.assertEqual(
            crenshaw_assessor["directory_url"],
            "https://crenshawcountyalonline.com/#/RevenueCommissioner",
        )
        self.assertIn("reCAPTCHA-gated search", crenshaw_assessor["note"])
        crenshaw_tax_sale = county_source_links("AL", "Crenshaw County")[
            "tax_sale"
        ]
        self.assertEqual(
            crenshaw_tax_sale["directory_url"],
            "https://crenshawcountyalonline.com/#/RevenueCommissioner/News",
        )
        self.assertEqual(
            crenshaw_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_24.PDF",
        )
        self.assertIn("three consecutive weeks in April", crenshaw_tax_sale["note"])
        self.assertIn("date announced each year", crenshaw_tax_sale["note"])
        self.assertIn(
            "No current year-specific sale date/list",
            crenshaw_tax_sale["note"],
        )
        crenshaw_code = county_source_links("AL", "Crenshaw County")[
            "code_enforcement"
        ]
        self.assertEqual(
            crenshaw_code["directory_url"],
            "https://crenshawcountyalonline.com/#/CountyCommission",
        )
        self.assertIn("Building Code Permit Letter", crenshaw_code["note"])
        crenshaw_foreclosure = county_source_links(
            "AL", "Crenshaw County"
        )["foreclosure"]
        self.assertIn(
            "did not expose a sheriff-sale or foreclosure calendar/list",
            crenshaw_foreclosure["note"],
        )
        crenshaw_pre_foreclosure = county_source_links(
            "AL", "Crenshaw County"
        )["pre_foreclosure"]
        self.assertEqual(
            crenshaw_pre_foreclosure["directory_url"],
            "https://crenshawcountyalonline.com/#/",
        )
        self.assertIn(
            "Syscon's terms prohibit data mining",
            crenshaw_pre_foreclosure["note"],
        )
        self.assertIn("not Crenshaw", crenshaw_pre_foreclosure["note"])
        cullman_assessor = county_source_links("AL", "Cullman County")[
            "assessor"
        ]
        self.assertEqual(
            cullman_assessor["directory_url"],
            "https://cullmanrevenuecommissioner.com/",
        )
        self.assertIn("parcel viewer", cullman_assessor["note"])
        cullman_tax_sale = county_source_links("AL", "Cullman County")[
            "tax_sale"
        ]
        self.assertEqual(
            cullman_tax_sale["directory_url"],
            "https://cullmanproperty.countygovservices.com/"
            "Property/DelinquentParcels",
        )
        self.assertEqual(
            cullman_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_25.PDF",
        )
        self.assertIn("listing is currently disabled", cullman_tax_sale["note"])
        self.assertIn("No current sale list/date", cullman_tax_sale["note"])
        cullman_code = county_source_links("AL", "Cullman County")[
            "code_enforcement"
        ]
        self.assertEqual(
            cullman_code["directory_url"],
            "https://co.cullman.al.us/sales-tax.html",
        )
        self.assertIn("illegal dumping and littering", cullman_code["note"])
        self.assertIn("not a property-level", cullman_code["note"])
        cullman_foreclosure = county_source_links(
            "AL", "Cullman County"
        )["foreclosure"]
        self.assertIn("HTTP 403", cullman_foreclosure["note"])
        self.assertIn("no county-specific authorized feed", cullman_foreclosure["note"])
        cullman_pre_foreclosure = county_source_links(
            "AL", "Cullman County"
        )["pre_foreclosure"]
        self.assertEqual(
            cullman_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Cullman_Probate/",
        )
        self.assertIn(
            "expressly prohibits automated systems",
            cullman_pre_foreclosure["note"],
        )
        dale_assessor = county_source_links("AL", "Dale County")["assessor"]
        self.assertEqual(
            dale_assessor["directory_url"],
            "https://www.dalecountyrevenue.com/home/homenew/property-tax/",
        )
        self.assertIn("BPP location number and access code", dale_assessor["note"])
        self.assertIn("expressly prohibits bots", dale_assessor["note"])
        dale_tax_sale = county_source_links("AL", "Dale County")["tax_sale"]
        self.assertEqual(
            dale_tax_sale["directory_url"],
            "https://www.dalecountyrevenue.com/"
            "home/homenew/property-tax/deliquent-property-taxes/",
        )
        self.assertEqual(
            dale_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_26.PDF",
        )
        self.assertIn("April 14, 2026", dale_tax_sale["note"])
        self.assertIn("DELINQUENT LIST UNAVAILABLE", dale_tax_sale["note"])
        self.assertIn("No 2027 sale date/list", dale_tax_sale["note"])
        dale_code = county_source_links("AL", "Dale County")[
            "code_enforcement"
        ]
        self.assertIn("No Dale County property-level code-enforcement", dale_code["note"])
        dale_foreclosure = county_source_links("AL", "Dale County")[
            "foreclosure"
        ]
        self.assertIn("http://daleso.com", dale_foreclosure["note"])
        self.assertIn("request timed out", dale_foreclosure["note"])
        dale_pre_foreclosure = county_source_links(
            "AL", "Dale County"
        )["pre_foreclosure"]
        self.assertEqual(
            dale_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Dale_Probate/",
        )
        self.assertIn(
            "expressly prohibits automated systems",
            dale_pre_foreclosure["note"],
        )
        dallas_sources = county_source_links("AL", "Dallas County", "01047")
        dallas_assessor = dallas_sources["assessor"]
        self.assertEqual(
            dallas_assessor["directory_url"],
            "https://www.dallascounty-al.org/County-Departments/"
            "Tax-Assessor/Assessor-Department",
        )
        self.assertEqual(
            dallas_assessor["source_url"],
            "https://dallascountyal.maps.arcgis.com/apps/"
            "webappviewer/index.html?id=747eebce86fe460a88a0dbb29f828560",
        )
        self.assertIn("not a documented assessment feed/export/API", dallas_assessor["note"])
        dallas_tax_sale = dallas_sources["tax_sale"]
        self.assertEqual(
            dallas_tax_sale["directory_url"],
            "https://dallas.capturecama.com/collection",
        )
        self.assertEqual(
            dallas_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_27.PDF",
        )
        self.assertIn("April 15, 2026", dallas_tax_sale["note"])
        self.assertIn("generic Citizen Access Portal shell", dallas_tax_sale["note"])
        self.assertIn("No current sale date/list", dallas_tax_sale["note"])
        self.assertIn("not the county auction calendar", dallas_tax_sale["note"])
        dallas_code = dallas_sources["code_enforcement"]
        self.assertEqual(
            dallas_code["directory_url"],
            "https://www.dallascounty-al.org/Find-It-Here/"
            "County-and-State-Offices",
        )
        self.assertIn(
            "no property-level code-enforcement or open-violation list/feed",
            dallas_code["note"],
        )
        dallas_foreclosure = dallas_sources["foreclosure"]
        self.assertEqual(
            dallas_foreclosure["directory_url"],
            "https://www.dallascounty-al.org/Public-notices",
        )
        self.assertIn("334-874-2530", dallas_foreclosure["note"])
        self.assertIn("no current real-estate sale list", dallas_foreclosure["note"])
        self.assertIn(
            "Terms prohibit scraping and automated commercial collection",
            dallas_foreclosure["note"],
        )
        dallas_pre_foreclosure = dallas_sources["pre_foreclosure"]
        self.assertEqual(
            dallas_pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Dallas_Probate/",
        )
        self.assertIn(
            "expressly prohibits bots, scrapers",
            dallas_pre_foreclosure["note"],
        )
        self.assertIn(
            "No lis-pendens/default index or pre-foreclosure feed",
            dallas_pre_foreclosure["note"],
        )
        dekalb_sources = county_source_links("AL", "DeKalb County", "01049")
        dekalb_assessor = dekalb_sources["assessor"]
        self.assertEqual(
            dekalb_assessor["directory_url"],
            "https://revenue-dekalbco-al.us/appraisal/",
        )
        self.assertEqual(
            dekalb_assessor["source_url"],
            "https://isv.kcsgis.com/al.dekalb_revenue/",
        )
        self.assertIn("AssuranceWeb", dekalb_assessor["note"])
        self.assertIn(
            "not documented assessment feeds/export/APIs",
            dekalb_assessor["note"],
        )
        dekalb_tax_sale = dekalb_sources["tax_sale"]
        self.assertEqual(
            dekalb_tax_sale["directory_url"],
            "https://revenue-dekalbco-al.us/taxes/",
        )
        self.assertEqual(
            dekalb_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_28.PDF",
        )
        self.assertIn("auctioned in April or May", dekalb_tax_sale["note"])
        self.assertIn("no current year-specific sale date or auction list", dekalb_tax_sale["note"])
        self.assertIn("not the county auction calendar", dekalb_tax_sale["note"])
        dekalb_code = dekalb_sources["code_enforcement"]
        self.assertEqual(dekalb_code["directory_url"], "https://dekalbcountyal.us/")
        self.assertIn(
            "no countywide property-level code-enforcement",
            dekalb_code["note"],
        )
        dekalb_foreclosure = dekalb_sources["foreclosure"]
        self.assertEqual(
            dekalb_foreclosure["directory_url"],
            "https://www.dekalbcountysheriff.org/",
        )
        self.assertIn(
            "no identified real-estate foreclosure/sheriff-sale calendar or list",
            dekalb_foreclosure["note"],
        )
        self.assertIn(
            "Terms prohibit scraping and automated commercial collection",
            dekalb_foreclosure["note"],
        )
        dekalb_pre_foreclosure = dekalb_sources["pre_foreclosure"]
        self.assertEqual(
            dekalb_pre_foreclosure["directory_url"],
            "https://services.revenue-dekalbco-al.us/ProbateRecords",
        )
        self.assertIn(
            "official Probate Judge website's Links page",
            dekalb_pre_foreclosure["note"],
        )
        self.assertIn(
            "no public lis-pendens/default index or pre-foreclosure feed",
            dekalb_pre_foreclosure["note"],
        )
        elmore_sources = county_source_links("AL", "Elmore County", "01051")
        elmore_assessor = elmore_sources["assessor"]
        self.assertEqual(
            elmore_assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Elmore",
        )
        self.assertEqual(
            elmore_assessor["source_url"],
            "https://elmorerevenuecommissioner.net/",
        )
        self.assertIn(
            "not documented feed/export/APIs",
            elmore_assessor["note"],
        )
        elmore_tax_sale = elmore_sources["tax_sale"]
        self.assertEqual(
            elmore_tax_sale["directory_url"],
            "https://elmorerevenuecommissioner.net/DelqSearch",
        )
        self.assertEqual(
            elmore_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_29.PDF",
        )
        self.assertIn("no current county auction date, sale list", elmore_tax_sale["note"])
        self.assertIn("not a local auction calendar", elmore_tax_sale["note"])
        self.assertIn("lack physical addresses", elmore_tax_sale["note"])
        elmore_code = elmore_sources["code_enforcement"]
        self.assertEqual(
            elmore_code["directory_url"],
            "https://www.elmoreco.org/service-directory",
        )
        self.assertIn(
            "No countywide property-level code-enforcement/open-violation feed",
            elmore_code["note"],
        )
        elmore_foreclosure = elmore_sources["foreclosure"]
        self.assertEqual(
            elmore_foreclosure["directory_url"],
            "https://www.elmoreso.com/departments-services",
        )
        self.assertEqual(
            elmore_foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn(
            "no real-estate foreclosure/sheriff-sale calendar, list, or feed",
            elmore_foreclosure["note"],
        )
        self.assertIn(
            "Terms prohibit scraping, spidering, automated collection",
            elmore_foreclosure["note"],
        )
        elmore_pre_foreclosure = elmore_sources["pre_foreclosure"]
        self.assertEqual(
            elmore_pre_foreclosure["directory_url"],
            "https://www.elmoreco.org/elmore-county-recording",
        )
        self.assertEqual(
            elmore_pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Elmore_Probate/",
        )
        self.assertIn("REAACT notice", elmore_pre_foreclosure["note"])
        self.assertIn(
            "expressly prohibits automated systems",
            elmore_pre_foreclosure["note"],
        )
        self.assertIn(
            "No lis-pendens/default index, authorized bulk feed",
            elmore_pre_foreclosure["note"],
        )
        escambia_sources = county_source_links(
            "AL", "Escambia County", "01053"
        )
        escambia_assessor = escambia_sources["assessor"]
        self.assertEqual(
            escambia_assessor["directory_url"],
            "https://www.escambiacountyal.gov/government/"
            "tax_assessor/index.php",
        )
        self.assertEqual(
            escambia_assessor["source_url"],
            "https://www.alabamagis.com/escambia/",
        )
        self.assertIn("CAMA sales inventory", escambia_assessor["note"])
        self.assertIn(
            "no documented assessment feed/export/API",
            escambia_assessor["note"],
        )
        escambia_tax_sale = escambia_sources["tax_sale"]
        self.assertEqual(
            escambia_tax_sale["directory_url"],
            "https://www.escambiacountyal.gov/government/"
            "tax_collector/delinquent_taxes.php",
        )
        self.assertEqual(
            escambia_tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_30.PDF",
        )
        self.assertIn(
            "TAX LIEN SALE LIST is available only April-May",
            escambia_tax_sale["note"],
        )
        self.assertIn("PDF route returned HTTP 404", escambia_tax_sale["note"])
        self.assertIn("three-year redemption", escambia_tax_sale["note"])
        escambia_code = escambia_sources["code_enforcement"]
        self.assertEqual(
            escambia_code["directory_url"],
            "https://www.escambiacountyal.gov/",
        )
        self.assertIn(
            "no countywide property-level code-enforcement",
            escambia_code["note"],
        )
        escambia_foreclosure = escambia_sources["foreclosure"]
        self.assertEqual(
            escambia_foreclosure["directory_url"],
            "https://www.escambiacountysheriffal.org/",
        )
        self.assertEqual(
            escambia_foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn(
            "no real-estate foreclosure/sheriff-sale calendar, list, or feed",
            escambia_foreclosure["note"],
        )
        self.assertIn(
            "Terms prohibit scraping, spidering, automated collection",
            escambia_foreclosure["note"],
        )
        escambia_pre_foreclosure = escambia_sources["pre_foreclosure"]
        self.assertEqual(
            escambia_pre_foreclosure["directory_url"],
            "https://www.escambiacountyal.gov/courts___legal/"
            "judge_of_probate/index.php",
        )
        self.assertEqual(
            escambia_pre_foreclosure["source_url"],
            "https://ingprobate.com/Escambia_Probate/ProbateDefault.aspx",
        )
        self.assertIn(
            "expressly prohibits automated systems",
            escambia_pre_foreclosure["note"],
        )
        self.assertIn(
            "No public lis-pendens/default index, pre-foreclosure feed",
            escambia_pre_foreclosure["note"],
        )
        alabama_foreclosure = county_source_links(
            "AL", "Jefferson County"
        )["foreclosure"]
        self.assertEqual(
            alabama_foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("participating newspapers", alabama_foreclosure["note"])
        self.assertIn("commercial exploitation", alabama_foreclosure["note"])
        alabama_pre_foreclosure = county_source_links(
            "AL", "Jefferson County"
        )["pre_foreclosure"]
        self.assertEqual(
            alabama_pre_foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn(
            "No complete statewide pre-foreclosure/default-notice feed",
            alabama_pre_foreclosure["note"],
        )
        self.assertEqual(
            ohio["assessor"]["source_url"],
            "https://caao.org/auditors-directory/name/franklin-county/",
        )
        self.assertTrue(alabama["assessor"]["source_url"].endswith("#Jefferson"))
        self.assertEqual(
            texas["assessor"]["directory_url"],
            "https://comptroller.texas.gov/taxes/property-tax/county-directory/",
        )

    def test_public_notice_discovery_sources_record_scope_and_reuse_limits(self):
        missouri = county_source_links("MO", "Boone County")
        ohio = county_source_links("OH", "Franklin County")
        texas = county_source_links("TX", "Harris County")

        self.assertEqual(
            missouri["tax_sale"]["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("prohibit scraping", missouri["tax_sale"]["note"])
        self.assertEqual(
            missouri["foreclosure"]["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertEqual(
            missouri["tax_sale"]["directory_url"],
            "https://www.boonemo.gov/collector/",
        )
        self.assertEqual(
            county_source_links("MO", "St. Louis County", "29189")["tax_sale"][
                "directory_url"
            ],
            "https://www.mocounties.com/st-louis-county",
        )
        self.assertEqual(
            county_source_links("MO", "Platte County", "29165")["tax_sale"][
                "directory_url"
            ],
            "https://www.co.platte.mo.us/",
        )
        self.assertEqual(
            county_source_links("MO", "St. Louis city", "29510")["tax_sale"][
                "directory_url"
            ],
            "https://www.stlouis-mo.gov/",
        )
        self.assertEqual(
            ohio["foreclosure"]["source_url"],
            "https://www.publicnoticesohio.com/",
        )
        self.assertIn("personal, non-commercial", ohio["foreclosure"]["note"])
        self.assertIn("87 other county portals", ohio["foreclosure"]["note"])
        self.assertIn("express written consent", ohio["foreclosure"]["note"])
        ohio_pre_foreclosure = ohio["pre_foreclosure"]
        self.assertEqual(
            ohio_pre_foreclosure["source_url"],
            "https://buckeyesheriffs.org/contact-your-sheriff/",
        )
        self.assertIn("contact directory only", ohio_pre_foreclosure["note"])
        self.assertIn(
            "no complete statewide pre-foreclosure feed",
            ohio_pre_foreclosure["note"],
        )
        self.assertIn(
            "all 88 Ohio counties",
            ohio["tax_sale"]["note"],
        )
        self.assertIn("only 48 entries", ohio["tax_sale"]["note"])
        self.assertIn("reached 41", ohio["tax_sale"]["note"])
        self.assertIn("Monroe returned 404", ohio["tax_sale"]["note"])
        self.assertEqual(
            texas["tax_sale"]["source_url"],
            "https://www.texaspublicnotices.com/",
        )
        self.assertIn("249 named counties plus Unknown", texas["tax_sale"]["note"])
        self.assertIn("prohibit automated collection", texas["foreclosure"]["note"])

    def test_alabama_tax_transcripts_cover_all_counties_and_jefferson_split(self):
        counties = [
            county["county"].removesuffix(" County")
            for county in county_jurisdictions()
            if county["state"] == "AL"
        ]
        self.assertEqual(len(counties), 67)
        self.assertEqual(
            set(ALABAMA_TAX_TRANSCRIPT_CODES),
            {county.upper() for county in counties if county != "Jefferson"},
        )
        self.assertEqual(
            set(ALABAMA_TAX_TRANSCRIPT_CODES.values()),
            {f"{code:02}" for code in range(2, 68)},
        )
        self.assertEqual(ALABAMA_TAX_TRANSCRIPT_CODES["MOBILE"], "02")
        self.assertEqual(ALABAMA_TAX_TRANSCRIPT_CODES["MONTGOMERY"], "03")

        for county in counties:
            source = county_source_links("AL", f"{county} County")["tax_sale"]
            if county == "Jefferson":
                self.assertEqual(
                    source["source_url"],
                    "https://www.revenue.alabama.gov/property-tax/"
                    "tax-delinquent-property-and-land-sales/",
                )
            elif county == "Tuscaloosa":
                self.assertEqual(
                    source["source_url"],
                    "https://www.tuscco.com/wp-content/uploads/2026/06/"
                    "Copy-of-List-for-IT-2025-Tax-Year-Prop-did-not-sell-"
                    "002.pdf",
                )
                self.assertIn("WWW_TRANS_63.PDF", source["note"])
            elif county == "Walker":
                self.assertEqual(
                    source["source_url"],
                    "https://www.walkercountyrevenue.com/tax-sale/",
                )
                self.assertIn("WWW_TRANS_64.PDF", source["note"])
            else:
                code = ALABAMA_TAX_TRANSCRIPT_CODES[county.upper()]
                self.assertTrue(source["source_url"].endswith(f"WWW_TRANS_{code}.PDF"))

    def test_tested_endpoints_show_scope_and_unresolved_feed_requirements(self):
        jefferson = county_source_links("AL", "Jefferson County", "01073")[
            "assessor"
        ]
        self.assertEqual(
            jefferson["endpoint_url"],
            "https://jccgis.jccal.org/server/rest/services/Basemap/Parcels/"
            "MapServer/0",
        )
        self.assertEqual(jefferson["endpoint_record_count"], 410119)
        self.assertEqual(
            jefferson["endpoint_status"], "freshness_review_required"
        )
        self.assertIn("generated nightly", jefferson["endpoint_note"])

        mobile = county_source_links("AL", "Mobile County", "01097")["assessor"]
        self.assertEqual(
            mobile["endpoint_url"],
            "https://services8.arcgis.com/HND1NcQt6vgOGn1z/arcgis/rest/services/"
            "MCRC_Public_Parcels/FeatureServer/0",
        )
        self.assertEqual(mobile["endpoint_last_verified"], "2026-10-19")
        self.assertEqual(mobile["endpoint_record_count"], 214040)
        self.assertEqual(mobile["endpoint_status"], "terms_review_required")

        benton = county_source_links("AR", "Benton County", "05007")["assessor"]
        self.assertEqual(benton["endpoint_status"], "restricted_planning")
        self.assertIn("Do not use it commercially", benton["endpoint_note"])

        franklin = county_source_links("OH", "Franklin County", "39049")[
            "assessor"
        ]
        self.assertEqual(
            franklin["endpoint_url"],
            "https://gis.franklincountyohio.gov/hosting/rest/services/"
            "ParcelFeatures/Parcel_Features/MapServer/0",
        )
        self.assertEqual(franklin["endpoint_record_count"], 494902)
        self.assertIn("no site-city field", franklin["endpoint_note"])

        ohio = county_source_links("OH", "Athens County", "39009")["assessor"]
        self.assertEqual(ohio["endpoint_scope"], "Ohio statewide")
        self.assertEqual(ohio["endpoint_record_count"], 6313610)
        self.assertIn("January 21, 2024", ohio["endpoint_note"])

        st_louis = county_source_links("MO", "St. Louis County", "29189")[
            "assessor"
        ]
        self.assertEqual(st_louis["endpoint_record_count"], 400796)
        self.assertEqual(st_louis["endpoint_status"], "historical_not_daily")
        self.assertIn("maximum TAXYR aggregate returned 2023", st_louis["endpoint_note"])

        dallas = county_source_links("TX", "Dallas County", "48113")[
            "code_enforcement"
        ]
        self.assertEqual(dallas["endpoint_status"], "historical_not_daily")
        self.assertEqual(dallas["endpoint_record_count"], 135257)
        self.assertEqual(dallas["endpoint_scope"], "City of Dallas only")

        harris = county_source_links("TX", "Harris County", "48201")["assessor"]
        self.assertEqual(
            harris["endpoint_url"],
            "https://www.gis.hctx.net/arcgishcpid/rest/services/HCAD/Parcels/"
            "MapServer/0",
        )
        self.assertEqual(harris["endpoint_record_count"], 1551736)
        self.assertIn("updated bi-weekly", harris["endpoint_note"])

        cincinnati = county_source_links("OH", "Hamilton County", "39061")[
            "code_enforcement"
        ]
        self.assertEqual(cincinnati["endpoint_record_count"], 771669)
        self.assertEqual(
            cincinnati["additional_endpoints"][0]["url"],
            "https://data.cincinnati-oh.gov/resource/pk9w-99n6.json",
        )

        kansas_city = county_source_links("MO", "Jackson County", "29095")[
            "code_enforcement"
        ]
        self.assertEqual(kansas_city["endpoint_status"], "freshness_review_required")
        self.assertEqual(kansas_city["endpoint_record_count"], 174999)

        midland = county_source_links("TX", "Midland County", "48329")[
            "code_enforcement"
        ]
        self.assertEqual(midland["endpoint_status"], "historical_not_daily")
        self.assertEqual(midland["endpoint_record_count"], 293437)
        self.assertIn("March 4, 2026", midland["endpoint_note"])

    def test_etowah_sources_record_verified_links_and_feed_limits(self):
        sources = county_source_links("AL", "Etowah County", "01055")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://etowahcounty.org/revenue-commissioner/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://etowahcounty.org/department/appraisal/",
        )
        self.assertIn("not a public daily feed", assessor["note"])
        self.assertIn(
            "No documented property-record export/API",
            assessor["note"],
        )

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://etowahcounty.org/department/assessing/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_31.PDF",
        )
        self.assertIn("May 4, 2026 at 9:00 a.m.", tax_sale["note"])
        self.assertIn("no 2027 date is posted", tax_sale["note"])
        self.assertIn("generic AssuranceGov shell", tax_sale["note"])
        self.assertIn("not the county auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["directory_url"], "https://etowahcounty.org/")
        self.assertIn(
            "no countywide property-level code-enforcement",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.etowahcountysheriff.com/upages.php?id=41",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("direct retrieval", foreclosure["note"])
        self.assertIn("participating newspapers", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://etowahcounty.org/deeds-and-records/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://etowahprobate.assurancegov.com/",
        )
        self.assertIn("lists lis pendens", pre_foreclosure["note"])
        self.assertIn("redirects to sign-in", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_fayette_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Fayette County", "01057")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.fayetteco.net/home/departments/"
            "revenue-commissioner/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.alabamagis.com/Fayette/",
        )
        self.assertIn("GIS welcome page", assessor["note"])
        self.assertIn("No assessment export", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.fayetteco.net/home/departments/"
            "revenue-commissioner/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_32.PDF",
        )
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("Fayette County, Georgia", tax_sale["note"])
        self.assertIn("No current Alabama county list/date", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.fayetteco.net/home/government/local-government/",
        )
        self.assertEqual(
            code["source_url"],
            "https://www.fayetteco.net/home/about/faqs/",
        )
        self.assertIn(
            "no building or permitting requirements",
            code["note"],
        )
        self.assertIn(
            "No countywide property-level code-enforcement",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.fayetteso.com/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn(
            "no real-estate foreclosure/sheriff-sale calendar",
            foreclosure["note"],
        )
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.fayetteco.net/home/departments/"
            "probate-office/online-record-search/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/fayette_probate/",
        )
        self.assertIn(
            "expressly prohibit automated systems",
            pre_foreclosure["note"],
        )
        self.assertIn(
            "No public lis-pendens/default index",
            pre_foreclosure["note"],
        )

    def test_franklin_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Franklin County", "01059")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://franklincountyrevenue.com/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://franklinproperty.countygovservices.com/"
            "Property/Search",
        )
        self.assertIn("generic portal shells/titles", assessor["note"])
        self.assertIn("No documented assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://franklincountyrevenue.com/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_33.PDF",
        )
        self.assertIn("general GovEase homepage", tax_sale["note"])
        self.assertIn("No current auction date/list", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://franklincountyal.org/departments/",
        )
        self.assertIn(
            "no building-code or code-enforcement department",
            code["note"],
        )
        self.assertIn(
            "No countywide property-level code-enforcement",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.franklinsheriff.org/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("direct requests timed out", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://franklincountyal.org/departments/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Franklin_Probate/",
        )
        self.assertIn("R.E.A.A.C.T. option", pre_foreclosure["note"])
        self.assertIn(
            "expressly prohibits automated systems",
            pre_foreclosure["note"],
        )
        self.assertIn("No authorized pre-foreclosure feed", pre_foreclosure["note"])

    def test_geneva_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Geneva County", "01061")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://genevacountyal.gov/revenue/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.alabamagis.com/Geneva/",
        )
        self.assertIn("generic welcome page", assessor["note"])
        self.assertIn("returned HTTP 503", assessor["note"])
        self.assertIn("No documented assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://genevacountyal.gov/revenue-tax-sale-info/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_34.PDF",
        )
        self.assertIn("2018 sale was postponed to May 7, 2019", tax_sale["note"])
        self.assertIn("No current county sale list/date", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.genevaal.gov/building-department",
        )
        self.assertIn("not a countywide department", code["note"])
        self.assertIn("publishes no property-level violation list", code["note"])
        self.assertIn("confirm each property's municipality", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://genevacountyal.gov/sheriff/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("title-only landing page", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])
        self.assertIn("unverified manual leads only", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://genevacountyal.gov/probate/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Geneva_Probate/",
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])
        self.assertIn("not configured as feeds", pre_foreclosure["note"])

    def test_greene_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Greene County", "01063")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://experience.arcgis.com/experience/"
            "c4dc2ec2622a42f88610d370f32ea0f8/",
        )
        self.assertIn("inactive as of October 2026", assessor["note"])
        self.assertIn("owner as GreeneCountyAL", assessor["note"])
        self.assertIn("No documented assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://greenecountycommission.com/taxinformation/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_35.PDF",
        )
        self.assertIn("Information coming soon", tax_sale["note"])
        self.assertIn("No current County auction date/list", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("out-of-state jurisdictions", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://greenecountycommission.com/directory/",
        )
        self.assertIn("manual discovery link only", code["note"])
        self.assertIn("No current County or municipal", code["note"])
        self.assertIn("Confirm the responsible jurisdiction", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.gcsoal.org/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("returned a React app shell", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])
        self.assertIn("No county-specific authorized foreclosure feed", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Greene_Probate/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Greene_Probate/",
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_hale_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Hale County", "01065")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://hcal.maps.arcgis.com/apps/webappviewer/"
            "index.html?id=096bf46a286340ffa7f5e5b78fb2800c",
        )
        self.assertIn("public item metadata names HaleCounty as owner", assessor["note"])
        self.assertIn("Business Personal Property return login", assessor["note"])
        self.assertIn("prohibits automated access and extraction", assessor["note"])
        self.assertIn("No documented real-property export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.halecountyal.gov/"
            "notice-sale-tax-liens-collecting-delinquent-property-tax",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_36.PDF",
        )
        self.assertIn("requests to the County host timed out", tax_sale["note"])
        self.assertIn("No current sale date/list", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.halecountyal.gov/",
        )
        self.assertIn("No County or municipal property-level", code["note"])
        self.assertIn("Confirm the responsible jurisdiction", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.halecoso.com/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("Alabama Sheriffs Association directory", foreclosure["note"])
        self.assertIn("failed at the DNS/TLS transport layer", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.halecountyal.gov/probate-judge",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.altags.com/Hale_Probate/",
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_henry_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Henry County", "01067")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/",
        )
        self.assertEqual(assessor["source_url"], "https://henry.capturecama.com/")
        self.assertIn("public GIS and CaptureCAMA online record search", assessor["note"])
        self.assertIn("No documented assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://henry.capturecama.com/DelqSearch",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_37.PDF",
        )
        self.assertIn("No current Henry County tax-sale date", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["directory_url"], "https://www.henrycountyal.com/")
        self.assertIn("no property-level code-enforcement office", code["note"])
        self.assertIn("Confirm the responsible provider", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.henrycountyal.com/public-notice",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("not a foreclosure or sheriff-sale calendar/list", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.henrycountyal.com/records-deeds",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Henry_Probate/",
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_houston_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Houston County", "01069")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://houstoncountyal.gov/revenue/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.ingproperty.com/Houston_Revenue/property.aspx",
        )
        self.assertIn("Houston County GIS", assessor["note"])
        self.assertIn("No documented bulk assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://houstoncountyal.gov/revenue/tax_sale",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_38.PDF",
        )
        self.assertIn("beginning May 4, 2026", tax_sale["note"])
        self.assertIn("sale date is past", tax_sale["note"])
        self.assertIn("2026_tax_lien_auction_parcels_for_2025_tax_year_", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://houstoncountyal.gov/departments/",
        )
        self.assertIn("no property-level code-enforcement office", code["note"])
        self.assertIn("verify the responsible provider", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://houstoncosoal.gov/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no real-estate foreclosure/sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://houstoncountyal.gov/probate/recording_guidelines/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Houston_Probate/",
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_jackson_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Jackson County", "01071")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.jacksoncountyal.gov/245/"
            "Revenue-Commissioner/revenuecommissioner",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://jacksonproperty.countygovservices.com/Property/Search",
        )
        self.assertIn("appraising real property", assessor["note"])
        self.assertIn("No documented bulk assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.jacksoncountyal.gov/245/"
            "Revenue-Commissioner/revenuecommissioner",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_39.PDF",
        )
        self.assertIn("newspaper advertising in March", tax_sale["note"])
        self.assertIn("tax sale in April", tax_sale["note"])
        self.assertIn("does not provide a current year-specific date", tax_sale["note"])
        self.assertIn("not the county auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["directory_url"], "https://www.jacksoncountyal.gov/")
        self.assertIn("No provider-specific", code["note"])
        self.assertIn("Confirm the responsible provider", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.jacksoncountysheriffal.org/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no real-estate foreclosure or sheriff-sale", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.jacksoncountyal.gov/245/"
            "Revenue-Commissioner/revenuecommissioner",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no public lis-pendens/default index", pre_foreclosure["note"])
        self.assertIn("prohibit automated/commercial collection", pre_foreclosure["note"])

    def test_jefferson_sources_record_access_limits_and_split_transcripts(self):
        sources = county_source_links("AL", "Jefferson County", "01073")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["endpoint_url"],
            "https://jccgis.jccal.org/server/rest/services/Basemap/Parcels/"
            "MapServer/0",
        )
        self.assertEqual(assessor["endpoint_record_count"], 410119)

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "tax-delinquent-property-and-land-sales/",
        )
        self.assertIn("split between Birmingham and Bessemer PDFs", tax_sale["note"])
        self.assertIn("returned HTTP 403", tax_sale["note"])
        self.assertIn("not an upcoming county auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["directory_url"], "https://www.jccal.org/")
        self.assertIn("No countywide property-level", code["note"])
        self.assertIn("Confirm the provider by the property's municipality", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.jccal.org/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("returned HTTP 403", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.jccal.org/",
        )
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])
        self.assertIn("prohibits automated/commercial collection", pre_foreclosure["note"])

    def test_lamar_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Lamar County", "01075")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.alabamagis.com/lamar/",
        )
        self.assertIn("Lamar County Alabama Public GIS welcome page", assessor["note"])
        self.assertIn("No assessment update cadence", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Lamar",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_40.PDF",
        )
        self.assertIn("no Lamar-specific upcoming auction date", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Lamar",
        )
        self.assertIn("No Lamar County or municipal property-level", code["note"])
        self.assertIn("Confirm the responsible provider", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no verified Lamar-specific sheriff-sale", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Lamar_Probate/",
        )
        self.assertEqual(pre_foreclosure["source_url"], pre_foreclosure["directory_url"])
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_lauderdale_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Lauderdale County", "01077")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.lauderdalecountyal.gov/Default.asp",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://altags.com/lauderdale_revenue/",
        )
        self.assertIn("identifies the Lauderdale Revenue Commission", assessor["note"])
        self.assertIn("expressly prohibits automated systems", assessor["note"])
        self.assertIn("No authorized bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Lauderdale",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_41.PDF",
        )
        self.assertIn("no current Lauderdale tax-sale date", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.lauderdalecountyal.gov/home/departments/",
        )
        self.assertIn("no property-level code-enforcement provider", code["note"])
        self.assertIn(
            "Confirm the provider by each property's municipality",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("redirects to a GoDaddy parking page", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Lauderdale_Probate/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Lauderdale_Probate/",
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_lawrence_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Lawrence County", "01079")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Lawrence",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.lawrencecountyrevenue.com/#/",
        )
        self.assertIn("links the Lawrence County Revenue Commissioner", assessor["note"])
        self.assertIn("returned an application shell", assessor["note"])
        self.assertIn("No bulk assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://lawrencecountyal.org/revenue-commissioner/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_42.PDF",
        )
        self.assertIn("no current tax-sale date", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://lawrencecountyal.org/departments/",
        )
        self.assertIn(
            "did not identify a property-level code-enforcement office",
            code["note"],
        )
        self.assertIn(
            "Confirm the responsible provider by each property's municipality",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://lawrencecountyal.org/sherriff-dept/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("not a foreclosure or sheriff-sale calendar/list", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://lawrencecountyal.org/probate-judge/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Lawrence_Probate/",
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_lee_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Lee County", "01081")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Lee",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.altags.com/lee_license/default.aspx",
        )
        self.assertIn(
            "links the Lee County Revenue Commissioner's website",
            assessor["note"],
        )
        self.assertIn("expressly prohibits automated systems", assessor["note"])
        self.assertIn("no documented bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.leecountyrevenuecommissioner.com/"
            "home/property-tax/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_43.PDF",
        )
        self.assertIn("no current Lee County tax-sale date", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["directory_url"], "https://www.leecountyal.gov/")
        self.assertEqual(code["source_url"], "https://leecountyplanning.com/")
        self.assertIn("not a property-level code-enforcement", code["note"])
        self.assertIn(
            "Confirm the enforcing municipality for each property",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("failed DNS resolution", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.leecountyal.gov/government/"
            "probate_judge/recording/index.php",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            pre_foreclosure["directory_url"],
        )
        self.assertIn("public stations in the Probate Office", pre_foreclosure["note"])
        self.assertIn("returned 404", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default feed", pre_foreclosure["note"])

    def test_limestone_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Limestone County", "01083")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Limestone",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.limestonerevenue.net/",
        )
        self.assertIn(
            "links the Limestone County Citizen Access Portal",
            assessor["note"],
        )
        self.assertIn("JavaScript-only application shell", assessor["note"])
        self.assertIn("is not permission to extract data", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.limestonerevenue.net/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_44.PDF",
        )
        self.assertIn("no current Limestone County tax-sale date", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.limestonecounty-al.gov/Home",
        )
        self.assertIn("did not identify a property-level", code["note"])
        self.assertIn(
            "Confirm the responsible provider by each property's municipality",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn(
            "no Limestone County sheriff-sale calendar",
            foreclosure["note"],
        )
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Limestone_Probate/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            pre_foreclosure["directory_url"],
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_lowndes_sources_record_verified_links_and_source_limits(self):
        sources = county_source_links("AL", "Lowndes County", "01085")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Lowndes",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.alabamagis.com/lowndes/",
        )
        self.assertIn("links this Lowndes County public GIS", assessor["note"])
        self.assertIn(
            "rather than official ownership records",
            assessor["note"],
        )
        self.assertIn("No documented bulk assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "tax-delinquent-property-and-land-sales/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_45.PDF",
        )
        self.assertIn("no current County tax-sale date", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Lowndes",
        )
        self.assertIn("no County property-level code-enforcement provider", code["note"])
        self.assertIn(
            "Confirm the responsible provider by each property's municipality",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no Lowndes County sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Lowndes_Probate/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            pre_foreclosure["directory_url"],
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_macon_sources_record_current_tax_lien_list_and_access_limits(self):
        sources = county_source_links("AL", "Macon County", "01087")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Macon",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://macon.capturecama.com/",
        )
        self.assertIn("links this Citizen Access Portal", assessor["note"])
        self.assertIn("JavaScript application shell", assessor["note"])
        self.assertIn("No documented bulk assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://maconcountyal.com/2025-tax-lien-list/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_46.PDF",
        )
        self.assertIn("modified April 8, 2026", tax_sale["note"])
        self.assertIn("May 12, 2026 at 10:00 a.m.", tax_sale["note"])
        self.assertIn("That sale date has passed", tax_sale["note"])
        self.assertIn("annual PDF is a static snapshot", tax_sale["note"])
        self.assertIn("no documented recurring API", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["directory_url"], "https://maconcountyal.com/")
        self.assertIn("not code enforcement", code["note"])
        self.assertIn("No property-level County code-enforcement office", code["note"])
        self.assertIn(
            "Confirm the responsible provider by each property's municipality",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no Macon County sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Macon_Probate/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            pre_foreclosure["directory_url"],
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_madison_sources_record_access_limits_and_tax_transcript(self):
        sources = county_source_links("AL", "Madison County", "01089")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Madison",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://madisonproperty.countygovservices.com/"
            "Property/Property/Search",
        )
        self.assertIn("links this property-record search", assessor["note"])
        self.assertIn("returned HTTP 403", assessor["note"])
        self.assertIn("robots.txt and terms-of-use routes returned 404", assessor["note"])
        self.assertIn("no bulk assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "tax-delinquent-property-and-land-sales/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_47.PDF",
        )
        self.assertIn("returned HTTP 403", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.madisoncountyal.gov/",
        )
        self.assertIn("No countywide property-level", code["note"])
        self.assertIn(
            "Confirm the responsible provider by each property's municipality",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("sheriff-sale calendar or list could not be inspected", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.madisoncountyal.gov/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.madisoncountyal.gov/",
        )
        self.assertIn("returned 404", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_marengo_sources_record_auction_details_and_access_limits(self):
        sources = county_source_links("AL", "Marengo County", "01091")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Marengo",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://marengo.alabamagis.com/Marengo/",
        )
        self.assertIn("requires a business personal property", assessor["note"])
        self.assertIn("returned a GIS welcome page", assessor["note"])
        self.assertIn("route returned HTTP 503", assessor["note"])
        self.assertIn("No documented residential bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.marengocountyal.com/home/revenue/"
            "tax-lien-information/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_48.PDF",
        )
        self.assertIn("May 5, 2026 at 8:30 a.m.", tax_sale["note"])
        self.assertIn("that date has passed", tax_sale["note"])
        self.assertIn("held once per year between March 1 and June 15", tax_sale["note"])
        self.assertIn("expressly prohibits automated systems", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["directory_url"], "https://www.marengocountyal.com/")
        self.assertIn("No documented export/API", code["note"])
        self.assertIn("Confirm the responsible provider by each property's municipality", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("redirected to the general homepage", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.marengocountyal.com/home/probate/"
            "office-of-the-probate-judge/welcome-to-the-probate-office/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            pre_foreclosure["directory_url"],
        )
        self.assertIn("returned 404", pre_foreclosure["note"])
        self.assertIn("No public county lis-pendens/default index", pre_foreclosure["note"])

    def test_marion_sources_record_live_links_and_access_limits(self):
        sources = county_source_links("AL", "Marion County", "01093")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Marion",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://marion.alabamagis.com/marion/",
        )
        self.assertIn("links the County website and public GIS", assessor["note"])
        self.assertIn("public GIS welcome page", assessor["note"])
        self.assertIn("No documented residential parcel export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.marioncountyal.org/home/departments/"
            "revenue-commissioner/tax-commission/property-tax-office/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_49.PDF",
        )
        self.assertIn("DELINQUENT LIST UNAVAILABLE", tax_sale["note"])
        self.assertIn("did not provide a current tax-sale date", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.marioncountyal.org/home/departments/",
        )
        self.assertIn("No documented export/API", code["note"])
        self.assertIn("Confirm the responsible provider by each property's municipality", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.marionsoal.com/civil-process",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("publishes no real-estate sale calendar or list", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.marioncountyal.org/home/departments/"
            "probate-office/public-records/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Marion_Probate/default.aspx",
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("A specific public lis-pendens/default index", pre_foreclosure["note"])

    def test_marshall_sources_record_tax_schedule_and_access_limits(self):
        sources = county_source_links("AL", "Marshall County", "01095")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Marshall",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://marshall.countygovservices.com/property/"
            "Property/Search",
        )
        self.assertIn("links this CountyGovServices property-tax search", assessor["note"])
        self.assertIn("ISV3 map", assessor["note"])
        self.assertIn("No documented residential bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://marshallrc.org/property-tax-information/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_50.PDF",
        )
        self.assertIn("first Tuesday in May", tax_sale["note"])
        self.assertIn("not an event-specific notice or parcel sale list", tax_sale["note"])
        self.assertIn("usual May window had passed", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.marshallal.gov/departments/solidwaste/"
            "solidwaste.html",
        )
        self.assertIn("responsible for license inspection", code["note"])
        self.assertIn("No documented export/API", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.marshallso.org/calendar",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("currently says there are no items available", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.marshallal.gov/departments/probate/"
            "probate.html",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Marshall_Probate/",
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("A specific public lis-pendens/default index", pre_foreclosure["note"])

    def test_mobile_sources_record_tax_auction_and_access_limits(self):
        sources = county_source_links("AL", "Mobile County", "01097")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Mobile",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://esearch.mobilecopropertytax.com/",
        )
        self.assertIn("displays 2026 values", assessor["note"])
        self.assertIn("Terms restrict commercial endeavors", assessor["note"])
        self.assertIn("prohibit unauthorized data scrubbing", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://mobilecopropertytax.com/taxliensale/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_02.PDF",
        )
        self.assertIn("May 11, 2026, starting at 8:30 a.m. CDT", tax_sale["note"])
        self.assertIn("10,506 data rows", tax_sale["note"])
        self.assertIn("8,963 data rows", tax_sale["note"])
        self.assertIn("not a daily feed", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.mobilecountyal.gov/government/departments/"
            "environmental-enforcement/",
        )
        self.assertIn("in unincorporated Mobile County", code["note"])
        self.assertIn("Inspection Services regulates construction", code["note"])
        self.assertIn("publish no searchable property-level violation", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.mobileso.com/civil-division-central-records/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("foreclosures are non-judicial", foreclosure["note"])
        self.assertIn("failed HTTPS retrieval", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://probate.mobilecountyal.gov/public-records/"
            "records-search",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://benchmark.probate.mobilecountyal.gov/"
            "LandmarkWeb/Account/LogOn/",
        )
        self.assertIn("records from 1813 to the present", pre_foreclosure["note"])
        self.assertIn("Index search requires registration", pre_foreclosure["note"])
        self.assertIn("No documented bulk export/API", pre_foreclosure["note"])

    def test_monroe_sources_record_portal_limits_and_missing_sale_feeds(self):
        sources = county_source_links("AL", "Monroe County", "01099")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Monroe",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://monroe.capturecama.com/CAPortal_MainPage.aspx",
        )
        self.assertIn("generic Citizen Access Portal application shell", assessor["note"])
        self.assertIn("No documented residential data export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Monroe",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_51.PDF",
        )
        self.assertIn("no Monroe County tax-sale calendar", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Monroe",
        )
        self.assertIn("do not identify a code-enforcement provider", code["note"])
        self.assertIn("Confirm the responsible provider by each property's municipality", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("No Monroe County sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Monroe",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Monroe_Probate/",
        )
        self.assertIn("identifies the Monroe County License Commissioner", pre_foreclosure["note"])
        self.assertIn("not a Probate land-records", pre_foreclosure["note"])
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])

    def test_montgomery_sources_record_access_limits_and_missing_sale_feeds(self):
        sources = county_source_links("AL", "Montgomery County", "01101")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Montgomery",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://montgomery.capturecama.com/",
        )
        self.assertIn("returned HTTP 403", assessor["note"])
        self.assertIn("generic Citizen Access Portal application shell", assessor["note"])
        self.assertIn("No documented parcel export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Montgomery",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_03.PDF",
        )
        self.assertIn("no local tax-sale calendar", tax_sale["note"])
        self.assertIn("not a local auction calendar", tax_sale["note"])
        self.assertIn("lack physical addresses", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Montgomery",
        )
        self.assertIn("returned HTTP 403", code["note"])
        self.assertIn("do not identify a code-enforcement provider", code["note"])
        self.assertIn(
            "Confirm the responsible provider for each property's municipality",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("No Montgomery County sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Montgomery_Probate/",
        )
        self.assertIn("identifies the County Commission and Judge of Probate", pre_foreclosure["note"])
        self.assertIn("terms expressly prohibit automated systems", pre_foreclosure["note"])
        self.assertIn("No bulk export/API", pre_foreclosure["note"])

    def test_morgan_sources_record_annual_sale_and_portal_limits(self):
        sources = county_source_links("AL", "Morgan County", "01103")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Morgan",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://morgan.capturecama.com/CA_ParcelSearch.aspx",
        )
        self.assertIn("uploaded frequently", assessor["note"])
        self.assertIn("generic application shell", assessor["note"])
        self.assertIn("does not grant data-extraction authorization", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.morgancountyrevenue.com/tax-sale",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_52.PDF",
        )
        self.assertIn("May 12, 2026", tax_sale["note"])
        self.assertIn("contains 750 parcel entries", tax_sale["note"])
        self.assertIn("robots.txt disallows /images/", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Morgan",
        )
        self.assertIn("timed out on both HTTP and HTTPS", code["note"])
        self.assertIn("do not identify a county code-enforcement provider", code["note"])
        self.assertIn(
            "confirm the responsible provider for each property's municipality",
            code["note"],
        )

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("No Morgan County sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Morgan",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "http://www.morgancountyprobate.com/",
        )
        self.assertIn("document searches require a username and password", pre_foreclosure["note"])
        self.assertIn("returned HTTP 404", pre_foreclosure["note"])
        self.assertIn("No authorized daily pre-foreclosure feed", pre_foreclosure["note"])

    def test_perry_sources_record_gis_and_delinquent_list_limits(self):
        sources = county_source_links("AL", "Perry County", "01105")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Perry",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://perry.alabamagis.com/perry/",
        )
        self.assertIn("GIS welcome page", assessor["note"])
        self.assertIn("empty response body", assessor["note"])
        self.assertIn("no residential assessment export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "tax-delinquent-property-and-land-sales/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_53.PDF",
        )
        self.assertIn("generated 2026-10-19", tax_sale["note"])
        self.assertIn("not physical addresses or a local auction calendar", tax_sale["note"])
        self.assertIn("no Perry-specific auction date", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Perry",
        )
        self.assertIn("does not identify a code-enforcement provider", code["note"])
        self.assertIn("property-level violation feed", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("No Perry County sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Perry_Probate/",
        )
        self.assertIn("identifies the Perry County Commission and Perry Probate Judge", pre_foreclosure["note"])
        self.assertIn("terms expressly prohibit automated systems", pre_foreclosure["note"])
        self.assertIn("No bulk export/API", pre_foreclosure["note"])

    def test_pickens_sources_record_portal_and_transcript_limits(self):
        sources = county_source_links("AL", "Pickens County", "01107")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Pickens",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://taxes.pickensalabama.com/#/",
        )
        self.assertIn("rendered only a Loading screen", assessor["note"])
        self.assertIn("robots.txt route returned the same app shell", assessor["note"])
        self.assertIn("No accessible residential parcel search", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "tax-delinquent-property-and-land-sales/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_54.PDF",
        )
        self.assertIn("generated 2026-10-19", tax_sale["note"])
        self.assertIn("contains only the report header", tax_sale["note"])
        self.assertIn("No Pickens-specific sale date", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Pickens",
        )
        self.assertIn("do not identify a code-enforcement provider", code["note"])
        self.assertIn("property-level violation feed", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("No Pickens County sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Pickens_Probate/",
        )
        self.assertIn("identifies the Pickens County Commission and Pickens Judge of Probate", pre_foreclosure["note"])
        self.assertIn("terms expressly prohibit automated systems", pre_foreclosure["note"])
        self.assertIn("No bulk export/API", pre_foreclosure["note"])

    def test_randolph_sources_record_broken_gis_and_access_limits(self):
        sources = county_source_links("AL", "Randolph County", "01111")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Randolph",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://isv.kcsgis.com/al.randolph_revenue/",
        )
        self.assertIn("returned HTTP 404", assessor["note"])
        self.assertIn("No alternate public residential assessment search", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "tax-delinquent-property-and-land-sales/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_56.PDF",
        )
        self.assertIn("generated 2026-10-19", tax_sale["note"])
        self.assertIn("not physical addresses or the local auction calendar", tax_sale["note"])
        self.assertIn("No Randolph-specific auction date", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Randolph",
        )
        self.assertIn("returned HTTP 404", code["note"])
        self.assertIn("does not identify a code-enforcement provider", code["note"])
        self.assertIn("property-level violation feed", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("No Randolph County sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Randolph_Probate/",
        )
        self.assertIn("identifies the Randolph County Commission and Randolph Judge of Probate", pre_foreclosure["note"])
        self.assertIn("terms expressly prohibit automated systems", pre_foreclosure["note"])
        self.assertIn("No bulk export/API", pre_foreclosure["note"])

    def test_pike_sources_record_tax_method_and_access_limits(self):
        sources = county_source_links("AL", "Pike County", "01109")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Pike",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.pikerevenue.com/home/taxpayer-search-and-pay/",
        )
        self.assertIn("may be slightly dated", assessor["note"])
        self.assertIn("BPP location number and access code", assessor["note"])
        self.assertIn("expressly prohibits automated systems", assessor["note"])
        self.assertIn("No residential bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.pikerevenue.com/home/news/main/"
            "?pg=News&action=view&aid=30",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_55.PDF",
        )
        self.assertIn("tax-lien auction method for 2020-2021", tax_sale["note"])
        self.assertIn("does not provide an event-specific sale date", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])
        self.assertIn("No current Pike sale schedule", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Pike",
        )
        self.assertIn("do not identify a code-enforcement provider", code["note"])
        self.assertIn("property-level violation feed", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("No Pike County sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Pike",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.ingprobate.com/Pike_Probate/",
        )
        self.assertIn("returned HTTP 404", pre_foreclosure["note"])
        self.assertIn("No verified public lis-pendens/default index", pre_foreclosure["note"])
        self.assertIn("No authorized daily feed", pre_foreclosure["note"])

    def test_russell_sources_record_application_shells_and_access_limits(self):
        sources = county_source_links("AL", "Russell County", "01113")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Russell",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://russell.capturecama.com/",
        )
        self.assertIn("Revenue site rendered only a Loading screen", assessor["note"])
        self.assertIn("generic Citizen Access Portal shell", assessor["note"])
        self.assertIn("No accessible residential parcel export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.russellcountyrevenuecommissioner.com/#/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_57.PDF",
        )
        self.assertIn("no local tax-sale date", tax_sale["note"])
        self.assertIn("10-page weekly state-held delinquent-land inventory", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Russell",
        )
        self.assertIn("do not identify a code-enforcement provider", code["note"])
        self.assertIn("property-level violation feed", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("No Russell County sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.ingprobate.com/Russell_Probate/",
        )
        self.assertIn("identifies the Russell County Commission and Russell County Judge of Probate", pre_foreclosure["note"])
        self.assertIn("terms expressly prohibit automated systems", pre_foreclosure["note"])
        self.assertIn("No bulk export/API", pre_foreclosure["note"])

    def test_shelby_sources_record_portal_and_records_search_limits(self):
        sources = county_source_links("AL", "Shelby County", "01117")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Shelby",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://ptc.shelbyal.com/",
        )
        self.assertIn("generic Citizen Access Portal shell", assessor["note"])
        self.assertIn("unsupported-browser message", assessor["note"])
        self.assertIn("No documented residential bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.shelbyal.com/490/Property-Tax-Commissioner",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_58.PDF",
        )
        self.assertIn("no local tax-sale date", tax_sale["note"])
        self.assertIn("11-page weekly state-held delinquent-land inventory", tax_sale["note"])
        self.assertIn("not the local auction calendar", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.shelbyal.com/236/Permits-and-Inspections",
        )
        self.assertIn("do not expose a searchable property-level violation", code["note"])
        self.assertIn("do not establish coverage of municipal jurisdictions", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.shelbyso.com/101/Services",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("did not expose a civil-process foreclosure-sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://probaterecords.shelbyal.com/shelby/search.do",
        )
        self.assertIn("requires acceptance of its Terms of Use", pre_foreclosure["note"])
        self.assertIn("older mortgage cancellations", pre_foreclosure["note"])
        self.assertIn("or explicit permission for automated access", pre_foreclosure["note"])

    def test_st_clair_sources_record_tax_sale_schedule_and_access_limits(self):
        sources = county_source_links("AL", "St. Clair County", "01115")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#St.%20Clair",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.ingproperty.com/StClair_Revenue/property.aspx",
        )
        self.assertIn("tax-year filters through 2027", assessor["note"])
        self.assertIn("requires a BPP location number/access code", assessor["note"])
        self.assertIn("expressly prohibits automated systems", assessor["note"])
        self.assertIn("treat the property search as manual-only", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.stclairco.com/418/Tax-Lien-Auction",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_59.PDF",
        )
        self.assertIn("typically during the first week of May", tax_sale["note"])
        self.assertIn("May 5, 2026 at 9:00 AM", tax_sale["note"])
        self.assertIn("no 2027 date was posted", tax_sale["note"])
        self.assertIn("manual-only absent written permission", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.stclairco.com/SiteMap",
        )
        self.assertIn("did not identify a code-enforcement provider", code["note"])
        self.assertIn("property-level violation feed", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.stclairsheriff.org/civil-process",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("conducts sheriff's sales", foreclosure["note"])
        self.assertIn("publishes no searchable sale calendar/list", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.stclairco.com/232/Probate-Office",
        )
        self.assertIn("returned HTTP 404", pre_foreclosure["note"])
        self.assertIn("no public land-record or lis-pendens/default search", pre_foreclosure["note"])
        self.assertIn("No public pre-foreclosure source", pre_foreclosure["note"])


    def test_sumter_sources_record_official_links_and_feed_gaps(self):
        sources = county_source_links("AL", "Sumter County", "01119")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Sumter",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://sumter.capturecama.com/CAPortal_MainPage.aspx",
        )
        self.assertIn("rendered only its 'Citizen Access Portal' title", assessor["note"])
        self.assertIn("GIS redirected to a welcome page", assessor["note"])
        self.assertIn("No working parcel results, bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://sumtercountyal.com/tax-collector/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_60.PDF",
        )
        self.assertIn("no current tax-sale date, list, or auction platform", tax_sale["note"])
        self.assertIn("one-page weekly state-held delinquent-land inventory", tax_sale["note"])
        self.assertIn("not the County auction calendar", tax_sale["note"])
        self.assertIn("No recurring local sale feed", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["directory_url"], "https://sumtercountyal.com/")
        self.assertIn("did not identify a code-enforcement provider", code["note"])
        self.assertIn("property-level violation feed", code["note"])
        self.assertIn("confirm the responsible provider", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://sumtercountyal.com/sheriffjail/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no civil-process sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])
        self.assertIn("No authorized daily foreclosure source", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://sumtercountyal.com/judge-of-probate/",
        )
        self.assertIn("no electronic land-record search", pre_foreclosure["note"])
        self.assertIn("No public bulk export/API", pre_foreclosure["note"])
        self.assertIn("manual office discovery only", pre_foreclosure["note"])


    def test_talladega_sources_record_county_portals_and_sale_gaps(self):
        sources = county_source_links("AL", "Talladega County", "01121")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Talladega",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.talladegacountyal.org/departments/"
            "appraisal/index.php",
        )
        self.assertIn("no public parcel-search link", assessor["note"])
        self.assertIn("route at https://www.alabamagis.com/Talladega returned HTTP 404", assessor["note"])
        self.assertIn("No working parcel export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.talladegacountyal.org/government/"
            "revenue_commission.php",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_61.PDF",
        )
        self.assertIn("no current tax-sale date, list, or auction platform", tax_sale["note"])
        self.assertIn("not the County auction calendar", tax_sale["note"])
        self.assertIn("No recurring local sale feed", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.talladegacountyal.org/departments/"
            "highway/permits_and_zoning.php",
        )
        self.assertIn("does not expose a searchable property-level code violation feed", code["note"])
        self.assertIn("No countywide or municipal provider", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.talladegacountyal.org/government/sheriff.php",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no civil-process sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.talladegacountyal.org/departments/"
            "probate_office/index.php",
        )
        self.assertIn("records deeds, mortgages, judgments, and liens", pre_foreclosure["note"])
        self.assertIn("no public online record search", pre_foreclosure["note"])
        self.assertIn("manual office discovery only", pre_foreclosure["note"])


    def test_tallapoosa_sources_record_auction_and_portal_restrictions(self):
        sources = county_source_links("AL", "Tallapoosa County", "01123")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Tallapoosa",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://altags.com/Tallapoosa_Revenue/default.aspx",
        )
        self.assertIn("GIS redirects to a welcome page", assessor["note"])
        self.assertIn("expressly prohibits automated systems", assessor["note"])
        self.assertIn("offline readers, data extraction", assessor["note"])
        self.assertIn("BPP location number/access code", assessor["note"])
        self.assertIn("No authorization for daily/commercial automation", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://tallaco.com/resources/taxes/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_62.PDF",
        )
        self.assertIn("online-only and conducted once per year", tax_sale["note"])
        self.assertIn("generic GovEase homepage", tax_sale["note"])
        self.assertIn("redirects to the general Revenue Commission homepage", tax_sale["note"])
        self.assertIn("one-page weekly state-held delinquent-land inventory", tax_sale["note"])
        self.assertIn("No authorized daily sale feed", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://tallaco.com/departments/building/",
        )
        self.assertIn("enforces adopted building", code["note"])
        self.assertIn("no searchable property-level violation/inspection case data", code["note"])
        self.assertIn("municipal code-enforcement providers remain unverified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://tallaco.com/departments/sheriff/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no civil-process sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://tallaco.com/departments/probate-office/real-estate/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://tallapoosaprobate.countygovservices.com/",
        )
        self.assertIn("computer indexes beginning in October 1985", pre_foreclosure["note"])
        self.assertIn("redirects unauthenticated visitors to sign-in", pre_foreclosure["note"])
        self.assertIn("No anonymous public lis-pendens/default index", pre_foreclosure["note"])

    def test_tuscaloosa_sources_record_sale_list_and_access_limits(self):
        sources = county_source_links("AL", "Tuscaloosa County", "01125")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.tuscco.com/tax-assessor/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://altags.com/Tuscaloosa_Revenue/default.aspx",
        )
        self.assertIn("GIS route at https://www.alabamagis.com/Tuscaloosa", assessor["note"])
        self.assertIn("AlTags legal disclaimer prohibits", assessor["note"])
        self.assertIn("automated logins, and interactions", assessor["note"])
        self.assertIn("treat assessment lookup as manual-only", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.tuscco.com/tax-collector/tax-lien-sale/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.tuscco.com/wp-content/uploads/2026/06/"
            "Copy-of-List-for-IT-2025-Tax-Year-Prop-did-not-sell-002.pdf",
        )
        self.assertIn("generic GovEase", tax_sale["note"])
        self.assertIn("published in April 2022", tax_sale["note"])
        self.assertIn("created June 18, 2026", tax_sale["note"])
        self.assertIn("post-sale unsold-property list", tax_sale["note"])
        self.assertIn("WWW_TRANS_63.PDF", tax_sale["note"])
        self.assertIn("No recurring local feed", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.tuscco.com/public-works/environmental/",
        )
        self.assertIn("no property-level building/code violation", code["note"])
        self.assertIn("confirm the code authority for each property's municipality", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.tuscco.com/county-officials/sheriff/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no civil-process sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])
        self.assertIn("No authorized county foreclosure notice feed", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.tuscco.com/probate/records-and-recordings/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://probate.tuscco.com/ProbateWeb/",
        )
        self.assertIn("Search Probate Records", pre_foreclosure["note"])
        self.assertIn("Microsoft B2C sign-up/sign-in flow", pre_foreclosure["note"])
        self.assertIn("No public lis-pendens/default index", pre_foreclosure["note"])

    def test_walker_sources_record_upcoming_sale_and_access_limits(self):
        sources = county_source_links("AL", "Walker County", "01127")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.walkercountyrevenue.com/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.walkercountyrevenue.com/#/property",
        )
        self.assertIn("online property-tax search/view/pay service", assessor["note"])
        self.assertIn("resolve to an Alabamagis welcome page", assessor["note"])
        self.assertIn("no parcel bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.walkercountyrevenue.com/tax-sale/",
        )
        self.assertEqual(tax_sale["source_url"], tax_sale["directory_url"])
        self.assertIn("May 3, 2027 at 8:30 a.m.", tax_sale["note"])
        self.assertIn("scheduled for April 2, 2027", tax_sale["note"])
        self.assertIn("2027 parcel list was not yet posted", tax_sale["note"])
        self.assertIn("WWW_TRANS_64.PDF", tax_sale["note"])
        self.assertIn("No machine-readable list feed", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.walkercountyal.us/administrator/engineering/",
        )
        self.assertIn("no general building regulations", code["note"])
        self.assertIn("No countywide property-level code-enforcement feed", code["note"])
        self.assertIn("Municipal and environmental enforcement providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://walkercountysheriff.com/index.html",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("sitemap, last modified in 2017", foreclosure["note"])
        self.assertIn("no civil-process sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.walkercountyprobate.com/records/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://ingprobate.com/Walker_Probate/",
        )
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("automated account creation/logins", pre_foreclosure["note"])
        self.assertIn("No lis-pendens/default index", pre_foreclosure["note"])

    def test_washington_sources_record_missing_feeds_and_portal_limits(self):
        sources = county_source_links("AL", "Washington County", "01129")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Washington",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.alabamagis.com/Washington/",
        )
        self.assertIn("GIS resolves to a welcome page", assessor["note"])
        self.assertIn("returned HTTP 404", assessor["note"])
        self.assertIn("No working parcel results", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Washington",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_65.PDF",
        )
        self.assertIn("no County Revenue/property-tax website", tax_sale["note"])
        self.assertIn("one-page weekly state-held", tax_sale["note"])
        self.assertIn("not the County auction calendar", tax_sale["note"])
        self.assertIn("contact the Revenue Commissioner's Office", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertIn("no countywide property-level code-enforcement provider", code["note"])
        self.assertIn("check the authority for each property's municipality", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.washingtoncountysheriff.org/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("no civil-process sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])
        self.assertIn("No authorized county foreclosure notice feed", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(pre_foreclosure["directory_url"], "https://washprobate.com/")
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://ingprobate.com/washington_probate/default.aspx",
        )
        self.assertIn("online records search", pre_foreclosure["note"])
        self.assertIn("prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No dedicated lis-pendens/default feed", pre_foreclosure["note"])

    def test_wilcox_sources_record_portal_failures_and_access_limits(self):
        sources = county_source_links("AL", "Wilcox County", "01131")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Wilcox",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://wilcox.capturecama.com/CAPortal_MainPage.aspx",
        )
        self.assertIn("rendered only its 'Citizen Access Portal' title", assessor["note"])
        self.assertIn("GIS resolves to a welcome page", assessor["note"])
        self.assertIn("No working parcel results", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_66.PDF",
        )
        self.assertIn("no County sale date", tax_sale["note"])
        self.assertIn("one-page weekly state-held", tax_sale["note"])
        self.assertIn("not the County auction calendar", tax_sale["note"])
        self.assertIn("No recurring local sale feed", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertIn("no countywide property-level", code["note"])
        self.assertIn("confirm the authority for each property's municipality", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("No Wilcox County Sheriff's sale calendar", foreclosure["note"])
        self.assertIn("manual office discovery, not a sales feed", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://ingprobate.com/Wilcox_Probate/",
        )
        self.assertEqual(pre_foreclosure["source_url"], pre_foreclosure["directory_url"])
        self.assertIn("identifies the Wilcox County Commission", pre_foreclosure["note"])
        self.assertIn("expressly prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No dedicated lis-pendens/default feed", pre_foreclosure["note"])

    def test_arkansas_county_sources_identify_interactive_assessor_and_state_sale_catalog(self):
        sources = county_source_links("AR", "Arkansas County", "05001")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/arkansas/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Arkansas&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("not an Arkansas County auction calendar", tax_sale["note"])
        self.assertIn("did not expose an Arkansas County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/arkansas/",
        )
        self.assertIn("no countywide violation feed was identified", code["note"])
        self.assertIn("Municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/arkansas/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission is required", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.arcounties.org/counties/arkansas/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Arkansas County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_ashley_sources_do_not_claim_an_assessor_portal_or_daily_feed(self):
        sources = county_source_links("AR", "Ashley County", "05003")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/ashley/",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("lists 35 counties and excludes Ashley", assessor["note"])
        self.assertIn("redirected to the generic homepage", assessor["note"])
        self.assertIn("No other county-specific parcel search", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose an Ashley County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/ashley/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/ashley/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("No Ashley County Sheriff's sale calendar", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission is required", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Ashley County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_baxter_sources_identify_assessor_search_but_not_a_daily_feed(self):
        sources = county_source_links("AR", "Baxter County", "05005")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/baxter/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Baxter&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Baxter County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/baxter/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/baxter/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Baxter County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_benton_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Benton County", "05007")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/benton/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Benton&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Benton County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/benton/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/benton/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Benton County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_boone_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Boone County", "05009")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/boone/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Boone&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Boone County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/boone/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/boone/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Boone County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_bradley_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Bradley County", "05011")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/bradley/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Bradley&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Bradley County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/bradley/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/bradley/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Bradley County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_calhoun_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Calhoun County", "05013")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/calhoun/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Calhoun&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Calhoun County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/calhoun/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/calhoun/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Calhoun County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_carroll_sources_flag_paid_stale_assessor_data(self):
        sources = county_source_links("AR", "Carroll County", "05015")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/carroll/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Carroll&s=R",
        )
        self.assertIn("Paid Users Login button", assessor["note"])
        self.assertIn("no free public-search interface", assessor["note"])
        self.assertIn("Collector Data last updated 2024-12-13", assessor["note"])
        self.assertIn("no assessor-data date is displayed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily ingestion was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a Carroll County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/carroll/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Carroll County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_chicot_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Chicot County", "05017")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/chicot/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Chicot&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Chicot County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/chicot/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/chicot/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Chicot County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_clark_sources_distinguish_collector_search_from_assessor_data(self):
        sources = county_source_links("AR", "Clark County", "05019")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/clark/",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("labeled Search Tax Records / Receipts", assessor["note"])
        self.assertIn("Collector sponsors a free public search", assessor["note"])
        self.assertIn("not an Assessor valuation/parcel search", assessor["note"])
        self.assertIn("No separate county assessor search", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a Clark County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/clark/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Clark County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_clay_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Clay County", "05021")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/clay/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Clay&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Clay County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/clay/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/clay/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Clay County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_cleburne_sources_distinguish_collector_search_and_county_site_shell(self):
        sources = county_source_links("AR", "Cleburne County", "05023")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/cleburne/",
        )
        self.assertEqual(assessor["source_url"], "https://www.cleburnecountyar.com/")
        self.assertIn("only a Wix shell", assessor["note"])
        self.assertIn("Collector-sponsored search", assessor["note"])
        self.assertIn("not assessor valuation data", assessor["note"])
        self.assertIn("No county-specific assessor search", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a Cleburne County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://www.cleburnecountyar.com/")
        self.assertIn("without code-enforcement links", code["note"])
        self.assertIn("No countywide violation feed", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or foreclosure list", foreclosure["note"])
        self.assertIn("Written permission is required", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Cleburne County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_cleveland_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Cleveland County", "05025")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/cleveland/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Cleveland&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Cleveland County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/cleveland/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/cleveland/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Cleveland County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_columbia_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Columbia County", "05027")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/columbia/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Columbia&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Columbia County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/columbia/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/columbia/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Columbia County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_conway_sources_record_absence_from_property_data_vendor(self):
        sources = county_source_links("AR", "Conway County", "05029")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/conway/",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("lists 35 counties and excludes Conway", assessor["note"])
        self.assertIn("redirected to the generic homepage", assessor["note"])
        self.assertIn("No Conway assessor parcel search", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a Conway County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/conway/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Conway County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_craighead_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Craighead County", "05031")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/craighead/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Craighead&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Craighead County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/craighead/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/craighead/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Craighead County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_crittenden_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Crittenden County", "05035")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/crittenden/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Crittenden&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Crittenden County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/crittenden/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/crittenden/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Crittenden County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_boone_sources_confirm_search_terms_and_code_complaint_limits(self):
        sources = county_source_links("MO", "Boone County", "29019")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.boonemo.gov/assessor/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://report.boonemo.gov/mrcjava/servlet/AS00_MP.I00240s",
        )
        self.assertIn("live real-property search", assessor["note"])
        self.assertIn("personal, informational, non-commercial use", assessor["note"])
        self.assertIn("prior written consent", assessor["note"])
        self.assertIn("No public bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.boonemo.gov/collector/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("primary tax records are held for public use", tax_sale["note"])
        self.assertIn("does not provide a delinquent-tax-sale calendar", tax_sale["note"])
        self.assertIn("no current Boone-specific sale list", tax_sale["note"])
        self.assertIn("prohibit scraping and automation", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.boonemo.gov/resource-management/planning-zoning/",
        )
        self.assertIn("investigates zoning complaints", code["note"])
        self.assertIn("redirected to a login", code["note"])
        self.assertIn("not a public violation list", code["note"])
        self.assertIn("Columbia and other municipal jurisdictions", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.boonemo.gov/sheriff/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("did not expose a real-estate foreclosure", foreclosure["note"])
        self.assertIn("no current Boone-specific sale list", foreclosure["note"])
        self.assertIn("prohibit scraping and automation", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.courts.mo.gov/hosted/circuit13/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.courts.mo.gov/cnet/cases/newHeader.do",
        )
        self.assertIn("both returned HTTP 403", pre_foreclosure["note"])
        self.assertIn("No Boone-specific bulk default/lis-pendens feed", pre_foreclosure["note"])

    def test_bollinger_sources_confirm_vendor_restrictions_and_manual_sales(self):
        sources = county_source_links("MO", "Bollinger County", "29017")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.mocounties.com/bollinger-county",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://bollinger.missouriassessors.com/search.php",
        )
        self.assertIn("identifies Bollinger County", assessor["note"])
        self.assertIn("adjoining jurisdiction notice", assessor["note"])
        self.assertIn("Terms prohibit data mining, robots, screen scraping", assessor["note"])
        self.assertIn("without express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://bollingermo.devnetwedge.com/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("tax-payment site", tax_sale["note"])
        self.assertIn("does not expose a delinquent tax-sale calendar", tax_sale["note"])
        self.assertIn("no current Bollinger-specific list", tax_sale["note"])
        self.assertIn("prohibit scraping and automation", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], code["directory_url"])
        self.assertIn("not a code-enforcement service", code["note"])
        self.assertIn("No countywide property-level violation portal", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("not a foreclosure or sheriff-sale calendar", foreclosure["note"])
        self.assertIn("no current Bollinger-specific sale list", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.courts.mo.gov/cnet/cases/newHeader.do",
        )
        self.assertIn("not a property-default or lis-pendens index", pre_foreclosure["note"])
        self.assertIn("returned HTTP 403", pre_foreclosure["note"])
        self.assertIn("No Bollinger-specific bulk pre-foreclosure feed", pre_foreclosure["note"])

    def test_benton_sources_record_missing_parcel_and_sale_feeds(self):
        sources = county_source_links("MO", "Benton County", "29015")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.mocounties.com/benton-county",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://stc.mo.gov/assessor/assessor-directory/",
        )
        self.assertIn("lists the Assessor's contact", assessor["note"])
        self.assertIn("displayed a 2013 date", assessor["note"])
        self.assertIn("returned an Admin page", assessor["note"])
        self.assertIn("returned HTTP 404", assessor["note"])
        self.assertIn("no current Benton parcel search", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.mocounties.com/benton-county",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("lists the Collector's contact", tax_sale["note"])
        self.assertIn("not a delinquent-tax-sale calendar", tax_sale["note"])
        self.assertIn("no current Benton-specific list", tax_sale["note"])
        self.assertIn("prohibit scraping and automation", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], code["directory_url"])
        self.assertIn("no countywide property-level code-enforcement service", code["note"])
        self.assertIn("Municipal providers remain unverified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("not a foreclosure or sheriff-sale calendar", foreclosure["note"])
        self.assertIn("no current Benton-specific sale list", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.courts.mo.gov/cnet/cases/newHeader.do",
        )
        self.assertIn("not a property-default or lis-pendens index", pre_foreclosure["note"])
        self.assertIn("returned HTTP 403", pre_foreclosure["note"])
        self.assertIn("No Benton-specific bulk pre-foreclosure feed", pre_foreclosure["note"])

    def test_bates_sources_record_unverified_assessor_and_manual_notice_limits(self):
        sources = county_source_links("MO", "Bates County", "29013")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.mocounties.com/bates-county",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://stc.mo.gov/assessor/assessor-directory/",
        )
        self.assertIn("displayed a 2013 date", assessor["note"])
        self.assertIn("returned an Admin page", assessor["note"])
        self.assertIn("returned HTTP 404", assessor["note"])
        self.assertIn("no current Bates parcel search", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("not a delinquent-tax-sale calendar", tax_sale["note"])
        self.assertIn("no current Bates-specific list", tax_sale["note"])
        self.assertIn("prohibit scraping and automation", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], code["directory_url"])
        self.assertIn("no countywide property-level code-enforcement service", code["note"])
        self.assertIn("Municipal providers remain unverified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("lists the Sheriff and Circuit Clerk contacts", foreclosure["note"])
        self.assertIn("no current Bates-specific sale list", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.courts.mo.gov/cnet/cases/newHeader.do",
        )
        self.assertIn("not a property-default or lis-pendens index", pre_foreclosure["note"])
        self.assertIn("returned HTTP 403", pre_foreclosure["note"])
        self.assertIn("No Bates-specific bulk pre-foreclosure feed", pre_foreclosure["note"])

    def test_barton_sources_confirm_assessor_search_and_restrict_automation(self):
        sources = county_source_links("MO", "Barton County", "29011")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.mocounties.com/barton-county",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://barton.missouriassessors.com/search.php",
        )
        self.assertIn("identifies the Barton County Assessor", assessor["note"])
        self.assertIn("interactive property search", assessor["note"])
        self.assertIn("property information is supplied as-is", assessor["note"])
        self.assertIn("Terms prohibit data mining, robots, screen scraping", assessor["note"])
        self.assertIn("without express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.mocounties.com/barton-county",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("not a delinquent tax-sale calendar", tax_sale["note"])
        self.assertIn("no current Barton-specific list", tax_sale["note"])
        self.assertIn("prohibit scraping and automation", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], code["directory_url"])
        self.assertIn("no countywide property-level code-enforcement service", code["note"])
        self.assertIn("Municipal providers remain unverified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("not a foreclosure or sheriff-sale calendar", foreclosure["note"])
        self.assertIn("no current Barton-specific sale list", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.courts.mo.gov/cnet/cases/newHeader.do",
        )
        self.assertIn("not a property-default or lis-pendens index", pre_foreclosure["note"])
        self.assertIn("returned HTTP 403", pre_foreclosure["note"])
        self.assertIn("No Barton-specific bulk pre-foreclosure feed", pre_foreclosure["note"])

    def test_barry_sources_reject_wrong_assessor_domain_and_restrict_notice_use(self):
        sources = county_source_links("MO", "Barry County", "29009")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://stc.mo.gov/assessor/assessor-directory/",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("displayed a 2013 date", assessor["note"])
        self.assertIn("not Barry County, Missouri", assessor["note"])
        self.assertIn("not a valid Barry parcel source", assessor["note"])
        self.assertIn("No current Barry-specific assessor portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.mocounties.com/barry-county",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("not a delinquent-tax-sale calendar", tax_sale["note"])
        self.assertIn("no current Barry-specific list", tax_sale["note"])
        self.assertIn("prohibit scraping and automation", tax_sale["note"])
        self.assertIn("use manual research only", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], code["directory_url"])
        self.assertIn("no countywide property-level code-enforcement service", code["note"])
        self.assertIn("Municipal code-enforcement providers remain unverified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.mocounties.com/barry-county",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("lists the Sheriff and Circuit Clerk contacts", foreclosure["note"])
        self.assertIn("no current Barry-specific sale list", foreclosure["note"])
        self.assertIn("prohibit scraping and automation", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.mocounties.com/barry-county",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.courts.mo.gov/cnet/cases/newHeader.do",
        )
        self.assertIn("not a property-default or lis-pendens index", pre_foreclosure["note"])
        self.assertIn("returned HTTP 403", pre_foreclosure["note"])
        self.assertIn("No Barry-specific bulk pre-foreclosure feed", pre_foreclosure["note"])

    def test_audrain_sources_confirm_assessor_portal_and_limit_automation(self):
        sources = county_source_links("MO", "Audrain County", "29007")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.audraincounty.org/assessor/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://audrain.missouriassessors.com/search.php",
        )
        self.assertIn("official County website links to the Vanguard", assessor["note"])
        self.assertIn("Terms prohibit data mining, robots, screen scraping", assessor["note"])
        self.assertIn("without express written consent", assessor["note"])
        self.assertIn("No bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.audraincounty.org/pay-county-taxes-online",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("method to pay county taxes", tax_sale["note"])
        self.assertIn("does not provide a delinquent tax-sale list or calendar", tax_sale["note"])
        self.assertIn("Audrain County and a Tax Sale category", tax_sale["note"])
        self.assertIn("prohibit scraping and automation", tax_sale["note"])
        self.assertIn("use manual research only", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.audraincounty.org/county-commission/",
        )
        self.assertEqual(code["source_url"], code["directory_url"])
        self.assertIn("did not expose a countywide property-level", code["note"])
        self.assertIn("Municipal providers, including Mexico and Vandalia", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.audraincounty.org/sheriff/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertIn("not a foreclosure/sheriff-sale calendar", foreclosure["note"])
        self.assertIn("Audrain County and Foreclosure/Sheriff Sales categories", foreclosure["note"])
        self.assertIn("prohibit scraping and automation", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.audraincounty.org/county-clerk/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.courts.mo.gov/cnet/cases/newHeader.do",
        )
        self.assertIn("concerns election administration", pre_foreclosure["note"])
        self.assertIn("returned HTTP 403", pre_foreclosure["note"])
        self.assertIn("No Audrain-specific bulk pre-foreclosure feed", pre_foreclosure["note"])

    def test_atchison_sources_distinguish_directory_notices_and_restrictions(self):
        sources = county_source_links("MO", "Atchison County", "29005")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.mocounties.com/atchison-county",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("lists the County Assessor's mailing address", assessor["note"])
        self.assertIn("no property search portal or data export", assessor["note"])
        self.assertIn("displayed a 2013 date", assessor["note"])
        self.assertIn("returned HTTP 404", assessor["note"])
        self.assertIn("Development Corporation, not a County Assessor site", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertEqual(tax_sale["source_url"], tax_sale["directory_url"])
        self.assertIn("Atchison County and a Tax Sale category", tax_sale["note"])
        self.assertIn("No current Atchison-specific parcel list", tax_sale["note"])
        self.assertIn("prohibit scraping and automation", tax_sale["note"])
        self.assertIn("use manual research only", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://www.mocounties.com/atchison-county",
        )
        self.assertEqual(code["source_url"], code["directory_url"])
        self.assertIn("not a code-enforcement service", code["note"])
        self.assertIn("No countywide property-level violation portal", code["note"])
        self.assertIn("Municipal code-enforcement providers remain unverified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.mopublicnotices.com/",
        )
        self.assertEqual(foreclosure["source_url"], foreclosure["directory_url"])
        self.assertIn("Atchison County and Foreclosure/Sheriff Sales categories", foreclosure["note"])
        self.assertIn("no current Atchison-specific foreclosure", foreclosure["note"])
        self.assertIn("prohibit scraping and automation", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.mocounties.com/atchison-county",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.courts.mo.gov/cnet/cases/newHeader.do",
        )
        self.assertIn("returned HTTP 403", pre_foreclosure["note"])
        self.assertIn("not a default or lis-pendens index", pre_foreclosure["note"])
        self.assertIn("No Atchison-specific bulk pre-foreclosure feed", pre_foreclosure["note"])

    def test_andrew_sources_verify_tax_sale_calendar_and_stale_parcel_list(self):
        sources = county_source_links("MO", "Andrew County", "29003")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://andrewcounty.org/offices/assessor/",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("describes assessment responsibilities and map sales", assessor["note"])
        self.assertIn("exposes no parcel-search portal or export", assessor["note"])
        self.assertIn("not a verified Assessor parcel feed", assessor["note"])
        self.assertIn("No machine-readable assessment feed/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://andrewcounty.org/offices/collector/tax-auction/",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://andrewcounty.org/wp-content/uploads/Tax-Sale-7-15-2025.pdf",
        )
        self.assertIn("annual, on the fourth Monday in August", tax_sale["note"])
        self.assertIn("three consecutive weeks", tax_sale["note"])
        self.assertIn("dated 2025-07-15, not a current 2026 list", tax_sale["note"])
        self.assertIn("No daily feed/API", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["directory_url"], "https://andrewcounty.org/offices/")
        self.assertEqual(code["source_url"], "https://andrewcounty.org/")
        self.assertIn("did not expose a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide code feed", code["note"])
        self.assertIn("municipal providers remain unverified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://andrewcounty.org/offices/sheriff/",
        )
        self.assertEqual(foreclosure["source_url"], foreclosure["directory_url"])
        self.assertIn("separate Sheriff website", foreclosure["note"])
        self.assertIn("failed to load in this check", foreclosure["note"])
        self.assertIn("No County foreclosure/sheriff sale calendar", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.mocounties.com/andrew-county",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.courts.mo.gov/cnet/cases/newHeader.do",
        )
        self.assertIn("returned HTTP 403", pre_foreclosure["note"])
        self.assertIn("No Andrew County-specific bulk default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not a pre-foreclosure data service", pre_foreclosure["note"])

    def test_adair_sources_verify_assessor_search_and_restrict_scraping(self):
        sources = county_source_links("MO", "Adair County", "29001")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://adaircountymissouri.com/departments/assessor/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://adair.missouriassessors.com/search.php",
        )
        self.assertIn("official County Assessor page links", assessor["note"])
        self.assertIn("Vanguard Appraisals", assessor["note"])
        self.assertIn("prohibit data mining, robots, screen scraping", assessor["note"])
        self.assertIn("commercial use without express written consent", assessor["note"])
        self.assertIn("do not automate collection absent written permission", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://adaircountymissouri.com/departments/collector/",
        )
        self.assertEqual(tax_sale["source_url"], tax_sale["directory_url"])
        self.assertIn("collects current and delinquent real-estate", tax_sale["note"])
        self.assertIn("does not expose a tax-sale calendar", tax_sale["note"])
        self.assertIn("No county-specific automated tax-sale source", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["directory_url"],
            "https://adaircountymissouri.com/departments/commission/",
        )
        self.assertEqual(
            code["source_url"],
            "https://adaircountymissouri.com/wp-content/uploads/"
            "2026/09/Resolution-2026-1.pdf",
        )
        self.assertIn("currently has no zoning regulations for large-scale facilities", code["note"])
        self.assertIn("This does not establish that all code enforcement is absent", code["note"])
        self.assertIn("No property-level countywide code-violation feed", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://adaircountymissouri.com/departments/sheriff/",
        )
        self.assertEqual(foreclosure["source_url"], foreclosure["directory_url"])
        self.assertIn("directs users to the office's Facebook page", foreclosure["note"])
        self.assertIn("no foreclosure or sheriff-sale calendar", foreclosure["note"])
        self.assertIn("No county-authorized automated foreclosure source", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.mocounties.com/adair-county",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://www.courts.mo.gov/cnet/cases/newHeader.do",
        )
        self.assertIn("returned HTTP 403", pre_foreclosure["note"])
        self.assertIn("No Adair County-specific bulk default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not a pre-foreclosure data service", pre_foreclosure["note"])

    def test_washington_sources_note_unavailable_county_and_assessor_sites(self):
        sources = county_source_links("AR", "Washington County", "05143")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/washington/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.washingtoncountyar.gov/",
        )
        self.assertIn("official website, but that site returned HTTP 403", assessor["note"])
        self.assertIn("ARCountyData URL redirected to the generic welcome page", assessor["note"])
        self.assertIn("No verified Assessor property-search portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a Washington County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.washingtoncountyar.gov/",
        )
        self.assertIn("returned HTTP 403", code["note"])
        self.assertIn("No countywide property-level violation feed was established", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("personal, non-commercial purposes", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Washington County-specific default/lis-pendens feed", pre_foreclosure["note"])

    def test_white_sources_verify_search_but_not_feed_authorization(self):
        sources = county_source_links("AR", "White County", "05145")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/white/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=White&s=R",
        )
        self.assertIn("Assessor sponsors a free public real-estate search", assessor["note"])
        self.assertIn("interactive third-party portal", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("official County website returned HTTP 403", assessor["note"])
        self.assertIn("express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a White County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://www.whitecountyar.org/")
        self.assertIn("returned HTTP 403", code["note"])
        self.assertIn("No countywide violation feed was established", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("returned HTTP 403", foreclosure["note"])
        self.assertIn("personal, non-commercial purposes", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no White County-specific default/lis-pendens feed", pre_foreclosure["note"])

    def test_woodruff_sources_distinguish_clerk_search_from_assessor_data(self):
        sources = county_source_links("AR", "Woodruff County", "05147")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/woodruff/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Woodruff&s=R",
        )
        self.assertIn("free County Clerk marriage-record search", assessor["note"])
        self.assertIn("not Assessor parcel data", assessor["note"])
        self.assertIn("returned only a County address", assessor["note"])
        self.assertIn("No verified Assessor property-search portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a Woodruff County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://portal.arkansas.gov/counties/woodruff/",
        )
        self.assertIn("only the County address", code["note"])
        self.assertIn("not County services", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("No County Sheriff sale calendar", foreclosure["note"])
        self.assertIn("personal, non-commercial purposes", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Woodruff County-specific default/lis-pendens feed", pre_foreclosure["note"])

    def test_yell_sources_note_no_county_specific_assessor_records(self):
        sources = county_source_links("AR", "Yell County", "05149")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/yell/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Yell&s=R",
        )
        self.assertIn("general property-tax estimate and Assessor duties", assessor["note"])
        self.assertIn("no county-specific Assessor search or parcel records", assessor["note"])
        self.assertIn("No verified Assessor property-search portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a Yell County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/yell/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("No County Sheriff sale calendar", foreclosure["note"])
        self.assertIn("personal, non-commercial purposes", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Yell County-specific default/lis-pendens feed", pre_foreclosure["note"])

    def test_stone_sources_identify_assessor_search_and_feed_limits(self):
        sources = county_source_links("AR", "Stone County", "05137")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/stone/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Stone&s=R",
        )
        self.assertIn("Assessor sponsors a free public real-estate search", assessor["note"])
        self.assertIn("interactive third-party portal", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a Stone County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/stone/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("No County Sheriff sale calendar", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Stone County-specific default/lis-pendens feed", pre_foreclosure["note"])

    def test_union_sources_note_stale_collector_data_and_no_assessor_records(self):
        sources = county_source_links("AR", "Union County", "05139")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/union/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Union&s=R",
        )
        self.assertIn("no Assessor search or parcel records", assessor["note"])
        self.assertIn("Collector data last updated 2019-03-07", assessor["note"])
        self.assertIn("County history, not an Assessor property search", assessor["note"])
        self.assertIn("No verified Assessor property-search portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a Union County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://www.unioncountyar.com/")
        self.assertIn("historical County information", code["note"])
        self.assertIn("not property-level code-enforcement services or records", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists the County Sheriff", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Union County-specific default/lis-pendens feed", pre_foreclosure["note"])

    def test_van_buren_sources_identify_assessor_search_and_feed_limits(self):
        sources = county_source_links("AR", "Van Buren County", "05141")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/van-buren/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Van%20Buren&s=R",
        )
        self.assertIn("Assessor sponsors a free public real-estate search", assessor["note"])
        self.assertIn("interactive third-party portal", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("did not expose a Van Buren County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.vanburencountyar.gov/",
        )
        self.assertIn("general community information", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists the County Sheriff", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Van Buren County-specific default/lis-pendens feed", pre_foreclosure["note"])

    def test_sevier_sources_note_stale_collector_data_and_no_assessor_records(self):
        sources = county_source_links("AR", "Sevier County", "05133")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/sevier/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Sevier&s=R",
        )
        self.assertIn("no Assessor search or parcel records", assessor["note"])
        self.assertIn("Collector data last updated 2023-12-14", assessor["note"])
        self.assertIn("courthouse-closure page with 2024 dates", assessor["note"])
        self.assertIn("No verified Assessor property-search portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn(
            "did not expose a Sevier County-specific current sale date/list",
            tax_sale["note"],
        )

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://www.seviercountyar.org/")
        self.assertIn("courthouse-closure page with 2024 dates", code["note"])
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Sevier County-specific default/lis-pendens feed", pre_foreclosure["note"])

    def test_sharp_sources_note_no_county_specific_assessor_records(self):
        sources = county_source_links("AR", "Sharp County", "05135")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/sharp/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Sharp&s=R",
        )
        self.assertIn("general property-tax estimate and Assessor duties", assessor["note"])
        self.assertIn("no county-specific Assessor search or parcel records", assessor["note"])
        self.assertIn("No verified Assessor property-search portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn(
            "did not expose a Sharp County-specific current sale date/list",
            tax_sale["note"],
        )

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/sharp/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("No County Sheriff sale calendar", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Sharp County-specific default/lis-pendens feed", pre_foreclosure["note"])

    def test_st_francis_sources_identify_assessor_search_and_limits(self):
        sources = county_source_links("AR", "St. Francis County", "05123")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://stfranciscountyar.gov/departments/assessor/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=St.%20Francis&s=R",
        )
        self.assertIn("County Assessor department page identifies the Assessor", assessor["note"])
        self.assertIn("Assessor sponsors a free public real-estate search", assessor["note"])
        self.assertIn("interactive third-party portal", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn(
            "did not expose a St. Francis County-specific current sale date/list",
            tax_sale["note"],
        )

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://stfranciscountyar.gov/")
        self.assertIn("County Judge welcome content", code["note"])
        self.assertIn("not a property-level county code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("did not expose a Sheriff sale calendar", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no St. Francis County-specific default/lis-pendens feed", pre_foreclosure["note"])

    def test_sebastian_sources_verify_assessor_and_commissioner_sale_calendar(self):
        sources = county_source_links("AR", "Sebastian County", "05131")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/sebastian/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Sebastian&s=R",
        )
        self.assertIn("Assessor sponsors a free public real-estate search", assessor["note"])
        self.assertIn("interactive third-party portal", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn(
            "did not expose a Sebastian County-specific current State Land Office sale list",
            tax_sale["note"],
        )

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.sebastiancountyar.gov/",
        )
        self.assertIn("no property-level countywide code-enforcement service/feed", code["note"])
        self.assertIn("Municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.sebastiancountyar.gov/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.sebastiancountyar.gov/Home/County-Calendar",
        )
        self.assertIn("Commissioner's Sale events", foreclosure["note"])
        self.assertIn("court case numbers", foreclosure["note"])
        self.assertIn("does not establish that each event is a mortgage foreclosure or tax sale", foreclosure["note"])
        self.assertIn("No bulk API/export", foreclosure["note"])
        self.assertIn("personal, non-commercial purposes", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Sebastian County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("Commissioner's Sale events are not pre-foreclosure records", pre_foreclosure["note"])

    def test_searcy_sources_verify_assessor_search_and_limited_online_services(self):
        sources = county_source_links("AR", "Searcy County", "05129")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/searcy/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Searcy&s=R",
        )
        self.assertIn("Assessor sponsors a free public real-estate search", assessor["note"])
        self.assertIn("interactive third-party portal", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("only people who assessed in Searcy County the prior year", assessor["note"])
        self.assertIn("not a parcel-valuation search", assessor["note"])
        self.assertIn("express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["source_url"],
            "https://cosl.org/Home/Contents",
        )
        self.assertIn("online payments are not accepted", tax_sale["note"])
        self.assertIn("no Searcy-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://searcyco.org/")
        self.assertIn("general welcome and governance content", code["note"])
        self.assertIn("not property-level code-enforcement services or records", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists the County Sheriff", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Searcy County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_scott_sources_verify_assessor_portal_and_tax_sale_process(self):
        sources = county_source_links("AR", "Scott County", "05127")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://scottcountyar.com/assessor/assessor.cshtml",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://countyservice.net/assess?name=Scott",
        )
        self.assertIn("official County Assessor page", assessor["note"])
        self.assertIn("prior year", assessor["note"])
        self.assertIn("not a parcel-valuation search", assessor["note"])
        self.assertIn("No property search feed/API", assessor["note"])
        self.assertIn("express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["directory_url"],
            "https://scottcountyar.com/collector/tax_collector.cshtml",
        )
        self.assertEqual(
            tax_sale["source_url"],
            "https://cosl.org/Home/Contents",
        )
        self.assertIn("published in the local newspaper", tax_sale["note"])
        self.assertIn("late November or early December", tax_sale["note"])
        self.assertIn("forwarded to the State Land Office", tax_sale["note"])
        self.assertIn("no Scott-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://scottcountyar.com/welcome")
        self.assertIn("no property-level code-enforcement service", code["note"])
        self.assertIn("No countywide code feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/scott/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists the County Sheriff", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Scott County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_saline_sources_note_assessor_portal_and_broken_county_site(self):
        sources = county_source_links("AR", "Saline County", "05125")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/saline/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Saline&s=R",
        )
        self.assertIn("Assessor sponsors a free public real-estate search", assessor["note"])
        self.assertIn("interactive third-party portal", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Saline County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.salinecounty.org/",
        )
        self.assertIn("template instruction to copy and paste a link", code["note"])
        self.assertIn("not County services or records", code["note"])
        self.assertIn("No property-level county code-enforcement service/feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/saline/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists the County Sheriff", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Saline County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_randolph_sources_note_assessor_portal_unavailability(self):
        sources = county_source_links("AR", "Randolph County", "05121")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/randolph/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcounties.org/counties/randolph/",
        )
        self.assertIn("lists the County Assessor and office contact", assessor["note"])
        self.assertIn("redirected to the site's generic welcome page", assessor["note"])
        self.assertIn("not Randolph County parcel records", assessor["note"])
        self.assertIn("No verified Assessor property-search portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Randolph County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://portal.arkansas.gov/counties/randolph/",
        )
        self.assertIn("only a county address", code["note"])
        self.assertIn(
            "Neither page exposes a property-level code-enforcement service",
            code["note"],
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists the County Sheriff", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Randolph County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_pulaski_sources_identify_assessor_portal_and_feed_limits(self):
        sources = county_source_links("AR", "Pulaski County", "05119")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/pulaski/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Pulaski&s=R",
        )
        self.assertIn("lists the County Assessor and office contact", assessor["note"])
        self.assertIn("Assessor sponsors a free public real-estate search", assessor["note"])
        self.assertIn("interactive third-party portal", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Pulaski County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.pulaskicounty.net/departments",
        )
        self.assertIn("official County departments page", code["note"])
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(foreclosure["directory_url"], "https://pcso.org/")
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("official agency page", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Pulaski County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_prairie_sources_distinguish_collector_search_from_assessor_data(self):
        sources = county_source_links("AR", "Prairie County", "05117")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/prairie/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Prairie&s=R",
        )
        self.assertIn("lists the County Assessor and office contact", assessor["note"])
        self.assertIn("not a parcel-data service", assessor["note"])
        self.assertIn("free Collector tax-record/receipt search", assessor["note"])
        self.assertIn("not an Assessor valuation search", assessor["note"])
        self.assertIn("No verified Assessor property portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Prairie County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/prairie/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/prairie/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists the County Sheriff", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Prairie County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_pope_sources_identify_assessor_search_and_limits(self):
        sources = county_source_links("AR", "Pope County", "05115")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/pope/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Pope&s=R",
        )
        self.assertIn("Assessor sponsors a free public real-estate search", assessor["note"])
        self.assertIn("interactive third-party portal", assessor["note"])
        self.assertIn("no machine-readable feed/API", assessor["note"])
        self.assertIn("express written consent", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Pope County-specific current sale date/list", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.popecountyar.gov/",
        )
        self.assertIn("agenda-deadline and budget/quorum-court content", code["note"])
        self.assertIn("No property-level county code enforcement service/feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("did not establish a Sheriff sale calendar", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Pope County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_polk_sources_distinguish_collector_search_from_assessor_data(self):
        sources = county_source_links("AR", "Polk County", "05113")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/polk/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Polk&s=R",
        )
        self.assertIn("provides County background and an address", assessor["note"])
        self.assertIn("no Assessor contact or parcel records", assessor["note"])
        self.assertIn("explicitly a free Collector tax-record/receipt search", assessor["note"])
        self.assertIn("not an Assessor valuation search", assessor["note"])
        self.assertIn("No verified Assessor property portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Polk County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/polk/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Polk County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_poinsett_sources_identify_assessor_search_and_broken_county_site(self):
        sources = county_source_links("AR", "Poinsett County", "05111")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/poinsett/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Poinsett&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Poinsett County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://www.poinsettar.gov/")
        self.assertIn("returned only a template instruction to copy/paste a link", code["note"])
        self.assertIn("not usable County services or records", code["note"])
        self.assertIn("No property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Poinsett County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_pike_sources_identify_assessor_search_and_county_site_limits(self):
        sources = county_source_links("AR", "Pike County", "05109")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/pike/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Pike&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Pike County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://pikecountyar.org/")
        self.assertIn("returned general county history", code["note"])
        self.assertIn("quick links provide official contacts", code["note"])
        self.assertIn("no property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Pike County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_phillips_sources_distinguish_collector_from_assessor_data(self):
        sources = county_source_links("AR", "Phillips County", "05107")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/phillips/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Phillips&s=R",
        )
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("explicitly a free Collector tax-record/receipt search", assessor["note"])
        self.assertIn("not an Assessor valuation search", assessor["note"])
        self.assertIn("No verified Assessor property portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Phillips County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/phillips/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Phillips County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_perry_sources_distinguish_collector_search_and_county_site_scope(self):
        sources = county_source_links("AR", "Perry County", "05105")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/perry/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Perry&s=R",
        )
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("explicitly a free Collector tax-record/receipt search", assessor["note"])
        self.assertIn("not an Assessor valuation search", assessor["note"])
        self.assertIn("No verified Assessor property portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Perry County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://perrycoarkansas.org/")
        self.assertIn("returned a County Judge message", code["note"])
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Perry County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_ouachita_sources_distinguish_collector_from_assessor_data(self):
        sources = county_source_links("AR", "Ouachita County", "05103")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/ouachita/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Ouachita&s=R",
        )
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("explicitly a free Collector tax-record/receipt search", assessor["note"])
        self.assertIn("not an Assessor valuation search", assessor["note"])
        self.assertIn("No verified Assessor property portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose an Ouachita County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/ouachita/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Ouachita County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_newton_sources_distinguish_assessor_background_from_search(self):
        sources = county_source_links("AR", "Newton County", "05101")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/newton/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Newton&s=R",
        )
        self.assertIn("no Assessor-sponsored search or parcel results", assessor["note"])
        self.assertIn("provides County background and an address", assessor["note"])
        self.assertIn("not property records", assessor["note"])
        self.assertIn("No verified property-search portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Newton County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/newton/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Newton County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_nevada_sources_distinguish_collector_from_assessor_records(self):
        sources = county_source_links("AR", "Nevada County", "05099")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/nevada/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Nevada&s=R",
        )
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("explicitly a free Collector tax-record/receipt search", assessor["note"])
        self.assertIn("not an Assessor valuation search", assessor["note"])
        self.assertIn("No verified Assessor property portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Nevada County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/nevada/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Nevada County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_montgomery_sources_distinguish_collector_from_assessor_data(self):
        sources = county_source_links("AR", "Montgomery County", "05097")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/montgomery/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Montgomery&s=R",
        )
        self.assertIn("provides County background and an address", assessor["note"])
        self.assertIn("no Assessor contact or parcel records", assessor["note"])
        self.assertIn("explicitly a free Collector tax-record/receipt search", assessor["note"])
        self.assertIn("not an Assessor valuation search", assessor["note"])
        self.assertIn("No verified Assessor property portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Montgomery County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/montgomery/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Montgomery County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_monroe_sources_identify_assessor_search_and_remaining_feed_gaps(self):
        sources = county_source_links("AR", "Monroe County", "05095")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/monroe/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Monroe&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Monroe County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/monroe/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Monroe County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_mississippi_sources_identify_assessor_search_and_feed_gaps(self):
        sources = county_source_links("AR", "Mississippi County", "05093")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/mississippi/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Mississippi&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Mississippi County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/mississippi/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Mississippi County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_miller_sources_distinguish_collector_from_assessor_records(self):
        sources = county_source_links("AR", "Miller County", "05091")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/miller/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Miller&s=R",
        )
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("explicitly a free Collector tax-record/receipt search", assessor["note"])
        self.assertIn("not an Assessor valuation search", assessor["note"])
        self.assertIn("No verified Assessor property portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Miller County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/miller/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Miller County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_marion_sources_identify_assessor_search_and_county_site_restriction(self):
        sources = county_source_links("AR", "Marion County", "05089")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/marion/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Marion&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Marion County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/marion/",
        )
        self.assertIn("County website returned HTTP 403", code["note"])
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Marion County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_madison_sources_record_missing_search_and_alert_placeholder(self):
        sources = county_source_links("AR", "Madison County", "05087")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/madison/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Madison&s=R",
        )
        self.assertIn("redirected to its generic welcome page", assessor["note"])
        self.assertIn("no Madison-specific property search was exposed", assessor["note"])
        self.assertIn("No verified Assessor portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Madison County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://madisoncountyar.gov/",
        )
        self.assertIn("redirects to this County website", code["note"])
        self.assertIn("returned only an alert placeholder", code["note"])
        self.assertIn("No property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Madison County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_lonoke_sources_identify_assessor_search_and_other_feed_gaps(self):
        sources = county_source_links("AR", "Lonoke County", "05085")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/lonoke/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Lonoke&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Lonoke County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/lonoke/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Lonoke County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_logan_sources_identify_assessor_search_and_courthouse_only_site(self):
        sources = county_source_links("AR", "Logan County", "05083")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/logan/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Logan&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Logan County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://logancountyark.org/")
        self.assertIn("returned addresses for the Paris and Booneville courthouses only", code["note"])
        self.assertIn("no property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Logan County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_little_river_sources_distinguish_collector_from_assessor_records(self):
        sources = county_source_links("AR", "Little River County", "05081")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/little-river/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Little%20River&s=R",
        )
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("explicitly a free Collector tax-record/receipt search", assessor["note"])
        self.assertIn("not an Assessor valuation search", assessor["note"])
        self.assertIn("No verified Assessor property portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Little River County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/little-river/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Little River County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_lincoln_sources_record_missing_assessor_search_and_feed_gaps(self):
        sources = county_source_links("AR", "Lincoln County", "05079")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/lincoln/",
        )
        self.assertEqual(assessor["source_url"], "https://www.arcountydata.com/county.asp?county=Lincoln&s=R")
        self.assertIn("provides County background and an address", assessor["note"])
        self.assertIn("no Assessor contact or parcel records", assessor["note"])
        self.assertIn("redirected to its generic welcome page", assessor["note"])
        self.assertIn("no Lincoln-specific property search was exposed", assessor["note"])
        self.assertIn("No verified Assessor portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Lincoln County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/lincoln/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Lincoln County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_lee_sources_identify_assessor_search_and_other_feed_gaps(self):
        sources = county_source_links("AR", "Lee County", "05077")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/lee/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Lee&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Lee County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/lee/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Lee County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_lawrence_sources_identify_assessor_search_and_county_site_maintenance(self):
        sources = county_source_links("AR", "Lawrence County", "05075")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/lawrence/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Lawrence&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Lawrence County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.lawrencecountyarkansas.com/",
        )
        self.assertIn("returned a message that it is undergoing changes", code["note"])
        self.assertIn("no property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Lawrence County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_lafayette_sources_identify_assessor_search_and_state_portal_redirect(self):
        sources = county_source_links("AR", "Lafayette County", "05073")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/lafayette/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Lafayette&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Lafayette County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://portal.arkansas.gov/counties/lafayette/",
        )
        self.assertIn("redirects to this State Portal page", code["note"])
        self.assertIn("returned only the courthouse location", code["note"])
        self.assertIn("No property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists the Sheriff and contact details", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Lafayette County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_johnson_sources_identify_assessor_search_and_statewide_sources(self):
        sources = county_source_links("AR", "Johnson County", "05071")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/johnson/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Johnson&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Johnson County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/johnson/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Johnson County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_jefferson_sources_distinguish_clerk_records_from_assessor_data(self):
        sources = county_source_links("AR", "Jefferson County", "05069")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/jefferson/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Jefferson&s=R",
        )
        self.assertIn("free County Clerk marriage-record search", assessor["note"])
        self.assertIn("not Assessor valuation data", assessor["note"])
        self.assertIn("lists the Assessor office contact", assessor["note"])
        self.assertIn("No verified property assessment search", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Jefferson County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/jefferson/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Jefferson County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_jackson_sources_distinguish_clerk_search_from_assessor_data(self):
        sources = county_source_links("AR", "Jackson County", "05067")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/jackson/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Jackson&s=R",
        )
        self.assertIn("free County Clerk marriage-record search", assessor["note"])
        self.assertIn("not Assessor valuation data", assessor["note"])
        self.assertIn("no property assessment search", assessor["note"])
        self.assertIn("No verified Assessor portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Jackson County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://jacksoncountyar.com/")
        self.assertIn("general history and community information", code["note"])
        self.assertIn("no property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Jackson County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_izard_sources_record_stale_paid_assessor_data_and_other_feed_gaps(self):
        sources = county_source_links("AR", "Izard County", "05065")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/izard/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Izard&s=R",
        )
        self.assertIn("empty property-search area with a paid-user login", assessor["note"])
        self.assertIn("32,120 parcels", assessor["note"])
        self.assertIn("Assessor data last updated 10/20/2022", assessor["note"])
        self.assertIn("Collector data last updated 1/27/2022", assessor["note"])
        self.assertIn("displayed data dates are stale", assessor["note"])
        self.assertIn("could not be retrieved", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose an Izard County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://izardcountyar.org/")
        self.assertIn("could not be retrieved in this check", code["note"])
        self.assertIn("No property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Izard County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_independence_sources_record_assessor_contact_and_missing_search(self):
        sources = county_source_links("AR", "Independence County", "05063")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/independence/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Independence&s=R",
        )
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("redirected to its generic welcome page", assessor["note"])
        self.assertIn("no Independence-specific property search was exposed", assessor["note"])
        self.assertIn("No verified Assessor portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose an Independence County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/independence/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Independence County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_howard_sources_identify_assessor_search_and_limitations(self):
        sources = county_source_links("AR", "Howard County", "05061")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/howard/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Howard&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Howard County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/howard/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Howard County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_hot_spring_sources_distinguish_clerk_records_from_assessor_data(self):
        sources = county_source_links("AR", "Hot Spring County", "05059")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/hot-spring/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Hot%20Spring&s=R",
        )
        self.assertIn("free County Clerk marriage-record search", assessor["note"])
        self.assertIn("not Assessor valuation data", assessor["note"])
        self.assertIn("no property assessment search", assessor["note"])
        self.assertIn("No verified Assessor portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Hot Spring County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://hotspringcounty.org/")
        self.assertIn("returned county-history information only", code["note"])
        self.assertIn("no property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Hot Spring County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_hempstead_sources_distinguish_collector_data_and_misdirected_link(self):
        sources = county_source_links("AR", "Hempstead County", "05057")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/hempstead/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Hempstead&s=R",
        )
        self.assertIn("free search as Collector tax records and receipts", assessor["note"])
        self.assertIn("not Assessor valuation data", assessor["note"])
        self.assertIn("links to garlandcounty.org", assessor["note"])
        self.assertIn("rather than a Hempstead County site", assessor["note"])
        self.assertIn("No verified Hempstead Assessor portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Hempstead County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/hempstead/",
        )
        self.assertIn("resolves to Garland County rather than Hempstead County", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Hempstead Sheriff sale calendar", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Hempstead County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_greene_sources_distinguish_assessor_background_from_search(self):
        sources = county_source_links("AR", "Greene County", "05055")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/greene/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Greene&s=R",
        )
        self.assertIn("no Assessor-sponsored search or parcel results", assessor["note"])
        self.assertIn("due-date and partial-payment guidance", assessor["note"])
        self.assertIn("not parcel assessment records", assessor["note"])
        self.assertIn("No verified property-search portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Greene County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://greenecounty.arkansas.gov/",
        )
        self.assertIn("general county and tax-payment information", code["note"])
        self.assertIn("no property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Greene County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_grant_sources_identify_assessor_search_and_county_site_limit(self):
        sources = county_source_links("AR", "Grant County", "05053")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/grant/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Grant&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Grant County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://grantcountyar.com/")
        self.assertIn("returned a county-history introduction", code["note"])
        self.assertIn("no property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Grant County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_garland_sources_record_assessor_contact_and_missing_search(self):
        sources = county_source_links("AR", "Garland County", "05051")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/garland/",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("redirected to its generic welcome page", assessor["note"])
        self.assertIn("no Garland-specific property search was exposed", assessor["note"])
        self.assertIn("No verified Assessor portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Garland County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/garland/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Garland County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_fulton_sources_identify_assessor_search_and_unavailable_county_site(self):
        sources = county_source_links("AR", "Fulton County", "05049")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/fulton/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Fulton&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Fulton County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(code["source_url"], "https://www.fultoncountyar.gov/")
        self.assertIn("could not be retrieved in this check", code["note"])
        self.assertIn("No property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Fulton County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_franklin_sources_record_assessor_directory_and_missing_search(self):
        sources = county_source_links("AR", "Franklin County", "05047")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/franklin/",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("redirected to its generic welcome page", assessor["note"])
        self.assertIn("no Franklin-specific property search was exposed", assessor["note"])
        self.assertIn("No verified Assessor portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Franklin County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/franklin/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists Sheriff contacts", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Franklin County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_faulkner_sources_identify_assessor_search_and_official_site_limit(self):
        sources = county_source_links("AR", "Faulkner County", "05045")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/faulkner/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Faulkner&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Faulkner County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.faulknercountyar.gov/",
        )
        self.assertIn("returned only a courthouse-closure announcement", code["note"])
        self.assertIn("no property-level code-enforcement service or feed", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("lists the Sheriff and contact details", foreclosure["note"])
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Faulkner County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_drew_sources_record_no_county_specific_portals_or_feeds(self):
        sources = county_source_links("AR", "Drew County", "05043")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/drew/",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("provides county background and an address", assessor["note"])
        self.assertIn("no Assessor contact or parcel records", assessor["note"])
        self.assertIn("redirected to its generic welcome page", assessor["note"])
        self.assertIn("no Drew-specific property search was exposed", assessor["note"])
        self.assertIn("No verified Assessor portal", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Drew County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/drew/",
        )
        self.assertIn("not a property-level code-enforcement service", code["note"])
        self.assertIn("No countywide violation feed was identified", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no County Sheriff sale calendar", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Drew County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_cross_sources_record_county_assessor_and_feed_gaps(self):
        sources = county_source_links("AR", "Cross County", "05037")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/cross/",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("redirected to its generic welcome page", assessor["note"])
        self.assertIn("no Cross-specific property search was exposed", assessor["note"])
        self.assertIn("listed county website could not be retrieved", assessor["note"])
        self.assertIn("No verified Assessor feed/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Cross County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/cross/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("linked County website could not be retrieved", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Cross County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_crawford_sources_distinguish_collector_records_from_assessor_data(self):
        sources = county_source_links("AR", "Crawford County", "05033")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/crawford/",
        )
        self.assertEqual(assessor["source_url"], assessor["directory_url"])
        self.assertIn("lists the County Assessor contact", assessor["note"])
        self.assertIn("explicitly a Collector tax-record/receipt search", assessor["note"])
        self.assertIn("not an Assessor valuation search", assessor["note"])
        self.assertIn("No verified Assessor property portal", assessor["note"])
        self.assertIn("permission for daily commercial extraction was identified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Crawford County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/crawford/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Crawford County Sheriff sale calendar", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Crawford County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_dallas_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Dallas County", "05039")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/dallas/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Dallas&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Dallas County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/dallas/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no Sheriff sale calendar or foreclosure feed", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("no Dallas County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_desha_sources_identify_assessor_search_and_statewide_sale_source(self):
        sources = county_source_links("AR", "Desha County", "05041")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.arcounties.org/counties/desha/",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://www.arcountydata.com/county.asp?county=Desha&s=R",
        )
        self.assertIn("Assessor sponsors a free public property-record search", assessor["note"])
        self.assertIn("not a documented daily feed", assessor["note"])
        self.assertIn("express written consent", assessor["note"])
        self.assertIn("permission for commercial daily extraction was verified", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(tax_sale["directory_url"], "https://cosl.org/Home/RealEstate")
        self.assertEqual(tax_sale["source_url"], "https://cosl.org/Home/Contents")
        self.assertIn("statewide auction catalog", tax_sale["note"])
        self.assertIn("did not expose a Desha County-specific current sale date/list", tax_sale["note"])
        self.assertIn("permission for daily/commercial automation were not verified", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertEqual(
            code["source_url"],
            "https://www.arcounties.org/counties/desha/",
        )
        self.assertIn("No countywide violation feed was identified", code["note"])
        self.assertIn("municipal providers", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.arcounties.org/counties/desha/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.arkansaspublicnotices.com/",
        )
        self.assertIn("no sale calendar or County-authorized foreclosure feed", foreclosure["note"])
        self.assertIn("not the official publication", foreclosure["note"])
        self.assertIn("Written permission", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://caseinfo.arcourts.gov/opad",
        )
        self.assertIn("general navigation tips", pre_foreclosure["note"])
        self.assertIn("no Desha County-specific default/lis-pendens feed", pre_foreclosure["note"])
        self.assertIn("not pre-foreclosure records", pre_foreclosure["note"])

    def test_winston_sources_record_gis_shell_and_records_limits(self):
        sources = county_source_links("AL", "Winston County", "01133")

        assessor = sources["assessor"]
        self.assertEqual(
            assessor["directory_url"],
            "https://www.revenue.alabama.gov/property-tax/"
            "county-offices-appraisal-assessment-records/#Winston",
        )
        self.assertEqual(
            assessor["source_url"],
            "https://isv.kcsgis.com/al.winston_revenue/",
        )
        self.assertIn("Winston County ISV3", assessor["note"])
        self.assertIn("no parcel results, bulk export/API", assessor["note"])

        tax_sale = sources["tax_sale"]
        self.assertEqual(
            tax_sale["source_url"],
            "https://www.revenue.alabama.gov/wp-content/uploads/"
            "property-tax-transcripts/WWW_TRANS_67.PDF",
        )
        self.assertIn("no County sale date", tax_sale["note"])
        self.assertIn("one-page weekly state-held", tax_sale["note"])
        self.assertIn("not the County auction calendar", tax_sale["note"])
        self.assertIn("No recurring local sale feed", tax_sale["note"])

        code = sources["code_enforcement"]
        self.assertIn("no countywide property-level code-enforcement provider", code["note"])
        self.assertIn("check the authority for each property's municipality", code["note"])

        foreclosure = sources["foreclosure"]
        self.assertEqual(
            foreclosure["directory_url"],
            "https://www.alabamasheriffs.com/sheriffsdirectory/",
        )
        self.assertEqual(
            foreclosure["source_url"],
            "https://www.alabamapublicnotices.com/",
        )
        self.assertIn("No Winston County Sheriff's sale calendar", foreclosure["note"])
        self.assertIn("Terms prohibit scraping", foreclosure["note"])
        self.assertIn("No authorized daily foreclosure source", foreclosure["note"])

        pre_foreclosure = sources["pre_foreclosure"]
        self.assertEqual(
            pre_foreclosure["directory_url"],
            "https://www.winstoncountyprobate.org/",
        )
        self.assertEqual(
            pre_foreclosure["source_url"],
            "https://ingprobate.com/Winston_Probate/",
        )
        self.assertIn("direct records route redirected", pre_foreclosure["note"])
        self.assertIn("identifies the Winston County Probate Judge", pre_foreclosure["note"])
        self.assertIn("prohibits automated systems", pre_foreclosure["note"])
        self.assertIn("No dedicated lis-pendens/default feed", pre_foreclosure["note"])


if __name__ == "__main__":
    unittest.main()
