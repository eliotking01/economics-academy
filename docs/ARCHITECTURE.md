# How a page is assembled

Standalone HTML, no includes and no partials. Everything is duplicated per file.
Re-derive any count here with the script named beside it; do not trust the
number written down.

## The split

`python3 scripts/verify_page_shell.py` prints the split on its first line:
463 published pages, 17 of them hand-written.

- **446 pages** get their `<head>`, wrapper and script tail from
  `scripts/page_shell.py`, which all five page generators import.
- **17 pages** are hand-written and get theirs from
  `scripts/bake_templates.py --apply`. Run `bake_templates.py` with no flag to
  list them. They are the 9 root pages (permanently out of `page_shell` scope,
  `docs/audit/DECISIONS.md` D34), the 5 `past-papers/` hubs and the 3
  `revision-notes/` non-topic pages.

`page_shell.SCRIPT_TAIL` is the single place the script tail is declared.
`verify_page_shell.py` check 2 restates it as an independent literal, so changing
the tail has to change two files in the same commit. The tail is `nav.js`,
`track.js`, `main.js`: `js/components/track.js` is the GA4 conversion tracking
(`begin_checkout`, `purchase`, `generate_lead`, `intro_call_booked`, `sign_up`,
`cta_click`) — its header comment lists every event and its parameters, and
it is on every page because the CTA events are delegated on `document`.

## The header and footer are baked in at build time

Into all 463 pages. **Nothing is fetched at page load.**
`templates/header.html` and `templates/footer.html` remain the single source of
truth. `js/components/nav.js` builds the mobile `#navPanel` and `#titleBar` from
`#nav` and adds the two things CSS cannot do for the desktop dropdowns; the
dropdowns themselves are CSS, so they work with scripting off.

**Editing the nav is a rebuild, not a one-file edit** — see the command block in
the root `CLAUDE.md`.

`verify_page_shell.py` **check 9** is what makes the 463 copies safe: it lifts
the block back out of every page and requires it to equal the template byte for
byte, and asserts 0 pages still carry a runtime placeholder. A nav edit that
reaches 462 pages fails there rather than shipping.

## What a new page needs

The gtag block, `<html lang="en-GB">`, title, meta description, canonical, OG and
Twitter cards, JSON-LD, the favicon/manifest set, `/css/main.css`, its own
`/css/pages/<page>.css`, the script tail (**cite `page_shell.SCRIPT_TAIL`**), and
the baked header and footer blocks. Add it to the sitemap by running
`build_sitemap.py`. If it is hand-written rather than generated, add it to
`bake_templates.py`'s `EXPECTED` count in the same commit or that script refuses
to run.

Topic pages carry two JSON-LD blocks — `LearningResource` and `BreadcrumbList` —
and load MathJax 3 from jsDelivr only if they use `\( … \)`.

## Board identity is recorded once

In `boards-data/boards.json`, read by five generators through
`scripts/board_data.py`. **Editing a board name or slug is a two-file commit:**
`verify_boards.py` keeps an independent restatement of the whole record in
`PINNED`, because its comparison against the generators is circular now that they
read it. `--show` reprints the table.

**The record holds a name PER CONSUMER, and collapsing them rewrites live pages.**
Theme 2 ships as three different strings — `names.taxonomy` with an em dash in
`taxonomy.json` and the notes hub `<h1>`, `names.flashcards` with a hyphen in the
decks, and `names.practiceQuestionsButton` as "Theme 2: The UK Economy" on the
practice-questions hub. All three are correct. `board_data.py` therefore hands
back the record and never a canonical "name of a group"; **do not give it one.**

**Its group order is published output too** — `BOARD_ORDER` is that order's index
and it sorts every board index page, which is what
`board_data.EXPECTED_NOTES_DIRS` guards.

Prose that names a board is page copy, not board identity, and stays in the
generator that prints it: `build_glossary.BOARD_COPY`,
`build_questions.HUB_SECTIONS` and the hub's own meta description.

## Generated assets that must not be hand-edited

- `css/fontawesome-all.min.css` is a **subset**, not the full library, despite
  the name. It is kept under that name so 463 `<head>` blocks do not have to
  change.
- `webfonts/fa-solid-900.woff2` is subsetted from the full font in
  `_working/fontawesome/`.
- The diagram PNGs in `images/diagrams/` are re-encoded to a 64-colour palette.

Adding an icon means adding its rule to the stylesheet **and** re-running the
subsetter — `verify_icons.py` fails if you forget, because a subset font renders
a missing glyph as nothing at all, silently.

## Layout

```
revision-notes/{edexcel-theme-1..4,aqa-a2-micro,aqa-a2-macro}/  topic pages - GENERATED
revision-notes/{macro,micro}economics-diagrams.html             diagram galleries
revision-notes/macro-application/                               real-world data page
revision-notes/glossary/{,edexcel-a/,aqa/}                      GENERATED
past-papers/{aqa,edexcel,edexcel-b,ocr}/{a-level,as-level}/paper-N/   281 PDFs
practice-questions/, past-paper-questions/, flashcards/         GENERATED
templates/{header,footer}.html                                  baked in at build time
css/main.css                                                    site-wide
css/pages/<page>.css                                            one per page
js/components/, js/data/                                        hand-written; the rest is vendor
images/diagrams/                                                note diagrams (+ svg/ for flashcards)
*-data/                                                         the sources; all excluded
_working/, _archive/                                            excluded by the underscore rule
```

Root holds the commercial and utility pages: `index`, `tutoring`, `marking`,
`about`, `contact`, `faq`, `privacy`, `confirmation`, `404`.

Names are lowercase kebab-case throughout. Topic pages are
`1-2-3-short-title-slug.html` — spec code with dots as hyphens. Paper PDFs are
`{board}-{level}-economics-paper-{n}-{month}-{year}-{question-paper|mark-scheme}.pdf`.
