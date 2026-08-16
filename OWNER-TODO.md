# Owner To-Do — things only Eliot can do

Kept out of the published site via `_config.yml`. One prioritised list,
consolidated 2026-08-16 at the end of the site-wide overhaul. Items are in
priority order within each group.

## Do next

- [ ] **Write the missing About-page paragraph** — 2–3 sentences on why you
      moved from finance to tutoring. Aim for warm and direct; the paragraphs
      either side already cover the facts (Bath, the London jobs, the 11+
      story), so this is the "why", not the CV. Where it goes: about.html has
      an HTML comment marked `OWNER COPY NEEDED` in the My Story section —
      paste the text to Claude and it will insert it properly.
- [ ] **Formspree dashboard, 5 minutes** — the honeypot spam trap is now live
      in the code on both forms and needs no setup, but two things live only
      in the dashboard: log in at formspree.io and for BOTH forms (`xblapyky`
      = contact page, `mqadgbbw` = tutoring enquiry pop-up) open Settings and
      (1) check the notification email is the address you actually read,
      (2) look at the "Spam" section and make sure Formspree's own filtering
      is on. Leave reCAPTCHA off — no puzzles for real users unless bot
      submissions continue after this.
- [ ] **Click the LinkedIn link once** on the new About page and check it
      lands on your profile. (LinkedIn blocks automated checks, so this is
      the one link that couldn't be verified by machine.)
- [ ] **One glance in the Stripe dashboard**: confirm each of the 8 payment
      links redirects to `https://economicsacademy.co.uk/confirmation.html`
      after payment — the only part of the marking journey nobody has been
      able to verify from outside.
- [ ] **One 30-second check in Kit**: confirm "double opt-in" (the
      confirmation email) is ON for form 9803307 — it's Kit's default, and
      the home page already promises "You will get a confirmation email
      first".
- [ ] **Send yourself a test signup** on the live home page and confirm the
      confirmation email arrives and you appear as a subscriber in Kit. This
      is the only thing that proves the form works end to end.

## Soon

- [ ] **Request indexing in Search Console** — quota is roughly 10/day.
      Priority order:
      1. The 9 that already rank: `/revision-notes/` first, then
         `/revision-notes/edexcel-theme-4/`, `/revision-notes/aqa-a2-micro/`,
         `/revision-notes/aqa-a2-macro/`, `/past-papers/`,
         `/past-papers/edexcel/`, `/past-papers/aqa/`, `/past-papers/ocr/`,
         `/past-papers/edexcel-b/`.
      2. The 12 new-section pages: six flashcards decks
         (`/flashcards/edexcel-a/theme-1/` … `theme-4/`,
         `/flashcards/aqa/micro/`, `/flashcards/aqa/macro/`) and six
         practice-questions theme pages
         (`/practice-questions/edexcel-theme-1/` … `-4/`,
         `/practice-questions/aqa-a2-micro/`,
         `/practice-questions/aqa-a2-macro/`).
      3. After the About/Contact branch merges: `/about.html` and
         `/contact.html`.
- [ ] **Phone skim** of the live pages changed recently, once each: marking
      (packages, enquiry box, example panels), home (photo, wording, form),
      and after the merge, About and Contact.
- [ ] **Marking examples** — prepare two real, fully-anonymised examples and
      save them as `marking-examples/annotated-paper-example.pdf` and
      `marking-examples/feedback-email-example.pdf`, then tell Claude —
      it generates the previews and swaps the "coming soon" boxes.
      Anonymisation checklist: student name, school/centre name,
      candidate/centre numbers (front page AND page headers), any date+class
      combination, the email greeting/address/thread, and PDF metadata
      (export via Print → "Save as PDF", then check Get Info shows no student
      name). Both PDFs will be publicly visible — that's the point, so check
      them like anything else you publish.
- [ ] **Check each exam board's licensing terms for hosting past papers.**
      The site already hosts all 281 paper PDFs itself, so this is due
      diligence on something already published, not a future decision. Look
      for the "copyright" or "using our materials" page on Pearson/Edexcel,
      AQA and OCR: is hosting complete past papers for free educational use
      permitted, is attribution wording required, does any embargo apply to
      recent series. Nothing needs taking down unless a term says so.

## Worth doing over the coming weeks

- [ ] **Google Business Profile**: as an online-only service you can create a
      profile without a public address ("service area" business). It enables
      Google reviews, which show for brand searches — the single cheapest
      trust signal available.
- [ ] **Collect Google reviews** (once the profile exists): ask 3–5 recent
      parents/students. Tutorful reviews cannot be imported.
- [ ] **Backlinks** — realistic, white-hat only: tutor directories (First
      Tutors, Tutor Hunt), university alumni pages; when emailing schools or
      teachers, link the notes hub, not the tutoring page.
- [ ] Optional writing task: 1–2 sentences for the About page on who you are
      outside economics (a hobby, what you're like to work with) — humanises
      the page for parents. No placeholder waits on it; tell Claude where you
      want it if you write it.
- [ ] **Consider a short "meet the tutor" video** on the tutoring page later.

## Newsletter, ongoing

- [ ] Decide a realistic sending rhythm — even one email per half-term is
      fine; the page promises "occasional", so anything beats silence.
- [ ] First email idea: new-resource roundup (flashcards, question finder,
      glossary) — the six home-page cards are effectively the draft.
- [ ] Optional, ~5 minutes: a one-email welcome automation in Kit (Automate →
      Visual Automations → trigger "Joins a form" → Send email). The free
      plan includes exactly one automation. Not required.

## Ongoing habits (the maintenance routine)

- **New or reworked page goes live → request indexing** for it in Search
  Console (paste URL in the top bar → "Request indexing"). The sitemap
  updates automatically at build time; the manual request just speeds Google
  up.
- **Glance at Search Console monthly**: Performance for clicks/position
  trends, and Pages → "Why pages aren't indexed" for anything unexpected.
- **Never edit generated pages by hand** (Claude knows which are which — if
  in doubt, ask before editing anything under revision-notes/, flashcards/,
  practice-questions/ or the glossary).
- **Content mistakes you spot** go in REVIEW-NOTES.md (site) or
  docs/CONTENT_ISSUES.md (flashcards) rather than being fixed on the spot,
  so every wording change stays deliberate.

## Already scheduled

- [ ] **~22 September 2026 GSC check**: compare tutoring.html against its
      2026-08-08 baseline (position 26.27, 440 impressions, 17 clicks) and
      check the home page held or improved (baseline: 223 clicks, 2,463
      impressions, position 17.35, CTR 9.05%). These two comparisons are
      clean. The D45 wait was overridden on 2026-08-15 (D50), so treat any
      movement on revision-notes and past-papers pages as directional only
      (their baselines: notes hub 361 clicks pos ≈9.5, edexcel-b 158, ocr
      133, aqa 51).

## Done — kept only where the DATE matters to a later measurement

- **2026-08-15 — indexing requested** for 7 redesigned/new pages:
  `/flashcards/`, `/practice-questions/`, `/past-paper-questions/`,
  `/revision-notes/glossary/`, `/revision-notes/edexcel-theme-1/`, `-2/`,
  `-3/`. Same ~22 September clock as below.
- **2026-08-14 — re-indexing requested** for `/`, `/privacy.html`,
  `/tutoring.html`, `/faq.html`. This is the clock the ~22 September check
  reads from: movement before roughly late August is noise, not a result.
- **2026-08-14 — Tutorful profile updated** to £65/hour; **tutoring agreement
  updated** with group billing detail; **other profiles checked** for the old
  £80 price; **Kit account, form and form ID** (9803307) wired into
  index.html and verified live.
