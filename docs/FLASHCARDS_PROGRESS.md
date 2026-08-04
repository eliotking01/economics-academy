# Flashcards — progress and handoff

The live state of the flashcards feature. A fresh session resumes from this
file. Full plan context: CLAUDE.md ("Flashcards" section) and the approved
Phase 1 plan summarised under Decisions below.

_Last updated: 2026-08-04._

## Current state

On branch `flashcards-feature`. Style guide LOCKED (proof diagrams approved
2026-08-04, after Eliot caught a guide-alignment defect that visual self-QA
missed — see the geometry-checker entry below). Builder, player, hub and
deck page all work end-to-end; content **batch 1 (22 cards, vertical slice
across all seven card types) is awaiting Eliot's review**. Player screenshots
in `_working/flashcards/player-qa/`. Not yet done: batches 2+, remaining ~13
diagrams, AQA variants, nav/sitemap integration, final QA pass.

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

1. Eliot reviews content batch 1 (`flashcards-data/edexcel-a/theme-1.json`,
   22 cards). Facts flagged for his spot-check: Soft Drinks Industry Levy
   rates and the "sugar fell by over a third" claim; the Smith/Hayek/Marx
   attributions on 1.1.5–1.1.6 cards.
2. Batches 2+: remaining Theme 1 subtopics (~90 more cards), authored
   subtopic-by-subtopic; suspected notes errors go to docs/CONTENT_ISSUES.md,
   never fixed directly.
3. Remaining ~13 diagrams through the locked QA loop; AQA variant cards.
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
