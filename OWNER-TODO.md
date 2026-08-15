# Owner To-Do — things only Eliot can do

Kept out of the published site via `_config.yml`. Items are grouped by when.

## Resource-pages unification — added 2026-08-15

- [ ] **Check each exam board's licensing terms for hosting past papers.**
      Important context: the site does not link out to the boards' websites —
      it already hosts all 281 paper PDFs itself, live, in `past-papers/`.
      So this is not a question about a future decision; it is due diligence
      on something already published. Look for the "copyright" or
      "using our materials" page on each of: Pearson/Edexcel, AQA and OCR.
      What to check: whether hosting complete past papers for free
      educational use is permitted, whether attribution wording is required,
      and whether any embargo applies to recent series. Nothing needs taking
      down unless a term says so — this is a check, not an alarm.
- [ ] **Google Search Console → request indexing for the new sections' hubs**
      (they went live mid-August and Google barely knows them yet):
      `https://economicsacademy.co.uk/flashcards/`,
      `https://economicsacademy.co.uk/practice-questions/`,
      `https://economicsacademy.co.uk/past-paper-questions/`,
      `https://economicsacademy.co.uk/revision-notes/glossary/`.
      In GSC: paste each URL into the top search bar → "Request indexing".
      ~2 minutes for all four.
- [ ] **Phase 1 merged 2026-08-15 — request indexing for the 7 flashcards
      pages** (same GSC routine as above): `/flashcards/`, then
      `/flashcards/edexcel-a/theme-1/` … `theme-4/`, `/flashcards/aqa/micro/`
      and `/flashcards/aqa/macro/`. If you already did the hub in the item
      above, no harm in requesting it again.
- [ ] **After Phase 2 merges — request indexing for the 7 practice-questions
      pages** (same GSC routine as above): `/practice-questions/`, then
      `/practice-questions/edexcel-theme-1/` … `edexcel-theme-4/`,
      `/practice-questions/aqa-a2-micro/` and
      `/practice-questions/aqa-a2-macro/`. Not before the merge — the live
      pages haven't changed yet.
- [ ] **After Phase 3 merges — request indexing for the 5 past-papers
      pages** (same GSC routine as above): `/past-papers/`, then
      `/past-papers/edexcel/`, `/past-papers/aqa/`, `/past-papers/ocr/`
      and `/past-papers/edexcel-b/`. Not before the merge — the live
      pages haven't changed yet. These four board pages already rank
      well; re-indexing just tells Google about the redesign sooner.
- [ ] **After each later resource phase merges**: request indexing for the
      pages that phase changed (the phase's review summary will list them).

## Marking page relaunch — live since 2026-08-15

- [ ] **One glance in the Stripe dashboard**: confirm each of the 8 payment
      links redirects to `https://economicsacademy.co.uk/confirmation.html`
      after payment — that setting isn't visible from outside, and it's the
      only part of the new journey nobody has been able to verify. A £0 test
      isn't possible, so the first real order is the true end-to-end proof.
- [ ] Skim the live marking page on your phone once — the packages, the
      enquiry box and the "coming soon" example panels.

## Marking page examples — any time (placeholders show until done)

- [ ] **Prepare two real examples, fully anonymised**, and save them into a
      new `marking-examples/` folder in the repo with exactly these names:
      - `marking-examples/annotated-paper-example.pdf` — a real annotated
        paper
      - `marking-examples/feedback-email-example.pdf` — a real follow-up
        email, exported to PDF (in Gmail: open the email → the printer icon →
        destination "Save as PDF")
      Then tell Claude the files are in place: it will generate the preview
      images from them and swap the "coming soon" boxes on the marking page
      for the real previews and links.
- [ ] **Anonymisation checklist** — check every page before saving:
      - Student name, school/centre name, candidate/centre numbers — including
        the script's front page and any page headers
      - Any date + class combination that could identify the student
      - In the email: the greeting, the student's email address, and anything
        in the thread below your reply
      - Metadata: export via Print → "Save as PDF" (this drops the original
        author fields), then check the PDF's Get Info / properties shows no
        student name
      - The two PDFs will be publicly visible on the site (that's the point),
        so check them as carefully as anything else you publish

## Now

- [ ] **One 30-second check in Kit**: confirm "double opt-in" (the
      confirmation email) is ON for the form — it's Kit's default, and the
      page already promises "You will get a confirmation email first".
- [ ] **Send yourself a test signup** on the live site (your own email) and
      confirm the confirmation email arrives and you appear as a subscriber
      in Kit. This is the only thing that proves the form works end to end.
- [ ] Skim the live home page on your phone once — you're checking the photo,
      the wording and the form, not the code.

## Newsletter, ongoing

- [ ] Decide a realistic sending rhythm — even one email per half-term is
      fine; the page promises "occasional", so anything beats silence.
- [ ] First email idea: new-resource roundup (flashcards, question finder,
      glossary) — the six home-page cards are effectively the draft.
- [ ] Optional, ~5 minutes: a one-email welcome automation in Kit
      (Automate → Visual Automations → trigger "Joins a form" → Send email).
      The free plan includes exactly one automation, which is this. Not
      required — the confirmation email already greets every subscriber.

## Worth doing over the next few weeks

- [ ] **Google Business Profile**: as an online-only service you can create a
      profile without a public address ("service area" business). It enables
      Google reviews, which show for brand searches. Optional but the single
      cheapest trust signal available.
- [ ] **Collect Google reviews** (once the profile exists): ask 3–5 recent
      parents/students. Tutorful reviews cannot be imported.
- [ ] **Backlinks** — realistic, white-hat options only: tutor directories
      (First Tutors, Tutor Hunt), university alumni pages, and when emailing
      schools or teachers link the notes hub, not the tutoring page.
- [ ] **Consider a short "meet the tutor" video** on the tutoring page later.

## Already scheduled

- [ ] **~22 September 2026 GSC check**: compare tutoring.html against its
      2026-08-08 baseline (position 26.27, 440 impressions, 17 clicks) and
      check the home page's clicks/position held or improved after the revamp
      (baseline: 223 clicks, 2,463 impressions, position 17.35, CTR 9.05%).
      These two comparisons are still clean. What changed: you overrode the
      D45 wait on 2026-08-15 (D50) so resource phases 3–4 could ship before
      the new academic year — so treat any movement on the revision-notes and
      past-papers pages as directional only, not as a verdict on the earlier
      SEO work (their baselines: notes hub 361 clicks pos ≈9.5, edexcel-b 158,
      ocr 133, aqa 51).

## Done — kept only where the DATE matters to a later measurement

- **2026-08-14 — re-indexing requested** in Search Console for `/`,
  `/privacy.html`, `/tutoring.html` and `/faq.html`. This is the clock the
  ~22 September check reads from: a recrawl typically lands within days to a
  few weeks, so any ranking movement before roughly late August is noise
  rather than a result.
- **2026-08-14 — Tutorful profile updated** to £65/hour, so the site and the
  profile agree for anyone searching Eliot by name.
- **2026-08-14 — tutoring agreement updated** with the group billing detail
  (per half-term/term, by number of lessons). The site deliberately keeps
  only a brief mention and points at the agreement, so the two now match.
- **2026-08-14 — other profiles checked** for the old £80 single-lesson
  price; nothing stale left public.
- **2026-08-14 — Kit account, form and form ID** (9803307), wired into
  index.html and verified live.
