import unittest

from app.models import Property
from app.schemas import UnderwritingAssumptions
from app.underwriting import analyze_property


class UnderwritingTests(unittest.TestCase):
    def test_complete_section8_scenario_uses_conservative_published_benchmark(self):
        property_record = Property(
            id=7,
            asking_price=120_000,
            estimated_repairs=20_000,
            annual_property_tax=None,
            assessed_value=90_000,
            tax_rate_percent=1.2,
            annual_insurance_estimate=1_200,
            expected_market_rent_monthly=1_250,
            hud_fmr_monthly=1_400,
            pha_payment_standard_monthly=1_300,
            pha_program_status="confirmed",
            population_growth_percent=1.5,
            violent_crime_rate_per_100k=500,
        )

        result = analyze_property(property_record, UnderwritingAssumptions())

        section8 = result["section8"]
        scenario = section8["scenario"]
        self.assertEqual(section8["published_rent_benchmark_monthly"], 1_300)
        self.assertEqual(scenario["rent_monthly"], 1_300)
        self.assertEqual(scenario["annual_property_tax"], 1_080)
        self.assertEqual(scenario["monthly_operating_cash_flow_before_financing_and_hoa"], 837)
        self.assertEqual(scenario["capital_basis_for_cap_rate"], 140_000)
        self.assertAlmostEqual(scenario["cap_rate_percent_before_financing_and_hoa"], 7.1743, places=4)
        self.assertTrue(scenario["complete_for_displayed_costs"])
        self.assertEqual(result["score"]["coverage"], 1)

    def test_missing_insurance_never_becomes_a_complete_cash_flow_estimate(self):
        property_record = Property(
            id=8,
            asking_price=100_000,
            annual_property_tax=1_000,
            expected_market_rent_monthly=1_200,
            annual_insurance_estimate=None,
        )

        result = analyze_property(property_record, UnderwritingAssumptions())

        scenario = result["market_rent_scenario"]
        self.assertIsNone(scenario["monthly_operating_cash_flow_before_financing_and_hoa"])
        self.assertIn("insurance quote or user-entered estimate", scenario["missing_inputs"])
        self.assertIsNone(result["score"]["components"].get("yield"))

    def test_unconfirmed_program_does_not_claim_section8_rent_or_zero_open_vouchers(self):
        property_record = Property(
            id=9,
            hud_fmr_monthly=1_100,
            pha_program_status="unknown",
            voucher_waitlist_status="open",
            open_voucher_count=None,
        )

        result = analyze_property(property_record, UnderwritingAssumptions())

        self.assertEqual(result["section8"]["published_rent_benchmark_monthly"], 1_100)
        self.assertIsNone(result["section8"]["scenario"]["rent_monthly"])
        self.assertIsNone(result["section8"]["open_voucher_count"])
        self.assertIn("unknown", result["section8"]["voucher_count_note"])


if __name__ == "__main__":
    unittest.main()
