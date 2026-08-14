# Wave 5.1 — the 83 SVG/PNG pairs, verified

**Verified by Eliot, 2026-08-14**, from the side-by-side sheet built by
`_working/diagram-review/build.py`. This is PH08-047 step 1, and it closes it.
Everything below is his verdict, recorded verbatim; nothing here is my judgement
of a diagram's economics.

**Coverage is complete and was checked, not assumed:** 83 verdicts against the
83 files in `images/diagrams/svg/`, **0 SVGs without a verdict and 0 verdicts
without an SVG.**

```
faithful  70   (of which 9 carry an amendment note and 4 a pairing confirmation)
differs   12
correct    1   (game-theory, recorded "unsure" then explained as deliberate)
```

## The headline is not the one the finding expected

PH08-047 asked whether the SVGs could safely replace the notes' PNGs. The answer
is that **12 cannot, today.** But the result that matters more was not what the
finding was looking for:

> **All 83 SVGs are already live**, and **21 of them carry a defect Eliot has
> now identified** — 12 `differs` and 9 amendments. Every one is in the public
> flashcard payloads (`flashcards/data/*.json`), **21 of 21, none premium-gated**,
> across 41 cards and all 6 decks. One, `comparative-advantage`, is also live in
> the notes on 3 pages.

So 5.1 was framed as a precondition for 5.3 and has instead produced a
**live-site defect list**. That list does not depend on whether 5.3 ever happens.

## The four classes of `differs`

**These four categories need different work and should not be batched together.**

### (a) A panel is missing — 4

`perfect-competition-short-run-supernormal-profit`,
`perfect-competition-short-run-loss`, `price-discrimination`,
`short-run-shutdown-condition`.

PH08-047 found **one** of these. There are **four**. Each SVG draws one panel of
a two-panel PNG and, in Eliot's words on two of them, *"otherwise it doesn't
work"*. These are the ones that would delete economics content from a notes page
if swapped, and they are also incomplete as flashcards today.

**`price-discrimination` and `short-run-shutdown-condition` carry an option in
the verdict** — *"either needs to be included here or in a different diagram"* —
so the fix is a decision, not just drawing.

### (b) A label is incomplete — 2

`efficiency-perfect-competition`, `efficiency-imperfect-competition`. Both say
"Productive" / "Allocative" where they should say "Productive efficiency" /
"Allocative efficiency"; the second also needs a dynamic-efficiency label on the
shaded area. Cheapest class to fix.

### (c) The drawing is wrong on its own terms — 5

`j-curve`, `laffer-curve`, `normal-profit-imperfect-competition`,
`perfect-competition-market-price`, `trade-union-monopsony`.

**These are not comparisons against the PNG — they are errors in the SVG**, and
two of them are economics rather than cosmetics: the `j-curve` has Surplus and
Deficit on the wrong side of the Y axis, and
`normal-profit-imperfect-competition`'s AC minimum is not at its intersection
with MC. `verify_diagram_geometry.py` passes all 83 today, so **its declarations
do not encode these constraints** — that is a gap in the checker, found by eye.

### (d) The figure teaches something Eliot no longer wants it to teach — 1

`comparative-advantage`. **This is the only item on the list that is a content
change rather than a repair, and it is the one live in the notes.**

The current SVG shows each country with an absolute advantage in one good.
Eliot's verdict asks for **Germany to have an absolute advantage in both**. That
reverses a design decision taken on 2026-08-06 under `CONTENT_ISSUES.md` #26,
where the macro gallery's blurb was reworded *because* the absolute-advantage-in-
both case was no longer illustrated.

**Its true scope is not the SVG.** `4-1-2-specialisation-trade.html` and its AQA
twin `2-6-2-trade.html` carry the figure's numbers in prose — Germany 10m chips /
75mn T-shirts, Vietnam 5m / 100mn, opportunity costs 7.5 and 20, 0.13 and 0.05,
and a 15m / 175mn global total. Giving Germany the absolute advantage in T-shirts
too changes **every one of those figures**, on two pages, plus three figcaptions
and the gallery blurb. That is an economics rewrite and needs its own explicit
instruction; it is recorded here and **not acted on**.

## Nine amendments on diagrams Eliot passed as faithful

Right economics, drawing to tidy. `collusion` (MC hockey-stick),
`economies-of-scale` (label overlaps the curve), `kinked-demand-curve` (extend
MC right), `nationalisation-privatisation` (curves sit far right, not centred),
`short-run-costs` (AFC tail, AC/AVC squashed low), and **one repeated class on
four files** — `overconsumption`, `overproduction`, `underconsumption`,
`underproduction` all need the welfare-loss label to point at the shaded region
rather than the triangle's corner.

## Four verdicts settle open questions rather than raising them

- **`lras-shift` — "Shows classical", faithful.** This closes the decision
  `docs/FLASHCARDS_PROGRESS.md` recorded as *"pending Eliot"* on 2026-08-05 and
  which no later entry closed. Drawing only the classical panel is ratified.
- **`lras-shift-keynesian` — "Shows Keynesian", faithful.**
- **`exchange-rate-appreciation` / `-depreciation` — faithful, and Eliot named
  which panel each takes** (appreciation = the right-hand panel, depreciation =
  the left). The two-panel split is confirmed against the figure.
- **`game-theory` — recorded `unsure`, then explained: "It has the High
  Price/Low Price swapped but this is intentional so it is correct."** That is
  the `CONTENT_ISSUES.md` #9 fix working as designed. Treat as **correct**.

## Two numbers from PH08-047 that did not survive

- **"Every SVG is 4:3; 2 of 78 agree within 2%."** The 4:3 holds — all 83
  viewBoxes are `0 0 800 600`, one value. The agreement count is **1 of 78**, at
  `31dcc4e` and at `da0fff0`, the finding's own commit. `underconsumption` is
  2.03% off and falls just outside. So the aspect ratio changes on **77** of 78,
  not 76.
- **"231 tags across 94 pages."** 231 is right and is the twinned-tag count; no
  page count is 94. Measured at both commits: **295** `<img>` at a diagram PNG
  across **95** pages, of which **231** across **85** pages have a same-named
  SVG. `DECISIONS.md` D25 repeats the same pair for the WebP route, where the
  correct figure is 295.

## Aspect ratio predicts the panel class and nothing else

PH08-047's Result 3 said there is no mechanical screen. That is confirmed, and
now quantified:

```
PNG aspect >= 1.9 :  6 differs of 17   (35%)
PNG aspect <  1.9 :  6 differs of 66   ( 9%)
```

**All 4 panel-drops sit at 2.54 and above** — so width does predict *that* class.
But **6 of the 12 problems are on narrow PNGs**, down to 1.392
(`trade-union-monopsony`), and screening on width would have missed half of them.
`efficiency-imperfect-competition` at 1.820 fell just outside the sheet's own
risky-first block and is a `differs`.

## What this does to 5.3

**5.3 cannot proceed as a sweep.** 12 of 83 SVGs are not currently a safe
replacement for the PNG they would displace, and 4 of those would remove a panel
of economics from a live notes page. 5.3 is now gated on repairing them, which is
5.2's kind of work rather than 5.1's.

Two further constraints on 5.3, measured while building the sheet and unrelated
to any verdict above:

- **An SVG swapped in at `width="800" height="600"` renders 800 CSS px wide
  where the PNG it replaces renders at the container's ~1,120 px** — measured on
  `3-4-4-oligopoly.html`, whose `game-theory.svg` is 798 px of white against
  1,118 px for the two PNGs beside it. PH08-047 step 3 prescribes setting
  `width`/`height` to the viewBox, which would shrink **every** swapped diagram
  by 29%.
- **`verify_image_dimensions.py` requires the declared size to equal the file's
  intrinsic size, not merely its ratio**, so a larger declaration fails CI step 7.
  Fixing the shrinkage means changing the SVG files, the stylesheet, or the
  checker — a decision, not an attribute edit.

## The full record

`amend` marks a diagram Eliot passed as faithful with a drawing note. PNG AR is
the ground-truth file's aspect ratio; every SVG viewBox is 1.333.

| # | SVG | Ground truth | PNG AR | Verdict | Class | Eliot's note |
| --: | --- | --- | --: | --- | --- | --- |
| 1 | `ad-movements` | same name | 1.491 | faithful | — | — |
| 2 | `ad-shift` | same name | 1.475 | faithful | — | — |
| 3 | `ad-shift-right` | same name | 1.467 | faithful | — | — |
| 4 | `buffer-stocks` | same name | 1.505 | faithful | — | — |
| 5 | `circular-flow-of-income` | same name | 1.377 | faithful | — | — |
| 6 | `circular-flow-of-income-injections-withdrawals` | same name | 1.852 | faithful | — | — |
| 7 | `classical-ad-shift-right` | same name | 1.509 | faithful | — | — |
| 8 | `classical-lras-shift-right` | same name | 1.509 | faithful | — | — |
| 9 | `collusion` | same name | 1.625 | faithful | amend | The MC curve should rise more on the left hand side to make it look more like a "hockey stick" |
| 10 | `comparative-advantage` | same name | 1.526 | **differs** | content | This SVG results in the same outcome of goods if following absolute advantage or comparative advantage. The diagram needs to show Germany with absolute advantage in both (higher possible total production on both axis). |
| 11 | `consumer-producer-surplus-equilibrium` | same name | 1.296 | faithful | — | — |
| 12 | `demand-curve-shift` | same name | 1.394 | faithful | — | — |
| 13 | `demand-for-labour` | same name | 1.494 | faithful | — | — |
| 14 | `economies-of-scale` | same name | 1.496 | faithful | amend | Text needs to be moved left slightly - currently overlapping the curve. |
| 15 | `efficiency-imperfect-competition` | same name | 1.820 | **differs** | label | "Productive" and "Allocative" need the say "Productive efficiency" and "allocative efficiency" respectively. Also need a label to show dynamic efficiency as the shaded area. |
| 16 | `efficiency-perfect-competition` | same name | 2.423 | **differs** | label | "Productive" should read "Productive efficiency" and "Allocative" should read "Allocative efficiency" |
| 17 | `excess-demand` | same name | 1.306 | faithful | — | — |
| 18 | `excess-supply` | same name | 1.260 | faithful | — | — |
| 19 | `exchange-rate-appreciation` | `exchange-rates` | 2.719 | faithful | — | The SVG correctly shows the appreciation of the curreny (the right hand PNG) |
| 20 | `exchange-rate-depreciation` | `exchange-rates` | 2.719 | faithful | — | The SVG correctly shows the depreciation of the curreny (the left hand PNG) |
| 21 | `game-theory` | same name | 1.504 | correct | — | It has the High Price/Low Price swapped but this is intentional so it is correct |
| 22 | `indirect-tax-elastic-demand` | `Indirect-tax-incidence-elastic-inelastic` | 2.191 | faithful | — | — |
| 23 | `indirect-tax-gov-revenue` | same name | 1.261 | faithful | — | — |
| 24 | `indirect-tax-incidence` | same name | 1.303 | faithful | — | — |
| 25 | `indirect-tax-inelastic-demand` | `Indirect-tax-incidence-elastic-inelastic` | 2.191 | faithful | — | — |
| 26 | `j-curve` | same name | 1.582 | **differs** | drawing | Surplus and Deficit are the wrong side of the Y axis - should be on the left. "Depreciation occurs" should be above the left hand dotted line |
| 27 | `keynesian-ad-shift-right` | same name | 1.487 | faithful | — | — |
| 28 | `keynesian-lras-shift-right` | same name | 1.445 | faithful | — | — |
| 29 | `kinked-demand-curve` | same name | 1.585 | faithful | amend | MC curve should be extended further on the right hand side |
| 30 | `kuznets-curve` | same name | 1.667 | faithful | — | — |
| 31 | `laffer-curve` | same name | 1.631 | **differs** | drawing | Curve should be a smooth, upside down U shape |
| 32 | `long-run-costs` | same name | 1.537 | faithful | — | — |
| 33 | `long-run-phillips-curve` | same name | 1.833 | faithful | — | — |
| 34 | `lorenz-curve` | same name | 1.515 | faithful | — | — |
| 35 | `loss` | same name | 1.427 | faithful | — | — |
| 36 | `lras-classical` | same name | 1.478 | faithful | — | — |
| 37 | `lras-keynesian` | same name | 1.507 | faithful | — | — |
| 38 | `lras-shift` | same name | 2.809 | faithful | — | Shows classical |
| 39 | `lras-shift-keynesian` | `lras-shift` | 2.809 | faithful | — | Shows Keynesian |
| 40 | `market-equilibrium` | same name | 1.243 | faithful | — | — |
| 41 | `max-price` | same name | 1.462 | faithful | — | — |
| 42 | `min-price` | same name | 1.481 | faithful | — | — |
| 43 | `min-wage` | same name | 1.477 | faithful | — | — |
| 44 | `monopsony` | same name | 1.499 | faithful | — | — |
| 45 | `multiplier` | same name | 1.485 | faithful | — | — |
| 46 | `nationalisation-privatisation` | same name | 1.561 | faithful | amend | All curves need to be shifted left - currently they are all on the far right of the diagram space, not centered. |
| 47 | `negative-output-gap-classical` | same name | 1.469 | faithful | — | — |
| 48 | `negative-output-gap-keynesian` | same name | 1.485 | faithful | — | — |
| 49 | `normal-profit-imperfect-competition` | same name | 1.472 | **differs** | drawing | The AC curve has two requirements: it needs its lowest point to be where it intersects MC, and it needs to be touching the point/tangential where P,C meet AR (which it currently does). |
| 50 | `overconsumption` | same name | 1.356 | faithful | amend | Welfare loss should point to the shaded region, not the corner of the triangle. |
| 51 | `overproduction` | same name | 1.392 | faithful | amend | Welfare loss should point to the shaded region, not the corner of the triangle. |
| 52 | `perfect-competition-market-price` | same name | 2.820 | **differs** | drawing | The Revenue/Quantity Diagram needs its horizontal line extended to cover the width of the axis. |
| 53 | `perfect-competition-short-run-loss` | same name | 2.713 | **differs** | panel | This diagram needs to include the market diagram too (left hand PNG) otherwise it doesn't work |
| 54 | `perfect-competition-short-run-supernormal-profit` | same name | 2.766 | **differs** | panel | This diagram needs to include the market diagram too (left hand PNG) otherwise it doesn't work |
| 55 | `positive-output-gap-classical` | same name | 1.479 | faithful | — | — |
| 56 | `ppf-basic` | same name | 1.975 | faithful | — | — |
| 57 | `ppf-growth-decline` | same name | 1.865 | faithful | — | — |
| 58 | `ppf-short-run-growth` | same name | 1.553 | faithful | — | — |
| 59 | `price-discrimination` | same name | 3.372 | **differs** | panel | Missing the combined market - either needs to be included here or in a different diagram |
| 60 | `profit-max` | same name | 1.511 | faithful | — | — |
| 61 | `revenue-imperfect-competition` | same name | 2.647 | faithful | — | — |
| 62 | `revenue-max` | same name | 1.489 | faithful | — | — |
| 63 | `revenue-perfect-competition` | same name | 2.909 | faithful | — | — |
| 64 | `sales-max` | same name | 1.475 | faithful | — | — |
| 65 | `short-run-costs` | same name | 1.507 | faithful | amend | AFC should curve upwards more on the left tail, and the AC and AVC curves could be higher up as they arae squashed at the bottom. |
| 66 | `short-run-phillips-curve` | same name | 1.917 | faithful | — | — |
| 67 | `short-run-shutdown-condition` | same name | 2.542 | **differs** | panel | This shows the short-run situation where the firm should shut down. In the PNG there is also the short run situation where the firm should not shut down. This needs to be included either here or in a different diagram. |
| 68 | `sras-movements` | same name | 1.521 | faithful | — | — |
| 69 | `sras-shift` | same name | 1.473 | faithful | — | — |
| 70 | `sras-shift-left` | same name | 1.498 | faithful | — | — |
| 71 | `subsidy-gov-expenditure` | same name | 1.374 | faithful | — | — |
| 72 | `subsidy-incidence` | same name | 1.268 | faithful | — | — |
| 73 | `supernormal-profit` | same name | 1.501 | faithful | — | — |
| 74 | `supply-curve-shift` | same name | 1.274 | faithful | — | — |
| 75 | `supply-of-labour-market-individual` | same name | 2.446 | faithful | — | — |
| 76 | `tariff` | same name | 1.515 | faithful | — | — |
| 77 | `total-utility` | same name | 1.474 | faithful | — | — |
| 78 | `trade-cycle` | same name | 1.719 | faithful | — | — |
| 79 | `trade-union-competitive` | same name | 1.389 | faithful | — | — |
| 80 | `trade-union-monopsony` | same name | 1.392 | **differs** | drawing | There should also be a red line extending from the intersection of W(TU) and S=AC up along the S=AC curve |
| 81 | `underconsumption` | same name | 1.360 | faithful | amend | Welfare loss should point to the shaded region, not the corner of the triangle. |
| 82 | `underproduction` | same name | 1.486 | faithful | amend | Welfare loss should point to the shaded region, not the corner of the triangle. |
| 83 | `wage-determination` | same name | 1.569 | faithful | — | — |

---

# The repairs — state as of 2026-08-14

On branch `wave5-1-diagram-review`, off `31dcc4e`. **Nothing pushed, nothing
merged.** All 23 workflow steps green after every commit.

**All 16 "clean" repairs are DONE**, across 20 SVG files and three commits:

- **`6a2ae7c`** — the 6 label and annotation defects. The four welfare-loss
  leaders ended *at* a vertex, three of them outside the shading entirely; each
  now ends at the triangle's centroid. The two efficiency keys went to two lines
  per entry because `Productive efficiency: MC=AC` measures **321px** at 24px
  and would have run **112px past the 800px canvas**. Eliot chose
  `Supernormal profit / → dynamic efficiency` over naming the box after its
  consequence.
- **`8fc02da`** — four of the five curve-shape amendments.
- **`94301ce`** — the MC blade, and the kinked curve.

**The blade decision is the one worth carrying forward.** Eliot flagged the
hockey-stick shape on `collusion` alone, but that MC path is shared **byte-for-
byte across 13 SVGs**, 12 of which he had just marked faithful. He chose to
apply it to all 13. Only each file's **first segment** changes, so every
declared intersection in every file is untouched and
`verify_diagram_geometry.py` stays at 83 files, 0 flags. All 13 were rendered
and read individually, because the blade raises MC's left end 45px into space
occupied by something different in each.

**One thing I broke and fixed** — `c0f8e76`. The 5.1 review sheet added 166
`<img>` tags with no `width`/`height` and turned the workflow's 7th step red.
`verify_image_dimensions.py` enumerates through `git ls-files`, so `_working/`
is in scope, exactly like a published page. It never reached `main`.

## The four panel-drops

Eliot delegated the choice between a second panel and a second diagram, and the
answer is a second **panel** — not for layout reasons but because **each of
these SVGs is referenced by an existing flashcard**. A second file would leave
that card still showing half the figure, and adding a card is flashcards content
work needing its own approval. The panel repairs the card that already exists.

**The two-panel layout was not invented for this.** Three SVGs already use it on
the 800×600 canvas, and `supply-of-labour-market-individual` — passed as
faithful in this very review — is the exemplar: panels at x 70–370 and 460–760,
axes 120–460, panel titles at y=112.

| Diagram | State |
| --- | --- |
| `perfect-competition-short-run-supernormal-profit` | **DONE**, `7f89f3d` |
| `perfect-competition-short-run-loss` | **DONE**, `7f89f3d` |
| `price-discrimination` | **DONE differently**, `49a423f` — see below |
| `short-run-shutdown-condition` | **DONE**, `49a423f` |

**The method for the two that are done, and the one to reuse.** The firm panel
is **transformed, not redrawn**: `x' = 460 + (x-100)/2`, a **uniform** half
scale. Uniform is the whole point — DIAGRAM_STYLE requires exact 45° slopes and
computed intersections, and a non-uniform squeeze breaks both. The MC/AC
tangency transforms exactly instead of being re-eyeballed. The market panel is
drawn natively, and a dashed line carries P1 across the gap to the firm's
horizontal demand curve — the carry-across is the teaching point the
single-panel version could not make.

`perfect-competition-short-run-loss` needed an extra **60px lift** on top of the
transform: its price line is low in the original, and mapping it straight down
squashed the market equilibrium against the axis with no room for S and D. The
ground-truth PNG puts that price line mid-panel. A lift is a translation, so
nothing moves relative to anything else.

**Axis titles moved to their own row at y=524** on both, because the firm's `Q1`
label sits near the right of its panel and collided with `Quantity` at the
shared y=492.

## Still not started, and why

- **`comparative-advantage`** — Eliot's verdict asks for Germany to hold the
  absolute advantage in both goods. That reverses `CONTENT_ISSUES.md` #26 and
  changes every figure in the worked example on `4-1-2` and `2-6-2`, in prose.
  An economics rewrite, not a diagram fix. Needs its own instruction.
- **Wave 5.2, 5.3, 5.4.** 5.3 is still gated: it cannot proceed as a sweep while
  any panel-drop is open.

## All four panel-drops are closed, and one took the other route

`short-run-shutdown-condition` gained its second panel. Both panels are the same
drawing at a uniform half scale, so MC, AVC and ATC are **identical** between
them — which is the point, because the two cases differ *only* in the height of
demand. The keep-operating panel's AR and MR were **solved, not drawn**: they
share an intercept with MR at twice AR's slope, and the pair chosen puts MR
through MC at Q=460 with price 45.2 above AVC and 111.9 below ATC.

**`price-discrimination` took the separate-diagram route, and that was measured
rather than preferred.** Three panels on the locked 800×600 canvas gives 205px
each: the panel titles do not fit on one line, there is nowhere to put the
`AC=MC` label that is not over a curve, and at 400×300 each panel would be about
100px wide. The existing two-panel file is unchanged;
`price-discrimination-combined-market.svg` is new.

Its single price is **fixed by the construction, not chosen**: MR bisects the
horizontal distance under a straight AR, so P is the midpoint of the AR intercept
and the cost line — (165+380)/2 = **272.5** — whatever slope AR takes. That sits
between the **265** and **280** of the two sub-markets, which is the comparison
the pair exists to make.

**The new SVG is referenced by nothing.** A new diagram needs a flashcard to
consume it, and writing one is content work needing Eliot's approval, so no card
was added. Until one exists it is an unreferenced asset of exactly the class D38
had to adjudicate — recorded here rather than left for a future census to
rediscover and propose deleting.
