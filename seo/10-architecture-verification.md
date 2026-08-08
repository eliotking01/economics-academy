# Phase 10 — Architecture pass verification

Branch `seo/architecture-pass`, 10 commits, **not yet deployed**. Everything
below is measured, and where a number turned out to be wrong it is corrected
rather than quietly restated.

```
python3 seo/tools/verify_seo.py          # 14 assertions, was 10
python3 seo/tools/link_graph.py          # the graph and the topic map
python3 scripts/verify_html.py
python3 scripts/verify_text_integrity.py 0875e28
python3 scripts/verify_markup_integrity.py 0875e28 --strict
```

---

## 1. Assertions — 14/14 pass

Four are new and permanent.

```
[PASS]  1  no internal link points at a non-canonical URL        21,282 internal references
[PASS]  2  no internal link is case-mismatched or dead
[PASS]  3  every page has a self-referencing canonical           461 pages
[PASS]  4  og:url matches canonical; social titles match <title>
[PASS]  5  exactly one <h1>, a title and a description
[PASS]  6  titles and meta descriptions are unique               461 / 461
[PASS]  7  no unintended noindex
[PASS]  8  every JSON-LD block parses and every page has one     921 blocks (was 904)
[PASS]  9  sitemap valid, complete, canonical-only               744 URLs across 7 sitemaps
[PASS] 10  robots.txt blocks nothing and names the sitemap
[PASS] 11  every page within 3 clicks of the homepage (rendered) max depth 3     ← new
[PASS] 12  every page has 3+ inbound internal links (rendered)   3 exceptions    ← new
[PASS] 13  no link crosses an exam board                         2 allowed       ← new
[PASS] 14  every indexable page below the homepage has a crumb   460 pages       ← new
```

Assertions 11–13 import `seo/tools/link_graph.py` rather than restating what an
edge, a board or a topic page is, so the checker and the analysis cannot drift.

**Assertion 15 — "every `<img>` has width and height" — was NOT shipped.** See
§6; it is blocked on a CSS question I will not answer blind.

### The two documented exception sets

Both are named in the code with the reason, not silently tolerated:

- **Assertion 12**, 3 pages below 3 inbound links.
  `practice-questions/edexcel-theme-3/3-2-1-business-objectives.html` is the only
  topic alone in its unit, so it has no siblings to link it. The two glossary
  board pages are reached from the glossary hub and from each other, which is
  their whole intended entry path.
- **Assertion 13**, 2 links. The glossary's own board selector
  (`Switch to the Edexcel A glossary` and its mirror) — the one place on the site
  where crossing boards is the point. **Verified present at `0875e28`**, before
  this pass.

---

## 2. Cross-board links — the headline safety number

> **This pass introduced ZERO cross-board links.**
>
> Total sitewide: **2**. Both are the glossary board selector and both predate
> the pass. Asserted permanently by check 13.

This was the highest-risk failure mode in the work, because 37 bare topic codes
exist on both boards and mean different topics — `1.1.1` is *Economics as a
Social Science* on Edexcel and *Economic Methodology* on AQA. A wrong link would
resolve to a real page, 404 nothing, and pass every other assertion here.

**No topic code was ever matched.** Every join used something that names the
board:

| Join | Key |
| --- | --- |
| practice → past-paper-questions | `questionsUrl`, a full site path |
| practice → sibling topics | `(boardDir, unit)` — the directory carries the board |
| notes → past-paper-questions | slug looked up in `questions.json`; query board, record board and destination path must all agree or the run aborts |
| notes → diagram galleries | only pages the Edexcel-scoped galleries already link to |

A late check caught the one place this could have gone wrong: **both diagram
galleries are explicitly Edexcel-only** — *"a complete collection of
Microeconomics diagrams from Edexcel Theme 1 and Theme 3 revision notes"* — so
linking AQA notes pages to them would have been exactly the silent cross-board
error. Verified after the change: **0 AQA pages link to either gallery.**

---

## 3. Link architecture — before and after

| Measure | Before | After |
| --- | ---: | ---: |
| max click depth, rendered | 3 | 3 |
| max click depth, static | 4 | 4 |
| pages at depth ≥4, rendered | 0 | 0 |
| orphans | 0 | 0 |
| **pages with <3 inbound, static** | **94** | **8** |
| **pages with <3 inbound, rendered** | **89** | **3** |
| **practice → past-paper-questions** | **0/166** | **151/166** |
| practice → past-paper-questions (topic page) | 0/166 | 81/166 |
| **practice-questions lateral sibling links** | **0/166** | **165/166** (mean 3.3) |
| notes → ppq topic pages, Edexcel | 32/87 (36.8%) | 45/87 (51.7%) |
| ppq topic pages with a direct notes link | 66/87 | 79/87 |
| `microeconomics-diagrams.html` inbound | 1 | 27 |
| `macroeconomics-diagrams.html` inbound | 1 | 22 |
| internal references | 20,501 | 21,282 |

Depth is unchanged **by design** — it was already at the target. The work went
into inbound distribution and lateral connectivity, which is what tells a
crawler that 263 never-crawled pages are not an undifferentiated block.

### Two corrections made during the work

1. **past-paper-questions was never at 0/87 lateral links.** It is at **100%,
   averaging 9.2 sibling links per page**. My check excluded every `index.html`
   and a ppq topic page *is* `…/<slug>/index.html`. Item 3 therefore applied to
   166 pages, not 253, and that section was correctly left untouched.
2. **The 21 ppq pages I called "reachable only from the sitemap" were not
   orphans.** Six were section hubs; the other 15 each had 5–17 inbound links
   from inside their own section. The real defect was narrower — their notes
   page linked to the hub with a query string instead of to the topic page.

---

## 4. Structured data

| Measure | Before | After |
| --- | ---: | ---: |
| JSON-LD blocks | 904 | 921 |
| parse failures | 0 | 0 |
| **`Review` / `AggregateRating`** | **5 objects on index.html** | **0** |
| `EducationalOrganization` with `@id` | 0/354 | **354/354** |
| Eliot King `Person` with `@id` | 0/7 | **7/7** |
| indexable non-homepage pages without a breadcrumb | 17 | **0** |
| `Organization.logo` | absent | present, 512×512, verified live |

The removal was the important one: an organisation reviewing itself, with a
claimed `reviewCount` of 20, **none of which appeared in the page's 1,011
characters of visible text**. Two guidelines violations at once, producing no
rich result.

### Three eligibility premises that had moved

Checked against current documentation in August 2026 rather than assumed:

- **Practice problems is not subject-restricted — it is deprecated outright**
  (announced Nov 2025, docs removed Jan 2026). The `Quiz` markup on 166 pages
  is accurate and matches the page, and Google says deprecated markup carries no
  penalty, so it stays. **Expect no rich result from it.**
- **FAQ rich results were removed entirely on 7 May 2026**, not merely narrowed
  to government and health sites in 2023. `faq.html` will produce nothing.
- **Education Q&A (flashcards) is still live, but this site is ineligible** —
  only 3 of 95 cards are in the HTML, the rest fetched from a data file, and the
  feature requires the questions to be visible. Adding it would have repeated
  the violation just removed from the homepage.

---

## 5. Core Web Vitals — and a correction to the baseline

### The baseline numbers in `seo/09` were reading noise

Re-running the identical method at 7 runs against **the same unchanged deployed
code** produced materially different medians:

| Page | 3-run LCP | 7-run LCP | 3-run perf | 7-run perf |
| --- | ---: | ---: | ---: | ---: |
| homepage | 4.73 s | 3.04 s | 72 | 88 |
| notes-topic | 6.84 s | 3.04 s | 61 | 85 |
| practice-questions | 5.08 s | 1.79 s | 69 | 99 |

The runs are **bimodal, not noisy**. `notes-topic` across 7 runs: 7.3, 8.0,
**1.7**, 7.1, **1.8**, 3.0, 3.0. Each page clusters around ~1.6 s and ~5–8 s, so
the median reports which mode won.

**So my baseline verdict — "LCP 4.7–6.8 s, performance 61–72, poor" — was
wrong.** Lab medians over the CDN are not a usable instrument for this site, and
no before/after taken that way would have meant anything.

### The measurement that does work: a local A/B

Both commits served from `python3 -m http.server`, identical method, 5 runs.
This removes the CDN — **run-to-run spread fell to 0.00–0.16 s** — while the
Google Fonts request still resolves to the real third-party origin, which is
exactly what the change affected.

| Page | LCP before | LCP after | Δ | Render-blocking Δ | Critical chain |
| --- | ---: | ---: | ---: | ---: | --- |
| homepage | 3.61 s | 3.45 s | **−0.16 s** | −147 ms | 4 → **3** |
| section-hub | 3.15 s | 2.85 s | **−0.30 s** | −300 ms | 4 → **3** |
| notes-topic | 3.61 s | 3.31 s | **−0.30 s** | −302 ms | 2 → 2 |
| practice-questions | 3.60 s | 3.45 s | **−0.15 s** | −457 ms | 4 → **3** |
| past-paper-questions | 3.61 s | 3.30 s | **−0.31 s** | −151 ms | 4 → **3** |
| flashcards | 3.75 s | 3.61 s | **−0.15 s** | −301 ms | 4 → **3** |

**Total render-blocking across the six pages: 15,864 ms → 14,206 ms (−10.5%).**
**Critical chain depth 4 → 3 on five of six pages** — the structural goal.

Improvement on **all six pages in both metrics**, and the deltas (0.15–0.31 s)
are larger than the 0.00–0.16 s spread, so they are attributable rather than
noise. **No regression on any page.**

This is much smaller than Lighthouse's own "eliminate render-blocking" estimate
of 774–2788 ms, exactly as `seo/09` predicted it would be: hoisting the
`@import` removes a round trip of *discovery latency*, not the font transfer.

**Honest summary: a real, consistent, modest win.** Not the multi-second gain
the opportunity estimate implied.

---

## 5a. Post-deploy re-measurement — done

Merged as PR #15 and deployed. The live re-run in §7 step 1 has been executed:
`seo/lh-live-after-7run.json`, 7 runs, identical method.

**The structural change is confirmed live:**

| Page | Critical chain before | after |
| --- | ---: | ---: |
| homepage | 4 | **3** |
| section-hub | 4 | **3** |
| notes-topic | 2 | 2 |
| practice-questions | 4 | **3** |
| past-paper-questions | 4 | **3** |
| flashcards | 4 | **3** |

**4 → 3 on five of six pages**, reproducing the local A/B exactly. This is read
from the request trace rather than a timing median, so it is the reliable
result — the `@import` hoist did on the real CDN what it did on localhost.

### ⚠️ The live LCP numbers still cannot be used, and they look better than they are

| Page | LCP before | LCP after |
| --- | ---: | ---: |
| homepage | 3.04 s | 1.79 s |
| section-hub | 4.25 s | 1.84 s |
| notes-topic | 3.04 s | 1.83 s |
| flashcards | 5.23 s | 1.82 s |

**Do not read this as a 1–3 second win.** The bimodality documented in §5 is
unchanged. Post-deploy `notes-topic` across its 7 runs:

```
6.91, 1.87, 1.77, 1.93, 1.79, 1.83, 1.81      spread 5.14 s
```

Spreads are 3.15–5.14 s, the same two clusters at ~1.8 s and ~5 s. The
post-deploy runs simply landed in the fast cluster more often. Render-blocking
moved the *other* way on five of six pages (+5 to +203 ms, −708 ms on
flashcards, −5.1% net), which is the same noise pointing the opposite direction.

**Nothing about live LCP is attributable.** The local A/B in §5 — spread
0.00–0.16 s, −0.15 to −0.31 s LCP, −10.5% render-blocking, consistent on all six
pages — remains the only measurement of what the change was worth.

### Raw reports are not committed

A 6-page 7-run pass writes 42 JSON files and 23 MB. Only the medians are kept
(`seo/lh-live-after-7run.json`, 5.9 KB), matching how the pre-deploy runs were
handled. `.gitignore` carries `seo/lh-*/` so future runs are not staged by
accident; the trailing slash matches the output directories only, never the
`seo/lh-*.json` medians beside them. The per-run reports are regenerable.

---

## 6. What was deliberately NOT done

- **Assertion 15, `<img>` width and height.** Blocked, not forgotten. The three
  images (`about.html` ×2, `tutoring.html` ×1) have known intrinsic sizes, but
  `main.css` sets `.image img { width: 100% }` **without `height: auto`**, so
  adding a `height` attribute could distort the aspect ratio on narrow screens.
  The safe change is 3 HTML attributes **plus** `height: auto` on two or three
  CSS rules, and it needs a visual check in Live Server on two commercial pages.
  **Measured CLS is 0.000 everywhere sampled, so there is no urgency.**
- **The 2 notes pages with no past-papers block** —
  `1-1-6-types-of-economies.html` and `2-2-5-net-trade.html`.
  `append_past_papers_link.py` anchors on `<div class="notes-questions-link">`
  and every notes page now carries two of those, since the flashcards block
  reuses the class. Its ambiguity guard therefore fires on any page that does
  not already have the block. Fixing it means changing that script's anchor
  logic, which would rewrite 24 pages — out of scope, and yours to approve.
- **WebP conversion of 112 diagram PNGs** — dropped once measurement showed the
  LCP element is text on all six sampled pages.
- **Swapping MathJax for KaTeX** — CLS is 0.000 and MathJax loads `async`.
  Never justified.
- **`/past-papers/edexcel-b/` and `/ocr/` inbound links** — no notes exist for
  those boards, so there is no topically honest anchor. Declined rather than
  manufactured. They still earn 11,971 impressions on one header link each.
- **`seo/05-verification.md` Liquid warning** — predates this pass, and `seo/`
  is excluded in `_config.yml`, confirmed live (that path 404s). Cannot affect
  the deploy.

---

## 7. What you must do — manually

### Before deploying

Nothing. `main` auto-publishes, so the merge **is** the deploy. Confirm first.

### Immediately after deploying

1. ~~**Re-run the live Lighthouse baseline**~~ — **done, see §5a.** The chain
   depth confirmed 4 → 3 on five of six pages; the bimodality persisted exactly
   as predicted, so the LCP medians were not usable.
   ```
   python3 seo/tools/run_lighthouse.py --out seo/lh-live-after --runs 7
   ```

2. **Spot-check in the Rich Results Test** — these five, in this order:
   ```
   https://economicsacademy.co.uk/                   Organization + WebSite + logo
   https://economicsacademy.co.uk/about.html         Person + BreadcrumbList
   https://economicsacademy.co.uk/tutoring.html      Service + BreadcrumbList
   https://economicsacademy.co.uk/revision-notes/edexcel-theme-1/   BreadcrumbList
   https://economicsacademy.co.uk/past-papers/ocr/   BreadcrumbList
   ```
   The homepage is the one that matters: confirm **no review/rating warning**
   now appears, and that the logo is picked up.

3. **Visually check two pages in a browser** — the font change touched all 463.
   A notes page and the homepage are enough. The cascade order was preserved
   exactly (fontawesome, then Google Fonts, then `main.css`), but this is the
   one change in the pass that could look wrong rather than measure wrong.

### In Search Console, and when

| When | Where | What you are looking for |
| --- | --- | --- |
| 2–3 days | Indexing → Pages | `/practice-questions/` and `/past-paper-questions/` starting to leave "Discovered – currently not indexed" |
| 1 week | Indexing → Sitemaps | the per-section child sitemaps showing rising "indexed" counts |
| 2 weeks | Enhancements → Breadcrumbs | 460 valid items, 0 errors. This is the clearest signal the pass worked |
| 2 weeks | Manual actions | should stay empty — the review markup that could have triggered one is gone |
| 4–6 weeks | Performance → Pages | first impressions on `/practice-questions/` URLs |
| Any time | Experience → Core Web Vitals | **still expected to say "no data"**; the site is below the CrUX threshold |

**The one thing worth watching hardest:** whether the two never-crawled sections
begin to index. That is what this pass was for, and breadcrumbs plus lateral
linking plus 151 new cross-section links are the levers pulled. Page experience
is a weak signal and was never going to be the thing that moved them.
