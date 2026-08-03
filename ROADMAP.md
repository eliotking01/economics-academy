# ROADMAP

Planned and intended work. Referenced from `CLAUDE.md`.

**What belongs here:** things you intend to build or change — new content, new
pages, features, redesigns, deliberate refactors.

**What belongs in `REVIEW-NOTES.md` instead:** things that are already wrong —
broken links, inconsistencies, accessibility faults, open economics content
errors. Findings, not intentions.

---

## Now

- **Glossary & formulae.** One page per exam board at
  `/revision-notes/glossary/`, generated from the notes' own definitions.
  In progress on `feature/glossary` — live state in
  `_working/glossary/PROGRESS.md`.

## Next

_Nothing recorded yet._

## Someday

- **Flashcard / self-test mode on the glossary.** Explicitly out of scope for
  v1. The data model already supports it: `glossary-data/terms.json` holds term,
  definition and source separately, so a test mode needs no re-extraction.
- **Migrate the revision notes from MathJax to KaTeX.** The glossary
  pre-renders KaTeX at build time; the 125 LaTeX-bearing notes pages still load
  MathJax 3 from a CDN. Until they converge, the same formula looks slightly
  different in the two places. Converging would also drop a CDN dependency and
  make formulae render with JavaScript off site-wide.
- **A downloadable PDF glossary per board.** Deliberately not in v1 — it needs a
  headless browser or a PDF library on a repo with no build dependencies, and
  becomes a second artefact that drifts from the page. The print stylesheet
  covers Cmd+P. Revisit if students ask for it.
