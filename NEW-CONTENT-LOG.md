# NEW-CONTENT-LOG

Every piece of newly written content added by the notes consistency &
enrichment pass, so it can be reviewed in situ. Nothing here is existing
economics wording; it is all new prose written for this pass.

Branch: `notes-consistency-pass`. Plan: `PLAN-enrichment-aqa-micro.md` (batch 1).

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
