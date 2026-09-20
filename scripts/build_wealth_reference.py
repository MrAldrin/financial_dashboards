# /// script
# requires-python = ">=3.13"
# dependencies = ["pymupdf==1.27.2.2"]
# ///
"""Rebuild embedded browser data from immutable public snapshots; --check verifies.

Run: uv run scripts/build_wealth_reference.py [--check]
No runtime network request or local Python module is needed by the WASM app.
"""

import argparse
import hashlib
import json
from pathlib import Path
import pprint
import re

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/wealth/2026-09-20"
START = "# BEGIN GENERATED PUBLIC REFERENCE\n"
END = "# END GENERATED PUBLIC REFERENCE\n"


def derive_reference() -> dict:
    article = (SNAPSHOT / "article.html").read_text()
    charts = []
    for text in re.findall(r"<script[^>]*>(.*?)</script>", article, re.S):
        if '"jsxPath":"site/parts/highchart/Highchart"' in text:
            charts.append(json.loads(text)["props"]["highcharts"][0]["config"])
    assert len(charts) == 4
    means = next(s["data"] for s in charts[1]["series"] if s["name"] == "2024 (Kroner)")
    financial = [{"decile": i + 1, "mean": amount} for i, amount in enumerate(means)]
    composition = [
        {
            "group": str(group).strip(),
            "component": series["name"].strip(),
            "percent": percent,
        }
        for series in charts[2]["series"]
        for group, percent in zip(charts[2]["categories"], series["data"], strict=True)
    ]
    table = json.loads((SNAPSHOT / "10318.json").read_text())
    assert table["id"] == ["Desiler", "ContentsCode", "Tid"]
    assert table["size"] == [14, 3, 1]
    assert list(table["dimension"]["ContentsCode"]["category"]["index"]) == [
        "Grenseverdi",
        "Hushald",
        "BereknFormue",
    ]
    groups = table["dimension"]["Desiler"]["category"]
    wealth = [
        {
            "code": code,
            "label": groups["label"][code],
            "cutoff": table["value"][index * 3],
            "households": table["value"][index * 3 + 1],
            "mean": table["value"][index * 3 + 2],
        }
        for code, index in groups["index"].items()
    ]
    with pymupdf.open(SNAPSHOT / "housing.pdf") as pdf:
        polygon = next(d for d in pdf[7].get_drawings() if len(d["items"]) == 60)
    vertices = [polygon["items"][0][1]] + [item[2] for item in polygon["items"][:29]]
    # PDF coordinates verified against slide 8 axes: 0 and 400,000 homes.
    # Labels 1..30 are interpreted as upper edges of million-NOK bands.
    # This bin-edge convention is an assumption, not metadata from the chart.
    counts = [
        round((433.08 - point.y) / (433.08 - 163.81) * 400_000 / 100) * 100
        for point in vertices
    ]
    assert len(counts) == 30 and min(counts) >= 0
    assert 0.018 < sum(counts[14:]) / sum(counts) < 0.023
    housing = [
        {"lower": i * 1_000_000, "upper": (i + 1) * 1_000_000, "count": count}
        for i, count in enumerate(counts)
    ]
    return {
        "snapshot": "2026-09-20",
        "wealth_year": 2024,
        "financial_means": financial,
        "financial_composition": composition,
        "wealth_groups": wealth,
        "housing_bins": housing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((SNAPSHOT / "manifest.json").read_text())
    for source in manifest["sources"]:
        actual = hashlib.sha256((SNAPSHOT / source["file"]).read_bytes()).hexdigest()
        if actual != source["sha256"]:
            raise ValueError(f"Snapshot checksum mismatch: {source['file']}")
    data = derive_reference()
    notebook = ROOT / "apps/building_taxation.py"
    text = notebook.read_text()
    if args.check:
        # Compare values, not formatting: Ruff may reflow the generated literal.
        import ast

        tree = ast.parse(text)
        function = next(
            n
            for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name == "public_reference_data"
        )
        embedded = ast.literal_eval(
            next(n.value for n in function.body if isinstance(n, ast.Return))
        )
        if embedded != data:
            raise ValueError("Embedded data differs; regenerate reference")
        print("Snapshot checksums and embedded reference verified")
    else:
        literal = pprint.pformat(data, width=100, sort_dicts=False)
        body = '@app.function\ndef public_reference_data() -> dict:\n    """Public aggregates; generated offline by scripts/build_wealth_reference.py."""\n    return '
        body += literal.replace("\n", "\n    ") + "\n\n\n"
        before, rest = text.split(START)
        _, after = rest.split(END)
        notebook.write_text(before + START + body + END + after)
        (SNAPSHOT / "derived.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        )


if __name__ == "__main__":
    main()
