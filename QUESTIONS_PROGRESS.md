# QUESTIONS_PROGRESS

Batch state and working notes for the free practice questions. The authoring
standard is `QUESTIONS_GUIDE.md`; this file records what is done, what is next,
and everything learned along the way, so work can resume cleanly in a new
session.

**Live: 74 topics, 567 questions. AQA Microeconomics is complete; AQA
Macroeconomics units 2.1 to 2.5 are done, leaving only 2.6.**
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

### AQA Macroeconomics — 5 topics, 43 questions still to write

Units 2.1 to 2.5 are done (batches 6 to 10). Only unit 2.6 remains:

| Unit | Topics and planned counts |
| --- | --- |
| 2.6 | 2.6.1 (7) · 2.6.2 (9) · 2.6.3 (9) · 2.6.4 (10) · 2.6.5 (8) — 43 |

Expect the **calculation share to recover here**: index numbers, real vs
nominal, the multiplier and exchange rates are all genuinely arithmetic. Unit
2.1 confirmed this — it came in at 24% `calculation` against a ~15% target.

### Edexcel — 87 topics, 662 questions planned

| Theme | Topics | Questions |
| --- | --- | --- |
| Theme 1 | 22 | 157 |
| Theme 2 | 24 | 185 |
| Theme 3 | 20 | 157 |
| Theme 4 | 21 | 163 |

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

---

## AQA Macroeconomics — 20 of 25 topics

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
