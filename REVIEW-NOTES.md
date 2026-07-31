# REVIEW-NOTES — notes consistency & enrichment pass

Running log for branch `notes-consistency-pass`. Things I found but did not fix,
plus the verification record. Updated as the pass proceeds.

Safety net: `backup-pre-enrichment` points at `main` as it was before any of this.

---

## Status

| Phase | State |
| --- | --- |
| Phase 0 — reconnaissance | Complete — `RECON.md` |
| Phase 1A — mechanical plan | Complete — `PLAN-mechanical.md`, approved |
| Phase 2 commits 1–5 — mechanical work | **Complete** |
| Phase 2 commits 6–7 — emphasis | **Complete** |
| Phase 1B — enrichment plans | **All 6 batches delivered and applied** |
| Phase 2 — enrichment | **Complete** — 31 components on 34 pages, `NEW-CONTENT-LOG.md` |
| Phase 3 — final verification | **Complete** — see "Phase 3" below |

---

## Economics content — flagged, not changed

Nothing in this section has been altered. Content errors are the author's call.

### New in this pass

**N1 — a leading space inside `\text{}` in two multiplier formulas.**
`aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html` and
`edexcel-theme-2/2-4-4-the-multiplier.html` both render

```
k = \frac{\text{Final Change in Real GDP/NI}} {\text{ Injection}}
```

The space inside `\text{ Injection}` puts a small gap at the start of the
denominator. I initially took this for Prettier reflow damage and removed it, then
reverted: Prettier only breaks lines at whitespace that is already there, so the
space was authored. Cosmetic, and yours to decide.

Related: the same formula labels the denominator "Injection" where the numerator is
a change in real GDP. Worth confirming the intended denominator is the *initial*
injection, since that is what the multiplier ratio needs.

**N2 — a sentence stops mid-clause. FIXED.**
`aqa-a2-micro/1-5-8-the-dynamics-of-competition-and-competitive-market-processes.html`,
in the "Short-Run and Long-Run Benefits of Competition" table:

> **Improved Choice:** competition can lead to a wider variety of products and

The cell ends there. Present on `main`, so not introduced by this pass, and the
Edexcel side has no equivalent page to borrow the ending from. Needs a few words
from you.

Also on that page: the short-run column has three rows and the long-run column two,
so the third row has a single cell rather than a pair. That is a markup asymmetry
rather than a wording problem, but the two columns no longer line up as a
comparison.

**N1–N3 were fixed by the author on 31 Jul 2026** (commit "N2 and N3", plus the
decision to leave the `\text{ Injection}` space as authored). Kept below for the
record.

**N3 — a concentration ratio described as both 3-firm and 5-firm. FIXED.**
`aqa-a2-micro/1-5-5-oligopoly.html`, "Concentration Ratios":

> "For example, a **3-firm concentration ratio of 80%** means that the top
> **five** firms account for 80% of total market sales."

One of the two numbers is wrong. This page's `spec-alert` requires students to
"calculate and interpret concentration ratios", so it is the sentence they will
read most closely. Found while preparing `PLAN-enrichment-aqa-micro.md`; the worked
example proposed there sits directly beneath this sentence, which would make the
inconsistency more conspicuous, so it is worth fixing first.

**N4 — 32 unescaped `<` characters in note body text. FIXED in this pass.**

Examples: `\( X < M \)` on `aqa-a2-macro/2-2-3` and `edexcel-theme-2/2-2-5`,
`(PED < 1)` on `aqa-a2-micro/1-3-2` and `edexcel-theme-3/3-3-1`, `0 < PES < 1` on
`aqa-a2-micro/1-3-4`, `\( MC < AVC \)` on `aqa-a2-micro/1-4-4`.

Every one is `<` followed by a space or a backslash, which the HTML5 parser
recovers as literal text — so all 32 render correctly and MathJax receives what it
expects. Invalid markup rather than a visible fault. The earlier audit escaped bare
`&` across 29 files but not `<`.

Escaped to `&lt;` at the author's request (commit "Escape bare < characters in note
text"). Markup-only: 0 visible text changes, 0 tag or link changes, and pixel-
identical rendering.

**N5 — the Edexcel twin carried the concentration-ratio error fixed on AQA. FIXED.**
`edexcel-theme-3/3-4-4-oligopoly.html`:

> "a **3-firm concentration ratio of 80%** means that the top **five** firms
> account for 80% of total market sales"

Corrected on `aqa-a2-micro/1-5-5` on 31 July but not on its Edexcel twin. Fixed
here on the author's explicit instruction — the **only** wording change made in this
entire pass, and a single word: "five" to "three". The sentence now matches the AQA
twin exactly. The held concentration-ratio component was then applied.

**N6 — a formula was removed with an Exam Preparation section. DECIDED: leave it out.**

`edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html` was the one
page of the 87 whose Exam Preparation section contained a `formula-box` as well as
checklist bullets. It held the **midpoint (arc) method** for percentage change:

```
%Δ = (New − Old) / ((New + Old)/2) × 100
```

Removing the section removed the formula, and it now appears **nowhere on the site**
— the AQA twin never carried it. I noted at reconnaissance that one section
contained a `formula-box`, and recorded it in the removal table, but did not follow
through on the fact that a *method* rather than a checklist item would go with it.
Found by the Phase 3 formula-integrity check.

**Decision: leave it out** (author, 31 Jul 2026). Edexcel mark schemes calculate
percentage change from the original value, not the midpoint, and the PED worked
example now on that page uses the original-value method. On that example's own
figures the two methods disagree — original-value gives PED −0.50, midpoint gives
−0.58 — so restoring the formula would put two conflicting answers on one page.
The page is now aligned with the exam board and the removed formula was the odd one
out.

No code change. Recorded here so a future session does not "restore" it as an
oversight: its absence is deliberate.

### Carried over from `docs/revision-notes-audit.md` — still open

Not duplicated here; see that document for the full write-up.

| # | Where | Summary |
| --- | --- | --- |
| **C1** | `edexcel-theme-1/1-2-4-supply.html` + AQA twin `aqa-a2-micro/1-3-3` | **STALE — not an open defect.** Checked directly against the file: the caption reads "point A to B … 'Extension in QS' due to a price rise" and "point B to A … 'Contraction in QS' due to a price fall", which is correct, and the bullets agree. It reads correctly on `main` too, so it was fixed after the audit was written. I carried it as open for several batches on the audit's word rather than checking; noting the error here. |
| **C4** | `aqa-a2-macro/2-2-3`, `aqa-a2-micro/1-5-6` | Both cross-reference Edexcel theme numbers that do not exist in the AQA specification the reader is following. |
| **C5** | `aqa-a2-macro/2-1-2` | Confirm the unemployment-rate denominator matches the ONS/ILO "economically active" definition given a few lines above. |
| **C6** | `aqa-a2-macro/2-1-2` | Real GDP growth stated as an identity; it is an approximation valid at low inflation. Standard at A-Level. |
| **W1** | `aqa-a2-macro/2-3-1`, `<h2>The Trade Cycle?</h2>` | Stray question mark on a heading that is not a question. A wording change, so out of scope here. |
| **F1–F4** | various | Four figure captions that contradict their own diagram. |

---

## What changed, commit by commit

### 1. Exam Preparation sections removed — 87 files

Every Edexcel topic page ended with `<section><h2>Exam Preparation</h2><div
class="exam-tip">…</div></section>` and nothing else in it. All 87 removed, wrapper
and contents. Two heading variants went with them: `Exam Preparation:` on
`edexcel-theme-1/1-2-8` and `Exam Focus` on `edexcel-theme-1/1-2-9`.

Removed text archived verbatim in
[`docs/removed-exam-preparation-sections.md`](docs/removed-exam-preparation-sections.md)
— kept out of this file to stop an 800-line appendix swamping it.

`edexcel-theme-1/1-1-5-specialisation-division-of-labour.html` needed special
handling: its CTA was nested *inside* the section rather than following it. The CTA
was preserved and re-parented, and all 87 CTA blocks then hashed byte-identical.

### 2. `formula-box` LaTeX protected — 24 files

`<!-- prettier-ignore -->` added to the 28 of 51 `formula-box` divs that lacked it.
8 display formulas that had been split across source lines were rejoined; the 4 that
sit inline in prose rather than in a guarded `formula-box` were left in Prettier's
preferred form.

> **Correction worth recording.** My first attempt at this also stripped the space
> after `\text{`, on the assumption that no legitimate LaTeX needs one. That was
> wrong, and it broke the oligopoly concentration-ratio formula on
> `aqa-a2-micro/1-5-5` and `edexcel-theme-3/3-4-4`: `\text{ firms}` became
> `\text{firms}`, rendering "top *n*firms". Caught by the formula-equivalence check,
> reverted, and the commit rebuilt. All 176 files now render every formula exactly
> as `main` does.

### 3. `.notes-cta` extracted — 89 files + 1 stylesheet

The inline-styled CTA block, duplicated across 87 Edexcel pages and both diagram
galleries, replaced by a `.notes-cta` class. ~350 inline style declarations removed,
addressing part of audit flag S5. No copy or link changes; the galleries keep their
board-neutral `/past-papers/index.html`.

### 4. AQA conversion CTA added — 79 files

Closes audit flag S1. Every AQA topic page now ends with the same `.notes-cta` block
as its Edexcel counterpart, pointing at `/past-papers/aqa/index.html`. All 166 topic
pages now carry exactly one CTA.

### 5. Dead `chart-container` wrappers removed — 94 files

Closes part of audit flag S6. 211 wrappers with no CSS rule anywhere, each wrapping
exactly one `<figure class="diagram-figure">`. Prettier reflowed 63 files afterwards
because attributes that had been split now fit on one line.

### 6–7. Emphasis on under-emphasised pages — 16 files

25 pages were flagged as under-emphasised by combined
(`<strong>` + `key-definition`) density. **16 needed work; 9 did not** and were
left alone. The metric over-flags pages whose content sits in long explanatory
text after an already-bolded lead-in, or inside a correctly-emphasised table — this
was anticipated in `PLAN-mechanical.md`, though the estimate there was 15–20 of 25
and the AQA half came in lower.

Three patterns applied, each with an existing on-site precedent:

| Pattern | Precedent | Where used |
| --- | --- | --- |
| Bold every `concept-table` row label | 76 of 91 tables already do | `1-8-7` (11 rows) |
| Bold the operative opening phrase of a bullet | `1-2-9`, `1-3-5` — "**Consumer price rises** from P1 to P2" | `2-6-1`, `4-1-1`, `1-5-7`, `1-8-8`, `1-2-10` |
| Bold direction of change and outcome in prose | `1-2-6`, `1-3-5` | `2-2-2`, `2-2-5`, `4-4-1`, `4-4-3`, `4-3-2`, `4-3-3`, `3-4-4`, `1-3-6`, `1-1-1` |

**AQA (6 changed, 7 left):** `1-8-7`, `2-6-1`, `1-8-8`, `1-5-7`, `1-3-6`, `1-2-3`.
Left alone: `1-6-4`, `1-5-8`, `2-1-2`, `1-7-3`, `1-4-8`, `1-4-5`, `1-8-6`.

**Edexcel (10 changed, 2 left):** `2-2-2`, `4-1-1`, `2-2-5`, `4-4-1`, `4-4-3`,
`4-3-2`, `4-3-3`, `3-4-4`, `1-1-1`, `1-2-10`. Left alone: `4-5-4`, `3-3-3`.

`2-2-2-consumption` was the weakest page on the site (1.35) and is now 8.41, above
the 6.12 median. `4-1-1-globalisation` and its AQA twin `2-6-1` carry the same 18
bullets word for word and now bold the same 35 phrases, so the twins match.

Deliberately **not** emphasised:

- Two tables on `1-8-8` keep an unbolded first column — both are parallel-content
  columns (Arguments for / Arguments against), not row labels, the same shape as
  the Debt vs Equity table on exemplar `2-4-1`.
- The three ILO survey questions on `2-1-2` — verbatim questions with no anchor.
- 2–6 word enumerations on `1-8-7` ("Lower prices", "Abuse of monopoly power") —
  bolding a whole short item is the same as bolding nothing.
- Illustrative examples on `1-8-8` ("The 2008 financial crisis…") — examples, not
  concepts.
- The rationality-assumption list on `1-2-3` — its terms are already carried by
  `key-definition` chips.

---

## Verification so far

Three stdlib-only validators were written for this pass, since the site has no build,
lint or test step:

- `scripts/verify_html.py` — strict well-formedness and duplicate-id check
- `scripts/verify_text_integrity.py` — extracts visible text at two commits and diffs
- `scripts/verify_links.py` — resolves every internal href and fragment against disk

### Results at commit 7

| Check | Result |
| --- | --- |
| HTML well-formedness | **176/176 files parse, 0 errors** |
| Internal links and fragments | **3,863 refs, 0 broken hrefs, 0 broken fragments** |
| Display-formula rendering vs `main` | **0 of 176 files changed** (whitespace-collapsed comparison of every `\[…\]`) |
| Prettier 3.9.6 | Clean on every file touched. 2 files still fail — `revision-notes/index.html` and `macro-application/index.html` — both **pre-existing on `main`** and both untouched here. |
| Emphasis tags | `<b>`, `<i>`, `<u>`, `<mark>`: still **0 uses**, as before |
| CTA uniformity | 87 Edexcel blocks identical; 2 gallery blocks identical; 166/166 topic pages carry exactly one |

### Text integrity, commit by commit

Only the two commits that are *meant* to change wording do so:

| Commit | Files whose visible text differs |
| --- | ---: |
| Exam Prep removal — change expected | 87 |
| `formula-box` protection | **0** |
| `.notes-cta` extraction | **0** |
| AQA CTA — change expected | 79 |
| `chart-container` removal | **0** |
| Emphasis, AQA | **0** |
| Emphasis, Edexcel | **0** |

### Visual regression

Headless Chrome, pixel comparison against the immediately preceding commit:

- `.notes-cta` extraction — **identical** at 1440/768/480px on
  `edexcel-theme-1/1-1-1`, `edexcel-theme-3/3-1-3`, `edexcel-theme-4/4-2-1`
- `chart-container` removal — **identical** at 1440/480px on
  `edexcel-theme-1/1-1-4`, `aqa-a2-micro/1-5-11`, `aqa-a2-micro/1-8-4`

Pages carrying MathJax were avoided for pixel work: inline MathJax renders
non-deterministically between runs, so formula bands are noise rather than signal.

---

## Notes for later

- **`.coming-soon` is dead CSS** — rules exist, no markup uses it. Four lines,
  unrelated to this pass; left alone.
- **`css/pages/revision-notes-textbook.css` fails Prettier on `main`**, at a long
  `linear-gradient` in the `.coming-soon` block (line ~830). Pre-existing and not
  introduced here. `docs/revision-notes-audit.md` records only a `macro-application.css`
  nit, so this one appears to have been missed.
- **Remaining inline styles** — audit flag S5 is now partly closed. Roughly 279
  `style` attributes remain, mostly table column widths.

---

## Regression caught and fixed during batch 1

The emphasis commits (6–7) **destroyed two internal links**, and the verification
in place at the time did not notice.

The scripts that rebuilt emphasised paragraphs worked from the element's flattened
text, and guarded against damaging links by skipping any element containing
`<a `— with a trailing space. Prettier wraps long tags, so a link written as
`<a\n  href="…"` does not contain that string, slipped past the guard, and was
stripped when the paragraph was rebuilt.

Two contextual links added by the earlier SEO audit were lost:

| File | Lost link |
| --- | --- |
| `edexcel-theme-1/1-2-10-alternative-views-of-consumer-behaviour.html` | → `edexcel-theme-4/4-1-6-restrictions-on-free-trade.html` |
| `edexcel-theme-2/2-2-5-net-trade.html` | → `edexcel-theme-4/4-1-6-restrictions-on-free-trade.html` |

Both are restored. `2-2-5` keeps all four of its emphasis marks, none of which
overlaps the anchor. The `1-2-10` bullet gives its emphasis up, because the phrase
that had been bolded spanned the link.

**Why nothing caught it.** `verify_text_integrity.py` compares visible text, and
stripping a tag changes no text at all — so a link can vanish with the check still
reporting a clean run. `verify_links.py` only resolves the links that are present;
it cannot know one used to exist. `scripts/verify_markup_integrity.py` was written
to close the gap: it compares tag counts and link targets between two commits, and
run against the emphasis commits it reports exactly those four problems. It now
reports 0 for the whole branch.

### Separately: 13 links removed with the Exam Preparation sections

Not a defect — a consequence of commit 1, which was approved. The earlier audit
placed 13 of its 156 contextual note-to-note links inside the checklists that this
pass deletes, across 11 pages. Checked afterwards: **every affected target still
has at least 2 inbound links and nothing is orphaned** (range 2–9). Worth knowing
if inbound-link counts are ever audited again.

---

# Phase 3 — final verification

Run across the whole branch after the last enrichment commit.

## Results

| Check | Result |
| --- | --- |
| HTML well-formedness | **176/176 parse, 0 errors** |
| Internal links and anchors | **3,863 refs, 0 broken hrefs, 0 broken fragments** |
| Markup integrity since the Exam Prep removal | **0 losses**, 79 additions |
| Markup integrity vs `main` | 23 losses — all the approved Exam-Prep link removals, verified to orphan nothing |
| Display formulas vs `main` | **1 lost** — see flag N6 |
| Prettier 3.9.6 | Clean on every file touched |
| Rendering | Components verified in headless Chrome: MathJax fractions, `calculation-table` styling and the EXAM TIP pill all render correctly, in the intended position |

## Text integrity — the commits that must not change wording

| Commit | Files whose visible text differs |
| --- | ---: |
| `formula-box` protection | **0** |
| `.notes-cta` extraction | **0** |
| `chart-container` removal | **0** |
| Emphasis, both boards | **0** |
| Escaping reflow | **0** |

The only commits that changed visible text are the ones intended to: the Exam
Preparation removal (87 files), the AQA CTA addition (79), the enrichment commits,
and the single authorised one-word fix on `3-4-4-oligopoly`.

## Outcome against the brief

| | |
| --- | ---: |
| Exam Preparation sections remaining | **0** (was 87) |
| Topic pages carrying exactly one `.notes-cta` | **166 / 166** |
| Inline-styled CTA blocks remaining | **0** (was 89) |
| Dead `chart-container` wrappers remaining | **0** (was 211) |
| `formula-box` divs without `prettier-ignore` | **0** (was 28) |
| Unescaped `<` in note text | **0** (was 32) |
| `<b>` / `<i>` / `<u>` in notes | **0** (unchanged) |
| Worked examples added | 32 total on the site |
| Exam tips added | 14 total on the site |
| **Pages carrying a component** | **34 of 166 (20%)** |
| **Pages receiving nothing** | **132 of 166 (80%)** |

184 files changed against `main`.

## Prettier — the two persistent failures

`revision-notes/index.html` and `revision-notes/macro-application/index.html` still
fail `prettier --check`. Both fail on `main` too and neither was touched by this
pass. `css/pages/revision-notes-textbook.css` also fails on `main`, at a long
`linear-gradient` in the dead `.coming-soon` block — the `.notes-cta` rules added
here are clean.

## Known scope decisions worth remembering

- **Duplication was approved.** The current account worked example appears on three
  pages (`aqa-a2-macro/2-6-3`, `edexcel-theme-2/2-1-4`, `edexcel-theme-4/4-1-7`)
  because Edexcel covers the balance of payments in two themes. Several other
  components appear on two pages, one per board. Each duplicate is hash-verified
  identical to its source, so they can be updated together.
- **One wording change was made**, on explicit authorisation: "five" to "three" on
  `edexcel-theme-3/3-4-4-oligopoly.html`. Nothing else in 166 pages had a word
  altered.

---

# Site-wide scan and fixes — 31 Jul 2026

Found while scanning the whole site to write `CLAUDE.md`, then worked through on
the author's instruction. The enrichment pass covered only the 166 topic pages;
this scan covered the commercial pages, past-paper pages, hubs, CSS and JS too,
which is where nearly all of it sat.

Numbering matches the list the author triaged. **12 of 15 fixed, 3 left.**

| # | Finding | Outcome |
| ---: | --- | --- |
| 1 | 3 dead Edexcel B mark-scheme links | **Left** — author fixing |
| 2 | 55 keyboard-inaccessible accordions | **Fixed** |
| 3 | `privacy.html` had no `<h1>` | **Fixed** |
| 4 | `macro-application` had no `<h1>`, canonical or OG | **Fixed** |
| 5 | Heading-level skips on 12 pages | **Fixed** |
| 6 | Dead `carousel.js` + its CSS | **Removed** |
| 7 | No `.gitignore`; 11 junk files tracked | **Fixed** |
| 8 | `lang="en"` on 22 pages | **Fixed** — all now `en-GB` |
| 9 | `.notes-container` defined in two stylesheets | **Left** |
| 10 | 3 relative asset paths | **Fixed** |
| 11 | `confirmation.html` had no description or canonical | **Partly** — see below |
| 12 | Stale `codex-promts/`, empty `raw-notes/aqa/` | **Deleted** |
| 13 | Filename outliers (`eliot_shirt.JPG` etc.) | **Left** |
| 14 | 284 `target="_blank"` without `rel` | **Fixed** |
| 15 | Dead `.coming-soon` CSS | **Removed** |

## The two that need explaining

**#11 — the canonical was deliberately not added.** `confirmation.html` already
carries `<meta name="robots" content="noindex, nofollow">`, which the original
finding missed. A canonical on a `noindex` page is a mixed signal — it asks
search engines to consolidate a page they have been told to ignore — so only the
meta description was added, which costs nothing and is ready if the `noindex` is
ever lifted. Add the canonical only if that tag goes.

**#2 — the two past-paper toggle implementations were kept separate.**
`past-papers/aqa/index.html` uses a different `toggleYear` from the other three
boards: it toggles `.collapsed`/`.expanded` and lets CSS animate, while
`edexcel`, `edexcel-b` and `ocr` drive `max-height` from JS with a 300 ms
`setTimeout`. Unifying them would have changed how the AQA page animates, so
both were left as they were and only the accessibility wiring was added. Worth
unifying deliberately at some point; it is a behaviour change, not a refactor.

## What #2 actually changed

Every `<li class="topic-item" onclick=…>` and `<li class="year-item" onclick=…>`
became:

```html
<li class="topic-item">
  <div class="topic-header">
    <h2>
      <button type="button" class="topic-toggle"
              aria-expanded="false" aria-controls="subtopic-1">
        1.1 Nature of Economics
      </button>
    </h2>
    <span class="toggle-icon" aria-hidden="true">+</span>
  </div>
```

The heading text moved inside a `<button>`, so it is focusable and announces its
state. The card keeps its click-anywhere behaviour through a delegated listener;
clicks originating on the button call `stopPropagation` so one tap cannot toggle
twice. There are now **no `onclick` attributes anywhere in the repo**.

Behaviour was checked in a browser, not just by eye: a temporary harness drove
the first accordion through open/close by button, open by card body, and a
repeat button press, asserting `display`, `aria-expanded` and the `+`/`-` glyph
at each step. 11/11 passed. The harness was deleted afterwards.

## Regressions caught during verification

Four changes looked correct and were not. Each was caught by comparing
screenshots against `main`, and each is a cascade rule that a reading of the
markup would not have surfaced. Recorded because they are all traps for the
next person touching this CSS.

| What broke | Cause |
| --- | --- |
| Accordion headings rendered near-white | `css/main.css:1756` styles **every bare `<button>`** as a pink CTA with `color: #fff !important`. A plain reset loses to it; the override has to be `!important` too. |
| `privacy.html` title gained a white box | `header.major h2` sets `background: #fff`, but `#main .major h2` (line 2448) overrides it to `#f7f7f7` for anything inside `#main`. Only the second value was ever visible. |
| `macro-application` title dropped ~20px | `header.major h2` also applies `position: relative; top: -0.65em`. Promoting the title to `h1` silently dropped the lift. |
| Every retagged heading was too large below 736px | `css/main.css:2909` sets `h2–h6` to `1.25em` at `max-width: 736px`. Unconditional compensation rules overrode it. Note this rule does **not** cover `h1`. |

## Verification

Against `main`, on a pristine worktree served side by side with the working copy.

| Check | Result |
| --- | --- |
| `scripts/verify_html.py .` | **192/192 parse, 0 errors** |
| `scripts/verify_links.py .` | 4,421 internal refs, **3 broken — all finding #1**, which was left |
| Visible text vs `main` | **0 pages changed** |
| `<a>` links vs `main` | **0 lost, 0 gained** |
| `<img>` sources vs `main` | 3 changed — exactly the intended relative→absolute fixes |
| `aria-controls` targets | 85 references, **0 unresolved** |
| Heading structure | **0 pages** with a missing/duplicate `h1` or a skipped level (was 19) |
| Pixel comparison at 480 / 760 / 1024 / 1440px | **Identical** on every changed page |

Two pages cannot be pixel-compared and were excluded by proof, not assumption:
`confirmation.html` builds its reference number from `Date.now()` and
`Math.random()`, and `tutoring.html` embeds a Calendly widget whose loading
spinner depends on real network timing. Both were shown non-deterministic by
re-rendering the *same* version repeatedly and getting different bytes.

`verify_links.py` also reports `templates/header.html:2 -> #main` as a broken
fragment. That is a **false positive**: the template is injected into a host page
that does have `#main`, and the script resolves fragments against the file it
found them in.

## Still open after this work

- **#1, #9, #13** as triaged above.
- **`css/main.css` fails `prettier --check`** at line 2407, a `box-shadow` list.
  Pre-existing on `main` and untouched here.
  `css/pages/revision-notes-textbook.css` **now passes** — its long-standing
  failure was the `linear-gradient` inside the dead `.coming-soon` block removed
  as #15.
- **`.year-header h4` in `css/pages/past-papers-list.css` is a dead selector** —
  that markup has always used `h2`. Noticed while fixing #2; left alone.
- **`404.html`** has no canonical and no Open Graph tags. Defensible for a 404,
  listed so it is a decision rather than an oversight.
