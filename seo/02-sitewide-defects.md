# Phase 2 — Every defect, generalised sitewide

The GSC exports name 132 URLs. This site has 461 indexable pages, and Google
stopped crawling most sections months ago, so those exports describe a subset of
a subset — and cannot contain any page created since. **A page absent from them
is unobserved, not clean.**

Every rule below is mechanical, runs against all 463 pages in the working tree,
and never consults GSC to decide what to inspect. GSC is used only to *label* a
finding as reported or unreported.

Reproduce with:

```
python3 seo/tools/audit.py
python3 seo/tools/audit.py --json /tmp/findings.json
```

**Of the 461 indexable pages, GSC knows 42 and has never seen 419.**

---

## Defect classes: reported vs unreported

Counted as *instances* (a page with 12 bad links contributes 12).

| Defect class | Reported | Unreported | Total | Pages | Source responsible |
| --- | ---: | ---: | ---: | ---: | --- |
| `link-noncanonical` | 111 | 1,182 | **1,293** | 458 | 4 generators + `templates/header.html` + 184 hand-written pages |
| `title-long` (>60 chars) | 12 | 274 | 286 | 286 | `build_questions.py`, `build_past_paper_questions.py` |
| `link-parameterised` | 45 | 194 | 239 | 166 | hand-written notes pages + generators |
| `description-length` (outside 70–160) | 12 | 114 | 126 | 126 | `build_past_paper_questions.py` + others |
| `thin-content` (<300 words) | 8 | 12 | 20 | 20 | hub pages, by design |
| `canonical-wrong` | **0** | **7** | 7 | 7 | `scripts/build_questions.py` |
| `near-duplicate` (≥80% shingle) | 2 | 3 | 5 | 5 | deliberate AQA↔Edexcel twins |
| `link-dead` | 3 | 0 | 3 | 1 | `past-papers/edexcel-b/index.html` |
| `title-duplicate` | 1 | 1 | 2 | 2 | `scripts/build_past_paper_questions.py` |
| `ogtitle-mismatch` | 1 | 1 | 2 | 2 | two hand-written pages |
| `jsonld-missing` | 0 | 2 | 2 | 2 | `privacy.html`, `macro-application/index.html` |
| `twittertitle-mismatch` | 0 | 1 | 1 | 1 | `macro-application/index.html` |
| **Total** | **195** | **1,791** | **1,986** | | |

### Rules that ran and found nothing

Stated explicitly, because a clean result is only meaningful if the rule
actually executed. All 13 rules ran; these returned zero across all 463 pages:

`canonical-missing` · `ogurl-mismatch` · `title-missing` · `description-missing`
· `description-duplicate` · `h1-missing` · `h1-multiple` · `lang-missing` ·
`lang-wrong` · `noindex-accidental` · `jsonld-invalid` · `link-case-mismatch` ·
`orphan` · `sitemap-missing` · `sitemap-stale`

---

## (d) Defects running HIGHER on undiscovered pages — recent regressions

Rate = share of pages in each group carrying at least one instance.

| Defect class | Reported (42 pages) | Unreported (419 pages) | Verdict |
| --- | ---: | ---: | --- |
| `title-long` | 28.6% | **65.4%** | **Regression — 2.3×** |
| `canonical-wrong` | 0.0% | **1.7%** | **Regression — 100% unseen** |
| `link-noncanonical` | 95.2% | 99.3% | near-universal both ways |
| `description-length` | 28.6% | 27.2% | flat |
| `link-parameterised` | 69.0% | 32.7% | lower on new pages |
| `thin-content` | 19.0% | 2.9% | lower — the thin pages are the hubs Google already knows |
| `near-duplicate` | 4.8% | 0.7% | lower |

Two genuine regressions, both traceable to the newer generated sections:

1. **`title-long` more than doubled.** 171 of 286 long titles are in
   `practice-questions/` and 90 in `past-paper-questions/` — both fully
   generated, both essentially unknown to Google. The generators build titles by
   concatenating a full topic name with a board and a site suffix, which
   overflows 60 characters far more often than the hand-written notes titles do.
   Advisory severity: Google truncates the SERP display but does not penalise.

2. **`canonical-wrong` is 100% concentrated on pages Google has never crawled.**
   All 7 are `practice-questions/` hubs. Google has not yet seen this defect —
   **it is about to meet it on first contact**, which is precisely the scenario
   the brief is trying to pre-empt. This is the highest-leverage item in the
   whole audit relative to its effort: one generator, seven pages, 173 pages
   sitting beneath them.

---

## (c) Tracing each defect to its source

A defect on 200 pages is one bug in one file, not 200 bugs.

### `link-noncanonical` — 1,293 instances, 458 files

| Origin | Links | Files | Fix at |
| --- | ---: | ---: | --- |
| Hand-written pages | 533 | 184 | the pages (516 of them in `revision-notes/`) |
| `scripts/build_questions.py` | 523 | 173 | the generator |
| `scripts/build_past_paper_questions.py` | 189 | 90 | the generator |
| `templates/header.html` | 22 | 1 | the template |
| `scripts/build_flashcards.py` | 20 | 7 | the generator |
| `scripts/build_glossary.py` | 6 | 3 | the generator |

**Five source files account for 760 of the 1,293 links (59%).** The remaining
533 live in hand-written HTML and need a direct rewrite.

The root cause is written down explicitly in
`scripts/build_past_paper_questions.py:473-474`:

```python
"""The site writes the home link as /index.html but canonicalises it as /."""
return "/index.html" if path == "/" else path
```

That is the convention, encoded as a helper. It has to go, or the next build
undoes any fix applied to the emitted HTML.

The 12 most-linked non-canonical targets:

```
275  /revision-notes/index.html          60  /revision-notes/aqa-a2-micro/index.html
185  /past-papers/edexcel/index.html     57  /practice-questions/aqa-a2-micro/index.html
175  /practice-questions/index.html      31  /revision-notes/aqa-a2-macro/index.html
165  /past-papers/aqa/index.html         30  /revision-notes/edexcel-theme-2/index.html
 93  /index.html                         28  /revision-notes/edexcel-theme-1/index.html
                                         27  /practice-questions/edexcel-theme-2/index.html
```

### `canonical-wrong` — 7 instances, `scripts/build_questions.py`

Every `practice-questions/**/index.html` emits
`canonical = …/index.html` while `sitemap.xml` lists `…/`. The two signals
contradict each other. Confirmed live in Phase 1.

### `link-dead` — 3 instances, `past-papers/edexcel-b/index.html`

Links to Edexcel B June 2023 **mark schemes** for Papers 1, 2 and 3. Only the
question papers exist on disk; the mark schemes were never added. One of the
three is in GSC's `not-found-404` export, crawled 2026-03-06.

### `title-duplicate` — 1 pair, `scripts/build_past_paper_questions.py`

`past-paper-questions/index.html` and `past-paper-questions/edexcel/index.html`
both render *"Edexcel A-Level Economics Past Paper Questions | Economics
Academy"*. The master page has taken the board page's title.

### `jsonld-missing` / `ogtitle-mismatch` / `twittertitle-mismatch` — 5 instances

Hand-written: `privacy.html` (no JSON-LD), `revision-notes/index.html`
(`og:title` differs from `<title>`), `revision-notes/macro-application/index.html`
(no JSON-LD, and both `og:title` and `twitter:title` differ).

### `link-parameterised` — 239 instances, 166 files

`?topic=` and `?board=` deep links into the flashcard decks and the question
bank. Emitted by both hand-written notes pages and the generators. **Not a
duplication defect** — every target self-canonicalises to the clean URL — but
239 URLs of crawl budget spent while 340 pages wait to be discovered.

---

## Forward-looking readiness — the 419 pages Google has never seen

These are about to be crawled for the first time. A page judged thin or
duplicate on first contact can sit in "Crawled – currently not indexed" for
months, so each was checked against every criterion in the brief:

| Check | Result |
| --- | --- |
| Reachable at its canonical URL (HTTP 200) | **419 / 419** ✓ |
| Correct self-referencing canonical | 412 / 419 — **7 gaps** |
| Not orphaned | 419 / 419 ✓ |
| No accidental `noindex` | 419 / 419 ✓ |
| Unique `<title>` | 418 / 419 — **1 gap** |
| Unique meta description | 419 / 419 ✓ |
| Has exactly one `<h1>` | 419 / 419 ✓ |
| Sufficient unique main content (≥300 words) | 407 / 419 — **12 gaps**, 10 of them hub pages |
| Correct case in all inbound internal links | 419 / 419 ✓ |
| Present in `sitemap.xml` | 419 / 419 ✓ |

**Only 20 of the 419 undiscovered pages have any blocking defect at all**, and
they are concentrated in one place.

### Ranked: undiscovered pages most at risk on first crawl

Scored by defect severity (`canonical-wrong` 10, `link-dead` 8, `title-duplicate`
6, `thin-content` 5, `near-duplicate` 4, `jsonld-missing` 3, og/twitter 2,
title/description length 1, per-link defects fractional).

| Score | Page | Defects |
| ---: | --- | --- |
| 17.1 | `practice-questions/edexcel-theme-1/index.html` | canonical-wrong, thin, title-long, description-length |
| 17.1 | `practice-questions/edexcel-theme-2/index.html` | canonical-wrong, thin, title-long, description-length |
| 16.1 | `practice-questions/index.html` | canonical-wrong, thin, title-long |
| 16.1 | `practice-questions/edexcel-theme-3/index.html` | canonical-wrong, thin, title-long |
| 16.1 | `practice-questions/edexcel-theme-4/index.html` | canonical-wrong, thin, title-long |
| 12.1 | `practice-questions/aqa-a2-micro/index.html` | canonical-wrong, title-long, description-length |
| 11.1 | `practice-questions/aqa-a2-macro/index.html` | canonical-wrong, title-long |
| 9.0 | `revision-notes/macro-application/index.html` | jsonld-missing, og+twitter mismatch, description-length |
| 8.1 | `past-paper-questions/edexcel/index.html` | title-duplicate, title-long, description-length |
| 7.1 | `index.html` (homepage) | thin (118w), title-long, description-length |
| 7.0 | `revision-notes/aqa-a2-macro/index.html` | thin, title-long, description-length |
| 7.0 | `revision-notes/edexcel-theme-2/index.html` | thin, title-long, description-length |
| 6.1 | `revision-notes/glossary/index.html` | thin, title-long |
| 5.1 | `revision-notes/aqa-a2-micro/1-4-1-production-and-productivity.html` | thin (287w) |
| 5.1 | `revision-notes/aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html` | thin (249w) |
| 5.0 | `flashcards/index.html` | thin (106w) |
| 3.0 | `privacy.html` | jsonld-missing |

**The top seven are all the same bug in `scripts/build_questions.py`.** Fixing
that one file, plus re-running the generator, clears the entire top of this list
before Google's first crawl — which is the single most valuable thing available
in this pass.
