# Phase 6 findings — HTML page architecture & generation strategy

Run 2026-08-09 on `audit/organisation-audit` at `d7744c3`.

**This is a proposal. No production file was written, no site file was changed.**
Everything below is reproducible in seconds from two new read-only scripts:

```
python3 docs/audit/scripts/page_anatomy.py     # boilerplate volume, skeletons, a11y
python3 docs/audit/scripts/notes_drift.py      # spines, provenance, metadata drift
```

Regression checks re-run before starting, all clean: 0 broken internal links,
461/463 reachable without JS, 0 duplicate titles, 0 duplicate descriptions, 0
canonical mismatches, `build_sitemap.py --check` → nothing written.

---

## How to read this document

It is written to be understood without prior knowledge of static-site tooling.
Section 0 explains the vocabulary. If you only read one section, read **§5, the
decision brief** — it is one page and it includes the honest case for doing
nothing.

---

## 0. The vocabulary, in plain terms

**A static site** is a folder of finished `.html` files. A web server hands the
file over unchanged. That is what this site is today: `revision-notes/edexcel-theme-1/1-1-1-economics-as-a-social-science.html`
is a real file, and its URL is its path.

**A build step** is a program you run *before* publishing. It reads some source
material and writes the finished `.html` files. The site still ends up as a
folder of finished files — the build just means a machine assembles them instead
of you.

**You already have a build step.** `scripts/build_questions.py`,
`build_glossary.py`, `build_flashcards.py` and `build_past_paper_questions.py`
between them write **273 of the 463 published pages** (59%) from JSON. You run
them by hand and commit the result. Phase 9b proved they are byte-idempotent:
run them again on unchanged input and you get identical files back.

So the question in this phase is **not** "should this site have a build step".
It has one. The question is: **should the remaining 190 hand-written pages join
it, and if so, built by what.**

**A template / layout** is the page skeleton with holes in it — everything that
is the same on every page, with `{title}` where the title goes.

**A partial / include** is a reusable fragment, e.g. one shared `<head>`.

**Boilerplate** is markup repeated identically in every file. Not *similar* —
byte-for-byte identical.

---

## 1. Current-state analysis

### 1.1 What is duplicated in every file, and how much of it there is

Twelve blocks of markup are byte-identical wherever they appear. Measured by
`page_anatomy.py` §1 across all 463 published pages:

| Block | On pages | Bytes/page | Total |
| --- | ---: | ---: | ---: |
| `gtag` script pair (GA4) | 463 | 348 | 158 KB |
| `charset` + `viewport` | 452 | 99 | 44 KB |
| `og:type` / `og:site_name` / `og:locale` | 442 | 160 | 69 KB |
| `og:image` set (5 tags) | 459 | 332 | 149 KB |
| `twitter:card` | 460 | 58 | 26 KB |
| favicon / apple-touch-icon / manifest | 463 | 169 | 76 KB |
| the `@import`-hoist explanatory comment | 463 | 346 | 156 KB |
| `preconnect` pair | 463 | 136 | 62 KB |
| fontawesome + Google Fonts + `main.css` | 463 | 369 | 167 KB |
| the seven-script tail | 463 | 338 | 153 KB |
| `<body>` wrapper + header placeholder | 463 | 116 | 53 KB |
| footer placeholder + wrapper close | 462 | 67 | 31 KB |
| **Total** | | **≈2,500** | **1,143 KB** |

**1.1 MB of the 21.4 MB of published HTML is the same ~2.5 KB repeated 463
times.** That is 5.2% of the bytes.

Restricted to the 190 hand-written pages — the ones this phase is actually about:

```
190 pages, 3,993 KB, 94,463 lines
identical boilerplate: 467 KB (11.7% of those pages' bytes)
```

Per family, bytes of identical boilerplate per page, and what share of the page
it is:

| Family | Pages | Generated | Boilerplate/pg | `<head>`/pg | Page/pg | Boiler % |
| --- | ---: | :---: | ---: | ---: | ---: | ---: |
| notes-topic | 166 | — | 2,548 | 6,118 | 19,404 | **13.1%** |
| notes-hub | 7 | — | 2,390 | 5,046 | 36,771 | 6.5% |
| notes-other | 3 | — | 2,456 | 7,269 | 66,953 | 3.7% |
| past-papers | 5 | — | 2,273 | 4,448 | 45,477 | 5.0% |
| root | 9 | — | 2,174 | 5,270 | 20,189 | 10.8% |
| mcq-topic | 166 | Y | 2,532 | 23,179 | 66,143 | 3.8% |
| mcq-hub | 7 | Y | 2,532 | 5,466 | 26,309 | 9.6% |
| ppq | 90 | Y | 2,548 | 5,532 | 64,368 | 4.0% |
| flashcards | 7 | Y | 2,548 | 5,131 | 20,088 | 12.7% |
| glossary | 3 | Y | 2,548 | 114,786 | 403,251 | 0.6% |

The generated families' `<head>` looks enormous on `mcq-topic` and `glossary`
because those pages embed their whole question set or term list as JSON-LD. That
is payload, not boilerplate.

**The `<head>` overall is 5,768 KB — 26.4% of every byte of HTML on the site.**
1,116 KB of that is hand-maintained.

#### The `<head>` is 100% derivable, and that is checkable

`notes_drift.py` §3 compares the fields that appear more than once per page:

```
pages where a duplicated <head> field disagrees with itself: 18 of 463
of those:  generated  0        hand-written  18
```

`<title>` = `og:title` = `twitter:title` on **463/463** pages. Meta description =
`og:description` = `twitter:description` on 445; the 18 exceptions carry a
deliberately shortened social variant (`about.html`, `index.html`,
`tutoring.html`, all five `past-papers/*` hubs, six notes hubs, and
`revision-notes/macro-application/`).

**Zero of the 18 are on a generated page.** Generators cannot disagree with
themselves; hand-written pages can, and do.

So a notes topic page's entire 6.1 KB `<head>` is computable from about ten
values: board, spec code, slug, `<title>`, meta description, an optional social
description, the JSON-LD `name` and `description`, the parent theme name, and a
"does this page use MathJax" flag.

### 1.2 Structural drift

`page_anatomy.py` strips every word of text out of a page and keeps only the tag
+ `id` + `class` structure. Two pages with the same skeleton differ only in
words. Two pages with different skeletons differ in markup — and markup
differences are what a template layer has to reconcile.

#### The outer shell is uniform. This is the good news.

| Family | Pages | Distinct `<head>` shapes | Distinct body shells | Distinct script tails | Distinct CSS sets |
| --- | ---: | ---: | ---: | ---: | ---: |
| **notes-topic** | **166** | **4** | **1** | **1** | **1** |
| mcq-topic | 166 | 1 | 1 | 1 | 1 |
| ppq | 90 | 1 | 3 | 1 | 1 |
| notes-hub | 7 | 2 | 2 | 1 | 2 |
| flashcards | 7 | 2 | 2 | 1 | 2 |
| mcq-hub | 7 | 2 | 2 | 1 | 1 |
| past-papers | 5 | 2 | 2 | 1 | 2 |
| glossary | 3 | 2 | 2 | 1 | 2 |
| notes-other | 3 | 2 | 3 | 1 | 2 |
| root | 9 | 9 | 9 | 3 | 9 |

**All 166 notes topic pages share exactly one body shell, one script tail and
one stylesheet set.** The root pages are all different, which is correct — they
are nine different pages, not a family.

#### The four `<head>` shapes among the 166 notes pages

Diffed with `difflib`, so the result is exact:

| | Pages | Difference from shape [1] |
| --- | ---: | --- |
| [1] | 97 | *(baseline)* MathJax config + `<script id="MathJax-script" src="…mathjax@3…">` |
| [2] | 40 | no MathJax at all — these pages contain no `\( … \)` |
| [3] | **28** | MathJax loaded **without** `id="MathJax-script"` |
| [4] | 1 | shape [1] **plus a `<style>` block in `<head>`** |

Shape [2] is legitimate: 40 pages have no maths. Shapes [3] and [4] are drift:

- **28 pages load the identical MathJax asset with different markup.** All 28 are
  Edexcel (`1-2-x`, `2-x-x`, `4-x-x`). Two ways of writing one thing, produced by
  hand at different times.
- **One page, `revision-notes/aqa-a2-micro/1-5-1-market-structures.html`, carries
  a 30-line `<style>` block in `<head>`** for a `.comp-spectrum` component.
  Against the house rule (CLAUDE.md: "No inline `style` attributes — extract a
  class"), and it is the only one.

#### The content spine: 9 shapes across 166 pages

The "spine" is the ordered list of direct children of `<div class="notes-container">`
— the top-level blocks of the page, ignoring everything nested inside them.
Runs of identical siblings are collapsed, because "this page has six `<section>`s
and that one has four" is content length, not structural drift.

Raw, that gives **38 distinct spines**. Collapsed, it gives **9**:

| | Pages | Spine |
| --- | ---: | --- |
| [1] | 95 | `header.major · spec-alert · section… · notes-cta · questions-link · past-papers-link · flashcards-link` |
| [2] | 29 | as [1] **+ `p.notes-diagrams-link`** |
| [3] | 15 | `header.major · spec-alert · section… · notes-cta · questions-link` *(no past-papers, no flashcards)* |
| [4] | 11 | as [3] **+ diagrams-link** |
| [5] | 7 | as [1] but no flashcards block, **+ diagrams-link** |
| [6] | 6 | as [1] but no flashcards block |
| [7] | 1 | **`… section · p · ul · p · notes-cta …`** — prose sitting outside any `<section>` |
| [8] | 1 | **`header.major · h2 · spec-alert · …`** — an `<h2>` *before* the spec-alert |
| [9] | 1 | **`… section · p · h3 · p · ul · notes-cta …`** — prose outside any `<section>` |

**Shapes [1]–[6] are the same page with different optional footers.** Six of the
nine "variants" are just which of three trailing link blocks is present:

| Board directory | Pages | has past-papers link | has diagrams link | Spine shapes |
| --- | ---: | ---: | ---: | ---: |
| `aqa-a2-macro` | 25 | 25 | 0 | 2 |
| `aqa-a2-micro` | 54 | 48 | 0 | 4 |
| `edexcel-theme-1` | 22 | 13 | 11 | 4 |
| `edexcel-theme-2` | 24 | 15 | 15 | 4 |
| `edexcel-theme-3` | 20 | 18 | 15 | 4 |
| `edexcel-theme-4` | 21 | 20 | 6 | 3 |

139 of 166 carry the past-papers link; 47 carry the diagrams link (that is
`d1e7a3a`'s 47 Edexcel pages, exactly). The diagrams link exists only on Edexcel
because only Edexcel has diagram galleries — correct, not drift.

**Shapes [7], [8] and [9] are three genuinely malformed pages**, and nothing in
the repo would catch them:

- `revision-notes/aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html:189`
  — `<h2>The Central Purpose of Economic Activity</h2>` sits between the `<h1>`
  and the `spec-alert`. CLAUDE.md's component contract says `spec-alert` "opens
  every topic page". On this page it does not.
- `revision-notes/aqa-a2-macro/2-1-2-macroeconomic-indicators.html` and
  `revision-notes/aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html`
  — paragraphs and lists sitting directly in `.notes-container`, outside any
  `<section>`.

#### Content vs chrome, by volume

The content region — from `<div class="spec-alert">` to `<div class="notes-cta">`
— is present **exactly once on 166/166 pages**, as is `header.major`, `<h1>`,
`notes-cta` and `notes-container`. There is no page where the boundary is
ambiguous.

```
notes-topic corpus:      3,146 KB
content region:          1,590 KB   50.5%
everything else:         1,556 KB   49.5%
```

Half the notes corpus is machinery. Of that half, the only per-page *prose* is in
the trailing link blocks: 3 distinct `<h2>` strings across all 166 pages, and 637
paragraphs of which 305 are unique to one page.

#### One of those "unique" paragraphs is not unique at all

`notes_drift.py` §2 joins each notes page to `questions-data/<board>/<spec>.json`:

```
Notes-page MCQ teaser vs questions-data notesTeaser
  identical to questions-data        166
```

**All 166 "Test yourself on this topic" blurbs on hand-written notes pages are
identical to the `notesTeaser` field in a JSON file that already exists.** They
were put there by `scripts/append_questions_link.py`, a one-shot additive script.
Edit the JSON today and the notes page silently goes stale; nothing compares
them. This is a single-source-of-truth violation of exactly the kind Phase 9
found in the data model — but here the duplicate copy is in the *published HTML*.

#### Breadcrumbs are authored twice per page, in two languages

Every page with a breadcrumb writes it twice: once as visible `<nav>` markup and
once as `BreadcrumbList` JSON-LD.

```
visible breadcrumb <nav class="breadcrumb">      441 pages
  with aria-label="Breadcrumb"                   100   (the 90 ppq + 7 flashcards + 3 glossary pages)
  without                                        341   (includes all 166 notes topic pages)
no visible breadcrumb                             22

visible vs JSON-LD copy:  agree 440,  DISAGREE 1
```

The one disagreement is `revision-notes/macro-application/index.html`: the JSON-LD
lists `Home › Revision Notes › Macroeconomic Application`, the visible trail omits
`Home`. 440/441 agreement is a good result — and it is a good result achieved by
hand, twice per page, with no check.

The `aria-label` split is the clearest picture of how drift happens here: the
three newest, *generated* families emit it; the 341 older pages do not. A
convention improved, and only the pages behind a generator received it.

### 1.3 The one page template that already exists, and why it is dangerous

`scripts/convert_raw_notes.py:785` contains a **complete revision-notes page
template** — doctype, `<head>`, body, script tail, 2,641 bytes. It converts
`raw-notes/edexcel/*.md` (73 files) into topic pages. CLAUDE.md documents
`raw-notes/` as "markdown source for converted notes" and does not mention that
the converter has fallen behind.

`notes_drift.py` §5, template vs a live page:

| Feature | In the template | On the live page |
| --- | ---: | ---: |
| `lang="en-GB"` | **0** | 1 (it emits `lang="en"`) |
| `rel="canonical"` | **0** | 1 |
| `og:` tags | **0** | 11 |
| `twitter:` tags | **0** | 4 |
| JSON-LD blocks | **0** | 2 |
| `LearningResource` | **0** | 1 |
| `BreadcrumbList` | **0** | 1 |
| hoisted fontawesome + fonts CSS | **0** | 1 |
| `preconnect` | **0** | 2 |
| `notes-cta` | **0** | 1 |
| `notes-questions-link` | **0** | 2 |

A page produced by this script today would ship with no canonical, no social
cards, no structured data, the wrong `lang`, no call-to-action — **and no web
fonts and no FontAwesome at all**, because `4db232c` removed the two `@import`
rules from `css/main.css` (verified: `css/main.css` mentions `@import` only in
the comment explaining their removal) and this template never learned to link
them in `<head>`.

This is the cost of an un-owned template layer stated as concretely as it can be:
**there is already a generator for this family, and running it would undo seven
SEO commits.**

### 1.4 Heading hierarchy, semantics and accessibility basics

`page_anatomy.py` §4, all 463 pages:

| Family | Pages | `h1` ≠ 1 | Skipped heading level | Images | Missing `alt` | Missing `width`/`height` | Missing `loading` | No `<main>` | Inline `style=` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| notes-topic | 166 | 0 | 0 | 211 | 0 | 0 | **94** | 166 | **26** |
| notes-other | 3 | 0 | 0 | 89 | 0 | 0 | 0 | 3 | 1 |
| notes-hub | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 6 |
| past-papers | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 5 |
| root | 9 | 0 | 0 | 3 | 0 | 3 | 2 | 8 | 6 |
| mcq-topic | 166 | 0 | 0 | 0 | 0 | 0 | 0 | 166 | 0 |
| mcq-hub | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| ppq | 90 | 0 | 0 | 0 | 0 | 0 | 0 | 90 | 0 |
| flashcards | 7 | 0 | 0 | 6 | 0 | 0 | 0 | 7 | 5 |
| glossary | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 2 |

**What is clean, and should not be re-audited:**

- **Exactly one `<h1>` on 463/463 pages. Zero skipped heading levels anywhere.**
  Heading hierarchy is correct across the whole site.
- **Zero images missing `alt`.** 309 images, all with alt text.
- `lang="en-GB"` on 463/463; the `#main` skip-link target exists on every page.

**What is not:**

- **No page uses the `<main>` landmark element** except `index.html`. The other
  462 use `<section id="main">`. The skip link in `templates/header.html:2`
  (`<a href="#main" class="skip-to-content">`) therefore works, but assistive
  technology gets no `main` landmark. Changing `<section id="main">` to
  `<main id="main">` is a one-attribute change that preserves the anchor — and
  it is a 462-file edit today.
- **94 of the 211 notes images have no `loading` attribute**, spread over 33
  pages. `width`/`height` are present everywhere, so there is no layout shift;
  this is bandwidth only.
- **26 notes topic pages carry inline `style=` attributes**, plus 1 `<style>`
  block. This is PH00-008 re-measured over the 463 pages: **51 pages carry at
  least one inline `style`, 44 of them hand-written and 7 generated.**
- **341 breadcrumbs lack `aria-label`**, per §1.2.

### 1.5 The concrete cost of a global change today

`notes_drift.py` §6:

| Change | Files to edit | Note |
| --- | ---: | --- |
| Add or change one nav item | **1** | `templates/header.html` — already solved by runtime injection |
| Add one `<meta>` tag to every page | **463** | 273 via 4 generator edits + rebuild; **190 by hand or by scripted rewrite** |
| Add `aria-label` to every breadcrumb | **341** | the 100 newest already have it |
| `<section id="main">` → `<main id="main">` | **462** | one attribute, every page |
| Add `loading="lazy"` to every note image | **33** | 94 images |
| Change the notes call-to-action wording | **166** | all hand-written |
| Add a board-switcher link to every note | **166** | all hand-written |
| Change the seven-script tail | **463** | every page |

This is not hypothetical. It is what the last four sitewide changes actually cost:

```
4db232c   469 files   hoist two @imports out of css/main.css into every <head>
befb061   184 files   rewrite remaining internal links to canonical URL form
17571f3   171 files   past-paper + sibling links on practice-questions pages
d1e7a3a    49 files   link 47 notes pages to their diagram gallery
```

**`4db232c` is the argument in one line: a two-line change to the `<head>`, and
it touched 469 files.** It was done correctly and it broke nothing. It was also
done by a script, in a repo whose own hard rule is that "scripted paragraph
rebuilds have silently destroyed `<a>` tags here before."

Every future structural improvement in this document costs 166–463 file edits
today and 1 edit after a template layer exists. That is the whole case.

---

## 2. Options appraisal

Five options, plus one that is not on the list but is the recommendation. Each is
scored on the nine axes asked for.

Throughout: **"interactivity"** means the flashcards, the MCQ quiz, the glossary
filter, the past-paper question search and the runtime header/footer injection —
six files in `js/components/`. Every one of them is vanilla JavaScript that
`fetch()`es a JSON file at runtime. **None of them is affected by any option
here**, because none of them is built. That axis is a tie and is not repeated
below except where an option threatens it.

### (a) Keep raw HTML, harden it

Add checks rather than machinery: a `verify_page_shell.py` that asserts every
page in a family has an identical `<head>` skeleton, body shell and script tail,
and that duplicated fields agree.

| Axis | Assessment |
| --- | --- |
| Migration effort | **Very low.** One new verifier, ~200 lines. `page_anatomy.py` is already 80% of it |
| URL stability risk | **None.** Nothing moves |
| SEO impact | **Neutral.** Stops new drift; fixes none of the existing 18+341+28 |
| Build complexity | **None added** |
| Ongoing maintenance | **Unchanged, i.e. bad.** Every sitewide change stays a 190–463 file scripted rewrite |
| Board dimension | **Unchanged.** 111 hardcoded board literals (PH01-012) stay |
| Interactivity | Unaffected |
| Failure modes | Drift accrues faster than checks are written. The `append_*_link.py` pattern — one-shot scripts that mutate finished pages — proliferates, and each is a fresh chance to destroy an `<a>` tag |
| Reversibility | N/A |

**Verdict.** This is the correct *floor*, not the answer. It should be done
regardless of what else is decided, and it is Phase 1 of the recommendation
below. On its own it converts an architecture problem into a monitoring problem.

### (b) Server-render the header/footer at build time only

Bake `templates/header.html` and `footer.html` into all 463 pages at build time
and drop the runtime `fetch()`.

| Axis | Assessment |
| --- | --- |
| Migration effort | **Medium.** Needs a build touching all 463 pages, i.e. most of the work of a real template layer |
| URL stability risk | **None** |
| SEO impact | **Positive, but it is P3's call not P6's.** It converts 14,816 injected link edges into raw ones, which directly addresses PH00-001 (`/past-papers/ocr/` and `/past-papers/edexcel-b/` have 1 raw inbound link each and carry 12k impressions between them). It also closes PH00-006, the no-fallback fetch failure |
| Build complexity | Low, but you have paid for a build and bought one feature |
| Ongoing maintenance | **The actual finding is untouched.** The `<head>` is still 190 hand-maintained copies |
| Board dimension | Unchanged |
| Interactivity | Removes one `fetch()`; the other five stay |
| Failure modes | Adds ~8 KB of nav markup × 463 pages (+3.7 MB). Editing the nav becomes a rebuild-and-recommit of 463 files instead of a 1-file edit — **it makes the cheapest change on the site more expensive** |
| Reversibility | High |

**Verdict.** Solves a real problem, but not this phase's problem, and it makes
one thing measurably worse. It belongs as an *optional later phase* of a template
migration — at which point it is nearly free — and it should not happen before P3
rules on link equity. **Not recommended as a standalone.**

### (c) Jekyll — front matter + `_layouts` + `_includes`

GitHub Pages already runs Jekyll on this repo. Add YAML front matter to the 190
hand-written pages, move the shell into `_layouts/`, the `<head>` into
`_includes/`.

| Axis | Assessment |
| --- | --- |
| Migration effort | **Medium-high.** 190 files edited once; layouts written; the 273 generated pages either stay outside Liquid (two template systems) or are rewritten |
| URL stability risk | **Low.** Front matter on a `.html` file does not change its output path. Zero URLs move |
| SEO impact | Neutral to positive |
| Build complexity | **Zero new tooling on the server** — this is Jekyll's one big advantage. But see failure modes |
| Ongoing maintenance | Good for the 190. **The `<head>` would then exist twice: once in Liquid, once in four Python generators.** That is Phase 9b's central tension restated, not solved |
| Board dimension | Good fit — `_data/boards.yml` is exactly the `boards.json` design from PH09 |
| Interactivity | Unaffected |
| **Failure modes** | **This is where it loses.** (1) **A stray `{%` fails the entire deploy — not the page, the site.** That has happened here once already. Today only 2 markdown files carry that risk; adding front matter to 190 HTML pages multiplies the exposure ~100×. Measured mitigating fact: there are currently **0 occurrences of `{%` and 0 of `{{` across all 465 published HTML files (463 pages plus the 2 templates)**, so the risk is future, not present. (2) **You cannot see what GitHub will build.** GitHub Pages builds server-side with its own pinned gem set. There is no Jekyll installed here, and the system Ruby is **2.6.10** — old enough that installing the current `github-pages` gem needs a newer Ruby first (unverified precisely; what *is* verified is that `jekyll` is absent and Ruby is 2.6.10). Even with Ruby installed, local Jekyll ≠ GitHub's Jekyll unless the gem versions are pinned to match. **The audit's own requirement is byte-comparable output at each step, and this option is the one where you cannot produce the "after" locally to compare.** |
| Reversibility | Medium. Strip front matter, re-inline. Only if the pre-migration HTML was kept |

**Verdict.** The most obvious option, and it is genuinely close. It fails on one
thing: **a migration you cannot verify locally is not a migration you can run
against a 100%-pass harness.** Second choice among the five named.

### (d) Eleventy via GitHub Actions

Eleventy is a small Node static-site generator. Node 22.19.0 is already installed
here. Publishing would move from GitHub Pages' branch build to a GitHub Actions
workflow that runs the build and deploys the output.

| Axis | Assessment |
| --- | --- |
| Migration effort | **Medium.** `package.json`, `.eleventy.js`, a workflow, layouts. Eleventy passthrough-copies anything it does not own, so migration is genuinely per-file opt-in |
| URL stability risk | **Medium, but fully controllable.** Flat `.html` and directory URLs are both reproducible via `permalink`. The harness proves it before anything ships |
| SEO impact | Neutral, with the same upside as (c) |
| Build complexity | **Real and new.** A `node_modules` tree, an npm dependency surface, a workflow whose failure means no deploy, and a Node version to keep current |
| Ongoing maintenance | Good. Layouts, includes, a data cascade, `collections` for hub pages and related links |
| Board dimension | Very good — `_data/boards.json` read by every template |
| Interactivity | Unaffected |
| **Failure modes** | **Switching Pages to "GitHub Actions" as the source disables the built-in Jekyll build — and with it `_config.yml`'s `exclude` list.** DO-NOT-BREAK records that this list is "the only thing keeping working files off the site"; before it existed, `/CLAUDE.md` and `/scripts/build_glossary.py` were live URLs. Under Actions, whatever the build copies is what ships, so the publishing gate must be rebuilt as an explicit allowlist and re-verified. Also: the deployed artifact is 227 MB, 171 MB of it exam-paper PDFs, uploaded on every deploy. Also: the repo stops being the served site — `git revert` no longer restores what is live |
| Reversibility | **High for the content**, medium for the plumbing. Eleventy's output is byte-comparable to today's tree, so you can always stop, commit the output and switch Pages back to branch-serving |

**Verdict.** The strongest of the three SSG options and the right answer *if* the
site were being rebuilt from scratch or grew a team. Today it introduces a second
language for templating alongside four proven Python generators, which leaves the
`<head>` defined twice — the same defect as (c) — and it demolishes the
publishing gate as a side effect. **Second choice overall, first among the named
SSGs.**

### (e) Astro via GitHub Actions

| Axis | Assessment |
| --- | --- |
| Migration effort | **High.** Astro wants to own the page: components, its own build pipeline, a large `node_modules` |
| URL stability risk | **Highest of the five.** Astro's `build.format` is a global switch — `'directory'` gives `/foo/`, `'file'` gives `/foo.html`. This site has **both grammars at once** (PH00-002: two families flat `.html`, three directory), so every page needs an explicit per-page override. Every one is a chance to move a URL under a host with no 301s |
| SEO impact | Neutral if URLs hold; catastrophic if they do not |
| Build complexity | Highest |
| Ongoing maintenance | Highest churn — major versions, framework integrations |
| Board dimension | Fine, no better than (d) |
| Interactivity | **This is the argument for Astro and it does not apply.** Astro's islands architecture exists to ship framework components (React/Svelte/Vue) with partial hydration. This site has zero framework components. Six vanilla JS files that fetch JSON gain nothing |
| Failure modes | Everything in (d), plus a much larger surface, plus the mixed-URL-grammar trap |
| Reversibility | Lowest — pages become `.astro` files, not HTML |

**Verdict. Ruled out explicitly.** Maximum cost, maximum URL risk, and its one
distinguishing capability is one this site does not use.

### (f) Extend the existing Python generation layer — **the recommendation**

Not on the brief's list. It is the recommendation, so it is argued in full.

Add a shared, stdlib-only Python module — call it `scripts/page_shell.py` — that
owns the `<head>`, the body wrapper, the breadcrumb (both copies, from one
source), and the script tail. Then:

1. The four existing generators import it and stop emitting their own `<head>`.
2. A fifth generator, `scripts/build_notes.py`, renders the 190 hand-written
   pages from extracted content fragments + a metadata JSON per page.
3. **Output is committed, exactly as the other 273 pages already are.**
   Publishing does not change. `_config.yml` does not change. GitHub Pages keeps
   branch-serving. No Actions in the deploy path.
4. GitHub Actions is added for **verification only** — run the harness and the
   eight `verify_*.py` scripts on every push. A workflow that only reads cannot
   break a deploy.

| Axis | Assessment |
| --- | --- |
| Migration effort | **Medium.** Comparable to (c) or (d), minus learning a new tool, minus the plumbing |
| URL stability risk | **Zero by construction.** The generator writes to the same paths that exist today. A path that changes is a diff the harness fails on |
| SEO impact | Neutral at migration (harness enforces it), then strongly positive — see §4 |
| Build complexity | **Lowest of any option with a build.** Stdlib-only Python, matching the repo's existing absolute norm. No `package.json`, no `node_modules`, no Gemfile, no lockfile, no supply chain |
| Ongoing maintenance | **Best available**, because it is the only option that ends with the `<head>` defined **once**. Every other option leaves it in two languages |
| Board dimension | `boards.json` from PH09, read by `page_shell.py`, kills PH01-012's 111 literals at the root |
| Interactivity | Unaffected |
| Failure modes | Python string templating is ad-hoc where Liquid/Nunjucks are designed systems — mitigated by the fact that four generators already do this successfully and idempotently. No hot-reload dev server; you rebuild and refresh Live Server |
| **Reversibility** | **Highest of every option.** Output is committed, so rollback is `git revert` and the served bytes return exactly. Abandon after any phase and the site is a normal folder of finished HTML — because it always was |

#### Why this beats (c) and (d) on this specific repo

1. **It is the only option that ends with one `<head>`.** Phase 9b named this as
   P6's central design question: a template layer over the 190 must either
   coexist with four generators that emit their own `<head>`, or absorb them.
   Jekyll and Eleventy can only coexist — Liquid or Nunjucks cannot be called
   from `build_glossary.py`. A Python module can be imported by all five.
2. **The pattern is already proven in this repo.** 273 pages, 59% of the site,
   built this way, verified byte-idempotent in Phase 9b, with Prettier normalising
   the output so a second build is byte-identical.
3. **It preserves "what is in the repo is what is served."** For a solo project
   with no CI and no team, that is a real virtue, and options (d) and (e) spend it.
4. **It does not touch the publishing gate.** `_config.yml`'s `exclude` list keeps
   working. DO-NOT-BREAK's first three entries survive untouched.
5. **Verification is possible.** You can build locally, byte-compare, and only
   then commit. Under (c) you cannot.

#### What (f) gives up, honestly

- No dev server with hot reload. For a site whose content is finished, this
  matters less than it would otherwise.
- Python string templates have no template language's guard rails; escaping and
  indentation are the author's problem. Prettier over the output mitigates this,
  as it already does for four generators.
- If the project ever gains collaborators who do not write Python, (d) is better.

### Summary

| Option | Migration | URL risk | Build cost | Maintenance after | Reversible | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| (a) harden raw HTML | Very low | None | None | Unchanged | n/a | **Do it anyway — it is Phase 1** |
| (b) bake header/footer | Medium | None | Low | Unchanged | High | Later, optional, after P3 |
| (c) Jekyll | Medium-high | Low | None new | Two `<head>`s | Medium | **Third.** Cannot verify locally |
| (d) Eleventy + Actions | Medium | Medium | Real | Two `<head>`s | High | **Second overall** |
| (e) Astro + Actions | High | **Highest** | Highest | Two `<head>`s | Low | **Ruled out** |
| **(f) Python shell module** | **Medium** | **Zero** | **Lowest** | **One `<head>`** | **Highest** | **RECOMMENDED** |

**Recommendation: (f).** **Second choice: (d) Eleventy via GitHub Actions** —
and if it is ever chosen, choose it as a whole-site rewrite that also absorbs the
four Python generators, not as a layer beside them.

---

## 3. Migration plan for the recommended option

Seven phases. **Each ends with a commit, a passing harness, and a site that is
complete and consistent.** Abandon after any phase and nothing is half-done.

### Phase 0 — The harness. No site file is touched.

**This is the deliverable that gates everything else, and it is built first.**

`docs/audit/scripts/harness/compare_trees.py OLD NEW` takes two directory trees and
runs ten assertions. Migration of a page family does not proceed until all ten
pass for every page in it.

| # | Assertion | How | Rationale |
| --- | --- | --- | --- |
| 1 | **URL set identical** | Enumerate published `.html` in both trees, map through `lib.canonical_url()`, assert set equality. Repeat for the 281 PDFs and every asset | The non-negotiable constraint. A missing page and a moved page look the same to a crawler |
| 2 | **Normalised visible text zero-diff, per page** | Reuse `verify_text_integrity.py`'s `TextExtractor`: drop `<script>`/`<style>` content, decode entities, NFC-normalise, collapse whitespace. Assert `old == new` **per file**, not in aggregate | The content guarantee. Content survives byte-identical after whitespace normalisation, or the page does not migrate |
| 3 | **LaTeX spans compared byte-exact** | Extract every `\( … \)` and `\[ … \]` span and compare without whitespace collapsing | Assertion 2 collapses whitespace, which could mask a real change inside a formula. This closes that hole |
| 4 | **Markup integrity** | `verify_markup_integrity.py --strict`, adapted to compare trees rather than git refs: no element type's count may drop; no `href` or `src` present before may vanish | Stripping an `<a>` changes no visible text, so assertion 2 is blind to it. This is the check that catches the failure mode CLAUDE.md warns about |
| 5 | **`<head>` field equality** | `title`, `description`, `canonical`, every `og:*`, every `twitter:*`, `robots`, `lang`: assert identical unless the page+field appears in `_audit/harness/intentional-changes.json` with a written reason | "Identical unless deliberately changed", made mechanical. An empty allowlist means nothing may change |
| 6 | **JSON-LD semantic equality** | Parse each block; compare as normalised JSON — key order irrelevant, `itemListElement` order significant | Indentation will legitimately change. Meaning must not |
| 7 | **Internal link set preserved or improved** | Per page, resolved internal `<a href>` targets: assert `old ⊆ new`; report additions separately. Sitewide, re-run `link_graph.py` on NEW and assert 0 broken targets and ≤2 orphans | Links may be added, never lost |
| 8 | **Non-migrated files byte-identical** | Every file outside the family being migrated must be byte-for-byte unchanged | Proves the build is a no-op everywhere it is not wanted |
| 9 | **Idempotence** | Build twice into two trees, assert byte-identical | The repo's established standard (Phase 9b). Also flushes out any build-date stamp — see PH09b-025 |
| 10 | **Existing verifiers still pass** | `verify_html.py`, `verify_links.py`, `verify_glossary.py`, `verify_past_paper_tags.py`, `seo/tools/verify_seo.py` (4 permanent assertions), `build_sitemap.py --check` | The Phase 9b baseline must not regress |

Two supporting notes:

- **Prettier is run over both sides before byte comparison** where the generator
  runs Prettier over its own output, as `build_glossary.py` and
  `build_past_paper_questions.py` already do. Otherwise assertion 9 fails on
  formatting rather than meaning.
- **The harness lives in `_audit/`** during the audit and moves to `scripts/`
  when the first family migrates, so it becomes a permanent verifier rather than
  a one-off.

**Rollback:** nothing to roll back. No site file has been touched.

### Phase 1 — Harden in place (option (a)), and fix nothing else

Add `scripts/verify_page_shell.py`: for each family, assert one `<head>`
skeleton, one body shell, one script tail, one stylesheet set, and that
duplicated `<head>` fields agree. Seed it with today's measured values — 4 head
shapes on notes-topic, 9 spines, the 18 known `og:description` exceptions — so it
passes on the current tree and fails on anything new.

This is worth doing **even if the migration is rejected**. It is the cheapest 80%
of the value in this document.

**Rollback:** delete one file.

### Phase 2 — `boards.json` and `page_shell.py`, wired into nothing

Write `scripts/page_shell.py` (the shared `<head>`, wrapper, breadcrumb and
script tail) and `boards.json` (PH09's design). Prove them by rendering the
existing pages' `<head>` blocks and byte-comparing — **without writing a single
file.** A `--selftest` flag that reports "190/190 heads reproduced byte-identical"
is the phase's exit criterion.

**This is the highest-information, lowest-risk step in the plan.** If the shell
module cannot reproduce today's `<head>` exactly, that is discovered here, at
zero cost, before anything is written.

**Rollback:** delete two files.

### Phase 3 — Pilot: `past-papers`, 5 pages

The smallest family, no economics prose, high commercial value (the two
best-earning non-homepage URLs live here — PH00-001), and it has a real
board dimension (Edexcel, Edexcel B, AQA, OCR) so it exercises `boards.json`.

Mechanical extraction, described in full below. Then: build to a scratch tree,
run the harness, and only if all ten assertions pass, write into the working tree
and commit.

**Rollback:** `git revert` one commit. Because output is committed, the served
bytes return exactly.

### Phase 4 — Root pages (9), notes hubs (7), notes-other (3), notes index

19 pages. These carry 13 of the 18 `og:description` mismatches, so they exercise
the "intentional exception as data" path in assertion 5.

**Rollback:** `git revert`.

### Phase 5 — `notes-topic`, 166 pages, one board directory at a time

Six sub-phases, smallest first: `edexcel-theme-3` (20) → `theme-4` (21) →
`theme-1` (22) → `theme-2` (24) → `aqa-a2-macro` (25) → `aqa-a2-micro` (54). Each
is a commit and a harness run.

Deliberate normalisations, each recorded in `intentional-changes.json` with a
reason, each individually revertable:

- the 28 MathJax tags gain `id="MathJax-script"` (28 pages)
- `aria-label="Breadcrumb"` added (166 pages)
- `<section id="main">` → `<main id="main">` (166 pages, anchor preserved)
- `loading="lazy"` on the 94 images lacking it (33 pages)
- the `<style>` block on `1-5-1-market-structures.html` moves to
  `css/pages/revision-notes-textbook.css`
- the 26 inline `style=` attributes become classes

**None of these is done in Phase 5 by default.** They are proposed, listed, and
applied one at a time *after* the family has migrated byte-identically. Migrate
first, improve second — otherwise a harness failure is ambiguous between "the
template is wrong" and "the improvement is wrong".

**Rollback:** `git revert` the sub-phase. The other five board directories are
unaffected.

### Phase 6 — Absorb the four existing generators' `<head>`

Change `build_questions.py`, `build_glossary.py`, `build_flashcards.py` and
`build_past_paper_questions.py` to import `page_shell.py`. Rebuild, harness,
expect zero diff on all 273 pages.

**This is the phase that actually resolves Phase 9b's central tension** — after
it, the `<head>` exists once, for all 463 pages.

**Rollback:** `git revert`.

### Phase 7 (optional, gated on P3) — bake the header/footer at build time

Option (b), now nearly free. **Do not start it until P3 has ruled on link
equity.** If it happens, editing the nav becomes a rebuild rather than a 1-file
edit, which is a real cost that must be traded knowingly.

### The mechanical extraction, in detail

The single most important rule:

> **The content is moved by slicing bytes out of the existing file. It is never
> parsed and re-serialised. No HTML parser round-trip. No prose is regenerated.**

That is what protects against the failure mode CLAUDE.md records — "scripted
paragraph rebuilds have silently destroyed `<a>` tags here before". A byte slice
cannot destroy an `<a>` tag, because it does not understand what one is.

For a notes topic page:

1. **Find the content boundaries.** `<div class="notes-container">` … opening of
   `<div class="notes-cta">`. Verified present **exactly once on 166/166 pages**
   (`page_anatomy.py`). If a page had zero or two, extraction refuses to run on
   it and it is handled by hand.
2. **Write the slice verbatim** to `notes-data/<board-dir>/<spec>.html` — the raw
   bytes, unmodified, including the `<h1>`, the `spec-alert`, all `<section>`s
   and any of the three anomalous stray blocks. Those three pages migrate
   unchanged precisely *because* the slice does not model the structure.
3. **Lift the metadata verbatim** into `notes-data/<board-dir>/<spec>.json`:
   `title`, `description`, optional `ogDescription`, `canonical`, JSON-LD `name`
   and `description`, `themeName`, `board`, `spec`, `slug`, `mathjax` (true/false
   and whether the tag carries the id), and flags for the three optional trailing
   blocks. **Lifted from the page, never re-derived** — the meta descriptions are
   bespoke per page and re-writing them would be a content change.
4. **Do not extract the MCQ teaser.** It is already `notesTeaser` in
   `questions-data/<board>/<spec>.json`, proven identical on 166/166. The
   generator reads it from there. This deletes the duplicate copy rather than
   moving it, and makes the two permanently unable to drift.
5. **Render** = shell + slice + trailing blocks, then Prettier.
6. **Compare** against the original with all ten assertions.

`notes-data/` goes into `_config.yml`'s `exclude` **in the same commit that
creates it**, before anything is pushed. The published-file census
(`lib.published_html()`) is run to confirm before commit.

### Rollback plan, per phase

| Phase | Rollback | Site state after rollback |
| --- | --- | --- |
| 0 harness | none needed | untouched |
| 1 shell verifier | delete 1 file | untouched |
| 2 shell module | delete 2 files | untouched |
| 3 pilot (5 pages) | `git revert <sha>` | exact prior bytes restored |
| 4 root/hubs (19) | `git revert <sha>` | exact prior bytes restored |
| 5 notes (×6 sub-phases) | `git revert` the sub-phase | other five directories unaffected |
| 6 absorb generators | `git revert <sha>` | generators re-emit their own `<head>` |
| 7 bake templates | `git revert <sha>` | runtime injection restored |

**Rollback is `git revert` at every stage, and it restores the served bytes
exactly, because the output is committed.** This property is the single strongest
argument for option (f) over (d) — under an Actions-deploy model, rollback means
re-running an old workflow and hoping the toolchain still resolves.

### What could go wrong, and the early warning signs

| Risk | Early warning sign | Mitigation |
| --- | --- | --- |
| **Prettier reflows the generated HTML differently from the committed HTML** | First build shows a large diff on *every* page, all whitespace | Run Prettier 3.9.6 over both sides before comparison. Pin the version — CLAUDE.md already records 3.9.6 |
| **Entity encoding drift** (`&rsaquo;` → `›`, `&amp;` → `&`) | Every page differs by the same small delta | Assertion 2 decodes entities; assertion 8's byte comparison catches it on non-migrated files. Slicing rather than re-serialising prevents it in the first place |
| **Whitespace collapsing hides a change inside LaTeX** | Nothing — this is the silent one | Assertion 3 exists solely for this |
| **A meta description gets re-derived instead of lifted** | Assertion 5 fails on a handful of pages | Extraction lifts verbatim; the 18 known `og:description` exceptions are modelled as an optional field, not normalised away |
| **Board differentiation erased by "factoring out" `spec-alert` / `notes-cta`** | Assertion 2 fails, and P5's similarity numbers would rise | **DO-NOT-BREAK, P5.** These two blocks are load-bearing SEO on the 22 near-identical Edexcel/AQA pairs. They stay inside the per-page slice and per-page data, never in the shared layout. The board name and unit must survive into the output verbatim |
| **`notes-data/` published by accident** | `/notes-data/…` appears in a filesystem census, or in `sitemap.xml` | Add to `_config.yml` `exclude` in the same commit; run `lib.published_html()` and `build_sitemap.py --check` before committing |
| **A build-date stamp reintroduced** | Assertion 9 fails on a second build; every rebuild dirties files | PH09b-025 is the precedent. `page_shell.py` must contain no date. Assertion 9 makes it impossible to miss |
| **The three malformed pages fail to template** | Assertion 2 fails on exactly `1-1-2-…`, `2-1-2-…`, `1-6-3-…` | They cannot fail: the slice is verbatim. If they do, extraction has strayed from slicing into parsing — stop and re-read the code |
| **`--check` gives a false pass** | It reports success, then a real build changes files | PH09b-026. The new generator's `--check` must compare rendered output against the file on disk and exit non-zero on any difference, copying `build_sitemap.py:252` |
| **Scope creep: improvements applied during migration** | A harness failure that is ambiguous between "template wrong" and "improvement wrong" | Migrate byte-identically first. Every improvement is a separate later commit with its own harness run |
| **`verify_text_integrity.py` only covers `revision-notes/`** | It passes while a root page changes | The harness must cover all 463, not inherit that scope limit |

---

## 4. What this unlocks

Each item names the finding it closes and the cost today vs after.

| Capability | Finding | Cost today | Cost after |
| --- | ---: | ---: | ---: |
| **One `<head>` for the whole site** | PH00-004 (corrected to 190), PH09b | 463 files | **1 file** |
| **`aria-label` on every breadcrumb** | §1.2 — 341 pages lack it | 341 files | **1 file** |
| **`<main>` landmark** | §1.4 — 462 pages have none | 462 files | **1 file** |
| **`EducationalOrganization` on all pages** | PH00-007 — missing from 109 | 109 files / 3 generators | **1 file** |
| **Breadcrumb written once, rendered twice** | §1.2 — 1 page's two copies disagree | 441 pages × 2 copies | **1 file**, and they cannot disagree |
| **Board-switcher links** | PH05-019 | 166 files | **1 file** |
| **Related-topic links** | PH00-001, P3 | 166 files | **1 file** |
| **"Papers for other boards" row on the 4 hubs** | PH00-001 | 4 files | **1 file** |
| **`boards.json` as one board identity** | PH00-003, PH01-012, PH09-022 | 111 literals in 9 generators | **1 file** |
| **`loading="lazy"` on every image** | §1.4 — 94 images, 33 pages | 33 files | **1 file** |
| **Consistent metadata, enforced** | §1.1 — 18 self-disagreements | unenforceable | schema-enforced |
| **MCQ teaser cannot drift from its JSON** | §1.2 — 166 duplicate copies | unenforceable | duplicate deleted |

Four worth spelling out.

**Board-switcher links close a genuine SEO gap that P5 identified.** P5 found 22
Edexcel/AQA topic-page pairs whose prose is ≥0.95 identical, one differing by the
single token `1.5.3`. DO-NOT-BREAK records that `spec-alert` and `notes-cta` are
currently "the only things telling Google the two pages are different". A link
reading *"Studying AQA? See 1.5.3 Perfect Competition"* on the Edexcel page and
its mirror on the AQA page adds board-specific anchor text and a board-specific
outbound edge to **both** pages — differentiation, not consolidation, which is
exactly what D4 requires. Today: 22 hand edits, done by hand, on the 22 pages the
audit happens to know about. After: derived from `boards.json` + the topic
pairing that `board_similarity.py` already computes, for all 166 pages, in one
template edit. **This is the largest single SEO opportunity in the document and
it is currently priced at "too expensive to try."**

**PH00-001's two best-earning URLs.** `/past-papers/edexcel-b/` and
`/past-papers/ocr/` carry 143 clicks and 11,971 impressions between them and have
**one raw inbound link each**. P3 will decide whether a "papers for other boards"
row on the four board hubs is defensible. It is a 4-file edit today, which is
cheap — but the *reason* it was declined in `seo/07b-link-decisions.md` §4 was
that there is no topically honest anchor. A template that knows the board set can
generate an honest one ("Also available: AQA, OCR, Edexcel B") consistently on
every hub, and extend it to the 166 notes pages' `notes-cta` if P3 approves.

**The sitemap stops drifting.** PH01-017 found four stale `lastmod` values because
nothing re-runs `build_sitemap.py` after a commit. With a build step, the sitemap
is regenerated as part of the same command, and the Actions verification workflow
fails the push if `build_sitemap.py --check` reports a difference.

**PH09b-026's broken `--check` gets fixed for free.** The new generator ships with
a real output comparison from day one, and `page_shell.py` gives the other four a
copyable place to inherit it from. Fix PH09b-025 (the build-date stamps) first,
or every `--check` cries wolf.

---

## 5. Decision brief

**One page. Read this and decide.**

### What was measured

- **190 pages are hand-written**, not 463 (Phase 9b's correction holds). 166 of
  them are revision-note topic pages.
- **≈2.5 KB of byte-identical boilerplate sits in every one of the 463 pages** —
  1.1 MB in total, 5.2% of all published HTML. The `<head>` is 26.4% of the
  site's HTML bytes and is **100% derivable** from about ten values per page.
- **The shell is remarkably uniform.** All 166 notes pages share one body
  skeleton, one script tail, one stylesheet set, and just **4 `<head>` shapes**
  (of which one is legitimate: 40 pages have no maths). The content spine has
  **9 shapes, and 6 of those are just which optional footer link is present.**
- **Drift is small but real and unmonitored:** 28 pages load MathJax with
  different markup; 341 breadcrumbs lack the `aria-label` the newest 100 have;
  18 hand-written pages disagree with themselves on a `<head>` field they write
  twice (0 generated pages do); 3 notes pages are structurally malformed; 1 page
  has a `<style>` block in `<head>`; 462 pages have no `<main>` element.
- **`scripts/convert_raw_notes.py` already contains a full notes-page template —
  and it is seven SEO commits out of date.** A page built with it today would
  ship with no canonical, no social cards, no structured data, `lang="en"`, and
  **no web fonts at all**. This is the clearest possible evidence of an un-owned
  template layer.
- **All 166 "Test yourself" blurbs on notes pages are byte-identical copies of
  `notesTeaser` in `questions-data/`.** Nothing checks they still agree.
- **A sitewide `<head>` change costs 463 file edits.** `4db232c` — a two-line
  change — touched 469 files.

### What is recommended

**Extend the existing Python generation layer.** A shared stdlib-only
`scripts/page_shell.py` owning the `<head>`, wrapper, breadcrumb and script tail;
a fifth generator for the 190 hand-written pages; output committed exactly as the
other 273 pages already are. **Publishing does not change. `_config.yml` does not
change. No URL moves. No new dependency.** GitHub Actions is added for
verification only — never in the deploy path.

**Second choice: Eleventy via GitHub Actions.** Better tooling, real templates, a
dev server — but it introduces a second templating language beside four proven
Python generators, so the `<head>` still ends up defined twice; and switching
Pages to Actions disables `_config.yml`'s `exclude`, which DO-NOT-BREAK names as
"the only thing keeping working files off the site".

**Jekyll is third** — natively supported, changes no URL, needs no new tooling on
the server, but **you cannot build it locally on this machine to compare against**
(no Jekyll installed, system Ruby 2.6.10), and a migration that cannot be verified
locally cannot be run against a 100%-pass harness. **Astro is ruled out**: highest
URL risk on a site with two URL grammars, and its one distinguishing feature —
islands for framework components — is one this site has no use for.

### What it costs

Roughly five focused sessions, of which the first two touch no site file at all
(harness, then the shell module proven by self-test). The pilot is 5 pages. The
166 notes pages migrate one board directory at a time, smallest first. **Nothing
proceeds on any family until the ten-assertion harness passes 100% on it.**

### The honest case against

1. **The site is currently correct on every axis anyone measures.** 0 duplicate
   titles, 0 duplicate descriptions, 0 canonical mismatches, 0 broken internal
   links, 461/463 reachable without JS, exactly one `<h1>` per page, zero images
   without alt text, zero skipped heading levels. A migration risks a site that is
   measurably fine.
2. **The content is finished**, so the cost being removed is the cost of *future
   structural* changes. If you make none, the migration returns nothing. It is a
   bet on doing more structural work later, and only you know whether that is true.
3. **The drift is much smaller than Phase 0 implied.** 4 head shapes, not 166.
   9 spine shapes, 6 of them trivial. One body shell. This is a well-kept site,
   and PH00-004's "463 hand-maintained `<head>` blocks" overstated the disorder
   as well as the count.
4. **"What is in the repo is what is served" is a genuine virtue** for a solo
   project with no CI, and the migration spends 166 more pages of it. After
   migration you cannot open a notes page and fix a typo — you fix a fragment and
   rebuild. That is a real, daily loss against an occasional gain.
5. **You already have a workaround that works.** Scripted rewrites did `4db232c`
   across 469 files and broke nothing, verified by `verify_text_integrity.py` and
   `verify_markup_integrity.py`. The danger is real but it has not yet bitten.
6. **The harness is itself a non-trivial build** — ten assertions, and it must be
   right, because everything else trusts it.

### If you only do one thing

**Do Phase 1 alone.** `scripts/verify_page_shell.py` — assert that every page in
a family shares one `<head>` skeleton, one body shell, one script tail, and that
fields written twice agree. It is ~200 lines, `page_anatomy.py` is most of it
already, it changes not one published byte, and it would have caught every drift
in this document. It converts the architecture problem into a monitoring problem,
which is a much cheaper problem to own.

Then decide about the rest later, with the drift held still in the meantime.

### The three questions I need answered to proceed

| | Question | My recommendation |
| --- | --- | --- |
| **Q18** | Option (f) — Python shell module, output committed — or (d) Eleventy? | **(f)**, for the reasons in §2 |
| **Q19** | Is GitHub Actions acceptable for **verification only**, never in the deploy path? | **Yes.** A read-only workflow cannot break a deploy, and it fixes PH01-017 and PH09b-026 |
| **Q20** | Do the deliberate normalisations in Phase 5 (28 MathJax tags, 341 `aria-label`s, `<main>`, 94 `loading="lazy"`, 26 inline styles) have approval **as separate later commits**? | **Yes to all five, separately, after each family has migrated byte-identically** |

---

## Findings logged

IDs are stable. Never renumber.

### PH06-027 — The only revision-notes page template is seven SEO commits out of date, and re-running it regresses the page

**Severity:** High · **Category:** Generation / governance · **CERTAIN**

**Evidence.** `scripts/convert_raw_notes.py:785` holds a complete 2,641-byte page
template. Compared with a live page (`notes_drift.py` §5), it emits **zero** of:
`rel="canonical"`, any `og:` tag (live: 11), any `twitter:` tag (live: 4), either
JSON-LD block, `preconnect`, the hoisted fontawesome/fonts stylesheets, or
`notes-cta`. It emits `lang="en"` where every live page has `lang="en-GB"`.

Because `4db232c` removed the two `@import` rules from `css/main.css` — verified,
`css/main.css` mentions `@import` only in the comment explaining their removal —
a page produced by this script today would load **no web fonts and no
FontAwesome**.

**Why it matters.** CLAUDE.md documents `raw-notes/` as the source for converted
notes and does not record that the converter is stale. 73 markdown sources are
sitting there. The next person to add an Edexcel topic from `raw-notes/` runs the
documented command and ships a page that silently undoes seven commits of SEO
work — and `verify_seo.py`'s four assertions do not cover canonicals or og tags
per page.

**Recommendation.** Either bring the template up to date, or — better, and this is
what §3 Phase 5 does — replace it with `page_shell.py` so there is one template
that cannot fall behind. Until then, add a loud comment at
`convert_raw_notes.py:785` and a line in CLAUDE.md.

**Effort:** S to warn, M to fix properly · **Risk of acting:** Low ·
**Risk of not acting:** High — a silent, one-command SEO regression ·
**Dependencies:** none · **Status:** OPEN

### PH06-028 — All 166 notes pages carry a duplicate copy of prose that already exists in `questions-data/`

**Severity:** Medium · **Category:** Single source of truth · **CERTAIN**

**Evidence.** `notes_drift.py` §2 joins each notes page to
`questions-data/<board-dir>/<spec>.json`. The `<p>` inside
`<div class="notes-questions-link">` is identical, after whitespace
normalisation, to that file's `notesTeaser` field on **166 of 166** pages. It was
placed there by `scripts/append_questions_link.py`.

**Why it matters.** Editing `notesTeaser` today updates the practice-questions
page and silently leaves the notes page stale. Nothing compares them, and
`verify_text_integrity.py` compares a page against its own past, not against its
source of truth. Phase 9 found source-of-truth problems in the data model; this
is the same defect with the duplicate copy sitting in published HTML.

**Recommendation.** Have the notes generator read `notesTeaser` from
`questions-data/` rather than storing a copy (§3, extraction step 4). Until then,
a three-line check in `verify_page_shell.py` closes it.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low-Medium ·
**Dependencies:** none · **Status:** OPEN

### PH06-029 — Eighteen hand-written pages disagree with themselves on a `<head>` field they write twice; zero generated pages do

**Severity:** Low-Medium · **Category:** Metadata consistency · **CERTAIN**

**Evidence.** `notes_drift.py` §3. `<title>` = `og:title` = `twitter:title` on
463/463. Meta description = `og:description` on 445/463; the 18 exceptions are
`about`, `contact`, `faq`, `index`, `marking`, `tutoring`, all five
`past-papers/*` hubs, six notes hubs, `revision-notes/index.html`, and
`revision-notes/macro-application/` (that last on `twitter:description`).

**Generated pages: 0 of 273. Hand-written pages: 18 of 190.**

**Why it matters.** The variants read like deliberate, shorter social copy, and
may well be. But nothing records the intent, so the next scripted `<head>` rewrite
either flattens them or preserves them by accident. The split — 0 generated, 18
hand-written — is the finding: generators cannot disagree with themselves.

**Recommendation.** Decide whether the 18 are deliberate. If yes, model them as an
explicit `ogDescription` field so they survive any future rewrite; if no, make
them agree. Either way, assert it thereafter.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low ·
**Dependencies:** none · **Status:** OPEN

### PH06-030 — Breadcrumbs are authored twice per page in two languages; 341 lack the `aria-label` the newest 100 have

**Severity:** Medium · **Category:** Accessibility / duplication · **CERTAIN**

**Evidence.** `notes_drift.py` §4. 441 pages carry `<nav class="breadcrumb">` and
440 also carry a `BreadcrumbList` JSON-LD block listing the same names. Of the
441, **100 have `aria-label="Breadcrumb"` and 341 do not** — the 100 are exactly
the three newest, generated families (90 ppq + 7 flashcards + 3 glossary). All
166 notes topic pages are in the 341.

One page's two copies disagree: `revision-notes/macro-application/index.html`
lists `Home › Revision Notes › Macroeconomic Application` in JSON-LD and omits
`Home` from the visible trail.

**Why it matters.** 440/441 agreement, achieved by hand, twice per page, with no
check — that is luck holding, not a system. And the `aria-label` split is the
clean picture of how this repo drifts: a convention improved, and only the pages
behind a generator received the improvement.

**Recommendation.** Derive both copies from one breadcrumb definition (§3). Until
then, `verify_page_shell.py` should assert the two agree; that check would have
caught the macro-application page.

**Effort:** S to check, M to unify · **Risk of acting:** Low ·
**Risk of not acting:** Low-Medium · **Dependencies:** none · **Status:** OPEN

### PH06-031 — Four structural anomalies in the notes family that nothing would catch

**Severity:** Low · **Category:** Markup consistency · **CERTAIN**

**Evidence.** `page_anatomy.py` §3 and `notes_drift.py` §1:

- `revision-notes/aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html:189`
  — an `<h2>` sits between the `<h1>` and the `spec-alert`, so the page does not
  open with the `spec-alert` as the component contract requires.
- `revision-notes/aqa-a2-macro/2-1-2-macroeconomic-indicators.html` and
  `revision-notes/aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html`
  — paragraphs and lists directly inside `.notes-container`, outside any
  `<section>`.
- `revision-notes/aqa-a2-micro/1-5-1-market-structures.html:136` — a 30-line
  `<style>` block in `<head>`, the only one in the family, against the house rule.

Also in scope, though a variant rather than a defect: **28 Edexcel pages load
MathJax without `id="MathJax-script"`** while 98 load it with — one asset, two
markups. And 29 of 166 pages carry more than two components, against CLAUDE.md's
"max two components per page, total".

**Why it matters.** Low individually. Collectively they are the argument: five
distinct inconsistencies, none of which any of the eight `verify_*.py` scripts
looks for, in the family that gets the most editorial attention on the site.

**Recommendation.** Fix as separate commits after any migration, never during
(§3). The `<style>` block moves to `css/pages/revision-notes-textbook.css`. The
`<h2>` ordering and the two stray-prose pages are markup-only moves — **but they
are inside prose regions, so they need explicit approval and `verify_text_integrity.py`
run against the prior commit.** The MathJax `id` is a safe normalisation. The 29
over-budget component pages are an editorial call, not a technical one.

**Effort:** S · **Risk of acting:** Low, but touches prose regions ·
**Risk of not acting:** Low · **Dependencies:** none · **Status:** OPEN

### PH06-032 — 462 of 463 pages have no `<main>` landmark

**Severity:** Low · **Category:** Accessibility · **CERTAIN**

**Evidence.** `page_anatomy.py` §4: `<main>` appears on `index.html` only. Every
other page uses `<section id="main">`. The skip link at
`templates/header.html:2` (`<a href="#main">`) therefore lands correctly, so
keyboard users are served; screen-reader users get no `main` landmark to jump to.

**Why it matters.** Modest, and it is the cheapest accessibility win available:
`<section id="main" class="x">` → `<main id="main" class="x">` preserves the
anchor, the id, the class and every CSS rule scoped under it. It is a 462-file
edit today and a one-file edit after a template layer, which makes it a good
proxy for the value of this whole phase.

**Recommendation.** Do it as part of §3 Phase 5/6, or as a scripted attribute
substitution verified by `verify_markup_integrity.py --strict`. Check the CSS
first: rules written as `section#main` rather than `#main` would need updating.

**Effort:** S · **Risk of acting:** Low-Medium (462 files) ·
**Risk of not acting:** Low · **Dependencies:** P8 · **Status:** OPEN

---

## What Phase 6 did not find, so nobody re-audits it

- **Heading hierarchy is correct sitewide.** Exactly one `<h1>` on 463/463 pages;
  **zero** skipped heading levels anywhere.
- **Zero images anywhere are missing `alt`** — 309 images across the site.
- **Zero images are missing `width`/`height`** outside 3 on root pages, so there
  is no image-driven layout shift.
- **The body shell of the 166 notes pages is a single variant.** One wrapper
  chain, one script tail, one stylesheet set. Whatever else is true, the shell
  was not maintained carelessly.
- **`<title>` = `og:title` = `twitter:title` on 463/463.**
- **There are 0 occurrences of `{%` and 0 of `{{` across all 465 published HTML
  files**, so Jekyll front matter would not fail the deploy today. The risk is
  future, not present.
- **Every interactive component is runtime-`fetch()`-based and build-agnostic.**
  No option in §2 threatens the flashcards, the quiz, the glossary filter or the
  past-paper search.
