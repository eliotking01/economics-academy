# Flashcards — progress and handoff

The live state of the flashcards feature. A fresh session resumes from this
file. Full plan context: CLAUDE.md ("Flashcards" section) and the approved
Phase 1 plan summarised under Decisions below.

_Last updated: 2026-08-04._

## Current state

Scaffolding done on branch `flashcards-feature`. The three style-guide proof
diagrams are built, self-QA'd and **awaiting Eliot's visual approval** — that
approval locks docs/DIAGRAM_STYLE.md. SVGs in `images/diagrams/svg/`, their
headless-Chrome QA renders in `_working/flashcards/diagram-qa/`. No builder,
player or card content exists yet.

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

## Next steps

1. Three style-guide proof diagrams (demand shift; indirect tax incidence;
   negative production externality, ground truth `overproduction.png`) through
   the full self-QA loop → present to Eliot → lock docs/DIAGRAM_STYLE.md.
2. `scripts/build_flashcards.py`: schema validation, KaTeX pre-render (reuse
   build_glossary.py's invocation), Prettier idempotency, premium filtering,
   notes-verbatim verification.
3. Player: `js/components/flashcards.js`, `css/pages/flashcards.css`
   (scoped under `.flashcards-page`), hub + deck landing templates.
4. Theme 1 content subtopic-by-subtopic; Eliot reviews in ~20-card batches.
   Suspected notes errors go to docs/CONTENT_ISSUES.md, never fixed directly.
5. Remaining ~13 diagrams; AQA variant cards.
6. Integration: nav + inject-templates.js pageMap, revision-notes hub card,
   sitemap.xml, notes-page links (separate commit, needs explicit approval —
   standing rule 1).
7. QA pass (mobile, JSON validity, SEO tags, performance, keyboard/screen
   reader, print incl. SVGs, GA4 DebugView, verify scripts, build idempotency
   run-twice-diff-empty).

## Open questions

- None blocking. Deferred by design: typed-answer mode (`acceptableAnswers`
  stays empty), premium delivery layer (out of scope until freemium),
  whether notes pages later swap their PNGs for the SVG library.
