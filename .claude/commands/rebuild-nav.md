---
description: Rebuild every page after editing templates/header.html or footer.html
---

The header and footer are baked into all 463 pages at build time. Editing
`templates/header.html` or `templates/footer.html` changes nothing on its own —
it is a rebuild, not a one-file edit.

Run in this order:

```bash
# 1. the 446 generated pages
python3 scripts/build_notes_pages.py \
  && python3 scripts/build_past_paper_questions.py \
  && python3 scripts/build_questions.py \
  && python3 scripts/build_glossary.py \
  && python3 scripts/build_flashcards.py

# 2. the other 17, hand-written. Dry run first, without --apply.
python3 scripts/bake_templates.py
python3 scripts/bake_templates.py --apply

# 3. check it reached every page BEFORE committing
python3 scripts/verify_page_shell.py     # check 9 is the one that matters
```

**Then commit the page changes.**

```bash
# 4. ONLY AFTER COMMITTING - build_sitemap takes every <lastmod> from
#    `git log -1 -- <path>`, so running it before the commit bakes in stale
#    dates and needs a second commit to fix. This has happened.
python3 scripts/build_sitemap.py
```

Commit the sitemap separately.

Notes:

- **If you ran Prettier at any point, re-run `bake_templates.py --apply` after
  it.** Prettier reformats the baked header inside root pages.
- **Never run Prettier over `revision-notes/index.html`** without re-splicing its
  frozen head back to `main`'s exact bytes.
- `verify_page_shell.py` check 9 lifts the block back out of every page and
  requires it to equal the template byte for byte. A nav edit that reaches 462
  pages fails there rather than shipping.
- Finish with `/verify`.
