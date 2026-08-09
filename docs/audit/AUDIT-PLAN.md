# Audit plan

Agreed 2026-08-08. Phase 0 complete; P1 next.

Working rules, unchanged from the brief: **read-only on the site**, no
opportunistic fixes, no guessing (evidence or UNKNOWN), URLs frozen by default,
static-only recommendations. One phase at a time, check in at the end of each.

---

## Changes made to the original scaffold, and why

| Change | Reason |
| --- | --- |
| **P2 merged into P1** | There is no router — URL architecture *is* file structure here. Phase 0 already cleared sitemap, canonicals, robots and 404 handling. What remains (four URL grammars, three board spellings) belongs beside the file-layout discussion, not in its own phase |
| **P3 halved** | The raw-vs-rendered link graph, orphan detection and broken-link check are done and clean (`docs/audit/scripts/link_graph.py`). Remaining scope is click depth, anchor-text distribution and hub/spoke integrity |
| **P4 slimmed** | Titles, descriptions, canonicals, `og:url`, `lang`, robots and sitemap are all verified clean. Only structured-data validity and the `EducationalOrganization` gap survive |
| **P8 renamed** to "Front-end assets, semantics & accessibility" | The scaffold has no accessibility phase at all, and 52 pages already violate the repo's own inline-style rule |
| **`DO-NOT-BREAK.md` moved from P11 to Phase 0**, appended to continuously | A protection register written at the end protects nothing during the audit |
| **New P9b, "Generation coverage & drift"** | Distinct from the data-model question: how much of the 463 is generated, and does re-running every generator today still produce byte-identical output. Several generators claim idempotence; nobody has checked recently |
| P5, P6, P7, P10, P11 kept as briefed | Sound as written |

**Order:** P1 → P5 → P9 → P9b → P6 → P8 → P3 → P4 → P7 → P10 → P11.

P5/P9/P9b run before P6 because P6's proposal depends on knowing what is already
generated and how the two boards' pages actually differ. P3/P4 run late because
they are small and confirmatory rather than exploratory.

---

## Phases

### P1 — Repo, file structure & URL architecture

**Audits.** Folder logic and naming; the four URL grammars (PH00-002); board-slug
encoding (PH00-003); unreferenced and dead published assets (PH00-005); duplicate
and near-duplicate files; `.gitignore` hygiene; the 176 MB `.git` and 284 PDFs;
14 merged branches (PH00-010); the six overlapping root progress documents.

**Good looks like.** One written rule per structural decision, and a URL-shape
rule for the next page family that requires changing nothing existing.

**Method.** Scripted census + `git log` on each anomaly to recover intent.

**Context cost.** Low. **Own session:** no.

### P5 — Board-variant duplication

**Audits.** Normalised text similarity across 91 Edexcel × 81 AQA topic pages.
For pairs above ~0.80: whether title, H1, meta description, spec reference,
internal links and structured data are genuinely board-differentiated.

**Good looks like.** A similarity distribution with a stated threshold and
per-pair differentiation evidence. **Not** a cross-board canonical recommendation
— the owner wants both boards ranking for board-specific queries, and the
evidence bar for claiming cannibalisation is GSC data showing two of the site's
own URLs competing on one query, not similarity alone.

**Method.** Extract body text (strip nav, head, scripts), shingled Jaccard,
scripted. Cross-check the top pairs by hand.

**Context cost.** Medium. **Own session:** borderline — run directly after P1.

### P9 — Data layer & content model

**Audits.** Schema consistency across the four JSON families;
single-source-of-truth violations; ID and slug strategy; the board-identity
problem from PH00-003; a written "how would I add OCR notes today" walkthrough
against "how it should work".

**Good looks like.** One canonical board identity as data, and a documented
answer to "what do I create, in what order, to add a topic or a board".

**Context cost.** Medium. **Own session:** no.

### P9b — Generation coverage & drift

**Audits.** Which of the 463 pages are script-generated vs hand-maintained, and
whether every generator is still byte-idempotent today.

**Good looks like.** A clean idempotence run, or a named list of generators whose
output has drifted from their source.

**Method.** Generate into a temporary tree and diff. **Never over the working
tree** — that would violate read-only and could destroy hand-edits that have not
yet been identified as such.

**Context cost.** Medium. **Own session:** no.

### P6 — HTML page architecture & generation · HIGHEST PRIORITY · OWN SESSION

**Audits.** The 463 duplicated `<head>` blocks (PH00-004); how much of each body
is boilerplate; what a template layer could be given no build step; whether
Jekyll front matter + `_includes` is viable (it changes no URL); the cost and
staging of any move.

**Good looks like.** A costed, staged proposal that changes zero URLs, keeps
output byte-comparable, and can be abandoned halfway without leaving the site
inconsistent.

**Context cost.** High. **Own session:** yes. Do not start without checking in.

### P8 — Front-end assets, semantics & accessibility

**Audits.** 19 `css/pages/*.css` against 463 pages; dead CSS and JS; the 52
inline-`style` pages and 9 `<style>` blocks (PH00-008); render-blocking order;
198 images (format, dimensions, alt text, lazy loading); fonts; heading
hierarchy; ARIA; the injection fallback gap (PH00-006); GA4 consistency.

**Good looks like.** Every rule scoped under its page wrapper per the house
convention; no unreferenced stylesheet; alt text present and meaningful on every
content image.

**Context cost.** Medium-High. **Own session:** likely.

### P3 — Internal linking & crawl depth

**Audits.** BFS click depth from `/` on the raw graph; anchor-text distribution
(the ppq topic-chip monoculture — 68 links reading `2.6.2 Demand-side Policies`);
hub/spoke integrity; fragment targets; PH00-001.

**Good looks like.** Nothing important beyond depth 3; no anchor string used more
than ~50 times; every hub links to all its children and vice versa.

**Context cost.** Low — reuses `docs/audit/scripts/link_graph.py`. **Own session:** no.

### P4 — Structured data validity

**Audits.** Every JSON-LD block parses; required properties present per type;
`@type` choices defensible; PH00-007.

**Good looks like.** Every emitted type validates, and every page in a family
emits the same set.

**Context cost.** Low-Medium. **Own session:** no.

### P7 — Information architecture & UX

**Audits.** Taxonomy and label consistency across boards and resource types; nav
structure; click depth to key tasks; search and filter usability; mobile;
conversion paths to tutoring and marking; print styles.

**Context cost.** Medium. **Own session:** no.

### P10 — Tooling, automation & governance

**Audits.** 25 `scripts/` + 11 unique `seo/tools/`; which checks are automatable;
GitHub Actions feasibility given the site has no CI at all; pre-commit hooks; the
quality of `CLAUDE.md`; the six overlapping progress documents.

**Good looks like.** A named set of checks that could run on every push without
risking the deploy, and one conventions document that replaces the parts of six.

**Context cost.** Medium. **Own session:** no.

### P11 — Synthesis

Prioritised roadmap (impact × effort × risk), sequencing and dependencies,
`DO-NOT-BREAK.md` finalised, rollback plan for anything URL-affecting.

**Context cost.** Low. **Own session:** no.

---

## Verification that the audit changed nothing

Before and after. Output must be identical; any difference means a rule was
broken.

```
python3 scripts/verify_html.py
python3 scripts/verify_links.py
python3 scripts/verify_text_integrity.py
python3 scripts/verify_markup_integrity.py
python3 scripts/verify_liquid.py
python3 scripts/verify_glossary.py
python3 seo/tools/verify_seo.py
```

Plus: `git status --porcelain` on the site tree stays empty, and
~~`git check-ignore -v _audit/PROGRESS.md` keeps reporting a match.~~
**Superseded 2026-08-09 by D30:** the audit is committed at `docs/audit/` and is
no longer gitignored. The equivalent check is
`python3 scripts/build_sitemap.py --check` reporting "nothing written", which
proves `docs/` in `_config.yml`'s `exclude` is still withholding it.
