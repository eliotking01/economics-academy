# Revision notes: keyword and metadata brief

21 August 2026. The targeting rules for the 166 generated topic pages under
`revision-notes/` (87 Edexcel, 79 AQA), the two diagram gallery pages and the
seven hub pages. Written to be applied mechanically:
if a rule here is ambiguous on a given page, stop and log it rather than
guessing.

Companion documents:

- `seo/16-url-structure-and-redirect-options.md` — why the URLs are frozen and
  what it would take to change them.
- `seo/15-notes-seo-manual-todo-2026-08-21.md` — the tasks only Eliot can do.

---

## 1. What students actually search

From the site's own Search Console export, `seo/gsc-exports/21-08-2026/performance-28d-compare/Queries.csv`
— 1,508 queries, 5,563 impressions, 28 days to 21 August 2026. Percentages are
share of impressions.

| Pattern in the query | Queries | Impressions | Share |
| --- | --- | --- | --- |
| contains "a level" / "a-level" / "alevel" | 354 | 2,289 | **41.1%** |
| contains "past paper" | 243 | 981 | 17.6% |
| contains "edexcel" | 188 | 947 | 17.0% |
| contains "diagram" or "graph" | 163 | 512 | **9.2%** |
| contains "revision" | 49 | 518 | 9.3% |
| contains "definition" / "meaning" / "what is" / "define" | 177 | 354 | 6.4% |
| contains "aqa" | 133 | 341 | 6.1% |
| contains "notes" | 67 | 311 | 5.6% |
| contains "tutor" or "tuition" | 25 | 277 | 5.0% |
| contains "ocr" | 57 | 261 | 4.7% |
| contains "theme" | 33 | 92 | 1.7% |
| **contains a spec code (1.2.1, 4.1.3.2 …)** | **9** | **4** | **0.1%** |

Query length, weighted by impressions: 2 words 21.4%, 3 words 20.2%,
4 words 20.5%, 5 words 13.6%, 6 words 12.7%. **62% of impressions come from
two-to-four-word queries.**

Bare topic-name searches with no board and no "a level" qualifier are a real
and separate demand pool. Examples currently earning impressions:
`microeconomics diagrams` (102), `government expenditure` (47),
`price elasticity of supply` (45), `division of labour` (30),
`types of market failure` (30), `specialisation definition economics` (29),
`government failure definition` (23), `macroeconomics diagram` (21).

### How much to trust this data

**Not as much as its precision suggests.** Two problems, one bounded and one
not:

**Self-traffic.** Some of these impressions are Eliot or an AI assistant
searching Google while working on the site, not students. Search Console has no
way to exclude them. The damage is measurable:

- Brand queries ("economics academy" and variants) are **148 of 5,563
  impressions — 2.7%** — but **29 of 57 clicks**. Clicks and CTR from this
  export are effectively unusable. Impressions are broadly usable.
- Re-running the pattern analysis over the subset least likely to be
  self-traffic — non-brand queries, zero clicks, average position worse than 10,
  which is 670 queries and 3,143 impressions, 58% of non-brand impressions —
  gives this:

| Pattern | All queries | Non-brand | Least-contaminated subset |
| --- | --- | --- | --- |
| "a level" | 41.1% | 42.3% | **36.0%** |
| past paper | 17.6% | 18.1% | 21.7% |
| diagram / graph | 9.2% | 9.5% | **7.3%** |
| definition-type | 6.4% | 6.5% | **7.2%** |
| revision | 9.3% | 9.6% | 4.0% |
| notes | 5.6% | 5.7% | 2.9% |
| edexcel | 17.0% | 17.5% | **8.3%** |
| aqa | 6.1% | 6.3% | **10.4%** |
| tutor / tuition | 5.0% | 5.1% | 8.5% |
| **spec code** | **0.1%** | **0.1%** | **0.1%** |

What survives the strictest filter: the spec-code figure is unchanged at 0.1%;
"a level" is still the dominant qualifier; the definition cluster actually grows;
the diagram cluster stays substantial.

What does not survive, and must not be used: **all click and CTR figures**; the
Edexcel-over-AQA weighting, which reverses under the filter and probably
reflects where the site's own development work has been focused; and the
"notes" and "revision" shares, which roughly halve.

**Seasonality.** This window is the 28 days to 21 August 2026 — results day and
the dead middle of the summer holiday. Student search behaviour in October or
in the fortnight before a May exam will not look like this. Nothing here should
be treated as a stable share.

**So: this data corroborates, it does not decide.** The title formula in §4
rests primarily on the competitor SERP evidence in §2 — what actually ranks —
and on general search behaviour. The Search Console figures are used to confirm
that nothing about this site's audience contradicts it, and to kill the one
assumption that would otherwise be tempting (that spec codes are worth title
space). A term-time re-export, task 2 of the manual to-do list, is what turns
this from directional into reliable. *Parked 22 August 2026: the notes were not
complete until after the 2026 summer exams, so no clean term-time window exists
yet — the first is the autumn term 2026.*

### The three conclusions that matter

All three hold on the least-contaminated subset, not just the headline figures.

1. **The topic name is the query.** Not the board, not the code. The topic name
   must lead the title.
2. **Spec codes have almost no search demand** — 4 impressions in 28 days,
   and 0.1% under every filter. If anything this is an over-count, since a
   developer searching a spec code while working on the site would land in it.
   Every character a code occupies at the front of a title is wasted.
3. **Diagrams are a demand pool the site is under-serving.** 7.3–9.2% of
   impressions are diagram or graph queries depending on the filter, and 72 of the 166 topic pages
   carry no image or inline SVG at all, while `images/diagrams/svg/` holds 84
   diagrams.

---

## 2. What the competition does

Verified 21 August 2026 by reading the live `<title>` tags, not Google's
rewrites. Full evidence in the audit report; the pattern is the point here.

| Site | Title formula | Topic position | Spec code | Board |
| --- | --- | --- | --- | --- |
| Save My Exams | `Aggregate demand - A Level Economics Revision Notes` | **first** | never | inconsistent |
| Save My Exams (legacy) | `Supply \| Edexcel A Level Economics A Revision Notes 2015` | **first** | never | yes |
| TutorChase | `1.3.2 Externalities and Welfare Effects \| Edexcel A-Level Economics Notes \| TutorChase` | second (Edexcel) | leading | yes |
| TutorChase | `Externalities in Consumption (8.5.2) \| AQA A-Level Economics Notes \| TutorChase` | **first** (AQA/CIE) | bracketed, after | yes |
| tutor2u | `3.4.5 Monopoly (Edexcel) \| Reference Library \| Economics \| tutor2u` | second | leading | bracketed |
| Study Mind | `Price Elasticity of Demand - A-Level Economics - Study Mind` | **first** | never | never |
| Seneca | `Externalities \| Free Notes & Practice – Economics: Edexcel A A Level` | **first** | never | last |
| Economics Help | `Government Failure - Economics Help` | **first** | never | never |
| PMT | no HTML topic pages — PDFs only | — | — | — |

Six of the seven put the topic name first. The two that don't (tutor2u,
TutorChase's Edexcel set) are the two that treat spec codes as a product
feature for teachers, and both also run parallel code-free pages.

Observed on live SERPs for unqualified student queries — "aggregate demand a
level economics", "externalities notes a level", "government failure economics
a level", "monopoly a level economics revision notes", "division of labour a
level economics", "elasticity of supply a level":

- Board-specific pages win unqualified queries. There is no evidence Google
  prefers a board-agnostic page when the student doesn't name a board.
- Save My Exams routinely ranks its AQA **and** Edexcel pages on the same
  page-one SERP for the same topic. Splitting by board is not
  self-cannibalising for them.
- Google reads the board from the URL path and page context, not only the
  title: for "aqa economics notes monopoly" the #1 result is an SME AQA page
  whose title contains no board name at all.

Caveat: those SERPs were sampled from a US IP. Task 1 of the manual to-do list
is to re-check a handful from a UK IP before treating them as settled.

**UK check, 22 August 2026 — Eliot, UK IP, incognito.** Across the six queries
in task 1 the top results are dominated by three sites: Economics Help, tutor2u
and Save My Exams. Of the three, only tutor2u puts the unit code in its titles;
Economics Help and Save My Exams lead with the topic name and carry no code.
That is the same pattern the US sample found, so the formula in §4 stands:
topic name first, no code in the title.

---

## 3. The current state of the site

Measured across the 166 topic pages on 21 August 2026.

| Field | State |
| --- | --- |
| Title formula | 100% `{Board} A-Level Economics {code} {Topic}` — topic name **last** |
| Title length | min 33, median 51, max 64 chars; 4 pages over 60 |
| Spec code in title | 162 of 166 |
| Duplicate titles | none |
| Description length | min 151, median 156, max 170; 2 over 160 |
| Duplicate descriptions | none |
| H1 | Edexcel (87): bare topic name. AQA (79): **code-prefixed** (`2.6.5 Economic Growth and Development`) — two conventions in one folder |
| Words in `<main>` | min 300, median 741, mean 859, max 2,547; **17 pages under 500** |
| Pages with no image or SVG in `<main>` | **72 of 166** |
| `BreadcrumbList` schema | present |
| `LearningResource` schema | present, but **no `datePublished`, no `dateModified`, no author** |
| `og:image` | site logo, 1200×1200, declared with `summary_large_image` (wants 2:1) |

The metadata is clean and consistent. It is consistently pointed the wrong way.

---

## 4. The title formula

Apply the first variant that fits within **60 characters**. Measure the
rendered string, not the template.

**Edexcel topic pages** (`revision-notes/edexcel-theme-*`)

> **Amended 22 August 2026, by Eliot.** Variants 1 and 2 are retired: no
> Edexcel title carries a spec code either, on the same evidence that settled
> AQA — 0.1% of impressions under every filter. Measured before deciding:
> dropping the codes let 23 of the 87 titles newly fit "Revision Notes" and
> lost it on none. The code stays in the description (§5 below, unchanged)
> and in the on-page sub-label. The one collision this created — Edexcel
> carries "Balance of Payments" twice — is resolved with "(Theme 2)" /
> "(Theme 4)" labels in those two titles. `verify_seo.py` assertion 15 now
> rejects a spec code in any title, either board. DECISIONS.md D54.

1. ~~`{Topic} ({code}) – Edexcel A-Level Economics Revision Notes`~~
2. ~~`{Topic} ({code}) – Edexcel A-Level Economics Notes`~~
3. `{Topic} – Edexcel A-Level Economics Revision Notes`
4. `{Topic} – Edexcel A-Level Economics Notes`
5. `{Topic} – Edexcel A-Level Economics`

**AQA topic pages** (`revision-notes/aqa-a2-*`) — **no spec code in the title.**
The AQA codes on this site are site-local `1.x.y` / `2.x.y`, deliberately not
the real 7136 codes. Printing them in a title cannot match a search and can
mislead an AQA student who compares them against their own spec.

1. `{Topic} – AQA A-Level Economics Revision Notes`
2. `{Topic} – AQA A-Level Economics Notes`
3. `{Topic} – AQA A-Level Economics`

**Rules**

- `{Topic}` is the page's existing H1 topic name, with the AQA code prefix
  stripped where present. Do not invent a new name for a topic. If the real
  name is too long for variant 5, stop and add the page to the approval list
  with a proposed shorter display name — do not truncate silently.
- Separator is an en dash with spaces (` – `). Consistent, and reads better
  than a pipe when the topic name already contains punctuation.
- Board string is `Edexcel` and `AQA`. Not "Edexcel A", not "Edexcel
  Economics A" — students search the short form.
- Never exceed 65 characters, even at variant 5.
- Titles must stay unique across all 166 pages. Two topics sharing a display
  name on the same board is a collision: log it, don't disambiguate by
  reinstating the code.
- `og:title` and `twitter:title` mirror `<title>` exactly.

**Worked examples**

| Page | Now | Becomes |
| --- | --- | --- |
| `edexcel-theme-1/1-2-2-demand.html` | `Edexcel A-Level Economics 1.2.2 Demand` | `Demand (1.2.2) – Edexcel A-Level Economics Revision Notes` |
| `edexcel-theme-1/1-2-1-rational-decision-making.html` | `Edexcel A-Level Economics 1.2.1 Rational Decision Making` | `Rational Decision Making (1.2.1) – Edexcel A-Level Economics` |
| `aqa-a2-macro/2-3-3-inflation-and-deflation.html` | `AQA A-Level Economics 2.3.3 Inflation and Deflation` | `Inflation and Deflation – AQA A-Level Economics Revision Notes` |
| `aqa-a2-macro/2-3-4-possible-conflicts-between-macroeconomic-policy-objectives.html` | `AQA A-Level Economics 2.3.4 Macroeconomic Policy Conflicts` | `Macroeconomic Policy Conflicts – AQA A-Level Economics Notes` |

Check each rendered length against the 60/65 rule rather than trusting these
examples.

---

## 5. The meta description formula

Target **145–158 characters**. Front-load. Every description must be specific
to its page and must not claim a feature the page does not have.

```
{Topic} for {Board} A-Level Economics{ (code) for Edexcel}. Covers {two or three
sub-concepts taken from this page's own H2 headings}{, with a diagram | with key
definitions | with evaluation points} for the exam.
```

- Sub-concepts come from the page's existing H2s or `key-definition` chips.
  Never from memory of what the topic "should" cover.
- Only write "with a diagram" if the page actually contains an image or inline
  SVG. Only write "with key definitions" if it has `key-definition` chips.
- The Edexcel code goes in the description even when it fits the title, and
  **always** for AQA pages it does not — for AQA, name the module instead
  ("AQA A-Level Economics macro") rather than a site-local code.
- Include one word from the definition cluster ("what X means", "definition")
  on pages whose topic attracts definition searches — 6.4% of impressions, and
  the one pattern that grows rather than shrinks when self-traffic is filtered
  out.
- `og:description` and `twitter:description` mirror the meta description.

---

## 6. H1 and heading structure

- **H1 is the bare topic name on both boards.** This is a change for the 79
  AQA pages that currently prefix the code, bringing them in line with the 87
  Edexcel pages. It is a visible-text change, so it goes on the approval list
  before it is applied.
- The spec code stays visible, in a sub-label line beneath the H1 — markup,
  not prose: board · module · code. That keeps the code for a student
  confirming they are on the right page, without spending title or H1 weight
  on it.
- Every H2 gets a stable `id` so it can be linked and cited.
- Do not rewrite H2 wording. Where an H2's phrasing is costing a likely search
  (a section on the definition of a term not using the word "definition", for
  instance), propose the rewrite on the approval list with the query evidence.

---

## 7. Structured data

Keep the existing `LearningResource` and `BreadcrumbList`. Add to
`LearningResource`:

- `datePublished` and `dateModified` — from git history for the page's source
  slice, not invented.
- `author` and `publisher` — the `#organization` node already referenced.
  A named `Person` author with credentials is a real ranking and trust signal
  and every competitor that outranks this site has one; it needs Eliot's own
  wording, so it is on the manual to-do list, not applied here.
- `audience` as `EducationalAudience` with `educationalRole: student`.
- `educationalLevel` — already present, keep.
- `about` — the topic as a `DefinedTerm` or `Thing` with the topic name.
- `educationalAlignment` — `alignmentType: educationalSubject`,
  `targetName` the board and spec reference.
- `timeRequired` where a sensible reading time can be computed from word count.

**Do not add:**

- `FAQPage`. Google stopped showing FAQ rich results on **7 May 2026** and is
  removing the search appearance, the rich result report and Rich Results Test
  support in June 2026. The markup is harmless but earns nothing.
- `HowTo`. Deprecated on mobile in August 2023.
- Practice-problem / `Quiz` markup. Google announced its deprecation in
  November 2025 and has removed the help documentation.

---

## 8. Internal linking

- Every topic page links to its **twin on the other board** where one exists.
  Derive twins from `seo/07a-topic-map.csv` and topic identity, never from the
  bare spec code — `verify_seo.py` assertion 13 exists because 37 codes
  collide across the two boards (1.1.1 is "Economics as a Social Science" on
  Edexcel and "Economic Methodology" on AQA).
- Related-topic links within the board, drawn from the topic map, with the
  topic name as anchor text.
- The existing previous/next chain, hub link, and resource links to practice
  questions, flashcards and past-paper questions stay as they are.
- No page should be more than two clicks from its hub on the rendered graph —
  `verify_seo.py` assertions 11 and 12 already enforce a version of this;
  extend rather than duplicate.

---

## 9. Priority order

If time is short, this is the order of expected return:

1. Titles — 166 pages, all currently pointing the wrong way.
2. Meta descriptions — rebuilt to the new formula.
3. `dateModified` plus a visible last-updated line.
4. Twin-board and related-topic links.
5. Diagram coverage on the 72 pages that have none (needs approval).
6. The 17 pages under 500 words (needs approval).
7. Author byline and credentials (needs Eliot).
