#!/usr/bin/env python3
"""The title and description formulas from seo/14-notes-keyword-brief.md.

One module, imported by both the rewriter that applies them and the verifier
that asserts them, so the rule and the check can never drift apart. Read only:
this file computes strings and writes nothing.

    python3 seo/tools/notes_titles.py          # print every page's new title

THE DISPLAY NAME
----------------
`{Topic}` is the page's H1 with any AQA spec-code prefix stripped. 130 of the
166 pages fit a title variant with that name. The other 36 do not - AQA 1.6.3's
H1 is 104 characters - and the brief says to propose a shorter display name
rather than truncate silently.

Every one of those 36 already HAS a short display name, in its own current
<title>: 1.6.3 reads "Competitive Wage Determination" today. DISPLAY_NAME
records them. They are Eliot's own published wording, lifted from the field
this module is rewriting, not names invented here - approved 2026-08-21, and
listed page by page in seo/18-notes-content-approval-2026-08-21.md so any one
of them can be vetoed.

Six of the 36 use an abbreviation that cannot match a search - "AD and AS
Analysis", "Determinants of SRAS", "PED, YED and XED". Spelling those out
would be a name neither the H1 nor the current title uses, so they are a
proposal in the approval document and NOT applied here. ABBREVIATED names
them so the report can count them without a second list going stale.
"""

from __future__ import annotations

import re

# Rendered-length ceilings from the brief §4. Measured on the rendered string,
# not the template, and not on the stored one either: a stored "&amp;" is one
# character to a reader and five to len().
PREFERRED_MAX = 60
HARD_MAX = 65

EDEXCEL_VARIANTS = [
    "{topic} ({code}) – Edexcel A-Level Economics Revision Notes",
    "{topic} ({code}) – Edexcel A-Level Economics Notes",
    "{topic} – Edexcel A-Level Economics Revision Notes",
    "{topic} – Edexcel A-Level Economics Notes",
    "{topic} – Edexcel A-Level Economics",
]

# No spec code, ever. The AQA codes on this site are site-local 1.x.y / 2.x.y
# and deliberately not the real 7136 codes (DECISIONS.md, ratified). Printing
# one in a title cannot match a search - spec-code queries are 0.1% of
# impressions under every filter in the brief §1 - and can mislead an AQA
# student comparing it against their own specification.
AQA_VARIANTS = [
    "{topic} – AQA A-Level Economics Revision Notes",
    "{topic} – AQA A-Level Economics Notes",
    "{topic} – AQA A-Level Economics",
]

# slug -> the display name already published in that page's own <title>.
# Keyed on slug rather than on (board, code) because 37 spec codes collide
# across the two boards and a bare code would silently rename the wrong page -
# the same hazard verify_seo.py assertion 13 exists for.
DISPLAY_NAME = {
    # AQA macro
    "2-1-1-the-objectives-of-government-economic-policy": "Government Policy Objectives",
    "2-2-2-aggregate-demand-and-aggregate-supply-analysis": "AD and AS Analysis",
    "2-2-4-aggregate-demand-and-the-level-of-economic-activity": "AD and the Multiplier",
    "2-2-5-determinants-of-short-run-aggregate-supply": "Determinants of SRAS",
    "2-3-4-possible-conflicts-between-macroeconomic-policy-objectives": "Macroeconomic Policy Conflicts",
    "2-4-1-the-structure-of-financial-markets-and-financial-assets": "Financial Markets and Assets",
    # AQA micro
    "1-1-2-the-nature-and-purpose-of-economic-activity": "The Purpose of Economic Activity",
    "1-1-4-scarcity-choice-and-the-allocation-of-resources": "Scarcity, Choice and Allocation",
    "1-3-1-the-determinants-of-the-demand-for-goods-and-services": "The Determinants of Demand",
    "1-3-2-price-income-and-cross-elasticities-of-demand": "Elasticities of Demand",
    "1-3-3-the-determinants-of-the-supply-of-goods-and-services": "The Determinants of Supply",
    "1-3-5-the-determination-of-equilibrium-market-prices": "Equilibrium Market Prices",
    "1-4-2-specialisation-division-of-labour-and-exchange": "Specialisation and Exchange",
    "1-4-3-the-law-of-diminishing-returns-and-returns-to-scale": "Diminishing Returns and Scale",
    "1-5-10-market-structure-efficiency-resource-allocation": "Efficiency and Market Structure",
    "1-5-8-the-dynamics-of-competition-and-competitive-market-processes": "The Dynamics of Competition",
    "1-6-1-the-demand-for-labour-marginal-productivity-theory": "The Demand for Labour and MRP",
    "1-6-2-influence-upon-the-supply-of-labour-to-different-markets": "The Supply of Labour",
    "1-6-3-wage-determination-perfectly-competitive-labour-markets": "Competitive Wage Determination",
    "1-6-4-wage-determination-imperfectly-competitive-labour-markets": "Wage Determination: Monopsony",
    "1-6-5-the-influence-of-trade-unions-in-determining-wages-and-levels-of-employment": "Trade Unions and Wages",
    "1-7-3-government-policies-poverty-income-distribution": "Policies to Reduce Poverty",
    "1-8-3-public-goods-private-goods-and-quasi-public-goods": "Public and Quasi-Public Goods",
    "1-8-4-positive-and-negative-externalities-in-consumption-and-production": "Externalities",
    "1-8-8-public-ownership-privatisation-regulation-and-deregulation-of-markets": "Privatisation and Regulation",
    # Edexcel
    "1-1-5-specialisation-division-of-labour": "Division of Labour",
    "1-2-10-alternative-views-of-consumer-behaviour": "Consumer Behaviour",
    "1-2-3-price-income-cross-elasticities-of-demand": "PED, YED and XED",
    "2-4-3-equilibrium-levels-of-real-national-output": "Equilibrium National Output",
    "2-6-4-conflicts-between-objectives-and-policies": "Conflicts Between Objectives",
    "3-3-4-normal-profits-supernormal-profits-losses": "Profits and Losses",
    "4-1-5-trading-blocs-and-the-world-trade-organisation": "Trading Blocs and the WTO",
    "4-3-2-factors-influencing-growth-development": "Influences on Development",
    "4-3-3-strategies-influencing-growth-development": "Strategies for Development",
    "4-4-2-market-failure-in-the-financial-sector": "Financial Market Failure",
    "4-5-4-macroeconomic-policies-in-a-global-context": "Global Macroeconomic Policy",
}

# The six display names above that lead with an abbreviation a student is
# unlikely to type. Named here so the audit can count them; a spelled-out
# replacement is proposed in the approval document, not applied.
ABBREVIATED = {
    "2-2-2-aggregate-demand-and-aggregate-supply-analysis",
    "2-2-4-aggregate-demand-and-the-level-of-economic-activity",
    "2-2-5-determinants-of-short-run-aggregate-supply",
    "1-6-1-the-demand-for-labour-marginal-productivity-theory",
    "1-2-3-price-income-cross-elasticities-of-demand",
    "4-1-5-trading-blocs-and-the-world-trade-organisation",
}

CODE_PREFIX_RE = re.compile(r"^(\d+(?:\.\d+)+)\s+(.*)$")


def display_name(slug: str, h1: str) -> str:
    """The topic name a title should carry: the H1, or the recorded short name."""
    if slug in DISPLAY_NAME:
        return DISPLAY_NAME[slug]
    m = CODE_PREFIX_RE.match(h1)
    return m.group(2) if m else h1


# Two Edexcel pages share the display name "Balance of Payments": Theme 2's
# 2.1.4, where it is a measure of macroeconomic performance, and Theme 4's
# 4.1.7, where it is international economics. The brief says a same-board
# display-name collision is to be logged rather than disambiguated by
# reinstating the code - but verify_seo.py assertion 6 requires unique titles
# across every page on the site and runs in CI, so two identical titles cannot
# ship. These two therefore keep a code-bearing variant, which is unique, and
# the collision is logged for a decision on a distinct display name.
COLLIDING = {
    "2-1-4-balance-of-payments",
    "4-1-7-balance-of-payments",
}


def title_for(board: str, slug: str, h1: str, code: str) -> tuple[str, int]:
    """(title, variant number). Raises if even the last variant overflows."""
    variants = EDEXCEL_VARIANTS if board == "Edexcel" else AQA_VARIANTS
    topic = display_name(slug, h1)
    rendered = [v.format(topic=topic, code=code) for v in variants]

    if slug in COLLIDING:
        # The longest code-bearing variant inside the hard ceiling. Only the
        # first two Edexcel variants carry the code, so this is a choice
        # between them, not a licence to overflow.
        for i, s in enumerate(rendered[:2], 1):
            if len(s) <= HARD_MAX:
                return s, i

    for i, s in enumerate(rendered, 1):
        if len(s) <= PREFERRED_MAX:
            return s, i
    if len(rendered[-1]) <= HARD_MAX:
        return rendered[-1], len(variants)
    raise ValueError(
        f"{slug}: no variant fits - shortest is {len(rendered[-1])} chars "
        f"({rendered[-1]!r}). Add a display name to DISPLAY_NAME, with the "
        f"page on the approval list.")


# ------------------------------------------------------------------ description

DESC_MIN, DESC_MAX = 145, 158

# Offered only where TRUE for the page, and never claimed otherwise: §5
# forbids naming a feature the page does not have, so each is gated on a
# measurement of the page's own body rather than on what the topic "should"
# contain.
TAILS = [
    (", with evaluation points for the exam.", "evaluation"),
    (", with key definitions for the exam.", "definitions"),
    (", with diagrams for the exam.", "diagrams"),
    (", with a diagram for the exam.", "diagram"),
    # Short forms of the same four claims. They exist because the difference
    # between a 142-character description and the 145 floor is three
    # characters, and the only honest way to spend three characters is to say
    # one more true thing about the page.
    (", with evaluation points.", "evaluation"),
    (", with key definitions.", "definitions"),
    (", with diagrams.", "diagrams"),
    (", with a diagram.", "diagram"),
]

# Four ways to write the same sentence, longest first. §5 gives the first;
# the other three are the same clause with the join tightened, and exist only
# because no single one of them lands 166 different pages in a 14-character
# band. The topic name leads in all four, which is the rule that matters.
LEAD_FORMS = [
    ("A", "{topic} for {board} A-Level Economics {where}. {clause}"),
    ("B", "{topic} — {board} A-Level Economics {where}. {clause}"),
    ("C", "{topic} for {board} A-Level Economics {where}: {items}."),
    ("D", "{topic} — {board} A-Level Economics {where}: {items}."),
]

DESC_MIN, DESC_MAX = 145, 158

COVERS_RE = re.compile(r"\bCovers\b")


def covers_clause(existing: str) -> str:
    """The page's own sub-concept sentence, lifted whole.

    §5 requires the sub-concepts to come from the page's H2s or its
    key-definition chips and never from memory. Every one of the 166 existing
    descriptions already carries exactly that, written against the page, as a
    sentence beginning "Covers". Lifting it keeps Eliot's wording and keeps
    the claim true; assembling a fresh list from lowercased H2 text would read
    like a machine wrote it and would risk asserting coverage the sentence
    does not.

    Any trailing feature sentence ("With diagrams.") is dropped: those are
    re-derived from the page below and re-added only where still true.
    """
    m = COVERS_RE.search(existing)
    if not m:
        raise ValueError(f"no 'Covers' clause in {existing!r}")
    clause = existing[m.start():].strip()
    return re.split(r"(?<=\.)\s+", clause)[0].rstrip()


# WHY THERE IS NO LIST-SHORTENING HERE
#
# 20 of the 166 descriptions cannot be brought under 158 characters without
# dropping an item from the page's own sub-concept list, and the brief asks
# for "two or three sub-concepts" while several of these lists carry five.
# Shortening them looked like the obvious fix and it was attempted, splitting
# each list on ", " and " and " and re-joining a shorter one.
#
# It mangled 25 of them. " and " occurs INSIDE items as often as between them,
# so "how demand and supply set price and quantity" came back as "how demand,
# supply set price, quantity", and several rejoins produced a literal "and
# and". Every one of those would have shipped as a page's SERP snippet.
#
# That is hard rule 6 - never bulk-rewrite prose with a script - arriving in
# a field nobody thinks of as prose. The 20 pages keep their full list and
# run 159 to 168 characters, which Google truncates and nothing else. They
# are named in the audit report; shortening any of them is a hand edit.

def description_for(topic: str, board: str, module: str, code: str,
                    existing: str, *, images: int, key_definitions: int,
                    evaluation: bool) -> tuple[str, str]:
    """(description, "<form><tail>"). Front-loaded, 145-158 where reachable.

    Every candidate is the same set of words in the same order; what varies is
    the join and whether a truthful feature tail fits. The first candidate
    that lands in the band wins, so form A - the brief's own sentence - is
    used wherever it fits, and the tighter joins exist only for the pages
    where it does not.
    """
    where = f"({code})" if board == "Edexcel" else module
    clause = covers_clause(existing)
    items = clause[len("Covers "):].rstrip(".")

    allowed = {
        "evaluation": evaluation,
        "definitions": key_definitions > 0,
        "diagram": images == 1,
        "diagrams": images > 1,
    }

    candidates: list[tuple[str, str]] = []
    for form, template in LEAD_FORMS:
        base = template.format(topic=topic, board=board, where=where,
                               clause=clause, items=items)
        candidates.append((base, f"{form}-none"))
        for tail, name in TAILS:
            if allowed[name]:
                candidates.append((base[:-1] + tail, f"{form}-{name}"))

    in_band = [c for c in candidates if DESC_MIN <= len(c[0]) <= DESC_MAX]
    if in_band:
        return max(in_band, key=lambda c: len(c[0]))

    # Nothing lands. Prefer the longest that still fits the ceiling - a short
    # description wastes SERP space but shows in full; only if every candidate
    # overflows do we take the shortest and let the page be logged.
    under = [c for c in candidates if len(c[0]) <= DESC_MAX]
    if under:
        return max(under, key=lambda c: len(c[0]))
    return min(candidates, key=lambda c: len(c[0]))
