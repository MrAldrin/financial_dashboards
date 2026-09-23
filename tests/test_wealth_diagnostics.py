"""Exact selected-point accounting and one-sided marginal slopes."""

import unittest

from apps.building_taxation import calculate_wealth_tax_df, selected_tax_diagnostics

BASE = dict(
    tiers=[{"limit": 14_000_000, "rate": 25}, {"limit": None, "rate": 70}],
    base_deduction=1_900_000,
    tax_rate=1,
    upper_tax_rate=1.1,
    scenario_name="reference",
)
HOUSEHOLD = dict(
    is_couple=False, ownership_share=1, mortgage_debt=1_600_000, other_net_wealth=0
)


class DiagnosticTests(unittest.TestCase):
    def test_onset_and_valuation_kink(self) -> None:
        frame = calculate_wealth_tax_df(
            **BASE, **HOUSEHOLD, selected_value=14_000_000, max_value=20_000_000
        )
        result = selected_tax_diagnostics(frame, 14_000_000, BASE, HOUSEHOLD)
        self.assertEqual(result["Skatteenhetens boligverdi (kr)"], 3_500_000)
        self.assertEqual(result["Netto skatteformue før fradrag (kr)"], 1_900_000)
        self.assertEqual(result["Grunnlag før nullgulv (kr)"], 0)
        self.assertEqual(result["Skatt (kr/år)"], 0)
        self.assertAlmostEqual(result["Venstre marginal (kr per +1 mill.)"], 0)
        self.assertAlmostEqual(result["Høyre marginal (kr per +1 mill.)"], 7_000)
        self.assertAlmostEqual(result["Ordinært bånd (kr/år)"], 0)
        reform = {
            **BASE,
            "tiers": [{"limit": 10_000_000, "rate": 25}, {"limit": None, "rate": 70}],
            "scenario_name": "reform",
        }
        other = selected_tax_diagnostics(
            calculate_wealth_tax_df(
                **reform, **HOUSEHOLD, selected_value=14_000_000, max_value=20_000_000
            ),
            14_000_000,
            reform,
            HOUSEHOLD,
        )
        self.assertAlmostEqual(other["Skatt (kr/år)"], 18_000)
        self.assertAlmostEqual(other["Venstre marginal (kr per +1 mill.)"], 7_000)
        self.assertAlmostEqual(other["Høyre marginal (kr per +1 mill.)"], 7_000)

    def test_joint_upper_band_and_fractional_share(self) -> None:
        household = {
            **HOUSEHOLD,
            "is_couple": True,
            "ownership_share": 0.5,
            "other_net_wealth": 43_000_000,
            "mortgage_debt": 0,
        }
        frame = calculate_wealth_tax_df(
            **BASE, **household, selected_value=0, max_value=20_000_000
        )
        result = selected_tax_diagnostics(frame, 0, BASE, household)
        self.assertEqual(result["Personfradrag (kr)"], 3_800_000)
        self.assertEqual(result["Øvre bånd (kr/år)"], 0)
        self.assertEqual(result["Ordinært bånd (kr/år)"], 392_000)
        self.assertIsNone(result["Venstre marginal (kr per +1 mill.)"])
        self.assertAlmostEqual(result["Høyre marginal (kr per +1 mill.)"], 1_375)
        # Beyond the upper net-wealth boundary, the band changes but remains continuous.
        upper = selected_tax_diagnostics(frame, 1_000_000, BASE, household)
        self.assertAlmostEqual(upper["Høyre marginal (kr per +1 mill.)"], 1_375)
        self.assertGreater(upper["Øvre bånd (kr/år)"], 0)
        self.assertIsNone(
            selected_tax_diagnostics(frame, 20_000_000, BASE, household)[
                "Høyre marginal (kr per +1 mill.)"
            ]
        )
        with self.assertRaises(ValueError):
            selected_tax_diagnostics(frame, 21_000_000, BASE, household)


if __name__ == "__main__":
    unittest.main()
