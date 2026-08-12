# Audit progress

**Read this plus `AUDIT-PLAN.md` and you can resume with zero prior context.**
Nothing below needs the site re-crawled — the scripts in `docs/audit/scripts/`
reproduce every figure in seconds.

Last updated: **2026-08-10**. **THE AUDIT IS COMPLETE**; implementation is
under way — jump to `# HANDOVER` at the end of this file for the current state.

---

## Where things stand

| | |
| --- | --- |
| Branch | `audit/organisation-audit`, cut from `main` at `8c8034b` |
| Phase complete | **ALL ELEVEN.** P0, P1, P5, P9, P9b, P6, P8, P3, P4, P7, P10, P11 |
| Phase next | **None — implementation.** Start at `findings/PH11-synthesis.md` §6 |
| Findings so far | 63 (`PH00-001` … `PH10-063`). 4 RESOLVED, PH00-001 and PH00-007 CLOSED, **PH01-013 RESOLVED-BY-DECISION (D28)**, 2 CORRECTED, 1 SUPERSEDED, 1 AMENDED (D29) |
| Open questions | **None.** Q1–Q26 all answered |
| **P6 proposal** | **APPROVED as put**, 2026-08-09 — `DECISIONS.md` D18. Option (f), Actions for verification only, all six normalisations. **P8 corrects the target list of normalisation 5 and 6 — see PH08-042** |
| **Implementation** | **Deferred to after P11**, by decision D20. The audit stays read-only throughout; D18's approval carries forward and needs no re-asking |
| **Dated dependency** | **Day-45 GSC re-measure, ≈2026-09-22.** PH05-019 and PH05-021 are blocked on it |
| Blockers | None. **One decision has a deadline: what becomes of `_audit/` — PH11 §5** |
| Site files modified | `.gitignore` (brief); plus 3 changes Eliot authorised explicitly — see D11, D12, **D21** |

### Verify the working state before doing anything

**SUPERSEDED 2026-08-09 by D30** — the audit moved from `_audit/` to
`docs/audit/` and is now committed. The `check-ignore` test below is inverted:
it now correctly reports nothing, and that is no longer a reason to stop. What
keeps the audit off the site is `docs/` in `_config.yml`'s `exclude`, not
`.gitignore`. Original text kept below, struck through, per the append-only
convention.

```
git branch --show-current            # audit/organisation-audit
git status --porcelain               # must be empty; both changes are committed
python3 scripts/build_sitemap.py --check   # must say "nothing written"
grep -n '^  - docs/' _config.yml     # must match: this is what withholds the audit
```

~~`git check-ignore -v _audit/PROGRESS.md` — must report `.gitignore:35`. If
`check-ignore` reports nothing, **stop** — `_audit/` would become a set of
live, crawlable URLs on economicsacademy.co.uk.~~

---

## The rules, restated because they are easy to drift from

1. **Read-only on the site.** Only `_audit/**` may be written. Four exceptions
   have been taken, each on Eliot's explicit instruction and each recorded:
   the `.gitignore` block (D1), the spec-PDF removal (D12), the `.codex/` move
   (D14), and the CLS correction to `seo/09-web-vitals-baseline.md` (D21).
   **A grant of permission is not a licence to skip verification** — D24 is the
   case that proves it: permission to swap the SVG diagrams was given, inspection
   came first anyway, and inspection stopped the swap.
2. **No opportunistic fixes.** Trivial problems become findings.
3. **The SEO work of 2026-08-08 is protected.** Read `DO-NOT-BREAK.md` before
   recommending anything.
4. **Never guess.** File path + line, command output, or a count. Otherwise
   UNKNOWN, and into `OPEN-QUESTIONS.md`.
5. **URLs are frozen.** GitHub Pages issues no 301. Any URL-affecting proposal is
   flagged HIGH RISK with a redirect strategy and rollback plan.
6. **Economics prose is untouchable.** HTML structure is fair game; the words are
   not, in any circumstance.
7. **Never bulk-read HTML.** Sample 2–3 per family, script the rest, state the
   sampling logic.

---

## Done in Phase 0

- `.gitignore` — added the `_audit/` block, verified ignored before writing.
- `docs/audit/scripts/lib.py` — shared read-only helpers. File lists come from
  `git ls-files`, so local cruft cannot skew a count.
- `docs/audit/scripts/link_graph.py` — the link graph, computed twice.
- `docs/audit/scripts/metadata_census.py` — `<head>` and JSON-LD census.
- `docs/audit/00-INVENTORY.md` — repo map, injection mechanism, page families, data
  layer, board dimension, GSC cross-check, protected-work enumeration.
- `docs/audit/findings/PH00-baseline.md` — 11 findings + the resolved-already log.
- `docs/audit/DO-NOT-BREAK.md` — the protection register, started early on purpose.
- `docs/audit/AUDIT-PLAN.md`, `OPEN-QUESTIONS.md`, `DECISIONS.md`.

### The five things worth knowing before P1

1. **No build step exists.** No `package.json`, `Gemfile`, `.github/`, CI or
   hooks. GitHub Pages' default Jekyll build, governed entirely by
   `_config.yml`'s `exclude`. There is **no `.nojekyll`** and there must not be.
2. **Header/footer are `fetch()` + `outerHTML`** on all 463 pages
   (`js/components/inject-templates.js:116-140`). **Breadcrumbs and JSON-LD are
   NOT injected** — they are static in the source.
3. **The recent internal-linking work is in page bodies, not the templates**, so
   a non-rendering crawler sees it. This was the brief's anticipated CRITICAL
   finding and it does not apply. What the injection costs is equity
   distribution, not discovery — 461 of 463 pages are reachable without JS.
4. **Technical SEO is clean**: 0 duplicate titles, 0 duplicate descriptions, 0
   canonical mismatches, 0 broken internal links, sitemap ⇄ filesystem diff of 0.
   Do not go looking for these again; watch for regression instead.
5. **The real risks are structural**: four URL grammars, three spellings of
   "Edexcel A", 463 hand-maintained `<head>` blocks.

### Baseline verifier state — record this, it is the audit's control

Run on `8c8034b` before any audit work:

| Script | Result |
| --- | --- |
| `verify_html.py` | 179 files parsed, **0 errors** |
| `verify_links.py` | 179 pages, 5,329 internal refs, **0 broken hrefs, 0 broken fragments** |
| `verify_liquid.py` | 106 files, **1 problem — exits 1**. Pre-existing false positive, finding PH00-011 |

~~`verify_liquid.py` failing is the **expected** state today. If it ever reports 0,
someone has changed something; if it reports 2, look at what was added.~~

**Superseded 2026-08-09 by D31.** The table above is the baseline as measured on
`8c8034b` and stays as a record. PH00-011 has since been fixed: `verify_liquid.py`
parses `_config.yml`'s `exclude` and now reports **1 file checked, 0 problems,
exit 0**. Reporting 0 is no longer a signal that something changed — it is the
pass condition. A problem now means a genuine deploy risk.

---

## Done in Phase 1

- `docs/audit/findings/PH01-structure.md` — 7 findings (PH01-012 … PH01-018), the
  URL-shape rule for the next page family, and answers to Q14 and Q15.
- PH00-005 and PH00-009 marked RESOLVED — both closed by Eliot-authorised
  changes, not by audit action.

**Two site changes were made in Phase 1 on Eliot's explicit instruction**, and
are the only site edits in the audit beyond `.gitignore`:

| Commit | Change |
| --- | --- |
| — | 26 Finder duplicate files deleted (all gitignored, none tracked) |
| `d220ad0` | The two exam-board specification PDFs removed; sitemaps regenerated |
| `d7744c3` | `.codex/` removed, content moved to `docs/`; `logo/` recorded as undecided |
| — | All 14 merged branches deleted, local and remote (refs only — every tip is still an ancestor of `main`) |

`d220ad0` is a **deliberate URL removal** against the frozen-URL rule, justified
on copyright grounds and recorded in `DECISIONS.md` D12 and `DO-NOT-BREAK.md`.

### What P1 established

- **Clean:** 0 case-sensitivity mismatches in any `src`/`href` (the live-vs-macOS
  trap), 0 references to non-existent files, 0 tracked files caught by an ignore
  rule, 0 dead ignore patterns, 0 branches with unmerged work.
- **PH01-012 is the headline:** 111 hardcoded board string literals across 9
  generators, including a two-board assumption baked into a ternary at
  `build_glossary.py:679`. This is the measured cost of PH00-003.
- **Published-surface leaks:** `logo/` (8 files, unreferenced),
  `old-logos-archive/` (13), `.codex/notes-workflow.md` (live at
  `/.codex/notes-workflow.html`), 10 unreferenced diagram PNGs.
- **Governance:** 12 progress documents, 9,336 lines, with known-defect logging
  split three ways between `REVIEW-NOTES.md`, `docs/CONTENT_ISSUES.md` and
  `PROJECT-LOG.md` — the last of which claims to be the only one.

---

## Done in Phase 5

- `docs/audit/scripts/board_similarity.py` — 5-word shingled Jaccard over body prose,
  boilerplate stripped, all 87 × 79 pairs. Pairing is an *output*: AQA uses
  site-local spec codes, so pages cannot be matched on code.
- `docs/audit/findings/PH05-boards.md` — PH05-019, PH05-020, PH05-021.
- Appended the board-differentiation block to `DO-NOT-BREAK.md`.

### The one thing to carry forward

**The duplication is real; the harm is not demonstrated, and the two must not be
conflated.**

- 26 Edexcel pages have an AQA twin at ≥0.80, **22 at ≥0.95**. A hand-checked
  pair (`3-4-2-perfect-competition` / `1-5-3-perfect-competition`) is 591 vs 592
  words differing by the single token `1.5.3`. CERTAIN.
- Every *other* signal is board-specific: title, H1, description and spec-alert
  differ on 26/26; outbound links share a mean Jaccard of 0.266 with no pair
  above 50%.
- **But zero AQA notes pages earn any impressions — because all 26 GSC
  "excluded by noindex" URLs were AQA notes pages, and the tag came off on
  2026-07-30, nine days before the export.** The measurement window is
  contaminated. Any duplication conclusion drawn before the day-45 re-measure is
  unsound, including one drawn from this audit's own similarity numbers.
- Counterintuitive and worth not re-deriving: keeping boilerplate *lowers*
  measured similarity (26 pairs → 6), because the template furniture is itself
  board-specific. It is doing differentiation work.

---

## Done in Phase 9

- `docs/audit/findings/PH09-data-model.md` — PH09-022/023/024, a `boards.json`
  design, and a worked "add OCR notes today vs ideally" comparison.
- Appended the data-model block to `DO-NOT-BREAK.md`.

### The one thing to carry forward

**The data is consistent; the model is not.** Keyed on `(board, spec)`,
`taxonomy.json` and `questions-data` agree on 166/166 titles and slugs — zero
disagreements. Nothing is corrupt.

- **PH09-022.** Four generators define a board four different ways, and
  `build_glossary.py` already carries a field literally called
  `"taxonomy": "edexcel"` to bridge its own `edexcel-a` to the taxonomy's
  `edexcel`. The need for one canonical identity is already recognised in the
  code — it is just solved privately in one file.
- **PH09-023.** Spec code is **not** a key: 37 of 129 collide across boards.
  Joining on `spec` alone yields 22 phantom disagreements. `questions.json` keys
  topics on bare slug with no board and is safe only because no slug happens to
  collide.
- **Adding OCR today = 9 files**, including a two-board assumption in a ternary
  at `build_glossary.py:679` that fails silently. With `boards.json` it is 2.

---

## Done in Phase 9b

- `docs/audit/findings/PH09b-generation-drift.md` — PH09b-025, PH09b-026, the
  generation-coverage census, and the verifier baseline.
- **Corrected PH00-004**: the hand-maintained `<head>` count is **190, not 463**.

### The one thing to carry forward

**Idempotence is essentially perfect, and no generated file has been
hand-edited.** Running all six generators in a pristine `git worktree` checkout
of `d7744c3` changed **7 files, one line each** — a `"generated": "<date>"` stamp
in the six flashcard deck payloads and `questions.json`. All 273 generated HTML
pages, `taxonomy.json` and all 7 sitemaps came back byte-identical.

- **PH09b-025.** That build-date stamp means every rebuild produces a spurious
  diff, so "re-run, check `git diff` is empty, commit" does not work. Nothing
  reads the field — the only `grep` hits in `js/` are comments. Same defect
  `be3ec19` already fixed for the sitemap; the JSON payloads were missed.
- **PH09b-026.** `--check` validates **inputs only**. Four of the five generators
  never compare against committed output — 0 hits for `WOULD CHANGE`,
  `read_text() !=` or `filecmp` in each. All four reported success, then writing
  for real changed seven files. Only `build_sitemap.py:252` does a real
  comparison. Fix PH09b-025 first or the new check cries wolf every run.
- **Coverage: 273 generated (59%) / 190 hand-written (41%).**

---

## Done in Phase 6

- `docs/audit/findings/PH06-html-architecture.md` — the full proposal: current-state
  analysis, six costed options, a seven-phase migration plan with a ten-assertion
  verification harness, what it unlocks, and a one-page decision brief that
  includes the honest case against migrating. **6 findings, PH06-027 … PH06-032.**
- `docs/audit/scripts/page_anatomy.py` — boilerplate volume, head/body skeletons,
  content spines, heading hierarchy and accessibility basics, cost-of-change.
- `docs/audit/scripts/notes_drift.py` — spine shapes, teaser provenance, metadata
  drift, breadcrumb drift, the stale template, historical change costs.
- Q13 answered (D16: yes to a build step). D17 records the recommendation.
  Q18, Q19, Q20 raised — **all three gate implementation**.
- `DO-NOT-BREAK.md` gained an HTML-architecture block.

### The five things worth knowing before P8

1. **The recommendation is a Python shell module, not an SSG.** `page_shell.py`,
   stdlib-only, imported by all five generators; output committed exactly as the
   existing 273 generated pages already are. **It is the only option of six that
   ends with the `<head>` defined once** — Liquid and Nunjucks cannot be called
   from `build_glossary.py`, so Jekyll and Eleventy both leave it defined twice.
   Second choice Eleventy, third Jekyll, Astro ruled out. D17.
2. **The shell is far more uniform than Phase 0 implied.** All 166 notes topic
   pages share **one** body skeleton, **one** script tail, **one** stylesheet set
   and just **4 `<head>` shapes** — one of which is legitimate (40 pages have no
   maths). The content spine has 9 shapes and 6 of those are only which optional
   footer link is present. PH00-004 overstated the disorder as well as the count.
3. **`scripts/convert_raw_notes.py` is a live hazard.** It holds a full notes-page
   template that predates seven SEO commits and would ship a page with no
   canonical, no social cards, no structured data and **no web fonts**. 73 raw
   markdown sources are still sitting there. PH06-027, and in `DO-NOT-BREAK.md`.
4. **P8 can reuse both new scripts directly.** `page_anatomy.py` §4 already
   produced P8's accessibility census: exactly one `<h1>` on 463/463, **zero**
   skipped heading levels, **zero** missing `alt` across 309 images, zero missing
   `width`/`height` outside 3 root images. What is left for P8 is the 94 images
   without `loading`, the 51 inline-`style` pages (44 hand-written, 7 generated),
   the 341 breadcrumbs without `aria-label`, and the 462 pages with no `<main>`.
5. **The proposal was approved as put on 2026-08-09** (D18) — option (f), Actions
   for verification only, all six normalisations. **Nothing has been implemented.**
   The audit remains read-only until Q21 settles when building starts; D19 records
   that approving *what* is not the same as deciding *when*.

---

## Superseded: the Phase 6 kickoff brief (kept for the reasoning)

**HIGHEST PRIORITY. OWN SESSION. Do not start without checking in** — the brief
says so, and the phase is large enough that a cold session should begin here
rather than inherit a half-full context.

**Scope, now quantified by P9b.** Not 463 pages — **190**. Of those, 176 are
revision-note topic pages and hubs. The other 273 already have a template layer
in their Python generator.

**The central design question**, which P9b surfaced: a template layer covering
the hand-written 190 must either **coexist** with four generators that emit their
own `<head>`, or absorb them. Coexistence means the same `<head>` defined twice,
in two languages, which is the problem restated rather than solved.

**Options to cost** (Q13, still unanswered — put it to Eliot at kickoff):

1. Change nothing; keep using scripted rewrites for sitewide `<head>` changes.
2. Jekyll front matter + `_includes`. GitHub Pages already runs Jekyll. Adds no
   tooling and **changes no URL**, but touches all 190 files once and makes the
   deploy depend on Liquid parsing every page — today a stray `{%` only risks
   markdown, and there are only 2 such files (PH00-011).
3. Extend the existing Python generators to cover the 190.
4. A real SSG. Rule this out explicitly — biggest URL risk, no redirects available.

**Hard constraints for whatever is proposed.** Read `DO-NOT-BREAK.md` first, in
particular: the `spec-alert` and `notes-cta` blocks are board-specific and are
doing real SEO differentiation work on the 22 near-identical page pairs (P5); the
two `@import` rules must stay hoisted into each `<head>`; and economics prose is
untouchable in all circumstances.

**Good looks like.** A costed, staged proposal that changes zero URLs, keeps
output byte-comparable at each step, and can be abandoned halfway without leaving
the site inconsistent.

---

## Done in Phase 8

- `docs/audit/findings/PH08-frontend.md` — 14 findings, `PH08-033` … `PH08-046`,
  plus a clean list, two hand-offs and a decision brief.
- `docs/audit/scripts/asset_census.py` — nine read-only censuses: stylesheets,
  scoping, selector reach, scripts, `<head>` order, images, fonts, ARIA, GA4.
  Run a section alone with `python3 docs/audit/scripts/asset_census.py 6`.
- `DO-NOT-BREAK.md` gained a front-end block and 10 new assertions.
- Q22–Q25 raised. **None blocks the remaining phases.**

### The five things worth knowing before P3

1. **CLS is not 0.000, and the SEO report says it is.** PH08-035 is the finding
   with teeth. `seo/lh-live-after-7run.json` — committed in `8c8034b`, part of the
   protected work — records **past-paper-questions 0.253** and **notes-topic
   0.110** against Google's 0.1 threshold, while
   `seo/09-web-vitals-baseline.md` still asserts "no layout-shift problem exists"
   from its superseded 3-run data. The ppq mechanism is identified and certain:
   `.ppq-controls` ships `hidden`, nothing reserves its height, and
   `question-search.js:682` reveals it only after a **414 KB** `fetch` resolves.
   The notes-topic cause is **UNKNOWN** and must be measured, not guessed.
2. **Do not re-audit the asset inventory. It is clean.** 0 unreferenced
   stylesheets, 0 unreferenced JS, 0 unresolvable `href`/`src`, 1 GA4 ID and 1
   gtag snippet on 463/463, 0 dangling `aria-controls`, 0 duplicate `id`, 0 unsafe
   `target="_blank"`, 0 non-descriptive link texts, skip-link target present on
   463/463. Watch for regression; do not go looking again.
3. **P8 extends P6 in two places rather than contradicting it.** P6 measured
   raw source and was right about it. Adding the runtime-injected templates:
   **every page renders two `<h1>`** (the template's "Economics Academy" first,
   PH08-036), and **no page has a `<footer>` or banner landmark** because both
   templates use `<section>` (PH08-037) — so all three principal landmarks are
   missing sitewide, not just `<main>`.
4. **The D18 normalisation list needs a correction before it is executed.**
   PH08-042: 1,187 of the site's 1,520 inline styles are KaTeX output and must
   never be touched; only 333 are authored, across 45 files including
   `templates/footer.html`, which nobody had counted. And six of the nine
   `<style>` blocks are deliberate `<noscript>` fallbacks — the real violations
   are three, not one.
5. **The pattern is P6's pattern again: conventions only reach generated pages.**
   Wrapper scoping (5 generated sheets + `privacy.css`, versus 13 hand-written
   sheets), `size-adjust` fallback metrics (173 pages), `decoding` on images (89
   of 309), `<noscript>` (15 pages), breadcrumb `aria-label` (100 of 441). P8
   therefore recommends **no new sitewide hand-edits before the shell module
   exists**, except where a fix lives in exactly one file.

---

## Next: Phase 3 — internal linking & crawl depth

Scope per `AUDIT-PLAN.md`: BFS click depth from `/` on the **raw** graph;
anchor-text distribution (the ppq topic-chip monoculture — 68 links reading
`2.6.2 Demand-side Policies`); hub/spoke integrity; fragment targets; PH00-001.

Reuses `docs/audit/scripts/link_graph.py`, which already computes both graphs. Low
context cost, no own session needed.

**Two things P3 must settle for other phases**, both already waiting on it:

- **PH00-001, nav-only link equity.** Eleven URLs draw ≥98% of inbound links
  from the injected templates, including the site's two best-earning non-homepage
  URLs. D3 deferred the judgement to P3.
- **D18's migration Phase 7** (baking the header/footer at build time) is gated
  on P3's ruling, and PH08-043 (removing jQuery) is gated on that in turn.

**First commands, every session — these are the audit's control:**

```
python3 docs/audit/scripts/link_graph.py        # regression: expect 0 broken, 461/463
python3 docs/audit/scripts/metadata_census.py   # regression: expect 0 dupes
python3 scripts/build_sitemap.py --check    # regression: expect "nothing written"
python3 docs/audit/scripts/page_anatomy.py      # P6 baseline: 4 head shapes, 9 spines
python3 docs/audit/scripts/notes_drift.py       # P6 baseline: 18 / 341 / 1 / 166
python3 docs/audit/scripts/asset_census.py 1 4 9  # P8 baseline: 0 / 0 unreferenced, 1 GA4 id
```

All six were clean at the end of P8.

---

## Done in Phase 3

- `docs/audit/findings/PH03-linking.md` — 4 findings, `PH03-048` … `PH03-051`, plus
  a clean list and the ruling migration Phase 7 was waiting for.
- `docs/audit/scripts/link_depth.py` — BFS click depth (raw and injected), anchor-text
  distribution, hub/spoke integrity, fragment resolution, PH00-001 quantified.
- **PH00-001 CLOSED.**
- One correction to `00-INVENTORY.md` §3, recorded in the findings file.

### The four things worth knowing before P4

1. **Depth 4 is removable with 8 links from 2 pages.** Today 253 of 463 pages sit
   at raw depth 4 — the whole practice-questions family and most of the
   past-paper-questions one. Only four pages are at depth 1, so only they can pull
   a hub up. Simulated: `/revision-notes/` → the 6 practice hubs, plus
   `/past-papers/` → the 2 ppq board hubs, takes the maximum raw depth to **3**
   and leaves **0** pages at 4. The intuitive fix (each notes board hub → its
   practice twin) moves only 6 pages, because those hubs are themselves at depth 2.
2. **PH00-001's answer is that the injection costs depth, not discovery — and the
   two pages where equity actually bites cannot be fixed by linking.**
   `/past-papers/edexcel-b/` and `/past-papers/ocr/` have **one** raw inbound link
   each and earn **291 clicks / 21,131 impressions** between them, the most on the
   site outside the homepage. They have one link because nothing on the site is
   *about* those boards. `seo/07b-link-decisions.md` item 4b already declined
   manufacturing links there, for that reason, and **P3 does not re-propose it**.
3. **Two whole categories came back perfect and must not be re-audited:**
   hub/spoke integrity (13 directories, 332 spokes, **0** missing links in either
   direction, 166/166 notes↔mcq both ways) and fragment targets (**4,979**
   `#anchor` links, **0** unresolved, checked cross-page).
4. **The ppq topic-chip monoculture is gone.** `AUDIT-PLAN.md` carried it into P3
   as scope; measured today it is **0** links with that string and **0** using the
   `?topic=` form. `55dda8a` fixed it before the audit began.

---

## Next: Phase 4 — structured data validity

Scope per `AUDIT-PLAN.md`, already slimmed: titles, descriptions, canonicals,
`og:url`, `lang`, robots and sitemap are verified clean and are **not** re-audited.
What remains is that every JSON-LD block parses, required properties are present
per type, `@type` choices are defensible, and the family-level gaps are ruled on.

**P4 arrives carrying three specific questions:**

- **Q11 / PH00-007** — `EducationalOrganization` on 354 of 463 pages but on none
  of the 90 `/past-paper-questions/` pages and no section hub. Deliberate or
  oversight?
- **PH08-045** — 19 pages emit `BreadcrumbList` with no visible breadcrumb trail:
  6 root, 6 notes-hub, 5 past-papers, `revision-notes/index.html`,
  `practice-questions/index.html`. P8 handed this here so both are decided
  together.
- `metadata_census.py`'s PARTIAL rows — several families emit a type on all but
  one page (e.g. `Question` on 25/26 aqa-a2-macro practice pages). Establish
  whether each is a real gap or a legitimately different page.

**First commands, every session — these are the audit's control:**

```
python3 docs/audit/scripts/link_graph.py          # 0 broken, 461/463 reachable
python3 docs/audit/scripts/metadata_census.py     # 0 dupes, 0 canonical mismatches
python3 scripts/build_sitemap.py --check      # "nothing written"
python3 docs/audit/scripts/page_anatomy.py        # P6: 4 head shapes, 9 spines
python3 docs/audit/scripts/notes_drift.py         # P6: 18 / 341 / 1 / 166
python3 docs/audit/scripts/asset_census.py 1 4 9  # P8: 0 / 0 unreferenced, 1 GA4 id
python3 docs/audit/scripts/link_depth.py 3 4      # P3: 0 hub gaps, 0 bad fragments
```

All seven were clean at the end of P3.

---

## Done in Phase 4

- `docs/audit/findings/PH04-structured-data.md` — 4 findings, `PH04-052` … `PH04-055`.
- `docs/audit/scripts/structured_data.py` — parses every JSON-LD block, checks
  required properties per type, family coverage, breadcrumb integrity, `@type`
  inventory, and cross-checks URLs/dates/canonicals.
- **Q11 / PH00-007 answered by measurement** (D26). **PH08-045 closed** by PH04-053.
- PH06-030 independently confirmed by a second method.

### The four things worth knowing before P7

1. **The Quiz markup is the site's best structured-data asset and must not be
   refactored.** 166 `Quiz` nodes, **1,267** `Question` nodes, **0** missing any
   field Google requires for the practice-problems rich result. Every answer
   carries a `Comment` explanation. This is the one rich result the site is
   positioned to win.
2. **Q11's answer is that it was never a decision.** The ppq and mcq-hub
   generators emit `WebSite` where the others emit `EducationalOrganization` —
   two generators, two boilerplates, each internally consistent. A copyright
   motive is ruled out because those pages already name the site as publisher
   another way. And all 100 `WebSite` nodes lack `potentialAction`, so 99 of them
   do nothing at all.
3. **Structured data is otherwise in very good order.** 921 blocks, **0** parse
   errors; 460 breadcrumbs with **0** bad positions and **0** unresolvable item
   URLs; **0** placeholder values; **0** non-ISO dates; **0** disagreements
   between a page's JSON-LD `url` and its own canonical.
4. **Two of P4's own first-pass flags were false positives** and are recorded as
   such in §4 of the findings file so nobody "fixes" them: the 179 `Course` nodes
   missing `description` are `isPartOf` *references*, not page entities; and
   `index.html`'s context-less first block is a valid JSON-LD array whose members
   each carry `@context`.

---

## Next: Phase 7 — information architecture & UX

Scope per `AUDIT-PLAN.md`: taxonomy and label consistency across boards and
resource types; nav structure; click depth to key tasks; search and filter
usability; mobile; conversion paths to tutoring and marking; print styles.

**P7 arrives carrying three things already measured:**

- **Click depth** is done — P3 §1. Do not re-measure it; use it.
- **Print styles** were measured in P8 and handed here: only **5** `@media print`
  blocks exist, in `revision-notes-textbook.css` (3), `glossary.css` (1) and
  `flashcards.css` (1). The 166 practice-question pages, 90 past-paper-question
  pages, 5 past-paper hubs and 9 root pages have none. Students print revision
  material; whether that matters is P7's judgement to make.
- **PH04-053's 19 pages with no visible breadcrumb** are a navigation gap as much
  as a structured-data one, and they include every past-papers hub.

Then **P10** (tooling, automation & governance) and **P11** (synthesis).

**First commands, every session — these are the audit's control:**

```
python3 docs/audit/scripts/link_graph.py           # 0 broken, 461/463 reachable
python3 docs/audit/scripts/metadata_census.py      # 0 dupes, 0 canonical mismatches
python3 scripts/build_sitemap.py --check       # "nothing written"
python3 docs/audit/scripts/page_anatomy.py         # P6: 4 head shapes, 9 spines
python3 docs/audit/scripts/notes_drift.py          # P6: 18 / 341 / 1 / 166
python3 docs/audit/scripts/asset_census.py 1 4 9   # P8: 0 / 0 unreferenced, 1 GA4 id
python3 docs/audit/scripts/link_depth.py 3 4       # P3: 0 hub gaps, 0 bad fragments
python3 docs/audit/scripts/structured_data.py 1 4  # P4: 0 parse errors, 0 bad positions
```

All eight were clean at the end of P4.

---

## Done in Phase 7

- `docs/audit/findings/PH07-ia-ux.md` — 4 findings, `PH07-056` … `PH07-059`, plus the
  nav tree, the board-label matrix, the conversion-path table, and the print-style
  judgement received from P8.
- Q16 and Q17 answered (D27, D28). **PH01-013 resolved by decision.**
- PH04-055 amended (D29) because Q17 was answered the opposite way to its premise.

### The four things worth knowing before P10

1. **PH07-056 is the finding worth reading twice.** Edexcel A is named six
   different ways in text students read — `Edexcel`, `Edexcel A`,
   `Edexcel Theme 1`, `Edexcel A Theme 1`, `Edexcel Papers`, and the full
   `Edexcel Theme 1: Introduction to Markets and Market Failure`. Only **10 pages
   of 463** ever write "Edexcel A". The site publishes past papers for four boards
   and notes for two, so a student arriving on `/past-papers/edexcel-b/` — one of
   the two best-earning URLs on the site — has no way to learn from the notes
   section that those notes are not for their board. **This is the user-facing
   half of PH00-003**, which P9 audited only in the data.
2. **The fix must add specificity, never remove it.** P5 established that on the
   22 near-identical Edexcel/AQA pairs the breadcrumb is one of the few
   differentiators. `Edexcel Theme 1` → `Edexcel A Theme 1` adds a token and is
   safe; anything that shortens a breadcrumb is not. And it is **visible text
   only** — no URL, slug or directory name moves.
3. **Two responsive breakpoint systems are live on every page.** `css/main.css`
   carries both the inherited theme's set (1680/1280/980/736/480) and Bootstrap's
   (992/768/576) — it contains 736, 767 *and* 768. `revision-notes-textbook.css`,
   on 169 pages, switches at 768 while the page chrome switches at 736, so between
   737 px and 768 px the notes render tablet chrome around desktop content.
4. **Print styles are correct as they stand and were declined as a finding** —
   §6 of the findings file says why, so it is not raised again.

---

## Next: Phase 10 — tooling, automation & governance

Scope per `AUDIT-PLAN.md`: the 25 `scripts/` and 11 unique `seo/tools/`; which
checks are automatable; GitHub Actions feasibility given there is no CI; pre-commit
hooks; the quality of `CLAUDE.md`; the overlapping progress documents.

**P10 arrives carrying a lot that is already decided or measured:**

- **D18/Q19 already approved GitHub Actions for verification only, never in the
  deploy path.** P10 designs the workflow; it does not re-litigate whether to have
  one.
- **PH09b-026** — `--check` validates inputs only on four of five generators.
  **PH09b-025** — the build-date stamp makes every rebuild produce a spurious diff,
  so fix that first or the new check cries wolf.
- **PH01-017** — the sitemap drifts because nothing re-runs `build_sitemap.py`.
- **PH00-011** — `verify_liquid.py` reports 1 pre-existing problem and **that is
  the expected state**. A workflow must not treat it as a failure.
- **PH07-059 hands over one concrete gap:** CLAUDE.md's CSS conventions say
  nothing about breakpoints, and there are two systems.
- P1 measured the governance surface: **12 progress documents, 9,336 lines**, with
  known-defect logging split three ways between `REVIEW-NOTES.md`,
  `docs/CONTENT_ISSUES.md` and `PROJECT-LOG.md` — the last of which claims to be
  the only one. The audit has since added its own `_audit/` tree, which P10 should
  say what happens to.

**First commands, every session — these are the audit's control:**

```
python3 docs/audit/scripts/link_graph.py           # 0 broken, 461/463 reachable
python3 docs/audit/scripts/metadata_census.py      # 0 dupes, 0 canonical mismatches
python3 scripts/build_sitemap.py --check       # "nothing written"
python3 docs/audit/scripts/page_anatomy.py         # P6: 4 head shapes, 9 spines
python3 docs/audit/scripts/notes_drift.py          # P6: 18 / 341 / 1 / 166
python3 docs/audit/scripts/asset_census.py 1 4 9   # P8: 0 / 0 unreferenced, 1 GA4 id
python3 docs/audit/scripts/link_depth.py 3 4       # P3: 0 hub gaps, 0 bad fragments
python3 docs/audit/scripts/structured_data.py 1 4  # P4: 0 parse errors, 0 bad positions
```

All eight were clean at the end of P7.

---

## Done in Phase 10

- `docs/audit/findings/PH10-tooling.md` — 4 findings, `PH10-060` … `PH10-063`,
  the timed verification-suite table, and the `verify.yml` workflow D18 approved.

### The four things worth knowing before P11

1. **The entire verification suite runs in 13.1 seconds** — 13 checks, no
   dependencies beyond Python 3 and Node, no network, all green except the one
   known `verify_liquid.py` problem. **Nothing runs any of it.** That number is
   the whole automation argument, and PH01-017, PH09b-026 and PH06-027 are all
   waiting on somewhere to run.
2. **PH10-060 is the finding the audit nearly missed.**
   `revision-notes/macro-application/macro-application-uk-sa.md` — 429 lines of
   source markdown — is tracked, **not excluded**, and served live. It went unseen
   for ten phases because **every enumeration tool in the repo globs `*.html`**:
   `lib.is_published()` says True and `lib.published_html()` says False for the
   same file. `_config.yml`'s exclude list is maintained by directory and cannot
   catch a source file inside a content directory.
3. **CLAUDE.md's counts have drifted, and one of them disagrees with a script that
   prints the truth on every run.** "300 note diagrams" is 112. "46 definitions"
   rewritten is 44 — `verify_glossary.py` check 7 has been saying `44/44` all
   along. "7 that add wording" is 3. The structural claims are all correct; only
   the numbers are stale. Cite the command, not the value.
4. **`_audit/` is gitignored (D1), so it is not in git history at all.** P11 must
   say what becomes of it. Leaving it ignored and undiscussed is the one option
   that loses the work.

---

## Next: Phase 11 — synthesis. The last phase.

Per `AUDIT-PLAN.md`: a prioritised roadmap (impact × effort × risk), sequencing
and dependencies, `DO-NOT-BREAK.md` finalised, and a rollback plan for anything
URL-affecting.

**What P11 has to work with:** 63 findings across 10 phases, every one of the 26
open questions answered, and D18's approved architecture proposal waiting to be
built.

**The sequencing constraints already established, which P11 must respect:**

- **PH09b-025 before PH10-062** — the build-date stamp must stop producing
  spurious diffs before any idempotence check is automated.
- **PH00-011 before `verify_liquid.py` joins the workflow** — a red-from-day-one
  workflow is one nobody reads.
- **P8's inline-style work before or with D18's normalisation 5 and 6** —
  PH08-042 corrected the target list (333 authored attributes across 45 files
  including `templates/footer.html`; 1,187 KaTeX styles that must never be
  touched; 3 real `<style>` violations, not 1).
- **PH07-056's board labels with PH09-022's `boards.json`** — a `displayName`
  field is where the label belongs; doing the labels first re-creates the drift.
- **Migration Phase 7 is unblocked** — P3 ruled on it: proceed on its own merits
  (one source of truth for the nav, no runtime fetch, drops one of jQuery's three
  consumers), but **not** as a link-equity fix, because it is not one.

**Dated dependency:** the day-45 GSC re-measure, ≈**2026-09-22**. PH05-019,
PH05-021 and PH03-049 step 2 are all waiting on it.

**First commands, every session — these are the audit's control:**

```
python3 docs/audit/scripts/link_graph.py           # 0 broken, 461/463 reachable
python3 docs/audit/scripts/metadata_census.py      # 0 dupes, 0 canonical mismatches
python3 scripts/build_sitemap.py --check       # "nothing written"
python3 docs/audit/scripts/page_anatomy.py         # P6: 4 head shapes, 9 spines
python3 docs/audit/scripts/notes_drift.py          # P6: 18 / 341 / 1 / 166
python3 docs/audit/scripts/asset_census.py 1 4 9   # P8: 0 / 0 unreferenced, 1 GA4 id
python3 docs/audit/scripts/link_depth.py 3 4       # P3: 0 hub gaps, 0 bad fragments
python3 docs/audit/scripts/structured_data.py 1 4  # P4: 0 parse errors, 0 bad positions
```

All eight were clean at the end of P10.

---

# THE AUDIT IS COMPLETE — 2026-08-09

**11 phases. 63 findings. 26 questions asked and answered. 0 site files changed
except the four Eliot authorised** (`.gitignore`, the spec-PDF removal, the
`.codex/` move, the CLS correction).

## Start here

**`docs/audit/findings/PH11-synthesis.md`** is the deliverable. It holds the
prioritised roadmap, the sequencing constraints, the "what NOT to do" list, the
rollback plans for the only two URL-affecting changes, and §6's suggested order.

Everything else is evidence: `DO-NOT-BREAK.md` (finalised), `DECISIONS.md` (D1–D29,
append-only), `OPEN-QUESTIONS.md` (all 26 answered), `00-INVENTORY.md`, and ten
`findings/` files.

## The one decision with a deadline

**`_audit/` is gitignored under D1, so none of this is in git history.** D1's
reasoning was sound when the audit was a list of defects; it expires the moment
the roadmap starts, because the roadmap *is* the audit. PH11 §5 sets out three
options and recommends moving it to `docs/audit/` — already excluded from
publishing, so it stays off the site while entering history, which was D1's actual
concern. **If that is chosen, the `_audit/` line must come out of `.gitignore` in
the same commit or the move silently does nothing.**

## If you do nothing else

Wave 0 of the roadmap: **nine single-file edits, about an hour, no dependencies,
zero URL changes.** The first of them — a `min-height` on `.ppq-controls` — closes
a 0.253 CLS on 90 pages and is the highest value-per-line change in the audit.

## The scripts, and what they are for

`docs/audit/scripts/` reproduces every figure in this audit in about 20 seconds and
writes nothing:

| Script | Reproduces |
| --- | --- |
| `lib.py` | shared helpers; file lists come from `git ls-files` |
| `link_graph.py` | the raw-vs-injected link graph, orphans, injection dependency |
| `metadata_census.py` | `<head>` and JSON-LD census |
| `board_similarity.py` | P5's shingled Jaccard over 87 × 79 board pairs |
| `page_anatomy.py` | boilerplate volume, head/body skeletons, accessibility basics |
| `notes_drift.py` | spine shapes, teaser provenance, metadata and breadcrumb drift |
| `asset_census.py` | stylesheets, scoping, dead CSS, scripts, images, fonts, ARIA, GA4 |
| `link_depth.py` | BFS click depth, anchor text, hub/spoke, fragments |
| `structured_data.py` | JSON-LD parse, required properties, coverage, breadcrumbs |

**They are read-only by construction and were never given write access to a site
file.**

---

# IMPLEMENTATION — started 2026-08-09

The audit is finished and the roadmap is being built.
**`findings/PH11-synthesis.md` §2 is the plan; this section is the state.**

## Done, merged to `main`, live

| Wave | Item | Finding | Commit |
| --- | --- | --- | --- |
| — | Audit moved to `docs/audit/`, committed | PH11 §5 | D30 |
| 1.2 | `verify_liquid.py` parses `_config.yml`'s `exclude` | PH00-011 | D31 |
| 0.2 | FontAwesome `font-display: block` → `swap` | PH08-033 | |
| 0.3 | Generic `sans-serif` fallback on the base stack | PH08-041.1 | |
| 0.4 | Focus rings on the colour-only `:focus` rules | PH08-040 | |
| 0.5 | Site title is a paragraph; one `<h1>` per page | PH08-036 | |
| 0.6 | `<header>`/`<footer>` landmarks; 11 inline styles → CSS | PH08-037 | |
| 0.7 | Flashcards promoted to a top-level nav item | PH07-057 | |
| 0.8 | CLAUDE.md counts corrected; cite commands | PH10-061 | |
| 0.9 | The two `Regulation` definitions logged as G4 | PH10-063 | |
| 0.1 | ppq filter panel ships visible; CLS 0.245 → 0.012 | PH08-035 | |
| 1.1 | Build-date stamp dropped from 7 JSON payloads | PH09b-025 | |
| 1.3 | `verify_generated.py` | PH09b-026 | |
| 1.5 | `verify_published_surface.py` | PH10-060 | |
| 1.6 | Capitalisation check fails on unclassified | PH10-063 | |
| 1.4 | `.github/workflows/verify.yml`, 15 steps, read-only | PH10-062 | |
| 4b | `macro-application-uk-sa.md` → `raw-notes/` | PH10-060 | D32 |
| 4.1 | 112 diagram PNGs to a 64-colour palette, 26.21 → 5.41 MiB | PH08-034, D25 | |
| — | `Regulation` defined on the Edexcel glossary page | PH10-063 | |
| 4.4 | `size-adjust` fallbacks in `main.css`; the two `ch` measures dropped | PH08-041, PH08-035 | |
| 4.2 | FontAwesome subset: stylesheet 69.4 KB → 2.9 KB, fonts 2.79 MiB → 1.5 KB | PH08-033 | |
| 4.3 | Per-topic ppq payloads, 413.7 KB → 9.6 KB median on 81 pages | PH08-046 | |
| 4.5 | 18 media queries 768 → 767, pairing with the nav boundary | PH07-059 | |
| — | `verify_image_dimensions.py`; 3 root photos gain dimensions | PH08-034 | |
| — | Nav fits one line at every desktop width (Flashcards made it 9 items) | — | |

**Wave 0 and Wave 1 are complete.** PH01-017 was hit twice during the work and
fixed both times; it is now guarded.

## Five things the roadmap got wrong, each found by measuring

Recorded because the same habit will be needed for Waves 2–5.

1. **0.1's stated fix could not work.** A `min-height` on `.ppq-controls`
   reserves nothing: the element ships `hidden` and the component enforces
   `[hidden] { display: none !important }`. The intermediate fix that looked
   right — revealing early from JS — improved 1280px and took 736px from 0.318
   to **0.799**, because the panel is 811px at mobile. Measured, rejected, not
   shipped.
2. **0.2 was a change, not an addition.** All three `@font-face` rules already
   had `font-display`, set to `block`, which *is* the FOIT.
3. **0.4 had two offenders, not three.** `contact.css` already carried a ring and
   is byte-identical to the audit baseline; the finding's table row is wrong.
4. **0.6's trap was the reverse of the one recorded.** There are no
   `section#header` selectors. The danger was that changing the element brings
   the theme's bare `header {}`, `header > p {}` and `footer {}` rules into scope
   for the first time.
5. **PH10-063 is Edexcel-only.** AQA already had a real definition from a chip
   actually titled "Regulation".

## Three traps worth carrying forward

- **`build_sitemap.py --check` prints "nothing written" on both paths.** It is
  not a pass signal. Read the exit code and look for `WOULD CHANGE`. Misreading
  it shipped a stale sitemap for one commit.
- **Local green does not imply CI green.** The workflow failed on its first run
  while all 15 steps passed locally, because `actions/checkout` clones shallowly
  and `build_sitemap.py` reads `lastmod` from `git log`. Fixed with
  `fetch-depth: 0`, reproduced with `git clone --depth 2` first.
- **Measure the element the reader sees, not its container.** 0.5 measured
  `.site-title` — correct throughout — while the `<a>` inside it went pink and
  underlined, because the theme styles `h1 a` and not `p a`.

## Wave 4 — in progress, started 2026-08-10

### 4.4 done. PH08-035 is fully closed, both halves

The roadmap's one-line version — move the `size-adjust` `@font-face` rules from
`quiz.css` to `main.css` — is necessary and **not sufficient**. Two additions
were needed and both were found by measuring, not by reading:

1. **An `@font-face` is inert until a `font-family` stack names it.** Only
   `quiz.css` did. `main.css`'s base stack was `"Source Sans Pro", sans-serif`
   and 13 rules in `revision-notes-textbook.css` said `font-family:
   "Source Sans Pro"` with no fallback at all. Moving the declarations alone
   would have measured as no change on the other 297 pages.
2. **`ch` is the one reflow `size-adjust` cannot absorb.** It is the advance of
   "0" alone; `size-adjust` matches *average* advance width. `.ppq-intro`'s
   `max-width: 60ch` is 442.5px in Source Sans Pro and 466.0px in the fallback,
   so the paragraph gained a line on swap. Fixing (1) without (2) took
   past-paper-questions **from 0.086 to 0.307 at 736px** — a real regression,
   caught before it shipped. Both `ch` measures are now `em`.

CLS, measured locally in headless Chrome with the shipped CSS. **Fonts as the
only moving part** (JS suppressed, so neither the header injection nor
`question-search.js` is in the number), median of two runs, 1280/800/736:

| page | before | after |
| --- | --- | --- |
| notes-topic | 0.026 / 0.144 / 0.131 | 0.001 / 0.002 / 0.001 |
| past-paper-questions | 0.023 / 0.003 / 0.065 | 0.000 / 0.001 / 0.001 |
| homepage | 0.002 / 0.004 / 0.024 | 0.001 / 0.003 / 0.002 |
| practice-questions | 0.001 / 0.001 / 0.001 | 0.001 / 0.001 / 0.001 |

Whole page, JS on, median of three:

| page | before | after |
| --- | --- | --- |
| notes-topic | 0.037 / 0.024 / **0.157** | 0.009 / 0.015 / 0.021 |
| past-paper-questions | 0.052 / 0.089 / 0.086 | 0.009 / 0.014 / 0.021 |
| practice-questions | 0.010 / 0.018 / 0.022 | 0.009 / 0.015 / 0.021 |

**PH08-035's notes-topic 0.110 was UNKNOWN and is now answered: web-font
reflow, the same cause as the past-paper-questions page.** All four page types
now sit on one residual — 0.009 / 0.015 / 0.021 — and that residual is
`section#main` moving when `inject-templates.js` swaps the header in. **That is
Wave 2 phase 7 and nothing in Wave 4 will touch it.**

Two side-effects, both checked rather than assumed:

- With the web font loaded the past-paper-questions page is **pixel-identical**
  before and after, at 1280 and 736.
- On a **cold** load MathJax typesets against whatever font is on screen. The
  new fallback's ex-height is **5.98%** off Merriweather where the old one was
  **19.19%** off, so a cold-load formula should render closer to the
  warm-cache one, not further away.

  **CORRECTED 2026-08-10, while measuring 4.5.** This originally said the notes
  pages "render maths 1–2px differently" and attributed an observed pixel diff
  to the change. That attribution was not established: two renders of the
  **same, unchanged** CSS were later found to differ by 60,726 pixels in a
  MathJax formula, so cold-load MathJax output varies between runs on its own.
  The ex-height figures above were measured independently and stand; the 4.4
  CLS result stands, three runs per point with tight variance. Only the
  pixel-diff attribution was overstated. **Cause of the variance: UNKNOWN** —
  MathJax loads from jsDelivr and races the web font, which is the obvious
  suspect and was not confirmed.

### 4.1 done. The palette is the whole saving; the resize is not

**26.21 MiB → 5.41 MiB, 79.4%, same filenames and same pixel dimensions, 0 HTML
edits.** Mean image weight on the 95 pages carrying a diagram: **709 KB → 146
KB**. Heaviest page, the microeconomics gallery: **11.3 MB → 2.4 MB**.
`scripts/reencode_diagrams.py --apply`, dry run by default.

**D25's two gates, both answered by measurement.**

- **No diagram needs a non-white backdrop, and the question is moot.** All 112
  are RGBA with **zero** non-opaque pixels — nothing is composited against the
  page at all. Twelve have one corner at 250–254 grey, which is render noise.
- **Quantisation is invisible on the shaded diagrams.** `j-curve` and
  `perfect-competition-short-run-supernormal-profit` are indistinguishable at
  display width. The worst-error window of the worst file (`trade-union`, 4,867
  source colours) is indistinguishable at 2×: 1,424 of 120,000 pixels differ by
  more than 16, all on antialiased edges. The whole microeconomics gallery page,
  rendered, has **0** pixels differing by more than 8 of 255.

**Two departures from the roadmap line, both forced by the measurement.**

1. **No resize to 1600px.** The palette alone is 79.4%; adding the resize gives
   81.7% — 0.61 MiB across the whole site. It would cost 293 `<img>` rewrites
   and sharpness on every 2× display: the notes container is ~1088 CSS px, so
   2176 device px, and the sources are 2200–3600px today. Resampling to 2200px
   measured **larger** than not resizing, because Lanczos invents intermediate
   colours the palette then spends entries on. **The resize is not where the
   saving comes from.**
2. **~3.2 MB is not reachable here.** That figure assumes pngquant/libimagequant,
   which is not installed and which Pillow does not carry. Pillow's fast-octree
   does reach 4.48 MiB and was rejected: it maps white to `(254,254,254)` on all
   112, which would put every diagram in a faint grey rectangle. Median cut
   keeps pure white on 112/112.

**Not idempotent until it was made so.** Median cut re-quantises a converted
file to different bytes; before the skip guard a second `--apply` rewrote 37 of
112 files to the same total size. That is PH09b-025's failure mode in a new
place.

**One pre-existing defect found by the same check and fixed.**
`long-run-growth-ad-lras.png` declared `1667x593` on
`revision-notes/macroeconomics-diagrams.html` against `3030x1454` on disk — the
one tag of 293 disagreeing with its file, reserving a box 35% too short. All 293
now agree.

**Still open, not decided here:** 11 of the 112 diagrams are referenced by
nothing (3.1 MiB before, 0.6 MiB now) and are published. They were re-encoded
with the rest. Whether they should exist at all is a published-surface question
of the same kind as D28's `logo/`, and is nobody's call but Eliot's.

### 4.2 done. One family, one weight, 15 glyphs

| | before | after |
| --- | --- | --- |
| `css/fontawesome-all.min.css` | 69.4 KB | **2.9 KB** — render-blocking in the `<head>` of all 463 pages |
| `webfonts/` | 2.79 MiB | **1.5 KB** (1,580 bytes) |

Same filename, so **no `<head>` was touched** and `4db232c` stands: still a
direct `<link>` in every page, ahead of the font stylesheet, and the two
`@import` rules stay out of `css/main.css`.

**The site's Font Awesome usage is far smaller than the roadmap's "20 icons".**
The markup is the theme's `.icon` convention, never Font Awesome's own: **0**
uses of `fas`/`far`/`fab`/`fal`/`fad`, **0** utility classes (`fa-2x`, `fa-fw`,
`fa-spin`), and 476 of 480 HTML files contain no `fa-` class at all. Of 1,458
icon rules, 15 are reachable; of three font families, one is. Brands (1.06 MiB)
was entirely unused — the six `ul.social li a.fa-*` rules in `main.css` that
look like users are background-colour rules for a social list the site has
never had.

**Who actually downloads the font, measured across 12 pages:**

| viewport | pages fetching `fa-solid-900.woff2` |
| --- | --- |
| 1280px | **4** — homepage, faq, contact, marking |
| 500px | **all 12** |

The mobile difference is one glyph: `#titleBar .toggle:before` is
`content: "\f0c9"` at weight 900 — the hamburger. That single character is why
459 otherwise icon-free pages pulled 76.4 KB on a phone. Correcting an earlier
claim in this file's history: it was never *every* page on desktop.

**One visible change, and it is a fix.** `faq.html` had 30
`class="icon fa-plus"` spans with no `solid`, asking for weight 400, where
`plus` is a solid-only glyph in Free 5. They rendered **nothing** — the
accordion has had no open/close indicator, and the JS has been toggling between
two invisible states. Dropping the Regular face leaves one face in the family,
so weight matching falls 400 → 900 and the `+`/`−` appears. The 30 spans now
say `solid` so that the fix does not depend on the family having exactly one
face. Pixel-verified: only the 13px column the icons sit in changes;
`contact.html`, `index.html`, `marking.html` and the mobile hamburger are 0
differing pixels, and the homepage's 140 differing pixels are sub-glyph
antialiasing, identical at 4×.

**`scripts/verify_icons.py` is in the workflow**, because a subset font fails
silently and the FAQ is the proof of how long that goes unnoticed. Stdlib only,
four failure modes, each tested by breaking it deliberately: a class with no
rule; a CSS `content` the subset lacks; a rule whose glyph is not in the font;
the font replaced without re-running. The third needs to read the woff2, which
needs brotli, so the subsetter writes `_working/fontawesome/subset-manifest.txt`
and the checker compares against that.

**Two dependencies now, both one-off, neither in CI:** Pillow for 4.1's
`reencode_diagrams.py`, fonttools + brotli for 4.2's `subset_fontawesome.py`.
Both default to dry run.

**PH09b-025's failure mode turned up for the third time.** The subsetter was not
deterministic until `recalcTimestamp=False` moved onto the `TTFont`
constructor — it is not the same thing as `subset.Options.recalc_timestamp`.
Caught by hashing three consecutive runs, which is now worth doing to anything
here that writes a file.

### 4.3 done. 81 topic pages stop fetching the whole bank

Each of the 81 topic pages fetched the full **413.7 KB** index to use a median
of 15 questions. Each now fetches its own payload, written beside it by
`build_past_paper_questions.py`:

| | |
| --- | --- |
| median | **9.6 KB** |
| largest | 26.0 KB — `1-3-2-externalities`, 23 questions |
| total across all 81 | 907 KB, against 32.7 MiB of repeated full payload |

**`past-paper-questions/questions.json` is untouched and still published**, as
DO-NOT-BREAK requires. The master page, the 2 board pages and the 6 section
pages still fetch it and must — their Topic filter lists every topic on the
board. Only the 81 pages carrying `data-prefilter-topic` get a payload, and
only those carry `data-src`.

**Two things that would have broken it, both checked before writing code.**

- **`papers` stays a sparse list**, `null` in every unreferenced slot.
  `question-search.js` addresses it as `data.papers[q.p]` — `q.p` is an
  *index*, so re-packing the list would silently re-point every question at
  the wrong paper. The nulls cost about 300 bytes. Confirmed the component
  only ever subscripts that field and never iterates it
  (`question-search.js:136`, `:393`).
- **`topics` keeps every topic any included question is tagged with**, not just
  the page's own, because each card renders a link per tag.

**One deliberate behaviour change.** `populate()` builds the Paper, Year,
Marks, Section and Qualification dropdowns from the payload, so they now offer
only values that exist on the page. A topic page used to list all 9 years where
a mean of **4.9** have questions, and all 3 papers where a mean of **1.7** do;
choosing one of the others returned nothing. Those dead options are gone.
Otherwise the rendered page is **pixel-identical** — 0 differing pixels at
1000px.

**The CLS half of this item was already closed by 4.4**, which took the
past-paper-questions page to 0.009 / 0.014 / 0.021 with the residual being the
header injection. 4.3 is weight only.

**Caught in passing:** `search_component()` assigned rather than appended to
`attr` in the topic branch, so `data-src` was silently dropped on exactly the
pages that needed it. The first run wrote 81 payloads that nothing fetched.

### 4.5 done — but not the change the roadmap asked for

**The roadmap's premise is wrong and the record should say so.** 4.5 says to
take `revision-notes-textbook.css` from 768 to 736 first, because PH07-059
records the page chrome as switching at 736. **It does not.** The nav switches
at 767/768 — `css/main.css:2334` puts the desktop `#nav` behind
`min-width: 768px` and `:2346` puts the mobile `#navPanel` behind
`max-width: 767px`. `main.css` runs **two tiers, both real**: 767/768 for the
nav, header and `#header-placeholder`, and 736 for `.container`, the row grid
and body sizing. `revision-notes-textbook.css` at 768 was already aligned with
the nav tier.

The 768 → 736 change was made, measured and **reverted**: outside 737–768 it
changed nothing, and inside that band it put full-size desktop notes underneath
a hamburger nav — creating the mismatch PH07-059 feared rather than removing
it. A screenshot at 752px settled it.

**The real defect was one pixel wide.** At exactly 768 the desktop nav shows
(`min-width: 768px`) *and* the content is mobile-styled (`max-width: 768px`).
768 is iPad portrait. **18 media queries across 11 stylesheets** moved to
`max-width: 767px`; both `min-width: 768px` rules were left alone, so the
pairing is now exclusive everywhere.

Measured on ten pages at 767 / 768 / 769: **767 and 769 pixel-identical before
and after on all ten**; 768 changes on eight, and now differs from 769 by only
the 12k–31k pixels a 1px reflow costs, against 167k–494k from 767. Before, the
768 render sat apart from both neighbours.

**The 736 tier was deliberately left alone.** Reconciling it with 767 means
changing the inherited theme's own breakpoints on all 463 pages, and nothing
measured says it is broken.

### 4.6 done for one sheet of three, and the other two are declined

**`revision-notes-textbook.css` is 132 / 0.** `asset_census.py 2` reported 11
bare selectors of 132 on 169 pages — nine `.diagram-figure` / `-image` /
`-caption` rules across three breakpoints, plus `.breadcrumb` and
`.breadcrumb .separator`, which beat `css/main.css:3233` and `:3252` on load
order. All 11 now carry `.revision-notes-content`. `:root` stays bare; CLAUDE.md
puts the colour tokens in this file and the census does not count it.

Checked over all 169 pages before editing, not on a sample: 169/169 carry the
wrapper on `<section id="main">`; all 169 breadcrumbs, 503 separators and 300
each of figure/image/caption are inside it and **0** outside; `.diagram-*` is
defined in no other stylesheet; the two `.breadcrumb` rules only rise in
specificity against rules they already won. **0 differing pixels across 15
renders**, five pages at 1280/700/400, against a 0-pixel noise floor.

**`contact.css` and `tutoring.css` cannot be scoped, and the finding is
measured.** PH08-038 says "no HTML changes are needed, because every one of
these pages already has a wrapper class on its `section#main`". Neither page has
one. Worse, on both pages `css/main.css` is currently **winning**, so scoping
does not remove a load-order dependency — it reverses the design:

| contact.html, plain `.contact-page` scoping | before → after |
| --- | --- |
| `.row.gtr-uniform` margin-top | −30px → 0 |
| `.col-*` padding-top, 6 elements | 30px → 0 |
| form height | 733.9px → 614.0px |
| `select` / `textarea` font-size, padding | 14.67px → 16px, 11/14.67px → 15px — while the text inputs keep 14.67px, because `form input[type="text"]` at (0,1,2) still beats (0,1,1) |
| `header.major`, its `h2` margin-bottom | 36.67 → 40px, 0 → 15px |

**tutoring.html is worse: the modal breaks.** `#contactModal` is a *sibling* of
`section#main`, so `.tutoring-page .modal` matches nothing —
`position: fixed → static`, `display: none → block`, and the enquiry form lands
inline on the page. 33 elements change, all in the modal subtree.

Three alternatives were measured and rejected. `:where(.contact-page)` scoping
is exactly cascade-neutral — **0 of 281 and 0 of 362 elements changed** — but it
does not remove the load-order dependency either, since the specificity is
unchanged; it buys the census metric and nothing else. Re-declaring what
main.css was winning still moved 33 elements. Moving the modal into
`section#main` is not free: it becomes the new `section > :last-child` and
shifts the margin on the element that used to be.

**What was done instead is the guard the risk actually needs.**
`scripts/verify_css_load_order.py`, the workflow's 19th step. Load order is what
keeps those two pages correct, it is now an invariant rather than an accident,
and **a `<head>` generated by Wave 2's `page_shell.py` is exactly what would
change it** — with no error and no failed request. Three checks, all green on
their first run, all five failure modes tested by deliberately breaking them:
`css/main.css` precedes the page sheet on **462/462**; `4db232c`'s order
(fontawesome → Google Fonts → main.css) holds on **462/462**, which until now
nothing checked; and exactly one page loads two page sheets, named rather than
counted, in the spirit of `build_past_paper_taxonomy.py`'s `EXPECTED`.

The other 11 unscoped sheets are left alone by the same reasoning. The roadmap
line says nine; the census says **11** — the two it misses are
`macro-application.css`, which has the wrapper and uses it on 21 of 35, and
`privacy.css`, which PH08-038 counts as scoped under `.privacy-notice` and the
census does not.

**Two measurement lessons, both expensive.** Gallery renders are not
deterministic: one run differed from its own baseline by 42,388 px and was
nearly attributed to the change. The cause is `loading="lazy"` on all 89 gallery
diagrams plus image-decode races, not the MathJax variance of 4.5. Second, a
scripted selector prefix mangled the comments in `contact.css` on the first
attempt — the "never bulk-rewrite with a script" rule earns its place on CSS as
well as prose.

### 4.9 done. The contradiction was real and both documents survive it

**`seo/07b-link-decisions.md` §5's "449" and "275" are PAGE counts, not link
counts.** That is what made the two documents look incompatible. Measured before
writing anything: **449 pages / 455 links** to `tutoring.html`, **275 pages /
276 links** to `marking.html` — §5's figures are still exactly current, so it
could not be dismissed as stale.

**The fact that settles it is in neither document: 444 of those 455 tutoring
links read `Book a Free Intro Call`.** 97.6%, across 8 distinct anchors. §5's
*next* bullet declines reusing an anchor string precisely because "adding more
deepens a monoculture". So ten more of the same string is the thing §5 objects
to, and ten links carrying new anchor text is not. §5 was written against the
*bulk* proposals in the same document — items 1–3 were 166- and 253-page sweeps.

| | before | after |
| --- | ---: | ---: |
| pages linking `tutoring.html` | 449 | **459** |
| pages linking `marking.html` | 275 | **285** |
| distinct tutoring anchors | 8 | **10** |
| distinct marking anchors | 7 | **9** |
| published pages with no commercial link | 13 | **2** |

**PH07-058 says ten pages; there were thirteen.** The three it missed are
`privacy.html` and `confirmation.html`, both correctly excluded, and
**`revision-notes/macro-application/index.html`** — the only 1 of 176 notes
pages with no link to a paid service. That page already *had* a `notes-cta`;
it was one button long. It now matches the two diagram galleries button for
button, which also answers the board question the component contract raises:
a page with no board points at `/past-papers/`, the hub, exactly as they do.

Both generators only, no generated HTML hand-edited; `glossary.css` 108/0 and
`flashcards.css` 125/0 unscoped; both new blocks hidden in `@media print`;
three consecutive runs of each generator hash identically, deck JSON included.

**Caught by rendering rather than reading:** the notes CTA's `#f8f8f8` panel is
invisible on these pages. It works on a topic page because `.notes-container` is
white; the glossary and flashcards blocks sit directly on `#main`, which
`css/main.css` paints `#f7f7f7`, so the block drew as a red bar floating in the
page with no panel at all. Both are white with a border. `macro-application`
kept `#f8f8f8` and is correct, because it *is* on a `.notes-container`.

### `verify_text_integrity.py` was wrong in both directions

Found while doing 4.9, and the two errors had been hiding each other because the
step had never been anything but green — checked over the last 15 commits on
`main`, all exit 0.

- **14 hand-written published pages were never compared:** the 9 root pages and
  the 5 `past-papers/` hubs. The root pages are the commercial surface, so the
  wording most worth protecting was the wording nobody checked.
  `templates/header.html` and `footer.html` were out too, and every nav label on
  all 463 pages comes from them.
- **The 3 generated glossary pages were compared**, which is the one place a
  legitimate change routinely appears. Their wording already has a stronger
  guarantee: `verify_glossary.py` check 1 and `verify_generated.py`.

Now 192 hand-written pages, enumerating through `build_sitemap.published()` like
`verify_liquid.py` and `verify_css_load_order.py`. Five modes tested by
breaking each.

### An approved content change now declares itself

4.9 opened a gap and closed it. `verify_text_integrity.py` cannot tell an
approved content change from prose tampering, and had no way to be told — so it
went **red on correct work**, which the workflow's own comment says is exactly
how a check gets ignored and then protects nothing. Wave 5 is nothing but
approved content changes and Wave 3's relabelling is another, so it would have
been red more often than green.

A commit that means to change visible text now names the pages it changes:

```
Text-Change: revision-notes/macro-application/index.html
```

one line per path, reason in the commit body. Three properties make it a
declaration rather than an off switch:

- **It lives in a commit message**, so it applies to exactly that commit and
  cannot be left on by accident. There is no file to forget to revert.
- **It is per path.** Declaring one page and changing the wording of another
  still fails — that is the accident being guarded against, and it is the
  property a blanket flag would not have.
- **It is in `git log` forever**, so the record of every deliberate wording
  change is the history itself.

Trailers are collected across the whole range, not one commit, because the case
that matters is a **merge**: CI compares the merge commit against `main`'s
previous tip, and the declarations sit on the commits being merged. A
declaration for a file that did not move is reported, never failed — a commit
message cannot be amended once pushed, so a stale trailer must not wedge the
workflow.

Five behaviours tested on throwaway branches. Two first came back green for the
wrong reason — one edit landed in an `alt` attribute, which is not visible text,
and one merged a branch holding a deliberately-bad commit. **Both were harness
bugs**, and both are why the harness now asserts that every edit applied.

### Three counts checked before Wave 2, and only two were wrong

Checked because Wave 2 will be built on numbers written during the audit, and
PH10-061's lesson is that a written count goes stale invisibly. **One of the
three I suspected was not wrong at all**, which is worth as much as the two
that were.

**1. The unreferenced diagrams were never 11.** `asset_census.py` section 6
reports **10**. Applying the same rule at `91e5d53`, the commit that wrote the
"11", also gives **10** — so this is an error at the time of writing, not
drift. The 10 are `comparative-advantage`, `consumer-producer-surplus-`
`{competitive,monopoly}`, `game-theory`, `lras-classical-keynesian-ad-shift`,
`lras-{classical,keynesian}-shift`, `supply-of-labour` and
`trade-union-{competitive,monopsony}`, 608 KB in total.

**2. "78 SVG/PNG pairs" is correct and is not a drift.** There are **83** SVGs,
of which **78 have a same-named PNG** — exactly what PH11 §5.1 claims. The
other **5 have no PNG at all**: `exchange-rate-{appreciation,depreciation}`,
`indirect-tax-{elastic,inelastic}-demand`, `lras-shift-keynesian`. That matters
for 5.1, whose method is "verify each SVG against its ground-truth PNG" — for
those five there is nothing to verify against, and 5.1 needs a different answer
for them. **PH11 was right; the suspicion was wrong.**

**3. The inline-style figure is stale, but not for the reason it looked.**
PH11 §2's Wave 2 row says "333 authored inline `style=` → classes across 45
files". Re-measured today with PH08-042's own method — which reproduces its
1,187 KaTeX count exactly, so the method is right — it is **322 across 44
files**. The missing 11 are `templates/footer.html`, which PH08-042 identified
as the 45th file, and which **Wave 0.6 already converted** in `be92eb2`. So the
row would send Wave 2 after work that is done. D18's "44 hand-written pages"
now matches the current count by coincidence rather than by measurement: it is
a different set of 44.

**A tooling note found doing this.** `asset_census.py` cannot be run inside a
linked `git worktree`. It locates the repo root by walking up for a `.git`
**directory**, and a linked worktree has a `.git` **file**, so it walks past the
worktree and chdirs somewhere with no site HTML — reporting 0 of everything
rather than failing. That is D30's breakage in a new place. `verify_generated.py`
does use a worktree, but the generators find their root from `__file__` and are
unaffected.

### 5.5 is closed

Eliot confirmed on 2026-08-11 that the two `Regulation` glossary definitions are
settled. `Regulation` is defined on the Edexcel page (PH10-063, in the Wave 0
table above), `check_glossary_capitalisation.py --check` is the 13th step of the
workflow and green, and no definition is unclassified. **Wave 5 is now 5.1–5.4.**

### A verifier for the defect 4.1 found by hand

`scripts/verify_image_dimensions.py`, 18th step in the workflow. Nothing
compared an `<img>`'s declared dimensions with the file's real ones, which is
how `macroeconomics-diagrams.html` shipped a box 35% too short. Pure stdlib —
it reads the PNG, JPEG, GIF, WEBP and SVG headers itself. Both failure modes
tested by breaking them. **3 root photographs** gained dimensions in the same
commit, because a check that is red on its first run gets ignored.

### The nav, after Flashcards made it nine items

Not a roadmap item — raised by Eliot on 2026-08-10. Nine top-level items need
**1045px** for one line; below that the nav wrapped, worst at 1000–1024 where
eight sat on the first row and **"Contact" was orphaned** on the second. That is
the half-screen width of a 1920 display.

**44% of the nav's 1018px was horizontal padding and margin** — 19.2px each side
of every link plus 5.6px of margin, against 571px of text. One compact tier
below 1100px (padding `0.5em`, margin `0.15em`, type `0.875em`) fits all nine on
one line from **768px up**. Vertical padding is untouched, so the link height and
tap target are unchanged, and ≥1100px is byte-identical CSS.

Two alternatives were measured and rejected: raising the hamburger breakpoint to
~1100 hides the nav from laptop users **and** drags all 18 of 4.5's breakpoints
with it; tightening spacing without the type change only relocated the orphan
from 1000–1024 to 850.

---

### Wave 2 done, 2026-08-11, except Phases 4 and 7

**Six phases in sixteen commits. The `<head>` now exists once, in
`scripts/page_shell.py`, for 446 of the 463 pages.**

| Phase | What | Result |
| --- | --- | --- |
| 0 | `compare_trees.py`, ten assertions | 32 self-test cases, each assertion broken on purpose |
| 1 | `verify_page_shell.py` | 8 checks, 20th workflow step, 17 failure modes tested |
| 2 | `page_shell.py` + `boards.json` + `verify_boards.py` | wired into nothing; 25 board assertions |
| 3 | pilot: 7 notes hubs | all ten assertions; 7/7 at D33's criterion |
| 5 | 166 notes topic pages, six sub-phases | **192 deletions, 0 insertions, 0 words of prose** |
| 6 | all four existing generators absorbed | 273 pages; the `<head>` exists once |
| 4 | root pages | **declined, D34** |
| 7 | bake header/footer | **not started; unblocks 4.10** |

Phase 5, sub-phase by sub-phase — every change a blank line:

```
edexcel-theme-3   20 pages    0 lines      aqa-a2-macro   25 pages   48 deletions
edexcel-theme-4   21 pages    5 deletions  aqa-a2-micro   54 pages  108 deletions
edexcel-theme-1   22 pages   15 deletions
edexcel-theme-2   24 pages   16 deletions  166 pages, 192 deletions, 0 insertions
```

Phase 6, one commit per generator: flashcards 7 pages / 21 deletions, glossary 3
/ 9, past-paper-questions 90 / 90, questions 173 / **6,747 insertions and 2,074
deletions**. That last one is the only absorbed generator that never ran
Prettier, so `page_shell`'s 80-column wrapping rewrapped every long tag: 173/173
still identical at D33's criterion, +0.24% bytes, and gzip removes it on the
wire. It was taken deliberately rather than leaving 37% of the site outside the
shared `<head>`.

**Assertion 2 reported 0 differing files across all 465 on every one of the
eleven migration runs.** `verify_text_integrity.py` agrees: 0 across 192 pages,
every commit.

#### Four numbers the roadmap got wrong, and one I got wrong myself

1. **PH11's `loading="lazy"` row is "33 pages / 94 images".** Measured: 96
   images across **96** pages, one each, and on all 96 the one lacking it is the
   **first image on the page**. Zero pages depart from it. It is not drift with
   stragglers, it is a convention held 96 times out of 96 — `d7bba50` added
   `loading="lazy"` to the *second* image of a two-image page and left the first,
   because a lazy first image delays the LCP candidate. **Applying that row as
   written would reverse it on 96 pages.** `verify_page_shell.py` check 7 now
   asserts the convention.
2. **PH06 section 1.1 names only 15 of the 18 self-disagreeing pages.**
   `contact.html`, `faq.html` and `marking.html` are missing from its list, and
   one of the 18 is `twitter:description` rather than `og:description`. The
   count was right; the list was short.
3. **PH08-039 counted the MathJax `<script>` tag's `id` and never looked at the
   config beneath it.** There are **three** distinct config bodies across the 126
   pages that load it — 89 / 18 / 19. Variant 2, on 19 pages, is not cosmetic:
   it drops `processEscapes`, `autoload` **and** `options.skipHtmlTags`, so those
   19 pages let MathJax typeset inside `<pre>`, `<style>` and `<textarea>`.
   Normalising the tag is smaller than the work.
4. **PH11's "111 board literals" is 113, in 11 scripts.** Close enough to act on;
   recorded so the next count starts from a measured figure.
5. **Mine: Phase 2 reported `L1 = 0/190` and I drew a conclusion from it.** The 0
   was a bug in my own selftest — see D33's correction. The real figure is
   61/190, so byte-identical migration *is* reachable for a third of the corpus.
   The Prettier measurement underneath it was independent and stands.

#### Wave 3.1 landed with Wave 2

`boards-data/boards.json` + `scripts/verify_boards.py`, 25 assertions against all
four hardcoded structures, in the workflow. **Nothing imports it yet** — that is
PH09's migration step 1, deliberately. Measuring it turned up something PH09 did
not anticipate: **group names need the same per-consumer treatment as slugs**,
because Theme 2 reaches published output as three different strings. See
DO-NOT-BREAK.

---

### Wave 2 Phase 7 done, 2026-08-11. Wave 2 is complete

**The nav is in the source of all 463 pages.** Six commits. `inject-templates.js`
fetched `templates/header.html` and `templates/footer.html` at page load and
swapped them into two placeholder divs; they are baked in at build time now.

| Commit | What |
| --- | --- |
| 1/6 | tooling and the nav script tolerate both forms. No page changed |
| 2/6 | the five generators bake. **446** pages |
| 3/6 | `bake_templates.py` syncs the **17** no generator owns; check 9 pins all 463 |
| 4/6 | the fetch, the highlight and the placeholder's CLS reservation deleted |
| 5/6 | the rename to `nav.js` measured and declined |
| 6/6 | documents, and the corrections below |

**Both of the two things the brief said to check first were wrong.**

1. **It is 446 generated and 17 not, never 454 and 9.** The "454" is `463 − 9`,
   taken from D34's decision about the root pages rather than measured, and it
   was in D34, CLAUDE.md, DO-NOT-BREAK.md and four places here. The uncounted 8
   are the 5 `past-papers/` hubs — PH06 planned them as the Phase 3 pilot and
   the notes hubs were migrated instead — and the 3 `revision-notes/` non-topic
   pages, which D34 explicitly left undecided. The build confirms it unprompted:
   446 baked, 17 published pages still holding a placeholder.
2. **`inject-templates.js` did not leave, so check 2 did not change.** Counting
   `$(` per function before touching anything: 9 of its 11 jQuery calls are in
   `initNavigation()`, 2 are the bootstrap, and `injectTemplates()` and
   `setActivePage()` used **zero** — both were already `fetch`,
   `getElementById`, `querySelector` and `classList`. So **PH08-043 is wrong on
   detail**: removing the fetch removed no jQuery consumer. The file went 209
   lines to 121 and still needs jQuery. Check 2 is neither weakened nor updated;
   **check 9 is what proves the phase reached every page**, and it is stronger —
   the whole nav block, byte-identical to the template, on 463 of 463.

**A third wrong number, this one in a verifier's own output.**
`verify_page_shell.py` has printed "463 published pages, 190 of them
hand-written" on every CI run since Phases 3 and 5 made the notes pages
generated. It is 17, and it is now the same 17 `bake_templates.py` owns.

**What it bought.** The nav exists without JavaScript for the first time.
CLS measured in headless Chrome over a threaded server, four page types, two
viewports, the same PerformanceObserver probe injected into both sides:

```
1400px   index    0.0253 -> 0.0037      390px   index    0.0220 -> 0.0018
         tutoring 0.0223 -> 0.0034              tutoring 0.0388 -> 0.0181
         ocr      0.0224 -> 0.0022              ocr      0.0246 -> 0.0056
         notes    0.0234 -> 0.0021              notes    0.0028 -> 0.0026
```

Three repeats of the notes page at 1400px give **before** 0.0241, 0.0024, 0.0240
and **after** 0.0032, 0.0021, 0.0027 — the before figure is bimodal because it
depended on whether the two fetches beat first paint. **Baking removed a race,
not a constant**, which is the more useful way to say it. Lab numbers; CrUX is
the real one.

**What it cost.** Median **+1,217 bytes gzipped per page**, +23.5%, 654 KiB
sitewide, measured across all 463 before starting. And a nav edit is now a
rebuild — D18's trade, re-confirmed by Eliot when it was put concretely.

**The gate, and why assertion 2 needed re-pointing rather than relaxing.**
Baking changes the visible text of every page's *source* while changing nothing
a reader sees, so `compare_trees.py` assertion 2 and `verify_text_integrity.py`
would both have gone red on all 463 by design. Weakening either was the wrong
answer. Instead the comparison is re-pointed at **OLD-spliced** — OLD with the
templates pasted in at the placeholders, which is byte-for-byte what
`outerHTML = data` builds in the browser — by
`docs/audit/scripts/harness/splice_baseline.py`, deliberately a *second*
implementation so a bug in `bake()` cannot cancel itself out. Checked against
OLD it reports 463 of 465 files differing, which is the proof it can return
something other than zero. All ten assertions then passed on both page commits.

**Three checks the bake walked into, all fixed rather than relaxed.**

- **`verify_seo` assertion 13, "no link crosses an exam board", went to 3,887
  failures.** The nav offers every board from every page and always has — at
  runtime, where the check could not see it. Baking made a menu look like
  content links. `link_graph.Graph.chrome` now records which edges came from the
  baked block and 13 skips them; the static/rendered distinction the graph
  reports is untouched, because the two converging is the point of the phase.
- **`verify_glossary` check 3** renders in memory and compares; it bakes the
  expectation now.
- **`verify_markup_integrity --strict`** reported `<div>` 366 → 365 on the three
  glossary pages and was right: two placeholder divs out, the footer's one
  container div in. It resolves placeholders before profiling now, the same
  treatment `verify_text_integrity` got.

Each of the three, and check 9, was proved still able to fail by breaking it.

**Verified by rendering, not only by asserting.** `4421f26` and the finished
branch served side by side and rendered in headless Chrome: every href in the
desktop nav and the mobile panel, the nav's visible text, which item carries
`current`, the `#titleBar`, and every footer link — identical on all 10 pages
tested, covering every page type. The comparison was then proved capable of
failing by retyping one nav label.

**Left alone deliberately:** `_working/flashcards/qa/`'s QA pages keep their
placeholders and now show an empty div where the header was. They are
unpublished frozen records; baking them would create copies of the nav that
check 9 does not cover.

---

### Wave 4.10 done, 2026-08-11. jQuery and dropotron are gone

**188 KB of source and 45,891 gzipped bytes per page, removed from all 463.**
Four commits.

| Commit | What |
| --- | --- |
| 1/4 | `render_nav.py` — the nav rendered in a browser and compared. No site file |
| 2/4 | the script tail declared once, in `page_shell.SCRIPT_TAIL`. No output moved |
| 3/4 | jQuery, dropotron and `util.js` deleted; `inject-templates.js` → `nav.js` |
| 4/4 | the nav bar redesigned — presentation only, no page rebuilt |

```
js/jquery.min.js             168,019 B   40,276 gzipped   deleted
js/jquery.dropotron.min.js    10,964 B    2,368           deleted
js/util.js                    12,942 B    3,247           deleted
js/components/nav.js                      3,197           new
css/main.css                  +8,180 B   +2,846           the CSS replacement
                                        ---------
                            NET per page  -43,265 B gzipped
```

**Three more numbers in the roadmap were wrong.** The pattern holds.

1. **`inject-templates.js` was 141 lines, not 121.** 121 is what is left after
   its own 20-line header comment. Both D35 and the brief repeated it.
2. **PH08-043 lists `util.js` as a jQuery consumer with 22 calls**, which is
   true and misleading. Of its four exports only `navList()` had a caller
   anywhere on the site; `panel()`, `placeholder()` and `$.prioritize` had
   **zero**. 349 of 490 lines were dead, and the live part is about 30 lines.
   Deleting the file was cheaper than porting it, and Eliot chose that.
3. **`breakpoints.min.js` has one call site and `browser.min.js` has zero.**
   Both are jQuery-free, so neither was in 4.10's scope; both are dead weight
   (2,141 B gzipped per page) and are logged in `REVIEW-NOTES.md`.

**And one nobody had measured at all: dropotron was duplicating the navigation
into every page.** It built 11 `.dropotron` menus at page load, and the
document's `<a>` count falls 118 → 95 with no link lost — **23 duplicated
anchors and 23 duplicated list items on every one of 463 pages**, in front of
every crawler. It is the most useful thing the render harness found and no
bytes-based check could have seen it.

**The dropdowns are CSS now, and work with scripting off.** The submenus were
always in `templates/header.html`; nothing in the markup changed. `nav.js` adds
only tap-to-open and Escape, as a class on top of `:hover` and
`:focus-within`, so switching the file off leaves working dropdowns.

**What the assertions said, and why three of them failing is the report.**
Assertions 1, 4 and 8 fail — the three D35 predicted for the rename, now also
carrying three deletions. Each was decomposed rather than asserted benign:

- **4**: 2,315 losses = 463 × 4 removed `src`s + 463 `<script>` counts down by
  exactly 3. **Zero** unexpected lines.
- **8**: 474 files differ = **463 HTML differing only in `<script src>` lines**,
  plus `css/main.css`, `js/main.js` and nine unpublished scripts.
- **1**: 4 assets removed, 1 added. The intended swap.

**Rendered, not only asserted.** 10 pages × 2 viewports plus the three
dropdowns, `4421f26`-style: `nav`, `panel`, `navCurrent`, `navDisplay`,
`titleBar`, `panelAttrs`, `skipLink`, `footer` **and `interact`** identical on
23 of 23 captures; only `counts` differs, by exactly −23 `<a>`, −23 `<li>`, −3
`<script>` everywhere. `interact` covers what no assertion can: each dropdown
opened and its visible links recorded, and on mobile the toggle, Escape with
focus returning to the button, click-outside and swipe-left, with the panel's
computed transform moving −275px ↔ 0 on every cycle. The comparison was proved
able to fail by retyping one nav label, and three consecutive captures of
`main` are byte-identical.

**Four measurement bugs, all found by insisting a zero can be non-zero.**

- **The CLS probe reported 0.0000 for a deliberate 200px layout shift.** Chrome's
  animation clock does not advance under `--virtual-time-budget`, so no
  `layout-shift` entry is ever generated — and without virtual time the probe's
  result lands after `--dump-dom` has dumped. Rebuilt to POST back to the
  server; it reports 0.1444 for the same shift, which is what makes the real
  zeros worth anything.
- **`getComputedStyle` reported the panel at `translateX(-275px)` open and shut
  alike**, and `getBoundingClientRect().left` reported −275 in both states, for
  the same reason. The probe disables transitions before interacting.
- **dropotron answers only the FIRST synthetic hover of a page.** A loop over
  the three openers reported "no dropdown" for two of them; it would have passed
  by being blind.
- **`subprocess.run()` cannot drive Chrome.** It writes the DOM and does not
  exit, because its updater children inherit the stdout pipe — intermittently,
  after four successful captures.

**What moved, and what did not.** Script bytes per page 205.3 KB → 22.3 KB.
Under a Slow 4G transfer model (1.6 Mbit/s, 150 ms RTT, applied identically to
both trees) DOMContentLoaded falls **693–836 ms** on all four page types at both
viewports. **On localhost nothing moves at all** — FCP, DCL and load all inside
run-to-run noise, because the scripts sit at the end of `<body>` and there is no
wire to save. **CLS was 0.0000 before and after**: Phase 7 had already taken it
there. **FCP is about 20 ms worse**, entirely because `css/main.css` grew; the
+68 ms first seen was the 8 KB chunk quantisation of the throttle, and 1 KB
chunks give +20 ms against the 18.7 ms the byte growth predicts.

**Two verifiers were taught rather than relaxed.** `verify_page_shell` check 2
keeps its independent literal and gained a second assertion — 0 of 463 pages
load a removed script — because the ordering test filters to tail members and a
page that kept jQuery would have sailed through it. `verify_markup_integrity
--strict` reported 895 true losses and now skips `<script src>` tags, on the
ground that check 2 makes a strictly stronger statement about the same bytes;
proved still able to fail by deleting one `<a>` from inside a notes body.

**Check 2 also caught the one incidental change.** `index.html` put its two
review scripts between `util.js` and `main.js`; `util.js` is gone and the tail
is re-emitted before a page's own scripts, so they follow `main.js` now.
`EXPECTED_INTERLEAVED` went `["index.html"]` → `[]`, declared in the same
commit.

**The redesign, commit 4/4.** Eliot: *"You also have licence to improve the nav
bar so that changes encompass the entire nav bar, not just the dropdowns."*
Presentation only — no label, href or structure moved, `templates/header.html`
untouched, check 9 unmoved, no page rebuilt. Upright rather than italic; one
accent language for hover, focus and open where a grey box and a red pill
shared nothing; a chevron on the three items that open a submenu, drawn in CSS
because the Font Awesome subset would otherwise need re-running; a light
dropdown card instead of the theme's near-black slab; 44px rows instead of 28.
The rendered comparison against 3/4 shows **`panel` as the only field that
differs, on 23 of 23, and the difference is one link gaining `current`** — the
right one every time.

**The one genuinely new behaviour: the mobile panel now says where you are.**
The desktop bar has had a highlight since the beginning and the phone had
nothing. `nav.js` copies the class off the baked `<li class="current">` rather
than re-deriving it from the URL, so the two navigations cannot disagree.

**The sitemap did not need regenerating, and that is luck rather than a
property.** Every `lastmod` is a date, Phase 7 landed on 2026-08-11 and so did
this; `build_sitemap.py --check` exits 0 with 0 `WOULD CHANGE`. Work continuing
past midnight will need it.

---

# HANDOVER — 2026-08-11. WAVE 4.10 IS COMPLETE AND UNMERGED

**Waves 0, 1, 2, 4 are complete, Wave 3.1 is done, and Wave 4.10 is done on the
branch `wave4-10`** — four commits off `58281ce`, **not pushed and not merged**.
Everything before it is merged and live.

```
687b9e8 wave4.10(4/n): redesign the nav bar, not only the dropdowns
198c6b0 wave4.10(3/n): jQuery, dropotron and util.js leave all 463 pages
488769a wave4.10(2/n): the script tail is declared once. No output moves
70e00cd wave4.10(1/n): render the nav in a browser, because the assertions cannot
```

## What a fresh session needs to know

1. **Read `DO-NOT-BREAK.md` first.** It gained a whole "The navigation, without
   jQuery" block on 2026-08-11 — what `nav.js` may and may not take over from
   CSS, why check 2 does not import the constant it checks, and four things
   about driving headless Chrome that cost hours each.
2. **`DECISIONS.md` is D1–D36.** D36 is this wave.
3. **The workflow is 21 steps** and all 21 are green on `687b9e8`.
4. **The script tail is four scripts** and is declared in
   `page_shell.SCRIPT_TAIL`. `verify_page_shell.SCRIPT_TAIL` restates it
   independently on purpose; `bake_templates.LEGACY_TAIL` is how the 17
   hand-written pages lose a script the other 446 have already lost.
5. **`render_nav.py` is the gate for anything touching the nav**, and
   `compare_trees.py` cannot replace it: the mobile panel exists in no file.
6. **The roadmap is reliable on direction and unreliable on detail.** Wave 2
   found five wrong numbers, Phase 7 three, this wave three more plus one
   nobody had measured. Re-derive, and say so when an item is wrong.

## Open, not started

**Runnable now**

- **Wave 3.2 and 3.3** — repoint the **113** board literals in 11 scripts at
  `boards.json`, one generator per commit with output proved unmoved, then key
  everything on `(board, spec)`. **3.4 is blocked** until the GSC re-measure.
- **Remove `browser.min.js` and `breakpoints.min.js`**, 2,141 B gzipped per
  page. Zero and one call sites respectively; `REVIEW-NOTES.md` has the
  measurement. It is a tail change, so it is the same four-file edit 4.10 made.
- **`inert` on the closed `#navPanel`**, dropping `aria-hidden`. A real
  conformance failure, pre-dating 4.10, deliberately not folded into it —
  `REVIEW-NOTES.md`.
- **Wave 5.1–5.4** — content and editorial, each needing explicit approval.
- **Move `compare_trees.py` into `scripts/`** and add it to the workflow, per
  PH06 section 3. `render_nav.py` needs Chrome, so it stays out.

**Deliberate normalisations, each its own commit**

`aria-label="Breadcrumb"` (341), `<main id="main">` keeping the id (462), the
three MathJax config variants (89/19/18 — the 19 drop `skipHtmlTags`, so it is
not cosmetic), the two preconnect lineages (190 after `<title>`, 273 before).

**Decisions for Eliot, not tasks**

- **`logo/` and `old-logos-archive/`** — 31 tracked files, published, 0
  references, 0 GSC rows. UNDECIDED since 2026-08-09.
- **The 10 unreferenced diagrams**, 608 KB.
- **PH06-031's three malformed notes pages.**

**Blocked until ≈2026-09-22, the day-45 GSC re-measure**

4.7, 4.8, Wave 3.4, PH05-019/020/021 and PH03-049 step 2.

## One stale line found in passing, not this wave's to fix

`DO-NOT-BREAK.md`'s `verify_liquid.py` note says the script "deliberately
fails" if it has 0 files to check. `79f75de` moved the last published markdown
to `raw-notes/`, so it now checks 0 files, exits 0, and prints a justification
naming `verify_published_surface.py` as what makes that a real pass. The
script is right and the register's paragraph is stale.
