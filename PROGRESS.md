# Site Work — Progress

Live state of in-flight work. A fresh session should read this first, then
CLAUDE.md. Excluded from publishing via `_config.yml`.

---

## Unifying the four resource sections — PHASE 1 BUILT, AWAITING ELIOT'S REVIEW

**STATE (2026-08-15): Phase 1 (flashcards) is built and verified on branch
`resources-phase-1-flashcards`, three commits, NOT pushed and NOT merged.
Eliot reviews the branch; his review approves the wording changes listed
below. After merge: he requests GSC indexing for the 7 changed pages, and
Phase 2 (practice questions) can start on `resources-phase-2-practice-questions`.**

Eliot approved the Phase 0 plan in chat on 2026-08-15: the plan itself, the
phase-order swap with the ≈2026-09-22 gate on Phases 3–4,
review-as-wording-approval, and both housekeeping finds (stray CSS
duplicate — deleted; "Behavior"→"Behaviour" on the notes hub — approved now,
apply in Phase 4).

### What Phase 1 changed (commits f8a59d7, 978c2b7, ce52387)

- **`css/main.css`** — new additive `.resource-*` component block at the end
  of the file: hero (copied from the notes hub's winner shape), stat strip,
  card grid + card, cross-resource strip, services panel. Used by flashcards
  now; Phases 2–4 reuse it. Nothing above the block changed.
- **`scripts/build_flashcards.py`** — hub board/deck order from boards.json
  via `GROUP_ORDER` (was alphabetical: AQA above Edexcel A, macro above
  micro); hub hero + measured stat strip; CollectionPage `hasPart` naming
  the six decks; cross strip gains the question finder (master on the hub,
  board-filtered `QB_SLUGS` link per deck). Deck data payloads unchanged.
- **`css/pages/flashcards.css`** — rules superseded by the shared block
  removed; print + reduced-motion selectors retargeted.
- **Wording changes for Eliot's review (the complete list; everything else
  is verbatim):**
  1. Hub `<title>`: "A-Level Economics Flashcards | Economics Academy" →
     "A-Level Economics Flashcards | Free Edexcel A &amp; AQA Revision Cards"
  2. Hub H1: "A-Level Economics Flashcards" → "Free A-Level Economics
     Flashcards" (JSON-LD name matches)
  3. Hub, new stat line: "671 cards · 166 topics · 6 decks · free, no sign-up"
  4. Hub, new button: "Search real past paper questions"
  5. Deck pages ×6, new button: "Search Edexcel A past paper questions" /
     "Search AQA past paper questions"
- **Housekeeping:** both untracked Finder duplicates deleted —
  `css/pages/revision-notes-diagrams 2.css` (byte-identical to its sibling,
  explicitly approved) and `scripts/verify_boards 2.py` (found during Phase
  1; an older copy byte-identical to the committed version at `647b836`, so
  nothing was lost — flagged to Eliot in the review summary).

### Verification (all on 2026-08-15, before commit)

Every `scripts/verify_*.py` passes; two generator runs byte-identical;
`verify_text_integrity.py HEAD` reports 0 visible-text diffs in its 192
covered files (flashcards pages are outside its set, so no `Text-Change:`
trailers apply — its guard for this family is `verify_generated`);
`build_sitemap.py --check` exit 0 after the sitemap commit. Rendered in
headless Chrome at 1280px and at 390px via the iframe wrapper, all four
shots visually checked: board order, cards, stat strip, cross strip,
services panel, player still initialises.

### D45 compliance

No new link edges into `/revision-notes/` or `/past-papers/`. The only new
edges point at `/past-paper-questions/` (hub + its two board pages), which
has no GSC presence and is on no held list. Board display labels untouched
(hub already said "Edexcel A"; deck wording unchanged).

The brief (pasted 2026-08-15): unify Revision Notes, Flashcards, Practice
Questions and Past Papers — hubs and board/theme pages only (~26 pages, plus
the 3 question-finder pages as integration surfaces) — one design language,
better cross-linking, no URL changes, no economics content changes, notes hub
`<head>` frozen. Phased, one branch per phase, Eliot reviews each.

### Facts established in Phase 0 (all measured 2026-08-15, baseline green)

1. **The brief's past-papers premise is outdated: the site already hosts all
   281 paper PDFs** (`past-papers/**`, local hrefs, GSC clicks on the PDFs
   themselves). The licensing check is therefore about papers already live —
   OWNER-TODO item added. Do not add more PDFs until Eliot rules.
2. **Who owns each in-scope page** (decides where every edit lands):
   - notes hub `revision-notes/index.html` + past-papers 5 pages: hand-written,
     header/footer baked by `bake_templates.py`.
   - notes theme pages ×6 (+ macro-application): body slice in
     `notes-data/hubs/*.html` + head JSON, built by `build_notes_pages.py`.
   - practice hub + 6 theme pages: `build_questions.py`. Flashcards hub + 6
     decks: `build_flashcards.py`. Question-finder ×3 in scope:
     `build_past_paper_questions.py`. Never hand-edit generated output.
3. **GSC (seo/performance-pages.csv, 2026-08-08):** notes hub is the winner —
   361 clicks over its two URL forms, position ≈9.5, beating even home (223).
   Second tier: past-papers BOARD pages (edexcel-b 158 clicks pos 6.5–10.3,
   ocr 133, aqa 51) — their heads get the same frozen treatment. The
   past-papers hub itself is weak (3 clicks, pos 33.5). Flashcards, practice
   questions, glossary, question finder: zero GSC rows (live only since
   ~2026-08-13) — they are the indexing upside and carry near-zero ranking
   risk to redesign.
4. **Collision with the audit roadmap: D45 blocks five items until the
   ≈2026-09-22 GSC re-measure** — board display labels (3.4), the 8 hub
   cross-links (4.7), notes back-link anchors (4.8), PH05-019/020/021,
   PH03-049 step 2. Exactly the internal-linking / labelling work this
   project would do on the notes and past-papers sections. Eliot's recorded
   reason: acting early destroys the measurement. Hence the phase order below.
5. Board order disagrees across hubs: notes/practice hubs are Edexcel-first,
   flashcards hub AQA-first. `boards-data/boards.json` records edexcel-a
   first — that order wins; Phase 1 flips the flashcards hub.
6. Cross-links already good at page level (flashcards decks → notes topics;
   practice topics → notes + finder deep links). The gap is hub/theme level.
7. Housekeeping found: `css/pages/revision-notes-diagrams 2.css` is an
   untracked Finder duplicate, byte-identical to its sibling — delete in
   Phase 1. `revision-notes/index.html` button says US "Behavior" (Theme 3)
   where JSON-LD and practice hub say "Behaviour" — wording change, needs
   Eliot's explicit approval, earmarked Phase 4.

### The frozen list (beyond "all URLs frozen")

`<title>`, H1, meta description, canonical untouched on: `/revision-notes/`
(crown jewel) **and the four past-papers board pages** (second-tier winners).
The new sections' hubs (flashcards, practice, finder) MAY have heads tuned —
nothing ranks on them yet.

### The unified design (one component set, per-section stylesheets stay)

Derived from what the winner does + the flashcards' newer patterns: hero
(H1 + boards-naming intro + one-line stat strip of measured counts) →
board sections in boards.json order → one **resource-card** component
(descriptive title + counts meta line) for theme/deck/board links → one
**cross-resource strip** ("same topic, other tools") → one **services CTA**
(tutoring/marking, notes-cta-strip pattern). JSON-LD: add `hasPart` to the
three hubs lacking it. Shared component CSS goes into `css/main.css` as one
clearly-marked additive block (no new requests, no load-order change);
page-specific rules stay in each page's own sheet. New breakpoints use the
theme set (736 etc.). Board display labels: each section keeps its current
strings until Wave 3.4 unlocks (D45) — labelling unifies in Phases 3–4.

### Cross-linking policy (the D45-safe line)

Phases 1–2 add/restyle links freely **between the new sections** (flashcards ↔
practice ↔ finder) and may restyle links to notes/past-papers **that already
exist on those pages today**, but add **zero new edges into the measured
sections** before the re-measure. New edges into notes/past-papers (including
audit items 4.7/4.8 if Eliot approves them then) land in Phases 3–4.

### Phases (each its own branch, merged after Eliot's review)

| Phase | Branch | Pages | Gate |
| --- | --- | --- | --- |
| 1 Flashcards | `resources-phase-1-flashcards` | hub + 6 decks | on approval |
| 2 Practice Questions | `resources-phase-2-practice-questions` | hub + 6 themes | after Phase 1 review |
| 3 Past Papers | `resources-phase-3-past-papers` | hub + 4 board pages, finder integration | **≈2026-09-22 re-measure taken** |
| 4 Revision Notes | `resources-phase-4-revision-notes` | hub + 6 themes, held links 4.7/4.8 if approved | after Phase 3, crown-jewel care |

Deviation from the brief, flagged for approval: the brief's order was
flashcards → past papers → practice → notes. Past papers and practice are
swapped so both D45-touching sections land after the re-measure. Notes stays
last. Wording changes on redesigned pages (intros, CTA copy, tuned heads of
new-section hubs) are listed per phase in the review summary — Eliot's branch
review is the approval.

### Also recommended (decisions, not yet actions)

- **Do NOT expose all 166 topic links on the notes hub** — link dump, dilutes
  the winner; theme pages already list every topic. Declined in plan.
- Self-hosting PDFs: keep (already earning clicks, powers the finder's
  page-anchored mark-scheme links); the real question is licensing
  (OWNER-TODO). Reversal would orphan finder deep links.
- GSC "Request indexing" for new-section hubs now, and per phase after merge
  (OWNER-TODO).
- Optional, separate decision: self-host Google Fonts later (perf/CLS).

## 0. Marking page update & payment journey — branch `marking-page-update`

**STATE: MERGED AND LIVE.** Eliot approved in chat and the branch was merged
to main (merge commit `d4be06b`, --no-ff) and pushed on 2026-08-15; the
branch is deleted. Both workflows succeeded — verify CI (the branch commits'
Text-Change trailers accepted across the merge range) and the Pages
deployment — and the live site was spot-checked: 8 Stripe links serving with
0 placeholders, all four package cards, no trust strip, no coursework
mention, confirmation.html on the one-job version with Formspree gone,
faq.html carrying the next-day prices, and the `<title>` byte-identical.
All five Stripe links were created by Eliot; every one of the 8 checkout
pages was rendered headless and shows the right product, price, Exam Board
dropdown and "What should we mark?" field. The one thing unverifiable from
outside remains each link's after-payment redirect to confirmation.html
(Eliot configured it; worth a dashboard glance before the first real order).

**The #1 guardrail: marking.html ranks #1 for "Economics paper marking".** Its
URL, `<title>`, H1, meta description, canonical, og/twitter tags and
breadcrumb were left byte-identical. Changes are body copy, JSON-LD (offers
updated to the new prices; a duplicate `"provider"` key removed — the ignored
first one, so what Google reads is unchanged) and UX only.

### What changed (approved plan, 2026-08-15)

1. **marking.html** — four packages replace the old three, each card with two
   direct Stripe buttons (48-hour / next-day): Single 25-mark £25/£30, bundle
   of three 25-mark £60/£75 (Save £15), single full paper £60/£70, bundle of
   three full papers £150/£180 (Save £30). Three 48-hour links reused from the
   old page; five placeholders for Eliot. The old click-to-select flow, email
   capture panel and its inline script are deleted — a buy button is now a
   plain link, and the page's only scripts are the standard two-script tail.
   New: custom-enquiry box (custom + regular marking, quote by email), "What
   You Actually Get" section (mark+grade / annotated PDF / follow-up email)
   with two placeholder example panels, and a six-box FAQ. The trust strip
   was REMOVED at Eliot's request (2026-08-15 review): it kept mis-wrapping,
   contributes nothing to SEO, and every fact in it appears elsewhere on the
   page (boards + turnarounds in the packages intro and FAQ, credentials in
   "Who does the marking?").
2. **confirmation.html** — rebuilt around one job: email the work. Big mailto
   CTA, include-checklist, what-happens-next timeline. The Formspree form and
   client-side reference number are REMOVED (approved): Stripe now collects
   exam board + what's-being-marked at checkout via custom fields (Eliot
   configures — OWNER-TODO), and matching is by email address. Page is now
   JS-free beyond the tail. Still noindex, still not in the sitemap, still
   linked from nowhere.
3. **faq.html** — marking accordions + FAQPage JSON-LD updated in lockstep:
   four packages with both prices, next-day replaces the 24-hour £10 add-on
   (accordion id `marking-24-hour` renamed `marking-next-day`, internal link
   updated), three-deliverable feedback answer, regular-marking mention.
4. **CSS** — marking.css: selection-panel/fast-track/email-capture styles
   removed; new `marking-package`, `marking-buy-options`, `marking-custom-box`,
   `marking-deliverable*`, `marking-example*`. confirmation.css rewritten
   (single centred column, form styles gone).

### Still to do (in order)

- [x] Eliot: five Stripe links + custom fields + redirects — done 2026-08-15.
- [x] Paste the five URLs over the placeholders; re-run verifiers — done
      2026-08-15; the placeholder comments were removed with the hrefs.
- [x] Review and merge — merged 2026-08-15, live and spot-checked.
- [ ] Eliot: two anonymised example PDFs into `marking-examples/` (can come
      after merge — placeholders show until then). Then a session generates
      one PNG preview per PDF (first page), adds width/height from the real
      files, swaps the placeholder divs in marking.html for preview + "view
      full example" links, and updates `verify_page_shell.py`'s image
      expectations (`EXPECTED_IMAGES` +2 etc.) in the same commit. Note:
      `build_sitemap.py` auto-lists published PDFs in sitemaps/pdfs.xml —
      expected, harmless.

### Traps hit / to know (beyond §1's inherited five)

- The `.row` grid in main.css has a built-in 50px gutter (`.row > *` padding)
  — package cards use `height: 100%` like the testimonials, no extra margins.
- The example panels are styled divs, NOT `<img>`/`<a>` to the future files:
  verify_links and verify_image_dimensions fail on references to files that
  do not exist yet. Do not add the links before the files land.
- Baseline for the ~2026-09-22 GSC check: marking.html had no recorded
  baseline in this file; its ranking claim ("#1 for Economics paper marking")
  is Eliot's report on 2026-08-15.

## 1. Home page revamp — branch `home-page-revamp`

**STATE: MERGED AND LIVE.** Eliot approved in chat and the branch was merged
to main (merge commit `f53b7fe`, --no-ff) and pushed on 2026-08-14. Both
workflows succeeded — verify CI (the two Text-Change trailers were accepted
across the merge range) and the Pages deployment — and the live site was
spot-checked: new H1, Kit form 9803307, board tiles, static testimonials and
the privacy additions all serving, `<title>` byte-identical, old review
scripts gone. The newsletter form posts to Kit form **9803307** (endpoint
sanity-checked, GET 200).

**Eliot re-indexed `/`, `/privacy.html`, `/tutoring.html` and `/faq.html` on
2026-08-14**, which is the clock the ~2026-09-22 GSC check reads from — the
tutoring rework's own follow-ups (Tutorful price, agreement document, other
profiles) are all closed the same day. What is left is the newsletter's
end-to-end proof: a live test signup and the Kit double-opt-in glance, both
in OWNER-TODO.md. Measure the page against its baseline (223 clicks, 2,463
impressions, position 17.35) at the ~2026-09-22 check.

### The brief (approved 2026-08-14, all four plan questions answered yes)

Revamp the home page for SEO and users. Priority ranking to PRESERVE at all
costs: "A Level Economics Revision (Notes)" — the page's title was therefore
left completely unchanged and the phrase kept verbatim at the front of the H1.
Secondary: support "A Level Economics Tutor" without competing with
tutoring.html (home mentions the phrase in body text and links to the tutoring
page; only tutoring.html headlines it). Revision notes outrank tutoring in
page hierarchy. Approved specifics: H1 drops "Past Papers"; Kit for the
newsletter; all four exam-board tiles including OCR/Edexcel B (Eliot
knowingly front-ran the PH03-049-step-2 hold — the board section creates the
honest anchor context that seo/07b §5 said was missing).

### What was built (top to bottom of the page)

1. **Hero** — H1 now "A-Level Economics Revision Notes & Expert Tutoring";
   subhead names all six free resources; both CTAs and the trust line kept.
2. **Free resources** — 2 cards → 6 (notes / flashcards / practice questions /
   past papers / question finder / glossary), grid variant
   `resource-grid--three`, real measured numbers (provenance below).
3. **Revise by Exam Board** — 4 tiles with pill links into each board's notes
   and papers. verify_seo check 13 exempts the homepage (no board of its own).
4. **Meet Your Tutor** — solo portrait `/images/eliot_shirt.JPG` (the same
   photo tutoring.html uses; `eliot_grad.jpg` was tried first and is a group
   shot — swap back only if Eliot prefers it), credential bullets reused
   verbatim from tutoring.html, two links with FRESH anchor texts ("Explore
   1-to-1 & Group Tutoring", "More About Eliot"), then the two existing paid
   action cards untouched.
5. **Trust bar** — untouched.
6. **Testimonials** — now static HTML: the three reviews tutoring.html does
   NOT use (William E., Alex B., Ebrahim D.), markup mirroring what
   reviews-render.js used to emit so home.css applies unchanged.
   `js/data/reviews.js` and `js/components/reviews-render.js` are DELETED
   (only index.html referenced them; the fourth unused review, Harry G., now
   exists only in git history).
7. **Quick Answers** — four always-visible Q&As (no accordion, no JS, no
   FAQPage JSON-LD — Google removed FAQ rich results May 2026), plus a link
   to faq.html (one of GSC's "crawled, not indexed" pages).
8. **Newsletter** — plain HTML form POSTing to Kit, zero scripts.
   Connected: `action="https://app.kit.com/forms/9803307/subscriptions"`.
9. Head: meta description and og:description rewritten (identical strings, so
   index.html LEFT `KNOWN_SELF_DISAGREEMENT` — 16 remain). `<title>`, JSON-LD,
   canonical, GA all untouched.

privacy.html gained newsletter coverage: collection li, "subscribe" li, use
li, a Kit entry under sharing, and retention ("until you unsubscribe").

### Numbers on the page and where each came from (re-derive before changing)

| Claim | Measured | How |
| --- | --- | --- |
| 166 topic pages | 166 | notes topic pages, `verify_page_shell.py` families |
| 670+ flashcards | 671 | sum of `flashcards/data/*.json` cards |
| 1,267 practice questions | 1,267 | sum of `questions-data/*/*.json` |
| 280+ past papers | 281 | `find past-papers -name '*.pdf' \| wc -l` |
| 300+ definitions | 325 | entries in `glossary-data/terms.json` |

Floors ("+") were used where the count naturally grows; exact numbers where
the corpus is complete. If content grows, update the copy by hand.

### Verifier expectations updated in the same commit (the declared pattern)

- `verify_page_shell.py`: root script tails 3 → 2; images 309 → 310; pages
  with images 104 → 105; all-lazy pages 8 → 9 (index.html's one image is the
  below-fold tutor photo, so lazy is correct); index.html removed from
  `KNOWN_SELF_DISAGREEMENT` and from `EXPECTED_EXTRA_SCRIPTS`.
- `bake_templates.py`: comments about index.html's own-tail scripts updated.

### Verification state (all green before commit)

verify_generated (8 generators, 0 files would change), verify_seo 14/14,
verify_page_shell 9/9, verify_image_dimensions, verify_css_load_order,
verify_inline_styles, verify_icons (no new icons — every new section uses the
existing 15-icon subset), verify_liquid, verify_published_surface,
verify_boards. Rendered in headless Chrome at 1280px and 390px and visually
checked.

### Traps a fresh session must know (inherited from the tutoring rework)

1. Prettier reformats the BAKED HEADER inside root pages — always run
   `python3 scripts/bake_templates.py --apply` AFTER Prettier.
2. Any commit changing visible wording on a published page needs one
   `Text-Change: <path>` trailer per page, in the final trailer block of the
   commit message, or CI fails. Merge with a merge commit, NOT a squash.
3. Root pages are hand-written (out of page_shell scope, D34) — edit
   directly.
4. Run `python3 scripts/build_sitemap.py` AFTER committing page edits (it
   takes lastmod from git) and commit the sitemap separately.
5. Only icons already in `css/fontawesome-all.min.css` may be used.

## 2. Tutoring page SEO rework — MERGED AND LIVE (2026-08-14)

Rebuilt tutoring.html around the new offer (1-to-1 £65/hr flat, groups of
2–4 at £35/hr per student), new head + Service/FAQPage JSON-LD, credentials,
pricing cards, group section, exam-board section, 6 testimonials, 8-question
FAQ; faq.html prices updated; home card updated (superseded by the revamp
above, which keeps its copy verbatim). Merge commit `e09cdef`, both workflows
green, live site spot-checked. Full detail in git history of this file.

Baseline to beat at the ~2026-09-22 GSC check: tutoring.html at position
26.27 / 440 impressions / 17 clicks (`seo/performance-pages.csv`,
exported 2026-08-08). Eliot's follow-ups live in OWNER-TODO.md.
