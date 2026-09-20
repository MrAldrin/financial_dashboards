# Public wealth reference — 2026-09-20 snapshot

The app embeds compact derived aggregates, so WASM does not need filesystem imports, live SSB calls, or additional copied assets. Raw sources are retained here for audit, not loaded in the browser. The immutable snapshot's `manifest.json` records exact URLs/queries, retrieval date, and SHA-256 checksums. Do not overwrite it during a refresh; create a new dated snapshot and explicitly review revisions.

## Reproduction

```sh
uv run scripts/build_wealth_reference.py
uv run ruff format apps/building_taxation.py
uv run scripts/build_wealth_reference.py --check
uv run python -m unittest discover -s tests
```

The generator uses PyMuPDF **offline only**, not as a notebook dependency. The generated function is enclosed by named markers. Ruff formatting is safe; verification compares values. Raw JSON-stat2 responses preserve dimensions, codes, units, source revisions and missing values.

## Evidence and transformations

| Input | Population, year, method | Used for |
|---|---|---|
| `10318.json`, `10318-meta.json` | SSB PxWeb API v2; all wealth groups; `Grenseverdi,Hushald,BereknFormue`; 2024; households excluding student households; corrected February 2026 | Broad economic-net-wealth brackets, not exact ranks |
| `article.html` | SSB 19 February 2026, figures 2–3; 2024; households excluding student households; ranked by net wealth | Mean financial assets and composition; no housing/debt decomposition inferred |
| `housing.pdf` | Finance Ministry 27 February 2026 presentation; primary properties in tax-card values; slide 8 vector shape and slide 10's rounded 2% reference | Reconstructed property distribution, **not taxpayers** |
| `rates.html` | Skatteetaten page, 2026 selected by default at retrieval | Published simplified policy reference; not a legal adoption archive |

### Housing digitisation

Slide 8 has an area polygon with 30 upper vertices. At PDF y=433.08, count=0; at y=163.81, count=400,000. Linear scaling reconstructs counts, rounded to 100 properties. The sum is approximately 1,711,400, of which 34,800 (2.03%) are in labels 15–30, consistent with the **rounded** 2% above 14m on slide 10. This agreement is a check, not evidence of exact counts or a known tail.

Labels 1–30 are **assumed** to denote upper edges of 0–1m, 1–2m, …, 29–30m intervals. The chart does not publish explicit bin-edge metadata. The dashboard preserves these source categories rather than fitting a log-normal distribution. It interpolates uniformly inside a bin for exposure estimates and also reports the possible within-bin count range. These ranges condition on the assumed bin edges and digitised counts; they do not capture digitisation or bin-definition uncertainty. No count above 30m is observed here, and none is silently asserted to be zero. The yellow region explicitly indicates that gap even when the plotted x range is larger.

### Financial assets

Figure 2 supplies exact published 2024 means for ten wealth deciles. Figure 3 supplies rounded component percentages, which may sum to 99 or 101. They are not renormalised. Top 1% and top 0.1% are nested details, not additional deciles. Financial assets do not include housing, and total financial assets are not synonymous with cash available to pay tax. Unpublished housing/debt components are not fabricated.

### Compatible net-wealth residual

The additional net-balance chart joins SSB 10318 mean net wealth with article figure 2 mean financial wealth **by the same 2024 net-wealth decile and household population** (excluding students). It calculates `net wealth - financial assets = real assets - total debt`. This is a derived accounting residual, not a reconstructed household, primary-home value, or mortgage-equity estimate. A negative residual means total debt exceeds real assets; neither housing nor financial assets is drawn as a negative asset. Tests check all ten component identities and missing-value rejection. Cross-checking table 10318 exposes a small **published inconsistency**: decile counts total 2,616,825 versus 2,616,826 overall, and their weighted net-wealth mean is 3,890,862.11 versus the published 3,890,400 (difference about 462 kroner / 0.012%). The cause is not established. Tests preserve this discrepancy rather than changing the values to force reconciliation; the UI discloses it. The residual is arithmetic on published means, not a directly observed portfolio. Do not generalise this join to income deciles or another reference year.

### Policy scope

One full-owner tax unit, primary home, undiscounted other assets and fully deductible debt. Joint assessment doubles the allowance and upper wealth-tax threshold, not the property's valuation threshold. It does not cover ordinary cohabitants as a single unit, partial ownership, discounted shares/debt allocation, municipal exceptions, or municipal property tax. The reference is explicitly based on the published rate page; legal adoption history remains a research task. Input income is gross annual income and affects only burden ratios, never the wealth-tax base.

## Distribution-weighted illustration

`weighted_policy_effect` uses the same household calculator as the curves. It inserts all bin edges and both policies' valuation/allowance/upper-rate breakpoints, then integrates tax differences with trapezoids. This is exact for the supported piecewise-linear schedules under a uniform within-bin distribution; it is not tax on a group-average home. It also evaluates per-bin minimum/maximum differences as conditional within-bin-placement bounds.

The app explicitly applies the selected household's debt, undiscounted assets and assessment status to **every property**. This is one tax unit per home, not an inferred ownership distribution. Tail counts are user assumptions (default 1,000 total, half in 30–40m and half in 40–60m), never published observations. Sensitivity crosses 0.5/1/1.5 times selected debt with 0/1/2 times assumed tail counts and takes the extrema across within-bin placements. It cannot capture unknown asset/debt correlations, ownership structures, bin-edge errors, or values above the assumed tail cap. The resulting range is not a confidence interval or forecast of actual Norwegian receipts. The personal income slider does not affect this static model.

## Validation

`uv run python -m unittest discover -s tests` covers mechanics, integration, reference totals, missing cutoffs and wealth brackets. `uv run scripts/check_wealth_browser.py` serves the exported `_site` on a temporary local port, runs Chrome/Chromium and verifies a 10m reform and reset to 14m. It does not restart a Marimo session. The notebook runtime uses only Marimo, Polars and Altair; offline scripts have their own isolated dependencies.

## Remaining data gaps

- Housing tail beyond 30m and explicit original bin-edge definitions.
- Housing, financial assets and debt jointly distributed across wealth groups.
- Ownership/tax-unit mapping sufficient for a national receipts forecast.
- Enacted-law timeline, municipal exceptions and full mixed-asset debt allocation.
- Reconciliation of February (730m) versus May (830m) official threshold estimates and their different reference vintages. These are not combined or used as a calibration target here.
