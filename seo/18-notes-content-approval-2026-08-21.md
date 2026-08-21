# Revision notes SEO — what needs your yes

21 August 2026. Everything the on-page audit found that would change what a
student reads, and therefore could not be applied. Companion to
`seo/17-notes-seo-audit-2026-08-21.md`.

Each item is one decision, not one per page — where 79 pages need the same
change, that is one item. Ordered by what costs the most while it waits.

**Nothing here has been done.** The branch `seo/notes-onpage-audit` contains
only the changes that touch metadata, markup and structure.

---

## 1. Strip the spec code from the 79 AQA headings — DONE

**Pages:** all 79 AQA topic pages. **Eliot said "strip them", 21 August 2026.
Applied in commit `94a0726`.** `DO-NOT-BREAK.md` PH05-021 is lifted;
`DECISIONS.md` D53 records the reasoning, including the re-measurement that
justified overriding it. The rest of this item is the case as it was put.

**Before:** `2.6.5 Economic Growth and Development`
**After:** `Economic Growth and Development`

**Why it would help.** The 87 Edexcel pages already carry a bare topic name and
the 79 AQA pages do not — two conventions in one folder, and the AQA one puts
five characters nobody searches for in front of the words they do. An `<h1>` is
the second-strongest on-page signal after the title, and 0.1% of your
impressions come from spec-code queries under every filter.

The code does not disappear. This pass has already put **board · module · code**
in a sub-label directly under every `<h1>`, on all 166 pages, so a student
checking they are on the right AQA unit still sees `AQA · Microeconomics ·
1.4.2`. That is what makes this change cheap now and would not have been last
month.

**The cost of not doing it.** Small but real, and permanent while it stands.
The AQA `<h1>` spends its opening on a site-local code that cannot match a
search and that an AQA student comparing it with their own 7136 specification
will find does not match theirs either.

**There is a documented reason to say no, and you should see it.**
`docs/audit/DO-NOT-BREAK.md` records "The AQA `<h1>` spec-code prefix stays
until the day-45 read" (PH05-021), because on the near-identical Edexcel/AQA
pairs it is the last textual differentiator. Measured today, that argument is
weaker than it was: at 5-word-shingle similarity **no cross-board pair is above
0.95 and only six are above 0.80**, and every one of those six is now also
differentiated by a board-specific title, a board-specific description, a
board-specific sub-label and a twin link that names the other board. The brief
recommends stripping; DO-NOT-BREAK says wait for the day-45 read.

**My recommendation: yes, strip them** — but if you would rather hold to the
day-45 read, that is a defensible call and the sub-label means the site is
already consistent where it matters most.

**If you say yes**, it is one edit to 79 byte slices and a rebuild, and
`verify_seo.py` assertion 19 already permits the resulting cross-board `<h1>`
matches because it is scoped per board.

---

## 2. Thirty-six pages now use a display name from their own old title

**Pages:** 36 topic pages, listed in full below. **Already applied** — you
approved the approach on 21 August; this is the page-by-page list so you can
veto any of them.

Their `<h1>` is too long for even the shortest title formula. AQA 1.6.3's is
104 characters. Rather than truncate one silently, each title uses the short
display name **that page's own `<title>` already carried**, so no name is
invented — it is your wording, moved to the front.

**Nothing a student reads on the page changed.** These are titles: the browser
tab and the search result, not the page.

**Six are marked \*** — they lead with an abbreviation a student is unlikely
to type. Those are item 3.


| Page | H1 | Display name used | Title now |
| --- | --- | --- | --- |
| `aqa-a2-macro/2-1-1-the-objectives-of-government-economic-policy.html` | The Objectives of Government Economic Policy | Government Policy Objectives | Government Policy Objectives – AQA A-Level Economics Notes |
| `aqa-a2-macro/2-2-2-aggregate-demand-and-aggregate-supply-analysis.html` | Aggregate Demand and Aggregate Supply Analysis | AD and AS Analysis **\*** | AD and AS Analysis – AQA A-Level Economics Revision Notes |
| `aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html` | Aggregate Demand and the Level of Economic Activity | AD and the Multiplier **\*** | AD and the Multiplier – AQA A-Level Economics Revision Notes |
| `aqa-a2-macro/2-2-5-determinants-of-short-run-aggregate-supply.html` | Determinants of Short-Run Aggregate Supply | Determinants of SRAS **\*** | Determinants of SRAS – AQA A-Level Economics Revision Notes |
| `aqa-a2-macro/2-3-4-possible-conflicts-between-macroeconomic-policy-objectives.html` | Possible Conflicts between Macroeconomic Policy Obje | Macroeconomic Policy Conflicts | Macroeconomic Policy Conflicts – AQA A-Level Economics Notes |
| `aqa-a2-macro/2-4-1-the-structure-of-financial-markets-and-financial-assets.html` | The Structure of Financial Markets and Financial Ass | Financial Markets and Assets | Financial Markets and Assets – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html` | The Nature and Purpose of Economic Activity | The Purpose of Economic Activity | The Purpose of Economic Activity – AQA A-Level Economics |
| `aqa-a2-micro/1-1-4-scarcity-choice-and-the-allocation-of-resources.html` | Scarcity, Choice and the Allocation of Resources | Scarcity, Choice and Allocation | Scarcity, Choice and Allocation – AQA A-Level Economics |
| `aqa-a2-micro/1-3-1-the-determinants-of-the-demand-for-goods-and-services.html` | The Determinants of the Demand for Goods and Service | The Determinants of Demand | The Determinants of Demand – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-3-2-price-income-and-cross-elasticities-of-demand.html` | Price, Income and Cross Elasticities of Demand | Elasticities of Demand | Elasticities of Demand – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-3-3-the-determinants-of-the-supply-of-goods-and-services.html` | The Determinants of the Supply of Goods and Services | The Determinants of Supply | The Determinants of Supply – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-3-5-the-determination-of-equilibrium-market-prices.html` | The Determination of Equilibrium Market Prices | Equilibrium Market Prices | Equilibrium Market Prices – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-4-2-specialisation-division-of-labour-and-exchange.html` | Specialisation, Division of Labour and Exchange | Specialisation and Exchange | Specialisation and Exchange – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-4-3-the-law-of-diminishing-returns-and-returns-to-scale.html` | The Law of Diminishing Returns and Returns to Scale | Diminishing Returns and Scale | Diminishing Returns and Scale – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-5-10-market-structure-efficiency-resource-allocation.html` | Market Structure, Static Efficiency, Dynamic Efficie | Efficiency and Market Structure | Efficiency and Market Structure – AQA A-Level Economics |
| `aqa-a2-micro/1-5-8-the-dynamics-of-competition-and-competitive-market-processes.html` | The Dynamics of Competition and Competitive Market P | The Dynamics of Competition | The Dynamics of Competition – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-6-1-the-demand-for-labour-marginal-productivity-theory.html` | The Demand for Labour, Marginal Productivity Theory | The Demand for Labour and MRP **\*** | The Demand for Labour and MRP – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-6-2-influence-upon-the-supply-of-labour-to-different-markets.html` | Influence upon the Supply of Labour to Different Mar | The Supply of Labour | The Supply of Labour – AQA A-Level Economics Revision Notes |
| `aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html` | The Determination of Relative Wage rates and Levels  | Competitive Wage Determination | Competitive Wage Determination – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-6-4-wage-determination-imperfectly-competitive-labour-markets.html` | The Determination of Relative Wage rates and Levels  | Wage Determination: Monopsony | Wage Determination: Monopsony – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-6-5-the-influence-of-trade-unions-in-determining-wages-and-levels-of-employment.html` | The Influence of Trade Unions in Determining Wages a | Trade Unions and Wages | Trade Unions and Wages – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-7-3-government-policies-poverty-income-distribution.html` | Government Policies to Alleviate Poverty and to Infl | Policies to Reduce Poverty | Policies to Reduce Poverty – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-8-3-public-goods-private-goods-and-quasi-public-goods.html` | Public Goods, Private Goods and Quasi-Public Goods | Public and Quasi-Public Goods | Public and Quasi-Public Goods – AQA A-Level Economics Notes |
| `aqa-a2-micro/1-8-4-positive-and-negative-externalities-in-consumption-and-production.html` | Positive and Negative Externalities in Consumption a | Externalities | Externalities – AQA A-Level Economics Revision Notes |
| `aqa-a2-micro/1-8-8-public-ownership-privatisation-regulation-and-deregulation-of-markets.html` | Public Ownership, Privatisation, Regulation and Dere | Privatisation and Regulation | Privatisation and Regulation – AQA A-Level Economics Notes |
| `edexcel-theme-1/1-1-5-specialisation-division-of-labour.html` | Specialisation and the Division of Labour | Division of Labour | Division of Labour (1.1.5) – Edexcel A-Level Economics Notes |
| `edexcel-theme-1/1-2-10-alternative-views-of-consumer-behaviour.html` | Alternative Views of Consumer Behaviour | Consumer Behaviour | Consumer Behaviour – Edexcel A-Level Economics Notes |
| `edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html` | Price, Income and Cross Elasticities of Demand | PED, YED and XED **\*** | PED, YED and XED (1.2.3) – Edexcel A-Level Economics Notes |
| `edexcel-theme-2/2-4-3-equilibrium-levels-of-real-national-output.html` | Equilibrium Levels of Real National Output | Equilibrium National Output | Equilibrium National Output – Edexcel A-Level Economics |
| `edexcel-theme-2/2-6-4-conflicts-between-objectives-and-policies.html` | Conflicts Between Objectives and Policies | Conflicts Between Objectives | Conflicts Between Objectives – Edexcel A-Level Economics |
| `edexcel-theme-3/3-3-4-normal-profits-supernormal-profits-losses.html` | Normal Profits, Supernormal Profits and Losses | Profits and Losses | Profits and Losses (3.3.4) – Edexcel A-Level Economics Notes |
| `edexcel-theme-4/4-1-5-trading-blocs-and-the-world-trade-organisation.html` | Trading Blocs and the World Trade Organisation | Trading Blocs and the WTO **\*** | Trading Blocs and the WTO – Edexcel A-Level Economics Notes |
| `edexcel-theme-4/4-3-2-factors-influencing-growth-development.html` | Factors Influencing Growth and Development | Influences on Development | Influences on Development – Edexcel A-Level Economics Notes |
| `edexcel-theme-4/4-3-3-strategies-influencing-growth-development.html` | Strategies Influencing Growth and Development | Strategies for Development | Strategies for Development – Edexcel A-Level Economics Notes |
| `edexcel-theme-4/4-4-2-market-failure-in-the-financial-sector.html` | Market Failure in the Financial Sector | Financial Market Failure | Financial Market Failure – Edexcel A-Level Economics Notes |
| `edexcel-theme-4/4-5-4-macroeconomic-policies-in-a-global-context.html` | Macroeconomic Policies in a Global Context | Global Macroeconomic Policy | Global Macroeconomic Policy – Edexcel A-Level Economics |


---

## 3. Six titles lead with an abbreviation — spell them out?

**Pages:** 6, all from the list above. **Not applied.**

| Page | Title now | Proposed |
| --- | --- | --- |
| `aqa-a2-macro/2-2-2-aggregate-demand-and-aggregate-supply-analysis.html` | AD and AS Analysis – AQA A-Level Economics Revision Notes | **Aggregate Demand and Supply – AQA A-Level Economics Notes** |
| `aqa-a2-macro/2-2-4-aggregate-demand-and-the-level-of-economic-activity.html` | AD and the Multiplier – AQA A-Level Economics Revision Notes | **The Multiplier – AQA A-Level Economics Revision Notes** |
| `aqa-a2-macro/2-2-5-determinants-of-short-run-aggregate-supply.html` | Determinants of SRAS – AQA A-Level Economics Revision Notes | **Short-Run Aggregate Supply – AQA A-Level Economics Notes** |
| `aqa-a2-micro/1-6-1-the-demand-for-labour-marginal-productivity-theory.html` | The Demand for Labour and MRP – AQA A-Level Economics Notes | **Demand for Labour – AQA A-Level Economics Revision Notes** |
| `edexcel-theme-1/1-2-3-price-income-cross-elasticities-of-demand.html` | PED, YED and XED (1.2.3) – Edexcel A-Level Economics | **Elasticities of Demand (1.2.3) – Edexcel A-Level Economics** |
| `edexcel-theme-4/4-1-5-trading-blocs-and-the-world-trade-organisation.html` | Trading Blocs and the WTO (4.1.5) – Edexcel A-Level Economics | leave as is — "WTO" is what students type |

**Why it would help.** "AD", "SRAS", "MRP", "PED", "YED", "XED" are how you and
your students write once they are in the room. They are not what a student
types into Google before they know the subject, and a title that leads with an
abbreviation matches neither the abbreviation query nor the spelled-out one
well.

**The cost of not doing it.** These five pages front their title with two or
three letters. Nobody searching "aggregate demand and aggregate supply" or
"short run aggregate supply" sees a match in the first words.

**"WTO" is the exception and I would leave it** — it is genuinely the common
form and "World Trade Organisation" would push the title past 65 characters.

**My recommendation: yes to the five, no to the sixth.** Each proposed name is
mine rather than yours, which is why this is a separate item from 2.

---

## 4. Seven new visible strings

**Pages:** all 166. **Already applied** — the mission authorised the blocks;
this is so you have seen the exact words.

| String | Where |
| --- | --- |
| `Updated` | before the date, under every `<h1>` |
| `On this page` | the heading of the contents list |
| `Related topics` | the heading of the related block |
| `Studying AQA instead?` | on Edexcel pages with a twin |
| `Studying Edexcel instead?` | on AQA pages with a twin |
| `covers this on AQA.` | after the twin link, on Edexcel pages |
| `covers this on Edexcel.` | after the twin link, on AQA pages |

The precedent is the three prev/next captions you approved on 21 August
("Previous topic", "Next topic", "Topic list"). Every other word in these
blocks is reused: contents entries are the page's own `<h2>` text, and related
and twin anchors are the hub's own link text with the code prefix removed.

**Say if any of them reads wrong** and it is a one-line change in
`scripts/notes_extras.py` and a rebuild.

---

## 5. Edexcel has two pages called "Balance of Payments"

**Pages:** `edexcel-theme-2/2-1-4-balance-of-payments.html` and
`edexcel-theme-4/4-1-7-balance-of-payments.html`.

Theme 2 covers it as a measure of macroeconomic performance; Theme 4 covers it
as international economics. Both are legitimate — it really is on the
specification twice.

The keyword brief says a same-board display-name collision should be logged
rather than resolved by putting the code back in the title. It cannot be left
alone, though: `verify_seo.py` assertion 6 requires unique titles across the
whole site and runs on every push, so two identical titles cannot ship. Both
therefore keep the code:

- `Balance of Payments (2.1.4) – Edexcel A-Level Economics Notes`
- `Balance of Payments (4.1.7) – Edexcel A-Level Economics Notes`

**The question for you:** would one of them read better with a distinguishing
word? For instance Theme 2's as `Balance of Payments (2.1.4) – Edexcel
A-Level Economics` and Theme 4's as `The Balance of Payments and Trade
(4.1.7) – …`. Either is fine; a code in brackets is a weak differentiator to a
student scanning a results page.

**My recommendation: leave them.** The codes do distinguish them, both pages
also carry different Theme names in their breadcrumb, and inventing a
distinguishing phrase is worth less than the time it takes to choose one.

---

## 6. Twenty descriptions run 159–168 characters

**Pages:** 20 topic pages. **Not applied.**

Google truncates a meta description at roughly 155–160 characters. These 20 run
up to 168, so a few words are cut off with an ellipsis. Bringing them into the
band means dropping one item from that page's own list of sub-concepts — for
instance `1-1-4-production-possibility-frontiers`:

> Production Possibility Frontiers — Edexcel A-Level Economics (1.1.4):
> movements along versus shifts of the PPF, capital versus consumer goods and
> productive efficiency.

would lose "and productive efficiency".

**A script cannot do this safely.** It was tried. Splitting each list on ", "
and " and " and re-joining a shorter one mangled 25 of them, because " and "
occurs *inside* items as often as between them: "how demand and supply set
price and quantity" came back as "how demand, supply set price, quantity", and
several rejoins produced a literal "and and". Every one would have shipped as a
page's search snippet.

**The cost of not doing it.** Between one and ten characters of a snippet get
an ellipsis on 20 of 166 pages. That is all.

**My recommendation: leave them.** This is the cheapest item on this list to
say no to, and the only way to say yes is 20 hand edits.

---

## 7. Four pages define no term — WAS TWELVE, AND THE TWELVE WAS WRONG

**Eliot said yes on 21 August 2026, and asked to be asked if the definitions
needed writing. Four of them do — task 18 of the manual list has the ask.**

**The twelve was a bad measurement and this item now says so.** It counted
pages carrying a `key-definition` chip, which is what the glossary extractor
looks for — not whether the page answers "what is X", which is what a searching
student needs and what Google reads. Read one by one, **eight of the twelve
already answer it or have a topic that is not a definable term**. The four that
genuinely do not are AQA 1.3.6, AQA 1.6.3, Edexcel 2.4.2 and Edexcel 4.4.1;
§3 of the audit report has the page-by-page verdict.

**A better finding came out of looking properly.** Five pages carry **fourteen
definitions you have already written**, under a plain `<strong>Term:</strong>`
instead of a chip, so the glossary cannot see them. Converting them adds
fourteen glossary entries and changes not one word. Task 19.

**The original twelve:**

`aqa-a2-micro/1-1-2-the-nature-and-purpose-of-economic-activity.html`,
`aqa-a2-micro/1-1-3-economic-resources.html`,
`aqa-a2-micro/1-3-6-the-interrelationship-between-markets.html`,
`aqa-a2-micro/1-6-3-wage-determination-perfectly-competitive-labour-markets.html`,
`aqa-a2-micro/1-6-4-wage-determination-imperfectly-competitive-labour-markets.html`,
`aqa-a2-micro/1-7-3-government-policies-poverty-income-distribution.html`,
`edexcel-theme-2/2-2-4-government-expenditure.html`,
`edexcel-theme-2/2-2-5-net-trade.html`,
`edexcel-theme-2/2-4-2-injections-withdrawals.html`,
`edexcel-theme-2/2-4-3-equilibrium-levels-of-real-national-output.html`,
`edexcel-theme-2/2-5-4-the-impact-of-economic-growth.html`,
`edexcel-theme-4/4-4-1-role-of-financial-markets.html`

**What would change:** each gains one `key-definition` chip defining its own
topic, in the page's first section, in your words.

**Why it would help.** Definition queries — "what is X", "X definition",
"X meaning" — are 6.4% of your impressions and the **only pattern in the whole
Search Console analysis that grows rather than shrinks when the
self-traffic filter is applied.** 154 of the 166 pages already answer that
query in their opening section. These twelve do not.

There is a second benefit: `key-definition` chips are what the glossary is
extracted from, so each new one adds a glossary entry for free.

**The cost of not doing it.** Twelve pages open without answering the most
common shape of question asked about their own topic.

**My recommendation: yes, but it is your writing.** I can list what each page
would need a definition of; the sentence has to be yours. Budget ten minutes.

---

## 8. Seventeen pages under 500 words — ELIOT WILL EXPAND THEM

**Eliot said "I can expand these", 21 August 2026. Task 20 of the manual list
carries it, with the rebuild commands.**

**Pages:** listed with word counts in §8 of the audit report, thinnest first.
**Twelve of the seventeen are AQA micro**, which makes this a section-level
problem rather than a scatter of short pages.

Your call per page: expand it, merge it into a neighbour, or leave it because
the specification point genuinely is that small. Padding for word count makes a
page worse and I will not propose it.

**The cost of not doing it.** The measurable competitors on these topics run
650–3,500 words with 1,200–2,000 typical; the site's median is 741 and these
seventeen are 300–485.

**One knock-on you should know about.** Four pages have only one section, so
their new contents list has a single entry: `aqa-a2-micro/1-6-3-…`,
`aqa-a2-micro/1-6-6-the-national-minimum-wage`,
`edexcel-theme-4/4-4-1-role-of-financial-markets` and
`edexcel-theme-4/4-4-3-role-of-central-banks`. A one-item contents list looks
odd, and it is the thinness showing rather than a fault in the list. Expanding
any of those four fixes it.

**My recommendation:** take the AQA micro twelve as one project rather than
seventeen separate decisions. This is task 7 of the manual list.

---

## 9. Placing a diagram on 43 pages, and drawing 9 — ELIOT WILL ADD THEM

**Eliot said "I'll add diagrams", 21 August 2026. Task 21 of the manual list
carries it, with the markup convention and the two verifiers that catch a
mistake.**

**Pages:** the full 72-row table is §7 of the audit report, with three columns:
the page, the diagram already on disk that matches it, and what I suggest.

- **43 pages have a matching diagram already in `images/diagrams/`.** Placing
  one is a `<figure>`, an `<img>` and a caption — the caption is the only new
  wording and it follows the existing `Figure N:` convention.
- **9 want a diagram drawn** that does not exist: the consumption function, the
  accelerator, total/average/marginal product, the competition spectrum, a
  discriminating employer's MRP, bond price against yield, terms of trade
  against export revenue, unit labour costs, and the monetary policy
  transmission mechanism.
- **20 need none.** A list of policy objectives does not want a graph.

`comparative-advantage.png` is worth noticing on its own: it exists, it is
drawn, and it is currently on **no page at all**. Three of the 43 would use it.

**Why it would help.** Diagram and graph queries are 7.3–9.2% of your
impressions depending on the filter — the third-largest pattern in your data,
ahead of both "notes" and "revision". Save My Exams titles their AQA monopoly
page *"Monopoly diagram economics"*, which tells you what they think it is
worth.

**The cost of not doing it.** 43% of your topic pages are invisible to the
third-largest query pattern you have, on a subject that is taught in diagrams.

**My recommendation: work down the 43 in theme order** and mark each "place",
"draw" or "not needed" as you go. This is task 8 of the manual list.

---

## 10. Four twin-board pairings I am least sure of

**Pages:** 4 of the 109 twin links. **Already applied**, and easily reversed —
one line each in `scripts/notes_twins.py`.

| From | Links to | Why I am unsure |
| --- | --- | --- |
| Edexcel 3.5.3 Wage Determination | AQA 1.6.3 Competitive Wage Determination | AQA splits this across 1.6.3, 1.6.4 and 1.6.5; 1.6.3 is where it starts but it is not the whole topic |
| Edexcel 3.4.6 Monopsony | AQA 1.6.4 Wage Determination: Monopsony | AQA has no monopsony page of its own; 1.6.4 is where the content lives and its own title says so |
| Edexcel 1.3.4 Information Gaps | AQA 1.2.2 Imperfect Information | the measured best match was 1.8.6 Market Imperfections; I chose the one whose name means the same thing |
| Edexcel 4.4.2 Market Failure in the Financial Sector | AQA 2.4.4 The Regulation of the Financial System | near-identical subject, but the prose similarity is only 0.062 |

**Everything else in the map is either the mutual best match on measured prose
similarity or a name-for-name equivalence.** Print the whole thing with
`python3 scripts/notes_twins.py`; twenty minutes of your eyes on it is worth
more than any other review in this document, because a wrong row sends a
student to the wrong board.

**57 pages have no twin at all**, which is deliberate — a pairing that is
merely the nearest available page is worse than none. `python3
scripts/notes_twins.py --unpaired` lists them.

---

## 11. Edexcel Theme 3's hub title lost a word

**Page:** `revision-notes/edexcel-theme-3/index.html`. **Already applied.**

**Before:** `Edexcel Theme 3 Revision Notes | Business Behaviour & Labour
Market | Economics Academy` (91 characters)
**After:** `Edexcel Theme 3 Revision Notes | Business & Labour Market`
(56 characters)

Dropping ` | Economics Academy` was mechanical — Google appends your site name
itself, so those 22 characters were buying nothing. That alone left this title
at 66, one character over the ceiling, so "Behaviour" went too.

The alternative was dropping the whole descriptor, leaving a bare `Edexcel
Theme 3 Revision Notes` — which carries none of the words a student searching
for business or labour-market notes would type. **My recommendation: keep the
trim**, but say if you would rather have `Business Behaviour & Labour Market`
back and lose something else.

The other six hub titles kept their descriptors intact.

---

## 12. Seven hub descriptions are rewritten

**Pages:** the six board hubs and `macro-application/`. **Already applied** —
you asked for these on 21 August. Here they are in full so you can read them.

Every one was 177–247 characters, so Google was truncating all seven. Each
ended with the same 64-character sentence — "Every topic covered, with links to
detailed notes on each subtopic" — which said nothing a hub does not obviously
do. That sentence is gone and the topic list is front-loaded.

| Hub | Now |
| --- | --- |
| Theme 1 | Theme 1 revision notes for Edexcel A-Level Economics: markets, market failure and government intervention. Free notes on every topic in the theme. |
| Theme 2 | Theme 2 revision notes for Edexcel A-Level Economics: aggregate demand and supply, national income, economic growth and macroeconomic policy. Free. |
| Theme 3 | Theme 3 revision notes for Edexcel A-Level Economics: business growth and objectives, costs, market structures and the labour market. Free, on every topic. |
| Theme 4 | Theme 4 revision notes for Edexcel A-Level Economics: international economics, poverty and inequality, emerging economies and the role of the state. Free. |
| AQA micro | Microeconomics revision notes for AQA A-Level Economics: individual decision making, price determination, market structures and labour markets. Free. |
| AQA macro | Macroeconomics revision notes for AQA A-Level Economics: macroeconomic performance, AD and AS, financial markets, policy and the international economy. |
| Macro application | Real-world UK and South Africa macroeconomic data for A-Level Economics. Application points on growth, inflation, unemployment, trade, inequality and policy. |

**These are my sentences, not yours.** They keep your facts and your topic
lists and they are all in the 145–158 band, but the wording is mine. If any of
the seven reads wrong, say which and it is a one-line change.

`revision-notes/index.html` was **not** touched — its head is frozen
(`docs/audit/DECISIONS.md` D50).
