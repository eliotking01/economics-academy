# How publishing works

`main` is served by GitHub Pages with **the default Jekyll build**. There is no
`.nojekyll`, and `_config.yml` exists only to hold an `exclude:` list. Two
consequences that are not obvious.

## `_config.yml` decides what is public

It keeps the repo's working files off the site: `scripts/`, `docs/`, `seo/`, the
seven `*-data/` directories, and the root markdown. Before it existed,
`/REVIEW-NOTES.html`, `/CLAUDE.md` and `/scripts/build_glossary.py` were all live
and crawlable.

**`exclude` REPLACES Jekyll's defaults rather than adding to them**, which is why
the defaults are restated in the file. Anything deleted from that list becomes
public again.

**Adding a nested `CLAUDE.md` to a published directory publishes it.**
`revision-notes/CLAUDE.md` and `css/CLAUDE.md` are listed in `exclude:` for
exactly that reason. `scripts/verify_published_surface.py` is the backstop — it
whitelists file suffixes and `.md` is not among them, so a forgotten one fails
CI rather than shipping.

Two lists must move together: `_config.yml` and `docs/audit/scripts/lib.py`,
which restates the exclude list and calls `verify_matches_config()` on import.
Every script in `docs/audit/scripts/` breaks immediately if they drift.

### Still public by decision

- **`past-paper-questions/`** — `questions.json` is fetched at runtime by
  `js/components/question-search.js`. Must stay.
- **`flashcards/`** — `flashcards/data/*.json` is fetched at runtime by
  `js/components/flashcards.js`. Must stay.
- **`templates/`** — **no longer fetched.** Wave 2 Phase 7 bakes the header and
  footer in at build time and Wave 4.10 deleted the script that fetched them.
  Verified 2026-08-20: zero inbound links, in no sitemap, and in none of the
  eight Search Console exports in `seo/gsc-exports/` — so Google does not have
  either URL and unpublishing would cost nothing. Left published anyway, because
  removing two live URLs is not something to do by habit. To close it out, add
  `- templates/` to `exclude:`.

## Directories beginning with `_` are excluded by Jekyll's own rule

That is what makes `_working/` and `_archive/` safe. **Adding a `.nojekyll` file
would immediately expose every `_` directory** — if that is ever wanted, move
`_working/` and `_archive/` out of the repo first.

## Liquid runs over every markdown file, before Markdown

A stray `{%` opens a tag that never closes and **the whole deploy fails** — not
the page, the deploy. Backticks do not protect it: Liquid runs first and has no
idea what a code span is. This has happened once, on a line quoting the LaTeX
`\text{` followed by an unescaped `%`.

Wrap such text in `{% raw %}` … `{% endraw %}` and run
`python3 scripts/verify_liquid.py`, which reproduces Liquid 4.0.4's behaviour and
was cross-checked against it.

The site's own HTML is safe — it has no front matter, so Jekyll copies it
verbatim without rendering.

## A published URL is permanent

GitHub Pages cannot issue a 301. There is no `_redirects`, `netlify.toml`,
`vercel.json` or `.htaccess` here, and the default Jekyll build offers nothing
equivalent. A meta-refresh or JS redirect is the only option, both pass authority
unreliably, and the stub pages then have to stay in the repo permanently.
Evaluated for the glossary on 2026-08-07 and rejected on exactly that basis.

**So decide a new feature's URL once, before it ships.** A feature nests under
the section it belongs to; only a standalone tool sits at root. The glossary is
`/revision-notes/glossary/` because it is a glossary of the notes' own terms.
`/flashcards/` and `/practice-questions/` are at root because they stand alone.

Nesting has one incidental benefit: the nav highlight is chosen by path prefix,
so a page under `/revision-notes/` needs no new rule. The rule list is `PAGE_MAP`
in `scripts/page_shell.py`.

## CI

`.github/workflows/verify.yml` runs the whole suite on every push and PR. It is
**verification only and must never gain a build or deploy step** — switching
Pages to Actions-based deployment disables `_config.yml`'s `exclude`, which is
the only thing keeping working files off the live site. Approved on exactly that
basis.

Two things it needs that are easy to break:

- **`fetch-depth: 0`.** `build_sitemap.py` reads every `<lastmod>` from
  `git log -1 -- <path>`, which a shallow clone cannot answer, and two checks
  diff against `HEAD~1`. A shallow clone fails the workflow, not the site.
- **Both jobs need `node`**, for Prettier and the glossary's KaTeX pre-render.

CI verifies; it does not gate the deploy. Pages publishes whatever is on `main`.
