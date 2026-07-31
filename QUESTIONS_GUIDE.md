# QUESTIONS_GUIDE

The authoring standard for the free end-of-topic practice questions under
`/practice-questions/`. Every question set is written to this document. Referenced
from `CLAUDE.md`.

Progress and batch state live in `QUESTIONS_PROGRESS.md`.

---

## Hard constraints

- **Every question is 100% original.** The AQA past-paper PDFs in `past-papers/` are
  calibration material for style and difficulty only. Never copy, closely paraphrase or
  reuse a stem, an option, a data set, a number or a phrase from them. If a draft
  question could be laid beside a real one and read as a rewrite, it is not original
  enough — change the context, the numbers and the reasoning step.
- **No question may require a displayed diagram.** Nothing is rendered on the page but
  text and tables. Questions that ask the student to *sketch* a diagram themselves to
  reach the answer are allowed and encouraged — tag those `"sketch": true`.
- **Board fidelity.** AQA sets use AQA terminology and AQA spec boundaries; Edexcel sets
  use Edexcel's. The two boards get fully separate sets even where the economics is
  identical. Never reuse a question across boards.
- **Never touch existing notes wording.** The only edit a question set makes to a
  pre-existing file is the additive end-of-notes block. See `CLAUDE.md`.

---

## Format

Four-option multiple choice, A–D, exactly one unambiguously best answer, calibrated to
AQA Paper 3 Section A.

**Calibration, from June 2019 and June 2023 Paper 3 Section A.** Thirty one-mark items
per paper. Stems are one to four short sentences. Options are short, parallel and
grammatically uniform, and are ordered alphabetically where they are noun phrases or
sentences. Knowledge alone is almost never enough — nearly every item needs one chained
inference on top of a definition. Distractors are plausible misapplications, never
jokes. There is no "all of the above" and no "none of the above".

### Skill mix

Each set should carry a spread of skills where the topic supports one. Target shares
across a set, mirroring the real papers with the diagram items redistributed:

| `skill` | Target share | What it looks like |
| --- | --- | --- |
| `applied-reasoning` | ~40% | "Which one of the following is most likely to…", "All other things being equal, the most likely consequence is…". One causal chain the student has to follow. |
| `data-table` | ~20% | A small HTML table the student must read and interpret. Not necessarily a calculation. |
| `calculation` | ~15% | Elasticities, index numbers, real vs nominal, the multiplier, exchange rates, costs, revenue, profit, tax incidence. |
| `definition-in-context` | ~15% | A term applied to a situation, not recited. "Regulatory capture describes a situation in which…" |
| `sketch` (`"sketch": true`) | ~10% | The student draws the diagram themselves to answer. Overlaid on the tags above — a sketch item still carries a `skill`. |

Narrow, definitional topics will not support the full spread. Concision beats coverage;
a five-question set of genuinely good questions beats a ten-question set with filler.

### Difficulty

| `difficulty` | Meaning |
| --- | --- |
| `foundation` | One step. A secure student answers it without hesitation. |
| `standard` | The default. One chained inference beyond the definition. This is Paper 3 Section A's centre of gravity. |
| `stretch` | Two chained inferences, or a calculation with a trap in it. No more than about two per set. |

### Distractors

Every distractor must reflect a real student misconception, and the model answer must
name it. The recurring ones:

- inverted elasticity formula (`%ΔP ÷ %ΔQ`)
- sign errors, especially XED for substitutes vs complements, and dropping PED's minus
  sign before rather than after classifying
- movement along a curve vs a shift of the curve
- nominal vs real, and index points vs percentage change
- denominator errors — dividing by the new value instead of the original, or by a level
  instead of a change
- average vs marginal (cost, revenue, product, tax rate)
- correlation read as causation from a data table
- confusing a policy's intention with its most likely effect

Banned: joke options, "all of the above", "none of the above", "both A and B", options
that are true but do not answer the stem.

### Option hygiene

- Correct-answer letters roughly even across a set. The generator refuses a set where
  any letter's count is more than 2 away from even.
- Options parallel in length, grammar and form. The correct answer must never be the
  longest or the most hedged.
- Options in a natural order — ascending for numbers, alphabetical for noun phrases —
  so ordering carries no signal.
- Each option must be a complete, defensible statement on its own terms. A distractor
  that is obviously nonsense is a wasted option.

### Calculations

- Clean, realistic numbers. £ sterling for UK contexts.
- State units and any required rounding **in the stem**: "to one decimal place",
  "to the nearest £". If no rounding is stated the answer must be exact.
- Percentage changes are measured against the **original** value unless the stem says
  otherwise. The midpoint formula is not used anywhere on this site.
- Verify every figure by recomputation before the set is committed. Every number in a
  distractor must be reachable by the specific error the model answer names.

### Language

UK English throughout — *maximise*, *labour*, *behaviour*, *specialisation*,
*organisation*, *programme*. Standard A-Level terminology. Em-dash `—` in new prose.
Precise and plain: the register of the existing notes, not textbook formality and not
chat.

---

## Spec references

Use the spec code **exactly as the notes page uses it**, so a student never sees two
numbering systems.

- **AQA** — the site-local codes `1.x.y` (micro) and `2.x.y` (macro). These are
  deliberately not the real AQA 7136 codes; see `CLAUDE.md`. Do not "fix" them, and do
  not introduce `4.1.x` / `4.2.x` anywhere.
- **Edexcel (A)** — the real theme codes, `1.2.3`, `4.5.2`, and so on.

---

## Data schema

One JSON file per topic, hand-authored, committed:

```
questions-data/<board-dir>/<spec-code-with-hyphens>.json
questions-data/aqa-a2-micro/1-3-2.json
questions-data/edexcel-theme-1/1-2-3.json
```

`scripts/build_questions.py` reads these and writes the static pages. The JSON is the
single source of truth for both the visible HTML and the JSON-LD, so the two can never
drift.

### Topic object

| Field | Type | Notes |
| --- | --- | --- |
| `board` | `"aqa"` \| `"edexcel"` | Used in the localStorage key and `data-board`. |
| `boardDir` | string | Directory name, identical to the notes directory: `aqa-a2-micro`, `edexcel-theme-3`, … |
| `boardName` | string | Breadcrumb and dropdown label: `"AQA Microeconomics"`, `"Edexcel Theme 1"`. |
| `spec` | string | Spec code as the notes page writes it: `"1.3.2"`. |
| `slug` | string | **Byte-identical to the notes filename, without `.html`.** The generator checks the notes file exists. |
| `title` | string | Full topic title, as on the notes page `h1`. |
| `shortTitle` | string | Used in `h1`, buttons and links: `"Elasticities of Demand"`. |
| `pageTitle` | string | `<title>`. Authored per topic, targeting a real search term. Ends `\| Economics Academy`. |
| `metaDescription` | string | 140–160 characters. Natural, no keyword stuffing. |
| `intro` | HTML fragment | One or two sentences under the `h1`. |
| `notesTeaser` | HTML fragment | The sentence used in the end-of-notes block on the notes page. |
| `questions` | array | 4–10 question objects. |

### Question object

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | `"<board>-<spec-with-hyphens>-q<n>"`. Unique site-wide. |
| `skill` | enum | `calculation` \| `data-table` \| `applied-reasoning` \| `definition-in-context` |
| `difficulty` | enum | `foundation` \| `standard` \| `stretch` |
| `sketch` | boolean | `true` if the student needs to sketch a diagram. Renders a visible "sketch to solve" tag. |
| `stem` | HTML fragment | The question. Ends without a question mark where it reads as a sentence completion, matching AQA. |
| `table` | object \| absent | `{ "caption": "…", "head": […], "rows": [[…], …] }`. Rendered inside `<div class="table-container">`. |
| `options` | object | Keys `A`,`B`,`C`,`D`, all four required. |
| `answer` | `"A"`–`"D"` | The one best answer. |
| `model.working` | HTML fragment | Full worked reasoning for the correct option. For a calculation, every line of arithmetic. |
| `model.distractors` | object | One entry per **wrong** letter — all three required. Each names the misconception. |

### HTML fragments

`stem`, `intro`, `notesTeaser`, `model.working`, `model.distractors.*`, option values and
table cells are HTML fragments, not plain text. They are emitted verbatim into the page,
so they must already be escaped: `&lt;` for `<`, `&amp;` for `&`.

Allowed tags, enforced by the generator: `<strong>`, `<em>`, `<sub>`, `<sup>`, `<br />`.
Anything else is rejected. Use `<strong>` for key terms and figures, `<em>` only for
logical contrast — the same rule as the notes.

For the JSON-LD the generator strips tags and resolves entities, so schema.org gets
plain text.

**No LaTeX and no MathJax.** Questions pages do not load MathJax. Write maths with
Unicode: `×`, `÷`, `−` (U+2212 minus, not a hyphen), `%`, `£`, `≈`, `Δ`, `Q₁`, `P₂`.
Fractions go inline as `10 ÷ 20 = 0.5`.

---

## Worked example

The complete record for one question — the JSON, the HTML the generator produces from
it, and the JSON-LD. This is AQA 1.3.2, question 4.

### JSON

```json
{
  "id": "aqa-1-3-2-q4",
  "skill": "calculation",
  "difficulty": "standard",
  "sketch": false,
  "stem": "A supermarket raises the price of its own-brand tea. The price of its own-brand coffee is unchanged. Table 1 shows weekly sales of own-brand coffee before and after the price rise.<br />Measuring each percentage change against its original value, the cross elasticity of demand for own-brand coffee with respect to the price of own-brand tea is",
  "table": {
    "caption": "Table 1: Own-brand tea price and own-brand coffee sales",
    "head": ["", "Price of a pack of tea", "Packs of coffee sold per week"],
    "rows": [
      ["Before the price rise", "£2.00", "4,000"],
      ["After the price rise", "£2.40", "4,400"]
    ]
  },
  "options": {
    "A": "−2.0",
    "B": "−0.5",
    "C": "+0.5",
    "D": "+2.0"
  },
  "answer": "C",
  "model": {
    "working": "Cross elasticity of demand is the percentage change in the quantity demanded of one good divided by the percentage change in the price of another good.<br />Percentage change in quantity of coffee: (4,400 − 4,000) ÷ 4,000 × 100 = <strong>+10%</strong>.<br />Percentage change in the price of tea: (£2.40 − £2.00) ÷ £2.00 × 100 = <strong>+20%</strong>.<br />XED = +10 ÷ +20 = <strong>+0.5</strong>.<br />The sign is the useful part. A positive XED means the two goods are <strong>substitutes</strong>, which is what you would expect of tea and coffee: dearer tea pushes buyers towards coffee. A magnitude below 1 says they are weak substitutes — a 20% rise in the price of tea moved coffee sales by only 10%.",
    "distractors": {
      "A": "Both errors at once: the formula has been inverted <em>and</em> a minus sign carried across from PED. 20 ÷ 10 = 2, then negated.",
      "B": "The arithmetic is right but the sign is wrong. PED is negative for a normal demand curve, and that minus sign gets attached to XED out of habit. XED is negative only for <strong>complements</strong>. Here both percentage changes are positive, so the answer must be positive.",
      "D": "The formula has been inverted: 20 ÷ 10 rather than 10 ÷ 20. That measures the responsiveness of the price of tea to coffee sales, which is not what XED means. The percentage change in the <strong>quantity demanded of the other good</strong> always goes on top."
    }
  }
}
```

### Rendered HTML

```html
<li
  class="quiz-item"
  id="q4"
  data-qid="aqa-1-3-2-q4"
  data-board="aqa"
  data-spec="1.3.2"
  data-skill="calculation"
  data-difficulty="standard"
  data-sketch="false"
  data-answer="C"
>
  <h2 class="quiz-stem"><span class="quiz-number">4.</span> A supermarket raises the price of its own-brand tea. …</h2>

  <p class="quiz-tags">
    <span class="quiz-tag">Calculation</span>
    <!-- plus <span class="quiz-tag quiz-tag-sketch">Sketch to solve</span> when sketch is true -->
  </p>

  <div class="table-container">
    <table class="quiz-data">
      <caption>Table 1: Own-brand tea price and own-brand coffee sales</caption>
      <thead>
        <tr><th scope="col"></th><th scope="col">Price of a pack of tea</th><th scope="col">Packs of coffee sold per week</th></tr>
      </thead>
      <tbody>
        <tr><th scope="row">Before the price rise</th><td>£2.00</td><td>4,000</td></tr>
        <tr><th scope="row">After the price rise</th><td>£2.40</td><td>4,400</td></tr>
      </tbody>
    </table>
  </div>

  <fieldset class="quiz-options">
    <legend class="quiz-options-legend">Select one answer</legend>
    <div class="quiz-option">
      <input type="radio" id="aqa-1-3-2-q4-A" name="aqa-1-3-2-q4" value="A" />
      <label for="aqa-1-3-2-q4-A"><span class="quiz-letter">A</span> −2.0</label>
    </div>
    <!-- B, C, D identical in shape -->
  </fieldset>

  <p class="quiz-feedback" data-quiz-feedback role="status" hidden></p>

  <details class="quiz-model">
    <summary>Show model answer</summary>
    <div class="quiz-model-body">
      <p><strong>Answer: C (+0.5).</strong> Cross elasticity of demand is …</p>
      <p class="quiz-why-wrong-heading"><strong>Why the other options are wrong</strong></p>
      <ul class="quiz-why-wrong">
        <li><strong>A</strong> — Both errors at once: …</li>
        <li><strong>B</strong> — The arithmetic is right but the sign is wrong. …</li>
        <li><strong>D</strong> — The formula has been inverted: …</li>
      </ul>
    </div>
  </details>
</li>
```

Notes on the markup contract:

- The stem is an `h2`, so the page has one `h1` and a flat, logical heading list.
- Options are real radios in a `fieldset`/`legend`, so arrow-key navigation, grouping
  and screen-reader announcement are all native. No ARIA needed to make them work.
- `data-answer` is in the source. That is accepted — this is free content.
- `.quiz-feedback` ships `hidden` with `role="status"`, so the verdict is announced when
  `quiz.js` fills it. `quiz.css` reserves its height, so nothing shifts.
- `<details>` is the model answer. It works with JavaScript disabled. `quiz.js` may open
  it, never remove it.
- `.quiz-tags` always carries the skill label. A `sketch: true` question gains a second
  chip, `<span class="quiz-tag quiz-tag-sketch">Sketch to solve</span>`.

### JSON-LD emitted for this question

```json
{
  "@type": "Question",
  "eduQuestionType": "Multiple choice",
  "learningResourceType": "Practice problem",
  "name": "Cross elasticity of demand for coffee with respect to the price of tea",
  "text": "A supermarket raises the price of its own-brand tea. …",
  "acceptedAnswer": {
    "@type": "Answer",
    "text": "+0.5",
    "comment": { "@type": "Comment", "text": "Cross elasticity of demand is the percentage change in …" }
  },
  "suggestedAnswer": [
    { "@type": "Answer", "text": "−2.0", "comment": { "@type": "Comment", "text": "Both errors at once: …" } },
    { "@type": "Answer", "text": "−0.5", "comment": { "@type": "Comment", "text": "The arithmetic is right but …" } },
    { "@type": "Answer", "text": "+2.0", "comment": { "@type": "Comment", "text": "The formula has been inverted: …" } }
  ]
}
```

---

## Verification protocol

Run after **every** batch, as a separate pass, before the batch is committed. The point
is a genuinely fresh solve — read the stem and options only, work the answer out, and
only then look at `answer`.

1. **Re-solve cold.** For each question, answer it from the stem alone without reading
   `answer` or `model`. Compare. Any mismatch is a defect in the question, the key or
   both — fix it, do not rationalise it.
2. **One defensible answer.** For each of the three distractors, ask whether a
   well-taught student could argue it. If yes, the stem is underspecified. Tighten it.
3. **Arithmetic.** Recompute every number in the stem, the table, the correct option and
   the model answer. Confirm each distractor number is reachable by the named error.
4. **Spec reference** valid for that board, and in that board's own numbering.
5. **Letter distribution** within the set no more than 2 from even.
6. **Option parallelism** — length, grammar, form. The correct answer is not the longest.
7. **UK spelling** and A-Level terminology.
8. **Originality** — no stem, number or phrase traceable to a past paper.

`scripts/build_questions.py` enforces the mechanical subset of this (items 4–5 in part,
plus option count, duplicate ids, missing distractor explanations, banned option strings
and a US-spelling blocklist) and refuses to write a page that fails. Items 1–3 and 8 are
judgement and must be done by reading.

---

## Page and set checklist

Before a batch is committed:

- [ ] Every question re-solved cold; keys agree.
- [ ] `scripts/build_questions.py` runs clean.
- [ ] `python3 scripts/verify_html.py` clean over `practice-questions/`.
- [ ] `python3 scripts/verify_links.py revision-notes practice-questions` clean.
- [ ] Every notes page in the batch links to its questions page and vice versa.
- [ ] `sitemap.xml` updated.
- [ ] `python3 scripts/verify_text_integrity.py <base-ref>` clean.
- [ ] `python3 scripts/verify_markup_integrity.py <base-ref> --strict` clean.
- [ ] `git diff <base-ref> -- revision-notes/` contains no removed line.
- [ ] `QUESTIONS_PROGRESS.md` updated.
