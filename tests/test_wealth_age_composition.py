"""10317 age means describe statistical households, never modelled tax units."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from apps.building_taxation import (
    age_composition_reference,
    create_household_composition_chart,
)
from scripts.build_wealth_reference import derive_age_composition

SNAPSHOT = Path(__file__).resolve().parents[1] / "data/wealth/2026-09-20-feasibility"


class AgeCompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.table = json.loads((SNAPSHOT / "10317.json").read_text())
        self.metadata = json.loads((SNAPSHOT / "10317-meta.json").read_text())

    def test_archived_cells_and_accounting(self) -> None:
        data = derive_age_composition(self.table, self.metadata)
        self.assertEqual(data, age_composition_reference())
        self.assertEqual(data["table"], "10317")
        self.assertEqual(data["year"], 2024)
        self.assertEqual(data["national"]["households"], 2_616_826)
        self.assertEqual(data["national"]["net_wealth"], 3_890_400)
        self.assertEqual(sum(row["households"] for row in data["groups"]), 2_616_826)
        self.assertEqual(len(data["groups"]), 7)
        fields = {
            "primary_housing": "MarknverdiPri",
            "secondary_housing": "MarknverdiSek",
            "real_assets": "Realkapital",
            "financial_assets": "SkattplKapital",
            "debt": "Gjeld",
            "net_wealth": "FormueNettBerekn",
            "households": "Hushald",
        }
        positions = self.table["dimension"]["AlderHovedinn"]["category"]["index"]
        metrics = self.table["dimension"]["ContentsCode"]["category"]["index"]
        for row in [data["national"], *data["groups"]]:
            for field, metric in fields.items():
                self.assertEqual(
                    row[field],
                    self.table["value"][positions[row["code"]] * 17 + metrics[metric]],
                )
            self.assertEqual(
                row["other_real_assets"]
                + row["primary_housing"]
                + row["secondary_housing"],
                row["real_assets"],
            )
            self.assertLessEqual(abs(row["accounting_difference"]), 100)
        self.assertEqual(
            {row["accounting_difference"] for row in data["groups"]}, {0, 100}
        )

    def test_invalid_source_rejected(self) -> None:
        for value in (None, -1):
            table = deepcopy(self.table)
            table["value"][1] = value
            with self.assertRaises(ValueError):
                derive_age_composition(table, self.metadata)
        table = deepcopy(self.table)
        table["dimension"]["Tid"]["category"]["index"] = {"2025": 0}
        with self.assertRaises(ValueError):
            derive_age_composition(table, self.metadata)
        metadata = deepcopy(self.metadata)
        metadata["dimension"]["ContentsCode"]["category"]["unit"]["Gjeld"]["base"] = (
            "millioner kr"
        )
        with self.assertRaises(ValueError):
            derive_age_composition(self.table, metadata)

    def test_chart_has_signed_components_not_national_as_extra_group(self) -> None:
        spec = create_household_composition_chart(age_composition_reference()).to_dict(
            validate=True
        )
        bars = spec["datasets"][spec["layer"][0]["data"]["name"]]
        self.assertEqual(len(bars), 35)
        self.assertEqual(sum(row["amount"] < 0 for row in bars), 7)
        self.assertNotIn("999D", {row["code"] for row in bars})
        self.assertEqual(spec["layer"][1]["encoding"]["y"]["field"], "net_wealth")


if __name__ == "__main__":
    unittest.main()
