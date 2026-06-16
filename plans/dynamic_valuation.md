# Plan: Dynamic Tiered Valuation System

## Goal
Replace the "multiple scenario" comparison with a single, highly advanced scenario where the user can dynamically add and remove valuation tiers ("verdsettelsestrinn").

## 1. Architecture: State & Data Structure
Instead of a fixed `default_sandbox_vals`, we will maintain a list of tiers in `mo.state`.

**Data Structure:**
```python
tiers = [
    {"limit": 14_000_000, "rate": 25.0}, # Everything up to 14M is valued at 25%
    {"limit": None, "rate": 70.0}        # Everything above is valued at 70%
]
```

## 2. Dynamic UI Components
- **`render_tier(index, tier_data)`**: A function that returns a UI row with:
    - A `mo.ui.number` for the `rate`.
    - A `mo.ui.number` for the `limit` (only if it's not the final tier).
    - A "Remove" button (if there's more than one tier).
- **"Add Tier" Button**: Appends a new entry to the state with sensible defaults.

## 3. Calculation Logic (Polars)
The `calculate_wealth_tax_df` needs to change from hardcoded logic to a loop-based or conditional-based approach for N tiers.

**New logic approach:**
1. Sort tiers by limit.
2. For each market value, calculate the portion that falls within each tier's range.
3. Multiply each portion by the tier's rate and sum them up.

## 4. Layout
- **Top**: Personal Finance (Debt, Other Wealth).
- **Middle Left**: The Dynamic Tier List (Advanced Valuation).
- **Middle Right**: Global settings (Bunnfradrag, Skatteprosent).
- **Bottom**: The resulting Charts.

---
## Progress Tracker
- [x] Implement `mo.state` for dynamic tiers.
- [x] Create UI functions for adding/removing/rendering tiers.
- [x] Refactor `calculate_wealth_tax_df` for N-tiers.
- [x] Simplify `tax_df` to compare "Current Rules" vs "Your Custom Dynamic Rules".
- [x] Verify Altair charts still work with the new data structure.
