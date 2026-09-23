# /// script
# requires-python = ">=3.13"
# dependencies = ["pymupdf==1.27.2.2"]
# ///
"""Rebuild embedded browser data from immutable public snapshots; --check verifies.

Run: uv run scripts/build_wealth_reference.py [--check]
No runtime network request or local Python module is needed by the WASM app.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import pprint
import re

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data/wealth/2026-09-20"
COMPOSITION_SNAPSHOT = ROOT / "data/wealth/2026-09-20-feasibility"


def derive_reference() -> dict:
    import pymupdf

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


def derive_household_composition(table: dict, metadata: dict) -> dict:
    """Extract unconditional means by code; retain published rounding residuals."""
    if (
        table["id"] != ["Hushaldstype", "ContentsCode", "Tid"]
        or table["size"] != [16, 18, 1]
        or table["dimension"]["Tid"]["category"]["index"] != {"2024": 0}
        or len(table["value"]) != 288
    ):
        raise ValueError("Unexpected 10316 dimensions or reference year")
    groups = table["dimension"]["Hushaldstype"]["category"]
    metrics = table["dimension"]["ContentsCode"]["category"]
    fields = {
        "primary_housing": "MarknverdiPri",
        "secondary_housing": "MarknverdiSek",
        "real_assets": "Realkapital",
        "financial_assets": "SkattplKapital",
        "debt": "Gjeld",
        "net_wealth": "FormueNettBerekn",
        "households": "Hushald",
    }
    if set(groups["index"]) != {str(n) for n in range(50, 66)}:
        raise ValueError("Expected national total and 15 household types")
    rows = []
    for code, position in sorted(groups["index"].items(), key=lambda pair: pair[1]):
        row = {"code": code, "label": groups["label"][code]}
        for field, metric in fields.items():
            expected_unit = "hushald" if field == "households" else "kr"
            if (
                metadata["dimension"]["ContentsCode"]["category"]["unit"][metric][
                    "base"
                ]
                != expected_unit
            ):
                raise ValueError(f"Unexpected unit for {metric}")
            value = table["value"][position * 18 + metrics["index"][metric]]
            if not isinstance(value, int) or (field != "net_wealth" and value < 0):
                raise ValueError(f"Missing or invalid mean/count: {code}/{metric}")
            row[field] = value
        row["other_real_assets"] = (
            row["real_assets"] - row["primary_housing"] - row["secondary_housing"]
        )
        row["accounting_difference"] = (
            row["real_assets"]
            + row["financial_assets"]
            - row["debt"]
            - row["net_wealth"]
        )
        if row["other_real_assets"] < 0 or abs(row["accounting_difference"]) > 100:
            raise ValueError(f"Unexpected component accounting: {code}")
        rows.append(row)
    national = next(row for row in rows if row["code"] == "50")
    types = [row for row in rows if row["code"] != "50"]
    if sum(row["households"] for row in types) != national["households"]:
        raise ValueError("Household-type counts do not reconcile")
    return {
        "schema_version": 1,
        "snapshot": "2026-09-20-feasibility",
        "table": "10316",
        "year": 2024,
        "updated": table["updated"],
        "national": national,
        "groups": types,
    }


def derive_age_composition(table: dict, metadata: dict) -> dict:
    """Extract all-household means by main earner age; no taxpayer inference."""
    if (
        table["id"] != ["AlderHovedinn", "ContentsCode", "Tid"]
        or table["size"] != [8, 17, 1]
        or table["dimension"]["Tid"]["category"]["index"] != {"2024": 0}
        or len(table["value"]) != 136
    ):
        raise ValueError("Unexpected 10317 dimensions or reference year")
    groups = table["dimension"]["AlderHovedinn"]["category"]
    metrics = table["dimension"]["ContentsCode"]["category"]
    if list(groups["index"]) != [
        "999D",
        "-24",
        "25-34",
        "35-44",
        "45-54",
        "55-66",
        "67-79",
        "80+",
    ]:
        raise ValueError("Unexpected age groups")
    fields = {
        "primary_housing": "MarknverdiPri",
        "secondary_housing": "MarknverdiSek",
        "real_assets": "Realkapital",
        "financial_assets": "SkattplKapital",
        "debt": "Gjeld",
        "net_wealth": "FormueNettBerekn",
        "households": "Hushald",
    }
    rows = []
    for code, position in groups["index"].items():
        row = {"code": code, "label": groups["label"][code]}
        for field, metric in fields.items():
            unit = metadata["dimension"]["ContentsCode"]["category"]["unit"][metric][
                "base"
            ]
            if unit != ("hushald" if field == "households" else "kr"):
                raise ValueError(f"Unexpected unit for {metric}")
            value = table["value"][position * 17 + metrics["index"][metric]]
            if not isinstance(value, int) or (field != "net_wealth" and value < 0):
                raise ValueError(f"Invalid age mean/count: {code}/{metric}")
            row[field] = value
        row["other_real_assets"] = (
            row["real_assets"] - row["primary_housing"] - row["secondary_housing"]
        )
        row["accounting_difference"] = (
            row["real_assets"]
            + row["financial_assets"]
            - row["debt"]
            - row["net_wealth"]
        )
        if row["other_real_assets"] < 0 or abs(row["accounting_difference"]) > 100:
            raise ValueError(f"Unexpected age accounting: {code}")
        rows.append(row)
    national, *ages = rows
    if (
        sum(row["households"] for row in ages) != national["households"]
        or national["households"] != 2_616_826
    ):
        raise ValueError("Age groups do not reconcile to national households")
    return {
        "schema_version": 1,
        "snapshot": "2026-09-20-feasibility",
        "table": "10317",
        "year": 2024,
        "updated": table["updated"],
        "national": national,
        "groups": ages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for snapshot in (SNAPSHOT, COMPOSITION_SNAPSHOT):
        manifest = json.loads((snapshot / "manifest.json").read_text())
        for source in manifest["sources"]:
            actual = hashlib.sha256(
                (snapshot / source["file"]).read_bytes()
            ).hexdigest()
            if actual != source["sha256"]:
                raise ValueError(f"Snapshot checksum mismatch: {source['file']}")
    references = [
        ("PUBLIC REFERENCE", "public_reference_data", derive_reference()),
        (
            "HOUSEHOLD COMPOSITION",
            "household_composition_reference",
            derive_household_composition(
                json.loads((COMPOSITION_SNAPSHOT / "10316.json").read_text()),
                json.loads((COMPOSITION_SNAPSHOT / "10316-meta.json").read_text()),
            ),
        ),
        (
            "AGE COMPOSITION",
            "age_composition_reference",
            derive_age_composition(
                json.loads((COMPOSITION_SNAPSHOT / "10317.json").read_text()),
                json.loads((COMPOSITION_SNAPSHOT / "10317-meta.json").read_text()),
            ),
        ),
    ]
    # The original derived artifact is immutable, not an output to overwrite.
    if references[0][2] != json.loads((SNAPSHOT / "derived.json").read_text()):
        raise ValueError("Original reference changed; use a new snapshot")
    notebook = ROOT / "apps/building_taxation.py"
    text = notebook.read_text()
    for marker, name, data in references:
        if args.check:
            # Compare values, not formatting: Ruff may reflow generated literals.
            function = next(
                n
                for n in ast.parse(text).body
                if isinstance(n, ast.FunctionDef) and n.name == name
            )
            embedded = ast.literal_eval(
                next(n.value for n in function.body if isinstance(n, ast.Return))
            )
            if embedded != data:
                raise ValueError(f"Embedded {name} differs; regenerate reference")
        else:
            literal = pprint.pformat(data, width=100, sort_dicts=False)
            body = f'@app.function\ndef {name}() -> dict:\n    """Public aggregates; generated offline by scripts/build_wealth_reference.py."""\n    return '
            body += literal.replace("\n", "\n    ") + "\n\n\n"
            start = f"# BEGIN GENERATED {marker}\n"
            end = f"# END GENERATED {marker}\n"
            before, rest = text.split(start)
            _, after = rest.split(end)
            text = before + start + body + end + after
    if args.check:
        print("Snapshot checksums and all three embedded references verified")
    else:
        notebook.write_text(text)


if __name__ == "__main__":
    main()
