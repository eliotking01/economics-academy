# Past Paper Question Bank — Progress

Live state file. A new session with no conversation history should be able to
resume from this file, `CLAUDE.md` and `git log` alone.

**Branch:** `feature/question-bank-as-level`, based on `main` at `523888d`.
**Last updated:** 7 August 2026.

> `feature/question-bank` was merged to `main` in PR #7 and is fully contained
> in it — `git log main..feature/question-bank` is empty. Everything described
> below as "Phase 1–4" is live on the site.

---

## Session of 7 August 2026 — audit, cleanup, AS Level

Three tasks, in order: (1) audit the PDF page-link code, (2) strip source
attributions from question text, (3) add Edexcel AS (8EC0) Sections B and C.

### Task 1 — PDF page-link audit: PASS, no defect found

Inspection only, no code changed. Every check below was run against the shipped
files and the 281 hosted PDFs.

| Check | Result |
| --- | --- |
| `#page=N` present on all three link types | Pass — question paper, extract and mark scheme all carry it |
| Fragment not URL-encoded | Pass — 0 occurrences of `%23page` anywhere in the generated output |
| `download` attribute | Pass — none in the repo |
| Same-origin | Pass — every href is root-relative `/past-papers/…` |
| JS intercepting the click | Pass — nothing binds a handler to card links |
| Stored numbers are physical 1-based indices | Pass — verified by content on all 440 questions |
| Any page number out of range | Pass — 0 of 1,229 references exceed their PDF's page count |
| Fragment syntax consistent across link types | Pass — one shared expression per renderer |
| Question paper / mark scheme / extract share a code path | Pass — one function each side, no drift |
| Python and JS renderers agree | Pass — enforced by `test_question_search.js` |
| PDFs force page 1 via `/OpenAction` | Pass — 0 of 281 PDFs carry one |

Also established, because it bears on the symptom: printed folio numbers and
physical indices coincide in these papers (the cover is physical 1 and prints no
number), so a printed-vs-physical mix-up could not produce the symptom even in
principle. 151 of the 281 PDFs are not linearised, which delays first paint but
does not drop the fragment.

Conclusion reported to the owner: the code is correct, and the Chrome-on-macOS
behaviour is environmental. The most likely cause is Chrome's
**"Download PDFs instead of automatically opening them in Chrome"** setting,
which bypasses the built-in viewer entirely and so ignores `#page=`.

### Task 2 — source attributions moved out of question text: DONE

Approved by the owner on the dry run, then applied. **20 questions, 11 files,
all Edexcel A Section C.** AQA had none: its extractor already dropped them.

Four variants existed, all bracketed and all carrying a URL — `(Source adapted
from: <URL>)` ×12, `(Source: adapted from <URL>)` ×5, `(Source: <URL>)` ×2,
`(Sources: adapted from <URL> and <URL>)` ×1. There is **no** bare `Source: X`
and no unbracketed `Adapted from X`. 19 sat mid-text between the stimulus and
the instruction; 1 was trailing. All 20 removals are pure deletions — verified
mechanically, not by eye — so no orphaned bracket, dangling punctuation or
doubled space arose to clean up.

The text is preserved in a new `sourceAttribution` field on the question.
`build_past_paper_questions.py` builds its payload from an explicit whitelist,
so the field never reaches `questions.json`, the card or the search index; a
comment there records that as a decision rather than an accident.

**The extractors are the fix, not the script.** `stripAttribution()` in
`extract_past_paper_questions.swift` does it at source and emits the field, so
re-extraction cannot reintroduce a citation and the AS papers never carry one.
`scripts/strip_source_attributions.py` remains as a re-runnable safety net over
data already on disk; with the extractor fixed it reports **0 changes**, and
that agreement is the test.

The script is **format-preserving on purpose**. A first version round-tripped
through `json.dumps` and would have reformatted all 48 files — both extractors
hand-write their JSON as raw UTF-8 with `context`/`questionPaper`/`markScheme`
on one line each, so the next extractor run would have reverted it and
`git diff` after regeneration would never have been empty again. Caught by a
round-trip test before anything was written.

Also fixed, at the owner's request: `aqa-p2-2018-jun-q3` read `self- correcting`
where the PDF broke the word across a line. `rejoin_hyphenation()` in the AQA
extractor repairs it, guarded against the suspended hyphen — `short- and
long-run`, `pre- or post-tax` — where the space is correct. One character
changed across 248 AQA questions.

Other artefacts, **reported and deliberately not touched**: none found. No
`(Total for Question N = X marks)`, no `TOTAL FOR SECTION`, no `Turn over`, no
copyright lines, no dot leaders, no page-footer codes, no doubled spaces, no
stray newlines, no unbalanced brackets. The extraction was cleaner than
expected; the hyphenation break was the only other defect in 440 questions.

Verified after re-extraction: `verify_past_paper_extraction.swift` 192 checked,
all passed; `verify_past_paper_tags.py` all tag checks passed. Page
regeneration is deliberately deferred to the end of Task 3 so the site rebuilds
once.

### Task 3b — AS extraction and integration: DONE

**112 questions from 16 papers, all high confidence, all page mappings
verified.** Full QA in `_working/question-bank/as-extraction-qa.md`.

The bank is now **552 questions from 64 papers**: Edexcel A Level 192, Edexcel
AS 112, AQA 248. 90 generated pages, up from 75. **15 topics reach the volume
gate only because AS is included** and get a page for the first time — the
Theme 1–2 foundation topics the original phase noted as empty because Edexcel
tests them in Section A at A Level. Topics with no question fall 27 → 15.

What changed, and why:

- `extract_past_paper_questions.swift` handles both qualifications. `parseMeta`
  reads the level off the path; `extractParts` takes the run of part letters so
  AS can be (a)–(g) while the A Level stays (a)–(e); Section B ends at the end
  of the paper for AS, since there is no Section C to stop at.
- **Two data directories**, `edexcel-a` and `edexcel-a-as`. Both qualifications
  have a Paper 1 in the same series, so one directory would mean colliding
  filenames. `paper_index` in the build is now keyed on level too, for the same
  reason.
- A **qualification badge on every card**, second in the row, in the static HTML
  and not applied by script. Both renderers changed together and
  `test_question_search.js` confirms they still agree across all 552.
- A **`Qualification` filter**, defaulting to both, per the owner's decision.
- The **board record's `qualification` was silently wrong** once Edexcel spanned
  two qualifications. The badge and the search haystack now read the per-paper
  value.
- **A contrast failure was caught before it shipped.** The first AS badge colour
  reached only 3.25:1 against white at 0.68em bold — it looked fine. Replaced
  with `#875300` at 6.43:1.
- Two questions carried a **stray trailing full stop** left by the answer-line
  leaders; fixed in `normalise()`, end-of-string only.

Verified: 304 Edexcel questions re-checked by the independent verifier, all
passed; all tag checks passed; 552 records indexed with every search check
passing; 90 files well-formed; 11,678 internal refs and 0 broken; two build runs
byte-identical; Prettier clean; sitemap 461 URLs with no duplicates.

`tags.json` grew 440 → 552 entries, **793 insertions and 0 deletions**. No
existing page prose was altered anywhere: the only edit to a hand-written page
is the question count between the markers in `past-papers/index.html`, which the
build owns.

### Task 3a — Edexcel AS (8EC0) inventory and structure: signed off 7 August 2026

**Inventory.** 16 sittings, Papers 1 and 2, **every one a complete QP + MS pair**,
32 files. June 2016, 2017, 2018, 2019, October 2020, June 2022, 2023, 2024. No
June 2020 or June 2021 (COVID), and **no November 2021** — the A Level has that
sitting, AS does not. Nothing is missing its pair.

**8EC0 has no Section C.** Verified from all 16 PDFs, not from memory. The paper
is Section A (Questions 1–5, 20 marks) and Section B (Question 6, 60 marks),
total 80. So the instruction "Sections B and C" has no referent on this
qualification, and the concrete meaning proposed is **all of Section B**.

Section B is identical in shape across all 16 papers: **Q6(a)–(g)**, (a)–(e)
compulsory then **(f) OR (g)**. Tariffs: (e) is always 15, (f) and (g) always
20; (a)–(d) permute 4/5/6/10 (Paper 1 opens on 5, Paper 2 on 4) and always sum
to 25. **112 questions**, 16 papers × 7 parts.

AS Section B therefore **merges what the A Level splits**: (a)–(e) is the
data-response that 9EC0 calls Section B, and (f)/(g) is the extended essay that
9EC0 calls Section C — except that AS keeps it inside Section B, attached to the
same extract block.

**No Paper 3.** AS is two papers. Paper names differ from the A Level and are
taken from the covers: Paper 1 *Introduction to Markets and Market Failure*,
Paper 2 *The UK Economy – Performance and Policies*.

**Duplicates: none.** The premise that Edexcel reuses questions between 8EC0 and
9EC0 is **not supported by the data**. Across 112 AS × 192 A Level comparisons:
0 exact, 0 near (≥0.90), 0 strong (≥0.80). The maximum was 0.754, and every
match at that level is a shared formulaic stem — *"With reference to Extract A,
assess the likely…"* — over different economics. Confirmed a second way, by rare
content-word overlap: the highest Jaccard was 0.556 and the shared words were
all generic (*aggregate, demand, supply*). Six AS-internal pairs scored above
0.85; all are the stem *"With reference to Figure 1, explain the term ‘X’"* with
a different X each year. **Nothing to collapse.** A policy is still recorded so
the question does not have to be reopened.

**Extracts.** AS follows the existing policy unchanged: the extract block is not
reproduced, and each question links to its page in the hosted question paper.
One AS-specific difference, and it is the opposite of what the A Level does:
9EC0 Section C carries its own short stimulus and no extract link (`ctxPage`
null), whereas **AS (f)/(g) sit under the Q6 extract block like every other
part**, so all seven AS parts get a `ctxPage`.

**Taxonomy: no additions needed.** AS covers Themes 1 and 2 only, and both are
already in the 87-topic taxonomy. No new slugs, so no permanent-URL risk. This
should also lift a number of the 31 currently-empty Theme 1–2 topics over the
volume gate of 4, giving them topic pages for the first time.

**Filters and payload.** The marks filter is derived from the data rather than
hard-coded, so the new 4, 6 and 20 tariffs appear by themselves. `questions.json`
goes from 353 KB / 51 KB gzipped to roughly 443 KB / 64 KB. One thing that does
need changing: `qualification` currently sits on the **board** record as a single
string, and Edexcel would now span two qualifications — the badge must read the
per-paper `qualification`, which is already there and already correct.

---

## Current position

**Phase 1 (data extraction) — complete, reviewed and signed off 2 August 2026.**
One tagging change was requested and applied (labour immobility, P1 June 2018
Q6e, is now 3.5.2 Supply of Labour only). Future scope was confirmed at the same
time and is recorded under "Still to do".

**Phase 2 (master search page) — complete, reviewed 2 August 2026.** Three bugs
were found on review and all three are fixed: source-citation URLs polluting the
search index, the show-more counter running negative, and the `#page=` fragment
(see "Flagged issues" — not fixable from our side). The nav entry was approved
and applied at the same time: a child of the existing **Past Papers** dropdown,
not a ninth top-level item.

**Phase 3 (theme and topic pages) — complete, reviewed 2 August 2026.** Three
follow-ups were requested and delivered: notes-page links, a question paper link
on every card, and an explanation of per-question pages (see "Decisions").

**Phase 4 — complete.** Both boards are extracted, tagged and published.

The bank is **440 questions from 48 papers**: Edexcel A 192 (Papers 1-3,
Sections B and C) and AQA 248 (Papers 1-2 Sections A and B, Paper 3 Section B).
75 generated pages, 66 of them topic pages, and 139 notes pages linking in.

`/past-papers/` now carries a CTA into the bank, between the board buttons and
the resources row.

**Next action: the site owner reviews it in Live Server**, then decides about
merging to `main` — which publishes. Nothing is pushed.

---

## What this project is

A searchable bank of real Edexcel A Level Economics A (9EC0) exam questions,
extracted from the PDFs the site already hosts, at `/past-paper-questions/`.
Two tiers: a master search page over the whole bank, plus a statically generated
page per topic carrying the same search component pre-filtered.

Mark schemes are **not** extracted. Each question deep-links to the site's own
hosted mark-scheme PDF at the exact page.

Approved plan: `/Users/eliotking/.claude/plans/claude-code-prompt-dreamy-turing.md`
(scratch — the durable record is this file).

---

## Decisions made, and why

| Decision                      | Choice                                                                               | Why                                                                                                                                                                                                     |
| ----------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phase 1 scope                 | Section B **and** Section C, Papers 1–2, 2017–2024                                   | Section C alone is only 32 questions — too few to support topic pages without them being thin                                                                                                           |
| Section B extracts            | Not reproduced; each question links to the extract page in the hosted question paper | Owner's call. Avoids reproducing several pages of stimulus per question                                                                                                                                 |
| Topic pages                   | **Volume-gated**: generated only where a topic has ≥ 4 questions                     | 87 topics against 112 questions would mean most pages carried 0–1 questions. Thin/doorway content is an SEO liability, not a win. Gate is re-evaluated on every run, so pages appear as the bank grows  |
| Branch base                   | `main`                                                                               | The owner merged `feature/topic-questions` first, so `main` now has `questions-data/` and `build_questions.py`                                                                                          |
| URL root                      | `/past-paper-questions/`                                                             | Matches search intent; distinct from `/past-papers/` (PDFs) and `/practice-questions/` (original MCQs)                                                                                                  |
| Topic slugs                   | Reuse the 87 existing notes slugs verbatim, spec code and all                        | No new taxonomy means no rename risk. Bare keyword slugs collide — `balance-of-payments` is both 2.1.4 and 4.1.7                                                                                        |
| PDF tooling                   | Swift + PDFKit                                                                       | No Python PDF library, no `requirements.txt`, no venv in this repo; macOS ships PDFKit. Precedent set in `QUESTIONS_PROGRESS.md` §7                                                                     |
| Tags separate from extraction | `tags.json` keyed by question id                                                     | Re-running the extractor must never destroy hand-tagging                                                                                                                                                |
| Progress file name            | `PAST-PAPERS-PROGRESS.md`, not `PROGRESS.md`                                         | Matches the existing `PROJECT-LOG.md` / `QUESTIONS_PROGRESS.md` convention                                                                                                                              |
| `CLAUDE.md`                   | Extended with one section, **not** overwritten                                       | The existing file is good and was already the project's memory                                                                                                                                          |
| AQA extraction                | A second extractor, `extract_aqa_questions.py`, using pdfplumber                     | PDFKit returns AQA's pages in a scrambled reading order. pdfplumber reads the number cells by coordinate, which is exact rather than heuristic. Repo's first Python dependency, authoring-time only     |
| Board separation              | `/past-paper-questions/<board>/...`, boards never mixed on a page                    | 37 spec codes mean different things on each board, and 11 topics share a title. A flat namespace would show two numbering systems and split search intent across duplicate pages                        |
| HTML escaping                 | Hand-rolled `e()` in the generator, **not** `html.escape`                            | `html.escape` turns an apostrophe into `&#x27;` and the JavaScript renderer does not, so a question containing one rendered differently once JavaScript ran. The two must agree character for character |
| Hub CTA count                 | Marker comments in `past-papers/index.html`, refreshed by the build                  | A hard-coded figure goes stale the moment the bank grows and nothing would flag it. Only the digits are rewritten, so the surrounding copy stays hand-written                                           |
| Fuzzy search                  | Custom bounded-edit-distance index, **not** Fuse.js                                  | Fuse v7 ships only `.cjs` and `.mjs`, so it would force an ES module into a site whose seven scripts are all classic — and this repo has no JS dependencies. The plan permitted this alternative        |
| Generated page formatting     | The generator runs `npx prettier@3.9.6` over its own output                          | Otherwise every run undoes the repo's formatting and the file churns in `git diff` forever. Generating twice is now byte-identical                                                                      |
| Topic page links              | `hasPage` == clears the gate                                                         | In Phase 2 this was a disk probe so the master page could not link to pages that did not exist yet. Phase 3 generates them in the same run, so the gate is the authority again                          |
| Notes-page links              | All 56 tagged topics, not just the 18 with pages                                     | The 38 without a page link to `?topic=<slug>` on the master search, so every tagged topic has a useful destination                                                                                      |
| Per-question pages            | Not built                                                                            | One paragraph and three links each is thin content, and 112 near-identical pages risks the section's quality signals. Card ids already work as anchors                                                  |
| Structured data               | `CollectionPage` + `BreadcrumbList`, **not** `Quiz`/`Question`                       | Quiz markup expects an `acceptedAnswer` or `suggestedAnswer`. This bank deliberately does not host answers — it links to Pearson's schemes — so declaring `Question` earns no rich result and misleads  |
| Static vs rendered cards      | Both renderers emit identical markup, enforced by test                               | Topic pages ship questions as real HTML for crawlers, then the component re-renders from JSON. If the two drifted, enabling JavaScript would silently change the page                                   |

---

## Files created

Four pre-existing files have been modified, all additively, none in their
prose: `CLAUDE.md` (one section, two `See also` lines), `templates/header.html`
(one nav `<li>`), `js/components/inject-templates.js` (one `pageMap` entry) and
`sitemap.xml` (a new block between markers, 25 lines added, none removed).
`verify_text_integrity.py` confirms 0 visible-text differences across all 176
pages, and `verify_markup_integrity.py --strict` confirms 0 losses.

| File                                         | Kind                | Notes                                                                                                                |
| -------------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `scripts/build_past_paper_taxonomy.py`       | generator           | Builds `taxonomy.json` from `questions-data/` + `UNITS` in `build_questions.py`. `--check` validates without writing |
| `scripts/extract_past_paper_questions.swift` | generator           | PDF → per-paper JSON. Deterministic. Never invents text                                                              |
| `scripts/verify_past_paper_extraction.swift` | verifier            | Independent re-check against the PDFs, deliberately not sharing the extractor's matching logic                       |
| `scripts/verify_past_paper_tags.py`          | verifier            | Tags vs taxonomy vs extraction, plus the topic coverage histogram                                                    |
| `past-paper-questions-data/taxonomy.json`    | data (generated)    | 4 themes, 21 units, 87 topics                                                                                        |
| `past-paper-questions-data/edexcel-a/*.json` | data (generated)    | 16 files, 7 questions each                                                                                           |
| `past-paper-questions-data/tags.json`        | data (hand-written) | 112 entries: topics + keywords                                                                                       |
| `extraction-qa-report.md`                    | report              | Phase 1 QA. Reviewed and signed off 2 August 2026                                                                    |

Phase 2:

| File                                    | Kind             | Notes                                                                                      |
| --------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------ |
| `scripts/build_past_paper_questions.py` | generator        | Joins extraction + tags + taxonomy, writes the index and the master page. Grows in Phase 3 |
| `js/components/question-search.js`      | component        | The reusable search/filter/results UI. Takes an optional pre-filter                        |
| `css/pages/past-paper-questions.css`    | stylesheet       | Every rule scoped under `.past-paper-questions-page`                                       |
| `scripts/test_question_search.js`       | test             | `node scripts/test_question_search.js`. Runs against the shipped component, not a copy     |
| `past-paper-questions/index.html`       | page (generated) | Do not hand-edit; re-run the generator                                                     |
| `past-paper-questions/questions.json`   | data (generated) | 88 KB, 16 KB gzipped                                                                       |

---

## Verified done

- 112 questions extracted from 16 papers: 80 Section B, 32 Section C.
- Mark tariffs exactly as expected — 16 each of 5/8/10/12/15, and 32 × 25.
- **All 112 at high confidence. All 112 mark-scheme page mappings verified**, by
  a second pass that does not share the extractor's matching logic. 0 failures.
- Extraction is deterministic — two runs produce byte-identical output.
- All 112 hand-tagged; every topic slug validated against the taxonomy.
- All 22 line-wrapped source URLs repaired to well-formed URLs.
- Page furniture, dot leaders and the rotated `DO NOT WRITE IN THIS AREA`
  margin text removed from all question text.

Phase 2:

- Master page generates, is well-formed, and has **0 broken links** and
  0 broken fragments.
- Generating twice is **byte-identical**, and the output passes
  `prettier@3.9.6 --check` because the generator formats its own output.
- Search tests pass against the shipped component: typo tolerance
  ("quantitive easing" finds the same set as the correct spelling), all five
  mark phrasings agree, AND semantics, ranking, deep-link construction,
  HTML escaping, and Section B/C extract-link asymmetry.
- Accessibility: all 8 form controls have matching labels, the result count is
  a polite live region, no inline styles, no `onclick`, one `h1`, controls
  hidden until the data is in.
- Reviewed in the browser 2 August 2026. Three bugs found and fixed.

Phase 3:

- 22 pages generated: 4 theme, 18 topic. Every question is real HTML in the
  page source, not injected by script.
- **The Python and JavaScript card renderers are byte-identical** across all
  112 questions, checked by `test_question_search.js`. If they ever drift,
  enabling JavaScript would silently change the page, so this is the test
  that matters most here.
- 23 pages: unique titles, descriptions and canonicals; one `h1` each; no
  inline styles; **1428 internal links, 0 broken**; prettier clean.
- All 25 generated files are **byte-identical across two generator runs**.
- Stale pages are deleted, so the output stays a pure function of the data.
- `sitemap.xml`: 23 URLs added between markers, 0 lines removed, still valid
  XML with 384 URLs and no duplicates.

Follow-ups after the Phase 3 review:

- Every card now links the **question paper** as well as the mark scheme, so
  a question can be attempted in its printed form. Section B carries three
  PDF links, Section C two.
- **All 56 tagged notes pages** link to their past paper questions. The 18
  with a page link there; the other 38 link to the master search filtered by
  `?topic=`, which the component now reads.
- Notes edits verified additive: 504 insertions, 0 deletions, 0 markup
  losses, and each page's original visible text still intact and contiguous.

Coverage: 56 of 87 topics have at least one question; **18 reach the gate of 4**
and would get a page in Phase 3. The 31 empty topics are mostly Theme 1–2
foundation material that Edexcel tests in Section A, not Section B or C.

---

## Settled

- **Boundary tagging calls** (`extraction-qa-report.md` §6(a)) — reviewed
  2 August 2026. Price discrimination, subjective happiness and streaming market
  structure approved as tagged; labour immobility changed to 3.5.2 only.
- **Coverage and the volume gate** (§6(b)) — approved.
- **Future scope** (§7) — Edexcel A Paper 3 and Section A both wanted; AQA
  wanted with a partial scope. See "Still to do".
- **Nav placement** — approved 2 August 2026 as a child of the Past Papers
  dropdown. Applied; both edits purely additive.
- **Sitemap timing** — approved to wait for Phase 3, so the whole block is
  reviewed as one diff.

## Open questions awaiting the owner

1. **Internal links** from notes pages to their topic's questions page, following
   the additive-only pattern of `scripts/append_questions_link.py`.
2. **Copyright.** The bank reproduces Pearson question text verbatim. The site
   already hosts all 281 papers in full, so this is not a new category of
   exposure, but it is a wider one. Raised; owner's call.
3. **Any push to `main`** — it auto-publishes to economicsacademy.co.uk.

---

## Flagged issues

- **AQA needed a second extractor, and now has one.** PDFKit returns AQA's
  pages in a scrambled reading order; pdfplumber reads them by coordinate.
  `scripts/extract_aqa_questions.py` is the result, and `requirements.txt` and
  `.venv/` exist for it. This is the repo's first Python dependency, approved on
  2 August 2026 on the basis that it is authoring-time only: nothing ships and
  the site is still static with no build step. Edexcel still uses Swift and
  PDFKit, which reads those papers correctly and needs no rework.

- **`#page=N` deep links are honoured by Chrome, Firefox and Edge, but not by
  Safari.** Safari's PDF viewer ignores the fragment and opens at page 1.
  Nothing is wrong on our side: the PDFs carry no `/OpenAction`, they are
  linearised, and the hrefs are correct. The only cross-browser fix is to
  render the PDFs ourselves with a vendored PDF.js (~1.4 MB), which the owner
  judged not worth it against a repo with no dependencies. **The mitigation is
  that every link also shows its page number as text** ("Mark scheme — p.19"),
  so a reader can navigate manually. Reviewed and accepted 2 August 2026.
- **Three live 404s, outside this project's scope.**
  `past-papers/edexcel-b/index.html` links three June 2023 mark schemes that are
  not on disk (A-Level papers 1, 2, 3) — 68 hrefs against 65 files.
- **Untracked file in the working tree:** `js/components/quiz 2.js`, which looks
  like a Finder duplicate. Not created by this work and not touched.
- The 2024 Paper 1 mark scheme cover carries a Pearson typo, "Market and
  Business Behaviour". The extractor uses the correct name.

---

## Still to do

**Per-question pages — considered and deliberately not built.** A URL per
question (`/past-paper-questions/edexcel-a-p1-2019-jun-q7/`), 112 pages today.
Rejected because each would carry one paragraph of Pearson's text and three
links: thin content of exactly the kind the volume gate exists to avoid, and 112
near-identical templates risks the same quality signals across the section.
Explained to the owner and left alone 2 August 2026. Every card already has its
id as a stable anchor, so `/past-paper-questions/3-4-5-monopoly/#edexcel-a-p1-2019-jun-q7`
addresses a single question today. The ids are ready if this is ever revisited.

**Nothing is outstanding in the agreed scope.** What was deliberately left out,
and would be the next thing to consider:

- **Edexcel Papers 1-2 Section A** (short-answer). Confirmed wanted "at a later
  date". Adding it needs no new mechanism: extract, tag, re-run, and the volume
  gate gives the newly-covered topics pages by itself.
- **AS-level, Edexcel B and OCR** remain out of scope.
- **AQA specimen papers** (10 PDFs) remain excluded.
- **Per-question pages** were considered and rejected; see "Decisions".

---

## How to sanity-check the current state

```bash
git log --oneline main..feature/question-bank

# regenerate everything; nothing should change
python3 scripts/build_past_paper_taxonomy.py
swift scripts/extract_past_paper_questions.swift \
  past-papers/edexcel/a-level/paper-{1,2}/*question-paper.pdf
python3 scripts/build_past_paper_questions.py
git diff --stat past-paper-questions-data/ past-paper-questions/ sitemap.xml
# expect: nothing, unless it is a different calendar day, in which case the
# sitemap block is rewritten with a fresh lastmod. Same caveat as the
# practice-questions block.

# verify
swift scripts/verify_past_paper_extraction.swift   # 112 checked, all passed
python3 scripts/verify_past_paper_tags.py          # all tag checks passed
node scripts/test_question_search.js               # every check passed,
                                                   # including Python vs JS cards
python3 scripts/verify_html.py past-paper-questions    # 23 files, 0 errors
python3 scripts/verify_links.py past-paper-questions   # 1428 refs, 0 broken

# prove no existing page was touched
git diff main -- revision-notes/ templates/ js/ css/ past-papers/ sitemap.xml \
  | grep '^-[^-]'
```

The last command must print nothing.

Then open these in Live Server:

- `/past-paper-questions/` — results appear, typing filters them, each filter
  narrows the count, "Clear all" resets, the layout holds when narrow.
- `/past-paper-questions/theme-3/` — 38 questions, theme control hidden.
- `/past-paper-questions/3-4-5-monopoly/` — 5 questions, topic control hidden,
  related topics listed.

With JavaScript disabled the topic and theme pages must still show every
question: that is the crawlable content, and it is what the Python renderer
wrote.
