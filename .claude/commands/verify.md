---
description: Run the full verification suite, exactly as CI does
---

Run every check `.github/workflows/verify.yml` runs, in this order, and report a
one-line PASS/FAIL per check. Do not stop at the first failure — run them all,
then summarise.

```bash
python3 scripts/verify_html.py
python3 scripts/verify_links.py
python3 scripts/verify_glossary.py
python3 scripts/verify_past_paper_tags.py
python3 scripts/verify_diagram_geometry.py
python3 scripts/verify_icons.py
python3 scripts/verify_image_dimensions.py
python3 scripts/verify_css_load_order.py
python3 scripts/verify_inline_styles.py
python3 scripts/verify_page_shell.py
python3 scripts/verify_boards.py
python3 seo/tools/verify_seo.py
python3 scripts/verify_liquid.py
python3 scripts/verify_published_surface.py
python3 scripts/strip_source_attributions.py
python3 scripts/build_sitemap.py --check
python3 scripts/check_glossary_capitalisation.py --check
node scripts/test_question_search.js
node scripts/test_glossary_filter.js
python3 scripts/verify_text_integrity.py HEAD~1
python3 scripts/verify_markup_integrity.py HEAD~1 --strict
python3 scripts/verify_generated.py
python3 scripts/test_compare_trees.py
python3 -c "import sys;sys.path.insert(0,'docs/audit/scripts');import lib"
```

Two traps when reading the output:

- **`build_sitemap.py --check` prints "nothing written" whether it passes or
  fails.** The pass signal is **exit 0 with no `WOULD CHANGE` lines**. Misreading
  it once already shipped a stale sitemap.
- **`verify_generated.py` checks HEAD, not the working tree.** If there are
  uncommitted changes it says so and still reports on the last commit. Commit
  first if you want it to mean anything.

If `verify_markup_integrity` reports a loss you made on purpose, the commit needs
a `Markup-Change: <path>` trailer — one line per file. Same for
`Text-Change: <path>` when visible wording changed on a published page.
