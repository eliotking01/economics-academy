# RECON — Revision Notes Consistency & Enrichment Pass

Phase 0 reconnaissance, carried out read-only. Written for a future session with no
memory of this one: everything needed to resume without re-deriving it.

**Scope of the pass:** the 166 revision-notes topic pages. Past-paper pages,
tutoring/marking pages, hub `index.html` pages and `macro-application/` are out of
scope except where explicitly noted.

---

## 1. Structure

**Static site, no build step.** Plain HTML served from the repo root; GitHub Pages
auto-publishes from `main` (see `CNAME`). 192 HTML files in total.

### Notes file inventory

| Directory | Topic pages | Hub | Naming |
| --- | ---: | --- | --- |
| `revision-notes/aqa-a2-micro/` | 54 | `index.html` | `1-x-y-slug.html` |
| `revision-notes/aqa-a2-macro/` | 25 | `index.html` | `2-x-y-slug.html` |
| `revision-notes/edexcel-theme-1/` | 22 | `index.html` | `1-x-y-slug.html` |
| `revision-notes/edexcel-theme-2/` | 24 | `index.html` | `2-x-y-slug.html` |
| `revision-notes/edexcel-theme-3/` | 20 | `index.html` | `3-x-y-slug.html` |
| `revision-notes/edexcel-theme-4/` | 21 | `index.html` | `4-x-y-slug.html` |
| **Total topic pages** | **166** | | AQA 79 / Edexcel 87 |

Also under `revision-notes/`: `index.html`, `macroeconomics-diagrams.html`,
`microeconomics-diagrams.html` (diagram galleries — the prior audit counted these as
note pages, which is where its "168" figure comes from), and
`macro-application/index.html` (out of scope, has its own compatibility stylesheet).

AQA pages use **site-local codes** `1.x.y` (micro) / `2.x.y` (macro), not real AQA
7136 codes (`4.1.x.x` / `4.2.x.x`). This is a deliberate, author-ratified decision —
see `docs/revision-notes-audit.md`. Do not raise it as a defect.

### How pages are assembled

Fully standalone HTML — **no templating, no includes, no build-time partials.**
Header and footer are injected **client-side at runtime**:

- Each page contains `<div id="header-placeholder"></div>` and
  `<div id="footer-placeholder"></div>`
- `js/components/inject-templates.js` `fetch()`es `/templates/header.html` and
  `/templates/footer.html` and replaces those divs via `outerHTML`
- Everything else — ~100 lines of head boilerplate, two JSON-LD blocks, the
  breadcrumb nav, and the body — is duplicated per file

Page shell, identical on all 166 topic pages:

```
<body class="is-preload"> → #page-wrapper → #header-placeholder
  → <section id="main" class="revision-notes-content"> → .container
    → nav.breadcrumb → .notes-container
      → <header class="major"><h1>…</h1></header>
      → <div class="spec-alert">…</div>
      → <section><h2>…</h2> … </section>   ×N
  → #footer-placeholder
```

Stylesheets: `/css/main.css` (site-wide) + `/css/pages/revision-notes-textbook.css`
(all note pages). MathJax 3 is loaded from CDN on 98 pages for `\[ … \]` display and
`\( … \)` inline maths.

---

## 2. Reference patterns — the house style

Derived from reading `aqa-a2-macro/2-1-3-uses-of-index-numbers.html`,
`2-1-4-uses-of-national-income-data.html` and
`2-4-1-the-structure-of-financial-markets-and-financial-assets.html` in full. These
are the author's exemplars.

### Exact markup — worked example

```html
<div class="worked-example">
  <h3>Worked Example: Building a House Price Index</h3>
  <p>Suppose the average house price … with <strong>2022 chosen as the base year</strong>:</p>
  <div class="table-container">
    <table class="concept-table">
      <thead><tr><th>Year</th><th>Average House Price</th><th>Index Number (2022 = 100)</th></tr></thead>
      <tbody>
        <tr><td><strong>2022 (base)</strong></td><td>£200,000</td>
            <td>\( \frac{200{,}000}{200{,}000} \times 100 = 100 \)</td></tr>
      </tbody>
    </table>
  </div>
  <p>An index of <strong>115</strong> in 2024 tells us that house prices are
     <strong>15% higher</strong> than in the base year of 2022.</p>
</div>
```

Two table idioms are in use inside worked examples, and they are **not**
interchangeable:

- `<div class="table-container"><table class="concept-table">` — a multi-column
  comparison (years × values × index). Always wrapped.
- `<table class="calculation-table">` — bare, **no** wrapper, two columns,
  label/value. CSS bolds the first column and highlights the last row as the answer.
  Used for a running vertical calculation (C, I, G, X−M → GDP).

`formula-box` divs are preceded by `<!-- prettier-ignore -->` and normally sit
**outside** the worked example, immediately before it.

### Exact markup — exam tip

```html
<div class="exam-tip">
  <p>
    <strong>Falling inflation is not falling prices.</strong> If the inflation rate
    falls from 3.5% to 2%, prices are still <em>rising</em> - just more slowly. This
    is <strong>disinflation</strong>. Prices only fall when the inflation rate turns
    negative, which is <strong>deflation</strong>.
  </p>
</div>
```

**No heading. A single `<p>`.** Opens with a bolded imperative or assertion sentence
(CSS renders `.exam-tip strong` in green), then 2–3 sentences of explanation. Never
a list in the exemplars.

### Inferred house style

| Dimension | Observation |
| --- | --- |
| Worked-example length | 45–75 source lines: intro sentence → table → interpretation paragraph. **Always ends by interpreting the number**, never on the arithmetic. |
| Worked-example title | `<h3>Worked Example: {Specific Thing}</h3>` — CSS strips the underline and colours it navy. |
| Exam-tip length | 3–5 lines, 40–70 words. |
| Exam-tip content | Always a **discrimination** — a distinction students conflate (coupon vs yield, disinflation vs deflation, base vs non-base % change) or a required method. Never restates theory. |
| Placement | Directly after the content it corrects, **inside** the relevant `<section>`. Never in a dedicated end-of-page section. |
| Frequency | The exemplars are the densest pages on the site: 2.1.3 and 2.1.4 each carry 3 worked examples + 2 tips; 2.4.1 carries 1 + 1. All three are heavily quantitative. |
| Register | UK English, £ sterling, hyphen `-` used as the dash character throughout (not en-dash). Curly apostrophes `’` appear in older Edexcel prose. |
| Emphasis inside components | Heavy `<strong>`; `<em>` reserved for logical contrast (`only`, `non-base`, `rising`, `increases`) and publication titles (`The Economist's`). |

### Current distribution of the two in-scope components

| Directory | `worked-example` | `exam-tip` |
| --- | ---: | ---: |
| `aqa-a2-micro` (54 pages) | **0** | **0** |
| `aqa-a2-macro` (25 pages) | 7 (in 3 files) | 8 (in 5 files) |
| `edexcel-theme-1` (22) | 0 | 22 (1 per page) |
| `edexcel-theme-2` (24) | 0 | 24 (1 per page) |
| `edexcel-theme-3` (20) | 0 | 20 (1 per page) |
| `edexcel-theme-4` (21) | 0 | 21 (1 per page) |

AQA macro files carrying components: `2-1-3` (2 tips / 3 WE), `2-1-4` (2/3),
`2-4-1` (1/1), `2-4-2` (2/0), `2-4-4` (1/0).

> **Key fact:** every one of the 87 Edexcel exam-tips is the sole content of that
> page's "Exam Preparation" section. Removing those sections removes every Edexcel
> exam tip on the site.

---

## 3. Component library

Every class defined in `css/pages/revision-notes-textbook.css`:

| Class | Rendered as | Uses in notes | Scope this pass |
| --- | --- | ---: | --- |
| `worked-example` | Navy left-rule card, "WORKED EXAMPLE" pill, navy `h3` | 8 | **IN SCOPE** |
| `exam-tip` | Green left-rule card, "EXAM TIP" pill, green `strong` | 96 | **IN SCOPE** |
| `spec-alert` | Purple card, "SPECIFICATION" pill | 169 | no |
| `evaluation-point` | Orange card, "EVALUATION" pill | 2 | out of scope |
| `application` | Grey card, "APPLICATION" pill | 1 | out of scope |
| `concept-table` | Striped table, hover states | 103 | markup only |
| `table-container` | Horizontal-scroll wrapper + mobile fade hint | 103 | markup only |
| `calculation-table` | 2-col calculation table, last row = answer | 3 | markup only |
| `key-definition` | Pink inline term chip | 639 | markup only |
| `content-example` | Green inline "Example:" chip | 6 | out of scope |
| `formula-box` | Centred MathJax display block | 51 | markup only |
| `flow-chain` / `flow-node` / `flow-node--end` / `flow-arrow` | Chained pill diagram | 15 | markup only |
| `diagram-figure` / `diagram-image` / `diagram-caption` | `<figure>` + `<figcaption>` | 300 | no |
| `coming-soon` | has CSS rules, **zero markup uses** | 0 | dead CSS |
| `chart-container` | **211 markup uses, no CSS rule anywhere** | 211 | dead markup |

`exam-note`, `exam-sentence`, `fact-line`, `subtopic-item` and
`application macro-card` appear only on `macro-application/index.html` and the hub
pages — never on a note page.

---

## 4. "Exam Preparation" sections

**87 instances. All on Edexcel topic pages. Zero on AQA.** Exactly one per Edexcel
topic page — no page has two, none is missing.

### Variants found

| Heading | Count | Files |
| --- | ---: | --- |
| `<h2>Exam Preparation</h2>` | 85 | across all four themes |
| `<h2>Exam Preparation:</h2>` | 1 | `edexcel-theme-1/1-2-8-producer-consumer-surplus.html` |
| `<h2>Exam Focus</h2>` | 1 | `edexcel-theme-1/1-2-9-indirect-taxes-subsidies.html` |

Searched for and **not found anywhere on the site**: "Exam Prep" (short form),
"Exam Technique", "Preparing for the Exam", "Exam Skills", "Exam Practice",
"Exam Advice", "In the Exam", "Assessment".

### Structure — uniform across all 87

```html
<section>
  <h2>Exam Preparation</h2>
  <div class="exam-tip">
    <ul> … </ul>     <!-- or <ol>; 2–7 <li>, typically 3 -->
  </div>
</section>
```

Verified by regex against all 87: **74 use `<ul>`, 13 use `<ol>`.** One page
(`edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html`) also
contains a `formula-box` inside the tip. **No page has anything else in the section.**

### Two representative examples

`edexcel-theme-1/1-1-1-economics-as-a-social-science.html:271`

```html
<section>
  <h2>Exam Preparation</h2>
  <div class="exam-tip">
    <ul>
      <li>You must be able to <strong>define</strong> and <strong>apply</strong>
          the term <strong>ceteris paribus</strong> to any economic model (e.g., demand, supply).</li>
      <li>Be prepared to <strong>evaluate</strong> the use of models, highlighting
          their simplifications and reliance on assumptions.</li>
      <li>Understand the core difference between economics (a social science) and
          the natural sciences, focusing on the inability to run true experiments.</li>
    </ul>
  </div>
</section>
```

`edexcel-theme-1/1-1-6-types-of-economies.html:323`

```html
<section>
  <h2>Exam Preparation</h2>
  <div class="exam-tip">
    <ol>
      <li><strong>Spectrum Thinking:</strong> View economies on a spectrum from
          'free market' to 'command', with 'mixed' in between. …</li>
      <li><strong>Evaluation:</strong> The debate centres on the trade-off between
          efficiency and equity. …</li>
      <li><strong>Application:</strong> Use real-world examples. E.g., the NHS
          (government provision) vs. the smartphone market (free market). …</li>
    </ol>
  </div>
</section>
```

These are generic coverage checklists — "you must be able to define X, evaluate Y" —
structurally and tonally the opposite of the AQA exemplar tips, which correct one
specific confusion in context.

### Removal-safety check — nothing references them

- **No `id` attribute** on any Exam Preparation section or heading. The only `id`s on
  note pages are `page-wrapper`, `main`, `header-placeholder`, `footer-placeholder`
  and `MathJax-script`. (`subtopic-N` and named section anchors exist only on hub and
  gallery pages.)
- **No in-page table of contents** on any topic page. All 16 `href="#…"` links under
  `revision-notes/` are on the two galleries and the hub pages, and every one targets
  a section id on that same page.
- **No sidebar nav.** Navigation is the injected `templates/header.html` only.
- **No cross-page fragment link** anywhere in the repo targets a note page.
- **`sitemap.xml`** lists page URLs only, no fragments.
- **No search index** exists — `js/data/` contains only `reviews.js`.

**Conclusion: removal is link-safe.**

> **The one trap.** On `edexcel-theme-1/1-1-5-specialisation-division-of-labour.html`
> the commercial CTA block is nested **inside** the Exam Preparation `<section>`
> rather than following it as a sibling. On the other 86 pages it is a sibling.
> Naive deletion of `<section>…</section>` on that file would delete the CTA with it.
> This is also why its CTA hashes differently from the other 86: one extra level of
> indentation, otherwise byte-identical.

---

## 5. Emphasis

| Tag | Uses across the 166 note pages |
| --- | ---: |
| `<strong>` | **4,831** |
| `<em>` | 12 |
| `<b>` / `<i>` / `<u>` / `<mark>` | 0 |

**`<strong>` is the settled convention** — key terms on first statement, list-item
lead-ins (`<strong>Durability:</strong> …`), and table row labels. `<b>` is styled
identically in CSS (`.revision-notes-content strong, .revision-notes-content b`) but
never appears in markup, so there is nothing to normalise away.

`<em>` is effectively unused: 12 instances, 10 of them on the three exemplar pages
plus the demand pair (`<em>ceteris paribus</em>`, `<em>only</em>`). The exemplars
show the intended use — logical contrast words and publication titles.

### Measuring it

Raw `<strong>` density is a **misleading** metric on its own, because
`key-definition` chips do the same job on some pages. `aqa-a2-micro/1-2-3` has one
`<strong>` in 4,187 characters — worst on the site by raw count — but carries 10
`key-definition` chips, so its key terms are in fact marked. The honest signal is
**(`<strong>` + `key-definition`) per 1,000 characters of visible text**, measured
with the Exam Preparation section excluded so Edexcel pages are not flattered.

Combined median: **6.12**. The 25 weakest pages:

| # | Combined | `strong` | `key-def` | chars | Page |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 1.31 | 1 | 3 | 3051 | `edexcel-theme-2/2-2-2-consumption.html` |
| 2 | 1.60 | 3 | 0 | 1870 | `edexcel-theme-4/4-4-1-role-of-financial-markets.html` |
| 3 | 2.00 | 14 | 3 | 8488 | `aqa-a2-micro/1-8-7-competition-policy.html` |
| 4 | 2.34 | 18 | 4 | 9409 | `edexcel-theme-4/4-3-3-strategies-influencing-growth-development.html` |
| 5 | 2.49 | 8 | 0 | 3210 | `aqa-a2-micro/1-3-6-the-interrelationship-between-markets.html` |
| 6 | 2.63 | 1 | 10 | 4187 | `aqa-a2-micro/1-2-3-aspects-of-behavioural-economic-theory.html` |
| 7 | 2.74 | 11 | 5 | 5833 | `aqa-a2-micro/1-8-8-public-ownership-privatisation-regulation-and-deregulation-of-markets.html` |
| 8 | 2.82 | 9 | 0 | 3192 | `edexcel-theme-2/2-2-5-net-trade.html` |
| 9 | 3.34 | 21 | 1 | 6585 | `edexcel-theme-4/4-1-1-globalisation.html` |
| 10 | 3.45 | 21 | 1 | 6382 | `aqa-a2-macro/2-6-1-globalisation.html` |
| 11 | 3.49 | 9 | 1 | 2862 | `edexcel-theme-4/4-4-3-role-of-central-banks.html` |
| 12 | 3.60 | 15 | 4 | 5279 | `edexcel-theme-4/4-3-2-factors-influencing-growth-development.html` |
| 13 | 3.73 | 26 | 1 | 7230 | `edexcel-theme-4/4-5-4-macroeconomic-policies-in-a-global-context.html` |
| 14 | 3.78 | 9 | 0 | 2380 | `aqa-a2-micro/1-6-4-wage-determination-imperfectly-competitive-labour-markets.html` |
| 15 | 3.82 | 28 | 2 | 7847 | `edexcel-theme-3/3-4-4-oligopoly.html` |
| 16 | 3.83 | 6 | 1 | 1827 | `aqa-a2-micro/1-5-8-the-dynamics-of-competition-and-competitive-market-processes.html` |
| 17 | 3.94 | 16 | 2 | 4574 | `aqa-a2-macro/2-1-2-macroeconomic-indicators.html` |
| 18 | 3.96 | 10 | 0 | 2527 | `aqa-a2-micro/1-7-3-government-policies-poverty-income-distribution.html` |
| 19 | 4.03 | 23 | 4 | 6703 | `edexcel-theme-3/3-3-3-economies-diseconomies-of-scale.html` |
| 20 | 4.04 | 4 | 2 | 1484 | `aqa-a2-micro/1-4-8-technological-change.html` |
| 21 | 4.08 | 23 | 4 | 6616 | `aqa-a2-micro/1-4-5-economies-and-diseconomies-of-scale.html` |
| 22 | 4.09 | 11 | 1 | 2935 | `edexcel-theme-1/1-1-1-economics-as-a-social-science.html` |
| 23 | 4.11 | 10 | 3 | 3160 | `aqa-a2-micro/1-5-7-price-discrimination.html` |
| 24 | 4.20 | 7 | 7 | 3333 | `edexcel-theme-1/1-2-10-alternative-views-of-consumer-behaviour.html` |
| 25 | 4.21 | 8 | 9 | 4041 | `aqa-a2-micro/1-8-6-market-imperfections.html` |

**Emphasis used well** (top of the distribution, useful as style references):
`edexcel-theme-1/1-2-9-indirect-taxes-subsidies`, `edexcel-theme-3/3-3-1-revenue`,
`aqa-a2-micro/1-4-6-marginal-average-and-total-revenue`,
`edexcel-theme-3/3-4-1-efficiency`, `edexcel-theme-1/1-2-6-price-determination`.

---

## 6. Bottom-of-page CTAs

### Edexcel topic pages — 87, byte-identical

Only `1-1-5-specialisation-division-of-labour.html` differs, by one extra level of
indentation (it sits inside the Exam Prep section).

```html
            <div
              style="
                margin-top: 2.5em;
                padding: 1.5em;
                background: #f8f8f8;
                border-left: 4px solid #d52349;
                border-radius: 4px;
                text-align: center;
              "
            >
              <p
                style="
                  margin: 0 0 1em;
                  font-weight: 600;
                  font-family: &quot;Open Sans&quot;, sans-serif;
                "
              >
                Ready to apply these notes?
              </p>
              <a
                href="/past-papers/edexcel/index.html"
                class="button alt"
                style="margin: 0.3em"
                >Edexcel Past Papers</a
              >
              <a href="/marking.html" class="button alt" style="margin: 0.3em"
                >Get Essays Marked</a
              >
              <a href="/tutoring.html" class="button" style="margin: 0.3em"
                >Book a Free Intro Call</a
              >
            </div>
```

| # | Copy | `href` | Class |
| --- | --- | --- | --- |
| 1 | **Edexcel Past Papers** | `/past-papers/edexcel/index.html` | `button alt` |
| 2 | Get Essays Marked | `/marking.html` | `button alt` |
| 3 | Book a Free Intro Call | `/tutoring.html` | `button` |

**CTA #1 is the past-papers link.** The AQA equivalent it must point to is
**`/past-papers/aqa/index.html`** — confirmed present at `past-papers/aqa/index.html`
(alongside `a-level/paper-1|2|3/` and `as-level/`), and already the destination used
by the AQA hub pages.

### AQA topic pages — 79, no CTA at all

The AQA **hub** pages do already carry a three-button block, in a different layout
(`.row` / `.col-4 col-12-medium`, `style="width: 100%"`) with the copy
**AQA Past Papers** · **Paper Marking** · **Book a Free Intro Call**.

### Diagram galleries — already board-neutral

Both galleries carry the same inline-styled block but with
`href="/past-papers/index.html"` and the label **"Past Papers"**. They are **not**
Edexcel-specific and need no link or copy change — markup conversion only.

### Link totals under `revision-notes/`

91 × `/past-papers/edexcel/index.html` (87 topic pages + 4 theme hubs),
2 × `/past-papers/aqa/index.html` (AQA hubs), 2 × `/past-papers/index.html`
(galleries), 96 × `/marking.html`, 96 × `/tutoring.html`.

---

## 7. Tooling

**There is no build, no lint, no HTML validation and no test step.**

- No `package.json`, no `node_modules`, no `Makefile`, no CI (`.github/` is absent),
  no active git hooks. The only build-adjacent file is `scripts/convert_raw_notes.py`,
  a one-off converter for `raw-notes/`.
- **Prettier has been used** — `docs/revision-notes-audit.md` records "Prettier 3.9.6
  reports all changed files clean", and 11 files carry `<!-- prettier-ignore -->` —
  but it is **not installed** and there is no `.prettierrc`. Run it as
  `npx prettier@3.9.6` (Node v22.19.0 and npx 10.9.3 are available).
- Python 3.12 is available with **the standard library only**. `bs4`, `lxml` and
  `html5lib` are **not** installed. Verification scripts must use `html.parser`,
  which is what the prior audit used.

**A validator therefore has to be written for Phase 3** — three stdlib-only Python
scripts (well-formedness, text integrity, link/anchor resolution).

### Findings from the tooling check

- **All 103 `concept-table`s are already wrapped** in `table-container`. There is no
  mobile-scroll gap to close. The 3 `calculation-table`s are deliberately unwrapped,
  matching the exemplars.
- **28 of the 51 `formula-box` divs lack a preceding `<!-- prettier-ignore -->`**, so
  a future Prettier run can reflow their LaTeX.
- **12 display formulas are already broken across source lines** by past reflow.
  Ten are cosmetically harmless (LaTeX collapses whitespace between brace groups).
  **Two render a spurious leading space** because the break falls inside a `\text{}`
  group — `\text{ Injection}`:
  - `aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html:202`
  - `edexcel-theme-2/2-4-4-the-multiplier.html:198`

---

## 8. Prior work — read before changing anything

`docs/revision-notes-audit.md` (511 lines) records a two-phase audit already merged
from `chore/revision-notes-audit`. It **already fixed** the following; do not redo:

- Heading hierarchy — exactly one `<h1>` per page, no skipped levels, no `<h4>` in
  bodies (`h2`→`h1`, `h3`→`h2`, `h4`→`h3`, with the stylesheet shifted to match)
- All 300 images — `width`/`height`, `loading="lazy"` (except first-per-page), and
  rewritten alt text. **Zero images lack alt.**
- Titles and meta descriptions to SEO length; `lang="en-GB"`; canonical, Open Graph
  and Twitter cards; JSON-LD `LearningResource` + `BreadcrumbList` on every page
- 156 contextual note-to-note internal links (capped at 3 per page, never cross-board)
- British English spellings, bare `&` escaped, all breadcrumbs starting at Home

### Open flags from that audit, relevant here

- **C1** — `edexcel-theme-1/1-2-4-supply.html` and its AQA twin
  `aqa-a2-micro/1-3-3-…supply…html`: the Figure 1 caption transposes extension and
  contraction. **Still open.** An economics error — log it, never fix it.
- **W1** — `aqa-a2-macro/2-3-1-…html:562`, `<h2>The Trade Cycle?</h2>`, stray question mark
- **F1–F4** — four figure captions that contradict their own diagram
- **S1** — the CTA asymmetry this pass fixes. The audit explicitly declined it
  because it required writing new prose, which was outside its scope.
- **S5** — 629 inline `style` attributes, only 17 distinct values, 4 accounting for 530
- **S6** — dead CSS: `chart-container` (211 uses, no rule), `.coming-soon` (rules, no markup)

---

## 9. Decisions taken for this pass

| # | Decision |
| --- | --- |
| D1 | Exam Preparation: **delete the whole `<section>`**, `h2` and `exam-tip` included, on all 87 pages. |
| D2 | **Extract a `.notes-cta` class**; use it for the 79 new AQA blocks *and* convert the 87 Edexcel ones. |
| D3 | Enrichment planned in **6 batches by directory**, presented one at a time. |
| D4 | Emphasis work **targets the ~25 weakest pages** (§5 table); the other ~140 are untouched. |
| D5 | Diagram galleries: **convert markup to `.notes-cta`**, no link or copy change (they are already board-neutral). |
| D6 | **One accent colour `#d52349`** for all CTAs — a single rule, no board modifier. |
| D7 | Approved additional work: remove the 211 dead `chart-container` wrappers; add `<!-- prettier-ignore -->` to the 28 unprotected `formula-box` divs. **Not approved:** extracting the remaining inline styles; section-ordering normalisation. |

Working assumptions: the 7 hub `index.html` pages are entirely out of scope;
`Exam Preparation:` and `Exam Focus` are treated identically to `Exam Preparation`;
the 2-component cap applies to *additions* only, so the three exemplar pages get
nothing.
