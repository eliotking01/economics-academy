# Phase 3 findings — internal linking & crawl depth

Branch `audit/organisation-audit`, working tree at `89074e0`. Compiled
2026-08-09. **Read-only phase: no site file was opened for writing.**

Reproducible with `python3 docs/audit/scripts/link_depth.py [1-5]`, which reuses the
graph `link_graph.py` already builds. Findings continue the audit's sequence at
`PH03-048`.

**This phase closes PH00-001**, the nav-only link-equity question that D3
deferred here from Phase 0.

---

## 1. Click depth from `/`

Breadth-first search from `index.html`, run twice: once over `<a href>` in raw
HTML as a non-rendering crawler sees it, once adding the two runtime-injected
templates as edges from every page.

| Depth | RAW (no JavaScript) | INJECTED |
| ---: | ---: | ---: |
| 0 | 1 | 1 |
| 1 | 4 | 29 |
| 2 | 19 | 350 |
| 3 | **184** | **81** |
| 4 | **253** | 0 |
| unreached | 2 | 2 |

The two unreached are `404.html` and `confirmation.html`, both `noindex`, both
correct. **461 of 463 pages are reachable without JavaScript**, unchanged from
Phase 0.

Raw depth by family:

| Family | min / median / max | Pages |
| --- | --- | ---: |
| root | 0 / 2 / 3 | 7 |
| notes-other | 1 / 2 / 2 | 3 |
| past-papers | 1 / 2 / 2 | 5 |
| notes-hub | 2 / 2 / 2 | 7 |
| glossary | 2 / 3 / 3 | 3 |
| flashcards | 2 / 3 / 3 | 7 |
| **notes-topic** | **3 / 3 / 3** | 166 |
| **ppq** | 2 / **4** / 4 | 90 |
| **mcq-hub** | 3 / **4** / 4 | 7 |
| **mcq-topic** | **4 / 4 / 4** | 166 |

## 2. Anchor text

2,563 internal `<a>` occurrences in page bodies (templates excluded, since their
anchor text is identical on every page by construction), across 971 distinct
strings.

Strings used more than 50 times — P3's stated threshold:

| Uses | String | What it is |
| ---: | --- | --- |
| 441 | `Home` | breadcrumb root |
| **345** | `Book a Free Intro Call` | **commercial CTA** |
| 173 | `Revision Notes` | breadcrumb |
| 172 | `Practice Questions` | breadcrumb |
| **166** | `Back to the notes` | **mcq → notes twin** |
| 89 | `Past Paper Questions` | breadcrumb |
| 52 | `Edexcel` | breadcrumb |

Five of the seven are breadcrumb segments, which are *supposed* to repeat. Two
are not, and they are PH03-051 and PH03-050.

Anchor diversity by destination family:

| Destination family | Inbound | Distinct anchors | Top string's share |
| --- | ---: | ---: | ---: |
| mcq-topic | 228 | **228** | 0% |
| notes-hub | 190 | 185 | 3% |
| ppq | 561 | 290 | 16% |
| mcq-hub | 351 | 174 | 49% |
| root | 808 | 19 | 55% |
| **notes-topic** | 219 | 54 | **76%** |
| notes-other | 177 | 5 | 98% |

## 3. Hub / spoke integrity — perfect

Every `<dir>/index.html` against the pages in its directory:

```
13 hub directories, 332 spokes
missing hub -> spoke links : 0
missing spoke -> hub links : 0
```

And the cross-family pairing:

```
notes-topic <-> mcq-topic pairs : 166
notes -> mcq : 166 / 166        mcq -> notes : 166 / 166
```

**Nothing is missing in either direction anywhere.** This is a genuinely strong
result for a hand-maintained site of this size and it should not be re-audited.

## 4. Fragment targets — perfect

```
internal links carrying a #fragment : 4,979
fragments that do not resolve       : 0
```

Every `#anchor` on the site points at an `id` (or `name`) that exists on the
target page. 4,979 of them, checked cross-page, not just same-page.

---

## Findings

### PH03-048 — Without JavaScript, 253 of 463 pages sit at click depth 4; with it, nothing is deeper than 3

**Severity:** Medium · **Category:** Crawl architecture · **CERTAIN**

**Evidence.** §1. The raw graph's deepest tier holds 253 pages: all 166
`mcq-topic`, 4 of the 7 `mcq-hub`, and 83 of the 90 `ppq`. The injected graph has
a maximum depth of 3 and puts 350 pages at depth 2.

The raw path to a practice-questions page is:

```
/  →  /revision-notes/  →  /revision-notes/edexcel-theme-1/
   →  …/1-1-1-economics-as-a-social-science.html
   →  /practice-questions/edexcel-theme-1/1-1-1-….html
```

Five URLs, four clicks. **The practice-questions family has no shorter raw
route** because its six hubs are themselves at depth 4 — they are linked from the
injected nav and from their own topic pages, and from almost nothing else in page
bodies. The `mcq-hub` pages carry 22–56 raw inbound links each, and every one of
them comes from a page that is itself at depth 3 or 4.

**Why it matters, and why it is Medium rather than High.** `AUDIT-PLAN.md`'s
"good looks like" was "nothing important beyond depth 3", and 253 pages are at 4.
But depth is a proxy for crawl priority, not a threshold with a cliff, and three
things soften it: every one of the 253 is in the sitemap; every one is reachable;
and Google renders JavaScript, so its effective depth is the injected figure.
The exposure is to non-rendering crawlers and to the render-budget delay, not to
discovery.

**Recommendation — 8 links from 2 pages remove the depth-4 tier entirely.**

Only four pages sit at raw depth 1: `revision-notes/index.html`,
`past-papers/index.html`, `tutoring.html` and `marking.html`. A hub can only be
pulled to depth 2 by a link from one of those, and that is what makes the fix so
small. Simulated over the real graph:

| Change | d2 | d3 | **d4** |
| --- | ---: | ---: | ---: |
| today | 19 | 184 | **253** |
| **A.** `/revision-notes/` → the 6 practice-questions board hubs | 25 | 350 | **81** |
| **B.** each notes board hub → its practice hub | 19 | 190 | 247 |
| **D.** `/past-papers/` → the 2 past-paper-question board hubs | 21 | 263 | 172 |
| **A + D** | 27 | **429** | **0** |

**A + D is 8 links across 2 hand-written pages and leaves nothing on the site
deeper than 3 clicks.** B — the intuitive fix, linking each notes board hub to
its practice twin — moves only 6 pages, because those hubs are themselves at
depth 2, so their spokes land back on 4. That is worth recording, because B is
what one would reach for without measuring.

Both links are honest. A revision-notes index that links to the matching
practice-question hubs describes a real relationship, and `/past-papers/` already
links to `/past-paper-questions/` generically — D just makes it per board.

This is **not** on `seo/07b-link-decisions.md`'s declined list — that document
declined PDF links, more `tutoring`/`marking` links, ppq anchor reuse, and
raising notes→ppq coverage. These 8 links are new.

**Effort:** S — two hand-written pages, eight links · **Risk of acting:** Low ·
**Risk of not acting:** Low-Medium · **Dependencies:** none · **Status:** OPEN

### PH03-049 — PH00-001 ruled on: the site's two best-earning pages have exactly one raw inbound link each, and the existing decision not to manufacture more still stands

**Severity:** Medium-High · **Category:** Link equity · **CERTAIN** ·
**Closes PH00-001**

**Evidence.** Phase 0 measured that eleven URLs draw ≥98% of their inbound links
from the injected templates. P3 resolves what that costs, per URL — and the
answer is not what the phrasing suggested.

**Discovery is not at risk.** Every injection-dependent URL is reachable in the
raw graph; none is an orphan. What the injection buys is depth:

| Page | Raw inbound | Raw depth | Injected depth |
| --- | ---: | ---: | ---: |
| `past-papers/edexcel-b/` | **1** | 2 | 1 |
| `past-papers/ocr/` | **1** | 2 | 1 |
| `privacy.html` | 1 | 3 | 1 |
| `faq.html` | 2 | 2 | 1 |
| `revision-notes/macro-application/` | 2 | 2 | 1 |
| `contact.html` | 3 | 2 | 1 |
| `about.html` | 4 | 2 | 1 |
| the 6 `practice-questions/*/` hubs | 22–56 | **4** | 1 |
| `past-papers/aqa/` | 164 | 2 | 1 |
| `past-papers/edexcel/` | 184 | 2 | 1 |

**The two with a single inbound link are the two that earn the site's traffic.**
From `seo/performance-pages.csv`, summing the trailing-slash and `/index.html`
rows (the same page, mid-consolidation):

| URL | Clicks | Impressions |
| --- | ---: | ---: |
| `/past-papers/edexcel-b/` | 78 + 80 = **158** | 7,214 + 4,476 = **11,690** |
| `/past-papers/ocr/` | 65 + 68 = **133** | 4,757 + 4,684 = **9,441** |
| **Together** | **291** | **21,131** |

That is larger than the figure `00-INVENTORY.md` §3 recorded (143 clicks / 11,971
impressions), which counted only the trailing-slash form. **Correction noted.**

**Why they have one link, and why that is not carelessness.** Both are linked
from `/past-papers/`, and from nothing else. `past-papers/aqa/` and
`past-papers/edexcel/` have 164 and 184 because the notes, practice-questions and
past-paper-question families link to them — and those families cover **only
Edexcel A and AQA**. Nothing on the site is *about* Edexcel B or OCR, so nothing
on the site has an honest reason to link to their past papers.

`seo/07b-link-decisions.md` reached exactly this conclusion and recorded it as
item 4b: *"Manufacture links to `/past-papers/edexcel-b/` and `/ocr/` —
**decline** — no honest anchor exists."*

**The ruling.** **That decline stands, and P3 does not re-propose it.**
`DO-NOT-BREAK.md` requires new evidence to reopen a declined decision, and the
new evidence P3 has — the single inbound link, the 99.8% injection dependency,
the corrected traffic figures — sharpens the *cost* without touching the
*reason*. There is still no honest anchor.

**What is available, and was not considered in 2026-08-08:** the constraint binds
on the leaf pages, not on the hub. `/past-papers/` has **6 raw inbound links**
(`index.html`, `faq.html`, `404.html`, `past-paper-questions/index.html` and the
two diagram galleries) and is the sole raw route to both leaves. Strengthening
the hub is honest — a past-papers index is a relevant destination from many pages
— and it lifts both leaves without inventing an anchor for either.

**Recommendation.** Do not manufacture leaf links. Instead:

1. **Raise `/past-papers/` inbound from the notes and practice families**, where
   a past-papers link is already the established pattern — the `notes-cta` block
   on every topic page already links to *that page's board's* past papers, so the
   generic hub is the natural companion link. This lifts edexcel-b and ocr by one
   degree each, honestly.
2. **Re-measure at the day-45 GSC read (≈2026-09-22).** These two URLs rank at
   scale today on one internal link each, which is itself evidence that internal
   equity is not what is carrying them. If the day-45 read shows them stable, the
   right answer may be to do nothing at all — and that is a legitimate outcome,
   not a failure to act.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low —
these pages are performing · **Dependencies:** day-45 GSC read ·
**Status:** OPEN. **PH00-001 is CLOSED by this finding.**

### PH03-050 — 76% of the internal anchor text pointing at the site's notes pages reads "Back to the notes"

**Severity:** Medium · **Category:** Anchor text · **CERTAIN**

**Evidence.** §2. Notes topic pages receive 219 internal inbound links across 54
distinct anchor strings, and **166 of the 219 (76%) are the single string
`Back to the notes`** — one from each practice-questions topic page to its notes
twin.

The same generator pair does the opposite direction well. Links *into*
`mcq-topic` pages number 228, with **228 distinct anchor strings** — the notes
pages' teaser links carry the spec code and topic title.

```
notes-topic  destinations : 219 inbound,  54 distinct, top string 76%
mcq-topic    destinations : 228 inbound, 228 distinct, top string  0%
```

**Why it matters.** The notes topic pages are the site's primary content and its
ranking target. Three-quarters of their internal anchor text carries no topical
signal at all — `Back to the notes` says nothing about elasticity, or market
failure, or aggregate demand. The forward link proves the data to write a better
one is already in hand: `questions-data/<board-dir>/<spec>.json` holds `title`
and `spec` on all 166, and PH06-028 established that the notes page already
carries a verbatim copy of `notesTeaser` from that same file.

This also sits directly beside P5's finding that on the 22 near-identical
Edexcel/AQA page pairs, the `<title>`, `<h1>`, description and `spec-alert` are
the *only* things differentiating them. Internal anchor text is a differentiator
the site currently declines to use.

**Recommendation.** Change the back-link anchor in
`scripts/build_questions.py` from `Back to the notes` to the topic's own name —
`1.2.3 Price, Income and Cross Elasticities of Demand revision notes`, or
`Back to the 1.2.3 notes` if the shorter register is preferred. **One string in
one generator, then re-run**; the output is regenerated for all 166 pages and no
hand edit is involved.

Two guards, both already recorded: it must not reuse the ppq topic-chip anchor
string (`seo/07b-link-decisions.md` §5), and it is a **link text** change on a
generated page, not a change to any notes prose.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low-Medium ·
**Dependencies:** none · **Status:** OPEN

### PH03-051 — 345 internal links carry the identical commercial anchor `Book a Free Intro Call`

**Severity:** Low · **Category:** Anchor text · **CERTAIN**

**Evidence.** §2. `tutoring.html` receives 350 internal inbound links from page
bodies, of which **345 read `Book a Free Intro Call`** — 99%, across 6 distinct
strings in total. It is the second most repeated anchor string on the site, after
the breadcrumb `Home`.

**Why it matters, and why it is Low.** An exact-match commercial anchor repeated
345 times is the classic over-optimisation pattern. Two things argue it is fine
here: it is a *call to action*, not a keyword-match anchor — nobody searches
"book a free intro call" — and `seo/07b-link-decisions.md` §5 has already
declined *more* links to `tutoring.html` on the grounds that it is the
most-linked page on the site (449 inbound including templates).

So the count is known and the growth is already capped. What is not recorded is
the anchor uniformity.

**Recommendation.** No action, and log it as considered. If the notes CTA is ever
reworded for another reason, vary this string across boards or themes at the same
time — it costs nothing to do then and is not worth a 166-page edit on its own.
Revisit only if the day-45 GSC read shows `tutoring.html` losing ground.

**Effort:** S if bundled, M standalone · **Risk of acting:** Low ·
**Risk of not acting:** Low · **Dependencies:** none ·
**Status:** OPEN, no action recommended

---

## What Phase 3 checked and found clean, so nobody re-audits it

- **Hub/spoke integrity is perfect.** 13 hub directories, 332 spokes, **0**
  missing links in either direction. Plus 166/166 notes↔mcq pairing, both ways.
- **All 4,979 `#fragment` targets resolve**, checked cross-page.
- **0 internal links with empty or image-only anchor text.**
- **461 of 463 pages reachable without JavaScript**, 0 orphans among the
  template-linked URLs. Re-confirms Phase 0.
- **The ppq topic-chip monoculture is gone.** `AUDIT-PLAN.md` carried forward
  "68 links reading exactly `2.6.2 Demand-side Policies`" as P3 scope. Measured
  today: **0** links carry that string, and **0** links use the `?topic=` query
  form at all. `55dda8a` re-pointed them. Links into `/past-paper-questions/`
  now number 561 across **290** distinct anchors. Resolved before the audit
  started; do not look for it again.
- **971 distinct anchor strings across 2,563 internal links** — the distribution
  is healthy apart from the two cases logged above.

---

## Corrections to earlier audit documents

- **`00-INVENTORY.md` §3** states the two top injection-dependent URLs earn "143
  clicks and 11,971 impressions between them". Counting both the trailing-slash
  and `/index.html` rows in `seo/performance-pages.csv`, the correct figures are
  **291 clicks and 21,131 impressions**. The conclusion drawn from it is
  unchanged and is now stronger.

## Handed on

| Item | To | Why |
| --- | --- | --- |
| PH03-049 step 2, the day-45 re-measure | **≈2026-09-22** | Joins PH05-019 and PH05-021 on the same dated dependency. |
| PH03-048 and PH03-050, both generator-level | **P11** | Both are one-line changes to a Python generator plus a re-run, and both are cheaper once D18's shell module exists. |
| **D18 migration Phase 7** — baking the header/footer at build time | **unblocked** | It was gated on this phase. See below. |

## The ruling migration Phase 7 was waiting for

D19 recorded that baking the header and footer at build time "trades a 1-file nav
edit for a rebuild, and whether that trade is worth making depends on P3's ruling
on link equity".

**P3's ruling: the trade is worth making, but link equity is not the reason to
make it.** The injection costs depth, not discovery — 461 of 463 pages are
reachable without it, and the eleven injection-dependent URLs are all reachable
too. Baking the templates would move 253 pages from raw depth 4 to raw depth 1–2
and give every page a real `<nav>` in its source, which is a genuine gain. But
the two pages where the equity question actually bites (PH03-049) have **one**
raw inbound link each for a reason no template change fixes — nothing on the site
is about their exam board.

So: **proceed with migration Phase 7 on its own merits** — one source of truth
for the nav, no runtime fetch, no jQuery dependency for `inject-templates.js`
(PH08-043) — and do not justify it as a link-equity fix, because it is not one.
