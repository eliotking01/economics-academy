#!/usr/bin/env python3
"""Which page on the other board covers the same topic, and its neighbours.

    python3 scripts/notes_twins.py              # print the whole map
    python3 scripts/notes_twins.py --unpaired   # topics with no twin, and why

Imported by build_notes_pages.py, which renders the block, and by
seo/tools/verify_seo.py, which asserts every pair resolves and crosses the
board boundary in exactly one declared place. One definition, two consumers -
the same arrangement as notes_sequence.py.

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
over 5-word shingles, the measure seo/07-link-graph.md and DO-NOT-BREAK use,
computed by seo/tools/twin_evidence.py. Rows were seeded by taking the
mutual best match on that measure and then read one by one; the ones changed
or added by hand say so.

WHAT IS DELIBERATELY LEFT OUT
-----------------------------
A pairing that is merely the nearest available page is worse than no pairing.
The two boards genuinely split some topics differently - Edexcel's
"Demand-Side Policies" is monetary AND fiscal, which AQA separates into 2.4.3
and 2.5.1 - and 61 topics have no counterpart worth linking. `--unpaired`
lists them with the best score found, so a future session can see what was
considered rather than repeating the search.

THE MAP IS DIRECTED, NOT A BIJECTION
------------------------------------
Two Edexcel pages can legitimately point at one AQA page: Edexcel splits
economic methodology across 1.1.1 and 1.1.2 and AQA does not. Each direction
is stated separately so neither has to be inferred.

Standard library only.
"""

from __future__ import annotations

import argparse
import sys

E1, E2, E3, E4 = ("edexcel-theme-1", "edexcel-theme-2",
                  "edexcel-theme-3", "edexcel-theme-4")
AMI, AMA = "aqa-a2-micro", "aqa-a2-macro"

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


def twin(notes_dir: str, slug: str) -> tuple[str, str] | None:
    return TWINS.get((notes_dir, slug))


def board_of_dir(notes_dir: str) -> str:
    return "aqa" if notes_dir.startswith("aqa") else "edexcel"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--unpaired", action="store_true")
    args = ap.parse_args(argv)

    root = __import__("pathlib").Path(__file__).resolve().parent.parent
    all_topics = {(p.parent.name, p.stem)
                  for p in (root / "notes-data" / "topics").glob("*/*.json")}
    bad = [f"{k} -> {v}" for k, v in TWINS.items() if v not in all_topics]
    same = [f"{k} -> {v}" for k, v in TWINS.items()
            if board_of_dir(k[0]) == board_of_dir(v[0])]
    if bad:
        print("targets that do not exist:")
        for b in bad:
            print(f"  {b}")
    if same:
        print("pairs that do not cross a board:")
        for s in same:
            print(f"  {s}")

    if args.unpaired:
        for key in sorted(all_topics - set(TWINS)):
            print(f"  no twin: {key[0]}/{key[1]}")
    else:
        for k, v in TWINS.items():
            print(f"  {k[0]}/{k[1]}  ->  {v[0]}/{v[1]}")
    print(f"\n{len(TWINS)} directed pairs over {len(all_topics)} topic pages; "
          f"{len(all_topics) - len(TWINS)} pages have no twin")
    return 1 if bad or same else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
