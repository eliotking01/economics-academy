# Revision notes SEO — things only you can do

21 August 2026. Companion to `seo/14-notes-keyword-brief.md` (the strategy) and
`seo/16-url-structure-and-redirect-options.md` (the URL question). Nothing here
can be done by Claude Code in the repo — each item needs your judgement, your
words, your Google account or your money.

Ordered by return per minute spent. Tasks 1–5 are worth doing this week;
6–9 are worth doing before term starts; 10–12 are optional.

---

## 1. Check the SERPs from a UK IP — 20 minutes

The competitor SERP evidence behind the title formula was sampled through a
US-routed search tool. UK results for UK exam queries can differ. Before the
new titles ship, open an incognito window and search these six, and note the
top five results for each:

- `aggregate demand a level economics`
- `externalities a level economics notes`
- `government failure economics a level`
- `price elasticity of supply a level`
- `division of labour a level economics`
- `edexcel a level economics monopoly revision notes`

What you're looking for: does the topic name lead the titles that rank? If yes,
the formula stands. If UK results look materially different — PMT PDFs
dominating, or an aggregator you've never heard of taking the top three — say
so and the formula gets revisited.

Write what you find into `seo/14-notes-keyword-brief.md` §2 as a dated note.

---

## 2. Re-export Search Console over a term-time window — 15 minutes

The strategy in `seo/14-notes-keyword-brief.md` is built partly on the 28 days
to 21 August 2026. That window has two problems you already spotted:

- **It is contaminated by your own searching.** You and Claude have been working
  on this site all month, and every Google search either of you ran that
  surfaced the site counted as an impression. Brand queries are only 2.7% of
  impressions, but they are **51% of clicks** — so the click and CTR figures in
  that export are junk. Search Console has no way to filter this out.
- **It is the dead season.** Results day and the middle of the summer holiday.
  Student search behaviour in October looks nothing like it.

The brief already re-runs its analysis over the subset least likely to be you —
non-brand queries, zero clicks, position worse than 10 — and every headline
conclusion survives, so nothing needs changing today. But to move this from
directional to reliable:

1. In Search Console → Performance → Search results, set the date range to
   **1 May – 30 June 2026** (term time, running into the exam period).
2. Export Queries and Pages.
3. Save to `seo/gsc-exports/term-time-2026-05-06/`.
4. Ask Claude Code to re-run the §1 pattern analysis over that window and update
   `seo/14-notes-keyword-brief.md` §1 with a dated note on anything that moved.

Going forward, one cheap habit: when you're rank-checking, note the date. A line
in `OWNER-TODO.md` saying "rank-checked heavily 18–21 Aug" is enough to explain
a spike later.

---

## 3. Decide the two content questions Claude Code will ask — 10 minutes

The audit produces `seo/18-notes-content-approval-<date>.md`. Two decisions in
it are worth pre-empting, because the whole run's value depends on them:

**a. The AQA H1 code prefix.** 79 AQA pages have an H1 like
`2.6.5 Economic Growth and Development`. The 87 Edexcel pages have a bare topic
name. Recommendation: strip the code from the AQA H1s so all 166 match, and
show the code in a sub-label underneath instead. It's a visible-text change on
79 pages, so it needs your explicit yes.

**b. The AQA site-local codes generally.** The `1.x.y` / `2.x.y` codes are
deliberately not AQA's real 7136 codes — that was ratified and I am not
proposing you undo it. But be clear on the cost: an AQA student searching a
real spec code finds nothing, and an AQA student comparing your codes to their
spec sees numbers that don't match. Spec-code searches are 0.1% of your
impressions, so the cost is small. The brief keeps the codes off AQA titles for
this reason. Confirm you're happy with that.

---

## 4. Write your author byline and credentials — 30 minutes

Every site outranking you on these queries has a named author with visible
credentials. Save My Exams puts a byline and an author page on each note.
TutorChase prints "Cambridge University — BA Hons Economics, 8 years tutoring".
You have real credentials and a real business; the pages don't say so.

Write, in your own words:

- A one-line byline: name, degree, institution, years teaching, boards taught.
- A two-to-three sentence bio for an `/about` anchor the byline links to.
- Confirm the name you want to publish under.

Once you've written it, Claude Code can put it on all 166 pages and into the
`LearningResource` schema as a `Person` author in a single pass.

This is the highest-value item on the list. It is also the one nobody else can
write.

---

## 5. Search Console: submit the updated sitemap and spot-check — 15 minutes

**Only after the changes are live and you have loaded a real URL yourself.**

1. Load two changed pages on the live site — one Edexcel, one AQA — and check
   the browser tab shows the new title.
2. In Search Console, use the URL Inspection tool on both, then
   **Request indexing**.
3. Re-submit `sitemaps/revision-notes.xml` so the new `lastmod` dates are
   picked up.
4. Do **not** request a validation on any error type — that's a separate
   process covered in `seo/13-gsc-manual-todo-2026-08-21.md`.

---

## 6. Fix the Open Graph image — 30 minutes

`og-image.png` is the logo at 1200×1200 (square), but every page declares
`twitter:card = summary_large_image`, which wants roughly 2:1. Shared links
render as a cropped logo.

Make a 1200×630 image: site name, "A-Level Economics Revision Notes", the two
board names, clean background. Canva will do it in ten minutes. Save it as
`og-image-wide.png` and Claude Code can wire it in and bump the cache-busting
`?v=`.

Better still, and worth considering later: a per-topic OG image with the topic
name on it. That's a generator job, not a manual one, but it needs your design
decision first.

---

## 7. Decide what to do about the 17 thin pages — 1 hour of your judgement

Seventeen topic pages carry under 500 words in `<main>`, the thinnest at 300.
The median across the site is 741. Competitors ranking above you on these
topics run considerably longer with worked examples and diagrams.

Claude Code will list them with their word counts in the audit report. Your
call, per page: expand it, merge it into a neighbour, or leave it because the
spec point genuinely is that small. Nobody but you can make that judgement, and
padding for word count would make the pages worse.

The list to expect, thinnest first: `1-1-2-the-nature-and-purpose-of-economic-activity`,
`1-4-1-production-and-productivity`, `1-5-1-market-structures`,
`1-2-2-imperfect-information`, `1-4-8-technological-change` (all AQA micro),
`1-1-4-scarcity-choice-and-the-allocation-of-resources`, then
`1-3-3-public-goods` (Edexcel), `1-1-3-economic-resources`,
`4-2-1-absolute-relative-poverty` and `1-2-1-rational-decision-making`.

---

## 8. Decide the diagram plan — 45 minutes

72 of the 166 topic pages contain no image or inline SVG. Diagram and graph
queries are **9.2% of your impressions** — the third-largest pattern in your
Search Console data, ahead of "notes" and "revision". You already have 84 SVGs
in `images/diagrams/svg/`.

Claude Code will produce a table of which of the 72 pages have a matching
existing diagram and which would need one drawn. Your job is to go through it
and mark: place this one, draw this one, this topic doesn't need a diagram.

Placing an existing diagram on a page is a content change, so it waits for your
yes on each.

---

## 9. Google Business Profile and the tutoring queries — 30 minutes

Not a notes-page task, but it showed up in the same data and is worth 30
minutes. You have impressions and no clicks on
`a level economics tutor online` (56 impressions, average position 35),
`online a level economics tutor` (47, position 23) and
`a level economics tuition` (50, position 52). Those are the queries that pay.

Caveat, per task 2: some of those impressions may be you checking where you
rank. The positions are the robust part and they're the point — 23rd, 35th and
52nd is nowhere, and no amount of self-searching moves an average position that
far down.

The notes pages are the top of that funnel; the tutoring page is what has to
convert. That is a separate piece of work — flagging it here so it doesn't get
lost.

---

## 10. Optional: watch what the new titles do — 10 minutes, in a month

Around 21 September, export Search Console performance for the previous 28 days
filtered to `/revision-notes/`, and compare it to the term-time baseline from
task 2 — **not** to the 21 August export, whose clicks are half your own.
Titles usually show a CTR effect within two to four weeks of Google recrawling;
position moves take longer.

Two things to watch for so you don't fool yourself: September is term starting,
so traffic rises whatever you do, and any rank-checking you did in the window
inflates impressions on the exact terms you were checking. Compare *shares and
positions*, not raw totals, and discount anything at position 1–3 with no
clicks.

If average position on topic queries is flat after six weeks, the titles aren't
the constraint and the next lever is content depth and diagrams.

---

## 11. Optional: a keyword tool, if you want real volumes — £0–£99/month

Everything in the brief is built on live SERPs plus your own Search Console
data, and that second half is both contaminated and out of season (task 2).
Search Console also only ever shows queries you already appear for. A
keyword tool would show demand you're invisible to.

Free: Google Keyword Planner (needs a Google Ads account, gives banded
volumes), Google Trends for relative seasonality. Paid and worth it only if you
would actually use it monthly: Ahrefs or Semrush at around £99/month, or
Keywords Everywhere at roughly £10 for a credit pack.

My honest view: skip it for now. You have 166 pages that aren't yet ranking for
the terms you already know about. Fix those first.

---

## 12. Optional: decide the URL question properly — 1 hour, in the spring

`seo/16-url-structure-and-redirect-options.md` sets it out. Short version: the
URLs are frozen because GitHub Pages cannot issue a 301, the gain from renaming
is small, and you are mid-way through an indexing recovery. Revisit after a
full term of data on the new titles.

---

*Tasks 13 to 17 were added on 21 August 2026 by the on-page audit
(`seo/17-notes-seo-audit-2026-08-21.md`), which found five things it could not
do itself and one it could not check.*

---

## 13. Re-run the web vitals against the live site — 20 minutes, after the push

The audit measured Core Web Vitals as a local before/after A/B, because nothing
is pushed and a live run would have measured the old pages. It was too noisy to
trust: the LCP spread *within* one configuration reached 3.4 seconds, and
`seo/09-web-vitals-baseline.md` hit exactly the same wall in 2026-08
(7-run spread of 1.7 to 8.0 seconds on a notes page).

Once the changes are live:

```bash
python3 seo/tools/run_lighthouse.py --out seo/lh-live-notes-seo
```

Compare it to `seo/lh-live-after/`. Same URLs, same run count, same flags, same
Lighthouse major version — which is the whole reason that script exists rather
than a hand-run CLI.

**What to look for.** The one figure the local run could trust was +75 ms of
LCP on Edexcel 1.2.2, alongside −93 ms of total blocking time and a +3
performance score, so the expected answer is "no change worth seeing". **CLS
is the number that would matter if it moved** — a contents list now sits above
the fold on all 166 pages. Locally it did not move at all, on any of the six.

If LCP is genuinely up by more than about 200 ms on the live site, say so and
the contents block gets a second look.

---

## 14. Look at a topic page — 10 minutes

Not optional, and not something this session could do. Every automated check is
green and the markup was read line by line, but nobody has opened one of these
pages and looked at it.

Open two in Live Server — one Edexcel, one AQA — and check:

- The **board · module · code** line under the heading is not crowding it.
- The **"On this page"** box reads as helpful rather than as clutter, at
  desktop width and on a phone.
- The **Related topics** pills at the foot wrap sensibly and do not look like
  buttons you are meant to press.
- The **"Studying AQA instead?"** sentence reads naturally where it sits.
- Nothing jumps as the page loads.

Then look at one of the four pages whose contents list has a single entry —
`aqa-a2-micro/1-6-6-the-national-minimum-wage.html` is the clearest — and
decide whether a one-item list is acceptable until that page is expanded.
It is item 8 of `seo/18-notes-content-approval-2026-08-21.md`.

---

## 15. Read the twin-board map — 20 minutes

```bash
python3 scripts/notes_twins.py
python3 scripts/notes_twins.py --unpaired
```

109 links now say "Studying AQA instead? *[topic]* covers this on AQA", and
the reverse. The map was built by measuring how similar each pair of pages
actually is and then reading every row, but it is economics judgement in the
end and **a wrong row sends a student to the wrong board's content** — the one
failure `docs/audit/DO-NOT-BREAK.md` is most emphatic about.

The four I am least confident in are item 10 of the approval document. Start
there, then skim the rest. 57 pages have no twin on purpose; `--unpaired`
shows them with the best score found, so you can see what was considered.

This is the highest-value twenty minutes of review in the whole audit.

---

## 16. Decide the AQA heading question — 10 minutes

Item 1 of `seo/18-notes-content-approval-2026-08-21.md`, and it is the one
decision the audit could not make for you because two of your own documents
disagree.

`seo/14-notes-keyword-brief.md` §6 says strip the spec code from the 79 AQA
`<h1>`s. `docs/audit/DO-NOT-BREAK.md` says it "stays until the day-45 read"
because on near-identical cross-board pairs it is the last textual
differentiator.

The audit re-measured that: **no cross-board pair is above 0.95 similarity and
only six are above 0.80**, and all six are now differentiated four other ways
as well. The code is also now visible in a sub-label on all 166 pages, so
nothing is lost from the page.

Read item 1, then say yes or "wait for day 45". Either is defensible; leaving
it undecided is the only bad answer, because the AQA half of the site keeps a
convention the Edexcel half does not.

---

## 17. Note the date whenever you rank-check — ongoing, 10 seconds

Repeating task 2's closing suggestion because it now has teeth. Every Search
Console figure in this audit carries a caveat, and the reason is that nobody
wrote down when the site was being searched by the people building it.

A line in `OWNER-TODO.md` — "rank-checked heavily 18–21 Aug" — is enough to
explain a spike later. Ten seconds now saves an hour of second-guessing an
export in October.
