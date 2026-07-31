# PLAN — Part B, batch 4: Edexcel Theme 2 (24 pages)

Phase 1B deliverable. **Nothing here has been applied.** Awaiting approval.

**Proposed: 5 worked examples across 5 pages. 19 of 24 pages get nothing.**

| | |
| --- | ---: |
| Worked examples | 5 |
| Exam tips | 0 |
| Of which reused verbatim from an AQA page | 3 |
| Of which newly written | 2 |
| Pages receiving 0 | **19** |

---

## The board-asymmetry finding

**All three exemplar pages are AQA** — `2-1-3`, `2-1-4` and `2-4-1`. Edexcel has no
exemplar anywhere on the site. Those three AQA pages carry 7 worked examples between
them, covering index numbers, CPI, the inflation rate, GDP by expenditure, PPP and
bond yields.

The practical effect is that **an AQA student sees several core macro calculations
worked through and an Edexcel student sees none of them**. Theme 2 is where that
bites hardest, because it is the Edexcel macro theme and it covers the same
measurement topics — inflation, unemployment, the balance of payments, national
income — with the formulas stated and never used.

This batch closes that gap. It is larger than batches 2 and 3 for that reason, not
because Theme 2 is thin.

### True twin measurements

Measured with `difflib.SequenceMatcher.ratio()` on visible text. (Batch 3's figures
came from `quick_ratio()`, which is only an upper bound; re-checked, its two twins
are ~100% on true matching too, so that conclusion stands.)

| Edexcel page | Closest AQA page | True similarity |
| --- | --- | ---: |
| `2-6-3-supply-side-policies` | `2-5-2-supply-side-policies` | **100%** |
| `2-4-4-the-multiplier` | `2-2-4-aggregate-demand-and-the-level…` | **99%** |
| `2-3-2-short-run-aggregate-supply` | `2-2-5-determinants-of-short-run…` | **99%** |
| `2-4-1-national-income` | `2-2-1-the-circular-flow-of-income` | **99%** |
| `2-3-3-long-run-aggregate-supply` | `2-2-6-determinants-of-long-run…` | **98%** |
| `2-1-3-employment-unemployment` | `2-3-2-employment-and-unemployment` | **96%** |

Only `2-4-4` has a twin that carries a component, so only it takes a verbatim copy
on twin grounds. The other two reuses below are made on **coverage** grounds — same
calculation, different page — which is the parity that actually matters to a student.

---

## Proposed additions

### 1. `2-1-2-inflation.html` — worked example (1)

**Section:** "Measuring Inflation", after the CPI and inflation-rate formulas.

**Why here:** The page states both formulas and computes neither. AQA students get
this worked three ways on exemplar `2-1-3`; Edexcel students get nothing anywhere on
the site. This is the single widest coverage gap in the batch.

Deliberately **not** a copy of the AQA exemplar's version: that one is built around
weighting and index numbers, whereas this page's formula is the simpler
basket-cost ratio, so the example follows the formula as this page states it.

```html
              <div class="worked-example">
                <h3>Worked Example: From Basket Cost to Inflation Rate</h3>
                <p>
                  The cost of a representative basket of goods is recorded for
                  three years, with <strong>2023 as the base year</strong>:
                </p>
                <div class="table-container">
                  <table class="concept-table">
                    <thead>
                      <tr>
                        <th>Year</th>
                        <th>Cost of basket</th>
                        <th>CPI (2023 = 100)</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>2023 (base)</strong></td>
                        <td>£480.00</td>
                        <td>\( \frac{480}{480} \times 100 = 100 \)</td>
                      </tr>
                      <tr>
                        <td><strong>2024</strong></td>
                        <td>£504.00</td>
                        <td>\( \frac{504}{480} \times 100 = 105 \)</td>
                      </tr>
                      <tr>
                        <td><strong>2025</strong></td>
                        <td>£524.16</td>
                        <td>\( \frac{524.16}{480} \times 100 = 109.2 \)</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <table class="calculation-table">
                  <tr>
                    <td>Inflation in 2024</td>
                    <td>\( \frac{105 - 100}{100} \times 100 = 5\% \)</td>
                  </tr>
                  <tr>
                    <td><strong>Inflation in 2025</strong></td>
                    <td>\( \frac{109.2 - 105}{105} \times 100 = 4\% \)</td>
                  </tr>
                </table>
                <p>
                  The inflation rate <strong>fell</strong> from 5% to 4%, yet the
                  basket still costs <strong>more</strong> in 2025 than in 2024.
                  A falling inflation rate means prices are rising more slowly,
                  not falling. Note too that the 2025 rate is measured against
                  the 2024 index of 105, not against the base year.
                </p>
              </div>
```

*Arithmetic checked: 504 ÷ 480 × 100 = 105; 524.16 ÷ 480 × 100 = 109.2;
(105−100)/100 = 5%; (109.2−105)/105 = 4%.*

---

### 2. `2-1-3-employment-unemployment.html` — worked example (1)

**Section:** "Key Definitions", after the definitions of Unemployed, Labour Force
and Economically Inactive.

**Why here:** The page defines exactly the three groups the calculation needs —
employed, unemployed, economically inactive — and then never uses them arithmetically.
AQA students get this on `2-1-2` (applied in batch 2). Placing it directly beneath
the three definitions makes them do work rather than sit as vocabulary.

**One caveat worth your judgement:** unlike every other component in this pass, this
page does **not** state the rate formulas, so the example introduces them rather than
demonstrating something already present. Edexcel 2.1.3 does require measures of
unemployment, and the page already defines the denominator (Labour Force), so I
think it is justified — but it is a slightly larger addition than the others.

**Markup: byte-identical to the component applied to `aqa-a2-macro/2-1-2`** —
40m working-age population, 26m employed, 2m unemployed, 12m inactive, giving a 7.1%
unemployment rate and 65% employment rate. Reproduced in full in
`PLAN-enrichment-aqa-macro.md` §1.

---

### 3. `2-1-4-balance-of-payments.html` — worked example (1)

**Section:** "The Current Account", after the four components are listed.

**Why here:** Same structure as its AQA counterpart `2-6-3`: the four current
account components are listed and never added up. Summing them is the standard
exam task.

**Markup: byte-identical to the component applied to `aqa-a2-macro/2-6-3`** — goods
−£90bn, services +£80bn, primary income −£25bn, secondary income −£15bn, giving a
current account deficit of £50bn. Reproduced in full in
`PLAN-enrichment-aqa-macro.md` §3.

---

### 4. `2-2-1-aggregate-demand.html` — worked example (1)

**Section:** "The Components of AD and Their Relative Importance", after the four
bullets giving each component's share.

**Why here:** `C + I + G + (X − M)` appears on five Theme 2 pages and is computed on
none. This page is its natural home, because it is the page that already claims
consumption is "around 60% of AD", investment 14% and government spending 25% —
claims a student currently has to take on trust.

The figures are chosen so the resulting shares **corroborate the page's own
percentages** rather than sitting awkwardly beside them.

```html
              <div class="worked-example">
                <h3>Worked Example: Calculating Aggregate Demand</h3>
                <p>
                  An economy records the following expenditure over a year:
                </p>
                <table class="calculation-table">
                  <tr>
                    <td>Consumption (C)</td>
                    <td>£1,200bn</td>
                  </tr>
                  <tr>
                    <td>Investment (I)</td>
                    <td>£280bn</td>
                  </tr>
                  <tr>
                    <td>Government spending (G)</td>
                    <td>£500bn</td>
                  </tr>
                  <tr>
                    <td>Exports (X)</td>
                    <td>£640bn</td>
                  </tr>
                  <tr>
                    <td>Imports (M)</td>
                    <td>£660bn</td>
                  </tr>
                  <tr>
                    <td><strong>Aggregate demand</strong></td>
                    <td>
                      1,200 + 280 + 500 + (640 − 660) =
                      <strong>£1,960bn</strong>
                    </td>
                  </tr>
                </table>
                <p>
                  Net trade is <strong>negative</strong> here, at −£20bn, because
                  imports exceed exports - so it is
                  <strong>subtracted</strong> from the other three components.
                  Consumption alone is about <strong>61%</strong> of AD, which is
                  why a change in consumer confidence or interest rates shifts
                  the AD curve far more than an equivalent percentage change in
                  investment.
                </p>
              </div>
```

*Arithmetic checked: 1,200 + 280 + 500 = 1,980; less 20 = £1,960bn. Shares: C 61%,
I 14%, G 26%, net trade −1% — matching the page's stated "around 60%", "around 14%",
"around 25%" and "roughly 1% or less".*

---

### 5. `2-4-4-the-multiplier.html` — worked example (1)

**Section:** "Calculating the Multiplier", after the existing formulas.

**Why here:** A **99% true twin** of `aqa-a2-macro/2-2-4`, which received this
component in batch 2. Same three formulas, same single-leakage illustration, same
absent multi-leakage case.

**Markup: byte-identical to the component applied to `aqa-a2-macro/2-2-4`** — MPS
0.1, MPT 0.25, MPM 0.05, giving a multiplier of 2.5 and a £10bn effect from a £4bn
injection. Reproduced in full in `PLAN-enrichment-aqa-macro.md` §2.

---

## Considered and rejected

| Page | Idea | Why not |
| --- | --- | --- |
| `2-6-3-supply-side-policies` | Anything | 100% twin of `aqa-a2-macro/2-5-2`, which got nothing. Qualitative policy list on both boards. |
| `2-3-2` / `2-3-3` aggregate supply | Exam tip on SRAS vs LRAS shifts | 99% and 98% twins of AQA pages that got nothing; both are diagram-led and already separate the two. **`2-3-2` also carries open flag F1** — a caption describing a shift on a movements diagram. |
| `2-4-1-national-income` | Worked example on the circular flow identity | Despite its name this is the circular flow page, and `J = W` is an identity rather than a calculation. The expenditure calculation goes on `2-2-1` where the components are actually listed. |
| `2-4-2-injections-withdrawals` | Worked example on equilibrium national income | Overlaps `2-4-4`'s multiplier example; two near-identical leakage calculations in one theme is repetition. |
| `2-5-2-output-gaps` | Worked example calculating an output gap | The gap is read off a diagram as the distance between actual and potential output; a number adds nothing the figure does not show. |
| `2-6-2-demand-side-policies` | Exam tip on monetary vs fiscal policy | 12.2 KB, the longest page in the theme, and it already separates the two throughout. |
| `2-2-2-consumption` | Worked example on the MPC | The page already works one: "an extra £100 of disposable income and spends £80 of it, the MPC is 0.8". |

---

## No addition — the remaining 19 pages

| Page | Reason |
| --- | --- |
| `2-1-1-economic-growth.html` | Growth definitions and measurement; the index-number work sits on 2.1.2. |
| `2-2-2-consumption.html` | See "Considered and rejected". Emphasis improved earlier in this pass. |
| `2-2-3-investment.html` | Determinants of investment; qualitative. |
| `2-2-4-government-expenditure.html` | Qualitative; the AD calculation sits on 2.2.1. |
| `2-2-5-net-trade.html` | Determinants of net trade; the balance calculation sits on 2.1.4. Emphasis improved earlier. |
| `2-3-1-aggregate-supply.html` | Overview; SRAS and LRAS have their own pages. |
| `2-3-2-short-run-aggregate-supply.html` | See "Considered and rejected". **Open flag F1.** |
| `2-3-3-long-run-aggregate-supply.html` | See "Considered and rejected". |
| `2-4-1-national-income.html` | See "Considered and rejected". |
| `2-4-2-injections-withdrawals.html` | See "Considered and rejected". |
| `2-4-3-equilibrium-levels-of-real-national-output.html` | Equilibrium is diagram-led; the multiplier arithmetic sits on 2.4.4. |
| `2-5-1-causes-of-growth.html` | Causes list; qualitative. |
| `2-5-2-output-gaps.html` | See "Considered and rejected". |
| `2-5-3-trade-cycle.html` | Cycle stages; diagram-led. |
| `2-5-4-the-impact-of-economic-growth.html` | Costs and benefits; evaluative, and evaluation components are out of scope. |
| `2-6-1-possible-macroeconomic-objectives.html` | Objectives list; qualitative. |
| `2-6-2-demand-side-policies.html` | See "Considered and rejected". |
| `2-6-3-supply-side-policies.html` | See "Considered and rejected". |
| `2-6-4-conflicts-between-objectives-and-policies.html` | Trade-offs are evaluative; out of scope. |

---

## A note on duplication

Three of these five are the same block of markup as an AQA page. That is deliberate
and consistent with batch 3, but it is worth stating the trade-off plainly: it means
six pages on the site will carry a block of text that also appears elsewhere.

I think that is right here — the two boards already carry near-identical prose
throughout by design, the alternative is writing a second version of the same
calculation purely to look different, and a student should not get a thinner page
because of which board they study. **Say if you would rather each board had its own
distinct examples** and I will draft alternatives for the three.

---

## On approval

These 5 components become commit 11, `Add worked examples to Edexcel Theme 2 notes`,
with every insertion appended to `NEW-CONTENT-LOG.md`.

After this batch the running total is **22 components across 20 pages** of the 166.
Two batches remain: Themes 3 (20 pages) and 4 (21).
