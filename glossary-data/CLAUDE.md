# glossary-data/

Source for the three glossary pages at `/revision-notes/glossary/`. Excluded
from publishing. `scripts/build_glossary.py` renders the pages and runs Prettier
over its own output, so generating twice is byte-identical.

**The definitions are the notes' own words.** Every entry is lifted verbatim from
a `<span class="key-definition">` chip and the paragraph that follows it on a
topic page, and `scripts/verify_glossary.py` check 1 re-reads the notes and fails
if a shipped definition no longer appears in its source page.

**There are exactly two declared exceptions, and both are counted on every verify
run so neither goes quiet:**

1. **`authored.json`** — definitions written for the glossary, covering concepts
   the notes teach without ever defining and that a specification requires.
   Tagged `origin="authored"` through to the page and exempt from the verbatim
   check. **This file is meant to shrink:** move a definition into its notes page
   as a chip and the extractor picks it up, at which point the build errors until
   the authored copy is deleted. Reviewed in `_working/glossary/authored-review.md`.
2. **The `rewrite` block in `curation.json`** — replaces the **lead-in** of
   definitions the notes wrote with the term as sentence subject
   (*"Globalisation is the increasing integration…"*) so they read as
   definitions. A rule replaces a **leading substring only**; the few that add
   wording are marked `adds` or `not-a-definition`. The build **fails** if `from`
   is no longer how the definition opens, so rewording a notes page cannot
   silently re-point a rule. Instructed by Eliot on 2026-08-07, explicitly
   overriding the rule below.

**Outside those two, a term that reads badly is fixed IN THE NOTES, then
re-extracted — never edited here.**

**When a definition reads badly, look on the page before writing anything.**
Three cases here turned out to have the real definition already in the notes,
just somewhere the extractor could not reach — under a plain
`<strong>Effect:</strong>` instead of a chip (`Maximum Price`), or in the `<ul>`
below the chip (the five trading blocs). `excludeSources` + `authored.json`, and
`attachList`, fixed both without inventing a word.

## Files

- `terms.json` — **generated** by `scripts/extract_glossary.py`. Never hand-edit.
- `curation.json` — hand-written judgement: the non-term stop-list, display
  casing, alias merges, approved table harvests, the `capitalise` and `rewrite`
  blocks. Kept separate so re-extraction cannot destroy it.
- `authored.json` — the exception above.

**Capitalisation and lead-in rewrites are applied at render time**, never in
`terms.json` — the data must stay byte-identical to the notes or the verbatim
check stops meaning anything.

Because of this, **check 1 proves the extraction is faithful, not the page.** Do
not describe the glossary as word-for-word without that qualification.

Formulae are **KaTeX pre-rendered to static HTML at build time**, CSS and woff2
self-hosted in `css/vendor/katex/`. Every emitted KaTeX block needs
`<!-- prettier-ignore -->` before it or Prettier reflows it and the build stops
being idempotent. The notes pages still use MathJax 3, so the same formula looks
slightly different in the two places.

The full glossary is real HTML in the page, not fetched — it must be readable
with JavaScript off. `js/components/glossary-filter.js` only enhances.
**Search matches the term name only**, ranked exact → prefix → word start →
contains → fuzzy. There is **no synonyms field**: abbreviations match only
because the notes put them in the term (`Price Elasticity of Demand (PED)`) and
the tokeniser splits on the brackets.
