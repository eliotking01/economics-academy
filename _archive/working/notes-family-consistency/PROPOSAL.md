# Notes family consistency — Gate 1

Branch `feature/notes-family-consistency`, from `main` after the notes
redesign merge (PR #30). **Final scope: the two diagram galleries** —
`/revision-notes/microeconomics-diagrams.html` and
`/revision-notes/macroeconomics-diagrams.html` — now wear the D61 system:
the shared sheet `css/pages/revision-notes-topic.css` plus a rewritten
`revision-notes-diagrams.css` for what only a gallery needs, and
`js/components/notes.js` for the enhancements. This is an application of
the settled design, not a new one; where a gallery needed something the
topic pages did not, the part is designed in the same grammar and the
decision is recorded below.

**Macro-application is reverted, not redesigned.** Its move onto the
system was built three ways (chips as no-JS jump links; labelled
always-visible groups; a ground-up rebuild as plain text-link lists —
the record branch `record/macro-application-attempts` holds each
version), and in every
version the filter panel intermittently painted squashed in Eliot's
browsers, Chrome and Safari both, its painted size varying with scroll
while its measured geometry stayed correct — a compositing fault that no
headless engine (Chromium real-clock, WebKit, Firefox) reproduced, and
that survived paint-isolation (`translateZ(0)`, `contain: paint`) and the
removal of the 90-row rail span. On Eliot's instruction the page, its
record, its sheet and `revision-notes-textbook.css` (which it alone
loads) are restored **byte-identical to the pre-task state** — proved by
`git diff` against the merge base — and every hook that pointed notes.js
at it is unwound. Its move onto the design is future work needing a
different approach (likely starting from why that page's paint misbehaves
when the 166 topic pages' identical rail construct never has).

Because the galleries are hand-written, **the built pages are the mock** —
open them in Live Server on this branch. Everything is committed; nothing
is pushed.

| Evidence | File (in `shots/`) |
| --- | --- |
| Micro gallery, 1280 / 360, top + full | `micro-1280-top/full.png`, `micro-360-top/full.png` |
| Micro gallery, JS off, both widths | `micro-1280-nojs.png`, `micro-360-nojs.png` |
| Macro gallery, same six | `macro-*.png` |
| A topic page and a hub, unchanged, for comparison | `topic-1-2-2-*.png`, `hub-theme-1-*.png` |
| Print preview, micro gallery | `micro-print.pdf` |
| Content-identity proof | `python3 _working/notes-family-consistency/check_content_identity.py` |

The proof reports, against the pre-redesign pages on `main`:

    microeconomics-diagrams: text identical, 3,653 words; 55 (src, alt) pairs, same order
    macroeconomics-diagrams: text identical, 2,232 words; 34 (src, alt) pairs, same order
    macro-application:       text identical, 9,319 words
    CONTENT IDENTITY OK

(macro-application is stronger than the proof needs: `git diff` against
the merge base shows zero difference of any kind - the revert is exact.)

Every caption, exam note and image is byte-identical, same order. The only
wording that changed is the galleries' navigation chrome listed in §3.

---

## 1. The galleries — decisions

**The card grid stays.** A gallery is a visual index of 55/34 diagrams; a
38em reading column would stack them into a scroll of five screens per
topic. So these two pages keep a wider content track — 50em, with the
same 14em sticky rail from 1024px that the topic pages have — and the
cards sit in the same auto-fit grid as before: two cards across at
typical laptop widths (each diagram larger than the old three-across),
three across on screens over 1680px, one column on phones. Everything
about the cards is now the topic pages' grammar: white ground, hairline
border, no drop shadow; the Theme/spec tags are quiet small-caps teal
text instead of boxed chips; card titles are the shared h3 treatment;
captions the shared muted caption.

**`exam-note` wears the exam-tip clothes** — green tint, 3px green rule —
and, like the spec panel and worked examples, its own bold "Use in
exams:" lead does the labelling; no CSS label added.

**The topic-jump-list became the "On this page" rail** — the same
`topic-contents` element the topic pages use, same anchors, same anchor
text, so the scrollspy highlights the section you are scrolled to from
1024px (notes.js gained a step-back on upward scroll for the tall-section
case, which mildly improves the topic pages too). On mobile it is the
same in-flow numbered box as a topic page. The heading "Contents" became
the label "On this page" (declared, §3).

**Every raster diagram gets the framed `diagram-zoom` tap-to-enlarge** —
a real link to the PNG with JS off, the `<dialog>` lightbox with JS on,
exactly the topic-page treatment. The two SVG diagrams (game theory on
micro, comparative advantage on macro) keep today's rendering with no
zoom — the same call D61 made for the one SVG topic page (4-1-2).

**First diagram promoted, rest lazy — yes.** Matching the topic-page
rule: the first diagram on each gallery lost its `loading="lazy"` and
gained `fetchpriority="high"`; the other 53/32 keep `loading="lazy"`.

**Mark-as-revised stays a topic-page thing**: notes.js now gates it on
the `.topic-meta` sub-label only topic pages have, so a reference page
never grows a toggle that would mean nothing there. The progress bar,
back-to-top, scrollspy and lightbox run on the galleries.

## 2. Shared decisions

**The notes-cta on both galleries.** Replaced by the D58-style close: a
two-panel "Carry on revising" unit (Glossary & Formulae; Past papers) and
one services sentence reusing D58's approved anchor texts ("online
A-Level Economics tutor", "A-Level Economics essay marking"). **Every
destination survives exactly once** — `/revision-notes/glossary/`,
`/past-papers/`, `/marking.html`, `/tutoring.html` — deliberately
unchanged, including the past-papers link staying the all-boards hub
rather than being upgraded to `/past-papers/edexcel/`, because the brief
pinned the destinations. (If you would rather the two Edexcel galleries
pointed at the Edexcel hub, that is a one-line change each — say so;
it changes a link destination, so it is not mine to decide.)
Macro-application keeps its original notes-cta, untouched.

**notes.js reaches the galleries through a declared hook, not hand-edited
tails**: a new per-page mechanism in `bake_templates.py`
(`EXTRA_COMPONENT_SCRIPTS`), restated independently in
`verify_page_shell.py`'s `EXTRA_SCRIPT_PAGES`, with the notes-other
script-tail shape reseeded 1 → 2. `revision-notes/index.html` and the
seven hub records stay on the plain tail.

**Two page sheets per page stays the arrangement for all three two-sheet
pages.** The galleries load `revision-notes-topic.css` plus their own
sheet; macro-application loads `revision-notes-textbook.css` plus its own
sheet, exactly as before this task — so the textbook sheet now serves one
page instead of three, and D61's "frozen for exactly three pages" note
needs a D62 amendment at Gate 2, not a deletion. `TWO_SHEET_PAGES` keeps
its three entries. The gallery sheet scopes every rule under the page's
own class and wins against the shared sheet by specificity, never load
order; no inline styles; no new icons; AA pairs pinned (two new gallery
pairs in `verify_contrast.py`; the four textbook pairs stay live).

## 3. Every visible string that changes

Both galleries only; declared with `Text-Change:`/`Markup-Change:`
trailers. Macro-application's wording is untouched end to end.

**Removed:** `Contents` (the jump-list heading); `Ready to apply these
notes?`; `Get Essays Marked`; `Book a Free Intro Call`; `Past Papers`
(button label; see replacement).

**Added:** `On this page` (the rail label, matching the 166); `Carry on
revising` (the unit label); `Past papers` (panel link, sentence case per
the D58 tail); `Definitions and formulae from the revision notes, in one
place.` (glossary panel note); `Question papers and mark schemes for
every board, by paper and year.` (past-papers panel note, adapted from
the D58 no-questions note); `Stuck on a diagram? Work through it with an
online A-Level Economics tutor in a free 15-minute intro call, or send an
essay for A-Level Economics essay marking.` (services sentence).

**Unchanged:** `Glossary & Formulae` (kept verbatim as its panel link),
the h1s, the subtitles, the breadcrumbs, every caption, exam note and
source-link.

## 4. What is verified already (formal report at Gate 2)

The whole `verify.yml` suite is green locally on the branch, including
`verify_generated.py` (0 files would change), both integrity checks
against the merge base (declared, nothing undeclared), the 39-case
compare-trees suite, `verify_css_load_order.py`, `verify_contrast.py`,
`verify_links.py`, `verify_html.py`, `build_sitemap.py --check` and
`seo/tools/verify_seo.py` (20/20).

One audit-script artefact, noted rather than fixed:
`docs/audit/scripts/link_graph.py` enumerates HTML pages only, so it
reports every `diagram-zoom` anchor to a PNG as a "broken internal
target" — 101 such lines already on `main` (from D61's topic-page zoom
links), 102 on this branch (the galleries link one PNG no topic page
does). The files exist and `verify_links.py`, the CI check, is green;
no-JS reachability stays 507/509, the same two exceptions as the recorded
baseline.

## 5. Stop

Waiting on your approval — of the two galleries as built, the decisions
in §1–2, and the wording list in §3. Gate 2 (formal verification report,
D62, PROGRESS.md, the CLAUDE.md updates, PR) follows once you have
reviewed. Two open questions: the galleries' past-papers link (§2), and
whether to log the macro-application paint fault anywhere permanent
(OWNER-TODO or REVIEW-NOTES) so the future attempt starts from what was
learned.
