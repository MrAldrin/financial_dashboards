# Supported wealth-tax scenarios (T2)

Specification dated 21 September 2026. Educational standard-rate model, not a tax return or eligibility decision. T2 preserves the full-owner baseline.

## Evidence and bounded follow-up

Sources are immutable in `data/wealth/2026-09-20-legal/`; URLs and SHA-256 hashes are in its manifest. Substantive provisions were reread for this specification:

- [Skatteloven § 4-10(2)](https://lovdata.no/dokument/NL/lov/1999-03-26-14/§4-10), `law-housing.html`: 25% through 14m, 70% of excess. [Law 23 June 2026 no. 66](https://lovdata.no/dokument/LTI/lov/2026-06-23-66), `amendment.html`, II/IV: effective for income year 2026.
- [Skatte-ABC B-11-2.7.1](https://www.skatteetaten.no/rettskilder/type/handboker/skatte-abc/gjeldende/b-11-bolig--formue/B-11.002/B-11.012/), `abc-calculation.html.gz`: test whole-property value, then allocate by ownership. Its 10m examples are outdated; only the allocation method is used, with enacted 14m parameters.
- [§§ 2-10, 2-12, 2-16](https://lovdata.no/dokument/NL/lov/1999-03-26-14/§2-10), `law-joint.html`: joint wealth assessment, marriage-year/separation exceptions and specified reporting pensioner cohabitants. § 2-13 allocation of the resulting bill between spouses is not implemented.
- [Agency 2026 rate table](https://www.skatteetaten.no/satser/formuesskatt/), `rates.html`: allowance 1.9m; upper boundary 21.5m before allowance; both double for qualifying joint assessment. Standard municipal 0.35% plus state 0.65%/0.75% gives 1%/1.1%, not universal municipal rates.
- § 4-19, `law-housing.html`: discounted-asset debt allocation is outside the simplified portfolio.

One targeted search on 21 September (`site.stortinget.no "skatt av inntekt og formue" "2026" "1 900 000"`) returned no results. No annual-resolution document was found or newly archived; this is a bounded search limitation, not evidence of absence. Rate support remains the archived agency table. No general legal survey was repeated.

## Supported inputs and order of calculation

One ordinary primary residence, one selected tax unit. The input V is the **whole property's** calculated/documented market-value scenario, not the price of the owner's share. Share s is finite, 0 ≤ s ≤ 1 (default 1). All included ownership must qualify as primary residence; the app does not decide residence status.

1. Whole-home valuation F(V) = 0.25 min(V,14m) + 0.70 max(V−14m,0).
2. Tax-unit housing valuation H = s F(V), never F(sV).
3. Tax-unit net tax wealth N = H + A − D. A is undiscounted assets and D is deductible debt **already allocated to this tax unit**. Neither is multiplied by s. Income I likewise belongs to this unit and affects only tax/income (undefined when I=0).
4. With m=1 individual or m=2 qualifying joint, allowance B=1.9m×m and upper boundary U=21.5m×m. Tax = 0.01 min(max(N−B,0),U−B) + 0.011 max(N−U,0). Never multiply the final tax by s.
5. Economic net wealth = sV + A − D. This tax unit is not necessarily an SSB statistical household; comparison with household wealth brackets is illustrative, not a personal percentile.

Sandbox valuation tiers and rates remain hypothetical alternatives. Their whole-property valuation is allocated in the same order. Exact onset/upper-band curve crossings invert F against (target−A+D)/s. With s=0, positive housing targets are never reached; targets already met by A−D are reached at V=0. Zero share does not erase other-asset tax or debt.

Supported cases:

- Full-owner individual: s=1, joint off; unchanged default.
- Fractional individual: use that person's share and allocated assets/debt/income. Ordinary cohabitants run separate scenarios, never combine merely because they live together.
- Qualifying joint unit: use the sum of its members' primary-home shares (at most 1), combined assets/debt and optional combined income. A 50/50 qualifying couple owning the whole home enters s=1, not 0.5. The 14m housing tier never doubles.
- Joint unit owning only part of the property: same formula with its combined share; outside owners are excluded.
- Zero-share mathematical edge: no housing exposure, but the supplied tax-unit portfolio remains taxable.

## Worked examples / executable expectations

All amounts NOK; standard reference rules. These are derived examples, not published 2026 worked examples. Unless stated, A=D=0.

| V | s | Unit | H | Tax |
|---:|---:|---|---:|---:|
| 14,000,000 | 1 | individual, D=1,600,000 (default) | 3,500,000 | 0 |
| 16,000,000 | 0.5 | individual | 2,450,000 | 5,500 |
| 16,000,000 | 0.25 | individual | 1,225,000 | 0 |
| 16,000,000 | 0.75 | individual | 3,675,000 | 17,750 |
| 16,000,000 | 1 | qualifying joint | 4,900,000 | 11,000 |
| 16,000,000 | 0.5 | qualifying joint | 2,450,000 | 0 |
| 16,000,000 | 0.5 | individual, A=1,000,000, D=200,000 | 2,450,000 | 13,500 |
| any | 0 | individual, A=22,500,000 | 0 | 207,000 |
| any | 0 | joint, A=43,000,000 | 0 | 392,000 |
| any | 0 | joint, A=45,000,000 | 0 | 414,000 |

For the 50% individual at 16m, incorrectly valuing the 8m share separately gives 2m rather than 2.45m; halving the full-owner 30,000 tax gives 15,000 rather than 5,500. For separate 25%/75% owners the combined bill is 17,750, not the qualifying joint full-owner 11,000. A=1m/D=0.2m half-owner example has economic net wealth 8.8m; I=900,000 gives 1.5% burden.

Tests must cover full-owner T0 outputs, uneven shares, joint bands, valuation/onset/upper-band continuity, exact fractional crossing insertion, zero share/income, out-of-range/nonfinite shares and invalid numeric inputs.

## Explicit exclusions and population boundary

No eligibility determination for marriage year, separation, pension/reporting status, death, children, cross-border or other special taxpayers. Selecting joint is an assertion of qualification, not certification. No secondary-residence or mixed-residence calculation: a resident individual may model their own qualifying share, but the nonresident co-owner's bill is not computed. Joint shares with different residence classifications are excluded. No multi-unit special buildings, multiple homes, detailed valuation appeals/carry-forward, discounted securities/business assets, statutory mixed-asset debt allocation, spouse bill allocation, municipality-specific rates or property tax.

Amounts must be finite and nonnegative; allowance cannot exceed the upper threshold; assessment flag must be boolean. Unsupported legal facts cannot be detected from numeric inputs: they are excluded by the input contract and visible explanations, not claimed to be automatically rejected.

The legacy population illustration retains **one full-owner tax unit per property** with selected common debt/assets/assessment. Personal ownership share must not propagate into its weights or liabilities. No national ownership distribution is inferred. Static public references and official fiscal estimates stay unchanged. T3 is a separate task.
