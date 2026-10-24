---
description: Write the Edexcel B practice MCQs for one spec unit, e.g. /edexcel-b-questions 1.6
---

Write the original practice questions for every Edexcel B topic in spec unit **$ARGUMENTS**, to the standard of the existing Edexcel A and AQA sets. D67 Phase 1.

## Before you start

- Work on `feature/edexcel-b-questions`. Never on `main`, never push. One unit per run, then stop.
- Phase 0 is answered (D68, `review/phase-0-groundwork.md`): sets live in `questions-data/edexcel-b-theme-N/`, the 89 URLs in that sheet's Q5 are approved, and B's `practiceQuestions` is **staged** in `boards-data/boards.json` while it is written. Staged means `build_questions.py` validates every B set with its normal rules and writes no page.
- **First unit only:** add `"staged": ["practiceQuestions"]` to the `edexcel-b` record if it is not there, and run `python3 scripts/verify_boards.py --reseed`. Before the first preview, B needs the fields its pages print, all visible wording drafted from the Edexcel A pattern and **listed for Eliot's approval** in that unit's review sheet: each B group's `names.practiceQuestions`, `practiceQuestionsLabel` and `practiceQuestionsButton` in `boards.json`, B's entry in `build_questions.HUB_SECTIONS`, and B's rows in `build_questions.UNITS` (the unit names, from the B notes hubs).
- These questions are sold, so they must be **100% original** (CLAUDE.md rule 4). Never copy or paraphrase a real exam question, and never open `past-paper-questions-data/` while writing.
- Read in full: `docs/QUESTIONS_GUIDE.md`; `docs/QUESTIONS_PROGRESS.md` "Recurring problems" §5 and §7-§9; `questions-data/CLAUDE.md`; every B notes page in the unit (`revision-notes/edexcel-b-theme-N/<slug>.html`); the unit's text in `/Users/eliotking/Desktop/Economics Academy/05-website/drafts/edexcel-b-notes/spec-edexcel-b-themes-1-4.txt`.
- Read two nearby Edexcel A sets **for calibration only**: format and difficulty. Never reuse a stem, number, context or distractor across boards.
- Edexcel B (9EB0) sets **no MCQs**. These are retrieval practice in the existing four-option format (D67), so do not claim exam style. Each set's `intro` and `notesTeaser` say "original multiple-choice questions" without "written to Paper N Section A style".

## For each topic in the unit, in spec order

1. **One record per topic** at `questions-data/edexcel-b-theme-N/<spec-with-dashes>.json`. Copy the shape of an Edexcel A record. `board` is `edexcel-b`, `boardDir` is the notes directory, `slug` is **byte-identical** to the B notes slug, and ids are `edexcel-b-<spec-with-dashes>-qN`.
2. **5-10 questions, aim ~7.** Fewer for a thin definitional topic. Concision beats coverage. Follow the guide's skill mix, difficulty spread, distractor rules, option hygiene and letter balance.
   - **B terms and B spec boundaries.** Every fact must be checkable on the B notes page or in the B spec text. Nothing only Edexcel A or AQA teaches.
   - Lean on B's business framing (firms, entrepreneurs, stakeholders, costs, cash flow, break-even, competitiveness) where the topic allows.
   - Prefer a scenario the student must interpret over a stock stem (§7: it is both more original and a better question).
   - No displayed diagrams. `sketch: true` items are allowed.
3. **Concept-grep (§9) before writing**: list the four or five ideas the set turns on and search the whole of `questions-data/` for each, so you know what is already tested.

## Checks, in this order

1. **Cold re-solve.** Write a temp file to the scratchpad holding only `board`, and per question `id`, `stem`, `table`, `options`, with `answer` and `model` stripped:
   ```bash
   python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(json.dumps({'board':'Edexcel B (9EB0)','questions':[{k:q[k] for k in ('id','stem','table','options') if k in q} for q in d['questions']]},indent=1))" questions-data/edexcel-b-theme-N/X-Y-Z.json > <scratchpad>/solve-X-Y-Z.json
   ```
   Give the path to the `cold-solver` agent in **solve** mode. Every mismatch, and every "more than one defensible" note, is a defect: fix the **question**, not the key, and re-solve the fixed items.
2. **Originality.** `python3 scripts/check_originality.py check questions-data/edexcel-b-theme-N/*.json`. Run `corpus` first if `_working/originality-corpus/` is missing. The bar is **0 EXACT and 0 NEAR** against the AQA, Edexcel A and Edexcel B papers and the bank. Read every READ line: a shared run inside the stem's own scenario is a port and gets rewritten, while shared house phrasing is fine. Compare archetypes for every REVIEW line.
3. `python3 scripts/build_questions.py --check` is clean.
4. **Local preview, never committed.** `EA_PREVIEW=edexcel-b:practiceQuestions python3 scripts/build_questions.py`, that generator **alone**: until all 85 sets exist, the full `build.py` stops at the notes tail, which needs a set for every B topic once practice is live. Name the pages to open. Then undo it: `python3 scripts/build.py` (restores the hub and indexes), delete the untracked `practice-questions/edexcel-b-theme-*/` directories after `git status` shows they are the only untracked paths, and check `git status` is clean apart from your source edits. A preview page that reaches a commit mints a permanent URL.

## When the unit is done

Write `/Users/eliotking/Desktop/Economics Academy/05-website/drafts/all-boards-parity/review/questions-unit-X-Y.md`:
- per topic: question count and skill mix
- **only** the items the solver disagreed with, and how each was resolved
- originality: the totals line, and every READ/REVIEW line with your verdict
- anything you were unsure about, as numbered questions for Eliot
- **3 random questions from the unit** reproduced in full (stem, table, options, answer, working) for his spot-check

Commit as one commit ("Add Edexcel B practice questions, unit X.Y") with whatever trailers `python3 scripts/suggest_trailers.py` prints (normally none: `questions-data/` is not published). Name the preview pages to open in Live Server. Don't start the next unit.
