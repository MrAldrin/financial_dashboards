"""Executable cases from docs/wealth_tax_supported_scenarios.md."""

import unittest

from polars.testing import assert_frame_equal

from apps.building_taxation import calculate_wealth_tax_df, home_value_at_tax_wealth
from test_wealth_mechanics import BASE, example


class OwnershipTests(unittest.TestCase):
    def test_worked_shares_and_joint_units(self) -> None:
        for share, joint, valuation, tax in [
            (0.5, False, 2_450_000, 5500),
            (0.25, False, 1_225_000, 0),
            (0.75, False, 3_675_000, 17_750),
            (1, True, 4_900_000, 11_000),
            (0.5, True, 2_450_000, 0),
        ]:
            with self.subTest(share=share, joint=joint):
                row = example(16_000_000, ownership_share=share, is_couple=joint)
                self.assertEqual(row["whole_home_valuation"], 4_900_000)
                self.assertEqual(row["valuation"], valuation)
                self.assertEqual(row["tax"], tax)
                self.assertEqual(row["economic_wealth"], share * 16_000_000)
        # Separate owners' allowances are not pooled as a joint unit.
        separate = sum(
            example(16_000_000, ownership_share=s)["tax"] for s in (0.25, 0.75)
        )
        self.assertEqual(separate, 17_750)
        self.assertNotEqual(separate, example(16_000_000, is_couple=True)["tax"])

    def test_no_double_allocation(self) -> None:
        row = example(
            16_000_000,
            ownership_share=0.5,
            other_net_wealth=1_000_000,
            mortgage_debt=200_000,
            annual_income=900_000,
        )
        self.assertEqual(row["tax"], 13_500)
        self.assertEqual(row["economic_wealth"], 8_800_000)
        self.assertEqual(row["income_share"], 1.5)
        self.assertNotEqual(row["valuation"], example(8_000_000)["valuation"])
        self.assertNotEqual(
            example(16_000_000, ownership_share=0.5)["tax"],
            example(16_000_000)["tax"] / 2,
        )

    def test_zero_share_and_joint_bands(self) -> None:
        for joint, assets, tax in [
            (False, 22_500_000, 207_000),
            (True, 43_000_000, 392_000),
            (True, 45_000_000, 414_000),
        ]:
            for value in (0, 16_000_000, 60_000_000):
                row = example(
                    value, ownership_share=0, other_net_wealth=assets, is_couple=joint
                )
                self.assertEqual(row["valuation"], 0)
                self.assertEqual(row["tax"], tax)
                self.assertEqual(row["economic_wealth"], assets)
                self.assertIsNone(row["income_share"])
        self.assertEqual(
            example(16_000_000, ownership_share=0, mortgage_debt=200_000)[
                "economic_wealth"
            ],
            -200_000,
        )
        self.assertIsNone(home_value_at_tax_wealth(BASE, 1, 0))
        self.assertEqual(home_value_at_tax_wealth(BASE, 0, 0), 0)
        self.assertEqual(home_value_at_tax_wealth(BASE, -1, 0), 0)

    def test_fractional_crossings_and_continuity(self) -> None:
        for share in (0.25, 0.5, 0.75, 1):
            for joint in (False, True):
                multiplier = 2 if joint else 1
                for target in (1_900_000 * multiplier, 21_500_000 * multiplier):
                    crossing = home_value_at_tax_wealth(BASE, target, share)
                    frame = calculate_wealth_tax_df(
                        BASE,
                        1_900_000,
                        1,
                        "test",
                        joint,
                        0,
                        0,
                        ownership_share=share,
                        max_value=500_000_000,
                    )
                    self.assertIn(crossing, frame["market_value"].to_list())
                    left = example(
                        crossing - 1,
                        ownership_share=share,
                        is_couple=joint,
                        max_value=500_000_000,
                    )
                    right = example(
                        crossing + 1,
                        ownership_share=share,
                        is_couple=joint,
                        max_value=500_000_000,
                    )
                    self.assertLess(abs(right["tax"] - left["tax"]), 0.02)
            low = example(14_000_000 - 1, ownership_share=share)
            at = example(14_000_000, ownership_share=share)
            high = example(14_000_000 + 1, ownership_share=share)
            self.assertAlmostEqual(at["valuation"] - low["valuation"], 0.25 * share)
            self.assertAlmostEqual(high["valuation"] - at["valuation"], 0.70 * share)

    def test_invalid_inputs(self) -> None:
        for share in (-0.01, 1.01, float("nan"), float("inf"), None, "half"):
            with self.subTest(share=share), self.assertRaises(ValueError):
                example(0, ownership_share=share)
        for field in (
            "mortgage_debt",
            "other_net_wealth",
            "annual_income",
            "base_deduction",
            "upper_threshold",
            "max_value",
            "tax_rate",
            "upper_tax_rate",
        ):
            for value in (float("nan"), float("inf"), -1):
                with (
                    self.subTest(field=field, value=value),
                    self.assertRaises(ValueError),
                ):
                    example(0, **{field: value})
        for changes in (
            {"is_couple": "married"},
            {"extra_values": [float("nan")]},
            {"tiers": [{"limit": None, "rate": float("nan")}]},
            {"base_deduction": 22_000_000},
        ):
            with self.assertRaises(ValueError):
                example(0, **changes)

    def test_full_owner_baseline(self) -> None:
        options = dict(
            tiers=BASE,
            base_deduction=1_900_000,
            tax_rate=1,
            scenario_name="test",
            is_couple=False,
            mortgage_debt=1_600_000,
            other_net_wealth=0,
            annual_income=800_000,
        )
        assert_frame_equal(
            calculate_wealth_tax_df(**options),
            calculate_wealth_tax_df(**options, ownership_share=1),
        )
        for value, valuation, tax in [
            (0, 0, 0),
            (10_000_000, 2_500_000, 0),
            (14_000_000, 3_500_000, 0),
            (15_000_000, 4_200_000, 7000),
            (20_000_000, 7_700_000, 42000),
            (42_000_000, 23_100_000, 196000),
            (60_000_000, 35_700_000, 334600),
        ]:
            row = example(value, mortgage_debt=1_600_000, annual_income=800_000)
            self.assertEqual(row["valuation"], valuation)
            self.assertAlmostEqual(row["tax"], tax)
            self.assertEqual(row["economic_wealth"], value - 1_600_000)
