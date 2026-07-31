# QUESTIONS_PROGRESS

Batch state for the free practice questions. The authoring standard is
`QUESTIONS_GUIDE.md`; this file records what is done and what is next, so work
can resume cleanly across sessions.

**Live: 44 topics, 327 questions.** Target: 166 topics, ~1,272 questions.

---

## How to resume

```bash
# 1. author questions-data/<board-dir>/<code>.json for each topic in the batch
python3 scripts/build_questions.py --check          # validate, write nothing
python3 scripts/build_questions.py --sitemap        # build pages + sitemap block
python3 scripts/append_questions_link.py            # add the end-of-notes block

# 2. verification, against the commit before the batch
python3 scripts/verify_html.py practice-questions
python3 scripts/verify_links.py practice-questions revision-notes
python3 scripts/verify_text_integrity.py <base-ref>
python3 scripts/verify_markup_integrity.py <base-ref> --strict
git diff <base-ref> -- revision-notes/ | grep '^-[^-]'   # must be empty
```

Then re-solve every question in the batch cold, from the stem alone, and compare
with the recorded key. See "Verification protocol" in `QUESTIONS_GUIDE.md`.

---

## AQA Microeconomics — 44 of 54 topics

| Unit | Topic | Questions | State |
| --- | --- | --- | --- |
| 1.1 | 1.1.1 Economic Methodology | 6 | Done |
| 1.1 | 1.1.2 The Nature and Purpose of Economic Activity | 5 | Done |
| 1.1 | 1.1.3 Economic Resources | 5 | Done |
| 1.1 | 1.1.4 Scarcity, Choice and the Allocation of Resources | 6 | Done |
| 1.1 | 1.1.5 Production Possibility Diagrams | 8 | Done |
| 1.2 | 1.2.1 Consumer Behaviour | 7 | Done |
| 1.2 | 1.2.2 Imperfect Information | 6 | Done |
| 1.2 | 1.2.3 Aspects of Behavioural Economic Theory | 8 | Done |
| 1.2 | 1.2.4 Behavioural Economics and Economic Policy | 6 | Done |
| 1.3 | 1.3.1 The Determinants of Demand | 7 | Done |
| 1.3 | 1.3.2 Price, Income and Cross Elasticities of Demand | 10 | Done |
| 1.3 | 1.3.3 The Determinants of Supply | 6 | Done |
| 1.3 | 1.3.4 Price Elasticity of Supply | 8 | Done |
| 1.3 | 1.3.5 The Determination of Equilibrium Market Prices | 9 | Done |
| 1.3 | 1.3.6 The Interrelationship between Markets | 7 | Done |
| 1.4 | 1.4.1 Production and Productivity | 7 | Done |
| 1.4 | 1.4.2 Specialisation, Division of Labour and Exchange | 6 | Done |
| 1.4 | 1.4.3 The Law of Diminishing Returns and Returns to Scale | 9 | Done |
| 1.4 | 1.4.4 Costs of Production | 10 | Done |
| 1.4 | 1.4.5 Economies and Diseconomies of Scale | 8 | Done |
| 1.4 | 1.4.6 Marginal, Average and Total Revenue | 9 | Done |
| 1.4 | 1.4.7 Profit | 8 | Done |
| 1.4 | 1.4.8 Technological Change | 5 | Done |
| 1.5 | 1.5.1 Market Structures | 7 | Done |
| 1.5 | 1.5.2 The Objectives of Firms | 7 | Done |
| 1.5 | 1.5.3 Perfect Competition | 9 | Done |
| 1.5 | 1.5.4 Monopolistic Competition | 7 | Done |
| 1.5 | 1.5.5 Oligopoly | 9 | Done |
| 1.5 | 1.5.6 Monopoly and Monopoly Power | 9 | Done |
| 1.5 | 1.5.7 Price Discrimination | 8 | Done |
| 1.5 | 1.5.8 The Dynamics of Competition | 6 | Done |
| 1.5 | 1.5.9 Contestable and Non-Contestable Markets | 8 | Done |
| 1.5 | 1.5.10 Market Structure and Efficiency | 8 | Done |
| 1.5 | 1.5.11 Consumer and Producer Surplus | 8 | Done |
| 1.6 | 1.6.1 The Demand for Labour, Marginal Productivity Theory | 9 | Done |
| 1.6 | 1.6.2 Influences upon the Supply of Labour | 7 | Done |
| 1.6 | 1.6.3 Wage Determination: Competitive Labour Markets | 8 | Done |
| 1.6 | 1.6.4 Wage Determination: Imperfect Labour Markets | 8 | Done |
| 1.6 | 1.6.5 The Influence of Trade Unions | 7 | Done |
| 1.6 | 1.6.6 The National Minimum Wage | 8 | Done |
| 1.6 | 1.6.7 Discrimination in the Labour Market | 6 | Done |
| 1.7 | 1.7.1 The Distribution of Income and Wealth | 8 | Done |
| 1.7 | 1.7.2 The Problem of Poverty | 7 | Done |
| 1.7 | 1.7.3 Government Policies on Poverty and Distribution | 7 | Done |
| 1.8 | Market Failure and Government Intervention (10 topics) | 74 | Not started |

## Remaining boards — 0 of 112 topics

| Board | Topics | Planned questions | State |
| --- | --- | --- | --- |
| AQA Macroeconomics | 25 | 209 | Not started |
| Edexcel Theme 1 | 22 | 157 | Not started |
| Edexcel Theme 2 | 24 | 185 | Not started |
| Edexcel Theme 3 | 20 | 157 | Not started |
| Edexcel Theme 4 | 21 | 163 | Not started |

---

## Batch record

### Batch 1 — AQA micro 1.1–1.3 (2026-07-31)

15 topics, 104 questions. All 94 new questions re-solved cold from the stem
alone with **0 mismatches** against the recorded keys; every figure in every
calculation and data table recomputed and confirmed.

Fixed during verification:

- 1.3.6 failed the generator's letter-distribution check (C used four times in
  a set of seven). Option order across the four "effect on the other market"
  questions was regularised to demand-up / demand-down / supply-up /
  supply-down, which spread the answers and made the set internally consistent.
- 23 options rewritten across 9 sets because the correct option was more than
  10% longer than the next longest — a formatting tell. None remain.

Batch profile:

| | |
| --- | --- |
| Answer letters | A 30, B 28, C 21, D 25 (even would be 26) |
| Skills | applied-reasoning 62, definition-in-context 23, data-table 12, calculation 7 |
| Difficulty | foundation 16, standard 75, stretch 13 |
| Sketch to solve | 8 (8%) |

**Note on the skill mix.** `calculation` is well under its ~15% target for this
batch and `applied-reasoning` well over. That is a property of these topics
rather than a drafting failure: methodology, economic resources, imperfect
information and behavioural economics offer almost nothing to calculate. The
arithmetic in this batch is concentrated where it exists — 1.1.4, 1.1.5, 1.2.1,
1.3.4 and 1.3.5. Units 1.4 (costs and revenue) and 1.5 (market structures) will
pull the ratio back up on their own.

### Batch 2 — AQA micro 1.4 (2026-07-31)

8 topics, 62 questions. All 62 re-solved cold from the stem alone with **0
mismatches**; every figure in every calculation and cost, revenue and output
schedule recomputed and confirmed.

Fixed during verification:

- 1.4.5 failed the generator's letter-distribution check (A used five times in
  a set of eight). The "which type of economy of scale" questions were being
  pushed to early letters because the option lists were alphabetical. Ordering
  them as the notes list the types instead spread the answers out.
- 12 options rewritten because the correct answer was more than 10% longer
  than the next longest. None remain anywhere on the site.

Site profile after batch 2:

| | |
| --- | --- |
| Answer letters | A 46, B 48, C 39, D 33 (even would be 41.5) |
| Skills | applied-reasoning 96, definition-in-context 35, data-table 21, calculation 14 |
| Difficulty | foundation 24, standard 123, stretch 19 |
| Sketch to solve | 8 |

The `calculation` share recovered as predicted: unit 1.4 contributed 7 of the
site's 14 calculation items, and its data-table share is higher again, since
cost, revenue and output schedules are the natural form for this material.

### Batch 3 — AQA micro 1.5 (2026-07-31)

11 topics, 86 questions — the largest unit on the specification. All 86
re-solved cold from the stem alone with **0 mismatches**; the concentration
ratio and surplus calculations were recomputed and confirmed, including every
distractor figure.

Fixed during verification:

- 1.5.3 and 1.5.1 both failed the letter-distribution check. The cause was the
  same in each: option lists naming market structures sort alphabetically, and
  alphabetical order kept pushing the correct answer to an early letter. Those
  sets now order the structures by the competitive spectrum instead.
- 20 options rewritten where the correct answer ran more than 10% longer than
  the next longest.
- **A bug in the generator's own US-spelling blocklist.** It flagged
  `practise`, which is the correct UK *verb* form — the noun is `practice`.
  `license` had the same problem, being the UK verb alongside the noun
  `licence`. Both removed, with a comment recording why.

Site profile after batch 3:

| | |
| --- | --- |
| Answer letters | A 65, B 74, C 63, D 50 (even would be 63) |
| Skills | applied-reasoning 151, definition-in-context 59, data-table 24, calculation 18 |
| Difficulty | foundation 35, standard 187, stretch 30 |
| Sketch to solve | 15 |

### Batch 4 — AQA micro 1.6 and 1.7 (2026-07-31)

10 topics, 75 questions. All 75 re-solved cold from the stem alone with **0
mismatches**; the MRP, union density and relative poverty line calculations
were recomputed, including every distractor figure.

Fixed during verification:

- 1.6.7 and 1.7.2 both failed the letter-distribution check; option order was
  regularised in each.
- 19 options rewritten where the correct answer ran more than 10% longer than
  the next longest.

The monopsony result — that a union or a minimum wage can raise pay <em>and</em>
employment where a single dominant employer has been restricting hiring — is
tested three times from different angles (1.6.4 Q5, 1.6.5 Q6, 1.6.6 Q5),
because it is the evaluation point these topics turn on.

Site profile after batch 4:

| | |
| --- | --- |
| Answer letters | A 83, B 101, C 80, D 63 (even would be 82) |
| Skills | applied-reasoning 203, definition-in-context 76, data-table 26, calculation 22 |
| Difficulty | foundation 45, standard 242, stretch 40 |
| Sketch to solve | 17 |

---

## Open items

- **Nav sub-menu.** `templates/header.html` carries a top-level
  **Practice Questions** entry only. The two-level board dropdown that Revision
  Notes and Past Papers have is left out until the remaining board index pages
  exist, so the nav never points at a page that has not been built. A comment
  marks the insertion point.
- **Hub and board index density.** Both list only what is live, so they read
  thinly until more boards land. No action needed; they fill out per batch.
