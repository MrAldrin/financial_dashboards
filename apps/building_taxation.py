import marimo

__generated_with = "0.23.9"
app = marimo.App(width="full", sql_output="polars")

with app.setup:
    import marimo as mo
    import polars as pl
    import altair as alt


@app.cell
def _():
    mo.md("""
    # Norsk formueskattkalkulator
    *En interaktiv politisk sandkasse med fokus på verdivurdering av eiendom.*
    """)
    return


@app.cell
def _():
    is_couple = mo.ui.switch(label="Ektepar (Dobbelt bunnfradrag)?")
    mortgage_debt = mo.ui.number(label="Gjeld (NOK)", value=3000000, step=100000)
    other_net_wealth = mo.ui.number(
        label="Annen nettoformue (NOK)", value=500000, step=100000
    )
    return is_couple, mortgage_debt, other_net_wealth


@app.cell
def _():
    COLORS = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]
    get_tiers, set_tiers = mo.state(
        [
            {"limit": 12_000_000, "rate": 30.0},
            {"limit": None, "rate": 75.0},
        ]
    )
    base_deduction = mo.ui.number(
        label="Bunnfradrag (NOK)", value=1_900_000, step=100_000
    )
    tax_rate_ui = mo.ui.number(
        label="Skatteprosent (%)", value=1.0, step=0.1
    )
    return COLORS, base_deduction, get_tiers, set_tiers, tax_rate_ui


@app.cell
def _(get_tiers, set_tiers):
    def add_tier():
        current = get_tiers()
        last_limit = 0
        for t in current:
            if t["limit"] is not None:
                last_limit = max(last_limit, t["limit"])
        new_limit = last_limit + 5_000_000
        new_tier = {"limit": new_limit, "rate": 50.0}
        new_tiers = []
        inserted = False
        for t in current:
            if t["limit"] is None and not inserted:
                new_tiers.append(new_tier)
                inserted = True
            new_tiers.append(t)
        set_tiers(new_tiers)

    def remove_tier(index):
        current = get_tiers()
        if len(current) > 1:
            new_tiers = [t for i, t in enumerate(current) if i != index]
            set_tiers(new_tiers)

    def update_tier(index, key, value):
        current = get_tiers()
        new_tiers = list(current)
        new_tiers[index] = {**new_tiers[index], key: value}
        set_tiers(new_tiers)

    return add_tier, remove_tier, update_tier


@app.cell
def _(add_tier, get_tiers, remove_tier, update_tier):
    current_tiers = get_tiers()
    tier_rows = []
    for i, tier in enumerate(current_tiers):
        is_last = tier["limit"] is None
        rate_input = mo.ui.number(
            value=tier["rate"],
            label=f"Sats % (Trinn {i+1})",
            on_change=lambda v, idx=i: update_tier(idx, "rate", v),
        )
        inputs = [rate_input]
        if not is_last:
            limit_input = mo.ui.number(
                value=tier["limit"],
                label=f"Grense NOK (Trinn {i+1})",
                step=1_000_000,
                on_change=lambda v, idx=i: update_tier(idx, "limit", v),
            )
            inputs.append(limit_input)
        else:
            inputs.append(
                mo.md(f"Alt over forrige grense").style({"padding-top": "25px"})
            )
        if not is_last:
            remove_btn = mo.ui.button(
                label="✖", on_change=lambda _, idx=i: remove_tier(idx), kind="neutral"
            )
            inputs.append(remove_btn)
        tier_rows.append(mo.hstack(inputs, justify="start", align="center"))
    add_btn = mo.ui.button(
        label="Legg til verdsettelsesgrense", on_change=lambda _: add_tier()
    )
    valuation_ui = mo.vstack(
        [mo.md("#### Verdsettelsestrinn:"), *tier_rows, add_btn]
    )
    return (valuation_ui,)


@app.cell
def _(
    base_deduction,
    is_couple,
    mortgage_debt,
    other_net_wealth,
    tax_rate_ui,
    valuation_ui,
):
    ui_elements = mo.vstack(
        [
            mo.md("### Personlig økonomi"),
            is_couple,
            mo.hstack([mortgage_debt, other_net_wealth]),
            mo.md("### Politisk sandkasse (Egendefinerte regler)"),
            base_deduction,
            tax_rate_ui,
            valuation_ui,
        ]
    )
    return (ui_elements,)


@app.cell
def _(ui_elements):
    ui_elements
    return


@app.cell
def _(COLORS, tax_df):
    val_chart = create_valuation_chart(tax_df, COLORS, get_chart_domain_and_range)
    tax_chart = create_tax_chart(tax_df, COLORS, get_chart_domain_and_range)

    mo.vstack([val_chart, tax_chart])
    return


@app.cell
def _(
    base_deduction,
    get_tiers,
    is_couple,
    mortgage_debt,
    other_net_wealth,
    tax_rate_ui,
):
    current_df = calculate_wealth_tax_df(
        tiers=[{"limit": 14_000_000, "rate": 25.0}, {"limit": None, "rate": 70.0}],
        base_deduction=1_900_000.0,
        tax_rate=1.0,
        scenario_name="Dagens regelverk",
        is_couple=is_couple.value,
        mortgage_debt=mortgage_debt.value,
        other_net_wealth=other_net_wealth.value,
    )

    custom_df = calculate_wealth_tax_df(
        tiers=get_tiers(),
        base_deduction=base_deduction.value,
        tax_rate=tax_rate_ui.value,
        scenario_name="Din sandkasse",
        is_couple=is_couple.value,
        mortgage_debt=mortgage_debt.value,
        other_net_wealth=other_net_wealth.value,
    )
    tax_df = pl.concat([current_df, custom_df])
    return (tax_df,)


@app.function
def calculate_wealth_tax_df(
    tiers: list[dict],
    base_deduction: float,
    tax_rate: float,
    scenario_name: str,
    is_couple: bool,
    mortgage_debt: float,
    other_net_wealth: float,
) -> pl.DataFrame:
    df = pl.DataFrame({"market_value": range(0, 30_500_000, 500_000)})
    sorted_tiers = sorted(
        tiers, key=lambda x: x["limit"] if x["limit"] is not None else float("inf")
    )
    valuation_expr = pl.lit(0.0)
    prev_limit = 0.0
    for tier in sorted_tiers:
        limit = tier["limit"] if tier["limit"] is not None else float("inf")
        rate = tier.get("rate", 0.0) / 100
        portion = pl.when(pl.col("market_value") > prev_limit).then(
            pl.min_horizontal(pl.col("market_value"), limit) - prev_limit
        ).otherwise(0.0)
        valuation_expr += portion * rate
        prev_limit = limit
    df = df.with_columns(valuation=valuation_expr)
    df = df.with_columns(
        net_wealth=pl.col("valuation") + other_net_wealth - mortgage_debt
    )
    actual_base_ded = base_deduction * 2 if is_couple else base_deduction
    df = df.with_columns(
        taxable_wealth=pl.max_horizontal(0, pl.col("net_wealth") - actual_base_ded)
    )
    df = df.with_columns(
        tax=pl.col("taxable_wealth") * (tax_rate / 100),
        Scenario=pl.lit(scenario_name),
    )
    return df


@app.function
def get_chart_domain_and_range(df, colors):
    domain = ["Dagens regelverk", "Din sandkasse"]
    range_ = ["#000000", colors[0]]
    return domain, range_


@app.function
def create_valuation_chart(df, colors, get_chart_domain_and_range_fn):
    domain, range_ = get_chart_domain_and_range_fn(df, colors)
    return (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("market_value:Q", title="Reell markedsverdi (NOK)"),
            y=alt.Y("valuation:Q", title="Formuesverdi (NOK)"),
            color=alt.Color(
                "Scenario:N",
                scale=alt.Scale(domain=domain, range=range_),
            ),
            tooltip=["market_value", "valuation", "Scenario"],
        )
        .properties(
            width="container", height=350, title="Verdsettelseskurve (Formuesverdi)"
        )
    )


@app.function
def create_tax_chart(df, colors, get_chart_domain_and_range_fn):
    domain, range_ = get_chart_domain_and_range_fn(df, colors)
    return (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("market_value:Q", title="Reell markedsverdi (NOK)"),
            y=alt.Y("tax:Q", title="Årlig formuesskatt (NOK)"),
            color=alt.Color(
                "Scenario:N",
                scale=alt.Scale(domain=domain, range=range_),
            ),
            tooltip=["market_value", "tax", "Scenario"],
        )
        .properties(width="container", height=350, title="Formuesskatteffekt")
    )


if __name__ == "__main__":
    app.run()
