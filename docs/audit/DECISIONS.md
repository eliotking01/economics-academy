# Decisions

Append-only. Never edit or delete an entry — supersede it with a later one and
say which it replaces.

---

## 2026-08-08 · Phase 0 checkpoint

Ten questions were put with recommended defaults. Eliot: **"I approve the plan."**
All defaults accepted, no exceptions.

### D1 — `_audit/` is gitignored, not committed

Added to `.gitignore` as the audit's first action; verified with
`git check-ignore -v` before a single file was written into it.

**Rationale.** GitHub Pages serves every committed file, so committing the audit
would need a second `_config.yml` exclusion to stay unpublished — and the repo is
**public**, so "unpublished" still means "readable by anyone who opens the repo".
`_audit/` is a running list of this site's own structural defects with evidence
attached. Not committing it is the only option that actually withholds it.

**Consequence, accepted.** Phase commits will contain nothing but the one
`.gitignore` line, so git history is not the audit's memory.
`_audit/PROGRESS.md` is, and it has to be good enough for a zero-context session
to resume from.

### D2 — Work on `audit/organisation-audit`, cut from `main` at `8c8034b`

No pushes. `main` auto-publishes; nothing here should reach it.

### D3 — PH00-001 (nav-only link equity) is logged, not acted on

Evaluated properly in P3. The audit does not edit the site.

### D4 — P5 reports the full similarity distribution and flags above 0.80

Recommends differentiation, **not** cross-board canonicalisation. Both boards are
meant to rank for board-specific queries. Any cannibalisation claim needs GSC
evidence of two of the site's own URLs competing on one query — similarity alone
is not evidence of harm.

### D5 — P6 gets its own session, after P1 → P5 → P9 → P9b

Its proposal depends on knowing what is already generated and how the boards
differ. Deciding the architecture before measuring that would be guesswork.

### D6 — P9b's idempotence check generates into a temporary tree and diffs

Never over the working tree. Regenerating in place would violate read-only, and
would silently destroy any hand-edit to a generated file — which is one of the
things P9b exists to detect.

### D7 — The 26 Finder duplicates are logged for Eliot to delete

The audit is read-only, including on ignored files. Root cause is iCloud/Finder
duplication of a synced folder, which is outside git's reach; the `* [0-9].*`
ignore rules added in `d1d05ad` are working (0 tracked), they just cannot stop
the files appearing on disk.

### D8 — `specificiations/` and `old-logos-archive/` are findings, not actions

Note that `/specificiations/` is a **live URL**, so correcting the spelling is a
URL change under a host with no 301s. See Q12.

### D9 — The six overlapping progress docs are audited for contradiction and staleness

Consolidation is proposed in P10; nothing is changed.

### D11 — The 26 Finder duplicates were deleted · **supersedes D7**

Eliot, 2026-08-08: "I give you permission in this instance to clear the 26 finder
duplicates." Done — 26 removed, 0 remain on disk, 0 were ever tracked. PH00-009
RESOLVED.

The permission was explicitly for this instance. The audit remains read-only; the
root cause (an iCloud-synced folder) is unchanged, so they will come back.

### D12 — The two exam-board specification PDFs were deleted from the repo

Eliot, 2026-08-08, answering Q12: "no please remove the specifications from the
repo" — i.e. they are not his to host. Committed as `d220ad0`.

**Deleted, not excluded.** Excluding via `_config.yml` would take them off the
site while leaving the files in the working tree, which answers a publishing
question rather than the copyright one actually asked.

**This was a deliberate URL removal**, against the standing "URLs are frozen"
rule, and is recorded as such. Justified because: nothing on the site linked to
`/specificiations/` (0 references across every `.html`, `.css` and `.js`), neither
URL appears in any GSC indexation export or in `seo/performance-pages.csv`, and
copyright outranks SEO. Link checker still reports 0 broken hrefs.

`sitemap.xml` and `sitemaps/` were **regenerated, not hand-edited** — pdfs.xml
283 → 281. `core.xml` also changed, which was unrelated pre-existing drift now
logged as PH01-017.

**Caveat that remains open.** The PDFs are gone from `HEAD` but still in git
history, and this repo is public — GitHub serves blobs from history. If the
concern is distribution rather than presentation, removing them needs
`git filter-repo`, which rewrites every commit SHA. Raised as Q16.

---

## 2026-08-09 · Phase 1 checkpoint

### D13 — `logo/` stays published, but as an **undecided** case

Eliot: "I'm not sure but yes keep it for now."

Recorded in `_config.yml` as UNDECIDED rather than moved into the "deliberately
NOT excluded" list. Writing it up as deliberate would have turned "not sure" into
"intended", and the whole point of that block is that it distinguishes decisions
from habits. The comment says nothing references it, that the header is text, and
that this should be revisited. PH01-013 stays OPEN.

### D14 — `.codex/` removed; its content moved to `docs/`, not deleted

Eliot: "Yes, but I don't use codex anymore." Committed as `d7744c3`.

**Moved rather than excluded or deleted.** Three things were true at once: the
directory had to go (unused tool), the URL had to go (internal instructions
served at `/.codex/notes-workflow.html`), and the file's *content* is still live
knowledge — it is the `raw-notes/*.md` → `revision-notes/*.html` conversion
procedure, and CLAUDE.md names `raw-notes/` as the source without ever writing
down the steps. Deleting it would have lost the only copy of a procedure still in
use.

`docs/` is already excluded, so the move needed no new `_config.yml` line — one
less thing to keep in sync, and it removes the second of the two genuine Liquid
deploy risks identified in PH00-011. Renamed to lowercase-kebab per PH01-018.

**This went further than the question asked**, which was whether to exclude
`.codex/`. Flagged in chat at the time so it could be reversed with one
`git mv`. PH01-014 RESOLVED.

### D15 — All 14 merged branches deleted, local and remote

Eliot: "I give you permission to do this in just this instance."

Deleted with `git branch -d` (not `-D`), which refuses anything unmerged, after
re-confirming all 14 reported 0 unique commits against `main`. Twelve had remote
counterparts and were removed with `git push origin --delete`;
`backup-pre-enrichment` and `seo/indexing-fixes` were local only.

**Verified after the fact:** all 14 branch tips
(`bf3d40e a635038 fa66ddb 175f0e0 2e1867a a26f4f5 75bee4f 929ff89 c666f13
0af7294 af8f410 5cdb4df 53a3e54 4ab54b7`) are still ancestors of `main`. No
history was lost; only the refs are gone. `main` untouched at `8c8034b`.

Permission was for this instance. The audit does not push.

PH01-010 RESOLVED.

### D10 — Branches are inventoried in P1, deleted by Eliot

All 14 are fully merged (`git branch --no-merged main` returns nothing).
`backup-pre-enrichment` gets a diff against `main` before any recommendation —
see Q15.

---

## 2026-08-09 · Phase 6 kickoff

### D16 — Q13 answered: there is appetite for a build step · **closes Q13**

Eliot, 2026-08-09: *"Yes, there is appetite for a build step, so you are welcome
to propose one, ensure it is explained to me."*

This unlocks options 2, 3 and 4 of Q13 rather than choosing among them. P6 costs
all five options the brief named plus one it did not, and recommends.

**Second instruction, standing:** everything written in chat and in the
progress-type documents is to be explained so a beginner can follow it.
`PH06-html-architecture.md` opens with a vocabulary section for that reason, and
future phase documents should do the same where they introduce tooling concepts.

### D17 — P6 recommends a Python shell module over Jekyll, Eleventy and Astro

Recommendation is **option (f)**: a shared stdlib-only `scripts/page_shell.py`
owning the `<head>`, wrapper, breadcrumb and script tail; a fifth generator for
the 190 hand-written pages; **output committed, exactly as the other 273 pages
already are.** Publishing, `_config.yml` and the Pages source are unchanged.
GitHub Actions is proposed for **verification only, never in the deploy path**.

**The deciding argument, recorded so it is not re-litigated from scratch.** Phase
9b named P6's central design question: a template layer over the hand-written 190
must either coexist with four Python generators that emit their own `<head>`, or
absorb them. **Liquid and Nunjucks cannot be called from `build_glossary.py`; a
Python module can be imported by all five generators.** Option (f) is therefore
the only one of the six that ends with the `<head>` defined **once**. Jekyll and
Eleventy both leave it defined twice, in two languages, which is Phase 9b's
finding restated rather than solved.

Second choice: **(d) Eleventy via GitHub Actions** — and if ever chosen, as a
whole-site rewrite that also absorbs the four Python generators, not as a layer
beside them. Third: **(c) Jekyll**, which changes no URL and adds no server
tooling but cannot be built locally on this machine to compare against.
**(e) Astro is ruled out** — highest URL risk on a site with two URL grammars,
and its distinguishing feature (islands for framework components) is one this
site has no use for.

**Nothing is implemented.** P6 wrote zero production code and changed zero files
outside `_audit/`. Q18–Q20 must be answered before any of it starts.

---

## 2026-08-09 · Phase 6 checkpoint

### D18 — Q18, Q19 and Q20 all answered: recommendations approved as put

Eliot, 2026-08-09: **"I approve all recommendations."** All three defaults
accepted, no exceptions.

**Q18 — the build step is option (f), the Python shell module.** A shared
stdlib-only `scripts/page_shell.py` owning the `<head>`, body wrapper, breadcrumb
and script tail; a fifth generator for the 190 hand-written pages; **output
committed**, exactly as the existing 273 generated pages already are. Jekyll,
Eleventy and Astro are all declined, for the reason in D17: only a Python module
can be imported by the four existing generators, so only option (f) ends with the
`<head>` defined once.

Consequences accepted: no hot-reload dev server; Python string templates have no
template language's guard rails; every notes edit becomes edit-fragment-then-
rebuild rather than edit-the-page.

**Q19 — GitHub Actions is approved for verification only, never in the deploy
path.** The Pages source stays on branch-serving. `_config.yml`'s `exclude` list
stays the publishing gate. A workflow that only reads cannot break a deploy; the
worst case is a red tick.

**Q20 — all six normalisations approved, each as a separate commit after its
family has already migrated with a zero-diff harness pass.** MathJax `id` (28
pages), breadcrumb `aria-label` (341), `<section id="main">` → `<main id="main">`
(462), `loading="lazy"` (33), the one `<style>` block, and the 44 hand-written
pages' inline `style=` attributes.

**Explicitly NOT covered by this approval**, and still needing its own
instruction: the three structurally malformed notes pages in PH06-031. Those
edits sit inside prose regions, and the standing rule is that economics content
is never touched without explicit approval, every time.

### D19 — Approval records the decision; it does not by itself lift the audit's read-only rule

Stated because D11 and D15 set the pattern: permission in this project has been
given per instance, and the audit's rule 1 is that only `_audit/**` may be
written. D18 fixes **what** will be built and **how**; it does not decide **when**
building starts relative to the remaining audit phases (P8, P3, P4, P7, P10, P11).

That sequencing question is put to Eliot at this checkpoint. Two things argue for
finishing the audit first, and they are recorded here so the choice is made on
evidence rather than momentum:

- **Migration Phase 7 is already gated on P3.** Baking the header/footer at build
  time trades a 1-file nav edit for a rebuild, and whether that trade is worth
  making depends on P3's ruling on link equity (PH00-001).
- **Two of the six approved normalisations are P8's subject matter.** The 44
  inline-`style` pages and the `<style>` block are PH00-008, which P8 audits
  properly. Fixing them before P8 has looked at the CSS means fixing them twice.

### D20 — Q21 answered: the audit finishes before implementation starts

Eliot, 2026-08-09, choosing the recommended default: **finish the audit first.**

Order is unchanged from `AUDIT-PLAN.md`: **P8 → P3 → P4 → P7 → P10 → P11**, then
implement from P11's prioritised roadmap with every finding in hand.

**Consequence, accepted.** The drift measured in P6 stays on the site in the
meantime — 341 breadcrumbs without `aria-label`, 28 MathJax variants, 18 `<head>`
self-disagreements, 462 pages without `<main>`, and `convert_raw_notes.py` still
stale. None of it is user-visible or SEO-harmful today; PH06-027 is the one with
teeth, and it only bites if someone runs that script. It is recorded in
`DO-NOT-BREAK.md` for exactly that reason.

**The audit remains read-only.** Rule 1 stands unchanged: only `_audit/**` may be
written. D18's approval is carried forward to implementation time; it does not
need re-asking, but it also does not authorise a site edit before P11.

---

## 2026-08-09 · Phase 8 checkpoint

### D21 — Q22 answered: the CLS correction to `seo/09-web-vitals-baseline.md` was made

Eliot, 2026-08-09: **default.** The document has been corrected; the fixes
themselves wait for P11 per D20.

**This is the third site-tree edit of the audit**, after `.gitignore` and the two
changes under D11/D12, and the first to a `seo/` document. Recorded because audit
rule 1 says only `_audit/**` may be written, and this is a named exception rather
than a drift.

What changed, in `seo/09-web-vitals-baseline.md` only:

- A CLS block added to the existing "superseded in part" banner, carrying the
  7-run before/after table, the identified past-paper-questions mechanism, and an
  explicit **UNKNOWN** on the notes-topic 0.110 with the method that would answer
  it.
- Line 104's MathJax bullet annotated — the conclusion stands, the basis does not.
- Fix-table row 5's "CLS already 0.000" struck through and corrected.
- The "What is NOT wrong" CLS bullet struck through and retracted in place.

Nothing was deleted. The original wording is retained with strike-through, so the
record still shows what was believed and when.

### D22 — Q24 answered: the four single-file fixes wait for P11

Eliot, 2026-08-09, choosing the recommended default. `font-display: swap`,
`, sans-serif`, the three focus rings and the header `<h1>` all hold until P11,
consistent with D20. Nothing about them decays.

### D23 — Q25 answered: the `$…$` table was checked and looks correct; fix if optimal

Eliot, 2026-08-09: *"I have checked the table - seems to look correct as is, but
fix if optimal."*

**So the hazard is latent, not live.** That is a real result and it narrows
PH08-039: the PPP table on
`revision-notes/aqa-a2-macro/2-1-4-uses-of-national-income-data.html` renders
correctly today. MathJax 3's `FindMath` does not merge text across a `<strong>`
boundary in the way the static reading assumed.

The recommendation stands anyway, and is now a hardening rather than a fix:
**remove `["$", "$"]` from `inlineMath`.** No page uses `$…$` as a delimiter, the
only 8 literal `$` on the site are currency, and removing it immunises every
future page that mentions a dollar figure — including the next one, which may put
its two dollar signs somewhere MathJax *does* pair them. Scheduled with the rest
of the MathJax convergence work in P11.

### D24 — Q23 answered "adopt the 78 SVGs"; inspection then changed the premise · **see Q26**

Eliot, 2026-08-09: *"adopt the 78 SVGs - permission is granted in this instance."*
This **overrode** the recommended default, which was to re-encode the PNGs and
treat the SVG adoption as separate work.

**The permission was acted on by inspecting first**, per CLAUDE.md standing rule
4 — *visually inspected, never trusted by filename*. Four pairs were rendered
headlessly and compared. The inspection stopped the swap:

- **Every SVG is 4:3; 76 of the 78 PNGs are not.** The SVGs are recompositions
  drawn to a flashcard canvas, not re-encodings.
- **`perfect-competition-short-run-supernormal-profit` is not the same diagram.**
  The PNG is a two-panel market-and-firm figure; the SVG contains only the firm
  panel. Swapping it would delete the market panel from two topic pages and the
  microeconomics gallery — economics content, which CLAUDE.md's first hard
  constraint forbids altering without an explicit instruction. An instruction to
  adopt an image format is not an instruction to remove a panel.
- **Aspect ratio does not predict which are safe.** A 2.446 pair is faithful; a
  2.766 pair is not.
- **20 of the 95 affected pages would mix the two visual styles**, and 28
  diagrams have no SVG at all.

**Nothing was swapped.** No `src` was changed and no notes page was touched.
Logged as PH08-047 and re-put as **Q26**, because the answer given was to a
question whose premise no longer holds. The adoption is still judged worth doing
— it is a sequencing problem, not a rejection.

### D25 — Q26 answered: route (c), re-encode the PNGs; the SVG adoption becomes its own project

Eliot, 2026-08-09: **"C."** — re-encode now, treat the SVG adoption as separate
work. This supersedes D24's open question and settles what PH08-034 and PH08-047
become in the P11 roadmap.

**Execution is P11, per D20**, consistent with Q24. The audit stays read-only.
If the re-encode is wanted sooner, it is one command and needs no HTML change —
see the sub-variant below, which is the part of this decision worth reading.

**The saving was measured, not estimated**, on a 10-file sample spanning the
largest and the median diagrams, with Pillow 12.2.0 (already installed on this
machine; note it is **not** stdlib, against the repo's convention for committed
scripts — this is a one-off conversion, not a build step):

| Approach | 112 files, 26.2 MB → | HTML edits needed |
| --- | ---: | --- |
| Resize to 1600 px, keep RGBA PNG and the filename | **~10.2 MB** (−61%) | **none** |
| Resize + flatten to 64-colour palette, same filename | **~3.2 MB** (−88%) | **none** |
| WebP at q88 | ~2.0 MB (−92%) | **231 `src` edits across 94 pages** |

**The middle row is the recommendation.** It gets 88% of the weight off at zero
markup cost, because the filename and the aspect ratio are unchanged, and
`.diagram-image` is `max-width: 100%` so the intrinsic `width`/`height`
attributes keep working as an aspect-ratio pair. Mean notes-page image payload
would fall from **513 KB to roughly 63 KB**.

**Two things to verify before committing the conversion**, neither of which the
audit can settle without rendering:

1. **The 64-colour quantisation must be eyeballed** on a diagram with a shaded
   area (`perfect-competition-short-run-supernormal-profit`, `j-curve`) — flat
   line art on white quantises invisibly, but anti-aliased curve edges can band.
2. **The sample flattened RGBA onto white.** All 112 files are 8-bit RGBA. If any
   diagram is meant to sit on a non-white backdrop, flattening is wrong for it and
   the RGBA variant (row 1) applies instead.

WebP is declined for now on exactly the ground D20 sets: it is a 94-page HTML
change, and 94-page HTML changes are what D18's shell module exists to make
cheap. Revisit after the migration, when it costs one edit.

**PH08-047 stays OPEN and unscheduled.** The SVG adoption is not cancelled — it
is the better end state — but it is content work needing 78 individual
verifications and 28 new diagrams, and it now has no dependency on the re-encode.

---

## 2026-08-09 · Phase 4

### D26 — Q11 answered by measurement rather than by asking again

Phase 4 settled Q11 from the files, so it did not need to go back to Eliot.

**The `/past-paper-questions/` pages have no publisher markup because their
generator was written from different boilerplate, not because reproducing exam
board question text was thought to warrant it.** The proof is what those pages
emit *instead*: all 90 ppq pages and all 7 practice-question hubs carry a
`WebSite` node — a site-level entity — and 354 other pages carry
`EducationalOrganization`. Each generator is internally consistent; they disagree
with each other.

A copyright motive is ruled out on its own terms: those pages already identify
the site as the publisher through `WebSite` and `CollectionPage`, so withholding
`EducationalOrganization` withholds nothing.

Q11's recommended default — treat it as an oversight, fix at the generator in P4
— is therefore adopted, **as a recommendation for P11**, not executed. The audit
stays read-only under D20.

**Second half, which Q11 did not ask about and P4 found anyway:** all 100
`WebSite` nodes lack `potentialAction`, which is the only thing `WebSite` exists
to carry, and Google recognises it on the homepage alone. 99 of the 100 do
nothing. Removing them is part of the same generator fix. PH04-052.

**Standing exception preserved.** If the omission *was* deliberate, recording that
in `seo/08-structured-data.md` closes it and the markup stays as it is. That
remains Eliot's to say.

### D27 — Q16 answered: git history is left alone

Eliot, 2026-08-09: **"no not for now."** The two exam-board specification PDFs
stay in git history. `d220ad0` removed them from `HEAD` and from the site, which
answers the presentation concern; the distribution concern is accepted as a low
residual risk against a `git filter-repo` that would rewrite every commit SHA and
break every hash cited in `PROJECT-LOG.md`, `PAST-PAPERS-PROGRESS.md`, the `seo/`
reports and this audit.

**"For now" is recorded as written.** Reconsider only if a rights-holder asks.
Q16 closes; `DO-NOT-BREAK.md`'s note on `/specificiations/` is unchanged.

### D28 — Q17 answered: `logo/` is repo storage, not a published asset · **supersedes D13**

Eliot, 2026-08-09: *"The logo is in the files purely for safekeeping alongside
the other assets."*

**This resolves the UNDECIDED that D13 left open**, and it resolves it the
opposite way to Q17's recommended default. The intent was never a stable public
URL to hand to a third party; the files are in the repo to keep them safe. That
publication happens at all is incidental to GitHub Pages serving everything by
default.

**Recommendation, for P11:** add `logo/` and `old-logos-archive/` to
`_config.yml`'s `exclude`. The files stay in the repo, exactly as the answer
intends; they stop being 30 live URLs.

Evidence that this costs nothing, gathered before recommending it:

- **0 references** across every published `.html`, `.css`, `.js`, `.json`, `.xml`
  and `site.webmanifest` — PH01-013, re-confirmed by PH08-044.
- **0 rows** mentioning either path in any of the 8 `seo/gsc-exports/` CSVs or in
  `seo/performance-pages.csv`. Neither directory has ever earned an impression.
- 30 files, **2.4 MB** of published surface (`logo/` 447 KB,
  `old-logos-archive/` 1.96 MB).

The `_config.yml` comment block should change from the current UNDECIDED note to
a one-line statement of this decision, so the next reader sees a decision rather
than an open question. PH01-013 moves from OPEN to **RESOLVED-BY-DECISION**,
pending that edit.

### D29 — PH04-055's `logo` recommendation is amended, because it assumed Q17 went the other way

PH04-055 recommended pointing `EducationalOrganization.logo` at a file in
`logo/`, and said so on the grounds that it "supplies the missing reason to keep
`logo/` published". **D28 answers Q17 the other way, so that reasoning is
withdrawn.**

The finding itself stands — 353 of 354 organisation nodes have no `logo`,
`description` or `sameAs`, and only `index.html` carries a complete one. **The
amendment is which file to point at:** `android-chrome-512x512.png`, at the site
root, already published, already referenced by `site.webmanifest`, and already
what `index.html`'s existing complete node uses. No new published URL is needed
and `logo/` can be excluded without touching the structured data.

Recorded rather than edited in place, per the audit's append-only convention. The
amendment is also written into `PH04-structured-data.md` so a reader of the
finding is not left with the withdrawn version.

---

## 2026-08-09 · Implementation begins

### D30 — The audit moved to `docs/audit/` and is committed · **supersedes D1**

Eliot, 2026-08-09, approving PH11 §5 option (a). `_audit/` → `docs/audit/`, and
the `_audit/` line removed from `.gitignore` in the same commit — without that
second half the move stages nothing and silently does not happen.

**Why D1 expired rather than was wrong.** D1 withheld the audit because it is a
list of this site's own defects and the repo is public. That reasoning held while
the audit was only a list. It stops holding the moment the roadmap starts, because
the roadmap *is* the audit: every implementation commit wants to cite the finding
that motivated it, and a finding that is not in history cannot be cited. The
precedent for accepting the public half was already set by `REVIEW-NOTES.md`, a
1,596-line public list of known content errors, and by `docs/CONTENT_ISSUES.md`.

**What still withholds it from the site is now `_config.yml`, not `.gitignore`.**
`docs/` is already in `exclude`, so no new line was needed. Verified after the
move: `build_sitemap.py --check` reports "nothing written". Two consequences:

- The audit is no longer protected by Jekyll's `_`-prefix rule. `DO-NOT-BREAK.md`'s
  no-`.nojekyll` entry is annotated accordingly — it now protects more, not less.
- `verify_liquid.py` scans `docs/`, so the move takes it from **1 problem to 8**.
  All 7 additions are prose *about* the Liquid tag-open hazard, in files Jekyll never renders
  — the identical false positive as PH00-011, whose root cause is that the checker
  does not parse `exclude`. Wave 1 step 1.2 closes all eight together.

**What was rewritten in the moved files, and what deliberately was not.** 104
functional pointers — script invocation paths, `sys.path`, cross-references
between findings — were repointed at `docs/audit/`, because a reader following
them needs them to work. The ~32 references that are *narrative* were left
verbatim: D1 itself, the rule-1 statements, PH11 §5's decision brief, and every
"is gitignored" sentence. Rewriting those would falsify what was decided and when,
which is the one thing an append-only record exists to prevent.

Three sites were neither repointed nor left alone, because they are **live
instructions the move inverts** rather than history: `PROGRESS.md`'s
"verify the working state" block and `AUDIT-PLAN.md`'s closing check both told a
future session to **stop** if `git check-ignore` reported nothing, which is now
the correct state. Both are struck through with the replacement check beside them.

**Rollback.** `git revert` the move commit. The files return to `_audit/` and the
`.gitignore` line comes back in the same operation. Nothing published changes in
either direction, because `docs/` was excluded throughout.

### D31 — PH00-011 fixed: `verify_liquid.py` parses `_config.yml`'s `exclude`

Eliot, 2026-08-09: **"Continue with your recommendation."** Wave 1 step 1.2 pulled
forward ahead of the push, because D30's move took the checker from 1 false
positive to 8 and pushing a verifier that is red for reasons nobody can act on is
how a guard stops being read.

**Done ahead of Wave 1 step 1.1.** The strict order in PH11 §2 exists because 1.4
(the CI workflow) must not land before 1.2; 1.1 (the build-date stamp) is
independent of both. Nothing was skipped that 1.2 depended on.

**The fix is the one PH00-011 asked for.** `rendered_files()` knew only Jekyll's
`_`-prefix rule, because `exclude:` did not exist when it was written
(`fba7c7c` 2026-08-04, `d085317` 2026-08-08). It now imports
`build_sitemap.excludes()` and `build_sitemap.published()` rather than restating
the list — PH00-011 warned that a private skip list "recreates the same drift one
commit later", and two callers of one parser cannot drift at all. Both live in
`scripts/`, both stdlib-only, and `build_sitemap.py` is import-safe.

| | before | after |
| --- | ---: | ---: |
| markdown files checked | 124 | **1** |
| problems reported | 8 | **0** |
| exit code | 1 | **0** |

The one file it still checks is
`revision-notes/macro-application/macro-application-uk-sa.md` — the only markdown
GitHub Pages renders. PH00-011 predicted exactly two such files; `.codex/` became
`docs/` under D14, leaving one, which is what the parser independently finds.

**Verified in both directions, not just the happy one.** A planted stray `{%` in
`revision-notes/` is caught and exits 1; the identical fault in `docs/` is
correctly ignored and exits 0. Cross-checked against a second implementation:
`build_sitemap.published()` and the audit's own `lib.is_published()` agree on all
134 tracked markdown files, 0 disagreements.

**New failure mode, deliberate.** If the set of rendered markdown ever becomes
empty the script **fails** rather than printing a green zero, because a check
that checks nothing is dead code, not a pass. **This interacts with PH11 §4b**,
which proposes moving `macro-application-uk-sa.md` into `raw-notes/`: doing that
takes the count to 0 and this script starts failing by design. When 4b lands,
either delete `verify_liquid.py` or keep it as a guard against markdown
reappearing on the published surface — that is a decision, and it should be made
rather than absorbed as a red tick.

**Consequence: Wave 1 step 1.4's precondition is met.** `DO-NOT-BREAK.md`'s
"do not add this to CI before PH00-011 is fixed" is discharged, and its entry is
struck through and replaced rather than deleted.

### D32 — `verify_liquid.py` passes on an empty set · **amends D31**

Eliot, 2026-08-09, approving PH11 section 4b:
*"Yes move macro-application-uk-sa.md"*.

That move took the last published markdown file off the site, so
`verify_liquid.py` had nothing left to check — and D31 had deliberately made it
**fail** in exactly that case, on the grounds that a checker which checks nothing
passes for the wrong reason. D31 flagged this interaction in advance rather than
letting it surface as an unexplained red tick. Here is the resolution.

**The empty set is now the correct state, and something else asserts it.** When
D31 was written nothing watched the published surface, so "no markdown" was
indistinguishable from "the exclude list quietly swallowed everything". Wave 1
item 1.5 changed that: `.md` is not in `verify_published_surface.py`'s
`ALLOWED_SUFFIXES`, so any markdown file inside a published directory fails that
check, by name, before Jekyll could ever render it. Verified both ways — a
planted `revision-notes/probe.md` exits 1, removing it returns to 0.

So the guarantee moved rather than disappeared, and `verify_liquid.py` becomes a
**latent guard**: dormant while the published surface carries no markdown, and
immediately useful the moment a deliberate exception puts one there. Deleting it
— the other option D31 named — would throw away the only thing that then checks
that file's Liquid syntax, against a failure mode that takes down the whole
deploy rather than one page.

Both scripts now say this in comments, each pointing at the other, so neither
looks like dead code to the next reader.

**What did not change.** The hazard itself is untouched: Liquid still runs over
any published markdown before Markdown, and one stray `{%` still fails the entire
Pages build. `DO-NOT-BREAK.md`'s entry stands.

---

## 2026-08-11 · Wave 2 checkpoint

### D33 — Migration equality is "same tags, order and values", not byte-identity

Eliot, 2026-08-11, choosing Option A when the two were put to him.

**PH06 section 3's stated exit criterion — "190/190 heads reproduced
byte-identical" — was never reachable, and that is a fact about the committed
files rather than about any implementation.** Only **6 of the 190** hand-written
pages are byte-identical to their own Prettier output: the site's HTML has never
been run through Prettier, and only the generators run it, over their own
output. All 190 were put through Prettier 3.9.6 in a scratch tree to check, and
the 166 notes pages' 13 distinct byte-level `<head>` formats stayed at 13.

So a migrated page must instead carry **the same tags, in the same order, with
the same values; only whitespace may differ.** That is what the ten assertions
already check — nine of them are whitespace-insensitive, and the tenth
(assertion 3, LaTeX byte-exact) covers the content slice, which is copied
verbatim and never reformatted.

**The rejected alternative was to Prettier-format every page first**, in a
separate commit, so that byte-identity became meaningful afterwards. Declined
because it front-loads the exact operation the harness exists to guard — a bulk
automated rewrite of 166 pages of prose — and does it *before* the safety net
applies. CLAUDE.md's own rule is that scripted prose rewrites have destroyed
`<a>` tags in this repo before.

**A comment is not whitespace.** Where the shell would have dropped a decorative
`<!-- ==== -->` divider from 2 pages or a `<!-- Scoped styles -->` note from 1,
the divider and the note were lifted and re-emitted instead. Dropping them stays
available as a later normalisation and remains Eliot's call.

**In practice the criterion was met with room to spare.** 61 of the 190
hand-written pages migrated byte-identically anyway, including all 20 of
`edexcel-theme-3`, and every non-identical page differs by blank lines alone —
192 deletions and 0 insertions across the whole of Phase 5.

> **Correction, recorded because it changed a conclusion.** Phase 2 reported
> `L1 = 0/190` and concluded byte-identity was unreachable *by any
> implementation*. The 0 was a bug in the selftest: the captured `<head>` region
> ends with the two spaces that indent `</head>`, and the comparison used
> `.strip("\n")`, which could never match. Corrected, the figure is 61/190. The
> conclusion about Prettier stands and was measured independently; the stronger
> claim did not.

### D34 — The 9 root pages are permanently out of scope for the shell migration

Eliot, 2026-08-11: **"Leave it out of scope."**

Migration Phase 4 proposed moving the 9 root pages, 3 notes-other pages and the
notes index onto `page_shell.py`. The root pages are declined outright.

**They are nine pages, not a family.** `page_anatomy.py` measures 9 distinct
`<head>` shapes, 9 body shells, 3 script tails and 9 stylesheet sets across 9
pages — every one different, which is correct: `index`, `tutoring`, `marking`,
`about`, `faq`, `contact`, `privacy`, `confirmation` and `404` do nine different
jobs. They are also the only pages `page_shell` cannot reproduce at D33's
criterion: 5 of 9, against 459 of 463 sitewide.

Templating them would mean modelling nine one-off shapes in a shared module to
save nine duplicated `<head>` blocks — the cost of the abstraction exceeding what
it removes. The commercial pages are also the highest-value surface on the site
and the one place a silent regression is least acceptable.

**Consequence, accepted.** A future sitewide `<head>` change is 1 edit for 454
pages and 9 hand edits for the rest. `verify_page_shell.py` check 4 already holds
the root pages to CLAUDE.md's required-`<head>` list, so the 9 are watched even
though they are not generated.

**Not decided here:** the 3 `notes-other` pages and the notes index. Two of the
three already reproduce at D33's criterion, and the two diagram galleries carry
the other two head `<style>` blocks. They remain available if wanted; nothing
depends on them.
