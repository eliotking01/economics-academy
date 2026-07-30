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

**Flagged, not changed.** Renumbering would change filenames, URLs, page titles,
breadcrumbs and the sitemap. That is a decision, not a cleanup.

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

## Flagged for review — economics content, deliberately not edited

### C1 — Supply diagram caption is inverted (highest priority)

`edexcel-theme-1/1-2-4-supply.html` and its AQA twin
`aqa-a2-micro/1-3-3-the-determinants-of-the-supply-of-goods-and-services.html`:

> "A movement from point B to A shows a **'Contraction in QS' due to a price rise**.
> A movement from point A to B shows an **'Extension in QS' due to a price fall**."

Fifteen lines below, the same page correctly states _"Extension in QS: A rise in price
leads to a movement up the curve"_. The caption appears to have been copy-pasted from
the **demand** page — where "contraction due to a price rise" is correct — without
flipping the sign. It is wrong, and it contradicts the bullet list within one screen.

### C2 — Supernormal profit given as `P > C` rather than `P > AC`

`edexcel-theme-3/3-4-1-efficiency.html` (twice) and its AQA twin
`aqa-a2-micro/1-5-10-market-structure-efficiency-resource-allocation.html` (twice).
`C` is undefined on the page and `P > MC` appears two sentences earlier, so a student
could reasonably read `C` as marginal cost. Looks like a dropped "A".

### C3 — `aqa-a2-micro/1-4-7-profit.html` spec block is the wrong topic entirely

Reads "Edexcel unit 3.3.4 - Normal Profits, Supernormal Profits and Losses" on a page
whose heading is "1.4.7 Profit". The whole block was pasted from
`edexcel-theme-3/3-3-4`. Wrong board, wrong code **and** wrong topic — it needs new
spec wording written, so it was left alone.

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

1. **Rule on C1 and C2** — the only outright economics errors found.
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
9. **AQA spec renumbering** — see "Specifications in use" above.
