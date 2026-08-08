# Phase 7b — Link decisions for Eliot

No row in `seo/07a-topic-map.csv` landed below **high** confidence, so this file
is not the ambiguity list the brief anticipated. It is the list of **what to
link, and what I recommend declining**.

Numbers come from `seo/07-link-graph.md`. Nothing below has been applied.

---

## 1. Practice-questions → past-paper-questions · 0 of 166 · **recommend doing**

The only completely absent cross-section edge on the site. A student who has
just answered six multiple-choice questions on a topic has an obvious next step
— the real exam questions on the same topic — and there is currently no link.

- **Where**: in `scripts/build_questions.py`, beside the existing
  `quiz-notes-link` block. Generated, so it is one template change and a rebuild,
  not 166 edits.
- **Target**: `pastpaper_url` from the topic map where it exists (**81 of 166**);
  where it does not, the board-filtered hub, matching what the notes already do.
- **Board safety**: taken from the topic map row, which is keyed on the page's
  own `data-board`. No code matching.
- **Cost**: 1 link per page. Within the 8-link cap with room to spare.

## 2. The 15 stale query-string notes → ppq links · **recommend doing**

`append_past_papers_link.py` writes a direct link where the topic has its own
page and a query-string hub link where it does not. It is idempotent, so topics
that later earned a page never had their link upgraded.

**Correction to what I told you earlier:** these pages are *not* orphans. Each
has 5–17 inbound links from inside the ppq section. The defect is that the
notes page — the ideal topical referrer — points at the hub instead of the
topic page, so its signal lands on the hub. Worth fixing, but not urgent in the
way I first described.

Affected, all Edexcel:

```
1-1-3-the-economic-problem            2-1-1-economic-growth
1-1-6-types-of-economies              2-1-3-employment-unemployment
1-2-1-rational-decision-making        2-2-1-aggregate-demand
1-2-10-alternative-views…             2-2-2-consumption
1-2-2-demand                          2-2-3-investment
1-2-5-price-elasticity-of-supply      2-2-5-net-trade
1-3-1-types-of-market-failure         2-6-4-conflicts-between-objectives…
1-3-4-information-gaps
```

- **Where**: a new idempotent `seo/tools/upgrade_pastpaper_links.py`, modelled
  on `append_past_papers_link.py` — one anchored substitution of the `href`
  only. No prose touched, no block added or removed.
- **Cost**: 0 new links. It re-points 15 existing ones.

## 3. Lateral sibling links · **practice-questions only** · approved

> **Scope corrected before applying.** I first reported this as affecting both
> question sections, 0/166 and 0/87. The past-paper-questions figure was a
> measurement bug — a ppq topic page is `…/<slug>/index.html` and my sibling
> check excluded every `index.html`. That section already links laterally on
> **100% of pages, averaging 9.2 sibling links each**, because it carries a
> topic list in the page.
>
> **past-paper-questions therefore gets nothing.** Adding to it would duplicate
> what is there and push well past a sensible link count. The change is 166
> pages, not 253.

practice-questions is genuinely **0/166**. A "related topics" block of 3–4 links
to sibling topics in the same unit, same board, gives each page a lateral path
and lets the unit structure express itself. `revision-notes` does this at 53.6%
and `past-paper-questions` at 100%; practice-questions is the outlier.

Siblings come from the same `unit` in the topic map — **never by code
proximity**, since `1.2.1` and `1.2.2` are the same unit on *both* boards and
that is exactly how a cross-board link would slip in.

## 4. The four link-starved pages that already earn impressions · **recommend doing**

The highest-value items in the whole analysis, and they are outside the sections
this pass was aimed at:

| Page | Inbound | Impressions |
| --- | ---: | ---: |
| `/past-papers/edexcel-b/` | 1 | 7,214 |
| `/past-papers/ocr/` | 1 | 4,757 |
| `/revision-notes/macroeconomics-diagrams.html` | 1 | 2,620 |
| `/revision-notes/microeconomics-diagrams.html` | 1 | 1,463 |

16,054 impressions between them, on one inbound link each — and that link is the
**runtime-injected header**, so a non-rendering crawler sees none at all.

The diagram galleries are the clean case: real original content, high demand, and
**no notes page links to either**. A macro notes page linking to the macro
diagram gallery is genuinely useful to a student and is board-agnostic, since the
galleries cover both boards.

`/past-papers/edexcel-b/` and `/past-papers/ocr/` are harder: **no notes exist
for those boards**, so there is no topically honest in-content link to make. I
would **not** manufacture one. The honest fix is on the `/past-papers/` index,
which already links them, and possibly a line on the other board hubs — but that
edges toward a link dump, so I have not proposed it.

## 5. Things I recommend **against**

- **Adding links to the 283 PDFs.** They are exam-board documents that exist
  identically elsewhere and Google is right to treat them as duplicates.
- **More links to `tutoring.html` (449) or `marking.html` (275).** Already the
  most-linked pages on the site.
- **Anything reusing the ppq topic-chip anchor string.** 68 links already read
  exactly `2.6.2 Demand-side Policies`; adding more deepens a monoculture.
- **Raising notes → ppq "any" coverage above its current 76%/92%.** The
  remaining pages genuinely have no past-paper questions on that topic. A link
  to an empty filtered hub would be a worse student experience, not a better one.

---

## What I need from you

| # | Item | My recommendation |
| --- | --- | --- |
| 1 | practice → past-paper-questions, 166 pages, 1 link each | **do it** |
| 2 | Re-point the 15 stale query-string links | **do it** |
| 3 | Lateral sibling links, 253 pages, 3–4 links each | **your call** — biggest change here |
| 4a | Notes → the two diagram galleries | **do it** |
| 4b | Manufacture links to `/past-papers/edexcel-b/` and `/ocr/` | **decline** — no honest anchor exists |

Items 1, 2 and 4a together add **one** link per page to generated sections and
re-point 15 existing links. That is a small, safe change with a clear rationale
for every link. Item 3 is the one worth thinking about.
