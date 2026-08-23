# scripts/

Excluded from publishing. **Python standard library only** — everything CI runs
must stay that way.

## The eight generators

Each owns its output. Never hand-edit what a generator writes; edit the source
and re-run. **`python3 scripts/build.py` runs them all, in order, then bakes
the 17 hand-written pages and runs `verify_page_shell.py`**; `build.py
--sitemap` runs the sitemap afterwards, once the content is committed. The
list and its order are declared once, in `site_layout.py`, which both
`build.py` and `verify_generated.py` import — never restate it. The table
below is a description, not a recipe. `verify_generated.py` re-runs all
eight in a throwaway worktree and diffs against the committed tree, so drift
cannot ship.

Three generators format their output with Prettier. The call and the pinned
version live in `prettier_util.py` only (mirrored as a devDependency in the
root `package.json` for the record); a missing `npx` stops the build with a
message instead of writing unformatted pages and warning.

| Script | Source → Output |
| --- | --- |
| `build_notes_pages.py` | `notes-data/` → 173 pages under `revision-notes/` |
| `build_questions.py` | `questions-data/` → 173 pages under `practice-questions/` |
| `build_past_paper_questions.py` | `past-paper-questions-data/` → `past-paper-questions/` + every `questions.json` |
| `build_glossary.py` | `glossary-data/` → the 3 glossary pages |
| `build_flashcards.py` | `flashcards-data/` → `flashcards/` + `flashcards/data/*.json` |
| `build_past_paper_taxonomy.py` | the Edexcel topic records → `taxonomy.json` |
| `extract_glossary.py` | the notes pages → `glossary-data/terms.json` |
| `build_sitemap.py` | the filesystem → `sitemap.xml` + `sitemaps/*.xml` |

`build_notes_pages.py` also splices a previous/next topic row into each end of
the 166 TOPIC pages - not the hubs. The chain comes from `notes_sequence.py`,
which derives it rather than storing it: directory order from
`boards-data/boards.json` via `board_data.py`, topic order and every label from
each hub's own links. `verify_notes_sequence.py` is what holds those three
sources together.

`bake_templates.py --apply` owns the baked header, footer, script tail and (since
2026-08-23) the `<head>` analytics loader (`sync_gtag()`, from `page_shell.GTAG`)
and the stylesheet block (`sync_fonts()`, from `page_shell.stylesheet_block()` -
the hoist comment, the body-face preload, fontawesome, main.css)
on the 17 hand-written pages; the other 446 take theirs from `page_shell.py`, which all
five page generators import. Since 2026-08-23 `page_shell.py` also owns the
page skeleton (`page()`, `container()`), the shared head values
(`head_values()`, `social()`) and the breadcrumb builders (`breadcrumb_ld()`,
`breadcrumb_html()`); the four generators that used to carry their own copies
pass their family's quirks in as values (the ppq family's `e()` and
`jsonldAsciiEscaped`; the questions family's early preconnect comment went
with the Google Fonts link on 2026-08-23). What
the site is made of - the generator list, the publish rules, `family_of()`,
`pages()` - is `site_layout.py`, imported by generators and verifiers alike;
**a generator never imports a verifier** (`scripts/tests/test_site_layout.py`
asserts it).

`scripts/tests/` is stdlib `unittest`, run first in CI:
`python3 -m unittest discover scripts/tests`. It covers
`build_questions.validate()`, `notes_sequence`, the `page_shell` helpers,
`verify_liquid`'s tokeniser and `site_layout`. Add a test beside any pure
function you change. `page_shell.SCRIPT_TAIL` is the one place the tail
is declared, and `verify_page_shell.py` check 2 restates it independently — so
changing the tail must change two files in the same commit.

`build_sitemap.py` takes each `<lastmod>` from `git log -1 -- <path>`, so **run
it after committing the page edits** (`python3 scripts/build.py --sitemap`),
and commit the sitemap separately. `--check` ends with `SITEMAP OK` (exit 0)
or `SITEMAP STALE` (exit 1). `.githooks/post-commit`, once enabled, does the
rebuild-and-commit automatically.

`verify_text_integrity.py --staged` and `verify_markup_integrity.py --staged
--strict` compare HEAD against the index over the staged files;
`suggest_trailers.py` runs both with `--trailers` and prints the
`Text-Change:`/`Markup-Change:` lines the pending commit needs.
`.githooks/prepare-commit-msg` appends them to the commit template as
comments. CI's invocations are unchanged.

## The verifiers

All of these run in `.github/workflows/verify.yml` on every push, plus
`seo/tools/verify_seo.py`. Run the lot before a push.

```
python3 -m unittest discover scripts/tests      # the unit tests, first
verify_generated  verify_published_surface  verify_liquid  verify_icons
verify_image_dimensions  verify_css_load_order  verify_inline_styles
verify_page_shell  verify_boards  verify_glossary  verify_links  verify_html
verify_notes_sequence
verify_past_paper_tags  verify_diagram_geometry  check_glossary_capitalisation
verify_text_integrity <base>  verify_markup_integrity <base> --strict
build_sitemap.py --check  strip_source_attributions
node test_question_search.js  node test_glossary_filter.js
```

`test_compare_trees.py` (~2m30s) runs in its own workflow,
`compare-trees-suite.yml` - weekly, on demand, and on any change to the
harness - rather than on every push (2026-08-23).

The workflow is **verification only and must never gain a build or deploy step.**
Switching Pages to Actions-based deployment disables `_config.yml`'s `exclude`,
which is the only thing keeping working files off the live site. It also needs
`fetch-depth: 0` (shallow clones break `build_sitemap.py` and the two
`HEAD~1` diffs) and `node` in both jobs.

## Not in CI, and deliberately so

All need a package and all default to a dry run. They are conversions, not
build steps:

```
python3 scripts/reencode_diagrams.py --apply     # Pillow
python3 scripts/build_diagram_webp.py --apply    # Pillow - a lossless .webp twin per diagram PNG (2026-08-23)
python3 scripts/subset_fontawesome.py --apply    # fonttools + brotli
```

`build_diagram_webp.py` is idempotent (it compares pixels, so a re-run is a
no-op) and **must be re-run whenever a diagram PNG is added or changed** -
`verify_image_dimensions.py` (stdlib, in CI) fails if any PNG lacks a
same-size twin, and `build_notes_pages.py` only offers the WebP when the
twin is in the tree.

`scripts/extract_past_paper_questions.swift` and `verify_past_paper_extraction.swift`
use **Swift + PDFKit** — there is no Python PDF library here, but macOS ships
PDFKit. `extract_aqa_questions.py` is the exception and needs `pdfplumber` from
`requirements.txt` in `.venv/`.

## Where a number lives

**If a number is one a script computes, cite the script, not the value.** Counts
in this repo have drifted invisibly before — see `docs/HISTORY.md`. A number that
cannot go stale beats a number that is right today.

**Counts are declared once, in `boards-data/boards.json` (`expectedTopics`),
and derived everywhere else.** `verify_page_shell.py` splits its checks into
INVARIANTS (shape counts, the script tail, the exception sets, the zero
tripwires — pinned literals, and a change to one has to change the file in
the same commit) and CARDINALITIES (how many pages, breadcrumbs, extra
scripts — derived from `boards.json` and the tree). The verifiers that still
pin a literal on purpose each have `--reseed`, which rewrites the literal from
the measured state and prints the diff: `verify_page_shell.py --reseed`,
`verify_boards.py --reseed` (`PINNED`), `bake_templates.py --reseed`
(`EXPECTED`). Adding a topic is `python3 scripts/new_topic.py` — it bumps
`boards.json` and scaffolds the data — then `build.py`; nothing in a verifier
needs editing for it.
