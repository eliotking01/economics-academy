# PROJECT-LOG

What the two large pieces of work on this site did, and what they left flagged.

Both are **complete**. This file replaces eight planning documents that were
written for them, delivered in full, and then had nothing left to say — `RECON.md`,
`PLAN-mechanical.md` and the six `PLAN-enrichment-*.md` batch plans. They are in
git history if the detail is ever wanted.

Referenced from `CLAUDE.md`.

---

## The two projects, in one line each

| Project | Branch | State |
| --- | --- | --- |
| **Notes consistency & enrichment pass** | `notes-consistency-pass` | Complete. 184 files changed, merged |
| **Free practice questions** | `feature/topic-questions` | Complete. **Pushed, not merged** — `main` auto-publishes, so nothing is live |

---

## 1. Notes consistency & enrichment pass

Two jobs in one branch: make the 166 topic pages structurally consistent, then add
a small number of teaching components where a page genuinely needed one.

### The mechanical half

| | Before | After |
| --- | ---: | ---: |
| Generic "Exam Preparation" sections | 87 | **0** |
| Topic pages with exactly one `.notes-cta` | — | **166 / 166** |
| Inline-styled CTA blocks | 89 | **0** |
| Dead `chart-container` wrappers | 211 | **0** |
| `formula-box` divs without `prettier-ignore` | 28 | **0** |
| Unescaped `<` in note text | 32 | **0** |
| `<b>` / `<i>` / `<u>` in notes | 0 | **0** |

The removed Exam Preparation text is archived verbatim in
`docs/removed-exam-preparation-sections.md`, in case any of it is worth re-siting
as an in-context exam tip.

### The enrichment half

**31 components across 34 of 166 pages.** 132 pages received nothing, by design —
the house rule is a maximum of two components per page and 80% of pages carrying
none. Worked examples and exam tips only; every figure verified by recomputation.

The per-component inventory is `_archive/NEW-CONTENT-LOG.md`.

### Verification at the end

176/176 pages parse; 3,863 internal refs with 0 broken; **0 markup losses** since
the Exam Prep removal; visible text unchanged on every commit that was supposed to
leave wording alone. Components confirmed rendering in headless Chrome.

**One wording change was made in the whole pass** — a single word on
`3-4-4-oligopoly`, on explicit instruction, correcting "five" to "three" in a
concentration-ratio sentence.

---

## 2. Free practice questions

A bank of original multiple-choice questions, one set per topic page, built over
thirty batches.

| | |
| --- | ---: |
| Topics | **166 of 166** |
| Questions | **1,267** |
| Answer letters | A 320, B 358, C 331, D 258 |
| Skills | applied-reasoning 790, definition-in-context 247, data-table 127, calculation 103 |
| Difficulty | foundation 155, standard 950, stretch 162 |
| Sketch to solve | 38 |

| Board / theme | Topics | Questions |
| --- | ---: | ---: |
| AQA Microeconomics | 54 | 401 |
| AQA Macroeconomics | 25 | 209 |
| Edexcel Theme 1 | 22 | 166 |
| Edexcel Theme 2 | 24 | 198 |
| Edexcel Theme 3 | 20 | 148 |
| Edexcel Theme 4 | 21 | 145 |

**How it works.** `questions-data/<board>/<spec>.json` is the single source of
truth; `scripts/build_questions.py` validates it and writes the pages, the five
board indexes, the hub and the sitemap block, so the visible HTML and the JSON-LD
cannot drift. Question pages use `css/pages/quiz.css`; the hub and indexes use
`css/pages/practice-questions.css`.

**Every one of the 1,267 questions was re-solved cold from the stem alone**, in the
batch it was written in, and diffed against the recorded key. That step found real
defects and should be the last thing anyone drops.

**Originality was checked mechanically every batch** — shingled against the AQA and
Edexcel past-paper corpora, against the rest of the bank, and by comparing numeric
option sets against option blocks extracted from the papers.

The authoring standard is `QUESTIONS_GUIDE.md`. The batch-by-batch record, the
twin maps and the nine recurring failure modes are in `QUESTIONS_PROGRESS.md` —
that file is worth keeping for anyone extending the bank, because §8 (cross-board
duplication) and §9 (concept-grep) decided the shape of every batch after the
twelfth.

---

## 3. Site-wide scan, 31 July 2026

A separate sweep across the commercial pages, past papers, hubs, CSS and JS —
everything the enrichment pass did not cover. **12 of 15 findings fixed**,
including 55 keyboard-inaccessible accordions, heading-level skips on 12 pages,
`lang="en"` on 22 pages, and 284 `target="_blank"` links without `rel`.

Three were left: dead Edexcel B mark-scheme links (the site owner was fixing them),
`.notes-container` defined in two stylesheets, and filename outliers.

---

## 4. Notes corrections, 1 August 2026

Twenty findings were raised while writing the question sets, logged as N-Q1 to
N-Q20 in `REVIEW-NOTES.md`, and the site owner decided each one. **Sixteen were
applied**: a reversed sentence about the Claimant Count, an Edexcel spec code cited
on an AQA page, the IMF's role in fixed exchange rates, a US term, NAFTA→USMCA,
twelve typos, figure renumbering on twelve pages, six over-claiming spec alerts cut
back to what their bodies teach, the LRAC envelope stated precisely, and six pages
that had promised concepts their bodies never delivered.

**Two corrections to the findings themselves** are worth carrying forward: the
N-Q10 figure-number scan reported one page that was not broken (`1-5-11`, whose
`2a`/`2b` captions defeated the regex) and missed one that was (`2-5-1`). Any
re-run must allow for the lettered caption form.

**One question was removed from the bank** — `4.1.9` Q8, along with the over-claim
it depended on. That is why the total is 1,267 rather than 1,268.

---

## What remains flagged

Nothing here blocks anything. Everything needs an explicit instruction before a
page is touched, per `CLAUDE.md`.

### Economics content

| Item | Where | What it needs |
| --- | --- | --- |
| **N-Q8, three pages** | `1-4-2` regulatory capture; `2-2-2` the role of expectations; `2-5-4` sustainable development | New prose. None survives in `raw-notes/`, and **each is tested by a live question**, so cutting the claims would strand them. The only substantive item on this list |
| **N-Q7** | `2-6-5` HDI figures | Dated. Left by choice |
| **N-Q11** | `2.4.1` and `2.4.2` | The two pages share 55 ten-word runs; roughly a third of 2.4.2 repeats 2.4.1. Restructuring. Left by choice |
| **N1** | Two multiplier formulas | A leading space inside `\text{ Injection}`. Cosmetic; confirmed as authored, left deliberately |
| **N6** | `1-2-3` elasticities | The midpoint formula was removed with an Exam Preparation section and is now nowhere on the site. **Decided: leave it out** — Edexcel uses the original-value method and the page's worked example agrees |
| **C4** | `2-2-3`, `1-5-6` (AQA) | Both cross-reference Edexcel theme numbers that do not exist in the AQA specification |
| **C5** | `2-1-2` | Confirm the unemployment-rate denominator matches the ONS/ILO definition given a few lines above |

### Accessibility and performance

| Item | Impact | Fix |
| --- | --- | --- |
| **`navPanel` `aria-hidden`** | The only accessibility failure left on any page. Holds every page at 96 rather than 100 | `inject-templates.js` builds `#navPanel` with `aria-hidden="true"` while its links stay in the tab order. Toggle `inert` (or `tabindex="-1"`) alongside it in `openNav`/`closeNav` |
| **Breadcrumb contrast** | `css/main.css:3183` — a `#2a5c8d` link against `#7f888f` text is 1.9:1, and the text is 3.6:1 on white, under the 4.5:1 AA floor | `css/pages/quiz.css` already diverges correctly: underlined links, darkened separator. Worth matching site-wide |
| **Web-font layout shift** | CLS 0.078 on a notes page, 0.154 on a questions page, both above the 0.1 threshold. The largest remaining Performance cost | Self-host the three families with `size-adjust`, or preload the woff2 the fold needs |

### Housekeeping

- **`css/main.css` fails `prettier --check`** at line 2407, a `box-shadow` list.
  Pre-existing.
- **`.year-header h4` in `css/pages/past-papers-list.css` is a dead selector** —
  that markup has always used `h2`.
- **`404.html`** has no canonical and no Open Graph tags. Defensible for a 404;
  listed so it is a decision rather than an oversight.
- **Prettier** still fails on `revision-notes/index.html` and
  `revision-notes/macro-application/index.html`.

### Decisions waiting on the site owner

- **Merging `feature/topic-questions` into `main`.** The branch is pushed and
  verified; merging is what publishes 1,267 questions, five board indexes and the
  hub. Deliberately left manual.
- **The written-response extension.** A pilot was built — an optional `written`
  array, generator support, a stylesheet block and ten questions across five topics
  — then reverted on review. Recoverable in one command; the commit is titled
  "feat: written-response pilot on five topics".

---

## The documents that remain, and what each is for

| File | Purpose | Still live? |
| --- | --- | --- |
| `CLAUDE.md` | House rules, layout, conventions. Read first | **Yes** |
| `QUESTIONS_GUIDE.md` | The authoring standard for the question bank | **Yes** — needed to extend it |
| `QUESTIONS_PROGRESS.md` | Batch record, twin maps, the nine recurring failure modes | Historical, but the methodology is worth keeping |
| `REVIEW-NOTES.md` | The findings log — every problem found and what was decided | **Yes** — the evidence behind the flags above |
| `ROADMAP.md` | Intended work, as opposed to findings | **Yes** — currently empty |
| `_archive/NEW-CONTENT-LOG.md` | Inventory of the 31 enrichment components | Historical |
| `docs/revision-notes-audit.md` | The SEO and accessibility audit already applied | Historical |
| `docs/removed-exam-preparation-sections.md` | The 87 removed sections, verbatim | Archive |

**Deleted as redundant**, all delivered in full before this file replaced them:
`RECON.md`, `PLAN-mechanical.md`, `PLAN-enrichment-aqa-micro.md`,
`PLAN-enrichment-aqa-macro.md`, `PLAN-enrichment-edexcel-theme-1.md`,
`PLAN-enrichment-edexcel-theme-2.md`, `PLAN-enrichment-edexcel-theme-3.md`,
`PLAN-enrichment-edexcel-theme-4.md`.

---

## 5. Glossary & formulae, 3–4 August 2026

Every definition and formula a student needs, one page per exam board, at
`/revision-notes/glossary/`. Branch `feature/glossary`. **Built and verified;
not merged**, so nothing is live.

| | |
| --- | ---: |
| Terms | **325** |
| …Edexcel A / AQA | 269 / 290 |
| Formulae | **34** |
| …Edexcel A / AQA | 22 / 31 |
| Extracted verbatim from the notes | 251 |
| Written for the glossary | 74 |

**How it works.** `scripts/extract_glossary.py` reads the 166 topic pages and
writes `glossary-data/terms.json`; `scripts/build_glossary.py` renders the three
pages, owns its `sitemap.xml` block and runs Prettier over its own output, so
regenerating is byte-identical. Formulae are pre-rendered with KaTeX at build
time, so the pages carry no maths JavaScript and work with JavaScript off.

**The rule, and its one exception.** Definitions are the notes' own words,
lifted verbatim. `scripts/verify_glossary.py` re-reads each notes page and fails
if a shipped definition is no longer in it — the check is independent of the
extractor, and was tested by tampering with a definition. The exception is
`glossary-data/authored.json`: 74 definitions written to fill gaps the notes
never covered, tagged `origin="authored"` through to the page, exempt from that
check and counted separately so the exemption stays visible.

**Judgement is kept out of the extractor** and in `glossary-data/curation.json`,
which the scripts only read — the same split as `tags.json` against
`taxonomy.json`. It holds the stop-list of rhetorical chip labels, merges,
display names, and which sources to prefer or exclude.

### What it found in the notes

- **G3, fixed:** two AQA formulae wrote `%` unescaped. `%` begins a comment in
  TeX, so they rendered broken on the live notes pages too. Three characters.
- **Allocative, productive and dynamic efficiency had no definition anywhere.**
  On six market-structure pages the chip introduces a Yes/No verdict about that
  structure. Approving the two efficiency tables fixed all three.
- **The four marginal propensities were undefined** while four multiplier
  formulae depended on them. The multiplier tables supplied them.
- **G1 and G2 remain open** — `2-1-3-employment-unemployment` has LaTeX but
  never loads MathJax, and `.formula-box` has no CSS rule at all.

### Still flagged

- **The 74 authored definitions need their economics checked** —
  `_working/glossary/authored-review.md`, 132 wordings.
- **Links from the 166 topic pages** were deliberately deferred (P3a/P3b in
  `_working/glossary/integration-proposals.md`). The nav item, the hub button
  and the three gallery pages are done.
- Sections C, D and F of `review-decisions.md` were never answered and took
  their defaults: 16 heading-derived names, 33 chips without a colon, 6
  definitions that run on into a list.

Live state: `_working/glossary/PROGRESS.md`.
