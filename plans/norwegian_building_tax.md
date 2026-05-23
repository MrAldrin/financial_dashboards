# Plan: Norwegian Wealth Tax Calculator (Property Focus)

This plan outlines the implementation of an interactive policy sandbox for the Norwegian wealth tax, focusing on how real estate contributes to the tax burden across a wide spectrum of property values.

## 1. Rules & Constants (Current Law 2024/2025)

The application will compare a "Custom Sandbox" against these baseline current rules:

### Real Estate Valuation (Formuesverdi)
- **Primary Residence (Primærbolig)**:
    - **Tier 1**: 25% of market value up to NOK 14,000,000.
    - **Tier 2**: 70% of market value above NOK 14,000,000.
- **Secondary Residence (Sekundærbolig)**:
    - Valued at 100% of the estimated market value.

### Wealth & Debt Mechanics
- **Debt Deduction (Gjeldsfradrag)**: Debt (e.g., mortgages) reduces net wealth 1:1 (100% deduction), creating the famous Norwegian "property tax loophole" where highly leveraged primary homes yield negative net wealth.

### Wealth Tax Rates & Deductions
- **Base Deduction (Innslagspunkt)**: NOK 1,700,000 per person (NOK 3,400,000 for couples).
- **Standard Rate**: 1.0% for net wealth between the base deduction and NOK 20 million.
- **Higher Rate**: 1.1% for net wealth above NOK 20 million.

## 2. Proposed Architecture

### UI Elements (The Policy Sandbox)
The user tweaks their personal context and the underlying rules to see the macro-economic impact.

**Personal Context**
- `is_couple`: `mo.ui.switch` (Apply double base deduction).
- `property_type`: `mo.ui.radio` (Primary vs. Secondary residence).
- `mortgage_debt`: `mo.ui.number` (Outstanding loan on the property).
- `other_net_wealth`: `mo.ui.number` (Other taxable assets minus other non-mortgage debt).

**Policy Sandbox (Custom Rules)**
- `custom_tier1_rate`: `mo.ui.slider` (Default 25%)
- `custom_tier2_rate`: `mo.ui.slider` (Default 70%)
- `custom_valuation_threshold`: `mo.ui.number` (Default 14M)
- `custom_base_deduction`: `mo.ui.number` (Default 1.7M)
- `custom_tax_rate`: `mo.ui.slider` (Default 1.0%)

### Data Generation & Calculation Logic
Generate a Polars DataFrame representing a spectrum of property values (e.g., NOK 0 to 40,000,000 with 500k steps).
Calculate two scenarios: **Current Law** and **Custom Law**.

1. **Property Valuation**:
    - *Primary (Current)*: `min(value, 14M) * 0.25 + max(0, value - 14M) * 0.70`
    - *Secondary (Current)*: `value * 1.00`
    - *Custom*: `min(value, custom_threshold) * custom_tier1 + max(0, value - custom_threshold) * custom_tier2`
2. **Wealth Tax Calculation**:
    - Calculate Net Wealth: `Property Valuation + other_net_wealth - mortgage_debt`
    - Subtract the base deduction (1.7M or 3.4M).
    - Apply the tax rates to the remaining taxable wealth.

### Visualizations (Altair)
1. **The Valuation Curve**:
    - **X-axis**: Real Market Value | **Y-axis**: Taxable Value (Formuesverdi)
    - **Lines**: Current Law vs. Custom Sandbox.
2. **The Tax Impact Graph**:
    - **X-axis**: Real Market Value | **Y-axis**: Annual Wealth Tax (NOK)
    - **Lines**: Current Law vs. Custom Sandbox.
    - *Interactive Tooltips*: Hovering over the graph displays exact values.

## 3. Phase 2: Comprehensive Expansions
To make this a truly holistic financial dashboard, these features should be added once the core wealth tax engine is stable:

1. **Marginal Rate Graph**: A chart showing the *effective* tax rate vs the *marginal* tax rate as house prices increase.
2. **The "Debt Loophole" Visualization**: A specific chart showing how increasing your mortgage affects your total wealth tax burden, visualizing the arbitrage between 25% asset valuation and 100% debt deduction.
3. **Unit Testing**: Add a `local_testing/` script using `pytest` to strictly verify the tax math against known Skatteetaten examples.

## 4. Implementation Steps

7. [x] Remove old code from `apps/building_taxation.py`.
8. [x] Create "Personal Context" (including Mortgage/Property Type) and "Policy Sandbox" UI elements.
9. [x] Implement Polars DataFrame generation (0 to 40M).
10. [x] Write vectorised calculation logic for Current vs Custom Law, incorporating debt deductions.
11. [x] Build Altair charts with interactive tooltips.
12. [x] Arrange layout using `mo.vstack/hstack`.

---
**Progress Tracking**
- 2026-05-23: Plan updated to focus exclusively on Wealth Tax.
