# CLAUDE.md rewrite — what moved where, and what else the repo should have

Phase 3. Drafts only; nothing is in place. 2026-08-20.

---

## 1. The size

| | chars | lines |
| --- | ---: | ---: |
| Current root `CLAUDE.md` | **35,251** | 599 |
| Proposed root `CLAUDE.md` | **7,620** | 144 |
| **Saved, every session** | **27,631** | 455 |

That is **78% smaller, roughly 6,900 tokens back per session** — before any
tool call, on every single conversation, forever. The material is not lost: it
is 20,570 characters of nested `CLAUDE.md` that loads only when you work in that
directory, and 3 new `docs/` files that load only when asked for.

**Worst case is now better than the old best case.** Editing a topic page loads
root (7,620) + `revision-notes/` (2,900) ≈ 10,500 chars, still 70% below today's
unconditional 35,251. A conversation that touches no subdirectory pays 7,620.

---

## 2. Should the root file reference individual projects at all?

**No. It should not name a single project, and the draft does not.**

You asked me to analyse this rather than assume. The case:

1. **Projects finish; a rules file has no mechanism for noticing.** All three
   project sections in the current file open "In progress on `feature/…`". All
   three branches were merged and deleted; all three features are live. Nothing
   was wrong when they were written — the failure is structural. A description of
   live work embedded in a rules file has no natural death, because nobody
   deletes it at the moment the project lands.
2. **It is the wrong axis.** A rules file should hold **invariants** — things
   true regardless of what is being worked on. Project state is state, and state
   belongs in a dated, maintained file. That file now exists and is `PROGRESS.md`.
3. **The detail was never really project detail.** What the three sections
   actually contained was *data-model* rules — the `premium` flag contract, the
   `curation.json`/`authored.json` split, 8EC0 having no Section C. Those are
   properties of a directory, not of a project, which is why they belong in that
   directory's own `CLAUDE.md` and read better there.
4. **You lose nothing.** The root file's pointer table sends you to
   `PROGRESS.md` in one line, and `PROGRESS.md` now covers all nine projects.

So: one line, and it is a pointer, not a description.

---

## 3. Mapping — every section of the old file

| Old section | Lines | Goes to | Why |
| --- | ---: | --- | --- |
| Title + intro | 1–5 | **root** (rewritten) | Kept, tightened to 4 lines |
| Hard constraints | 6–16 | **root** Hard rules | Kept, expanded to cover exam-board accuracy and URL permanence, which were not in it |
| Tooling — the verifier list | 17–90 | **`scripts/CLAUDE.md`** | Only matters when running or writing tooling |
| Tooling — the nav rebuild chain | 91–110 | **root** Commands | The one multi-step command you must not get wrong |
| Tooling — `page_shell`, 446/17, boards.json | 111–156 | **`docs/ARCHITECTURE.md`** | Reference, consulted not memorised |
| Tooling — "cite the script, not the value" | ~150 | **`scripts/CLAUDE.md`** + **`docs/HISTORY.md`** | Rule in the first, the story behind it in the second |
| How publishing works | 157–189 | **`docs/DEPLOYMENT.md`** | Read when touching `_config.yml` or shipping a URL |
| Layout | 190–216 | **`docs/ARCHITECTURE.md`** | A map; you look it up |
| Where a new feature's URL goes | 217–236 | **`docs/DEPLOYMENT.md`** | Belongs with the no-301 constraint it derives from |
| How a page is assembled | 237–254 | **`docs/ARCHITECTURE.md`** | Reference |
| Conventions — HTML | 255–270 | **`revision-notes/CLAUDE.md`** | Only applies where you write page markup |
| Conventions — CSS | 271–288 | **`css/CLAUDE.md`** | Only applies in `css/` |
| Conventions — Prose | 289–293 | **`revision-notes/CLAUDE.md`** | Same |
| Component library | 294–318 | **`revision-notes/CLAUDE.md`** | The table is unusable anywhere else |
| Exemplars | 319–327 | **`revision-notes/CLAUDE.md`** | All four are notes pages or their CSS |
| Vocabulary | 328–341 | **root** (condensed 14 → 8 lines) | Board names must be right from the first sentence of a session |
| Past paper question bank | 342–421 | **`past-paper-questions-data/CLAUDE.md`** | Scope limits, the 8EC0 structure, the sparse-`papers` trap |
| Glossary & formulae | 422–510 | **`glossary-data/CLAUDE.md`** | The verbatim rule and its two exceptions |
| Flashcards | 511–562 | **`flashcards-data/CLAUDE.md`** | Card authoring, board fidelity, the freemium constraint |
| Flashcards — standing rules 1, 6 | 545–562 | **root** How to work here | They were never flashcard-specific: "never edit existing content without approval", "options with a recommendation" |
| See also | 563–599 | **root** Where to look | Rebuilt as a two-column table; every path re-checked against the tree |

**Nothing is dropped.** Three things are *deliberately not carried forward* and
each is called out below rather than deleted silently.

### Deliberately not carried forward — check these

1. **"the 112 PNGs" / "83 SVGs" / "D1–D39" / "454 pages".** Four stale counts.
   Replaced by the script that computes each. The *fact that they went stale* is
   preserved in `docs/HISTORY.md`, because it is the strongest argument for the
   rule.
2. **The three "In progress on `feature/…`" framings.** The branches do not
   exist. The technical content survives in the nested files; only the framing
   is gone.
3. **`_config.yml`'s and CLAUDE.md's description of `inject-templates.js`.**
   The script was deleted at Wave 4.10. Already corrected in `7e9c0a5`; the
   history is in `docs/HISTORY.md`.

### Added, that was not there before

- **"How to work here"** — 12 lines granting latitude. You said most of your
  coding now happens through Claude Code and you want creative, high-quality
  feature work. The old file is 599 lines of prohibition with no statement that
  building things is wanted, which reliably produces a cautious assistant that
  asks permission for everything. This section is the counterweight.
- **Exam-board accuracy and "never invent specification content"** as a *hard
  rule*. It was in the parent folder's `CLAUDE.md`, not this one.
- **URL permanence as a hard rule.** It was buried at line 217 under a heading
  about where new features go.
- **Commit trailer syntax.** It was in `PROGRESS.md`'s traps list only.

---

## 4. Files to create

### Nested `CLAUDE.md` — 8 files, 20,570 chars, all load-on-demand

| Path | Lines | Loads when |
| --- | ---: | --- |
| `revision-notes/CLAUDE.md` | 61 | Touching any notes page |
| `notes-data/CLAUDE.md` | 25 | Editing a slice |
| `css/CLAUDE.md` | 37 | Touching any stylesheet |
| `scripts/CLAUDE.md` | 74 | Running or writing tooling |
| `questions-data/CLAUDE.md` | 28 | Writing practice questions |
| `past-paper-questions-data/CLAUDE.md` | 53 | Working on the real-exam bank |
| `glossary-data/CLAUDE.md` | 66 | Working on the glossary |
| `flashcards-data/CLAUDE.md` | 47 | Writing cards |

**Two of these need a `_config.yml` line in the same commit.**
`revision-notes/` and `css/` are **published directories** — a `CLAUDE.md`
dropped in either is served at `/revision-notes/CLAUDE.md` and
`/css/CLAUDE.md`. The other six sit in directories already excluded wholesale.

`scripts/verify_published_surface.py` is the backstop: `.md` is not in its
suffix whitelist, so a forgotten entry fails CI rather than shipping. But CI
verifies, it does not gate the deploy — so get it right in the commit.

### New `docs/` reference files

| Path | Lines | Holds |
| --- | ---: | --- |
| `docs/DEPLOYMENT.md` | 94 | Jekyll, `_config.yml`, the Liquid deploy trap, the no-301 constraint, where a new URL goes, the CI contract |
| `docs/ARCHITECTURE.md` | 112 | Page assembly, the 446/17 split, `page_shell`, `boards.json`, generated assets, the layout map |
| `docs/HISTORY.md` | 128 | Nine stories: the stale counts, the finished-projects framing, the deleted script, the served source file, the hand-edited generated page, inline-style specificity, Prettier, GSC-frozen heads |

---

## 5. Beyond CLAUDE.md — how to set this repo up for Claude Code

You asked for this. Four recommendations, in order of value.

### 5.1 A `PreToolUse` hook that blocks writes to generated files — do this one

**This is the highest-value item in the whole phase, and it is the honest answer
to your "what has gone wrong that the file doesn't prevent" question.**

A rule in a document is advisory. On 2026-08-20 a generated page was hand-edited
and the edit was queued to be silently reverted by the next build. The rule
against that was already written down, in bold, in the file — and it did not
help, because a rule only fires if the model happens to be thinking about it.

A hook fires every time. In `.claude/settings.json`:

```jsonc
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write|NotebookEdit",
      "hooks": [{ "type": "command", "command": ".claude/hooks/block-generated.sh" }]
    }]
  }
}
```

The script exits non-zero with an explanatory message when the target path is
generated, and Claude is told to edit the source instead. The generated set is
exactly:

```
revision-notes/**            except index.html, macroeconomics-diagrams.html,
                             microeconomics-diagrams.html
practice-questions/**   past-paper-questions/**   flashcards/**
glossary-data/terms.json     sitemap.xml   sitemaps/**
past-paper-questions-data/taxonomy.json
```

`python3 scripts/bake_templates.py` prints the 17 hand-written pages, so the
allowlist can be derived rather than transcribed. **I can write this if you
want it** — say the word.

### 5.2 Your `.claude/settings.local.json` is dead config — every path in it is wrong

All of its path-scoped permissions point at
`/Users/eliotking/Desktop/GitHub/economics-academy`. The repo is at
`/Users/eliotking/Desktop/Economics Academy/github/economics-academy`. The old
path **does not exist** — I checked. So every one of those rules has been
silently failing to match, and you have been re-approving the same commands ever
since the folder moved.

**Recommendation:** replace it with a checked-in `.claude/settings.json` holding
a relative-path allowlist for the read-only verification commands, so the whole
suite runs without a prompt:

```jsonc
{
  "permissions": {
    "allow": [
      "Bash(python3 scripts/verify_*.py:*)",
      "Bash(python3 scripts/build_sitemap.py --check)",
      "Bash(python3 scripts/check_glossary_capitalisation.py --check)",
      "Bash(python3 seo/tools/verify_seo.py)",
      "Bash(node scripts/test_*.js)",
      "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)",
      "Bash(npx prettier@3.9.6 --check:*)"
    ]
  }
}
```

Checked in, so it follows the repo if it moves again. `.claude/settings.local.json`
is now gitignored (commit `5259bf0`) and is the right place for anything
machine-specific.

### 5.3 Two slash commands for the sequences that get done wrong

`.claude/commands/verify.md` — run the full 24-check suite and report pass/fail
per check. It is currently a 24-line shell invocation reconstructed from memory
every time, which is exactly how a check gets quietly skipped.

`.claude/commands/rebuild-nav.md` — the five generators, then
`bake_templates.py --apply`, then commit, **then** `build_sitemap.py`. The
ordering is the part that goes wrong: the sitemap takes `lastmod` from
`git log`, so running it before the commit bakes in stale dates. That happened
in this very session and needed a second commit to fix.

### 5.4 Worth considering, lower value

- **A `docs/PERFORMANCE.md`.** You want performance work. The relevant baselines
  are currently spread across `seo/09-web-vitals-baseline.md`, the Lighthouse
  JSON medians and `PROGRESS.md`. One page saying "here is what the site scores,
  here is what is known to cost it, here is how to measure a change" would make
  that work startable without an archaeology pass. The known items today are
  web-font CLS (0.078 notes / 0.154 questions) and MathJax loading from a CDN on
  the LaTeX-bearing notes pages.
- **Leave `.venv/` exactly as it is.** Gitignored, never committed, documented in
  `requirements.txt`. It costs the repo nothing.

---

## 6. What I need from you

1. **Approve or amend the root draft** at `_working/audit/CLAUDE.md.draft`.
   Particularly "How to work here" — that section is me putting words in your
   mouth about how much latitude you want.
2. **Eight nested files, or fewer?** The four `*-data/` ones are small and could
   instead be one `docs/DATA-MODEL.md` that the root file points at. I recommend
   nested: auto-loading beats remembering to read something.
3. **The hook (5.1) — yes or no?** It is the only change here that would have
   prevented an actual failure.
4. **The permissions file (5.2) — yes or no?** Pure convenience, no risk.
5. Anything in §3's "deliberately not carried forward" you want kept.

Nothing is in place. On your go I will move the drafts in, add the two
`_config.yml` lines, and re-run the suite.
