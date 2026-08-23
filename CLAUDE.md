# Economics Academy

Hand-written static site at **economicsacademy.co.uk**: free A-Level Economics
revision notes, past papers, flashcards and practice questions, plus paid
tutoring and marking. Solo project, no team, no framework, no build step.

**`main` auto-publishes** via GitHub Pages' default Jekyll build. What is public
is decided by `_config.yml`'s `exclude:` list and Jekyll's underscore rule —
nothing else. For any count of pages, terms or files, run the script that
computes it rather than trusting a number written down.

## Hard rules

1. **Confirm before pushing to `main`.** Pushing is publishing. Committing is
   not — commit freely, ask before the push.
2. **Never change economics wording without an explicit instruction, every
   time.** Formatting, markup and structure are fine. Wording is not. If a
   sentence is wrong, log it in `docs/REVIEW-NOTES.md` instead of fixing it.
3. **Never invent specification content.** Paper structure, command words and
   mark allocations come from the exam board's own PDFs. Those are not in this
   repo — ask rather than working from memory. Never assume a board.
4. **Practice questions must be 100% original.** They are sold. The past-paper
   bank reproduces real questions verbatim and is a separate thing; the two
   never share a data path. Never copy or paraphrase a real exam question into
   `questions-data/`.
5. **Never hand-edit a generated file.** Eight generators own 446 of the 463
   published pages plus every sitemap. Edit the source and re-run.
   `python3 scripts/verify_generated.py` names them and proves the tree matches.
   The 17 hand-written pages are listed by `python3 scripts/bake_templates.py`.
6. **Never bulk-rewrite prose with a script.** Scripted paragraph rebuilds have
   silently destroyed `<a>` tags here. Edit prose by hand.
7. **A published URL is permanent.** GitHub Pages cannot issue a 301 — there is
   no redirect mechanism of any kind. Moving or deleting a published file breaks
   an indexed URL forever. Flag it as a breaking change; never do it quietly.
8. **Never commit secrets.** Nothing here is secret today; keep it that way.
9. **Ask before anything irreversible** — deleting, overwriting, sending,
   publishing. Notion holds student records: update and archive, never delete.

## How to work here

You have latitude. New features, redesigns, accessibility and performance work
are wanted, not merely tolerated. The rules above are about not destroying
what exists, not about keeping you cautious.

- **Propose freely, apply carefully.** Design, prototype and recommend without
  asking. Get approval before it reaches a published page.
- **Significant decisions come as options with a recommendation**, not a survey.
- **Reuse before inventing.** The `.resource-*` blocks at the end of
  `css/main.css` and the component library in `revision-notes/CLAUDE.md` already
  cover most of what a new page needs.
- **The site has no runtime dependencies and no build step.** Everything
  ships as static HTML, CSS and hand-written JS; GitHub Pages serves `main`
  as-is. If a feature genuinely needs a dependency, say why first. **The
  tooling is a different matter:** the generators in `scripts/` are Python 3
  standard library only, plus Node for the two things Python cannot do —
  KaTeX pre-rendering and Prettier (`npx --yes prettier@<version>`, pinned in
  `scripts/prettier_util.py` and recorded in `package.json`; no `npm install`).
  Without Node the build stops loudly rather than writing unformatted pages.
- **Progressive enhancement.** Every page must work with JavaScript off. JS
  enhances; it never delivers content.
- **Verify twice: run the suite, then open the page.** Green checks do not prove
  a layout is right. Live Server in VSCode is the second half.
- **Say when you are unsure.** A stated uncertainty is worth more than a
  confident guess, especially about economics.

## Commands

```bash
python3 scripts/verify_generated.py         # 8 generators vs the committed tree
python3 scripts/build_sitemap.py --check    # ends SITEMAP OK (exit 0) or SITEMAP STALE (exit 1)
```

A stale sitemap is fixed by `python3 scripts/build.py --sitemap` AFTER the
content commit. With `.githooks/` enabled (`git config core.hooksPath
.githooks`, once) the post-commit hook does that for you.

Run the whole suite before any push — every check in `.github/workflows/verify.yml`
runs locally and all are stdlib-only. `scripts/CLAUDE.md` maps them.

**Rebuilding is one command.** After editing `templates/header.html` or
`templates/footer.html` (baked into all 463 pages), any `*-data/` source, or a
generator:

```bash
python3 scripts/build.py              # every generator in order, bake the 17, verify the shell
# commit the page changes, then:
python3 scripts/build.py --sitemap    # AFTER committing: lastmod comes from git
```

The generator list lives in `scripts/site_layout.py` and nowhere else;
`build.py` runs it and `verify_generated.py` proves it. Do not write the
sequence out by hand anywhere.

**Prettier** is `npx prettier@<version>`, not installed; the version and the
one call site are `scripts/prettier_util.py`, the settings are `.prettierrc`
(its defaults, written down) and **`.prettierignore` lists what it must never
touch** — the 17 hand-written pages (it rewraps their baked header, which
check 9 then rejects; `revision-notes/index.html` is also GSC-frozen) and the
generated notes pages. That file is generated by `bake_templates.py
--prettierignore`; regenerate it, never edit it. If you format anything by
hand, run `bake_templates.py --apply` afterwards.

**Commit style.** Imperative subject, body explaining *why*. Two trailers are
enforced by CI, one line per file:

```
Text-Change: <path>      # visible wording changed on a published page
Markup-Change: <path>    # markup deliberately removed from a published page
```

`python3 scripts/suggest_trailers.py` prints the exact lines a pending commit
needs (it runs both checks over the staged files). Merge with a merge commit,
never a squash, so CI sees trailers across the range.

**Git hooks** live in `.githooks/` and are opt-in — enable once per clone
with `git config core.hooksPath .githooks`. `prepare-commit-msg` appends the
suggested trailers to the commit template as comments; `post-commit` rebuilds
and commits the sitemap when a commit has made it stale. Neither can fail a
commit.

## Where to look

**Start with `PROGRESS.md`** — the single record of every project on this site
and the one consolidated list of what is still open. This file deliberately does
not track projects: they finish, and a description of live work embedded in a
rules file goes stale without anything noticing. That is how three features came
to be documented here as "in progress" on branches that no longer existed.

| Need | Read |
| --- | --- |
| A plain-English tour of every file and folder | `docs/REPO-MAP.md` |
| What has been built, what is still open | `PROGRESS.md` |
| Things only Eliot can do; ideas and someday | `OWNER-TODO.md` |
| Known content problems, logged not fixed | `docs/REVIEW-NOTES.md`, `docs/CONTENT_ISSUES.md` |
| What must not be broken, and why | `docs/audit/DO-NOT-BREAK.md` |
| Ratified decisions, append-only | `docs/audit/DECISIONS.md` |
| How publishing works; the Liquid deploy trap | `docs/DEPLOYMENT.md` |
| How a page is assembled; boards, generators | `docs/ARCHITECTURE.md` |
| Why a rule exists, when the reason is a story | `docs/HISTORY.md` |
| Authoring standard for practice questions | `docs/QUESTIONS_GUIDE.md` |
| The locked SVG diagram style guide | `docs/DIAGRAM_STYLE.md` |

**These directories carry their own `CLAUDE.md`**, loaded when you work in them,
so their detail is not in this file:

| Directory | Covers |
| --- | --- |
| `revision-notes/` | Topic pages, the component library, prose conventions |
| `notes-data/` | The byte slices the notes pages are built from |
| `css/` | One stylesheet per page, wrapper scoping, no inline styles |
| `scripts/` | Every generator and verifier, and which are not in CI |
| `questions-data/` | The original practice questions (feeds `/practice-questions/`) |
| `past-paper-questions-data/` | The real-exam bank, and its permanent scope limits |
| `glossary-data/` | The verbatim rule and its two declared exceptions |
| `flashcards-data/` | Card authoring, board fidelity, the freemium constraint |

## Vocabulary

- **Boards**: Edexcel (A), Edexcel B, AQA, OCR. Notes cover Edexcel and AQA
  only; past papers cover all four.
- **Theme 1–4** = Edexcel, real spec codes. **AQA micro/macro** use site-local
  codes `1.x.y`/`2.x.y`, deliberately not the real 7136 codes — ratified, do
  not "fix" them.
- **Twin** = the page covering the same content on the other board.
- Third-party: Formspree, Calendly, Stripe payment links, Kit, GA4. All IDs are
  public by design.
