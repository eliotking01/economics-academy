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

> **Amended 2026-08-11, Wave 2 Phase 7. `templates/` is no longer fetched, and
> it still stays published.** The header and footer are baked into every page
> at build time, so nothing requests those two URLs any more and excluding them
> would break nothing. They stay for a different and weaker reason: they are two
> live URLs, this site cannot issue a 301, and removing a published URL is a
> decision in its own right that nobody has needed to make. **They remain the
> single source of truth for the nav** — `page_shell.bake()` and
> `scripts/bake_templates.py` both read them from disk at build time — so
> deleting or renaming them still breaks the build, just not the site. The rest
> of the sentence above is unchanged: `questions.json` and the flashcard decks
> are still fetched.

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

> **Amended 2026-08-10, Wave 4.9. The "449 inbound" and "275" are PAGE counts,
> not link counts** — 449 pages / 455 links and 275 / 276, re-measured and
> still exactly right. 4.9 added a CTA to 11 pages that had none, taking them
> to 459 and 285, and it does **not** overturn §5. What reconciles them is a
> number in neither document: **444 of the 455 tutoring links read
> `Book a Free Intro Call`** — 97.6%, 8 distinct anchors — and §5's own next
> bullet declines reusing an anchor string because it "deepens a monoculture".
> So the rule that survives is about the **anchor**, not the count: any future
> link to `tutoring.html` or `marking.html` must carry new anchor text, and a
> bulk sweep repeating an existing string is still declined. 4.9 used four new
> ones and took the distinct counts to 10 and 9.

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

> **Amended 2026-08-12, Wave 3.3, D39. "By accident" is right, and it is two
> accidents, not one.** Both halves of a collision already occur independently:
> **37** of 129 spec codes sit on both boards, and **11** titles are used by
> both — on different codes. **0** shared codes share a title, and the closest
> pair is 0.579 (`1.1.3`, "The Economic Problem" against "Economic Resources").
>
> **The guard is now where slugs are minted**, in
> `build_past_paper_taxonomy.build()`. Its old `seen[(board, slug)]` key could
> not see a cross-board collision by construction — measured, it built a
> taxonomy of 166 topics carrying a duplicated slug and exited **0**. Both the
> within-board duplicate and the cross-board collision now fail there, with
> different messages. **`build_past_paper_questions.topic_lookup`'s
> `SystemExit` stays and is not redundant:** it protects a different file's
> assumption, and both guards were proved to fire and to stay silent on the
> real 166.
>
> **PH09-023's "22 phantom disagreements" is not reproducible.** A spec-only
> join gives **37** walking `questions-data/` alphabetically and **0** walking
> it reversed — the count is directory-walk order, and the 0 is the dangerous
> reading. Seven of the eight topic-keyed structures were already keyed
> correctly before this wave.

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

> **Added 2026-08-10, Wave 4.9.** `verify_text_integrity.py` is what makes the
> sentence above checkable rather than asserted, and it now compares **192
> hand-written published pages** — every published page except the four
> generated families. It used to walk `revision-notes/` alone, which left the
> 9 root pages, the 5 `past-papers/` hubs and both `templates/` files
> unchecked, and wasted three slots on generated glossary pages whose wording
> `verify_glossary.py` check 1 and `verify_generated.py` already guarantee.
>
> **A deliberate wording change declares itself with a `Text-Change:` commit
> trailer**, one line per path. Do not replace this with a flag, an env var or
> a skip file: the whole point is that the declaration lives in a commit
> message, so it applies to exactly one commit, cannot be left on by accident,
> and stays in `git log` as the record. **It is per path** — declaring one page
> and changing another still fails, and that is the accident being guarded
> against. Trailers are collected across the whole commit range so a merge
> inherits the declarations of what it merges; CI compares a merge against
> `main`'s previous tip, so without that every merge of a content change would
> be red.

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
`curation.json`'s `rewrite` block edits lead-ins at render time and
`authored.json` holds definitions the notes never gave. Do not describe the
glossary as word-for-word without that qualification.

> **Amended 2026-08-12, Wave 3.2. The two counts were removed rather than
> updated, because both had gone stale and this entry is PH10-061's own
> subject.** They were 46 and 76; re-derived on 2026-08-12 they are
> `rewrite.entries` **43** and `authored.json`'s `terms` **77**, and check 1
> reports **138** authored *instances* — the same set counted per term-page,
> which is a different unit from the 77. Run
> `python3 scripts/verify_glossary.py`; checks 1, 6 and 7 print all of it.

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

> **DONE 2026-08-13, wave-norm(7/11), and the id survived on 463 of 463.** All
> 462 are `<main id="main">` now. The condition above was the whole risk and it
> was checked BEFORE editing, not after: 10 `#main` rules in `css/main.css`,
> **none** written `section#main`, and **0** references to `#main` in any
> hand-written `js/`. Nothing had ever selected on the tag.
>
> **The closer was matched by NESTING DEPTH, not indentation.** The wrapper
> holds up to 13 nested `<section>`s (`privacy.html`), so "the `</section>` at
> six spaces" is a guess that is wrong on most pages.
>
> **The sentence above is what to keep.** The id is still the coupling and it
> is still silent when broken; `asset_census.py 8` holds it at 0 pages with a
> missing `#main` target.

**The MCQ teaser on a notes page is a copy of `notesTeaser` in
`questions-data/`.** Identical on 166/166 today, placed there by
`append_questions_link.py`, and nothing checks it stays that way. Do not edit
either copy in isolation. PH06-028.

**Both breadcrumb copies must stay in step.** Every page with a breadcrumb writes
it twice — visible `<nav>` and `BreadcrumbList` JSON-LD. PH06-030.

> **CLOSED 2026-08-13, wave-norm(5/11), (8/11) and (8b/11). Both halves.**
> `aria-label="Breadcrumb"` is on all of them, not 100 of 441; the 19 pages
> that declared a trail only in JSON-LD now render one; and
> `macro-application`, the single page whose two copies disagreed, agrees.
> **460 visible, 460 labelled, 460 agreeing, and
> `KNOWN_BREADCRUMB_DISAGREEMENT` is EMPTY.**
>
> **The empty dict is kept, not deleted.** The loop still runs over it, so a
> future deliberate mismatch has somewhere to be declared, and the per-page
> comparison is what catches an accidental one. Proved still able to fail with
> the exception gone: rewording one crumb turns check 8 red.
>
> **Every one of the 19 new trails was BUILT FROM THAT PAGE'S OWN
> `BreadcrumbList`**, names copied verbatim, so the two copies cannot disagree
> — which is why `agree` rose by exactly the same 19 as `visible`. Any future
> page must do the same. Cite `python3 scripts/verify_page_shell.py` check 8.

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

> **Amended 2026-08-13. The sentence above is still exactly right, and the
> script stopped being able to say so.** Wave 2 Phase 7 baked the header and
> footer into all 463 pages, so `link_depth.py`'s "RAW" graph — which meant
> "the page's own links, WITHOUT the nav", only because the nav used to be
> fetched at runtime — now already contains every template link. **RAW and
> INJECTED became numerically identical**, `{0:1, 1:29, 2:350, 3:81}`, and the
> pair went on printing as though it were two measurements.
>
> **So PH03-048 reads as SOLVED — 0 pages at depth ≥ 4 — while nothing was
> done about it.** Its own prescription is 8 links and **none of them exists**;
> checked link by link, not inferred.
>
> `link_depth.py 1` now prints a **third graph, CONTENT**, which is the baked
> blocks removed and is what "raw" used to mean. On it: **253 pages at depth
> ≥ 4**, and **depth 1 is exactly the four pages named above**. Both answers
> are true and they answer different questions — SERVED is the honest one for
> **discovery** (max depth 3 with JavaScript off, which Phase 7 bought), CONTENT
> is the honest one for **link equity**, because search engines discount
> sitewide boilerplate. **Cite which graph.**
>
> The third graph was added rather than the pair reinterpreted: **a metric that
> changes meaning silently is worse than one that is missing.** Wave 4.7 stays
> open.

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

~~**`logo/` and `old-logos-archive/` are repo storage, not published assets** —
Eliot, 2026-08-09, D28. 30 files, 2.4 MB, **0** references anywhere on the site and
**0** rows in any GSC export. The recommendation is to exclude both in
`_config.yml`.~~ **Do not point `EducationalOrganization.logo` at them; use the
root `android-chrome-512x512.png`,** which is already published and already named in
`site.webmanifest`. D29.

> **SUPERSEDED 2026-08-12, D38. Both directories are DELETED** — 31 files, not
> 30, and 2.47 MB — after Eliot confirmed he holds the originals elsewhere,
> which was the only thing keeping them here. The `EducationalOrganization.logo`
> sentence above still stands and is now unconditional: the root
> `android-chrome-512x512.png` is the target, and there is no longer anything
> else to point at. The 31st file was
> `old-logos-archive/favicon-assets/site.webmanifest`, a second live manifest
> nobody had found — PH10-060's class again.

**Four "unreferenced" diagram PNGs are the ground truth for a live SVG, and a
census cannot see that.** `comparative-advantage`, `game-theory`,
`trade-union-competitive` and `trade-union-monopsony` are named by no `<img>`
on any page, so `asset_census.py 6` lists them as referenced by nothing — but
each has a same-named SVG in `images/diagrams/svg/`, and the flashcards rule
above is that every SVG is verified against its ground-truth PNG. Wave 5.1 is
that verification for all 78 pairs. **Deleting these four would take 5.1 from 5
unverifiable SVGs to 9**, with no error at any point. D38 deleted the other six
and kept these; do not re-propose them on the strength of the census line.

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
`verify_glossary.py` check 7 and CLAUDE.md disagreed; the script has been right
all along. PH10-061. Prefer citing the command over restating the number.

> **Amended 2026-08-12, Wave 3.2, and the amendment is the point.** This entry
> recorded the check as printing `44/44` against CLAUDE.md's 46. It prints
> **`43/43`** today — so the number written down to illustrate a stale number
> had itself gone stale, in the register that warns about it. The rule survives
> and the figure is deleted rather than replaced: cite
> `python3 scripts/verify_glossary.py`.

## The build step (added by Wave 2, 2026-08-11)

**`notes-data/` and `boards-data/` are source, and `_config.yml`'s `exclude` is
the only thing keeping them off the site.** Both went into that list in the same
commit that created them, per the rule above. `compare_trees.py` assertion 1 is
what proves it: the published URL set stayed at 463 pages while the tree gained
over 300 files.

**`scripts/page_shell.py` owns the `<head>` for 446 of the 463 pages.** All five
generators import it.

> **Corrected 2026-08-11, Wave 2 Phase 7. It was written as 454 here, in
> CLAUDE.md, in PROGRESS.md and in D34, and it was never measured** — it is
> `463 − 9`, taken from D34's decision about the root pages. **17 pages are not
> generated:** the 9 root pages, the 5 `past-papers/` hubs and the 3
> `revision-notes/` non-topic pages. No generator writes the last 8; PH06
> planned the past-papers hubs as the Phase 3 pilot and the notes hubs were
> migrated instead. `verify_page_shell.py` prints the split on its first line,
> so cite the script. A change there reaches every page on the next rebuild,
which is the point — and is also why it must not grow page-specific behaviour.
Everything that varies per page is passed in as a value.

> **The values it lifts are not tidiness waiting to happen.** Each was measured
> and each would rewrite pages if "normalised" without a decision:
>
> - **Two preconnect lineages.** ~~All 273 generated pages put the font
>   preconnect **before** `<title>`; all 190 hand-written pages put it after the
>   favicons. Earlier is better for the preload scanner, so the generated
>   families are right and the hand-written ones are the laggards.~~ Do not
>   "align" them without measuring LCP.
>
>   **MEASURED 2026-08-13 AND DELIBERATELY NOT ALIGNED. The counts hold and
>   both of the sentences around them were wrong.** "Hand-written" is wrong:
>   173 of the 190 late pages are GENERATED, by `build_notes_pages.py` — the
>   split was written in Wave 2 and Phases 3 and 5 made the notes pages
>   generated underneath it. It is a per-page value,
>   `page_shell.preconnectEarly`, not a property of being generated.
>
>   **And "earlier is better" does not survive measurement here.** Every one
>   of the 463 pages carries its preconnect inside the first **4,145 gzipped
>   bytes**, either lineage, and **439 of 463 documents fit ENTIRELY** inside
>   TCP's ~14,600-byte initial congestion window. Both positions arrive in the
>   same burst, so there is no round trip between them to save. The largest
>   page, the AQA glossary at 70,907 B gzipped, still has its preconnect at
>   byte 325; its overflow is body, not head.
>
>   `docs/audit/scripts/harness/measure_preconnect.py` computes that and is
>   the evidence. **Its browser probe FAILED and its numbers must not be
>   cited** — in three configurations it could not distinguish *no preconnect*
>   from *preconnect*, so it cannot speak to where one sits. The script says so
>   itself and is kept for what it records about driving Chrome.
> - **Two explanatory comments.** The `4db232c` note is universal, 463/463.
>   `build_questions.py` writes a second one above its early preconnect on 173
>   pages. Both are correct; rewording either is a change nobody asked for.
> - **JSON-LD escaping differs by generator.** `build_past_paper_questions.py`
>   emits `\u2014` where the notes carry a literal em dash, on 87 pages. Both
>   are valid and parse identically. `jsonldAsciiEscaped` records which.
> - **The favicon trio moves**, on 17 of 463 pages, varying *inside* four
>   families. It is per page, not per family.
>
> **Two defects `page_shell.py` had and must not regain.** It filtered
> stylesheets to `/css/pages/`, which silently dropped
> `/css/vendor/katex/katex.min.css` and would have removed formula styling from
> 10 pages. And its `<style>` capture matched the `<style>` **inside** a
> `<noscript>`, emitting DO-NOT-BREAK's six protected blocks twice. Neither was
> reachable from the hand-written pages; both were found by measuring the
> generated ones before editing them.

**The content is moved by slicing bytes. It is never parsed and re-serialised.**
`extract_notes_pages.py` finds two offsets and copies what is between them, which
is why all three of PH06-031's malformed pages migrated untouched. **No generated
notes page is run through Prettier**, deliberately: Prettier is a
parse-and-re-serialise, and reflowing a slice containing prose can move a line
break across an inline tag boundary and turn `<strong>word</strong>s` into
"word s". Do not add it.

**`docs/audit/scripts/harness/compare_trees.py` is the gate, and its test suite
is what makes it evidence.** 39 cases break each of the ten assertions on
purpose, and **twelve of them expect a PASS** — pinning what each assertion is
deliberately blind to, each paired with the assertion that covers it. An
assertion that fires on everything is as useless as one that fires on nothing.
Do not delete the passing cases as redundant.

**Assertion 10 requires NEW to be a git tree and fails without one.** Seven of
the fourteen verifiers it runs enumerate through `git ls-files`. Running the
other seven and reporting a pass is exactly the "green for the wrong reason"
this harness exists to prevent.

**`verify_page_shell.py`'s EXPECTED tables fail on a count going DOWN as well as
up.** An improvement is welcome and must be declared: change the page and the
number in the same commit, so the diff records what improved. `--show` reprints
the tables for reseeding.

**`boards-data/boards.json` records names per consumer, not one canonical name.**
Theme 2 reaches published output as three different strings — em dash in
`taxonomy.json` and the notes hub `<h1>`, hyphen in the flashcards decks, and the
short form in practice-questions. Collapsing them would silently rewrite visible
text on a whole page family. `verify_boards.py` compares the record against the
code and **the code wins**: a disagreement means the transcription is wrong.

~~**Nothing imports `boards.json` yet.** Wave 3.2 repoints the 113 board literals
in 11 scripts, one generator per commit, each with its output proved unmoved.~~

> **SUPERSEDED 2026-08-12, Wave 3.2, D39. Five generators read it now**, through
> `scripts/board_data.py`. The 113 was unreproducible and so was
> `PH11-synthesis.md` §2's 111: the real edit surface was **107** board-data
> literals in 5 scripts. Cite `python3 scripts/verify_boards.py`, not a number.
>
> **`scripts/verify_boards.py` keeps a second copy of the record, and removing
> it disarms the check.** Its four code comparisons are now circular for every
> swapped generator — they ask whether `boards.json` agrees with a structure
> `boards.json` produced, and agree with any value including a wrong one. Check
> 0 compares the record against `PINNED`, an independent restatement of all 82
> leaves in a deliberately different shape. Same argument as
> `verify_page_shell` check 2 not importing `SCRIPT_TAIL`. **Changing a board
> name or slug is a two-file commit**; `--show` reprints the table. Do not
> "remove the duplication".
>
> **`scripts/board_data.py` must never grow a canonical accessor.** It hands
> back the record and lets each caller name the field it wants, because a
> helper meaning "the name of a group" is exactly the collapse the paragraph
> above forbids. All three of Theme 2's spellings are live and were each proved
> to reach a different page family: `names.taxonomy` (em dash) →
> `taxonomy.json`, `names.flashcards` (hyphen) → the decks,
> `names.practiceQuestionsButton` ("Theme 2: The UK Economy") → the hub button.
>
> **`board_data.EXPECTED_KEYS` and `EXPECTED_NOTES_DIRS` exist because the
> record's ORDER is published output.** `build_questions.BOARD_ORDER` is the
> group order's index and it sorts the topics on every board index page, so a
> reordered `boards.json` would silently reorder a page. Same property as
> `build_past_paper_taxonomy.EXPECTED`.
>
> **Five recorded fields are read by no code** — `slugs.questionBank`,
> `slugs.dataDir`, `specCodesAreReal`, each group's `names.flashcards`, and
> `build_glossary`'s board-level `notesUrl`, which is dead in that generator and
> was dead before the wave. `PINNED` stops them drifting against the record;
> nothing proves they still match what they were transcribed from.
> **`slugs.dataDir` is also incomplete** — Edexcel A has two past-paper data
> directories, `edexcel-a` and `edexcel-a-as`, and the record names one.
> **CLOSED 2026-08-12, D40: it stays that way.** Recording the second means
> inventing a shape the record does not have, and Eliot judged a second AS-Level
> board unlikely. The hardcoded triple in `build_past_paper_questions.py:64` and
> `verify_past_paper_tags.py:44` is the correct home for that list. Do not
> "fix" it.

## The baked header and footer (added by Wave 2 Phase 7, 2026-08-11)

**`templates/header.html` is now copied into 463 files, and
`verify_page_shell.py` check 9 is the only thing keeping them one file.** It
lifts the block back out of every page, removes the uniform indent and the one
`class="current"` the page adds, and requires what is left to equal the
template **byte for byte**. It also asserts 0 published pages still carry a
runtime placeholder. Do not make it tolerant of whitespace: `page_shell.bake()`
emits the template verbatim and never reformats it, so there is no legitimate
reason for a byte to differ, and a forgiving check would forgive a Prettier run
that had quietly rewrapped a nav label.

**Editing the nav is a rebuild.** Edit the template, run the five generators,
run `scripts/bake_templates.py --apply`, run `build_sitemap.py`. Running only
one half leaves the site with two different navs and check 9 fails. The command
sequence is in CLAUDE.md. Accepted by Eliot on 2026-08-11, re-confirming D18.

**The bake runs AFTER Prettier, never before.** Prettier is a
parse-and-re-serialise; run over the block it rewraps the nav's markup and the
block stops being byte-comparable with its template, which is check 9's whole
basis. `build_notes_pages.py` bakes inside `render()` instead, because it
deliberately runs no Prettier at all.

**`scripts/bake_templates.py` carries `EXPECTED = 17` and refuses to run if the
page set has moved.** Same property as `build_past_paper_taxonomy.py`'s
`EXPECTED` dict: a new hand-written page must be declared rather than silently
skipped. A skipped page is a page with no navigation.

**The `class="current"` is written at build time and must stay that way.**
`#nav > ul > li.current > a` sets `font-weight: 700`, which changes that item's
width, so applying the highlight after load is itself a layout shift. It cost
nothing while the whole nav arrived at once; on a baked page it would be a new
shift. `PAGE_MAP` in `page_shell.py` is the rule list, moved there verbatim
from `setActivePage()`.

**`js/components/inject-templates.js` injects nothing and keeps its name.**
Renaming it to `nav.js` was built, harnessed and reverted: it edits 463 pages
and changes a published asset URL to gain a filename, which is the trade
`css/fontawesome-all.min.css` already declined above. Wave 4.10 rewrites the
file and the script tail together and the rename is free there. **Check 2 is
therefore NOT what proves Phase 7 reached every page — check 9 is.**

**PH08-043 is wrong on detail, and 4.10 should not be planned from it.** It
says removing the runtime fetch removes one of jQuery's three consumers. It
does not: of the file's 11 jQuery calls, 9 are in `initNavigation()` and 2 are
the bootstrap; the fetch and the nav highlight were already vanilla and used
none. What Phase 7 actually leaves for 4.10 is a 121-line file that is nothing
but nav plumbing, with no async injection sequence to preserve.

**`_working/flashcards/qa/`'s QA pages still carry placeholders** and now show
an empty div where the header was. They are unpublished frozen records of the
flashcards work. Baking them would create copies of the nav that check 9 does
not cover, which is the drift this phase removed. Left alone deliberately.

## The navigation, without jQuery (added by Wave 4.10, 2026-08-11)

**`page_shell.SCRIPT_TAIL` is the one declaration of the script tail, and
`verify_page_shell.py` check 2 deliberately does NOT import it.** Check 2
restates the same four scripts as its own literal, so changing the tail has to
change two files in the same commit — the `build_past_paper_taxonomy.py`
`EXPECTED` pattern. A check that reads the value it is checking agrees with any
value, including a wrong one. Do not "remove the duplication".

**Check 2 also asserts that 0 of 463 pages load anything in
`REMOVED_SCRIPTS`, and that assertion is not redundant.** The ordering test
beside it filters the page's scripts to tail members, and removed scripts are
not members any more — so a page that still loaded jQuery would pass the
ordering test in silence. Removing anything from `SCRIPT_TAIL` means adding it
to `REMOVED_SCRIPTS` here and to `bake_templates.LEGACY_TAIL`, or the 17
hand-written pages keep loading it after the other 446 have stopped.

> **Amended 2026-08-12, Wave 4.11.** The list was four and is six, and the
> line check 2 prints now counts `REMOVED_SCRIPTS` instead of naming its
> members — the sentence that named four went stale the moment two were added,
> which is the same failure this register records for CLAUDE.md's counts.
> **Proved able to fail rather than read:** re-adding one `browser.min.js` tag
> to `about.html` turns check 2 red three ways while the ordering test beside
> it stays green, which is this paragraph demonstrated rather than asserted.

**The script tail is two scripts, and the number is the wrong thing to
remember.** Seven until 2026-08-11, four until 2026-08-12, two now. Cite
`page_shell.SCRIPT_TAIL`. Removing one is a **four-file** edit —
`page_shell.SCRIPT_TAIL`, `verify_page_shell.SCRIPT_TAIL`,
`verify_page_shell.REMOVED_SCRIPTS`, `bake_templates.LEGACY_TAIL` — then the
five generators, `bake_templates.py --apply`, and `build_sitemap.py`.

**The closed `#navPanel` is `inert`, not `aria-hidden="true"`, and the two must
not both be set.** Wave 4.11, D37. The panel is off-canvas by `transform`
rather than `display: none` because the slide is animated, so before this its
32 links stayed in the tab order the whole time it was shut, while
`aria-hidden="true"` on an element with focusable descendants was an ARIA 1.2
conformance failure Chrome logs. `inert` removes it from both the tab order and
the accessibility tree. **Do not add an `aria-hidden` fallback for browsers
without `inert`:** that reinstates the conformance failure for exactly those
users, and it was declined on that ground rather than overlooked.

**`render_nav.py`'s `tabbable` field is the only thing that can see that**, and
anything touching the panel's open/close must keep it honest. `inert` changes
no markup, no link, no class and no transform, so all ten of the harness's
other fields compared identical across the change. `tabbable` focuses each
panel link in turn and counts how many accept it, **closed then open then
closed again on the same run** — 0/32, 32/32, 0/32 today. The middle reading is
not decoration: without it the zero is indistinguishable from a broken probe,
which is exactly what the `render_nav.py` entry at the end of this section
records happening to a CLS measurement.

**`scripts/bake_templates.py` owns the script tail on the 17 pages no generator
writes, as well as the header and footer.** Same argument as Wave 2 Phase 7:
without it `/past-papers/edexcel-b/` and `/past-papers/ocr/` — 291 clicks and
21,131 impressions between them, PH03-049 — would have gone on requesting a
jQuery that is no longer in the repo.

**The desktop dropdowns are CSS, and `js/components/nav.js` is an enhancement
on top of them, never a dependency.** `:hover` and `:focus-within` open the
menus; `nav.js` adds `.nav-open` for touch and handles Escape. That ordering is
what makes the dropdowns work with scripting off — which they never did under
dropotron — so do not move the opening logic into the script.

**`transform: translateX(-50%)` centres the dropdown, never `margin-left:
-50%`.** A percentage margin resolves against the containing block — the `<li>`
— not against the panel's own width, and the panel sat 32px right of its item.
Because the open/close lift also uses `transform`, every transform in that
block names both axes; changing one and not the other un-centres the menu.

**The invisible `:after` strip above each level-0 dropdown is load-bearing.**
It bridges the gap between the nav item and the panel. Without it the pointer
leaves both elements on the way down and the menu closes; dropotron papered
over the same problem with a 250 ms hide delay. Shrink the gap and the strip
together, or not at all.

**The chevrons are drawn in CSS on purpose.** `css/fontawesome-all.min.css` and
`webfonts/fa-solid-900.woff2` are subsets, and a subset font renders a missing
glyph as nothing at all, with no error — the failure mode recorded above from
Wave 4.2. A CSS chevron needs no glyph and no re-run of the subsetter. It is
selected with `:has()`; where that is unsupported the chevron is simply absent,
which is the correct degradation.

**The mobile panel's `current` class is copied off the baked
`<li class="current">`, not re-derived from the URL.** `PAGE_MAP` in
`page_shell.py` decides which nav item is current, at build time; `nav.js`
reads that decision rather than making a second one. A URL-matching rule in the
script would be a second source of truth that can disagree with the first on
exactly the pages where it matters. It reads the **direct parent only** — the
current `<li>` contains its whole submenu, so `closest()` marks eleven links
instead of one.

**`docs/audit/scripts/harness/render_nav.py` is what covers behaviour, and
`compare_trees.py` cannot replace it.** The ten assertions read committed bytes;
the mobile `#navPanel` exists in no file, being built from `#nav` at
DOMContentLoaded. All ten assertions pass on a site whose menu no longer opens.
Four things it records that were learned the hard way and must not be undone:

- `subprocess.run()` cannot be used to drive Chrome. It writes the DOM and does
  not exit — its updater and crash-handler children inherit the stdout pipe —
  and it hangs on `data:text/html,<h1>hi</h1>` as readily as on a real page,
  intermittently. Poll a file, then kill the process group, swallowing
  `PermissionError` as well as `ProcessLookupError`.
- A single-threaded `http.server` deadlocks against Chrome's parallel
  connections and every page times out.
- Chrome's animation clock does not advance under `--virtual-time-budget`, so
  `getComputedStyle` during a transition returns the FROM value forever, and
  **no `layout-shift` entry is ever generated**. A CLS probe run that way
  reported 0.0000 for a deliberate 200px shift. The nav probe disables
  transitions before interacting; anything measuring CLS must abandon virtual
  time and POST its result back to the server instead.
- dropotron answered only the FIRST synthetic hover of a page. A loop over the
  three openers reported "no dropdown" for two of them and would have passed by
  being blind rather than by being right.

## The deliberate normalisations (added by wave-norm, 2026-08-13)

**`page_shell.ORGANISATION_REF` is the one declaration of the publisher, and
callers name the PROPERTY.** Four generators emit it. There is deliberately no
helper meaning "the publisher bit of a page", because the right property
depends on the node it attaches to: 105 of the 107 pages take `publisher`, and
`marking.html` and `tutoring.html` are `Service` nodes taking `provider`,
which is what `Service` defines for the same relationship. Same argument as
`board_data.py` never growing a canonical accessor.

**`isPartOf` references are NOT page entities, and that rule now covers two
properties, not one.** The register already said it of the 179 `Course` nodes.
PH04-052 asks for the 99 `WebSite` nodes to be deleted on the grounds that
they are site-level entities occupying the publisher's slot. **Measured: 1 is
a top-level entity — `index.html` — and 99 are the value of an `isPartOf`
property**, which is the standard way for a page to say it belongs to a site
and does not compete with `publisher`. `privacy.html` carries both, correctly.
**Item (i) is dropped, D42.** Do not re-propose it from the finding's wording.

**`verify_markup_integrity.py` has a `Markup-Change:` trailer, and it declares
a PATH, not a TAG.** Same three properties as `Text-Change:` and for the same
reason — a commit-message declaration applies to exactly one commit, cannot be
left on by accident, and stays in `git log`. A declared path still PRINTS
every loss; it is not silenced, only not counted. A commit that means to drop
one `<section>` and also drops an `<a>` from the same page still fails.

**The three real `<style>` blocks are gone and the six protected ones are all
that remain.** 0 real, 6 inside `<noscript>`. The two diagram galleries share
`css/pages/revision-notes-diagrams.css` — they were the same file twice, 3,502
bytes each, differing only in `.macro-` against `.micro-`, so each rule carries
both scopes rather than being duplicated. **The `.comp-spectrum` rules were
scoped to `.revision-notes-content` on the way into
`revision-notes-textbook.css`**, because a bare class name in a sheet 179 pages
load is the collision the house rule exists to prevent.

**One MathJax markup on 126 pages, and `$…$` is not a delimiter anywhere.**
D23. `page_shell.MATHJAX_CONFIG_BODY` is the only config and every
`notes-data` record has `mathjaxConfig: null`. `displayMath`'s `["$$","$$"]`
deliberately stays: pairing needs two ADJACENT dollars and there are none
among the 8 literal `$` on the site, all of which are currency.

**`verify_page_shell.py` check 5 counts POPULATED labels, not labels.** The
`<style>` label is held at 0 as a tripwire for a block coming back, and
counting it would demand a shape that is meant not to exist. Proved live in
both directions.

## Inline styles, after item (f) (added 2026-08-13)

**The 1,187 KaTeX inline styles survived the sweep and are now ASSERTED, not
merely avoided.** `scripts/verify_inline_styles.py` is the workflow's 9th step
and pins them **per page** across the 7 pages that carry them — the two
glossary pages and five flashcard decks — so one page losing 20 while another
gains 20 cannot cancel out. Classification is **by construction**: an
attribute is KaTeX output if it sits inside an element whose class list holds a
token beginning `katex`. Never by page path. All four of its failure paths were
tested by breaking each one deliberately. Cite the script, not the 1,187.

**AUTHORED INLINE STYLES ARE 0 AND THAT IS AN ASSERTION.** 322 across 44 files
became 0 on 2026-08-13. There is deliberately no allowlist: CLAUDE.md admits no
exception, so the right shape is a bare zero, and a genuine need for one is a
`DECISIONS.md` entry plus a named exception here — not a number to nudge.

**EXTRACTING AN INLINE STYLE IS NOT A RENAME, AND `compare_trees.py` CANNOT
SEE THE DIFFERENCE.** An inline style outranks every class selector, so the
class can lose to a rule the attribute was beating. Assertion 4 fires only on
LOSSES and an attribute becoming a class is a loss of nothing; assertions 2, 3,
6 and 7 never look at CSS. **Two of item (f)'s last 35 attributes moved the
rendered page and all ten assertions passed both:**

- `tutoring.html` lost 44px. `css/main.css`'s `section > :last-child {
  margin-bottom: 0 }` is **(0,1,1)**; a lone class is (0,1,0) and loses. Fixed
  as `.row.tutoring-intro-row`.
- `404.html` gained 14.67px per link row, the other way. `css/main.css:3415`'s
  `#main .row > div[class*="col-"]` is **(1,2,1)**, and **no number of bare
  classes beats a selector containing an ID.** Fixed as
  `#main .row > div.error-link-col`.

Both rules carry a comment saying so. **Do not "simplify" either selector.**

**`docs/audit/scripts/harness/computed_style_diff.py` is what measures it**,
and `compare_trees.py` cannot replace it — same relationship as `render_nav.py`
for the mobile panel. It serves each tree from **its own origin** and compares
every computed property on every element in a real browser. Four things it
records, each of which cost a false result:

- **One origin per tree is the whole thing.** Every asset path here is
  root-absolute, so serving both trees under path prefixes on one origin sends
  both iframes to the *same* `/css/main.css` and the probe reports 0
  differences whatever changed. That is what its `--selftest` caught on the
  first run. Two origins means cross-origin frames, hence
  `--disable-web-security`, hence `--user-data-dir` being mandatory.
- **`--hide-scrollbars` and a resolver rule refusing every host but
  127.0.0.1.** Without them `.container`'s `margin: 0 auto` resolved
  differently on two IDENTICAL trees, because Calendly's arrival time decided
  the page height and so whether there was a scrollbar.
- **`--body-only` for a page that deliberately gains a `<head>` element.**
  Elements align by document index, so 404.html's one new `<link>` shifted
  every index and the page was SKIPPED with `element count 199 -> 200` — an
  uncompared page inside a run whose last line said PASS. That is
  `--max-report 0` again. The second regression above was invisible until this
  existed.
- **Run `--selftest` whenever the answer is 0.** It appends one declaration to
  a copy of NEW's `main.css` and requires the probe to see it.

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

   > **THE SWEEP HAPPENED, 2026-08-13, and this entry held.** Item (f) took
   > authored inline styles 322 → 0 and touched **none** of the 1,187: they are
   > still on the same 7 pages, count unchanged, and are now asserted per page
   > by `scripts/verify_inline_styles.py` rather than merely left alone. The
   > exclusion was by construction — a `katex` class token — exactly as this
   > entry demanded, and it was sensitivity-checked four ways before being
   > believed, because "0 authored on the KaTeX pages" is a zero that has to be
   > earned. The six `<noscript>` blocks were never in scope; the three real
   > `<style>` blocks went in the previous wave. **See "Inline styles, after
   > item (f)" above for what the sweep cost — two silent cascade regressions,
   > both invisible to all ten harness assertions.**
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
python3 scripts/verify_inline_styles.py   # 0 authored; 1,187 KaTeX on 7 pages
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
