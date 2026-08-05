# Diagram style guide (SVG flashcard diagrams)

**Status: LOCKED** (Eliot approved the three proof diagrams — demand shift,
indirect tax incidence, negative production externality — on 2026-08-04,
including the palette, the shift arrow, in-diagram welfare-loss labelling and
compact curve identities). Every diagram follows this file; changes to it
require re-checking every shipped SVG.

Ground truth: each SVG is drawn from visual inspection of its existing PNG in
`images/diagrams/` **and** the figure caption on the notes page that uses it —
never from a filename. Board conventions (Edexcel A 9EC0 vs AQA 7136) win over
the PNG where they conflict; conflicts are logged in docs/CONTENT_ISSUES.md.

## Canvas

- `viewBox="0 0 800 600"` (4:3), no fixed width/height on the `<svg>` element;
  the page's `<img>` supplies intrinsic size and `max-width: 100%`.
- No background rect — pages and print are white.
- Plot area: x from 100 to 690, y from 60 to 520 (i.e. margins: left 100,
  bottom 80, top 60, right 110). The right margin holds end-of-curve labels;
  the left and bottom hold axis titles.

## Palette

| Use | Colour | Notes |
| --- | --- | --- |
| Axes, axis titles, point labels | `#333333` | near-black, matches site text |
| Original curves (D, S, AD, AS…) | `#1d70b8` | dark blue, prints legibly in greyscale |
| Shifted/new curves (D1, S1…) and shift arrows | `#d52349` | brand accent |
| Second original curve where two originals must differ (e.g. MPC vs MSC) | `#0f7b6c` | dark teal |
| Guide (dashed) lines to axes | `#767676` | |
| Shaded areas | fill of the associated curve colour at `fill-opacity="0.15"` | welfare-loss triangles `#767676` at `0.25` |

## Strokes

- Axes: 2.5px, square caps, plain L (no axis arrowheads — matches the notes'
  PNGs).
- Curves: 3.5px, `stroke-linecap="round"`. Straight-line curves are `<line>`/
  `<path>` with no curvature — A-Level convention draws D and S straight;
  Keynesian AS and genuinely curved relationships use smooth paths.
- **Geometry is computed, never eyeballed.** Straight curves default to exact
  45° screen slopes (|Δx| = |Δy|); every intersection a guide marks is
  derived algebraically from the curve endpoints before the guides are drawn.
  The first proof batch shipped a demand curve at slope 0.86 against guides
  computed for slope 1, and every marker sat ~12px off — visual QA missed it.
- Guide lines: 2px, `stroke-dasharray="6 5"`.
- Shift arrows: 2.5px in the shifted curve's colour, with an arrowhead
  `<marker>`, drawn between the curves roughly mid-way along them.

## Text

- `font-family="Helvetica Neue, Helvetica, Arial, sans-serif"`. Deliberately
  **not** Source Sans Pro: SVGs referenced via `<img>` cannot load webfonts,
  so the site font would silently fall back differently per machine. The
  humanist system stack is visually close and predictable.
- Sizes at 800×600: axis titles 26px; curve labels 26px bold; point/quantity
  labels on axes 24px; annotation text (e.g. "Excess demand") 24px.
- Axis titles follow the notes' PNGs: y-axis "Price" (rotated −90° or
  horizontal at the axis top, whichever the ground-truth PNG uses), x-axis
  "Quantity". Market-specific variants ("Price of labour (W)", "Real GDP")
  follow the ground truth.
- Curve naming matches the notes captions: `D`, `D1`, `S`, `S1` — plain
  digits, no Unicode subscripts. Curve identity labels use a compact equals
  with no spaces (`S=MPC`, `D=MPB=MSB`), matching the notes' PNGs — and long
  right-hand labels must be width-checked against the 800px canvas edge.
- Axis value labels are `P`, `P1`, `Q`, `Q1` at the guide-line feet, 24px.
- Minimum clearance: 8px between any label and any stroke it does not name;
  curve labels sit just past the curve's end, right of the plot area.

## Accessibility

Every SVG starts:

```svg
<svg viewBox="0 0 800 600" role="img" aria-labelledby="t d"
     xmlns="http://www.w3.org/2000/svg">
  <title id="t">…one-line name…</title>
  <desc id="d">…what the diagram shows, as a sentence or two…</desc>
```

The card record's alt text (used on the `<img>`) describes the same content;
`<title>`/`<desc>` make the file self-describing when opened directly.

## Schematic flow diagrams (no axes)

Approved by Eliot 2026-08-05 with the circular-flow pair. For diagrams
that are boxes/rings and arrows rather than curves on axes:

- The flow itself (the ring) is an original curve: `#1d70b8` at 3.5px,
  with short 3.5px directional stubs carrying arrowhead markers laid
  over it.
- Flows **entering** the system (injections) are dark teal `#0f7b6c`;
  flows **leaving** it (withdrawals) are the brand accent `#d52349` —
  both 2.5px with matching arrowhead markers, like shift arrows.
- Agent names (Firms, Households) are 26px bold `#333333`; all other
  labels 24px, same clearance rules as axis diagrams.
- The `<!-- geometry -->` comment is still mandatory; declare no points
  and state why (`schematic flow diagram: no axis geometry to declare`).
  The visual pass carries the QA weight for this class.

## Board variants

Where Edexcel A and AQA conventions differ (e.g. AQA's emphasis on the
Keynesian LRAS curve vs Edexcel using both classical and Keynesian), separate
files suffixed `-edexcel` / `-aqa`. Shared-convention diagrams get one file,
no suffix.

## File naming

`images/diagrams/svg/<concept>.svg`, lowercase kebab-case, matching the
ground-truth PNG's name where one exists (`demand-curve-shift.svg` beside
`demand-curve-shift.png`), so the pairing is greppable.

## Self-QA loop (standing rule 4)

0. Declare the diagram's economics in a `<!-- geometry -->` comment —
   `intersections:` points that must lie on two curves, `on-curve:` points
   that must lie on one — then run
   `python3 scripts/verify_diagram_geometry.py`; zero flags required. The
   declaration is mandatory: the checker fails any SVG without one.
1. Render:
   `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless
   --screenshot=<out>.png --window-size=800,600 --hide-scrollbars <file>.svg`
2. Read the PNG back visually. Check: no overlapping or clipped labels;
   every curve is labelled and the labels name the right curves; shaded areas
   cover exactly the region claimed; arrows point the right way. For
   intersections, additionally render zoomed close-ups (copy the SVG with a
   cropped `viewBox` around each junction) — full-size renders hide a 10px
   miss.
3. Repeat at `--window-size=400,300` and confirm labels are still legible at
   mobile scale. Headless Chrome reserves scrollbar width at this size, so a
   ~15px right-edge crop in the render is an artifact, not an SVG fault —
   judge label legibility only. (In pages the SVG is an `<img>` and scales
   correctly.)
4. Only then present for approval, in batches.
