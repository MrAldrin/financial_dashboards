import unittest

from apps.building_taxation import exposure_above, public_reference_data, wealth_bracket


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

    def test_partial_bin_bounds(self) -> None:
        band = [{"lower": 0, "upper": 1_000_000, "count": 1000}]
        estimate = exposure_above(band, 500_000)
        self.assertEqual(estimate["midtanslag_viste_grupper"], 500)
        self.assertEqual(estimate["nedre_viste_grupper"], 0)
        self.assertEqual(estimate["øvre_viste_grupper"], 1000)
        self.assertEqual(exposure_above(band, 1_000_000)["midtanslag_viste_grupper"], 0)


if __name__ == "__main__":
    unittest.main()
