# Mobile navigation redesign — proposal and mock

**Status: waiting for Eliot's approval. Nothing in the template, nav.js or
main.css has been touched.** This folder is the static mock (`mock.html` —
open it with Live Server from the repo root so the site's fonts and icons
resolve) and the four screenshots beside it: 360px open and closed, 390px
with a second group expanded, and the money block in view.

## The two problems this fixes

1. **Robustness.** `#nav` is `display: none` under 768px and the hamburger
   and panel exist only after `js/components/nav.js` runs. If that script
   fails, a phone visitor has no navigation at all.
2. **Design (Eliot's brief).** The current panel is a long flat black list
   slid in from the side: no grouping, off-brand, and four rows ("Edexcel",
   "AQA" — `href="#"`) that do nothing when tapped.

## The mechanism (the robustness fix)

**A second nav block in `templates/header.html`, mobile-only, complete
without JavaScript.** The desktop `#nav` (768px+) is untouched — its nested
lists drive the hover dropdowns and stay exactly as they are. Below 768px
the new block renders **in the page flow**: grouped links inside native
`<details>`, so with JavaScript off a phone visitor gets the full menu —
groups open and close, every link works, nothing depends on a script.

`nav.js` then *enhances* that block into the sliding drawer: only once the
drawer exists does it get lifted out of the flow (a class on `body`, added
by the script — no script, no hiding). The old panel-building code and the
old panel go.

Because both nav blocks live in the same template file, they can only
drift if someone edits one and not the other; a unit test in
`scripts/tests/` will assert the two blocks carry the same set of hrefs.

## The design (what the mock shows)

- **White surface, brand accents.** White drawer, backdrop dimmed site-ink;
  small-caps section labels in the notes' darkened teal `#1f6b77`; red
  `#d52349` for icons, the current-page marker and the money block. The
  mobile title bar lightens to match (white, hairline border, red burger) —
  the one visual change outside the panel, flagged here deliberately.
- **Two labelled sections.** "Free resources" (Revision Notes, Practice
  Questions, Flashcards, Past Papers) and "Work with Eliot" (Tutoring,
  Marking, as red-tinted cards with subset icons — chalkboard-teacher and
  check-double, both already shipped).
- **Groups are native `<details>`.** The group row opens the group (plus
  rotates to ×, the FAQ's language — no new glyph, no re-subset); board
  names inside are **non-tappable small-caps labels**, which is what
  replaces the four dead `href="#"` rows. Every tappable row now navigates
  or visibly opens a group.
- **Hub links stay reachable.** Tapping a group name no longer navigates
  (it expands), so each group ends with an explicit hub row: "All revision
  notes", "All practice questions", and — missing from the current panel
  entirely — "All past papers" for `/past-papers/`.
- **Current page** gets a red left bar, tint and weight (Flashcards in the
  mock).

## Behaviour (implementation commitments, per the review)

Touch targets ≥ 44px (rows are 48px, sub-rows 44px) · panel scrolls
independently, body scroll locked while open · safe-area insets respected
(`viewport-fit=cover` + `env()` padding) · Esc and backdrop-tap close ·
focus trapped while open, returned to the hamburger on close ·
`aria-expanded` on the hamburger, `inert` kept on the page behind (the
current panel's standard) · slide suppressed under
`prefers-reduced-motion` (the new global reduce block already covers it).

## New visible strings (for approval)

| String | Where |
| --- | --- |
| Menu | drawer header |
| Free resources | section label |
| Work with Eliot | section label |
| All revision notes | hub row in the Revision Notes group |
| All practice questions | hub row in the Practice Questions group |
| All past papers | hub row in the Past Papers group |
| Close menu | aria-label on the × (not visible) |

Everything else reuses the header's existing link texts verbatim.

## Cost when approved

`templates/header.html` edit → full rebuild (`build.py`) →
`bake_templates.py --apply` → `verify_page_shell.py` pins reseeded and
listed in the PR → Text-Change trailers for the new baked strings →
sitemap as its own commit. All 463 pages change. Desktop (≥768px) renders
byte-identically except the removed dead-panel scripts.
