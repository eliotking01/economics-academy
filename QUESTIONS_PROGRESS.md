# QUESTIONS_PROGRESS

Batch state and working notes for the free practice questions. The authoring
standard is `QUESTIONS_GUIDE.md`; this file records what is done, what is next,
and everything learned along the way, so work can resume cleanly in a new
session.

**Live: 105 topics, 808 questions. AQA is complete, Edexcel Theme 1 is complete,
and Theme 2 unit 2.1 is done. 61 topics remain.**
Target: 166 topics, ~1,272 questions.

**Branch:** `feature/topic-questions`, branched from `main`.
**Nothing has been pushed.** `main` auto-publishes, so pushing needs explicit
approval — see `CLAUDE.md`.

---

## Read this first if you are resuming

1. `QUESTIONS_GUIDE.md` — the authoring standard. Non-negotiable.
2. This file's **Recurring problems** section below. Five batches produced the
   same handful of failures over and over; reading it first will save a lot of
   rework.
3. `scripts/build_questions.py` — the generator and validator. It refuses to
   write a page from a bad source, so treat `--check` as the first gate.

---

## Resume workflow

```bash
git checkout feature/topic-questions
BASE=$(git rev-parse HEAD)        # capture BEFORE touching anything

# 1. author questions-data/<board-dir>/<code>.json for each topic in the batch
python3 scripts/build_questions.py --check          # validate, write nothing
python3 scripts/build_questions.py --sitemap        # build pages + sitemap block
python3 scripts/append_questions_link.py            # add the end-of-notes block

# 2. verification, against the commit before the batch
python3 scripts/verify_html.py practice-questions revision-notes
python3 scripts/verify_links.py practice-questions revision-notes
python3 scripts/verify_text_integrity.py $BASE
python3 scripts/verify_markup_integrity.py $BASE --strict
git diff $BASE -- revision-notes/ templates/ js/ css/ sitemap.xml | grep '^-[^-]'
#   ^ must print nothing. Any output means a pre-existing line was changed.
```

Then run the **cold re-solve** (see below), fix what it finds, rebuild, and
commit.

### Authoring efficiently

Writing JSON by hand is slow and error-prone past a couple of sets. Batches 4
and 5 used a throwaway Python helper to emit the files, which was substantially
faster and eliminated a whole class of malformed-JSON mistakes:

```python
# a scratch file, not committed
def q(i, skill, diff, stem, opts, ans, working, distractors, table=None, sketch=False): ...
def write(spec, slug, title, short, pageTitle, metaDesc, intro, teaser, questions): ...
#   write() asserts 120 <= len(metaDesc) <= 165 so the length rule fails fast
```

Read the corresponding notes page **before** writing each set. Every question
must be answerable from what the notes actually teach — see "Board fidelity"
below.

### The cold re-solve (do not skip this)

The single most valuable step. Print the stems and options with the keys
**withheld**, answer every question yourself from the stem alone, then diff your
answers against the recorded keys:

```bash
# print without answers
python3 - <<'PY'
import json,re,pathlib
def c(s): return re.sub(r'\s+',' ',re.sub(r'<br />',' | ',re.sub(r'</?(strong|em)>','',s))).strip()
for f in sorted(pathlib.Path('questions-data/<board-dir>').glob('<pattern>')):
    d=json.loads(f.read_text()); print(f"\n## {d['spec']}")
    for i,q in enumerate(d['questions'],1):
        print(f"Q{i}. {c(q['stem'])}")
        if q.get('table'): print("   T: "+" || ".join(" | ".join(r) for r in [q['table']['head']]+q['table']['rows']))
        for L in "ABCD": print(f"   {L} {c(q['options'][L])}")
PY
```

Then diff a dict of `{spec: "ABCD..."}` against the files. Across 401 questions
this produced 0 mismatches — but only because problems were caught and fixed
*during* authoring by the checks below.

---

## Recurring problems, and how to avoid them

These came up in every batch. Design around them from the start rather than
fixing them afterwards.

### 1. Alphabetical option order pushes the answer to A or B

**By far the most common failure.** Six sets failed the generator's
letter-distribution check, and the cause was the same every time: when options
are names — market structures, types of economy of scale, functions of money,
behavioural biases — sorting them alphabetically tends to put the correct answer
early, because the right answer is often the most specific term.

**Fix:** for option lists that name things, order them by a *domain* sequence
instead of alphabetically — the competitive spectrum, the order the notes list
them, or a consistent grid (demand-up / demand-down / supply-up / supply-down).
`QUESTIONS_GUIDE.md` permits this; the rule is that ordering must carry no
signal, not that it must be alphabetical.

### 2. The correct option is the longest

About 120 options were rewritten across the five batches for this. It happens
naturally because the correct answer often carries an explanatory clause
("…, because X") that the distractors lack. A student can exploit it without
knowing any economics.

**Check after every batch:**

```bash
python3 - <<'PY'
import json,re,pathlib
def clean(s): return re.sub(r'\s+',' ',re.sub(r'</?(strong|em)>','',s)).strip()
flags=[]
for f in pathlib.Path('questions-data').rglob('*.json'):
    for q in json.loads(f.read_text())['questions']:
        L={k:len(clean(v)) for k,v in q['options'].items()}
        if max(L.values())<30: continue          # one-word labels carry no signal
        key=L[q['answer']]; other=max(v for k,v in L.items() if k!=q['answer'])
        if other and key/other>1.10: flags.append((q['id'],key,other))
print(flags or "none")
PY
```

Fix by **shortening the correct option**, not by padding distractors — padding
tends to make them waffly and obviously wrong.

### 3. metaDescription length

The validator requires 120–165 characters and this failed repeatedly. Assert it
in the authoring helper so it fails at write time rather than at build time.

### 4. The generator's own checks can be wrong

In batch 3 the US-spelling blocklist rejected `practise`, which is correct UK
English for the *verb* (`practice` is the noun). `license`/`licence` had the
same problem. Both were removed from `US_SPELLINGS` with a comment explaining
why. **If a validator complains about something that looks correct, check the
validator before changing the question.**

### 5. Originality against the past papers

Batch 1's first draft of the XED calculation used a supermarket tea/coffee pair.
The June 2023 Paper 3 uses a coffee/tea pairing twice (Extract C, and Q22 on
comparative advantage), and its Q03 is an XED calculation from a two-row table.
Same archetype plus a similar commodity pair is too close, even with different
numbers. Rewritten to a gym membership vs day passes.

**The archetype is fine to reuse — the surface detail is not.** When writing a
calculation that mirrors a real question's structure, change the context
completely.

### 6. Repetitive question formats within a set

An early draft of 1.2.3 had seven consecutive "which bias is this?" items. Real
papers vary the format. Mix identification with consequence questions, data
tables, and contrasts between two accounts of the same behaviour.

### 7. Check originality mechanically — the past papers are readable

Batches 1–5 checked originality by eye. Batch 6 automated it, and immediately
caught something reading had missed (see the batch 6 record). Do this from now
on; it takes about a minute per batch.

There is no `pdftotext` on this machine and no Python PDF library, but macOS
ships Swift with PDFKit, which extracts the text properly. A four-line script is
enough:

```swift
import Foundation
import PDFKit
for path in CommandLine.arguments.dropFirst() {
    guard let doc = PDFDocument(url: URL(fileURLWithPath: path)) else { continue }
    print("@@@FILE \(path)"); print(doc.string ?? "")
}
```

```bash
swift pdftext.swift past-papers/aqa/*/*/*question-paper.pdf > aqa-all.txt
```

45 AQA question papers come to about 945 KB of text and take a couple of minutes
to extract. Then shingle both sides into word n-grams and intersect. What the
results mean:

- **Hits at N=6–8 are almost all stock AQA scaffolding** — "Which one of the
  following is", "All other things being equal, the most likely". Those are the
  calibration target, so leave them alone.
- **Anything at N=10 is a real problem.** Both batches checked so far were clean
  at N=10.
- **Also grep the corpus for each distinctive figure** in a new stem, table or
  option. This is what caught 2.1.3 Q7: the numbers matched before any phrasing
  did. Common round numbers (£480, 460) collide harmlessly all the time, so read
  the surrounding context before rewriting anything.
- **Compare whole option sets, not just single values.** Batch 7's multiplier
  item shared three of its four options with a real question on the same
  archetype while sharing no phrasing at all, so only a set comparison would
  find it. One value in common is coincidence — 2.0, 2.5, 5.0 and 10.0 are the
  multiplier values every textbook uses. Three is worth investigating.

  Do this by **extracting real option blocks** with a regex over the corpus
  (`A <num> B <num> C <num> D <num>`) and intersecting sets — not by testing
  whether each value appears somewhere in the text. A substring test against
  945 KB of prose reports every number as "found" and tells you nothing. There
  are about 52 numeric option sets across the 45 papers.

  Three shared values is a **prompt to compare archetypes, not a verdict**. In
  batch 8 one of our sets shared three values with a real question that turned
  out to be price elasticity of supply read off a diagram — a different topic
  entirely, so coincidence. Another shared three with a natural-rate calculation
  that asked for the same quantity by the same route, which was a rewrite.

- **The highest-risk shape is a stock AQA stem followed by a list of causes.**
  "Which one of the following is most likely to cause demand-pull inflation?"
  collided word for word in batch 8. The stems are fixed phrases and the set of
  textbook causes is small, so the two together collide almost by default.
  Prefer a scenario the student has to interpret; it is both more original and a
  better question.

  Batch 10 tested this deliberately by dropping the stock opening entirely and
  using scenarios and tables throughout. It returned **zero hits at every n-gram
  length, including 8** — the only batch so far to do so. Treat the scenario form
  as the default and the stock stem as the exception.

Do **not** try to parse the PDFs with a stdlib script. Their content streams use
subsetted fonts with custom encodings, so pulling the parenthesised strings out
of the decompressed streams returns binary noise, not text.

### 8. Cross-board duplication — the binding constraint on Edexcel

**New in batch 12, and the single biggest risk for every remaining batch.** The
past papers are no longer the main originality problem. **Our own AQA bank is.**
610 AQA questions already exist, and most Edexcel topics cover economics that
one of them already tests.

Batch 12 was written from the Edexcel notes with no reference to the AQA sets,
and it still produced **four questions that read as ports**, including one whose
stem was word-for-word identical to an AQA stem with only the commodity changed.
None of them was visible while drafting. All four were caught by shingling the
new sets against `questions-data/` and comparing stems:

```python
# 8-grams over STEMS ONLY, new sets vs every AQA question
aqa = {(spec, i): norm(q['stem']).split() for ...}   # skip edexcel dirs
```

Run this **as well as** the past-paper check, from now on. Notes on reading it:

- **Shared option grids are fine and expected.** The four price/quantity
  strings ("A higher price and a higher quantity", …) produce 19 shared
  10-grams between any two questions that use them, and §1 above explicitly
  tells you to standardise on that grid. Ignore option-only overlap.
- **The elasticity stem template is fine.** "Measuring each percentage change
  against its original value, the … elasticity of … is" appears in every
  elasticity question on the site, on both boards. It is a precision
  instruction the guide requires, and inventing a different phrasing per board
  would make the site inconsistent for no gain.
- **Shared runs inside the stem's own scenario are not fine.** That is the
  signal. Filter the template and the option strings out first, then read what
  is left by hand.

The four fixed in batch 12, all rebuilt on new scenarios:

| Ours | Collided with | What was shared |
| --- | --- | --- |
| 1.1.1 Q1 | AQA 1.1.1 Q3 | Identical second sentence; same answer; only the commodity differed |
| 1.2.8 Q4 | AQA 1.5.11 Q5 | Identical opening sentence; same answer; near-identical correct option |
| 1.2.3 Q9 | AQA 1.3.2 Q8 | Same question in substance — which PED maximises tax revenue |
| 1.2.8 Q2 | AQA 1.5.11 Q3 | Same straight-line surplus template and the same £20 equilibrium price |

---

## Ratified content decisions

Do not revisit these without asking.

- **AQA spec codes are the site-local `1.x.y` / `2.x.y`**, not the real AQA 7136
  codes (`4.1.x` / `4.2.x`). See `CLAUDE.md`. Confirmed with the site owner at
  the planning stage.
- **No MathJax on question pages.** It is render-blocking and would put
  Lighthouse Performance at risk across ~1,270 pages. Use Unicode maths: `×`,
  `÷`, `−` (U+2212, not a hyphen), `%`, `£`, `Δ`, `Q₁`.
- **Every option opens with a capital letter**, including sentence-completion
  stems. Enforced by the validator. Requested by the site owner after reviewing
  the prototype.
- **Two page looks.** Question pages use `css/pages/quiz.css` (revision-notes
  textbook look). The hub and board indexes use
  `css/pages/practice-questions.css` (section landing-page look, matching
  `revision-notes/index.html` and the notes board indexes) — *without* the white
  `.notes-container` card. Requested by the site owner; do not merge them.
- **Numbers use comma separators** (`1,200`), matching the existing notes.

---

## Board fidelity — important for the Edexcel batches

Every set so far was written **against its own notes page**, and this mattered
more than expected:

- 1.2.2 (Imperfect Information) deliberately stays inside *information gaps* and
  *asymmetric information*. Draft questions on adverse selection and moral
  hazard were cut, because the notes do not teach those terms.
- The behavioural sets use the notes' exact vocabulary — *herding bias*, *rule
  of thumb*, *bounded self control* — not the textbook alternatives.
- Where the notes carry a worked example, the questions use **different
  figures**, so a student is not simply re-doing the same sum.

**The Edexcel themes will test this hardest.** Several Edexcel topics cover the
same economics as AQA topics already written — Edexcel 1.2.3 elasticities against
AQA 1.3.2, Edexcel 3.3.2 costs against AQA 1.4.4, Edexcel 3.4.x market
structures against AQA 1.5.x. `QUESTIONS_GUIDE.md` requires **fully separate
sets**: new contexts, new numbers, and each board's own terminology and spec
boundaries. Do not port an AQA set across and relabel it.

---

## Verification harness notes

Useful things established while building, worth not rediscovering.

- **Local serving needs a real server**, not `file://` — `inject-templates.js`
  fetches the header and footer at runtime.
- **Lighthouse must be run against a gzip-capable server.** `python3 -m
  http.server` sends no gzip, which penalises the largest page heavily and
  produced a misleading Performance score of 68. With gzip and cache headers on
  (as GitHub Pages serves), the same page scores 92–97. A throwaway gzip server
  is enough.
- **`--dump-dom` and `--disable-javascript` fight each other.** To check the
  no-JS experience properly, launch Chrome with
  `--blink-settings=scriptEnabled=false` and take a *screenshot* via CDP —
  `Runtime.evaluate` cannot run with scripting off. CDP's
  `Emulation.setScriptExecutionDisabled` does **not** trigger `<noscript>`.
- **Node 22 has a global `WebSocket`**, so a ~40-line CDP driver needs no npm
  install. That was used for interaction testing, CLS measurement and font
  metric comparison.
- **CLS only appears under network throttling.** On localhost the fonts land
  before first paint and CLS reads 0.

---

## Remaining work

### Edexcel — 65 topics, 505 questions still to write

**This is all that is left.** AQA is finished and Theme 1 is complete.

| Theme | Topics left | Questions left |
| --- | --- | --- |
| Theme 1 | 0 — **complete**, 22 topics and 163 questions | — |
| Theme 2 | 20 (units 2.2 to 2.6) | ~150 |
| Theme 3 | 20 | 157 |
| Theme 4 | 21 | 163 |

**Next batch: Theme 2 unit 2.2 (Aggregate Demand)** — 2.2.1 aggregate demand,
2.2.2 consumption, 2.2.3 investment, 2.2.4 government expenditure, 2.2.5 net
trade. Five topics. Edexcel splits AD into five separate topics where AQA has
one (2.2.3 Determinants of AD, 9 questions), so there is more room than the
overlap first suggests — each Edexcel topic can go deeper into its own component
than the single AQA set does.

**The twins for the rest of Theme 2 are AQA macro, and the overlap is severe.**
Unit 2.1 alone collided with AQA 2.1.2, 2.1.3, 2.1.4, 2.3.2, 2.3.3 and 2.6.3.
Print every AQA macro stem before writing, exactly as batch 13 did for micro.
Specific ground already occupied:

- **2.2 (AD)** — AQA 2.2.2 and 2.2.3: the AD expression, why AD slopes down,
  MPC calculation, interest rates and consumption, the wealth effect, net
  investment, automatic stabilisers, depreciation and net trade.
- **2.3 (AS)** — AQA 2.2.5 and 2.2.6 cover SRAS and LRAS almost completely,
  including the Keynesian/Classical contrast and both sketch items.
- **2.4 (national income)** — AQA 2.2.1 (circular flow) and 2.2.4 (the
  multiplier, 10 questions including five calculations).
- **2.5 (growth)** — AQA 2.3.1 (growth and the economic cycle, output gaps).
- **2.6 (objectives and policies)** — AQA 2.1.1, 2.3.4, 2.5.1 and 2.5.2.

**Four Theme 2 pages in the remaining units are incomplete** — see
`REVIEW-NOTES.md` N-Q9. 2.2.2 does not teach expectations, 2.2.3 does not teach
the accelerator, 2.4.1 does not teach the three approaches to measuring GDP, and
2.5.1 does not teach demand-side causes of growth. Write to what each body
actually contains and note the omission, as unit 2.1 did.

**Reading the notes.** `raw-notes/edexcel/` has markdown for most of Themes 2–4,
which is far quicker than scraping the HTML — but **the published pages are what
counts**, and they differ. In Theme 1 the conversion dropped whole sections that
the raw notes contain (see the 1.3.4 case in `REVIEW-NOTES.md` N-Q8). Read the
raw markdown for speed, then diff it against the page before writing anything
that depends on a section only the markdown has.

Per-topic counts follow the same pattern: 10 for the densest calculable topics,
5–6 for narrow definitional ones, 7–9 otherwise. Recompute from the notes page
if in doubt — the guide's rule is that concision beats coverage.

---

## Open items

- **Nav sub-menu.** `templates/header.html` carries a top-level
  **Practice Questions** entry only. The two-level board dropdown that Revision
  Notes and Past Papers have was written and then deliberately removed, because
  it would have pointed at five board index pages that do not yet exist. A
  comment marks the insertion point. **Add it once the remaining board indexes
  are built.**
- **Hub and board index density.** Both list only what is live. They fill out
  per batch; no action needed.
- **Nav sub-menu.** Three of the five board indexes now exist — both AQA ones and
  `practice-questions/edexcel-theme-1/index.html`, which is now **complete** at
  22 of 22 topics rather than partial. Themes 2, 3 and 4 do not exist, so the
  two-level dropdown still cannot list all five. Now is a reasonable moment to
  restore it with the three that are finished, since none of them will change
  again; the alternative is to keep waiting until Theme 4 lands. **Needs the site
  owner's call** — it is a nav change on every page.
- **Skill mix across AQA micro.** `applied-reasoning` finished at 64% against a
  ~40% target and `calculation` at 6% against ~15%. This is a property of the
  specification — units 1.1, 1.2, 1.5, 1.7 and 1.8 are conceptual almost
  throughout. Recorded rather than corrected; watch whether macro and Edexcel
  bring the site-wide ratio closer to target. Macro 2.1 pulled the right way —
  24% `calculation` and 15% `data-table` in that batch — and 2.2 held
  `calculation` at 14%, taking the site-wide figures to 8% and 8%. Progress is
  real but slow, because micro's 401 questions dominate the total. Edexcel
  Themes 2 and 4 are where the rest of the arithmetic lives.
- **Written-response extension.** Proposed in the original brief but **not
  built** and not approved: 1–2 short written questions per topic with
  indicative-content model answers behind `<details>`, plus a marking-service
  call to action. Needs the site owner's sign-off before any work starts.
- **Site-wide issues found but not fixed** are logged in `REVIEW-NOTES.md`, per
  `CLAUDE.md`: the `navPanel` `aria-hidden` bug (the only remaining
  accessibility failure on any page), breadcrumb contrast in `css/main.css`, and
  web-font layout shift.

---

## Batch record

### Batch 1 — AQA micro 1.1–1.3 (2026-07-31)

15 topics, 104 questions. All 94 new questions re-solved cold from the stem
alone with **0 mismatches** against the recorded keys; every figure in every
calculation and data table recomputed and confirmed.

Fixed during verification:

- 1.3.6 failed the generator's letter-distribution check (C used four times in
  a set of seven). Option order across the four "effect on the other market"
  questions was regularised to demand-up / demand-down / supply-up /
  supply-down, which spread the answers and made the set internally consistent.
- 23 options rewritten across 9 sets because the correct option was more than
  10% longer than the next longest — a formatting tell. None remain.
- 1.3.2 Q4's context was rewritten for originality (see Recurring problems §5).

| | |
| --- | --- |
| Answer letters | A 30, B 28, C 21, D 25 (even would be 26) |
| Skills | applied-reasoning 62, definition-in-context 23, data-table 12, calculation 7 |
| Difficulty | foundation 16, standard 75, stretch 13 |
| Sketch to solve | 8 |

### Batch 2 — AQA micro 1.4 (2026-07-31)

8 topics, 62 questions. All 62 re-solved cold with **0 mismatches**; every
figure in every cost, revenue and output schedule recomputed.

Fixed: 1.4.5 failed the letter-distribution check (A five times in a set of
eight) — the "which type of economy of scale" items were pushing the answer to
early letters because their options were alphabetical, so they now follow the
notes' ordering. 12 options rewritten for length.

| | |
| --- | --- |
| Answer letters | A 46, B 48, C 39, D 33 (even would be 41.5) |
| Skills | applied-reasoning 96, definition-in-context 35, data-table 21, calculation 14 |
| Difficulty | foundation 24, standard 123, stretch 19 |
| Sketch to solve | 8 |

The `calculation` share recovered as predicted: unit 1.4 contributed 7 of the
site's 14 calculation items.

### Batch 3 — AQA micro 1.5 (2026-07-31)

11 topics, 86 questions — the largest unit on the specification. All 86
re-solved cold with **0 mismatches**; concentration ratio and surplus
calculations recomputed including every distractor figure.

Fixed: 1.5.1 and 1.5.3 failed the letter-distribution check (market-structure
names sorting alphabetically); both now order options along the competitive
spectrum. 20 options rewritten for length. **The `practise` blocklist bug** was
found and fixed here (Recurring problems §4).

| | |
| --- | --- |
| Answer letters | A 65, B 74, C 63, D 50 (even would be 63) |
| Skills | applied-reasoning 151, definition-in-context 59, data-table 24, calculation 18 |
| Difficulty | foundation 35, standard 187, stretch 30 |
| Sketch to solve | 15 |

### Batch 4 — AQA micro 1.6 and 1.7 (2026-07-31)

10 topics, 75 questions. All 75 re-solved cold with **0 mismatches**; MRP, union
density and relative poverty line calculations recomputed including every
distractor figure.

Fixed: 1.6.7 and 1.7.2 failed the letter-distribution check; option order
regularised. 19 options rewritten for length.

The monopsony result — that a union or a minimum wage can raise pay *and*
employment where a single dominant employer has been restricting hiring — is
tested three times from different angles (1.6.4 Q5, 1.6.5 Q6, 1.6.6 Q5), because
it is the evaluation point these topics turn on and students routinely miss it.

| | |
| --- | --- |
| Answer letters | A 83, B 101, C 80, D 63 (even would be 82) |
| Skills | applied-reasoning 203, definition-in-context 76, data-table 26, calculation 22 |
| Difficulty | foundation 45, standard 242, stretch 40 |
| Sketch to solve | 17 |

### Batch 5 — AQA micro 1.8 (2026-07-31)

10 topics, 74 questions. **Completes AQA Microeconomics: 54 of 54 topics and
401 questions**, exactly the figure planned.

All 74 re-solved cold with **0 mismatches**. The social-cost table (1.8.4 Q9)
and tax revenue calculation (1.8.9 Q6) recomputed with every distractor figure;
1.8.9 Q6 tests whether revenue is taken on the post-tax quantity, with the
pre-tax quantity offered as the trap.

Fixed: 23 options rewritten for length. No letter-distribution failures.

**AQA Microeconomics complete — final profile:**

| | |
| --- | --- |
| Topics | 54 of 54 |
| Questions | 401 |
| Answer letters | A 98, B 122, C 102, D 79 (even would be 100) |
| Skills | applied-reasoning 257, definition-in-context 94, data-table 27, calculation 23 |
| Difficulty | foundation 55, standard 296, stretch 50 |
| Sketch to solve | 20 |

### Batch 6 — AQA macro 2.1 (2026-07-31)

4 topics, 33 questions. The first macro batch. All 33 re-derived from the stem
alone with **0 mismatches**; every figure in every calculation and table
recomputed, including all distractor values.

Fixed during verification:

- **2.1.3 Q7 was too close to a real question.** The first draft used a CPI
  table with `2020 = 100` and a value of 118.0. AQA's June 2022 Paper 3 carries
  an index-table item — copper exports, `2020 = 100`, running 100.0 / 106.0 /
  112.1 / 118.0 — so the base year and two values coincided with a real stem of
  the same archetype. Rebuilt on `2017 = 100` with values sharing nothing with
  it. See Recurring problems §5 and §7.
- **2.1.3 Q4's swapped-weights distractor landed on 108.85**, an exact rounding
  boundary, so "to one decimal place" had two defensible answers. Weights
  re-picked as 400 / 300 / 300 so all four options are exact.
- 2.1.3 Q2's earnings figures moved off £480, which appears in a real AQA data
  table.
- 3 options rewritten for length. No letter-distribution failures.
- 2.1.2 Q6 dropped a "to one decimal place" instruction that claimed exactness
  the options ("about 2.5%") did not have.

**No `sketch` items in this batch, by design.** Unit 2.1 is indicators and
national income data; the AD/AS diagrams start at 2.2, so a sketch item here
would have been invented rather than earned. Expect the sketch share to return
from 2.2 onward.

| | |
| --- | --- |
| Answer letters | A 9, B 7, C 8, D 9 (even would be 8.25) |
| Skills | applied-reasoning 15, calculation 8, data-table 5, definition-in-context 5 |
| Difficulty | foundation 4, standard 24, stretch 5 |
| Sketch to solve | 0 |

The skill mix landed much closer to target than any micro batch:
`calculation` 24% against a ~15% target and `data-table` 15% against ~20%,
against 6% and 7% across the whole of micro.

### Batch 7 — AQA macro 2.2 (2026-07-31)

6 topics, 50 questions. All 50 re-derived from the stem alone with **0
mismatches**; every figure in every multiplier, propensity and circular-flow
calculation recomputed, including all distractor values.

Fixed during verification:

- **2.2.4 Q3 shared three option values with a real question.** AQA's June 2019
  Paper 3 asks for the value of a multiplier with options `2.0 / 2.5 / 5.0 /
  10.0`. The draft set was `2.0 / 3.3 / 5.0 / 10.0` on the same archetype — too
  close, even though the route to the answer was different. Leakages re-picked
  as 0.05 / 0.15 / 0.05, giving `1.3 / 4.0 / 6.7 / 20.0` and no overlap. This is
  the second batch running where the mechanical originality check (§7) found
  something reading had not.
- **2.2.4 Q9 had two options meaning the same thing** — "At full capacity
  output" and "On the vertical section of the LRAS curve". A duplicate option is
  a wasted option and hands students an elimination shortcut. Replaced with
  "Slightly below full capacity output", so the four options are distinct points
  on one scale.
- 5 options rewritten for length. No letter-distribution failures.

**Sketch items are back**, as predicted: 5 of 50, exactly the ~10% target. Unit
2.2 is the AD/AS unit, so the diagram is the natural way to answer — the
Keynesian versus Classical LRAS contrast (2.2.2 Q5 and Q6) is tested by asking
what the student's own sketch shows.

| | |
| --- | --- |
| Answer letters | A 11, B 14, C 13, D 12 (even would be 12.5) |
| Skills | applied-reasoning 26, definition-in-context 12, calculation 7, data-table 5 |
| Difficulty | foundation 8, standard 36, stretch 6 |
| Sketch to solve | 5 |

`calculation` landed at 14% against the ~15% target — unit 2.2.4 alone
contributed 5 items. `data-table` came in at 10% against ~20%: the unit is
diagram- and concept-led, and forcing more tables into it would have meant
inventing data rather than interpreting it.

### Batch 8 — AQA macro 2.3 (2026-07-31)

4 topics, 36 questions. All 36 re-derived from the stem alone with **0
mismatches**; every output gap, natural rate and quantity theory figure
recomputed, including all distractor values.

**The originality check earned its keep here — it caught two genuine rewrites
that reading had passed.**

- **2.3.3 Q2 duplicated a real stem word for word.** The draft opened "Which one
  of the following is most likely to cause demand-pull inflation?", which is
  exactly the stem of a real AQA Paper 3 item, and three of the four options
  matched it in substance (indirect taxation, oil prices, a fall in interest
  rates). Laid side by side it read as a rewrite. Replaced with a scenario — an
  income tax cut in an economy near full capacity — where the student has to
  identify the mechanism rather than pick from a list of causes.
- **2.3.2 Q7 reproduced a real calculation almost exactly.** AQA June 2020 asks
  for the natural rate given "2% frictional plus 3% structural" and cyclical
  unemployment of 4%, with options 3 / 5 / 6 / 9. The draft asked for the same
  quantity by the same route, reached the same 5% answer, and its components
  worked out to precisely 2% and 3%. Rebuilt as the inverse operation —
  subtracting cyclical unemployment from total unemployment — on new figures.

**Lesson worth carrying forward: a stock AQA stem plus a list of causes is the
highest-risk question shape there is.** Those stems are fixed phrases, the set
of textbook causes is small, and the two together collide almost by default.
Prefer a scenario the student has to interpret. See Recurring problems §7.

The site-wide option-set audit was also run retrospectively over all 520
questions, using option blocks extracted from the papers rather than a substring
test. Nothing from batches 1 to 7 needed changing; one further set in this batch
(2.3.3 Q6, Fisher's equation) shared three values with a real *price elasticity
of supply* question, which is a different topic and archetype entirely — the
numbers were changed anyway, since it cost nothing.

| | |
| --- | --- |
| Answer letters | A 5, B 10, C 12, D 9 (even would be 9) |
| Skills | applied-reasoning 21, definition-in-context 8, data-table 4, calculation 3 |
| Difficulty | foundation 5, standard 27, stretch 4 |
| Sketch to solve | 3 |

`calculation` fell back to 8% here. Unit 2.3 is largely conceptual — types of
unemployment, causes of inflation, policy trade-offs — and the arithmetic it does
support (unemployment rates, inflation rates from a CPI series) was already used
in unit 2.1, so repeating it would have meant near-duplicate questions across two
topics.

### Batch 9 — AQA macro 2.4 (2026-07-31)

4 topics, 30 questions. All 30 re-derived from the stem alone with **0
mismatches**; every bond yield, balance sheet total, credit creation multiple
and bank ratio recomputed, including all distractor values.

Nothing needed rewriting for originality — the first macro batch where that was
true. Two 8-gram hits were stock stem scaffolding, and both were checked by hand
against the real questions that produced them:

- "Which one of the following is a function of…" appears in a real paper, but
  the completion there is *prices in a market economy*, not banks. Only the
  stock opening is shared.
- The corpus does contain a real **bank balance sheet** item and a real
  **systemic risk** item, both worth knowing about. The balance sheet one gives
  a full balance sheet and asks what kind of bank it is; ours gives four line
  items and asks for total liabilities, on entirely different figures. The
  systemic risk one asks under what conditions systemic risk arises; ours gives
  a contagion scenario and asks the student to name it. Archetype reuse is
  allowed and the surface detail differs throughout.

Worth recording for later batches: the papers also contain a **Fisher's equation
of exchange** item asking for the percentage rise in the price level. Unit
2.3.3 Q6 asks for the price level itself on unrelated figures, and shares none
of its options — but anyone writing more quantity theory questions should check
against it.

| | |
| --- | --- |
| Answer letters | A 7, B 8, C 10, D 5 (even would be 7.5) |
| Skills | applied-reasoning 14, definition-in-context 10, calculation 3, data-table 3 |
| Difficulty | foundation 4, standard 22, stretch 4 |
| Sketch to solve | 0 |

**No sketch items, by design.** Unit 2.4 is money, banking and regulation; its
only diagram is a single AD/AS figure for monetary policy, and a sketch item
there would have duplicated 2.2 and 2.3. The unit does carry good arithmetic
instead — bond yields, credit creation and bank ratios — though at 30 questions
that is only 3 calculation items.

### Batch 10 — AQA macro 2.5 (2026-07-31)

2 topics, 17 questions. All 17 re-derived from the stem alone with **0
mismatches**; the budget balance and tax progressivity figures recomputed,
including all distractor values.

**Originality came back completely clean — no shared runs even at 8 words.**
That is the first batch with no hits at all, and it is not luck: this batch
deliberately avoided the stock "Which one of the following…" opening throughout,
using scenarios and table-based items instead. Batch 8 identified that stem plus
a list of causes as the highest-collision shape on the paper; dropping it removed
every hit at once. Worth doing by default from here.

The set validator passed on the first run, with no length or distribution fixes
needed — also a first, and a consequence of applying the option-ordering and
length rules while drafting rather than afterwards.

One option was rewritten on quality grounds rather than because a check caught
it. In 2.5.2 Q6, "Is owned by shareholders rather than the state" is true of any
privatised firm and so obviously not a reason for the policy to fail — a wasted
option. It became "Has less access to government funding than before", which is
a mistake a student might genuinely make.

Care was needed over overlap with earlier units, which is now the binding
constraint on macro rather than originality against the papers:

- 2.2.6 Q6 already asks how training raises capacity (quality of labour), so
  2.5.2 uses **infrastructure** for the mechanism question instead.
- 2.2.6 Q7 already asks what an LRAS shift does with AD unchanged, so 2.5.2 Q7
  asks for the **contrast with expansionary fiscal policy** instead.
- 2.2.3 Q6 already covers automatic stabilisers, so 2.5.1 stays on the deficit
  and debt distinction, the Laffer curve, crowding out and Ricardian
  equivalence.

| | |
| --- | --- |
| Answer letters | A 4, B 5, C 5, D 3 (even would be 4.25) |
| Skills | applied-reasoning 9, definition-in-context 5, data-table 2, calculation 1 |
| Difficulty | foundation 2, standard 13, stretch 2 |
| Sketch to solve | 1 |

### Batch 11 — AQA macro 2.6 (2026-08-01)

5 topics, 43 questions. **Completes AQA Macroeconomics: 25 of 25 topics and 209
questions, exactly the figure planned.**

All 43 re-derived from the stem alone with **0 mismatches**; every opportunity
cost, current account balance, elasticity sum and exchange rate conversion
recomputed, including all distractor values.

**Originality clean at every n-gram length again**, confirming batch 10's
finding rather than repeating a fluke. Two batches running now, both written on
scenarios and tables rather than stock stems, have produced zero hits.

Fixed during verification: 5 options shortened for length. No letter-distribution
failures and no answer-key changes.

**Re-verified in full after the commit** (2026-08-01), including a second cold
re-solve of all 43 — again 0 mismatches. The numeric option-set check, which the
first pass did not record, turned up one 3-value overlap and it is a coincidence:
2.6.2 Q2 (opportunity cost from a maximum-output table) has options
`0.25 / 2 / 4 / 240 units of cloth`, against `A +0.25 B +2.0 C +4.0 D +7.5` in
AQA June 2019 Paper 3 Q29 — **price elasticity of supply read off a diagram**.
Different topic, different route, different units, and our fourth value shares
nothing. This is the same real question that batch 8 adjudicated the same way;
0.25 / 2 / 4 are simply the reciprocal pairs that any ratio question lands on.
**Left as it is — do not rewrite it a third time round.**

Also noted, not changed: 2.6.4 Q3 carries `"skill": "calculation"` but its only
arithmetic is 0.4 + 0.5 against the Marshall-Lerner threshold. Defensible, since
the condition is numeric, but it flatters the batch's calculation share by one.

**A verification gotcha worth knowing about.** This batch ran on a different
calendar day from the previous one, and the removed-line guard

```bash
git diff $BASE -- revision-notes/ templates/ js/ css/ sitemap.xml | grep '^-[^-]'
```

fired on roughly 75 lines of `sitemap.xml`. It was benign: `build_questions.py
--sitemap` rewrites the whole practice-questions block with today's `lastmod`,
so every existing URL line is removed and re-added with a new date. Confirm it
rather than assuming — compare the URL sets and the entries with `lastmod`
stripped out:

```python
urls    = set(re.findall(r"<loc>(.*?)</loc>", text))
entries = set(re.sub(r"<lastmod>[^<]*</lastmod>", "", e)
              for e in re.findall(r"<url>.*?</url>", text))
```

Zero URLs removed and zero entries lost means it is a date change only. **Run
the guard against `revision-notes/ templates/ js/ css/` separately** — that is
the check that actually matters, and it stays clean.

| | |
| --- | --- |
| Answer letters | A 9, B 12, C 11, D 11 (even would be 10.75) |
| Skills | applied-reasoning 26, definition-in-context 9, data-table 4, calculation 4 |
| Difficulty | foundation 5, standard 33, stretch 5 |
| Sketch to solve | 2 |

### Batch 12 — Edexcel Theme 1, units 1.1 and 1.2 (2026-08-01)

16 topics, 122 questions. **The first Edexcel batch**, and the first questions
on the site written to Edexcel rather than AQA.

All 122 re-derived from the stem alone with **0 mismatches**. Every figure
recomputed independently, including all distractor values — 50 arithmetic
checks, plus the internal consistency of the four schedules (the PPF table's
sacrifices rise 4 / 8 / 12 / 16 for equal 30-thousand steps; the coffee schedule
clears at exactly one price; the candle and snack-bar tables shift by a constant
amount at every price).

**Originality against the 40 Edexcel papers came back completely clean — zero
shared runs at 8 words or more**, and no numeric option set shared three values
with any of the 25 numeric option sets in the papers. The batch used scenarios
and tables throughout and avoided stock stem openings, which is now the third
batch running to return nothing (see batches 10 and 11).

**Originality against our own AQA bank was a different story, and is the real
finding of this batch.** Four questions read as ports and were rebuilt; see
Recurring problems §8, which is the most important thing to read before the next
Edexcel batch.

Also fixed during verification: 3 options lengthened so the correct one was not
the longest, and one stem/option grammar clash (1.2.8 Q7's stem ended "…social
surplus is" while its options opened "Is unchanged", "Rises"). Worth checking
mechanically — a stem ending in a verb plus an option starting with one is easy
to introduce when options get reordered to fix the letter distribution. No
letter-distribution failures and no answer-key changes.

**Board fidelity.** Every set was written against its own Edexcel notes page.
Points where that changed what could be asked:

- Edexcel 1.1.5 teaches the **functions of money** and the double coincidence of
  wants inside the specialisation topic, which AQA does not, so two questions
  cover it.
- Edexcel 1.2.3 covers PED, YED **and** XED in one topic, where AQA splits them.
  That is why 1.2.3 carries 10 questions and three separate calculations.
- Edexcel 1.2.10 uses the notes' own vocabulary — *herding*, *consumer inertia*,
  *bounded rationality*, *nudges*. Anchoring and loss aversion were left out
  because the notes do not teach them.
- Where a notes page carries a worked example, the questions use different
  figures throughout: the 1.2.3 latte, the 1.2.5 t-shirts, the 1.2.8 £14/50
  surplus market and the 1.2.9 £2 tax all have fresh contexts and numbers.

**The Edexcel notes for units 1.1 and 1.2 have no `raw-notes/` markdown** — only
1.2.9, 1.2.10 and the 1.3/1.4 topics do. The 16 pages had to be read by
extracting visible text from the HTML. A throwaway extractor that strips
`<script>`, `<nav>` and tags while keeping headings, list items and table cells
was enough, and is worth rebuilding rather than reading 240 KB of markup.

| | |
| --- | --- |
| Answer letters | A 35, B 38, C 30, D 19 (even would be 30.5) |
| Skills | applied-reasoning 68, definition-in-context 25, data-table 19, calculation 10 |
| Difficulty | foundation 21, standard 85, stretch 16 |
| Sketch to solve | 2 |

**D is under-used at batch level** — 19 against an even 30.5. Every set passes
the generator's per-set check (no letter more than 2 from even in its own set),
which is the standard the guide sets, so nothing was changed. The cause is the
one described in §1: alphabetical option order pushes correct answers to early
letters, and correcting it set by set pushes them to B and C rather than to D.
AQA micro finished the same way (D 79 against an even 100). If it is to be
fixed, the fix is to order more option lists by domain sequence while drafting,
not to reshuffle afterwards.

`data-table` at 16% is the best of any batch so far, and `calculation` at 8%
reflects units 1.1 and 1.2 being conceptual for the most part — the arithmetic
lives in 1.2.3, 1.2.5, 1.2.8 and 1.2.9, which supplied 9 of the 10.

**Only 2 sketch items**, against a ~10% target. Units 1.1 and 1.2 are where the
diagrams are first taught rather than applied, and the notes carry the figures on
the page, so most diagram questions would have been asking the student to
redraw something they are looking at. Expect the share to recover in 1.3 and 1.4,
where externality and intervention diagrams have to be constructed.

### Batch 13 — Edexcel Theme 1, units 1.3 and 1.4 (2026-08-01)

6 topics, 41 questions. **Completes Edexcel Theme 1: 22 of 22 topics and 163
questions**, against 157 planned.

All 41 re-derived from the stem alone with **0 mismatches**; every figure
recomputed, including the social cost and social benefit sums, both price-control
gaps read off the schedule, and the two-row welfare table in 1.4.2 Q6.

**Both originality checks came back clean, and the second one is the story.**
Zero shared runs of 8 words or more against either past-paper corpus. Against the
existing 732-question bank, a single 8-gram survived — "in a market with a
negative externality in", shared between our 1.3.2 Q4 and AQA 1.8.4 Q7, which
handle different sub-cases (production against consumption) and ask different
things. That is the terminology, not the question.

**This is the batch where §8 was applied in advance rather than after the fact,
and it worked.** Units 1.3 and 1.4 are the closest twins in the whole project —
AQA 1.8.2 to 1.8.10 plus 1.2.2 carry **53 questions** over the same economics.
Before writing a line, every one of those 53 stems was printed and read. The
angles they already occupy were then avoided outright:

- AQA has the definition stems ("An externality is best defined as…",
  "Market failure occurs when…"), so all six Edexcel sets open on scenarios.
- AQA already uses the factory-air-pollution, solar-panel, worker-training,
  crowded-beach, electronic-tolling, second-hand-car and second-hand-boiler
  contexts. None is reused; Edexcel gets late-night drinking, a lighthouse, a
  village flood barrier, a damp flat, a loft-insulation grant and a nutrition
  label.
- AQA 1.8.9 already covers the alcohol minimum price and the rent maximum price,
  so the Edexcel price-control questions use bottled water in a drought, a
  capped medicine price, and farm price support.

Cost: roughly the time of writing two extra sets. Benefit: one residual 8-gram
across 41 questions, against four rewrites in batch 12. **Do the twin audit
first, every time.**

**Where Edexcel genuinely differs from AQA**, and what it bought:

- Edexcel teaches **merit and demerit goods inside 1.3.2**, where AQA gives them
  their own topic (1.8.5). The definition question sits in the externalities set.
- Edexcel's page labels the diagram **Q1 and Q2**, not Qm and Qopt. The questions
  follow the page.
- Edexcel attaches an **evaluation** to every policy tool — PED, regressive
  incidence, enforcement cost, harm to small firms, subsidy dependency,
  opportunity cost. Four questions test those evaluations, which is a shape the
  AQA sets do not have at all.
- Edexcel's four **reasons to intervene** include earning revenue and supporting
  firms, which AQA does not frame that way. 1.4.1 Q1 tests it.
- Edexcel 1.4.2 makes the point that **a tax can be set too high**, pushing a
  demerit good below its optimal consumption, because such goods still yield some
  value. That became the stretch item (1.4.2 Q3) and has no AQA counterpart.

**Two content defects found and logged, not fixed** — `REVIEW-NOTES.md` N-Q8.
`1-3-4-information-gaps.html` promises adverse selection and moral hazard in its
spec alert, meta description, OG and Twitter cards and JSON-LD, and never
mentions either in the body; `raw-notes/edexcel/1.3.4.md` defines both, so the
content was dropped in conversion. `1-4-2-government-failure.html` promises
regulatory capture the same way and never delivers it. **The question sets were
written to what the bodies actually teach, so neither term is tested.** If the
pages are ever completed, both sets are worth revisiting — the terms are good
material and the AQA sets do not use them either.

| | |
| --- | --- |
| Answer letters | A 8, B 10, C 14, D 9 (even would be 10.25) |
| Skills | applied-reasoning 27, definition-in-context 7, data-table 5, calculation 2 |
| Difficulty | foundation 6, standard 28, stretch 7 |
| Sketch to solve | 1 |

`applied-reasoning` at 66% is the highest of any batch, and it is a property of
the material: market failure and government intervention are argued rather than
calculated, and the two calculations the units support (MSC = MPC + MEC and
MSB = MPB + MEB) are both in 1.3.2. The `stretch` share is also the highest so
far at 17%, because the interesting questions here are all comparative — which
tool fits which failure, and whether intervening beats leaving it alone.

**Letter distribution came out much better than batch 12** — 8 / 10 / 14 / 9
against an even 10.25, with D at 9 rather than badly under. The difference was
deliberate: option lists were ordered by domain sequence while drafting (the
notes' own list of causes, the notes' own order of interventions, consistent
over/under and expansion/contraction grids) rather than alphabetically and then
patched. That is what §1 has recommended all along, and this is the first batch
to follow it from the start.

### Batch 14 — Edexcel Theme 2, unit 2.1 (2026-08-01)

4 topics, 35 questions. **Measures of Economic Performance** — the first macro
questions written for Edexcel.

All 35 re-derived from the stem alone with **0 mismatches**; 28 arithmetic
checks, covering every figure in every calculation and distractor.

**Originality finished clean on both fronts — zero shared 8-word runs against
either past-paper corpus and zero against the whole 773-question bank.** It did
not start that way. The first draft produced **five** collisions with AQA macro,
two of which were effectively the same question with new numbers:

- **2.1.2 Q3** asked for the inflation rate from two CPI values, "to one decimal
  place" — which is AQA 2.1.3 Q8 exactly, down to the rounding instruction.
  Rebuilt to run the calculation *forwards* instead: given the index and the
  rate, find next year's index. AQA has nothing of that shape, and it tests the
  index-points-versus-percentage confusion more directly.
- **2.1.4 Q2** shared "Using Table 1, the current account balance is" with both
  AQA 2.1.2 Q5 and AQA 2.6.3 Q2. Recast to ask whether the account is in deficit
  or surplus and by how much, with the options as deficit/surplus statements
  rather than signed figures.
- 2.1.2 Q4, 2.1.3 Q6 and 2.1.4 Q7 needed stem rewording only.

**"All other things being equal, the most likely…" is now a liability.** One
draft stem using it collided with **20 existing questions** in our own bank and
with the AQA papers. It is stock exam scaffolding and was fine when the bank was
small; at 800 questions it is noise that buries real findings. Prefer a specific
ceteris paribus clause — "without anything else in the labour market changing" —
which is both more original and more precise.

**Where Edexcel differs from AQA on this unit**, and what it bought:

- Edexcel teaches the **income approach** to GDP (wages + rent + interest +
  profit) alongside the expenditure approach, and that both should give the same
  total. AQA uses only the expenditure method. Two questions come from this.
- Edexcel names **disinflation** as a third category beside inflation and
  deflation. AQA does not teach the term at all, and it makes a clean foundation
  question.
- Edexcel gives five named **CPI limitations**, including substitution bias and
  quality change, neither of which AQA tests.
- Edexcel defines the **capital account** as non-produced, non-financial assets —
  land and patents. AQA never tests the capital account, so the patent question
  is entirely free ground.
- Edexcel names **real wage unemployment** as a type; AQA's list does not
  include it.
- Edexcel's page makes the **two-denominator** point explicitly: the
  unemployment rate is measured against the labour force, the employment rate
  against the working-age population. That is Q3.

| | |
| --- | --- |
| Answer letters | A 11, B 9, C 9, D 6 (even would be 8.75) |
| Skills | applied-reasoning 19, calculation 8, definition-in-context 5, data-table 3 |
| Difficulty | foundation 4, standard 26, stretch 5 |
| Sketch to solve | 0 |

**`calculation` at 23% is the highest share of any batch on the site**, against a
~15% target, and it confirms what AQA macro showed: the macro specification is
simply more quantitative. GDP from its components, PPP conversion, CPI from a
basket, index from a rate, a weighted price index, real wages, the unemployment
rate and the current account balance are all genuine arithmetic that unit 2.1
supports naturally.

**No sketch items, by design.** Unit 2.1 is measurement — indicators, indices and
the balance of payments. The AD/AS diagrams start at 2.2, and a sketch item here
would have been invented rather than earned. The same thing happened at AQA 2.1,
and the share recovered from 2.2 onward.

---

## Edexcel Theme 1 — 22 of 22 topics, complete

**Final profile:**

| | |
| --- | --- |
| Topics | 22 of 22 |
| Questions | 163, against 157 planned |
| Answer letters | A 43, B 48, C 44, D 28 (even would be 40.75) |
| Skills | applied-reasoning 95, definition-in-context 32, data-table 24, calculation 12 |
| Difficulty | foundation 27, standard 113, stretch 23 |
| Sketch to solve | 3 |

Theme 1 came in at 8% `data-table` and 7% `calculation`, close to AQA micro and
well below AQA macro. Only units 1.2.3, 1.2.5, 1.2.8, 1.2.9 and 1.3.2 support
real arithmetic; the rest of the theme is conceptual by design.

`D` finished at 28 against an even 40.75. Every individual set passes the
generator's per-set check, and the shortfall is concentrated in the batch 12
sets, which were ordered alphabetically first and rebalanced afterwards. Batch 13
shows the fix works when applied while drafting.

---

## AQA Macroeconomics — 25 of 25 topics, complete

**Final profile:**

| | |
| --- | --- |
| Topics | 25 of 25 |
| Questions | 209 — exactly as planned |
| Answer letters | A 45, B 56, C 59, D 49 (even would be 52.25) |
| Skills | applied-reasoning 111, definition-in-context 49, calculation 26, data-table 23 |
| Difficulty | foundation 28, standard 155, stretch 26 |
| Sketch to solve | 11 |

Macro came in noticeably closer to the target skill mix than micro did:
`calculation` at 12% and `data-table` at 11%, against 6% and 7% across micro.
The specification is simply more quantitative — index numbers, the multiplier,
bond yields, bank ratios, exchange rates and the balance of payments all support
genuine arithmetic. Site-wide the two now sit at 8% each.

`applied-reasoning` finished at 53% against a ~40% target, against 64% in micro.

---

## AQA Macroeconomics — topic list

| Unit | Topic | Questions | State |
| --- | --- | --- | --- |
| 2.1 | 2.1.1 The Objectives of Government Economic Policy | 7 | Done |
| 2.1 | 2.1.2 Macroeconomic Indicators | 8 | Done |
| 2.1 | 2.1.3 Uses of Index Numbers | 10 | Done |
| 2.1 | 2.1.4 Uses of National Income Data | 8 | Done |
| 2.2 | 2.2.1 The Circular Flow of Income | 8 | Done |
| 2.2 | 2.2.2 Aggregate Demand and Aggregate Supply Analysis | 9 | Done |
| 2.2 | 2.2.3 The Determinants of Aggregate Demand | 9 | Done |
| 2.2 | 2.2.4 Aggregate Demand and the Level of Economic Activity | 10 | Done |
| 2.2 | 2.2.5 Determinants of Short-Run Aggregate Supply | 7 | Done |
| 2.2 | 2.2.6 Determinants of Long-Run Aggregate Supply | 7 | Done |
| 2.3 | 2.3.1 Economic Growth and the Economic Cycle | 9 | Done |
| 2.3 | 2.3.2 Employment and Unemployment | 9 | Done |
| 2.3 | 2.3.3 Inflation and Deflation | 10 | Done |
| 2.3 | 2.3.4 Possible Conflicts between Macroeconomic Policy Objectives | 8 | Done |
| 2.4 | 2.4.1 The Structure of Financial Markets and Financial Assets | 8 | Done |
| 2.4 | 2.4.2 Commercial Banks and Investment Banks | 7 | Done |
| 2.4 | 2.4.3 Central Banks and Monetary Policy | 9 | Done |
| 2.4 | 2.4.4 The Regulation of the Financial System | 6 | Done |
| 2.5 | 2.5.1 Fiscal Policy | 9 | Done |
| 2.5 | 2.5.2 Supply-Side Policies | 8 | Done |
| 2.6 | 2.6.1 Globalisation | 7 | Done |
| 2.6 | 2.6.2 Trade | 9 | Done |
| 2.6 | 2.6.3 The Balance of Payments | 9 | Done |
| 2.6 | 2.6.4 Exchange Rate Systems | 10 | Done |
| 2.6 | 2.6.5 Economic Growth and Development | 8 | Done |

---

## AQA Microeconomics — 54 of 54 topics, complete

| Unit | Topic | Questions | State |
| --- | --- | --- | --- |
| 1.1 | 1.1.1 Economic Methodology | 6 | Done |
| 1.1 | 1.1.2 The Nature and Purpose of Economic Activity | 5 | Done |
| 1.1 | 1.1.3 Economic Resources | 5 | Done |
| 1.1 | 1.1.4 Scarcity, Choice and the Allocation of Resources | 6 | Done |
| 1.1 | 1.1.5 Production Possibility Diagrams | 8 | Done |
| 1.2 | 1.2.1 Consumer Behaviour | 7 | Done |
| 1.2 | 1.2.2 Imperfect Information | 6 | Done |
| 1.2 | 1.2.3 Aspects of Behavioural Economic Theory | 8 | Done |
| 1.2 | 1.2.4 Behavioural Economics and Economic Policy | 6 | Done |
| 1.3 | 1.3.1 The Determinants of Demand | 7 | Done |
| 1.3 | 1.3.2 Price, Income and Cross Elasticities of Demand | 10 | Done |
| 1.3 | 1.3.3 The Determinants of Supply | 6 | Done |
| 1.3 | 1.3.4 Price Elasticity of Supply | 8 | Done |
| 1.3 | 1.3.5 The Determination of Equilibrium Market Prices | 9 | Done |
| 1.3 | 1.3.6 The Interrelationship between Markets | 7 | Done |
| 1.4 | 1.4.1 Production and Productivity | 7 | Done |
| 1.4 | 1.4.2 Specialisation, Division of Labour and Exchange | 6 | Done |
| 1.4 | 1.4.3 The Law of Diminishing Returns and Returns to Scale | 9 | Done |
| 1.4 | 1.4.4 Costs of Production | 10 | Done |
| 1.4 | 1.4.5 Economies and Diseconomies of Scale | 8 | Done |
| 1.4 | 1.4.6 Marginal, Average and Total Revenue | 9 | Done |
| 1.4 | 1.4.7 Profit | 8 | Done |
| 1.4 | 1.4.8 Technological Change | 5 | Done |
| 1.5 | 1.5.1 Market Structures | 7 | Done |
| 1.5 | 1.5.2 The Objectives of Firms | 7 | Done |
| 1.5 | 1.5.3 Perfect Competition | 9 | Done |
| 1.5 | 1.5.4 Monopolistic Competition | 7 | Done |
| 1.5 | 1.5.5 Oligopoly | 9 | Done |
| 1.5 | 1.5.6 Monopoly and Monopoly Power | 9 | Done |
| 1.5 | 1.5.7 Price Discrimination | 8 | Done |
| 1.5 | 1.5.8 The Dynamics of Competition | 6 | Done |
| 1.5 | 1.5.9 Contestable and Non-Contestable Markets | 8 | Done |
| 1.5 | 1.5.10 Market Structure and Efficiency | 8 | Done |
| 1.5 | 1.5.11 Consumer and Producer Surplus | 8 | Done |
| 1.6 | 1.6.1 The Demand for Labour, Marginal Productivity Theory | 9 | Done |
| 1.6 | 1.6.2 Influences upon the Supply of Labour | 7 | Done |
| 1.6 | 1.6.3 Wage Determination: Competitive Labour Markets | 8 | Done |
| 1.6 | 1.6.4 Wage Determination: Imperfect Labour Markets | 8 | Done |
| 1.6 | 1.6.5 The Influence of Trade Unions | 7 | Done |
| 1.6 | 1.6.6 The National Minimum Wage | 8 | Done |
| 1.6 | 1.6.7 Discrimination in the Labour Market | 6 | Done |
| 1.7 | 1.7.1 The Distribution of Income and Wealth | 8 | Done |
| 1.7 | 1.7.2 The Problem of Poverty | 7 | Done |
| 1.7 | 1.7.3 Government Policies on Poverty and Distribution | 7 | Done |
| 1.8 | 1.8.1 How Markets and Prices Allocate Resources | 7 | Done |
| 1.8 | 1.8.2 The Meaning of Market Failure | 6 | Done |
| 1.8 | 1.8.3 Public, Private and Quasi-Public Goods | 8 | Done |
| 1.8 | 1.8.4 Positive and Negative Externalities | 10 | Done |
| 1.8 | 1.8.5 Merit and Demerit Goods | 7 | Done |
| 1.8 | 1.8.6 Market Imperfections | 6 | Done |
| 1.8 | 1.8.7 Competition Policy | 7 | Done |
| 1.8 | 1.8.8 Public Ownership, Privatisation, Regulation | 7 | Done |
| 1.8 | 1.8.9 Government Intervention in Markets | 9 | Done |
| 1.8 | 1.8.10 Government Failure | 7 | Done |
