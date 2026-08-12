# Economics Academy

Static site: free A-Level Economics revision notes and past papers, plus paid
tutoring and marking. Solo project, no team.

## Hard constraints

- **Never alter existing economics wording.** Formatting, markup and structure
  only. A wording or content change needs an explicit instruction, every time.
- **Never bulk-rewrite prose with a script.** Scripted paragraph rebuilds have
  silently destroyed `<a>` tags here before. Edit prose by hand.
- **`main` auto-publishes** to economicsacademy.co.uk via GitHub Pages. Confirm
  before any push.
- **Never commit secrets, API keys or credentials.** Nothing in this repo is a
  secret today; keep it that way.

## Tooling

No build step for the site's own pages, no lint, no `package.json`. Changes are
still verified by opening the page — Live Server in VSCode.

**There is CI.** `.github/workflows/verify.yml` runs the whole verification
suite on every push and pull request. It is **verification only and must never
gain a build or deploy step** — switching Pages to Actions-based deployment
disables `_config.yml`'s `exclude`, which is the only thing keeping working
files off the live site. Approved on exactly that basis.

Two things it needs that are easy to break:

- **`fetch-depth: 0`.** `build_sitemap.py` reads every `<lastmod>` from
  `git log -1 -- <path>`, which a shallow clone cannot answer, and two checks
  diff against `HEAD~1`. A shallow clone fails the workflow, not the site.
- **Both jobs need `node`**, for Prettier and the glossary's KaTeX pre-render.

The verifiers are all stdlib-only and can still be run by hand:

```
python3 scripts/verify_generated.py          # every generator, output vs source
python3 scripts/verify_published_surface.py  # nothing unexpected is served
python3 scripts/verify_liquid.py             # a stray {%…%} fails the DEPLOY
python3 scripts/verify_icons.py              # the Font Awesome subset covers every icon used
python3 scripts/verify_image_dimensions.py   # every <img> width/height matches its file
python3 scripts/verify_css_load_order.py     # main.css is linked before every page stylesheet
python3 scripts/verify_page_shell.py         # the <head>, wrapper and script tail have not drifted
python3 scripts/verify_boards.py             # boards.json matches its pinned copy AND the code
python3 scripts/build_sitemap.py --check     # read the EXIT CODE, see below
```

**Two scripts need a package and are deliberately NOT in CI.** They are one-off
conversions, not build steps, and both default to dry run:

```
python3 scripts/reencode_diagrams.py --apply    # Pillow
python3 scripts/subset_fontawesome.py --apply   # fonttools + brotli
```

Everything the workflow runs is stdlib-only and must stay that way.

**The `<head>` is generated for 446 of the 463 pages** by `scripts/page_shell.py`,
which all five generators import. **17 pages are not generated**, not 9: the 9
root pages (permanently out of scope, `docs/audit/DECISIONS.md` D34), the 5
`past-papers/` hubs and the 3 `revision-notes/` non-topic pages. The figure
"454" appeared here and in three other documents until 2026-08-11; it was
`463 − 9` rather than a measurement, and no generator writes the missing 8.
Re-derive it with `python3 scripts/verify_page_shell.py`, whose first line
prints the split. The 173 notes pages (166 topic + 7 hub) are rendered by
`scripts/build_notes_pages.py` from `notes-data/`, which holds a verbatim byte
slice of each page's content plus its lifted metadata — **do not hand-edit a
notes page, edit the slice and re-run**. `scripts/extract_notes_pages.py` is the
one-off that created them and defaults to a dry run.

**The header and footer are baked into all 463 pages at build time.** Nothing
is fetched at page load. `js/components/nav.js` builds the mobile `#navPanel`
and `#titleBar` from `#nav` and adds the two things CSS cannot do for the
desktop dropdowns; the dropdowns themselves are CSS, so they work with
scripting off. `templates/header.html` and `templates/footer.html` are still
the single source of truth and are still published. **Editing the nav is a
rebuild, not a one-file edit:**

```
# edit templates/header.html, then:
python3 scripts/build_notes_pages.py && python3 scripts/build_past_paper_questions.py \
  && python3 scripts/build_questions.py && python3 scripts/build_glossary.py \
  && python3 scripts/build_flashcards.py     # the 446 generated pages
python3 scripts/bake_templates.py --apply    # the other 17; dry run without --apply
python3 scripts/build_sitemap.py             # lastmod moved on every page you changed
```

`bake_templates.py` also owns the **script tail** on those 17, from Wave 4.10.
The other 446 take it from `page_shell.SCRIPT_TAIL`, which is the one place the
tail is declared; `verify_page_shell.py` check 2 restates it as an independent
literal, so changing the tail has to change two files in the same commit.

`verify_page_shell.py` **check 9** is what makes the 463 copies safe: it lifts
the block back out of every page and requires it to equal the template byte for
byte, and asserts 0 pages still carry a runtime placeholder. A nav edit that
reaches 462 pages fails there rather than shipping.

**What an exam board is called and where it lives is recorded once**, in
`boards-data/boards.json`, and five generators read it through
`scripts/board_data.py` — Wave 3.2, D39. **Editing a board name or slug is a
two-file commit:** `verify_boards.py` keeps an independent restatement of the
whole record in `PINNED`, because its comparison against the generators is
circular now that they read it. `--show` reprints the table.

**The record holds a name PER CONSUMER, and collapsing them rewrites live
pages.** Theme 2 ships as three different strings — `names.taxonomy` with an em
dash in `taxonomy.json` and the notes hub `<h1>`, `names.flashcards` with a
hyphen in the decks, and `names.practiceQuestionsButton` as "Theme 2: The UK
Economy" on the practice-questions hub. All three are correct. `board_data.py`
therefore hands back the record and never a canonical "name of a group"; do not
give it one. **Its group order is published output too** — `BOARD_ORDER` is that
order's index and it sorts every board index page — which is what
`board_data.EXPECTED_NOTES_DIRS` is guarding.

Prose that names a board is page copy, not board identity, and stays in the
generator that prints it: `build_glossary.BOARD_COPY`,
`build_questions.HUB_SECTIONS` and the hub's own meta description.

**Three published assets are generated and must not be hand-edited:**
`css/fontawesome-all.min.css` is a **subset**, not the full library, despite the
name — it is kept so that 463 `<head>` blocks do not have to change;
`webfonts/fa-solid-900.woff2` is subsetted from the full font kept in
`_working/fontawesome/`; and the 112 PNGs in `images/diagrams/` are re-encoded
to a 64-colour palette. Adding an icon means adding its rule to the stylesheet
and re-running the subsetter — `verify_icons.py` fails if you forget, because a
subset font renders a missing glyph as nothing at all, silently.

**`build_sitemap.py --check` prints "nothing written" on both paths.** It is not
a pass signal — it means "this run wrote nothing". The pass signal is exit 0 and
no `WOULD CHANGE` lines. Misreading it once already let a stale sitemap ship.

Prettier 3.9.6 is used via `npx prettier@3.9.6`; it is not installed and there is
no config. Two generators run it over their own output, which is why committed
output is `prettier(render)` and why `verify_generated.py` compares by
regenerating rather than by rendering into memory.

**Where a number in this file is one a script computes, cite the script, not the
value.** Counts here have drifted before and the drift is invisible: this file
said the `rewrite` block covered 46 definitions while `verify_glossary.py` check
7 printed a different figure on every run for weeks, and nothing compared them.
**That check printed `44/44` when PH10-061 was written and prints `43/43`
today** — the number written down to illustrate a stale number had itself gone
stale, here and in DO-NOT-BREAK, which is the strongest case for the rule there
is. A number that cannot go stale beats a number that is right today. PH10-061.

## How publishing works

`main` is served by GitHub Pages with **the default Jekyll build** — there is no
`.nojekyll`, and there is a `_config.yml` that exists only to hold an `exclude`
list. Two consequences that are not obvious:

- **`_config.yml` decides what is published.** It exists only to hold an
  `exclude` list, which keeps the repo's working files off the site: `scripts/`,
  `raw-notes/`, `docs/`, the seven `*-data/` directories (including
  `boards-data/` and `notes-data/`) and the root markdown.
  Before it, `/REVIEW-NOTES.html`, `/CLAUDE.md` and `/scripts/build_glossary.py`
  were all live. **`exclude` replaces Jekyll's defaults rather than adding to
  them**, so the defaults are restated in the file; anything deleted from that
  list becomes public again.
- **Still public by decision:** `past-paper-questions/` is fetched at runtime
  and must stay. `templates/` is **no longer fetched** — Wave 2 Phase 7 bakes it
  in at build time — and stays published anyway, because unpublishing it removes
  two live URLs and that is a separate decision nobody has needed to make.
  `specificiations/` holds the exam-board PDFs and is a separate call.
- **Directories beginning with `_` are excluded**, by Jekyll's own rule. That is
  what makes `_working/` a safe place for build-time working files. **Adding a
  `.nojekyll` file would immediately expose every `_` directory** — if that is
  ever wanted, move `_working/` out of the repo first.
- **Jekyll runs Liquid over every markdown file, before Markdown.** A stray
  `{%` opens a tag that never closes and **the whole deploy fails** — not the
  page, the deploy. Backticks do not protect it: Liquid runs first and has no
  idea what a code span is. This has happened once, on a line quoting the LaTeX
  `\text{` followed by an unescaped `%`. Wrap such text in
  `{% raw %}` … `{% endraw %}`, and run `python3 scripts/verify_liquid.py`,
  which reproduces Liquid 4.0.4's behaviour and was cross-checked against it.
  The site's own HTML is safe — it has no front matter, so Jekyll copies it
  verbatim without rendering.

## Layout

```
revision-notes/{edexcel-theme-1..4,aqa-a2-micro,aqa-a2-macro}/  166 topic pages, each dir has index.html - GENERATED
revision-notes/{macro,micro}economics-diagrams.html             diagram galleries
revision-notes/macro-application/                               real-world data page
past-papers/{aqa,edexcel,edexcel-b,ocr}/{a-level,as-level}/paper-N/   281 PDFs, index.html per board
templates/{header,footer}.html                                  baked in at build time
css/main.css                                                    site-wide
css/pages/<page>.css                                            one per page
js/components/, js/data/                                        hand-written; the rest is vendor
images/diagrams/                                                112 note diagram PNGs (+83 SVGs in svg/)
raw-notes/edexcel/<spec-code>.md                                markdown source for converted notes
revision-notes/glossary/{,edexcel-a/,aqa/}                      generated glossary pages
glossary-data/                                                  glossary source of truth
boards-data/boards.json                                         canonical board identity, read by 5 generators via scripts/board_data.py
notes-data/{hubs,topics/<board-dir>}/                           byte slice + metadata for the 173 generated notes pages
_working/glossary/                                              build-time working files, not published
```

Root holds the commercial and utility pages: `index`, `tutoring`, `marking`,
`about`, `contact`, `faq`, `privacy`, `confirmation`, `404`.

Names are lowercase kebab-case throughout. Topic pages are
`1-2-3-short-title-slug.html` — spec code with dots as hyphens. Paper PDFs are
`{board}-{level}-economics-paper-{n}-{month}-{year}-{question-paper|mark-scheme}.pdf`.

### Where a new feature's URL goes

**A feature nests under the section it belongs to; only a standalone tool sits
at root.** The glossary is `/revision-notes/glossary/` because it is a glossary
of the notes' own terms. `/flashcards/` and `/practice-questions/` are at root
because they stand on their own.

**Decide this once, before the URLs ship.** GitHub Pages cannot issue a 301 —
there is no `_redirects`, `netlify.toml`, `vercel.json` or `.htaccess` here, and
the default Jekyll build offers nothing equivalent. A meta-refresh or JS
redirect is the only option, both pass authority unreliably, and the stub pages
then have to stay in the repo permanently. Evaluated for the glossary on
2026-08-07 and rejected on exactly that basis; see `_working/glossary/PROGRESS.md`.

Nesting has one incidental benefit: the nav highlight is chosen by path prefix,
so a page under `/revision-notes/` needs no new rule. `/flashcards/` needed its
own line for that reason. The rule list is `PAGE_MAP` in `scripts/page_shell.py`
— it moved there from the nav script in Wave 2 Phase 7, when the
`class="current"` started being written at build time.

## How a page is assembled

Standalone HTML, no includes and no partials. The header and footer are baked
into every page from `templates/header.html` and `templates/footer.html` at
build time — `page_shell.bake()` for the 446 generated pages,
`scripts/bake_templates.py` for the other 17. Nothing is fetched at page load.
Everything else is duplicated per file.

A new page needs: the gtag block, `<html lang="en-GB">`, title, meta
description, canonical, OG and Twitter cards, JSON-LD, the favicon/manifest set,
`/css/main.css`, its own `/css/pages/<page>.css`, the script tail (**cite
`page_shell.SCRIPT_TAIL`** — it is two scripts today, was four until
2026-08-12 and seven until 2026-08-11, and a list written out here goes stale
without anything noticing) and the baked header and footer blocks. Add it to `sitemap.xml`. If it is hand-written
rather than generated, add it to `bake_templates.py`'s `EXPECTED` count in the
same commit, or that script refuses to run. Topic pages carry two JSON-LD blocks — `LearningResource` and
`BreadcrumbList` — and load MathJax 3 from jsDelivr only if they use `\( … \)`.

## Conventions

**HTML**

- `<strong>` for key terms, table row labels and bullet lead-ins. `<em>` only for
  logical contrast. Never `<b>`, `<i>`, `<u>`, `<mark>`.
- Root-absolute paths: `/images/…`, `/css/…`, `/marking.html`.
- Expand/collapse is a `<button>` with `aria-expanded` and `aria-controls`, wired
  up in JS. No `onclick` attributes remain in the repo; don't reintroduce one.
- Escape `<` as `&lt;` and `&` as `&amp;` in body text, LaTeX included.
- Diagram captions on topic pages open `Figure N:`.

**CSS**

- One stylesheet per page in `css/pages/`, named after the page.
- Scope it: put a wrapper class on the page's `<section id="main">` and nest
  every rule under it — `.revision-notes-content .notes-cta { … }`. Bare class
  names have already collided across two files.
- `:root` colour tokens live in `revision-notes-textbook.css` and are for notes
  only. Elsewhere use hex. The brand accent is `#d52349`.
- No inline `style` attributes — extract a class.

**Prose**

- UK English, £ sterling, "A-Level", A-Level register: precise and plain.
- Em-dash `—` in new prose. Existing notes use hyphens; leave them alone.

## Component library

Defined in `css/pages/revision-notes-textbook.css`, for topic pages.

| Class | Contract |
| --- | --- |
| `spec-alert` | Opens every topic page. `<strong>Specification Coverage:</strong> {Board} unit X.Y.Z - …` |
| `worked-example` | `<h3>Worked Example: …</h3>`, intro, table, then a sentence interpreting the number. Never end on the arithmetic. |
| `exam-tip` | One `<p>`, no heading. Bolded lead sentence, then 2–3 sentences. Corrects a specific confusion; never restates theory. |
| `concept-table` | Multi-column comparison. **Always** inside `<div class="table-container">`. |
| `calculation-table` | Two-column running calculation. **Never** wrapped. Last row is the answer. |
| `key-definition` | Inline term chip. |
| `formula-box` | Centred MathJax display. Must be preceded by `<!-- prettier-ignore -->`. |
| `flow-chain` / `flow-node` | Chained pill diagram. |
| `diagram-figure` / `-image` / `-caption` | `<figure>` + `<figcaption>`. Images need `width`, `height`, real alt text. |
| `notes-cta` | Closes every topic page. Three buttons; the past-papers link must match the page's board. |

House rules:

- **Max two components per page, total** — counting any already there.
- **Concision beats coverage.** 80% of topic pages carry no component, by design.
- A worked example earns its place only where the page states a formula it never
  demonstrates. Verify every figure by recomputation.
- Where a page has a twin on the other board, both use the component verbatim.

## Exemplars

- `revision-notes/aqa-a2-macro/2-1-3-uses-of-index-numbers.html` — worked
  examples and exam tips, densest page on the site
- `revision-notes/edexcel-theme-1/1-1-1-economics-as-a-social-science.html` —
  the plain topic-page shell
- `css/pages/macro-application.css` — the wrapper-scoping convention
- `templates/header.html` — nav structure

## Vocabulary

- **Boards**: Edexcel (A), Edexcel B, AQA, OCR. Notes cover Edexcel and AQA only;
  past papers cover all four.
- **"Theme 1–4"** = Edexcel, `revision-notes/edexcel-theme-N/`, real spec codes.
- **"AQA micro" / "AQA macro"** = `revision-notes/aqa-a2-micro|macro/`. These use
  **site-local** codes `1.x.y` and `2.x.y`, deliberately not the real AQA 7136
  codes (`4.1.x` / `4.2.x`). Ratified — do not "fix" them.
- **"Macro application"** = `revision-notes/macro-application/`, real-world UK and
  South Africa data for exam application.
- **"Twin"** = the page covering the same content on the other board.
- Papers: A-Level has papers 1–3, AS has 1–2; each sitting has a question paper
  and a mark scheme.

## Past paper question bank

In progress on `feature/question-bank`. **Read `PAST-PAPERS-PROGRESS.md` first.**

A searchable bank of real exam questions, at `/past-paper-questions/`. Distinct
from `/practice-questions/` in one decisive way: **it reproduces real exam
question text verbatim**, where the practice bank's hard rule is that every
question is 100% original. The two never share a data path.

### Scope

| In scope | Out of scope, permanently |
| --- | --- |
| Edexcel A **A Level** (9EC0), Papers 1–3 | **Section A, every board and qualification.** Do not extract it |
| Edexcel A **AS Level** (8EC0), Papers 1–2 | **AQA AS papers.** When AQA extends, A Level only |
| AQA A Level (7136) | Edexcel B, OCR, AQA specimen papers |

**8EC0 has no Section C** — verified from all 16 papers, not from the
specification. It is Section A (Q1–5, 20 marks) and Section B (Q6, 60 marks).
Section B is `Q6(a)–(g)`: (a)–(e) compulsory then **(f) OR (g)**, with (e)
always 15 and (f)/(g) always 20. So AS **merges what the A Level splits** —
(a)–(e) is 9EC0's Section B, (f)/(g) is 9EC0's Section C, but AS keeps both
inside Section B against the same extract block. Stored as `section: "B"`, as
printed. Do not invent a Section C for it.

Unlike 9EC0 Section C, **every AS part carries a `ctxPage`**, because the
essay choice sits under the Q6 extracts rather than having its own stimulus.

**Duplicates across qualifications: keep both, never collapse.** Checked at the
outset — 0 exact and 0 near-duplicates across 112 AS × 192 A Level, the maximum
being 0.754 on shared formulaic stems. If one ever appears, both entries stay
and both are labelled; a collapsed entry would hide that a question was set at
two different demands.

**Every card carries a qualification badge** (`AS Level` / `A Level`) in the
static HTML, not applied by script. AS and A Level are **mixed in one list** on
topic pages and both show by default on the master page; a `Qualification`
filter narrows. The badge is doing all the disambiguation, so it is never
optional.

- `past-paper-questions-data/edexcel-a/*.json` and `edexcel-a-as/*.json` — one
  file per paper, machine written by `scripts/extract_past_paper_questions.swift`.
  Never hand-edit. **Two directories because both qualifications have a Paper 1
  in the same series**, so `p1-june-2017.json` would otherwise name two
  different papers. They share a board and mix freely from the build onwards.
- **Source attributions are stripped at extraction**, not afterwards. Pearson
  prints `(Source adapted from: https://…)` under the Section C stimulus;
  `stripAttribution()` lifts it into a `sourceAttribution` field, which the
  build's field whitelist deliberately never emits into `questions.json`, so it
  stays out of the card and the search index. `scripts/strip_source_attributions.py`
  is the re-runnable safety net over data already on disk and should report
  **0 changes** — that agreement is the test. It edits the JSON as text, because
  both extractors hand-write theirs and a `json.dumps` round-trip would reformat
  all 64 files and break build idempotence.
- `past-paper-questions-data/tags.json` — topics and keywords, hand-written.
  Kept separate so re-extraction cannot destroy it.
- `past-paper-questions-data/taxonomy.json` — generated from the existing 87
  Edexcel topic records; the bank invents no taxonomy of its own.
- `past-paper-questions/index.html` and `questions.json` — **generated** by
  `scripts/build_past_paper_questions.py`. Do not hand-edit either; re-run it.
  It runs Prettier over its own HTML, so generating twice is byte-identical.
- **Each topic page also has its own `questions.json` beside it**, generated by
  the same script, so it does not fetch the whole bank to show one topic. The
  master `questions.json` stays where it is and is still what the master, board
  and section pages fetch — their Topic filter needs every topic on the board.
  In a per-topic payload, `papers` is a **sparse list with nulls**: the search
  component indexes into it with `q.p`, so re-packing it would silently re-point
  every question at the wrong paper.

Mark scheme content is **never** extracted. Each question deep-links to the
site's own hosted PDF at the right page.

PDF work uses **Swift + PDFKit**, not Python: there is no PDF library, no
`requirements.txt` and no venv here, but macOS ships PDFKit.

Search is `js/components/question-search.js` — one reusable component used on
the master page and, pre-filtered, on every topic page. No Fuse.js and no
dependency: it is a small bounded-edit-distance token index. Tested by
`node scripts/test_question_search.js`, which runs against the shipped file.

## Glossary & formulae

In progress on `feature/glossary`. **Read `_working/glossary/PROGRESS.md` first.**

Every definition and formula a student needs, one page per exam board, at
`/revision-notes/glossary/{edexcel-a,aqa}/` with a board selector at
`/revision-notes/glossary/`.

**The definitions are the notes' own words, with two declared exceptions.** Every
entry except those in `glossary-data/authored.json` is lifted verbatim from the
`<span class="key-definition">` chip and the paragraph that follows it on a topic
page, and `scripts/verify_glossary.py` re-reads the notes and fails if a shipped
definition no longer appears in its source page. The second exception is the
`rewrite` block in `curation.json`, which edits the **lead-in** of a set of
definitions at render time — `verify_glossary.py` check 7 prints how many — see
"Capitalisation and lead-in rewrites" below.

Outside those two, a term that reads badly is fixed **in the notes**, then
re-extracted — never edited in the glossary. Both exceptions are counted on
every `verify_glossary.py` run so neither goes quiet.

- `glossary-data/terms.json` — **generated** by `scripts/extract_glossary.py`
  from the notes HTML. Never hand-edit.
- **When a definition reads badly, look on the page before writing anything.**
  Three separate cases here turned out to have the real definition already in
  the notes, just somewhere the extractor could not reach: under a plain
  `<strong>Effect:</strong>` instead of a chip (`Maximum Price`), or in the
  `<ul>` below the chip (the five trading blocs). `excludeSources` +
  `authored.json`, and `attachList`, fixed both without inventing a word.
- `glossary-data/curation.json` — hand-written judgement: the non-term stop-list,
  display casing, alias merges, approved table harvests. Kept separate so
  re-extraction cannot destroy it, exactly as `tags.json` is for the past papers.
- `glossary-data/authored.json` — the **one exception** to the rule above.
  Definitions written for the glossary, covering concepts the notes teach without
  ever defining and that a specification requires. Tagged `origin="authored"`
  through to the page and exempt from the verbatim check, because there is
  nothing in the notes for them to match. **The file is meant to shrink:** move a
  definition into its notes page as a chip and the extractor picks it up, at
  which point the build errors until the authored copy is deleted. Reviewed in
  `_working/glossary/authored-review.md`.
- `revision-notes/glossary/**/index.html` — **generated** by
  `scripts/build_glossary.py`. Do not hand-edit; re-run it. It runs Prettier over
  its own HTML, so generating twice is byte-identical.

Formulae are **KaTeX pre-rendered to static HTML at build time**, with KaTeX's
CSS and woff2 fonts self-hosted in `css/vendor/katex/`. The notes pages still use
MathJax 3, so the same formula looks slightly different in the two places. Every
emitted KaTeX block needs `<!-- prettier-ignore -->` before it or Prettier
reflows it and the build stops being idempotent.

The full glossary is real HTML in the page, not fetched — it must be readable
with JavaScript off. `js/components/glossary-filter.js` only enhances.

**Search matches the term name only**, ranked exact → prefix → word start →
contains → fuzzy. `SEARCH_FIELDS` in that file is the whole of that decision.
Ranking needs the order to change, so a query moves the matches into one flat
list and hides the A–Z; clearing puts them back. A topic filter alone reorders
nothing and leaves the A–Z in place.

**Capitalisation and lead-in rewrites are applied at render time**, from
`curation.json`, never in `terms.json` — the data has to stay byte-identical to
the notes or the verbatim check stops meaning anything.

- `capitalise` — definitions the notes wrote as `Term: definition` get their
  first letter upper-cased. `verify_glossary.py` check 6 prints the count.
- `rewrite` — **the second declared exception to "the notes' own words"**, after
  `authored.json`. Definitions the notes wrote with the term as the sentence
  subject (*"Globalisation is the increasing integration…"*) have their lead-in
  replaced so they read as definitions. Instructed by Eliot on 2026-08-07,
  explicitly overriding the rule that such a definition is fixed in the notes
  and re-extracted. A rule replaces a **leading substring only**; most merely
  drop a lead-in and invent no word, and the few that do are marked `adds` or
  `not-a-definition`. `verify_glossary.py` check 7 prints both counts — how many
  are anchored and how many carry added wording. The build **fails** if `from`
  is no longer how the definition opens, so rewording a notes page cannot
  silently re-point a rule.

`scripts/check_glossary_capitalisation.py` classifies and reports both.
`verify_glossary.py` check 6 fails on any lower-case start nobody has ruled on;
check 7 keeps every rewrite anchored and prints how many are shown.

Because of this, **check 1 proves the extraction is faithful, not the page.**
Do not describe the glossary as word-for-word without that qualification — the
board pages' own intro was reworded on 2026-08-07 for the same reason.

There is **no synonyms or alternative-names field.** Abbreviations only match
because the notes put them in the term (`Price Elasticity of Demand (PED)`), and
the tokeniser splits on the brackets.

## Flashcards

In progress on `flashcards-feature`. **Read `docs/FLASHCARDS_PROGRESS.md`
first.**

Interactive revision flashcards at `/flashcards/`, one deck per board per
theme, with Leitner spaced repetition in localStorage. Pilot: Edexcel Theme 1
plus AQA variant cards. Supersedes ROADMAP's "flashcard mode on the glossary"
idea.

- `flashcards-data/<board>/<theme>.json` — hand-authored source of truth,
  excluded from publishing. Card text is card-optimised prose cross-checked
  against `glossary-data/terms.json` and the specs; where a notes chip
  definition is already tight it is reused verbatim and tagged
  `origin="notes-verbatim"`.
- `flashcards/**` and `flashcards/data/*.json` — **generated** by
  `scripts/build_flashcards.py`. Do not hand-edit; re-run it. Cards with
  `premium: true` never enter the public payloads.
- `images/diagrams/svg/` — hand-authored SVG diagrams for diagram cards, per
  `docs/DIAGRAM_STYLE.md`. Each is verified against its ground-truth PNG in
  `images/diagrams/` and self-QA'd via a headless-Chrome render before review.
- `js/components/flashcards.js` — progressive enhancement over static sample
  cards; the deck JSON is fetched at runtime (question-search.js pattern).

### Architectural note

Future freemium will use Stripe payment links, which cannot gate static
content by themselves. Premium gating will eventually require a lightweight
auth/delivery layer (e.g. Cloudflare Workers) serving premium JSON. Nothing in
this feature may assume client-side-only paywalling is sufficient; the premium
flag in the data schema exists so premium cards can later be excluded from
public payloads without restructuring. If the repo is public, premium content
ultimately cannot live in this repo at all. (The repo **is** public.)

### Standing rules

1. Never edit any existing written content on the site without my explicit
   approval in chat. You may always ask.
2. All flashcard content must be exam-board accurate. Where Edexcel A and AQA
   define or treat a concept differently, create separate board-specific cards
   and diagram variants.
3. The data model and code must remain freemium-ready per the ARCHITECTURAL
   NOTE in CLAUDE.md.
4. Every generated diagram must be verified against the existing diagram image
   (visually inspected, never trusted by filename) and its caption in the notes,
   must follow docs/DIAGRAM_STYLE.md, and must pass the SVG-to-PNG self-QA
   visual check before being presented for approval.
5. Update docs/FLASHCARDS_PROGRESS.md before ending any session and whenever
   context is running long, so a fresh session can resume seamlessly.
6. Present significant decisions as options with a recommendation; wait for my
   choice.

## See also

- **`docs/audit/` — the eleven-phase organisation audit and the roadmap being
  built from it. Start at `docs/audit/findings/PH11-synthesis.md` for what to do
  next, `docs/audit/PROGRESS.md` for what is already done, and
  `docs/audit/DO-NOT-BREAK.md` before touching anything. `DECISIONS.md` is
  append-only, D1–D39.** Excluded from publishing; readable in the public repo,
  on the same judgement as `REVIEW-NOTES.md`.
- `_working/glossary/PROGRESS.md` — live state of the glossary build.
- `_working/glossary/authored-review.md` — the authored **terms**, the only
  entries on the site that are not the notes' own words. Two units are in play
  and both are true, so say which you mean: `authored.json`'s `terms` list, and
  the same set counted as term-page instances, most appearing on both board
  pages. **Cite `python3 scripts/verify_glossary.py` check 1 for the second** —
  the pair was written here as 76 and 137 and re-derived on 2026-08-12 as 77
  and 138.
- `PROJECT-LOG.md` — what the two large pieces of work did, and the single
  consolidated list of what is still flagged. **Start here.**
- `PAST-PAPERS-PROGRESS.md` — live state of the past paper question bank.
- `docs/FLASHCARDS_PROGRESS.md` — live state of the flashcards build.
- `docs/DIAGRAM_STYLE.md` — the locked SVG diagram style guide.
- `docs/CONTENT_ISSUES.md` — suspected notes errors found while writing cards;
  logged for approval, never fixed unilaterally.
- `extraction-qa-report.md` — Phase 1 extraction QA for that bank.
- `_working/question-bank/as-extraction-qa.md` — QA for the Edexcel AS (8EC0)
  extraction, including the duplicate analysis that found none.
- `ROADMAP.md` — planned work.
- `QUESTIONS_GUIDE.md` — the authoring standard for the free practice questions.
- `REVIEW-NOTES.md` — problems found but not fixed, including open economics
  content errors. Log new ones there rather than fixing them.
- `QUESTIONS_PROGRESS.md` — the question bank's batch record and the recurring
  failure modes. Historical, but read §8 and §9 before extending the bank.
- `docs/revision-notes-audit.md` — the SEO and accessibility audit already applied.
- Third-party services: Formspree, Calendly, Stripe payment links, GA4. All IDs
  are public by design.
