# Phase 1 — Live crawl findings

Produced by `seo/tools/crawl.py` against production on 2026-08-08. ~2 req/sec,
custom User-Agent `EconomicsAcademy-SEO-Audit/1.0`, retry with backoff on 429
and 5xx. Raw data: `seo/01-crawl.csv`, `seo/01-variants.csv`, `seo/01-pdfs.csv`,
`seo/01-crawl.json`.

Three passes, deliberately separate:

1. **Link crawl** from `/`, following only links present in static HTML.
2. **Inventory fetch** of every URL derived from the filesystem.
3. **Variant probe** — `/path/`, `/path/index.html`, `/path.html`, `/path`,
   plus `http://` and `www.` — on every page.

The first two differ because `templates/header.html` and `footer.html` are
injected at runtime by `js/components/inject-templates.js`. A crawler that does
not execute JavaScript sees only what is written into each page. **That
difference turns out to be the most important result in this report.**

---

## Headline: 20 of 21 hub pages are never linked at their canonical URL

The link crawl reached 701 URLs. Of the 463 real pages, **22 were unreachable by
following static links.** Two are `404.html` and `confirmation.html` — correctly
`noindex` and correctly unlinked. The other **20 are the site's hub pages**:

```
/revision-notes/                      /practice-questions/
/revision-notes/edexcel-theme-1/      /practice-questions/edexcel-theme-1/
/revision-notes/edexcel-theme-2/      /practice-questions/edexcel-theme-2/
/revision-notes/edexcel-theme-3/      /practice-questions/edexcel-theme-3/
/revision-notes/edexcel-theme-4/      /practice-questions/edexcel-theme-4/
/revision-notes/aqa-a2-micro/         /practice-questions/aqa-a2-micro/
/revision-notes/aqa-a2-macro/         /practice-questions/aqa-a2-macro/
/revision-notes/macro-application/    /past-papers/
/past-papers/aqa/                     /past-papers/edexcel/
/past-papers/edexcel-b/               /past-papers/ocr/
```

For every one of them, the crawler reached the `…/index.html` twin instead. The
canonical URL — the one in `sitemap.xml`, the one each page's own `rel=canonical`
names — has **zero internal inbound links anywhere on the site.**

This is worse than "some links use the wrong form". It means:

- Google discovers `/revision-notes/index.html` by following links, crawls it,
  reads `canonical → /revision-notes/`, and must then crawl `/revision-notes/`
  as a separate request. **Every hub page costs two crawls, forever.**
- Internal PageRank lands on the non-canonical URL and has to be forwarded by
  the canonical tag, which is a hint rather than a redirect and consolidates
  slowly and incompletely.
- The canonical URL's only discovery path is the sitemap — which is exactly the
  thing that has not been processed yet.

These 20 pages carry the site's traffic: `/past-papers/edexcel-b/` (7,214
impressions), `/revision-notes/` (5,791), `/past-papers/ocr/` (4,757),
`/past-papers/aqa/` (3,827).

---

## Response codes

| | Count |
| --- | ---: |
| URLs fetched | 723 |
| HTTP 200 | **723** |
| HTTP 404 | 0 |
| HTTP 5xx | 0 |
| Redirect chains encountered in the link graph | 0 |
| Redirect loops | 0 |
| Network errors | 0 |

**No internal link on the site resolves to a 404, a redirect, or an error.**
The three dead PDF links found in Phase 2 are `href`s to files that do not
exist; they are not followed by this crawler because it skips PDFs, and are
reported in `seo/02-sitewide-defects.md` instead.

## Duplicate URL variants both returning 200

Confirmed by direct probe, not inferred:

| Page form | Canonical | Duplicate also 200 | Pages | Internally linked? |
| --- | --- | --- | ---: | --- |
| `<dir>/index.html` | `/<dir>/` | `/<dir>/index.html` | 121 | **Yes — 1,300 links** |
| `<path>.html` | `/<path>.html` | `/<path>` | 340 | No — zero links |

Requesting a directory without its trailing slash (`/revision-notes`) correctly
301s to `/revision-notes/`. `http://`, `http://www.` and `https://www.` all 301
to apex HTTPS. `https://eliotking01.github.io/economics-academy/` 301s to the
apex domain. Host and protocol canonicalisation is correct.

`/Revision-Notes/` returns 404 — GitHub Pages is case-sensitive, as expected.

**The extensionless duplicate is latent, not active.** Zero internal links use
it, every affected page self-canonicalises to the `.html` form, and no GSC
export mentions one. It is reachable only by an external link or a manual guess.
Out of scope this pass under the root-`.html` deferral; carried to
`seo/04-decisions.md`.

## Canonical tags

| | Count |
| --- | ---: |
| 200 responses parsed | 723 |
| `canonical` == request URL | 461 |
| `canonical` != request URL, **correctly** (duplicate variant pointing home) | 253 |
| `canonical` != request URL, **incorrectly** | **7** |
| No canonical at all | 2 (`404.html`, `confirmation.html` — both `noindex`) |

The 7 incorrect ones all point *away* from the URL the sitemap advertises:

```
/practice-questions/                  -> /practice-questions/index.html
/practice-questions/aqa-a2-macro/     -> /practice-questions/aqa-a2-macro/index.html
/practice-questions/aqa-a2-micro/     -> /practice-questions/aqa-a2-micro/index.html
/practice-questions/edexcel-theme-1/  -> /practice-questions/edexcel-theme-1/index.html
/practice-questions/edexcel-theme-2/  -> /practice-questions/edexcel-theme-2/index.html
/practice-questions/edexcel-theme-3/  -> /practice-questions/edexcel-theme-3/index.html
/practice-questions/edexcel-theme-4/  -> /practice-questions/edexcel-theme-4/index.html
```

The sitemap says index `/practice-questions/`; the page at that URL says "index
`/practice-questions/index.html` instead". The two signals contradict each other,
and 173 practice-question pages sit under these seven hubs.

## Query-parameter URLs

The link crawl discovered **239 parameterised URLs behind just 7 real pages** —
`?topic=` on the six flashcard decks and `?board=…&topic=…` on
`/past-paper-questions/`:

```
 73  /past-paper-questions/?board=…&topic=…
 54  /flashcards/aqa/micro/?topic=…
 25  /flashcards/aqa/macro/?topic=…
 24  /flashcards/edexcel-a/theme-2/?topic=…
 22  /flashcards/edexcel-a/theme-1/?topic=…
 21  /flashcards/edexcel-a/theme-4/?topic=…
 20  /flashcards/edexcel-a/theme-3/?topic=…
```

**This is not a duplication defect.** Each target page's hardcoded canonical
names the clean URL, so Google consolidates correctly. It is a crawl-budget
cost: 239 URLs Googlebot must fetch and discard, competing with the 340 pages it
has never seen. Judgement call, carried to `seo/04-decisions.md`.

## Accidental noindex

**None.** Across all 723 URLs, exactly two carry a robots meta tag, both
`noindex, nofollow`, both intentional:

```
/404.html
/confirmation.html
```

The 26 URLs GSC lists under "Excluded by 'noindex' tag" — all AQA topic pages —
**return 200 with no robots meta today.** Their crawl dates run 2026-05-18 to
2026-07-13, all before commit `203f6bd` (2026-07-30). The report is stale and
those pages recover on re-crawl with no work.

## Titles, descriptions, headings

Measured on the 484 non-parameterised 200 responses:

| | Result |
| --- | --- |
| Pages with exactly one `<h1>` | **484 / 484** |
| Pages with zero or multiple `<h1>` | 0 |
| Missing `<title>` | 0 |
| Missing meta description | 0 |
| Title length | min 33, median 73, max 160 — **307 exceed 60 chars** |
| Description length | min 118, median 157, max 247 — **143 outside 70–160** |
| Duplicate titles | 1 pair |
| Duplicate descriptions | 0 |

Title and description length are **advisory, not defects**. Google truncates the
display but does not penalise, and every title here is descriptive and unique.
Ranked accordingly in Phase 3 — this is not where the value is.

## Content depth

Main-content word count, taken from `<body>` minus `script/style/svg/noscript`:

| | Words |
| --- | ---: |
| Minimum | 25 |
| 10th percentile | 414 |
| Median | **914** |
| 90th percentile | 2,114 |
| Maximum | 18,890 |
| Pages under 300 words | **27** |

The site is not thin. 27 pages fall under 300 words and **25 of them are hub or
index pages whose job is navigation** — `/revision-notes/` at 118 words is a
board selector, not an article. Only two genuine content pages are short:

```
249w  revision-notes/aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html
287w  revision-notes/aqa-a2-micro/1-4-1-production-and-productivity.html
```

Near-duplicate clustering (8-word shingles, Jaccard ≥ 0.80, compared within
sections) found **5 pairs**, all AQA↔Edexcel twins covering the same topic on
two boards:

```
87%  aqa-a2-macro/2-5-2-supply-side-policies       <-> edexcel-theme-2/2-6-3-supply-side-policies
83%  aqa-a2-micro/1-4-5-economies-and-diseconomies <-> edexcel-theme-3/3-3-3-economies-diseconomies
81%  aqa-a2-micro/1-8-9-government-intervention    <-> edexcel-theme-1/1-4-1-government-intervention
80%  aqa-a2-macro/2-6-1-globalisation              <-> edexcel-theme-4/4-1-1-globalisation
80%  aqa-a2-micro/1-3-2-price-income-cross-elast.  <-> edexcel-theme-1/1-2-3-price-income-cross-elast.
```

These are deliberate — CLAUDE.md defines a "twin" as the page covering the same
content on the other board, and they target different board-specific queries.
No action recommended; assessed honestly in Phase 3 group C.

## Internal link graph

| | Count |
| --- | ---: |
| Internal link instances in static HTML | 17,962 |
| Dead targets | **0** |
| Case-mismatched targets | **0** |
| Pages with zero static inbound links | 22 (20 hubs + the 2 `noindex` pages) |
| Pages with 1–2 inbound links | 98 |
| Median inbound links per page | 28 |

Excluding the hub-page problem above, the site is densely and correctly
interlinked. Nothing is orphaned in the ordinary sense.
