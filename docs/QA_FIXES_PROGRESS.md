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
| A — merged points on one line | in progress | 206 cards (229 blocks) | 2 | `edexcel-a-theme-1` **done (0 left)**. Next: `edexcel-a-theme-2`. |
| B — exam board references | not started | 47 cards (64 mentions) | 0 | — |
| C — multiple revision points | not started | 123 candidates, to be hand-filtered | 0 | — |
| D — long inline lists | in progress | 67 cards (76 lists) | 4 | `edexcel-a-theme-1` **done**; its 2 remaining hits are judged false positives and deliberately left (see below). Next: `edexcel-a-theme-2`. |

Per deck, cards remaining:

| Deck | A | B | C | D |
| --- | --- | --- | --- | --- |
| `edexcel-a-theme-1` | **0** | 3 | 13 | 2 (both false positives, left) |
| `edexcel-a-theme-2` | 36 | 7 | 28 | 12 |
| `edexcel-a-theme-3` | 34 | 2 | 12 | 6 |
| `edexcel-a-theme-4` | 43 | 0 | 1 | 12 |
| `aqa-micro` | 43 | 17 | 37 | 15 |
| `aqa-macro` | 48 | 18 | 32 | 16 |

**The D count fell from 168 cards to 67 when the detector was tightened after
the Theme 1 calibration batch.** The first version split sentences on commas,
which counts clauses rather than list items, so ordinary prose ("The market
produces at Q1, where MPC = MPB, but the social optimum is Q2, where MSC =
MSB.") read as a four-item list. Three corrections, all in
`audit.py:list_runs()`: parenthetical examples are stripped before scanning;
a segment opening with a subordinator or a participle breaks the run instead of
extending it (`NOT_AN_ITEM`); and the atomic/substantive test uses the median
item length, not the mean. Spot-checked against Theme 1 by hand afterwards.

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

## BATCH LOG

**Batch 1 — `edexcel-a-theme-1`, issues A and D (2026-08-07).** 6 cards edited,
2 candidates read and deliberately left. Deck now audits A=0, D=2 (both the
left-alone false positives).

| Card | What changed |
| --- | --- |
| `edexcel-a-1-2-3-formula-02` | A — the YED sign rules ran together in one sentence; now two labelled bullets plus the luxury threshold on its own line. |
| `edexcel-a-1-2-3-formula-03` | A — the three XED sign rules ran together; now three labelled bullets. |
| `edexcel-a-1-2-2-diagram-01` | D — the four non-price demand factors were inline inside the shift sentence; now a lead-in line, four bullets, and the price/quantity reading on its own line. |
| `edexcel-a-1-2-4-diagram-01` | D — the same treatment for the three supply shift factors, kept parallel with its demand twin above; the leftward-shift sentence also split onto its own line. |
| `edexcel-a-1-1-4-diagram-02` | D — the four causes of growth bulleted; "outward shift"/"inward shift" bolded to match the AQA twin card. |
| `edexcel-a-1-1-5-eval-01` | D — two `<li>`s each crammed 3–4 semicolon-separated points; now a **For** heading with 4 bullets and an **Against** heading with 3. |

Read and left alone, with reasons (Eliot's check on my judgement):

- `edexcel-a-1-1-5-def-01` — "individuals, firms, regions, or countries" is the
  subject of a definition sentence, not a list of revision points.
- `edexcel-a-1-1-4-diagram-01` — "E, inside the frontier, is inefficient; F,
  outside it, is currently unattainable" is prose; the commas are appositive.
- `edexcel-a-1-1-3-def-01`, `edexcel-a-1-1-3-def-04`, `edexcel-a-1-4-1-app-02`,
  `edexcel-a-1-3-1-def-01`, `edexcel-a-1-3-3-def-02`, `edexcel-a-1-4-1-diagram-01`,
  `edexcel-a-1-1-2-def-02` and others — flagged only by the first, loose
  version of the D detector; all ordinary prose or parenthetical examples. They
  no longer flag.

No economics wording was changed in any of the six: every clause is the
original text, re-split across lines. No list exceeded six items, so the
TRIMMED LISTS LOG is still empty.

A CSS follow-up came out of the visual check: a lead-in `<p>` and the `<ul>` it
introduces were 2em apart (the site-wide block margin), so the bullets floated
away from the sentence setting them up. Scoped rules now pull the list up and
give `<li>`s a little breathing room, on card faces, static samples and the
print sheet alike.

## NEXT STEPS

1. Issue A + D on `edexcel-a-theme-2` — 36 A-cards and 12 D-cards. Work in
   ~20-card batches: batch 2 = the first ~20 A/D cards in deck order.
2. Then Themes 3 and 4, then `aqa-micro`, then `aqa-macro`, same treatment.
3. Then Issue B (47 cards; listing from `audit.py --issue B --show`).
4. Then Issue C: hand-filter the 123 candidates, split the confirmed ones, bump
   the localStorage prefix `ea-flashcards:v1:` → `:v2:`, and update card counts
   in deck landing pages, the hub, meta descriptions and the
   FLASHCARDS_PROGRESS coverage matrix.
5. Then Phase 3 verification.

## OPEN QUESTIONS FOR ME

None outstanding. Answered so far:

1. **The card is now as tall as its answer** — Eliot chose (a) accept it,
   2026-08-07: CSS-only, no layout jump on flip, no new JS. A short question
   therefore sits vertically centred in a panel sized by its answer.

## Untracked oddity, not touched

`flashcards-data/aqa 2/`, `flashcards-data/edexcel-a 2/`, `flashcards/aqa 2/`,
`flashcards/data 2/` and `flashcards/edexcel-a 2/` are **empty** directories
dated 2026-08-07, almost certainly a Finder/sync duplication artefact. Git does
not track empty directories, so the tree still reports clean. Left alone —
deleting them is Eliot's call.
