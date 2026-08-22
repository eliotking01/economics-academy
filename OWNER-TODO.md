# Owner To-Do — things only Eliot can do

Kept out of the published site via `_config.yml`. **One prioritised list**,
consolidated 2026-08-16 at the end of the site-wide overhaul and
**re-consolidated 2026-08-22**, when it absorbed the three lists the 21 August
audits left behind — `seo/13-gsc-manual-todo-2026-08-21.md`,
`seo/15-notes-seo-manual-todo-2026-08-21.md` and
`seo/18-notes-content-approval-2026-08-21.md`. Those three now carry a
SUPERSEDED banner and are kept as the record of what was asked and decided;
nothing still open lives only there. Items are in priority order within each
group.

**Things that are already *wrong* still go in `docs/REVIEW-NOTES.md` (site) or
`docs/CONTENT_ISSUES.md` (flashcards), not here.** This file points at the
decisions waiting in those logs; it does not repeat them.

## Do next — this week

- [ ] **Search Console, after the notes push (live since 2026-08-22, merge
      `ee24918`) — 15 minutes.** Load one Edexcel and one AQA topic page on
      the live site and check the tab shows the new title and the page shows
      the byline. URL-inspect both and **Request indexing**. Re-submit
      `sitemaps/revision-notes.xml` so the new `lastmod` dates are picked up.
      Do **not** request a validation on any error type — see "Already
      scheduled" for when.
- [ ] **Look at a topic page in a browser — 10 minutes.** Nobody has. One
      Edexcel, one AQA, desktop and phone (Live Server is fine). Check: the
      board · module · code line and the byline under the heading are not
      crowding it — the heading group is now three lines of small text and if
      it feels crowded on a phone the credentials half can hide below 600px in
      one CSS rule; the "On this page" box reads as helpful; the Related
      topics pills wrap sensibly and do not look like buttons; the "Studying
      AQA instead?" sentence reads naturally; nothing jumps as the page loads.
      Then open `aqa-a2-micro/1-6-6-the-national-minimum-wage.html`, one of
      four pages whose contents list has a single entry, and decide whether
      that is acceptable until the page is expanded (see "Content work").
- [ ] **Read the twin-board map — 20 minutes, the highest-value review on this
      list.** 109 links say "Studying AQA instead? *[topic]* covers this on
      AQA" (and the reverse). A wrong row sends a student to the wrong board's
      content. Print it: `python3 scripts/notes_twins.py`; the 57 deliberately
      unpaired: `python3 scripts/notes_twins.py --unpaired`. Start with the
      four rows I am least sure of, then skim the rest:
      - Edexcel 3.5.3 Wage Determination → AQA 1.6.3 Competitive Wage
        Determination (AQA splits this across 1.6.3–1.6.5)
      - Edexcel 3.4.6 Monopsony → AQA 1.6.4 Wage Determination: Monopsony
        (AQA has no monopsony page of its own)
      - Edexcel 1.3.4 Information Gaps → AQA 1.2.2 Imperfect Information (the
        measured best match was 1.8.6 Market Imperfections)
      - Edexcel 4.4.2 Market Failure in the Financial Sector → AQA 2.4.4 The
        Regulation of the Financial System (prose similarity only 0.062)
      A wrong row is one line in `scripts/notes_twins.py`.
- [ ] **One 30-second check in Kit**: confirm "double opt-in" (the
      confirmation email) is ON for form 9803307 — it's Kit's default, and
      the home page already promises "You will get a confirmation email
      first".
- [ ] **Send yourself a test signup** on the live home page and confirm the
      confirmation email arrives and you appear as a subscriber in Kit. This
      is the only thing that proves the form works end to end.

## Soon — before term starts

- [ ] **Re-run the web vitals against the live site — 20 minutes.** The notes
      SEO changes were measured only as a local A/B, which was too noisy to
      trust. Now they are live:
      `python3 seo/tools/run_lighthouse.py --out seo/lh-live-notes-seo` and
      compare with `seo/lh-live-after/` (same URLs, runs, flags and Lighthouse
      version — which is why the script exists). Expected answer: no change
      worth seeing. **CLS is the number that would matter** — a contents list
      and a byline now sit above the fold on all 166 pages. If LCP is
      genuinely up by more than ~200 ms, say so and the blocks get a second
      look.
- [ ] **Fix the Open Graph image — 30 minutes.** `og-image.png` is the logo at
      1200×1200, but every page declares `twitter:card = summary_large_image`,
      which wants ~2:1, so shared links render as a cropped logo. Make a
      1200×630 image — site name, "A-Level Economics Revision Notes", the
      board names, clean background (Canva will do it) — save it as
      `og-image-wide.png` and Claude Code wires it in and bumps the
      cache-busting `?v=`. Per-topic OG images are a generator job for later
      and need your design call first.
- [ ] **Check each exam board's licensing terms for hosting past papers.**
      The site already hosts all 281 paper PDFs itself, so this is due
      diligence on something already published, not a future decision. Look
      for the "copyright" or "using our materials" page on Pearson/Edexcel,
      AQA and OCR: is hosting complete past papers for free educational use
      permitted, is attribution wording required, does any embargo apply to
      recent series. Nothing needs taking down unless a term says so.
- [ ] **OCR A Level Paper 3, June 2023 — the question paper is missing.** Both
      PDFs at that path are the mark scheme, byte-identical. Download H460/03
      June 2023 from OCR and save it over the existing question-paper
      filename. No URL, link or sitemap change.
- [ ] **Check the economics of the glossary's authored definitions.**
      `_working/glossary/authored-review.md` lists the 138 definitions written
      *for* the glossary rather than lifted from the notes — the only wording
      on the site that is not the notes' own. Correct anything wrong in
      `glossary-data/authored.json`; Claude Code re-runs the extractor and
      builder.
- [ ] **Google Business Profile**: as an online-only service you can create a
      profile without a public address ("service area" business). It enables
      Google reviews, which show for brand searches — the single cheapest
      trust signal available. Context from the notes audit: you have
      impressions and no clicks on `a level economics tutor online` (56
      impressions, position 35), `online a level economics tutor` (47,
      position 23) and `a level economics tuition` (50, position 52). Those
      are the queries that pay; 23rd–52nd is nowhere, and the tutoring page is
      what has to convert. A separate piece of work — flagged so it is not
      lost.
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

## Content work — your judgement, at your pace

Everything here changes a word a student reads, so each page needs your
explicit yes and the wording is yours. Claude Code does the markup, the
rebuild and the checks.

- [ ] **Expand the seventeen thin pages.** Under 500 words in `<main>` against
      a site median of 741 and competitor pages of 1,200–2,000. Twelve are AQA
      micro, which makes it a section-level project rather than seventeen
      decisions. Per page: expand, merge into a neighbour, or leave it because
      the spec point genuinely is that small — **do not pad for word count**;
      a longer bad page ranks worse than a short good one. Thinnest first
      (words in `<main>`, measured 2026-08-21 by `seo/tools/notes_baseline.py`):

      | Page | Words |
      | --- | ---: |
      | `aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity` | 300 |
      | `aqa-a2-micro/1-4-1-production-and-productivity` | 345 |
      | `aqa-a2-micro/1-5-1-market-structures` | 367 |
      | `aqa-a2-micro/1-2-2-imperfect-information` | 368 |
      | `aqa-a2-micro/1-4-8-technological-change` | 372 |
      | `aqa-a2-micro/1-1-4-scarcity-choice-and-the-allocation-of-resources` | 390 |
      | `edexcel-theme-1/1-3-3-public-goods` | 399 |
      | `aqa-a2-micro/1-1-3-economic-resources` | 404 |
      | `edexcel-theme-4/4-2-1-absolute-relative-poverty` | 432 |
      | `edexcel-theme-1/1-2-1-rational-decision-making` | 442 |
      | `edexcel-theme-4/4-4-1-role-of-financial-markets` | 448 |
      | `edexcel-theme-1/1-1-2-positive-normative-statements` | 450 |
      | `aqa-a2-micro/1-5-8-the-dynamics-of-competition-and-competitive-market-processes` | 451 |
      | `edexcel-theme-4/4-1-3-pattern-of-trade` | 453 |
      | `aqa-a2-micro/1-2-4-behavioural-economics-and-economic-policy` | 465 |
      | `aqa-a2-micro/1-6-6-the-national-minimum-wage` | 477 |
      | `edexcel-theme-1/1-1-3-the-economic-problem` | 485 |

      Four pages will visibly improve the moment you do, because they have
      only one section and so a one-item "On this page" list:
      `aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets`,
      `aqa-a2-micro/1-6-6-the-national-minimum-wage`,
      `edexcel-theme-4/4-4-1-role-of-financial-markets`,
      `edexcel-theme-4/4-4-3-role-of-central-banks`. After each page:
      `python3 scripts/build_notes_pages.py`, then
      `python3 seo/tools/rewrite_notes_meta.py --apply` (refreshes its
      `dateModified`), then `python3 scripts/extract_glossary.py && python3
      scripts/build_glossary.py`.
- [ ] **Place the diagrams.** 72 of the 166 topic pages carry no image or
      inline SVG, and diagram/graph queries are 7–9% of your impressions — the
      third-largest pattern in your Search Console data. The 72-row table —
      page, matching diagram already on disk, suggested action — is §7 of
      `seo/17-notes-seo-audit-2026-08-21.md`: **43 to place** (the PNG already
      exists in `images/diagrams/`), **9 to draw** (consumption function,
      accelerator, total/average/marginal product, competition spectrum, a
      discriminating employer's MRP, bond price v yield, terms of trade v
      export revenue, unit labour costs, monetary transmission mechanism),
      **20 need none**. Start with the 43; `comparative-advantage.png` first —
      it exists, it is drawn, and it is on no page at all (Edexcel 1.1.5 and
      4.1.3, AQA 1.4.2 would all use it). Work down in theme order marking
      each "place", "draw" or "not needed". Convention in
      `revision-notes/CLAUDE.md`: `diagram-figure` / `-image` / `-caption`, a
      caption opening `Figure N:`, real alt text, `width` and `height`, and
      the first image on a page never `loading="lazy"`;
      `verify_image_dimensions.py` and `verify_diagram_geometry.py` catch a
      wrong dimension.
- [ ] **Decide the open economics findings in `docs/REVIEW-NOTES.md`.** Each
      needs an explicit instruction before a page is touched. Open as of
      2026-08-22 (evidence under each ID): **N-Q8** on AQA `2-2-2` (the role of
      expectations — new prose, tested by a live question); **N-Q11** (`2.4.1`
      and `2.4.2` substantially duplicate each other — restructuring);
      **N-Q7** (`2-6-5` dated HDI figures); **N-Q12, N-Q13, N-Q14, N-Q16,
      N-Q17, N-Q18, N-Q19, N-Q20** (spec alerts that promise what the page
      does not teach, or a textbook simplification — each is "write the
      missing paragraph or trim the claim"); **C4** (AQA `2-2-3`, `1-5-6`
      cross-reference Edexcel theme numbers — needs reading, not grepping);
      **C5** (`2-1-2` unemployment-rate denominator v the ILO definition);
      **G4** (`Regulation` defined twice, neither reads as a definition);
      **G1** (`/contact.html` at 343 words is not indexed — a content decision,
      not to be rushed). `docs/CONTENT_ISSUES.md` has nothing open: 35 fixed,
      1 rejected.
- [ ] **Fourteen definitions you have already written are invisible to the
      glossary — optional, about an hour.** Five pages carry a definition
      under a plain `<strong>Term:</strong>` rather than a `key-definition`
      chip, so `extract_glossary.py` cannot see it: `aqa-a2-micro/1-1-2-…`
      (Needs, Wants), `1-1-3-economic-resources` (Goods, Services, Renewable
      and Non-renewable resources), `1-6-4-…` (Monopsony power, Trade unions),
      `edexcel-theme-2/2-4-2-injections-withdrawals` (Investment, Government
      Spending, Exports, Savings), `2-4-3-…` (Short-run and Long-run
      equilibrium). Converting them is markup, not wording, and lets
      `Monopsony` come out of `authored.json`; several need a `rewrite` rule
      in `curation.json` because they open "These are…", which is the
      judgement part. Improves the glossary rather than search, so the smaller
      prize.
- [ ] **Skim what the notes audit applied without asking, and veto anything
      that reads wrong** — items 2, 4–6 and 10–12 of
      `seo/18-notes-content-approval-2026-08-21.md`: the 36 titles that use a
      page's own short display name; the nine chrome strings ("Updated", "On
      this page", "Related topics", "Studying AQA instead?", "Written by",
      "About the author", …); the two Edexcel "Balance of Payments" titles
      (kept distinct by theme label — recommended leave); the 20 descriptions
      that run 159–168 characters (recommended leave — the only fix is 20
      hand edits); the trimmed Theme 3 hub title; the seven rewritten hub
      descriptions, which are Claude's sentences on your facts. Each is a
      one-line change if you want it different.

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
- **Note the date whenever you rank-check** — in the "Rank-check log" at the
  bottom of this file, ten seconds. Every Search Console figure in the August
  audits carries a caveat because nobody wrote down when the site was being
  searched by the people building it; brand queries were 2.7% of impressions
  but 51% of clicks. A line here is what lets an October export be read
  rather than second-guessed.
- **Glance at Search Console monthly**: Performance for clicks/position
  trends, and Pages → "Why pages aren't indexed" for anything unexpected.
  When something there looks wrong, **check the `Last crawled` date on the row
  before believing the verdict** — the report lags by days and routinely
  describes a version of a page that no longer exists. Exporting the CSVs into
  a dated folder under `seo/gsc-exports/` and running
  `python3 seo/tools/gsc_reconcile.py <folder>` does that check for you, and
  will say plainly which verdicts contradict the repo. Read `revision-notes`
  and `practice-questions` separately (Indexing → Sitemaps → the per-sitemap
  "See page indexing" icon) and ignore the site-wide total, which the 283
  exam-board PDFs drag down.
- **Never request a validation until the fix is live and you have checked it
  live yourself.** A failed validation costs a fortnight. And **never validate
  "Not found (404)"**: all ten URLs correctly return 404 and the validation is
  guaranteed to fail.
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
- [ ] **~21 September 2026 — first read of the new notes titles, 10 minutes.**
      Export Search Console performance for the previous 28 days filtered to
      `/revision-notes/`. There is **no clean pre-change baseline** — the notes
      were not complete before the 2026 exams and the 21 August export is
      half your own searching — so compare *shares and positions*, not raw
      totals; September is term starting, so traffic rises whatever you do;
      discount anything at position 1–3 with no clicks. Titles usually show a
      CTR effect within 2–4 weeks of recrawl; position moves take longer.
      Read it as measuring **both** title changes together (AQA codes off
      21 Aug, Edexcel codes off 22 Aug, D54). If average position on topic
      queries is flat after six weeks, titles aren't the constraint and the
      next lever is content depth and diagrams.
- [ ] **~22 September 2026 GSC check**: compare tutoring.html against its
      2026-08-08 baseline (position 26.27, 440 impressions, 17 clicks) and
      check the home page held or improved (baseline: 223 clicks, 2,463
      impressions, position 17.35, CTR 9.05%). These two comparisons are
      clean. The D45 wait was overridden on 2026-08-15 (D50), so treat any
      movement on revision-notes and past-papers pages as directional only
      (their baselines: notes hub 361 clicks pos ≈9.5, edexcel-b 158, ocr
      133, aqa 51).
- [ ] **1 October 2026 — re-export the Search Console CSVs** into
      `seo/gsc-exports/01-10-2026/` (Indexing → Pages → each row under "Why
      pages aren't indexed" → Export, plus the indexed list, same filenames as
      21 August) and re-run the audit. One command:
      `python3 seo/tools/gsc_reconcile.py seo/gsc-exports/01-10-2026 --diff seo/gsc-exports/21-08-2026`.
      What to expect, stated in advance so it can be checked rather than
      rationalised, is in `13-…` task 8b. The three things to look at hardest:
      whether "Excluded by 'noindex' tag" has cleared to zero; whether
      revision-notes indexed has climbed from 60 towards 130–150; and whether
      `/revision-notes/` has recovered the 22 clicks and three ranking
      positions it lost in August — if not, that is a question in its own
      right and the biggest on the site.
- [ ] **1 October 2026 — decide on `sitemaps/pdfs.xml`.** If Google has still
      indexed only 11 of the 283 PDFs, stop submitting them. Not because they
      cost crawl budget — that was measured and they do not, beyond one burst
      on 8–9 August — but because a sitemap should list URLs you expect to be
      indexed. The change is scoped and ready as Action 3 in `seo/12-…`.
- [ ] **Early November 2026 — the term-time Search Console export.** The
      notes strategy was built on 28 contaminated, out-of-season days, and the
      May–June re-export was parked because the notes were not complete then.
      The autumn term is the first clean window: once a few weeks of it have
      accrued, export Queries and Pages for a 28-day slice to
      `seo/gsc-exports/term-time-2026-autumn/` and ask Claude Code to re-run
      the `seo/14-notes-keyword-brief.md` §1 pattern analysis and note what
      moved.
- [ ] **Spring 2027 — the URL question.** `seo/16-url-structure-and-redirect-options.md`
      sets it out: the URLs are frozen because GitHub Pages cannot issue a
      301, the gain from renaming is small, and you were mid-way through an
      indexing recovery. Revisit after a full term of data on the new titles.
- [ ] **Optional — a year-on-year Search Console comparison, 4 minutes**
      (`13-…` task 7a): Performance → Compare → Last 28 days v same period
      last year, Page tab filtered to `/past-papers/` and `/revision-notes/`.
      Settles whether August's hub-page losses were seasonal. Skip if the
      property has no 2025 data — the October read answers it later.
- [ ] **Optional — a keyword tool.** Skip for now: 166 pages are not yet
      ranking for the terms you already know about. If ever: Google Keyword
      Planner (free, banded), Google Trends (seasonality), or Ahrefs/Semrush
      at ~£99/month only if you would use it monthly.

## Rank-check log

Note the date whenever you search for the site yourself; a spike in Search
Console is then explainable rather than alarming.

- **18–21 August 2026** — heavy, during the GSC and notes audits (Claude and
  Eliot both). Brand queries were 2.7% of impressions and 51% of clicks in
  the 28 days to 21 August: treat that window's click and CTR figures as junk.
- **22 August 2026** — the six UK-IP SERP checks for the title formula
  (`seo/14-notes-keyword-brief.md` §2).

## Done — kept only where the DATE matters to a later measurement

- **2026-08-22 — the revision-notes on-page SEO pass is live** (merge
  `ee24918`): topic-first titles and descriptions on 166 topics and 7 hubs,
  spec codes off both boards' titles and the AQA headings, a spec sub-label,
  contents list, related topics and twin-board link on every topic page, four
  definitions, and **Eliot named as author** on every topic page and in the
  `LearningResource` schema (D53–D55). Google's recrawl of the 166 starts from
  this date; the ~21 September read above measures it. The UK-IP SERP check
  confirmed the title formula the same day.
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
- [ ] **A small photo in the "About the author" box** on the 166 topic pages
      (Save My Exams has one). It is an `<img>` on 166 pages, so it wants a
      decision on weight first.
- [ ] **Per-topic Open Graph images** with the topic name on them — a
      generator job once the 1200×630 site image above exists.

**Shipped, from ROADMAP's "Now" list** — both were the reason that file existed
and both are live, so it had nothing left to say:

- Glossary and formulae merged 2026-08-09 — 325 terms, 34 formulae, three pages.
- Interactive flashcards live — six decks with Leitner spaced repetition.
