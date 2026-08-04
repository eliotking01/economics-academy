# Flashcards — progress and handoff

The live state of the flashcards feature. A fresh session resumes from this
file. Full plan context: CLAUDE.md ("Flashcards" section) and the approved
Phase 1 plan summarised under Decisions below.

_Last updated: 2026-08-04._

## Current state

On branch `flashcards-feature`. Style guide LOCKED. Batches 1–4 approved
(2026-08-04); caption fixes shipped. Edexcel Theme 1 deck: 95 cards / 22
subtopics. **AQA micro starter deck (13 cards, 6 topics — the concepts AQA
names that Edexcel does not, plus AQA's verbatim definitions) awaits
Eliot's review**, as does the proposed notes-page links change (markup in
the chat; standing rule 1). Integration is live on the branch: nav
dropdown entry, inject-templates pageMap (flashcards light up Revision
Notes), notes-hub button, sitemap section — verify_html/links pass over
182 pages including all three flashcard pages.

QA still open (mostly needs a real browser): print preview of "Print this
deck" (the headless print-to-pdf check was inconclusive — beforeprint may
not fire there; the button path is code-verified), GA4 DebugView once
deployed, keyboard/screen-reader spot check, DevTools device-mode mobile.
Automated checks all green and continuously re-run: geometry (17 SVGs),
HTML, links, glossary, Liquid, build idempotency.

Useful QA technique: to screenshot player states, copy the built deck page
into `_working/`, append a script that clicks `.fc-step`/`.fc-card`, serve
the repo root with `python3 -m http.server`, and shoot it with headless
Chrome (`--virtual-time-budget=6000`). At mobile widths headless Chrome
shows the same right-edge overflow on existing quiz pages as on flashcards
pages — site baseline, not a flashcards regression; check real devices via
DevTools device mode in the QA pass.

## Decisions made (with reasons)

- **Pilot = full Edexcel Theme 1 (~110–115 cards) + ~12–15 AQA variant cards.**
  Theme 1 is foundational micro with the richest diagram ground truth, and
  nearly every topic has an AQA twin, so the board-variant machinery gets
  exercised in the pilot. (Eliot approved, 2026-08-04.)
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
  self-QA (clipped `D=MPB=MSB` label). Style guide gained two rulings from
  the loop: compact-equals curve identity labels, and the known mobile-render
  scrollbar artifact.
- 2026-08-04 — **Eliot's review caught what visual self-QA missed**: in the
  tax and externality diagrams the demand curve ran at slope 0.86 while every
  guide position assumed slope 1, so intersection markers and the welfare
  triangle sat ~12px off the true crossings. Fixed (all straight curves now
  exact 45°). Countermeasures now locked into the style guide:
  `scripts/verify_diagram_geometry.py` (stdlib; every diagram declares its
  intended intersections in a `<!-- geometry -->` comment and the checker
  proves each one lies on the curves — regression-tested against the buggy
  version, which it flags), plus zoomed-viewBox close-up renders of every
  junction in the visual pass.

## Next steps

1. Eliot reviews batch 2 (cards `edexcel-a-1-1-4-diagram-01` through
   `edexcel-a-1-2-8-diagram-01` in `flashcards-data/edexcel-a/theme-1.json`)
   and the four new diagrams (ppf-basic, supply-curve-shift,
   market-equilibrium, consumer-producer-surplus-equilibrium). Batch 1 facts
   (SDIL, Smith/Hayek/Marx) were approved with batch 1.
2. Batch 3: 1.2.10, 1.3.x, 1.4.x (~30 cards; diagrams: min price, max price,
   subsidy incidence, indirect-tax government revenue, elastic/inelastic
   incidence variant). Suspected notes errors go to docs/CONTENT_ISSUES.md.
3. AQA variant cards (the boards' genuine differences; use the glossary's 42
   variant-definition terms to find them mechanically).
4. Integration: nav + inject-templates.js pageMap, revision-notes hub card,
   sitemap.xml, notes-page links (separate commit, needs explicit approval —
   standing rule 1).
5. QA pass (real-device/DevTools mobile, JSON validity, SEO tags,
   performance, keyboard/screen reader, print incl. SVGs, GA4 DebugView,
   verify scripts, build idempotency run-twice-diff-empty).

## Open questions

- None blocking. Deferred by design: typed-answer mode (`acceptableAnswers`
  stays empty), premium delivery layer (out of scope until freemium),
  whether notes pages later swap their PNGs for the SVG library.
