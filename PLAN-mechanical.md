# PLAN — Part A: mechanical work

Phase 1 deliverable. **Nothing here has been applied.** Awaiting approval.

Companion documents: `RECON.md` (Phase 0 findings), `PLAN-enrichment-*.md`
(Part B, delivered per batch).

**Constraint governing everything below: no existing economics wording changes.**
Markup, classes, emphasis tags, heading levels, list structure and whitespace only.
Genuine errors get logged to `REVIEW-NOTES.md`, never fixed.

---

## 1. Exam Preparation removals — 87 files

### What is removed

The entire `<section>` wrapper, its `<h2>` and the `<div class="exam-tip">` inside
it. Per decision **D1**, the checklist content goes; Edexcel then matches AQA.

```html
<!-- BEFORE -->
            <section>
              <h2>Exam Preparation</h2>
              <div class="exam-tip">
                <ul>
                  <li>You must be able to <strong>define</strong> and …</li>
                  <li>Be prepared to <strong>evaluate</strong> the use of models …</li>
                  <li>Understand the core difference between economics …</li>
                </ul>
              </div>
            </section>
            <div style="margin-top: 2.5em; …">   <!-- CTA, untouched by this commit -->

<!-- AFTER -->
            <div style="margin-top: 2.5em; …">   <!-- CTA, untouched by this commit -->
```

### Anchor / ToC fixes needed: **none**

Verified in `RECON.md` §4 — no `id`s on these sections, no in-page ToC, no sidebar,
no cross-page fragment links, no sitemap fragments, no search index. **785 anchors
were resolved with zero breakage in the prior audit and none of them targets an Exam
Preparation section.** The Phase 3 link check re-confirms this after the fact.

### The one file needing special handling

`edexcel-theme-1/1-1-5-specialisation-division-of-labour.html` — the CTA is nested
**inside** the section being deleted. Handling: delete the `<section>`, `<h2>` and
`exam-tip` div, then **re-parent the CTA to sibling position** and dedent it by one
level so it matches the other 86 pages byte-for-byte. Verified afterwards by hashing
its CTA block against the other 86.

### Per-file table

### edexcel-theme-1 — 22 removals

| File | Heading | List | `<li>` | Lines | Notes |
| --- | --- | --- | ---: | --- | --- |
| `1-1-1-economics-as-a-social-science.html` | Exam Preparation | `<ul>` | 3 | 271–294 | — |
| `1-1-2-positive-normative-statements.html` | Exam Preparation | `<ul>` | 3 | 283–308 | — |
| `1-1-3-the-economic-problem.html` | Exam Preparation | `<ul>` | 2 | 269–285 | — |
| `1-1-4-production-possibility-frontiers.html` | Exam Preparation | `<ol>` | 5 | 328–357 | — |
| `1-1-5-specialisation-division-of-labour.html` | Exam Preparation | `<ol>` | 3 | 318–374 | **CTA nested inside — must be preserved and re-parented** |
| `1-1-6-types-of-economies.html` | Exam Preparation | `<ol>` | 3 | 322–346 | — |
| `1-2-1-rational-decision-making.html` | Exam Preparation | `<ol>` | 3 | 232–257 | — |
| `1-2-10-alternative-views-of-consumer-behaviour.html` | Exam Preparation | `<ol>` | 4 | 283–312 | — |
| `1-2-2-demand.html` | Exam Preparation | `<ol>` | 5 | 370–398 | — |
| `1-2-3-price-income-cross-elasticities-of-demand.html` | Exam Preparation | `<ol>` | 4 | 444–474 | contains a `formula-box` |
| `1-2-4-supply.html` | Exam Preparation | `<ol>` | 5 | 361–390 | — |
| `1-2-5-price-elasticity-of-supply.html` | Exam Preparation | `<ol>` | 4 | 364–392 | — |
| `1-2-6-price-determination.html` | Exam Preparation | `<ol>` | 5 | 406–439 | — |
| `1-2-7-price-mechanism.html` | Exam Preparation | `<ol>` | 7 | 364–402 | — |
| `1-2-8-producer-consumer-surplus.html` | Exam Preparation: | `<ol>` | 5 | 343–373 | heading variant `Exam Preparation:` |
| `1-2-9-indirect-taxes-subsidies.html` | Exam Focus | `<ol>` | 5 | 403–433 | heading variant `Exam Focus` |
| `1-3-1-types-of-market-failure.html` | Exam Preparation | `<ul>` | 4 | 303–331 | — |
| `1-3-2-externalities.html` | Exam Preparation | `<ul>` | 5 | 592–621 | — |
| `1-3-3-public-goods.html` | Exam Preparation | `<ul>` | 4 | 233–260 | — |
| `1-3-4-information-gaps.html` | Exam Preparation | `<ul>` | 4 | 237–264 | — |
| `1-4-1-government-intervention-in-markets.html` | Exam Preparation | `<ul>` | 5 | 496–528 | — |
| `1-4-2-government-failure.html` | Exam Preparation | `<ul>` | 4 | 242–273 | — |

### edexcel-theme-2 — 24 removals

| File | Heading | List | `<li>` | Lines | Notes |
| --- | --- | --- | ---: | --- | --- |
| `2-1-1-economic-growth.html` | Exam Preparation | `<ul>` | 4 | 298–327 | — |
| `2-1-2-inflation.html` | Exam Preparation | `<ul>` | 5 | 482–511 | — |
| `2-1-3-employment-unemployment.html` | Exam Preparation | `<ul>` | 4 | 326–371 | — |
| `2-1-4-balance-of-payments.html` | Exam Preparation | `<ul>` | 4 | 308–341 | — |
| `2-2-1-aggregate-demand.html` | Exam Preparation | `<ul>` | 4 | 409–436 | — |
| `2-2-2-consumption.html` | Exam Preparation | `<ul>` | 4 | 292–324 | — |
| `2-2-3-investment.html` | Exam Preparation | `<ul>` | 4 | 265–296 | — |
| `2-2-4-government-expenditure.html` | Exam Preparation | `<ul>` | 4 | 259–296 | — |
| `2-2-5-net-trade.html` | Exam Preparation | `<ul>` | 4 | 286–318 | — |
| `2-3-1-aggregate-supply.html` | Exam Preparation | `<ul>` | 5 | 343–374 | — |
| `2-3-2-short-run-aggregate-supply.html` | Exam Preparation | `<ul>` | 4 | 323–347 | — |
| `2-3-3-long-run-aggregate-supply.html` | Exam Preparation | `<ul>` | 5 | 421–453 | — |
| `2-4-1-national-income.html` | Exam Preparation | `<ul>` | 5 | 347–383 | — |
| `2-4-2-injections-withdrawals.html` | Exam Preparation | `<ul>` | 5 | 320–349 | — |
| `2-4-3-equilibrium-levels-of-real-national-output.html` | Exam Preparation | `<ul>` | 5 | 352–383 | — |
| `2-4-4-the-multiplier.html` | Exam Preparation | `<ul>` | 5 | 368–396 | — |
| `2-5-1-causes-of-growth.html` | Exam Preparation | `<ul>` | 5 | 407–438 | — |
| `2-5-2-output-gaps.html` | Exam Preparation | `<ul>` | 5 | 358–386 | — |
| `2-5-3-trade-cycle.html` | Exam Preparation | `<ul>` | 5 | 339–372 | — |
| `2-5-4-the-impact-of-economic-growth.html` | Exam Preparation | `<ul>` | 4 | 313–339 | — |
| `2-6-1-possible-macroeconomic-objectives.html` | Exam Preparation | `<ul>` | 4 | 289–312 | — |
| `2-6-2-demand-side-policies.html` | Exam Preparation | `<ul>` | 5 | 682–709 | — |
| `2-6-3-supply-side-policies.html` | Exam Preparation | `<ul>` | 5 | 518–548 | — |
| `2-6-4-conflicts-between-objectives-and-policies.html` | Exam Preparation | `<ul>` | 4 | 363–387 | — |

### edexcel-theme-3 — 20 removals

| File | Heading | List | `<li>` | Lines | Notes |
| --- | --- | --- | ---: | --- | --- |
| `3-1-1-sizes-types-of-firms.html` | Exam Preparation | `<ul>` | 4 | 288–317 | — |
| `3-1-2-business-growth.html` | Exam Preparation | `<ul>` | 5 | 330–356 | — |
| `3-1-3-demergers.html` | Exam Preparation | `<ul>` | 3 | 309–331 | — |
| `3-2-1-business-objectives.html` | Exam Preparation | `<ul>` | 4 | 384–407 | — |
| `3-3-1-revenue.html` | Exam Preparation | `<ul>` | 5 | 317–342 | — |
| `3-3-2-costs.html` | Exam Preparation | `<ul>` | 5 | 365–396 | — |
| `3-3-3-economies-diseconomies-of-scale.html` | Exam Preparation | `<ul>` | 5 | 443–470 | — |
| `3-3-4-normal-profits-supernormal-profits-losses.html` | Exam Preparation | `<ul>` | 5 | 309–336 | — |
| `3-4-1-efficiency.html` | Exam Preparation | `<ul>` | 5 | 321–349 | — |
| `3-4-2-perfect-competition.html` | Exam Preparation | `<ul>` | 5 | 395–423 | — |
| `3-4-3-monopolistic-competition.html` | Exam Preparation | `<ul>` | 5 | 392–424 | — |
| `3-4-4-oligopoly.html` | Exam Preparation | `<ul>` | 5 | 485–512 | — |
| `3-4-5-monopoly.html` | Exam Preparation | `<ul>` | 4 | 508–531 | — |
| `3-4-6-monopsony.html` | Exam Preparation | `<ul>` | 5 | 283–311 | — |
| `3-4-7-contestability.html` | Exam Preparation | `<ul>` | 5 | 377–404 | — |
| `3-5-1-demand-for-labour.html` | Exam Preparation | `<ul>` | 5 | 319–345 | — |
| `3-5-2-supply-of-labour.html` | Exam Preparation | `<ul>` | 5 | 365–391 | — |
| `3-5-3-wage-determination.html` | Exam Preparation | `<ul>` | 5 | 518–547 | — |
| `3-6-1-government-intervention.html` | Exam Preparation | `<ul>` | 5 | 431–460 | — |
| `3-6-2-the-impact-of-government-intervention.html` | Exam Preparation | `<ul>` | 4 | 274–297 | — |

### edexcel-theme-4 — 21 removals

| File | Heading | List | `<li>` | Lines | Notes |
| --- | --- | --- | ---: | --- | --- |
| `4-1-1-globalisation.html` | Exam Preparation | `<ul>` | 4 | 422–453 | — |
| `4-1-2-specialisation-trade.html` | Exam Preparation | `<ul>` | 5 | 368–395 | — |
| `4-1-3-pattern-of-trade.html` | Exam Preparation | `<ul>` | 4 | 215–239 | — |
| `4-1-4-terms-of-trade.html` | Exam Preparation | `<ul>` | 4 | 274–297 | — |
| `4-1-5-trading-blocs-and-the-world-trade-organisation.html` | Exam Preparation | `<ul>` | 4 | 337–359 | — |
| `4-1-6-restrictions-on-free-trade.html` | Exam Preparation | `<ul>` | 4 | 359–382 | — |
| `4-1-7-balance-of-payments.html` | Exam Preparation | `<ul>` | 4 | 364–387 | — |
| `4-1-8-exchange-rates.html` | Exam Preparation | `<ul>` | 5 | 481–508 | — |
| `4-1-9-international-competitiveness.html` | Exam Preparation | `<ul>` | 4 | 307–330 | — |
| `4-2-1-absolute-relative-poverty.html` | Exam Preparation | `<ul>` | 4 | 234–258 | — |
| `4-2-2-inequality.html` | Exam Preparation | `<ul>` | 5 | 445–475 | — |
| `4-3-1-measures-of-development.html` | Exam Preparation | `<ul>` | 4 | 331–355 | — |
| `4-3-2-factors-influencing-growth-development.html` | Exam Preparation | `<ul>` | 4 | 331–354 | — |
| `4-3-3-strategies-influencing-growth-development.html` | Exam Preparation | `<ul>` | 5 | 529–559 | — |
| `4-4-1-role-of-financial-markets.html` | Exam Preparation | `<ul>` | 4 | 207–232 | — |
| `4-4-2-market-failure-in-the-financial-sector.html` | Exam Preparation | `<ul>` | 4 | 277–302 | — |
| `4-4-3-role-of-central-banks.html` | Exam Preparation | `<ul>` | 4 | 248–271 | — |
| `4-5-1-public-expenditure.html` | Exam Preparation | `<ul>` | 4 | 262–286 | — |
| `4-5-2-taxation.html` | Exam Preparation | `<ul>` | 4 | 369–398 | — |
| `4-5-3-public-sector-finances.html` | Exam Preparation | `<ul>` | 4 | 335–358 | — |
| `4-5-4-macroeconomic-policies-in-a-global-context.html` | Exam Preparation | `<ul>` | 4 | 392–416 | — |

---

## 2. The `.notes-cta` conversion

Per decisions **D2**, **D5** and **D6**: one class, one accent colour, applied to all
166 topic pages plus the 2 galleries.

### New CSS — appended to `css/pages/revision-notes-textbook.css`

```css
/* Bottom-of-page conversion CTA */
.revision-notes-content .notes-cta {
  margin-top: 2.5em;
  padding: 1.5em;
  background: #f8f8f8;
  border-left: 4px solid #d52349;
  border-radius: 4px;
  text-align: center;
}

.revision-notes-content .notes-cta p {
  margin: 0 0 1em;
  font-weight: 600;
  font-family: "Open Sans", sans-serif;
}

.revision-notes-content .notes-cta .button {
  margin: 0.3em;
}
```

**Why this is rendering-equivalent** — checked, not assumed:

- The inline styles only ever set `margin`, `font-weight` and `font-family` on the
  `<p>`. Everything else (`font-size`, `line-height`, colour) was already coming
  from the cascade and is unaffected.
- `.revision-notes-content .notes-cta p` has specificity (0,2,1); the existing
  `.revision-notes-content p { margin-bottom: 1.5em; font-size: 1.05em; }` is
  (0,1,1). The new rule wins on `margin`, and never touched `font-size` before or
  after.
- `.button` in `main.css` sets no `margin`, so `.revision-notes-content .notes-cta
  .button` (0,3,0) is uncontested.
- The `@media` block at `revision-notes-textbook.css:776` sets `font-size` only on
  `.revision-notes-content p` — unaffected either way, as the inline style never
  set `font-size`.

Confirmed by pixel diff in Phase 3 regardless.

### New markup — AQA topic pages (79 files)

```html
            <div class="notes-cta">
              <p>Ready to apply these notes?</p>
              <a href="/past-papers/aqa/index.html" class="button alt"
                >AQA Past Papers</a
              >
              <a href="/marking.html" class="button alt">Get Essays Marked</a>
              <a href="/tutoring.html" class="button">Book a Free Intro Call</a>
            </div>
```

Placement: as the last child of `.notes-container`, immediately after the final
`</section>` — the same position it occupies on all 87 Edexcel pages.

`/past-papers/aqa/index.html` confirmed to exist. The copy reuses the exact Edexcel
strings, with only "Edexcel Past Papers" → "AQA Past Papers"; the AQA hub pages use
"Paper Marking" for the middle button, but matching the note-page wording is the
consistency that matters here.

### Converted markup — Edexcel topic pages (87 files)

```html
            <div class="notes-cta">
              <p>Ready to apply these notes?</p>
              <a href="/past-papers/edexcel/index.html" class="button alt"
                >Edexcel Past Papers</a
              >
              <a href="/marking.html" class="button alt">Get Essays Marked</a>
              <a href="/tutoring.html" class="button">Book a Free Intro Call</a>
            </div>
```

### Converted markup — the 2 diagram galleries

Identical, keeping their existing board-neutral link and label:

```html
              <a href="/past-papers/index.html" class="button alt">Past Papers</a>
```

**Net effect:** 168 inline-styled blocks → 168 class-based blocks; roughly 350 inline
`style` attributes removed, addressing part of audit flag S5. No copy changes, no
link changes.

---

## 3. Formatting and emphasis

### Tag convention — stated explicitly

- **`<strong>`** for key terms on first statement, list-item lead-ins, and table row
  labels. This is what the site already does, 4,831 times.
- **`<em>`** only for logical contrast words (`only`, `not`, `non-base`) and
  publication titles — exactly as the exemplars use it. Currently 12 uses; expect
  fewer than 20 after this pass.
- **`<b>` and `<i>` never.** Zero in the codebase today; keeping it that way.

Rationale for `<strong>` over `<b>`: it carries semantic weight for screen readers,
it is the established convention here, and `css` already styles both identically so
there is no visual argument for `<b>`.

### Which pages

The 25 weakest pages by combined (`<strong>` + `key-definition`) density — the table
in `RECON.md` §5. Per **D4**, the other ~141 pages get no emphasis changes.

**This is a candidate list, not a mandate.** Working through it, some pages will come
back as "no change needed" — for example
`aqa-a2-micro/1-3-6-the-interrelationship-between-markets.html` scores 2.49 only
because its content sits almost entirely inside a `concept-table` whose row labels
are *already* bolded correctly. Pages like that will be reported as inspected and
left alone. I expect to touch roughly 15–20 of the 25.

### The five worked before/after examples

---

#### Example 1 — key causal terms in prose

`edexcel-theme-2/2-2-2-consumption.html` (combined density 1.31, the weakest page on
the site). Four `<h3>` sections each explain a determinant of consumption in plain
prose with no emphasis at all.

**BEFORE**

```html
              <h3>Consumer Confidence</h3>
              <p>
                Consumer confidence is a measure of how optimistic households
                are about their future income and the state of the economy.
              </p>
              <p>
                A rise in consumer confidence encourages households to spend
                more and borrow more, increasing consumption. A fall in consumer
                confidence encourages households to save more and borrow less,
                reducing consumption.
              </p>
```

**AFTER**

```html
              <h3>Consumer Confidence</h3>
              <p>
                <strong>Consumer confidence</strong> is a measure of how
                optimistic households are about their future income and the
                state of the economy.
              </p>
              <p>
                A <strong>rise</strong> in consumer confidence encourages
                households to spend more and borrow more,
                <strong>increasing consumption</strong>. A
                <strong>fall</strong> in consumer confidence encourages
                households to save more and borrow less,
                <strong>reducing consumption</strong>.
              </p>
```

Precedent: `consumer confidence` is already bolded on
`aqa-a2-macro/2-2-3`, `aqa-a2-macro/2-3-1` and `edexcel-theme-2/2-5-3`. Marking the
direction of change (`rise`/`fall` → `increasing`/`reducing`) is the dominant
pattern on the well-emphasised pages such as `edexcel-theme-1/1-2-6-price-determination`.

---

#### Example 2 — definitional lead-in promoted to the house pattern

`aqa-a2-micro/1-4-1-production-and-productivity.html` (combined 2.61 — 3 `<strong>`
in 1,149 characters). "Labour productivity" is defined in a bare paragraph while the
two neighbouring definitions on the same page get `key-definition` chips.

**BEFORE**

```html
              <p>
                <strong>Labour productivity:</strong> A measure of the output
                produced per unit of labour input, often expressed as output per
                worker or output per worker per hour.
              </p>
```

**AFTER**

```html
              <p>
                <span class="key-definition">Labour productivity:</span> A
                measure of the output produced per unit of labour input, often
                expressed as output per worker or output per worker per hour.
              </p>
```

This is a class change, not an emphasis addition — it brings the third definition on
the page into line with the two above it (`Production:`, `Productivity:`), both of
which already use `key-definition`. Zero words change.

---

#### Example 3 — list items with an unmarked operative constraint

`aqa-a2-micro/1-2-3-aspects-of-behavioural-economic-theory.html` (combined 2.63).
The definitions are already handled by `key-definition` chips; the gap is in the
bullets beneath them, where the operative constraint is buried mid-sentence.

**BEFORE**

```html
              <ul>
                <li>
                  Individuals may not have access to all the information needed
                  to make a rational decision.
                </li>
                <li>
                  Individuals may not have the time to consider all the
                  information and possible options.
                </li>
                <li>
                  Individuals may not have the ability to process all the
                  information and make a rational decision.
                </li>
              </ul>
```

**AFTER**

```html
              <ul>
                <li>
                  Individuals may not have access to all the
                  <strong>information</strong> needed to make a rational
                  decision.
                </li>
                <li>
                  Individuals may not have the <strong>time</strong> to consider
                  all the information and possible options.
                </li>
                <li>
                  Individuals may not have the <strong>ability</strong> to
                  process all the information and make a rational decision.
                </li>
              </ul>
```

The three bullets are the three limbs of bounded rationality — information, time,
ability — named in the definition directly above them. Marking them makes the
structure scannable. Precedent: the `<strong>` lead-in bullet pattern used
throughout `aqa-a2-macro/2-4-1`.

---

#### Example 4 — `<em>` for logical contrast

`edexcel-theme-4/4-4-1-role-of-financial-markets.html` (combined 1.60). Restrained,
one instance; `<em>` stays rare by design.

**BEFORE**

```html
              <p>
                Forward and futures markets allow firms to trade commodities and
                currencies at a price agreed today for delivery in the future.
              </p>
```

**AFTER**

```html
              <p>
                Forward and futures markets allow firms to trade commodities and
                currencies at a price <em>agreed today</em> for delivery
                <em>in the future</em>.
              </p>
```

The whole point of a forward market is the gap between the two times; the contrast is
the content. This mirrors `<em>only</em>` / `<em>non-base</em>` in exemplar 2.1.3.

---

#### Example 5 — structural, not emphasis: dead wrapper removal

Applies to all 211 `chart-container` divs (approved additional suggestion). The class
has **no CSS rule anywhere in the codebase**, and it always wraps exactly one
`<figure class="diagram-figure">`.

**BEFORE**

```html
              <div class="chart-container">
                <figure class="diagram-figure">
                  <img
                    src="/images/diagrams/ppf-basic.png"
                    alt="Production possibility frontier showing the opportunity cost trade-off between capital goods and consumer goods"
                    class="diagram-image"
                    width="2257"
                    height="1143"
                  />
                  <figcaption class="diagram-caption">…</figcaption>
                </figure>
              </div>
```

**AFTER**

```html
              <figure class="diagram-figure">
                <img
                  src="/images/diagrams/ppf-basic.png"
                  alt="Production possibility frontier showing the opportunity cost trade-off between capital goods and consumer goods"
                  class="diagram-image"
                  width="2257"
                  height="1143"
                />
                <figcaption class="diagram-caption">…</figcaption>
              </figure>
```

Layout is unchanged: an unstyled `<div>` and the `<section>` that becomes the new
parent are both full-width block boxes, so `.diagram-figure`'s
`margin: 2em auto; max-width: 800px` centres identically. Verified by pixel diff in
Phase 3.

Distribution: 73 in `aqa-a2-micro`, 36 `aqa-a2-macro`, 26 theme-1, 34 theme-2,
34 theme-3, 8 theme-4.

---

## 4. The other approved additional work

### `<!-- prettier-ignore -->` on unprotected `formula-box` divs — 28 instances

23 of the 51 `formula-box` divs already carry the comment; 28 do not, leaving their
LaTeX exposed to reflow on the next Prettier run.

```html
<!-- BEFORE -->
              <div class="formula-box">
                <p>\[ \text{Output Gap} = \text{Y} - \text{Yfe} \]</p>
              </div>

<!-- AFTER -->
              <!-- prettier-ignore -->
              <div class="formula-box">
                <p>\[ \text{Output Gap} = \text{Y} - \text{Yfe} \]</p>
              </div>
```

### Flagged, needs your call: 12 formulas already broken by past reflow

Adding the comment protects against *future* damage but does not undo what has
already happened. Twelve display formulas are currently split across source lines.
Ten are cosmetically harmless — LaTeX collapses whitespace between brace groups.
**Two are not**, because the break falls inside a `\text{}` group and MathJax renders
the resulting leading space:

| File | Line | Currently renders |
| --- | --- | --- |
| `aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html` | 202 | `\text{ Injection}` — spurious leading space |
| `edexcel-theme-2/2-4-4-the-multiplier.html` | 198 | same |

Rejoining these onto one source line is a **whitespace-only** change (explicitly
within the permitted list) and alters no symbol, number or word. It does change what
renders, by removing a space that should not be there.

**My recommendation: fix both, and rejoin the other ten too** so the protection
comment is applied to clean source. **Say if you would rather I only log them.**
Default if you say nothing: I will log all 12 in `REVIEW-NOTES.md` and rejoin none.

### Not proceeding with (your decision)

- Extracting the remaining ~279 inline `style` attributes (audit S5) — not approved
- Section-ordering normalisation across twin pages — not approved

### Dropped — no work to do

Wrapping unwrapped wide `concept-table`s for mobile scroll: **all 103 are already
wrapped** in `table-container`. The 3 `calculation-table`s are deliberately
unwrapped, matching the exemplars. Nothing to fix. (Listed as a recommendation in the
plan before I measured it; recording the correction rather than silently dropping it.)

---

## 5. Git strategy and commit sequence

### Setup

```bash
git branch backup-pre-enrichment      # safety net on current main
git checkout -b notes-consistency-pass
```

**Never `push`, `merge`, `rebase` or `force-push`. Never check out or commit to
`main`.** The repo auto-publishes from `main`; this branch is for your review and
you merge it yourself.

### Commits — separate per phase per board, so any can be reverted alone

| # | Message | Files |
| ---: | --- | ---: |
| 1 | `Remove generic Exam Preparation sections from Edexcel notes` | 87 |
| 2 | `Extract .notes-cta class and convert Edexcel note CTAs` | 87 + 2 galleries + 1 CSS |
| 3 | `Add conversion CTA to AQA note pages` | 79 |
| 4 | `Remove dead chart-container wrappers` | ~94 |
| 5 | `Protect formula-box LaTeX from Prettier reflow` | ~22 |
| 6 | `Improve emphasis on under-emphasised AQA notes` | ~12 |
| 7 | `Improve emphasis on under-emphasised Edexcel notes` | ~8 |
| 8 | `Add worked examples and exam tips to AQA notes` | from Part B |
| 9 | `Add worked examples and exam tips to Edexcel notes` | from Part B |

Commits 6–7 are the ones the text-integrity check in Phase 3 gates on: it diffs the
extracted plain text at commit 5 against commit 7 and requires byte-identical output
for all 166 files.

Commits 8–9 are split by theme in practice — after each theme batch I show you a diff
summary and the file list, then wait.

`NEW-CONTENT-LOG.md` is updated as commits 8–9 are made: file, line, component type,
one line on what it adds.

---

## 6. Additional suggestions — record of decisions

| Suggestion | Effort | My call | Yours |
| --- | --- | --- | --- |
| Remove 211 dead `chart-container` wrappers (audit S6) | ~1h, scripted | **Recommend** | **Approved** |
| `<!-- prettier-ignore -->` on all 51 `formula-box` divs | ~20min | **Recommend** | **Approved** |
| Wrap unwrapped wide `concept-table`s for mobile | — | **Recommend** | Approved, but **no work exists** — all 103 already wrapped |
| Extract remaining ~279 inline `style` attributes (audit S5) | ~3h + full visual regression | **Don't recommend** this pass — large diff, competes with the enrichment work for review attention | Not approved |
| Normalise section ordering across twin pages | ~4h | **Don't recommend** — reordering sections is editorial, not formatting, and risks changing how an argument builds | Not approved |
| Rejoin 12 Prettier-broken LaTeX formulas | ~15min | **Recommend** — 2 of them render a visible spurious space | **Awaiting your call** (§4) |

### Also noted, not proposed as work

- `.coming-soon` has CSS rules and zero markup uses. Dead, but it is 4 lines of CSS
  and removing it is unrelated to this pass. Logging only.
- The `<h2>The Trade Cycle?</h2>` stray question mark (audit flag W1,
  `aqa-a2-macro/2-3-1-…html:562`) is a **wording** change and stays out of scope.
  Re-logged in `REVIEW-NOTES.md`.
- Audit flag **C1** — the inverted supply-diagram caption on
  `edexcel-theme-1/1-2-4-supply.html` and its AQA twin — remains the one open
  economics error. Not fixed, re-logged.

---

## 7. What happens on approval

1. `git branch backup-pre-enrichment` and `git checkout -b notes-consistency-pass`
2. Commits 1–5 (the purely mechanical work), with a diff summary after each
3. Commits 6–7 (emphasis), after showing you the first 3 files of commit 6 in situ
4. Then Part B batch 1 (`PLAN-enrichment-aqa-micro.md`) for separate approval

**I stop after commit 5 and wait**, before touching emphasis.
