# Decisions needed from you

Five items. Everything else is in Group A of `seo/03-diagnosis.md` and needs no
decision. Nothing has been changed on the site — this branch contains reports
and tools only.

Tick a box or tell me in chat.

---

## B1 — Approve the 458-file internal-link rewrite ★ the main one

**What:** rewrite every `href="/x/index.html"` → `href="/x/"` and
`href="/index.html"` → `href="/"`. 1,300 links across 458 files.

**Why:** 20 of your 21 hub pages currently have **zero internal links at their
canonical URL** — a crawler following links only ever reaches the `/index.html`
twin, which returns 200. Google is ranking both halves of ten pages, splitting
**1,000 clicks and 44,809 impressions** (81% of clicks, 64% of impressions).

**This exceeds the 20-file bulk threshold, so it needs your sign-off.**

### Proposed two-track approach

| Track | Files | Links | Method | Why |
| --- | ---: | ---: | --- | --- |
| Generated | 273 | 745 | fix the 4 generators, re-run them | The generators run Prettier over their own output, so re-running reflows the now-shorter tags correctly and keeps the builds byte-idempotent |
| Hand-written | 185 | 555 | `seo/tools/fix_links.py` | No Prettier. The rewrite leaves wrapping exactly as it is |

Plus `templates/header.html` (22 links, one file, fixes every page's nav).

### Safety

`fix_links.py` never parses or re-serialises HTML. It replaces only the bytes
between the quotes of an `href="…"`, and asserts per file that (1) blanking every
href leaves old and new byte-identical, and (2) the `href=` count is unchanged.
A file failing either is skipped and reported, not written.

Dry run over the working tree: **458 files, 1,300 rewrites, 0 failures.**

### Real sample diff — `revision-notes/edexcel-theme-1/1-2-2-demand.html`

```diff
@@ -161,7 +161,7 @@
             <a href="/">Home</a>
             <span class="separator">›</span>
-            <a href="/revision-notes/index.html">Revision Notes</a>
+            <a href="/revision-notes/">Revision Notes</a>
             <span class="separator">›</span>
-            <a href="/revision-notes/edexcel-theme-1/index.html"
+            <a href="/revision-notes/edexcel-theme-1/"
               >Edexcel Theme 1: Introduction to Markets and Market Failure</a
             >
@@ -365,5 +365,5 @@
             <div class="notes-cta">
               <p>Ready to apply these notes?</p>
-              <a href="/past-papers/edexcel/index.html" class="button alt"
+              <a href="/past-papers/edexcel/" class="button alt"
                 >Edexcel Past Papers</a
               >
```

Note the third hunk: the shortened `href` would now fit on one line, but the
wrapping is left untouched. That is deliberate — reflowing it means running
Prettier over 185 hand-written notes files, and CLAUDE.md's hard constraint is
that nothing rewrites notes prose. **Cosmetically imperfect, functionally exact.**

**Known short-term cost:** consolidating each duplicate pair takes Google 2–6
weeks, during which GSC will look noisier before it looks better. This is the
correct trade and the reason to do it before the crawl wave rather than after.

- [ ] **Approve** — do both tracks (recommended)
- [ ] Generated files only (745 links, 273 files) — lower risk, leaves 555
- [ ] Hold

---

## B2 — The extensionless duplicate surface (`/faq` alongside `/faq.html`)

GitHub Pages serves **every** `.html` page at its extensionless URL too, at HTTP
200. That is 340 pages × 2 URLs. Verified live on root and subdirectory pages
alike.

**It is currently latent:** zero internal links use the extensionless form,
every page self-canonicalises to `.html`, and no GSC export mentions one. Only an
external link or a manual guess reaches it.

Your URL policy defers root `.html` changes to a later pass, and this is the same
question. My recommendation is to leave it and revisit in Phase 6 — acting now
would mean either 340 meta-refresh stubs (which GitHub Pages consolidates
unreliably) or a full URL restructure, both of which are exactly what you
deferred.

- [ ] **Leave it, revisit in Phase 6** (recommended)
- [ ] Deal with it now — tell me and I will scope it properly first

---

## B3 — 239 `?topic=` / `?board=` parameter URLs

239 internal links create 239 crawlable URLs behind **7** real pages.

**Not a duplication problem** — every target's canonical names the clean URL and
Google consolidates correctly. It is a crawl-budget cost, arriving just as you
want Googlebot spending its time on 340 never-crawled pages.

Removing them means moving `?topic=` to `#topic=` in
`js/components/flashcards.js:109`, `question-search.js:644` and
`glossary-filter.js:354`. That is a **functional change to working features**,
not an SEO markup fix, and fragments change how deep links behave.

- [ ] **Leave it** (recommended) — the canonical already does its job
- [ ] Convert to fragments — I will scope the JS change separately

---

## B4 — 286 titles longer than 60 characters

Runs at 65% on undiscovered pages vs 29% on known ones — a real regression, from
`build_questions.py` and `build_past_paper_questions.py` concatenating a full
topic name + board + site suffix.

Google truncates the SERP display; it does not penalise. Every title is unique
and descriptive. Shortening 286 titles is a genuine content-shaped change to
generated copy across two generators.

- [ ] **Leave it** (recommended) — cosmetic, and the effort is better spent elsewhere
- [ ] Shorten the two generators' title templates — I will show you the new
      pattern and a sample before regenerating

---

## B5 — Two short notes pages

```
249 words  revision-notes/aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html
287 words  revision-notes/aqa-a2-micro/1-4-1-production-and-productivity.html
```

The only two genuine content pages under 300 words — the other 18 thin pages are
navigation hubs and are fine as they are.

Expanding these is a **content decision** and would mean writing new economics
prose, which your standing rule 1 says I never do without explicit approval.
I am not recommending it as an SEO fix; 250 words is short but not penalised,
and neither page currently earns impressions.

- [ ] **Leave them** (recommended)
- [ ] I will expand them myself
- [ ] Draft additions for my review

---

## Already decided — no action needed from you

| | Decision |
| --- | --- |
| 3 dead Edexcel B mark-scheme links | Remove them |
| 283 PDFs | Add as a separate `sitemaps/pdfs.xml` inside a sitemap index |
| Live crawl | Full, all variants — done |
| Indexed-pages export | Not needed; discovery gap stated as a floor (≥340) |

## Deliberately not doing

- No stubs for `/revision-notes/aqa-as-micro/*` — correctly deleted, stays 404
- No `_redirects`, `netlify.toml`, `vercel.json`, `.htaccess`, `_headers` — inert
  on GitHub Pages
- No `.nojekyll` — it would immediately publish `_working/`
- No meta-refresh redirects anywhere in this pass
- No changes to economics wording
