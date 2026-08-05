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
