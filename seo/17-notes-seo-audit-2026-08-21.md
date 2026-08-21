# Revision notes: on-page SEO audit

21 August 2026. The 166 generated topic pages under `revision-notes/`, their
seven hub pages, `revision-notes/index.html` and the two diagram galleries —
176 pages in scope, counted by `python3 seo/tools/notes_baseline.py`, not from
a number written down.

**Strategy**: `seo/14-notes-keyword-brief.md`. **Owner tasks**:
`seo/15-notes-seo-manual-todo-2026-08-21.md`. **URLs**:
`seo/16-url-structure-and-redirect-options.md`. **Approval needed**:
`seo/18-notes-content-approval-2026-08-21.md`. **Rename option**:
`seo/19-notes-url-rename-proposal-2026-08-21.md`.

**Before and after**: `seo/17-notes-baseline-2026-08-21.csv` and
`seo/17-notes-after-2026-08-21.csv`, one row per page, regenerate either with
`python3 seo/tools/notes_baseline.py --out <path>`.

Every finding below is labelled with what it rests on:

- **[repo]** — measured in this repository by a script named beside it.
- **[SERP]** — read off a live search result page or a competitor's own HTML
  on 21 August 2026.
- **[GSC]** — from `seo/gsc-exports/21-08-2026/`.

> **The Search Console caveat, stated once.** These exports are contaminated by
> the site owner's and AI assistants' own searching while building the site,
> and the window is the dead middle of the summer holiday. Brand queries are
> 2.7% of impressions but 51% of clicks, so **no click, CTR or position figure
> from them is used anywhere in this report**, and no page is ranked by clicks.
> Impressions are used directionally at the pattern level only, and only as the
> brief has already filtered them. The one exception is index coverage: which
> URLs Google has crawled and indexed is a factual report about the crawler,
> not a performance metric, and is used directly.
>
> **No traffic or click forecast appears in this report.** There is not enough
> clean data to support a number, and an invented one is worse than none.

---

## The five things costing the most traffic

Most important first.

### 1. The topic name came last in all 166 titles — FIXED

**[repo]** Every one of the 166 topic pages carried
`{Board} A-Level Economics {code} {Topic}`. The words a student actually types
were behind two things almost nobody types.

**[GSC]** Spec-code queries are **4 impressions in 28 days, 0.1% of the
total**, and 0.1% under every filter the brief applies, including the
least-contaminated subset. **[SERP]** Six of the seven competing sites put the
topic name first; the two that do not are the two selling spec-code navigation
to teachers, and both run parallel code-free pages as well.

**Effect:** the title is the strongest on-page ranking signal there is and the
only one a student reads before deciding whether to click. Every one of these
166 titles was spending its most valuable characters on a string with
measurably no demand.

**Applied.** 166 titles rewritten to the §4 formula; 43 keep an Edexcel code in
brackets after the topic name, 0 AQA titles carry one. Locked by
`verify_seo.py` assertion 15.

### 2. The revision notes are the worst-indexed section of the site

**[GSC]** **59 of the 176 in-scope pages are indexed — 33.5%.** The site as a
whole is at 66.5% (`seo/11-gsc-index-audit-2026-08-21.md`). So the section that
should be the top of the funnel is indexed at half the site's own rate.

| Verdict | In-scope URLs |
| --- | ---: |
| Indexed | 59 |
| Discovered — currently not indexed | 87 |
| Excluded by 'noindex' tag | 26 |
| Crawled — currently not indexed | 4 |

The 26 "noindex" pages **carry no noindex tag and have not since 30 July**.
That was established on 21 August and needs a recrawl, not a fix —
`seo/11-` §2 and `seo/12-`. Nothing in this audit changes it.

**Effect:** an unindexed page cannot rank at whatever its title says. This is
the ceiling on everything else in this report, and the reason task 5 of the
manual to-do list — resubmit the sitemap, request indexing on two changed
pages — is worth more of Eliot's fifteen minutes than anything else on it.

### 3. Nothing on any topic page said when it was written or by whom

**[repo]** 0 of 166 `LearningResource` blocks carried `datePublished`,
`dateModified` or an author. No page displayed a date. **[SERP]** tutor2u
prints "Last updated 19 Sept 2023"; Economics Help prints both a published and
an updated date and a named author with an Oxford PPE line; TutorChase prints
"Dave — Cambridge University, BA Hons Economics, over 8 years of tutoring".

**Effect:** freshness and authorship are the two signals a search engine can
only read if a page states them, and on a subject where the syllabus and the
data both change annually a student reads them too.

**Partly applied.** Dates are in, in the schema and visible on the page, taken
from git rather than invented. **The named author is not** — it needs Eliot's
own words and is task 4 of the manual list. It is the single highest-value
thing on that list.

### 4. There was no way from a topic to the same topic on the other board

**[repo]** Before this pass the site carried **zero cross-board links** outside
the glossary's own board selector — by design, and the design was too strict.
**[SERP]** Save My Exams routinely ranks its AQA *and* its Edexcel page for the
same topic on one page-one SERP; splitting by board is not self-cannibalising
for them.

**Effect:** a student searching "monopoly a level economics" without naming a
board lands on whichever page Google picks and, if it is the wrong one, leaves.

**Applied.** 109 directed twin links from a hand-verified table with its
evidence recorded per row, `scripts/notes_twins.py`. `verify_seo.py` assertion
13 is amended to permit exactly those pairs and nothing else, so it still
fails on any cross-board link the table does not name.

### 5. 72 of 166 pages carry no diagram, and 84 diagrams are sitting on disk

**[repo]** 72 pages contain no `<img>` and no inline `<svg>`;
`images/diagrams/` holds 106 PNGs of which 5 are used on no page at all.
**[GSC]** Diagram and graph queries are 7.3–9.2% of impressions depending on
the filter — the third-largest pattern, ahead of "notes" and "revision".
**[SERP]** Save My Exams's AQA monopoly page is titled *"Monopoly diagram
economics — A Level Economics Revision Notes"*: they have optimised that page
around the diagram query, and the board is not in the title at all.

**Effect:** economics is a diagram subject and this is a demand pool the site
is not serving on 43% of its topic pages.

**Not applied — needs Eliot.** Placing a diagram changes what a student reads.
The full 72-row table is in §7 below: **43 pages have a matching diagram
already on disk**, 9 want one drawn, 20 need none.

---

## 1. Titles and descriptions

**[repo]** Measured by `seo/tools/notes_baseline.py` before and after.

| | Before | After |
| --- | --- | --- |
| Titles leading with the topic name | 0 / 166 | **166 / 166** |
| Title length (min / median / max) | 33 / 51 / 64 | 44 / 58 / 65 |
| Titles over 60 characters | 4 | 17 |
| Titles over 65 characters | 0 | **0** |
| Spec code in the title | 166 | 43, all Edexcel |
| Spec code in an AQA title | 79 | **0** |
| Duplicate titles | 0 | 0 |
| Description length (min / median / max) | 151 / 156 / 170 | 142 / 157 / 168 |
| Descriptions in the 145–158 band | 147 | 145 |
| Duplicate descriptions | 0 | 0 |
| `og:`/`twitter:` mirrors out of sync | 0 | 0 |
| Hub title length (min / median / max) | 67 / 80 / 108 | **41 / 53 / 60** |
| Hub description length | 177 / 230 / 247 | **146 / 151 / 157** |

**Be honest about the description numbers.** The band was already almost met —
147 of 166 — and after the rewrite it is 145. **The gain here is the
front-loading, not the length.** Twenty descriptions run 159–168 and one runs
142; the ceiling could only be reached by dropping an item from each page's own
sub-concept list, and a scripted attempt at that mangled 25 of them ("and
and", "how demand, supply set price"). `seo/tools/notes_titles.py` records the
attempt and why there is no list-shortening code. The 20 are named in
`seo/18-` item 6; my recommendation there is to leave them.

**Titles over 60.** Seventeen sit between 61 and 65, all at the formula's last
variant, which the brief permits explicitly ("never exceed 65, even at variant
5"). Google truncates on pixel width rather than characters, so a 62-character
title with narrow letters often shows in full.

**One display-name collision, logged not resolved.** Edexcel carries "Balance
of Payments" twice — Theme 2's 2.1.4 as a measure of macroeconomic performance
and Theme 4's 4.1.7 as international economics. The brief says to log a
same-board collision rather than disambiguate it by reinstating the code, but
`verify_seo.py` assertion 6 requires unique titles across the whole site and
runs in CI, so two identical titles cannot ship. Both keep a code-bearing
variant and the collision is item 5 of the approval document.

**Thirty-six pages use a display name rather than their H1**, because their H1
does not fit even the shortest variant — AQA 1.6.3's is 104 characters. Each
name is lifted from that page's own current `<title>`, so none is invented.
Approved 2026-08-21; every one is listed in `seo/18-` item 2 and can be vetoed
singly. Six of the 36 lead with an abbreviation and are a separate proposal.

## 2. Headings

**[repo]**

| | Before | After |
| --- | --- | --- |
| Pages with exactly one `<h1>` | 166 | 166 |
| Heading-level skips (h2 → h4 and similar) | **0** | 0 |
| `<h1>`s carrying a spec-code prefix | **79 of 166** | **0** |
| `<h2>` elements carrying a stable `id` | **0 of 1,159** | **1,159 of 1,159** |
| Pages with a table of contents | 0 | 166 |

Heading structure was already sound: no skips anywhere, one `<h1>` per page,
and every `<h2>` open tag bare and identically formed across all 1,159 — which
is what made adding ids a safe attribute insertion rather than a rewrite.

**The AQA code prefix.** **79 of 166 H1s are code-prefixed**
(`2.6.5 Economic Growth and Development`); the 87 Edexcel H1s are the bare
topic name. Two conventions in one folder. `docs/audit/DO-NOT-BREAK.md` says
the prefix "stays until the day-45 read" (PH05-021) because on the
near-identical Edexcel/AQA pairs it is the last textual differentiator. The
brief recommended stripping it.

> **RESOLVED 21 August 2026: Eliot said strip them, and they are stripped.**
> All 166 `<h1>`s are now the bare topic name, and the table above is the
> before-state. `DO-NOT-BREAK.md`'s PH05-021 is lifted and `DECISIONS.md` D53
> records why: re-measured on the current prose, no cross-board pair reaches
> 0.95 similarity and only six reach 0.80, and each of those six is now
> separated four further ways that did not exist when PH05-021 was written.
> `verify_seo.py` assertion 19 holds the line, scoped per board.

The spec sub-label added under every H1 in this pass is what makes that
decision cheap either way: the code is now visible as markup on all 166 pages,
so removing it from the 79 AQA headings loses nothing a student can see.

## 3. Search intent coverage

**[repo]**, against the query clusters the brief identifies in §1.

| Cluster | Coverage found |
| --- | --- |
| Bare topic name | 166 / 166 pages now lead their title with it |
| Definition ("what is X", "X definition") | 154 / 166 carry a `key-definition` chip; **124** carry one in the page's first section; 46 first `<h2>`s use an explicit definition word |
| Diagram ("X diagram", "X graph") | **94 / 166** carry an image or inline SVG |

**Twelve pages carry no `key-definition` chip at all**, which on a
definition-cluster topic is a real gap:
`1-1-2-the-nature-and-purpose-of-economic-activity`, `1-1-3-economic-resources`,
`1-3-6-the-interrelationship-between-markets`,
`1-6-3-wage-determination-perfectly-competitive-labour-markets`,
`1-6-4-wage-determination-imperfectly-competitive-labour-markets`,
`1-7-3-government-policies-poverty-income-distribution` (all AQA micro);
`2-2-4-government-expenditure`, `2-2-5-net-trade`,
`2-4-2-injections-withdrawals`,
`2-4-3-equilibrium-levels-of-real-national-output`,
`2-5-4-the-impact-of-economic-growth`, `4-4-1-role-of-financial-markets`
(Edexcel).

**Nothing was rewritten.** Adding a definition to a page is a content change
and is item 7 of the approval document.

## 4. Structured data

**[repo]** `verify_seo.py` assertion 8: 926 JSON-LD blocks across the site,
all parse. All 166 topic pages and all 7 hubs carry both `LearningResource`
and `BreadcrumbList`; assertion 14 holds the breadcrumb.

Added to every `LearningResource` per §7:

| Field | Source |
| --- | --- |
| `datePublished` | the earlier of the slice's first commit and the rendered page's, both `--follow` |
| `dateModified` | the last commit touching the slice |
| `author`, `publisher` | `@id` reference to the existing `#organization` node |
| `audience` | `EducationalAudience`, `educationalRole: student` |
| `about` | `Thing` with the topic name |
| `educationalAlignment` | `alignmentType: educationalSubject`; Edexcel gets board, theme and unit, **AQA gets board and module and no code** |
| `timeRequired` | `PT{n}M` at 200 words a minute, floor 2 |

`datePublished` spans 2025-06-15 to 2026-08-11 and is not invented. Seventeen
slices were created whole during the Wave 2 migration and `--follow` cannot see
past that; taking the earlier of the two dates recovers 2025-09-01 for
`1-3-3-public-goods` where the slice alone would have claimed 2026-08-11.

**No AQA site-local code appears in any structured-data field.** Publishing
`1.4.2` inside an `educationalAlignment` would assert it as a specification
reference, which is the one thing it is not.

**Not added, deliberately:** `FAQPage` (Google stopped showing FAQ rich results
on 7 May 2026 and is removing the search appearance, the report and Rich
Results Test support), `HowTo` (deprecated on mobile, August 2023), and
practice-problem / `Quiz` markup (deprecation announced November 2025). All
three would be harmless and would earn nothing.

**One thing left alone:** `LearningResource.description` is a longer,
differently worded field from the meta description and always has been. The two
are not required to agree, and rewriting it would put a second set of new
sentences on 166 pages for no search gain.

## 5. Internal links

**[repo]** `python3 seo/tools/link_graph.py`.

| | Before | After |
| --- | --- | --- |
| Broken internal links | 0 | 0 |
| Case-mismatched internal links | 0 | 0 |
| Orphans (0 static inbound) | 0 | 0 |
| Maximum click depth from the homepage | 3 | 3 |
| Topic pages linking to a sibling | 166 / 166 | 166 / 166 |
| Topic pages with an editorial related-topic link | **109 / 166** | 166 / 166 |
| Topic pages with a link to their twin on the other board | **0** | **109** |
| Internal links out of the 166, total | 2,323 | 2,831 |
| Generic anchors ("click here", "read more") | **0** | 0 |

Link hygiene was already excellent and nothing here was broken. The 923
"generic" anchors `link_graph.py` reports are all the breadcrumb's own "Home",
which is correct.

**The real gap was lateral reach.** 57 of the 166 had no editorial link to a
related topic — only the previous/next chain, which reaches exactly two pages.
Every page now carries up to three same-sub-unit siblings, and 109 carry the
twin.

**Twins are derived from topic identity, never from the spec code.** 37 codes
collide across the two boards. The map was seeded by taking the mutual best
match on 5-word-shingle Jaccard similarity of the two pages' prose, then read
row by row; eight rows were changed or added by hand and say so. 57 pages have
no counterpart worth linking — `python3 scripts/notes_twins.py --unpaired`
lists them with the best score found, so the next session can see what was
considered rather than repeat the search. Edexcel's "Demand-Side Policies" is
the clearest of these: it is monetary *and* fiscal, which AQA separates into
2.4.3 and 2.5.1, so it is a twin of neither half.

## 6. Crawl and index basics

Kept short: the deep version was done on 21 August and is in `seo/11-` and
`seo/12-`.

**[repo]** All 461 indexable pages self-canonicalise (assertion 3). All 176
in-scope pages are in `sitemaps/revision-notes.xml` with a valid `lastmod`
(assertion 9). `robots.txt` disallows nothing and names the sitemap (assertion
10). No in-scope page carries a `noindex` (assertion 7).

**[GSC]** The index-coverage figures are in finding 2 above. Nothing in scope
is 404ing, redirecting, or reported as a duplicate without a user-selected
canonical.

**One thing was deliberately not touched.** `revision-notes/index.html` is on
the frozen-head list — `docs/audit/DECISIONS.md` D50, "crown jewel" — and keeps
its `<title>`, H1, meta description and canonical byte-identical.

## 7. Images and diagrams

**[repo]** 211 `<img>` elements across the 166 topic pages. **Alt text needs no
work at all**: 0 missing, 0 empty, shortest 85 characters, median 113, and every
one describes what the diagram shows rather than saying "diagram". 0 images are
missing `width`/`height`. That was on the fix list and turned out not to need
fixing.

**72 pages carry no image and no inline SVG.** The table below is the three
columns asked for. Every diagram named exists on disk — checked, not typed —
and `comparative-advantage.png` is one of the five currently used on no page at
all.

**Summary: 43 place an existing diagram, 9 want one drawn, 20 need none.**

| Page | Topic | Matching diagram on disk | Suggested action |
| --- | --- | --- | --- |
| `aqa-a2-macro/2-1-1-the-objectives-of-government-economic-policy.html` | AQA 2.1.1 The Objectives of Government Economic Policy | none | no diagram needed - a list of objectives |
| `aqa-a2-macro/2-1-2-macroeconomic-indicators.html` | AQA 2.1.2 Macroeconomic Indicators | none | no diagram needed - definitions and measurement |
| `aqa-a2-macro/2-1-3-uses-of-index-numbers.html` | AQA 2.1.3 Uses of Index Numbers | none | no diagram needed - a worked calculation page |
| `aqa-a2-macro/2-1-4-uses-of-national-income-data.html` | AQA 2.1.4 Uses of National Income Data | `circular-flow-of-income.png` | place |
| `aqa-a2-macro/2-2-3-the-determinants-of-aggregate-demand.html` | AQA 2.2.3 The Determinants of Aggregate Demand | `ad-shift-right.png` | place |
| `aqa-a2-macro/2-3-2-employment-and-unemployment.html` | AQA 2.3.2 Employment and Unemployment | `short-run-phillips-curve.png` | place |
| `aqa-a2-macro/2-4-1-the-structure-of-financial-markets-and-financial-assets.html` | AQA 2.4.1 The Structure of Financial Markets and Finan | none | draw - bond price against yield |
| `aqa-a2-macro/2-4-2-commercial-banks-and-investment-banks.html` | AQA 2.4.2 Commercial Banks and Investment Banks | none | no diagram needed - institutions and balance sheets |
| `aqa-a2-macro/2-4-4-the-regulation-of-the-financial-system.html` | AQA 2.4.4 The Regulation of the Financial System | none | no diagram needed - regulators and ratios |
| `aqa-a2-macro/2-6-1-globalisation.html` | AQA 2.6.1 Globalisation | none | no diagram needed - drivers and impacts |
| `aqa-a2-macro/2-6-3-the-balance-of-payments.html` | AQA 2.6.3 The Balance of Payments | `j-curve.png` | place |
| `aqa-a2-micro/1-1-1-economic-methodology.html` | AQA 1.1.1 Economic Methodology | `ppf-basic.png` | place |
| `aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html` | AQA 1.1.2 The Nature and Purpose of Economic Activity | `ppf-basic.png` | place |
| `aqa-a2-micro/1-1-3-economic-resources.html` | AQA 1.1.3 Economic Resources | `ppf-basic.png` | place |
| `aqa-a2-micro/1-1-4-scarcity-choice-and-the-allocation-of-resources.html` | AQA 1.1.4 Scarcity, Choice and the Allocation of Resou | `ppf-basic.png` | place |
| `aqa-a2-micro/1-2-2-imperfect-information.html` | AQA 1.2.2 Imperfect Information | `underconsumption.png` | place |
| `aqa-a2-micro/1-2-3-aspects-of-behavioural-economic-theory.html` | AQA 1.2.3 Aspects of Behavioural Economic Theory | none | no diagram needed - biases and heuristics |
| `aqa-a2-micro/1-2-4-behavioural-economics-and-economic-policy.html` | AQA 1.2.4 Behavioural Economics and Economic Policy | none | no diagram needed - choice architecture |
| `aqa-a2-micro/1-4-1-production-and-productivity.html` | AQA 1.4.1 Production & Productivity | none | draw - total, average and marginal product |
| `aqa-a2-micro/1-4-2-specialisation-division-of-labour-and-exchange.html` | AQA 1.4.2 Specialisation, Division of Labour and Excha | `comparative-advantage.png` | place - the asset exists and is used nowhere |
| `aqa-a2-micro/1-4-3-the-law-of-diminishing-returns-and-returns-to-scale.html` | AQA 1.4.3 The Law of Diminishing Returns and Returns t | `short-run-costs.png` | place |
| `aqa-a2-micro/1-4-8-technological-change.html` | AQA 1.4.8 Technological Change | none | no diagram needed - invention against innovation |
| `aqa-a2-micro/1-5-1-market-structures.html` | AQA 1.5.1 Market Structures | none | draw - the competition spectrum |
| `aqa-a2-micro/1-5-8-the-dynamics-of-competition-and-competitive-market-processes.html` | AQA 1.5.8 The Dynamics of Competition and Competitive  | `perfect-competition-profit-to-longrun.png` | place |
| `aqa-a2-micro/1-6-7-discrimination-in-the-labour-market.html` | AQA 1.6.7 Discrimination in the Labour Market | none | draw - a discriminating employer's MRP |
| `aqa-a2-micro/1-7-2-the-problem-of-poverty.html` | AQA 1.7.2 The Problem of Poverty | `lorenz-curve.png` | place |
| `aqa-a2-micro/1-7-3-government-policies-poverty-income-distribution.html` | AQA 1.7.3 Government Policies to Alleviate Poverty and | `lorenz-curve.png` | place |
| `aqa-a2-micro/1-8-2-the-meaning-of-market-failure.html` | AQA 1.8.2 The Meaning of Market Failure | `overproduction.png` | place |
| `aqa-a2-micro/1-8-3-public-goods-private-goods-and-quasi-public-goods.html` | AQA 1.8.3 Public Goods, Private Goods and Quasi-Public | none | no diagram needed - non-rivalry and non-excludability |
| `aqa-a2-micro/1-8-6-market-imperfections.html` | AQA 1.8.6 Market Imperfections | `underconsumption.png` | place |
| `aqa-a2-micro/1-8-7-competition-policy.html` | AQA 1.8.7 Competition Policy | `net-welfare-loss-monopoly.png` | place |
| `aqa-a2-micro/1-8-10-government-failure.html` | AQA 1.8.10 Government Failure | `max-price.png` | place |
| `edexcel-theme-1/1-1-1-economics-as-a-social-science.html` | Edexcel 1.1.1 Economics as a Social Science | `ppf-basic.png` | place |
| `edexcel-theme-1/1-1-2-positive-normative-statements.html` | Edexcel 1.1.2 Positive and Normative Statements | none | no diagram needed - fact against value judgement |
| `edexcel-theme-1/1-1-3-the-economic-problem.html` | Edexcel 1.1.3 The Economic Problem | `ppf-basic.png` | place |
| `edexcel-theme-1/1-1-5-specialisation-division-of-labour.html` | Edexcel 1.1.5 Specialisation and the Division of Labour | `comparative-advantage.png` | place - the asset exists and is used nowhere |
| `edexcel-theme-1/1-1-6-types-of-economies.html` | Edexcel 1.1.6 Types of Economies | none | no diagram needed - a comparison of systems |
| `edexcel-theme-1/1-2-1-rational-decision-making.html` | Edexcel 1.2.1 Rational Decision Making | `total-utility.png` | place |
| `edexcel-theme-1/1-2-10-alternative-views-of-consumer-behaviour.html` | Edexcel 1.2.10 Alternative Views of Consumer Behaviour | none | no diagram needed - biases and heuristics |
| `edexcel-theme-1/1-3-1-types-of-market-failure.html` | Edexcel 1.3.1 Types of Market Failure | `overproduction.png` | place |
| `edexcel-theme-1/1-3-3-public-goods.html` | Edexcel 1.3.3 Public Goods | none | no diagram needed - non-rivalry and non-excludability |
| `edexcel-theme-1/1-3-4-information-gaps.html` | Edexcel 1.3.4 Information Gaps | `underconsumption.png` | place |
| `edexcel-theme-1/1-4-2-government-failure.html` | Edexcel 1.4.2 Government Failure | `max-price.png` | place |
| `edexcel-theme-2/2-1-1-economic-growth.html` | Edexcel 2.1.1 Economic Growth | `ppf-growth-decline.png` | place |
| `edexcel-theme-2/2-1-3-employment-unemployment.html` | Edexcel 2.1.3 Employment and Unemployment | `short-run-phillips-curve.png` | place |
| `edexcel-theme-2/2-1-4-balance-of-payments.html` | Edexcel 2.1.4 Balance of Payments | `j-curve.png` | place |
| `edexcel-theme-2/2-2-2-consumption.html` | Edexcel 2.2.2 Consumption | none | draw - the consumption function |
| `edexcel-theme-2/2-2-3-investment.html` | Edexcel 2.2.3 Investment | none | draw - the accelerator, or investment against the interest rate |
| `edexcel-theme-2/2-2-4-government-expenditure.html` | Edexcel 2.2.4 Government Expenditure | `ad-shift-right.png` | place |
| `edexcel-theme-2/2-2-5-net-trade.html` | Edexcel 2.2.5 Net Trade | `j-curve.png` | place |
| `edexcel-theme-2/2-5-4-the-impact-of-economic-growth.html` | Edexcel 2.5.4 The Impact of Economic Growth | `ppf-growth-decline.png` | place |
| `edexcel-theme-2/2-6-1-possible-macroeconomic-objectives.html` | Edexcel 2.6.1 Possible Macroeconomic Objectives | `short-run-phillips-curve.png` | place |
| `edexcel-theme-3/3-1-1-sizes-types-of-firms.html` | Edexcel 3.1.1 Sizes and Types of Firms | none | no diagram needed - firm types and the divorce of ownership |
| `edexcel-theme-3/3-1-2-business-growth.html` | Edexcel 3.1.2 Business Growth | `economies-of-scale.png` | place |
| `edexcel-theme-3/3-1-3-demergers.html` | Edexcel 3.1.3 Demergers | none | no diagram needed - reasons and impacts |
| `edexcel-theme-3/3-4-6-monopsony.html` | Edexcel 3.4.6 Monopsony | `monopsony.png` | place - exact match, and the page has none |
| `edexcel-theme-3/3-6-2-the-impact-of-government-intervention.html` | Edexcel 3.6.2 The Impact of Government Intervention | `nationalisation-privatisation.png` | place |
| `edexcel-theme-4/4-1-1-globalisation.html` | Edexcel 4.1.1 Globalisation | none | no diagram needed - drivers and impacts |
| `edexcel-theme-4/4-1-3-pattern-of-trade.html` | Edexcel 4.1.3 Pattern of Trade | `comparative-advantage.png` | place - the asset exists and is used nowhere |
| `edexcel-theme-4/4-1-4-terms-of-trade.html` | Edexcel 4.1.4 Terms of Trade | none | draw - terms of trade against export revenue |
| `edexcel-theme-4/4-1-5-trading-blocs-and-the-world-trade-organisation.html` | Edexcel 4.1.5 Trading Blocs and the World Trade Organisati | `tariff.png` | place |
| `edexcel-theme-4/4-1-7-balance-of-payments.html` | Edexcel 4.1.7 Balance of Payments | `j-curve.png` | place |
| `edexcel-theme-4/4-1-9-international-competitiveness.html` | Edexcel 4.1.9 International Competitiveness | none | draw - unit labour costs against competitiveness |
| `edexcel-theme-4/4-2-1-absolute-relative-poverty.html` | Edexcel 4.2.1 Absolute and Relative Poverty | `lorenz-curve.png` | place |
| `edexcel-theme-4/4-3-1-measures-of-development.html` | Edexcel 4.3.1 Measures of Development | `kuznets-curve.png` | place |
| `edexcel-theme-4/4-3-2-factors-influencing-growth-development.html` | Edexcel 4.3.2 Factors Influencing Growth and Development | `ppf-growth-decline.png` | place |
| `edexcel-theme-4/4-4-1-role-of-financial-markets.html` | Edexcel 4.4.1 Role of Financial Markets | none | no diagram needed - the six functions |
| `edexcel-theme-4/4-4-2-market-failure-in-the-financial-sector.html` | Edexcel 4.4.2 Market Failure in the Financial Sector | none | no diagram needed - asymmetric information and moral hazard |
| `edexcel-theme-4/4-4-3-role-of-central-banks.html` | Edexcel 4.4.3 Role of Central Banks | none | draw - the monetary policy transmission mechanism |
| `edexcel-theme-4/4-5-1-public-expenditure.html` | Edexcel 4.5.1 Public Expenditure | `ad-shift-right.png` | place |
| `edexcel-theme-4/4-5-3-public-sector-finances.html` | Edexcel 4.5.3 Public Sector Finances | `laffer-curve.png` | place |
| `edexcel-theme-4/4-5-4-macroeconomic-policies-in-a-global-context.html` | Edexcel 4.5.4 Macroeconomic Policies in a Global Context | none | no diagram needed - policy in an open economy |

## 8. Content depth

**[repo]** Words inside `<main>`, measured on the **baseline** — the chrome
this pass added contributes 30–60 words a page and would flatter every figure
below if the after-state were used.

| | Words |
| --- | --- |
| Minimum | 300 |
| Median | 741 |
| Mean | 859 |
| Maximum | 2,547 |
| Under 500 | **17 pages** |

Reproduces the brief's §3 figures exactly, which is what makes the two
comparable. `notes_baseline.py` uses a tag-strip rather than the HTML parser's
own word counter for this reason; the two disagree by about 5% and the brief
was measured with a tag-strip.

The 17, thinnest first:

| Page | Board | Words |
| --- | --- | --- |
| `aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html` | AQA 1.1.2 | 300 |
| `aqa-a2-micro/1-4-1-production-and-productivity.html` | AQA 1.4.1 | 345 |
| `aqa-a2-micro/1-5-1-market-structures.html` | AQA 1.5.1 | 367 |
| `aqa-a2-micro/1-2-2-imperfect-information.html` | AQA 1.2.2 | 368 |
| `aqa-a2-micro/1-4-8-technological-change.html` | AQA 1.4.8 | 372 |
| `aqa-a2-micro/1-1-4-scarcity-choice-and-the-allocation-of-resources.html` | AQA 1.1.4 | 390 |
| `edexcel-theme-1/1-3-3-public-goods.html` | Edexcel 1.3.3 | 399 |
| `aqa-a2-micro/1-1-3-economic-resources.html` | AQA 1.1.3 | 404 |
| `edexcel-theme-4/4-2-1-absolute-relative-poverty.html` | Edexcel 4.2.1 | 432 |
| `edexcel-theme-1/1-2-1-rational-decision-making.html` | Edexcel 1.2.1 | 442 |
| `edexcel-theme-4/4-4-1-role-of-financial-markets.html` | Edexcel 4.4.1 | 448 |
| `edexcel-theme-1/1-1-2-positive-normative-statements.html` | Edexcel 1.1.2 | 450 |
| `aqa-a2-micro/1-5-8-the-dynamics-of-competition-and-competitive-market-processes.html` | AQA 1.5.8 | 451 |
| `edexcel-theme-4/4-1-3-pattern-of-trade.html` | Edexcel 4.1.3 | 453 |
| `aqa-a2-micro/1-2-4-behavioural-economics-and-economic-policy.html` | AQA 1.2.4 | 465 |
| `aqa-a2-micro/1-6-6-the-national-minimum-wage.html` | AQA 1.6.6 | 477 |
| `edexcel-theme-1/1-1-3-the-economic-problem.html` | Edexcel 1.1.3 | 485 |

**Twelve of the seventeen are AQA micro.** That is worth noticing on its own:
it is a whole sub-section at half the site's median depth, not a scatter.

**[SERP]** Against what ranks for these topics, on the pages measurable
(§9 explains why Save My Exams is not): tutor2u's market-failure page is ~650
words, Study Mind's is ~800, Study Rocket's is 1,200–1,400, Economics Help's
government-failure page is ~1,200, Seneca's aggregate demand page is
1,800–2,000, TutorChase's externalities page is ~3,500. The site's median of
741 sits at the bottom of that range and its thinnest pages sit well below it.

**Report only.** Expanding a page is writing economics, and padding for word
count makes a page worse. This is item 8 of the approval document and task 7 of
the owner list.

## 9. Board twins and near-duplication

**[repo]** Jaccard similarity of the two pages' prose over 5-word shingles —
the measure `docs/audit/DO-NOT-BREAK.md` uses, reproduced here so the two
numbers are comparable. Across all 87 × 79 = 6,873 cross-board pairs:

| Threshold | Pairs, blocks in | Pairs, `spec-alert` and `notes-cta` stripped |
| --- | ---: | ---: |
| ≥ 0.95 | **0** | 2 |
| ≥ 0.80 | **6** | 12 |
| ≥ 0.60 | 24 | — |

The six at or above 0.80, none of which is a self-competition risk worth
acting on:

| Similarity | Edexcel | AQA |
| ---: | --- | --- |
| 0.891 | 2.6.3 Supply-Side Policies | 2.5.2 Supply-Side Policies |
| 0.858 | 3.3.3 Economies and Diseconomies of Scale | 1.4.5 Economies and Diseconomies of Scale |
| 0.838 | 1.4.1 Government Intervention in Markets | 1.8.9 Government Intervention in Markets |
| 0.831 | 4.1.1 Globalisation | 2.6.1 Globalisation |
| 0.822 | 1.2.3 Price, Income and Cross Elasticities of Demand | 1.3.2 Price, Income and Cross Elasticities of Demand |
| 0.816 | 4.1.7 Balance of Payments | 2.6.3 The Balance of Payments |

**Two conclusions.**

First, **`spec-alert` and `notes-cta` are load-bearing and the measurement
proves it again**: stripping them doubles the ≥0.80 count from 6 to 12 and
creates two pairs above 0.95. `DO-NOT-BREAK.md` says so and it is still true.

Second, **this is not a problem to fix.** Six pairs at 0.80–0.89 on a subject
where both boards teach the same economics is what near-duplication looks like
when it is legitimate. **[SERP]** Save My Exams ranks its AQA and Edexcel pages
for the same topic on one page-one SERP, so Google is demonstrably willing to
show both. `DECISIONS.md` D4 already refuses a cross-board canonical and that
stands.

The twin-board links added in this pass make the pairs *more* connected, not
less distinct: each names the other board in its own sentence, so the
relationship is stated rather than left for Google to infer.

## 10. Social and sharing

**[repo]** Confirmed. All 173 generated notes pages declare
`twitter:card = summary_large_image`, which wants roughly 2:1, and point
`og:image` at `/og-image.png?v=1`, which is **1200 × 1200** — square, verified
by reading the PNG header. A shared link renders as a cropped logo.

The declared `og:image:width` and `og:image:height` are 1200 and 1200, so the
markup is honest; the mismatch is between the card type and the aspect ratio.

**Eliot's job**, task 6 of the manual list: a 1200 × 630 image saved as
`og-image-wide.png`. Wiring it in and bumping the cache-busting `?v=` is a
five-minute change here once it exists.

---

## What was applied

Three commits on `seo/notes-onpage-audit`. Nothing pushed.

| | Count |
| --- | ---: |
| Titles rewritten to the §4 formula | 166 topics + 7 hubs |
| Meta descriptions rewritten and front-loaded | 166 topics + 7 hubs |
| `og:`/`twitter:` mirrors brought with them | 173 pages |
| `LearningResource` nodes gaining the §7 fields | 173 |
| `<h2>` elements gaining a stable `id` | 1,159 |
| Pages gaining a table of contents | 166 |
| Pages gaining a board · module · code sub-label | 166 |
| Pages gaining a visible "Updated" date | 166 |
| Pages gaining a related-topics block | 166 |
| Twin-board links added | 109 |
| New internal links, total | 508 |
| New assertions in `seo/tools/verify_seo.py` | 5 (15–19) |
| AQA `<h1>`s losing their spec-code prefix | 79 |
| Published URLs moved, added or removed | **0** |
| Words of economics wording changed | **0** |

The 79 headings are the one exception to that last row and it is not really an
exception: **no word was changed, a spec code was deleted.** Eliot approved it
on 21 August 2026 and the code is still on every page, in the sub-label
directly beneath the heading.

`verify_text_integrity.py` reports **0 removals** across all 166 pages: every
difference is an addition. `verify_markup_integrity.py --strict` reports 0
losses.

**Seven new visible strings**, all chrome, all listed at the top of
`scripts/notes_extras.py`: "Updated", "On this page", "Related topics",
"Studying AQA instead?", "Studying Edexcel instead?", "covers this on AQA.",
"covers this on Edexcel." They are item 3 of the approval document.

**Not applied, by category:** anything that changes a word a student reads.
That is the whole of `seo/18-notes-content-approval-2026-08-21.md`.

**`scripts/intentional-changes.json` was deliberately not extended.**
`compare_trees.py` assertion 5 governs `<head>` field equality and 166 pages ×
six fields is roughly 996 entries with 996 written reasons — for a script
`.github/workflows/verify.yml` states outright is not a step, because it is red
on any commit without a `--family` declaration and "a check that is always red
protects nothing". Its test suite runs instead, and passes: 39 of 39 cases.
Eliot chose the written record over the ritual on 21 August 2026.

---

## Live SERP comparison

Twelve topics, chosen for coverage and not by any Search Console metric.
Searched 21 August 2026; competitor titles read off their own HTML rather than
taken from Google's rewrite, per the brief's §2 method.

**The single most important observation: Economics Academy appears nowhere in
the top results for any of the twelve.** Not on page one, not in the top ten
returned for any query. That is the finding; everything below is about what the
pages that do appear have.

| # | Query | Chosen because | Site's page |
| --- | --- | --- | --- |
| 1 | types of market failure a level economics revision notes | bare topic name | Edexcel 1.3.1 (no diagram) |
| 2 | price elasticity of supply a level economics | bare topic name, both boards | Edexcel 1.2.5 / AQA 1.3.4 |
| 3 | aggregate demand a level economics revision notes | bare topic name | Edexcel 2.2.1 |
| 4 | division of labour a level economics | bare topic name | Edexcel 1.1.5 (no diagram) |
| 5 | inflation and deflation aqa a level economics notes | AQA macro | AQA 2.3.3 |
| 6 | monopoly and monopoly power aqa a level economics notes | AQA micro | AQA 1.5.6 |
| 7 | supply side policies a level economics edexcel revision notes | Edexcel macro | Edexcel 2.6.3 |
| 8 | externalities a level economics notes | Edexcel micro | Edexcel 1.3.2 |
| 9 | nature and purpose of economic activity aqa a level economics | thin page, 300 words | AQA 1.1.2 |
| 10 | public goods a level economics revision notes | thin page, 399 words | Edexcel 1.3.3 |
| 11 | government failure a level economics | no diagram | Edexcel 1.4.2 |
| 12 | globalisation a level economics revision notes edexcel | no diagram | Edexcel 4.1.1 |

### What the ranking pages carry

Verbatim titles and measured attributes. Word counts are the article body.

| Site | Verbatim `<title>` | Words | Diagrams | ToC | Byline | Date | FAQ |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| Save My Exams | `Types of market failure - A Level Economics Revision Notes` | — | — | — | no | no | — |
| Save My Exams | `Monopoly diagram economics - A Level Economics Revision Notes` | — | — | — | no | no | — |
| Save My Exams | `Economic Activity - A Level Economics Revision Notes` | — | — | — | no | no | — |
| Save My Exams | `Globalisation \| Edexcel A Level Economics A Revision Notes 2015` | — | — | — | no | no | — |
| tutor2u | `1.3.1 Types of Market Failure (Edexcel) \| Reference Library \| Economics \| tutor2u` | ~650 | none | yes | no | **"Last updated 19 Sept 2023"** | no |
| Study Mind | `Market Failure - A-Level Economics - Study Mind` | ~800 | 1–2 | partial | no | no | **8 questions** |
| Study Mind | `Public Goods - A-Level Economics - Study Mind` | ~800 | 1 | **yes** | no | no | **10 questions** |
| Seneca | `Aggregate Demand \| Free Notes & Practice – Economics: Edexcel A A Level` | 1,800–2,000 | 6–8 | **yes** | no | no | 5 practice questions |
| Study Rocket | `Types of Market Failure – A Level Economics A Edexcel Revision – Study Rocket` | 1,200–1,400 | 2 | **yes** (sidebar, 82 topics) | no | no | no |
| TutorChase | `1.3.2 Externalities and Welfare Effects \| Edexcel A-Level Economics Notes \| TutorChase` | ~3,500 | 2–3 | **yes** | **"Dave — Cambridge University, BA Hons Economics", 8 years tutoring** | no | **6 questions** |
| Economics Help | `Government Failure - Economics Help` | ~1,200 | 2 | no | **"Tejvan Pettinger", PPE, Oxford** | **published and updated** | no |
| PMT | no HTML topic pages — PDFs only | — | — | — | — | — | — |

**Save My Exams's body could not be measured** and the dashes say so rather
than guessing: their pages render their content in JavaScript, so a fetch
returns navigation and nothing else. Their titles and the absence of a byline
or date are readable and are what is recorded.

### What the winning pages have that Economics Academy did not

In one sentence each, and only where it is true:

1. **The topic name at the front of the title.** Six of the seven, and Save My
   Exams goes further — `Monopoly diagram economics` and `Government failure
   economics` append the bare word "economics" to catch the unqualified query,
   with no board in the title at all. *Fixed in this pass.*
2. **A table of contents.** Seneca, TutorChase, Study Mind and Study Rocket all
   have one; none of the 166 did. *Fixed in this pass.*
3. **A named author with credentials.** TutorChase and Economics Help print
   one; the two of the twelve queries where a single page is hardest to
   dislodge are Economics Help's. *Eliot's, task 4.*
4. **A visible date.** tutor2u and Economics Help print one. *Fixed in this
   pass.*
5. **More words.** The site's median is 741 and its thinnest pages are 300–400;
   the measurable competitors run 650–3,500 with 1,200–2,000 typical.
   *Approval item 8.*
6. **A question-and-answer block.** Study Mind runs 8–10 questions, TutorChase
   6. **Not recommended as an SEO fix**: Google removed FAQ rich results on
   7 May 2026, so the markup earns nothing, and the site already has a
   practice-questions page linked from every topic doing the same job better.

**Nothing was copied.** This is competitive intelligence; the notes and
questions on this site are original and stay original.

**Caveat inherited from the brief:** these SERPs were sampled through a
US-routed search tool. Task 1 of the manual list is to re-check six of them
from a UK IP before the formula is treated as settled.

---

## Core Web Vitals

Six pages, both boards, the thinnest and the heaviest of each. Lighthouse
12.8.2, three runs per configuration, medians, simulated throttling.

**The measurement is a LOCAL before/after A/B, and that is a departure from
`seo/tools/run_lighthouse.py`, which runs against the live site.** It has to
be: nothing is pushed, so the live site does not carry these changes, and a
live run would measure the old pages. Two `git worktree` copies were served on
localhost — `f58c4c9` (metadata only, no layout change) against `HEAD`.

| Page | Metric | Before | After | Change |
| --- | --- | ---: | ---: | ---: |
| Edexcel 1.2.2 Demand | Performance | 89 | 92 | **+3** |
| Edexcel 1.2.2 Demand | LCP | 2,177 ms | 2,252 ms | **+75 ms** |
| Edexcel 1.2.2 Demand | TBT | 347 ms | 254 ms | −93 ms |
| Edexcel 1.2.2 Demand | CLS | 0.003 | 0.003 | −0.000 |
| Edexcel 1.3.3 (399 words) | LCP | 3,658 ms | 4,862 ms | +1,204 ms |
| Edexcel 3.4.5 Monopoly | LCP | 2,778 ms | 4,509 ms | +1,732 ms |
| AQA 1.1.2 (300 words) | LCP | 2,513 ms | 3,711 ms | +1,198 ms |
| AQA 1.5.3 Perfect Competition | LCP | 2,980 ms | 4,272 ms | +1,293 ms |
| AQA 2.5.1 (2,547 words) | LCP | 3,940 ms | 3,937 ms | −3 ms |
| CLS, all six pages | | 0.002–0.021 | 0.002–0.021 | **≤ ±0.001** |

### Read those LCP numbers with care — five of the six are noise

Three things say so, and they all point the same way.

**The LCP element is identical before and after on every page**, and it is
`div.spec-alert` — which sits **above** everything this pass inserted. The
table of contents goes below it and the related block goes near the foot of
the page. There is no mechanism by which the new markup delays an element that
paints before it.

**The within-configuration spread is larger than the between-configuration
difference.** Edexcel 1.3.3's three "before" runs were 4,176 / 2,523 / 3,658
ms and its three "after" runs 2,104 / 4,862 / 4,896 — the ranges overlap.
Edexcel 3.4.5's "after" runs were 7,426 / 4,509 / 4,030. Three runs did not
suppress it.

**The one page measured back to back, before the machine was also running
other work, is rock steady**: Edexcel 1.2.2's before runs were 2,178 / 2,177 /
2,177 and its after runs 2,252 / 2,253 / 2,252. **That +75 ms, on essentially
zero variance, is the only LCP figure here worth believing** — and 75 ms on a
2.2 s LCP is a change nobody can see.

`seo/09-web-vitals-baseline.md` hit exactly the same wall and says so in its
own words: it recorded a `notes-topic` seven-run spread of 7.3, 8.0, 1.7, 7.1,
1.8, 3.0, 3.0 seconds and concluded "the absolute timings below are not
trustworthy". This audit is not the first to find that a local run on a working
machine is too noisy for LCP.

### What IS trustworthy here

**CLS did not move.** 0.002 to 0.021 before, the same after, every delta at or
below 0.001. That is the metric this pass could most plausibly have damaged —
a block inserted above the fold is the textbook cause of layout shift — and it
is also far less sensitive to server latency than LCP, so the measurement
holds. The contents block sits between two elements that both have their own
reserved height, and the sub-label is a fixed-height line inside a header that
already existed.

For context, `seo/09-web-vitals-baseline.md` recorded a `notes-topic` CLS of
0.102–0.110 with "no identified cause" in some conditions. Nothing measured
here comes near that.

**Total blocking time did not move either**, other than on the page whose
measurement is trustworthy, where it fell 93 ms. This pass adds no JavaScript.

### No regression is fixed here, because none is identified

The mission's rule is to fix only what is clearly mine. Nothing in this data is
clearly mine. The one attributable change is +75 ms of LCP with a −93 ms TBT
and a +3 performance score alongside it.

**What would settle it**, and it is cheap: after the push,
`python3 seo/tools/run_lighthouse.py --out seo/lh-live-notes-seo` against the
live site, compared to `seo/lh-live-after/`. Same URLs, same run count, same
flags, same Lighthouse major version — which is the whole reason that script
exists rather than a hand-run CLI. That is now task 13 of the manual list.

---

## What could not be determined

**Whether the pages look right in a browser.** Every automated check is green
and the markup was read line by line, but this session has no way to open a
page in Live Server and look at it. The CSS is scoped, uses only existing
`:root` tokens, adds no inline styles and passes `verify_inline_styles.py` and
`verify_css_load_order.py`, and Prettier disagrees with the stylesheet only at
three pre-existing places, none of them in the new block. **That is not the
same as having looked.** Task 14 of the manual list.

**Save My Exams's page bodies.** Their content is rendered in JavaScript and a
fetch returns the navigation. Word counts, diagram counts and table-of-contents
presence for the site that ranks first on most of these queries are unknown,
and the competitor table says "—" rather than guessing.

**Whether the twin map is right on all 109 rows.** It is my economics
judgement, seeded by a measured similarity and read row by row, and eight rows
are hand corrections that the file names individually. A wrong row sends a
student to a page that is related but not the counterpart. The full map prints
with `python3 scripts/notes_twins.py` and is worth twenty minutes of Eliot's
eyes; the four rows I am least sure of are item 9 of the approval document.

**Whether any of this moves a ranking.** No forecast appears in this report.
The data available is one contaminated, out-of-season Search Console window and
a set of SERPs sampled from the wrong country. Task 2 of the manual list — a
term-time re-export — is what turns the next audit's answer from directional
into measurable.

**Whether 2026-08-13 is the right `dateModified` for 163 of the 166 pages.**
It is the truth about the repository: it is when the source slice was last
edited. Whether the economics on those pages was reviewed that day is a
different question and git cannot answer it.
