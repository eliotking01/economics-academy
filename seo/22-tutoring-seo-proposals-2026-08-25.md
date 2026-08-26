# Tutoring page — SEO proposals (2026-08-25)

The plan from the 2026-08-25 tutoring-page pass, on branch
`seo/tutoring-page`. Evidence for every claim is in
`seo/21-tutoring-baseline-2026-08-25.md` (Parts 1–3), labelled [repo],
[live search] or [Google docs] below. **Nothing here has been applied.**
Each item waits on Eliot's yes, item by item.

> **Decided 2026-08-26, Eliot, item by item.** Applied on
> `seo/tutoring-page` exactly as approved: A1 option 1, A2 keep, A3 yes
> (Somerset confirmed), A4 yes, A5c yes with his availability facts
> (weekday evenings, morning and daytime slots for free or study
> periods, weekends kept deliberately vague), A6 yes, A7a and A7b yes,
> **D1 yes - the revision-notes/index.html body-anchor exception
> granted**, its head byte-identical and proved so. Declined: A5a, A5b,
> A8, A9. The verifier assertions (A10) are 21-23 in
> `seo/tools/verify_seo.py`.

## The verdict

The page is close to saturated on-page, and the constraint on
"a level economics tutor" is authority, not content. Page 1 for that query
is national marketplaces and agencies (MyTutor, Tutorful, Tutor Hunt,
Keystone) whose domains this site will not out-link in a year, and the
individual tutors who do rank do it on board-specific and long-tail queries
with two assets this site lacks: Google reviews with a visible count, and
video. The repo work below is real but marginal - a cleaner snippet, four
honest content gaps, a handful of better internal anchors, one schema
addition. What can actually move the head query is in group B, which is
why it is the group to start with: the Google Business Profile and reviews
(already on OWNER-TODO), and the off-site profiles. The page's page-1
position for "online a level economics tutor" is an asset to protect:
nothing in group A touches the phrase that ranks, and the title is
deliberately left alone.

---

## Group A — changes I can make in the repo

Ordered by expected effect. Every visible-wording change needs your yes and
ships with a `Text-Change:` trailer; markup-only changes are noted as such.

### A1 — Rewrite the meta description (one decision: pick an option)

**Where:** `tutoring.html` `<head>`, mirrored in `og:description`.
**Evidence:** [repo] 195 chars, ~1,260 px — truncates on desktop around
character ~155–160, cutting "6+ years' experience. Book your free intro
call". [Google docs] no fixed limit, truncated to device width. Also an em
dash, banned by `writing-style.md`.
**Before:**

> Online A-Level Economics tutor for Edexcel, AQA, Edexcel B & OCR — 1-to-1
> lessons £65/hour, small groups £35/hour. First-Class Economics graduate,
> 6+ years' experience. Book your free intro call.

**Option 1 (recommended, 159 chars — everything a parent scans for survives
truncation):**

> Online A-Level Economics tutor for Edexcel, AQA, Edexcel B and OCR.
> 1-to-1 lessons £65/hour, small groups £35/hour. First-Class graduate,
> 6+ years' experience.

**Option 2 (148 chars — no truncation anywhere, but drops the credential):**

> Online A-Level Economics tutor for Edexcel, AQA, Edexcel B and OCR.
> Lessons £65/hour 1-to-1 or £35/hour in a small group. Free 15-minute
> intro call.

**Gain:** a complete snippet for both target queries; CTR, not position.
**Risk:** none to rankings for the "online" query - the leading phrase
"Online A-Level Economics tutor" is unchanged in both options. The
description does not affect ranking; it affects whether the parent clicks.
**Effort:** minutes. `Text-Change: tutoring.html`.

### A2 — The title: options considered, recommendation is keep it

**Evidence:** [repo] 75 chars, ~720 px — the brand truncates on desktop;
both target phrases survive. [Google docs] brand at the end behind a
delimiter is exactly their best practice; truncation of the site name costs
nothing for a site nobody searches by name yet. No em dash (the H1 has one;
see A4).
**Option 1 (recommended): keep the title byte-identical.** The page is on
page 1 for "online a level economics tutor" with this title; the exact
phrase "A-Level Economics Tutor" leads it; the only part lost to
truncation is the brand. Any shortening means deleting either "Online",
"1-to-1", "Group Tuition" or the brand, and each is doing a job ("Group
Tuition" is the only place the word "tuition" reaches the title - it
covers the "a level economics tuition" query).
**Option 2 (only if you want the brand visible on desktop, 61 chars):**
`A-Level Economics Tutor | Online Tuition | Economics Academy` — drops
"1-to-1 & Group". **Risk:** removes "group" from the title of the only
page selling group lessons, for a cosmetic gain. Not recommended.

### A3 — Answer the "near me" cluster: a "Where are you based?" FAQ

**Where:** new FAQ box in the Common Questions section + the same pair in
the FAQPage JSON-LD (kept in sync with the visible text, as the existing
eight are).
**Evidence:** [live search] Google's UK autocomplete for "a level economics
tutor" is dominated by location variants (near me, london, uk,
birmingham); [repo] "Somerset" appears nowhere on the page or the site.
One sentence grounds the page for every local-intent variant without
pretending to be a location page.
**Draft (your voice; two sentences, spaced hyphen, nothing banned):**

> **Where are you based?**
> I'm based in Somerset and teach every lesson online, so I work with
> students right across the UK. Online lessons mean no travel time and a
> much wider choice of lesson slots.

[ELIOT: confirm you are happy naming Somerset on a public page - the site
currently never does.]
**Gain:** the only honest on-page answer to the largest variant cluster;
also feeds A6's schema. **Risk:** none to the "online" query - it
reinforces it. **Effort:** minutes. `Text-Change: tutoring.html`.

### A4 — Writing-style pass: em dashes out of Eliot's own copy

**Where:** H1 (1), hero subhead (1), body copy and FAQ answers (~15), the
JSON-LD Service/FAQ text (6). **Not** the six testimonial blockquotes -
those are the reviewers' words and stay as quoted.
**Evidence:** [repo] `writing-style.md` bans the em dash outright; the page
carries 23 in visible text. The H1 becomes:

> A-Level Economics Tutor - Online 1-to-1 & Small Group Lessons

(punctuation only; wording byte-identical otherwise).
**Gain:** consistency with your voice everywhere else; no ranking effect
claimed. **Risk:** none - Google is punctuation-blind here, and the H1
phrase is unchanged. **Effort:** an hour by hand (rule: no scripted prose
rewrites). `Text-Change: tutoring.html`.

### A5 — Three content sentences the intent analysis says are missing

All drafts; each needs your facts or your yes. One decision per sentence.

**(a) Why book direct** - add to the pricing note, after "…the tutoring
agreement you receive before starting.":

> You book with me directly - no agency and no platform fee. The person
> you speak to on the intro call is the person who teaches every lesson.

**(b) What you get after each lesson** - add to the "3. Learn, practise,
improve" step card or the typical-session FAQ:

> After each lesson I send a short note of what we covered and what to
> practise next. [ELIOT: confirm this is what you actually send - do not
> publish otherwise.]

**(c) Availability** - new FAQ box:

> **When do lessons happen?**
> [ELIOT: confirm your real pattern - e.g. weekday evenings with some
> weekend slots, and whether September places remain.] 

**Evidence:** [repo] Part 2 "Headings and intent" gaps 2–5; [live search]
the ranking individual sites all answer these. **Gain:** covers real
parent questions; modest topical depth without padding. **Risk:** none if
factual; (b) and (c) are blocked until you confirm the facts. **Effort:**
minutes each once confirmed. `Text-Change: tutoring.html`.

### A6 — Restate the full Person node on tutoring.html

**Where:** the `EducationalOrganization` block's `founder`, upgraded from
the name-and-jobTitle stub to the complete Person that already exists on
`about.html` (same `@id`, so the two remain one entity): alumniOf,
hasCredential (First-Class BSc, University of Bath), sameAs (LinkedIn,
Tutorful), description, plus `knowsAbout: ["A-Level Economics", "Edexcel A",
"AQA", "Edexcel B", "OCR"]` on both pages.
**Evidence:** [repo] about.html carries the full node; search engines do
not resolve `@id` across pages (DO-NOT-BREAK PH04-055), so on the page
where the tutor is the product, a parser sees a stub. [Google docs] no
rich result attaches - labelled honestly as entity/E-E-A-T work, plausible
help, unmeasurable.
**Gain:** the tutor query's page carries the tutor's credentials in
machine-readable form. **Risk:** none - additive markup, no visible
change, every fact already published. **Effort:** ~20 lines of JSON-LD.
No trailer needed (not visible text); Rich Results Test before and after.

### A7 — Two contextual internal links with descriptive anchors

**Evidence:** [repo] the site's most-linked pages reach tutoring.html only
via CTA-button anchors ("Book a Free Intro Call", "1-on-1 Tutoring");
07b §5's amended rule allows new links with new anchor text, and declines
sweeps - this is two links, two anchors, two hand-written pages.

**(a) `past-papers/index.html`** (the depth-1 papers hub) - the
resource-services sentence currently reads "…or work through it with a
specialist tutor." Link the phrase and extend it:

- Before: `or work through it with a specialist tutor.`
- After: `or work through it with a <a href="/tutoring.html">specialist
  A-Level Economics tutor</a>.`

(three added words + the anchor; the "1-on-1 Tutoring" button stays).
`Text-Change: past-papers/index.html`.

**(b) `marking.html`** (275 inbound) - the cross-sell paragraph "Combine
marking with 1-on-1 tutoring to work through feedback together…" gains an
anchor on the existing words, wording unchanged:

- After: `Combine marking with <a href="/tutoring.html">1-on-1
  tutoring</a> to work through feedback together…`

Markup-only (no wording change, no Text-Change trailer; the button below
it stays).

**Gain:** descriptive anchors from two high-authority pages for the exact
head-query phrase family. **Risk:** none identified; both pages keep
their buttons, so conversion paths are untouched. **Effort:** minutes.
(The biggest prize of this kind - `revision-notes/index.html`, 271
inbound - is frozen and sits in group D.)

### A8 — One trust link to the real marked examples

**Where:** the testimonials section close or the credentials box: one
sentence linking the two anonymised marked papers that already exist on
marking.html.
**Draft:**

> You can see the standard of feedback I give in the
> [two real marked papers](/marking.html#examples) on the marking page.

[Check the anchor id on marking.html before applying; adjust to its real
fragment.]
**Evidence:** [repo] the assets exist and are the site's best proof of
teaching quality; the tutoring page never mentions them. **Gain:** trust,
and a third distinct anchor into marking.html. **Risk:** none. **Effort:**
minutes. `Text-Change: tutoring.html`.

### A9 — Hero trust line carries the price (conversion work, not ranking)

**Where:** the hero trust line.
**Before:** `100+ students tutored · 6+ years experience · Rated 5/5 on
Tutorful`
**After:** `100+ students tutored · Rated 5/5 on Tutorful · 1-to-1
£65/hour`
**Evidence:** [repo] Part 2 layout analysis: the price a parent came for is
three screens down or one tap. Labelled conversion work - no ranking
claim. **Risk:** leading with price is a judgement call that is yours;
"6+ years experience" moves off the first screen (it stays in the
credentials box). Take it or leave it. **Effort:** minutes.
`Text-Change: tutoring.html`.

### A10 — Verifier assertions to hold whatever you approve

After the approved items land: `seo/tools/verify_seo.py` gains, in its
numbered style with a written reason each, (i) a ceiling on the tutoring
title length if A2 stays as-is (guards against a future well-meant
lengthening), (ii) the description length ceiling from A1, (iii) the
presence of the full Person node from A6. Effort: ~30 minutes including
break-testing each.

---

## Group B — things only you can do

Off-site first, because that is where the head query will actually move.

1. **Google Business Profile, then Google reviews.** Both already on
   OWNER-TODO ("Soon - before term starts") - referenced, not restated.
   What I add once they exist: the review link wired into the site's
   review-ask points, and the trust line updated with the real Google
   count once it is 5 or more (never before, and never a made-up number).
   The Phase 2 table is blunt about why this is first: the one individual
   tutor site ranking for both board queries leads with "87+ five-star
   Google reviews". (~45 minutes to create; reviews accrue over weeks.)
2. **Off-site profiles and directories, white-hat only** (extends the
   OWNER-TODO backlinks line with named targets): First Tutors and Tutor
   Hunt free listings (you are already on Tutorful), The Tutors'
   Association membership if you want the directory listing and the badge,
   and the University of Bath alumni/careers profile if one is open to
   you. Each links the domain from a page about tutoring. (~20 minutes
   each; the Association has a fee - your call whether the badge earns it.)
3. **The 1200×630 og-image** - already on OWNER-TODO; once
   `og-image-wide.png` exists I wire it into tutoring.html (and site-wide)
   and bump the `?v=`. (30 minutes in Canva.)
4. **A Lessonspace screenshot** - one image of a real (or staged) lesson
   whiteboard, no student name visible. I place it in How It Works with
   proper sizing and WebP. It shows a parent what "online lesson" means.
   (10 minutes to capture.)
5. **The "meet the tutor" video** - already an OWNER-TODO idea. Once a
   file exists I add a lazy-loaded, poster-first embed that does not touch
   the Lighthouse score. Phase 2 note: both strong individual-site
   competitors lead with video. (An afternoon, whenever.)
6. **Facts to confirm for group A**: Somerset naming (A3), what you send
   after lessons (A5b), your availability pattern (A5c), and whether you
   want the first-lesson shape described (Part 2 gap 5 - needs two
   sentences from you about how you actually run lesson one).
7. **A two-minute check**: search the two main queries in a clean browser
   profile and note what you see (then log the date in OWNER-TODO's
   Rank-check log). Google blocked every automated route (Part 3 method
   note), so the Phase 2 ordering is approximate until a human looks.

---

## Group C — considered, and recommend against

1. **Review/AggregateRating schema anywhere.** Self-serving reviews are
   ineligible and `Service` is not a supported review-snippet type -
   confirmed against the live documentation on 2026-08-25, same answer as
   seo/08. The visible "Rated 5/5 on Tutorful" line is fine; markup is not.
2. **A separate "online A-Level Economics tutor" page.** It would compete
   with this page for its best query, split the inbound anchors, and
   create a permanent URL on a site that can never redirect. The "online"
   query is already page 1 on this page.
3. **Any URL change** (`/a-level-economics-tutor/` etc.).
   `seo/16-url-structure-and-redirect-options.md` already settles it; no
   new evidence, and the canonical-plus-new-page trick stays declined.
4. **Padding the body toward competitor word counts.** The ranking pages
   are 1,200–2,800 words mostly of tutor cards and FAQ boilerplate; this
   page converts. A5's targeted sentences close real gaps; a word-count
   chase would blunt the page for no ranking mechanism I can point to.
5. **LocalBusiness schema.** Requires a physical postal address in the
   markup; the docs offer nothing for online-only businesses. Publishing
   your home address is not an SEO decision I am willing to propose.
6. **Removing the FAQPage block.** It earns nothing (feature removed for
   all sites, May 2026 - live doc), but removal also earns nothing and
   the markup is accurate. Keep, expect nothing, stop counting it as an
   asset.
7. **Re-anchoring the generated families' CTA buttons** (the 320 "Book a
   Free Intro Call" links on mcq/ppq topic pages). One generator string
   would swap 320 anchors at once - exactly the bulk sweep 07b §5
   declines, and the notes tails already provide 168 descriptive anchors.
8. **Chasing "edexcel/aqa economics tutor" with new content.** Autocomplete
   shows those queries are mostly resource-seeking (tutor2u, PMT). The
   exam-board section already covers the tutor-intent slice; the notes own
   the resource slice.
9. **Forcing the unhyphenated "A level" spelling into the copy.** Google
   treats the spellings as close variants; the one unhyphenated
   occurrence (in a testimonial) is enough, and deliberate misspelling
   reads as exactly that.

---

## Group D — blocked by a rule; asking

1. **A descriptive anchor on `revision-notes/index.html`.** The site's
   second-most-linked page (271 inbound) reaches tutoring.html with "Book
   a Free Intro Call" - the least descriptive anchor on the most valuable
   page. The fix is one anchor's text (or one added in-sentence link) in
   its services panel. **The rule:** the file is GSC-frozen -
   D50 froze the head, and `.prettierignore` marks the whole file frozen;
   the brief says ask before proposing anything in its body. **Why I
   would break it:** the head stays byte-identical - this touches only
   body anchor text, which no freeze rationale I can find actually
   covers - and it is the single highest-authority descriptive anchor
   available to this page. **Your call**; if no, A7's two links stand
   alone.
2. **The home-page head split.** index.html's title and H1 both carry
   "Tutoring" and, in the one (stale) index checkable, the home page
   outranks tutoring.html for the tutor query. The clean fix would be a
   home title tweak - **blocked by your own decision** (the home side of
   the ~22 September check stays clean), and rightly: September's data
   will show whether the cannibalisation is real before anything is
   risked. Not asking now; flagging so the September read looks for it.

---

## What happens next

Nothing, until you reply. Say yes/no per item (A1 option 1 or 2, A2 keep
or change, A3 with or without Somerset, A4, A5a–c, A6, A7a–b, A8, A9, D1)
and I apply exactly those, then run the suite, Live Server at desktop and
360 px, Lighthouse to `seo/lh-tutoring-after`, and the Rich Results Test,
per the brief's Phases 4–6.
