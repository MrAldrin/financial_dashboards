# Wealth-tax dashboard: autonomous follow-through before human review

## Mandate and relationship to the master plan

The user is travelling and cannot inspect the dashboard. They requested prioritisation and an on-disk plan so agents can complete useful work step by step without intermediate human review.

This is the current execution queue supplementing `plans/wealth_tax_evidence_and_dashboard_research.md`. It replaces the assumption that reaching its last recorded milestone means all useful autonomous work must stop. Earlier completed implementation and investigations remain completed; their evidence limitations remain valid.

This session creates the plan only, not application code. Subsequent agents assigned to execute this plan may implement the bounded tasks below. Do not interpret this as permission for unrelated features, unrestricted research, deployment or a complete tax-return engine.

**Goal:** improve correctness, usability and explanatory modelling before one final human review. Human review is needed for preferences and acceptance, not routine testing, evidence-supported implementation or reversible improvements.

## Non-negotiable boundaries

- Preserve the full-range valuation/base/tax/difference/income curves and existing public-reference views. Do not replace them with selected-point cards.
- Keep one dashboard. New advanced views should be compact/expandable or selectable, not a wall of additional default charts.
- Use public, open sources only. No outreach, paid data, commissioned tables or restricted microdata.
- Preserve immutable snapshots, provenance and source-definition caveats. Observations, derived arithmetic and assumptions must remain distinguishable.
- Never infer a joint population from unrelated marginal averages and call it observed. An assumption-dependent population model is allowed; an unsupported claim of national accuracy is not.
- Keep the current full-owner calculation as a regression baseline. Do not silently change its meaning or relabel it a comprehensive legal calculator.
- No automatic calibration to official revenue figures. Do not present sensitivity scenarios as confidence intervals.
- Do not restart the watched Marimo session; do not use `@app.cell(hide_code=True)`. Preserve WASM/offline operation.
- Follow repository instructions and load relevant Marimo/WASM skills before implementation. Follow the version-control-workflow skill for JJ changes; do not move bookmarks, push or integrate without user instruction.
- When evidence or a preference blocks one subtask, document it and continue independent tasks. Do not repeatedly ask the travelling user to inspect screenshots.

## Why this order

First establish a reproducible baseline and fix objectively testable problems. Next make policy semantics and ownership scenarios trustworthy. Only then extend population modelling: the property-to-tax-unit conversion must be explicit before multiplying household results into a population figure. Additional descriptive views and educational plots come later because they add value but also increase interface density.

The main statistical trap is nonlinear taxation: tax on a group's mean portfolio is not generally the group's mean tax. Published component means constrain a scenario, but do not reveal who simultaneously owns an expensive home, has debt and owns other assets. More sophisticated code cannot remove this evidence limitation.

## Agent operating procedure

1. Read this plan, the master plan's latest progress records, relevant source reports and current code/tests. Check the working copy and do not overwrite other work.
2. Select the first ready task. Record its ID, status and a short intended scope in the tracker before implementation. One coherent task per reviewable change; split a large task into documented substeps.
3. Inspect existing helpers before introducing abstractions. Preserve the offline generator/embedded-reference architecture unless a demonstrated problem requires a change.
4. Implement and validate the task. Fix failures introduced by the task; distinguish pre-existing failures and environmental limits.
5. Append a completion record with files changed, exact checks/results, limitations and the next ready task. Do not mark success from a planned command or export alone.
6. If blocked, record the precise missing evidence or decision and whether a smaller safe subset was delivered. Proceed to another ready task.
7. Do not create optional work just to remain busy. Finish with the consolidated review packet in T8.

## T0 — Re-establish the technical baseline

**Priority:** first. **Depends on:** nothing. **Effort:** small.

- Read `apps/building_taxation.py`, `scripts/build_wealth_reference.py`, `scripts/check_wealth_browser.py` and the five current `tests/test_wealth_*.py` files.
- Run the existing test, lint, Marimo, generated-reference, WASM and browser checks. The previous record reports 23 unit tests passing; verify current results rather than assuming they still hold.
- Record default household/policy inputs and representative baseline outputs for regression comparisons, plus current export size and repeatable browser timing observations.
- Check that legal provenance shown in the app agrees with the archived audit. Distinguish enacted rules from dated official fiscal scenarios.

**Deliverable:** `local_testing/wealth_autonomous_baseline.md` with commands, environment, results and existing issues. Avoid machine-specific timing pass/fail thresholds without a measured basis.

**Acceptance:** baseline is reproducible, or exact environmental blockers are documented. Do not change financial logic to make a failing expectation pass without investigating it.

## T1 — Objective usability, accessibility and interaction hardening

**Priority:** high. **Depends on:** T0. **Effort:** medium; split tests and fixes if needed.

- Extend browser coverage to desktop and narrow mobile widths, initial load, custom controls, preset switching, tier add/remove and return-to-baseline interactions.
- Check unintended page overflow, clipped labels, unreachable controls, keyboard focus and programmatic labels. Charts may use deliberate contained scrolling when shrinking would make them unreadable.
- Fix measured defects with minimal layout changes. Preserve chart order unless required to fix a concrete problem; queue subjective alternatives for final review.
- Make baseline/custom status and preset scope explicit. Existing housing presets reset housing tiers only: label that accurately. If adding a reset-all action, keep it separate and test every control it promises to reset.
- Confirm static reference charts and official fiscal context do not change when policy controls change.
- Measure load/update performance; optimise only demonstrated bottlenecks while preserving readable code and offline packaging.

**Deliverable:** regression checks, targeted app fixes, desktop/mobile screenshots and a concise findings report under `local_testing/`.

**Acceptance:** tested interactions behave consistently; no new browser errors; accessible labels and known limitations documented. Automated accessibility and screenshots are supporting checks, not human acceptance.

## T2 — Bounded legal specification and explicit ownership scenarios

**Priority:** high. **Depends on:** T0; coordinate app edits with T1. **Effort:** medium per substep, not one small patch.

### T2a: executable scope specification

Read `data/wealth/legal_audit_2026.md` and its archived sources. Specify supported full-owner, fractional-owner and qualifying joint-assessment cases in `docs/wealth_tax_supported_scenarios.md`, with worked examples and source references. Check rates/allowances against the annual resolution if a directly accessible official source can be found.

Separate whole-property valuation, ownership allocation, the user's tax unit, other assets, debt and allowance. A selected assessment mode is a user-supplied scenario, not a determination that the user legally qualifies. State unsupported marriage/separation, residence and mixed-asset cases explicitly.

Use a bounded direct-source follow-up: at most one targeted search pass and relevant linked documents. Archive any new sources immutably. If a rule remains ambiguous, exclude that case and continue; do not expand into a municipality-wide legal survey.

### T2b: supported scenario implementation

- Extend the existing `is_couple` handling rather than rebuild it: the current engine already doubles the allowance and upper tax threshold. Verify and clarify qualifying-joint-unit semantics, and add ownership-share scenarios only for cases established in T2a.
- Retain the simplified asset scope; do not add discounted shares/business assets or full statutory debt allocation implicitly.
- Keep whole-home price distinct from the share belonging to the selected tax unit. Apply valuation tiers to the whole property before ownership allocation where the verified rule requires it.
- Label assets/debt/income as belonging to the selected tax unit; avoid double allocation. Explain that summing unrelated co-owners is not joint assessment.
- Preserve the existing default full-owner results. Test fractional ownership, verified joint allowance/band treatment, threshold continuity, zero ownership handling and unsupported/invalid inputs.
- Do not automatically apply personal ownership settings to every national property. Preserve the legacy common-profile illustration and label its mapping, pending the explicit scenario engine in T3.

**Acceptance:** verified worked examples, unchanged legacy defaults and clear eligibility/exclusions. Deliver T2a even if some T2b cases must be deferred.

## T3 — Transparent multi-profile population scenario engine

**Priority:** high educational value. **Depends on:** T0 and T2a; ownership-aware profiles require the relevant T2b support. **Effort:** medium-to-large; execute in substeps.

This is a scenario improvement, not a promise of statistically identified national receipts.

### T3a: modelling contract

Write `docs/wealth_population_scenarios.md` before implementing the engine. Define:

- Property bins, counts, unknown-tail treatment and source vintages.
- Explicit assumed profile mixtures conditional on property bins, including debt and other assets, and ownership/tax-unit mappings where supported.
- Which parameters are published, derived or freely assumed; no invented empirical weights.
- Whether a record represents a property or a tax unit, and how property weight is allocated without double counting properties/co-owners or duplicating allowances.
- Comparison with the existing common-profile illustration, and limitations caused by unobserved correlations.

Retain existing exact bin integration where its assumptions apply. If numerical integration is introduced, document convergence and compare against cases with analytic answers.

### T3b: engine and tested illustrative profiles

- Build a small typed, validated profile representation and deterministic weighted calculation using existing financial helpers.
- Implement a small set of explicitly illustrative mixtures, not group-average households presented as observed taxpayers.
- Use verified aggregate data as plausibility/context checks only where populations and units match. Do not force incompatible sources to reconcile.
- Show how changing debt/asset correlation and ownership assumptions changes results, not merely changes to the home-price tail.
- Test weight normalisation, invalid/missing values, no double counting, identity-policy zero change and equivalence to the current engine when all profiles collapse to its full-owner common profile.
- Keep static official estimates outside the calculation; discrepancies are information, not a target to fit.

### T3c: compact dashboard integration

Add an advanced scenario section with clear assumption summaries, baseline/reform/difference results and sensitivity. Keep the existing simple illustration available. Name alternatives by their assumptions; use “low/high model result” only when the calculated ordering supports it. Never label arbitrary assumptions “likely” or an uncertainty interval “95%”.

**Acceptance:** reproducible outputs, transparent weights/units, meaningful sensitivity, unchanged reference data and no claim of observed representative portfolios or validated national prediction. If evidence does not support empirical default weights, ship labelled illustrative weights rather than fabricate evidence or abandon the entire feature.

## T4 — Additional verified descriptive context

**Priority:** medium. **Depends on:** T0. **Effort:** medium. Independent of T2/T3.

- Add the verified SSB 10317 age-based composition through the existing snapshot/generator pipeline, ideally as a household-type/age selector rather than another full default panel.
- Preserve the current household-type and wealth-decile views. Explain that these are different groupings, not joinable records.
- Verify every selected source value, counts, signed accounting, rounding discrepancies and the national row. Retain year, exclusions, denominator and mixed-valuation explanations.
- Do not convert age means into national tax profiles or claim a lifecycle effect from a cross-section.

**Acceptance:** source-to-generated-data tests, chart schema/browser checks and fixed reference data through policy changes. No live runtime SSB fetches or new notebook dependencies.

## T5 — Compact educational diagnostics

**Priority:** medium, after correctness and scenario work. **Depends on:** T1; use T2 semantics if implemented. **Effort:** medium, split by diagnostic.

- Add an expandable selected-point valuation-to-tax breakdown consistent with the existing full curves. Show market value, included housing value, other assets, debt, taxable base, allowance and tax bands without subtracting an allowance twice.
- Add an optional marginal-tax/slope view using exact piecewise behaviour where possible. Explain units and one-sided behaviour at kinks; avoid noisy finite differences that suggest discontinuities in tax.
- Add an optional debt-versus-home-value tax/difference heatmap if it can reuse the same engine with bounded grid cost. Preserve the main curves and coordinate selected-point inputs.
- Use a compact advanced-view selector or expandable section; do not display all diagnostics by default. No custom widget framework solely for these views.

**Acceptance:** numeric cross-checks against the main engine, breakpoint tests, explicit units, WASM/browser performance checks. Record useful diagnostics even if one proves too costly or redundant; do not make it a blocker for T8.

## T6 — Bounded evidence-gap closure check

**Priority:** low, only when there is a concrete new lead. **Depends on:** reading the prior reports. **Effort:** capped.

- Do not repeat the completed catalogue/web search merely because the user is unavailable.
- Reopen matching wealth-decile housing/debt or official February/May reconciliation only for an identifiable new public source or overlooked direct reference.
- Limit each reopened question to one targeted pass; record sources checked and stop if it adds no evidence.
- Municipality-specific rates, comprehensive special-case support and actual national ownership/tax-unit mapping are not completion requirements for this queue.

**Acceptance:** either a verified, scoped finding or an explicit “not reopened: no new lead”. A documented unresolved data gap is a legitimate result, not a failed implementation task.

## T7 — Integrated verification and maintenance

**Priority:** mandatory after implemented tasks. **Depends on:** completed/skipped T1–T6. **Effort:** medium.

Run and record, checking current command interfaces first:

- `uv run python -m unittest discover -s tests`
- `uv run ruff check .`
- `uv run marimo check apps/building_taxation.py`
- `uv run scripts/build_wealth_reference.py --check`
- `uv run .github/scripts/build.py`
- `uv run scripts/check_wealth_browser.py`

Verify immutable-source hashes using existing manifest conventions. Repeat desktop/mobile checks on the final exported app; test interacting features together, not only isolated helpers. Compare full-owner defaults against T0 and explain intentional differences. Report export size and timing differences with measurement conditions.

Use focused checks after each subtask and the full suite here. Documentation-only tasks need appropriate source/document checks, not gratuitous browser rebuilds. Do not claim a successful export proves browser execution. If browser/environment support is unavailable, clearly mark that validation incomplete.

**Acceptance:** no unexplained regression; all available checks pass; remaining environmental or functional limitations are listed explicitly. Avoid unrelated repository-wide formatting/refactoring.

## T8 — One final human-review packet

**Priority:** mandatory final deliverable. **Depends on:** T7. **Effort:** small.

Create `plans/wealth_tax_human_review.md` with:

- How to open the dashboard and a short suggested walkthrough.
- Before/after summary and desktop/mobile screenshots or links to local artifacts.
- What is implemented, what was intentionally skipped and what evidence remains unavailable.
- A small numbered set of genuine human decisions: default density/order, understandable labels, usefulness of advanced diagnostics and acceptance of the scenario assumptions/presentation.
- Exact validation results and untested aspects.
- Version-control/integration status; no push or integration without instruction.

Update the master plan with a concise completion cross-reference rather than marking unresolved evidence ambitions complete. Stop here for human acceptance unless additional work is explicitly requested.

## Progress tracker

Status vocabulary: pending / in progress / done / blocked / skipped with reason. Record verification separately from implementation.

| ID | Task | Status | Completion evidence / next action |
|---|---|---|---|
| Plan | Prioritised autonomous queue | done | Plan written; no application code changed or checks rerun in this planning session |
| T0 | Baseline | done | [Baseline report](../local_testing/wealth_autonomous_baseline.md): 23 tests, lint/Marimo/reference checks, 3-app export, three browser passes, 69 source hashes; defaults, sizes, timings and legal caveats recorded |
| T1 | Objective usability/accessibility | done | [Findings and screenshots](../local_testing/wealth_t1_findings.md): mobile control wrapping, labelled tier removal, policy status/preset scope; 29 tests, export and desktop/mobile browser checks pass. Human acceptance still pending T8. |
| T2a | Legal scenario specification | done | `docs/wealth_tax_supported_scenarios.md`: archived provisions reread, worked examples and exclusions specified; one annual-resolution search returned no results |
| T2b | Bounded ownership scenarios | done | Whole-property-first ownership, existing joint mode clarified, exact crossings/zero share, explicit full-owner population isolation; 29 tests and expanded WASM browser checks pass |
| T3a | Population modelling contract | pending | Depends on T0/T2a |
| T3b | Multi-profile engine | pending | Depends on T3a and any used ownership support |
| T3c | Advanced scenario UI | pending | Depends on T3b |
| T4 | Age composition reference | pending | Independent after T0 |
| T5 | Educational diagnostics | pending | After T1 and applicable T2 changes; implement separately |
| T6 | New-lead evidence check | pending | Skip if no concrete new lead |
| T7 | Integrated verification | pending | After implementation queue resolves |
| T8 | Human-review packet | pending | Final task |

### Completion log

- T1 — 23 September 2026: updated `apps/building_taxation.py` and `scripts/check_wealth_browser.py`; recorded measurements and desktop/mobile screenshots in `local_testing/wealth_t1_findings.md`. Tested and fixed clipped mobile control rows (page-width-only checks missed them), named the tier-remove buttons and clarified policy baseline/custom state and housing-only preset behavior. Existing curves, reference charts and financial logic remain intact. Verification: 29 unit tests, Ruff, Marimo, generated-reference consistency, all three WASM exports and two final desktop/mobile Chrome browser passes; no captured browser errors. Target exported HTML 225,916 bytes (not a T1-only comparison to T0). Initial canvas times 18.68/20.78s and first desktop preset updates 0.96/0.95s under unthrottled local conditions; see report for mobile timings and limits. Framework numeric-field accessible labels contain HTML markup; comprehensive WCAG/screen-reader review, narrow screens below 390px and offline cold start remain untested. No bookmarks intentionally moved, pushed or integrated. Next ready task: T3a modelling contract; independent T4 remains ready. Final human acceptance stays T8.

- T2b — 21 September 2026: updated `apps/building_taxation.py`, `data/wealth/README.md`, mechanics tests, new `tests/test_wealth_ownership.py` and `scripts/check_wealth_browser.py`. Existing engine/switch now support the T2a bounded shares; whole-home valuation and owned market value remain distinct, debt/assets/income are not allocated twice, and exact onset/upper-band inverses account for ownership including zero. UI explains eligibility, exclusions, enactment and tax-unit versus statistical-household comparisons. Population UI explicitly retains 100% ownership. No new runtime dependency (only standard-library `math.isfinite`), runtime source fetch, session restart or snapshot change.
  - Verification: `uv run python -m unittest discover -s tests` **29 passed** (0.720s); `uv run ruff check .`, `uv run marimo check apps/building_taxation.py`, `uv run scripts/build_wealth_reference.py --check` all passed. Verified all **69 archived SHA-256 hashes**, including stored/uncompressed handbook hashes. `uv run .github/scripts/build.py` exported all three notebooks successfully. Expanded `uv run scripts/check_wealth_browser.py` passed in desktop Chrome repeatedly, final timed run **22.59s** whole-process wall time (more interactions than T0, not a performance regression metric). Exercised 10m reform/reset, 50% individual at 16m = 5,500 NOK, joint 50% = zero, joint 100% = 11,000, zero share, restored defaults, stable official/composition references and population +869.4m unchanged by personal share. No captured browser errors. Target HTML **222,465 bytes** versus T0 212,373; no fresh whole-site size claim.
  - Regression: all seven T0 full-owner representative points preserved; default onset/upper crossing 14m/42m, economic wealth 12.4m, zero tax/differences and all nine population changes zero. Tests cover uneven shares, independent versus joint units, debt/assets/income allocation, fractional threshold continuity and exact grids, invalid/nonfinite inputs and joint upper bands.
  - Test-development limitation: initial browser locator expected spinbuttons; inspected DOM and corrected to Marimo text inputs. Their accessible labels contain HTML markup; broader accessibility/mobile evaluation remains T1, not completed here. Cold disconnected startup and comprehensive special-case law remain untested/excluded. Annual-resolution search gap retained; no municipal or mixed-asset engine added. `jj diff --check` is unsupported by installed JJ; reviewed `jj diff` instead. Stopped after authorised T2; T1 remains pending, T3+ not started. No bookmarks moved, push or integration.

- T2a — 21 September 2026: specified full/fractional individual and qualifying-joint units, whole-property-first allocation, zero-share behavior, worked arithmetic, input validation and population isolation in `docs/wealth_tax_supported_scenarios.md`. Reread archived statutory/agency/handbook provisions; obsolete handbook 10m threshold is not reused. One targeted annual-resolution search returned no results; no new evidence archived, rate-resolution gap retained. No app changes in this substep. Next: authorised T2b (T1 remains pending).

- T0 — 21 September 2026: created `local_testing/wealth_autonomous_baseline.md`; no application/financial-logic changes. All existing checks passed, including three real WASM browser runs (14.19/15.49/14.33 seconds whole-test wall time). Recorded clean export size separately from stale `_site` contents, local/exporter Marimo version mismatch, default and preset numeric outputs, and conservative app provenance versus the enacted-law audit. Full timing conditions, commands, results and untested scope are in the report. No session restart, bookmark movement, push or integration. Next ready task: T1.

- Planning session: reviewed the master plan's execution order/latest progress, the public-data feasibility report and current script/test inventory. Prioritised bounded implementation separately from unresolvable-by-coding evidence gaps. Next: T0. No application changes, fresh tests, source revalidation, commits or deployment performed.
