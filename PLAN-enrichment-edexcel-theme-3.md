# PLAN — Part B, batch 5: Edexcel Theme 3 (20 pages)

Phase 1B deliverable. **Nothing here has been applied.** Awaiting approval.

**Proposed: 6 components across 6 pages. 14 of 20 pages get nothing.**

| | |
| --- | ---: |
| Worked examples | 4 |
| Exam tips | 2 |
| **Newly written prose** | **0** |
| Pages receiving 0 | **14** |

**Every component in this batch is an existing AQA component reused verbatim.**
There is no new prose to approve — only placement.

---

## Why this batch is entirely reuse

Theme 3 maps almost one-to-one onto AQA micro sections 1.4–1.6, which received six
components in batch 1. Measured with true `SequenceMatcher.ratio()`:

| Edexcel page | AQA counterpart | Similarity | AQA component |
| --- | --- | ---: | --- |
| `3-3-3-economies-diseconomies-of-scale` | `1-4-5` | **100%** | diseconomies exam tip |
| `3-3-2-costs` | `1-4-4` | **95%** | cost schedule |
| `3-4-4-oligopoly` | `1-5-5` | **85%** | concentration ratio |
| `3-3-1-revenue` | `1-4-6` | 77% | TR/AR/MR schedule |
| `3-5-1-demand-for-labour` | `1-6-1` | 74% | MRP schedule |
| `3-3-4-normal-profits-supernormal-profits-losses` | `1-4-7` | 40% | normal profit exam tip |

The last three fall below the twin threshold on wording, so I checked each page
directly rather than relying on the score. All three carry the **same headings and
the same formulas** as their AQA counterpart, with no figures anywhere:

- `3-3-1` has "Key Definitions", "Revenue in Perfect Competition" and "Revenue in
  Imperfect Competition", with `P × Q`, `TR/Q`, `ΔTR/ΔQ`, `AR = MR = Price` and
  `MR = 0` — plus an extra section on the total revenue rule and PED, which the
  worked example feeds directly.
- `3-3-4` defines normal profit as `TR = TC` and gives `AR > AC` / `AR < AC`
  explicitly — the exact relation the exam tip turns on — plus shut-down rules.
- `3-5-1` has "The Marginal Revenue Product Theory" and `MRP = MPP × MR`.

So the components fit on the content, not just on the similarity score.

---

## Proposed additions

Each is byte-identical to the component already applied to the named AQA page, and
will be hash-verified after insertion as in batches 3 and 4.

| # | Page | Component | Section | Source |
| --- | --- | --- | --- | --- |
| 1 | `3-3-1-revenue.html` | worked example | Revenue in Imperfect Competition | `aqa-a2-micro/1-4-6` |
| 2 | `3-3-2-costs.html` | worked example | Key Definitions | `aqa-a2-micro/1-4-4` |
| 3 | `3-3-3-economies-diseconomies-of-scale.html` | exam tip | Diseconomies of Scale | `aqa-a2-micro/1-4-5` |
| 4 | `3-3-4-normal-profits-supernormal-profits-losses.html` | exam tip | Key Definitions | `aqa-a2-micro/1-4-7` |
| 5 | `3-4-4-oligopoly.html` | worked example | Concentration Ratios | `aqa-a2-micro/1-5-5` |
| 6 | `3-5-1-demand-for-labour.html` | worked example | The Marginal Revenue Product Theory | `aqa-a2-micro/1-6-1` |

The full markup for all six is reproduced in `PLAN-enrichment-aqa-micro.md`.

Summary of what each contains:

1. **TR/AR/MR schedule** — four rows showing MR falling below AR and total revenue
   peaking at £18 where MR crosses zero.
2. **Cost schedule** — TFC/TVC/TC/AC/MC across four output levels, with MC cutting
   AC at its minimum.
3. **Diminishing returns vs diseconomies of scale** — short run and marginal cost
   against long run and long-run average cost.
4. **Normal profit is a cost** — a firm earning it sits at AR = AC, and only the
   area above AC is supernormal.
5. **Concentration ratio** — six firms' sales giving a 3-firm ratio of 90%.
6. **MRP schedule** — MPP turning down, and how many workers are hired at a £80 wage.

---

## Blocker on item 5

**N5 — `3-4-4-oligopoly.html` still carries the error you fixed on the AQA twin.**

```
a 3-firm concentration ratio of 80% means that the top five firms
account for 80% of total market sales
```

You corrected this on `aqa-a2-micro/1-5-5` ("top three firms") on 31 July, but the
Edexcel twin was not changed, so the same sentence is still wrong on this page. It
is the same one-word fix.

This matters here specifically because the proposed worked example sits directly
beneath that sentence and calculates a **3-firm** ratio correctly — which would put
a correct calculation immediately below an incorrect description of the same thing.

**I propose applying items 1–4 and 6 now, and holding item 5 until the word is
fixed** — the same approach taken with `1-2-4-supply` and flag C1 in batch 3. Say if
you would rather I apply all six and you fix the word afterwards.

---

## Considered and rejected

Six Theme 3 pages are near-perfect twins of AQA pages that received nothing in batch
1. Rejecting them again is the consistent call — the reasons that applied to the AQA
page apply unchanged here.

| Page | AQA twin | Similarity | Why not |
| --- | --- | ---: | --- |
| `3-4-2-perfect-competition` | `1-5-3` | 100% | Both already state that entry competes supernormal profit away in the long run. |
| `3-4-3-monopolistic-competition` | `1-5-4` | 100% | Same short-run/long-run adjustment, already worked through. |
| `3-4-1-efficiency` | `1-5-10` | 99% | Allocative and productive efficiency conditions are already tabulated separately. |
| `3-4-7-contestability` | `1-5-9` | 99% | Hit-and-run entry and sunk costs are qualitative. |
| `3-5-2-supply-of-labour` | `1-6-2` | 99% | Qualitative determinants list. |
| `3-2-1-business-objectives` | `1-5-2` | 85% | Objectives are diagram-led and already labelled. |

Edexcel-only pages with no AQA counterpart, all qualitative or diagram-led:
`3-1-1-sizes-types-of-firms`, `3-1-2-business-growth`, `3-1-3-demergers`,
`3-4-6-monopsony`, `3-5-3-wage-determination`, `3-6-1-government-intervention`,
`3-6-2-the-impact-of-government-intervention`. `3-4-5-monopoly` is an 80% twin of
`1-5-6`, which also received nothing; both are diagram-led, and `1-5-6` additionally
carries open flag C4.

---

## No addition — the remaining 14 pages

| Page | Reason |
| --- | --- |
| `3-1-1-sizes-types-of-firms.html` | Firm size and type; qualitative. |
| `3-1-2-business-growth.html` | Organic and inorganic growth; qualitative. |
| `3-1-3-demergers.html` | Reasons for demerger; qualitative. |
| `3-2-1-business-objectives.html` | See "Considered and rejected". |
| `3-4-1-efficiency.html` | See "Considered and rejected". |
| `3-4-2-perfect-competition.html` | See "Considered and rejected". |
| `3-4-3-monopolistic-competition.html` | See "Considered and rejected". |
| `3-4-5-monopoly.html` | Diagram-led; twin `1-5-6` received nothing and carries flag C4. |
| `3-4-6-monopsony.html` | Edexcel-only; diagram-led. |
| `3-4-7-contestability.html` | See "Considered and rejected". |
| `3-5-2-supply-of-labour.html` | See "Considered and rejected". |
| `3-5-3-wage-determination.html` | Diagram-led; the MRP calculation sits on 3.5.1. |
| `3-6-1-government-intervention.html` | Intervention types are diagram-led. |
| `3-6-2-the-impact-of-government-intervention.html` | Evaluative; evaluation components are out of scope. |

---

## On approval

These become commit 12, `Add worked examples and exam tips to Edexcel Theme 3
notes`, with every insertion appended to `NEW-CONTENT-LOG.md`.

After this batch the running total is **27 or 28 components across 25 or 26 pages**
of the 166, depending on whether item 5 goes in now or after the N5 fix.

One batch remains: Theme 4 (21 pages).
