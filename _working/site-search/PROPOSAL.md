# Site-wide search — mock for approval

**Branch `feature/site-search`. Nothing here touches a published page yet.**
This folder is the static mock plus the real index generator; the header
template, the shipped JS/CSS and the build wiring follow once the design and
the wording below are approved.

## See it

Serve the repo root (Live Server in VSCode works) and open
`/_working/site-search/mock.html`. Click the magnifier in the header's
top-right, or press `/`, then type. Worth trying:

- `monopsony` — the glossary definition floats to the top, whole, with links
  to both board glossaries; the notes results underneath find the AQA
  labour-market pages through their own section headings.
- `theme 2 flashcards` — resolves straight to the deck.
- `how much is marking` — the marking page and the two marking FAQs.
- `monetry policy` — the typo still finds Monetary Policy everywhere.
- Clear the box — quick links, never a blank panel.

Screenshots in this folder: `mock-desktop-closed.png` (the header icon),
`mock-desktop-empty.png`, `mock-desktop-m.png`, `mock-desktop-monopsony.png`,
`mock-desktop-flashcards.png`, `mock-desktop-marking.png`,
`mock-desktop-typo.png`, and `mock-360-monopsony.png` (full-screen overlay at
phone width, rendered in a 360px iframe per the hub-redesign method).

## What it searches, and the index

`scripts/build_search_index.py` (in this folder's parent `scripts/`, already
written) builds **`/search-index.json`** — one static file, generated, never
hand-edited:

| Source | What goes in |
| --- | --- |
| The 166 topic pages | Title, board, unit, spec code from the topic's `questions-data` record; the page's own `<h2>` headings as match text. Each topic also drives its practice-questions row and, where the topic has a question-bank page (same volume gate as the page tail), that row too. |
| The glossary | Every term and formula. The definition text is `build_glossary.ld_description()` — the same words the glossary page shows, curation applied. A term on both boards shows the Edexcel wording and links to both anchors. |
| Flashcards | The six decks, `deckTitle` from `flashcards-data/`. |
| Pages | Hand-written pages and the resource hubs — title extracted from each page's own `<h1>` at build time; each FAQ question indexed separately, linking to its anchor. |

**Deliberately excluded:** the individual past-paper exam questions — the
bank keeps its own purpose-built finder.

**Size: 112,904 bytes raw, 31,342 gzipped** (599 records) — under the
150 KB / 40 KB budget. Fetched once, lazily, the first time the overlay
opens; never on page load. Two runs of the generator produce identical bytes.

**Proposed location: `/search-index.json` at the repo root** — the same
profile as `sitemap.xml`: generated, fetched at runtime, not a page. (The
alternatives were `/js/search-index.json`, which mixes a generated file into
a hand-written directory, or a new `search/` directory for one file.) It is
a published file, so it will be listed with the runtime-fetched JSON in
`_config.yml`'s "deliberately NOT excluded" comment.

## Decisions taken in this mock (flag anything you'd change)

1. **The header control is a visible search box, not a bare icon** —
   Eliot's call, 2026-08-24: a pink pill (magnifier + "Search…") centred
   above the site title, in the brand palette (`#fdf6f8` fill, `#f3c6d1`
   border, `#b01d3c` text, `#d52349` icon). On desktop it floats in the
   header's existing 5em top padding, so nothing moves; below 768px it
   sits in normal flow above the title and the header grows ~3em to fit —
   baked markup, there from first paint, so no layout shift.
2. **No dead control without JavaScript**: that control is an
   `<a href="/revision-notes/">` — a real destination with scripting
   off — and the script upgrades it to open the overlay. (The alternative
   was a box that only exists when JS runs.)
3. **The magnifier is already in the Font Awesome subset** (`fa-search`,
   used by the FAQ's own search box), so no subsetter re-run is needed.
4. **On phones** the overlay is full-screen, the input is over 16px (no iOS
   zoom), and the search bar stays pinned while results scroll. The fixed
   mobile title bar (the hamburger bar) gains a search button too, added by
   the script beside the existing toggle.
5. **Ranking**: groups in a fixed order — Revision notes → Glossary →
   Practice & flashcards → Pages — capped at 6/5/5/4 rows. Within a group:
   title word-match beats title substring beats everything else; exact
   title match gets a large bonus; ties break by shorter title. Typo
   tolerance reuses `question-search.js`'s bounded-edit-distance matcher,
   and only runs when an exact pass finds nothing (otherwise "marking"
   would surface fuzzy "Making" pages above the marking page — caught in
   this mock, screenshot on file).
6. **Stopwords**: how/much/is/the/… are dropped from a query unless the
   whole query is stopwords, so "how much is marking" searches "marking".
7. **A query that IS a glossary term** floats that one definition card to
   the very top with the definition shown whole — the group itself is not
   promoted. Keyboard Enter on the card goes to the first board's glossary
   anchor; the card also carries a link per board.
8. **GA4**: one standard `search` event with `search_term`, fired when a
   result is chosen (not per keystroke), only if `gtag` exists — the same
   consent-gated no-op pattern as `track.js`.
9. **Accessibility**: `role="dialog"` + `aria-modal`, labelled input
   (combobox pattern, `aria-activedescendant`), arrow keys move, Enter
   opens, Esc closes, backdrop click closes, focus trapped inside and
   returned to the opener on close, `prefers-reduced-motion` honoured (the
   only animation is a 0.16s fade-in, removed for those users).

## Every new string (the approval list)

One string is baked into every page's header — the visible "Search…" on
the new control — so the rebuild commit will carry the `Text-Change:`
trailers `verify_text_integrity.py` asks for. Everything else is rendered
by the script.

| Where | String |
| --- | --- |
| The header search box (visible, on all 463 pages) | "Search…" |
| Header link, title-bar button, dialog, input (aria-labels) | "Search this site" |
| Input placeholder | "Search topics, definitions, resources…" |
| Close button (aria-label; shows ×) | "Close search" |
| Group headings | "Revision notes" · "Glossary" · "Practice & flashcards" · "Pages" |
| Result meta labels | "Practice questions" · "Past paper questions" · "Flashcards" · "Glossary" · "Formula" · "FAQ" · "Tutoring" · "Marking" · "Contact" · "About" · "Privacy" · "Revision notes" · "Diagram gallery" · "Past papers" · "Economics Academy" |
| Empty state | "Try a topic, a term, or a page — or jump straight in:" |
| Quick links (empty, no-results and failure states) | "Revision notes" · "Practice questions" · "Flashcards" · "Past papers" · "Glossary & formulae" |
| No results | "Nothing for '&lt;query&gt;' — try a topic name or a glossary term." |
| Index failed to load | "Search couldn't load. Check your connection and try again, or jump straight to a section:" |
| While fetching | "Loading…" |
| Definition card | "In the glossary: Edexcel · AQA" |
| Keyboard hint (desktop only) | "↑ ↓ to move · Enter to open · Esc to close" |

## The synonym list (match text only, never displayed)

Curated in `scripts/build_search_index.py` (`PAGES`); tune freely.

| Page | Synonyms |
| --- | --- |
| / | home start |
| /tutoring.html | tutor tutoring lessons online one to one 1-to-1 group price cost book intro call free call |
| /marking.html | marking marked essay feedback 25 marker paper marking service price cost send an essay |
| /contact.html | contact email enquiry message get in touch |
| /about.html | about eliot king who tutor credentials dbs experience |
| /faq.html | faq questions answers help |
| /privacy.html | privacy cookies analytics consent data policy |
| /revision-notes/ | revision notes free |
| /revision-notes/glossary/ | glossary definitions formulae formulas key terms |
| /revision-notes/macro-application/ | macro application uk economy applied examples |
| /revision-notes/microeconomics-diagrams.html | diagrams graphs curves micro microeconomics |
| /revision-notes/macroeconomics-diagrams.html | diagrams graphs curves macro macroeconomics |
| /practice-questions/ | practice questions quiz mcq multiple choice test |
| /flashcards/ | flashcards cards decks spaced repetition |
| /past-papers/ | past papers pdf question papers mark schemes |
| /past-papers/edexcel/ | edexcel past papers mark schemes 9ec0 8ec0 |
| /past-papers/aqa/ | aqa past papers mark schemes 7136 |
| /past-papers/ocr/ | ocr past papers mark schemes h460 |
| /past-papers/edexcel-b/ | edexcel b past papers mark schemes 9eb0 |
| /past-paper-questions/ | past paper questions real exam questions search finder by topic |

(The 12 board hubs and the 2 board glossaries are indexed by their own
`<h1>`s with no synonyms; topic/practice/deck rows carry fixed group words —
"quiz mcq multiple choice test", "flashcards cards deck revise", "real
exam" — in the script, not the payload.)

## What implementation will touch (after approval)

- `templates/header.html` — the one `<a>` — then the full rebuild
  (`python3 scripts/build.py`), touching all 463 pages' baked header.
- `js/components/site-search.js` (this folder's draft, moved) appended to
  `page_shell.SCRIPT_TAIL` **and** `verify_page_shell.py`'s independent
  `SCRIPT_TAIL` literal — the deliberate two-file pin.
- The `.site-search` CSS block onto the end of `css/main.css` (site-wide
  component, like the consent bar).
- `scripts/build_search_index.py` wired into `site_layout.GENERATORS`
  (last content generator), so `build.py` runs it and a stale index fails
  `verify_generated.py` in CI.
- `search-index.json` committed; `_config.yml` comment noting it stays
  published. No sitemap change (it is not a page). A unit test beside the
  generator and a node test for the matcher, following
  `test_question_search.js`.
- Any further `verify_page_shell.py` pins the rebuild reveals — every one
  will be listed in the PR.
