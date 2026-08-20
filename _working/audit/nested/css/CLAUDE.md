# css/

`main.css` is site-wide. **One stylesheet per page in `css/pages/`, named after
the page.** Three pages load two: `macro-application` and the two diagram
galleries, which share `revision-notes-diagrams.css`.
`scripts/verify_css_load_order.py` names them, and a fourth fails there.

- **Scope everything.** Put a wrapper class on the page's `<main id="main">` and
  nest every rule under it — `.revision-notes-content .notes-cta { … }`. Bare
  class names have already collided across two files. `css/pages/macro-application.css`
  is the exemplar.
- **`main.css` must be linked before every page stylesheet.** Enforced.
- **No inline `style` attributes.** 0 authored ones remain and
  `verify_inline_styles.py` holds it there. The ~1,187 in a grep are KaTeX build
  output on 7 pages and must never be touched.
  **Extracting an inline style is not a rename:** an inline style outranks every
  class selector, so the class can lose to a rule the attribute was beating. Two
  real cases here were a `(0,1,1)` `section > :last-child` reset and a `(1,2,1)`
  `#main .row > div[class*="col-"]`, and every harness assertion passed both.
  Prove it with `python3 docs/audit/scripts/harness/computed_style_diff.py OLD NEW`.
- **`:root` colour tokens live in `revision-notes-textbook.css` and are for the
  notes only.** Elsewhere use hex. The brand accent is `#d52349`.
- **Reuse the `.resource-*` block at the END of `main.css`** — the shared hero,
  stat strip, card grid, cross strip and services panel used by all four
  resource sections. Don't fork it.
- Watch `#main .row > div[class*="col-"]` (specificity 1,2,1) — a bare class
  selector loses to it. The contact form's honeypot rendered visibly until its
  selector was raised. Check computed style in a real render for anything that
  must be hidden.

**`fontawesome-all.min.css` is generated and is a SUBSET**, despite the name.
Adding an icon means adding its rule here *and* re-running
`python3 scripts/subset_fontawesome.py --apply` (needs fonttools + brotli, not in
CI). `verify_icons.py` fails if you forget — a subset font renders a missing
glyph as nothing at all, silently.

`main.css` currently fails `prettier --check` at a `box-shadow` list. Pre-existing.
