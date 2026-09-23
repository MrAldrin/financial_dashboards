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
    from math import isfinite
    from bisect import bisect_right
    from typing import TypedDict

    class TaxUnitProfile(TypedDict):
        ownership_share: float
        is_couple: bool
        mortgage_debt: float
        other_net_wealth: float

    class PropertyTemplate(TypedDict):
        weight: float  # Probability conditional on the property bin, not per owner.
        units: list[TaxUnitProfile]

    class PropertyScenarioBin(TypedDict):
        lower: float
        upper: float
        count: float
        templates: list[PropertyTemplate]


@app.cell
def _():
    mo.md("""
    # Bolig, formue og skatt — utforsk samspillet
    **Modellberegning, ikke en skattemelding.** Velg én skatteenhets andel av en
    ordinær primærbolig (én person eller kvalifisert fellesfastsetting).
    Hele boligen verdsettes før eierandelen fordeles. Andre eiendeler er
    bankinnskudd / eiendeler uten verdsettingsrabatt. Gjeld trekkes fra én gang.
    Aksjer med rabatt, sekundærbolig, særskilte flerboligbygg, blandet bostedsstatus
    innen skatteenheten og kommunale særregler er ikke modellert.

    Boligregelen er vedtatt i [lov 23.06.2026 nr. 66, II/IV](https://lovdata.no/dokument/LTI/lov/2026-06-23-66),
    med virkning fra inntektsåret 2026. Standardrater, ikke alle kommuners satser:
    publiserte [2026-satser fra Skatteetaten](https://www.skatteetaten.no/satser/formuesskatt/),
    14 mill. boliggrense, 25/70 % verdsettelse, 1,9 mill. fradrag,
    1/1,1 % skatt og øvre innslag 21,5 mill. Dette er ikke en full juridisk regelmotor.
    """)
    return


@app.cell
def _():
    is_couple = mo.ui.switch(
        label="Fellesfastsetting (doble personlige innslag, ikke boliggrensen)"
    )
    ownership_share_ui = mo.ui.number(
        label="Skatteenhetens samlede eierandel (%)",
        start=0,
        stop=100,
        value=100,
        step=1,
    )
    mortgage_debt = mo.ui.number(
        label="Skatteenhetens gjeld (NOK, allerede fordelt)",
        start=0,
        value=1_600_000,
        step=100_000,
    )
    other_net_wealth = mo.ui.number(
        label="Skatteenhetens andre eiendeler uten rabatt, før gjeld (NOK)",
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
        label="Hele boligens verdi (NOK)",
    )
    annual_income = mo.ui.number(
        start=0,
        value=800_000,
        step=50_000,
        label="Skatteenhetens årlige bruttoinntekt (NOK)",
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
        ownership_share_ui,
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
                label=f"Fjern trinn {i + 1}",
                on_change=lambda _, idx=i: remove_tier(idx),
                kind="neutral",
            )
            inputs.append(remove_btn)
        tier_rows.append(mo.hstack(inputs, justify="start", align="center", wrap=True))
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
        wrap=True,
    )
    valuation_ui = mo.vstack(
        [
            mo.md("#### Verdsettelsestrinn (sorteres etter grense):"),
            mo.md(
                "**Boligtrinn-knappene endrer bare verdsettelsestrinn** (grense og andel); "
                "personlig økonomi, fradrag og skattesatser beholdes. "
                "«Boligtrinn: 14 mill.» er ikke en nullstilling av hele sandkassen."
            ),
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
    get_tiers,
    is_couple,
    mortgage_debt,
    other_net_wealth,
    ownership_share_ui,
    selected_home,
    tax_rate_ui,
    upper_rate_ui,
    valuation_ui,
):
    ui_elements = mo.vstack(
        [
            mo.md("### Personlig økonomi"),
            is_couple,
            mo.md(
                "Fellesfastsetting er et selvvalgt scenario, ikke en kvalifikasjonskontroll. "
                "Ekteskapets inngåelsesår og separasjon/varig adskillelse ved årsslutt "
                "har særregler. Institusjonsopphold alene er ikke varig adskillelse. "
                "Vanlige samboere beregnes hver for seg; bare særskilt kvalifiserte "
                "meldepliktige samboere omfattes. "
                "[Regler: §§ 2-10–2-16](https://lovdata.no/dokument/NL/lov/1999-03-26-14/§2-10). "
                "Ved fellesfastsetting oppgis samlet eierandel og økonomi for begge. "
                "Et kvalifisert par som eier 50 % hver, oppgir 100 %. "
                "All oppgitt boligandel må være primærbolig for skatteenheten. "
                "Andre eiendeler, gjeld og inntekt er allerede fordelt og skaleres ikke med eierandelen."
            ),
            ownership_share_ui,
            mo.hstack([mortgage_debt, other_net_wealth, annual_income], wrap=True),
            selected_home,
            mo.md("### Politisk sandkasse — sammenlignet med fast 2026-referanse"),
            mo.md(
                "**Status: "
                + (
                    "samme politikk som 2026-referansen"
                    if get_tiers()
                    == [
                        {"limit": 14_000_000, "rate": 25.0},
                        {"limit": None, "rate": 70.0},
                    ]
                    and base_deduction.value == 1_900_000
                    and tax_rate_ui.value == 1.0
                    and upper_rate_ui.value == 1.1
                    else "egendefinert politikk"
                )
                + "**. Personlig økonomi gjelder begge kurver; boligtrinn-knappene "
                "endrer bare sandkassens boligtrinn."
            ),
            mo.hstack([base_deduction, tax_rate_ui, upper_rate_ui], wrap=True),
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
    ownership_share_ui,
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
        ownership_share=ownership_share_ui.value / 100,
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
                ownership_share=shared_inputs["ownership_share"],
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
    policy_inputs,
    selected_home,
    shared_inputs,
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
        f"Skatteenhetens boligandel: **{selected_rows[1]['owned_market_value']:,.0f} kr** · "
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
            ("valuation", "Skatteenhetens boligformuesverdi (NOK)"),
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
    diagnostic_rows = [
        selected_tax_diagnostics(
            tax_df.filter(pl.col("Scenario") == policy["scenario_name"]),
            selected_home.value,
            policy,
            shared_inputs,
        )
        for policy in policy_inputs
    ]
    diagnostic_table = pl.DataFrame(
        {
            "Størrelse": [key for key in diagnostic_rows[0] if key != "Politikk"],
            "2026-referanse": [
                round(value) if value is not None else None
                for key, value in diagnostic_rows[0].items()
                if key != "Politikk"
            ],
            "Din sandkasse": [
                round(value) if value is not None else None
                for key, value in diagnostic_rows[1].items()
                if key != "Politikk"
            ],
        }
    )
    mo.vstack(
        [
            selected_summary,
            coordinated_curves,
            mo.accordion(
                {
                    "Vis valgt boligs verdsetting, skattebånd og marginal endring": mo.vstack(
                        [
                            mo.md(
                                "Beløpene gjelder **skatteenheten** ved valgt *hel* boligverdi. "
                                "Verdsetting skjer før eierandelen fordeles; andre eiendeler og "
                                "gjeld er allerede fordelt. Skattegrunnlag før nullgulv = "
                                "boligformuesverdi + andre eiendeler − gjeld − personfradrag. "
                                "Begge skattebånd beregnes på samme nettoformue; fradraget trekkes "
                                "**bare én gang**. Marginalene viser ekstra årlig skatt i kroner "
                                "ved +1 mill. kr *hel* boligverdi, innen et lineært stykke, ikke "
                                "skatt på en faktisk 1m-endring som krysser flere grenser. "
                                "Ved knekk kan venstre og høyre avvike; regningen hopper ikke. "
                                "Tom venstre/høyre betyr utenfor vist område."
                            ),
                            mo.ui.table(
                                diagnostic_table,
                                selection=None,
                                pagination=False,
                                show_column_summaries=False,
                                show_data_types=False,
                                show_search=False,
                                show_download=False,
                            ),
                        ]
                    ),
                    "Hvor knekker kurvene?": mo.md("\n\n".join(marker_notes)),
                }
            ),
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
                "uten prisjustering; pensjonsrettigheter er ikke med. Et dyrt hus alene bestemmer ikke rang. "
                "Skatteenheten er ikke nødvendigvis en hel statistisk husholdning: særlig ved delt "
                "eierskap er dette kun en beløpssammenligning, ikke din personlige persentil."
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
                "Din personlige eierandel brukes ikke her: illustrasjonen beholder 100 % eierskap. "
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
                    "ownership_share": 1.0,
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


@app.cell
def _(policy_inputs, reference, tail_count_ui, tail_upper_ui):
    # Separate from the personal controls and the legacy one-full-owner result.
    # All alternatives use the same published bins, assumed tail and two policies.
    scenario_names = {
        "starting_mix": "Startmiks: antatt gjeld/eierskap",
        "high_assets": "Dyre boliger: +2 mill. andre eiendeler",
        "high_debt": "Dyre boliger: +2 mill. gjeld",
        "uneven_owners": "Separate eiere: 25/75 i stedet for 50/50",
    }
    scenario_rows = []
    for variant, name in scenario_names.items():
        bins = illustrative_scenario_bins(
            reference["housing_bins"], tail_count_ui.value, tail_upper_ui.value, variant
        )
        effect = weighted_scenario_effect(bins, policy_inputs)
        scenario_rows.append(
            {
                "Antakelse": name,
                "Boliger": round(effect["properties"]),
                "Antatte skatteenheter": round(effect["tax_units"]),
                "Referanse (mill. kr/år)": round(effect["reference"] / 1_000_000, 1),
                "Sandkasse (mill. kr/år)": round(effect["reform"] / 1_000_000, 1),
                "Endring (mill. kr/år)": round(effect["uniform"] / 1_000_000, 1),
            }
        )
    mo.accordion(
        {
            "Avansert: antatte eiere og gjeld/formue per bolig": mo.vstack(
                [
                    mo.md(
                        "**Illustrative årsbeløp, ikke observerte norske skatteinntekter.** "
                        "Endring = sandkasse minus fast 2026-referanse for **samme** "
                        "antatte befolkning i hver rad; pluss betyr mer skatt i modellen. "
                        "Boligene er ca. 1,71 mill. rekonstruert fra Finansdepartementets "
                        "2026-figur (0–30 mill.) pluss valgt, **uobservert** antall over 30 mill. "
                        "(halvt i 30–40 mill., halvt i 40 mill.–valgt haletak). Jevn prisfordeling "
                        "innen hvert intervall; ingen boliger over taket er modellert."
                    ),
                    mo.ui.table(
                        pl.DataFrame(scenario_rows),
                        selection=None,
                        pagination=False,
                        show_column_summaries=False,
                        show_data_types=False,
                        show_search=False,
                        show_download=False,
                    ),
                    mo.md(
                        "**Alle vekter, eierskap og porteføljer er antakelser:** "
                        "Under 14 mill.: 80 % én eier, 10 % kvalifisert felles skatteenhet, "
                        "10 % to separate eiere. 14–30 mill.: 60/20/20 %; antatt hale: "
                        "50/25/25 %. Separate eiere har 50/50-andeler i startmiksen. "
                        "Annen formue/gjeld per *bolig* er 0/1,6 mill., 0,5/2 mill. "
                        "og 2/3 mill. i de tre prisgruppene, fordelt én gang på skatteenheter. "
                        "Et fellesfastsatt par er én skatteenhet; to separate eiere er to, "
                        "med hvert sitt personfradrag. Kvalifikasjon for fellesfastsetting "
                        "er forutsatt, ikke fastslått. Tabellen teller **boliger og antatte "
                        "skatteenheter**, ikke SSBs statistiske husholdninger."
                    ),
                    mo.md(
                        "De to «dyre boliger»-radene legger til henholdsvis 2 mill. "
                        "eiendeler eller 2 mill. gjeld per bolig ved verdi fra 14 mill.; "
                        "de endrer derfor **samlet antatt portefølje**, ikke bare samvariasjon. "
                        "25/75-raden beholder boligantall, enhetsmiks og samlet gjeld/eiendeler "
                        "per bolig, men flytter andeler mellom separate eiere. "
                        "Dette er navngitte sensitiviteter, **ikke** nedre/øvre statistiske "
                        "grenser eller konfidensintervall. Ukjent samvariasjon, virkelig "
                        "eierfordeling, verdier over haletaket, andre rabatter, særregler "
                        "og atferd mangler. "
                        "[Metode og kilder](https://github.com/MrAldrin/financial_dashboards/blob/main/docs/wealth_population_scenarios.md). "
                        "Offisielle anslag nedenfor og SSBs husholdningsreferanser er faste, "
                        "ikke tilpasset disse radene."
                    ),
                ]
            )
        }
    )
    return scenario_rows


@app.cell
def _():
    mo.md("""
    ### Offisielle scenarioer — faste, daterte referanser

    **Publiserte anslag, ikke resultater fra skyveknappene.** Minus betyr lavere
    skatteinntekter i kildens sammenligning. Beløpene er omtrentlige millioner kroner.

    | Kilde og dato | Endring og sammenligningsgrunnlag | Anslag |
    | :--- | :--- | ---: |
    | [Svar 1404, 12.02.2026](https://www.stortinget.no/globalassets/pdf/dokumentserien/2025-2026/dok15-202526-1404-vedlegg.pdf), s. 2 | Boliggrense 10 → 20 mill.; mot vedtatte 2026-regler, påløpt | −1 250 |
    | [Finansdepartementet, 27.02.2026](https://www.regjeringen.no/contentassets/27840e5ecb354f02a249f3cbd86b01d9/finmins-presentasjon-oppdatert-boligmodell-27.02.26.pdf), lysbilde 5 | Boliggrense 10 → 14 mill.; del av figur mot videreført 2025-system i 2026 | −730 |
    | [Prop. 95 LS, 12.05.2026](https://www.regjeringen.no/no/dokumenter/prop.-95-ls-20252026/id3159628/?ch=3), kap. 3, korrigert utgave 11.06.2026 | Boliggrense 10 → 14 mill.; isolert mot vedtatt budsjett, påløpt i 2026 | −830 |

    **Ikke samme regnestykke:** Appen bruker 14 mill. som referanse. En valgt
    10-millionersgrense går derfor motsatt vei av den offisielle lettelsen 10 → 14.
    Selv med snudd fortegn er fellesprofilen ikke en nasjonal modell. Vi kalibrerer
    ikke illustrasjonen til disse tallene. Forskjellen mellom februaranslaget
    −730 og maianslaget −830 er ikke avklart; de skal ikke summeres eller blandes.

    **Maianslaget i sammenheng:** Proposisjonen oppgir også +550 mill. fra oppdaterte
    modellanslag mot forutsetningene bak budsjettvedtaket. Sammen med tidligere
    vedtatte endringer gir pakken −280 mill. påløpt i 2026. Dette er ikke enda et
    isolert terskelanslag. Pakkens bokførte virkning i 2026 anslås til null, avhengig
    av endrede skattekort; bokført og påløpt er forskjellige størrelser.

    **Hvem gjelder 20-millionersanslaget?** Svar 1404 anslår om lag **114 600 personer**
    med lavere skatt, om lag **11 000 kr** i gjennomsnittlig lettelse og **1,72 mill. kr**
    i gjennomsnittlig bruttoinntekt blant de berørte. Dette er personer, ikke boliger
    eller husholdninger, og sier ikke hva en vilkårlig eier av en dyr bolig tjener.
    Avrundede gjennomsnitt og antall skal ikke tvinges til å gi nøyaktig proveny.
    Persondesilene i svaret kobles ikke til SSBs husholdningsdesiler nedenfor.

    Beregningen bruker LOTTE-Skatt med et 2023-utvalg framskrevet til 2026 og
    boligverdier fra skattekortene for 2026 (s. 5–6). Den inkluderer ikke
    atferdsendringer eller at flere kan dokumentere lavere boligverdi.
    Kildene beskriver daterte forslag/anslag, ikke dokumentasjon av dagens lovvedtak.
    """)
    return


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


@app.function
def illustrative_property_templates(
    lower: float, upper: float
) -> list[PropertyTemplate]:
    """Assumed price-conditional profiles from docs/wealth_population_scenarios.md.

    The tail is assumed, not observed. Input bins must not straddle 14m or 30m.
    Assets and debt are already allocated to each distinct tax unit.
    """
    if not all(isinstance(v, (int, float)) and isfinite(v) for v in (lower, upper)):
        raise ValueError("Finite property-bin edges required")
    if 0 <= lower < upper <= 14_000_000:
        weights, assets, debt = (0.8, 0.1, 0.1), 0, 1_600_000
    elif 14_000_000 <= lower < upper <= 30_000_000:
        weights, assets, debt = (0.6, 0.2, 0.2), 500_000, 2_000_000
    elif 30_000_000 <= lower < upper:
        weights, assets, debt = (0.5, 0.25, 0.25), 2_000_000, 3_000_000
    else:
        raise ValueError("Split bins at 14m and 30m before assigning profiles")
    full = dict(
        ownership_share=1.0,
        is_couple=False,
        mortgage_debt=debt,
        other_net_wealth=assets,
    )
    joint = {**full, "is_couple": True}
    half = {
        **full,
        "ownership_share": 0.5,
        "mortgage_debt": debt / 2,
        "other_net_wealth": assets / 2,
    }
    return [
        {"weight": weights[0], "units": [full]},
        {"weight": weights[1], "units": [joint]},
        {"weight": weights[2], "units": [half, half.copy()]},
    ]


@app.function
def illustrative_scenario_bins(
    housing_bins: list[dict], tail_count: float, tail_upper: float, variant: str
) -> list[PropertyScenarioBin]:
    """Keep property counts fixed while changing explicitly assumed unit profiles.

    The two expensive-home variants add holdings rather than exchange equal
    population marginals: they are sensitivity experiments, not correlation bounds.
    """
    if variant not in {"starting_mix", "high_assets", "high_debt", "uneven_owners"}:
        raise ValueError("Unknown illustrative scenario")
    if (
        not isinstance(tail_count, (int, float))
        or not isfinite(tail_count)
        or tail_count < 0
        or not isinstance(tail_upper, (int, float))
        or not isfinite(tail_upper)
        or tail_upper < 50_000_000
    ):
        raise ValueError("Invalid assumed tail")
    bins = [
        *housing_bins,
        {"lower": 30_000_000, "upper": 40_000_000, "count": tail_count / 2},
        {"lower": 40_000_000, "upper": tail_upper, "count": tail_count / 2},
    ]
    result: list[PropertyScenarioBin] = []
    for band in bins:
        templates = illustrative_property_templates(band["lower"], band["upper"])
        if variant in ("high_assets", "high_debt") and band["lower"] >= 14_000_000:
            # Add 2m per property, divided across separate units, never per owner.
            key = "other_net_wealth" if variant == "high_assets" else "mortgage_debt"
            for template in templates:
                for unit in template["units"]:
                    unit[key] += 2_000_000 / len(template["units"])
        if variant == "uneven_owners":
            separate = templates[2]["units"]
            for unit, share in zip(separate, (0.25, 0.75), strict=True):
                unit["ownership_share"] = share
                # Preserve property-level holdings, reallocating by owner share.
                unit["mortgage_debt"] *= 2 * share
                unit["other_net_wealth"] *= 2 * share
        result.append({**band, "templates": templates})
    return result


@app.function
def weighted_scenario_effect(
    bins: list[PropertyScenarioBin], policies: list[dict]
) -> dict[str, float]:
    """Exactly integrate assumed property templates, taxing each unit once.

    Uniform prices within each bin; extrema condition on within-bin placement.
    Both policies evaluate the SAME templates. Not an observed national estimate.
    """

    def nonnegative(value: object) -> bool:
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and isfinite(value)
            and value >= 0
        )

    if len(policies) != 2 or not bins:
        raise ValueError("Two policies and at least one property bin required")
    for band in bins:
        if (
            not isinstance(band, dict)
            or set(band) != {"lower", "upper", "count", "templates"}
            or not isinstance(band["templates"], list)
        ):
            raise ValueError("Property bins need edges, count and templates")
        for template in band["templates"]:
            if (
                not isinstance(template, dict)
                or set(template) != {"weight", "units"}
                or not isinstance(template["units"], list)
            ):
                raise ValueError("Templates need probability and tax units")
            for unit in template["units"]:
                if not isinstance(unit, dict) or set(unit) != {
                    "ownership_share",
                    "is_couple",
                    "mortgage_debt",
                    "other_net_wealth",
                }:
                    raise ValueError(
                        "Tax units need share, assessment, assets and debt"
                    )
    if any(
        not all(nonnegative(band[key]) for key in ("lower", "upper", "count"))
        for band in bins
    ):
        raise ValueError("Finite nonnegative property bins required")
    ordered = sorted(bins, key=lambda band: band["lower"])
    previous_upper = 0.0
    for band in ordered:
        lower, upper, count = (band[key] for key in ("lower", "upper", "count"))
        if (
            not all(nonnegative(v) for v in (lower, upper, count))
            or lower >= upper
            or lower < previous_upper
            or not band["templates"]
        ):
            raise ValueError("Finite, nonoverlapping property bins required")
        previous_upper = upper
        weights = []
        for template in band["templates"]:
            weight, units = template["weight"], template["units"]
            if not nonnegative(weight) or not units:
                raise ValueError("Each template needs a valid weight and units")
            weights.append(weight)
            shares = []
            for unit in units:
                share = unit["ownership_share"]
                if (
                    not nonnegative(share)
                    or share == 0
                    or share > 1
                    or not isinstance(unit["is_couple"], bool)
                    or not nonnegative(unit["mortgage_debt"])
                    or not nonnegative(unit["other_net_wealth"])
                ):
                    raise ValueError("Invalid or unsupported tax-unit profile")
                shares.append(share)
            if not abs(sum(shares) - 1) <= 1e-9:
                raise ValueError("Tax-unit shares must cover one property exactly")
        if not abs(sum(weights) - 1) <= 1e-9:
            raise ValueError("Template probabilities must sum to one per bin")

    result = dict(
        reference=0.0,
        reform=0.0,
        uniform=0.0,
        minimum=0.0,
        maximum=0.0,
        properties=0.0,
        tax_units=0.0,
    )
    for band in ordered:
        lower, upper, count = (band[key] for key in ("lower", "upper", "count"))
        result["properties"] += count
        for template in band["templates"]:
            weight = template["weight"]
            result["tax_units"] += count * weight * len(template["units"])
            # Each unit's calculator grid contains its own tier, allowance and
            # upper-band crossings. Union them before interpolating the sums.
            series = []
            points = {float(lower), float(upper)}
            for policy in policies:
                policy_series = []
                for unit in template["units"]:
                    frame = calculate_wealth_tax_df(
                        **policy,
                        **unit,
                        max_value=upper,
                        selected_value=lower,
                        extra_values=[lower, upper],
                    )
                    values = frame["market_value"].to_list()
                    taxes = frame["tax"].to_list()
                    points.update(v for v in values if lower <= v <= upper)
                    policy_series.append((values, taxes))
                series.append(policy_series)

            def tax_at(value: float, policy_series: list[tuple[list, list]]) -> float:
                total = 0.0
                for values, taxes in policy_series:
                    idx = min(bisect_right(values, value) - 1, len(values) - 2)
                    left, right = values[idx], values[idx + 1]
                    total += taxes[idx] + (taxes[idx + 1] - taxes[idx]) * (
                        value - left
                    ) / (right - left)
                return total

            grid = sorted(points)
            reference = [tax_at(v, series[0]) for v in grid]
            reform = [tax_at(v, series[1]) for v in grid]
            delta = [b - a for a, b in zip(reference, reform, strict=True)]
            factor = count * weight
            for name, values in (("reference", reference), ("reform", reform)):
                area = sum(
                    (grid[i + 1] - grid[i]) * (values[i] + values[i + 1]) / 2
                    for i in range(len(grid) - 1)
                )
                result[name] += factor * area / (upper - lower)
            result["minimum"] += factor * min(delta)
            result["maximum"] += factor * max(delta)
    result["uniform"] = result["reform"] - result["reference"]
    return result


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


@app.cell
def _():
    composition_group = mo.ui.dropdown(
        options=["Husholdningstype", "Alder på hovedinntektstaker"],
        value="Husholdningstype",
        label="Vis formue etter (SSB 2024)",
    )
    composition_group
    return (composition_group,)


@app.cell
def _(composition_group):
    by_age = composition_group.value == "Alder på hovedinntektstaker"
    composition_reference = (
        age_composition_reference() if by_age else household_composition_reference()
    )
    household_composition_chart = create_household_composition_chart(
        composition_reference
    )
    mo.vstack(
        [
            mo.md(f"""
        ### Formuens sammensetning etter {"alder på hovedinntektstaker" if by_age else "husholdningstype"} — 2024

        **Gjennomsnitt for alle husholdninger i hver type, også dem som ikke eier bolig.**
        Husholdningstype er ikke formuesrang. Dette er ikke typiske faktiske husholdninger.
        Eiendeler vises over null, **samlet gjeld** under null og publisert nettoformue
        som svart diamant. Gjeld er ikke bare boliglån; figuren viser ikke boligegenkapital.
        **Blandet verdsettelse:** SSB kombinerer beregnede markedsverdier og enkelte
        skatteverdier; dette er ikke kalkulatorens skattebase.
        Tallene er faste referanser og endres ikke av skattevalgene over.
        """),
            household_composition_chart,
            mo.md(f"""
        [SSB {composition_reference["table"]}](https://www.ssb.no/statbank/table/{composition_reference["table"]}), 2024, korrigert 12.02.2026;
        kildesnapshot 20.09.2026. Studenthusholdninger og aleneboende barn under 18 år
        er utelatt. Landstotalen på **2 616 826 husholdninger** er ikke en ekstra type.
        **Avrundede gjennomsnitt beholdes:** komponentenes sum kan avvike fra publisert
        nettoformue med opptil 100 kr. Hold pekeren over diamantene for avvik og antall.
        """),
            mo.accordion(
                {
                    "Definisjoner og begrensninger — statistiske husholdninger": mo.md("""
        Andre realaktiva = beregnet realkapital minus primærbolig minus sekundærbolig.
        Total realkapital stables derfor ikke i tillegg til delene.
        **Blandet verdsettelse:** bolig, næringseiendom, skog og gårdsbruk bruker
        beregnede markedsverdier; annen eiendom, driftsmidler og innbo kan ha skatteverdier.
        Våningshus på gårdsbruk inngår ikke i primærboligkomponenten.
        Finansformue følger SSBs statistiske definisjon før aktuelle verdsettingsrabatter,
        ikke kalkulatorens skattebase; enkelte eiendeler er ufullstendig verdsatt.
        Pensjonsrettigheter er utelatt. Gjeld er før skatterelaterte reduksjoner og
        inkluderer andeler av boligselskapenes gjeld.

        Par omfatter også samboere og er ikke automatisk én felles skatteenhet.
        Gruppemidlene lastes ikke inn i kalkulatoren eller brukes som nasjonale vekter:
        **skatt på gjennomsnittsformuen er ikke gjennomsnittlig skatt**.
        Aldersgruppene er definert ved **hovedinntektstakerens alder**, ikke alle
        beboeres alder; snitt fra ett år viser ikke en livsløpseffekt. Aldersgruppene
        kan ikke krysskobles med husholdningstyper eller formuesdesiler som om de var
        observerte personer. Kilden gir ikke fordelingen innad i gruppene eller bolig
        og gjeld etter formuesdesil.
        [SSBs definisjoner](https://www.ssb.no/inntekt-og-forbruk/inntekt-og-formue/statistikk/inntekts-og-formuesstatistikk-for-husholdninger).
        """)
                }
            ),
        ]
    )
    return (household_composition_chart,)


@app.function
def create_household_composition_chart(reference: dict) -> alt.LayerChart:
    """Display disjoint asset components, negative total debt and independent net wealth."""
    frame = pl.DataFrame(reference["groups"])
    components = {
        "primary_housing": "Primærbolig",
        "secondary_housing": "Sekundærbolig",
        "other_real_assets": "Andre realaktiva (beregnet)",
        "financial_assets": "Finansformue",
        "debt": "Samlet gjeld",
    }
    amounts = (
        frame.with_columns(debt=-pl.col("debt"))
        .unpivot(
            on=list(components),
            index=["code", "label"],
            variable_name="component",
            value_name="amount",
        )
        .with_columns(pl.col("component").replace_strict(components))
    )
    by_age = reference["table"] == "10317"
    x = alt.X(
        "label:N",
        sort=frame["label"].to_list(),
        title=(
            "Hovedinntektstakerens alder"
            if by_age
            else "Husholdningstype (SSBs rekkefølge, ikke formuesrang)"
        ),
        axis=alt.Axis(labelAngle=-45, labelLimit=280),
    )
    bars = (
        alt.Chart(amounts)
        .mark_bar()
        .encode(
            x=x,
            y=alt.Y(
                "amount:Q", stack="zero", title="Gjennomsnitt per husholdning (NOK)"
            ),
            color=alt.Color(
                "component:N",
                title="Komponent",
                scale=alt.Scale(
                    domain=list(components.values()),
                    range=["#0072b2", "#56b4e9", "#e69f00", "#009e73", "#999999"],
                ),
                legend=alt.Legend(orient="top", columns=3),
            ),
            tooltip=[
                alt.Tooltip("label:N", title="Husholdningstype"),
                alt.Tooltip("component:N", title="Komponent"),
                alt.Tooltip("amount:Q", title="NOK", format=",.0f"),
            ],
        )
    )
    markers = (
        alt.Chart(frame)
        .mark_point(shape="diamond", filled=True, color="#222", size=85)
        .encode(
            x=x,
            y="net_wealth:Q",
            tooltip=[
                alt.Tooltip("label:N", title="Husholdningstype"),
                alt.Tooltip(
                    "net_wealth:Q", title="Publisert nettoformue", format=",.0f"
                ),
                alt.Tooltip(
                    "households:Q", title="Antall husholdninger", format=",.0f"
                ),
                alt.Tooltip(
                    "accounting_difference:Q",
                    title="Komponentsum minus nettoformue (kr)",
                    format="+,.0f",
                ),
            ],
        )
    )
    zero = (
        alt.Chart(pl.DataFrame({"zero": [0]}))
        .mark_rule(color="#666")
        .encode(y="zero:Q")
    )
    return (bars + markers + zero).properties(
        width=950,
        height=300,
        title=(
            f"SSB {reference['table']}: {'alder' if by_age else 'husholdningstype'} — eiendeler, gjeld og nettoformue (2024)"
        ),
    )


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
def selected_tax_diagnostics(
    frame: pl.DataFrame, selected: float, policy: dict, household: dict
) -> dict:
    """Explain the selected unit's bill and exact one-sided linear slopes.

    The calculator inserts each valuation/allowance/upper-band kink in its grid;
    adjacent points therefore give local slopes, not sampled tax jumps.
    """
    rows = frame.sort("market_value").to_dicts()
    index = next(
        (i for i, row in enumerate(rows) if row["market_value"] == selected), None
    )
    if index is None:
        raise ValueError("Selected whole-home value must be in the tax grid")
    row = rows[index]
    multiplier = 2 if household["is_couple"] else 1
    allowance = policy["base_deduction"] * multiplier
    upper = 21_500_000 * multiplier
    regular = (
        min(max(row["net_wealth"] - allowance, 0), upper - allowance)
        * policy["tax_rate"]
        / 100
    )
    higher = max(row["net_wealth"] - upper, 0) * policy["upper_tax_rate"] / 100

    def marginal(neighbour: dict | None) -> float | None:
        if neighbour is None:
            return None
        return (
            (neighbour["tax"] - row["tax"])
            / (neighbour["market_value"] - selected)
            * 1_000_000
        )

    if abs(regular + higher - row["tax"]) > 1e-5:
        raise ValueError("Tax-band breakdown does not reproduce calculated tax")
    return {
        "Politikk": policy["scenario_name"],
        "Hel bolig (kr)": selected,
        "Skatteenhetens boligverdi (kr)": row["valuation"],
        "Andre eiendeler (kr)": household["other_net_wealth"],
        "Gjeld (kr)": household["mortgage_debt"],
        "Netto skatteformue før fradrag (kr)": row["net_wealth"],
        "Personfradrag (kr)": allowance,
        "Grunnlag før nullgulv (kr)": row["tax_base"],
        "Ordinært bånd (kr/år)": regular,
        "Øvre bånd (kr/år)": higher,
        "Skatt (kr/år)": row["tax"],
        "Venstre marginal (kr per +1 mill.)": marginal(
            rows[index - 1] if index else None
        ),
        "Høyre marginal (kr per +1 mill.)": marginal(
            rows[index + 1] if index + 1 < len(rows) else None
        ),
    }


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
    ownership_share: float = 1.0,
) -> pl.DataFrame:
    """Allocate whole-primary-home valuation to one tax unit before taxation.

    Joint assessment doubles the allowance and upper tax threshold, not the
    whole-property valuation tier. Mixed discounted assets are outside scope.
    Assets/debt/income already belong to that unit and are never share-scaled.
    Rates are percentages; upper_threshold is BEFORE the personal allowance.
    """
    numeric_inputs = [
        base_deduction,
        tax_rate,
        upper_tax_rate,
        upper_threshold,
        mortgage_debt,
        other_net_wealth,
        annual_income,
        selected_value,
        max_value,
        ownership_share,
        *(extra_values or []),
        *(t["rate"] for t in tiers),
        *(t["limit"] for t in tiers if t["limit"] is not None),
    ]
    if (
        not isinstance(is_couple, bool)
        or any(
            not isinstance(v, (int, float)) or not isfinite(v) for v in numeric_inputs
        )
        or not 0 <= ownership_share <= 1
        or any(v < 0 for v in (extra_values or []))
    ):
        raise ValueError(
            "Finite numeric inputs, boolean assessment and share in [0, 1] required"
        )
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
            tiers, target - other_net_wealth + mortgage_debt, ownership_share
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
    # Apply progressive tiers to the whole property, THEN allocate its value.
    df = df.with_columns(
        whole_home_valuation=valuation_expr,
        valuation=valuation_expr * ownership_share,
        owned_market_value=pl.col("market_value") * ownership_share,
    )
    df = df.with_columns(
        net_wealth=pl.col("valuation") + other_net_wealth - mortgage_debt
    )
    actual_base_ded = base_deduction * 2 if is_couple else base_deduction
    df = df.with_columns(
        tax_base=pl.col("net_wealth") - actual_base_ded,
        economic_wealth=pl.col("owned_market_value") + other_net_wealth - mortgage_debt,
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
def home_value_at_tax_wealth(
    tiers: list[dict], target: float, ownership_share: float = 1.0
) -> float | None:
    """Invert allocated valuation into whole-home value; None means unreachable."""
    if (
        not isfinite(ownership_share)
        or not 0 <= ownership_share <= 1
        or not isfinite(target)
    ):
        raise ValueError("Finite target and ownership share in [0, 1] required")
    if target <= 0:
        return 0.0
    if ownership_share == 0:
        return None
    target /= ownership_share
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


# BEGIN GENERATED HOUSEHOLD COMPOSITION
@app.function
def household_composition_reference() -> dict:
    """Public aggregates; generated offline by scripts/build_wealth_reference.py."""
    return {
        "schema_version": 1,
        "snapshot": "2026-09-20-feasibility",
        "table": "10316",
        "year": 2024,
        "updated": "2026-02-12T07:00:00Z",
        "national": {
            "code": "50",
            "label": "Alle hushald",
            "primary_housing": 3151100,
            "secondary_housing": 349000,
            "real_assets": 3797700,
            "financial_assets": 1850000,
            "debt": 1757300,
            "net_wealth": 3890400,
            "households": 2616826,
            "other_real_assets": 297600,
            "accounting_difference": 0,
        },
        "groups": [
            {
                "code": "51",
                "label": "Aleinebuande under 30 år",
                "primary_housing": 929000,
                "secondary_housing": 76400,
                "real_assets": 1044500,
                "financial_assets": 408600,
                "debt": 886400,
                "net_wealth": 566700,
                "households": 181197,
                "other_real_assets": 39100,
                "accounting_difference": 0,
            },
            {
                "code": "52",
                "label": "Aleinebuande 30-44 år",
                "primary_housing": 1538300,
                "secondary_housing": 134900,
                "real_assets": 1746900,
                "financial_assets": 550900,
                "debt": 1179100,
                "net_wealth": 1118700,
                "households": 248128,
                "other_real_assets": 73700,
                "accounting_difference": 0,
            },
            {
                "code": "53",
                "label": "Aleinebuande 45-66 år",
                "primary_housing": 2179500,
                "secondary_housing": 228700,
                "real_assets": 2573900,
                "financial_assets": 1222000,
                "debt": 982600,
                "net_wealth": 2813300,
                "households": 350143,
                "other_real_assets": 165700,
                "accounting_difference": 0,
            },
            {
                "code": "54",
                "label": "Aleinebuande 67 år og eldre",
                "primary_housing": 2810000,
                "secondary_housing": 184900,
                "real_assets": 3133900,
                "financial_assets": 1430600,
                "debt": 434300,
                "net_wealth": 4130200,
                "households": 324621,
                "other_real_assets": 139000,
                "accounting_difference": 0,
            },
            {
                "code": "55",
                "label": "Par utan barn, eldste person under 30 år",
                "primary_housing": 2219600,
                "secondary_housing": 166400,
                "real_assets": 2489400,
                "financial_assets": 902700,
                "debt": 2376500,
                "net_wealth": 1015700,
                "households": 52128,
                "other_real_assets": 103400,
                "accounting_difference": -100,
            },
            {
                "code": "56",
                "label": "Par utan barn, eldste person 30-44 år",
                "primary_housing": 3214700,
                "secondary_housing": 306500,
                "real_assets": 3680600,
                "financial_assets": 1388100,
                "debt": 2930600,
                "net_wealth": 2138100,
                "households": 78801,
                "other_real_assets": 159400,
                "accounting_difference": 0,
            },
            {
                "code": "57",
                "label": "Par utan barn, eldste person 45-66 år",
                "primary_housing": 4157000,
                "secondary_housing": 645200,
                "real_assets": 5433100,
                "financial_assets": 3219200,
                "debt": 2146600,
                "net_wealth": 6505700,
                "households": 210383,
                "other_real_assets": 630900,
                "accounting_difference": 0,
            },
            {
                "code": "58",
                "label": "Par utan barn, eldste person 67 år og eldre",
                "primary_housing": 4136700,
                "secondary_housing": 491100,
                "real_assets": 5099500,
                "financial_assets": 3299200,
                "debt": 822300,
                "net_wealth": 7576400,
                "households": 287837,
                "other_real_assets": 471700,
                "accounting_difference": 0,
            },
            {
                "code": "59",
                "label": "Par med barn 0-5 år",
                "primary_housing": 4211300,
                "secondary_housing": 389100,
                "real_assets": 4917800,
                "financial_assets": 1656800,
                "debt": 3789600,
                "net_wealth": 2785000,
                "households": 215525,
                "other_real_assets": 317400,
                "accounting_difference": 0,
            },
            {
                "code": "60",
                "label": "Par med barn 6-17 år",
                "primary_housing": 4771000,
                "secondary_housing": 531400,
                "real_assets": 5816500,
                "financial_assets": 2698900,
                "debt": 3477600,
                "net_wealth": 5037800,
                "households": 269166,
                "other_real_assets": 514100,
                "accounting_difference": 0,
            },
            {
                "code": "61",
                "label": "Par med barn 18 år og eldre",
                "primary_housing": 4725800,
                "secondary_housing": 769500,
                "real_assets": 6180500,
                "financial_assets": 4110500,
                "debt": 2808600,
                "net_wealth": 7482300,
                "households": 124522,
                "other_real_assets": 685200,
                "accounting_difference": 100,
            },
            {
                "code": "62",
                "label": "Einsleg mor/far med barn 0-5 år",
                "primary_housing": 1643300,
                "secondary_housing": 156800,
                "real_assets": 1887400,
                "financial_assets": 441000,
                "debt": 1342200,
                "net_wealth": 986200,
                "households": 21498,
                "other_real_assets": 87300,
                "accounting_difference": 0,
            },
            {
                "code": "63",
                "label": "Einsleg mor/far med barn 6-17 år",
                "primary_housing": 2643800,
                "secondary_housing": 189300,
                "real_assets": 2977700,
                "financial_assets": 883000,
                "debt": 1740000,
                "net_wealth": 2120700,
                "households": 86703,
                "other_real_assets": 144600,
                "accounting_difference": 0,
            },
            {
                "code": "64",
                "label": "Einsleg mor/far med barn 18 år og eldre",
                "primary_housing": 3232200,
                "secondary_housing": 308900,
                "real_assets": 3798200,
                "financial_assets": 1501800,
                "debt": 1593600,
                "net_wealth": 3706300,
                "households": 68351,
                "other_real_assets": 257100,
                "accounting_difference": 100,
            },
            {
                "code": "65",
                "label": "Fleirfamiliehushald",
                "primary_housing": 3275100,
                "secondary_housing": 534700,
                "real_assets": 4215800,
                "financial_assets": 1746400,
                "debt": 2309800,
                "net_wealth": 3652400,
                "households": 97823,
                "other_real_assets": 406000,
                "accounting_difference": 0,
            },
        ],
    }


# END GENERATED HOUSEHOLD COMPOSITION


# BEGIN GENERATED AGE COMPOSITION
@app.function
def age_composition_reference() -> dict:
    """Public aggregates; generated offline by scripts/build_wealth_reference.py."""
    return {
        "schema_version": 1,
        "snapshot": "2026-09-20-feasibility",
        "table": "10317",
        "year": 2024,
        "updated": "2026-02-12T07:00:00Z",
        "national": {
            "code": "999D",
            "label": "Alle aldre",
            "primary_housing": 3151100,
            "secondary_housing": 349000,
            "real_assets": 3797700,
            "financial_assets": 1850000,
            "debt": 1757300,
            "net_wealth": 3890400,
            "households": 2616826,
            "other_real_assets": 297600,
            "accounting_difference": 0,
        },
        "groups": [
            {
                "code": "-24",
                "label": "Under 25 år",
                "primary_housing": 839500,
                "secondary_housing": 82100,
                "real_assets": 994400,
                "financial_assets": 502500,
                "debt": 807900,
                "net_wealth": 689000,
                "households": 95261,
                "other_real_assets": 72800,
                "accounting_difference": 0,
            },
            {
                "code": "25-34",
                "label": "25-34 år",
                "primary_housing": 2198500,
                "secondary_housing": 193500,
                "real_assets": 2521900,
                "financial_assets": 916700,
                "debt": 2087500,
                "net_wealth": 1351000,
                "households": 449137,
                "other_real_assets": 129900,
                "accounting_difference": 100,
            },
            {
                "code": "35-44",
                "label": "35-44 år",
                "primary_housing": 3175100,
                "secondary_housing": 296100,
                "real_assets": 3717000,
                "financial_assets": 1236200,
                "debt": 2575500,
                "net_wealth": 2377700,
                "households": 471027,
                "other_real_assets": 245800,
                "accounting_difference": 0,
            },
            {
                "code": "45-54",
                "label": "45-54 år",
                "primary_housing": 3592800,
                "secondary_housing": 435300,
                "real_assets": 4409400,
                "financial_assets": 2081100,
                "debt": 2404200,
                "net_wealth": 4086300,
                "households": 463879,
                "other_real_assets": 381300,
                "accounting_difference": 0,
            },
            {
                "code": "55-66",
                "label": "55-66 år",
                "primary_housing": 3634300,
                "secondary_housing": 518600,
                "real_assets": 4610800,
                "financial_assets": 2661500,
                "debt": 1659800,
                "net_wealth": 5612500,
                "households": 527130,
                "other_real_assets": 457900,
                "accounting_difference": 0,
            },
            {
                "code": "67-79",
                "label": "67-79 år",
                "primary_housing": 3557700,
                "secondary_housing": 396800,
                "real_assets": 4316400,
                "financial_assets": 2575800,
                "debt": 754800,
                "net_wealth": 6137400,
                "households": 414257,
                "other_real_assets": 361900,
                "accounting_difference": 0,
            },
            {
                "code": "80+",
                "label": "80 år eller eldre",
                "primary_housing": 3195100,
                "secondary_housing": 201100,
                "real_assets": 3546600,
                "financial_assets": 1855800,
                "debt": 346500,
                "net_wealth": 5055900,
                "households": 196135,
                "other_real_assets": 150400,
                "accounting_difference": 0,
            },
        ],
    }


# END GENERATED AGE COMPOSITION


if __name__ == "__main__":
    app.run()
