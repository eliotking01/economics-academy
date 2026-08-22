# Revision notes SEO — things only you can do

> ## ⚠️ SUPERSEDED — 2026-08-22
>
> **For what to do now, read `OWNER-TODO.md`** — the one list of everything
> only Eliot can do. Every open item here is there: tasks 5, 13, 14, 15 and 17
> under "Do next" and "Soon", 6 and 9 under "Soon", 19, 20 and 21 under
> "Content work", 10, 11, 12 and the parked 2 under "Already scheduled".
>
> This file is kept as the record of what was asked and decided on 21 and
> 22 August: tasks 1, 3, 4, 16 and 18 done, task 2 parked, and the reasoning
> behind each. The work it describes merged to `main` on 2026-08-22 (merge
> `ee24918`) and is live.

21 August 2026. Companion to `seo/14-notes-keyword-brief.md` (the strategy) and
`seo/16-url-structure-and-redirect-options.md` (the URL question). Nothing here
can be done by Claude Code in the repo — each item needs your judgement, your
words, your Google account or your money.

Ordered by return per minute spent. Tasks 1–5 are worth doing this week;
6–9 are worth doing before term starts; 10–12 are optional.

**Status, 22 August 2026.** Tasks 1, 3, 4, 16 and 18 are done. Task 2 is
parked (no usable term-time window exists yet). Task 4 — the byline — merged
to `main` and went live the same day (merge `ee24918`). Everything still open
is in `OWNER-TODO.md`.

---

## 1. Check the SERPs from a UK IP — DONE, 22 August 2026

Eliot checked the six queries from a UK IP. Three sites dominate the top
results across all six: Economics Help, tutor2u and Save My Exams. Only tutor2u
puts the unit code in its titles; the other two lead with the topic name. That
is the pattern the US-routed sample found, so the title formula stands.
Recorded as a dated note in `seo/14-notes-keyword-brief.md` §2.

*The original ask is kept below for the record.*

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

## 2. Re-export Search Console over a term-time window — PARKED, 22 August 2026

Not worth doing yet. The revision notes were not complete until after the
1 May – 30 June 2026 window, so a term-time export from then would measure a
site that no longer exists. The first usable term-time window is the autumn
term 2026: export a 28-day slice once a few clean weeks of it have accrued
(early November at the earliest). Two consequences:

- There will never be a clean *pre-change* term-time baseline, because the
  notes were not complete before the titles changed. Task 10 therefore tracks
  the autumn trend rather than comparing against a baseline.
- The brief stays directional until then, which it already says about itself.

*The original ask is kept below for the record.*

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

## 3. Decide the two content questions Claude Code will ask — DONE, 22 August 2026

**a.** Yes — the code was stripped from the 79 AQA headings in commit
`94a0726` (21 August 2026) and now sits in the sub-label under every heading.
**b.** Confirmed: the site-local AQA codes stay, and stay off the AQA titles.

*The original ask is kept below for the record.*

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

## 4. Write your author byline and credentials — DONE, 22 August 2026

Eliot supplied the byline, asked for the bio to be drawn from the about page,
approved both drafts and the placement the same day, and chose "6+ years"
over "6 years". Published under **Eliot King**. On the branch, in one pass:

- a byline under the heading on all 166 topic pages, and an "About the
  author" box between the related topics and the three buttons — both from
  `scripts/notes_extras.py`, which is the one place the wording lives;
- `id="eliot-king"` on the about page's profile section, so the byline link
  lands on the photo and the intro, and the `Person` `@id` every root page
  already uses is now a real fragment;
- `author` in the `LearningResource` schema switched from the organisation to
  that `Person` (`seo/tools/rewrite_notes_meta.py`);
- `verify_seo.py` assertion 20: the byline, the box and the schema must all
  name the same person, by the same `@id`. Proved able to fail three ways on
  1-2-2-demand before it shipped.

The shipped wording is below. The only change from the approved draft is
"6 years" → "6+ years" in the byline and "for six years" → "for over six
years" in the bio, which is the prose form about.html also uses.

**Byline, as shipped:**

> Written by **Eliot King** — First-Class BSc (Hons) Economics, University of
> Bath · 6+ years teaching A-Level Economics · Edexcel A, Edexcel B, AQA and OCR

**Bio, as shipped:**

> **Eliot King** is a First-Class BSc (Hons) Economics graduate from the
> University of Bath and the founder of Economics Academy. Eliot has taught
> A-Level Economics for over six years across Edexcel A, Edexcel B, AQA and
> OCR, supporting over 100 students with a particular focus on the exam
> technique and essay structure that mark schemes reward.

Not done, and worth a thought later: a small photo in the author box (Save My
Exams has one; it is an `<img>` on 166 pages, so it wants a decision on
weight), and whether the credentials half of the byline should hide on a
phone, where the heading group is now three lines of small text. Task 14 —
look at a page — is where that gets judged.

*The drafts as approved, and the original ask, are kept below for the record.*

Eliot supplied the byline and asked for the bio to be drawn from the about
page. Publish under **Eliot King**.

**Byline, as supplied:** Eliot King, First-Class BSc Economics (Hons),
University of Bath, 6 years teaching, Edexcel A, Edexcel B, AQA and OCR.

**Byline, tidied for the page (draft):**

> Written by **Eliot King** — First-Class BSc (Hons) Economics, University of
> Bath · 6 years teaching A-Level Economics · Edexcel A, Edexcel B, AQA and OCR

Two tidies: "BSc (Hons) Economics" is the order the about page's credentials
list and its `Person` schema already use, and "teaching" is qualified with
"A-Level Economics" so the line makes sense away from the about page.

**Bio (draft, adapted from the about page's opening paragraph):**

> Eliot King is a First-Class BSc (Hons) Economics graduate from the University
> of Bath and the founder of Economics Academy. Eliot has taught A-Level
> Economics for six years across Edexcel A, Edexcel B, AQA and OCR, supporting
> over 100 students with a particular focus on the exam technique and essay
> structure that mark schemes reward.

Two things changed from the about page: it is in the third person (the about
page says "I"), and the four boards are named. Every claim in it is already on
the about page. One inconsistency to settle: the byline says "6 years"; the
about page says "over 6 years" and "6+ years".

**Once approved, the single pass is:** a byline under the H1 on all 166 topic
pages; an "About the author" box at the foot of each carrying the bio and
linking to `/about.html#eliot-king`; that `id` added to the about page's
profile section (the JSON-LD already uses `about.html#eliot-king` as the
`Person` `@id`, but no element on the page carries it); and `author` in the
`LearningResource` schema switched from the `#organization` node to that
`Person`. Visible text on 167 pages, so it needs an explicit yes.

*The original ask is kept below for the record.*

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
*(22 August 2026: task 2 is parked and there will be no clean pre-change
term-time baseline — see task 2. Watch positions and shares across the autumn
exports instead.)*
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

## 16. Decide the AQA heading question — DONE, 21 August 2026

Eliot said yes; the code came off the 79 AQA headings in commit `94a0726`.
Item 1 of `seo/18-notes-content-approval-2026-08-21.md` records it.

*The original ask is kept below for the record.*

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

---

*Tasks 18 to 21 were added later on 21 August 2026, when Eliot took the four
decisions in `seo/18-notes-content-approval-2026-08-21.md` items 1, 7, 8 and 9.
Items 1 is done. The other three are yours, and 18 is the one that unblocks
work already scoped and waiting.*

---

## 18. Write four definitions — DONE, 21 August 2026

Eliot supplied three and approved a fourth. In and live on the branch:
*perfectly competitive labour market* (AQA 1.6.3), *injection* and *withdrawal*
(Edexcel 2.4.2), *financial markets* (Edexcel 4.4.1). All four are extracted
into the glossary as `origin=chip`.

**1.3.6 was asked about and deliberately left.** It already defines all five
relationships in its own table; the umbrella phrase is not one anyone searches.

**Worth knowing for task 19**: those five table definitions cannot currently be
harvested into the glossary. `curation.json`'s `tables` list is the approved
mechanism, but `extract_glossary.tables_on()` only offers a table as a
candidate when a column header contains "definition", "meaning", "what it
means" or "description" — and 1.3.6's column is headed **"Explanation"**.
Adding that word would newly expose 34 tables as *candidates* for review, not
harvests, since the curation list is opt-in; most of the 34 are
"Limitation | Explanation" and would rightly never be approved. It is a
one-line generator change and it belongs with task 19, not on its own.

*The original ask is kept below for the record.*

## 18a. The original ask — 15 minutes

You said yes to adding key terms and to ask if the definitions needed writing.
**Four of them do.** The audit report overstated this and has been corrected:
it counted pages carrying a `key-definition` chip, which is how the glossary
finds a definition — not whether the page answers "what is X", which is what a
searching student needs. Eight of the twelve already answer it.

These four do not define their own subject anywhere on the page. One or two
sentences each, in your words, and Claude Code puts them in as chips in one
pass:

| Page | What it needs a definition of |
| --- | --- |
| `aqa-a2-micro/1-3-6-the-interrelationship-between-markets.html` | what it means for two markets to be interrelated — the page defines joint, competitive and composite demand in a table but never the idea itself |
| `aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html` | what a perfectly competitive labour market is |
| `edexcel-theme-2/2-4-2-injections-withdrawals.html` | what an injection and a withdrawal are — the page defines each *example* (Investment, Savings, Exports) beautifully but not the two categories |
| `edexcel-theme-4/4-4-1-role-of-financial-markets.html` | what a financial market is — the page opens straight into its six functions |

Three more pages have topics that are not really definable terms, and forcing a
definition onto them would make them worse. I have not asked for those:
`1-7-3` (a list of policies), `2-5-4` (a discussion of trade-offs) and `1-6-4`
(a set of causes — though see task 19, which covers it another way).

---

## 19. Fourteen definitions you have already written are invisible to the glossary

**Not a writing job — a markup one, and it changes no words.** Flagging it
because it is your call whether it is worth doing, and it wants an hour.

Five pages carry a definition under a plain `<strong>Term:</strong>` instead of
a `key-definition` chip, which is the one thing `extract_glossary.py` looks
for. `glossary-data/CLAUDE.md` names this exact situation — "three cases here
turned out to have the real definition already in the notes, just somewhere the
extractor could not reach".

| Page | Definitions the glossary cannot see |
| --- | --- |
| `aqa-a2-micro/1-1-2-…` | Needs, Wants |
| `aqa-a2-micro/1-1-3-economic-resources.html` | Goods, Services, Renewable resources, Non-renewable resources |
| `aqa-a2-micro/1-6-4-…` | Monopsony power, Trade unions |
| `edexcel-theme-2/2-4-2-injections-withdrawals.html` | Investment (I), Government Spending (G), Exports (X), Savings (S) |
| `edexcel-theme-2/2-4-3-…` | Short-run equilibrium, Long-run equilibrium |

Converting them would add fourteen glossary entries in your own words and let
**`Monopsony` come out of `authored.json`**, which that file says is meant to
shrink exactly this way.

**Why it is an hour and not ten minutes.** Several open with "These are…" or
"This occurs where…", which reads wrong as a glossary lead-in, so each needs a
`rewrite` rule in `curation.json` — the mechanism you instructed on 2026-08-07.
That is judgement, not typing.

**My recommendation: worth doing, but after the four in task 18.** It improves
the glossary rather than the notes' search performance, so it is the smaller
prize.

---

## 20. Expand the seventeen thin pages — your judgement, at your pace

`seo/18-notes-content-approval-2026-08-21.md` item 8 has the full list with
word counts, thinnest first. You said you can expand these.

**Take the AQA micro twelve as one project.** Twelve of the seventeen are AQA
micro, which makes this a section at half the site's median depth rather than a
scatter of short pages. The thinnest is 300 words against a site median of 741
and competitor pages of 1,200–2,000.

**Four of them will visibly improve the moment you do.** These have only one
section, so the new "On this page" list has a single entry, which looks like a
fault and is really the thinness showing:

- `aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html`
- `aqa-a2-micro/1-6-6-the-national-minimum-wage.html`
- `edexcel-theme-4/4-4-1-role-of-financial-markets.html`
- `edexcel-theme-4/4-4-3-role-of-central-banks.html`

**Do not pad for word count.** A longer bad page ranks worse than a short good
one. If a specification point genuinely is that small, say so and it stays.

When a page is expanded, re-run:

```bash
python3 scripts/build_notes_pages.py
python3 seo/tools/rewrite_notes_meta.py --apply   # refreshes its dateModified
python3 scripts/extract_glossary.py && python3 scripts/build_glossary.py
```

---

## 21. Place the diagrams — your judgement, at your pace

`seo/17-notes-seo-audit-2026-08-21.md` §7 is the 72-row table: the page, the
matching diagram already on disk, and a suggested action. You said you will add
these.

**Start with the 43 that need no drawing.** Each already has a matching PNG in
`images/diagrams/`; placing one is a `<figure>`, an `<img>` with `width` and
`height`, and a caption opening `Figure N:`. Nine want a diagram drawn and
twenty need none.

**`comparative-advantage.png` first.** It exists, it is drawn, and it is
currently on **no page at all**. Three pages in the table would use it —
Edexcel 1.1.5 and 4.1.3, and AQA 1.4.2.

Diagram and graph queries are 7.3–9.2% of your impressions depending on the
filter, and 43% of your topic pages currently carry no diagram at all.

**The convention** is in `revision-notes/CLAUDE.md`: `diagram-figure` /
`-image` / `-caption`, real alt text describing what the diagram shows rather
than "diagram", and the first image on a page is never `loading="lazy"`.
`verify_image_dimensions.py` and `verify_diagram_geometry.py` will both fail if
a dimension is wrong, which is the safety net.
