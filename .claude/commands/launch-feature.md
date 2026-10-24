---
description: Switch a finished resource family on for a board, e.g. /launch-feature edexcel-b practiceQuestions
---

Launch **$ARGUMENTS** (`<board key> <feature>`, the feature being one of `practiceQuestions`, `flashcards`, `glossary`, `pastPaperBank`). D67. Run it on the feature's own branch, and only when Eliot says the feature is complete.

Launching publishes permanent URLs: GitHub Pages cannot redirect (CLAUDE.md rule 7). Every step below that adds a page or changes visible wording waits for Eliot.

## 1. Confirm it is complete

Use counts from the scripts, never a number written down.
- `practiceQuestions`: one `questions-data/<notesDir>/` record per topic for **every** group of the board, equal to `expectedTopics` (`python3 scripts/verify_notes_sequence.py` gives the per-board notes counts), and `python3 scripts/build_questions.py --check` clean.
- `flashcards`: one deck per group in `flashcards-data/<board>/`, every topic of the board carried by at least one card, and the deck-level fields approved (`review/flashcards-decks.md`).
- `glossary`: `practiceQuestions` already live (board_data refuses otherwise, because the taxonomy is built from those records). `extract_glossary.py` run, `verify_glossary.py` and `check_glossary_capitalisation.py --check` clean.
- `pastPaperBank`: `practiceQuestions` already live. Every paper in scope extracted and verified, `tags.json` complete for them, `verify_past_paper_tags.py` and `strip_source_attributions.py` (0 changes) clean.

If anything is short, stop and list it.

## 2. List every URL it will mint, for approval

Build into a throwaway worktree with the feature on, and list every new path the build writes: `git status --porcelain` there, with untracked files expanded. Compare it with the approved list in `review/phase-0-groundwork.md`. **Anything not on that list stops the launch** until Eliot approves it.

## 3. Switch it on

- Move the feature from the board's `staged` list to its `features` in `boards-data/boards.json` (drop `staged` if it empties). The slugs were approved in Phase 0 (D68) and are already in the record; the group names must be the ones Eliot approved.
- `python3 scripts/verify_boards.py --reseed`, and read the diff: it is the list of leaves that moved.

## 4. Everything that names the board's resources

Draft all new visible wording from the Edexcel A pattern into `/Users/eliotking/Desktop/Economics Academy/05-website/drafts/all-boards-parity/review/launch-<feature>.md`, and **get Eliot's approval before applying any of it**:
- the menus in `templates/header.html`, desktop and mobile (then the build bakes them into every page)
- the notes tail: it derives itself from `features` in `scripts/notes_extras.py`, but its per-directory maps (`FLASHCARDS_OF_DIR`) need the board's rows
- site search: `scripts/build_search_index.py` (`BOARD_HUBS` gains the board's new hubs; the `quiz` flag already follows `practiceQuestions`)
- hubs and board indexes: `build_questions.HUB_SECTIONS`, `build_glossary.BOARD_COPY`, the flashcards hub, the bank's board cascade
- the home page resource cards and the FAQ "Which exam boards are covered?" answer
- the lines on `revision-notes/index.html` that name boards

Frozen heads stay byte-identical (PROGRESS.md trap 8). Never change economics wording.

## 5. Build and verify

`python3 scripts/build.py`, then `/verify`, then `python3 scripts/suggest_trailers.py`. Commit with every `Text-Change:` / `Markup-Change:` line it prints.

## 6. Hand over

Name the pages to open in Live Server, at desktop width and at 360 px: the new hub or index, two topic pages, one notes page whose tail changed, and the menu. Then **ask before pushing**. After the push: `python3 scripts/build.py --sitemap`, commit the sitemap, and add the launch to the project's block in `PROGRESS.md`.
