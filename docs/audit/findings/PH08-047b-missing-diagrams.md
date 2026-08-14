# Wave 5.2 — how many diagrams are actually missing, and why the count was wrong

**Measured 2026-08-14**, on `wave5-2-diagram-gaps` off `37060f5`. Nothing was
drawn: Eliot's instruction was to take the measurement and stop, and the three
grid diagrams below are a `DIAGRAM_STYLE.md` decision he has deliberately left
open. This file is the record so the next session does not re-derive it.

The evidence is `_working/diagram-review/gaps.py`, which builds a side-by-side
sheet of all 28 files and refuses to run if its row list has drifted from disk.

## The headline

**The roadmap's "28 missing diagrams" is arithmetic, not a measurement.** It is
`106 PNGs − 78 same-name pairs`. Looked at:

```
already drawn under another filename    6   ( 11 panels, 17 live <img> on 13 pages)
drawn as part of a larger diagram       1   (  1 panel,   3 live <img> on  3 pages)
genuinely missing                      21   ( 43 panels, 44 live <img> on 20 pages)
```

**Nothing a student sees depends on any of the 21.** The public flashcard
payloads reference **83** SVGs and **not one** of these 28 stems, so the only
route from a new SVG to a student is a new flashcard (content work, needs
approval) or Wave 5.3's swap. 5.2 is stock-building.

## The six that were already drawn

Each is a wide PNG that was split into one SVG per panel, under names that do
not match the PNG. The pairing for the first three is Eliot's own 5.1 verdict;
the last three were checked panel by panel while building the sheet.

| PNG | Drawn as | Evidence |
| --- | --- | --- |
| `exchange-rates` | `exchange-rate-appreciation` + `-depreciation` | PH08-047 rows 19, 20 — Eliot named which panel each takes |
| `Indirect-tax-incidence-elastic-inelastic` | `indirect-tax-elastic-demand` + `-inelastic-demand` | PH08-047 rows 22, 25 |
| `trade-union` | `trade-union-competitive` + `-monopsony` | PH08-047 rows 79, 80; the monopsony half was a `differs`, repaired in 5.1 |
| `ad-shift-right-classical-keynesian` | `keynesian-ad-shift-right` + `classical-ad-shift-right` | Left panel Keynesian, right classical; same PL1/PL2, Y1/Y2/Yfe, AD1/AD2, LRAS1 labels |
| `long-run-growth-ad-lras` | `classical-lras-shift-right` + `keynesian-lras-shift-right` | Both draw LRAS1→LRAS2 against fixed AD. The Keynesian SVG says Y1/Y2 where the PNG says Yfe1/Yfe2 — a label difference, not a different diagram |
| `sras-ad-shift-right` | `ad-shift-right` | Single panel each. SRAS fixed, AD1→AD2, PL1→PL2, Y1→Y2. Only the filenames disagree |

`ppf-long-run-growth` is the seventh and is a judgement call rather than a
finding: `ppf-growth-decline.svg` draws PPF1 outward to PPF2 **and** inward to
PPF3, so it contains the notes' figure and adds a case the caption never
mentions. Left open.

## A same-name prefix means nothing, and two cases prove it

**`demand-curve-shift` is not `demand-curve-movement`.** One draws D1→D2; the
other draws a movement along a single curve between points A and B — extension
and contraction. Different concept, and the one A-Level students most often get
wrong.

**`lras-classical` and `lras-keynesian` do not cover `ad-lras-equilibrium`.**
They draw the LRAS curve alone, with no AD curve and no equilibrium. The PNG's
entire point is where AD meets LRAS at PL1.

`demand-increase` fails the same test against `demand-curve-shift`: the
candidate has no supply curve and no equilibrium change, where the PNG moves
equilibrium from P1,Q1 to P2,Q2.

## Aspect ratio predicts panel count for the 83 pairs and NOT for these 28

This is the result worth carrying forward, because it inverts a screen that
worked last wave. PH08-047 and D46 established that a PNG at ≥1.9 aspect
predicts the panel-drop class — true of the pairs, and **false here**:

```
price-elasticity-demand-ranges   aspect 1.559   FIVE  panels
price-elasticity-supply-ranges   aspect 1.146   FOUR  panels   <- narrowest of all 28
shifts-in-equilibrium            aspect 1.202   FOUR  panels
```

All three sit below the 1.9 line, and all three are the most expensive rows on
the list. **A width screen would have called the three hardest diagrams cheap.**
Meanwhile `consumer-producer-surplus-price-discrimination-before` is 1.504 and
is a single panel — the drawing sits left with the `MC=AC=S` line running out to
the right, which is what inflates the aspect.

The rule that survives: **count the panels, per file, by looking.** Nothing
about the file's shape substitutes for it.

## The three grid diagrams cannot go on the locked canvas

D46 measured three panels on the locked 800×600 canvas at **205px each** and
rejected it for `price-discrimination` — the panel titles do not fit on one
line, there is nowhere for the `AC=MC` label that is not over a curve, and each
panel would be ~100px wide on mobile. Four and five panels are strictly worse.

So these three are not a drawing task. Drawing them needs either a second
canvas size in `DIAGRAM_STYLE.md` — whose status line requires re-checking every
shipped SVG, **84 files** — or splitting each figure into one file per panel,
which is 13 files and leaves no single drawing matching the notes' figure.

**Eliot, 2026-08-14: leave them as PNGs and decide separately.** Recorded so a
future census does not read three unpaired PNGs as an oversight.

## The 21 real gaps

| Diagram | Panels | Viewed? |
| --- | ---: | --- |
| `price-elasticity-demand-ranges` | 5 | yes |
| `price-elasticity-supply-ranges` | 4 | yes |
| `shifts-in-equilibrium` | 4 | yes |
| `ad-lras-equilibrium` | 2 | yes |
| `perfect-competition-profit-to-longrun` | 2 | yes |
| `perfect-competition-loss-to-longrun` | 2 | yes |
| `consumer-producer-surplus-competitive-monopoly` | 2 | yes |
| `consumer-producer-surplus-price-discrimination-after` | 2 | yes |
| `surplus-demand-increase` | 2 | yes |
| `joint-demand` | 2 | yes |
| `composite-demand` | 2 | yes |
| `surplus-supply-increase` | 2 | **inferred from its twin** |
| `joint-supply` | 2 | **inferred from its page-mates** |
| `derived-demand` | 2 | **inferred from its page-mates** |
| `competitive-demand` | 2 | **inferred from its page-mates** |
| `demand-curve-movement` | 1 | yes |
| `demand-increase` | 1 | yes |
| `consumer-producer-surplus-price-discrimination-before` | 1 | yes |
| `net-welfare-loss-monopoly` | 1 | yes |
| `supply-curve-movement` | 1 | **inferred from its twin** |
| `supply-increase` | 1 | **inferred from its twin** |

**Six panel counts are inferred rather than viewed** and say so both here and on
the sheet, in red. They are not measurements and must not be cited as ones.

Two of the two-panel rows are worth a note when they are drawn. The two
`perfect-competition-*-to-longrun` figures are the **adjustment** to long-run
equilibrium — entry or exit shifting market supply, the firm ending at P2,C2
with AC minimum on MC — and are a different diagram from the short-run pair 5.1
rebuilt, not an extension of it. And
`consumer-producer-surplus-price-discrimination-after` sits next to the
deliberately unreferenced `price-discrimination-combined-market.svg` that D46
records as Eliot's to place; the two are related and neither is proposed here.

## What this does not settle

5.3 is gated on these 21 **and** on `comparative-advantage`, which is out of
scope by instruction. So 5.3 cannot proceed as a sweep whatever happens to 5.2,
and drawing the 21 buys nothing until both gates clear.
