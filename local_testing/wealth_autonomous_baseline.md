# T0 — Wealth dashboard technical baseline

Measured 21 September 2026 (12:04–12:06 UTC), against parent revision `6a97f04f`. T0 changes documentation only; financial logic, sources, dependencies and browser checker are unchanged. No watched Marimo session was restarted.

## Environment and checks

Linux 7.0.0-31-generic, x86_64; uv 0.11.3; Python 3.13.11. Project environment: Marimo 0.23.14, Polars 1.42.1, Altair 6.2.2, Ruff 0.15.22. Exporter's `uvx marimo --version`: **0.24.2**. Browser: Google Chrome 153.0.8010.52, headless, 1400×1000 viewport. Script dependency environments are resolved by uv from their PEP 723 metadata.

Run from repository root:

| Command | Actual result |
|---|---|
| `uv run python -m unittest discover -s tests` | 23 tests passed, 0.553 seconds |
| `uv run ruff check .` | All checks passed |
| `uv run marimo check apps/building_taxation.py` | Passed, no diagnostics |
| `uv run scripts/build_wealth_reference.py --check` | Snapshot checksums and both embedded references verified |
| `uv run .github/scripts/build.py` | All three exports succeeded; index generated |
| `uv run scripts/check_wealth_browser.py` | Passed on three consecutive runs; no captured console/page errors |

Read the entire notebook, generator, browser checker and all five wealth test files before verification. `app.run()` executed both within the test suite and separately to capture definitions/results below. Chart schemas validate in existing tests.

An additional SHA-256 sweep over every `data/wealth/*/manifest.json` passed: original 5, feasibility 46, legal 9, official 3, reconciliation 6 (**69 archived files**). Also verified the legal compressed handbook's `uncompressed_sha256` where present. No snapshot bytes changed.

Reproduce the hash sweep with Python: load each manifest, iterate `sources`, compare `hashlib.sha256((manifest.parent / source['file']).read_bytes()).hexdigest()` with `source['sha256']`; for `uncompressed_sha256`, hash `gzip.decompress(raw)` as well.

## Default inputs

All money is NOK; tax is annual.

- One full-owner individual tax unit; joint-assessment switch off.
- Debt 1,600,000; other undiscounted assets before debt 0; gross income 800,000.
- Selected whole-home value 14,000,000; curve maximum 60,000,000.
- Both reference and sandbox: 25% included through 14,000,000, then 70% of the excess.
- Personal allowance 1,900,000; ordinary/upper rates 1% / 1.1%; upper threshold 21,500,000 before the allowance.
- Assumed tail count 1,000; upper value 60,000,000. Half in 30–40m, half in 40–60m, uniform within bins.
- Sensitivity debt factors 0.5/1/1.5 and tail factors 0/1/2. These are assumptions, not observed population profiles.

## Regression outputs

The reference and sandbox full curves coincide; every default difference is zero. `tax_base` below is after debt and allowance but **before the zero floor**.

| Home value | Housing valuation | Tax base | Tax | Tax / income (%) |
|---:|---:|---:|---:|---:|
| 0 | 0 | −3,500,000 | 0 | 0 |
| 10,000,000 | 2,500,000 | −1,000,000 | 0 | 0 |
| 14,000,000 | 3,500,000 | 0 | 0 | 0 |
| 15,000,000 | 4,200,000 | 700,000 | 7,000 | 0.875 |
| 20,000,000 | 7,700,000 | 4,200,000 | 42,000 | 5.25 |
| 42,000,000 | 23,100,000 | 19,600,000 | 196,000 | 24.5 |
| 60,000,000 | 35,700,000 | 32,200,000 | 334,600 | 41.825 |

Selected 14m home: economic net wealth 12,400,000; tax-valued net wealth before allowance 1,900,000; both taxes and difference zero. Both policies' tax onset is 14m and upper-band crossing 42m.

To reproduce values without modifying controls: `from apps.building_taxation import app, calculate_wealth_tax_df`; `_, d = app.run()`; inspect `d['shared_inputs']`, `d['policy_inputs']`, `d['selected_rows']`, `d['marker_notes']`, `d['central_effect']`. Calculate the full reference frame with `calculate_wealth_tax_df(**d['policy_inputs'][0], **d['shared_inputs'])`, selecting the table's market values. Compare floating-point values with tolerance rather than formatted strings.

Population changes below use the original 30 housing bins plus the two default assumed tail bins, unchanged household inputs, and sandbox minus reference:

| Housing tier preset | Uniform change | Within-bin minimum | Within-bin maximum |
|---|---:|---:|---:|
| 14m (identity) | 0 | 0 | 0 |
| 10m | 869,399,285.714286 | 783,900,000 | 978,800,000 |
| 20m | −526,009,821.428571 | −586,350,000 | −464,850,000 |

Reproduce using `weighted_policy_effect(bins, [reference_policy, changed_policy], d['shared_inputs'])`, changing only the finite tier limit to 10m or 20m. These bounds hold the central debt/tail assumptions fixed; they are **not** the wider nine-scenario sensitivity envelope. Default identity gives zero in all nine scenarios.

Browser check confirms 14m→10m produces selected-home tax 18,000 and displayed aggregate +869.4m, then 10m→14m restores zero. Official table and household-composition specification remain fixed throughout; composition has 75 signed component records, including 15 negative debt records, and a rendered canvas. Desktop custom-input, mobile and accessibility coverage are T1, not claimed here.

## Browser timing observations

Repeat exactly:

```bash
/usr/bin/time -f 'browser wall seconds=%e' uv run scripts/check_wealth_browser.py
```

Three sequential complete-process wall times: **14.19, 15.49, 14.33 seconds** (median 14.33). Each run launches a fresh headless Chrome browser with the existing checker's temporary context and local HTTP server. No deliberate network/CPU throttling; uv/package/OS caches were not cleared; runtime network downloads may vary.

These measure the **whole smoke test** (startup, initial rendering, reform, reset and cleanup), not isolated time-to-interactive or update latency. The script currently exposes no phase timing. Do not turn these three observations into a machine-independent performance threshold. T1 should add separate load/update instrumentation before making optimisation decisions.

## Export size and reproducibility caveats

Target `_site/apps/building_taxation.html`: **212,373 bytes**. Existing `_site` after build: 3,336 files / 139,182,364 bytes, including stale assets and old exports. The build does not clean the output directory, so this total is unsuitable for regression comparisons.

A second full build into an empty temporary directory succeeded:

```bash
OUT=$(mktemp -d /tmp/wealth-t0-export-XXXXXX)
uv run .github/scripts/build.py --output-dir "$OUT"
```

Sum regular-file `stat().st_size` recursively (logical uncompressed bytes, not disk allocation):

| Fresh output scope | Files | Bytes |
|---|---:|---:|
| Entire three-notebook site | 1,009 | 49,144,626 |
| `apps/` (both apps and shared assets) | 724 | 27,088,584 |
| `notebooks/` | 284 | 22,052,972 |
| Target wealth HTML alone | 1 | 212,373 |

Fresh measurement directory: `/tmp/wealth-t0-export-xU318O` (temporary, not a durable artifact). Browser runs used the newly regenerated target in `_site`, not this separate fresh directory. HTML/export success is not substituted for browser execution. Export size does not include remote runtime downloads or measure transferred compressed bytes.

**Known maintenance limits:** build invokes unpinned `uvx marimo`, whereas checks use the project environment; preserve the versions above for comparisons. Build catches individual export failures and can still finish successfully: inspect all per-file results, not just exit status. No build-system change is part of T0.

## Legal provenance comparison

Compared visible introduction, assessment control, official-scenario section and financial constants against `data/wealth/legal_audit_2026.md` and verified the archived sources' hashes.

- 14m / 25% / 70%, 1.9m allowance, 21.5m upper threshold and combined 1% / 1.1% agree with the audit. Joint assessment already doubles personal thresholds, not the housing tier.
- The audit establishes enactment as law 23 June 2026 no. 66, parts II/IV, effective for income year 2026. The app only links published agency rates. This is conservative/incomplete provenance, not a numeric contradiction; dated enactment citation and eligibility detail belong in T2.
- Full ownership, undiscounted other assets, single debt subtraction and municipal/special-case exclusions remain explicit. Standard combined rates must not become a claim about every municipality. Marriage-year/separation and qualifying-cohabitant eligibility are not determined by the switch.
- The static −1,250m (12 February), −730m (27 February) and −830m (12 May, corrected edition 11 June) are explicitly dated fiscal scenarios, **not enactment evidence**. Their baselines differ; February/May numerical reconciliation remains unresolved. No calibration or summation is performed.
- Annual parliamentary rate-resolution archive, municipal decisions and special cases remain audit gaps. T0 checks agreement with archived evidence; it does not claim a fresh web/legal audit.

## WASM compatibility and remaining scope

**PASS for the exercised existing browser flow.** Marimo, Polars and Altair are the only notebook packages and are listed in PEP 723 metadata; all are supported by the existing Marimo/Pyodide runtime. No runtime local-data read, subprocess/threading or environment-variable requirement exists in the notebook. PyMuPDF is generator-only; Playwright is test-only. Embedded public data avoid live SSB requests. Fully disconnected cold startup was not tested; browser runtime/package loading is distinct from offline reference-data availability.

No failing technical baseline checks or environmental blockers found. This does not imply comprehensive legal correctness, mobile/accessibility acceptance or complete interaction coverage.

## Progress

- [x] Read required code/tests and latest prior progress.
- [x] Run all existing checks and verify archived hashes.
- [x] Capture defaults, representative results, export sizes and repeatable timing observations.
- [x] Compare app provenance with archived audit; document existing limitations.
- [x] T0 complete; next ready task **T1**, objective usability/accessibility and interaction hardening.
