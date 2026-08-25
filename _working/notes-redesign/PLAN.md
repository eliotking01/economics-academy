# Notes topic-page redesign — Gate 2 roll-out plan, for approval

The approved design (PROPOSAL.md revision 2) applied to all 166 topic
pages. Nothing under the published tree changes until Gate 3; every number
below was measured on this branch today, not assumed. The companion
`EDITING-NOTES-draft.md` is the editing guide that ships as
`docs/EDITING-NOTES.md`.

**The headline: this lands almost entirely in one new stylesheet, one new
JS file, and two small generator functions.** The slices are untouched, the
`<head>` is untouched, `page_shell.py` is untouched, the spine keeps its
one shape, and the roll-out is expected to need zero `Text-Change:` and
zero `Markup-Change:` trailers — the baked-page changes are additions and
attributes only.

---

## 1. Where each piece lives

| Piece | File | Change |
| --- | --- | --- |
| The new look | `css/pages/revision-notes-topic.css` — **new file**, the mock's `notes-redesign.css` verbatim (scoped `.revision-notes-content`, tokens in `:root` as the old sheet's are) | new |
| Which sheet the 166 load | `notes-data/topics/**/*.json` — `pageStylesheets` value only | scripted metadata edit, §3 |
| Definition cards | `scripts/notes_extras.py` — new `with_definition_cards()` | new function |
| Scrollable-table attributes | `scripts/notes_extras.py` — new `with_table_regions()` | new function |
| Both wired in | `notes_extras.apply_all()`, after `with_contents()` | one line each |
| Diagram zoom link + `fetchpriority` | `scripts/build_notes_pages.py` — `with_webp_pictures()` grows the `<a class="diagram-zoom">` wrapper and first-diagram promotion; docstring updated | extended |
| The enhancements | `js/components/notes.js` — **new file**: the mock's inline prototype, with the mark-as-revised key derived from `location.pathname` (no per-page wiring) | new |
| Loading it | `build_notes_pages.render()` emits `page_shell.script_tail(("/js/components/notes.js",))` for TOPIC records, the plain tail for hubs — the same `extra` mechanism quiz.js and flashcards.js already use, `defer` included | one line |
| `page_shell.py` | — | **no change** (head and skeleton untouched; the extra-script hook already exists) |
| The old sheet | `css/pages/revision-notes-textbook.css` | **no change, byte for byte** |
| The guide | `docs/EDITING-NOTES.md` from the draft; `notes-data/CLAUDE.md`, `revision-notes/CLAUDE.md` component table, `css/CLAUDE.md` token note updated to match | Gate 3 docs commit |

## 2. Every build-time transform, with its anchor measured across all 166

The existing transforms (sub-label, byline, h2 ids, contents, tail,
prev/next, WebP) are unchanged and their anchors re-verified at Gate 3 by
the build itself — each already fails loudly on a miss. The new ones:

**T1 — definition cards.** Anchor: a bare `<p>` whose first content is a
`key-definition` chip; the transform rewrites `<p>` to
`<p class="topic-definition">`. Measured today: **641 chips across the
166; 540 open a bare `<p>` (become cards); 0 chip-first paragraphs carry
any attribute on the `<p>`; 22 open an `<li>` (stay inline — a card
inside a bullet list breaks the list's rhythm, and this mirrors
`extract_glossary.py`'s chip-opens-the-block reading); 79 sit mid-sentence
(stay inline highlights). 0 odd `<span>` spellings — every chip is
literally `<span class="key-definition"`.** Hand-edit behaviour: tolerant
by construction — a chip anywhere else simply keeps the inline colour;
there is nothing to fail. Collision check: no slice contains
`topic-definition` today.

**T2 — scrollable tables.** Anchor: the literal `<div
class="table-container">`; the transform adds `tabindex="0" role="region"
aria-label="Scrollable table"`. Measured: **122 instances, all spelled
exactly that way, 0 with extra classes.** Hand-edit behaviour: a
container with an unexpected class list is left alone (renders, still
scrolls, loses only the keyboard focus stop) — a degradation, not a trap;
the pattern matches what `revision-notes/CLAUDE.md` tells an editor to
paste.

**T3 — diagram zoom + priority.** Extends the existing `with_webp_pictures()`
match (`<img>` with `src="/images/diagrams/….png"`, the measured pattern
the WebP wrapper already relies on): each match is wrapped
`<a class="diagram-zoom" href="<png>">…</a>` around the `<picture>` (or the
bare `<img>` where a twin were ever missing — today **0 of the diagram
images lack a WebP twin**), and the FIRST match on a page gains
`fetchpriority="high"` **only if it does not carry `loading="lazy"`**.
Measured: **93 pages match (the 94th `diagram-figure` page,
`edexcel-theme-4/4-1-2`, holds the site's one inline SVG `<img>` — not a
PNG, so it keeps its current rendering, deliberately); exactly 1 page
(`aqa-a2-macro/2-6-2-trade`) has a lazy first diagram and is simply not
promoted.** Collision check: no slice contains `diagram-zoom`.

**The slices are untouched.** `notes-data/topics/**/*.html` — zero edits,
zero proposals to edit them. The one scripted change under `notes-data/`
is metadata: each of the 166 `.json` records'
`pageStylesheets: ["/css/pages/revision-notes-textbook.css"]` becomes
`["/css/pages/revision-notes-topic.css"]` (measured: all 166 carry exactly
that one-element list today). Not prose, declared here as the brief allows.
**No date trap:** `rewrite_notes_meta.py` takes `dateModified` from the
`.html` slice's last commit (checked at its call sites, lines 277/302) —
the `.json` edit cannot move any "Updated" date, and `dateModified` is not
refreshed for this change (D58 precedent).

## 3. The editing story

The source format stays one hand-written HTML slice per topic — no
Markdown case to make. Every new transform above states its hand-edit
behaviour; none depends on indentation or line position, and none can
silently skip a page (T1/T2 are per-instance and inert on no match; the
build's existing hard anchors — container line, spec-alert unit, slice
ending — keep their fail-with-filename messages). `EDITING-NOTES-draft.md`
beside this file is the guide, two pages, snippet-per-component; Gate 3
proves it by following it on a scratch slice (add a paragraph, a
definition, a diagram, a worked example; build; then break the slice
ending and confirm the message names the file and the fix).

## 4. Every verifier and test that changes — smallest amendments

| File | Amendment | Why |
| --- | --- | --- |
| `scripts/verify_page_shell.py` | ONE line: `FAMILY_SCRIPT["notes-topic"] = "/js/components/notes.js"` | the family-script relation is the declared mechanism; check 2's tail literal, `EXPECTED_SHAPES` and `EXPECTED_NOTES_SPINES` (still 1 — the spine profiles top-level blocks of `.notes-container` and none is added or removed; the shape table counts DISTINCT heads/tails/css-sets per family, and every count is unchanged by a sheet rename) all stay as they are. If the run proves any pin wrong, `--reseed` in the same commit with the diff quoted in the message |
| `scripts/verify_contrast.py` | the four notes entries stay (textbook.css still ships for the three other pages) and **new pairs are added** for the new sheet: the four small-caps label colours on their tints, the pink chip on white and on the definition tint, muted meta on white, the flow end-node white-on-teal | the pins follow the tokens; the two chip pairs the a11y pass flagged are finally closed |
| `scripts/tests/test_notes_extras.py` | new cases: chip-first `<p>` gains the class, mid-sentence and `<li>` chips do not; table-container gains the three attributes exactly once; totals against the measured 540/122 | tests beside the new pure functions |
| `scripts/tests/test_page_shell_helpers.py` | **no change** — `page_shell.py` is untouched | |
| `scripts/verify_css_load_order.py` | **no change** — it asserts order and the named `TWO_SHEET_PAGES`, not sheet names; a new `/css/pages/` sheet is in scope automatically | |
| `scripts/verify_image_dimensions.py` | **no change** — it parses `<img>`/`<source>`/`<picture>` tags by regex; the `<a>` wrapper is invisible to it | confirmed by reading its parser |
| `scripts/verify_notes_sequence.py` | **no change** — both rows stay | |
| `seo/tools/verify_seo.py` | **no change expected** (titles, descriptions, twins, author anchors all untouched) — run and confirmed at Gate 3, not assumed | |
| `compare_trees.py` fixtures | suite run on this branch at Gate 2 (result recorded below before commit); run again at Gate 3 | they gripped the pre-D58 tail last time |
| `verify_text_integrity.py` / `verify_markup_integrity.py --strict` | expected **zero trailers of either kind**: no visible baked text changes, and the markup changes are additions (both checks fire on losses/changes) | `suggest_trailers.py` is the arbiter before the commit; if it prints anything, that is a defect in this plan to investigate, not a trailer to paste |

Also confirmed no-change, with the reason: `verify_links.py` (the new
zoom `href`s point at PNGs already in the tree), `verify_icons.py` (no new
glyph — the back-to-top arrow is a text character), `verify_glossary.py` /
`extract_glossary.py` (the class lands on the `<p>`, the chip and its
siblings are byte-identical), `build_search_index.py` (reads `<h1>`/`<h2>`
text, unchanged).

## 5. The three other pages that load the old sheet

`revision-notes/macroeconomics-diagrams.html`,
`microeconomics-diagrams.html` and `macro-application/` keep loading
`revision-notes-textbook.css`, which does not change by one byte, so they
render exactly as today. Proof at Gate 3: the sheet's diff is empty
(`git diff` shows no hunk in it), plus a before/after screenshot pair of
each of the three at 1280 — belt and braces on top of `verify_generated.py`.

## 6. Gate 3 sequence

1. **Implementation commit:** new sheet, `notes.js`, the two
   `notes_extras` functions, the `build_notes_pages` changes, the 166
   record edits, the `FAMILY_SCRIPT` line, the contrast pairs, the new
   tests — then `python3 scripts/build.py` and commit source + rebuilt
   pages together (the tree must match its generators at every commit).
   `suggest_trailers.py` run first; expected silent.
2. **Verify:** the unit tests, then the full `verify.yml` list locally,
   `verify_generated.py`, `verify_seo.py`, `build_sitemap.py --check`
   (stale, as expected, until step 4).
3. **Look:** Live Server at 1280 and 360, JS on and off, print preview —
   Demand, 2-1-3 (densest), 1-6-6 (single section), 1-1-1 (plain shell), a
   MathJax page, one page from each remaining directory, 4-1-2 (the SVG
   exception), and the three old-sheet pages against `main`. Then the
   editing-story proof from §3. Findings reported as what was seen.
4. **Docs commit:** `docs/EDITING-NOTES.md`, D61 in
   `docs/audit/DECISIONS.md`, the PROGRESS.md section (and the stale
   "IN REVIEW" heading on the a11y pass fixed to LIVE, PR #26, `745f9cb2`),
   `revision-notes/CLAUDE.md` component table, `notes-data/CLAUDE.md`,
   `css/CLAUDE.md` token note, `scripts/CLAUDE.md` if the generator list
   description needs a word.
5. **Sitemap commit:** `python3 scripts/build.py --sitemap` after the
   content commits (166 `lastmod` values move), committed separately.
6. **PR** with before/after screenshots at both widths and the string
   list; merge will be a merge commit. **Stop before merging; never push
   to main.**

## 7. Risks, and the rollback

- **A content pattern the mocks never met.** The two mocks plus the
  component sheet cover every library component, but 166 hand-written
  pages hold surprises by definition. Mitigation: the transforms are
  inert-on-no-match rather than strict, the suite is green before the PR,
  and step 3 eyeballs the extremes (densest, thinnest, SVG, maths).
- **The theme cascade.** Two known traps are already handled in the sheet
  (`#main` background at ID specificity; the button `color: #fff
  !important`). Anything similar found at step 3 gets the same
  counter-declaration treatment, named in a comment.
- **compare-trees fixtures.** Run on this branch at Gate 2:
  `python3 scripts/test_compare_trees.py` → "all 39 cases behaved as
  expected", exit 0. Run again at Gate 3 after the rebuild; any fixture
  gripping notes internals is repaired on the branch, not after the merge.
- **localStorage:** keys are namespaced (`ea-revised:<pathname>`), reads
  and writes wrapped in try/catch, and the control is JS-injected, so no
  variant of failure leaves a dead element on the page.
- **Rollback** is one `git revert` of the merge commit: the record edits,
  the new files and the rebuilt pages all revert cleanly; no URL is
  created, moved or removed anywhere in this project.

## 8. Open points (none blocking, my positions stated)

- The **22 list-item definitions** stay inline-styled — flagged in §2; say
  if you would rather they card like the paragraph ones and I will treat
  it as a design change to mock first.
- The **one SVG diagram** (4-1-2) keeps today's rendering and does not get
  tap-to-enlarge in this pass; it is also OWNER-TODO's diagram-work
  territory.
- `2-6-2-trade`'s lazy first diagram looks like an authoring accident; I
  will log it in `docs/REVIEW-NOTES.md` rather than change it (the fix is
  a slice edit — yours).

Approve, and Gate 3 starts.
