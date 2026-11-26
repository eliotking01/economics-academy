# Site Work — Progress

**The single record of what has been built on this site, and the entry point
for a fresh session — read this first, then CLAUDE.md.** Excluded from
publishing via `_config.yml`.

One short block per project, newest first, in the Project index at the end;
**the full write-ups moved verbatim to `_archive/PROGRESS-detail-2026-08.md`
on 2026-08-26**, same headings, same order. The exhaustive per-item wording
lists each branch carried for review live in this file's own git history,
not here.

Reorganised 2026-08-16 when the site-wide overhaul finished. **On 2026-08-20 it
absorbed `PROJECT-LOG.md`**, which covered the five older projects and is now at
`_archive/PROJECT-LOG.md`. Everything of its that was still true is in §5–§9 and
in "What remains flagged" below; most of its flagged list had quietly been
fixed without the file being updated, which is why that list is now dated and
says how each line was checked. **Collapsed 2026-08-26 in the September
clean-up**: the project sections moved to the archive file above and "What
remains flagged" moved up beside the traps.

## The overhaul at a glance

| Project | State | Merged | Merge commit |
| --- | --- | --- | --- |
| All-boards parity (D67) — Phase 9: AQA AS (7135) Section A MCQs in the past-paper bank (360 questions, 3 new pages) | live (PR #58) | 2026-11-26 | `1dadc8c2` |
| All-boards parity (D67) — Phase 7: real exam MCQs in the past-paper bank, AQA and Edexcel A (450 questions, 15 new pages) | live (PR #56) | 2026-11-25 | `ed377dc7` |
| All-boards parity (D67) — Phase 6: Edexcel A Papers 1–2 Section A written parts in the past-paper bank (259 questions, 13 new pages) | live (PR #54) | 2026-11-25 | `96439950` |
| All-boards parity (D67) — Phase 5: twin links across three boards (185 pages reworded, no new URLs) | live (PR #53) | 2026-11-24 | `f1110a8a` |
| All-boards parity (D67) — Phase 4: Edexcel B past-paper bank, launched (84 new pages, 362 questions) | live (PR #51) | 2026-11-17 | `ce9369ed` |
| All-boards parity (D67) — Phase 3: Edexcel B glossary, launched (1 new URL) | live (PR #50) | 2026-11-16 | `b7e12e77` |
| All-boards parity (D67) — Phase 2: Edexcel B flashcards, all four decks, launched (8 new URLs) | live (PR #49) | 2026-11-12 | `9576a168` |
| All-boards parity (D67) — Phase 1: Edexcel B practice questions, all 85 sets, launched (89 new URLs) | live (PR #48) | 2026-11-08 | `39403ead` |
| June 2025 papers added to the past-paper question bank | live (PR #47) | 2026-10-24 | `d96b0928` |
| June 2025 papers and the June 2023 Edexcel B mark schemes published | live (PR #46) | 2026-10-24 | `ed1d9539` |
| All-boards parity (D67) — Phase 0 groundwork: per-board feature flags, originality corpus, cold-solver, three commands | live (PR #45) | 2026-10-24 | `fafdf34f` |
| Edexcel B notes — Theme 3: 19 pages, index card, site search; Edexcel B complete, 85 pages | live (PR #44) | 2026-10-21 | `755c56e0` |
| Edexcel B notes — Theme 2: 24 pages, index card, site search | live | 2026-10-19 | `ada29e8b` |
| Edexcel B notes — Theme 4: 19 pages, index card, site search | live | 2026-10-17 | `fec344d2` |
| Edexcel B notes — Theme 1: 23 pages, index section, site search | live | 2026-10-15 | `782bafd7` |
| Calendly retired — #booking becomes an enquiry block | live | 2026-09-25 | `7aec6877` |
| Form spam hardening — endpoints rotated, Turnstile on both forms | live | 2026-09-15 | `a7a303bc` |
| Past-paper search — Board drives the board-shaped dropdowns | live | 2026-08-27 | `8fbb6ba5` |
| Tutoring page SEO pass — snippet, FAQs, anchors, Person schema | live | 2026-08-26 | `0bcac57c` |
| Notes family consistency — the two diagram galleries | live | 2026-08-25 | `0bad0c88` |
| Notes topic-page redesign — the 166 pages | live | 2026-08-25 | `53532083` |
| Question-bank page gate 4 → 2 — 46 new topic pages | live | 2026-08-24 | `fc2400a6` |
| Accessibility & progressive enhancement pass | live | 2026-08-24 | `745f9cb2` |
| Site-wide search — header box + overlay, all 463 pages | live | 2026-08-24 | `8b329f1e` |
| Topic-page tail redesign — the 166 notes pages | live | 2026-08-24 | `32c0bacb` |
| Tutoring enquiry form — board, year, enquirer, days | live | 2026-08-23 | `ab255c6` |
| Performance pass — MathJax, fonts, hubs, images | live | 2026-08-23 | `367297b` |
| Analytics consent — hard gate + cookie bar | live | 2026-08-23 | `83ae353` |
| Maintainability — one build, derived counts, tests | live | 2026-08-23 | `95cf271` |
| Hub redesign (notes + practice board hubs) | live | 2026-08-23 | `dedd5d1` |
| Previous / next topic navigation | live | 2026-08-21 | `c0a80f6` |
| GA4 conversion tracking | live | 2026-08-22 | `bb18d6d` |
| Revision notes on-page SEO | live | 2026-08-22 | `ee24918` |
| About + Contact + finishing pass | live | 2026-08-16 | `437dc7e` |
| Resource unification, Phases 1–4 | live | 2026-08-15 | `d0fdcaf`, `2295213`, `1e8dfed`, `f537312` |
| Marking page + payment journey | live | 2026-08-15 | `d4be06b` |
| Home page revamp | live | 2026-08-14 | `f53b7fe` |
| Tutoring page SEO rework | live | 2026-08-14 | `e09cdef` |
| Flashcards | live | 2026-08-15 | §5 |
| Glossary & formulae | live | 2026-08-09 | §6 |
| Past paper question bank | live | 2026-08-13 | §7 |
| Free practice questions | live | 2026-08-01 | §8 |
| Notes consistency & enrichment | live | 2026-08-01 | §9 |

Everything Eliot still has to do himself is in OWNER-TODO.md (consolidated
2026-08-16, re-consolidated 2026-08-22 when it absorbed the three 21 August
audit lists). The dated Search Console reads and their baselines are recorded
there.

## Traps every future session must know

1. **Prettier must not touch the 17 hand-written pages or the notes pages.**
   Since 2026-08-23 `.prettierignore` (generated by `bake_templates.py
   --prettierignore`) enforces that and `.prettierrc` pins the settings; the
   full reason is in the root CLAUDE.md's Prettier paragraph.
2. **Any commit changing visible wording on a published page needs one
   `Text-Change: <path>` trailer per page** in the commit message's final
   trailer block, or CI fails. Merge with a merge commit, NOT a squash, so CI
   sees the trailers across the range.
3. **Any commit touching `revision-notes/` markup**: run
   `python3 scripts/verify_markup_integrity.py <base> --strict` locally and
   declare `Markup-Change:` per page alongside `Text-Change:`.
4. Root pages are hand-written (out of page_shell scope, D34) — edit
   directly. Generated pages are never hand-edited — rerun their generator.
5. Run `python3 scripts/build_sitemap.py` AFTER committing page edits (it
   takes lastmod from git) and commit the sitemap separately.
6. Only icons already in `css/fontawesome-all.min.css` may be used (15 solid
   icons; no brand icons — LinkedIn is a text button for this reason).
7. **A bare class selector can silently lose to main.css's grid rule**
   `#main .row > div[class*="col-"]` (specificity 1,2,1) — the contact form's
   honeypot rendered visibly until its selector was raised to match. Check
   computed style in a real render for anything that must be hidden.
8. The GSC-frozen heads (`<title>`, H1, meta description, canonical):
   `/revision-notes/`, the four past-papers board pages, marking.html,
   index.html's title. **tutoring.html left this list on 2026-08-25 —
   Eliot lifted its freeze for the tutoring SEO pass (D63); its September
   GSC comparison is directional only.** about/contact/faq heads are
   tunable but their og:description must stay a shortened variant
   (`KNOWN_SELF_DISAGREEMENT` in verify_page_shell.py) or leave that list in
   the same commit.
9. **Search Console's Pages report LAGS its own Crawl stats by days.** Every
   verdict in a page-indexing export is only as fresh as the `Last crawled`
   date on that row, so **read that column before believing the verdict**. On
   2026-08-21 the export implied no PDF had been crawled since 6 August while
   Crawl stats showed a spike of ~128 PDF requests a day on 8–9 August — and
   the audit reached a wrong conclusion before the graph was checked.
   `seo/tools/gsc_reconcile.py` now flags any verdict older than the file's
   last commit automatically.

## What remains flagged

Absorbed from `PROJECT-LOG.md` (now `_archive/PROJECT-LOG.md`) on 2026-08-20 and **re-checked line by line
before being written down here**, because most of the list it arrived with had
already been fixed without the file being updated. How each was checked is
stated. Nothing here blocks anything, and everything needs an explicit
instruction before a page is touched, per CLAUDE.md.

### Still open — economics content

The evidence for each is in `docs/REVIEW-NOTES.md` under the given ID. These
are **carried over and not independently re-verified**, except where stated.

| Item | Where | What it needs |
| --- | --- | --- |
| **N-Q8** | AQA `2-2-2` the role of expectations | New prose, and it is tested by a live question, so cutting the claim would strand it. Checked 2026-08-20: the phrase appears 0 times on the page, so this one is still open. The other two N-Q8 pages are now fixed — `1-4-2` covers regulatory capture and `2-5-4` covers sustainable development |
| **N-Q11** | Edexcel `2.4.1` and `2.4.2` | Still duplicating. Re-measured 2026-08-20: **90 shared ten-word runs**, about 17% of 2.4.2's body. Restructuring. Left by choice |
| **N-Q7** | `2-6-5` HDI figures | Dated. Left by choice |
| **N1** | Two multiplier formulas | A leading space inside `\text{ Injection}`. Cosmetic; confirmed as authored, left deliberately |
| **N6** | `1-2-3` elasticities | The midpoint formula went with an Exam Preparation section. **Decided: leave it out** — Edexcel uses the original-value method and the page's worked example agrees |
| **C4** | AQA `2-2-3`, `1-5-6` | Both were reported as cross-referencing Edexcel theme numbers that do not exist in the AQA specification. **Not re-verified** — a grep for "Theme N" now matches the baked nav on every page, so it needs reading, not grepping |
| **C5** | `2-1-2` | Confirm the unemployment-rate denominator matches the ONS/ILO definition given a few lines above |
| **G4** | `Regulation` | Defined twice, from two notes pages, and neither reads as a definition |

### Still open — housekeeping

| Item | Status on 2026-08-20 | Fix |
| --- | --- | --- |
| **`.notes-container` defined in more than one stylesheet** | **Worse than recorded.** PROJECT-LOG said two; it is now **five**: `revision-notes-topics`, `revision-notes-textbook`, `glossary`, `macro-application`, `practice-questions`. *2026-08-23: `revision-notes-topics` is now scoped under `.notes-hub-page` and `practice-questions` no longer defines it, so three remain* | Scope each under its page wrapper, per the CSS convention in CLAUDE.md |
| **Prettier fails on three files** | Confirmed with `npx prettier@3.9.6 --check`: `css/main.css`, `revision-notes/index.html`, `revision-notes/macro-application/index.html` | main.css is a `box-shadow` list and pre-existing. The two HTML files must NOT simply be formatted — trap 1 |
| **`404.html` has no canonical and no Open Graph tags** | Confirmed: 0 matches | Defensible for a 404. Listed so it stays a decision |
| **`.year-header h4` in `css/pages/past-papers-list.css`** | Still present at line 45 while line 196 styles `.year-header h2` | Likely dead. Read the markup before deleting |
| **Web-font layout shift** | Not re-measured. CLS was 0.078 on a notes page and 0.154 on a questions page | Self-host with `size-adjust`, or preload the woff2 the fold needs |
| **Past-paper bank payload size** | Added 2026-11-25 (Phase 7). The master `/past-paper-questions/questions.json` went from 877 KB to 1,246 KB (204 KB gzipped) when the 450 MCQs went live; AQA's board payload is 441 KB. Phase 9 (2026-11-26) took the master to 1,526 KB (253 KB gzipped) and AQA's board payload to 721 KB (127 KB gzipped), shipped as measured (`aqa-as-mcq-tags.md` T3 A). Nothing caps either | Decide whether a budget is wanted. If so, measure what the search page actually loads before choosing what to trim or split |
| **OCR A Level Paper 3, June 2023** | **The question paper is missing.** Both PDFs at that path are the mark scheme, byte-identical, md5 `35b8975c…`. Confirmed by Eliot and verified independently; a sweep of all 281 PDFs found no other case | Download H460/03 June 2023 from OCR and save it over the existing filename. No URL, link or sitemap change |

### Still open — Edexcel B follow-ups

From the Theme 3 pre-launch checklist
(`05-website/drafts/edexcel-b-notes/review/theme-3-prelaunch.md`, "After
launch"), recorded 2026-10-20 when Edexcel B was completed. None blocks
anything.

| Item | What it needs |
| --- | --- |
| **An Edexcel B glossary** | **Closed.** Launched in `ba780911` and merged 2026-11-16 as PR #50 (`b7e12e77`), Phase 3 below. The index's glossary card took its approved wording at launch, and "with a page for Edexcel A and AQA" no longer appears on it |
| **National Living Wage on 3.5.3** | Dates every April. Next change: April 2027 |
| **The other dated figures** | Re-check once a year: the poverty line, aid, the CMA thresholds, Bank Rate history, PPP shares. Sources are in the unit review sheets |

### Closed since PROJECT-LOG was written — do not re-raise

Each was on its "still flagged" list and each is now done. Checked 2026-08-20.

- **`navPanel` `aria-hidden`** — the accessibility failure that held every page
  at 96. `js/components/nav.js` now uses `inert`, which takes the panel out of
  the tab order *and* the accessibility tree from one attribute.
- **Breadcrumb contrast** — `css/main.css` now carries the reasoning at line
  3464; the old `#7f888f` is gone.
- **Dead Edexcel B mark-scheme links** — 65 PDF links on that hub, 0 missing.
- **N-Q8 on `1-4-2` and `2-5-4`** — both now cover what they promised.
- **Merging `feature/topic-questions`** — live, §8.
- **Merging `feature/glossary`** — live, §6.
- **`inject-templates.js`** — replaced by `js/components/nav.js` at Wave 4.10.
  Nothing is fetched at page load any more. `_config.yml` still described it as
  a runtime fetch until 2026-08-20.

## September 2026 clean-up (2026-08-26) — branch `chore/september-cleanup`

The pre-term tidy-up: everything finished recorded and filed, everything
unfinished done, parked or handed to `OWNER-TODO.md`. One commit per phase,
each approved by Eliot at a phase gate; merged with a merge commit (the PR
number is in the merge commit itself).

- **Git**: the 14 merged local and 22 merged remote branches deleted with
  Eliot's approval; `record/macro-application-attempts` kept on origin,
  unmerged, as the paint-fault record (local copy deleted, re-fetchable).
- **Disk**: 182 gitignored Finder/iCloud duplicates (byte-checked against
  their originals and git history first), six `__pycache__/` and twelve
  `.DS_Store` removed with approval; `node_modules/` now in `.gitignore`
  by rule, not luck.
- **Moves, all `git mv`**: the five finished design-record folders
  (`mobile-nav`, `notes-family-consistency`, `notes-redesign`,
  `site-search`, `topic-tail`) → `_archive/working/`; the three finished
  build logs (`FLASHCARDS_PROGRESS`, `PAST-PAPERS-PROGRESS`,
  `QA_FIXES_PROGRESS`) → `_archive/`; this file's 26 project write-ups →
  `_archive/PROGRESS-detail-2026-08.md`, verbatim (D64), leaving the
  summary-plus-index shape above. `_working/` keeps only what scripts
  read or write on every run (`fontawesome/`, `glossary/`).
- **Extractions, so nothing was lost**: `docs/CONTENT_ISSUES.md` #37 (the
  flashcard alt texts), `docs/REVIEW-NOTES.md` N-Q21 (the
  comparative-advantage reversal — a live defect), the ten uncovered spec
  topics, the bank's verbatim-text licensing question, the deferred SVG
  cluster, Edexcel Section A, the written-response pilot and the
  galleries' past-papers panel — all into OWNER-TODO or the logs.
  `docs/audit/OPEN-QUESTIONS.md` Q14–Q17 gained their overdue ANSWERED
  banners; nothing there was actually open.
- **Also**: `README.md` became the half-page front door; the live web
  vitals were re-measured (CLS 0.000 on all eight samples,
  `seo/lh-live-2026-08-26/`); the tutoring SEO pass was marked LIVE
  (merge `0bcac57c`, PR #33).

## Project index

One block per project, newest first. **The full write-up of every project —
what changed file by file, how it was verified, and its "things a future
session needs to know" — is in `_archive/PROGRESS-detail-2026-08.md`,
verbatim, under the same headings and in the same order.** The blocks here
are the summary: what shipped, when, which merge.

### All-boards parity — Phase 9, AQA AS Section A MCQs (2026-11-25 to 2026-11-26) — LIVE, MERGED 2026-11-26 AS PR #58 (`1dadc8c2`, branch `feature/aqa-as-mcqs`)

D71. The design sheet is `review/phase-9-aqa-as-mcqs.md` (every
recommendation approved 2026-11-25), the tags sheet `review/aqa-as-mcq-tags.md`
(T1–T3 A, 2026-11-26). The dry run, page images beside records, is
`review/phase-9-dry-run.html`.

- **Scope.** Section A of the 18 non-specimen AQA AS Paper 1 and 2 papers
  (June 2016–2019, November 2020, June 2022–2025): 20 one-mark MCQs each,
  360 cards. Section B and the specimens stay out. No reuse against Paper
  3's 270 MCQs. Between AS papers one question was set twice (P1 June 2016
  Q20, P1 June 2018 Q16), which the design sheet's §5 missed; per the
  bank's rule both stay, each card labelled by its series.
- **Done: the extractor and its checks.** `extract_aqa_questions.py` reads
  AS Section A into `aqa-as/`: the question count is a parameter (30 or 20);
  the 2016–2019 closing line "QUESTION 20 IS THE LAST QUESTION IN SECTION A"
  is furniture (it set a false `usesFigure`); a space glyph starting inside a
  letter is dropped (it split "F igure" in six 2022–2025 papers); an AS paper
  is accepted on its own Section A, because the hosted PDFs bundle the
  Insert inconsistently. All 27 A-level files re-extract byte-identical.
  The verifier's M4 counts twenty on AS. `aqa-as` is in `BANK_DIRS`.
  `test_question_search.js` holds AS as shared once every board sets it,
  and gains an AQA AS block that runs once the data has one.
- **Done: extraction (2026-11-25).** All 18 papers, 20 records each, every
  one high confidence with its key-list page and no answer field;
  `verify_past_paper_extraction.swift` reads `aqa-as/` (M1–M5, M4 at
  twenty) and passes. One more extractor fix: an option that wraps back to
  the letter column rather than the indent (AS P2 June 2016 Q4 "…and a
  higher / exchange rate") continues the option above when it sits between
  two option rows. The 27 A-level files are still byte-identical. Untagged,
  so nothing publishes.
- **Done: tagging (2026-11-25).** First pass committed (`273df531`), then a
  blind `cold-solver` pass per paper: 260 of 360 match. The 100
  disagreements, the page list (1.1.2, 1.1.3, 1.4.2, all MCQ-only) and the
  measured payloads went to Eliot in `review/aqa-as-mcq-tags.md`. The blind
  pass found one more extractor defect (a 7pt space, "Q2,the"), fixed in
  `5ef39fb9`; a dropped-line audit found three (`57513bd7`, `75210df9`).
- **Done: build (2026-11-26).** Eliot answered T1 A, T2 A, T3 A: 46 tag
  changes applied; 1.1.2, 1.1.3 and 1.4.2 built (all MCQ-only);
  `QUALIFICATION_PHRASE["aqa"]` (W1–W3); `verify_page_shell` ppq 253 to 256.
  `test_question_search.js` needed two fixes on its first run against AQA
  AS data (`cedfd666`): an AS-aware extract rule, and the AQA AS block
  moved below the filter harness it calls.
- **Merged 2026-11-26 as PR #58 (`1dadc8c2`)**, with a merge commit. CI
  passed on the PR. The bank holds 2,052 questions; the AQA hub 909.
- **Left open:** the bank's payload size, under "Still open —
  housekeeping".

### All-boards parity — Phase 7, real exam MCQs (2026-11-25) — LIVE, MERGED 2026-11-25 AS PR #56 (`ed377dc7`, branch `feature/bank-mcqs`)

Brief §13, D67. The review sheets are `review/phase-7-mcqs.md` (the design,
answered 1-5 A and W1-W4), `review/mcq-tags.md` (the tags, T1-T3 A) and
`review/launch-pastPaperMcqs.md` (the AQA launch, M1 A, M2 A; the
Edexcel A launch, N1 A).

- **Family.** `pastPaperMcqs` is a sixth feature in `boards.json`, inside
  the bank, so it can be staged while the bank stays live. Records sit in
  the existing paper files with `type: "mcq"`, `options` (A-D as printed,
  or null when they are not text) and `usesFigure`. They have **no answer
  key anywhere**, and the verifier fails if one appears. Written records
  are byte-identical.
- **Extraction** (`11dca100`). 450 MCQs: 270 AQA Paper 3 Section A, 180
  Edexcel A Papers 1-2 Section A. `verify_past_paper_extraction.swift`
  gains M1-M5.
- **Rendering** (`7e4b1713`). The card lists its options with no radio
  buttons and carries a "Multiple choice" badge and a figure or options
  note. A "Question type" filter is `hidden` wherever a page's payload has
  one type. MCQs count toward the D60 gate (answer 4 A, which supersedes
  D68's "mint no URLs").
- **Tags** (`8578df10`, `f9d8376b`). A first pass, then a blind
  `cold-solver` pass that agreed exactly on 355 of 450; 55 entries changed.
  T2 approved 15 new topic pages: 12 AQA and 3 Edexcel A.
- **AQA launch** (`cd53c005`, sitemap `1ca1662a`, pushed 2026-11-25).
  `/launch-feature aqa pastPaperMcqs`.
  - A throwaway build minted exactly the 12 approved AQA topic pages.
  - The bank goes from 1,242 to 1,512 questions, and the AQA hub from 279
    to 549.
  - M1: the notes tail's "1 marks" became "1 mark", which also fixed the
    live Edexcel A 1.1.1 page.
  - Three question-search checks and one notes-tail test assumed no live
    MCQs, and now state the approved design.
  - The full suite passed before the push.
- **Edexcel A launch** (`9e3a37fc`, sitemap `e2222ee5`, pushed
  2026-11-25). `/launch-feature edexcel-a pastPaperMcqs`.
  - The throwaway build minted exactly the 3 approved pages (2.3.1, 3.4.2,
    4.5.1), and no AQA or Edexcel B file changed.
  - The bank goes to 1,692 questions, and the Edexcel A hub from 601 to
    781.
  - N1: the bank's topic and section heroes said "A-Level Economics
    papers" whatever they held. `level_phrase()` now says "AS" or
    "A-Level and AS" where the questions are, on 100 Edexcel A and B
    pages.
  - `verify_page_shell.py`'s bank page count was reseeded from 238 to 253,
    covering both launches. The AQA commit missed it: `pages()` counts
    tracked files only, so the check passed while the new pages were
    untracked. **Reseed in the same commit that adds pages.**
- **Merged 2026-11-25 as PR #56 (`ed377dc7`)**, both launches in one PR,
  with a merge commit. CI passed on the PR.
- **Left open:** the bank's payload size, under "Still open —
  housekeeping".

### All-boards parity — Phase 6, Edexcel A Section A written parts (2026-11-24 to 2026-11-25) — LIVE, MERGED 2026-11-25 AS PR #54 (`96439950`, branch `feature/edexcel-a-section-a`)

Brief §13. The review sheets are `review/phase-6-section-a.md` (the split
and the card shape), `review/section-a-tags.md` (the tags, answered
2026-11-24) and `review/launch-section-a.md` (W1-W3, answered 2026-11-25).

- **Scope.** Section A of every 9EC0 and 8EC0 Paper 1 and 2, 36 papers:
  **259 written parts**, 124 A Level and 135 AS. A part is an MCQ if and
  only if it prints A-D answer boxes; each question's one 1-mark MCQ is
  not extracted and waits for Phase 7.
- **Extraction** (`a112e1fe`). `extractSectionA()` in
  `scripts/extract_past_paper_questions.swift`. Each card carries its
  question's stem and lead-ins verbatim, then its own text; sub-parts stay
  inside their part with the marks summed. A part printed on a later page
  than its stem links back to it: "Question N as printed". One glued table
  cell is removed by a named exception that fails loudly if the layout
  changes. Every existing record, and every Edexcel B and Paper 3 file, is
  byte-identical, and a re-run changes nothing.
- **Verification.** `verify_past_paper_extraction.swift` gains Section A
  checks: words come off the pages in runs, the closing run is on the
  part's page, no card reads as an MCQ, and each question sits exactly one
  mark short of its printed total. Planted errors were caught three times
  out of four; the fourth, the glued-cell class, only the rendered page
  shows.
- **Tags** (`08e5466a`, `a3a315e5`). A first pass in `tags.json`, then a
  blind `cold-solver` pass that agreed exactly on 182 of 259. Eliot took
  option A on R1-R4 and the recommendation on all 80 rows, so 63 entries
  changed. R5 approved the 13 new topic pages (D60 gate of 2); every
  existing topic page keeps its place.
- **Pages** (`a3a315e5`). 13 new topic pages under
  `/past-paper-questions/edexcel/`. The bank goes from 983 to 1242
  questions and the Edexcel A hub from 342 to 601. 72 Edexcel A notes
  pages show new "real exam questions" counts, and on 8 of them the
  past-paper link now points at a new topic page instead of a search
  (Markup-Change).
- **Wording** (`review/launch-section-a.md`). W1: "1 mark", singular, on
  the bank's first 1-mark cards (45 parts) and the Marks filter
  (`88aa1b55`). W2 option A and W3: the Edexcel A and Edexcel B hubs and
  the master page name both qualifications, A Level and AS, through
  `QUALIFICATION_PHRASE` in `build_past_paper_questions.py` (`a6e5d03d`).
  AQA and `boards.json` are unchanged.
- **The pinned count missed again.** `a3a315e5` added the 13 pages but
  left `verify_page_shell`'s `ppq` count at 225; it passed until the
  pages were committed. Reseeded to 238 in `88aa1b55`. This is the Phase 4
  lesson recurring: **run the whole suite again after the commit that
  adds pages.**
- **Documentation.** The scope table in
  `past-paper-questions-data/CLAUDE.md` records Section A as built.
- **Merged 2026-11-25 as PR #54 (`96439950`).**

### All-boards parity — Phase 5, twin links across three boards (2026-11-24) — LIVE, MERGED 2026-11-24 AS PR #53 (`f1110a8a`, branch `feature/edexcel-b-twins`)

Brief §12. The review sheet is `review/twins.md`, approved Q1-Q9 on
2026-11-24 (D70).

- **`scripts/notes_twins.py`.** `board_of_dir` returns `edexcel-b` for B
  directories. Three new directed tables (`B_TO_A`, `B_TO_AQA`, `TO_B`) sit
  beside the unchanged `TWINS`. `twins()` returns at most one twin per other
  board; `PAIRS` is every declared pair. `main()` checks that each table only
  crosses its own boundary. Counts: `python3 scripts/notes_twins.py`.
- **`scripts/notes_extras.py`.** `twin_sentence()` renders one or two twins
  as one sentence. "Edexcel" became "Edexcel A".
- **`seo/tools/verify_seo.py`.** Assertion 13 reads `PAIRS`. Assertion 18
  checks every declared twin, and that a block holds no others.
- **`scripts/new_topic.py`.** The twin step is shared by both checklists.
- **Pages.** 175 notes pages rebuilt: every B page that gained a twin, and
  every Edexcel A / AQA page that gained a B twin or lost the bare
  "Edexcel". `dateModified` was not moved. Text-Change trailers on all 175.
- **Hub switch lines** (Q4; H1-H3 approved 2026-11-24). The four B hubs
  gain a "Studying Edexcel A or AQA instead?" line, and the six Edexcel A
  and AQA hubs gain an Edexcel B sentence. The sources are in
  `notes-data/hubs/`, edited by hand. `verify_seo` `HUB_TWINS` goes from 8
  to 27 pairs. 10 hub pages rebuilt.
- **Merged 2026-11-24 as PR #53 (`f1110a8a`).**

### All-boards parity — Phase 4, Edexcel B past-paper bank (2026-11-16 to 2026-11-17) — LIVE, MERGED 2026-11-17 AS PR #51 (`ce9369ed`, branch `feature/edexcel-b-bank`)

Step 1 of brief §11. The review sheet is `review/phase-4-extraction.md`, with
a side-by-side page for A Level Paper 1 June 2019 beside it. Eliot approved
Q1-Q6 on 2026-11-16.

- **Extractor.** `extract_past_paper_questions.swift` gains `extractB()` for
  9EB0 and 8EB0, routed by filename. Before this, a B filename matched the
  Edexcel A pattern and would have been written over
  `edexcel-a/p1-<series>.json` as 9EC0. The structure is read from the page:
  - Sections come from the "before answering" openers. Parts run (a)-(h),
    and a single 20-mark question has no parts.
  - Each question's tariffs must sum to its printed "Total for Question".
  - Lead-ins are kept verbatim at the start of `questionText` (Q2).
  - P2 June 2022 1(b)'s in-question table is not reproduced (Q3).
  - The parse stops at "TOTAL FOR PAPER", so P3's bound-in pre-release
    insert (June 2017, November 2021) is skipped.
  - Two mark-scheme heading layouts are used for B only.
  - **Edexcel A re-extracted byte-identical**, all 45 papers.
- **Data.** `edexcel-b/` and `edexcel-b-as/` (Phase 0 Q8). Counts come
  from the extractor's run, and today they are:
  - 36 papers and 351 questions from text-layer PDFs (the 37th is by OCR,
    below), all high confidence;
  - every mark-scheme page matched;
  - `strip_source_attributions.py`: 0 changes.

  Ids are `edexcel-b-p1-2019-jun-q1a` and `edexcel-b-as-…` (Q6).
- **Verifier.** `verify_past_paper_extraction.swift` reads the B
  directories, with four checks of its own (5-8):
  - the closing words are on the question page;
  - the label heads a mark-scheme row next to "Knowledge" (a bare "2" proves
    nothing);
  - the marks sum to the printed total;
  - the context page carries an extract, and there are no choice groups.

  A mutation test confirmed all four fire. It checks 693 questions across
  81 papers and passes, with three warnings:
  - Edexcel A P3 November 2021 2(d) and Edexcel B AS P1 October 2020 2(d):
    the scheme labels each "(d)" without the question number.
  - Edexcel B P1 June 2025 prints no "Sources for use with SECTION B" booklet
    heading. Its Q2 links Extract G (p25), found by name; the first pass
    linked its own question page, which the verifier caught.
- **AS Paper 2 June 2019 by OCR (Q4, option A of the follow-up).** The
  question paper is an image-only scan ("Microsoft: Print To PDF"). Eliot
  found no text-layer copy anywhere, so it was OCRed:
  - `scripts/ocr_pdf_pages.swift` uses Apple Vision and needs no new
    dependency.
  - Every question and structural line was checked word by word against the
    page images, with four glyph corrections (‘ ’ and –).
  - The checked transcript is committed as
    `past-paper-questions-data/ocr/…june-2019-question-paper.txt`, and the
    extractor reads it for that paper only, giving 11 questions.
  - The verifier runs its own OCR at different settings. For a scanned paper
    it requires the whole question text, not just the opening and closing
    words (check 9). Three planted transcript misreads were all caught; the
    mid-sentence one only by check 9.
  - Spot-checked by Eliot against the page images, 2026-11-16
    (`review/phase-4-ocr-as-p2-june-2019.html`): confirmed.
  - The Phase 4 totals are 37 papers and 362 questions, with the verifier at
    704 questions across 82 papers.
- **Approved wording, for Step 3 (Q5).** The Paper 3 card note reads:
  "Paper 3 is set on a broad context that Pearson pre-released the November
  before the exam. The extracts in the paper were unseen on the day." It
  comes from the 9EB0 specification.
- **Step 2, tagging (2026-11-16).** Every B question has a first-pass entry
  in `tags.json`.
  - `verify_past_paper_tags.py` reads the two B directories. It gains
    check 6, a topic must be the question's own board's, which a planted
    Edexcel A slug confirmed. It counts only live boards towards the gate.
  - A blind `cold-solver` pass in tag mode saw the question text and a
    taxonomy excerpt only. The disagreements, with a recommendation each,
    are in `review/bank-b-tags.md`.
  - The first blind run for Paper 3 and AS came back before those groups
    were tagged, so they were compared against a fresh second run instead.
  - The card's "Revision notes" link goes to a question's **first** topic,
    so lead-topic order is a real disagreement, not a cosmetic one.
  - **Eliot approved every recommendation (2026-11-16).** The rules are:
    - Q1: tag both themes where the spec teaches a topic twice.
    - Q2: tag 1.6.1 only when the percentage change is the answer.
    - Q3: use an out-of-paper topic only where the spec teaches it nowhere
      else.
    - Q4: on a supply and demand diagram, the curve that shifts leads.

    All 129 rows were applied, changing 92 entries. Two agreed-but-wrong
    tags were also fixed, found by checking the mark schemes. With the
    final tags, 79 B topics would reach the gate of 2.
  - Taxonomy note for Step 3: 3.5.3 is titled "Minimum Wage Legislation"
    but also carries skills shortages and migration (spec 3.5.3 b, c).
- **Step 3, the build (2026-11-17, `e6cd7f8f`).** B stages
  `pastPaperBank`, so a normal build checks B and publishes nothing
  (`build.py` and `verify_generated`: 0 files). The review sheet is
  `review/phase-4-build.md`.
  - **How the build reads B.** The generator reads paper directories by
    flag (`BANK_DIRS`, `paper_dirs()`). B's papers append after A and AQA,
    so no live `q.p` index moves. `validate_staged()` builds B's index and
    renders its pages in memory, and fails on an untagged B question.
  - **The Paper 3 note** sits under the question on all 72 B A Level
    Paper 3 cards. It's held once, in `PAPER_NOTES`.
  - **The master search.** `question-search.js` keys groups by board and
    slug, because Edexcel A and B share `theme-1`..`theme-4`. Keyed by
    slug alone, B's names labelled A's themes and picking A's Theme 1
    adopted Edexcel B. Section C and AS Level are now listed once, under
    every board that sets them.
  - **Tests.** `test_question_search.js` runs B-only checks whenever the
    data carries B.
  - **Docs.** The scope table in `past-paper-questions-data/CLAUDE.md` is
    updated per D67. The OWNER-TODO licensing item is closed: checked by
    Eliot, 2026-10.
  - **The preview** (`EA_PREVIEW=edexcel-b:pastPaperBank`) had 983
    questions, with B adding a hub, 4 theme pages and 79 topic pages.
    Every new path is under `/past-paper-questions/edexcel-b/`, and every
    topic slug is its notes page's own.
  - **Eliot approved the preview, the 84 URLs and Q1–Q3 (2026-11-17):**
    - the note stays under the question;
    - 3.5.3 keeps the spec's title;
    - the hub intro keeps the 9EB0-only pattern Edexcel A's uses.

    The preview was then removed from the tree.
- **Step 4, the launch (2026-11-17, `64331b4e`; sitemap `e9aa2ca4`).**
  `/launch-feature edexcel-b pastPaperBank`. The review sheet is
  `review/launch-pastPaperBank.md`; Eliot took L1–L6 as recommended and
  L7 B.
  - **URLs.** A feature-on worktree wrote exactly the 84 approved pages and
    their 80 payloads, all under `/past-paper-questions/edexcel-b/`. No
    live `q.p` index moved.
  - **Master page** (L1–L3). The boards are named from an approved phrase
    per board set (`BOARDS_PHRASE`; an unknown set stops the build):
    "Edexcel A, Edexcel B & AQA" in the title, "… and AQA" in prose. The
    Board select says "All boards". "The specifications number their
    topics differently…" has no count.
  - **`/past-papers/`** (L4) names the three boards and gains "Search
    Edexcel B questions"; the A button says "Search Edexcel A questions".
  - **`/past-papers/edexcel-b/` and the four B notes hubs** (L5, L6) carry
    Edexcel A's resource strips in A's wording. That closes a gap the
    practice and flashcards launches left. Frozen heads untouched.
  - **The bank calls Edexcel A "Edexcel A"** (L7), from `names.display`,
    set once in `build_past_paper_questions.load()`. About 70 indexed A
    bank titles changed; no URL did. Eliot kept "Edexcel A A-Level
    Economics …" on the A hub as it reads.
  - **Derived, in A/AQA wording:** the 85 B notes tails, the 85 B practice
    pages and 4 board indexes, the 4 deck buttons (`PAPERS_LINK`), the bank
    link on 79 B topics in site search, and the `/past-papers/` count.
- **CI caught a pinned count** on PR #51: `verify_page_shell` pins each
  family's page count, and the 84 pages took `ppq` from 141 to 225. It
  passed locally because it counts committed files and the pages were
  untracked when the suite ran. Reseeded in `0fe2c8de`. **Run the whole
  suite again after the launch commit**, not just the checks that look
  commit-dependent.
- **Merged 2026-11-17 as PR #51 (`ce9369ed`).**

### All-boards parity — Phase 3, Edexcel B glossary (2026-11-12 to 2026-11-16) — LIVE, MERGED 2026-11-16 AS PR #50 (`b7e12e77`, branch `feature/edexcel-b-glossary`)

The B glossary is built and checked in full, and no page is written (D68).
Every live page, `terms.json` and the search index were byte-identical at
each commit. The review sheet is `review/glossary-b.md`: Eliot took every
recommendation on Q1-Q13 on 2026-11-16.

- **Staging, and what it found** (`fd7452ae`). `board_data` can stage the
  glossary, and a staged glossary puts its board in `taxonomy.json`.
  `extract_glossary.py` runs a second extraction into the gitignored
  `_working/glossary/staged/`. That run fails on B's problems, and on any
  change launching B would make to a live page (`launch_impact`). The guard
  caught B's formula headings taking two live anchors. **`GENERATION`** now
  settles names, labels and ids oldest board first, so a later board never
  renames an earlier one's entry. `build_glossary.py` keys groups on
  (board, slug) and renders the staged pages in memory. It also pre-renders
  display maths inside a definition (17 B chips). `check_glossary_
  capitalisation.py --staged`. The search bitmask is derived (B = 4) and
  `site-search.js` decodes it; this is dormant until launch.
- **Eliot's answers applied** (the commit after `fd7452ae`):
  - Q1-Q3: B's intro and meta, the three-board "Switch to the … or …
    glossary" hero, and the landing copy ("three specifications", "Edexcel
    A, Edexcel B and AQA"). They are in `build_glossary.py` and print on no
    page until launch.
  - Q6: 35 B formula labels in `curation.formulaLabel`, with no exclusions.
  - Q7: no authored definitions for B. **The B glossary is entirely the B
    notes' own words.**
  - Q8: every B definition capitalised at render time
    (`--approve --staged`, plus "man-made" and "supply-side" added to the
    classifier). The approve run dropped two stale `regulation` "leave"
    keys that matched no current definition.
  - Q9: B shows 2.5.3 for inflation, 2.5.4 unemployment, 2.4.2 economic
    growth, 4.2.1 trade union, 3.1.5 appreciation and 1.5.2 subsidy, plus
    the 4.x wording for aggregate demand, monetary policy and supply-side
    policies (decided 2026-11-11).
  - Q10: risk and interdependence show two numbered senses under one
    headword (`curation.senses`, `.gl-senses` in `glossary.css`).
  - Q11: on B 1.3.1 and 1.3.2, each chip now has its own paragraph. This is
    markup only, with no wording changed. B gains Substitutes and
    Complements, and indirect tax no longer runs on into the subsidy
    sentence. This closes the Theme 3 QA item "subsidy has a third chip on
    1.3.2": the glossary shows 1.5.2.
  - Q12: "average cost" is aliased into "Average Cost (AC)". Q13: no table
    harvests.
- **Rationalisation** (2.3.2 "cutting capacity…" against 3.1.1
  "reorganising a business…"): Eliot, 2026-11-16, said 2.3.2 only. It shows
  2.3.2, with 3.1.1 under "Also covered in", which is the default, so no
  curation is needed. Nothing in Phase 3 is still open before launch.
- **At `/launch-feature`** (wording approved): move glossary from `staged`
  to `features`. Change the `revision-notes/index.html` card line to "…with a
  page for Edexcel A, Edexcel B and AQA." (Q4). Change site search's Edexcel
  A glossary label from "Edexcel" to "Edexcel A" (Q5). Add
  `/revision-notes/glossary/edexcel-b/` to `build_search_index.BOARD_HUBS`.
  Add `Text-Change:` trailers on the landing page, both live glossary pages
  and the index. Run the sitemap after the push.
- **Launched, 2026-11-16 (`ba780911`, sitemap `43d4c14a`;
  `review/launch-glossary.md`, G1 A recorded as D69, G2 A). Merged
  2026-11-16 as PR #50 (`b7e12e77`).**

### All-boards parity — Phase 2, Edexcel B flashcards (2026-11-08 to 2026-11-12) — LIVE, MERGED 2026-11-12 AS PR #49 (`9576a168`, branch `feature/edexcel-b-flashcards`)

`/edexcel-b-flashcards`, one unit per run, into
`flashcards-data/edexcel-b/theme-N.json`. B's `flashcards` is **staged** in
`boards.json`, so the decks are validated and no page is written. Review
sheets: `05-website/drafts/all-boards-parity/review/flashcards-unit-X-Y.md`.

- **Theme 1 written: 142 cards, units 1.1 to 1.6.** Every card verified
  cold against its notes page. Deck-level wording approved 2026-11-09.
- **Card budget (Eliot, 2026-11-09):** Theme 1 stays at 142. Themes 2 to 4
  aim for about 5 cards a topic (about 120, 95 and 95), more only for a
  diagram or calculation that needs its own card, named in the unit sheet.
  Written into the skill.
- **Answers to the Theme 1 sheets, 2026-11-09:** four notes wording changes
  on Edexcel B Theme 1 pages (the 1.6.3 profit chip now matches 1.2.2's;
  `CONTENT_ISSUES.md` #38 and #39 fixed; 1.5.2 "a larger share of a poorer
  household's income"), and the excess-demand/supply SVG `<desc>` text
  aligned to Qd/Qs.
- **Theme 1 diagrams approved (Eliot, 2026-11-09):** each of the 11 diagram
  cards' SVGs rendered headless and compared with its notes-page PNG in
  `review/flashcard-diagrams-theme-1.md`. Every label, curve and number
  the card text relies on is present. No SVG or card changed; nine of the
  SVGs are shared with the Edexcel A and AQA decks.
- **Numbered PPF drawn, 2026-11-09:** `images/diagrams/svg/ppf-numbered.svg`
  is a new file; `ppf-basic.svg` is untouched. Q2 answered (a): 1.1.1
  diagram-01 and calc-01 now use it, with alt text that gives the four
  points' figures. Fronts and backs unchanged.
- **Theme 1 QA applied (Eliot, 2026-11-09, all four fixes approved):**
  `review/qa-flashcards-theme-1.md` found no high or medium defects. The
  1.2.5 interest-rate chip now uses 1.4.1's wording ("…or the reward for
  saving it, shown as a percentage of the amount borrowed or saved per
  year"), and card 1.2.5 def-01 follows it. Three shared SVGs get label
  clearance under `DIAGRAM_STYLE.md`'s 8px rule: `excess-demand.svg`'s
  "Excess demand" gains a white halo over the guides, and the "Government
  expenditure" / "Government revenue" labels move off the P1 guide. Those
  three also change the live Edexcel A and AQA decks at the next push.
- **Theme 2 written: 126 cards across 24 topics, units 2.1 to 2.6**,
  including the new PED-ranges diagram card for 2.2.1 (its 800×960 SVG and
  the multi-panel canvas line in `DIAGRAM_STYLE.md` approved in
  `review/flashcard-diagrams-theme-2.md`, Q1 (a) and Q2 (a)).
- **Theme 2 QA applied (Eliot, 2026-11-10, all four fixes approved):**
  `review/qa-flashcards-theme-2.md` found no high or medium defects. The
  niche-market chips on 2.1.5 and 2.2.1 and the trade-off chip on 2.6.3
  now use the Theme 1 wording (1.3.4 and 1.1.1), and cards 2.1.5 def-02
  and 2.6.3 diagram-01 follow them. 2.2.4 eval-01 no longer calls used
  cars an inferior good, and 2.4.1 app-01 says China joining the WTO is
  also trade liberalisation. `trade-cycle.svg`'s "Boom" moves to y=284 to
  clear the curve by 8px; that SVG is shared with the live Edexcel A and
  AQA decks, so they change at the next push. The 3.3.2 niche-market chip
  this left behind was aligned on 2026-11-10 (`db6bb8e3`).
- **Theme 3 written: 100 cards across 19 topics, units 3.1 to 3.6**
  (`1ef93593` to `a635ab49`), with a review sheet per unit.
  CONTENT_ISSUES #42 and #43 fixed, #44 and #45 closed with no change.
- **Theme 3 QA applied and diagrams approved (Eliot, 2026-11-11, all
  fixes accepted):** `review/qa-flashcards-theme-3.md` found no high
  defects and no factual or calculation errors. Five 3.1 chips now take the
  earlier B wording, and their cards follow: nominal value and real value
  (3.1.1, from 2.5.3), trade liberalisation (3.1.2, from 2.4.1), subsidy
  (3.1.4, from 1.5.2) and current account (3.1.5, from 2.6.1, which adds
  transfers). Two shared SVGs get 8px label clearance: on `j-curve.svg`,
  "Depreciation occurs" is centred over its guide at y=44 and both guides
  stop at y=496, above "Deficit (X<M)"; on `tariff.svg`, "Ddomestic" moves
  to y=508. Both are shared with the live Edexcel A and AQA decks, so those
  change at the next push. All six Theme 3 diagrams are then approved
  (`review/flashcard-diagrams-theme-3.md`, Q1 answered by the QA fix).
  **Still open, before the B glossary (one wording per term):** subsidy
  has a third chip on 1.3.2 ("…to producers, which lowers their costs"),
  which the approved fix did not name. Trading bloc, appreciation and
  exchange rate differ only by an example sentence, so the glossary takes
  the shared first sentence. The B practice question 3.1.4 working still
  quotes the old subsidy wording; it is not a chip, so it was left.
- **Theme 4 written: 98 cards across 19 topics, units 4.1 to 4.5**
  (`4b87b7da` to `f74e639f`), with a review sheet per unit.
- **Theme 4 QA applied and diagrams approved (Eliot, 2026-11-11, all
  fixes accepted):** `review/qa-flashcards-theme-4.md` found no high
  defects and no factual or calculation errors.
  - `natural-monopoly.svg`'s "D=AR" moves to (520, 550), below the axis
    beside the end of its line, clearing LRMC. 4.2.1's
    `natural-monopoly.png` was re-rasterised from it (headless Chrome at
    2x, the 64-colour re-encode, a new WebP twin). Neither file is used
    outside B.
  - 4.1.1 def-01 gains a line saying that where the B spec lists imperfect
    competition beside monopoly and oligopoly, it means monopolistic
    competition. 4.1.2 def-01's front no longer mentions "the page".
  - One wording per term, before the B glossary. (a) Each citing chip now
    quotes the chip it cites, pointer kept: market failure on 4.2.1 (from
    1.5.1), productivity on 4.1.5 (from 2.3.1) and trade union on 3.5.2
    (from 4.2.1). (b) The 4.x chips take the earlier wording: average cost
    on 4.1.4 (from 1.6.1's first sentence; its "Total cost ÷ Quantity"
    formula is unchanged), economies of scale on 4.1.2 (from 2.1.1),
    fiscal policy on 4.4.2 (from 2.6.2) and non-price competition on 4.1.1
    (from 2.2.3, with its examples). The cards follow, with the verbatim
    source updated. (c) Aggregate demand, monetary policy and supply-side
    policies keep both chips; **the B glossary uses the fuller 4.x
    wording** (4.4.1, 4.4.2, 4.4.3). (d) Risk (1.4.2 business risk, 4.5.1
    measurable risk) and interdependence (3.1.3 countries, 4.1.3 firms)
    keep both chips; **the B glossary gives each two senses under one
    headword**.
  - Diagram sheet (`review/flashcard-diagrams-theme-4.md`): Q1 (a), the new
    `perfect-competition-profit-to-longrun.svg` and card 4.1.1 diagram-02,
    so the deck is 99. Q2 (a), `perfect-competition-short-run-supernormal-profit.svg`'s
    dashed price line stops at x=415, short of the firm's "P1". That SVG is
    shared with the live Edexcel A and AQA decks, so they change at the next
    push.
  - Eliot approved the text of card 4.1.1 diagram-02 on 2026-11-11.
  - `perfect-competition-short-run-loss.svg` (A and AQA only) had the same
    line-through-"P1" fault. Eliot asked for the same fix on 2026-11-11:
    its dashed price line now stops at x=415, 8px short of the firm's "P1".
    Its firm-panel Q1 guide also ran through the "1" of "D=AR=MR=P1"; it
    now breaks around the label (y 393 to 428), 8px clear of the ink
    above and below. It is shared with the live Edexcel A and AQA decks,
    so they change at the next push.
- **Unit 4.5 answers (Eliot, 2026-11-11, all four recommendations taken):**
  CONTENT_ISSUES #54 fixed. 4.5.3 now says "the Bank regularly checks" and
  the 4.5.4 table says "Regular stress tests", because since 2025 the Bank
  runs its main capital stress test every other year (checked on
  bankofengland.co.uk the same day; the entry cites the pages). #53 and
  #55 closed with no change. The two stress-test cards keep "regularly" /
  "Regular", and 4.5.3 def-02 keeps its added sentence. **Theme 4 is
  accepted as complete at 99 cards.**
- **Launched, 2026-11-11 (`4cfe0dac`, sitemap `740dfc17`; PR #49).**
  `/launch-feature edexcel-b flashcards`: 85 of 85 topics carried, 467
  cards, and the throwaway-worktree build wrote exactly the 8 URLs of
  Phase 0 Q6. `flashcards` moved from `staged` to `features`. Eliot's
  answers to `review/launch-flashcards.md` (F1 to F5) applied: the B
  notes tails, the `/flashcards/` hub head, the home page card, FAQ and B
  board card, and `names.flashcards` on the B groups.
  **F1, for the B bank launch:** B deck pages' third button links
  "Edexcel B past papers" (`papersUrl`), because the bank button would
  have been a 404. `build_flashcards.PAPERS_LINK` flips it to the bank
  when B's `pastPaperBank` goes live; `/launch-feature` step 4 now has
  the check. The search-index test's deck count is now derived, and
  `EXPECTED_KATEX_PAGES` declares B Themes 2 to 4.
- **Five Theme 1 cards removed (Eliot, 2026-11-12), not replaced:**
  `1-1-2-def-01`, `1-1-3-eval-01`, `1-1-3-eval-02`, `1-2-1-chain-01`,
  `1-2-2-eval-01`. Theme 1 is now 137, B 462, all decks 1,133; still 85 of
  85 topics carried, and the Theme 1 sample cards are unchanged.
- **Still open:** CONTENT_ISSUES #46 and #52, both deferred by Eliot.
- **Merged 2026-11-12 as PR #49 (`9576a168`).**

### All-boards parity — Phase 1, Edexcel B practice questions (2026-10-25 to 2026-11-08) — LIVE, MERGED 2026-11-08 AS PR #48 (`39403ead`, branch `feature/edexcel-b-questions`)

`/edexcel-b-questions <unit>`, one unit per run. Each unit gets a review
sheet, `review/questions-unit-X-Y.md`. Count the sets with
`ls questions-data/edexcel-b-theme-*/`, not from this list.

- **Launched 2026-11-08** (`3e764789`, sitemap `6ceb448d`, pushed to the
  branch; live only once the branch merges into `main`). `/launch-feature
  edexcel-b practiceQuestions` moved the family from `staged` to
  `features`. A throwaway build first confirmed it mints exactly the 89
  URLs approved in Phase 0 Q5. Launch wording is in
  `review/launch-practiceQuestions.md`, W1-W7, answered by Eliot the same
  day. The two that matter: B's board indexes say the sets "test your
  knowledge of the … content" and the hub intro keeps the real-papers
  claim for Edexcel A and AQA only, because 9EB0 sets no MCQs (D67). Also:
  the Edexcel B menu group (desktop and mobile), "Edexcel A Economics" on
  the hub, the home page practice card, FAQ and B board card, practice
  links on the B cards of `/revision-notes/` (replacing a stand-in
  past-papers link), and 2.1.3's set title with "(R&D)". The full suite
  passed, 27/27, before the push.
- **Before the merge:** check the pages in Live Server at desktop and
  360 px (the hub, a B board index, two B topic pages, a B notes tail, the
  menu, `/` and `/revision-notes/`). Then open the PR; it merges with a
  merge commit, so CI sees the trailers.

- **Unit 1.1** (`f8506b72`, answered 2026-10-26): 22 questions across
  1.1.1-1.1.3, 22/22 cold, 0 exact / 0 near. The first unit also staged the
  family and added the wording B's pages will print, all approved: each
  group's three practice names, B's `HUB_SECTIONS` entry, and 23 `UNITS`
  rows copied verbatim from the B notes hubs.
- **Hub wording is already approved and wired** for launch (unit 1.1 Q2):
  `build_questions.HUB_BOARDS_PHRASE` switches the hub's title and
  description to "Edexcel A, Edexcel B and AQA" when B goes live. Step 4 of
  `/launch-feature` needs no new wording for those two lines or for
  `HUB_SECTIONS`.

### All-boards parity — Phase 0 groundwork (2026-10-24) — LIVE (merged 2026-10-24, `fafdf34f`, PR #45; branch `feature/all-boards-groundwork`)

D67 (2026-10-24) gives Edexcel B practice questions, flashcards, a glossary
and a past-paper bank, and widens the bank to Edexcel A Section A short
answers and search-only real MCQs. Nine phases. The plan is the Claude Doc
"All-Boards Parity Plan", and the technical brief is
`05-website/claude-code-prompts/all-boards-parity/BRIEF.md`. Review sheets
go in `05-website/drafts/all-boards-parity/review/`. This branch is Phase 0
and mints no URL.

- **Per-board feature flags** (`15cd34ff`). `notesOnly` became a `features`
  list per board in `boards.json`. `board_data.load(family)` and
  `groups(family)` take the family and have no default.
  `has_feature(notes_dir, family)` replaced `is_notes_only`. The taxonomy is
  a derived family (glossary or bank), and `board_data` refuses either
  without practiceQuestions. The bank and the glossary each filter
  `taxonomy.json` to their own boards. `verify_boards.py` PINNED was
  reseeded. **Byte-identical**: `build.py` over the edited tree reported 0
  files changed, and `verify_generated.py` on the commit said 0 files would
  change. A throwaway worktree with AQA's `pastPaperBank` removed moved the
  73 AQA notes tails, which proves the flag is read.
- **Originality check committed** (`47ea497e`):
  `scripts/check_originality.py` and `scripts/pdf_text.swift`. Corpora for
  AQA, Edexcel A and Edexcel B (45, 40 and 34 question papers) go in the
  gitignored `_working/originality-corpus/`. Its first whole-bank run found
  two live AQA questions too close to real papers, logged as REVIEW-NOTES
  **N-Q25** and not fixed.
- **`.claude/agents/cold-solver.md`** (solve, verify and tag modes, Read
  only, and barred from the data directories and the review sheets), and
  `/edexcel-b-questions`, `/edexcel-b-flashcards` and `/launch-feature`.
- **D67** appended to `docs/audit/DECISIONS.md`.

**Eliot's answers, 2026-10-24 (D68): every recommendation taken.**
- **Staged families** are built. A family in a board's `staged` list is
  validated by its generator and written to no page; practice questions
  and flashcards so far.
- **`EA_PREVIEW=<board>:<family>`** forces a staged family live for one local
  run, and `verify_generated.py` refuses to run under it.
- **B's slugs** are in `boards.json`, and the B URL list is approved.
- **Phase 7 MCQs** mint no URLs and don't count toward the gate.
- **N-Q25:** both AQA questions were rewritten and re-solved cold.

A worktree run proved staging on AQA's flashcards: the decks were validated
and nothing was written. The preview of the same state reproduced the
committed tree exactly, with 0 differences.

Phase 1 (`/edexcel-b-questions`) can start.

### Edexcel B revision notes — Theme 3 (2026-10-20) — LIVE (merged 2026-10-21, `755c56e0`, PR #44)

The fourth and last theme in publishing order (1, 4, 2, 3; D66). **With it,
Edexcel B is complete: all 85 topic pages across Themes 1-4**, and the
site has 251 notes topic pages (`verify_notes_sequence.py`: Edexcel A 87,
AQA 79, Edexcel B 85). Opened 2026-10-20 together with unit 3.1
(`36e103d3`): the hub out of `notes-data/hubs/drafts/`, the group in
`boards.json` between Themes 2 and 4, `EXPECTED_NOTES_DIRS` and
`notes_extras.BOARD_OF_DIR`, the menu entry (desktop and mobile), and a
Year 2 card plus a `hasPart` entry on `revision-notes/index.html`. B's
chain now runs Theme 1 -> 2 -> 3 -> 4.

- **Units 3.1-3.6 written 2026-10-20**, one commit each, every page passing
  `check_overlap.py` against PMT (0.0-0.7%, no copied runs); Eliot's
  answers to each `review/unit-3-1.md` to `unit-3-6.md` applied in the
  commit after it. `expectedTopics` 66 -> 85. Four title-only display
  names in `seo/tools/notes_titles.py` (3.2.2, 3.3.2, 3.4.1, 3.6.3).
- **Diagrams**: `import-quota` drawn and approved for 3.1.4 (`5c195c75`);
  five more are reused: `tariff` (3.1.4), `j-curve` (3.1.5),
  `wage-determination` (3.5.2), `min-wage` (3.5.3) and `lorenz-curve`
  (3.6.1). 3.2.1
  links to 2.1.3 for `product-life-cycle` rather than repeating it. No
  `DIAGRAM PENDING` comment remains anywhere in Edexcel B (checked
  2026-10-20).
- **Revision pass** (`119799fe` to `d6da83a5`, answers `ef94f0c1`): a
  lighter trim than Theme 2's, 18,047 -> 17,669 words; log in
  `review/theme-3-revision-pass.md`.

**Pre-launch jobs, all done 2026-10-20:**
- [x] origin/main checked: it had not moved since Theme 2's merge
  (`ada29e8b`), so there was nothing to merge.
- [x] `datePublished` and `dateModified`: the 19 topic records already
  carried 2026-10-20; the hub record moved from 2026-09-26 (`f5747f7d`).
- [x] Site-wide copy, wording approved by Eliot: the homepage Revision
  Notes card (251 pages, Edexcel A, Edexcel B and AQA) and the "Which exam
  boards are covered?" FAQ answer; on `revision-notes/index.html` the
  intro ("plus all four Edexcel B themes"), the hero topics line (251, was
  232), the Theme 3 card (19 topics, was 0), the JSON-LD description and
  `og:description`.
  The D50-frozen head (title, H1, meta description, canonical) is
  untouched. CLAUDE.md's vocabulary line now says notes cover Edexcel A,
  Edexcel B and AQA.
- [x] Site search: the Theme 3 hub and all 19 topics are in
  `/search-index.json`.
- [x] Previous/next: 2.6.3 -> 3.1.1 and 3.6.4 -> 4.1.1, in both
  directions.

**Open follow-ups** are in "Still open — Edexcel B follow-ups" above.

### Edexcel B revision notes — Theme 2 (2026-10-17 to 2026-10-19) — LIVE (merged 2026-10-19, `ada29e8b`, PR #43)

The third theme in publishing order (1, 4, 2, 3; D66). Opened 2026-10-17
together with unit 2.1 (`f6fcf691`), as a theme cannot open empty: the hub
out of `notes-data/hubs/drafts/`, the group in `boards.json` between
Themes 1 and 4, `EXPECTED_NOTES_DIRS` and `notes_extras.BOARD_OF_DIR`, the
menu entry (desktop and mobile), and a Year 1 card plus a `hasPart` entry
on `revision-notes/index.html`. B's chain now runs Theme 1 -> 2 -> 4.

- **Units 2.1-2.6 written 2026-10-17 to 2026-10-19**, one commit each,
  every page passing `check_overlap.py` against PMT with no copied runs;
  Eliot's answers to each `05-website/drafts/edexcel-b-notes/review/
  unit-2-1.md` to `unit-2-6.md` applied in the commit after it.
  `expectedTopics` 42 -> 66. Six title-only display names in
  `seo/tools/notes_titles.py` (2.1.3, 2.1.4, 2.3.3, 2.4.2, 2.5.2, 2.6.3).
- **Diagrams** (`4acd8855`): `product-life-cycle` (2.1.3) and `long-tail`
  (2.1.4) drawn and approved; Eliot decided against
  `non-price-competition-demand` (2.2.3). 2.4.3 and 2.4.4 reuse
  `comparative-advantage` and `exchange-rates`. No `DIAGRAM PENDING`
  comment remains (checked 2026-10-19).
- **Revision pass** (`2f149324`, answers `ce6c0c1a`): every page trimmed
  by hand, 23,766 -> 22,453 words; log in `review/theme-2-revision-pass.md`.
- **Changes to pages that were already live**, made on this branch:
  N-Q21 resolved on Eliot's instruction (`f1134459`, `6e435b36`) -
  `comparative-advantage.svg` redrawn and the example rewritten
  identically on Edexcel A 4.1.2 and AQA 2.6.2, both diagram flashcards
  and the macro gallery blurb; display maths outside a formula-box now
  scrolls sideways on a phone (`0a842399`, `revision-notes-topic.css`);
  plain-text pointers to Theme 2 units became links on B 1.2.5, 1.5.2,
  1.6.1, 4.1.1 and 4.1.5.

**Pre-launch jobs, all done 2026-10-19:**
- [x] origin/main checked: it had not moved since Theme 4's merge
  (`fec344d2`), so there was nothing to merge.
- [x] `datePublished` and `dateModified` on the Theme 2 hub record and all
  24 topic records set to 2026-10-19, the publish day (`2ad20bdd`).
- [x] `revision-notes/index.html` (`0571837f`, wording approved by Eliot):
  the Theme 2 card's "0 topics" is now 24, the intro says "plus Edexcel B
  Themes 1, 2 and 4", and the hero topics line is 232 (was 208). The
  D50-frozen head is untouched.
- [x] Site search: the Theme 2 hub and all 24 topics are in
  `/search-index.json` (picked up from the hub, no change needed).
- [x] Previous/next: 1.6.4 -> 2.1.1 and 2.6.3 -> 4.1.1, and every link
  between, top and bottom rows agreeing on all 26 pages.

**When the last theme opens (Theme 3):** add its card to the index (Year 2)
and update the topics line (232 today) and the intro sentence. *Done
2026-10-20, see Theme 3 above.*

### Edexcel B revision notes — Theme 4 (2026-10-16 to 2026-10-17) — LIVE (merged 2026-10-17, `fec344d2`, PR #42)

The second theme in publishing order (1, 4, 2, 3; D66). Opened 2026-10-16
by `new_topic.py`'s three steps: the hub out of `notes-data/hubs/drafts/`,
the group in `boards.json` and `EXPECTED_NOTES_DIRS`, `verify_boards.py
--reseed`, the menu entry (desktop and mobile). Theme 4 also has a Year 2
card in the Edexcel B section of `revision-notes/index.html`, and a
`hasPart` entry in that page's JSON-LD.

- **A theme cannot open empty.** `notes_sequence.hub_topics()` stops the
  build when a hub links to no topic, so the opening changes are committed
  together with unit 4.1 (`/edexcel-b-unit 4.1`), not on their own. 4.1.1
  is Spectrum of Competition, `4-1-1-spectrum-of-competition`
  (`05-website/drafts/edexcel-b-notes/theme-4-coverage.md`).
- **Opening also needs a row in `scripts/notes_extras.py` `BOARD_OF_DIR`**
  (the sub-label's board and module); the build fails without it.
  `new_topic.py` now prints it as part of step 3.
- **Unit 4.1 is written (2026-10-16)**: 4.1.1-4.1.5, five pages, awaiting
  Eliot's review (`05-website/drafts/edexcel-b-notes/review/unit-4-1.md`,
  12 questions). 4.1.4 and 4.1.5 carry proposed title-only display names in
  `seo/tools/notes_titles.py` (their full names overflow the 65-character
  ceiling), on the approval list in that sheet. Theme 1's 1.6.4 now links
  forward to 4.1.1, B's chain running in open-theme order. Eliot's answers
  applied the same day (`931147a8`).
- **Unit 4.2 is written (2026-10-16)**: 4.2.1-4.2.3, three pages, awaiting
  review (`review/unit-4-2.md`, 9 questions). 4.2.1 carries a
  `DIAGRAM PENDING: natural-monopoly` marker (optional diagram). 4.2.3 has a
  proposed title-only display name in `notes_titles.py`. Eliot's answers
  applied the same day (`73fbc38d`).
- **Unit 4.3 is written (2026-10-16)**: 4.3.1-4.3.3, three pages, awaiting
  review (`review/unit-4-3.md`, 8 questions). They are shorter than
  planned because Theme 1's 1.5.1 and 1.5.2 already carry the externality
  and tax diagrams; these pages link back. 4.3.3 has a proposed title-only
  display name. Eliot's answers applied the same day (`148b735e`).
- **Unit 4.4 is written (2026-10-16)**: 4.4.1-4.4.4, four pages, awaiting
  review (`review/unit-4-4.md`, 9 questions). No diagrams pending. 4.4.4
  has a proposed title-only display name. The pages don't link to B's
  Theme 2, which isn't open yet. Eliot's answers the same day keep
  everything as written, so no page changed.

- **Unit 4.5 is written (2026-10-16)**: 4.5.1-4.5.4, four pages
  (`037952df`), completing Theme 4's 19 topics; `expectedTopics` 38 -> 42.
  Eliot's answers applied the same day (`85fc60e8`): 4.5.1's slug became
  `4-5-1-risks-and-uncertainty` before it was ever published.
- **Final review pass (2026-10-17)**: the natural-monopoly diagram drawn
  and placed on 4.2.1 (`306ac3b4`), so no `DIAGRAM PENDING` comment
  remains; definitions tightened across nine pages and the two
  scene-setting ones (Market structure, Regulation) removed, on Eliot's
  instructions (`4cb9124c`).
- **Theme 4 is complete and approved (2026-10-17)**: all 19 pages, units
  4.1-4.5, each reviewed by Eliot (`review/unit-4-1.md` to `unit-4-5.md`).

**Pre-launch jobs, all done 2026-10-17:**
- [x] `datePublished` and `dateModified` on the Theme 4 hub record and all
  19 topic records set to 2026-10-17, the publish day (`6359e988`), as was
  done for Theme 1.
- [x] `revision-notes/index.html` (`29844cb2`, wording approved by Eliot):
  the Theme 4 card's "0 topics" is now 19, the intro says "plus Edexcel B
  Themes 1 and 4", and the hero topics line is 208 (was 189). The D50-frozen
  head is untouched.
- [x] Site search: the Theme 4 hub and all 19 topics are in
  `/search-index.json` (checked 2026-10-17; picked up from the hub, no
  change needed).
- [x] origin/main checked 2026-10-17: it had not moved since the branch
  was cut, so there was nothing to merge.

**When the next theme opens (Theme 2):** add its card to the index (Year 1)
and update the topics line (208 today) and the intro sentence.

### Edexcel B revision notes — Theme 1 (2026-09-26 to 2026-10-15) — LIVE (merged 2026-10-15, `782bafd7`, PR #41)

85 Edexcel B (9EB0) topic pages across Themes 1-4 are coming, one unit per
session, from the project pack in `05-website/drafts/edexcel-b-notes/`. This
first session did the plumbing and no content. DECISIONS.md D66 has the reasons.

- **Edexcel B is a notes-only board** (`"notesOnly": true` in `boards.json`):
  notes and nothing else. `board_data.load()`/`groups()` leave it out, so the
  flashcards, glossary, taxonomy and practice-question generators never see
  it; the notes family reads `load_notes()`. Its topic pages' tail has the
  Edexcel B past-papers panel only, and it needs no `questions-data/` record.
- **Themes open one at a time, in publishing order** (1, 4, 2, 3), each
  finished and pushed before the next starts. Theme 1's hub is built; the
  other three are written and wait in `notes-data/hubs/drafts/`, which
  nothing builds. `new_topic.py` refuses an unopened theme and prints the
  three steps that open it.
- **`new_topic.py edexcel-b …`** scaffolds a page: `--slug` for the agreed
  shorter slugs, empty unit panels, the first topic in an empty directory,
  and the hub's stats line now bumped too (for every board).
- **The menu** has Edexcel B → Theme 1, and the old "Edexcel" group heading
  reads "Edexcel A" (Revision Notes and Practice Questions, desktop and
  mobile). 192 `Text-Change:` trailers.
- **Units 1.1 and 1.2 are written (2026-09-27)**: 1.1.1-1.2.5, eight
  pages, awaiting Eliot's review (`05-website/drafts/edexcel-b-notes/review/`,
  `unit-1-1.md` and `unit-1-2.md`). The temporary one-page-spine
  declarations are all gone: `MALFORMED_NOTES_PAGES` is empty again and
  `EXPECTED_NOTES_SPINES` is back to 1.
- **Theme 1 is complete and approved (2026-10-15)**: all 23 pages,
  units 1.1-1.6, each reviewed by Eliot (`05-website/drafts/edexcel-b-notes/
  review/unit-1-1.md` to `unit-1-6.md`). Two revision passes followed:
  conciseness and point &rarr; chain of analysis &rarr; evaluation for
  impact topics, then simpler examples and a maths formatting fix on
  1.6.1-1.6.3 (log: `review/theme-1-revision-pass.md`). The two new
  diagrams, `market-map` (1.3.6) and `break-even-chart` (1.6.2), are
  placed; no `DIAGRAM PENDING` comment remains.
- **Publish dates**: `datePublished` and `dateModified` on all 23 topic
  records and the Theme 1 hub were set to 2026-10-15, the publish day, as
  Eliot asked. Earlier dates were writing dates for pages that were never
  live.
- `/edexcel-b-unit` now writes to the Theme 1 house style (`d141bf07`).

**Hub wording approved by Eliot on 2026-09-27**: every line of
`05-website/drafts/edexcel-b-notes/setup-approval-list.md`, all four hubs,
including the closing box keeping its em dash as reused Edexcel A copy.
Pages are written one unit per session with `/edexcel-b-unit X.Y`
(`.claude/commands/edexcel-b-unit.md`).

**Pre-launch jobs, all done 2026-10-15:** every page written and approved;
the Edexcel B section on `revision-notes/index.html` (`76bbe145`, wording
approved by Eliot; the D50-frozen title, H1, meta and canonical are
byte-identical, and "Edexcel Economics" became "Edexcel A Economics" to
match the menu); B topics in site search (`e25b9c84`: notes-only rows come
from the hub, and a `quiz` flag on each `dirs` row stops practice links);
origin/main merged in (PR #40's corrections). **When the next theme
opens:** add its card to the index (Themes 1-2 Year 1, 3-4 Year 2) and
update the topics line (189 today); search picks it up automatically.
**After launch:** twin links
(`notes_twins.board_of_dir` treats any `edexcel*` directory as Edexcel A and
needs fixing first) and a B glossary, both deferred on purpose.

### Calendly retired — self-booking replaced by enquiry-first (2026-09-25) — LIVE (merged 2026-09-25, `7aec6877`, PR #39)

Eliot is close to full for 2026-27 with only a few weekly slots left, and
prospects kept self-booking intro calls he then had to cancel. The flow is now
enquire first: the visitor sends the Formspree enquiry (or emails), Eliot
replies within 24 hours with real availability, and offers the free 15-minute
call by email only if there is a fit. No fit means the waiting list.

`tutoring.html`'s `#booking` section is now an enquiry block. **The id is
unchanged and must stay** — `about.html`, `contact.html`, `faq.html` and four
buttons on the page itself deep-link to `/tutoring.html#booking`, and a
published URL is permanent. The primary button is an ordinary
`.enquire-button`, so it opens the modal that already existed rather than
adding a second form; beside it is a `mailto` with a `Tutoring enquiry`
subject, which is the JS-off route and needs no script.

`openModal()` gained a second argument. The modal heading is literally
"Enquire About &lt;package&gt;", so `data-package="General enquiry"` would have
read "Enquire About General enquiry". The optional `data-modal-title` splits
the two: Formspree still receives `General enquiry` (useful in the inbox), the
heading reads "Enquire About Tutoring", and the three pricing cards, which
carry no such attribute, fall back to the package name exactly as before.

**Everything Calendly is gone from the live site except the privacy notice.**
The two preconnects, the `widget.css` head comment, the inline lazy loader,
the widget div and its fallback link, the `.calendly-inline-widget` /
`.calendly-fallback` CSS, and `track.js`'s `intro_call_booked` postMessage
listener. That GA4 event is retired, not renamed — its history stays in the
property and the tutoring funnel now ends at `generate_lead`, which the
enquiry form already fired. `privacy.html` deliberately keeps Calendly as a
processor: Eliot may still send a booking link privately, so the wording moved
from "bookings are handled here" to "a link may be sent to you by email".

**The CTA sweep was the bulk of the diff.** 330 generated pages plus
`index.html` (×2) and `marking.html` carried a "Book a Free Intro Call" button
pointing at `/tutoring.html` — a button promising something the page can no
longer do. The four sources (`build_questions.py` ×3,
`build_past_paper_questions.py`, the seven `notes-data/hubs/*.html`) now say
"Enquire About Tutoring". This *helps* `seo/07b-link-decisions.md` §5 rather
than breaching it: 444 of 455 tutoring links used to read the one anchor
string, which that decision names as a monoculture to avoid deepening.

`faq.html` lost one question. "How do I get started with tutoring?" and "What
is the Calendly booking for?" answered nearly the same thing once booking was
gone, so they were merged into the first, in both the visible accordion and
the FAQPage JSON-LD. **`#tutoring-intro-call` no longer resolves** — it lands
at the top of `faq.html` rather than 404ing, since it was only ever a
fragment. Nothing internal linked to it; `search-index.json` regenerated
itself.

Deliberately untouched: the ~170 revision-notes pages whose tail reads "in a
free 15-minute intro call" (no Calendly link, still true) and
`scripts/notes_extras.py` that writes it.

### Form spam hardening — Turnstile on both Formspree forms (2026-09-15) — LIVE (merged 2026-09-15, `a7a303bc`, PR #37)

An automated scanner found both forms from ~13 September and began fuzzing
them with SQL-injection probes — one poisoned parameter per request, every
other field empty, all seven `preferred_days` boxes ticked, which is a direct
POST to the endpoint rather than a browser. Nothing could be breached (no
database; Pages serves static files and Formspree relays email); the risk was
the free plan's 50 submissions a month being eaten, which drops a real enquiry
silently.

Both endpoint IDs rotated — `xblapyky` and `mqadgbbw` are hardcoded in the bot
and are burned — and Cloudflare Turnstile added to both new forms, verified
server-side by Formspree with the Secret Key, which is the only defence a
direct POST cannot walk past. Explicit rendering via the new shared
`js/components/turnstile-form.js`, because the tutoring form sits in a
`display:none` modal and a widget rendered into a zero-layout box comes up
blank; the widget is reset in each page's `finally` block because tokens are
single-use. `ea:lead` still fires only on `response.ok`, so GA4 is untouched.

**This is the site's one progressive-enhancement exception** — both forms now
need JavaScript, recorded in CLAUDE.md with the reasoning. `verify_page_shell`
carries it: the two scripts in `EXTRA_SCRIPT_PAGES`, the root family's tail
count reseeded 1 → 2.

### Past-paper search — board cascade in the filters (2026-08-27) — LIVE (merged 2026-08-27, `8fbb6ba5`, PR #35)

The master page's Board select now drives Qualification, Theme / area,
Paper section and Topic (still-valid choices kept, the rest reset); with
no board chosen, Topic and Theme / area group under `<optgroup>`s
labelled from `data.boards`, Section C and AS Level sit under Edexcel's
name, and picking a topic or theme adopts its board. The cascade is
gated to pages with a live Board control: the pre-filtered hub, theme
and topic pages keep their flat lists byte-for-byte (a hub's visible
Theme / area select deliberately still does not narrow Topic — pinned by
test; lift the gate in `question-search.js` if ever wanted).
`optionList()` stays the single option builder. One file plus its tests;
`scripts/test_question_search.js` now runs the component's real `init()`
against the real payloads through a minimal fake-select harness, slicing
the component file down to its `boot` marker.

### Tutoring page SEO pass (2026-08-26) — LIVE (merged 2026-08-26, `0bcac57c`, PR #33)

Meta description 195 → 159 chars, two visible FAQ boxes with byte-synced
FAQPage JSON-LD twins, the full Person schema on tutoring + about, three
descriptive in-body anchors from other pages, 30 em-dash swaps in Eliot's
own copy (the testimonial quotes keep theirs), verify_seo assertions 21–23,
search index rebuilt. D63: the tutoring GSC freeze is lifted — the ~22
September comparison is directional only. The 75-char title is deliberate;
the FAQPage block earns no rich result and is kept anyway.

### Notes family consistency — the two diagram galleries (2026-08-25) — LIVE (merged 2026-08-25, `0bad0c88`, PR #32)

Both hand-written diagram galleries joined the D61 reading design (topic
sheet + rewritten `revision-notes-diagrams.css`), content byte-identical.
macro-application was moved and then REVERTED byte for byte on Eliot's
instruction over a paint fault no headless engine reproduces —
`revision-notes-textbook.css` now serves that one page only. The record:
`_archive/working/notes-family-consistency/` and branch
`record/macro-application-attempts` (on origin, kept unmerged). D62.

### Notes topic-page redesign — the 166 pages (2026-08-25) — LIVE (merged 2026-08-25, `53532083`, PR #30)

The generated topic pages left the 2025 textbook card for a reading layout:
`css/pages/revision-notes-topic.css`, definition cards and table regions
derived at build time, framed no-JS tap-to-enlarge diagrams,
`js/components/notes.js` as the family extra script. Economics content
byte-identical. Eliot's editing guide: `docs/EDITING-NOTES.md`. D61.

### Past-paper question bank — page gate 4 → 2 (2026-08-24) — LIVE (merged 2026-08-24, `fc2400a6`, PR #27)

`GATE` fell 4 → 2: 46 new topic pages (the bank 81 → 127), real indexable
URLs replacing JS-only query-string filters on 92 linking pages. The gate
may fall and never rise; the bank mints no slugs. D60.

### Accessibility & progressive enhancement pass (2026-08-24) — LIVE (merged 2026-08-24, `745f9cb2`, PR #26)

Five phases, one commit each: FAQ accordion → native `<details>`; the
mobile-nav drawer (the baked `#mobileNav`, moved to body level by `nav.js` —
load-bearing); flashcard-player accessible names and flip announcements; the
contrast darkenings pinned by the new `verify_contrast.py`; reduced motion
and site-wide print. The EXAM TIP/EVALUATION chips were deferred to the
notes redesign, which closed them.

### Site-wide search — header box + overlay (2026-08-24) — LIVE (merged 2026-08-24, `8b329f1e`, PR #24)

The 9th generator (`build_search_index.py`, deliberately last) +
`/search-index.json`, the baked "Search…" box on all 463 pages (190
Text-Change trailers), the overlay component, script tail four → five. The
index schema is declared twice on purpose; `scripts/test_site_search.js`
holds the two halves together. D59.

### Topic-page tail redesign — the 166 notes pages (2026-08-23) — LIVE (merged 2026-08-24, `32c0bacb`, PR #23)

The six-box tail became four derived blocks (related topics → "Carry on
with this topic" → slimmer author box → one services sentence with real
anchor text); the legacy tail was stripped from the 166 slices (5,567
deletions, 0 additions); the past-paper line is computed from the bank's
SOURCE files. `dateModified` deliberately not refreshed. D58.

### Tutoring enquiry form — board, year, enquirer, days (2026-08-23) — LIVE (merged 2026-08-23, `ab255c6`, PR #21)

The modal gained exam board, school year, who-is-asking and preferred-days
fields, named to read as labels in the Formspree email. `novalidate` is
gone — do not put it back without writing the validation it implies; the
dialog stacks above the cookie bar; `ea:lead` still carries no field values.

### Performance pass — MathJax, fonts, hubs, images (2026-08-23) — LIVE (merged 2026-08-23, `367297b`, PR #19)

MathJax only where a body has maths; fonts self-hosted under `/webfonts/`
(Open Sans retired for Source Sans Pro, Eliot's call); the two big board
hubs bake 20 cards + per-board payloads; Calendly lazy-loaded; WebP twins
for every diagram PNG and the five photos. Live Lighthouse: home 91 → 100,
tutoring 56 → 98. The numbers: `seo/20-performance-pass-2026-08-23.md`.

### Analytics consent — hard gate + cookie bar (2026-08-23) — LIVE (merged 2026-08-23, `83ae353`, PR #17)

gtag.js loads only after "That's fine" on the bottom-of-page bar
(`localStorage["ea-consent"]`); privacy.html carries the only change
button. From this date GA4 counts consenting visitors only — never read
the drop as lost traffic. D57.

### Maintainability — one build, derived counts, tests (2026-08-23) — LIVE (merged 2026-08-23, `95cf271`, PR #16)

`scripts/build.py` (the one build command), the generator list declared
once in `site_layout.py`, `prettier_util.py` with `.prettierignore` /
`.prettierrc`, `--reseed` on the pinned verifiers, `page_shell.py` owning
the page skeleton, `scripts/tests/` in CI, and the opt-in `.githooks/`.
No published page changed.

### Hub redesign — the 12 board hubs (2026-08-23) — LIVE (merged 2026-08-23, `dedd5d1`)

The JS-only accordions on the notes and practice board hubs became an
always-open topic index (the shared `.resource-index-*` block in main.css).
`notes_sequence.py` reads the hubs' link order and anchor text — moving the
spec code outside the `<a>` renames every prev/next label on the site. D56.

### GA4 conversion tracking (2026-08-22) — LIVE (merged 2026-08-22, `bb18d6d`)

`js/components/track.js` fires begin_checkout, purchase, generate_lead,
intro_call_booked, sign_up and cta_click on every page; the file's header
comment is the authoritative event list. GA4 admin done 2026-08-22; the
custom dimensions exist only from that date.

### Revision notes on-page SEO (2026-08-21) — LIVE (merged 2026-08-22, `ee24918`)

Topic-first titles and descriptions on 166 topics + 7 hubs, contents
lists, twin-board links (`scripts/notes_twins.py` — a written-down table,
deliberately), byline and Person author, 508 internal links, verify_seo
assertions 15–20. The dates are STORED in `notes-data/`, refreshed only by
`seo/tools/rewrite_notes_meta.py`. D53–D55.

### Previous / next topic navigation (2026-08-21) — LIVE (merged 2026-08-21, `c0a80f6`)

A derived prev/next row at each end of the 166 topic pages; two chains,
never joined (Edexcel themes 1→4, AQA micro→macro). `notes_sequence.py`
derives it, `verify_notes_sequence.py` holds its three sources together.
Below 768px the top row shows captions only — re-measure before
"restoring" the titles.

### SEO / indexing — Search Console index audit (2026-08-21) — REPORT ONLY (committed `bb020d8`)

746 URLs reconciled against the export: 66.5% of HTML indexed; the 26
"noindex" verdicts are stale crawls; "Discovered — currently not indexed"
is a queue, not a defect. `seo/tools/gsc_reconcile.py` reproduces the
whole audit from one command; the reports are `seo/11–13`.

### 0. About + Contact + site finishing pass (2026-08-16) — LIVE (merged `437dc7e`)

The last two unrevamped pages rebuilt around trust (quick-facts strip, My
Story, testimonials, one Name field, the `_subject` dropdown, honeypots),
"within 24 hours" unified on faq, LinkedIn into structured data sitewide.
The closing session of the overhaul.

### 1. Resource unification, Phases 1–4 (2026-08-15) — LIVE (merges `d0fdcaf`, `2295213`, `1e8dfed`, `f537312`)

One design language and full cross-linking across flashcards, practice
questions, past papers and revision notes. The shared component set is the
`.resource-*` block at the END of css/main.css — reuse it, don't fork it.

### 2. Marking page + payment journey (2026-08-15) — LIVE (merged `d4be06b`)

Four packages with direct Stripe buttons (all 8 links verified end to
end), the two real example PDFs, confirmation.html rebuilt around one job.
marking.html ranks #1 for "Economics paper marking" — its head stayed
byte-identical. Bundles are pay-once, submit-over-time: six places state
it and move in lockstep.

### 3. Home page revamp (2026-08-14) — LIVE (merged `f53b7fe`)

Hero H1, six free-resource cards with measured numbers (derived 2026-08-14
— update the copy by hand as content grows), four board tiles, Meet Your
Tutor, static testimonials, the Kit newsletter form (9803307).

### 4. Tutoring page SEO rework (2026-08-14) — LIVE (merged `e09cdef`)

Rebuilt around the current offer — 1-to-1 £65/hr, groups of 2–4 at £35/hr
per student — with Service/FAQPage JSON-LD and the Calendly booking
section (`id="booking"`, the deep-link target other pages use).

### 5. Flashcards — LIVE (2026-08-15)

Six decks with Leitner spaced repetition in localStorage. The `premium`
flag exists because the repo is public and client-side paywalling is not
sufficient; the 84 hand-drawn SVGs are referenced only from
`flashcards/data/*.json`. Full record: `_archive/FLASHCARDS_PROGRESS.md`.

### 6. Glossary & formulae — LIVE (merged 2026-08-09)

325 terms and 34 formulae at `/revision-notes/glossary/`, KaTeX
pre-rendered at build time. Definitions are the notes' own words, held by
`verify_glossary.py`; the two declared exceptions are
`glossary-data/authored.json` and `curation.json`'s rewrites. Working
records: `_working/glossary/`.

### 7. Past paper question bank — LIVE (2026-08-13)

Real exam questions reproduced verbatim (Edexcel A + AQA; Section A
permanently out of scope) — never sharing a data path with the original
practice bank. PDF work is Swift + PDFKit;
`strip_source_attributions.py` must always report 0. Full record:
`_archive/PAST-PAPERS-PROGRESS.md`.

### 8. Free practice questions — LIVE (2026-08-01)

1,267 original MCQs across all 166 topics, every question re-solved cold
from the stem, originality checked mechanically each batch (0 exact and 0
near-duplicate stems against the real papers). The standard:
`docs/QUESTIONS_GUIDE.md`; the batch record and failure modes:
`docs/QUESTIONS_PROGRESS.md`. A written-response pilot was built and
reverted on review — recoverable from `be4d7b8`.

### 9. Notes consistency & enrichment pass — LIVE (2026-08-01)

The 166 topic pages made structurally consistent (0 generic Exam
Preparation sections, 0 inline-styled CTAs, 0 dead wrappers) and 31
teaching components added across 34 pages, every figure recomputed. The
removed text is archived verbatim. Under the same heading: the July
site-wide scan (12 of 15 findings fixed) and the N-Q1–N-Q20 corrections
(16 applied).
