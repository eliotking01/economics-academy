# Revision Notes Audit

Full record of the audit carried out on `/revision-notes/` on branch
`chore/revision-notes-audit`.

**Scope:** 168 note pages — 54 `aqa-a2-micro`, 25 `aqa-a2-macro`, 22 `edexcel-theme-1`,
24 `edexcel-theme-2`, 20 `edexcel-theme-3`, 21 `edexcel-theme-4`, plus
`macroeconomics-diagrams.html` and `microeconomics-diagrams.html`.
The 7 `index.html` hub pages were out of scope and **none was modified**.

**Files changed:** 171 — 168 note pages, 2 stylesheets, `sitemap.xml`.

---

## Specifications in use

**Edexcel — Economics A (9EC0).** Themes 1–4, with Theme 3 covering monopsony and
contestability and Theme 4 titled "A Global Perspective". The codes in the
`spec-alert` blocks are genuine 9EC0 codes and match the filenames.

**AQA — Economics (7136), but the site does not use real AQA codes.** AQA 7136 numbers
its content `4.1.x.x` (Individual markets and market failure) and `4.2.x.x` (The
national and international economy). The site uses `1.x` for micro and `2.x` for
macro and labels them "AQA unit 1.5.10". The mapping is a clean shift —
site `1.x` = AQA `4.1.x`, site `2.x` = AQA `4.2.x` — so the content is organised
correctly and only the codes are wrong.

**Decided: leave as-is.** Renumbering would change filenames, URLs, page titles,
breadcrumbs and the sitemap. The author has reviewed this and chosen to keep the
existing numbering, so it should not be raised again as a defect.

---

## Before / after

| Metric                                  | Before |                           After |
| --------------------------------------- | -----: | ------------------------------: |
| Pages with no `<h1>`                    |     81 |                               0 |
| Pages skipping a heading level          |     87 |                               0 |
| `<h4>` in note bodies                   |    509 |                               0 |
| Duplicate intro paragraphs              |     87 |                               0 |
| Invalid JSON-LD blocks                  |      1 |                               0 |
| Pages with no canonical / OG / Twitter  |      7 |                               0 |
| Images with no width/height             |    300 |                               0 |
| Images without `loading="lazy"`         |    211 | 94 (first-per-page, deliberate) |
| Bare unescaped `&`                      |     64 |                               0 |
| Pages with `noindex`                    |      1 |                               0 |
| Sitemap entries not resolving to a file |      1 |                               0 |
| HTML parse errors                       |      0 |                               0 |
| Broken links / anchors (785 checked)    |      0 |                               0 |

---

## What changed, commit by commit

### 1. Duplicate intro paragraphs removed (87 files)

Every Edexcel note page carried a centred, inline-styled paragraph between the
`<h1>` and the `spec-alert` block, restating what the notes covered. No AQA page
had one. The markup was byte-identical across all 87, so a single fixed pattern
removed them all.

> A naive `grep "color: #5d5d5d"` matches 88 files. The 88th,
> `aqa-a2-micro/1-5-1-market-structures.html`, is a false positive — that colour
> is in a page-local `<style>` block for the competition-spectrum diagram. It was
> not touched.

**Harvesting.** 45 of the 87 paragraphs named concepts the spec block did not.
Those terms were appended to that page's existing `spec-alert` as a trailing
sentence beginning "These notes also cover …" before the paragraph was deleted.
Append-only: no existing spec wording was rewritten and no spec code altered.
The other 42 paragraphs added nothing beyond the spec block and were simply removed.

Pages harvested: 1.1.4, 1.1.5, 1.1.6, 1.2.1, 1.2.4, 1.2.8, 1.2.10, 1.3.3, 1.4.1,
1.4.2, 2.1.1, 2.2.2, 2.2.3, 2.3.1, 2.3.2, 2.3.3, 2.4.1, 2.5.1, 2.5.2, 2.5.3, 2.5.4,
3.1.1, 3.1.3, 3.3.2, 3.4.3, 3.4.4, 3.4.5, 3.4.6, 3.5.2, 3.6.1, 4.1.1, 4.1.3, 4.1.7,
4.1.9, 4.2.1, 4.2.2, 4.3.2, 4.3.3, 4.4.1, 4.4.2, 4.4.3, 4.5.1, 4.5.2, 4.5.3, 4.5.4.

### 2. Heading hierarchy (166 files + 2 stylesheets)

Every page failed heading structure, differently by board — 81 pages had no `<h1>`
at all, and 87 had an `<h1>` then skipped to `<h3>`.

- 81 page titles promoted `h2` → `h1`
- 793 section headings `h3` → `h2`
- 509 sub-headings `h4` → `h3`

`revision-notes-textbook.css` shifted its body-heading styles up one level so the
new `h2` renders exactly as the old `h3` and the new `h3` exactly as the old `h4`.

**macro-application.** `revision-notes/macro-application/index.html` is out of scope
but shares the same container classes and stylesheet. A compatibility block in
`css/pages/macro-application.css` — loaded only by that page, and after the textbook
CSS — restores its previous `h2`/`h3`/`h4` appearance, including at 768px and 480px.
No markup on that page was changed and it is pixel-identical to before.

### 3. British English and spelling (60 files, 119 fixes)

30 American spellings, 73 misspellings across 42 distinct words, 4 doubled words,
2 verb uses of "practice" → "practise", 10 spaces before punctuation.

Replacements were word-boundary anchored and confined to visible text nodes, so
attributes, class names, scripts and LaTeX notation were untouched. The single
exception is `\text{Labor Force}` in the unemployment-rate formula, where the
spelling renders as prose to students.

Most defects came in AQA/Edexcel twin pairs, because the two sets of pages were
copy-pasted from one another.

### 4. High-severity SEO defects (14 files)

- **`noindex` removed** from `aqa-a2-macro/2-1-4-uses-of-national-income-data.html`.
  Its own TODO said to drop it once the notes existed; the page is complete
  (547 lines, three sections, five tables) and was listed in the sitemap, so it was
  advertised to crawlers and then hidden from them.
- **Invalid JSON-LD fixed** in `aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html`
  — a missing comma made Google discard the whole `LearningResource` block.
- **Canonical, Open Graph, Twitter card and `LearningResource` added** to the 7 pages
  that had none: `edexcel-theme-2/` 2-2-1, 2-3-1, 2-4-3, 2-5-1, 2-6-2, and both
  diagram collections.
- **Sitemap:** corrected the stale `1-2-5-price-income-cross-elasticities-of-supply`
  entry (no such file) to the real `1-2-5-price-elasticity-of-supply`, and added the
  omitted `privacy.html`. All 188 entries now resolve to files on disk.

### 5. AQA structured data (79 files)

All 54 `aqa-a2-micro` pages claimed `isPartOf.name` = "AQA A-Level Economics **Theme 1**:
Introduction to Markets and Market Failure" — the Edexcel Theme 1 course title with the
board swapped. AQA has no "Themes", and the claim was wrong for the 1.4–1.8 pages, which
cover firms, labour markets and market failure. One page also had a stray
`| Economics Academy` inside the value. The 25 `aqa-a2-macro` pages declared no course
association at all.

Both now use real AQA 7136 section names:

- `aqa-a2-micro` → AQA A-Level Economics: Individual Markets and Market Failure
- `aqa-a2-macro` → AQA A-Level Economics: The National and International Economy

Also corrected `aqa-a2-micro/1-5-3-perfect-competition.html`, whose spec-alert read
"Edexcel unit 1.5.3" on an AQA page — code and title were already right, so only the
board name changed.

### 6. Images (48 files, 300 images)

- **width and height** added to all 300 images, read from each PNG's own header.
  `.diagram-image` already sets `max-width:100%` and `height:auto`, so the images
  remain responsive; the attributes only reserve the correct aspect ratio and remove
  layout shift.
- **`loading="lazy"`** added to 117 images. The first image on each page is left
  eager so the largest contentful paint is not delayed.
- **115 alt attributes rewritten.** Ten diagrams claimed to be "PPF diagram showing
  long-run growth" while actually showing Phillips curves, AD shifts, output gaps and
  the trade cycle; six demand and supply diagrams shared one "diagram template"
  description; `trade-union.png` was described as a monopsony. Alt text is now keyed to
  the diagram itself — no two different diagrams share a description, and none is
  shorter than 20 characters.

### 7. Bare ampersands (29 files, 64 occurrences)

Ampersands in headings and table cells ("Reason & Example", "R&D", "Economic Growth &
Decline") escaped to `&amp;`. No visible rendering change.

---

## Economics content — flagged, and what was decided

### C1 — Supply diagram caption is inverted — STILL OPEN

**`edexcel-theme-1/1-2-4-supply.html` lines 199–204**, and its AQA twin
**`aqa-a2-micro/1-3-3-the-determinants-of-the-supply-of-goods-and-services.html`
lines 210–215.** This is the caption on **Figure 1**, the `supply-curve-movement.png`
diagram — not Figure 2, the shift diagram directly below it.

> "Figure 1: … A movement from point B to A shows a **'Contraction in QS' due to a
> price rise**. A movement from point A to B shows an **'Extension in QS' due to a
> price fall**."

The two causes are transposed. Supply slopes upward, so a price **rise** causes an
extension and a price **fall** causes a contraction. Fifteen lines below, the bullet
list states it correctly:

> **Extension in QS:** A rise in price leads to a movement up the curve (A → B).
> **Contraction in QS:** A fall in price leads to a movement down the curve (A → C).

So the caption contradicts the bullets beneath it. It reads plausibly because
"contraction due to a price rise" _is_ correct on the **demand** page — the caption
appears to have been copy-pasted from there without flipping the sign.

Secondary point: the caption names only points A and B, while the bullets use
A → B and A → C.

### C2 — Supernormal profit given as `P > C` rather than `P > AC` — FIXED

`edexcel-theme-3/3-4-1-efficiency.html` (figure caption + body) and its AQA twin
`aqa-a2-micro/1-5-10-market-structure-efficiency-resource-allocation.html`.
`C` was undefined on the page and `P > MC` appears two lines earlier in the same
caption as the allocative inefficiency condition, so a student could reasonably read
`C` as marginal cost. Corrected to `P > AC` in all four places.

### C3 — `aqa-a2-micro/1-4-7-profit.html` spec block was the wrong topic — FIXED BY AUTHOR

Read "Edexcel unit 3.3.4 - Normal Profits, Supernormal Profits and Losses" on a page
headed "1.4.7 Profit" — the block had been pasted wholesale from
`edexcel-theme-3/3-3-4`. Rewritten by the author as "AQA unit 1.4.7 - Profit".

### C4 — Two AQA pages cross-reference Edexcel theme numbers

`aqa-a2-macro/2-2-3-the-determinants-of-aggregate-demand.html` ("see Theme 4.1.8
Exchange Rates") and `aqa-a2-micro/1-5-6-monopoly-and-monopoly-power.html` ("explored
further in Theme 3.6.1"). Those codes do not exist in the specification the student on
that page is following.

### C5 — Unemployment-rate denominator

`aqa-a2-macro/2-1-2-macroeconomic-indicators.html`. The spelling was corrected to
"Labour Force"; worth confirming the denominator matches the ONS/ILO "economically
active" definition given a few lines above.

### C6 — Real GDP growth stated as an identity

Same file: `% Change in Real GDP = % Change in Nominal GDP − Inflation Rate` is an
approximation valid at low inflation. Standard at A-Level, so probably intentional.

All 67 other display formulas checked out — AD = C+I+G+(X−M), the multiplier, MV = PQ,
MRP, Gini, Marshall-Lerner, terms of trade, and the PED/YED/XED/PES ranges.

### Other items flagged, not changed

- **"program" vs "programme"** — 22 occurrences, all policy contexts ("welfare
  programs", "training programs") where British English would prefer "programme".
  An editorial call rather than a mechanical fix.

---

## Known visual change

Promoting the 79 AQA page titles from `h2` to `h1` means they no longer pick up
`css/main.css`'s `header.major h2` rule, which applied `top: -0.65em` and `padding: 0 1em`.
AQA titles therefore sit about 10px lower and their teal underline is 2em narrower —
they now render exactly like the 87 Edexcel titles, which are unchanged.

That rule is a vestige of a design where `header.major` had a `border-top` for the title
to sit on; the revision-notes stylesheet removes that border with `border: none !important`,
so the offset no longer serves a purpose. Converging on the Edexcel rendering leaves the
larger set of pages untouched and drops the artefact.

**If you prefer the old AQA look instead**, add these three declarations to the
`header.major h1, header.major h2` rule in `css/pages/revision-notes-textbook.css`
(around line 41). All 166 titles will then match the old AQA rendering:

```css
position: relative;
top: -0.65em;
padding: 0 1em 0.5em 1em;
```

---

## Verification

- **HTML** — all 168 files parsed with Python `html.parser`: 0 mismatched tags,
  0 duplicate IDs, before and after.
- **Headings** — every page has exactly one `<h1>`, no level skips, no `<h4>` in bodies.
- **JSON-LD** — all 336 blocks parse; `isPartOf.name` resolves to exactly six values,
  one per directory.
- **Links** — 785 anchors resolved against the filesystem: 0 broken hrefs, 0 broken
  fragments, 0 missing local assets.
- **Images** — all 300 declare width and height, and every declared dimension was
  checked against the real PNG header.
- **Sitemap** — 188/188 entries resolve to files on disk.
- **Formatting** — Prettier 3.9.6 reports all changed files clean, except one
  pre-existing `transition:` line in `macro-application.css` that predates this work.
- **Visual regression** — headless Chrome, five pages at 1440/768/480px, compared
  against a worktree of `main`:
  - Edexcel note pages differ only from the point where the intro paragraph was removed.
  - AQA note pages differ only in the title band (see "Known visual change").
  - `macro-application/index.html` is **pixel-identical at all three widths**.
  - Note: inline MathJax renders non-deterministically between runs. The same unmodified
    page screenshotted twice differs in its formula regions, so those bands are
    rendering noise, not a change introduced here.

---

## Recommended next steps

Reported here but **not** actioned, in rough priority order.

1. **C1 — the inverted supply caption is the one economics error still outstanding.**
   C2 has been corrected and C3 was fixed by the author.
2. **Titles and meta descriptions.** 163 of 168 titles exceed 70 characters (max 172)
   and 156 of 168 descriptions exceed 160 (max 323), so almost all truncate in search
   results. The boilerplate suffix `| <Board> A-Level Economics Revision Notes |
Economics Academy` is 55–58 characters on its own. One exact duplicate title pair
   (`2-1-4-balance-of-payments` and `4-1-7-balance-of-payments`). AQA titles lead with
   the spec code, Edexcel titles never do.
3. **Internal linking.** 166 of 168 pages have no contextual link to any other note
   page — every note is a dead end. Separately, no AQA page links to tutoring, marking
   or past papers, while all 87 Edexcel pages link to all three; `past-papers/aqa/`
   exists but is never linked.
4. **Image weight.** `/images/diagrams/` is 25.9 MB across 112 files, 71 of them over
   200 KB (largest `trade-union.png` at 774 KB), with no WebP/AVIF and no `srcset`.
   `microeconomics-diagrams.html` alone ships 11.6 MB. This is now the biggest Core Web
   Vitals problem left. Seven diagram files are unused by any page.
5. **`lang="en-GB"`.** All 168 pages declare `lang="en"`; `og:locale` is absent
   site-wide, as are `twitter:title` and `twitter:description`.
6. **Sitemap `lastmod`.** All 188 entries are frozen at `2026-05-13`, so the field
   carries no freshness signal.
7. **Inline styles.** 629 `style` attributes but only 17 distinct values; four account
   for 530 of them. Extracting those into classes would remove most in one pass.
   Recommended, not done — it is a structural change.
8. **Dead CSS.** `chart-container` is used 211 times with no rule anywhere;
   `.coming-soon` has rules but no markup uses it; `.evaluation-point` has 7 rules and
   2 uses.
   **Not on this list:** AQA spec renumbering. The author has reviewed it and decided to
   keep the current numbering — see "Specifications in use" above.

---

# Phase 2 — SEO

Carried out on branch `chore/revision-notes-audit`, in three reviewed waves.
**172 files changed:** 168 note pages, `sitemap.xml`, and three manifests under
`docs/`. No `index.html` hub page was modified.

Each wave produced a manifest for review first, then applied it verbatim.

- `docs/seo-manifest-head.csv` — 168 rows
- `docs/seo-manifest-images.csv` — 300 rows
- `docs/seo-manifest-links.csv` — 156 rows

## Before / after

| Metric                                  | Before |              After |
| --------------------------------------- | -----: | -----------------: |
| Titles over 70 characters               |    163 |              **0** |
| Longest title                           |    172 |             **64** |
| Duplicate titles                        | 1 pair |              **0** |
| Meta descriptions over 160 characters   |    156 |              **0** |
| Longest description                     |    323 |            **160** |
| Descriptions in the 150–160 band        |      5 |            **168** |
| Pages declaring `lang="en-GB"`          |      0 |            **168** |
| `og:locale` / `og:site_name`            |      0 |            **168** |
| `twitter:title` / `twitter:description` |      0 |            **168** |
| Diagrams with more than one alt string  |     57 | **1** (deliberate) |
| Note-to-note contextual links           |      0 |            **156** |
| Pages with only one inbound link        |    121 |             **94** |
| Orphan pages                            |      0 |              **0** |
| Breadcrumb trails starting at Home      |     79 |            **168** |
| Sitemap entries with a real `lastmod`   |      0 |            **188** |
| Broken links                            |      0 |              **0** |

## Wave 1 — head metadata

Titles now follow `{Board} A-Level Economics {code} {Topic}`. The requested
`| Revision Notes` suffix was dropped: the pattern was impossible at the target
length, because the chrome alone came to 49 characters. 60 topic names are
shortened **for the title only** — every `<h1>` and all body text is unchanged.

All 168 titles and all 168 descriptions are unique site-wide. Where the two
boards cover the same concept the descriptions differ on emphasis rather than
being paraphrases; the previously-duplicated balance-of-payments pair is now
clearly distinct.

`og:title` and `og:description` were resynced to the new strings so social
previews match the page. Head block order was checked across all 168 pages and
was already identical everywhere, so no reordering was needed.

**Canonical domain** is `https://economicsacademy.co.uk` — one scheme, no www
variant, matching `CNAME` and every sitemap entry. All 168 canonicals were
checked against their own page: zero mismatches.

## Wave 2 — diagram alt text

300 images across 95 pages. Alt text now states what each diagram shows
economically — the direction of the change and its consequence — instead of
naming the diagram.

57 of the 104 diagrams previously carried two or more competing alt strings
depending on which page they appeared on. Each now has exactly one. The single
exception is `sales-max.png`, which legitimately illustrates sales maximisation
on the business-objectives pages and limit pricing on the two contestability
pages.

**Five alts described the wrong economics.** Each was checked against the
rendered PNG before rewriting:

| Diagram                    | What the alt claimed                              | What the image shows                                                               |
| -------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `joint-demand`             | a rise in demand raises demand for the complement | a car **price** rise contracts quantity demanded and shifts petrol demand **left** |
| `derived-demand`           | a rise in demand for the final good               | both panels shift **left**; the wage falls                                         |
| `total-utility`            | total **and marginal** utility                    | only a total utility curve is drawn                                                |
| `surplus-demand-increase`  | first panel producer surplus                      | the first panel is **consumer** surplus                                            |
| `classical-ad-shift-right` | both Classical and Keynesian                      | the Classical panel only                                                           |

No decorative images exist, so nothing was given `alt=""`. All 300 retain
`width` and `height`.

## Wave 3 — links, breadcrumbs, sitemap

**156 contextual links across 92 pages**, capped at 3 per page and never
crossing between boards. Every link wraps words that were already in the prose.
This was verified by stripping all markup from all 168 pages and diffing the
visible text against the previous commit: **0 pages read differently**.

76 pages received no link, because no natural anchor existed on them. The 2
diagram collections remain the most-linked destinations alongside the efficiency
and cost pages.

**Breadcrumbs:** the 87 Edexcel pages and 2 diagram pages began their trail at
Revision Notes while all 79 AQA pages began at Home. All 168 now start at Home,
with the visible nav and the `BreadcrumbList` JSON-LD updated together and
`position` renumbered. Verified: 168/168 trails agree between nav and JSON-LD.

**Sitemap:** coverage was already correct — all 188 entries resolve to a file,
and the only HTML not listed is `404.html` and `confirmation.html`, both rightly
excluded. Nothing was added or removed. Every entry now carries the real commit
date of the file it points at, replacing the single frozen `2026-05-13`.
`robots.txt` was checked and left unchanged.

**Headings:** verified only. All 168 pages already had exactly one `<h1>`, no
skipped levels and no `<h4>` in the body, from Phase 1.

**`FAQPage` was not added anywhere.** No page legitimately qualifies: there is
no FAQ section, no `<dt>` and no `<summary>` in scope. The 28 question-shaped
`<h2>` headings introduce ordinary prose; using them would be exactly the
manufactured Q&A to avoid. The real FAQ content lives in `faq.html`.

## Verification

- **HTML** — all 168 parse; 0 mismatched tags, 0 duplicate IDs
- **Manifest fidelity** — 168/168 titles, 168/168 descriptions and 300/300 alts
  match their manifest cell byte-for-byte
- **Uniqueness** — 168 unique titles, 168 unique descriptions
- **JSON-LD** — all 336 blocks parse; breadcrumb positions contiguous from 1
- **Links** — 1030 anchors resolved: 0 broken hrefs, 0 broken fragments
- **Images** — 300/300 keep `width`/`height`; no empty alt
- **Sitemap** — 188/188 resolve; all `lastmod` well-formed
- **Prettier 3.9.6** — clean on every changed file
- **Visual regression** — headless Chrome at 1440px and 480px against the
  pre-Phase-2 commit. Wave 1 was pixel-identical, as expected for head-only
  changes. The only differences after Wave 3 are the added Home breadcrumb and
  the underline on newly linked words. `macro-application/index.html`, which is
  out of scope, is **pixel-identical**.

## Deliberate decisions worth knowing

1. **Commercial links untouched.** Normalising the 87 Edexcel CTA blocks was
   considered and rejected once it emerged that **no page mentions past papers,
   tutoring, marking or essays anywhere in its prose** — so "wrap existing
   words" would have removed all 267 commercial links and replaced them with
   none. The blocks stay as they are. The board asymmetry therefore persists:
   87 Edexcel pages carry 3 commercial links each, 79 AQA pages carry none,
   and `/past-papers/aqa/` is still never linked from an AQA note page.
2. **4 titles run to 61–64 characters** rather than ≤60, to keep the exact
   phrase students search for: `Production Possibility Frontiers`,
   `Consumer and Producer Surplus`, `International Competitiveness`,
   `Absolute and Relative Poverty`.
3. **The 2 diagram gallery pages keep `loading="lazy"` on their first image**,
   unlike the other 94 image-bearing pages. Their above-the-fold content is a
   heading, a scope note and a contents list, so the first image is not the
   largest contentful paint element.
4. **Cross-board links were not used.** An AQA student has no reason to open an
   Edexcel page, and linking the two would put near-identical pages in
   competition for the same query.

---

# Flag list — everything left for the author

Nothing in this section has been changed. Grouped by type, most important first.

## A. Economics content

| #      | Where                                                                                                                  | Issue                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------ | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **C1** | `edexcel-theme-1/1-2-4-supply.html` and `aqa-a2-micro/1-3-3-the-determinants-of-the-supply-of-goods-and-services.html` | **Still open.** The **Figure 1** caption (the `supply-curve-movement.png` diagram, not Figure 2 below it) transposes the two causes: it pairs _contraction_ with a price rise and _extension_ with a price fall. Supply slopes upward, so a price rise causes an extension. The bullet list 15 lines below states it correctly, so the page contradicts itself. It reads plausibly because that pairing **is** correct on the demand page, which is where it appears to have been copied from. The caption also names only points A and B while the bullets use A → B and A → C. |
| **C4** | `aqa-a2-macro/2-2-3-the-determinants-of-aggregate-demand.html`, `aqa-a2-micro/1-5-6-monopoly-and-monopoly-power.html`  | Both cross-reference _Edexcel_ theme numbers — "see Theme 4.1.8 Exchange Rates" and "explored further in Theme 3.6.1" — which do not exist in the specification the student on that page is following.                                                                                                                                                                                                                                                                                                                                                                           |
| **C5** | `aqa-a2-macro/2-1-2-macroeconomic-indicators.html`                                                                     | The unemployment-rate formula denominator now reads "Labour Force" (spelling corrected in Phase 3). Worth confirming it matches the ONS/ILO "economically active" definition given a few lines above.                                                                                                                                                                                                                                                                                                                                                                            |
| **C6** | `aqa-a2-macro/2-1-2-macroeconomic-indicators.html`                                                                     | `% Change in Real GDP = % Change in Nominal GDP − Inflation Rate` is stated as an identity; it is an approximation valid at low inflation. Standard at A-Level, so probably intentional.                                                                                                                                                                                                                                                                                                                                                                                         |

## B. Figure captions that contradict their own diagram

All verified against the rendered image. These are visible body text, so they
were left alone.

| #      | Where                                                                                        | Issue                                                                                                                                                                                                                                                                                                                                                     |
| ------ | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **F1** | `aqa-a2-macro/2-2-2`, `aqa-a2-macro/2-2-5`, `edexcel-theme-2/2-3-2`                          | `sras-movements.png` is a **movements along the curve** diagram, but all three pages caption it "A shift of the SRAS curve to the right (SRAS1 to SRAS2) due to a decrease in production costs". `edexcel-theme-2/2-3-1` and the macro gallery caption it correctly.                                                                                      |
| **F2** | `aqa-a2-micro/1-1-5-production-possibility-diagrams.html`                                    | Two consecutive figures carry the **same** caption: "Figure 1: Standard PPF curve showing opportunity cost through movement from C to D". The second belongs to `ppf-growth-decline.png` under the heading "Shifts in the PPF: Economic Growth & Decline", so both the figure number and the description are stale.                                       |
| **F3** | `revision-notes/macroeconomics-diagrams.html`                                                | The card for `lras-classical-keynesian-ad-shift.png` is headed "Long-Run Growth in AD/AS" and captioned "Shows LRAS shifting right, increasing the economy's productive potential". I opened the PNG: it shows **AD1 → AD2 shifting with LRAS fixed**, compared on Keynesian and Classical curves. Both heading and caption describe a different diagram. |
| **F4** | `aqa-a2-micro/1-5-6-monopoly-and-monopoly-power.html`, `edexcel-theme-3/3-4-5-monopoly.html` | `nationalisation-privatisation.png` is captioned here as a natural-monopoly cost diagram, but as an ownership comparison on `aqa-a2-micro/1-8-8` and `edexcel-theme-3/3-6-1`. The alt now covers both readings, but the captions still frame it two different ways.                                                                                       |

## C. Wording and typography

| #      | Where                                                                | Issue                                                                                                                                                                        |
| ------ | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **W1** | `aqa-a2-macro/2-3-1-economic-growth-and-the-economic-cycle.html:562` | `<h2>The Trade Cycle?</h2>` — stray question mark on a heading that is not a question.                                                                                       |
| **W2** | 22 occurrences site-wide                                             | `program` / `programs` in policy contexts ("welfare programs", "training programs") where British English would prefer `programme`. An editorial call, not a mechanical fix. |
| **W3** | Both diagram gallery pages                                           | The second breadcrumb separator is the entity `&rsaquo;` while every other separator on the site is a literal `›`. Renders identically; inconsistent in source.              |

## D. Structural items reported but not actioned

| #      | Item                                                                                                                                                                                                                                                                                          |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **S1** | **Commercial link asymmetry.** 87 Edexcel pages carry a 3-button CTA block; 79 AQA pages carry nothing. `/past-papers/aqa/` exists, is in the sitemap and is linked from the AQA hubs, but no AQA note page links to it. Adding one would need new prose, since no page mentions past papers. |
| **S2** | **The 8 index/hub pages still declare `lang="en"`.** They are out of scope for this pass; the 168 note pages are now `en-GB`.                                                                                                                                                                 |
| **S3** | **94 pages still have only one inbound link** (down from 121). Raising this further would mean either linking from the hub pages or relaxing the 3-per-page cap.                                                                                                                              |
| **S4** | **Image weight.** `/images/diagrams/` is 25.9 MB across 112 files, 71 over 200 KB, no WebP/AVIF, no `srcset`. `microeconomics-diagrams.html` alone ships 11.6 MB. This is now the largest Core Web Vitals issue remaining. 7 diagram files are unused.                                        |
| **S5** | **629 inline `style` attributes** but only 17 distinct values; four account for 530. Extracting them into classes would remove most in one pass. Structural, so recommended rather than done.                                                                                                 |
| **S6** | **Dead CSS.** `chart-container` is used 211 times with no rule anywhere; `.coming-soon` has rules but no markup; `.evaluation-point` has 7 rules and 2 uses.                                                                                                                                  |
| **S7** | **One pre-existing Prettier nit** — a `transition:` shorthand in `css/pages/macro-application.css` that predates all of this work.                                                                                                                                                            |
