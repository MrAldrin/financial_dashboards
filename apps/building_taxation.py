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
    mortgage_debt = mo.ui.number(
        label="Mortgage Debt (NOK)", value=3000000, step=100000
    )
    other_net_wealth = mo.ui.number(
        label="Other Net Wealth (NOK)", value=500000, step=100000
    )
    return is_couple, mortgage_debt, other_net_wealth


@app.cell
def _():
    MIN_SCENARIOS = 1
    MAX_SCENARIOS = 4
    COLORS = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]
    return COLORS, MAX_SCENARIOS, MIN_SCENARIOS


@app.cell
def _(create_add_remove_buttons):
    default_sandbox_vals = {
        "tier1_rate": 25.0,
        "tier2_rate": 70.0,
        "valuation_threshold": 14_000_000.0,
        "base_deduction": 1_900_000.0,
        "tax_rate": 1.0,
    }

    (
        get_scenarios,
        set_scenarios,
        get_visible_count,
        set_visible_count,
    ) = create_scenario_manager(default_sandbox_vals)

    add_button, remove_button = create_add_remove_buttons(set_visible_count)
    return (
        add_button,
        get_scenarios,
        get_visible_count,
        remove_button,
        set_scenarios,
    )


@app.cell
def _(get_scenarios, get_visible_count, set_scenarios):
    scenarios = get_scenarios()
    visible_count = get_visible_count()

    SANDBOX_CONFIGS = {
        "tier1_rate": {
            "start": 0.0,
            "stop": 100.0,
            "step": 1.0,
            "label": "Tier 1 Rate (%)",
        },
        "tier2_rate": {
            "start": 0.0,
            "stop": 100.0,
            "step": 1.0,
            "label": "Tier 2 Rate (%)",
        },
        "valuation_threshold": {
            "value": 14_000_000.0,
            "step": 1_000_000.0,
            "label": "Valuation Threshold (NOK)",
        },
        "base_deduction": {
            "value": 1_900_000.0,
            "step": 100_000.0,
            "label": "Base Deduction (NOK)",
        },
        "tax_rate": {
            "start": 0.0,
            "stop": 5.0,
            "step": 0.1,
            "label": "Standard Tax Rate (%)",
        },
    }

    alternatives = mo.ui.array(
        [
            create_scenario_sliders(
                {
                    key: {**SANDBOX_CONFIGS[key], "value": scenario[key]}
                    for key in SANDBOX_CONFIGS
                },
                color_index=i,
                scenario_setter=set_scenarios,
                mo=mo,
            )
            for i, scenario in enumerate(scenarios[:visible_count])
        ]
    )
    return (alternatives,)


@app.cell
def _(is_couple, mortgage_debt, other_net_wealth, ui_sliders):
    ui_elements = mo.vstack(
        [
            mo.md("### Personal Context"),
            is_couple,
            mo.hstack([mortgage_debt, other_net_wealth]),
            mo.md("### Policy Sandbox (Custom Rules)"),
            ui_sliders,
        ]
    )
    return (ui_elements,)


@app.cell
def _(
    MAX_SCENARIOS,
    MIN_SCENARIOS,
    add_button,
    alternatives,
    get_visible_count,
    remove_button,
    render_scenario_sliders,
):
    ui_sliders = create_slider_ui(
        alternatives,
        lambda d, i, mo: render_scenario_sliders(
            d,
            i,
            [
                "tier1_rate",
                "tier2_rate",
                "valuation_threshold",
                "base_deduction",
                "tax_rate",
            ],
            mo,
        ),
        get_visible_count,
        add_button,
        remove_button,
        MIN_SCENARIOS,
        MAX_SCENARIOS,
        mo,
    )
    return (ui_sliders,)


@app.cell
def _(ui_elements):
    ui_elements
    return


@app.cell
def _(create_charts, tax_df):
    create_charts(tax_df)
    return


@app.cell
def _(alternatives, calculate_wealth_tax_df):
    current_df = calculate_wealth_tax_df(
        tier1_rate=25.0,
        tier2_rate=70.0,
        valuation_threshold=14_000_000.0,
        base_deduction=1_900_000.0,
        tax_rate=1.0,
        scenario_name="Current Law",
    )

    df_alts = build_alternatives(alternatives, calculate_wealth_tax_df)
    tax_df = pl.concat([current_df] + df_alts)
    return (tax_df,)


@app.cell
def _(is_couple, mortgage_debt, other_net_wealth):
    def calculate_wealth_tax_df(
        tier1_rate: float,
        tier2_rate: float,
        valuation_threshold: float,
        base_deduction: float,
        tax_rate: float,
        scenario_name: str,
    ) -> pl.DataFrame:
        market_values = pl.Series("market_value", range(0, 40_500_000, 500_000))
        df = pl.DataFrame([market_values])

        df = df.with_columns(
            valuation=pl.when(pl.col("market_value") <= valuation_threshold)
            .then(pl.col("market_value") * (tier1_rate / 100))
            .otherwise(
                valuation_threshold * (tier1_rate / 100)
                + (pl.col("market_value") - valuation_threshold) * (tier2_rate / 100)
            )
        )

        df = df.with_columns(
            net_wealth=pl.col("valuation")
            + other_net_wealth.value
            - mortgage_debt.value
        )

        actual_base_ded = base_deduction * 2 if is_couple.value else base_deduction

        df = df.with_columns(
            taxable_wealth=pl.max_horizontal(0, pl.col("net_wealth") - actual_base_ded)
        )

        if scenario_name == "Current Law":
            df = df.with_columns(
                tax=pl.when(pl.col("taxable_wealth") <= 20_000_000)
                .then(pl.col("taxable_wealth") * 0.01)
                .otherwise(
                    20_000_000 * 0.01 + (pl.col("taxable_wealth") - 20_000_000) * 0.011
                )
            )
        else:
            df = df.with_columns(tax=pl.col("taxable_wealth") * (tax_rate / 100))

        df = df.with_columns(pl.lit(scenario_name).alias("Scenario"))
        return df

    return (calculate_wealth_tax_df,)


@app.function
def build_alternatives(alts, calc_fn):
    df_alternatives = []
    for i, _alternative in enumerate(alts):
        kwargs = {key: _alternative[key].value for key in _alternative}
        df = calc_fn(**kwargs, scenario_name=f"Alternative {i + 1}")
        df_alternatives.append(df)
    return df_alternatives


@app.cell
def _(COLORS):
    def create_charts(df):
        val_chart = (
            alt.Chart(df)
            .mark_line()
            .encode(
                x=alt.X("market_value:Q", title="Real Market Value (NOK)"),
                y=alt.Y("valuation:Q", title="Taxable Value (NOK)"),
                color=alt.Color(
                    "Scenario:N",
                    scale=alt.Scale(
                        domain=["Current Law"]
                        + [f"Alternative {i + 1}" for i in range(4)],
                        range=["#000000"] + COLORS,
                    ),
                ),
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
                color=alt.Color(
                    "Scenario:N",
                    scale=alt.Scale(
                        domain=["Current Law"]
                        + [f"Alternative {i + 1}" for i in range(4)],
                        range=["#000000"] + COLORS,
                    ),
                ),
                tooltip=["market_value", "tax", "Scenario"],
            )
            .properties(width="container", height=350, title="Wealth Tax Impact")
        )

        return mo.vstack([val_chart, tax_chart])

    return (create_charts,)


@app.cell
def _(MAX_SCENARIOS, MIN_SCENARIOS):
    def create_add_remove_buttons(set_visible_count_fn):
        add_button = mo.ui.button(
            label="Add alternative",
            on_change=lambda _: set_visible_count_fn(
                lambda count: min(count + 1, MAX_SCENARIOS)
            ),
        )
        remove_button = mo.ui.button(
            label="Remove alternative",
            on_change=lambda _: set_visible_count_fn(
                lambda count: max(count - 1, MIN_SCENARIOS)
            ),
        )
        return add_button, remove_button

    return (create_add_remove_buttons,)


@app.function
def create_scenario_manager(default_values, max_scenarios=4):
    get_scenarios, set_scenarios = mo.state([default_values] * max_scenarios)
    get_visible_count, set_visible_count = mo.state(1)
    return get_scenarios, set_scenarios, get_visible_count, set_visible_count


@app.cell
def _(COLORS):
    def render_scenario_sliders(scenario_dict, color_index, keys, mo):
        color = COLORS[color_index % len(COLORS)]
        rendered_sliders = mo.hstack([scenario_dict[key] for key in keys])
        colored_sliders = mo.vstack([rendered_sliders]).style(
            {
                "border-left": f"4px solid {color}",
                "padding-left": "10px",
                "margin": "10px 0",
            }
        )
        return colored_sliders

    return (render_scenario_sliders,)


@app.function
def create_slider_ui(
    alternatives,
    render_fn,
    get_visible_count_fn,
    add_button,
    remove_button,
    min_scen,
    max_scen,
    mo,
):
    left_buttons = []
    right_buttons = []
    if get_visible_count_fn() < max_scen:
        left_buttons.append(add_button)
    if get_visible_count_fn() > min_scen:
        right_buttons.append(remove_button)

    ui_sliders_alternatives = mo.vstack(
        [
            *[
                render_fn(alternative, i, mo)
                for i, alternative in enumerate(alternatives)
            ],
            mo.hstack(
                [
                    mo.hstack(left_buttons) if left_buttons else mo.Html(""),
                    mo.hstack(right_buttons, justify="end")
                    if right_buttons
                    else mo.Html(""),
                ]
            ),
        ]
    )
    return ui_sliders_alternatives


@app.function
def create_scenario_sliders(slider_configs, color_index, scenario_setter, mo):
    slider_dict = mo.ui.dictionary(
        {
            key: mo.ui.number(
                value=cfg["value"],
                step=cfg.get("step", 1),
                label=cfg["label"],
            )
            for key, cfg in slider_configs.items()
        },
        on_change=lambda new_vals: scenario_setter(
            lambda scenarios: [
                (new_vals if i == color_index else s) for i, s in enumerate(scenarios)
            ]
        ),
    )
    return slider_dict


if __name__ == "__main__":
    app.run()
