# flashcards-data/

Hand-authored source of truth for `/flashcards/`. Excluded from publishing.
`scripts/build_flashcards.py` writes the pages and the runtime payloads in
`flashcards/data/` — **never hand-edit those; re-run the script.**

One file per board per theme: `<board>/<theme>.json`.

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

Live state and the full decision record: `docs/FLASHCARDS_PROGRESS.md`.
