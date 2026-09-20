import unittest
from copy import deepcopy

from apps.building_taxation import (
    decile_net_balance,
    exposure_above,
    public_reference_data,
    wealth_bracket,
)


class PublicReferenceTests(unittest.TestCase):
    def test_source_totals(self) -> None:
        data = public_reference_data()
        bins = data["housing_bins"]
        self.assertEqual(sum(b["count"] for b in bins), 1_711_400)
        self.assertEqual(sum(b["count"] for b in bins[14:]), 34_800)
        self.assertEqual(len(data["financial_means"]), 10)
        self.assertEqual(data["financial_means"][-1]["mean"], 12_322_000)
        self.assertEqual(len(data["financial_composition"]), 60)
        self.assertIsNone(data["wealth_groups"][0]["cutoff"])
        for left, right in zip(bins, bins[1:]):
            self.assertEqual(left["upper"], right["lower"])

    def test_wealth_cutoffs(self) -> None:
        groups = public_reference_data()["wealth_groups"]
        self.assertIn("95. og 99.", wealth_bracket(14_000_000, groups))
        self.assertIn("90. og 95.", wealth_bracket(11_000_000, groups))
        self.assertIn("90. og 95.", wealth_bracket(8_454_200, groups))
        self.assertIn("0. og 10.", wealth_bracket(-10_000_000, groups))
        self.assertIn("Topp 0,1", wealth_bracket(133_425_400, groups))

    def test_decile_net_balance_identity(self) -> None:
        data = public_reference_data()
        frame = decile_net_balance(data)
        for row in frame.to_dicts():
            self.assertEqual(
                row["Finansformue"] + row["Realkapital minus samlet gjeld"],
                row["net_wealth"],
            )
        self.assertEqual(frame["Realkapital minus samlet gjeld"][0], -1_242_300)
        self.assertEqual(frame["Realkapital minus samlet gjeld"][-1], 7_889_300)
        weighted_mean = (frame["net_wealth"] * frame["households"]).sum() / frame[
            "households"
        ].sum()
        # Preserve the published inconsistency; do not force calibrated totals.
        self.assertAlmostEqual(
            weighted_mean - data["wealth_groups"][0]["mean"], 462.106369, places=5
        )
        self.assertEqual(
            frame["households"].sum(), data["wealth_groups"][0]["households"] - 1
        )

    def test_decile_missing_values_rejected(self) -> None:
        data = deepcopy(public_reference_data())
        data["financial_means"][0]["mean"] = None
        with self.assertRaises(ValueError):
            decile_net_balance(data)
        data["financial_means"].pop()
        with self.assertRaises(ValueError):
            decile_net_balance(data)

    def test_partial_bin_bounds(self) -> None:
        band = [{"lower": 0, "upper": 1_000_000, "count": 1000}]
        estimate = exposure_above(band, 500_000)
        self.assertEqual(estimate["midtanslag_viste_grupper"], 500)
        self.assertEqual(estimate["nedre_viste_grupper"], 0)
        self.assertEqual(estimate["øvre_viste_grupper"], 1000)
        self.assertEqual(exposure_above(band, 1_000_000)["midtanslag_viste_grupper"], 0)


if __name__ == "__main__":
    unittest.main()
