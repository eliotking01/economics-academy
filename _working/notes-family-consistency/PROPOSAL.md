# Notes family consistency — Gate 1

Branch `feature/notes-family-consistency`, from `main` after the notes
redesign merge (PR #30). The last three pages on the old "textbook" design —
`/revision-notes/microeconomics-diagrams.html`,
`/revision-notes/macroeconomics-diagrams.html` and
`/revision-notes/macro-application/` — now wear the D61 system: the shared
sheet `css/pages/revision-notes-topic.css` plus a rewritten page sheet each,
`js/components/notes.js` for the enhancements, and
`css/pages/revision-notes-textbook.css` is deleted. This is an application
of the settled design, not a new one; where these pages needed something the
topic pages did not, the part is designed in the same grammar and the
decision is recorded below.

Because the galleries are hand-written, **the built pages are the mock** —
open them in Live Server on this branch. Everything is committed; nothing is
pushed.

| Evidence | File (in `shots/`) |
| --- | --- |
| Micro gallery, 1280 / 360, top + full | `micro-1280-top/full.png`, `micro-360-top/full.png` |
| Micro gallery, JS off, both widths | `micro-1280-nojs.png`, `micro-360-nojs.png` |
| Macro gallery, same six | `macro-*.png` |
| Macro-application, same six (the filters especially) | `macro-app-*.png` |
| A topic page and a hub, unchanged, for comparison | `topic-1-2-2-*.png`, `hub-theme-1-*.png` |
| Print preview, micro gallery | `micro-print.pdf` |
| Content-identity proof | `python3 _working/notes-family-consistency/check_content_identity.py` |

The proof reports, against the pre-redesign pages on `main`:

    microeconomics-diagrams: text identical, 3,653 words; 55 (src, alt) pairs, same order
    macroeconomics-diagrams: text identical, 2,232 words; 34 (src, alt) pairs, same order
    macro-application:       text identical, 9,319 words; 0 images
    CONTENT IDENTITY OK

Every caption, exam note, fact line, exam sentence, the worked example and
the specification sentence are byte-identical, same order. The only wording
that changed is the navigation chrome listed in §4.

---

## 1. The galleries — decisions

**The card grid stays.** A gallery is a visual index of 55/34 diagrams; a
38em reading column would stack them into a scroll of five screens per
topic. So these two pages keep a wider content track — 50em, with the same
14em sticky rail from 1024px that the topic pages have — and the cards sit
in the same auto-fit grid as before: two cards across at typical laptop
widths (each diagram larger than the old three-across), three across on
screens over 1680px, one column on phones. Everything about the cards is
now the topic pages' grammar: white ground, hairline border, no drop shadow; the
Theme/spec tags are quiet small-caps teal text instead of boxed chips; card
titles are the shared h3 treatment; captions the shared muted caption.

**`exam-note` wears the exam-tip clothes** — green tint, 3px green rule —
and, like the spec panel and worked examples, its own bold "Use in exams:"
lead does the labelling; no CSS label added.

**The topic-jump-list became the "On this page" rail** — the same
`topic-contents` element the topic pages use, same anchors, same anchor
text, so the scrollspy highlights the section you are scrolled to from
1024px. On mobile it is the same in-flow numbered box as a topic page. The
heading "Contents" became the label "On this page" (declared, §4).

**Every raster diagram gets the framed `diagram-zoom` tap-to-enlarge** —
a real link to the PNG with JS off, the `<dialog>` lightbox with JS on,
exactly the topic-page treatment. The two SVG diagrams (game theory on
micro, comparative advantage on macro) keep today's rendering with no zoom
— the same call D61 made for the one SVG topic page (4-1-2).

**First diagram promoted, rest lazy — yes.** Matching the topic-page rule:
the first diagram on each gallery lost its `loading="lazy"` and gained
`fetchpriority="high"`; the other 53/32 keep `loading="lazy"`.

## 2. Macro-application — decisions

**It gets the topic-page chrome where the chrome earns it, authored in the
slice, not the generator.** The contents rail was the obvious win over 18
sections; it is grouped — four top-level entries (Before You Start, United
Kingdom, South Africa, How to Use Application Well) with a sub-list of the
nine topic sections per country — because a flat list of 20 would repeat
"Labour Market" twice with nothing telling them apart. The rail is written
into the slice rather than derived by `notes_extras.py`: that module's
anchors are measured contracts across the 166 *topic* slices (bare `<h2>`s,
one container shape), none of which hold here, and a one-page carve-out
with its own anchor contract is more machinery than one hand-maintained
nav block in a slice that gains a section roughly never. The trade: if a
section is ever added, the rail is edited by hand in the same slice — same
as the galleries, and `verify_links.py` catches a dangling anchor.

**No byline, no D58 topic tail.** The byline and the "About the author"
block are wired to the topic schema (`verify_seo.py` assertion 20 holds the
page and its LearningResource to the same person), and this page's head is
frozen with no author node; a page-only byline would split that. The D58
practice/flashcards/past-paper panels are derived per topic and this page
has no topic record, no board and no twin. Both are possible later as their
own decision. The page keeps the topic layout (38em column), with the fact
cards stacked single-column — with the filters and the rail doing the
finding, two cramped columns of prose cards bought height at the cost of
readability.

**The filters now work without JavaScript — this is the fix the brief
flagged.** On the live page the 21 filter chips are `<button>`s wired by an
inline script, so with scripting off they are dead controls. They are now
real links, the mobile-nav precedent: every topic chip jumps to its
section, UK/South Africa jump to their country blocks, and All jumps to the
top of the fact bank (a new `#application-bank` wrapper around the two
country blocks). Every fact is visible, every control does something. With
JS, `notes.js` upgrades the chips in place (role="button",
`aria-pressed`, preventDefault) to exactly the show/hide filtering the old
inline script gave — which is retired from the record's `afterScripts`, so
the page has no inline script left ("progressive enhancement via notes.js,
not a second script").

**Generated component labels are suppressed where a card labels itself.**
The 50 fact cards carry `class="application"`, so the shared sheet would
stamp "APPLICATION" on every one — noise when each card has its own h4
title. Suppressed, on the worked-example precedent ("the heading is the
label"); same for the closing section's two h4-led blocks, including the
`evaluation-point` whose generated "Evaluation" label would actually
mislabel it ("Five habits for stronger application" is advice, not
evaluation). The one `exam-tip` keeps its label — it has no heading.

## 3. Shared decisions

**The notes-cta, on all three.** Replaced by the D58-style close: a
two-panel "Carry on revising" unit (Glossary & Formulae; Past papers) and
one services sentence reusing D58's approved anchor texts ("online A-Level
Economics tutor", "A-Level Economics essay marking"). **Every destination
survives exactly once** — `/revision-notes/glossary/`, `/past-papers/`,
`/marking.html`, `/tutoring.html` — deliberately unchanged, including the
past-papers link staying the all-boards hub rather than being upgraded to a
board page, because the brief pinned the destinations and macro-application
is genuinely board-neutral. (If you would rather the two Edexcel galleries
pointed at `/past-papers/edexcel/`, that is a one-line change each — say
so and I will make it; it changes a link destination, so it is not mine to
decide.)

**notes.js is the one enhancement script, and it reaches the three pages
through the declared hooks, not hand-edited tails.** The galleries get it
from a new per-page hook in `bake_templates.py`
(`EXTRA_COMPONENT_SCRIPTS`), macro-application from a named carve-out in
`build_notes_pages.py`; `verify_page_shell.py` restates all three in
`EXTRA_SCRIPT_PAGES`, and the notes-hub / notes-other script-tail shape
pins were reseeded 1 → 2 (the six board hubs and `/revision-notes/` stay
on the plain tail — they are index pages and out of scope). Three notes.js
changes, each degrading cleanly on pages that lack the markup:

1. **Mark-as-revised is gated on `.topic-meta`** (the sub-label only topic
   pages have), so the three reference pages don't grow a toggle that means
   nothing there. Progress bar, back-to-top, scrollspy and lightbox run
   everywhere.
2. **The scrollspy steps back on upward scroll**: these pages anchor the
   rail on tall sections, which never re-fire the observer on the way back
   up, so the highlight now falls back to the previous link when the
   current target scrolls out below the band. (Mildly improves the topic
   pages too.)
3. **The fact-bank filter module**, keyed on `#filter-bar`, inert
   everywhere else.

**Two page sheets per page stays the arrangement.** Each page loads
`revision-notes-topic.css` (the system) plus its own sheet (only what it
alone needs) — no gallery or filter rule touched the shared sheet the 166
load. `TWO_SHEET_PAGES` keeps its three entries (they are paths, so only
its comment changed). Both rewritten sheets scope every rule under the
page's own class and win against the shared sheet by specificity, never
load order; no inline styles; no new icons; AA pairs pinned — seven new
entries in `verify_contrast.py` (gallery meta tags, exam-note lead, chip
rest/active states, exam sentence on its tint, the closing evaluation h4),
the four textbook.css pairs and one dead `.section-placeholder` pair gone
with their rules.

**revision-notes-textbook.css is deleted.** `verify_css_load_order.py` is
green with no page loading it; a stylesheet is not an indexed page, so hard
rule 7 does not apply. Every live comment that pointed at it (main.css,
quiz.css, flashcards.css, glossary.css, past-paper-questions.css,
webfonts/FONTS.txt, the verifiers) now points at revision-notes-topic.css;
mentions in docs/audit history and _working/ design records stay as
history. The Merriweather @font-face it declared lives on in
revision-notes-topic.css, which all three pages now load.

## 4. Every visible string that changes

All on the three pages only; declared with `Text-Change:` trailers, one per
page, in commit `f95f1132`. The economics content is untouched (§ proof
above).

**Removed:**

| String | Where |
| --- | --- |
| `Contents` (the jump-list heading) | both galleries |
| `Ready to apply these notes?` | all three |
| `Get Essays Marked` | all three |
| `Book a Free Intro Call` | all three |
| `Past Papers` (button label; see replacement) | all three |

**Added:**

| String | Where |
| --- | --- |
| `On this page` | all three (the rail label, matching the 166) |
| `Carry on revising` | all three (the unit label) |
| `Past papers` | all three (panel link, sentence case per the D58 tail) |
| `Definitions and formulae from the revision notes, in one place.` | all three (glossary panel note) |
| `Question papers and mark schemes for every board, by paper and year.` | all three (past-papers panel note; adapted from the D58 no-questions note) |
| `Stuck on a diagram? Work through it with an online A-Level Economics tutor in a free 15-minute intro call, or send an essay for A-Level Economics essay marking.` | both galleries (services sentence) |
| `Not sure how to work these into an essay? Practise with an online A-Level Economics tutor in a free 15-minute intro call, or send an essay for A-Level Economics essay marking.` | macro-application (services sentence) |
| The rail entries on macro-application repeat the page's own heading text (`Before You Start`, `United Kingdom`, the nine topic names each side, `South Africa`, `How to Use Application Well`) | macro-application |

**Unchanged:** `Glossary & Formulae` (kept verbatim as its panel link), the
h1s, the subtitles, the breadcrumbs, every filter chip (`All`, `UK`,
`South Africa` and the 18 topic chips — same text, `<button>` → `<a>`),
every caption, exam note, fact line, exam sentence and source-link.

## 5. What is verified already (full formal run is Gate 2)

The whole `verify.yml` suite is green locally on the branch, including
`verify_generated.py` (0 files would change), `verify_text_integrity.py` /
`verify_markup_integrity.py --strict` against the merge base (3 declared /
3 declared, nothing undeclared), `verify_css_load_order.py`,
`verify_contrast.py`, `verify_links.py`, `verify_html.py`,
`build_sitemap.py --check` and `seo/tools/verify_seo.py` (20/20). The
sitemap refresh is its own commit (the post-commit hook did it).

One audit-script artefact, noted rather than fixed: `docs/audit/scripts/
link_graph.py` enumerates HTML pages only, so it reports every
`diagram-zoom` anchor to a PNG as a "broken internal target" — 101 such
lines already on `main` (from D61's topic-page zoom links), 102 on this
branch (the galleries link one PNG no topic page does). The files exist
and `verify_links.py`, the CI check, is green; no-JS reachability stays
507/509, the same two exceptions as the recorded baseline.

## 6. Stop

Waiting on your approval — of the three pages as built, the decisions in
§1–3, and the wording list in §4. Gate 2 (formal verification report,
D62, PROGRESS.md, the CLAUDE.md updates, PR) follows once you have
reviewed. Say the word on the board-named past-papers question in §3
either way.
