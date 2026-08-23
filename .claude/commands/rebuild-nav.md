---
description: Rebuild every page after editing templates/header.html or footer.html
---

The header and footer are baked into all 463 pages at build time. Editing
`templates/header.html` or `templates/footer.html` changes nothing on its own —
it is a rebuild, not a one-file edit.

```bash
# 1. every generator in order (scripts/site_layout.GENERATORS), then
#    bake_templates.py --apply for the 17 hand-written pages, then
#    verify_page_shell.py (check 9 is the one that matters). One command:
python3 scripts/build.py
```

**Then commit the page changes.**

```bash
# 2. ONLY AFTER COMMITTING - build_sitemap takes every <lastmod> from
#    `git log -1 -- <path>`, so running it before the commit bakes in stale
#    dates and needs a second commit to fix. This has happened.
python3 scripts/build.py --sitemap
```

Commit the sitemap separately. (If `.githooks/` is enabled, the post-commit
hook does step 2 for you.)

Notes:

- Do not write the generator sequence out by hand — it is `scripts/site_layout.py`
  and `build.py` runs it. The hand-copied lists this file used to carry were
  one of four that disagreed with each other.
- **If you ran Prettier at any point, re-run `bake_templates.py --apply` after
  it.** Prettier reformats the baked header inside root pages, and `.prettierignore`
  lists what must never be formatted.
- `verify_page_shell.py` check 9 lifts the block back out of every page and
  requires it to equal the template byte for byte. A nav edit that reaches 462
  pages fails there rather than shipping.
- Finish with `/verify`.
