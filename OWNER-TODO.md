# Owner To-Do — things only Eliot can do

Kept out of the published site via `_config.yml`. One prioritised list,
consolidated 2026-08-16 at the end of the site-wide overhaul. Items are in
priority order within each group.

**On 2026-08-20 this absorbed `ROADMAP.md`** (now `_archive/ROADMAP.md`), which
held intended work as opposed to findings. Both its "Now" items had shipped;
what survived is the "Ideas and someday" section at the bottom. **Things that
are already *wrong* still go in `docs/REVIEW-NOTES.md`, not here** — that
distinction was ROADMAP's and it is worth keeping.

## Do next

- [ ] **One 30-second check in Kit**: confirm "double opt-in" (the
      confirmation email) is ON for form 9803307 — it's Kit's default, and
      the home page already promises "You will get a confirmation email
      first".
- [ ] **Send yourself a test signup** on the live home page and confirm the
      confirmation email arrives and you appear as a subscriber in Kit. This
      is the only thing that proves the form works end to end.

## Soon

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
  When something there looks wrong, **check the `Last crawled` date on the row
  before believing the verdict** — the report lags by days and routinely
  describes a version of a page that no longer exists. Exporting the CSVs into
  a dated folder under `seo/gsc-exports/` and running
  `python3 seo/tools/gsc_reconcile.py <folder>` does that check for you, and
  will say plainly which verdicts contradict the repo.
- **Never edit generated pages by hand** (Claude knows which are which — if
  in doubt, ask before editing anything under revision-notes/, flashcards/,
  practice-questions/ or the glossary).
- **Content mistakes you spot** go in docs/REVIEW-NOTES.md (site) or
  docs/CONTENT_ISSUES.md (flashcards) rather than being fixed on the spot,
  so every wording change stays deliberate.

## Already scheduled

- [ ] **~20 September 2026 — validate "Alternate page with proper canonical
      tag"** in Search Console (Indexing → Pages → that issue → Validate Fix).
      **Not before.** The count is meant to rise before it falls — it went
      9 → 15 between 8 and 21 August as Google re-crawled each old
      `…/index.html` twin and learned it is now unlinked. Validating while it
      is still climbing would fail and cost a fortnight. Step-by-step in
      `seo/13-gsc-manual-todo-2026-08-21.md`, task 8a.
- [ ] **1 October 2026 — re-export the Search Console CSVs** into
      `seo/gsc-exports/01-10-2026/` and re-run the audit. One command:
      `python3 seo/tools/gsc_reconcile.py seo/gsc-exports/01-10-2026 --diff seo/gsc-exports/21-08-2026`.
      What to expect, stated in advance so it can be checked rather than
      rationalised, is in `13-…` task 8b. The two things to look at hardest:
      whether "Excluded by 'noindex' tag" has cleared to zero, and whether
      `/revision-notes/` has recovered the 22 clicks and three ranking
      positions it lost in August.
- [ ] **1 October 2026 — decide on `sitemaps/pdfs.xml`.** If Google has still
      indexed only 11 of the 283 PDFs, stop submitting them. Not because they
      cost crawl budget — that was measured and they do not, beyond one burst
      on 8–9 August — but because a sitemap should list URLs you expect to be
      indexed. The change is scoped and ready as Action 3 in `seo/12-…`.
- [ ] **~22 September 2026 GSC check**: compare tutoring.html against its
      2026-08-08 baseline (position 26.27, 440 impressions, 17 clicks) and
      check the home page held or improved (baseline: 223 clicks, 2,463
      impressions, position 17.35, CTR 9.05%). These two comparisons are
      clean. The D45 wait was overridden on 2026-08-15 (D50), so treat any
      movement on revision-notes and past-papers pages as directional only
      (their baselines: notes hub 361 clicks pos ≈9.5, edexcel-b 158, ocr
      133, aqa 51).

## Done — kept only where the DATE matters to a later measurement

- **2026-08-21 — Search Console index audit.** Full reconciliation in
  `seo/11-gsc-index-audit-2026-08-21.md`. Dates that matter to a later reading:
  - **Two validations confirmed *Started*** — "Excluded by 'noindex' tag" (26
    URLs) and "Redirect error" (1). Both were begun around 8 August, so they
    are due to finish between now and early September. **Do not restart
    either** — Google's own guidance is to let a cycle complete.
  - **Indexing requested for 6 pages whose Search Console verdict was older
    than the page**: `/about.html`, `/contact.html` and four Edexcel Theme 1
    notes pages (`1-1-6`, `1-2-3`, `1-2-4`, `1-3-2`). All six had been edited
    since Google last crawled them; `/about.html` and `/contact.html` were
    last crawled in **April**, before the August rewrite of both.
  - **Crawl stats read**: PDF 15% of requests, HTML 57%, JS 12%, CSS 9%,
    other 3%. **Average response time 108 ms** — which means Googlebot is not
    being held back by the hosting, so the low crawl rate is Google's choice,
    not a capacity limit. PDF detail: 491 requests / 379 MB / 211 ms over
    90 days, with a spike to ~128 a day on 8–9 August and nothing since.
  - **Performance exported** to
    `seo/gsc-exports/21-08-2026/performance-28d-compare/`. Site clicks
    206 → 248 (+20%), impressions 13,612 → 25,851 (+90%). This is the
    pre-October baseline.
- **2026-08-21 — indexing requested for the last 3 URLs** (`/practice-questions/aqa-a2-macro/`,
  `/about.html`, `/contact.html`), closing out the 2026-08-16 indexing round.
- **2026-08-21 — phone skim done**, all looks fine: marking (packages, enquiry
  box, the two real example panels), home (photo, wording, form), About and
  Contact.
- **2026-08-16 — marking examples live** (merge `fca6d93`): the two real
  anonymised PDFs replaced the "coming soon" panels — the marking page's
  journey is now complete end to end, from example to payment to
  confirmation.
- **2026-08-16 — indexing requested** for the 9 pages that already rank:
  `/revision-notes/`, `/revision-notes/edexcel-theme-4/`,
  `/revision-notes/aqa-a2-micro/`, `/revision-notes/aqa-a2-macro/`,
  `/past-papers/` and the four board pages (`edexcel`, `aqa`, `ocr`,
  `edexcel-b`). Same ~22 September clock as the entries below — and these
  are the pages whose baselines that check compares against, so a recrawl
  landing this week is what makes the comparison meaningful.
- **2026-08-16 — three verification loops closed**, all previously
  unverifiable from outside: **Formspree dashboard** checked on both forms
  (`xblapyky` contact, `mqadgbbw` tutoring pop-up) — notification address
  and spam filtering confirmed; **Stripe dashboard** checked — all 8 payment
  links confirmed redirecting to `confirmation.html` after payment, which
  closes the last open question on the marking journey; **LinkedIn link**
  on the About page clicked and confirmed landing on the right profile.
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

## Ideas and someday — not scheduled, not promised

Absorbed from `ROADMAP.md` on 2026-08-20. These are things worth building, not
things that are wrong; anything already broken belongs in `docs/REVIEW-NOTES.md`
or `docs/CONTENT_ISSUES.md` instead.

- [ ] **Migrate the revision notes from MathJax to KaTeX.** The glossary
      pre-renders KaTeX at build time; the LaTeX-bearing notes pages still load
      MathJax 3 from a CDN, so the same formula looks slightly different in the
      two places. Converging would also drop a CDN dependency and make formulae
      render with JavaScript off site-wide. The biggest single item on this
      list, and entirely optional.
- [ ] **A downloadable PDF glossary per board.** Deliberately not in v1 — it
      needs a headless browser or a PDF library in a repo with no build
      dependencies, and becomes a second artefact that drifts from the page.
      The print stylesheet already covers Cmd+P. Revisit if students ask.

**Shipped, from ROADMAP's "Now" list** — both were the reason that file existed
and both are live, so it had nothing left to say:

- Glossary and formulae merged 2026-08-09 — 325 terms, 34 formulae, three pages.
- Interactive flashcards live — six decks with Leitner spaced repetition.
