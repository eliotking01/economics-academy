# Phase 10 findings — tooling, automation & governance

Branch `audit/organisation-audit`, working tree at `4fd7d82`. Compiled
2026-08-09. **Read-only phase: no site file was opened for writing.**

Findings continue the audit's sequence at `PH10-060`.

---

## 1. The tooling, measured

**25 scripts in `scripts/`** (plus `scripts/vendor/`, which is KaTeX 0.16.11
vendored for the glossary build and correctly documented as build-time only) and
**13 in `seo/tools/`**. No `.github/` directory. No git hooks —
`.git/hooks/` contains only `.sample` files.

### The whole verification suite runs in 13.1 seconds

Every check, timed on this machine, working tree at `4fd7d82`:

| Command | Exit | Time | Last line |
| --- | ---: | ---: | --- |
| `verify_html.py` | 0 | 0.4 s | 179 files parsed, 0 with errors |
| `verify_links.py` | 0 | 0.5 s | broken fragments: 0 |
| `verify_liquid.py` | **1** | 0.1 s | 106 markdown files checked, **1 problem** |
| `verify_glossary.py` | 0 | 1.5 s | all checks passed |
| `verify_past_paper_tags.py` | 0 | 0.1 s | all tag checks passed |
| `verify_diagram_geometry.py` | 0 | 0.3 s | 83 files checked, 0 flags |
| `verify_text_integrity.py HEAD` | 0 | 3.8 s | visible text differs: 0 |
| `verify_markup_integrity.py HEAD --strict` | 0 | 3.0 s | 0 losses, 0 additions |
| `seo/tools/verify_seo.py` | 0 | 2.5 s | 14/14 assertions passed |
| `node test_question_search.js` | 0 | 0.3 s | all 552 records indexed |
| `node test_glossary_filter.js` | 0 | 0.1 s | all checks passed |
| `check_glossary_capitalisation.py` | 0 | 0.4 s | **2 Unclassified — needs a look** |
| `strip_source_attributions.py` | 0 | 0.1 s | would change 0 questions across 0 files |
| **Total** | | **13.1 s** | |

**That number is the whole automation argument.** Thirteen seconds, no
dependencies beyond Python 3 and Node, no network. Nothing runs any of it
automatically.

### What is well built, and should be said

- **All five one-shot site-mutating scripts in `seo/tools/` default to dry-run**
  and require `--apply`: `fix_font_loading.py`, `fix_links.py`,
  `fix_structured_data.py`, `add_diagram_gallery_links.py`,
  `upgrade_pastpaper_links.py`. Each has 3–4 dry-run flags and exactly one write
  call. Re-running any of them today does nothing without an explicit flag.
  **This is the correct pattern, and it is the exact opposite of PH06-027's
  `convert_raw_notes.py`, which has no guard at all.** The SEO tooling learned a
  lesson the notes converter did not.
- **`strip_source_attributions.py` reports `would change 0 questions across 0
  files`** — precisely the agreement CLAUDE.md names as the test. It passes.
- **`scripts/vendor/README.md` is a model of its kind**: it says what the file is,
  why it is vendored rather than fetched, what the browser gets instead, and how
  to upgrade. Every vendored dependency should be documented like this.

---

## 2. Findings

### PH10-060 — A markdown source file is published on the live site, and every verification script in the repo is blind to it

**Severity:** Medium-High · **Category:** Published surface / tooling ·
**CERTAIN**

**Evidence.**

```
revision-notes/macro-application/macro-application-uk-sa.md   429 lines
```

- **Tracked**, and **not** in `_config.yml`'s `exclude` — `grep` for
  `macro-application` and `revision-notes` in `_config.yml` returns nothing.
- `lib.is_published()` returns **True** for it.
- It has **no YAML front matter**, so Jekyll copies it verbatim rather than
  rendering it. It is served at
  `/revision-notes/macro-application/macro-application-uk-sa.md`.
- It is the **source** for the published `macro-application/index.html`, so the
  same content is on the site twice, in two formats, at two URLs.

**It is the only such file.** Every other tracked markdown is either excluded
(`raw-notes/`, `docs/`, `seo/`, the root files) or under `_working/`.

**Why this went unseen for the whole audit, which is the actual finding.** Every
tool that enumerates the published surface globs `*.html`:

```
lib.published_html()          -> tracked("*.html")
lib.pages()                   -> published_html() minus templates/
scripts/build_sitemap.py      -> enumerates .html and .pdf
scripts/verify_links.py       -> 179 .html files
```

So `is_published()` says **True** and `published_html()` says **False**, for the
same file. Phase 0 counted 463 published pages; `build_sitemap.py --check`
reports 461 pages plus 281 PDFs. **None of those numbers includes this file, and
none of them is wrong** — they are all counting HTML.

`_config.yml`'s exclude list is maintained **by directory**, and it catches every
directory that is *entirely* source. It cannot catch a source file that lives
inside a content directory, and nothing else looks.

**There is a second, sharper risk.** `DO-NOT-BREAK.md` records that Liquid runs
over every markdown file before Markdown, and a stray `{%` **fails the whole
deploy**. `verify_liquid.py` checks 106 markdown files and currently reports the
one known pre-existing problem (PH00-011). A markdown file inside a published
content directory is exactly where a future `{%` would be least expected and most
damaging.

**Recommendation.**

1. **Move it to `raw-notes/`**, beside `raw-notes/macro-application.md` — which
   already exists, is 229 lines, and is the same kind of artefact. `raw-notes/` is
   already excluded, so the move needs no `_config.yml` change. This is the same
   reasoning D14 used for `.codex/` → `docs/`.
2. **Add a check that closes the class, not the instance.** One assertion:
   *every tracked file under a published directory is either `.html`, an asset
   type, or explicitly excluded.* Roughly ten lines, and it belongs in the
   workflow proposed in PH10-062.

**Effort:** S · **Risk of acting:** Low — it is a `git mv` of an unreferenced
file; confirm nothing links to the `.md` URL first (nothing does: 0 references) ·
**Risk of not acting:** Medium — a live source file and an open deploy-failure
class · **Dependencies:** none · **Status:** OPEN

### PH10-061 — CLAUDE.md's numbers have drifted from what the verifiers report, and the verifiers are the ones that run

**Severity:** Medium · **Category:** Governance · **CERTAIN**

**Evidence.** CLAUDE.md's factual claims, checked against the files and against
`verify_glossary.py`'s own output:

| CLAUDE.md says | Measured | Verdict |
| --- | --- | --- |
| `images/diagrams/` — "**300** note diagrams" | **112** PNGs (195 image files incl. the 83 SVGs) | **wrong, by 2.7×** |
| `rewrite` "edits the lead-in of **46** definitions" | `curation.json` `rewrite.entries` = **44**; `verify_glossary.py` check 7 = **44/44 anchored, 41 shown** | **wrong** |
| "the **7** that do add wording are marked `adds`" | check 7: **3** carry added wording | **wrong** |
| "**58** wordings" capitalised | `capitalise.apply` = 58; check 6 = 58 | correct |
| "**76** authored definitions" | `authored.json` = 76 entries; check 1 reports **137 authored** | **units unstated** — 76 terms, 137 term-page instances. Both are true and the document does not say which it means |
| 166 topic pages, 281 PDFs, 25 `scripts/`, 8 `verify_*.py`, 89 SVGs | all confirmed | correct |

**Why it matters.** CLAUDE.md is the file every session reads first, and it is
mostly excellent — the hard constraints, the publishing mechanics and the
component contracts are precise and have held up under nine phases of audit.
The drift is confined to **counts**, and counts are the part a reader is least
likely to check and most likely to quote. This audit quoted "300 note diagrams"
from it in Phase 0 and only caught it in Phase 8, by measuring.

The `46` case is the instructive one: `verify_glossary.py` prints the true number
**on every run**, and it has been 44 for as long as anyone has run it. The
document and the check disagree, out loud, and nobody was listening because
nothing compares them.

**Recommendation.**

1. **Correct the six numbers.** Small edit, and CLAUDE.md is excluded from
   publishing so there is no site risk.
2. **Stop hand-maintaining counts that a script already prints.** Where CLAUDE.md
   states a number a verifier computes, cite the command instead of the value —
   *"see `verify_glossary.py` check 7"* rather than *"46 definitions"*. A number
   that cannot go stale is better than a number that is right today.
3. **State the unit for "authored".** 76 terms; 137 term-page instances because
   most appear on both board pages.

**Effort:** S · **Risk of acting:** None — a documentation edit to an excluded
file · **Risk of not acting:** Medium — the next session inherits wrong numbers ·
**Dependencies:** none · **Status:** OPEN

### PH10-062 — Nothing runs the 13-second verification suite, and three findings are already waiting on somewhere to run

**Severity:** Medium-High · **Category:** Automation · **CERTAIN** ·
**Delivers Q19/D18's approved workflow**

**Evidence.** §1: 13 checks, 13.1 seconds, all green except the one known
pre-existing `verify_liquid.py` failure. `.github/` does not exist and
`.git/hooks/` has no active hook. Every check is run by hand, when someone
remembers.

**Three open findings are blocked on exactly this:**

- **PH01-017** — `sitemap.xml` drifts because nothing re-runs `build_sitemap.py`
  after a commit.
- **PH09b-026** — `--check` validates *inputs only* on four of the five
  generators; there is nowhere for a fixed `--check` to run.
- **PH06-027** — `convert_raw_notes.py` would ship a page missing seven commits
  of SEO work, and nothing would catch it.

**Q19 is already answered** (D18): GitHub Actions is approved **for verification
only, never in the deploy path**. Pages stays on branch-serving and
`_config.yml`'s `exclude` stays the publishing gate. So P10's job is to design
the workflow, not to re-argue it.

**Recommendation — one workflow, `verify.yml`, that only reads.**

```yaml
name: verify
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 2 }        # HEAD~1 for the integrity checks
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: python3 scripts/verify_html.py
      - run: python3 scripts/verify_links.py
      - run: python3 scripts/verify_glossary.py
      - run: python3 scripts/verify_past_paper_tags.py
      - run: python3 scripts/verify_diagram_geometry.py
      - run: python3 seo/tools/verify_seo.py
      - run: node scripts/test_question_search.js
      - run: node scripts/test_glossary_filter.js
      - run: python3 scripts/strip_source_attributions.py   # must report 0
      - run: python3 scripts/build_sitemap.py --check       # closes PH01-017
      - run: python3 scripts/verify_text_integrity.py HEAD~1
      - run: python3 scripts/verify_markup_integrity.py HEAD~1 --strict
```

**Four things this design gets right, each for a stated reason:**

1. **`verify_liquid.py` is deliberately absent from the list above.** It exits **1**
   today, on a known pre-existing false positive (PH00-011). A workflow that is
   red from the first commit gets ignored within a week. Either fix PH00-011
   first and then add it — which is the right order — or add it as
   `continue-on-error: true` with a comment saying why. **Do not add it as-is.**
2. **It never builds and never deploys.** A read-only workflow cannot break the
   site; the worst outcome is a red tick. This is the whole basis of D18's
   approval and must not be widened later.
3. **`fetch-depth: 2`** is required — `verify_text_integrity.py` and
   `verify_markup_integrity.py` compare against a ref, and a shallow clone has no
   `HEAD~1`.
4. **Two checks are added that do not exist yet**, and both come from this audit:
   `build_sitemap.py --check` (PH01-017) and the published-surface assertion from
   PH10-060.

**Pre-commit hooks are not recommended.** They run on one machine, are not in git,
are silently skippable with `--no-verify`, and on a solo project add a failure
mode (a commit blocked at 11pm) without adding a guarantee. The 13 seconds belong
in CI, where the result is visible and permanent.

**Sequencing.** PH09b-025 must be fixed **first** — the `"generated": "<date>"`
stamp makes every rebuild produce a spurious diff, so an idempotence check added
before it would fail on every run and train everyone to ignore the workflow.

**Effort:** S — one file, and it is already approved · **Risk of acting:**
**Low, by construction** · **Risk of not acting:** Medium ·
**Dependencies:** PH09b-025 first; PH00-011 before adding `verify_liquid.py` ·
**Status:** OPEN

### PH10-063 — A script queues work into a report nobody opens, and known defects are logged in three places

**Severity:** Low-Medium · **Category:** Governance · **CERTAIN**

**Evidence, part one — the silent queue.**
`scripts/check_glossary_capitalisation.py` exits **0** and prints:

```
    95  Clean — capitalise the first letter
    75  Fragment — rewritten at render time
     8  Example plus the notes' own defining list — resolved
    22  Intentional — leave alone
     2  Unclassified — needs a look
```

The two unclassified entries are real and unresolved, in
`_working/glossary/capitalisation-report.md`:

| Term | Definition opens | Notes source |
| --- | --- | --- |
| Regulation | *"ban/limit the production or consumption of goods that generate negative externalities…"* | edexcel-a 1.3.2 |
| Regulation | *"bans/limits on the production of demerit goods or requiring the consumption of merit goods…"* | edexcel-a 1.4.1 |

Neither reads as a definition of *Regulation*, and **the same term is defined
twice from two different notes pages**. The script found this, wrote it to a file
under `_working/` — which is unpublished and not in anyone's path — and exited
**0**. It has been sitting there since the glossary build.

This is a **content** issue, so this audit logs it rather than fixing it: it
belongs in `REVIEW-NOTES.md`. The **governance** finding is the shape — a check
that identifies work and then exits successfully cannot cause the work to happen.

**Evidence, part two — three defect logs.** Known problems are recorded in:

| File | Lines | Last touched |
| --- | ---: | --- |
| `REVIEW-NOTES.md` | 1,596 | 2026-08-04 |
| `docs/CONTENT_ISSUES.md` | 659 | 2026-08-07 |
| `PROJECT-LOG.md` | 267 | 2026-08-04 |

`PROJECT-LOG.md` describes itself as "the single consolidated list of what is
still flagged" and CLAUDE.md says to **start there** — while being the oldest of
the three and a fifth the size of `REVIEW-NOTES.md`. P1 found this; P10 confirms
it is unchanged, and adds that the `_working/glossary/capitalisation-report.md`
queue is a **fourth** place, and this audit's `docs/audit/findings/` is a fifth.

The wider surface: **13 governance documents, ~9,100 lines**, spanning
`CLAUDE.md` (422), `QUESTIONS_PROGRESS.md` (2,949), `REVIEW-NOTES.md` (1,596),
`docs/FLASHCARDS_PROGRESS.md` (1,399), `docs/CONTENT_ISSUES.md` (659),
`PAST-PAPERS-PROGRESS.md` (483), `QUESTIONS_GUIDE.md` (403),
`_working/glossary/PROGRESS.md` (361), `extraction-qa-report.md` (307),
`PROJECT-LOG.md` (267), `NEW-CONTENT-LOG.md` (166), `docs/DIAGRAM_STYLE.md` (135),
`ROADMAP.md` (41). Plus 11 `seo/*.md` reports, 2,634 lines.

**Recommendation.**

1. **Make the unclassified queue loud.** `check_glossary_capitalisation.py` should
   exit **non-zero** when the unclassified count is above zero, so the workflow in
   PH10-062 surfaces it. Two entries today; the fix is a one-line exit code plus
   ruling on the two.
2. **Log the two `Regulation` definitions in `REVIEW-NOTES.md`** as content
   defects, per this repo's own rule that suspected content problems are logged
   for approval and never fixed unilaterally.
3. **One defect log, not three.** `REVIEW-NOTES.md` is the largest and the
   best-maintained; make it the one, have `PROJECT-LOG.md` point at it rather than
   claim to be it, and keep `docs/CONTENT_ISSUES.md` only if flashcard-specific
   issues genuinely need their own file — in which case say so in both.
4. **Decide what happens to `_audit/`.** It is gitignored by D1 and is therefore
   not in git history at all. When the audit closes, either it becomes a
   permanent unignored `docs/audit/` (and its findings become the roadmap), or it
   is deliberately discarded once P11's synthesis is written elsewhere. **Leaving
   it ignored and undiscussed is the one option that loses the work.** This is the
   only P10 recommendation with a deadline attached to it.

**Effort:** S for (1) and (2), M for (3), S for (4) ·
**Risk of acting:** None — documentation and an exit code ·
**Risk of not acting:** Low-Medium · **Dependencies:** (1) needs PH10-062 ·
**Status:** OPEN

---

## 3. What Phase 10 checked and found clean

- **Every one of the 13 checks passes**, except the known pre-existing
  `verify_liquid.py` problem (PH00-011). The suite is green.
- **All five `seo/tools/` mutators default to dry-run.** Re-running any of them
  today changes nothing without `--apply`. The correct pattern, already in place.
- **`strip_source_attributions.py` reports 0 changes**, which is the agreement
  CLAUDE.md names as its test.
- **`scripts/vendor/` is correctly documented and correctly scoped** —
  KaTeX 0.16.11, build-time only, with a written rationale for vendoring rather
  than fetching, and a note that the browser gets `css/vendor/katex/` instead.
- **No git hooks exist**, so nothing is silently modifying commits.
- **CLAUDE.md's structural claims are all accurate** — 166 topic pages, 281 PDFs,
  25 `scripts/`, 8 `verify_*.py`, 89 SVGs, 76 `authored.json` entries. Only the
  counts in PH10-061 have drifted.

---

## 4. Handed to P11

Everything in this phase is a P11 roadmap item. Two are sequencing constraints
rather than tasks:

- **PH09b-025 before PH10-062.** The build-date stamp must stop producing spurious
  diffs before any idempotence check is automated.
- **PH00-011 before adding `verify_liquid.py` to the workflow.** A workflow that is
  red from day one is a workflow nobody reads.

And one has a deadline: **PH10-063 item 4** — `_audit/` is gitignored, so unless
P11 says what becomes of it, the audit's own record is the thing most likely to be
lost.
