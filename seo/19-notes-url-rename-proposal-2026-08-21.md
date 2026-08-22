# Revision notes: the URL rename, costed

21 August 2026. Every in-scope page with the URL it would have under the
better structure, and one line on what the rename would gain. **Nothing here
has been changed and nothing here should be.**

Mechanics, and why the URLs are frozen:
`seo/16-url-structure-and-redirect-options.md`. Read it before deciding
anything from this document.

---

## The honest summary: do not do this set

**Not now, and probably not this academic year.** Four reasons, in order of
weight.

**1. GitHub Pages cannot issue a 301.** Not a `.htaccess`, not a `_redirects`,
no server configuration of any kind. Move a file Google has indexed and that
URL 404s forever. Renaming these 176 pages without redirects in place first is
not a risky change, it is a destructive one.

**2. You are mid-way through an indexing recovery, and this section is the
worst part of it.** 59 of the 176 in-scope pages are indexed — 33.5%, against
66.5% site-wide. Renaming a URL resets whatever crawl history it has. Doing
that to a set that is only a third indexed is spending the recovery you have
already paid for.

**3. The gain is small and Google says so.** Exact-match keywords in URLs are a
weak ranking factor. The evidence is on the SERPs themselves: Save My Exams
ranks first for "government failure economics a level" with the topic name
buried seven segments deep. Titles, content and links decide these results —
which is why this audit spent its effort on titles, content and links.

**4. The titles have not had their run yet.** Every one of these 166 pages got
a new title today. Renaming the URLs in the same window makes it impossible to
tell which change moved anything. Give the titles a term.

### When it would be worth revisiting

All four of these must be true, and the third is the one to watch:

1. Real 301s are in place and tested — Cloudflare in front of GitHub Pages is
   the option `seo/16-` recommends, and it changes nothing about how you work.
2. Search Console shows the current URLs are indexed, so a recovery can be
   measured rather than guessed at.
3. You are not mid-way through another indexing recovery. **On 21 August 2026
   you are.**
4. You have a fortnight where a temporary dip does not matter. Term starts in
   early September; a dip then costs the autumn.

**Revisit in the spring**, after a full term of data on the new titles.

### What is actually wrong with the current URLs

Little, and it is worth being precise since this document is 176 rows of
proposed change:

- **`.html` is dated but carries no ranking penalty.** Cosmetic.
- **`edexcel-theme-1` does not say "a-level economics".** A student reading the
  URL in a search result gets less confirmation than
  `savemyexams.com/a-level/economics/edexcel/…` gives them.
- **The `1-2-1-` prefix pushes the meaningful words two segments right.** Words
  earlier in a URL carry slightly more weight, and "slightly" is doing real
  work in that sentence.

What is right about them: the topic name is in the slug, the board is in the
path, they are lowercase, hyphenated, shallow and stable. That is most of what
a URL can do.

### The cheaper halfway house

If you ever migrate, `seo/16-` §2 offers a smaller diff with most of the
benefit — same directories, code dropped from the leaf:

```
/revision-notes/edexcel-theme-1/rational-decision-making/
```

The table below gives the **full** structure rather than the halfway one,
because a costed option should be the whole cost. Halve every row's change and
you have the cheaper version.

### And do not start new pages at the new structure

The tempting move is to leave these 176 alone and build new topic pages the
better way, since that one is free. Don't. You would end up with two
conventions in one folder and a generator that has to know which page is which.
On a site this size the consistency is worth more than the marginal URL
quality. `seo/16-` §5.

---

## The full list

176 rows: `revision-notes/index.html`, the seven hubs, the two diagram
galleries and all 166 topic pages. Generated from
`seo/17-notes-after-2026-08-21.csv`, so it cannot disagree with the tree.

| Current URL | Proposed URL | What the rename would gain |
| --- | --- | --- |
| `/revision-notes/index.html` | `/revision-notes/` | nothing — already the canonical directory form |
| `/revision-notes/aqa-a2-macro/` | `/revision-notes/aqa-a-level-economics/macroeconomics/` | adds "a-level-economics" to the path a student reads in the SERP |
| `/revision-notes/aqa-a2-micro/` | `/revision-notes/aqa-a-level-economics/microeconomics/` | adds "a-level-economics" to the path a student reads in the SERP |
| `/revision-notes/edexcel-theme-1/` | `/revision-notes/edexcel-a-level-economics/theme-1/` | adds "a-level-economics" to the path a student reads in the SERP |
| `/revision-notes/edexcel-theme-2/` | `/revision-notes/edexcel-a-level-economics/theme-2/` | adds "a-level-economics" to the path a student reads in the SERP |
| `/revision-notes/edexcel-theme-3/` | `/revision-notes/edexcel-a-level-economics/theme-3/` | adds "a-level-economics" to the path a student reads in the SERP |
| `/revision-notes/edexcel-theme-4/` | `/revision-notes/edexcel-a-level-economics/theme-4/` | adds "a-level-economics" to the path a student reads in the SERP |
| `/revision-notes/macro-application/` | unchanged | nothing — already the canonical directory form |
| `/revision-notes/aqa-a2-macro/2-1-1-the-objectives-of-government-economic-policy.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/the-objectives-of-government-economic-policy/` | moves `2-1-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-1-2-macroeconomic-indicators.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/macroeconomic-indicators/` | moves `2-1-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-1-3-uses-of-index-numbers.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/uses-of-index-numbers/` | moves `2-1-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-1-4-uses-of-national-income-data.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/uses-of-national-income-data/` | moves `2-1-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-2-1-the-circular-flow-of-income.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/the-circular-flow-of-income/` | moves `2-2-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-2-2-aggregate-demand-and-aggregate-supply-analysis.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/aggregate-demand-and-aggregate-supply-analysis/` | moves `2-2-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-2-3-the-determinants-of-aggregate-demand.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/the-determinants-of-aggregate-demand/` | moves `2-2-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/aggregate-demand-and-the-level-of-economic-activity/` | moves `2-2-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-2-5-determinants-of-short-run-aggregate-supply.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/determinants-of-short-run-aggregate-supply/` | moves `2-2-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-2-6-determinants-of-long-run-aggregate-supply.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/determinants-of-long-run-aggregate-supply/` | moves `2-2-6` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-3-1-economic-growth-and-the-economic-cycle.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/economic-growth-and-the-economic-cycle/` | moves `2-3-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-3-2-employment-and-unemployment.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/employment-and-unemployment/` | moves `2-3-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-3-3-inflation-and-deflation.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/inflation-and-deflation/` | moves `2-3-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-3-4-possible-conflicts-between-macroeconomic-policy-objectives.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/possible-conflicts-between-macroeconomic-policy-objectives/` | moves `2-3-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-4-1-the-structure-of-financial-markets-and-financial-assets.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/the-structure-of-financial-markets-and-financial-assets/` | moves `2-4-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-4-2-commercial-banks-and-investment-banks.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/commercial-banks-and-investment-banks/` | moves `2-4-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-4-3-central-banks-and-monetary-policy.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/central-banks-and-monetary-policy/` | moves `2-4-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-4-4-the-regulation-of-the-financial-system.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/the-regulation-of-the-financial-system/` | moves `2-4-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-5-1-fiscal-policy.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/fiscal-policy/` | moves `2-5-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-5-2-supply-side-policies.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/supply-side-policies/` | moves `2-5-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-6-1-globalisation.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/globalisation/` | moves `2-6-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-6-2-trade.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/trade/` | moves `2-6-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-6-3-the-balance-of-payments.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/the-balance-of-payments/` | moves `2-6-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-6-4-exchange-rate-systems.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/exchange-rate-systems/` | moves `2-6-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-macro/2-6-5-economic-growth-and-development.html` | `/revision-notes/aqa-a-level-economics/macroeconomics/economic-growth-and-development/` | moves `2-6-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-1-1-economic-methodology.html` | `/revision-notes/aqa-a-level-economics/microeconomics/economic-methodology/` | moves `1-1-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-nature-and-purpose-of-economic-activity/` | moves `1-1-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-1-3-economic-resources.html` | `/revision-notes/aqa-a-level-economics/microeconomics/economic-resources/` | moves `1-1-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-1-4-scarcity-choice-and-the-allocation-of-resources.html` | `/revision-notes/aqa-a-level-economics/microeconomics/scarcity-choice-and-the-allocation-of-resources/` | moves `1-1-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-1-5-production-possibility-diagrams.html` | `/revision-notes/aqa-a-level-economics/microeconomics/production-possibility-diagrams/` | moves `1-1-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-2-1-consumer-behaviour.html` | `/revision-notes/aqa-a-level-economics/microeconomics/consumer-behaviour/` | moves `1-2-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-2-2-imperfect-information.html` | `/revision-notes/aqa-a-level-economics/microeconomics/imperfect-information/` | moves `1-2-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-2-3-aspects-of-behavioural-economic-theory.html` | `/revision-notes/aqa-a-level-economics/microeconomics/aspects-of-behavioural-economic-theory/` | moves `1-2-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-2-4-behavioural-economics-and-economic-policy.html` | `/revision-notes/aqa-a-level-economics/microeconomics/behavioural-economics-and-economic-policy/` | moves `1-2-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-3-1-the-determinants-of-the-demand-for-goods-and-services.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-determinants-of-the-demand-for-goods-and-services/` | moves `1-3-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-3-2-price-income-and-cross-elasticities-of-demand.html` | `/revision-notes/aqa-a-level-economics/microeconomics/price-income-and-cross-elasticities-of-demand/` | moves `1-3-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-3-3-the-determinants-of-the-supply-of-goods-and-services.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-determinants-of-the-supply-of-goods-and-services/` | moves `1-3-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-3-4-price-elasticity-of-supply.html` | `/revision-notes/aqa-a-level-economics/microeconomics/price-elasticity-of-supply/` | moves `1-3-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-3-5-the-determination-of-equilibrium-market-prices.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-determination-of-equilibrium-market-prices/` | moves `1-3-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-3-6-the-interrelationship-between-markets.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-interrelationship-between-markets/` | moves `1-3-6` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-4-1-production-and-productivity.html` | `/revision-notes/aqa-a-level-economics/microeconomics/production-and-productivity/` | moves `1-4-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-4-2-specialisation-division-of-labour-and-exchange.html` | `/revision-notes/aqa-a-level-economics/microeconomics/specialisation-division-of-labour-and-exchange/` | moves `1-4-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-4-3-the-law-of-diminishing-returns-and-returns-to-scale.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-law-of-diminishing-returns-and-returns-to-scale/` | moves `1-4-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-4-4-costs-of-production.html` | `/revision-notes/aqa-a-level-economics/microeconomics/costs-of-production/` | moves `1-4-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-4-5-economies-and-diseconomies-of-scale.html` | `/revision-notes/aqa-a-level-economics/microeconomics/economies-and-diseconomies-of-scale/` | moves `1-4-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-4-6-marginal-average-and-total-revenue.html` | `/revision-notes/aqa-a-level-economics/microeconomics/marginal-average-and-total-revenue/` | moves `1-4-6` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-4-7-profit.html` | `/revision-notes/aqa-a-level-economics/microeconomics/profit/` | moves `1-4-7` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-4-8-technological-change.html` | `/revision-notes/aqa-a-level-economics/microeconomics/technological-change/` | moves `1-4-8` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-1-market-structures.html` | `/revision-notes/aqa-a-level-economics/microeconomics/market-structures/` | moves `1-5-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-10-market-structure-efficiency-resource-allocation.html` | `/revision-notes/aqa-a-level-economics/microeconomics/market-structure-efficiency-resource-allocation/` | moves `1-5-10` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-11-consumer-and-producer-surplus.html` | `/revision-notes/aqa-a-level-economics/microeconomics/consumer-and-producer-surplus/` | moves `1-5-11` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-2-the-objectives-of-firms.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-objectives-of-firms/` | moves `1-5-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-3-perfect-competition.html` | `/revision-notes/aqa-a-level-economics/microeconomics/perfect-competition/` | moves `1-5-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-4-monopolistic-competition.html` | `/revision-notes/aqa-a-level-economics/microeconomics/monopolistic-competition/` | moves `1-5-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-5-oligopoly.html` | `/revision-notes/aqa-a-level-economics/microeconomics/oligopoly/` | moves `1-5-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-6-monopoly-and-monopoly-power.html` | `/revision-notes/aqa-a-level-economics/microeconomics/monopoly-and-monopoly-power/` | moves `1-5-6` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-7-price-discrimination.html` | `/revision-notes/aqa-a-level-economics/microeconomics/price-discrimination/` | moves `1-5-7` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-8-the-dynamics-of-competition-and-competitive-market-processes.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-dynamics-of-competition-and-competitive-market-processes/` | moves `1-5-8` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-5-9-contestable-and-non-contestable-markets.html` | `/revision-notes/aqa-a-level-economics/microeconomics/contestable-and-non-contestable-markets/` | moves `1-5-9` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-6-1-the-demand-for-labour-marginal-productivity-theory.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-demand-for-labour-marginal-productivity-theory/` | moves `1-6-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-6-2-influence-upon-the-supply-of-labour-to-different-markets.html` | `/revision-notes/aqa-a-level-economics/microeconomics/influence-upon-the-supply-of-labour-to-different-markets/` | moves `1-6-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html` | `/revision-notes/aqa-a-level-economics/microeconomics/wage-determination-perfectly-competitive-labour-markets/` | moves `1-6-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-6-4-wage-determination-imperfectly-competitive-labour-markets.html` | `/revision-notes/aqa-a-level-economics/microeconomics/wage-determination-imperfectly-competitive-labour-markets/` | moves `1-6-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-6-5-the-influence-of-trade-unions-in-determining-wages-and-levels-of-employment.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-influence-of-trade-unions-in-determining-wages-and-levels-of-employment/` | moves `1-6-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-6-6-the-national-minimum-wage.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-national-minimum-wage/` | moves `1-6-6` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-6-7-discrimination-in-the-labour-market.html` | `/revision-notes/aqa-a-level-economics/microeconomics/discrimination-in-the-labour-market/` | moves `1-6-7` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-7-1-the-distribution-of-income-and-wealth.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-distribution-of-income-and-wealth/` | moves `1-7-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-7-2-the-problem-of-poverty.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-problem-of-poverty/` | moves `1-7-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-7-3-government-policies-poverty-income-distribution.html` | `/revision-notes/aqa-a-level-economics/microeconomics/government-policies-poverty-income-distribution/` | moves `1-7-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-8-1-how-markets-and-prices-allocate-resources.html` | `/revision-notes/aqa-a-level-economics/microeconomics/how-markets-and-prices-allocate-resources/` | moves `1-8-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-8-10-government-failure.html` | `/revision-notes/aqa-a-level-economics/microeconomics/government-failure/` | moves `1-8-10` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-8-2-the-meaning-of-market-failure.html` | `/revision-notes/aqa-a-level-economics/microeconomics/the-meaning-of-market-failure/` | moves `1-8-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-8-3-public-goods-private-goods-and-quasi-public-goods.html` | `/revision-notes/aqa-a-level-economics/microeconomics/public-goods-private-goods-and-quasi-public-goods/` | moves `1-8-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-8-4-positive-and-negative-externalities-in-consumption-and-production.html` | `/revision-notes/aqa-a-level-economics/microeconomics/positive-and-negative-externalities-in-consumption-and-production/` | moves `1-8-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-8-5-merit-and-demerit-goods.html` | `/revision-notes/aqa-a-level-economics/microeconomics/merit-and-demerit-goods/` | moves `1-8-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-8-6-market-imperfections.html` | `/revision-notes/aqa-a-level-economics/microeconomics/market-imperfections/` | moves `1-8-6` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-8-7-competition-policy.html` | `/revision-notes/aqa-a-level-economics/microeconomics/competition-policy/` | moves `1-8-7` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-8-8-public-ownership-privatisation-regulation-and-deregulation-of-markets.html` | `/revision-notes/aqa-a-level-economics/microeconomics/public-ownership-privatisation-regulation-and-deregulation-of-markets/` | moves `1-8-8` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/aqa-a2-micro/1-8-9-government-intervention-in-markets.html` | `/revision-notes/aqa-a-level-economics/microeconomics/government-intervention-in-markets/` | moves `1-8-9` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-1-1-economics-as-a-social-science.html` | `/revision-notes/edexcel-a-level-economics/theme-1/economics-as-a-social-science/` | moves `1-1-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-1-2-positive-normative-statements.html` | `/revision-notes/edexcel-a-level-economics/theme-1/positive-normative-statements/` | moves `1-1-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-1-3-the-economic-problem.html` | `/revision-notes/edexcel-a-level-economics/theme-1/the-economic-problem/` | moves `1-1-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-1-4-production-possibility-frontiers.html` | `/revision-notes/edexcel-a-level-economics/theme-1/production-possibility-frontiers/` | moves `1-1-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-1-5-specialisation-division-of-labour.html` | `/revision-notes/edexcel-a-level-economics/theme-1/specialisation-division-of-labour/` | moves `1-1-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-1-6-types-of-economies.html` | `/revision-notes/edexcel-a-level-economics/theme-1/types-of-economies/` | moves `1-1-6` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-2-1-rational-decision-making.html` | `/revision-notes/edexcel-a-level-economics/theme-1/rational-decision-making/` | moves `1-2-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-2-10-alternative-views-of-consumer-behaviour.html` | `/revision-notes/edexcel-a-level-economics/theme-1/alternative-views-of-consumer-behaviour/` | moves `1-2-10` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-2-2-demand.html` | `/revision-notes/edexcel-a-level-economics/theme-1/demand/` | moves `1-2-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html` | `/revision-notes/edexcel-a-level-economics/theme-1/price-income-cross-elasticities-of-demand/` | moves `1-2-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-2-4-supply.html` | `/revision-notes/edexcel-a-level-economics/theme-1/supply/` | moves `1-2-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-2-5-price-elasticity-of-supply.html` | `/revision-notes/edexcel-a-level-economics/theme-1/price-elasticity-of-supply/` | moves `1-2-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-2-6-price-determination.html` | `/revision-notes/edexcel-a-level-economics/theme-1/price-determination/` | moves `1-2-6` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-2-7-price-mechanism.html` | `/revision-notes/edexcel-a-level-economics/theme-1/price-mechanism/` | moves `1-2-7` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-2-8-producer-consumer-surplus.html` | `/revision-notes/edexcel-a-level-economics/theme-1/producer-consumer-surplus/` | moves `1-2-8` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-2-9-indirect-taxes-subsidies.html` | `/revision-notes/edexcel-a-level-economics/theme-1/indirect-taxes-subsidies/` | moves `1-2-9` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-3-1-types-of-market-failure.html` | `/revision-notes/edexcel-a-level-economics/theme-1/types-of-market-failure/` | moves `1-3-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-3-2-externalities.html` | `/revision-notes/edexcel-a-level-economics/theme-1/externalities/` | moves `1-3-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-3-3-public-goods.html` | `/revision-notes/edexcel-a-level-economics/theme-1/public-goods/` | moves `1-3-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-3-4-information-gaps.html` | `/revision-notes/edexcel-a-level-economics/theme-1/information-gaps/` | moves `1-3-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-4-1-government-intervention-in-markets.html` | `/revision-notes/edexcel-a-level-economics/theme-1/government-intervention-in-markets/` | moves `1-4-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-1/1-4-2-government-failure.html` | `/revision-notes/edexcel-a-level-economics/theme-1/government-failure/` | moves `1-4-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-1-1-economic-growth.html` | `/revision-notes/edexcel-a-level-economics/theme-2/economic-growth/` | moves `2-1-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-1-2-inflation.html` | `/revision-notes/edexcel-a-level-economics/theme-2/inflation/` | moves `2-1-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-1-3-employment-unemployment.html` | `/revision-notes/edexcel-a-level-economics/theme-2/employment-unemployment/` | moves `2-1-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-1-4-balance-of-payments.html` | `/revision-notes/edexcel-a-level-economics/theme-2/balance-of-payments/` | moves `2-1-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-2-1-aggregate-demand.html` | `/revision-notes/edexcel-a-level-economics/theme-2/aggregate-demand/` | moves `2-2-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-2-2-consumption.html` | `/revision-notes/edexcel-a-level-economics/theme-2/consumption/` | moves `2-2-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-2-3-investment.html` | `/revision-notes/edexcel-a-level-economics/theme-2/investment/` | moves `2-2-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-2-4-government-expenditure.html` | `/revision-notes/edexcel-a-level-economics/theme-2/government-expenditure/` | moves `2-2-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-2-5-net-trade.html` | `/revision-notes/edexcel-a-level-economics/theme-2/net-trade/` | moves `2-2-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-3-1-aggregate-supply.html` | `/revision-notes/edexcel-a-level-economics/theme-2/aggregate-supply/` | moves `2-3-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-3-2-short-run-aggregate-supply.html` | `/revision-notes/edexcel-a-level-economics/theme-2/short-run-aggregate-supply/` | moves `2-3-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-3-3-long-run-aggregate-supply.html` | `/revision-notes/edexcel-a-level-economics/theme-2/long-run-aggregate-supply/` | moves `2-3-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-4-1-national-income.html` | `/revision-notes/edexcel-a-level-economics/theme-2/national-income/` | moves `2-4-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-4-2-injections-withdrawals.html` | `/revision-notes/edexcel-a-level-economics/theme-2/injections-withdrawals/` | moves `2-4-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-4-3-equilibrium-levels-of-real-national-output.html` | `/revision-notes/edexcel-a-level-economics/theme-2/equilibrium-levels-of-real-national-output/` | moves `2-4-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-4-4-the-multiplier.html` | `/revision-notes/edexcel-a-level-economics/theme-2/the-multiplier/` | moves `2-4-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-5-1-causes-of-growth.html` | `/revision-notes/edexcel-a-level-economics/theme-2/causes-of-growth/` | moves `2-5-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-5-2-output-gaps.html` | `/revision-notes/edexcel-a-level-economics/theme-2/output-gaps/` | moves `2-5-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-5-3-trade-cycle.html` | `/revision-notes/edexcel-a-level-economics/theme-2/trade-cycle/` | moves `2-5-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-5-4-the-impact-of-economic-growth.html` | `/revision-notes/edexcel-a-level-economics/theme-2/the-impact-of-economic-growth/` | moves `2-5-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-6-1-possible-macroeconomic-objectives.html` | `/revision-notes/edexcel-a-level-economics/theme-2/possible-macroeconomic-objectives/` | moves `2-6-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-6-2-demand-side-policies.html` | `/revision-notes/edexcel-a-level-economics/theme-2/demand-side-policies/` | moves `2-6-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-6-3-supply-side-policies.html` | `/revision-notes/edexcel-a-level-economics/theme-2/supply-side-policies/` | moves `2-6-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-2/2-6-4-conflicts-between-objectives-and-policies.html` | `/revision-notes/edexcel-a-level-economics/theme-2/conflicts-between-objectives-and-policies/` | moves `2-6-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-1-1-sizes-types-of-firms.html` | `/revision-notes/edexcel-a-level-economics/theme-3/sizes-types-of-firms/` | moves `3-1-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-1-2-business-growth.html` | `/revision-notes/edexcel-a-level-economics/theme-3/business-growth/` | moves `3-1-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-1-3-demergers.html` | `/revision-notes/edexcel-a-level-economics/theme-3/demergers/` | moves `3-1-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-2-1-business-objectives.html` | `/revision-notes/edexcel-a-level-economics/theme-3/business-objectives/` | moves `3-2-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-3-1-revenue.html` | `/revision-notes/edexcel-a-level-economics/theme-3/revenue/` | moves `3-3-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-3-2-costs.html` | `/revision-notes/edexcel-a-level-economics/theme-3/costs/` | moves `3-3-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-3-3-economies-diseconomies-of-scale.html` | `/revision-notes/edexcel-a-level-economics/theme-3/economies-diseconomies-of-scale/` | moves `3-3-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-3-4-normal-profits-supernormal-profits-losses.html` | `/revision-notes/edexcel-a-level-economics/theme-3/normal-profits-supernormal-profits-losses/` | moves `3-3-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-4-1-efficiency.html` | `/revision-notes/edexcel-a-level-economics/theme-3/efficiency/` | moves `3-4-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-4-2-perfect-competition.html` | `/revision-notes/edexcel-a-level-economics/theme-3/perfect-competition/` | moves `3-4-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-4-3-monopolistic-competition.html` | `/revision-notes/edexcel-a-level-economics/theme-3/monopolistic-competition/` | moves `3-4-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-4-4-oligopoly.html` | `/revision-notes/edexcel-a-level-economics/theme-3/oligopoly/` | moves `3-4-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-4-5-monopoly.html` | `/revision-notes/edexcel-a-level-economics/theme-3/monopoly/` | moves `3-4-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-4-6-monopsony.html` | `/revision-notes/edexcel-a-level-economics/theme-3/monopsony/` | moves `3-4-6` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-4-7-contestability.html` | `/revision-notes/edexcel-a-level-economics/theme-3/contestability/` | moves `3-4-7` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-5-1-demand-for-labour.html` | `/revision-notes/edexcel-a-level-economics/theme-3/demand-for-labour/` | moves `3-5-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-5-2-supply-of-labour.html` | `/revision-notes/edexcel-a-level-economics/theme-3/supply-of-labour/` | moves `3-5-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-5-3-wage-determination.html` | `/revision-notes/edexcel-a-level-economics/theme-3/wage-determination/` | moves `3-5-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-6-1-government-intervention.html` | `/revision-notes/edexcel-a-level-economics/theme-3/government-intervention/` | moves `3-6-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-3/3-6-2-the-impact-of-government-intervention.html` | `/revision-notes/edexcel-a-level-economics/theme-3/the-impact-of-government-intervention/` | moves `3-6-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-1-1-globalisation.html` | `/revision-notes/edexcel-a-level-economics/theme-4/globalisation/` | moves `4-1-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-1-2-specialisation-trade.html` | `/revision-notes/edexcel-a-level-economics/theme-4/specialisation-trade/` | moves `4-1-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-1-3-pattern-of-trade.html` | `/revision-notes/edexcel-a-level-economics/theme-4/pattern-of-trade/` | moves `4-1-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-1-4-terms-of-trade.html` | `/revision-notes/edexcel-a-level-economics/theme-4/terms-of-trade/` | moves `4-1-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-1-5-trading-blocs-and-the-world-trade-organisation.html` | `/revision-notes/edexcel-a-level-economics/theme-4/trading-blocs-and-the-world-trade-organisation/` | moves `4-1-5` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-1-6-restrictions-on-free-trade.html` | `/revision-notes/edexcel-a-level-economics/theme-4/restrictions-on-free-trade/` | moves `4-1-6` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-1-7-balance-of-payments.html` | `/revision-notes/edexcel-a-level-economics/theme-4/balance-of-payments/` | moves `4-1-7` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-1-8-exchange-rates.html` | `/revision-notes/edexcel-a-level-economics/theme-4/exchange-rates/` | moves `4-1-8` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-1-9-international-competitiveness.html` | `/revision-notes/edexcel-a-level-economics/theme-4/international-competitiveness/` | moves `4-1-9` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-2-1-absolute-relative-poverty.html` | `/revision-notes/edexcel-a-level-economics/theme-4/absolute-relative-poverty/` | moves `4-2-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-2-2-inequality.html` | `/revision-notes/edexcel-a-level-economics/theme-4/inequality/` | moves `4-2-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-3-1-measures-of-development.html` | `/revision-notes/edexcel-a-level-economics/theme-4/measures-of-development/` | moves `4-3-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-3-2-factors-influencing-growth-development.html` | `/revision-notes/edexcel-a-level-economics/theme-4/factors-influencing-growth-development/` | moves `4-3-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-3-3-strategies-influencing-growth-development.html` | `/revision-notes/edexcel-a-level-economics/theme-4/strategies-influencing-growth-development/` | moves `4-3-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-4-1-role-of-financial-markets.html` | `/revision-notes/edexcel-a-level-economics/theme-4/role-of-financial-markets/` | moves `4-4-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-4-2-market-failure-in-the-financial-sector.html` | `/revision-notes/edexcel-a-level-economics/theme-4/market-failure-in-the-financial-sector/` | moves `4-4-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-4-3-role-of-central-banks.html` | `/revision-notes/edexcel-a-level-economics/theme-4/role-of-central-banks/` | moves `4-4-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-5-1-public-expenditure.html` | `/revision-notes/edexcel-a-level-economics/theme-4/public-expenditure/` | moves `4-5-1` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-5-2-taxation.html` | `/revision-notes/edexcel-a-level-economics/theme-4/taxation/` | moves `4-5-2` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-5-3-public-sector-finances.html` | `/revision-notes/edexcel-a-level-economics/theme-4/public-sector-finances/` | moves `4-5-3` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/edexcel-theme-4/4-5-4-macroeconomic-policies-in-a-global-context.html` | `/revision-notes/edexcel-a-level-economics/theme-4/macroeconomic-policies-in-a-global-context/` | moves `4-5-4` out of the leaf, so the topic name starts the segment; drops `.html` |
| `/revision-notes/macroeconomics-diagrams.html` | `/revision-notes/macroeconomics-diagrams/` | drops `.html`; cosmetic only |
| `/revision-notes/microeconomics-diagrams.html` | `/revision-notes/microeconomics-diagrams/` | drops `.html`; cosmetic only |

---

## If you ever do it, the order is

1. Move DNS to Cloudflare, keep GitHub Pages as the origin, and add one bulk
   redirect. Test it on a handful of URLs first — the docs say the free plan
   allows 10,000 redirects across 5 lists, but community reports in 2025–26
   say lists cap at 20 items in practice, and 176 is well past 20.
2. Rename in one commit, all 176, never in batches. A half-migrated folder is
   the worst of both.
3. Re-run `python3 scripts/build_sitemap.py` and resubmit.
4. Update `boards-data/boards.json`'s `slugs`, which exists precisely because
   the URLs are frozen, and re-run `verify_boards.py` — it keeps an independent
   restatement of the whole record and will fail until both sides agree.
5. Expect a dip of two to six weeks. Measure against the term-time baseline
   from task 2 of the manual list, not against an August export.

**`scripts/verify_published_surface.py` is the acceptance test** for anything
that changes what is published. Run it before and after.
