# QUESTIONS_PROGRESS

Batch state for the free practice questions. The authoring standard is
`QUESTIONS_GUIDE.md`; this file records what is done and what is next, so work
can resume cleanly across sessions.

**Live: 23 topics, 166 questions.** Target: 166 topics, ~1,272 questions.

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

## AQA Microeconomics — 23 of 54 topics

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
| 1.5 | Market Structures (11 topics) | 86 | Not started |
| 1.6 | The Labour Market (7 topics) | 53 | Not started |
| 1.7 | Distribution of Income and Wealth (3 topics) | 22 | Not started |
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

---

## Open items

- **Nav sub-menu.** `templates/header.html` carries a top-level
  **Practice Questions** entry only. The two-level board dropdown that Revision
  Notes and Past Papers have is left out until the remaining board index pages
  exist, so the nav never points at a page that has not been built. A comment
  marks the insertion point.
- **Hub and board index density.** Both list only what is live, so they read
  thinly until more boards land. No action needed; they fill out per batch.
