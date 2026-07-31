# PLAN — Part B, batch 3: Edexcel Theme 1 (22 pages)

Phase 1B deliverable. **Nothing here has been applied.** Awaiting approval.

**Proposed: 5 components across 4 pages. 18 of 22 pages get nothing.**

| | |
| --- | ---: |
| Worked examples | 4 |
| Exam tips | 1 |
| Pages receiving 2 (the cap) | 1 |
| Pages receiving 1 | 3 |
| Pages receiving 0 | **18** |

Two of the five are **byte-identical reuse** of components already approved and
applied to the AQA twin pages — see below.

---

## The twin-page finding

Two Theme 1 pages are the same page as their AQA counterpart:

| Edexcel | AQA twin | Visible text similarity |
| --- | --- | ---: |
| `1-2-3-price-income-cross-elasticities-of-demand` | `aqa-a2-micro/1-3-2` | **100%** |
| `1-2-5-price-elasticity-of-supply` | `aqa-a2-micro/1-3-4` | **94%** |

`1-2-3` is word-for-word identical to the AQA page that received a PED worked
example and the sign exam tip in batch 1. `1-2-5` differs only in minor wording from
the page that received the PES worked example.

Giving the twins the same components is the consistent call, and it is the same
decision already taken (and applied) for the globalisation emphasis, where
`aqa-a2-macro/2-6-1` and `edexcel-theme-4/4-1-1` now bold the same 35 phrases. A
student who lands on the Edexcel elasticity page should not get a thinner treatment
than one who lands on the AQA one.

**The alternative — giving Edexcel a different worked example on the same topic —
was considered and rejected.** Two different PED examples on two identical pages is
maintenance debt with no pedagogical gain, and it would make the twins diverge for
no reason.

---

## Proposed additions

### 1. `1-2-3-price-income-cross-elasticities-of-demand.html` — worked example + exam tip (2, at cap)

**Section:** "Price Elasticity of Demand (PED)", after the classification table and
before "Key Determinants of PED" — the same position as on the AQA twin.

**Why here:** Identical reasoning to the AQA page. Three elasticity formulas and
three classification tables, and not one value calculated anywhere. Elasticity is
the most heavily examined quantitative skill in Theme 1.

**Markup: byte-identical to the components applied to `aqa-a2-micro/1-3-2`** — the
PED worked example (£3.00 → £3.60 latte, PED = −0.5, revenue £1,500 → £1,620) and
the exam tip on classifying by magnitude rather than sign. Reproduced in full in
`PLAN-enrichment-aqa-micro.md` §1.

---

### 2. `1-2-5-price-elasticity-of-supply.html` — worked example (1)

**Section:** "Interpreting PES Values", after the classification table.

**Why here:** As on the AQA twin, the page gives the PES formula and a
classification table with no figures, while its own spec block requires "the
calculation and interpretation of PES values".

**Markup: byte-identical to the component applied to `aqa-a2-micro/1-3-4`** — the
same 25% price rise giving PES 0.4 in the short run and 2.0 in the long run.
Reproduced in full in `PLAN-enrichment-aqa-micro.md` §2.

---

### 3. `1-2-9-indirect-taxes-subsidies.html` — worked example (1)

**Section:** "Tax Incidence", after the three bullets defining consumer incidence,
producer incidence and government revenue.

**Why here:** The page already gives the three incidence formulas
symbolically — `(P2 − P1) × Q2`, `(P1 − P3) × Q2` and `(P2 − P3) × Q2` — and then
never puts a number through any of them. Tax incidence is one of the most
frequently set calculations in Edexcel Paper 1, and the symbolic form is exactly
where students lose marks: they multiply by `Q1` instead of `Q2`, or forget that the
two incidences must sum to total revenue.

The figures are deliberately chosen so demand is **inelastic** and consumers bear
three quarters of the tax, which sets up the PED section immediately below rather
than duplicating it.

```html
              <div class="worked-example">
                <h3>Worked Example: Calculating Tax Incidence</h3>
                <p>
                  The government places a <strong>specific tax of £2</strong> per
                  unit on a good. The market moves as follows:
                </p>
                <div class="table-container">
                  <table class="concept-table">
                    <thead>
                      <tr>
                        <th></th>
                        <th>Before the tax</th>
                        <th>After the tax</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>Price paid by consumers</strong></td>
                        <td>P1 = £8.00</td>
                        <td>P2 = £9.50</td>
                      </tr>
                      <tr>
                        <td><strong>Price received by producers</strong></td>
                        <td>£8.00</td>
                        <td>P3 = £7.50</td>
                      </tr>
                      <tr>
                        <td><strong>Quantity traded</strong></td>
                        <td>Q1 = 100</td>
                        <td>Q2 = 92</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <table class="calculation-table">
                  <tr>
                    <td>Consumer incidence</td>
                    <td>(£9.50 − £8.00) × 92 = <strong>£138</strong></td>
                  </tr>
                  <tr>
                    <td>Producer incidence</td>
                    <td>(£8.00 − £7.50) × 92 = <strong>£46</strong></td>
                  </tr>
                  <tr>
                    <td><strong>Government revenue</strong></td>
                    <td>(£9.50 − £7.50) × 92 = <strong>£184</strong></td>
                  </tr>
                </table>
                <p>
                  The two incidences add to the government's revenue: £138 + £46
                  = £184. Every area is measured at the
                  <strong>new</strong> quantity Q2, not the old one - using Q1
                  would overstate all three. Consumers here carry
                  <strong>75%</strong> of the tax, which tells you demand is the
                  more <strong>inelastic</strong> side of this market.
                </p>
              </div>
```

*Arithmetic checked: 1.50 × 92 = £138; 0.50 × 92 = £46; 2.00 × 92 = £184;
138 + 46 = 184; 138 ÷ 184 = 75%.*

---

### 4. `1-2-8-producer-consumer-surplus.html` — worked example (1)

**Section:** "Consumer & Producer Surplus at Market Equilibrium", after the bullets
identifying the two areas.

**Why here:** The page defines both surpluses and points at coloured areas on a
diagram, but never states that those areas are triangles or how to measure one. That
leaves the student able to identify surplus but not calculate it, and Edexcel sets
the calculation directly. One worked triangle covers both surpluses and their sum.

```html
              <div class="worked-example">
                <h3>Worked Example: Measuring Consumer and Producer Surplus</h3>
                <p>
                  In a market with straight-line demand and supply curves, the
                  equilibrium price is <strong>£14</strong> and the equilibrium
                  quantity is <strong>50 units</strong>. The demand curve meets
                  the price axis at <strong>£24</strong>, and the supply curve
                  meets it at <strong>£6</strong>.
                </p>
                <p>
                  Each surplus is the area of a triangle, so
                  \( \frac{1}{2} \times \text{base} \times \text{height} \),
                  where the base is the quantity traded:
                </p>
                <table class="calculation-table">
                  <tr>
                    <td>Consumer surplus</td>
                    <td>
                      \( \frac{1}{2} \times 50 \times (24 - 14) \) =
                      <strong>£250</strong>
                    </td>
                  </tr>
                  <tr>
                    <td>Producer surplus</td>
                    <td>
                      \( \frac{1}{2} \times 50 \times (14 - 6) \) =
                      <strong>£200</strong>
                    </td>
                  </tr>
                  <tr>
                    <td><strong>Social surplus</strong></td>
                    <td>£250 + £200 = <strong>£450</strong></td>
                  </tr>
                </table>
                <p>
                  The height of each triangle is the gap between the
                  equilibrium price and where that curve meets the price
                  axis - £10 above for consumers, £8 below for producers. The
                  larger consumer surplus here simply reflects that the demand
                  curve is the steeper of the two.
                </p>
              </div>
```

*Arithmetic checked: ½ × 50 × 10 = £250; ½ × 50 × 8 = £200; total £450.*

---

## Considered and rejected

| Page | Idea | Why not |
| --- | --- | --- |
| `1-3-2-externalities` | Exam tip on MPC/MSC/MPB/MSB and the welfare loss triangle | The page already uses all four abbreviations throughout and refers to welfare loss 14 times. A tip would restate it. |
| `1-2-2-demand` | Exam tip on movement along vs shift | Already covered — the page has a "Movement Along" heading and works through extension and contraction. |
| `1-2-4-supply` | Same idea for supply | Same reason, **and this page carries open flag C1** — its Figure 1 caption still transposes extension and contraction. Adding a component to a page with an unresolved contradiction would compound it. Left alone until C1 is fixed. |
| `1-1-4-production-possibility-frontiers` | Worked example on opportunity cost from a PPF | The figures and captions already walk through the movement; numbers would duplicate the diagram. |
| `1-1-5-specialisation-division-of-labour` | Worked example on productivity gains | The page already carries Adam Smith's figures — 10 workers at 48,000 pins, 4,800 each, against 20 for one unspecialised worker. |
| `1-3-3-public-goods` | Exam tip on non-rivalry vs non-excludability | 1.9 KB page that separates the two cleanly already. |
| `1-4-2-government-failure` | Exam tip on government failure vs market failure | The page defines government failure against market failure in its opening lines. |

---

## No addition — the remaining 18 pages

| Page | Reason |
| --- | --- |
| `1-1-1-economics-as-a-social-science.html` | Models, assumptions and ceteris paribus; nothing to calculate. |
| `1-1-2-positive-normative-statements.html` | 1.9 KB, definitional. |
| `1-1-3-the-economic-problem.html` | Scarcity and opportunity cost; conceptual. |
| `1-1-4-production-possibility-frontiers.html` | See "Considered and rejected". |
| `1-1-5-specialisation-division-of-labour.html` | See "Considered and rejected". |
| `1-1-6-types-of-economies.html` | Free market/command/mixed spectrum; qualitative. |
| `1-2-1-rational-decision-making.html` | 1.9 KB, definitional. |
| `1-2-2-demand.html` | See "Considered and rejected". |
| `1-2-4-supply.html` | See "Considered and rejected". **Open flag C1.** |
| `1-2-6-price-determination.html` | Excess supply/demand adjustment already worked through in prose; one of the best-emphasised pages on the site. |
| `1-2-7-price-mechanism.html` | Rationing, incentive and signalling functions; qualitative. |
| `1-2-10-alternative-views-of-consumer-behaviour.html` | Behavioural biases are definitional; emphasis improved earlier in this pass. |
| `1-3-1-types-of-market-failure.html` | Overview page; each failure type has its own page. |
| `1-3-2-externalities.html` | See "Considered and rejected". |
| `1-3-3-public-goods.html` | See "Considered and rejected". |
| `1-3-4-information-gaps.html` | 1.8 KB, shortest page in the theme. |
| `1-4-1-government-intervention-in-markets.html` | Intervention types are diagram-led; the tax calculation sits on 1.2.9. |
| `1-4-2-government-failure.html` | See "Considered and rejected". |

---

## On approval

These 5 components become commit 10, `Add worked examples and exam tips to Edexcel
Theme 1 notes`, with every insertion appended to `NEW-CONTENT-LOG.md`.

After this batch the running total is **17 components across 15 pages** of the 166.

Three batches remain: Edexcel Themes 2 (24 pages), 3 (20) and 4 (21).
