# Owner To-Do — things only Eliot can do

Kept out of the published site via `_config.yml`. Items are grouped by when.

## Marking page relaunch — before the `marking-page-update` branch merges

The new marking page has 8 buy buttons (4 packages × 48-hour/next-day). Three
reuse existing Stripe links; five are placeholders until you create the links.

- [ ] **1. Create five new Stripe payment links** (~10 minutes). In the Stripe
      dashboard go to **Payment Links → + New**, create a product with exactly
      this name and price, and copy each link URL:

      | Product name | Price |
      | --- | --- |
      | Single 25-Mark Question — Next-Day | £30 |
      | Bundle of Three 25-Mark Questions — Next-Day | £75 |
      | Single Full Exam Paper — Next-Day | £70 |
      | Bundle of Three Full Exam Papers | £150 |
      | Bundle of Three Full Exam Papers — Next-Day | £180 |

- [ ] **2. Configure ALL EIGHT links the same way** (the 5 new ones plus the 3
      already on the page — editing a link in Stripe keeps its URL, so the
      existing three stay valid). For each link, under its edit screen:
      - **After payment**: redirect to
        `https://economicsacademy.co.uk/confirmation.html` (the existing three
        should already do this — check while you're there).
      - **Custom fields** (the "collect additional information" option — Stripe
        allows up to three): add two:
        1. Dropdown — label `Exam board`, options `Edexcel A`, `Edexcel B`,
           `AQA`, `OCR`
        2. Text — label `What should we mark? (e.g. Paper 2 June 2023)`
      These answers then arrive attached to the payment in Stripe, so students
      don't have to repeat them by email.

- [ ] **3. Paste the five new link URLs into marking.html.** Each placeholder
      reads `href="#STRIPE-LINK-NEEDED-…"` with a comment above it naming the
      product and price:
      - `#STRIPE-LINK-NEEDED-single-question-next-day` → Single 25-Mark
        Question — Next-Day (£30)
      - `#STRIPE-LINK-NEEDED-three-questions-next-day` → Bundle of Three
        25-Mark Questions — Next-Day (£75)
      - `#STRIPE-LINK-NEEDED-single-paper-next-day` → Single Full Exam Paper —
        Next-Day (£70)
      - `#STRIPE-LINK-NEEDED-three-papers-standard` → Bundle of Three Full
        Exam Papers (£150)
      - `#STRIPE-LINK-NEEDED-three-papers-next-day` → Bundle of Three Full
        Exam Papers — Next-Day (£180)
      Easiest: paste the five URLs into a Claude chat and ask it to wire them
      in. **Before merging, search marking.html for `STRIPE-LINK-NEEDED` — it
      must find nothing.**

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
      The five audit items held by D45 also unlock on this date.

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
