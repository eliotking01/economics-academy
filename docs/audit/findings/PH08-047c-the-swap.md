# Wave 5.3 — the swap, measured and deferred

**Measured 2026-08-14**, on `wave5-2-diagram-gaps` off `37060f5`. **No page was
changed.** Eliot's decision, taken on the measurements below: record and hold
until Wave 5.2's 21 diagrams exist.

5.3 points the notes' `<img>` tags at the hand-drawn blue SVGs instead of the
black PNGs — **231 tags across 85 pages**, re-derived at HEAD. It is a `src`
and a size attribute; no wording moves.

## Two numbers from PH08-047 did not survive, and one of them I repeated first

### The 29% shrinkage does not exist

PH08-047's closing section, and D46 after it, say a swapped SVG renders
**"798 px of white against 1,118 px for the two PNGs beside it"** on
`3-4-4-oligopoly.html`, and conclude that PH08-047 step 3's prescription —
declare the viewBox — "would shrink every swapped diagram by 29%".

Measured in a real browser at six viewports by
`docs/audit/scripts/harness/measure_diagram_render.py`:

```
viewport 1920   collusion.png=800   kinked-demand-curve.png=800   game-theory.svg=800
viewport 1680   collusion.png=800   kinked-demand-curve.png=800   game-theory.svg=800
viewport 1440   collusion.png=800   kinked-demand-curve.png=800   game-theory.svg=800
viewport 1280   collusion.png=800   kinked-demand-curve.png=800   game-theory.svg=800
viewport 1100   collusion.png=800   kinked-demand-curve.png=800   game-theory.svg=800
viewport  980   collusion.png=800   kinked-demand-curve.png=800   game-theory.svg=800
```

The SVG already on that page and the two PNGs beside it render at **exactly the
same width**, because `css/pages/revision-notes-textbook.css:622` caps
`.diagram-figure` at `max-width: 800px`. That rule predates the finding; only
its selector changed, in `6814fa2` on 2026-08-10.

**The 1,118 is the `.notes-container`.** The ancestor chain of that image:

```
img.diagram-image=800
figure.diagram-figure=800
section.=1022
div.notes-container=1120
div.container=1120
main.revision-notes-content=1440
```

The width the SVG was compared against was the image's **great-grandparent**.

**I restated that pair as fact at the start of this session before measuring
it.** It is recorded here rather than quietly corrected, because the whole
reason PH08-047's own numbers were re-derived is that a repeated number carries
no evidence.

### So the second "constraint" dissolves with the first

PH08-047 says fixing the shrinkage "means changing the SVG files, the
stylesheet, or the checker — a decision, not an attribute edit." There is
nothing to fix. **Declaring the viewBox is correct**, and it is also the **only**
declaration `verify_image_dimensions.py` accepts: `DIAGRAM_STYLE.md` forbids an
absolute `width`/`height` on the `<svg>` element, so the checker falls back to
the viewBox, and any other declared size fails CI step 7.

## The real constraint runs the other way: every diagram gets TALLER

Swapping the two PNGs on that page for their same-named SVGs at 800×600:

```
file                      W before  H before   W after   H after       dH
collusion.png                  800     500.8       800     605.5   +104.7
kinked-demand-curve.png        800     512.8       800     605.5    +92.7
game-theory.svg                800     605.5       800     605.5     +0.0
```

Width unchanged; height up about 100 px per diagram. The cause is already in
the record — every SVG viewBox is 4:3 and the PNGs are mostly near 1.5, so
**the aspect changes on 77 of 78 pairs** (D46). The widest PNGs grow hardest:
`price-discrimination` at 3.372 aspect goes from roughly 231 px tall to 583 px.

**There is no layout shift** — the dimensions are declared, so the box is
reserved correctly either way. The pages simply get longer.

## Weight is a real saving and is not the reason

| | Bytes |
| --- | ---: |
| The 78 swappable pairs, as PNG | **3.77 MiB** |
| The same 78 as SVG | **192 KiB** |

95% lighter. But Wave 4.1 already took all 112 PNGs from 26.21 to 5.41 MiB and
the mean notes-page image payload with it, so this is a further ~3.6 MiB across
the whole site rather than a page-speed problem. **The honest case for 5.3 is
consistency with the flashcards, and it should be argued on that.**

## And consistency is what a swap today would not deliver

Because Wave 5.2 drew nothing, **64 `<img>` across 30 pages have no SVG to swap
to**. Overlaying that on the 85 swappable pages:

```
swappable now (same-name SVG, excluding comparative-advantage):  231 tags on 85 pages
would remain a black PNG (no SVG exists):                         64 tags on 30 pages
pages that would then show BLUE and BLACK side by side:                     20 pages
```

The 20 include `1-2-2-demand`, `1-2-4-supply`, `1-2-6-price-determination`,
`1-2-8-producer-consumer-surplus`, `1-5-11-consumer-and-producer-surplus`,
`3-4-2-perfect-competition`, `3-5-3-wage-determination` and **both diagram
galleries**. Today every diagram on a page matches every other diagram on it;
after a sweep, 20 pages would not. **A partial swap makes the site look less
considered, not more.**

## The gate, as recorded

D46 gates 5.3 on `comparative-advantage` and on Wave 5.2's diagrams. Worth
stating precisely: `comparative-advantage.svg` is **already live in the notes on
3 pages**, so it is a defect on the site rather than a blocker for the other 77
pairs. The binding gate is the 21 undrawn diagrams.

## What to do when it is picked up

1. Draw Wave 5.2's 21 (see `PH08-047b-missing-diagrams.md`), or accept a
   permanently mixed set and decide that deliberately.
2. Settle `comparative-advantage`, which is a prose rewrite on `4-1-2` and
   `2-6-2` and needs its own instruction.
3. Then swap all 78 in one commit: `src` to `/images/diagrams/svg/<stem>.svg`,
   `width="800" height="600"`, editing the `notes-data/` slices and rebuilding —
   never the pages.
4. Expect pages to lengthen by ~100 px per diagram and check the two galleries
   at mobile width, where the grid cells are 282.7 px.
