# PLAN — Part B, batch 1: AQA Microeconomics (54 pages)

Phase 1B deliverable. **Nothing here has been applied.** Awaiting approval.

**Proposed: 8 components across 7 pages. 47 of 54 pages get nothing.**

| | |
| --- | ---: |
| Worked examples | 5 |
| Exam tips | 3 |
| Pages receiving 2 (the cap) | 1 |
| Pages receiving 1 | 6 |
| Pages receiving 0 | **47** |

---

## Why this set, and why it is small

These 54 pages currently contain **zero** worked examples and **zero** exam tips —
the largest gap on the site. But the gap that actually matters is narrower than it
first looks.

Scanning all 54 for concrete figures found almost none: formulas are **stated but
never demonstrated**. `PED = %ΔQd / %ΔP`, `TC = TFC + TVC`, `MRP = MPP × MR` and the
concentration ratio all appear as notation, with no page showing what to do with
them. That is precisely the gap the three exemplar pages fill — every worked example
on 2.1.3, 2.1.4 and 2.4.1 takes a stated formula and puts numbers through it.

So the five worked examples below all meet the same test: **an examinable
calculation that the page defines but never performs.** Nothing is proposed for
pages that are qualitative by nature, or where the page already works the reasoning
through.

The three exam tips each correct a specific confusion the page does **not** already
address. Several tempting candidates were dropped for exactly that reason — see
"Considered and rejected".

---

## Proposed additions

### 1. `1-3-2-price-income-and-cross-elasticities-of-demand.html` — worked example + exam tip (2, at cap)

**Section:** "Price Elasticity of Demand (PED)", immediately after the
classification table and before "Key Determinants of PED".

**Why here:** The page gives the PED formula and a five-row classification table but
never calculates a single value. Elasticity calculation is the most frequently
examined quantitative skill in AQA micro, and the two errors students make —
computing the percentage change off the wrong base, and mishandling the negative
sign — are both invisible without a worked figure. Placing it after the
classification table means the student can immediately read the answer against the
categories directly above.

The example also lands the revenue point the page makes three sections later
(raise price when demand is inelastic) with actual numbers.

```html
              <div class="worked-example">
                <h3>Worked Example: Calculating PED</h3>
                <p>
                  A coffee shop raises the price of a latte from
                  <strong>£3.00</strong> to <strong>£3.60</strong>. Weekly sales
                  fall from <strong>500</strong> cups to
                  <strong>450</strong> cups. Each percentage change is measured
                  against the original value:
                </p>
                <table class="calculation-table">
                  <tr>
                    <td>% change in quantity demanded</td>
                    <td>\( \frac{450 - 500}{500} \times 100 = -10\% \)</td>
                  </tr>
                  <tr>
                    <td>% change in price</td>
                    <td>\( \frac{3.60 - 3.00}{3.00} \times 100 = +20\% \)</td>
                  </tr>
                  <tr>
                    <td><strong>PED</strong></td>
                    <td>\( \frac{-10}{+20} = -0.5 \)</td>
                  </tr>
                </table>
                <p>
                  A magnitude of <strong>0.5</strong> lies between 0 and 1, so
                  demand is <strong>relatively inelastic</strong>. Quantity fell
                  by proportionally less than price rose, so total revenue
                  <strong>rises</strong>, from £1,500 to £1,620.
                </p>
              </div>
```

**Then, directly beneath it:**

```html
              <div class="exam-tip">
                <p>
                  <strong>Drop the minus sign before you classify.</strong> Price
                  and quantity demanded move in opposite directions, so PED is
                  <em>always</em> negative for a normal demand curve. Show the
                  sign in the calculation, but classify on the
                  <strong>magnitude</strong>: −0.5 is inelastic and −3 is
                  elastic. The mistake to avoid is arguing that −3 is "smaller"
                  than −0.5 and therefore more inelastic.
                </p>
              </div>
```

---

### 2. `1-4-4-costs-of-production.html` — worked example (1)

**Section:** end of "Key Definitions", before "Short-Run Cost Curves and Diminishing
Returns".

**Why here:** Seven cost concepts are defined in notation on one screen — TFC, TVC,
TC, AC, AFC, AVC, MC — and none is ever given a number. A single schedule makes all
of them concrete at once and sets up the U-shape explanation in the very next
section, where the page asserts that MC cuts AC at its minimum without showing it.

```html
              <div class="worked-example">
                <h3>Worked Example: Building a Cost Schedule</h3>
                <p>
                  A bakery has <strong>fixed costs of £100 a day</strong> for
                  rent and insurance. Its variable costs rise with output:
                </p>
                <div class="table-container">
                  <table class="concept-table">
                    <thead>
                      <tr>
                        <th>Output</th>
                        <th>TFC</th>
                        <th>TVC</th>
                        <th>TC</th>
                        <th>AC</th>
                        <th>MC</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>10</strong></td>
                        <td>£100</td>
                        <td>£60</td>
                        <td>£160</td>
                        <td>£16.00</td>
                        <td>—</td>
                      </tr>
                      <tr>
                        <td><strong>20</strong></td>
                        <td>£100</td>
                        <td>£100</td>
                        <td>£200</td>
                        <td>£10.00</td>
                        <td>£4.00</td>
                      </tr>
                      <tr>
                        <td><strong>30</strong></td>
                        <td>£100</td>
                        <td>£160</td>
                        <td>£260</td>
                        <td>£8.67</td>
                        <td>£6.00</td>
                      </tr>
                      <tr>
                        <td><strong>40</strong></td>
                        <td>£100</td>
                        <td>£260</td>
                        <td>£360</td>
                        <td>£9.00</td>
                        <td>£10.00</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p>
                  TC is TFC plus TVC, AC is TC divided by output, and MC is the
                  change in TC divided by the change in output - so between 30
                  and 40 units MC is \( \frac{360 - 260}{40 - 30} = £10 \).
                  Notice that AC bottoms out at <strong>£8.67</strong> and then
                  rises: AC turns upward exactly where
                  <strong>MC rises above it</strong>.
                </p>
              </div>
```

*Arithmetic checked: AC = 16.00, 10.00, 8.67, 9.00; MC = 4, 6, 10. MC (£6) is below
AC (£8.67) at Q=30 and above it (£10 vs £9.00) at Q=40, so MC cuts AC between the
two — consistent with the claim the next section makes.*

---

### 3. `1-4-6-marginal-average-and-total-revenue.html` — worked example (1)

**Section:** "Revenue in Imperfect Competition", after the final paragraph.

**Why here:** The page makes two claims a student cannot verify from the text — that
MR lies below AR, and that TR is maximised where MR = 0. Both become obvious in four
rows of figures. It also fixes the most common revenue error: not seeing that a
price maker must cut the price on *every* unit, not just the extra one, which is
*why* MR falls faster than AR.

```html
              <div class="worked-example">
                <h3>Worked Example: Total, Average and Marginal Revenue</h3>
                <p>
                  A firm with market power must lower its price to sell more.
                  This schedule is read off its demand curve:
                </p>
                <div class="table-container">
                  <table class="concept-table">
                    <thead>
                      <tr>
                        <th>Price (AR)</th>
                        <th>Quantity</th>
                        <th>TR = P × Q</th>
                        <th>MR</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>£10</strong></td>
                        <td>1</td>
                        <td>£10</td>
                        <td>—</td>
                      </tr>
                      <tr>
                        <td><strong>£8</strong></td>
                        <td>2</td>
                        <td>£16</td>
                        <td>£6</td>
                      </tr>
                      <tr>
                        <td><strong>£6</strong></td>
                        <td>3</td>
                        <td>£18</td>
                        <td>£2</td>
                      </tr>
                      <tr>
                        <td><strong>£4</strong></td>
                        <td>4</td>
                        <td>£16</td>
                        <td>−£2</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p>
                  Price and AR are the same figure in every row. MR falls twice
                  as fast and stays <strong>below AR</strong>, because to sell
                  one more unit the firm must cut the price on
                  <strong>every</strong> unit, not just the last one. Total
                  revenue peaks at <strong>£18</strong>, at the output where MR
                  turns from positive to negative.
                </p>
              </div>
```

*Arithmetic checked: TR = 10, 16, 18, 16; MR = 6, 2, −2. TR peaks at Q = 3 where MR
crosses zero, matching the page's existing claim.*

---

### 4. `1-5-5-oligopoly.html` — worked example (1)

**Section:** "Concentration Ratios", after the formula.

**Why here:** This page's own `spec-alert` states that students must be able to
**"calculate and interpret concentration ratios"** — it is the one explicitly
examinable calculation on the page, and the formula is given with no figures. The
existing illustrative sentence is also internally inconsistent (see the flag below),
so a correct worked figure is worth more here than anywhere else in the batch.

```html
              <div class="worked-example">
                <h3>Worked Example: Calculating a Concentration Ratio</h3>
                <p>Six firms supply a market. Their annual sales are:</p>
                <div class="table-container">
                  <table class="concept-table">
                    <thead>
                      <tr>
                        <th>Firm</th>
                        <th>Annual Sales</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>A</strong></td>
                        <td>£240m</td>
                      </tr>
                      <tr>
                        <td><strong>B</strong></td>
                        <td>£180m</td>
                      </tr>
                      <tr>
                        <td><strong>C</strong></td>
                        <td>£120m</td>
                      </tr>
                      <tr>
                        <td><strong>D</strong></td>
                        <td>£40m</td>
                      </tr>
                      <tr>
                        <td><strong>E</strong></td>
                        <td>£15m</td>
                      </tr>
                      <tr>
                        <td><strong>F</strong></td>
                        <td>£5m</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <table class="calculation-table">
                  <tr>
                    <td>Sales of the largest three firms</td>
                    <td>£240m + £180m + £120m = £540m</td>
                  </tr>
                  <tr>
                    <td>Total market sales</td>
                    <td>£600m</td>
                  </tr>
                  <tr>
                    <td><strong>3-firm concentration ratio</strong></td>
                    <td>\( \frac{540}{600} \times 100 = 90\% \)</td>
                  </tr>
                </table>
                <p>
                  The three largest firms supply <strong>90%</strong> of the
                  market between them, leaving 10% for the other three. A ratio
                  this high marks a <strong>highly concentrated</strong> market
                  in which the leading firms are strongly interdependent.
                </p>
              </div>
```

*Arithmetic checked: 240 + 180 + 120 = 540; total = 600; 540 ÷ 600 × 100 = 90%.*

---

### 5. `1-6-1-the-demand-for-labour-marginal-productivity-theory.html` — worked example (1)

**Section:** "The Marginal Revenue Product Theory", after the paragraph explaining
that the MRP curve is the demand curve for labour.

**Why here:** The page states `MRP = MPP × MR` and asserts that the curve slopes
downward "because of the law of diminishing returns" — a causal claim the student
has to take on trust. A four-row schedule shows MPP turning down and drags MRP with
it, and then answers the question the theory exists to answer: how many workers does
the firm actually hire at a given wage?

```html
              <div class="worked-example">
                <h3>Worked Example: Calculating Marginal Revenue Product</h3>
                <p>
                  A firm sells its output at a constant
                  <strong>£5 per unit</strong>, so MR is £5. Adding workers
                  changes total output as follows:
                </p>
                <div class="table-container">
                  <table class="concept-table">
                    <thead>
                      <tr>
                        <th>Workers</th>
                        <th>Total Output</th>
                        <th>MPP</th>
                        <th>MRP = MPP × MR</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>1</strong></td>
                        <td>20</td>
                        <td>20</td>
                        <td>£100</td>
                      </tr>
                      <tr>
                        <td><strong>2</strong></td>
                        <td>46</td>
                        <td>26</td>
                        <td>£130</td>
                      </tr>
                      <tr>
                        <td><strong>3</strong></td>
                        <td>66</td>
                        <td>20</td>
                        <td>£100</td>
                      </tr>
                      <tr>
                        <td><strong>4</strong></td>
                        <td>78</td>
                        <td>12</td>
                        <td>£60</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p>
                  MPP rises to the second worker and falls after it - this is
                  the <strong>law of diminishing returns</strong> setting in, and
                  it is what makes the MRP curve slope downward. A firm hires an
                  extra worker only while MRP is at least the wage, so at a wage
                  of <strong>£80</strong> it employs
                  <strong>three</strong> workers: the fourth would add £60 of
                  revenue but £80 of cost.
                </p>
              </div>
```

*Arithmetic checked: MPP = 20, 26, 20, 12; MRP at MR = £5 gives 100, 130, 100, 60.
At a wage of £80 the third worker clears the bar (£100) and the fourth does not (£60).*

---

### 6. `1-4-5-economies-and-diseconomies-of-scale.html` — exam tip (1)

**Section:** "Diseconomies of Scale", after the diseconomies table.

**Why here:** This is the single most common confusion in AQA micro cost theory, and
this page does not address it — it mentions "long run" twice and never mentions
diminishing returns at all, while `1.4.3` and `1.4.4` cover diminishing returns
without ever contrasting the two. Neither page tells the student how to spot which
one a question is about.

```html
              <div class="exam-tip">
                <p>
                  <strong>Diseconomies of scale are not diminishing returns.</strong>
                  Diminishing returns are a <em>short-run</em> effect, caused by
                  adding a variable factor to a <strong>fixed</strong> one, and
                  they push <strong>marginal cost</strong> up. Diseconomies of
                  scale are a <em>long-run</em> effect, occurring once
                  <strong>all</strong> factors have been increased, and they push
                  <strong>long-run average cost</strong> up. If a question
                  describes a firm building a bigger plant or expanding its
                  scale, it is testing diseconomies.
                </p>
              </div>
```

---

### 7. `1-4-7-profit.html` — exam tip (1)

**Section:** "Key Definitions", after the definition of loss.

**Why here:** The page defines normal profit as `TR = TC` and calls it the
break-even point, but never says the thing students get wrong: that normal profit is
already inside the cost curves, so a firm earning it sits at AR = AC on a diagram.
Without that, "break-even" reads as "no profit at all", and students then cannot
identify supernormal profit as the area above AC on the diagrams two sections later.

```html
              <div class="exam-tip">
                <p>
                  <strong>Normal profit is a cost, not a bonus.</strong> It is
                  the opportunity cost of the entrepreneur staying in this
                  industry, so it is already counted inside the firm's costs. On
                  a diagram that means a firm making normal profit sits where
                  <strong>AR = AC</strong>, and only the area
                  <em>above</em> AC is supernormal profit. Such a firm is
                  breaking even in economic terms even though its accounts would
                  show a positive figure.
                </p>
              </div>
```

---

## Considered and rejected

Each of these was a plausible candidate, checked against the page, and dropped.

| Page | Idea | Why not |
| --- | --- | --- |
| `1-5-3-perfect-competition` | Exam tip on short-run supernormal profit competing away to normal profit in the long run | The page already states this explicitly under "Long-Run Equilibrium". A tip would restate theory. |
| `1-3-4-price-elasticity-of-supply` | Worked example calculating PES | Mechanically identical to the PED example in item 1. Adding it would be coverage for its own sake, and the elasticity method only needs demonstrating once. |
| `1-1-5-production-possibility-diagrams` | Worked example calculating opportunity cost from a PPF | The page's figures and captions already walk through the C→D movement. Numbers would duplicate the diagram. |
| `1-4-3-law-of-diminishing-returns` | Worked example on marginal/average/total returns | Overlaps the cost schedule in item 2 and the MRP schedule in item 5; three near-identical marginal tables across one theme is repetition. The distinction that *is* missing is covered by the tip in item 6. |
| `1-7-1-distribution-of-income-and-wealth` | Worked example calculating a Gini coefficient | Gini is not calculable at A-Level from the Lorenz curve without integration; the specification asks for interpretation only. |
| `1-5-10-market-structure-efficiency` | Exam tip on allocative (P=MC) vs productive (min AC) efficiency | The page's own tables already separate the two conditions cleanly. |
| `1-8-4-externalities` | Exam tip on which curve shifts and where the welfare loss triangle sits | Real confusion, but the page is 25.7 KB with four diagrams already walking it through — the longest page in the batch. Adding to it works against concision. |

---

## No addition — the remaining 47 pages

| Page | Reason |
| --- | --- |
| `1-1-1-economic-methodology.html` | Qualitative: positive/normative and the scientific method. Nothing to calculate. |
| `1-1-2-the-nature-and-purpose-of-economic-activity.html` | Short definitional page. |
| `1-1-3-economic-resources.html` | Factors of production; definitional. |
| `1-1-4-scarcity-choice-and-the-allocation-of-resources.html` | Conceptual; opportunity cost handled on 1.1.5. |
| `1-1-5-production-possibility-diagrams.html` | See "Considered and rejected". |
| `1-2-1-consumer-behaviour.html` | Utility theory, already diagram-led. |
| `1-2-2-imperfect-information.html` | Short qualitative page. |
| `1-2-3-aspects-of-behavioural-economic-theory.html` | Biases are definitional; no calculation and no single dominant confusion. |
| `1-2-4-behavioural-economics-and-economic-policy.html` | Short policy page (nudges, choice architecture). |
| `1-3-1-the-determinants-of-the-demand-for-goods-and-services.html` | Movement vs shift is already covered by the figures and captions. |
| `1-3-3-the-determinants-of-the-supply-of-goods-and-services.html` | Mirrors 1.3.1. **Note:** carries open flag C1, an inverted caption — content fix for the author, not enrichment. |
| `1-3-4-price-elasticity-of-supply.html` | See "Considered and rejected". |
| `1-3-5-the-determination-of-equilibrium-market-prices.html` | Already one of the best-emphasised pages; excess/shortage adjustment is fully worked in prose. |
| `1-3-6-the-interrelationship-between-markets.html` | Table plus four diagram analyses already cover every relationship. |
| `1-4-1-production-and-productivity.html` | 1.1 KB; the labour-productivity formula is self-evident. |
| `1-4-2-specialisation-division-of-labour-and-exchange.html` | Qualitative. |
| `1-4-3-the-law-of-diminishing-returns-and-returns-to-scale.html` | See "Considered and rejected". |
| `1-4-8-technological-change.html` | Short qualitative page. |
| `1-5-1-market-structures.html` | Overview page; the individual structures have their own pages. |
| `1-5-2-the-objectives-of-firms.html` | Objectives are diagram-led (profit max, sales max, revenue max) and already labelled. |
| `1-5-4-monopolistic-competition.html` | Short-run/long-run adjustment already worked through, as on 1.5.3. |
| `1-5-6-monopoly-and-monopoly-power.html` | Diagram-led. **Note:** carries open flag C4, an Edexcel cross-reference. |
| `1-5-7-price-discrimination.html` | Three degrees are definitional; the diagram covers third-degree. |
| `1-5-8-the-dynamics-of-competition-and-competitive-market-processes.html` | **Has a truncated sentence (flag N2) — needs an author fix before anything is added.** |
| `1-5-9-contestable-and-non-contestable-markets.html` | Hit-and-run entry and sunk costs are qualitative. |
| `1-5-10-market-structure-efficiency-resource-allocation.html` | See "Considered and rejected". |
| `1-5-11-consumer-and-producer-surplus.html` | Seven diagrams already; surplus is read off them, not computed. |
| `1-6-2-influence-upon-the-supply-of-labour-to-different-markets.html` | Qualitative determinants list. |
| `1-6-3-wage-determination-perfectly-competitive-labour-markets.html` | Diagram-led; MRP calculation sits on 1.6.1. |
| `1-6-4-wage-determination-imperfectly-competitive-labour-markets.html` | Monopsony diagram already walked through in prose. |
| `1-6-5-the-influence-of-trade-unions-in-determining-wages-and-levels-of-employment.html` | Diagram-led. |
| `1-6-6-the-national-minimum-wage.html` | Short; NMW effects are read off the diagram. |
| `1-6-7-discrimination-in-the-labour-market.html` | Qualitative. |
| `1-7-1-the-distribution-of-income-and-wealth.html` | See "Considered and rejected". |
| `1-7-2-the-problem-of-poverty.html` | Absolute vs relative poverty is definitional. |
| `1-7-3-government-policies-poverty-income-distribution.html` | Policy list, already fully emphasised. |
| `1-8-1-how-markets-and-prices-allocate-resources.html` | Price mechanism functions; qualitative. |
| `1-8-2-the-meaning-of-market-failure.html` | Definitional overview. |
| `1-8-3-public-goods-private-goods-and-quasi-public-goods.html` | Non-rivalry/non-excludability are definitional and the page separates them clearly. |
| `1-8-4-positive-and-negative-externalities-in-consumption-and-production.html` | See "Considered and rejected". |
| `1-8-5-merit-and-demerit-goods.html` | Follows directly from 1.8.4; adding here would duplicate. |
| `1-8-6-market-imperfections.html` | Information gaps, already covered on 1.2.2. |
| `1-8-7-competition-policy.html` | Policy costs and benefits already tabulated in depth. |
| `1-8-8-public-ownership-privatisation-regulation-and-deregulation-of-markets.html` | Argument tables already cover both sides. |
| `1-8-9-government-intervention-in-markets.html` | Intervention types are diagram-led. |
| `1-8-10-government-failure.html` | Short qualitative page. |

---

## Flag raised while preparing this batch

**N3 — `1-5-5-oligopoly.html`, "Concentration Ratios":**

> "For example, a **3-firm concentration ratio of 80%** means that the top
> **five** firms account for 80% of total market sales."

Three in the first half of the sentence, five in the second. One of the two numbers
is wrong. **Not fixed** — logged in `REVIEW-NOTES.md` for the author. The proposed
worked example sits directly below this sentence and uses a correct 3-firm
calculation, so the inconsistency would be more visible once added, not less. Worth
fixing before or alongside.

---

## On approval

These 8 components become commit 8, `Add worked examples and exam tips to AQA
notes`, applied by spec section with a diff summary after each, and every insertion
logged to `NEW-CONTENT-LOG.md` with file, line and component type.
