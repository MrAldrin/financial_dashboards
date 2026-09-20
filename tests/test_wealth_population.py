import unittest

from apps.building_taxation import weighted_policy_effect


BASE = dict(
    tiers=[{"limit": 14_000_000, "rate": 25}, {"limit": None, "rate": 70}],
    base_deduction=1_900_000,
    tax_rate=1,
    scenario_name="base",
)
OLD = {
    **BASE,
    "tiers": [{"limit": 10_000_000, "rate": 25}, {"limit": None, "rate": 70}],
}
HOUSEHOLD = dict(is_couple=False, mortgage_debt=0, other_net_wealth=0)


class PopulationTests(unittest.TestCase):
    def test_identity(self) -> None:
        result = weighted_policy_effect(
            [dict(lower=0, upper=60_000_000, count=100)], [BASE, BASE], HOUSEHOLD
        )
        self.assertEqual(result, dict(uniform=0, minimum=0, maximum=0))

    def test_linear_band_exact_integral(self) -> None:
        # Difference rises from 0 at 10m to 18,000 at 14m: average 9,000.
        result = weighted_policy_effect(
            [dict(lower=10_000_000, upper=14_000_000, count=100)],
            [BASE, OLD],
            HOUSEHOLD,
        )
        self.assertAlmostEqual(result["uniform"], 900_000)
        self.assertAlmostEqual(result["minimum"], 0)
        self.assertAlmostEqual(result["maximum"], 1_800_000)

    def test_integration_across_kink(self) -> None:
        # Difference zero 8–10m, linear 10–14m, constant 14–16m.
        bins = [dict(lower=8_000_000, upper=16_000_000, count=100)]
        result = weighted_policy_effect(bins, [BASE, OLD], HOUSEHOLD)
        self.assertAlmostEqual(result["uniform"], 900_000)
        reversed_result = weighted_policy_effect(bins, [OLD, BASE], HOUSEHOLD)
        self.assertAlmostEqual(reversed_result["uniform"], -result["uniform"])
        self.assertEqual(reversed_result["minimum"], -result["maximum"])

    def test_additive_weights_and_invalid_bins(self) -> None:
        band = dict(lower=11_000_000, upper=13_000_000, count=100)
        one = weighted_policy_effect([band], [BASE, OLD], HOUSEHOLD)
        two = weighted_policy_effect([band, band], [BASE, OLD], HOUSEHOLD)
        self.assertAlmostEqual(two["uniform"], 2 * one["uniform"])
        with self.assertRaises(ValueError):
            weighted_policy_effect(
                [dict(lower=0, upper=1, count=-1)], [BASE, OLD], HOUSEHOLD
            )


if __name__ == "__main__":
    unittest.main()
