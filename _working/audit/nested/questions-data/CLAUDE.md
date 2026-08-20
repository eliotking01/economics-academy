# questions-data/

**Source of truth for the FREE PRACTICE QUESTIONS at `/practice-questions/`** —
not for the past-paper bank, despite the name. `scripts/build_questions.py`
validates this and writes the 166 topic pages, five board indexes and the hub,
so the visible HTML and the JSON-LD cannot drift. Excluded from publishing.

**Every question here must be 100% original.** Eliot sells these; they must be
his own intellectual property. Never copy or closely paraphrase a real exam-board
question. `past-paper-questions-data/` is the bank that reproduces real questions
verbatim — **the two never share a data path**, in either direction.

Originality was checked mechanically on every batch: shingled against the AQA and
Edexcel past-paper corpora, against the rest of the bank, and by comparing numeric
option sets against option blocks extracted from the papers. Re-measured
2026-08-20: 0 exact and 0 near-duplicate stems across the two banks.

**Re-solve every new question cold from the stem alone** and diff against the
recorded key, before it is committed. That step has found real defects and is the
last thing to drop.

The authoring standard is `docs/QUESTIONS_GUIDE.md`. Read §8 (cross-board
duplication) and §9 (concept-grep) of `docs/QUESTIONS_PROGRESS.md` before
extending the bank — they decided the shape of every batch after the twelfth.

One file per topic: `<board-dir>/<spec>.json`, keyed by spec code with dots.
Question pages use `css/pages/quiz.css`; the hub and indexes use
`css/pages/practice-questions.css`.
