# Paid content — where it lives and how a buyer gets it

Design note, 2026-11-28 (health check, item 12). **Options and a
recommendation for Eliot to decide. Nothing is built.** Not legal or tax
advice: the VAT points below are what the public guidance says, to be
confirmed with an accountant before the first sale.

## The constraints

1. **This repo is public, so paid files can never be in it** — not in an
   excluded directory, not behind a flag. `_config.yml` keeps a file off
   GitHub Pages; it does not keep it off GitHub. `flashcards-data/CLAUDE.md`
   already says so. Checked 2026-11-28: no card carries `premium: true`
   today, so nothing paid has leaked.
2. **The free site keeps no runtime dependency and works with JavaScript
   off.** Buying must not add a script, an embed or a third-party origin to
   the free pages; a plain link out is fine.
3. **EU VAT is owed from the first sale.** For e-books and other digital
   downloads sold to EU consumers, the place of supply is where the buyer
   lives, and there is no threshold for a UK seller. Selling directly means
   registering for the EU's non-Union One Stop Shop in one member state (or
   for VAT in each country sold to), charging each country's rate, keeping
   two pieces of evidence of the buyer's location, and filing quarterly. UK
   sales below the £90,000 UK registration threshold carry no UK VAT for an
   unregistered sole trader. A **merchant of record** (MoR) is the legal
   seller instead: it charges, files and pays the VAT, and Eliot receives a
   payout.
4. **Paid practice questions must be 100% original** (CLAUDE.md rule 4) and
   never share a data path with the past-paper bank.

## Where the files live

**A separate, private repository** (for example `economics-academy-premium`)
holds the sources and whatever builds the sellable files. That is the only
answer constraint 1 leaves. It can import this repo's scripts (the KaTeX
renderer, the diagram SVGs) as a read-only dependency, but nothing flows
back. If premium flashcards are ever written, they live there, not in
`flashcards-data/` with a flag.

The finished files (PDFs, a ZIP of a question pack) are uploaded to the
storefront, which hosts and delivers them. The free site links to each
product page with an ordinary `<a href>`, as `marking.html` links to Stripe
today.

## How a buyer gets them — the options

Fees checked 2026-11-28 from the sources listed at the end; most are
third-party summaries, so confirm on each provider's own pricing page.

| Option | Who owes the VAT | Fee (headline) | Delivers files? | Fit |
| --- | --- | --- | --- | --- |
| **A. Payhip** | Payhip handles EU and UK digital VAT by default | 5% on the free plan; 2% / 0% on paid plans | Yes, built in | **Recommended** |
| B. Gumroad | Gumroad, as merchant of record since 1 Jan 2025 | 10% + $0.50 per sale, plus card processing | Yes, built in | Good, dearer |
| C. Stripe Managed Payments | Stripe, as merchant of record | 3.5% on top of normal Stripe fees | **No** file delivery | Needs a delivery service built |
| D. Paddle | Paddle, as merchant of record | 5% + $0.50 | No | Built for software; overkill |
| E. Stripe Payment Links, as today | **Eliot**, from the first EU sale | Stripe fees only | No | Not recommended |
| — Lemon Squeezy | — | — | — | **Closing**: sign-ups ended 16 Nov 2026, payments stop 31 Mar 2027 |

**Why A.** It is the only option that is both a merchant of record for EU
and UK digital VAT and a file-delivery store, at the lowest fee on the
smallest plan, with no monthly cost until sales justify one. The buyer
pays on Payhip's page, downloads at once, and gets a receipt and a VAT
invoice from Payhip; Eliot gets payouts and no VAT returns. The free site
changes by a link.

**Caveats on A.** Payhip's VAT handling covers EU and UK VAT only; US,
Canadian and Australian sales tax stay the seller's (for a UK A-level
product, rarely relevant). Its default VAT handling can be switched off in
settings, and must not be. How it treats UK VAT for a seller who is not
UK-registered is worth one question to Payhip before launch.

**Why not C, even though it keeps everything in Stripe.** Managed Payments
would be the cleanest tax story, but it does not deliver files, so a
private bucket plus a small server issuing signed download links would
have to be built and run: a runtime service, which is the thing this site
has avoided. Worth revisiting if Stripe adds delivery.

**Why not E.** The fees are lowest, but Eliot becomes liable for EU VAT
from the first sale, with the OSS registration, quarterly returns and
location evidence above — and still has no file delivery.

## Not in scope: paid content inside the site

Premium flashcards or question sets that run *in* the site (a logged-in
student sees more cards) need accounts, a server and gated data — a
separate application, not this static site. If it is ever wanted, it
belongs on its own subdomain, with the free site still linking to it with
a plain link. Start with downloads.

## If A is chosen, the first steps

1. Ask Payhip how it treats UK VAT for a non-registered UK seller.
2. Create the private repo; move nothing paid into this one.
3. One product, one link from the relevant free page, `Text-Change:` on
   that page; `privacy.html` needs no change for a plain outbound link.

## Sources (checked 2026-11-28)

- Lemon Squeezy's own wind-down notice: <https://docs.lemonsqueezy.com/migration>
- Payhip on EU/UK VAT: <https://payhip.com/eu-vat>, <https://help.payhip.com/article/127-digital-eu-vat>
- Stripe Managed Payments: <https://stripe.com/en-ch/managed-payments>
- Paddle pricing: <https://www.paddle.com/pricing>
- Gumroad fees (third-party summary): <https://checkoutpage.com/blog/gumroad-fees>
- HMRC, digital services to consumers: <https://www.gov.uk/guidance/the-vat-rules-if-you-supply-digital-services-to-private-consumers>
