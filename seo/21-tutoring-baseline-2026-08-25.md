# Tutoring page — baseline, audit and live-search comparison (2026-08-25)

The before snapshot for the tutoring-page SEO pass, on branch
`seo/tutoring-page`. Every claim in `seo/22-tutoring-seo-proposals-2026-08-25.md`
points back here. Three parts: the Phase 0 baseline (this state of the page,
measured), the Phase 1 audit findings, and the Phase 2 live-search comparison.

Method notes are inline. Search Console data is deliberately not used
anywhere in this file, on Eliot's instruction of 2026-08-25: the exports are
too small a sample for this page and contaminated by the site's own searches.
Evidence is the repository and live fetches only.

---

## Part 1 — Phase 0 baseline

Tree state: clean `main` at `0bad0c88`, all 24 checks of
`.github/workflows/verify.yml` green locally before anything was touched
(including `verify_generated.py`: 0 files would change, and
`build_sitemap.py --check`: SITEMAP OK).

### Head

| Field | Value | Length |
| --- | --- | --- |
| `<title>` | `A-Level Economics Tutor \| Online 1-to-1 & Group Tuition \| Economics Academy` | **75 chars, ~720 px** |
| meta description | `Online A-Level Economics tutor for Edexcel, AQA, Edexcel B & OCR — 1-to-1 lessons £65/hour, small groups £35/hour. First-Class Economics graduate, 6+ years' experience. Book your free intro call.` | **195 chars, ~1,260 px** |
| canonical | `https://economicsacademy.co.uk/tutoring.html` | — |
| robots meta | none (indexable) | — |
| og:type | `website` | — |
| og:title / og:description | mirror the title and description exactly | — |
| og:image | `/og-image.png?v=1`, declared 1200×1200 | square |
| twitter:card | `summary_large_image` (wants ~2:1 — the square logo renders cropped) | — |
| sitemap | in `sitemaps/core.xml`, lastmod 2026-08-24, priority 0.9 | — |

Pixel widths are estimates from per-character average advance widths (Arial
20 px title / 14 px description, the Google desktop rendering), accurate to a
few per cent — good enough to say confidently that both fields truncate
(desktop limits are roughly 600 px for the title and 920 px for the
description). What survives is measured in Part 2, "Head and snippet".

### Body

- `<h1>`: `A-Level Economics Tutor — Online 1-to-1 & Small Group Lessons`
- Words of visible text inside `<main>`: **1,288**. Whole `<body>` visible
  text (baked header + footer + the modal included, scripts and JSON-LD
  excluded): **1,623**. Measured by stripping tags from the source; the
  brief's "~3,700 words" figure is not reproducible by any counting method
  tried and should not be cited again.
- One image: `eliot_shirt.JPG` (WebP `srcset` 400 w/800 w via `<picture>`),
  `alt="Eliot King — A-Level Economics Tutor"`, 800×800, not lazy-loaded.

### Heading outline (whole page, in order)

```
H1 A-Level Economics Tutor — Online 1-to-1 & Small Group Lessons
H2 Eliot King - Expert Tutor and Founder of Economics Academy
H2 How It Works
  H3 1. Book a free intro call / 2. Get a tailored plan / 3. Learn, practise, improve
H2 Tutoring Prices
  H3 Introductory Call / One-to-One Lessons / Group Lessons
H2 Small Group Tutoring — £35 per Hour
  H3 Join with friends, or be matched / Try it before you commit
H2 Tutoring for Every A-Level Economics Exam Board
  H3 Edexcel (A) / AQA / Edexcel B / OCR
H2 What Students & Parents Say
H2 Book Your Free 15-Minute Intro Call
H2 Common Questions
  H3 ×8 (the FAQ questions, mirrored in the FAQPage JSON-LD)
H2 Enquire About …   (inside the hidden #contactModal, outside <main>)
```

Nesting is clean; no level is skipped.

### JSON-LD (4 blocks, all parse)

| Block | Fields carried |
| --- | --- |
| `Service` | name, description, url, serviceType "Online Tutoring", areaServed "GB", provider (`EducationalOrganization` by `@id` ref), offers ×3 (Offer: name, price 0/65/35, priceCurrency GBP, description) |
| `EducationalOrganization` | `@id` `#organization`, name, url, logo (ImageObject 512×512), description, sameAs (Tutorful, LinkedIn), founder (Person: `@id` `about.html#eliot-king`, name, jobTitle, url) |
| `BreadcrumbList` | Home → Tutoring (final item correctly without `item`) |
| `FAQPage` | 8 Question/Answer pairs, texts byte-matching the visible FAQ section |

### Links out of `<main>` (26, in order)

| Href | Anchor |
| --- | --- |
| `/` | Home (breadcrumb) |
| `#booking` ×4 | Book a Free Intro Call ×3, Book Now |
| `#pricing` | See Lesson Prices |
| `/about.html` ×2 | Find out more about the Tutor; About page |
| `https://tutorful.co.uk/tutors/qlorq3vr` ×2 | Reviews on Tutorful; Read All Reviews on Tutorful |
| `/contact.html` ×4 | Enquire Now ×2; Ask About Group Availability; Contact me |
| `/revision-notes/edexcel-theme-1/` | Free Edexcel notes |
| `/past-papers/edexcel/` | Edexcel past papers |
| `/revision-notes/aqa-a2-micro/` | Free AQA notes |
| `/past-papers/aqa/` | AQA past papers |
| `/past-papers/edexcel-b/` | Edexcel B past papers |
| `/past-papers/ocr/` | OCR past papers |
| `https://calendly.com/kingtuition/freeintroduction` | Book a free 15-minute intro call on Calendly (the no-JS fallback) |
| `/revision-notes/` ×2 | revision notes (FAQ answers) |
| `/past-papers/` | past papers |
| `/marking.html` | paper-marking service |
| `/faq.html` | View Full FAQ |

No bare `href="#"` in the page's own body (the two in the desktop nav are
baked template labels with `role="button"` — out of scope, per the brief).

### Inbound links, measured 2026-08-25

All published pages scanned for anchors to `/tutoring.html` (the baked
header counts, so the totals are the SERVED graph; the in-body rows are the
CONTENT graph the earlier audits cite):

- **508 pages link in; 1,532 links in total.** 1,017 of them are the baked
  navigation ("Tutoring", two per page — desktop nav + mobile drawer).
- **In-body (content) links: 515, across 14 distinct anchors** — a far
  better spread than the 2026-08-10 record of 444/455 on one string:

| Count | Anchor | From |
| ---: | --- | --- |
| 324 | Book a Free Intro Call (3 to `#booking`, 1 lowercase) | practice-questions and ppq topic pages, hubs, root pages |
| 168 | **online A-Level Economics tutor** | the 166 notes topic-page tails (D58) + both diagram galleries |
| 7 | Book a tutoring session | flashcards pages |
| 5 | 1-on-1 Tutoring | the past-papers hubs |
| 3 | Book a 1-on-1 session | glossary pages |
| 8 | eight other anchors, one or two uses each | index.html, about, faq, contact |

- **What the highest-authority pages use** (in-body, baked chrome excluded):
  - `index.html` (441 inbound): five links — `Book a Free Intro Call` ×2,
    `Explore 1-to-1 & Group Tutoring`, the service-card block (long anchor
    naming "specialist online A-Level Economics tutor"), `free 15-minute
    intro call`
  - `revision-notes/index.html` (271 inbound, GSC-frozen file): `Book a Free
    Intro Call` — its one tutoring link says nothing about tutoring
  - `practice-questions/index.html` (174): `Book a Free Intro Call`
  - `past-paper-questions/index.html` (164): `Book a Free Intro Call`
  - `past-papers/index.html` + the four board pages: `1-on-1 Tutoring`
  - `marking.html` (275): `Book a Free Intro Call`
  - the two diagram galleries: `online A-Level Economics tutor`
  - `flashcards/index.html`: `Book a tutoring session`
  - the glossary pages: `Book a 1-on-1 session`

### Third-party requests

At load: none until interaction/scroll. Referenced: `assets.calendly.com` +
`calendly.com` (preconnected in the head; widget.js/css fetched only when the
booking section nears the viewport — performance pass Phase 3),
`formspree.io` (modal submit only), `googletagmanager.com` (only after
analytics consent), `tutorful.co.uk` (outbound links). LinkedIn appears only
inside JSON-LD `sameAs`.

### Lighthouse (live URL, 2026-08-25)

`python3 seo/tools/run_lighthouse.py --out seo/lh-tutoring-before --only
tutoring` — Lighthouse 12, mobile, 3 runs, medians
(`seo/lh-tutoring-before/medians.json`):

| Page | Perf | LCP | CLS | TBT | FCP | SI | Weight |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| tutoring (before) | 97 | 1.90 s | 0.000 | 40 ms | 1.54 s | 3.91 s | 196 KB |

Critical chain 3 deep / 475 ms (`tutoring.css`, `fontawesome-all.min.css`
behind `main.css`). Consistent with the 2026-08-23 live run (98 / 1.77 s);
the point drop is run noise, not a regression. Core Web Vitals are not the
constraint on this page.

---

## Part 2 — Phase 1 audit findings

### Head and snippet

- **The title truncates on desktop and loses the brand.** 75 characters,
  ~720 px against Google's ~600 px desktop width. What survives is roughly
  `A-Level Economics Tutor | Online 1-to-1 & Group Tuition | Econo…` — the
  two target phrases both survive; "Economics Academy" is the part cut.
  Google's title-link documentation (fetched live 2026-08-25) sets no fixed
  limit but says long titles are truncated to device width and that the site
  name should sit at one end behind a delimiter — which this title does, so
  the truncation costs the brand, not the keywords. On mobile the title wraps
  to two lines and more of it survives.
- **The description truncates around character ~155–165 on desktop.** 195
  characters. What survives: `Online A-Level Economics tutor for Edexcel,
  AQA, Edexcel B & OCR — 1-to-1 lessons £65/hour, small groups £35/hour.
  First-Class Economics gradu…`. The prices — the thing a parent scans for —
  survive; "6+ years' experience" and the call to action ("Book your free
  intro call") are the parts lost. The description leads with the "online"
  phrasing, matching the query the page already ranks for.
- **Keyword variants, measured across visible text.** "A-Level" (hyphenated)
  8×; "A level" unhyphenated appears once, inside a testimonial quote. The
  exact string "a level economics tutor" as typed (no hyphen) never appears
  outside that quote; the hyphenated form appears in the title, H1 and twice
  in body text. "tuition" twice (subhead "Expert online tuition…" and the
  price FAQ "Specialist A-Level Economics tuition in the UK…") plus the
  title. "tutoring" 8×, "tutor" 22×, "private tutor" 0, "online" 6×. Reads
  naturally; the gaps are the unhyphenated spelling and "private tutor",
  neither of which justifies unnatural insertion — Google treats the
  spellings as close variants.
- **Writing-style finding: em dashes.** The H1 carries one, the meta
  description one, the visible body text 23, the JSON-LD descriptions and
  FAQ answers 6. `00-context/writing-style.md` bans the em dash outright
  (spaced hyphen ` - ` is Eliot's dash). The title is clean (pipes).
- **og:image is the square 1200×1200 logo on a `summary_large_image` card**
  (confirmed: file is 1200×1200 on disk, card declared on the page), so
  shared links crop the logo. Already an OWNER-TODO item (`og-image-wide.png`,
  1200×630); nothing repo-side until the image exists.

### Headings and intent

Section order on a phone: hero (H1, subhead, two CTA buttons, trust line) →
tutor credentials with photo → How It Works → Tutoring Prices → Small Group
Tutoring → Exam Boards → Testimonials → Booking (Calendly) → FAQ. The price
is one tap from the fold ("See Lesson Prices" anchor button in the hero) or
roughly three screens of scroll; the first CTA and the trust line
("100+ students tutored · 6+ years experience · Rated 5/5 on Tutorful") are
above the fold.

Against what a parent or student searching "a level economics tutor" wants
answered, the page covers: cost (pricing section + FAQ, with a market
comparison), who the tutor is and why trust them (credentials box, DBS,
Tutorful link), which boards (its own section), how lessons work (FAQ:
thelessonspace.com), how to start (intro call, three-step section), results
(six testimonial cards, two naming grade outcomes).

**Gaps — things the page does not answer at all:**

1. **Where Eliot is based.** "Somerset" appears nowhere on tutoring.html or
   about.html. One sentence ("based in Somerset, teaching UK-wide online")
   grounds the service for the "near me"/local-intent searcher and is the
   only honest answer this site can give to the "tutor near me" cluster that
   dominates autocomplete (Part 3).
2. **Availability and term-time pattern.** Nothing says when lessons happen
   (after school? weekends? holiday revision?) or whether new students can
   still get a slot for September.
3. **What a parent gets after each lesson.** No mention of feedback,
   homework, or progress reports to parents — the thing that
   distinguishes a tutor from a marketplace slot, and a standard parent
   question. Needs facts from Eliot (what he actually sends).
4. **Why book direct rather than through a marketplace.** The FAQ compares
   price to the market (£40–£90+) but never says the obvious: booking direct
   means the same specialist every week, no platform fee, and dealing with
   the tutor himself.
5. **How a first lesson (not the intro call) runs.** The intro call is well
   covered; what happens in lesson one — diagnostic, a plan, first topic —
   is not, beyond the generic "tailored plan" step card.
6. **Outcomes beyond the testimonial cards.** Two cards name grade
   improvements (C→A, "outstanding grade"). There is no aggregate outcomes
   claim ("most of my students improve by …") — and none can be written
   without facts only Eliot holds.

None of these needs a new section; each is one to three sentences in an
existing section. Drafts are in the proposals file.

### Structured data

Validated: all four blocks parse and carry their required fields (Part 1
table). Checked against Google's current documentation, fetched live
2026-08-25:

- **FAQPage earns nothing and will earn nothing.** Google removed FAQ rich
  results for all sites: the documentation carried a deprecation notice from
  May 2026 ("This feature will no longer appear in Google Search starting
  May 7, 2026") and the feature page has since been removed. The 2023
  restriction the brief mentions was the halfway point; it is now gone for
  everyone. Leaving the markup causes no harm (Google's stated position) and
  removal gains nothing — keep it, expect nothing from it.
- **Review/AggregateRating markup must not be added.** Confirmed from the
  live review-snippet documentation: self-serving reviews ("if the entity
  that's being reviewed controls the reviews about itself… ineligible for
  star review feature") and `Service` is not in the supported-types list.
  The "Rated 5/5 on Tutorful" visible text is fine; marking it up is not.
  This repeats seo/08's 2026-08-08 finding; nothing has changed.
- **LocalBusiness is not available to this business.** `address` (a physical
  postal address) is required and the docs offer nothing for online-only
  service businesses. Not eligible without publishing a home address — do
  not do it.
- **The Person entity exists in full on about.html** — `@id
  about.html#eliot-king`, alumniOf, hasCredential (First-Class BSc,
  University of Bath), sameAs (LinkedIn + Tutorful), worksFor — and
  tutoring.html references it only as a name-and-jobTitle stub inside
  `founder`. Search engines do not resolve `@id` across pages
  (DO-NOT-BREAK, PH04-055), so on the page where the tutor IS the product,
  the credentials are invisible to a parser. Restating the full Person node
  on tutoring.html costs ~15 lines, needs no new facts (every field already
  exists on about.html), and is the one structured-data addition with a
  case. No rich result attaches to it; the value is entity clarity for a
  page whose query is a person-service. Labelled honestly: plausible help,
  no measurable feature.
- **WebPage with dateModified**: absent. Adding it is harmless and signals
  freshness to parsers, but no rich result attaches; low value.
- **Offer extras** (availability, url, priceSpecification): earn no rich
  result on a Service page (Service is not a review/price feature type).
  The one defensible tweak is `UnitPriceSpecification` to say £65 is per
  hour rather than a flat price — semantic correctness, no visible feature.
  Recommend leaving unless touching the block anyway.

### Internal links

Baseline in Part 1. What it means:

- The anchor monoculture 07b §5 guarded against is materially better than
  its 2026-08-10 measurement: 14 distinct in-body anchors, and the 166
  notes topic pages all reach the page as "online A-Level Economics tutor"
  (the D58 tail). The rule that stands is: new links carry new anchors, no
  bulk sweeps.
- **The gap is at the top of the authority ladder, not in the volume.** The
  site's most-linked pages reach tutoring.html only with CTA-button anchors
  that say nothing about the page: `revision-notes/index.html` (271 inbound;
  "Book a Free Intro Call"), `practice-questions/index.html` (174; same),
  `past-paper-questions/index.html` (164; same), `marking.html` (275; same),
  the five past-papers pages ("1-on-1 Tutoring"). Re-anchoring a handful of
  those existing links — not adding links, and each with distinct wording —
  is the one internal-link move left. `revision-notes/index.html` is frozen
  (D50 head; .prettierignore marks the whole file) — its body is proposed
  only as an ask, in the plan's group D.
- **Outbound links are doing their work.** The board cards link both boards'
  notes and all four boards' papers; the FAQ links notes, papers, marking,
  about. Missing: nothing load-bearing. The credentials box already links
  about.html. A glossary or flashcards link would be padding, not use.

### Cannibalisation

What could be checked without Google SERP access (see Part 3 method note):
in the one live index that was queryable, a site-restricted search for the
tutor query returns the HOME page first, then tutoring.html — and that
index still holds the pre-14-August titles, so its snapshot of this site
is stale and the ordering is suggestive, not proof. On-site, the competing
signals are real: `index.html`'s title carries "…Revision Notes &
Tutoring", its H1 "…Revision Notes & Expert Tutoring", and
`about.html`'s title is "About Eliot King | A-Level Economics Tutor …".
The home head is frozen for the September check and about's title is
legitimate for its own page. The available sharpening is therefore: keep
every strong tutor-anchor pointing at tutoring.html (already true — 168
"online A-Level Economics tutor" anchors), add the descriptive re-anchors
above, and make tutoring.html itself the unambiguous tutor page (the
Person node, the Somerset sentence, the direct-booking paragraph).
GSC's Performance report would settle which URL Google actually serves per
query; it is off-limits for this task by instruction, and the September
read will show it anyway.

### Trust signals

Present: named tutor with photo; First-Class BSc (Bath) and A* A-Level;
100+ students, 6+ years; Enhanced DBS (FAQ + credentials list); "Rated 5/5
from 20+ reviews on Tutorful" with two links to the Tutorful profile; six
quoted testimonials with names, roles and outcome captions; professional
background (hedge fund, FinTech).

Weak or missing: **no Google reviews** (the single strongest independent
signal a small site can show; Google Business Profile already in
OWNER-TODO); **no video** (already an OWNER-TODO idea; two of the
individual-tutor sites that rank for board queries lead with one); **no
marked-essay example on this page** (marking.html has two real anonymised
PDFs — a one-line link is repo-side and free); no association memberships
(The Tutors' Association etc. — only if Eliot actually holds one).

### Images and media

One photo (eliot_shirt, properly sized, WebP, alt text correct). What would
earn a place, all owner assets: the 1200×630 og-image (OWNER-TODO);
a Lessonspace lesson screenshot (shows a parent what "online lesson"
actually looks like — none exists on the site); the marked-essay example
(exists already on marking.html — linkable now, embeddable as a thumbnail
with approval); the "meet the tutor" video (OWNER-TODO). Repo work waits on
each asset; the marking-example link is the only one doable today.

### Technical

Clean, as expected after the 23 August pass: canonical correct, no robots
meta, sitemap lastmod 2026-08-24, heading nesting valid, no `href="#"` in
the page's own body, modal buttons fall back to `/contact.html` with JS
off, Calendly has a real no-JS fallback link, form posts natively without
JS (novalidate removed 2026-08-23), Lighthouse 97 with CLS 0.000 (Part 1).
Nothing to do here.

### Layout and conversion

The intent analysis supports one reordering question and one addition, both
conversion work, not ranking work: the price a parent came to check is three
screens down (mitigated by the hero anchor button), and the hero trust line
could carry the two prices ("1-to-1 £65/hour · groups £35/hour") so the
answer is on the first screen. Low risk, but it is a visible-wording change
and rests on Eliot's judgement about leading with price. No other layout
change follows from the search intent; the page's conversion path (two taps
to Calendly from anywhere) is already short.

---

## Part 3 — Phase 2: live search comparison

### Method, stated plainly

**Google's own SERPs could not be fetched.** Four routes were tried on
2026-08-25: plain fetch of google.co.uk (consent wall), google.com with UK
parameters (consent wall), curl with consent cookies from this machine
(Google's JavaScript-required shell), and headless Chrome over CDP with the
consent cookie set (CAPTCHA — "unusual traffic", and repeat attempts extend
the block on this household's IP, so they were stopped). What stands in
place, each labelled where used:

- **Google autocomplete** (suggest API, `hl=en-GB&gl=uk`) — live Google
  data, UK-localised. Used for the query cluster.
- **A live web-search API** (US-localised, not Google's ranker) — used for
  the result-set comparison. Two caveats: ranking order is approximate for
  google.co.uk, and its crawl of THIS site is stale (it still shows the
  pre-14-August titles, e.g. "Expert A-Level Economics Tutor | Online
  Tutoring |…"), so its view of this domain lags the rebuild.
- **Direct fetches of each ranking competitor page** — live, first-hand.
- People Also Ask boxes could not be retrieved at all. The query-cluster
  evidence below substitutes autocomplete plus the questions competitors
  choose to answer.

A two-minute manual check by Eliot of the two main queries in a clean
browser profile would confirm or correct the ordering below; the shape of
the finding (marketplaces vs individual sites) does not depend on it.

### The query cluster (Google autocomplete, UK, 2026-08-25)

- `a level economics tutor` → …tutor **near me**, …tutor **online**,
  …tutor2u, …tutor jobs, …tutor **london**, …tutor **uk**, …tutor
  **birmingham**, …tutor **aqa**
- `online a level economics tutor` → itself; "economics tutor a level near
  me"
- `a level economics tuition` → …tuition **near me**, …tuition singapore,
  …tuition malaysia, then the tutor variants
- **The price variant the brief guessed at does not exist in autocomplete**:
  "a level economics tutor cost" and "how much does an a level economics
  tutor…" return no suggestions at all. The cost question lives in
  competitor FAQs, not in autocomplete.
- `aqa economics tutor` / `edexcel economics tutor` → dominated by
  **tutor2u** and Physics & Maths Tutor resource queries — much of the
  board-query volume is students wanting free resources, not parents
  wanting a tutor.

The cluster the page should cover, in plain terms: near me / UK / London
(location), online, board names, and the cost question. The page already
covers online, boards and cost; it says nothing locational (see Part 2,
gap 1).

### Who ranks (live API results, 2026-08-25; order approximate)

**"a level economics tutor"** — MyTutor (marketplace), Tutorful
(marketplace — where Eliot's own 20+ reviews live), Keystone (agency),
Tutor Hunt (directory), Edumentors (marketplace), PMT Education (agency).
**"online a level economics tutor"** — TutorChase (agency), Tutorful, Tutor
Hunt, Wyzant (US — an artefact of the API's US localisation), Keystone,
A-Level First (agency), Latimer Tuition (agency), one job listing.
**"a level economics tuition"** — Tutorful, Keystone, Tutor Hunt, Hampstead
& Frognal (agency), plus filler.
**"edexcel economics tutor"** (top 5) — tutor2u (resources), Owl Tutors
(agency), Expert Tuition (past-paper resources), tutor2u again,
**a-level-economics-tutor.com (individual tutor)**.
**"aqa economics tutor"** (top 5) — tutor2u, Owl Tutors,
**theeconomicstutor.co.uk (individual)**, **tfurber.com (individual)**,
**a-level-economics-tutor.com / udoecon.com (individual)**.

Attributes of the pages that rank, from direct fetches:

| Page | Type | ~Words | Price | Reviews | Named tutor | Video | FAQ | Booking |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| MyTutor /view-tutors/Economics/A-Level | marketplace, inner | 850 | from £26/hr | per-tutor, e.g. 5/5 (135) | many, with unis | no | yes | message flow |
| Tutorful /search/economics-a-level | marketplace, inner | 1,200 | £31–93/hr | 98% satisfaction + per-tutor | 6 featured | no | yes | find-a-tutor |
| Keystone /tutors/a-level-economics-tutors | agency, inner | 2,800 | none | testimonials, no counts | 20+ with photos | no | yes (3) | contact/phone |
| Tutor Hunt /subjects/economics/levels/a-level/ | directory, inner | 2,500+ | £30–118/hr | "109,419+ five-star" sitewide | 20 profiles | no | no | register first |
| TutorChase /a-level/economics | agency, inner | 1,300 | £30–80/hr | 4.93/5, 925 | first names only | no | yes (2) | multi-step form |
| Edumentors /tutors/economics/a-level | marketplace, inner | 2,500 | £23–52 | Trustpilot + Google badges | 11+ with unis | no | yes | free-trial CTA |
| PMT /tutor/economics | agency, inner | 1,200 | £30–74/hr | per-tutor counts | yes, with unis | no | no | request form |
| tfurber.com AQA page | **individual**, inner | 2,000 | £89/hr | 39 reviews | Cambridge, ex-economist | **yes** | no | contact form |
| udoecon.com | **individual**, home | 2,250 | none | YouTube comments | A*, BBC feature | **yes** | yes (15+) | apply + WhatsApp |
| a-level-economics-tutor.com Edexcel | **individual**, inner | 450 | none | **87+ 5-star Google reviews** | named, since 2017 | no | no | contact link |

### What page 1 has in common that this page lacks

Domain authority, first and everywhere: the two head queries are owned by
marketplaces and agencies whose domains carry thousands of subject pages
and years of national link acquisition — MyTutor, Tutorful, Tutor Hunt,
Keystone. That is not matchable by any on-page change in any timeframe
that matters, and it changes what this plan should put first: the off-site
items. Below the authority gap, the recurring on-page traits this page
lacks are: an independent review count with a named source that Google
itself displays (Tutorful shows Eliot's, but on Tutorful's domain — the
individual sites that rank carry **Google** reviews: 87+ on
a-level-economics-tutor.com); video (both strong individual sites lead
with one); and a choice-of-tutors framing this page rightly cannot offer.
The individual sites that do rank do it on the board and long-tail
queries, with deep single-topic pages (tfurber's AQA page is 2,000 words
on 25-markers and evaluation), named grade outcomes, and Google reviews.

### What this page has that page 1 lacks

A real price on the page (only the marketplaces show prices, as ranges;
none of the ranking individual sites publishes one — £65 flat is unusually
transparent); a named tutor with verifiable credentials on the same page
as the offer (the marketplaces split this across profiles); the free
resource depth behind it (463 pages of notes, papers, questions — no
ranking individual site has an equivalent, and only tutor2u/PMT have more,
as resource sites that do not sell 1-to-1 tutoring on those pages); an
enquiry form that collects board/year/enquirer; and page speed (Lighthouse
97–100 against heavyweight marketplace pages). The page is not thin, not
under-marked-up, and not slow. What it is, is one man's page on a
446-page-deep specialist site competing against national brands for a
head query — which is why the honest ordering in the proposals file puts
Eliot's off-site work first.
