# Phase 3 — Diagnosis

Structured by **defect class**, not by GSC reason. GSC reasons are evidence for
defects, not the unit of work — five of the seven reasons in your exports turn
out to describe Google behaving correctly, or a problem already fixed.

Evidence: `seo/00-inventory.md`, `seo/01-crawl-findings.md`,
`seo/02-sitewide-defects.md`. Decisions needing you: `seo/04-decisions.md`.

---

## The short version

The site is technically sound. 461 indexable pages, all returning 200, all with
a canonical, title, description, single `<h1>` and `og:url`; a sitemap that
matches the filesystem exactly; no orphans, no dead links, no case bugs, no
accidental `noindex`, correct host and protocol canonicalisation.

There is **one structural defect**, and it is significant:

> Every internal link to a hub page in `revision-notes/`, `practice-questions/`
> and `past-papers/` points at `/x/index.html`, which returns 200. The canonical
> URL `/x/` has zero internal inbound links. 20 hub pages are affected, they
> carry ~81% of the site's clicks, and Google is currently ranking both halves of
> ten of them as separate URLs.

Everything else is a short tail. The most urgent tail item is 7 wrong canonicals
in `practice-questions/` — urgent not because it is large, but because it sits
entirely on pages Google has never crawled and is about to.

---

# Defect classes

## D1 — Internal links point at non-canonical `/index.html` URLs

**Explains GSC reason:** `alternate-page-with-proper-canonical-tag` (9/9 rows).

**Reported pages affected:** 40 of 42 · **Unreported:** 416 of 419 · **Total:**
458 pages, 1,293 link instances.

### Root cause

GitHub Pages serves `/x/index.html` at **HTTP 200**, not a redirect (verified
live). The site's canonical tags correctly name `/x/`, but its links do not. The
convention is written down as a helper in
`scripts/build_past_paper_questions.py:473-474`:

```python
"""The site writes the home link as /index.html but canonicalises it as /."""
return "/index.html" if path == "/" else path
```

### Evidence

A link crawl following only static HTML reached 701 URLs. Of the 121
directory-form pages, 101 were reached at their canonical URL and **20 were not
reachable there at all** — it found the `/index.html` twin every time. Those 20
are the hubs of `revision-notes/`, `practice-questions/` and `past-papers/`; the
newer `flashcards/`, `past-paper-questions/` and `revision-notes/glossary/`
sections already link canonically. The canonical form's only discovery path for
those 20 is the sitemap, which has not been processed.

Google is already indexing both halves. From `seo/performance-pages.csv`:

| Canonical | clicks / impr | `…/index.html` | clicks / impr |
| --- | ---: | --- | ---: |
| `/past-papers/edexcel-b/` | 78 / 7,214 | | 80 / 4,476 |
| `/revision-notes/` | 187 / 5,791 | | 174 / 4,112 |
| `/past-papers/ocr/` | 65 / 4,757 | | 68 / 4,684 |
| `/past-papers/aqa/` | 34 / 3,827 | | 17 / 1,963 |
| `/` | 223 / 2,463 | | 1 / 272 |
| *(5 more pairs)* | | | |

**10 pairs, 1,000 clicks, 44,809 impressions — 81% of clicks and 64% of
impressions.** On three pairs the non-canonical variant outranks the canonical.

### Fixable in code on GitHub Pages? **Yes, completely.**

### Fix

Rewrite every `href="/x/index.html"` to `href="/x/"` and `href="/index.html"` to
`href="/"`, then fix the five sources so the next build does not undo it.

| Source | Links | Files |
| --- | ---: | ---: |
| Hand-written pages (516 in `revision-notes/`) | 533 | 184 |
| `scripts/build_questions.py` | 523 | 173 |
| `scripts/build_past_paper_questions.py` | 189 | 90 |
| `templates/header.html` | 22 | 1 |
| `scripts/build_flashcards.py` | 20 | 7 |
| `scripts/build_glossary.py` | 6 | 3 |

`seo/tools/fix_links.py` does the rewrite. Dry run over the working tree:
**458 files, 1,300 rewrites, 0 invariant failures.** It never parses or
re-serialises HTML — it replaces only the bytes between the quotes of an
`href="…"` and asserts per file that blanking every href leaves old and new
identical, and that the `href=` count is unchanged.

**This is a bulk operation over 458 files and needs your sign-off** — item B1 in
`seo/04-decisions.md`, with a sample diff.

---

## D2 — Seven canonicals contradict the sitemap

**Explains GSC reason:** none yet — *and that is the point*.

**Reported pages:** 0 · **Unreported:** 7 · **Total:** 7.

### Root cause

`scripts/build_questions.py` builds these pages and constructs their canonical
URL with the `index.html` suffix, in exactly two places:

```python
997:   url = f"{SITE}/practice-questions/{board_dir}/index.html"   # 6 board hubs
1095:  url = f"{SITE}/practice-questions/index.html"               # the master hub
```

That `url` feeds `rel=canonical` and `og:url`. Meanwhile `sitemap.xml` lists
`…/`. Confirmed live: fetching `https://economicsacademy.co.uk/practice-questions/`
returns a page whose canonical points *away from itself*.

(Note the script's docstring claims "Board index pages and the hub are built by a
later phase; this script currently emits topic pages and the sitemap block."
That is out of date — it builds them. Worth correcting while in there.)

### Why this ranks above its size

It is the only defect that is **100% concentrated on pages Google has never
crawled.** GSC has zero rows for `practice-questions/` — all 173 pages are
undiscovered. The seven hubs sit above them and are about to be crawled for the
first time, with the sitemap saying one thing and the page saying another.

### Fixable in code? **Yes.**

### Fix

`scripts/build_questions.py` — emit the directory form for `canonical` and
`og:url`, re-run the generator. 7 pages, one file.

---

## D3 — Three dead PDF links

**Explains GSC reason:** `not-found-404` (1 of 10 rows).

**Reported:** 3 instances · **Unreported:** 0 · **Total:** 3, all in one file.

`past-papers/edexcel-b/index.html` links to Edexcel B June 2023 **mark schemes**
for Papers 1–3. Only the question papers exist; the mark schemes were never
added. Crawled by Google 2026-03-06 and recorded as a 404.

**Fixable in code? Yes.** You have already chosen: remove the three links.

The other 6 `not-found-404` rows are `/revision-notes/aqa-as-micro/*` and
`aqa-a-micro/*` — a removed section with zero internal links. **Correctly dead.
No stubs.** (Ground rule 6.)

---

## D3b — The generators stamp build dates into `sitemap.xml`

**Explains GSC reason:** none directly — but it is why `lastmod` is not
trustworthy, and it will actively fight the Phase 4 sitemap fix.

Verified by running each generator against a clean tree and diffing:

| Generator | HTML output | Side effects |
| --- | --- | --- |
| `scripts/build_questions.py` | **byte-identical** (173 pages) | none |
| `scripts/build_past_paper_questions.py` | **byte-identical** (90 pages) | rewrites 90 `<lastmod>` entries in `sitemap.xml` to today, and `questions.json`'s `"generated"` field |

That is the mechanism behind Phase 0's observation that 440 of 461 `lastmod`
values are just three build dates. A page untouched since May is advertised to
Google as modified today, so Google learns to ignore the field entirely.

**Consequence for Phase 4:** regenerating `sitemap.xml` with git-derived
`lastmod` is not enough on its own. `build_past_paper_questions.py` must stop
writing `lastmod` into the sitemap, or the next run of it silently reverts 90
entries to the build date. Same for `build_questions.py --sitemap`.

**Fixable in code? Yes.** Have the sitemap builder own `lastmod` exclusively and
remove the date-stamping from the generators.

---

## D4 — Duplicate title

**Explains GSC reason:** none.

**Reported:** 1 · **Unreported:** 1 · **Total:** 2 pages.

`past-paper-questions/index.html` and `past-paper-questions/edexcel/index.html`
both render *"Edexcel A-Level Economics Past Paper Questions | Economics
Academy"* — the master page has taken the board page's title.

**Fixable in code? Yes.** `scripts/build_past_paper_questions.py`, then
regenerate.

---

## D5 — Social-tag and structured-data gaps

**Explains GSC reason:** none.

**Total:** 5 instances across 3 pages.

| Page | Gap |
| --- | --- |
| `privacy.html` | no JSON-LD |
| `revision-notes/index.html` | `og:title` ≠ `<title>` |
| `revision-notes/macro-application/index.html` | no JSON-LD; `og:title` and `twitter:title` ≠ `<title>` |

**Fixable in code? Yes.** Three hand-written files.

---

## D6 — Query-parameter URL proliferation

**Explains GSC reason:** none directly; contributes to crawl budget pressure
behind `crawled-currently-not-indexed`.

**Reported:** 45 · **Unreported:** 194 · **Total:** 239 links → 239 crawlable
URLs behind **7** real pages.

`?topic=` deep links into the six flashcard decks and `?board=…&topic=…` into
`/past-paper-questions/`.

**This is not a duplication defect.** Every target page's hardcoded canonical
names the clean URL, so Google consolidates correctly — verified. It is purely a
crawl-budget cost, and it lands at the worst moment: 239 URLs to fetch and
discard while 340 pages wait to be discovered for the first time.

**Fixable in code? Yes, but it is a functional change**, not a markup fix —
`js/components/flashcards.js:109`, `question-search.js:644` and
`glossary-filter.js:354` read `window.location.search`. Moving to a fragment
would remove the URLs entirely but changes how deep links behave.

**Recommendation: leave it.** Item B3 in `seo/04-decisions.md`.

---

## D7 — Title and description length

**Explains GSC reason:** none.

`title-long` (>60 chars): 286 pages. `description-length` (outside 70–160): 126
pages. Both **run higher on undiscovered pages** — `title-long` at 65.4% vs
28.6%, a 2.3× regression traceable to `build_questions.py` and
`build_past_paper_questions.py` concatenating a full topic name with a board and
a site suffix.

**These are advisory, not defects.** Google truncates the SERP display; it does
not penalise. Every title on the site is unique and descriptive.

**Recommendation: do not bulk-edit 286 titles to chase a character count.** The
work is real and the benefit is cosmetic. Item B4 in `seo/04-decisions.md` if
you want the two generators' title templates shortened.

---

# Group C — Not a code problem

Honest assessment. Nothing here has a technical remedy on GitHub Pages, and
presenting one would be misleading.

## C1 — 47 PDFs "Crawled – currently not indexed", 29 "Duplicate without user-selected canonical"

**76 of your 132 not-indexed URLs are PDFs.** On GitHub Pages a PDF cannot carry
a `rel=canonical`, cannot receive an `X-Robots-Tag`, and cannot be `noindex`ed at
all — there are no custom headers. Google is choosing not to index exam-board
PDFs that exist identically on dozens of other sites. That is a duplication
judgement about content you did not author and cannot differentiate.

**Realistic options:** none that change Google's mind about the PDFs
themselves. The leverage is the *HTML* around them — the four `past-papers/`
board pages that are already ranking well (`/past-papers/edexcel-b/`, 7,214
impressions). Adding the PDFs to a sitemap (your decision, D8 below) helps
discovery of the ~200 Google has never fetched, but will not make a duplicate
PDF indexable.

## C2 — 7 HTML pages "Crawled – currently not indexed"

```
/faq.html                                            crawled 2026-05-12
/about.html                                          crawled 2026-04-03
/contact.html                                        crawled 2026-04-08
/revision-notes/edexcel-theme-1/1-3-2-externalities.html                  2026-04-22
/revision-notes/edexcel-theme-1/1-2-4-supply.html                         2026-04-14
/revision-notes/edexcel-theme-1/1-2-5-price-income-cross-elast-of-supply.html  2026-03-05
/revision-notes/edexcel-theme-1/1-2-3-price-income-cross-elast-of-demand.html  2026-02-24
```

All 7 return 200, self-canonicalise, have unique titles and descriptions, one
`<h1>`, valid JSON-LD, and 600–1,500 words of real content. **There is no
technical defect on these pages.** "Crawled – currently not indexed" here is
Google's quality-and-priority judgement on a site with modest authority — it
crawled them, found nothing wrong, and declined to spend index space.

**Realistic options:** improve site authority over time; strengthen internal
linking to these specific pages (D1's fix helps — the theme hub that links them
will consolidate its own signals); and be patient. Note that `1-2-3-price-income-
cross-elasticities-of-demand.html` was last crawled **2026-02-24, five and a half
months ago** — its status reflects a version of the site that no longer exists.

## C3 — Five near-duplicate AQA↔Edexcel twin pairs

80–87% shingle overlap between e.g. `aqa-a2-macro/2-5-2-supply-side-policies` and
`edexcel-theme-2/2-6-3-supply-side-policies`. **Deliberate** — CLAUDE.md defines a
twin as the page covering the same content on the other board, and they target
different board-specific queries ("AQA supply side policies" vs "Edexcel theme 2
supply side policies").

**Realistic options:** leave them. The alternative is merging board-specific
pages, which would lose the board keyword targeting that is the whole point.
Flagged for transparency, not for action.

## C4 — 20 thin pages

18 of 20 are hub/index pages whose job is navigation, not prose —
`/revision-notes/` at 118 words is a board selector and ranks with 5,791
impressions. Only two genuine content pages are short:

```
249w  revision-notes/aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html
287w  revision-notes/aqa-a2-micro/1-4-1-production-and-productivity.html
```

**Realistic options:** expanding those two is a content decision, not a technical
one, and would need your approval per the standing rule on editing existing
content. Listed in `seo/04-decisions.md` as B5; **no recommendation to act.**

## C5 — 3 "Page with redirect" and 1 "Redirect error"

`http://`, `http://www.` and `https://www.` all 301 to apex HTTPS — **correct**.
`/past-paper-questions` re-tested live: clean HTTP/2 301 to
`/past-paper-questions/`, no chain, no protocol downgrade. Transient. Ground
rule 5: not bugs.

## C6 — 26 "Excluded by noindex" — already fixed, needs no work

Verified live: those AQA pages return 200 with **no robots meta**. Only
`404.html` and `confirmation.html` carry `noindex` anywhere in the repo. Crawl
dates 2026-05-18 → 2026-07-13 all predate commit `203f6bd` (2026-07-30).
**These 26 recover on re-crawl with zero effort** — a fifth of your not-indexed
count clears itself.

---

# Prioritised action list

Ranked by (pages recovered × existing impressions) / effort. Template and
generator fixes rank highest: most pages per edit, and they land before Google's
first crawl of the 419 undiscovered pages.

| # | Action | Group | Pages | Impressions at stake | Effort | Files |
| ---: | --- | :-: | ---: | ---: | :-: | --- |
| 1 | **Fix the 7 `practice-questions` canonicals** | A | 7 hubs + 173 below | first-crawl risk | XS | `build_questions.py` |
| 2 | **Rewrite 1,300 links to canonical form** | **B1** | 458 | **44,809** | M | 458 files + 5 sources |
| 3 | **Fix the 5 link sources** so #2 survives a rebuild | A | — | — | S | 4 generators + `header.html` |
| 4 | **Regenerate `sitemap.xml` as a sitemap index**, git `lastmod`, + PDF sitemap — and stop the generators stamping build dates into it (D3b) | A | 461 + 283 | discovery of 340 unseen pages | M | `sitemap.xml`, `sitemaps/*.xml`, `build_past_paper_questions.py`, `build_questions.py` |
| 5 | **Remove 3 dead PDF links** | A | 1 | — | XS | `past-papers/edexcel-b/index.html` |
| 6 | **Fix the duplicate title** | A | 2 | — | XS | `build_past_paper_questions.py` |
| 7 | **Add JSON-LD + fix og/twitter titles** | A | 3 | — | XS | 3 hand-written files |
| 8 | Shorten generated titles over 60 chars | B4 | 286 | cosmetic | M | 2 generators |
| 9 | Convert `?topic=` to fragments | B3 | 7 | crawl budget | M | 3 JS files |
| 10 | Expand 2 short notes pages | B5 | 2 | — | — | content decision |

**Do 1, 3, 5, 6, 7 first** — they are unambiguous, total under an hour, and
clear the entire top of the at-risk list. **2 and 4 are the value**, and 2 needs
your approval.

---

## Group A — Safe automated fixes, no decision needed

1. `practice-questions` canonicals — `scripts/build_questions.py` (7 pages)
2. The five `/index.html` link sources — 4 generators + `templates/header.html`
3. Remove 3 dead PDF links — `past-papers/edexcel-b/index.html`
4. Duplicate title — `scripts/build_past_paper_questions.py`
5. JSON-LD on `privacy.html` and `revision-notes/macro-application/index.html`
6. `og:title` / `twitter:title` on `revision-notes/index.html` and
   `revision-notes/macro-application/index.html`
7. Regenerate `sitemap.xml` as a sitemap index with git-derived `lastmod`, plus
   `sitemaps/pdfs.xml` (283 PDFs) — you have already chosen this

## Group B — Needs your decision

See `seo/04-decisions.md`. Five items: the 458-file bulk rewrite; the
extensionless-URL duplicate surface; `?topic=` parameters; over-long generated
titles; the two short notes pages.

## Group C — Not a code problem

C1–C6 above. **76 of your 132 not-indexed URLs are PDFs with no available
remedy, and 26 more are a stale report that clears itself.** That is 102 of 132.
The genuinely actionable indexing problems are far smaller than the GSC headline
suggests — and the real opportunity is not in the 132, it is in the **340 pages
Google has never seen.**
