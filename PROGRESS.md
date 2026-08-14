# Tutoring Page SEO & Rework — Progress

Branch: `tutoring-seo-rework`. Never merged to main by Claude — Eliot reviews
and merges. This file is the live state; a fresh session should read it first,
then CLAUDE.md, then `seo/03-diagnosis.md` for the prior technical-SEO audit.

## The brief (approved 2026-08-14)

Tutoring page earns 80%+ of income but ranks ~page 5 (GSC: position 26.27,
440 impressions, 17 clicks — `seo/performance-pages.csv`). Rework it around
the NEW offer, optimise home page for "A Level Economics Tutor" WITHOUT
harming its revision-notes ranking, and never risk marking.html's #1.

**The new offer (replaces everything previously on the page):**

- 1-to-1 lessons: **£65/hour flat** — no minimum number of lessons
  (supersedes the old £80 single / £65-with-3-minimum structure, Eliot
  confirmed 2026-08-14).
- Group lessons (2–4 students): **£35/hour per student**. Ready-made groups
  welcome, or individuals are matched into a group. First group lesson is
  pay-as-you-go to try it; after that billed per half-term or term (by number
  of lessons). Only a brief mention of billing on the page — the tutoring
  agreement document carries the detail.
- Online only. Free 15-minute Calendly intro call stays the primary CTA;
  Formspree modal + email are secondary.

## Key repo facts a fresh session needs

- Root pages (tutoring, index, faq…) are HAND-WRITTEN — not generated, out of
  page_shell scope (D34). Edit directly, format with `npx prettier@3.9.6`.
- CI (`.github/workflows/verify.yml`) diffs visible wording against HEAD~1:
  any commit changing words on a published page MUST carry one
  `Text-Change: <path>` trailer per page in the commit message, or CI fails.
  (`verify_markup_integrity.py` only covers revision-notes/ — not relevant.)
- New root `.md` files publish by default — both this file and OWNER-TODO.md
  are in `_config.yml`'s exclude list; anything else added at root must be too.
- Icon subset: only icons already in `css/fontawesome-all.min.css` may be
  used (fa-users, fa-calendar-check, fa-chalkboard-teacher, fa-graduation-cap,
  fa-bolt, fa-check-double, fa-star, fa-clipboard-list, fa-file-alt, fa-clock,
  fa-envelope, fa-search, fa-plus, fa-minus, fa-bars). A new icon needs the
  subsetter re-run — avoid.
- `seo/tools/verify_seo.py` (in CI) requires og:title == <title>, self
  canonical, one h1, unique titles/descriptions, parseable JSON-LD.
- After any commit that changes published pages, run
  `python3 scripts/build_sitemap.py` (it derives lastmod from git, so run it
  AFTER committing the page edits) and commit the sitemap separately.

## Done

- [x] Investigation: prior SEO audit read (`seo/`), GSC exports, testimonials
      found (`js/data/reviews.js` — 10 five-star reviews), competitor research.
- [x] Plan approved by Eliot 2026-08-14, including permission to edit
      existing wording on tutoring.html, faq.html, index.html (visible-text
      changes are otherwise forbidden by standing rule).
- [x] Branch `tutoring-seo-rework`; PROGRESS.md + OWNER-TODO.md created and
      excluded from publishing in `_config.yml`.

## In progress / next

- [ ] Rebuild tutoring.html: new pricing (3 cards: free call / 1-to-1 £65 /
      group £35), how-it-works strip, group-lessons section, exam-board
      section (Edexcel A, AQA, Edexcel B, OCR with internal links), full
      credentials (hedge fund + FinTech, DBS), 6 testimonials, expanded FAQ
      (8 Q&As) + FAQPage JSON-LD, fixed Service JSON-LD (it currently has a
      duplicate "provider" key and stale £85/£80 prices). New CSS classes in
      css/pages/tutoring.css: how-it-works/step-card/board-grid/board-card/
      pricing-note (collision-checked, all free).
- [ ] index.html (minimal, ranking-protective): tutoring card copy gains
      "online A-Level Economics tutor" anchor phrase + group mention; meta/og
      description "1-on-1" → "1-on-1 and small-group"; trust bar "3" → "4"
      exam boards. Title and H1 UNTOUCHED (they hold the notes ranking).
- [ ] faq.html: update tutoring-price answer (£65 flat, no minimum), group
      answer ("coming soon" → real offer), payment answer (group billing) —
      both visible text and the FAQPage JSON-LD near the top of the file.
- [ ] Prettier over edited pages; full verification suite (the list in
      CLAUDE.md ## Tooling); commit with Text-Change trailers.
- [ ] Rebuild sitemap; commit.
- [ ] Update this file + OWNER-TODO.md; final summary to Eliot.

## Decisions made

- No aggregateRating/review stars in structured data — Google treats
  self-serving review markup as a violation; Tutorful link does that job.
- Old £80 single-lesson tier dropped entirely (Eliot, 2026-08-14).
- Marking page untouched. Home title/H1 untouched.
- FAQ rich results are gov/health-only since 2023, so FAQPage JSON-LD is a
  correctness/consistency play, not a rich-result play — set expectations
  accordingly.
