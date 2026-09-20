# Research plan: Norwegian housing wealth, tax incidence, and public revenue

**Status:** Research and design proposal; implementation requires separate approval.  
**Initial source review:** 20 September 2026.  
**Target app:** `apps/building_taxation.py`.  
**Scope:** Primary-residence wealth taxation first. Secondary residences and municipal property tax are separate extensions.

## 1. Purpose and recommendation

Turn the current hypothetical-household calculator into an evidence-led dashboard answering:

1. **How unusual is this home's value, and how wealthy is its household?**
2. **Who pays more or less under a proposed tax rule, and by how much?**
3. **What is the annual effect on public tax revenue, relative to a clearly defined alternative?**
4. **How often does high housing wealth coexist with low income or few liquid assets?**

The dashboard should test claims about “ordinary homeowners” with distributions, not replace anecdotes with other anecdotes. Expensive housing, net wealth, income, and ability to pay are different quantities. Show them alongside one another rather than selecting a single definition of “rich.”

**Recommended sequence:** establish correct rules and comparisons; ship a public-data explanation and household calculator; obtain existing official distribution/revenue estimates; only then decide whether the available data justify a continuously adjustable national simulator.

A useful first release does **not** require a fabricated Norwegian population. Conversely, a smooth slider does not make an unsupported national estimate reliable.

## 2. Findings from the initial research

### 2.1 What actually changed

- The relevant threshold moved from **NOK 10 million to NOK 14 million**, not 40 million. NOK 40 million can still be a useful hypothetical scenario.
- The primary home's taxable valuation is **25% below the threshold and 70% on the excess**. These are discounts of **75% and 30%**, respectively. Crossing the threshold does not revalue the whole home at 70%.
- SSB's revised housing model uses smaller geographical areas based on *grunnkretser*, rather than the previous municipality-based structure. SSB describes improved predictive accuracy, not perfect individual valuations. [S3, S15]
- Higher estimated home values could increase **tax receipts**; this was not itself additional government spending. Raising the threshold reduces receipts relative to keeping the lower threshold.
- Government stated that the model transition should not raise aggregate revenue. It increased the general wealth-tax allowance and subsequently proposed increasing the housing threshold. Revenue neutrality does not mean that every individual is unaffected. [S2, S4]
- Skatteetaten's current 2026 rate page now lists the NOK 14 million threshold. Archive the enacted legal provision and effective date before implementing a legal preset; the February and May announcements were still proposals when published. [S1]

### 2.2 Verified 2026 baseline for further legal checking

| Component | Current published 2026 figure | Important qualification |
|---|---:|---|
| Primary-home threshold | NOK 14,000,000 | Whole-property valuation and ownership allocation must be checked explicitly |
| Taxable fraction below / above threshold | 25% / 70% | Apply progressively to portions of value |
| Personal wealth-tax allowance | NOK 1,900,000 | Doubled for qualifying jointly assessed couples, not every household of two adults |
| Standard combined wealth-tax rate | 1.0% | Published municipal rate 0.35% + state rate 0.65%; check municipal exceptions |
| Upper combined rate | 1.1% | On net taxable wealth above NOK 21,500,000 before subtracting the allowance; threshold doubles for qualifying joint assessment |
| Secondary-home taxable fraction | 100% | Remains in other-assets/background data even while its policy controls are deferred |

Do not confuse the NOK 14 million **housing valuation threshold** with the NOK 1.9 million **personal allowance** or NOK 21.5 million **upper wealth-tax threshold**. [S1]

### 2.3 Existing evidence directly relevant to the dashboard

**Housing rarity:** The Finance Ministry reported that approximately **98% of primary residences** would be valued entirely at 25% under the NOK 14 million threshold. Its 27 February presentation includes a primary-home value histogram in million-kroner bands and says about 2% of primary homes in the tax-card data were above NOK 14 million. This is a statement about **properties**, not the richest 2% of people. Request the underlying numbers, including the tail beyond the plotted range. [S2, S5]

**The model change:** SSB's corrected 23 January analysis estimates an isolated **NOK 973 million increase** in annual wealth-tax receipts from the revised valuation model. It reports 318,700 people with increased tax, 229,400 with reduced tax, and 4,107,600 in the approximately unchanged category. The latter corresponds to the article's -200 to +199 kroner band; it is not necessarily exact zero. These are model estimates for people aged 17+, using 2023 data projected to 2026, not final 2026 tax outcomes. Documented downward valuation corrections are not incorporated. [S3]

**The actual threshold proposal:** The corrected May budget proposition estimates that increasing the threshold from 10 to 14 million reduces annual accrued receipts by approximately **NOK 830 million**, relative to the stated adopted-budget comparison. With the updated housing-model estimates and other already adopted wealth-tax changes, it reports a combined **NOK 280 million revenue loss** relative to its budget reference. Accrued annual effects and cash booked in a particular year differ. [S4]

**Important source-version conflict to reconcile:** The February presentation showed **NOK 730 million**, not 830 million, for the threshold measure, within a comparison against continuation of the 2025 system into 2026. Keep both as dated estimates until the definition/vintage difference is resolved. Do not simply add or subtract the January, February, and May headline figures. [S3–S5]

**A particularly valuable distributional source:** In the Finance Minister's answer of 12 February to written question 1404, the **10-to-20-million proposal** is estimated to:

- Reduce annual receipts by NOK 1.25 billion.
- Benefit approximately 114,600 people, averaging about NOK 11,000 in tax relief.
- Benefit a group with **average gross annual income of about NOK 1.72 million**.
- Concentrate the reported relief strongly toward the top of the net-wealth distribution.

The answer contains seven tables covering income bands, income deciles/top percentiles, net-wealth bands/deciles/top percentiles, and centrality classes. This is already much closer to the intended dashboard than an invented log-normal house-price distribution. However:

- It concerns **20 million, not 14 million**.
- Its units are people, not households; income is gross income, not salary or disposable income.
- Means do not describe every beneficiary.
- Values are rounded: a reported zero group-average change does not prove nobody in that group benefits.
- Centrality class S01 includes Oslo, Lørenskog, Lillestrøm, Rælingen, and Bærum; it must not be relabelled “Oslo/Bærum/Asker.”
- The model uses 2023 records projected to 2026, updated with tax-card housing values, without behavioural responses or subsequent documented valuation reductions. [S6]

### 2.4 “How wealthy?” can already be partly answered with public data

SSB table **10318** publishes actual lower net-wealth cutoffs, not just decile averages. A live API extraction for 2024 returned:

| Household position | Lower cutoff, calculated net wealth |
|---|---:|
| Upper half | NOK 1,955,700 |
| Top 10% | NOK 8,454,200 |
| Top 5% | NOK 12,140,200 |
| Top 1% | NOK 28,250,400 |
| Top 0.1% | NOK 133,425,400 |

Population: households excluding student households. Values reflect SSB's wealth definition and the February 2026 correction. Pension entitlements are excluded; some assets are imperfectly valued. [S7, S8]

For illustration, **a household owning an entire NOK 14 million home, with no debt or other assets**, would lie between the published top-5% and top-1% thresholds when compared on a consistent 2024 valuation basis. Add NOK 3 million of debt and the resulting NOK 11 million net wealth lies between the top-10% and top-5% cutoffs. These are assumptions, not descriptions of actual owners of such homes.

This enables an honest dynamic statement such as “your specified household is in the top 5–10% bracket using 2024 reference data.” It does **not** justify “owners of 14-million homes are always in the top 5%,” or an invented exact rank such as “96.7th percentile.” A current-price input also needs a visible reference-year warning or an explicitly documented revaluation assumption.

## 3. Audit of the current app and earlier plans

### Useful foundations

- Marimo reactive controls, Polars calculations, and Altair charts already exist.
- Progressive, customisable valuation tiers are already implemented.
- Personal debt, other net wealth, and joint-assessment inputs provide a starting point.
- The current hardcoded comparison uses the now-published 14-million / 25%-70% baseline.

### Gaps that matter to the intended purpose

1. `calculate_wealth_tax_df` generates a house-value grid from zero to NOK 30 million. It is **not a dataset of Norwegian homes or taxpayers**.
2. The same hypothetical debt and other wealth are applied at every point. This is legitimate for a controlled example, not for population totals.
3. There is no selected-home value, population weight, income, liquidity, ownership share, or economic net-wealth ranking.
4. The tax engine applies one flat rate; it omits the higher tax band and municipal variation.
5. “Annen nettoformue” is not enough to recover both economic wealth and taxable wealth, or asset-dependent debt deductions. It also risks debt double-counting unless precisely defined.
6. “Dagens regelverk” has no tax year, source, effective date, or explicit assumptions.
7. The initial sandbox is 12 million / 30%-75%, rather than an explained policy alternative or a copy of the baseline.
8. The chart cannot show a NOK 40 million example. Chart extent should be adjustable and include policy breakpoints exactly, not only coarse grid points.
9. There is no dedicated display of tax differences, beneficiaries, statistical context, or uncertainty.

### Earlier planning assumptions to replace, not silently perpetuate

`plans/norwegian_taxation_dashboard_improvements.md` proposes unsourced population counts, housing-price averages, budget numbers, and a log-normal housing distribution. Treat these as **unverified placeholders**, not research findings.

- A house-price distribution alone cannot produce credible wealth-tax receipts: liabilities depend jointly on debt, other assets, ownership, and allowances.
- Total dwellings, primary residences, owner households, owners, and taxpayers are not interchangeable counts.
- A single log-normal curve can fit the middle and still miss the expensive tail that drives this question.
- “Housing wealth-tax revenue” has no unique standalone official meaning within a tax on total net wealth. Prefer the **change in total wealth-tax receipts caused by changing primary-housing rules**.
- The older `norwegian_building_tax.md` labels 14 million as a 2024/2025 rule and combines thresholds from different years. Its legal assumptions need replacement if implementation is approved.
- Do not portray borrowing with a fixed house value as a costless way to avoid tax. Borrowed money must go somewhere, and interest, asset purchases, retained cash, and economic net wealth must be accounted for.
- “X nurses” based only on salaries understates employment costs. Budget equivalents are optional context, not proof of social benefit or actual spending commitments.

This research plan proposes replacing those assumptions; it does not modify the older files or approve implementation.

## 4. Research workstreams

### A. Policy history, legal rules, and debate claims — highest priority

**Questions**

- What changed in the valuation method, housing threshold, personal allowance, and tax rates, and when?
- Which comparisons isolate the housing model, the housing threshold, or the whole budget package?
- Which criticisms concern valuation error, distributional fairness, cash-flow difficulty, geographic concentration, or predictability?
- Which changes were announced, proposed, adopted, and subsequently corrected?

**Tasks**

1. Build a dated timeline from the 2021 request, the 2025 budget process, the January 2026 revised estimates, February proposals, and final 2026 legislation.
2. Archive Skatteetaten's year-specific rates, applicable law and parliamentary adoption, ownership rules, debt-allocation guidance, and official worked examples.
3. Extract the January SSB analysis, February presentation, parliamentary question 1404 tables, and May budget estimate with source dates and comparison definitions.
4. Look for the equivalent distribution tables for **10 to 14 million**; request them if unpublished.
5. Maintain a claims ledger: claim, speaker, date, evidence, correct unit, supported/unsupported/uncertain, and what data could resolve it.
6. Review a small balanced set of reporting and stakeholder statements for the debate's framing. Use these to identify questions; use primary statistical/legal sources for numerical claims.

Initial contrasting frames are documented in the government's fairness/revenue-neutrality explanation and Høyre's predictability/ordinary-income-homeowner argument. The latter proposed a 20-million threshold and is a political argument, not independent evidence about how typical beneficiaries are. [S2, S9]

**Deliverable:** source-backed policy timeline, legal parameter sheet, comparison matrix, and claims ledger.

### B. Public-data inventory and reproducible extraction

The following table metadata were checked live during the initial review:

| SSB table/source | What it supplies | Appropriate use | What it does not establish |
|---|---|---|---|
| [10315](https://www.ssb.no/statbank/table/10315) | Household wealth components, sums, shares with amounts, means among those with amounts | Aggregate wealth/debt checks | Joint household portfolios or housing-value distribution |
| [10316](https://www.ssb.no/statbank/table/10316) | Wealth accounts by household type | Household context and calibration | Individual household records |
| [10317](https://www.ssb.no/statbank/table/10317) | Wealth accounts by main earner's age | Age comparisons | Conditional income/liquidity of expensive-home owners |
| [10318](https://www.ssb.no/statbank/table/10318) | Net-wealth shares, means, lower decile/top-group cutoffs, counts | Defensible national household wealth brackets | Exact continuous percentiles or home-price percentiles |
| [08564](https://www.ssb.no/statbank/table/08564) | State and municipal wealth tax amounts and taxpayer counts | Validate historical receipts and counts using consistent populations | Revenue attributable uniquely to primary housing |
| [08603](https://www.ssb.no/statbank/table/08603) | Income, taxable wealth, debt and tax aggregates by region | Regional consistency checks | Linked portfolios |
| [08815](https://www.ssb.no/statbank/table/08815) | Taxable wealth components, debt, wealth-tax totals/counts | Tax-system calibration | Undiscounted home values or joint distributions |
| [14781](https://www.ssb.no/statbank/table/14781) | Preliminary 2024/2025 taxable housing wealth by region, age, sex, population; means/medians | More recent regional/age context | Full market-value home prices; independent property counts |
| February presentation, slides 8–11 | Primary-home value histogram and above-14-million share | Housing rarity and data-request starting point | Reliable raw bin counts merely from the PDF plot |
| Written question 1404 | Official fixed-scenario distribution and revenue estimates | “Who benefits?” for the 20-million proposal | Arbitrary slider scenarios |

**Extraction protocol**

- Prefer SSB's current PxWebApi v2 for implementation. The initial metadata checks and table 10318 numerical spot-check used the still-working legacy endpoint; that is not a proposed permanent dependency. [S10]
- Record table ID, exact query and category codes, response metadata, extraction date, units, population exclusions, year, revisions, and source URL.
- Preserve immutable raw responses and derived small datasets; record transformations and checksums.
- Do not interpret suppressed/missing values as zero.
- Distinguish a mean over all households from a mean among households with a nonzero amount.
- Never recover a mean market value by simply dividing mean taxable housing wealth by 0.25: progressive tiers and ownership make that invalid.
- Check overlap and denominator definitions before joining or comparing tables.
- Keep 2024 final observations, 2025 preliminary figures, and 2026 projections distinct. The revised valuation model can create a methodological break, not just house-price inflation.

**Deliverable:** source registry and feasibility matrix: available now, needs clarification, requestable, restricted, or unavailable.

### C. Obtain the missing linked information

Start with **existing analyses and their underlying public aggregates**, not a large bespoke data order.

1. Ask the Finance Ministry/Skatteetaten for the numeric dataset behind the February primary-home histogram, including bin definitions, counts above 30 million, valuation vintage, and the unit of observation.
2. Ask for the underlying 10-to-14-million distribution tables and any later revisions, alongside comparable 10-to-20-million estimates.
3. Check existing SSB commissioned tables through eInnsyn. SSB says delivered commissioned tables are publicly available and can be requested free; a new custom order has a quoted cost and delivery time. [S11]
4. Request a quote only after checking whether existing material answers the key questions. Do not place a paid order without user approval.

**Minimum requested outputs, subject to feasibility and disclosure controls**

- Home-value bands: below 2m, 2–4m, 4–6m, 6–8m, 8–10m, 10–12m, 12–14m, 14–16m, 16–20m, 20–30m, 30–40m, and 40m+; finer bins near policy thresholds if feasible.
- Separate counts of properties, owner households, and affected taxpayers where available, with ownership-share definitions.
- Conditional distributions of household economic net wealth, gross/disposable income, liquid assets, debt, and taxable net wealth within housing-value bands.
- Taxpayer counts and total liability under a specified baseline and named alternatives, preferably by baseline net-wealth decile, income group, age/household type, and broad region.
- For isolating the valuation-model change: paired old/new valuations on a comparable underlying population, or official matched scenario outputs. A uniform percentage uplift is not an adequate substitute.

Do not ask for every dimension in one enormous cross-tab. Begin nationally, then request separate income, wealth, age, and regional breakdowns. Tail suppression and cost are likely constraints. Means within housing bands are useful descriptions but **not sufficient inputs for exact nonlinear tax calculations**.

**Draft initial request, not sent:**

> Vi utvikler et offentlig tilgjengelig visualiseringsverktøy om primærbolig og formuesskatt. Vi ønsker først å avklare hvilke eksisterende, anonyme tabeller som kan gjenbrukes, før vi eventuelt bestiller et tabelloppdrag.
>
> Finnes tallgrunnlaget bak fordelingen av primærboliger etter beregnet markedsverdi i Finansdepartementets presentasjon 27. februar 2026, og fordelingsberegninger for å heve verdsettingsgrensen fra 10 til 14 millioner kroner? Vi er særlig interessert i antall berørte, proveny og fordeling etter beregnet nettoformue, inntekt, alder og husholdningstype. Beregningene i svaret på skriftlig spørsmål 1404 (2025–2026), om 10 til 20 millioner, er et relevant utgangspunkt.
>
> Kan dere opplyse om populasjon, enhet (bolig/person/husholdning), verdsettingsår/-modell, sammenligningsgrunnlag, avrunding/usikkerhet og vilkår for viderepublisering? Dersom eksisterende tabeller ikke er tilstrekkelige, ønsker vi en uforpliktende avklaring av mulige anonyme krysstabeller og et pristilbud før eventuell bestilling.

**Access boundary:** public Statbank tables are not downloadable linked tax returns. SSB microdata access is restricted to eligible organisations/purposes, and microdata.no requires an institutional agreement; underlying records stay on its platform. A public browser app must never contain confidential records or credentials. A collaboration could produce approved aggregates, but access and publication rights cannot be assumed. [S12, S13]

**Deliverable:** data-request specification, inventory of existing tables, access/cost assessment, and recommendation to proceed or stop.

## 5. Method: what can legitimately update when a slider moves?

### 5.1 Maintain three evidence levels

| Level | Contents | Behaviour when controls change |
|---|---|---|
| Observed / published reference | SSB wealth cutoffs and housing counts | Highlight the selected position; do not alter underlying observations |
| Official scenario estimate | Published LOTTE-Skatt results for a defined reform | Display only for matching presets and label vintage/baseline |
| Dashboard calculation/model | A specified household, or approved weighted population model | Recalculate within its documented supported scope |

A fixed official estimate must not appear to be a live calculation. On leaving a supported preset, show “national estimate unavailable for these settings” unless there is a validated population model.

### 5.2 Household calculation: economic wealth and tax wealth are separate

For a simplified full-owner example, primary-home taxable value is:

**F(V, L) = 0.25 × min(V, L) + 0.70 × max(V − L, 0).**

For other selected rates, substitute the appropriate fractions; advanced mode can retain multiple progressive tiers.

Calculate separately:

- **Economic net wealth:** household asset values using the statistical reference definitions, less economic debt, before tax discounts.
- **Taxable net wealth:** tax values of relevant assets less legally deductible debt.
- **Wealth-tax liability:** municipal and state schedules applied to the appropriate person/joint tax unit.
- **Liquidity context:** accessible financial assets and annual tax relative to disposable income, if supplied; not a complete household affordability assessment.

Ownership and tax-unit rules precede household aggregation. Do not split a whole property's threshold independently among owners without verifying the allocation rule. Ordinary cohabitants are not automatically treated like jointly assessed spouses.

Primary-home debt does not generally receive the same reduction as debt allocated to discounted shares. The current simple debt subtraction is not a complete mixed-asset tax engine. Verify and test the statutory allocation rules; either support the required asset breakdown or explicitly restrict the simplified calculator. [S14]

For the upper band, distinguish net taxable wealth before the allowance from the taxable amount after it. The NOK 21.5 million threshold must not be shifted upward by subtracting the allowance twice.

**Useful worked comparison:** holding values, debt, other assets and 2026 tax parameters fixed, a single full owner of a NOK 12 million primary home with no debt or other assets pays NOK 20,000 with a 10-million threshold versus NOK 11,000 with a 14-million threshold: a NOK 9,000 annual difference. This is a calculation for an explicitly specified household, not an average beneficiary.

Above NOK 14 million, raising the threshold from 10 to 14 million lowers the property's taxable value by NOK 1.8 million. Actual tax savings depend on ownership, allowances, debt, and tax bands; they are not automatically NOK 18,000 for every owner.

### 5.3 Dynamic wealth context

- Household assets/debt controls update economic net wealth and its published bracket.
- A home-value histogram, if obtained, updates the property's highlighted bin and share above the selected value; disclose within-bin uncertainty.
- Policy sliders update tax liabilities and affected groups, **not pre-tax wealth ranks** in a static model.
- Switching the peer group changes the reference population visibly. Do not claim age- or municipality-specific percentiles from tables that publish only group means.
- If only broad bins exist, show a bracket or bound. Interpolation is a modelling assumption and must not masquerade as observed precision.
- Do not infer what owners of a certain-priced home typically earn from unrelated national income averages.

### 5.4 National revenue: sum taxes, not average homes

For weighted tax units, the static annual effect is:

**ΔR = Σ weightᵢ × [taxᵢ(custom policy) − taxᵢ(baseline policy)].**

Calculate tax per legal tax unit first; aggregate to households for distributional presentation afterward. Preserve relevant ownership, asset, debt, and assessment relationships.

Tax on an average portfolio is generally not average tax on the population: allowances, tax brackets, and housing tiers are nonlinear. Matching national means independently cannot recover the missing correlations.

Keep ranks fixed at baseline when reporting who benefits, so a policy does not change the classification used to evaluate it. Distinguish all households, homeowners, wealth-tax payers, and beneficiaries as denominators.

**Preferred population approaches, in order:**

1. Published/commissioned official scenario outputs for a finite policy menu.
2. Approved detailed grouped distributions or anonymous representative records with documented weights, sufficient for the allowed changes.
3. An explicitly synthetic population calibrated to joint aggregates and multiple official reform benchmarks, with sensitivity ranges.

A synthetic model is a last-resort exploratory tool, not “SSB data.” Its uncertainty should include alternative debt/asset correlations and expensive-tail shapes. Sensitivity ranges are not statistical confidence intervals unless derived as such.

A restricted scenario grid can be precomputed and packaged for the browser. If interpolation is later allowed, validate it around the nonlinear thresholds and show it as approximate; do not extrapolate beyond its support.

### 5.5 Baselines and interpretation

Provide distinct comparisons:

- **Threshold-only:** same 2026 valuation data and other tax rules, 10 versus 14 million.
- **Valuation-model-only:** old versus new values for comparable records, holding policy fixed; only available with matched data or official outputs.
- **Full policy package:** model, allowance, and threshold changes together, with a dated continuation-of-old-rules comparison.
- **Custom policy:** user changes against a named frozen baseline.

Use “estimated annual change in public wealth-tax receipts,” not “gain/loss to society.” Revenue is a fiscal transfer, not a complete welfare calculation. State and municipal shares should be separated where supported. Do not infer municipal effects from a national total without geographic data.

Initially exclude behavioural effects such as moving, changing debt, portfolio shifts, house-price responses, and migration. Explain that a static estimate holds these fixed. The valuation-model effect can also be reduced by documented corrections; sensitivity analysis is appropriate, but arbitrary correction percentages must not be presented as evidence.

Do not mix municipal **eiendomsskatt** into wealth-tax receipts. The revised valuation model may affect it later; the May proposition discusses possible 2028 effects, which are a separate tax and scenario. [S4]

## 6. Proposed dashboard structure

### View 1 — “Hva endret seg?”

- Short, source-backed timeline with old valuation model, revised model, allowance change, and threshold change.
- Side-by-side interpretation of market-value estimate, taxable valuation, and final tax.
- Show “25% included = 75% discount” together; avoid the current ambiguous “Sats %.”
- Explain that a model revaluation is not necessarily a sudden increase in real economic wealth.

### View 2 — “Hvor vanlig er denne formuen?”

- Selected home value with exact numeric entry; range supports 40 million and beyond as needed.
- Ownership, debt, cash/financial assets, other assets, and assessment status.
- Optional income/liquidity details rather than compulsory detailed financial disclosure.
- Home-value histogram with selection, plus a separate household economic-net-wealth bracket.
- Explicit national population, data year, and denominator labels.
- Presets for comparisons, not unsourced claims of representative households: debt-free single pensioner, indebted working-age couple, and otherwise identical households with different liquid assets.
- Browser-local personal inputs; do not save/share personal financial values by default.

### View 3 — “Hvem får skatteendringen?”

- Compare named scenarios, then expose a simple set of policy controls.
- Bars for aggregate and average tax change by **baseline net-wealth group**; companion income view to expose low-income/high-wealth cases.
- Beneficiary count, average/median relief where available, and share of relief going to top groups.
- Display both relief per beneficiary and total relief, since they answer different questions.
- Show household annual tax and policy difference beside the existing valuation/tax curves.
- Fixed official evidence stays visibly separate from live custom calculations.

### View 4 — “Hva betyr det for offentlige inntekter?”

- Baseline, alternative, annual revenue difference, number affected, and estimation status.
- For unsupported settings: unavailable national estimate rather than a spurious exact figure.
- Static-model assumptions and uncertainty beside the result, not only in a hidden footnote.
- Optional budget-scale comparison using same-year sourced recurring expenditure; never imply the revenue is earmarked or that salary alone equals service cost.

### Controls and interaction rules

**Basic mode:** housing threshold, lower/upper taxable fraction, personal allowance, with named 10m/14m presets and an explicitly historical 20m proposal. Defaults should copy the chosen baseline so the initial difference is zero.

**Advanced mode:** custom valuation tiers, both tax bands, ownership/asset details, and modelling assumptions within validated limits.

Keep personal assumptions separate from national policy: changing **my mortgage** must not assign that mortgage to every household in Norway. A geography filter changes the displayed population; it must be clear whether policy still applies nationally.

Use neutral colours for revenue changes rather than automatically equating more tax with good and less tax with bad. Add direct labels, keyboard-usable controls, and a reset-to-baseline button. Share policy settings separately from personal financial inputs.

## 7. Architecture and deployment implications — future implementation only

Retain **Marimo + Polars + Altair**. The important change is separating responsibilities:

1. **Source snapshots and metadata:** immutable public inputs, citations, versions, population definitions.
2. **Legal policy definitions:** dated parameters and supported tax-unit rules.
3. **Pure calculation functions:** household/tax-unit valuation and liabilities, independently testable.
4. **Population/scenario layer:** weights and joint records if defensible, otherwise official finite scenario outputs.
5. **Presentation layer:** controls, charts, explanatory text, evidence labels.

This separation prevents a cosmetic UI edit from silently changing the legal baseline and lets the same tested calculation serve examples and any future population model.

**WASM approach:** retrieve and validate data before export, then ship compact public aggregates/approved synthetic data as static same-origin assets. Do not depend on a live SSB request every time a slider moves. This improves reproducibility and avoids browser CORS/API-availability surprises. Keep confidential-data processing outside the public app entirely.

Use small weighted representative datasets rather than millions of browser rows. Check asset copying/loading in the existing build, memory use, numerical agreement, and library availability in the actual exported runtime. No new heavy modelling dependency is justified yet.

The app currently lacks PEP 723 dependency metadata; audit the build's dependency handling and add explicit supported declarations if needed during implementation. This research is not a WASM pass: no browser execution or build verification has been performed.

Do not restart the running Marimo session, and do not use `@app.cell(hide_code=True)`. Future functions should have type hints and financial logic should be documented.

## 8. Delivery phases, decision gates, and validation

### Phase 0 — Agree the analytical contract

Decide audience/language, national versus personal entry point, primary-housing scope, comparison baseline, and whether scenario-only national estimates are acceptable initially.

**Recommended defaults:** Norwegian public-facing explanatory dashboard; primary housing first; 10-versus-14-million isolated comparison; official presets for national effects; economic wealth and liquidity both visible; no paid data purchase yet.

### Phase 1 — Evidence pack and data feasibility

Complete workstreams A–C: source registry, legal audit, public-data extracts, official scenario tables, histogram request, and missing-data assessment.

**Gate:** can available data support (a) household wealth brackets, (b) property rarity, (c) distribution of relief, and (d) arbitrary national recalculation? Answer each separately. Do not make the entire useful dashboard depend on obtaining microdata.

### Phase 2 — Public-data MVP, after approval

Correct/date the baseline, add both tax bands or clearly restrict scope, introduce selected-household inputs, wealth brackets, a clear tax-difference display, and official fixed-scenario evidence.

**Acceptance:** a reader can understand what changed, place a specified household in a defensible wealth bracket, and distinguish household calculations from published national estimates.

### Phase 3 — Conditional national simulator

Proceed only if data acquisition or transparent modelling can support the chosen controls. Narrow the policy menu when the evidence is narrow.

**Acceptance:** compare against multiple independent reference quantities—not merely force-fit one revenue headline—including taxpayer counts, wealth/debt totals, group effects, and official reform deltas using compatible vintages. Define acceptable discrepancies before calibration; report discrepancies and reject unsupported outputs.

### Phase 4 — Engagement, accessibility, and extensions

Improve guided examples, shareable policy scenarios, charts, accessibility, and budget context. Consider secondary residences only after the primary-housing model is credible. Treat a municipal property-tax module as a separate project decision.

### Required future checks

- Reproduce official worked examples, including no-tax cases. [S2]
- Test values immediately below, exactly at, and above each housing and tax threshold; ensure continuous tiered valuation.
- Test ownership shares, jointly assessed couples versus cohabitants, zero/large debt, mixed assets, and no debt double-counting.
- Baseline compared with itself gives zero difference; aggregation is consistent with individual results.
- For a fixed, supported household model, reducing an included valuation fraction must not increase liability.
- Verify wealth-group cutoffs and missing/suppressed-data handling.
- Check all labels, years, units, denominators, rounds, and scenario baselines.
- Preserve tests with the future calculation changes; this repository currently has no formal suite.
- Run Marimo validation, applicable Ruff checks, and `uv run .github/scripts/build.py`; then test the exported app in an actual browser. Export success alone is not browser compatibility.

## 9. Source register

All sources below were opened/read during this initial review; Statbank inventory entries were checked through their metadata API. This is a starting evidence register, not a claim that every planned question has been resolved.

- **S1 — Skatteetaten, Formuesskatt og verdsettingsrabatter (2026 selected):** https://www.skatteetaten.no/satser/formuesskatt/
- **S2 — Finance Ministry, 27 February 2026 announcement and worked examples:** https://www.regjeringen.no/no/aktuelt/mer-rettferdig-formuesskatt-med-oppdatert-boligmodell/id3150420/
- **S3 — SSB, corrected 23 January 2026 valuation-model revenue analysis:** https://www.ssb.no/priser-og-prisindekser/boligpriser-og-boligprisindekser/artikler/ny-boligverdsetting-oker-inntektene-fra-formuesskatten
- **S4 — Prop. 95 LS (2025–2026), chapter 3; corrected edition marked 11 June 2026:** https://www.regjeringen.no/no/dokumenter/prop.-95-ls-20252026/id3159628/?ch=3
- **S5 — Finance Minister's 27 February 2026 presentation, particularly slides 5 and 8–11:** https://www.regjeringen.no/contentassets/27840e5ecb354f02a249f3cbd86b01d9/finmins-presentasjon-oppdatert-boligmodell-27.02.26.pdf
- **S6 — Written question 1404, ministerial answer dated 12 February 2026, tables 1–7:** https://www.stortinget.no/globalassets/pdf/dokumentserien/2025-2026/dok15-202526-1404-vedlegg.pdf
- **S7 — SSB table 10318, wealth-group cutoffs:** https://www.ssb.no/statbank/table/10318 ; numerical extraction used https://data.ssb.no/api/v0/no/table/10318 with year 2024, `ContentsCode=Grenseverdi,Hushald`, and deciles plus top 5%/1%/0.1%.
- **S8 — SSB, Hva er vanlig formue?, corrected 12 February 2026:** https://www.ssb.no/inntekt-og-forbruk/inntekt-og-formue/artikler/hva-er-vanlig-formue
- **S9 — Representantforslag 94 S (2025–2026), dated 27 January 2026:** https://www.stortinget.no/no/Saker-og-publikasjoner/Publikasjoner/Representantforslag/2025-2026/dok8-202526-094s/?all=true
- **S10 — SSB PxWebApi v2 documentation overview:** https://www.ssb.no/api/pxwebapi
- **S11 — SSB commissioned tables, public availability and pricing:** https://www.ssb.no/data-til-forskning/tabelloppdrag
- **S12 — SSB microdata eligibility:** https://www.ssb.no/data-til-forskning/utlan-av-data-til-forskere
- **S13 — microdata.no institutional access and anonymising interface:** https://www.microdata.no/om-microdata-no/
- **S14 — Skatteetaten debt allocation and valuation discounts:** https://www.skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/verdsettingsrabatt-ved-fastsetting-av-formue/ (worked example/historical discount table; verify target-year law before implementation).
- **S15 — SSB explanation of revised geographical valuation model, 1 December 2025:** https://www.ssb.no/priser-og-prisindekser/boligpriser-og-boligprisindekser/artikler/revidert-modell-for-beregning-av-formuesverdi-for-bolig
- **S16 — SSB LOTTE-Skatt overview:** https://www.ssb.no/forskning/offentlig-okonomi/inntektsfordeling/lotte-skatt (older background documentation; current scenario documents take precedence for sample/base-year details).

**Source trap:** SSB's report *Modell for beregning av boligformue*, published 27 February 2026 as Notater 2026/10, explicitly covers 2025 values and says a separate revised-model note will follow. Do not cite its accuracy statistics as if they validate the new 2026 model: https://www.ssb.no/priser-og-prisindekser/boligpriser-og-boligprisindekser/artikler/modell-for-beregning-av-boligformue-27022026

## 10. Progress tracker

### Completed in this planning session

- [x] Read the existing app and relevant earlier plans; identified unsupported macro assumptions.
- [x] Read relevant Marimo/WASM guidance; made no app or dependency changes.
- [x] Verified the 10-to-14-million threshold and 25%/70% included fractions against official sources.
- [x] Located and read official valuation-model, fiscal, and distributional analyses.
- [x] Found the published primary-home histogram and identified its underlying data as a high-priority request.
- [x] Checked candidate SSB table dimensions and extracted actual 2024 wealth-group cutoffs.
- [x] Identified estimation-vintage conflicts and person/household/property distinctions.
- [x] Drafted staged research, data-access, methodology, UX, and validation plans.

### Pending discussion / research

- [ ] User review and prioritisation; no implementation approved.
- [ ] Confirm enacted-law references, dates, co-ownership rules, and municipal exceptions.
- [ ] Save reproducible source/data snapshots and complete the claims ledger.
- [ ] Reconcile February versus May threshold-revenue estimates and comparison baselines.
- [ ] Search for existing 14-million distribution tables and obtain histogram raw numbers.
- [ ] Decide whether to send the draft data request; nothing has been sent or ordered.
- [ ] Assess need, cost, and eligibility for any commissioned aggregates/research collaboration.
- [ ] Choose official-presets-only versus a justified wider national simulator.
- [ ] Agree the MVP, unsupported-case behaviour, and acceptance criteria.

### Implementation — not started

- [ ] Correct/version and test the tax engine and scenario baselines.
- [ ] Add selected-household context, wealth brackets, and official scenario displays.
- [ ] Add national recalculation only if the evidence gate is satisfied.
- [ ] Rework UI and explanatory views.
- [ ] Run code checks, WASM export, and browser validation after implementation.
