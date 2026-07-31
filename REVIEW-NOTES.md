# REVIEW-NOTES — notes consistency & enrichment pass

Running log for branch `notes-consistency-pass`. Things I found but did not fix,
plus the verification record. Updated as the pass proceeds.

Safety net: `backup-pre-enrichment` points at `main` as it was before any of this.

---

## Status

| Phase | State |
| --- | --- |
| Phase 0 — reconnaissance | Complete — `RECON.md` |
| Phase 1A — mechanical plan | Complete — `PLAN-mechanical.md`, approved |
| Phase 2 commits 1–5 — mechanical work | **Complete** |
| Phase 1B — enrichment plans | Not started (6 batches, one at a time) |
| Phase 2 commits 6–7 — emphasis | Not started |
| Phase 2 commits 8–9 — enrichment | Not started |
| Phase 3 — final verification | Partial (run after each commit so far) |

---

## Economics content — flagged, not changed

Nothing in this section has been altered. Content errors are the author's call.

### New in this pass

**N1 — a leading space inside `\text{}` in two multiplier formulas.**
`aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html` and
`edexcel-theme-2/2-4-4-the-multiplier.html` both render

```
k = \frac{\text{Final Change in Real GDP/NI}} {\text{ Injection}}
```

The space inside `\text{ Injection}` puts a small gap at the start of the
denominator. I initially took this for Prettier reflow damage and removed it, then
reverted: Prettier only breaks lines at whitespace that is already there, so the
space was authored. Cosmetic, and yours to decide.

Related: the same formula labels the denominator "Injection" where the numerator is
a change in real GDP. Worth confirming the intended denominator is the *initial*
injection, since that is what the multiplier ratio needs.

### Carried over from `docs/revision-notes-audit.md` — still open

Not duplicated here; see that document for the full write-up.

| # | Where | Summary |
| --- | --- | --- |
| **C1** | `edexcel-theme-1/1-2-4-supply.html` + AQA twin `aqa-a2-micro/1-3-3` | **The one outstanding economics error.** The Figure 1 caption pairs *contraction* with a price rise and *extension* with a price fall. Supply slopes upward, so this is backwards, and the bullet list 15 lines below contradicts it. |
| **C4** | `aqa-a2-macro/2-2-3`, `aqa-a2-micro/1-5-6` | Both cross-reference Edexcel theme numbers that do not exist in the AQA specification the reader is following. |
| **C5** | `aqa-a2-macro/2-1-2` | Confirm the unemployment-rate denominator matches the ONS/ILO "economically active" definition given a few lines above. |
| **C6** | `aqa-a2-macro/2-1-2` | Real GDP growth stated as an identity; it is an approximation valid at low inflation. Standard at A-Level. |
| **W1** | `aqa-a2-macro/2-3-1`, `<h2>The Trade Cycle?</h2>` | Stray question mark on a heading that is not a question. A wording change, so out of scope here. |
| **F1–F4** | various | Four figure captions that contradict their own diagram. |

---

## What changed, commit by commit

### 1. Exam Preparation sections removed — 87 files

Every Edexcel topic page ended with `<section><h2>Exam Preparation</h2><div
class="exam-tip">…</div></section>` and nothing else in it. All 87 removed, wrapper
and contents. Two heading variants went with them: `Exam Preparation:` on
`edexcel-theme-1/1-2-8` and `Exam Focus` on `edexcel-theme-1/1-2-9`.

Removed text archived verbatim in
[`docs/removed-exam-preparation-sections.md`](docs/removed-exam-preparation-sections.md)
— kept out of this file to stop an 800-line appendix swamping it.

`edexcel-theme-1/1-1-5-specialisation-division-of-labour.html` needed special
handling: its CTA was nested *inside* the section rather than following it. The CTA
was preserved and re-parented, and all 87 CTA blocks then hashed byte-identical.

### 2. `formula-box` LaTeX protected — 24 files

`<!-- prettier-ignore -->` added to the 28 of 51 `formula-box` divs that lacked it.
8 display formulas that had been split across source lines were rejoined; the 4 that
sit inline in prose rather than in a guarded `formula-box` were left in Prettier's
preferred form.

> **Correction worth recording.** My first attempt at this also stripped the space
> after `\text{`, on the assumption that no legitimate LaTeX needs one. That was
> wrong, and it broke the oligopoly concentration-ratio formula on
> `aqa-a2-micro/1-5-5` and `edexcel-theme-3/3-4-4`: `\text{ firms}` became
> `\text{firms}`, rendering "top *n*firms". Caught by the formula-equivalence check,
> reverted, and the commit rebuilt. All 176 files now render every formula exactly
> as `main` does.

### 3. `.notes-cta` extracted — 89 files + 1 stylesheet

The inline-styled CTA block, duplicated across 87 Edexcel pages and both diagram
galleries, replaced by a `.notes-cta` class. ~350 inline style declarations removed,
addressing part of audit flag S5. No copy or link changes; the galleries keep their
board-neutral `/past-papers/index.html`.

### 4. AQA conversion CTA added — 79 files

Closes audit flag S1. Every AQA topic page now ends with the same `.notes-cta` block
as its Edexcel counterpart, pointing at `/past-papers/aqa/index.html`. All 166 topic
pages now carry exactly one CTA.

### 5. Dead `chart-container` wrappers removed — 94 files

Closes part of audit flag S6. 211 wrappers with no CSS rule anywhere, each wrapping
exactly one `<figure class="diagram-figure">`. Prettier reflowed 63 files afterwards
because attributes that had been split now fit on one line.

---

## Verification so far

Three stdlib-only validators were written for this pass, since the site has no build,
lint or test step:

- `scripts/verify_html.py` — strict well-formedness and duplicate-id check
- `scripts/verify_text_integrity.py` — extracts visible text at two commits and diffs
- `scripts/verify_links.py` — resolves every internal href and fragment against disk

### Results at commit 5

| Check | Result |
| --- | --- |
| HTML well-formedness | **176/176 files parse, 0 errors** |
| Internal links and fragments | **3,863 refs, 0 broken hrefs, 0 broken fragments** |
| Display-formula rendering vs `main` | **0 of 176 files changed** (whitespace-collapsed comparison of every `\[…\]`) |
| Prettier 3.9.6 | Clean on every file touched. 2 files still fail — `revision-notes/index.html` and `macro-application/index.html` — both **pre-existing on `main`** and both untouched here. |
| CTA uniformity | 87 Edexcel blocks identical; 2 gallery blocks identical; 166/166 topic pages carry exactly one |

### Text integrity, commit by commit

Only the two commits that are *meant* to change wording do so:

| Commit | Files whose visible text differs |
| --- | ---: |
| Exam Prep removal — change expected | 87 |
| `formula-box` protection | **0** |
| `.notes-cta` extraction | **0** |
| AQA CTA — change expected | 79 |
| `chart-container` removal | **0** |

### Visual regression

Headless Chrome, pixel comparison against the immediately preceding commit:

- `.notes-cta` extraction — **identical** at 1440/768/480px on
  `edexcel-theme-1/1-1-1`, `edexcel-theme-3/3-1-3`, `edexcel-theme-4/4-2-1`
- `chart-container` removal — **identical** at 1440/480px on
  `edexcel-theme-1/1-1-4`, `aqa-a2-micro/1-5-11`, `aqa-a2-micro/1-8-4`

Pages carrying MathJax were avoided for pixel work: inline MathJax renders
non-deterministically between runs, so formula bands are noise rather than signal.

---

## Notes for later

- **`.coming-soon` is dead CSS** — rules exist, no markup uses it. Four lines,
  unrelated to this pass; left alone.
- **`css/pages/revision-notes-textbook.css` fails Prettier on `main`**, at a long
  `linear-gradient` in the `.coming-soon` block (line ~830). Pre-existing and not
  introduced here. `docs/revision-notes-audit.md` records only a `macro-application.css`
  nit, so this one appears to have been missed.
- **Remaining inline styles** — audit flag S5 is now partly closed. Roughly 279
  `style` attributes remain, mostly table column widths.
