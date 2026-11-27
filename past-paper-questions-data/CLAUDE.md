# past-paper-questions-data/

Source for the searchable bank of **real exam questions** at
`/past-paper-questions/`. Excluded from publishing.

**This is the one place in the repo that reproduces exam-board question text
verbatim.** `questions-data/` is the opposite — 100% original questions that
Eliot sells. The two never share a data path.

**Mark scheme content is never extracted.** Each question deep-links to the
site's own hosted PDF at the right page.

## Scope

Widened by D67 (2026-10-24). Each change lands with the code that implements it.

| In scope | Out of scope |
| --- | --- |
| Edexcel A **A Level** (9EC0), Papers 1–3 | **An answer key for any multiple-choice card**, permanently (D67: search-only). No record carries one; the verifier fails if a field names one |
| Edexcel A Papers 1–2 **Section A written parts** (9EC0 and 8EC0), every part that prints no A–D answer boxes: 259 parts from 36 papers (counts: `build_past_paper_questions.py --check`). Brought in by D67, Phase 6; tags settled in `review/section-a-tags.md` and built 2026-11-24 | |
| **Multiple-choice questions** (D67, Phase 7): the one MCQ in each Edexcel A Papers 1–2 Section A question (9EC0 and 8EC0, 36 papers), and AQA Paper 3 Section A, Q1–Q30 (9 papers). Extracted 2026-11-25 in the shape approved in `review/phase-7-mcqs.md` and tagged the same day (`review/mcq-tags.md`). **Not yet published: staged** as the `pastPaperMcqs` family on `aqa` and `edexcel-a` in `boards.json`, so `load_bank()` drops them from every live build; `EA_PREVIEW=aqa:pastPaperMcqs,edexcel-a:pastPaperMcqs` previews them and `/launch-feature` launches them. Counts: `build_past_paper_questions.py --check` | |
| Edexcel A **AS Level** (8EC0), Papers 1–2 | **AQA AS Section B** (the data-response contexts, Q21–Q32), permanently (D71; D67 had ruled out AQA AS whole) |
| AQA A Level (7136) | OCR and AQA specimen papers, permanently (AS specimens included, D71) |
| **AQA AS Level (7135), Papers 1–2, Section A only** (D71, Phase 9): Q01–Q20, twenty 1-mark MCQs from each of the 18 non-specimen papers (June 2016–2019, November 2020, June 2022–2025), in the Phase 7 MCQ shape with no answer field. Extracted 2026-11-25 into `aqa-as/`; tags settled in `review/aqa-as-mcq-tags.md` and built 2026-11-26 (on the branch; live when it merges). Counts: `build_past_paper_questions.py --check` | |
| Edexcel B **A Level** (9EB0), Papers 1–3, and **AS Level** (8EB0), Papers 1–2, **every section**: B has no MCQs and no optional questions. Extracted into `edexcel-b/` and `edexcel-b-as/`. The build reads them by `boards.json`'s flag (`BANK_DIRS`, `paper_dirs()`). **Live** since `/launch-feature edexcel-b pastPaperBank` (2026-11-17) | |

**Edexcel B prints a lead-in above many parts** ("New Balance operates in a
competitive market. / (b) Explain…"). It is part of the question and is kept,
verbatim, at the start of `questionText`. A figure printed inside a question
(Paper 2 June 2022 1(b)) is not reproduced; its card links to the page.
**Every B A Level Paper 3 card carries a pre-release note** under the
question, approved wording from the 9EB0 specification (Phase 4 Q5). It lives
once, in `build_past_paper_questions.PAPER_NOTES`, and reaches the card
through the paper record's `note`, which no other paper carries.

**Edexcel A Papers 1–2 Section A** is five questions: 5 marks each on 9EC0,
4 on 8EC0. Every question has exactly one 1-mark MCQ beside its written
parts, so a question's cards sum to its printed total, the MCQ included (the
verifier's checks A5 and M4). A part is an MCQ **if and only if it prints A–D
answer boxes**, never by its mark — AS sets 1-mark "Define the term" parts.
Each card carries, verbatim: its question's opening stem, every lead-in
printed above it within the question, then its own text; sub-parts (i)/(ii)
stay inside their part, marks summed. Charts, tables and diagrams are not
reproduced. The context link is `type: "question"`, labelled "Question N as
printed" (approved 2026-11-24), and points at the question's first page — only
when the part is on a later page. Text printed after a part's label belongs to
that part, not the question (AS Paper 1 June 2025 Q3, Q4). Decisions in
`review/phase-6-section-a.md`; the PDF text-layer quirks the parser repairs
are listed in `extractSectionA()`.

**Multiple-choice records** (Phase 7) are the written record plus three
fields only they carry, so no written record changed by a byte: `"type":
"mcq"`; `options`, A–D as printed, or `null` when the options are diagrams,
the rows of a table, fractions, or bare letters naming points on a figure; and
`usesFigure`, true when the question prints a figure, chart or table the card
cannot show (always true when `options` is null). **There is no answer field
and there never will be** — `markScheme.page` is the page holding the key, as
for every card. An Edexcel MCQ carries its question's stem and lead-ins from
the stream, exactly as a written part does; its own sentence and its options
are read by line position (`mcqGeometry()`), because the text stream returns
options reversed, glued to the question or split by chart labels. AQA's are
read by character position (`extract_mcqs()`): its subscripts (SRAS1, E2) are
7pt glyphs set below the line, joined to their base as plain digits, the way
PDFKit returns Edexcel's "P1". Figure and table text is never reproduced.
`verify_past_paper_extraction.swift` checks every MCQ against PDFKit's plain
page text, which neither extractor reads options from (checks M1–M5).

**8EC0 has no Section C** — verified from all 16 papers, not from the
specification. Section B is `Q6(a)–(g)`: (a)–(e) compulsory then **(f) OR (g)**,
with (e) always 15 and (f)/(g) always 20. AS **merges what the A Level splits**.
Stored as `section: "B"`, as printed. Do not invent a Section C for it. Every AS
part carries a `ctxPage`, because the essay choice sits under the Q6 extracts.

**Duplicates across qualifications: keep both, never collapse.** 0 exact and 0
near-duplicates found across 112 AS × 192 A Level. If one ever appears, both stay
and both are labelled — a collapsed entry would hide that a question was set at
two different demands. Every card carries a qualification badge in the static
HTML, never applied by script, so it is never optional.

## Files

- `edexcel-a/*.json`, `edexcel-a-as/*.json`, `edexcel-b/*.json`,
  `edexcel-b-as/*.json`, `aqa/*.json`, `aqa-as/*.json` — one per paper,
  machine-written by `scripts/extract_past_paper_questions.swift` (Swift +
  PDFKit; AQA by `extract_aqa_questions.py`). **Never hand-edit.** Two
  directories per board because both qualifications have a Paper 1 in the
  same series. `verify_past_paper_extraction.swift` checks all four Edexcel
  directories against the PDFs, AQA's Paper 3 MCQs (not its written
  records) and every AQA AS record (all are MCQs).
- `ocr/` — reviewed OCR transcripts, one per question paper that has no text
  layer. Today there's one: Edexcel B AS Paper 2 June 2019, which Pearson
  publishes only as a scan. **A transcript is a checked source, not generated
  output.** Its header says what was checked against the page images and what
  was corrected. Edit it only to correct it against those images, and say so
  in the commit. The extractor fails loudly on a text-less PDF that has no
  transcript. The verifier checks the paper against its own OCR, never against
  the transcript.
- `tags.json` — topics and keywords, **hand-written**. Separate so re-extraction
  cannot destroy it.
- `taxonomy.json` — generated from the existing Edexcel topic records. The bank
  invents no taxonomy of its own.

**Source attributions are stripped at extraction**, lifted into a
`sourceAttribution` field that the build's whitelist never emits.
`scripts/strip_source_attributions.py` is the re-runnable safety net and should
report **0 changes** — that agreement is the test. It edits JSON as text on
purpose: a `json.dumps` round-trip would reformat all 64 files and break build
idempotence.

In a per-topic payload — and, since 2026-08-23, in the per-board payload at
`past-paper-questions/<board>/questions.json` that the board hub fetches
instead of the master, and since 2026-11-27 in the per-section payload at
`past-paper-questions/<board>/<section>/questions.json` that each section page
fetches (its own questions, the whole board's `topics`) — `papers` is a
**sparse list with nulls**: the search component indexes into it with `q.p`, so re-packing it
would silently re-point every question at the wrong paper. The master
`questions.json` is unchanged by either; the master page and
`build_questions.py` still read it.

**Each board hub bakes only the 20 most recent cards** (`HUB_CARDS`, held
equal to the component's `PAGE_SIZE` by `scripts/test_question_search.js`),
followed by a static note inside the results container; the section and
topic pages (counts: `build_past_paper_questions.py --check`) still bake
every card and are the no-JS list. Do not add
the rest back to the hubs: `edexcel/` was 799 KB and ~5,600 DOM nodes.
