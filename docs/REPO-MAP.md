# What is in this repo

A plain-English tour, written for someone who does not work with code every day.
Counts are from 2026-08-20; re-derive any of them with
`python3 scripts/verify_published_surface.py` rather than trusting the number.

## The one idea that makes everything else make sense

Almost everything here is one of three kinds of thing:

1. **Things visitors see.** Real files served at real web addresses.
2. **The sources those are built from.** You edit these; a script turns them
   into the things visitors see.
3. **Notes and machinery.** Only you and Claude read these. Never on the web.

The big content sections come in **pairs** — a source folder and a published
folder. The rule is always the same: **edit the source, run the script, never
touch the published copy.** Edit the published copy and the next build quietly
wipes your work. That happened on 2026-08-20; see `docs/HISTORY.md`.

A `PreToolUse` hook at `.claude/hooks/block-generated.py` now blocks that
mistake mechanically, because the written rule alone did not.

---

## Root files

### The nine web pages

`index.html` (home), `tutoring.html`, `marking.html`, `about.html`,
`contact.html`, `faq.html`, `privacy.html`, `confirmation.html` (the thank-you
page after a Stripe payment) and `404.html`.

These are the commercial pages — where people actually buy. Unlike the revision
notes they are **hand-written**, so they can be edited directly. They are the
only HTML in the repo that may be edited by hand, along with the five
`past-papers/` hubs and three `revision-notes/` pages.
`python3 scripts/bake_templates.py` prints the definitive list of all 17.

### Site plumbing

| File | What it does |
| --- | --- |
| `CNAME` | One line: the custom domain. **Delete it and the domain stops working.** |
| `_config.yml` | **The most consequential file here.** A list of what GitHub must *not* publish. Without it the scripts, working notes and the list of known site errors would all be public web pages — they genuinely were, once. |
| `robots.txt` | Tells Google it may crawl everything, and where the sitemap is. |
| `sitemap.xml` | Not the map itself — an index pointing at the seven real maps in `sitemaps/`. Generated. |
| `site.webmanifest` | Lets a phone "add to home screen" with a proper icon and name. |
| `favicon.ico`, `apple-touch-icon.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png` | The browser-tab and home-screen icons. **Root is correct, not mess:** browsers request `/favicon.ico` automatically whether or not a page links to it. The two `android-chrome` files are referenced from `site.webmanifest`, not from any page — that is why a search for them in the HTML finds nothing. |
| `og-image.png` | The picture shown when a link is shared on WhatsApp, LinkedIn or Facebook. **Never rename it** — social platforms cache the URL, so already-shared links would show a blank box. |

### Notes and config, not on the web

| File | What it does |
| --- | --- |
| `PROGRESS.md` | **Start here.** Every project on the site and one list of what is still open. |
| `OWNER-TODO.md` | Things only Eliot can do — Claude cannot log into Kit or Search Console. Plus the ideas-and-someday list. |
| `CLAUDE.md` | The rules Claude loads at the start of every session. 144 lines; it was 599 until 2026-08-20. |
| `README.md` | One line, shown on the GitHub page. |
| `requirements.txt` | Names one Python package, `pdfplumber`, needed by `scripts/extract_aqa_questions.py`. **Still needed** the next time an AQA series is added — AQA prints question numbers in boxed margin cells that PDFKit returns detached from their questions, so that one extractor reads by coordinates instead. |
| `LICENSE.txt` | The Creative Commons Attribution 3.0 text inherited from the HTML5 UP "Dopetrope" template the CSS descended from. No longer published, kept for the record; the credit CCA 3.0 actually asks for is in `_archive/README.txt`. |

---

## The paired folders — source in, web pages out

**You edit the left. A script writes the right.**

| You edit this | A script builds this | What it is |
| --- | --- | --- |
| `notes-data/` (347) | `revision-notes/` (179 live) | The revision notes: 166 topic pages plus hubs |
| `questions-data/` (167) | `practice-questions/` (173 live) | 1,267 **original** multiple-choice questions |
| `past-paper-questions-data/` (67) | `past-paper-questions/` (172 live) | The searchable bank of **real** exam questions |
| `flashcards-data/` (7) | `flashcards/` (13 live) | Six flashcard decks |
| `glossary-data/` (4) | `revision-notes/glossary/` | 325 definitions and 34 formulae |

**The confusing name to remember:** `questions-data/` feeds
`practice-questions/`, **not** the past-paper bank. They sort next to each other
and look like a pair. They are not.

**Why the two question banks must never mix:** `questions-data/` is 100%
original writing — that is what makes it Eliot's to sell.
`past-paper-questions-data/` reproduces real exam-board questions word for word.
If those ever crossed over, the site would be selling someone else's copyright.
Measured 2026-08-20: 0 exact and 0 near-duplicate stems between them.

Each of these directories carries its own `CLAUDE.md` with the rules that apply
inside it.

---

## The other live folders

| Folder | What it is |
| --- | --- |
| `past-papers/` (286 live) | **281 actual exam paper PDFs** plus five index pages. The biggest folder, and a genuine reason people find the site. Hand-organised; no script involved. |
| `css/` (44 live) | How the site looks. `main.css` is site-wide; `css/pages/` holds one file per page. |
| `js/` (6 live) | The only six hand-written scripts on the site — the menu, the flashcard player and the two search boxes. Every page works with JavaScript off; these only enhance. |
| `images/` (195 live) | Photos, 106 note diagrams, and 84 hand-drawn SVG diagrams used by the flashcards. The SVGs are referenced only from `flashcards/data/*.json`, so a tool that greps HTML reports them as unused. They are not. |
| `webfonts/` (1 live) | One icon font, **trimmed to only the icons the site uses**. Adding a new icon means adding its CSS rule *and* re-running the subsetter, or it renders as nothing at all, silently. |
| `marking-examples/` (2 live) | The two example PDFs on the marking page. |
| `sitemaps/` (7 live) | The seven real Google maps. Generated. |

---

## Folders you never need to open

| Folder | Files | What it is | Matters? |
| --- | ---: | --- | --- |
| `scripts/` | 45 | The 8 builders and ~16 checkers. The machinery. | **Yes** — without it nothing can be rebuilt |
| `templates/` | 2 | The menu and footer, written once and stamped into all 463 pages at build time. **Not fetched by the browser** and no longer published — but ten scripts read it, so **deleting it means the navigation can never be changed again.** | **Yes** |
| `docs/` | 52 | Project records, the known-errors log, reference guides and the eleven-phase audit | Yes, as reference |
| `.github/` | 1 | Tells GitHub to run every check automatically on each push | Yes, quietly |
| `.claude/` | 4 | Claude's settings, the generated-file hook, and the `/verify` and `/rebuild-nav` shortcuts | Yes |
| `boards-data/` | 1 | One file naming the four exam boards, so they are spelled consistently everywhere | Small but load-bearing |
| `seo/` | 42 | The SEO audit and Search Console exports — **plus `seo/tools/verify_seo.py`, which runs on every push** | See below |
| `_working/` | 20 | Scratch space. Holds the **full** Font Awesome font that the subsetter trims — do not delete that file | Partly |
| `_archive/` | 157 | Finished records and the old note drafts | No |
| `.venv/` | 0 | A Python folder on the Mac only. Not in the repo at all. | No |

**The underscore trick:** GitHub ignores any folder starting with `_`. That is
the only reason `_working/` and `_archive/` are not public — no configuration
needed and it cannot be forgotten. Adding a `.nojekyll` file would expose both
immediately.

---

## `seo/tools/verify_seo.py` — the check that protects the traffic

It runs on every push and makes 14 assertions across all 461 pages, not a
sample. In plain terms it proves:

- **Every internal link points at the real address** — 34,399 links checked. No
  dead links, no wrong-case links, nothing pointing at a URL that redirects.
- **Every page tells Google "this is the original"** (a self-referencing
  canonical).
- **All 461 titles are unique, and all 461 descriptions are unique.** Duplicates
  are a common reason Google quietly stops indexing pages.
- **No page accidentally says "do not index me"** — except `404.html` and
  `confirmation.html`, deliberately.
- **The sitemap matches the filesystem exactly** — no URL Google cannot reach,
  no page missing from the map.
- **Every page is within 3 clicks of the home page**, and **every page has at
  least 3 links pointing at it.** Orphaned pages do not rank.
- **No link crosses an exam board.** An Edexcel student is never sent to an AQA
  page by accident, apart from the glossary board selector and the main menu.

For a site that lives on search traffic, this is the check protecting the income.

---

## Three things worth knowing

**Some folders show more tracked files than live ones.** `revision-notes/` is
180 tracked and 179 live; `css/` is 45 and 44. The extra file in each is a
`CLAUDE.md` — instructions for Claude, deliberately kept off the web by a line
in `_config.yml`. Both directories *are* published, so that line is what stops
them being served.

**The two most fragile files are `CNAME` and `_config.yml`.** Both tiny, both
boring, and either going wrong takes down something big — the domain, or the
privacy of everything meant to stay internal.

**Three things are genuinely irreplaceable if lost:** `past-papers/` (281 PDFs
collected by hand), `notes-data/` (the writing) and `questions-data/` (1,267
questions written from scratch). Everything else is either rebuildable by a
script or replaceable.
