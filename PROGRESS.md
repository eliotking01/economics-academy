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

- [x] Rebuild tutoring.html — DONE. New head (title/description/og around
      "A-Level Economics Tutor", one description for both fields), fixed
      Service JSON-LD (the old block declared "provider" twice and priced a
      "Single Lesson" at £85 the page sold at £80), new FAQPage JSON-LD.
      Body: hero, credentials (adds hedge fund/FinTech + DBS), how-it-works,
      3-card pricing (free call / 1-to-1 £65 MOST POPULAR / group £35),
      group-lessons section (id="group-lessons"), exam-board section with
      internal links to each board's notes and papers, 6 testimonials
      verbatim from js/data/reviews.js, 8-question FAQ mirroring the JSON-LD.
      New CSS appended to css/pages/tutoring.css.
- [x] index.html — DONE, minimal: tutoring card is now "1-on-1 & Group
      Tutoring" with prices and the phrase "online A-Level Economics tutor";
      meta/og descriptions say "1-on-1 and small-group"; trust bar 3 → 4
      boards. Title, H1, hero untouched.
- [x] faq.html — DONE: prices, group answer, payment answer updated in both
      the visible accordions and the FAQPage JSON-LD.
- [x] Prettier + full verification suite — all green. Two traps hit and
      solved, recorded here for the next session:
      1. Prettier reformats the BAKED HEADER inside root pages so it stops
         being byte-identical to templates/header.html (verify_page_shell
         check 9). Fix: run `python3 scripts/bake_templates.py --apply`
         AFTER Prettier, never before.
      2. tutoring.html was removed from KNOWN_SELF_DISAGREEMENT in
         scripts/verify_page_shell.py (its og:description now equals its
         meta description; 17 entries remain).
- [ ] Rebuild sitemap after the content commit; commit separately.
- [ ] Final summary to Eliot.

## Merge instructions (for Eliot)

Merge with a **merge commit** (or plain fast-forward), not a squash. The
commits carry `Text-Change:` trailers that CI's text-integrity check reads
across the merged range; a squash merge would need those three trailer lines
copied into the squash commit message or CI goes red on main.

## Decisions made

- No aggregateRating/review stars in structured data — Google treats
  self-serving review markup as a violation; Tutorful link does that job.
- Old £80 single-lesson tier dropped entirely (Eliot, 2026-08-14).
- Marking page untouched. Home title/H1 untouched.
- FAQ rich results are gov/health-only since 2023, so FAQPage JSON-LD is a
  correctness/consistency play, not a rich-result play — set expectations
  accordingly.
