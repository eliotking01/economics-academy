# Past Paper Question Bank — Progress

Live state file. A new session with no conversation history should be able to
resume from this file, `CLAUDE.md` and `git log` alone.

**Branch:** `feature/question-bank`, based on `main` at `6bdc559`.
**Last updated:** 2 August 2026.

---

## Current position

**Phase 1 (data extraction) — complete, reviewed and signed off 2 August 2026.**
One tagging change was requested and applied (labour immobility, P1 June 2018
Q6e, is now 3.5.2 Supply of Labour only). Future scope was confirmed at the same
time and is recorded under "Still to do".

**Phase 2 (master search page) — complete, not yet reviewed.**
`/past-paper-questions/` exists and works: 112 questions, live search, six
filters, three sorts, verified deep links into the hosted mark schemes.

**Next action: the site owner opens `/past-paper-questions/` in Live Server**
and checks it looks and behaves right — this is the first part of the project
with a visual surface, and nothing here has been seen in a browser yet. Then
Phase 3, which generates the theme and topic pages.

Two shared-file changes are ready but **deliberately not applied**, because they
need the diff approved first: the nav entry, and the `sitemap.xml` block.

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

| Decision                      | Choice                                                                               | Why                                                                                                                                                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Phase 1 scope                 | Section B **and** Section C, Papers 1–2, 2017–2024                                   | Section C alone is only 32 questions — too few to support topic pages without them being thin                                                                                                          |
| Section B extracts            | Not reproduced; each question links to the extract page in the hosted question paper | Owner's call. Avoids reproducing several pages of stimulus per question                                                                                                                                |
| Topic pages                   | **Volume-gated**: generated only where a topic has ≥ 4 questions                     | 87 topics against 112 questions would mean most pages carried 0–1 questions. Thin/doorway content is an SEO liability, not a win. Gate is re-evaluated on every run, so pages appear as the bank grows |
| Branch base                   | `main`                                                                               | The owner merged `feature/topic-questions` first, so `main` now has `questions-data/` and `build_questions.py`                                                                                         |
| URL root                      | `/past-paper-questions/`                                                             | Matches search intent; distinct from `/past-papers/` (PDFs) and `/practice-questions/` (original MCQs)                                                                                                 |
| Topic slugs                   | Reuse the 87 existing notes slugs verbatim, spec code and all                        | No new taxonomy means no rename risk. Bare keyword slugs collide — `balance-of-payments` is both 2.1.4 and 4.1.7                                                                                       |
| PDF tooling                   | Swift + PDFKit                                                                       | No Python PDF library, no `requirements.txt`, no venv in this repo; macOS ships PDFKit. Precedent set in `QUESTIONS_PROGRESS.md` §7                                                                    |
| Tags separate from extraction | `tags.json` keyed by question id                                                     | Re-running the extractor must never destroy hand-tagging                                                                                                                                               |
| Progress file name            | `PAST-PAPERS-PROGRESS.md`, not `PROGRESS.md`                                         | Matches the existing `PROJECT-LOG.md` / `QUESTIONS_PROGRESS.md` convention                                                                                                                             |
| `CLAUDE.md`                   | Extended with one section, **not** overwritten                                       | The existing file is good and was already the project's memory                                                                                                                                         |
| Fuzzy search                  | Custom bounded-edit-distance index, **not** Fuse.js                                  | Fuse v7 ships only `.cjs` and `.mjs`, so it would force an ES module into a site whose seven scripts are all classic — and this repo has no JS dependencies. The plan permitted this alternative       |
| Generated page formatting     | The generator runs `npx prettier@3.9.6` over its own output                          | Otherwise every run undoes the repo's formatting and the file churns in `git diff` forever. Generating twice is now byte-identical                                                                     |
| Topic page links              | `hasPage` means "exists on disk", not "is warranted"                                 | The master page cannot ship links to Phase 3 pages that do not exist yet, and the links switch on by themselves once generated. No flag to remember                                                    |

---

## Files created

Nothing pre-existing has been modified except `CLAUDE.md`, which gained one
section and two `See also` lines.

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
- **Nothing has been looked at in a browser yet.** This is the gap in Phase 2's
  verification and the reason the next action is a Live Server check.

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

## Open questions awaiting the owner

1. **Nav entry.** A top-level "Past Paper Questions" item needs an edit to
   `templates/header.html` _and_ a new entry in the `pageMap` array in
   `js/components/inject-templates.js` — without the second, nothing highlights.
   Diff to be shown before applying.
2. **Internal links** from notes pages to their topic's questions page, following
   the additive-only pattern of `scripts/append_questions_link.py`.
3. **Copyright.** The bank reproduces Pearson question text verbatim. The site
   already hosts all 281 papers in full, so this is not a new category of
   exposure, but it is a wider one. Raised; owner's call.
4. **Any push to `main`** — it auto-publishes to economicsacademy.co.uk.

---

## Flagged issues

- **Three live 404s, outside this project's scope.**
  `past-papers/edexcel-b/index.html` links three June 2023 mark schemes that are
  not on disk (A-Level papers 1, 2, 3) — 68 hrefs against 65 files.
- **Untracked file in the working tree:** `js/components/quiz 2.js`, which looks
  like a Finder duplicate. Not created by this work and not touched.
- The 2024 Paper 1 mark scheme cover carries a Pearson typo, "Market and
  Business Behaviour". The extractor uses the correct name.

---

## Still to do

**Phase 3 — generated pages.** `scripts/build_past_paper_questions.py` renders 4
theme pages plus every gated topic page as crawlable HTML, each embedding the
search component pre-filtered, with breadcrumbs, unique title/meta, related-topic
links and a link back to the master page. Sitemap block written between
`<!-- Past Paper Questions -->` markers, matching the practice-questions
convention. `Quiz`/`Question` schema.org markup implies an answer the site
deliberately does not host, so `LearningResource` is the likelier fit.

**Phase 4+ — scope confirmed by the owner 2 August 2026; build after Phase 3.**
The schema already carries `context`, a string `questionNumber`,
`parentQuestion`, `choiceGroup` and a free-string `section`, so none of the
below needs a migration.

_In scope, in this order:_

1. **Edexcel A Paper 3** (16 PDFs, `past-papers/edexcel/a-level/paper-3/`).
   Confirmed wanted. Wholly context-based, so every question needs the
   `context` extract link that Section B already uses.
2. **Edexcel A Papers 1–2 Section A.** Not yet scheduled, but confirmed wanted
   at a later date. Once added, those questions must flow into the topic pages —
   which needs no new work, because the volume gate is re-evaluated on every
   generator run, so topics currently below the gate will gain pages
   automatically.
3. **AQA A-Level** (`past-papers/aqa/a-level/`). Include:
   - **Paper 1** — Section A _and_ Section B. **Section A carries extracts**, so
     it needs `context` links.
   - **Paper 2** — Section A _and_ Section B, same extract handling.
   - **Paper 3** — **Section B only.** Section A is 30 multiple-choice questions
     and is **excluded**. Section B is a case study and **needs extracts**.
   - **AQA AS-Level is excluded for now.**
   - AQA specimen papers (10 PDFs) remain out of scope unless asked for.

_Still excluded:_ Edexcel A AS-Level, Edexcel B, OCR.

Note for whoever picks this up: AQA mark tariffs and section meanings differ
from Edexcel's, which is why `section` is a free string and `marks` a plain
integer. Do not turn either into an enum.

---

## How to sanity-check the current state

```bash
git log --oneline main..feature/question-bank

# regenerate everything; nothing should change
python3 scripts/build_past_paper_taxonomy.py
swift scripts/extract_past_paper_questions.swift \
  past-papers/edexcel/a-level/paper-{1,2}/*question-paper.pdf
python3 scripts/build_past_paper_questions.py
git diff --stat past-paper-questions-data/ past-paper-questions/   # expect: nothing

# verify
swift scripts/verify_past_paper_extraction.swift   # 112 checked, all passed
python3 scripts/verify_past_paper_tags.py          # all tag checks passed
node scripts/test_question_search.js               # every check passed
python3 scripts/verify_html.py past-paper-questions
python3 scripts/verify_links.py past-paper-questions   # 0 broken

# prove no existing page was touched
git diff main -- revision-notes/ templates/ js/ css/ past-papers/ sitemap.xml \
  | grep '^-[^-]'
```

The last command must print nothing.

Then open `/past-paper-questions/` in Live Server and check: results appear,
typing filters them, each filter narrows the count, "Clear all" resets, a mark
scheme link opens the right page, and the layout holds on a narrow viewport.
