# Performance pass — measurements, pins and what was left alone (2026-08-23)

The four performance items from the August site review, built on
`feature/performance` in four commits (one per phase) — `9b6b61c` MathJax,
`5331fc7` fonts, `b6a299e` hubs + Calendly, `df68d2a` images + CSS + head.
The narrative is in `PROGRESS.md`; this file is the numbers.

## 1. Byte counts, before → after

Counted by script over the committed tree (`main` at `806b44e` against the
branch head).

| Measure | Before | After |
| --- | ---: | ---: |
| Pages loading MathJax (jsDelivr, ~300 KB) | 126 | **59** — exactly the pages whose body has maths |
| Pages with a `cdn.jsdelivr.net` preconnect | 0 | 59 |
| External `<head>` origins on every page | `fonts.googleapis.com`, `fonts.gstatic.com` (463/463) | **none** (463/463); + `cdn.jsdelivr.net` on the 59 MathJax pages, + Calendly's two on tutoring.html |
| Render-blocking Google Fonts stylesheet | 1 per page (~38 KB raw, ~3 KB gz) | 0 |
| Font files | 3 families, 11 cuts, from Google | 2 families, 9 cuts (Source Sans Pro ×6, Merriweather ×3), self-hosted, 238 KB total; a page still fetches only the cuts it renders (typically 5–6 files, ~75 KB). Open Sans went in the follow-up commit |
| `past-paper-questions/edexcel/index.html` | 799,267 B, ~5,600 DOM nodes (304 cards) | **87,857 B, 762 nodes** (20 cards + note) |
| `past-paper-questions/aqa/index.html` | 619,740 B (248 cards) | **82,478 B** (20 cards + note) |
| JSON fetched by a board hub / section page | `questions.json` 423,625 B | `<board>/questions.json` 226,154 B (Edexcel), 197,861 B (AQA) |
| `questions.json` (master) | 423,625 B | 423,625 B, byte-identical |
| tutoring.html third-party at load | Calendly widget.css (render-blocking) + widget.js + the booking iframe (~3.4 MB, Lighthouse weight) | nothing until the booking section is a screen away; 0 Calendly requests at the top of the page |
| `images/` | 7.0 MB; 5 files > 150 KB | + 116 WebP files; every PNG/JPEG still at its URL |
| Diagram PNGs → lossless WebP (106) | 5,293 KB | 3,588 KB (**−32.2 %**); sample of 10 before deciding: −29.8 % |
| Photos (served variant on a phone / desktop) | eliot_shirt.JPG 110 KB; eliot_grad.jpg 612 KB; eliot_boat.jpeg 198 KB; marking examples 168 / 162 KB | 14 / 34 KB; 34 / 142 KB; 30 / 103 KB; 19 / 48 KB; 23 / 69 KB |
| `css/main.css` | 78,987 B | 76,047 B (ul.social block, .footer-dark, 27 dead prefixes) |

Images over 150 KB, as asked, with where each is used and how large it
renders (CSS px; measured in Chrome at 360 / 768 / 1280):

| File | Bytes | Intrinsic | Pages | Rendered |
| --- | ---: | --- | --- | --- |
| images/eliot_grad.jpg | 612 KB | 1395×1423 | about.html | hidden / 241 / 427 px |
| images/eliot_boat.jpeg | 198 KB | 800×600 | about.html | 231 / 190 / 368 px |
| images/marking-example-annotated-paper.jpg | 168 KB | 800×1115 | marking.html | 288 / 686 / 593 px (cropped to 338 px tall) |
| images/diagrams/trade-union.png | 167 KB | 3544×1436 | 2 notes pages + micro gallery | 246 / 598 / 800 px |
| images/marking-example-feedback-email.jpg | 162 KB | 800×1131 | marking.html | 288 / 686 / 593 px |

(eliot_shirt.JPG is 110 KB, under the line, but was converted too: it is on
three pages at 240–400 px.)

## 2. Lighthouse

`seo/tools/run_lighthouse.py`, Lighthouse 12, mobile, simulated throttling,
3 runs per URL, median. Two pages were added to its list for this pass (the
Edexcel ppq board hub and tutoring.html); the six original entries are
unchanged.

**Three runs were made, and the first two taught something about the
method.** The live-site baseline (`seo/lh-perf-before/`) is the real
before. The after cannot be live until the PR merges, so the after is a
local A/B — but a local A/B of *this* change is only fair over HTTP/2:

- `python3 -m http.server` (HTTP/1.0, no keep-alive, no gzip) made the
  self-hosted fonts measure *slower* than Google's — Lighthouse charged a
  new connection per request and raw bytes. Discarded.
- An HTTP/1.1 keep-alive + gzip server (`seo/tools/serve_like_pages.py`)
  still showed self-hosting as slower: Lighthouse models six connections
  per origin over HTTP/1.1, so fonts on the site's own origin queued behind
  its CSS and JS, which they never did on `fonts.gstatic.com`. Discarded.
- `seo/tools/serve_h2.js` — HTTP/2 + TLS + gzip, which is what GitHub
  Pages (Fastly) serves — with `run_lighthouse.py --insecure` for the
  self-signed certificate. **This is the A/B below**, both sides on it.

| Page | Perf | LCP | CLS | TBT | FCP | Weight | Render-blocking |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| homepage | 99 → **100** | 1.57 → **1.36 s** | 0.002 → 0.002 | 0 → 0 ms | 1.57 → 1.36 s | 339 → **171 KB** | 767 → 561 ms |
| section-hub | 99 → **100** | 1.57 → **1.50 s** | 0.001 → 0.002 | 0 → 0 ms | 1.57 → 1.35 s | 212 → **132 KB** | 775 → 572 ms |
| notes-topic | 68 → **96** | 5.07 → **2.25 s** | 0.000 → 0.006 | 87 → 90 ms | 5.07 → 2.10 s | 676 → **598 KB** | 1689 → 1136 ms |
| practice-questions | 99 → **99** | 1.56 → **1.80 s** | 0.001 → 0.001 | 0 → 0 ms | 1.56 → 1.65 s | 304 → **213 KB** | 616 → 712 ms |
| past-paper-questions | 99 → **100** | 1.56 → **1.51 s** | 0.054 → 0.003 | 0 → 0 ms | 1.56 → 1.35 s | 227 → **134 KB** | 771 → 561 ms |
| flashcards | 99 → **100** | 1.81 → **1.21 s** | 0.003 → 0.005 | 0 → 0 ms | 1.57 → 1.05 s | 268 → **189 KB** | 774 → 260 ms |
| ppq-board-hub | 98 → **100** | 1.87 → **1.51 s** | 0.001 → 0.001 | 0 → 0 ms | 1.87 → 1.35 s | 340 → **179 KB** | 681 → 408 ms |
| tutoring | 98 → **100** | 2.26 → **1.65 s** | 0.029 → 0.030 | 0 → 0 ms | 1.59 → 1.35 s | 3380 → **176 KB** | 613 → 368 ms |

Both columns are `main` (`806b44e`) against the branch head, served from the
same machine by `serve_h2.js`, 3 runs each, medians; raw reports in
`seo/lh-perf-before-local/` and `seo/lh-perf-after/` (gitignored except the
`medians.json`). Read with the usual caution about lab medians
(`seo/09`): the notes-topic "before" was bimodal — runs of 1.56 / 5.08 /
5.65 s, the slow mode being the Google Fonts → MathJax race — and the
"after" was 2.26 / 2.26 / 1.36 s, so the headline 5.07 → 2.25 s is a change
of mode, not a 2.8 s saving on every load. practice-questions is the one
page whose lab LCP got worse (1.56 → 1.80 s on all three runs, perf 99
both sides, weight −30 %); the rest moved the right way or not at all.
Weight is down on all eight pages; tutoring.html's 3.4 MB was Calendly's
booking iframe, now loaded only when the booking section is near.

### Live, before → after (the real CDN; PR #19 merged 2026-08-23 as `367297b`)

`seo/lh-perf-before/` was taken against the live site before Phase 1;
`seo/lh-perf-live-after/` about 40 minutes after the merge deployed. Same
tool, same flags, same 8 URLs, 3 runs, medians.

| Page | Perf | LCP | CLS | TBT | FCP | Weight | Render-blocking |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| homepage | 91 → **100** | 2.82 → **1.16 s** | 0.000 → 0.002 | 0 → 0 ms | 2.82 → 1.16 s | 343 → **176 KB** | 1818 → 249 ms |
| section-hub | 90 → **99** | 2.92 → **1.61 s** | 0.000 → 0.000 | 0 → 0 ms | 2.92 → 1.48 s | 214 → **124 KB** | 1987 → 583 ms |
| notes-topic | 70 → **70** | 5.05 → **4.69 s** | 0.000 → 0.000 | 76 → 104 ms | 4.00 → 4.54 s | 679 → **592 KB** | 1681 → 1038 ms |
| practice-questions | 86 → **98** | 3.29 → **1.95 s** | 0.001 → 0.000 | 0 → 0 ms | 3.29 → 1.82 s | 308 → **233 KB** | 2284 → 885 ms |
| past-paper-questions | 89 → **98** | 2.84 → **1.55 s** | 0.000 → 0.000 | 0 → 0 ms | 2.84 → 1.40 s | 230 → **140 KB** | 1870 → 486 ms |
| flashcards | 90 → **99** | 2.86 → **1.83 s** | 0.000 → 0.000 | 0 → 0 ms | 2.86 → 1.53 s | 272 → **181 KB** | 1997 → 741 ms |
| ppq-board-hub | 98 → **98** | 1.95 → **1.70 s** | 0.001 → 0.000 | 0 → 16 ms | 1.95 → 1.40 s | 351 → **187 KB** | 696 → 419 ms |
| tutoring | 56 → **98** | 11.40 → **1.77 s** | 0.000 → 0.000 | 0 → 55 ms | 9.71 → 1.47 s | 3382 → **182 KB** | 985 → 390 ms |

The render-blocking column is the one to read: every page is down to
`main.css` plus at most one other file, because the Google Fonts
stylesheet — the largest render-blocking item on every page since `seo/09`
— is gone. Weight is down on all eight; tutoring's 3.4 MB was Calendly's
booking iframe, now fetched only when the booking section is near.

**notes-topic is the one page that did not move, and it is bimodal as it
always was:** after-runs of 4.69 / 4.84 / 1.15 s (before: 5.05 s median).
The sample is deliberately the densest MathJax page; in the slow runs the
document arrives in ~190 ms and then nothing paints for ~4 s ("render
delay" in the LCP breakdown), in the fast run it paints at 1.15 s. That is
the MathJax page's own problem — the same page over the same CDN did this
before any of these changes — and the fix is the OWNER-TODO item about
moving the notes from MathJax to pre-rendered KaTeX, not anything in this
pass.

## 3. Pins changed, and why

| File | Pin | Was → is | Why |
| --- | --- | --- | --- |
| `scripts/verify_page_shell.py` | `EXTRA_SCRIPT_PAGES` | `{calendly widget.js: {tutoring.html}}` → `{}` | the Calendly `<script src>` became an inline lazy loader |
| `scripts/verify_page_shell.py` | `EXPECTED_SHAPES["root"]` tails | 2 → 1 | same: every root page now ends in the plain two-script tail |
| `scripts/verify_css_load_order.py` | check 2 | fontawesome → Google Fonts → main.css → fontawesome → main.css; Google origins held at 0/463; body-face preload at 463/463 | the Google link is gone |
| `scripts/test_question_search.js` | — | new checks: `HUB_CARDS == PAGE_SIZE`, hub cards/note/payloads/`data-src` | Phase 3 |
| `scripts/verify_image_dimensions.py` | — | new checks: `<source srcset>` candidates, diagram PNG/WebP twins | Phase 4 |

No `EXPECTED_SHAPES` head count moved: every family's pages changed the
same way in Phases 2 and 4.

## 4. Deliberately left alone

- ~~Open Sans~~ — kept at first (seven rules, not four; two on every
  page), then swapped for Source Sans Pro at the same weights on Eliot's
  instruction the same day. Two families, nine font files. The breadcrumb
  had to be pinned at 400 (see DO-NOT-BREAK).
- **Source Sans Pro stays Source Sans Pro**, not Source Sans 3.
- **The Dopetrope `.row`/`.col-*` grid and `#main .row > div[class*="col-"]`**
  — audit done (five pages, ~30 rows; `contact.css` has a rival bare grid
  `main.css` is currently beating; `.profile-highlight`/`.teaching-methods`
  restyle the same classes). A page-by-page conversion with
  `computed_style_diff.py` each, not a deletion; OWNER-TODO has it.
- **The 6 ppq section pages** still bake every card (61–126) — the no-JS
  list lives there now.
- **Merriweather latin-ext**: one glyph (₹ on AQA `2-1-4`) falls back to
  Georgia. Not worth a 50 KB file.
- **Δ, →, ←, ∞ etc.** already fell back before (no Google subset of the
  text families covered them), so nothing changed there.
- **The maskable icon** needs artwork — OWNER-TODO.

## 5. Things measured on the way that are worth keeping

- MathJax's `matchFontHeight` scales formulae against whatever font the
  container has *when it measures*. Before, on a cold visit, that was the
  Georgia fallback (118 %); now the self-hosted Merriweather arrives first
  and it measures 125.7 % — the state a cached visitor already saw. A ~6 %
  larger formula on first visits to the 59 MathJax pages, and one fewer
  late reflow.
- Google serves Merriweather and Open Sans as **variable** fonts to modern
  browsers and static instances to old ones. The static instances were
  checked with fontTools against the variable files at the same weight: 0
  advance-width mismatches, identical x-height, so the `size-adjust`
  fallbacks in `main.css` did not need re-tuning.
- Calendly's `widget.js` **appends** its spinner and iframe to the host
  div; it does not clear it. Anything put inside the div as a fallback has
  to be removed by the page's own script.
