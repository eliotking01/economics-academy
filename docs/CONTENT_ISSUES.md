# Content issues found while writing flashcards

Suspected errors in the revision notes, found while sourcing and verifying
flashcard content. Logged here for Eliot's decision — **never fixed
unilaterally** (standing rule 1). Site-wide problems that predate the
flashcards work belong in REVIEW-NOTES.md instead; this file is only for
issues the flashcard verification pass turns up.

Format per entry:

- **Location** — file and section.
- **Issue** — what looks wrong.
- **Proposed correction** — exact replacement wording.
- **Confidence** — high / medium / low, with the source checked (spec,
  standard theory).
- **Status** — open / approved / rejected / fixed (commit).

---

## 1. Maximum-price figure caption describes a tax, not a price ceiling

- **Location** — `revision-notes/edexcel-theme-1/1-4-1-government-intervention-in-markets.html`,
  Figure 3 caption (`max-price.png`).
- **Issue** — the caption reads "showing the shift in supply, the new
  equilibrium, and the government revenue generated". A maximum price shifts
  no curve and raises no government revenue; the figure itself correctly
  shows a price ceiling below equilibrium with excess demand. The wording
  appears copy-pasted from the indirect-tax figure caption.
- **Proposed correction** — "Figure 3: The impact of a maximum price set
  below the equilibrium price, showing the resulting excess demand
  (shortage) between Qs and Qd."
- **Confidence** — high (standard theory; the diagram itself confirms).
- **Status** — fixed (approved by Eliot 2026-08-04; corrected in the
  "fix: correct the max/min price figure captions" commit).

## 2. Minimum-price figure caption has the same copy-paste error

- **Location** — same page, Figure 4 caption (`min-price.png`).
- **Issue** — identical wording problem: "the shift in supply, the new
  equilibrium, and the government revenue generated" describes neither a
  minimum price nor the figure, which correctly shows a price floor above
  equilibrium with excess supply.
- **Proposed correction** — "Figure 4: The impact of a minimum price set
  above the equilibrium price, showing the resulting excess supply
  (surplus) between Qd and Qs."
- **Confidence** — high.
- **Status** — fixed (approved by Eliot 2026-08-04; corrected in the
  "fix: correct the max/min price figure captions" commit).

## 3. AQA maximum-price figure caption has the same tax copy-paste error as the fixed Edexcel one

- **Location** — `revision-notes/aqa-a2-micro/1-8-9-government-intervention-in-markets.html`,
  Figure 3 caption (`max-price.png`).
- **Issue** — identical to issue 1 (fixed on the Edexcel twin 1.4.1 with
  Eliot's approval): the caption reads "showing the shift in supply, the
  new equilibrium, and the government revenue generated". A maximum price
  shifts no curve and raises no revenue; the figure correctly shows a
  ceiling below equilibrium with excess demand.
- **Proposed correction** — "Figure 3: The impact of a maximum price set
  below the equilibrium price, showing the resulting excess demand
  (shortage)." (mirrors the approved Edexcel wording).
- **Confidence** — high (same figure, same error class as the approved fix).
- **Status** — fixed (approved by Eliot 2026-08-05; applied with the
  Edexcel twin's approved wording verbatim, including the "between Qs
  and Qd" clause).

## 4. AQA minimum-price figure caption, same error

- **Location** — same page, Figure 4 caption (`min-price.png`).
- **Issue** — identical to issue 2: "the shift in supply, the new
  equilibrium, and the government revenue generated" describes neither a
  minimum price nor the figure, which shows a floor above equilibrium with
  excess supply.
- **Proposed correction** — "Figure 4: The impact of a minimum price set
  above the equilibrium price, showing the resulting excess supply
  (surplus)."
- **Confidence** — high.
- **Status** — fixed (approved by Eliot 2026-08-05; applied with the
  Edexcel twin's approved wording verbatim, including the "between Qd
  and Qs" clause).

## 5. AQA subsidy figure caption says "an subsidy" and "government revenue"

- **Location** — same page, Figure 2 caption (`subsidy-gov-expenditure.png`).
- **Issue** — "The impact of an subsidy on a market, showing the shift in
  supply, the new equilibrium, and the government revenue generated."
  Grammar ("an subsidy"), and a subsidy is government **expenditure**, not
  revenue — the figure's shaded rectangle is the cost to the government.
- **Proposed correction** — "Figure 2: The impact of a subsidy on a
  market, showing the shift in supply, the new equilibrium, and the
  government expenditure incurred."
- **Confidence** — high.
- **Status** — fixed (approved by Eliot 2026-08-05; applied as proposed).

## 6. Multiplier figure caption describes two AD curves; the figure draws three

- **Location** — `revision-notes/edexcel-theme-2/2-4-4-the-multiplier.html`,
  Figure 1 caption (`multiplier.png`).
- **Issue** — the caption reads "An initial increase in aggregate demand
  (AD) from AD1 to AD2 leads to a larger increase in real GDP from Y1 to
  Y2 due to the multiplier process." The figure itself draws **three**
  curves — AD1, AD2 and AD3, with feet Y1, Y2, Y3 and price levels PL1 to
  PL3 — where AD2 to AD3 is the induced multiplier stage the caption never
  mentions. As written the caption describes a two-curve diagram.
- **Proposed correction** — "Figure 1: The multiplier effect on an AD/AS
  diagram. An initial injection shifts aggregate demand from AD1 to AD2,
  and the induced rounds of spending carry it further to AD3, so the
  final rise in real GDP (Y1 to Y3) is larger than the initial injection
  alone."
- **Confidence** — high that caption and figure disagree (three curves
  are plainly drawn); the proposed wording is one way to fix it.
- **Status** — fixed (approved by Eliot 2026-08-05; applied as proposed
  in the batch-4 approval commit; text/markup integrity confirmed the
  caption was the only change).

## 7. AQA multiplier figure caption has the same two-vs-three-curve mismatch as the fixed Edexcel one

- **Location** — `revision-notes/aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html`,
  Figure 1 caption (`multiplier.png`).
- **Issue** — identical to issue 6 (fixed on the Edexcel twin 2.4.4 with
  Eliot's approval): the caption describes "AD1 to AD2 ... Y1 to Y2",
  but the figure draws three curves (AD1, AD2, AD3) with Y1/Y2/Y3.
- **Proposed correction** — the Edexcel twin's approved wording
  verbatim: "Figure 1: The multiplier effect on an AD/AS diagram. An
  initial injection shifts aggregate demand from AD1 to AD2, and the
  induced rounds of spending carry it further to AD3, so the final
  rise in real GDP (Y1 to Y3) is larger than the initial injection
  alone."
- **Confidence** — high (same figure, same error class as the approved
  fix).
- **Status** — fixed (approved by Eliot 2026-08-05; applied with the
  Edexcel twin's approved wording verbatim; text/markup integrity
  confirmed the caption was the only change).

## 8. Business-objectives page says "choose to satisficing" twice

- **Location** — `revision-notes/edexcel-theme-3/3-2-1-business-objectives.html`,
  Satisficing section.
- **Issue** — grammar: "they may choose to satisficing — achieving a
  level of profit..." and later "owners may also choose to satisficing
  to balance work-life priorities". The verb form should be
  "satisfice".
- **Proposed correction** — replace both instances of "choose to
  satisficing" with "choose to satisfice", leaving the rest of each
  sentence unchanged.
- **Confidence** — high (grammar only; no economics change).
- **Status** — open.
