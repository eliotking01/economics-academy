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

## Adding one (the workflow; the authoring standard is `docs/QUESTIONS_GUIDE.md`)

1. **The notes topic must exist first** — `notes-data/topics/<dir>/<spec>-*.json`
   and a hub link (`python3 scripts/new_topic.py` scaffolds both). Every
   practice set belongs to a notes page; `build_past_paper_taxonomy.py` asserts
   that this directory has exactly `boards.json`'s `expectedTopics` records per
   board, so a set without its topic — or a topic without its set — fails the
   build.
2. Copy the nearest sibling `<board-dir>/<spec>.json` (same board, adjacent
   spec code) and rewrite every field: `spec`, `slug` (must match the notes
   slug), `title`, `shortTitle`, `pageTitle`, `metaDescription`, `intro`,
   `notesTeaser`. Write 4–10 questions to the guide; `validate()` in
   `build_questions.py` rejects anything outside that range, a duplicated `id`,
   or an uneven answer spread. Question `id`s are `<board>-<spec-with-dashes>-qN`.
3. **Re-solve every question cold from the stem alone**, then diff against
   your recorded key. This step finds real defects; do not skip it.
4. Originality: shingle against both past-paper corpora (see the note above)
   before committing. 0 exact, 0 near-duplicate stems is the bar.
5. `python3 scripts/build_questions.py --check` validates the inputs;
   `python3 scripts/build.py` writes the page (and everything else). The
   "Practice questions" panel at the foot of the topic's notes page is
   generated from this record - `notesTeaser` is its line of context and the
   question count is `len(questions)` - so there is nothing to append; the
   notes page needs this record to build at all (`scripts/notes_extras.py`).
6. Suite (`/verify`), commit, then `python3 scripts/build.py --sitemap` and
   commit the sitemap. No verifier literal needs bumping: counts come from
   `boards.json`.
