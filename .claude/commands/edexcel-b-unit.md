---
description: Write the Edexcel B revision-notes pages for one spec unit, e.g. /edexcel-b-unit 1.3
---

Write every Edexcel B topic page in spec unit **$ARGUMENTS**.

The project pack is `../../05-website/drafts/edexcel-b-notes/`. Read its
`README.md` (the writing brief - every rule in it applies) and the unit's
entries in the matching `theme-N-coverage.md`. Also read
`revision-notes/CLAUDE.md` and `00-context/writing-style.md` ("Website
resources" and the AI-writing rules) at
`../../00-context/writing-style.md`.

Work on branch `feature/edexcel-b-notes`. Never push.

For each topic in the unit, in spec order:

1. **Scaffold** with
   `python3 scripts/new_topic.py edexcel-b <code> "<Title In Title Case>" --slug <slug>`,
   dry run first, then `--apply`. The slug is the coverage map's "Proposed
   slug" (1.6.2 is `1-6-2-break-even-analysis`, per D66). If the page
   already exists - 1.1.1 is a placeholder from setup - skip this and write
   into it. When 1.1.2 is created, delete the one-page-spine declaration
   for 1.1.1 in `scripts/verify_page_shell.py`, as `PROGRESS.md` says.
   Edexcel B is notes-only (D66): no `questions-data/` record is needed.
2. **Plan the page from the spec, not PMT.** List the H2 sections so every
   spec point (a, b, c...) is covered once, then add the coverage map's
   extras. Decide the (max two) components.
3. **Write the slice.** Adapt the twin page(s) named in the coverage map:
   keep what fits B, drop what B doesn't have, add what B adds, and reword
   throughout - B's spec wording, not the twin's sentences. B-ONLY topics
   are written from the spec and subject knowledge. Open the PMT text only
   after drafting, to check nothing is missing. Never take its sentences,
   examples or order.
4. **Diagrams.** Use the `reuse:` files with proper `diagram-figure`
   markup, width/height, alt text and `Figure N:` captions. For a `draft:`
   diagram, leave an HTML comment `<!-- DIAGRAM PENDING: <name> -->` where
   it will go and add it to the review sheet - drafting happens in a
   separate batch.
5. **Fact-check** anything marked FACT CHECK, and any other figure or
   named example that could have changed, against its primary source.
   Record source and date in the review sheet. If you can't verify it,
   leave it out.
6. **Check overlap:**
   `python3 ../../05-website/drafts/edexcel-b-notes/check_overlap.py <slice> --pmt ../../05-website/drafts/edexcel-b-notes/pmt-text/<file>.txt --twin <twin slice> ...`
   A PMT FAIL means rewrite the flagged passages and re-run until it
   passes. Reword near-matches unless they're a standard term. A twin WARN
   means reword more of the adapted text.
7. **Style pass.** No banned words or constructions from `writing-style.md`,
   spaced hyphens not em dashes, British spelling. Headings follow the
   existing Edexcel A notes (Title Case H1 and H2s), not the sentence-case
   rule in `writing-style.md` - matching the site wins here.
8. **Build and verify:** `python3 scripts/build.py`, then the `/verify` suite.

When the unit is done, write
`../../05-website/drafts/edexcel-b-notes/review/unit-<X-Y>.md` with, per page:
word count; each spec point and the H2 that covers it; which twin(s) were
adapted; `check_overlap.py` results; facts checked (source + date);
diagrams used and pending; anything you were unsure about, worded as a
question for Eliot. Commit the unit as one commit (message: "Add Edexcel B
unit X.Y notes"), then tell me which pages to open in Live Server. Don't
start the next unit.
