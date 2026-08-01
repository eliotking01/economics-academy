# QUESTIONS_PROGRESS

Batch state and working notes for the free practice questions. The authoring
standard is `QUESTIONS_GUIDE.md`; this file records what is done, what is next,
and everything learned along the way, so work can resume cleanly in a new
session.

**COMPLETE. 166 of 166 topics, 1,268 questions**, against ~1,272 planned. Every
board and every theme is finished: AQA Microeconomics and Macroeconomics, and
Edexcel Themes 1, 2, 3 and 4. **No topic remains.**

**Branch:** `feature/topic-questions`, branched from `main`.
**Nothing has been pushed.** `main` auto-publishes, so pushing needs explicit
approval — see `CLAUDE.md`.

---

## Read this first if you are resuming

**State at completion (2026-08-01).** Branch `feature/topic-questions`, **40
commits ahead of `main`**, working tree clean, **nothing pushed**. All 166 topics
and 1,268 questions are done, across thirty batches. `main` auto-publishes, so
the branch goes nowhere until the site owner says so.

**There is no remaining authoring work.** What is left is four decisions, all of
which belong to the site owner and three of which were deliberately deferred to
this point:

1. **Push the branch.** Forty commits, nothing published yet.
2. **The nav sub-menu.** All five board index pages now exist and are complete,
   so the two-level dropdown can be restored. It is a change to every page on the
   site, so it needs approval. See **Open items**.
3. **Monopsonistic exploitation.** The site owner asked for this to be raised at
   the end of the run. It is now the end of the run. See **Open items**.
4. **The written-response extension.** Proposed in the original brief, never
   approved, never built. See **Open items**.

Beyond those, `REVIEW-NOTES.md` carries **thirteen notes-page findings** turned
up while writing the questions (N-Q8, N-Q10 to N-Q20). None of them blocks
anything and all need an explicit instruction before any page is touched.

### If you are extending this rather than resuming it

Read these four things, in this order, before writing anything:

1. `QUESTIONS_GUIDE.md` — the authoring standard. Non-negotiable.
2. This file's **Recurring problems** section. Nine numbered failure modes, every
   one of which recurred across multiple batches. §8 (cross-board duplication)
   and §9 (concept-grep) are the two that decide how a batch turns out.
3. **The whole project** section at the head of the batch record — the site-wide
   profile, what it misses and why.
4. `scripts/build_questions.py` — the generator and validator. It refuses to
   write a page from a bad source, so treat `--check` as the first gate.

### The shape of a batch, as it has settled

Every batch since 21 has run the same way, and the order matters:

1. `BASE=$(git rev-parse HEAD)` before touching anything.
2. **Print the AQA twin set in full**, immediately before writing each Edexcel
   set — not all of them at the start of a multi-topic batch.
3. **Concept-grep the bank** for the four or five ideas the set will turn on
   (§9). This decides how many questions the set can honestly carry.
4. Read the **published** notes page, not the raw markdown, and write only to
   what its body actually teaches.
5. Author into a throwaway Python helper that asserts the mechanical rules at
   write time (see **Authoring efficiently**).
6. `--check`, then the originality script, then fix, then build.
7. **Cold re-solve every question from the stem alone**, then diff against the
   recorded keys. This has caught a real defect in three of the last seven
   batches.
8. Full verification suite, progress record, commit.

**Sets come in at four to ten questions, and the number is a finding rather than
a target.** Where AQA has already taken the ground, five honest questions beat
eight with three ports in them. Five of Theme 3's twenty sets are five or six
questions for exactly this reason.

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
git diff $BASE -- revision-notes/ templates/ js/ css/ | grep '^-[^-]'
#   ^ must print nothing. Any output means a pre-existing line was changed.
#   Note: run this WITHOUT sitemap.xml. On a different calendar day the sitemap
#   block is rewritten with a new lastmod and every URL line shows as removed
#   and re-added — benign, but it buries the check that matters. See batch 11.
```

Then run the **cold re-solve** (see below), fix what it finds, rebuild, and
commit.

### The two originality scripts, which are not committed

Both live in the session scratchpad and have to be rebuilt each time. They are
short, and the batch records describe what they do.

- **`orig.py`** — shingles the new sets against (a) the AQA past-paper corpus,
  (b) the Edexcel past-paper corpus, and (c) every other question in
  `questions-data/`, and separately compares numeric option sets against the
  option blocks extracted from the papers. Stem-only for the intra-bank pass,
  with the elasticity template and stock scaffolding filtered out first.
- **`pagetext.py`** — extracts the visible text of a notes page, keeping
  headings, list items, table cells and figure captions. Needed because the
  published pages differ from `raw-notes/edexcel/`, sometimes substantially.

**The past-paper corpora are worth locating rather than re-extracting.** They
were built once with a four-line Swift/PDFKit script (§7) and take a couple of
minutes to regenerate; copies have been kept in the session scratchpads as
`aqa-all.txt` (45 papers, 945 KB) and `edexcel-all.txt` (40 papers, 5.8 MB).

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

### 9. Shingling misses collisions that share no wording — grep by concept too

**New in batch 21.** The 8-gram check finds questions that share *phrasing*. It
cannot find two questions that ask the same thing in different words, and on the
micro topics that is now the more common failure.

Batch 21 drafted "A firm is productively efficient when it produces at the output
where… average cost is at its minimum". That is **AQA 1.5.10 Q2 in substance and
almost in wording**, and the shingle check returned nothing for it, because the
stems are phrased differently and the option sets share no runs. It was found by
grepping the whole bank for `productive efficiency`.

**Do both, every batch.** Before writing a set, list the four or five ideas it
will turn on and search `questions-data/` for each:

```python
for f in pathlib.Path('questions-data').rglob('*.json'):
    for q in json.loads(f.read_text())['questions']:
        if re.search(TERM, " ".join([q['stem'], *q['options'].values()]), re.I):
            print(spec, i, q['answer'], q['stem'][:100])
```

It takes a minute and it catches a class of duplication the shingle never will.
In batch 21 the same search also confirmed that the **shut-down rules** and the
**SRAC/LRAC envelope** appeared nowhere in 1,007 questions, which is how those
became the backbone of the unit rather than a guess.

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

**None.** All 166 topics are written, verified and committed. The thirty-batch
plan ran to completion:

```
batches 1-5    AQA Microeconomics, units 1.1 to 1.8      54 topics, 401 questions
batches 6-11   AQA Macroeconomics, units 2.1 to 2.6      25 topics, 209 questions
batches 12-13  Edexcel Theme 1                           22 topics, 166 questions
batches 14-19  Edexcel Theme 2                           24 topics, 198 questions
batches 20-25  Edexcel Theme 3                           20 topics, 148 questions
batches 26-30  Edexcel Theme 4                           21 topics, 146 questions
```

What is left is the four decisions listed at the head of this file: pushing the
branch, the nav sub-menu, monopsonistic exploitation and the written-response
extension. The sections below are kept because they record how the work was done
and what a future session would need to repeat it — the twin maps, the occupied
ground and the failure modes are all still accurate.

---

### The Theme 3 twin map, kept for reference

**Theme 3 is the closest twin of the whole project — closer than Theme 1's
market failure units were.** It is AQA micro units 1.4, 1.5 and 1.6 almost
topic for topic — **201 questions** between them, plus 1.8.7 and 1.8.8 on
competition policy. The twin map:

| Edexcel | AQA twin | AQA questions |
| --- | --- | --- |
| ~~3.1.1 sizes and types of firms~~ | 1.5.1, 1.4.5, 1.5.2 — **done, batch 20** | — |
| ~~3.1.2 business growth~~ | 1.8.7 competition policy — **done, batch 20** | — |
| ~~3.1.3 demergers~~ | none — **done, batch 20** | — |
| ~~3.2.1 business objectives~~ | 1.5.2, 1.4.6, 1.4.7 — **done, batch 20** | — |
| ~~3.3.1 revenue~~ | 1.4.6 — **done, batch 21** | — |
| ~~3.3.2 costs~~ | 1.4.4, 1.4.3 — **done, batch 21** | — |
| ~~3.3.3 economies and diseconomies of scale~~ | 1.4.5 — **done, batch 21** | — |
| ~~3.3.4 normal and supernormal profit~~ | 1.4.7 — **done, batch 21** | — |
| 3.4.1 efficiency | 1.5.10 market structure and efficiency | 8 |
| 3.4.2–3.4.5 | 1.5.3, 1.5.4, 1.5.5, 1.5.6, 1.5.7 | 42 |
| 3.4.6 monopsony | 1.6.4 imperfect labour markets (partly) | 8 |
| 3.4.7 contestability | 1.5.9 contestable markets | 8 |
| 3.5.1–3.5.3 labour | 1.6.1, 1.6.2, 1.6.3 | 24 |
| 3.6.1–3.6.2 intervention | 1.8.7, 1.8.8 competition policy | 14 |

**Print the AQA twin before writing each Edexcel set, without exception.**
Batch 13 proved the value of doing this in advance (one residual 8-gram over 41
questions) and batch 12 proved the cost of skipping it (four rewrites). At this
overlap density, doing it afterwards will not be recoverable.

Unlike Themes 1 and 2, Theme 3 has **real arithmetic on almost every page** —
revenue and cost schedules, average and marginal calculations, concentration
ratios, profit. That is the best chance the site has left to pull the `calculation`
share back towards its ~15% target from the current 8%. Plan the calculation
items deliberately, and note that AQA's 1.4.4 and 1.4.6 already use most of the
standard schedule archetypes, so the numbers and the framings both have to be new.

**`raw-notes/edexcel/` has markdown for all twenty Theme 3 topics** (3.2 is a
single file covering 3.2.1). Read it for speed, then diff against the published
page.

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

**All four now need the site owner. The run is finished, so the three that were
deferred to its end are due.**

- **Push the branch — decision 1.** Forty commits on `feature/topic-questions`,
  nothing published. `main` auto-publishes to economicsacademy.co.uk, so this is
  the decision that makes 1,268 questions live.
- **Monopsonistic exploitation — decision 2, deferred by the site owner to the
  end of the run, which is now.** `REVIEW-NOTES.md` N-Q15 was fixed on 2026-08-01: the 3.4.6 spec
  alert and its four metadata copies no longer promise the monopsony labour
  market diagram, minimum wages or trade unions, since those are taught on 3.5.3.
  **One part of that finding is still open.** *Monopsonistic exploitation* — the
  gap between a worker's marginal revenue product and the wage a monopsonist
  actually pays — appears on **neither** page. It is no longer claimed anywhere,
  so both pages are accurate as they stand, but the concept itself is missing
  from the site. Closing it properly means adding the term to
  `3-5-3-wage-determination`, which already teaches the mechanism without naming
  it. The site owner has asked to **resolve this at the end of the current run of
  work**. Note that 3.5.3 Q2 already tests the mechanism — where the monopsonist's
  wage is read from — so a question would not need rewriting, only the notes page.
  The change is one sentence naming the concept the page already explains.
- **Nav sub-menu — decision 3, needs the site owner's call.** `templates/header.html` carries
  a top-level **Practice Questions** entry only. The two-level board dropdown
  that Revision Notes and Past Papers have was written and then deliberately
  removed, because it would have pointed at five board index pages that did not
  yet exist. A comment marks the insertion point. **All five now exist, and four
  are complete and final** — both AQA indexes, `edexcel-theme-1` (22 of 22),
  `edexcel-theme-2` (24 of 24), `edexcel-theme-3` (20 of 20) and
  `edexcel-theme-4` (21 of 21). **All five are now complete and final, so the
  reason the dropdown was held back no longer applies.** It is still a nav change
  on every page, so it needs approval before it goes in.
- **Hub and board index density.** Both now list all 166 topics across the five
  board indexes. Nothing further to do.
- **Skill mix.** `applied-reasoning` runs at 62% site-wide against a ~40% target
  and `calculation` at 8% against ~15%. This is largely a property of the
  specifications — AQA micro units 1.1, 1.2, 1.5, 1.7 and 1.8 are conceptual
  almost throughout, and AQA micro's 401 questions dominate the total. Macro
  pulled the right way: AQA macro finished at 12% `calculation`, Edexcel Theme 2
  at 11%. Theme 3 was the last real chance to move it and shifted the total by
  under a point, and Theme 4 finished at 5% calculation — the lowest of any
  theme, and unavoidable on a trade-and-development theme whose arithmetic AQA
  macro had already used. **Recorded rather than corrected. It is now final**, and
  changing it would mean rewriting sets that pass every other check.
- **Written-response extension — decision 4.** Proposed in the original brief but
  **not built** and not approved: 1–2 short written questions per topic with
  indicative-content model answers behind `<details>`, plus a marking-service
  call to action. Needs the site owner's sign-off before any work starts.
- **Site-wide issues found but not fixed** are logged in `REVIEW-NOTES.md`, per
  `CLAUDE.md`: the `navPanel` `aria-hidden` bug (the only remaining
  accessibility failure on any page), breadcrumb contrast in `css/main.css`, and
  web-font layout shift.

### Notes-page findings raised while writing the questions

All are in `REVIEW-NOTES.md` with the evidence. **None blocks any batch.** They
are listed here so a new session knows they exist without reading that file end
to end.

| Entry | Page | What is wrong | Weight |
| --- | --- | --- | --- |
| N-Q8 | 9 pages, Themes 1–2 | Alerts promise concepts the bodies never deliver | Questions written anyway, per the batch 16 instruction |
| N-Q12 | `3-1-1-sizes-types-of-firms` | Promises private and public limited companies; body has neither | Not tested |
| N-Q13 | `3-3-4` | Promises explicit and implicit costs; never names them, though it teaches the idea | Tested via a calculation instead |
| N-Q14 | `3-3-2` | LRAC envelope stated as touching the SRAC minima — true only at MES | Question reworded to avoid it |
| **N-Q15** | `3-4-6-monopsony` | **Fixed 2026-08-01.** Alert and four metadata copies rewritten | One part still open — see below |
| N-Q16 | `4-1-3-pattern-of-trade` | Promises deindustrialisation; describes it, never names it | Not tested; one-word fix |
| **N-Q17** | `4-1-9` | Promises export market share as a measure; body omits it entirely | **`4.1.9` Q8 depends on it** |
| N-Q18 | `4-2-1` | Promises redistribution and social protection as policy responses; body has no policy section | Not tested; set written to the body |
| N-Q19 | `4-4-1` | Promises risk spreading, liquidity provision and financial intermediation; body has none of the three | Not tested; set written to the body |
| N-Q20 | `4-5-2`, plus soft cases on `4-5-3` and `4-5-4` | Promises tax incidence and the principles of a good tax system; body has neither | Not tested; incidence is taught on `1-2-9` |
| N-Q10 | 13 pages, all boards | Duplicate or non-sequential figure numbers | Cosmetic; already listed in full |

**N-Q17 is the one to act on first if any of these are taken up.** A question is
already live that the page does not support, written under the batch 16 policy of
covering advertised concepts and bringing the notes up afterwards. The paragraph
needed is short and the wording exists in the Q8 model answer.

**Audit coverage — both checks are now complete site-wide.** The N-Q8 spec-alert
check has been run over all 166 topic pages, and the N-Q10 figure-number check
re-run over all of them. Nothing further is outstanding on either. Note the
script's blind spot recorded with N-Q19: the end-of-notes question block sits
below the spec alert, so its teaser can match a concept the body never teaches.
Print the matching context and discard hits inside `notes-questions-cta`. The N-Q10 figure-number check is
**finished site-wide**: it was re-run over the whole of Theme 4 during batch 28
and units 4.2 to 4.5 are clean, so nothing beyond the thirteen pages already
listed needs renumbering. Both scripts are in `REVIEW-NOTES.md`, along with the
warning that the automated pass produces false positives at roughly one in three
and every hit must be read before it is recorded.

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

### Batch 30 — Edexcel Theme 4, unit 4.5 (2026-08-01)

4 topics, 28 questions. Public expenditure, taxation, public sector finances, and
macroeconomic policies in a global context. **This completes the project: 166 of
166 topics and 1,268 questions.**

All 28 re-derived from the stem alone with **0 mismatches**; the Laffer
calculation recomputed with every distractor value.

**Originality clean on all three fronts at the first attempt** — no rewrites, the
third batch running and the fifth in six.

**The fiscal material was the most heavily occupied of any unit on the site, and
the concept-grep is what made a batch of 28 possible at all.** AQA 2.5.1 alone
owns the deficit-and-debt flow/stock distinction, a budget position table, the
state pension as a transfer payment, why VAT is regressive, classifying a tax
from a table of households, crowding out, the structural deficit, the Laffer
curve and Ricardian equivalence. My own Edexcel 2.6.2 Q10 owns the arithmetic of
a deficit accumulating into debt, and 2.6.3 owns ten supply-side questions.
Automatic stabilisers are taken twice over — AQA 2.2.3 Q6 and Edexcel 2.2.4 Q1.

What the grep found free was everything Edexcel adds around that core:

| Concept | Hits before this batch |
| --- | --- |
| current against capital expenditure | 0 |
| demographic pressure on spending | 0 |
| public spending as a share of GDP | 0 |
| proportional taxation | 0 |
| brain drain and the mobile tax base | 0 |
| credit ratings | 0 |
| financing a deficit by creating money | 0 |
| debt restructuring | 0 |
| transfer pricing | 0 |
| regulatory arbitrage | 0 |
| international policy coordination, the OECD | 0 |
| forecasting error and uncontrollable shocks | 0 |

**The two best questions in the batch are both about the difference between an
asset and a bill.** 4.5.2 Q1 puts the Laffer curve into numbers for the first
time on the site — a rate rising from 40% to 50% against a base falling from
£150bn to £100bn, so revenue falls from £60bn to £50bn, with the static answer
(£75bn, a £15bn rise) offered as the trap. And 4.5.3 Q5 sets two governments
borrowing the same sum, one for railways and one for this year's pay bill, and
asks why intergenerational equity treats them differently: both pass on the debt,
only one passes on anything to show for it.

**4.5.4 is the largest set of genuinely new ground in Theme 4.** Transfer
pricing, regulatory arbitrage, common minimum tax rates agreed internationally,
debt restructuring, austerity being partly self-defeating in a downturn, and the
closing question of the whole project — a budget built on a 2% growth forecast
when growth comes in at 0.2%, which is the notes' own point about policymakers
acting on information that can prove wrong.

| | |
| --- | --- |
| Answer letters | A 8, B 9, C 5, D 6 (even would be 7) |
| Skills | applied-reasoning 20, data-table 4, definition-in-context 3, calculation 1 |
| Difficulty | foundation 1, standard 23, stretch 4 |
| Sketch to solve | 0 |

**No sketch items.** The unit's one diagram is the Laffer curve on the 4.5.2
page, and 4.5.2 Q1 and Q8 work the two facts it encodes — the peak and the
right-hand endpoint — arithmetically instead, which is the harder skill.

**Notes audit run at the same time, completing the sweep.** One new finding,
**N-Q20**: `4-5-2` promises tax incidence and the principles of a good tax
system, and has neither — though tax incidence is taught on `1-2-9` and already
tested there, so a cross-reference would settle half of it. Two soft cases
recorded alongside it: `4-5-3` promises the options for fiscal consolidation,
which are taught on `4-5-4`; and `4-5-4` promises capital mobility, which is
taught on `4-1-1`. No question depends on any of it.

**Both notes audits are now complete across all 166 topic pages** — N-Q8 for
over-promising spec alerts and N-Q10 for figure numbering.

### Batch 29 — Edexcel Theme 4, unit 4.4 (2026-08-01)

3 topics, 21 questions. Financial markets, market failure in the financial
sector, and central banks.

All 21 re-derived from the stem alone with **0 mismatches**.

**This was billed as the hardest batch remaining and it was not close to it.**
The prediction was that AQA 2.4.1 to 2.4.4's 30 questions would leave 4.4.3 with
almost nothing. What the concept-grep actually found was that AQA and Edexcel
approach the same unit from opposite ends, and barely meet:

| Concept | Hits before this batch |
| --- | --- |
| forward markets, futures, hedging | 0 |
| financial intermediation | 0 |
| market bubbles | 0 |
| market rigging, LIBOR, manipulation | 0 |
| bailouts and the taxpayer | 0 |
| banker to the government | 0 |
| the PRA, the FPC, macroprudential, loan-to-value | 0 |
| stress tests | 0 |
| the zero lower bound | 0 |
| the 2008 financial crisis | 0 |

AQA's unit 2.4 is a **money and banking** unit — narrow and broad money, the
money market against the capital market, bond yields, balance sheets, credit
creation, liquidity ratios. Edexcel's 4.4 is a **functions and failures** unit.
The two overlap on precisely four things, and all four were left alone: the
lender of last resort (AQA 2.4.3 Q1), the mechanics and purpose of QE (2.4.3 Q5
and Q6), naming systemic risk (2.4.4 Q5) and naming moral hazard (2.4.4 Q4).

**Two of those four are worth recording, because they cost real questions.**

- **The lender of last resort is not tested at all**, despite being one of the
  four functions on the 4.4.3 page. AQA 2.4.3 Q1 asks it directly, and the only
  distinct angle left — that standing ready to rescue banks encourages them to
  take risks — is moral hazard, which AQA 2.4.4 Q4 also owns. Two occupied
  approaches to one function; it appears in this batch only as a distractor and
  in a model answer.
- **Moral hazard is unusable as an answer anywhere in unit 4.4**, which is
  awkward on a page that gives it a heading. AQA owns the bailout version and my
  own Edexcel 1.3.4 Q7 owns the insurance version — Edexcel's two examples,
  exactly. So 4.4.2 covers the other four causes of failure and leaves it.

**Originality clean on all three fronts at the first attempt**, with no rewrites
— the second batch running, and the fourth in five.

**4.4.2 is the strongest set in the batch**, and the reason is that Edexcel's
framing of financial market failure is genuinely its own. Nine questions came out
of adverse selection driving the safest borrowers out of a credit market,
information gaps in high-cost lending and the disclosure remedy for them, the
externality argument for regulating banks more heavily than other firms, bubbles
and the 95% mortgage that turns one into a banking crisis, the LIBOR-style
benchmark manipulation and why it damages contracts across an economy, the run
that brings down a solvent bank, and the equity objection to a rescue.

**A length-check finding worth knowing.** 4.4.3 Q3 failed the option-length rule
because "The Prudential Regulation Authority" is 36 characters and "The Financial
Policy Committee" is 31 — a difference that carries no signal whatever, since
both are just the names of the bodies. The guide's script exempts option sets
whose longest entry is under 30 characters for exactly this reason, and proper
nouns sit just above the line. **The question was restructured rather than the
name mangled**: the stem now asks for the FPC via its system-wide remit, and the
PRA's stress-testing content moved into its own applied question, which is a
better set than the original in any case.

| | |
| --- | --- |
| Answer letters | A 7, B 5, C 6, D 3 (even would be 5.25) |
| Skills | applied-reasoning 12, definition-in-context 6, data-table 3 |
| Difficulty | foundation 3, standard 17, stretch 1 |
| Sketch to solve | 0 |

**No calculation items, and no sketch items.** Unit 4.4's arithmetic — bond
yields, the credit multiplier, liquidity and capital ratios — is entirely AQA
2.4.1, 2.4.2 and 2.4.4's, all of it already used, and Edexcel's pages carry no
figures of their own to build new ones from. The nearest this batch comes is
4.4.2 Q5, where a 95% mortgage against a one-third fall in prices has to be
turned into negative equity; it is tagged `applied-reasoning` because the
arithmetic is in the model answer rather than the stem. There is no diagram
anywhere in the unit.

**Notes audit run at the same time.** One new finding, **N-Q19**: `4-4-1`
promises the channelling of savings into investment, risk spreading, liquidity
provision and financial intermediation, and delivers the first in substance and
none of the other three — "liquid" and "intermediat" do not appear on the page at
all. No question depends on the missing material.

**A trap in the N-Q8 script, now that notes pages link to question sets.** The
script strips everything above the spec alert to avoid matching the metadata
copies, but the end-of-notes block sits *below* it, and its teaser is prose about
the topic. On 4.4.1 the phrase `channelling savings into investment` matched —
and the only occurrence on the page was in the block this project appended.
**Print the matching context rather than a boolean, and discard hits inside
`notes-questions-cta`.** Recorded in `REVIEW-NOTES.md` alongside N-Q19.

### Batch 28 — Edexcel Theme 4, units 4.2 and 4.3 (2026-08-01)

5 topics, 38 questions. Poverty, inequality, and the whole of unit 4.3 —
measuring development, the factors behind it, and the strategies for it.

All 38 re-derived from the stem alone with **0 mismatches**; the savings gap, the
Gini coefficient and both relative poverty lines recomputed with every distractor
value.

**Batch 27's verification pass was re-run first, in full, and came back clean** —
27 of 27 re-solved cold, both past-paper corpora and the intra-bank shingle clear
at every n-gram length, no numeric option-set flag, no option-length flag, and a
rebuild that reproduced the committed pages byte for byte.

**The two units could hardly have been less alike, and the concept-grep predicted
it exactly.**

- **Unit 4.2 is the most heavily occupied ground left on the site.** AQA 1.7.1,
  1.7.2 and 1.7.3 carry 22 questions, and between them they own the income/wealth
  flow-and-stock distinction, the Lorenz curve, a Gini coefficient of 0, a Gini
  comparison table, the 60%-of-median definition *and* its calculation, income
  doubling, the poverty trap, the consequences of poverty, progressive taxation,
  means-testing, inheritance tax and the incentive argument for inequality. Six
  and seven questions respectively is what honestly remained.
- **Unit 4.3 is almost virgin ground.** AQA 2.6.5 has eight questions in total,
  and outside them the grep returned **zero hits across 1,181 questions** for the
  Kuznets curve, capitalism, quintile shares, composite and single indicators,
  the MPI, the IHDI, infant mortality, clean water, primary product dependency,
  microfinance, aid, debt relief, Fairtrade, tourism, the Lewis model, buffer
  stocks, the World Bank, the IMF, NGOs, joint ventures, structural adjustment
  and profit repatriation. Twenty-five questions came out of that list.

**What was free in unit 4.2, and it is a short list.** The moving relative line
tracked across two years — a household £2,400 better off and no further out of
poverty, because the median rose by £4,000 — which is a different question from
AQA's one-step 60% calculation. The Gini coefficient computed from the areas,
A ÷ (A + B), which AQA never does. Cumulative quintile shares, where the trap is
reading the bottom-80% figure as the top-20% share. Both halves of the Kuznets
curve. Capitalism's distributive rule. And the **cost** side of the inequality
trade-off — extreme inequality demotivating, and social immobility — where AQA
1.7.1 Q7 owns the benefit side.

**One collision, caught by the shingle and reworded.** 4.2.1 Q1 opened "counts a
household as being in relative poverty when its income is below 60% of median
household income", which is AQA 1.7.2 Q2's stem and correct option run together —
nine shared words. The definition is unavoidable in a question that needs the
line; the *phrasing* of it was not. Rewritten to "draws its relative poverty line
at 60% of the median", and clean afterwards.

**Everything else was clean at the first attempt** on all three fronts: zero
shared 8-word runs against either past-paper corpus, and no numeric option-set
flag. That is now three batches running.

**Two adjacencies judged and kept, both recorded so they are not re-litigated:**

- 4.3.3 Q1 (three deregulating measures → market-orientated strategies) against
  Edexcel 2.6.3 Q3 (what makes a supply-side policy market-based). Same
  underlying distinction, different specification area, different question shape
  — one classifies concrete measures, the other defines the category by its
  mechanism. Edexcel teaches both, under different names.
- 4.3.1 Q6 (6% growth for a decade with every non-income indicator flat) against
  AQA 2.6.5 Q1 and Edexcel 2.5.4 Q3. AQA's is the definition; Edexcel 2.5.4's is
  about the distribution of growth's benefits. This one is about growth failing
  to move health, schooling and water at all, which is the point of the 4.3.1
  page.

**The best question in the batch is 4.3.3 Q3**, the buffer stock. Year 1's
harvest is large and the price would fall to £150; Year 2's fails and it would
reach £260; the target is £200. The rule — buy in the good years, release in the
bad — falls straight out of the table, and the two inverted options are exactly
what a student who has memorised "the agency intervenes" without the direction
will pick.

| | |
| --- | --- |
| Answer letters | A 9, B 12, C 11, D 6 (even would be 9.5) |
| Skills | applied-reasoning 23, definition-in-context 7, data-table 5, calculation 3 |
| Difficulty | foundation 5, standard 31, stretch 2 |
| Sketch to solve | 0 |

**No sketch items.** Unit 4.2's two diagrams are the Lorenz curve and the Kuznets
curve, and both are printed on the 4.2.2 page; 4.2.2 Q1 and Q2 ask the student to
work *from* them numerically instead, which is the harder skill and the one the
page supports. Unit 4.3's only diagram is the buffer stock, which 4.3.3 Q3 uses
as a table.

**Notes audit run at the same time.** N-Q8 checked over all five pages, N-Q10
re-run over units 4.2 to 4.5. One new finding, **N-Q18**: `4-2-1` promises
"redistribution and social protection as policy responses" in its spec alert and
four metadata copies, and the body has no policy section at all — "social
protection" appears nowhere in it. Unlike N-Q17, no question depends on it, since
the 4.2.1 set was written strictly to the body. **N-Q10 came back clean across
all twelve pages of units 4.2 to 4.5, which closes the figure-number audit
site-wide.**

### Batch 27 — Edexcel Theme 4, units 4.1.6 to 4.1.9 (2026-08-01)

4 topics, 27 questions. **Completes unit 4.1** — restrictions on free trade, the
balance of payments, exchange rates, and international competitiveness.

All 27 re-derived from the stem alone with **0 mismatches**.

**This was flagged in advance as the tightest batch remaining, and it was — but
not evenly.** The four topics split cleanly into two saturated and two open:

- **4.1.7 balance of payments is the most heavily occupied topic on the site.**
  AQA 2.6.3 has nine questions and my own Edexcel 2.1.4 has eight, and between
  them they cover the current account components, the balance calculation, the
  accounting identity, appreciation worsening the current account,
  expenditure-switching and expenditure-reducing policies, and financing a deficit
  by selling assets. **Seventeen questions on one topic before this batch
  started.** What remained is definitional detail nobody had used: remittances as
  secondary income, debt forgiveness as the capital account item, FDI against
  portfolio investment, and — the one genuinely good question — that **the size
  of a deficit matters less than the quality of what finances it**.
- **4.1.8 exchange rates is nearly as bad.** AQA 2.6.4's ten questions own
  depreciation against devaluation, the interest-rate sketch, Marshall-Lerner, a
  currency conversion, the J-curve, imported inflation, the cost of a fixed rate,
  a table of depreciation causes, currency unions and competitive devaluation.
  The concept-grep found the gaps: **managed floats returned zero hits**, as did
  central bank intervention by buying and selling its own currency, speculation as
  a self-fulfilling force, and reserves running out as the constraint on defending
  a peg. Six questions, all from that list.
- **4.1.6 and 4.1.9 were wide open.** Quotas, non-tariff barriers and unit labour
  costs all returned **zero hits across 1,154 questions**. AQA 2.6.2 has the
  tariff sketch, infant industries and the inelastic-demand evaluation, and
  nothing else on protection; it has no topic on competitiveness at all.

**One real collision, caught by the shingle and rebuilt.** 4.1.9 Q6 shared a
nine-word run with AQA 2.6.3 Q4 — "the most likely effect on its current account
is that it" — and, worse, the same answer shape, "Worsens, ... exports ...
abroad". Two questions from different topics converging on the same sentence and
the same conclusion is a port however it arose. Rebuilt on the **employment**
consequence of lost competitiveness instead, which Edexcel lists separately and
which nothing in the bank covered.

**Two more "all other things being equal" flags**, in 4.1.8 Q4 and Q5. Batch 14
recorded that phrase as a liability at bank scale and it keeps proving so —
it now collides with something almost every time it is used. Both reworded, to
"Taken on its own" and "With no other change in the market". **Stop reaching for
it.**

**The best question in the batch is 4.1.9 Q1**, and it is worth recording why.
Country A spends £4.8m on labour for 600 units; Country B spends £7.0m for 1,000.
B has the larger wage bill and is the more competitive producer, because its unit
labour cost is £7,000 against A's £8,000. The whole point of the measure is that a
total wage bill says nothing at all on its own — and the arithmetic makes that
far better than any definition would.

| | |
| --- | --- |
| Answer letters | A 6, B 6, C 9, D 6 (even would be 6.75) |
| Skills | applied-reasoning 19, definition-in-context 4, data-table 3, calculation 1 |
| Difficulty | foundation 1, standard 22, stretch 4 |
| Sketch to solve | 0 |

**No sketch items.** The two diagrams unit 4.1 turns on — the tariff diagram and
the currency demand-and-supply diagram — are both already owned as sketch items
by AQA 2.6.2 Q5 and 2.6.4 Q2. 4.1.6 Q6 asks about the tariff diagram's *areas*
instead, which is the part Edexcel sets out in detail and AQA does not.

### Batch 26 — Edexcel Theme 4, units 4.1.1 to 4.1.5 (2026-08-01)

5 topics, 32 questions. **The first Theme 4 batch** — globalisation,
specialisation and trade, the pattern of trade, the terms of trade, and trading
blocs and the WTO.

All 32 re-derived from the stem alone with **0 mismatches**; all three
calculations recomputed with every distractor value.

**Originality came back clean on all three fronts at the first attempt** — zero
shared 8-word runs against both past-paper corpora, zero against the
1,122-question bank, and no numeric option-set flag. Only batch 25 has managed
that before, and this batch is more than twice its size.

**The concept-grep found two topics that are effectively virgin ground**, which is
why the batch is 32 rather than the ~20 the AQA overlap would have suggested:

| Concept | Hits before this batch |
| --- | --- |
| terms of trade | 0 (one false positive, an unrelated micro distractor) |
| pattern of trade | 0 |
| emerging economies | 0 |
| WTO / World Trade Organisation | 0 as an answer |
| trade creation | 0 as an answer |
| free trade area, common market, monetary union | 0 (only the customs union definition) |

**4.1.4 terms of trade is the strongest set in the batch and AQA has nothing on
the topic at all.** It carries two of the three calculations — the index from two
price indices, and the harder one of applying two different growth rates to an
existing index — plus the three points that make the topic worth teaching:

- **The terms of trade is a ratio, so direction alone tells you nothing.** Export
  prices rising 4% while import prices rise 9% is a deterioration. Edexcel's own
  worked example makes the point and it is the best stretch item here.
- **Faster productivity growth *worsens* the terms of trade.** Lower costs mean
  lower export prices, which lowers the ratio — even though competitiveness has
  improved. Students reliably get this backwards.
- **An improvement can reduce export revenue.** With elastic demand for exports,
  higher prices lose more volume than they gain in margin, so the current account
  worsens. Edexcel sets it out explicitly; nothing in the bank had it.

**4.1.5 was expected to be occupied and was not.** AQA 2.6.2 has the customs
union definition and trade diversion, and that is all. Edexcel's four-rung ladder
(free trade area → customs union → common market → monetary union), the
**conditions for a successful monetary union** — synchronised cycles, labour
mobility, fiscal transfers, capital mobility — and the **WTO's two functions and
its tension with regional blocs** were all untouched, and carry six of the eight
questions.

**Where AQA did bind, the sets are short and built on what Edexcel adds.** 4.1.1
is five questions, because AQA 2.6.1 owns the definition, containerisation,
consumer effects, offshoring, the environment and inequality; what was left is
financial deregulation, global institutions, **cultural imperialism**, supply
chain dependence, and competition for skilled labour raising a domestic firm's
wage bill. 4.1.2 is six, because AQA 2.6.2 owns comparative advantage, the
opportunity cost table and the transport cost assumption; what was left is
consuming beyond the PPF, the **other four assumptions** of the model, and the
exploitation and food-security objections.

| | |
| --- | --- |
| Answer letters | A 9, B 8, C 8, D 7 (even would be 8) |
| Skills | applied-reasoning 23, definition-in-context 3, data-table 3, calculation 3 |
| Difficulty | foundation 1, standard 26, stretch 5 |
| Sketch to solve | 0 |

**No sketch items.** The one diagram unit 4.1 turns on is the PPF illustration of
comparative advantage, and it is printed on the 4.1.2 page — while AQA 2.6.2 Q5
already owns the tariff sketch. 4.1.2 Q1 asks what the diagram *shows* (consuming
beyond your own frontier) rather than asking a student to redraw it.

## Edexcel Theme 4 — 21 of 21 topics, complete

**Final profile:**

| | |
| --- | --- |
| Topics | 21 of 21 |
| Questions | 146 |
| Answer letters | A 39, B 40, C 39, D 28 (even would be 36.5) |
| Skills | applied-reasoning 97, definition-in-context 23, data-table 18, calculation 8 |
| Difficulty | foundation 11, standard 119, stretch 16 |
| Sketch to solve | 0 |

**Not one sketch item in 146 questions, and it is the right answer rather than an
oversight.** Theme 4's diagrams are the tariff diagram, the currency
demand-and-supply diagram, the PPF illustration of comparative advantage, the
Lorenz curve, the Kuznets curve, the buffer stock and the Laffer curve — and
every one of them is either already owned as a sketch item by an AQA set (AQA
2.6.2 Q5 and 2.6.4 Q2) or better tested by working *from* it than by redrawing
it. 4.2.2 Q1 computes a Gini coefficient from the areas; 4.5.2 Q1 puts the Laffer
curve into arithmetic; 4.3.3 Q3 turns the buffer stock into a table. Each of
those is a harder question than "sketch this and read off the answer".

**`calculation` at 5% is the lowest of any theme, and unavoidable.** Theme 4 is a
global-perspective theme: trade, development, finance and fiscal policy argued
rather than computed, and what arithmetic the specification does support was
almost entirely used by AQA macro 2.4, 2.5 and 2.6 first — bond yields, the
credit multiplier, liquidity ratios, the natural rate, current account balances,
the multiplier. The eight that survived were each built to be unlike the AQA
version: unit labour costs from two wage bills (4.1.9 Q1), the terms of trade
from two price indices (4.1.4), a relative poverty line tracked across two years
against a moving median (4.2.1 Q1), the Gini from A ÷ (A + B) (4.2.2 Q1), a
savings gap (4.3.2 Q1), and the Laffer curve in numbers (4.5.2 Q1).

**D at 28 against an even 36.5 is the weakest letter distribution of the four
Edexcel themes**, and the cause is identifiable: unit 4.1's nine sets were
drafted before the practice of choosing the option order deliberately had fully
settled, and they contributed D only 17 times in 59 questions. Units 4.2 to 4.5
came in at 39 / 39 / 34 / 28 across A to D — still light on D, but within
tolerance in every individual set, which is what the generator checks.

**The theme's own finding is that twin size does not predict batch size.** Unit
4.4 was forecast to be the hardest of the remaining batches because AQA's unit
2.4 carries 30 questions on the same specification area; it produced 21
questions with no rewrites, because AQA approaches financial markets through
money and banking mechanics and Edexcel approaches them through functions and
failures. Unit 4.2 was forecast to be manageable and produced the two smallest
sets in the theme, because AQA 1.7.1 to 1.7.3 had taken almost every angle on
poverty and inequality. **The concept-grep predicted both correctly and the twin
question count predicted neither.**

---

## The whole project — 166 of 166 topics, complete

**Site-wide profile, all six boards and themes:**

| | |
| --- | --- |
| Topics | 166 of 166 |
| Questions | **1,268**, against ~1,272 planned |
| Answer letters | A 320, B 358, C 332, D 258 (even would be 317) |
| Skills | applied-reasoning 791 (62%), definition-in-context 247 (19%), data-table 127 (10%), calculation 103 (8%) |
| Difficulty | foundation 155 (12%), standard 951 (75%), stretch 162 (13%) |
| Sketch to solve | 38 (3%) |

| Board / theme | Topics | Questions |
| --- | --- | --- |
| AQA Microeconomics | 54 | 401 |
| AQA Macroeconomics | 25 | 209 |
| Edexcel Theme 1 | 22 | 166 |
| Edexcel Theme 2 | 24 | 198 |
| Edexcel Theme 3 | 20 | 148 |
| Edexcel Theme 4 | 21 | 146 |

**Every one of the 1,268 questions was re-solved cold from the stem alone, in the
batch it was written in, and diffed against the recorded key.** Across thirty
batches that process found defects in a handful of questions and confirmed the
rest. It is the single most valuable step in the workflow and it should be the
last thing anyone drops.

**Where the profile misses its targets, and why.**

- `applied-reasoning` at 62% against a ~40% target, and `calculation` at 8%
  against ~15%. This was recorded and re-recorded from batch 5 onwards, and the
  cause never changed: AQA micro's 401 questions dominate the total, and units
  1.1, 1.2, 1.5, 1.7 and 1.8 are conceptual almost throughout. Macro pulled the
  right way — AQA macro finished at 12% calculation and Edexcel Theme 2 at 11% —
  but neither was large enough to move the total. **Not a defect to fix now: it
  would mean rewriting sets that pass every other check.**
- `data-table` at 10% against ~20% has the same shape. The tables that exist are
  real interpretation exercises rather than decoration, and inventing more would
  have meant inventing data.
- **D at 258 against an even 317** is the one genuine blemish. Its cause is §1 —
  alphabetically ordered option lists push correct answers early — and it was
  diagnosed in batch 1 and only fully designed around from batch 20. Every
  individual set passes the generator's tolerance; the site-wide skew is the
  accumulated residue of the first nineteen batches.

**What the workflow settled into, for anyone extending this.** Capture the base
commit; print the twin set in full immediately before writing each set;
concept-grep the bank for the four or five ideas the set turns on; read the
published page rather than the raw markdown; author into a throwaway helper that
asserts the mechanical rules at write time; run `--check`, then the three
originality passes; **cold re-solve every question**; then the verification
suite. Recurring problems §8 and §9 — cross-board duplication and concept-level
collision — decided the shape of every batch from 12 onwards and are the two
things a new session must read.

### Batch 25 — Edexcel Theme 3, unit 3.6 (2026-08-01)

2 topics, 14 questions. **Completes Edexcel Theme 3: 20 of 20 topics and 148
questions.** Government intervention, and its impact.

All 14 re-derived from the stem alone with **0 mismatches**; the RPI-X
calculation recomputed with every distractor.

**Originality clean on all three fronts, with no rewrites needed** — the first
batch since 21 where nothing had to be reworded for overlap. One numeric flag,
adjudicated and left: 3.6.1 Q1's options (2%, 3%, 5%, 7%) share three values with
an AQA paper set of 2 / 3 / 4 / 5, which is a question asking **how many workers**
a firm employs. Different topic, different units, single-digit integers.
Coincidence.

**3.6.1 turned out far richer than the twin audit suggested, and 3.6.2 far
poorer.** The reason is worth recording, because it inverts the usual pattern:

- **3.6.1's competition-policy material is AQA-occupied, but its *regulation*
  material is not.** AQA 1.8.7 and 1.8.8 own the CMA, price fixing, merger
  control, forced divestment, privatisation, deregulation and the purpose of a
  price cap. What they do not have is *how* regulation is actually done, which is
  where Edexcel goes into detail: the **RPI-X formula**, **profit regulation**
  and its perverse incentive, and **quality standards** with their unintended
  consequences. All three were free, and they carry the set.
- **3.6.2 is almost entirely occupied — by my own bank, not by AQA.** Edexcel
  1.4.2 (Government Failure, seven questions) already covers the definition,
  administrative costs exceeding benefits, unintended consequences, and — in Q7 —
  a regulator that recruits from the industry it oversees *and* depends on it for
  data, which is both of Edexcel 3.6.2's stated causes of regulatory capture in
  one question. AQA 1.8.10 adds seven more. That is 14 questions on government
  failure before this batch started, which is why 3.6.2 is only five.

**What survived in 3.6.2**: conflicting objectives (a price cap delivering lower
bills while starving investment), asymmetric information framed as firms being
able to *work around* a rule rather than the regulator mispricing a tax, the
five-aim list with productive efficiency picked out, compliance costs
entrenching incumbents, and the **revolving door** by name — which the bank
describes twice but has never labelled.

**Also free and used in 3.6.1**: competitive tendering, start-up support as a
contestability measure, and the whole of Edexcel's *protecting suppliers and
employees* section — minimum prices against monopsony power, and cooperatives
aggregating supply to counter a dominant buyer. Nothing in 1,108 questions
touched either.

| | |
| --- | --- |
| Answer letters | A 4, B 2, C 4, D 4 (even would be 3.5) |
| Skills | applied-reasoning 9, definition-in-context 2, data-table 2, calculation 1 |
| Difficulty | standard 11, stretch 3, foundation 0 |
| Sketch to solve | 0 |

---

## Edexcel Theme 3 — 20 of 20 topics, complete

**Final profile:**

| | |
| --- | --- |
| Topics | 20 of 20 |
| Questions | 148, against 157 planned |
| Answer letters | A 37, B 37, C 38, D 36 (even would be 37) |
| Skills | applied-reasoning 102, definition-in-context 17, data-table 16, calculation 13 |
| Difficulty | foundation 10, standard 118, stretch 20 |
| Sketch to solve | 2 |

**The letter distribution is the best on the site by a wide margin** — 37 / 37 /
38 / 36 against an even 37, a maximum deviation of one across 148 questions.
Themes 1 and 2 finished with D at 28 of 163 and 37 of 198 respectively. The
difference is that every Theme 3 set was ordered by domain sequence or reworded
to sort the correct option late **while drafting**, rather than reshuffled after
the generator complained. §1 has recommended this since batch 1; Theme 3 is the
first theme to do it from the first set to the last.

**148 against 157 planned, and the shortfall is deliberate.** Theme 3 is the
closest twin of the whole project — AQA micro units 1.4, 1.5, 1.6 and parts of
1.8 carry over 200 questions on the same economics. Five sets came in at five or
six questions rather than eight, because that was what remained after the
occupied ground was subtracted: 3.4.1 efficiency (5), 3.4.7 contestability (5),
3.6.2 impact of intervention (5), and the three unit 3.5 labour sets (6 each).
Padding them would have meant porting AQA questions with the nouns changed.

`applied-reasoning` at 69% is the highest of any theme, and `foundation` at 7%
the lowest. Both follow from the same cause: AQA had already taken essentially
every definitional item in the theme, so what was left needed a chained
inference by construction.

`calculation` at 9% is close to the site-wide 8%, and unit 3.3 alone supplied 8
of the 13. **The two new arithmetic archetypes worth remembering are the
marginal cost of labour computed from a wage bill (3.5.3 Q6) and MRP run
backwards to find a product price (3.5.1 Q2)** — both were built because AQA
already owned the forward version.

### Batch 24 — Edexcel Theme 3, unit 3.5 (2026-08-01)

3 topics, 18 questions. The labour market unit — demand for labour, supply of
labour and wage determination.

All 18 re-derived from the stem alone with **0 mismatches**; both calculations
recomputed with every distractor value.

**Originality clean on all three fronts.** One intra-bank hit was fixed first:
3.5.1 Q5 shared "over the following five years. the best explanation is that"
with Edexcel 1.2.3 Q10 — my own scaffolding, reworded.

**This was the tightest twin situation of the entire project.** AQA 1.6.1 to
1.6.6 carry **47 questions** across exactly this ground, and between them they
own:

- derived demand, MRP = MPP × MR, MRP from a table, hiring until MRP = wage, the
  downward slope from diminishing returns, and the criticism that individual
  output cannot be measured (1.6.1, nine questions)
- the upward-sloping supply curve, the backward bend, occupational and
  geographical immobility, retraining, and inelastic supply from training time
  (1.6.2, seven)
- wage takers, disequilibrium wages, the firm's perfectly elastic supply curve,
  product demand shifting the labour market, MRP against the wage, surgeons
  against cleaners, and migration (1.6.3, eight)
- the whole of monopsony (1.6.4, eight), the whole of trade unions (1.6.5,
  seven), and the whole of the minimum wage (1.6.6, eight)

**18 questions is what honestly remained.** The concept-grep is the only reason
there were that many: six of the eight ideas checked before drafting returned
**zero hits across 1,090 questions**, and each of them became a question.

| Concept | Hits before this batch |
| --- | --- |
| non-monetary benefits and working conditions | 0 |
| worker motivation offsetting a minimum wage | 0 |
| the vocational aspect of supply elasticity | 0 |
| labour demand more elastic in the long run | 0 |
| the price of the final product raising MRP | 0 |
| economic conditions and union bargaining power | 0 |

**The two calculations are both new archetypes for the bank:**

- **MRP run backwards.** Given MPP and MRP, find the product price. AQA 1.6.1 Q3
  runs it forwards off a table, which is the standard form and was unavailable.
- **The marginal cost of labour, computed.** 50 workers at £400, a 51st requiring
  £405 for everyone: MCL = £655, not the £405 the new worker receives. AQA 1.6.4
  Q3 *explains* why MCL lies above the supply curve but never puts a number on
  it, and the arithmetic makes the point far better than the words do.

**Where else Edexcel opened room:**

- **The price of the final product** as a shift factor distinct from demand for
  it. Both work through MR, and AQA only tests the demand side.
- **Substitutability as a shifter rather than an elasticity determinant.** AQA
  uses cheap capital to explain elasticity; Edexcel lists it as something that
  moves the curve.
- **Three of the four wage-elasticity-of-demand determinants** — labour's share
  of total costs, the time period, and the PED of the final product. AQA tests
  only the fourth.
- **The available pool of labour and the vocational aspect** on the supply side.
- **Where the monopsonist's wage is actually read from.** AQA establishes that
  workers are paid less than their MRP; nothing in the bank says the wage comes
  off the *supply curve* at the chosen quantity, which is the step students miss.
- **Both minimum-wage evaluations Edexcel gives** — that the effect depends on
  how far above equilibrium the floor is set, and that improved motivation can
  offset the cost rise. The second is the best question in the batch.

| | |
| --- | --- |
| Answer letters | A 6, B 5, C 3, D 4 (even would be 4.5) |
| Skills | applied-reasoning 14, calculation 2, data-table 1, definition-in-context 1 |
| Difficulty | standard 16, stretch 2, foundation 0 |
| Sketch to solve | 0 |

**No foundation items and no sketch items, both for the same reason.** Every
straightforward definitional question in this unit — derived demand, MRP, wage
takers, the backward bend, union density, the minimum wage as a price floor — is
already in the AQA bank, and so is every obvious diagram, including AQA 1.6.3 Q3
and 1.6.6 Q5. What was left needs a chained inference by construction, which is
why the batch is almost entirely `standard`.

### Batch 23 — Edexcel Theme 3, units 3.4.5 to 3.4.7 (2026-08-01)

3 topics, 19 questions. **Completes unit 3.4** — monopoly, monopsony and
contestability.

All 19 re-derived from the stem alone with **0 mismatches**. Originality clean on
all three fronts after fixing two option-length and template issues.

**19 questions across three topics is the lightest batch on the site, and it is
the right number.** AQA 1.5.6, 1.5.7, 1.5.9 and 1.6.4 carry **33 questions** over
this ground, and two of the three topics are close to exhausted by them:

- **AQA 1.5.9 owns contestability almost entirely** — the definition, the
  competition-against-contestability distinction, sunk costs, hit-and-run entry,
  two firms pricing near AC to deter entry, brand loyalty as a barrier, lower
  prices in contestable markets, and reducing barriers as the policy response.
  Eight of eight. Edexcel's page adds the **types of barrier** list and the
  Amazon/eBay observation that a concentrated market can behave competitively, so
  the set is five questions built on those.
- **AQA 1.5.7 owns price discrimination**, all three degrees and the conditions.
  What survived is Edexcel's own material: the **cost to the firm** of separating
  markets and policing resale, and the benefit to elastic-demand consumers of
  **quieter services and better availability**, neither of which AQA tests.

**Monopsony was the free topic, and the concept-grep is what confirmed it.**
Searching the bank returned 14 hits for monopsony, **every one of them AQA 1.6.x
and every one framed as a labour market** — a dominant employer, the marginal
cost of labour above the supply curve, unions and minimum wages. The Edexcel page
frames monopsony as **general buyer power** ("a single buyer of a good, service or
factor of production") and works through a four-agent ledger of firms, consumers,
workers and suppliers. That is untouched ground, and the whole set was written on
it: the supermarket-and-farmers case, delayed payment as the cost to suppliers,
stable order books as the genuine benefit to them, lower shop prices as the
consumer defence, and a firm holding monopoly and monopsony power at once.

**Deliberately left alone: the monopsony labour market diagram.** The Edexcel page
defers it to 3.5.3, and AQA 1.6.4/1.6.5/1.6.6 already carry a union-and-monopsonist
question, a minimum-wage-in-monopsony sketch and the MCL-above-supply explanation.
Those questions belong in the 3.5.3 set if anywhere.

**Where 3.4.5 found room despite AQA's nine questions:**

- **Asymmetric information as a characteristic of monopoly.** Edexcel lists it;
  AQA does not, and the concept-grep confirmed the bank tests asymmetric
  information eleven times without ever attaching it to monopoly.
- **Patents as the barrier that sustains long-run profit.** One hit in the whole
  bank, and that was in the balance of payments.
- **The stakeholder ledger**, especially the effects on **suppliers and workers**,
  which AQA's monopoly set does not consider at all.
- **Natural monopoly by its cost structure** rather than its definition — high
  fixed costs, low marginal costs, LRAC falling across the whole range of demand.
  AQA Q5 gives the definition and Q9 the marginal-cost-pricing problem; the reason
  behind both was free.
- **X-inefficiency as conditional.** Edexcel says "possible", depending on the
  barriers. Two firms each with 100% share but different entry threats makes that
  concrete, and it is a genuinely good stretch item.
- **Why a price maker still cannot charge anything it likes.** Nothing in the
  bank makes the point that market power widens the choice without removing the
  demand constraint.

**A new N-Q finding, and the largest over-promise on the site** —
`REVIEW-NOTES.md` N-Q15. `3-4-6-monopsony` promises the monopsony labour market
diagram, monopsonistic exploitation, minimum wages and trade unions, and the body
contains none of the four. Unlike the earlier cases most of the material exists,
on `3-5-3-wage-determination`, so it is mainly a **cross-reference problem**: the
alert claims for itself what another page delivers. Only monopsonistic
exploitation is missing from both.

**Table stems collided twice more with my own bank** — "From Table 1, the only one
that is a…" against 3.1.3 Q6. That is the third batch running. The wording is now
varied per set rather than per noun: "the consequence usually presented as an
advantage", "the effect that harms rather than helps", "the sunk cost is".

| | |
| --- | --- |
| Answer letters | A 4, B 6, C 5, D 4 (even would be 4.75) |
| Skills | applied-reasoning 14, data-table 3, definition-in-context 2 |
| Difficulty | foundation 1, standard 15, stretch 3 |
| Sketch to solve | 0 |

**No calculations and no sketch items**, and neither is an oversight. The three
pages carry no figures at all, and every diagram on them is printed rather than
constructed — while AQA 1.5.6 Q4 already owns the monopoly sketch. Unit 3.4 as a
whole finished with 2 calculations and 1 sketch across 47 questions.

### Batch 22 — Edexcel Theme 3, units 3.4.1 to 3.4.4 (2026-08-01)

4 topics, 28 questions. Efficiency, perfect competition, monopolistic competition
and oligopoly — the first half of the market structures unit, split in two as
planned.

All 28 re-derived from the stem alone with **0 mismatches**; the two calculations
and every distractor figure recomputed.

**Originality clean on all three fronts after two rounds of fixes** — zero shared
8-word runs against both past-paper corpora and zero against the 1,043-question
bank.

**The concept-grep from §9 decided the shape of this batch, and it is the reason
it exists at all.** Searching the whole bank before writing established that four
ideas the Edexcel pages teach appear **nowhere in 1,043 questions**:

| Concept | Hits in the bank before this batch |
| --- | --- |
| game theory, Prisoner's Dilemma, Nash equilibrium, dominant strategy | 0 |
| deadweight loss | 0 |
| price wars | 0 |
| sticky or rigid prices | 0 |

Those four carry six of the nine questions in 3.4.4 and one in 3.4.1. Without the
grep this batch would have been written round the same concentration ratios and
cartel definitions AQA 1.5.5 already has, and would have collided badly. **The
search took under a minute.**

The same search found the opposite result for **X-inefficiency**, which AQA tests
three times (1.5.10 Q3, 1.5.6 Q7, 1.5.8 Q5) — including a "costs drift upwards
with no competition" scenario almost identical to the one drafted for 3.4.1. That
question was rebuilt to test Edexcel's *other* stated cause, a lack of profit
incentive, and to ask which condition produces X-inefficiency rather than what to
call it.

**Twin pressure was heaviest on 3.4.1, and the set is only five questions as a
result.** AQA 1.5.10's eight questions cover allocative at AR = MC, productive at
minimum AC, static efficiency, dynamic efficiency needing reinvested supernormal
profit, a three-situation classification table, perfect competition's static-but-
not-dynamic verdict, the monopolist's allocative inefficiency, and the static
against dynamic trade-off in a break-up decision. That is the whole topic. What
was left is genuinely Edexcel: **deadweight welfare loss** as the consequence of
underproduction, X-inefficiency by cause rather than label, and the page's careful
word **potential** — imperfect competition has the potential for dynamic
efficiency, which a firm paying all its profit out to shareholders does not
realise. Five good questions beat eight with three ports in them.

**Where Edexcel opened room the AQA sets do not have:**

- **The loss-to-exit adjustment**, in both 3.4.2 and 3.4.3. AQA runs the long-run
  adjustment only from supernormal profit inwards; Edexcel's pages set out both
  directions, so the exit case is free on both topics.
- **The four-way equality P = AR = AC = MC** decomposed. Asking what AR = AC on
  its own tells you separates three facts students usually blur together.
- **Edexcel's consumer-impact treatment of monopolistic competition** — prices
  possibly higher because small firms miss economies of scale, and choice possibly
  illusory because differentiation is surface-level. AQA has no evaluative
  material here at all, and the shampoo-shelf question is the best in that set.
- **Overt against tacit collusion, and price leadership.** AQA has "collusive
  behaviour, forming a cartel" and nothing else.
- **Predatory pricing as an answer.** It appears five times in the AQA bank, always
  as a distractor.
- **The kinked demand curve's asymmetry explained.** AQA sketches the curve and
  asks what the firm does; Edexcel explains why each side has the elasticity it
  has, which is a different and better question.

**Two table-caption collisions, both with the same source.** 3.4.1 Q5 and 3.4.3 Q4
both shared "Table 1 sets out four claims a student makes about" with Edexcel
2.6.4 Q6. This is the template problem batch 18 first flagged and batch 19 warned
about, and it has now recurred twice in one batch. The two were varied to
"statements" and "notes" respectively. **Vary the noun as well as the verb: the
bank now has claims, changes, developments, consequences, notes and statements,
and the check will keep surfacing whichever gets reused.**

| | |
| --- | --- |
| Answer letters | A 8, B 7, C 7, D 6 (even would be 7) |
| Skills | applied-reasoning 19, definition-in-context 5, data-table 2, calculation 2 |
| Difficulty | foundation 3, standard 22, stretch 3 |
| Sketch to solve | 1 |

`calculation` at 7% is exactly what was predicted for this unit — the only
arithmetic unit 3.4 supports is the concentration ratio, and AQA 1.5.5 Q2 already
runs it forwards, so 3.4.4 Q4 runs it backwards from the ratio to the market
total. The one sketch item is in 3.4.2, where the market and the firm have to be
drawn side by side to see that the firm's horizontal demand curve rises with the
market price.

### Batch 21 — Edexcel Theme 3, unit 3.3 (2026-08-01)

4 topics, 36 questions. Revenue, costs, economies of scale, and profit — **the
arithmetic unit of the specification, and the batch that was supposed to pull the
calculation share back up. It did.**

All 36 re-derived from the stem alone with **0 mismatches**; every figure in
every schedule recomputed, including all distractor values — 30 arithmetic checks
in total, plus the internal consistency of each cost schedule (AFC + AVC = AC in
3.3.2 Q2 and Q9; the MR series in 3.3.1 Q4 falling +22, +14, +6, −2; the two
shut-down cases in 3.3.4 Q2 and Q10 cross-checked against the contribution).

**`calculation` came in at 8 of 36 — 22%**, against a ~15% target and against 0%
in batch 20. Only unit 2.1's 23% beats it. Site-wide the figure has moved from 8%
to 9%, which does not sound like much but is the first upward movement in nine
batches. The material is what did it: revenue and cost schedules, marginal
calculations, opportunity-cost profit and the shut-down arithmetic are all
genuinely on these four pages.

**Originality clean against both past-paper corpora at every n-gram length.**
Against the 1,007-question bank, two hits, one of them serious:

- **3.3.1 Q4 shared a fourteen-word stem sentence with AQA 1.4.6 Q2** — "Table 1
  shows the price a firm must [charge/set] in order to sell each quantity of its
  output" — *and* asked the same thing off the same kind of table. Rebuilt from
  the other direction: the table now gives quantity and total revenue, and the
  question asks where marginal revenue first turns negative. That forces the
  student to compute MR from TR rather than read a peak off a column, which is a
  better question as well as an original one.
- 3.3.3 Q7 shared "has risen. the most likely explanation is that" with AQA 1.7.2
  Q7 — stock scaffolding across unrelated topics, reworded anyway.

**One numeric option-set flag, adjudicated and left.** 3.3.1 Q2's options
(−£15, −£6, £3, £9) share three values with an AQA paper set of 3 / 5 / 6 / 9.
That real question is the **natural rate of unemployment** item batches 8 and 11
have both looked at before: percentages, macro, no negatives. Coincidence, as
§7 predicts for small integers. **Do not rewrite it on a fourth encounter.**

**Six drafted questions were dropped or rebuilt at the twin-audit stage**, which
is the highest count of any batch and exactly what was predicted for this unit:

- An MC-from-two-total-costs item that reproduced AQA 1.4.4 Q3 sentence for
  sentence. Rebuilt as a per-unit question on new figures.
- A supernormal-profit calculation that was AQA 1.4.7 Q2 with different numbers
  (units × price against total costs including normal profit).
- "MC is above AVC, so AVC will…", which is AQA 1.4.4 Q5 mirrored.
- "Productively efficient at minimum AC", which is **AQA 1.5.10 Q2 verbatim** —
  caught by grepping the whole bank for the concept rather than by shingling.
- A bigger-factory-higher-LRAC item, which is AQA 1.4.3 Q9.
- A U-shaped-LRAC item whose first sentence matched AQA 1.4.5 Q8.

**Grepping the bank by concept, not just shingling by phrase, is what caught the
worst of these.** The productive-efficiency collision shared almost no wording
with AQA 1.5.10 Q2 and would have survived the 8-gram check untouched. Worth
doing for every unit from here: pick the four or five ideas the set turns on and
search the whole bank for each.

**What was left, once AQA's 44 questions were subtracted:**

- **The shut-down rules are completely free ground**, and they are the best
  material in the batch. Nothing anywhere in the bank mentions AVC as a decision
  rule. Five questions come from them: the short-run test, why it is AVC rather
  than AC, the long-run test, a four-firm table where the largest loss is *not*
  the firm that should stop, and the case where the two rules disagree and the
  answer is to run out the year and then leave.
- **The SRAC/LRAC envelope** — also entirely absent from the bank.
- **Marginal cost is unaffected by a change in fixed costs.** A rent rise moves AC
  at every output and leaves MC untouched, so the profit-maximising output does
  not move. Edexcel's page supports it and AQA never tests it; it also sets up the
  shut-down rule directly.
- **The total revenue rule as a full grid.** AQA tests one cell of it. Unitary
  elasticity leaving TR unchanged, and the inelastic-so-raise-the-price decision,
  are both free.
- **Favourable legislation** as an external economy of scale, and **motivational**
  and **geographical** diseconomies, all of which Edexcel names and AQA uses only
  as distractors.
- **MES applied to market structure** rather than defined. AQA defines it; asking
  what a MES of 40% of demand implies about the number of firms is new, and it is
  the best question in 3.3.3.
- **Edexcel's explanation of *why* a supplier grants a bulk discount** — the order
  is a large share of the supplier's own revenue. AQA asks students to classify
  the discount; Edexcel explains the bargaining behind it.

**Two content findings logged, not fixed** — `REVIEW-NOTES.md` N-Q13 and N-Q14.
`3-3-4` promises explicit and implicit costs in its spec alert and never names
either, though it does teach the underlying idea inside its treatment of normal
profit. And `3-3-2` states the LRAC envelope as touching "the lowest points of the
SRAC curves", which holds only at minimum efficient scale. The second was found
*during the cold re-solve*: 3.3.2 Q6 had been drafted on the page's wording, and
solving it cold surfaced the problem. It now asks what the envelope is — the
lowest cost achievable at each output — which is right on the page's terms and
right in general.

**No sketch items.** Unit 3.3 is where the cost and revenue curves are built, and
every diagram the four pages carry is printed on the page. Asking a student to
sketch what they are looking at earns nothing; the sketch items in this theme
belong in 3.4, where the curves have to be combined.

| | |
| --- | --- |
| Answer letters | A 8, B 9, C 11, D 8 (even would be 9) |
| Skills | applied-reasoning 21, calculation 8, data-table 4, definition-in-context 3 |
| Difficulty | foundation 3, standard 28, stretch 5 |
| Sketch to solve | 0 |

### Batch 20 — Edexcel Theme 3, units 3.1 and 3.2 (2026-08-01)

4 topics, 33 questions. **The first Theme 3 batch** — sizes and types of firms,
business growth, demergers and business objectives.

All 33 re-derived from the stem alone with **0 mismatches**, and the cold
re-solve earned its keep for the first time in several batches: **3.2.1 Q6 had
two defensible answers.** The stem asked which firm was pursuing an objective
"outside the standard three of profit, revenue and sales maximisation", and one
of the distractor rows described satisficing — which is also outside those three.
The stem now names all four objectives explicitly, leaving only the CSR row.
Nothing about that was visible while drafting; it only showed up on solving the
question cold against its own options.

**Originality clean against both past-paper corpora at every n-gram length.**
Against the 974-question bank, two hits, one of them real:

- **3.2.1 Q2 opened "A firm switches from profit maximisation to revenue
  maximisation" — AQA 1.5.2 Q6's opening sentence word for word.** The questions
  differ (AQA asks what happens to price and output; ours asks why a firm would
  do it), but the shared sentence is exactly the §8 signal. Rebuilt to name the
  rules instead of the labels: "produces past the output at which MC = MR,
  settling instead at the output where MR = 0". That is a better stem as well as
  an original one, since it makes the student apply the rule rather than
  recognise the term.
- 3.1.1 Q4 shared "of the following, the measure most likely to" with Edexcel
  2.2.2 Q8. Stock scaffolding, reworded anyway.

**Three drafted questions were dropped outright at the twin-audit stage**, before
anything was written down, and it is worth recording what they were, because the
same traps will recur through unit 3.3:

- A *diseconomies of scale* item for 3.1.1 — the scenario (instructions delayed
  and distorted on the way to the shop floor, costs rising) is AQA 1.4.5 Q6
  almost word for word.
- An *access to finance* item built on two firms of different sizes being quoted
  different interest rates — that is AQA 1.4.5 Q3, the financial economies of
  scale question. Rewritten around a single firm turned down by lenders.
- A *horizontal merger* item opening "two of the four firms in a market agree to
  merge" — AQA 1.8.7 Q4 uses the identical setup. Replaced with the culture-clash
  question, which is Edexcel's own material and better anyway.

**Where the twins bind hardest, and what was left:**

- **AQA 1.5.2 owns the whole of Edexcel 3.2.1's core** — MR = 0, AC = AR, the
  divorce of ownership from control, the principal-agent problem, satisficing,
  the profit-max-to-revenue-max comparison and limit pricing. Seven of seven.
- **AQA 1.4.7 Q4 and 1.4.6 Q5 own the two remaining rules**, MC = MR for profit
  maximisation and MR = 0 for revenue maximisation, so all three definitional
  items were gone before drafting began.
- What survived is the **three-way ranking** (Qpm &lt; Qrm &lt; Qsm and the prices
  in reverse), which AQA never asks and which makes the batch's sketch item; the
  **commercial reason** for revenue maximisation, which Edexcel states as
  economies of scale raising long-term profit; **satisficing's position between
  the two extremes**; and the **other objectives** Edexcel lists and AQA does not
  — survival, employee welfare and CSR.

**3.1.3 has no AQA twin at all.** Demergers are not on the AQA specification, so
the whole topic is free ground: the six motives, the loss of synergies, the
stakeholder split between business, workers and consumers, and the evaluation
that a demerger only cuts costs where diseconomies genuinely existed.

**3.1.2 is nearly as free.** AQA has nothing on organic against inorganic growth
or on the three types of integration; only 1.8.7 touches mergers, and from the
competition authority's side. This is why the set runs to ten.

**`calculation` is zero, and that is not an oversight.** Units 3.1 and 3.2 carry
no numbers at all — no cost schedules, no revenue schedules, no figures on any of
the four pages. Inventing arithmetic here would have meant pre-empting 3.3.1 and
3.3.2, where it belongs and where the notes actually supply it. The claim in
"Remaining work" that Theme 3 is where the calculation share recovers stands, but
it rests entirely on unit 3.3 and on the concentration ratios in 3.4.

**One sketch item** (3.2.1 Q1), and it is a genuine one: the single AR/MR/AC/MC
diagram with all three objective outputs marked on it is exactly what the Edexcel
page asks students to be able to draw, and no AQA question uses it.

**A new N-Q8-type finding, logged not fixed** — `REVIEW-NOTES.md` N-Q12.
`3-1-1-sizes-types-of-firms` promises "sole traders, partnerships, and private
and public limited companies" in its spec alert and metadata, and the body never
mentions limited companies at all. Unlike the Theme 2 cases this is not a
conversion loss: `raw-notes/edexcel/3.1.1.md` does not contain the material
either. The other three pages in this batch check out clean.

| | |
| --- | --- |
| Answer letters | A 7, B 8, C 8, D 10 (even would be 8.25) |
| Skills | applied-reasoning 25, definition-in-context 4, data-table 4, calculation 0 |
| Difficulty | foundation 3, standard 26, stretch 4 |
| Sketch to solve | 1 |

`applied-reasoning` at 76% is the second highest of any batch, behind unit 2.3.
The material is classification and evaluation throughout — which type of
integration is this, why did this firm stay small, what did this demerger cost —
and the definitional items that would have balanced it were the ones AQA had
already taken. **D leads the batch for the second time running**, at 10 of 33.

### Batch 19 — Edexcel Theme 2, unit 2.6 (2026-08-01)

4 topics, 34 questions. **Completes Edexcel Theme 2: 24 of 24 topics and 198
questions.** Objectives, demand-side policies, supply-side policies and the
conflicts between them.

All 34 re-derived from the stem alone with **0 mismatches**; the one calculation
(2.6.2 Q10, a deficit added to a debt stock) recomputed with all three distractor
figures.

**Both originality checks came back completely clean, and this is the headline.**
Zero shared runs of 8 words or more against either past-paper corpus, **and zero
against the 940-question bank** — no rewrites, no rewordings, nothing to
adjudicate. That is the first batch on either board to return nothing on all
three fronts at once, and it happened on the unit that was flagged in advance as
having the largest twin overlap of any Edexcel unit so far.

**The reason is the twin audit, run in full before a word was written.** All 41
questions from AQA 2.1.1, 2.3.4, 2.4.3, 2.5.1 and 2.5.2 were printed and read,
and so were all 164 existing Edexcel Theme 2 stems, which turned out to matter
just as much. The ground that had to be surrendered:

- **AQA 2.4.3 owns the whole monetary transmission mechanism** — variable-rate
  mortgages, hot money and the exchange rate, what QE buys, why QE raises
  lending, the liquidity trap, and a rate cut blunted by weak confidence. Six of
  the nine.
- **AQA 2.5.1 owns fiscal policy's set pieces** — deficit against debt, the
  budget-position table, transfer payments, VAT's regressiveness, crowding out,
  the structural deficit, the Laffer curve and Ricardian equivalence. Eight of
  the nine, and the Edexcel page teaches all of them.
- **AQA 2.5.2 owns five of the eight supply-side archetypes** — the aim, the
  market-based/interventionist table, infrastructure, the income tax incentive,
  the minimum wage cut narrowing the benefit gap, privatisation into a monopoly,
  and the education time lag.
- **AQA 2.3.4 owns the Phillips curve outright**, including the sketch item, the
  vertical long-run curve and supply-side policy cutting the natural rate.
- **My own Theme 2 sets had already taken more than expected**: infrastructure
  raising AD then LRAS (2.2.4 Q4), training doing the same (2.5.1 Q5), tightening
  in a boom (2.5.3 Q5), a table of measures that shift LRAS (2.3.3 Q3), an LRAS
  shift lowering the price level (2.4.3 Q5), and growth worsening the current
  account (2.5.4 Q6).

**What was left is almost entirely Edexcel's own material, and there was more of
it than the twin overlap suggested:**

- **The seven-objective impact grid.** The Edexcel 2.6.2 and 2.6.3 pages work
  through what each policy does to growth, inflation, employment, the current
  account, income distribution, the environment and the government budget. AQA
  never does this systematically, and three questions come straight out of it:
  low rates widening *wealth* inequality through asset prices, expansionary
  fiscal policy improving equality through progressive tax and public services,
  and a rate cut improving the budget by cutting debt-servicing costs.
- **The balance of payments effect of a tax cut depends on which tax.** An income
  tax cut pulls in imports; a VAT cut works on prices and helps exports. The
  Edexcel page states both halves. This is the best question in the batch and has
  no counterpart anywhere in the bank.
- **Cutting income tax can *reduce* hours worked**, because the same target income
  is now reachable in less time. Edexcel gives this as the evaluation of the
  policy AQA 2.5.2 Q4 tests straight.
- **Evaluations attached to every supply-side tool** — subsidy dependency,
  deregulation's unintended quality effects, weaker unions damaging motivation
  and so productivity, lower corporation tax against the budget. Five questions,
  and AQA has none of these.
- **Full employment stated as 4-5% rather than 0%**, and the fiscal target stated
  **over the cycle** rather than annually. Both are Edexcel framings.
- **Large current account *surpluses* as a problem.** AQA only ever tests
  deficits.
- **The Edexcel mechanism for the unemployment-inflation link** — people moving
  from benefits onto a full wage and spending the difference, so the inflation is
  explicitly demand-pull rather than cost-push. Naming demand-pull in the stem is
  what makes the wage-cost distractor cleanly wrong.

**No sketch items, and this one is a genuine loss rather than a design choice.**
Unit 2.6 is where AD/AS and LRAS diagrams are applied, but AQA 2.5.2 Q7 already
has the supply-side-against-fiscal sketch, AQA 2.3.4 Q2 has the Phillips curve,
and my own 2.3.3 and 2.4.3 have the Keynesian ones. The one free diagram — the
raw notes' contractionary policy on a Keynesian curve, with AD in the vertical
section — **is not on the published page**, so it was left alone.

**Letter distribution came out at A 9, B 7, C 8, D 10** — the first batch on the
site where D is the most-used letter. Options were ordered by domain sequence
while drafting, and where alphabetical order would have pushed the answer early,
the correct option was reworded to sort later rather than the set being
reshuffled afterwards. That is §1's advice applied at the point it is cheap.

| | |
| --- | --- |
| Answer letters | A 9, B 7, C 8, D 10 (even would be 8.5) |
| Skills | applied-reasoning 23, definition-in-context 6, data-table 4, calculation 1 |
| Difficulty | foundation 4, standard 26, stretch 4 |
| Sketch to solve | 0 |

`applied-reasoning` at 68% is the second highest of any batch. Unit 2.6 is policy
evaluation from end to end: every page is a list of tools followed by a list of
reasons each may fail. `calculation` at 3% matches unit 2.5's low, and for the
same reason — the only arithmetic these four pages support is the budget
identity, and using it twice would have produced near-duplicate questions.

### Batch 18 — Edexcel Theme 2, unit 2.5 (2026-08-01)

4 topics, 31 questions. **Economic Growth** — its causes, output gaps, the trade
cycle and the impact of growth.

All 31 re-derived from the stem alone with **0 mismatches**.

**Originality: zero shared 8-word runs against either past-paper corpus.**
Against our own bank, three needed fixing and one of them was a port:

- **2.5.2 Q2 was AQA 2.3.1 Q6 with new numbers.** Both read "…Expressed as a
  percentage of potential GDP, the output gap is", differing only in the figures
  and the sign of the gap. Rebuilt to run the calculation the other way: given a
  5% positive gap and potential GDP, find actual GDP. Same concept, and the
  distractors now test the sign and the base rather than the divisor.
- 2.5.3 Q3 shared its stem shape with AQA 2.3.1 Q5 *and* AQA 2.3.4 Q7, both of
  which open "Table 1 shows four indicators for an economy…". Reworded, and the
  question asked was already different — AQA asks for the phase of the cycle,
  ours for the output gap, which is the link the Edexcel page draws.
- **2.5.1 Q4 collided with three of my own sets.** "Table 1 lists four
  developments in an economy" had by then been used in 2.1.4, 2.2.3 and 2.3.1.
  That is not a duplication problem, but four identical captions across the bank
  is careless, and it buries real signal in the check output. Varied to "sets out
  four changes taking place in an economy".

**Worth carrying forward: my own table captions are becoming a template.** The
cross-bank check now surfaces them more often than it surfaces real overlaps.
Vary the caption wording per set, or the noise will keep growing as the bank does.

**Re-verified in full before batch 19 (2026-08-01).** Second cold re-solve of all
31 — again 0 mismatches. Every mechanical gate clean: the generator, HTML, links,
text and markup integrity, no removed lines, no site-wide option-length flags,
cross-links and sitemap entries present on all four topics. Originality re-run
returned zero hits at n=8 against both past-paper corpora and no numeric option
set sharing three values with a paper.

One intra-bank 8-gram survived and **is being left alone**: 2.5.1 Q4 shares
"in an economy. using table 1 the change that" with 2.2.1 Q5. That is exactly the
caption-plus-stem template this batch flagged — the two tables and the two
questions have nothing else in common (potential against actual output, versus
net trade). It is noise of my own making, not duplication. The fix is to vary the
template in new sets, which batch 19 did, not to rewrite a committed question for
a third time.

**Angles Edexcel opens that AQA does not:**

- **Export-led growth**, named with the China example and its risks. AQA has
  nothing on it, so two questions come free.
- **The trend rate of growth** as a defined term — a ten-year average — which
  gives the output gap a benchmark AQA never states.
- **Recessionary and inflationary gap** as alternative names for the negative and
  positive gaps.
- **A positive output gap cannot be drawn on a Keynesian diagram**, because the
  curve turns vertical at Yfe. A genuinely good question and distinctly Edexcel.
- **The difficulty of measuring potential output**, which has its own section.
  2.5.2 Q8 turns it into a government-failure item: a fiscal expansion aimed at a
  negative gap that turns out not to exist.
- **The whole of 2.5.4.** AQA has no topic on the impact of growth, so the costs
  and benefits, the growth-versus-well-being debate and the environmental
  trade-off are all free ground.
- **Spending on a supply-side measure is also a demand injection** (2.5.1 Q5):
  training raises AD now and LRAS later.

**Two more N-Q9 corrections, both from reading the pages rather than grepping.**
`2-5-4` does cover inequality, as "Worsened Income Equality" — my audit searched
for the wrong word. Only sustainable development was genuinely missing.
`2-5-3` is worse than recorded: it names none of the four phases, not just slump
and recovery. Questions were written for both gaps per the site owner's
instruction. See `REVIEW-NOTES.md`; the corrected list is 8 pages.

| | |
| --- | --- |
| Answer letters | A 8, B 10, C 8, D 5 (even would be 7.75) |
| Skills | applied-reasoning 21, definition-in-context 6, data-table 3, calculation 1 |
| Difficulty | foundation 4, standard 23, stretch 4 |
| Sketch to solve | 0 |

**`calculation` at 3% is the lowest of any batch**, and it is a property of the
material rather than an oversight. The only arithmetic unit 2.5 supports is the
output gap, and using it twice would have meant near-duplicate questions. Growth,
the trade cycle and the impact of growth are argued rather than computed.

---

### Batch 17 — Edexcel Theme 2, unit 2.4 (2026-08-01)

4 topics, 31 questions. **National Income** — the circular flow, injections and
withdrawals, macroeconomic equilibrium and the multiplier.

All 31 re-derived from the stem alone with **0 mismatches**; 24 arithmetic
checks, including the internal consistency of the propensity identities.

**Originality finished clean — zero shared 8-word runs against either past-paper
corpus and zero against the 878-question bank.** Three stems needed rewriting
first, and one of them was the collision this batch was warned about:

- **2.4.4 Q1 was the same archetype as AQA 2.2.4 Q8 in near-identical wording.**
  Both opened "In an economy the marginal propensity to consume/save is 0.xx, the
  marginal propensity to tax is 0.xx and the marginal propensity to import is
  0.xx". The questions differ in what is given and what is asked — AQA asks for
  MPC, ours for MPW — but the sentence was shared almost word for word, and the
  run also matched the AQA papers. Rebuilt around a household receiving an extra
  £100 and splitting it in pounds, which is both distinct and closer to how the
  Edexcel page presents it.
- 2.4.1 Q6 shared "in the basic two-sector circular flow model" with AQA 2.2.1
  Q3; reworded to "the simplest circular flow model, containing only households
  and firms".
- 2.4.2 Q2 shared "a withdrawal from the circular flow of income" with both the
  Edexcel papers and AQA 2.2.1 Q1. Reworded to use **leakage**, which is the
  Edexcel page's own alternative term for the same thing.

**The multiplier needed different framings, not different numbers.** AQA 2.2.4's
ten questions take every standard archetype: 1/MPS, 1/MPW, the multiplier from a
propensities table, the final rise from an injection, the multiplier implied by
an injection and an outcome, and two economies compared. What was left, and what
this set uses:

- **Work backwards from the target.** Given the multiplier and the desired rise
  in GDP, find the injection needed. AQA always runs it forwards.
- **The single-leakage trap, stated in the stem.** The Edexcel page makes a point
  of it — using MPS alone gives 10 instead of 2.5. Q2 hands the student the wrong
  answer of 20.0 and asks for the right one, with each distractor being a
  different single leakage.
- **The two formulas agreeing.** Q5 asks what 1 ÷ (1 − MPC) gives when 1 ÷ MPW
  has already given 2.5. The answer is that they are the same equation, which is
  a genuinely useful thing to know and which AQA never tests.
- **The multiplier in reverse.** Q9 cuts government spending by £2bn with a
  multiplier of 3. Students routinely treat the multiplier as applying only to
  increases, and nothing in the bank tested it.
- **Confidence as a determinant**, which Edexcel lists and AQA does not.

**Where else Edexcel differs:**

- The **output method** of measuring national income. AQA uses the expenditure
  method and, in the Edexcel 2.1.1 set, the income method — the output method was
  still free.
- The **financial sector as the link between saving and investment**, which the
  Edexcel page draws out explicitly by naming the source or destination of every
  flow. 2.4.2 Q3 turns on it.
- **An LRAS shift lowering the price level** while raising output (2.4.3 Q5). The
  Edexcel page states it in Figures 5 and 6; it is the cleanest statement of why
  supply-side improvement is preferred to demand-side stimulus.

| | |
| --- | --- |
| Answer letters | A 8, B 9, C 9, D 5 (even would be 7.75) |
| Skills | applied-reasoning 18, calculation 6, definition-in-context 5, data-table 2 |
| Difficulty | foundation 5, standard 22, stretch 4 |
| Sketch to solve | 1 |

`calculation` at 19% is the second highest of any batch, behind unit 2.1's 23%.
The multiplier and the circular flow identity both support real arithmetic, and
the J = W condition gives two good "find the missing component" items that need
no table at all.

---

### Batch 16 — Edexcel Theme 2 unit 2.3, plus a retrofit pass (2026-08-01)

**Two things in one batch: 3 new topics (23 questions) and 10 questions added to
six already-committed sets.** 33 questions in total, all re-derived from the stem
alone with **0 mismatches**.

#### The retrofit — a ratified change of policy

Until now, every Edexcel set was written strictly to what its notes page body
actually teaches, and concepts the page merely *advertised* were left out. Ten
questions were skipped that way across six sets, all recorded in `REVIEW-NOTES.md`
under N-Q8 and N-Q9.

**The site owner has now asked for those concepts to be covered anyway**, and
will bring the notes pages up to match afterwards. So they were written and
added:

| Set | Concept | Questions | New size |
| --- | --- | --- | --- |
| 1.3.4 | adverse selection; moral hazard | 2 | 5 → 7 |
| 1.4.2 | regulatory capture | 1 | 6 → 7 |
| 2.1.1 | actual against potential growth; productive capacity | 2 | 8 → 10 |
| 2.2.2 | the role of expectations | 1 | 8 → 9 |
| 2.2.3 | the accelerator effect | 2 | 7 → 9 |
| 2.2.5 | Marshall-Lerner and the J-curve, by name | 2 | 7 → 9 |

**How to do this safely.** Appending to a committed set rather than regenerating
it keeps the existing questions and their ids untouched, which matters because
`id` is unique site-wide and the JSON-LD is derived from it. The retrofit script
loads each file, appends question objects with ids continuing the sequence,
re-runs the letter-distribution and option-length assertions over the *whole*
set, and writes back. Two points learned:

- **The script writes per file, so a mid-run assertion failure leaves earlier
  files already modified.** `git checkout -- questions-data/` before re-running,
  or the additions get applied twice.
- **Adding questions changes the set's letter distribution**, so pick the answers
  to improve it. Every one of the six sets came out closer to even than before.

**The model answers are carrying the teaching here**, since the notes pages do
not yet cover these concepts. They were written longer than usual and to stand
alone for exactly that reason — a student who gets one wrong and returns to the
notes will currently find nothing there.

#### Unit 2.3 — Aggregate Supply

3 topics, 23 questions. `2-3-2` promised cost-push shocks and never covered them,
so that question (2.3.2 Q3) was written directly into the new set rather than
retrofitted.

**Originality: zero shared 8-word runs against either past-paper corpus.**
Against our own bank, six overlaps, all of them template scaffolding — "Using
Table 1, the only change that shifts…", "Table 1 lists four developments in an
economy", "while the average price level is unchanged". None was scenario
overlap, which is the distinction §8 draws. Two were reworded anyway to keep the
signal clean.

**This was expected to be the hardest twin problem so far and it was.** AQA
2.2.2, 2.2.5 and 2.2.6 carry 23 questions over the same ground, including both
obvious sketch items. Unlike unit 2.2, Edexcel does not subdivide further than
AQA does, so there was no structural room. The angles had to come from what the
Edexcel pages emphasise differently:

- **Subsidies as an SRAS factor.** Edexcel lists them; AQA's SRAS factors do not.
- **The Keynesian curve's middle segment.** AQA's sketch item asks where the
  curve is perfectly elastic. The Edexcel page describes all three segments with
  reasons, so 2.3.3 Q1 asks what happens on the *upward-sloping* section — close
  to capacity but not at it — which AQA never tests.
- **Institutional quality** — property rights and corruption — as an LRAS factor.
  Edexcel lists it; AQA does not.
- **Competition policy and deregulation** as an LRAS factor, likewise.
- **The SRAS/LRAS relationship stated as a trend.** The Edexcel page says the
  economy tends towards its LRAS level while SRAS shocks are temporary
  adjustments around it. Two questions come from that framing.
- **The cost-push policy dilemma** (2.3.2 Q3): responding to a leftward SRAS
  shift by raising AD recovers output but pushes prices higher still. Nothing in
  the bank covered it, on either board.

| | |
| --- | --- |
| Answer letters, unit 2.3 | A 9, B 6, C 4, D 4 (even would be 5.75) |
| Skills | applied-reasoning 18, data-table 3, definition-in-context 2 |
| Difficulty | foundation 1, standard 18, stretch 4 |
| Sketch to solve | 1 |

`applied-reasoning` at 78% is the highest of any batch and `calculation` is zero.
Aggregate supply is a diagram-and-mechanism topic: there is nothing on these
three pages to compute. The single foundation item reflects the same thing —
almost every question needs a chained inference, because the bare definitions
were already used in unit 2.2.

**Site-wide letter distribution is now A 219, B 255, C 230, D 174 of 878.** D
remains under-used by about 45 against an even 219.5. Every individual set passes
the per-set check, and the retrofit improved six sets, but the site-wide skew has
not shifted much because it was built up over the first twelve batches. It is not
worth retrofitting further; it is worth continuing to order options by domain
sequence while drafting, which is what has kept the recent batches balanced.

---

### Batch 15 — Edexcel Theme 2, unit 2.2 (2026-08-01)

5 topics, 37 questions. **Aggregate Demand** — its components, the AD curve, and
each of the four components in its own topic.

All 37 re-derived from the stem alone with **0 mismatches**; 11 arithmetic
checks covering every figure and distractor.

**Originality: zero shared 8-word runs against either past-paper corpus, and one
collision against our own bank, fixed.** Edexcel 2.2.2 Q2 opened "In an economy
the marginal propensity to save is 0.15…", which is AQA 2.2.4 Q8 word for word
*and* uses the same MPS value. The two questions then diverge completely — ours
asks for the MPC, AQA's is a multiplier calculation — but the opening and the
number together were too close. Rebuilt around a household saving 0.2 of each
extra pound.

**Edexcel splitting AD into five topics is what made this batch possible.** AQA
covers the same economics in one set of nine (2.2.3 Determinants of AD) plus
parts of 2.2.2. Five separate Edexcel topics meant each component could be taken
further than a single shared set can go — consumption alone supports eight
questions on disposable income, the MPC, interest rates, confidence, wealth and
income distribution. Where Edexcel does *not* subdivide further than AQA, as in
unit 2.3, that structural room will not be there.

**Angles Edexcel opens that AQA does not:**

- **G excludes transfer payments**, stated explicitly on the Edexcel page. 2.2.1
  Q2 turns on where £90bn of benefits and pensions actually lands in the AD
  equation — not in G, but in C once recipients spend it.
- **The three reasons the AD curve slopes down are named** — wealth, interest
  rate and international trade effects. AQA asks the general question; the
  Edexcel set can test one specific effect and use the other two as distractors,
  which is a much better question.
- **The relative shares** (C ~60%, I ~14%, G ~25%, net trade ~1%) support a
  question about why a given percentage change in consumption matters far more
  than the same change in net trade.
- **Income distribution as a determinant of aggregate consumption** — that
  redistributing towards lower earners raises consumption because their MPC is
  higher. AQA has nothing on this, and it makes the best stretch item in the
  batch.
- **Animal spirits**, named on the Edexcel investment page. AQA does not use the
  term.
- **Gross against net investment with depreciation arithmetic.** AQA defines net
  investment; Edexcel works the subtraction, so the calculation is free ground.
- **Automatic stabilisers against discretionary policy as a contrast.** AQA has
  automatic stabilisers as a definition; Edexcel's page frames the pair, so the
  question can put both halves in one stem and ask which is which.

**A second over-promising page found: `2-2-5-net-trade`.** Its spec alert names
the **Marshall-Lerner condition** and the **J-curve**; neither term appears in
the body. This one is a softer case than the others in N-Q9 — the body *does*
describe the J-curve mechanism, in the note that a depreciation "may initially
worsen the trade balance before improving it" — it simply never gives it a name.
The question (2.2.5 Q4) tests the mechanism without using the label.

| | |
| --- | --- |
| Answer letters | A 11, B 11, C 9, D 6 (even would be 9.25) |
| Skills | applied-reasoning 24, calculation 5, definition-in-context 4, data-table 4 |
| Difficulty | foundation 6, standard 26, stretch 5 |
| Sketch to solve | 0 |

**No sketch items again**, and for the same reason as unit 2.1: the AD curve is
introduced here but the AD/AS diagram that makes sketching worthwhile arrives in
unit 2.3. Expect the share to recover there — and note that AQA 2.2.2 and 2.2.6
already use both obvious AS sketch items, so the Edexcel ones will need a
different angle rather than a different diagram.

**Five option sets needed lengthening** so the correct answer was not the
longest — the highest count since batch 12, and all in the same direction: the
correct option carried an explanatory clause the distractors lacked. Worth
watching when a set is written quickly.

---

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

## Edexcel Theme 2 — 24 of 24 topics, complete

**Final profile:**

| | |
| --- | --- |
| Topics | 24 of 24 |
| Questions | 198, against 187 planned |
| Answer letters | A 57, B 55, C 49, D 37 (even would be 49.5) |
| Skills | applied-reasoning 127, definition-in-context 31, calculation 21, data-table 19 |
| Difficulty | foundation 24, standard 147, stretch 27 |
| Sketch to solve | 2 |

Theme 2 is the site's best theme for arithmetic — `calculation` at 11% and
`data-table` at 10%, against 7% and 8% in Theme 1. The macro specification
carries it: GDP from its components, PPP conversion, index numbers, real wages,
the unemployment rate, the current account, net investment, the multiplier, the
output gap and the budget identity are all genuine calculations that the pages
support without invention.

**Only 2 sketch items across 198 questions**, against a ~10% target, and the
cause is structural rather than an oversight. AQA macro was written first and
took both obvious AS sketch items (2.2.2 and 2.2.6), the supply-side against
fiscal contrast (2.5.2) and the Phillips curve (2.3.4). Where Edexcel introduces
a diagram — the AD curve in 2.2, the trade cycle in 2.5.3, AD/AS in 2.6 — the
page has the figure printed on it, so asking a student to sketch what they are
looking at earns nothing. The two that survived are in 2.3.3 and 2.4.3, where the
Keynesian and Classical models have to be compared rather than reproduced.

`D` finished at 37 against an even 49.5, the same shortfall Theme 1 showed. It is
concentrated in units 2.1 to 2.4; the last two batches came in at D 5 of 31 and
D 10 of 34 respectively, so the drafting-order fix works when it is applied from
the start. Not worth retrofitting.

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
