# Prompt: repo cleanup audit — economics-academy

Paste everything below the line into Claude Code in VSCode, with the repo root open.
Run it in **Plan Mode** (Shift+Tab) so nothing gets touched until you've approved the plan.

---

You are auditing this repository (`economics-academy`) — a hand-built static site published to GitHub Pages at economicsacademy.co.uk via Jekyll (`_config.yml` is present). Over ~a year of solo development it has accumulated loose progress files, overlapping content directories, and a 35KB CLAUDE.md that eats a large share of every context window.

Your job has three phases. **Do not modify, move, or delete a single file until I have explicitly approved the plan in Phase 2.** Phase 1 is read-only. Treat the live site as production: any change that alters a published URL is a breaking change and must be flagged as such, not made quietly.

## Phase 1 — Audit (read-only, produce a report)

Build an evidence-based picture of what is actually in use. Work from facts you can verify in the repo, not from filenames or assumptions.

For every top-level file and directory, and every subdirectory more than trivially large, determine:

1. **Is it published?** Check `_config.yml` for `include`/`exclude` lists, Jekyll's default underscore-prefix behaviour, and `.gitignore`. State clearly whether each item is (a) served on the live site, (b) in the repo but excluded from the build, or (c) ignored by git entirely.
2. **Is it referenced?** Grep the HTML, JS, CSS, JSON data files, `sitemap.xml`, `sitemaps/`, and `scripts/` for references to each file and directory. Report the reference count and show the two or three strongest examples. A JSON data file loaded by `fetch()` in a page's JS counts as in use; one that nothing loads does not.
3. **Is it live?** Report last-modified date from `git log -1 --format=%ai -- <path>` and total commits touching it. Flag anything untouched for 6+ months.
4. **Is it duplicated?** I suspect real overlap between `past-paper-questions/`, `past-paper-questions-data/`, `past-papers/`, `practice-questions/`, and `questions-data/`, and possibly between `notes-data/`, `raw-notes/`, and `revision-notes/`. Work out what each one actually contains, which is canonical, whether any are stale copies or generated outputs of another, and whether any are byte-identical duplicates. Do the same for `README.md` vs `README.txt`.
5. **Is it generated?** Identify which directories are outputs of scripts in `scripts/` versus hand-authored source. Generated output that can be rebuilt should be treated differently from source.

Pay particular attention to these, which I already think are suspect — confirm or correct me rather than agreeing:

- Root-level tracking/log markdown: `PROGRESS.md`, `PROJECT-LOG.md`, `PAST-PAPERS-PROGRESS.md`, `QUESTIONS_PROGRESS.md` (159KB), `REVIEW-NOTES.md` (92KB), `NEW-CONTENT-LOG.md`, `extraction-qa-report.md`, `QUESTIONS_GUIDE.md`, `ROADMAP.md`, `OWNER-TODO.md`. Which of these are still consulted, which are historical records worth archiving, and which are dead weight? Check whether CLAUDE.md or any script tells you or me to read or update them — that is what keeps a file alive.
- `.venv/` — confirm whether it is gitignored and whether it is genuinely committed. If it's in the repo history, say so plainly and tell me the size cost.
- `.DS_Store` files throughout — are they gitignored?
- `_working/`, `docs/`, `seo/`, `templates/`, `marking-examples/`, `boards-data/`, `flashcards/` vs `flashcards-data/`.
- Orphaned assets in `images/` and `webfonts/`: list any file with zero references in CSS/HTML/JS. Be careful with fonts — check `@font-face` src paths and any preload tags before calling a font unused.

Output this phase as `_working/audit/REPO-AUDIT.md`, with a table per category and a one-line verdict for every item: **Keep / Archive / Delete / Investigate**. Use *Investigate* honestly — if you cannot establish that something is unused, say so rather than guessing. Every Delete verdict must cite the specific evidence that justifies it.

Also give me a short "surprises" section: anything you found that I probably don't know about — broken references, pages not in the sitemap, orphaned pages nothing links to, data files loaded by pages that no longer exist, scripts referencing paths that have moved.

## Phase 2 — Restructure plan (proposal only, no execution)

Propose a target structure for the repo, then the migration to reach it.

Constraints you must respect:

- **URLs are sacred.** Any published `.html` page or asset that moves changes a live URL. For each such move, state the old and new URL and the redirect required, and prefer *not moving it* unless the benefit is real. Assume Google has these pages indexed. Non-published files (data, scripts, docs, working notes) can move freely.
- **Jekyll's underscore rule**: directories prefixed with `_` are excluded from the build by default. Use this deliberately rather than accidentally.
- **Nothing is deleted destructively.** Anything you propose removing goes to a `_archive/` directory (gitignored or Jekyll-excluded, your recommendation with reasoning) in the first pass, not `rm`. Git history is the safety net for anything I later regret.
- Use `git mv`, never `mv`, so history follows the file.
- **One category per commit**, so each step is independently revertable.

Deliver `_working/audit/RESTRUCTURE-PLAN.md` containing: the proposed tree (before → after), a numbered migration sequence with the exact commands for each step, the specific files whose internal paths need rewriting after each move, a verification step per phase (build the site locally, diff the generated output, check for broken links), and a rollback command per step.

Order the plan by risk: zero-risk cleanups first (gitignore fixes, dead files nothing references), then internal reorganisation, then anything touching published URLs last and only if clearly worth it. Tell me explicitly if you think a proposed move *isn't* worth the risk — I would rather keep an ugly-but-working structure than break indexed pages for tidiness.

Do not execute any of this. Present it and stop.

## Phase 3 — Rewrite CLAUDE.md

The current root `CLAUDE.md` is ~35,000 characters and is loaded into every single session. That is the biggest ongoing cost in this repo. I want a slim root file plus context that loads only when relevant.

Before you write anything, **read the existing CLAUDE.md in full, then interview me.** Ask your questions in batches of no more than five, and make them specific to what you actually found in the file — not generic questions. I'm expecting you to ask about things like:

- Which rules have I actually needed you to follow, versus rules written once defensively and never load-bearing since?
- Which sections are reference material (data schemas, file formats, exam board specifics, content conventions) that only matter when working in one directory — and could therefore live in a nested `CLAUDE.md` in that directory, or in a `docs/` file you read on demand?
- Where does the current file contradict itself, or describe a structure the repo no longer has?
- What has gone wrong in past sessions that the file doesn't currently prevent?
- What in there is background narrative that neither of us needs restated every session?

Flag anything in the current file you believe is stale, duplicated, or unenforceable, and ask before cutting it — don't silently drop rules on the assumption they don't matter.

Then produce a draft at `_working/audit/CLAUDE.md.draft` targeting **under 150 lines**, structured roughly as:

- What this repo is, in three or four lines
- Hard rules — the small set of things that must never happen (deployment safety, URL changes, exam-board accuracy, never inventing specification content)
- Working conventions — commands, build/test/verify steps, commit style
- A pointer index: where to find deeper context, as explicit file paths I can tell you to read, plus which directories carry their own nested `CLAUDE.md`

Everything cut from the root file must be preserved somewhere — either in a nested `CLAUDE.md`, a `docs/` reference file, or `_archive/`. Give me a mapping table of what moved where, and tell me the before/after character count and roughly what that saves per session.

## Working rules for this whole task

- British English throughout.
- Ask me before doing anything destructive or irreversible — that includes `rm`, force pushes, history rewrites, and `.gitignore` changes that would untrack files.
- Where you're uncertain whether something is in use, say "uncertain" and explain what would resolve it. Do not guess and do not pad the report to look thorough.
- Push back if you think part of my premise is wrong — for example if the big markdown files are actually earning their place, or if the directory overlap I suspect turns out to be a sensible separation.
- Start with Phase 1 only. Report back and wait.
