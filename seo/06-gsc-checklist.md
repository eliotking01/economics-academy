# What to do in Search Console, in what order

Nothing here is deployed yet. **Step 0 is yours.**

---

## Step 0 — Deploy (you, before anything else)

The work is on branch `seo/indexing-fixes`. Nothing has been pushed and `main`
is untouched, so the live site is still running the old code.

```
git checkout main
git merge seo/indexing-fixes
git push          # main auto-publishes to economicsacademy.co.uk
```

Then wait for the GitHub Pages build (usually 1–2 minutes) and confirm three
URLs by eye before touching Search Console:

| URL | Expect |
| --- | --- |
| `https://economicsacademy.co.uk/practice-questions/` | canonical points at itself, not `…/index.html` |
| `https://economicsacademy.co.uk/sitemap.xml` | a `<sitemapindex>` listing 7 sitemaps |
| `https://economicsacademy.co.uk/sitemaps/pdfs.xml` | 283 PDF URLs |

If the sitemap index 404s, the `sitemaps/` directory did not publish — check it
is not caught by `_config.yml`'s `exclude` list.

---

## Step 1 — Submit the new sitemaps (day 0, ~5 minutes)

**Indexing → Sitemaps.**

1. **Submit `sitemap.xml`, and nothing else.** It is now an index. Google reads
   it, discovers all seven children, and lists each child as its own row in the
   Sitemaps report with its own discovered and indexed counts. **That is where
   the per-section visibility comes from — the index structure, not from
   submitting each child by hand.** Submitting them individually is optional and
   changes nothing about the reporting.

2. Leave the previously submitted `sitemap.xml` entry in place — it is the same
   URL, now serving an index. Nothing to remove.

### If you do submit a child and get "Invalid sitemap address"

The box already contains your property prefix as greyed-out text, so you type
only the remainder, **with no leading slash**:

```
sitemaps/core.xml          correct
/sitemaps/core.xml         becomes https://economicsacademy.co.uk//sitemaps/core.xml
```

That doubled slash is the usual cause of that message.

If the box shows *no* greyed-out prefix, the property is a **Domain** property
(verified by DNS) rather than a URL-prefix one, and there is nothing to append
to — paste the full URL instead:

```
https://economicsacademy.co.uk/sitemaps/core.xml
```

Confirmed live and serving `application/xml`: `/sitemap.xml` returns a
`<sitemapindex>`, and each of the seven children returns a `<urlset>`. A
rejection at this point is an input-format problem, not a hosting one.

**Expect:** status "Success" within a few hours to a few days, with a discovered
URL count. The count Google reports may lag the real 744 for a week or more;
that is normal and not a fault.

## Step 2 — Request indexing for the highest-value pages (day 0, ~10 minutes)

**URL Inspection**, one at a time. You get roughly 10–12 manual submissions a
day, so spend them on the pages where the duplicate split was costing most:

```
https://economicsacademy.co.uk/revision-notes/
https://economicsacademy.co.uk/past-papers/edexcel-b/
https://economicsacademy.co.uk/past-papers/ocr/
https://economicsacademy.co.uk/past-papers/aqa/
https://economicsacademy.co.uk/past-papers/edexcel/
https://economicsacademy.co.uk/practice-questions/
https://economicsacademy.co.uk/revision-notes/edexcel-theme-1/
https://economicsacademy.co.uk/past-papers/
```

For each: **Test Live URL** first, confirm it reports "URL is available to
Google" and that the **user-declared canonical matches the URL you typed**, then
**Request Indexing**.

Do *not* request indexing for the `…/index.html` variants. You want those to
fade, not to be refreshed.

## Step 3 — Do nothing for two weeks

(Step 4's two validations are the exception - start them now, they run in the
background and need nothing further from you.)

This is the hardest step and the most important. Re-submitting, re-requesting or
changing things again during consolidation makes the signal noisier, not
stronger.

**What you will see, and should not panic about:**

- **"Alternate page with proper canonical tag" goes UP before it goes down.**
  Google has to re-crawl each `…/index.html` URL to learn it is now unlinked.
  Every one it re-crawls lands in this bucket. That is the fix working.
- **Impressions may dip for 1–3 weeks** on the ten split pairs while Google
  merges each pair into one URL. Combined clicks should recover and then exceed
  the previous total, because the signals stop being divided.
- **Total indexed pages may briefly fall** as duplicates are dropped before the
  461 canonical pages are all discovered.

## Step 4 — Validate, but only the two issues that will pass

A **failed** validation is worse than never starting one: it resets, and you run
the whole ~2-week cycle again. So only validate what has actually been fixed at
the URL Google will re-crawl.

**Indexing → Pages**, click the issue, then **Validate Fix**:

| Issue | Rows | When | Why |
| --- | ---: | --- | --- |
| **Excluded by 'noindex' tag** | 26 | **Now** | All 26 checked live: HTTP 200, no robots meta. Fixed by commit `203f6bd` on 2026-07-30, so this does not depend on the recent deploy at all. Will pass. |
| **Redirect error** | 1 | **Now** | `/past-paper-questions` returns a clean HTTP/2 301 to `/past-paper-questions/` — no chain, no protocol downgrade. Will pass. |
| **Not found (404)** | 10 | **Never** | See below. |
| **Alternate page with proper canonical tag** | 9 | **~day 45** | It will climb before it falls (Step 3). Validating now would fail. |

### Do not validate "Not found (404)"

Checked live: **all 10 still return 404, and correctly so.** Nine are
`/revision-notes/aqa-as-micro/*` and `aqa-a-micro/*` — a deleted section — and
the tenth is an Edexcel B mark scheme that does not exist.

Removing the link to that PDF was still the right fix, because it stops Google
rediscovering the URL. But **GSC validates the URL, not the links pointing at
it**, so the response code is unchanged and validation would fail.

Leave this issue alone. Google drops persistent 404s from the report by itself
over a few months. Do not create stub pages for correctly-deleted URLs.

### Nothing to validate

The 76 PDF rows (`crawled-currently-not-indexed`, `duplicate-without-user-selected-canonical`)
and the 7 HTML pages under "Crawled – currently not indexed" have no technical
defect to re-check. See group C of `seo/03-diagnosis.md`.

## Step 5 — First real read (day 30)

**Indexing → Pages**, and now the per-sitemap view is what you came for.

Check each sitemap's coverage separately:

- `revision-notes` (179) — was mostly indexed already; expect it to hold.
- `practice-questions` (173) — **the one to watch.** Google had never crawled a
  single page here. This is the clearest measure of whether the crawl wave
  worked.
- `past-paper-questions` (90) and `flashcards` (7) — same story, smaller.
- `pdfs` (283) — expect a **low** indexed rate and do not chase it. Exam-board
  PDFs are identical across dozens of sites; Google indexing few of them is a
  duplication judgement, not a defect, and there is no fix available on GitHub
  Pages.

**Performance → Search results**, compare the 28 days after deploy against the
28 before, filtered to `/revision-notes/` and `/past-papers/`. You are looking
for the ten duplicate pairs collapsing into single rows with combined clicks.

## Step 6 — Close the loop (day 45)

1. Validate **"Alternate page with proper canonical tag"** now. By this point the
   `…/index.html` URLs should be dropping out rather than accumulating.
2. Re-export the "why pages aren't indexed" CSVs into `seo/gsc-exports/` and
   re-run the audit to see what actually changed:

   ```
   python3 seo/tools/inventory.py
   python3 seo/tools/audit.py
   python3 seo/tools/verify_seo.py
   ```

3. Also export the **indexed** pages this time. It was the one thing missing
   from this audit — without it the discovery gap could only be bounded (≥340
   pages) rather than stated exactly.

---

## Realistic expectations

| Timeframe | What should have happened |
| --- | --- |
| Days 1–3 | Sitemaps read; the 8 manually-submitted URLs re-crawled |
| Week 1–2 | Crawl volume rises sharply as Google works through 744 URLs, most for the first time. GSC looks *worse*: more "Alternate page" rows, indexed count wobbles |
| Week 3–4 | Duplicate pairs start merging. `practice-questions` and `past-paper-questions` begin appearing in the index at all |
| Week 6–8 | The ten split pairs should be single URLs. Combined clicks at or above the previous total |
| Beyond | The 7 "Crawled – currently not indexed" HTML pages and most of the 283 PDFs are a site-authority and duplication question, not a technical one. No further code change will move them |

**What this work cannot do:** make Google index exam-board PDFs it considers
duplicates of other sites' copies, or overcome a low-authority domain on
competitive revision-notes queries. Those are the honest limits, and they were
already stated in group C of `seo/03-diagnosis.md`.

## If something looks wrong

- **A page you expect is "Discovered – currently not indexed"** — normal for a
  new page in a large batch. It means Google knows about it and has queued it.
  Give it 4–6 weeks before treating it as a problem.
- **The sitemap reports fewer URLs than 744** — check `sitemaps/` published, and
  that GitHub Pages did not 404 one of the seven children.
- **A canonical looks wrong in URL Inspection** — run
  `python3 seo/tools/verify_seo.py`; assertion 3 covers every page and would
  have failed.
