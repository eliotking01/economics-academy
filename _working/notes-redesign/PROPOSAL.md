# Notes topic-page redesign — Gate 1 proposal, for approval

Branch `feature/notes-redesign`. Nothing under the published tree has changed:
this folder holds a full mock of the redesigned Demand page, a component
sheet showing every library component in the new design, screenshots at both
widths with JS on and off, a print PDF, and the proof that the economics
content is byte-identical. Open in Live Server:

- `/_working/notes-redesign/1-2-2-demand.html` — the redesigned page
- `/_working/notes-redesign/components.html` — the component sheet

`notes-redesign.css` beside them is the proposed page sheet (it would ship as
`css/pages/revision-notes-topic.css` — the sheet decision is below).
`components.css` is catalogue layout only and ships nowhere.

| Evidence | File |
| --- | --- |
| 1280, JS on, top / full page | `mock-1280-top.png`, `mock-1280-full.png` |
| 1024 — the width the contents rail appears | `mock-1024-top.png` |
| 360, JS on, top / full page | `mock-360-top.png`, `mock-360-full.png` |
| JS off, both widths (identical page minus enhancements) | `mock-1280-nojs.png`, `mock-360-nojs.png` |
| Print preview | `mock-print.pdf` |
| Component sheet, both widths | `components-1280-full.png`, `components-360-full.png` |
| Content-identity proof | `python3 _working/notes-redesign/check_content_identity.py` |

---

## 1. The design audit — what is wrong with the current page

Looked at properly at 1280 and 360 (nobody had; OWNER-TODO said so):

1. **The measure is the biggest problem.** Prose runs the full width of a
   1,088px card — 110–120 characters per line in Merriweather. Nobody can
   read that for twenty minutes; every serious reading site (and Save My
   Exams) sets notes in a 600–750px column.
2. **Seven components compete in seven voices.** Five callout boxes with
   floating pill labels in five colours, two inline chips, gradient bars on
   every h2, gradient table headers, dashed rules on h3, drop shadows on
   everything. A student cannot tell what to scan for because everything
   shouts. Two of the pills fail AA outright (white on #27ae60 at 2.9:1,
   white on #f57c00 at 2.7:1 — the pair the a11y pass left for this
   overhaul).
3. **The inline definition chip breaks when it wraps.** An inline span with
   padding, border-left, radius and shadow splits apart across lines — and
   definitions are the single thing 157 of 166 pages carry.
4. **Dated furniture.** The white card on grey with drop shadow, the teal
   h1 underline, gradient h2 bars, dashed link underlines that turn pink —
   2015-theme grammar that reads as less trustworthy than the content is.
5. **The eye goes to the chrome, not the content.** At 1280 the strongest
   visual elements are the h2 gradient bars and the pill labels; at 360 the
   heading arrives after a captions-only nav row that serves the 1% who want
   the previous topic before reading this one.
6. **Wasted width.** At 1280 the card is 1,200px, yet diagrams cap at 800px
   and tables sprawl. Nothing uses the width well because nothing decided
   what the width was for.

What the current page already gets right (kept, not re-litigated): the D58
tail order with the paid ask last, board-and-unit sub-label under the h1, the
named author, the contents list, metric-matched font fallbacks, the derived
counts, the spec-alert's first-paint board differentiation.

## 2. The design — a reading page, not a card

**What the page is for.** A student on a phone the night before a mock reads
one topic for twenty minutes, screenshots the diagram, and either comes back
tomorrow or doesn't. Everything below serves reading stamina, scanability of
definitions/tips/examples, and a reason to return — and the ranking case
follows from that, not the other way round.

**What the page carries, in order** (top prev/next row is the one removal —
flagged in §3):

1. Breadcrumb (unchanged, site-wide component)
2. **h1**, left-aligned, no underline — then one quiet meta line (board ·
   module · code, updated date, **"N min read"** derived from the schema's
   existing `timeRequired`), then the byline
3. **Specification panel** — same position, same words, restyled from a
   shouting purple box to a quiet reference panel; its own bold
   "Specification Coverage:" lead replaces the redundant floating pill
4. **"On this page"** — below 1024px the in-flow box it is today; from
   1024px **the same element** becomes a sticky right rail that tracks the
   current section (CSS grid moves it — one element, no duplicate markup,
   works with JS off; the highlight is the JS enhancement)
5. **The teaching sections** in a 38em (~72-character) reading column,
   hairline rules between sections, calm typographic headings
6. "Mark as revised" (JS-injected, §5)
7. The D58 tail, wording and order untouched, restyled to the same grammar
8. Previous / next — the bottom row, as cards

**The component system.** One grammar for everything: a 3px left rule, a
near-white tint, a small-caps label in the component's text-safe colour.
Definitions pink, exam tips green, evaluation orange, worked examples navy,
specification purple, navigation and labels teal. No gradients, no floating
pills, no shadows. The two failing chips are fixed by construction: labels
are now dark-on-tint text (green #1c7a42 at 5.1:1, orange darkened to
#a04d00 at 5.6:1). The full contrast table is in §7.

**Definitions look like definitions.** A paragraph that *opens* with a
`key-definition` chip becomes a definition card (pink tint, pink rule) via a
build-time class on the `<p>` — the same "chip opens the block" test
`extract_glossary.py` already uses, so the card set and the glossary agree by
construction. A mid-sentence chip stays inline and just takes the colour.
Chip class and text untouched; the glossary extraction is unaffected.

**Diagrams.** Full column width (bigger than today on phones), hairline
frame, and the generator wraps each `<picture>` in an `<a>` to the PNG —
tap-to-enlarge that works with JS off; `notes.js` upgrades it to a `<dialog>`
lightbox. First diagram gets `fetchpriority="high"` at build time (the
`loading="lazy"` precedent). Image bytes, alt, width/height untouched.

**Tables.** Horizontal scroll stays the phone answer, but the
"↔ Scroll to view full table" strip goes: the cue is the visibly clipped
column plus edge fades that appear only while there is more to see. The
generator adds `tabindex="0" role="region" aria-label="Scrollable table"` so
keyboard users can scroll too. Active at every width now — a four-column
table is wider than the reading column on desktop as well.

**Typography.** Merriweather 400/700 for prose at 1em/1.75 (the old sheet's
`font-weight: 800` was a synthesis request the browser resolved to 700
anyway); Source Sans Pro for headings, interface, tables and captions.
Native list markers in teal at a hanging indent replace the absolutely
positioned custom bullets.

## 3. Changes that need a flag, and what I rejected

**The top prev/next row is removed** (my recommendation — say if you want it
back, it is one generator function and one CSS block). The 2026-08-21 pass
compressed it because it was pushing the h1 down 219–279px on a phone; this
completes that direction rather than reversing it: the measured problem was
the row's cost above the heading, and its benefit ("finished one topic, move
to the next") lives at the bottom, where the identical row remains with both
destinations. Nothing is lost from the page's link set; `rel=prev/next`
survive on the bottom row. It needs `verify_notes_sequence.py` amended (it
asserts a row at each end) and is the main `Markup-Change:`/`Text-Change:`
on all 166.

**Rejected, and why:**

- **A "Key terms on this page" strip** — it duplicates text already on the
  page, costs vertical space, and the chips that read "Definition:" need the
  extractor's heading fallback plus human review to name. Styling the
  definitions in place gets the scanning benefit with none of that.
- **Dark mode** — 211 opaque white-background diagram PNGs would need a
  treatment; not cheap, not complete, so per the brief: skipped.
- **Tabs / collapsed sections** — everything stays visible on first paint;
  crawlers, no-JS visitors and students get the same page (house rule).
- **Card-per-row responsive tables** — rebuilding 83 pages of comparison
  tables as stacked cards means markup surgery on hand-written slices for a
  pattern that reads worse for side-by-side comparison. Scroll, cued
  honestly, is the right trade.
- **Markdown source** — the slices stay HTML (hard rule 6 history; tables,
  formulae and worked examples need HTML anyway). Not proposed.
- **CSS-numbered h2s** — numbering would change what a student reads without
  changing the bytes; headings render exactly as written.
- **A new font family** — see §6.
- **A left-hand contents rail** — "on this page" on the right is the
  convention readers know (MDN, GitHub, docs sites); left would fight the
  breadcrumb-to-h1 reading line.

**Also rehomed/notable:** the spec-alert stays in position (restyled only) —
re-homing it lower was considered and dropped: it is the board
differentiator on first paint and genuinely useful ("what you need to be
able to do") before reading. The `application` component (used by 0 pages)
is kept in the library and the sheet.

## 4. Every chrome string that changes

**New (baked into the page):**

| String | Where |
| --- | --- |
| `N min read` (e.g. "3 min read") | meta line; derived from the record's existing `timeRequired` (PT3M → 3), never hand-typed |
| `Scrollable table` | `aria-label` on each `.table-container`, added at build time |

**New (JS-injected only — never in the baked page):**

| String | Where |
| --- | --- |
| `Mark as revised` / `✓ Revised` | the toggle after the last section |
| `Saved on this device, like your flashcard progress.` | its note |
| `Back to top` | the scroll button's `aria-label` |
| `Close` | the diagram lightbox button |

**Changed (CSS-generated labels, restyled and recased):**

| Today | Proposed |
| --- | --- |
| `EXAM TIP` (white on #27ae60, 2.9:1) | `Exam tip` (#1c7a42 on green tint, 5.1:1) |
| `EVALUATION` (white on #f57c00, 2.7:1) | `Evaluation` (#a04d00 on orange tint, 5.6:1) |
| `APPLICATION` | `Application` (navy-2 on tint) |

**Dropped:**

| String | Why |
| --- | --- |
| `SPECIFICATION` pill | the content's own bold "Specification Coverage:" lead already labels it |
| `WORKED EXAMPLE` pill | every worked example carries its own visible "Worked Example: …" h3 |
| `↔ Scroll to view full table` | replaced by the clipped-column + edge-fade cue and the keyboard-accessible region |
| One `Previous topic` / `Next topic` instance per page | the top row goes; both strings remain in the bottom row |

**Unchanged:** every D58 tail string, "On this page", "Updated", the byline
and bio, the breadcrumb, "Topic list", all `notesTeaser` and derived
past-paper sentences.

## 5. Reasons to come back (all JS-injected, all optional to approve)

- **Reading progress bar** — 3px teal, top of viewport; hidden under
  `prefers-reduced-motion`.
- **Scrollspy** — the rail highlights the section you are in (≥1024px).
- **Back to top** — appears after two screens.
- **Mark as revised** — localStorage, keyed per page, in the flashcards'
  "saved on this device" idiom; injected after the last section so a no-JS
  page shows no dead control. (A theme-wide "what have I covered" view on
  the hubs is a natural follow-up, deliberately not in this scope.)
- **Diagram lightbox** — native `<dialog>` over the no-JS `<a>`-to-PNG.

In production all of this is one new file, `js/components/notes.js`
(~3 KB), loaded by the 166 topic pages only (the per-family extra-script
mechanism, not the site-wide tail — the five-script tail is untouched). The
mock inlines it for reviewability; the code is the prototype.

## 6. The font decision

**No change: Merriweather 400/400i/700 for prose, Source Sans Pro for
everything else. Zero new bytes.** Merriweather is a genuinely good reading
serif, it is distinctive against the sans-everything competitors, the
metric-matched fallback machinery already exists for it, and the calm the
current page lacks comes from layout and colour discipline, not the face.
The one typographic correction: bold is requested at 700, the cut that
actually loads. (If you would rather the notes read sans like the rest of
the site, that is a one-line stack change to test in a revision — but I
recommend keeping the serif.)

## 7. Accessibility

Every colour used as text was computed against the ground it sits on
(WCAG 2.1 relative luminance; script in the session log, values re-checkable
with `scripts/verify_contrast.py`'s own maths):

| Pair | Ratio | AA (4.5 / 3.0 large) |
| --- | --- | --- |
| body #333 on white | 12.6:1 | pass |
| navy #1a3e72 headings on white | 10.6:1 | pass |
| navy-2 #2a5c8d h3 on white | 7.0:1 | pass |
| teal #1f6b77 links/labels on white | 6.1:1 | pass |
| teal on wash #f8fafc | 5.9:1 | pass |
| muted #5a6b80 meta on white | 5.5:1 | pass |
| pink #c2185b chips on white | 5.9:1 | pass |
| pink on definition tint #fdf6f8 | 5.5:1 | pass |
| green #1c7a42 on tip tint #f2faf5 | 5.1:1 | pass |
| **orange #a04d00 on eval tint #fef8f2** | **5.6:1** | **pass — was 2.7:1** |
| purple #5e35b1 on spec tint #f7f5fb | 7.7:1 | pass |
| white on teal #1f6b77 (flow end node) | 6.1:1 | pass |

Also designed in: the h1→h2→h3 outline and every stable id unchanged;
`scroll-margin-top` on section anchors; `:focus-visible` rings on every
interactive element; scrollable tables reachable by keyboard
(`tabindex="0"`, labelled region); the lightbox is a native `<dialog>`
(Esc, backdrop click, focus handling for free); `aria-pressed` on the
revised toggle; the progress bar `aria-hidden` and gone under
`prefers-reduced-motion`; smooth scroll gated on the same query; JS off =
same content, no dead controls (screenshots prove it). Not yet done — Gate 3
work: an axe pass and a VoiceOver walk of the finished pages.

## 8. Weight

| | Today | Mock | Notes |
| --- | --- | --- | --- |
| Page stylesheet | 46,601 B (10.4 KB gz) | 39,003 B (8.5 KB gz) | new sheet, comments included; the 166 stop paying for the galleries' rules |
| Page HTML (Demand) | 37,938 B | ~36.9 KB estimated shipped | head unchanged; top nav row −1.5 KB; zoom/definition/aria additions +0.4 KB |
| Requests | 3 CSS + 3 Merriweather + FA + images | same **+ notes.js (~3 KB, one file, cached across all 166)** | no new font, no new origin, nothing render-blocking added |
| LCP element | h1 / first diagram | same, first diagram now `fetchpriority="high"` | |
| CLS | fallback-matched fonts | same mechanism, same faces; rail is CSS-placed at first paint; JS injects only fixed-position overlays and one below-content block before first paint | |

## 9. Content identity — proven, not asserted

`python3 _working/notes-redesign/check_content_identity.py` strips tags from
the content region (h1, spec-alert, every section) of the live generated page
and of the mock and diffs:

```
text identical: 3052 characters, 523 words
images identical: 2 (src, alt) pairs, same order
CONTENT IDENTITY OK
```

Every heading, paragraph, list, table, figure caption, alt text and the
section order are byte-identical. The additions are attributes and wrappers
(the definition class, the zoom anchor, the table region attributes, ids the
generator already adds) — markup, not words.

## 10. What adding content will look like (draft snippets)

The full guide becomes `docs/EDITING-NOTES.md` at Gate 3. The rule the
design keeps: **everything derived is derived at build time** — ids, the
contents list, definition cards, zoom links, WebP twins, table attributes,
figure behaviour. You paste plain HTML into the slice and run
`python3 scripts/build.py`; there is no id to invent and no attribute to
remember.

```html
<!-- A new section (the contents list picks it up by itself) -->
<section>
  <h2>Heading</h2>
  <p>Text.</p>
</section>

<!-- A definition (glossary and definition card both derive from this) -->
<p>
  <span class="key-definition">Term:</span> The definition.
</p>

<!-- An exam tip: one <p>, no heading; bold lead sentence -->
<div class="exam-tip">
  <p><strong>Lead sentence.</strong> Two or three more.</p>
</div>

<!-- A diagram: PNG into images/diagrams/, then
     python3 scripts/build_diagram_webp.py --apply -->
<figure class="diagram-figure">
  <img
    src="/images/diagrams/NAME.png"
    alt="What the diagram shows"
    class="diagram-image"
    width="1731"
    height="1280"
    loading="lazy"
  />
  <figcaption class="diagram-caption">Figure N: caption.</figcaption>
</figure>

<!-- A comparison table (always inside the container) -->
<div class="table-container">
  <table class="concept-table">
    <thead><tr><th>…</th></tr></thead>
    <tbody><tr><td>…</td></tr></tbody>
  </table>
</div>

<!-- A formula -->
<!-- prettier-ignore -->
<div class="formula-box">
  \[ \text{Formula} = \frac{a}{b} \]
</div>

<!-- A worked example -->
<div class="worked-example">
  <h3>Worked Example: Title</h3>
  <p>Setup…</p>
  <table class="calculation-table">
    <tr><td>Step</td><td>Value</td></tr>
    <tr><td><strong>Answer</strong></td><td>…</td></tr>
  </table>
  <p>Sentence interpreting the number.</p>
</div>
```

(`loading="lazy"` on any diagram after the first; the build promotes the
first one itself. Everything else in the table above is exactly what the
slices already contain.)

## 11. The sheet decision (for Gate 2, lean stated now)

**Recommendation: the 166 topic pages load a new
`css/pages/revision-notes-topic.css`; the two diagram galleries and
macro-application keep `revision-notes-textbook.css` unchanged** — those
three pages render byte-for-byte as today, proven by a screenshot pair and
`verify_css_load_order.py`. Cost: a scripted edit of `pageStylesheets` in
the 166 records (metadata, not prose — a scripted edit is acceptable there
and will be declared as such) plus the verifier's sheet lists. The
alternative — rewriting `revision-notes-textbook.css` in place — makes the
galleries' rendering depend on a sheet designed for a different page shape,
which is how the current sheet got its duplicated blocks in the first place.

## 12. Verifiers and tests I expect Gate 3 to touch

| Check | Why |
| --- | --- |
| `verify_page_shell.py` | `EXPECTED_NOTES_SPINES` reseed (top row gone); notes family gains an extra script (`notes.js`); per-family CSS set changes with the new sheet name |
| `verify_notes_sequence.py` | asserts a nav row at each end; becomes bottom-only |
| `verify_contrast.py` | the four notes pairs re-pointed at the new tokens; new pairs added for every label/tint above |
| `verify_css_load_order.py` | the 166 load the new sheet; the three others keep the old one |
| `verify_image_dimensions.py` | must tolerate the `<a>` wrapper around `<picture>` |
| `scripts/tests/test_notes_extras.py` | chrome-string and structure changes |
| `compare_trees.py` fixtures | checked on the branch (they gripped the pre-D58 tail last time) |
| `verify_text_integrity.py` / `verify_markup_integrity.py --strict` | 166 `Text-Change:` (read time added, one Previous/Next caption pair removed) and 166 `Markup-Change:` (top row) trailers, generated by `suggest_trailers.py` |
| `seo/tools/verify_seo.py` | expected green unchanged (byline, twins, titles untouched) — verified, not assumed |

`page_shell.SCRIPT_TAIL` is untouched — `notes.js` is a family extra, not a
tail change.

## 13. Questions for you (everything else I have taken a position on)

1. **The top prev/next row** — removed in the mock, one flag away from
   staying. Approve the removal?
2. **"N min read"** — happy with the wording and with it sitting between the
   updated date and nothing else?
3. **"Mark as revised"** — worth having at all? (Cheap, but it is a feature
   promise; the localStorage idiom matches the flashcards.)
4. **The byline credentials at 360px** run to three small lines. Keep in
   full (as mocked), or hide the credentials half below 600px in one CSS
   rule (name stays)?
5. Anything on the component sheet you want treated differently before I
   plan the roll-out?

Reply with approvals, edits or rejections and Gate 2 (the roll-out plan
across all 166, every anchor measured, every verifier amendment written
down) follows. Expecting at least one round of revisions — say what to
change and the mock comes back updated.
