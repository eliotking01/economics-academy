# Phase 7 findings — information architecture & UX

Branch `audit/organisation-audit`, working tree at `a02ee42`. Compiled
2026-08-09. **Read-only phase: no site file was opened for writing.**

Findings continue the audit's sequence at `PH07-056`. Click depth is **not**
re-measured here — P3 §1 did it, and P7 uses those numbers.

---

## 1. The navigation, as a tree

Parsed from `templates/header.html` with `html.parser`. **32 links, maximum
depth 3, 4 of them `href="#"` toggles.**

```
Home                          /
Tutoring                      /tutoring.html
Marking                       /marking.html
Revision Notes                /revision-notes/
  Edexcel                     #
    Theme 1..4                /revision-notes/edexcel-theme-{1..4}/
  AQA                         #
    Microeconomics            /revision-notes/aqa-a2-micro/
    Macroeconomics            /revision-notes/aqa-a2-macro/
  Macro Application           /revision-notes/macro-application/
  Glossary & Formulae         /revision-notes/glossary/
  Flashcards                  /flashcards/          <-- root URL, nested nav
Practice Questions            /practice-questions/
  Edexcel                     #
    Theme 1..4                /practice-questions/edexcel-theme-{1..4}/
  AQA
    Microeconomics            /practice-questions/aqa-a2-micro/
    Macroeconomics            /practice-questions/aqa-a2-macro/
Past Papers                   /past-papers/
  Search Past Paper Questions /past-paper-questions/  <-- root URL, nested nav
  AQA Papers                  /past-papers/aqa/
  Edexcel Papers              /past-papers/edexcel/
  OCR Papers                  /past-papers/ocr/
  Edexcel B Papers            /past-papers/edexcel-b/
About                         /about.html
Contact                       /contact.html
```

**Not in the nav at all:** `/faq.html`, `/privacy.html` (both in the footer), and
the two diagram galleries `/revision-notes/{macro,micro}economics-diagrams.html`
— 89 images of real content, reachable only from the 47 notes pages that `d1e7a3a`
linked to them.

## 2. Where every user-visible board label comes from

Extracted from the nav and from the third breadcrumb crumb on every page.

| Surface | Edexcel A appears as | AQA appears as |
| --- | --- | --- |
| nav, Revision Notes | `Edexcel` → `Theme 1` | `AQA` → `Microeconomics` |
| nav, Past Papers | `Edexcel Papers` | `AQA Papers` |
| notes-topic breadcrumb (166) | `Edexcel Theme 1: Introduction to Markets and Market Failure` | `AQA Microeconomics` |
| mcq-topic breadcrumb (166) | `Edexcel Theme 1` | `AQA Microeconomics` |
| notes-hub / mcq-hub breadcrumb | `Edexcel Theme 1` | `AQA Microeconomics` |
| flashcards breadcrumb (6) | **`Edexcel A Theme 1`** | `AQA Microeconomics` |
| ppq breadcrumb (89) | **`Edexcel`** | **`AQA`** |
| past-papers breadcrumb (4) | **`Edexcel A`** | **`AQA`** |

## 3. Conversion paths, by family

Body links only — the injected footer is excluded, since it is identical
everywhere.

| Family | Pages | → tutoring | → marking | → contact |
| --- | ---: | ---: | ---: | ---: |
| notes-topic | 166 | 166 | 166 | 0 |
| mcq-topic | 166 | 166 | 0 | 0 |
| ppq | 90 | 90 | 90 | 0 |
| notes-hub | 7 | 6 | 6 | 0 |
| mcq-hub | 7 | 7 | 1 | 0 |
| past-papers | 5 | 5 | 5 | 0 |
| notes-other | 3 | 3 | 3 | 0 |
| root | 9 | 6 | 4 | 3 |
| **glossary** | **3** | **0** | **0** | **0** |
| **flashcards** | **7** | **0** | **0** | **0** |

## 4. Interactive surfaces

| Component | Pages | Family |
| --- | ---: | --- |
| `quiz.js` | 173 | mcq-topic 166, mcq-hub 7 |
| `question-search.js` | 90 | ppq |
| `flashcards.js` | 7 | flashcards |
| `glossary-filter.js` | 3 | glossary |
| FAQ search | 1 | `faq.html` |
| `#filter-bar` | 1 | macro-application |

Six independent search/filter implementations. Only `question-search.js` is
described in CLAUDE.md as reusable, and it is reused — on the master page and,
pre-filtered, on all 90 topic pages.

---

## 5. Findings

### PH07-056 — Edexcel A is labelled six different ways and AQA four, in text students read, and "Edexcel" never distinguishes itself from "Edexcel B"

**Severity:** Medium-High · **Category:** Information architecture · **CERTAIN**

**Evidence.** §2. The same exam board is named `Edexcel`, `Edexcel A`,
`Edexcel Theme 1`, `Edexcel A Theme 1`, `Edexcel Papers`, and
`Edexcel Theme 1: Introduction to Markets and Market Failure` depending on which
part of the site the student is in. AQA is `AQA`, `AQA Papers`,
`AQA Microeconomics` and `Microeconomics`.

**This is the user-facing half of PH00-003.** Phase 9 audited the board-identity
problem in the *data* — `edexcel`, `edexcel-a`, `edexcel-theme-N` across URLs,
directory names and JSON fields — and proposed `boards.json`. It did not look at
what the reader sees. The same inconsistency is in the interface, and it has a
consequence the data version does not.

**The consequence.** The site publishes past papers for **four** boards and notes
for **two**. In the nav, a student sees `Edexcel Papers` and `Edexcel B Papers`
side by side under Past Papers — so "Edexcel" there implicitly means "Edexcel A".
But under Revision Notes they see only `Edexcel`, with no `Edexcel B` anywhere,
and nothing on the notes pages says "A" at all: the breadcrumb reads
`Edexcel Theme 1`, the spec-alert names the unit, and the `<h1>` names the topic.

**A student on Edexcel B has no way to learn, from the notes section, that these
notes are not for them.** The only two places on the entire site that write
`Edexcel A` are the flashcards breadcrumb and the past-papers breadcrumb — 10
pages out of 463.

This is not hypothetical traffic. PH03-049 measured `/past-papers/edexcel-b/` as
one of the site's two best-earning URLs (158 clicks, 11,690 impressions). Edexcel
B students are arriving in numbers.

**Why it is not simply "rename everything".** Two constraints bind:

- **P5 / `DO-NOT-BREAK.md`:** on the 22 near-identical Edexcel/AQA page pairs, the
  breadcrumb, `<title>`, `<h1>` and `spec-alert` are the only things telling Google
  the two pages differ. Changing breadcrumb text changes a differentiator, so it
  must be done in a direction that adds specificity, never removes it.
- **URLs are frozen.** This finding is about **visible labels only**. No directory
  name, slug or URL changes.

**Recommendation.** Adopt one written label per board and apply it to visible text
only:

| Board | Label |
| --- | --- |
| Edexcel A (9EC0/8EC0) | **Edexcel A** |
| Edexcel B | **Edexcel B** |
| AQA | **AQA** |
| OCR | **OCR** |

That means the notes breadcrumb becomes `Edexcel A Theme 1: …`, the ppq
breadcrumb `Edexcel A`, and the nav `Edexcel A` — the form the flashcards
generator already uses. It **adds** a differentiating token to 166 notes
breadcrumbs rather than removing one, so it is compatible with P5.

Sequence it with **PH09-022's `boards.json`**, which is where a `displayName`
field belongs. Doing it there means the label is decided once and every generator
reads it; doing it by hand means six generators and the nav template drifting
again.

**Effort:** M · **Risk of acting:** Low-Medium — touches visible text on ~460
pages, so it needs `verify_text_integrity.py` against the prior commit ·
**Risk of not acting:** Medium — students on the wrong board ·
**Dependencies:** PH09-022 · **Status:** OPEN

### PH07-057 — Two features have a root-level URL and a nested nav position, against the rule CLAUDE.md writes down

**Severity:** Low-Medium · **Category:** Information architecture · **CERTAIN**

**Evidence.** CLAUDE.md, "Where a new feature's URL goes":

> **A feature nests under the section it belongs to; only a standalone tool sits
> at root.** The glossary is `/revision-notes/glossary/` because it is a glossary
> of the notes' own terms. `/flashcards/` and `/practice-questions/` are at root
> because they stand on their own.

Against the nav in §1:

| Feature | URL says | Nav says | Agree? |
| --- | --- | --- | --- |
| Glossary | nested (`/revision-notes/glossary/`) | nested, under Revision Notes | **yes** |
| Practice Questions | root (`/practice-questions/`) | top-level item | **yes** |
| **Flashcards** | root (`/flashcards/`) | **nested, under Revision Notes** | **no** |
| **Past-paper questions** | root (`/past-paper-questions/`) | **nested, under Past Papers** | **no** |

Two features declare themselves standalone in the URL grammar — the decision
CLAUDE.md says to make once, before the URLs ship — and are then presented as
sub-items of another section.

**Why it matters, and why it is Low-Medium.** Nothing is broken and no URL is
wrong. But `setActivePage()` in `inject-templates.js` highlights by path prefix,
so a student on `/flashcards/` gets the **Revision Notes** nav item highlighted
while standing on a page whose URL is not under `/revision-notes/`. CLAUDE.md
notes `/flashcards/` "needed its own line for that reason" — the workaround
exists, which is the tell that the two decisions disagree.

The past-paper-questions case is milder: nesting it under Past Papers is
defensible in a way flashcards-under-notes is not, since it *is* about past
papers.

**Recommendation.** Do not move any URL — that is frozen, and CLAUDE.md's own
analysis of the glossary in 2026-08-07 rejected redirect stubs on exactly this
ground. Instead **make the nav match the URL**: promote Flashcards to a top-level
nav item beside Practice Questions. One line in `templates/header.html`, and it
removes the special case in `setActivePage()`.

If instead the *nav* is judged right and flashcards really is a revision-notes
sub-feature, then record that in CLAUDE.md and accept that the URL rule was not
followed — but do not leave the two disagreeing silently.

**Effort:** S · **Risk of acting:** Low — one template line ·
**Risk of not acting:** Low · **Dependencies:** none · **Status:** OPEN

### PH07-058 — The glossary and flashcards are commercial dead ends; every other family converts

**Severity:** Medium · **Category:** Conversion paths · **CERTAIN**

**Evidence.** §3. Ten pages carry **zero** body links to `tutoring.html`,
`marking.html` or `contact.html`:

```
revision-notes/glossary/{,edexcel-a/,aqa/}       3 pages
flashcards/{,edexcel-a/theme-{1..4}/,aqa/{micro,macro}/}  7 pages
```

Every other family links to tutoring on effectively every page — 166/166 notes,
166/166 mcq-topic, 90/90 ppq — and to marking on 166/166 notes and 90/90 ppq.

**Why it matters.** These are the site's two newest features and they are the two
that ask most of a student's attention: a glossary is consulted repeatedly, and a
flashcard deck is a return-visit surface with spaced repetition built in. They are
exactly where an engaged student is, and they are the only places with no path to
the paid services. The injected footer is the sole route, and PH03-049 established
what template-only linking is worth.

It also reads as an oversight rather than a choice: `seo/07b-link-decisions.md` §5
declined *more* links to `tutoring.html` on the grounds it is already the
most-linked page on the site (449 inbound). That is an argument against adding
links to families that already have them, not against covering two families that
have none.

**Recommendation.** Add the standard CTA block to the glossary and flashcards
generators — `build_glossary.py` and `build_flashcards.py` — matching the
`notes-cta` pattern the notes pages already use. Ten pages, two generator edits,
no hand-editing.

**Check against the declined decision first:** this adds 10 inbound links to
`tutoring.html`, taking it from 449 to ~459. That is inside the spirit of the
decline (which was about *bulk* additions across 166+ pages), but it does
increase a count that document flagged, so record it rather than assume.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low-Medium ·
**Dependencies:** none · **Status:** OPEN

### PH07-059 — Two responsive breakpoint systems run on every page, and they disagree by 32 pixels on the site's most-loaded stylesheet

**Severity:** Medium · **Category:** Responsive design · **CERTAIN**

**Evidence.** Ten distinct breakpoint values across the site's stylesheets:

```
1680 (3)  1280 (3)  992 (3)  980 (5)  768 (20)  767 (3)  736 (15)  600 (1)  576 (1)  480 (6)
```

Per sheet:

| Sheet | Breakpoints | System |
| --- | --- | --- |
| `css/main.css` | 1680, 1280, 992, 980, **768, 767, 736**, 576 | **both** |
| `revision-notes-textbook.css` (169 pages) | **768**, 480 | Bootstrap-ish |
| `quiz.css` (166), `past-paper-questions.css` (90) | **736** | theme |
| `glossary.css`, `flashcards.css`, `privacy.css`, `revision-notes-topics.css` | 736 | theme |
| `tutoring.css` | 992, 768, 736, 480 | both |
| `contact.css` | 992, 768, 736 | both |
| `faq.css`, `home.css` | 980, 736 | theme |
| `macro-application.css` | 980, 768, 600, 480 | both |

**1680 / 1280 / 980 / 736 / 480 is the inherited HTML5 UP theme's set.
992 / 768 / 576 is Bootstrap's.** Both are live, on every page, because
`css/main.css` contains both and each page sheet picks one or mixes them.

**The concrete defect.** `css/main.css` switches the page chrome to its tablet
layout at **736 px**. `revision-notes-textbook.css` — the stylesheet on **169
pages, more than any other** — switches the textbook content at **768 px**. So
between **737 px and 768 px** the notes pages render tablet chrome around desktop
content. That band includes the iPad Mini portrait width (768) and sits directly
in the range of small tablets and large phones in landscape.

`css/main.css` containing **736, 767 and 768** simultaneously is the clearest
single symptom.

**Why it matters.** It is invisible until someone loads a page at exactly the
wrong width, which is why it has survived. It is also the kind of thing that gets
"fixed" per-component forever unless the systems are reconciled once.

**Recommendation.** Pick one system and state it in CLAUDE.md's CSS conventions,
which currently say nothing about breakpoints. **Recommend the theme's set**
(1680/1280/980/736/480) rather than Bootstrap's, on the grounds that `css/main.css`
is inherited, is on all 463 pages, and is the more expensive of the two to change.
Then move `revision-notes-textbook.css`'s 768 to 736 first — highest page count,
smallest edit, and it closes the specific 32 px band.

**Verify by loading a notes page at 750 px** before and after, per the repo's own
method. This is CSS-only; no HTML changes.

**Effort:** M · **Risk of acting:** Medium — responsive layout, and a wrong
breakpoint is invisible on a desktop ·
**Risk of not acting:** Low-Medium · **Dependencies:** none · **Status:** OPEN

---

## 6. Received from Phase 8: print styles

P8 measured this and handed the judgement here.

```
@media print blocks, whole site : 5
  revision-notes-textbook.css   : 3   (169 pages)
  glossary.css                  : 1   (3 pages)
  flashcards.css                : 1   (7 pages)
```

**179 pages have print styles. 284 do not** — including all 166 practice-question
pages, all 90 past-paper-question pages, the 5 past-paper hubs and the 9 root
pages.

**P7's judgement: this is correct as it stands, and is not a finding.** The
families that have print styles are the ones a student prints — notes, glossary,
flashcards. The families that lack them are interactive by nature: a
practice-question page is a quiz whose answers are revealed by script, and a
past-paper-question page is a search interface whose value is the filtering. A
printed copy of either is not a worse experience, it is a different and largely
pointless artefact — and the actual printable content, the exam papers, is already
PDFs.

The one arguable gap is the two diagram galleries (`notes-other`), which carry 89
images and **do** load `revision-notes-textbook.css`, so they inherit its print
rules. Covered.

**Recorded as considered and declined**, so it is not raised again.

---

## 7. What Phase 7 checked and found clean

- **Nav depth is 3 and every nav destination resolves.** 32 links, 28 real hrefs,
  4 `#` toggles (the toggles are PH08-037, already logged).
- **Every page family has a consistent interactive surface.** Six search/filter
  implementations, each on exactly the family it belongs to, none half-applied.
- **Click depth to the two paid services is 1 from anywhere**, via the injected
  nav, and ≤2 in the raw graph from 452 of 463 pages.
- **`question-search.js` is genuinely reused**, as CLAUDE.md claims — one
  component, 90 pre-filtered topic pages plus the master page.
- **Print styles are correctly scoped** — see §6.

---

## 8. Handed on

| Item | To | Why |
| --- | --- | --- |
| PH07-056's board labels | **P11, with PH09-022** | `displayName` belongs in `boards.json`. Doing the labels without it re-creates the drift. |
| PH07-058's CTA blocks | **P11** | Two generator edits; check the `tutoring.html` inbound count against `seo/07b-link-decisions.md` §5 first. |
| PH07-059's breakpoints | **P11** | CSS-only, but needs visual verification at 750 px. |
| CLAUDE.md has no breakpoint convention | **P10** | P10 audits `CLAUDE.md`'s quality; this is a concrete gap to add. |

No new open questions. PH07-056 is the one worth reading twice.
