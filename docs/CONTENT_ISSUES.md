# Content issues found while writing flashcards

Suspected errors in the revision notes, found while sourcing and verifying
flashcard content. Logged here for Eliot's decision — **never fixed
unilaterally** (standing rule 1). Site-wide problems that predate the
flashcards work belong in docs/REVIEW-NOTES.md instead; this file is only for
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
- **Status** — fixed (approved by Eliot 2026-08-05; both instances
  corrected; text/markup integrity confirmed the two words were the
  only change).

## 9. Game-theory payoff matrix has its Low/High price labels swapped

- **Location** — `images/diagrams/game-theory.png`, used as Figure 3 on
  `revision-notes/edexcel-theme-3/3-4-4-oligopoly.html`.
- **Issue** — as drawn, the matrix contradicts both the page's own prose
  and standard theory. The prose says colluding on a **high** price earns
  £150bn each, cheating with a **low** price earns £200bn against £50bn,
  and the Nash equilibrium at **low** prices earns £100bn each. But the
  figure places £150bn/£150bn in the Low/Low cell, £100bn/£100bn in the
  High/High cell, and gives £200bn to the **High**-price player in each
  mixed cell — so as drawn, the dominant strategy is High and "collusion"
  means agreeing on low prices, which is backwards.
- **Proposed correction** — swap the "Low Price" and "High Price" header
  labels on both axes of the figure (the payoff numbers can stay where
  they are). The caption and prose are already correct.
- **Confidence** — high (the figure is inconsistent with the adjacent
  prose, the figure caption, and standard prisoner's-dilemma theory).
- **Status** — fixed (approved by Eliot 2026-08-05, who chose to swap
  the notes to the corrected `game-theory.svg` rather than edit the
  PNG: both `3-4-4-oligopoly.html` and `microeconomics-diagrams.html`
  now reference `/images/diagrams/svg/game-theory.svg` at 800×600; alt
  text and captions unchanged. `game-theory.png` is now unreferenced
  and **known-incorrect — do not use it as ground truth**; the SVG is
  authoritative).

## 10. Price-discrimination figure titles the inelastic panel "off-peak tickets"

- **Location** — `images/diagrams/price-discrimination.png`, Figure 2 on
  `revision-notes/edexcel-theme-3/3-4-5-monopoly.html`.
- **Issue** — the first panel is titled "Price Inelastic Demand e.g.
  off-peak tickets" and the second "Price Elastic Demand e.g. off-peak
  tickets". Off-peak travel is the standard **elastic** example; the
  inelastic sub-market's example should be **peak** tickets (as the notes
  prose itself says: "peak and off-peak train travel"). Both panels
  currently carry the same "off-peak" example.
- **Proposed correction** — retitle panel 1 "Price Inelastic Demand e.g.
  peak tickets" (image edit).
- **Confidence** — high.
- **Status** — fixed (approved by Eliot 2026-08-05; the PNG patched in
  place via Swift + CoreGraphics — "off-peak tickets" whited out and
  "peak tickets" redrawn at matched size and colour #22252a, dimensions
  unchanged at 3642×1080, visually verified against panels 2–3. The fix
  propagates to all three pages that show the file. The flashcard SVG
  uses neutral panel titles and was never affected).

## 11. Monopolistic-competition page says "to a some extent"

- **Location** — `revision-notes/edexcel-theme-3/3-4-3-monopolistic-competition.html`,
  Efficiency in Long-Run Equilibrium section, dynamic-efficiency paragraph.
- **Issue** — grammar: "which may allow them to invest in research and
  development to a some extent". Should be "to some extent".
- **Proposed correction** — delete the stray "a": "...to invest in
  research and development to some extent."
- **Confidence** — high (grammar only; no economics change).
- **Status** — fixed (approved by Eliot 2026-08-05; the stray "a"
  deleted, text-integrity check confirmed it is the only wording
  change in the working tree).

## 12. Contestability barriers table lists "Economies of scale" twice

- **Location** — `revision-notes/edexcel-theme-3/3-4-7-contestability.html`,
  "Types of Barriers to Entry" table.
- **Issue** — the table's first and third rows are identical duplicates:
  both read "Economies of scale — Large existing firms may have much
  lower unit costs, making entry difficult for new small firms."
- **Proposed correction** — delete the third row (the second occurrence),
  leaving the table at six distinct barriers.
- **Confidence** — high (verbatim duplicate; no economics change).
- **Status** — fixed (approved by Eliot 2026-08-05; the duplicate row
  deleted, text/markup integrity confirm the removal is clean).

## 13. Government-intervention page has four grammar slips

- **Location** — `revision-notes/edexcel-theme-3/3-6-1-government-intervention.html`.
- **Issue** — four grammar errors, no economics change:
  1. "force the combined firm to sell certain assets in order to
     **limits** its market share" — should be "limit".
  2. "Maximum prices can be implemented to **low** the prices set by
     monopolies" — should be "lower".
  3. "This creates **a incentive** to profit maximise" — should be
     "an incentive".
  4. "to put social pressure on employers to **pair** a fair wage" —
     should be "pay".
- **Proposed correction** — the four single-word fixes above, nothing
  else changed.
- **Confidence** — high (grammar only).
- **Status** — fixed (approved by Eliot 2026-08-05; all four applied,
  text-integrity confirms the page's only wording changes).

## 14. Impact-of-intervention page has three grammar slips

- **Location** — `revision-notes/edexcel-theme-3/3-6-2-the-impact-of-government-intervention.html`,
  Regulatory Capture section.
- **Issue** — three grammar errors, no economics change:
  1. "shape the rules in their own favour rather than in **consumers
     interest**" — should be "consumers' interests".
  2. "often the regulator lacks the expertise or information required
     to regulate the business and therefore **rely** on the company" —
     should be "relies".
  3. "The regulated firm can present this information **is a manor**
     which benefits them" — should be "in a manner".
- **Proposed correction** — the three fixes above, nothing else
  changed.
- **Confidence** — high (grammar only).
- **Status** — fixed (approved by Eliot 2026-08-05; all three applied,
  text-integrity confirms the page's only wording changes).

## 15. AQA technological-change page: "the creation entirely new"

- **Location** — `revision-notes/aqa-a2-micro/1-4-8-technological-change.html`,
  Inventions chip definition.
- **Issue** — "Inventions: the creation entirely new and original
  products, processes or ideas" — missing "of".
- **Proposed correction** — "the creation of entirely new and original
  products, processes or ideas".
- **Confidence** — high (grammar only).
- **Status** — fixed (approved by Eliot 2026-08-05; "of" inserted. The
  Inventions chip is a glossary source, so the glossary was
  re-extracted and rebuilt per the documented pipeline — the rebuild
  also picked up issue #14's regulatory-capture correction, which the
  shipped glossary had still been carrying in its old wording).

## 16. AQA economies-of-scale page: Tesco buys milk from "daily suppliers"

- **Location** — `revision-notes/aqa-a2-micro/1-4-5-economies-and-diseconomies-of-scale.html`,
  Purchasing economies example.
- **Issue** — "Tesco can negotiate a lower price per unit for milk from
  daily suppliers" — given the milk context this should surely be
  "dairy suppliers".
- **Proposed correction** — "…for milk from dairy suppliers…".
- **Confidence** — high (typo; no economics change).
- **Status** — fixed (approved by Eliot 2026-08-05; applied, no
  glossary coupling).

## 17. AQA price-discrimination page calls second-degree PD "Purchasing Economies of Scale"

- **Location** — `revision-notes/aqa-a2-micro/1-5-7-price-discrimination.html`,
  Types of Price Discrimination section.
- **Issue** — "Second-degree price discrimination occurs when a firm
  charges different prices based on the quantity purchased or the
  version of the product, such as bulk discounts or premium versions.
  **Also known as Purchasing Economies of Scale.**" The last sentence
  conflates two different concepts: purchasing economies of scale are
  the *buyer's* cost saving from bulk-buying inputs (as taught on
  1-4-5), while second-degree price discrimination is the *seller's*
  pricing strategy. Second-degree PD is not "also known as" purchasing
  economies of scale.
- **Proposed correction** — delete the sentence "Also known as
  Purchasing Economies of Scale.", leaving the (correct) definition
  and examples.
- **Confidence** — high that the equivalence claim is wrong (standard
  theory; contradicts the site's own 1-4-5 usage).
- **Status** — rejected (Eliot, 2026-08-05: the two concepts are the
  same; leave the page alone). The page is unchanged. The approved
  flashcard (aqa-1-5-7-def-01) simply does not mention the
  equivalence either way.

## 18. AQA objectives page says "choose to satisficing" twice — twin of fixed issue #8

- **Location** — `revision-notes/aqa-a2-micro/1-5-2-the-objectives-of-firms.html`,
  Satisficing section.
- **Issue** — identical to issue 8 (fixed on the Edexcel twin 3-2-1
  with Eliot's approval): "they may choose to satisficing — achieving
  a level of profit..." and "owners may also choose to satisficing to
  balance work-life priorities". The verb form should be "satisfice".
- **Proposed correction** — replace both instances of "choose to
  satisficing" with "choose to satisfice", exactly as approved for the
  Edexcel twin.
- **Confidence** — high (same error class as the approved fix).
- **Status** — fixed (approved by Eliot 2026-08-05; both instances
  corrected, no glossary coupling, text-integrity clean).

## 19. AQA 1.6.3 spec-alert says "wage discrimination" for "wage determination"

- **Location** — `revision-notes/aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html`,
  spec-alert block.
- **Issue** — "Students should be able to explain the model of wage
  discrimination in a perfectly competitive labour market". The AQA 7136
  spec bullet (4.1.6.3) reads "The economists' model of wage
  **determination** in a perfectly competitive labour market" — and the
  page itself is titled and about wage determination. Wage discrimination
  is a different concept, covered on 1.6.7.
- **Proposed correction** — "…explain the model of wage determination in
  a perfectly competitive labour market…".
- **Confidence** — high (checked against the 7136 spec p42; one-word
  copy slip).
- **Status** — fixed (approved by Eliot 2026-08-06; applied as
  proposed, no glossary coupling — the page has no key-definition
  chips).

## 20. AQA 1.6.3 says a below-equilibrium wage correction decreases employment

- **Location** — same page, "Role of Market Forces" bullet list, second
  bullet.
- **Issue** — "Firms will compete for workers by offering higher wages,
  resulting in an increase in the wage rate and a **decrease in
  employment** until the market reaches equilibrium again." At a wage
  below equilibrium, employment is constrained by the labour supplied;
  as the wage rises towards equilibrium, the quantity of labour supplied
  extends, so employment **rises** (exactly as the page's own
  above-equilibrium bullet says employment rises as the wage falls). As
  written the bullet has the direction backwards — the thing that
  decreases is the quantity of labour demanded, from its notional
  excess, not employment.
- **Proposed correction** — "…resulting in an increase in the wage rate
  and an increase in employment until the market reaches equilibrium
  again."
- **Confidence** — high (standard theory; contradicts the page's own
  first bullet's logic).
- **Status** — fixed (approved by Eliot 2026-08-06; "a decrease in
  employment" replaced with "an increase in employment", nothing else
  changed).

## 21. AQA 1.7.2 relative-poverty sentence ends with a comma

- **Location** — `revision-notes/aqa-a2-micro/1-7-2-the-problem-of-poverty.html`,
  Key Definitions section.
- **Issue** — "Relative poverty exists when household income is below a
  certain proportion of median income in an economy," — the sentence
  (and paragraph) ends with a comma instead of a full stop. The next
  paragraph starts a new sentence ("In the UK, for example…").
- **Proposed correction** — end the sentence with a full stop: "…below
  a certain proportion of median income in an economy."
- **Confidence** — high (punctuation only; no economics change).
- **Status** — fixed (approved by Eliot 2026-08-06. The Relative
  poverty chip is a glossary source, so the glossary was re-extracted
  and rebuilt per its documented pipeline; verify_glossary exits 0).

## 22. AQA 1.7.1 spec-alert missing a space: "wealth,measure"

- **Location** — `revision-notes/aqa-a2-micro/1-7-1-the-distribution-of-income-and-wealth.html`,
  spec-alert block.
- **Issue** — "…the factors which influence the distribution of income
  and wealth,measure and interpret inequality…" — missing space after
  the comma.
- **Proposed correction** — "…income and wealth, measure and interpret
  inequality…".
- **Confidence** — high (typo only).
- **Status** — fixed (approved by Eliot 2026-08-06; space inserted,
  no glossary coupling — spec-alert text is not a glossary source).

## 23. Theme 4 comparative-advantage example claims an impossible specialisation total

- **Location** — `revision-notes/edexcel-theme-4/4-1-2-specialisation-trade.html`,
  "Illustrating Comparative Advantage with PPFs" section, final
  paragraph.
- **Issue** — "the total global output can be increased to 20m computer
  chips and 200mn T-shirts". With the figure's PPFs (Germany: 20mn
  chips or 200mn T-shirts; Vietnam: 10mn chips or 150mn T-shirts),
  producing 20m chips takes ALL of Germany's resources, and Vietnam's
  maximum T-shirt output is 150mn — so 20m chips and 200mn T-shirts
  can never be produced simultaneously. Full specialisation actually
  yields 20m chips + 150mn T-shirts, which is more chips but FEWER
  T-shirts than the page's no-specialisation total (15m + 175mn), so
  as written the example does not demonstrate a clean gain either.
- **Proposed correction** — use partial specialisation, which does
  demonstrate the gain with these numbers: "If Vietnam fully
  specialises in T-shirts (150mn) and Germany produces 25mn T-shirts
  alongside 17.5m computer chips, global output is 17.5m computer
  chips and 175mn T-shirts — 2.5m more computer chips than before
  with no loss of T-shirts."
- **Confidence** — high that the current claim is impossible
  (arithmetic against the figure's own numbers); the proposed wording
  is one way to fix it.
- **Status** — fixed (Eliot 2026-08-06, choosing a different remedy
  from the proposal: keep FULL specialisation — students are not
  taught partial specialisation — and change the numbers so it works.
  Because a country holding absolute advantage in both goods can
  never gain in both goods under full specialisation from half-half
  baselines, the T-shirt maxima were swapped: Germany 20mn chips /
  150mn T-shirts, Vietnam 10mn chips / 200mn T-shirts — each country
  now absolute-advantaged in one good, and the page's existing
  headline totals (15m + 175mn without specialisation, 20m + 200mn
  with) become exactly correct. Applied: the page now references
  /images/diagrams/svg/comparative-advantage.svg (redrawn to the new
  numbers, full self-QA); the Absolute Advantage paragraph, midpoint
  outputs and the four opportunity-cost bullets updated (7.5 and 20
  T-shirts per chip; 0.13 and 0.05 chips per T-shirt); caption
  rewritten. comparative-advantage.png is now unreferenced by this
  page but still displayed by two others — see issue #25).

## 25. AQA 2.6.2 twin and the macro gallery still carry the old comparative-advantage example

- **Location** — `revision-notes/aqa-a2-macro/2-6-2-trade.html` (the
  4.1.2 twin) and `revision-notes/macroeconomics-diagrams.html` (the
  gallery), both displaying `comparative-advantage.png`.
- **Issue** — 2-6-2-trade repeats the 4.1.2 example verbatim with the
  OLD numbers, including the impossible "20m computer chips and 200mn
  T-shirts" total fixed on the Edexcel page under issue #23, and both
  pages still display the old-numbers PNG — so the site now shows two
  contradictory versions of the same figure.
- **Proposed correction** — apply the approved 4.1.2 treatment
  verbatim to 2-6-2-trade (SVG swap, absolute-advantage paragraph,
  midpoint outputs, opportunity-cost bullets, caption), and swap the
  gallery's image to the SVG (game-theory precedent, which swapped
  the gallery too). comparative-advantage.png then becomes
  unreferenced and known-incorrect, like game-theory.png.
- **Confidence** — high (same arithmetic, same figure; the fix is
  already approved on the twin).
- **Status** — fixed (approved by Eliot 2026-08-06; the 4-1-2
  treatment applied verbatim to 2-6-2-trade — image swap, caption,
  absolute-advantage paragraph, midpoint outputs, all four
  opportunity-cost bullets — and the gallery's image swapped to the
  SVG. `comparative-advantage.png` is now unreferenced and carries
  the superseded numbers — do not use it as ground truth; the SVG is
  authoritative).

## 26. Macro gallery's comparative-advantage blurb describes a case the figure no longer shows

- **Location** — `revision-notes/macroeconomics-diagrams.html`,
  Comparative Advantage card, descriptive paragraph.
- **Issue** — the paragraph ends "Specialisation and trade can
  increase total welfare even if one country has an absolute
  advantage in both goods." That is true as general theory, but
  after the approved #23/#25 fix the displayed figure shows each
  country with an absolute advantage in one good — the
  "absolute advantage in both" case is no longer illustrated, so
  the sentence may confuse a student reading it against the figure.
- **Proposed correction** — end the sentence at the theory the
  figure shows: "Specialisation and trade can increase total
  welfare when countries specialise where their opportunity cost is
  lowest." (Or delete the final clause "even if one country has an
  absolute advantage in both goods.")
- **Confidence** — medium (the sentence is not wrong, just no
  longer illustrated; purely a coherence question).
- **Status** — fixed (approved by Eliot 2026-08-06; applied as
  proposed — the sentence now reads "…can increase total welfare
  when countries specialise where their opportunity cost is
  lowest.").
  **Note added 2026-08-26:** Eliot's later Wave 5.1 verdict (D46,
  2026-08-14) reverses the position this fix rests on — see
  `docs/REVIEW-NOTES.md` N-Q21. Do not treat this entry as the
  current ruling on the comparative-advantage example.
  **Note added 2026-10-19:** N-Q21 is resolved. The figure shows
  Germany with the absolute advantage in both goods again, and the
  gallery sentence now reads "…can increase total welfare even if one
  country has an absolute advantage in both goods, as long as each
  specialises where its opportunity cost is lowest."

## 27. Theme 4 balance-of-payments page: "may be require"

- **Location** — `revision-notes/edexcel-theme-4/4-1-7-balance-of-payments.html`,
  Significance of Global Imbalances, Persistent deficits paragraph.
- **Issue** — "a build-up of foreign debt, which may be require higher
  taxes or spending cuts" — stray "be".
- **Proposed correction** — "…which may require higher taxes or
  spending cuts…".
- **Confidence** — high (grammar only).
- **Status** — fixed (approved by Eliot 2026-08-06. The Persistent
  deficits chip is a glossary source, so the glossary was
  re-extracted and rebuilt per its pipeline; verify_glossary exits
  0).

## 28. Theme 4 exchange-rates caption describes a different diagram from the figure

- **Location** — `revision-notes/edexcel-theme-4/4-1-8-exchange-rates.html`,
  Figure 1 caption (`exchange-rates.png`).
- **Issue** — the caption reads "An increase in demand for the currency
  (D1 to D2) causes an appreciation (E1 to E2), while an increase in
  supply (S1 to S2) causes a depreciation (E1 to E3)" — describing a
  single diagram with exchange-rate labels E1/E2/E3. The figure is
  actually TWO panels, each labelled P1/P2: the left panel shows the
  supply shift (S1 to S2, P1 falling to P2), the right panel the
  demand shift (D1 to D2, P1 rising to P2). No E labels exist anywhere
  in the figure. Same error class as the fixed multiplier captions
  (#6/#7).
- **Proposed correction** — "Figure 1: In the left panel, an increase
  in the supply of the currency (S1 to S2) lowers the exchange rate
  from P1 to P2 — a depreciation. In the right panel, an increase in
  demand for the currency (D1 to D2) raises the exchange rate from P1
  to P2 — an appreciation."
- **Confidence** — high that caption and figure disagree; the wording
  is one way to fix it.
- **Status** — fixed (approved by Eliot 2026-08-06; applied as
  proposed, no glossary coupling — captions are not glossary
  sources).

## 29. Theme 4 balance-of-payments: a "cause of a deficit" bullet describes a surplus

- **Location** — same page as #27, "Causes of a Current Account
  Deficit" list, fourth bullet.
- **Issue** — under the heading "Causes of a Current Account Deficit",
  the bullet reads "Economic growth abroad: If other countries are
  growing faster than the domestic economy, they may import more from
  the domestic country, leading to a surplus." As written it describes
  a cause of a *surplus*, contradicting its own list's heading.
- **Proposed correction** — reverse the direction so the bullet
  belongs in its list: "Slow economic growth abroad: If other
  countries are growing more slowly than the domestic economy, demand
  for the country's exports weakens while its own demand for imports
  stays strong, leading to a deficit."
- **Confidence** — high that the bullet contradicts its heading; the
  proposed wording is one way to fix it. (The flashcard on deficit
  causes omits this bullet either way.)
- **Status** — fixed (approved by Eliot 2026-08-06; applied as
  proposed, no glossary coupling — the bullet is not a chip
  definition).

## 30. Theme 4 poverty page: relative-poverty sentence ends with a comma — twin of fixed #21

- **Location** — `revision-notes/edexcel-theme-4/4-2-1-absolute-relative-poverty.html`,
  Key Definitions section.
- **Issue** — identical to issue 21 (fixed on the AQA twin 1-7-2 with
  Eliot's approval): "Relative poverty exists when household income is
  below a certain proportion of median income in an economy," — comma
  instead of a full stop at the end of the sentence and paragraph.
- **Proposed correction** — "…below a certain proportion of median
  income in an economy." (the approved #21 treatment verbatim).
- **Confidence** — high (punctuation only; same error class as the
  approved fix).
- **Status** — fixed (approved by Eliot 2026-08-06; the Relative
  poverty chip is indeed a glossary source, so the glossary was
  re-extracted and rebuilt per its pipeline; verify_glossary exits
  0).

## 31. Theme 4 poverty page: "Education and skils"

- **Location** — same page, Causes of changes in Relative Poverty,
  first bullet.
- **Issue** — "Education and skils (skills gap)" — typo "skils".
- **Proposed correction** — "Education and skills (skills gap)".
- **Confidence** — high (typo only).
- **Status** — fixed (approved by Eliot 2026-08-06; applied, no
  glossary coupling — the bullet is not a chip definition).

## 32. Theme 4 taxation page: "A tax where where"

- **Location** — `revision-notes/edexcel-theme-4/4-5-2-taxation.html`,
  Types of Tax Systems, Regressive Tax definition.
- **Issue** — "Regressive Tax: A tax where where the percentage of
  income paid in tax falls as income rises" — doubled "where".
- **Proposed correction** — "A tax where the percentage of income
  paid in tax falls as income rises". (The Regressive Tax chip is a
  glossary source candidate — if approved, check verify_glossary.)
- **Confidence** — high (typo only).
- **Status** — fixed (approved by Eliot 2026-08-06. The Regressive
  Tax chip IS a glossary source, so the glossary was re-extracted
  and rebuilt per its pipeline; verify_glossary exits 0).

## 33. Theme 4 taxation caption references a T* label the figure does not carry

- **Location** — same page, Figure 1 caption (`laffer-curve.png`).
- **Issue** — the caption says "there is an optimal tax rate (T*)
  that maximises revenue", but the figure labels only t1, t2, R1 and
  R2 — no T* appears anywhere in it (nor in laffer-curve.svg, which
  matches the PNG).
- **Proposed correction** — drop the parenthetical: "…suggests there
  is an optimal tax rate that maximises revenue, while rates above
  this can lead to decreased revenue…".
- **Confidence** — high (the figure plainly carries no T* label).
- **Status** — fixed (approved by Eliot 2026-08-06; the parenthetical
  "(T*)" removed from the caption, nothing else changed — captions
  are not glossary sources).

## 34. AQA exchange-rate-systems caption has the E1/E2/E3 mismatch — twin of fixed #28

- **Location** — `revision-notes/aqa-a2-macro/2-6-4-exchange-rate-systems.html`,
  Figure 1 caption (`exchange-rates.png`).
- **Issue** — identical to issue 28 (fixed on the Edexcel twin 4-1-8
  with Eliot's approval): the caption describes a single diagram with
  labels E1/E2/E3 that appear nowhere in the two-panel P1/P2 figure.
- **Proposed correction** — the Edexcel twin's approved wording
  verbatim: "Figure 1: In the left panel, an increase in the supply of
  the currency (S1 to S2) lowers the exchange rate from P1 to P2 — a
  depreciation. In the right panel, an increase in demand for the
  currency (D1 to D2) raises the exchange rate from P1 to P2 — an
  appreciation."
- **Confidence** — high (same figure, same error class as the
  approved fix).
- **Status** — fixed (approved by Eliot 2026-08-06; applied with the
  Edexcel twin's approved wording verbatim — captions are not
  glossary sources).

## 35. AQA balance-of-payments page: "may be require" — twin of fixed #27

- **Location** — `revision-notes/aqa-a2-macro/2-6-3-the-balance-of-payments.html`,
  Significance of Global Imbalances, Persistent deficits paragraph.
- **Issue** — identical to issue 27 (fixed on the Edexcel twin
  4-1-7): "a build-up of foreign debt, which may be require higher
  taxes or spending cuts" — stray "be".
- **Proposed correction** — "…which may require higher taxes or
  spending cuts…". (As on the twin, the Persistent deficits chip is
  a glossary source — if approved, rerun the glossary pipeline.)
- **Confidence** — high (grammar only; same error class as the
  approved fix).
- **Status** — fixed (approved by Eliot 2026-08-06. As on the twin,
  the Persistent deficits chip IS a glossary source — the glossary
  was re-extracted and rebuilt; verify_glossary exits 0).

## 36. AQA balance-of-payments: the "cause of a deficit" surplus bullet — twin of fixed #29

- **Location** — same page, "Causes of a Current Account Deficit"
  list.
- **Issue** — identical to issue 29 (fixed on the Edexcel twin
  4-1-7): under the deficit-causes heading, the bullet reads
  "Economic growth abroad: If other countries are growing faster
  than the domestic economy, they may import more from the domestic
  country, leading to a surplus."
- **Proposed correction** — the Edexcel twin's approved wording
  verbatim: "Slow economic growth abroad: If other countries are
  growing more slowly than the domestic economy, demand for the
  country's exports weakens while its own demand for imports stays
  strong, leading to a deficit."
- **Confidence** — high (same error class as the approved fix).
- **Status** — fixed (approved by Eliot 2026-08-06; applied with the
  Edexcel twin's approved wording verbatim, no glossary coupling —
  the bullet is not a chip definition).

## 24. Theme 4 terms-of-trade interpretation paragraph missing a full stop

- **Location** — `revision-notes/edexcel-theme-4/4-1-4-terms-of-trade.html`,
  Definition and Calculation section, Interpretation paragraph.
- **Issue** — the paragraph ends "…which is generally considered a
  deterioration in the terms of trade" with no full stop.
- **Proposed correction** — "…a deterioration in the terms of trade."
- **Confidence** — high (punctuation only).
- **Status** — fixed (approved by Eliot 2026-08-06; full stop added,
  no glossary coupling).

## 37. Five diagram cards' alt text still describes the old single-panel SVGs

- **Location** — the deck sources: `flashcards-data/aqa/micro.json`
  (`aqa-1-5-3-diagram-02`, `aqa-1-5-3-diagram-03`) and
  `flashcards-data/edexcel-a/theme-3.json` (`edexcel-a-3-4-2-diagram-02`,
  `edexcel-a-3-4-2-diagram-03`, `edexcel-a-3-3-4-diagram-03`).
- **Issue** — `perfect-competition-short-run-supernormal-profit.svg`,
  `perfect-competition-short-run-loss.svg` and
  `short-run-shutdown-condition.svg` each gained a second panel in the
  QA remediation (Market/Firm; keep-operating/shut-down), but these
  cards' alt text still describes the single-panel versions — a
  screen-reader user is told about half the diagram. Carried from
  `_archive/FLASHCARDS_PROGRESS.md` ("should be revisited when those
  cards are next edited") during the 2026-08-26 clean-up; verified
  still live in the payloads the same day.
- **Proposed correction** — reword each alt to describe both panels;
  the wording is card text, so it is Eliot's.
- **Confidence** — high (the SVGs and the deck JSON visibly disagree
  today).
- **Status** — open.

## 38. Edexcel B 1.4.3 exam tip offers trade credit for paying staff

- **Location** — `revision-notes/edexcel-b-theme-1/1-4-3-types-and-sources-of-credit.html`,
  "Comparing Sources of Finance", the "Match the finance to what it is for"
  exam tip (source: `notes-data/topics/edexcel-b-theme-1/1-4-3-types-and-sources-of-credit.html`).
- **Issue** — the tip reads "A short-term need, such as paying staff while
  waiting for a customer to pay, suits an overdraft or trade credit." Trade
  credit comes from suppliers: it defers what a business owes for goods and
  cannot pay wages. At best it helps indirectly, by freeing up cash that would
  otherwise go to suppliers. The page's own definition says this ("a supplier
  lets a business take goods now and pay for them later"). Found by the
  cold-solver verify pass on Edexcel B flashcards unit 1.4 (`NOTES?` on
  `edexcel-b-1-4-3-app-01`). The card now says "Overdraft" alone and does
  not rely on this sentence.
- **Proposed correction** — either change the example so both sources fit:
  "A short-term need, such as buying stock or covering a gap while waiting for
  a customer to pay, suits an overdraft or trade credit." Or keep the example
  and drop trade credit: "A short-term need, such as paying staff while
  waiting for a customer to pay, suits an overdraft." The wording is Eliot's
  call.
- **Confidence** — medium-high (standard theory; the page's own trade-credit
  definition). It is a loose example, not a false principle.
- **Status** — fixed (approved by Eliot 2026-11-09: the second
  wording, trade credit dropped; "...suits an overdraft." No glossary
  coupling, the tip is not a chip).

## 39. Edexcel B 1.6.4 worked example treats a cash surplus as proof of profit

- **Location** — `revision-notes/edexcel-b-theme-1/1-6-4-business-survival-and-cash-flow.html`,
  "Worked Example: Rosa's Christmas Rush", the paragraph under the table
  (source: `notes-data/topics/edexcel-b-theme-1/1-6-4-business-survival-and-cash-flow.html`).
- **Issue** — the page reads "Over the three months Rosa takes £24,000 and
  spends £14,000, so the quarter is profitable: her bank balance ends £10,000
  higher than it started." That reasons from cash to profit, on the page whose
  point is that the two differ. It roughly holds here, because all Rosa's
  customers pay straight away, but materials bought in October and not yet
  used by the end of December would not be a cost of the quarter, so the cash
  surplus and the profit need not match. Found by the cold-solver verify pass
  on Edexcel B flashcards unit 1.6 (`NOTES?`). No card depends on this
  sentence.
- **Proposed correction** — keep the cash fact and drop the inference, e.g.
  "Over the three months Rosa takes £24,000 and spends £14,000, so her bank
  balance ends £10,000 higher than it started, and the season is a good one."
  Or keep "profitable" and say why it holds here: "...and because her
  customers pay straight away and she uses the materials she buys, the
  quarter is profitable too." The wording is Eliot's call.
- **Confidence** — medium (the sentence is not false for Rosa; it models a
  shortcut the page warns against).
- **Status** — fixed (approved by Eliot 2026-11-09: the first
  wording, verbatim. No card or glossary coupling).

## 40. Edexcel B 2.3.1 states a capital-intensive firm always has the higher break-even output

- **Location** — `revision-notes/edexcel-b-theme-2/2-3-1-productivity.html`,
  "Labour-Intensive and Capital-Intensive Production", the paragraph under the
  comparison table (source: `notes-data/topics/edexcel-b-theme-2/2-3-1-productivity.html`).
- **Issue** — the page reads "Because its costs are mostly fixed, a
  capital-intensive firm has a higher break-even output than a labour-intensive
  one." Break-even output is fixed costs ÷ contribution per unit. A
  capital-intensive firm usually has lower variable cost per unit, so a larger
  contribution, which pulls break-even output down. Higher break-even output is
  likely but not certain. It is a common textbook simplification, stated here
  as a rule. Found by the cold-solver verify pass on Edexcel B flashcards unit
  2.3 (`NOTES?` on `edexcel-b-2-3-1-def-02`). The card now stops at "it needs
  high output to keep average cost down" and does not rely on this sentence.
- **Proposed correction** — hedge it, e.g. "Because its costs are mostly
  fixed, a capital-intensive firm usually has a higher break-even output than
  a labour-intensive one." Or leave it as written, as a deliberate
  simplification. The wording is Eliot's call.
- **Confidence** — medium (standard theory; the claim holds in the typical
  case and the page's own context).
- **Status** — fixed (approved by Eliot 2026-11-09: "usually" added,
  "...a capital-intensive firm usually has a higher break-even output than a
  labour-intensive one". No glossary coupling, the sentence is not a chip.
  The card `edexcel-b-2-3-1-def-02` stays without the clause).

## 41. Edexcel B 2.5.3 says the ONS does not count RPI as an official statistic

- **Location** — `revision-notes/edexcel-b-theme-2/2-5-3-inflation.html`,
  "Price Indices: CPI and RPI", the RPI paragraph (source:
  `notes-data/topics/edexcel-b-theme-2/2-5-3-inflation.html`).
- **Issue** — the page reads "The ONS says RPI is not good enough to be an
  official statistic, but still publishes it because some long-term
  contracts are linked to it." RPI lost its *National Statistic* (now
  "accredited official statistic") status in 2013, but it is still
  produced and published as an official statistic. "Not good enough to be
  an official statistic" overstates the downgrade. Found by the cold-solver
  verify pass on Edexcel B flashcards unit 2.5 (`NOTES?` on
  `edexcel-b-2-5-3-formula-01`). The card now says only "It is still
  published because some long-term contracts are linked to it." It does
  not rely on the doubtful clause.
- **Proposed correction** — "The ONS no longer treats RPI as an accredited
  National Statistic, because it is a poor measure of inflation, but still
  publishes it because some long-term contracts are linked to it." Or,
  simpler: "RPI is no longer an accredited National Statistic, but the ONS
  still publishes it because some long-term contracts are linked to it."
  The wording is Eliot's call.
- **Confidence** — medium-high (the 2013 de-designation of RPI as a
  National Statistic is well documented; checked from memory, not against
  the ONS or UK Statistics Authority page in this session). Not a chip, so
  no glossary coupling.
- **Status** — fixed (approved by Eliot 2026-11-09, the simpler wording:
  "RPI is no longer an accredited National Statistic, but the ONS still
  publishes it because some long-term contracts are linked to it." The
  card `edexcel-b-2-5-3-formula-01` stays as it is: it no longer makes the
  claim either way).

## 42. Edexcel B 3.1.4 labels the tariff diagram's green area as "revenue and profit"

- **Location** — `revision-notes/edexcel-b-theme-3/3-1-4-trade-policy-and-trade-negotiations.html`,
  "Tariffs", the "Home producers gain" bullet under Figure 1 (source:
  `notes-data/topics/edexcel-b-theme-3/3-1-4-trade-policy-and-trade-negotiations.html`).
- **Issue** — the page reads "they expand output from Q1 to Q2 → higher
  revenue and profit (the green area), and more jobs." The green area, to
  the left of Sdomestic between Sworld and Sworld+tariff, is the gain in
  domestic producer surplus. The rise in revenue is larger: it is the green
  area plus the cost of producing the extra units Q1 to Q2, which is the
  area under Sdomestic between Q1 and Q2 (the left red triangle and the
  rectangle below Sworld). So "revenue" is not the green area. "Profit"
  is close enough at A level, since producer surplus is usually taught as
  the producers' gain. Found by the cold-solver verify
  pass on Edexcel B flashcards unit 3.1 (`NOTES?` on
  `edexcel-b-3-1-4-diagram-01`). The card now says "a gain in producer
  surplus (the green area), and more jobs".
- **Proposed correction** — "→ higher revenue and profit, and more jobs.
  The green area is their gain in producer surplus." Or, shorter: "→ a gain
  in producer surplus (the green area), and more jobs." Or leave it as
  written, as a deliberate simplification. The wording is Eliot's call.
- **Confidence** — medium (standard welfare analysis; the bullet is loose,
  not backwards). Not a chip, so no glossary coupling. The same sentence
  does not appear in the figure's caption or alt text.
- **Status** — fixed (approved by Eliot 2026-11-10, the shorter wording:
  "→ a gain in producer surplus (the green area), and more jobs." The card
  `edexcel-b-3-1-4-diagram-01` already says the same, so it is unchanged).

## 43. Edexcel B 3.2.1 gives lower foreign wages as the cost saving from outsourcing as well as offshoring

- **Location** — `revision-notes/edexcel-b-theme-3/3-2-1-conditions-that-prompt-trade.html`,
  "Offshoring and Outsourcing", the "Costs" bullet under "When a firm
  offshores or outsources:" (source:
  `notes-data/topics/edexcel-b-theme-3/3-2-1-conditions-that-prompt-trade.html`).
- **Issue** — the bullet reads "Costs: wages and rents are lower abroad →
  lower unit costs → the firm can cut prices or earn a higher margin." The
  list is introduced as applying to a firm that "offshores or outsources",
  but the page's own exam tip says outsourcing hands work to another firm
  "which may be in the same town". For outsourcing within the UK, lower
  wages abroad are not why it saves money. The section's opening line,
  "Firms also trade by buying from abroad", has the same slant, though
  that line is about trade and is fair in context. Found by the cold-solver
  verify pass on Edexcel B flashcards unit 3.2 (`NOTES?` on
  `edexcel-b-3-2-1-eval-01`). The card now reads "Lower costs: when the
  work moves abroad, wages and rents are lower → …".
- **Proposed correction** — "Costs: when the work moves abroad, wages and
  rents are lower → lower unit costs → …". Or leave it as written: the
  section is about trade, so the reader can take it as offshoring. The
  wording is Eliot's call.
- **Confidence** — low (the bullet is loose, not wrong for the offshoring
  case the section is mainly about). Not a chip, so no glossary coupling.
- **Status** — fixed (approved by Eliot 2026-11-10, the proposed wording:
  "Costs: when the work moves abroad, wages and rents are lower → lower
  unit costs → …". The card `edexcel-b-3-2-1-eval-01` already says the
  same, so it is unchanged).

## 44. Edexcel B 3.3.2 sends the reader to the PED page for mass and niche markets

- **Location** — `revision-notes/edexcel-b-theme-3/3-3-2-demand-side-factors-in-global-markets.html`,
  "How Firms Respond to Demand-Side Factors", second paragraph: "How far a
  firm then adapts its marketing depends on whether it sells to a mass
  market or a niche (unit 2.2.1)" (source:
  `notes-data/topics/edexcel-b-theme-3/3-3-2-demand-side-factors-in-global-markets.html`).
- **Issue** — the cross-reference goes to
  `2-2-1-price-elasticity-of-demand.html`. The cold-solver verify pass on
  Edexcel B flashcards unit 3.3 (`NOTES?`, raised while checking
  `edexcel-b-3-3-2-def-02`) questioned whether a PED page is the right
  place to send a reader for mass and niche markets. Checked: 2.2.1 has a
  section, "Pricing in Niche and Mass Markets", with chips for both terms,
  so the link lands on a definition. B also defines both terms in 1.3.4
  (`1-3-4-price-mechanism.html`) and niche markets in 2.1.5. The card does
  not depend on the link and is unchanged.
- **Proposed correction** — none recommended: leave the link as written.
  The alternative is to point it at 1.3.4, where B first teaches the two
  terms. The wording is Eliot's call.
- **Confidence** — low (the link is defensible; this is a choice of
  target, not an error). Not a chip, so no glossary coupling.
- **Status** — closed, no change (Eliot, 2026-11-10: the link stays on
  2.2.1).

## 45. Edexcel B 3.5.2 lists the cost to firms under "Both can push wages up"

- **Location** — `revision-notes/edexcel-b-theme-3/3-5-2-wage-rates.html`,
  "Trade Unions and Professional Bodies", the list introduced by "Both can
  push wages up:" (source:
  `notes-data/topics/edexcel-b-theme-3/3-5-2-wage-rates.html`).
- **Issue** — the list has three bullets: collective bargaining, entry
  requirements and "The cost to firms: pay rises → labour costs rise → the
  firm raises prices, accepts lower profit or employs fewer people". The
  third is a consequence of higher pay, not a way a union or professional
  body pushes wages up, so it sits under a heading it does not answer. The
  economics is right; only the grouping is off. Found by the cold-solver
  verify pass on Edexcel B flashcards unit 3.5 (`NOTES?`, raised while
  rechecking `edexcel-b-3-5-2-eval-01`). The cards `3-5-2-def-03` and
  `3-5-2-eval-01` give the cost its own line and do not depend on the
  heading.
- **Proposed correction** — either change the lead-in to something like
  "Both can push wages up, at a cost to firms:", or move the third bullet
  out of the list into its own sentence before "Firms can gain too." Or
  leave it as written. The wording is Eliot's call.
- **Confidence** — low (a structure point, not an error of fact). Not a
  chip, so no glossary coupling.
- **Status** — closed, no change (Eliot, 2026-11-10: the list stays as
  written).

## 46. The kinked demand curve labels the kink price "Pcompetitive"

- **Location** — the figure `images/diagrams/kinked-demand-curve.png`, its
  alt text on `revision-notes/edexcel-b-theme-4/4-1-3-oligopoly.html`,
  "Interdependence and Price Stability", Figure 1 (source:
  `notes-data/topics/edexcel-b-theme-4/4-1-3-oligopoly.html`). The same
  PNG is on Edexcel A 3.4.4 and AQA 1.5.5, whose prose calls it
  "P_competitive". The flashcard SVG `images/diagrams/svg/kinked-demand-curve.svg`
  shortens it to "Pcomp" and is used by `edexcel-a-3-4-4-diagram-02`,
  `aqa-1-5-5-diagram-02` and now `edexcel-b-4-1-3-diagram-01`.
- **Issue** — the kink sits at the price the market has settled at. It is
  not the competitive price in the textbook sense (P = MC, normal profit):
  the same figure draws an AC curve giving C below the kink price, so the
  firm is making supernormal profit there. A student could read
  "competitive" as meaning the oligopoly prices like a competitive market.
  "P1" or "Pcurrent" would be clearer. Found by the cold-solver verify pass
  on Edexcel B flashcards unit 4.1 (`NOTES?` on
  `edexcel-b-4-1-3-diagram-01`). The card no longer glosses the label as
  "the competitive price". It says "the current price, labelled Pcomp".
- **Proposed correction** — none recommended in this run. Relabelling is a
  figure change across three boards (one PNG, one SVG and the A and AQA
  prose that names the label), so it is a decision about the shared
  diagram, not a B wording fix. Options: relabel to P1 everywhere, change
  only the B alt text, or leave it. The wording is Eliot's call.
- **Confidence** — medium (the label is loose rather than wrong; "the
  competitive price" can be read as "the price competition has settled
  at"). Not a chip, so no glossary coupling.
- **Status** — open, deferred (Eliot, 2026-11-11: leave it for now; it
  is a change to a figure shared by three boards, for a later look).

## 47. The perfect competition figures use one Q label for the market and the firm

- **Location** — `images/diagrams/perfect-competition-short-run-supernormal-profit.png`
  and `images/diagrams/perfect-competition-profit-to-longrun.png`, as
  described in the alt text on
  `revision-notes/edexcel-b-theme-4/4-1-1-spectrum-of-competition.html`,
  Figures 1 and 2 (source:
  `notes-data/topics/edexcel-b-theme-4/4-1-1-spectrum-of-competition.html`).
  Both PNGs are also on Edexcel A 3.4.2 and AQA 1.5.3.
- **Issue** — the market panel and the firm panel both mark output Q1 in
  Figure 1, and Q2 in Figure 2. The market's quantity and one firm's
  quantity are not the same number. In Figure 2 the firm's output also
  moves down its MC curve as the price falls, while the market quantity
  rises, so the shared "Q2" suggests both rise. This is a common A-level
  shortcut. Found by the cold-solver verify pass on Edexcel B flashcards
  unit 4.1 (`NOTES?`, low priority, raised while checking
  `edexcel-b-4-1-1-diagram-01`). The card uses the flashcard SVG for
  Figure 1 only, which also labels both Q1, and does not depend on the
  label.
- **Proposed correction** — none recommended: leave the figures as drawn.
  The alternative is to relabel the firm panels q1 and q2, a figure change
  on three boards. The wording is Eliot's call.
- **Confidence** — low (a labelling convention, widely used). Not a chip,
  so no glossary coupling.
- **Status** — closed, no change (Eliot, 2026-11-11: the figures stay
  as drawn).

## 48. Edexcel B 4.1.2 equates limit pricing with pricing at about average cost

- **Location** — `revision-notes/edexcel-b-theme-4/4-1-2-barriers-to-entry.html`,
  "Contestability and Ease of Entry", the "Prices" bullet (source:
  `notes-data/topics/edexcel-b-theme-4/4-1-2-barriers-to-entry.html`).
- **Issue** — the page says firms "keep prices close to average cost, a
  tactic called limit pricing". Strictly, limit pricing means setting a
  price just low enough to deter entry, which need not be average cost.
  Equating the two is a simplification. It is the same one Edexcel A 3.4.7
  and AQA 1.5.9 make in their `limit pricing` chip ("set price below the
  profit-maximising level so that they earn only normal profit", "around
  AR = AC"), so B is consistent with the rest of the site. Found by the
  cold-solver verify pass on Edexcel B flashcards unit 4.1 (`NOTES?`, low
  priority and "arguably fine", raised while checking
  `edexcel-b-4-1-2-def-02`). The card follows the page.
- **Proposed correction** — none recommended: leave it, as the simplest
  accurate version for A level and consistent with A and AQA. The wording
  is Eliot's call.
- **Confidence** — low. Not a chip on B, so no glossary coupling.
- **Status** — closed, no change (Eliot, 2026-11-11: the page stays as
  written).

## 49. Edexcel B 4.4.3 says privatisation lowers barriers to entry

- **Location** — `revision-notes/edexcel-b-theme-4/4-4-3-supply-side-policies.html`,
  "Policies for Each Aim" table, the "Promote competition" row, market-based
  column (source:
  `notes-data/topics/edexcel-b-theme-4/4-4-3-supply-side-policies.html`).
- **Issue** — the cell reads "Deregulation and privatisation, lowering
  barriers to entry". Deregulation lowers barriers to entry. Privatisation
  on its own only moves a firm from public to private ownership: a
  privatised monopoly stays a monopoly unless the market is also opened to
  new firms. The cell lets a reader take the two together. Found by the
  cold-solver verify pass on Edexcel B flashcards unit 4.4 (`NOTES?`,
  raised while checking `edexcel-b-4-4-3-app-01`). The card now says only
  that privatisation is market-based and promotes competition, which is
  the row it sits in.
- **Proposed correction** — "Deregulation, lowering barriers to entry;
  privatisation, with markets opened to new firms". Or leave it as the
  simplest version for A level. The wording is Eliot's call.
- **Confidence** — medium (standard theory: privatisation and
  liberalisation are separate policies). Not a chip, so no glossary
  coupling.
- **Status** — open.

## 50. Edexcel B 4.4.3 classes R&D tax relief as interventionist

- **Location** — same page, "Policies for Each Aim" table, the "Increase
  incentives" row, interventionist column.
- **Issue** — the cell reads "Tax relief or grants for research and
  development, and for investment in new equipment". Grants are clearly
  interventionist. Tax relief is classed either way in textbooks: some
  call any tax incentive market-based. On the page's own chips, relief
  targeted at one activity is the government directing resources, so
  interventionist is defensible, but a student who reads "market-based
  ... incentives are stronger" could fairly answer market-based. Found by
  the cold-solver verify pass on Edexcel B flashcards unit 4.4 (`NOTES?`,
  "a wording risk, not an error"). The card no longer uses this item.
- **Proposed correction** — none needed for accuracy. Optionally "Grants
  for research and development and for new equipment, or tax relief
  targeted at them" to show why it counts as directing resources. The
  wording is Eliot's call.
- **Confidence** — low (a classification convention). Not a chip, so no
  glossary coupling.
- **Status** — open.

## 51. Edexcel B 4.4.3 says a Keynesian LRAS shift always lowers the price level

- **Location** — same page, "Showing Supply-Side Policies on a Diagram",
  the sentence before Figure 2 and the Figure 2 caption.
- **Issue** — on the Keynesian diagram, a right shift of LRAS lowers the
  price level and raises real GDP only where AD crosses LRAS on its rising
  or vertical section. Where AD crosses the flat section, output and
  prices barely change. The page states the result without that
  condition, though its own "No help in a recession" bullet makes the same
  point in words. Found by the cold-solver verify pass on Edexcel B
  flashcards unit 4.4 (`NOTES?`, "minor, possibly not worth logging",
  raised while checking `edexcel-b-4-4-3-diagram-01`). The card follows
  the page and the figure, which draws AD on the rising section.
- **Proposed correction** — none recommended: Figure 2 shows the case the
  sentence describes, and the recession bullet covers the rest. Leaving it
  keeps the page simple.
- **Confidence** — low. Not a chip, so no glossary coupling.
- **Status** — open.
