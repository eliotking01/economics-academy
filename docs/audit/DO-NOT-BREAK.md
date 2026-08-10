# Do not break

Started in Phase 0, appended to as the audit proceeds. Anything listed here is
load-bearing: it looks removable and is not. Every entry says **why**, because an
entry without a reason gets deleted by the next person who finds it inconvenient.

No recommendation in this audit may propose undoing anything below without
saying so explicitly, in those words, with a justification.

---

## Hosting and publishing

**No `.nojekyll`.** Adding one disables `_config.yml`'s `exclude` entirely and
immediately publishes every `_`-prefixed directory — `_working/` and `_audit/`
included. If `.nojekyll` is ever wanted, `_working/` and `_audit/` must move out
of the repo first.

> **Added 2026-08-09, D30.** `_audit/` is now `docs/audit/`, so it is no longer
> protected by Jekyll's `_`-prefix rule — **only** by `docs/` in `exclude`. That
> makes the warning above stronger, not weaker: a `.nojekyll` would publish the
> entire audit as well as `_working/`. `_working/` is still `_`-prefixed and the
> original sentence still applies to it.

**`_config.yml`'s `exclude` list is the only thing keeping working files off the
site.** `exclude` **replaces** Jekyll's defaults rather than adding to them,
which is why `Gemfile`, `node_modules` and `vendor/` are restated inside it.
Deleting any line publishes that path. Before this list existed,
`/REVIEW-NOTES.html`, `/CLAUDE.md` and `/scripts/build_glossary.py` were live.

**`templates/`, `past-paper-questions/questions.json` and `flashcards/data/*.json`
must stay published.** They are fetched at runtime. Excluding `templates/`
removes navigation from all 463 pages.

**Liquid runs over every markdown file before Markdown.** A stray `{%` fails the
whole deploy, not the page. Backticks do not protect it. `_audit/` is gitignored
so its markdown never reaches the Jekyll build — but if that ever changes, run
`python3 scripts/verify_liquid.py`.

> **Added 2026-08-09, D30; RESOLVED the same day by D31.** Committing the audit
> to `docs/audit/` put 18 more markdown files in front of `verify_liquid.py` and
> took it from 1 problem to 8 — all of them prose *about* the hazard, in files
> Jekyll never renders. That was PH00-011's false positive reproduced eight-fold,
> and it is now fixed at the root: the checker parses `_config.yml`'s `exclude`.
>
> **The current expected state is `0 problems`, exit `0`** — see D31 and the
> suite listing at the foot of this file. What it now checks is the **1**
> markdown file Jekyll actually renders,
> `revision-notes/macro-application/macro-application-uk-sa.md`, which is
> PH10-060 and is proposed for `raw-notes/` by PH11 §4b. **If that move happens,
> the file count goes to 0 and the script deliberately fails**, on the grounds
> that a checker with nothing to check is dead code rather than a pass.

---

## URLs

**Every published URL is frozen.** GitHub Pages issues no 301. There is no
`_redirects`, `netlify.toml`, `vercel.json` or `.htaccess`, and the default
Jekyll build offers no equivalent. Meta-refresh and JS redirects pass authority
unreliably and leave stub pages in the repo permanently. This was evaluated for
the glossary on 2026-08-07 and rejected on exactly that basis.

**Canonical URL form is the trailing-slash directory, never `/index.html`.**
Established across `b7c5efc`, `1880565`, `2d8936a`, `79faf81`, `befb061`,
`cf9b4c7`. Currently 0 mismatches across 463 pages, and 0 internal links to an
`index.html`. Google is mid-consolidation on this and re-introducing an
`index.html` link would reverse it.

**`/specificiations/` no longer exists.** The two exam-board specification PDFs
were deleted on 2026-08-08 (`d220ad0`) on copyright grounds — the one deliberate
URL removal in this audit, recorded in `DECISIONS.md` D12. Both URLs now 404,
intentionally. **Do not recreate the directory**, and do not create stub pages
for the two URLs. The typo is preserved in history and in the commit message
because the directory was always spelled that way.

**`scripts/build_sitemap.py` is the only thing that may write `sitemap.xml` or
`sitemaps/*.xml`.** It enumerates from the filesystem and takes `lastmod` from
git, so deleting or adding a file is reflected by re-running it. Hand-editing
either reintroduces the build-date problem that `b7161e6` fixed. It parses
`_config.yml`'s `exclude` at line 93 rather than restating it — copy that pattern
rather than adding skip lists.

**The 9 `not-found-404` URLs in the GSC export are correctly 404.** They are a
deleted `aqa-as-micro`/`aqa-a-micro` section plus one Edexcel B mark scheme that
does not exist. Do not create stub pages for them. Do not run GSC validation on
that issue — it will fail and reset the two-week cycle.

---

## The SEO work of 2026-08-08

**The two `@import` rules must stay out of `css/main.css`.** `4db232c` hoisted
FontAwesome and the font stylesheet into every `<head>`, in that order, to remove
a render-blocking chain. Putting them back reverses a measured CWV improvement
(`seo/09-web-vitals-baseline.md`, `seo/lh-live-after-7run.json`).

**`sitemap.xml` is a `<sitemapindex>`, not a `<urlset>`.** Seven children under
`sitemaps/`, 744 URLs. Per-section indexation reporting in GSC comes from the
index structure. Do not flatten it. `lastmod` is taken from git, not build date —
two generators previously stamped build dates and were fixed (`be3ec19`).

**Link decisions already made and declined are decisions.**
`seo/07b-link-decisions.md` §5 declined: links to the 283 PDFs; more links to
`tutoring.html` (449 inbound) or `marking.html` (275); reuse of the ppq
topic-chip anchor string; and raising notes→ppq coverage above 76%/92%. Each has
a reason. Re-propose only with new evidence.

**`seo/tools/verify_seo.py` carries 4 permanent assertions** added in `53a3e54`.
It must keep passing.

**`seo/gsc-exports/` is a dated baseline, not current state.** Exported
2026-08-08, before Google recrawled. Re-export at day 45 and compare; do not read
it as live.

---

## Board differentiation

**The `spec-alert` and `notes-cta` blocks are load-bearing SEO, not furniture.**
Measured in P5: stripping them raises Edexcel/AQA page similarity from 6 pairs
≥0.80 to 26, because they are board-specific — the `spec-alert` names the board
and unit, the `notes-cta` links to that board's past papers. On the 22 pairs
whose prose is ≥0.95 identical, these blocks and the `<title>`/`<h1>`/description
are **the only things telling Google the two pages are different**. Making them
board-generic, or factoring them into a shared template that drops the board
name, would remove that.

**Never add a cross-board canonical.** Both boards are meant to rank for
board-specific queries. `DECISIONS.md` D4.

**The AQA `<h1>` spec-code prefix stays until the day-45 read.** On the identical
pairs it is the last textual differentiator. PH05-021.

## The data model

**Spec code is not a key. Always use `(board, spec)`.** 37 of 129 spec codes are
claimed by both boards with entirely different meanings — `1.1.1` is "Economic
Methodology" on AQA and "Economics as a Social Science" on Edexcel, because AQA
notes use site-local codes in the same namespace as Edexcel's real ones. Joining
on `spec` alone produces 22 phantom disagreements that are not real. PH09-023.

**`questions.json`'s topic keys are bare slugs and work by accident.** No slug
collides today because each is `spec-code` + `title`. Two boards giving the same
code the same title would merge their questions under one key with no error.
Do not "simplify" a topic key by dropping the spec-code prefix from a slug — that
prefix is what is keeping the namespace unique.

**Flashcard IDs are effectively immutable.** Leitner spaced-repetition state is
keyed on card ID in `localStorage`. Renaming an ID resets a student's progress
silently. PH09-024.

**`EXPECTED = {"edexcel": 87, "aqa": 79}` in `build_past_paper_taxonomy.py` is a
feature.** It makes adding a board fail loudly rather than silently emit a short
taxonomy. Anything that replaces it must keep that property.

## Content and generation

**Never alter existing economics wording.** Formatting, markup and structure
only. This audit's own definition of scope: restructuring HTML is legitimate,
touching the prose is not, in any circumstance.

**Never bulk-rewrite prose with a script.** Scripted paragraph rebuilds have
silently destroyed `<a>` tags in this repo before.

**Generated output is not hand-editable.** `revision-notes/glossary/**`,
`practice-questions/**`, `past-paper-questions/index.html` +
`questions.json`, `flashcards/**` — fix the source or the generator and re-run.
Several generators run Prettier over their own output so that generating twice is
byte-identical; hand-edits break that idempotence silently.

**Hand-written data files must survive re-extraction.**
`past-paper-questions-data/tags.json`, `glossary-data/curation.json` and
`glossary-data/authored.json` are human judgement kept deliberately outside the
generated files. Re-extraction must never write to them.

**The glossary's verbatim guarantee is narrower than it sounds.**
`verify_glossary.py` check 1 proves the *extraction* is faithful, not the page —
`curation.json`'s `rewrite` block edits 46 lead-ins at render time and
`authored.json` holds 76 definitions the notes never gave. Do not describe the
glossary as word-for-word without that qualification.

**AQA notes use site-local spec codes `1.x.y`/`2.x.y`,** deliberately not the real
AQA 7136 codes (`4.1.x`/`4.2.x`). Ratified. Do not "fix" them.

**Past-paper Section A is permanently out of scope**, every board and
qualification. **8EC0 has no Section C** — verified from all 16 papers. Do not
invent one.

**Duplicate questions across qualifications are kept, never collapsed.** A
collapsed entry would hide that a question was set at two different demands.

**Mark scheme content is never extracted.**

---

## Numbers that must not regress

Re-check with the commands given. All measured 2026-08-08 on `8c8034b`.

| Assertion | Value | Command |
| --- | --- | --- |
| Broken internal links | 0 | `python3 docs/audit/scripts/link_graph.py` |
| Pages reachable without JS | 461 / 463 | same |
| Duplicate titles | 0 | `python3 docs/audit/scripts/metadata_census.py` |
| Duplicate meta descriptions | 0 | same |
| Canonical ≠ expected | 0 | same |
| `og:url` ≠ canonical | 0 | same |
| `lang="en-GB"` | 463 / 463 | same |
| GA4 ID `G-YVCNRW4QH6` | 463 / 463 | `grep -L 'G-YVCNRW4QH6'` over published HTML |
| Sitemap ⇄ filesystem diff | 0 both directions | `docs/audit/scripts/` (P4) |
| Tracked `" N.ext"` duplicates | 0 | `git ls-files \| grep -cE ' [0-9]+\.'` |
| `onclick=` attributes | 0 | `grep -lF 'onclick='` over published HTML |

## HTML architecture (added by P6)

**`scripts/convert_raw_notes.py` must not be run as-is.** Its page template
(line 785) predates seven SEO commits: it emits no canonical, no `og:`/`twitter:`
tags, neither JSON-LD block, `lang="en"` instead of `en-GB`, no `notes-cta`, and
— because `4db232c` removed the two `@import` rules from `css/main.css` — **no web
fonts and no FontAwesome**. CLAUDE.md names `raw-notes/` as the source for
converted notes without recording this. 73 markdown sources are still sitting
there. PH06-027.

**The `spec-alert` and `notes-cta` blocks stay per-page, never in a shared
layout.** P5 measured them as the load-bearing board differentiation on the 22
near-identical Edexcel/AQA pairs. Any template layer must keep the board name and
unit reaching the output verbatim, per page. Restated here because a template
migration is exactly the operation that would "helpfully" factor them out.

**`<section id="main">` and the `#main` anchor are coupled.** The skip link at
`templates/header.html:2` targets `#main`. If `<section id="main">` ever becomes
`<main id="main">`, the `id` must survive, or every page loses its skip link
silently. 462 pages are affected; only `index.html` uses `<main>` today. PH06-032.

**The MCQ teaser on a notes page is a copy of `notesTeaser` in
`questions-data/`.** Identical on 166/166 today, placed there by
`append_questions_link.py`, and nothing checks it stays that way. Do not edit
either copy in isolation. PH06-028.

**Both breadcrumb copies must stay in step.** Every page with a breadcrumb writes
it twice — visible `<nav>` and `BreadcrumbList` JSON-LD. 440 of 441 agree;
`revision-notes/macro-application/index.html` is the one that does not. PH06-030.

**Any new source directory goes into `_config.yml`'s `exclude` in the same commit
that creates it.** A build step means new source files in the repo, and this repo
publishes by default. Verify with `lib.published_html()` and
`build_sitemap.py --check` before committing, not after.

**Migration is byte-identical, improvements come after.** No structural change to
a page family may be combined with the commit that moves it onto a template. A
harness failure must be unambiguous.

## Front-end assets (added by P8)

**The 1,187 inline `style=` attributes inside KaTeX subtrees are build output.**
They are the `top:`, `height:`, `margin-right:` and `vertical-align:` offsets
KaTeX emits to position glyphs, on the two glossary pages and five flashcard
pages. Removing them or "extracting them to classes" breaks every formula on
those pages. Of the site's 1,520 inline styles, **only 333 are authored** — and
none of those is on a generated page. Any sweep against PH00-008 / D18's
normalisation 6 must exclude KaTeX output by construction, not by hand. PH08-042.

**The six `<style>` blocks on the practice-questions hubs are inside
`<noscript>`.** They re-open an accordion that CSS collapses and `quiz.js`
re-opens, so with scripting off the topic links would be unreachable. The
generator writes them deliberately and explains why in a comment. Three of the
site's nine `<style>` blocks are genuine violations; these six are not.
PH08-042.

**The `size-adjust` fallback `@font-face` rules in `css/pages/quiz.css` are
deliberate CLS work.** `"Merriweather Fallback"` and `"Source Sans Pro Fallback"`
use `src: local(...)` with metric adjustment so text does not reflow when the web
font arrives. They look like dead code and are not. If they move to `css/main.css`
so all 463 pages get them — which P8 recommends — they must not be dropped on the
way. PH08-041.

> **Done 2026-08-10, Wave 4.4.** Both rules are now in `css/main.css`, declared
> once, immediately above the base `body, input, textarea, select` stack.
> `quiz.css` keeps every `"… Fallback"` name in its stacks and carries a comment
> saying where they are declared. Two things learned doing it, both load-bearing:
>
> - **An `@font-face` is inert until a stack names it.** Moving the declarations
>   alone would have changed nothing on the other 297 pages. Every stack that
>   renders text now lists the matched fallback before the generic, including 13
>   rules in `revision-notes-textbook.css` that named `"Source Sans Pro"` with no
>   fallback of any kind.
> - **Never size an element in `ch` on this site.** `ch` is the advance of "0"
>   alone, so the element's own width changes when the font swaps — the one
>   reflow `size-adjust` cannot absorb, because it matches *average* advance
>   width. `.ppq-intro`'s `60ch` was 442.5px in Source Sans Pro and 466.0px in
>   the fallback and took the past-paper-questions page to CLS 0.288 at 736px.
>   Both uses are now `em`: `60ch → 28.73em` and `72ch → 34.48em`, from Source
>   Sans Pro's own ch/em ratio of 0.4789, so the rendered measure is unchanged.
>   `grep -rn '[0-9]ch\b' css/` must stay empty outside `css/vendor/katex/`.

**`past-paper-questions/questions.json` stays published at its current path.**
Already recorded above as fetched at runtime. P8 proposes *adding* per-topic
payloads beside it, never replacing it: the master search page needs the full
index. PH08-046.

> **Done 2026-08-10, Wave 4.3, and the master payload is untouched.** 81
> per-topic payloads now sit at
> `past-paper-questions/<board>/<slug>/questions.json`, median 9.6 KB against
> the 413.7 KB those pages used to fetch. All 90 files are generated — do not
> hand-edit any of them, re-run `scripts/build_past_paper_questions.py`.
>
> - **The master, board and section pages must keep fetching the full index.**
>   Their Topic filter is live and lists every topic on the board, which a
>   per-topic payload cannot supply. Only pages with `data-prefilter-topic`
>   carry `data-src`.
> - **`papers` in a per-topic payload is a sparse list, and the nulls are
>   load-bearing.** `question-search.js` reads `data.papers[q.p]` where `q.p`
>   is an index into it (`:136`, `:393`). Re-packing the list to drop the nulls
>   would re-point every question at the wrong paper, silently, with no error
>   and plausible-looking output. It saves about 300 bytes. Do not do it.
> - **`topics` carries every tag on every included question**, not just the
>   page's own topic, because each card renders a link per tag.
> - The stale-output sweep at the end of the generator deletes per-topic
>   payloads by the same rule as pages, and skips `PAGE_DIR` itself — that
>   guard is what stops it deleting the master `questions.json`.

**`contact.css` and `tutoring.css` keep their bare selectors, and
`css/main.css` must stay linked first.** Wave 4.6 scoped
`revision-notes-textbook.css` and **declined these two, measured**: on both
pages `main.css` is currently *winning*, so scoping reverses the design rather
than removing a dependency. contact.html loses 120px of form height and its
`select`/`textarea` stop matching its text inputs; tutoring.html's
`#contactModal` is a **sibling** of `section#main`, so `.tutoring-page .modal`
matches nothing and the modal drops from `position: fixed` to `static`, putting
the enquiry form inline on the page. `:where()` scoping is cascade-neutral (0 of
281 and 0 of 362 elements changed) but buys only the census metric, since the
specificity is unchanged.

> **The guard is `scripts/verify_css_load_order.py`, the workflow's 19th step,
> and it must stay there.** Load order is now an invariant, not an accident. It
> asserts `css/main.css` precedes every `css/pages/*.css` (462/462), that
> `4db232c`'s order fontawesome → Google Fonts → main.css holds (462/462, which
> nothing checked before), and that
> `revision-notes/macro-application/index.html` is the **only** page loading two
> page sheets. **Wave 2's `page_shell.py` is the thing this exists for** — a
> generated `<head>` that emits the same links in a different order breaks two
> commercial pages with no error and no failed request.

**`4db232c` is not to be reversed by anything in PH08-033.** Removing
FontAwesome's render-blocking chain and reducing FontAwesome's *size* are
different changes. The two `@import` rules stay out of `css/main.css`; the
stylesheet stays a direct `<link>` in every `<head>`, in order.

> **Done 2026-08-10, Wave 4.2, and `4db232c` is intact** — same filename, same
> `<link>`, same position, no `<head>` touched. Stylesheet 69.4 KB → 2.9 KB,
> `webfonts/` 2.79 MiB → 1.5 KB.
>
> - **`css/fontawesome-all.min.css` is a subset and its name is a lie.** 15 of
>   1,458 icon rules, one `@font-face` of three. Renaming it would mean editing
>   463 `<head>` blocks to gain nothing, so it keeps the name and says so in a
>   comment at the top. Do not "restore" the full file.
> - **`webfonts/fa-solid-900.woff2` is generated.** The full font is
>   `_working/fontawesome/fa-solid-900.woff2`, unpublished, and
>   `scripts/subset_fontawesome.py --apply` regenerates the shipped one from
>   it. Adding an icon is: add the `.fa-x:before` rule to the stylesheet, re-run
>   the subsetter, commit both. There is no second glyph list — the subsetter
>   reads the stylesheet.
> - **`scripts/verify_icons.py` must stay in the workflow.** A subset font
>   fails silently: the glyph renders as nothing, with no error anywhere. That
>   is exactly how faq.html's 30 accordion `+` icons stayed invisible until a
>   pixel diff found them. All four of its checks were tested by deliberately
>   breaking each one.
> - **`recalcTimestamp=False` goes on the `TTFont` constructor**, not on
>   `subset.Options`. Without it `head.modified` is stamped with the current
>   time and two runs a second apart give different bytes — PH09b-025 again,
>   for the third time. Hash three consecutive runs of anything here that
>   writes a file.
> - Two one-off, non-stdlib dependencies now exist and neither is in CI:
>   **Pillow** (`reencode_diagrams.py`) and **fonttools + brotli**
>   (`subset_fontawesome.py`). Everything the workflow runs is still
>   stdlib-only, and must stay that way.

**Diagram `width`/`height` attributes encode the file's true aspect ratio.** All
211 notes images carry the intrinsic pixel dimensions, and `max-width: 100%`
means browsers use them only for the ratio. A re-encode that preserves the exact
aspect ratio needs no HTML edit; one that changes it by even a rounding step must
update all 295 `<img>` tags in the same commit, or layout shift appears where
there is none today. PH08-034.

> **Done 2026-08-10, Wave 4.1, and the count is 293 not 295.** All 112 PNGs were
> re-encoded to a 64-colour palette in place — same filenames, **same pixel
> dimensions**, so no HTML edit was needed and none was made. 26.21 → 5.41 MiB.
> Three things worth keeping:
>
> - **The resize was dropped, deliberately.** The palette does 79.4% alone;
>   1600px takes it to 81.7%, which is 0.61 MiB sitewide, against rewriting 293
>   `<img>` tags and softening every diagram on a 2× display — the notes
>   container is ~1088 CSS px, so 2176 device px, and the sources are
>   2200–3600px. Resampling to 2200px measured **larger** than not resizing.
>   Do not re-propose the resize without new evidence.
> - **Never quantise these with fast-octree.** It is smaller (4.48 MiB) and it
>   maps the white background to `(254,254,254)` on all 112, putting every
>   diagram in a faint grey rectangle. Median cut keeps pure white on 112/112
>   and `scripts/reencode_diagrams.py` aborts if any file loses it.
> - **`scripts/reencode_diagrams.py` skips files already converted, and must
>   keep doing so.** Median cut is not idempotent: without the guard a second
>   `--apply` rewrote 37 of 112 files to the same total size and different
>   bytes. It is the only script in the repo needing a non-stdlib package
>   (Pillow), it is a one-off conversion rather than a build step, and it is
>   **not** in the CI workflow.
>
> **One pre-existing defect was found and fixed by the same check.**
> `long-run-growth-ad-lras.png` was declared `1667x593` on
> `revision-notes/macroeconomics-diagrams.html` against `3030x1454` on disk —
> the one tag of 293 that disagreed with its file. All 293 now agree, and that
> is worth re-checking after anything touches `images/diagrams/`.

## Numbers added by P8

| Assertion | Value | Command |
| --- | --- | --- |
| Unreferenced stylesheets | 0 | `python3 docs/audit/scripts/asset_census.py 1` |
| Unreferenced JS files | 0 | `python3 docs/audit/scripts/asset_census.py 4` |
| Stylesheet/script hrefs not resolving to a file | 0 | sections 1 and 4 |
| Distinct GA4 IDs / distinct gtag snippets | 1 / 1 | `python3 docs/audit/scripts/asset_census.py 9` |
| Dangling `aria-controls` targets | 0 | `python3 docs/audit/scripts/asset_census.py 8` |
| Duplicate `id=` within a page | 0 | same |
| `target="_blank"` without `noopener` | 0 | same |
| Pages whose `#main` skip-link target is missing | 0 | same |
| `<button>` without `type=` inside a `<form>` | 0 | PH08 §3 |
| Third-party origins contacted | 4 | `python3 docs/audit/scripts/asset_census.py 9` |

## Internal linking (added by P3)

**Only four pages sit at raw click depth 1** — `revision-notes/index.html`,
`past-papers/index.html`, `tutoring.html`, `marking.html`. A hub can only be
pulled to depth 2 by a link from one of those. That is why the depth fix in
PH03-048 is 8 links from 2 pages, and why the intuitive version (each notes board
hub → its practice twin) moves only 6 pages. Do not "improve" the fix by moving
those links to the board hubs; measure it with `link_depth.py 1` first.

**`/past-papers/edexcel-b/` and `/past-papers/ocr/` have one raw inbound link
each, and that is not a defect to fix by linking.** They earn 291 clicks and
21,131 impressions between them — the most on the site outside the homepage — and
they have one link because nothing on the site is *about* those exam boards.
`seo/07b-link-decisions.md` item 4b declined manufacturing links there because no
honest anchor exists, and P3 re-confirmed that the reason still holds.
PH03-049.

**Hub/spoke integrity is currently perfect and is worth keeping that way.** 13
hub directories, 332 spokes, 0 missing links in either direction, plus 166/166
notes↔mcq pairing both ways. Any new page family should be checked with
`link_depth.py 3` before it ships.

**All 4,979 `#fragment` links resolve.** `link_depth.py 4` checks this
cross-page, which `verify_links.py` does too. Keep both passing.

**The ppq topic-chip anchor monoculture is already fixed — do not reintroduce
it.** `55dda8a` re-pointed the query-string links. Today: 0 links read
`2.6.2 Demand-side Policies`, 0 links use the `?topic=` form, and 561 links into
`/past-paper-questions/` carry 290 distinct anchors. `seo/07b-link-decisions.md`
§5 declines any reuse of that anchor string.

## Structured data (added by P4)

**The practice-questions Quiz markup is complete and compliant — do not
refactor it.** 166 `Quiz` nodes and 1,267 `Question` nodes carry every field
Google requires for the practice-problems rich result, with a `Comment`
explanation on each answer. **0** omissions. It is the one rich result this site
is positioned to win. Any change to `build_questions.py`'s JSON-LD must re-run
`structured_data.py 2` and keep that at 0.

**The 179 `Course` nodes are `isPartOf` references, not page entities.** They
carry `@type`, `name` and `provider` and that is correct. Google's Course
requirements (`description`, `provider`, `hasCourseInstance`) apply to a Course
that is the page's subject. An automated validator will flag these; it is wrong.
Do not "complete" them.

**`index.html`'s first JSON-LD block is an array, not an object.** Each member
carries its own `@context`. Valid. Do not add a top-level `@context`.

**`@id` references to `https://economicsacademy.co.uk/#organization` are the
correct linked-data pattern** on the 353 pages that use them. The qualification
is that search engines do not resolve `@id` across pages, so the full
organisation node still needs to exist on the pages that matter. Do not
"deduplicate" the complete node off `index.html`. PH04-055.

**`ListItem.item` is deliberately absent from the last breadcrumb item**, on all
460 pages. Google specifies this. 376 of 1,871 `ListItem` nodes omit it and all
376 are final items. Do not add it.

**`images/eliot_shirt.JPG` is the site's one uppercase image extension**, and the
reference to it in `about.html`'s JSON-LD matches its case. It works. If either
side is ever retyped, it breaks on a case-sensitive host and not on macOS.
P1's case-sensitivity check covers `src`/`href` only, not JSON-LD.

## Labels and layout (added by P7)

**Any board-label change must ADD specificity, never remove it.** P5 measured the
breadcrumb, `<title>`, `<h1>` and `spec-alert` as the only things distinguishing
the 22 near-identical Edexcel/AQA page pairs. `Edexcel Theme 1` →
`Edexcel A Theme 1` adds a token and is safe. Shortening any breadcrumb is not.
PH07-056 is a **visible-text** change only — no URL, slug or directory name moves.

**`css/main.css` contains 736, 767 AND 768 px breakpoints.** Two systems are live
on every page: the inherited HTML5 UP theme's (1680/1280/980/736/480) and
Bootstrap's (992/768/576). Do not "tidy" one value in isolation — check which
system the sheet belongs to first, with `link_depth.py`-style measurement rather
than by eye. PH07-059.

> **Amended 2026-08-10, Wave 4.5. The claim that "the page chrome switches at
> 736" is wrong, and acting on it makes the site worse.** Measured:
>
> - **The nav switches at 767/768.** `css/main.css:2334` puts the desktop `#nav`
>   behind `min-width: 768px`; `:2346` puts the mobile `#navPanel` behind
>   `max-width: 767px`. `#header-placeholder` and the 34-rule "narrow" block are
>   on the same tier.
> - **736 is a second, real tier** governing `.container`, the row grid and body
>   sizing. Both tiers are live at once. There is no single "chrome breakpoint".
> - `revision-notes-textbook.css` at 768 was **already aligned** with the nav
>   tier. Moving it to 736 was tried and reverted: it puts full-size desktop
>   notes under a hamburger nav between 737 and 768.
>
> **What was actually done:** all 18 `max-width: 768px` queries moved to
> `max-width: 767px`, so every "mobile" query pairs exclusively with the nav's
> `min-width: 768px`. Before that, 768px exactly — iPad portrait — was the one
> width showing the desktop nav above mobile-styled content. **Do not
> reintroduce a `max-width: 768px`;** use 767, or the pairing breaks again at
> one real device width. `min-width: 768px` stays as it is in both places.
>
> **The 736 tier is deliberately untouched.** Reconciling it with 767 means
> changing the inherited theme's own breakpoints on all 463 pages, and nothing
> measured says it is broken.

**Print styles are deliberately partial.** Only `revision-notes-textbook.css`,
`glossary.css` and `flashcards.css` have `@media print`, covering 179 pages. The
practice-question and past-paper-question families are interactive surfaces whose
printed form is pointless, and the actual printable content is the PDFs.
Considered and declined by P7 §6; do not raise it as a gap.

**`logo/` and `old-logos-archive/` are repo storage, not published assets** —
Eliot, 2026-08-09, D28. 30 files, 2.4 MB, **0** references anywhere on the site and
**0** rows in any GSC export. The recommendation is to exclude both in
`_config.yml`. Do not point `EducationalOrganization.logo` at them; use the
root `android-chrome-512x512.png`, which is already published and already named in
`site.webmanifest`. D29.

## Tooling (added by P10)

**All five `seo/tools/` mutators default to dry-run and need `--apply`** —
`fix_font_loading.py`, `fix_links.py`, `fix_structured_data.py`,
`add_diagram_gallery_links.py`, `upgrade_pastpaper_links.py`. Keep it that way.
They have already been applied once and the site has moved on since; a no-flag
re-run must stay harmless. Contrast `convert_raw_notes.py`, which has no guard —
PH06-027.

~~**`verify_liquid.py` exits 1 and that is the expected state.** PH00-011 is a
pre-existing false positive. Do NOT add this script to a CI workflow before
PH00-011 is fixed: a workflow that is red from its first run gets ignored, and
then it protects nothing. If it ever reports 0, something changed; if 2, look at
what was added.~~

**RESOLVED 2026-08-09, D31 — PH00-011 is fixed. `verify_liquid.py` now exits 0,
and that is the expected state.** It parses `_config.yml`'s `exclude` (importing
`build_sitemap.excludes()` rather than restating the list) and checks only the
markdown Jekyll actually renders: **1 file, 0 problems, 133 excluded**. The
precondition on Wave 1 step 1.4 is therefore met — this script may now join the
CI workflow. If it ever reports a problem, that is a **real** deploy risk, which
is the whole point of the fix.

**Every enumeration tool in this repo globs `*.html`.** `lib.published_html()`,
`lib.pages()`, `build_sitemap.py` and `verify_links.py` all do. So
`lib.is_published()` and `lib.published_html()` can disagree about the same file,
and a non-HTML file inside a published directory is invisible to all of them —
which is how PH10-060 survived ten phases. Any new check of the published surface
must enumerate **all tracked files**, not just HTML.

**`scripts/vendor/katex.min.js` is build-time only and is never served.**
`build_glossary.py` shells out to `node` with it to pre-render formulae. What the
browser gets is `css/vendor/katex/`. It is vendored rather than fetched because
`npx --package` does not put the module on `NODE_PATH`. Upgrade both together.

**Where CLAUDE.md states a count a verifier computes, the verifier wins.**
`verify_glossary.py` check 7 prints `44/44` and CLAUDE.md says 46; the script has
been right all along. PH10-061. Prefer citing the command over restating the
number.

---

# FINALISED — Phase 11, 2026-08-09

This register is complete. Everything above is load-bearing and was written when
the evidence for it was fresh. **Read it before touching anything in
`PH11-synthesis.md`'s roadmap**, and add to it rather than editing it.

The four entries that will be hardest to resist undoing, and are most costly to
undo:

1. **The `spec-alert` and `notes-cta` blocks stay per-page.** A template migration
   is exactly the operation that would helpfully factor them out, and they are the
   load-bearing board differentiation on 22 near-identical page pairs.
2. **The 1,187 KaTeX inline styles and the 6 `<noscript>` `<style>` blocks are
   build output.** An inline-style sweep against PH00-008 will hit both unless it
   excludes them by construction.
3. **`_config.yml`'s `exclude` is the only thing keeping working files off the
   site**, and it replaces Jekyll's defaults rather than adding to them.
4. **`<section id="main">` → `<main id="main">` must keep the `id`.** 462 pages,
   and the skip link in `templates/header.html:2` is the only thing that breaks —
   silently.

**Verification that any change kept faith with this register:**

```
python3 scripts/verify_html.py
python3 scripts/verify_links.py
python3 scripts/verify_text_integrity.py <before-ref>
python3 scripts/verify_markup_integrity.py <before-ref> --strict
python3 scripts/verify_liquid.py          # 1 file checked, 0 problems, exit 0 (D31)
python3 scripts/verify_glossary.py
python3 seo/tools/verify_seo.py           # 14/14
python3 scripts/build_sitemap.py --check  # "nothing written"
node scripts/test_question_search.js
node scripts/test_glossary_filter.js
python3 docs/audit/scripts/link_graph.py           # 0 broken, 461/463
python3 docs/audit/scripts/metadata_census.py      # 0 dupes
python3 docs/audit/scripts/link_depth.py 3 4       # 0 hub gaps, 0 bad fragments
python3 docs/audit/scripts/structured_data.py 1 4  # 0 parse errors
python3 docs/audit/scripts/asset_census.py 1 4 9   # 0 unreferenced, 1 GA4 id
```

Total runtime: about 20 seconds.
