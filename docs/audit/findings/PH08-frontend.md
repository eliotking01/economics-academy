# Phase 8 findings — front-end assets, semantics & accessibility

Branch `audit/organisation-audit`, working tree at `d7744c3`. Compiled
2026-08-09. **Read-only phase: no site file was opened for writing.**

Every figure is reproducible with `python3 docs/audit/scripts/asset_census.py [1-9]`
or the command quoted inline. Findings are numbered `PH08-033` onward and
continue the audit's single sequence; IDs are stable and never renumbered.

---

## How to read this document

§0 is vocabulary, per decision D16 — everything here should be followable
without front-end background. §1 is what was measured. §2 lists the findings.
§3 says what P8 checked and found **clean**, so nobody audits it again. §4 hands
two items to later phases. §5 is the decision brief and the questions.

**This phase does not undo the SEO work of 2026-08-08.** It does correct one
conclusion in `seo/09-web-vitals-baseline.md` — using that same body of work's
own later measurement file, which is committed in the repo and disagrees with
the document's text. That is PH08-035, and it is the most consequential finding
here.

---

## 0. The vocabulary, in plain terms

| Term | What it means here |
| --- | --- |
| **Render-blocking** | A `<link rel="stylesheet">` or a `<script>` without `defer`/`async` that the browser must download and process *before it can paint anything*. The page is blank until it finishes. |
| **CLS** — Cumulative Layout Shift | How much the page jumps around after it first appears, e.g. a panel appearing and shoving everything down. Google's "good" threshold is **0.1**; above 0.25 is "poor". It is one of the three Core Web Vitals. |
| **LCP** — Largest Contentful Paint | How long until the biggest thing on screen has drawn. |
| **FOIT** | "Flash of Invisible Text". A font set to `font-display: block` renders *nothing* in its place for up to 3 seconds while it downloads. `swap` shows a fallback font instead. |
| **Landmark** | A semantic HTML element (`<main>`, `<nav>`, `<header>`, `<footer>`) that lets a screen reader jump straight to a region. A `<section id="main">` is not a landmark; a `<main id="main">` is. |
| **Scoping** (this repo's house rule) | Prefixing every rule in a page's stylesheet with that page's wrapper class, e.g. `.quiz-page .breadcrumb { … }` rather than `.breadcrumb { … }`, so two stylesheets cannot fight over the same class name. |
| **Specificity** | How CSS decides which of two competing rules wins. `.quiz-page .breadcrumb` (two classes) beats `.breadcrumb` (one). Where specificity ties, the sheet that loads **later** wins. |
| **SRI** — Subresource Integrity | A hash on a `<script src>` pointing at someone else's server. If the file changes, the browser refuses to run it. |
| **Progressive enhancement** | Ship working HTML, then let JavaScript improve it. The opposite failure is shipping markup that only works once a script has run. |

---

## 1. Current state

### 1.1 Stylesheets — the inventory is clean

`asset_census.py 1`, over 465 published HTML files (the 463 pages plus the two
templates):

```
tracked published .css files : 22
unreferenced stylesheets     : 0
stylesheet hrefs that do not resolve to a file : 0
```

**Every stylesheet in the repo is loaded by at least one page, and every
stylesheet a page asks for exists.** That is worth stating plainly because
"dead CSS files" was in the phase brief and there are none.

Loading is also strikingly uniform. Ten of the eleven page families load exactly
one combination of stylesheets:

| Family | Pages | Distinct stylesheet sets |
| --- | ---: | ---: |
| notes-topic | 166 | 1 |
| mcq-topic | 166 | 1 |
| ppq | 90 | 1 |
| mcq-hub | 7 | 1 |
| notes-hub, notes-other, glossary, past-papers, flashcards | 25 | 2 each |
| root | 9 | 9 — one per page, as intended |

**Exactly one page loads two `css/pages/*.css` sheets** —
`revision-notes/macro-application/index.html`, which loads
`revision-notes-textbook.css` and then `macro-application.css` on top. Every
other page loads exactly one, and three pages (`404.html` and the two templates)
load none.

That single fact makes the collision risk the house rule was written to prevent
**structurally impossible today between two page sheets**. The real collision
surface is elsewhere — see PH08-038.

### 1.2 Byte weight, and what actually blocks rendering

Source sizes on disk:

| File | Size | Loaded on |
| --- | ---: | ---: |
| `css/fontawesome-all.min.css` | **69.4 KB** | 463 pages |
| `css/main.css` | 48.8 KB | 463 pages |
| `css/vendor/katex/katex.min.css` | 21.2 KB | 8 pages |
| `css/pages/revision-notes-textbook.css` | 21.1 KB | 169 pages |
| the other 18 `css/pages/*.css` | 1.2–15.4 KB | 1–166 pages each |
| `js/jquery.min.js` | **164.1 KB** | 463 pages |
| `js/util.js` | 12.6 KB | 463 pages |
| `js/jquery.dropotron.min.js` | 10.7 KB | 463 pages |
| `js/main.js` | 0.6 KB | 463 pages |

The repo already contains the measurement that matters, and it is better
evidence than file sizes: `seo/lh-live-after-7run.json`, Lighthouse 12.8.2,
mobile, **7-run medians against the live site**, committed in `8c8034b`. Its
render-blocking list is identical in shape on all six sampled pages:

| Blocking resource | Wire bytes | Blocking time | On how many of the 6 sampled pages |
| --- | ---: | ---: | ---: |
| Google Fonts stylesheet | 2,983 | **813–835 ms** | 6 / 6 |
| `js/jquery.min.js` | ~41,700 | **325–500 ms** | 6 / 6 |
| `css/fontawesome-all.min.css` | ~13,250 | **325–333 ms** | 6 / 6 |
| `css/main.css` or the page sheet | 2,797–9,670 | 162–167 ms | 6 / 6 |

Three of the four largest render-blocking items on every page of this site are
**FontAwesome, jQuery and a Google Fonts request** — see PH08-033, PH08-043 and
PH08-041.

### 1.3 The page families' measured vitals

From the same file, and from `seo/lh-baseline-live-7run.json` (the same method
run *before* the architecture pass, committed in `53a3e54`):

| Page sampled | CLS before | CLS after | LCP after | Weight |
| --- | ---: | ---: | ---: | ---: |
| `/` | 0.020 | 0.021 | 1,792 ms | 415 KB |
| `/revision-notes/` | 0.000 | 0.022 | 1,841 ms | 412 KB |
| notes-topic | **0.102** | **0.110** | 1,826 ms | **911 KB** |
| practice-questions | 0.020 | 0.021 | 1,814 ms | 507 KB |
| **past-paper-questions** | **0.635** | **0.253** | 1,977 ms | 533 KB |
| flashcards | 0.000 | 0.020 | 1,825 ms | 515 KB |

Two families are over Google's 0.1 CLS threshold. One is 2.5× over it. See
PH08-035.

---

## 2. Findings

IDs are stable. Never renumber.

### PH08-033 — FontAwesome is 69 KB of render-blocking CSS on 463 pages, defining 1,458 icons, of which 20 are used

**Severity:** Medium-High · **Category:** Assets / performance · **CERTAIN**

**Evidence.** `css/fontawesome-all.min.css` is 69.4 KB on disk, ~13.25 KB over
the wire, and is a render-blocking `<link>` in the `<head>` of all 463 pages.
Lighthouse attributes **325–333 ms of render-blocking time** to it on 6 of 6
sampled pages (`seo/lh-live-after-7run.json`).

It defines **1,458** icon glyph classes (`grep -c '\.fa-[a-z0-9-]*:before'`).
Scanning every published `.html`, every tracked `.js`, every other `.css` and
every generator in `scripts/` for `fa-*` tokens finds **20 in use**:

```
fa-bolt fa-calendar-check fa-chalkboard-teacher fa-check-double fa-clipboard-list
fa-clock fa-dribbble fa-envelope fa-facebook fa-file-alt fa-google-plus
fa-graduation-cap fa-linkedin fa-minus fa-plus fa-search fa-star fa-tumblr
fa-twitter fa-users
```

It also declares `font-display: block` on all three of its `@font-face` rules —
the FOIT setting, so icon slots render **empty** for up to 3 s while the font
downloads. No other stylesheet on the site uses `block`.

The backing font files are `webfonts/`, **2.8 MB tracked across 15 files**, of
which only the three `.woff2` (164 KB total) are fetched by any browser released
in the last decade. The `.eot`, `.svg` and `.ttf` copies — 2.49 MB — are legacy
formats that exist because FontAwesome 5 ships them.

**Why it matters.** This is the single largest ratio of shipped-to-used on the
site: 1,458 icons defined, 20 used, on every page, before the page can paint.
`4db232c` correctly moved this file *out* of an `@import` chain and into a
direct `<link>`; that fixed the chain, and left the file's size untouched.
Nothing in this finding proposes reversing `4db232c`.

**Recommendation.** Two independent changes, in order of value:

1. **Set `font-display: swap`** (or `optional`) on the three `@font-face` rules.
   One-line change per rule, no markup change, removes the FOIT. Do this first —
   it is nearly free.
2. **Ship a 20-icon subset.** FontAwesome's own build tooling, or hand-writing a
   small stylesheet with the 20 `content:` codepoints, cuts ~69 KB to ~2 KB and
   the three font files to one. The icon class names stay identical, so **no HTML
   changes at all**. The 2.49 MB of legacy font formats can then go with it.

The third option — inline `<svg>` per icon, removing the font entirely — is
cleaner still but touches markup on 463 pages, so it belongs after the template
layer of D18 exists, not before.

**Effort:** S for (1), M for (2) · **Risk of acting:** Low — verify the 20 icons
render, in the footer (brands) and on `marking.html`/`tutoring.html` (solid) ·
**Risk of not acting:** Low-Medium, ongoing · **Dependencies:** none ·
**Status:** OPEN

### PH08-034 — 26.2 MB of diagram PNGs, stored at ~2,350 px wide in RGBA, put 513 KB of images on the average notes page

**Severity:** High · **Category:** Assets / performance · **CERTAIN**

**Evidence.** `images/diagrams/*.png` is **112 files, 26.2 MB, mean 240 KB**.
Reading each file's IHDR header directly:

```
colour type : RGBA on 112 / 112      bit depth: 8 on 112 / 112
intrinsic width: min 958 px, median 2,350 px, max 3,642 px
```

Every one is a line diagram — axes, curves, labels — stored as a full-colour
image with an 8-bit alpha channel. There is not one palette (PNG-8) file among
them, and **zero WebP or AVIF anywhere on the site**.

Per notes page, summing the files each `<img>` points at:

```
notes-topic pages carrying >=1 image : 94 of 166
mean image payload                    : 513 KB / page
median                                : 388 KB
heaviest                              : 1,911 KB  (aqa-a2-macro/2-3-1-economic-growth-and-the-economic-cycle.html)
```

Lighthouse's sampled notes page weighs **911 KB** against 412–533 KB for every
other family (`seo/lh-live-after-7run.json`).

**The display width is a fraction of the stored width.**
`css/pages/revision-notes-textbook.css:570-573` sets
`.diagram-image { max-width: 100%; height: auto }`, inside a content column. A
2,350 px file is therefore being served for a slot roughly 700–900 px wide —
about 2.5–3× more pixels than a 2× retina screen needs.

**A resize needs no HTML edit.** The `width`/`height` attributes are set to the
intrinsic pixel dimensions on all 211 notes images, and browsers use them only
to compute the aspect ratio when CSS controls the width. Halving both dimensions
of a file **while preserving its exact aspect ratio** changes nothing about the
layout and requires no attribute change. If the ratio moves by even a rounding
step, the attributes must be updated in the same commit or CLS appears.

**78 of the 112 already have a hand-authored SVG twin.** `images/diagrams/svg/`
holds 83 SVGs built for the flashcards feature, each verified against its
ground-truth PNG per CLAUDE.md standing rule 4. 78 share a basename with a PNG:

```
those 78 as PNG : 18.2 MB        those 78 as SVG : 184 KB
<img> tags on notes pages pointing at a PNG that has an SVG twin : 231 of 295
```

That is a 99% reduction, already drawn and already checked — **but the SVGs were
authored to a different visual standard** (`docs/DIAGRAM_STYLE.md`) for a
different surface, so swapping them into the notes changes what a student sees.

**Why it matters.** The notes pages are the site's content and its traffic. They
are also the heaviest pages on the site by a factor of two, entirely because of
these files, and the excess is pure storage format rather than anything a reader
gets.

**Recommendation.** Two separate proposals; do not conflate them.

- **(a) Zero-visual-change, do this one.** Re-encode the 112 PNGs at ~1,600 px
  wide with a palette or lossy-alpha encoder, and add a WebP alongside behind
  `<picture>` (or serve WebP only — support is universal). Expect 26.2 MB → under
  3 MB and the mean notes page to drop ~450 KB. Verify by opening a sample of
  pages, per the repo's own method. **Not a content change:** the diagram is the
  same diagram.
- **(b) Adopt the 78 SVG twins.** Much larger win, and a **visible** change to
  the notes, so it needs explicit approval, a side-by-side review of all 78, and
  a decision about the 34 PNGs with no twin (a half-migrated gallery would look
  inconsistent). Log it, do not start it.

Note (a) is `src`-attribute work on up to 94 files, which is exactly the class of
change D18's template layer makes cheap. There is a real argument for sequencing
it after implementation rather than before.

**Effort:** M for (a), L for (b) · **Risk of acting:** Low for (a), Medium for
(b) — visual change to published content · **Risk of not acting:** Medium ·
**Dependencies:** (b) needs Eliot's approval under standing rule 1 ·
**Status:** OPEN

### PH08-035 — `seo/09-web-vitals-baseline.md` says CLS is 0.000 and there is no layout-shift problem; the repo's own later measurements say 0.253 and 0.110

**Severity:** High · **Category:** Performance / governance · **CERTAIN**

**Evidence.** `seo/09-web-vitals-baseline.md` states, in a section its own
"superseded in part" banner does **not** retract:

- line 104: *"**CLS is 0.000 on all six pages**, including the MathJax page.
  There is no layout-shift problem on this site at all."*
- line 223: *"CLS already 0.000"*
- line 253: *"**CLS: 0.000 on all six pages.** No layout-shift problem exists."*

Those numbers come from the 3-run measurement the banner already disowns for
LCP. The 7-run replacements are committed in the same repo:

| Page | `lh-baseline-live-7run.json` (`53a3e54`) | `lh-live-after-7run.json` (`8c8034b`) |
| --- | ---: | ---: |
| homepage | 0.020 | 0.021 |
| section-hub | 0.000 | 0.022 |
| **notes-topic** | **0.102** | **0.110** |
| practice-questions | 0.020 | 0.021 |
| **past-paper-questions** | **0.635** | **0.253** |
| flashcards | 0.000 | 0.020 |

Google's thresholds: ≤0.1 good, >0.25 poor. **Two families are over. The
past-paper-questions family sits at 2.5× the threshold**, and it is the lowest
Lighthouse performance score on the site (0.76 against 0.95–0.99).

The architecture pass **improved** ppq CLS from 0.635 to 0.253 — the work was
directionally right. It did not finish the job, and the document says the job
never existed.

**The mechanism on the ppq pages is identifiable from the source, and is
CERTAIN:**

1. `js/components/question-search.js:682` — `els.controls.hidden = false`. The
   filter panel ships with the `hidden` attribute set and is revealed by script.
2. Nothing in `css/pages/past-paper-questions.css` reserves height for it.
   `.ppq-controls` (line 57) has `padding: 1.2em 1.5em`, a border and a radius,
   and no `min-height`.
3. The reveal happens inside the `.then()` of
   `fetch("/past-paper-questions/questions.json")` — a **414 KB** payload
   (`past-paper-questions/questions.json`).
4. So a padded, bordered, multi-field panel appears after a 414 KB network round
   trip and pushes every result card down the page. That is the textbook CLS
   pattern, and 0.253 is what it measures.

**The notes-topic 0.110 has no identified cause and is marked UNKNOWN.** It is
stable across both runs (0.102 → 0.110), so it is pre-existing rather than a
regression. What would identify it is Lighthouse's `layout-shift-elements`
audit detail, which lives in the raw reports — deliberately not kept
(`8c8034b`, "Keep the post-deploy Lighthouse medians, not the 23 MB of raw
reports"). Re-running `seo/tools/run_lighthouse.py` and reading that one audit
answers it in minutes. **Do not guess at it; measure it.**

**Why it matters.** A document that says "no layout-shift problem exists" tells
the next person not to look. This audit only found it by reading the JSON beside
the document. CLS is a ranking signal, and the worst page here is the newest
feature.

**Recommendation.** Three things, in order:

1. **Correct the document.** Add the 7-run CLS table to
   `seo/09-web-vitals-baseline.md`'s superseding banner and strike the three
   "0.000 / no layout-shift problem" claims. This is a documentation edit outside
   `_audit/`, so it is a **proposal, not an action** under audit rule 1.
2. **Reserve the ppq controls' height.** A `min-height` on `.ppq-controls`
   matching its rendered height, or shipping the panel visible-but-disabled and
   enabling it on load. One rule in one generated stylesheet; affects 90 pages.
   This is the highest-value single CSS change identified in P8.
3. **Diagnose notes-topic** with one Lighthouse run before proposing anything.

**Effort:** S for (1) and (2), S to diagnose (3) · **Risk of acting:** Low ·
**Risk of not acting:** Medium-High — a Core Web Vital, on the newest feature,
believed fixed · **Dependencies:** none · **Status:** OPEN

### PH08-036 — Every page renders two `<h1>` elements; the first is "Economics Academy", on all 463

**Severity:** Medium · **Category:** Semantics / SEO · **CERTAIN**

**Evidence.** `templates/header.html:4` is
`<h1><a href="/">Economics Academy</a></h1>`. That template is injected into
`<div id="header-placeholder">` by `js/components/inject-templates.js:116-140`,
replacing the placeholder's `outerHTML`.

```
pages containing a header placeholder                      : 463 / 463
placeholder appears before the page's own <h1> in source   : 463 / 463
=> <h1> count in the rendered DOM                          : 2 on every page
```

The template's `<h1>` is therefore **always first** in the rendered document,
and every page's real `<h1>` is second.

**This extends Phase 6 rather than contradicting it.** `page_anatomy.py` §4
measured "exactly one `<h1>` on 463/463" over the **raw source**, which is
correct and is the right measure for a non-rendering crawler. It does not
include the injected header, because nothing static does. Googlebot renders
JavaScript, so it sees both. Screen readers see both.

**Why it matters.** Two effects, one modest and one worth fixing:

- Every page's document outline opens with the site name rather than the page
  topic. On 166 near-identical-by-board notes pages, whose `<h1>` P5 named as one
  of the few things differentiating a pair, the *first* heading is identical
  sitewide.
- A screen-reader user navigating by heading lands on "Economics Academy" on
  every page before reaching the page's own title.

**Recommendation.** Change `templates/header.html:4` to a `<p>` or a `<div>`
carrying the same class, or to a `<span>` inside the existing `<section
id="header">`. **One file, one line, affecting all 463 pages** — this is the
cheapest structural fix in the whole audit, precisely because the header is the
one thing already templated. Check `css/main.css` for `#header h1` selectors
first and update them in the same commit.

**Effort:** S · **Risk of acting:** Low — one file, styling to re-check ·
**Risk of not acting:** Low-Medium · **Dependencies:** none · **Status:** OPEN

### PH08-037 — No page has a `<footer>` or banner landmark; the injected footer is a `<section>` carrying 11 inline styles, and the nav's dropdown toggles are `<a href="#">`

**Severity:** Medium · **Category:** Accessibility · **CERTAIN**

**Evidence.** All three from the two runtime-injected templates, so all three
apply to **463 of 463 pages**.

1. **`templates/footer.html:1` is `<section id="footer" style="…">`, not
   `<footer>`.** There is no `<footer>` element anywhere on the site.
   `templates/header.html:3` is `<section id="header">`, so there is no banner
   landmark either. Together with PH06-032 (462 pages with no `<main>`), that
   means **all three principal landmarks are absent sitewide**. P6 found one of
   the three because it only looked at page source; the other two are in the
   templates.
2. **`templates/footer.html` carries 11 inline `style=` attributes** — the
   `<section>` itself, the link lists, the copyright line. The house rule in
   CLAUDE.md is "No inline `style` attributes — extract a class." Neither
   PH00-008 nor Q20 item 6 counted this file; both counted pages only. It is one
   file and it reaches every page.
3. **The four nav dropdown parents are `<a href="#" role="button">` with no
   `aria-expanded`** (`templates/header.html`, 4 occurrences of each).
   `role="button"` tells assistive technology it is a button, but `href="#"`
   means Space does not activate it and a click jumps to the top of the page,
   and with no `aria-expanded` there is no announcement of open or closed state.
   The site's own house rule for expand/collapse is "a `<button>` with
   `aria-expanded` and `aria-controls`" — the rule exists and the nav predates it.

**Why it matters.** Item 1 is the cheapest accessibility win available after
PH06-032 and is in a **single file** rather than 462. Item 3 is the site's
primary navigation, on every page, for keyboard and screen-reader users.

**Recommendation.** All three are `templates/` edits, so each is one file:

- `<section id="footer">` → `<footer id="footer">`; `<section id="header">` →
  `<header id="header">`. Keep the `id` and every class — check `css/main.css`
  for `section#header` / `section#footer` selectors first, exactly as PH06-032
  requires for `#main`.
- Move the 11 inline styles into `css/main.css` under `#footer`.
- Give the four dropdown parents `aria-expanded`, maintained by
  `jquery.dropotron` or by `inject-templates.js`'s `initNavigation`. Changing
  them from `<a href="#">` to `<button>` is the correct fix but is a larger
  change to a third-party plugin's expected markup; propose it, do not assume it.

**Effort:** S for the landmarks and inline styles, M for the nav ·
**Risk of acting:** Low-Medium — the templates are on every page, so a mistake
is sitewide; verify by opening pages in Live Server ·
**Risk of not acting:** Medium · **Dependencies:** none · **Status:** OPEN

### PH08-038 — The scoping convention is followed by the generated stylesheets and almost nowhere else: 6 of 19 sheets fully scoped, 392 of 955 selectors bare

**Severity:** Medium · **Category:** CSS architecture · **CERTAIN**

**Evidence.** For each `css/pages/*.css`, the count of selectors nested under a
single leading wrapper class:

| Sheet | Selectors | Under one wrapper | |
| --- | ---: | ---: | --- |
| `flashcards.css` | 121 | **121 / 121** | `.flashcards-page` |
| `glossary.css` | 104 | **104 / 104** | `.glossary-page` |
| `quiz.css` | 92 | **92 / 92** | `.quiz-page` |
| `past-paper-questions.css` | 55 | **55 / 55** | `.past-paper-questions-page` |
| `practice-questions.css` | 49 | **49 / 49** | `.practice-questions-page` |
| `privacy.css` | 8 | **8 / 8** | `.privacy-notice` |
| `revision-notes-textbook.css` | 132 | 120 / 132 | `.revision-notes-content` |
| `macro-application.css` | 35 | 21 / 35 | `.revision-notes-content` |
| `tutoring.css` | 56 | 5 / 56 | — |
| `contact.css` | 55 | 7 / 55 | — |
| `faq.css` | 54 | 16 / 54 | — |
| `past-papers-list.css` | 46 | 6 / 46 | — |
| `home.css` | 44 | 4 / 44 | — |
| `marking.css` | 31 | 4 / 31 | — |
| `revision-notes-topics.css` | 21 | 4 / 21 | — |
| `revision-notes.css` | 15 | 3 / 15 | — |
| `confirmation.css` | 13 | 2 / 13 | — |
| `past-papers.css` | 13 | 2 / 13 | — |
| `about.css` | 11 | 3 / 11 | — |

**Five of the six fully-scoped sheets belong to a generated page family.** The
sixth, `privacy.css`, is hand-written, eight selectors long, and uses
`.privacy-notice` rather than the wrapper on `section#main`. This is the same
pattern P6 found for breadcrumb `aria-label` and P8 finds again in PH08-039 and
PH08-041: **a convention gets adopted, and only the pages behind a generator
receive it.**

**The collision the rule prevents is not the collision that exists.** Only one
page loads two page sheets (§1.1), so two page stylesheets cannot fight. What
they can and do fight with is `css/main.css` — 209 class names, loaded on all
463 pages, ahead of every page sheet:

```
(sheet, class) pairs where a css/pages sheet redefines a class main.css defines : 50
across 15 of the 19 sheets
```

`contact.css` alone redefines 12 of main.css's classes (`.box`, `.row`,
`.col-4`, `.col-6`, `.col-8`, `.col-12`, `.button`, `.actions`, `.major`, `.alt`,
`.gtr-uniform`, `.contact-icon`), all bare, all at equal specificity. They win
only because the page sheet loads second. `tutoring.css` redefines 6 the same
way. The five generated sheets have the same overlap on paper (`.breadcrumb`,
`.major`, `.separator`, `.button`) and are immune, because
`.quiz-page .breadcrumb` outranks `.breadcrumb` on specificity rather than on
load order.

**`revision-notes-textbook.css` is the one that matters most.** It loads on 169
pages — more than any other page sheet — and **11 of its 132 selectors are
bare**: nine `.diagram-figure` / `.diagram-image` / `.diagram-caption` rules
across three breakpoints, plus `.breadcrumb` and `.breadcrumb .separator`. Those
last two directly override `css/main.css:3178`. (A twelfth non-wrapper selector,
`:root`, is the site's colour-token block, which CLAUDE.md places in this file
deliberately. It is correct and is not counted as a violation.)

**Why it matters.** Nothing is broken today. The rule is a rule because load
order is a fragile way to win an argument: reorder two `<link>` tags, or add a
second page sheet to a page, and the cascade flips silently. CLAUDE.md already
records that this has happened once.

**Recommendation.** Scope the 12 bare selectors in
`revision-notes-textbook.css` under `.revision-notes-content` first — highest
page count, smallest edit, and it is where a future second stylesheet is most
likely to land. Then `contact.css` and `tutoring.css`, whose overlap with
`main.css` is largest. The eight single-page root sheets are the lowest priority:
a stylesheet loaded by exactly one page cannot collide with another page's.

Do this **as CSS-only commits**, verified by opening each page — no HTML changes
are needed, because every one of these pages already has a wrapper class on its
`section#main`.

**Effort:** M · **Risk of acting:** Low-Medium — a mis-scoped selector silently
stops applying; check visually · **Risk of not acting:** Low today, Medium once
a template layer starts reordering `<head>` contents ·
**Dependencies:** none, but cheaper alongside D18's migration · **Status:** OPEN

### PH08-039 — 126 pages load MathJax with three different configurations, and one page has a live rendering hazard from the `$…$` delimiter

**Severity:** Medium · **Category:** Consistency / correctness · **CERTAIN**

**Evidence.** 126 of the 166 notes topic pages load MathJax 3 from jsDelivr.
Across them:

| Config block | Pages | Contains |
| --- | ---: | --- |
| full, with explanatory comments | 89 | `processEscapes`, `autoload.ams`, `skipHtmlTags` |
| full, comments stripped | 18 | same three |
| **minimal** | **19** | **none of the three** |

and two script tags:

```
98 pages   id="MathJax-script" async src="…/tex-mml-chtml.js"
28 pages   src="…/tex-mml-chtml.js" async
```

PH06-031 recorded the 28/98 script-tag split. The three **config** objects are
new here, and they are the more consequential half: the 19 minimal pages omit
`skipHtmlTags` (so MathJax will process the contents of `<pre>`, `<code>`,
`<textarea>`), `processEscapes` (so `\_` and `\$` in prose are not escaped) and
`autoload: { ams: ["boldsymbol"] }` (so `\boldsymbol` does not render).

**Checked, and none of those 19 is currently affected:** 0 of the 19 contain a
`<code>`, `<pre>` or `<textarea>` element or a `\boldsymbol` in the body. The
divergence is latent, not live.

**One live hazard does exist, and it is on a different page.** All three configs
enable `$` as an inline-maths delimiter:

```js
inlineMath: [ ["$", "$"], ["\\(", "\\)"] ]
```

CLAUDE.md documents `\( … \)` as the site's maths delimiter and never mentions
`$…$`. Scanning the body of every MathJax page for a literal `$`:

```
revision-notes/aqa-a2-macro/2-1-4-uses-of-national-income-data.html   7
revision-notes/aqa-a2-micro/1-7-2-the-problem-of-poverty.html         1
all other 124 MathJax pages                                           0
```

The first is a purchasing-power-parity worked example, lines 500–523, and line
515 is a single table cell reading:

```html
<td>₹6,000 ÷ $120 = <strong>₹50 = $1</strong></td>
```

**Two `$` inside one cell, with only inline markup between them.** MathJax's
TeX input scans a container's text across inline elements, so it will pair those
two delimiters and typeset `120 = ₹50 = ` as mathematics. The second page has a
single, unpaired `$` and is safe.

**What is CERTAIN and what is not.** That the configuration enables `$…$` and
that the page contains an even number of `$` inside one element: certain, from
the files. The exact visual result: **not verified — this audit does not render
pages.** Open
`revision-notes/aqa-a2-macro/2-1-4-uses-of-national-income-data.html` in Live
Server and look at the PPP table. That is a two-minute check and it settles it.

**Why it matters.** Small, specific, and the sort of thing that stays broken for
years because no verifier looks for it. It is also the only *live* rendering
defect P8 found.

**Recommendation.**

1. **Remove `["$", "$"]` from `inlineMath` on all 126 pages.** No page on the
   site uses `$…$` as a maths delimiter — the only 8 literal `$` characters are
   currency. This is a `<head>` change, not a prose change, so it does not touch
   economics content. It permanently removes the hazard for every future page
   that mentions a dollar figure.
2. **Then** converge the three configs and two script tags to one. This is
   exactly the "one asset, N markups" problem D18's `page_shell.py` exists to
   end; it should be one of the first things the shell owns.
3. Re-check the PPP table in a browser either way.

**Effort:** S · **Risk of acting:** Low — `<head>` only ·
**Risk of not acting:** Low-Medium; one page probably renders wrongly today ·
**Dependencies:** none · **Status:** OPEN

### PH08-040 — Three stylesheets remove the focus outline and replace it with a colour change only, on 92 pages

**Severity:** Medium · **Category:** Accessibility · **CERTAIN**

**Evidence.** Five `outline: none` / `outline: 0` declarations exist in the
site's CSS. One (`css/main.css:1861`, `.image { outline: 0 }`) is not a focus
rule. Of the remaining four:

| Location | Rule | Replacement cue | Pages |
| --- | --- | --- | ---: |
| `css/pages/past-paper-questions.css:79-82` | `.ppq-search-input:focus` | `box-shadow: 0 0 0 3px rgba(213,35,73,.15)` — **a real ring** | 90 |
| `css/pages/past-paper-questions.css:121-124` | `.ppq-field select:focus` | `border-color` only | **90** |
| `css/pages/faq.css:59-62` | `.faq-search-input:focus` | `border-color` only | 1 |
| `css/pages/contact.css:181-185` | `input/select/textarea:focus` | `border-color` only | 1 |

The first is fine — a 3 px shadow is a legitimate substitute for the browser
outline. **The other three replace a shape cue with a colour cue.** A keyboard
user on the past-paper-questions filter selects, the FAQ search box or the
contact form gets no non-colour indication of where focus is. That fails WCAG
2.2 SC 1.4.11 (Non-text Contrast) and SC 2.4.11 (Focus Appearance), and it fails
completely for anyone who cannot distinguish `#d52349` from the resting border.

The site does otherwise know how to do this: **14 `:focus-visible` rules** exist
across `main.css` (7) and six page sheets. The three offenders are simply older
than the convention.

**Why it matters.** 90 of the 92 pages are the newest feature on the site, and
its search-and-filter UI is the one place a keyboard user must tab through
several controls in sequence.

**Recommendation.** Add the same `box-shadow` ring already used 3 lines above it
in `past-paper-questions.css` to the other three rules. Three CSS edits, no
markup change, no page regenerated. Test by tabbing through
`/past-paper-questions/`, `/faq.html` and `/contact.html`.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Medium — a
real barrier for real users · **Dependencies:** none · **Status:** OPEN

### PH08-041 — The font setup has four separate defects, all sitewide

**Severity:** Medium · **Category:** Assets / robustness · **CERTAIN**

**Evidence.** All 463 pages request one Google Fonts stylesheet:

```
https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;1,400
  &family=Open+Sans:wght@400;600;700
  &family=Source+Sans+Pro:ital,wght@0,300;0,400;0,700;0,900;1,300&display=swap
```

Three families, twelve faces. It is the **largest render-blocking item on 6 of 6
sampled pages, at 813–835 ms** (`seo/lh-live-after-7run.json`) — a figure
`seo/09-web-vitals-baseline.md` itself names as surviving its supersession.

1. **The base font declaration has no generic fallback.**
   `css/main.css:249` is `font-family: "Source Sans Pro";` with nothing after it.
   If that request fails — blocked network, Google Fonts unreachable, an ad
   blocker — the browser falls back to its **default** font, which is a serif on
   most desktop browsers, not a sans-serif. One word (`, sans-serif`) fixes it.
2. **A weight is requested in CSS that is never fetched for that family.**
   Source Sans Pro is fetched at 300, 400, 700 and 900 — **not 600**.
   `font-weight: 600` appears **24 times** across the site's stylesheets, and at
   `css/pages/past-paper-questions.css:111-115` and `:130-134` the family and the
   weight sit in the same rule: Source Sans Pro at 600, which was never
   downloaded. The browser synthesises a faux-bold or substitutes 700. Open Sans
   *is* fetched at 600, so the one rule that pairs them
   (`revision-notes-textbook.css:880-884`, `.notes-cta p`) is correct; the rest
   need checking one by one, which needs a browser and is not done here.
3. **Metric-adjusted fallback fonts exist on one family only.**
   `css/pages/quiz.css:14-24` declares `"Merriweather Fallback"` and
   `"Source Sans Pro Fallback"` using `src: local(...)` and `size-adjust`, with a
   comment explaining exactly why. It is careful, deliberate CLS work — and it is
   loaded on **173 pages of 463**. The other 290, including all 166 notes topic
   pages, get nothing. Same drift pattern as PH08-039 and PH06-030.
4. **No `preload` anywhere, and no `preconnect` for the MathJax CDN.** There are
   `preconnect` hints for `fonts.googleapis.com` and `fonts.gstatic.com` on all
   463 pages, which is right. But **126 pages fetch MathJax from
   `cdn.jsdelivr.net` with no `preconnect` to that host** — a fourth origin, on
   the content pages, unhinted. Separately, **no third-party script on the site
   carries an `integrity` attribute**: 463 gtag, 126 MathJax, 1 Calendly.

**Why it matters.** (1) is a one-word robustness fix. (2) makes text render
slightly wrong in a way nobody will ever trace. (3) is good work that never
propagated and is directly relevant to the notes-topic CLS of 0.110 in PH08-035
— an unmatched fallback metric is one of the standard causes. (4) SRI on a CDN
script is the difference between "jsDelivr had a bad day" and "jsDelivr served
arbitrary JavaScript to every notes page".

**Recommendation.**

- Add `, sans-serif` at `css/main.css:249`. Do it first; it costs nothing.
- Either add `600` to the Source Sans Pro request or change the 17 rules to 700.
  Adding the weight is one URL edit but lands on 463 pages' `<head>`; changing
  the CSS is 3 files. **Prefer the CSS change** — it does not add a font face.
- Move the `size-adjust` fallback declarations out of `quiz.css` into
  `css/main.css` so all 463 pages get them, and **measure notes-topic CLS before
  and after** — it may close PH08-035's second half on its own.
- Add `<link rel="preconnect" href="https://cdn.jsdelivr.net">` to the 126
  MathJax pages, and `integrity` + `crossorigin` to the MathJax tag. Both are
  `<head>` changes and both are natural jobs for `page_shell.py`.

**Effort:** S each · **Risk of acting:** Low; the `size-adjust` move needs a
visual check on a serif-heavy page · **Risk of not acting:** Low-Medium ·
**Dependencies:** none · **Status:** OPEN

### PH08-042 — Inline styles and `<style>` blocks re-measured: 1,187 of the 1,520 must never be touched, and the approved fix list is missing 4 files

**Severity:** Low-Medium · **Category:** Markup consistency · **CERTAIN**

**Evidence.** PH00-008 counted pages; Q20 item 6 approved fixing "44 hand-written
pages". Counting **attributes**, and classifying each by whether it sits inside a
`<span class="katex…">` subtree:

```
inline style= attributes, all published HTML : 1,520
  inside a KaTeX subtree                     : 1,187   (78%)
  authored                                   :   333
pages carrying >=1 authored inline style     :    45
```

| Family | Pages | Authored attributes |
| --- | ---: | ---: |
| past-papers | 5 | **161** |
| notes-topic | 26 | 96 |
| root | 6 | 35 |
| notes-hub | 6 | 24 |
| **templates** | **1** | **11** |
| notes-other | 1 | 6 |
| glossary, flashcards, mcq, ppq | 0 | **0** |

Two corrections to the approved list follow:

1. **The 1,187 KaTeX styles are build output and must not be "fixed".** They are
   `top:`, `height:`, `margin-right:` and `vertical-align:` offsets that KaTeX
   emits to position glyphs. Removing or externalising any of them breaks formula
   rendering on the glossary and flashcards pages. Once they are excluded, **no
   generated page carries an authored inline style at all** — Q20's "7 generated"
   were all KaTeX.
2. **`templates/footer.html` is a 45th file**, not counted by PH00-008, Q20 or
   P6, and it reaches all 463 pages. It is also PH08-037 item 2.

**`<style>` blocks: there are 9, not 1, and 6 of them are load-bearing.**

| Pages | Where | Verdict |
| ---: | --- | --- |
| 6 | `practice-questions/*/index.html` | **Keep.** Inside `<noscript>`, at offset 4,654 against the `<noscript>` at 4,356, with a comment explaining that the accordion collapses in CSS and `quiz.js` reopens it, so with scripting off the topic links would be unreachable. Deliberate progressive enhancement, generated. |
| 1 | `revision-notes/aqa-a2-micro/1-5-1-market-structures.html` | Violation. 30 lines. Named in Q20 item 5. |
| 2 | `revision-notes/{macro,micro}economics-diagrams.html` | **Violation, not previously named.** ~3.5 KB each, scoped `.macro-diagrams-page` / `.micro-diagrams-page` rules — a full page stylesheet living in the `<head>`. These two pages load `revision-notes-textbook.css` and have no page sheet of their own. |

**Recommendation.** Amend the D18/Q20 item 5–6 scope to read: 333 authored
attributes across 45 files including `templates/footer.html`; three `<style>`
blocks, of which the two diagram-gallery ones become a new
`css/pages/revision-notes-diagrams.css`; and an explicit **do not touch** on
KaTeX output and on the six `<noscript>` blocks. This does not reopen the
approval — it corrects the target list so the approved work hits the right files.

**Effort:** S to amend, M to execute · **Risk of acting:** Low ·
**Risk of not acting:** Low, but the approved work would miss 4 files and could
break 2 pages · **Dependencies:** D18 · **Status:** OPEN

### PH08-043 — jQuery and dropotron are 175 KB serving the injected navigation and nothing else; none of the five modern components use them

**Severity:** Medium · **Category:** Assets / architecture · **CERTAIN**

**Evidence.** Every page loads a fixed seven-script tail. `jquery.min.js` is
**164.1 KB on disk, ~41.7 KB over the wire**, and Lighthouse attributes
**325–500 ms of render-blocking time** to it on 6 of 6 sampled pages — the
second-largest blocking item everywhere. `jquery.dropotron.min.js` adds 10.7 KB.

Who actually uses it:

| File | `$(` calls | Verdict |
| --- | ---: | --- |
| `js/util.js` | 22 | HTML5 UP template helpers |
| `js/components/inject-templates.js` | 11 | the header/footer injection |
| `js/main.js` | 2 | template bootstrap |
| `js/jquery.dropotron.min.js` | — | the nav dropdown plugin |
| `js/components/quiz.js` | **0** | |
| `js/components/flashcards.js` | **0** | |
| `js/components/glossary-filter.js` | **0** | |
| `js/components/question-search.js` | **0** | |
| `js/components/reviews-render.js` | **0** | |

**All five components written for this site are vanilla JavaScript.** jQuery
exists for the inherited HTML5 UP theme and the dropdown navigation.

`inject-templates.js` uses jQuery for a `$(function(){})` ready handler and DOM
queries — both have one-line native equivalents. The genuine dependency is
`dropotron`, which is a jQuery plugin, and `util.js`, which is theme code.

**Why it matters.** 175 KB of source and ~52 KB of wire, on every page, at the
front of the critical path, to open a navigation menu. It is also the reason
`inject-templates.js` cannot run before jQuery has parsed — which is what makes
the header injection block rendering at all.

**Recommendation.** **Do not act on this in isolation, and do not act on it
before P11.** It is the largest performance item on the site and the one with
the most ways to go wrong: removing jQuery means replacing `dropotron` with a
hand-written dropdown, rewriting `util.js`'s consumers, and re-testing navigation
on 463 pages and every breakpoint.

What P8 recommends is narrower: **record the measurement and sequence the
decision into P11**, alongside D18's migration Phase 7 (baking the header/footer
at build time), which is already gated on P3. If the header and footer stop being
fetched at runtime, `inject-templates.js` disappears and one of jQuery's three
consumers goes with it — at which point this is a much smaller job. Doing it
before then means doing it twice.

**Effort:** L · **Risk of acting:** **High** — sitewide navigation ·
**Risk of not acting:** Medium, ongoing · **Dependencies:** P3, and D18
migration Phase 7 · **Status:** OPEN, deferred to P11 by recommendation

### PH08-044 — 43 published image files, 5.4 MB, are referenced by nothing

**Severity:** Low · **Category:** Published surface · **CERTAIN**

**Evidence.** 239 published image files, 31.5 MB. Cross-referencing every
published `.html`, `.css`, `.js`, `.json`, `.xml` and `site.webmanifest`,
normalising absolute `https://economicsacademy.co.uk/…` forms and CSS-relative
`../` forms:

```
referenced by nothing: 43 files, 5,380 KB
```

| Group | Files | Bytes | Status |
| --- | ---: | ---: | --- |
| `old-logos-archive/**` | 22 | 1,958 KB | PH01, already logged |
| `logo/**` | 8 | 447 KB | PH01-013, **UNDECIDED** per D13 |
| `images/diagrams/*.png` (10 unreferenced) | 10 | 2,969 KB | PH01, already logged |
| `favicon-16x16.png`, `-32x32.png`, `-48x48.png` | 3 | 4 KB | **new** |

The three favicon PNGs are new: `index.html` links `/favicon.ico`,
`/apple-touch-icon.png` and `/site.webmanifest`, and the manifest names
`/android-chrome-192x192.png` and `/android-chrome-512x512.png`. All five of
those exist and are referenced. The three sized PNGs are left over from an
earlier favicon block. All eight root icon files were verified present on disk
and tracked.

**Why it matters.** Marginal — unreferenced files cost nothing to serve. It is
listed because the repo is public and everything here is a live URL, and because
`old-logos-archive/` at 1.96 MB is 6% of the site's image weight for zero use.

**Recommendation.** Fold into P1's existing published-surface decision rather
than treating as new. `logo/` stays UNDECIDED per D13. The three favicon PNGs
are safe to remove or safe to leave; note them and move on.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low ·
**Dependencies:** none · **Status:** OPEN

### PH08-045 — 19 pages emit `BreadcrumbList` structured data with no breadcrumb visible on the page

**Severity:** Low-Medium · **Category:** Structured data · **CERTAIN**

**Evidence.** Pages containing a `BreadcrumbList` JSON-LD block and no element
with `class="breadcrumb…"`:

```
19 pages: root 6, notes-hub 6, past-papers 5, notes-other 1, mcq-hub 1
```

Named: `about.html`, `contact.html`, `faq.html`, `marking.html`, `privacy.html`,
`tutoring.html`; all five `past-papers/*` hubs; all six `revision-notes/*/`
hubs plus `revision-notes/index.html`; `practice-questions/index.html`.

**Why it matters.** Google's structured-data guidance is that markup should
describe content visible on the page. A breadcrumb trail declared only in JSON-LD
is a mismatch, and it is also a navigation gap in its own right — these 19 are
hub and commercial pages, and a user on `past-papers/ocr/` has no trail back.

**Recommendation.** Hand to **P4**, which is the structured-data phase and is
already carrying Q11 (the `EducationalOrganization` gap on the same kind of
page). The choice is add the visible trail or drop the markup, and it should be
made once for both questions together. Do not decide it here.

**Effort:** S–M · **Risk of acting:** Low · **Risk of not acting:** Low ·
**Dependencies:** P4 · **Status:** OPEN, handed to P4

### PH08-046 — Each of the 90 past-paper-question pages downloads the entire 414 KB question index to display its own ~28 questions

**Severity:** Medium · **Category:** Assets / architecture · **CERTAIN**

**Evidence.** `past-paper-questions/questions.json` is **414 KB**.
`js/components/question-search.js` boot (line ~688) fetches
`data-src` or the default `/past-paper-questions/questions.json` on every page
carrying `[data-question-search]` — the master page and all 90 topic pages. The
sampled topic page (`edexcel/1-2-3-price-income-cross-elasticities-of-demand/`)
ships **14** `.ppq-card` blocks in its static HTML.

This is also the fetch that gates the controls reveal in PH08-035, so it is
directly implicated in the 0.253 CLS.

By comparison the flashcards feature already solved this: `flashcards/data/` is
**six per-deck payloads of 97–238 KB**, each page fetching only its own.

**Why it matters.** 414 KB is roughly the entire weight of the homepage,
downloaded on each of 90 pages to filter it down to the dozen-or-so records
already present in that page's HTML. It is the largest single runtime payload on
the site.

**Recommendation.** Emit a per-topic payload from
`scripts/build_past_paper_questions.py` — the generator already knows the split,
and `flashcards/data/*.json` is the pattern to copy — with the master page
continuing to load the full index. Keep `questions.json` published at its current
path either way: `DO-NOT-BREAK.md` records it as fetched at runtime, and the
master page needs it.

Combined with PH08-035's `min-height`, this closes the ppq CLS from both ends.

**Effort:** M · **Risk of acting:** Low-Medium — regenerated output, verify with
`node scripts/test_question_search.js` · **Risk of not acting:** Medium ·
**Dependencies:** none · **Status:** OPEN

---

## 3. What Phase 8 checked and found clean, so nobody re-audits it

- **Zero unreferenced stylesheets. Zero unreferenced JavaScript files.** All 22
  published CSS and all 13 published JS files are loaded by at least one page.
- **Zero `href`/`src` values that do not resolve to a file** — stylesheets,
  scripts and `url()` references in CSS all resolve. Confirms P1's case-sensitivity
  result from a different direction.
- **GA4 is perfectly consistent.** One measurement ID, `G-YVCNRW4QH6`, on
  **463 of 463** pages, with exactly **one** distinct `gtag` init snippet. No page
  is missing it and no second property exists. This is the `DO-NOT-BREAK.md`
  assertion, re-verified.
- **Zero dangling `aria-controls`.** Every `aria-controls` value names an `id`
  present in the same page.
- **Zero duplicate `id` attributes within a page**, across all 465 files.
- **Zero non-descriptive link texts** — no "click here", "read more", "here" or
  empty anchors anywhere.
- **Zero `target="_blank"` without `rel="noopener"`.**
- **The skip link resolves on 463 of 463 pages.** `templates/header.html:2` is
  `<a href="#main" class="skip-to-content">` and every page has an `id="main"`.
- **No `<button>` lacking `type=` sits inside a `<form>`.** 62 buttons omit
  `type`, all outside forms, so none can accidentally submit.
- **Only four third-party origins are contacted:** googletagmanager (463 pages),
  fonts.googleapis + fonts.gstatic (463), cdn.jsdelivr (126), assets.calendly (1).
  No tracker, tag manager or widget beyond those.
- **`prefers-reduced-motion` is respected** — 4 rules present.
- **Zero pages use `\( … \)` maths without loading MathJax.**
- **The three root images missing `width`/`height`** are already PH00/P6's; P8
  confirms the count is 3 and that no other image on the site lacks them.

---

## 4. Handed to later phases

| Item | To | Why |
| --- | --- | --- |
| PH08-045, breadcrumb markup vs visible trail on 19 pages | **P4** | Structured-data validity is P4's subject and Q11 is the same kind of question about the same kind of page. Decide both together. |
| **Print styles** | **P7** | Only 5 `@media print` blocks exist, in 3 stylesheets — `revision-notes-textbook.css` (3), `glossary.css` (1), `flashcards.css` (1). The 166 practice-question pages, 90 past-paper-question pages, 5 past-paper hubs and 9 root pages have none. Students print revision material; whether that matters is a UX judgement, and `AUDIT-PLAN.md` puts print styles in P7. Measured here, judged there. |
| PH08-043, removing jQuery | **P11** | Gated on P3 and on D18's migration Phase 7. |
| PH08-034(b), adopting the 78 SVG diagram twins | **P11**, with Eliot's approval | Visible change to published content. |

**Colour contrast was not measured.** It needs a rendering engine to resolve
computed colours against computed backgrounds, and this audit does not render.
Marked **UNKNOWN**, not clean. `seo/tools/run_lighthouse.py` already runs
Lighthouse, whose accessibility category includes a contrast audit — one run
against six sampled pages would answer it, and that is the recommended method.

---

## 5. Decision brief

### What was measured

Nine censuses over 465 published HTML files, 22 stylesheets, 13 scripts, 239
images and 32 font files, plus the two Lighthouse 7-run median files already in
the repo. New script: `docs/audit/scripts/asset_census.py`, read-only, stdlib-only,
sections runnable individually.

### The three things that matter

1. **CLS is not zero, and the document that says it is has not been corrected.**
   past-paper-questions 0.253, notes-topic 0.110, against a 0.1 threshold. The
   mechanism on the ppq pages is identified and is a `min-height` away from being
   fixed. PH08-035, and PH08-046 beside it.
2. **Three of the four largest render-blocking resources on every page are
   fixable without touching a single line of prose.** FontAwesome ships 1,458
   icons to use 20 (PH08-033); jQuery serves a dropdown menu (PH08-043); the font
   request has no fallback and asks for a weight it does not fetch (PH08-041).
3. **The notes pages carry 513 KB of images each because 112 line diagrams are
   stored as 2,350 px RGBA PNGs.** A re-encode is invisible to the reader and
   removes ~450 KB a page. PH08-034.

### The pattern, stated once

Every consistency finding in this phase has the same shape as P6's: **a good
convention exists, and only the pages behind a generator received it.**

| Convention | Has it | Does not |
| --- | --- | --- |
| Wrapper-class scoping | 5 generated sheets + `privacy.css` | 13 hand-written sheets |
| `size-adjust` fallback font metrics | `quiz.css`, 173 pages | 290 pages |
| `decoding` on images | the 2 diagram galleries, 89 images | 220 images |
| `aria-label` on breadcrumbs (P6) | 100 generated pages | 341 |
| `<noscript>` fallback | 15 generated pages | 448 |
| One MathJax config | — | 3 configs, 2 script tags, 126 pages |

This is the case for D18 restated in a different register, and it is why P8
recommends **no new sitewide hand-edits before the shell module exists**, except
where a fix lives in one file: a stylesheet, a template, or a generator.

### If you only do four things

In this order, on evidence of value per unit of risk:

1. `min-height` on `.ppq-controls` — one CSS rule, closes a 0.253 CLS on 90 pages.
2. `font-display: swap` on FontAwesome's three `@font-face` rules, and
   `, sans-serif` at `css/main.css:249` — four lines, zero risk.
3. The three `outline: none` focus rules get the box-shadow ring that already
   exists three lines above one of them — three lines, real accessibility gain.
4. `templates/header.html:4` `<h1>` → `<p>`, and `<section id="footer">` →
   `<footer>` — two lines, two files, corrects every page on the site.

All four are single-file edits. None touches prose. None changes a URL.

### The honest case against acting on any of this yet

D20 says the audit finishes first, and that still holds. Nothing in P8 is
degrading: no measurement here gets worse by waiting, and P11 will be able to
sequence these against P3's link-equity ruling and P10's automation proposal,
which is a better decision than taking them in the order they were found.

The one exception worth naming is **PH08-039's `$…$` hazard**, because one page
may be rendering incorrectly on the live site today. That is a two-minute browser
check, and if it confirms, it is a `<head>` edit on one page — not a programme of
work.

### Questions

Four, all with recommended defaults, in `OPEN-QUESTIONS.md` as **Q22–Q25**.

---

## Addendum, 2026-08-09 — Q23 answered, and what visual inspection found

Eliot answered Q23 by **overriding the recommended default**: adopt the 78 SVG
twins, permission granted in this instance. Standing rule 4 in CLAUDE.md
requires every diagram to be *visually inspected, never trusted by filename*
before being presented for approval, so the first step was inspection rather
than a `src` rewrite. **It stopped the swap.** This addendum records why, and
logs it as PH08-047.

### PH08-047 — The 78 SVG "twins" are not all the same diagram; at least one silently drops a panel of economics content

**Severity:** High · **Category:** Content integrity · **CERTAIN**

**Method.** Each SVG rendered headlessly (`Google Chrome --headless
--screenshot`, 1200×900, white background) and compared against its PNG side by
side. Four pairs inspected, chosen to span the aspect-ratio range.

**Result 1 — every SVG is 4:3; almost no PNG is.** Comparing `viewBox` against
the PNG's IHDR dimensions across all 78 pairs:

```
aspect ratio agrees within 2% :  2 of 78
differs by more than 2%       : 76 of 78
every SVG viewBox             : 4:3 (1.333)
PNG aspect ratios             : 1.30 – 3.37, median ~1.5
```

The SVGs were drawn to a fixed flashcard canvas. They are recompositions, not
re-encodings.

**Result 2 — and that recomposition sometimes removed content.**

| Pair | PNG AR | Verdict |
| --- | ---: | --- |
| `laffer-curve` | 1.631 | **Faithful.** Same axes, same R1/R2/t1/t2 labels, same curve, same "Laffer curve" annotation. Style differs (blue/thin vs black/thick-dashed); economics identical. |
| `supply-of-labour-market-individual` | 2.446 | **Faithful.** Both the Market and Individual panels present, W1/W2/Q1/Q2 on both. One small regression: the x-axis reads "Quantity" where the PNG reads "Quantity of Labour". |
| `perfect-competition-short-run-supernormal-profit` | 2.766 | **NOT EQUIVALENT.** The PNG is a **two-panel** figure — market (S and D crossing at P1/Q1) on the left, firm (D=AR=MR=P1, MC=S, AC, shaded profit) on the right. **The SVG contains only the firm panel.** The entire market panel is absent. |
| `ppf-basic` | 1.975 | rendered, not needed once the above was established |

**Result 3 — aspect ratio does not predict which.** A pair at **2.446** is
faithful and a pair at **2.766** is not. There is no mechanical screen. Every one
of the 78 needs eyes on it, which is exactly what standing rule 4 says and
exactly why it exists.

**Result 4 — the swap would leave the notes in two visual styles for a long
time.** Of the 95 notes pages carrying a diagram PNG:

```
every diagram on the page has an SVG twin : 65
MIXED — some twinned, some not            : 20
no diagram twinned                        : 10
distinct diagrams with no SVG twin        : 28
```

The two diagram galleries are the worst affected — `microeconomics-diagrams.html`
would show 12 black PNGs among the blue SVGs, `macroeconomics-diagrams.html` 6.

**Why it matters.** Adopting the SVGs is **not a format change. It is a visual
restyle of the notes' diagrams, applied to 70% of them, on a set that includes at
least one drawing whose content differs from the figure it would replace.**
Swapping `perfect-competition-short-run-supernormal-profit` alone would delete
the market panel from `1-5-3-perfect-competition.html`, `3-4-2-perfect-competition.html`
and the microeconomics gallery — and CLAUDE.md's first hard constraint is that
economics content is never altered without an explicit instruction. An
instruction to swap image formats is not an instruction to remove a panel.

**Recommendation.** The adoption is worth doing and should not be abandoned. It
should be sequenced as content work, not asset work:

1. **Verify all 78 pairs individually**, PNG against SVG against the notes'
   own `<figcaption>` — a caption that says "the market and the firm" against an
   SVG showing only the firm is the failure this catches. Record each as
   faithful / subset / regressed-label in a table.
2. **Draw the 28 missing diagrams** to the same style guide, so the notes convert
   in one step rather than living in two styles for months.
3. **Then swap**, per board directory, updating every `<img>`'s `width`/`height`
   to the SVG's `viewBox` in the same commit — 231 tags across 94 pages — because
   the aspect ratio changes on 76 of 78 and stale attributes would introduce the
   very layout shift PH08-035 is about.

**This supersedes PH08-034(b) as written.** That finding described the 78 as
"already drawn and already checked", which was true of their flashcard use and is
not sufficient for this one. The correction is recorded rather than edited in
place, per the audit's own append-only convention.

**Effort:** L · **Risk of acting without step 1:** **High — silent content
loss** · **Risk of not acting:** Low; the PNGs are correct today ·
**Dependencies:** Eliot's approval on the 28 new diagrams · **Status:** OPEN

**Q23 is therefore re-put as Q26**, because the answer given was to a question
whose premise this inspection has changed.

---

## Addendum 2, 2026-08-09 — Q26 answered (route c), and the saving measured

Eliot chose route (c): re-encode the PNGs, treat the SVG adoption as separate
work. `DECISIONS.md` D25.

PH08-034(a) said "expect 26.2 MB → under 3 MB" from static reasoning. That has
now been measured on a 10-file sample (the 6 largest plus 4 at the median), using
Pillow 12.2.0:

```
sample of 10:  4.01 MB
  resize to 1600px, RGBA->RGB, optimize   1.56 MB   ratio 0.389
  + 64-colour palette                     0.49 MB   ratio 0.123
  WebP q88 method 6                       0.30 MB   ratio 0.075

projected over all 112 files (26.2 MB)
  resize only, same .png filenames        ~10.2 MB   0 HTML edits
  + 64-colour palette, same filenames     ~ 3.2 MB   0 HTML edits
  WebP                                    ~ 2.0 MB   231 src edits, 94 pages
```

**The estimate holds, and the zero-HTML-edit route reaches it.** Resize plus
64-colour palette gives 88% of the weight back without touching a single `<img>`,
because the filename and aspect ratio are unchanged. Mean notes-page image
payload falls from **513 KB to roughly 63 KB**.

Two verifications are outstanding and need a browser, not this audit: the
quantisation must be eyeballed on a shaded diagram for colour banding, and the
sample flattened RGBA onto white, which is wrong for any diagram intended to sit
on a non-white backdrop. Both are recorded in D25.
