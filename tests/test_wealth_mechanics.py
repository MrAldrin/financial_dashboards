"""Run with uv run python -m unittest discover -s local_testing -p 'test_wealth*.py'."""

import unittest

from apps.building_taxation import calculate_wealth_tax_df, home_value_at_tax_wealth


BASE = [{"limit": 14_000_000, "rate": 25.0}, {"limit": None, "rate": 70.0}]


def example(value: float, **changes: object) -> dict:
    options = dict(
        tiers=BASE,
        base_deduction=1_900_000,
        tax_rate=1,
        scenario_name="test",
        is_couple=False,
        mortgage_debt=0,
        other_net_wealth=0,
        selected_value=value,
    )
    options.update(changes)
    return (
        calculate_wealth_tax_df(**options)
        .filter(__import__("polars").col("market_value") == value)
        .row(0, named=True)
    )


class WealthMechanicsTests(unittest.TestCase):
    def test_worked_threshold_comparison(self) -> None:
        old = [{"limit": 10_000_000, "rate": 25}, {"limit": None, "rate": 70}]
        self.assertEqual(example(12_000_000, tiers=old)["tax"], 20_000)
        self.assertEqual(example(12_000_000)["tax"], 11_000)

    def test_onset_and_continuity(self) -> None:
        for value, tax in [
            (14_000_000, 0),
            (14_100_000, 700),
            (15_000_000, 7000),
            (16_000_000, 14000),
        ]:
            self.assertAlmostEqual(example(value, mortgage_debt=1_600_000)["tax"], tax)
        self.assertAlmostEqual(
            example(14_000_001)["valuation"] - example(14_000_000)["valuation"], 0.7
        )
        self.assertEqual(home_value_at_tax_wealth(BASE, 1_900_000), 7_600_000)
        self.assertIsNone(home_value_at_tax_wealth([{"limit": None, "rate": 0}], 1))

    def test_upper_band_not_shifted_by_allowance(self) -> None:
        self.assertEqual(example(0, other_net_wealth=21_500_000)["tax"], 196_000)
        self.assertEqual(example(0, other_net_wealth=22_500_000)["tax"], 207_000)
        self.assertEqual(
            example(0, other_net_wealth=45_000_000, is_couple=True)["tax"], 414_000
        )

    def test_income_does_not_change_tax(self) -> None:
        zero = example(14_000_000)
        income = example(14_000_000, annual_income=800_000)
        self.assertEqual(zero["tax"], income["tax"])
        self.assertIsNone(zero["income_share"])
        self.assertEqual(income["income_share"], 2)

    def test_debt_and_validation(self) -> None:
        row = example(14_000_000, mortgage_debt=20_000_000)
        self.assertLess(row["tax_base"], 0)
        self.assertEqual(row["tax"], 0)
        with self.assertRaises(ValueError):
            example(0, tiers=[{"limit": None, "rate": -1}])

    def test_discount_monotonicity_and_exact_grid(self) -> None:
        cheaper = [{"limit": 14_000_000, "rate": 20}, {"limit": None, "rate": 60}]
        for value in [0, 5_000_000, 14_000_000, 40_000_000]:
            self.assertLessEqual(
                example(value, tiers=cheaper)["tax"], example(value)["tax"]
            )
        frame = calculate_wealth_tax_df(BASE, 1_900_000, 1, "test", False, 12345, 0)
        self.assertIn(
            home_value_at_tax_wealth(BASE, 1_912_345), frame["market_value"].to_list()
        )


if __name__ == "__main__":
    unittest.main()
