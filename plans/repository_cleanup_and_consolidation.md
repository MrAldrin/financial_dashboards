# Plan: Repository Cleanup and Plan Consolidation

This plan outlines the steps to clean up the `plans/` directory, create a new `docs/` directory for static reference materials (like tax laws), and consolidate overlapping/completed plans.

## 1. Analysis of Existing Documents & Implementation Status

We have analyzed the current codebase (`apps/building_taxation.py`) and verified which parts of the four files in the `plans/` folder are already implemented:

### A. [plans/dynamic_valuation.md](file:///home/hsa/projects/financial_dashboards/plans/dynamic_valuation.md)
* **Status:** **100% Implemented**
* **Evidence in Code:**
  - `mo.state` is used to manage dynamic tiers (`get_tiers`, `set_tiers`).
  - Dynamic UI functions (`add_tier`, `remove_tier`, `update_tier`, `valuation_ui`) are fully present in `apps/building_taxation.py`.
  - Calculation logic in `calculate_wealth_tax_df` sorted the tiers and dynamically evaluated the custom rules using Polars.

### B. [plans/norwegian_building_tax.md](file:///home/hsa/projects/financial_dashboards/plans/norwegian_building_tax.md)
* **Status:** **100% Implemented (Rules & Core Sandbox)**
* **Evidence in Code:**
  - Personal context UI elements (Couple status, mortgage debt, other net wealth inputs) are active.
  - Wealth and debt mechanics (e.g. 100% mortgage debt deduction) are implemented inside the Polars tax calculations.
  - Valuation curves and tax impact graphs are built using Altair with hover tooltips.
* **Reference Content:** The first section of this document contains valuable documentation of the actual Norwegian tax laws (2024/2025). This is static reference material rather than active plan steps.

### C. [plans/ui_improvements.md](file:///home/hsa/projects/financial_dashboards/plans/ui_improvements.md)
* **Status:** **Pending / Superceded**
* **Analysis:** Most of the suggestions (using sliders, grouping inputs, personal summary cards) are subsumed and expanded by the new master plan: [plans/norwegian_taxation_dashboard_improvements.md](file:///home/hsa/projects/financial_dashboards/plans/norwegian_taxation_dashboard_improvements.md).
* **Missing Feature:** The suggestion to add a comparison table comparing tax rates at fixed property intervals (5M, 10M, 15M, etc.) is still very valuable and should be merged into the active master plan.

### D. [plans/norwegian_taxation_dashboard_improvements.md](file:///home/hsa/projects/financial_dashboards/plans/norwegian_taxation_dashboard_improvements.md)
* **Status:** **Active Master Plan**
* **Analysis:** This is the latest and most relevant roadmap. It expands the sandbox with log-normal housing stock distributions, Norwegian State Budget comparisons, the "Debt Loophole" interactive visualizer, and a premium card layout.

---

## 2. Proposed Cleanup Strategy

To clean up the repository, we propose the following structure:

1. **Create a `docs/` Directory:** A directory for static reference docs, guidelines, and tax law summaries.
2. **Move Tax Reference Info:** Copy the tax law rules from `plans/norwegian_building_tax.md` to `docs/norwegian_wealth_tax_rules.md`.
3. **Consolidate Active Plans:** Update `plans/norwegian_taxation_dashboard_improvements.md` to include the *Fixed Intervals Data Table* feature from `ui_improvements.md`.
4. **Clean up `plans/`:** Remove completed/obsolete plans from the directory (either delete them or move them to a `docs/archived_plans/` folder).

### Target Directory Structure:
```text
financial_dashboards/
├── apps/
│   └── building_taxation.py
├── docs/                             <-- New folder for reference docs
│   ├── norwegian_wealth_tax_rules.md <-- Tax rules reference sheet
│   └── archived_plans/               <-- Optional: archive folder for old plans
│       ├── dynamic_valuation.md
│       └── ui_improvements.md
└── plans/
    ├── norwegian_taxation_dashboard_improvements.md <-- Master Plan (updated)
    └── repository_cleanup_and_consolidation.md     <-- This plan
```

---

## 3. Implementation Steps

1. Create the `docs/` and `docs/archived_plans/` directories.
2. Extract the Norwegian tax laws section from `plans/norwegian_building_tax.md` and save it to `docs/norwegian_wealth_tax_rules.md`.
3. Append the "Fixed Property Value Comparison Table" task from `ui_improvements.md` to the bottom of the master plan `plans/norwegian_taxation_dashboard_improvements.md`.
4. Move `plans/dynamic_valuation.md`, `plans/norwegian_building_tax.md`, and `plans/ui_improvements.md` to the `docs/archived_plans/` directory.
5. Verify the repository build integrity by running the WASM build script (`uv run .github/scripts/build.py`).

---

## Progress Tracker

- [ ] Create `docs/` and `docs/archived_plans/` directories
- [ ] Create `docs/norwegian_wealth_tax_rules.md`
- [ ] Update `plans/norwegian_taxation_dashboard_improvements.md` with the comparison table task
- [ ] Move completed plans to `docs/archived_plans/`
- [ ] Run WASM local build to check compatibility
