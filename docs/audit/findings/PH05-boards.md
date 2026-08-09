# Phase 5 findings — board-variant duplication

Run 2026-08-09 on `audit/organisation-audit` at `d7744c3`.
Script: `docs/audit/scripts/board_similarity.py`. 87 Edexcel × 79 AQA topic pages,
6,873 comparisons, 5-word shingled Jaccard on body prose with template
furniture stripped.

**Read the headline and the caveat together, or you will act on the wrong one.**

> **Headline.** 26 Edexcel pages have an AQA counterpart at ≥0.80 similarity;
> **22 are ≥0.95**, and a hand-checked pair is word-for-word identical bar one
> token. The duplication is real, measured, and CERTAIN.
>
> **Caveat.** The claimed *harm* — cannibalisation or duplicate suppression — is
> **NOT DEMONSTRATED and cannot be, from the data currently in the repo.** Every
> AQA notes page carried `noindex` until 2026-07-30, nine days before the GSC
> export. The measurement window is contaminated. See PH05-020.

---

## PH05-019 — 22 Edexcel/AQA topic-page pairs are near-verbatim; one is identical bar a single token

**Severity:** Medium · **Category:** Content architecture / SEO · **CERTAIN
(on the duplication) / NOT DEMONSTRATED (on the harm)**

### Distribution

Each Edexcel page scored against its best AQA match:

```
  0.0-0.1   24  ########################
  0.1-0.2    7  #######
  0.2-0.3    9  #########
  0.3-0.4    6  ######
  0.4-0.5    4  ####
  0.5-0.6    1  #
  0.6-0.7    5  #####
  0.7-0.8    5  #####
  0.8-0.9    3  ###
  0.9-1.0   23  #######################
```

Strongly **bimodal**, which is the important shape: 24 pages have essentially no
AQA counterpart, 23 are near-identical, and little sits between. The boards are
not "somewhat overlapping" — each page is either genuinely board-specific or a
copy.

Robust to parameter choice: at 10-word shingles, 22 pairs remain ≥0.90 and 25
≥0.80 (vs 23 and 26 at 5-word). The result is not an artefact of shingle size.

### Verified by hand

`revision-notes/edexcel-theme-3/3-4-2-perfect-competition.html` vs
`revision-notes/aqa-a2-micro/1-5-3-perfect-competition.html`:

```
edexcel words: 591   aqa words: 592
word-level ratio: 0.999
the only differing run:
  insert  ED[]
          AQ[1.5.3]
```

The pages are the same text. The single difference is the spec code in the AQA
`<h1>`.

### Everything except the prose IS differentiated

This is the part that matters for judging severity, and it is good news:

| Signal | Identical across the 26 pairs |
| --- | ---: |
| `<title>` | **0 / 26** |
| `<h1>` | **0 / 26** |
| meta description | **0 / 26** |
| `spec-alert` block | **0 / 26** |
| Outbound internal links | mean Jaccard **0.266**; **0** pairs share >50% |
| JSON-LD `@type` set | identical by design — `BreadcrumbList`, `Course`, `EducationalOrganization`, `LearningResource`, `ListItem` on all 52 pages |

So every signal Google uses to tell two pages apart *other than the body text*
is already board-specific. The pages are not naive duplicates; they are
differentiated wrappers around identical prose.

### Measured, not assumed: the template furniture is doing real work

Running with `--keep-boilerplate` — leaving the breadcrumb, `spec-alert`,
`notes-cta` and diagram-gallery line in — **lowers** the count at ≥0.80 from 26
to 6 and the median from 0.368 to 0.325.

That is the opposite of the usual boilerplate effect, and it is worth
understanding rather than filing away: the furniture is itself board-specific
(the `spec-alert` names the board and unit, the `notes-cta` links to that
board's past papers), so it differentiates rather than pads. **Any future
"tidying" that made these blocks board-generic would delete the differentiation
that currently exists.** Added to `DO-NOT-BREAK.md`.

### Why it matters

Forward-looking, not retrospective. Now that the AQA section is indexable
(PH05-020), Google is about to crawl 79 pages of which 26 are near-verbatim
copies of pages it has already indexed. The likely outcomes are that it indexes
both, or picks one and files the other as "Alternate page" / "Duplicate without
user-selected canonical". Which happens is not predictable from the repo, and
the differentiated metadata genuinely improves the odds.

### Recommendation

**Do nothing yet, and specifically do not canonicalise.** Per `DECISIONS.md` D4,
both boards are meant to rank for board-specific queries, and a cross-board
canonical would permanently forfeit that for the 26 topics where AQA students are
most likely to search.

The evidence needed to act arrives at the day-45 re-measure, which already exists
as step 6 of `seo/06-gsc-checklist.md`. Pre-registering what to look for, so the
answer is read off rather than argued:

| Observation at day 45 | Meaning | Action |
| --- | --- | --- |
| Both pages indexed, both earning impressions | No harm. Differentiated metadata was sufficient | None. Close this finding |
| AQA page indexed, ~0 impressions, Edexcel ranks | Google prefers the Edexcel page on shared queries | Differentiate — see below |
| AQA page in "Duplicate without user-selected canonical" or "Alternate page with proper canonical tag", pointing at the Edexcel URL | Google has actively merged them | Differentiate, and treat as urgent — 26 pages |
| AQA page indexed and ranking on `aqa …` queries specifically | Working as intended | None |

**If differentiation is needed, note what is and is not available here.** The
audit's own scope rule forbids altering, rewording or regenerating economics
prose, so "rewrite the AQA pages" is not a recommendation I can make and not one
this audit will make. The available levers are all **additive** and all require
Eliot's decision because they are content:

- Board-specific worked examples, using each board's own question style.
- Board-specific exam-technique framing — AQA's 25-mark essay vs Edexcel's
  data-response structure differ genuinely, and saying so is not a reword.
- The `past-paper-questions` links already on the pages, made more prominent —
  these are already board-filtered and already differ.

**Effort:** S to monitor, L if differentiation is needed · **Risk of acting**
(prematurely): High — content work on 26 pages to fix a problem that may not
exist · **Risk of not acting:** Medium, and bounded by the day-45 read ·
**Dependencies:** PH05-020 · **Status:** OPEN — MONITOR

---

## PH05-020 — The AQA notes section earns nothing, and duplication is not the reason

**Severity:** High · **Category:** Measurement / indexation · **CERTAIN**

**Evidence.** Not one of the 79 AQA topic pages has a single click or impression:

| Section | Pages | Ranked | Impressions |
| --- | ---: | ---: | ---: |
| `edexcel-theme-1` | 22 | 16 | 10,401 |
| `edexcel-theme-2` | 24 | 15 | 1,770 |
| `edexcel-theme-3` | 20 | 1 | 46 |
| `edexcel-theme-4` | 21 | 5 | 72 |
| **`aqa-a2-micro`** | **54** | **0** | **0** |
| **`aqa-a2-macro`** | **25** | **0** | **0** |

Across the 26 near-identical pairs: **both pages rank 0 times, one ranks 10
times, neither ranks 16 times** — and in every one of the 10, the page that ranks
is the Edexcel one. Zero of the 26 AQA pages appear in
`indexed-pages-baseline-2026-08-08.csv`; 8 of the 26 Edexcel pages do.

**On its own that reads as textbook duplicate suppression. It is not.**

```
$ tail -n +2 seo/gsc-exports/excluded-by-noindex-tag.csv | awk -F/ '{print $4"/"$5}' | sort | uniq -c
  18 revision-notes/aqa-a2-micro
   8 revision-notes/aqa-a2-macro
```

**All 26 "excluded by noindex" URLs are AQA notes pages**, and the tag was
removed on **2026-07-30** in `203f6bd` — **nine days** before the GSC export of
2026-08-08. Age is not the confound either: `aqa-a2-micro` and `aqa-a2-macro`
were first committed 2025-06-15, the same day as `edexcel-theme-1`.

So the AQA section spent effectively the whole measurement window telling Google
not to index it. Zero impressions is the expected result of that, and it would be
the result whether or not a single page were duplicated.

**Why it matters.** Two things, and the second is the bigger one.

1. **48% of the site's topic pages currently earn nothing**, and the fix already
   shipped 10 days ago. This is the largest single upside in the repo, and it is
   already in flight rather than needing work.
2. **The baseline is contaminated, and the only clean read is the day-45
   re-measure.** `seo/06-gsc-checklist.md` schedules it, but nothing in the repo
   holds anyone to it, and `indexed-pages-baseline-2026-08-08.csv` is the file
   the comparison depends on. Any conclusion about board duplication drawn before
   that date is unsound — including one drawn from this audit's own similarity
   numbers.

**Recommendation.** No code change. Three things:

- Treat the day-45 read (≈2026-09-22) as a scheduled task with an owner, not a
  line in a checklist. It is now load-bearing for PH05-019 as well as for the
  original indexing work.
- When re-exporting, export the **indexed pages** again — the checklist already
  flags that its absence was the one gap in the previous audit, and it is now the
  file that answers the duplication question.
- Add the AQA notes section to the URL Inspection priority list. The existing
  step 2 list in `06-gsc-checklist.md` predates the noindex fix landing and does
  not include a single AQA notes URL.

**Effort:** S · **Risk of acting:** None · **Risk of not acting:** High — the one
measurement that resolves the largest open question does not happen ·
**Dependencies:** none · **Status:** OPEN

---

## PH05-021 — `<h1>` convention differs by board: AQA carries the spec code, Edexcel does not

**Severity:** Low · **Category:** Consistency · **CERTAIN**

**Evidence.** Across all 26 pairs, without exception:

```
edexcel H1 plain          26   e.g. "Perfect Competition"
aqa H1 has spec code      26   e.g. "1.5.3 Perfect Competition"
```

**Why it matters.** Minor, and genuinely two-sided. It is an unplanned
inconsistency in how a page presents itself, and the `<h1>` is a strong on-page
signal — a user searching "perfect competition a level" sees a cleaner heading on
one board than the other. Against that, it is currently the *only* textual
difference between the two pages in the worst case, and it is a real
differentiator.

**Recommendation.** Do not change it while PH05-019 is unresolved — removing the
spec code from AQA `<h1>`s would make the identical pair fully identical. Revisit
after the day-45 read, and decide the convention then. If it is ever unified,
unify **towards** including the code on both, not away from it.

Note this is `<h1>` text, which sits on the boundary of the prose rule. Changing
it is a formatting decision, not a content one — but it is the owner's call.

**Effort:** S · **Risk of acting:** Medium right now — could remove the last
differentiator · **Risk of not acting:** Low · **Dependencies:** PH05-019 ·
**Status:** OPEN — BLOCKED on the day-45 read

---

## What P5 did not find

- **No cross-board canonical tags**, and none should be added.
- **No duplicate titles or descriptions** anywhere — confirmed again against the
  P0 census, 0 of 463.
- **No structured-data divergence** between the boards; both emit the same five
  `@type`s on all 52 pages.
- **No evidence of actual cannibalisation.** Zero pairs where both URLs earn
  impressions on the same query, because zero AQA pages earn impressions at all —
  which is PH05-020, not a duplication result.
