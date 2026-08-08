# Phase 7 — Internal link architecture

About **crawl priority distribution**, not link hygiene. Hygiene is already
asserted green by `seo/tools/verify_seo.py` and nothing here re-solves it.

```
python3 seo/tools/link_graph.py            # the analysis
python3 seo/tools/link_graph.py --write    # + seo/07a-topic-map.csv
```

461 page nodes. The 283 PDFs are excluded as nodes and reported separately.

---

## Read this first: there are two graphs, and they disagree

The header and footer are **not in any page's HTML**. `inject-templates.js`
fetches them at runtime and injects them into placeholder divs. So:

- **static** — only links written in the page. What a non-rendering crawler sees.
- **rendered** — static, plus the **30** header/footer links from every page.
  What Googlebot sees after rendering.

Quoting one number would be misleading whichever was picked, so both are given
throughout.

| | static | rendered |
| --- | ---: | ---: |
| max click depth from `/` | **4** | **3** |
| pages at depth ≥ 4 | **253** | **0** |
| unreachable from `/` | 0 | 0 |
| pages with < 3 inbound links | 94 | 89 |
| pages with 0 inbound links | **0** | 0 |

Depth histograms:

```
static    0:1   1:4    2:19   3:184  4:253
rendered  0:1   1:29   2:350  3:81
```

**The brief's target — every page within 3 clicks — is already met in the
rendered graph.** In the static graph 253 pages sit at depth 4: 172
practice-questions and 81 past-paper-questions topic pages, all reached via
hub → board index → topic.

There are **no orphans**. Nothing is reachable only from the sitemap.

---

## ⚠️ A correction to an earlier claim

I previously reported that *"21 past-paper-questions topic pages receive zero
direct inbound links"* and are *"reachable only from the sitemap"*. **The second
half of that was wrong**, and the first half needs a qualifier.

What is actually true:

- **15 ppq topic pages** have no direct link **from their own notes page** —
  the notes page links to `/past-paper-questions/?board=…&topic=…` instead,
  which strips to the hub. They still carry **5–17 inbound links each** from
  inside the ppq section.
- **6 of the 21** were not topic pages at all but ppq **section hubs**
  (`edexcel/theme-1…4`, `aqa/micro`, `aqa/macro`), with 12–20 inbound each.
  They are not supposed to have notes links.

So this is a *"the notes page points at the hub instead of the topic page"*
defect, worth fixing because the notes page is the topically ideal referrer and
a query-string link passes its signal to the hub rather than the topic. It is
**not** an orphan-page emergency, and I should not have called it one.

---

## Cross-section coverage, by board

"any" counts any link into the section, hub included. "topic" counts links to a
specific topic page. The gap between them is the whole finding.

| From → To | Board | any | topic |
| --- | --- | ---: | ---: |
| revision-notes → practice-questions | edexcel | 87/87 100% | **87/87 100%** |
| revision-notes → practice-questions | aqa | 79/79 100% | **79/79 100%** |
| revision-notes → past-paper-questions | edexcel | 66/87 75.9% | **32/87 36.8%** |
| revision-notes → past-paper-questions | aqa | 73/79 92.4% | **34/79 43.0%** |
| practice-questions → revision-notes | edexcel | 87/87 100% | **87/87 100%** |
| practice-questions → revision-notes | aqa | 79/79 100% | **79/79 100%** |
| **practice-questions → past-paper-questions** | edexcel | **0/87** | **0/87** |
| **practice-questions → past-paper-questions** | aqa | **0/79** | **0/79** |

Notes ↔ practice is complete in both directions. The two real gaps are the
notes → ppq topic rate (36.8% / 43.0%, the query-string defect) and
practice → ppq, which is **zero**.

---

## Reciprocity: practice-questions is pure hub-and-spoke

Pages linking to **any sibling topic page in the same section and same board**:

| Section | Pages with ≥1 sibling link | Sibling edges | Mean per page |
| --- | ---: | ---: | ---: |
| revision-notes | 90/168 **53.6%** | 293 | 1.7 |
| **practice-questions** | **0/166 — 0.0%** | **0** | **0.0** |
| past-paper-questions | 87/87 **100.0%** | 801 | 9.2 |

> **Corrected.** An earlier version of this table reported past-paper-questions
> at **0/87**. That was an artefact: the check excluded every `index.html`, and
> a ppq topic page *is* `…/<slug>/index.html`, so every sibling was filtered
> out. The section in fact links laterally on **every** page, averaging 9.2
> sibling links — it already carries a full topic list in the page. The metric
> in `link_graph.py` now uses the same `is_topic_page` rule as the coverage
> table, so the two cannot disagree again.

So the gap is **practice-questions alone**. A crawler arriving at a
practice-question page has exactly one way onward that is not the hub. All 166
topic pages sit at the same depth with the same 2 inbound links, and nothing in
the structure says any one of them matters more than another.

That is 166 of the never-crawled pages, not 263. past-paper-questions needs
nothing here and should not be touched.

---

## Link-starved pages that already earn impressions

Cross-referenced against `seo/performance-pages.csv`. Per the brief these rank
above everything else — they have demonstrated demand and no internal support.

| Page | Inbound | Impressions | Clicks |
| --- | ---: | ---: | ---: |
| `/past-papers/edexcel-b/` | **1** | **7,214** | 78 |
| `/past-papers/ocr/` | **1** | **4,757** | 65 |
| `/revision-notes/macroeconomics-diagrams.html` | **1** | **2,620** | 37 |
| `/revision-notes/microeconomics-diagrams.html` | **1** | **1,463** | 14 |
| `/revision-notes/edexcel-theme-1/1-3-1-types-of-market-failure.html` | 5 | 2,077 | 2 |
| `/faq.html` | 2 | 22 | 1 |

The top four are **not** in the sections this pass was aimed at. Between them
they earn **16,054 impressions** on a single inbound link each — and that one
link is the runtime-injected header, so a non-rendering crawler sees none.

The two diagram galleries are the clearest case: 4,083 impressions, real
original content, and no notes page links to either.

---

## Link equity concentration (static inbound)

| Page | Inbound |
| --- | ---: |
| `tutoring.html` | 449 |
| `index.html` | 441 |
| `marking.html` | 275 |
| `revision-notes/index.html` | 271 |
| `past-papers/edexcel/index.html` | 184 |
| `practice-questions/index.html` | 174 |
| `past-paper-questions/index.html` | 164 |
| `past-papers/aqa/index.html` | 164 |
| `revision-notes/aqa-a2-micro/index.html` | 58 |
| `practice-questions/aqa-a2-micro/index.html` | 56 |

Sensible for a commercial site — `tutoring.html` leading is by design. The
distribution is hub-heavy, consistent with the reciprocity finding: everything
below the board indexes drops off a cliff to 2–5 inbound links.

---

## Anchor text

- Targets receiving a **generic** anchor ("click here", "read more"): **1**.
  Effectively a non-issue; anchor text on this site is descriptive.
- Targets whose inbound anchors are >90% one identical string: **100**.

The large repeat counts are sitewide CTAs and are correct as they are:

| Count | Anchor | Target |
| ---: | --- | --- |
| 445 | "Book a Free Intro Call" | `tutoring.html` |
| 441 | "Home" | `index.html` |
| 183 | "Edexcel Past Papers" | `past-papers/edexcel/` |
| 173 | "Practice Questions" | `practice-questions/` |

The ones worth noting are the ppq topic pages — e.g. 68 links to
`/past-paper-questions/edexcel/2-6-2-demand-side-policies/` all reading exactly
`2.6.2 Demand-side Policies`. Those come from the topic chip lists on the ppq
index pages. **Any link added in A2 must not repeat that string**, or it deepens
an existing monoculture.

---

## PDFs

283 published PDFs, linked from **93 pages**. Excluded as graph nodes
deliberately: they are exam-board documents that exist identically on other
sites, and Google is correctly treating them as duplicates. Nothing in this pass
should push more signal at them.

---

## Topic map

`seo/07a-topic-map.csv` — **166 rows, all `high` confidence, 0 cross-board rows.**

| | |
| --- | --- |
| rows | 166 (edexcel 87, aqa 79) |
| with `practice_url` | 166 |
| with `pastpaper_url` | 81 |
| with `flashcard_url` | 166, across the 6 real decks |

### How "high" was earned, and why bare topic codes were never used

**37 bare topic codes exist on both boards and mean different topics** — `1.1.1`
is *Economics as a Social Science* on Edexcel and *Economic Methodology* on AQA.
Matching on a code alone would mis-link 37 topics, resolve to live pages, 404
nothing, and pass every existing assertion.

So each row required a **declared, board-naming source inside the page** to
agree with the directory structure. Titles were rejected as evidence: they
legitimately differ (notes *"2.1.1 The Objectives of Government Economic
Policy"* vs practice *"2.1.1 Objectives of Government Policy"*), and Edexcel
notes h1s carry no code at all. Three sources qualified, each on 100% of pages:

| Section | Declared evidence |
| --- | --- |
| revision-notes | `spec-alert`: `Specification Coverage: {Board} unit X.Y.Z` |
| practice-questions | `data-board` and `data-spec` on every question `<li>` |
| past-paper-questions | `taxonomy.json` `board` **and** its `notesDir` |

A row is `high` only where the in-page declaration, the taxonomy record and the
board directory all name the same board and the same code. All 166 do.

Notes ↔ practice additionally share **byte-identical filenames**, 166/166.

`seo/07b-link-decisions.md` holds what needs your decision. Nothing landed below
high confidence, so that file is about **what to link**, not about resolving
ambiguity.
