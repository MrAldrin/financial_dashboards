"""Property-weighted assumptions, not observed national tax units."""

import unittest

from apps.building_taxation import (
    illustrative_property_templates,
    illustrative_scenario_bins,
    weighted_policy_effect,
    weighted_scenario_effect,
)

BASE = dict(
    tiers=[{"limit": 14_000_000, "rate": 25}, {"limit": None, "rate": 70}],
    base_deduction=1_900_000,
    tax_rate=1,
    upper_tax_rate=1.1,
    scenario_name="reference",
)
REFORM = {
    **BASE,
    "tiers": [{"limit": 10_000_000, "rate": 25}, {"limit": None, "rate": 70}],
    "scenario_name": "reform",
}


def unit(
    share: float = 1, joint: bool = False, assets: float = 0, debt: float = 0
) -> dict:
    return dict(
        ownership_share=share,
        is_couple=joint,
        other_net_wealth=assets,
        mortgage_debt=debt,
    )


def band(lower: float, upper: float, count: float, *templates: dict) -> dict:
    return dict(lower=lower, upper=upper, count=count, templates=list(templates))


def template(weight: float, *units: dict) -> dict:
    return dict(weight=weight, units=list(units))


class ScenarioTests(unittest.TestCase):
    def test_full_owner_collapse_and_additivity(self) -> None:
        bins = [
            band(9_000_000, 15_000_000, 100, template(1, unit(debt=1_600_000))),
            band(30_000_000, 31_000_000, 20, template(1, unit(debt=1_600_000))),
        ]
        result = weighted_scenario_effect(bins, [BASE, REFORM])
        legacy = weighted_policy_effect(
            [{key: b[key] for key in ("lower", "upper", "count")} for b in bins],
            [BASE, REFORM],
            dict(is_couple=False, mortgage_debt=1_600_000, other_net_wealth=0),
        )
        for field in ("uniform", "minimum", "maximum"):
            self.assertAlmostEqual(result[field], legacy[field], places=5)
        self.assertEqual(result["properties"], 120)
        self.assertEqual(result["tax_units"], 120)
        self.assertAlmostEqual(
            result["uniform"], result["reform"] - result["reference"]
        )
        doubled = weighted_scenario_effect(
            [{**b, "count": b["count"] * 2} for b in bins], [BASE, REFORM]
        )
        for field in result:
            self.assertAlmostEqual(doubled[field], result[field] * 2)

    def test_separate_owners_and_joint_allowances(self) -> None:
        # At 16m with no other holdings: two separate 50% taxpayers each pay
        # 5,500; one qualifying joint 100% unit pays 11,000 under the base.
        # Coincidence at this value does NOT make assessment units equivalent.
        bins = [
            band(
                15_999_999,
                16_000_001,
                10,
                template(0.5, unit(0.25), unit(0.75)),
                template(0.5, unit(joint=True)),
            )
        ]
        result = weighted_scenario_effect(bins, [BASE, BASE])
        self.assertAlmostEqual(result["reference"], 10 * (17_750 + 11_000) / 2)
        self.assertEqual(result["uniform"], 0)
        self.assertEqual(result["minimum"], 0)
        self.assertEqual(result["maximum"], 0)
        self.assertEqual(result["properties"], 10)
        self.assertEqual(result["tax_units"], 15)

    def test_assumed_profiles_and_price_correlation(self) -> None:
        low = band(
            10_000_000,
            11_000_000,
            5,
            *illustrative_property_templates(10_000_000, 11_000_000),
        )
        high = band(
            30_000_000,
            31_000_000,
            5,
            *illustrative_property_templates(30_000_000, 31_000_000),
        )
        example = weighted_scenario_effect([low, high], [BASE, REFORM])
        self.assertEqual(example["properties"], 10)
        self.assertAlmostEqual(example["tax_units"], 5 * 1.1 + 5 * 1.25)
        # Same two property counts and the same two portfolios, but reverse
        # their allocation to expensive versus cheaper homes.
        asset = unit(assets=20_000_000)
        debt = unit(debt=2_000_000)
        first = [
            band(10_000_000, 11_000_000, 1, template(1, debt)),
            band(30_000_000, 31_000_000, 1, template(1, asset)),
        ]
        second = [
            band(10_000_000, 11_000_000, 1, template(1, asset)),
            band(30_000_000, 31_000_000, 1, template(1, debt)),
        ]
        self.assertNotAlmostEqual(
            weighted_scenario_effect(first, [BASE, REFORM])["uniform"],
            weighted_scenario_effect(second, [BASE, REFORM])["uniform"],
        )

    def test_exact_kink_and_uneven_share(self) -> None:
        # Difference rises linearly from 0 to 18,000 over 10–14m.
        result = weighted_scenario_effect(
            [band(10_000_000, 14_000_000, 100, template(1, unit()))],
            [BASE, REFORM],
        )
        self.assertAlmostEqual(result["uniform"], 900_000)
        self.assertAlmostEqual(result["minimum"], 0)
        self.assertAlmostEqual(result["maximum"], 1_800_000)
        reversed_result = weighted_scenario_effect(
            [band(10_000_000, 14_000_000, 100, template(1, unit()))],
            [REFORM, BASE],
        )
        self.assertAlmostEqual(reversed_result["uniform"], -result["uniform"])
        self.assertAlmostEqual(reversed_result["minimum"], -result["maximum"])

    def test_dashboard_variants_preserve_property_units_and_identity(self) -> None:
        housing = [
            dict(lower=13_000_000, upper=14_000_000, count=100),
            dict(lower=14_000_000, upper=15_000_000, count=50),
        ]
        results = {}
        for variant in ("starting_mix", "high_assets", "high_debt", "uneven_owners"):
            bins = illustrative_scenario_bins(housing, 10, 60_000_000, variant)
            result = weighted_scenario_effect(bins, [BASE, REFORM])
            results[variant] = result
            self.assertAlmostEqual(result["properties"], 160)
            self.assertAlmostEqual(
                result["tax_units"], 100 * 1.1 + 50 * 1.2 + 10 * 1.25
            )
            self.assertAlmostEqual(
                result["uniform"], result["reform"] - result["reference"]
            )
            self.assertAlmostEqual(
                weighted_scenario_effect(bins, [BASE, BASE])["uniform"], 0
            )
        self.assertNotAlmostEqual(
            results["high_assets"]["uniform"], results["high_debt"]["uniform"]
        )
        self.assertNotAlmostEqual(
            results["uneven_owners"]["uniform"], results["starting_mix"]["uniform"]
        )
        uneven = illustrative_scenario_bins(housing, 10, 60_000_000, "uneven_owners")
        for band in uneven:
            separate = band["templates"][2]["units"]
            self.assertEqual([u["ownership_share"] for u in separate], [0.25, 0.75])
            self.assertAlmostEqual(
                sum(u["mortgage_debt"] for u in separate),
                band["templates"][0]["units"][0]["mortgage_debt"],
            )
        for invalid in ("other",):
            with self.assertRaises(ValueError):
                illustrative_scenario_bins(housing, 10, 60_000_000, invalid)
        with self.assertRaises(ValueError):
            illustrative_scenario_bins(housing, -1, 60_000_000, "starting_mix")

    def test_invalid_templates_bins_and_values(self) -> None:
        valid = band(0, 1_000_000, 1, template(1, unit()))
        for invalid in (
            band(0, 1_000_000, 1, template(0.9, unit())),
            band(0, 1_000_000, 1, template(1, unit(0.5))),
            band(0, 1_000_000, 1, template(1, unit(0), unit())),
            band(0, 1_000_000, 1, template(1, unit(debt=-1))),
            band(0, 1_000_000, 1, template(1, unit(assets=float("nan")))),
            band(0, 1_000_000, 1, template(float("inf"), unit())),
            band(0, 1_000_000, -1, template(1, unit())),
            band(0, 0, 1, template(1, unit())),
            band(0, 1_000_000, 1),
            band(0, 1_000_000, 1, template(1)),
            band(0, 1_000_000, 1, template(1, {**unit(), "is_couple": 1})),
            band(0, 1_000_000, 1, template(1, {"ownership_share": 1})),
            {"lower": 0, "upper": 1, "count": 1},
            band("missing", 1_000_000, 1, template(1, unit())),
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                weighted_scenario_effect([invalid], [BASE, REFORM])
        with self.assertRaises(ValueError):
            weighted_scenario_effect([valid, valid], [BASE, REFORM])
        with self.assertRaises(ValueError):
            illustrative_property_templates(13_000_000, 15_000_000)
        with self.assertRaises(ValueError):
            weighted_scenario_effect([valid], [BASE])


if __name__ == "__main__":
    unittest.main()
