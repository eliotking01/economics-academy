# Search Console — things only you can do

21 August 2026. Companion to `seo/11-gsc-index-audit-2026-08-21.md` (the
analysis) and `seo/12-index-fix-actions-2026-08-21.md` (the repo work).

Everything here happens in Search Console at
**<https://search.google.com/search-console>**, on the
`economicsacademy.co.uk` property. Nothing here needs a code change first
unless a task says so.

Total time for tasks 1–5: **about 25 minutes today.** Tasks 6–8 are later.

---

## Status at 21 August, end of day

| Task | State |
| --- | --- |
| 1 — Check the two validations | ✅ **Done.** Both report **Started**. |
| 2 — Validate "Excluded by 'noindex' tag" | ⏭️ **Not needed** — task 1 showed it already running. |
| 3 — Request indexing, six stale pages | ✅ **Done.** All six requested. |
| 4 — Do *not* validate "Not found (404)" | ✅ Understood. |
| 5 — Per-sitemap filter | ✅ Done, figures match. |
| 6 — Crawl stats | ✅ **Done — and it changed two conclusions.** See task 6a. |
| 6a — PDF crawl time series | ✅ **Done.** Spike 8–9 Aug, then back to baseline. `pdfs.xml` stays. |
| 7 — Performance export | ✅ **Done.** Analysed in `11-…` §3a. |
| 7a — Year-on-year comparison | 🟡 **NEW. Optional.** Settles a confound. |
| 8 — Wait, then re-audit 1 October | ⏳ Running. |

**Nothing needs you now.** Task 7a is optional; everything else is done or
waiting on Google. Next action is 8a on ~20 September.

---

## Before you start — the one rule

> **Never request a validation until the fix is live and you have checked it
> live yourself.**

Not after the commit. Not after the push. After you have loaded the real URL on
the real domain and seen the fix. For the two issues in task 1, **I have already
done that check for you today** — all the evidence is in `11-…` §5, including
the raw HTTP responses. So you can act on those two with confidence.

**If a validation fails:** the issue goes back to its previous state, the
affected URLs return to *Pending*, and you have to start a fresh cycle — roughly
another fortnight. Nothing is broken and there is no penalty; you just lose the
time. That is why task 4 tells you *not* to validate one particular issue.

---

## Task 1 — Check the two validations you already started · ✅ DONE

You started validations on **Excluded by 'noindex' tag** and **Redirect error**
around 8 August (per `06-gsc-checklist.md` Step 4). They are about thirteen days
old. Google says validation *"typically takes up to about two weeks, but in some
cases can take much longer."*

**I cannot see their state from the CSV exports** — the exports contain only
URLs and crawl dates. You have to look at the screen. This is the first task
because task 2 depends entirely on what you find.

### Click by click

1. Left sidebar → **Indexing** → **Pages**.
2. Scroll to **Why pages aren't indexed**.
3. Click the row **Excluded by 'noindex' tag** (newer Search Console wording:
   *URL marked 'noindex'*).
4. Look at the top of the detail page for a **validation banner**. It will say
   one of: *Not started* · *Started* · *Looking good* · *Passed* · *Failed*
   · *N/A*.
5. Note it down. Then click the browser back button and repeat for
   **Redirect error**.

### What to do with each answer

| It says | Do this | Why |
| --- | --- | --- |
| **Started** or **Looking good** | **Nothing. Leave it alone.** | Google's documentation: *"Wait for a validation cycle to complete before requesting another cycle."* Clicking again restarts the clock and delays your result. |
| **Passed** | Nothing — it worked. Go to task 3. | The pages will re-enter the index as they are recrawled. |
| **Not started** | Go to task 2 and start it. | It never ran. |
| **Failed** | Go to task 2 and start a fresh one. | It cannot fail on the merits — see `11-…` §5. A failure means the sample was taken at an unlucky moment. |

### Outcome — 21 August

**Both report *Started*.** So the puzzle above resolves the harmless way: the
validations are running, and the page-indexing export simply has not caught up
with the recrawls yet. That is normal — the report lags by days.

**Do nothing further with either.** Google's documentation is explicit that you
wait for a cycle to finish. You should get an email when each completes;
expect that any time from now to early September, since they started around
8 August and the typical cycle is "up to about two weeks, sometimes longer".

---

## Task 2 — Validate "Excluded by 'noindex' tag" · ⏭️ NOT NEEDED

**Task 1 showed this validation is already *Started*.** Do not start another —
that would restart the clock and delay the result. Everything below is kept as
the record of why it will pass.

---

### (original task, for reference)

**This is the highest-value thing you can do today.** 26 pages of your own
original AQA A-Level economics writing are outside Google's index for a reason
that stopped being true three weeks ago.

### Why it will pass

I fetched all 26 live today. Every one: **HTTP 200, no `<meta name="robots">`
tag, no `X-Robots-Tag` header.** The tags were removed across July 2026 as you
finished each page; Google's last crawl of every single one predates its
removal. Full per-file trace in `11-…` §8, full URL list in appendix A1.3.

### Click by click

1. **Indexing** → **Pages** → **Excluded by 'noindex' tag**.
2. Top right of the detail page → **VALIDATE FIX**.
3. Confirm. The banner changes to **Started**.

### What to expect afterwards

- Search Console immediately tests a sample. Because there is genuinely no
  noindex tag, it will pass that test and enter *Started* rather than stopping.
- Google then recrawls all 26 over the following days.
- **Up to two weeks**, sometimes longer, before it reads *Passed*.
- You will get an email when it finishes, pass or fail.
- The 26 pages should then start appearing in the index. Expect that over
  2–4 weeks after the validation passes, not instantly.

### Do not

Do not also Request Indexing on these 26 individually. Validation already forces
a recrawl of every affected URL, and you would burn your daily quota (task 3
needs it) for no extra effect.

---

## Task 3 — Request indexing for six stale pages · ✅ DONE 21 August

All six requested. Google says indexing "can take up to a week or two", though a
recrawl often lands within a day or two. **Expect four of the six to be indexed
and two to be uncertain**: `/contact.html` at 343 words is the kind of page
search engines routinely decline, and `/about.html` is a judgement call. If the
four revision-notes pages are still out in October, tell me — that would be a
different problem from the one diagnosed here.

---

### (original task, for reference)

Six pages carry a "Crawled — currently not indexed" verdict that is **older than
the page it describes.** Every one has been edited since Google last looked.
`/about.html` and `/contact.html` were last crawled in **April**, before you
rewrote them both in August.

| URL | Google last crawled | You last changed it |
| --- | --- | --- |
| `https://economicsacademy.co.uk/about.html` | 2026-04-03 | 2026-08-21 |
| `https://economicsacademy.co.uk/contact.html` | 2026-04-08 | 2026-08-16 |
| `https://economicsacademy.co.uk/revision-notes/edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html` | 2026-02-24 | 2026-08-13 |
| `https://economicsacademy.co.uk/revision-notes/edexcel-theme-1/1-2-4-supply.html` | 2026-04-14 | 2026-08-13 |
| `https://economicsacademy.co.uk/revision-notes/edexcel-theme-1/1-3-2-externalities.html` | 2026-04-22 | 2026-08-13 |
| `https://economicsacademy.co.uk/revision-notes/edexcel-theme-1/1-1-6-types-of-economies.html` | 2026-07-09 | 2026-08-13 |

### Click by click, once per URL

1. Click the **search box at the very top** of Search Console (it reads
   *"Inspect any URL in economicsacademy.co.uk"*).
2. Paste the full URL. Press Enter. Wait for the result.
3. Click **TEST LIVE URL** (top right). Wait — it takes 15–30 seconds.
4. Confirm two things on the live result:
   - it says **"URL is available to Google"**;
   - under **Coverage**, the **User-declared canonical** is the same URL you
     typed.
   Both are true today — I checked all six live — but check anyway, because that
   is the habit that keeps you out of trouble.
5. Click **REQUEST INDEXING**. Wait for the "Indexing requested" confirmation.
6. Repeat for the next URL.

### What to expect afterwards

- Google says *"Indexing can take up to a week or two"*, though a recrawl often
  happens within a day or two.
- There is a **daily quota** of manual indexing requests per property — roughly
  10–12. Six leaves you headroom.
- Being recrawled does not guarantee being indexed. `/contact.html` is 343 words
  and search engines routinely decline to index contact pages; if it stays out,
  that is normal, not a fault.

---

## Task 4 — Do **not** validate "Not found (404)" · 0 minutes

There are 10 URLs in this issue and it is tempting to clear them. **Do not.**

All ten correctly return 404. Nine belong to the AQA AS section you deleted in
May 2026, or to broken relative links inside it; the tenth is an Edexcel B mark
scheme that was never uploaded. Validation re-checks the URL's **response
code** — not the links pointing at it — and that code is 404 and should stay
404. The validation is guaranteed to fail and cost you a fortnight.

There is also no alternative available: GitHub Pages has **no redirect mechanism
of any kind**, so "just 301 them" is not an option, and creating stub pages at
correctly-deleted URLs was already ruled out in `04-decisions.md`.

Google drops persistent 404s from the report by itself over a few months. Leave
it. Same advice as `06-gsc-checklist.md` Step 4, and it still holds.

---

## Task 5 — Learn the per-sitemap filter · ✅ DONE 21 August (figures match)

This is the single change that will make Search Console legible to you, and it
takes two clicks. Your headline indexed rate of **42.8%** is depressing and
misleading, because 283 exam-board PDFs are dragging it down. Your HTML pages
are at **66.5%**.

### Click by click

1. **Indexing** → **Sitemaps**. You should see eight rows: `sitemap.xml` and its
   seven children. If a child is missing or errored, that is a real problem —
   tell me.
2. Click the **"See page indexing"** icon at the right of the
   `sitemaps/revision-notes.xml` row. (Or: go to **Indexing → Pages** and use
   the **All submitted pages** dropdown at the top to pick a single sitemap.)
3. You are now looking at that section alone.

### What you should see today

| Sitemap | pages | indexed | read it as |
| --- | ---: | ---: | --- |
| `flashcards` | 7 | 7 | done |
| `past-papers` | 5 | 5 | done |
| `practice-questions` | 173 | 155 | **the success story** — was zero on 8 August |
| `past-paper-questions` | 90 | 76 | same story |
| `core` | 7 | 5 | task 3 addresses the other 2 |
| `revision-notes` | 179 | 60 | **the one to watch** — 26 clear via task 2, 89 are queued |
| `pdfs` | 283 | 11 | ignore. See `11-…` §7 |

Google's own counts will differ from these by a few either way — the report lags
by days. The shape is what matters.

**From now on, read `revision-notes` and `practice-questions` separately and
ignore the site-wide total.** That is what the sitemap-index structure was built
for on 8 August.

---

## Task 6 — Check Crawl stats by file type · ✅ DONE 21 August

### What you found

| File type | Share of crawl requests |
| --- | ---: |
| HTML | 57% |
| **PDF** | **15%** |
| JavaScript | 12% |
| CSS | 9% |
| Other | 3% |

**Average response time: 108 ms.**

### What it changed — two things, and one of them matters a lot

**1. The 108 ms is genuinely good news, and it sharpens the diagnosis.**
Anything under about 300 ms means Googlebot is not being held back by your
hosting, which is what you would expect from static files on GitHub Pages behind
a CDN. Google's stock explanation for "Discovered — currently not indexed" is
that crawling "was expected to overload the site" — at 108 ms that is plainly
not what is happening.

So the limit is not how much Googlebot **can** fetch from you. It is how much it
**wants** to. That is crawl *demand*, which tracks how valuable Google currently
judges the site — and it is a slower thing to shift than a queue. I have revised
the confidence in `11-…` §4 from "high" down to "moderate-to-high" because of
this. A queue drains by itself; a judgement does not.

**2. The 15% put the PDF question back open.** I had ruled the PDFs out as
competition for crawl, on the grounds that the page-indexing export shows none
crawled since 6 August. 15% is above the "under 10% confirms it" threshold I set
before looking, so I have to take that back.

Both readings can be true, because Crawl stats covers **90 days** — about 23 May
to 21 August — and 77 of those days precede the sitemap submission, when Google
*was* crawling your PDFs heavily. A 15% share of a mostly-pre-submission window
says nothing about today. Task 6a settles it.

---

## Task 6a — The PDF crawl time series · ✅ DONE 21 August

### What the chart showed

PDF only, 90 days: **491 crawl requests, 379 MB, 211 ms average.** The line runs
at a flat baseline of roughly 4 requests a day, with a bump around 16 June, then
a **spike to about 128 requests in a day on 8–9 August** — the same two days as
the HTML burst — and a **fall back to baseline** from about 12 August.

That is the third branch of the table I gave you: a spike, not a stop and not a
continuation.

### What it means

| Question | Answer |
| --- | --- |
| Did submitting `pdfs.xml` cause a crawl? | **Yes** — roughly 140 requests above baseline |
| One-off or ongoing? | **One-off.** Back to baseline within days |
| Costing crawl budget now? | **No** |
| New PDFs indexed as a result? | **Zero** |

**Decision: leave `sitemaps/pdfs.xml` exactly as it is.** The crawl cost is real
but already spent, and removing the sitemap today cannot recover it. `12-…`
Action 3 is parked until 1 October, when the question becomes simply whether
eight weeks produced any new indexing.

### It also corrected a mistake of mine

I told you this morning that "Google has not crawled a single PDF since
6 August", reading the `Last crawled` column of the page-indexing export at face
value. **That was wrong** — the export lags Crawl stats by days and had not
caught up. Corrected in `11-…` §4 and §7.

### And it produced the most useful number in the whole audit

If 491 PDF requests are 15% of the total, Googlebot made roughly **3,270
requests to your entire site in 90 days — about 36 a day, or four fetches per
page in three months.** For a 746-URL site that is a low crawl rate, and with a
108 ms average response time it is demonstrably not your hosting causing it.
That is the crawl-demand diagnosis in `11-…` §4, with a number attached to it
for the first time.

---

### (original task 6, for reference)

I concluded in `11-…` §7 that the 283 PDFs are **not** eating the crawl budget
your pages need — because the export shows no PDF crawled since 6 August. That
conclusion depends on the report being current, and the report lags. This
settles it properly.

### Click by click

1. Left sidebar → **Settings** (the cog, near the bottom).
2. Under **Crawling**, click **Crawl stats** → **OPEN REPORT**.
3. Look at **Total crawl requests** over the last 90 days. There should be a
   visible spike around 9–10 August.
4. Scroll to **By file type**. Note the share for **PDF**.

### What to expect

If PDF is a small share (say under 10%) and the spike is HTML, my reading is
confirmed and there is nothing to do. **If PDF is a large share**, tell me — it
would change the recommendation in `11-…` §7 and make Action 3 in `12-…` worth
doing now rather than in October.

Also glance at **Average response time**. If it is under about 300 ms, crawl
rate is not being limited by your hosting, which is what you would expect from
static files on GitHub Pages.

---

## Task 7 — Export a fresh Performance report · ✅ DONE 21 August

### Where it went, and what I did with your files

You put it in `seo/gsc-exports/21-08-2026/performance-28d-compare/` — exactly
the right place. **I have deleted and moved nothing.** You offered, but nothing
needed it: all six CSVs are the standard Search Console Performance export and
four of them are directly useful. `Countries.csv` and `Devices.csv` are less
interesting for this question but cost nothing to keep, and `Devices.csv` turned
out to be the cleanest source for the site totals.

### What it says

Full analysis in `11-…` §3a. The headlines:

| | previous 28d | last 28d | |
| --- | ---: | ---: | ---: |
| Clicks | 206 | **248** | **+20%** |
| Impressions | 13,612 | **25,851** | **+90%** |

**The newly-indexed pages earned 50 clicks and 3,316 impressions from a standing
start of zero.** Practice questions: 0 → 28 clicks. Past-paper questions:
0 → 17. Those sections did not exist in Google's index a fortnight ago.

**But your established hubs lost ground.** `/revision-notes/` is down from 84 to
62 clicks and from position 9.1 to 12.1. `/past-papers/ocr/` went 14 clicks to 2.
The `past-papers` section as a whole lost 19 clicks.

I cannot tell you how much of that is duplicate consolidation (which
`06-gsc-checklist.md` predicted would look exactly like this) and how much is
the exam calendar — the comparison window ends in late July, the current one
runs through results day, and past-paper demand is at its annual floor in
August. Hence task 7a.

---

## Task 7a — A year-on-year comparison · 4 minutes · 🟡 **OPTIONAL, but it removes a confound**

Only worth doing if the property has data back to August 2025.

1. **Performance** → **Search results**.
2. Date range → **Compare** → **Custom** → set **Last 28 days** against **Same
   period last year**.
3. Look at `/past-papers/` and `/revision-notes/` specifically, using the
   **Page** tab with a "URL contains" filter.

**What it tells you:** if past-papers clicks fell by a similar proportion in the
same weeks of 2025, the decline in task 7 is seasonal and there is nothing to
investigate. If 2025 held steady across the same window, the decline is ours and
belongs on the October agenda.

If the property has no 2025 data, skip it — the October read answers the same
question, just later.

---

### (original task 7, for reference)

`seo/performance-pages.csv` is your pre-submission baseline. 255 more pages are
now indexed and nothing yet records whether they earned anything.

1. Left sidebar → **Performance** → **Search results**.
2. Date range → **Compare** → **Last 28 days** vs **Previous period**.
3. **EXPORT** (top right) → **Download CSV**.
4. Save it into `seo/gsc-exports/21-08-2026/` as
   `performance-28d-compare.csv`.

Two things to look at while you are there, both predicted in
`06-gsc-checklist.md` Step 3:

- **Impressions may have dipped** on the ten duplicate pairs while Google merges
  each pair into one URL. Combined clicks should recover and then exceed the old
  total. A dip here is the fix working, not failing.
- `/past-papers/edexcel/index.html` has already moved from *indexed* to
  *alternate page with proper canonical tag*. That is the first pair collapsing.

---

## Task 8 — Wait, then re-audit on 1 October 2026 · **diarise it**

**Do nothing else until then.** Re-submitting, re-requesting or changing things
again during consolidation makes the signal noisier, not stronger. This was the
hardest instruction in `06-gsc-checklist.md` and it is the hardest one here.

### On or about 20 September — one item only

Validate **"Alternate page with proper canonical tag"**.

Not before. This count is *meant* to rise before it falls: it went 9 → 15 in a
fortnight, because Google has to re-crawl each old `…/index.html` URL to learn
it is now unlinked, and every one it re-crawls lands in this bucket. Validating
while it is still climbing would fail. Around 20 September it should be falling.

**Indexing → Pages → Alternate page with proper canonical tag → VALIDATE FIX.**

### On 1 October — the re-audit

1. **Indexing → Pages.** For each row under *Why pages aren't indexed*, click
   in and **EXPORT → Download CSV**. Also export the **indexed** list.
2. Save all of them into a new folder, `seo/gsc-exports/01-10-2026/`, keeping
   the same filenames as today's export.
3. Tell me, and I will re-run the reconciliation. (If Action 1 in `12-…` has
   been built by then, it is one command:
   `python3 seo/tools/gsc_reconcile.py seo/gsc-exports/01-10-2026 --diff seo/gsc-exports/21-08-2026`.)

### What I expect the October export to show

Stated now so it can be checked rather than rationalised later:

| | Expectation |
| --- | --- |
| Excluded by 'noindex' tag | **0 or close to it.** If it is still 26, the validation never ran — go back to task 1. |
| Revision notes indexed | Up from 60 towards 130–150 |
| Discovered — not indexed (HTML) | Down from 121, most of the way to zero |
| Discovered — not indexed (PDF) | **Still around 195.** Not a failure. |
| Crawled — not indexed (HTML) | 6 or fewer |
| Alternate page with proper canonical tag | Falling from 15 |
| Not found (404) | Still 10, possibly fewer. Do not chase it. |
| PDFs indexed | Still around 11 |

Add one more thing to check in October: **`/revision-notes/` clicks and average
position.** It fell from 84 clicks at position 9.1 to 62 at position 12.1 in the
last 28 days. If it has recovered, that was consolidation noise. If it has not,
it is a question in its own right and the biggest one on the site.

**If revision-notes indexing has not moved by October**, the queue explanation in
`11-…` §4 was wrong and it becomes a site-authority question instead. That is
the point at which the conversation changes — and it is a genuinely different
conversation, not more of this one.

---

## Order of play

| # | Task | When | State |
| --- | --- | --- | --- |
| 1 | Check the two existing validations | done | ✅ both *Started* |
| 2 | Validate "Excluded by 'noindex' tag" | — | ⏭️ not needed, already running |
| 3 | Request indexing for the six stale pages | done | ✅ |
| 4 | **Do not** validate "Not found (404)" | never | ✅ |
| 5 | Learn the per-sitemap filter | done | ✅ |
| 6 | Crawl stats by file type | done | ✅ |
| 6a | PDF crawl time series | done | ✅ `pdfs.xml` stays |
| 7 | Export the Performance comparison | done | ✅ |
| 7a | Year-on-year comparison | optional | 🟡 |
| 8a | Validate "Alternate page…" | ~20 September | ⏳ |
| 8b | Re-export everything and re-audit | 1 October | ⏳ |

**Nothing in this file waits on a change from `12-…`.** That is worth saying
plainly: every action available to you today is available today, because the
repo-side work was already done — some of it three weeks ago. `12-…` Action 3
is now parked until 1 October and needs nothing from you before then.

---

## Revision log

**21 August 2026, end of day.** Updated after you worked through tasks 1–7.
Tasks 1, 3, 5, 6 and 7 marked done with their outcomes recorded; task 2 marked
redundant; two new tasks added:

- **6a** (PDF crawl time series) — because task 6's 15% figure reopened a
  question I had closed. **Now done**, and it both settled the PDF question
  (leave the sitemap alone) and corrected a factual error of mine.
- **7a** (year-on-year) — because task 7's data cannot separate consolidation
  from exam seasonality on its own. Still optional and still open.

The October expectations in task 8 are unchanged, with one addition: if
`/revision-notes/` has not recovered its clicks and position by then, that
becomes an agenda item in its own right.
