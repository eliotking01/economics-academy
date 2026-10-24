---
description: Write the Edexcel B flashcards for one spec unit, e.g. /edexcel-b-flashcards 1.6
---

Write the flashcards for every Edexcel B topic in spec unit **$ARGUMENTS**, into the theme's deck. D67 Phase 2.

## Before you start

- Work on `feature/edexcel-b-flashcards`. Never on `main`, never push. One unit per run, then stop.
- **Phase 0 must be answered.** Open `/Users/eliotking/Desktop/Economics Academy/05-website/drafts/all-boards-parity/review/phase-0-groundwork.md`. If Eliot's answers to the feature-flag design (Q1-Q3) and the flashcard URLs and deck ids (Q6) are not recorded there, stop and say so. Where his answer differs from what is written here, his answer wins.
- Read: `flashcards-data/CLAUDE.md` in full; `_archive/FLASHCARDS_PROGRESS.md`; the Edexcel A deck for the nearest theme (`flashcards-data/edexcel-a/theme-N.json`), for **shape and mix only**; every B notes page in the unit (`revision-notes/edexcel-b-theme-N/<slug>.html`); `docs/DIAGRAM_STYLE.md` if the unit has a diagram.
- **Card ids are permanent.** Spaced-repetition progress is keyed on them in students' browsers (DO-NOT-BREAK). Pattern: `edexcel-b-<spec-with-dashes>-<type>-NN`, e.g. `edexcel-b-1-6-2-def-01`.

## The deck

- One deck per theme: `flashcards-data/edexcel-b/theme-N.json`. If it does not exist yet, draft the deck-level fields (`board`, `boardName`, `theme`, `themeName`, `deckId`, `deckTitle`, `metaDescription`, `intro`) from the Edexcel A pattern and **list them for approval** in `review/flashcards-decks.md`. They are visible wording: never publish them unapproved.
- Mix roughly as the A decks: about half definitions, then diagram, chain, evaluation, formula, calculation and application cards. About 15-25 cards per unit, 75-95 per theme.

## For each topic in the unit, in spec order

1. **Definitions** reuse the B page's `key-definition` chip text **verbatim**, with `origin: "notes-verbatim"`. Never improve the wording (CLAUDE.md rule 2). If the chip looks wrong, log it.
2. Every card's `subtopic` is the B notes slug, and every claim on it is traceable to that page.
3. **Board fidelity.** Write B-specific cards in B's terms. Never copy or adapt an Edexcel A card.
4. **Diagram cards.** Reuse `images/diagrams/svg/` where the B page uses the same diagram. For a B-only diagram (`break-even-chart`, `market-map`, `product-life-cycle`, `long-tail`, `import-quota`, `natural-monopoly`), first check whether a flashcard-ready SVG exists. If not, queue it in `review/flashcard-diagrams-theme-N.md`: drawn to `docs/DIAGRAM_STYLE.md`, verified against the notes PNG, rendered headless. Do not draw it in this run unless that sheet is approved.

## Checks

1. **Independent check.** Write a temp file to the scratchpad holding each card's `id`, `type`, `front`, `back`, `origin` and its notes page path. Give it to the `cold-solver` agent in **verify** mode. A DISAGREE is fixed in the card. A `NOTES?` is a suspected notes error: log it in `docs/CONTENT_ISSUES.md` in that file's format, and never fix it.
2. **Build.** For this generator the build is the check. Use the preview mechanism Phase 0 agreed (recommended: `EA_PREVIEW=edexcel-b:flashcards python3 scripts/build.py`). Then rebuild without it and confirm `git status` shows no generated page.

## When the unit is done

Write `/Users/eliotking/Desktop/Economics Academy/05-website/drafts/all-boards-parity/review/flashcards-unit-X-Y.md`:
- counts by card type, per topic
- verifier disagreements and how each was resolved, and any `NOTES?` logged
- open questions for Eliot, numbered
- **3 random cards** reproduced in full

Commit ("Add Edexcel B flashcards, unit X.Y") with the trailers `suggest_trailers.py` prints. Name the preview deck page to open in Live Server. Stop.
