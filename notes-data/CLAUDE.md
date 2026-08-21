# notes-data/

The source of truth for the 173 generated pages under `revision-notes/`.
Excluded from publishing.

- `topics/<board-dir>/<slug>.html` — a **verbatim byte slice** of that page's
  content, from `<main>` inwards. Not a template, not markdown: the exact bytes
  the page will carry.
- `topics/<board-dir>/<slug>.json` — its lifted metadata (`path`, `head`, `body`).
- `hubs/` — the same pair for the seven hub pages.

**One thing on a topic page is NOT in its slice.** The previous/next topic row
at each end of `.notes-container` is spliced in by `build_notes_pages.py` at
build time, from the chain in `scripts/notes_sequence.py`. Do not paste it into
a slice: a slice is a record of the page's *content*, and 166 hand-inserted
copies is the scripted bulk edit hard rule 6 forbids. A new topic gets its row
automatically as soon as its hub links to it.

**Edit here, then run `python3 scripts/build_notes_pages.py`.** Never edit the
rendered page in `revision-notes/`; the next build overwrites it.

`scripts/extract_notes_pages.py` is the one-off that created these from the
live pages. It defaults to a dry run and should not be needed again.

After any content edit, the glossary may need re-extracting too — definitions
are lifted from `key-definition` chips on these pages:

```bash
python3 scripts/build_notes_pages.py
python3 scripts/extract_glossary.py && python3 scripts/build_glossary.py
python3 scripts/build_sitemap.py     # AFTER committing: lastmod comes from git
```
