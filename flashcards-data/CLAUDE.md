# flashcards-data/

Hand-authored source of truth for `/flashcards/`. Excluded from publishing.
`scripts/build_flashcards.py` writes the pages and the runtime payloads in
`flashcards/data/` — **never hand-edit those; re-run the script.**

One file per board per theme: `<board>/<theme>.json`.

## Adding one (the workflow; the rules below are the authoring standard)

1. **A card belongs to an existing deck and an existing notes topic.** Open
   `<board>/<theme>.json` for the topic's board and theme; the topic must have
   a notes page (`notes-data/topics/<dir>/<slug>.*`) because `subtopic` is that
   slug and every card links to the page that teaches it.
2. Append a card object to `cards`, copying the nearest sibling for the
   shape: `id` (`<board>-<spec-with-dashes>-<type>-NN`, unique across the
   deck), `specCode` (dotted), `topic` (the unit heading string the siblings
   use), `subtopic` (the notes slug), `cardType`, `front`/`back` (HTML, card
   prose), `svgRef`, `difficulty`, `tags`, `premium`, `acceptableAnswers`.
   Authored order does not matter — the build sorts by `specCode`.
3. A diagram card needs its SVG verified against the ground-truth PNG in
   `images/diagrams/` and `docs/DIAGRAM_STYLE.md` (rule 4 below) before it is
   presented for approval.
4. `python3 scripts/build.py` runs `build_flashcards.py` (`validate_deck()`
   rejects an unknown board/theme pair, a missing field or a duplicate id)
   and writes the deck page and `flashcards/data/<deckId>.json`. There is no
   `--check` for this generator; the build is the check.
5. Suite (`/verify`), commit, then `python3 scripts/build.py --sitemap` and
   commit. No verifier literal needs bumping: the deck count is derived from
   this directory.

A new **deck** (a new board/theme pair) is bigger than a card: the pair must
be a group in `boards-data/boards.json` (`build_flashcards.NOTES_DIRS` is
derived from it), and the deck file needs every deck-level field — follow an
existing deck file and say so in the commit.

## Rules

1. **Never edit existing written content on the site without explicit approval
   in chat.** You may always ask.
2. **All card content must be exam-board accurate.** Where Edexcel A and AQA
   define or treat a concept differently, create **separate board-specific cards
   and diagram variants** — do not write one card that hedges across both.
3. Card text is card-optimised prose, cross-checked against
   `glossary-data/terms.json` and the specifications. Where a notes chip
   definition is already tight, reuse it verbatim and tag
   `origin="notes-verbatim"`.
4. **Every diagram card's SVG must be verified against the ground-truth PNG in
   `images/diagrams/`** — visually inspected, never trusted by filename — and
   against its caption in the notes. It must follow `docs/DIAGRAM_STYLE.md` and
   pass an SVG-to-PNG headless render check before being presented for approval.
5. Suspected notes errors found while writing cards go in
   `docs/CONTENT_ISSUES.md`. **Logged for approval, never fixed unilaterally.**
6. Present significant decisions as options with a recommendation, and wait.

## The freemium constraint

`premium: true` cards **never enter the public payloads** — `build_flashcards.py`
excludes them. That flag exists so premium content can later be withheld without
restructuring the data model.

**This repo is public.** Client-side paywalling is not sufficient and nothing
here may assume it is. Real gating will need a lightweight auth/delivery layer
serving premium JSON from outside this repo; ultimately premium content cannot
live in a public repo at all.

`js/components/flashcards.js` is progressive enhancement over static sample
cards, and fetches the deck JSON at runtime — the same pattern as
`question-search.js`. Leitner spaced repetition state lives in localStorage.

Hand-authored SVGs for diagram cards live in `images/diagrams/svg/`. They are
referenced only from `flashcards/data/*.json`, which is why a tool that greps
HTML reports them as unused.

The full build and decision record: `_archive/FLASHCARDS_PROGRESS.md`
(archived 2026-08-26; its one live leftover is `docs/CONTENT_ISSUES.md` #37).
