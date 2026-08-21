# Search Console page-indexing audit — 21 August 2026

Read-only analysis. **No site file was changed in this session.** Companion
files: `seo/12-index-fix-actions-2026-08-21.md` (what I can fix in the repo) and
`seo/13-gsc-manual-todo-2026-08-21.md` (what only you can do, in Search
Console).

This builds on the August audit and does not re-open anything settled in
`seo/04-decisions.md`. Where an old decision explains something here, it is
referenced rather than re-argued.

---

## The one-minute version

**Your real published surface is 746 URLs** — 463 HTML pages and 283 PDFs.
Not a number written down anywhere; derived by running
`python3 scripts/verify_published_surface.py` and `python3 scripts/build_sitemap.py --check`
against the committed tree. 744 of those are submitted in the sitemaps; the
other 2 are `404.html` and `confirmation.html`, deliberately kept out.

| | count | share |
| --- | ---: | ---: |
| **Indexed** | **319** | 42.8% |
| Not indexed, some GSC reason | 423 | 56.7% |
| In no GSC export at all | 4 | 0.5% |
| **Total published** | **746** | 100% |

That headline number is misleading on its own, because the PDFs drag it down.
Split it:

| | published | indexed | share |
| --- | ---: | ---: | ---: |
| **HTML pages** | 463 | **308** | **66.5%** |
| PDFs | 283 | 11 | 3.9% |

**Did the sitemap submission help? Yes — emphatically, and more than any other
thing you have done.** On 8 August Google had judged 172 of your published URLs
and indexed 64 of them. Today it has judged 742 and indexed 319. **255 more of
your pages are in Google's index than a fortnight ago.** Practice questions went from
*nothing indexed at all* to 155 of 173; past-paper questions from nothing to 76
of 90; flashcards from nothing to 7 of 7.

**The single most important finding:** the 26 URLs sitting under *"Excluded by
'noindex' tag"* have **no noindex tag on them, and have not had one for over
three weeks.** I fetched all 26 live: every one returns HTTP 200 with no
`<meta name="robots">` and no `X-Robots-Tag` header. Google's verdict is simply
older than your fix — it last crawled these pages between 18 May and 13 July,
and the tags came off between 6 and 30 July. This is not a bug to fix. It is a
recrawl to wait for, and a Search Console validation for it is **already running
as of 21 August** (`13-…`, task 1).

**The second most important finding, and the one you asked about:**
"Discovered — currently not indexed" is 316 URLs and it is **not a defect**. It
means Google has learned the URL exists and has not yet fetched it. Google's own
documentation for this state reads: *"Google wanted to crawl the URL but this
was expected to overload the site. No action needed."* You handed Google 570
published URLs it had never judged, in one go, thirteen days ago. It crawled
roughly 288 of them, indexed 257, and queued the rest. That is a queue, not a
rejection. Confidence: **moderate-to-high** — revised down from "high" once
Crawl stats showed an average response time of 108 ms, which means Google is not
holding back because your site is slow. It is holding back because it has
decided not to spend more crawl here yet. Details, and the alternatives I ruled
out, are in §4.

**And the money question — did any of it earn anything?** Yes. The newly-indexed
pages took **50 clicks and 3,316 impressions from a standing start of zero**,
and the site is up 20% on clicks and 90% on impressions. But your established
hub pages went backwards over the same window — `/revision-notes/` is down 22
clicks and three ranking positions — and I cannot yet separate duplicate
consolidation from the end of exam season. §3a has the numbers and says plainly
what it cannot prove.

**On the PDFs:** submitting them caused one crawl burst on 8–9 August and
indexed nothing. There is no ongoing cost, so **leave `sitemaps/pdfs.xml` alone**
and re-decide on 1 October on the indexing outcome. §7.

**The number that frames everything else:** Googlebot made roughly **3,270
requests to your whole site in 90 days — about four fetches per page in three
months.** That is a low crawl rate, and with an average response time of 108 ms
it is not your hosting causing it. §4.

---

## Where the data is soft

Three caveats that some conclusions rest on. Stated up front rather than buried.

1. **The exports are Google's *example* lists, not a guaranteed census.** Google
   documents that "the list of example URLs in the report is limited to 1,000
   items, and isn't guaranteed to show all URLs in a given status, even when
   less than 1,000 items." Every category here is far below 1,000, and all 746
   published URLs reconcile into exactly one bucket each with only 4 left over —
   which is strong evidence the lists are complete for this property, but it is
   evidence, not a guarantee.

2. **The report lags reality by days.** Every judgement in it is the judgement
   Google made when it last crawled that URL. The `Last crawled` column is
   therefore the single most useful field in the export, and I have used it
   throughout to separate "still true" from "true when Google last looked".
   Everything in §6 marked *stale* depends on this.

3. **"Last crawled = 1970-01-01" is not a date.** It is the Unix epoch — the
   zero value of a timestamp field — meaning *never crawled*. All 316
   "Discovered" rows carry it. Read it as a blank, not as an ancient crawl.

Where I could not determine something, §10 says so.

---

## 1. The true published inventory

Derived from the repo, not from any recorded count.

```
python3 scripts/verify_published_surface.py   → 1096 tracked files are published, exit 0
python3 scripts/build_sitemap.py --check      → exit 0, no WOULD CHANGE lines
```

`build_sitemap.py --check` exiting 0 with no `WOULD CHANGE` lines is the pass
signal: **the committed sitemaps match the filesystem exactly.** Its own output:
`461 pages + 283 PDFs across 7 sitemaps`, with `404.html` and
`confirmation.html` held back for carrying a deliberate noindex.

| Sitemap | URLs | What it holds |
| --- | ---: | --- |
| `sitemaps/core.xml` | 7 | homepage, tutoring, marking, about, contact, faq, privacy |
| `sitemaps/revision-notes.xml` | 179 | revision notes + glossary + diagram galleries |
| `sitemaps/practice-questions.xml` | 173 | your original practice questions |
| `sitemaps/past-paper-questions.xml` | 90 | the real-exam question bank |
| `sitemaps/past-papers.xml` | 5 | the four board hubs + the section hub |
| `sitemaps/flashcards.xml` | 7 | the six decks + hub |
| `sitemaps/pdfs.xml` | 283 | exam-board question papers and mark schemes |
| **submitted total** | **744** | |
| not submitted | 2 | `404.html`, `confirmation.html` (deliberate noindex) |
| **published total** | **746** | 463 HTML + 283 PDF |

`python3 seo/tools/verify_seo.py` passes **14/14**, including "every page has a
self-referencing canonical" (461), "no unintended noindex", "sitemap valid,
complete, canonical-only, no duplicates" (744) and "robots.txt blocks nothing".
**There is no on-page technical defect standing between these pages and the
index.** That matters for §4, because it removes a whole class of explanation.

---

## 2. Reconciliation — every published URL, in exactly one bucket

746 in, 746 out. No URL appears in two GSC categories (checked), and none is
dropped.

| Bucket | URLs | HTML | PDF |
| --- | ---: | ---: | ---: |
| Indexed | 319 | 308 | 11 |
| Discovered — currently not indexed | 316 | 121 | 195 |
| Crawled — currently not indexed | 73 | 6 | 67 |
| Excluded by 'noindex' tag | 26 | 26 | 0 |
| Duplicate without user-selected canonical | 8 | 0 | 8 |
| **In no GSC export at all** | **4** | **2** | **2** |
| **Total** | **746** | **463** | **283** |

### 2a. By sitemap — this is the table that tells the story

| Sitemap | total | indexed | discovered | crawled-NI | noindex | dup | unjudged | **% indexed** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `flashcards` | 7 | 7 | 0 | 0 | 0 | 0 | 0 | **100%** |
| `past-papers` | 5 | 5 | 0 | 0 | 0 | 0 | 0 | **100%** |
| `practice-questions` | 173 | 155 | 18 | 0 | 0 | 0 | 0 | **89.6%** |
| `past-paper-questions` | 90 | 76 | 14 | 0 | 0 | 0 | 0 | **84.4%** |
| `core` | 7 | 5 | 0 | 2 | 0 | 0 | 0 | 71.4% |
| `revision-notes` | 179 | 60 | 89 | 4 | 26 | 0 | 0 | **33.5%** |
| `pdfs` | 283 | 11 | 195 | 67 | 0 | 8 | 2 | **3.9%** |
| not submitted | 2 | 0 | 0 | 0 | 0 | 0 | 2 | — |
| **all** | **746** | **319** | **316** | **73** | **26** | **8** | **4** | 42.8% |

Two things jump out.

**Revision notes is the laggard, at 33.5%** — and it is your best content. 26 of
its 119 unindexed pages are the stale-noindex group, which will clear on
recrawl. The other 89 have never been crawled. Broken down by folder, with
"known to Google on 8 August" alongside:

| Folder | pages | known 8 Aug | indexed | never crawled | stale noindex |
| --- | ---: | ---: | ---: | ---: | ---: |
| `revision-notes/` (3 hubs) | 3 | 3 | 3 | 0 | 0 |
| `edexcel-theme-1` | 23 | 18 | 14 | 5 | 0 |
| `edexcel-theme-2` | 25 | 16 | 16 | 9 | 0 |
| `edexcel-theme-3` | 21 | **2** | 3 | **18** | 0 |
| `edexcel-theme-4` | 22 | 7 | 8 | 14 | 0 |
| `aqa-a2-micro` | 55 | 19 | 7 | 30 | 18 |
| `aqa-a2-macro` | 26 | 9 | 8 | 10 | 8 |
| `glossary` | 3 | 0 | 1 | 2 | 0 |
| `macro-application` | 1 | 0 | 0 | 1 | 0 |

The "known 8 Aug" column tracks the indexed column almost exactly. **Google
indexes what it already knew, and queues what is new to it.** Theme 3 is the
extreme case: Google had seen 2 of 21 pages, and 18 are still queued. This is a
familiarity effect, not a quality judgement — see §4.

**PDFs are at 3.9%, and none of that is new.** All 11 indexed PDFs were already
indexed on 8 August, before `pdfs.xml` existed. §7 deals with them.

### 2b. The 4 published URLs in no GSC export at all — a finding, not a gap

| URL | Why |
| --- | --- |
| `/404.html` | Deliberate noindex. Correct that Google has no verdict. |
| `/confirmation.html` | Deliberate noindex (Formspree thank-you page). Correct. |
| `/marking-examples/annotated-paper-example.pdf` | Only entered a sitemap on 16 August — 5 days ago |
| `/marking-examples/feedback-email-example.pdf` | Same |

**Nothing here is wrong.** The two noindex pages are absent because they are
meant to be, and the two marking-example PDFs are simply too new for Google to
have formed a view. Both were confirmed live at HTTP 200. Re-check the PDFs in
mid-September; if they are still absent then, they have not been discovered and
that would be worth a look.

### 2c. Ghosts — 32 URLs in a GSC export that this site does not publish

Every one traced to source.

| Group | n | Where it came from | Live status today |
| --- | ---: | --- | --- |
| `…/index.html` variants | 14 | The legacy internal-link convention fixed by decision **B1** in `04-decisions.md`. GitHub Pages serves them at 200, so Google indexed them; no published page links to any of them now (verified: 0 `index.html` hrefs in tracked HTML outside `_archive/`, `_working/`) | 200, canonical correctly names the slash form |
| `?topic=` flashcard URLs | 2 | The 239 parameter URLs of decision **B3** ("leave it") | 200, canonical names the clean URL |
| `http://`, `www.` homepage | 3 | GitHub Pages' own protocol and host canonicalisation | single 301 → `https://economicsacademy.co.uk/`, then 200 |
| `/revision-notes/aqa-as-micro/index.html` | 1 | Deleted in commit `747fab8`, 12 May 2026, "removing aqa as level" | 404 |
| `…/aqa-a-micro/4.x.x.html`, `…/aqa-as-micro/3.x.x.html` | 8 | Broken **relative** links inside the old AQA pages (`href="aqa-a-micro/4.1.1.html"` resolving against the wrong folder). No published page contains them now | 404 |
| `…/edexcel-b-…-june-2023-mark-scheme.pdf` | 1 | A link to a mark scheme that was never uploaded; link removed in `5f2d3aa`, 8 Aug | 404 |
| `…/1-2-5-price-income-cross-elasticities-of-supply.html` | 1 | A **stale sitemap entry for a file that never existed**, corrected in commit `203f6bd`, 30 July 2026 | 404 |
| `/past-paper-questions` (no trailing slash) | 1 | Google guessed or followed an external link | clean 301 → `/past-paper-questions/` → 200 |
| `/index.html` | 1 | Same legacy convention; **still indexed alongside `/`** | 200, canonical names `/` |

**18 of the 32 do appear in `seo/01-crawl.csv`** — the live crawl run on
8 August. That is consistent rather than contradictory: the crawl was taken
*before* the B1 link rewrite reached the live site, so it still found the
`…/index.html` twins and the two `?topic=` URLs that your pages were emitting at
the time. Re-crawled today they would not appear, because no published page
links to any of them now. The other 14 — the 404s, the `http://` / `www.`
variants and the slashless `/past-paper-questions` — were not in that crawl
either, which is the expected result for URLs Google remembers but your site has
never emitted.

Two ghosts are worth a second look, because they are **live duplicate pairs that
have not yet consolidated**:

- `/index.html` **and** `/` are both currently indexed. The twin was last
  crawled 2 July, before the link rewrite went live on 8 August.
- `/flashcards/aqa/macro/?topic=2-6-2-trade` **and**
  `/flashcards/aqa/macro/` are both indexed.

Both have correct canonicals pointing at the clean URL. Both should merge on
recrawl. Neither is actionable in the repo — see `12-…` "Not worth doing".

---

## 3. What actually changed between 8 and 21 August

### By category

| Category | 08-08 | 21-08 | change | added | resolved | unchanged |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Indexed | 66 | 321 | **+255** | 258 | 3 | 63 |
| Discovered — currently not indexed | 0 | 316 | **+316** | 316 | 0 | 0 |
| Crawled — currently not indexed | 54 | 74 | +20 | 24 | 4 | 50 |
| Duplicate without user-selected canonical | 29 | 8 | **−21** | 1 | 22 | 7 |
| Alternate page with proper canonical tag | 9 | 15 | +6 | 6 | 0 | 9 |
| Excluded by 'noindex' tag | 26 | 26 | 0 | 0 | 0 | 26 |
| Not found (404) | 10 | 10 | 0 | 0 | 0 | 10 |
| Page with redirect | 3 | 3 | 0 | 0 | 0 | 3 |
| Redirect error | 1 | 1 | 0 | 0 | 0 | 1 |
| **URLs Google knows about** | **198** | **774** | **+576** | | | |

*(These are export-row counts and include the 32 ghosts. Counting only URLs this
site actually publishes, indexed went **64 → 319, up 255**; the two extra rows in
the 8 August indexed figure were `/index.html` and `/past-papers/edexcel/index.html`,
both ghosts. The published-only figures throughout are in §2.)*

### Direction of travel — the answer to your question

You asked whether pages moved from not-indexed to indexed, or whether Google
simply discovered a lot and parked them. It is overwhelmingly the second, plus a
very large amount of *straight-to-indexed*:

| Movement | URLs |
| --- | ---: |
| **not previously known → indexed** | **257** |
| **not previously known → discovered, not indexed** | **314** |
| not previously known → alternate page (correct behaviour) | 5 |
| duplicate without canonical → crawled, not indexed *(all PDFs)* | 22 |
| indexed → crawled, not indexed *(a regression)* | 2 |
| crawled, not indexed → discovered *(both PDFs)* | 2 |
| **not indexed → indexed** | **1** |
| indexed → alternate page *(the duplicate merging — a win)* | 1 |
| crawled, not indexed → duplicate without canonical | 1 |
| *unchanged in the same category* | 169 |

**Only one URL was rescued from a not-indexed state** — `/faq.html`, crawled
14 August and now indexed. Everything else that got indexed was new to Google.
So the honest statement is:

> The sitemap submission did not fix anything that was already broken. It made
> Google aware of 570 published URLs it had never judged, and Google indexed 257
> of them outright. That is what a sitemap is for, and it worked.

### The crawl burst you noticed

Counting URLs by the date Google last fetched them:

```
2026-08-08    10
2026-08-09   146     ← the burst
2026-08-10    76     ←
2026-08-11    14
2026-08-12 – 18   3–12 per day
```

288 URLs were crawled on or after 7 August. **Every single one was an HTML page
or a ghost — not one PDF.** The most recent PDF crawl anywhere in the export is
6 August. Hold that thought for §7.

### The two regressions, and one quiet win

- `/past-papers/aqa/…/aqa-as-level-economics-paper-1-specimen-question-paper.pdf`
  went indexed → crawled, not indexed. A PDF; consistent with §7.
- `/revision-notes/edexcel-theme-1/1-1-6-types-of-economies.html` went indexed →
  crawled, not indexed. **Last crawled 9 July; the page was rebuilt on
  13 August.** Google's verdict predates the current page. Worth watching, not
  worth acting on yet.
- `/past-papers/edexcel/index.html` moved from **indexed** to **alternate page
  with proper canonical tag**. That is a duplicate pair collapsing into one URL
  — precisely the outcome `06-gsc-checklist.md` Step 3 predicted, and the first
  hard evidence that the B1 link rewrite is working.

All eight URLs you were told to Request Indexing for on day 0 are now indexed at
their canonical form, 8/8.

---

## 3a. What it earned — the Performance data (added later on 21 August)

`06-gsc-checklist.md` Step 6 flagged that the one thing this audit could not do
was say whether newly-indexed pages actually earn anything. That export now
exists at `seo/gsc-exports/21-08-2026/performance-28d-compare/`.

**Read the window before the numbers.** GSC's "Last 28 days" runs to about
18 August, so roughly **24 July – 18 August**. The sitemap landed on 8 August.
**Only about 11 of the 28 days are post-submission**, and the comparison period
(late June to late July) is a different point in the A-Level year. Every figure
below understates the effect and is confounded by season. Treat the *direction*
as informative and the magnitude as provisional.

### Site totals

| | previous 28d | last 28d | change |
| --- | ---: | ---: | ---: |
| Clicks | 206 | **248** | **+42 (+20%)** |
| Impressions | 13,612 | **25,851** | **+12,239 (+90%)** |

*(Site totals from `Devices.csv`. `Pages.csv` sums about 3% higher — normal GSC
aggregation difference between dimensions, not an error in either.)*

### Did the newly-indexed pages earn anything? Yes.

Splitting every row of `Pages.csv` by what Search Console said about that URL on
8 August versus today:

| Group | rows | clicks | impressions |
| --- | ---: | ---: | ---: |
| **Newly indexed** (absent on 8 Aug → indexed now) | 230 | **0 → 50** | **0 → 3,316** |
| Already indexed on 8 August | 63 | 196 → 195 | 13,163 → **22,621** |
| Still not indexed (`alternate page`, `crawled — not indexed`) | 19 | 10 → 3 | 984 → 668 |

**Fifty clicks and 3,316 impressions from pages that had literally none.** By
section: practice-questions 0 → 28 clicks and 0 → 1,299 impressions;
past-paper-questions 0 → 17 and 0 → 1,381; flashcards 0 → 0 and 0 → 62. Those
three sections did not exist in Google's index a fortnight ago.

### The uncomfortable half

**Your established hub pages lost ground.**

| Page | clicks | avg. position |
| --- | ---: | ---: |
| `/revision-notes/` | 84 → **62** | 9.13 → **12.14** |
| `/past-papers/ocr/` | 14 → **2** | 14.47 → **22.66** |
| `/past-papers/aqa/` | 10 → **2** | 20.56 → **24.15** |
| `/past-papers/edexcel-b/` | 11 → 10 | 11.04 → **15.98** |

The `past-papers` section as a whole went from 35 clicks to 16. The 63
already-indexed pages gained 9,458 impressions and **lost one click** between
them — they are being shown for far more searches, at worse average positions.

**I cannot tell you how much of this is consolidation and how much is the exam
calendar**, and I am not going to pretend otherwise. Both explanations fit:

- *Consolidation* is what `06-gsc-checklist.md` Step 3 predicted almost exactly:
  "Impressions may dip for 1–3 weeks on the ten split pairs while Google merges
  each pair into one URL. Combined clicks should recover and then exceed the
  previous total."
- *Seasonality* is at least as plausible. The comparison window is late June to
  late July; the current window is late July to mid-August. UK A-Level exams
  finish in June and results day was 13 August. Past-paper demand is at its
  annual floor in this window, which is exactly where the losses are
  concentrated.

The query data cannot settle it either: `Queries.csv` accounts for only **57 of
the 248 clicks**, because Search Console omits queries below a privacy
threshold. The page-level movements happen in the anonymised tail.

**What would settle it:** a year-on-year comparison — the same 28 days in 2025 —
if the property has that history. That is task 7a in `13-…`. Failing that, the
October read.

### What I would take from this today

The site gained 42 clicks net. The new sections contributed +50, the old hubs
gave back some of it, and the balance is positive. Impressions nearly doubled.
Nothing here says the submission was a mistake. But **`/revision-notes/` is your
second-biggest page and it is down 22 clicks and three positions**, and that is
a watch item, not a rounding error. If it has not recovered by the October read,
it stops being consolidation noise and becomes a question in its own right.

---

## 4. Diagnosis: why 316 URLs are "Discovered — currently not indexed"

This is the biggest category and the one you care most about, so I worked
through the candidate causes and tried to kill each one with evidence from your
repo rather than general SEO advice.

### First, what the state actually means

Google has the URL on a list. It has **not fetched the page**. Nothing on the
page — not its words, not its markup, not its title — can be the reason, because
Google has not read any of it. That single fact eliminates most of what the
internet will tell you to do about this status. Whatever is happening is
happening in Google's *scheduler*, before your page is ever involved.

Google's own description of this state, from the Page Indexing report
documentation: *"Google wanted to crawl the URL but this was expected to
overload the site. No action needed."*

### Candidate causes, ruled in or out

**Thin, templated or near-duplicate generated content — RULED OUT.**
If templating were the problem, the most templated section would suffer most.
It suffers least. `practice-questions/` is 173 pages from one generator with an
identical shell, and it is **89.6% indexed**. Word counts do not separate the
groups either:

| Section | indexed (median words) | discovered (median words) |
| --- | ---: | ---: |
| revision-notes | 808 | **831** |
| practice-questions | 1,938 | **2,006** |
| past-paper-questions | 718 | **752** |

In every section the queued pages are *slightly longer* than the indexed ones.
There is no thinness signal here. (The two genuinely short notes pages of
decision **B5** are a separate, already-settled matter; neither is in this
bucket.)

**Internal linking depth and orphan pages — RULED OUT.**
`python3 seo/tools/link_graph.py`, run today:

```
pages (nodes): 461
depth histogram (static):   0:1, 1:29, 2:350, 3:81
unreachable from homepage:  0
pages at depth >= 4:        0
pages with <3 inbound links: 3
```

Maximum depth 3, no orphans, three pages with fewer than three inbound links and
all three explained in `07-link-graph.md`. **Note that `07-link-graph.md`'s
"static vs rendered" split no longer applies**: it was written when the header
and footer were injected at runtime by JavaScript. Since Wave 2 Phase 7 they are
baked into all 463 pages, so the two graphs are now identical — which is why
`link_graph.py` prints the same histogram twice. The nav is visible to a crawler
that never runs JavaScript. Nothing is hiding behind JS.

**Sitemap size and structure — RULED OUT.**
Seven child sitemaps behind an index, largest 283 URLs, all well inside the
50,000-URL / 50 MB limits. `verify_seo.py` assertion 9 passes: valid, complete,
canonical-only, no duplicates. And within `revision-notes.xml` the queued and
indexed pages carry the *same* `<lastmod>` (2026-08-13) and the *same*
`<priority>` (0.8), so nothing in the sitemap distinguishes them.
Incidentally, this is a good demonstration that Google ignores `<priority>`
entirely: revision-notes pages are 0.8 and 33.5% indexed; practice-questions are
0.7 and 89.6% indexed.

**Robots, headers, HTTP status — RULED OUT.**
I fetched a sample of 15 queued HTML pages and 8 queued PDFs live. All 23
returned HTTP 200, no redirect, no `X-Robots-Tag` header, correct
self-referencing canonical, no robots meta. `robots.txt` is three lines and
blocks nothing.

**PDFs stealing crawl budget from your HTML — RESOLVED, and I had a fact wrong.**

> ⚠️ **Correction.** I wrote this morning that "Google has not crawled a single
> PDF since 6 August", taking the `Last crawled` column of the page-indexing
> export at face value. **That was wrong.** The Crawl stats time series shows a
> large PDF crawl on **8–9 August**. The page-indexing report simply had not
> caught up — it lags Crawl stats by days, which is caveat 2 in "Where the data
> is soft", applied to my own conclusion rather than to yours.

What the PDF time series actually shows (Crawl stats → By file type → PDF,
90 days: **491 requests, 379 MB, 211 ms average**):

- a flat baseline of roughly **4 requests a day**;
- one earlier bump around 16 June (~35);
- a **spike to about 128 requests in a day on 8–9 August** — the same two days
  as the HTML burst, and unmistakably `pdfs.xml` being processed;
- then a **fall back to baseline**, near zero from about 12 August onward.

Estimating the spike at ~140 requests above baseline, that is **roughly 29% of
all PDF crawling in the 90-day window, compressed into two days.** So:

| Question | Answer |
| --- | --- |
| Did submitting `pdfs.xml` cause a crawl? | **Yes** — about 140 extra requests |
| Was it a one-off or an ongoing drain? | **One-off.** Back to baseline within days |
| Is it costing crawl budget *now*? | **No** |
| What did those 140 requests buy? | **Nothing. Zero new PDFs indexed.** |

**So the cost is real, already paid, and not recurring.** The conclusion I
reached this morning survives, but the reasoning that got me there did not.

**A useful number falls out of this.** If 491 PDF requests are 15% of the total,
Googlebot made roughly **3,270 requests to your whole site in 90 days — about 36
a day** for a site of 746 URLs. HTML would be ~1,870 of those, which is about
**four fetches per page in three months.** That is a low crawl rate, and it is
the clearest quantitative evidence in this audit that crawl *demand* is the
binding constraint. (Derived from a rounded 15%, so treat it as an order of
magnitude, not a measurement.)

**Did the PDF spike displace HTML crawling?** Probably not much, and I cannot
prove it either way. Displacement requires a capacity ceiling, and the 108 ms
site-wide response time says there was no ceiling being hit — Googlebot spiked to
well over 100 requests a day when it chose to. Under a demand constraint, Google
decides per URL whether a fetch is worth making; it does not run down a fixed
daily allowance. The honest position is that the 140 PDF requests were probably
additional rather than substitutive.

**Crawl capacity is NOT the limit — and that matters more than the PDF question.**
Crawl stats reports an **average response time of 108 ms**. Google's stock
explanation for "Discovered — currently not indexed" is that crawling "was
expected to overload the site". At 108 ms on static files behind a CDN, that is
plainly not what is happening here. So the constraint is not how much Googlebot
*can* fetch from you — it is how much it *wants* to. That is crawl **demand**,
which is a function of how valuable Google currently judges the site, not of
your hosting. See the confidence note below, which I have revised down because
of this.

**Crawl budget and site authority — RULED IN, as the mechanism.**
"Crawl budget" is just the rate at which Google is willing to fetch from your
site. It is set mostly by how fast your server responds and how much Google
thinks the site is worth fetching. A single-author site on a domain Google had
crawled fewer than 200 URLs of is at the modest end of that. Google will not
fetch 570 new URLs in a fortnight for such a site; it fetched about 288 and
queued the rest. That is the mechanism, and it is not something you can
configure.

**A sudden volume of new URLs from one submission — RULED IN, as the trigger.**
On 8 August, commit `b7161e6` replaced a flat 461-URL sitemap with an index
covering 744 URLs, and added the 283 PDFs to a sitemap for the very first time.
Google went from knowing 198 URLs to knowing 774 in thirteen days. The
"Discovered" bucket did not exist in the 8 August export at all; it now holds
316 URLs, **314 of which Google had never listed in any state before.**

### Primary cause, and confidence

> **Primary cause: crawl scheduling after a large one-off discovery event.**
> You quadrupled the number of URLs Google knew about, overnight, on a site
> whose crawl rate is modest. Google crawled what it could — about 288 URLs,
> concentrated on 9–10 August — indexed 257 of them, and put the remaining 316
> in a queue. The pages it prioritised are the ones it already knew (see the
> "known 8 Aug" column in §2a), which is exactly how a crawl scheduler behaves.
>
> **Confidence: moderate-to-high** for the HTML (121 URLs) — revised down from
> "high" after the Crawl stats check. Everything else was tested and eliminated;
> the timing, the volume, the familiarity pattern and Google's own documented
> description of the state all point the same way. What pulls it down is the
> 108 ms response time: because capacity is clearly not the constraint, this is
> Google choosing not to spend crawl here, and *choosing* is less certain to
> resolve itself with time than *queuing* is. The October read distinguishes
> them — a queue drains, a judgement does not.
>
> **Confidence: high, different cause** for the PDFs (195 URLs). Those are not
> queued because Google is busy — they are queued because Google has already
> seen 86 of your PDFs, indexed 11, and evidently has little appetite for the
> rest. See §7.

**And yes — this is normal behaviour for a new bulk submission, and it will
partly resolve itself with time.** I am not going to manufacture a fix for it.
The word doing the work in that sentence is **partly**: the 108 ms finding above
means I would no longer bet on *all* 121 draining on their own.
Google's documentation says "no action needed" for this state, and on the
evidence here that is correct. Expect the 121 HTML URLs to drain over roughly
4–8 more weeks. If a large number are still queued in mid-October, *that* is the
point at which it becomes a site-authority question rather than a queue.

There is one thing worth doing that is not "wait", and it is in `12-…`: the 89
queued revision-notes pages are your strongest content sitting behind your
weakest crawl coverage, and there are cheap ways to raise their priority in the
queue without touching a single published URL.

---

## 5. Live verification — where GSC and reality disagree

I fetched **121 URLs** live (every URL in each small category, plus samples of
the large ones), recording HTTP status, the full redirect chain,
`<link rel="canonical">`, `<meta name="robots">` and any `X-Robots-Tag` header.
Requests were rate-limited to roughly one per half-second.

| Category checked | n | Live result | Agrees with GSC? |
| --- | ---: | --- | --- |
| Excluded by 'noindex' tag | 26 | **200, no robots meta, no X-Robots-Tag** | ❌ **contradicts** |
| Discovered — not indexed (HTML) | 15 | 200, self-canonical, no robots meta | ✅ |
| Discovered — not indexed (PDF) | 8 | 200 | ✅ |
| Crawled — not indexed (HTML) | 6 | 200, self-canonical | ✅ (but see below) |
| Crawled — not indexed (PDF) | 8 | 200 | ✅ |
| Duplicate without canonical (PDF) | 8 | 200, **no way to declare a canonical** | ✅ |
| Indexed (HTML) | 10 | 200, self-canonical | ✅ |
| Indexed (PDF) | 4 | 200 | ✅ |
| Not found (404) ghosts | 10 | 404 (serving `404.html`, which is noindex) | ✅ |
| Alternate page ghosts | 15 | 200, canonical names the slash form | ✅ |
| Page with redirect ghosts | 3 | single 301 → apex https, then 200 | ✅ |
| Redirect error ghost | 1 | **single clean 301 → 200** | ❌ **contradicts** |
| Not judged | 4 | 200 | n/a |

**No `X-Robots-Tag` header was found anywhere on the site.** Not one. I also
took a full header dump on two URLs (one PDF, one HTML page): GitHub Pages' and
Fastly's own headers only. There is nothing site-controlled in the response
headers, because GitHub Pages offers no way to set any.

### Contradiction 1 — the 26 "noindex" pages

Every one of the 26 is live at 200 with no robots directive of any kind. Cross-
referencing each page's GSC crawl date against the commit that removed its
noindex tag:

| | |
| --- | --- |
| GSC last-crawled range | 2026-05-18 → **2026-07-13** |
| noindex removal commit range | **2026-07-06** → 2026-07-30 |
| Pages where the removal came *after* Google's last crawl | **26 of 26** |

Not one of these pages has been crawled since the tag came off. §8 has the full
trace.

### Contradiction 2 — the "Redirect error"

`https://economicsacademy.co.uk/past-paper-questions` (no trailing slash):

```
HTTP/2 301
location: https://economicsacademy.co.uk/past-paper-questions/
HTTP/2 200
```

One hop, no loop, no protocol downgrade, no chain. GSC last crawled it on
5 August. Whatever it hit then, it does not hit now. No published page links to
the slashless form (checked: zero `href="/past-paper-questions"` in tracked
HTML), so nothing on your side is generating it.

### A near-contradiction worth noting

All six HTML pages under "Crawled — currently not indexed" have been **edited
since Google last crawled them**:

| Page | GSC last crawled | Last commit |
| --- | --- | --- |
| `/about.html` | 2026-04-03 | 2026-08-21 |
| `/contact.html` | 2026-04-08 | 2026-08-16 |
| `/revision-notes/edexcel-theme-1/1-1-6-types-of-economies.html` | 2026-07-09 | 2026-08-13 |
| `/revision-notes/edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html` | 2026-02-24 | 2026-08-13 |
| `/revision-notes/edexcel-theme-1/1-2-4-supply.html` | 2026-04-14 | 2026-08-13 |
| `/revision-notes/edexcel-theme-1/1-3-2-externalities.html` | 2026-04-22 | 2026-08-13 |

`/about.html` and `/contact.html` were last looked at by Google **four and a
half months ago**, before your August rewrite of both. Their "not indexed"
verdict describes pages that no longer exist in that form. That is the single
cheapest win available to you and it is task 3 in `13-…`.

---

## 6. Every not-indexed reason, in plain English

Eight reasons appear in the 21 August export. One section each.

First, two terms I will use throughout, defined once:

- **Crawl** — Google fetching the page, the way your browser does.
- **Index** — Google storing the page so it can appear in search results. A page
  can be crawled and not indexed. It cannot be indexed without being crawled.
- **Canonical** — a line in a page's HTML (`<link rel="canonical" href="…">`)
  saying "if you find several URLs showing this content, this one is the real
  address". Yours are all correct; `verify_seo.py` assertion 3 checks all 461.

---

### 6.1 Discovered — currently not indexed · 316 URLs

**What Google means.** "I know this URL exists. I have not fetched it yet."
Nothing has been read, so nothing has been judged.

**Which of your URLs.** 195 PDFs, 89 revision-notes pages, 18 practice-questions
pages, 14 past-paper-questions pages. Full list: appendix A1.1 and A2.1.

**Real problem, expected behaviour, or a URL that doesn't exist?** This one
splits, and the split matters:

- **121 HTML pages — expected behaviour.** A queue, working through itself.
- **195 PDFs — expected behaviour, different reason.** Google has already
  crawled 86 of your PDFs and indexed 11. It is not short of information about
  what your PDFs are. See §7.

**What causes it here.** §4: a fourfold increase in known URLs in thirteen days
against a modest crawl rate.

**What would fix it, and is it worth it.** Nothing in the repo fixes it
directly, and Google's documentation says no action is needed. Two things
genuinely help at the margin, both in `12-…`: keep the site's crawl rate healthy
(it already is), and give the 89 queued revision-notes pages stronger internal
signals so the scheduler reaches them sooner. **Worth doing: the second one,
modestly. Worth doing: nothing else.** The rest is waiting.

---

### 6.2 Crawled — currently not indexed · 74 URLs (73 published + 1 ghost)

**What Google means.** "I fetched this page, read it, and chose not to store
it." No technical fault — a judgement about whether the page is worth keeping.

**Which of your URLs.** 67 PDFs, 6 HTML pages, plus one ghost. Appendix A1.2,
A2.2, A4.

**Real problem, expected, or non-existent?** All three are present here:

| Group | n | Verdict |
| --- | ---: | --- |
| PDFs | 67 | **Expected.** Third-party exam-board documents that exist identically on dozens of sites. §7. |
| `/about.html`, `/contact.html` | 2 | **Stale verdict.** Both rewritten since Google last looked (April). `/contact.html` at 343 words is genuinely thin, and search engines routinely decline to index contact pages — that part is normal. |
| 4 Edexcel Theme 1 notes pages | 4 | **Stale verdict.** All rebuilt 13 August; Google's judgement is from February–July. |
| `…/1-2-5-price-income-cross-elasticities-of-supply.html` | 1 | **A URL that does not exist.** A phantom sitemap entry, corrected 30 July in `203f6bd`. Live: 404. |

**What causes it here.** For the PDFs, duplication with other sites. For the six
HTML pages, a verdict older than the page.

**What would fix it, and is it worth it.** For the six HTML pages: a recrawl,
which you can ask for directly (`13-…` task 3). **Worth doing — it costs five
minutes.** For the PDFs: nothing available. For the phantom URL: nothing; it is
correctly a 404 and Google will drop it.

---

### 6.3 Excluded by 'noindex' tag · 26 URLs

**What Google means.** "The last time I fetched this page it carried an
instruction not to index it, so I have not." (Newer Search Console wording:
*URL marked 'noindex'*.)

**Which of your URLs.** 26 AQA A2 revision-notes pages — 18 micro, 8 macro.
Full list with dates: appendix A1.3.

**Real problem, expected, or non-existent?** **A stale verdict on 26 real,
finished, indexable pages.** Not one currently carries a noindex tag.

**What causes it here.** A deliberate placeholder convention you used while
writing the AQA notes. Each stub carried:

```html
<!-- ============================================================ -->
<!-- TODO: REMOVE the noindex tag below once the revision notes  -->
<!-- for this page have been written, so it can be indexed.      -->
<!-- ============================================================ -->
<meta name="robots" content="noindex" />
```

You removed each tag as you finished each page, across July 2026. Google has not
been back since. §8 has the full per-file trace.

**What would fix it, and is it worth it.** Nothing in the repo — the fix
happened three weeks ago. What is needed is a recrawl, and Search Console has a
button for exactly this. **Worth doing: yes, top priority.** These are 26 pages
of your own original A-Level economics writing sitting outside the index for no
reason. `13-…` task 2.

---

### 6.4 Duplicate without user-selected canonical · 8 URLs

**What Google means.** "This page looks like a copy of something else, and it
does not tell me which address is the real one, so I picked one myself and kept
that instead."

**Which of your URLs.** 8 exam-board PDFs — 4 OCR, 2 AQA, 1 Edexcel, 1 Edexcel B.
Appendix A2.3.

**Real problem, expected, or non-existent?** **Expected, and unfixable on
GitHub Pages.** A PDF has no HTML `<head>`, so the only way to give it a
canonical is an HTTP `Link:` response header, and GitHub Pages gives you no way
to set response headers. Confirmed live today with a full header dump on one of
these PDFs: GitHub's and Fastly's own headers only, no `Link:`, nothing
site-controlled.

**What causes it here.** Identical exam-board PDFs hosted on many sites.

**What would fix it, and is it worth it.** Nothing available. **Not worth
pursuing.** Note this category *fell* from 29 to 8: 22 of those PDFs were
reclassified into "Crawled — currently not indexed". Same outcome, different
label; not an improvement, just Google changing its mind about the reason.

---

### 6.5 Alternate page with proper canonical tag · 15 URLs

**What Google means.** "This URL is a duplicate, it correctly tells me which
address is the real one, and I have indexed that one instead."

**Which of your URLs.** None. All 15 are ghosts: 14 `…/index.html` twins and one
`?topic=` flashcards URL.

**Real problem, expected, or non-existent?** **Expected — this is a success
state.** It is Google saying "understood, I will use the other one".

**What causes it here.** GitHub Pages serves `/x/index.html` at 200 as well as
`/x/`, so both addresses work; your canonical tags name the slash form; Google
obeys.

**What would fix it, and is it worth it.** **Nothing, and it needs no fix.**
`06-gsc-checklist.md` Step 3 predicted this count would rise before it falls, as
Google re-crawls each old twin and learns it is now unlinked. It has: 9 → 15.
That is the B1 link rewrite working, not failing.

---

### 6.6 Page with redirect · 3 URLs

**What Google means.** "This address forwards somewhere else, so I indexed the
destination."

**Which of your URLs.** None — three ghosts:
`http://economicsacademy.co.uk/`, `http://www.economicsacademy.co.uk/`,
`https://www.economicsacademy.co.uk/`.

**Real problem, expected, or non-existent?** **Expected and correct.** These are
GitHub Pages' own automatic http→https and www→apex redirects. Verified live:
each is a single 301 to `https://economicsacademy.co.uk/`.

**What would fix it, and is it worth it.** Nothing to fix. Leave alone
permanently.

---

### 6.7 Redirect error · 1 URL

**What Google means.** "I followed a redirect and something went wrong — a loop,
a chain that was too long, or a malformed response."

**Which of your URLs.** `/past-paper-questions` (no trailing slash). A ghost —
your site does not publish or link this form.

**Real problem, expected, or non-existent?** **Stale.** Live today it is one
clean 301 to `/past-paper-questions/`, then 200. Last crawled 5 August.

**What causes it here.** Unknown, and I cannot determine it from the data
available. The most likely explanation is a transient fetch failure on
5 August. Nothing in the repo produces this URL.

**What would fix it, and is it worth it.** Nothing to fix — it already works.
It needs a recrawl to clear. You have already requested validation on it; see
`13-…` task 1.

*One important nuance, since it bears on every recommendation in `12-…`:*
GitHub Pages **does** emit two kinds of redirect automatically — protocol/host
canonicalisation (§6.6) and this trailing-slash 301. What it does **not** offer
is any way for you to define a redirect of your own. So "redirect the old URL to
the new one" remains unavailable, exactly as `CLAUDE.md` rule 7 states.

---

### 6.8 Not found (404) · 10 URLs

**What Google means.** "This address returns 'page does not exist'."

**Which of your URLs.** None — all 10 are ghosts. Appendix A4.

**Real problem, expected, or non-existent?** **All ten are URLs that do not
exist and should not.** Nine belong to the AQA AS section you deleted in May
2026 or to broken relative links inside it; the tenth is an Edexcel B mark
scheme that was never uploaded, whose link you removed on 8 August.

**What causes it here.** Google remembers URLs for a long time after they stop
existing. All 10 return a correct 404 serving your custom `404.html`, which
itself carries `noindex, nofollow` — the right arrangement.

**What would fix it, and is it worth it.** **Nothing, and do not try.** The only
"fixes" available would be creating stub pages at correctly-deleted URLs — which
`04-decisions.md` already ruled out — or redirecting them, which GitHub Pages
cannot do. Google drops persistent 404s from the report by itself over a few
months. **Do not run a validation on this issue**; it would fail, because
validation re-checks the URL's response code and that code is correctly 404.
This repeats the advice in `06-gsc-checklist.md` Step 4 and it still holds.

---

## 7. The PDFs — one recommendation

### What the evidence says

| | |
| --- | --- |
| PDFs published | 283 |
| In `sitemaps/pdfs.xml` since | **8 August 2026** (commit `b7161e6`) — first time ever |
| Indexed | **11** (3.9%) |
| Indexed *before* the sitemap existed | **11 of 11** |
| Crawled by Google, ever (distinct URLs in the page-indexing export) | 86 |
| **Crawl requests on 8–9 August, when `pdfs.xml` was processed** | **~140 above baseline** |
| **New PDFs indexed as a result** | **0** |
| PDF crawl rate since ~12 August | back to baseline, ~4/day |
| Boards with any PDF indexed | AQA only |
| Mark schemes indexed, any board | **0** |
| Traffic, older baseline (`seo/performance-pages.csv`) | 89 clicks, 6,808 impressions — 7.2% of clicks, 9.7% of impressions |
| **Traffic, last 28 days** (`performance-28d-compare/Pages.csv`) | **4 clicks, 511 impressions — 1.6% of clicks, 1.9% of impressions** |
| Change in PDF impressions over that window | **1,305 → 511, −61%**, while the site rose +90% |
| Share of Googlebot's crawl requests (90 days) | **15%** |

Three things follow. First, **the sitemap did not deliver any of the PDF
traffic**: all eleven indexed PDFs got there before `pdfs.xml` existed, found
through the links on your past-papers hub pages. Second, **the traffic case is
much weaker than it looked this morning.** I originally argued the PDFs earn
7.2% of your clicks, using the older `performance-pages.csv` baseline. On the
last 28 days they earn **1.6% of clicks and 1.9% of impressions**, and their
impressions **fell 61%** while the rest of the site rose 90%. Some of that is
the exam calendar — past-paper demand bottoms out in July and August — but it is
no longer true to say these files are pulling a tenth of your visibility.

Third, **submitting them cost you one burst of crawl and bought nothing.**
The Crawl stats time series (task 6a) shows a spike to ~128 PDF requests a day on
8–9 August — `pdfs.xml` being processed — then a fall back to a ~4/day baseline
within days. About 140 requests above baseline, and **zero new PDFs indexed as a
result.** §4 has the detail, including a correction to a claim I got wrong this
morning.

### My recommendation

> **Leave `pdfs.xml` exactly as it is. Re-decide on 1 October, on the indexing
> outcome alone.**

This is where I started this morning, though the reasoning has changed under it
and I went round the houses to get back. The argument now:

- **The crawl cost is real but sunk.** ~140 requests, spent on 8–9 August.
  Removing the sitemap today cannot recover them.
- **There is no ongoing cost.** PDF crawling has been at baseline since about
  12 August. `pdfs.xml` is not currently taking anything from the 121 queued
  HTML pages.
- **So removing it now buys nothing** except a tidier coverage report — and
  that is already solved by the per-sitemap filter (task 5).
- **The traffic case for keeping it is weak** — 1.6% of clicks on current data,
  down from the 7.2% I quoted this morning off an older baseline — but "weak
  benefit, zero cost" still nets out in favour of leaving it alone.

**What would change my mind, and when.** On 1 October, if `sitemaps/pdfs.xml`
still shows 11 of 283 indexed, then eight weeks and one crawl burst will have
produced nothing, and I would remove it then — not to save crawl, but because a
sitemap should list URLs you expect Google to index, and 3.9% is not that.

**One thing to watch out for in the meantime:** if you add more PDFs, expect
another burst like 8–9 August when Google reprocesses the sitemap. That is not a
reason to avoid adding them, just a reason not to be alarmed by the graph.

The other cost of keeping them is that they make your coverage numbers
unreadable — 195 of the 316 "Discovered" URLs are PDFs, and they drag the
headline indexed rate from a healthy 66.5% (HTML) down to 42.8% (everything).
But that problem is already solved by the structure you built on 8 August:
Search Console lets you filter the Pages report **by individual sitemap**, so
you can read `revision-notes` and `practice-questions` without the PDFs in the
way. That is `13-…` task 5, and it costs two clicks rather than a code change.

`12-…` Action 3 records exactly what the removal involves, so it is ready to run
in October if the indexing outcome has not moved.

**If you decide to remove them anyway, here is exactly what it costs.** Not
much, and less than you might fear:

- **You would not lose the 11 indexed PDFs.** Taking a URL out of a sitemap does
  not remove it from the index. They stay, and they keep their links from the
  past-papers hub pages.
- **You would not lose the traffic they earn**, for the same reason — currently
  4 clicks and 511 impressions in 28 days.
- **You would lose the fastest discovery route for PDFs you add in future.** New
  papers would be found via the hub-page links instead — slower, but it is how
  the current 11 were found in the first place.
- **No URL would move or disappear**, so it is not a breaking change. The PDFs
  stay published at the same addresses.

I want to be explicit about one thing I did *not* weigh heavily. You noted these
are third-party exam-board documents you did not write. That is true, and it is
why Google indexes so few of them — but it is not a reason to stop *submitting*
them. Hosting them is legitimate and useful to your students; Google simply
prefers the exam board's own copy. That is a duplication judgement, and it is
the same conclusion `03-diagnosis.md` group C reached.

---

## 8. Every noindex in the repo, traced

You said you do not remember choosing a noindex on 25 pages. **You did not.**
There is no noindex on any of them today, and there has not been since 30 July.

### What exists in the repo right now

An exhaustive search of every tracked file for `noindex`, `content="none"`,
`noarchive`, `nosnippet` and `name="googlebot"` — across HTML, the generators,
the templates and the JavaScript — returns exactly **two** robots meta tags on
published pages:

| File | Tag | Deliberate? |
| --- | --- | --- |
| `404.html:19` | `<meta name="robots" content="noindex, nofollow" />` | **Yes, unambiguously.** A "page not found" page must never be indexed. |
| `confirmation.html:19` | `<meta name="robots" content="noindex, nofollow" />` | **Yes, unambiguously.** The Formspree thank-you page; indexing it would put "thanks for your enquiry" in search results. |

Both are registered as intentional in three independent places, which is why no
check has ever flagged them:

- `seo/tools/inventory.py:36` — `DELIBERATE_NOINDEX = {"404.html", "confirmation.html"}`
- `scripts/build_sitemap.py` — excludes noindex pages from the sitemap; prints
  `excluded (noindex): 404.html, confirmation.html` on every run
- `scripts/verify_page_shell.py:234` — records them as the two exceptions

`seo/tools/verify_seo.py` assertion 7, "no unintended noindex", **passes**.

**Nothing else in the repo emits a robots directive.** Not `page_shell.py`, not
`templates/header.html` or `footer.html`, not any of the eight generators, not
any hand-written page, and no JavaScript. There is no `X-Robots-Tag` anywhere,
and there could not be — GitHub Pages does not allow custom response headers.

### Where the 26 came from

The AQA A2 notes were written as stubs first and filled in later. Each stub
carried a noindex with a TODO comment beside it. You removed each tag in the
commit that finished each page:

| Commit | Date | Pages finished |
| --- | --- | ---: |
| `2dd6e06` 1-1-3 done | 2026-07-06 | 1 |
| `a089166` 1.1 done for AQA | 2026-07-06 | 2 |
| `143ca21` 1.3 done | 2026-07-06 | 1 |
| `6732a5f` 1.3 aqa done | 2026-07-17 | 2 |
| `0d93eb4` 1.4 aqa done | 2026-07-17 | 2 |
| `8645817` 1.5 done aqa | 2026-07-19 | 4 |
| `eb443f5` 1.6 aqa done | 2026-07-22 | 4 |
| `8c5e1db` 2.2 aqa done | 2026-07-29 | 3 |
| `1282621` 2.1, 2.2, 2.5 done | 2026-07-29 | 3 |
| `e6bbb5e` AQA micro done! | 2026-07-29 | 2 |
| `a12573d` All notes done woohoooo | 2026-07-30 | 2 |
| **total** | | **26** |

A twenty-seventh page, `aqa-a2-macro/2-1-4-uses-of-national-income-data.html`,
had the same tag removed on 30 July in `203f6bd` ("Remove the stale noindex …
Its own TODO said to drop it once the notes were written"). It does **not**
appear in the noindex export — Google recrawled it in time.

**For all 26, Google's last crawl predates the removal.** That is the whole
story.

### Ambiguous cases needing your confirmation

**There are none.** I looked for them and could not find any. Every noindex that
has ever existed in this repo was either the deliberate pair on `404.html` /
`confirmation.html`, or a stub placeholder that has since been correctly
removed. So I have nothing to ask you to confirm before recommending removal —
because there is nothing left to remove.

The one thing worth flagging is not a noindex at all but the pattern that
created them: **a `noindex` on a stub page is invisible once you forget it, and
a TODO comment in HTML is not a reminder anyone sees.** `12-…` proposes a cheap
guard so this cannot recur silently.

---

## 9. Search Console validation — what is available, and when

Checked against Google's current Page Indexing report and URL Inspection
documentation (fetched 21 August 2026), not from memory.

### What Google documents

- **Validation is offered on all "why pages aren't indexed" reasons.** There is
  a "Validate Fix" button on each issue's detail page.
- **How long:** *"Validation typically takes up to about two weeks, but in some
  cases can take much longer."*
- **What happens when you click it:** Search Console immediately tests a sample.
  If the issue is still present on those samples, validation stops there and
  the state does not change. Otherwise it enters **Started** and Google recrawls
  the known affected URLs over the following days.
- **The states:** *Not started* · *Started* · *Looking good* (everything checked
  so far is fixed) · *Passed* (all known instances gone) · *Failed* (a threshold
  of pages still show the issue) · *N/A* (Google noticed the fix without you
  asking).
- **If it fails:** you must start a new cycle. On a restart, only *Pending* and
  *Failed* URLs plus newly-found instances are re-checked; anything already
  *Passed* is skipped.
- **Do not stack requests:** *"Wait for a validation cycle to complete before
  requesting another cycle, even if you have fixed some issues."*
- **Request Indexing** (URL Inspection) has a **daily quota per property**;
  Google's guidance for many pages is to use a sitemap instead. *"Indexing can
  take up to a week or two."*

### Per reason

| Reason | Validate Fix? | What I would actually do |
| --- | --- | --- |
| Excluded by 'noindex' tag | **Yes — and it will pass** | Validation, if one is not already running. All 26 verified live today: 200, no robots tag. |
| Redirect error | **Yes — and it will pass** | Validation. Verified live: clean single 301 → 200. |
| Not found (404) | Yes, but **it will fail** | Nothing. All 10 correctly return 404; validation re-checks the response code, which has not changed and should not. |
| Alternate page with proper canonical tag | Yes | **Not yet.** This count is meant to rise before it falls. Around 20 September. |
| Duplicate without user-selected canonical | Yes | Nothing. No fix exists on GitHub Pages, so validation has nothing to confirm. |
| Crawled — currently not indexed | Technically yes | **No.** There is no defect for it to re-check. Use **URL Inspection → Request Indexing** on the six HTML pages instead — that is the right instrument for "the page changed, please look again". |
| Discovered — currently not indexed | Technically yes | **No.** Google has not crawled these, so there is nothing to re-verify. Waiting is the correct action, plus a handful of Request Indexing calls on your best pages. |
| Page with redirect | Yes | Nothing. Correct behaviour. |

### Your two existing validation requests

You have previously requested validation on **Excluded by 'noindex' tag** and
**Redirect error**. `06-gsc-checklist.md` Step 4 told you to start both on
8 August, so they are around thirteen days old.

**What state they will be in — and I want to be straight that I cannot see
this from the CSV exports.** The exports carry only URLs and crawl dates;
validation state lives only in the Search Console interface. What I can tell you
is what the export implies:

- Both should be **Started** or **Passed**. Both were genuinely fixed before you
  clicked, so neither can have failed the initial sample test.
- **But the 26 noindex URLs still carry their old crawl dates (18 May – 13 July)
  in today's export.** If validation were progressing, you would expect fresh
  crawl dates on at least some of them. Two readings: either the validation is
  still working through the queue and the report has not caught up, or the
  validation was never actually started. **You need to look at the screen to
  tell which** — `13-…` task 1 is exactly that check, and it comes first for
  this reason.

**Would requesting again now help or hurt?**

- **If either says *Started* or *Looking good*: do not touch it.** Google's
  documentation is explicit that you should wait for a cycle to finish. Clicking
  again restarts the clock and delays the result.
- **If either says *Not started*: start it now.** Both will pass.
- **If either says *Failed*: start a new one.** It cannot fail on the merits —
  the live evidence in §5 is unambiguous — so a failure would mean the sample
  was taken at a bad moment.
- **If either says *Passed*: nothing to do.** The pages will re-enter the index
  as they are recrawled.

### The rule that governs all of this

**Only request validation after the fix is live and you have verified it live.**
Not after the commit. Not after the push. After you have loaded the real URL on
the real domain and seen the fix with your own eyes — which for the two
outstanding issues, I have done for you in §5.

**And if a validation fails:** the issue returns to its previous state, the
affected URLs go back to *Pending*, and you must start a fresh cycle from
scratch — another two weeks or so. Nothing is broken and no penalty is applied;
you simply lose the time. That is the entire reason not to validate "Not found
(404)": it is a guaranteed failure and a guaranteed fortnight wasted.

---

## 10. What I could not determine

Stated rather than papered over.

1. ~~**The live validation state of your two existing requests.**~~
   **RESOLVED 21 Aug:** both report **Started**. Neither can have failed its
   initial sample test, which is consistent with the live evidence in §5. Leave
   both alone until they finish.
2. ~~**Whether Google has crawled any PDFs since 6 August.**~~
   **RESOLVED 21 Aug, and my earlier answer was wrong.** Crawl stats shows a
   spike to ~128 PDF requests a day on 8–9 August, then a return to baseline.
   The page-indexing export's `Last crawled` column had not caught up. The cost
   of `pdfs.xml` is one burst of ~140 requests, already paid, with zero new PDFs
   indexed to show for it. See §4 and §7.
3. **Why the "Redirect error" occurred on 5 August.** The URL behaves correctly
   now. URL Inspection on that exact URL would show Google's recorded reason.
4. **Whether the 121 queued HTML pages will drain on their own.** My reading is
   that most will, over 4–8 weeks. That is a forecast, not a measurement. The
   October re-export settles it.
5. **Why `revision-notes` lagged `practice-questions` so heavily in the crawl
   burst.** The familiarity pattern in §2a is a strong correlation — Google
   crawled what it already knew — but I cannot prove causation from thirteen
   days of data, and I did not find a repo-side difference that explains it.
   `verify_seo.py` passes identically on both sections.
6. **Whether the two remaining live duplicate pairs (`/` vs `/index.html`, and
   the one `?topic=` flashcards URL) will merge.** They should; both canonicals
   are correct. Confirmed only by watching.
7. ~~**Impressions and clicks since 8 August.**~~ **RESOLVED 21 Aug** — see §3a.
   The newly-indexed pages earned 50 clicks and 3,316 impressions from a
   standing start; the site is +42 clicks and +90% impressions.
8. **Whether the hub-page losses in §3a are consolidation or seasonality.**
   `/revision-notes/` is down 22 clicks and three positions, and `past-papers/`
   down 19 clicks. Both explanations fit and I cannot separate them from a
   28-day window that straddles the end of exam season. A year-on-year
   comparison (`13-…` task 7a) or the October read would settle it.
9. **Whether the 121 queued HTML pages are queued or declined.** §4 now rates
   this moderate-to-high rather than high, because the 108 ms response time
   shows capacity is not the constraint. A queue drains by itself; a judgement
   does not. October distinguishes them.

---

---

## Appendices — full URL lists

Generated 2026-08-21 from `seo/gsc-exports/21-08-2026/` reconciled against the
repo inventory. Paths are shown relative to `https://economicsacademy.co.uk`.
Dates in brackets are GSC's `Last crawled`.

### A1 — Published HTML pages, not indexed


#### A1.1 Discovered — currently not indexed (HTML) — 121

```
/past-paper-questions/aqa/1-3-1-the-determinants-of-the-demand-for-goods-and-services/  [1970-01-01]
/past-paper-questions/aqa/1-5-5-oligopoly/  [1970-01-01]
/past-paper-questions/aqa/1-7-2-the-problem-of-poverty/  [1970-01-01]
/past-paper-questions/aqa/2-1-2-macroeconomic-indicators/  [1970-01-01]
/past-paper-questions/aqa/2-3-1-economic-growth-and-the-economic-cycle/  [1970-01-01]
/past-paper-questions/aqa/2-3-4-possible-conflicts-between-macroeconomic-policy-objectives/  [1970-01-01]
/past-paper-questions/aqa/2-6-5-economic-growth-and-development/  [1970-01-01]
/past-paper-questions/edexcel/1-2-9-indirect-taxes-subsidies/  [1970-01-01]
/past-paper-questions/edexcel/2-1-1-economic-growth/  [1970-01-01]
/past-paper-questions/edexcel/2-6-3-supply-side-policies/  [1970-01-01]
/past-paper-questions/edexcel/3-5-2-supply-of-labour/  [1970-01-01]
/past-paper-questions/edexcel/4-1-3-pattern-of-trade/  [1970-01-01]
/past-paper-questions/edexcel/4-1-5-trading-blocs-and-the-world-trade-organisation/  [1970-01-01]
/past-paper-questions/edexcel/theme-4/  [1970-01-01]
/practice-questions/aqa-a2-micro/1-1-4-scarcity-choice-and-the-allocation-of-resources.html  [1970-01-01]
/practice-questions/aqa-a2-micro/1-3-3-the-determinants-of-the-supply-of-goods-and-services.html  [1970-01-01]
/practice-questions/aqa-a2-micro/1-3-4-price-elasticity-of-supply.html  [1970-01-01]
/practice-questions/aqa-a2-micro/1-5-7-price-discrimination.html  [1970-01-01]
/practice-questions/aqa-a2-micro/1-6-2-influence-upon-the-supply-of-labour-to-different-markets.html  [1970-01-01]
/practice-questions/aqa-a2-micro/1-7-1-the-distribution-of-income-and-wealth.html  [1970-01-01]
/practice-questions/edexcel-theme-1/1-1-1-economics-as-a-social-science.html  [1970-01-01]
/practice-questions/edexcel-theme-1/1-1-6-types-of-economies.html  [1970-01-01]
/practice-questions/edexcel-theme-2/2-1-3-employment-unemployment.html  [1970-01-01]
/practice-questions/edexcel-theme-2/2-1-4-balance-of-payments.html  [1970-01-01]
/practice-questions/edexcel-theme-2/2-2-1-aggregate-demand.html  [1970-01-01]
/practice-questions/edexcel-theme-2/2-3-1-aggregate-supply.html  [1970-01-01]
/practice-questions/edexcel-theme-2/2-5-3-trade-cycle.html  [1970-01-01]
/practice-questions/edexcel-theme-2/2-6-1-possible-macroeconomic-objectives.html  [1970-01-01]
/practice-questions/edexcel-theme-2/2-6-4-conflicts-between-objectives-and-policies.html  [1970-01-01]
/practice-questions/edexcel-theme-3/3-3-3-economies-diseconomies-of-scale.html  [1970-01-01]
/practice-questions/edexcel-theme-4/4-3-3-strategies-influencing-growth-development.html  [1970-01-01]
/practice-questions/edexcel-theme-4/4-5-4-macroeconomic-policies-in-a-global-context.html  [1970-01-01]
/revision-notes/aqa-a2-macro/2-1-1-the-objectives-of-government-economic-policy.html  [1970-01-01]
/revision-notes/aqa-a2-macro/2-2-1-the-circular-flow-of-income.html  [1970-01-01]
/revision-notes/aqa-a2-macro/2-2-3-the-determinants-of-aggregate-demand.html  [1970-01-01]
/revision-notes/aqa-a2-macro/2-2-6-determinants-of-long-run-aggregate-supply.html  [1970-01-01]
/revision-notes/aqa-a2-macro/2-3-1-economic-growth-and-the-economic-cycle.html  [1970-01-01]
/revision-notes/aqa-a2-macro/2-3-4-possible-conflicts-between-macroeconomic-policy-objectives.html  [1970-01-01]
/revision-notes/aqa-a2-macro/2-4-3-central-banks-and-monetary-policy.html  [1970-01-01]
/revision-notes/aqa-a2-macro/2-4-4-the-regulation-of-the-financial-system.html  [1970-01-01]
/revision-notes/aqa-a2-macro/2-6-3-the-balance-of-payments.html  [1970-01-01]
/revision-notes/aqa-a2-macro/2-6-5-economic-growth-and-development.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-1-1-economic-methodology.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-2-1-consumer-behaviour.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-2-3-aspects-of-behavioural-economic-theory.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-2-4-behavioural-economics-and-economic-policy.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-3-1-the-determinants-of-the-demand-for-goods-and-services.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-3-2-price-income-and-cross-elasticities-of-demand.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-3-3-the-determinants-of-the-supply-of-goods-and-services.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-4-1-production-and-productivity.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-4-2-specialisation-division-of-labour-and-exchange.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-4-3-the-law-of-diminishing-returns-and-returns-to-scale.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-4-4-costs-of-production.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-4-5-economies-and-diseconomies-of-scale.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-4-6-marginal-average-and-total-revenue.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-5-10-market-structure-efficiency-resource-allocation.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-5-3-perfect-competition.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-5-4-monopolistic-competition.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-5-7-price-discrimination.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-5-8-the-dynamics-of-competition-and-competitive-market-processes.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-6-2-influence-upon-the-supply-of-labour-to-different-markets.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-6-5-the-influence-of-trade-unions-in-determining-wages-and-levels-of-employment.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-7-1-the-distribution-of-income-and-wealth.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-7-2-the-problem-of-poverty.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-8-1-how-markets-and-prices-allocate-resources.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-8-3-public-goods-private-goods-and-quasi-public-goods.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-8-4-positive-and-negative-externalities-in-consumption-and-production.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-8-5-merit-and-demerit-goods.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-8-7-competition-policy.html  [1970-01-01]
/revision-notes/aqa-a2-micro/1-8-8-public-ownership-privatisation-regulation-and-deregulation-of-markets.html  [1970-01-01]
/revision-notes/edexcel-theme-1/1-2-10-alternative-views-of-consumer-behaviour.html  [1970-01-01]
/revision-notes/edexcel-theme-1/1-2-6-price-determination.html  [1970-01-01]
/revision-notes/edexcel-theme-1/1-2-8-producer-consumer-surplus.html  [1970-01-01]
/revision-notes/edexcel-theme-1/1-2-9-indirect-taxes-subsidies.html  [1970-01-01]
/revision-notes/edexcel-theme-1/1-3-3-public-goods.html  [1970-01-01]
/revision-notes/edexcel-theme-2/2-1-1-economic-growth.html  [1970-01-01]
/revision-notes/edexcel-theme-2/2-2-3-investment.html  [1970-01-01]
/revision-notes/edexcel-theme-2/2-2-5-net-trade.html  [1970-01-01]
/revision-notes/edexcel-theme-2/2-3-3-long-run-aggregate-supply.html  [1970-01-01]
/revision-notes/edexcel-theme-2/2-4-1-national-income.html  [1970-01-01]
/revision-notes/edexcel-theme-2/2-4-2-injections-withdrawals.html  [1970-01-01]
/revision-notes/edexcel-theme-2/2-4-3-equilibrium-levels-of-real-national-output.html  [1970-01-01]
/revision-notes/edexcel-theme-2/2-4-4-the-multiplier.html  [1970-01-01]
/revision-notes/edexcel-theme-2/2-5-3-trade-cycle.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-1-1-sizes-types-of-firms.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-1-2-business-growth.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-1-3-demergers.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-2-1-business-objectives.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-3-1-revenue.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-3-2-costs.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-3-3-economies-diseconomies-of-scale.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-3-4-normal-profits-supernormal-profits-losses.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-4-1-efficiency.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-4-2-perfect-competition.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-4-3-monopolistic-competition.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-4-4-oligopoly.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-4-5-monopoly.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-4-6-monopsony.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-5-1-demand-for-labour.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-5-2-supply-of-labour.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-5-3-wage-determination.html  [1970-01-01]
/revision-notes/edexcel-theme-3/3-6-1-government-intervention.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-1-1-globalisation.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-1-2-specialisation-trade.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-1-3-pattern-of-trade.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-1-4-terms-of-trade.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-1-5-trading-blocs-and-the-world-trade-organisation.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-1-6-restrictions-on-free-trade.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-1-7-balance-of-payments.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-1-9-international-competitiveness.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-2-1-absolute-relative-poverty.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-3-1-measures-of-development.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-4-3-role-of-central-banks.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-5-1-public-expenditure.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-5-2-taxation.html  [1970-01-01]
/revision-notes/edexcel-theme-4/4-5-4-macroeconomic-policies-in-a-global-context.html  [1970-01-01]
/revision-notes/glossary/aqa/  [1970-01-01]
/revision-notes/glossary/edexcel-a/  [1970-01-01]
/revision-notes/macro-application/  [1970-01-01]
```

#### A1.2 Crawled — currently not indexed (HTML) — 6

```
/about.html  [2026-04-03]
/contact.html  [2026-04-08]
/revision-notes/edexcel-theme-1/1-1-6-types-of-economies.html  [2026-07-09]
/revision-notes/edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html  [2026-02-24]
/revision-notes/edexcel-theme-1/1-2-4-supply.html  [2026-04-14]
/revision-notes/edexcel-theme-1/1-3-2-externalities.html  [2026-04-22]
```

#### A1.3 Excluded by 'noindex' tag — every row is stale — 26

```
/revision-notes/aqa-a2-macro/2-2-2-aggregate-demand-and-aggregate-supply-analysis.html  [2026-05-25]
/revision-notes/aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html  [2026-05-24]
/revision-notes/aqa-a2-macro/2-2-5-determinants-of-short-run-aggregate-supply.html  [2026-05-24]
/revision-notes/aqa-a2-macro/2-3-3-inflation-and-deflation.html  [2026-05-31]
/revision-notes/aqa-a2-macro/2-4-1-the-structure-of-financial-markets-and-financial-assets.html  [2026-05-18]
/revision-notes/aqa-a2-macro/2-4-2-commercial-banks-and-investment-banks.html  [2026-05-31]
/revision-notes/aqa-a2-macro/2-5-1-fiscal-policy.html  [2026-05-24]
/revision-notes/aqa-a2-macro/2-5-2-supply-side-policies.html  [2026-07-13]
/revision-notes/aqa-a2-micro/1-1-3-economic-resources.html  [2026-05-25]
/revision-notes/aqa-a2-micro/1-1-4-scarcity-choice-and-the-allocation-of-resources.html  [2026-05-24]
/revision-notes/aqa-a2-micro/1-1-5-production-possibility-diagrams.html  [2026-05-24]
/revision-notes/aqa-a2-micro/1-2-2-imperfect-information.html  [2026-05-24]
/revision-notes/aqa-a2-micro/1-3-4-price-elasticity-of-supply.html  [2026-05-26]
/revision-notes/aqa-a2-micro/1-3-5-the-determination-of-equilibrium-market-prices.html  [2026-05-25]
/revision-notes/aqa-a2-micro/1-4-7-profit.html  [2026-05-25]
/revision-notes/aqa-a2-micro/1-4-8-technological-change.html  [2026-05-26]
/revision-notes/aqa-a2-micro/1-5-11-consumer-and-producer-surplus.html  [2026-05-20]
/revision-notes/aqa-a2-micro/1-5-2-the-objectives-of-firms.html  [2026-05-24]
/revision-notes/aqa-a2-micro/1-5-6-monopoly-and-monopoly-power.html  [2026-05-28]
/revision-notes/aqa-a2-micro/1-5-9-contestable-and-non-contestable-markets.html  [2026-05-19]
/revision-notes/aqa-a2-micro/1-6-1-the-demand-for-labour-marginal-productivity-theory.html  [2026-05-24]
/revision-notes/aqa-a2-micro/1-6-4-wage-determination-imperfectly-competitive-labour-markets.html  [2026-05-19]
/revision-notes/aqa-a2-micro/1-6-6-the-national-minimum-wage.html  [2026-05-25]
/revision-notes/aqa-a2-micro/1-6-7-discrimination-in-the-labour-market.html  [2026-05-20]
/revision-notes/aqa-a2-micro/1-8-10-government-failure.html  [2026-05-24]
/revision-notes/aqa-a2-micro/1-8-9-government-intervention-in-markets.html  [2026-06-19]
```

### A2 — Published PDFs, not indexed


#### A2.1 Discovered — currently not indexed (PDF) — 195

```
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2017-mark-scheme.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2017-question-paper.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2018-mark-scheme.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2019-mark-scheme.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2019-question-paper.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2020-mark-scheme.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2020-question-paper.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2021-mark-scheme.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2021-question-paper.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2022-mark-scheme.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2022-question-paper.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2023-mark-scheme.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2023-question-paper.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2024-mark-scheme.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2024-question-paper.pdf
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-specimen-mark-scheme.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2017-question-paper.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2018-mark-scheme.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2018-question-paper.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2019-mark-scheme.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2019-question-paper.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2020-mark-scheme.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2020-question-paper.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2021-question-paper.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2022-mark-scheme.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2022-question-paper.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2023-mark-scheme.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2023-question-paper.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2024-mark-scheme.pdf
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-specimen-mark-scheme.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2017-mark-scheme.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2017-question-paper.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2018-mark-scheme.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2019-mark-scheme.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2019-question-paper.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2020-mark-scheme.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2021-mark-scheme.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2022-mark-scheme.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2024-mark-scheme.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-specimen-mark-scheme.pdf
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-specimen-question-paper.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2016-mark-scheme.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2016-question-paper.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2017-mark-scheme.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2018-mark-scheme.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2019-mark-scheme.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2022-mark-scheme.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2022-question-paper.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2023-mark-scheme.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2023-question-paper.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2024-mark-scheme.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-november-2020-mark-scheme.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-november-2020-question-paper.pdf
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-specimen-mark-scheme.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2016-mark-scheme.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2017-mark-scheme.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2017-question-paper.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2018-mark-scheme.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2019-mark-scheme.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2022-mark-scheme.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2023-mark-scheme.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2023-question-paper.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2024-mark-scheme.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2024-question-paper.pdf
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-november-2020-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2017-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2018-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2018-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2019-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2022-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2022-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2023-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2024-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2024-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-november-2021-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-november-2021-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-october-2020-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-october-2020-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2017-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2018-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2018-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2019-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2022-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2022-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2023-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2024-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2024-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-november-2021-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-november-2021-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-october-2020-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2017-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2017-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2018-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2018-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2019-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2022-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2022-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2024-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2024-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-november-2021-mark-scheme.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-november-2021-question-paper.pdf
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-october-2020-mark-scheme.pdf
/past-papers/edexcel-b/as-level/paper-1/edexcel-b-as-level-economics-paper-1-june-2016-question-paper.pdf
/past-papers/edexcel-b/as-level/paper-1/edexcel-b-as-level-economics-paper-1-june-2017-mark-scheme.pdf
/past-papers/edexcel-b/as-level/paper-1/edexcel-b-as-level-economics-paper-1-june-2018-mark-scheme.pdf
/past-papers/edexcel-b/as-level/paper-1/edexcel-b-as-level-economics-paper-1-june-2018-question-paper.pdf
/past-papers/edexcel-b/as-level/paper-1/edexcel-b-as-level-economics-paper-1-june-2019-mark-scheme.pdf
/past-papers/edexcel-b/as-level/paper-1/edexcel-b-as-level-economics-paper-1-june-2019-question-paper.pdf
/past-papers/edexcel-b/as-level/paper-1/edexcel-b-as-level-economics-paper-1-october-2020-mark-scheme.pdf
/past-papers/edexcel-b/as-level/paper-1/edexcel-b-as-level-economics-paper-1-october-2020-question-paper.pdf
/past-papers/edexcel-b/as-level/paper-2/edexcel-b-as-level-economics-paper-2-june-2016-mark-scheme.pdf
/past-papers/edexcel-b/as-level/paper-2/edexcel-b-as-level-economics-paper-2-june-2016-question-paper.pdf
/past-papers/edexcel-b/as-level/paper-2/edexcel-b-as-level-economics-paper-2-june-2017-mark-scheme.pdf
/past-papers/edexcel-b/as-level/paper-2/edexcel-b-as-level-economics-paper-2-june-2017-question-paper.pdf
/past-papers/edexcel-b/as-level/paper-2/edexcel-b-as-level-economics-paper-2-june-2018-mark-scheme.pdf
/past-papers/edexcel-b/as-level/paper-2/edexcel-b-as-level-economics-paper-2-june-2018-question-paper.pdf
/past-papers/edexcel-b/as-level/paper-2/edexcel-b-as-level-economics-paper-2-june-2019-mark-scheme.pdf
/past-papers/edexcel-b/as-level/paper-2/edexcel-b-as-level-economics-paper-2-june-2019-question-paper.pdf
/past-papers/edexcel-b/as-level/paper-2/edexcel-b-as-level-economics-paper-2-october-2020-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2017-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2017-question-paper.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2018-question-paper.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2019-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2019-question-paper.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2022-question-paper.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2023-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2024-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2024-question-paper.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-november-2021-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-october-2020-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-october-2020-question-paper.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2017-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2018-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2019-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2019-question-paper.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2022-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2022-question-paper.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2023-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2023-question-paper.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2024-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2024-question-paper.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-november-2021-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-november-2021-question-paper.pdf
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-october-2020-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2017-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2018-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2018-question-paper.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2019-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2019-question-paper.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2022-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2022-question-paper.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2023-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2023-question-paper.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2024-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2024-question-paper.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-november-2021-mark-scheme.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-november-2021-question-paper.pdf
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-october-2020-question-paper.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2016-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2017-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2017-question-paper.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2018-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2019-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2022-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2022-question-paper.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2023-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2023-question-paper.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2024-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2024-question-paper.pdf
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-october-2020-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2016-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2016-question-paper.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2017-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2017-question-paper.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2018-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2018-question-paper.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2019-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2019-question-paper.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2022-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2022-question-paper.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2023-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2023-question-paper.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2024-mark-scheme.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-june-2024-question-paper.pdf
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-october-2020-mark-scheme.pdf
/past-papers/ocr/a-level/paper-1/ocr-a-level-economics-paper-1-june-2024-mark-scheme.pdf
/past-papers/ocr/a-level/paper-2/ocr-a-level-economics-paper-2-june-2023-question-paper.pdf
/past-papers/ocr/a-level/paper-2/ocr-a-level-economics-paper-2-november-2020-question-paper.pdf
/past-papers/ocr/a-level/paper-2/ocr-a-level-economics-paper-2-november-2021-question-paper.pdf
/past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-june-2022-question-paper.pdf
/past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-june-2023-question-paper.pdf
/past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-november-2020-mark-scheme.pdf
/past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-november-2020-question-paper.pdf
/past-papers/ocr/as-level/paper-1/ocr-as-level-economics-paper-1-june-2023-mark-scheme.pdf
/past-papers/ocr/as-level/paper-2/ocr-as-level-economics-paper-2-june-2023-question-paper.pdf
```

#### A2.2 Crawled — currently not indexed (PDF) — 67

```
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2017-mark-scheme.pdf  [2026-04-10]
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2024-question-paper.pdf  [2026-03-27]
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2018-question-paper.pdf  [2026-03-30]
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2023-mark-scheme.pdf  [2026-02-23]
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2023-question-paper.pdf  [2026-04-05]
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2024-question-paper.pdf  [2025-10-22]
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2018-question-paper.pdf  [2026-04-14]
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2024-question-paper.pdf  [2026-03-11]
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-specimen-question-paper.pdf  [2026-07-31]
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2016-question-paper.pdf  [2026-03-25]
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-specimen-mark-scheme.pdf  [2026-03-06]
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-specimen-question-paper.pdf  [2026-04-01]
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2017-question-paper.pdf  [2026-03-04]
/past-papers/edexcel-b/a-level/paper-1/edexcel-b-a-level-economics-paper-1-june-2019-question-paper.pdf  [2026-03-04]
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2017-question-paper.pdf  [2026-03-04]
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-october-2020-mark-scheme.pdf  [2026-04-10]
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2019-mark-scheme.pdf  [2026-03-04]
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2023-question-paper.pdf  [2026-04-09]
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-october-2020-question-paper.pdf  [2026-03-04]
/past-papers/edexcel-b/as-level/paper-1/edexcel-b-as-level-economics-paper-1-june-2016-mark-scheme.pdf  [2026-03-04]
/past-papers/edexcel-b/as-level/paper-1/edexcel-b-as-level-economics-paper-1-june-2017-question-paper.pdf  [2026-03-06]
/past-papers/edexcel-b/as-level/paper-2/edexcel-b-as-level-economics-paper-2-october-2020-question-paper.pdf  [2026-03-05]
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2018-mark-scheme.pdf  [2026-07-29]
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2022-mark-scheme.pdf  [2026-03-12]
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-june-2023-question-paper.pdf  [2026-07-26]
/past-papers/edexcel/a-level/paper-1/edexcel-a-level-economics-paper-1-november-2021-question-paper.pdf  [2026-07-25]
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2018-question-paper.pdf  [2026-07-31]
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-october-2020-question-paper.pdf  [2026-05-14]
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-june-2017-question-paper.pdf  [2026-08-05]
/past-papers/edexcel/a-level/paper-3/edexcel-a-level-economics-paper-3-october-2020-mark-scheme.pdf  [2026-07-21]
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2016-question-paper.pdf  [2026-03-03]
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2018-question-paper.pdf  [2026-07-18]
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-june-2019-question-paper.pdf  [2026-03-03]
/past-papers/edexcel/as-level/paper-1/edexcel-as-level-economics-paper-1-october-2020-question-paper.pdf  [2026-07-29]
/past-papers/edexcel/as-level/paper-2/edexcel-as-level-economics-paper-2-october-2020-question-paper.pdf  [2025-12-06]
/past-papers/ocr/a-level/paper-1/ocr-a-level-economics-paper-1-june-2022-mark-scheme.pdf  [2026-08-03]
/past-papers/ocr/a-level/paper-1/ocr-a-level-economics-paper-1-june-2022-question-paper.pdf  [2026-07-07]
/past-papers/ocr/a-level/paper-1/ocr-a-level-economics-paper-1-june-2023-mark-scheme.pdf  [2026-07-29]
/past-papers/ocr/a-level/paper-1/ocr-a-level-economics-paper-1-june-2023-question-paper.pdf  [2026-05-24]
/past-papers/ocr/a-level/paper-1/ocr-a-level-economics-paper-1-june-2024-question-paper.pdf  [2026-08-01]
/past-papers/ocr/a-level/paper-1/ocr-a-level-economics-paper-1-november-2020-mark-scheme.pdf  [2026-02-26]
/past-papers/ocr/a-level/paper-1/ocr-a-level-economics-paper-1-november-2020-question-paper.pdf  [2026-02-23]
/past-papers/ocr/a-level/paper-1/ocr-a-level-economics-paper-1-november-2021-mark-scheme.pdf  [2026-02-23]
/past-papers/ocr/a-level/paper-1/ocr-a-level-economics-paper-1-november-2021-question-paper.pdf  [2026-08-02]
/past-papers/ocr/a-level/paper-2/ocr-a-level-economics-paper-2-june-2022-mark-scheme.pdf  [2026-02-26]
/past-papers/ocr/a-level/paper-2/ocr-a-level-economics-paper-2-june-2022-question-paper.pdf  [2026-02-23]
/past-papers/ocr/a-level/paper-2/ocr-a-level-economics-paper-2-june-2024-mark-scheme.pdf  [2026-02-24]
/past-papers/ocr/a-level/paper-2/ocr-a-level-economics-paper-2-june-2024-question-paper.pdf  [2026-02-23]
/past-papers/ocr/a-level/paper-2/ocr-a-level-economics-paper-2-november-2020-mark-scheme.pdf  [2026-02-26]
/past-papers/ocr/a-level/paper-2/ocr-a-level-economics-paper-2-november-2021-mark-scheme.pdf  [2026-08-01]
/past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-june-2022-mark-scheme.pdf  [2026-02-23]
/past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-june-2023-mark-scheme.pdf  [2026-08-01]
/past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-june-2024-mark-scheme.pdf  [2026-08-01]
/past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-june-2024-question-paper.pdf  [2026-08-02]
/past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-november-2021-mark-scheme.pdf  [2026-02-23]
/past-papers/ocr/as-level/paper-1/ocr-as-level-economics-paper-1-june-2022-mark-scheme.pdf  [2026-02-23]
/past-papers/ocr/as-level/paper-1/ocr-as-level-economics-paper-1-june-2022-question-paper.pdf  [2026-02-23]
/past-papers/ocr/as-level/paper-1/ocr-as-level-economics-paper-1-june-2023-question-paper.pdf  [2026-02-23]
/past-papers/ocr/as-level/paper-1/ocr-as-level-economics-paper-1-june-2024-mark-scheme.pdf  [2026-03-14]
/past-papers/ocr/as-level/paper-1/ocr-as-level-economics-paper-1-november-2020-question-paper.pdf  [2026-02-26]
/past-papers/ocr/as-level/paper-2/ocr-as-level-economics-paper-2-june-2022-mark-scheme.pdf  [2026-08-06]
/past-papers/ocr/as-level/paper-2/ocr-as-level-economics-paper-2-june-2022-question-paper.pdf  [2026-07-31]
/past-papers/ocr/as-level/paper-2/ocr-as-level-economics-paper-2-june-2023-mark-scheme.pdf  [2026-02-23]
/past-papers/ocr/as-level/paper-2/ocr-as-level-economics-paper-2-june-2024-mark-scheme.pdf  [2026-03-20]
/past-papers/ocr/as-level/paper-2/ocr-as-level-economics-paper-2-june-2024-question-paper.pdf  [2026-07-31]
/past-papers/ocr/as-level/paper-2/ocr-as-level-economics-paper-2-november-2020-mark-scheme.pdf  [2026-02-23]
/past-papers/ocr/as-level/paper-2/ocr-as-level-economics-paper-2-november-2020-question-paper.pdf  [2026-03-03]
```

#### A2.3 Duplicate without user-selected canonical (PDF) — 8

```
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-june-2018-question-paper.pdf  [2026-08-03]
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-june-2021-mark-scheme.pdf  [2026-06-11]
/past-papers/edexcel-b/a-level/paper-2/edexcel-b-a-level-economics-paper-2-june-2019-mark-scheme.pdf  [2026-05-07]
/past-papers/edexcel/a-level/paper-2/edexcel-a-level-economics-paper-2-june-2017-question-paper.pdf  [2026-07-27]
/past-papers/ocr/a-level/paper-2/ocr-a-level-economics-paper-2-june-2023-mark-scheme.pdf  [2026-07-25]
/past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-november-2021-question-paper.pdf  [2026-08-05]
/past-papers/ocr/as-level/paper-1/ocr-as-level-economics-paper-1-june-2024-question-paper.pdf  [2026-08-03]
/past-papers/ocr/as-level/paper-1/ocr-as-level-economics-paper-1-november-2020-mark-scheme.pdf  [2026-07-23]
```

### A3 — Published URLs in no GSC export at all


#### A3.1 Not judged — 4

```
/404.html
/confirmation.html
/marking-examples/annotated-paper-example.pdf
/marking-examples/feedback-email-example.pdf
```

### A4 — Ghosts: in a GSC export, not a URL this site publishes


#### A4.1 Alternate page with proper canonical tag — 15

```
/flashcards/aqa/macro/?topic=2-6-1-globalisation  [2026-08-11]
/past-papers/aqa/index.html  [2026-08-12]
/past-papers/edexcel-b/index.html  [2026-07-31]
/past-papers/edexcel/index.html  [2026-08-13]
/past-papers/index.html  [2026-08-05]
/past-papers/ocr/index.html  [2026-08-11]
/practice-questions/edexcel-theme-1/index.html  [2026-08-09]
/practice-questions/edexcel-theme-2/index.html  [2026-08-18]
/practice-questions/edexcel-theme-3/index.html  [2026-08-09]
/practice-questions/edexcel-theme-4/index.html  [2026-08-09]
/revision-notes/aqa-a2-micro/index.html  [2026-07-23]
/revision-notes/edexcel-theme-1/index.html  [2026-08-01]
/revision-notes/edexcel-theme-3/index.html  [2026-08-12]
/revision-notes/edexcel-theme-4/index.html  [2026-07-18]
/revision-notes/index.html  [2026-08-08]
```

#### A4.2 Crawled — currently not indexed — 1

```
/revision-notes/edexcel-theme-1/1-2-5-price-income-cross-elasticities-of-supply.html  [2026-03-05]
```

#### A4.3 Indexed — 2

```
/flashcards/aqa/macro/?topic=2-6-2-trade  [2026-08-10]
/index.html  [2026-07-02]
```

#### A4.4 Not found (404) — 10

```
/past-papers/edexcel-b/a-level/paper-3/edexcel-b-a-level-economics-paper-3-june-2023-mark-scheme.pdf  [2026-03-06]
/revision-notes/aqa-a2-micro/aqa-a-micro/4.1.1.html  [2026-02-26]
/revision-notes/aqa-a2-micro/aqa-a-micro/4.2.1.html  [2026-02-27]
/revision-notes/aqa-a2-micro/aqa-a-micro/4.3.1.html  [2026-02-26]
/revision-notes/aqa-a2-micro/aqa-a-micro/4.5.3.html  [2026-03-05]
/revision-notes/aqa-a2-micro/aqa-a-micro/4.6.3.html  [2026-03-03]
/revision-notes/aqa-a2-micro/aqa-a-micro/4.7.3.html  [2026-02-28]
/revision-notes/aqa-as-micro/aqa-as-micro/3.2.2.html  [2026-07-17]
/revision-notes/aqa-as-micro/aqa-as-micro/3.3.4.html  [2026-07-23]
/revision-notes/aqa-as-micro/index.html  [2026-07-04]
```

#### A4.5 Page with redirect — 3

```
http://economicsacademy.co.uk/  [2026-08-13]
http://www.economicsacademy.co.uk/  [2026-08-03]
https://www.economicsacademy.co.uk/  [2026-08-13]
```

#### A4.6 Redirect error — 1

```
/past-paper-questions  [2026-08-05]
```


### A5 — Indexed published PDFs — 11

```
/past-papers/aqa/a-level/paper-1/aqa-a-level-economics-paper-1-specimen-question-paper.pdf  [2026-07-22]
/past-papers/aqa/a-level/paper-2/aqa-a-level-economics-paper-2-specimen-question-paper.pdf  [2026-07-30]
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2020-question-paper.pdf  [2026-07-30]
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2021-question-paper.pdf  [2026-07-09]
/past-papers/aqa/a-level/paper-3/aqa-a-level-economics-paper-3-june-2022-question-paper.pdf  [2026-07-28]
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2017-question-paper.pdf  [2026-06-13]
/past-papers/aqa/as-level/paper-1/aqa-as-level-economics-paper-1-june-2019-question-paper.pdf  [2026-07-31]
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2018-question-paper.pdf  [2026-07-22]
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2019-question-paper.pdf  [2026-07-17]
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-june-2022-question-paper.pdf  [2026-07-03]
/past-papers/aqa/as-level/paper-2/aqa-as-level-economics-paper-2-november-2020-question-paper.pdf  [2026-06-13]
```


### A6 — Indexed published HTML pages — 308

```
/  [2026-08-14]
/faq.html  [2026-08-14]
/flashcards/  [2026-08-15]
/flashcards/aqa/macro/  [2026-08-17]
/flashcards/aqa/micro/  [2026-08-17]
/flashcards/edexcel-a/theme-1/  [2026-08-17]
/flashcards/edexcel-a/theme-2/  [2026-08-17]
/flashcards/edexcel-a/theme-3/  [2026-08-17]
/flashcards/edexcel-a/theme-4/  [2026-08-17]
/marking.html  [2026-07-31]
/past-paper-questions/  [2026-08-15]
/past-paper-questions/aqa/  [2026-08-09]
/past-paper-questions/aqa/1-3-5-the-determination-of-equilibrium-market-prices/  [2026-08-09]
/past-paper-questions/aqa/1-4-7-profit/  [2026-08-09]
/past-paper-questions/aqa/1-4-8-technological-change/  [2026-08-10]
/past-paper-questions/aqa/1-5-10-market-structure-efficiency-resource-allocation/  [2026-08-09]
/past-paper-questions/aqa/1-5-6-monopoly-and-monopoly-power/  [2026-08-10]
/past-paper-questions/aqa/1-5-8-the-dynamics-of-competition-and-competitive-market-processes/  [2026-08-09]
/past-paper-questions/aqa/1-6-2-influence-upon-the-supply-of-labour-to-different-markets/  [2026-08-09]
/past-paper-questions/aqa/1-6-5-the-influence-of-trade-unions-in-determining-wages-and-levels-of-employment/  [2026-08-10]
/past-paper-questions/aqa/1-6-7-discrimination-in-the-labour-market/  [2026-08-09]
/past-paper-questions/aqa/1-7-1-the-distribution-of-income-and-wealth/  [2026-08-09]
/past-paper-questions/aqa/1-7-3-government-policies-poverty-income-distribution/  [2026-08-09]
/past-paper-questions/aqa/1-8-4-positive-and-negative-externalities-in-consumption-and-production/  [2026-08-10]
/past-paper-questions/aqa/1-8-7-competition-policy/  [2026-08-10]
/past-paper-questions/aqa/1-8-8-public-ownership-privatisation-regulation-and-deregulation-of-markets/  [2026-08-10]
/past-paper-questions/aqa/1-8-9-government-intervention-in-markets/  [2026-08-12]
/past-paper-questions/aqa/2-1-4-uses-of-national-income-data/  [2026-08-09]
/past-paper-questions/aqa/2-2-3-the-determinants-of-aggregate-demand/  [2026-08-09]
/past-paper-questions/aqa/2-2-6-determinants-of-long-run-aggregate-supply/  [2026-08-09]
/past-paper-questions/aqa/2-3-2-employment-and-unemployment/  [2026-08-09]
/past-paper-questions/aqa/2-3-3-inflation-and-deflation/  [2026-08-09]
/past-paper-questions/aqa/2-4-3-central-banks-and-monetary-policy/  [2026-08-09]
/past-paper-questions/aqa/2-5-1-fiscal-policy/  [2026-08-11]
/past-paper-questions/aqa/2-5-2-supply-side-policies/  [2026-08-09]
/past-paper-questions/aqa/2-6-1-globalisation/  [2026-08-10]
/past-paper-questions/aqa/2-6-2-trade/  [2026-08-09]
/past-paper-questions/aqa/2-6-3-the-balance-of-payments/  [2026-08-08]
/past-paper-questions/aqa/2-6-4-exchange-rate-systems/  [2026-08-09]
/past-paper-questions/aqa/macroeconomics/  [2026-08-08]
/past-paper-questions/aqa/microeconomics/  [2026-08-09]
/past-paper-questions/edexcel/  [2026-08-09]
/past-paper-questions/edexcel/1-1-3-the-economic-problem/  [2026-08-09]
/past-paper-questions/edexcel/1-1-6-types-of-economies/  [2026-08-10]
/past-paper-questions/edexcel/1-2-1-rational-decision-making/  [2026-08-09]
/past-paper-questions/edexcel/1-2-10-alternative-views-of-consumer-behaviour/  [2026-08-09]
/past-paper-questions/edexcel/1-2-2-demand/  [2026-08-09]
/past-paper-questions/edexcel/1-2-3-price-income-cross-elasticities-of-demand/  [2026-08-09]
/past-paper-questions/edexcel/1-2-5-price-elasticity-of-supply/  [2026-08-10]
/past-paper-questions/edexcel/1-2-6-price-determination/  [2026-08-10]
/past-paper-questions/edexcel/1-3-1-types-of-market-failure/  [2026-08-10]
/past-paper-questions/edexcel/1-3-2-externalities/  [2026-08-10]
/past-paper-questions/edexcel/1-3-4-information-gaps/  [2026-08-09]
/past-paper-questions/edexcel/1-4-1-government-intervention-in-markets/  [2026-08-09]
/past-paper-questions/edexcel/2-1-2-inflation/  [2026-08-09]
/past-paper-questions/edexcel/2-1-3-employment-unemployment/  [2026-08-09]
/past-paper-questions/edexcel/2-2-1-aggregate-demand/  [2026-08-09]
/past-paper-questions/edexcel/2-2-2-consumption/  [2026-08-09]
/past-paper-questions/edexcel/2-2-3-investment/  [2026-08-10]
/past-paper-questions/edexcel/2-2-4-government-expenditure/  [2026-08-09]
/past-paper-questions/edexcel/2-2-5-net-trade/  [2026-08-10]
/past-paper-questions/edexcel/2-5-1-causes-of-growth/  [2026-08-10]
/past-paper-questions/edexcel/2-6-2-demand-side-policies/  [2026-08-09]
/past-paper-questions/edexcel/2-6-4-conflicts-between-objectives-and-policies/  [2026-08-09]
/past-paper-questions/edexcel/3-1-2-business-growth/  [2026-08-09]
/past-paper-questions/edexcel/3-3-1-revenue/  [2026-08-08]
/past-paper-questions/edexcel/3-3-2-costs/  [2026-08-09]
/past-paper-questions/edexcel/3-3-4-normal-profits-supernormal-profits-losses/  [2026-08-09]
/past-paper-questions/edexcel/3-4-4-oligopoly/  [2026-08-09]
/past-paper-questions/edexcel/3-4-5-monopoly/  [2026-08-09]
/past-paper-questions/edexcel/3-4-7-contestability/  [2026-08-09]
/past-paper-questions/edexcel/3-5-3-wage-determination/  [2026-08-10]
/past-paper-questions/edexcel/3-6-1-government-intervention/  [2026-08-09]
/past-paper-questions/edexcel/4-1-1-globalisation/  [2026-08-09]
/past-paper-questions/edexcel/4-1-8-exchange-rates/  [2026-08-09]
/past-paper-questions/edexcel/4-1-9-international-competitiveness/  [2026-08-10]
/past-paper-questions/edexcel/4-2-2-inequality/  [2026-08-09]
/past-paper-questions/edexcel/4-3-2-factors-influencing-growth-development/  [2026-08-10]
/past-paper-questions/edexcel/4-3-3-strategies-influencing-growth-development/  [2026-08-09]
/past-paper-questions/edexcel/4-4-1-role-of-financial-markets/  [2026-08-10]
/past-paper-questions/edexcel/4-4-3-role-of-central-banks/  [2026-08-09]
/past-paper-questions/edexcel/4-5-2-taxation/  [2026-08-09]
/past-paper-questions/edexcel/4-5-3-public-sector-finances/  [2026-08-10]
/past-paper-questions/edexcel/theme-1/  [2026-08-09]
/past-paper-questions/edexcel/theme-2/  [2026-08-09]
/past-paper-questions/edexcel/theme-3/  [2026-08-09]
/past-papers/  [2026-08-16]
/past-papers/aqa/  [2026-08-16]
/past-papers/edexcel-b/  [2026-08-16]
/past-papers/edexcel/  [2026-08-16]
/past-papers/ocr/  [2026-08-16]
/practice-questions/  [2026-08-15]
/practice-questions/aqa-a2-macro/  [2026-08-17]
/practice-questions/aqa-a2-macro/2-1-1-the-objectives-of-government-economic-policy.html  [2026-08-10]
/practice-questions/aqa-a2-macro/2-1-2-macroeconomic-indicators.html  [2026-08-10]
/practice-questions/aqa-a2-macro/2-1-3-uses-of-index-numbers.html  [2026-08-11]
/practice-questions/aqa-a2-macro/2-1-4-uses-of-national-income-data.html  [2026-08-08]
/practice-questions/aqa-a2-macro/2-2-1-the-circular-flow-of-income.html  [2026-08-11]
/practice-questions/aqa-a2-macro/2-2-2-aggregate-demand-and-aggregate-supply-analysis.html  [2026-08-08]
/practice-questions/aqa-a2-macro/2-2-3-the-determinants-of-aggregate-demand.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-2-5-determinants-of-short-run-aggregate-supply.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-2-6-determinants-of-long-run-aggregate-supply.html  [2026-08-10]
/practice-questions/aqa-a2-macro/2-3-1-economic-growth-and-the-economic-cycle.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-3-2-employment-and-unemployment.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-3-3-inflation-and-deflation.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-3-4-possible-conflicts-between-macroeconomic-policy-objectives.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-4-1-the-structure-of-financial-markets-and-financial-assets.html  [2026-08-10]
/practice-questions/aqa-a2-macro/2-4-2-commercial-banks-and-investment-banks.html  [2026-08-10]
/practice-questions/aqa-a2-macro/2-4-3-central-banks-and-monetary-policy.html  [2026-08-11]
/practice-questions/aqa-a2-macro/2-4-4-the-regulation-of-the-financial-system.html  [2026-08-10]
/practice-questions/aqa-a2-macro/2-5-1-fiscal-policy.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-5-2-supply-side-policies.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-6-1-globalisation.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-6-2-trade.html  [2026-08-09]
/practice-questions/aqa-a2-macro/2-6-3-the-balance-of-payments.html  [2026-08-10]
/practice-questions/aqa-a2-macro/2-6-4-exchange-rate-systems.html  [2026-08-11]
/practice-questions/aqa-a2-macro/2-6-5-economic-growth-and-development.html  [2026-08-09]
/practice-questions/aqa-a2-micro/  [2026-08-10]
/practice-questions/aqa-a2-micro/1-1-1-economic-methodology.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-1-3-economic-resources.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-1-5-production-possibility-diagrams.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-2-1-consumer-behaviour.html  [2026-08-11]
/practice-questions/aqa-a2-micro/1-2-2-imperfect-information.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-2-3-aspects-of-behavioural-economic-theory.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-2-4-behavioural-economics-and-economic-policy.html  [2026-08-14]
/practice-questions/aqa-a2-micro/1-3-1-the-determinants-of-the-demand-for-goods-and-services.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-3-2-price-income-and-cross-elasticities-of-demand.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-3-5-the-determination-of-equilibrium-market-prices.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-3-6-the-interrelationship-between-markets.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-4-1-production-and-productivity.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-4-2-specialisation-division-of-labour-and-exchange.html  [2026-08-11]
/practice-questions/aqa-a2-micro/1-4-3-the-law-of-diminishing-returns-and-returns-to-scale.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-4-4-costs-of-production.html  [2026-08-11]
/practice-questions/aqa-a2-micro/1-4-5-economies-and-diseconomies-of-scale.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-4-6-marginal-average-and-total-revenue.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-4-7-profit.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-4-8-technological-change.html  [2026-08-11]
/practice-questions/aqa-a2-micro/1-5-1-market-structures.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-5-10-market-structure-efficiency-resource-allocation.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-5-11-consumer-and-producer-surplus.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-5-2-the-objectives-of-firms.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-5-3-perfect-competition.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-5-4-monopolistic-competition.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-5-5-oligopoly.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-5-6-monopoly-and-monopoly-power.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-5-8-the-dynamics-of-competition-and-competitive-market-processes.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-5-9-contestable-and-non-contestable-markets.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-6-1-the-demand-for-labour-marginal-productivity-theory.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-6-4-wage-determination-imperfectly-competitive-labour-markets.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-6-5-the-influence-of-trade-unions-in-determining-wages-and-levels-of-employment.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-6-6-the-national-minimum-wage.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-6-7-discrimination-in-the-labour-market.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-7-2-the-problem-of-poverty.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-7-3-government-policies-poverty-income-distribution.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-8-1-how-markets-and-prices-allocate-resources.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-8-10-government-failure.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-8-2-the-meaning-of-market-failure.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-8-3-public-goods-private-goods-and-quasi-public-goods.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-8-4-positive-and-negative-externalities-in-consumption-and-production.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-8-5-merit-and-demerit-goods.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-8-6-market-imperfections.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-8-7-competition-policy.html  [2026-08-09]
/practice-questions/aqa-a2-micro/1-8-8-public-ownership-privatisation-regulation-and-deregulation-of-markets.html  [2026-08-10]
/practice-questions/aqa-a2-micro/1-8-9-government-intervention-in-markets.html  [2026-08-10]
/practice-questions/edexcel-theme-1/  [2026-08-17]
/practice-questions/edexcel-theme-1/1-1-2-positive-normative-statements.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-1-3-the-economic-problem.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-1-4-production-possibility-frontiers.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-1-5-specialisation-division-of-labour.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-2-1-rational-decision-making.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-2-10-alternative-views-of-consumer-behaviour.html  [2026-08-10]
/practice-questions/edexcel-theme-1/1-2-2-demand.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-2-4-supply.html  [2026-08-10]
/practice-questions/edexcel-theme-1/1-2-5-price-elasticity-of-supply.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-2-6-price-determination.html  [2026-08-10]
/practice-questions/edexcel-theme-1/1-2-7-price-mechanism.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-2-8-producer-consumer-surplus.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-2-9-indirect-taxes-subsidies.html  [2026-08-10]
/practice-questions/edexcel-theme-1/1-3-1-types-of-market-failure.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-3-2-externalities.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-3-3-public-goods.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-3-4-information-gaps.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-4-1-government-intervention-in-markets.html  [2026-08-09]
/practice-questions/edexcel-theme-1/1-4-2-government-failure.html  [2026-08-09]
/practice-questions/edexcel-theme-2/  [2026-08-17]
/practice-questions/edexcel-theme-2/2-1-1-economic-growth.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-1-2-inflation.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-2-2-consumption.html  [2026-08-10]
/practice-questions/edexcel-theme-2/2-2-3-investment.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-2-4-government-expenditure.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-2-5-net-trade.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-3-2-short-run-aggregate-supply.html  [2026-08-10]
/practice-questions/edexcel-theme-2/2-3-3-long-run-aggregate-supply.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-4-1-national-income.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-4-2-injections-withdrawals.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-4-3-equilibrium-levels-of-real-national-output.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-4-4-the-multiplier.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-5-1-causes-of-growth.html  [2026-08-10]
/practice-questions/edexcel-theme-2/2-5-2-output-gaps.html  [2026-08-10]
/practice-questions/edexcel-theme-2/2-5-4-the-impact-of-economic-growth.html  [2026-08-09]
/practice-questions/edexcel-theme-2/2-6-2-demand-side-policies.html  [2026-08-10]
/practice-questions/edexcel-theme-2/2-6-3-supply-side-policies.html  [2026-08-10]
/practice-questions/edexcel-theme-3/  [2026-08-17]
/practice-questions/edexcel-theme-3/3-1-1-sizes-types-of-firms.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-1-2-business-growth.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-1-3-demergers.html  [2026-08-10]
/practice-questions/edexcel-theme-3/3-2-1-business-objectives.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-3-1-revenue.html  [2026-08-10]
/practice-questions/edexcel-theme-3/3-3-2-costs.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-3-4-normal-profits-supernormal-profits-losses.html  [2026-08-10]
/practice-questions/edexcel-theme-3/3-4-1-efficiency.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-4-2-perfect-competition.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-4-3-monopolistic-competition.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-4-4-oligopoly.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-4-5-monopoly.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-4-6-monopsony.html  [2026-08-10]
/practice-questions/edexcel-theme-3/3-4-7-contestability.html  [2026-08-10]
/practice-questions/edexcel-theme-3/3-5-1-demand-for-labour.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-5-2-supply-of-labour.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-5-3-wage-determination.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-6-1-government-intervention.html  [2026-08-09]
/practice-questions/edexcel-theme-3/3-6-2-the-impact-of-government-intervention.html  [2026-08-09]
/practice-questions/edexcel-theme-4/  [2026-08-17]
/practice-questions/edexcel-theme-4/4-1-1-globalisation.html  [2026-08-09]
/practice-questions/edexcel-theme-4/4-1-2-specialisation-trade.html  [2026-08-10]
/practice-questions/edexcel-theme-4/4-1-3-pattern-of-trade.html  [2026-08-09]
/practice-questions/edexcel-theme-4/4-1-4-terms-of-trade.html  [2026-08-09]
/practice-questions/edexcel-theme-4/4-1-5-trading-blocs-and-the-world-trade-organisation.html  [2026-08-10]
/practice-questions/edexcel-theme-4/4-1-6-restrictions-on-free-trade.html  [2026-08-10]
/practice-questions/edexcel-theme-4/4-1-7-balance-of-payments.html  [2026-08-09]
/practice-questions/edexcel-theme-4/4-1-8-exchange-rates.html  [2026-08-09]
/practice-questions/edexcel-theme-4/4-1-9-international-competitiveness.html  [2026-08-09]
/practice-questions/edexcel-theme-4/4-2-1-absolute-relative-poverty.html  [2026-08-09]
/practice-questions/edexcel-theme-4/4-2-2-inequality.html  [2026-08-10]
/practice-questions/edexcel-theme-4/4-3-1-measures-of-development.html  [2026-08-10]
/practice-questions/edexcel-theme-4/4-3-2-factors-influencing-growth-development.html  [2026-08-10]
/practice-questions/edexcel-theme-4/4-4-1-role-of-financial-markets.html  [2026-08-08]
/practice-questions/edexcel-theme-4/4-4-2-market-failure-in-the-financial-sector.html  [2026-08-09]
/practice-questions/edexcel-theme-4/4-4-3-role-of-central-banks.html  [2026-08-10]
/practice-questions/edexcel-theme-4/4-5-1-public-expenditure.html  [2026-08-09]
/practice-questions/edexcel-theme-4/4-5-2-taxation.html  [2026-08-10]
/practice-questions/edexcel-theme-4/4-5-3-public-sector-finances.html  [2026-08-09]
/privacy.html  [2026-08-14]
/revision-notes/  [2026-08-08]
/revision-notes/aqa-a2-macro/  [2026-08-16]
/revision-notes/aqa-a2-macro/2-1-2-macroeconomic-indicators.html  [2026-08-11]
/revision-notes/aqa-a2-macro/2-1-3-uses-of-index-numbers.html  [2026-08-10]
/revision-notes/aqa-a2-macro/2-1-4-uses-of-national-income-data.html  [2026-08-09]
/revision-notes/aqa-a2-macro/2-3-2-employment-and-unemployment.html  [2026-08-09]
/revision-notes/aqa-a2-macro/2-6-1-globalisation.html  [2026-08-10]
/revision-notes/aqa-a2-macro/2-6-2-trade.html  [2026-08-11]
/revision-notes/aqa-a2-macro/2-6-4-exchange-rate-systems.html  [2026-08-10]
/revision-notes/aqa-a2-micro/  [2026-08-16]
/revision-notes/aqa-a2-micro/1-3-6-the-interrelationship-between-markets.html  [2026-08-11]
/revision-notes/aqa-a2-micro/1-5-1-market-structures.html  [2026-08-10]
/revision-notes/aqa-a2-micro/1-5-5-oligopoly.html  [2026-08-09]
/revision-notes/aqa-a2-micro/1-7-3-government-policies-poverty-income-distribution.html  [2026-08-09]
/revision-notes/aqa-a2-micro/1-8-2-the-meaning-of-market-failure.html  [2026-08-09]
/revision-notes/aqa-a2-micro/1-8-6-market-imperfections.html  [2026-08-09]
/revision-notes/edexcel-theme-1/  [2026-08-15]
/revision-notes/edexcel-theme-1/1-1-1-economics-as-a-social-science.html  [2026-08-08]
/revision-notes/edexcel-theme-1/1-1-2-positive-normative-statements.html  [2026-06-01]
/revision-notes/edexcel-theme-1/1-1-3-the-economic-problem.html  [2026-07-05]
/revision-notes/edexcel-theme-1/1-1-4-production-possibility-frontiers.html  [2026-07-27]
/revision-notes/edexcel-theme-1/1-1-5-specialisation-division-of-labour.html  [2026-08-17]
/revision-notes/edexcel-theme-1/1-2-1-rational-decision-making.html  [2026-07-09]
/revision-notes/edexcel-theme-1/1-2-2-demand.html  [2026-05-31]
/revision-notes/edexcel-theme-1/1-2-5-price-elasticity-of-supply.html  [2026-07-21]
/revision-notes/edexcel-theme-1/1-2-7-price-mechanism.html  [2026-06-01]
/revision-notes/edexcel-theme-1/1-3-1-types-of-market-failure.html  [2026-07-31]
/revision-notes/edexcel-theme-1/1-3-4-information-gaps.html  [2026-07-20]
/revision-notes/edexcel-theme-1/1-4-1-government-intervention-in-markets.html  [2026-05-23]
/revision-notes/edexcel-theme-1/1-4-2-government-failure.html  [2026-08-12]
/revision-notes/edexcel-theme-2/  [2026-08-15]
/revision-notes/edexcel-theme-2/2-1-2-inflation.html  [2026-05-24]
/revision-notes/edexcel-theme-2/2-1-3-employment-unemployment.html  [2026-05-24]
/revision-notes/edexcel-theme-2/2-1-4-balance-of-payments.html  [2026-05-24]
/revision-notes/edexcel-theme-2/2-2-1-aggregate-demand.html  [2026-05-24]
/revision-notes/edexcel-theme-2/2-2-2-consumption.html  [2026-05-24]
/revision-notes/edexcel-theme-2/2-2-4-government-expenditure.html  [2026-07-21]
/revision-notes/edexcel-theme-2/2-3-1-aggregate-supply.html  [2026-05-24]
/revision-notes/edexcel-theme-2/2-3-2-short-run-aggregate-supply.html  [2026-05-31]
/revision-notes/edexcel-theme-2/2-5-1-causes-of-growth.html  [2026-07-22]
/revision-notes/edexcel-theme-2/2-5-2-output-gaps.html  [2026-05-24]
/revision-notes/edexcel-theme-2/2-5-4-the-impact-of-economic-growth.html  [2026-05-24]
/revision-notes/edexcel-theme-2/2-6-1-possible-macroeconomic-objectives.html  [2026-05-24]
/revision-notes/edexcel-theme-2/2-6-2-demand-side-policies.html  [2026-05-24]
/revision-notes/edexcel-theme-2/2-6-3-supply-side-policies.html  [2026-07-09]
/revision-notes/edexcel-theme-2/2-6-4-conflicts-between-objectives-and-policies.html  [2026-07-22]
/revision-notes/edexcel-theme-3/  [2026-08-15]
/revision-notes/edexcel-theme-3/3-4-7-contestability.html  [2026-08-08]
/revision-notes/edexcel-theme-3/3-6-2-the-impact-of-government-intervention.html  [2026-05-19]
/revision-notes/edexcel-theme-4/  [2026-08-16]
/revision-notes/edexcel-theme-4/4-1-8-exchange-rates.html  [2026-08-09]
/revision-notes/edexcel-theme-4/4-2-2-inequality.html  [2026-07-29]
/revision-notes/edexcel-theme-4/4-3-2-factors-influencing-growth-development.html  [2026-06-21]
/revision-notes/edexcel-theme-4/4-3-3-strategies-influencing-growth-development.html  [2026-06-23]
/revision-notes/edexcel-theme-4/4-4-1-role-of-financial-markets.html  [2026-06-26]
/revision-notes/edexcel-theme-4/4-4-2-market-failure-in-the-financial-sector.html  [2026-06-26]
/revision-notes/edexcel-theme-4/4-5-3-public-sector-finances.html  [2026-06-10]
/revision-notes/glossary/  [2026-08-15]
/revision-notes/macroeconomics-diagrams.html  [2026-08-18]
/revision-notes/microeconomics-diagrams.html  [2026-08-15]
/tutoring.html  [2026-08-14]
```


---

## Revision log

**21 August 2026, later the same day.** Revised twice after you worked through
`13-…` and supplied three things the morning analysis was missing: the Crawl
stats summary, the PDF crawl time series, and the Performance export.

| What changed | Where | Why |
| --- | --- | --- |
| Added the Performance analysis | new §3a | The export now exists. It answers "did the newly-indexed pages earn anything" — yes, 50 clicks and 3,316 impressions — and surfaces a hub-page decline I had no way to see this morning. |
| "PDFs are not competing for crawl" → **not proven either way** | §4 | Crawl stats puts PDFs at 15% of requests, above the <10% threshold I set before looking. The 90-day window is confounded; the time series decides it. |
| Diagnosis confidence **high → moderate-to-high** | §4 | 108 ms average response time means crawl *capacity* is not the constraint, so this is crawl *demand* — a judgement rather than a queue, and less certain to resolve on its own. |
| PDF recommendation, twice | §7 | First moved to "get the time series and decide", then — once the time series arrived — settled back on **"leave `pdfs.xml` alone, re-decide 1 October on the indexing outcome"**. Same answer as the morning, different and better reasoning under it. |
| ⚠️ **Corrected a factual error of mine**: "no PDF crawled since 6 August" | §4, §7 | Wrong. Crawl stats shows ~128 PDF requests a day on 8–9 August. I had trusted the page-indexing export's `Last crawled` column without allowing for its lag — the exact caveat I had written into "Where the data is soft" and then failed to apply to my own conclusion. |
| Added the derived whole-site crawl rate | §4 | ~3,270 requests in 90 days, ~4 fetches per page. Quantifies the crawl-demand diagnosis for the first time. |
| Two open questions closed, three opened | §10 | Validation state and Performance data resolved; seasonality-vs-consolidation, the PDF time series and queue-vs-judgement opened. |

Nothing in §1, §2, §5, §6 or §8 changed. The reconciliation, the live
verification, the per-reason explanations and the noindex trace all stand as
written.
