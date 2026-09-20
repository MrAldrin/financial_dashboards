# Legal evidence audit — Norwegian wealth tax, income year 2026

**Audited:** 20 September 2026. **Scope:** documentary audit, not legal advice or a calculator extension. The notebook, its numerical baseline and runtime dependencies are unchanged.

## Result

The dashboard's **14m / 25% / 70% primary-home reference is enacted law**, not merely a proposal. Law 23 June 2026 no. 66, part II, amended skatteloven § 4-10(2), third sentence. Part IV makes that amendment effective immediately **with effect from income year 2026**. Do not confuse this with the same amending act's separate 1 July rules. The consolidated law's overall “last changed / from 1 July” metadata is not the housing amendment's commencement rule.

The published 2026 allowance and standard combined rates also match the dashboard. Ordinary co-ownership and qualifying joint assessment must remain distinct. No evidence reviewed requires changing the calculator's supported full-owner numerical baseline. It remains a simplified model, not coverage of every taxpayer or municipality.

## Immutable evidence and reproduction

`2026-09-20-legal/manifest.json` records requested source URLs, retrieval date and SHA-256 hashes. Files contain fetched response bytes, not search snippets. `abc-calculation.html.gz` is the full raw handbook HTML, losslessly gzip-compressed to avoid retaining several megabytes of navigation uncompressed; its manifest also records the uncompressed hash. Read it with `gzip -dc` or Python's `gzip.decompress`. Existing snapshots were not overwritten.

Lovdata redirects section requests to chapter pages: `law-housing.html` contains chapter 4's valuation provisions, including §§ 4-10 and 4-19; `law-joint.html` contains §§ 2-10–2-16; `law-municipal.html` contains chapter 15. The amending-law request redirects to `https://lovdata.no/dokument/LTI/lov/2026-06-23-66`. HTML page navigation is not substantive evidence: use the sections named below.

## Adoption timeline

| Date | Event | Evidence and interpretation |
|---|---|---|
| 27 February 2026 | Government announces the proposed threshold increase | Previously archived presentation, `2026-09-20/housing.pdf`; announcement is not enactment. |
| 12 May 2026 | Prop. 95 LS submitted | Previously archived proposition/index and new parliamentary case page. Corrected edition dated 11 June is a document revision, not an adoption date. |
| 10 June 2026 | Innst. 459 L delivered | Parliamentary case timeline. |
| 15 June 2026 | First parliamentary consideration; Lovvedtak 92 | `adoption.html`, part II sets 14,000,000; part IV specifies income year 2026. |
| 18 June 2026 | Second parliamentary consideration | `case.html` and the amending act's legislative-history note. |
| 23 June 2026 | Sanction/enactment as law no. 66 | `case.html` explicitly associates Lovvedtak 92 with law 66; `amendment.html` contains the promulgated act. Housing provision commences immediately, with effect from income year 2026. |

Sources: [parliamentary case](https://www.stortinget.no/no/Saker-og-publikasjoner/Saker/Sak/?p=200312), [Lovvedtak 92](https://www.stortinget.no/no/Saker-og-publikasjoner/Vedtak/Beslutninger/Lovvedtak/2025-2026/vedtak-202526-092/), [promulgated amendment](https://lovdata.no/dokument/LTI/lov/2026-06-23-66).

## Legal parameter and claims ledger

| Claim | Evidence / status | Implication for the dashboard |
|---|---|---|
| Primary-home valuation includes 25% through 14m and 70% of the excess | **Verified statute:** § 4-10(2), `law-housing.html`; amendment parts II/IV. It refers to calculated or documented market value. | Existing continuous progressive valuation matches. No whole-home jump at 14m. |
| Owner can claim valuation based on documented market value | **Verified statute:** § 4-10(2). Detailed documentation/carry-forward administration is outside this audit. | Input is a chosen valuation scenario, not an official assessment or a guarantee that SSB's calculated value is correct. |
| Secondary dwelling is included at 100% | **Verified statute:** § 4-10(3). | Does not authorise adding secondary-home policy controls; remains separate scope. |
| 2026 personal allowance 1.9m; upper state-tax boundary 21.5m | **Verified current agency table:** `rates.html`. Annual parliamentary tax-resolution text has not yet been archived. | Upper boundary is net taxable wealth before subtracting the allowance, not 21.5m above the allowance. |
| Municipal table rate 0.35%; state 0.65% / 0.75% | **Verified current agency table:** `rates.html`. Combined 1.0% / 1.1% is arithmetic, not a guarantee for every municipality. | Current baseline is a standard-rate illustration. Preserve municipal-exception caveat. |
| Municipal wealth-tax rate need not equal the standard table everywhere | **Verified statutory framework:** § 15-2(1)(a) says Parliament sets maximum municipal wealth/income tax rates; § 15-1 covers annual state rates. | Do not call 1.0% / 1.1% universal. Specific 2026 municipal decisions and an exhaustive exception list remain unverified; no Bø or other local rate is asserted. Do not confuse municipal wealth tax with property tax. |
| Jointly assessed spouses share a wealth-tax unit | **Verified statute:** § 2-10, subject to exceptions in § 2-12; agency rate table explicitly doubles the allowance and upper boundary for qualifying joint assessment. | 3.8m allowance and 43m upper boundary for the supported joint unit; the property's 14m tier does not double. |
| Marriage alone always qualifies for joint assessment | **False as a general claim:** § 2-12 requires separate assessment in the marriage year and where separated or permanently apart at year-end; institutional residence alone is not permanent separation. | Assessment control must describe qualifying joint assessment, not every married couple. Do not infer status from number of adults. |
| All cohabitants are jointly assessed | **Unsupported/incorrect:** § 2-16 extends spousal provisions to the specified pensioner/reporting category, with its stated exception; agency rates separately identify meldepliktige samboere. | Ordinary cohabitants must not be combined automatically. Full eligibility/benefit-status determination is not implemented. |
| Same home can be primary for one co-owner and secondary for another | **Verified guidance:** `housing.html` (child/parents example); handbook B-11-2.7.1. | Ownership share and each owner's residence status precede tax-unit aggregation. |
| Housing tier is tested against whole-property value for ordinary co-ownership | **Verified allocation guidance, older threshold vintage:** handbook B-11-2.7.1 explicitly says the 70% test uses the whole property's market value, then illustrates proportional allocation. | Do not apply a fresh 14m allowance to each owner's share. For an ordinary primary-home owner with share s, inferred 2026 valuation is s × F(V, 14m), not F(s × V, 14m). Partial ownership is still unsupported by the app. |
| Debt can always be deducted in full with discounted assets | **False:** § 4-19(1)–(3) defines proportional debt reduction for specified assets, with joint spousal assets/debt and undiscounted primary-home value included in the allocation denominator. Primary home § 4-10(2) is not itself listed as a debt-reduction asset. | Full deduction is appropriate only within the existing simplified scope. Do not feed discounted shares into an undifferentiated “other assets” input and claim complete legal coverage. |

Sources: [2026 agency rates](https://www.skatteetaten.no/satser/formuesskatt/), [residential-property guidance](https://www.skatteetaten.no/person/skatt/hjelp-til-riktig-skatt/bolig-og-eiendeler/bolig-eiendom-tomt/formuesverdi/formuesverdi-bolig/), [valuation and debt statutes](https://lovdata.no/dokument/NL/lov/1999-03-26-14/§4-10), [joint-assessment statutes](https://lovdata.no/dokument/NL/lov/1999-03-26-14/§2-10), [rate-setting statutes](https://lovdata.no/dokument/NL/lov/1999-03-26-14/§15-3), [handbook allocation guidance](https://www.skatteetaten.no/rettskilder/type/handboker/skatte-abc/gjeldende/b-11-bolig--formue/B-11.002/B-11.012/).

## Source-version trap and derived ownership check

The retrieved **Skatte-ABC 2025/2026**, despite its `/gjeldende/` URL, still states the **10m** threshold in B-11-2.7.1. Its worked 16m-home example allocates half the property to a resident owner:

`0.5 × (0.25 × 10m + 0.70 × 6m) = 3.35m`.

That is evidence for the allocation method, not a current 2026 threshold. Applying the enacted 14m rule to the same ordinary ownership structure gives **2.45m**: `0.5 × (0.25 × 14m + 0.70 × 2m)`. This is our derived check, not a published 2026 worked example. Incorrectly applying the tier after splitting the property would give 2m and understate the resident owner's taxable property value.

The handbook separately treats buildings with five or more unsectioned dwelling units in B-11-2.7.2. Do not generalise the simple whole-property formula to all multi-unit buildings; the relevant dwelling unit and residence status matter. Those special cases remain outside calculator scope.

## Follow-ups — not silently implemented

1. **Documentation/UI provenance:** a separately authorised update can replace “published reference only” with a dated enacted-law citation, retaining the standard-rate and simplified-scope caveats. Current app wording is conservative, not a reason to change numbers.
2. **Assessment wording:** ensure the future user-facing joint option explains eligibility, including marriage-year/separation exceptions. This audit does not implement eligibility logic.
3. **Before partial ownership support:** model the whole property, individual shares and residence classification, then each tax unit's assets/debt/allowances; test uneven shares, mixed residence status and separate cohabitants. Do not merely multiply the final household tax by ownership share.
4. **Before municipal support:** archive the 2026 annual parliamentary tax resolution and applicable municipality-specific decisions. No exhaustive municipality audit or local preset was completed here.
5. **Before mixed-asset support:** separate asset categories and test statutory debt allocation. Current direct debt subtraction remains explicitly restricted.
6. **Remaining legal scope:** multi-unit properties, detailed meldeplikt eligibility, cross-border/special taxpayer rules and documentation/carry-forward procedures are not comprehensively audited. No implication of a production tax-advice engine.

Human review of these scope choices is queued at the plan's **final review gate**. Independent evidence work may proceed without asking the user to inspect screens.

## Audit verification record

- Opened the sources and checked the substantive sections above; search-result summaries were not used as proof.
- Checked the agreement between Lovvedtak 92, the parliamentary timeline, the promulgated act and consolidated § 4-10.
- Verified archived-file hashes, gzip round-trip hash, expected legal markers and the two ownership calculations with an ad-hoc check.
- No notebook, generated reference values, dependencies or browser packaging changed. Existing unit tests and generated-reference consistency were rerun; no new WASM/browser run was needed for this documentation-only change.
