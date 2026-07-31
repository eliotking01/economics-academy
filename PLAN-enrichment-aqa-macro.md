# PLAN — Part B, batch 2: AQA Macroeconomics (25 pages)

Phase 1B deliverable. **Nothing here has been applied.** Awaiting approval.

**Proposed: 3 worked examples across 3 pages. 22 of 25 pages get nothing.**

| | |
| --- | ---: |
| Worked examples | 3 |
| Exam tips | 0 |
| Pages receiving 1 | 3 |
| Pages receiving 0 | **22** |

---

## Why this batch is much smaller than batch 1

AQA macro is already the best-served directory on the site. Five of its 25 pages
carry components: the three exemplars (`2-1-3`, `2-1-4`, `2-4-1`, with 5, 5 and 2)
plus `2-4-2` and `2-4-4` with 2 and 1 exam tips. So a fifth of the batch is
enriched before this pass starts, and the exemplars in particular are already at
saturation.

More importantly, this directory **does** work its numbers through. Where AQA micro
stated formulas and never used them, macro repeatedly does the opposite:

- `2-6-2` derives comparative advantage from actual output figures and computes the
  opportunity cost ratios
- `2-2-4` already calculates a multiplier of 5 from an MPC of 0.8 and states the
  resulting £5bn GDP effect
- `2-6-3` explains that the balance of payments must balance, so a current account
  deficit is financed by a capital and financial account surplus
- `2-6-4` distinguishes revaluation and devaluation (fixed) from appreciation and
  depreciation (floating)
- `2-5-1` gives separate `key-definition` blocks for budget deficit, fiscal deficit,
  national debt, cyclical deficit and structural deficit

Each of those was a candidate I expected to propose something for, and each turned
out to be already handled. What remains is three calculations that are genuinely
absent, all of them standard AQA exam questions.

---

## Proposed additions

### 1. `2-1-2-macroeconomic-indicators.html` — worked example

**Section:** "Unemployment Indicators", after the paragraph explaining the
economically inactive population.

**Why here:** The page carries **six formulas and almost no numbers**. It gives the
unemployment rate and employment rate formulas back to back, then notes that they
do not sum to 100% because of the economically inactive — which is the exact point
students get wrong, and the reason is a difference of *denominator* that the prose
states but never shows. One population breakdown makes both rates and the gap
between them concrete at once.

This also settles open audit flag **C5**, which asked whether the unemployment-rate
denominator matches the ONS/ILO "economically active" definition given a few lines
above: the example defines the labour force explicitly as employed plus unemployed,
so the two agree on the page rather than only by implication.

```html
              <div class="worked-example">
                <h3>Worked Example: Unemployment and Employment Rates</h3>
                <p>
                  An economy has a
                  <strong>working-age population of 40 million</strong>, made up
                  as follows:
                </p>
                <div class="table-container">
                  <table class="concept-table">
                    <thead>
                      <tr>
                        <th>Group</th>
                        <th>People</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>In employment</strong></td>
                        <td>26 million</td>
                      </tr>
                      <tr>
                        <td>
                          <strong>Unemployed</strong> (available and seeking
                          work)
                        </td>
                        <td>2 million</td>
                      </tr>
                      <tr>
                        <td><strong>Economically inactive</strong></td>
                        <td>12 million</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <table class="calculation-table">
                  <tr>
                    <td>Labour force</td>
                    <td>26m + 2m = 28m</td>
                  </tr>
                  <tr>
                    <td>Unemployment rate</td>
                    <td>\( \frac{2}{28} \times 100 = 7.1\% \)</td>
                  </tr>
                  <tr>
                    <td><strong>Employment rate</strong></td>
                    <td>\( \frac{26}{40} \times 100 = 65\% \)</td>
                  </tr>
                </table>
                <p>
                  The two rates use <strong>different denominators</strong>. The
                  unemployment rate is measured against the
                  <strong>labour force</strong> of 28 million; the employment
                  rate against the whole
                  <strong>working-age population</strong> of 40 million. That is
                  why 7.1% and 65% do not sum to 100% - the missing 12 million
                  are economically inactive and appear in neither rate.
                </p>
              </div>
```

*Arithmetic checked: 26 + 2 + 12 = 40; 2 ÷ 28 × 100 = 7.14% → 7.1%; 26 ÷ 40 × 100 = 65%.*

---

### 2. `2-2-4-aggregate-demand-and-the-level-of-economic-activity.html` — worked example

**Section:** "Calculating the Multiplier", after the existing MPC = 0.8 illustration.

**Why here:** The page gives three multiplier formulas — `1/(1−MPC)`,
`1/(MPS+MPT+MPM)` and `1/MPW` — but only ever demonstrates the first, with a single
leakage. The exam question is almost always the other way round: you are handed MPS,
MPT and MPM separately and must combine them. The classic error is dividing by the
saving figure alone, which here would overstate the effect fourfold.

Placing it after the existing illustration means the page moves from the simple case
to the exam case, and the closing line reconciles the two formulas so they are
visibly the same thing rather than two rules to memorise.

```html
              <div class="worked-example">
                <h3>Worked Example: The Multiplier with Several Leakages</h3>
                <p>
                  Out of every extra £1 of income, households in an economy save
                  10p, pay 25p in tax and spend 5p on imports. The government
                  raises its spending by <strong>£4 billion</strong>.
                </p>
                <table class="calculation-table">
                  <tr>
                    <td>Marginal propensity to save (MPS)</td>
                    <td>0.1</td>
                  </tr>
                  <tr>
                    <td>Marginal propensity to tax (MPT)</td>
                    <td>0.25</td>
                  </tr>
                  <tr>
                    <td>Marginal propensity to import (MPM)</td>
                    <td>0.05</td>
                  </tr>
                  <tr>
                    <td>Marginal propensity to withdraw (MPW)</td>
                    <td>0.1 + 0.25 + 0.05 = 0.4</td>
                  </tr>
                  <tr>
                    <td>Multiplier</td>
                    <td>\( \frac{1}{0.4} = 2.5 \)</td>
                  </tr>
                  <tr>
                    <td><strong>Final change in real GDP</strong></td>
                    <td>£4bn × 2.5 = <strong>£10bn</strong></td>
                  </tr>
                </table>
                <p>
                  <strong>Every</strong> leakage counts, not just saving. Using
                  the saving figure on its own would give
                  \( \frac{1}{0.1} = 10 \) and a £40bn effect, four times too
                  large. The two formulas agree: MPC here is
                  \( 1 - 0.4 = 0.6 \), so \( \frac{1}{1 - 0.6} \) also gives
                  <strong>2.5</strong>.
                </p>
              </div>
```

*Arithmetic checked: MPW = 0.4; 1 ÷ 0.4 = 2.5; £4bn × 2.5 = £10bn; the saving-only
error gives 10 and £40bn; 1 ÷ (1 − 0.6) = 2.5.*

---

### 3. `2-6-3-the-balance-of-payments.html` — worked example

**Section:** "Current Account Deficits and Surpluses", after the three bullets.

**Why here:** This is the only page in the batch with **no formula and no figure
anywhere**. It lists the four current account components — trade in goods, trade in
services, primary income, secondary income — and then discusses deficits and
surpluses without ever adding the components up, which is precisely the calculation
AQA sets. The figures below also carry the structural point that a goods deficit can
coexist with a services surplus, so quoting the goods figure alone misstates the
position.

```html
              <div class="worked-example">
                <h3>Worked Example: Calculating the Current Account Balance</h3>
                <p>
                  A country records the following flows over one year. Credits
                  are inflows, debits are outflows:
                </p>
                <div class="table-container">
                  <table class="concept-table">
                    <thead>
                      <tr>
                        <th>Component</th>
                        <th>Credits</th>
                        <th>Debits</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>Trade in goods</strong></td>
                        <td>£320bn</td>
                        <td>£410bn</td>
                      </tr>
                      <tr>
                        <td><strong>Trade in services</strong></td>
                        <td>£290bn</td>
                        <td>£210bn</td>
                      </tr>
                      <tr>
                        <td><strong>Primary income</strong></td>
                        <td>£95bn</td>
                        <td>£120bn</td>
                      </tr>
                      <tr>
                        <td><strong>Secondary income</strong></td>
                        <td>£20bn</td>
                        <td>£35bn</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <table class="calculation-table">
                  <tr>
                    <td>Trade in goods</td>
                    <td>320 − 410 = −£90bn</td>
                  </tr>
                  <tr>
                    <td>Trade in services</td>
                    <td>290 − 210 = +£80bn</td>
                  </tr>
                  <tr>
                    <td>Primary income</td>
                    <td>95 − 120 = −£25bn</td>
                  </tr>
                  <tr>
                    <td>Secondary income</td>
                    <td>20 − 35 = −£15bn</td>
                  </tr>
                  <tr>
                    <td><strong>Current account balance</strong></td>
                    <td>−90 + 80 − 25 − 15 = <strong>−£50bn</strong></td>
                  </tr>
                </table>
                <p>
                  The country runs a
                  <strong>current account deficit of £50bn</strong>. Note the
                  <em>surplus</em> on services partly offsetting a much larger
                  deficit on goods: quoting the goods figure alone would
                  overstate the deficit by £40bn.
                </p>
              </div>
```

*Arithmetic checked: −90, +80, −25, −15; sum −£50bn; goods alone (−£90bn) overstates
by £40bn.*

---

## Considered and rejected

| Page | Idea | Why not |
| --- | --- | --- |
| `2-6-2-trade` | Worked example computing opportunity cost ratios for comparative advantage | The page already does exactly this, with Vietnam and Germany output figures and the ratios derived from them. |
| `2-5-1-fiscal-policy` | Exam tip on budget deficit (a flow) vs national debt (a stock) | The page carries separate `key-definition` blocks for budget deficit, fiscal deficit, national debt, cyclical deficit and structural deficit. A tip would restate them. |
| `2-6-3-the-balance-of-payments` | Exam tip on the balance of payments always balancing | Already stated explicitly: "a current account deficit must be financed by a surplus in the capital and financial accounts". |
| `2-6-4-exchange-rate-systems` | Exam tip on depreciation vs devaluation | Already distinguished — revaluation/devaluation under fixed systems, appreciation/depreciation under floating. |
| `2-3-3-inflation-and-deflation` | Exam tip on deflation vs disinflation | Exemplar `2-1-3` already carries exactly this tip. Repeating it on a second page is uniformity, not value. |
| `2-2-2-aggregate-demand-and-aggregate-supply-analysis` | Exam tip on movement along vs shift of AD/AS | The page already separates "Movement Along" from "Shift of" in its own headings. |
| `2-2-4` | A second component, an exam tip on leakages | Folded into the worked example instead, which teaches the same point with figures attached. One component, not two. |
| `2-6-5-economic-growth-and-development` | Worked example calculating HDI | AQA requires interpretation of HDI, not its computation. |

---

## No addition — the remaining 22 pages

| Page | Reason |
| --- | --- |
| `2-1-1-the-objectives-of-government-economic-policy.html` | Objectives overview; qualitative. |
| `2-1-3-uses-of-index-numbers.html` | **Exemplar.** Already 3 worked examples and 2 exam tips. |
| `2-1-4-uses-of-national-income-data.html` | **Exemplar.** Already 3 worked examples and 2 exam tips. |
| `2-2-1-the-circular-flow-of-income.html` | Injections/withdrawals identity already stated; the multiplier arithmetic sits on 2.2.4. |
| `2-2-2-aggregate-demand-and-aggregate-supply-analysis.html` | See "Considered and rejected". |
| `2-2-3-the-determinants-of-aggregate-demand.html` | Determinants are qualitative. **Note:** carries open flag C4, an Edexcel cross-reference. |
| `2-2-5-determinants-of-short-run-aggregate-supply.html` | 2.4 KB, shortest page in the batch. **Note:** carries open flag F1, a caption describing a shift on a movements diagram. |
| `2-2-6-determinants-of-long-run-aggregate-supply.html` | Determinants list; diagram-led. |
| `2-3-1-economic-growth-and-the-economic-cycle.html` | Cycle stages and output gaps already diagram-led. **Note:** carries open flag W1, the stray question mark heading. |
| `2-3-2-employment-and-unemployment.html` | Types of unemployment are definitional; the rate calculation sits on 2.1.2. |
| `2-3-3-inflation-and-deflation.html` | See "Considered and rejected". |
| `2-3-4-possible-conflicts-between-macroeconomic-policy-objectives.html` | Trade-offs are evaluative — and evaluation components are out of scope this pass. |
| `2-4-1-the-structure-of-financial-markets-and-financial-assets.html` | **Exemplar.** Already 1 worked example and 1 exam tip. |
| `2-4-2-commercial-banks-and-investment-banks.html` | Already carries 2 exam tips. |
| `2-4-3-central-banks-and-monetary-policy.html` | Functions and transmission mechanism; qualitative. |
| `2-4-4-the-regulation-of-the-financial-system.html` | Already carries 1 exam tip. |
| `2-5-1-fiscal-policy.html` | See "Considered and rejected". |
| `2-5-2-supply-side-policies.html` | Policy list; qualitative. |
| `2-6-1-globalisation.html` | Qualitative; emphasis improved earlier in this pass. |
| `2-6-2-trade.html` | See "Considered and rejected". |
| `2-6-4-exchange-rate-systems.html` | See "Considered and rejected". |
| `2-6-5-economic-growth-and-development.html` | See "Considered and rejected". |

---

## Flag raised while preparing this batch

**N4 — 32 unescaped `<` characters in note body text, across 20 pages.**

Examples: `\( X < M \)` on `2-2-3` and `2-2-5`, `(PED < 1)` on `1-3-2` and `3-3-1`,
`0 < PES < 1` on `1-3-4`, `\( MC < AVC \)` on `1-4-4` and `3-3-2`.

Every one is `<` followed by a space or a backslash, which the HTML5 parser recovers
as literal text, so **all 32 render correctly in every browser** and MathJax
receives what it expects. It is invalid markup rather than a visible fault. The
earlier audit escaped bare `&` to `&amp;` across 29 files but did not do the same
for `<`.

Escaping them to `&lt;` would be a markup-only change with no rendering difference,
which is within the remit of this pass — but it is not in any approved plan, so it
is logged rather than done. **Say the word and I will fold it into a commit;** it is
about 20 minutes and fully verifiable by the markup-integrity check.

---

## On approval

These 3 components become commit 9, `Add worked examples to AQA macroeconomics
notes`, with every insertion appended to `NEW-CONTENT-LOG.md`.

Running total once applied: **12 components across 11 pages** of the 79 AQA pages.
