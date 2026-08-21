# scripts/

Excluded from publishing. **Python standard library only** — everything CI runs
must stay that way.

## The eight generators

Each owns its output. Never hand-edit what a generator writes; edit the source
and re-run. `verify_generated.py` re-runs all eight in a throwaway worktree and
diffs against the committed tree, so drift cannot ship.

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

`bake_templates.py --apply` owns the baked header, footer and script tail on the
17 hand-written pages; the other 446 take theirs from `page_shell.py`, which all
five page generators import. `page_shell.SCRIPT_TAIL` is the one place the tail
is declared, and `verify_page_shell.py` check 2 restates it independently — so
changing the tail must change two files in the same commit.

`build_sitemap.py` takes each `<lastmod>` from `git log -1 -- <path>`, so **run
it after committing the page edits**, and commit the sitemap separately.
`--check` prints "nothing written" on both paths: the pass signal is exit 0 with
no `WOULD CHANGE` lines.

## The verifiers

All of these run in `.github/workflows/verify.yml` on every push, plus
`seo/tools/verify_seo.py`. Run the lot before a push.

```
verify_generated  verify_published_surface  verify_liquid  verify_icons
verify_image_dimensions  verify_css_load_order  verify_inline_styles
verify_page_shell  verify_boards  verify_glossary  verify_links  verify_html
verify_notes_sequence
verify_past_paper_tags  verify_diagram_geometry  check_glossary_capitalisation
verify_text_integrity <base>  verify_markup_integrity <base> --strict
build_sitemap.py --check  strip_source_attributions  test_compare_trees
node test_question_search.js  node test_glossary_filter.js
```

The workflow is **verification only and must never gain a build or deploy step.**
Switching Pages to Actions-based deployment disables `_config.yml`'s `exclude`,
which is the only thing keeping working files off the live site. It also needs
`fetch-depth: 0` (shallow clones break `build_sitemap.py` and the two
`HEAD~1` diffs) and `node` in both jobs.

## Not in CI, and deliberately so

Both need a package and both default to a dry run. They are one-off conversions,
not build steps:

```
python3 scripts/reencode_diagrams.py --apply     # Pillow
python3 scripts/subset_fontawesome.py --apply    # fonttools + brotli
```

`scripts/extract_past_paper_questions.swift` and `verify_past_paper_extraction.swift`
use **Swift + PDFKit** — there is no Python PDF library here, but macOS ships
PDFKit. `extract_aqa_questions.py` is the exception and needs `pdfplumber` from
`requirements.txt` in `.venv/`.

## Where a number lives

**If a number is one a script computes, cite the script, not the value.** Counts
in this repo have drifted invisibly before — see `docs/HISTORY.md`. A number that
cannot go stale beats a number that is right today.
