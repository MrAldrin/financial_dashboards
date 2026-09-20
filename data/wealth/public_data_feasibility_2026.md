# Public housing/debt composition and ownership feasibility

**Investigated:** 20 September 2026. **Scope:** bounded open-source documentary investigation; no calculator, generated reference, dependency or packaging changes. All new response bytes are in `2026-09-20-feasibility/`, with exact GET URLs (including selection queries), retrieval dates and SHA-256 hashes in `manifest.json`. Earlier snapshots remain unchanged.

## Result and recommendation

1. **A complete coarse balance-sheet view is feasible by household type or main earner's age.** SSB 10316/10317 publish primary housing, secondary housing, real capital, financial assets, total debt and counts for the same groups. These are means over all households in each group, not only owners. This is a useful evidence-supported alternative to inventing wealth-decile portfolios.
2. **Matching housing and debt components by economic-net-wealth decile were not found in this search.** Preserve the verified 2024 join of 10318 and S17 financial-wealth means, including its published count/weighted-mean discrepancies. Its residual remains **real assets minus total debt**, not primary-home equity.
3. **Some joint housing/debt information is published, but on a different basis:** survey table 14066 gives estimated home values and loan means by mortgage-size group. This is not a wealth-decile distribution, administrative market valuation, or complete household portfolio. In the extraction, estimated home values are missing for 2024 but available for 2025.
4. **Ownership prevalence is not an ownership-share/tax-unit mapping.** Revised register tables jointly classify tenure and household type; a method report also publishes owner–dwelling linkage totals. Neither supplies the distribution of fractional ownership, co-owners' residence/tax status and balance sheets conditional on home value. A national receipts estimate remains assumption-dependent, not identified by these aggregates.

**Recommended next separately authorised step:** add a modest, descriptive household-type composition reference from 10316 (or age from 10317), retaining the existing wealth-decile view and full curves. Separate primary housing, secondary housing, other real assets, financial assets and negative total debt; disclose rounding and mixed valuation definitions. Do not automatically load group means as representative taxpayers or recalibrate the common-profile illustration. This recommendation is not implementation approval; visual choices remain at the final human-review gate.

## Evidence definitions and join rules

**H24:** Income/wealth-statistics private households, income year 2024, excluding student households; wealth stocks at year-end. A student household has a main earner who is neither primarily employed nor a benefit recipient and at least one member receiving a student loan. Tables 10315–10319 record the February 2026 correction to bank deposits/foreign wealth. Table 10316 additionally documents exclusion of lone children under 18. Its total and 10317's total both equal 2,616,826, matching the existing 10318 national count.

**Valuation is not universally market value:** primary/secondary housing, commercial property, forest and farms use estimated market values; other property, business equipment and household contents retain tax-value measures. Primary housing is the owner's registered residence at year-end; farm dwelling houses are not included in that component. Financial wealth is adjusted for applicable valuation discounts, but unlisted shares/other assets can remain imperfectly valued; pension entitlements are excluded. Total debt is before tax-related debt reductions and includes housing-company debt shares. These are SSB statistical definitions, not a complete economic balance sheet or the legal taxable base. [F1, F2]

**R25:** Register-based housing conditions on **1 January 2025**, using the revised series retrieved in September 2026. Private households/persons linked to a dwelling; domestic students are not excluded as in H24. Institutions and other non-private households are outside scope; the statistics page reports about 39,000 households / 64,000 people omitted because they cannot be linked to a dwelling. A household is an owner household if at least one resident is identified as owner. Person counts classify **household tenure**, not each person's legal ownership. Income groups use the previous year's income. [F3]

**S24/S25:** EU-SILC housing survey, 2024/2025 interview years; sample drawn from resident persons aged 16+ outside institutions, with household weights for household results. Household definition includes shared food budget. No H24-style student-household exclusion is specified. Mortgage/home-value information is principally self-reported; missing mortgage information can use register total debt **after debt reduction**. Other-property loans are outside the current-home mortgage measure. Survey weights, non-response and imputation apply; respondent counts are not population weights. [F4]

**Join rule:** matching years or labels such as “decile”, “couple” or “owner” are insufficient. Require the same population, grouping/rank, valuation, denominator and time. Published component means within a common group support additive accounting. They do not recover the within-group joint distribution needed for nonlinear tax calculations. Separate age, household-type, income and wealth marginal tables cannot be cross-joined into observed records.

## Feasibility matrix

**P** = directly published; **R** = reconstructable arithmetic from compatible published aggregates; **A** = assumption-dependent; **U** = not found for the requested joint mapping within this bounded search. U does not mean that SSB lacks the underlying records.

| Target | Status and exact usable grouping | Population / unit / year / valuation | Join compatibility and remaining gap |
|---|---|---|---|
| Primary housing | **P** 10315 national totals/nonzero shares; 10316 household type; 10317 main-earner age | H24; million NOK totals or NOK mean; 10315 means among those with amounts, 10316/17 over all group households; estimated market value, excluding farm dwelling houses | **U** same-net-wealth-decile component. Household-type/age means cannot be assigned to wealth deciles or interpreted as a property-price histogram. |
| Secondary housing and other real assets | **P** secondary housing and total real capital in 10315/16/17; **R** other real assets = real capital − primary − secondary housing | H24; same denominators within 10316/17; real capital uses mixed estimated-market/tax definitions | Residual is other real assets, not just holiday homes. **U** net-wealth-decile split. Components are nested: do not stack total real capital alongside its subcomponents. |
| Financial assets | **P** S17 figures 2–3 by economic-net-wealth decile, with nested top groups in figure 3; 10316/17 by type/age | H24; figure 2 NOK means; figure 3 rounded percentages; financial valuations before applicable discounts | Existing S17 + 10318 join remains valid. **R** net wealth − financial assets = real assets − total debt. 06886 ranks by financial wealth and is **not** a replacement for S17's net-wealth ranking. |
| Total debt | **P** 10315/16/17 national/type/age values | H24; full debt before tax-related reduction, including housing-company shares; not mortgage-only | **U** debt by the same net-wealth deciles. 07894 is ranked by total income, not wealth. Cannot separate debt and real assets from their difference alone. |
| Mortgage-specific debt | **P** 14059 mortgage bands by tenure, 14062 by household type; 14065/66 mortgage means and other indicators by tenure/loan band | S24/S25; percentage, NOK mean, respondent counts. Loans secured on current home, not just purchase finance; imputation caveat above | 14066 supplies genuine grouped joint home-value/loan context in 2025, but **U** matching H24 net-wealth rank or full balance sheet. **A** transferring it to H24/expensive-home owners. Total debt − student debt − unsecured debt is **not** an observed mortgage measure. |
| Ownership shares / number of actual owners | **P** Notater 2026/17 pp. 18–19 gives aggregate 2024 owner–dwelling linkage totals; **U** fractional-share distribution conditional on home values/wealth | Administrative linkage-file units, not H24 households; registered owners believed to live in the dwelling; address matching can be less precise than dwelling ID | Linkage totals do not reveal whether co-owners share one tax unit, their fractional interests or other assets/debt. Equal 50/50 splitting, one tax unit per property, or applying an average owner multiplier are **A**, not observed mappings. |
| Residence / owner-occupancy status | **P** 14890/91 tenure by region, 14898 tenure × household type, 14900 tenure × income groups; tax primary/secondary totals in 08815/14781 | R25 counts/percentages versus taxable-person components in final 2024 / preliminary 2024–25 tax data; different universes and valuation concepts | Describes owner-household prevalence, not every owner's primary/secondary classification. **U** joint owner-residence/share/value mapping. “Andels- eller aksjeeier” is a tenure category, not a published fractional share. |
| Household composition | **P** 10316 type × balance-sheet means/counts; 14898 type × tenure; 06071 person groups and 06076 household totals | H24 versus R25 / family-statistics 1 January population, not identical exclusions/calibration. “Couple” includes married, cohabiting and registered partners | **P** within-table cross-tabulations; **A** joining 10316 and 14898 to infer owner-specific portfolios. No wealth-decile × type × tenure matrix found. |
| Legal assessment units | **P** legal eligibility/allocation rules in the existing legal audit; **U** their joint observed frequency with property values, shares and portfolios in reviewed data | Person/qualifying joint unit for income year 2026, not statistical household, family or property | Marriage-year/separation exceptions and specified cohabitant eligibility matter. Even a count of married couples does not identify jointly assessed owner units. **A** national profile weights until those relationships are explicitly assumed. |

## Source/table inventory and negative controls

All table IDs below have new archived v2 metadata unless explicitly marked catalogue-only. API queries use `lang=no`; numerical selections are recorded verbatim in manifest URLs, not implied by table titles.

| Source | Dimensions / years checked | Why useful or rejected for the requested join |
|---|---|---|
| 10315 | Wealth component × measure × year, 2010–2024; extracted all 2024 cells | National sums, ownership/nonzero prevalence, conditional means. **Not** means over all households and no rank dimension. |
| 10316 | Household type × component/count × year, 2010–2024; all 2024 cells | Directly compatible component means within type; groups merge married/cohabiting couples. |
| 10317 | Main earner age × component/count × year, 2010–2024; all 2024 cells | Directly compatible component means within age; cannot identify age × type or age × wealth rank. |
| 10318 | Economic-net-wealth decile/top group × share/mean/cutoff/count × year | New metadata identical to the old snapshot. No separate housing/debt components. Existing 2024 numerical snapshot retained, not regenerated. |
| 10319 / 07894 | Total-household-income decile × net wealth / debt × year through 2024 | Different ranking from 10318. Income-decile debt is not wealth-decile debt. |
| 06886 | Financial-wealth decile × mean/share × year through 2024 | Different ranking from S17. S8's explanation explicitly describes this ranking; do not join decile numbers alone. |
| 08564 | Region × tax component × population-specific count/amount/mean × year through 2024 | Final tax totals, including state/municipal wealth tax; not housing attribution or owner linkage. Metadata distinguishes taxable persons and resident 17+ measures; main population basis changes in 2024. |
| 08603 | Region × income/wealth/debt/tax component × population-specific measure × year through 2024 | Taxable wealth, not H24 statistical wealth. Means with amounts versus all persons must be selected explicitly; no joint portfolios. |
| 08815 | Taxable wealth/debt/tax component × population-specific measure × year through 2024 | Primary/secondary **tax values**, person counts, conditional means; not property counts or market prices. 2024 financial-component definition changes documented. |
| 14781 | Region × primary/secondary housing tax value × age × sex × population × measure × 2024–2025 | Preliminary draft-return values; not final assessments. Under-17 coverage changes in 2025; preliminary geography uses 31 December residence rather than final-tax 1 January tax municipality. No share/value/wealth-rank mapping. |
| 09916 | Tax component × **taxable gross-wealth** decile × mean/person count × year through 2024 | Includes primary/secondary housing and debt, but resident taxable persons aged 17+ with amounts, not H24 households or economic net-wealth ranking. Cannot repair H24 missing components. |
| 05946 | Region × taxable-net-wealth interval × mean component × year through 2024 | Person-based taxable intervals, not household economic-net-wealth deciles; no separate primary housing component in measures. |
| 14890/91 | Region × tenure × person/household count or percentage × 2015–2025 | Extracted national 2025; person count means people in households of that tenure. |
| 14898 / 14900 | Region × tenure × household type / income group × measure × 2015–2025 | Extracted national 2025; genuinely joint tenure/type or tenure/income, but not wealth, fractional shares or assessment status. Income quartiles use equivalised after-tax income, not 10319's total-income deciles. |
| 14903 / 14917 | Region × crowding / building type × household measure × 2015–2025 | Checked links from statistics landing page; not ownership-share or portfolio tables. |
| 06071 / 06076 | Person sex/age/type / regional private-household totals; latest 2025 | Demographic context, not tax-unit identities. Family-statistics documentation explicitly notes differences from income-statistics household calibration. |
| 14059 / 14066 | Tenure / mortgage-size group × housing-finance indicators × year, 2011–2025 | Extracted all indicators for 2024–2025; preserve missing cells and status codes. |
| 14062 / 14065 | Household type × housing finance / tenure × owner mortgage costs, 2011–2025 | Additional metadata confirms coarser mortgage-context options, not wealth-decile or legal-unit coverage. |

### Verified coarse accounting, not a synthetic population

10316, `Hushaldstype=50`, 2024, gives these **all-household** means in NOK:

| Component | Mean |
|---|---:|
| Primary housing (`MarknverdiPri`) | 3,151,100 |
| Secondary housing (`MarknverdiSek`) | 349,000 |
| Other real assets, derived: `Realkapital − MarknverdiPri − MarknverdiSek` | 297,600 |
| Financial assets (`SkattplKapital`) | 1,850,000 |
| Total debt (`Gjeld`), displayed below zero | −1,757,300 |
| Published net wealth (`FormueNettBerekn`) | 3,890,400 |

The five signed components sum to the published national mean. All 15 household-type groups and all seven age groups have nonnegative derived other-real-asset means. Their group counts each sum to 2,616,826. At group level, real capital + financial assets − debt differs from published net wealth by at most NOK 100, consistent with the precision of the published means; retain the values rather than forcing exact equality. National 10315 totals also have NOK 1 million accounting differences at published precision. No adjustment was made.

**Denominator trap:** 10315 primary housing has a 68.9% nonzero share and NOK 4,576,100 mean **among households with amounts**. The 10316 national mean is NOK 3,151,100 **over all households**. Neither is the mean whole-property value in the Ministry histogram. Multiplying rounded shares and rounded conditional means only approximates an unconditional mean; prefer the directly published 10316 value.

**Debt trap:** F1 explicitly warns that tax-return debt, student-loan records and unsecured-debt records can use different reporting times. Subtracting the latter two from total debt need not even reproduce a consistent “other debt” total; it certainly does not establish mortgage debt or housing equity.

### A useful but separate mortgage/home-value cross-tabulation

14066, 2025, provides the following pairs of published means:

| Current-home mortgage group | Mortgage mean, NOK | Self-reported estimated home sale value, NOK |
|---|---:|---:|
| Below 1m | 526,012 | 4,176,188 |
| 1–2m | 1,455,311 | 4,297,878 |
| 2–3m | 2,386,711 | 4,995,922 |
| Above 3m | 4,521,865 | 7,471,899 |

This demonstrates useful conditional information without claiming a net-wealth join. It gives home value **conditional on loan group**, not the loan distribution conditional on a 14m home. Reversing that relationship requires group frequencies and within-group distributions not supplied by these means.

The `Alle eiere` mortgage mean is 2,288,302, identical to `Boligeiere som har boliglån, i alt`: the variable definition conditions the mortgage mean on having a loan, even when the row is “all owners”. It must not be treated as zero-inclusive debt for all owners. The 4,279 responding owner households are a sample count, not a national weight. The 2024 `AntattSalgspris` cells are null; do not fill them with zero or carry 2025 prices backwards. No debt-free-home mortgage nulls were changed to numerical observations.

## What ownership statistics can actually map

### Revised tenure series: use the new vintage, not old headlines

The housing statistics page records a 2026 revision back to 2015, including owner-status classification. Notater 2026/17 (18 March) describes the then-proposed method; the current statistics page confirms its subsequent implementation. Its pre-revision figures must not be presented as the current series.

National 14891 for 1 January 2025 reports 2,610,377 linked households: 1,545,334 self-owner, 351,420 cooperative/share-owner and 713,623 renter households. The corresponding 14890 total is 5,490,986 **residents**, including children and non-owning partners. These are not legal owner or wealth-taxpayer counts. The owner-household sum is 1,896,754; it is not interchangeable with the approximately 1.71m reconstructed primary properties in the separate 2026 tax-card histogram.

14898 can answer, for example, how tenure varies by household type. It cannot say which adult owns which fraction, whether that adult lives elsewhere, or how jointly assessed spouses distribute other assets/debt. 14900's groups also overlap (income quartiles, low income, benefits, high debt burden); they must not be added as disjoint population weights.

### A published owner–dwelling linkage anchor, with a strict boundary

Notater 2026/17 pp. 18–19 describes an administrative source file combining Matrikkelen, SERG and residence information. More than one owner can appear for the same dwelling. It reports **1,860,803 unique dwelling units and 2,597,771 registered owners** in its 2024 file; table 3.1 describes unique person–dwelling links. This is evidence that properties and owners are not one-to-one, not a national conversion factor for the Ministry histogram.

The file concerns owners assumed to both own and live in a dwelling; ownership extraction is in early March and some address matches are below full dwelling precision. It does not publish fractional shares or co-owner joint-assessment status by price/wealth group. The separate tax-return exercise on p. 21 retains 2,611,618 selected primary-home/farm ownerships for **income year 2023**, one selected ownership per person. It is neither the same year's universe nor a count of all properties. Do not divide/multiply these totals into a synthetic national owner count.

The report shows that SSB can use detailed ownership records internally. It does not make those linked microdata an open published dataset. This investigation used the public report only; no access request or private-record extraction was attempted.

### Statistical couples are not legal joint assessment

10316 explicitly combines married couples, cohabitants and registered partners. The family-statistics definitions also classify some separated couples living at the same address as married couples. That is not the legal eligibility test in the existing [legal audit](legal_audit_2026.md), which documents separate assessment in the marriage year and separation exceptions, plus the special category of qualifying reporting cohabitants. Neither a two-adult household count nor even a demographic “married couple” count supplies observed joint-tax-unit weights.

For future ownership modelling, retain this order: whole property's value → each owner's share and primary/secondary residence status → owner/qualifying joint unit's assets and legally deductible debt → tax schedule → household presentation. No reviewed public table completes that chain with observed joint frequencies.

## Bounded search record

Before searching, read the active plan, source README/claims ledger, legal audit, estimate-comparison report, existing manifest and reference transformation script. Did not reopen February/May reconciliation.

**Six DuckDuckGo queries:**

- `site.ssb.no formue desil realkapital gjeld boligformue 2024`
- `site.ssb.no eierskap bolig eierandel husholdninger register selveier samboere`
- `site.ssb.no "nettoformue" "desil" "gjeld" "bolig"`
- `site.ssb.no "eierandel" "bolig" "ektepar"`
- `site.ssb.no "formue" "desiler" "realkapital"`
- `site.ssb.no "boliglån" "nettoformue" "desil"`

The first two located official statistics landing pages; later exact-term queries yielded no useful organic results. No claim rests on snippets. Opened primary pages, read definition/production/revision sections, followed the ownership report PDF, inspected S8's narrative and public chart configurations, and retained the already verified S17 extraction. S8 supplies national/age/distribution context, not the missing complete wealth-decile composition.

**Direct v2 catalogue searches**, archived with complete one-page responses (`pageSize=100`): `formue` (38 results), `nettoformue` (26), `desil` (15), `eierstatus` (17), `boliglån` (16). Inspected titles/dimensions and fetched the relevant metadata listed above. This revealed additional false friends (07894, 06886, 09916, 05946) and useful tenure/mortgage cross-tabs. Catalogue-only alternatives such as 10320 concern net-wealth intervals, not matching components. No claim of a full metadata audit of every catalogue result.

The `/statbank/list/ifhus` and `/statbank/list/boforhold` requests returned only client application shells; used the v2 catalogue instead. An initial guessed housing-survey URL returned 404; followed the working link from the register-statistics page. Those unsuccessful discovery responses are not included as evidence sources.

**Stopping boundary:** nine original candidate tables plus 16 follow-up metadata responses, five catalogue queries, nine small data queries, six official HTML pages and one report PDF (46 archived responses). Did not crawl every historical report, reconstruct confidential microdata, contact agencies, use paid data or commission tables. The negative finding is limited to this search; a concrete new matching public source would justify reopening it.

## Source register

Exact API and PDF URLs and query encodings are in the snapshot manifest. Human-readable primary links:

- **F1 — Household income/wealth definitions:** https://www.ssb.no/inntekt-og-forbruk/inntekt-og-formue/statistikk/inntekts-og-formuesstatistikk-for-husholdninger (`household-statistics.html`).
- **F2 — Hva er vanlig formue?:** https://www.ssb.no/inntekt-og-forbruk/inntekt-og-formue/artikler/hva-er-vanlig-formue (`ordinary-wealth.html`); existing plan S8.
- **F3 — Register housing conditions:** https://www.ssb.no/bygg-bolig-og-eiendom/bolig-og-boforhold/statistikk/boforhold-registerbasert (`housing-register.html`).
- **F4 — Survey housing conditions:** https://www.ssb.no/bygg-bolig-og-eiendom/bolig-og-boforhold/statistikk/boforhold-levekarsundersokelsen (`housing-survey.html`).
- **F5 — Families and households:** https://www.ssb.no/befolkning/barn-familier-og-husholdninger/statistikk/familier-og-husholdninger (`families.html`).
- **F6 — Ownership revision, Notater 2026/17:** https://www.ssb.no/bygg-bolig-og-eiendom/bolig-og-boforhold/artikler/boforholdsregisteret-dokumentasjon-og-revisjon-av-eierstatus-variabel (`ownership-revision.html`, linked `ownership-revision.pdf`), especially pp. 4, 18–21 and 26–28.
- **Tables:** `https://www.ssb.no/statbank/table/<ID>`; archived v2 metadata contain labels, category codes, units, notes and update dates. Data files preserve nulls/status codes; no generated dataset was substituted for response bytes.
- **Existing compatible evidence:** S17 `2026-09-20/article.html` and 10318 `2026-09-20/10318.json`; unchanged extraction in `scripts/build_wealth_reference.py`.

## Completion and verification

- [x] Record published, reconstructable, assumption-dependent and unavailable dimensions without inventing decile portfolios or ownership weights.
- [x] Archive 46 primary API/HTML/PDF responses in a new immutable snapshot; preserve previous snapshots.
- [x] Verify hashes, metadata selections, population/denominator warnings, coarse accounting and tenure totals; retain missing mortgage/home-value cells and rounded discrepancies.
- [x] All 18 existing unit tests, generated-reference consistency and Ruff passed. Ad-hoc checks verified all 46 new hashes plus every earlier manifest, metadata/catalogue completeness, component accounting, tenure sums, mortgage figures/nulls and definition markers. Evidence-only diff review confirms no code, old snapshot or embedded-data changes. No new WASM/browser run was needed for this documentary change.

The next implementation or modelling step requires separate authorisation. Human visual/scope evaluation remains at the plan's final gate.
