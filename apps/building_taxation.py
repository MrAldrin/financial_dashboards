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


@app.cell(hide_code=True)
def _():
    mo.md("""
    # Norwegian Wealth Tax Calculator
    *An interactive policy sandbox focusing on real estate valuation.*
    """)
    return


@app.cell(hide_code=True)
def _():
    is_couple = mo.ui.switch(label="Is Couple (Double base deduction)?")
    property_type = mo.ui.radio(
        options=["Primary Residence", "Secondary Residence"],
        value="Primary Residence",
        label="Property Type",
    )
    mortgage_debt = mo.ui.number(
        label="Mortgage Debt (NOK)", value=3000000, step=100000
    )
    other_net_wealth = mo.ui.number(
        label="Other Net Wealth (NOK)", value=500000, step=100000
    )
    return is_couple, mortgage_debt, other_net_wealth, property_type


@app.cell(hide_code=True)
def _():
    custom_tier1_rate = mo.ui.slider(
        start=0, stop=100, step=1, value=25, label="Custom Tier 1 Rate (%)"
    )
    custom_tier2_rate = mo.ui.slider(
        start=0, stop=100, step=1, value=70, label="Custom Tier 2 Rate (%)"
    )
    custom_valuation_threshold = mo.ui.number(
        label="Custom Valuation Threshold (NOK)", value=14000000, step=1000000
    )
    custom_base_deduction = mo.ui.number(
        label="Custom Base Deduction (NOK)", value=1700000, step=100000
    )
    custom_tax_rate = mo.ui.slider(
        start=0.0, stop=5.0, step=0.1, value=1.0, label="Custom Standard Tax Rate (%)"
    )
    return (
        custom_base_deduction,
        custom_tax_rate,
        custom_tier1_rate,
        custom_tier2_rate,
        custom_valuation_threshold,
    )


@app.cell(hide_code=True)
def _(
    custom_base_deduction,
    custom_tax_rate,
    custom_tier1_rate,
    custom_tier2_rate,
    custom_valuation_threshold,
    is_couple,
    mortgage_debt,
    other_net_wealth,
    property_type,
):
    mo.vstack(
        [
            mo.md("### Personal Context"),
            mo.hstack([is_couple, property_type]),
            mo.hstack([mortgage_debt, other_net_wealth]),
            mo.md("### Policy Sandbox (Custom Rules)"),
            mo.hstack([custom_tier1_rate, custom_tier2_rate]),
            mo.hstack([custom_valuation_threshold, custom_base_deduction]),
            custom_tax_rate,
        ]
    )
    return


@app.cell(hide_code=True)
def _(
    custom_base_deduction,
    custom_tax_rate,
    custom_tier1_rate,
    custom_tier2_rate,
    custom_valuation_threshold,
    is_couple,
    mortgage_debt,
    other_net_wealth,
    property_type,
):
    def calculate_wealth_tax_df(
        is_couple: bool,
        property_type: str,
        mortgage_debt: float,
        other_net_wealth: float,
        custom_tier1: float,
        custom_tier2: float,
        custom_threshold: float,
        custom_base_ded: float,
        custom_tax_rate: float,
    ) -> pl.DataFrame:
        # 0 to 40M with 500k steps
        market_values = pl.Series("market_value", range(0, 40_500_000, 500_000))
        df = pl.DataFrame([market_values])

        # Current Law Valuation
        if property_type == "Primary Residence":
            df = df.with_columns(
                current_valuation=pl.when(pl.col("market_value") <= 14_000_000)
                .then(pl.col("market_value") * 0.25)
                .otherwise(
                    14_000_000 * 0.25 + (pl.col("market_value") - 14_000_000) * 0.70
                )
            )
        else:
            df = df.with_columns(current_valuation=pl.col("market_value") * 1.00)

        # Custom Law Valuation
        if property_type == "Primary Residence":
            df = df.with_columns(
                custom_valuation=pl.when(pl.col("market_value") <= custom_threshold)
                .then(pl.col("market_value") * (custom_tier1 / 100))
                .otherwise(
                    custom_threshold * (custom_tier1 / 100)
                    + (pl.col("market_value") - custom_threshold) * (custom_tier2 / 100)
                )
            )
        else:
            df = df.with_columns(custom_valuation=pl.col("market_value") * 1.00)

        # Calculate Net Wealth
        df = df.with_columns(
            current_net_wealth=pl.col("current_valuation")
            + other_net_wealth
            - mortgage_debt,
            custom_net_wealth=pl.col("custom_valuation")
            + other_net_wealth
            - mortgage_debt,
        )

        # Apply Deductions
        current_base_deduction = 3_400_000 if is_couple else 1_700_000
        custom_base_ded_actual = custom_base_ded * 2 if is_couple else custom_base_ded

        df = df.with_columns(
            current_taxable_wealth=pl.max_horizontal(
                0, pl.col("current_net_wealth") - current_base_deduction
            ),
            custom_taxable_wealth=pl.max_horizontal(
                0, pl.col("custom_net_wealth") - custom_base_ded_actual
            ),
        )

        # Calculate Tax
        # Current Standard: 1.0% up to 20M, 1.1% above 20M
        df = df.with_columns(
            current_tax=pl.when(pl.col("current_taxable_wealth") <= 20_000_000)
            .then(pl.col("current_taxable_wealth") * 0.01)
            .otherwise(
                20_000_000 * 0.01
                + (pl.col("current_taxable_wealth") - 20_000_000) * 0.011
            ),
            custom_tax=pl.col("custom_taxable_wealth") * (custom_tax_rate / 100),
        )

        return df

    tax_df = calculate_wealth_tax_df(
        is_couple=is_couple.value,
        property_type=property_type.value,
        mortgage_debt=mortgage_debt.value,
        other_net_wealth=other_net_wealth.value,
        custom_tier1=custom_tier1_rate.value,
        custom_tier2=custom_tier2_rate.value,
        custom_threshold=custom_valuation_threshold.value,
        custom_base_ded=custom_base_deduction.value,
        custom_tax_rate=custom_tax_rate.value,
    )
    return (tax_df,)


@app.cell(hide_code=True)
def _(tax_df):
    def create_charts(df: pl.DataFrame):
        # Melt for Valuation Curve
        df_val = df.select(
            ["market_value", "current_valuation", "custom_valuation"]
        ).unpivot(
            index="market_value", variable_name="Scenario", value_name="Taxable Value"
        )
        df_val = df_val.with_columns(
            pl.col("Scenario")
            .str.replace("current_valuation", "Current Law")
            .str.replace("custom_valuation", "Custom Sandbox")
        )

        val_chart = (
            alt.Chart(df_val)
            .mark_line()
            .encode(
                x=alt.X("market_value:Q", title="Real Market Value (NOK)"),
                y=alt.Y("Taxable Value:Q", title="Taxable Value (NOK)"),
                color="Scenario:N",
                tooltip=["market_value", "Taxable Value", "Scenario"],
            )
            .properties(
                width="container", height=350, title="Valuation Curve (Formuesverdi)"
            )
        )

        # Melt for Tax Impact Graph
        df_tax = df.select(["market_value", "current_tax", "custom_tax"]).unpivot(
            index="market_value", variable_name="Scenario", value_name="Annual Tax"
        )
        df_tax = df_tax.with_columns(
            pl.col("Scenario")
            .str.replace("current_tax", "Current Law")
            .str.replace("custom_tax", "Custom Sandbox")
        )

        tax_chart = (
            alt.Chart(df_tax)
            .mark_line()
            .encode(
                x=alt.X("market_value:Q", title="Real Market Value (NOK)"),
                y=alt.Y("Annual Tax:Q", title="Annual Wealth Tax (NOK)"),
                color="Scenario:N",
                tooltip=["market_value", "Annual Tax", "Scenario"],
            )
            .properties(width="container", height=350, title="Wealth Tax Impact")
        )

        return mo.vstack([val_chart, tax_chart])

    charts = create_charts(tax_df)
    charts
    return


if __name__ == "__main__":
    app.run()
