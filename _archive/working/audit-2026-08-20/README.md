# Repo audit and restructure — 2026-08-20

A one-day pass over the whole repository: audit, restructure, and a rewrite of
`CLAUDE.md`. All of it shipped the same day.

| File | What it is |
| --- | --- |
| `00-the-brief.md` | What Eliot asked for |
| `REPO-AUDIT.md` | Phase 1. Read-only findings: every file and folder classified published / in-repo / ignored, with a verdict and the evidence for it. The "surprises" section is the useful part |
| `RESTRUCTURE-PLAN.md` | Phase 2. The plan, plus an execution record at the end |
| `CLAUDE-MIGRATION.md` | Phase 3. Where every section of the old 599-line `CLAUDE.md` went, and the Claude Code setup recommendations |

**These are dated records. Paths inside them are deliberately NOT rewritten when
files move later** — the same rule as `docs/audit/findings/`. They describe the
tree as it stood on 2026-08-20.

## What it changed

- Fixed a generated page that had been hand-edited, whose 143 deleted words the
  next build would have restored. Four CI checks were red because of it.
- Compressed the marking-example PDF, 8.6 MB → 1.77 MB, no visible loss.
- Root markdown 12 files → 4. `_archive/` created; `raw-notes/` retired.
- `PROGRESS.md` absorbed `PROJECT-LOG.md` and became the entry point;
  `OWNER-TODO.md` absorbed `ROADMAP.md`.
- `CLAUDE.md` 35,251 → 7,620 characters, plus eight nested `CLAUDE.md` files and
  three new `docs/` references.
- Added a `PreToolUse` hook that blocks edits to generated files — the failure
  above, made mechanically impossible.
- Stopped publishing `templates/` and `LICENSE.txt`.

**The published surface was 1,099 files before and 1,096 after**, the difference
being those three deliberately removed URLs. Nothing else moved.

## Left open

The OCR A Level Paper 3 June 2023 **question paper is missing** — both PDFs at
that path are the mark scheme, byte-identical. Recorded in `PROGRESS.md` under
"What remains flagged".
