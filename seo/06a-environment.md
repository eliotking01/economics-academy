# Phase 6a — Environment detection

What this repo actually is, measured rather than assumed, because it determines
how every fix in the architecture pass has to be applied. Read before
`seo/07-link-graph.md`, `seo/08-structured-data.md` and
`seo/09-web-vitals-baseline.md`.

**Baseline re-confirmed before any of this**, on 2026-08-08:

```
python3 seo/tools/verify_seo.py
→ 10/10 assertions passed
  461 pages · 20,501 internal references · 904 JSON-LD blocks
  744 sitemap URLs across 7 sitemaps
```

Nothing in this pass re-solves canonicals, internal-link hygiene, titles,
descriptions or the sitemap. Those are done and enforced.

---

## a. Build step and template system

| Looked for | Found |
| --- | --- |
| `package.json` | absent |
| `Gemfile` / `Gemfile.lock` | absent |
| `netlify.toml`, `vercel.json`, `.htaccess`, `_redirects` | absent |
| Astro / Next / Hugo / Eleventy config | absent |
| `_config.yml` | **present** |
| `.nojekyll` | **absent** |

**Jekyll is active** — GitHub Pages runs its default build because there is no
`.nojekyll`. But it renders nothing: no page carries front matter, so every
`.html` file is copied verbatim. `_config.yml` contains an `exclude:` list and
nothing else; its only job is keeping working files (`scripts/`, `seo/`,
`docs/`, the `*-data/` directories, root markdown) off the public site.

Two consequences that bound this pass:

- **Adding `.nojekyll` would immediately publish every `_`-prefixed directory**,
  including `_working/`. Out of scope, and must not be done as a side effect of
  anything here.
- **`exclude` replaces Jekyll's defaults rather than adding to them.** Nothing in
  this pass edits that list.

There is no server-side capability of any kind: no headers, no redirects, no
301s. Every fix is in-page HTML, or in the script that generates it.

## b. Hand-written or generated — **both, and the split decides the method**

There is no single answer. Per section:

| Section | Pages | Source |
| --- | --- | --- |
| `revision-notes/` topic pages | 166 | **hand-written** |
| `revision-notes/glossary/` | 3 | generated — `scripts/build_glossary.py` |
| `practice-questions/` | 173 | generated — `scripts/build_questions.py` |
| `past-paper-questions/` | 90 | generated — `scripts/build_past_paper_questions.py` |
| `flashcards/` | 7 | generated — `scripts/build_flashcards.py` |
| root pages + `past-papers/` | 14 | **hand-written** |
| | **461** | 295 generated, 166 hand-written |

**295 of 461 pages must be changed at the generator, never in the output.**
`build_glossary.py` and `build_past_paper_questions.py` both run Prettier over
their own HTML and are byte-idempotent by design — a hand edit to a generated
page is destroyed on the next run, silently.

### There is no shared template

Sampled 14 pages across every section. Each duplicates, in full: the gtag block,
`<html lang="en-GB">`, title, meta description, canonical, OG and Twitter cards,
JSON-LD, the favicon/manifest set, `/css/main.css` plus one page stylesheet, and
the seven-script tail. Boilerplate is identical in shape and duplicated per file.

The only shared markup is `<div id="header-placeholder">` and
`<div id="footer-placeholder">`, which `js/components/inject-templates.js`
**fetches at runtime** from `/templates/header.html` and `/templates/footer.html`.

**The 34 header links and 4 footer links are therefore not in the static HTML.**
That matters for the link graph: Google renders JavaScript and will see them, but
they are not statically discoverable, and any depth or orphan claim has to say
which of the two graphs it is talking about. `seo/07-link-graph.md` reports both.

### The precedent for editing hand-written notes pages safely

Two scripts already do this and both are the model to copy:

- `scripts/append_questions_link.py`
- `scripts/append_past_papers_link.py`

Each inserts one fixed block of markup after an existing anchor and does nothing
else. Neither parses, reflows or rewrites prose — scripted paragraph rebuilds
have destroyed `<a>` tags in this repo before. Both are idempotent: a page
already carrying the block is skipped, so a re-run over all 166 pages is safe.
Both are verified afterwards against the pre-run ref with:

```
python3 scripts/verify_text_integrity.py <before-ref>
python3 scripts/verify_markup_integrity.py <before-ref> --strict
```

**Any new bulk edit in this pass follows that pattern exactly**, is committed to
`seo/tools/`, and is dry-run with three sample diffs before it writes anything.

## c. Tooling available

| Tool | Version |
| --- | --- |
| Node | **v22.19.0** |
| npx | 10.9.3 |
| Python | **3.12.4** |
| Google Chrome | present, `/Applications/Google Chrome.app` |
| Lighthouse | **not installed** — runnable via `npx lighthouse` |

**Lighthouse can run.** The fallback for an environment without Node does not
apply, and no measurement is being skipped. It is run against the **live** site
rather than a local server, because the largest performance finding is a
serialised third-party request chain that a localhost run would understate.

## d. Flashcards granularity — **per board per theme/tier**

Seven pages, read rather than inferred:

```
/flashcards/                        hub
/flashcards/edexcel-a/theme-1/      ┐
/flashcards/edexcel-a/theme-2/      │ Edexcel A, one page per theme
/flashcards/edexcel-a/theme-3/      │
/flashcards/edexcel-a/theme-4/      ┘
/flashcards/aqa/micro/              ┐ AQA, one page per tier
/flashcards/aqa/macro/              ┘
```

**Not per topic.** Topic-level entry points already exist and are done with a
query string on the theme page — `/flashcards/aqa/micro/?topic=1-1-1-economic-methodology`
— which `js/components/flashcards.js` reads. That is the correct granularity and
the existing notes → flashcards links already use it, on all 166 topic pages.

No topic-level flashcard URLs exist. **None are to be invented**, and no
topic-level link may be forced at a theme-level page beyond the existing
query-string form.

## e. Practice-question answers — **in the HTML at page load**

Checked in the served markup of
`practice-questions/edexcel-theme-1/1-1-1-economics-as-a-social-science.html`,
not inferred from the script tail. Every question carries, statically:

- `<fieldset class="quiz-options">` with all four options as real `<label>` text;
- `<details class="quiz-model"><summary>Show model answer</summary>` containing
  the full model-answer prose;
- `data-answer="A"` on the `<li>`.

`js/components/quiz.js` is the last script on the page, loads `defer`, and only
*enhances* — scoring, progress bar, localStorage. **Nothing is JS-injected.**

**Google sees all 173 pages in full, answers included.** There is no crawlability
problem on this section. `<details>` content is in the DOM at load and is indexed
normally; it is collapsed for the user, not hidden from the crawler.

### These pages already carry structured data

Each also emits `Quiz` JSON-LD with nested `Question`, `acceptedAnswer` and
`suggestedAnswer`, generated from the same `questions-data/` JSON that produces
the visible HTML — so the two cannot drift. Task B is therefore an **audit and
correction of 904 existing blocks**, not a greenfield addition.

---

## What this changes about the plan

1. **Every fix to `practice-questions/`, `past-paper-questions/`, `flashcards/`
   and the glossary goes in the generator**, then the section is rebuilt. 295 pages.
2. **The 166 hand-written notes pages get a committed, idempotent script** in
   `seo/tools/`, modelled on `append_past_papers_link.py`, dry-run first.
3. **No `.nojekyll`, no URL changes, no `_config.yml` edits.**
4. **The link graph is reported twice**, with and without the 38 runtime-injected
   template edges.
5. **Task B is an audit**, and the practice-question `Quiz` markup is checked
   against what is actually visible — which, per (e), is everything.
