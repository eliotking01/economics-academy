# notes-data/

The source of truth for the 173 generated pages under `revision-notes/`.
Excluded from publishing.

- `topics/<board-dir>/<slug>.html` — a **verbatim byte slice** of that page's
  content, from `<main>` inwards. Not a template, not markdown: the exact bytes
  the page will carry.
- `topics/<board-dir>/<slug>.json` — its lifted metadata (`path`, `head`, `body`).
- `hubs/` — the same pair for the seven hub pages.

**The chrome on a topic page is NOT in its slice.** The previous/next topic
row at each end of `.notes-container` is spliced in by `build_notes_pages.py`
at build time, from the chain in `scripts/notes_sequence.py`; the sub-label,
byline, contents list and the whole tail after the last section (related
topics, the practice / flashcards / past-paper panels, author, services) come
from `scripts/notes_extras.py`, derived from data. Since the notes redesign
(2026-08-25, D61) three more derivations join them, all per-instance and
tolerant of hand-written variants: a `<p>` opening with a `key-definition`
chip gains `class="topic-definition"`, each `<div class="table-container">`
gains its scrollable-region attributes, and each diagram `<img>` is wrapped
in `<picture>` plus an `<a class="diagram-zoom">`, the first per page
promoted `fetchpriority="high"` unless it is `loading="lazy"`. Do not paste
any of those into a slice either - `docs/EDITING-NOTES.md` shows exactly
what an editor writes. The records' `pageStylesheets` name
`/css/pages/revision-notes-topic.css` on all 166 topics (the hubs differ);
`new_topic.py` copies a sibling record, so a new topic inherits it. Do not paste any of it into
a slice: a slice is a record of the page's *content*, and 166 hand-inserted
copies is the scripted bulk edit hard rule 6 forbids. **A topic slice ends at
its last `</section>`** - plus, on the Edexcel pages that carry diagrams, one
`<p class="notes-diagrams-link">` - and then the container close; the build
fails on anything else there. (Until 2026-08-23 every slice ended in a
`notes-cta` button box and two or three resource blocks; they were stripped
in the topic-tail redesign - `git log -- notes-data/topics` shows the one
commit, and it is the one commit that touched every slice without changing
a word of content. `seo/tools/rewrite_notes_meta.py` takes `dateModified`
from the slice's last commit, so do not take that commit as a content edit.)
A new topic gets its row and its tail automatically as soon as its hub links
to it and its `questions-data/` record exists.

**Edit here, then run `python3 scripts/build.py`.** Never edit the rendered
page in `revision-notes/`; the next build overwrites it. (`build_notes_pages.py`
on its own is fine for a quick look, but the glossary is extracted from these
pages too, so the full build is what keeps the tree consistent.)

`scripts/extract_notes_pages.py` is the one-off that created these from the
live pages. It defaults to a dry run and should not be needed again.

After any content edit, the glossary needs re-extracting too — definitions
are lifted from `key-definition` chips on these pages. `build.py` runs every
generator in the right order (the list is `scripts/site_layout.py`, declared
once), so do not chain them by hand:

```bash
python3 scripts/build.py
# commit, then:
python3 scripts/build.py --sitemap   # AFTER committing: lastmod comes from git
```
