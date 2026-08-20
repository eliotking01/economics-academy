# Why some rules exist

Rules whose reason is a story. None of this needs to be in context every
session; it is here so that when a rule looks arbitrary, the reason is findable
rather than lost.

## Written-down numbers go stale, and the drift is invisible

**Cite the script that computes a number, not the number.**

The old root `CLAUDE.md` said the `<head>` was generated for **454** pages. That
figure appeared there and in three other documents until 2026-08-11. It was
`463 − 9` — an arithmetic guess, not a measurement — and no generator wrote the
missing 8. The real split is what `scripts/verify_page_shell.py` prints on its
first line.

The same file said the glossary's `rewrite` block covered **46** definitions
while `verify_glossary.py` check 7 printed a different figure on every run for
weeks, and nothing compared the two. **That check printed `44/44` when PH10-061
was written and prints `43/43` today** — the number written down to illustrate a
stale number had itself gone stale, in two documents.

It also said `images/diagrams/` held **112** PNGs and `svg/` held **83**. On
2026-08-20 they were 106 and 84.

And it said `docs/audit/DECISIONS.md` was append-only **D1–D39**. It was D1–D50.

A number that cannot go stale beats a number that is right today. PH10-061.

## The file described work that had finished

Until 2026-08-20 the root `CLAUDE.md` carried three sections opening "In progress
on `feature/question-bank`", "In progress on `feature/glossary`" and "In progress
on `flashcards-feature`". All three branches had been merged and deleted and all
three features were live.

Nothing was wrong with the sections when they were written. The problem is
structural: a description of live work embedded in a rules file has no natural
death, because nobody deletes it when the project lands. **That is why the root
file no longer tracks projects at all** — `PROGRESS.md` does, and `PROGRESS.md`
is dated and maintained.

## `_config.yml` described a script that had been deleted

Its comment block claimed `templates/` was "fetched at runtime by
inject-templates.js". That script was replaced by `js/components/nav.js` at Wave
4.10 and nothing has been fetched at page load since Wave 2 Phase 7. The block
also listed `logo/` and `old-logos-archive/`, neither of which exists, one of
them with nine lines agonising over whether to keep publishing it.

The `exclude:` list itself was correct throughout. Only the explanation had
rotted — in the one file that decides what is public. Corrected 2026-08-20.

## The script tail has changed length three times

`page_shell.SCRIPT_TAIL` is two scripts today. It was four until 2026-08-12 and
seven until 2026-08-11. Any document that writes the list out goes stale without
anything noticing, which is why the rule is to cite the constant.

## `convert_raw_notes.py` was deleted, and should not come back

Deleted 2026-08-13, D44. It wrote a whole page into a path
`build_notes_pages.py` now generates, and its 73 markdown sources in
`raw-notes/` measured **0 of 73** still in sync with their live pages. Re-measured
2026-08-20 before archiving them: still 0 of 73, median word overlap 0.63, worst
0.40. Those files are historical drafts at `_archive/raw-notes/` and are not a
build input.

Do not restore the script to "fix" its `<head>`; the `<head>` was never the
problem, and `page_shell.py` owns it now anyway.

## A source file was served live for eleven phases

`revision-notes/macro-application/macro-application-uk-sa.md` — 429 lines of
source markdown — was tracked, not excluded, and served at its own URL through
the entire eleven-phase audit. It survived because **every enumeration tool in
this repo globs `*.html`**, so `is_published()` returned True and
`published_html()` returned False for the same file, and every count was right
while none of them included it.

`scripts/verify_published_surface.py` closes the class rather than the instance:
it enumerates all tracked files, not just HTML, and whitelists suffixes. The
sharper risk it guards is a deploy failure, not a stray URL — see the Liquid
trap in `DEPLOYMENT.md`. PH10-060.

## A generated page was hand-edited, and the edit was queued to vanish

On 2026-08-20, commit `63437c6` edited
`revision-notes/aqa-a2-micro/1-8-4-…externalities…html` directly to remove a
duplicated block, and did not update the slice in `notes-data/`. The page was
correct and the site looked fine. The next `build_notes_pages.py` run — which any
nav edit requires — would have restored 143 deleted words.

Four CI checks went red and named it, but each read like a stale-build warning
rather than "your content edit is about to be undone". Fixed in `6cc2d65` by
putting the deletion into the slice and regenerating.

**This is the failure mode that a rule in a document does not prevent.** If a
`PreToolUse` hook is ever added to this repo, blocking writes to generated paths
is the thing it should do.

## Extracting an inline style is not a rename

An inline `style` attribute outranks every class selector, so the class you
extract it into can lose to a rule the attribute was beating. Two of the last 35
did exactly that — a `(0,1,1)` `section > :last-child` reset and a `(1,2,1)`
`#main .row > div[class*="col-"]` — and **every harness assertion passed both.**

Prove it with
`python3 docs/audit/scripts/harness/computed_style_diff.py OLD NEW`, which
compares every computed property on every element in a real browser.

## Prettier reformats the baked header

Always run `python3 scripts/bake_templates.py --apply` **after** Prettier. And
never run Prettier over `revision-notes/index.html` at all without re-splicing
its frozen head back to `main`'s exact bytes.

## GSC-frozen heads

These pages' `<title>`, H1, meta description and canonical must not change —
they are what current rankings are measured against: `/revision-notes/`, the four
past-papers board pages, `marking.html`, and the titles of `index.html` and
`tutoring.html`. `marking.html` ranks #1 for "Economics paper marking".

`about`/`contact`/`faq` heads are tunable, but their `og:description` must stay a
shortened variant (`KNOWN_SELF_DISAGREEMENT` in `verify_page_shell.py`) or leave
that list in the same commit.
