# Phase 1 findings — repo, file structure & URL architecture

Run 2026-08-08 on `audit/organisation-audit` at `d220ad0`. IDs continue from
Phase 0 and are stable.

**Scope note.** Two site changes were made during this phase on Eliot's explicit
instruction and are not audit actions: the 26 Finder duplicates were deleted, and
the two exam-board specification PDFs were removed (`d220ad0`). PH00-005 and
PH00-009 are therefore **RESOLVED**. Everything else here is logged, not fixed.

---

## What is clean, so nobody re-audits it

| Check | Result |
| --- | --- |
| Case-sensitivity of every `src`/`href` to a served file | **0 mismatches.** Matters because GitHub Pages is case-sensitive and macOS is not, so a mismatch works locally and 404s live |
| References to files that do not exist | **0** |
| Tracked files that an existing `.gitignore` rule would now catch | **0** |
| Dead `.gitignore` patterns | **0** — every rule still matches something on disk, or guards a real class (`.vscode/`, `*.swp`, `Thumbs.db`) |
| Branches with unmerged work | **0 of 14** |
| Naming convention (lowercase kebab-case) | 2 genuine violations out of 1,555 files — see PH01-018 |

---

## PH01-012 — 111 hardcoded board string literals across 9 generators

**Severity:** High · **Category:** Data model / scaling · **CERTAIN** ·
*Elaborates PH00-003*

**Evidence.** The translation between board encodings exists — it is just written
out by hand, in each generator that needs it.
[`scripts/build_flashcards.py:57-64`](../../scripts/build_flashcards.py#L57-L64):

```python
# (board, theme) -> the revision-notes directory that teaches it.
NOTES_DIRS = {
    ("edexcel-a", "theme-1"): "edexcel-theme-1",
    ("edexcel-a", "theme-2"): "edexcel-theme-2",
    ("edexcel-a", "theme-3"): "edexcel-theme-3",
    ("edexcel-a", "theme-4"): "edexcel-theme-4",
    ("aqa", "micro"): "aqa-a2-micro",
    ("aqa", "macro"): "aqa-a2-macro",
}
```

Counting board-name string literals per script:

```
scripts/build_questions.py                57
scripts/build_flashcards.py               12
scripts/build_past_paper_taxonomy.py      10
scripts/extract_glossary.py               10
scripts/build_glossary.py                  9
scripts/verify_glossary.py                 4
scripts/build_past_paper_questions.py      3
scripts/extract_aqa_questions.py           3
scripts/verify_past_paper_tags.py          3
                                    total 111
```

`build_glossary.py:679` even hardcodes the *pairing*:
`other_board = "aqa" if board == "edexcel-a" else "edexcel-a"` — which silently
assumes there will only ever be two boards.

**Why it matters.** This is the measured cost of PH00-003 and the single biggest
tax on the owner's stated goal. Adding OCR or Edexcel B notes means editing nine
scripts, choosing among three encodings in each, and finding the two-board
assumption baked into a ternary. Nothing would fail loudly if one were missed.

**Recommendation.** P9. One `boards.json` holding, per board: canonical `id`,
the slug used in each family's URLs, display name, and the notes directories.
Generators read it. **This changes no URL** — every existing slug becomes a
recorded value rather than something to fix. `scripts/build_sitemap.py:93` is the
in-repo precedent: it parses `_config.yml` rather than restating it.

**Effort:** M · **Risk of acting:** Low if URLs untouched · **Risk of not
acting:** High, and paid again per board · **Dependencies:** P9 · **Status:** OPEN

---

## PH01-013 — 31 unreferenced brand assets are published, 2.5 MB, including the entire `logo/` directory

**Severity:** Medium · **Category:** Published surface · **CERTAIN**

**Evidence.** Cross-referencing every published asset against every published
`.html`, `.css`, `.js`, `.json`, `.xml` and `.webmanifest`:

```
  8  logo/                        (0 references — the whole directory)
 13  old-logos-archive/           (incl. favicon-assets/)
  3  favicon-{16,32,48}x48.png    at root
```

`logo/` is not a stale archive — it is the current brand kit
(`economics-academy-logo-horizontal.svg`, `-stacked.svg`, `-mark-square.svg` and
PNG equivalents). **No page uses any of them.** The site header is text:
`<h1><a href="/">Economics Academy</a></h1>` in
[`templates/header.html:4`](../../templates/header.html#L4).

The three root favicon PNGs are unreferenced because the pages link only
`/favicon.ico` and `/apple-touch-icon.png`, and `site.webmanifest` names only the
two `android-chrome-*` PNGs. CLAUDE.md tells a new page to include "the
favicon/manifest set", which overstates what is actually wired up.

**Why it matters.** Low SEO impact; moderate tidiness impact. `old-logos-archive/`
is 2.0 MB of superseded branding served publicly at guessable URLs, which is a
mild brand-hygiene issue rather than a technical one.

**Recommendation.** P1 decision, executed by you.

- `old-logos-archive/` → add to `_config.yml` `exclude`. Nothing links to it;
  keeping it in the repo is fine, serving it is pointless.
- `logo/` → **do not exclude without deciding first.** An unreferenced brand kit
  at a stable URL is genuinely useful to hand to a third party. If that is the
  intent, write it into `_config.yml`'s "deliberately NOT excluded" block, which
  is exactly what that block is for.
- The three root favicon PNGs → leave them. Harmless, and some crawlers probe
  `/favicon-32x32.png` directly. Correct CLAUDE.md's description instead.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low ·
**Dependencies:** none · **Status:** OPEN

---

## PH01-014 — `.codex/notes-workflow.md` is published as a live HTML page

**Severity:** Medium · **Category:** Published surface · **CERTAIN**

**Evidence.** `.codex/` is the only dotted directory GitHub Pages serves, and it
holds one tracked file. Jekyll renders markdown, so it is live at
`/.codex/notes-workflow.html`. It is internal tooling instruction — it opens
"When converting notes pages for this repository:".

It is also one of only **two** markdown files the site actually publishes, the
other being `revision-notes/macro-application/macro-application-uk-sa.md`. That
makes it the second of the two genuine Liquid deploy risks identified in
PH00-011: a stray `{%` in it would fail the whole deploy.

**Why it matters.** Same category as the `/REVIEW-NOTES.html` exposure that
`d085317` fixed — an internal working file that became a public URL because
nothing said otherwise. It was missed then because `_config.yml`'s exclude list
enumerates known directories and `.codex/` was not one of them.

**Recommendation.** Add `.codex/` to `_config.yml`'s `exclude`. Zero risk:
nothing links to it, and it has no GSC impressions.

**Effort:** S · **Risk of acting:** Low — removes one unlinked URL ·
**Risk of not acting:** Low-Medium — internal instructions public, and a live
deploy-failure surface · **Dependencies:** none ·
**Status: RESOLVED** 2026-08-09, `d7744c3`. Moved to
`docs/notes-conversion-workflow.md` rather than excluded — the content is a
procedure still in use and CLAUDE.md does not record it. See `DECISIONS.md` D14.

---

## PH01-015 — 10 diagram PNGs are published but referenced by nothing

**Severity:** Low · **Category:** Dead assets · **CERTAIN**

**Evidence.**

```
images/diagrams/comparative-advantage.png
images/diagrams/consumer-producer-surplus-competitive.png
images/diagrams/consumer-producer-surplus-monopoly.png
images/diagrams/game-theory.png
images/diagrams/lras-classical-keynesian-ad-shift.png
images/diagrams/lras-classical-shift.png
images/diagrams/lras-keynesian-shift.png
images/diagrams/supply-of-labour.png
images/diagrams/trade-union-competitive.png
images/diagrams/trade-union-monopsony.png
```

10 of 112 diagram PNGs. Every one names real A-Level content that the notes
cover.

**Why it matters.** Ambiguous, which is why this is a question rather than a
recommendation. These are either (a) diagrams drawn for pages that never used
them, (b) ground-truth references for the hand-authored SVGs in
`images/diagrams/svg/` — CLAUDE.md says each SVG "is verified against its
ground-truth PNG" — or (c) diagrams a notes page *should* be using and is not.

(b) is likely for several: `lras-classical-shift` and `lras-keynesian-shift` are
exactly the kind of pair the flashcard SVG work needed.

**Recommendation.** Do not delete. Check each against
`flashcards-data/**` and `images/diagrams/svg/` in P8; if they are SVG ground
truth they should arguably move to a `_`-prefixed directory so they stop being
published, since that costs nothing and they are working files.

**Effort:** S · **Risk of acting:** Medium if deleted blind — a PNG that is SVG
ground truth is not replaceable from the SVG · **Risk of not acting:** Low ·
**Dependencies:** P8 · **Status:** OPEN

---

## PH01-016 — Twelve progress documents, 9,336 lines, with overlapping jurisdiction

**Severity:** Medium · **Category:** Governance · **CERTAIN**

**Evidence.**

| Document | Lines | Last touched |
| --- | ---: | --- |
| `QUESTIONS_PROGRESS.md` | 2,949 | 2026-08-01 |
| `REVIEW-NOTES.md` | 1,596 | 2026-08-04 |
| `docs/FLASHCARDS_PROGRESS.md` | 1,399 | 2026-08-07 |
| `docs/QA_FIXES_PROGRESS.md` | 705 | 2026-08-07 |
| `docs/CONTENT_ISSUES.md` | 659 | 2026-08-07 |
| `PAST-PAPERS-PROGRESS.md` | 483 | 2026-08-07 |
| `QUESTIONS_GUIDE.md` | 403 | 2026-08-01 |
| `_working/glossary/PROGRESS.md` | 361 | 2026-08-07 |
| `extraction-qa-report.md` | 307 | 2026-08-02 |
| `PROJECT-LOG.md` | 267 | 2026-08-04 |
| `NEW-CONTENT-LOG.md` | 166 | 2026-08-01 |
| `ROADMAP.md` | 41 | 2026-08-04 |
| **Total** | **9,336** | |

Plus `CLAUDE.md` at 23,660 bytes, whose "See also" section is the only index and
lists 10 of the 12.

Two overlaps are structural rather than cosmetic. **Known-defect logging is split
three ways**: `REVIEW-NOTES.md` ("problems found but not fixed, including open
economics content errors"), `docs/CONTENT_ISSUES.md` ("suspected notes errors
found while writing cards"), and `PROJECT-LOG.md` ("the single consolidated list
of what is still flagged" — which by its own description should be the only one).
**Progress state is split by location for no stated reason**: three progress
files at root, three under `docs/`, one under `_working/`.

**Why it matters.** Governance, and it compounds. CLAUDE.md tells a fresh session
to "Start here" at `PROJECT-LOG.md` while four other documents also claim to hold
current state. The risk is a real defect logged in the file nobody reads.

**Recommendation.** P10. Do not merge the content — these are records and merging
loses provenance. Instead: pick one location convention, and make
`PROJECT-LOG.md` genuinely the single index by having it point at the others
rather than duplicate them. The naming split is separate — see PH01-018.

**Effort:** M · **Risk of acting:** Low · **Risk of not acting:** Medium ·
**Dependencies:** P10 · **Status:** OPEN

---

## PH01-017 — Sitemap `lastmod` drifts silently; nothing re-runs the generator after a commit

**Severity:** Medium · **Category:** Tooling / governance · **CERTAIN** ·
*Found in P1, belongs to P9b*

**Evidence.** Before any change in this session, `build_sitemap.py --check`
reported `WOULD CHANGE sitemaps/core.xml`. The diff:

```
- about.html     <lastmod>2026-07-31</lastmod>
+ about.html     <lastmod>2026-08-08</lastmod>
- contact.html   <lastmod>2026-07-31</lastmod>   (and marking.html, tutoring.html)
+ contact.html   <lastmod>2026-08-08</lastmod>
```

Four root pages were committed **after** the sitemap was last generated — the
`@import` hoist in `4db232c` touched every page — so the sitemap advertised them
as older than they are.

**Why it matters.** Modest but self-inflicted. The generator exists precisely
because "every generator stamped `<lastmod>` with the date it ran" and Google
"had no reason to trust the field" (its own docstring). Taking the date from git
fixed the accuracy; nothing fixed the *freshness*, so the field decays after
every commit that does not happen to be followed by a rebuild.

Note this is the mildest possible instance of a general problem — **there is no
CI, so no generated artefact is guaranteed to match its source.** P9b measures
the general case.

**Recommendation.** P9b to measure, P10 to fix. `--check` already exits usefully,
so this is a pre-commit hook or a GitHub Action away. Resolved incidentally for
`core.xml` by `d220ad0`; the mechanism is untouched.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low-Medium ·
**Dependencies:** P9b, P10 · **Status:** OPEN

---

## PH01-018 — Three naming conventions for documents, three spellings of "JPEG", two stray filenames

**Severity:** Low · **Category:** Naming · **CERTAIN**

**Evidence.** 40 of 1,555 tracked paths break lowercase-kebab. All but two are
legitimate (root docs are conventionally uppercase; `css/vendor/katex/fonts/`
is vendor). The genuine items:

```
images/diagrams/Indirect-tax-incidence-elastic-inelastic.png   capitalised
images/eliot_shirt.JPG                                          snake_case + uppercase ext
```

Both are referenced with matching case, so **neither is broken** — the
case-sensitivity check returned 0 mismatches. They are a trap rather than a
defect: the repo's rule is lowercase kebab-case, and these are the two places
where copying the pattern would produce a live 404 on GitHub Pages while working
on macOS.

Image extensions: `112 .png`, `83 .svg`, and then `1 .jpg`, `1 .jpeg`, `1 .JPG` —
three spellings across three files.

Document naming: root uses `SCREAMING-KEBAB.md` (`PROJECT-LOG`, `REVIEW-NOTES`,
`NEW-CONTENT-LOG`), root *also* uses `SCREAMING_SNAKE.md` (`QUESTIONS_GUIDE`,
`QUESTIONS_PROGRESS`), and `docs/` uses `SCREAMING_SNAKE.md` throughout. Three
conventions, no rule.

**Why it matters.** Low. It is the kind of inconsistency that makes a repo feel
unowned, and the two case-sensitive filenames are a genuine (if currently
dormant) GitHub Pages hazard.

**Recommendation.** Renaming `images/*` is a URL change for assets — low risk
since nothing external hotlinks them, but not free. Recommend: **leave the two
files, write the rule down**, and enforce it for new files only. Not worth
churn.

**Effort:** S · **Risk of acting:** Low-Medium (asset URL change) ·
**Risk of not acting:** Low · **Dependencies:** P10 · **Status:** OPEN

---

## The URL-shape rule, for the next page family

P1's deliverable against PH00-002. **Nothing existing changes.**

Existing state, recorded as fact rather than defect:

| Family | Shape | Verdict |
| --- | --- | --- |
| `revision-notes/<board-dir>/<spec>-<slug>.html` | flat `.html` | **frozen historical exception** |
| `practice-questions/<board-dir>/<spec>-<slug>.html` | flat `.html` | **frozen historical exception** — deliberately mirrors notes 1:1, which is worth more than shape consistency |
| `past-paper-questions/<board>/<slug>/` | directory | conforms |
| `flashcards/<board>/<theme>/` | directory | conforms |
| `revision-notes/glossary/<board>/` | directory | conforms |

**The rule.** A new page family uses `directory/` form with a trailing slash.
Three of five already do, it is the form the SEO pass canonicalised everything
to, and it leaves the extension free to change later without a URL change.

**Where it nests** is already answered in CLAUDE.md and needs no restatement: a
feature nests under the section it belongs to; only a standalone tool sits at
root. Worth adding is *why the two `.html` families are not a precedent* — they
predate the rule, and the cost of changing them is unbounded because GitHub
Pages cannot issue a 301.

**One thing this rule does not settle**, and P9 must: the *board segment*. Three
of the five conforming families put the board first (`<board>/<thing>/`) and the
glossary puts it second (`glossary/<board>/`). Both are defensible. The rule
should say which, and PH01-012's `boards.json` is where the answer gets recorded.

---

## Answers to Phase 0 open questions

### Q14 — the 282 exam-board PDFs · **out of scope, as recommended**

286 files under `past-papers/`, and the bulk of the 176 MB `.git`. Git LFS would
rewrite history and change every commit SHA — for a solo project whose only clone
is on one machine, that trades a real risk for a benefit nobody needs. GSC treats
most of them as duplicates of other sites' copies, which
`seo/07b-link-decisions.md` §5 already accepted as correct and unfixable. **No
recommendation.**

One observation for the copyright thread opened by the specification removal:
these are the same category of file. They differ in that they are the site's
actual product, extensively linked, and earning impressions — so the calculus is
genuinely different, not merely more convenient. Flagging it as yours to think
about, not proposing anything.

### Q15 — `backup-pre-enrichment` · **safe to delete**

```
git rev-list --count main..backup-pre-enrichment   →  0
```

Zero unique commits. `git diff main backup-pre-enrichment` shows 1,016 files and
625,435 deletions, all of which is `main` being *ahead* — the branch is a
snapshot of an older state, fully contained in history. Deleting the ref loses
nothing; the commits stay reachable from `main`.

The same is true of all 13 others: every branch reports 0 unique commits.

**Recommendation.** Delete all 13 merged branches, local and remote. Yours to
run — the audit does not push.

```
for b in backup-pre-enrichment chore/flags-w2-w3 chore/revision-notes-audit \
         feature/glossary feature/question-bank feature/question-bank-as-level \
         feature/topic-questions fix/glossary-polish flashcards-feature \
         flashcards-qa-fixes logo-migration notes-consistency-pass \
         seo/architecture-pass seo/indexing-fixes; do
  git branch -d "$b" && git push origin --delete "$b"
done
```

`git branch -d` (not `-D`) refuses anything unmerged, so it is self-checking.
`seo/indexing-fixes` has no remote counterpart; that push will report an error
and can be ignored.

---

## Status changes

| ID | Was | Now | Why |
| --- | --- | --- | --- |
| PH00-005 | OPEN | **RESOLVED** | Specifications removed in `d220ad0`; `old-logos-archive/` carried forward as PH01-013 |
| PH00-009 | OPEN | **RESOLVED** | 26 Finder duplicates deleted; 0 remain, 0 tracked |
| PH00-010 | OPEN | **RESOLVED** | All 14 merged branches deleted 2026-08-09, local and remote. Every tip still an ancestor of `main` — refs gone, history intact. D15 |
| PH01-014 | OPEN | **RESOLVED** | `.codex/` removed, content moved to `docs/`. D14 |
| PH01-013 | OPEN | OPEN — **narrowed** | `logo/` recorded in `_config.yml` as UNDECIDED and left published (D13). `old-logos-archive/` and the 3 root favicon PNGs still unaddressed |
