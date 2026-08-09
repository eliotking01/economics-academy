# Phase 4 findings — structured data validity

Branch `audit/organisation-audit`, working tree at `0af72ad`. Compiled
2026-08-09. **Read-only phase: no site file was opened for writing.**

Reproducible with `python3 docs/audit/scripts/structured_data.py [1-6]`. Findings
continue the audit's sequence at `PH04-052`.

**This phase answers Q11 / PH00-007 and closes PH08-045.**

---

## 1. What was measured

Every `<script type="application/ld+json">` block on all 463 pages, parsed with
`json.loads` and walked recursively so nested nodes (`isPartOf`, `hasPart`,
`acceptedAnswer`, `provider`) are checked, not just top-level ones.

```
pages with >=1 JSON-LD block : 461 of 463   (404.html and confirmation.html have none, correctly)
blocks total                 : 921
blocks that fail to parse    : 0
blocks per page              : 2 on 460 pages, 1 on 1, 0 on 2
@context                     : "https://schema.org" on every block
```

23 distinct `@type` values are in use across 15,000+ nodes:

| Nodes | Pages | `@type` | | Nodes | Pages | `@type` |
| ---: | ---: | --- | --- | ---: | ---: | --- |
| 5,098 | 167 | `Answer` | | 166 | 166 | `Quiz` |
| 5,068 | 166 | `Comment` | | 166 | 166 | `Thing` |
| 1,871 | 460 | `ListItem` | | 166 | 166 | `AlignmentObject` |
| 1,297 | 167 | `Question` | | 105 | 105 | `CollectionPage` |
| 559 | 2 | `DefinedTerm` | | 100 | 100 | `WebSite` |
| 460 | 460 | `BreadcrumbList` | | 11 | 3 | `WebPage` |
| 354 | 354 | `EducationalOrganization` | | 7 | 7 | `Person` |
| 181 | 181 | `LearningResource` | | 7 | 2 | `Offer` |
| 179 | 179 | `Course` | | 4 | 3 | `DefinedTermSet` |

plus `CollegeOrUniversity` (3), `Service` (2), `EducationalOccupationalCredential`,
`ContactPage` and `FAQPage` (1 each).

---

## 2. Findings

### PH04-052 — Q11 answered: the missing publisher markup is template divergence, not a decision — and the same 97 pages emit a site-level entity that belongs only on the homepage

**Severity:** Medium · **Category:** Structured data · **CERTAIN** ·
**Answers Q11 / PH00-007**

**Evidence.** `EducationalOrganization` is absent from **109** of 463 pages:

| Family | Pages without it |
| --- | ---: |
| ppq | **90** |
| mcq-hub | **7** |
| root | 6 — `404`, `confirmation`, `contact`, `faq`, `marking`, `tutoring` |
| notes-other | 3 — `revision-notes/index.html` and the 2 diagram galleries |
| past-papers | 1 — `past-papers/index.html`, while all 4 of its board children have it |
| glossary | 1 — `revision-notes/glossary/index.html`, while both board pages have it |
| flashcards | 1 — `flashcards/index.html`, while all 6 decks have it |

**The decisive evidence for Q11 is what those pages emit instead.** `WebSite` is
emitted on exactly **100** pages: `index.html`, `privacy.html`,
`revision-notes/glossary/index.html`, the 7 mcq-hub pages and all 90 ppq pages.

So the ppq and practice-questions-hub generators emit `WebSite` — a **site-level**
entity — and omit `EducationalOrganization`, the publisher. The notes and
mcq-topic generators do the opposite. **Two generators disagree about which
site-wide entity a page should carry, and each is internally consistent.** That is
a template that was written from different boilerplate, not a judgement about
reproducing Pearson's and AQA's question text.

Q11's recommended default was to treat it as an oversight. **The evidence supports
that**, and adds a second half nobody had asked about:

**All 100 `WebSite` nodes lack `potentialAction`.** `WebSite` exists in Google's
vocabulary to carry a `SearchAction` for the sitelinks search box, and that is
recognised **on the homepage only**. A `WebSite` node with just `name` and `url`,
on 90 topic pages, does nothing at all — it is not harmful, it is noise, and it is
occupying the slot where the publisher should be.

**Recommendation.**

1. **Add `EducationalOrganization` to the ppq and mcq-hub generators**, matching
   the reference form the other 354 pages already use
   (`@id: https://economicsacademy.co.uk/#organization`, `name`, `url`). Two
   generator edits and a re-run; no hand-editing.
2. **Remove `WebSite` from every page except `index.html`**, and give the
   homepage's copy a `potentialAction` if a site search is ever wanted. 99 pages
   lose a node that does nothing.
3. Add the publisher to the four hub pages that lack it while their children have
   it (`past-papers/`, `flashcards/`, `revision-notes/glossary/`,
   `revision-notes/index.html`) and to `contact`, `faq`, `marking`, `tutoring`.
   `404` and `confirmation` are `noindex` and should keep nothing.

**If the omission on `/past-paper-questions/` was in fact deliberate** — keeping
publisher identity off pages that reproduce exam-board question text — then say so
in `seo/08-structured-data.md` and leave it. That would be a good reason. But it
cannot be the reason as things stand, because those pages **do** carry `WebSite`
and `CollectionPage` naming the site, so the site is already identified as the
publisher of the page.

**Effort:** S — two generator edits · **Risk of acting:** Low ·
**Risk of not acting:** Low-Medium · **Dependencies:** none · **Status:** OPEN

### PH04-053 — 19 pages declare a breadcrumb trail in JSON-LD that does not exist on the page

**Severity:** Medium · **Category:** Structured data · **CERTAIN** ·
**Closes PH08-045**

**Evidence.** Confirmed independently of P8, by parsing the JSON-LD rather than
grepping for a class name — same 19 pages:

```
root         6   about, contact, faq, marking, privacy, tutoring
notes-hub    6   all six revision-notes board hubs
past-papers  5   index + all four board hubs
notes-other  1   revision-notes/index.html
mcq-hub      1   practice-questions/index.html
```

Each emits a full `BreadcrumbList` with correct positions and resolvable URLs,
and renders no visible trail at all.

**Why it matters.** Google's structured-data policy is that markup must describe
content visible on the page; breadcrumb markup with no on-page breadcrumb is
outside that. The practical risk is low — Google generally ignores rather than
penalises — but the second half matters more: **these 19 are hub and commercial
pages, and a user on `/past-papers/ocr/` has no way back up.** PH03-049 measured
that same page as one of the site's two best earners with a single inbound link.
It is a navigation gap on the pages that can least afford one.

**Recommendation.** Add the visible trail rather than remove the markup. The
markup is already correct and already names the right ancestors, so the trail can
be generated from it. The six notes hubs and `practice-questions/index.html` are
behind generators; the other 12 are hand-written and are exactly the kind of
repeated fragment D18's `page_shell.py` is meant to own — which argues for doing
this **during** the migration rather than twice.

**Effort:** S per page, M overall · **Risk of acting:** Low ·
**Risk of not acting:** Low-Medium · **Dependencies:** cheaper after D18 ·
**Status:** OPEN

### PH04-054 — `inLanguage` says `en` on 179 nodes and `en-GB` on 274, while every page declares `lang="en-GB"`

**Severity:** Low · **Category:** Consistency · **CERTAIN**

**Evidence.** `inLanguage` appears on 453 nodes:

```
en-GB : 274        en : 179
```

Meanwhile `<html lang="en-GB">` is on **463 of 463** pages (`metadata_census.py`,
unchanged since Phase 0). The 179 `en` nodes are the `LearningResource` blocks on
the notes topic and hub pages.

**Why it matters.** Low. `en` is not wrong, it is less specific, and no consumer
will be confused. It is logged because it is the same defect shape as PH08-039's
three MathJax configs and PH06-030's breadcrumb `aria-label`: **one value, two
answers, split along generator lines.** A site that says `en-GB` in the `<html>`
element on every page and `en` in a third of its structured data has no single
place where that fact is decided.

**Recommendation.** Make it `en-GB` everywhere, at the generator. One-line change
in the notes-page emitter. Fold into the D18 shell module's remit — the language
tag is exactly the sort of value the shell should own once.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low ·
**Dependencies:** none · **Status:** OPEN

### PH04-055 — The publisher is a four-property stub on 353 of 354 pages, and has no logo — while an unreferenced brand kit sits published in the repo

**Severity:** Low-Medium · **Category:** Structured data · **CERTAIN**

**Evidence.** Of 354 `EducationalOrganization` nodes:

```
carry @type, @id, name, url : 354
carry logo                  :   1     (index.html)
carry sameAs                :   1     (index.html)
carry description           :   1     (index.html)
carry founder               :   1     (index.html)
```

`index.html`'s copy is complete and points `logo` at
`https://economicsacademy.co.uk/android-chrome-512x512.png`. The other 353 are
references by `@id` to `https://economicsacademy.co.uk/#organization`.

**Referencing by `@id` is the correct linked-data pattern** and this is not a
defect in the abstract. The qualification is that **`@id` references are not
resolved across pages by search engines** — each page is parsed on its own. So on
353 pages the organisation is, in practice, a name and a URL with no logo, no
description and no `sameAs` links.

**Amended 2026-08-09 — see `DECISIONS.md` D29.** This finding originally
proposed pointing `EducationalOrganization.logo` at a file in `logo/`, on the
grounds that it would supply the missing reason to keep that directory published
and so answer Q17. **Eliot answered Q17 the other way** — `logo/` is repo
storage, not a published asset (D28) — so that reasoning is withdrawn.

The finding stands; only the target changes. Point `logo` at
**`android-chrome-512x512.png`**, at the site root: already published, already
named in `site.webmanifest`, and already what `index.html`'s complete node uses.
No new published URL is required, and `logo/` can be excluded without touching
any structured data.

**Recommendation.** Emit the full organisation node — `logo`, `description`,
`sameAs` — on the pages most likely to be the entity's home (`index.html`,
`about.html`, `tutoring.html`, `marking.html`, `contact.html`) rather than on all
354, where it would add ~300 bytes a page for no gain. Point `logo` at
`https://economicsacademy.co.uk/android-chrome-512x512.png`.

`sameAs` should list whatever profiles exist — the footer already links social
accounts, so the URLs are in the repo.

**Effort:** S · **Risk of acting:** Low · **Risk of not acting:** Low ·
**Dependencies:** answers Q17 / PH01-013 · **Status:** OPEN

---

## 3. Confirmed from an earlier phase by a second method

**PH06-030's one disagreeing breadcrumb is real.** P6 found it by comparing
extracted names; P4 found it by parsing the JSON-LD and decoding HTML entities in
the visible trail. Same single page, same defect:

```
revision-notes/macro-application/index.html
  json-ld : ['Home', 'Revision Notes', 'Macroeconomic Application']
  visible : [        'Revision Notes', 'Macroeconomic Application']
```

**440 of 441 agree.** No new finding; PH06-030 stands, now with two independent
measurements behind it.

---

## 4. What Phase 4 checked and found clean, so nobody re-audits it

- **All 921 JSON-LD blocks parse. Zero syntax errors.** Every block carries
  `@context: "https://schema.org"`.
- **The Quiz markup is fully compliant with Google's practice-problems
  requirements.** Across 166 `Quiz` nodes and **1,267** `Question` nodes:
  **0** missing `about`, `hasPart`, `eduQuestionType`, `text`, `acceptedAnswer`
  or `suggestedAnswer`. Each answer carries a `Comment` explanation. This is the
  one rich result the site is genuinely positioned to win and the markup is
  textbook. **Do not refactor it.**
- **Breadcrumb mechanics are perfect.** 460 `BreadcrumbList` nodes: **0** with a
  position sequence other than 1..n, **0** with an `item` URL that does not
  resolve to a real page.
- **0 placeholder values** — no `lorem`, `TODO`, `example.com` anywhere in any
  block.
- **0 non-ISO dates.**
- **0 disagreements between a page's JSON-LD `url`/`@id` and its own
  `rel=canonical`**, across every `LearningResource`, `Course`, `CollectionPage`,
  `WebPage`, `Quiz` and `FAQPage`. This is a meaningful result given the SEO
  pass's trailing-slash rewrite touched both.
- **`ListItem.item` absent on 376 of 1,871** is correct, not a gap: Google
  specifies that the final breadcrumb item omits `item`.
- **`Course` nodes carrying only `@type`/`name`/`provider` are correct.** All 179
  appear as `LearningResource.isPartOf` — a *reference* to a course, never the
  page's primary entity — so Google's Course rich-result requirements
  (`description`, `provider`) do not apply to them. An automated checker will flag
  these; it is wrong to.
- **`index.html`'s first block having no top-level `@context` is correct.** It is
  a JSON-LD **array** of two nodes, each carrying its own `@context`. Valid.
- **`CollegeOrUniversity` (2) is `alumniOf: University of Bath`** — correct usage,
  re-confirmed from Phase 0.

### Two false positives this phase generated, recorded so they are not "fixed"

Both were flagged by the audit's own first-pass checks and are **not defects**:

1. `Course.description` "missing" on 179 nodes — they are `isPartOf` references,
   see above.
2. `about.html`'s `image=…/images/eliot_shirt.JPG` "not resolving" — the file
   exists and is tracked; the checker's extension allow-list was lower-case only.
   Worth noting that this is the site's **one uppercase image extension**, which
   is the class of thing that works on macOS and fails on a case-sensitive host.
   P1 measured 0 case mismatches across every `src`/`href`; this reference is in
   **JSON-LD**, which P1's check did not cover, and it is correct.

---

## 5. Handed on

| Item | To | Why |
| --- | --- | --- |
| PH04-053's 12 hand-written pages | **P11 / D18 migration** | The visible trail is a repeated fragment; adding it by hand to 12 pages now means adding it twice. |
| PH04-055's `logo` property | **P11** | Points at the root `android-chrome-512x512.png`, not at `logo/`. Amended by D29 after Q17 was answered. |
| PH04-054's `inLanguage` | **D18 shell module** | A single value the shell should own. |

**Q11 is answered and moves to `DECISIONS.md`.** No new open questions are raised
by this phase.
