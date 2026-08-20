# ROADMAP

Planned and intended work. Referenced from `CLAUDE.md`.

**What belongs here:** things you intend to build or change — new content, new
pages, features, redesigns, deliberate refactors.

**What belongs in `docs/REVIEW-NOTES.md` instead:** things that are already wrong —
broken links, inconsistencies, accessibility faults, open economics content
errors. Findings, not intentions.

---

## Now

- **Merge `feature/glossary`.** Built and verified; merging is what publishes
  325 terms and 34 formulae across three pages. Deliberately left manual,
  because `main` auto-publishes. Before merging, check the economics of the 74
  authored definitions in `_working/glossary/authored-review.md` — they are the
  only entries on the site that are not the notes' own words.

- **Interactive flashcards** (`/flashcards/`), in progress on
  `flashcards-feature` — see `docs/FLASHCARDS_PROGRESS.md`. Supersedes the
  "flashcard mode on the glossary" idea that used to sit under Someday: the
  glossary's extracted terms (`glossary-data/terms.json`) are folded in as the
  cross-check source for definition cards.

## Next

_Nothing recorded yet._

## Someday
- **Migrate the revision notes from MathJax to KaTeX.** The glossary
  pre-renders KaTeX at build time; the 125 LaTeX-bearing notes pages still load
  MathJax 3 from a CDN. Until they converge, the same formula looks slightly
  different in the two places. Converging would also drop a CDN dependency and
  make formulae render with JavaScript off site-wide.
- **A downloadable PDF glossary per board.** Deliberately not in v1 — it needs a
  headless browser or a PDF library on a repo with no build dependencies, and
  becomes a second artefact that drifts from the page. The print stylesheet
  covers Cmd+P. Revisit if students ask for it.
