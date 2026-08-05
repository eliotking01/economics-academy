# Flashcards — progress and handoff

The live state of the flashcards feature. A fresh session resumes from this
file. Full plan context: CLAUDE.md ("Flashcards" section).

_Last updated: 2026-08-05._

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

Tally (2026-08-05): **22 ✅ · 26 🟡 · 118 ❌** of 166 units.
Cards shipped: 184 (95 Edexcel Theme 1 + 89 AQA micro). SVG diagrams
shipped: 20 (all geometry-verified; twelve are shared with the AQA deck;
total-utility, underproduction and overconsumption are AQA-only — the
last two complete the four externality quadrants).

Build order approved by Eliot 2026-08-05: **Option A, paired mirrors**
(AQA T1-mirrors → Edexcel T2 → AQA macro T2-mirrors → Edexcel T3 → AQA
1.4–1.6 → Edexcel T4 → AQA remainder), single deck per AQA side.
**Phase 1 is fully authored** across three batches, all **awaiting
Eliot's review** (units stay 🟡 until he approves): batch 1 (24 cards —
1.1, 1.2.1–1.2.2), batch 2 (24 — 1.2 top-ups + section 1.3), batch 3
(28 — 1.5.11 + section 1.8 complete, with two new externality SVGs).
Known gap, deliberate: `subsidy-gov-expenditure.png` (AQA 1.8.9 Figure 2)
has no SVG yet — the subsidy card ships without a diagram until it is
drawn. Three caption errors on the AQA 1.8.9 page are logged in
docs/CONTENT_ISSUES.md (issues 3–5, the max/min/subsidy captions —
same class as the fixed Edexcel 1.4.1 pair); cards use corrected
descriptions.

Phase 2 next (needs no further approval on order): Edexcel Theme 2,
~100–110 cards in ~4 batches, ~12–15 new diagrams (circular flow, AD/AS,
classical vs Keynesian LRAS, output gaps, trade cycle, multiplier).

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

### Edexcel A (9EC0) — Theme 2 ❌ (no deck; 24 units)

| Unit | Status |
| --- | --- |
| 2.1.1 Economic growth | ❌ |
| 2.1.2 Inflation | ❌ |
| 2.1.3 Employment & unemployment | ❌ |
| 2.1.4 Balance of payments | ❌ |
| 2.2.1 Aggregate demand | ❌ |
| 2.2.2 Consumption | ❌ |
| 2.2.3 Investment | ❌ |
| 2.2.4 Government expenditure | ❌ |
| 2.2.5 Net trade | ❌ |
| 2.3.1 Aggregate supply | ❌ |
| 2.3.2 Short-run aggregate supply | ❌ |
| 2.3.3 Long-run aggregate supply | ❌ |
| 2.4.1 National income | ❌ |
| 2.4.2 Injections & withdrawals | ❌ |
| 2.4.3 Equilibrium levels of real national output | ❌ |
| 2.4.4 The multiplier | ❌ |
| 2.5.1 Causes of growth | ❌ |
| 2.5.2 Output gaps | ❌ |
| 2.5.3 Trade cycle | ❌ |
| 2.5.4 The impact of economic growth | ❌ |
| 2.6.1 Possible macroeconomic objectives | ❌ |
| 2.6.2 Demand-side policies | ❌ |
| 2.6.3 Supply-side policies | ❌ |
| 2.6.4 Conflicts between objectives and policies | ❌ |

### Edexcel A (9EC0) — Theme 3 ❌ (no deck; 20 units)

| Unit | Status |
| --- | --- |
| 3.1.1 Sizes & types of firms | ❌ |
| 3.1.2 Business growth | ❌ |
| 3.1.3 Demergers | ❌ |
| 3.2.1 Business objectives | ❌ |
| 3.3.1 Revenue | ❌ |
| 3.3.2 Costs | ❌ |
| 3.3.3 Economies & diseconomies of scale | ❌ |
| 3.3.4 Normal profits, supernormal profits & losses | ❌ |
| 3.4.1 Efficiency | ❌ |
| 3.4.2 Perfect competition | ❌ |
| 3.4.3 Monopolistic competition | ❌ |
| 3.4.4 Oligopoly | ❌ |
| 3.4.5 Monopoly | ❌ |
| 3.4.6 Monopsony | ❌ |
| 3.4.7 Contestability | ❌ |
| 3.5.1 Demand for labour | ❌ |
| 3.5.2 Supply of labour | ❌ |
| 3.5.3 Wage determination | ❌ |
| 3.6.1 Government intervention | ❌ |
| 3.6.2 The impact of government intervention | ❌ |

### Edexcel A (9EC0) — Theme 4 ❌ (no deck; 21 units)

| Unit | Status |
| --- | --- |
| 4.1.1 Globalisation | ❌ |
| 4.1.2 Specialisation & trade | ❌ |
| 4.1.3 Pattern of trade | ❌ |
| 4.1.4 Terms of trade | ❌ |
| 4.1.5 Trading blocs & the WTO | ❌ |
| 4.1.6 Restrictions on free trade | ❌ |
| 4.1.7 Balance of payments | ❌ |
| 4.1.8 Exchange rates | ❌ |
| 4.1.9 International competitiveness | ❌ |
| 4.2.1 Absolute & relative poverty | ❌ |
| 4.2.2 Inequality | ❌ |
| 4.3.1 Measures of development | ❌ |
| 4.3.2 Factors influencing growth & development | ❌ |
| 4.3.3 Strategies influencing growth & development | ❌ |
| 4.4.1 Role of financial markets | ❌ |
| 4.4.2 Market failure in the financial sector | ❌ |
| 4.4.3 Role of central banks | ❌ |
| 4.5.1 Public expenditure | ❌ |
| 4.5.2 Taxation | ❌ |
| 4.5.3 Public sector finances | ❌ |
| 4.5.4 Macroeconomic policies in a global context | ❌ |

### AQA (7136) — micro, site codes 1.x.y ≙ spec 4.1.x (deck `aqa-micro`, 13 cards so far; 54 units)

The 13-card starter deck (approved 2026-08-04) deliberately carried only
board-difference cards — AQA-named concepts Edexcel lacks, plus AQA's
verbatim definitions — so even its six units are 🟡, not at density.

| Unit | Status | Cards by type |
| --- | --- | --- |
| 1.1.1 Economic methodology | 🟡 review | 5 definition |
| 1.1.2 Nature & purpose of economic activity | 🟡 review | 2 definition |
| 1.1.3 Economic resources | 🟡 review | 3 definition |
| 1.1.4 Scarcity, choice & the allocation of resources | 🟡 review | 2 definition, 1 chain |
| 1.1.5 Production possibility diagrams | 🟡 review | 1 definition, 2 diagram, 1 chain |
| 1.2.1 Consumer behaviour | 🟡 review | 4 definition, 1 diagram |
| 1.2.2 Imperfect information | 🟡 review | 1 definition, 1 chain |
| 1.2.3 Aspects of behavioural economic theory | 🟡 review | 6 definition |
| 1.2.4 Behavioural economics & economic policy | 🟡 review | 3 definition, 1 application |
| 1.3.1 Determinants of demand | 🟡 review | 1 definition, 1 diagram |
| 1.3.2 PED, YED, XED | 🟡 review | 1 definition, 3 formula, 1 calculation, 1 chain |
| 1.3.3 Determinants of supply | 🟡 review | 1 definition, 1 diagram |
| 1.3.4 Price elasticity of supply | 🟡 review | 1 definition, 1 formula, 1 calculation |
| 1.3.5 Determination of equilibrium market prices | 🟡 review | 1 definition, 2 diagram, 1 chain |
| 1.3.6 Interrelationship between markets | 🟡 review | 3 definition |
| 1.4.1 Production & productivity | ❌ | |
| 1.4.2 Specialisation, division of labour & exchange | ❌ | |
| 1.4.3 Law of diminishing returns & returns to scale | ❌ | |
| 1.4.4 Costs of production | ❌ | |
| 1.4.5 Economies & diseconomies of scale | ❌ | |
| 1.4.6 Marginal, average & total revenue | ❌ | |
| 1.4.7 Profit | ❌ | |
| 1.4.8 Technological change | ❌ | |
| 1.5.1 Market structures | ❌ | |
| 1.5.2 The objectives of firms | ❌ | |
| 1.5.3 Perfect competition | ❌ | |
| 1.5.4 Monopolistic competition | ❌ | |
| 1.5.5 Oligopoly | ❌ | |
| 1.5.6 Monopoly & monopoly power | ❌ | |
| 1.5.7 Price discrimination | ❌ | |
| 1.5.8 Dynamics of competition | ❌ | |
| 1.5.9 Contestable & non-contestable markets | ❌ | |
| 1.5.10 Market structure, efficiency & resource allocation | ❌ | |
| 1.5.11 Consumer & producer surplus | 🟡 review | 1 definition, 1 diagram, 1 chain |
| 1.6.1 Demand for labour, marginal productivity theory | ❌ | |
| 1.6.2 Influences upon the supply of labour | ❌ | |
| 1.6.3 Wage determination: perfectly competitive labour markets | ❌ | |
| 1.6.4 Wage determination: imperfectly competitive labour markets | ❌ | |
| 1.6.5 Trade unions, wages & employment | ❌ | |
| 1.6.6 The national minimum wage | ❌ | |
| 1.6.7 Discrimination in the labour market | ❌ | |
| 1.7.1 Distribution of income & wealth | ❌ | |
| 1.7.2 The problem of poverty | ❌ | |
| 1.7.3 Government policies: poverty & income distribution | ❌ | |
| 1.8.1 How markets & prices allocate resources | 🟡 review | 2 definition, 1 evaluation |
| 1.8.2 The meaning of market failure | 🟡 review | 3 definition |
| 1.8.3 Public, private & quasi-public goods | 🟡 review | 3 definition |
| 1.8.4 Positive & negative externalities | 🟡 review | 2 definition, 4 diagram |
| 1.8.5 Merit & demerit goods | 🟡 review | 3 definition |
| 1.8.6 Market imperfections | 🟡 review | 2 definition |
| 1.8.7 Competition policy | 🟡 review | 1 definition |
| 1.8.8 Public ownership, privatisation, regulation & deregulation | 🟡 review | 3 definition |
| 1.8.9 Government intervention in markets | 🟡 review | 3 definition, 3 diagram |
| 1.8.10 Government failure | 🟡 review | 1 definition, 1 chain |

### AQA (7136) — macro, site codes 2.x.y ≙ spec 4.2.x ❌ (no deck; 25 units)

| Unit | Status |
| --- | --- |
| 2.1.1 Objectives of government economic policy | ❌ |
| 2.1.2 Macroeconomic indicators | ❌ |
| 2.1.3 Uses of index numbers | ❌ |
| 2.1.4 Uses of national income data | ❌ |
| 2.2.1 Circular flow of income | ❌ |
| 2.2.2 AD/AS analysis | ❌ |
| 2.2.3 Determinants of aggregate demand | ❌ |
| 2.2.4 Aggregate demand & the level of economic activity | ❌ |
| 2.2.5 Determinants of short-run aggregate supply | ❌ |
| 2.2.6 Determinants of long-run aggregate supply | ❌ |
| 2.3.1 Economic growth & the economic cycle | ❌ |
| 2.3.2 Employment & unemployment | ❌ |
| 2.3.3 Inflation & deflation | ❌ |
| 2.3.4 Conflicts between macroeconomic policy objectives | ❌ |
| 2.4.1 Structure of financial markets & financial assets | ❌ |
| 2.4.2 Commercial banks & investment banks | ❌ |
| 2.4.3 Central banks & monetary policy | ❌ |
| 2.4.4 Regulation of the financial system | ❌ |
| 2.5.1 Fiscal policy | ❌ |
| 2.5.2 Supply-side policies | ❌ |
| 2.6.1 Globalisation | ❌ |
| 2.6.2 Trade | ❌ |
| 2.6.3 The balance of payments | ❌ |
| 2.6.4 Exchange rate systems | ❌ |
| 2.6.5 Economic growth & development | ❌ |

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
- **localStorage follows quiz.js verbatim**: `ea-flashcards:v1:` prefix,
  availability probe, key index for global reset.
- **GA4 events** (site's first custom events): `deck_start`, `card_flip`,
  `card_rated`, `deck_complete`, `deck_print`, all with `board`/`theme`/
  `deck_id`, wrapped so they no-op silently without gtag.

## Working state and QA

On branch `flashcards-feature`, clean tree. Style guide LOCKED
(docs/DIAGRAM_STYLE.md). Automated checks all green and continuously
re-run: geometry (17 SVGs), HTML, links, glossary, Liquid, text/markup
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

## Next steps

1. **Eliot chooses the build order** for the 138 ❌ / 6 🟡 remaining units
   (roadmap options proposed in chat 2026-08-05; recommendation: paired
   mirrors — an Edexcel theme, then immediately its AQA mirror sections).
   Also pending his call: AQA deck granularity (recommend keeping the single
   `aqa-micro` deck and one future `aqa-macro` deck, matching the shipped
   URLs) and AQA notes-page links wording.
2. Build per the approved order under the standing rules: every card
   verified against the official spec, board-specific cards and diagram
   variants where the boards differ, diagrams per docs/DIAGRAM_STYLE.md with
   geometry declarations and SVG-to-PNG self-QA, content presented in
   ~20-card batches for review, suspected notes errors to
   docs/CONTENT_ISSUES.md, sitemap/SEO updated as decks ship, small frequent
   commits, coverage matrix updated every session.
3. Browser/deploy-bound QA (see Working state) once Eliot is ready.

## Open questions

- Build order, AQA deck granularity, AQA links wording — all awaiting
  Eliot (see Next steps 1).
- Deferred by design: typed-answer mode (`acceptableAnswers` stays empty),
  premium delivery layer (out of scope until freemium), whether notes pages
  later swap their PNGs for the SVG library.
