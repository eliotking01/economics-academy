# Glossary & Formulae — PROGRESS

Live state of the Glossary & Formulae build. **Read this first** after any
`/clear`. Updated immediately after every completed step, approval or decision —
never batched.

- **Branch:** `feature/glossary` (off `main` at `faccb6a`)
- **Current phase:** Phase 1 — setup
- **Current step:** 2.1 — build `scripts/extract_glossary.py` (chip pass)
- **Last updated:** 2026-08-03

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
| `_working/glossary/gap-report.md` | For Eliot's manual review |
| `_working/glossary/spec-checklist.md` | Per-board required terms, from the spec PDFs |

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
- [x] 1.2 `CLAUDE.md` additions; two bugs logged as G1/G2 in `REVIEW-NOTES.md`; `ROADMAP.md` updated

### Phase 2 — Extraction & gap analysis — IN PROGRESS

- [ ] 2.1 `scripts/extract_glossary.py` — chip pass → `glossary-data/terms.json`
- [ ] 2.2 Append results to `inventory.md` incrementally
- [ ] 2.3 Table-column harvest: list all candidate rows for Eliot's approval
- [ ] 2.4 Scan both spec PDFs as a **checklist only** → `spec-checklist.md`
- [ ] 2.5 `gap-report.md`
- [ ] 2.6 **PAUSE — Eliot reviews inventory + gap report + table rows**

### Phase 3 — Build

- [ ] 3.1 `scripts/build_glossary.py`
- [ ] 3.2 Vendor KaTeX (CSS + woff2 only) into `css/vendor/katex/`
- [ ] 3.3 The three pages
- [ ] 3.4 `css/pages/glossary.css` (incl. print block)
- [ ] 3.5 `js/components/glossary-filter.js`
- [ ] 3.6 `scripts/verify_glossary.py`

### Phase 4 — SEO & integration

- [ ] 4.1 JSON-LD: `DefinedTermSet` / `DefinedTerm` + `BreadcrumbList`
- [ ] 4.2 Sitemap block
- [ ] 4.3 **PROPOSE ONLY** — nav `<li>`, "More Free Resources" button, notes→glossary links

### Phase 5 — QA & handover

- [ ] 5.1 Verify scripts, idempotence, HTML, links
- [ ] 5.2 Manual: 3 widths, JS disabled, keyboard, print preview
- [ ] 5.3 Summary + handover

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
| D10 | Flashcards / self-test **out of scope for v1** | Set in the brief. To be recorded in `ROADMAP.md` |

---

## Open questions awaiting Eliot

_None right now._ Next decision point is **2.6**, the Phase 2 review pause.

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
12. `raw-notes/edexcel/*.md` is **not** a usable source: it covers only 73 of 166
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
| `REVIEW-NOTES.md` | Appended — G1 (MathJax missing on `2-1-3`), G2 (`.formula-box` unstyled) |
| `ROADMAP.md` | Modified — glossary under Now; flashcards, KaTeX migration and PDF export under Someday |

**No revision-notes topic page has been edited, and none will be.**

---

## Outstanding for Eliot (carried to handover)

- **The spec PDFs are live on the public site.** `faccb6a "added specs"`
  committed `specificiations/{aqa-spec,edexcel-a-spec}.pdf`, and both return
  HTTP 200 at `economicsacademy.co.uk/specificiations/` with `robots.txt` set to
  `Allow: /`. They are AQA's and Pearson's copyright. Eliot has said he will
  remove them manually once this project is complete. `git rm --cached` plus a
  `.gitignore` entry would keep the local files (which is all the extraction
  needs) while taking them off the site.

---

## Exact next action

**Step 2.1.** Write `scripts/extract_glossary.py` — the chip pass. Stdlib only.
Reads the 166 topic pages, applies the twelve gotchas above, and writes
`glossary-data/terms.json` plus an incremental append to `inventory.md`.

Support `--check` (validate and write nothing). Board attribution comes from the
`spec-alert` line. Records key on the canonical URL, never the spec code.
