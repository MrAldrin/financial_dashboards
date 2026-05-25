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
    MIN_SCENARIOS = 1
    MAX_SCENARIOS = 4
    COLORS = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]
    return COLORS, MAX_SCENARIOS, MIN_SCENARIOS


@app.cell
def _(MAX_SCENARIOS, MIN_SCENARIOS):
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

    add_button, remove_button = create_add_remove_buttons(
        set_visible_count, MIN_SCENARIOS, MAX_SCENARIOS, mo
    )
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
            "label": "Verdsettelse Trinn 1 (%)",
        },
        "tier2_rate": {
            "start": 0.0,
            "stop": 100.0,
            "step": 1.0,
            "label": "Verdsettelse Trinn 2 (%)",
        },
        "valuation_threshold": {
            "value": 10_000_000.0,
            "step": 1_000_000.0,
            "label": "Verdsettelsesgrense (NOK)",
        },
        "base_deduction": {
            "value": 1_900_000.0,
            "step": 100_000.0,
            "label": "Bunnfradrag (NOK)",
        },
        "tax_rate": {
            "start": 0.0,
            "stop": 5.0,
            "step": 0.1,
            "label": "Skatteprosent (%)",
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
            mo.md("### Personlig økonomi"),
            is_couple,
            mo.hstack([mortgage_debt, other_net_wealth]),
            mo.md("### Politisk sandkasse (Egendefinerte regler)"),
            ui_sliders,
        ]
    )
    return (ui_elements,)


@app.cell
def _(
    COLORS,
    MAX_SCENARIOS,
    MIN_SCENARIOS,
    add_button,
    alternatives,
    get_visible_count,
    remove_button,
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
            COLORS,
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
def _(COLORS, tax_df):
    val_chart = create_valuation_chart(tax_df, COLORS, get_chart_domain_and_range)
    tax_chart = create_tax_chart(tax_df, COLORS, get_chart_domain_and_range)

    mo.vstack([val_chart, tax_chart])
    return


@app.cell
def _(alternatives, is_couple, mortgage_debt, other_net_wealth):
    current_df = calculate_wealth_tax_df(
        tier1_rate=25.0,
        tier2_rate=70.0,
        valuation_threshold=14_000_000.0,
        base_deduction=1_900_000.0,
        tax_rate=1.0,
        scenario_name="Dagens regelverk",
        is_couple=is_couple.value,
        mortgage_debt=mortgage_debt.value,
        other_net_wealth=other_net_wealth.value,
    )

    df_alts = build_alternatives(
        alternatives,
        calculate_wealth_tax_df,
        is_couple=is_couple.value,
        mortgage_debt=mortgage_debt.value,
        other_net_wealth=other_net_wealth.value,
    )
    tax_df = pl.concat([current_df] + df_alts)
    return (tax_df,)


@app.function
def calculate_wealth_tax_df(
    tier1_rate: float,
    tier2_rate: float,
    valuation_threshold: float,
    base_deduction: float,
    tax_rate: float,
    scenario_name: str,
    is_couple: bool,
    mortgage_debt: float,
    other_net_wealth: float,
) -> pl.DataFrame:
    market_values = pl.Series("market_value", range(0, 30_500_000, 500_000))
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
        net_wealth=pl.col("valuation") + other_net_wealth - mortgage_debt
    )

    actual_base_ded = base_deduction * 2 if is_couple else base_deduction

    df = df.with_columns(
        taxable_wealth=pl.max_horizontal(0, pl.col("net_wealth") - actual_base_ded)
    )

    if scenario_name == "Dagens regelverk":
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


@app.function
def build_alternatives(alts, calc_fn, is_couple, mortgage_debt, other_net_wealth):
    df_alternatives = []
    for i, _alternative in enumerate(alts):
        kwargs = {key: _alternative[key].value for key in _alternative}
        df = calc_fn(
            **kwargs,
            scenario_name=f"Alternativ {i + 1}",
            is_couple=is_couple,
            mortgage_debt=mortgage_debt,
            other_net_wealth=other_net_wealth,
        )
        df_alternatives.append(df)
    return df_alternatives


@app.function
def get_chart_domain_and_range(df, colors):
    num_alts = df["Scenario"].n_unique() - 1
    domain = ["Dagens regelverk"] + [f"Alternativ {i + 1}" for i in range(num_alts)]
    range_ = ["#000000"] + colors[:num_alts]
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


@app.function
def create_add_remove_buttons(set_visible_count_fn, min_scenarios, max_scenarios, mo):
    add_button = mo.ui.button(
        label="Legg til alternativ",
        on_change=lambda _: set_visible_count_fn(
            lambda count: min(count + 1, max_scenarios)
        ),
    )
    remove_button = mo.ui.button(
        label="Fjern alternativ",
        on_change=lambda _: set_visible_count_fn(
            lambda count: max(count - 1, min_scenarios)
        ),
    )
    return add_button, remove_button


@app.function
def create_scenario_manager(default_values, max_scenarios=4):
    get_scenarios, set_scenarios = mo.state([default_values] * max_scenarios)
    get_visible_count, set_visible_count = mo.state(1)
    return get_scenarios, set_scenarios, get_visible_count, set_visible_count


@app.function
def render_scenario_sliders(scenario_dict, color_index, keys, colors, mo):
    color = colors[color_index % len(colors)]
    rendered_sliders = mo.hstack([scenario_dict[key] for key in keys])
    colored_sliders = mo.vstack([rendered_sliders]).style(
        {
            "border-left": f"4px solid {color}",
            "padding-left": "10px",
            "margin": "10px 0",
        }
    )
    return colored_sliders


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
