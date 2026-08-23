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
  stat strip, card grid, cross strip, services panel and (since 2026-08-23)
  the `.resource-index-*` topic index used by the notes and practice board
  hubs. Don't fork it.
- Watch `#main .row > div[class*="col-"]` (specificity 1,2,1) — a bare class
  selector loses to it. (Still live: the 2026-08-23 performance pass removed
  the dead `ul.social` brand-icon block, `.footer-dark` and 27 dead `-moz-`/
  `-ms-` prefixes — proved cascade-neutral across 16 pages with
  `computed_style_diff.py` — but left the `.row`/`.col-*` grid; OWNER-TODO
  has the plan.) The contact form's honeypot rendered visibly until its
  selector was raised. Check computed style in a real render for anything that
  must be hidden.

**The web fonts are self-hosted under `/webfonts/`** (since 2026-08-23): the
static latin woff2 files Google Fonts itself serves, byte-for-byte for Source
Sans Pro, metric-identical instances for Merriweather, licences alongside.
Source Sans Pro (6 cuts: 300, 300 italic, 400, 600, 700, 900) is `@font-face`
in `main.css`; Merriweather (3) only in `revision-notes-textbook.css` and
`quiz.css`, so it downloads only where a stack names it. **Open Sans is gone**
(Eliot's call, 2026-08-23): the breadcrumb, consent bar, hub index counts and
codes and the CTA straps now use Source Sans Pro at the same weights — do not
reintroduce a third family. The two `… Fallback`
`size-adjust` faces in `main.css` still match — same files, same metrics. No
page may link `fonts.googleapis.com` or `fonts.gstatic.com`
(`verify_css_load_order.py` holds it at 0/463) and every head preloads the
body face, `page_shell.BODY_FONT`. Do not swap Source Sans Pro for Source
Sans 3: it is a visual change and needs approval. Adding a weight means
adding the file and the `@font-face`, not a Google link.

**`fontawesome-all.min.css` is generated and is a SUBSET**, despite the name.
Adding an icon means adding its rule here *and* re-running
`python3 scripts/subset_fontawesome.py --apply` (needs fonttools + brotli, not in
CI). `verify_icons.py` fails if you forget — a subset font renders a missing
glyph as nothing at all, silently.

`main.css` currently fails `prettier --check` at a `box-shadow` list. Pre-existing.
