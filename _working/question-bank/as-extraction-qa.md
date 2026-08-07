# Edexcel AS (8EC0) extraction — QA report

7 August 2026. Branch `feature/question-bank-as-level`.
Companion to `extraction-qa-report.md`, which covered the original 9EC0 phase.

---

## 1. What was extracted

**112 questions from 16 papers** — Edexcel AS Economics A (8EC0), Papers 1 and 2,
Section B only. Section A is permanently out of scope.

| | |
| --- | --- |
| Sittings | June 2016, 2017, 2018, 2019, Oct 2020, June 2022, 2023, 2024 |
| Papers per sitting | 2 |
| Questions per paper | 7 — Q6(a) to Q6(g) |
| Question paper / mark scheme pairs | 16 of 16 complete |
| Missing | No June 2020 or 2021 (COVID). No November 2021 — the A Level has that sitting, AS does not |

## 2. Extraction confidence

| Measure | Result |
| --- | --- |
| High confidence | **112 / 112** |
| Low or medium confidence | 0 |
| Extraction notes raised | 0 |
| Problems reported by the extractor | 0 across all 16 papers |

## 3. Page mappings — all verified

Verified twice: once by `verify_past_paper_extraction.swift`, which does not
share the extractor's matching logic, and once by an independent pdfplumber pass
written for this session that re-opens each PDF and checks the stored page by
content.

| Check | Result |
| --- | --- |
| Mark scheme page recorded and `verified: true` | **112 / 112** |
| Mark scheme page names the question | 112 / 112 |
| Question paper page contains the question text | 112 / 112 |
| Extract (`ctxPage`) recorded | **112 / 112** — see §6 |
| Any page number out of range | **0** |

## 4. Mark tariffs — match the papers exactly

Measured from the PDFs before extraction, then compared against the output.

| Marks | Count | Part |
| --- | --- | --- |
| 4 | 16 | one of (a)–(d) |
| 5 | 16 | one of (a)–(d) |
| 6 | 16 | one of (a)–(d) |
| 10 | 16 | one of (a)–(d) |
| 15 | 16 | always (e) |
| 20 | 32 | (f) and (g) — answer one |

All 16 papers total 60 marks for Question 6, and all 16 run (a) to (g) with no
exceptions. (a)–(d) permute 4/5/6/10 — Paper 1 always opens on 5, Paper 2 on 4.

New tariffs entering the bank: **4, 6 and 20**. The marks filter is derived from
the data rather than hard-coded, so they appear without any change.

## 5. Tagging

- **112 / 112 tagged**, by hand, against the existing 87-topic taxonomy.
- **No taxonomy additions.** AS covers Themes 1 and 2, both already present. No
  new slugs means no permanent-URL risk.
- 36 distinct topics used; 37 questions carry more than one topic.
- Heaviest: government intervention (15), inflation (15), demand-side policies
  (11), externalities (9), price determination (8), elasticities of demand (8).
- `tags.json` grew 440 → 552 entries, **793 insertions and 0 deletions** — no
  existing tag was touched.

## 6. AS-specific differences from the A Level

- **No Section C.** 8EC0 is Sections A and B only. Section B carries the whole
  paper bar Section A.
- **The 20-mark essay choice lives inside Section B**, as (f)/(g), where 9EC0
  splits it out as Section C Q7/Q8. Stored as `section: "B"` as printed; no
  Section C was invented for it.
- **Every AS part has an extract page.** 9EC0 Section C has its own short
  stimulus and no extract link, so `ctxPage` is null there. AS (f)/(g) sit under
  the Q6 extracts like every other part, so all 112 carry one. This is the
  opposite of the A Level pattern and is deliberate.
- **Paper names differ** and are taken from the covers: Paper 1 *Introduction to
  Markets and Market Failure*, Paper 2 *The UK Economy – Performance and
  Policies*.

## 7. Duplicates across qualifications

**None.** The working assumption going in was that Edexcel reuses questions
between 8EC0 and 9EC0. It does not.

| Similarity | Count |
| --- | --- |
| Exact (1.00) | **0** |
| Near (0.90–0.99) | **0** |
| Strong (0.80–0.89) | **0** |
| Moderate (0.70–0.79) | 7 |
| Weak (0.60–0.69) | 46 |

The maximum was 0.754, and every match at that level is a shared formulaic stem
— *"With reference to Extract A, assess the likely…"* — over unrelated
economics. Confirmed a second way by rare content-word overlap, which catches
reuse even when stems differ: highest Jaccard 0.556, and the shared words were
all generic (*aggregate, demand, supply*).

Six AS-internal pairs scored above 0.85. All are *"With reference to Figure 1,
explain the term ‘X’"* with a different X each year — *real income*, *net
trade*, *investment*, *inflation rate*. Not duplicates.

Policy recorded in `CLAUDE.md`: **keep both, never collapse.**

## 8. Defects found and fixed

- **Two questions carried a stray trailing full stop** (`…and workers. .`) —
  `p2-june-2023` (a) and (e). The answer-line dot leaders are stripped by a
  6-or-more-dots rule, and where the PDF spaces the first dot away from the rest
  it survived alone. Fixed in `normalise()`, and only ever at the end of the
  string, so an ellipsis or a decimal point mid-sentence cannot be touched. 0
  remain across all 552 questions.
- **The board record's `qualification` became wrong** once Edexcel spanned two
  qualifications. The card badge and the search haystack now read the per-paper
  `qualification`, which was already present and already correct.

## 9. Integration

| Check | Result |
| --- | --- |
| Total bank | 440 → **552 questions from 64 papers** |
| Generated pages | 75 → **90** (2 board, 6 section, 81 topic) |
| Topics at or above the gate of 4 | 66 → **81** |
| Topics with no question | 27 → **15** |
| `questions.json` | 353 KB → **414 KB** raw, 51 KB → **60 KB** gzipped |
| Two build runs byte-identical | Yes, all 90 files |
| Prettier clean | Yes |
| HTML well-formed | 90 files, 0 errors |
| Internal links | 11,678 refs, **0 broken**, 0 broken fragments |
| Python vs JavaScript card renderers | Identical across all 552 |
| Sitemap | 461 URLs, 0 duplicates, valid XML |

**15 topics reach the volume gate only because AS is included**, and so get a
topic page for the first time — among them the economic problem, types of
economies, rational decision making, price elasticity of supply, information
gaps, aggregate demand and consumption. These are exactly the Theme 1–2
foundation topics the original phase noted as empty because Edexcel tests them
in Section A at A Level.

## 10. Labelling

- Badge on **every** card, in the static HTML, not applied by script. Second in
  the row, straight after the board.
- AS and A Level **mixed in one list** on topic pages; both shown by default on
  the master page.
- `Qualification` filter added, defaulting to both.
- Contrast: white on `#37474f` is 9.65:1, white on `#875300` is 6.43:1. The
  badge row is bold uppercase at 0.68em, which is small text, so 4.5:1 is the
  bar. **A lighter goldenrod was tried first and reached only 3.25:1** — it
  looked fine and would have failed an audit.

## 11. Nothing skipped

Every Section B question in all 16 papers was extracted, tagged and published.
No question was dropped, flagged for review, or left untagged.
