"""Keep dated references independent of live policy and preserve source provenance."""

import ast
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OfficialContextTests(unittest.TestCase):
    def test_archived_sources(self) -> None:
        snapshot = ROOT / "data/wealth/2026-09-20-official"
        manifest = json.loads((snapshot / "manifest.json").read_text())
        self.assertEqual(len(manifest["sources"]), 3)
        for source in manifest["sources"]:
            self.assertEqual(
                hashlib.sha256((snapshot / source["file"]).read_bytes()).hexdigest(),
                source["sha256"],
            )
        chapter = (snapshot / "proposition.html").read_text()
        for amount in ("830", "550", "280"):
            self.assertIn(f"{amount}\u00a0mill. kroner", chapter)
        index = (snapshot / "proposition-index.html").read_text()
        self.assertIn("2026-05-12", index)
        self.assertIn("11.6.2026", index)

    def test_context_is_static_and_preserves_comparison_caveats(self) -> None:
        tree = ast.parse((ROOT / "apps/building_taxation.py").read_text())
        cells = [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and any(
                isinstance(value, ast.Constant)
                and isinstance(value.value, str)
                and "### Offisielle scenarioer" in value.value
                for value in ast.walk(node)
            )
        ]
        self.assertEqual(len(cells), 1)
        cell = cells[0]
        self.assertEqual(cell.args.args, [])
        # Only a literal markdown call: no slider values or live calculations.
        call = cell.body[0].value
        self.assertIsInstance(call, ast.Call)
        text = ast.literal_eval(call.args[0])
        for phrase in (
            "−1 250",
            "−730",
            "−830",
            "+550",
            "−280",
            "114 600 personer",
            "1,72 mill. kr",
            "11 000 kr",
            "ikke avklart",
            "bokført og påløpt",
            "motsatt vei",
            "Persondesilene",
            "2023-utvalg",
            "atferdsendringer",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
