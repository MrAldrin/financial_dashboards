# Research plan: Norwegian housing wealth, tax incidence, and public revenue

**Status:** Core dashboard implemented. On 20 September 2026 the user requested autonomous work first and **all human review at the end**. The legal audit and subsequently authorised bounded February/May official-estimate investigation are complete; the latter records an unresolved evidence gap, not a forced reconciliation. Neither authorises calculator changes or optional features. See the current execution order below and progress records at the bottom. Earlier “plan only” wording records the original research-session scope.  
**Initial source review:** 20 September 2026.  
**Target app:** `apps/building_taxation.py`.  
**Scope:** Primary-residence wealth taxation first, within a combined household balance-sheet and income context. Secondary-residence policy and municipal property tax are separate extensions.  
**User clarification incorporated:** 20 September 2026. Preserve the full-range interactive curves; use open data only; allow transparent distribution-based estimates; build toward one coordinated dashboard, not separate replacement apps.

## 1. Purpose and recommendation

Extend the existing interactive policy sandbox with evidence and population context. **The full tax and valuation curves are a core educational feature, not a temporary substitute for individual tax-return data.** They let users discover how brackets, debt, other assets, and allowances interact across the entire home-value range, including where no tax is due and where the slope becomes steeper.

The dashboard should answer:

1. **How do these rules interact, across all home values and for my selected example?**
2. **How many Norwegian homes lie in the ranges affected by this change?**
3. **What do households in each wealth decile own, and how important is housing versus other assets and debt?**
4. **Who pays more or less, and what is the estimated annual revenue effect?**
5. **How do economic wealth, income, and available cash differ?**

The dashboard should test claims about “ordinary homeowners” with distributions, not replace anecdotes with other anecdotes. Expensive housing, net wealth, income, and ability to pay are different quantities. Show them together, with focused explanations available when helpful.

### Agreed direction for the next agent

- **Keep and improve the full-range curves.** A selected-household point is an annotation on those curves, never their replacement.
- **One dashboard with multiple coordinated plots.** Explain components individually, but also provide a combined playground where the controls and their consequences are visible together.
- **Open data only.** Use published SSB tables/APIs, articles and chart data, and other openly published official material. No ministry/SSB outreach, email, eInnsyn requests, commissioned tables, paid data, restricted microdata, or institutional-access work.
- **Distribution-based approximation is welcome.** We do not need every household record. Use public distributions, weighted groups, interpolation, and explicit assumptions to make useful exploratory calculations. Distinguish observations from estimates and show sensitivity without treating missing microdata as a reason to abandon the feature.
- **Preserve the research already gathered.** Official scenario estimates and wealth cutoffs remain useful reference points and validation checks, not a restriction to preset-only interaction.
- **Plan now, implement later.** This document is the handoff specification for a later agent; no charts, prototypes, or app code are being built in this session.

**Current execution order — autonomous work before human review:**

1. Audit the 2026 legal basis: enactment/effective dates, co-ownership, joint assessment, municipal-rate scope and debt-allocation exclusions. Archive evidence and identify calculator follow-ups separately.
2. Investigate remaining open-data gaps: February/May estimate comparability, matching housing/debt components, and ownership/tax-unit mapping. Record bounded negative findings; do not invent national profiles or force reconciliation.
3. Complete separately authorised, evidence-supported maintenance and automated QA. Technical checks of overflow, accessibility and performance can be automated without asking the user to inspect screens. Preserve full curves and aligned axes; defer preference-dependent layout changes and optional plots.
4. **Final human-review gate:** consolidate the findings, outstanding modelling/scope decisions, plot order/density, desktop/mobile experience, baseline/custom control clarity, and optional features into one review. No intermediate human visual-review checkpoints. If a decision requires user preference, queue it here and continue independent authorised work instead of guessing.

This sequencing change postpones review, not safety constraints or evidence requirements. New calculator scope still needs explicit authorisation; bookmarks, pushing and integration remain user-controlled.

## 2. Findings from the initial research

### 2.1 What actually changed

- The relevant threshold moved from **NOK 10 million to NOK 14 million**, not 40 million. NOK 40 million can still be a useful hypothetical scenario.
- The primary home's taxable valuation is **25% below the threshold and 70% on the excess**. These are discounts of **75% and 30%**, respectively. Crossing the threshold does not revalue the whole home at 70%.
- SSB's revised housing model uses smaller geographical areas based on *grunnkretser*, rather than the previous municipality-based structure. SSB describes improved predictive accuracy, not perfect individual valuations. [S3, S15]
- Higher estimated home values could increase **tax receipts**; this was not itself additional government spending. Raising the threshold reduces receipts relative to keeping the lower threshold.
- Government stated that the model transition should not raise aggregate revenue. It increased the general wealth-tax allowance and subsequently proposed increasing the housing threshold. Revenue neutrality does not mean that every individual is unaffected. [S2, S4]
- Skatteetaten's current 2026 rate page lists the NOK 14 million threshold. The follow-up legal audit verifies enactment by law 23 June 2026 no. 66, part II, effective immediately with effect from income year 2026 under part IV. The February and May announcements were proposals when published. See `data/wealth/legal_audit_2026.md` and its immutable legal snapshot. [S1]

### 2.2 Verified 2026 baseline for further legal checking

| Component | Current published 2026 figure | Important qualification |
|---|---:|---|
| Primary-home threshold | NOK 14,000,000 | Enacted for income year 2026; ordinary whole-property valuation/share allocation audited separately; special buildings remain excluded |
| Taxable fraction below / above threshold | 25% / 70% | Apply progressively to portions of value |
| Personal wealth-tax allowance | NOK 1,900,000 | Doubled for qualifying jointly assessed couples, not every household of two adults |
| Standard combined wealth-tax rate | 1.0% | Published municipal rate 0.35% + state rate 0.65%; check municipal exceptions |
| Upper combined rate | 1.1% | On net taxable wealth above NOK 21,500,000 before subtracting the allowance; threshold doubles for qualifying joint assessment |
| Secondary-home taxable fraction | 100% | Remains in other-assets/background data even while its policy controls are deferred |

Do not confuse the NOK 14 million **housing valuation threshold** with the NOK 1.9 million **personal allowance** or NOK 21.5 million **upper wealth-tax threshold**. [S1]

### 2.3 Existing evidence directly relevant to the dashboard

**Housing rarity:** The Finance Ministry reported that approximately **98% of primary residences** would be valued entirely at 25% under the NOK 14 million threshold. Its 27 February presentation includes a primary-home value histogram in million-kroner bands and says about 2% of primary homes in the tax-card data were above NOK 14 million. This is a statement about **properties**, not the richest 2% of people. Search for already-open numeric chart data; if unavailable, a documented approximation from the published plot is acceptable. Keep the unshown upper tail explicit rather than treating it as zero. [S2, S5]

**The model change:** SSB's corrected 23 January analysis estimates an isolated **NOK 973 million increase** in annual wealth-tax receipts from the revised valuation model. It reports 318,700 people with increased tax, 229,400 with reduced tax, and 4,107,600 in the approximately unchanged category. The latter corresponds to the article's -200 to +199 kroner band; it is not necessarily exact zero. These are model estimates for people aged 17+, using 2023 data projected to 2026, not final 2026 tax outcomes. Documented downward valuation corrections are not incorporated. [S3]

**The actual threshold proposal:** The corrected May budget proposition estimates that increasing the threshold from 10 to 14 million reduces annual accrued receipts by approximately **NOK 830 million**, relative to the stated adopted-budget comparison. With the updated housing-model estimates and other already adopted wealth-tax changes, it reports a combined **NOK 280 million revenue loss** relative to its budget reference. Accrued annual effects and cash booked in a particular year differ. [S4]

**Important source-version conflict to reconcile:** The February presentation showed **NOK 730 million**, not 830 million, for the threshold measure, within a comparison against continuation of the 2025 system into 2026. Keep both as dated estimates until the definition/vintage difference is resolved. Do not simply add or subtract the January, February, and May headline figures. [S3–S5]

**A particularly valuable distributional source:** In the Finance Minister's answer of 12 February to written question 1404, the **10-to-20-million proposal** is estimated to:

- Reduce annual receipts by NOK 1.25 billion.
- Benefit approximately 114,600 people, averaging about NOK 11,000 in tax relief.
- Benefit a group with **average gross annual income of about NOK 1.72 million**.
- Concentrate the reported relief strongly toward the top of the net-wealth distribution.

The answer contains seven tables covering income bands, income deciles/top percentiles, net-wealth bands/deciles/top percentiles, and centrality classes. This provides valuable distributional context and calibration targets alongside the interactive curves and any public-data-based population approximation. However:

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

## 3. Preserve the existing strengths and extend them

### The current curves are the foundation

- Marimo reactive controls, Polars calculations, Altair charts, and custom progressive tiers already support the intended exploratory experience.
- A full curve across home values answers a different, important question from a single result: **where and why does tax begin, and how fast does it grow?**
- Holding debt and other assets fixed while moving across house values is a deliberate controlled comparison. Keep it as the default household-mechanics mode.
- The flat zero-tax region, the point where the allowance is exhausted, and the change in slope at a housing tier are exactly the features the user wants people to understand.
- The existing 14-million / 25%-70% baseline is a useful starting point. Enhance its explanation, year/source labels, and treatment of the upper wealth-tax band.

### Additions, not replacements

1. Retain baseline/custom valuation and annual-tax lines over the full home-value range; include exact breakpoints and extend the range beyond 40 million when needed.
2. Add a selected-value marker, a line showing the tax base **before clipping at zero**, and clear annotations for tier boundaries and the onset of tax liability.
3. Add an aligned housing-value histogram underneath so users see both the rule and how many homes are exposed to it.
4. Add income context, economic net wealth, wealth-composition plots, and a live difference curve; retain combined adjustment of debt, other assets, allowance, and valuation rules.
5. Use public-data distributions to weight examples and develop an estimated population effect, with assumptions visible.
6. Clarify “Annen nettoformue” or split it into asset/debt components when needed so economic wealth and taxable wealth stay distinct and debt is not deducted twice.

### Earlier ideas to carry forward with sources

`plans/norwegian_taxation_dashboard_improvements.md` already points toward population distributions and public-revenue context. Keep that direction. Its proposed counts, housing-price averages, budget figures, and log-normal parameters are starting hypotheses to replace with open-source values or documented estimates, not reasons to discard population modelling.

- Prefer published bins or reconstructed public-chart bins to fitting a single curve from only a mean and median; use a fitted distribution when useful and show tail sensitivity.
- A housing distribution directly supports counts above/below a threshold. Revenue additionally needs assumed debt, other assets and tax-unit structure; estimate these transparently rather than implying that property counts alone determine actual liabilities.
- Distinguish homes, owners, households, and taxpayers in chart labels and weights.
- Prefer **change in total wealth-tax receipts caused by primary-housing rules** over an undefined standalone “housing wealth tax.”
- Update mixed-year legal parameters in older plans when implementing. Preserve source-backed findings in this plan.
- Debt experiments are useful controlled comparisons, not advice that borrowing is free: explain the disposition of borrowed money if modelling a borrowing decision.
- Budget equivalents are optional context and should use sourced full costs, not salaries alone.

This plan updates the design direction without changing the app or the older plan files.

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
4. Look for already-published equivalent distribution tables for **10 to 14 million**. If absent, record the gap and use labelled modelling assumptions; do not request data.
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
| February presentation, slides 8–11 | Primary-home value histogram and above-14-million share | Housing rarity; published bins or documented chart-based reconstruction for weighting | Exact raw counts merely from reading bar heights |
| Written question 1404 | Official fixed-scenario distribution and revenue estimates | “Who benefits?” and model cross-checks for the 20-million proposal | Observed outcomes for arbitrary slider scenarios |
| SSB, *Vekst i husholdningenes finansformue i 2024*, figures 2–3 [S17] | Financial wealth by net-wealth decile; financial-asset composition including top 1% and 0.1% | Open evidence for the wealth-composition view | Complete primary-home/debt breakdown by decile |
| [10319](https://www.ssb.no/statbank/table/10319), metadata checked during revision | Mean net wealth by **income** decile | Optional income/wealth context | Asset composition by **wealth** decile; these rankings must not be confused |

**Extraction protocol**

- Prefer SSB's current PxWebApi v2 for implementation. The initial metadata checks and table 10318 numerical spot-check used the still-working legacy endpoint; that is not a proposed permanent dependency. [S10]
- Record table ID, exact query and category codes, response metadata, extraction date, units, population exclusions, year, revisions, and source URL.
- Preserve immutable raw responses and derived small datasets; record transformations and checksums.
- Do not interpret suppressed/missing values as zero.
- Distinguish a mean over all households from a mean among households with a nonzero amount.
- Never recover a mean market value by simply dividing mean taxable housing wealth by 0.25: progressive tiers and ownership make that invalid.
- Check overlap and denominator definitions before joining or comparing tables.
- Keep 2024 final observations, 2025 preliminary figures, and 2026 projections distinct. The revised valuation model can create a methodological break, not just house-price inflation.

**Deliverable:** source registry and feasibility matrix: directly published, reconstructable from public material, estimated from public anchors, or unavailable within scope.

### C. Build usable distributions from open sources only

**No outreach or access applications.** The previous data-request route and draft letter are removed. Lack of individual records is expected; the task is to construct a useful, documented approximation from public distributions.

1. Search SSB Statbank and article figures, including their public “Vis som tabell” data, downloadable files and embedded chart series. Public official PDFs are also in scope.
2. For the housing histogram, prefer published numeric bins. If only a plot is open, reconstruct approximate bar values, record the page/axes/method, and check against published totals and the above-14-million share. Label this as digitised/estimated, not exact administrative counts.
3. Preserve the source bins; add finer interpolation near movable thresholds only with an explicit rule (for example uniform density within a bin). Show a bounds/sensitivity option for thresholds inside coarse bins.
4. Keep the upper tail, including 30–40m and 40m+, represented. If its shape is unavailable, use clearly stated alternative tail assumptions rather than silently excluding it.
5. Use SSB wealth-group counts, cutoffs, means and available component totals as anchors for weighted representative groups. Add assumed within-group variation for tax calculations, where useful; we do not need a reconstructed record for every person.
6. Search for open debt and housing/financial-asset composition by the **same wealth ranking**. Record which relationships are published and which are assumed. Never join separate decile tables as if they identify the same households unless their ranking and population match.
7. Use official published reform estimates as reasonableness checks, allowing differences in years and definitions. They are benchmarks, not a prerequisite for every slider position.

**Initial distribution targets:** source-defined home-value bands with detail around 10m and 14m; wealth deciles 0–10%, 10–20%, …, 90–100%; a separate top-1% detail panel when data permit. Do not invent unavailable fine-resolution observations.

**Deliverable:** compact open-data distributions, a source/assumption sheet, and a first estimated weighting approach with low/base/high sensitivity variants.

### D. Wealth composition by decile — new core research question

The requested question is: **“Where is the wealth held at different points in the wealth distribution?”** Rank households by baseline **economic net wealth**, not by house price or income.

Target components: primary-home value, other property/real assets, bank deposits, shares/funds/other financial assets, and debt. Use mutually exclusive categories to avoid counting financial assets or real estate twice.

- First plot: average kroner per household in each decile, with assets stacked above zero, debt below zero, and net wealth marked separately.
- Companion plot: housing and other asset shares of **gross assets**. Avoid dividing by zero/negative net wealth, which produces misleading percentages.
- Negative net wealth in lower deciles is possible and supported by SSB; it does **not** mean the house itself has negative value. Show housing equity only when mortgage-specific debt is available or an allocation assumption is explicitly labelled. Total household debt includes more than mortgages.
- Show top 1% (optionally top 0.1%) as a nested detail, not an extra disjoint group added to the ten deciles. An alternative non-overlapping upper split is 90–99% and 99–100%, if sufficient data support it.
- Distinguish the ratio of group-total housing to group-total assets from the average household housing share; the former is readily obtainable from compatible component means but is not the latter.
- Clicking a decile can highlight it and optionally load a **stylised group profile** into the playground. A profile assembled from means is not an actual or necessarily typical household.

**Verified open lead:** SSB's 19 February 2026 article [S17] says real capital, mainly housing, accounted for roughly two-thirds of aggregate gross wealth in 2024. It provides financial wealth by net-wealth decile (figure 2) and financial-asset composition by those deciles plus the top 1% and 0.1% (figure 3). Real capital is broader than housing. This is useful partial coverage; a full housing-and-debt decomposition for every decile has **not yet been verified**. Extract the public figure data next and continue the open-source search. If components remain unavailable, present the verified decomposition alongside clearly marked estimates or a coarser grouping—not a false claim of exact coverage.

## 5. Method: what can legitimately update when a slider moves?

### 5.1 Maintain three evidence levels

| Level | Contents | Behaviour when controls change |
|---|---|---|
| Observed / published reference | SSB wealth cutoffs and housing counts | Highlight the selected position; do not alter underlying observations |
| Official scenario estimate | Published LOTTE-Skatt results for a defined reform | Display only for matching presets and label vintage/baseline |
| Dashboard calculation/model | A specified household or open-data-informed weighted population approximation | Recalculate with documented assumptions and scope |

A fixed official estimate must not appear to be a live calculation. Custom settings should use the dashboard's public-data-based estimate where implemented, labelled **illustrative** or **modelled estimate** and accompanied by assumptions. Show unavailable only for genuinely unsupported dimensions/ranges; do not disable the core sandbox merely because no official estimate exists for that exact setting.

### 5.2 Household calculation: economic wealth and tax wealth are separate

For a simplified full-owner example, primary-home taxable value is:

**F(V, L) = 0.25 × min(V, L) + 0.70 × max(V − L, 0).**

For other selected rates, substitute the appropriate fractions; advanced mode can retain multiple progressive tiers.

Calculate separately:

- **Economic net wealth:** household asset values using the statistical reference definitions, less economic debt, before tax discounts.
- **Taxable net wealth:** tax values of relevant assets less legally deductible debt.
- **Wealth-tax liability:** municipal and state schedules applied to the appropriate person/joint tax unit.
- **Liquidity context:** accessible financial assets and annual tax relative to disposable income, if supplied; not a complete household affordability assessment.

Ownership and tax-unit rules precede household aggregation. The follow-up legal audit confirms ordinary co-ownership uses whole-property valuation followed by ownership-share allocation, not an independent whole-property threshold for each owner. Special multi-unit cases remain outside scope. Ordinary cohabitants are not automatically treated like jointly assessed spouses.

Primary-home debt does not generally receive the same reduction as debt allocated to discounted shares. The current simple debt subtraction is not a complete mixed-asset tax engine. Verify and test the statutory allocation rules; either support the required asset breakdown or explicitly restrict the simplified calculator. [S14]

For the upper band, distinguish net taxable wealth before the allowance from the taxable amount after it. The NOK 21.5 million threshold must not be shifted upward by subtracting the allowance twice.

**Useful worked comparison:** holding values, debt, other assets and 2026 tax parameters fixed, a single full owner of a NOK 12 million primary home with no debt or other assets pays NOK 20,000 with a 10-million threshold versus NOK 11,000 with a 14-million threshold: a NOK 9,000 annual difference. This is a calculation for an explicitly specified household, not an average beneficiary.

Above NOK 14 million, raising the threshold from 10 to 14 million lowers the property's taxable value by NOK 1.8 million. Actual tax savings depend on ownership, allowances, debt, and tax bands; they are not automatically NOK 18,000 for every owner.

### 5.2a Make the interacting thresholds visible across the whole curve

For the simplified example, also plot **Z(V) = F(V) + other taxable assets − deductible debt − allowance**, before replacing negative values with zero for the tax calculation.

- The housing threshold **L** is where the valuation slope changes.
- The tax-onset value **V₀** is where Z(V) first becomes positive. It depends on debt, other assets, the allowance and the selected rules; it is not generally equal to L.
- Mark L and V₀ separately and label coincident markers when they meet. Show any upper wealth-tax transition separately too. If tax is already due at zero home value or never becomes due in the displayed range, say so instead of inventing a crossing.
- Above the onset, at a 1% wealth-tax rate, including 25% of an extra NOK 1 million adds NOK 2,500 of annual tax; including 70% adds NOK 7,000. These local slopes apply only within the corresponding active bands.
- Crossing the housing threshold creates a **kink, not a jump** in the bill. When the allowance is exhausted near that kink, the transition from zero tax to rapid growth is especially informative.

**Demonstration preset:** single full owner; no other assets; NOK 1.6m debt; NOK 1.9m allowance; 14m housing threshold; 25%/70% valuation. Both markers meet at 14m. Annual tax is zero at 14m, NOK 700 at 14.1m, NOK 7,000 at 15m, and NOK 14,000 at 16m under the standard 1% band. Moving the debt, other-assets or allowance controls shifts the onset; moving the housing threshold changes where the slope steepens. Keep the full curve visible throughout.

### 5.2b Include income without confusing a flow with wealth

Add an annual-income control, optionally initialised from a clearly sourced mean/median for a named population. It is part of the combined playground, not a substitute for the other-assets control.

- Income by itself does not enter the basic wealth-tax base; unspent income becomes wealth only through a separately specified saving assumption.
- With assets and debt fixed, the income slider changes **wealth tax as a percentage of income**, not the kroner wealth-tax curve. Label gross versus disposable income explicitly and handle zero income without division errors.
- A second plot can show that burden ratio across all house values. This makes a salary/average-income slider useful while preserving correct tax mechanics.
- If a later scope decision adds income tax or accumulation over time, use a separate model. Do not silently build either into this wealth-tax extension.

### 5.3 Dynamic wealth context

- Household assets/debt controls update economic net wealth and its published bracket.
- The public-data or estimated home-value histogram updates the selected bin, the shaded valuation tiers, and the counts/shares on each side of movable thresholds; disclose within-bin uncertainty.
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

**Use a practical open-data modelling ladder, not a microdata prerequisite:**

1. **Property exposure:** integrate the published/estimated housing-value distribution to count homes in each valuation tier and the region between old/new thresholds. This needs no assumptions about owners' other assets, but it measures homes, not people who actually pay tax.
2. **Distribution-weighted illustration:** apply the selected household balance-sheet assumptions across that housing distribution. Show an illustrative aggregate tax change under those assumptions. Make explicit if it assumes one full-owner tax unit per home; do not relabel it as actual Norwegian receipts or use household weights on property bins without an ownership mapping.
3. **Estimated national scenario:** replace the single balance sheet with a compact weighted mix of household/tax-unit profiles informed by open wealth, debt, ownership and household-type statistics. Document the mapping from properties to owners/tax units, missing correlations, and within-group assumptions. Use a few profiles per group or integration points rather than tax on a single group mean where possible.
4. **Official benchmark:** show comparable published reform results beside the model to check scale and explain differences. These are not the only permitted slider positions.

This approach allows immediate exploration without claiming to reproduce tax records. Start with simple, inspectable assumptions and improve them as open sources permit. A synthetic/grouped model is an acceptable intended tool, labelled as a **dashboard estimate informed by SSB**, not as observed SSB microdata.

Vary debt/asset relationships, within-bin distributions and expensive-tail assumptions to produce low/base/high scenarios. These are sensitivity ranges, not statistical confidence intervals. Round totals to the precision the inputs justify. If estimates are unstable, still show the robust exposure counts and explain the range rather than presenting a precise headline.

Custom slider recalculation is the goal. A precomputed grid is an optional performance technique, not a replacement for the interactive sandbox; validate interpolation near thresholds and identify unsupported extrapolation.

### 5.5 Baselines and interpretation

Provide distinct comparisons:

- **Threshold-only:** same 2026 valuation data and other tax rules, 10 versus 14 million.
- **Valuation-model-only:** old versus new values for comparable records, holding policy fixed; only available with matched data or official outputs.
- **Full policy package:** model, allowance, and threshold changes together, with a dated continuation-of-old-rules comparison.
- **Custom policy:** user changes against a named frozen baseline.

Use “estimated annual change in public wealth-tax receipts,” not “gain/loss to society.” Revenue is a fiscal transfer, not a complete welfare calculation. State and municipal shares should be separated where supported. Do not infer municipal effects from a national total without geographic data.

Initially exclude behavioural effects such as moving, changing debt, portfolio shifts, house-price responses, and migration. Explain that a static estimate holds these fixed. The valuation-model effect can also be reduced by documented corrections; sensitivity analysis is appropriate, but arbitrary correction percentages must not be presented as evidence.

Do not mix municipal **eiendomsskatt** into wealth-tax receipts. The revised valuation model may affect it later; the May proposition discusses possible 2028 effects, which are a separate tax and scenario. [S4]

## 6. Proposed dashboard structure: one coordinated playground

Use several plots in the existing app, sharing controls and highlighting. Focused explanation sections are useful, but **a combined view is required**: the user must be able to see how housing, other wealth, debt, the allowance, and income context interact without switching among separate apps or disconnected calculators.

### Main view — “Utforsk samspillet”

Keep shared controls visible next to or above an aligned chart stack:

1. **Taxable home valuation versus home value:** baseline and custom full-range lines, labelled valuation tiers.
2. **Tax base after debt and allowance, before the zero floor:** plot Z(V) from section 5.2a, including its negative region and zero line. This explains why taxable home value is not itself the bill.
3. **Annual wealth tax versus home value:** baseline/custom lines, separate housing-tier and tax-onset markers, selected-household point, and exact breakpoint tooltips.
4. **Norwegian home-value histogram underneath:** same home-value x-axis and aligned boundaries. Shade the range between the baseline and custom thresholds, show counts/shares within each tier, and retain the tail when zooming into ordinary values.
5. **Policy difference curve:** annual kroner saved/paid at every home value, not only at the selected point. This can be a compact panel rather than another large chart.

The core explanatory panels have now been implemented. Preserve them during autonomous checks; queue user evaluation of clarity for the final human-review gate. Compact panels/collapsible explanations are acceptable, but do not reduce the playground to a single number or hide all interactions in separate tabs.

Use separate vertically aligned plots instead of confusing independent tax/count scales on one y-axis. Shared hover/selection should connect the same home value across the panels. Moving a policy threshold changes the tax lines and histogram shading; it does **not** move the observed home values in a static simulation. A separate valuation-model or price scenario may change those values, clearly labelled.

**Counts require careful wording:** “homes above the valuation threshold” is directly distribution-based; “people now paying wealth tax” requires balance-sheet/tax-unit assumptions. If shading values above the selected profile's tax-onset point, label it “homes in the taxable range for this example profile,” not actual taxpayers.

### Supporting view — “Hvor ligger formuen?”

- Wealth-decile component charts described in workstream D: average asset amounts above zero, debt below zero, net wealth marker, and optional gross-asset composition shares.
- A separate top-1% detail so its different composition is not hidden in the top decile.
- A selected household's net-wealth bracket alongside the source year and definition.
- Highlight that housing can dominate ordinary balance sheets while financial assets are more concentrated toward the top; let the data determine the magnitude.
- Optional decile-to-stylised-profile interaction with a clear reset, without claiming that means reconstruct an actual household.

### Supporting view — “Inntekt og skattebelastning”

- Annual income slider/number input with optional sourced average/median presets.
- Wealth tax as a percentage of that income across the **whole home-value range**, or at least alongside the main curve's selected point.
- Debt-free pensioner, indebted working-age couple and high-financial-wealth example profiles; these are demonstrations, not assertions about typical owners.
- Explain that income changes burden ratios; wealth, debt and rules determine wealth tax. Accessible cash can add liquidity context without a full spending/affordability model.

### Combined results — “Hvem påvirkes, og hva blir provenyet?”

Keep a compact summary visible with the playground: selected annual bill/difference, homes in the changed range, household wealth bracket, and distribution-weighted estimated revenue difference with its evidence label.

Provide detail panels for baseline-wealth-group/income-group tax changes where the open data/model support them. Distinguish aggregate relief, relief per beneficiary, and average change across everyone. Display official published estimates as references, not as live values for arbitrary settings.

Sensitivity assumptions and low/base/high results should be accessible beside the national estimate. A deliberately simple common-profile illustration is a useful early stage; label it accordingly rather than pretending it is already a national forecast.

### Brief context — “Hva endret seg?”

Retain the source-backed timeline, the distinction between valuation-model and tax-rule changes, and the explanation “25% included = 75% discount.” This supports the playground rather than replacing it as the main experience.

### Controls and interaction rules

- **Household:** home-value marker, ownership/assessment status, debt, other assets, annual income, optional liquid assets.
- **Policy:** housing thresholds, included valuation fractions, personal allowance, and tax rates; retain dynamic custom tiers. Sliders should have matching numeric inputs for exact examples.
- **Population assumptions:** public-data year, distribution/interpolation choices, and debt/other-assets profile assumptions for weighted calculations. Keep these separately labelled from the personal controls.
- Default custom rules can copy the baseline so the initial difference is zero; offer 10m/14m and historically labelled 20m comparison presets without restricting free exploration.
- Holding the household's other assets/debt fixed along the line is intentional. In an explicitly selected **common-profile illustration**, use those controls for the weighted calculation too. In the estimated-national mode, personal sliders must not silently overwrite every household's finances.
- A region filter changes the reference population visibly; distinguish it from a national policy change.
- Use neutral colours for revenue gains/losses, accessible labels and keyboard controls, and a reset-to-baseline button. Keep personal inputs browser-local and exclude them from shared policy links by default.

**Final human-review candidates, not separate apps to build now:** a marginal-tax/slope panel, a debt-versus-home-value heatmap, and a valuation-to-tax waterfall at the selected point. Defer these optional additions until the final review of the coordinated curves, histogram and composition charts; they do not block autonomous evidence work.

## 7. Architecture and deployment implications — future implementation only

Retain **Marimo + Polars + Altair**. The important change is separating responsibilities:

1. **Source snapshots and metadata:** immutable public inputs, citations, versions, population definitions.
2. **Legal policy definitions:** dated parameters and supported tax-unit rules.
3. **Pure calculation functions:** household/tax-unit valuation and liabilities, independently testable.
4. **Population/scenario layer:** open distributions and weighted representative profiles with explicit assumptions; published official scenarios as benchmarks.
5. **Presentation layer:** controls, charts, explanatory text, evidence labels.

This separation prevents a cosmetic UI edit from silently changing the legal baseline and lets the same tested calculation serve the full curves, selected examples and distribution-weighted estimates. All plots should depend on the same scenario definitions rather than duplicating separate calculators.

**WASM approach:** retrieve and validate open data before export, then ship compact public aggregates/derived representative profiles as static same-origin assets. Do not depend on a live SSB request every time a slider moves. This improves reproducibility and avoids browser CORS/API-availability surprises. Restricted/confidential data processing is outside this project's scope entirely.

Use small weighted representative datasets rather than millions of browser rows. Check asset copying/loading in the existing build, memory use, numerical agreement, and library availability in the actual exported runtime. No new heavy modelling dependency is justified yet.

The app currently lacks PEP 723 dependency metadata; audit the build's dependency handling and add explicit supported declarations if needed during implementation. This research is not a WASM pass: no browser execution or build verification has been performed.

Do not restart the running Marimo session, and do not use `@app.cell(hide_code=True)`. Future functions should have type hints and financial logic should be documented.

## 8. Delivery phases, decision gates, and validation

### Phase 0 — Preserve the agreed direction

**Already decided:** open sources only; full-range curves remain central; one coordinated app with focused explanations and a combined playground; distribution-based estimates are acceptable; no implementation in this planning session.

**Recommended defaults:** Norwegian public-facing app, primary-housing policy first, 10-versus-14-million comparison as an example rather than a restriction, and other assets/debt/income visible in the combined context.

Remaining human review concerns plot priority and complexity, not whether to replace the curves or seek private data. Queue it at the final gate rather than making it a prerequisite for independent research and automated checks.

### Phase 1 — Open evidence and distribution inputs

Complete workstreams A–D: source registry, legal checks, public histogram extraction/reconstruction, wealth-component figure data, official reference estimates and a source/assumption inventory.

**Checkpoint:** identify which quantities are published, reconstructed, or modelled. Select a usable initial housing distribution and document the uncertain tail; identify the verified versus missing wealth-composition components. Do not block work waiting for unavailable individual records.

### Phase 2 — Curve-first extension, after implementation approval

Version/test the tax rules, preserve baseline/custom lines, add tax-onset and tier markers, introduce the aligned histogram and dynamic exposure counts, selected-home annotation and income-burden context. Add the decile composition chart using verified or explicitly estimated components.

**Acceptance:** a user can move debt, other assets, allowance and valuation tiers and explain why the full tax curve shifts or steepens; see how many homes lie in the changed range; and inspect housing/financial wealth/debt across wealth groups. The selected point never replaces the line.

### Phase 3 — Combined distribution-weighted estimates

First connect the housing distribution to an explicitly common-profile illustration. Then improve it with a compact open-data-informed mix of balance sheets and tax units, keeping low/base/high assumptions visible. Keep the combined playground usable while components are developed and evaluated.

**Acceptance:** calculations and weights are inspectable; uncertainty and evidence labels match the method; model aggregates are checked against available wealth/debt totals, counts and compatible official reform estimates without forcing an artificial exact match. Where correlations remain unknown, show sensitivity and avoid unsupported claims about precisely who benefits.

### Phase 4 — Evaluate the plots and refine

First complete authorised independent research and automated technical evaluation. Collect, rather than interrupt work for, decisions about explanatory text, accessibility, performance, shared settings and layout preferences. Then hold one final user evaluation of the coordinated plots, desktop/mobile layout and controls, alongside the evidence limitations. Optional heatmaps, marginal-slope plots and additional presets stay deferred until that final review. Secondary-residence policy and municipal property tax remain separate scope decisions.

### Required future checks

- Reproduce official worked examples, including no-tax cases. [S2]
- Test values immediately below, exactly at, and above each housing and tax threshold; ensure continuous tiered valuation and no fictitious tax jump at 14m.
- Verify separate tax-onset and valuation-tier markers, including the worked 1.6m-debt example and cases where the markers differ.
- Changing income alone must leave the kroner wealth-tax curve unchanged while updating its income ratio; handle zero income.
- Ensure the tax lines and histogram share the same x-axis and that policy-only changes leave underlying home values fixed.
- Histogram counts must sum consistently; label interpolated counts and unknown-tail assumptions, and distinguish properties from taxpayers.
- Wealth-composition charts must keep debt negative, asset values nonnegative, categories non-overlapping and top-1% detail separate from additive decile totals.
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
- **S14 — Skatteetaten debt allocation and valuation discounts:** https://www.skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/verdsettingsrabatt-ved-fastsetting-av-formue/ (worked example/historical discount table; verify target-year law before implementation).
- **S15 — SSB explanation of revised geographical valuation model, 1 December 2025:** https://www.ssb.no/priser-og-prisindekser/boligpriser-og-boligprisindekser/artikler/revidert-modell-for-beregning-av-formuesverdi-for-bolig
- **S16 — SSB LOTTE-Skatt overview:** https://www.ssb.no/forskning/offentlig-okonomi/inntektsfordeling/lotte-skatt (older background documentation; current scenario documents take precedence for sample/base-year details).
- **S17 — SSB, Vekst i husholdningenes finansformue i 2024, 19 February 2026, especially figures 2–3:** https://www.ssb.no/inntekt-og-forbruk/inntekt-og-formue/statistikk/inntekts-og-formuesstatistikk-for-husholdninger/artikler/vekst-i-husholdningenes-finansformue-i-2024 (article read during plan revision; extracting its public chart series is pending).

Source IDs S11–S13 from the first draft concerned commissioned/restricted data routes; they were removed to reflect the open-data-only decision. Remaining IDs are preserved so citations stay stable.

**Source trap:** SSB's report *Modell for beregning av boligformue*, published 27 February 2026 as Notater 2026/10, explicitly covers 2025 values and says a separate revised-model note will follow. Do not cite its accuracy statistics as if they validate the new 2026 model: https://www.ssb.no/priser-og-prisindekser/boligpriser-og-boligprisindekser/artikler/modell-for-beregning-av-boligformue-27022026

## 10. Progress tracker

### Completed research and planning

- [x] Read the existing app and relevant earlier plans; documented the foundations to retain and modelling assumptions to source.
- [x] Read relevant Marimo/WASM guidance; made no app or dependency changes.
- [x] Verified the 10-to-14-million threshold and 25%/70% included fractions against official sources.
- [x] Located and read official valuation-model, fiscal, and distributional analyses.
- [x] Found the published primary-home histogram for open-data extraction or approximation.
- [x] Checked candidate SSB table dimensions and extracted actual 2024 wealth-group cutoffs.
- [x] Identified estimation-vintage conflicts and person/household/property distinctions.
- [x] Revised the plan to preserve the full-range curves and make their threshold interactions central.
- [x] Removed all outreach, paid/commissioned-data and restricted-data routes, including the draft request.
- [x] Added coordinated curves/histogram, combined controls, income context and wealth-composition requirements.
- [x] Read the open SSB financial-wealth-by-decile article; full housing/debt composition remains to be established.
- [x] Reframed distribution-weighted approximations as an intended approach, with official estimates as benchmarks rather than preset-only restrictions.

### Pending discussion / open research

- [x] Follow-up user approval to implement incrementally, adapting measures to available open data.
- [x] Audit enacted-law references and dates, ordinary co-ownership guidance, joint-assessment rules and the statutory municipal-rate ceiling; archive findings in `data/wealth/legal_audit_2026.md`.
- [ ] Complete remaining legal detail: annual tax-resolution archive, municipality-specific 2026 decisions, and special property/taxpayer cases. Do not represent these as supported calculator features.
- [x] Save reproducible snapshots and claims ledgers for the implemented public references, official scenarios and legal audit.
- [ ] Extend those ledgers as remaining evidence gaps are investigated; do not imply all planned sources have been verified.
- [x] Investigate February versus May threshold-revenue estimates and comparison baselines within a bounded open-source search; record unresolved numerical reconciliation in `data/wealth/official_estimate_reconciliation_2026.md`.
- [x] Reconstruct public housing-figure bins from PDF vectors; document interpolation, assumed bin boundaries and unknown tail.
- [x] Extract S17 financial-wealth chart data; display verified financial composition. Matching housing/debt components remain an open extension.
- [ ] Select initial weighted profiles and low/base/high population assumptions using open data only.
- [ ] Final human review only: evaluate the implemented plot set/order, density, mobile/desktop layout, controls and queued scope decisions together after autonomous work.

### Implementation — for a later agent after approval

- [x] Test the simplified full-owner tax engine, including distinct tier/onset thresholds and the upper tax band. Full mixed-asset legal coverage remains excluded.
- [x] Preserve and enhance full curves; align reconstructed housing counts and show exposure estimates.
- [x] Add asset/debt/income controls, wealth brackets and verified financial-composition context in the same app.
- [x] Add distribution-weighted common-profile illustration with debt, tail and within-bin sensitivity.
- [ ] Refine national estimates with evidence-backed representative profiles and ownership mapping.
- [ ] At the final human-review gate, decide whether any optional extra plots are useful; do not add them to keep autonomous work busy.
- [x] Run Ruff, Marimo checks, unit tests, WASM export and actual browser interaction checks.

### Implementation record — 20 September 2026

Four reviewable `feat - wealth lab` JJ changes, without moving bookmarks or integrating into `main`:

1. **Tax mechanics:** progressive valuation, exact breakpoints, unclipped tax base, separate economic wealth, upper rate on net taxable wealth before the allowance, income-ratio zero handling and worked-example tests.
2. **Combined playground:** shared household/policy controls, retained dynamic tiers, 10/14/20m housing presets, full valuation/base/tax/difference/income curves, selected-value annotation, onset/upper-band markers and expandable explanations.
3. **Public reference:** immutable source snapshots with URLs, queries and checksums; SSB API v2 wealth brackets; embedded article chart series; reproducibly digitised Ministry housing figure. `data/wealth/README.md` documents populations, transformations, assumptions and exclusions. Compact data is generated into the notebook so WASM needs neither local helper modules nor live SSB calls.
4. **Weighted illustration:** exact piecewise-linear integration across the housing bins, one full-owner tax unit per property, common balance sheet linked explicitly to the personal controls, assumed 30–40m and 40m–tail-cap bins, nine debt/tail combinations and within-bin extrema. These are conditional modelling scenarios, not actual national receipts or confidence intervals. Browser testing also caught and fixed numeric-widget step origins that displayed a one-krone offset.

**Adaptation to available data:** S17 supplies financial assets by net-wealth decile, not a complete housing/debt balance sheet. Show that verified story with separate nested top-group detail; do not fabricate the missing components. Housing reconstruction totals about 1.71m properties in the displayed categories, with 2.03% in labels above 14m, consistent with the source's rounded 2%. The unshown tail is always labelled unknown; assumed tail values affect only the model.

**Verification performed:** `uv run ruff check .`; `uv run marimo check apps/building_taxation.py`; 14 unittest cases; snapshot/embedded-data consistency check; full `.github/scripts/build.py` export of all three apps/notebooks; final target re-export; Chrome execution of the exported WASM app, switching 14m→10m→14m and checking both household and aggregate results and chart rendering without browser errors. Repeat the browser test with `uv run scripts/check_wealth_browser.py`. The runtime uses only Marimo, Polars and Altair (WASM-compatible); extraction-only PyMuPDF and browser-test Playwright are not notebook dependencies.

**Follow-up substep completed:** a fifth JJ change compares compatible 2024 net-wealth-decile means from SSB 10318 and S17 figure 2. The new signed bar chart shows financial assets plus the derived residual **real assets minus total debt**, with published net wealth marked as a diamond. It does not label the residual housing equity or manufacture separate housing/debt data. Validation found a small source inconsistency: decile counts sum to one fewer household than the national total; their weighted net-wealth mean exceeds the published overall mean by about NOK 462 (0.012%). The app, source notes and regression tests retain/disclose this difference rather than force reconciliation. Now 16 unittest cases pass, including all ten accounting identities, missing-data rejection and chart schema validation; Ruff, Marimo, snapshot checks, target WASM export and Chrome reform/reset smoke checks were repeated successfully.

**Sixth substep completed — dated official context:** directly rechecked and archived S4 chapter 3, its index confirming 12 May / corrected 11 June 2026, and S6 question 1404 in `data/wealth/2026-09-20-official/`, with URLs and SHA-256 manifest. A static linked section beside the population illustration distinguishes the February −730m, May −830m, and 10→20m −1,250m estimates, their baselines, and accrued versus booked amounts. It separately explains May's +550m revision and −280m package, and S6's 114,600 people / 11,000 NOK average relief / 1.72m gross income among beneficiaries. No person-to-household decile join, national calibration, or enacted-law claim is made. Static Markdown intentionally adds no runtime dependency, network fetch or policy-control dependency. February/May reconciliation remains open. The source README now contains a claims ledger. All 18 unit tests, Ruff, Marimo checks, existing generated-reference verification, full three-notebook WASM build and Chrome interaction checks passed; browser checks additionally confirm the official table is unchanged through 14m→10m→14m.

**Final review / known limits:** chart density, responsive layout, control clarity, shared hover and richer tier highlighting are queued for the final human-review gate, not an immediate user task. Housing presets reset housing tiers only, not all custom tax controls. Legal enactment and ordinary ownership/assessment principles are now documented by the audit below; municipality-specific rates, special legal cases, calculator support for discounted-asset debt allocation, official-scenario reconciliation, matching housing/debt composition, population ownership mapping and credible national-profile modelling remain open. No behavioural effects, property tax, precise household percentiles, or inferred income of expensive-home owners are claimed.

### Legal audit and review sequencing — 20 September 2026

- [x] Move all human visual/preference/scope review to the final gate; independent evidence work and automated checks no longer depend on intermediate user inspection.
- [x] Verify housing-rule enactment: Lovvedtak 92, first/second consideration 15/18 June, sanctioned as law 23 June 2026 no. 66; part II takes effect immediately with effect from income year 2026 under part IV.
- [x] Archive nine primary/legal-guidance sources in `data/wealth/2026-09-20-legal/` with hashes. Document legal parameters, source-vintage distinctions and exclusions in `data/wealth/legal_audit_2026.md`; extend the source README's claims ledger.
- [x] Verify qualifying joint-assessment principles and exceptions; document whole-property valuation followed by ownership allocation, municipal-rate ceiling and mixed-asset debt rules.
- [x] Retain explicit gaps: municipality-specific decisions, annual tax-resolution archive and special legal cases. The current handbook still uses 10m examples; use it for allocation guidance, not the enacted 2026 threshold.
- [x] Keep calculator numbers/code unchanged. Any app provenance/eligibility clarification or ownership extension is a separate task, not an implicit consequence of the audit.
- [x] Verify new snapshot hashes/legal markers and derived ownership arithmetic; rerun the 18 existing unit tests and generated-reference check. Documentation-only change; no Marimo restart or new browser/WASM export.

### Official-estimate investigation — 20 September 2026

- [x] Following explicit user approval, re-read original archived sources and the claims ledger before searching; produce the full baseline/vintage/population/year/accounting/exclusions comparison matrix in `data/wealth/official_estimate_reconciliation_2026.md`.
- [x] Archive six primary sources in new immutable `data/wealth/2026-09-20-reconciliation/` with URLs/date/SHA-256 hashes; preserve all earlier snapshots.
- [x] Establish that the original May proposition already gives −830m and neither linked correction letter revises it. The corrected-edition date does not explain the difference.
- [x] Verify February's published manuscript explicitly compares −730m with 2025 and reports a −280m package total. Matching package totals are not proof of matching counterfactuals.
- [x] Distinguish SSB's published explanation of January versus earlier model estimates from the still-unexplained February/May threshold difference. Complete six search queries plus direct-source link follow-up; record poor search coverage and the limited negative finding.
- [x] Leave calculator, dependencies, embedded values and packaging unchanged; do not calibrate or invent a numerical bridge.

**Outcome:** bounded documentary task complete; numerical reconciliation remains an evidence gap. Verification passed: all six new source hashes, original-May/February-manuscript evidence markers, 18 unit tests, generated-reference consistency and Ruff. Diff review confirms evidence/documentation-only scope. No new WASM/browser run is needed for this evidence-only work.

**Next independent plan task, subject to authorisation:** matching housing/debt composition and ownership/tax-unit mapping feasibility using public sources. Reopen official-estimate reconciliation only for a concrete new public lead. Human dashboard evaluation stays at the end.
