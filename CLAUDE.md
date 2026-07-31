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

No build, no test, no lint, no CI, no `package.json`. There is nothing to run.
Changes are verified by opening the page — Live Server in VSCode.

`scripts/verify_*.py` (stdlib-only: HTML well-formedness, links, text integrity,
markup integrity) exist and can be run on demand. Nothing runs them
automatically. Prettier 3.9.6 has been used via `npx prettier@3.9.6`; it is not
installed and there is no config.

## Layout

```
revision-notes/{edexcel-theme-1..4,aqa-a2-micro,aqa-a2-macro}/  166 topic pages, each dir has index.html
revision-notes/{macro,micro}economics-diagrams.html             diagram galleries
revision-notes/macro-application/                               real-world data page
past-papers/{aqa,edexcel,edexcel-b,ocr}/{a-level,as-level}/paper-N/   281 PDFs, index.html per board
templates/{header,footer}.html                                  injected at runtime
css/main.css                                                    site-wide
css/pages/<page>.css                                            one per page
js/components/, js/data/                                        hand-written; the rest is vendor
images/diagrams/                                                300 note diagrams
raw-notes/edexcel/<spec-code>.md                                markdown source for converted notes
```

Root holds the commercial and utility pages: `index`, `tutoring`, `marking`,
`about`, `contact`, `faq`, `privacy`, `confirmation`, `404`.

Names are lowercase kebab-case throughout. Topic pages are
`1-2-3-short-title-slug.html` — spec code with dots as hyphens. Paper PDFs are
`{board}-{level}-economics-paper-{n}-{month}-{year}-{question-paper|mark-scheme}.pdf`.

## How a page is assembled

Standalone HTML. No includes, no partials, no build. Header and footer are
fetched at runtime by `js/components/inject-templates.js` and swapped into
`<div id="header-placeholder">` and `<div id="footer-placeholder">`. Everything
else is duplicated per file.

A new page needs: the gtag block, `<html lang="en-GB">`, title, meta
description, canonical, OG and Twitter cards, JSON-LD, the favicon/manifest set,
`/css/main.css`, its own `/css/pages/<page>.css`, and the seven-script tail
(jquery, dropotron, inject-templates, browser, breakpoints, util, main). Add it
to `sitemap.xml`. Topic pages carry two JSON-LD blocks — `LearningResource` and
`BreadcrumbList` — and load MathJax 3 from jsDelivr only if they use `\( … \)`.

## Conventions

**HTML**

- `<strong>` for key terms, table row labels and bullet lead-ins. `<em>` only for
  logical contrast. Never `<b>`, `<i>`, `<u>`, `<mark>`.
- Root-absolute paths: `/images/…`, `/css/…`, `/marking.html`.
- Expand/collapse is a `<button>` with `aria-expanded` and `aria-controls`. Never
  `onclick` on an `<li>` — the hub pages do that; don't copy it.
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

## See also

- `ROADMAP.md` — planned work.
- `REVIEW-NOTES.md` — problems found but not fixed, including open economics
  content errors. Log new ones there rather than fixing them.
- `docs/revision-notes-audit.md` — the SEO and accessibility audit already applied.
- Third-party services: Formspree, Calendly, Stripe payment links, GA4. All IDs
  are public by design.
