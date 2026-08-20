# Glossary & Formulae — PROGRESS

Live state of the Glossary & Formulae build. **Read this first** after any
`/clear`. Updated immediately after every completed step, approval or decision —
never batched.

- **Branch:** `fix/glossary-polish` (off `main` at `11e763a`). The build itself
  merged to `main` on 2026-08-04 and is live.
- **Current phase:** Phase 7 — post-launch fixes
- **Current step:** all five fixes applied; manual QA is Eliot's
- **Last updated:** 2026-08-07

---

## Where the files live

`_working/glossary/` is **not published**. There is no `.nojekyll` and no
`_config.yml`, so GitHub Pages runs the default Jekyll build, and Jekyll excludes
any directory whose name begins with `_`. Verified against the live site on
2026-08-03: `/PROJECT-LOG.html` serves markdown wrapped in the stock Jekyll
theme (proving Jekyll runs), and a bogus URL correctly returns 404 (proving a
200 means a real file).

**Fragile in one specific way: adding `.nojekyll` to this repo at any point in
the future would immediately expose `_working/` on the live site.** Recorded in
`CLAUDE.md` for that reason.

| File | Purpose |
| --- | --- |
| `_working/glossary/PROGRESS.md` | This file |
| `_working/glossary/inventory.md` | Every extracted term, appended incrementally |
| `_archive/working/glossary/gap-report.md` | For Eliot's manual review |
| `_archive/working/glossary/spec-checklist.md` | Per-board required terms, from the spec PDFs |

---

## Checklist

### Phase 0 — Discover — COMPLETE

- [x] Map repo, notes organisation, naming, specs, sitemap, robots, build tooling
- [x] Map shared assets: header/footer/nav, meta conventions, breadcrumbs, page shell
- [x] Confirm `_working/` is not published (verified against the live site)
- [x] Measure the actual definition and formula content (see Numbers below)
- [x] Report findings

### Phase 1 — Setup — COMPLETE

- [x] 1.1 Branch `feature/glossary`, create `_working/glossary/`, write `PROGRESS.md`
- [x] 1.2 `CLAUDE.md` additions; two bugs logged as G1/G2 in `docs/REVIEW-NOTES.md`; `_archive/ROADMAP.md` updated

### Phase 2 — Extraction & gap analysis — COMPLETE

- [x] 2.1 `scripts/extract_glossary.py` — 255 terms, 49 formulae, 0 problems
- [x] 2.2 `inventory.md` written (rewritten whole each run — deterministic, so safer than appending)
- [x] 2.3 9 table candidates listed with every row in `review-decisions.md` §A
- [x] 2.4 Both specs scanned as a checklist → `spec-checklist.md`. No spec wording in the repo
- [x] 2.5 `gap-report.md`
- [x] 2.6 Reviewed and answered. A, B, E, G decided; C, D, F left to defaults

### Phase 3 — Build — COMPLETE

- [x] 3.1 `scripts/build_glossary.py`
- [x] 3.2 KaTeX vendored: `css/vendor/katex/` for the browser, `scripts/vendor/katex.min.js` for the build
- [x] 3.3 The three pages
- [x] 3.4 `css/pages/glossary.css` incl. the print block
- [x] 3.5 `js/components/glossary-filter.js`
- [x] 3.6 `scripts/verify_glossary.py` — 5 checks, all passing

### Phase 4 — SEO & integration — COMPLETE

- [x] 4.1 JSON-LD: `DefinedTermSet` / `DefinedTerm` + `BreadcrumbList` — 427 terms, all anchors resolve
- [x] 4.2 Sitemap block between `<!-- Glossary -->` markers
- [x] 4.3 P1, P2a and P3c approved and applied. P3a/P3b deferred by choice

### Phase 5 — QA & handover — IN PROGRESS

- [x] 5.1 All verifiers pass; rebuild byte-identical; 0 text removed, 0 markup lost
- [ ] 5.2 Manual, **for Eliot**: real phone, JS disabled, keyboard, print preview, Rich Results
- [ ] 5.3 Summary + handover

### Phase 7 — post-launch fixes — COMPLETE (2026-08-07)

Five fixes, one commit each, on `fix/glossary-polish`.

- [x] 7.1 **Capitalisation.** 58 approved wordings (95 records) capitalised at
      render time. The 79 fragment records were left alone here and handled
      separately in 7.5. New `scripts/check_glossary_capitalisation.py`, new
      verifier check 6.
- [x] 7.2 **Theme tags** recoloured grey → `--gl-accent` (`#d52349`). Fixed an
      existing AA failure: white on `#7a7a7a` is 4.29:1, on `#d52349` 5.04:1.
      Print unchanged (outlined, no fill).
- [x] 7.3 **Search matches the term only**, ranked, with a flat results list
      while a query is active. Verified end-to-end in headless Chrome.
- [x] 7.4 **URL move evaluated and rejected.** Stays at
      `/revision-notes/glossary/`. Convention recorded in `CLAUDE.md`.
- [x] 7.5 **Fragment definitions rewritten at render time** (D16), notes
      untouched. 46 rules in `curation.json` → `rewrite`; new verifier check 7;
      "word for word" claims reworded on all three pages and in the meta
      descriptions, since they had stopped being true.
- [x] 7.7 **The 8 `e.g.` chips resolved** (D18). `Free trade area`,
      `Customs union`, `Common market`, `Monetary union` and `Currency union`
      gave an example where a definition was expected — the defining
      characteristics were the `<ul>` underneath, which the extractor skipped
      because the text does not end on a colon. New `curation.json` →
      `attachList` names them and the list is taken as part of the definition.
      **No wording written**, and the verbatim check covers the list. The list
      renders **before** the example (Eliot's call): the extractor sets
      `listIsDefinition` on the source, and `entry_html` orders the two on it.
      The JSON-LD description folds the list in as a sentence, since "e.g.
      USMCA" alone was useless as structured data. A duplicated `.gl-def-list`
      block in `glossary.css` was removed at the same time.
- [x] 7.6 **`Maximum Price` and `Minimum Price` given real definitions** (D17).
      Both notes pages already define them properly under
      `<strong>Effect:</strong>`, which is not a chip and so was invisible to
      the extractor. The externalities-page chips are dropped via
      `excludeSources` and the definitions added to `authored.json`, adapted
      from those pages' own Purpose/Effect wording. 44 rewrite rules remain; the
      two `not-a-definition` ones are gone.

---

## Decisions approved by Eliot

| # | Decision | Rationale |
| --- | --- | --- |
| D1 | **One page per exam board** | Set in the brief. Students revise for one board |
| D2 | URLs at **`/revision-notes/glossary/{,edexcel-a/,aqa/}`** | There is no "Extra Resources" area on the site, so nesting there would invent an empty folder level. Also means `inject-templates.js` needs no change — its existing `/^\/revision-notes(\/\|$)/` rule already highlights "Revision Notes" |
| D3 | Extraction = **`key-definition` chips + approved table columns** | Chips are fully mechanical; table rows get row-by-row sign-off so no judgement is exercised unreviewed |
| D4 | **KaTeX, pre-rendered at build time**, CSS + woff2 self-hosted | Formulae load instantly and render with JS off. Accepts a visual divergence from the MathJax-rendered notes pages |
| D5 | Spec PDFs are a **checklist only** | They are the boards' copyright; no spec wording enters the site |
| D6 | Board pages **self-canonical**, no cross-canonical | Cross-canonicalling would deindex one board and forfeit "AQA economics glossary" traffic |
| D7 | Definition text stored **per source**, not per term | Makes "verbatim from my notes" enforceable per board; the 12 known cross-board divergences render honestly instead of one board inheriting the other's wording |
| D8 | **A–Z is the primary order**, theme is a filter + per-entry metadata | Listing every term twice under two orderings would double the page and confuse the anchors. Flagged in the plan as reversible to a view toggle if Eliot prefers |
| D9 | **No downloadable PDF in v1** — print stylesheet only | Would need a headless browser or PDF library on a repo with zero build deps, and becomes a second artefact that drifts. Cmd+P covers it |
| D10 | Flashcards / self-test **out of scope for v1** | Set in the brief. To be recorded in `_archive/ROADMAP.md` |
| D11 | Capitalisation applied **at render time from `curation.json`**, never in `terms.json` | `terms.json` is generated and must stay byte-identical to the notes, or check 1 stops meaning anything. Keyed on term id + a hash of the wording, so rewording a notes chip lapses the approval instead of silently carrying it to text nobody approved |
| D12 | Fragments are **not** capitalised and **not** reworded | "Globalisation is the increasing integration" would become "Is the increasing integration". Rewording is a wording change, which is Eliot's alone. **Superseded by D16 on 2026-08-07** |
| D13 | Theme tags take **one accent for all themes**, `#d52349` | A colour per theme would imply a meaning the tag does not carry. Green lost twice: `#4caf50` is 2.78:1 with white text, and already means "correct" as the tick glyph in `main.css` |
| D14 | Search matches the **term only**, ranked, results flattened while querying | Matching definitions buried the Demand entry under every definition mentioning demand. Ranking requires the order to change, so A-Z gives way during a query and returns on clear |
| D15 | Glossary **stays at `/revision-notes/glossary/`** | GitHub Pages cannot 301. Meta-refresh or JS redirect would be the only option, both pass authority unreliably, and the stubs would live in the repo forever. URL depth is a weak signal and the pages were 3 days old — the gain did not cover the cost. Confirms D2 |
| D18 | The five trading-bloc chips take their **following list** as the definition | They give an example, not a definition — but the defining characteristics are already on the page, in the `<ul>` under the chip. `following_list()` only fired on a trailing colon, so curation names them in `attachList` instead. Same mechanism, same words, wider reach. Preferred over authoring, which would have duplicated content the notes already carry |
| D17 | `Maximum Price` / `Minimum Price` moved to **`authored.json`**, their externalities-page chips excluded | Instructed by Eliot on 2026-08-07: replace the non-definitions with the real thing. Both government-intervention pages already define them, but under `<strong>Effect:</strong>` rather than a `key-definition` chip, so the extractor cannot reach the wording. This is the path `extract_glossary.py` was already built for — exclusions are applied *before* the authored layer precisely so an authored entry can replace an excluded chip. The definitions are adapted from those pages' own Purpose/Effect wording and link to them per board |
| D16 | **Fragment definitions are rewritten at render time**, notes untouched | Instructed by Eliot on 2026-08-07, explicitly overriding D12 and the CLAUDE.md rule that a badly-reading definition is fixed in the notes. Kept as narrow as possible: a rule replaces a **leading substring only**, 39 of 46 invent no word, and the build fails if `from` stops matching so a reworded notes page cannot silently re-point a rule. This is the **second** declared departure from "the notes' own words", after `authored.json` |

---

## Open questions awaiting Eliot

Nothing blocking. Five things flagged for a decision when convenient, all
recorded in the round-two report:

1. **B6 kept but B12/B19 excluded** — B6 is `M = 1/(1 - 0.8) = 1/0.2 = 5`,
   worked arithmetic of the same kind as the two that were excluded. Probably
   a slip in a run of consecutive numbers.
2. **Percentage change now has no formula** — B15 was excluded. It is QS2 on
   both specifications and was the headline gap-report finding.
3. **CPI now has no formula** — B20, B21 and B46 were all excluded.
4. **Five more formulae dropped** that state a real relationship: Output Gap
   (B36), GNI (B25), Unit Labour Costs (B45), Capital Ratio (B22), Liquidity
   Ratio (B33).
5. **Three notes gaps found while deciding E** — Edexcel has no general
   definition of Regulation, AQA none of Subsidies, and Edexcel's merit/demerit
   good wording puts the external cost on the producer. See `e-decisions.md`.

Also worth a sentence back: what did **"not sure students will use these
labels"** refer to? Read as the section G stop-list, it agrees with removing
them. If it meant the display renames (R1-R15), say so and they change.

---

## Numbers established in Phase 0

Measured, not sampled — from the 166 topic pages.

| | |
| --- | ---: |
| `key-definition` chips total | 639 |
| …that are a clean paragraph-leading term + definition | **560** |
| Unique terms after filtering 6 non-term labels | **268** |
| Non-term chip instances dropped (`Definition:` 30, `Aim:` 14, `Why?` 8, `Result:` 4, `Reason:` 2, `Limitation:` 2) | 60 |
| Terms defined on both boards | 161 |
| …with byte-identical definition text | **149** |
| `(term, board)` pairs defined differently on 2+ pages | 40 |
| Pages with no chip at all | 12 |
| `concept-table`s with a definition-ish column | 12 candidates, ~54 rows |
| Formulae in LaTeX | ~50 across 29 pages |
| Formulae written as plain text instead | ~54 |
| Chips split across lines by Prettier (`</span\n>`) | 65 |

Per-board chip split: Edexcel 267, AQA 293.

---

## Extraction gotchas — do not rediscover these

1. Prettier splits `</span\n>` on **65** chips. The regex needs `re.DOTALL`:
   `<span class="key-definition"\s*>(.*?)</span\s*>`
2. The MathJax config block contains the literal strings `["\\[", "\\]"]`, so a
   naive LaTeX grep returns a phantom hit on all 125 MathJax pages.
   **Strip `<script>…</script>` before scanning.**
3. `&amp;` appears on 89 pages, `&lt;` on 15 — including *inside* LaTeX. Decode.
4. **79 chips sit mid-sentence** as highlights, not headings; the definition
   wraps around them. Detect by "is the chip the first content in its block?"
5. **8 chips have no definition text at all** (`Prices`, `Quality`, `Choice`,
   `Types of Indirect Tax:`, `Causes:`). Blacklist.
6. Generic `Definition:` chips (30) need the term resolved from the nearest
   preceding `<h2>` / `<h1>`.
7. **2 display formulae live in `<p><strong>`**, outside any `formula-box`
   (`4-1-4-terms-of-trade`, `4-1-9-international-competitiveness`).
8. A `formula-box` is **not** 1:1 with a formula — it may hold a label
   paragraph, a gloss paragraph, or two equations. Extract per `\[…\]`.
9. **Spec codes collide across boards.** `1.3.2` is Edexcel Externalities *and*
   AQA Elasticities of Demand. Key records on the canonical URL, never the code.
10. `1-2-10-…` sorts between `1-2-1-` and `1-2-2-` lexically. Sort naturally.
11. Board attribution comes from the `spec-alert` line, not the JSON-LD — the
    JSON-LD `isPartOf` names have ~20 inconsistent variants. 161 of 166
    `spec-alert`s match `(AQA|Edexcel) unit ([\d.]+) - <Title>`; the 5 that don't
    are AQA micro pages missing the ` - ` separator.
12. `_archive/raw-notes/edexcel/*.md` is **not** a usable source: it covers only 73 of 166
    pages, nothing for AQA, and its wording is a superseded April draft that
    differs from the live pages.

---

## House rules that apply to the generated output

- Every emitted KaTeX block needs `<!-- prettier-ignore -->` before it, or
  Prettier reflows it and the build stops being idempotent.
- Generator is stdlib-only, run as plain `python3 scripts/build_glossary.py`.
  `.venv` exists solely for the AQA PDF extractor.
- One scoped stylesheet, every rule under `.glossary-page` on `<section id="main">`.
- `.glossary-page [hidden] { display: none !important }` is required — any author
  `display` rule beats the UA's `[hidden]` rule.
- Restate the breadcrumb colour; the inherited `#7f888f` fails AA on `#main`'s
  `#f7f7f7` background.
- Seven-script tail in order, page scripts appended after with `defer`.
- Sitemap: one `<url>` per line, no internal whitespace, `<loc><lastmod><priority>`.

---

## Files created or modified so far

| Path | State |
| --- | --- |
| `_working/glossary/PROGRESS.md` | Created (this file) |
| `CLAUDE.md` | Modified — new "How publishing works" and "Glossary & formulae" sections; 3 lines added to Layout; 1 line to See also |
| `docs/REVIEW-NOTES.md` | Appended — G1 (MathJax missing on `2-1-3`), G2 (`.formula-box` unstyled) |
| `_archive/ROADMAP.md` | Modified — glossary under Now; flashcards, KaTeX migration and PDF export under Someday |
| `scripts/extract_glossary.py` | Created — the extractor and the review-file generator |
| `glossary-data/curation.json` | Created — hand-written judgement, no definition text |
| `glossary-data/terms.json` | Generated — 255 terms, 49 formulae |
| `_working/glossary/inventory.md` | Generated |
| `_working/glossary/review-decisions.md` | Generated — the decisions needed |
| `_archive/working/glossary/spec-checklist.md` | Generated — per-board spec coverage |
| `_archive/working/glossary/gap-report.md` | Written — the summary and judgement calls |
| `_archive/working/glossary/e-decisions.md` | Written — every section E judgement and its reason |
| `_archive/working/glossary/integration-proposals.md` | Written — P1-P4, awaiting sign-off |
| `scripts/test_glossary_filter.js` | Created — filter tests + markup contract |
| `scripts/build_glossary.py` | Created — generator |
| `scripts/verify_glossary.py` | Created — the anti-drift check; check 6 added 2026-08-07 |
| `scripts/check_glossary_capitalisation.py` | Created 2026-08-07 — classifies, reports, `--approve`, `--check` |
| `_working/glossary/capitalisation-report.md` | Generated 2026-08-07 — the 206 lower-case starts |
| `scripts/vendor/katex.min.js` + `README.md` | Created — build-time only, not served |
| `css/vendor/katex/katex.min.css` + `fonts/*.woff2` | Created — 20 woff2, 296KB |
| `css/pages/glossary.css` | Created — scoped under `.glossary-page` |
| `js/components/glossary-filter.js` | Created |
| `revision-notes/glossary/{,edexcel-a/,aqa/}index.html` | **Generated** |
| `sitemap.xml` | Modified — new Glossary block, 3 URLs |
| `revision-notes/aqa-a2-macro/2-1-{2,3}-*.html` | Modified — G3, three `%`→`\%`, no wording change |
| `glossary-data/authored.json` | Created — 76 authored definitions, 4 formulae (Maximum/Minimum Price added 2026-08-07) |
| `_working/glossary/authored-review.md` | Generated — the economics to check |
| `templates/header.html` | Modified — P1, one `<li>` |
| `revision-notes/index.html` | Modified — P2a, col-4→col-3 ×3 plus a fourth button |
| `revision-notes/{micro,macro}economics-diagrams.html` | Modified — P3c, one button in the existing `.notes-cta` |
| `revision-notes/macro-application/index.html` | Modified — P3c, a new minimal `.notes-cta` |

**No revision-notes topic page has been edited, and none will be.**

---

## Synonyms — worth building, not built

**The glossary data has no synonyms or alternative-names field.**
`curation.json`'s `aliases` merges duplicate *spellings* during extraction and
never reaches the page.

This matters more now search is term-only. An abbreviation only matches because
the notes happen to put it in the term itself — `Price Elasticity of Demand
(PED)` tokenises to include `ped`, so "PED", "GDP", "AD", "YED" and "XED" all
work by luck of house style rather than by design. Student shorthand that is
**not** in any term string matches nothing at all: `PPF`, `PPC`, `MRP`, `MPC`
where the term is written out, and any term whose common abbreviation the notes
never bracket.

The shape it would take: a `synonyms` array per term in `curation.json` (so
re-extraction cannot destroy it), emitted as a `data-synonyms` attribute and
concatenated into `termTokens` by `buildIndex`. Ranked below a real term match.
Roughly an hour, no new dependency.

Not built — no instruction to.

---

## Outstanding for Eliot (carried to handover)

- **`Maximum Price` and `Minimum Price` now carry real definitions** — done
  2026-08-07, see 7.6. Check the economics: they are **W70/W71** and **W74/W75**
  in `authored-review.md`.
- **Three rewrites add a word**, the only new wording in the glossary outside
  `authored.json`. Worth a read: `Composite indicators` and `Single indicators`
  gained "Indicators that", `Non-excludability` (×2) gained "Where", and
  `Information Provision` has "educate" → "Educating". All marked `adds` in
  `curation.json`, all listed in the report.
- **3 rules are inert** — `Information Provision`, `Non-excludability` and
  `Regulation` have a rule for a source that is not the one displayed on either
  board, so they change nothing a reader sees. Harmless, and correct if the
  preferred source ever changes. Check 7 reports shown vs total.
- ~~8 chips are examples, not definitions~~ **Resolved 2026-08-07, see 7.7.**
  All five trading-bloc terms had their defining characteristics in the list
  underneath the chip; the extractor now takes it. Nothing was written.
- **2 unclassified**, both `Regulation`. Same report.
- **The pages no longer claim "word for word".** The board intros, the landing
  page and the meta descriptions said each definition was taken word for word
  from the notes, which stopped being true for these 46. Reworded to "comes
  from" / "taken from". The landing page also said "Nothing here is written for
  the glossary", which was already false — `authored.json` has 76 — and that
  sentence is gone.

- **The spec PDFs are live on the public site.** `faccb6a "added specs"`
  committed `specificiations/{aqa-spec,edexcel-a-spec}.pdf`, and both return
  HTTP 200 at `economicsacademy.co.uk/specificiations/` with `robots.txt` set to
  `Allow: /`. They are AQA's and Pearson's copyright. Eliot has said he will
  remove them manually once this project is complete. `git rm --cached` plus a
  `.gitignore` entry would keep the local files (which is all the extraction
  needs) while taking them off the site.

---

## Exact next action

**Nothing.** Phase 7 is complete: all four post-launch fixes are applied and
committed on `fix/glossary-polish`, which is **not merged** — merging is what
publishes it.

Waiting on Eliot:

0. Review and merge `fix/glossary-polish`, then check the four fixes on the live
   site. The 79 fragments above are the only content decision outstanding.

1. **Check the economics** in `_working/glossary/authored-review.md` — 132
   authored wordings across 74 terms. These are the only entries on the site
   that are not the notes' own words.
2. Manual QA — real phone, JavaScript off, keyboard-only, print preview, and the
   JSON-LD through Google's Rich Results test.
3. Merge to `main`, which is what publishes it.
4. The spec PDFs are still live at `economicsacademy.co.uk/specificiations/`.

The intended direction of travel for `authored.json` is downwards: each entry
moved into its notes page as a `key-definition` chip becomes extracted, and the
build then errors until the authored copy is removed.
