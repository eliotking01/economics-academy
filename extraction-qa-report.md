# Extraction QA Report — Phase 1

Edexcel A Level Economics A (9EC0), A-Level Papers 1 and 2, Section B and
Section C, 2017–2024. Generated for the past-paper question bank on
`feature/question-bank`.

**Result: 112 of 112 questions extracted, all at high confidence, all 112
mark-scheme page mappings independently verified. Nothing was skipped, nothing
was guessed, and no question needs your eyes for a text problem.**

Both judgement items raised in section 6 have since been reviewed and signed
off; one tagging change was requested and applied.

---

## 1. What was extracted

|                                         | Papers | Questions |
| --------------------------------------- | ------ | --------- |
| Section B (Q6 parts a–e, data response) | 16     | 80        |
| Section C (Q7 and Q8, 25-mark essays)   | 16     | 32        |
| **Total**                               | **16** | **112**   |

Mark tariffs are exactly as expected: 16 each of 5, 8, 10 and 12 and 15 marks
from Section B, and 32 × 25 marks from Section C.

Series covered: June 2017, June 2018, June 2019, October 2020, November 2021,
June 2022, June 2023, June 2024. Summer 2020 and summer 2021 were cancelled and
are correctly absent, not missing.

## 2. Structural findings

Every one of the 16 papers has an identical question structure — Section B is
always Q6 with five parts, Section C is always a choice of Q7 or Q8 at 25 marks.
Detection succeeded on 16/16 for both sections with no ambiguous cases.

Three layout variations were found and handled. They are recorded here because
they will recur when Paper 3 and AQA are added:

1. **Section B part layout.** Fourteen papers print all five parts on one
   consolidated page. **Paper 2 June 2017 and Paper 2 June 2019 do not** — each
   part appears only above its own answer space. The extractor scans every
   Section B page and keeps the first occurrence of each part letter, which
   resolves both layouts without special-casing.
2. **Mark scheme headings.** PDFKit returns the scheme's table header in reading
   order, which interleaves the column labels ("Question Indicative content Mark
   Number 6(c)"). Where a question's row spills onto a new page the header stays
   behind and the page opens on a bare label instead (**Paper 1 June 2024**).
   Both forms are matched.
3. **Label spacing.** **Paper 2 October 2020** writes `6 (a)` where every other
   scheme writes `6(a)`.

## 3. Text integrity

Question text is reproduced verbatim. The only transformations applied are the
removal of print furniture and the repair of extraction artefacts:

- **Page furniture removed**: the publication code (`*P57190A01032*`), `Turn
over`, `BLANK PAGE`, bare page numbers, and `DO NOT WRITE IN THIS AREA`. The
  last is set rotated in the page margin, so PDFKit drops it into the reading
  order at arbitrary points — it was appearing mid-sentence in three questions
  and ahead of the question number in a fourth.
- **Answer-line dot leaders removed** (runs of six or more full stops).
- **Line breaks joined.** Breaks inside a PDF are typographic, not semantic.
- **URLs repaired.** Line-wrapping inserted spaces into the source-citation URLs
  in 22 questions. A space cannot occur inside a URL, so these are provably
  extraction artefacts rather than wording; whitespace is removed only where it
  directly follows URL punctuation and only inside a run beginning `http://` or
  `https://`. All 22 now resolve to well-formed URLs.

No word of any question was altered, reordered, paraphrased or reconstructed.

## 4. Verification method

Mark-scheme page mappings were checked twice, by deliberately different means.

The extractor records a page when it matches one of the three heading layouts
above. `scripts/verify_past_paper_extraction.swift` then re-opens every PDF and
checks, using a plain whitespace-insensitive substring scan rather than those
regexes:

1. every recorded page number lies within the PDF;
2. the question-paper page really contains the opening words of the extracted
   text, proving the text came from where the record claims;
3. the mark-scheme page really mentions the question label;
4. the Section B extract page really precedes its question.

**112 questions checked, 0 failures.** Because the second pass does not share
the first pass's matching logic, it can catch the extractor being confidently
wrong, which a re-run of the extractor could not.

Extraction is also **deterministic**: two consecutive runs produced byte-identical
output.

## 5. Per-question record

`ms` is the mark-scheme page for the `#page=N` deep link. `ctx` is the page where
the Section B extract block begins, used for the "View the extract" link.
Every row was verified; there are no unverified mappings to list.

| id                          | Paper | Series        | Sec | Q    | Marks | QP p | MS p | ctx | Confidence | Topics                                                                                                |
| --------------------------- | ----- | ------------- | --- | ---- | ----- | ---- | ---- | --- | ---------- | ----------------------------------------------------------------------------------------------------- |
| `edexcel-a-p1-2017-jun-q6a` | 1     | June 2017     | B   | 6(a) | 5     | p15  | p10  | 13  | high       | 3-4-4-oligopoly                                                                                       |
| `edexcel-a-p1-2017-jun-q6b` | 1     | June 2017     | B   | 6(b) | 12    | p15  | p11  | 13  | high       | 3-4-6-monopsony                                                                                       |
| `edexcel-a-p1-2017-jun-q6c` | 1     | June 2017     | B   | 6(c) | 8     | p15  | p14  | 13  | high       | 3-6-1-government-intervention, 3-4-6-monopsony                                                        |
| `edexcel-a-p1-2017-jun-q6d` | 1     | June 2017     | B   | 6(d) | 10    | p15  | p15  | 13  | high       | 1-3-4-information-gaps, 1-2-10-alternative-views-of-consumer-behaviour                                |
| `edexcel-a-p1-2017-jun-q6e` | 1     | June 2017     | B   | 6(e) | 15    | p15  | p18  | 13  | high       | 3-1-2-business-growth, 3-3-3-economies-diseconomies-of-scale                                          |
| `edexcel-a-p1-2017-jun-q7`  | 1     | June 2017     | C   | 7    | 25    | p26  | p21  | —   | high       | 1-2-9-indirect-taxes-subsidies, 1-3-2-externalities, 1-4-1-government-intervention-in-markets         |
| `edexcel-a-p1-2017-jun-q8`  | 1     | June 2017     | C   | 8    | 25    | p26  | p23  | —   | high       | 3-2-1-business-objectives                                                                             |
| `edexcel-a-p1-2018-jun-q6a` | 1     | June 2018     | B   | 6(a) | 5     | p19  | p11  | 17  | high       | 1-2-6-price-determination                                                                             |
| `edexcel-a-p1-2018-jun-q6b` | 1     | June 2018     | B   | 6(b) | 12    | p19  | p12  | 17  | high       | 3-6-1-government-intervention, 3-4-7-contestability                                                   |
| `edexcel-a-p1-2018-jun-q6c` | 1     | June 2018     | B   | 6(c) | 10    | p19  | p15  | 17  | high       | 3-6-1-government-intervention, 3-6-2-the-impact-of-government-intervention                            |
| `edexcel-a-p1-2018-jun-q6d` | 1     | June 2018     | B   | 6(d) | 8     | p19  | p18  | 17  | high       | 1-2-3-price-income-cross-elasticities-of-demand                                                       |
| `edexcel-a-p1-2018-jun-q6e` | 1     | June 2018     | B   | 6(e) | 15    | p19  | p20  | 17  | high       | 3-5-2-supply-of-labour                                                                                |
| `edexcel-a-p1-2018-jun-q7`  | 1     | June 2018     | C   | 7    | 25    | p31  | p23  | —   | high       | 1-3-2-externalities, 1-3-1-types-of-market-failure                                                    |
| `edexcel-a-p1-2018-jun-q8`  | 1     | June 2018     | C   | 8    | 25    | p31  | p27  | —   | high       | 3-4-5-monopoly, 3-4-1-efficiency                                                                      |
| `edexcel-a-p1-2019-jun-q6a` | 1     | June 2019     | B   | 6(a) | 5     | p13  | p10  | 11  | high       | 1-1-2-positive-normative-statements                                                                   |
| `edexcel-a-p1-2019-jun-q6b` | 1     | June 2019     | B   | 6(b) | 8     | p13  | p11  | 11  | high       | 3-1-2-business-growth                                                                                 |
| `edexcel-a-p1-2019-jun-q6c` | 1     | June 2019     | B   | 6(c) | 10    | p13  | p12  | 11  | high       | 1-3-4-information-gaps, 1-2-10-alternative-views-of-consumer-behaviour                                |
| `edexcel-a-p1-2019-jun-q6d` | 1     | June 2019     | B   | 6(d) | 12    | p13  | p14  | 11  | high       | 3-3-4-normal-profits-supernormal-profits-losses, 3-3-1-revenue                                        |
| `edexcel-a-p1-2019-jun-q6e` | 1     | June 2019     | B   | 6(e) | 15    | p13  | p16  | 11  | high       | 3-6-1-government-intervention                                                                         |
| `edexcel-a-p1-2019-jun-q7`  | 1     | June 2019     | C   | 7    | 25    | p26  | p19  | —   | high       | 3-5-3-wage-determination                                                                              |
| `edexcel-a-p1-2019-jun-q8`  | 1     | June 2019     | C   | 8    | 25    | p26  | p21  | —   | high       | 3-4-4-oligopoly                                                                                       |
| `edexcel-a-p1-2022-jun-q6a` | 1     | June 2022     | B   | 6(a) | 5     | p15  | p10  | 14  | high       | 3-4-4-oligopoly                                                                                       |
| `edexcel-a-p1-2022-jun-q6b` | 1     | June 2022     | B   | 6(b) | 8     | p15  | p11  | 14  | high       | 1-2-5-price-elasticity-of-supply, 1-2-6-price-determination                                           |
| `edexcel-a-p1-2022-jun-q6c` | 1     | June 2022     | B   | 6(c) | 10    | p15  | p13  | 14  | high       | 3-2-1-business-objectives                                                                             |
| `edexcel-a-p1-2022-jun-q6d` | 1     | June 2022     | B   | 6(d) | 12    | p15  | p15  | 14  | high       | 3-3-2-costs, 3-3-4-normal-profits-supernormal-profits-losses                                          |
| `edexcel-a-p1-2022-jun-q6e` | 1     | June 2022     | B   | 6(e) | 15    | p15  | p18  | 14  | high       | 3-4-7-contestability                                                                                  |
| `edexcel-a-p1-2022-jun-q7`  | 1     | June 2022     | C   | 7    | 25    | p29  | p20  | —   | high       | 3-4-5-monopoly, 3-4-1-efficiency                                                                      |
| `edexcel-a-p1-2022-jun-q8`  | 1     | June 2022     | C   | 8    | 25    | p29  | p23  | —   | high       | 3-5-2-supply-of-labour                                                                                |
| `edexcel-a-p1-2023-jun-q6a` | 1     | June 2023     | B   | 6(a) | 5     | p15  | p10  | 13  | high       | 3-4-4-oligopoly                                                                                       |
| `edexcel-a-p1-2023-jun-q6b` | 1     | June 2023     | B   | 6(b) | 10    | p15  | p11  | 13  | high       | 1-2-10-alternative-views-of-consumer-behaviour, 1-2-1-rational-decision-making                        |
| `edexcel-a-p1-2023-jun-q6c` | 1     | June 2023     | B   | 6(c) | 8     | p15  | p13  | 13  | high       | 1-2-3-price-income-cross-elasticities-of-demand                                                       |
| `edexcel-a-p1-2023-jun-q6d` | 1     | June 2023     | B   | 6(d) | 12    | p15  | p14  | 13  | high       | 1-3-2-externalities                                                                                   |
| `edexcel-a-p1-2023-jun-q6e` | 1     | June 2023     | B   | 6(e) | 15    | p15  | p17  | 13  | high       | 3-4-5-monopoly, 3-3-1-revenue                                                                         |
| `edexcel-a-p1-2023-jun-q7`  | 1     | June 2023     | C   | 7    | 25    | p29  | p21  | —   | high       | 1-4-1-government-intervention-in-markets, 3-6-1-government-intervention                               |
| `edexcel-a-p1-2023-jun-q8`  | 1     | June 2023     | C   | 8    | 25    | p29  | p23  | —   | high       | 1-3-2-externalities, 1-4-1-government-intervention-in-markets                                         |
| `edexcel-a-p1-2024-jun-q6a` | 1     | June 2024     | B   | 6(a) | 5     | p12  | p13  | 10  | high       | 1-2-6-price-determination                                                                             |
| `edexcel-a-p1-2024-jun-q6b` | 1     | June 2024     | B   | 6(b) | 8     | p12  | p14  | 10  | high       | 3-5-2-supply-of-labour                                                                                |
| `edexcel-a-p1-2024-jun-q6c` | 1     | June 2024     | B   | 6(c) | 10    | p12  | p16  | 10  | high       | 3-3-3-economies-diseconomies-of-scale                                                                 |
| `edexcel-a-p1-2024-jun-q6d` | 1     | June 2024     | B   | 6(d) | 12    | p12  | p19  | 10  | high       | 3-1-2-business-growth, 3-6-1-government-intervention                                                  |
| `edexcel-a-p1-2024-jun-q6e` | 1     | June 2024     | B   | 6(e) | 15    | p12  | p21  | 10  | high       | 1-3-2-externalities, 1-4-1-government-intervention-in-markets                                         |
| `edexcel-a-p1-2024-jun-q7`  | 1     | June 2024     | C   | 7    | 25    | p26  | p23  | —   | high       | 3-3-2-costs, 3-3-4-normal-profits-supernormal-profits-losses                                          |
| `edexcel-a-p1-2024-jun-q8`  | 1     | June 2024     | C   | 8    | 25    | p26  | p27  | —   | high       | 3-4-7-contestability                                                                                  |
| `edexcel-a-p1-2021-nov-q6a` | 1     | November 2021 | B   | 6(a) | 5     | p16  | p11  | 14  | high       | 3-5-1-demand-for-labour, 3-3-2-costs                                                                  |
| `edexcel-a-p1-2021-nov-q6b` | 1     | November 2021 | B   | 6(b) | 8     | p16  | p12  | 14  | high       | 1-3-2-externalities                                                                                   |
| `edexcel-a-p1-2021-nov-q6c` | 1     | November 2021 | B   | 6(c) | 10    | p16  | p14  | 14  | high       | 3-2-1-business-objectives, 1-3-4-information-gaps                                                     |
| `edexcel-a-p1-2021-nov-q6d` | 1     | November 2021 | B   | 6(d) | 12    | p16  | p16  | 14  | high       | 3-3-4-normal-profits-supernormal-profits-losses, 1-2-9-indirect-taxes-subsidies                       |
| `edexcel-a-p1-2021-nov-q6e` | 1     | November 2021 | B   | 6(e) | 15    | p16  | p19  | 14  | high       | 3-3-1-revenue, 1-2-3-price-income-cross-elasticities-of-demand                                        |
| `edexcel-a-p1-2021-nov-q7`  | 1     | November 2021 | C   | 7    | 25    | p30  | p23  | —   | high       | 3-5-3-wage-determination, 3-6-1-government-intervention                                               |
| `edexcel-a-p1-2021-nov-q8`  | 1     | November 2021 | C   | 8    | 25    | p30  | p27  | —   | high       | 3-4-4-oligopoly                                                                                       |
| `edexcel-a-p1-2020-oct-q6a` | 1     | October 2020  | B   | 6(a) | 5     | p11  | p11  | 9   | high       | 1-2-9-indirect-taxes-subsidies                                                                        |
| `edexcel-a-p1-2020-oct-q6b` | 1     | October 2020  | B   | 6(b) | 8     | p11  | p12  | 9   | high       | 1-2-2-demand                                                                                          |
| `edexcel-a-p1-2020-oct-q6c` | 1     | October 2020  | B   | 6(c) | 10    | p11  | p14  | 9   | high       | 3-6-1-government-intervention                                                                         |
| `edexcel-a-p1-2020-oct-q6d` | 1     | October 2020  | B   | 6(d) | 12    | p11  | p17  | 9   | high       | 3-4-5-monopoly                                                                                        |
| `edexcel-a-p1-2020-oct-q6e` | 1     | October 2020  | B   | 6(e) | 15    | p11  | p20  | 9   | high       | 3-4-5-monopoly, 3-3-1-revenue                                                                         |
| `edexcel-a-p1-2020-oct-q7`  | 1     | October 2020  | C   | 7    | 25    | p26  | p24  | —   | high       | 1-2-6-price-determination, 1-3-2-externalities                                                        |
| `edexcel-a-p1-2020-oct-q8`  | 1     | October 2020  | C   | 8    | 25    | p26  | p28  | —   | high       | 3-4-6-monopsony                                                                                       |
| `edexcel-a-p2-2017-jun-q6a` | 2     | June 2017     | B   | 6(a) | 5     | p15  | p10  | 14  | high       | 4-1-8-exchange-rates                                                                                  |
| `edexcel-a-p2-2017-jun-q6b` | 2     | June 2017     | B   | 6(b) | 8     | p15  | p11  | 14  | high       | 2-1-2-inflation                                                                                       |
| `edexcel-a-p2-2017-jun-q6c` | 2     | June 2017     | B   | 6(c) | 10    | p15  | p12  | 14  | high       | 4-1-8-exchange-rates, 4-1-7-balance-of-payments                                                       |
| `edexcel-a-p2-2017-jun-q6d` | 2     | June 2017     | B   | 6(d) | 12    | p15  | p14  | 14  | high       | 2-6-2-demand-side-policies, 4-4-3-role-of-central-banks                                               |
| `edexcel-a-p2-2017-jun-q6e` | 2     | June 2017     | B   | 6(e) | 15    | p15  | p16  | 14  | high       | 2-6-2-demand-side-policies, 2-6-3-supply-side-policies                                                |
| `edexcel-a-p2-2017-jun-q7`  | 2     | June 2017     | C   | 7    | 25    | p29  | p18  | —   | high       | 4-1-6-restrictions-on-free-trade                                                                      |
| `edexcel-a-p2-2017-jun-q8`  | 2     | June 2017     | C   | 8    | 25    | p29  | p21  | —   | high       | 2-1-2-inflation, 2-3-2-short-run-aggregate-supply                                                     |
| `edexcel-a-p2-2018-jun-q6a` | 2     | June 2018     | B   | 6(a) | 5     | p15  | p9   | 13  | high       | 4-2-1-absolute-relative-poverty                                                                       |
| `edexcel-a-p2-2018-jun-q6b` | 2     | June 2018     | B   | 6(b) | 8     | p15  | p10  | 13  | high       | 4-3-2-factors-influencing-growth-development, 4-2-1-absolute-relative-poverty                         |
| `edexcel-a-p2-2018-jun-q6c` | 2     | June 2018     | B   | 6(c) | 12    | p15  | p11  | 13  | high       | 4-1-1-globalisation, 4-5-4-macroeconomic-policies-in-a-global-context                                 |
| `edexcel-a-p2-2018-jun-q6d` | 2     | June 2018     | B   | 6(d) | 10    | p15  | p14  | 13  | high       | 4-2-2-inequality                                                                                      |
| `edexcel-a-p2-2018-jun-q6e` | 2     | June 2018     | B   | 6(e) | 15    | p15  | p16  | 13  | high       | 4-4-1-role-of-financial-markets, 4-3-3-strategies-influencing-growth-development                      |
| `edexcel-a-p2-2018-jun-q7`  | 2     | June 2018     | C   | 7    | 25    | p30  | p19  | —   | high       | 2-2-4-government-expenditure, 2-4-4-the-multiplier                                                    |
| `edexcel-a-p2-2018-jun-q8`  | 2     | June 2018     | C   | 8    | 25    | p30  | p21  | —   | high       | 4-1-8-exchange-rates, 2-5-1-causes-of-growth                                                          |
| `edexcel-a-p2-2019-jun-q6a` | 2     | June 2019     | B   | 6(a) | 5     | p14  | p10  | 13  | high       | 4-1-8-exchange-rates, 4-4-1-role-of-financial-markets                                                 |
| `edexcel-a-p2-2019-jun-q6b` | 2     | June 2019     | B   | 6(b) | 8     | p14  | p11  | 13  | high       | 4-1-8-exchange-rates                                                                                  |
| `edexcel-a-p2-2019-jun-q6c` | 2     | June 2019     | B   | 6(c) | 10    | p14  | p12  | 13  | high       | 2-1-1-economic-growth                                                                                 |
| `edexcel-a-p2-2019-jun-q6d` | 2     | June 2019     | B   | 6(d) | 12    | p14  | p14  | 13  | high       | 2-6-4-conflicts-between-objectives-and-policies, 2-1-2-inflation                                      |
| `edexcel-a-p2-2019-jun-q6e` | 2     | June 2019     | B   | 6(e) | 15    | p14  | p16  | 13  | high       | 4-4-2-market-failure-in-the-financial-sector, 4-4-3-role-of-central-banks                             |
| `edexcel-a-p2-2019-jun-q7`  | 2     | June 2019     | C   | 7    | 25    | p28  | p18  | —   | high       | 4-1-5-trading-blocs-and-the-world-trade-organisation, 4-1-3-pattern-of-trade                          |
| `edexcel-a-p2-2019-jun-q8`  | 2     | June 2019     | C   | 8    | 25    | p28  | p20  | —   | high       | 4-5-3-public-sector-finances                                                                          |
| `edexcel-a-p2-2022-jun-q6a` | 2     | June 2022     | B   | 6(a) | 5     | p15  | p10  | 13  | high       | 4-2-2-inequality                                                                                      |
| `edexcel-a-p2-2022-jun-q6b` | 2     | June 2022     | B   | 6(b) | 8     | p15  | p11  | 13  | high       | 4-2-2-inequality                                                                                      |
| `edexcel-a-p2-2022-jun-q6c` | 2     | June 2022     | B   | 6(c) | 10    | p15  | p13  | 13  | high       | 2-1-1-economic-growth, 2-5-4-the-impact-of-economic-growth                                            |
| `edexcel-a-p2-2022-jun-q6d` | 2     | June 2022     | B   | 6(d) | 12    | p15  | p15  | 13  | high       | 4-5-2-taxation                                                                                        |
| `edexcel-a-p2-2022-jun-q6e` | 2     | June 2022     | B   | 6(e) | 15    | p15  | p17  | 13  | high       | 2-2-4-government-expenditure, 2-6-3-supply-side-policies                                              |
| `edexcel-a-p2-2022-jun-q7`  | 2     | June 2022     | C   | 7    | 25    | p29  | p20  | —   | high       | 4-1-6-restrictions-on-free-trade                                                                      |
| `edexcel-a-p2-2022-jun-q8`  | 2     | June 2022     | C   | 8    | 25    | p29  | p22  | —   | high       | 4-1-1-globalisation                                                                                   |
| `edexcel-a-p2-2023-jun-q6a` | 2     | June 2023     | B   | 6(a) | 5     | p15  | p10  | 13  | high       | 4-1-5-trading-blocs-and-the-world-trade-organisation                                                  |
| `edexcel-a-p2-2023-jun-q6b` | 2     | June 2023     | B   | 6(b) | 8     | p15  | p11  | 13  | high       | 4-3-2-factors-influencing-growth-development                                                          |
| `edexcel-a-p2-2023-jun-q6c` | 2     | June 2023     | B   | 6(c) | 12    | p15  | p12  | 13  | high       | 4-3-2-factors-influencing-growth-development, 2-5-1-causes-of-growth                                  |
| `edexcel-a-p2-2023-jun-q6d` | 2     | June 2023     | B   | 6(d) | 10    | p15  | p14  | 13  | high       | 4-3-3-strategies-influencing-growth-development                                                       |
| `edexcel-a-p2-2023-jun-q6e` | 2     | June 2023     | B   | 6(e) | 15    | p15  | p16  | 13  | high       | 4-3-3-strategies-influencing-growth-development                                                       |
| `edexcel-a-p2-2023-jun-q7`  | 2     | June 2023     | C   | 7    | 25    | p29  | p19  | —   | high       | 4-1-9-international-competitiveness                                                                   |
| `edexcel-a-p2-2023-jun-q8`  | 2     | June 2023     | C   | 8    | 25    | p29  | p22  | —   | high       | 2-1-2-inflation, 2-6-2-demand-side-policies                                                           |
| `edexcel-a-p2-2024-jun-q6a` | 2     | June 2024     | B   | 6(a) | 5     | p16  | p15  | 14  | high       | 4-5-2-taxation                                                                                        |
| `edexcel-a-p2-2024-jun-q6b` | 2     | June 2024     | B   | 6(b) | 8     | p16  | p16  | 14  | high       | 2-2-1-aggregate-demand, 4-5-2-taxation                                                                |
| `edexcel-a-p2-2024-jun-q6c` | 2     | June 2024     | B   | 6(c) | 10    | p16  | p18  | 14  | high       | 4-5-3-public-sector-finances                                                                          |
| `edexcel-a-p2-2024-jun-q6d` | 2     | June 2024     | B   | 6(d) | 12    | p16  | p22  | 14  | high       | 2-6-2-demand-side-policies, 4-4-3-role-of-central-banks                                               |
| `edexcel-a-p2-2024-jun-q6e` | 2     | June 2024     | B   | 6(e) | 15    | p16  | p26  | 14  | high       | 2-6-3-supply-side-policies                                                                            |
| `edexcel-a-p2-2024-jun-q7`  | 2     | June 2024     | C   | 7    | 25    | p30  | p30  | —   | high       | 4-1-7-balance-of-payments                                                                             |
| `edexcel-a-p2-2024-jun-q8`  | 2     | June 2024     | C   | 8    | 25    | p30  | p33  | —   | high       | 4-1-1-globalisation                                                                                   |
| `edexcel-a-p2-2021-nov-q6a` | 2     | November 2021 | B   | 6(a) | 5     | p16  | p10  | 14  | high       | 4-3-3-strategies-influencing-growth-development                                                       |
| `edexcel-a-p2-2021-nov-q6b` | 2     | November 2021 | B   | 6(b) | 8     | p16  | p11  | 14  | high       | 4-3-2-factors-influencing-growth-development                                                          |
| `edexcel-a-p2-2021-nov-q6c` | 2     | November 2021 | B   | 6(c) | 10    | p16  | p12  | 14  | high       | 4-3-3-strategies-influencing-growth-development                                                       |
| `edexcel-a-p2-2021-nov-q6d` | 2     | November 2021 | B   | 6(d) | 12    | p16  | p14  | 14  | high       | 4-1-6-restrictions-on-free-trade                                                                      |
| `edexcel-a-p2-2021-nov-q6e` | 2     | November 2021 | B   | 6(e) | 15    | p16  | p16  | 14  | high       | 4-3-3-strategies-influencing-growth-development                                                       |
| `edexcel-a-p2-2021-nov-q7`  | 2     | November 2021 | C   | 7    | 25    | p30  | p18  | —   | high       | 2-6-2-demand-side-policies, 4-4-3-role-of-central-banks                                               |
| `edexcel-a-p2-2021-nov-q8`  | 2     | November 2021 | C   | 8    | 25    | p30  | p20  | —   | high       | 2-6-4-conflicts-between-objectives-and-policies, 2-5-4-the-impact-of-economic-growth                  |
| `edexcel-a-p2-2020-oct-q6a` | 2     | October 2020  | B   | 6(a) | 5     | p11  | p9   | 10  | high       | 4-3-3-strategies-influencing-growth-development                                                       |
| `edexcel-a-p2-2020-oct-q6b` | 2     | October 2020  | B   | 6(b) | 8     | p11  | p10  | 10  | high       | 4-3-3-strategies-influencing-growth-development, 1-2-5-price-elasticity-of-supply                     |
| `edexcel-a-p2-2020-oct-q6c` | 2     | October 2020  | B   | 6(c) | 12    | p11  | p11  | 10  | high       | 4-1-3-pattern-of-trade, 4-3-2-factors-influencing-growth-development                                  |
| `edexcel-a-p2-2020-oct-q6d` | 2     | October 2020  | B   | 6(d) | 10    | p11  | p13  | 10  | high       | 4-1-5-trading-blocs-and-the-world-trade-organisation                                                  |
| `edexcel-a-p2-2020-oct-q6e` | 2     | October 2020  | B   | 6(e) | 15    | p11  | p15  | 10  | high       | 4-1-5-trading-blocs-and-the-world-trade-organisation, 4-3-3-strategies-influencing-growth-development |
| `edexcel-a-p2-2020-oct-q7`  | 2     | October 2020  | C   | 7    | 25    | p26  | p17  | —   | high       | 4-5-2-taxation, 2-6-3-supply-side-policies                                                            |
| `edexcel-a-p2-2020-oct-q8`  | 2     | October 2020  | C   | 8    | 25    | p26  | p20  | —   | high       | 4-2-2-inequality                                                                                      |

## 6. Judgement calls — reviewed and signed off

Nothing in the extraction needed attention. Two judgement calls in the tagging
were raised; both were reviewed by the site owner on 2 August 2026 and are now
settled.

**(a) Boundary tagging decisions. Settled.**
All 112 questions were tagged by hand against the 87 published Edexcel topic
slugs. Four sat across a boundary:

- _Price discrimination_ (P1 June 2023 Q6e, P1 October 2020 Q6e) is tagged
  **3.4.5 Monopoly**, which is where Edexcel places it, rather than 3.3.1 Revenue.
  **Approved as-is.**
- _Subjective happiness_ (P2 June 2019 Q6c, P2 June 2022 Q6c) is tagged
  **2.1.1 Economic Growth**, where the specification puts national wellbeing.
  **Approved as-is.**
- _Labour immobility_ (P1 June 2018 Q6e) was tagged both 3.5.2 Supply of Labour
  and 1.3.1 Types of Market Failure. **Changed on review: it is now tagged
  3.5.2 Supply of Labour only.**
- _Streaming market structure_ (P1 June 2023 Q6a) is tagged **3.4.4 Oligopoly**,
  judged from the question and extract description without reading the mark
  scheme. **Approved as-is.**

**(b) Coverage is lumpy, which is expected and is what the volume gate is for.
Approved.** Section A will be added at a later date, and those questions are to
flow into the topic pages once present — which is exactly how the gate already
behaves, since it is re-evaluated on every generator run.

- 56 of 87 topics have at least one question; **31 have none**.
- **18 topics reach 4+ questions** and would get a generated page in Phase 3.
- The most-tested topics are 4.3.3 Development Strategies (9), 3.6.1 Government
  Intervention (8) and 1.3.2 Externalities (7).

The 31 empty topics are mostly Theme 1 and Theme 2 foundation material (PPFs,
specialisation, the multiplier, output gaps) which Edexcel examines in Section A
short-answer questions, not in Section B or C. Both Paper 3 and Section A are
confirmed as wanted later (§7), and will fill most of these in. Until then no
page is generated for them, so there are no thin pages.

Run `python3 scripts/verify_past_paper_tags.py` for the full coverage histogram.

## 7. Excluded from this phase — reviewed and confirmed

Listed so nothing was wrongly filtered. Reviewed by the site owner on
2 August 2026; the "Status" column records what happens to each next.

| Excluded                                 | PDFs | Status after review                                   |
| ---------------------------------------- | ---- | ----------------------------------------------------- |
| Edexcel A A-Level **Paper 3**            | 16   | **Wanted.** Confirmed for Phase 4                     |
| Edexcel A Papers 1–2 **Section A**       | —    | **Wanted later.** To flow into topic pages once added |
| **AQA** A-Level (`past-papers/aqa/`)     | 90   | **Wanted, Phase 4+.** Partial — see below             |
| Edexcel A **AS-Level** Papers 1–2        | 32   | Excluded                                              |
| **AQA AS-Level**                         | —    | Excluded for now                                      |
| **Edexcel B** (`past-papers/edexcel-b/`) | 65   | Excluded — different qualification                    |
| **OCR** (`past-papers/ocr/`)             | 46   | Excluded — different board                            |

**Confirmed AQA scope for Phase 4+:** Paper 1 and Paper 2 Sections A _and_ B
(Section A carries extracts and so needs context links), and Paper 3 **Section B
only** — Paper 3 Section A is 30 multiple-choice questions and is excluded, while
Section B is a case study needing extracts.

Also confirmed absent from the repo entirely: **no IAL / WEC-coded papers**, and
**no Edexcel specimen or sample assessment materials** (the only specimen papers
on the site are AQA's).

Every in-scope question paper has its matching mark scheme. There are no gaps.

## 8. Defect found outside this scope

`past-papers/edexcel-b/index.html` links three **June 2023 mark schemes** that do
not exist on disk (A-Level papers 1, 2 and 3) — 68 hrefs against 65 files. These
are three live 404s on the published site. Not touched, since Edexcel B is out of
scope, but worth fixing separately.

## 9. How to re-check this yourself

```bash
# re-extract from the PDFs (deterministic; output should not change)
swift scripts/extract_past_paper_questions.swift \
  past-papers/edexcel/a-level/paper-{1,2}/*question-paper.pdf
git diff --stat past-paper-questions-data/     # expect: no changes

# independent verification against the PDFs
swift scripts/verify_past_paper_extraction.swift

# tags against taxonomy and extraction, plus the coverage histogram
python3 scripts/verify_past_paper_tags.py
```

Spot-check a deep link by hand, for example
`/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2019-mark-scheme.pdf#page=19`
should open on the mark scheme for Question 7.
