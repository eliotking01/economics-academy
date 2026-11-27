# Health check, November 2026 — Phase A measurements

Branch `chore/health-check-2026-11`, cut from `main` at `8f37df16`. Measure
only: nothing on a published page changed in Phase A. One section per brief
item, each committed with its evidence.

## 1. Live Lighthouse re-run (27 November 2026)

`python3 seo/tools/run_lighthouse.py --out seo/lh-live-2026-11-27`: same
script, flags and Lighthouse version (12.8.2) as `seo/lh-live-2026-08-26/`,
three runs per page, medians. The eight August samples are unchanged; four
were appended for the November launches, and the runner now records
`dom-size` (August's DOM figures below are read from its raw reports).
**Headless Chrome moved from 151 to 158 between the two runs.**

| Page | Aug score | LCP | CLS | TBT | Bytes | DOM | Nov score | LCP | CLS | TBT | Bytes | DOM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| homepage | 99 | 1.75 s | 0.000 | 0 ms | 189 KB | 371 | 100 | 1.21 s | 0.045 | 0 ms | 190 KB | 405 |
| section-hub (`/revision-notes/`) | 100 | 1.52 s | 0.000 | 0 ms | 136 KB | 263 | **93** | 1.35 s | **0.153** | 0 ms | 137 KB | 329 |
| notes-topic (MathJax) | 70 | 4.77 s | 0.000 | 106 ms | 606 KB | 1,084 | 98 | 1.28 s | 0.048 | 151 ms | 556 KB | 1,118 |
| practice-questions | 96 | 1.98 s | 0.000 | 0 ms | 247 KB | 487 | 100 | 1.23 s | 0.044 | 0 ms | 299 KB | 521 |
| past-paper-questions (topic) | 98 | 1.57 s | 0.000 | 0 ms | 152 KB | 537 | 100 | 1.23 s | 0.048 | 0 ms | 168 KB | 740 |
| flashcards | 99 | 1.88 s | 0.000 | 0 ms | 195 KB | 401 | 100 | 1.25 s | 0.048 | 0 ms | 196 KB | 433 |
| ppq-board-hub (`/edexcel/`) | 97 | 1.86 s | 0.000 | 19 ms | 199 KB | 938 | 99 | 1.23 s | 0.044 | 111 ms | 261 KB | 1,099 |
| tutoring | 97 | 1.93 s | 0.000 | 65 ms | 197 KB | 485 | 98 | 2.02 s | 0.070 | 0 ms | 230 KB | 523 |
| ppq-aqa-micro | — | — | — | — | — | — | 97 | 1.81 s | 0.045 | 153 ms | 395 KB | 1,018* |
| ppq-edexcel-theme-2 | — | — | — | — | — | — | 99 | 1.53 s | 0.045 | 82 ms | 304 KB | 900* |
| glossary-edexcel-b | — | — | — | — | — | — | **86** | 1.84 s | **0.258** | 0 ms | 278 KB | 5,516 |
| notes-edexcel-b (MathJax) | — | — | — | — | — | — | 98 | 1.28 s | 0.061 | 132 ms | 520 KB | 570 |

\* DOM after `question-search.js` has replaced the static cards with its
first 20 results. The parser still builds the full static list first
(11,189 and 6,212 elements, §3); TBT is where that shows.

**Three readings, one of them checked by A/B:**

- **The ~0.045 CLS on every page is the Chrome upgrade, not the site.** A
  local A/B (`serve_h2.js`, today's Chrome) of the 26 August tree
  (`ae030240`) against today's tree gives the same ~0.045 shift on
  `main#main` on both, on the homepage and the notes hub. The shifting
  node is `main` under `body.mnav-enhanced`, i.e. the mobile-nav
  enhancement in `js/components/nav.js`. Inside "good" (< 0.1), but it is
  on every page and is now visible to the measurement.
- **The `/revision-notes/` hub regressed for real:** 0.05 on the August
  tree against 0.16–0.23 on today's under the same Chrome, with
  `div.exam-board-section` shifting on the web-font swap. The hub gained
  its Edexcel B section in October. Score 100 → 93.
- **The Edexcel B glossary is the worst page sampled:** CLS 0.258 ("poor"
  is > 0.25), a single shift of `main.glossary-page`, with 5,516 elements.
- **The MathJax LCP problem did not reproduce.** August's notes sample was
  bimodal at ~4.8 s; today it is 2.77 / 1.28 / 1.22 s (median 1.28 s), and
  the Edexcel B MathJax page is 1.22–1.36 s. MathJax still carries ~130–150
  ms of TBT on both and is the last third-party origin, but the LCP case
  for item 4 is much weaker than `seo/20` §2 recorded.

## 2. The Search Console read (export of 26–27 November 2026)

**Export:** `seo/gsc-exports/27-11-2026/`. The brief expected `26-11-2026/`;
the folder Eliot exported is dated the 27th, and its indexed list is
`indexed-pages-26-11-2026.csv`. Same filenames as `21-08-2026/` otherwise.

**Command:** `python3 seo/tools/gsc_reconcile.py seo/gsc-exports/27-11-2026
--diff seo/gsc-exports/21-08-2026`. Self-check: all five PASS (1,134 URLs,
each in exactly one bucket).

**One caveat on the Performance export:** its search-type filter reads
`Web (text-based)` where August's reads `Web`. It is the same report under
Search Console's newer label as far as can be told from the file, but that
is not verified, so treat any cross-period comparison of totals as
directional.

### Indexing — old inventory separated from new

"Old" is every URL in the sitemaps at `c55265ea` (the last sitemap commit on
or before 21 August); "new" is everything added since. The site went from
~743 to 1,134 published URLs (812 HTML, 322 PDFs).

| Sitemap | Old URLs | Indexed Aug | Indexed Nov | New URLs | New indexed |
| --- | ---: | ---: | ---: | ---: | ---: |
| revision-notes | 179 | 60 | **128** | 90 | 70 |
| practice-questions | 173 | 155 | 170 | 89 | 7 |
| past-paper-questions | 90 | 76 | 84 | 166 | 29 |
| pdfs | 283 | 11 | 23 | 39 | 3 |
| flashcards | 7 | 7 | 7 | 4 | 3 |
| core | 7 | 5 | 7 | 0 | 0 |
| past-papers | 5 | 5 | 5 | 0 | 0 |

115 of the 117 "unjudged" URLs (in no export at all) are past-paper-question
pages, almost all of the Edexcel B bank and the November section pages,
launched 17–26 November. That is expected at this age, not a finding.

### The three questions OWNER-TODO set in advance

1. **Has "Excluded by 'noindex' tag" cleared to zero? No: 26 → 10.** All ten
   are AQA notes pages whose tag was removed in August. Their `Last crawled`
   dates run from **24 May to 13 July 2026**, so Google has simply not been
   back (trap 9). The verdict describes a page that no longer exists; there
   is nothing to fix in the repo. Eliot's move: Request Indexing on the ten
   (one day's manual quota), or check whether the August validation is still
   open before starting another.
2. **Has revision-notes indexed climbed from 60 towards 130–150? Yes, to
   128 of the 179 old URLs**, just short of the predicted band, plus 70 of
   the 90 new (Edexcel B) pages. 198 of 269 overall.
3. **Has `/revision-notes/` recovered? Yes, and more.** August: 62 clicks
   (previous 28 days 84), position 12.14 (previous 9.13). November: 390
   clicks (previous 314), **position 5.96** (previous 6.50). Position is the
   clean signal here; clicks rose with term time and are inflated (below).

### The `sitemaps/pdfs.xml` decision (scheduled for 1 October)

The rule written in advance was "if Google has still indexed only 11 of the
283 PDFs, stop submitting them". **The trigger is not met:** 23 of the 283
are indexed (26 of 322 overall), and 21 of the 26 indexed PDFs were crawled
in November. PDFs earned 34 clicks and 1,048 impressions in the 28 days
(August: 4 and 506). **Recommendation: keep `pdfs.xml`, and re-decide at
the next read.** Not yet explained: 81 PDFs now sit in
"Duplicate without user-selected canonical" (August: 8), 64 of them crawled
in November. Google has decided they duplicate some other URL; the export
does not say which. Worth a URL-inspect on two or three before the next read.

### Performance — new inventory separated from movement on old pages

Impressions-weighted mean position; canonical `https://` origin only
(`http://`, `www.` and `#fragment` jump-link rows excluded).

| Family | Set | Aug pages | Aug clicks | Aug impr | Aug pos | Nov pages | Nov clicks | Nov impr | Nov pos |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| home | old | 1 | 38 | 635 | 22.5 | 1 | 1,555 | 8,397 | 6.7 |
| revision-notes | old | 61 | 129 | 17,707 | 12.4 | 128 | 1,627 | 101,118 | 5.9 |
| revision-notes | new | 3 | 2 | 65 | 11.8 | 72 | 267 | 58,713 | 6.0 |
| practice-questions | old | 135 | 28 | 1,299 | 20.8 | 169 | 1,065 | 20,727 | 5.9 |
| past-paper-questions | old | 71 | 17 | 1,381 | 22.9 | 85 | 1,523 | 27,277 | 6.2 |
| past-paper-questions | new | 0 | 0 | 0 | — | 48 | 200 | 3,049 | 6.5 |
| past-papers (incl. PDFs) | old | 17 | 20 | 4,354 | 24.2 | 25 | 61 | 6,059 | 10.6 |
| flashcards | old | 6 | 0 | 62 | 24.4 | 7 | 124 | 2,499 | 5.4 |
| root pages | old | 6 | 11 | 368 | 21.2 | 6 | 65 | 4,690 | 9.7 |

Site totals from `Pages.csv`: clicks 248 → 6,523, impressions 26,609 →
233,015. **The old pages moved, not just the inventory:** the 128 old notes
pages now ranking average position 5.9 against 12.4, and carry about two
thirds of all notes impressions.

**What I cannot tell you from the files:** how much of the November click
total is real. Brand queries are 4.5% of impressions but **1,099 of 1,474
query clicks (75%)**, against 2.7% and 51% in August. Some is students
returning by name in term time, and some is the people building the site:
November had nine launch phases, and the Rank-check log has no entry since
25 August. Impressions and positions are usable. Treat clicks and CTR as
unreliable, as §1 did in August.

The scheduled Sept–Nov comparisons in OWNER-TODO ("~22 September GSC check",
the home-page baseline of 223 clicks and position 17.35) are all superseded
by this read: the home page is at position 6.71.

### §1 pattern analysis (`seo/14-notes-keyword-brief.md`), re-run

Method checked first: re-running it on the August `Queries.csv` reproduces
§1's own table to 0.1 points, including the 670-query "least-contaminated"
subset and the 2.7% brand share. Brand = `econ(omics|omy)? academy`, the
domain, `econacademy`.

| Pattern | Aug all | Nov all | Aug non-brand | Nov non-brand | Aug least-contam. | Nov least-contam. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| "a level" | 41.2% | 39.8% | 42.3% | 41.7% | 36.1% | 26.9% |
| past paper | 17.6% | 9.9% | 18.1% | 10.4% | 21.7% | 16.9% |
| edexcel | 17.0% | 5.3% | 17.5% | 5.5% | 8.3% | 4.3% |
| diagram / graph | 9.2% | 9.5% | 9.5% | 10.0% | 7.3% | 2.6% |
| revision | 9.3% | 3.5% | 9.6% | 3.6% | 4.0% | 2.1% |
| definition-type | 6.4% | 5.6% | 6.6% | 5.9% | 7.3% | 3.9% |
| aqa | 6.1% | 7.0% | 6.3% | 7.3% | 10.4% | 7.0% |
| notes | 5.6% | 1.9% | 5.7% | 1.9% | 2.9% | 0.6% |
| tutor / tuition | 5.0% | 7.8% | 5.1% | 8.2% | 8.5% | 12.2% |
| ocr | 4.7% | 0.9% | 4.8% | 0.9% | 6.8% | 5.0% |
| theme | 1.7% | 3.6% | 1.7% | 3.8% | 1.1% | 0.5% |
| spec code | 0.1% | 0.3% | 0.1% | 0.3% | 0.1% | 0.0% |
| question / MCQ | 0.4% | 2.8% | 0.4% | 2.7% | 0.5% | 0.9% |

Queries 1,076 → 1,316 with impressions; impressions 5,563 → 37,833. The
least-contaminated subset (non-brand, zero clicks, position worse than 10)
shrank from 669 queries / 3,142 impressions to **248 / 4,534**. That is
because most queries now rank inside the top 10, so the filter means less
than it did and its column is the weakest of the three. Query length,
impression-weighted: 2 words 24.6%, 3 words 27.5%, 4 words 14.3%; 66% from
two-to-four-word queries (August 62%).

**What moved:**

- **§1's three conclusions all hold.** The topic name is the query. Spec
  codes stay negligible (0.3%). Diagram/graph demand is unchanged at 9.5%
  of all impressions.
- **"Past paper" and "Edexcel" shares fell sharply.** That is dilution, not
  loss: notes impressions grew about nine-fold (`Pages.csv`), so board and
  past-paper queries make up a smaller share of a far larger total.
- **Tutor/tuition rose to 7.8%** (12.2% in the strict subset), the queries
  that pay. The tutoring page sits at position 10.19 (August 25.75).
- **Question/MCQ queries appeared** (0.4% → 2.8%), plausibly the November
  bank launches.

The Pages-side picture above says the same thing: the old notes pages
ranking around position 6 now carry the site.

## 3. Payload map for the past-paper bank

Measured on the committed tree at `8f37df16`. "Served" is the gzip transfer
GitHub Pages actually sends (`curl -H 'Accept-Encoding: gzip'`, 27 Nov);
"gz" is local gzip -9, about 10% smaller than served. Elements are start
tags counted by `html.parser`. The fetch is chosen in
`js/components/question-search.js` `boot()`: the first
`[data-question-search]`'s `data-src`, else `/past-paper-questions/questions.json`.
It fires at `DOMContentLoaded` on every page, whether or not the visitor
touches the filters.

| Page type | Example | HTML raw | HTML served | Elements | Fetches | JSON raw | JSON served | Questions in JSON |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Master search | `/past-paper-questions/` | 33 KB | 7 KB | 344 | master `questions.json` (default, no `data-src`) | 1,490 KB | 258 KB | all boards |
| Board hub | `/aqa/` | 108 KB | 14 KB | 982 | `aqa/questions.json` | 705 KB | 129 KB | 909 |
| Board hub | `/edexcel/` | 108 KB | — | 984 | `edexcel/questions.json` | 544 KB | 88 KB | 781 |
| Board hub | `/edexcel-b/` | 104 KB | — | 908 | `edexcel-b/questions.json` | 243 KB | 34 KB | 362 |
| Section | `/aqa/microeconomics/` | 1,383 KB | 120 KB | 11,189 | **whole AQA board** | 705 KB | 129 KB | 909 (471 its own) |
| Section | `/aqa/macroeconomics/` | 1,321 KB | — | 10,703 | **whole AQA board** | 705 KB | 129 KB | 909 (462 its own) |
| Section | `/edexcel/theme-1/` | 768 KB | — | 5,627 | **whole Edexcel A board** | 544 KB | 88 KB | 781 (280) |
| Section | `/edexcel/theme-2/` | 824 KB | 56 KB | 6,212 | **whole Edexcel A board** | 544 KB | 88 KB | 781 (305) |
| Section | `/edexcel/theme-3/` | 330 KB | — | 2,456 | **whole Edexcel A board** | 544 KB | 88 KB | 781 (115) |
| Section | `/edexcel/theme-4/` | 401 KB | — | 2,990 | **whole Edexcel A board** | 544 KB | 88 KB | 781 (140) |
| Section | `/edexcel-b/theme-1/` … `theme-4/` | 210–411 KB | — | 1,540–2,915 | **whole Edexcel B board** | 243 KB | 34 KB | 362 (67–149) |
| Topic (242 pages) | median | 56 KB | — | 499 | its own `<topic>/questions.json` | — | — | its own |
| Topic | largest, `/aqa/2-5-1-fiscal-policy/` | 223 KB | 21 KB | 1,885 | its own | 73 KB | 11 KB | 71 |

**What a per-section JSON would weigh** (the board file filtered to the
section's `groups` and `topics`, every other key kept, compact JSON):

| Section | Questions | Today raw / gz | Per-section raw / gz | Saved gz |
| --- | ---: | ---: | ---: | ---: |
| AQA micro | 471 | 705 / 124 KB | ~393 / 68 KB | ~56 KB |
| AQA macro | 462 | 705 / 124 KB | ~352 / 55 KB | ~69 KB |
| Edexcel A Theme 1 | 280 | 544 / 84 KB | ~215 / 31 KB | ~53 KB |
| Edexcel A Theme 2 | 305 | 544 / 84 KB | ~214 / 27 KB | ~57 KB |
| Edexcel A Theme 3 | 115 | 544 / 84 KB | ~105 / 15 KB | ~69 KB |
| Edexcel A Theme 4 | 140 | 544 / 84 KB | ~117 / 16 KB | ~68 KB |
| Edexcel B Themes 1–4 | 67–149 | 243 / 32 KB | ~64–106 / 8–13 KB | ~19–24 KB |

AQA's sections overlap by 24 questions (471 + 462 = 933 > 909); a question
tagged to both groups would appear in both files.

**Where the weight actually is.** On the heaviest page (AQA micro) the
static HTML, not the JSON, is the bigger cost: 1.38 MB raw, 120 KB served,
11,189 elements for 471 cards of about 2.9 KB each. 39% of the raw bytes are
Prettier's indentation, but gzip absorbs most of that: stripping it saves
~15% of the gzipped transfer, so whitespace is not the lever. The element
count is the lever, and only a change to what the no-JS page shows moves
it (the brief rules that out without asking). Wrapping cards in `<details>`
would not help, since collapsed content is still parsed; splitting the page
would mint new, permanent URLs. The JSON
fetch duplicates the static cards in data form; about half of it is the
other section's questions on every section page.

The master search page is the opposite shape: light HTML (7 KB served) and
the heaviest single fetch in the bank (258 KB served, 1.49 MB to parse),
because it has no static list and searches every board.
