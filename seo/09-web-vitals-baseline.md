# Phase 9 — Core Web Vitals baseline

> ## ⚠️ Superseded in part — read this first
>
> The medians in this document came from **3 runs per URL**. Re-running the
> identical method at **7 runs against the same unchanged deployed code** gave
> materially different answers:
>
> | Page | 3-run LCP | 7-run LCP | 3-run perf | 7-run perf |
> | --- | ---: | ---: | ---: | ---: |
> | homepage | 4.73 s | **3.04 s** | 72 | **88** |
> | notes-topic | 6.84 s | **3.04 s** | 61 | **85** |
> | practice-questions | 5.08 s | **1.79 s** | 69 | **99** |
> | past-paper-questions | 4.98 s | **1.80 s** | 72 | **75** |
>
> The runs are **bimodal**, not noisy — each page clusters around ~1.6 s and
> ~5–8 s, so the median reports whichever mode won rather than the page's
> speed. `notes-topic` at 7 runs: 7.3, 8.0, 1.7, 7.1, 1.8, 3.0, 3.0.
>
> **So the absolute timings below are not trustworthy, and the verdict "LCP
> 4.7–6.8 s, performance 61–72, poor" was wrong** — it was reading noise. Lab
> medians over the CDN are not a usable instrument for this site.
>
> What survives, because it comes from the request trace rather than a timing
> median: the 4-deep critical chain, the Google Fonts stylesheet being the
> largest render-blocking item on 6 of 6 pages, and the 190 pages with no
> preconnect. Those were all real and all fixed.
>
> The attributable measurement is the **local A/B in
> `seo/10-architecture-verification.md`**, which removes the CDN, has a
> run-to-run spread of 0.00–0.16 s, and shows the change is worth
> −0.15 to −0.31 s of LCP and −10.5% render-blocking.


Measured **before any page in this pass was modified**, so a later regression can
be attributed. Reproduce with:

```
python3 seo/tools/run_lighthouse.py --out <dir> --runs 3
```

Lighthouse **12.8.2**, mobile form factor, simulated throttling, 3 runs per URL,
**median per metric**. Run against the **live** site on 2026-08-08, not a local
server — the largest finding is a serialised third-party request chain that a
localhost run would understate by construction.

---

## ⚠️ Two caveats, and they are not boilerplate

### 1. This is LAB data

**Field data status: unconfirmed at time of writing.** Eliot is checking
Experience → Core Web Vitals in Search Console. With ~223 clicks on the busiest
page the site is very likely below the CrUX reporting threshold, in which case
GSC will report "no data" or too few URLs.

**Google ranks on field data, not on this.** Everything below is lab data:
directional, useful for finding *what* is slow and in what order, and not a
prediction of what any real user experiences. Simulated mobile throttling models
a slow 4G connection with a 4× CPU slowdown, which is harsher than most of this
site's actual traffic.

### 2. Run-to-run spread is larger than most effects worth measuring

| Page | LCP across the 3 runs | Spread |
| --- | --- | ---: |
| homepage | 5.16 / 4.73 / **1.54** s | 3.62 s |
| section-hub | 5.01 / 4.49 / 4.85 s | 0.52 s |
| notes-topic | 7.76 / 6.84 / **2.84** s | 4.92 s |
| practice-questions | 5.08 / 5.19 / **1.79** s | 3.40 s |
| past-paper-questions | 4.98 / 5.99 / **1.80** s | 4.18 s |
| flashcards | 5.52 / **1.81** / 5.31 s | 3.71 s |

Five of six sets contain one run 3–5 s faster than the other two. The median
correctly rejects it, but **a spread that large means only large deltas are
attributable**. The after-measurement should use **`--runs 7`**, not 3, and any
change smaller than about 1 s should be treated as noise rather than a result.

---

## Medians

| Page | Perf | LCP | CLS | TBT | FCP | Speed Index | Weight |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| homepage | 72 | 4.73 s | **0.000** | 0 ms | 3.96 s | 4.76 s | 405 KB |
| section-hub | 71 | 4.85 s | **0.000** | 0 ms | 4.06 s | 4.81 s | 402 KB |
| notes-topic | **61** | **6.84 s** | **0.000** | 226 ms | 5.18 s | 5.55 s | **888 KB** |
| practice-questions | 69 | 5.08 s | **0.000** | 0 ms | 4.45 s | 4.98 s | 495 KB |
| past-paper-questions | 72 | 4.98 s | **0.000** | 76 ms | 3.32 s | 4.63 s | 519 KB |
| flashcards | 68 | 5.31 s | **0.000** | 64 ms | 4.35 s | 4.97 s | 501 KB |

**INP is not measurable in the lab** — it is a field-only metric. TBT is its lab
proxy and is reported instead. TBT is fine everywhere (0–226 ms against a 200 ms
"good" threshold), so there is no evidence of an interactivity problem.

---

## Three predictions from static analysis that the measurement killed

Stated plainly, because they were in the pre-measurement note and acting on them
would have wasted effort:

1. **"MathJax is a common cause of CLS."** ❌ **CLS is 0.000 on all six pages**,
   including the MathJax page. There is no layout-shift problem on this site at
   all. The reason is structural: jQuery and `inject-templates.js` are synchronous
   scripts, so the header/footer injection completes *before* first paint rather
   than after it. Nothing to fix.
2. **"Diagram PNGs are the LCP element on notes pages."** ❌ **The LCP element is
   text on every one of the six pages** — a hero `<h1>` or an intro `<p>`:

   | Page | LCP element |
   | --- | --- |
   | homepage | `h1.hero-title` |
   | section-hub | `p.notes-intro` |
   | notes-topic | `div.spec-alert` |
   | practice-questions | `p.quiz-intro` |
   | past-paper-questions | `p.ppq-intro` |
   | flashcards | `p.fc-intro` |

   The 26.2 MB of diagram PNGs are below the fold and 213 of 309 images already
   carry `loading="lazy"`. **They are not on the critical path.** Converting them
   to WebP is a bandwidth saving, not an LCP fix, and it is not worth the risk to
   166 hand-written pages.
3. **"The site is close to as fast as static-on-CDN gets."** ❌ Too generous.
   Performance 61–72 and LCP 4.7–6.8 s on mobile is **poor** — Google's "good"
   threshold for LCP is 2.5 s. TTFB is excellent (~100 ms, GitHub Pages is doing
   its job); everything after it is not.

**Because the LCP element is text on every page, LCP is gated entirely by when
the fonts arrive and when render-blocking CSS clears.** That makes the font
loading chain the whole story, not a nice-to-have.

---

## The actual problem: a 4-deep critical chain, on all 463 pages

`css/main.css` opens with two `@import` rules:

```css
@import url("fontawesome-all.min.css");
@import url("https://fonts.googleapis.com/css2?family=Merriweather:…&display=swap");
```

An `@import` inside a render-blocking stylesheet cannot be discovered by the
preload scanner. The browser must download and parse `main.css` before it even
learns those two requests exist. The result is a **4-deep critical request chain
on every page measured**:

```
HTML  →  /css/main.css  →  fonts.googleapis.com/css2  →  fonts.gstatic.com/*.woff2
                        ↘  /css/fontawesome-all.min.css  →  /webfonts/fa-solid-900.woff2
```

**The Google Fonts stylesheet is the single largest render-blocking item on all
six pages** — 2.9 KB of CSS costing **782–834 ms**, entirely because it is
discovered late and lives on a third-party origin.

| Page | Total render-blocking | Longest chain |
| --- | ---: | ---: |
| notes-topic | **2342 ms** | 4 deep, 586 ms |
| past-paper-questions | **2334 ms** | 4 deep, 1329 ms |
| practice-questions | 1684 ms | 4 deep, 1393 ms |
| flashcards | 1667 ms | 4 deep, 541 ms |
| section-hub | 1421 ms | 4 deep, 1400 ms |
| homepage | 1217 ms | 4 deep, 534 ms |

### Made worse: 190 pages have no font `preconnect` at all

| | Pages | Preconnect to `fonts.gstatic.com`? |
| --- | ---: | --- |
| `practice-questions/` | 173 | ✅ yes |
| `past-paper-questions/` | 90 | ✅ yes |
| `flashcards/` | 7 | ✅ yes |
| `revision-notes/glossary/` | 3 | ✅ yes |
| **`revision-notes/` topic + hub pages** | **176** | ❌ **no** |
| **root pages** (`index`, `tutoring`, `marking`, `faq`, …) | **9** | ❌ **no** |
| **`past-papers/`** | **5** | ❌ **no** |

The pattern is exact: **every generated section emits the preconnect; no
hand-written page has it.** Lighthouse flags "Preconnect to required origins"
worth 213–309 ms on precisely the three pages that lack it (homepage,
section-hub, notes-topic) and does not flag it on the three that have it.

This includes the homepage and every commercial page.

### Font payload is heavy for a text-LCP site

263 KB from Google Fonts on the notes page, for three families and eleven cuts:

| File | Size |
| --- | ---: |
| Merriweather (2 cuts) | **146.1 KB** |
| Open Sans (1 cut) | 42.5 KB |
| Source Sans Pro (5 cuts) | 71.7 KB |
| `fa-solid-900.woff2` (self-hosted) | 76.6 KB |

`&display=swap` is already set, so text is never invisible. FontAwesome **is**
in use — 122 icon instances, mostly `fa-plus` on FAQ and accordion toggles — so
it cannot simply be dropped.

### Third-party weight on the notes page

| Origin | Transfer | Main-thread blocking |
| --- | ---: | ---: |
| jsDelivr (MathJax 3 + its woff fonts) | 292.5 KB | 164 ms |
| Google Tag Manager (gtag) | 165.8 KB | 71 ms |
| Google Fonts | 263.1 KB | 0 ms |

MathJax loads `async`, so it is **not** render-blocking. It costs 292 KB and
164 ms of main thread on the 127 pages that use it, and produces no layout shift.

---

## Ranked fixes — (pages affected × measured impact) / effort

| # | Fix | Pages | Measured basis | Effort | Risk |
| --- | --- | ---: | --- | --- | --- |
| **1** | **Replace both `@import`s in `css/main.css` with `<link>` tags** | **463** | Top render-blocking item on 6/6 pages, 782–834 ms each; collapses a 4-deep chain to 2 | 1 file + a line in each page's `<head>` | Medium — sitewide CSS |
| **2** | **Add font `preconnect` to the 190 pages missing it** | **190** | LH flags 213–309 ms on exactly those pages | Script, additive `<head>` lines | Low |
| **3** | Trim Google Fonts cuts (5 Source Sans Pro weights, 2 Merriweather) | 463 | 263 KB font payload; LCP is text | Audit which cuts CSS uses | Low, but visual |
| **4** | `loading="lazy"` on the 94 remaining notes images | 94 | Bandwidth only — not LCP | Script | Low |
| **5** | `width`/`height` on 3 images (`about.html` ×2, `tutoring.html` ×1) | 3 | CLS already 0.000 | Trivial | None |
| — | ~~WebP conversion of 112 diagram PNGs~~ | — | **Not the LCP element. Dropped.** | — | — |
| — | ~~Swap MathJax for KaTeX~~ | — | **Async, 0 CLS. Not justified.** | — | — |

### On #1, the honest caveat

Lighthouse's own "Eliminate render-blocking resources" estimate is 774–2788 ms
per page, but that is a *model*, not a measurement. Fixing the `@import` cannot
recover all of it, because the font files still have to download — it removes one
round trip of *discovery latency*, not the transfer. **The real figure is
whatever the after-measurement shows**, at `--runs 7`, and it goes in
`seo/10-architecture-verification.md` whether or not it flatters the change.

### Proportionality

Fixes 1 and 2 are the whole of the value here and are cheap. **3, 4 and 5 are
marginal and can reasonably be declined.** Nothing below #2 is worth touching 166
hand-written pages for.

And the standing point holds: **page experience is a weak ranking signal and is
not what is holding the never-crawled pages back.** The reason to do #1 and #2 is
that they are cheap and genuinely help students on slow connections — not that
they will move rankings.

---

## What is NOT wrong

Recorded so it is not re-investigated:

- **CLS: 0.000 on all six pages.** No layout-shift problem exists.
- **TBT: 0–226 ms.** No interactivity problem.
- **TTFB ~100 ms.** GitHub Pages' CDN is fine.
- **Only 2 stylesheets per page**, both small.
- **All 7 site scripts load at end of `<body>`.**
- **0 images missing `alt`**; 3 of 309 missing dimensions.
- **Median page 29.9 KB** of HTML.
