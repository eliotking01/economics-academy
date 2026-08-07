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
