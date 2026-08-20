# Restructure plan — economics-academy

Proposal only. Nothing here has been executed. Written 2026-08-20 against
`6cc2d65`, with the three Phase 1 fixes committed and the full CI suite green.

**Read §7 first if you only read one section.** It is the list of things I think
you should *not* do, and it is longer than the list of things I think you should.

---

## 1. The rules this plan obeys

1. **No published URL moves.** GitHub Pages cannot issue a 301 — no
   `_redirects`, no `netlify.toml`, no `.htaccess`, and the default Jekyll build
   offers nothing equivalent. That was already evaluated and rejected for the
   glossary on 2026-08-07. Every step below touches only files that
   `_config.yml` excludes from the build, so **not one live URL changes.**
2. **`git mv`, never `mv`.** History follows the file.
3. **Nothing is `rm`ed** except 68 files that git has never tracked (§3, Step 1)
   — and even that needs your explicit yes.
4. **One category per commit**, each independently revertable.
5. **Every move of an excluded path is a two-file lockstep commit:**
   `_config.yml` *and* `docs/audit/scripts/lib.py`. `lib.py` restates the exclude
   list and calls `verify_matches_config()` on import, so if the two drift,
   every script in `docs/audit/scripts/` fails immediately. That is a free
   verification step and the plan uses it as one.

### What "verified" means at each step

The repo has an unusually strong safety net. Every step below ends with:

```
python3 -c "import sys;sys.path.insert(0,'docs/audit/scripts');import lib"   # exclude lists agree
python3 scripts/verify_published_surface.py    # nothing new is served
python3 scripts/build_sitemap.py --check       # exit 0, no WOULD CHANGE lines
python3 scripts/verify_generated.py            # all 8 generators reproduce the tree
python3 scripts/verify_links.py                # 11,286 internal refs, 0 broken
```

and the full 23-check CI suite before the final push. All 23 are green today.

---

## 2. Target tree — before and after

Only the changed parts are shown. **Everything not listed stays exactly where it
is**, including all 1,099 published files.

```
BEFORE                                  AFTER
──────────────────────────────────────  ──────────────────────────────────────
CLAUDE.md                               CLAUDE.md              (rewritten, Ph3)
README.md                               README.md
OWNER-TODO.md                           OWNER-TODO.md          ← stays: yours
PROGRESS.md                             PROGRESS.md            ← stays: entry point
PROJECT-LOG.md                          docs/PROJECT-LOG.md
PAST-PAPERS-PROGRESS.md                 docs/PAST-PAPERS-PROGRESS.md
QUESTIONS_PROGRESS.md                   docs/QUESTIONS_PROGRESS.md
QUESTIONS_GUIDE.md                      docs/QUESTIONS_GUIDE.md
REVIEW-NOTES.md                         docs/REVIEW-NOTES.md
ROADMAP.md                              docs/ROADMAP.md
NEW-CONTENT-LOG.md                      _archive/NEW-CONTENT-LOG.md
extraction-qa-report.md                 _archive/extraction-qa-report.md
README.txt                              _archive/README.txt
raw-notes/            (75 files)        _archive/raw-notes/
images/diagrams/game-theory.png         _archive/diagrams/game-theory.png
images/diagrams/comparative-advantage.png  _archive/diagrams/comparative-advantage.png
(68 Finder duplicates, untracked)       deleted from disk
.gitignore                              .gitignore  + 3 lines

docs/  (10 files + audit/)              docs/  (16 files + audit/)  ← flat, no new subdirs
```

**Root markdown: 12 files → 4.** The four that stay are the ones you or a fresh
session actually open first.

**`docs/` stays flat.** I considered `docs/progress/`, `docs/guides/`,
`docs/issues/`. Sixteen files do not need three subdirectories, and each one
would double the path-rewriting in every step below. Bicycle, not spaceship.

### Why `_archive/` and not `.gitignore`

You offered me the choice. **Recommendation: `_archive/`, tracked in git,
excluded from the build by Jekyll's underscore rule.** Reasoning:

- Gitignoring it takes the files *out of git*. The only copy would then be your
  disk, and the only recoverable copy would be in history at the old path — the
  exact archaeology you said you wanted to avoid. Tracked means `git mv` carries
  the full history forward and the file stays readable on GitHub.
- The underscore prefix is **structural** exclusion. `_working/` already relies
  on it, `build_sitemap.py` skips any path segment starting with `_` natively,
  and `lib.py`'s `EXCLUDED_PREFIXES` already contains a bare `"_"`. Nothing has
  to be remembered.
- Cost: the repo is public, so `_archive/` is readable on GitHub. So are
  `docs/`, `seo/` and `REVIEW-NOTES.md` today, on a judgement CLAUDE.md already
  records. This changes nothing about that.
- I will still add `_archive/` to `_config.yml`'s "already excluded by the
  underscore rule, listed so the intent survives" block — matching exactly what
  the file does for `_working/`.

**One caveat you should know:** adding a `.nojekyll` file at any point in the
future would immediately expose every `_` directory, `_archive/` and `_working/`
included. That is already true today and already written down in CLAUDE.md.
This plan adds one more directory to that blast radius.

---

## 3. Migration sequence

Ordered by risk, lowest first. Each step is one commit.

### Step 1 — Finder duplicates and `.gitignore` (zero risk)

**Needs your explicit yes: this is the only `rm` in the plan.**

68 files matching `* [0-9].*`. Every one is untracked (`git ls-files` returns
none of them), every one is ignored (`git check-ignore -v` attributes each to
`.gitignore` line 27), none is published, none is in a sitemap. Deleting them
removes nothing git can lose.

```bash
# Look before you leap — this prints the list without deleting anything:
find . -name '* [0-9].*' -not -path './.git/*' -not -path './.venv/*'

# Confirm every one is untracked. Must print nothing:
find . -name '* [0-9].*' -not -path './.git/*' -not -path './.venv/*' -print0 \
  | xargs -0 git ls-files --error-unmatch 2>/dev/null

# Then, and only after you have said yes:
find . -name '* [0-9].*' -not -path './.git/*' -not -path './.venv/*' -delete
```

Then harden `.gitignore` against the two things that produced them:

```bash
cat >> .gitignore <<'EOF'

# Claude Code local settings. Machine-specific; nothing here belongs to anyone
# else working on the repo.
.claude/settings.local.json

# Xcode / Swift build products, if extract_past_paper_questions.swift is ever
# compiled rather than run with `swift`.
.build/
*.o
EOF
git add .gitignore && git commit -m "chore: ignore local Claude settings and Swift build products"
```

**Rewrites needed:** none.
**Verify:** `git status --porcelain` clean; `python3 scripts/verify_published_surface.py`.
**Rollback:** `git revert HEAD` for the `.gitignore` commit. The deleted files
are **not** recoverable from git — they were never in it. That is why the
confirmation step above exists. If you would rather not, skip the `-delete` and
keep them; they cost nothing but noise.

---

### Step 2 — create `_archive/` and retire three dead root files (zero risk)

`NEW-CONTENT-LOG.md`, `extraction-qa-report.md`, `README.txt`. Evidence for each
is in `REPO-AUDIT.md` §3; in short: a per-batch review log for a merged-and-gone
branch, a completed one-off QA report, and the HTML5 UP "Dopetrope" template
readme.

```bash
mkdir -p _archive
git mv NEW-CONTENT-LOG.md      _archive/NEW-CONTENT-LOG.md
git mv extraction-qa-report.md _archive/extraction-qa-report.md
git mv README.txt              _archive/README.txt
```

Write `_archive/README.md` saying what the directory is and that
`_archive/README.txt` is the *template's* readme, kept for its CCA 3.0
attribution to HTML5 UP — that attribution is the one reason not to simply
delete it.

**Files whose contents need rewriting** (exact counts measured, not estimated):

| File | mentions to update |
| --- | ---: |
| `_config.yml` | 3 — remove all three from `exclude:`, they are now under `_archive/` |
| `docs/audit/scripts/lib.py` | 3 — remove from `EXCLUDED_FILES` (lockstep with above) |
| `CLAUDE.md` | 1 (`extraction-qa-report.md`) |
| `PROJECT-LOG.md` | 2 |
| `REVIEW-NOTES.md` | 1 |
| `PAST-PAPERS-PROGRESS.md` | 2 |
| `_working/question-bank/as-extraction-qa.md` | 1 |

Also add to `_config.yml`, in the existing underscore-rule comment block:

```yaml
  - _working/
  - _archive/          # NEW — same rule, listed so the intent survives
  - .github/
```

**Deliberately NOT rewritten:** `docs/audit/findings/PH01-structure.md` and
`PH10-tooling.md`. Those are **dated findings describing the tree as it was**.
Rewriting a path inside a historical record falsifies the record. Same principle
for `docs/audit/DECISIONS.md`, which is append-only. If a future reader is
confused, the fix is a new decision entry, not an edit to an old one.

**Verify:**
```bash
python3 -c "import sys;sys.path.insert(0,'docs/audit/scripts');import lib"
python3 scripts/verify_published_surface.py
python3 scripts/build_sitemap.py --check
git ls-files _archive/ | wc -l          # expect 4
```
**Rollback:** `git revert <sha>`.

---

### Step 3 — `raw-notes/` → `_archive/raw-notes/` (low risk)

75 files, 368 KB. Nothing reads it. The script that consumed it,
`convert_raw_notes.py`, was deleted on 2026-08-13 under D44. I re-measured the
drift independently: **0 of 73 markdown files are still in sync with their live
page**, median word overlap 0.63, worst 0.40.

This is the one directory a future session could mistake for a build input.
Moving it under `_archive/` makes that mistake impossible to make.

```bash
git mv raw-notes _archive/raw-notes
```

**Rewrites:** `_config.yml` (drop `raw-notes/` from `exclude:`),
`docs/audit/scripts/lib.py` (drop from `EXCLUDED_PREFIXES`), `CLAUDE.md`
(3 mentions incl. the Layout block), `PROJECT-LOG.md`, `REVIEW-NOTES.md`,
`QUESTIONS_PROGRESS.md`, `_working/glossary/PROGRESS.md`,
`docs/notes-conversion-workflow.md`.

Two references are **comments only** and I would update them for accuracy:
`.github/workflows/verify.yml` line 11 and
`scripts/verify_published_surface.py` line 64. Neither is executable code —
`verify_published_surface.py` mentions `raw-notes/` in its docstring explaining
where `macro-application-uk-sa.md` was moved to, and that sentence stays true if
you write `_archive/raw-notes/`.

Again, **leave `docs/audit/**` findings and `DECISIONS.md` alone.**

**Verify:** the five commands in §1, plus
`ls _archive/raw-notes/edexcel | wc -l` → 73.
**Rollback:** `git revert <sha>`.

---

### Step 4 — consolidate the six project records into `docs/` (low risk, most churn)

This is the step that actually answers "loose progress files".

**The argument I find convincing:** `docs/FLASHCARDS_PROGRESS.md` and
`docs/QA_FIXES_PROGRESS.md` already live in `docs/`, while
`PAST-PAPERS-PROGRESS.md` and `QUESTIONS_PROGRESS.md` sit at root doing exactly
the same job. That is an inconsistency with no reason behind it, and it is the
kind that makes a repo feel disordered even when nothing is wrong.

**The argument I do not find convincing, and want to correct:** I first thought
this was a *safety* win, because root markdown is public-by-default and only
kept private by being named individually in `_config.yml`. On inspection it
mostly is not — `scripts/verify_published_surface.py` whitelists file suffixes
and `.md` is not on the list, so CI catches a stray root markdown file. The
residual gap is narrow: CI is verification-only and does not block the deploy,
so a stray file would be live for as long as it took you to notice, and `.txt`
*is* whitelisted. Real, but small. **Treat this step as tidiness, not safety.**

```bash
git mv PROJECT-LOG.md           docs/PROJECT-LOG.md
git mv PAST-PAPERS-PROGRESS.md  docs/PAST-PAPERS-PROGRESS.md
git mv QUESTIONS_PROGRESS.md    docs/QUESTIONS_PROGRESS.md
git mv QUESTIONS_GUIDE.md       docs/QUESTIONS_GUIDE.md
git mv REVIEW-NOTES.md          docs/REVIEW-NOTES.md
git mv ROADMAP.md               docs/ROADMAP.md
```

**Files to rewrite, measured exactly.** Counts are occurrences, and the match
must be anchored — a naive `s/PROGRESS.md/…/` also hits
`PAST-PAPERS-PROGRESS.md`, `QUESTIONS_PROGRESS.md`, `FLASHCARDS_PROGRESS.md`,
`QA_FIXES_PROGRESS.md` and `docs/audit/PROGRESS.md`. Use
`(?<![-\w/])<name>` as the pattern.

| Moved file | non-published files to rewrite |
| --- | --- |
| `PROJECT-LOG.md` | `CLAUDE.md`(1) `_config.yml`(1) `lib.py`(1) `REVIEW-NOTES.md`(2) `PAST-PAPERS-PROGRESS.md`(1) `docs/audit/OPEN-QUESTIONS.md`(1) `docs/audit/PROGRESS.md`(2) |
| `PAST-PAPERS-PROGRESS.md` | `CLAUDE.md`(2) `_config.yml`(1) `lib.py`(1) `docs/QA_FIXES_PROGRESS.md`(1) `docs/audit/OPEN-QUESTIONS.md`(1) |
| `QUESTIONS_PROGRESS.md` | `CLAUDE.md`(1) `_config.yml`(1) `lib.py`(1) `PROJECT-LOG.md`(2) `QUESTIONS_GUIDE.md`(2) `REVIEW-NOTES.md`(4) `PAST-PAPERS-PROGRESS.md`(2) `scripts/extract_past_paper_questions.swift`(1) |
| `QUESTIONS_GUIDE.md` | `CLAUDE.md`(1) `_config.yml`(1) `lib.py`(1) `PROJECT-LOG.md`(2) `QUESTIONS_PROGRESS.md`(4) `REVIEW-NOTES.md`(2) `scripts/build_questions.py`(1) |
| `REVIEW-NOTES.md` | `CLAUDE.md`(2) `_config.yml`(2) `lib.py`(1) `OWNER-TODO.md`(1) `PROJECT-LOG.md`(2) `QUESTIONS_PROGRESS.md`(16) `ROADMAP.md`(1) `_working/glossary/PROGRESS.md`(2) `_working/glossary/gap-report.md`(2) `docs/CONTENT_ISSUES.md`(1) `docs/audit/PROGRESS.md`(4) `scripts/check_glossary_capitalisation.py`(1) `scripts/verify_liquid.py`(1) |
| `ROADMAP.md` | `CLAUDE.md`(1) `_config.yml`(1) `lib.py`(1) `PROJECT-LOG.md`(1) `_working/glossary/PROGRESS.md`(3) `scripts/build_glossary.py`(1) |

**Two published files name `REVIEW-NOTES.md` in a source comment:**
`css/pages/revision-notes-textbook.css` line 523 and `js/components/nav.js`
line 131. Both are comments with no rendered effect. **My recommendation: leave
them.** They are shipped bytes, editing them makes this commit touch the
published surface for zero user benefit, and a comment reading "logged as G2 in
REVIEW-NOTES.md" is still findable. If you would rather they were right, it is
a two-line follow-up commit of its own, not part of this one.

**Verify:** the five commands in §1, plus
```bash
ls *.md            # expect exactly: CLAUDE.md OWNER-TODO.md PROGRESS.md README.md
grep -rn "](\.\./" docs/*.md | head      # no relative links broke on the way in
```
**Rollback:** `git revert <sha>`. If only part of it is wrong,
`git checkout <sha>~1 -- <path>` per file.

---

### Step 5 — two superseded diagram PNGs (low risk)

`images/diagrams/game-theory.png` and `images/diagrams/comparative-advantage.png`
are unreferenced by any served file. Both are documented in
`docs/CONTENT_ISSUES.md` (#9 and #23) as **known-incorrect**, replaced by
redrawn SVGs with your approval on 2026-08-05, and #9 says in as many words
"do not use it as ground truth".

```bash
mkdir -p _archive/diagrams
git mv images/diagrams/game-theory.png          _archive/diagrams/game-theory.png
git mv images/diagrams/comparative-advantage.png _archive/diagrams/comparative-advantage.png
python3 scripts/build_sitemap.py     # they are not in a sitemap, but run it anyway
```

**This does remove two live URLs** — `/images/diagrams/game-theory.png` and
`/images/diagrams/comparative-advantage.png`. Neither appears in any sitemap,
neither is linked from any page, and neither is in your Search Console exports.
Google Images could conceivably hold them. If that worries you at all, **skip
this step** — two stale PNGs cost you nothing but 200 KB, and the CONTENT_ISSUES
entries already stop anyone using them by mistake. I would call this optional.

**Do NOT move** `trade-union-competitive.png`, `trade-union-monopsony.png` or
`svg/price-discrimination-combined-market.svg`. They are unreferenced because
the notes pages that would use them **do not exist yet** — `PH01-structure.md`
lists them as content gaps. Archiving them hides the gap.

**Verify:** `python3 scripts/verify_image_dimensions.py`,
`python3 scripts/verify_icons.py`, `python3 scripts/build_sitemap.py --check`.
**Rollback:** `git revert <sha>`.

---

### Step 6 — fix `_config.yml`'s stale self-description (zero risk, do it regardless)

Not a move. The file that decides your entire published surface currently
documents three directories that do not exist and one runtime fetch that stopped
happening in Wave 4.10:

- `templates/ — fetched at runtime by inject-templates.js` — false;
  `js/components/inject-templates.js` does not exist, and `nav.js` line 3 says
  it replaced it.
- `old-logos-archive/` — directory absent.
- `logo/` — directory absent. Nine lines agonise over an undecided question
  about a directory that is not there.

The `exclude:` list itself is correct and `verify_published_surface.py` passes.
Only the comments are wrong. **This is the cheapest high-value change in the
plan** — comment-only, zero risk, and it removes three pieces of misinformation
from the one file nobody can afford to misread.

**Rollback:** `git revert <sha>`.

---

## 4. Suggested commit sequence

```
1  chore: ignore local Claude settings and Swift build products
2  chore: retire three finished records to _archive/
3  chore: raw-notes/ is historical — move it to _archive/
4  chore: consolidate the project records into docs/
5  chore: archive two superseded diagram PNGs          [optional, see §3 Step 5]
6  docs(_config): correct three stale comments
```

Run the full 23-check suite once at the end, then push. **Do not push
mid-sequence** — steps 2–4 each leave the exclude lists briefly inconsistent
between staging and working tree if interrupted, and `main` auto-publishes.

---

## 5. Verification, per phase

| After step | Command | Expected |
| --- | --- | --- |
| any | `python3 -c "import sys;sys.path.insert(0,'docs/audit/scripts');import lib"` | no output — exclude lists agree |
| any | `python3 scripts/verify_published_surface.py` | `1099 tracked files are published` (unchanged by every step except 5, which gives 1097) |
| any | `python3 scripts/build_sitemap.py --check` | **exit 0 and no `WOULD CHANGE` lines.** "nothing written" is *not* the pass signal |
| any | `python3 scripts/verify_generated.py` | `all 8 generators ran; 0 files would change` |
| any | `python3 scripts/verify_links.py` | `11286 internal refs checked, 0 broken` |
| 4, 5 | `python3 scripts/verify_page_shell.py` | `463 published pages, 17 of them hand-written`, all checks ok |
| final | the 23-check suite | all green |

**Build the site locally** before the final push: Live Server on `index.html`,
then click through `/revision-notes/`, `/past-papers/ocr/`,
`/past-paper-questions/`, `/flashcards/` and `/marking.html`. Nothing in this
plan should change a single rendered pixel; if anything looks different, stop.

---

## 6. Universal rollback

Every step is one commit and nothing is force-pushed, so:

```bash
git revert <sha>                      # undo one step, keeps history honest
git revert <oldest-sha>..<newest-sha> # undo a run of steps
git checkout <sha>~1 -- <path>        # pull back one file from before a step
git reset --hard origin/main          # discard everything local, if nothing is pushed
```

The single irreversible action in the whole plan is the `find … -delete` in
Step 1, on files git has never tracked. Everything else is a `git mv` or a text
edit and comes back with one command.

---

## 7. What I recommend against

You said you would rather keep an ugly-but-working structure than break indexed
pages for tidiness. Applying that test:

### 7.1 Do not rename `questions-data/` — my Phase 1 instinct was wrong

I flagged in the audit that `questions-data/` feeds `practice-questions/` and
nothing in the name says so. Having counted the cost, I am withdrawing the
suggestion.

- **Cost:** 33 tracked files, of which **11 are scripts** including five
  generators, plus `_config.yml` and `lib.py`.
- **Benefit:** removes one naming confusion.
- **And the naming is not actually inconsistent.** The repo's pattern is
  `<thing>-data/` feeds `<place>/`: `notes-data/` → `revision-notes/`,
  `flashcards-data/` → `flashcards/`, `questions-data/` → `practice-questions/`.
  Nobody trips over the first two. The confusion is purely that
  `past-paper-questions-data/` sorts next to `questions-data/` in a directory
  listing.

**One line in the new CLAUDE.md fixes this for good, at a cost of one line.**
That is the right trade. If you disagree and want it renamed anyway, say so and
I will produce the exact command set — the risk genuinely is low, because
`verify_generated.py` re-runs all eight generators and would catch any missed
reference immediately. It is the effort, not the danger, that I am objecting to.

### 7.2 Do not move anything under `revision-notes/`, `past-papers/`, `practice-questions/`, `past-paper-questions/` or `flashcards/`

744 URLs in your sitemaps — 461 pages plus 283 PDFs. No redirect mechanism exists. There is no tidiness argument
that survives contact with that number.

### 7.3 Unpublishing `templates/` — technically free, and still not worth a commit

Phase 1 established that `/templates/header.html` and `/templates/footer.html`
have zero inbound links, are in no sitemap, are no longer fetched at runtime,
and appear in **none** of your eight Search Console exports. So removing them
from the published surface costs nothing measurable.

But it also *gains* nothing measurable — two unlisted files served to nobody.
It removes two live URLs, which is a category of change this plan otherwise
avoids entirely, in exchange for tidiness on a surface no user sees.
**Recommendation: leave it.** If you ever edit `_config.yml` for another reason
and want to close it out, the change is adding `- templates/` to `exclude:` and
nothing else. It is a footnote, not a step.

### 7.4 Do not split `REVIEW-NOTES.md` or `QUESTIONS_PROGRESS.md` yet

Phase 1 measured ~28% of `REVIEW-NOTES.md` and ~78% of `QUESTIONS_PROGRESS.md`
as finished record. Splitting them is a genuine improvement — but it means
*reading and classifying* 4,700 lines of your own notes, and getting a call
wrong archives an open economics error. That is a content review, not a
restructure, and it should not ride along in a tidying commit. **Propose it as
its own session, after Phase 3.**

### 7.5 Do not rewrite paths inside `docs/audit/findings/**` or `DECISIONS.md`

They are dated records of what the tree looked like at the time, and
`DECISIONS.md` is explicitly append-only. Steps 2–4 skip them deliberately. If
the stale paths ever confuse someone, the fix is a new decision entry.

### 7.6 Do not delete the four merged branches as part of this

`breadcrumb-standardisation`, `home-page-revamp`, `tutoring-seo-rework` and
`wave5-1-diagram-review` are all 0 commits ahead of `main`. Deleting them is
safe and one command each — but it is your call, not a restructure step, and
`git branch -d` refuses anything unmerged anyway so you cannot get it wrong.

### 7.7 `seo/lh-live-after/` — your call, no repo impact

23 MB on disk, already gitignored, regenerable by re-running
`seo/tools/run_lighthouse.py`. `rm -rf seo/lh-live-after/` frees the space and
git neither knows nor cares. Not in the plan because it is housekeeping on your
machine, not a repo change.

---

## 8. What this plan does not fix, and cannot

**The OCR June 2023 Paper 3 question paper is missing.** You confirmed both PDFs
are the mark scheme, and I verified it independently — page 1 of both reads
"GCE Economics · H460/03: Themes in economics · A Level · Mark Scheme for June
2023". I also swept all 281 PDFs for the same fault: 13 Edexcel files initially
flagged, all false positives from the text extractor splitting "M ark Scheme".
**This is the only genuine one.**

I cannot create the missing file. Your options:

1. **Download `H460/03` June 2023 question paper from OCR and overwrite
   `past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-june-2023-question-paper.pdf`.**
   Same filename, so no URL changes, no link changes, no sitemap change. This is
   the only option that leaves the site correct. Recommended.
2. **Interim, if you cannot get the file today:** remove the question-paper link
   from `past-papers/ocr/index.html` and drop the file and its sitemap entry.
   Honest, but it leaves a 404 at a URL Google has crawled, and it is a
   published-surface change.
3. **Leave it.** Every student who clicks "Question paper" for that sitting gets
   the mark scheme instead. I would not leave it.

Tell me which and I will do it. Until then it stays exactly as it is.

---

## 9. Open questions before I execute anything

1. **Step 1's `-delete`** — yes or no on removing the 68 untracked Finder
   duplicates?
2. **Step 5** — archive the two known-incorrect diagram PNGs, or leave them?
   They are the only step that removes a live URL.
3. **`ROADMAP.md`** — 41 lines, last touched 2026-08-04. Should it move to
   `docs/` as planned, or fold into `OWNER-TODO.md` and go to `_archive/`? I
   cannot tell which of its items you still want.
4. **`PROJECT-LOG.md` vs `PROGRESS.md`** — CLAUDE.md calls the first "Start
   here"; the second says "read this first" and has 14× the commits. Which is
   the entry point? Phase 3 needs the answer to write the pointer index.
5. **The two published source comments naming `REVIEW-NOTES.md`** — leave them
   pointing at the old path (my recommendation), or a follow-up commit?

---

Nothing executed. Say which steps you want and I will run them one commit at a
time, verifying between each.

---

## 10. Execution record — 2026-08-20

Executed with Eliot's answers to §9: delete the duplicates (yes), skip Step 5
(no), fold ROADMAP into OWNER-TODO, merge PROJECT-LOG into PROGRESS, leave the
two published source comments alone.

| Commit | Step |
| --- | --- |
| `5259bf0` | 1 — 68 untracked Finder duplicates deleted; `.gitignore` hardened |
| `418b985` | 2 — `_archive/` created; three finished records retired |
| `ca0da8a` | 3 — `raw-notes/` → `_archive/raw-notes/` |
| `9f9b165` | — the audit deliverables, committed separately |
| `cc931ce` | 4a — four project records → `docs/` |
| `d4bbe55` | 4b — `PROGRESS.md` absorbs `PROJECT-LOG.md`, becomes the entry point |
| `0646a37` | 4c — `ROADMAP.md` folded into `OWNER-TODO.md` |
| `7e9c0a5` | 6 — `_config.yml`'s three stale comments corrected |

**Step 5 skipped**, as instructed: the two known-incorrect diagram PNGs stay
published.

### Proof that no URL changed

The published surface was enumerated at `63437c6` (before) and at `HEAD`
(after) by applying `_config.yml`'s exclude list plus Jekyll's underscore rule
to `git ls-tree`:

```
published before : 1099
published after  : 1099
removed from the site: NOTHING
added to the site   : NOTHING
```

All 24 checks green, including `verify_generated.py` (8 generators, 0 files
would change) and `verify_published_surface.py`.

### Two deviations from the plan as written

1. **`ca0da8a` was committed twice.** The first attempt used `git add -A` and
   swept the audit deliverables into the `raw-notes` commit, breaking the
   one-category-per-commit rule. Nothing was pushed, so it was uncommitted and
   split into `ca0da8a` and `9f9b165`.
2. **`verify_links.py` reports 11,284 internal refs, not the 11,286 quoted in
   §1.** The two are the duplicate glossary cross-references removed by
   `6cc2d65`, before this sequence began. 0 broken throughout.

### Not done, still open

- The OCR June 2023 Paper 3 question paper (§8). Recorded in `PROGRESS.md`
  under "What remains flagged".
- Nothing is pushed. `main` auto-publishes, so that is Eliot's call.
