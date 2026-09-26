# Wealth-tax dashboard: final human review

**Ready for acceptance; pre-human checks updated 26 September 2026.** [Execution tracker](wealth_tax_autonomous_followthrough.md) · [Scope/evidence plan](wealth_tax_evidence_and_dashboard_research.md). This is one 2026 Norwegian primary-home wealth-tax **educational sandbox**, not a tax return, observed taxpayer population or national-receipts forecast.

## Open and walk through

- Local exported browser app: `uv run .github/scripts/build.py`, then `python -m http.server -d _site`; open `http://localhost:8000/apps/building_taxation.html`. Or use the normal Marimo development session without restarting a watched session. Do not deploy/integrate merely to review.
- Start at the 14m default: inspect the full-range valuation, unclipped tax-base, tax, reconstructed-home histogram, policy-difference and income-share curves. Change **Boligtrinn: 10 mill.**; the selected 14m, full-owner individual has +18,000 kr annual tax and the *legacy* one-full-owner-per-property illustration shows +869.4m kr. Use **Boligtrinn: 14 mill.** to return to identity (these buttons reset housing tiers only).
- Open **Vis valgt boligs verdsetting, skattebånd og marginal endring** beside the curves: compare the single tax unit's inputs, tax bands and left/right tax slopes at 14m. Try 16m/50% ownership and joint assessment, then restore 100% ownership. The legacy population illustration must *not* inherit the personal share.
- Open **Avansert: antatte eiere og gjeld/formue per bolig** under the legacy illustration. Compare four explicitly assumed populations' reference, sandbox and difference totals for the **same** policy pair, including 25/75 separate co-owners and high-assets versus high-debt expensive properties. Change the assumed >30m tail count; watch model property/tax-unit counts respond. These are not estimates of the number of actual Norwegian taxpayers or confidence bounds.
- Switch **Vis formue etter (SSB 2024)** from household type (10316) to main earner age (10317) and back; compare these *separate* all-household descriptions with the wealth-decile financial-wealth view. They do not feed the tax calculator. The published official fiscal table also stays static when policy changes.

## Before / after and review artifacts

- T0 baseline: full-owner rules and seven recorded representative outputs, 23 unit tests, one full-owner common-profile weighted example, a static 10316 chart. The [T0 baseline](../local_testing/wealth_autonomous_baseline.md) and [T1 usability findings](../local_testing/wealth_t1_findings.md) retain the original reference outputs/screenshots.
- Added bounded fractional/joint-unit clarity and interaction hardening (T1/T2), a documented/tested property-to-tax-unit mixture engine and compact named-assumption comparison (T3), selectable verified 10317 age reference (T4), and selected-point tax-band/one-sided slope diagnostic (T5). The existing complete curves, legacy illustration, wealth-decile context and dated official estimates remain. No source snapshots, official values, new runtime dependencies or live browser data requests changed.
- Historical screenshots: [initial desktop](../local_testing/wealth_t1_desktop.png), [initial mobile](../local_testing/wealth_t1_mobile.png), [final advanced desktop](../local_testing/wealth_t3c_desktop.png), [final advanced mobile](../local_testing/wealth_t3c_mobile.png), [final diagnostic mobile](../local_testing/wealth_t5_mobile.png). Pre-human revalidation captures from the exact final exported WASM, in new names so historical screenshots were not overwritten: [desktop controls](../local_testing/wealth_t7_revalidation_desktop.png), [desktop scenarios](../local_testing/wealth_t7_revalidation_scenarios_desktop.png), [320px controls](../local_testing/wealth_t7_revalidation_320px_controls.png), [360px controls](../local_testing/wealth_t7_revalidation_360px_controls.png), [390px controls](../local_testing/wealth_t7_revalidation_390px_controls.png), [390px diagnostic](../local_testing/wealth_t7_revalidation_390px_diagnostics.png), [390px scenarios](../local_testing/wealth_t7_revalidation_390px_scenarios.png), [390px curves](../local_testing/wealth_t7_revalidation_390px_curves.png). The advanced table scrolls horizontally on mobile to show the three money columns; its first visible columns are assumptions/property counts. Screenshots support, but do not replace, visual or accessibility sign-off.

## What remains intentionally outside scope

- Unknown original housing-bin edges/heights (reconstructed 2026 Ministry chart); >30m count and 40m–cap placement are assumptions (default 1,000 properties in two bins); values over the selected cap are not modelled. For the displayed starting mix, 1,712,400 properties and 1,887,270 **assumed tax units** follow the supplied probabilities; they are **not** the 2,616,826 2024 SSB statistical households.
- No public joint distribution linking home prices, actual ownership fractions, legal tax-unit status, debt and other assets, or matching wealth-decile primary housing/debt breakdown. The two expensive-home sensitivity variants **add** 2m in assets/debt per expensive property and thus change portfolio marginals; they are not isolated, fixed-marginal correlation effects. The 25/75 variant preserves per-property assets/debt but reallocates them across separate owners. No calibration to official revenue estimates or confidence interval; the February −730m vs May −830m published-estimate bridge remains unresolved. T6 evidence search was not reopened absent a concrete new source.
- Age/type means include nonowner households, are separate marginal groupings and cannot be taxed as typical owners. The age cross-section does not establish lifecycle changes. The legal model excludes mixed discounted assets/debt allocation, municipal exceptions, special residence/assessment cases, property tax and behavioural responses; selecting joint assessment does not establish legal eligibility. No additional heatmap was added: it would introduce a two-dimensional compute grid and interface density without a demonstrated need. This is a scope choice, not a benchmarked WASM performance result.
- The final exported app was checked at 320, 360 and 390px; that does not establish acceptable visual density or broader responsive behavior. A scoped programmatic DOM audit of 51 visible/enabled controls found 2 with no detectable accessible name (the Marimo slider thumb and top-bar ellipsis menu), 42 aria-label strings containing literal HTML markup, and `html lang="en"` around Norwegian text. These are Marimo/export-level limitations; no supported app-owned language/name override was found, and the approved scope did not permit a Marimo upgrade or export/runtime patch. No axe-core run, systematic WCAG audit, screen-reader testing or human accessibility acceptance was performed. Cold disconnected startup was tested and is unsupported by current external Pyodide asset loading; evidence follows below. Export success alone is not browser execution.

## Integrated verification (23 September 2026; historical T7 record)

| Check | Observed result |
|---|---|
| `uv run python -m unittest discover -s tests` | **40 passed**, 1.840s on final code (including source values, invalid cases, scenarios and diagnostics) |
| `uv run ruff check .`; `uv run marimo check apps/building_taxation.py` | Both passed |
| `uv run scripts/build_wealth_reference.py --check` | Three embedded references agree with archived sources; original derived artifact unchanged |
| All snapshot manifests | **69** archived SHA-256 hashes match; compressed legal handbook also matches uncompressed hash |
| `uv run .github/scripts/build.py` | All **three** HTML-WASM notebooks/apps exported and index generated |
| `uv run scripts/check_wealth_browser.py` | Passed actual exported Chrome WASM on 1400×1000 desktop and 390×844 mobile, including policy reform/reset, ownership, tail, age selector, diagnostic table, unchanged official/composition references, and no captured page/console errors |
| T0 financial regression | Seven full-owner valuation/base/tax points unchanged. Legacy identity/10m/20m uniform effects = 0 / +869,399,285.714286 / −526,009,821.428571 kr, matching T0 within 0.01 kr |

Final target HTML: **299,187 bytes**, T0 **212,373 bytes** (+86,814). `_site` may include stale build assets, so total directory size is not used. Browser script final complete-process wall **55.85s** versus T0's median **14.33s**, but this run exercises substantially more interactions, not comparable performance evidence. Final unthrottled warm Chrome initial render **13.16s**, first desktop/mobile housing-preset updates **0.96/0.95s**; cache, network and run conditions vary. This does not establish a causal improvement or a universal time threshold. Marimo + Polars + Altair remain the only notebook packages (declared in PEP 723); PyMuPDF and Playwright are offline/test-only. Export *and* actual WASM browser execution passed.

## Pre-human revalidation (26 September 2026)

| Check | Observed result |
|---|---|
| `uv run python -m unittest discover -s tests` | **40 passed** (1.807s) |
| `uv run ruff check .`; `uv run marimo check apps/building_taxation.py` | Both passed; no Marimo diagnostics |
| `uv run scripts/build_wealth_reference.py --check` | Three embedded references and generator-checked source hashes passed |
| Manifest SHA-256 sweep | **69** source-file hashes plus the compressed legal handbook's uncompressed hash passed |
| `uv run .github/scripts/build.py` | Final rerun after the previously interrupted invocation exported all three notebooks/apps; index generated; wealth HTML **293,088 bytes** |
| `uv run scripts/check_wealth_browser.py` | Against the final export, the first run reported `The following error occurred while loading polars: Failed to fetch`; an unchanged retry passed actual WASM on desktop 1400×1000 and mobile **320×844, 360×844, 390×844**, with no captured page/console errors. The retry checked document overflow, visibility and viewport bounds of visible number inputs, increment/decrement controls, slider, switch, presets, tier controls and reference selector; existing policy/ownership/tail/age/diagnostic/reference regressions still passed. This run-to-run failure indicates external runtime/package fetch variability; it was not reproduced on retry. |
| Unique revalidation screenshots | Eight views of the final exported WASM were saved and intentionally force-tracked despite the local `local_testing/*` ignore rule; none overwrote historical screenshots. See links above. |
| `uv run scripts/check_wealth_accessibility.py` | Scoped audit covered **51** visible/enabled controls and reported 2 unnamed controls, 42 literal-HTML aria-labels and `lang="en"`; keyboard Tab reached tier-add in 21 presses, Enter added a tier, Shift+Tab/Enter removed it. This is an automated diagnostic, **not** an accessibility pass or WCAG certification. |
| Cold disconnected browser probe | Fresh context with no warmed cache/storage, service workers blocked, and all off-origin requests intercepted before navigation. Local exported HTML/assets served (**212** requests); off-origin `wasm.marimo.app/pyodide-lock.json` and jsDelivr Pyodide stdlib/wasm/module (**4** requests) failed, so the dashboard **did not cold-start offline**. No service worker or offline redesign added. |

The responsive defect reproduced before the edit was the slider's increment/decrement buttons partially outside a 320px viewport while page width stayed at 320px. Setting the existing slider's supported `full_width=True` puts its label above the control; viewport-bound assertions now pass at all three widths. No formulas, defaults, curves or reference data changed.

No built-in `lang` setting is exposed in the installed Marimo app configuration; fixing document language, malformed widget names and the unnamed framework toolbar/slider would require a framework or export/runtime-level change. These are deferred for human review, per the approved scope. The cold-offline result likewise remains an external-asset limitation. Local static files are available, but Pyodide cannot initialize when the browser has no external network.

## Decisions for the human reviewer

1. Is the default chart order/density readable on desktop and the 320/360/390px mobile views while preserving the full curves? Is contained horizontal scrolling of advanced tables acceptable?
2. Are the Norwegian labels, policy preset scope, distinction between a personal tax unit, reconstructed properties, assumed tax units and SSB households, and the difference sign understandable?
3. Is the selected-point breakdown/one-sided marginal explanation useful as an expandable diagnostic? Would a debt–price heatmap clarify enough to justify another plot and browser computation?
4. Are the explicitly hypothetical mixture weights, debt/assets variants and unknown-tail warnings appropriate as an educational illustration, or should the advanced section be hidden/adjusted by default?

## Version control and stopping point

A reviewable JJ stack above the older `dev` bookmark contains T3a/T3b, T3c, T4, T5 and UI polish plus this final packet; `main` is separate and user-managed. After this documentation change the agent leaves an empty working change. No bookmark moved, push, merge or deployment performed. **Stop for human acceptance and integration instructions.**

## Progress

- [x] T7 integrated verification and final exported-browser screenshots.
- [x] T8 consolidated review packet and master-plan cross-reference.
- [ ] Human acceptance of presentation, assumptions and optional diagnostic scope; integration remains user-controlled.
