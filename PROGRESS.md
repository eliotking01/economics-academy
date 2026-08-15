# Site Work — Progress

Live state of in-flight work. A fresh session should read this first, then
CLAUDE.md. Excluded from publishing via `_config.yml`.

---

## 0. Marking page update & payment journey — branch `marking-page-update`

**STATE: BUILT, AWAITING ELIOT'S STRIPE LINKS.** The branch must NOT merge
until the five `STRIPE-LINK-NEEDED` placeholders in marking.html are replaced
— `grep STRIPE-LINK-NEEDED marking.html` must return nothing first. Eliot's
steps are at the top of OWNER-TODO.md.

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
   with two placeholder example panels, and a six-box FAQ. Trust strip
   updated (next-day; all four boards named).
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

- [ ] Eliot: five Stripe links + custom fields + redirects (OWNER-TODO top).
- [ ] Paste the five URLs over the placeholders; re-run verifiers; merge
      (merge commit, not squash).
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
