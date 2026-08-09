# 00 — Inventory

Phase 0. Compiled 2026-08-08 on branch `audit/organisation-audit`, cut from
`main` at `8c8034b`. Every figure below is reproducible from the scripts in
`docs/audit/scripts/` or the commands quoted inline.

---

## 1. What the repo is

| | |
| --- | --- |
| Tracked files | 1,555 |
| Working tree | 512 MB (`.git` 176 MB of it) |
| Published HTML pages | 463 (excludes `templates/`, `_working/`) |
| PDFs | 284 tracked, 283 published + 1 under `_working/` |
| Images | 198 tracked |
| Build step | **None.** No `package.json`, `Gemfile`, `.github/`, CI, or hooks |
| Host | GitHub Pages, custom domain via `CNAME` → `economicsacademy.co.uk` |
| Jekyll | **Default build, active.** No `.nojekyll` — deliberate |

File counts by extension, `git ls-files`:

```
480 html   284 pdf    270 json   162 png    116 md     89 svg
 41 py      23 woff2   22 css     16 js      16 csv     8 xml
```

### The build step, stated plainly

There is no build step. `_config.yml` is not a build configuration in the usual
sense: it contains an `exclude:` list and nothing else. No page carries front
matter, so Jekyll copies every `.html` verbatim. All generation is manual —
`python3 scripts/build_*.py`, run by hand, output committed.

**`exclude` replaces Jekyll's defaults rather than adding to them.** The defaults
are restated in the file for that reason; deleting a line makes that path public.
It currently withholds `scripts/`, `docs/`, `seo/`, `raw-notes/`, the four
`*-data/` directories, and the root markdown. Directories beginning with `_` are
skipped by Jekyll's own rule, which is what makes `_working/` and `_audit/` safe.

**Adding `.nojekyll` would immediately publish every `_` directory** and disable
`exclude` entirely. It must not be added.

---

## 2. Header/footer injection — the exact mechanism

[`js/components/inject-templates.js:116-140`](../js/components/inject-templates.js#L116-L140):

```js
function injectTemplates() {
  fetch("/templates/header.html")
    .then((response) => response.text())
    .then((data) => {
      document.getElementById("header-placeholder").outerHTML = data;
      setActivePage();
      setTimeout(initNavigation, 50);
    })
    .catch((error) => { console.error("Error loading header:", error); });

  fetch("/templates/footer.html")
    .then((response) => response.text())
    .then((data) => {
      document.getElementById("footer-placeholder").outerHTML = data;
    })
    .catch((error) => { console.error("Error loading footer:", error); });
}
```

Fired from a jQuery ready handler (`$(function () { injectTemplates(); })`,
line 189). **`fetch` + `outerHTML` replacement.** Not `document.write`, not a web
component, not a custom element.

Answers to the specific questions asked:

| Question | Answer |
| --- | --- |
| Mechanism | `fetch()` → `.text()` → `element.outerHTML = data` |
| Nav/footer links in raw HTML? | **No.** The source contains only `<div id="header-placeholder"></div>` and `<div id="footer-placeholder"></div>`. All 463 pages, 0 exceptions |
| Recent internal-linking work inside the injected templates? | **No — see §3. Not the CRITICAL case.** |
| Breadcrumb markup injected? | **No.** Static in the source: 441 pages carry a visible `class="breadcrumb…"` nav |
| JSON-LD injected? | **No.** Static: 460 of 463 pages carry `BreadcrumbList` in the source |
| Fetch failure | **No fallback.** `console.error` only, no `<noscript>` nav. A 404 or hang on `/templates/header.html` leaves every page with no navigation and no footer |
| Layout shift | **Handled.** [`css/main.css:210`](../css/main.css#L210) reserves `min-height: 240px`, reduced to `120px` under 767 px |

`setActivePage()` (line 143) highlights the nav item by path prefix, which is why
a new page under an existing section needs no nav rule and `/flashcards/` needed
its own line.

---

## 3. The raw-vs-rendered link graph

`python3 docs/audit/scripts/link_graph.py`. Computed twice: once over `<a href>` in
raw HTML as a non-rendering crawler sees it, once adding the two templates'
links as edges from all 463 pages.

```
published pages: 463
raw internal edges: 7,915
injected edges: 14,816
BROKEN internal targets: none
ORPHANS (zero raw inbound): 404.html, confirmation.html
  → 461 of 463 pages reachable without JavaScript
```

**The recent internal-linking work is in page bodies, not the templates.** The
diagram-gallery links added by `d1e7a3a` show 22 and 27 raw inbound links; the
practice→past-paper links from `17571f3` and the 13 re-pointed links from
`55dda8a` are all in generated page bodies. A non-rendering crawler sees them.
This is the good news, and it is the opposite of what the brief anticipated.

**What the injection does cost is equity distribution, not discovery.** Eleven
URLs draw ≥98% of their inbound links from the templates:

| raw | injected | inj% | url |
| ---: | ---: | ---: | --- |
| 1 | 463 | 99.8% | `/past-papers/edexcel-b/` |
| 1 | 463 | 99.8% | `/past-papers/ocr/` |
| 1 | 463 | 99.8% | `/privacy.html` |
| 2 | 463 | 99.6% | `/revision-notes/macro-application/` |
| 2 | 463 | 99.6% | `/faq.html` |
| 3 | 926 | 99.7% | `/contact.html` |
| 4 | 926 | 99.6% | `/about.html` |
| 6 | 463 | 98.7% | `/revision-notes/glossary/` |
| 6 | 463 | 98.7% | `/past-papers/` |
| 7 | 463 | 98.5% | `/flashcards/` |

The top two are the site's best-earning non-homepage URLs: 143 clicks and 11,971
impressions between them (`seo/performance-pages.csv`). See finding PH00-001.

---

## 4. Page families

| Family | Pages | URL shape | Generated by |
| --- | ---: | --- | --- |
| Revision notes — topic | 166 | `/revision-notes/<board-dir>/1-1-1-slug.html` | hand-written (some from `raw-notes/` via `convert_raw_notes.py`) |
| Revision notes — hub | 6 | `/revision-notes/<board-dir>/` | hand-written |
| Revision notes — other | 6 | `/revision-notes/{,macro-application/,*-diagrams.html}` | hand-written |
| Glossary | 3 | `/revision-notes/glossary/{,edexcel-a/,aqa/}` | `scripts/build_glossary.py` |
| Practice questions (MCQ) — topic | 166 | `/practice-questions/<board-dir>/1-1-1-slug.html` | `scripts/build_questions.py` |
| Practice questions — hub | 7 | `/practice-questions/<board-dir>/` | `scripts/build_questions.py` |
| Past-paper questions | 90 | `/past-paper-questions/<board>/<slug>/` | `scripts/build_past_paper_questions.py` |
| Past papers | 5 | `/past-papers/<board>/` | hand-written |
| Flashcards | 7 | `/flashcards/<board>/<theme>/` | `scripts/build_flashcards.py` |
| Root: commercial | 4 | `/{index,tutoring,marking,about}.html` | hand-written |
| Root: utility/legal | 5 | `/{contact,faq,privacy,confirmation,404}.html` | hand-written |
| **Total published** | **463** | | |

Revision-note topic pages by board directory: `aqa-a2-micro` 54, `aqa-a2-macro`
25, `edexcel-theme-2` 24, `edexcel-theme-1` 22, `edexcel-theme-4` 21,
`edexcel-theme-3` 20. Practice questions mirror this 1:1.

### Four incompatible URL shapes

```
/revision-notes/edexcel-theme-1/1-1-1-economics-as-a-social-science.html   flat .html
/practice-questions/edexcel-theme-1/1-1-1-economics-as-a-social-science.html   flat .html
/past-paper-questions/edexcel/1-2-2-demand/                               directory
/flashcards/edexcel-a/theme-1/                                            directory
/revision-notes/glossary/edexcel-a/                                       directory
```

Notes and MCQs share a shape; the three newer families each chose a directory
shape but a different path grammar. **URLs are frozen** — see finding PH00-002.

---

## 5. Data layer

| Source (excluded from publishing) | Files | Generator | Published output |
| --- | ---: | --- | --- |
| `questions-data/<board-dir>/*.json` | 166 | `build_questions.py` | 173 HTML pages, no JSON |
| `flashcards-data/<board>/*.json` | 6 | `build_flashcards.py` | 7 HTML + `flashcards/data/*.json` |
| `past-paper-questions-data/<board>/*.json` | 64 | `build_past_paper_questions.py` | 90 HTML + `questions.json` |
| `glossary-data/{terms,curation,authored}.json` | 3 | `build_glossary.py` | 3 HTML, no JSON |

Shapes are internally consistent within each family (verified: all 166
`questions-data` files share an identical top-level key set). They share **no**
common envelope across families:

```
questions-data      board boardDir boardName spec slug title shortTitle
                    pageTitle metaDescription intro notesTeaser questions
flashcards-data     board boardName theme themeName deckId deckTitle
                    metaDescription intro cards
ppq-data            qualification board boardName level paper paperName year
                    series seriesSlug questionPaperUrl markSchemeUrl
                    problems questions
glossary terms.json source site stats terms formulae
```

Hand-written, protected-from-regeneration side files: `tags.json`,
`curation.json`, `authored.json`. Generated: `taxonomy.json`, `terms.json`.

---

## 6. The exam-board dimension

Coverage is asymmetric, as expected — but the **encoding is not consistent**.

| Family | Edexcel A | Edexcel B | AQA | OCR |
| --- | --- | --- | --- | --- |
| Revision notes | `edexcel-theme-{1..4}` | — | `aqa-a2-{micro,macro}` | — |
| Practice questions | `edexcel-theme-{1..4}` | — | `aqa-a2-{micro,macro}` | — |
| Past-paper questions | `edexcel` | — | `aqa` | — |
| Flashcards | `edexcel-a` | — | `aqa` | — |
| Glossary | `edexcel-a` | — | `aqa` | — |
| Past papers | `edexcel` | `edexcel-b` | `aqa` | `ocr` |

**"Edexcel A" is spelled three ways** — `edexcel`, `edexcel-a`, and
`edexcel-theme-N` — across URLs, directory names and JSON `board` fields, and the
directory name does not always match the field inside it
(`past-paper-questions-data/edexcel-a/*.json` contains `"board": "edexcel"`).
See finding PH00-003.

AQA notes use **site-local** spec codes `1.x.y`/`2.x.y`, deliberately not the real
AQA 7136 codes. Ratified in CLAUDE.md — not a defect.

---

## 7. Metadata and indexation state

`python3 docs/audit/scripts/metadata_census.py`. This is the SEO pass's output and it
is clean:

```
pages: 463
missing <title>: 0          missing description: 0
missing canonical: 2        (404.html, confirmation.html — both noindex)
canonical != expected: 0    og:url != canonical: 0
duplicate titles: 0         duplicate descriptions: 0
lang: en-GB on 463/463      meta robots: noindex on 2, absent on 461
```

Sitemap: `sitemap.xml` is a `<sitemapindex>` over seven children totalling 744
URLs. Filesystem ⇄ sitemap diff is **0 in both directions** for HTML (the only
two absences are `404.html` and `confirmation.html`, correctly) and **0 phantom /
0 missing** for the 283 published PDFs.

`robots.txt`: `Allow: /` plus the sitemap line. No disallows.

Structured data, `@type` counts across 463 pages:

```
460 BreadcrumbList   354 EducationalOrganization   181 LearningResource
179 Course           166 Quiz                      105 CollectionPage
100 WebSite            3 DefinedTermSet              1 FAQPage
```

`CollegeOrUniversity` (2) is `alumniOf: University of Bath` — correct usage,
checked, not a defect.

---

## 8. Search Console exports

**Location:** `seo/gsc-exports/`, 8 CSVs. **Exported 2026-08-08**; crawl dates
inside them span 2026-05-12 → 2026-08-05. Committed in `a26f4f5`.

**Publicly served?** **No.** `seo/` is in the `exclude` list of `_config.yml`,
added by commit `d085317` for exactly this reason. No action needed — verified,
not assumed.

| Export | Rows | Verified against current files |
| --- | ---: | --- |
| `excluded-by-noindex-tag.csv` | 25 | **Resolved** `203f6bd`. 461 of 463 pages carry no meta robots |
| `alternate-page-with-proper-canonical-tag.csv` | 8 | **Resolved.** 0 canonical mismatches, 0 internal `index.html` links |
| `redirect-error.csv` | 1 | **Resolved.** `/past-paper-questions` 301s cleanly to the trailing-slash form |
| `not-found-404.csv` | 9 | **Correct as-is.** Deleted `aqa-as-micro`/`aqa-a-micro` section + 1 non-existent Edexcel B mark scheme. Link removed in `5f2d3aa`; the URLs still 404, correctly |
| `duplicate-without-user-selected-canonical.csv` | 28 | PDFs. No technical defect; a duplication judgement about exam-board documents |
| `crawled-currently-not-indexed.csv` | 53 | Mostly PDFs + 7 HTML. Authority, not technical |
| `page-with-redirect.csv` | 2 | `www.` → apex. Correct |
| `indexed-pages-baseline-2026-08-08.csv` | 65 | Baseline for the day-45 re-measure |

**Nothing from the exports is still live in the current files.** Every cause with
a technical fix has one. Logged once here as "previously flagged, now resolved";
not raised as findings.

**Fix pattern used, for consistency in future recommendations:** defects were
corrected **at the generator and re-run**, not hand-edited in the output
(`b7c5efc`, `1880565`, `2d8936a`). Canonical URL form is directory-with-trailing-
slash, never `/index.html`. New recommendations must follow both.

---

## 9. Recent work, and what is protected

`git log` since the feature wave. All 14 branches are fully merged into `main`.

| Commits | Work | Status |
| --- | --- | --- |
| `2f5fbf3`…`c666f13` | Flashcards feature: 671 cards, 6 decks, 89 SVGs | PROTECTED |
| `3af31e2`…`4df2e75` | Flashcards QA: card splits, board-reference removal | PROTECTED |
| `12bcaad`…`929ff89` | Glossary polish: capitalisation, rewrites, search ranking | PROTECTED |
| `1bb8337` | Past-paper question bank, Edexcel AS (8EC0) | PROTECTED |
| `5a51450`…`bcc1e34` | **SEO indexing fixes** | **PROTECTED — see below** |
| `2a47535`…`53a3e54` | **SEO architecture pass** | **PROTECTED — see below** |

### What the SEO work changed, enumerated

**Indexing fixes (`seo/indexing-fixes`), 2026-08-08:**

1. `d085317` — added `seo/`, `docs/`, `raw-notes/`, `scripts/`, the `*-data/`
   dirs and the root markdown to `_config.yml`'s `exclude`. Before this,
   `/REVIEW-NOTES.html`, `/CLAUDE.md` and `/scripts/build_glossary.py` were live.
2. `b7161e6` — rebuilt `sitemap.xml` as a `<sitemapindex>` over 7 children, with
   `lastmod` taken from git rather than build date.
3. `b7c5efc`, `1880565`, `2d8936a`, `79faf81`, `befb061`, `cf9b4c7` — rewrote
   every internal link and every canonical / `og:url` / `BreadcrumbList` URL to
   the trailing-slash directory form. **Fixed at the generator, then re-run.**
4. `5f2d3aa` — removed 3 links to Edexcel B June 2023 mark schemes that do not exist.
5. `d1d05ad` — deleted 33 Finder duplicate files and added the `* [0-9].*`
   ignore rules. One (`js/components/quiz 2.js`) had been served publicly.

**Architecture pass (`seo/architecture-pass`), 2026-08-08:**

6. `4db232c` — hoisted two `@import` rules out of `css/main.css` into every
   `<head>`, in order. Render-blocking chain removal. **Do not put them back.**
7. `17571f3` — practice-questions → past-paper-questions links, and lateral
   sibling links, on 166 pages. Generated.
8. `55dda8a` — re-pointed 13 stale query-string notes links to topic pages.
9. `d1e7a3a` — linked 47 Edexcel notes pages to their diagram gallery.
10. `6b2fe99` — four approved structured-data changes.
11. `53a3e54` — added 4 permanent assertions to `seo/tools/verify_seo.py`.

**The register of what must not be broken is `docs/audit/DO-NOT-BREAK.md`.**

---

## 10. Tooling present

| Location | Count | Nature |
| --- | ---: | --- |
| `scripts/` | 25 | Builders, extractors, 8 `verify_*` checkers. Stdlib-only Python + 2 Swift/PDFKit |
| `seo/tools/` | 24 files, 11 unique | SEO crawler, auditor, link graph, Lighthouse runner, `verify_seo.py` |
| `.github/` | — | **Does not exist.** Nothing runs automatically |

The 13 extra files in `seo/tools/` are Finder duplicates (`… 2.py`, `… 3.py`),
gitignored but present on disk. See finding PH00-005.
