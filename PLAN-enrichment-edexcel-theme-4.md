# PLAN — Part B, batch 6: Edexcel Theme 4 (21 pages)

Phase 1B deliverable — the last batch. **Nothing here has been applied.**

**Proposed: 3 worked examples across 3 pages. 18 of 21 pages get nothing.**

| | |
| --- | ---: |
| Worked examples | 3 |
| Exam tips | 0 |
| Of which reused verbatim from AQA | 1 |
| Of which newly written | 2 |
| Pages receiving 0 | **18** |

---

## Why Theme 4 yields less than Theme 3

Theme 3 was almost entirely reuse because it mirrors AQA micro 1.4–1.6. Theme 4 is
the opposite: it is largely **Edexcel-only content** with no AQA counterpart —
development economics, poverty and inequality, trading blocs, public finance. Only
one page is a true twin of an AQA page that carries a component.

It is also the theme where the notes already do the arithmetic. Two of my strongest
expected candidates turned out to be worked through already:

- **`4-1-2-specialisation-trade`** computes the opportunity cost of a computer chip
  in T-shirts for both Germany and Vietnam, from stated output figures.
- **`4-5-3-public-sector-finances`** carries the budget identity and separate
  definitions of deficit and debt, as its AQA counterpart does.

What remains is three calculations that are stated and never performed.

### Twin measurement (true `ratio()`)

| Edexcel page | Closest AQA page | Similarity | AQA has |
| --- | --- | ---: | --- |
| `4-1-1-globalisation` | `2-6-1-globalisation` | 100% | nothing |
| `4-1-7-balance-of-payments` | `2-6-3-the-balance-of-payments` | **96%** | current account WE |
| `4-2-2-inequality` | `1-7-1-the-distribution-of-income-and-wealth` | 87% | nothing |
| `4-1-8-exchange-rates` | `2-6-4-exchange-rate-systems` | 82% | nothing |

---

## Proposed additions

### 1. `4-1-4-terms-of-trade.html` — worked example (1)

**Section:** "Definition and Calculation", after the formula.

**Why here:** The page gives the terms of trade formula and then explains a rise and
a fall entirely in words. It is a standard Edexcel Paper 3 calculation, it has **no
AQA counterpart anywhere on the site** — AQA has no terms of trade page — and the
index arithmetic is exactly where students slip, because they compare the two
indices directly instead of taking the ratio.

Two years are shown so both a deterioration and an improvement appear, matching the
page's own two-directional explanation.

```html
              <div class="worked-example">
                <h3>Worked Example: Calculating the Terms of Trade</h3>
                <p>
                  A country's average export and import prices are recorded as
                  index numbers, with <strong>Year 1 as the base year</strong>:
                </p>
                <div class="table-container">
                  <table class="concept-table">
                    <thead>
                      <tr>
                        <th>Year</th>
                        <th>Export price index</th>
                        <th>Import price index</th>
                        <th>Terms of trade</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>Year 1 (base)</strong></td>
                        <td>100</td>
                        <td>100</td>
                        <td>\( \frac{100}{100} \times 100 = 100 \)</td>
                      </tr>
                      <tr>
                        <td><strong>Year 2</strong></td>
                        <td>106</td>
                        <td>112</td>
                        <td>\( \frac{106}{112} \times 100 = 94.6 \)</td>
                      </tr>
                      <tr>
                        <td><strong>Year 3</strong></td>
                        <td>115</td>
                        <td>110</td>
                        <td>\( \frac{115}{110} \times 100 = 104.5 \)</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p>
                  In Year 2 the index falls to <strong>94.6</strong>: import
                  prices rose faster than export prices, so each unit of exports
                  buys fewer imports. In Year 3 it rises to
                  <strong>104.5</strong>. Note that export prices rose in
                  <em>both</em> years - what moves the terms of trade is the
                  <strong>ratio</strong> of the two indices, not the direction of
                  either one on its own.
                </p>
              </div>
```

*Arithmetic checked: 106 ÷ 112 × 100 = 94.64 → 94.6; 115 ÷ 110 × 100 = 104.55 → 104.5.*

---

### 2. `4-1-7-balance-of-payments.html` — worked example (1)

**Section:** "The Current Account", after the components are listed.

**Why here:** A **96% true twin** of `aqa-a2-macro/2-6-3`, which received this
component in batch 2, and the same twin was already given it on
`edexcel-theme-2/2-1-4` in batch 4. Same four components listed, same absence of any
sum.

**Markup: byte-identical to the component on `aqa-a2-macro/2-6-3`** — goods −£90bn,
services +£80bn, primary income −£25bn, secondary income −£15bn, current account
−£50bn. Reproduced in full in `PLAN-enrichment-aqa-macro.md` §3.

> **Worth flagging:** this would be the **third** page carrying this block, after
> `aqa-a2-macro/2-6-3` and `edexcel-theme-2/2-1-4`. Edexcel covers the balance of
> payments twice, in Themes 2 and 4. You approved duplication in batch 4, but three
> copies is further than that went — **say if you would rather this page got a
> distinct example**, or nothing at all, and I will adjust.

---

### 3. `4-1-9-international-competitiveness.html` — worked example (1)

**Section:** "Definition and Measures", after the unit labour costs formula.

**Why here:** The page states the ULC formula, then says competitiveness "is
relative, so it depends on how one country performs compared with its rivals" —
without ever putting two countries side by side. A one-country ULC figure means
nothing on its own, which is the whole point the page is making and the thing the
figures below demonstrate.

```html
              <div class="worked-example">
                <h3>Worked Example: Comparing Unit Labour Costs</h3>
                <p>
                  Two countries produce the same good. Unit labour cost is total
                  labour cost divided by total output:
                </p>
                <div class="table-container">
                  <table class="concept-table">
                    <thead>
                      <tr>
                        <th>Country</th>
                        <th>Total labour costs</th>
                        <th>Total output</th>
                        <th>Unit labour cost</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>Country A</strong></td>
                        <td>£4.8m</td>
                        <td>600 units</td>
                        <td>\( \frac{4{,}800{,}000}{600} = £8{,}000 \)</td>
                      </tr>
                      <tr>
                        <td><strong>Country B</strong></td>
                        <td>£7.0m</td>
                        <td>1,000 units</td>
                        <td>\( \frac{7{,}000{,}000}{1{,}000} = £7{,}000 \)</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p>
                  Country B spends <strong>more</strong> on labour in total, yet
                  its unit labour cost is <strong>lower</strong>, because its
                  output is higher still. On this measure B is the more
                  cost-competitive of the two: A's unit labour costs are
                  <strong>14% higher</strong>. A total wage bill on its own says
                  nothing about competitiveness - only cost <em>per unit</em>
                  does.
                </p>
              </div>
```

*Arithmetic checked: 4,800,000 ÷ 600 = £8,000; 7,000,000 ÷ 1,000 = £7,000;
8,000 ÷ 7,000 = 1.143, so 14% higher.*

---

## Considered and rejected

| Page | Idea | Why not |
| --- | --- | --- |
| `4-1-2-specialisation-trade` | Worked example calculating opportunity cost | Already done on the page: Germany gives up 10 T-shirts per computer chip, Vietnam 15, derived from stated output figures. |
| `4-5-3-public-sector-finances` | Exam tip on deficit (a flow) vs debt (a stock) | The page carries the budget identity and separate definitions, as its AQA counterpart does. |
| `4-2-2-inequality` | Worked example calculating a Gini coefficient | Same reason as the AQA twin `1-7-1`: Gini is not calculable from a Lorenz curve at A-Level without integration, and the specification asks for interpretation. |
| `4-1-8-exchange-rates` | Worked example converting currencies | 82% twin of `2-6-4`, which received nothing. The page's quantitative content is the Marshall-Lerner condition, which is a threshold to interpret rather than a calculation to perform. |
| `4-1-1-globalisation` | Anything | 100% twin of `2-6-1`, which received nothing. Qualitative; emphasis improved earlier in this pass. |
| `4-5-2-taxation` | Worked example on average vs marginal tax rates | The page covers tax types and impacts, not rate arithmetic — there is no stated formula to demonstrate. |
| `4-3-1-measures-of-development` | Worked example calculating HDI | As on AQA `2-6-5`: the specification requires interpretation of HDI, not its computation. |

---

## No addition — the remaining 18 pages

| Page | Reason |
| --- | --- |
| `4-1-1-globalisation.html` | See "Considered and rejected". |
| `4-1-2-specialisation-trade.html` | See "Considered and rejected". |
| `4-1-3-pattern-of-trade.html` | Factors changing trade patterns; qualitative. |
| `4-1-5-trading-blocs-and-the-world-trade-organisation.html` | Types of bloc and WTO role; qualitative. |
| `4-1-6-restrictions-on-free-trade.html` | Protectionist instruments; diagram-led. |
| `4-1-8-exchange-rates.html` | See "Considered and rejected". |
| `4-2-1-absolute-relative-poverty.html` | Absolute vs relative poverty; definitional. |
| `4-2-2-inequality.html` | See "Considered and rejected". |
| `4-3-1-measures-of-development.html` | See "Considered and rejected". |
| `4-3-2-factors-influencing-growth-development.html` | Barriers to development; qualitative. Emphasis improved earlier in this pass. |
| `4-3-3-strategies-influencing-growth-development.html` | Strategies and their evaluation; evaluation is out of scope. Emphasis improved earlier. |
| `4-4-1-role-of-financial-markets.html` | Functions of financial markets; qualitative. Emphasis improved earlier. |
| `4-4-2-market-failure-in-the-financial-sector.html` | Types of financial market failure; qualitative. |
| `4-4-3-role-of-central-banks.html` | Central bank functions; qualitative. Emphasis improved earlier. |
| `4-5-1-public-expenditure.html` | Composition and significance of public spending; qualitative. |
| `4-5-2-taxation.html` | See "Considered and rejected". |
| `4-5-3-public-sector-finances.html` | See "Considered and rejected". |
| `4-5-4-macroeconomic-policies-in-a-global-context.html` | Policy in a global context; evaluative and out of scope. |

---

## On approval

These become commit 14, `Add worked examples to Edexcel Theme 4 notes`, with every
insertion appended to `NEW-CONTENT-LOG.md`.

**This completes Phase 1B and Phase 2.** Final total: **31 components across 29 of
the 166 pages** — 82% of pages received nothing, which is the outcome the brief
asked for.

Phase 3 then runs the full verification suite across the whole branch and writes the
closing summary into `REVIEW-NOTES.md`.
