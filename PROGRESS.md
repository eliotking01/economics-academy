# Site Work — Progress

Live state of in-flight work. A fresh session should read this first, then
CLAUDE.md. Excluded from publishing via `_config.yml`.

---

## 1. Home page revamp — branch `home-page-revamp`

**STATE: BUILT AND VERIFIED, on the branch, NOT merged.** Two things remain
and both are Eliot's: paste the real Kit form ID into the newsletter form
(see OWNER-TODO.md — the form is inert until then), and review/merge. Nothing
is live until the merge.

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
   `action="https://app.kit.com/forms/KIT_FORM_ID/subscriptions"` — the
   KIT_FORM_ID placeholder is the one thing to replace before merge.
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
