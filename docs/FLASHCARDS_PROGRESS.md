# Flashcards — progress and handoff

The live state of the flashcards feature. A fresh session resumes from this
file. Full plan context: CLAUDE.md ("Flashcards" section).

_Last updated: 2026-08-15._

> **2026-08-15 — resource unification Phase 1** (branch
> `resources-phase-1-flashcards`, see the top section of the repo-root
> `PROGRESS.md`): the hub and six deck pages were restyled onto the shared
> `.resource-*` components in `css/main.css`; `build_flashcards.py` now takes
> hub board/deck order from `boards.json` (Edexcel A first, micro before
> macro), adds a hero stat strip, `hasPart` structured data and
> question-finder cross-links, and the hub title/H1 gained "Free". Card
> content, deck data, the player and all card wording are untouched. Nothing
> below this note changes.

## FULL PROJECT SCOPE

Complete flashcard coverage of the ENTIRE A-Level specification for BOTH
boards — Edexcel A (9EC0) Themes 1, 2, 3 and 4, AND AQA (7136) 4.1 (all
micro sections) and 4.2 (all macro sections). The Edexcel Theme 1 deck was
the pilot, not the project. **This project is not finished until every unit
in the coverage matrix is ✅.**

Every future session must update the coverage matrix below — never delete
it. If any other part of this file appears to say the project is done, the
scope statement above overrides it.

AQA units use the site-local codes (`1.x.y` micro, `2.x.y` macro) per
CLAUDE.md — they correspond to the real AQA 7136 sections 4.1.x and 4.2.x
but are deliberately not those codes. Verification of card content is
always against the official 7136 specification.

## Coverage matrix

Status: ✅ = cards authored to plan density, approved by Eliot, built and
integrated · 🟡 = some approved cards exist but the unit is below density ·
❌ = no cards.

Tally (2026-08-07): **166 ✅ · 0 🟡 · 0 ❌ of 166 units — THE
COVERAGE MATRIX IS COMPLETE.** All seven phases of the approved
Option A build order are authored, reviewed and approved: six
decks, **671 cards** (665 authored, plus 6 created by the
2026-08-07 QA pass splitting multi-focus cards — see
docs/QA_FIXES_PROGRESS.md), 83 SVGs. Phase 7 approved 2026-08-06; content
issues #34–36 fixed the same day (the #35 chip was a glossary
source — glossary re-extracted and rebuilt, exits 0). All 36
logged content issues are resolved (34 fixed, #17 rejected,
none open). **What remains is NOT authoring — see "Outstanding
tasks for Eliot" below.**
**The AQA MICRO DECK IS COMPLETE — all 54 units ✅ (185 cards)**
(phase 5 batch 4 approved 2026-08-06, Kuznets card ratified in;
content issues #21–22 fixed the same day, with the glossary
re-extracted and rebuilt for #21's Relative poverty chip).
**Phase 6 open: the `edexcel-a-theme-4` deck exists** — batch 1
(18 cards, sections 4.1.1–4.1.5, comparative-advantage.svg)
FULLY approved 2026-08-06, including the revised 4.1.2 diagram
card. Content issues #23–25 all fixed the same day (Eliot's
full-specialisation remedy: swapped T-shirt maxima, SVG swap
applied to 4-1-2, its AQA twin 2-6-2-trade, and the macro
gallery — **comparative-advantage.png is now unreferenced and
carries superseded numbers; never use it as ground truth, the
SVG is authoritative**). **#26 (gallery blurb describes the
absolute-in-both case the figure no longer shows) is OPEN.**
Remaining after Theme 4: AQA macro 2.4 + 2.6 (9 units, phase 7).
**Edexcel Themes 1, 2 and 3 are COMPLETE** (95 + 106 + 97 cards),
and AQA micro sections 1.1–1.6 plus 1.8 are done — only 1.7
remains on the micro side. Cards shipped: 529 (295 Edexcel +
172 AQA micro + 62 AQA macro), **all approved by Eliot** (phase 5
batch 3 approved 2026-08-06; content issues #19–20 fixed the same
day; the backward-bend exclusion ratified — cards stay silent, the
1-6-2 notes page stays as written; **#17 remains rejected — the
1-5-7 page stays as written**).
SVG diagrams shipped: 75 — the 1.4 batch needed ZERO new SVGs,
only firm-family reuses. Content issues 9–14 fixed (note
**game-theory.png is unreferenced and known-incorrect; the notes
pages use game-theory.svg**). **Batches from batch 3 onward are
approved but NOT committed: Eliot has paused commits until he
says otherwise** — the "commit frequently" standing rule is
suspended for now.

Build order approved by Eliot 2026-08-05: **Option A, paired mirrors**
(AQA T1-mirrors → Edexcel T2 → AQA macro T2-mirrors → Edexcel T3 → AQA
1.4–1.6 → Edexcel T4 → AQA remainder), single deck per AQA side.
**Phase 1 (AQA batches 1–3, 89 cards) and Theme 2 batch 1 (21 cards) are
all approved by Eliot, 2026-08-05** — 30 units flipped to ✅. Also
approved and applied the same day: CONTENT_ISSUES 3–5 (the AQA 1.8.9
max/min/subsidy captions, fixed with the Edexcel twin's approved
wording) and `subsidy-gov-expenditure.svg` (attached to
`aqa-1-8-9-diagram-04`). No open content issues.

**Phase 2 (Edexcel Theme 2) is underway** — sections 2.1–2.3 done and
approved (batch 3 approved 2026-08-05, including the lras-shift
decision: **both** a classical and a Keynesian shift diagram ship, as
separate cards). Batch 4 approved 2026-08-05; CONTENT_ISSUES #6 approved and fixed
the same day. Batch 5 approved 2026-08-05 — **Theme 2 is COMPLETE**. Phase 3
(AQA macro deck: T2-mirror sections 2.1–2.3 and 2.5, then the rest
in phase 7) is underway.

### Edexcel A (9EC0) — Theme 1 ✅ (deck `edexcel-a-theme-1`, 95 cards, 17 diagrams)

| Unit | Status | Cards by type |
| --- | --- | --- |
| 1.1.1 Economics as a social science | ✅ | 2 definition |
| 1.1.2 Positive & normative statements | ✅ | 3 definition |
| 1.1.3 The economic problem | ✅ | 4 definition |
| 1.1.4 Production possibility frontiers | ✅ | 1 definition, 2 diagram |
| 1.1.5 Specialisation & division of labour | ✅ | 2 definition, 1 evaluation |
| 1.1.6 Types of economies | ✅ | 3 definition, 1 evaluation |
| 1.2.1 Rational decision making | ✅ | 1 definition |
| 1.2.2 Demand | ✅ | 4 definition, 1 diagram, 1 chain |
| 1.2.3 PED, YED, XED | ✅ | 5 definition, 3 formula, 2 calculation, 1 chain |
| 1.2.4 Supply | ✅ | 2 definition, 1 diagram, 1 chain |
| 1.2.5 Price elasticity of supply | ✅ | 2 definition, 1 formula, 1 calculation |
| 1.2.6 Price determination | ✅ | 2 definition, 3 diagram, 1 chain |
| 1.2.7 Price mechanism | ✅ | 1 definition, 1 chain, 1 evaluation |
| 1.2.8 Producer & consumer surplus | ✅ | 3 definition, 1 diagram |
| 1.2.9 Indirect taxes & subsidies | ✅ | 1 definition, 5 diagram, 2 evaluation, 1 application |
| 1.2.10 Alternative views of consumer behaviour | ✅ | 2 definition |
| 1.3.1 Types of market failure | ✅ | 2 definition |
| 1.3.2 Externalities | ✅ | 4 definition, 2 diagram, 1 chain |
| 1.3.3 Public goods | ✅ | 2 definition |
| 1.3.4 Information gaps | ✅ | 1 definition, 1 chain |
| 1.4.1 Government intervention in markets | ✅ | 3 definition, 2 diagram, 3 evaluation, 2 application |
| 1.4.2 Government failure | ✅ | 2 definition, 1 chain |

### Edexcel A (9EC0) — Theme 2 ✅ (deck `edexcel-a-theme-2`, 106 cards; 24 units, all approved)

| Unit | Status | Cards by type |
| --- | --- | --- |
| 2.1.1 Economic growth | ✅ | 3 definition, 1 formula, 1 evaluation |
| 2.1.2 Inflation | ✅ | 2 definition, 1 formula, 1 calculation, 1 chain, 1 evaluation, 2 diagram |
| 2.1.3 Employment & unemployment | ✅ | 4 definition, 1 calculation, 1 evaluation |
| 2.1.4 Balance of payments | ✅ | 2 definition, 1 calculation, 1 chain |
| 2.2.1 Aggregate demand | ✅ | 2 definition, 1 formula, 1 calculation, 1 diagram |
| 2.2.2 Consumption | ✅ | 3 definition |
| 2.2.3 Investment | ✅ | 2 definition, 2 chain |
| 2.2.4 Government expenditure | ✅ | 1 definition, 1 chain |
| 2.2.5 Net trade | ✅ | 2 definition, 1 chain |
| 2.3.1 Aggregate supply | ✅ | 3 definition, 1 diagram |
| 2.3.2 Short-run aggregate supply | ✅ | 1 definition, 1 diagram, 2 chain |
| 2.3.3 Long-run aggregate supply | ✅ | 2 definition, 4 diagram, 1 evaluation |
| 2.4.1 National income | ✅ | 2 definition, 1 diagram |
| 2.4.2 Injections & withdrawals | ✅ | 2 definition, 1 formula, 1 diagram |
| 2.4.3 Equilibrium levels of real national output | ✅ | 1 definition, 4 diagram |
| 2.4.4 The multiplier | ✅ | 2 definition, 1 chain, 1 formula, 1 calculation, 1 diagram |
| 2.5.1 Causes of growth | ✅ | 1 definition, 2 diagram, 1 chain |
| 2.5.2 Output gaps | ✅ | 1 definition, 3 diagram, 1 evaluation |
| 2.5.3 Trade cycle | ✅ | 2 definition, 1 diagram |
| 2.5.4 The impact of economic growth | ✅ | 2 evaluation |
| 2.6.1 Possible macroeconomic objectives | ✅ | 1 definition, 1 evaluation |
| 2.6.2 Demand-side policies | ✅ | 4 definition, 1 chain, 1 diagram, 1 evaluation |
| 2.6.3 Supply-side policies | ✅ | 2 definition, 1 diagram, 1 evaluation |
| 2.6.4 Conflicts between objectives and policies | ✅ | 1 definition, 1 diagram, 1 evaluation |

### Edexcel A (9EC0) — Theme 3 ✅ (deck `edexcel-a-theme-3`, 97 cards; 20 units, all approved)

| Unit | Status |
| --- | --- |
| 3.1.1 Sizes & types of firms | ✅ | 3 definition |
| 3.1.2 Business growth | ✅ | 2 definition, 1 evaluation |
| 3.1.3 Demergers | ✅ | 1 definition, 1 evaluation |
| 3.2.1 Business objectives | ✅ | 2 definition, 3 diagram |
| 3.3.1 Revenue | ✅ | 1 definition, 1 formula, 2 diagram |
| 3.3.2 Costs | ✅ | 1 formula, 1 calculation, 2 diagram |
| 3.3.3 Economies & diseconomies of scale | ✅ | 2 definition, 1 diagram, 1 evaluation |
| 3.3.4 Normal profits, supernormal profits & losses | ✅ | 3 definition, 3 diagram |
| 3.4.1 Efficiency | ✅ | 3 definition, 2 diagram, 1 evaluation |
| 3.4.2 Perfect competition | ✅ | 1 definition, 4 diagram, 1 chain |
| 3.4.3 Monopolistic competition | ✅ | 2 definition, 2 diagram, 1 evaluation |
| 3.4.4 Oligopoly | ✅ | 3 definition, 1 formula, 1 calculation, 3 diagram |
| 3.4.5 Monopoly | ✅ | 3 definition, 3 diagram, 1 evaluation |
| 3.4.6 Monopsony | ✅ | 1 definition, 1 evaluation |
| 3.4.7 Contestability | ✅ | 3 definition, 1 diagram |
| 3.5.1 Demand for labour | ✅ | 3 definition, 1 formula, 1 calculation, 1 diagram |
| 3.5.2 Supply of labour | ✅ | 4 definition, 1 diagram |
| 3.5.3 Wage determination | ✅ | 5 diagram, 1 formula, 1 evaluation |
| 3.6.1 Government intervention | ✅ | 5 definition, 1 diagram, 1 evaluation |
| 3.6.2 The impact of government intervention | ✅ | 2 definition, 1 evaluation |

### Edexcel A (9EC0) — Theme 4 ✅ (deck `edexcel-a-theme-4`, 84 cards; 21 units, all approved)

| Unit | Status | Cards by type |
| --- | --- | --- |
| 4.1.1 Globalisation | ✅ | 2 definition, 2 evaluation |
| 4.1.2 Specialisation & trade | ✅ | 2 definition, 1 diagram, 1 calculation, 1 evaluation |
| 4.1.3 Pattern of trade | ✅ | 2 definition |
| 4.1.4 Terms of trade | ✅ | 1 formula, 1 calculation, 1 evaluation |
| 4.1.5 Trading blocs & the WTO | ✅ | 4 definition |
| 4.1.6 Restrictions on free trade | ✅ | 2 definition, 1 diagram, 1 evaluation |
| 4.1.7 Balance of payments | ✅ | 3 definition, 1 calculation, 1 evaluation |
| 4.1.8 Exchange rates | ✅ | 3 definition, 3 diagram, 1 evaluation |
| 4.1.9 International competitiveness | ✅ | 2 definition, 1 formula, 1 calculation, 1 evaluation |
| 4.2.1 Absolute & relative poverty | ✅ | 3 definition |
| 4.2.2 Inequality | ✅ | 3 definition, 2 diagram, 1 formula, 1 evaluation |
| 4.3.1 Measures of development | ✅ | 4 definition, 1 evaluation |
| 4.3.2 Factors influencing growth & development | ✅ | 5 definition |
| 4.3.3 Strategies influencing growth & development | ✅ | 4 definition, 1 diagram, 1 evaluation |
| 4.4.1 Role of financial markets | ✅ | 1 definition |
| 4.4.2 Market failure in the financial sector | ✅ | 3 definition |
| 4.4.3 Role of central banks | ✅ | 2 definition |
| 4.5.1 Public expenditure | ✅ | 2 definition, 1 evaluation |
| 4.5.2 Taxation | ✅ | 1 definition, 1 diagram, 1 evaluation |
| 4.5.3 Public sector finances | ✅ | 3 definition, 1 evaluation |
| 4.5.4 Macroeconomic policies in a global context | ✅ | 2 definition, 1 evaluation |

### AQA (7136) — micro, site codes 1.x.y ≙ spec 4.1.x (deck `aqa-micro`, 185 cards; 54 units)

Sections 1.1–1.3, 1.5.11 and 1.8 are complete and approved (phase 1,
2026-08-05); sections 1.4 and 1.5 followed as phase 5 batches 1–2
(approved 2026-08-05). Section 1.6 is authored (batch 3, 2026-08-06,
awaiting review); 1.7 remains.

| Unit | Status | Cards by type |
| --- | --- | --- |
| 1.1.1 Economic methodology | ✅ | 5 definition |
| 1.1.2 Nature & purpose of economic activity | ✅ | 2 definition |
| 1.1.3 Economic resources | ✅ | 3 definition |
| 1.1.4 Scarcity, choice & the allocation of resources | ✅ | 2 definition, 1 chain |
| 1.1.5 Production possibility diagrams | ✅ | 1 definition, 2 diagram, 1 chain |
| 1.2.1 Consumer behaviour | ✅ | 4 definition, 1 diagram |
| 1.2.2 Imperfect information | ✅ | 1 definition, 1 chain |
| 1.2.3 Aspects of behavioural economic theory | ✅ | 6 definition |
| 1.2.4 Behavioural economics & economic policy | ✅ | 3 definition, 1 application |
| 1.3.1 Determinants of demand | ✅ | 1 definition, 1 diagram |
| 1.3.2 PED, YED, XED | ✅ | 1 definition, 3 formula, 1 calculation, 1 chain |
| 1.3.3 Determinants of supply | ✅ | 1 definition, 1 diagram |
| 1.3.4 Price elasticity of supply | ✅ | 1 definition, 1 formula, 1 calculation |
| 1.3.5 Determination of equilibrium market prices | ✅ | 1 definition, 2 diagram, 1 chain |
| 1.3.6 Interrelationship between markets | ✅ | 3 definition |
| 1.4.1 Production & productivity | ✅ | 1 definition, 1 formula |
| 1.4.2 Specialisation, division of labour & exchange | ✅ | 2 definition, 1 evaluation |
| 1.4.3 Law of diminishing returns & returns to scale | ✅ | 3 definition |
| 1.4.4 Costs of production | ✅ | 1 formula, 1 calculation, 2 diagram |
| 1.4.5 Economies & diseconomies of scale | ✅ | 2 definition, 1 diagram |
| 1.4.6 Marginal, average & total revenue | ✅ | 1 formula, 1 calculation, 2 diagram |
| 1.4.7 Profit | ✅ | 2 definition, 2 diagram |
| 1.4.8 Technological change | ✅ | 2 definition |
| 1.5.1 Market structures | ✅ | 2 definition |
| 1.5.2 The objectives of firms | ✅ | 2 definition, 3 diagram |
| 1.5.3 Perfect competition | ✅ | 1 definition, 3 diagram, 1 chain |
| 1.5.4 Monopolistic competition | ✅ | 1 definition, 2 diagram |
| 1.5.5 Oligopoly | ✅ | 2 definition, 1 formula, 2 diagram |
| 1.5.6 Monopoly & monopoly power | ✅ | 2 definition, 2 diagram |
| 1.5.7 Price discrimination | ✅ | 2 definition, 1 diagram |
| 1.5.8 Dynamics of competition | ✅ | 2 definition |
| 1.5.9 Contestable & non-contestable markets | ✅ | 2 definition, 1 diagram |
| 1.5.10 Market structure, efficiency & resource allocation | ✅ | 1 definition, 2 diagram, 1 evaluation |
| 1.5.11 Consumer & producer surplus | ✅ | 1 definition, 1 diagram, 1 chain |
| 1.6.1 Demand for labour, marginal productivity theory | ✅ | 3 definition, 1 formula, 1 calculation, 1 diagram |
| 1.6.2 Influences upon the supply of labour | ✅ | 4 definition |
| 1.6.3 Wage determination: perfectly competitive labour markets | ✅ | 1 diagram, 1 chain |
| 1.6.4 Wage determination: imperfectly competitive labour markets | ✅ | 1 definition, 1 diagram |
| 1.6.5 Trade unions, wages & employment | ✅ | 1 formula, 2 diagram |
| 1.6.6 The national minimum wage | ✅ | 1 diagram, 1 evaluation |
| 1.6.7 Discrimination in the labour market | ✅ | 3 definition |
| 1.7.1 Distribution of income & wealth | ✅ | 3 definition, 2 diagram, 1 formula, 1 evaluation |
| 1.7.2 The problem of poverty | ✅ | 2 definition, 1 chain |
| 1.7.3 Government policies: poverty & income distribution | ✅ | 1 definition, 1 evaluation |
| 1.8.1 How markets & prices allocate resources | ✅ | 2 definition, 1 evaluation |
| 1.8.2 The meaning of market failure | ✅ | 3 definition |
| 1.8.3 Public, private & quasi-public goods | ✅ | 3 definition |
| 1.8.4 Positive & negative externalities | ✅ | 2 definition, 4 diagram |
| 1.8.5 Merit & demerit goods | ✅ | 3 definition |
| 1.8.6 Market imperfections | ✅ | 2 definition |
| 1.8.7 Competition policy | ✅ | 1 definition |
| 1.8.8 Public ownership, privatisation, regulation & deregulation | ✅ | 3 definition |
| 1.8.9 Government intervention in markets | ✅ | 2 definition, 4 diagram |
| 1.8.10 Government failure | ✅ | 1 definition, 1 chain |

### AQA (7136) — macro, site codes 2.x.y ≙ spec 4.2.x (deck `aqa-macro`, 104 cards; 25 units)

| Unit | Status |
| --- | --- |
| 2.1.1 Objectives of government economic policy | ✅ | 2 definition, 1 evaluation |
| 2.1.2 Macroeconomic indicators | ✅ | 3 definition, 1 formula |
| 2.1.3 Uses of index numbers | ✅ | 2 definition, 1 formula, 1 calculation |
| 2.1.4 Uses of national income data | ✅ | 3 definition, 1 evaluation |
| 2.2.1 Circular flow of income | ✅ | 2 definition, 1 diagram |
| 2.2.2 AD/AS analysis | ✅ | 1 definition, 3 diagram, 1 chain |
| 2.2.3 Determinants of aggregate demand | ✅ | 3 definition, 1 chain |
| 2.2.4 Aggregate demand & the level of economic activity | ✅ | 1 definition, 1 formula, 1 diagram |
| 2.2.5 Determinants of short-run aggregate supply | ✅ | 1 definition, 1 diagram |
| 2.2.6 Determinants of long-run aggregate supply | ✅ | 2 definition, 2 diagram |
| 2.3.1 Economic growth & the economic cycle | ✅ | 1 definition, 2 diagram, 2 evaluation |
| 2.3.2 Employment & unemployment | ✅ | 4 definition, 1 evaluation |
| 2.3.3 Inflation & deflation | ✅ | 1 definition, 2 diagram, 1 formula, 1 evaluation |
| 2.3.4 Conflicts between macroeconomic policy objectives | ✅ | 1 definition, 2 diagram |
| 2.4.1 Structure of financial markets & financial assets | ✅ | 4 definition, 1 formula, 1 calculation |
| 2.4.2 Commercial banks & investment banks | ✅ | 4 definition |
| 2.4.3 Central banks & monetary policy | ✅ | 3 definition, 1 diagram, 1 evaluation |
| 2.4.4 Regulation of the financial system | ✅ | 1 definition, 1 formula, 1 evaluation |
| 2.5.1 Fiscal policy | ✅ | 4 definition, 1 diagram |
| 2.5.2 Supply-side policies | ✅ | 2 definition, 1 diagram |
| 2.6.1 Globalisation | ✅ | 2 definition, 1 evaluation |
| 2.6.2 Trade | ✅ | 4 definition, 2 diagram |
| 2.6.3 The balance of payments | ✅ | 2 definition, 1 calculation, 1 evaluation |
| 2.6.4 Exchange rate systems | ✅ | 2 definition, 2 diagram |
| 2.6.5 Economic growth & development | ✅ | 3 definition, 1 diagram, 1 evaluation |

### Integration wiring (audited 2026-08-05)

- Hub `/flashcards/` lists both existing decks ✓; nav dropdown entry ✓;
  inject-templates pageMap ✓; sitemap.xml has all three flashcard pages ✓.
- Theme 1 notes-page links blocks: 22/22 ✓ (shipped 2026-08-04).
- AQA notes-page links: 0 — blocked on approved AQA wording (the approved
  block says "Theme 1 deck"), and pointless until AQA units reach density.
- Every future deck must be wired as it ships: hub card, sitemap entries,
  notes-page links (with approved wording), and — for a new AQA macro deck —
  a `flashcards-data/aqa/macro.json` source and builder run.

## Decisions made (with reasons)

- **Pilot = full Edexcel Theme 1 (~110–115 cards) + ~12–15 AQA variant cards.**
  Theme 1 is foundational micro with the richest diagram ground truth, and
  nearly every topic has an AQA twin, so the board-variant machinery gets
  exercised in the pilot. (Eliot approved, 2026-08-04.) **The pilot is the
  start of the full two-board scope above, not the whole project.**
- **Hybrid card text.** Fronts/backs are card-optimised prose cross-checked
  against `glossary-data/terms.json` and the official specs; where the notes'
  `key-definition` chip is already tight it is reused verbatim, recorded via
  `source.origin: "notes-verbatim"` and verified by the builder against the
  source page (the glossary's verification idea, reused). (Eliot approved.)
- **URLs top-level `/flashcards/`**, nav entry inside the Revision Notes
  dropdown, card on the revision-notes hub. Matches the /practice-questions/
  precedent; flashcard pages light up the `revision-notes` nav item, the way
  the question bank lights up `past-papers`. (Eliot approved.)
- **Architecture is the house idiom**: `flashcards-data/` source (excluded from
  publishing) → `scripts/build_flashcards.py` → static crawlable landing pages
  with sample cards baked in + public deck JSON fetched at runtime by
  `js/components/flashcards.js` (question-search.js boot pattern). Chosen
  because the MCQ feature turned out to be build-time static, not runtime JSON;
  static-first degrades gracefully and keeps SEO pages real HTML.
- **Premium gating happens in the builder**: `premium: true` cards never enter
  the public payloads. The repo is public (confirmed via the GitHub API), so
  premium content ultimately cannot live here at all — see the architectural
  note in CLAUDE.md.
- **Formulae are KaTeX pre-rendered at build time** into the public JSON
  (glossary precedent, `css/vendor/katex/` already self-hosted). No runtime
  MathJax dependency for the player.
- **SVGs are separate files** in `images/diagrams/svg/`, referenced by
  `svgRef` — cacheable, reusable by notes pages later, keeps deck JSON small.
- **SVG label fonts are the system humanist stack** (Helvetica/Arial), not
  Source Sans Pro: SVGs loaded via `<img>` cannot fetch webfonts, so declaring
  the site font would render inconsistently across machines. Documented in
  docs/DIAGRAM_STYLE.md.
- **Self-QA renders use headless Google Chrome** (150 installed). No
  rsvg-convert/ImageMagick/Inkscape on this machine.
- **localStorage follows quiz.js verbatim**: `ea-flashcards:v2:` prefix
  (bumped from `:v1:` by the 2026-08-07 QA pass, which split six cards and so
  changed the card-id set — see docs/QA_FIXES_PROGRESS.md),
  availability probe, key index for global reset.
- **GA4 events** (site's first custom events): `deck_start`, `card_flip`,
  `card_rated`, `deck_complete`, `deck_print`, all with `board`/`theme`/
  `deck_id`, wrapped so they no-op silently without gtag.

## Working state and QA

On branch `flashcards-feature`. The tree is NOT clean by design:
everything from Theme 3 batch 3 onward sits approved but uncommitted
(Eliot's commit pause). Style guide LOCKED (docs/DIAGRAM_STYLE.md). Automated checks all green and continuously
re-run: geometry (43 SVGs), HTML, links, glossary, Liquid, text/markup
integrity, build idempotency.

QA still open (needs a real browser/deploy): real print-dialog check to
close the loop on the 2026-08-04 print fix, GA4 DebugView once deployed,
keyboard/screen-reader spot check, DevTools device-mode mobile.

Useful QA techniques:

- Player states: copy the built deck page into `_working/`, append a script
  that clicks `.fc-step`/`.fc-card`, serve the repo root with
  `python3 -m http.server`, shoot with headless Chrome
  (`--virtual-time-budget=6000`). Mobile-width right-edge overflow in
  headless renders is site baseline, not a flashcards regression.
- Print: stub `window.print`, click "Print this deck", render with Chrome
  `--print-to-pdf`, extract text via Swift PDFKit. PDF text sees CSS
  `text-transform: uppercase` output, so probe for "ANSWER" not "Answer".
  Proof renders in `_working/flashcards/print-qa/`.

## Completed work

- 2026-08-04 — Orientation: mapped MCQ build pattern, runtime-fetch precedent,
  localStorage idiom, diagram inventory (112 PNGs), GA4 placement, SVG tooling;
  confirmed repo is public. Phase 1 plan approved by Eliot.
- 2026-08-04 — Scaffolding: branch `flashcards-feature`; CLAUDE.md Flashcards
  section (standing rules + architectural note verbatim); `flashcards-data/`
  added to `_config.yml` exclude; ROADMAP updated (glossary flashcard idea
  superseded); this file, docs/DIAGRAM_STYLE.md (draft), docs/CONTENT_ISSUES.md
  created.
- 2026-08-04 — Proof diagrams: `demand-curve-shift.svg`,
  `indirect-tax-incidence.svg`, `overproduction.svg` authored from visual
  inspection of their ground-truth PNGs + notes captions, rendered via
  headless Chrome at 800×600 and 400×300, one defect caught and fixed in
  self-QA (clipped `D=MPB=MSB` label).
- 2026-08-04 — **Eliot's review caught what visual self-QA missed**: demand
  curve at slope 0.86 against guides computed for slope 1 in two diagrams.
  Fixed (all straight curves exact 45°); countermeasures locked in:
  `scripts/verify_diagram_geometry.py` (mandatory `<!-- geometry -->`
  declarations, algebraic checks) plus zoomed-viewBox close-ups of every
  junction in the visual pass.
- 2026-08-04 — Card batches 1–4 (95 cards, 17 SVGs) and the AQA starter deck
  (13 cards) all approved by Eliot. Integration shipped: nav, pageMap, hub
  button, sitemap.
- 2026-08-04 — Print-this-deck bug (empty PDF) diagnosed and fixed —
  printsheet moved out of the print-hidden mount; verified via headless
  print-to-PDF with PDFKit text extraction and visual renders.
- 2026-08-04 — Approved "Revise this topic with flashcards" block added to
  all 22 Theme 1 topic pages, each deep-linking `?topic=<page-slug>`.
  Hand-edited; verify_html, verify_links, text/markup integrity all green.
- 2026-08-05 — Full-scope re-grounding: coverage matrix built from a repo
  audit (decks, SVGs, pages, wiring); this file restructured around the
  FULL PROJECT SCOPE statement.
- 2026-08-05 — Build order approved (Option A, paired mirrors; single
  deck per AQA side). **Phase 1 built and approved**: AQA micro batches
  1–3 (76 new cards — sections 1.1–1.3 complete, 1.2/1.8 top-ups,
  1.5.11, 1.8 complete) with three new SVGs (total-utility,
  underproduction, overconsumption completing the externality quadrants).
  CONTENT_ISSUES 3–5 (AQA 1.8.9 captions) approved and fixed;
  subsidy-gov-expenditure.svg drawn and attached.
- 2026-08-05 — **Phase 2 started and approved through section 2.2**:
  `edexcel-a-theme-2` deck created (sitemap entry added, hub automatic);
  batch 1 (21 cards, section 2.1) and batch 2 (17 cards, section 2.2,
  with ad-shift.svg opening the AD/AS family) both approved by Eliot.
- 2026-08-05 — **Theme 2 batch 3 approved by Eliot** (same day), with one
  amendment: he chose to ship **both** LRAS-shift variants, so
  `lras-shift-keynesian.svg` was drawn from the left panel of
  lras-shift.png (same self-QA loop) and card
  `edexcel-a-2-3-3-diagram-04` added; the classical card's front gained
  the word "classical" to keep the pair distinct. Batch as built:
  16 cards (section 2.3 complete — 4 + 4 + 6 across the three units —
  plus the two deferred 2.1.2 demand-pull/cost-push diagram cards) and
  seven SVGs (sras-movements, sras-shift, lras-classical,
  lras-keynesian, lras-shift, ad-shift-right, sras-shift-left), each
  drawn from visual inspection of its ground-truth PNG and passed
  through the full self-QA loop (geometry checker zero flags, 800×600
  render, zoomed junction close-ups, 400×300 legibility). One defect
  caught in self-QA: Keynesian Yfe label crowding "Real GDP" — curve
  moved left. lras-shift deliberately draws only the classical panel
  of the two-panel ground-truth PNG (decision pending Eliot). Both
  verbatim cards (SRAS, LRAS chips) pass the builder's check; all
  verifiers green; build idempotent.
  Matrix: 57 ✅ · 3 🟡 · 106 ❌; 238 cards, 29 SVGs, three decks.

- 2026-08-05 — **Theme 2 batch 4 authored and built, awaiting review**:
  18 cards completing section 2.4 (circular flow, injections &
  withdrawals with the J=W equilibrium formula, classical vs Keynesian
  equilibrium with all four AD/LRAS shift diagrams, and the multiplier
  with formulae, an original calculation and the three-AD diagram) plus
  seven SVGs, each drawn from visual inspection of its ground-truth PNG
  and through the full self-QA loop (zero geometry flags, junction
  close-ups all exact, mobile legible). The two circular-flow SVGs open
  a schematic diagram class (no axes; ring + directional arrows; teal
  injections, red withdrawals — palette extension to confirm with
  Eliot). CONTENT_ISSUES #6 logged (multiplier.png caption/figure
  mismatch), left open. Matrix: 60 ✅ · 4 🟡 · 102 ❌; 257 cards, 37
  SVGs.

- 2026-08-05 — **Theme 2 batch 5 authored and built, awaiting review**:
  30 cards covering ALL of sections 2.5–2.6 (causes of growth with both
  PPF diagrams, output gaps in classical and Keynesian models, trade
  cycle, impact of growth, the seven objectives, monetary/fiscal policy
  with QE and the MPC, supply-side policies, conflicts with the SRPC)
  and six new SVGs (ppf-short-run-growth, negative-output-gap-classical
  and -keynesian, positive-output-gap-classical, trade-cycle — first
  use of shaded boom/recession lenses, teal/red per the approved
  schematic palette — and short-run-phillips-curve), all through the
  full self-QA loop with zero geometry flags. Four batch-4 SVGs and
  ppf-growth-decline are reused on policy/growth cards. The MPC card
  (2-6-2-def-04) is spec-sourced: the notes never cover the Monetary
  Policy Committee (see Open questions). Matrix: 64 ✅ · 8 🟡 · 94 ❌;
  287 cards, 43 SVGs.

- 2026-08-05 — **Phase 3 opened: AQA macro deck created** with batch 1
  (15 cards, section 2.1 complete: objectives in AQA's four-main
  framing, indicators, index numbers with an original weighted-CPI
  calculation, national income data with PPP — five notes-verbatim
  cards). Deck auto-discovered by the builder, sitemap entry added,
  hub automatic. Notes gaps found: 2-1-2 lists productivity in its
  spec-alert but has no productivity section (covered lightly from
  the spec on aqa-2-1-2-def-03). Matrix: 72 ✅ · 4 🟡 · 90 ❌; 302
  cards, 43 SVGs, four decks.

- 2026-08-05 — **AQA macro batch 2 authored and built, awaiting
  review**: 21 cards completing section 2.2 (circular flow, AD/AS
  analysis, determinants of AD with the accelerator, the multiplier in
  AQA's MPC-only framing, SRAS/LRAS determinants with AQA's own lists
  and the Keynesian AS curve). One new SVG — ad-movements.svg, drawn
  from ad-movements.png on the sras-movements idiom, full QA loop —
  and seven reuses from the shared library (circular flow, ad-shift,
  negative-output-gap-classical, multiplier, sras-shift,
  lras-keynesian, lras-shift), each checked against the PNG its AQA
  page actually displays. CONTENT_ISSUES #7 logged (AQA 2-2-4
  multiplier caption, twin of fixed #6) — open. Notes gaps: 2-2-3 has
  no explicit determinants-of-saving or saving-vs-investment section
  (spec 4.2.2.3); covered on cards from the spec. Matrix: 72 ✅ ·
  10 🟡 · 84 ❌; 323 cards, 44 SVGs.

- 2026-08-05 — **AQA macro batches 1–2 approved by Eliot** (same
  day). CONTENT_ISSUES #7 approved and fixed with the Edexcel twin's
  wording; integrity checks confirmed the caption was the only
  change. Sections 2.1–2.2 flipped to ✅.

- 2026-08-05 — **AQA macro batch 3 authored and built, awaiting
  review**: 26 cards completing sections 2.3 and 2.5 (growth and the
  cycle with AQA's cyclical-instability list, unemployment with the
  natural rate and both UK measures, inflation with Fisher's MV=PQ
  and the Quantity Theory, conflicts with BOTH Phillips curves,
  fiscal policy through to cyclical/structural deficits and the OBR,
  supply-side policies with the policies-vs-improvements
  distinction). Two new SVGs — long-run-phillips-curve (vertical at
  NRU, SRPC1/SRPC2 at 2%/5%) and laffer-curve (one self-QA catch:
  t2 label collided with the axis title; descent vertex moved left)
  — plus seven shared-library reuses, each checked against the PNG
  its AQA page displays. Matrix: 82 ✅ · 6 🟡 · 78 ❌; 349 cards, 46
  SVGs.

- 2026-08-05 — **AQA macro batch 3 approved by Eliot** (same day) —
  phase 3 complete. Sections 2.3 and 2.5 flipped to ✅.

- 2026-08-05 — **Phase 4 opened: Theme 3 deck created** with batch 1
  (13 cards, sections 3.1–3.2: firm growth and the principal-agent
  problem, integration types, demergers, and the four business
  objectives with their rules). The **firm-diagram family** ships its
  first three SVGs (profit-max, revenue-max, sales-max): shared
  canonical layout — D=AR, MR at twice the slope from the same
  intercept, J-shaped MC=S through AC's exact minimum (470,405), all
  crossings computed algebraically. Two self-QA catches: MC initially
  crossed AC on its falling arm (economically wrong — caught by
  reading the verifier's crossing list, not the render); and wide
  two-line axis titles crossed the y-axis stroke (fixed here and on
  laffer-curve by single-line titles above the axis top). The
  unlabelled fifth curve in the ground-truth PNGs is deliberately
  omitted (fails the every-curve-labelled rule) — flagged for Eliot.
  CONTENT_ISSUES #8 logged ("choose to satisficing" ×2 on 3-2-1),
  open. Matrix: 88 ✅ · 4 🟡 · 74 ❌; 362 cards, 49 SVGs, five decks.

- 2026-08-05 — **Theme 3 batch 1 approved by Eliot** (same day),
  including the firm-diagram adaptations. CONTENT_ISSUES #8 approved
  and fixed. Sections 3.1–3.2 flipped to ✅.

- 2026-08-05 — **Theme 3 batch 2 authored and built, awaiting
  review**: 12 cards covering revenue (TR/AR/MR with both market
  types and the PED total-revenue rule), costs (the seven measures,
  an original cost-schedule calculation where MC meets AC at £15,
  short-run curves, the LRAC envelope) and economies of scale (six
  internal types, MES diagram, internal vs external, diseconomies).
  Five new SVGs: revenue-perfect-competition and
  revenue-imperfect-competition (each combining its two-panel ground
  truth into one panel), short-run-costs (MC through the exact minima
  of BOTH AVC and AC), long-run-costs (LRAC envelope, SRAC2 kissing
  the minimum exactly, SRACs in teal as second-original curves) and
  economies-of-scale (MES + annotation arrows). All crossings
  computed; zero geometry flags. Matrix: 92 ✅ · 3 🟡 · 71 ❌; 374
  cards, 54 SVGs.

- 2026-08-05 — **Theme 3 batch 2 approved by Eliot** (same day),
  including the combined-panel revenue adaptation. Sections
  3.3.1–3.3.3 flipped to ✅. Session ended here by Eliot's request;
  the Next steps block below is the resume point, with the reusable
  firm-diagram geometry recorded for batch 3.

- 2026-08-05 — **Theme 3 batch 3 authored and built, awaiting
  review**: 18 cards covering 3.3.4 (normal/supernormal profit and
  loss with TR-vs-TC definitions, normal-profit-as-a-cost, both
  shaded firm diagrams, the shut-down rules and the shut-down
  diagram), 3.4.1 (all four efficiency types, static efficiency as
  a notes-verbatim chip card, efficiency in perfect and imperfect
  competition, the static-vs-dynamic evaluation) and 3.4.2
  (characteristics/price taker, the two-panel market-price diagram,
  short-run profit and loss, the entry/exit adjustment chain,
  long-run equilibrium). Eight new SVGs on the recorded
  firm-diagram base: supernormal-profit, loss (AC raised to a min
  at 505,300 on MC), short-run-shutdown-condition (AVC min 505,300
  and ATC min 530,150 both exactly on an extended MC),
  efficiency-perfect-competition (price line tangent at the
  470,405 triple point), efficiency-imperfect-competition
  (efficiency points at AC min and the computed MC×AR crossing
  485,373.7), perfect-competition-market-price (**first two-panel
  SVG**: market panel sets P1, dashed guide carries it to the firm
  panel), and the pc short-run profit/loss pair (horizontal price
  lines crossing MC at 505,300 and 437.9,445). Profit rectangles
  teal, loss rectangles red at 0.15 (trade-cycle palette).
  efficiency-perfect-competition.svg is shared by a 3.4.1 card and
  the 3.4.2 long-run card. Two defects caught in self-QA: clipped
  D=AR=MR=P1 labels at the canvas edge (both pc single-panel
  files) and the two-panel P1 label sitting on its dashed guide.
  All verifiers green; build idempotent (byte-identical hashes).
  Adaptations to flag for Eliot are in the batch presentation.
  Matrix: 95 ✅ · 3 🟡 · 68 ❌; 392 cards, 62 SVGs.

- 2026-08-05 — **Theme 3 batch 3 approved by Eliot** (same day),
  including all six flagged adaptations: single-panel shutdown
  diagram; the first two-panel SVG (market price); palette-colour
  efficiency markers with in-canvas key; teal/red profit/loss
  rectangles at 0.15; no MC=MR dot on the shutdown diagram; the
  long-run adjustment PNGs deliberately not drawn (chain card +
  long-run equilibrium diagram carry that story). Units 3.3.4,
  3.4.1, 3.4.2 flipped to ✅. **NOT committed — Eliot has paused
  commits**; the batch sits approved in the working tree.

- 2026-08-05 — **Theme 3 batch 4 authored and built, awaiting
  review**: 20 cards covering 3.4.3 (characteristics, SR
  equilibrium reusing supernormal-profit.svg exactly as the notes
  page reuses the PNG, the LR tangency diagram, efficiency, and a
  consumer-impact evaluation), 3.4.4 (characteristics, the
  concentration-ratio formula plus an original 81.25% calculation,
  overt/tacit collusion, the collusion diagram, the kinked demand
  curve, price/non-price competition, and the prisoner's dilemma)
  and 3.4.5 (pure/legal monopoly with a notes-verbatim chip,
  equilibrium reusing supernormal-profit.svg, efficiency,
  third-degree price discrimination definition and diagram, a
  stakeholder evaluation, and natural monopoly). Six new SVGs:
  normal-profit-imperfect-competition (AC tangent to AR at exactly
  393.1,304.8 with min on MC at 496,338), collusion (DWL triangle
  hugging MC via exact sub-Bezier control points, lowercase
  relative path per the trade-cycle precedent),
  kinked-demand-curve (MR gap 340→430 at Q with MC through it at
  430,370; AC min on MC at 390,435; rotated segment annotations),
  game-theory (schematic payoff matrix with the CORRECTED
  High/Low labels per CONTENT_ISSUES #9; collusion cell teal,
  Nash cell red), price-discrimination (two-panel, one shared
  AC=MC line, computed MR crossings at 185.7,380 and 613.3,380)
  and nationalisation-privatisation (falling LRAC/LRMC, private
  guides grey, nationalised guides red-dashed — palette
  adaptation to flag). Four defects caught in self-QA: DWL
  control-point flags, game-theory border rect invisible to the
  checker, the rotated inelastic label colliding with D=AR, and
  the MC tip poking into that label (MC now ends below the
  demand segment). Content issues #9–11 logged, all open. All
  verifiers green; build idempotent. Matrix: 98 ✅ · 3 🟡 ·
  65 ❌; 412 cards, 68 SVGs.

- 2026-08-05 — **Theme 3 batch 4 approved by Eliot** (same day)
  with all adaptations; 3.4.3–3.4.5 flipped to ✅. Content issues
  #9–11 approved and fixed: the stray "a" on 3-4-3 deleted
  (text-integrity confirms it is the only wording change);
  **both notes pages showing the incorrect game-theory.png now
  reference /images/diagrams/svg/game-theory.svg instead**
  (3-4-4-oligopoly and the microeconomics-diagrams gallery,
  width/height 800×600; the PNG is unreferenced and
  known-incorrect — never use it as ground truth); and
  price-discrimination.png patched in place via Swift +
  CoreGraphics ("peak tickets" at matched size/colour, visually
  verified, 3642×1080 unchanged), fixing all three pages that
  display it. Markup-integrity's two "lost src" reports are the
  approved swap. Still NOT committed — commit pause holds.

- 2026-08-05 — **Theme 3 batch 5 authored and built, awaiting
  review**: 12 cards covering 3.4.6 (monopsony definition as a
  notes-verbatim chip card plus the stakeholder evaluation — the
  unit has no diagrams by design, its labour-market diagram
  belongs to 3.5.3), 3.4.7 (contestable market and the
  competition-vs-contestability distinction, characteristics with
  hit-and-run entry, limit pricing REUSING sales-max.svg exactly
  as the notes page reuses sales-max.png, sunk costs and entry
  barriers) and 3.5.1 (demand for labour as a notes-verbatim chip
  card with derived demand, MRP = MPP × MR, an original £4/£50
  MRP calculation, the D(L)=MRP diagram, shifts, and wage
  elasticity of labour demand). One new SVG:
  demand-for-labour.svg (45° curve through exact guide corners
  330,260 and 460,390, first "3.5 Labour market" topic in the
  deck). Content issue #12 logged (3-4-7 barriers table lists
  "Economies of scale" twice), open. Spec verification against
  9EC0 p41; the 3-5-1 worked example's arithmetic recomputed and
  confirmed. All verifiers green; build idempotent. Matrix:
  101 ✅ · 3 🟡 · 62 ❌; 424 cards, 69 SVGs.

- 2026-08-05 — **Theme 3 batch 5 approved by Eliot** (same day);
  3.4.6, 3.4.7, 3.5.1 flipped to ✅. Content issue #12 approved
  and fixed: the duplicate "Economies of scale" row deleted from
  the 3-4-7 barriers table (text/markup integrity clean — the
  working tree's only wording changes remain the two approved
  fixes on 3-4-3 and 3-4-7). Still NOT committed — commit pause
  holds.

- 2026-08-05 — **Theme 3 batch 6 authored and built, awaiting
  review**: 12 cards covering 3.5.2 (supply of labour as a
  notes-verbatim chip card, the market/individual supply diagram
  with the backward bend and income-vs-substitution effects,
  shift factors, labour immobility as market failure, and supply
  elasticity) and 3.5.3 (competitive wage determination, the
  monopsony diagram with monopsonistic exploitation, trade
  union + union density as a notes-verbatim formula card, the
  union in a competitive market, the union-vs-monopsony bilateral
  monopoly, the national minimum wage, and its evaluation). Six
  new SVGs: wage-determination, min-wage and
  trade-union-competitive all reuse min-price.svg's exact
  approved geometry (S×D at 360,300; floor at 240 hitting D at
  300 and S at 420; #d52349 3px intervention lines with bold red
  labels); monopsony (MCL at exactly twice the supply slope from
  a shared apex, all crossings round: MCL×MRP 300,240, S×D
  355,295, Wm 300,350); trade-union-monopsony (monopsony base +
  the union's effective-MCL path in #d52349: flat at W(TU) to Qc,
  vertical jump to MCL at 355,130, then collinear along it); and
  supply-of-labour-market-individual (two-panel; the individual
  curve's rightmost point exactly at the W2 guide corner 633,265
  via a vertical-tangent joint). The heavy two-panel
  trade-union.png was split into two single-panel SVGs (shutdown
  precedent). Notes gaps found on 3.5.3: spec 3.5.3c maximum
  wages and public-sector wage setting, and 3.5.3b current
  labour market issues, have no notes coverage — logged in Open
  questions, no spec-sourced cards authored for them this batch.
  All verifiers green; build idempotent. Matrix: 104 ✅ · 2 🟡 ·
  60 ❌; 436 cards, 75 SVGs.

- 2026-08-05 — **Theme 3 batch 6 approved by Eliot** (same day);
  3.5.2 and 3.5.3 flipped to ✅. Still NOT committed — commit
  pause holds.

- 2026-08-05 — **Theme 3 batch 7 authored and built, awaiting
  review — the deck's final units**: 10 cards covering 3.6.1 (the
  CMA as a notes-verbatim chip card with merger control and
  Sainsbury's–Asda, price regulation RPI−X with profit
  regulation, quality standards and performance targets,
  promoting competition and contestability, nationalisation vs
  privatisation REUSING nationalisation-privatisation.svg as
  planned when it was drawn, the privatisation evaluation, and
  protecting suppliers/employees) and 3.6.2 (the five impact
  yardsticks — prices, quality, choice, profit, efficiency —
  regulatory capture with its two causes, and the
  limits-of-intervention evaluation ending in government
  failure). No new SVGs. Content issues #13 (four grammar slips
  on 3-6-1) and #14 (three on 3-6-2) logged, open — the
  regulatory-capture card is deliberately card-authored rather
  than verbatim because the chip sentence contains #14's
  "consumers interest" error. All verifiers green; build
  idempotent. **All 20 Theme 3 units are now authored** (97
  cards). Matrix: 106 ✅ · 2 🟡 · 58 ❌; 446 cards, 75 SVGs.

- 2026-08-05 — **Theme 3 batch 7 approved by Eliot** (same day):
  3.6.1 and 3.6.2 flipped to ✅ — **THEME 3 COMPLETE, and with it
  all three authored Edexcel themes**. Content issues #13–14
  approved and fixed (seven grammar corrections across the two
  3.6 pages; text-integrity shows exactly the four approved
  pages changed, glossary verifier still green). Phase 5 opens:
  AQA micro 1.4–1.6. Still NOT committed — commit pause holds.

- 2026-08-05 — **Phase 5 batch 1 authored and built, awaiting
  review**: 25 cards completing ALL of AQA section 1.4
  (production and productivity with the labour-productivity
  formula and a verbatim production chip; specialisation with
  Adam Smith's pin factory, its evaluation, and money as the
  answer to barter's double coincidence of wants; short run vs
  long run, diminishing returns and returns to scale; the
  seven-cost toolkit with an original £150-fixed-cost schedule
  and BOTH cost diagrams; six internal economies, the MES
  diagram, and diseconomies with the not-diminishing-returns
  distinction; TR/AR/MR with both revenue diagrams and an
  original TR-max-at-MR=0 calculation; profit in AQA's
  "abnormal" vocabulary with both profit/loss diagrams and the
  role of profit; invention vs innovation and technological
  change with creative destruction). **Zero new SVGs — six
  firm-family reuses** (short-run-costs, long-run-costs,
  economies-of-scale, revenue-perfect/imperfect-competition,
  supernormal-profit, loss), each checked against the PNG and
  caption its AQA page actually displays. All content verified
  against AQA 7136 spec pp36–38; both notes worked examples
  recomputed and confirmed. Creative destruction is
  spec-sourced (4.1.4.8 requires it; the notes never name it) —
  see Open questions. Notes gap: the spec's L-shaped LRAC
  (4.1.4.5) is uncovered by the notes and left off the cards.
  Content issues #15 ("the creation entirely new", 1-4-8) and
  #16 ("daily suppliers" for milk, 1-4-5) logged, open. All
  verifiers green; build idempotent. Matrix: 108 ✅ · 8 🟡 ·
  50 ❌; 471 cards, 75 SVGs.

- 2026-08-05 — **Phase 5 batch 1 approved by Eliot** (same day);
  the eight 1.4 rows flipped to ✅. Content issues #15–16 approved
  and fixed. #15 (the Inventions chip) is a glossary source, so
  the glossary was re-extracted and rebuilt per its documented
  pipeline — the rebuild also carried through issue #14's
  regulatory-capture correction, which the shipped glossary had
  still held in the old wording (caught because verify_glossary
  is now checked by exit code, not by eyeballing tail output).
  verify_glossary exits 0; glossary rebuild idempotent. Still NOT
  committed — commit pause holds.

- 2026-08-05 — **Phase 5 batch 2 authored and built, awaiting
  review**: 36 cards completing ALL of AQA 1.5.1–1.5.10 (the
  spectrum of competition with a verbatim chip; the three
  objective diagrams plus divorce of ownership and satisficing
  with AQA's extra objectives — CSR, survival, employee welfare;
  perfect competition mirroring the approved Edexcel set with the
  chain card carrying the long-run adjustment; monopolistic
  competition; oligopoly with CR formula, collusion and the
  kinked demand curve — NO game-theory card because the AQA page,
  unlike Edexcel's, never covers the prisoner's dilemma; monopoly
  with pure/legal verbatim chip and natural monopoly; price
  discrimination in AQA's three-degree framing; dynamics of
  competition with the creative-destruction verbatim chip and
  Kodak; contestability with limit pricing on sales-max.svg; and
  the efficiency set with the static-efficiency verbatim chip).
  **Zero new SVGs — 14 diagram cards, all library reuses**, each
  checked against the PNG its AQA page displays. Verified against
  AQA 7136 spec pp38–41; the 1-5-5 worked example (90% CR)
  recomputed and confirmed. Content issues #17 (1-5-7 calls
  second-degree PD "Purchasing Economies of Scale" — the card
  omits the claim) and #18 ("choose to satisficing" twice on
  1-5-2, the twin of fixed #8) logged, open. Notes gap: spec
  4.1.5.5's cooperation-vs-collusion distinction has no notes
  coverage (Open questions). NOTE: the batch-1 claim that the
  notes never name creative destruction was wrong — 1-5-8 does;
  the 1-4-8 card's mention is simply cross-unit. All verifiers
  green; build idempotent. Matrix: 116 ✅ · 10 🟡 · 40 ❌; 507
  cards, 75 SVGs.

- 2026-08-05 — **Phase 5 batch 2 approved by Eliot** (same day);
  all ten 1.5 rows flipped to ✅. Content issue #18 approved and
  fixed (both "choose to satisficing" corrected, no glossary
  coupling). **Content issue #17 REJECTED by Eliot** — he ruled
  that second-degree price discrimination and purchasing
  economies of scale are the same concept and the 1-5-7 page
  stays as written; the approved card (aqa-1-5-7-def-01) is
  silent on the equivalence, which stands. Session ended here at
  Eliot's request; the Next steps block below is the resume
  point. Still NOT committed — commit pause holds.

- 2026-08-06 — **Phase 5 batch 3 authored and built, awaiting
  review**: 22 cards covering ALL of AQA section 1.6 (labour).
  1.6.1 demand for labour with the verbatim chip, MRP = MPP × MR,
  an original £6/£60 MRP calculation (hires three workers), the
  D(L)=MRP diagram, shifts and demand elasticity; 1.6.2 supply of
  labour (verbatim chip) framed on the spec's monetary vs
  non-monetary considerations, shifts, immobility-as-market-failure
  with mobility policies (angled away from the existing
  aqa-1-8-6-def-02), and supply elasticity; 1.6.3 the competitive
  wage-determination diagram plus a market-forces chain card;
  1.6.4 the three causes of imperfect labour markets with monopsony
  (NHS example) and the monopsony diagram; 1.6.5 trade union
  verbatim chip + union density formula, and the union-in-
  competitive / union-vs-monopsony (bilateral monopoly) diagram
  pair; 1.6.6 the NMW diagram card (verbatim chip) and its
  evaluation; 1.6.7 discrimination with the wage-discrimination
  verbatim chip, the four necessary conditions, and forms/impacts.
  **Zero new SVGs — six labour-family reuses** (demand-for-labour,
  wage-determination, monopsony, trade-union-competitive,
  trade-union-monopsony, min-wage), each re-verified visually
  against the PNG its AQA page actually displays (same ground-truth
  files as the Edexcel 3.5 twins). Verified against AQA 7136 spec
  4.1.6 (pp42–43, extracted via Swift+PDFKit); the 1-6-1 worked
  example recomputed and confirmed (three workers at £80).
  **Board difference honoured**: spec 4.1.6.2 explicitly excludes
  the backward-bending individual supply curve, so the AQA deck
  ships NO supply-of-labour diagram card and the 1.6.2 cards stay
  silent on the bend (the notes page does teach it) — decision
  flagged for Eliot. The 1.6.3 chain card is deliberately
  card-authored around content issue #20's error. Content issues
  #19 (spec-alert says "wage discrimination" for "wage
  determination", 1-6-3) and #20 (below-equilibrium bullet says
  employment decreases as the wage rises to equilibrium, 1-6-3)
  logged, both open. Notes gap: spec 4.1.6.7's advantages of wage
  discrimination for employers/the economy has no notes coverage
  (Open questions). All verifiers green (geometry 75/0, HTML 185/0,
  links 0 broken, glossary exit 0, liquid exit 0); text/markup
  integrity vs HEAD shows only the previously approved changes;
  build idempotent (byte-identical hashes). Matrix: 126 ✅ · 7 🟡 ·
  33 ❌; 529 cards, 75 SVGs. Still NOT committed — commit pause
  holds.

- 2026-08-06 — **Phase 5 batch 3 approved by Eliot** (same day);
  all seven 1.6 rows flipped to ✅ — **AQA section 1.6 complete**.
  Eliot ratified the backward-bend exclusion: the curve stays out
  of the AQA cards AND the 1-6-2 notes page stays as written.
  Content issues #19–20 approved and fixed (two wording
  corrections on 1-6-3: "wage determination" in the spec-alert,
  and the below-equilibrium bullet now says employment increases;
  no glossary coupling — the page has no chips; verify_html
  clean, diff confirmed to be exactly the two approved changes).
  Phase 5 batch 4 (AQA 1.7, the micro deck's final section)
  opens next. Still NOT committed — commit pause holds.

- 2026-08-06 — **Phase 5 batch 4 authored and built, awaiting
  review — the AQA micro deck's final section**: 12 cards
  covering ALL of AQA 1.7 (1.7.1 income vs wealth with the
  flow/stock distinction and verbatim chip, the Lorenz curve
  diagram, the Gini = A ÷ (A + B) formula card with AQA's
  interpret-don't-calculate note, the six distribution factors,
  equality vs equity (verbatim chip) with the three
  perspectives, the Kuznets curve diagram, and the
  benefits-vs-costs-of-inequality evaluation; 1.7.2 absolute vs
  relative poverty (verbatim chip, $2.15/day 2022 PPP and UK
  60%-of-median thresholds), the poverty-trap chain card
  covering both notes cycles, and the five economic
  consequences; 1.7.3 the six policies and the
  unintended-consequences / opportunity-cost /
  equity-vs-efficiency evaluation). **Two new SVGs**:
  lorenz-curve.svg (square plot 130,520–590,60 for an exact 45°
  equality line, Lorenz as teal second-original Q-Bezier through
  both endpoints, A/B area letters, dashed square-completion
  guides) and kuznets-curve.svg (inverted-U cubic with apex at
  exactly 395,177.5, dashed guide ending on the apex,
  developing/developed labels) — both drawn from visual
  inspection of their ground-truth PNGs on 1-7-1, zero geometry
  flags, full self-QA loop. One defect class caught in self-QA:
  dash-phase gaps left guide ends visibly short of their
  junctions; fixed by drawing guides FROM the junction so ink
  starts exactly there (note for future SVGs). The Kuznets card
  is page content but NOT in the AQA spec (no exclusion either
  — flagged for Eliot in the batch presentation). Verified
  against AQA 7136 spec 4.1.7 (pp44–45). Content issues #21
  (1-7-2 sentence ends in comma) and #22 (1-7-1 spec-alert
  "wealth,measure") logged, open. Notes gaps: spec additional
  info on UK income/wealth distribution data and on excessive
  inequality as both cause and consequence of market failure
  have no notes coverage (kept notes-grounded). All verifiers
  green; build idempotent; only 1-6-3 joins the approved-change
  set in text integrity. Matrix: 133 ✅ · 3 🟡 · 30 ❌; 541
  cards, 77 SVGs. Still NOT committed — commit pause holds.

- 2026-08-06 — **Phase 5 batch 4 approved by Eliot** (same day),
  including both new diagrams and the Kuznets card (ratified in:
  page content beyond the spec is fine here) — all three 1.7
  rows flipped to ✅ and **the AQA micro deck is COMPLETE: 54
  units, 184 cards, phase 5 closed**. Content issues #21–22
  approved and fixed: the 1-7-2 comma-for-full-stop (the
  Relative poverty chip is a glossary source, so the glossary
  was re-extracted and rebuilt — verify_glossary exits 0, and
  the rebuild is the only glossary change beyond the previously
  approved set) and the 1-7-1 "wealth,measure" missing space.
  Text integrity now shows exactly the approved set: the nine
  prior files plus 1-6-3, 1-7-1 and 1-7-2. Phase 6 (Edexcel
  Theme 4, new deck) opens. Still NOT committed — commit pause
  holds.

- 2026-08-06 — **Phase 6 opened: Theme 4 deck created**
  (`flashcards-data/edexcel-a/theme-4.json`, themeName "Theme 4:
  A Global Perspective"; builder auto-discovered it, hub card
  automatic, sitemap entry added for
  /flashcards/edexcel-a/theme-4/) **with batch 1 authored and
  built, awaiting review**: 18 cards covering 4.1.1–4.1.5
  (globalisation with verbatim chip, its six drivers, and
  impacts split across two evaluation cards by stakeholder;
  absolute vs comparative advantage with verbatim chip, the PPF
  diagram, an original cars/wheat opportunity-cost calculation
  where the absolute-advantage country still specialises, the
  five model assumptions, and the trade evaluation; pattern of
  trade verbatim chip and its four factors with the UK
  manufacturing/Brexit/exchange-rate examples; the ToT formula
  card, an original 108/120 → 90 calculation, and the
  PED-hinged impact evaluation; the four-bloc integration
  ladder, trade creation vs diversion, monetary-union success
  conditions, and the WTO's role and bloc tension). **One new
  SVG**: comparative-advantage.svg (Germany PPF 100,100→600,520
  and Vietnam PPF 100,205→350,520 on shared axes, teal
  second-original for Vietnam, zero geometry flags, full
  self-QA loop — one authoring catch: the Vietnam label's first
  position clipped the Germany PPF, recomputed to the
  between-PPF gap at 315,460). Verified against 9EC0 spec 4.1
  (p44 extracted via Swift+PDFKit) — all five units' spec
  bullets covered. The 4-1-4 worked example recomputed (94.6,
  104.5 both ✓). **Content issue #23 logged: 4-1-2's claimed
  post-specialisation total of "20m computer chips and 200mn
  T-shirts" is arithmetically impossible against its own
  figure** — the cards avoid the broken total, carrying only
  the correct opportunity costs and the qualitative gain. #24
  logged (4-1-4 missing full stop). Both open. All verifiers
  green (geometry 78/0, HTML 186/0, links 0 broken); build
  idempotent; no notes pages touched this batch. Matrix:
  136 ✅ · 5 🟡 · 25 ❌; 559 cards, 78 SVGs, six decks. Still
  NOT committed — commit pause holds.

- 2026-08-06 — **Theme 4 batch 1 approved by Eliot** (same day),
  who chose his own remedy for content issue #23: keep FULL
  specialisation (students are not taught partial
  specialisation) and change the numbers so it works. Since
  absolute-advantage-in-both can never yield a both-goods gain
  under full specialisation from half-half baselines, the
  T-shirt maxima were swapped (Germany 20mn chips/150mn
  T-shirts; Vietnam 10mn chips/200mn T-shirts) — the page's
  existing totals (15m + 175mn → 20m + 200mn) become exactly
  correct. Applied: comparative-advantage.svg redrawn to the
  new numbers (PPFs now cross at the computed point 200,268;
  full self-QA loop rerun); 4-1-2 swapped to the SVG
  (game-theory precedent) with the absolute-advantage
  paragraph, midpoint outputs, four opportunity-cost bullets
  (7.5/20 and 0.13/0.05) and caption updated; and the 4.1.2
  diagram card's back/svgAlt revised to match — **that one
  card changed after approval and needs re-review** (4.1.2 row
  🟡). Four rows flipped ✅ (4.1.1, 4.1.3–4.1.5). Issue #25
  logged, open: the AQA twin 2-6-2-trade repeats the old broken
  example verbatim and, with macroeconomics-diagrams.html,
  still displays the old-numbers PNG — proposed fix is the
  approved 4-1-2 treatment verbatim; until ruled on, the site
  shows two contradictory versions of the figure.
  comparative-advantage.png: do not use as ground truth — the
  SVG is authoritative. All verifiers green; build idempotent;
  text integrity = the approved set + 4-1-2. Matrix: 140 ✅ ·
  1 🟡 · 25 ❌; 559 cards, 78 SVGs. Still NOT committed —
  commit pause holds.

- 2026-08-06 — **Revised 4.1.2 card approved; content issues
  #24–25 approved and fixed**: the 4-1-4 full stop; the 4-1-2
  treatment applied verbatim to the AQA twin 2-6-2-trade
  (image swap + caption + absolute-advantage paragraph +
  midpoint outputs + all four opportunity-cost bullets — its
  markup was byte-identical to the old 4-1-2, so the approved
  edits dropped straight in) and the macro gallery's image
  swapped to the SVG. Issue #26 logged (open, medium): the
  gallery blurb still says trade helps "even if one country
  has an absolute advantage in both goods", a case the figure
  no longer illustrates. All verifiers green; markup integrity
  = exactly the five approved image swaps; text integrity =
  the approved set + 4-1-4 + 2-6-2-trade. Matrix: 141 ✅ ·
  0 🟡 · 25 ❌. Batch 2 (4.1.6–4.1.9) opens. Still NOT
  committed — commit pause holds.

- 2026-08-06 — **Theme 4 batch 2 authored and built, awaiting
  review**: 21 cards covering 4.1.6–4.1.9 (protectionism's seven
  reasons, the four methods with the tariff verbatim chip, the
  tariff diagram and its evaluation; the BoP verbatim chip with
  all three accounts, an original four-component current-account
  calculation landing at −£25bn, deficit causes + financing, the
  three policy routes as an evaluation, and global imbalances;
  the three exchange-rate systems with the floating verbatim
  chip and the appreciation/revaluation vocabulary, both
  currency-market diagrams, central-bank intervention,
  competitive devaluation (verbatim chip), the depreciation
  impacts evaluation, and the J-curve diagram carrying the
  Marshall-Lerner condition; competitiveness verbatim chip with
  both measures, the ULC formula, an original £6,000-vs-£6,500
  ULC comparison, cost/non-cost factors, and the significance
  evaluation). **Four new SVGs**, all from visual inspection of
  their ground-truth PNGs with full self-QA: tariff.svg (exact
  45° Sdomestic/Ddomestic, world-supply lines at 380/300, all
  five crossings computed, shaded areas hugging the curves —
  **palette extension to flag: green #2e8540 and purple #6929c4
  fills, because the notes prose names the areas by colour**;
  P1/P2 axis labels added though the PNG lacks them, since the
  prose references them); exchange-rate-appreciation and
  -depreciation (the two-panel PNG split per the trade-union
  precedent, following the figure's P1/P2 labels — NOT the
  caption's E1/E2/E3, see issue #28); and j-curve.svg (trough
  node exactly on the second dashed line, zero-crossing node
  exactly on the time axis). Two defect classes caught in
  self-QA: the j-curve region labels collided with the
  full-height dashed lines (lines now start below the label
  band) and the exchange-rate demand curves ended exactly ON
  the x-axis with labels straddling it (ends raised, labels
  lifted). Content issues logged, all open: #27 ("may be
  require", 4-1-7), #28 (exchange-rates caption describes
  E1/E2/E3 on one diagram; the figure is two panels labelled
  P1/P2), #29 (a "causes of a deficit" bullet that ends
  "leading to a surplus"). Notes gap: spec 4.1.8g's impact of
  exchange rates on FDI flows has no notes coverage (kept
  notes-grounded). Both 4-1-7 and 4-1-9 worked examples
  recomputed and confirmed. All verifiers green (82 SVGs/0
  flags); build idempotent; no notes pages touched. Matrix:
  141 ✅ · 4 🟡 · 21 ❌; 580 cards, 82 SVGs. Still NOT
  committed — commit pause holds.

- 2026-08-06 — **Theme 4 batch 2 approved by Eliot** (same day)
  with all three adaptations ratified: the tariff palette
  extension (green #2e8540 and purple #6929c4 area fills — the
  notes prose names areas by colour), the P1/P2 labels added to
  tariff.svg beyond its PNG, and the exchange-rates two-panel
  split following the figure's P1/P2 labels. 4.1.6–4.1.9
  flipped ✅ — **section 4.1 complete**. Content issues #26–29
  approved and fixed: the gallery blurb now ends "when
  countries specialise where their opportunity cost is lowest";
  "may require" on 4-1-7 (the Persistent-deficits chip is a
  glossary source — glossary re-extracted and rebuilt, exits
  0); the exchange-rates caption rewritten to the two-panel
  P1/P2 wording; and the growth-abroad bullet reversed to "Slow
  economic growth abroad … leading to a deficit". Batch 3
  (section 4.2) opens. Still NOT committed — commit pause
  holds.

- 2026-08-06 — **Theme 4 batch 3 authored and built, awaiting
  review**: 10 cards covering ALL of section 4.2 (absolute vs
  relative poverty with the verbatim chip and both thresholds;
  causes of changes in absolute and in relative poverty as
  separate cards; income vs wealth inequality with the verbatim
  chip; the Lorenz diagram and Gini formula cards; the
  six-factor causes card; the Kuznets diagram — spec-required
  here (4.2.2d), unlike on the AQA side; capitalism's
  significance for inequality with the verbatim chip (4.2.2e,
  Edexcel-specific — no AQA twin card); and the
  benefits-vs-costs evaluation). **Zero new SVGs — lorenz-curve
  and kuznets-curve reused**, verified against the same
  ground-truth PNGs this page displays (identical files and
  captions to AQA 1-7-1, both inspected this session). Mirrors
  the approved AQA 1.7 card set with the AQA-only
  interpret-don't-calculate note dropped from the Gini card.
  Verified against 9EC0 spec 4.2 (p46, extracted earlier).
  Content issues #30 (relative-poverty comma — the exact twin
  of fixed #21; the chip is a glossary source, so the fix needs
  the glossary pipeline) and #31 ("Education and skils")
  logged, both open. All verifiers green; build idempotent;
  the only new text-integrity entries are the four approved
  #26–29 fixes. Matrix: 145 ✅ · 2 🟡 · 19 ❌; 590 cards, 82
  SVGs. Still NOT committed — commit pause holds.

- 2026-08-06 — **Theme 4 batch 3 approved by Eliot** (same
  day); 4.2.1 and 4.2.2 flipped ✅ — **section 4.2 complete**.
  Content issue #30 approved and fixed (comma → full stop on
  the 4-2-1 Relative poverty chip, glossary re-extracted and
  rebuilt, exits 0). **#31 was NOT ruled on — still open.**
  Batch 4 (section 4.3) opens. Still NOT committed — commit
  pause holds.

- 2026-08-06 — **Theme 4 batch 4 authored and built, awaiting
  review**: 16 cards covering ALL of section 4.3 (growth vs
  development with the verbatim chip; single vs composite
  indicators; the HDI's three dimensions with the 0–1 score and
  Norway/Niger; the HDI evaluation; the seven other indicators;
  primary product dependency with volatility and Dutch disease;
  the savings gap + Harrod-Domar verbatim chip; foreign
  currency gap (verbatim chip) + capital flight; the remaining
  six economic factors; the four non-economic factors; the six
  market-orientated and six interventionist strategies as
  paired list cards; the buffer-stock diagram; the Lewis model
  (verbatim chip) with tourism and primary industries; the
  Fairtrade/aid/debt-relief evaluation; and World Bank vs IMF
  vs NGOs). **One new SVG**: buffer-stocks.svg — D plus three
  supply curves at exact 45° slopes with a teal Pmax/Pmin band,
  all three equilibria computed (S3×D at 360,300 above the
  band, S1×D at 420,360 inside it, S2×D at 480,420 below it),
  full self-QA loop. **Adaptation to flag: two single
  intervention arrows pointing toward S1** (sell stock after a
  bad harvest, buy after a good one) replace the PNG's
  ambiguous red/blue double-arrow pairs. Verified against 9EC0
  spec 4.3 (pp47–48) — every bullet of 4.3.1–4.3.3 covered.
  All verifiers green (83 SVGs/0 flags); build idempotent; the
  only new text-integrity entry is the approved #30 fix.
  Matrix: 147 ✅ · 3 🟡 · 16 ❌; 606 cards, 83 SVGs. Still NOT
  committed — commit pause holds.

- 2026-08-06 — **Theme 4 batch 4 approved by Eliot** (same
  day), including the intervention-arrows adaptation on
  buffer-stocks.svg; 4.3.1–4.3.3 flipped ✅ — **section 4.3
  complete**. Content issue #31 approved and fixed ("skils" →
  "skills" on 4-2-1, not a chip, no glossary coupling). Batch 5
  (sections 4.4 + 4.5, the theme's final batch) opens. Still
  NOT committed — commit pause holds.

- 2026-08-06 — **Theme 4 batch 5 authored and built, awaiting
  review — the theme's final batch**: 19 cards covering ALL of
  sections 4.4 and 4.5 (the five functions of financial markets
  on one card; financial market failure split across asymmetric
  information/externalities, moral hazard (verbatim
  chip)/speculation/rigging, and the four consequences; central
  bank functions with the lender-of-last-resort verbatim chip
  and the PRA-vs-FPC regulation card; the three types of public
  expenditure (current-expenditure verbatim chip), why spending
  changes, and the %-of-GDP evaluation with crowding out; the
  three tax systems (progressive verbatim chip) with the
  direct/indirect mapping, the Laffer diagram card REUSING
  laffer-curve.svg — verified against the identical PNG and
  this page's t1/t2/R1/R2 prose — and the six-variable tax
  evaluation; automatic stabilisers (verbatim chip) vs
  discretionary policy, deficit vs debt (verbatim chip) with
  cyclical vs structural, deficit/debt size factors, and the
  significance evaluation; the global policy toolkit, control
  of global companies with the transfer-pricing verbatim chip,
  and the policymakers'-problems evaluation). Verified against
  9EC0 spec 4.4–4.5 (pp49–51) — every bullet covered. Content
  issues #32 (doubled "where" in the Regressive Tax chip —
  glossary source candidate) and #33 (caption references T*
  absent from the figure) logged, both open. All verifiers
  green; build idempotent; no notes pages touched. Matrix:
  150 ✅ · 7 🟡 · 9 ❌; 625 cards, 83 SVGs. Still NOT
  committed — commit pause holds.

- 2026-08-06 — **Theme 4 batch 5 approved by Eliot** (same
  day); all seven 4.4/4.5 rows flipped ✅ — **THEME 4 COMPLETE
  (84 cards, all 21 units), and with it ALL FOUR EDEXCEL
  THEMES**. Content issues #32–33 approved and fixed: the
  doubled "where" (the Regressive Tax chip IS a glossary
  source — glossary re-extracted and rebuilt, exits 0) and the
  caption's phantom "(T*)" removed. Phase 7 — the project's
  final batch — opens. Still NOT committed — commit pause
  holds.

- 2026-08-06 — **Phase 7 authored and built, awaiting review —
  the project's FINAL batch**: 40 cards covering ALL of AQA
  macro 2.4 and 2.6. Section 2.4 (AQA-specific financial
  content): money's functions and characteristics, the money
  supply (verbatim chip) with narrow vs broad money, the three
  financial markets, debt vs equity, the bond card (verbatim
  chip) with the yield formula, and an original £4-coupon
  calculation showing the price-yield inverse (5% at £80, 2.5%
  at £160); commercial vs investment banks (verbatim chip), the
  balance sheet (Assets = Liabilities + Capital), the three
  objectives and their conflicts, and credit creation (verbatim
  chip); the central bank card (verbatim chip), the
  transmission-to-AD card, the expansionary-policy diagram
  REUSING keynesian-ad-shift-right.svg (the two-panel
  2-4-3 PNG's left panel — label sets match exactly; the
  classical contrast is carried in words, panel-split
  precedent), QE + the four transmission channels, and the
  monetary-policy evaluation; the three regulators (PRA, FPC,
  FCA), the liquidity/capital ratio formula card (verbatim
  chip), and the systemic-risk/moral-hazard trade-off
  evaluation (verbatim chip). Section 2.6 (Theme 4 twins in
  AQA's framing): globalisation (verbatim chip), its drivers,
  and a consolidated consequences evaluation; comparative
  advantage (verbatim chip) with the corrected
  comparative-advantage.svg (this page already displays the
  SVG), trade benefits/pattern, the tariff.svg diagram card,
  protectionism causes/consequences, and customs
  unions/creation/diversion/WTO; the BoP (verbatim chip), an
  original −£40bn current-account calculation, causes +
  imbalances, and the three-policy-routes evaluation; fixed vs
  floating systems (verbatim chip, AQA's own pros/cons table),
  the appreciation diagram, the J-curve + Marshall-Lerner
  diagram, and the currency-union card (AQA-specific);
  growth-vs-development (verbatim chip) with the HDI, the HDI
  evaluation, barriers, strategies + AQA's three forms of aid,
  and the buffer-stocks.svg diagram card. **Zero new SVGs —
  seven diagram cards, all library reuses**, each verified
  against the PNG (or SVG) its AQA page actually displays.
  Verified against AQA 7136 spec 4.2.4 (pp55–57) and 4.2.6
  (pp59–61); the 2-4-1 yield worked example recomputed (6.25%,
  4% both ✓). Content issues #34 (2-6-4 caption, twin of #28),
  #35 ("may be require" on 2-6-3, twin of #27) and #36 (the
  surplus bullet on 2-6-3, twin of #29) logged, all open.
  Notes gap: spec 4.2.6.2's Single European Market
  characteristics are never named on 2-6-2 (kept
  notes-grounded). All verifiers green; build idempotent; the
  only new text-integrity entry is the approved #32/#33 page.
  Matrix: 157 ✅ · 9 🟡 · 0 ❌ — **zero ❌ for the first
  time**; 665 cards, 83 SVGs. Still NOT committed — commit
  pause holds.

- 2026-08-06 — **Phase 7 approved by Eliot** (same day); the
  last nine rows flipped ✅ — **ALL 166 UNITS COMPLETE. The
  project's authoring is DONE**: six decks (edexcel-a-theme-1
  through -4, aqa-micro, aqa-macro), 665 cards, 83 SVGs, all
  approved. Content issues #34–36 approved and fixed with the
  Edexcel twins' approved wording (the 2-6-4 caption; "may
  require" on 2-6-3 with the glossary pipeline rerun; the
  slow-growth-abroad bullet on 2-6-3). Eliot will commit and
  merge manually — the working tree holds everything from
  Theme 3 batch 3 onward, all approved and verified green.

- 2026-08-07 — **Final integration tasks done at Eliot's
  request**: (1) the notes-page flashcard links rolled out to
  all 144 remaining topic pages (see item 2 below); (2) the
  **hub page reformatted into an even grid** — the deck cards
  had been a single narrow left column (`max-width: 480px`,
  stacked). `css/pages/flashcards.css` now lays each `.fc-board`
  out as a two-column grid (AQA 2-up, Edexcel 2×2, cards
  spanning the full container; single column under 736px; the
  board `h2` spans the grid with `justify-self: start` keeping
  its underline shrink-to-fit). CSS-only — the generated hub
  HTML is untouched and the build stays byte-idempotent.
  Verified by headless-Chrome renders at 1280px and 400px.

- 2026-08-07 — **Content-quality QA pass, on branch
  `flashcards-qa-fixes`** (full record: docs/QA_FIXES_PROGRESS.md).
  Four issues fixed across all six decks: merged points split onto
  their own lines, exam board references removed from visible card
  text, long inline lists bulleted at six, and six multi-focus cards
  split in two. **265 cards edited, 6 split; the deck total is now
  671.** No economics wording was changed — every clause is the
  original text, re-split — with one logged exception (a
  seven-item list on `edexcel-a-2-5-4-eval-02` trimmed to six) and
  four small joins rewritten where a split half lost its antecedent.
  A **pre-existing rendering defect was found and fixed**: card faces
  were absolutely positioned in a fixed-height box, so 556 of 665
  answers (84%) were clipped at 390px and 154 at 1280px. The faces now
  stack in one grid cell; 0 of 671 overflow at either width.
  localStorage bumped to `ea-flashcards:v2:` because the card-id set
  changed. Verified by 54/54 end-to-end functional checks, a real print
  PDF, GA4 event capture and reduced-motion emulation. **No revision
  notes or glossary data were touched.**

## Outstanding tasks for Eliot (the authoring is done)

1. **Commit and merge** (Eliot doing this manually, his call
   2026-08-06). The working tree holds every change from Theme 3
   batch 3 onward: all six deck sources and builds, 40 SVGs
   untracked in `images/diagrams/svg/`, the approved notes fixes
   (issues #9–16, #18–36 minus rejected #17), the glossary
   rebuilds they triggered, the patched
   `images/diagrams/price-discrimination.png`, and `sitemap.xml`.
   Every verifier is green and the builds are idempotent, so the
   tree can land as one commit series. Reminder: `main`
   auto-publishes on push.
2. **Notes-page flashcard links — DONE 2026-08-07** (Eliot
   approved adapting the Theme 1 wording per deck). All 166
   topic pages now carry the "Revise this topic with
   flashcards" block: the 144 non-Theme-1 pages received the
   Theme 1 block verbatim with only the deck name ("the Theme
   2/3/4 deck", "the AQA microeconomics/macroeconomics deck"),
   the deck href and the per-page `?topic=<page-slug>` swapped
   in. Inserted by a byte-safe splice (pure insertion at the
   unique closing anchor, original bytes asserted unchanged per
   file — NOT a prose rewrite); every page slug was verified to
   have matching card subtopics in its deck, so no deep link
   lands empty. verify_html 186/0, verify_links 5,410 refs/0
   broken, markup integrity: 144 additions, no new losses.
3. **Deploy-bound QA** (needs a real browser/deploy): the real
   print-dialog check closing the 2026-08-04 print fix loop,
   GA4 DebugView on the five custom events, a
   keyboard/screen-reader spot check, and DevTools device-mode
   mobile.
4. **Two orphaned PNGs, deletion is Eliot's call**:
   `images/diagrams/game-theory.png` and
   `images/diagrams/comparative-advantage.png` are unreferenced
   and carry superseded/incorrect content — never use either as
   ground truth (the SVGs are authoritative). Delete or keep.
5. **Candidate notes additions** (spec-required content the
   notes never cover; cards stayed notes-grounded or, where
   noted, spec-sourced — all logged in Open questions below):
   national happiness (2.1.1); the Bank of England MPC and the
   Great Depression/2008 responses (Edexcel 2.6.2); maximum
   wages, public-sector wage setting and current labour-market
   issues (Edexcel 3.5.3); advantages of wage discrimination
   (AQA 1.6.7); the L-shaped LRAC (AQA 4.1.4.5); saving
   determinants (AQA 2.2.3); UK income/wealth distribution data
   and inequality as cause/consequence of market failure (AQA
   1.7.1); cooperation vs collusion (AQA 4.1.5.5); the impact
   of exchange rates on FDI flows (Edexcel 4.1.8g); and the
   Single European Market's characteristics (AQA 2.6.2).
6. **Deferred by design** (revisit when wanted): typed-answer
   mode (`acceptableAnswers` stays empty), the premium delivery
   layer (freemium; premium content cannot live in this public
   repo), and whether notes pages swap their remaining PNGs for
   the SVG library.
2. **Theme 4 batch 2: 4.1.6–4.1.9** (restrictions on free trade,
   balance of payments, exchange rates, international
   competitiveness). Figures displayed: tariff.png (4.1.6),
   exchange-rates.png + j-curve.png (4.1.8) — three new SVG
   candidates; 9EC0 spec 4.1.6–4.1.9 already extracted (p44–45
   area, re-extract p45–46 for 4.1.7 onward detail). Then 4.2
   poverty/inequality (mirrors of AQA 1.7 content), 4.3
   development, 4.4 financial sector, 4.5 role of the state.
   After Theme 4: AQA macro remainder 2.4 + 2.6 (phase 7, 9
   units) finishes the project.
3. Pending Eliot whenever he wants: lifting the commit pause
   (everything from Theme 3 batch 3 onward sits approved and
   uncommitted in the working tree — the tree is verified green
   — and batch 3 joins the queue once approved, so a single
   commit series can land it); and approved wording for
   notes-page flashcard links on Theme 2/3 and AQA pages (see
   Open questions).
4. **Reusable firm-diagram base** (reference — used by profit-max/revenue-max/
   sales-max and short-run-costs; reuse for 3.3.4's shaded diagrams
   and every 3.4 market-structure equilibrium): axes titles "Cost,
   revenue"/"Quantity" ("Costs" for pure cost diagrams; wide y-titles
   go on ONE line at y=40, above the axis top). Curves: D=AR
   (160,130)→(620,475) slope 0.75; MR (160,130)→(420,520) slope 1.5
   (twice AR, same intercept, ending ON the axis where MR = 0); MC
   path `M 260,485 Q 320,505 380,485 Q 425,470 470,405 Q 488,379
   505,300 Q 513,265 530,150`; AC path `M 300,330 Q 380,405 470,405 Q
   560,405 620,330` (min at 470,405, on MC exactly); AVC path (in
   short-run-costs.svg) has its min at (425,457.5), on MC exactly.
   Known crossings: MC×MR = (393.1,479.6); AC×AR = (518.6,399); AR at
   x is 0.75x+10. Objective/equilibrium markers: circle r=7 #d52349.
   Shaded areas for profit/loss rectangles: the guide corners P and C
   at the chosen Q are exact — use lowercase relative path commands
   for any shaded shape with curved edges so the checker skips its
   control points (trade-cycle precedent); plain rectangles can use
   `<rect fill-opacity>`, whose corners the checker verifies.
5. Present each ~20-card batch for Eliot's review; matrix rows stay
   🟡 review until he approves.

Session know-how a fresh chat needs:

- `verify_html.py`/`verify_links.py` default to `revision-notes/` only —
  run them as `python3 scripts/verify_html.py flashcards revision-notes`
  to cover the flashcard pages (183 pages currently).
- Spec text comes out of `specificiations/*.pdf` with a small Swift +
  PDFKit script (macOS has no pdftotext; the house rule is Swift+PDFKit
  for PDF work). AQA 7136 A-level content starts ~p32 (4.1.x) and ~p45
  (4.1.8); Edexcel 9EC0 Theme 2 starts p26.
- The builder auto-discovers any `flashcards-data/<board>/<theme>.json`;
  hub cards are automatic, sitemap entries are manual.
- Verbatim cards: `source.verbatim` must appear in the notes page after
  tag-stripping (tags become spaces) and whitespace-normalisation — copy
  the exact punctuation, including curly quotes where the page has them.

## Open questions

- **Notes-page links wording** for Theme 2 pages and AQA pages: the
  approved block says "Theme 1 deck", so each new deck needs Eliot to
  approve a wording variant before any notes page is edited (standing
  rule 1). Ask when a deck's coverage justifies it.
- The 2.1.1 national-happiness card is spec-sourced; the notes never
  cover that bullet — a candidate notes addition for Eliot someday.
- Likewise the 2.6.2 MPC card (edexcel-a-2-6-2-def-04): spec 2.6.2g
  requires the role of the Bank of England's Monetary Policy
  Committee, but the 2-6-2 notes page never mentions it. Card is
  spec-sourced; a notes addition is the eventual fix. Spec 2.6.2h
  (Great Depression / 2008 policy responses) is likewise uncovered by
  the notes; only QE's 2008 context made it into a card.
- Notes gap on 1.6.7 (candidate notes addition for Eliot someday):
  spec 4.1.6.7 expects students to "assess the advantages and
  disadvantages of wage discrimination for workers, employers and the
  economy as a whole" — the notes cover only the (negative) impacts,
  so no card covers the advantages side (kept notes-grounded).
- AQA 1.6.2 board difference — RESOLVED by Eliot 2026-08-06 with the
  batch-3 approval: the backward-bending individual supply curve
  stays OUT of the AQA cards (spec 4.1.6.2 excludes it) and the
  1-6-2 notes page stays as written (it may keep teaching the bend).
- Notes gaps on 3.5.3 (candidate notes additions for Eliot someday):
  spec 3.5.3c requires **maximum wages** and **public sector wage
  setting**, and 3.5.3b **current labour market issues** — none has
  a section on the wage-determination page, so no cards cover them
  (kept notes-grounded rather than spec-sourced this time).
- Browser/deploy-bound QA still open: real print-dialog check, GA4
  DebugView after deploy, keyboard/screen-reader spot check, DevTools
  device-mode mobile.
- Deferred by design: typed-answer mode (`acceptableAnswers` stays empty),
  premium delivery layer (out of scope until freemium), whether notes pages
  later swap their PNGs for the SVG library.

## 2026-08-14 — Wave 5.1 repaired 21 live diagrams; one new SVG awaits a card

Eliot verified all 83 SVG/PNG pairs (audit Wave 5.1, D46). **21 SVGs carried a
defect and every one was already live in the public deck payloads** — none
premium-gated, 41 cards, all 6 decks. All 21 are now repaired on `main`; the
card records themselves are untouched, because only the SVG files changed and
every `viewBox` stayed 800×600.

Worth knowing for future card work:

- **The MC curve changed shape on 13 decks' diagrams at once.** That path is
  shared byte-for-byte across 13 SVGs and now carries a hockey-stick blade. Any
  new cost diagram should match it.
- **Four SVGs gained a second panel** —
  `perfect-competition-short-run-{supernormal-profit,loss}` and
  `short-run-shutdown-condition` (plus `price-discrimination`, handled
  differently). Their alt text in the deck JSON still describes the single-panel
  version and **should be revisited when those cards are next edited**.
- **`lras-shift.svg` drawing only the classical panel is now ratified** — the
  decision this file recorded as "pending Eliot" on 2026-08-05 and never closed.

**OPEN, deliberately: `images/diagrams/svg/price-discrimination-combined-market.svg`
has no card.** It is the counterfactual to third-degree price discrimination —
one demand curve, one price, a smaller profit rectangle than the two sub-markets
added together. Eliot, 2026-08-14: *"Leave the combined-market flash card for
now, but keep the diagram stored so I can implement this into flashcards and
notes in my own time."* Its single price of 272.5 sits deliberately between the
265 and 280 of `price-discrimination.svg`'s two sub-markets, so the two diagrams
are meant to be read as a pair.
