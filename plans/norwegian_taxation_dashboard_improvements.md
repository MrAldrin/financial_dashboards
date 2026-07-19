# Plan: Norwegian Taxation & Wealth Tax Dashboard Improvements

This plan outlines proposed enhancements to the Norwegian Building Taxation & Wealth Tax Dashboard to make it a more engaging, insightful, and educational tool. The goal is to move from a basic calculator to an interactive policy simulator that shows both the personal financial impact and the macro-economic consequences of tax policy changes, grounded in real-world data.

---

## 1. Pillar 1: Realistic Housing Stock & Valuation Data

Currently, the dashboard only plots a hypothetical curve from 0 to 30.5M NOK. We will integrate a statistical model of Norway's actual housing stock to show the macro-level impact of tax changes.

### A. Housing Distribution Model
We will model the distribution of Norway's **2.55 million primary residences** and **330,000 secondary residences** using a log-normal distribution parameterized by Statistics Norway (SSB) data:
- **Median house price:** ~3.8M NOK
- **Mean house price:** ~4.4M NOK
- **Right-skewed tail:** Captured to accurately represent luxury properties in areas like Oslo, Asker, and Bærum.

**Insights Conveyed:**
- **Total Housing Wealth Tax Revenue:** The total annual revenue the state collects from residential property (in billion NOK).
- **Taxpayer Count:** The number and percentage of Norwegian households that actually pay wealth tax on their primary/secondary homes.
- **Average Tax per Household:** The average wealth tax burden on homeowners.

### B. Regional Property Explorer
Introduce a drop-down or selection card with representative property values from different parts of Norway:
- **Oslo Central:** Average home price ~7.5M NOK
- **Bærum (High-income suburb):** Average home price ~9.0M NOK
- **Bergen / Stavanger / Trondheim:** Average home price ~5.0M NOK
- **Innlandet (Regional):** Average home price ~3.0M NOK
- **Custom Value:** Allow the user to input their own estimated home value.

Selecting a region will automatically pre-populate the "Your Property Value" slider, anchoring the policy simulations in regional reality.

---

## 2. Pillar 2: Norwegian State Budget Perspective

To help users put large numbers (like billions of NOK) into perspective, we will integrate key figures from the **2026 Norwegian State Budget (Statsbudsjettet)**:

### A. Core Budget Benchmarks
- **Total State Revenue:** 2,270 billion NOK
- **Total State Expenditures:** 2,201 billion NOK
- **Total Wealth Tax Revenue:** 36.1 billion NOK (with ~35 billion NOK from personal taxpayers)

### B. "What Does this Buy?" (Concrete Equivalents)
When the user modifies the sandbox rules, we will calculate the revenue difference between **Dagens regelverk** (Current rules) and **Din sandkasse** (Your sandbox). We will display this difference in terms of concrete public equivalents:
- **Major Hospitals:** "Equivalent to funding X% of the new **Mjøssykehuset** (budgeted at 18 billion NOK)."
- **Police Force:** "Equivalent to funding the entire **Norwegian Police Force** (driftsbudsjett of 27 billion NOK) for X months."
- **National Defense:** "Equivalent to X% of the yearly **Defense Budget** (112 billion NOK, excluding Ukraine aid)."
- **Public Servants:** "Equivalent to funding the annual salaries of X nurses or teachers (average cost ~650,000 NOK/year)."

---

## 3. Pillar 3: Educational Insights & Policy Mechanics

To make the app intellectually stimulating, we will visualize two of the most hotly debated mechanics in Norwegian wealth taxation:

### A. The "Debt Loophole" (Gjeldsarbitrasje) Visualizer
Norway's tax code has a famous asymmetry: mortgage debt is deducted 1:1 (100%), while primary residences are valued at a steep discount (only 25% up to 14M NOK). This creates a powerful incentive to take on debt to buy property.
- **New Visualization:** A chart or interactive table showing how your tax liability decreases as you increase your mortgage leverage, keeping house value constant.
- **Insight:** Clearly demonstrates why Norwegian households have some of the highest debt-to-income ratios in the OECD.

### B. Progressive Tax Equity (Who Pays?)
- **Lorenz-style Progressivity Curve:** Plot the cumulative share of housing wealth tax paid by housing wealth deciles.
- **Insight:** Shows whether a policy change makes the tax system more progressive (shifting burden to luxury properties) or regressive (raising taxes on middle-class homeowners).

---

## 4. Pillar 4: Premium UI/UX Design

We will restructure the app using a premium dashboard layout using Marimo's columns and cards:

### A. Key Performance Indicator (KPI) Cards
At the top of the dashboard, we will place clean KPI metrics:
1. **Total State Revenue from Housing:** NOK X.X Billion (Sandbox vs. Current)
2. **Net Budget Impact:** `+NOK X.X Million` (Green) or `-NOK X.X Million` (Red)
3. **Your Estimated Tax Bill:** NOK X,XXX (Sandbox vs. Current)

### B. Interactive Control Center
Group the controls logically into collapsible sections or clean sidebars:
- **My Household Portfolio:**
  - Marital status (couple or single)
  - Estimated Property Value (with regional presets)
  - Mortgage Debt
  - Other Taxable Wealth
- **Policy Sandbox Parameters:**
  - Base deduction (Bunnfradrag)
  - Tax rates (Trinn 1 & Trinn 2)
  - Dynamic valuation tiers (allowing the user to add multiple tiers, e.g. 25% up to 10M, 50% up to 20M, 70% above)

---

## 5. Proposed Architecture & Implementation Plan

### Cell-by-Cell Structure:
1. **Setup & Imports:** Import `marimo as mo`, `polars as pl`, `altair as alt`, and define global budget constants.
2. **Data Modeling Cell:** Generate the housing stock distribution (2.55M primary, 330k secondary) using Polars.
3. **UI Input Cell:** Declare sliders, switches, and dropdowns for personal portfolios and tax rules.
4. **Calculations Cell:** Write vectorised Polars expressions to evaluate both personal tax and total state revenues for both scenarios.
5. **UI Rendering Cell:** Structure the layout (KPI Cards -> Input Controls -> Charts -> Budget Perspective).

---

## Progress Tracker

- [ ] Discuss proposals with the user and prioritize features.
- [ ] Create the mock housing stock distribution in Polars.
- [ ] Refactor calculations to compute both personal tax and macro revenue totals.
- [ ] Integrate the State Budget benchmarking and equivalency formulas.
- [ ] Implement the new premium dashboard layout (KPI cards, grouped sliders).
- [ ] Add the "Debt Loophole" interactive analyzer.
- [ ] Run `uv run .github/scripts/build.py` to test WASM build compatibility.
