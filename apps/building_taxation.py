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
        if last_limit >= 200_000_000:
            return
        new_limit = min(last_limit + 5_000_000, 200_000_000)
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
                start=0,
                stop=200_000_000,
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
        len(tier_limits) != len(set(tier_limits))
        or any(limit <= 0 for limit in tier_limits),
        mo.md("**Bruk ulike, positive grenser for hvert trinn.**"),
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
def _(
    curve_max,
    difference_df,
    housing_chart,
    marker_notes,
    markers_df,
    selected_home,
    tax_df,
):
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
        *curve_panels, housing_chart, delta_panel, burden_panel
    ).resolve_scale(x="shared", color="shared")
    mo.vstack(
        [
            selected_summary,
            coordinated_curves,
            mo.accordion({"Hvor knekker kurvene?": mo.md("\n\n".join(marker_notes))}),
        ]
    )
    return coordinated_curves, selected_rows


@app.cell
def _(curve_max, get_tiers, selected_home):
    reference = public_reference_data()
    housing_df = pl.DataFrame(reference["housing_bins"])
    housing_bars = (
        alt.Chart(housing_df)
        .mark_bar(color="#999", opacity=0.8, clip=True)
        .encode(
            x=alt.X(
                "lower:Q",
                title="Hele boligens markedsverdi (NOK)",
                scale=alt.Scale(domain=[0, curve_max]),
            ),
            x2="upper:Q",
            y=alt.Y("count:Q", title="Boliger (rekonstruert)"),
            tooltip=["lower:Q", "upper:Q", alt.Tooltip("count:Q", format=",.0f")],
        )
    )
    histogram_rules = (
        alt.Chart(
            pl.DataFrame(
                {
                    "value": [14_000_000, selected_home.value]
                    + [t["limit"] for t in get_tiers() if t["limit"] is not None]
                }
            )
        )
        .mark_rule(color="#9c6500")
        .encode(x="value:Q")
    )
    unknown_tail = (
        alt.Chart(
            pl.DataFrame({"lower": [30_000_000], "upper": [max(30_000_000, curve_max)]})
        )
        .mark_rect(color="#e9d8a6", opacity=0.35, clip=True)
        .encode(x="lower:Q", x2="upper:Q")
    )
    housing_chart = (housing_bars + histogram_rules + unknown_tail).properties(
        width=950,
        height=160,
        title="Primærboliger: digitalisert fra departementets figur (2026). Gul hale >30m: ukjent, ikke null.",
    )
    return housing_chart, housing_df, reference


@app.cell
def _(get_tiers, housing_df, reference, selected_rows):
    wealth_context = wealth_bracket(
        selected_rows[1]["economic_wealth"], reference["wealth_groups"]
    )
    exposure_limits = sorted(
        {14_000_000, *[t["limit"] for t in get_tiers() if t["limit"] is not None]}
    )
    exposure_rows = [
        dict(grense=limit, **exposure_above(reference["housing_bins"], limit))
        for limit in exposure_limits
    ]
    mo.vstack(
        [
            mo.md(
                f"### Hvor ligger eksemplet i formuesfordelingen?\n**{wealth_context}**\n\n"
                "SSB 10318, beregnet nettoformue i **2024**, husholdninger uten studenthusholdninger. "
                "Dette er et intervall, ikke en eksakt rang. Dagens egenoppgitte kroner sammenlignes "
                "uten prisjustering; pensjonsrettigheter er ikke med. Et dyrt hus alene bestemmer ikke rang."
            ),
            mo.md(
                f"### Hvor mange boliger ligger over grensene?\n"
                f"Figuren dekker omtrent **{housing_df['count'].sum() / 1_000_000:.2f} millioner** primærboliger i viste grupper. "
                "Antall under er **rekonstruert**, ikke eksakte registertellinger. "
                "Midtestimatet antar jevn fordeling i hvert millionintervall; nedre/øvre gjelder ukjent "
                "plassering innen intervallet. **Boliger over 30 mill. kommer i tillegg og er ukjent.** "
                "Dette teller boliger, ikke skattebetalere. Departementet oppgir avrundet 2 % over 14 mill."
            ),
            mo.ui.table(pl.DataFrame(exposure_rows), selection=None),
            mo.accordion(
                {
                    "Kilder og metode": mo.md(
                        "[Boligfigur, Finansdepartementet 27.02.2026, side 8 og 10](https://www.regjeringen.no/contentassets/27840e5ecb354f02a249f3cbd86b01d9/finmins-presentasjon-oppdatert-boligmodell-27.02.26.pdf). "
                        "Høyder hentet fra PDF-vektorer, avrundet til 100 boliger. Etikett 1 tolkes som 0–1 mill., "
                        "etikett 2 som 1–2 mill. osv.; intervallgrensene er en antakelse. "
                        "Ingen ukjent hale er fylt inn som observerte boliger. "
                        "[Formuesgrenser: SSB 10318](https://www.ssb.no/statbank/table/10318), korrigert februar 2026. "
                        "Kildesnapshot 20.09.2026 er pakket i appen; ingen personlige verdier sendes til SSB."
                    )
                }
            ),
        ]
    )
    return


@app.cell
def _():
    tail_count_ui = mo.ui.number(
        start=0,
        stop=100_000,
        value=1000,
        step=500,
        label="Antatt antall boliger over 30 mill. (ikke observert)",
    )
    tail_upper_ui = mo.ui.number(
        start=50_000_000,
        stop=200_000_000,
        value=60_000_000,
        step=10_000_000,
        label="Antatt øvre boligverdi i halen (NOK)",
    )
    mo.vstack(
        [
            mo.md(
                "### Fordelingsvektet illustrasjon — ikke et anslag på Norges faktiske proveny\n"
                "**Felles profil:** Vi legger samme gjeld, andre eiendeler og fastsettingsform som "
                "du valgte over, på alle boliger. Én hel-eier-skatteenhet per bolig. "
                "Dette er en kontrollert øvelse, ikke observerte norske husholdninger. "
                "Halen er selvvalgt: halvparten i 30–40 mill., halvparten i 40 mill.–øvre verdi. "
                "Alle intervaller antas jevnt fordelt i midtestimatet."
            ),
            mo.hstack([tail_count_ui, tail_upper_ui]),
        ]
    )
    return tail_count_ui, tail_upper_ui


@app.cell
def _(policy_inputs, reference, shared_inputs, tail_count_ui, tail_upper_ui):
    population_results = []
    for debt_factor in (0.5, 1.0, 1.5):
        for tail_factor in (0.0, 1.0, 2.0):
            assumed_bins = reference["housing_bins"] + [
                dict(
                    lower=30_000_000,
                    upper=40_000_000,
                    count=tail_count_ui.value * tail_factor / 2,
                ),
                dict(
                    lower=40_000_000,
                    upper=tail_upper_ui.value,
                    count=tail_count_ui.value * tail_factor / 2,
                ),
            ]
            population_effect = weighted_policy_effect(
                assumed_bins,
                policy_inputs,
                {
                    **shared_inputs,
                    "mortgage_debt": shared_inputs["mortgage_debt"] * debt_factor,
                },
            )
            population_results.append(
                dict(
                    gjeldsfaktor=debt_factor,
                    halefaktor=tail_factor,
                    **population_effect,
                )
            )
    central_effect = next(
        r for r in population_results if r["gjeldsfaktor"] == 1 and r["halefaktor"] == 1
    )
    sensitivity_low = min(r["minimum"] for r in population_results)
    sensitivity_high = max(r["maximum"] for r in population_results)
    population_table = pl.DataFrame(population_results).with_columns(
        pl.col("uniform", "minimum", "maximum").truediv(1_000_000).round(1)
    )
    mo.vstack(
        [
            mo.md(
                f"**Illustrert årlig endring i samlede skatteinntekter: {central_effect['uniform'] / 1_000_000:+.1f} mill. kr.** "
                "Minus betyr mindre skatt enn 2026-referansen.\n\n"
                f"**Sensitivitet: {sensitivity_low / 1_000_000:+.1f} til {sensitivity_high / 1_000_000:+.1f} mill. kr.** "
                "Dette er ikke et konfidensintervall eller en nasjonal prognose. "
                "Vi varierer gjelden til 0,5×/1×/1,5× din valgte gjeld og haleantallet til 0×/1×/2× antakelsen. "
                "I tillegg brukes laveste/høyeste skatteendring innen hvert verdiintervall. "
                "Hvis valgt gjeld er null, gir gjeldsfaktorene samme profil. "
                "Ukjente eierforhold, samvariasjon mellom bolig/annen formue/gjeld og verdier over haletaket "
                "er ikke fanget av spennet. Inntekt og atferd endrer ikke dette statiske regnestykket."
            ),
            mo.accordion(
                {
                    "Vis regnestykkets sensitivitet (millioner kr/år)": mo.ui.table(
                        population_table, selection=None
                    )
                }
            ),
        ]
    )
    return central_effect, population_results


@app.function
def weighted_policy_effect(
    bins: list[dict], policies: list[dict], household: dict
) -> dict:
    """Integrate tax differences per property, not tax on the average home.

    Piecewise linear tax is integrated exactly by trapezoids including every
    valuation, allowance and upper-rate kink. Per-bin extrema are conditional
    bounds for unknown within-bin placement, not statistical confidence bounds.
    """
    if len(policies) != 2 or any(
        b["upper"] <= b["lower"] or b["count"] < 0 for b in bins
    ):
        raise ValueError("Two policies and valid nonnegative property bins required")
    maximum = max(b["upper"] for b in bins)
    edges = [float(b[key]) for b in bins for key in ("lower", "upper")]
    inputs = {
        **household,
        "max_value": maximum,
        "selected_value": 0,
        "extra_values": edges,
    }
    first_pass = [calculate_wealth_tax_df(**policy, **inputs) for policy in policies]
    inputs["extra_values"] = sorted(
        set(pl.concat(first_pass)["market_value"].to_list())
    )
    frames = [calculate_wealth_tax_df(**policy, **inputs) for policy in policies]
    values = frames[0]["market_value"].to_list()
    differences = (frames[1]["tax"] - frames[0]["tax"]).to_list()
    uniform = minimum = maximum_effect = 0.0
    for band in bins:
        points = [
            (v, delta)
            for v, delta in zip(values, differences, strict=True)
            if band["lower"] <= v <= band["upper"]
        ]
        area = sum(
            (right[0] - left[0]) * (right[1] + left[1]) / 2
            for left, right in zip(points, points[1:])
        )
        uniform += band["count"] * area / (band["upper"] - band["lower"])
        minimum += band["count"] * min(delta for _, delta in points)
        maximum_effect += band["count"] * max(delta for _, delta in points)
    return {"uniform": uniform, "minimum": minimum, "maximum": maximum_effect}


@app.cell
def _(reference):
    financial_means_df = pl.DataFrame(reference["financial_means"])
    composition_df = pl.DataFrame(reference["financial_composition"])
    balance_df = decile_net_balance(reference)
    balance_components = balance_df.unpivot(
        on=["Finansformue", "Realkapital minus samlet gjeld"],
        index="decile",
        variable_name="component",
        value_name="amount",
    )
    balance_bars = (
        alt.Chart(balance_components)
        .mark_bar()
        .encode(
            x=alt.X("decile:O", title="Desil etter beregnet nettoformue (1 = lavest)"),
            y=alt.Y(
                "amount:Q", title="Gjennomsnitt per husholdning (NOK)", stack="zero"
            ),
            color=alt.Color(
                "component:N",
                title="Del av nettoformuen",
                scale=alt.Scale(
                    domain=["Finansformue", "Realkapital minus samlet gjeld"],
                    range=["#0072b2", "#d89b32"],
                ),
            ),
            tooltip=["decile:O", "component:N", alt.Tooltip("amount:Q", format=",.0f")],
        )
    )
    balance_markers = (
        alt.Chart(balance_df)
        .mark_point(shape="diamond", filled=True, color="#222", size=85)
        .encode(
            x="decile:O",
            y="net_wealth:Q",
            tooltip=[
                "decile:O",
                alt.Tooltip("net_wealth:Q", title="Nettoformue", format=",.0f"),
            ],
        )
    )
    balance_zero = (
        alt.Chart(pl.DataFrame({"zero": [0]}))
        .mark_rule(color="#666")
        .encode(y="zero:Q")
    )
    net_balance_chart = (balance_bars + balance_markers + balance_zero).properties(
        width=950, height=280
    )
    financial_mean_chart = (
        alt.Chart(financial_means_df)
        .mark_bar(color="#0072b2")
        .encode(
            x=alt.X("decile:O", title="Desil etter beregnet nettoformue (1 = lavest)"),
            y=alt.Y("mean:Q", title="Gjennomsnittlig finansformue (NOK)"),
            tooltip=["decile:O", "mean:Q"],
        )
        .properties(width=950, height=240)
    )
    decile_composition = (
        alt.Chart(composition_df.filter(~pl.col("group").str.starts_with("Topp")))
        .mark_bar()
        .encode(
            x=alt.X(
                "group:O",
                sort=[str(n) for n in range(1, 11)],
                title="Nettoformuesdesil",
            ),
            y=alt.Y("percent:Q", title="Andel av finansformuen (%)"),
            color=alt.Color("component:N", title="Komponent"),
            tooltip=["group:N", "component:N", "percent:Q"],
        )
        .properties(width=950, height=240)
    )
    top_composition = (
        alt.Chart(composition_df.filter(pl.col("group").str.starts_with("Topp")))
        .mark_bar()
        .encode(
            x=alt.X("group:N", title="Detalj: inngår allerede i desil 10"),
            y=alt.Y("percent:Q", title="Andel av finansformuen (%)"),
            color=alt.Color("component:N", title="Komponent"),
            tooltip=["group:N", "component:N", "percent:Q"],
        )
        .properties(width=950, height=180)
    )
    mo.vstack(
        [
            mo.md(
                "### Hvor er finansformuen? — publiserte SSB-tall, 2024\n"
                "Husholdninger rangert etter **nettoformue**, ikke inntekt eller boligpris. "
                "Finansformue er bankinnskudd, verdipapirer m.m., **ikke bolig eller gjeld**. "
                "Vi viser den verifiserte delhistorien fremfor å finne på bolig- og gjeldsfordelingen."
            ),
            mo.md(
                "#### Nettoformuen: finansformue og realkapital etter samlet gjeld\n"
                "**Svart diamant = publisert nettoformue.** Blått = publisert finansformue. "
                "Gult = nettoformue minus finansformue, altså realkapital minus **all** gjeld. "
                "Vi trekker fra kompatible desilgjennomsnitt fra SSB 10318 og artikkelens figur 2, "
                "samme år og befolkning. Dette er en regnskapsmessig differanse, ikke en antatt boligportefølje. "
                "Negativt gult betyr at samlet gjeld overstiger realkapitalen; det betyr ikke at boligen har negativ verdi. "
                "Realkapital omfatter mer enn bolig, og samlet gjeld omfatter mer enn boliglån."
            ),
            net_balance_chart,
            mo.accordion(
                {
                    "Avstemming av publiserte desiltall": mo.md(
                        "SSB 10318s desilgrupper summerer til én husholdning mindre enn landstotalen. "
                        "Det vektede desilgjennomsnittet er om lag 462 kr høyere enn publisert "
                        "landsgjennomsnitt på 3 890 400 kr (ca. 0,012 %). Årsaken er ikke avklart. "
                        "Vi beholder de publiserte verdiene uten å skalere dem for å tvinge samsvar. "
                        "Gul differanse er beregnet fra publiserte gjennomsnitt, ikke direkte observerte porteføljer."
                    )
                }
            ),
            mo.md("#### Finansformuen alene"),
            financial_mean_chart,
            decile_composition,
            top_composition,
            mo.md(
                "[SSB, Vekst i husholdningenes finansformue i 2024, figur 2–3 (19.02.2026)]"
                "(https://www.ssb.no/inntekt-og-forbruk/inntekt-og-formue/statistikk/inntekts-og-formuesstatistikk-for-husholdninger/artikler/vekst-i-husholdningenes-finansformue-i-2024). "
                "Studenthusholdninger utelatt. Prosentene er avrundet og kan summere til 99 eller 101. "
                "Toppgruppene overlapper og skal ikke legges til desilene. "
                "Gjennomsnitt er ikke en typisk husholdning; finansformue er heller ikke bare tilgjengelige kontanter."
            ),
        ]
    )
    return financial_mean_chart, decile_composition, top_composition, net_balance_chart


@app.function
def decile_net_balance(reference: dict) -> pl.DataFrame:
    """Accounting residual from compatible 2024 net-wealth-ranked means.

    Net wealth = real assets + financial assets - total debt. Subtracting
    financial assets does NOT identify housing equity or mortgage debt.
    The sources exclude student households and use the same wealth ranking.
    """
    means = {row["decile"]: row["mean"] for row in reference["financial_means"]}
    groups = {
        int(row["code"]): row
        for row in reference["wealth_groups"]
        if row["code"].isdigit()
    }
    if set(means) != set(range(1, 11)) or set(groups) != set(means):
        raise ValueError("Exactly ten matching net-wealth deciles required")
    rows = []
    for decile in sorted(means):
        if means[decile] is None or groups[decile]["mean"] is None:
            raise ValueError("Missing source mean; cannot treat it as zero")
        rows.append(
            {
                "decile": decile,
                "Finansformue": means[decile],
                "Realkapital minus samlet gjeld": groups[decile]["mean"]
                - means[decile],
                "net_wealth": groups[decile]["mean"],
                "households": groups[decile]["households"],
            }
        )
    return pl.DataFrame(rows)


@app.function
def wealth_bracket(net_wealth: float, groups: list[dict]) -> str:
    boundaries = [
        (row["cutoff"], (int(row["code"]) - 1) * 10)
        for row in groups
        if row["code"].isdigit() and row["cutoff"] is not None
    ]
    boundaries += [
        (row["cutoff"], {"05b": 95, "01b": 99, "01c": 99.9}[row["code"]])
        for row in groups
        if row["code"] in ("05b", "01b", "01c")
    ]
    lower_percentile = 0.0
    for cutoff, percentile in sorted(boundaries):
        if net_wealth < cutoff:
            return f"Mellom {lower_percentile:g}. og {percentile:g}. persentil (2024-referanse)"
        lower_percentile = percentile
    return "Topp 0,1 % (2024-referanse)"


@app.function
def exposure_above(bins: list[dict], threshold: float) -> dict:
    estimate = lower = upper = 0.0
    for band in bins:
        if threshold <= band["lower"]:
            lower += band["count"]
            upper += band["count"]
            estimate += band["count"]
        elif threshold < band["upper"]:
            upper += band["count"]
            estimate += (
                band["count"]
                * (band["upper"] - threshold)
                / (band["upper"] - band["lower"])
            )
    return {
        "midtanslag_viste_grupper": round(estimate / 100) * 100,
        "nedre_viste_grupper": round(lower / 100) * 100,
        "øvre_viste_grupper": round(upper / 100) * 100,
    }


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


# BEGIN GENERATED PUBLIC REFERENCE
@app.function
def public_reference_data() -> dict:
    """Public aggregates; generated offline by scripts/build_wealth_reference.py."""
    return {
        "snapshot": "2026-09-20",
        "wealth_year": 2024,
        "financial_means": [
            {"decile": 1, "mean": 210800},
            {"decile": 2, "mean": 65400},
            {"decile": 3, "mean": 193100},
            {"decile": 4, "mean": 403200},
            {"decile": 5, "mean": 491500},
            {"decile": 6, "mean": 625500},
            {"decile": 7, "mean": 856100},
            {"decile": 8, "mean": 1251100},
            {"decile": 9, "mean": 2081800},
            {"decile": 10, "mean": 12322000},
        ],
        "financial_composition": [
            {"group": "1", "component": "Bankinnskudd", "percent": 58},
            {"group": "2", "component": "Bankinnskudd", "percent": 73},
            {"group": "3", "component": "Bankinnskudd", "percent": 78},
            {"group": "4", "component": "Bankinnskudd", "percent": 72},
            {"group": "5", "component": "Bankinnskudd", "percent": 67},
            {"group": "6", "component": "Bankinnskudd", "percent": 66},
            {"group": "7", "component": "Bankinnskudd", "percent": 66},
            {"group": "8", "component": "Bankinnskudd", "percent": 65},
            {"group": "9", "component": "Bankinnskudd", "percent": 61},
            {"group": "10", "component": "Bankinnskudd", "percent": 19},
            {"group": "Topp 1 prosent", "component": "Bankinnskudd", "percent": 6},
            {"group": "Topp 0,1 prosent", "component": "Bankinnskudd", "percent": 2},
            {"group": "1", "component": "Andeler i verdipapirfond", "percent": 5},
            {"group": "2", "component": "Andeler i verdipapirfond", "percent": 5},
            {"group": "3", "component": "Andeler i verdipapirfond", "percent": 4},
            {"group": "4", "component": "Andeler i verdipapirfond", "percent": 5},
            {"group": "5", "component": "Andeler i verdipapirfond", "percent": 6},
            {"group": "6", "component": "Andeler i verdipapirfond", "percent": 6},
            {"group": "7", "component": "Andeler i verdipapirfond", "percent": 6},
            {"group": "8", "component": "Andeler i verdipapirfond", "percent": 6},
            {"group": "9", "component": "Andeler i verdipapirfond", "percent": 6},
            {"group": "10", "component": "Andeler i verdipapirfond", "percent": 4},
            {
                "group": "Topp 1 prosent",
                "component": "Andeler i verdipapirfond",
                "percent": 3,
            },
            {
                "group": "Topp 0,1 prosent",
                "component": "Andeler i verdipapirfond",
                "percent": 2,
            },
            {"group": "1", "component": "Aksjer og andre verdipapir", "percent": 17},
            {"group": "2", "component": "Aksjer og andre verdipapir", "percent": 7},
            {"group": "3", "component": "Aksjer og andre verdipapir", "percent": 5},
            {"group": "4", "component": "Aksjer og andre verdipapir", "percent": 7},
            {"group": "5", "component": "Aksjer og andre verdipapir", "percent": 8},
            {"group": "6", "component": "Aksjer og andre verdipapir", "percent": 9},
            {"group": "7", "component": "Aksjer og andre verdipapir", "percent": 9},
            {"group": "8", "component": "Aksjer og andre verdipapir", "percent": 10},
            {"group": "9", "component": "Aksjer og andre verdipapir", "percent": 13},
            {"group": "10", "component": "Aksjer og andre verdipapir", "percent": 60},
            {
                "group": "Topp 1 prosent",
                "component": "Aksjer og andre verdipapir",
                "percent": 80,
            },
            {
                "group": "Topp 0,1 prosent",
                "component": "Aksjer og andre verdipapir",
                "percent": 89,
            },
            {"group": "1", "component": "Aksjesparekonto", "percent": 11},
            {"group": "2", "component": "Aksjesparekonto", "percent": 10},
            {"group": "3", "component": "Aksjesparekonto", "percent": 8},
            {"group": "4", "component": "Aksjesparekonto", "percent": 10},
            {"group": "5", "component": "Aksjesparekonto", "percent": 12},
            {"group": "6", "component": "Aksjesparekonto", "percent": 12},
            {"group": "7", "component": "Aksjesparekonto", "percent": 12},
            {"group": "8", "component": "Aksjesparekonto", "percent": 12},
            {"group": "9", "component": "Aksjesparekonto", "percent": 13},
            {"group": "10", "component": "Aksjesparekonto", "percent": 9},
            {"group": "Topp 1 prosent", "component": "Aksjesparekonto", "percent": 5},
            {"group": "Topp 0,1 prosent", "component": "Aksjesparekonto", "percent": 2},
            {"group": "1", "component": "Annen finansformue", "percent": 9},
            {"group": "2", "component": "Annen finansformue", "percent": 6},
            {"group": "3", "component": "Annen finansformue", "percent": 5},
            {"group": "4", "component": "Annen finansformue", "percent": 6},
            {"group": "5", "component": "Annen finansformue", "percent": 7},
            {"group": "6", "component": "Annen finansformue", "percent": 7},
            {"group": "7", "component": "Annen finansformue", "percent": 7},
            {"group": "8", "component": "Annen finansformue", "percent": 7},
            {"group": "9", "component": "Annen finansformue", "percent": 7},
            {"group": "10", "component": "Annen finansformue", "percent": 7},
            {
                "group": "Topp 1 prosent",
                "component": "Annen finansformue",
                "percent": 6,
            },
            {
                "group": "Topp 0,1 prosent",
                "component": "Annen finansformue",
                "percent": 6,
            },
        ],
        "wealth_groups": [
            {
                "code": "Ialt",
                "label": "I alt",
                "cutoff": None,
                "households": 2616826,
                "mean": 3890400,
            },
            {
                "code": "01",
                "label": "Desil 1",
                "cutoff": None,
                "households": 261682,
                "mean": -1031500,
            },
            {
                "code": "02",
                "label": "Desil 2",
                "cutoff": -192800,
                "households": 261685,
                "mean": -42900,
            },
            {
                "code": "03",
                "label": "Desil 3",
                "cutoff": 20800,
                "households": 261680,
                "mean": 159700,
            },
            {
                "code": "04",
                "label": "Desil 4",
                "cutoff": 390300,
                "households": 261684,
                "mean": 748600,
            },
            {
                "code": "05",
                "label": "Desil 5",
                "cutoff": 1131000,
                "households": 261682,
                "mean": 1538100,
            },
            {
                "code": "06",
                "label": "Desil 6",
                "cutoff": 1955700,
                "households": 261683,
                "mean": 2406400,
            },
            {
                "code": "07",
                "label": "Desil 7",
                "cutoff": 2880100,
                "households": 261681,
                "mean": 3415800,
            },
            {
                "code": "08",
                "label": "Desil 8",
                "cutoff": 3996700,
                "households": 261683,
                "mean": 4715300,
            },
            {
                "code": "09",
                "label": "Desil 9",
                "cutoff": 5543100,
                "households": 261682,
                "mean": 6787800,
            },
            {
                "code": "10",
                "label": "Desil 10",
                "cutoff": 8454200,
                "households": 261683,
                "mean": 20211300,
            },
            {
                "code": "05b",
                "label": "Høgaste 5 prosent",
                "cutoff": 12140200,
                "households": 130842,
                "mean": 30419900,
            },
            {
                "code": "01b",
                "label": "Høgaste 1 prosent",
                "cutoff": 28250400,
                "households": 26169,
                "mean": 84551200,
            },
            {
                "code": "01c",
                "label": "Høgaste 0,1 prosent",
                "cutoff": 133425400,
                "households": 2617,
                "mean": 402084700,
            },
        ],
        "housing_bins": [
            {"lower": 0, "upper": 1000000, "count": 96400},
            {"lower": 1000000, "upper": 2000000, "count": 253300},
            {"lower": 2000000, "upper": 3000000, "count": 353800},
            {"lower": 3000000, "upper": 4000000, "count": 318000},
            {"lower": 4000000, "upper": 5000000, "count": 226200},
            {"lower": 5000000, "upper": 6000000, "count": 149000},
            {"lower": 6000000, "upper": 7000000, "count": 95500},
            {"lower": 7000000, "upper": 8000000, "count": 61500},
            {"lower": 8000000, "upper": 9000000, "count": 41900},
            {"lower": 9000000, "upper": 10000000, "count": 28000},
            {"lower": 10000000, "upper": 11000000, "count": 19200},
            {"lower": 11000000, "upper": 12000000, "count": 14200},
            {"lower": 12000000, "upper": 13000000, "count": 10900},
            {"lower": 13000000, "upper": 14000000, "count": 8700},
            {"lower": 14000000, "upper": 15000000, "count": 7300},
            {"lower": 15000000, "upper": 16000000, "count": 6100},
            {"lower": 16000000, "upper": 17000000, "count": 4600},
            {"lower": 17000000, "upper": 18000000, "count": 3700},
            {"lower": 18000000, "upper": 19000000, "count": 2700},
            {"lower": 19000000, "upper": 20000000, "count": 2300},
            {"lower": 20000000, "upper": 21000000, "count": 1800},
            {"lower": 21000000, "upper": 22000000, "count": 1400},
            {"lower": 22000000, "upper": 23000000, "count": 1100},
            {"lower": 23000000, "upper": 24000000, "count": 900},
            {"lower": 24000000, "upper": 25000000, "count": 700},
            {"lower": 25000000, "upper": 26000000, "count": 500},
            {"lower": 26000000, "upper": 27000000, "count": 500},
            {"lower": 27000000, "upper": 28000000, "count": 400},
            {"lower": 28000000, "upper": 29000000, "count": 400},
            {"lower": 29000000, "upper": 30000000, "count": 400},
        ],
    }


# END GENERATED PUBLIC REFERENCE


if __name__ == "__main__":
    app.run()
