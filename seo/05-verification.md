# Phase 5 — Verification

Every claim here is produced by a rule that runs over **all 463 pages**, not a
sample. Re-run any of them:

```
python3 seo/tools/verify_seo.py      # the ten assertions below
python3 seo/tools/audit.py           # the Phase 2 defect sweep, re-run
python3 seo/tools/fix_links.py       # dry run; must report 0 files
python3 scripts/verify_html.py
python3 scripts/verify_links.py revision-notes practice-questions past-paper-questions flashcards past-papers
python3 scripts/verify_glossary.py
python3 scripts/verify_liquid.py
python3 scripts/build_sitemap.py --check
```

**Nothing is deployed.** 25 commits on `seo/indexing-fixes`; `main` is untouched.

---

## The ten assertions

```
[PASS]  1  no internal link points at a non-canonical URL      20,501 internal references
[PASS]  2  no internal link is case-mismatched or dead
[PASS]  3  every page has a self-referencing canonical         461 pages
[PASS]  4  og:url matches canonical; social titles match <title>
[PASS]  5  exactly one <h1>, a title and a description on every page
[PASS]  6  titles and meta descriptions are unique             461 titles, 461 descriptions
[PASS]  7  no unintended noindex                               intentional: 404.html, confirmation.html
[PASS]  8  every JSON-LD block parses and every page has one   904 blocks
[PASS]  9  sitemap valid, complete, canonical-only, no duplicates   744 URLs across 7 sitemaps
[PASS] 10  robots.txt blocks nothing and names the sitemap

10/10 assertions passed
```

Assertion 9 checks both directions — every indexable page and published PDF is
in a sitemap, and every sitemap URL has a file behind it. It also rejects
duplicates across sitemaps, non-HTTPS URLs, `index.html` variants and malformed
`lastmod`.

## Before and after

| Measure | Before | After |
| --- | ---: | ---: |
| Internal links to non-canonical URLs | **1,300** | **0** |
| BreadcrumbList JSON-LD URLs pointing at duplicates | **334** | **0** |
| Canonical pages reachable from `/` by static link crawl | **441 / 461** | **461 / 461** |
| Pages whose canonical contradicts the sitemap | **7** | **0** |
| Dead internal links | **3** | **0** |
| Duplicate titles | **1 pair** | **0** |
| `og:title` / `twitter:title` mismatches | **3** | **0** |
| Indexable pages with no JSON-LD | **2** | **0** |
| Sitemap format | flat `<urlset>`, 461 URLs | index → 7 sitemaps, **744 URLs** |
| PDFs in the sitemap | **0 of 283** | **283 of 283** |
| Distinct `lastmod` values | 3 build dates covering 440 of 461 | derived from `git log` |
| Generators that rewrite the sitemap | 3 | **0** |

### The headline fix, measured

A crawl of the built site from `/`, following static HTML links only and
executing no JavaScript:

```
before:  701 URLs reached — 20 canonical hub pages unreachable
after:   700 URLs reached — 0 canonical pages unreachable, all 200
```

The 20 hub pages of `revision-notes/`, `practice-questions/` and `past-papers/`
had **zero internal links at their canonical URL**; a crawler only ever found
the `…/index.html` twin. They now have inbound links at the URL they
canonicalise to, the one in the sitemap, the one Google should rank.

## Content integrity

The link rewrite touched 184 hand-written pages and 168 JSON-LD blocks. CLAUDE.md
records that scripted prose rebuilds have silently destroyed `<a>` tags in this
repo before, so the result was proved rather than trusted:

| Check | Result |
| --- | --- |
| `verify_text_integrity.py` (HEAD → working tree) | 179 files compared, **0 differ** |
| `verify_markup_integrity.py` | **0 element-count drops.** All 181 reported reference losses are the old `index.html` URL strings themselves |
| Visible-text SHA-256 per page | unchanged on **465 / 465** |
| Anchor count, `<title>`, word count per page | unchanged on **465 / 465** |
| `verify_html.py` | **0 errors** across every changed file |
| `verify_links.py` | 5,103 internal refs, **0 broken hrefs, 0 broken fragments** |
| `verify_glossary.py` | **all 7 checks pass** — no definition moved |
| `verify_liquid.py` | 98 markdown files, **0 problems** (a stray `{%` fails the whole deploy) |

**No economics wording was changed anywhere.** The only prose that moved is the
`<title>` of `past-paper-questions/index.html`, which was a duplicate of the
Edexcel board page's title and named one board on a page covering both.

## Generator idempotence

All five generators re-run clean, which is what makes the source fixes durable:

| Generator | Output after re-run |
| --- | --- |
| `build_questions.py` | byte-identical (173 pages) |
| `build_past_paper_questions.py` | byte-identical (90 pages) |
| `build_glossary.py` | byte-identical (3 pages) |
| `build_flashcards.py` | byte-identical (7 pages) |
| `build_past_paper_taxonomy.py` | byte-identical |
| `build_sitemap.py --check` | reports no change |

None of them touches `sitemap.xml` any more. Verified by snapshotting the file,
running all four page generators, and diffing.

## What is deliberately still true

These are not failures. Each was decided, and the reasoning is in
`seo/04-decisions.md`.

| Finding | Count | Why it stands |
| --- | ---: | --- |
| `duplicate-url-variant` | 463 | GitHub Pages serves every page at two URLs. The `/index.html` half now has **zero inbound links** and will fade. The extensionless half (`/faq` beside `/faq.html`) is latent — no internal links, correct canonicals — and is deferred to Phase 6 with the root `.html` question (**B2**) |
| `link-parameterised` | 239 | `?topic=` deep links. Every target self-canonicalises to the clean URL, so Google consolidates correctly; converting to fragments would lose GA4 visibility and touch an untested component (**B3**) |
| `title-long` | 286 | Over 60 characters. Not a ranking factor — Google truncates the display only (**B4**) |
| `description-length` | 126 | Outside 70–160 characters. Advisory |
| `thin-content` | 20 | 18 are navigation hubs doing their job; 2 are short notes pages left by decision (**B5**) |
| `near-duplicate` | 5 | Deliberate AQA↔Edexcel twins targeting different board queries |

## One thing this branch fixed that was not in the diagnosis

`_config.yml` had no `exclude` entry for `seo/`, so this audit would have
published itself — the reports, the crawl CSVs, and the Search Console exports
listing every URL Google has judged. Added in commit `d085317`. `verify_liquid.py`
confirms the new markdown contains no `{%`, so the deploy was never at risk.

## Not done

- No meta-refresh stubs anywhere.
- No root `.html` renames — deferred to Phase 6 as agreed.
- No stubs for `/revision-notes/aqa-as-micro/*`. Correctly deleted, stays 404.
- No `_redirects`, `netlify.toml`, `vercel.json`, `.htaccess` or `_headers` —
  all inert on GitHub Pages.
- No `.nojekyll` — it would immediately publish `_working/`.

## Next

`seo/06-gsc-checklist.md`: what to do in Search Console, in what order, and what
to expect. **Step 0 is the deploy, and it is yours to make.**
