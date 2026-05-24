# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.23.8",
# ]
# ///

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="full", sql_output="polars")

with app.setup:
    import marimo as mo
    import polars as pl
    import altair as alt


@app.cell
def _():
    mo.md("""
    # Norwegian Wealth Tax Calculator
    *An interactive policy sandbox focusing on real estate valuation.*
    """)
    return


@app.cell
def _():
    is_couple = mo.ui.switch(label="Is Couple (Double base deduction)?")
    mortgage_debt = mo.ui.number(label="Mortgage Debt (NOK)", value=3000000, step=100000)
    other_net_wealth = mo.ui.number(
        label="Other Net Wealth (NOK)", value=500000, step=100000
    )
    return is_couple, mortgage_debt, other_net_wealth


@app.cell
def _():
    custom_tier1_rate = mo.ui.slider(
        start=0, stop=100, step=1, value=25, label="Tier 1 Rate (%)"
    )
    custom_tier2_rate = mo.ui.slider(
        start=0, stop=100, step=1, value=70, label="Tier 2 Rate (%)"
    )
    custom_valuation_threshold = mo.ui.number(
        label="Valuation Threshold (NOK)", value=14000000, step=1000000
    )
    custom_base_deduction = mo.ui.number(
        label="Base Deduction (NOK)", value=1900000, step=100000
    )
    custom_tax_rate = mo.ui.slider(
        start=0.0, stop=5.0, step=0.1, value=1.0, label="Standard Tax Rate (%)"
    )
    return (
        custom_base_deduction,
        custom_tax_rate,
        custom_tier1_rate,
        custom_tier2_rate,
        custom_valuation_threshold,
    )


@app.cell
def _(
    custom_base_deduction,
    custom_tax_rate,
    custom_tier1_rate,
    custom_tier2_rate,
    custom_valuation_threshold,
    is_couple,
    mortgage_debt,
    other_net_wealth,
):
    # Current Law baseline constants
    current_df = calculate_wealth_tax_df(
        is_couple=is_couple.value,
        mortgage_debt=mortgage_debt.value,
        other_net_wealth=other_net_wealth.value,
        tier1_rate=25.0,
        tier2_rate=70.0,
        valuation_threshold=14_000_000.0,
        base_deduction=1_900_000.0,
        tax_rate=1.0,
        scenario_name="Current Law",
    )

    # Custom Sandbox scenario
    custom_df = calculate_wealth_tax_df(
        is_couple=is_couple.value,
        mortgage_debt=mortgage_debt.value,
        other_net_wealth=other_net_wealth.value,
        tier1_rate=custom_tier1_rate.value,
        tier2_rate=custom_tier2_rate.value,
        valuation_threshold=custom_valuation_threshold.value,
        base_deduction=custom_base_deduction.value,
        tax_rate=custom_tax_rate.value,
        scenario_name="Custom Sandbox",
    )

    # Concat for plotting
    tax_df = pl.concat([current_df, custom_df])
    return (tax_df,)


@app.cell
def _(
    custom_base_deduction,
    custom_tax_rate,
    custom_tier1_rate,
    custom_tier2_rate,
    custom_valuation_threshold,
    is_couple,
    mortgage_debt,
    other_net_wealth,
):
    mo.vstack(
        [
            mo.md("### Personal Context"),
            is_couple,
            mo.hstack([mortgage_debt, other_net_wealth]),
            mo.md("### Policy Sandbox"),
            mo.hstack([custom_tier1_rate, custom_tier2_rate]),
            mo.hstack([custom_valuation_threshold, custom_base_deduction]),
            custom_tax_rate,
        ]
    )
    return


@app.cell
def _(tax_df):
    create_charts(tax_df)
    return


@app.function
def create_charts(df: pl.DataFrame):
    val_chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("market_value:Q", title="Real Market Value (NOK)"),
            y=alt.Y("valuation:Q", title="Taxable Value (NOK)"),
            color="Scenario:N",
            tooltip=["market_value", "valuation", "Scenario"],
        )
        .properties(
            width="container", height=350, title="Valuation Curve (Formuesverdi)"
        )
    )

    tax_chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("market_value:Q", title="Real Market Value (NOK)"),
            y=alt.Y("tax:Q", title="Annual Wealth Tax (NOK)"),
            color="Scenario:N",
            tooltip=["market_value", "tax", "Scenario"],
        )
        .properties(width="container", height=350, title="Wealth Tax Impact")
    )

    return mo.vstack([val_chart, tax_chart])


@app.function
def calculate_wealth_tax_df(
    is_couple: bool,
    mortgage_debt: float,
    other_net_wealth: float,
    tier1_rate: float,
    tier2_rate: float,
    valuation_threshold: float,
    base_deduction: float,
    tax_rate: float,
    scenario_name: str,
) -> pl.DataFrame:
    # 0 to 40M with 500k steps
    market_values = pl.Series("market_value", range(0, 30_500_000, 500_000))
    df = pl.DataFrame([market_values])

    # Valuation
    df = df.with_columns(
        valuation=pl.when(pl.col("market_value") <= valuation_threshold)
        .then(pl.col("market_value") * (tier1_rate / 100))
        .otherwise(
            valuation_threshold * (tier1_rate / 100)
            + (pl.col("market_value") - valuation_threshold) * (tier2_rate / 100)
        )
    )

    # Net Wealth
    df = df.with_columns(
        net_wealth=pl.col("valuation") + other_net_wealth - mortgage_debt
    )

    # Base Deduction
    actual_base_ded = base_deduction * 2 if is_couple else base_deduction

    # Taxable Wealth
    df = df.with_columns(
        taxable_wealth=pl.max_horizontal(0, pl.col("net_wealth") - actual_base_ded)
    )

    # Tax Calculation
    if scenario_name == "Current Law":
        # Current Standard: 1.0% up to 20M, 1.1% above 20M
        df = df.with_columns(
            tax=pl.when(pl.col("taxable_wealth") <= 20_000_000)
            .then(pl.col("taxable_wealth") * 0.01)
            .otherwise(
                20_000_000 * 0.01 + (pl.col("taxable_wealth") - 20_000_000) * 0.011
            )
        )
    else:
        df = df.with_columns(tax=pl.col("taxable_wealth") * (tax_rate / 100))

    # Add scenario column
    df = df.with_columns(pl.lit(scenario_name).alias("Scenario"))

    return df


if __name__ == "__main__":
    app.run()
