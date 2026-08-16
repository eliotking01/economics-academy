# Site Work — Progress

The record of the 2026 site-wide overhaul. A fresh session should read this
first, then CLAUDE.md. Excluded from publishing via `_config.yml`.

Reorganised 2026-08-16 into its final state: the overhaul is complete, so
this file is now a map — one section per project with what changed and the
traps, newest first. The exhaustive per-item wording lists each branch
carried for review live in this file's own git history, not here.

## The overhaul at a glance

| Project | State | Merged | Merge commit |
| --- | --- | --- | --- |
| About + Contact + finishing pass | live | 2026-08-16 | `437dc7e` |
| Resource unification, Phases 1–4 | live | 2026-08-15 | `d0fdcaf`, `2295213`, `1e8dfed`, `f537312` |
| Marking page + payment journey | live | 2026-08-15 | `d4be06b` |
| Home page revamp | live | 2026-08-14 | `f53b7fe` |
| Tutoring page SEO rework | live | 2026-08-14 | `e09cdef` |

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
list). The 8.6 MB scan was deliberately NOT compressed: it downloads only
on click, so page metrics never see it, and compression would soften the
handwriting the panel exists to show.

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
