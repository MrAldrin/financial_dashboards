# /// script
# requires-python = ">=3.13"
# dependencies = ["marimo>=0.23.9", "polars>=1.36", "altair>=6"]
# ///

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
    # Bolig, formue og skatt — utforsk samspillet
    **Modellberegning, ikke en skattemelding.** Hele primærboligen eies av én
    skatteenhet (én person eller kvalifisert fellesfastsetting). Andre eiendeler
    er bankinnskudd / eiendeler uten verdsettingsrabatt. Gjeld trekkes fra én gang.
    Aksjer med rabatt, delt eierskap og kommunale særregler er ikke modellert.

    Referanse: publiserte [2026-satser fra Skatteetaten](https://www.skatteetaten.no/satser/formuesskatt/),
    14 mill. boliggrense, 25/70 % verdsettelse, 1,9 mill. fradrag,
    1/1,1 % skatt og øvre innslag 21,5 mill. Dette er ikke en full juridisk regelmotor.
    """)
    return


@app.cell
def _():
    is_couple = mo.ui.switch(
        label="Fellesfastsetting (doble personlige innslag, ikke boliggrensen)"
    )
    mortgage_debt = mo.ui.number(
        label="Samlet gjeld (NOK)", start=0, value=1_600_000, step=100_000
    )
    other_net_wealth = mo.ui.number(
        label="Andre eiendeler uten rabatt, før gjeld (NOK)",
        start=0,
        value=0,
        step=100_000,
    )
    selected_home = mo.ui.slider(
        start=0,
        stop=100_000_000,
        step=100_000,
        value=14_000_000,
        show_value=True,
        include_input=True,
        label="Valgt boligverdi (NOK)",
    )
    annual_income = mo.ui.number(
        start=0,
        value=800_000,
        step=50_000,
        label="Årlig bruttoinntekt (NOK, selvvalgt eksempel)",
    )
    chart_max = mo.ui.number(
        start=20_000_000,
        stop=200_000_000,
        value=60_000_000,
        step=10_000_000,
        label="Kurvenes øvre boligverdi (NOK)",
    )
    return (
        annual_income,
        chart_max,
        is_couple,
        mortgage_debt,
        other_net_wealth,
        selected_home,
    )


@app.cell
def _():
    get_tiers, set_tiers = mo.state(
        [
            {"limit": 14_000_000, "rate": 25.0},
            {"limit": None, "rate": 70.0},
        ]
    )
    base_deduction = mo.ui.number(
        label="Bunnfradrag per person (NOK)",
        start=0,
        stop=21_500_000,
        value=1_900_000,
        step=100_000,
    )
    tax_rate_ui = mo.ui.number(
        label="Ordinær skattesats (%)", start=0, stop=10, value=1.0, step=0.1
    )
    upper_rate_ui = mo.ui.number(
        label="Øvre skattesats (%)", start=0, stop=10, value=1.1, step=0.1
    )
    return base_deduction, get_tiers, set_tiers, tax_rate_ui, upper_rate_ui


@app.cell
def _(get_tiers, set_tiers):
    def add_tier() -> None:
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

    def remove_tier(index: int) -> None:
        current = get_tiers()
        if len(current) > 1:
            new_tiers = [t for i, t in enumerate(current) if i != index]
            set_tiers(new_tiers)

    def update_tier(index: int, key: str, value: float) -> None:
        current = get_tiers()
        new_tiers = list(current)
        new_tiers[index] = {**new_tiers[index], key: value}
        set_tiers(new_tiers)

    return add_tier, remove_tier, update_tier


@app.cell
def _(add_tier, get_tiers, remove_tier, set_tiers, update_tier):
    current_tiers = get_tiers()
    tier_rows = []
    for i, tier in enumerate(current_tiers):
        is_last = tier["limit"] is None
        rate_input = mo.ui.number(
            value=tier["rate"],
            start=0,
            stop=100,
            label=f"Andel med i formuen, % (trinn {i + 1})",
            on_change=lambda v, idx=i: update_tier(idx, "rate", v),
        )
        inputs = [rate_input]
        if not is_last:
            limit_input = mo.ui.number(
                value=tier["limit"],
                start=1,
                label=f"Grense NOK (Trinn {i + 1})",
                step=1_000_000,
                on_change=lambda v, idx=i: update_tier(idx, "limit", v),
            )
            inputs.append(limit_input)
        else:
            inputs.append(
                mo.md("Alt over forrige grense").style({"padding-top": "25px"})
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
    tier_presets = mo.hstack(
        [
            mo.ui.button(
                label=f"Boligtrinn: {limit} mill.",
                on_change=lambda _, limit=limit: set_tiers(
                    [
                        {"limit": limit * 1_000_000, "rate": 25.0},
                        {"limit": None, "rate": 70.0},
                    ]
                ),
            )
            for limit in (10, 14, 20)
        ],
        justify="start",
    )
    valuation_ui = mo.vstack(
        [
            mo.md("#### Verdsettelsestrinn (sorteres etter grense):"),
            tier_presets,
            *tier_rows,
            add_btn,
        ]
    )
    return (valuation_ui,)


@app.cell
def _(
    annual_income,
    base_deduction,
    chart_max,
    is_couple,
    mortgage_debt,
    other_net_wealth,
    selected_home,
    tax_rate_ui,
    upper_rate_ui,
    valuation_ui,
):
    ui_elements = mo.vstack(
        [
            mo.md("### Personlig økonomi"),
            is_couple,
            mo.hstack([mortgage_debt, other_net_wealth, annual_income]),
            selected_home,
            mo.md("### Politisk sandkasse — sammenlignet med fast 2026-referanse"),
            mo.hstack([base_deduction, tax_rate_ui, upper_rate_ui]),
            valuation_ui,
            chart_max,
            mo.md(
                "25 % med i formuen betyr 75 % rabatt. En boliggrense lager en knekk, "
                "ikke et hopp. Inntekt påvirker prosentbelastningen, ikke skatten i kroner. "
                "Gjeld og andre eiendeler holdes faste langs hele kurven. "
                "Standardeksemplet har skattestart og boliggrense ved 14 mill."
            ),
        ]
    )
    return (ui_elements,)


@app.cell
def _(ui_elements):
    ui_elements
    return


@app.cell
def _(
    annual_income,
    base_deduction,
    chart_max,
    get_tiers,
    is_couple,
    mortgage_debt,
    other_net_wealth,
    selected_home,
    tax_rate_ui,
    upper_rate_ui,
):
    tier_limits = [tier["limit"] for tier in get_tiers() if tier["limit"] is not None]
    mo.stop(
        len(tier_limits) != len(set(tier_limits)),
        mo.md("**Bruk ulike grenser for hvert trinn.**"),
    )
    curve_max = max(chart_max.value, selected_home.value, *tier_limits, 14_000_000)
    shared_inputs = dict(
        is_couple=is_couple.value,
        mortgage_debt=mortgage_debt.value,
        other_net_wealth=other_net_wealth.value,
        annual_income=annual_income.value,
        max_value=curve_max,
        selected_value=selected_home.value,
    )
    policy_inputs = [
        dict(
            tiers=[{"limit": 14_000_000, "rate": 25.0}, {"limit": None, "rate": 70.0}],
            base_deduction=1_900_000,
            tax_rate=1.0,
            upper_tax_rate=1.1,
            scenario_name="2026-referanse",
        ),
        dict(
            tiers=get_tiers(),
            base_deduction=base_deduction.value,
            tax_rate=tax_rate_ui.value,
            upper_tax_rate=upper_rate_ui.value,
            scenario_name="Din sandkasse",
        ),
    ]
    preliminary = [
        calculate_wealth_tax_df(**policy, **shared_inputs) for policy in policy_inputs
    ]
    shared_grid = sorted(set(pl.concat(preliminary)["market_value"].to_list()))
    scenario_frames = [
        calculate_wealth_tax_df(**policy, **shared_inputs, extra_values=shared_grid)
        for policy in policy_inputs
    ]
    tax_df = pl.concat(scenario_frames)
    difference_df = (
        scenario_frames[1]
        .select("market_value", "tax")
        .with_columns(difference=pl.col("tax") - scenario_frames[0]["tax"])
    )
    marker_rows = []
    marker_notes = []
    for policy in policy_inputs:
        for boundary_tier in policy["tiers"]:
            if boundary_tier["limit"] is not None:
                marker_rows.append(
                    dict(
                        market_value=float(boundary_tier["limit"]),
                        Scenario=policy["scenario_name"],
                        kind="Boligtrinn",
                    )
                )
        for kind, target in [
            ("Skattestart", policy["base_deduction"]),
            ("Øvre skattebånd", 21_500_000),
        ]:
            crossing = home_value_at_tax_wealth(
                policy["tiers"],
                target * (2 if is_couple.value else 1)
                - other_net_wealth.value
                + mortgage_debt.value,
            )
            if crossing is not None and crossing <= curve_max:
                marker_rows.append(
                    dict(
                        market_value=crossing,
                        Scenario=policy["scenario_name"],
                        kind=kind,
                    )
                )
            note = (
                "aldri nådd"
                if crossing is None
                else "nådd allerede ved boligverdi 0"
                if crossing == 0
                else f"{crossing / 1_000_000:.3f} mill. NOK"
                + (" (utenfor kurven)" if crossing > curve_max else "")
            )
            marker_notes.append(f"{policy['scenario_name']} — {kind.lower()}: {note}")
    markers_df = pl.DataFrame(marker_rows)
    return (
        curve_max,
        difference_df,
        marker_notes,
        markers_df,
        policy_inputs,
        shared_inputs,
        tax_df,
    )


@app.cell
def _(curve_max, difference_df, marker_notes, markers_df, selected_home, tax_df):
    selected_rows = tax_df.filter(
        pl.col("market_value") == selected_home.value
    ).to_dicts()
    selected_delta = selected_rows[1]["tax"] - selected_rows[0]["tax"]
    selected_summary = mo.md(
        f"### Valgt bolig: {selected_home.value / 1_000_000:g} mill. NOK\n"
        f"Referanse: **{selected_rows[0]['tax']:,.0f} kr/år** · "
        f"Sandkasse: **{selected_rows[1]['tax']:,.0f} kr/år** · "
        f"Endring: **{selected_delta:+,.0f} kr/år**\n\n"
        f"Økonomisk nettoformue: **{selected_rows[1]['economic_wealth']:,.0f} kr** "
        "(før skatterabatt). Inntektsandel: "
        + (
            f"**{selected_rows[1]['income_share']:.2f} %** av bruttoinntekt."
            if selected_rows[1]["income_share"] is not None
            else "ikke definert ved null inntekt."
        )
    )
    curve_panels = [
        create_curve_panel(
            tax_df, field, title, markers_df, selected_home.value, curve_max
        )
        for field, title in [
            ("valuation", "Boligens formuesverdi (NOK)"),
            ("tax_base", "Etter gjeld og fradrag — før nullgulv (NOK)"),
            ("tax", "Årlig formuesskatt (NOK)"),
        ]
    ]
    delta_panel = create_curve_panel(
        difference_df.with_columns(Scenario=pl.lit("Din sandkasse")),
        "difference",
        "Endring fra referansen (NOK/år)",
        markers_df,
        selected_home.value,
        curve_max,
    )
    burden_panel = create_curve_panel(
        tax_df,
        "income_share",
        "Skatt / bruttoinntekt (%)",
        markers_df,
        selected_home.value,
        curve_max,
    )
    coordinated_curves = alt.vconcat(
        *curve_panels, delta_panel, burden_panel
    ).resolve_scale(x="shared", color="shared")
    mo.vstack(
        [
            selected_summary,
            coordinated_curves,
            mo.accordion({"Hvor knekker kurvene?": mo.md("\n\n".join(marker_notes))}),
        ]
    )
    return coordinated_curves, selected_rows


@app.function
def create_curve_panel(
    df: pl.DataFrame,
    field: str,
    title: str,
    markers: pl.DataFrame,
    selected: float,
    maximum: float,
) -> alt.LayerChart:
    color = alt.Color(
        "Scenario:N",
        scale=alt.Scale(
            domain=["2026-referanse", "Din sandkasse"], range=["#34495e", "#0072b2"]
        ),
    )
    x = alt.X(
        "market_value:Q",
        title="Hele boligens markedsverdi (NOK)",
        scale=alt.Scale(domain=[0, maximum]),
        axis=alt.Axis(format="~s"),
    )
    lines = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=x,
            y=alt.Y(f"{field}:Q", title=title),
            color=color,
            tooltip=[
                "Scenario:N",
                alt.Tooltip("market_value:Q", format=",.0f"),
                alt.Tooltip(f"{field}:Q", format=",.2f"),
            ],
        )
    )
    boundaries = (
        alt.Chart(markers)
        .mark_rule(opacity=0.35)
        .encode(
            x=x,
            color=color,
            strokeDash=alt.StrokeDash("kind:N", title="Grense"),
            tooltip=["Scenario:N", "kind:N", "market_value:Q"],
        )
    )
    selected_rule = (
        alt.Chart(pl.DataFrame({"market_value": [selected]}))
        .mark_rule(color="#9c6500")
        .encode(x=x)
    )
    dots = (
        alt.Chart(df.filter(pl.col("market_value") == selected))
        .mark_point(filled=True, size=55)
        .encode(x=x, y=f"{field}:Q", color=color)
    )
    zero = (
        alt.Chart(pl.DataFrame({"zero": [0]}))
        .mark_rule(color="#aaa")
        .encode(y="zero:Q")
    )
    return (lines + boundaries + selected_rule + dots + zero).properties(
        width=950, height=160
    )


@app.function
def calculate_wealth_tax_df(
    tiers: list[dict],
    base_deduction: float,
    tax_rate: float,
    scenario_name: str,
    is_couple: bool,
    mortgage_debt: float,
    other_net_wealth: float,
    upper_tax_rate: float = 1.1,
    upper_threshold: float = 21_500_000,
    max_value: float = 60_000_000,
    selected_value: float = 14_000_000,
    annual_income: float = 0,
    extra_values: list[float] | None = None,
) -> pl.DataFrame:
    """Full-owner primary home plus undiscounted assets; debt deducted once.

    Joint assessment doubles the allowance and upper tax threshold, not the
    whole-property valuation tier. Mixed discounted assets are outside scope.
    Rates are percentages; upper_threshold is BEFORE the personal allowance.
    """
    sorted_limits = sorted(t["limit"] for t in tiers if t["limit"] is not None)
    if (
        not tiers
        or sum(t["limit"] is None for t in tiers) != 1
        or len(set(sorted_limits)) != len(sorted_limits)
        or any(limit <= 0 for limit in sorted_limits)
        or any(not 0 <= t["rate"] <= 100 for t in tiers)
        or min(
            base_deduction,
            tax_rate,
            upper_tax_rate,
            mortgage_debt,
            other_net_wealth,
            annual_income,
            selected_value,
        )
        < 0
        or upper_threshold < base_deduction
        or max_value <= 0
    ):
        raise ValueError("Invalid tiers, balance sheet, or tax schedule")
    multiplier = 2 if is_couple else 1
    allowance = base_deduction * multiplier
    upper = upper_threshold * multiplier
    # Exact inverse breakpoints prevent a sampled line from rounding off kinks.
    points = {0.0, float(max_value), selected_value}
    points.update(float(v) for v in range(0, int(max_value), 100_000))
    points.update(sorted_limits)
    points.update(extra_values or [])
    for target in (allowance, upper):
        crossing = home_value_at_tax_wealth(
            tiers, target - other_net_wealth + mortgage_debt
        )
        if crossing is not None:
            points.add(crossing)
    df = pl.DataFrame(
        {"market_value": sorted(v for v in points if 0 <= v <= max_value)}
    )
    sorted_tiers = sorted(
        tiers, key=lambda x: x["limit"] if x["limit"] is not None else float("inf")
    )
    valuation_expr = pl.lit(0.0)
    prev_limit = 0.0
    for tier in sorted_tiers:
        limit = tier["limit"] if tier["limit"] is not None else float("inf")
        rate = tier.get("rate", 0.0) / 100
        portion = (
            pl.when(pl.col("market_value") > prev_limit)
            .then(pl.min_horizontal(pl.col("market_value"), limit) - prev_limit)
            .otherwise(0.0)
        )
        valuation_expr += portion * rate
        prev_limit = limit
    df = df.with_columns(valuation=valuation_expr)
    df = df.with_columns(
        net_wealth=pl.col("valuation") + other_net_wealth - mortgage_debt
    )
    actual_base_ded = base_deduction * 2 if is_couple else base_deduction
    df = df.with_columns(
        tax_base=pl.col("net_wealth") - actual_base_ded,
        economic_wealth=pl.col("market_value") + other_net_wealth - mortgage_debt,
        taxable_wealth=pl.max_horizontal(0, pl.col("net_wealth") - actual_base_ded),
    )
    # Clip each band independently: the upper band starts at net taxable wealth,
    # not at (upper threshold + allowance).
    df = df.with_columns(
        tax=(
            pl.min_horizontal(pl.col("taxable_wealth"), upper - allowance)
            * (tax_rate / 100)
            + pl.max_horizontal(0, pl.col("net_wealth") - upper)
            * (upper_tax_rate / 100)
        ),
        Scenario=pl.lit(scenario_name),
    )
    return df.with_columns(
        income_share=pl.col("tax") / annual_income * 100
        if annual_income > 0
        else pl.lit(None, dtype=pl.Float64)
    )


@app.function
def home_value_at_tax_wealth(tiers: list[dict], target: float) -> float | None:
    """Invert continuous progressive valuation; None means never reached."""
    if target <= 0:
        return 0.0
    previous = 0.0
    accumulated = 0.0
    for tier in sorted(
        tiers, key=lambda t: float("inf") if t["limit"] is None else t["limit"]
    ):
        limit = float("inf") if tier["limit"] is None else tier["limit"]
        rate = tier["rate"] / 100
        if rate > 0 and target <= accumulated + (limit - previous) * rate:
            return previous + (target - accumulated) / rate
        if rate > 0:
            accumulated += (limit - previous) * rate
        previous = limit
    return None


if __name__ == "__main__":
    app.run()
