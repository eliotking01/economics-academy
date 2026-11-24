#!/usr/bin/env python3
"""Which page on each other board covers the same topic.

    python3 scripts/notes_twins.py              # print the whole map
    python3 scripts/notes_twins.py --unpaired   # topics with no twin

Imported by notes_extras.py, which renders the block, and by
seo/tools/verify_seo.py, which asserts every pair resolves and crosses the
board boundary in exactly one declared place. One definition, two consumers -
the same arrangement as notes_sequence.py.

THREE BOARDS, AT MOST ONE TWIN PER OTHER BOARD
----------------------------------------------
A page links to at most one page on each of the other two boards, so an
Edexcel B page can carry an Edexcel A twin and an AQA twin, and an Edexcel A
or AQA page can carry its existing twin plus an Edexcel B one. `twins()`
returns them in BOARD_ORDER and the block renders them as one sentence.
The tables are kept apart by direction - TWINS (Edexcel A <-> AQA, 2026-08-21),
B_TO_A, B_TO_AQA and TO_B (2026-11-24, D67 Phase 5) - so no table can hold two
targets on one board for a page, and `main()` checks each one only ever
crosses the boundary it is named for.

WHY THIS IS A TABLE AND NOT A DERIVATION
----------------------------------------
Everything else about the notes is derived from something that already owns
it: the chain from the hubs' own link order, the board record from
boards.json. There is nothing in this repo that owns the mapping between an
Edexcel topic and its AQA counterpart, and the one thing that looks like it
does - the spec code - is the trap. 37 codes are claimed by both boards with
different meanings; 1.1.1 is "Economics as a Social Science" on Edexcel and
"Economic Methodology" on AQA. A map keyed on a bare code would resolve, 404
nothing, pass every other check and send students to the wrong board.

So the table is written down, and the evidence for each row is written down
with it. Each row's number is the Jaccard similarity of the two pages' prose
over 5-word shingles, the measure seo/07-link-graph.md and DO-NOT-BREAK use.
(The seo/tools/twin_evidence.py that computed it was never committed.) Rows
were seeded by taking the mutual best match on that measure and then read one
by one; the ones changed or added by hand say so.

The Edexcel B rows cannot use that measure: the B pages were written fresh, so
every B pairing scores 0.014 or less. They were seeded from the coverage maps
the B pages were planned from and judged on what each page teaches - its <h2>
sections and its key-definition terms, both ways. Each row's comment is its
rating (close / partial / loose) and, where it matters, what the two pages do
not share. The review sheet that Eliot approved row by row is
drafts/all-boards-parity/review/twins.md, outside the repo.

WHAT IS DELIBERATELY LEFT OUT
-----------------------------
A pairing that is merely the nearest available page is worse than no pairing.
The two boards genuinely split some topics differently - Edexcel's
"Demand-Side Policies" is monetary AND fiscal, which AQA separates into 2.4.3
and 2.5.1 - and some topics have no counterpart worth linking. `--unpaired`
lists them. Edexcel B is the extreme case: its business units (break-even,
cash flow, MNCs, lean production...) have no page on either other board, and
the candidates that were considered and dropped for B are recorded in the
review sheet so a future session need not repeat the search.

THE MAP IS DIRECTED, NOT A BIJECTION
------------------------------------
Two Edexcel pages can legitimately point at one AQA page: Edexcel splits
economic methodology across 1.1.1 and 1.1.2 and AQA does not. Each direction
is stated separately so neither has to be inferred. With Edexcel B this
matters more: B 4.4.1 The AD/AS Model is one page where Edexcel A and AQA have
five each, so ten pages point at it while it points at one on each board.

Standard library only.
"""

from __future__ import annotations

import argparse
import sys

E1, E2, E3, E4 = ("edexcel-theme-1", "edexcel-theme-2",
                  "edexcel-theme-3", "edexcel-theme-4")
AMI, AMA = "aqa-a2-micro", "aqa-a2-macro"
B1, B2, B3, B4 = ("edexcel-b-theme-1", "edexcel-b-theme-2",
                  "edexcel-b-theme-3", "edexcel-b-theme-4")

# The board keys, in the order a page's twins are named, and how the twin
# sentence names each board. "Edexcel A", not "Edexcel": once an Edexcel B
# link can sit beside it, the bare name is ambiguous (approved 2026-11-24).
BOARD_ORDER = ("edexcel", "aqa", "edexcel-b")
BOARD_LABEL = {"edexcel": "Edexcel A", "aqa": "AQA", "edexcel-b": "Edexcel B"}

# (dir, slug) -> (dir, slug). The comment on each row is its measured prose
# similarity; "hand" marks a row that is not the mutual best match, with the
# reason.
TWINS: dict[tuple[str, str], tuple[str, str]] = {
    # ---- Edexcel -> AQA ------------------------------------------------
    (E1, "1-1-1-economics-as-a-social-science"): (AMI, "1-1-1-economic-methodology"),                              # 0.334 hand: AQA 1.1.1 is the whole of Edexcel 1.1.1 plus 1.1.2
    (E1, "1-1-2-positive-normative-statements"): (AMI, "1-1-1-economic-methodology"),                              # 0.354
    (E1, "1-1-3-the-economic-problem"): (AMI, "1-1-4-scarcity-choice-and-the-allocation-of-resources"),            # 0.366
    (E1, "1-1-4-production-possibility-frontiers"): (AMI, "1-1-5-production-possibility-diagrams"),                # 0.651
    (E1, "1-1-5-specialisation-division-of-labour"): (AMI, "1-4-2-specialisation-division-of-labour-and-exchange"),# 0.722
    (E1, "1-2-1-rational-decision-making"): (AMI, "1-2-1-consumer-behaviour"),                                     # 0.186
    (E1, "1-2-2-demand"): (AMI, "1-3-1-the-determinants-of-the-demand-for-goods-and-services"),                    # 0.662
    (E1, "1-2-3-price-income-cross-elasticities-of-demand"): (AMI, "1-3-2-price-income-and-cross-elasticities-of-demand"),  # 0.822
    (E1, "1-2-4-supply"): (AMI, "1-3-3-the-determinants-of-the-supply-of-goods-and-services"),                     # 0.623
    (E1, "1-2-5-price-elasticity-of-supply"): (AMI, "1-3-4-price-elasticity-of-supply"),                           # 0.764
    (E1, "1-2-6-price-determination"): (AMI, "1-3-5-the-determination-of-equilibrium-market-prices"),              # 0.648
    (E1, "1-2-7-price-mechanism"): (AMI, "1-8-1-how-markets-and-prices-allocate-resources"),                       # 0.564
    (E1, "1-2-8-producer-consumer-surplus"): (AMI, "1-5-11-consumer-and-producer-surplus"),                        # 0.394
    (E1, "1-3-1-types-of-market-failure"): (AMI, "1-8-2-the-meaning-of-market-failure"),                           # 0.490
    (E1, "1-3-2-externalities"): (AMI, "1-8-4-positive-and-negative-externalities-in-consumption-and-production"), # 0.737
    (E1, "1-3-3-public-goods"): (AMI, "1-8-3-public-goods-private-goods-and-quasi-public-goods"),                  # 0.326
    (E1, "1-3-4-information-gaps"): (AMI, "1-2-2-imperfect-information"),                                          # 0.197 hand: the mutual best match was 1.8.6 Market Imperfections at 0.265, but AQA names the topic itself in 1.2.2
    (E1, "1-4-1-government-intervention-in-markets"): (AMI, "1-8-9-government-intervention-in-markets"),           # 0.838
    (E1, "1-4-2-government-failure"): (AMI, "1-8-10-government-failure"),                                          # 0.672
    (E2, "2-1-2-inflation"): (AMA, "2-3-3-inflation-and-deflation"),                                               # 0.459
    (E2, "2-1-3-employment-unemployment"): (AMA, "2-3-2-employment-and-unemployment"),                             # 0.698
    (E2, "2-1-4-balance-of-payments"): (AMA, "2-6-3-the-balance-of-payments"),                                     # 0.118 hand: Edexcel carries this topic twice; 4.1.7 is the mutual match at 0.816 and this is its Theme 2 half
    (E2, "2-3-2-short-run-aggregate-supply"): (AMA, "2-2-5-determinants-of-short-run-aggregate-supply"),           # 0.584
    (E2, "2-3-3-long-run-aggregate-supply"): (AMA, "2-2-6-determinants-of-long-run-aggregate-supply"),             # 0.739
    (E2, "2-4-1-national-income"): (AMA, "2-2-1-the-circular-flow-of-income"),                                     # 0.603
    (E2, "2-4-4-the-multiplier"): (AMA, "2-2-4-aggregate-demand-and-the-level-of-economic-activity"),              # 0.771
    (E2, "2-5-1-causes-of-growth"): (AMA, "2-3-1-economic-growth-and-the-economic-cycle"),                         # 0.228
    (E2, "2-6-1-possible-macroeconomic-objectives"): (AMA, "2-1-1-the-objectives-of-government-economic-policy"),  # 0.491
    (E2, "2-6-3-supply-side-policies"): (AMA, "2-5-2-supply-side-policies"),                                       # 0.891
    (E2, "2-6-4-conflicts-between-objectives-and-policies"): (AMA, "2-3-4-possible-conflicts-between-macroeconomic-policy-objectives"),  # 0.565
    (E3, "3-2-1-business-objectives"): (AMI, "1-5-2-the-objectives-of-firms"),                                     # 0.498
    (E3, "3-3-1-revenue"): (AMI, "1-4-6-marginal-average-and-total-revenue"),                                      # 0.604
    (E3, "3-3-2-costs"): (AMI, "1-4-4-costs-of-production"),                                                       # 0.701
    (E3, "3-3-3-economies-diseconomies-of-scale"): (AMI, "1-4-5-economies-and-diseconomies-of-scale"),             # 0.858
    (E3, "3-3-4-normal-profits-supernormal-profits-losses"): (AMI, "1-4-7-profit"),                                # 0.266
    (E3, "3-4-1-efficiency"): (AMI, "1-5-10-market-structure-efficiency-resource-allocation"),                     # 0.679
    (E3, "3-4-2-perfect-competition"): (AMI, "1-5-3-perfect-competition"),                                         # 0.664
    (E3, "3-4-3-monopolistic-competition"): (AMI, "1-5-4-monopolistic-competition"),                               # 0.767
    (E3, "3-4-4-oligopoly"): (AMI, "1-5-5-oligopoly"),                                                             # 0.695
    (E3, "3-4-5-monopoly"): (AMI, "1-5-6-monopoly-and-monopoly-power"),                                            # 0.550
    (E3, "3-4-6-monopsony"): (AMI, "1-6-4-wage-determination-imperfectly-competitive-labour-markets"),             # 0.074 hand: AQA has no monopsony page of its own and covers it here, which its own title says
    (E3, "3-4-7-contestability"): (AMI, "1-5-9-contestable-and-non-contestable-markets"),                           # 0.741
    (E3, "3-5-1-demand-for-labour"): (AMI, "1-6-1-the-demand-for-labour-marginal-productivity-theory"),            # 0.729
    (E3, "3-5-2-supply-of-labour"): (AMI, "1-6-2-influence-upon-the-supply-of-labour-to-different-markets"),       # 0.743
    (E3, "3-5-3-wage-determination"): (AMI, "1-6-3-wage-determination-perfectly-competitive-labour-markets"),      # 0.078 hand: the mutual match was 1.6.5 Trade Unions at 0.214, but AQA splits this topic across 1.6.3 to 1.6.5 and 1.6.3 is where it starts
    (E4, "4-1-1-globalisation"): (AMA, "2-6-1-globalisation"),                                                     # 0.831
    (E4, "4-1-2-specialisation-trade"): (AMA, "2-6-2-trade"),                                                      # 0.362
    (E4, "4-1-7-balance-of-payments"): (AMA, "2-6-3-the-balance-of-payments"),                                     # 0.816
    (E4, "4-1-8-exchange-rates"): (AMA, "2-6-4-exchange-rate-systems"),                                            # 0.592
    (E4, "4-2-1-absolute-relative-poverty"): (AMI, "1-7-2-the-problem-of-poverty"),                                # 0.206
    (E4, "4-2-2-inequality"): (AMI, "1-7-1-the-distribution-of-income-and-wealth"),                                # 0.599
    (E4, "4-3-2-factors-influencing-growth-development"): (AMA, "2-6-5-economic-growth-and-development"),          # 0.311
    (E4, "4-4-1-role-of-financial-markets"): (AMA, "2-4-1-the-structure-of-financial-markets-and-financial-assets"),  # 0.107
    (E4, "4-4-2-market-failure-in-the-financial-sector"): (AMA, "2-4-4-the-regulation-of-the-financial-system"),   # 0.062 hand: name-equivalent, and 2.4.4 is where AQA puts financial-sector failure
    (E4, "4-4-3-role-of-central-banks"): (AMA, "2-4-3-central-banks-and-monetary-policy"),                         # 0.093 hand: near-identical titles; the mutual match had 2.4.3 paired with Edexcel's Demand-Side Policies, which is monetary AND fiscal and so is not a twin of either AQA half

    # ---- AQA -> Edexcel ------------------------------------------------
    (AMI, "1-1-1-economic-methodology"): (E1, "1-1-1-economics-as-a-social-science"),
    (AMI, "1-1-4-scarcity-choice-and-the-allocation-of-resources"): (E1, "1-1-3-the-economic-problem"),
    (AMI, "1-1-5-production-possibility-diagrams"): (E1, "1-1-4-production-possibility-frontiers"),
    (AMI, "1-2-1-consumer-behaviour"): (E1, "1-2-1-rational-decision-making"),
    (AMI, "1-2-2-imperfect-information"): (E1, "1-3-4-information-gaps"),
    (AMI, "1-3-1-the-determinants-of-the-demand-for-goods-and-services"): (E1, "1-2-2-demand"),
    (AMI, "1-3-2-price-income-and-cross-elasticities-of-demand"): (E1, "1-2-3-price-income-cross-elasticities-of-demand"),
    (AMI, "1-3-3-the-determinants-of-the-supply-of-goods-and-services"): (E1, "1-2-4-supply"),
    (AMI, "1-3-4-price-elasticity-of-supply"): (E1, "1-2-5-price-elasticity-of-supply"),
    (AMI, "1-3-5-the-determination-of-equilibrium-market-prices"): (E1, "1-2-6-price-determination"),
    (AMI, "1-4-2-specialisation-division-of-labour-and-exchange"): (E1, "1-1-5-specialisation-division-of-labour"),
    (AMI, "1-4-4-costs-of-production"): (E3, "3-3-2-costs"),
    (AMI, "1-4-5-economies-and-diseconomies-of-scale"): (E3, "3-3-3-economies-diseconomies-of-scale"),
    (AMI, "1-4-6-marginal-average-and-total-revenue"): (E3, "3-3-1-revenue"),
    (AMI, "1-4-7-profit"): (E3, "3-3-4-normal-profits-supernormal-profits-losses"),
    (AMI, "1-5-2-the-objectives-of-firms"): (E3, "3-2-1-business-objectives"),
    (AMI, "1-5-3-perfect-competition"): (E3, "3-4-2-perfect-competition"),
    (AMI, "1-5-4-monopolistic-competition"): (E3, "3-4-3-monopolistic-competition"),
    (AMI, "1-5-5-oligopoly"): (E3, "3-4-4-oligopoly"),
    (AMI, "1-5-6-monopoly-and-monopoly-power"): (E3, "3-4-5-monopoly"),
    (AMI, "1-5-9-contestable-and-non-contestable-markets"): (E3, "3-4-7-contestability"),
    (AMI, "1-5-10-market-structure-efficiency-resource-allocation"): (E3, "3-4-1-efficiency"),
    (AMI, "1-5-11-consumer-and-producer-surplus"): (E1, "1-2-8-producer-consumer-surplus"),
    (AMI, "1-6-1-the-demand-for-labour-marginal-productivity-theory"): (E3, "3-5-1-demand-for-labour"),
    (AMI, "1-6-2-influence-upon-the-supply-of-labour-to-different-markets"): (E3, "3-5-2-supply-of-labour"),
    (AMI, "1-6-3-wage-determination-perfectly-competitive-labour-markets"): (E3, "3-5-3-wage-determination"),
    (AMI, "1-6-4-wage-determination-imperfectly-competitive-labour-markets"): (E3, "3-4-6-monopsony"),
    (AMI, "1-6-5-the-influence-of-trade-unions-in-determining-wages-and-levels-of-employment"): (E3, "3-5-3-wage-determination"),
    (AMI, "1-7-1-the-distribution-of-income-and-wealth"): (E4, "4-2-2-inequality"),
    (AMI, "1-7-2-the-problem-of-poverty"): (E4, "4-2-1-absolute-relative-poverty"),
    (AMI, "1-8-1-how-markets-and-prices-allocate-resources"): (E1, "1-2-7-price-mechanism"),
    (AMI, "1-8-2-the-meaning-of-market-failure"): (E1, "1-3-1-types-of-market-failure"),
    (AMI, "1-8-3-public-goods-private-goods-and-quasi-public-goods"): (E1, "1-3-3-public-goods"),
    (AMI, "1-8-4-positive-and-negative-externalities-in-consumption-and-production"): (E1, "1-3-2-externalities"),
    (AMI, "1-8-9-government-intervention-in-markets"): (E1, "1-4-1-government-intervention-in-markets"),
    (AMI, "1-8-10-government-failure"): (E1, "1-4-2-government-failure"),
    (AMA, "2-1-1-the-objectives-of-government-economic-policy"): (E2, "2-6-1-possible-macroeconomic-objectives"),
    (AMA, "2-2-1-the-circular-flow-of-income"): (E2, "2-4-1-national-income"),
    (AMA, "2-2-4-aggregate-demand-and-the-level-of-economic-activity"): (E2, "2-4-4-the-multiplier"),
    (AMA, "2-2-5-determinants-of-short-run-aggregate-supply"): (E2, "2-3-2-short-run-aggregate-supply"),
    (AMA, "2-2-6-determinants-of-long-run-aggregate-supply"): (E2, "2-3-3-long-run-aggregate-supply"),
    (AMA, "2-3-1-economic-growth-and-the-economic-cycle"): (E2, "2-5-1-causes-of-growth"),
    (AMA, "2-3-2-employment-and-unemployment"): (E2, "2-1-3-employment-unemployment"),
    (AMA, "2-3-3-inflation-and-deflation"): (E2, "2-1-2-inflation"),
    (AMA, "2-3-4-possible-conflicts-between-macroeconomic-policy-objectives"): (E2, "2-6-4-conflicts-between-objectives-and-policies"),
    (AMA, "2-4-1-the-structure-of-financial-markets-and-financial-assets"): (E4, "4-4-1-role-of-financial-markets"),
    (AMA, "2-4-3-central-banks-and-monetary-policy"): (E4, "4-4-3-role-of-central-banks"),
    (AMA, "2-4-4-the-regulation-of-the-financial-system"): (E4, "4-4-2-market-failure-in-the-financial-sector"),
    (AMA, "2-5-2-supply-side-policies"): (E2, "2-6-3-supply-side-policies"),
    (AMA, "2-6-1-globalisation"): (E4, "4-1-1-globalisation"),
    (AMA, "2-6-2-trade"): (E4, "4-1-2-specialisation-trade"),
    (AMA, "2-6-3-the-balance-of-payments"): (E4, "4-1-7-balance-of-payments"),
    (AMA, "2-6-4-exchange-rate-systems"): (E4, "4-1-8-exchange-rates"),
    (AMA, "2-6-5-economic-growth-and-development"): (E4, "4-3-2-factors-influencing-growth-development"),
}


# ---- Edexcel B (D67 Phase 5, approved 2026-11-24) ----------------------
# Comment = rating, then what the two pages do not share. A note on a B row
# describes that B page's pairing on both boards. "loose, kept on approval"
# is one of the three rows the review sheet flagged as materially different
# ground and Eliot chose to keep.
B_TO_A: dict[tuple[str, str], tuple[str, str]] = {
    (B1, "1-1-1-the-economic-problem"): (E1, "1-1-3-the-economic-problem"),  # close
    (B1, "1-1-2-business-objectives"): (E3, "3-2-1-business-objectives"),  # close: Twins state each objective as an MC/MR rule and add revenue maximisation; B describes them in words (the marginal conditions are B 4.1.4)
    (B1, "1-2-4-specialisation"): (E1, "1-1-5-specialisation-division-of-labour"),  # close: Twins add the functions of money; B splits pros and cons by employer, employee and firm
    (B1, "1-3-1-demand"): (E1, "1-2-2-demand"),  # close
    (B1, "1-3-2-supply"): (E1, "1-2-4-supply"),  # close
    (B1, "1-3-3-price-determination"): (E1, "1-2-6-price-determination"),  # close: B adds the limitations of the model
    (B1, "1-3-4-price-mechanism"): (E1, "1-2-7-price-mechanism"),  # partial: Shared: the three functions. B-only: firm responses, mass and niche markets, market growth - about half the B page
    (B1, "1-5-1-market-failure-and-externalities"): (E1, "1-3-2-externalities"),  # close: Twins add the intervention methods (B 1.5.2 / 4.3.3)
    (B1, "1-5-2-government-intervention-and-failure"): (E1, "1-4-1-government-intervention-in-markets"),  # partial: One B page for two on each board. Link goes to the intervention half (4 of 6 B sections); the government-failure pages point back here instead
    (B2, "2-1-1-growth"): (E3, "3-3-3-economies-diseconomies-of-scale"),  # partial: Shared: economies and diseconomies of scale. B adds market power, profitability, corporate culture; twins add LRAC theory
    (B2, "2-1-2-methods-of-growth"): (E3, "3-1-2-business-growth"),  # close: AQA has no page on growth or integration
    (B2, "2-2-1-price-elasticity-of-demand"): (E1, "1-2-3-price-income-cross-elasticities-of-demand"),  # partial: Twin covers PED, YED and XED on one page; B has no XED and puts YED on 2.2.4
    (B2, "2-2-4-income-elasticity-of-demand"): (E1, "1-2-3-price-income-cross-elasticities-of-demand"),  # partial: YED is one of four sections on the twin. Both B elasticity pages point at the same twin
    (B2, "2-4-1-globalisation"): (E4, "4-1-1-globalisation"),  # close: Twins add the impacts of globalisation
    (B2, "2-4-2-developed-emerging-and-developing-economies"): (E4, "4-3-1-measures-of-development"),  # loose, kept on approval: Shared: development indicators and HDI (one of four B sections). B-only: UK and BRIC growth, characteristics of the three kinds of economy, mean and median incomes
    (B2, "2-4-3-international-trade"): (E4, "4-1-2-specialisation-trade"),  # close: Comparative advantage is the shared core; the AQA page also spans protectionism, blocs and the WTO
    (B2, "2-4-4-exchange-rates"): (E4, "4-1-8-exchange-rates"),  # partial: Shared: changes and their impact. B-only: firms' view, reading exchange-rate data, effective exchange rates. Twin-only: fixed/managed systems, J-curve (on B 3.1.5)
    (B2, "2-5-1-the-economic-cycle"): (E2, "2-5-3-trade-cycle"),  # close: AQA page is mostly growth; the cycle is one section of six
    (B2, "2-5-2-circular-flow-of-income"): (E2, "2-4-1-national-income"),  # close: B adds the AD and AS factors
    (B2, "2-5-3-inflation"): (E2, "2-1-2-inflation"),  # close
    (B2, "2-5-4-employment-and-unemployment"): (E2, "2-1-3-employment-unemployment"),  # close
    (B2, "2-6-1-macroeconomic-objectives"): (E2, "2-6-1-possible-macroeconomic-objectives"),  # close: Twins list seven objectives; B four
    (B2, "2-6-2-policy-instruments"): (E2, "2-6-2-demand-side-policies"),  # partial: B overviews four instruments. Edexcel A's demand-side page covers two (fiscal, monetary). AQA spreads them over three pages, none more than a quarter, so no AQA twin
    (B2, "2-6-3-policy-conflicts-and-trade-offs"): (E2, "2-6-4-conflicts-between-objectives-and-policies"),  # close: B adds growth vs externalities, perspectives, unintended consequences
    (B3, "3-1-3-trading-blocs"): (E4, "4-1-5-trading-blocs-and-the-world-trade-organisation"),  # close: AQA: blocs are 2 of 12 sections on its trade page
    (B3, "3-1-4-trade-policy-and-trade-negotiations"): (E4, "4-1-6-restrictions-on-free-trade"),  # close: B adds G20/IMF/World Bank and bilateral deals. AQA: protectionism is 3 of 12 sections
    (B3, "3-1-5-exchange-rate-changes"): (E4, "4-1-8-exchange-rates"),  # close: Impacts, Marshall-Lerner and J-curve shared; AQA's currency-union sections match B's Eurozone
    (B3, "3-5-2-wage-rates"): (E3, "3-5-3-wage-determination"),  # partial: One less technical B page for three on Edexcel A and five on AQA. Every one of those points back here
    (B3, "3-6-1-poverty-and-inequality"): (E4, "4-2-2-inequality"),  # partial: B is one page for two on each board. Link goes to the inequality half (Lorenz, Gini); the poverty pages point back here
    (B3, "3-6-2-reducing-poverty"): (E4, "4-3-3-strategies-influencing-growth-development"),  # partial: Shared: aid and development strategies. B-only: NGOs as their own section
    (B4, "4-1-1-spectrum-of-competition"): (E3, "3-4-2-perfect-competition"),  # partial: Edexcel A has no spectrum page; perfect competition is 2 of B's 5 sections. AQA 1.5.1 is the spectrum page (212 words)
    (B4, "4-1-2-barriers-to-entry"): (E3, "3-4-7-contestability"),  # close
    (B4, "4-1-3-oligopoly"): (E3, "3-4-4-oligopoly"),  # close: B adds price discrimination; twins add collusive/non-collusive behaviour and game theory
    (B4, "4-1-4-business-objectives-and-pricing-decisions"): (E3, "3-3-1-revenue"),  # partial: Shared: AR, MR. B adds AC/MC calculation, the link to contribution, objectives and pricing
    (B4, "4-1-5-productive-and-allocative-efficiency"): (E3, "3-4-1-efficiency"),  # close: B adds productivity, market orientation, interacting markets
    (B4, "4-2-2-business-regulation"): (E3, "3-6-1-government-intervention"),  # close
    (B4, "4-2-3-arguments-for-and-against-regulation"): (E3, "3-6-2-the-impact-of-government-intervention"),  # close: AQA page is mostly ownership and privatisation; regulation and capture are 2 of 3 sections
    (B4, "4-3-1-market-failure-in-society"): (E1, "1-3-1-types-of-market-failure"),  # close: Overview pages on all three boards
    (B4, "4-3-2-externalities"): (E1, "1-3-2-externalities"),  # partial: B 4.3.2 (627 words) is shorter than B 1.5.1 and than either twin. The twins point back to 1.5.1, not here - see question 5
    (B4, "4-3-3-policies-to-deal-with-market-failure"): (E1, "1-4-1-government-intervention-in-markets"),  # close: Twins add maximum and minimum prices
    (B4, "4-4-1-the-ad-as-model"): (E2, "2-4-3-equilibrium-levels-of-real-national-output"),  # partial: One B page for five on Edexcel A; the link goes to the equilibrium page. AQA 2.2.2 is a single AD/AS page
    (B4, "4-4-2-demand-side-policies"): (E2, "2-6-2-demand-side-policies"),  # close: AQA splits fiscal (2.5.1) from monetary (2.4.3, which points to B 4.5.3)
    (B4, "4-4-3-supply-side-policies"): (E2, "2-6-3-supply-side-policies"),  # close
    (B4, "4-5-2-the-role-of-the-financial-sector"): (E4, "4-4-1-role-of-financial-markets"),  # close: AQA: the functions are one of six sections (money, money supply, bonds...)
    (B4, "4-5-3-the-role-of-the-central-bank"): (E4, "4-4-3-role-of-central-banks"),  # close
    (B4, "4-5-4-the-global-financial-crisis"): (E4, "4-4-2-market-failure-in-the-financial-sector"),  # partial: Shared: moral hazard, speculation, bubbles, regulation. B tells the 2007-08 story; twins are general
}

B_TO_AQA: dict[tuple[str, str], tuple[str, str]] = {
    (B1, "1-1-1-the-economic-problem"): (AMI, "1-1-4-scarcity-choice-and-the-allocation-of-resources"),  # close
    (B1, "1-1-2-business-objectives"): (AMI, "1-5-2-the-objectives-of-firms"),  # close: Twins state each objective as an MC/MR rule and add revenue maximisation; B describes them in words (the marginal conditions are B 4.1.4)
    (B1, "1-2-3-factors-of-production"): (AMI, "1-1-3-economic-resources"),  # close
    (B1, "1-2-4-specialisation"): (AMI, "1-4-2-specialisation-division-of-labour-and-exchange"),  # close: Twins add the functions of money; B splits pros and cons by employer, employee and firm
    (B1, "1-3-1-demand"): (AMI, "1-3-1-the-determinants-of-the-demand-for-goods-and-services"),  # close
    (B1, "1-3-2-supply"): (AMI, "1-3-3-the-determinants-of-the-supply-of-goods-and-services"),  # close
    (B1, "1-3-3-price-determination"): (AMI, "1-3-5-the-determination-of-equilibrium-market-prices"),  # close: B adds the limitations of the model
    (B1, "1-3-4-price-mechanism"): (AMI, "1-8-1-how-markets-and-prices-allocate-resources"),  # partial: Shared: the three functions. B-only: firm responses, mass and niche markets, market growth - about half the B page
    (B1, "1-4-1-role-of-banks-in-the-economy"): (AMA, "2-4-2-commercial-banks-and-investment-banks"),  # loose, kept on approval: AQA page goes far beyond B (balance sheets, bank objectives, credit creation); B is the borrower's view - collateral and why risk raises the rate. Shared: what banks do with savings and lending
    (B1, "1-5-1-market-failure-and-externalities"): (AMI, "1-8-4-positive-and-negative-externalities-in-consumption-and-production"),  # close: Twins add the intervention methods (B 1.5.2 / 4.3.3)
    (B1, "1-5-2-government-intervention-and-failure"): (AMI, "1-8-9-government-intervention-in-markets"),  # partial: One B page for two on each board. Link goes to the intervention half (4 of 6 B sections); the government-failure pages point back here instead
    (B2, "2-1-1-growth"): (AMI, "1-4-5-economies-and-diseconomies-of-scale"),  # partial: Shared: economies and diseconomies of scale. B adds market power, profitability, corporate culture; twins add LRAC theory
    (B2, "2-2-1-price-elasticity-of-demand"): (AMI, "1-3-2-price-income-and-cross-elasticities-of-demand"),  # partial: Twin covers PED, YED and XED on one page; B has no XED and puts YED on 2.2.4
    (B2, "2-2-4-income-elasticity-of-demand"): (AMI, "1-3-2-price-income-and-cross-elasticities-of-demand"),  # partial: YED is one of four sections on the twin. Both B elasticity pages point at the same twin
    (B2, "2-3-1-productivity"): (AMI, "1-4-1-production-and-productivity"),  # partial: Same topic, but the AQA page is a 181-word definition; B adds competitiveness, wages, growth, labour/capital intensity
    (B2, "2-4-1-globalisation"): (AMA, "2-6-1-globalisation"),  # close: Twins add the impacts of globalisation
    (B2, "2-4-2-developed-emerging-and-developing-economies"): (AMA, "2-6-5-economic-growth-and-development"),  # loose, kept on approval: Shared: development indicators and HDI (one of four B sections). B-only: UK and BRIC growth, characteristics of the three kinds of economy, mean and median incomes
    (B2, "2-4-3-international-trade"): (AMA, "2-6-2-trade"),  # close: Comparative advantage is the shared core; the AQA page also spans protectionism, blocs and the WTO
    (B2, "2-4-4-exchange-rates"): (AMA, "2-6-4-exchange-rate-systems"),  # partial: Shared: changes and their impact. B-only: firms' view, reading exchange-rate data, effective exchange rates. Twin-only: fixed/managed systems, J-curve (on B 3.1.5)
    (B2, "2-5-1-the-economic-cycle"): (AMA, "2-3-1-economic-growth-and-the-economic-cycle"),  # partial: AQA page is mostly growth; the cycle is one section of six
    (B2, "2-5-2-circular-flow-of-income"): (AMA, "2-2-1-the-circular-flow-of-income"),  # close: B adds the AD and AS factors
    (B2, "2-5-3-inflation"): (AMA, "2-3-3-inflation-and-deflation"),  # close
    (B2, "2-5-4-employment-and-unemployment"): (AMA, "2-3-2-employment-and-unemployment"),  # close
    (B2, "2-6-1-macroeconomic-objectives"): (AMA, "2-1-1-the-objectives-of-government-economic-policy"),  # close: Twins list seven objectives; B four
    (B2, "2-6-3-policy-conflicts-and-trade-offs"): (AMA, "2-3-4-possible-conflicts-between-macroeconomic-policy-objectives"),  # close: B adds growth vs externalities, perspectives, unintended consequences
    (B3, "3-1-3-trading-blocs"): (AMA, "2-6-2-trade"),  # partial: AQA: blocs are 2 of 12 sections on its trade page
    (B3, "3-1-4-trade-policy-and-trade-negotiations"): (AMA, "2-6-2-trade"),  # partial: B adds G20/IMF/World Bank and bilateral deals. AQA: protectionism is 3 of 12 sections
    (B3, "3-1-5-exchange-rate-changes"): (AMA, "2-6-4-exchange-rate-systems"),  # close: Impacts, Marshall-Lerner and J-curve shared; AQA's currency-union sections match B's Eurozone
    (B3, "3-5-2-wage-rates"): (AMI, "1-6-3-wage-determination-perfectly-competitive-labour-markets"),  # partial: One less technical B page for three on Edexcel A and five on AQA. Every one of those points back here
    (B3, "3-5-3-minimum-wage-legislation"): (AMI, "1-6-6-the-national-minimum-wage"),  # close: AQA page is 296 words; B adds developing countries, skill shortages, migration, incentives
    (B3, "3-6-1-poverty-and-inequality"): (AMI, "1-7-1-the-distribution-of-income-and-wealth"),  # partial: B is one page for two on each board. Link goes to the inequality half (Lorenz, Gini); the poverty pages point back here
    (B3, "3-6-2-reducing-poverty"): (AMA, "2-6-5-economic-growth-and-development"),  # partial: Shared: aid and development strategies. B-only: NGOs as their own section
    (B3, "3-6-4-redistribution-of-income-and-wealth"): (AMI, "1-7-3-government-policies-poverty-income-distribution"),  # partial: B adds income vs wealth and the poverty trap
    (B4, "4-1-1-spectrum-of-competition"): (AMI, "1-5-1-market-structures"),  # close: Edexcel A has no spectrum page; perfect competition is 2 of B's 5 sections. AQA 1.5.1 is the spectrum page (212 words)
    (B4, "4-1-2-barriers-to-entry"): (AMI, "1-5-9-contestable-and-non-contestable-markets"),  # close
    (B4, "4-1-3-oligopoly"): (AMI, "1-5-5-oligopoly"),  # close: B adds price discrimination; twins add collusive/non-collusive behaviour and game theory
    (B4, "4-1-4-business-objectives-and-pricing-decisions"): (AMI, "1-4-6-marginal-average-and-total-revenue"),  # partial: Shared: AR, MR. B adds AC/MC calculation, the link to contribution, objectives and pricing
    (B4, "4-1-5-productive-and-allocative-efficiency"): (AMI, "1-5-10-market-structure-efficiency-resource-allocation"),  # close: B adds productivity, market orientation, interacting markets
    (B4, "4-2-2-business-regulation"): (AMI, "1-8-7-competition-policy"),  # close
    (B4, "4-2-3-arguments-for-and-against-regulation"): (AMI, "1-8-8-public-ownership-privatisation-regulation-and-deregulation-of-markets"),  # partial: AQA page is mostly ownership and privatisation; regulation and capture are 2 of 3 sections
    (B4, "4-3-1-market-failure-in-society"): (AMI, "1-8-2-the-meaning-of-market-failure"),  # close: Overview pages on all three boards
    (B4, "4-3-2-externalities"): (AMI, "1-8-4-positive-and-negative-externalities-in-consumption-and-production"),  # partial: B 4.3.2 (627 words) is shorter than B 1.5.1 and than either twin. The twins point back to 1.5.1, not here - see question 5
    (B4, "4-3-3-policies-to-deal-with-market-failure"): (AMI, "1-8-9-government-intervention-in-markets"),  # close: Twins add maximum and minimum prices
    (B4, "4-4-1-the-ad-as-model"): (AMA, "2-2-2-aggregate-demand-and-aggregate-supply-analysis"),  # close: One B page for five on Edexcel A; the link goes to the equilibrium page. AQA 2.2.2 is a single AD/AS page
    (B4, "4-4-2-demand-side-policies"): (AMA, "2-5-1-fiscal-policy"),  # partial: AQA splits fiscal (2.5.1) from monetary (2.4.3, which points to B 4.5.3)
    (B4, "4-4-3-supply-side-policies"): (AMA, "2-5-2-supply-side-policies"),  # close
    (B4, "4-5-2-the-role-of-the-financial-sector"): (AMA, "2-4-1-the-structure-of-financial-markets-and-financial-assets"),  # partial: AQA: the functions are one of six sections (money, money supply, bonds...)
    (B4, "4-5-3-the-role-of-the-central-bank"): (AMA, "2-4-3-central-banks-and-monetary-policy"),  # close
    (B4, "4-5-4-the-global-financial-crisis"): (AMA, "2-4-4-the-regulation-of-the-financial-system"),  # partial: Shared: moral hazard, speculation, bubbles, regulation. B tells the 2007-08 story; twins are general
}

TO_B: dict[tuple[str, str], tuple[str, str]] = {
    # ---- Edexcel A -> Edexcel B ----------------------------------------
    (E1, "1-1-3-the-economic-problem"): (B1, "1-1-1-the-economic-problem"),  # close
    (E1, "1-1-5-specialisation-division-of-labour"): (B1, "1-2-4-specialisation"),  # close
    (E1, "1-2-2-demand"): (B1, "1-3-1-demand"),  # close
    (E1, "1-2-3-price-income-cross-elasticities-of-demand"): (B2, "2-2-1-price-elasticity-of-demand"),  # partial: PED is the largest part; YED is on B 2.2.4
    (E1, "1-2-4-supply"): (B1, "1-3-2-supply"),  # close
    (E1, "1-2-6-price-determination"): (B1, "1-3-3-price-determination"),  # close
    (E1, "1-2-7-price-mechanism"): (B1, "1-3-4-price-mechanism"),  # close
    (E1, "1-2-9-indirect-taxes-subsidies"): (B1, "1-5-2-government-intervention-and-failure"),  # partial: Not in the maps. B 1.5.2's tax and subsidy sections carry the same incidence diagrams
    (E1, "1-3-1-types-of-market-failure"): (B4, "4-3-1-market-failure-in-society"),  # close
    (E1, "1-3-2-externalities"): (B1, "1-5-1-market-failure-and-externalities"),  # close: 1.5.1, not 4.3.2: as built 1.5.1 is the fuller page (all four externality diagrams)
    (E1, "1-3-3-public-goods"): (B4, "4-3-1-market-failure-in-society"),  # partial: B covers public goods as one section of its overview
    (E1, "1-3-4-information-gaps"): (B4, "4-3-1-market-failure-in-society"),  # partial: B covers information as one section of its overview
    (E1, "1-4-1-government-intervention-in-markets"): (B4, "4-3-3-policies-to-deal-with-market-failure"),  # close: 4.3.3 has permits, provision and information, as A 1.4.1 does; 1.5.2 does not
    (E1, "1-4-2-government-failure"): (B1, "1-5-2-government-intervention-and-failure"),  # partial: B's only government-failure coverage; causes list matches
    (E2, "2-1-2-inflation"): (B2, "2-5-3-inflation"),  # close
    (E2, "2-1-3-employment-unemployment"): (B2, "2-5-4-employment-and-unemployment"),  # close
    (E2, "2-2-1-aggregate-demand"): (B4, "4-4-1-the-ad-as-model"),  # partial
    (E2, "2-3-1-aggregate-supply"): (B4, "4-4-1-the-ad-as-model"),  # partial
    (E2, "2-3-2-short-run-aggregate-supply"): (B4, "4-4-1-the-ad-as-model"),  # partial
    (E2, "2-3-3-long-run-aggregate-supply"): (B4, "4-4-1-the-ad-as-model"),  # partial
    (E2, "2-4-1-national-income"): (B2, "2-5-2-circular-flow-of-income"),  # close
    (E2, "2-4-2-injections-withdrawals"): (B2, "2-5-2-circular-flow-of-income"),  # close
    (E2, "2-4-3-equilibrium-levels-of-real-national-output"): (B4, "4-4-1-the-ad-as-model"),  # close
    (E2, "2-4-4-the-multiplier"): (B4, "4-4-1-the-ad-as-model"),  # partial: Multiplier is one section of B 4.4.1
    (E2, "2-5-3-trade-cycle"): (B2, "2-5-1-the-economic-cycle"),  # close
    (E2, "2-6-1-possible-macroeconomic-objectives"): (B2, "2-6-1-macroeconomic-objectives"),  # close
    (E2, "2-6-2-demand-side-policies"): (B4, "4-4-2-demand-side-policies"),  # close: 4.4.2 rather than 2.6.2 (the overview)
    (E2, "2-6-3-supply-side-policies"): (B4, "4-4-3-supply-side-policies"),  # close: 4.4.3 rather than 2.6.2
    (E2, "2-6-4-conflicts-between-objectives-and-policies"): (B2, "2-6-3-policy-conflicts-and-trade-offs"),  # close
    (E3, "3-1-2-business-growth"): (B2, "2-1-2-methods-of-growth"),  # close
    (E3, "3-2-1-business-objectives"): (B1, "1-1-2-business-objectives"),  # close
    (E3, "3-3-1-revenue"): (B4, "4-1-4-business-objectives-and-pricing-decisions"),  # partial
    (E3, "3-3-3-economies-diseconomies-of-scale"): (B2, "2-1-1-growth"),  # partial: 2.1.1 rather than 4.1.2, whose scale section is shorter
    (E3, "3-4-1-efficiency"): (B4, "4-1-5-productive-and-allocative-efficiency"),  # close
    (E3, "3-4-2-perfect-competition"): (B4, "4-1-1-spectrum-of-competition"),  # partial
    (E3, "3-4-4-oligopoly"): (B4, "4-1-3-oligopoly"),  # close
    (E3, "3-4-6-monopsony"): (B4, "4-2-1-market-power-and-market-failure"),  # partial: one way only: B's sole monopsony coverage, but 1 of 7 B sections, so B does not link back
    (E3, "3-4-7-contestability"): (B4, "4-1-2-barriers-to-entry"),  # close
    (E3, "3-5-1-demand-for-labour"): (B3, "3-5-2-wage-rates"),  # partial: MRP theory is optional on B
    (E3, "3-5-2-supply-of-labour"): (B3, "3-5-2-wage-rates"),  # partial
    (E3, "3-5-3-wage-determination"): (B3, "3-5-2-wage-rates"),  # partial
    (E3, "3-6-1-government-intervention"): (B4, "4-2-2-business-regulation"),  # close
    (E3, "3-6-2-the-impact-of-government-intervention"): (B4, "4-2-3-arguments-for-and-against-regulation"),  # close
    (E4, "4-1-1-globalisation"): (B2, "2-4-1-globalisation"),  # close
    (E4, "4-1-2-specialisation-trade"): (B2, "2-4-3-international-trade"),  # close
    (E4, "4-1-5-trading-blocs-and-the-world-trade-organisation"): (B3, "3-1-3-trading-blocs"),  # close
    (E4, "4-1-6-restrictions-on-free-trade"): (B3, "3-1-4-trade-policy-and-trade-negotiations"),  # close
    (E4, "4-1-8-exchange-rates"): (B3, "3-1-5-exchange-rate-changes"),  # close: 3.1.5, not 2.4.4: shares the macro impacts and Marshall-Lerner/J-curve
    (E4, "4-2-1-absolute-relative-poverty"): (B3, "3-6-1-poverty-and-inequality"),  # close
    (E4, "4-2-2-inequality"): (B3, "3-6-1-poverty-and-inequality"),  # close
    (E4, "4-3-1-measures-of-development"): (B2, "2-4-2-developed-emerging-and-developing-economies"),  # loose, kept on approval: shared: development indicators and HDI only
    (E4, "4-3-3-strategies-influencing-growth-development"): (B3, "3-6-2-reducing-poverty"),  # partial
    (E4, "4-4-1-role-of-financial-markets"): (B4, "4-5-2-the-role-of-the-financial-sector"),  # close
    (E4, "4-4-2-market-failure-in-the-financial-sector"): (B4, "4-5-4-the-global-financial-crisis"),  # partial
    (E4, "4-4-3-role-of-central-banks"): (B4, "4-5-3-the-role-of-the-central-bank"),  # close
    # ---- AQA -> Edexcel B ----------------------------------------
    (AMI, "1-1-3-economic-resources"): (B1, "1-2-3-factors-of-production"),  # close
    (AMI, "1-1-4-scarcity-choice-and-the-allocation-of-resources"): (B1, "1-1-1-the-economic-problem"),  # close
    (AMI, "1-2-2-imperfect-information"): (B4, "4-3-1-market-failure-in-society"),  # partial
    (AMI, "1-3-1-the-determinants-of-the-demand-for-goods-and-services"): (B1, "1-3-1-demand"),  # close
    (AMI, "1-3-2-price-income-and-cross-elasticities-of-demand"): (B2, "2-2-1-price-elasticity-of-demand"),  # partial
    (AMI, "1-3-3-the-determinants-of-the-supply-of-goods-and-services"): (B1, "1-3-2-supply"),  # close
    (AMI, "1-3-5-the-determination-of-equilibrium-market-prices"): (B1, "1-3-3-price-determination"),  # close
    (AMI, "1-4-1-production-and-productivity"): (B2, "2-3-1-productivity"),  # partial
    (AMI, "1-4-2-specialisation-division-of-labour-and-exchange"): (B1, "1-2-4-specialisation"),  # close
    (AMI, "1-4-5-economies-and-diseconomies-of-scale"): (B2, "2-1-1-growth"),  # partial
    (AMI, "1-4-6-marginal-average-and-total-revenue"): (B4, "4-1-4-business-objectives-and-pricing-decisions"),  # partial
    (AMI, "1-5-1-market-structures"): (B4, "4-1-1-spectrum-of-competition"),  # close
    (AMI, "1-5-2-the-objectives-of-firms"): (B1, "1-1-2-business-objectives"),  # close
    (AMI, "1-5-3-perfect-competition"): (B4, "4-1-1-spectrum-of-competition"),  # partial
    (AMI, "1-5-5-oligopoly"): (B4, "4-1-3-oligopoly"),  # close
    (AMI, "1-5-7-price-discrimination"): (B4, "4-1-3-oligopoly"),  # partial: B puts price discrimination under oligopoly
    (AMI, "1-5-9-contestable-and-non-contestable-markets"): (B4, "4-1-2-barriers-to-entry"),  # close
    (AMI, "1-5-10-market-structure-efficiency-resource-allocation"): (B4, "4-1-5-productive-and-allocative-efficiency"),  # close
    (AMI, "1-6-1-the-demand-for-labour-marginal-productivity-theory"): (B3, "3-5-2-wage-rates"),  # partial
    (AMI, "1-6-2-influence-upon-the-supply-of-labour-to-different-markets"): (B3, "3-5-2-wage-rates"),  # partial
    (AMI, "1-6-3-wage-determination-perfectly-competitive-labour-markets"): (B3, "3-5-2-wage-rates"),  # partial
    (AMI, "1-6-4-wage-determination-imperfectly-competitive-labour-markets"): (B4, "4-2-1-market-power-and-market-failure"),  # partial: one way only: B's sole monopsony coverage, but 1 of 7 B sections, so B does not link back
    (AMI, "1-6-5-the-influence-of-trade-unions-in-determining-wages-and-levels-of-employment"): (B3, "3-5-2-wage-rates"),  # partial
    (AMI, "1-6-6-the-national-minimum-wage"): (B3, "3-5-3-minimum-wage-legislation"),  # close
    (AMI, "1-7-1-the-distribution-of-income-and-wealth"): (B3, "3-6-1-poverty-and-inequality"),  # close
    (AMI, "1-7-2-the-problem-of-poverty"): (B3, "3-6-1-poverty-and-inequality"),  # partial: 3.6.1 rather than 3.6.4, which has the poverty trap only
    (AMI, "1-7-3-government-policies-poverty-income-distribution"): (B3, "3-6-4-redistribution-of-income-and-wealth"),  # partial
    (AMI, "1-8-1-how-markets-and-prices-allocate-resources"): (B1, "1-3-4-price-mechanism"),  # close
    (AMI, "1-8-2-the-meaning-of-market-failure"): (B4, "4-3-1-market-failure-in-society"),  # close
    (AMI, "1-8-3-public-goods-private-goods-and-quasi-public-goods"): (B4, "4-3-1-market-failure-in-society"),  # partial
    (AMI, "1-8-4-positive-and-negative-externalities-in-consumption-and-production"): (B1, "1-5-1-market-failure-and-externalities"),  # close: 1.5.1, not 4.3.2: as built 1.5.1 is the fuller page
    (AMI, "1-8-5-merit-and-demerit-goods"): (B4, "4-3-1-market-failure-in-society"),  # partial
    (AMI, "1-8-6-market-imperfections"): (B4, "4-3-1-market-failure-in-society"),  # close: Information, monopoly power and factor immobility all on 4.3.1
    (AMI, "1-8-7-competition-policy"): (B4, "4-2-2-business-regulation"),  # close
    (AMI, "1-8-8-public-ownership-privatisation-regulation-and-deregulation-of-markets"): (B4, "4-2-2-business-regulation"),  # partial: 4.2.2 has privatisation and natural-monopoly regulation; capture is on 4.2.3
    (AMI, "1-8-9-government-intervention-in-markets"): (B4, "4-3-3-policies-to-deal-with-market-failure"),  # close
    (AMI, "1-8-10-government-failure"): (B1, "1-5-2-government-intervention-and-failure"),  # partial
    (AMA, "2-1-1-the-objectives-of-government-economic-policy"): (B2, "2-6-1-macroeconomic-objectives"),  # close
    (AMA, "2-1-3-uses-of-index-numbers"): (B2, "2-5-3-inflation"),  # partial: CPI and index numbers; 3.1.1's index section is the alternative
    (AMA, "2-2-1-the-circular-flow-of-income"): (B2, "2-5-2-circular-flow-of-income"),  # close
    (AMA, "2-2-2-aggregate-demand-and-aggregate-supply-analysis"): (B4, "4-4-1-the-ad-as-model"),  # close
    (AMA, "2-2-3-the-determinants-of-aggregate-demand"): (B2, "2-5-2-circular-flow-of-income"),  # partial: B 2.5.2 has the C+I+G+(X-M) factors table
    (AMA, "2-2-4-aggregate-demand-and-the-level-of-economic-activity"): (B4, "4-4-1-the-ad-as-model"),  # partial
    (AMA, "2-2-5-determinants-of-short-run-aggregate-supply"): (B4, "4-4-1-the-ad-as-model"),  # partial
    (AMA, "2-2-6-determinants-of-long-run-aggregate-supply"): (B4, "4-4-1-the-ad-as-model"),  # partial
    (AMA, "2-3-1-economic-growth-and-the-economic-cycle"): (B2, "2-5-1-the-economic-cycle"),  # partial
    (AMA, "2-3-2-employment-and-unemployment"): (B2, "2-5-4-employment-and-unemployment"),  # close
    (AMA, "2-3-3-inflation-and-deflation"): (B2, "2-5-3-inflation"),  # close
    (AMA, "2-3-4-possible-conflicts-between-macroeconomic-policy-objectives"): (B2, "2-6-3-policy-conflicts-and-trade-offs"),  # close
    (AMA, "2-4-1-the-structure-of-financial-markets-and-financial-assets"): (B4, "4-5-2-the-role-of-the-financial-sector"),  # partial
    (AMA, "2-4-2-commercial-banks-and-investment-banks"): (B1, "1-4-1-role-of-banks-in-the-economy"),  # loose, kept on approval: shared: what banks do with savings and lending; AQA goes much further
    (AMA, "2-4-3-central-banks-and-monetary-policy"): (B4, "4-5-3-the-role-of-the-central-bank"),  # close: 4.5.3 rather than 4.4.2
    (AMA, "2-4-4-the-regulation-of-the-financial-system"): (B4, "4-5-3-the-role-of-the-central-bank"),  # partial: 4.5.3 (BoE, FPC) rather than 4.5.4 (the crisis story); close either way
    (AMA, "2-5-1-fiscal-policy"): (B4, "4-4-2-demand-side-policies"),  # partial
    (AMA, "2-5-2-supply-side-policies"): (B4, "4-4-3-supply-side-policies"),  # close
    (AMA, "2-6-1-globalisation"): (B2, "2-4-1-globalisation"),  # close
    (AMA, "2-6-2-trade"): (B2, "2-4-3-international-trade"),  # partial: Comparative advantage leads the AQA page; blocs and protectionism are on B 3.1.3/3.1.4
    (AMA, "2-6-4-exchange-rate-systems"): (B3, "3-1-5-exchange-rate-changes"),  # close: 3.1.5, not 2.4.4: shares the impacts, J-curve and currency unions (Eurozone)
    (AMA, "2-6-5-economic-growth-and-development"): (B2, "2-4-2-developed-emerging-and-developing-economies"),  # loose, kept on approval: shared: indicators and HDI; 3.6.2 (aid) was the alternative
}

TABLES: tuple[tuple[str, str, dict[tuple[str, str], tuple[str, str]]], ...] = (
    # (name, the boundary it may cross, as "from>to" over board_of_dir keys)
    ("TWINS", "edexcel>aqa|aqa>edexcel", TWINS),
    ("B_TO_A", "edexcel-b>edexcel", B_TO_A),
    ("B_TO_AQA", "edexcel-b>aqa", B_TO_AQA),
    ("TO_B", "edexcel>edexcel-b|aqa>edexcel-b", TO_B),
)

# Every declared (source, target) pair, for verify_seo assertion 13.
PAIRS: frozenset[tuple[tuple[str, str], tuple[str, str]]] = frozenset(
    (k, v) for _, _, t in TABLES for k, v in t.items())


def board_of_dir(notes_dir: str) -> str:
    """The board key of a notes directory. Edexcel B is its own board: before
    2026-11-24 this returned "edexcel" for every non-AQA directory, so a B page
    and an Edexcel A page read as the same board."""
    if notes_dir.startswith("aqa"):
        return "aqa"
    if notes_dir.startswith("edexcel-b-"):
        return "edexcel-b"
    return "edexcel"


def twins(notes_dir: str, slug: str) -> list[tuple[str, str]]:
    """This topic's twins, at most one per other board, in BOARD_ORDER."""
    key = (notes_dir, slug)
    found = [t[key] for _, _, t in TABLES if key in t]
    return sorted(found, key=lambda d: BOARD_ORDER.index(board_of_dir(d[0])))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--unpaired", action="store_true")
    args = ap.parse_args(argv)

    root = __import__("pathlib").Path(__file__).resolve().parent.parent
    all_topics = {(p.parent.name, p.stem)
                  for p in (root / "notes-data" / "topics").glob("*/*.json")}
    bad, wrong = [], []
    for name, allowed, table in TABLES:
        ok = set(allowed.split("|"))
        for k, v in table.items():
            if k not in all_topics or v not in all_topics:
                bad.append(f"{name}: {k} -> {v}")
            if f"{board_of_dir(k[0])}>{board_of_dir(v[0])}" not in ok:
                wrong.append(f"{name}: {k} -> {v}")
    if bad:
        print("pages that do not exist:")
        for b in bad:
            print(f"  {b}")
    if wrong:
        print("pairs that cross the wrong boundary (or none):")
        for w in wrong:
            print(f"  {w}")

    paired = {k for _, _, t in TABLES for k in t}
    if args.unpaired:
        for key in sorted(all_topics - paired):
            print(f"  no twin: {key[0]}/{key[1]}")
    else:
        for key in sorted(paired):
            for v in twins(*key):
                print(f"  {key[0]}/{key[1]}  ->  {v[0]}/{v[1]}")
    print(f"\n{len(PAIRS)} directed pairs over {len(all_topics)} topic pages; "
          f"{len(all_topics) - len(paired)} pages have no twin")
    return 1 if bad or wrong else 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
