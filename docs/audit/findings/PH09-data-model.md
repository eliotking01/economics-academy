# Phase 9 findings — data layer & content model

Run 2026-08-09 on `audit/organisation-audit` at `d7744c3`.

**The data itself is consistent.** Keyed correctly, `taxonomy.json` and
`questions-data` agree on **166 of 166** topic titles and slugs — 0 disagreements.
Nothing below is a data-corruption finding. Everything below is about the
*model*: what is a key, where board identity lives, and what a third board costs.

---

## PH09-022 — Four independent board definitions, in four generators, one of which contains an explicit translation table

**Severity:** High · **Category:** Data model / scaling · **CERTAIN** ·
*This is the concrete form of PH00-003 and PH01-012*

**Evidence.** Every generator that needs to know what a board is defines it
again, in a different shape:

| Location | Structure | Keyed on | Carries |
| --- | --- | --- | --- |
| [`build_glossary.py:63`](../../scripts/build_glossary.py#L63) | `BOARDS` dict | `edexcel-a` | `slug`, `name`, `long`, **`taxonomy`**, `notesUrl`, `intro`, `meta` |
| [`build_past_paper_taxonomy.py:45`](../../scripts/build_past_paper_taxonomy.py#L45) | `BOARDS` list | `edexcel` | `board`, `name`, `qualification`, `papersUrl`, `groups[]` |
| [`build_flashcards.py:57`](../../scripts/build_flashcards.py#L57) | `NOTES_DIRS` dict | `(edexcel-a, theme-1)` | notes directory only |
| [`build_questions.py:61-113`](../../scripts/build_questions.py#L61-L113) | **five** structures — `PAST_PAPERS`, `BOARD_LABELS`, `BOARDS`, `BOARD_ORDER`, `BOARD_BLURB` | `edexcel` and `edexcel-theme-1` | labels, order, blurb, papers URL |

**The decisive detail.** `build_glossary.py`'s board record contains a field
called `taxonomy`:

```python
"edexcel-a": {
    "slug": "edexcel-a",
    "name": "Edexcel A",
    "taxonomy": "edexcel",      # <- the translation, written down once
    ...
}
```

That field exists for exactly one reason: the glossary calls this board
`edexcel-a` and the taxonomy calls it `edexcel`, and something has to bridge
them. **The need for a canonical board identity is already recognised in the
codebase** — it is just solved privately, inside one generator, where nothing
else can reach it.

**Why it matters.** This is the single biggest tax on the owner's stated goal.
It is not that the mapping is missing; it is that it exists four times in four
shapes and no two agree on what the board's identifier is.

One genuinely good thing to preserve:
`build_past_paper_taxonomy.py` ends with `EXPECTED = {"edexcel": 87, "aqa": 79}`
and asserts against it. Adding a board **fails loudly** there rather than
silently producing a short taxonomy. Whatever replaces these structures should
keep that property.

**Recommendation.** See "The `boards.json` design" below. **No URL changes.**

**Effort:** M · **Risk of acting:** Low if URLs are untouched · **Risk of not
acting:** High, paid again per board · **Dependencies:** P6 depends on this ·
**Status:** OPEN

---

## PH09-023 — Spec code is not a unique key: 37 of 129 codes mean different topics on different boards, and `questions.json` drops board from its topic key

**Severity:** Medium · **Category:** Data model · **CERTAIN (mechanism) /
SUSPECTED (that it will ever fire)**

**Evidence.** AQA notes use site-local codes `1.x.y` / `2.x.y` — ratified in
CLAUDE.md, deliberately not the real 7136 codes. What CLAUDE.md does not record
is that this puts them in **the same namespace as Edexcel's real codes**, which
are also `1.x.y` through `4.x.y`. They collide:

```
spec codes claimed by both boards: 37 of 129

1.1.1:  aqa=Economic Methodology            | edexcel=Economics as a Social Science
1.1.2:  aqa=The Nature and Purpose of …     | edexcel=Positive and Normative Statements
1.1.3:  aqa=Economic Resources              | edexcel=The Economic Problem
1.1.4:  aqa=Scarcity, Choice and …          | edexcel=Production Possibility Frontiers
1.2.1:  aqa=Consumer Behaviour              | edexcel=Rational Decision Making
1.2.2:  aqa=Imperfect Information           | edexcel=Demand
```

I hit this while auditing: joining `taxonomy.json` to `questions-data` on `spec`
produced **22 apparent title disagreements**. Re-keyed on `(board, spec)`:
**0 disagreements, 166/166 agree.** The data was never wrong; `spec` alone is
simply not a key, and it looks like one.

**Where this is load-bearing today.** `past-paper-questions/questions.json`
holds a `topics` dict of 151 entries keyed on **bare slug, no board prefix** —
0 of 151 keys carry a board — and every question's `topics` field is a list of
bare slugs. `js/components/question-search.js` resolves against that dict.

**It currently works, and it works by accident.** Tested directly:

```
questions-data:  166 (board,spec) records -> 166 distinct slugs, 0 collisions
taxonomy.json:   166 (board,spec) pairs   -> 166 distinct slugs, 0 collisions
```

No slug collides, because each slug is `spec-code` + `title` and no board pair
shares both. The 151-vs-166 gap is coverage, not collapse — 151 topics have at
least one past-paper question, and every one of the 151 is referenced by a
question with none orphaned.

**Why it matters.** The safety depends on two boards never giving the same spec
code the same topic title — for two syllabuses teaching the same subject, in a
namespace already colliding 37 times. If it ever happens, two boards' questions
merge under one key with **no error**: the search index would return AQA
questions on an Edexcel topic page. Silent, and plausible.

**Recommendation.** P6/P9. Make the topic key `board:slug` in `questions.json`
and in `tags.json` references. This is a **data-internal** change — it does not
touch a URL, since the URL already carries the board
(`/past-paper-questions/edexcel/<slug>/`). Requires a coordinated change to
`build_past_paper_questions.py` and `question-search.js`, and `tags.json` is
hand-written so its keys would need migrating rather than regenerating.

Cheaper interim: an assertion in the build that fails if two `(board, spec)`
records ever produce the same slug. Five lines, catches the silent case, changes
nothing.

**Effort:** S for the assertion, M for the real fix · **Risk of acting:** Low ·
**Risk of not acting:** Low probability, silent failure · **Dependencies:** none ·
**Status:** OPEN

---

## PH09-024 — Five ID grammars across five families, two of which disagree about the same board

**Severity:** Low · **Category:** Data model / consistency · **CERTAIN**

**Evidence.**

| Family | Example ID | Grammar |
| --- | --- | --- |
| MCQ question | `edexcel-1-1-1-q1` | `{board}-{spec}-q{n}` |
| Flashcard | `edexcel-a-1-1-1-def-01` | `{board}-{spec}-{type}-{nn}` |
| Past-paper question | `edexcel-a-p1-2017-jun-q6a` | `{board}-{paper}-{year}-{series}-q{part}` |
| Glossary term | `absolute-advantage` | `{slug}` — **no board** |
| Topic | `1-1-1-economics-as-a-social-science` | `{spec}-{title}` |

The first two are the same fact — a card and a question about Edexcel topic
1.1.1 — and they disagree on the board prefix: `edexcel-` vs `edexcel-a-`. This
is PH00-003 again, now inside the ID namespace, where it is harder to fix later
because IDs may be persisted. **Flashcard IDs are persisted**: Leitner state is
keyed on card ID in `localStorage`, so renaming one resets a student's progress.

Glossary terms carry no board in the ID because a term can belong to both — 234
of 325 do. That is a correct modelling decision, not an inconsistency, and
should be left alone.

**Recommendation.** Do not renumber anything. Record the grammars in the
conventions doc, note that flashcard IDs are effectively immutable because of
`localStorage`, and specify one grammar for new families.

**Effort:** S · **Risk of acting:** Medium if IDs are changed — resets student
progress · **Risk of not acting:** Low · **Dependencies:** P10 · **Status:** OPEN

---

## The `boards.json` design

Answers PH09-022. Written as a proposal, not applied.

**Governing constraint: this file records what the slugs already are. It does not
change any of them.** Every value below was read from the current repo. Adopting
it is a refactor of four hardcoded structures into one, with byte-identical
output.

```jsonc
{
  "_comment": "Canonical board identity. Generators read this instead of
               hardcoding. Slugs are RECORDED, not chosen - changing one
               changes a live URL, which GitHub Pages cannot redirect.",
  "boards": {
    "edexcel-a": {
      "name":          "Edexcel A",
      "long":          "Edexcel A-Level Economics A",
      "qualification": "A Level Economics A (9EC0)",
      "slugs": {
        "pastPapers":  "edexcel",      // /past-papers/edexcel/
        "questionBank":"edexcel",      // /past-paper-questions/edexcel/
        "glossary":    "edexcel-a",    // /revision-notes/glossary/edexcel-a/
        "flashcards":  "edexcel-a",    // /flashcards/edexcel-a/
        "dataDir":     "edexcel-a"     // past-paper-questions-data/edexcel-a/
      },
      "groups": [
        { "id": "theme-1", "label": "Theme 1",
          "name": "Introduction to Markets and Market Failure",
          "notesDir": "edexcel-theme-1", "flashcardsSlug": "theme-1",
          "questionBankSlug": "theme-1" }
        // themes 2-4 likewise
      ],
      "specCodesAreReal": true,
      "expectedTopics": 87
    },
    "aqa": { /* same shape; groups micro/macro; specCodesAreReal: false */ }
  }
}
```

Three things this shape gets right that the current four do not:

1. **`slugs` is a map, not a value.** It stops the argument about which spelling
   of "Edexcel A" is correct by recording that all three are, per family. That is
   the honest model of a site whose URLs are frozen.
2. **`specCodesAreReal: false` makes the AQA site-local decision machine-visible.**
   Today it lives only in CLAUDE.md prose, and PH09-023's collision is its
   unrecorded consequence.
3. **`expectedTopics` preserves the loud-failure guard** already in
   `build_past_paper_taxonomy.py`.

Migration order, each step independently revertible and each verified by the
output being byte-identical:

1. Add `boards.json`. Change nothing. Add a test asserting it reproduces all four
   existing structures exactly.
2. Point `build_past_paper_taxonomy.py` at it — smallest, and `taxonomy.json` is
   generated so the diff should be empty.
3. Then `build_flashcards.py`, then `build_glossary.py`, then
   `build_questions.py` (largest — five structures).
4. Delete the hardcoded structures only once each generator's output is confirmed
   unchanged.

**`build_sitemap.py:93` is the precedent**: it parses `_config.yml` rather than
restating it, and that is why the exclude list has stayed correct.

---

## How you would add OCR notes today, vs how it should work

P9's deliverable. Not hypothetical — worked through against the actual code.

### Today

1. Choose a board slug — and choose it **five times**, because
   `/past-papers/ocr/` already exists and fixes one of them while the other four
   are open.
2. Create `revision-notes/ocr-<something>/` and hand-write every topic page.
3. `scripts/build_questions.py` — add to `PAST_PAPERS`, `BOARD_LABELS`, `BOARDS`,
   `BOARD_ORDER`, `BOARD_BLURB`. Five edits, one file.
4. `scripts/build_past_paper_taxonomy.py` — add a `BOARDS` entry with its groups,
   and update `EXPECTED`.
5. `scripts/build_flashcards.py` — add `NOTES_DIRS` entries per theme.
6. `scripts/build_glossary.py` — add a `BOARDS` entry **and** fix line 679:

   ```python
   other_board = "aqa" if board == "edexcel-a" else "edexcel-a"
   ```

   This is a two-board assumption in a ternary. With a third board the glossary's
   "switch to the other board" link points somewhere wrong, and nothing errors.
7. `scripts/extract_glossary.py`, `verify_glossary.py`,
   `verify_past_paper_tags.py`, `extract_aqa_questions.py` — board literals in
   each.
8. `templates/header.html` — nav entries.
9. `js/components/inject-templates.js` — a `pageMap` rule if the URL does not sit
   under an existing prefix.
10. `_config.yml` — only if new data directories are added.

**Nine files, four of them generators, and one silent-failure ternary.** No
single place lists what a board is, so step 1's choice has to be re-made in each
file, and nothing checks the answers agree.

### With `boards.json`

1. Add one entry to `boards.json`, including the per-family slugs.
2. Create the notes pages and the source data.
3. Re-run the generators.
4. Add the nav entries in `templates/header.html`.

**Two hand-edited files.** The generators stop being places where board
knowledge lives and become things that read it. The `expectedTopics` guard still
fails loudly if the data does not match the declaration.

That is the whole argument for the change, and it is worth making **before**
another board or resource type lands, not after.
