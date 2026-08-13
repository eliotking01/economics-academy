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

---

## 2026-08-11 · Wave 2 Phase 7

### D35 — The header and footer are baked in, and editing the nav is now a rebuild

Eliot, 2026-08-11, re-confirming D18's trade once it was put concretely:
**"Yes, proceed."** The question asked was the honest one — after this lands,
changing one nav label means editing `templates/header.html`, running the
rebuild, and committing about 463 changed files.

`js/components/inject-templates.js` no longer fetches anything. The header and
footer are written into all 463 pages at build time, by `page_shell.bake()` for
the 446 generated pages and `scripts/bake_templates.py` for the other 17.

**What it bought, all measured rather than argued:**

- **The nav exists without JavaScript**, on every page, for the first time.
- **CLS.** Four page types at two viewports, headless Chrome with a
  PerformanceObserver: 1400px went 0.0253 → 0.0037 (index), 0.0223 → 0.0034
  (tutoring), 0.0224 → 0.0022 (ocr), 0.0234 → 0.0021 (notes). Three repeats of
  the notes page show the *before* figure is bimodal — 0.0241, 0.0024, 0.0240 —
  because it depended on whether two fetches beat first paint. Baking removed a
  race, not a constant.
- **4.10 is unblocked**, though not for the reason PH08-043 gives. See below.

**What it cost:** a median **+1,217 bytes gzipped per page**, +23.5%, 654 KiB
across the site, against two fewer round trips per page and the CLS above.
Measured across all 463 before starting.

**The 17 pages were the decision.** 446 pages are generated and pick the header
up on a rebuild. The other 17 are not, and the three options were put: sync them
with a re-runnable script, leave them fetching, or hand-edit them. Eliot chose
the script. Leaving them would have half-landed the phase and left
`/past-papers/edexcel-b/` and `/past-papers/ocr/` — 291 clicks and 21,131
impressions between them, PH03-049 — as the only pages on the site whose
navigation still needed JavaScript.

**D34 is not overridden.** It puts the 9 root pages permanently out of scope for
the `<head>` migration, on the ground that they are nine one-off `<head>`
shapes. Their `<head>` is untouched. What changed is the body, where all nine
are identical to the other 454.

**The rename was declined.** `inject-templates.js` injects nothing now. Renaming
it to `nav.js` was built and put through the harness — assertions 1, 4 and 8
fail, each exactly and only the rename, and the other seven pass. It edits 463
pages and changes a published asset URL to gain a filename, which is the trade
`css/fontawesome-all.min.css` settled the other way in Wave 4.2. Wave 4.10
rewrites the file and the script tail together, and the rename is free there.

**Two numbers were wrong and are corrected.** The `<head>` is generated for
**446** of 463 pages, not 454 — that figure was `463 − 9` from D34 rather than a
measurement, and it appeared in D34 itself, CLAUDE.md, DO-NOT-BREAK.md and four
places in PROGRESS.md. And `verify_page_shell.py` had been printing "190 of them
hand-written" on every CI run since Phases 3 and 5 made the notes pages
generated; it is 17.

**PH08-043 is wrong on detail and 4.10 must not be planned from it as written.**
It says the runtime fetch leaving takes one of jQuery's three consumers with it.
Counted before touching anything: 9 of the file's 11 jQuery calls are in
`initNavigation()`, 2 are the bootstrap, and the fetch and the nav highlight
used **none** — both were already vanilla. The file shrank from 209 lines to
121 and still needs jQuery. What 4.10 actually inherits is better than the
finding promised: one file that is nothing but nav plumbing, with no async
injection ordering to preserve.

---

## 2026-08-11 · Wave 4.10

### D36 — jQuery, dropotron and util.js are gone; the desktop dropdowns are CSS; the nav bar is redesigned

Eliot, 2026-08-11, in two instructions. First, on the dropdown replacement:
**"I am happy to give you creative freedom here. I am not that attached to the
current look of the desktop dropdowns so I give you full creative licence to
improve the UX of these, just ensure it matches the brand."** Then, after the
removal landed: **"You also have licence to improve the nav bar so that changes
encompass the entire nav bar, not just the dropdowns."**

**What left, measured before deleting anything:** `jquery.min.js` (168,019 B,
40,276 gzipped), `jquery.dropotron.min.js` (10,964 / 2,368) and `util.js`
(12,942 / 3,247), on all 463 pages. `inject-templates.js` became
`js/components/nav.js` — the rename D35 declined in Phase 7 on the ground that
it edited 463 pages to gain a filename, and which cost nothing here because the
script tail was being rewritten on all 463 regardless. **Net −43,265 bytes
gzipped per page**, after the CSS the replacement added.

**PH08-043 was wrong on detail in a second way, beyond the one D35 recorded.**
It lists `util.js` as a jQuery consumer with 22 calls, which is true and
misleading: of its four exports only `navList()` had a caller anywhere on the
site. `panel()`, `placeholder()` and `$.prioritize` had **zero**, so 349 of its
490 lines were dead and the live part is about 30 lines, now inlined in
`nav.js`. Eliot chose deleting the file over porting it.

**dropotron was duplicating the navigation into every page.** Rendered and
counted: 11 `.dropotron` menus built at page load, and the document's `<a>`
count fell from 118 to 95 with no link lost — 23 duplicated anchors and 23
duplicated list items, on every one of 463 pages, in front of every crawler.
Nothing had recorded this and nothing was looking for it.

**The dropdowns are CSS now, and therefore work with scripting off**, which
they never did. The submenus were always in `templates/header.html`; no markup
changed. `nav.js` adds only what CSS cannot — tap-to-open at a width that gets
the desktop nav, and Escape — and adds it as a class on top of `:hover` and
`:focus-within`, so switching the file off leaves working dropdowns.

**The redesign is presentation only.** No label, href or structure moved;
`templates/header.html` is untouched and check 9 is unmoved. Upright instead of
italic; one accent language for hover, focus and open where there had been a
grey box and a red pill sharing nothing; a chevron on the three items that open
a submenu; a light dropdown card instead of the theme's near-black slab; 44px
rows instead of 28. **The one non-cosmetic part: the mobile panel had no "you
are here" indicator at all** — the desktop bar has had one since the beginning
— and `nav.js` now copies it off the baked `<li class="current">` rather than
re-deriving it, so the two navigations cannot disagree.

**What it cost:** `css/main.css` 55,270 → 63,450 bytes, 11,477 → 14,323
gzipped. **+2,846 B per page, and CSS is render-blocking where the script tail
was not.** That is the one number moving the wrong way and it is 6% of what the
wave removed.

**Three assertions of `compare_trees.py` fail, and that is the intended
report.** 1, 4 and 8 — the same three D35 predicted for the rename, now also
covering three deletions. Each was decomposed rather than waved through:
assertion 4's 2,315 losses are exactly 463 × 4 removed `src`s plus 463
`<script>` counts down by exactly 3, with **zero** unexpected lines; assertion
8's 474 differing files are **463 HTML differing only in `<script src>` lines**
plus `css/main.css`, `js/main.js` and nine unpublished scripts.

**Two verifiers were taught, not relaxed.** `verify_page_shell` check 2 keeps
its independent literal and gained a second assertion — 0 of 463 pages load any
removed script — because the ordering test filters to tail members and a page
that kept jQuery would have passed it. `verify_markup_integrity --strict`
skips `<script src>` tags, on the ground that check 2 makes a strictly stronger
statement about the same bytes; it was proved still able to fail by deleting
one `<a>` from inside a notes body.

---

## 2026-08-12 · Wave 4.11

### D37 — The closed mobile panel is `inert`; `browser.min.js` and `breakpoints.min.js` are deleted

Eliot, 2026-08-12, commissioning both in one brief: *"THIS SESSION IS TWO SMALL
COMMITS"* — `inert` on the closed `#navPanel` dropping `aria-hidden`, then the
removal of the two dead libraries. Both had been found by Wave 4.10, logged in
`REVIEW-NOTES.md`, and deliberately left out of it.

**They were kept as two commits because they share nothing.** One is an
accessibility fix in a script that no page rebuild touches; the other is a
sitewide script-tail change that rewrites 463 files. Landing them together
would have given one regression two candidate causes, which is the reason 4.10
gave for not doing the second in the first place.

**`inert` replaces `aria-hidden`, it does not join it.** The panel is moved
off-canvas by `transform` rather than `display: none`, because the slide has to
be animatable, so its 32 links stayed in the tab order while it was shut — and
`aria-hidden="true"` on an element with focusable descendants is an ARIA 1.2
conformance failure that Chrome logs. `inert` answers both. **The declined
alternative was a feature-detected `aria-hidden` fallback** for browsers
without `inert` (Firefox < 112, Safari < 15.5, Chrome < 102): declined because
it would reinstate for exactly those users the conformance failure the change
removes, and because two code paths would leave the one the harness does not
drive untested.

**The harness was extended rather than trusted.** `inert` changes no markup, no
link, no class and no transform, so every field `render_nav.py` recorded was
blind to it — 23 of 23 captures would have compared identical. It gained
`panelAttrs.inert` and a `tabbable` tally: **32 of 32 panel links focusable
with the panel shut before, 0 of 32 after, and 32 of 32 open in both**, on 10
pages at 390px. The open figure is taken by the same loop seconds later,
because a zero with no companion is what 4.10's CLS probe produced for a
deliberate 200px shift.

**The two libraries went for a reason unlike the three 4.10 deleted.** Neither
needed jQuery. Neither had a caller: `browser` **zero** call sites anywhere,
`breakpoints` **one**, `js/main.js`'s config call, which named four widths no
listener ever read back. Neither writes a class or inserts a node. 8,236 B raw,
**2,141 gzipped, off all 463 pages**, plus two fewer requests.

**Assertions 1, 4 and 8 fail again, and again that is the report.** 4's 1,389
losses are exactly 463 × 3 with zero unexpected lines; 8's 480 files are
463 HTML + 7 sitemap XML + 2 js deleted + 2 js edited + 3 scripts + 2 root
markdown + 1 harness. Rendered against the first commit, the second moves one
field on 23 of 23: `counts.script`, −2.

**This is the first wave to need the sitemap regenerated for the reason 4.10
had to correct itself about.** Every page was last touched on 2026-08-11 and is
touched again on 2026-08-12, so 467 `lastmod`s move. It can only be generated
after the pages are committed, because the date comes from `git log`.

**Three more numbers were wrong, two of them written by 4.10.** The
`breakpoints({…})` call named four widths, not five. `_working/flashcards/qa/`
holds 15 HTML files of which 14 carry the old tail, not 12. CLAUDE.md's
written-out four-script list is replaced by a pointer to the constant, because
a list written out in prose is what went stale twice in one file on one day.

---

## 2026-08-12 · post-4.11 cleanup

### D38 — `logo/` and `old-logos-archive/` are deleted; six of the ten unreferenced diagrams go and four stay · **supersedes D28, D13 and PH11 §4a**

Eliot, 2026-08-12, closing both of the two standing "decisions for Eliot, not
tasks": **"I have the logos files saved elsewhere, so feel free to do what is
required with this to optimise (delete if needed)"** and **"do whatever is
optimal with the unused diagrams (delete if needed)."**

**The logo directories are deleted, and that is a stronger action than PH11 §4a
recommended.** §4a proposed *excluding* them in `_config.yml` and said so on one
ground: the repo was their safekeeping, so the files had to stay. Eliot holding
copies elsewhere removes that ground, and with it the reason to prefer the
weaker option. 31 files, 2.47 MB. D28's evidence was re-derived first and still
holds: 0 references from any published file, 0 rows in any GSC export, absent
from every sitemap. **Deleting and excluding differ only in what a checkout
carries** — the blobs stay in history either way, so this is reversible with one
`git revert` and D27's rule against rewriting history is untouched.

**One number was wrong and one file was a finding nobody had made.** D28 says
"30 files, 2.4 MB"; it is **31**. The 31st is
`old-logos-archive/favicon-assets/site.webmanifest` — a second, stale
`site.webmanifest`, live at its own URL, which is precisely PH10-060's class: a
non-HTML file inside a published directory, invisible to every enumeration tool
because they all glob `*.html`.

**Four of the ten "unreferenced" diagrams are not unreferenced in the sense that
matters, and only one check finds it.** DO-NOT-BREAK's flashcards rule is that
every hand-drawn SVG is verified against its ground-truth PNG in
`images/diagrams/`, and Wave 5.1's entire method is verifying all 78 SVG/PNG
pairs. `comparative-advantage`, `game-theory`, `trade-union-competitive` and
`trade-union-monopsony` each have a same-named SVG referenced by 10, 5, 4 and 4
published files. Deleting those PNGs would have taken 5.1 from **5**
unverifiable SVGs to **9**, silently, months from now. They are kept, 358 KB,
and the reason is recorded in DO-NOT-BREAK so that the next census does not
propose it again.

**The other six are deleted**, 250 KB: no SVG twin, no reference of any kind.
Diagram PNGs 112 → 106; "images referenced by nothing" 43 → 7.

**A third case was found and deliberately NOT swept up.** The root
`favicon-16x16.png`, `favicon-32x32.png` and `favicon-48x48.png`, 4 KB, are
named by no `<link>` and are not in `site.webmanifest`. Browsers probe
`/favicon.ico` by convention but never those three, so they are probably dead —
and "probably" is why they get their own decision rather than riding along on
this one.

---

## 2026-08-12 · Wave 3.2 and 3.3

### D39 — `boards.json` is load-bearing; the check keeps an independent copy; a slug collision fails where slugs are minted

Eliot, 2026-08-12, commissioning the wave and then answering the one question it
raised. On the check: **"Go with Option A and leave the folder question."**

**Wave 3.2 in one sentence: five generators stopped restating what a board is
and started reading `boards-data/boards.json`, and no published byte moved.**
Seven commits, **0** published files changed at any point, all ten
`compare_trees.py` assertions passing on every one of them — unlike Waves 4.10
and 4.11, where assertions 1, 4 and 8 failing *was* the report.

**Option A, and why it was a real question.** Before this wave
`verify_boards.py` compared the record against the four hardcoded structures,
with the code winning. Once a generator reads the record that comparison is
circular — it asks whether `boards.json` agrees with a structure `boards.json`
just produced, and it agrees with any value, including a wrong one, while still
printing green. `PINNED` restates all **82** leaves as an independent literal in
a flat dotted-path shape, so changing a board name or slug now has to change two
files in one commit. This is `verify_page_shell.SCRIPT_TAIL` and
`build_past_paper_taxonomy.EXPECTED`, the same pattern for the same reason.

The rejected alternative was deleting the check and relying on
`verify_generated.py`. Declined because that catches a **forgotten rebuild**,
not a **wrong value**: edit the record, re-run the generators, commit, and it
goes green with every page rewritten.

**Proved able to fail before being trusted, four ways.** A one-sided value
change, an unpinned new field, and a removed pinned field each exit 1; the same
change made in both files exits 0. The first probe was the em-dash → hyphen
collapse on Theme 2 — the exact accident DO-NOT-BREAK names as the likeliest way
to get this wave wrong.

**The roadmap's size for this wave was unreproducible, both versions.**
`PROGRESS.md` said 113 literals across 11 scripts; `PH11-synthesis.md` §2 said
111 across 9 generators. PH01-012's per-script table was tested at the commit it
names, `d220ad0`, against six mechanical definitions: totals 154, 52, 204, 156,
176 and 120, none of them 111, and the closest matching only 4 of the 9 rows. It
was hand-counted under an unstated rule. The real edit surface was **107**
board-data literals in 5 scripts, and removing them took **64** literal-nodes
off those files.

**The roadmap said one two-board ternary. There were three.** PH01-012 and PH11
name `build_glossary.py:679`, now `:664`. `extract_glossary.py:290` and `:318`
were never counted, and `:290` is PH09-022's own bridge in a second location —
the finding pointed at `build_glossary.py`'s `taxonomy` field without recording
that the inverse was written out elsewhere. Six further `"E" if s ==
"edexcel-a" else "A"` ternaries render an unpublished `_working/` report and are
deliberately left.

**Two regexes were board lists in disguise**, `extract_glossary.SPEC_ALERT_RE`
and `build_questions.ID_RE`. Both are generated now, **longest name first**,
because `re` alternation is ordered and a slug that is a prefix of another would
shadow it. Both were proved equivalent to the literal they replace rather than
assumed: identical match groups on 179 of 179 notes files, and 0 differences
across all 1,267 real question IDs.

**Wave 3.3 was mostly already done, and saying so is the finding.** Seven of the
eight topic-keyed structures already carried the board in the key or were scoped
to one board; `siblings_for`'s docstring already explained why, and
`topic_lookup` already held the cross-board assertion PH09-023 proposed as its
cheap interim. That is the `loading="lazy"` case again.

**The one real gap was at the source.** Slugs are minted in
`build_past_paper_taxonomy.build()` and nowhere else, and its guard was keyed on
`(board, slug)`, which cannot see a cross-board collision by construction —
measured, it built a taxonomy of 166 topics carrying a duplicated slug and
exited 0. Both cases now fail where the slug is made.
`build_past_paper_questions.topic_lookup`'s guard stays, is not redundant, and
was proved to fire for the first time.

**PH09-023's "22 phantom disagreements" is not reproducible and the real number
is worse.** A spec-only join gives **37** apparent title disagreements walking
`questions-data/` alphabetically and **0** walking it reversed. The count is
directory order. The 0 is the dangerous reading: joined that way the data looks
clean while being silently wrong on 37 of 129 codes.

**And the namespace is safe by coincidence twice over, not by design.**
PH09-023 says the safety rests on two boards never giving one spec code the same
title. Both halves already occur independently: **37** of 129 codes sit on both
boards, and **11** titles are used by both — on different codes. **0** shared
codes share a title, and the closest pair is 0.579. That is the case for the
guard, not against it.

**What stayed hardcoded, and it is a line rather than an omission.** Prose that
names a board is page copy, not board identity: `build_glossary`'s `intro` and
`meta`, `build_questions`' `HUB_SECTIONS` year groups and hub copy,
`build_flashcards`' meta descriptions. `boards.json` records what a board is
called and where it lives, and no more.

**Deferred, not overlooked.** `slugs.dataDir` is a single value where
`build_past_paper_questions.py` and `verify_past_paper_tags.py` both walk three
directories, because Edexcel A has two — `edexcel-a` and `edexcel-a-as`.
Recording that is a schema extension rather than a transcription, and Eliot held
it back for its own piece of work. `questions.json`'s topic keys stay bare
slugs, per DO-NOT-BREAK.

**Five fields are recorded and read by no code:** `slugs.questionBank`,
`slugs.dataDir`, `specCodesAreReal`, each group's `names.flashcards`, and
`build_glossary`'s board-level `notesUrl`, which is copied into `BOARDS` and
consumed by no template — dead before this wave and found by a probe that
correctly moved nothing. `PINNED` stops all five drifting against the record;
nothing proves they still match the sources they were transcribed from.

### D40 — `slugs.dataDir` stays as it is; the AS-Level folder is not recorded · **closes the question D39 deferred**

Eliot, 2026-08-12, after the trade was put to him plainly: **"I now believe I am
unlikely to add AQA AS-Level, so leave it."**

**What was deferred.** `boards-data/boards.json` records one `dataDir` per
board. Edexcel A actually has two — `past-paper-questions-data/edexcel-a` (24
papers) and `edexcel-a-as` (16) — because one board offers two qualifications,
9EC0 and 8EC0, and both have a Paper 1 in the same series, so one directory
would mean colliding filenames. AQA has one (24). Two scripts type the list of
three out by hand:
`build_past_paper_questions.py:64` and `verify_past_paper_tags.py:44`.

**Why it is closed rather than done.** Recording it means inventing a shape the
record does not have — either a board holding a list of directories, or a
notion of *qualification* beneath a board. That is design, not transcription,
and Wave 3.2's entire safety argument was that it transcribed. The only payoff
was the day a second board gained an AS-Level tier, and Eliot's judgement is
that day is unlikely to come.

**What that costs, stated so nobody re-derives it as a defect.**
`slugs.dataDir` is now permanently a field that is recorded, pinned, and
**wrong for one of the two boards** in the sense that it is incomplete. It is
read by no code, so nothing acts on it. A future session finding it should read
this entry rather than "fixing" it: the hardcoded triple in those two scripts is
the correct place for that list, and it is deliberate.

**If AQA AS ever does arrive**, the work is: add its data directory, extend the
record with whatever shape is right *then*, and repoint those two scripts —
about half a day, and no worse for having waited.

### D41 — The three root `favicon-{16,32,48}` PNGs are deleted · **closes the last item D38 left open**

Eliot, 2026-08-12: **"Delete them."** D38 found them while closing the logo and
diagram questions and deliberately did not sweep them up, on the grounds that
"probably dead" deserved its own answer.

**They are not probably dead, they are provably redundant, and the proof is
one nobody had done.** `favicon.ico` — linked from all 463 pages — is 3,971
bytes and **bundles three images inside it**, at exactly the three sizes in
question:

```
                inside favicon.ico      the loose PNG
    16x16              647 bytes            657 bytes
    32x32            1,301 bytes          1,316 bytes
    48x48            1,969 bytes          1,975 bytes
```

They are the same icons, packaged twice: once in the `.ico` every page requests,
once loose where nothing does. That is a stronger statement than "unreferenced",
and it is the one D38's diagram case says to look for — **ask what depends on a
file, not what links to it.** Here nothing depends on them either, because the
thing that would need them already contains them.

**Evidence, re-derived before deleting.** 0 references from any file in the
repo, published or not, other than three audit documents discussing them. 0 rows
in any of the 8 `seo/gsc-exports/` CSVs. Absent from `site.webmanifest`, which
names only the two `android-chrome` icons. Absent from every sitemap. Browsers
probe `/favicon.ico` by convention and never guess at `/favicon-32x32.png`.
3,948 bytes.

**This removes three published URLs**, which is why it is a decision and why it
is not in Wave 3.2's branch. Only the third such removal in the audit, after
D12's specification PDFs and D38's files. Both prior cases are the precedent:
the blobs stay in git history, so `git revert` restores them.

**Checked afterwards rather than assumed:** 1,908 root-absolute asset references
across the published HTML, **0** now pointing at a file that does not exist —
and that check was proved able to fail by deleting `favicon.ico` itself, which
took it to 1 and named the URL. `verify_links.py`, `verify_published_surface.py`,
`verify_html.py` and `asset_census.py 1 4` all still pass, and
`build_sitemap.py --check` reports 0 `WOULD CHANGE`, correctly: the three were
never in a sitemap.

**Kept, and not to be re-proposed:** `favicon.ico`, `apple-touch-icon.png`,
`android-chrome-192x192.png`, `android-chrome-512x512.png` and
`site.webmanifest`. All five are referenced, and
`android-chrome-512x512.png` is additionally D29's target for
`EducationalOrganization.logo`.

---

## 2026-08-13 · The deliberate normalisations

### D42 — Eight of the eleven ship; one is dropped as a misreading; one is measured and declined

Eliot, 2026-08-13, commissioning the wave and then answering the four
questions it raised, each with the trade put plainly. **Option A on all four.**

**The wave in one sentence: eleven normalisations approved in D18's Q20 and
carried since, re-measured against the live tree before any of them was
built — and three of the eleven did not survive the measurement.**

| Item | Outcome |
| --- | --- |
| `inLanguage` → `en-GB` | shipped, 179 nodes |
| `EducationalOrganization` | shipped, 107 pages, 354 → 461 |
| Full organisation node | shipped, 4 pages, 1 → 5 |
| MathJax convergence + `$…$` | shipped, 126 pages |
| breadcrumb `aria-label` | shipped, 341 pages |
| 3 real `<style>` blocks | shipped, 10,114 B out of the HTML |
| `<main id="main">` | shipped, 462 pages |
| visible breadcrumb | shipped, 19 pages + macro-application |
| **`WebSite` removal** | **DROPPED — the finding misreads its own evidence** |
| **preconnect lineage** | **MEASURED AND DECLINED — no round trip to save** |
| 322 inline `style=` | not started; its own session |

**The `WebSite` item is dropped because PH04-052 reads nested references as
top-level entities.** It asks for 99 `WebSite` nodes to be deleted, calling
them site-level entities that "occupy the slot where the publisher should be".
Measured: **1 is a top-level entity and 99 are the value of an `isPartOf`
property**. `isPartOf` is how a page says it belongs to a site; it does not
compete with `publisher`, and `privacy.html` has carried both side by side all
along. DO-NOT-BREAK already protects the identical construction one property
along — "the 179 `Course` nodes are `isPartOf` references, not page entities…
an automated validator will flag these; **it is wrong**". Deleting the 99 would
have removed correct markup from 99 pages against an existing register entry
nobody had connected to it.

**The preconnect item is declined on evidence, which is what the register
asked for.** It forbids aligning the two lineages without measuring LCP.
Measured: every page carries its preconnect inside the first **4,145 gzipped
bytes**, and **439 of 463 documents fit entirely** inside TCP's ~14,600-byte
initial congestion window, so both positions arrive in the same burst. There
is no round trip between them to save. Two sentences around the counts were
also wrong: 173 of the 190 "hand-written" late pages are generated.

**The browser probe failed and is committed saying so.** Three configurations,
and in each it could not distinguish *no preconnect* from *preconnect* — so by
its own stated rule it cannot speak to where one sits. Kept because it records
what does not work. This is 4.11's rule applied in advance rather than in
hindsight: the `none` variant existed from the first run precisely so that a
null could be believed, and it is what proved the null could not be.

**Two pieces of tooling were built because the wave hit their absence.**
`compare_trees.py` printed **PASS over a real failure** at `--max-report 0` on
six of ten assertions, because the capped detail line was what set the verdict;
its suite was also 31 of 32, not 32, `a7-link-lost` having been silently
disarmed by Phase 7's baked nav two waves earlier. And
`verify_markup_integrity.py` had no `Markup-Change:` trailer, so an approved
structural change had no way to declare itself and would have turned CI red on
correct work — the exact failure `Text-Change:` was written to prevent.

**The four questions, all answered A.** The publisher node is copied from
`index.html` verbatim and nothing is invented — the footer links no social
accounts, and a LinkedIn exists but has never been referenced on the site, so
it stays out until a URL is given. Breadcrumb wording is lifted from each
page's own `BreadcrumbList`, so the two copies cannot disagree. The preconnect
is measured before acting, and the measurement is what declined it. The two
gallery `<style>` blocks share one file.

**PH06-030 is closed on both halves**, including `macro-application`, which
was outside the eleven and was approved separately once it was the only page
left out of step.

**Seven roadmap numbers were wrong**, every one found by measuring first: the
MathJax split (4 configs on 127 pages; it is 3 on 126), a third figure inside
`page_shell.py`'s own comment (33 and 18; they are 37 and 19), the preconnect
attribution, "the reference form the other 354 pages use" (there are six
roles, not one), the `WebSite` substance, the harness suite's 32, and one of
mine — I called the two gallery blocks byte-identical when they are the same
LENGTH, `macro` and `micro` both being five letters.

### D43 — Item (f) ships complete: 322 inline styles to 0, and two silent regressions on the way

Eliot, 2026-08-13, answering the three questions the measurement raised.
**Option A on all three.** This closes the eleventh and last of D18 Q20's
approved normalisations; D42 settled the other ten.

**The measurement came first, and for once every recorded number held.** 1,509
inline `style=` attributes on the published surface, 1,187 KaTeX, **322
authored across 44 files** — and the family split, the property split (width
143, font-size 142, colour 142, margin-top 20, text-align 19) and the 120-in-32
`notes-data` figure all re-derived unchanged. Two independent methods agreed at
1,509. **This is the first item in the wave where nothing moved.**

**PH08-042's own figures are stale and reconcile exactly.** It records 333
across 45 files; the 45th was `templates/footer.html` with 11, moved into CSS
by `be92eb2` in Wave 0. 333 − 11 = 322, 45 − 1 = 44. **One claim in it is still
wrong:** "no generated page carries an authored inline style". **32 of the 44
files are generated** — 26 notes-topic and 6 notes-hub, holding 120 attributes
inside `notes-data/**` slices. It went stale when Wave 2 Phases 3 and 5 made
the notes pages generated underneath it.

**The three decisions.**

- **The 96 `<th>` column widths were moved, knowing what that buys.** 35
  tables, 13 width tuples, 11 percentages: the width is per-table data, so
  `style="width: 25%"` becomes `class="width-25"` and the same fact is spelled
  differently. It is not more maintainable. It was put in those words and
  chosen anyway, because **a half-swept item is one no verifier can ever hold
  at zero** — the argument that also keeps `verify_page_shell` check 5's
  `<style>` label at 0 and `KNOWN_BREADCRUMB_DISAGREEMENT` empty. The rules are
  scoped twice, `.revision-notes-content .concept-table th.width-N`, because
  a bare `.width-25` in a sheet 179 pages load is the collision the house rule
  exists to prevent.
- **404.html gets `css/pages/404.css`.** It was the one published page with no
  page stylesheet, which is why its 15 attributes had nowhere to go.
  `verify_page_shell`'s `HEAD_EXEMPT["a page stylesheet"]` goes from
  `{"404.html"}` to empty and check 4 reads **463/463**. One published URL
  added, none removed.
- **One `.button.fit` in `css/main.css`**, a modifier on the site-wide button
  component beside `.alt`, `.primary` and `.large`, replacing the same
  declaration written inline 47 times across 9 pages and 4 stylesheets.

**THE RESULT THAT MATTERS IS NOT THE COUNT. Two of the last 35 attributes
moved the rendered page, and all ten harness assertions passed both.**

- `tutoring.html` **lost 44px**: `css/main.css`'s `section > :last-child {
  margin-bottom: 0 }` is specificity **(0,1,1)** and a lone class is (0,1,0).
- `404.html` **gained 14.67px per link row**, the other direction:
  `css/main.css:3415`'s `#main .row > div[class*="col-"]` is **(1,2,1)**, and
  no number of bare classes beats a selector containing an ID.

In both, the inline outranked a real rule and the class did not. **That is the
whole risk of this item and it was stated before any of it was written** —
`compare_trees` assertion 4 fires only on losses, and an attribute becoming a
class is a loss of nothing; assertions 2, 3, 6 and 7 never look at CSS. So
`computed_style_diff.py` was built first, in the wave's opening commit, and it
is what found both.

**That probe failed its own selftest on its first run, and the failure was
real.** Serving both trees under path prefixes on one origin sent both iframes
to the *same* `/css/main.css`, because every asset path here is root-absolute
— so it reported "0 differences" on a tree with a declaration deliberately
appended to `main.css`. **It could not have failed.** One origin per tree fixed
it. A second false positive, on two identical trees, traced to Calendly's
arrival time deciding whether there was a scrollbar. **And the 404.html
regression was invisible until `--body-only` existed:** the probe aligns
elements by index, so one new `<head>` `<link>` made it skip the page entirely
with `element count 199 -> 200`, inside a run whose final line said PASS. Same
shape as `compare_trees` printing PASS at `--max-report 0` in D42.

**`scripts/verify_inline_styles.py` is the workflow's 22nd step** and is what
the `<th>` trade was made for. It holds authored styles at 0 with no allowlist,
and **pins the 1,187 KaTeX offsets per page across all 7**, by construction
rather than by path. All four of its failure paths were tested by breaking each
one.

**One thing found in passing and fixed.** `docs/audit/scripts/lib.py`'s
`exclude` literal was two entries short of `_config.yml` — `boards-data/` and
`notes-data/` — so `lib.pages()` returned **636 instead of 463**, counting the
173 notes-data slices as pages, and `link_graph.py` reported 173 phantom
orphans. Eight audit scripts read through it and four of them back
DO-NOT-BREAK's "Numbers that must not regress" table. **The comment on that
list promised a `verify_matches_config()` that had never been written.** It is
written now, parses `_config.yml`, and runs on import.

**Three of my own predictions were wrong**, all in the direction of the harness
seeing less than I said: assertion 4 showed 1 addition rather than 0 (a `<link>`
is a tag); assertion 5 **passed** where I predicted it would move, because
`head_fields()` reads only `lang`, `title`, `meta:*`, `og:*`, `twitter:*` and
`rel="canonical"` and is structurally blind to a stylesheet link; and I did not
anticipate the `--body-only` gap at all.
