# Phase 0 — Ground truth

Read-only inventory. Every number below is produced by `seo/tools/inventory.py`
against the git index, `_config.yml`, `sitemap.xml`, `robots.txt` and the GSC
exports, or by a live HTTP request. Nothing is inferred from a filename.

Reproduce with:

```
python3 seo/tools/inventory.py
python3 seo/tools/inventory.py --json > /tmp/inventory.json
```

Date of audit: 2026-08-08. Site: `https://economicsacademy.co.uk` (GitHub Pages,
apex domain via `CNAME`, stock Jekyll build — there is no `.github/workflows/`).

---

## a. Every HTML file, mapped to its live URL

| Layer | Count |
| --- | ---: |
| HTML files tracked in git | 480 |
| — not published (Jekyll `_` rule, all in `_working/`) | 15 |
| **Published HTML** | **465** |
| — runtime partials, fetched by JS, not pages (`templates/header.html`, `templates/footer.html`) | 2 |
| **Real pages** | **463** |
| — deliberate `noindex` (`404.html`, `confirmation.html`) | 2 |
| **Indexable pages** | **461** |

A further 14 HTML files exist in `_working/flashcards/qa/` on disk but are
untracked; they are excluded twice over (untracked *and* under `_`), so they
cannot reach the site.

PDFs: **284 tracked, 283 published** — 281 past papers plus
`specificiations/aqa-spec.pdf` and `specificiations/edexcel-a-spec.pdf`. The one
unpublished PDF is `_working/flashcards/qa/print-qa/deck.pdf`.

### Breakdown by section

| Section | Indexable pages |
| --- | ---: |
| `revision-notes/` (topic pages, hubs, diagrams, glossary, macro-application) | 179 |
| `practice-questions/` | 173 |
| `past-paper-questions/` | 90 |
| Root (`index`, `about`, `contact`, `faq`, `marking`, `privacy`, `tutoring`) | 7 |
| `flashcards/` | 7 |
| `past-papers/` (board hub pages) | 5 |
| **Total** | **461** |

### URL mapping under the project URL policy

- `index.html` → `/`
- `<dir>/index.html` → `/<dir>/` — **121 pages** take this form
- `<path>.html` → `/<path>.html` — **340 pages** take this form

`_config.yml`'s `exclude` list is working exactly as documented in CLAUDE.md:
`scripts/`, `raw-notes/`, `docs/`, the four `*-data/` directories and the root
markdown are all unpublished. `templates/` and `past-paper-questions/` remain
public by decision, as required — they are fetched at runtime.

---

## b. sitemap.xml

| Property | Value |
| --- | --- |
| Format | flat `<urlset>`, **not** a sitemap index |
| `<loc>` entries | **461** |
| Entries with `<lastmod>` | 461 (100%) |
| Entries using `index.html` form | **0** |
| Non-HTTPS entries | 0 |
| Entries with no corresponding file | **0** |
| Published indexable pages absent from the sitemap | **0** |

**The sitemap is a byte-perfect 1:1 match with the filesystem.** This is the
single strongest thing about the current setup and the brief's assumption that
it might contain non-canonical variants is wrong — it does not.

Two caveats:

- **`lastmod` is not derived from git.** 440 of 461 entries carry just three
  dates — 174 × `2026-07-30`, 173 × `2026-08-01`, 93 × `2026-08-07` — which are
  build dates, not per-file modification dates. Plausible in the sense of being
  real recent dates, but they do not distinguish a page edited yesterday from
  one untouched since May. Google discounts `lastmod` it cannot corroborate.
- **All 283 published PDFs are absent from the sitemap**, including 77 that
  appear in the "not indexed" reports and 13 that already earn traffic
  (89 clicks / 6,803 impressions between them).

## c. robots.txt

```
User-agent: *
Allow: /

Sitemap: https://economicsacademy.co.uk/sitemap.xml
```

Nothing is blocked. Nothing crawlable is disallowed. **No defect.**

---

## d. GSC exports, normalised

All seven files detected as **UTF-8, comma-delimited** (checked per file by BOM
sniff and delimiter frequency, not assumed). Header is `URL,Last crawled` in
every file. Finder duplicates — `alternate-page-with-proper-canonical-tag 2.csv`,
`page-with-redirect 2.csv`, `performance-pages 2.csv` — are byte-identical to
their originals and are skipped so rows are not double-counted.

| `gsc_reason` | Rows | PDF | HTML |
| --- | ---: | ---: | ---: |
| `crawled-currently-not-indexed` | 54 | 47 | 7 |
| `duplicate-without-user-selected-canonical` | 29 | 29 | 0 |
| `excluded-by-noindex-tag` | 26 | 0 | 26 |
| `not-found-404` | 10 | 1 | 9 |
| `alternate-page-with-proper-canonical-tag` | 9 | 0 | 9 |
| `page-with-redirect` | 3 | 0 | 3 |
| `redirect-error` | 1 | 0 | 1 |
| **Total** | **132** | **77** | **55** |

132 rows, 132 distinct URLs, no overlap between files.

**Are the exports complete or truncated?** Complete. GSC reports 132 pages not
indexed and the exports total exactly 132. The 1,000-row cap was never reached —
the largest single file is 54 rows. **Every not-indexed URL Google knows about is
in these files.**

The one thing missing is an export of the 66 *indexed* URLs, which was not
supplied. Consequences are stated in the reconciliation below.

---

## Four-way reconciliation

| | HTML | PDF | Total |
| --- | ---: | ---: | ---: |
| **1. Repo — published, indexable** | 461 | 283 | 744 |
| **2. Sitemap URLs** | 461 | 0 | 461 |
| **3. GSC-known URLs** | ≤121 | ≥77 | 198 |
| **4. Live-crawlable URLs returning 200** | **922** | 283 | 1,205 |

### Gap 1 — Repo vs sitemap: **0 HTML, 283 PDF**

No HTML drift at all. The entire gap is PDFs, which are deliberately absent and
which you have decided to add as a separate sitemap in the index.

### Gap 2 — Discovery gap: **≥340 HTML pages (≥74%) Google has never seen**

Google knows 198 URLs (66 indexed + 132 not indexed). At least 77 of those are
PDFs, from the not-indexed exports alone. Therefore **at most 121 of the 461 HTML
pages are known to Google, and at least 340 are not.**

This is stated as a floor, not an exact figure, because the indexed-pages export
was not supplied — some of the 66 indexed URLs are certainly PDFs too, which
would push the true discovery gap *higher* than 340, never lower. The floor is
sufficient: every defect in this audit is detected by rule against the
filesystem, so no fix or priority depends on closing this measurement.

For context, the sections Google is least likely to know are the newest. Across
all 132 not-indexed rows there is exactly **one** URL from
`past-paper-questions/` (90 pages), **none** from `practice-questions/` (173),
**none** from `flashcards/` (7) and **none** from `revision-notes/glossary/` (3)
— **273 pages between them**, essentially invisible to Google today. These are the
pages the imminent crawl wave will meet for the first time, and the reason
template-level fixes must land before it.

### Gap 3 — Duplication gap: **461 pages serve at 922 distinct HTTP-200 URLs**

Verified live, not assumed. GitHub Pages serves every page at exactly two URLs:

| Page form | Canonical URL | Duplicate also returning **200** | Pages |
| --- | --- | --- | ---: |
| `<dir>/index.html` | `/<dir>/` | `/<dir>/index.html` | 121 |
| `<path>.html` | `/<path>.html` | `/<path>` (extensionless) | 340 |

Requesting a directory *without* a trailing slash (`/revision-notes`) correctly
301s to `/revision-notes/`, so that variant is not part of the problem.

The two halves of this gap are not equally urgent:

- **The `/index.html` half is live and costing traffic.** 1,300 internal links
  point at it, and Google has indexed and is ranking both variants of ten pages.
- **The extensionless half is latent.** Zero internal links use it, canonicals on
  those pages correctly self-reference the `.html` form, and no GSC export
  mentions one. It is reachable only via an external link. Out of scope this
  pass per the root-`.html` deferral; logged for Phase 6.

#### What the `/index.html` split is actually costing

From `seo/performance-pages.csv` — ten pages currently rank as twenty URLs:

| Canonical URL | clicks / impressions | Duplicate `…/index.html` | clicks / impressions |
| --- | ---: | ---: | ---: |
| `/past-papers/edexcel-b/` | 78 / 7,214 | | 80 / 4,476 |
| `/revision-notes/` | 187 / 5,791 | | 174 / 4,112 |
| `/past-papers/ocr/` | 65 / 4,757 | | 68 / 4,684 |
| `/past-papers/aqa/` | 34 / 3,827 | | 17 / 1,963 |
| `/` | 223 / 2,463 | | 1 / 272 |
| `/revision-notes/edexcel-theme-1/` | 23 / 1,101 | | 6 / 495 |
| `/revision-notes/aqa-a2-micro/` | 8 / 843 | | 4 / 341 |
| `/revision-notes/edexcel-theme-4/` | 6 / 621 | | 10 / 451 |
| `/past-papers/` | 1 / 100 | | 3 / 874 |
| `/revision-notes/edexcel-theme-3/` | 1 / 33 | | 11 / 391 |

**1,000 clicks and 44,809 impressions sit on these ten split pairs — 81% of the
site's clicks and 64% of its impressions.** On three of them
(`/past-papers/edexcel-b/`, `/revision-notes/edexcel-theme-3/`,
`/past-papers/`) the *non-canonical* variant is outperforming the canonical one.

### Gap 4 — Indexing gap: 132 not indexed, but most of it is not a defect

| Reason | Rows | Assessment |
| --- | ---: | --- |
| `excluded-by-noindex-tag` | 26 | **Stale. Already fixed.** Only `404.html` and `confirmation.html` carry `noindex` anywhere in the repo. Three of the reported AQA pages fetched live: all HTTP 200, no robots meta. Crawl dates run 2026-05-18 → 2026-07-13, all before commit `203f6bd` (2026-07-30). Recovers on re-crawl, no work needed. |
| `duplicate-without-user-selected-canonical` | 29 | 29/29 PDFs. Not fixable on GitHub Pages — no `X-Robots-Tag`, no canonical inside a PDF. |
| `crawled-currently-not-indexed` | 54 | 47 PDFs + 7 HTML. The 7 HTML pages are `about`/`contact`/`faq` and four Theme 1 topic pages, 600–1,500 words of real content, last crawled Feb–May 2026. A Google quality/priority judgement, not a technical defect. |
| `alternate-page-with-proper-canonical-tag` | 9 | 9/9 are `…/index.html` URLs. Google behaving correctly — this is the *symptom* of Gap 3, and the reason to fix the internal links. |
| `not-found-404` | 10 | 6 are `/revision-notes/aqa-as-micro/*` and `aqa-a-micro/*`, a removed section with zero internal links — correctly dead, leave 404. **1 is a real defect**: an Edexcel B June 2023 mark scheme still linked from a live page. |
| `page-with-redirect` | 3 | `http://`, `http://www.`, `https://www.` variants of the homepage, all correctly 301ing to apex HTTPS. Correct behaviour. |
| `redirect-error` | 1 | `/past-paper-questions`. Re-tested live: clean HTTP/2 301 to `/past-paper-questions/`, no protocol downgrade, no chain. Transient. |

---

## Host and build configuration

| Check | Finding |
| --- | --- |
| CI / build workflow | **None.** No `.github/workflows/`. Stock GitHub Pages Jekyll build. |
| `.nojekyll` | Absent — correct. Adding one would immediately publish every `_` directory, including `_working/`. |
| `_config.yml` | Present, `exclude`-only, verified working. |
| `CNAME` | `economicsacademy.co.uk` (apex). |
| `http://` → `https://` | 301 ✓ |
| `www.` → apex | 301 ✓ (both schemes) |
| `eliotking01.github.io/economics-academy/` | 301 → apex ✓ |
| 404 handling | `404.html` present, returns a real HTTP 404 ✓ |
| Case sensitivity | Confirmed: `/Revision-Notes/` → 404 while `/revision-notes/` → 200. |

---

## Summary of what is already correct

Worth stating plainly, because it changes where the effort should go: the
sitemap matches the filesystem exactly; all 461 indexable pages have a
canonical, `<title>`, meta description, `<h1>` and `og:url`; there are zero
orphan pages, zero case-mismatched internal links, zero dead internal HTML
links, zero invalid JSON-LD blocks and zero duplicate meta descriptions; host
and protocol canonicalisation is correct; `robots.txt` blocks nothing.

The work is not a clean-up. It is **one structural defect** — the `/index.html`
duplicate surface and the 1,300 internal links feeding it — plus a short tail of
small, individually-cheap fixes, quantified in Phase 2.
