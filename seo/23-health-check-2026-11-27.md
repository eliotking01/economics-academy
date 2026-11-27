# Health check, November 2026 — Phase A measurements

Branch `chore/health-check-2026-11`, cut from `main` at `8f37df16`. Measure
only: nothing on a published page changed in Phase A. One section per brief
item, each committed with its evidence.

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
