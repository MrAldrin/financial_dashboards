"""Archived all-household means, not synthetic taxpayers or owner-only values."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from apps.building_taxation import (
    create_household_composition_chart,
    household_composition_reference,
    public_reference_data,
)
from scripts.build_wealth_reference import derive_household_composition

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/wealth/2026-09-20-feasibility"


class HouseholdCompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.table = json.loads((SNAPSHOT / "10316.json").read_text())
        self.metadata = json.loads((SNAPSHOT / "10316-meta.json").read_text())

    def test_extraction_and_provenance(self) -> None:
        manifest = json.loads((SNAPSHOT / "manifest.json").read_text())
        for source in manifest["sources"]:
            self.assertEqual(
                hashlib.sha256((SNAPSHOT / source["file"]).read_bytes()).hexdigest(),
                source["sha256"],
            )
        data = derive_household_composition(self.table, self.metadata)
        self.assertEqual(data, household_composition_reference())
        self.assertEqual(data["snapshot"], "2026-09-20-feasibility")
        self.assertEqual(data["national"]["primary_housing"], 3_151_100)
        self.assertEqual(data["national"]["other_real_assets"], 297_600)
        self.assertEqual(data["national"]["net_wealth"], 3_890_400)
        self.assertEqual(data["national"]["households"], 2_616_826)
        self.assertEqual(sum(row["households"] for row in data["groups"]), 2_616_826)
        self.assertEqual(len(data["groups"]), 15)

    def test_all_source_cells_and_rounding_preserved(self) -> None:
        data = household_composition_reference()
        groups = self.table["dimension"]["Hushaldstype"]["category"]["index"]
        fields = {
            "primary_housing": 1,
            "secondary_housing": 2,
            "real_assets": 0,
            "financial_assets": 3,
            "debt": 10,
            "net_wealth": 13,
            "households": 17,
        }
        for row in [data["national"], *data["groups"]]:
            for field, index in fields.items():
                self.assertEqual(
                    row[field], self.table["value"][groups[row["code"]] * 18 + index]
                )
            self.assertGreaterEqual(row["other_real_assets"], 0)
            self.assertEqual(
                row["other_real_assets"]
                + row["primary_housing"]
                + row["secondary_housing"],
                row["real_assets"],
            )
            self.assertEqual(
                row["accounting_difference"],
                row["real_assets"]
                + row["financial_assets"]
                - row["debt"]
                - row["net_wealth"],
            )
        self.assertEqual(
            {row["accounting_difference"] for row in data["groups"]}, {-100, 0, 100}
        )

    def test_invalid_sources_rejected(self) -> None:
        for value in (None, -1):
            table = deepcopy(self.table)
            table["value"][1] = value
            with self.assertRaises(ValueError):
                derive_household_composition(table, self.metadata)
        for index, change in [(0, -1_000_000), (13, 1_000), (17, 1)]:
            table = deepcopy(self.table)
            table["value"][index] += change
            with self.assertRaises(ValueError):
                derive_household_composition(table, self.metadata)
        table = deepcopy(self.table)
        table["dimension"]["Tid"]["category"]["index"] = {"2025": 0}
        with self.assertRaises(ValueError):
            derive_household_composition(table, self.metadata)
        metadata = deepcopy(self.metadata)
        metadata["dimension"]["ContentsCode"]["category"]["unit"]["Gjeld"]["base"] = (
            "millioner kr"
        )
        with self.assertRaises(ValueError):
            derive_household_composition(self.table, metadata)

    def test_existing_reference_unchanged(self) -> None:
        original = json.loads(
            (ROOT / "data/wealth/2026-09-20/derived.json").read_text()
        )
        self.assertEqual(public_reference_data(), original)

    def test_chart_schema_and_signed_components(self) -> None:
        data = household_composition_reference()
        chart = create_household_composition_chart(data)
        spec = chart.to_dict(validate=True)
        self.assertEqual(spec["layer"][0]["encoding"]["y"]["stack"], "zero")
        self.assertEqual(spec["layer"][1]["encoding"]["y"]["field"], "net_wealth")
        self.assertEqual(spec["layer"][1]["mark"]["shape"], "diamond")
        bars = spec["datasets"][spec["layer"][0]["data"]["name"]]
        self.assertEqual(len(bars), 15 * 5)
        self.assertNotIn("50", {row["code"] for row in bars})
        for group in data["groups"]:
            rows = [row for row in bars if row["code"] == group["code"]]
            self.assertEqual(
                sum(row["amount"] for row in rows),
                group["net_wealth"] + group["accounting_difference"],
            )
            for row in rows:
                if row["component"] == "Samlet gjeld":
                    self.assertEqual(row["amount"], -group["debt"])
                else:
                    self.assertGreaterEqual(row["amount"], 0)


if __name__ == "__main__":
    unittest.main()
