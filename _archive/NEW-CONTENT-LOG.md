# NEW-CONTENT-LOG

Every piece of newly written content added by the notes consistency &
enrichment pass, so it can be reviewed in situ. Nothing here is existing
economics wording; it is all new prose written for this pass.

Branch: `notes-consistency-pass`. The batch plans this was built from are
retired; see `PROJECT-LOG.md`.

## Batch 1 — AQA Microeconomics

9 components across 8 of 54 pages. 46 pages received nothing.

| File | Line | Type | Sits under | What it adds |
| --- | ---: | --- | --- | --- |
| `aqa-a2-micro/1-3-2-price-income-and-cross-elasticities-of-demand.html` | 270 | worked example | Price Elasticity of Demand (PED) | Calculates PED from a £3.00→£3.60 latte price rise; shows both percentage changes and the revenue consequence |
| `aqa-a2-micro/1-3-2-price-income-and-cross-elasticities-of-demand.html` | 299 | exam tip | Price Elasticity of Demand (PED) | PED is always negative; classify on magnitude, not sign |
| `aqa-a2-micro/1-3-4-price-elasticity-of-supply.html` | 273 | worked example | Interpreting PES Values | Same 25% price rise in the short run and long run, giving PES 0.4 then 2.0 |
| `aqa-a2-micro/1-4-4-costs-of-production.html` | 223 | worked example | Key Definitions | Four-row cost schedule deriving TC, AC and MC, showing MC cutting AC at its minimum |
| `aqa-a2-micro/1-4-5-economies-and-diseconomies-of-scale.html` | 385 | exam tip | Diseconomies of Scale | Diminishing returns (short run, MC) vs diseconomies of scale (long run, LRAC) |
| `aqa-a2-micro/1-4-6-marginal-average-and-total-revenue.html` | 272 | worked example | Revenue in Imperfect Competition | TR/AR/MR schedule showing MR below AR and TR peaking where MR crosses zero |
| `aqa-a2-micro/1-4-7-profit.html` | 207 | exam tip | Key Definitions | Normal profit is a cost; a firm earning it sits at AR = AC |
| `aqa-a2-micro/1-5-5-oligopoly.html` | 253 | worked example | Concentration Ratios | 3-firm concentration ratio from six firms' sales, giving 90% |
| `aqa-a2-micro/1-6-1-the-demand-for-labour-marginal-productivity-theory.html` | 248 | worked example | The Marginal Revenue Product Theory | MPP and MRP schedule; how many workers are hired at a £80 wage |

Line numbers are the position of the opening `<div>` at the time of the
commit that added it.

**Every figure was verified by recomputation**: the cost schedule's MC genuinely
crosses AC between Q=30 and Q=40; TR genuinely peaks where MR changes sign; the
MRP example genuinely gives three workers at a wage of £80; 540 ÷ 600 = 90%.

### Style conformance

All nine follow the exemplar pattern from AQA 2.1.3, 2.1.4 and 2.4.1:

- worked examples open with `<h3>Worked Example: …</h3>`, present a table, and
  close by interpreting the number rather than the arithmetic
- multi-column comparisons use `table-container` + `concept-table`; running
  vertical calculations use a bare `calculation-table`
- exam tips are a single `<p>` with a bolded lead sentence and no heading, and
  each corrects a specific confusion rather than restating theory
- UK English, £ sterling, hyphen as the dash character

## Batch 2 — AQA Macroeconomics

3 components across 3 of 25 pages. 22 pages received nothing. The batch is small
because 5 of the 25 already carried components (the three exemplars plus 2-4-2 and
2-4-4), and because this directory already works most of its numbers through.

| File | Line | Type | Sits under | What it adds |
| --- | ---: | --- | --- | --- |
| `aqa-a2-macro/2-1-2-macroeconomic-indicators.html` | 293 | worked example | Unemployment Indicators | Unemployment and employment rates from a 40m working-age population, showing why the two do not sum to 100% |
| `aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html` | 324 | worked example | Calculating the Multiplier | Multiplier from MPS, MPT and MPM given separately; reconciles 1/MPW with 1/(1−MPC) |
| `aqa-a2-macro/2-6-3-the-balance-of-payments.html` | 284 | worked example | Current Account Deficits and Surpluses | Current account balance summed from its four components, giving −£50bn |

**Figures verified by recomputation**: 2 ÷ 28 = 7.1% and 26 ÷ 40 = 65%; MPW 0.4 →
multiplier 2.5 → £10bn, with the saving-only error giving £40bn; current account
−90 + 80 − 25 − 15 = −£50bn.

The 2-1-2 example also settles open audit flag C5: it defines the labour force
explicitly as employed plus unemployed, so the unemployment-rate formula and the
economically-inactive prose above it now agree on the page.

## Batch 3 — Edexcel Theme 1

5 components across 4 of 22 pages. 18 pages received nothing.

Three of the five are **byte-identical reuse** of components already applied to the
AQA twin pages, verified by hashing: `1-2-3` is word-for-word identical to
`aqa-a2-micro/1-3-2`, and `1-2-5` is 94% identical to `aqa-a2-micro/1-3-4`. Writing
different examples for identical pages would be maintenance debt with no gain.

| File | Line | Type | Sits under | What it adds |
| --- | ---: | --- | --- | --- |
| `edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html` | 270 | worked example | Price Elasticity of Demand (PED) | PED from a £3.00→£3.60 price rise — **reused verbatim from AQA 1-3-2** |
| `edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html` | 301 | exam tip | Price Elasticity of Demand (PED) | Classify PED on magnitude, not sign — **reused verbatim from AQA 1-3-2** |
| `edexcel-theme-1/1-2-5-price-elasticity-of-supply.html` | 273 | worked example | Interpreting PES Values | Same 25% price rise short run vs long run — **reused verbatim from AQA 1-3-4** |
| `edexcel-theme-1/1-2-8-producer-consumer-surplus.html` | 241 | worked example | Consumer & Producer Surplus at Market Equilibrium | Consumer and producer surplus as triangle areas, £250 and £200 |
| `edexcel-theme-1/1-2-9-indirect-taxes-subsidies.html` | 243 | worked example | Tax Incidence | Consumer £138, producer £46, government revenue £184 from a £2 specific tax |

**Figures verified by recomputation**: consumer incidence £138 + producer £46 =
government revenue £184 exactly, with consumers bearing 75%; surplus
½ × 50 × 10 = £250 and ½ × 50 × 8 = £200, social surplus £450.

`1-2-4-supply` was deliberately given nothing: open audit flag C1 is unresolved
there, so the page still contradicts itself between its Figure 1 caption and the
bullets below it. It is the natural home for a movement-versus-shift tip once C1
is fixed.

## Batch 4 — Edexcel Theme 2

5 worked examples across 5 of 24 pages. 19 pages received nothing.

Larger than batches 2 and 3 because all three exemplar pages are AQA and Edexcel has
none, so an AQA student saw these core macro calculations worked and an Edexcel
student saw none of them. Three components are reused verbatim from an AQA page —
approved explicitly — and hash-verified as identical.

| File | Line | Type | Sits under | What it adds |
| --- | ---: | --- | --- | --- |
| `edexcel-theme-2/2-1-2-inflation.html` | 251 | worked example | How It's Calculated | Basket cost → CPI 100/105/109.2 → inflation 5% then 4% — **new** |
| `edexcel-theme-2/2-1-3-employment-unemployment.html` | 179 | worked example | Key Definitions | Unemployment 7.1% and employment 65% from a 40m population — **reused verbatim from AQA 2-1-2** |
| `edexcel-theme-2/2-1-4-balance-of-payments.html` | 220 | worked example | The Current Account | Current account −£50bn from four components — **reused verbatim from AQA 2-6-3** |
| `edexcel-theme-2/2-2-1-aggregate-demand.html` | 253 | worked example | The Components of AD and Their Relative Importance | AD = £1,960bn; shares corroborate the page's stated 60/14/25% — **new** |
| `edexcel-theme-2/2-4-4-the-multiplier.html` | 321 | worked example | Calculating the Multiplier | Multiplier 2.5 from MPS/MPT/MPM, £4bn → £10bn — **reused verbatim from AQA 2-2-4** |

**Figures verified by recomputation**: 504 ÷ 480 × 100 = 105 and 524.16 ÷ 480 × 100
= 109.2, giving 5% then 4% inflation; AD 1,200 + 280 + 500 − 20 = £1,960bn with
shares 61 / 14 / 26 / −1%, matching the page's own "around 60%", "around 14%" and
"around 25%".

`2-1-3` is the one component in this pass that introduces a formula rather than
demonstrating one the page already states — the page defines the Labour Force but
gives no rate formula. Flagged in the plan and approved on that basis.

## Batch 5 — Edexcel Theme 3

5 of 6 planned components applied across 5 of 20 pages. 15 pages received nothing.

**No new prose.** Every component is an existing AQA component reused verbatim and
hash-verified identical. Theme 3 maps almost one-to-one onto AQA micro 1.4–1.6.

| File | Line | Type | Sits under | Reused from |
| --- | ---: | --- | --- | --- |
| `edexcel-theme-3/3-3-1-revenue.html` | 264 | worked example | Revenue in Imperfect Competition | AQA 1-4-6 |
| `edexcel-theme-3/3-3-2-costs.html` | 210 | worked example | Key Definitions | AQA 1-4-4 |
| `edexcel-theme-3/3-3-3-economies-diseconomies-of-scale.html` | 358 | exam tip | Diseconomies of Scale | AQA 1-4-5 |
| `edexcel-theme-3/3-3-4-normal-profits-supernormal-profits-losses.html` | 194 | exam tip | Key Definitions | AQA 1-4-7 |
| `edexcel-theme-3/3-5-1-demand-for-labour.html` | 228 | worked example | The Marginal Revenue Product Theory | AQA 1-6-1 |

**Sixth component, applied after the N5 fix:**

| File | Line | Type | Sits under | Reused from |
| --- | ---: | --- | --- | --- |
| `edexcel-theme-3/3-4-4-oligopoly.html` | 248 | worked example | Concentration Ratios | AQA 1-5-5 |

That page described a 3-firm ratio as covering "the top five firms" (flag N5). The
author authorised a single explicit exception to the no-wording-changes rule to
correct it — "five" to "three", one word, the only wording change in this pass —
after which the component was applied.

## Batch 6 — Edexcel Theme 4

3 worked examples across 3 of 21 pages. 18 pages received nothing.

Smaller than Theme 3 because Theme 4 is largely Edexcel-only content with no AQA
counterpart, and because the notes already do the arithmetic where it matters —
`4-1-2` computes opportunity cost for both countries and `4-5-3` already separates
deficit from debt.

| File | Line | Type | Sits under | What it adds |
| --- | ---: | --- | --- | --- |
| `edexcel-theme-4/4-1-4-terms-of-trade.html` | 198 | worked example | Definition and Calculation | ToT index across three years: 100, 94.6, 104.5 — **new** |
| `edexcel-theme-4/4-1-7-balance-of-payments.html` | 258 | worked example | Current Account Deficits and Surpluses | Current account −£50bn — **reused verbatim from AQA 2-6-3** |
| `edexcel-theme-4/4-1-9-international-competitiveness.html` | 216 | worked example | Definition and Measures | Unit labour costs £8,000 vs £7,000 across two countries — **new** |

**Figures verified by recomputation**: 106 ÷ 112 × 100 = 94.6 and 115 ÷ 110 × 100 =
104.5; 4,800,000 ÷ 600 = £8,000 and 7,000,000 ÷ 1,000 = £7,000, so A is 14% higher.

The current account component now appears on **three** pages — `aqa-a2-macro/2-6-3`,
`edexcel-theme-2/2-1-4` and here — because Edexcel covers the balance of payments in
both Theme 2 and Theme 4. Flagged in the plan and approved explicitly.

The terms of trade example has no counterpart anywhere on the site: AQA has no terms
of trade page.
