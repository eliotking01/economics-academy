# QUESTIONS_PROGRESS

Batch state and working notes for the free practice questions. The authoring
standard is `QUESTIONS_GUIDE.md`; this file records what is done, what is next,
and everything learned along the way, so work can resume cleanly in a new
session.

**Live: 54 topics, 401 questions. AQA Microeconomics is complete.**
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

### AQA Macroeconomics — 25 topics, 209 questions planned

| Unit | Topics and planned counts |
| --- | --- |
| 2.1 | 2.1.1 (7) · 2.1.2 (8) · 2.1.3 (10) · 2.1.4 (8) — 33 |
| 2.2 | 2.2.1 (8) · 2.2.2 (9) · 2.2.3 (9) · 2.2.4 (10) · 2.2.5 (7) · 2.2.6 (7) — 50 |
| 2.3 | 2.3.1 (9) · 2.3.2 (9) · 2.3.3 (10) · 2.3.4 (8) — 36 |
| 2.4 | 2.4.1 (8) · 2.4.2 (7) · 2.4.3 (9) · 2.4.4 (6) — 30 |
| 2.5 | 2.5.1 (9) · 2.5.2 (8) — 17 |
| 2.6 | 2.6.1 (7) · 2.6.2 (9) · 2.6.3 (9) · 2.6.4 (10) · 2.6.5 (8) — 43 |

Expect the **calculation share to recover here**: index numbers, real vs
nominal, the multiplier and exchange rates are all genuinely arithmetic.

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
  bring the site-wide ratio closer to target.
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
