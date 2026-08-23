# Topic-page tail redesign — proposal for approval

> **Approved 2026-08-23** (Eliot: option (b), strip the slices; `dateModified`
> not refreshed; wording as proposed) and built in the next commit. The
> `after-live-*.png` files are the rebuilt pages themselves - Edexcel 1.2.2
> and AQA 2.1.3 at 1280, Edexcel 1.2.2 and the single-section AQA 1.6.6 at
> 360. The rest of this file is the proposal as it was approved.

Branch `feature/topic-tail`. Nothing in the generator is touched yet: this
folder holds one static mock of `1-2-2-demand`'s new tail, before/after
screenshots at 1280px and 360px, and the wording list below. Open the mock in
Live Server at `/_working/topic-tail/1-2-2-demand-mock.html` — it loads the
live notes stylesheet plus `tail.css`, which is the CSS that will move into
`css/pages/revision-notes-textbook.css`.

| | Before | After |
| --- | --- | --- |
| 1280px | `before-desktop.png` — tail ≈ 1,150px tall | `after-desktop.png` — ≈ 530px |
| 360px | `before-mobile.png` — ≈ 2,100px (3+ phone screens) | `after-mobile.png` — ≈ 1,250px (under 2) |

## The new order and shape

1. **Related topics** — hairline rule, small label, three plain links in a
   row separated by a middle dot, then the twin-board sentence. No pills.
2. **Carry on with this topic** — the three free next steps as one unit: three
   quiet panels (flat light ground, 3px teal rule — the hub index's idiom in
   the notes palette), one column on a phone, three across from 768px. Each
   is a bold link plus one line of context. The 47 diagram-gallery sentences
   join the unit as its last line instead of floating centred on their own.
3. **About the author** — same words, a 3px blue rule instead of a filled box,
   smaller type. Still an `<aside>` with its label.
4. **One services sentence** — two real-text links, a 3px brand-red rule so it
   reads as "the paid thing" without being a billboard. A generator comment
   above it marks the newsletter insertion point; nothing is built there.
5. **Previous / next** — unchanged.

Every destination survives exactly once per page: the related topics, the
twin link, the quiz, the flashcard deck, the past-paper questions page (or
filtered search), the board's past-papers hub, the diagram gallery where it
was there, tutoring, marking, previous and next. `verify_seo.py` 18 (twins)
and 20 (author box) keep their anchors byte-for-byte.

## Wording — please approve, amend or strike

**Unchanged:** "Related topics", "Studying AQA/Edexcel instead?", "covers this
on AQA/Edexcel.", "About the author", the byline and bio, the prev/next
captions, the 47 diagram-gallery sentences (emitted verbatim from the slice),
and every quiz teaser ("Eight original multiple-choice questions on the law
of demand, …" — emitted verbatim from `questions-data/`, where it already
lives as `notesTeaser`, identical on 166/166).

**New (three strings):**

| Where | Text |
| --- | --- |
| Unit label | **Carry on with this topic** |
| Services line | **Stuck on this topic? Work through it with an _online A-Level Economics tutor_ in a free 15-minute intro call, or send an essay on it for _A-Level Economics essay marking_.** (italics = the two links; "free 15-minute intro call" is tutoring.html's own description) |
| End of the past-paper note | **Whole papers and mark schemes: _Edexcel past papers_.** (the board hub link, which today is the first CTA button) |

**Changed (derived or renamed):**

| Today | Proposed | Why |
| --- | --- | --- |
| button "Practice Questions: 1.2.2 Demand" | link **Practice questions: 1.2.2 Demand** | sentence case, consistent across the three |
| button "Revise 1.2.2 with flashcards" | link **Flashcards: 1.2.2 Demand** | same pattern as its neighbours |
| button "Past Paper Questions: 1.2.2 Demand" | link **Past paper questions: 1.2.2 Demand** | sentence case |
| "Flip through the Theme 1 deck filtered to this topic — definitions, diagrams and chains of reasoning, with your progress saved on this device." | **The Theme 1 deck filtered to this topic — definitions, diagrams and chains of reasoning, with your progress saved on this device.** | a fragment like the other two notes; say if you'd rather keep "Flip through" — one-line revert |
| "Two questions on Demand from the Edexcel A-Level papers, 2018–2020, 8 to 25 marks. Each one links straight to the page of the official mark scheme where its answer begins." (stale on 24 pages) | **Five questions from the Edexcel A-Level papers, 2017–2024, 4 to 25 marks, each linked to the page of the official mark scheme where its answer begins.** — derived at build time from `questions.json`; one question: "One question from the AQA A-Level papers, 2019, worth 25 marks, linked to …"; 36 topics whose questions include Edexcel AS papers now say "A-Level and AS papers" / "AS papers" (today's sentence calls them all A-Level, which is wrong for those) | can never go stale again; the topic name is dropped because the link above it already names the topic (and it fixes "One question on The National Minimum Wage") |
| 15 pages with no tagged past-paper questions (no block today) | third panel is the board hub itself: link **Edexcel past papers**, note **Question papers and mark schemes for every Edexcel A-Level and AS paper, by paper and year.** (the hub's own intro, shortened, with no year span to go stale; AQA reads "AQA A-Level and AS paper") | keeps the board link on every page; say if you'd rather a different line |

**Removed (166 pages):** "Ready to apply these notes?", the buttons "Edexcel /
AQA Past Papers", "Get Essays Marked", "Book a Free Intro Call", and the three
`<h2>`s "Test yourself on this topic", "Revise this topic with flashcards",
"Past paper questions on this topic". None of it is economics; all of it was
button copy. The three `<h2>`s going takes the site's heading count down by
471 and leaves every remaining notes `<h2>` a content heading.

**Also fixed while in there:** the small teal labels ("Related topics", "On
this page", the prev/next captions) move from `#2a8998` (4.09:1, fails AA) to
`#1f6b77` (6.1:1). Same hue, darker. The "On this page" label at the top of
the page is the same rule, so it changes too — say if you'd rather I left it.

## What the data says

- **24** of the 139 past-paper sentences are stale today (brief said 22 — the
  bank has grown since). **12** tagged topics have no block at all, including
  1.1.6 Types of economies (five questions and its own page). The redesign
  gives all 151 tagged topics a derived, current line.
- The quiz teaser is identical in the slice and in `questions-data/` on
  166/166, so the generator can take it from the data with no wording change.

## Two things to decide (I recommend the first in each)

**1. Where the tail lives.** Today the CTA box and the three resource blocks
are *in the 166 `notes-data/` slices*, not in the generator — only the related
block and author box are generated. Two ways to make the whole tail generated:

- **(a) Recommended — slices untouched; the generator ignores everything from
  `<div class="notes-cta">` to the end of the slice except the diagram-gallery
  line, and emits the new tail from data.** It asserts the legacy tail still
  has one of the known shapes and that the slice's teaser still equals the
  data's, so nothing can drift silently. Matches the repo's rule that slices
  are never written to, and — the real reason — `rewrite_notes_meta.py` takes
  each page's `dateModified` from the slice's last commit, so editing all 166
  slices would bump every "Updated" date to today the next time it runs, for
  a chrome change.
- (b) Strip the legacy tail out of the 166 slices once (scripted, verified
  link-for-link). Cleaner data, but it is a 166-file bulk edit of the slices
  and it carries the `dateModified` trap above.

**2. `dateModified`.** The last three chrome passes (prev/next, author box,
performance) did not refresh it, so I will not run `rewrite_notes_meta.py
--apply`; the "Updated" dates stay as they are. Say if you want otherwise.

## What changes in the tooling (for the record, no decision needed)

- `scripts/notes_extras.py` gains the tail builder; the nine chrome strings
  list at its top becomes the full list.
- `scripts/append_past_papers_link.py` and `scripts/append_questions_link.py`
  are **retired** (deleted) — they wrote into rendered pages that the next
  build overwrote, which is how the counts went stale. `scripts/new_topic.py`
  and `scripts/CLAUDE.md` stop mentioning them; a new topic's quiz, flashcard
  and past-paper lines appear the moment its data exists.
- `scripts/verify_page_shell.py` check 6: the notes content spine goes from
  6 shapes to **1** (every page: top nav, header, spec-alert, contents,
  sections, related, next-steps, author, services, bottom nav). Reseeded
  deliberately, reason in the commit.
- `css/pages/revision-notes-textbook.css`: the `.notes-cta`,
  `.notes-questions-link`, `.topic-related` pill and `.topic-author` box rules
  are replaced by what is in `tail.css` here.
- Trailers: `Text-Change:` and `Markup-Change:` for all 166 pages, generated
  by `suggest_trailers.py`, and `verify_markup_integrity.py main --strict`
  run before the commit.

Reply with approvals/edits to the wording and the two decisions and I will
implement, rebuild the 166, run the full suite, eyeball Edexcel, AQA and the
single-section 1.6.6 page at both widths, and open the PR.
