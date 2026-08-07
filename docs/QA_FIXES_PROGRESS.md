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

**IN PROGRESS** — Phase 0 (re-ground, rendering, tooling) and Phase 1 (audit)
complete. **Phase 2 is COMPLETE — all four issues (A, B, C, D) are done
across all six decks**: 265 cards edited across 13 batches, plus 6 cards split
in two. The deck total is now **671 cards** (was 665). Nothing is blocked.
Remaining: **Phase 3 verification** — end-to-end player testing, print
stylesheet, GA4, reduced motion, and the screenshot review.

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

**Known side effect, accepted by Eliot 2026-08-07:** because both faces share
one grid cell, the card is as tall as its taller face — so a short question
sits vertically centred in a card whose height is set by its answer. The
alternative (JS resizing the card on flip) was offered and declined in favour
of the CSS-only fix.

**Two later spacing changes, same file, both from visual checks:** card text
uses a 1em block gap rather than the site-wide 2em (which spread a four-line
answer over a screen and pushed calculation steps far apart), and a `<ul>`
directly after a `<p>` is pulled up so a lead-in line and its list read as one
unit. Both scoped to `.fc-face`, `.fc-sample-back` and `.fc-print-back`.

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
| A — merged points on one line | **DONE** | 206 cards | 189 | All six decks. The 17 residual hits are hand-reviewed false positives, named per deck in the batch log. |
| B — exam board references | **DONE** | 47 cards (64 mentions) | 47 | All six decks audit **0**. An independent regex sweep over card text in both the sources and the built payloads returns 0 hits for `edexcel\|aqa\|ocr\|specification\|spec\|exam board`. |
| C — multiple revision points | **DONE** | 123 candidates → **6 confirmed** | 6 split | All 123 read by hand. The 117 not split are single-focus questions with a natural two-clause phrasing; splitting them would have wrecked good cards. |
| D — long inline lists | **DONE** | 67 cards | 51 | All six decks. The 29 residual hits are hand-reviewed false positives. |

Per deck, cards **remaining** (re-run `audit.py` to refresh):

| Deck | A | B | C | D |
| --- | --- | --- | --- | --- |
| `edexcel-a-theme-1` | **0** | **0** | 13 | 2 (false positives, left) |
| `edexcel-a-theme-2` | **1** (false positive, left) | **0** | 28 | 5 (false positives, left) |
| `edexcel-a-theme-3` | **5** (false positives, left) | **0** | 12 | 3 (false positives, left) |
| `edexcel-a-theme-4` | **4** (false positives, left) | **0** | 1 | 7 (false positives, left) |
| `aqa-micro` | **4** (false positives, left) | **0** | 37 | 5 (false positives, left) |
| `aqa-macro` | **3** (false positives, left) | **0** | 32 | 7 (false positives, left) |

A residual count above zero does **not** mean unfinished work. **Every deck is
complete for A and D.** What remains is the set of detector hits read by hand and
judged not to be defects — bolded terms mid-sentence, examples clauses,
appositive commas, and figures whose thousands separators the comma-splitter
reads as list items. They are named per deck in the batch log so a future
session does not re-examine them.

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
| `edexcel-a-2-5-4-eval-02` — costs of economic growth | Demand-pull inflation · worsened inequality · environmental damage (pollution, resource depletion, biodiversity loss) · a worsening current account · worse work-life balance · more consumption of demerit goods | **"congestion and housing pressure"** | The list ran to seven. Spec 2.5.4 frames the costs of growth around consumers, firms, the government, current and future living standards and the environment. Congestion and housing pressure is the only one of the seven with no distinct home in that framing — it is a local symptom already carried by "environmental damage" and "worse work-life balance" — and it is the least often credited in mark schemes. Everything else in the list maps to a named spec strand. |

**One card deliberately keeps seven bullets:** `edexcel-a-2-6-1-def-01` asks for
"the **seven** macroeconomic objectives", so capping it at six would make the
card contradict its own question. The six-bullet cap is a limit on trimming
long prose lists, not a reason to drop content the question explicitly counts.

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

**Batch 2 — `edexcel-a-theme-2` sections 2.1–2.3, issues A and D
(2026-08-07).** 22 cards edited.

A (16): inflation/deflation/disinflation onto three lines (the example Eliot
named); actual vs potential growth; nominal vs real GDP; gross vs net
investment; MPC vs MPS; SRAS vs LRAS; the three balance-of-payments accounts;
the four AD components; the stakeholder effects of inflation and of
unemployment; the three causes of inflation; government expenditure's fiscal
choices; the trade-balance drivers; the three Keynesian LRAS phases; the CPI
calculation rebuilt as one step per line.

D (6): GDP's limitations, current-account deficit causes, net trade
influences, the SRAS shift factors.

**Batch 3 — `edexcel-a-theme-2` sections 2.3–2.6, issues A and D
(2026-08-07).** 21 cards edited, completing the deck.

A (17): the LRAS six; the circular flow's real and money flows; the three
injections and three withdrawals; the extended flow; the four marginal
propensities; the multiplier ratio and its example; the benefits of growth;
demand-side policy's two types; the interest-rate chain; deficit/surplus/
balance and direct vs indirect taxes; the weaknesses of demand-side policy;
supply-side policy's two approaches and its five aims; the four objective
trade-offs; the three policy conflicts.

D (4): the trade cycle's four phases; boom vs recession characteristics
(six bullets each, nothing trimmed); the costs of growth (**trimmed — see
TRIMMED LISTS LOG**); the seven objectives.

Read and left alone across both batches: `edexcel-a-2-1-3-def-01`
("full-time students, early retirees, the long-term sick, discouraged
workers" is an examples clause inside a definition), `edexcel-a-2-2-1-calc-01`
(the question stem's data, and a four-share figure list),
`edexcel-a-2-4-1-diagram-01` ("land, labour, capital, enterprise" and "rent,
wages, interest, profit" belong inside their sentences),
`edexcel-a-2-4-4-def-01` (an examples clause), `edexcel-a-2-5-1-diagram-01`
(appositive commas, not a list) and `edexcel-a-2-2-3-def-02` (one bullet with
a bolded phrase mid-way, not two merged points).

**Batch 4 — `edexcel-a-theme-3` sections 3.1–3.4.4, issues A and D
(2026-08-07).** 18 cards edited. A: the principal-agent split; public vs
private and profit vs not-for-profit; the three integration types; the four
growth constraints; the demerger impacts; the four business objectives;
TR/AR/MR; the seven cost measures; the cost calculation rebuilt one step per
line; the six internal economies; the causes of diseconomies; efficiency in
perfect competition and under market power; monopolistic competition's
consumer impact; overt vs tacit collusion; the kinked demand curve's two
segments; the three types of price competition. D: the six demerger reasons.
B: two fronts ("in the Edexcel specification", "in the specification").

**Batch 5 — `edexcel-a-theme-3` sections 3.4.5–3.6, issues A and D
(2026-08-07).** 17 cards edited, completing the deck. A: monopoly efficiency's
four verdicts; the monopoly and monopsony stakeholder sets; the natural-monopoly
regulator dilemma; competition vs contestability; limit pricing; MRP's two
parts; wage-elasticity conditions; labour supply shift factors; geographical vs
occupational immobility; the minimum-wage evaluation; the privatisation
for/against; the five intervention yardsticks; regulatory capture's two causes;
the four limits of intervention. D: the six entry barriers; the supplier and
employee protection lists.

Read and left alone in Theme 3: `edexcel-a-3-1-1-def-02`,
`edexcel-a-3-1-2-def-02`, `edexcel-a-3-3-1-diagram-01`,
`edexcel-a-3-4-1-def-01`, `edexcel-a-3-4-5-diagram-03`,
`edexcel-a-3-4-4-def-03`, `edexcel-a-3-4-6-def-01` and
`edexcel-a-3-4-7-diagram-01` — bolded terms mid-sentence and atomic example
lists, not merged points or revision lists.

**Batches 6 and 7 — `edexcel-a-theme-4`, issues A and D (2026-08-07).** 51
cards edited across the two, completing the deck and with it **every Edexcel
deck**. Batch 6 (24 cards, 4.1 trade): globalisation's six drivers, the
comparative-advantage figures and calculation, the model's five assumptions,
specialisation for/against, the four pattern-of-trade factors, the terms-of-trade
cases, the four trading blocs, trade creation vs diversion, the monetary-union
conditions, the reasons for and methods of protectionism, the BoP accounts and
calculation, deficit causes and the three policy routes, the three exchange-rate
systems, appreciation drivers, competitive devaluation's risks, the depreciation
costs, the J-curve and Marshall-Lerner, and the two competitiveness measures.
Batch 7 (27 cards, 4.1.9–4.5): unit labour costs, cost vs non-cost
competitiveness, the poverty drivers, inequality's six causes, the HDI's three
dimensions and the other indicators, economic and non-economic development
factors, the six interventionist strategies, the Lewis model's limits, Fairtrade
/ aid / debt relief, World Bank vs IMF vs NGOs, the five financial-market
functions, moral hazard / speculation / market rigging, the consequences of
financial failure, the central bank's four functions, the three types of public
expenditure and what changes them, the spending-share evaluation, progressive /
proportional / regressive taxes, deficit vs debt and cyclical vs structural, the
deficit influences, why debt matters, the global policy toolkit, controlling
global companies, and the policymaker's problems.

No list needed trimming in either batch. Where a card ran to seven points
(4.1.6's reasons for protection, 4.3.1's other indicators) the original's own
two-group structure was kept, so both lists sit under the cap and nothing was
dropped.

Read and left alone in Theme 4: `edexcel-a-4-1-2-diagram-01`,
`edexcel-a-4-4-2-def-02`, `edexcel-a-4-5-1-def-01`, `edexcel-a-4-5-2-def-01`,
`edexcel-a-4-1-1-eval-02`, `edexcel-a-4-1-4-eval-01`, `edexcel-a-4-1-7-calc-01`,
`edexcel-a-4-1-9-calc-01`, `edexcel-a-4-2-1-def-01`, `edexcel-a-4-2-2-def-01`
and `edexcel-a-4-3-3-def-04` — bolded terms mid-sentence, examples clauses, and
figures whose thousands separators the comma-splitter reads as list items.

**Batches 8 and 9 — `aqa-micro`, issues A and D (2026-08-07).** 49 cards
edited across the two, completing the deck. Batch 8 (20 cards, 1.1–1.5.5):
economics as a social science, needs vs wants, renewable vs non-renewable, the
PPD points, total vs marginal utility, demand and supply movement-vs-shift with
their factor lists, the PED and PES value ranges, the PES determinants, labour
productivity, marginal/average/total returns, returns to scale, the seven cost
measures and the cost calculation, diseconomies, TR/AR/MR, normal vs abnormal
profit, the five roles of profit, and overt vs tacit collusion. Batch 9 (29
cards, 1.5.5–1.8): the kinked demand curve, monopoly efficiency, natural
monopoly, the three degrees of price discrimination, contestability, the four
efficiency types and both efficiency diagrams, consumer and producer surplus,
MRP, the labour supply set (definition, shift factors, immobility), imperfect
labour markets and the monopsony diagram, the NMW evaluation, wage
discrimination's conditions and impacts, the income/wealth distribution set,
poverty's consequences and the policies against it, public goods, the
private/external/social identities, factor immobility, public ownership vs
privatisation, and the intervention toolkit.

**Where a card has an Edexcel twin the two now carry the same structure**, per
the house rule that twins match: the kinked demand curve, monopoly efficiency,
natural monopoly, contestability, both efficiency diagrams, MRP, labour supply
shift factors, immobility, the NMW evaluation, the inequality causes, and the
seven cost measures with its calculation.

B fixed on three cards already open for A/D: "which is why it recurs across the
whole specification" → "throughout the course"; "The AQA toolkit" → "The
toolkit"; and "Explain AQA's other intervention methods" → "Explain the other
intervention methods".

No list needed trimming. The longest — the PES determinants, the supply shift
factors, the inequality causes, the anti-poverty policies and the intervention
toolkit — all sit at exactly six.

Read and left alone in `aqa-micro`: `aqa-1-4-7-def-01`, `aqa-1-5-6-diagram-02`,
`aqa-1-6-2-def-01`, `aqa-1-6-2-def-03`, `aqa-1-1-1-def-01`, `aqa-1-3-4-calc-01`,
`aqa-1-4-2-def-01`, `aqa-1-7-1-def-01` and `aqa-1-7-2-def-01`.

**Batches 10, 11 and 12 — `aqa-macro`, issues A and D (2026-08-07).** 57 cards
edited, completing the deck and with it **every deck**. Batch 10 (26 cards,
2.1–2.4.1): the four objectives and UK targets, nominal/real/per-capita GDP, the
weighted CPI calculation, the limitations of national income data, real income,
the circular flow, injections vs withdrawals, AD's component shares,
consumption's determinants and the other influences, gross vs net investment,
the multiplier ratio, SRAS and its shift factors, the Keynesian AS curve, the
economic cycle and its indicators, cyclical instability's four amplifiers, the
costs and benefits of growth, the unemployment definitions and four types,
inflation/deflation/disinflation, money's functions and characteristics, the
money supply, the three financial markets, and bonds. Batch 11 (29 cards,
2.4.2–2.6.5): commercial vs investment banks, the balance sheet, the three bank
objectives, credit creation, the central bank's functions and transmission
channels, the monetary-policy evaluation, the liquidity and capital ratios,
systemic risk vs moral hazard, fiscal policy and public expenditure, the three
tax structures, supply-side policies vs improvements and their examples,
globalisation's drivers and consequences, comparative advantage, trade's
benefits and costs, customs unions, the BoP set with its calculation, exchange
rates and the J-curve, currency unions, growth vs development, the barriers, and
the development strategies. Batch 12 (2 cards) bulleted two lists first left as
prose on review.

B fixed on nine `aqa-macro` cards already open for A/D — "in the AQA
specification" (×2), "AQA also expects", "AQA's named shift factors", "Causes on
the AQA list", "The curve AQA names explicitly", "AQA expects a range of
indicators", "AQA names four amplifiers", "AQA expects a view on
sustainability", "AQA's trap", "AQA stresses" and "Give AQA's examples".

**One card regrouped rather than trimmed:** `aqa-2-6-5-def-02` listed **ten**
economic barriers to development. Rather than drop four spec-relevant barriers,
related pairs were combined into single bullets — foreign currency gap with
capital flight, demographics with debt servicing, credit access with
infrastructure, education with property rights — giving six bullets with
**nothing removed**. Same technique as `edexcel-a-4-3-1-def-04`.

Read and left alone in `aqa-macro`: `aqa-2-2-3-def-01`, `aqa-2-3-1-diagram-01`,
`aqa-2-6-2-diagram-01`, `aqa-2-1-1-def-02`, `aqa-2-1-3-calc-01`,
`aqa-2-2-1-diagram-01`, `aqa-2-2-4-def-01`, `aqa-2-3-2-def-01`,
`aqa-2-4-2-def-01` and `aqa-2-6-3-calc-01`.

**Batch 13 — issue B, all decks (2026-08-07).** The 25 cards still carrying a
board reference after the A/D pass. Every one was **rewritten, not just
truncated** — "AQA flags exactly this" became "That is the point to carry",
"AQA expects you to trace a change" became "Be ready to trace a change", "the
application AQA names in the specification" was dropped as redundant, and the
four Edexcel fronts saying "the specification's three/four/five …" now simply
say "the three/four/five …". `aqa-2-2-4-formula-01` also lost a cross-board
reference: an AQA card that said the withdrawal-propensity method "is Edexcel
territory". `aqa-2-2-6-def-02`'s six LRAS determinants were bulleted at the
same time.

Combined with the 22 fixed opportunistically during the A/D pass, that is all
47. Verified two ways: `audit.py` reports **B = 0** for every deck, and an
independent sweep of card text in both the sources and the built payloads finds
**0** matches for `edexcel|aqa|ocr|specification|spec|exam board`. Deck-level
`board` values, `deckTitle`s, page headings, nav and SEO text are untouched —
confirmed by printing them after the pass.

**Batch 14 — issue C, the splits (2026-08-07).** All 123 candidates read by
hand; **6 confirmed** and split, 117 left alone. The 117 are single-focus
questions whose phrasing happens to contain "and" — "Define national income,
and state the national income identity", "Draw and explain the Keynesian AS
curve", "Define SRAS, and name the cost changes that shift it". Splitting those
would have produced half-cards on one revision point each.

The six that genuinely tested two areas:

| Original (narrowed) | New card | Why it was two areas |
| --- | --- | --- |
| `edexcel-a-2-1-3-eval-01` — effects of unemployment | `edexcel-a-2-1-3-eval-02` — migration and skills | Eliot's named example. Unemployment's effects and the significance of migration are separate spec bullets. |
| `edexcel-a-2-1-1-eval-01` — limitations of GDP | `edexcel-a-2-1-1-eval-02` — the national happiness evidence | National wellbeing is its own spec bullet, and the card for it was spec-sourced in the first place. |
| `edexcel-a-2-1-4-chain-01` — causes of a deficit | `edexcel-a-2-1-4-eval-01` — how correcting one conflicts with other objectives | Causes sit in 2.1.4; the policy trade-off is 2.6.4 material. The new card changes type to `evaluation`, so it takes `eval-01` — the first free number in its **new** type group. |
| `aqa-2-1-2-def-03` — the current account | `aqa-2-1-2-def-04` — productivity as an indicator | Two unrelated indicators bolted together; the front literally said "and name the remaining indicator". |
| `aqa-2-5-1-def-02` — types of public expenditure | `aqa-2-5-1-def-05` — why governments levy taxes | Spending and taxation are distinct revision areas. |
| `aqa-1-8-5-def-03` — why the classification is a value judgement | `aqa-1-8-5-def-04` — how imperfect information causes mis-provision | Two distinct mechanisms, two distinct exam questions. |

**`aqa-2-1-2-def-03` was `notes-verbatim`.** Its verbatim sentence is the
current-account definition, which stayed on the original card, so the builder's
verbatim check still passes. The new productivity card is `card-authored`.

Wording: each half keeps its original text. Four small joins were rewritten
because the sentence lost its antecedent — "Hence the interest in national
wellbeing" → "National wellbeing is measured alongside GDP"; "Taxes exist to
fund **this** spending" → "**public** spending"; "The final indicator is
productivity — output per worker — which drives…" → "Productivity is output per
worker. It drives…"; and "Imperfect information **compounds the problem**:" →
"Imperfect information:". No economics changed.

Every new card carries the correct board (deck), theme (deck), topic, subtopic,
cardType, tags and difficulty — the builder validates all of these and passed.

**localStorage bumped** `ea-flashcards:v1:` → `ea-flashcards:v2:` in
`js/components/flashcards.js`, with the reason in a comment. `INDEX_KEY` derives
from the prefix so it follows automatically. No migration, no user-facing
notice — the feature has no users.

**Card counts updated everywhere and verified consistent**: deck landing pages
and the hub are regenerated by the builder (checked: source, built payload and
hub all agree, 671 total); `metaDescription` fields never quoted counts so
needed no change; and the FLASHCARDS_PROGRESS coverage matrix headers were
corrected — several were stale from earlier phases (Theme 4 still said "18
cards so far", `aqa-micro` 89, `aqa-macro` 62), so they now read 95 / 106 / 97 /
84 / 185 / 104 with a 671 tally. Dated log entries in that file were left as the
historical record they are.

## NEXT STEPS

**Phase 3 verification** — nothing else outstanding in Phase 2.

1. Re-run `audit.py` (A/B/D/C all at their reviewed floors) and validate JSON.
2. Screenshot a substantial sample: every card type, both boards, several
   themes, longest and most-bulleted backs, at 390px and 1280px. Inspect for
   overflow, clipping, cramped bullets and broken breaks.
3. Test end-to-end in a browser: flip, shuffle, again/got-it and the re-queue,
   session summary, localStorage reset, keyboard shortcuts, swipe,
   `prefers-reduced-motion`, and SVG diagram cards.
4. Check the print stylesheet now that bullets and multi-line backs exist.
5. Confirm GA4 events still fire.
3. Then Issue B: the 39 remaining cards (`audit.py --issue B --show`). Almost
   all are AQA cards saying "AQA" where the deck already says so.
4. Then Issue C: hand-filter the 123 candidates, split the confirmed ones, bump
   the localStorage prefix `ea-flashcards:v1:` → `:v2:` in
   `js/components/flashcards.js`, and update card counts in deck landing pages,
   the hub, meta descriptions and the FLASHCARDS_PROGRESS coverage matrix.
5. Then Phase 3 verification.

## HOW TO RESUME

```bash
python3 -m http.server 8899 &                        # tools need this
python3 _working/flashcards/qa/audit.py              # where things stand
python3 _working/flashcards/qa/audit.py --issue A --show --deck aqa-macro
```

To dump the full text of a deck's outstanding A/D cards, ready to edit:

```bash
python3 - <<'PY'
import json, subprocess
DECK = "aqa-macro"
ids = set()
for issue in ("A", "D"):
    out = subprocess.run(["python3", "_working/flashcards/qa/audit.py",
                          "--issue", issue, "--deck", DECK],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and not line.startswith("issue"):
            ids.add(parts[1])
path = {"edexcel-a-theme-1": "flashcards-data/edexcel-a/theme-1.json",
        "edexcel-a-theme-2": "flashcards-data/edexcel-a/theme-2.json",
        "edexcel-a-theme-3": "flashcards-data/edexcel-a/theme-3.json",
        "edexcel-a-theme-4": "flashcards-data/edexcel-a/theme-4.json",
        "aqa-micro": "flashcards-data/aqa/micro.json",
        "aqa-macro": "flashcards-data/aqa/macro.json"}[DECK]
deck = json.load(open(path))
sel = [c for c in deck["cards"] if c["id"] in ids]
sel.sort(key=lambda c: [int(x) for x in c["specCode"].split(".")])
for card in sel:
    print("=" * 74)
    print(card["id"], "|", card["cardType"])
    print("F:", card["front"])
    print("B:", card["back"])
PY
```

Then the loop for every batch:

```bash
python3 _working/flashcards/qa/apply.py _working/flashcards/qa/edits/batch-NN.json
python3 _working/flashcards/qa/touch.py <every id edited>
python3 scripts/build_flashcards.py
python3 _working/flashcards/qa/audit.py
python3 _working/flashcards/qa/shoot.py <a few ids> --side back --tag batch-NN
python3 scripts/verify_html.py flashcards revision-notes
```

Edit files live in `_working/flashcards/qa/edits/`. `apply.py` refuses to run
unless every `old` matches byte for byte, and proves afterwards that nothing
outside the named fields moved — so a stale or mistyped `old` costs nothing.

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
