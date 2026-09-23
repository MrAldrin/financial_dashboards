# Public wealth reference — 2026-09-20 snapshot

The app embeds compact derived aggregates, so WASM does not need filesystem imports, live SSB calls, or additional copied assets. Raw sources are retained here for audit, not loaded in the browser. The immutable snapshot's `manifest.json` records exact URLs/queries, retrieval date, and SHA-256 checksums. Do not overwrite it during a refresh; create a new dated snapshot and explicitly review revisions.

## Reproduction

```sh
uv run scripts/build_wealth_reference.py
uv run ruff format apps/building_taxation.py
uv run scripts/build_wealth_reference.py --check
uv run python -m unittest discover -s tests
```

The generator uses PyMuPDF **offline only**, not as a notebook dependency. Three independently sourced functions are enclosed by named markers: the original `public_reference_data()`, schema-version-1 `household_composition_reference()` (10316) and `age_composition_reference()` (10317) from `2026-09-20-feasibility/`. Ruff formatting is safe; verification compares values. Generation writes only the notebook, never into either immutable snapshot; it also checks the original reference against its archived `derived.json`. Raw JSON-stat2 responses preserve dimensions, codes, units, source revisions and missing values.

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

One selected individual or qualifying-joint tax unit, with full or fractional ownership of an ordinary primary home, undiscounted other assets and fully deductible debt. Whole-property valuation precedes share allocation; assets/debt/income are already tax-unit amounts and are not share-scaled. Joint assessment doubles the allowance and upper wealth-tax threshold, not the property's valuation threshold. Ordinary cohabitants are separate units. Mixed residence within the unit, special multi-unit buildings, discounted assets/debt allocation, municipal exceptions and property tax remain excluded. The app cites housing enactment and published standard rates; it does not determine eligibility. See [supported scenarios and worked examples](../../docs/wealth_tax_supported_scenarios.md) and the [legal audit](legal_audit_2026.md). Gross annual income affects only burden ratios, never the wealth-tax base.

## Distribution-weighted illustration

`weighted_policy_effect` uses the same household calculator as the curves. It inserts all bin edges and both policies' valuation/allowance/upper-rate breakpoints, then integrates tax differences with trapezoids. This is exact for the supported piecewise-linear schedules under a uniform within-bin distribution; it is not tax on a group-average home. It also evaluates per-bin minimum/maximum differences as conditional within-bin-placement bounds.

The app explicitly applies the selected household's debt, undiscounted assets and assessment status to **every property**. This remains one **full-owner** tax unit per home, not an inferred ownership distribution. The personal ownership-share control is explicitly ignored in this legacy illustration. Tail counts are user assumptions (default 1,000 total, half in 30–40m and half in 40–60m), never published observations. Sensitivity crosses 0.5/1/1.5 times selected debt with 0/1/2 times assumed tail counts and takes the extrema across within-bin placements. It cannot capture unknown asset/debt correlations, ownership structures, bin-edge errors, or values above the assumed tail cap. The resulting range is not a confidence interval or forecast of actual Norwegian receipts. The personal income slider does not affect this static model.

## Validation

`uv run python -m unittest discover -s tests` covers mechanics, integration, reference totals, missing cutoffs and wealth brackets. `uv run scripts/check_wealth_browser.py` serves the exported `_site` on a temporary local port, runs Chrome/Chromium and verifies a 10m reform and reset to 14m. It does not restart a Marimo session. The notebook runtime uses only Marimo, Polars and Altair; offline scripts have their own isolated dependencies.

## Dated official scenario context

The separate immutable `2026-09-20-official/` snapshot archives the directly verified chapter 3 of Prop. 95 LS, its index (12 May 2026; corrected edition 11 June 2026), and the minister's 12 February 2026 answer to question 1404. Its manifest records URLs, retrieval date and SHA-256 checksums; unit tests verify them. The February presentation is already archived as `2026-09-20/housing.pdf`. The notebook embeds a static, linked Markdown explanation, not another calculator or runtime data fetch. Browser checks confirm its table stays unchanged through policy changes.

Claims ledger:

| Source location | Claim and scope |
|---|---|
| Question 1404, p. 2 | 10→20m threshold: −1,250m NOK accrued versus adopted 2026 rules; approximately 114,600 people benefiting, average relief about 11,000 NOK, mean gross income among beneficiaries 1.72m NOK. Published rounded quantities are not forced to multiply exactly. |
| Question 1404, pp. 5–6 | LOTTE-Skatt, 2023 sample projected to 2026, updated tax-card housing values; excludes behavioural responses and additional documented downward value corrections. Person groups are not joined to SSB household deciles. |
| Housing presentation, slide 5 | −730m threshold contribution in a figure comparing with continuation of the 2025 system into 2026. No extra accrued/booked classification is inferred from this slide. |
| Proposition, chapter 3, paragraphs 3–4 | −830m accrued in 2026 for 10→14m versus adopted budget; +550m updated model estimate versus assumptions behind adoption; combined package −280m accrued, with booked 2026 effect estimated at zero. These are not three separate threshold reforms. |

The [bounded official-estimate investigation](official_estimate_reconciliation_2026.md) records the comparison matrix, six-query search and unresolved evidence gap. Six newly archived sources are in `2026-09-20-reconciliation/` with exact URLs and SHA-256 hashes. The original May proposition already contains −830m; neither linked correction letter revises it. February's published manuscript explicitly ties −730m to the 2025 comparison and states a −280m package total, but does not provide a bridge to May. SSB explains its January-versus-earlier model revision, not this threshold-estimate difference.

February's −730m and May's −830m remain unreconciled, separately dated estimates. The live app instead compares arbitrary settings against a 14m reference, so choosing 10m reverses the official relief direction. Reversing a sign does not make its property/common-profile population compatible with an official national model. The app's official-scenario section makes no calibration, attribution of income to individual homeowners, or enacted-law claim; the separate legal audit below now establishes the housing amendment's adoption.

## Legal evidence audit

[Legal audit and claims ledger](legal_audit_2026.md) records the adoption timeline, statutory housing rule, joint-assessment exceptions, ordinary co-ownership allocation, municipal-rate ceiling and mixed-asset debt limitations. `2026-09-20-legal/` archives nine sources with URL/date/hash metadata; the large handbook HTML is losslessly gzip-compressed with both stored and uncompressed hashes. The older handbook still uses 10m examples: its allocation guidance is not used as evidence for the current threshold. The enacted 14m rule is independently verified against the promulgated amendment and consolidated statute. No calculator or app-source changes were made by this audit. Subsequently authorised T2 implements only the bounded ownership scenarios linked above; the original audit remains a historical record.

Municipality-specific 2026 decisions, the annual parliamentary tax-resolution archive and special legal cases remain open. Human scope/visual review is deferred to the plan's final review gate.

## Public composition and ownership feasibility

The [bounded feasibility investigation](public_data_feasibility_2026.md) records the population/ranking/valuation/denominator matrix, sources checked and remaining joint-data gaps. The immutable `2026-09-20-feasibility/` snapshot contains 46 raw responses with exact URLs/queries, retrieval dates and SHA-256 hashes. Earlier snapshots and browser reference values remain unchanged.

Additional claims ledger:

| Source location | Verified claim and limit |
|---|---|
| 10316/10317, 2024 component means and counts | Primary/secondary housing, financial assets, total debt and derived other real assets can be shown together by household type or main-earner age. These are all-household means, not owner-only means or net-wealth-decile portfolios. Group accounting discrepancies of up to NOK 100 are retained. |
| Household-statistics definitions; 10315 | Total debt includes housing-company debt shares and reverses tax-related debt reductions. Student/unsecured-debt sources can use different reporting times; subtraction does not identify mortgage debt. 10315 means condition on having an amount, unlike 10316/17. |
| 14066 and survey definitions | Published 2025 home-value means by mortgage-size group provide limited joint context; 2024 home-value cells are missing. The mortgage-mean variable conditions on having a loan, even in the “all owners” row. Survey responses/weights and self-reported values differ from H24 administrative wealth data. |
| 14890/91/14898/14900 and register-statistics definitions | Revised tenure statistics support household-type/tenure cross-tabs. Person counts include all members of owner households, not just legal owners. The 2026 revision back to 2015 and dwelling-linkage exclusions matter. |
| Notater 2026/17, pp. 18–21 | Published 2024 linkage-file totals distinguish dwellings and owners; they do not supply fractional ownership, co-owner tax status or a conversion factor for the 2026 property histogram. Internal linked records are not an open microdataset. |
| 10316 notes, family-statistics definitions and existing legal audit | Statistical couples include cohabitants and some separated couples; they cannot be assigned joint wealth-tax assessment automatically. |

**Recommendation, not implementation approval:** use 10316 for a separate descriptive household-type composition reference (or 10317 for age), retaining the verified net-wealth-decile financial-assets/residual view. No matching primary-housing/debt components by that same wealth rank, or complete property-to-tax-unit mapping, were found within the bounded search. A national-profile model would still require explicit assumptions, not a join of unrelated marginal tables. Human visual/scope choices remain at the final gate.

## Descriptive household-type composition — implemented after approval

`household_composition_reference()` embeds 2024 unconditional means and counts from archived `2026-09-20-feasibility/10316.json`, with table ID, source revision, snapshot and schema version. The original reference remains separate and unchanged. No new download, copied browser asset, runtime dependency or packaging change is needed. The same chart can now show archived 10317 means by main earner's age instead of 10316 household types, via a selector (not an additional default chart). The seven disjoint age groups reconcile to the same 2,616,826 national households; 10317's published means include nonowners and retain up to NOK 100 rounding residuals. The age and type marginal groups cannot be cross-joined into observed tax units. A cross-sectional age comparison is not a lifecycle effect. Both charts remain static through policy changes and never populate the calculator.

The chart shows the 15 disjoint household types in SSB order, **not wealth rank**. The national row (`50`) is retained separately for validation, never stacked or added as a sixteenth group. Type counts sum to 2,616,826. The five plotted components are primary housing, secondary housing, **derived other real assets = real capital − primary − secondary housing**, financial assets and negative total debt. Total real capital is retained for auditing but never stacked alongside its subcomponents. Published net wealth is an independent diamond; its tooltip includes household count and `component sum − published net wealth`. The source's −100/0/+100 NOK discrepancies are preserved, not calibrated away.

These are means over all households in each type, including nonowners, not owner-only or typical actual portfolios. The UI labels the 2024 reference year, student/lone-under-18 exclusions, mixed market/tax valuation and rounding; definitions explain farm dwellings, pension exclusions, full debt and statistical couples versus legal tax units. The chart has no policy or personal-control dependency. It neither populates the calculator nor weights/calibrates the common-profile illustration: nonlinear tax on a group mean is not average tax. Existing decile residual and full curves remain intact.

Validation: extraction checks dimensions/year, metric units, nonmissing means, nonnegative asset/debt amounts, accounting and group counts. Tests compare all selected cells with the archived source, validate signed chart data/schema, reject invalid sources and preserve the original embedded reference. The browser checker confirms this specific chart's canvas and 75 component rows (15 negative debt rows), plus its unchanged specification through 14m→10m→14m. Automated checks do not replace the deferred human review of chart density, labels and mobile layout.

## Remaining data gaps

- Housing tail beyond 30m and explicit original bin-edge definitions.
- Housing, financial assets and debt jointly distributed across economic-net-wealth groups; coarse same-group component means by household type/age are now verified, not a substitute for the missing wealth-rank joint distribution.
- Ownership/tax-unit mapping sufficient for a national receipts forecast; tenure/type cross-tabs and owner–dwelling linkage totals do not identify fractional shares and legal assessment relationships.
- Annual tax-resolution archive, municipality-specific 2026 exceptions, special legal cases and calculator support for mixed-asset debt allocation (core legal principles and housing enactment are now audited).
- February (730m) versus May (830m) threshold-estimate bridge remains unavailable in the bounded investigation above. Different stated baselines are verified; a changed underlying data vintage is not established for these two threshold figures. These are not combined or used as a calibration target here.
