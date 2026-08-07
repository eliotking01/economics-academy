# Flashcards QA fixes — progress and handoff

The live state of the flashcard content-quality remediation pass. A fresh
session with no memory of the previous one resumes from this file alone.

_Last updated: 2026-08-07._

## BRANCH

`flashcards-qa-fixes` — **all work lives here; never `main`.** `main` holds the
merged flashcards feature and auto-publishes to economicsacademy.co.uk, so
nothing in this pass may be committed, merged or pushed to it. Eliot reviews
and merges himself.

## STATUS

**IN PROGRESS** — Phase 0 and Phase 1 (audit) complete. No content edited yet;
blocked on one decision (see OPEN QUESTIONS).

## RENDERING FINDINGS

**How card content is rendered.** Card `front` and `back` are **raw HTML
strings** in the deck JSON, inserted with `innerHTML` by
`js/components/flashcards.js` (`faceHTML()`, line ~276, and `renderCard()`,
line ~315). There is no markdown layer and no plain-text fallback. The builder
(`scripts/build_flashcards.py`) does **not** sanitise or whitelist tags — it
validates structure, not markup — so any HTML authored into the JSON reaches
the page verbatim. The content is hand-authored in this repo and never
user-supplied, so no sanitiser is being introduced; the tag vocabulary is kept
deliberately narrow instead.

**Tags already in use across the 665 cards**: `<p>` (3,744), `<strong>`
(5,590), `<li>` (290), `<ul>` (72), `<em>` (44). Nothing else.

**Bullet lists are therefore already supported** — 36 cards ship one today, and
`css/pages/flashcards.css` already carries `.fc-back ul:last-child` and
`.fc-sample-back ul:last-child` margin rules. Issue D needs no new markup
vocabulary: `<ul><li>` is the house idiom and it renders.

**But multi-line content did not FIT, and that was the real blocker.** The two
card faces were `position: absolute; inset: 0` inside a `.fc-card-inner` of
`min-height: 340px` (300px under 736px), with `overflow-y: auto` on the face.
The card was a fixed-height box that long answers scrolled inside. Measured
across all 665 cards on the shipped CSS:

| | backs overflowing | fronts overflowing |
| --- | --- | --- |
| mobile (390px) | **556 of 665 (84%)** | 0 |
| desktop (1280px) | **154 of 665 (23%)** | 0 |

Worst cases ran 354px past the visible box — answers were cut mid-sentence.
This is a **pre-existing defect, not something this pass introduced**, and
adding six-bullet lists would have made it considerably worse.

**Renderer change made** (`css/pages/flashcards.css`, CSS only, no JS): the two
faces are stacked in a single **grid cell** instead of being absolutely
positioned, so the card's height is the taller face's natural height.

- `.fc-card-inner` — `display: block; position: relative` → `display: grid;
  grid-template: 1fr / 1fr`. `min-height`, `transform-style: preserve-3d` and
  the flip transition are unchanged.
- `.fc-face` — `position: absolute; inset: 0` → `grid-area: 1 / 1`, and
  `overflow-y: auto` dropped (nothing overflows now).

Re-measured after the change: **0 of 665 backs and 0 of 665 fronts overflow at
either width.** The 3D flip, `backface-visibility`, the reduced-motion
crossfade branch and the print sheet (which uses separate `.fc-print-*` nodes,
not `.fc-face`) are all untouched by it.

**Known side effect, and the open decision:** because both faces share one grid
cell, the card is now as tall as its taller face — so a short question sits
vertically centred in a tall card whose height is set by its answer. See OPEN
QUESTIONS.

## TOOLING

All three tools live in `_working/flashcards/qa/` (Jekyll-excluded, never
published). Every one of them needs the local server running first:

```
python3 -m http.server 8899          # from the repo root
```

| Tool | What it does |
| --- | --- |
| `_working/flashcards/qa/audit.py` | Scans `flashcards-data/*/*.json` for issues A–D. `--issue A --show` lists every hit with context; `--deck <id>` narrows. No args = summary counts. |
| `_working/flashcards/qa/measure.py` | Loads every card into the real page at both widths and records `scrollHeight` vs `clientHeight` per face. `--tag before` writes `measure-before.json`. This is what produced the overflow table above. |
| `_working/flashcards/qa/shoot.py` | Screenshots real card faces. `shoot.py <card-id> [...] --side back --tag x`, or `--deck <id> --long 6` for the six longest backs in a deck. Images land in `_working/flashcards/qa/shots/<tag>/<card>-<side>-<width>.png`. |

`frame.html` is the shared harness both `measure.py` and `shoot.py` load.

**Two traps a future session must not re-discover.**

1. Chrome's `--window-size` does **not** control the layout viewport for a page
   carrying a viewport meta tag on this machine — asking for 390 gave a 485px
   viewport (741px with `--force-device-scale-factor`), so "mobile"
   screenshots were silently cropped desktop renders. Everything is therefore
   loaded **inside an iframe of the target width**; an iframe's viewport is
   exactly its CSS width. Verified: the harness reports `frame 390`.
   `--hide-scrollbars` is required or the iframe reports 375.
2. `--dump-dom` serialises only the top-level document, so measurements taken
   inside the iframe come back out by `postMessage` to `frame.html`.

The FLASHCARDS_PROGRESS note that "mobile-width right-edge overflow in headless
renders is site baseline" was an artefact of trap 1. At a true 390px viewport
the deck page has **zero** horizontally overflowing elements.

## ISSUE TABLE

Counts are cards affected, from `audit.py` over all 665 cards in all six decks.

| Issue | Status | Found | Fixed | Stopped at |
| --- | --- | --- | --- | --- |
| A — merged points on one line | not started | 206 cards (229 blocks) | 0 | — |
| B — exam board references | not started | 47 cards (64 mentions) | 0 | — |
| C — multiple revision points | not started | 123 candidates, to be hand-filtered | 0 | — |
| D — long inline lists | not started | 168 cards (187 lists) | 0 | — |

Per deck:

| Deck | A | B | C | D |
| --- | --- | --- | --- | --- |
| `edexcel-a-theme-1` | 2 | 3 | 13 | 17 |
| `edexcel-a-theme-2` | 36 | 7 | 28 | 25 |
| `edexcel-a-theme-3` | 34 | 2 | 12 | 19 |
| `edexcel-a-theme-4` | 43 | 0 | 1 | 26 |
| `aqa-micro` | 43 | 17 | 37 | 43 |
| `aqa-macro` | 48 | 18 | 32 | 38 |

Notes on what the numbers mean:

- **A** is precise — the detector fires on two or more `<strong>Term</strong> —
  definition` units in one `<p>`, on a bolded lead-in starting a sentence
  mid-block, or on two or more arithmetic steps sharing a block. Spot-checked
  and clean.
- **B** is exact, not a heuristic: a word-boundary match, so `specialisation`
  never matches `spec` and the `specCode` metadata field is not card text. One
  card (`aqa-2-2-4-formula-01`) references *Edexcel* on an AQA card.
- **C is a candidate net, not a finding.** Most of the 123 are single-focus
  questions with a natural two-clause phrasing ("Define national income, and
  state the national income identity") that must NOT be split. Only cards
  testing genuinely distinct revision areas get split — the named example,
  `edexcel-a-2-1-3-eval-01` ("Evaluate the effects of unemployment, and the
  significance of migration and skills"), is a true one. Every candidate is
  read by hand and the confirmed count recorded here when Issue C starts.
- **D** counts *substantive* enumerations only: four or more consecutive
  parallel items averaging more than three words each, i.e. lists of causes,
  impacts or evaluation points. A separate **17 cards** hold *atomic* noun
  lists ("land, labour, capital, enterprise") inside a sentence; bulleting
  those would break the sentence and they are deliberately out of scope.

## ID SCHEME

Existing convention, unchanged: `<board>-<spec-code-hyphenated>-<type>-<NN>`,
e.g. `edexcel-a-2-1-3-eval-01`, `aqa-1-8-9-diagram-04`. `<type>` is one of
`def`, `diagram`, `chain`, `eval`, `formula`, `calc`, `app`. The builder
enforces slug form, uniqueness, and the board prefix.

**For cards created by splitting (Issue C):**

- The original card **keeps its id**, narrowed to the first of the two areas.
  Ids are never reused, never reassigned, never renumbered.
- The new card takes the **next free `NN` in that spec-code + type group**,
  counting across the whole deck. If `…-2-1-3-eval-01` and `…-2-1-3-eval-02`
  exist, the split's new card is `…-2-1-3-eval-03`.
- Where the split changes the card's type (e.g. an evaluation whose second half
  is really a definition), the new card takes the next free `NN` in its **new**
  type group instead.
- `version` on both halves is bumped to `2`; `lastVerified` set to the edit
  date.

**localStorage:** Issue C changes the id set, so the prefix in
`js/components/flashcards.js` is bumped `ea-flashcards:v1:` → `ea-flashcards:v2:`,
discarding stale progress cleanly. The feature has no users yet, so no
migration and no user-facing notice. `INDEX_KEY` follows the prefix
automatically.

## TRIMMED LISTS LOG

Every card where a list was cut to six bullets, with exactly what was removed —
**this is Eliot's review list.** Nothing here yet; Issue D has not started.

| Card | Kept | Removed | Why |
| --- | --- | --- | --- |
| _(none yet)_ | | | |

## DECISIONS MADE

- **Bullets need no renderer change; card height did.** Investigated before
  editing anything, per the brief. `<ul>/<li>` already ship and already have
  CSS. The blocker was the fixed-height scrolling face, fixed in CSS only (see
  RENDERING FINDINGS). Reason for CSS over JS: no measurement code, no layout
  thrash, no new failure mode, and it degrades identically under
  `prefers-reduced-motion`.
- **No HTML sanitiser introduced.** Card HTML is hand-authored in-repo and
  never user-supplied, and this pass adds no new tag types beyond the `<ul>`,
  `<li>`, `<p>`, `<strong>`, `<em>` already in use. Adding a sanitiser would be
  new machinery guarding a threat that does not exist here.
- **Issue D covers substantive lists only** (causes, impacts, evaluation
  points), not atomic noun lists inside a sentence — that is what the brief
  asks for, and bulleting "land, labour, capital, enterprise" would break the
  sentence it sits in. The 17 atomic-list cards are logged but left alone.
- **Issue C is hand-filtered, not bulk-split.** The 123 detector hits are
  candidates; splitting all of them would wreck good single-focus cards.
- **Audit tooling lives in `_working/`**, not `scripts/`. It is a
  one-pass QA tool, not a standing verifier like `scripts/verify_*.py`, and
  `_working/` is already the unpublished home for build-time working files.

## NEXT STEPS

1. **Blocked**: get Eliot's answer on the card-height side effect (see OPEN
   QUESTIONS) before any content editing begins. The CSS change is already in
   the working tree and is trivially reversible.
2. Then Issue A + D together, deck by deck in ~20-card batches, starting with
   `edexcel-a-theme-1` (2 A-cards, 17 D-cards — the smallest deck, a good
   calibration batch). Present before/after for each batch.
3. Then Issue B (47 cards, listing already produced by
   `audit.py --issue B --show`).
4. Then Issue C: hand-filter the 123 candidates, split the confirmed ones, bump
   the localStorage prefix, and update card counts in deck landing pages, the
   hub, meta descriptions and the FLASHCARDS_PROGRESS coverage matrix.
5. Then Phase 3 verification.

## OPEN QUESTIONS FOR ME

1. **The card is now as tall as its answer.** Fixing the clipping means the
   question side of a card is as tall as its answer side, so a one-line
   question can sit vertically centred in a tall panel. Three ways to go:
   (a) accept it — CSS-only, no layout jump on flip, card size stays put;
   (b) add JS so the card resizes to whichever face is showing, animating with
   the flip — nicer, but new code and a possible jitter mid-flip;
   (c) revert and keep the scrolling fixed-height card, which means answers
   stay cut off. Recommendation: (a).

## Untracked oddity, not touched

`flashcards-data/aqa 2/`, `flashcards-data/edexcel-a 2/`, `flashcards/aqa 2/`,
`flashcards/data 2/` and `flashcards/edexcel-a 2/` are **empty** directories
dated 2026-08-07, almost certainly a Finder/sync duplication artefact. Git does
not track empty directories, so the tree still reports clean. Left alone —
deleting them is Eliot's call.
