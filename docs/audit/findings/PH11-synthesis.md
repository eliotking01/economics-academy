# Phase 11 — synthesis

Branch `audit/organisation-audit`, working tree at `41aa96d`. Compiled
2026-08-09. **The audit is complete: 11 phases, 63 findings, 26 questions asked
and answered, 0 site files changed except the four Eliot authorised.**

This document is the deliverable. `PROGRESS.md` says where things stand;
`DO-NOT-BREAK.md` says what must not be undone; the ten `findings/` files hold
the evidence. **This one says what to do, in what order, and what to do if it
goes wrong.**

---

## 1. The audit in one page

### What was found, in one sentence each

**The site is in far better shape than the brief anticipated.** Technical SEO is
clean and has stayed clean: 0 duplicate titles, 0 duplicate descriptions, 0
canonical mismatches, 0 broken internal links, 0 broken fragments across 4,979 of
them, a sitemap that matches the filesystem exactly, and 921 JSON-LD blocks that
all parse. Hub-and-spoke integrity is **perfect** — 332 spokes, 0 missing links
in either direction. The practice-question markup is fully compliant with
Google's practice-problems requirements across 1,267 questions with 0 omissions.
Heading hierarchy is correct sitewide and every one of 309 images has alt text.

**The problems are structural, and they have one shape.** Nine of the ten phases
independently found the same pattern: **a convention is adopted, and only the
pages behind a generator receive it.**

| Convention | Has it | Does not |
| --- | --- | --- |
| Breadcrumb `aria-label` | 100 generated pages | 341 |
| CSS wrapper scoping | 5 generated sheets (+`privacy.css`) | 13 hand-written sheets |
| `size-adjust` fallback font metrics | `quiz.css`, 173 pages | 290 |
| `decoding` on images | 2 diagram galleries, 89 images | 220 |
| `<noscript>` fallback | 15 generated pages | 448 |
| `EducationalOrganization` | 354 pages | 109 |
| One MathJax configuration | — | 3 configs, 2 script tags, 126 pages |
| `inLanguage: en-GB` | 274 nodes | 179 say `en` |

**That is the case for D18's build step, restated eight times by eight
independent measurements.** It is not a style preference; it is the mechanism by
which this site drifts.

### The four things that are actually costing something today

1. **CLS is not 0.000, and the report says it is.** past-paper-questions **0.253**,
   notes-topic **0.110**, against Google's 0.1 threshold — measured by the SEO
   work's own 7-run files and contradicted by its own prose. PH08-035.
2. **The notes pages weigh 911 KB because 112 line diagrams are stored as
   2,350 px RGBA PNGs.** Mean 513 KB of images per page. PH08-034.
3. **Edexcel A is named six different ways in text students read**, and only 10
   pages of 463 ever write "Edexcel A" — on a site that publishes past papers for
   four boards. PH07-056.
4. **Nothing runs the 13-second verification suite.** PH10-062.

### The three things that would have bitten someone eventually

- **`convert_raw_notes.py`** ships a page missing seven SEO commits, from a
  documented command, with 73 markdown sources waiting. PH06-027.
- **A 429-line markdown source file is live on the site** and invisible to every
  tool in the repo, because they all glob `*.html`. PH10-060.
- **The 78 SVG diagram "twins" are not all the same diagram** — at least one drops
  an entire panel of economics content. PH08-047, caught only because standing
  rule 4 required looking before swapping.

---

## 2. The roadmap

Ordered by **what unblocks what**, then by impact ÷ (effort × risk). Every item
cites its finding. Nothing here changes a URL except the two items in §4, which
carry rollback plans.

### Wave 0 — Free wins. Nine single-file edits, no dependencies, do them first

Each is one file, none touches prose, none changes a URL, and none is affected by
anything later in the roadmap. Together: about an hour.

| # | Change | File | Finding |
| --- | --- | --- | --- |
| 0.1 | `min-height` on `.ppq-controls` — closes a **0.253 CLS** on 90 pages | `css/pages/past-paper-questions.css` | PH08-035 |
| 0.2 | `font-display: swap` on FontAwesome's 3 `@font-face` rules — removes a 3 s FOIT sitewide | `css/fontawesome-all.min.css` | PH08-033 |
| 0.3 | `, sans-serif` after `"Source Sans Pro"` | `css/main.css:249` | PH08-041 |
| 0.4 | Focus ring on the 3 colour-only `outline: none` rules | `faq.css`, `contact.css`, `past-paper-questions.css` | PH08-040 |
| 0.5 | `<h1>` → `<p>` in the header template — every page currently renders two `<h1>` | `templates/header.html:4` | PH08-036 |
| 0.6 | `<section id="header\|footer">` → `<header>`/`<footer>`; move the 11 inline styles out | both templates | PH08-037 |
| 0.7 | Promote Flashcards to a top-level nav item, matching its root URL | `templates/header.html` | PH07-057 |
| 0.8 | Correct the six drifted counts; cite commands, not values | `CLAUDE.md` | PH10-061 |
| 0.9 | Log the two `Regulation` definitions as content defects | `REVIEW-NOTES.md` | PH10-063 |

**0.1 is the single highest value-per-line change in the whole audit.**

**Verify Wave 0 with:** `verify_html.py`, `verify_links.py`,
`verify_markup_integrity.py HEAD --strict`, and by opening one page per family in
Live Server. 0.5 and 0.6 touch the templates, so they reach all 463 pages — check
`css/main.css` for `#header h1`, `section#header` and `section#footer` selectors
**before** editing, not after.

### Wave 1 — The automation spine. Do this second; everything after is protected by it

Strict order — each step's failure mode is created by skipping the one before.

| # | Change | Finding | Why this order |
| --- | --- | --- | --- |
| 1.1 | Remove the `"generated": "<date>"` stamp from the 6 flashcard payloads and `questions.json` | PH09b-025 | Until this goes, every rebuild produces a spurious diff, so any idempotence check cries wolf on every run |
| 1.2 | Fix PH00-011 so `verify_liquid.py` exits 0 | PH00-011 | A workflow that is red from its first run gets ignored within a week |
| 1.3 | Make `--check` compare against committed output on the four generators that do not | PH09b-026 | Only `build_sitemap.py:252` does a real comparison today |
| 1.4 | Add `.github/workflows/verify.yml` — read-only, 13 checks, ~13 s | PH10-062 | Closes PH01-017; gives 1.3 somewhere to run |
| 1.5 | Add the published-surface assertion: every tracked file under a published directory is `.html`, a known asset type, or excluded | PH10-060 | Closes the class, not just the instance |
| 1.6 | Make `check_glossary_capitalisation.py` exit non-zero while anything is unclassified | PH10-063 | A check that queues work and exits 0 cannot cause the work to happen |

**The workflow is already approved** — D18/Q19, verification only, never in the
deploy path, Pages stays on branch-serving. It is drafted in full in
`PH10-tooling.md`. **Do not widen it to build or deploy**; that is the entire
basis of the approval.

### Wave 2 — The build step. D18, approved as put on 2026-08-09

`scripts/page_shell.py`, stdlib-only, imported by all five generators, output
committed exactly as the 273 generated pages already are. The seven-phase
migration plan and its ten-assertion harness are in `PH06-html-architecture.md`
§3. **Nothing here changes a URL, by construction.**

Migration is byte-identical by design. **These land as separate commits after
each family migrates clean** — never during, because a harness failure must be
unambiguous:

| Change | Pages | Finding |
| --- | ---: | --- |
| `aria-label="Breadcrumb"` | 341 | PH06-030 |
| `<section id="main">` → `<main id="main">` (keep the `id` — the skip link depends on it) | 462 | PH06-032 |
| `id="MathJax-script"` normalised, and **`["$","$"]` removed from `inlineMath`** | 126 | PH08-039 |
| `loading="lazy"` | 33 pages / 94 images | PH08-034 |
| The 3 real `<style>` blocks → `css/pages/` (**not** the 6 `<noscript>` ones) | 3 | PH08-042 |
| 333 authored inline `style=` → classes across 45 files (**never** the 1,187 KaTeX ones) | 45 | PH08-042 |
| Visible breadcrumb trail on the 19 pages that declare one in JSON-LD only | 19 | PH04-053 |
| `EducationalOrganization` added to ppq + mcq-hub; `WebSite` removed from 99 non-homepage pages | 106 | PH04-052 |
| `inLanguage` → `en-GB` everywhere | 179 nodes | PH04-054 |
| Notes teaser read from `questions-data/` rather than duplicated | 166 | PH06-028 |
| The 18 self-disagreeing `<head>` fields modelled as an explicit `ogDescription` | 18 | PH06-029 |
| `convert_raw_notes.py` replaced by `page_shell.py` | — | **PH06-027** |
| Full organisation node (`logo`, `description`, `sameAs`) on the 5 entity-home pages, pointing at the root `android-chrome-512x512.png` | 5 | PH04-055, D29 |

**Migration Phase 7 (baking the header/footer) is unblocked.** P3 ruled: proceed
on its own merits — one source of truth for the nav, no runtime fetch, and it
removes one of jQuery's three consumers — but **not** as a link-equity fix,
because PH03-049 established it is not one.

### Wave 3 — One board identity, in data

| # | Change | Finding |
| --- | --- | --- |
| 3.1 | `boards.json` — one canonical record per board, with `slug`, `dirName`, `taxonomyKey` **and `displayName`** | PH09-022 |
| 3.2 | All 111 hardcoded board literals across 9 generators read from it, including the two-board ternary at `build_glossary.py:679` | PH01-012 |
| 3.3 | Key everything on `(board, spec)`; never on `spec` alone — 37 of 129 codes collide | PH09-023 |
| 3.4 | **Adopt `Edexcel A` as the display label everywhere**, from `boards.json` | **PH07-056** |

**3.4 is the user-facing payoff and the reason to do 3.1 at all.** It must **add**
a token (`Edexcel Theme 1` → `Edexcel A Theme 1`), never shorten a breadcrumb —
P5 measured those as the differentiators on the 22 near-identical pairs. Visible
text only; no URL, slug or directory name moves. Run
`verify_text_integrity.py` against the prior commit.

### Wave 4 — Weight and speed

| # | Change | Effect | Finding |
| --- | --- | --- | --- |
| 4.1 | Re-encode 112 diagram PNGs: 1600 px + 64-colour palette, **same filenames** | **26.2 MB → ~3.2 MB**; mean notes page 513 KB → ~63 KB of images; **0 HTML edits** | PH08-034, D25 |
| 4.2 | Ship a 20-icon FontAwesome subset; drop the 2.49 MB of legacy `.eot`/`.svg`/`.ttf` | ~69 KB → ~2 KB, render-blocking on 463 pages; **no HTML change** | PH08-033 |
| 4.3 | Per-topic ppq payloads, keeping `questions.json` published for the master page | 414 KB → a few KB on 90 pages; closes the other half of the CLS | PH08-046 |
| 4.4 | Move the `size-adjust` fallback metrics from `quiz.css` to `css/main.css` | 290 more pages get them; **re-measure notes-topic CLS — this may close PH08-035's second half** | PH08-041 |
| 4.5 | Reconcile the two breakpoint systems on the theme's set; `revision-notes-textbook.css` 768 → 736 first | closes the 32 px band on 169 pages | PH07-059 |
| 4.6 | Scope the 11 bare selectors in `revision-notes-textbook.css`, then `contact.css` and `tutoring.css` | removes the load-order dependency | PH08-038 |
| 4.7 | 8 links from 2 pages: `/revision-notes/` → 6 practice hubs, `/past-papers/` → 2 ppq board hubs | **max raw click depth 4 → 3, 0 pages left at 4** | PH03-048 |
| 4.8 | Notes back-link anchor: `Back to the notes` → the topic's own name | 166 links gain topical signal | PH03-050 |
| 4.9 | CTA block on the glossary and flashcards generators | 10 pages stop being commercial dead ends | PH07-058 |
| 4.10 | **jQuery + dropotron removal — 175 KB, 325–500 ms render-blocking on every page** | biggest single perf win left | PH08-043 |

**4.1 before 4.10.** 4.10 is **gated on Wave 2 Phase 7**: once the header and
footer are baked at build time, `inject-templates.js` disappears and one of
jQuery's three consumers goes with it, which turns a high-risk rewrite into a
moderate one. Doing it before means doing it twice.

**4.4 before re-opening PH08-035.** Diagnose the notes-topic 0.110 with one
Lighthouse run **after** 4.4; the missing fallback metrics are the leading
hypothesis and it may already be closed.

### Wave 5 — Content and editorial. Each needs explicit approval, every time

| # | Change | Finding | Why it is here |
| --- | --- | --- | --- |
| 5.1 | Verify all 78 SVG/PNG diagram pairs individually against the PNG **and** the notes' own `<figcaption>` | PH08-047 | At least one SVG drops a panel. Aspect ratio does not predict which |
| 5.2 | Draw the 28 missing diagrams to `docs/DIAGRAM_STYLE.md` | PH08-047 | Without them, 20 pages sit in two visual styles indefinitely |
| 5.3 | Swap, per board directory, updating all 231 `width`/`height` pairs in the same commit | PH08-047 | The aspect ratio changes on 76 of 78 |
| 5.4 | The 3 structurally malformed notes pages | PH06-031 | Edits inside prose regions. **Explicitly excluded from D18's approval** |
| 5.5 | Rule on the two `Regulation` glossary definitions | PH10-063 | Content, logged not fixed |

**5.1–5.3 are a project, not a task.** Route (c) was chosen (D25): 4.1 delivers
88% of the weight saving now, and this wave keeps all of its value for later.

### Dated dependency — ≈2026-09-22

The **day-45 GSC re-measure**. Three findings are blocked on it and **none of them
can be honestly concluded before it**:

- **PH05-019/020** — all 26 AQA "excluded by noindex" URLs had the tag removed on
  2026-07-30, nine days before the export. The window is contaminated; any
  duplication conclusion drawn from it is unsound, **including one drawn from this
  audit's own similarity numbers**.
- **PH05-021** — whether the AQA `<h1>` spec-code prefix can go.
- **PH03-049 step 2** — whether `/past-papers/edexcel-b/` and `/ocr/` need
  anything at all. They rank at scale on one internal link each, which is itself
  evidence that internal equity is not what carries them.

---

## 3. What NOT to do

Recorded so it is not re-proposed. Each has a measured reason.

- **Do not manufacture links to `/past-papers/edexcel-b/` or `/ocr/`.**
  `seo/07b-link-decisions.md` item 4b declined this because no honest anchor
  exists — nothing on the site is *about* those boards. P3's new evidence sharpens
  the cost and leaves the reason intact. PH03-049.
- **Do not add a cross-board canonical.** Both boards are meant to rank for
  board-specific queries. D4.
- **Do not touch the 1,187 KaTeX inline styles or the 6 `<noscript>` `<style>`
  blocks.** Both are load-bearing build output. PH08-042.
- **Do not "complete" the 179 `Course` nodes.** They are `isPartOf` references;
  Google's Course requirements do not apply. A validator will flag them anyway.
- **Do not refactor the Quiz markup.** 1,267 questions, 0 omissions, fully
  compliant. It is the one rich result this site can win.
- **Do not add `verify_liquid.py` to CI before PH00-011 is fixed.**
- **Do not add `.nojekyll`**, ever, without moving `_working/` out first.
- **Do not add print styles to the practice-question or past-paper-question
  families.** Considered and declined, P7 §6.
- **Do not run `convert_raw_notes.py`** until Wave 2 replaces it.
- **Do not rewrite git history** for the specification PDFs. D27.
- **Do not switch Pages to Actions-based deployment.** It disables
  `_config.yml`'s `exclude`, which is the only thing keeping working files off
  the site.

---

## 4. Rollback plans for the two URL-affecting changes

**Everything else in this roadmap changes zero URLs.** Only these two remove one,
and both are additions to `_config.yml`'s `exclude` rather than deletions from the
repo.

### 4a. Exclude `logo/` and `old-logos-archive/` — 30 URLs

**Authorised by D28.** Evidence gathered before recommending: **0** references
across every published `.html`, `.css`, `.js`, `.json`, `.xml` and
`site.webmanifest`; **0** rows in any of the 8 `seo/gsc-exports/` CSVs or in
`seo/performance-pages.csv`. Neither directory has ever earned an impression.

- **Change:** two lines added to `exclude:`. Files stay in the repo, which is what
  "safekeeping" means.
- **Verify before:** `git ls-files logo old-logos-archive | wc -l` = 30, and
  `grep -r` for either path across published files returns nothing.
- **Verify after:** `build_sitemap.py --check` reports "nothing written" — these
  are not in the sitemap either way — and `verify_links.py` still reports 0 broken.
- **Rollback:** delete the two lines, push. The URLs return on the next deploy,
  unchanged, because the files never left the repo. **Reversible in under a
  minute, with no data loss at any point.**
- **Do not** point `EducationalOrganization.logo` at `logo/`. Use the root
  `android-chrome-512x512.png`. D29.

### 4b. Move `macro-application-uk-sa.md` to `raw-notes/` — 1 URL

- **Change:** `git mv revision-notes/macro-application/macro-application-uk-sa.md
  raw-notes/`. `raw-notes/` is already excluded, so no `_config.yml` edit.
- **Verify before:** 0 references to the `.md` URL anywhere (confirmed); the
  content is already published as `macro-application/index.html`.
- **Verify after:** `verify_links.py` 0 broken; `verify_liquid.py` still reports
  exactly its one known problem.
- **Rollback:** `git mv` it back. Reversible in seconds.

**Neither is a 301 situation.** GitHub Pages issues no redirects, but neither URL
is linked from anywhere, appears in any sitemap, or has ever earned an
impression — so there is nothing to redirect. This is materially different from
the frozen-URL rule, which protects URLs that carry equity.

---

## 5. What becomes of `_audit/` — the one decision with a deadline

`_audit/` is **gitignored** under D1, so **none of this is in git history.** It
exists only as files on one machine. D1's reasoning was sound at the time: the
repo is public, and the audit is a list of this site's defects with evidence
attached.

That reasoning **expires the moment the roadmap starts**, because the roadmap is
the audit. Three options:

| | Option | Consequence |
| --- | --- | --- |
| **a** | **Move to `docs/audit/` and commit.** `docs/` is already excluded from publishing, so it stays off the site while being in history. | The findings become the backlog. Still readable by anyone who opens the public repo — but so is `REVIEW-NOTES.md`, which is a 1,596-line list of known content errors, and that judgement was already made. |
| b | Keep it gitignored and work from it locally. | One disk failure from losing 11 phases of evidence. Nothing links a commit to the finding that motivated it. |
| c | Extract only this synthesis into `ROADMAP.md` and discard the rest. | The roadmap survives; the evidence behind every number does not, so the next person re-derives it. |

**Recommendation: (a).** The precedent already exists in this repo —
`REVIEW-NOTES.md` and `docs/CONTENT_ISSUES.md` are exactly this kind of document,
public, and deliberately so. Excluding `docs/` keeps it off the site, which was
D1's actual concern; being in a public repo was the acceptable half. Doing (a)
also lets each roadmap commit cite its finding ID, which is what makes the work
auditable a year from now.

**If (a) is chosen**, the move must add `docs/audit/` to nothing — `docs/` is
already excluded — and must remove the `_audit/` line from `.gitignore` in the
same commit, or the move silently does nothing.

---

## 6. Suggested order, if you want one list

1. **Wave 0**, all nine. About an hour, no dependencies, immediate.
2. **Wave 1**, in order. The workflow then guards everything after it.
3. **Decide `_audit/`** (§5) before Wave 2, so the roadmap commits can cite findings.
4. **Wave 4 items 4.1, 4.2, 4.3, 4.4** — pure asset work, no HTML edits, large
   measurable wins, independent of the build step. Re-measure CLS after 4.4.
5. **Wave 2**, the migration, phase by phase with the harness.
6. **Wave 3**, `boards.json` and the Edexcel A labels.
7. **Wave 4 remainder**, ending with 4.10 once migration Phase 7 has landed.
8. **≈2026-09-22:** the GSC re-measure, then close PH05-019/020/021 and
   PH03-049.
9. **Wave 5**, when there is appetite for content work.

**Nothing in this roadmap decays.** If it stalls after Wave 1, the site is
measurably better and fully protected, and every later wave still applies
unchanged.

---

## 7. Closing note on the audit's own limits

Three things this audit could **not** establish, marked UNKNOWN rather than
guessed:

- **The cause of the notes-topic CLS of 0.110.** Needs Lighthouse's
  `layout-shift-elements` detail — one run. The raw reports were deliberately not
  kept (`8c8034b`). PH08-035.
- **Colour contrast.** Needs a rendering engine; this audit does not render.
  `seo/tools/run_lighthouse.py` already runs the audit that answers it.
- **Whether the 18 shortened social descriptions are deliberate.** They read as
  intentional; nothing records it. PH06-029.

And two corrections the audit made to its own earlier work, recorded because the
originals were quoted onward: **PH00-004's hand-maintained `<head>` count is 190,
not 463**; and **`00-INVENTORY.md` §3 understated the two top injection-dependent
URLs at 143 clicks / 11,971 impressions — counting both URL forms, it is 291 and
21,131.**

**The single most useful habit this audit would recommend keeping:** when a
document states a number a script computes, cite the script. `verify_glossary.py`
printed `44/44` on every run for weeks while CLAUDE.md said 46, and nobody was
comparing them. Wave 1 exists to make that class of silence impossible.
