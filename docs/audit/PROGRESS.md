# Audit progress

**Read this plus `AUDIT-PLAN.md` and you can resume with zero prior context.**
Nothing below needs the site re-crawled — the scripts in `docs/audit/scripts/`
reproduce every figure in seconds.

Last updated: **2026-08-09**. **THE AUDIT IS COMPLETE.**

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

`verify_liquid.py` failing is the **expected** state today. If it ever reports 0,
someone has changed something; if it reports 2, look at what was added.

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
