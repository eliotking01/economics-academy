# past-paper-questions-data/

Source for the searchable bank of **real exam questions** at
`/past-paper-questions/`. Excluded from publishing.

**This is the one place in the repo that reproduces exam-board question text
verbatim.** `questions-data/` is the opposite — 100% original questions that
Eliot sells. The two never share a data path.

**Mark scheme content is never extracted.** Each question deep-links to the
site's own hosted PDF at the right page.

## Scope, permanently

| In scope | Out of scope, permanently |
| --- | --- |
| Edexcel A **A Level** (9EC0), Papers 1–3 | **Section A, every board and qualification.** Do not extract it |
| Edexcel A **AS Level** (8EC0), Papers 1–2 | **AQA AS papers.** When AQA extends, A Level only |
| AQA A Level (7136) | Edexcel B, OCR, AQA specimen papers |

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

- `edexcel-a/*.json`, `edexcel-a-as/*.json`, `aqa/*.json` — one per paper,
  machine-written by `scripts/extract_past_paper_questions.swift` (Swift +
  PDFKit). **Never hand-edit.** Two Edexcel directories because both
  qualifications have a Paper 1 in the same series.
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

In a per-topic payload, `papers` is a **sparse list with nulls**: the search
component indexes into it with `q.p`, so re-packing it would silently re-point
every question at the wrong paper.
