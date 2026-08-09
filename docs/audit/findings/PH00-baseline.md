# Phase 0 findings — baseline

IDs are stable. Never renumber. Status values: OPEN / ACCEPTED / REJECTED /
DEFERRED / RESOLVED.

Severity is judged against the owner's stated goal — make scaling cheap and
consistent — not against a generic SEO checklist.

---

## PH00-001 — The site's two best-earning pages have one raw inbound link each

**Severity:** High · **Category:** Internal linking / crawl · **CERTAIN**

**Evidence.** `python3 docs/audit/scripts/link_graph.py`:

```
   raw  injected   total    inj%  url
     1       463     464   99.8%  /past-papers/edexcel-b/
     1       463     464   99.8%  /past-papers/ocr/
     1       463     464   99.8%  /privacy.html
     2       463     465   99.6%  /revision-notes/macro-application/
     2       463     465   99.6%  /faq.html
     3       926     929   99.7%  /contact.html
     4       926     930   99.6%  /about.html
     6       463     469   98.7%  /revision-notes/glossary/
     6       463     469   98.7%  /past-papers/
     7       463     470   98.5%  /flashcards/
```

The single raw link to each of the two `/past-papers/` board hubs comes from
`/past-papers/index.html`. Everything else is the runtime-injected header.

From `seo/performance-pages.csv` (GSC, exported 2026-08-08), these two are the
highest-earning non-homepage URLs on the site:

```
/past-papers/edexcel-b/   78 clicks   7,214 impressions   pos 10.29
/past-papers/ocr/         65 clicks   4,757 impressions   pos 11.21
```

**Why it matters.** SEO. This is not a discovery problem — 461 of 463 pages are
reachable in a raw crawl, and Google renders JavaScript. It is an equity-
distribution problem: on the non-rendered pass that determines much of how
PageRank flows, these URLs receive one link each while `/tutoring.html` receives
449. Two pages carrying 12k impressions are being fed like leaf nodes.

**Complication, stated honestly.** `seo/07b-link-decisions.md` §4 already reached
this conclusion and **declined to act**, on the grounds that no notes exist for
OCR or Edexcel B so there is no topically honest in-content anchor. That
reasoning is sound and I am not overturning it. The gap it leaves is that the
alternative — raising raw inbound links from pages that *are* topically
adjacent, i.e. the other three board hubs and `/past-papers/` itself — was
described as "edging toward a link dump" and then not evaluated.

**Recommendation.** Evaluate in P3, not now. The specific question to answer is
whether a "papers for other boards" row on each of the four `/past-papers/<board>/`
hubs is defensible — it would take each of OCR and Edexcel B from 1 raw inbound
to 4, is genuinely useful to a student who picked the wrong board, and adds 3
links to 4 pages rather than 463. Do **not** touch the injected header.

**Effort:** S · **Risk of acting:** Low — 4 hand-edited hub pages, no URL change ·
**Risk of not acting:** Medium — a standing cap on two proven earners ·
**Dependencies:** P3 · **Status:** OPEN

---

## PH00-002 — Four incompatible URL grammars across five page families

**Severity:** High · **Category:** URL architecture / scaling · **CERTAIN**

**Evidence.**

```
/revision-notes/edexcel-theme-1/1-1-1-economics-as-a-social-science.html
/practice-questions/edexcel-theme-1/1-1-1-economics-as-a-social-science.html
/past-paper-questions/edexcel/1-2-2-demand/
/flashcards/edexcel-a/theme-1/
/revision-notes/glossary/edexcel-a/
```

Two families use `flat .html` with a spec-code-prefixed slug; three use
directories, each with a different path grammar (board/topic, board/theme,
glossary/board). Nothing in the repo documents which shape a sixth family should
adopt.

**Why it matters.** Scaling. Every new resource type re-litigates the decision,
and every cross-family join needs bespoke URL construction. `taxonomy.json`
already carries three separate URL fields per topic (`notesUrl`, `questionsUrl`,
`pastpaper_url`) because none can be derived from another.

**Recommendation.** Do **not** change existing URLs. Write the rule down instead:
new families use `directory/` form (it is the newer and better choice, and three
of five families already do). Record the two `.html` families as a documented
historical exception in a conventions doc. Decide and record this in P1 so P6 has
a fixed target.

**Effort:** S to document, L and HIGH RISK to unify · **Risk of acting:** High if
unified — GitHub Pages issues no 301, and meta-refresh stubs would have to live in
the repo forever. Rejected on exactly this basis for the glossary on 2026-08-07 ·
**Risk of not acting:** Medium, and compounding per new family ·
**Dependencies:** none · **Status:** OPEN

---

## PH00-003 — "Edexcel A" is encoded three ways, and directory names disagree with the data inside them

**Severity:** High · **Category:** Data model / naming · **CERTAIN**

**Evidence.**

| Encoding | Where |
| --- | --- |
| `edexcel` | `/past-papers/edexcel/`, `/past-paper-questions/edexcel/`, `questions-data` `board` field, `taxonomy.json` `board`+`slug` |
| `edexcel-a` | `/flashcards/edexcel-a/`, `/revision-notes/glossary/edexcel-a/`, `flashcards-data/edexcel-a/`, `glossary-data/terms.json` `boards` |
| `edexcel-theme-N` | `/revision-notes/edexcel-theme-1/`, `/practice-questions/edexcel-theme-1/`, `questions-data/edexcel-theme-1/`, `boardDir` field |

And the directory does not always match the field inside it:

```
past-paper-questions-data/edexcel-a/p1-june-2017.json  →  "board": "edexcel"
past-paper-questions-data/edexcel-a-as/*.json          →  "board": "edexcel"
flashcards-data/edexcel-a/theme-1.json                 →  "board": "edexcel-a"
```

`glossary-data/terms.json` uses `boards: ["aqa", "edexcel-a"]` on 234 of 325
terms — so a term shared with the notes cannot be joined to
`questions-data`'s `"board": "edexcel"` without a lookup that does not exist.

**Why it matters.** Scaling, directly. Adding Edexcel B or OCR notes means
choosing among three conventions and then writing the fourth translation. Any
future cross-resource feature — "show me everything on Demand" — needs a board
identity that currently has to be inferred per family.

**Recommendation.** P9. Introduce one canonical board identifier as data (a
`boards.json` with `id`, `slug-in-urls`, `display-name` per family), and have the
generators read it rather than hardcoding. **This changes no URLs** — the existing
slugs become recorded values in the mapping, not things to fix.

**Effort:** M · **Risk of acting:** Low if URLs are untouched; High if anyone
"tidies" a slug · **Risk of not acting:** High — this is the single biggest tax on
adding a board · **Dependencies:** P9, feeds P6 · **Status:** OPEN

---

## PH00-004 — 463 hand-maintained `<head>` blocks with no template

**Severity:** High · **Category:** HTML architecture / maintenance · **CERTAIN**

> **CORRECTED IN P9b, 2026-08-09: the number is 190, not 463.** 273 of the 463
> pages (59%) are generated and already have a template layer — changing every
> `<head>` under `practice-questions/` is one edit to `build_questions.py` and a
> rebuild. Only **190** pages are hand-maintained, 176 of them revision notes and
> hubs. The finding stands but is materially smaller than stated here; P6 should
> be scoped to the 190. See PH09b-generation-drift.md.

**Evidence.** Header and footer are injected at runtime, but `<head>` is not:
every page duplicates the gtag block, `<html lang="en-GB">`, title, description,
canonical, OG and Twitter cards, JSON-LD, the favicon/manifest set, two
stylesheet links and a seven-script tail. 463 copies.

It is currently **correct** — 0 duplicate titles, 0 duplicate descriptions, 0
canonical mismatches, `lang="en-GB"` on 463/463, one GA4 ID (`G-YVCNRW4QH6`) on
463/463. That correctness was achieved by scripted rewrites across all 463 files
(`befb061`, `79faf81`, `4db232c`).

**Why it matters.** Maintenance. Each sitewide `<head>` change is another
463-file scripted edit, in a repo whose own hard rule is that scripted paragraph
rebuilds have "silently destroyed `<a>` tags here before". The `@import` hoist in
`4db232c` was exactly this: a correct change that had to touch every page.

**Recommendation.** P6, its own session. The question is not "add a build step" —
it is what the minimum viable generation layer is, given that ~180 of the 463
pages are already generated from JSON and the remaining ~283 are not, and given
that Jekyll is already in the loop and could do includes if pages had front
matter. Front matter on a `.html` file changes no URL. That is the option worth
costing.

**Effort:** L · **Risk of acting:** Medium-High — touches every page ·
**Risk of not acting:** Medium, compounding · **Dependencies:** P1, P5, P9, P9b
must precede · **Status:** OPEN

---

## PH00-005 — Two unreferenced directories are published, one with a misspelled name

**Severity:** Medium · **Category:** Repo hygiene / published surface · **CERTAIN**

**Evidence.**

```
$ grep -rl 'specificiations' --include='*.html' . | grep -v '^./_working'
(no output)
$ grep -rl 'old-logos-archive' --include='*.html' --include='*.css' --include='*.js' .
(no output)
```

- `specificiations/` (sic) — 2 exam-board specification PDFs, referenced by zero
  HTML/CSS/JS, absent from `_config.yml`'s `exclude`, therefore **live and
  crawlable** at a misspelled URL. CLAUDE.md records that removing them "is a
  separate call, and was left as one".
- `old-logos-archive/` — 2.0 MB of superseded logos, referenced by nothing, live.

**Why it matters.** Published surface and crawl budget, minor. The misspelling
matters more than the files: `/specificiations/` is a live URL, so renaming it is
a URL change under a no-redirects host.

**Recommendation.** Log only, decide in P1. Three options for
`specificiations/`: leave it (zero risk, permanent typo); add it to `exclude`
(removes 2 URLs Google may have indexed — check GSC first); or create
`specifications/` alongside and leave the old one (duplicate content unless
canonicalised). Note `old-logos-archive/` is a straightforward `exclude`
candidate — nothing links to it.

**Effort:** S · **Risk of acting:** Low-Medium (URL removal) ·
**Risk of not acting:** Low · **Dependencies:** P1 · **Status:** OPEN

---

## PH00-006 — Template fetch failure has no fallback

**Severity:** Medium · **Category:** Resilience / UX · **CERTAIN**

**Evidence.** [`js/components/inject-templates.js:127-129`](../../js/components/inject-templates.js#L127-L129)
and `137-139`: both `.catch()` handlers do nothing but `console.error`. No
`<noscript>` navigation exists anywhere (the 15 pages containing `<noscript>` use
it for feature-specific messaging — flashcards, glossary, question search).

**Why it matters.** UX and single-point-of-failure. If `/templates/header.html`
404s or hangs, all 463 pages lose navigation and the footer simultaneously, with
no visible error. CLS is handled ([`css/main.css:210`](../../css/main.css#L210)),
so the failure mode is a silent 240 px blank band, not a jump.

**Recommendation.** P7/P8. Minimum: a `<noscript>` block in the placeholder div
carrying the six top-level nav links, and a `.catch()` that renders the same
minimal list. Both are additive and change no URL.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low probability,
high blast radius · **Dependencies:** none · **Status:** OPEN

---

## PH00-007 — Publisher identity markup is absent from 109 of 463 pages, including the entire past-paper-questions section

**Severity:** Low · **Category:** Structured data · **CERTAIN**

**Evidence.** `python3 docs/audit/scripts/metadata_census.py` —
`EducationalOrganization` appears on 354 of 463 pages. The 109 without it are:
all 90 `/past-paper-questions/` pages, all section hub `index.html` pages across
every family, `/flashcards/`, `/revision-notes/glossary/`, and 6 of the 9 root
pages.

**Why it matters.** SEO, modestly. Publisher identity is the entity signal that
ties a page to the site; emitting it on notes and MCQs but not on the newest
90-page section is an inconsistency between generators rather than a decision.

**Recommendation.** P4. Confirm whether the omission was deliberate, then make it
uniform at the generator. One template change per generator.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low ·
**Dependencies:** P4 · **Status:** OPEN

---

## PH00-008 — 52 pages carry inline `style` attributes and 9 carry `<style>` blocks, against the house rule

**Severity:** Low · **Category:** Front-end consistency · **CERTAIN**

**Evidence.** `grep -lE '<[a-z][^>]*\sstyle="'` over the 465 published files:
52 hits, concentrated in `revision-notes/aqa-a2-micro` (14) and
`revision-notes/edexcel-theme-1` (12). `grep -lF '<style'`: 9 files, six of them
the `practice-questions/*/index.html` hubs, which are **generated** — so the
generator emits them.

CLAUDE.md, Conventions → CSS: "No inline `style` attributes — extract a class."

**Why it matters.** Maintenance and consistency, not rendering. The generated
cases matter more than the hand-written ones: they will reappear on every rebuild.

**Recommendation.** P8. Separate the generated cases (fix at the generator) from
the hand-written ones (extract classes into the relevant `css/pages/*.css`).
Note this is markup-only and touches no economics prose.

**Effort:** M · **Risk of acting:** Low · **Risk of not acting:** Low ·
**Dependencies:** P8 · **Status:** OPEN

---

## PH00-009 — 26 Finder duplicate files on disk in `seo/`, reproducing a class of bug already cleaned up once

**Severity:** Low · **Category:** Repo hygiene · **CERTAIN**

**Evidence.** `find . -name '* [0-9].*'` returns 26 files, all under `seo/`:
13 in `seo/tools/` (including `link_graph 2.py`, `link_graph 3.py`) and 13
reports. All are correctly gitignored — `git ls-files | grep -E ' [0-9]+\.'`
returns **0**, so none reached git.

Commit `d1d05ad` deleted 33 of these and added the ignore rules, after one
(`js/components/quiz 2.js`) had been served publicly. The rules worked; the
files came back anyway, because the cause (iCloud/Finder duplication) is
external to git.

**Why it matters.** Low, but real: `seo/tools/link_graph 2.py` and
`link_graph 3.py` are stale copies of a script someone may edit by mistake.

**Recommendation.** Delete them. Audit is read-only, so this is yours to run:

```
find . -path ./.git -prune -o -name '* [0-9].*' -print -delete
```

Consider whether the repo should sit outside an iCloud-synced folder at all —
that is the actual root cause.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low ·
**Dependencies:** none · **Status:** OPEN

---

## PH00-010 — 14 fully-merged branches remain, local and remote

**Severity:** Low · **Category:** Repo hygiene · **CERTAIN**

**Evidence.** `git branch --no-merged main` returns **nothing**. All 14 local
branches and 13 remote branches are fully merged, including
`backup-pre-enrichment`, which by its name was a safety copy for work that has
since landed.

**Why it matters.** Low. Navigational noise, and `backup-pre-enrichment` is the
kind of name that stops anyone deleting it without checking.

**Recommendation.** P1 produces the list; you delete. Verify
`backup-pre-enrichment` really is redundant before removing it — its history is
what would be lost, and it is the only one whose name claims a purpose beyond
the merged feature.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low ·
**Dependencies:** none · **Status:** OPEN

---

## PH00-011 — `verify_liquid.py` fails on a file Jekyll never reads, and 104 of the 106 it checks carry no deploy risk at all

**Severity:** Medium · **Category:** Tooling / governance · **CERTAIN**

**Evidence.** `python3 scripts/verify_liquid.py` **exits 1** on current `main`:

```
seo/05-verification.md:91: unterminated '{%' - wrap it in {% raw %} ... {% endraw %}
106 markdown files checked, 1 problem(s)
```

The flagged line is:

```
| `verify_liquid.py` | 98 markdown files, **0 problems** (a stray `{%` fails the whole deploy) |
```

— a report line describing this checker's own success. `seo/05-verification.md`
is untouched by this audit (`git diff` empty; last written in `a8c926c`), so the
failure is pre-existing on `main`.

**It is a false positive.** `seo/` is in `_config.yml`'s `exclude` list, so Jekyll
never reads the file and it cannot fail a deploy. The timeline explains it:

```
2026-08-04  fba7c7c  verify_liquid.py added
2026-08-08  d085317  seo/ (and docs/, scripts/, raw-notes/, the *-data dirs,
                     the root markdown) added to _config.yml exclude
```

The checker knows about Jekyll's `_`-prefix rule — it skips `_working/`
explicitly — but not about the `exclude:` list, which did not exist when it was
written. Scoping it correctly today:

```
markdown scanned by verify_liquid:                 106
of those, never seen by Jekyll (in _config exclude): 104
actually at deploy risk:                             2
    .codex/notes-workflow.md
    revision-notes/macro-application/macro-application-uk-sa.md
```

**Why it matters.** Governance, and it is the sharpest example in the repo of why
P10 exists. This check guards against the one failure mode that takes down the
**entire site** rather than one page — it was written the day after that
happened. A guard that exits non-zero on a false positive gets ignored, and then
it is not a guard. It is also 53× wider than it needs to be, which is why the
false positive appeared at all.

**Recommendation.** P10. Teach it the `exclude:` list — ideally by parsing
`_config.yml` rather than restating it, so the two cannot drift again. Note
`_config.yml`'s `exclude` is a flat list of strings, so a dependency-free parse
is a few lines. Do **not** simply add `seo/` to a skip list; that recreates the
same drift one commit later.

**Secondary observation.** `.codex/notes-workflow.md` is one of only two markdown
files GitHub Pages actually publishes, meaning `/.codex/notes-workflow.html` is a
live URL. Not what a `.codex/` directory is for. Log for P1 alongside PH00-005.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Medium — a
deploy-killing class of bug guarded by a check people have reason to ignore ·
**Dependencies:** P10 · **Status:** OPEN

---

## Previously flagged, now resolved — logged once, not findings

Confirmed against current files, not taken from the GSC exports:

| Was | Now |
| --- | --- |
| `/REVIEW-NOTES.html`, `/CLAUDE.md`, `/scripts/*.py` publicly served | Excluded in `_config.yml` (`d085317`) |
| 25 pages "Excluded by noindex tag" | 461 of 463 carry no meta robots; the 2 that do are `404.html` and `confirmation.html`, correctly |
| 8 `…/index.html` duplicate canonicals | 0 canonical mismatches, 0 internal `index.html` links |
| `/past-paper-questions` redirect error | Clean 301 to trailing-slash form |
| 3 links to non-existent Edexcel B mark schemes | Removed (`5f2d3aa`); link graph reports 0 broken targets |
| 33 Finder duplicates in git, one served publicly | 0 tracked (`d1d05ad`) |
| Flat `sitemap.xml` | `<sitemapindex>` over 7 children, 744 URLs, 0 diff against filesystem |
| Two render-blocking `@import`s in `css/main.css` | Hoisted into every `<head>` (`4db232c`) |
