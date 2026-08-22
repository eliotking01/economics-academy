# Site Work — Progress

**The single record of what has been built on this site, and the entry point
for a fresh session — read this first, then CLAUDE.md.** Excluded from
publishing via `_config.yml`.

One section per project, newest first. The exhaustive per-item wording lists
each branch carried for review live in this file's own git history, not here.

Reorganised 2026-08-16 when the site-wide overhaul finished. **On 2026-08-20 it
absorbed `PROJECT-LOG.md`**, which covered the five older projects and is now at
`_archive/PROJECT-LOG.md`. Everything of its that was still true is in §5–§9 and
in "What remains flagged" below; most of its flagged list had quietly been
fixed without the file being updated, which is why that list is now dated and
says how each line was checked.

## The overhaul at a glance

| Project | State | Merged | Merge commit |
| --- | --- | --- | --- |
| About + Contact + finishing pass | live | 2026-08-16 | `437dc7e` |
| Resource unification, Phases 1–4 | live | 2026-08-15 | `d0fdcaf`, `2295213`, `1e8dfed`, `f537312` |
| Marking page + payment journey | live | 2026-08-15 | `d4be06b` |
| Home page revamp | live | 2026-08-14 | `f53b7fe` |
| Tutoring page SEO rework | live | 2026-08-14 | `e09cdef` |
| Flashcards | live | 2026-08-15 | §5 |
| Glossary & formulae | live | 2026-08-09 | §6 |
| Past paper question bank | live | 2026-08-13 | §7 |
| Free practice questions | live | 2026-08-01 | §8 |
| Notes consistency & enrichment | live | 2026-08-01 | §9 |

Everything Eliot still has to do himself is in OWNER-TODO.md (consolidated
2026-08-16). The ~22 September 2026 GSC check and its baselines are recorded
there.

## Traps every future session must know

1. **Prettier reformats the BAKED HEADER inside root pages** — always run
   `python3 scripts/bake_templates.py --apply` AFTER Prettier. And never run
   Prettier over `revision-notes/index.html` at all without re-splicing its
   frozen head back to main's exact bytes.
2. **Any commit changing visible wording on a published page needs one
   `Text-Change: <path>` trailer per page** in the commit message's final
   trailer block, or CI fails. Merge with a merge commit, NOT a squash, so CI
   sees the trailers across the range.
3. **Any commit touching `revision-notes/` markup**: run
   `python3 scripts/verify_markup_integrity.py <base> --strict` locally and
   declare `Markup-Change:` per page alongside `Text-Change:`.
4. Root pages are hand-written (out of page_shell scope, D34) — edit
   directly. Generated pages are never hand-edited — rerun their generator.
5. Run `python3 scripts/build_sitemap.py` AFTER committing page edits (it
   takes lastmod from git) and commit the sitemap separately.
6. Only icons already in `css/fontawesome-all.min.css` may be used (15 solid
   icons; no brand icons — LinkedIn is a text button for this reason).
7. **A bare class selector can silently lose to main.css's grid rule**
   `#main .row > div[class*="col-"]` (specificity 1,2,1) — the contact form's
   honeypot rendered visibly until its selector was raised to match. Check
   computed style in a real render for anything that must be hidden.
8. The GSC-frozen heads (`<title>`, H1, meta description, canonical):
   `/revision-notes/`, the four past-papers board pages, marking.html,
   index.html's title, tutoring.html's title. about/contact/faq heads are
   tunable but their og:description must stay a shortened variant
   (`KNOWN_SELF_DISAGREEMENT` in verify_page_shell.py) or leave that list in
   the same commit.
9. **Search Console's Pages report LAGS its own Crawl stats by days.** Every
   verdict in a page-indexing export is only as fresh as the `Last crawled`
   date on that row, so **read that column before believing the verdict**. On
   2026-08-21 the export implied no PDF had been crawled since 6 August while
   Crawl stats showed a spike of ~128 PDF requests a day on 8–9 August — and
   the audit reached a wrong conclusion before the graph was checked.
   `seo/tools/gsc_reconcile.py` now flags any verdict older than the file's
   last commit automatically.

## Revision notes on-page SEO (2026-08-21) — branch `seo/notes-onpage-audit`

**Unnumbered, for the same reason the two sections below it are.**

**STATE: committed on `seo/notes-onpage-audit`, NOT pushed, awaiting Eliot.**
Three commits plus the reports. Full verification suite green including five
new `verify_seo.py` assertions; `verify_generated.py` proves the committed tree
is what the generators produce.

The 166 topic pages, their 7 hubs and the 2 diagram galleries — 176 pages,
counted by `python3 seo/tools/notes_baseline.py`. Every one of the 166 titles
put the topic name LAST, behind a board and a spec code earning 4 impressions
in 28 days. They now put it first.

### What was applied

| | |
| --- | ---: |
| Titles rewritten to the brief's formula | 166 topics + 7 hubs |
| Descriptions rewritten and front-loaded | 166 topics + 7 hubs |
| `LearningResource` nodes gaining dates, author, audience, alignment | 173 |
| `<h2>` elements gaining a stable `id` | 1,159 |
| Pages gaining a contents list, a spec sub-label and an update date | 166 |
| Twin-board links, where none existed at all before | 109 |
| New internal links | 508 |
| New `verify_seo.py` assertions | 5 (15–19) |
| **Published URLs moved** | **0** |
| **Words of economics wording changed** | **0** |

`verify_text_integrity.py` reports 0 removals across the 166: every difference
is an addition. The seven new visible strings are chrome and are listed at the
top of `scripts/notes_extras.py`.

### Three things a future session needs to know

1. **`scripts/notes_twins.py` is a written-down table, not a derivation, and
   that is deliberate.** Nothing in this repo owns the mapping between an
   Edexcel topic and its AQA counterpart, and the spec code is the trap — 37
   codes are claimed by both boards with different meanings. Each row carries
   the measured prose similarity that seeded it; the eight hand corrections say
   which and why. `verify_seo.py` assertion 13 was AMENDED to permit exactly
   those pairs and nothing else, so a cross-board link the table does not name
   still fails.

2. **The contents list is on all 166 and not on the 95 that want one, because
   of `verify_page_shell.py` check 6.** Gating it on "four or more sections"
   takes the content spine from 6 shapes to 12 and gives two pages a shape of
   their own. That check exists to catch a malformed page and its declared
   singleton set is empty. The block goes everywhere and the spine stays at
   (97, 29, 16, 11, 7, 6).

3. **The dates are STORED in `notes-data/`, not read from git at build time.**
   `verify_generated.py` re-runs every generator in a throwaway worktree, so a
   generator that shelled out to `git log` would answer differently there and
   fail a correct commit. `seo/tools/rewrite_notes_meta.py` does the git
   reading, once; re-run it to refresh a `dateModified`.

### Eliot's four decisions, 21 August 2026

Taken after the audit was delivered, on items 1, 7, 8 and 9 of the approval
document.

| Item | Decision | State |
| --- | --- | --- |
| 1. Strip the spec code from the 79 AQA `<h1>`s | **"strip them"** | **DONE**, commit `94a0726`. Lifts DO-NOT-BREAK PH05-021; DECISIONS.md D53 |
| 7. Add key terms to the pages that define none | **yes; wrote three, approved a fourth** | **DONE**, commit `60da40a`. Four chips on three pages; 1.3.6 deliberately left |
| 8. The 17 pages under 500 words | **"I can expand these"** | Eliot's; manual list task 20 |
| 9. Diagrams on the 72 diagram-less pages | **"I'll add diagrams"** | Eliot's; manual list task 21 |

**Item 7 corrected a mistake in the audit's own reporting.** "Twelve pages
define no term" counted pages carrying a `key-definition` chip, which is a
GLOSSARY signal — Google does not read `class="key-definition"`. Read one by
one, eight of the twelve already answer "what is X" in their opening or have a
topic that is not a definable term. **The real gap is four pages.** Looking
properly also found a better item: five pages carry fourteen definitions Eliot
has already written, sitting under a plain `<strong>Term:</strong>` where the
extractor cannot reach them. Converting them adds fourteen glossary entries and
changes not one word — manual list task 19.

### What is still open

**Everything that changes a word a student reads** —
`seo/18-notes-content-approval-2026-08-21.md`. Items 1, 8 and 9 are decided
(above); item 3 closed 2026-08-22 — Eliot approved spelling out the five
abbreviated titles, WTO deliberately kept. Items 2, 4 to 6 and 10 to 12 are
read-and-confirm rather than blocking.

**Five things only Eliot can do**, appended to
`seo/15-notes-seo-manual-todo-2026-08-21.md` as tasks 13–17: a live web-vitals
re-run after the push, looking at a page in a browser, reading the twin map,
deciding the AQA heading question, and noting the date when rank-checking.

**The author byline** is task 4 of that list and remains the highest-value
item on it. Every competitor that outranks this site on these queries has a
named author with credentials; these pages do not.

### Where it lives

| File | What it is |
| --- | --- |
| `seo/17-notes-seo-audit-2026-08-21.md` | the audit, with the 72-row diagram table and the SERP comparison |
| `seo/17-notes-baseline-2026-08-21.csv` / `-after-` | before and after, one row per page |
| `seo/18-notes-content-approval-2026-08-21.md` | the twelve decisions needing Eliot |
| `seo/19-notes-url-rename-proposal-2026-08-21.md` | 176 rows, and why not to do it |
| `seo/tools/notes_baseline.py` | regenerates either CSV |
| `seo/tools/notes_titles.py` | the formulas, imported by the rewriter AND the verifier |
| `seo/tools/rewrite_notes_meta.py` | re-runnable; refreshes `dateModified` |
| `scripts/notes_extras.py`, `scripts/notes_twins.py` | the four blocks and the twin map |

### Deliberately not done

`scripts/intentional-changes.json` is not extended. `compare_trees.py`
assertion 5 governs `<head>` field equality and 166 pages × six fields is ~996
entries — for a script `verify.yml` states outright is not a step. Eliot chose
the written record over the ritual; `docs/audit/DECISIONS.md` D51 carries it.

## Previous / next topic navigation (2026-08-21) — branch `feature/topic-prev-next-nav`

**Unnumbered, for the same reason the section below it is.**

A previous/next row at each end of the notes body on all **166 topic pages**,
so a student who finishes one set of notes moves straight to the next instead
of going back to a hub. Two chains, never joined: Edexcel A runs theme 1 → 2 →
3 → 4 (87 pages) and AQA runs micro → macro (79). At the two ends of a chain
the spare slot points back at that page's own hub. Out of scope and untouched:
the seven hubs, `revision-notes/index.html`, the glossary, both diagram
galleries and `macro-application/`.

**The chain is derived, not stored.** `scripts/notes_sequence.py` takes the
directory order from `boards-data/boards.json`, the topic order and every
label from each hub's own links, and the chain lengths from the board's own
`expectedTopics`. Nothing is written down twice, so nothing can drift apart —
and `scripts/verify_notes_sequence.py`, now in CI, is what holds those three
sources together. It fails if a topic page has no place in the sequence, if
the sequence names a page that does not exist, if a hub's order stops being
spec-code order, or if navigation appears on a page outside the 166.

**The markup lives in the generator, not in the 166 slices.**
`build_notes_pages.py` splices it against two anchors that were measured
across all 166 first. `notes-data/topics/*.html` is still a verbatim byte
slice and is still never written to.

**No new economics wording.** Every topic label is the hub's own anchor text,
reused verbatim. The only new visible strings are three captions — "Previous
topic", "Next topic", "Topic list" — approved 2026-08-21. The same approval
fixed one typo carried by a hub label since it was written: Theme 2's 2.6.4
read "Polciies".

**The two rows are not styled alike, and that is deliberate.** The top row is
the only thing between the breadcrumb and the `<h1>`, so it is compressed, and
**below 768px it shows its captions only** — one side-by-side line, a flat
50px, instead of two stacked cards at 182–242px. Measured in Chrome, not
estimated: the row was pushing the heading down by 111–131px on desktop and
219–279px on a phone, and is now 57–97px on both. The titles there are hidden
rather than truncated; each link's `aria-label` still names its topic in full
and the bottom row shows both titles. Do not "restore" the titles at the top
on mobile without re-measuring.

No published URL moved; no file was added, removed or renamed under a
published path. 332 new internal links, all notes → notes, every anchor string
distinct, so `seo/07b-link-decisions.md` §5 is untouched. It takes lateral
linking inside the notes section from 53.6% to 100% on these 166 pages.

## SEO / indexing — Search Console index audit (2026-08-21) — REPORT ONLY

**Unnumbered deliberately.** The numbered sections below are the site-overhaul
projects and the "at a glance" table cross-references them by number, so
renumbering to squeeze this in would break those links. This is also not a
build project — **no published page was changed**, and
`verify_text_integrity.py` confirms 0 visible-text differences.

**State: committed `bb020d8`, pushed 2026-08-21.** Everything it produced lives
in `seo/` and `docs/`, both excluded from publishing.

### What it found

Reconciled the 21 August Search Console export against the real published
surface — **746 URLs, 463 HTML pages and 283 PDFs** — derived by running the
scripts, not from any recorded count.

| | published | indexed | |
| --- | ---: | ---: | ---: |
| HTML pages | 463 | 308 | **66.5%** |
| PDFs | 283 | 11 | 3.9% |

The sitemap submission of 8 August worked: published-and-indexed went
**64 → 319** in a fortnight, and the newly-indexed pages earned 50 clicks and
3,316 impressions from a standing start.

**Two findings that matter beyond this audit:**

1. **The 26 URLs Search Console reports as "Excluded by 'noindex' tag" carry no
   noindex tag** and have not since 30 July. They were stub placeholders removed
   as each AQA page was finished; Google's last crawl of every one predates its
   own removal. Nothing to fix — it needs a recrawl.
2. **"Discovered — currently not indexed" (316 URLs) is a queue, not a defect.**
   Thin content, templating, link depth, orphans, sitemap structure and robots
   directives were each tested against repo evidence and eliminated. What
   remains is crawl demand: about **3,270 crawl requests to the whole site in
   90 days, four fetches per page**, at a 108 ms average response time.
   Capacity is not the constraint.

### Where it lives

| File | What it is |
| --- | --- |
| `seo/11-gsc-index-audit-2026-08-21.md` | the analysis, with full URL lists in appendices |
| `seo/12-index-fix-actions-2026-08-21.md` | repo actions, and an explicit "not worth doing" list |
| `seo/13-gsc-manual-todo-2026-08-21.md` | Search Console tasks, with what is already done |
| `seo/tools/gsc_reconcile.py` | **reproduces the whole audit from one command** |
| `seo/gsc-exports/<date>/` | the raw exports, one folder per date |

```
python3 seo/tools/gsc_reconcile.py seo/gsc-exports/21-08-2026 \
        --diff seo/gsc-exports/08-08-2026
```

`seo/00-inventory.md` through `seo/10-architecture-verification.md` are the
earlier eleven-phase audit and are still the reference for anything structural.
**`seo/06-gsc-checklist.md` is superseded by `13-…`** for the Search Console
side and says so at its head.

### Deliberately not done

`sitemaps/pdfs.xml` stays. Submitting it caused one crawl burst on 8–9 August
and indexed nothing, but there is no ongoing cost, so removing it now would
recover nothing. Re-decide 1 October on the indexing outcome; the change is
scoped and ready as Action 3 in `seo/12-…`.

## 0. About + Contact + site finishing pass — MERGED AND LIVE (2026-08-16)

**STATE: MERGED AND LIVE** (merge `437dc7e`, --no-ff, pushed 2026-08-16;
branch deleted). Both workflows succeeded — verify CI accepted the four
Text-Change trailers across the merge range, and the Pages deployment went
out. Live site spot-checked: About serving My Story / the softened stat /
testimonials / the LinkedIn button with its `<title>` byte-identical,
Contact serving the new form with the honeypot hidden, faq carrying zero
"on weekdays" remnants, the tutoring modal honeypot and all five `sameAs`
additions live. The brief: revamp About and Contact (the last two
unrevamped pages), then a whole-site finishing pass — the closing session
of the overhaul. Approved decisions: soften the "100%" stat, Harry G. +
Alex B. testimonials, one Name field on the form, plain "within 24 hours"
everywhere, LinkedIn into structured data sitewide. Eliot closed the
Formspree-dashboard and LinkedIn-link follow-ups on 2026-08-16; the only
one still open is his own My Story paragraph, at the top of OWNER-TODO.md.

### About page (about.html + css/pages/about.css)

Restructured around trust, keeping Eliot's own words (no new personal copy
written): hero (boat photo, existing intro, tutoring's trust line verbatim,
intro-call + tutoring buttons) → NEW quick-facts strip (online lessons /
four boards / DBS / 24-hour replies — all facts already on the site) → "My
Story" (existing bio paragraphs; an `OWNER COPY NEEDED` comment marks where
the finance→tutoring paragraph goes — writing brief in OWNER-TODO) + LinkedIn
button → Proven Results restyled to brand colours, "100% improve by 1+
grade" softened to "1+ grades / Typical improvement after a year of tuition"
→ the four method cards (one typo fixed: "revision note" → "notes") → NEW
testimonials (Alex B., Harry G. — Harry was the one review used nowhere on
the site; quotes verbatim from the deleted reviews.js in git history) →
credentials unchanged → closing CTA (intro call deep-linked to
`/tutoring.html#booking`, tutoring, marking, plus a low-key free-resources
line). Mid-page CTA removed (duplicated the closing one). The one other
wording change: "Hedge Funds and FinTech startups" (plural) → "a hedge fund
and a FinTech startup", matching home and tutoring. Head untouched except
Person/Organization JSON-LD gaining LinkedIn in `sameAs`.

### Contact page (contact.html + css/pages/contact.css)

Email promoted to the clear first route (primary styling, "Replies within
24 hours" stated confidently); Book-a-call card deep-links to
`/tutoring.html#booking`. Form: First/Last Name merged into one Name field;
the dropdown reworded to "What's this about?" (One-to-one tutoring / Group
lessons / Marking quote / Free resources / Something else), now required and
named `_subject` so the chosen option becomes the notification email's
subject line — enquiries arrive pre-sorted. Honeypot added (Formspree's
`_gotcha`, hidden by CSS — see trap 7). Side box rewritten: heading "What
Can Eliot Help With?", stale "25-marker" line replaced with the
current-offer wording, "we" voice → Eliot throughout, footer button now
"More About Eliot". Status messages updated to match. Head untouched.

### Finishing pass

- faq.html: all three "within 24 hours on weekdays" → "within 24 hours"
  (visible answer + its FAQPage JSON-LD copy + the bottom CTA box), so the
  promise reads identically sitewide.
- LinkedIn (`https://www.linkedin.com/in/eliotking`) added to the
  Organization `sameAs` on the five pages that declare the full record
  (index, tutoring, marking, about, contact) and to the Person record on
  about. faq/privacy only reference the org by `@id` — correctly left alone.
- tutoring.html enquiry pop-up: same hidden honeypot added (its Formspree
  form `mqadgbbw` had no spam protection either). No visible change; the
  modal focus-trap and submit handler were checked against the new field.
- External links all verified live: Kit, all 8 Stripe links, Calendly,
  Tutorful, ICO all 200; both Formspree endpoints 405-on-GET (expected —
  POST-only); LinkedIn 999 (blocks robots — Eliot clicks it once,
  OWNER-TODO). Internal links: verify_links green.
- OWNER-TODO.md consolidated into one prioritised list; this file
  reorganised into its final state.

### Verification (2026-08-16, before commit)

All nine `scripts/verify_*.py` green, `verify_generated.py` green (8
generators, 0 would change), `seo/tools/verify_seo.py` 14/14,
`verify_links.py` green. Headless-Chrome renders at 1280px and 390px (iframe
wrapper), both pages, visually checked — which is what caught the honeypot
rendering visibly (trap 7). `verify_text_integrity.py` run against the
branch after committing; every differing file declared with a Text-Change
trailer. Sitemap rebuilt after the page commits.

## 1. Resource unification, Phases 1–4 — ALL LIVE (2026-08-15)

One design language and full cross-linking across the four resource
sections. Phase 1 flashcards (hub + 6 decks), Phase 2 practice questions
(hub + 6 themes), Phase 3 past papers (hub + 4 board pages), Phase 4
revision notes (hub + 6 theme pages + 166 practice back-links). All four
phases merged --no-ff and spot-checked live. Full per-phase detail —
including every approved wording change — is in this file's git history at
merge `f537312` and earlier.

What a future session needs:

- The shared component set is the `.resource-*` block at the END of
  css/main.css (hero, stat strip, card grid, cross strip, services panel).
  Reuse it; don't fork it.
- Page ownership: notes hub + past-papers 5 pages are hand-written (baked by
  bake_templates.py); notes theme pages are notes-data slices via
  build_notes_pages.py; practice pages via build_questions.py; flashcards
  via build_flashcards.py; finder via build_past_paper_questions.py.
- The notes hub's `<head>` is FROZEN and Prettier mangles it (trap 1). The
  six per-card "Practise … questions" links must stay on the hub
  (DO-NOT-BREAK: only depth-1 page in the section).
- Wave 3.4 board labels were deliberately NOT applied to notes pages
  ("Edexcel" is unambiguous there); Eliot did not override.
- Phase 4 was the first branch to face `verify_markup_integrity.py` (trap
  3); the retroactive declaration is recorded in this file's history.
- boards.json group order wins wherever boards are listed (Phase 1 flipped
  the flashcards hub to Edexcel-first).

## 2. Marking page + payment journey — LIVE (2026-08-15, merge `d4be06b`)

marking.html rebuilt around four packages with direct 48-hour/next-day
Stripe buttons (8 links, all verified rendering the right product and
price); old click-to-select flow and email-capture panel deleted; new
custom-enquiry box, "What You Actually Get" section, six-box FAQ.
confirmation.html rebuilt around one job (email the work) — Formspree form
and reference numbers removed; matching is by email address. faq.html
prices updated in lockstep. The trust strip was removed at Eliot's request.

**The #1 guardrail held: marking.html ranks #1 for "Economics paper
marking"** — URL, `<title>`, H1, meta description, canonical, og/twitter,
breadcrumb all byte-identical; body copy, JSON-LD offers and UX only.

**The payment journey is now fully verified end to end**: Eliot confirmed in
the Stripe dashboard on 2026-08-16 that all 8 links redirect to
confirmation.html after payment — the one part nobody could check from
outside.

**Bundles are pay-once, submit-over-time (merge `91e4109`, 2026-08-16,
live and spot-checked):** most bundle buyers send one paper a week or ad
hoc, so every place the turnaround promise appears now says papers can be
sent together or spread out, with each returned within the chosen
turnaround of when it is sent — the packages intro, a bullet on both
bundle cards, the four bundle offers in the Service JSON-LD, the
"What happens after I pay?" box, confirmation.html's timeline, and
faq.html's three marking answers plus their FAQPage JSON-LD twins. Change
any of these and the other five must move in lockstep.

**The example panels are REAL now — nothing else is open on this project.**
Merge `fca6d93` (2026-08-16, both workflows green, live site spot-checked)
replaced the two "coming soon" placeholders with page-1 previews linking to
the full PDFs in `marking-examples/`: a matched pair from the same AQA
Paper 1 2019 (52/80, B — the annotated 8-page scan and the 2-page feedback
email describing it, cross-checked mark by mark). Eliot's first upload was
two different papers whose numbers contradicted side by side; he
re-exported and the pair now agree on everything. Anonymisation was
verified page by page before publishing. Previews are 800px JPEGs
generated with PDFKit via Swift; verify_page_shell's image expectations
moved to 106 pages / 312 images / 10 all-lazy in the same commit
(marking.html's two images are below the fold, so it joined the all-lazy
list).

**The 8.6 MB scan WAS compressed on 2026-08-20 (`6cc2d65`), reversing the
decision recorded here.** The original reasoning was that it downloads only on
click, so page metrics never see it, and that compression would soften the
handwriting the panel exists to show. Eliot asked for it to be reduced if
appearance held up, and the second half of that reasoning was tested rather
than assumed: the PDF has **no text layer at all** — eight pages, one scanned
image each, embedded at roughly 445 DPI — so it was re-rendered at 150 DPI,
JPEG quality 80, page dimensions preserved exactly. Compared at 200 DPI
magnification the handwriting and blue annotation are indistinguishable from
the original. **8.6 MB → 1.77 MB, 79% smaller.** If it is ever re-exported from
the scanner, re-run that step; the source PDF is in git history at `fca6d93`.

## 3. Home page revamp — LIVE (2026-08-14, merge `f53b7fe`)

Hero H1 "A-Level Economics Revision Notes & Expert Tutoring" (title
deliberately unchanged — the "A Level Economics Revision" ranking is the
crown); six free-resource cards with measured numbers; four exam-board
tiles; Meet Your Tutor (eliot_shirt.JPG + credentials verbatim from
tutoring); static testimonials (William E., Alex B., Ebrahim D. — the three
tutoring does NOT use; reviews.js and reviews-render.js deleted, Harry G.
now used on the About page); Quick Answers; Kit newsletter form 9803307
(plain HTML POST, verified live). privacy.html gained newsletter coverage.

The measured numbers on the cards (166 topics, 671 cards, 1,267 questions,
281 papers, 325 definitions) were derived by script on 2026-08-14 — if
content grows, update the copy by hand; the provenance table is in this
file's git history.

Baseline for ~22 Sept: 223 clicks / 2,463 impressions / position 17.35.

## 4. Tutoring page SEO rework — LIVE (2026-08-14, merge `e09cdef`)

Rebuilt around the current offer: 1-to-1 £65/hr flat, groups of 2–4 at
£35/hr per student; new head + Service/FAQPage JSON-LD; credentials, pricing
cards, group section, exam-board section, 6 testimonials, 8-question FAQ,
Calendly booking section (`id="booking"` — the deep-link target other pages
use). faq.html prices updated in lockstep.

Baseline for ~22 Sept: position 26.27 / 440 impressions / 17 clicks
(2026-08-08 export).

## 5. Flashcards — LIVE

Interactive revision flashcards at `/flashcards/`, one deck per board per
theme, with Leitner spaced repetition in localStorage. Six decks: Edexcel A
Themes 1–4, AQA micro and macro.

`flashcards-data/<board>/<theme>.json` is hand-authored source and is not
published; `scripts/build_flashcards.py` writes the pages and the runtime
payloads in `flashcards/data/`. Cards marked `premium: true` never enter the
public payloads — that flag exists so premium content can later be excluded
without restructuring, because **the repo is public and client-side paywalling
is not sufficient**. Diagram cards reference the hand-authored SVGs in
`images/diagrams/svg/`, which is why those 84 files look unreferenced to any
tool that only greps HTML.

Live state and the full decision record: `docs/FLASHCARDS_PROGRESS.md`.
Suspected notes errors found while writing cards: `docs/CONTENT_ISSUES.md` —
logged, never fixed unilaterally.

## 6. Glossary & formulae — LIVE (merged 2026-08-09)

Every definition and formula a student needs, one page per exam board, at
`/revision-notes/glossary/`.

| | |
| --- | ---: |
| Terms | **325** |
| …Edexcel A / AQA | 269 / 290 |
| Formulae | **34** |
| Extracted verbatim from the notes | 251 |
| Written for the glossary | 74 |

**How it works.** `scripts/extract_glossary.py` reads the topic pages and writes
`glossary-data/terms.json`; `scripts/build_glossary.py` renders the three pages
and runs Prettier over its own output, so regenerating is byte-identical.
Formulae are pre-rendered with KaTeX at build time, so the pages carry no maths
JavaScript and work with JavaScript off.

**The rule, and its two exceptions.** Definitions are the notes' own words,
lifted verbatim, and `verify_glossary.py` check 1 re-reads each notes page and
fails if a shipped definition is no longer in it. The exceptions are
`glossary-data/authored.json` (definitions written to fill gaps the notes never
covered, tagged `origin="authored"` and exempt from that check) and the
`rewrite` block in `curation.json`, which edits lead-ins at render time. Both
are counted on every verify run so neither goes quiet.

**Judgement is kept out of the extractor** and in `glossary-data/curation.json`,
which the scripts only read — the same split as `tags.json` against
`taxonomy.json`.

What it found in the notes: two AQA formulae wrote `%` unescaped, so they
rendered broken on the live pages too (fixed); allocative, productive and
dynamic efficiency had no definition anywhere; the four marginal propensities
were undefined while four multiplier formulae depended on them.

Live state: `_working/glossary/PROGRESS.md`. The authored definitions:
`_working/glossary/authored-review.md`.

## 7. Past paper question bank — LIVE

A searchable bank of **real** exam questions at `/past-paper-questions/`,
Edexcel A (9EC0 A Level, 8EC0 AS) and AQA A Level.

**It reproduces real exam question text verbatim, which is the one decisive
difference from §8's practice bank, where every question must be 100% original.
The two never share a data path.** Section A is permanently out of scope for
every board. Mark scheme content is never extracted; each question deep-links
to the site's own hosted PDF at the right page.

Source attributions are stripped at extraction, not afterwards, and
`scripts/strip_source_attributions.py` is the re-runnable safety net that must
report 0 changes — that agreement is the test.

PDF work uses **Swift + PDFKit**, not Python. Search is
`js/components/question-search.js`, a small bounded-edit-distance token index
with no dependency, tested by `node scripts/test_question_search.js`.

Live state: `docs/PAST-PAPERS-PROGRESS.md`. Phase 1 extraction QA:
`_archive/extraction-qa-report.md`. AS extraction QA:
`_archive/working/question-bank/as-extraction-qa.md`.

## 8. Free practice questions — LIVE

A bank of **original** multiple-choice questions, one set per topic page, built
over thirty batches.

| | |
| --- | ---: |
| Topics | **166 of 166** |
| Questions | **1,267** |
| Answer letters | A 320, B 358, C 331, D 258 |
| Skills | applied-reasoning 790, definition-in-context 247, data-table 127, calculation 103 |
| Difficulty | foundation 155, standard 950, stretch 162 |

| Board / theme | Topics | Questions |
| --- | ---: | ---: |
| AQA Microeconomics | 54 | 401 |
| AQA Macroeconomics | 25 | 209 |
| Edexcel Theme 1 | 22 | 166 |
| Edexcel Theme 2 | 24 | 198 |
| Edexcel Theme 3 | 20 | 148 |
| Edexcel Theme 4 | 21 | 145 |

**How it works.** `questions-data/<board>/<spec>.json` is the single source of
truth — despite the name, it feeds `/practice-questions/`, not the past-paper
bank. `scripts/build_questions.py` validates it and writes the pages, the five
board indexes and the hub, so the visible HTML and the JSON-LD cannot drift.

**Every one of the 1,267 questions was re-solved cold from the stem alone**, in
the batch it was written in, and diffed against the recorded key. That step
found real defects and should be the last thing anyone drops.

**Originality was checked mechanically every batch** — shingled against the AQA
and Edexcel past-paper corpora, against the rest of the bank, and by comparing
numeric option sets against option blocks extracted from the papers. Re-measured
2026-08-20 across the two banks: **0 exact and 0 near-duplicate stems**, best
difflib ratio 0.000.

The authoring standard is `docs/QUESTIONS_GUIDE.md`. The batch record, the twin
maps and the nine recurring failure modes are in `docs/QUESTIONS_PROGRESS.md`;
read §8 (cross-board duplication) and §9 (concept-grep) before extending the
bank — they decided the shape of every batch after the twelfth.

**A written-response extension was piloted and reverted on review** — an
optional `written` array, generator support, a stylesheet block and ten
questions across five topics. Recoverable in one command from `be4d7b8`.

## 9. Notes consistency & enrichment pass — LIVE

Two jobs in one branch: make the 166 topic pages structurally consistent, then
add a small number of teaching components where a page genuinely needed one.

| | Before | After |
| --- | ---: | ---: |
| Generic "Exam Preparation" sections | 87 | **0** |
| Topic pages with exactly one `.notes-cta` | — | **166 / 166** |
| Inline-styled CTA blocks | 89 | **0** |
| Dead `chart-container` wrappers | 211 | **0** |
| `formula-box` divs without `prettier-ignore` | 28 | **0** |
| Unescaped `<` in note text | 32 | **0** |

The removed Exam Preparation text is archived verbatim in
`docs/removed-exam-preparation-sections.md`, in case any of it is worth
re-siting as an in-context exam tip.

**31 components across 34 of 166 pages.** 132 pages received nothing, by design
— the house rule is a maximum of two components per page and roughly 80% of
pages carrying none. Worked examples and exam tips only; every figure verified
by recomputation. The per-component inventory is `_archive/NEW-CONTENT-LOG.md`.

**One wording change was made in the whole pass** — a single word on
`3-4-4-oligopoly`, on explicit instruction, correcting "five" to "three" in a
concentration-ratio sentence.

Two related sweeps sit under this heading:

- **Site-wide scan, 31 July 2026.** 12 of 15 findings fixed, including 55
  keyboard-inaccessible accordions, heading-level skips on 12 pages, `lang="en"`
  on 22 pages, and 284 `target="_blank"` links without `rel`.
- **Notes corrections, 1 August 2026.** Twenty findings raised while writing the
  question sets, logged N-Q1 to N-Q20 in `docs/REVIEW-NOTES.md`; **16 applied.**
  Two corrections to the findings themselves are worth carrying forward: the
  N-Q10 figure-number scan reported one page that was not broken (`1-5-11`,
  whose `2a`/`2b` captions defeated the regex) and missed one that was
  (`2-5-1`). Any re-run must allow for the lettered caption form. One question
  was removed from the bank — `4.1.9` Q8, with the over-claim it depended on,
  which is why the total is 1,267 and not 1,268.

## What remains flagged

Absorbed from `PROJECT-LOG.md` (now `_archive/PROJECT-LOG.md`) on 2026-08-20 and **re-checked line by line
before being written down here**, because most of the list it arrived with had
already been fixed without the file being updated. How each was checked is
stated. Nothing here blocks anything, and everything needs an explicit
instruction before a page is touched, per CLAUDE.md.

### Still open — economics content

The evidence for each is in `docs/REVIEW-NOTES.md` under the given ID. These
are **carried over and not independently re-verified**, except where stated.

| Item | Where | What it needs |
| --- | --- | --- |
| **N-Q8** | AQA `2-2-2` the role of expectations | New prose, and it is tested by a live question, so cutting the claim would strand it. Checked 2026-08-20: the phrase appears 0 times on the page, so this one is still open. The other two N-Q8 pages are now fixed — `1-4-2` covers regulatory capture and `2-5-4` covers sustainable development |
| **N-Q11** | Edexcel `2.4.1` and `2.4.2` | Still duplicating. Re-measured 2026-08-20: **90 shared ten-word runs**, about 17% of 2.4.2's body. Restructuring. Left by choice |
| **N-Q7** | `2-6-5` HDI figures | Dated. Left by choice |
| **N1** | Two multiplier formulas | A leading space inside `\text{ Injection}`. Cosmetic; confirmed as authored, left deliberately |
| **N6** | `1-2-3` elasticities | The midpoint formula went with an Exam Preparation section. **Decided: leave it out** — Edexcel uses the original-value method and the page's worked example agrees |
| **C4** | AQA `2-2-3`, `1-5-6` | Both were reported as cross-referencing Edexcel theme numbers that do not exist in the AQA specification. **Not re-verified** — a grep for "Theme N" now matches the baked nav on every page, so it needs reading, not grepping |
| **C5** | `2-1-2` | Confirm the unemployment-rate denominator matches the ONS/ILO definition given a few lines above |
| **G4** | `Regulation` | Defined twice, from two notes pages, and neither reads as a definition |

### Still open — housekeeping

| Item | Status on 2026-08-20 | Fix |
| --- | --- | --- |
| **`.notes-container` defined in more than one stylesheet** | **Worse than recorded.** PROJECT-LOG said two; it is now **five**: `revision-notes-topics`, `revision-notes-textbook`, `glossary`, `macro-application`, `practice-questions` | Scope each under its page wrapper, per the CSS convention in CLAUDE.md |
| **Prettier fails on three files** | Confirmed with `npx prettier@3.9.6 --check`: `css/main.css`, `revision-notes/index.html`, `revision-notes/macro-application/index.html` | main.css is a `box-shadow` list and pre-existing. The two HTML files must NOT simply be formatted — trap 1 |
| **`404.html` has no canonical and no Open Graph tags** | Confirmed: 0 matches | Defensible for a 404. Listed so it stays a decision |
| **`.year-header h4` in `css/pages/past-papers-list.css`** | Still present at line 45 while line 196 styles `.year-header h2` | Likely dead. Read the markup before deleting |
| **Web-font layout shift** | Not re-measured. CLS was 0.078 on a notes page and 0.154 on a questions page | Self-host with `size-adjust`, or preload the woff2 the fold needs |
| **OCR A Level Paper 3, June 2023** | **The question paper is missing.** Both PDFs at that path are the mark scheme, byte-identical, md5 `35b8975c…`. Confirmed by Eliot and verified independently; a sweep of all 281 PDFs found no other case | Download H460/03 June 2023 from OCR and save it over the existing filename. No URL, link or sitemap change |

### Closed since PROJECT-LOG was written — do not re-raise

Each was on its "still flagged" list and each is now done. Checked 2026-08-20.

- **`navPanel` `aria-hidden`** — the accessibility failure that held every page
  at 96. `js/components/nav.js` now uses `inert`, which takes the panel out of
  the tab order *and* the accessibility tree from one attribute.
- **Breadcrumb contrast** — `css/main.css` now carries the reasoning at line
  3464; the old `#7f888f` is gone.
- **Dead Edexcel B mark-scheme links** — 65 PDF links on that hub, 0 missing.
- **N-Q8 on `1-4-2` and `2-5-4`** — both now cover what they promised.
- **Merging `feature/topic-questions`** — live, §8.
- **Merging `feature/glossary`** — live, §6.
- **`inject-templates.js`** — replaced by `js/components/nav.js` at Wave 4.10.
  Nothing is fetched at page load any more. `_config.yml` still described it as
  a runtime fetch until 2026-08-20.
