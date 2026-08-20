# Repository audit — economics-academy

Read-only. Nothing in the repo was modified, moved or deleted to produce this.
Date: 2026-08-20. HEAD: `63437c6` on `main`.

Every claim below is derived from a command run against this working tree. Where
I could not establish a fact, the verdict is **Investigate** and I say what would
settle it.

**Headline: the repo is in far better order than you think.** The five
"overlapping" question directories are not overlapping, `.venv` was never
committed, `.DS_Store` is handled, and 519 of 524 tracked binary assets are
referenced. What I did find is worse than clutter: **`main` is currently
publishing a page whose content will be silently reverted by the next build, and
CI is red.** That is §1.

---

## 1. Surprises — things I don't think you know

### 1.1 The last commit is unbuilt, and the next build will revert your edit

`63437c6` ("update to AQA externalities", 2026-08-20) hand-edited a **generated**
page:

```
revision-notes/aqa-a2-micro/1-8-4-positive-and-negative-externalities-in-consumption-and-production.html
```

It did not update the source slice at
`notes-data/topics/aqa-a2-micro/1-8-4-…html`, which is unchanged since
2026-08-13. I rebuilt the page in a throwaway worktree and diffed the visible
text:

| | words in `<main>` |
| --- | ---: |
| what is live now | 1,639 |
| what `build_notes_pages.py` produces | 1,782 |

The 143-word difference is a whole block you deleted, which the generator puts
straight back:

> *"Subsidising alternatives: provide financial incentives for consumers to
> choose goods or services that have positive externalities… Evaluations —
> Opportunity Cost: subsidies can be expensive for governments to fund…
> Information provision (negative advertising): educate consumers about the
> negative externalities…"*

The next time anyone runs `build_notes_pages.py` — which CLAUDE.md tells you to
do for *any nav edit* — that content returns and your edit disappears. No check
catches it, because `verify_generated.py` reports it as "generated file not
current", which reads like a stale-build warning rather than "your content edit
is about to be undone".

**Fix (not applied):** re-apply the deletion to the `notes-data` slice, re-run
`build_notes_pages.py`, then `build_sitemap.py`.

### 1.2 CI is red on `main` right now

`.github/workflows/verify.yml` runs on every push. Four of its checks fail at
HEAD. I ran all of them locally:

| Check | Result |
| --- | --- |
| `verify_generated.py` | **FAIL** — 3 files not current: the notes page above, `sitemap.xml`, `sitemaps/revision-notes.xml` |
| `verify_page_shell.py` check 9 | **FAIL** — 1 page carries a `templates/header.html` that is not the template |
| `verify_glossary.py` check 2 | **FAIL** — `glossary-data/terms.json` is stale; re-run `extract_glossary.py` |
| `build_sitemap.py --check` | **exit 1** — `WOULD CHANGE` on `sitemaps/revision-notes.xml` and `sitemap.xml` |

All four have the same root cause (§1.1). The check-9 failure is because the
commit reformatted the whole file at a different Prettier width, so the baked
header block no longer matches `templates/header.html` byte for byte.

Everything else passes: `verify_html`, `verify_links` (11,286 internal refs,
0 broken), `verify_icons`, `verify_image_dimensions`, `verify_css_load_order`,
`verify_inline_styles`, `verify_boards`, `verify_liquid`,
`verify_published_surface`, `bake_templates --apply` dry run (17 pages, 0 would
change).

### 1.3 A question paper and its mark scheme are the same file — on the live site

```
past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-june-2023-question-paper.pdf
past-papers/ocr/a-level/paper-3/ocr-a-level-economics-paper-3-june-2023-mark-scheme.pdf
```

Byte-identical: both md5 `35b8975c…`, both 545,686 bytes. They are the **only**
byte-identical pair anywhere in the tracked tree. Both are linked from
`past-papers/ocr/index.html` (lines 603 and 610) and both are in
`sitemaps/pdfs.xml`. One of those two links hands a student the wrong document.
I cannot tell you which is the correct file without the originals — that needs
you to check against OCR's own copies.

### 1.4 `marking.html` links an 8.6 MB PDF

`marking-examples/annotated-paper-example.pdf` is 8,617,128 bytes and is linked
four times from `marking.html` — your commercial page. That is a very slow
download on a phone. Correctly published and correctly in the sitemap; the issue
is purely weight.

### 1.5 Two published URLs nothing links to and nothing fetches

`/templates/header.html` and `/templates/footer.html` are served, are in **no**
sitemap, have **zero** inbound links from any of the other 463 published pages,
and are no longer fetched at runtime (Wave 2 Phase 7 baked them in). They appear
in **none** of the eight Search Console exports in `seo/gsc-exports/`, so Google
does not have them.

CLAUDE.md already says they stay published "because unpublishing them removes two
live URLs and that is a separate decision nobody has needed to make". The GSC
evidence makes that decision cheap: **the two URLs are not indexed, so
unpublishing them costs nothing.** That is new information, not a restatement.

Apart from these two, sitemap coverage is perfect: 465 published `.html`
pages, 461 in the sitemaps, and the only other omissions are `404.html` and
`confirmation.html`, both deliberately excluded as noindex. **Zero sitemap URLs
point at a file that doesn't exist.**

### 1.6 `_config.yml` documents three directories that no longer exist

The "Deliberately NOT excluded" comment block names:

- `templates/ — fetched at runtime by inject-templates.js` — **false** since
  Wave 4.10. `js/components/inject-templates.js` does not exist; `nav.js` line 3
  says it replaced it.
- `old-logos-archive/` — **directory absent**.
- `logo/` — **directory absent**. A nine-line comment agonises over whether to
  keep publishing a directory that isn't there.

None of this breaks anything — the `exclude:` list itself is correct and
`verify_published_surface.py` passes. But the file's own explanation of itself is
wrong in three places, and that file is the single thing deciding what is public.

### 1.7 CLAUDE.md's numbers have drifted — including in the section that warns about drift

CLAUDE.md contains a rule: *"Where a number in this file is one a script
computes, cite the script, not the value."* Measured against the tree:

| CLAUDE.md says | Actually |
| --- | --- |
| "the 112 PNGs in `images/diagrams/`" | **106** |
| "(+83 SVGs in `svg/`)" | **84** |
| "`DECISIONS.md` is append-only, **D1–D39**" | **D1–D50** |
| "In progress on `feature/question-bank`" | branch **absent**; feature is live |
| "In progress on `feature/glossary`" | branch **absent**; feature is live |
| "In progress on `flashcards-feature`" | branch **absent**; feature is live |

The page counts it cites *are* right: `verify_page_shell.py` prints "463
published pages, 17 of them hand-written", and `past-papers/` does hold 281 PDFs.

### 1.8 Two files both claim to be the one you read first

- CLAUDE.md § See also: "`PROJECT-LOG.md` — **Start here.**" (last touched
  2026-08-04, 2 commits)
- `PROGRESS.md` line 3: "A fresh session should read this first, then CLAUDE.md."
  (last touched 2026-08-16, 28 commits)

**CLAUDE.md never mentions root `PROGRESS.md` at all.** Every "PROGRESS.md" match
in CLAUDE.md is `_working/glossary/PROGRESS.md`, `docs/audit/PROGRESS.md` or
`PAST-PAPERS-PROGRESS.md`. The newer, more active file is invisible to a fresh
session; the older one is flagged as the entry point. Same for `OWNER-TODO.md`
(18 commits, touched today) and `NEW-CONTENT-LOG.md` — neither appears in
CLAUDE.md.

### 1.9 68 Finder duplicate files sit in the working tree

All gitignored by the `* [0-9].*` rule, so **none is published and none is
tracked** — this is local disk clutter only. But 64 of them are inside
`past-paper-questions/`, which *is* a published directory. The ignore rule is the
only thing keeping them off the site.

```
scripts/{bake_templates,build_notes_pages,extract_notes_pages,page_shell} 2.py
js/components/nav 2.js
boards-data/boards 2.json          (differs from boards.json — not a stale copy of it)
docs/audit/scripts/harness/{measure_preconnect,render_nav} 2.py
past-paper-questions/**/questions 2.json   × 64
```

### 1.10 Four merged branches, and 23 MB of ignored Lighthouse output

`breadcrumb-standardisation`, `home-page-revamp`, `tutoring-seo-rework` and
`wave5-1-diagram-review` are all **0 commits ahead of main** — fully merged, safe
to delete whenever you like. `seo/lh-live-after/` is 23 MB on disk, correctly
gitignored and regenerable.

---

## 2. Publication status — every tracked file

Derived by applying `_config.yml`'s `exclude:` list plus Jekyll's underscore/dot
rule to `git ls-files`. The published total, **1,099**, is independently
confirmed by `scripts/verify_published_surface.py`.

| Top level | Published | Excluded from build |
| --- | ---: | ---: |
| `(root files)` | 19 | 16 |
| `.github/` | 0 | 1 |
| `_working/` | 0 | 80 |
| `boards-data/` | 0 | 1 |
| `css/` | 44 | 0 |
| `docs/` | 0 | 45 |
| `flashcards/` | 13 | 0 |
| `flashcards-data/` | 0 | 6 |
| `glossary-data/` | 0 | 3 |
| `images/` | 195 | 0 |
| `js/` | 6 | 0 |
| `marking-examples/` | 2 | 0 |
| `notes-data/` | 0 | 346 |
| `past-paper-questions/` | 172 | 0 |
| `past-paper-questions-data/` | 0 | 66 |
| `past-papers/` | 286 | 0 |
| `practice-questions/` | 173 | 0 |
| `questions-data/` | 0 | 166 |
| `raw-notes/` | 0 | 75 |
| `revision-notes/` | 179 | 0 |
| `scripts/` | 0 | 44 |
| `seo/` | 0 | 42 |
| `sitemaps/` | 7 | 0 |
| `templates/` | 2 | 0 |
| `webfonts/` | 1 | 0 |
| **Total** | **1,099** | **891** |

Category (c), ignored by git entirely: `.venv/` (1,965 files, 64 MB),
`__pycache__/`, `.DS_Store` (12 on disk), `seo/lh-*/` (23 MB), the 68 Finder
duplicates, `.claude/settings.local.json`, and the generated QA artefacts under
`_working/flashcards/qa/` and `_working/diagram-review/` (two nested
`.gitignore` files).

---

## 3. Root-level files

| File | Published? | Last commit | Commits | Referenced by | Verdict |
| --- | --- | --- | ---: | --- | --- |
| `CLAUDE.md` | excluded | 2026-08-13 | 31 | loaded every session | **Keep** — rewrite in Phase 3 |
| `_config.yml` | excluded | 2026-08-14 | 9 | decides the whole published surface | **Keep** — correct §1.6 comments |
| `CNAME` | published | 2025-06-15 | 1 | GitHub Pages reads it | **Keep** |
| `README.md` | excluded | 2025-06-15 | 1 | nothing (the two `scripts/*.py` hits are `scripts/vendor/README.md`) | **Keep** — 19 bytes, it's the GitHub repo front page. Worth *expanding*, not deleting |
| `README.txt` | excluded | 2025-06-15 | 1 | nothing but `docs/` prose | **Archive** — it is the HTML5 UP "Dopetrope" template readme, crediting AJ at lkn.io and Janine Pring's demo images. Nothing to do with your site. *Caveat:* it also carries the CCA 3.0 attribution for the template the CSS descends from. Keeping it in `_archive/` preserves the attribution while getting it out of root |
| `LICENSE.txt` | **published** | 2025-06-15 | 1 | zero references in any served file | **Investigate** — it is served at `/LICENSE.txt`. Whether that's wanted is a licensing question I can't answer for you |
| `robots.txt` | published | 2026-05-12 | 1 | points at `/sitemap.xml` | **Keep** |
| `sitemap.xml` | published | 2026-08-16 | 72 | `robots.txt` | **Keep** — currently stale, see §1.2 |
| `site.webmanifest` | published | 2026-04-28 | 1 | 463 pages | **Keep** |
| `favicon.ico`, `apple-touch-icon.png`, `android-chrome-{192,512}.png` | published | 2026-05-16 | 2 | 463 pages via the favicon set | **Keep** |
| `og-image.png` | published | 2026-05-16 | 2 | 459 served files | **Keep** |
| `404.html`, `confirmation.html` | published | 2026-08-13/16 | 9 / 13 | deliberately not in sitemap, noindex | **Keep** |
| `index`, `about`, `contact`, `faq`, `marking`, `privacy`, `tutoring` `.html` | published | 2026-08-14/16 | 12–39 | the site | **Keep** |
| `requirements.txt` | excluded | 2026-08-02 | 1 | `extract_aqa_questions.py` only | **Keep** — one pinned package for one script, documented in the file itself |

### Root tracking / log markdown

"Alive" here means: something instructs a future session to read or update it.

| File | Size | Last commit | Commits | Told to read it by | Verdict |
| --- | ---: | --- | ---: | --- | --- |
| `OWNER-TODO.md` | 7 KB | **2026-08-20** | 18 | `PROGRESS.md` only — **not CLAUDE.md** | **Keep** — your live task list, touched today. Must be named in the new CLAUDE.md |
| `PROGRESS.md` | 14 KB | 2026-08-16 | 28 | nothing — **not CLAUDE.md** | **Keep** — most active tracking file in the repo and currently invisible to a fresh session. Its "Traps every future session must know" list is exactly what CLAUDE.md should point at |
| `REVIEW-NOTES.md` | 92 KB | 2026-08-12 | 45 | CLAUDE.md ("log new ones there rather than fixing them"), `check_glossary_capitalisation.py`, `verify_liquid.py` | **Keep, but split** — 47 `##` sections, 1,749 lines. The open economics content errors (`N-Q2`…`N-Q20`, `G4`) are load-bearing. The finished audit trail — "What changed, commit by commit", "Verification so far", "Results", "Outcome against the brief", "Regressions caught during verification", plus the `— FIXED` sections — measures **~496 lines, 28%**. That is a heuristic line-count, not an exact figure |
| `QUESTIONS_PROGRESS.md` | 159 KB | 2026-08-01 | 37 | CLAUDE.md ("Historical, but read §8 and §9"), `extract_past_paper_questions.swift` | **Keep, but split** — lines 655–2949 are the "Batch record" and seven per-theme completion logs: **78% of the file is a finished record**. Lines 1–654 hold "Recurring problems", "Ratified content decisions", "Board fidelity", "Remaining work" and "Open items" — that part earns its place |
| `PAST-PAPERS-PROGRESS.md` | 33 KB | 2026-08-07 | 12 | CLAUDE.md ("Read first") for the question bank | **Keep** — the bank is live; this is its state file |
| `QUESTIONS_GUIDE.md` | 20 KB | 2026-08-01 | 7 | CLAUDE.md, and `build_questions.py` | **Keep** — it is the authoring standard, cited by the generator |
| `PROJECT-LOG.md` | 13 KB | 2026-08-04 | 2 | CLAUDE.md, marked "**Start here.**" | **Investigate** — it is billed as the entry point but has 2 commits and is 16 days stale, while `PROGRESS.md` (28 commits) does the same job better. Either it is demoted or `PROGRESS.md` is merged into it; that's your call, not mine |
| `NEW-CONTENT-LOG.md` | 11 KB | 2026-08-01 | 8 | nothing but `PROJECT-LOG.md` and `REVIEW-NOTES.md` prose | **Archive** — a per-batch review log for the `notes-consistency-pass` branch, which is merged and gone. Its purpose was "so it can be reviewed in situ"; that review happened |
| `extraction-qa-report.md` | 34 KB | 2026-08-02 | 2 | CLAUDE.md ("Phase 1 extraction QA for that bank") | **Archive** — a completed one-off QA report for an extraction that shipped. Keep the pointer in CLAUDE.md aimed at the archived path |
| `ROADMAP.md` | 2 KB | 2026-08-04 | 4 | CLAUDE.md, and a comment in `build_glossary.py` | **Investigate** — only 41 lines, but I cannot tell from the file which items are still wanted. Read it and tell me; it may fold into `OWNER-TODO.md` |

**Pushing back on your premise:** you listed these as "suspect". Six of the ten
are actively maintained and two are cited by scripts. The real problem is not
that they exist, it is that **the two most active ones (`PROGRESS.md`,
`OWNER-TODO.md`) are not in CLAUDE.md and the least active one
(`PROJECT-LOG.md`) is flagged "Start here"**. That is a pointer problem, not a
file problem. Only `NEW-CONTENT-LOG.md`, `extraction-qa-report.md` and
`README.txt` are genuinely dead weight — 56 KB of 388 KB.

---

## 4. Directories

| Directory | Status | Last commit | Commits | Evidence of use | Verdict |
| --- | --- | --- | ---: | --- | --- |
| `revision-notes/` | published | 2026-08-20 | 248 | the site's core; 179 files | **Keep** |
| `past-papers/` | published | 2026-08-15 | 41 | 281 PDFs + 5 hubs, 283 sitemap entries | **Keep** |
| `practice-questions/` | published | 2026-08-15 | 52 | 173 pages, all in sitemap | **Keep** — generated |
| `past-paper-questions/` | published | 2026-08-13 | 20 | 90 sitemap entries; `questions.json` fetched by `question-search.js` | **Keep** — generated |
| `flashcards/` | published | 2026-08-15 | 42 | 7 sitemap entries; `data/*.json` fetched at runtime | **Keep** — generated |
| `css/` | published | 2026-08-16 | 107 | 44 files, **0 unreferenced** | **Keep** |
| `js/` | published | 2026-08-14 | 45 | 6 files, **0 unreferenced**; `main.js` on 463 pages, `nav.js` on 465 | **Keep** |
| `images/` | published | 2026-08-16 | 54 | 195 files, 5 unreferenced (§7) | **Keep** |
| `webfonts/` | published | 2026-08-10 | 3 | 1 file, referenced by `css/fontawesome-all.min.css`; `verify_icons.py` passes | **Keep** — do not touch without re-running `subset_fontawesome.py` |
| `marking-examples/` | published | 2026-08-16 | 2 | 4 links in `marking.html`, 2 sitemap entries | **Keep** — but see §1.4 on size |
| `sitemaps/` | published | 2026-08-16 | 38 | `sitemap.xml` index | **Keep** — generated |
| `templates/` | published | 2026-08-09 | 16 | source of truth for the baked header/footer; **zero runtime fetches** | **Keep the files, Investigate the publishing** — §1.5 shows unpublishing is now free |
| `notes-data/` | excluded | 2026-08-15 | 17 | source for 173 generated notes pages | **Keep** — canonical |
| `questions-data/` | excluded | 2026-08-01 | 36 | source for 173 practice pages | **Keep** — canonical |
| `past-paper-questions-data/` | excluded | 2026-08-08 | 11 | source for the bank | **Keep** — canonical |
| `glossary-data/` | excluded | 2026-08-09 | 15 | source for 3 glossary pages | **Keep** — canonical (currently stale, §1.2) |
| `flashcards-data/` | excluded | 2026-08-07 | 30 | source for 6 decks | **Keep** — canonical |
| `boards-data/` | excluded | 2026-08-12 | 2 | 1 file, read by 5 generators via `board_data.py`; `verify_boards.py` passes | **Keep** |
| `scripts/` | excluded | 2026-08-16 | 121 | 21 of them run in CI | **Keep** |
| `seo/` | excluded | 2026-08-11 | 36 | **`seo/tools/verify_seo.py` runs in CI** | **Keep** — see note below |
| `docs/` | excluded | 2026-08-15 | 112 | 45 files; `docs/audit/` cited throughout CLAUDE.md | **Keep** |
| `_working/` | excluded (underscore) | 2026-08-14 | 49 | holds the full Font Awesome source and the glossary state file | **Keep** — see note below |
| `raw-notes/` | excluded | 2026-08-09 | 4 | nothing reads it; no generator input | **Archive** — evidence in §6 |
| `.venv/` | **not in git** | — | 0 | — | **Keep on disk, no repo action** — §8 |
| `.github/` | excluded | 2026-08-13 | 11 | the CI workflow | **Keep** |

**`seo/` — correcting a likely instinct.** At 25 MB on disk it looks like the
obvious cut. 23 MB of that is `seo/lh-live-after/`, which is **already
gitignored** and regenerable. Only 42 files are tracked, and one of them,
`seo/tools/verify_seo.py`, is a CI step (`.github/workflows/verify.yml` line
124). Deleting `seo/` breaks the build. The `gsc-exports/` CSVs are also the only
record of what Google has actually indexed — that is what made §1.5 answerable.

**`_working/` — 8.4 MB of it is flashcard QA screenshots**, of which only 20 are
tracked; the rest are covered by two nested `.gitignore` files. It also holds
`_working/fontawesome/fa-solid-900.woff2`, the **full font** that
`subset_fontawesome.py` subsets from. Losing that means you cannot add an icon
again. Not a candidate for removal.

---

## 5. The five "overlapping" question directories — your premise is wrong

You suspected real overlap between `past-paper-questions/`,
`past-paper-questions-data/`, `past-papers/`, `practice-questions/` and
`questions-data/`. There is none. They are two independent banks plus a PDF
archive, each bank split source/output exactly as CLAUDE.md describes:

```
BANK A — original questions you wrote (must be 100% your IP)
  questions-data/**.json            166 files   source, hand-authored, EXCLUDED
        │ build_questions.py
        ▼
  practice-questions/**.html        173 files   output, PUBLISHED

BANK B — real exam questions, reproduced verbatim
  past-paper-questions-data/**.json  66 files   source, machine-extracted, EXCLUDED
        │ build_past_paper_questions.py
        ▼
  past-paper-questions/**           172 files   output, PUBLISHED

ARCHIVE — the PDFs both banks deep-link into
  past-papers/**.pdf               281 PDFs + 5 hubs, PUBLISHED
```

**Measured overlap between the two banks' question text:**

| | |
| --- | ---: |
| Distinct question stems in `past-paper-questions-data/` | 552 |
| Distinct question stems in `questions-data/` | 1,267 |
| **Exact matches between them** | **0** |
| **Best near-duplicate ratio** (200 practice questions vs all 552, difflib) | **0.000** |

Not one practice question resembles a real exam question. Your "never share a
data path" rule is holding, and it is the single most commercially important
invariant in this repo — the practice bank is what you sell.

The only thing genuinely wrong here is the **naming**: `questions-data/` is the
source for `practice-questions/`, not for `past-paper-questions/`, and nothing in
the name says so. That is a rename candidate for Phase 2 — and it is a
zero-risk one, because `questions-data/` is excluded from the build.

---

## 6. `notes-data/` vs `raw-notes/` vs `revision-notes/`

Also not duplication — a source, an output, and a genuinely dead ancestor.

- **`notes-data/`** (346 files, excluded) — canonical. A verbatim byte slice of
  each page's content plus lifted metadata JSON.
- **`revision-notes/`** (179 files, published) — generated from it by
  `build_notes_pages.py`. Verified: a clean rebuild reproduces 165 of 166 topic
  pages byte-for-byte. The one exception is §1.1.
- **`raw-notes/`** (75 files, excluded) — historical drafts. I measured drift
  independently rather than trusting CLAUDE.md's claim:

| | |
| --- | ---: |
| Markdown files in `raw-notes/edexcel/` | 73 |
| Matched to a live page | 73 |
| **Still in sync (word overlap ≥ 0.999)** | **0** |
| Median word overlap with the live page | 0.63 |
| Worst (`4.1.3 pattern-of-trade`) | 0.40 |

CLAUDE.md's "0 of 73, worst case 38% word overlap" is confirmed (my metric gives
40% for the same file — same conclusion). Nothing reads `raw-notes/`; the script
that consumed it, `convert_raw_notes.py`, was deleted on 2026-08-13 under D44.

**Verdict: Archive.** It is a historical draft set with a documented decision
behind it. It costs 368 KB and it is the one directory in the repo a future
session could mistake for a build input.

---

## 7. Orphaned assets

Checked by basename against every **served** file (`.html`, `.css`, `.js`,
`.xml`, `.webmanifest`, `.json`), which is what catches the flashcard decks and
the past-paper payloads that reference images from JSON.

**`webfonts/` — 0 orphans.** `fa-solid-900.woff2` is referenced from
`css/fontawesome-all.min.css`, and `verify_icons.py` passes ("15 icon rules, 13
classes used across 6 files"). I checked `@font-face` and preload paths as you
asked. Do not touch this file: it is a **subset**, and a subset font renders a
missing glyph as nothing at all, silently.

**`images/` — 5 of 195 unreferenced:**

| File | Status | Verdict |
| --- | --- | --- |
| `images/diagrams/game-theory.png` | `docs/CONTENT_ISSUES.md` #9 records it as **known-incorrect**; replaced by `svg/game-theory.svg` on 2026-08-05 with your approval | **Archive** — and it is explicitly flagged "do not use as ground truth" |
| `images/diagrams/comparative-advantage.png` | Same pattern; replaced by the redrawn SVG. `CONTENT_ISSUES.md` #25 said two other pages still used it — my scan shows **that is now fixed too** | **Archive** |
| `images/diagrams/trade-union-competitive.png` | Named only in `docs/audit/findings/PH01-structure.md` as one of "10 of 112 diagram PNGs" that name real content the notes never show | **Investigate** — this is a *missing page* signal, not dead weight. Deleting it hides a content gap |
| `images/diagrams/trade-union-monopsony.png` | as above | **Investigate** — as above |
| `images/diagrams/svg/price-discrimination-combined-market.svg` | Hand-authored SVG discussed in `PH08-047b-missing-diagrams.md` and `DECISIONS.md`; never wired into a page | **Investigate** — likely finished work that was never shipped |

The other 79 SVGs I initially flagged are **not** orphans: they are referenced
from `flashcards/data/*.json` and pulled in at runtime by `flashcards.js`. My
first pass missed them by excluding `.json` from the corpus. Correcting that took
`images/` from an apparent 82 orphans to a real 5.

**Nothing in `css/`, `js/`, `marking-examples/` or `templates/` is unreferenced.**

---

## 8. `.venv/`, `.DS_Store` and the Finder duplicates

**`.venv/` — your suspicion is wrong, and the news is good.**

```
git ls-files .venv          → 0 files
git log --all -- .venv      → 0 commits
```

It has **never** been committed, not in a single commit across the repo's whole
history. It is 64 MB and 1,965 files on your disk and costs the repository
nothing. `.gitignore` line 14 covers it, and `requirements.txt` documents the
venv workflow. **No action.**

**`.DS_Store` — gitignored now, but they are in history.**

- On disk: 12, all ignored.
- Currently tracked: **0**.
- In history: **10 commits** touched `.DS_Store` files, the earliest in "3rd Sept
  Changes" and the latest in "bug fixes", which added ten of them at once.

They were removed from tracking at some point and the ignore rule holds. The only
cost now is a handful of small blobs in the pack — negligible against a 168 MB
pack that is overwhelmingly the 281 exam PDFs. **No action; removing them from
history is not worth a rewrite.**

**Finder duplicates:** 68 files, all ignored, none tracked, none published. See
§1.9. **Delete-on-disk candidates** — but that is an `rm` outside git, so it needs
your explicit go-ahead and it belongs in Phase 2.

---

## 9. Generated vs hand-authored

Rebuilding from source is safe for everything in the right-hand column; editing
it by hand is not.

| Generator | Writes | Hand-editing it means |
| --- | --- | --- |
| `build_notes_pages.py` | `revision-notes/` 173 pages | your edit is reverted on next run — §1.1 |
| `build_questions.py` | `practice-questions/` 173 pages | reverted |
| `build_past_paper_questions.py` | `past-paper-questions/` + `questions.json` × N | reverted |
| `build_glossary.py` | `revision-notes/glossary/**` 3 pages | reverted |
| `build_flashcards.py` | `flashcards/**` + `flashcards/data/*.json` | reverted |
| `build_sitemap.py` | `sitemap.xml`, `sitemaps/*.xml` | reverted |
| `bake_templates.py` | the header/footer block in the 17 hand-written pages | reverted |
| `extract_glossary.py` | `glossary-data/terms.json` | reverted |
| `build_past_paper_taxonomy.py` | `past-paper-questions-data/taxonomy.json` | reverted |
| `subset_fontawesome.py` | `css/fontawesome-all.min.css`, `webfonts/fa-solid-900.woff2` | icons silently vanish |
| `reencode_diagrams.py` | `images/diagrams/*.png` | — |

Hand-authored source, never generated: `notes-data/`, `questions-data/`,
`glossary-data/{curation,authored}.json`, `flashcards-data/`,
`past-paper-questions-data/tags.json`, `boards-data/boards.json`,
`templates/`, `css/`, `js/`, the 17 non-generated pages, `past-papers/` PDFs.

Machine-extracted but never hand-edited: `past-paper-questions-data/*/*.json`
(Swift + PDFKit), `glossary-data/terms.json`.

---

## 10. Every verdict, in one list

**Keep (no action):** `revision-notes/`, `past-papers/`, `practice-questions/`,
`past-paper-questions/`, `flashcards/`, `css/`, `js/`, `webfonts/`,
`marking-examples/`, `sitemaps/`, all six `*-data/` directories, `scripts/`,
`seo/`, `docs/`, `_working/`, `.github/`, `.venv/`, every root `.html`, `CNAME`,
`robots.txt`, `site.webmanifest`, the favicon set, `og-image.png`,
`requirements.txt`, `README.md`, `_config.yml`, `CLAUDE.md`, `OWNER-TODO.md`,
`PROGRESS.md`, `PAST-PAPERS-PROGRESS.md`, `QUESTIONS_GUIDE.md`.

**Keep but split (live core + finished record):** `REVIEW-NOTES.md` (~28%
archivable, measured), `QUESTIONS_PROGRESS.md` (~78% archivable, measured).

**Archive:** `raw-notes/` (§6), `NEW-CONTENT-LOG.md`, `extraction-qa-report.md`,
`README.txt` (preserving the CCA 3.0 attribution),
`images/diagrams/game-theory.png`, `images/diagrams/comparative-advantage.png`.

**Delete (on disk only — never tracked, never published):** the 68 Finder
duplicate files listed in §1.9. Evidence: `git ls-files` returns none of them;
`git check-ignore -v` attributes each to `.gitignore`'s `* [0-9].*` rule; they
appear in no sitemap and no served file.

**Investigate — I could not establish these and will not guess:**

| Item | What would settle it |
| --- | --- |
| Which OCR June-2023 Paper 3 PDF is correct | Compare both against OCR's originals. I cannot tell from bytes alone |
| `LICENSE.txt` served at `/LICENSE.txt` | Your call on whether the site should publish a licence file |
| Unpublishing `templates/` | Now cheap (§1.5), but it removes two live URLs. Your decision |
| `PROJECT-LOG.md` vs `PROGRESS.md` as the entry point | Read both; one should absorb the other |
| `ROADMAP.md` | 41 lines. Tell me which items are still wanted |
| `trade-union-{competitive,monopsony}.png` | These flag *missing notes pages*. Do you intend to write them? |
| `svg/price-discrimination-combined-market.svg` | Finished diagram, never wired in. Was that deliberate? |
| The four merged branches | Fully merged, safe to delete — but deleting branches is yours to authorise |

---

## 11. Method, and what I did not check

Run against HEAD `63437c6` with a clean tree (one untracked file:
`_working/repo-cleanup-audit-prompt.md`).

- Publication status: `_config.yml` `exclude:` + Jekyll's underscore/dot rule
  applied to `git ls-files`; cross-checked against
  `scripts/verify_published_surface.py` (both give 1,099).
- Reference counts: `grep -l` over the tracked corpus, split into "served files"
  and "all tracked" so a mention in `docs/` never counts as use.
- Liveness: `git log -1 --format=%ad` and `git log --oneline | wc -l` per path.
- Duplication: `git ls-files -s` hash grouping for byte-identity; `difflib`
  token comparison for near-duplicates.
- Generation: every generator re-run in a throwaway `git worktree`, output
  diffed against the committed tree, then the worktree removed.

**Not checked:** whether any page's *economics* is correct; whether external
links resolve (1,021 skipped by `verify_links.py`); anything about the live
server beyond what `seo/gsc-exports/` records; the contents of the 281 PDFs.

---

Phase 2 (restructure plan) and Phase 3 (CLAUDE.md rewrite) not started — waiting
on your response to this.
