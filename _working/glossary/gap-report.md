# Glossary gap report

For your manual review. **Nothing in here has been acted on**, and no revision
notes page has been edited — every item is something for you to decide or write.

Three companion files:

| File | What it holds |
| --- | --- |
| `inventory.md` | All 255 extracted terms and 49 formulae, with sources |
| `review-decisions.md` | Questions the extractor refused to answer — tables, formulae, ambiguous chips |
| `spec-checklist.md` | Per-board specification coverage, term by term |

This file is the summary and the judgement calls. It answers the brief's three
questions: (a) required by a spec but missing from the notes, (b) defined
inconsistently, (c) ambiguous or borderline.

---

## The shape of it

| | Edexcel A | AQA | Both |
| --- | ---: | ---: | ---: |
| Topic pages scanned | 87 | 79 | 166 |
| Definitions extracted | 245 | 231 | 476 |
| Unique terms | — | — | **255** |
| Terms on both boards | — | — | 157 |
| Display formulae | — | — | 49 |
| Spec terms checked | 135 | 135 | — |
| …defined | 60 | 64 | — |
| …in the notes but undefined | 70 | 64 | — |
| …absent from the notes | 5 | 7 | — |

The headline: **coverage is good and the notes agree with themselves.** Of 157
terms defined on both boards, the wording is byte-identical on most. The work
below is mostly about promoting concepts the notes already teach into defined
terms — not about writing new economics.

---

## (a) Required by a specification, missing from the notes

### A1. Absent entirely — 10 distinct concepts

The phrase appears nowhere in that board's notes. Each needs content written, or
a decision that it is out of scope.

| Concept | Edexcel A | AQA | Note |
| --- | --- | --- | --- |
| **hysteresis** | absent | absent | Named by both specs, in neither set of notes. The clearest single gap on the site |
| **terms of trade** | defined | **absent** | The Edexcel notes have a whole page (4.1.4). AQA macro has `2-6-2-trade.html` but never mentions the terms of trade |
| **cost–benefit analysis** | in notes | **absent** | One Edexcel page mentions it; no AQA page does |
| **creative destruction** | **absent** | in notes | The reverse: AQA has it, Edexcel does not |
| **quasi-public goods** | **absent** | defined | AQA defines it on two pages; the Edexcel notes never use the phrase |
| **command economy** | defined | **absent** | |
| **free market economy** | defined | **absent** | |
| **mixed economy** | defined | **absent** | |
| **sustainable development** | in notes | **absent** | Already open as N-Q8 in `REVIEW-NOTES.md` for Edexcel `2-5-4` |
| **complementary goods** | **absent** | **absent** | Borderline — the notes discuss complements, just never with this phrase. See (c) |

The three economic-systems entries are worth one decision rather than three: AQA
A-level does not examine economic systems the way Edexcel Theme 1 does, so their
absence from the AQA notes may be entirely correct.

### A2. Quantitative skills with no formula in the glossary

Both specs require these calculations. The glossary can only show a formula the
notes already state, so each of these needs a `formula-box` adding to a notes
page before it can appear.

| Required calculation | Edexcel A | AQA |
| --- | --- | --- |
| ratios and fractions | absent | absent |
| percentage change | in notes, no formula | in notes, no formula |
| percentage **point** change | absent | absent |
| mean | in notes, no formula | in notes, no formula |
| median | in notes, no formula | in notes, no formula |
| quantiles | absent | absent |
| converting money to real terms | absent | absent |
| rate of change vs level of a variable | absent | *(Edexcel QS10 only)* |
| seasonally adjusted figures | absent | *(Edexcel QS12 only)* |

**Percentage change is the notable one.** It is QS2 on both specs, it is used
throughout the notes, and no page states it as a formula. Edexcel's QS10–12 —
rate of change against level, composite indicators, seasonally adjusted figures —
are Edexcel-only and only composite indicators is covered.

Cost, revenue, profit, elasticity and index numbers are all fully covered.

### A3. In the notes but never defined — 70 Edexcel, 64 AQA

The largest category and the cheapest to fix: the notes teach these, but no
`<span class="key-definition">` chip names them, so the extractor cannot see
them. Adding a chip to the page that already explains the concept is a
formatting change, not a wording change, and re-running the extractor picks it
up with no further work.

Full lists are in `spec-checklist.md`. The ones I would do first, because they
are core vocabulary a student would expect a glossary to have:

> `perfect competition`, `oligopoly`, `monopsony`, `natural monopoly`,
> `barriers to entry`, `contestable market`, `price discrimination`,
> `economies of scale`, `returns to scale`, `law of diminishing returns`,
> `public good`, `private good`, `free rider problem`, `negative externality`,
> `positive externality`, `external cost`, `external benefit`, `welfare loss`,
> `excess demand`, `excess supply`, `equilibrium price`, `price mechanism`,
> `aggregate supply`, `circular flow of income`, `real GDP`, `nominal GDP`,
> `unemployment rate`, `claimant count`, `exchange rate`, `interest rate`,
> `balance of payments`, `tariff`, `quota`, `trading bloc`,
> `transfer payment`, `subsidy`, `privatisation`, `quantitative easing`,
> `Laffer curve`, `Phillips curve`, `Lorenz curve`, `Gini coefficient`,
> `Human Development Index`, `J-curve effect`, `productivity`,
> `labour productivity`, `profit maximisation`,
> `marginal propensity to consume / save / tax / import`

**`marginal propensity to consume` deserves singling out.** All four marginal
propensities are undefined on both boards, yet the notes carry four multiplier
formulae that depend on them — `M = 1/(1 − MPC)` and `M = 1/(MPS + MPT + MPM)`.
The glossary will show the formulae with no definition of their terms.

---

## (b) Defined inconsistently

### B1. 36 terms are worded differently across their sources

Listed in full, with every wording side by side, in **`review-decisions.md`
section E**. Either align the notes, or name the canonical page in
`curation.preferredSources`.

### B2. Three terms whose chips are not definitions at all

The clearest defect found. On the market-structure pages, the chips for
**allocative efficiency**, **productive efficiency** and **dynamic efficiency**
introduce a verdict about that market structure rather than a definition:

> *Allocative efficiency:* “**No —** The firm does **not** produce where
> P = MC, so resources are not allocated efficiently.” — `1-5-4`, `3-4-3`

Six pages do this (`1.5.3`, `1.5.4`, `1.5.6` on AQA; `3.4.2`, `3.4.3`, `3.4.5`
on Edexcel). None of the three terms has a genuine chip definition anywhere.

**Their real definitions are in the efficiency comparison tables** on
`3-4-1-efficiency.html` and `1-5-10-market-structure-efficiency-resource-allocation.html`,
which are candidates in `review-decisions.md` section A. Approving those two
tables and excluding the six verdict chips fixes all three terms at once. That
is why the table harvest matters more than its size suggests.

### B3. Six definitions that run on into a list

The definition ends mid-thought because the rest is the bulleted list that
follows: `Competition`, `Partial Market Failure`, `Quasi-public goods`,
`Factors of production`, `Asymmetric information`, `Moral hazard`. Listed in
`review-decisions.md` section F. Either make the definition self-contained on the
page, or accept the short form.

---

## (c) Ambiguous or borderline

1. **`complementary goods`** — reported absent from both boards because that
   exact phrase is never used, though the notes do discuss complements. A
   wording question, not a content gap.

2. **33 chips have no trailing colon.** The notes use a trailing colon to signal
   a definition. Most of these are still definitions written as a sentence
   (“Globalisation is the increasing integration…”) and are fine. A few are the
   term used as a sentence subject rather than defined — `Behavioural economics
   challenges this view, arguing that…` is one. Listed in
   `review-decisions.md` section D.

3. **16 terms had to be named from a section heading**, because the chip said
   only `Definition:`. Headings are prose, so these produced names like
   `What Is LRAS?`. I have already merged the obvious ones into existing terms
   via `curation.aliases` — all listed for confirmation in
   `review-decisions.md` section G. The definitions themselves are untouched.

4. **Nine `concept-table`s carry a definition column.** Some genuinely define
   terms; some are classification grids that only look like it (the PES value
   tables, for instance). All nine are in `review-decisions.md` section A with
   every row shown.

5. **49 display formulae extracted, and some are worked arithmetic**, not
   formulae to learn — `M = 1/(1 − 0.8) = 1/0.2 = 5` is a multiplier example,
   not the multiplier formula. Marked for exclusion in
   `review-decisions.md` section B.

6. **~54 formulae in the notes are written as plain text, not LaTeX** —
   `MSC = MPC + MEC`, `AD = C + I + G + (X − M)` on `2-2-4`, `MRP = MPP × MR` in
   a table header. The same identity is sometimes LaTeX on one page and plain
   text on its twin. **The glossary shows only the LaTeX ones**, so these are
   invisible to it. Converting them to `formula-box` LaTeX on the notes pages
   would be a formatting change, and I have not made it — it needs your
   instruction, and it touches pages.

7. **162 inline `\( … \)` formulae are deliberately not extracted.** They are
   fragments inside sentences — `MC = MR`, `P × Q` — rather than formulae that
   stand alone. Say the word if you want them.

---

## Two pre-existing bugs, already logged

Found while scanning; logged as **G1** and **G2** in `REVIEW-NOTES.md`, not
fixed:

- `edexcel-theme-2/2-1-3-employment-unemployment.html` contains LaTeX but never
  loads MathJax, so its formulae render as literal `\[ … \]` on the live site.
  The only page in that state.
- `.formula-box` has no CSS rule anywhere in `css/`, despite `CLAUDE.md`
  documenting it as a component. All 51 instances render as an unstyled `div` —
  which also means the glossary's KaTeX formulae will look *better* than the
  ones on the notes pages until this is fixed.

---

## How the specification scan was done

`pdfplumber` in `.venv` extracted the text of both PDFs to a scratch directory
outside the repo. Two throwaway scripts then compared it against the notes: an
n-gram diff to surface candidate terms, and a precise checker over a sifted list
of 135 terms plus each board's quantitative-skills list.

**No specification text was written into the repo**, and the scratch files are
outside it. The scripts are not kept, because they depend on PDFs that are to be
deleted — this paragraph is the reproduction record.

**Still outstanding:** the two spec PDFs are committed and live at
`economicsacademy.co.uk/specificiations/` (both HTTP 200, `robots.txt` is
`Allow: /`). Extraction only needs them on disk, not in the repo.
