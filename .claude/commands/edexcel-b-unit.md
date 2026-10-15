---
description: Write the Edexcel B revision-notes pages for one spec unit, e.g. /edexcel-b-unit 4.1
---

Write every Edexcel B topic page in spec unit **$ARGUMENTS**, to the standard the finished Theme 1 pages set (approved by Eliot, October 2026).

## Before you start

- Work on the current theme branch (`feature/edexcel-b-theme-N`). Never on `main`, never push.
- The unit's theme must already be open (its hub out of `notes-data/hubs/drafts/`). If `new_topic.py` refuses because it isn't, stop and tell me.
- Read: the project pack's `README.md` (writing brief) and this unit's entries in the matching `theme-N-coverage.md`, both in `../../05-website/drafts/edexcel-b-notes/`; `revision-notes/CLAUDE.md`; `../../00-context/writing-style.md` ("Website resources" and the AI-writing rules).
- Study the Theme 1 exemplars in `notes-data/topics/edexcel-b-theme-1/`. These are the house style for B, more than any Edexcel A page:
  - `1-2-5-the-wider-economic-environment` - points, chains of analysis and evaluation
  - `1-6-2-break-even-analysis` - maths
  - `1-2-2-entrepreneurial-motives` - short, simple paragraphs

## How a B page is written

**1. Structure from the spec.** Plan the H2s so every spec point (a, b, c...) is covered once, then add the coverage map's extras. Never follow PMT's order or headings.

**2. Adapt, don't copy.** Use the twin page(s) named in the coverage map: keep what fits B, drop what B doesn't have, add what B adds, and reword everything. B-ONLY topics come from the spec and subject knowledge. Open the PMT text only after drafting, to check nothing is missing. Never use its sentences, examples or order.

**3. Concise from the first draft.** Theme 1 needed two trimming passes, so write tight now:
- An explanation paragraph states the idea, the mechanism, and at most one example, usually in 30-55 words.
- No background, history, scene-setting, named theorists or dates unless the spec needs them. Don't repeat something a table or an earlier paragraph already says.
- Examples are simple and easy to follow. A short made-up example (a bakery, a café) beats a detailed real-world case. Use a real case only when it's well known and adds something, and keep its figures to the one or two that matter. Every figure you add is one more thing that can go out of date.
- Leave out content beyond the spec unless the coverage map lists it as an extra.

**4. Exam focus: point → chain of analysis → evaluation.** Wherever the spec asks about impacts, advantages and disadvantages, effectiveness, or effects on firms, consumers, workers or the government, write it as exam-ready points:
- Introduce the list with a `<p>` (e.g. "When the pound strengthens:"), then `<ul>` items written as `<li><strong>Who/what is affected:</strong> cause &rarr; step &rarr; step &rarr; outcome for a named stakeholder.</li>`. Chains are two to four links and end in costs, prices, sales, profit, investment, jobs, wages or real incomes.
- Cover both directions where the effects differ (a rise and a fall; winners and losers).
- Follow each set of chains with evaluation: `<p>The effect depends on:</p>` (or similar), then `<ul>` items `<li><strong>Factor:</strong> why it changes the answer.</li>`. Typical factors are size and duration of the change, time lags, PED or PES, how much the firm imports, exports or borrows, whether it can pass costs on, market structure, and spare capacity.
- Use `&rarr;` in prose and lists. Don't add `flow-chain` components. Never put a bare `<strong>` directly inside a `<ul>`.
- Definitional and calculation topics don't need this. Use it where it helps students write analysis and evaluation.

**5. Maths.** Each formula is display maths `\[ ... \]` on one source line (never wrapped, and never split inside `\text{}`), inside its paragraph, with `<!-- prettier-ignore -->` on the line above that paragraph. No `<strong>` around maths. A `formula-box` only if the page has a component slot spare. Check the rendering in a headless browser.

**6. House rules.** At most two components per page. Title Case H1 and H2s to match the existing notes. Spaced hyphens, never em dashes. No banned words or constructions from `writing-style.md`. British spelling. `key-definition` chips on first use of each defined term. Concept tables, formulas and figures don't count as components.

## For each topic in the unit, in spec order

1. **Scaffold:** `python3 scripts/new_topic.py edexcel-b <code> "<Title In Title Case>" --slug <slug>`. Dry run first, then `--apply`. The slug is the coverage map's "Proposed slug". Edexcel B is notes-only (D66), so no `questions-data/` record is needed. If the theme's first page needs a temporary one-page-spine declaration in `scripts/verify_page_shell.py`, add it, and remove it when the second page exists, as Theme 1 did.
2. **Write the slice** following "How a B page is written" above. The spec alert reads `Edexcel B unit X.Y.Z - <page title>. ...`.
3. **Diagrams.** Use the `reuse:` files with full `diagram-figure` markup, `width`/`height`, alt text written from the image's actual labels, and `Figure N:` captions. For a `draft:` diagram, leave `<!-- DIAGRAM PENDING: <name> -->` where it will go and note it in the review sheet. Diagrams are drafted in a separate batch per theme.
4. **Fact-check** anything marked FACT CHECK, and any figure or named example that could have changed, against its primary source. Record source and date in the review sheet. If you can't verify it, leave it out.
5. **Overlap check:** `python3 ../../05-website/drafts/edexcel-b-notes/check_overlap.py <slice> --pmt ../../05-website/drafts/edexcel-b-notes/pmt-text/<file>.txt --twin <twin slice> ...`. A PMT FAIL means rewrite and re-run. Reword near-matches unless they're a standard definition. A twin WARN means reword more of the adapted text.
6. **Self-edit pass** before building. Reread the page as Eliot would:
   - cut any paragraph over about 60 words down to its point
   - shorten any example that tells a story
   - turn any general "this affects firms" prose into chains and evaluation
   - check every spec point is still covered
7. **Metadata:** `timeRequired` = words ÷ 200, rounded. Meta description within `verify_seo`'s band.
8. **Build and verify:** `python3 scripts/build.py`, then `/verify`.

## When the unit is done

Write `../../05-website/drafts/edexcel-b-notes/review/unit-<X-Y>.md` with, per page:
- word count and components
- each spec point and the H2 that covers it
- the twin(s) adapted
- `check_overlap.py` results
- facts checked (source and date)
- diagrams used and pending
- anything you were unsure about, as numbered questions for Eliot

Commit the unit as one commit ("Add Edexcel B unit X.Y notes") with the trailers `suggest_trailers.py` gives. Then tell me which pages to open in Live Server. Don't start the next unit.
