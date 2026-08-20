# _archive

Finished records, kept because they explain how something came to be the way it
is — not because anything still reads them.

**Excluded from the published site by Jekyll's underscore rule**, the same
mechanism that keeps `_working/` off the site. It needs no `_config.yml` entry to
be safe, but it is listed there anyway so the intent survives.

**Tracked in git, deliberately.** Gitignoring this directory would take these
files out of version control entirely, leaving one copy on one disk. Everything
here arrived by `git mv`, so its full history came with it.

| File | What it is | Retired |
| --- | --- | --- |
| `NEW-CONTENT-LOG.md` | Per-component inventory of the 31 teaching components added by the notes enrichment pass, written so they could be reviewed in situ. That review happened; the branch is merged and deleted. | 2026-08-20 |
| `extraction-qa-report.md` | Phase 1 QA for the Edexcel past-paper extraction. The extraction shipped. | 2026-08-20 |
| `README.txt` | The readme of "Dopetrope" by HTML5 UP, the template this site's CSS originally descended from. **Kept, not deleted, for its CCA 3.0 attribution** — that licence asks for credit, and this is where the credit lives. Nothing else in it applies to this site. | 2026-08-20 |
| `PROJECT-LOG.md` | Superseded by `PROGRESS.md`, which absorbed everything in it that was still true on 2026-08-20. Most of its "what remains flagged" list had been fixed without the file being updated. | 2026-08-20 |
| `ROADMAP.md` | Folded into `OWNER-TODO.md`. Its two "Now" items had both shipped. | 2026-08-20 |
| `raw-notes/` | 75 markdown drafts the Edexcel notes were originally written from. **0 of 73 are still in sync with their live page** (median word overlap 0.63, worst 0.40, re-measured 2026-08-20). The script that consumed them, `convert_raw_notes.py`, was deleted on 2026-08-13 under D44. Historical only — never a build input. | 2026-08-20 |

## `working/`

Finished working material moved out of `_working/` on 2026-08-20, once the work
it belonged to was live. Reference, not input — nothing reads any of it.

| Path | What it is |
| --- | --- |
| `working/flashcards-qa/` | 61 files: QA screenshots, measurement JSON and the scripts that produced them, from the flashcard build. The decisions they informed are in `docs/FLASHCARDS_PROGRESS.md`. |
| `working/glossary/` | Four hand-written decision and gap reports from the glossary build. **Three others were moved here by mistake on 2026-08-20 and moved straight back**: `inventory.md`, `review-decisions.md` and `capitalisation-report.md` are written by `extract_glossary.py` and `check_glossary_capitalisation.py` on every run, so they belong in `_working/glossary/` alongside `PROGRESS.md` and `authored-review.md`. |
| `working/diagram-review/` | The review tooling for the diagram pass. |
| `working/question-bank/` | The Edexcel AS extraction QA and a dry-run log. |
| `audit-2026-08-20/` | The repo audit, the restructure plan and the CLAUDE.md migration mapping. Dated records of the tree as it stood that day; paths inside them are **not** rewritten when files move later. |

**What deliberately stayed in `_working/`:**

- `_working/fontawesome/fa-solid-900.woff2` — the **full** Font Awesome font that
  `scripts/subset_fontawesome.py` trims to the 15 icons the site uses. Load-bearing:
  without it no new icon can ever be added.
- `_working/glossary/PROGRESS.md` and `authored-review.md` — still cited by
  `glossary-data/CLAUDE.md` and several docs.
