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

**Phase 2 (master search page) — complete, reviewed 2 August 2026.** Three bugs
were found on review and all three are fixed: source-citation URLs polluting the
search index, the show-more counter running negative, and the `#page=` fragment
(see "Flagged issues" — not fixable from our side). The nav entry was approved
and applied at the same time: a child of the existing **Past Papers** dropdown,
not a ninth top-level item.

**Phase 3 (theme and topic pages) — complete, not yet reviewed.** 22 new pages
and the sitemap block.

**Next action: the site owner reviews the generated pages in Live Server** —
`/past-paper-questions/theme-3/` and `/past-paper-questions/3-4-5-monopoly/` are
representative. Then Phase 4, whose scope is already confirmed under
"Still to do".

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
| Topic page links              | `hasPage` == clears the gate                                                         | In Phase 2 this was a disk probe so the master page could not link to pages that did not exist yet. Phase 3 generates them in the same run, so the gate is the authority again                         |
| Structured data               | `CollectionPage` + `BreadcrumbList`, **not** `Quiz`/`Question`                       | Quiz markup expects an `acceptedAnswer` or `suggestedAnswer`. This bank deliberately does not host answers — it links to Pearson's schemes — so declaring `Question` earns no rich result and misleads |
| Static vs rendered cards      | Both renderers emit identical markup, enforced by test                               | Topic pages ship questions as real HTML for crawlers, then the component re-renders from JSON. If the two drifted, enabling JavaScript would silently change the page                                  |

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

**Still open from the original brief, neither yet requested:**

- **Internal links from the notes pages** into their topic's questions page,
  following the additive-only pattern of `scripts/append_questions_link.py`.
  Needs the owner's approval since it touches 87 existing pages.
- **Per-question pages.** Deliberately not built. The stable question ids are
  ready to become URLs (`edexcel-a-p1-2019-jun-q7`) if that is ever wanted.

**Phase 4+ — scope confirmed by the owner 2 August 2026.**
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
