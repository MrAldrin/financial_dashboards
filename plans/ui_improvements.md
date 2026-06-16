# Plan: UI Improvements for Wealth Tax Sandbox

## Current State Analysis
- The notebook currently uses `mo.ui.number` for all scenario configurations.
- All 5 inputs (tier 1, tier 2, valuation threshold, base deduction, tax rate) are horizontally stacked (`mo.hstack`), which can feel cramped.
- Visual feedback is provided via Altair charts (valuation curve and tax effect), but exact numbers aren't immediately clear without hovering.

## Proposed Improvements

### 1. Upgrade Inputs to Sliders for Percentages
While `SANDBOX_CONFIGS` defines `start` and `stop` values for percentages (`tier1_rate`, `tier2_rate`, `tax_rate`), the UI component used is `mo.ui.number`. 
Changing these to `mo.ui.slider(show_value=True)` will allow users to "scrub" the values and instantly see the charts animate, which is much more engaging for a sandbox.

### 2. Introduce a "Your Property Value" Input & Summary Cards
Currently, "Personlig økonomi" asks for debt and other wealth, but doesn't explicitly calculate the tax for *a specific property value* (it plots the whole spectrum instead). 
- **Idea**: Add a `mo.ui.number` or slider for "Din anslåtte boligverdi" (Your estimated property value).
- **Benefit**: We can use `mo.stat` cards or a clean Markdown summary to show exactly what the user would pay in "Dagens regelverk" vs. the active alternatives. This grounds the abstract curves into a concrete, personal number.

### 3. Layout & Structure Polish
Horizontally stacking 5 inputs per scenario can be extremely cramped.
- **Idea**: Group the parameters logically within each alternative.
  - *Group 1 (Verdsettelse)*: Tier 1 %, Tier 2 %, Threshold
  - *Group 2 (Skatt)*: Base Deduction, Tax Rate %
- Alternatively, we could wrap each scenario in a `mo.ui.accordion` if they want to hide/show specific configurations to save vertical space.

### 4. Data Table for Exact Comparisons
Visual charts are great for the big picture, but a data table is best for precise numbers. 
- **Idea**: Add a `mo.ui.table` below the charts that compares the tax at fixed property intervals (e.g., 5M, 10M, 15M, 20M, 25M) across all active scenarios.

---
## Progress Tracker
- [ ] Discuss proposals with the user and select preferred features.
- [ ] Update `create_scenario_sliders` to use `mo.ui.slider` where appropriate.
- [ ] Implement layout changes (Grouping inputs).
- [ ] Add specific property value input and summary stats.
- [ ] Add data table comparison.
