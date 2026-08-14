# Owner To-Do — things only Eliot can do

Kept out of the published site via `_config.yml`. Items are grouped by when.

## BEFORE merging `home-page-revamp` (the newsletter needs ~10 minutes)

- [ ] **Create your free Kit account** at kit.com (choose the free Newsletter
      plan — free to 10,000 subscribers, no card needed).
- [ ] **Create the signup form**: in Kit go to Grow → Landing Pages & Forms →
      Create new → Form → **Inline**, name it e.g. "Homepage signup". Design
      doesn't matter — the site never loads Kit's design, only posts to it.
- [ ] **Get the form ID**: on the form, choose Embed → **HTML**. In that code
      you'll see a line like
      `action="https://app.kit.com/forms/1234567/subscriptions"`.
      Copy the number (or the whole URL if it looks different).
- [ ] **Send the number to Claude to paste in** — or do it yourself: in
      `index.html` there is exactly one `KIT_FORM_ID` to replace, next to an
      `OWNER-TODO` comment. Until then the Subscribe button does nothing.
- [ ] **Leave "double opt-in" ON in Kit** (subscribers confirm by email —
      it's the default and good UK GDPR practice; the page already says
      "You will get a confirmation email first").
- [ ] Optional: in Kit, set the form's "incentive/thank-you" email content —
      the default confirmation is fine to start.

If you'd rather launch without the newsletter, say so and Claude will remove
the section before merge — do not merge it with the placeholder in place.

## After merging `home-page-revamp` (day 0)

- [ ] **Request re-indexing in Search Console** (URL Inspection → Test Live
      URL → Request Indexing) for:
      1. `https://economicsacademy.co.uk/`
      2. `https://economicsacademy.co.uk/privacy.html`
- [ ] Skim the live home page on your phone once — you're checking the photo,
      the wording and the form, not the code.
- [ ] **Send yourself a test signup** (your own email) and confirm the
      confirmation email arrives and you appear as a subscriber in Kit.

## Newsletter, ongoing (only once it's live)

- [ ] Decide a realistic sending rhythm — even one email per half-term is
      fine; the page promises "occasional", so anything beats silence.
- [ ] First email idea: new-resource roundup (flashcards, question finder,
      glossary) — the six home-page cards are effectively the draft.

## From the tutoring rework (2026-08-14) — still open

- [ ] **Request re-indexing** for `tutoring.html`, `/`, and `faq.html` if you
      haven't already (the home-page item above supersedes `/`).
- [ ] **Update your Tutorful profile prices** to £65/hour so the site and
      profile agree.
- [ ] **Update the tutoring agreement document** to spell out group billing
      (per half-term/term, by number of lessons).
- [ ] If any other profile lists the old £80 single-lesson price, update it.

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
