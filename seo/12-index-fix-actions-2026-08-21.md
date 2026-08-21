# What I can fix in the repo — 21 August 2026

Companion to `seo/11-gsc-index-audit-2026-08-21.md`. **Nothing in this file has
been done.** It is a proposal; every item needs your approval before it touches
the repo, and anything reaching a published page needs your approval before it
is pushed.

---

## Read this before the list

**The audit found almost nothing wrong with the repo.** That is the honest
headline and I would rather state it than pad this file out.

Of the 427 published URLs Google has not indexed:

| Cause | URLs | Fixable in the repo? |
| --- | ---: | --- |
| Google has not crawled the page yet | 316 | **No.** It has read nothing, so there is nothing on the page to fix. |
| Exam-board PDFs Google crawled and declined | 75 | **No.** No canonical can be declared for a PDF on GitHub Pages. |
| Google's verdict predates your own fix | 32 | **No — already fixed.** Needs a recrawl, not a change. |
| In no export at all (2 deliberate noindex, 2 PDFs added 5 days ago) | 4 | **No.** Both pairs are correct as they are. |
| **Total not indexed** | **427** | |
| *of which: a real markup or configuration defect* | **0** | — |
| *of which: arguably thin (`/contact.html`, 343 words)* | 1 | Content decision — yours, not mine. |

`python3 seo/tools/verify_seo.py` passes 14/14 and
`python3 scripts/build_sitemap.py --check` exits 0 with no `WOULD CHANGE` lines.
There is no defect standing between your pages and Google's index.

So this file is short, and the "not worth doing" section at the end is longer
than the "do this" section. That is the correct shape for this audit.

**The highest-impact actions available to you are all in
`seo/13-gsc-manual-todo-2026-08-21.md`, not here.**

---

## Action 1 — Add `seo/tools/gsc_reconcile.py` · ✅ DONE 21 August

**Impact: medium. Effort: low. Risk: none. Touches no published page.**

### The problem

Producing `11-…` took most of a session of hand-analysis: parsing nine CSVs,
reconciling them against the true published inventory, splitting ghosts from
real URLs, and — the part that took longest and mattered most — spotting that
Google's "noindex" verdict on 26 pages **contradicts what the repo actually
contains**.

You will re-export these CSVs in October, and again after that. None of it
should be hand-work a second time. Nothing in `scripts/` or `seo/tools/` does
this job today:

| Existing tool | What it does | Why it does not cover this |
| --- | --- | --- |
| `seo/tools/inventory.py` | builds the page inventory from the repo | never reads a GSC export |
| `seo/tools/audit.py` | audits on-page SEO defects | never reads a GSC export |
| `seo/tools/verify_seo.py` | 14 assertions about the live markup | never reads a GSC export |
| `scripts/build_sitemap.py` | builds and checks the sitemaps | never reads a GSC export |

No new dependency: Python standard library only (`csv`, `json`, `pathlib`,
`subprocess`, `re`), in keeping with `scripts/CLAUDE.md` and the rest of
`seo/tools/`.

### What I would change

One new file, `seo/tools/gsc_reconcile.py`:

```
python3 seo/tools/gsc_reconcile.py seo/gsc-exports/21-08-2026
python3 seo/tools/gsc_reconcile.py seo/gsc-exports/21-08-2026 --diff seo/gsc-exports/08-08-2026
```

It would:

1. Rebuild the published inventory by importing `scripts/build_sitemap.py`'s own
   `excludes()` / `published()` / `url_for()` — so the inventory can never drift
   from the sitemap generator's view of what is published.
2. Assert every published URL lands in exactly **one** bucket and that the
   bucket totals sum to the inventory. Non-zero exit if they do not.
3. Print the §2 and §2a tables of `11-…` — reconciliation, and coverage by
   sitemap.
4. List **ghosts** (in an export, not published) and **unjudged** URLs
   (published, in no export) separately, because both are findings.
5. **Flag contradictions** — the valuable bit:
   - GSC says *noindex* but the repo file has no robots meta tag;
   - GSC says *404* but the file exists and is published;
   - GSC says *indexed* for a URL the site does not publish;
   - GSC's `Last crawled` predates the file's last commit (the verdict is
     stale — this catches all 32 stale verdicts found today, automatically).
6. With `--diff`, print the movement matrix of §3.

Roughly 250 lines. No writes; report only, like the other read-only tools in
`seo/tools/`.

### URLs affected

None. It reads.

### Risk

None. New file, not in CI, not published (`seo/` is in `_config.yml`'s
`exclude:` list), touches nothing.

### How it was verified

Run against `seo/gsc-exports/21-08-2026/`, it reproduces every number in
`11-…` §2 exactly: **746 published (463 HTML + 283 PDF), 319 indexed, 316
discovered, 73 crawled-NI, 26 noindex, 8 duplicate, 4 unjudged, 32 ghosts**, the
per-sitemap coverage table, and **32 stale verdicts** (26 phantom-noindex + 6
others). With `--diff seo/gsc-exports/08-08-2026` it reproduces the movement
matrix: 257 absent→indexed, 314 absent→discovered, **1** rescued from a
not-indexed state, 64→319 published-and-indexed.

Also checked:

- **Runs clean on the older 8 August export**, which has a different set of
  CSVs (no `discovered-…` file) — 574 unjudged, balances, exit 0.
- **The balance assertions actually fail when they should.** Injecting one URL
  into two category CSVs produces `[FAIL] no URL in two GSC categories at once
  (1 found)` and **exit 1**. That check was added *because* the first version
  absorbed the duplicate silently — `bucket_of()` takes the first match, so
  every downstream count would have been quietly wrong.
- **Standard library only** (`argparse`, `csv`, `re`, `subprocess`, `sys`,
  `pathlib`, `collections`), plus the repo's own `scripts/build_sitemap.py`.
- `--list <bucket>` prints one bucket's URLs; bad bucket names and bad
  directories exit 1 with a usable message.

### How long before GSC reflects it

Not applicable — it changes nothing on the site.

---

## Action 2 — Log the two content observations, do not fix them · ✅ DONE 21 August

**Impact: low. Effort: trivial. Risk: none. Touches no published page.**

### The problem

Two content facts surfaced that I am **not** going to act on, because
`CLAUDE.md` rule 2 says wording changes need an explicit instruction every time,
and both are your call:

1. **`/contact.html` is 343 words** — the thinnest page in `sitemaps/core.xml`,
   and it is "Crawled — currently not indexed". Search engines routinely decline
   to index contact pages, so this is probably normal rather than a defect. But
   it is the only page in the whole audit where thinness is a plausible
   contributor.
2. **`/flashcards/aqa/macro/?topic=2-6-2-trade` is indexed alongside
   `/flashcards/aqa/macro/`.** Decision **B3** in `04-decisions.md` chose to
   leave the 239 `?topic=` parameter URLs on the grounds that "every target's
   canonical names the clean URL and Google consolidates correctly". That is
   still true for 238 of them. One has not consolidated. This is evidence
   against B3's premise, but 1 URL in 239 is not a reason to reopen a settled
   decision or to change working JavaScript.

### What was changed

Two entries appended to `docs/REVIEW-NOTES.md` as **G1** and **G2**, in a new
dated section. No page edited, no wording touched.

`REVIEW-NOTES.md` is the right home by the repo's own routing: its header says
"things I found but did not fix", CLAUDE.md's table sends "known content
problems, logged not fixed" there, and `OWNER-TODO.md` states explicitly that
"things that are already *wrong* still go in `docs/REVIEW-NOTES.md`, not here".
`docs/CONTENT_ISSUES.md` was ruled out — it scopes itself to the flashcard
verification pass and says site-wide problems belong in REVIEW-NOTES instead.

**G1** records that `/about.html` is the second-shortest core page and carries
the same stale not-indexed verdict, which the morning analysis had not
connected to the `/contact.html` finding.

### URLs affected

None.

### Risk

None.

### How it was verified

The entries are there and say what the evidence was. One number in the first
draft was wrong — I wrote that every other `core.xml` page is "over 900 words",
then measured them: contact 343, **about 826**, home 982, marking 1,084,
privacy 1,373, tutoring 1,418, faq 1,811. Corrected in place, and the correction
is what surfaced `/about.html` as a second instance rather than a one-off.

---

## Action 3 — Ready for October, **not now**: stop submitting the PDFs

**Impact: low today. Effort: low. Risk: low. Not a breaking change.**

**Settled 21 August**, after the PDF crawl time series arrived (`13-…` task 6a).
Recorded here so it is ready to run on 1 October if the indexing outcome has not
moved. **Do not do this now.**

### Why not now

`sitemaps/pdfs.xml` advertises 283 exam-board PDFs, of which Google has indexed
**11 (3.9%)** — all eleven before the sitemap existed. 195 of the 316 URLs in
the "Discovered" bucket are these PDFs. So the case for removal looks strong
until you ask what removing it would actually save:

| | |
| --- | --- |
| Crawl cost of submitting them | **~140 requests, on 8–9 August** |
| Ongoing crawl cost | **None.** Back to ~4/day baseline since ~12 August |
| New PDFs indexed as a result | **Zero** |
| Recoverable by removing the sitemap now | **Nothing.** The cost is sunk |

The traffic case for keeping them is weak — 4 clicks and 511 impressions in
28 days, 1.6% of the site, down from the 7.2% quoted off the older baseline —
but weak benefit against zero ongoing cost still nets out in favour of leaving
it alone. The one real drawback, an unreadable coverage report, is already
solved by the per-sitemap filter in Search Console.

### What would trigger it

**1 October**, if `sitemaps/pdfs.xml` still shows 11 of 283 indexed. At that
point eight weeks and one crawl burst will have produced nothing, and a sitemap
should list URLs you expect Google to index.

### What I would change

`scripts/build_sitemap.py`, in `collect()`:

```python
if path.lower().endswith(".pdf"):
    pdfs.append((f"{SITE}/{path}", lastmod([path]), "0.4"))
    continue
```

Either drop that branch, or gate it behind a module-level `SUBMIT_PDFS = False`
so the decision is one legible line rather than a deletion. Then:

```
python3 scripts/build_sitemap.py          # after committing any page edits
python3 scripts/build_sitemap.py --check  # expect exit 0, no WOULD CHANGE
```

`sitemaps/pdfs.xml` would be deleted and `sitemap.xml` would drop its row.

### URLs affected

283 PDF URLs leave the sitemaps. **They stay published at exactly the same
addresses and keep every internal link from the past-papers hub pages.**

### Is this a breaking change? **No.**

No published URL moves, is deleted, or changes. `sitemaps/pdfs.xml` is itself a
published URL and would disappear — but it is a machine-readable file that only
Google fetches, has existed for under two weeks, and is not linked from any
page. It is named only inside `sitemap.xml`, which would be updated in the same
commit. **Worth flagging to you rather than doing quietly**, per `CLAUDE.md`
rule 7, but the risk is as close to zero as a URL removal gets.

### The cost

Set out in full in `11-…` §7. Short version: you keep the 11 indexed PDFs, you
keep the traffic they earn (currently 4 clicks and 511 impressions per 28 days),
and you lose the fastest discovery route for PDFs you add in future.

### How we would verify it worked

`build_sitemap.py --check` exits 0; `verify_seo.py` assertion 9 still passes
(it would then report 461 URLs across 6 sitemaps); the Sitemaps report in
Search Console shows the `pdfs` row gone.

### How long before GSC reflects it

The Sitemaps report updates within a few days. The 195 "Discovered" PDF rows
would drain out of the Pages report over several weeks — Google does not forget
a URL because it left a sitemap.

---

## Not worth doing

Things that look like problems and are not. Each was tested, not assumed.

### ❌ Add more internal links to the 89 queued revision-notes pages

This was my first instinct and **the data killed it.** Counting distinct
referring pages for every revision-notes page:

| GSC category | pages | median inbound links |
| --- | ---: | ---: |
| indexed | 60 | **10** |
| discovered — not indexed | 89 | **9** |
| excluded by noindex (stale) | 26 | 9 |

The queued pages are as well linked as the indexed ones. The same holds in
`practice-questions/`: indexed median 7, queued median 6. `link_graph.py` today
reports maximum depth 3, **zero** orphans and only 3 pages below 3 inbound
links, all three explained in `07-link-graph.md`.

There is no linking deficit to fix, and adding links would be work aimed at a
problem that does not exist. It would also risk deepening the anchor-text
monoculture `07-link-graph.md` warns about.

### ❌ Anything about "Discovered — currently not indexed"

Google has not fetched these pages. Nothing you change on them can affect a
decision made before they were read. Google's own documentation for this state
says "no action needed", and after ruling out thinness, templating, linking,
sitemap structure, robots directives and crawl-budget competition (`11-…` §4), I
agree with it.

### ❌ Remove the noindex from the 26 AQA pages

**There is no noindex on them.** There has not been since 30 July. `11-…` §8 has
the per-commit trace. This is the single most important thing to understand
about today's export.

### ❌ Create stub pages, or any kind of redirect, for the 10 URLs returning 404

All ten are correctly 404. `04-decisions.md` already ruled out stubs for the
deleted `aqa-as-micro` section, and **GitHub Pages offers no redirect mechanism
of any kind** — no `_redirects`, no `netlify.toml`, no `.htaccess`, no
`_headers`. Any advice that depends on "301 the old URL to the new one" is
simply unavailable to you and I will not propose it.

### ❌ Declare a canonical for the 8 duplicate PDFs

A PDF has no HTML `<head>`. The only mechanism is an HTTP `Link:` response
header, and GitHub Pages does not let you set response headers — confirmed live
today with a full header dump on one of these PDFs: GitHub's and Fastly's own
headers only, nothing site-controlled.

### ❌ Remove the `?topic=` parameter URLs

Decision **B3** settled this: it means changing working JavaScript in three
files (`flashcards.js`, `question-search.js`, `glossary-filter.js`) and altering
how deep links behave. One parameter URL out of 239 has failed to consolidate.
That is not enough to reopen it.

### ❌ Do anything about the extensionless duplicates (`/faq` as well as `/faq.html`)

Decision **B2** deferred this. **Today's export confirms the decision was
right:** across all nine CSVs and 774 URLs, **not one extensionless variant
appears.** The surface remains latent, exactly as B2 predicted. Leave it.

### ❌ Add a guard so a stub `noindex` cannot be forgotten again

Reasonable idea; **already built.** `seo/tools/verify_seo.py` assertion 7, "no
unintended noindex", allowlists only `404.html` and `confirmation.html` and
fails on anything else — and it runs in CI (`.github/workflows/verify.yml:124`).
It was written on 8 August, which is why it did not catch the July stubs. The
hole is closed; nothing more is needed.

### ❌ Touch `<priority>` in the sitemaps

Your revision-notes pages carry `priority 0.8` and are 33.5% indexed;
practice-questions carry `0.7` and are 89.6% indexed. Google ignores the field.
Changing it would achieve nothing.

### ❌ Re-run the generators, rebuild the header, or re-bake the templates

`python3 scripts/verify_generated.py` and `python3 scripts/build_sitemap.py --check`
both pass. The committed tree matches what the eight generators produce. There
is no drift to correct, and re-running them for no reason would churn 446 pages'
`lastmod` dates for nothing.

---

## Summary

| # | Action | Impact | Effort | Breaking? | Recommend |
| --- | --- | --- | --- | --- | --- |
| 1 | `seo/tools/gsc_reconcile.py` | medium | low | no | ✅ **Done 21 Aug** |
| 2 | Two entries in `docs/REVIEW-NOTES.md` | low | trivial | no | ✅ **Done 21 Aug** |
| 3 | Stop submitting the PDFs | low today | low | no | **Not now — re-decide 1 Oct** |

Everything else that matters is in `13-…`, and none of it is code.

---

## Revision log

**21 August 2026, later the same day.** Action 3 moved twice and landed back
where it started. First to "conditional on one check", after Crawl stats put
PDFs at 15% of crawl requests and the Performance export showed PDF impressions
down 61%. Then, once the PDF time series arrived, back to **"not now, re-decide
1 October"** — because the crawl cost turned out to be a single burst on
8–9 August that is already spent and is not recurring, so removal today would
recover nothing.

Actions 1 and 2 are unchanged. Nothing in "Not worth doing" changed — every item
there was tested against repo evidence that has not moved.

**21 August 2026, evening.** Actions 1 and 2 implemented on your instruction;
Action 3 deliberately not done, per the recommendation in `11-…` §7 to leave
`sitemaps/pdfs.xml` alone until 1 October. Two things worth recording from the
implementation:

- The tool's duplicate-category assertion was **added after the first version
  failed to catch a deliberately corrupted export**. Worth knowing that the
  check exists because it was needed, not because it seemed tidy.
- Writing up G1 turned up `/about.html` as a second thin core page with the same
  stale verdict. That came out of checking a number I had asserted without
  measuring.
