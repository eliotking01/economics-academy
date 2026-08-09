# Open questions

Numbered, stable, never renumbered. Each carries a recommended default so the
answer can be "defaults except 4 and 9". Answered questions move to
`DECISIONS.md` and are marked ANSWERED here with a pointer.

---

## Answered in Phase 0

Q1–Q10 were put to Eliot at the Phase 0 checkpoint and answered "I approve the
plan" — all defaults accepted. See `DECISIONS.md` D1–D10.

---

## Open — raised by Phase 0, to be resolved in the phase named

### Q11 — Is the past-paper-questions section's lack of publisher markup deliberate? · **ANSWERED by measurement**

**Answered 2026-08-09 by Phase 4: no — it is template divergence.** The same 97
pages emit `WebSite` instead, a site-level entity that belongs on the homepage
only, and all 100 `WebSite` nodes lack the `potentialAction` that is its only
purpose. Two generators disagree about which site-wide entity a page carries.
Finding PH04-052; `DECISIONS.md` D26. **If it *was* deliberate, say so and it
stands** — but it cannot be, because those pages already name the site as
publisher via `WebSite` and `CollectionPage`.

### Q11 (original text, retained)

`EducationalOrganization` is emitted on 354 of 463 pages but on **none** of the
90 `/past-paper-questions/` pages, and on no section hub. Finding PH00-007.

**Why I can't answer it from the repo.** `seo/08-structured-data.md` records four
approved changes but does not say whether this was considered and declined.

**Recommended default.** Treat it as an oversight and make it uniform at the
generator in P4. If you deliberately kept publisher identity off pages that
reproduce Pearson's and AQA's question text, say so — that would be a good
reason, and it should be written down rather than left implicit.

**Phase:** P4.

### Q16 — Do the specification PDFs need removing from git history too?

**NEW, raised by P1.** `d220ad0` removed them from `HEAD`. They remain in git
history, and this repo is **public** — GitHub serves blobs from history, so
anyone with a commit SHA can still fetch them.

**Why this is a real question and not pedantry.** The stated reason for removal
was that they are Pearson and AQA copyright. If the concern was that the site
*presents* them as its own, `d220ad0` fully answers it. If the concern is
*distributing* them, it does not.

**Recommended default.** Leave history alone. `git filter-repo` rewrites every
commit SHA, which breaks every commit reference in `PROJECT-LOG.md`,
`PAST-PAPERS-PROGRESS.md`, the `seo/` reports and this audit — all of which cite
hashes — and requires a force-push to a branch that auto-publishes. That is a
large, irreversible operation against a low residual risk: two PDFs, in history
only, at unguessable URLs, that no one has ever linked to.

Reconsider only if a rights-holder actually asks. Then it is worth doing
properly, and the cost is justified.

**Phase:** none — yours to decide. Not blocking.

### Q17 — Is `logo/` published deliberately?

**NEW, raised by P1.** The current brand kit — 8 files, `logo/` — is served
publicly and referenced by **nothing**. The site header is text, not an image.

**Recommended default.** Keep it published and say so in `_config.yml`'s
"deliberately NOT excluded" block, on the grounds that a stable URL for the logo
kit is useful to hand to a third party. If that was never the intent, exclude it
— nothing breaks either way. Finding PH01-013.

**Phase:** P1 decision, executed by you.

### Q12 — `/specificiations/` — leave the typo, or unpublish the directory? · **ANSWERED**

**Answered 2026-08-08: removed from the repo.** See `DECISIONS.md` D12. The
licensing sub-question was answered too — they were not Eliot's to host.
Follow-on question about git history is Q16.

### Q12 (original text, retained)

Two exam-board spec PDFs at a misspelled live URL, linked from nowhere on the
site. Finding PH00-005.

**Recommended default.** Add `specificiations/` to `_config.yml`'s `exclude`,
**after** checking GSC for impressions on those two URLs. Nothing links to them,
so unpublishing costs no internal equity. Do not rename — that is a URL change
under a no-redirect host, and renaming to a *new* URL while the old one 404s is
strictly worse than either leaving it or removing it.

**Open sub-question I cannot answer:** are these PDFs yours to host? They are
Pearson and AQA copyright. That is a licensing call, not a technical one.

**Phase:** P1.

### Q13 — How much appetite is there for a build step, in principle? · **ANSWERED**

**Answered 2026-08-09: yes.** See `DECISIONS.md` D16. P6 costed all the options
and recommends one in D17; the follow-on questions are Q18–Q20 below.

### Q13 (original text, retained)

P6's whole shape depends on this. The options are not equally invasive:

1. **Nothing changes** — keep 463 hand-maintained `<head>` blocks, keep using
   scripted rewrites for sitewide changes.
2. **Jekyll front matter + `_includes`** — GitHub Pages already runs Jekyll.
   Adding front matter to a `.html` file changes no URL and needs no new tooling,
   but touches all 463 files once and makes the deploy dependent on Liquid
   parsing every page (a stray `{%` currently only risks markdown).
3. **Extend the existing Python generators** to cover the ~283 hand-written
   pages, so all 463 come from source data.
4. **A real static-site generator** — biggest change, biggest risk to URLs.

**Recommended default.** Cost 2 and 3 properly in P6, recommend one, and rule out
4 explicitly. Do not decide now — the point of P5/P9/P9b running first is to make
this decision on evidence.

**Phase:** P6. Answer at the P6 kickoff, not before.

### Q14 — Should the audit propose anything for the 283 exam-board PDFs?

They are 176 MB of the repo, the bulk of `.git`, and GSC treats most as
duplicates of other sites' copies. `seo/07b-link-decisions.md` already declined
to add links to them.

**Recommended default.** Out of scope for organisation. Note the repo-size
consequence in P1 and move on. Git LFS would rewrite history and break every
existing commit reference for a benefit (clone speed) that a solo project does
not need.

**Phase:** P1, one paragraph.

### Q15 — Is `backup-pre-enrichment` safe to delete?

Fully merged into `main`, like all 13 others, but its name claims a purpose
beyond a merged feature branch. Finding PH00-010.

**Recommended default.** P1 diffs it against `main` and reports whether it holds
anything unique. Delete only if the diff is empty. You run the deletion; the
audit is read-only.

**Phase:** P1.

---

## Open — raised by Phase 6

These three gate any implementation. Nothing in the P6 proposal starts until they
are answered.

### Q18 — Python shell module, or Eleventy? · **ANSWERED**

**Answered 2026-08-09: option (f), the Python shell module.** See `DECISIONS.md`
D18.

### Q18 (original text, retained)

`PH06-html-architecture.md` §2 costs six options. The recommendation is **(f)**:
a shared stdlib-only `scripts/page_shell.py` that all five generators import,
with output committed exactly as the existing 273 generated pages already are.

**Why it beats the named alternatives.** It is the only option that ends with the
`<head>` defined once. Jekyll's Liquid and Eleventy's Nunjucks cannot be called
from `build_glossary.py`, so either would leave the `<head>` defined twice, in two
languages — which is Phase 9b's central finding restated rather than solved. It
also changes no URL by construction, adds no dependency, keeps `_config.yml`'s
`exclude` list as the publishing gate, and makes rollback a plain `git revert`
that restores the served bytes exactly.

**Recommended default.** (f). Second choice **(d) Eleventy via GitHub Actions**,
which is the better tool in the abstract and the wrong shape for this repo today.

**Phase:** answer before any implementation begins.

### Q19 — Is GitHub Actions acceptable for verification only, never for deploy? · **ANSWERED**

**Answered 2026-08-09: yes.** Pages stays on branch-serving; `_config.yml`'s
`exclude` stays the publishing gate. See `DECISIONS.md` D18.

### Q19 (original text, retained)

The proposal adds a workflow that runs the ten-assertion harness plus the eight
`verify_*.py` scripts on every push, and **nothing else**. It does not build the
site, does not deploy, and does not change the Pages source from branch-serving.

**Why it is worth having.** A read-only workflow cannot break a deploy — the worst
case is a red tick. It closes PH01-017 (the sitemap drifts because nothing re-runs
`build_sitemap.py` after a commit) and gives PH09b-026's fixed `--check` somewhere
to run. It is also P10's "a named set of checks that could run on every push
without risking the deploy", delivered early.

**Recommended default.** Yes. Note it is the *only* new automation proposed;
switching Pages itself to Actions is explicitly **not** recommended, because that
disables `_config.yml`'s `exclude` list, which `DO-NOT-BREAK.md` names as the only
thing keeping working files off the site.

**Phase:** answer before any implementation begins.

### Q20 — Are the six deliberate normalisations approved, as separate later commits? · **ANSWERED**

**Answered 2026-08-09: yes, all six, each as a separate commit after its family has
migrated clean.** The three malformed pages in PH06-031 are **not** covered and
still need their own instruction. See `DECISIONS.md` D18.

### Q20 (original text, retained)

Migration is byte-identical by design. These are improvements the migration makes
cheap, and each is a **separate commit after** its family has already migrated
with a zero-diff harness pass — never during, because a failure during migration
would be ambiguous between "the template is wrong" and "the improvement is wrong".

| # | Change | Pages | Note |
| --- | --- | ---: | --- |
| 1 | `id="MathJax-script"` added to the 28 tags that lack it | 28 | Cosmetic; one asset, two markups today |
| 2 | `aria-label="Breadcrumb"` added | 341 | The newest 100 pages already have it |
| 3 | `<section id="main">` → `<main id="main">` | 462 | Anchor, id, class and CSS all preserved. Check for `section#main` CSS selectors first |
| 4 | `loading="lazy"` on the 94 images lacking it | 33 | Bandwidth only; `width`/`height` already present everywhere |
| 5 | The `<style>` block on `1-5-1-market-structures.html` moves to `revision-notes-textbook.css` | 1 | House rule |
| 6 | 44 hand-written pages' inline `style=` attributes become classes | 44 | PH00-008 |

**Not in this list, and needing its own approval:** the three structurally
malformed notes pages in PH06-031 (an `<h2>` before the `spec-alert`, and two
pages with prose outside any `<section>`). Those edits sit inside prose regions,
so they are a separate conversation under the standing rule that economics content
is never touched without explicit instruction.

**Recommended default.** Yes to all six, separately, after each family migrates
clean.

**Phase:** answer before Phase 5 of the migration plan.

### Q21 — Does implementation start now, or after the audit finishes? · **ANSWERED**

**Answered 2026-08-09: after.** P8 → P3 → P4 → P7 → P10 → P11, then implement
from P11's roadmap. See `DECISIONS.md` D20.

### Q21 (original text, retained)

**NEW, raised at the P6 checkpoint.** D18 fixes what gets built and how. It does
not fix when, and `DECISIONS.md` D19 records why that is a real question rather
than a formality:

- Migration Phase 7 (baking the header/footer) is **already gated on P3**.
- Two of the six approved normalisations — the 44 inline-`style` pages and the
  one `<style>` block — are **P8's subject matter** (PH00-008). Fixing them before
  P8 has audited the CSS means fixing them twice.

**Recommended default.** Finish the audit first (P8 → P3 → P4 → P7 → P10 → P11),
then implement from P11's prioritised roadmap with every finding in hand. The
proposal is written to be resumable and nothing in it decays.

*(P8 has since qualified this in one place: PH08-039 identifies a page that may
be rendering incorrectly on the live site today. See Q25.)*

**Sensible middle path if that feels too slow:** build migration Phases 0–2 now —
the harness, `verify_page_shell.py` and `page_shell.py` proven by self-test.
Those three touch **no published byte**: the harness lives in `_audit/`, and the
other two are new files under `scripts/`, which `_config.yml` already excludes.
They also freeze today's drift in place while the remaining phases run.

**Phase:** yours to decide. Blocking for implementation, not for the audit.

---

## Open — raised by Phase 8

Four questions. None blocks the remaining audit phases; all four shape what P11
puts at the top of the roadmap.

### Q22 — CLS: fix the past-paper-questions layout shift now, or roll it into P11? · **ANSWERED**

**Answered 2026-08-09: default.** `seo/09-web-vitals-baseline.md` corrected; the
fixes wait for P11. See `DECISIONS.md` D21.

### Q22 (original text, retained)

**The measurement is not in dispute and is already in the repo.**
`seo/lh-live-after-7run.json` records **CLS 0.253** on a past-paper-questions
page and **0.110** on a notes topic page, against Google's 0.1 "good" threshold.
`seo/09-web-vitals-baseline.md` still says, in a section its own supersession
banner does not retract, that "CLS is 0.000 on all six pages" and "no
layout-shift problem exists". Finding PH08-035.

**Three separable actions.** They are listed apart because they carry different
risk and only one of them is urgent:

1. **Correct `seo/09-web-vitals-baseline.md`.** A documentation edit outside
   `_audit/`, so the audit will not make it without your word. Cost: minutes.
   Value: the next person stops being told not to look.
2. **Reserve height for `.ppq-controls`** — one CSS rule in one generated
   stylesheet, affecting 90 pages. The mechanism is identified and certain: the
   panel ships `hidden`, nothing reserves its space, and it is revealed only after
   a 414 KB `fetch` resolves.
3. **Diagnose the notes-topic 0.110** with one Lighthouse run before proposing
   anything. Cause currently **UNKNOWN**; PH08-041's missing fallback font metrics
   are the leading candidate but that is a hypothesis, not a finding.

**Recommended default.** Do (1) now — it is a document, not the site, and a wrong
number in a protected report is the kind of thing that compounds. Hold (2) and
(3) for P11 per D20, but put them at the top of the roadmap: (2) is the highest
value-per-line change in the whole audit.

**Phase:** P11 for the fixes; (1) is yours whenever you want it.

### Q23 — The 112 diagram PNGs: re-encode, or adopt the 78 SVG twins? · **ANSWERED, then re-put as Q26**

**Answered 2026-08-09: adopt the SVGs, permission granted in this instance.**
Inspecting before swapping — CLAUDE.md standing rule 4 — found the premise wrong:
the SVGs are recompositions, and at least one drops a panel of economics content.
Nothing was swapped. See `DECISIONS.md` D24, finding PH08-047, and **Q26** below.

### Q23 (original text, retained)

**Facts.** 26.2 MB of PNGs, median intrinsic width 2,350 px, all 8-bit RGBA, in a
content column roughly 700–900 px wide. Mean **513 KB of images per notes page**;
heaviest page 1.9 MB. 78 of the 112 already have a hand-authored SVG in
`images/diagrams/svg/`, drawn for flashcards and verified against the PNG per
CLAUDE.md standing rule 4 — 18.2 MB of PNG against **184 KB** of SVG.
Finding PH08-034.

**Why this is your call and not the audit's.** Re-encoding is invisible: the same
diagram, fewer bytes. **Swapping in the SVGs changes what a student sees** on
94 pages, and standing rule 1 says no existing content changes without your
explicit approval. The 34 PNGs with no SVG twin would also have to stay, so a
partial swap leaves the notes visually inconsistent until they are drawn.

**Recommended default.** Re-encode only, for now: ~1,600 px, WebP, expect
26.2 MB → under 3 MB and ~450 KB off the average notes page, with no visual
change and — provided the aspect ratio is preserved exactly — **no HTML edit at
all**, because `width`/`height` are used only for aspect ratio under
`max-width: 100%`. Log the SVG swap as a separate, larger, approved-in-its-own-
right piece of work.

**Phase:** P11.

### Q24 — Are the four single-file front-end fixes worth taking before P11? · **ANSWERED**

**Answered 2026-08-09: no, hold for P11.** See `DECISIONS.md` D22.

### Q24 (original text, retained)

D20 says the audit finishes before implementation, and P8 does not ask to reopen
that. But four of its findings are **one-line edits to a single file each**, none
touches prose, none changes a URL, and none is affected by anything P3, P4, P7 or
P10 might find:

| Fix | File | Lines | Finding |
| --- | --- | ---: | --- |
| `font-display: swap` on FontAwesome | `css/fontawesome-all.min.css` | 3 | PH08-033 |
| `, sans-serif` on the base font | `css/main.css:249` | 1 | PH08-041 |
| Focus ring on 3 `outline: none` rules | 3 page sheets | 3 | PH08-040 |
| `<h1>` → `<p>` in the header template | `templates/header.html:4` | 1 | PH08-036 |

**Recommended default.** No — hold them for P11 with everything else, because
D20's reasoning still applies and none of the four decays. But they are flagged
here so that if you want visible progress during the remaining phases, this is
the set with the best ratio of value to risk, and the header `<h1>` change is the
one whose effect is largest (all 463 pages, from one line).

**Phase:** P11, unless you say otherwise.

### Q25 — The `$…$` MathJax delimiter · **ANSWERED**

**Answered 2026-08-09: the table renders correctly; the hazard is latent, not
live.** Remove the delimiter anyway as hardening, in P11. `DECISIONS.md` D23.

### Q25 (original text, retained)

All 126 MathJax pages enable `$` as an inline-maths delimiter, which CLAUDE.md
never documents — it names `\( … \)`. Two pages contain a literal `$` in prose,
and `revision-notes/aqa-a2-macro/2-1-4-uses-of-national-income-data.html` has
**seven**, in a purchasing-power-parity worked example. Line 515 puts two of them
inside a single table cell, which MathJax will pair and typeset as mathematics.
Finding PH08-039.

**What the audit cannot tell you.** Whether it visibly breaks. This audit does
not render pages, and guessing is against its own rules. **Opening that page in
Live Server and looking at the PPP table settles it in two minutes**, and that is
the repo's own documented verification method.

**Recommended default.** Check the page. Then remove `["$", "$"]` from
`inlineMath` on all 126 pages regardless of the answer — no page on the site uses
`$…$` as a delimiter, the only 8 literal `$` characters on the site are currency,
and removing it immunises every future page that mentions a dollar figure. It is
a `<head>` change and touches no economics wording.

**Phase:** the browser check is yours and worth doing now; the `<head>` change is
P11, or sooner if the check confirms breakage.

---

## Open — raised by the Phase 8 checkpoint

### Q26 — How should the SVG diagram adoption actually be sequenced? · **ANSWERED**

**Answered 2026-08-09: route (c).** Re-encode the PNGs; the SVG adoption becomes
its own project. Saving measured, not estimated — see `DECISIONS.md` D25.

### Q26 (original text, retained) · replaces Q23

You approved adopting the 78 SVG twins. Inspecting them before swapping — which
CLAUDE.md standing rule 4 requires — found that the question I asked you was
based on a wrong premise, and I stopped rather than proceed. Finding PH08-047,
decision D24.

**What inspection found.** The SVGs are not the PNGs in another format. Every one
is drawn to a 4:3 flashcard canvas; 76 of the 78 PNGs are a different shape. Two
of the four pairs I rendered are faithful redraws (`laffer-curve`,
`supply-of-labour-market-individual` — both panels intact). One is not:
**`perfect-competition-short-run-supernormal-profit`'s PNG is a two-panel
market-and-firm figure, and the SVG is only the firm panel.** Swapping it would
remove the market diagram from two topic pages and the microeconomics gallery.
And aspect ratio does not tell the two cases apart — the faithful pair is *wider*
than the unfaithful one.

**Three routes, and none of them is "swap the 78".**

| | Route | What it costs | What you get |
| --- | --- | --- | --- |
| **a** | **Verify all 78 first, then swap only the faithful ones.** Each pair rendered and compared against the PNG *and* against the notes' own `<figcaption>` — a caption reading "the market and the firm" against a firm-only SVG is exactly what this catches. | ~78 image-pair comparisons. Real work, best done in board-sized batches across sessions. | An honest inventory, and a swap that cannot lose content. Still leaves 20 pages in two styles until (b) is done. |
| **b** | **(a), plus draw the 28 missing diagrams** to `docs/DIAGRAM_STYLE.md`, then convert everything in one step. | (a) + 28 new diagrams, each needing your approval under standing rule 2. | The notes end up in one style, ~18 MB lighter, no mixed pages, nothing lost. This is the version worth having. |
| **c** | **Re-encode the PNGs now (the original default), and treat (b) as a separate project.** | Small. No visual change, no HTML edit if aspect ratios are preserved. | ~450 KB off the average notes page this week, and the SVG project keeps all its value for later. |

**Recommended default: (c) now, (b) as the real answer.** They are not in
conflict — re-encoding costs nothing that (b) would waste, and it stops the notes
being the heaviest pages on the site while the diagram work is scheduled
properly. Doing (a) alone is the one combination I would avoid: it buys a
half-converted gallery and a standing inconsistency.

**If you want (b) started now, say so and I will begin the verification pass at
the next checkpoint** — it is a good use of a session, but it is a session, and
it is content work rather than audit work.

**Phase:** P11 for execution. The routing decision is yours.
