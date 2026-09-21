# Wealth-tax plans and evidence

## Start here

1. **Execute next:** [Autonomous follow-through](wealth_tax_autonomous_followthrough.md). Prioritised tasks, dependencies, validation and progress tracking while the user cannot perform human review. Start at T0.
2. **Understand the foundation:** [Research and implementation record](wealth_tax_evidence_and_dashboard_research.md). Original objectives, completed milestones, source register and unresolved evidence gaps. Historical sequencing is superseded by the follow-through queue.
3. **Check source definitions:** [Wealth data guide](../data/wealth/README.md), [legal audit](../data/wealth/legal_audit_2026.md), [official-estimate comparison](../data/wealth/official_estimate_reconciliation_2026.md) and [public-data feasibility](../data/wealth/public_data_feasibility_2026.md).

The future human-review packet will be created by T8; it does not exist yet. Implementation completion is not human acceptance or deployment approval.

## Retired planning documents

Removed during the documentation cleanup at the user's request. Their full text remains in version-control history; there is no duplicate archive to maintain. Removal does not mean every proposed feature was implemented.

| Former file | Disposition |
|---|---|
| `dynamic_valuation.md` | Completed dynamic tiers, add/remove controls and tier-based calculation are in `apps/building_taxation.py`; no separate implementation plan needed. |
| `norwegian_building_tax.md` | Core sandbox implemented and substantially evolved. Its mixed-year legal figures and broad debt/couple language are superseded by the legal audit and explicit current model scope, not copied into a new rules guide. Secondary-residence support is not implied by the old checked boxes. |
| `ui_improvements.md` | Selected-home summary and grouped inputs exist. Objective usability work continues in T1; subjective input-style choices remain for review. A fixed-value comparison table remains an optional review candidate, not a completed feature. |
| `norwegian_taxation_dashboard_improvements.md` | Replaced by the evidence-led master plan and follow-through queue. Population scenarios continue in T3, diagnostics in T5. Unverified population counts, regional prices, log-normal parameters and budget equivalents are not retained as facts. |
| `repository_cleanup_and_consolidation.md` | Superseded by this cleanup. Its proposed active master plan and recommendation to copy old tax figures were stale. Current source documentation already exists under `data/wealth/`. |

### Ideas retained without creating another execution backlog

- Fixed-property-value comparison table and percentage sliders: optional usability choices for final review; neither requires replacing the full curves.
- Regional presets, spending equivalents and distributional/progressivity summaries: require appropriate source validation and modelling definitions before any future implementation. No claim that these exist today.
- Secondary-residence policy and municipal property tax: separate scope, not authorised by removing old plans.
- Additional marginal/debt diagnostics: now explicitly covered by the bounded T5 tasks.

## Cleanup progress

- [x] Read all five retired plans and inspect current implementation/test evidence for their core claims.
- [x] Preserve live plans, source reports and immutable evidence; retain unresolved ideas above.
- [x] Remove obsolete plans and update the surviving reference and root navigation.
- [x] Clarify that joint-assessment mechanics already exist and should be validated/extended, not rebuilt.
- [x] Validate all 14 relative Markdown links across the root README and three surviving plan documents; check new/rewritten documents for trailing whitespace and inspect both JJ diffs. Documentation-only changes: application tests and WASM/browser checks were not rerun.
