# URL structure and redirect options

21 August 2026. Why the revision-notes URLs are frozen, what a better structure
would look like, and what it would actually take to move to it.

**Recommendation: do not rename anything now.** The gain is small, the risk is
permanent, and the pages are only just being indexed. Read section 4 before
deciding otherwise.

---

## 1. Where the URLs stand

A published URL on this site is permanent. GitHub Pages serves static files and
has **no redirect mechanism of any kind** — there is no `.htaccess`, no
`_redirects`, no server config. Move or delete a file that Google has indexed
and that URL 404s forever. That is why hard rule 7 exists.

Current shape:

```
/revision-notes/edexcel-theme-1/1-2-1-rational-decision-making.html
/revision-notes/aqa-a2-macro/2-3-3-inflation-and-deflation.html
```

What is weak about it, honestly:

- The `.html` extension is dated but carries **no ranking penalty**. It is
  cosmetic.
- `edexcel-theme-1` doesn't say "a-level economics". A user reading the URL in
  a SERP gets less confirmation than `savemyexams.com/a-level/economics/edexcel/…`
  gives.
- The code prefix `1-2-1-` pushes the meaningful words two segments right.
  Words earlier in a URL carry slightly more weight — but "slightly" is doing
  real work in that sentence.

What is right about it: the topic name is in the slug, the board is in the
path, it's lowercase, hyphenated, shallow, and stable. That covers most of what
a URL can do for you.

**Exact-match keywords in URLs are a weak ranking factor.** Google has said so
repeatedly, and the SERP evidence backs it: Save My Exams ranks first for
"government failure economics a level" with the topic name buried seven
segments deep in the URL. Titles, content and links decide these SERPs.

---

## 2. What a better structure would look like

If the site were being built today:

```
/revision-notes/edexcel-a-level-economics/theme-1/rational-decision-making/
/revision-notes/aqa-a-level-economics/macro/inflation-and-deflation/
```

Board and qualification in one readable segment, module next, topic name as the
leaf, no extension, trailing slash. That is roughly what Seneca and TutorChase
do, and close to Save My Exams minus their spec-year segments.

A lower-risk halfway house, if you ever migrate:

```
/revision-notes/edexcel-theme-1/rational-decision-making/
```

Same directories, code dropped from the leaf. Smaller diff, most of the
benefit.

The Claude Code audit produces the full page-by-page rename list as
`seo/19-notes-url-rename-proposal-<date>.md`. Treat it as a costed option, not
a plan.

---

## 3. The three ways to get redirects

### Option A — meta-refresh stubs on GitHub Pages (free, no move)

Leave a small HTML file at every old URL:

```html
<link rel="canonical" href="https://economicsacademy.co.uk/new/path/" />
<meta http-equiv="refresh" content="0; url=/new/path/" />
```

Google treats an instant meta refresh as a redirect and passes most signals,
but it processes them more slowly than a real 301 and treats them as a weaker
signal. The `jekyll-redirect-from` plugin is on GitHub Pages' allowed list and
generates exactly these from a `redirect_from:` line in each page's front
matter, so you would not hand-write 166 stubs.

Cost: 166 zombie files in the repo forever, and every one of them is a page
Google may keep crawling and reporting in Search Console.

### Option B — Cloudflare in front of GitHub Pages (free, small change)

Move the domain's DNS to Cloudflare, keep GitHub Pages as the origin, and add
redirects in Cloudflare's dashboard. These are **real 301s**, issued before the
request reaches GitHub.

Cloudflare's documented Free-plan limits: 15 Bulk Redirect rules, 5 Bulk
Redirect lists, and **10,000 URL redirects across those lists** — comfortably
more than 166. Caveat worth checking before you commit: several Cloudflare
community threads in 2025–26 report the free tier capping bulk redirect lists
at 20 items in practice, which contradicts the docs. Test with a handful before
building the full list.

Nothing about how you work changes: same repo, same `git push`, same GitHub
Pages build. You gain a caching layer and analytics as a side effect.

**This is the option I'd pick if you ever want real 301s.**

### Option C — move hosting to Cloudflare Pages or Netlify (free, bigger change)

Both deploy from the same GitHub repo on push, and both support a plain-text
`_redirects` file:

```
/revision-notes/edexcel-theme-1/1-2-1-rational-decision-making.html  /revision-notes/edexcel-theme-1/rational-decision-making/  301
```

Real 301s, no proxy layer, and you get build previews on branches.

The catch: this site relies on GitHub Pages' **default Jekyll build**, and what
is public is decided by `_config.yml`'s `exclude:` list. A move means
reproducing that build on the new host and re-proving the published surface
matches — `scripts/verify_published_surface.py` becomes the acceptance test.
That is a real project, not an afternoon.

---

## 4. When renaming would be worth it

Only if all four are true:

1. You have real 301s in place first (option B or C), tested on a few URLs.
2. Search Console shows the current URLs are fully indexed, so you can measure
   the recovery rather than guess at it.
3. You are not mid-way through another indexing recovery — as of 21 August
   2026 you are, with validations still running from the GSC audit.
4. You have a fortnight where a temporary ranking dip doesn't matter. Term
   starts in early September; a dip then costs the whole autumn's traffic.

Expected upside if you do it all correctly: small. A cleaner URL improves
click-through slightly and reads better when shared. It will not move you from
page two to page one — the title formula in `seo/14-notes-keyword-brief.md`
has a far better chance of that.

**So: leave the URLs alone. Revisit in the spring, after a full term of data on
the new titles.**

---

## 5. What to do about new pages

The tempting move is to start new topic pages at the better structure, since
that one is free. Don't. You would end up with 166 pages at `/x.html` and a
handful at `/x/`, two conventions in one folder, and a generator that has to
know which page is which. On a site this size the consistency is worth more
than the marginal URL quality.

New topic pages follow the existing convention. If you later migrate, they
migrate with everything else in one pass.
