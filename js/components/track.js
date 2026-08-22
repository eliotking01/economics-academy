/* Track - GA4 conversion events, loaded on every page.
 *
 * Until this file the only custom events on the site were the flashcard
 * player's (deck_start, card_flip, card_rated, deck_complete, deck_print in
 * flashcards.js). Nothing fired when a visitor did anything that makes money.
 * This file fires exactly these, through the same track() helper as
 * flashcards.js, which no-ops silently when window.gtag is absent (ad blocker,
 * GA blocked, script order):
 *
 *   begin_checkout     click on a Stripe payment link (a[href*="buy.stripe.com"],
 *                      the eight .marking-buy buttons on marking.html).
 *                      currency "GBP", value, items[{item_name, item_category
 *                      "marking", item_variant "48-hour"|"next-day", price,
 *                      quantity 1}] - all read from the link's data-package,
 *                      data-turnaround and data-price attributes, never from
 *                      the button text. Also stashes {package, turnaround,
 *                      price, ts} in sessionStorage["ea-checkout"] so the
 *                      purchase below can be attributed.
 *   purchase           on /confirmation.html load, where Stripe sends the
 *                      customer after paying (dashboard, 2026-08-16). Stripe
 *                      payment links carry nothing in the return URL, so the
 *                      package comes from the ea-checkout stash: currency
 *                      "GBP", value, transaction_id "ea-"+ts, items as above.
 *                      Stash absent (page opened cold): value 0, item_name
 *                      "unknown", so the hit is counted but obviously
 *                      unattributed. Once per page view; a refresh of the
 *                      same tab sends nothing rather than a second "unknown".
 *   generate_lead      a Formspree form accepted the submission. The two
 *                      inline form scripts (tutoring.html #enquiryForm,
 *                      contact.html #contact-form) dispatch
 *                      CustomEvent("ea:lead", {detail:{type}}) on document
 *                      after response.ok and nowhere else, so spam and
 *                      failures never count. lead_type "tutoring_enquiry" |
 *                      "contact_form".
 *   intro_call_booked  Calendly's postMessage "calendly.event_scheduled" from
 *                      origin https://calendly.com, once per page. Custom
 *                      name: GA4 has no recommended event for this.
 *   sign_up            submit of the Kit newsletter form on index.html
 *                      (action app.kit.com). The form posts natively and
 *                      leaves the page, so this fires on submit; gtag sends
 *                      with sendBeacon, which survives the navigation.
 *                      method "newsletter".
 *   cta_click          click on an in-content link to /tutoring.html,
 *                      /marking.html or /contact.html (any fragment), EXCLUDING
 *                      the header nav, mobile nav and footer (#header, #nav,
 *                      #navPanel, #titleBar, #footer). cta_text (trimmed, max
 *                      60 chars), cta_target (the path). Links to the page
 *                      the visitor is already on do not count - href="#" on
 *                      tutoring.html resolves to /tutoring.html#. This is the
 *                      event that says which free resource sends people to
 *                      the paid pages.
 *
 * Every event also carries page_path (location.pathname). Nothing personal is
 * ever sent: no names, emails, messages or form fields.
 *
 * Outbound clicks (Tutorful, LinkedIn) are deliberately NOT here: GA4 Enhanced
 * Measurement logs them as `click` with link_url on its own.
 *
 * Nothing here blocks or delays the visitor. Listeners are delegated on
 * document in the capture phase, the event is fired, and the default action
 * (navigation, form post) proceeds untouched - no preventDefault, no
 * event_callback. With JavaScript off the forms post natively to Formspree
 * and Kit and the Stripe links still work; no event fires, which is accepted.
 *
 * Vanilla, no jQuery, part of the page_shell.SCRIPT_TAIL on all 463 pages.
 */

(function () {
  "use strict";

  var CHECKOUT_KEY = "ea-checkout";
  var PURCHASE_SENT_KEY = "ea-purchase-sent";
  var CTA_TARGETS = { "/tutoring.html": 1, "/marking.html": 1, "/contact.html": 1 };
  var EXCLUDED_CHROME = "#header, #nav, #navPanel, #titleBar, #footer";
  var MAX_CTA_TEXT = 60;

  /* ----------------------------------------------------------- analytics */

  // Copied from flashcards.js: every call is a no-op when gtag is missing.
  function track(name, params) {
    if (typeof window.gtag === "function") {
      window.gtag("event", name, params || {});
    }
  }

  function withPage(params) {
    params.page_path = window.location.pathname;
    return params;
  }

  /* ------------------------------------------------------------- storage */

  // sessionStorage, not localStorage: the checkout stash only has to survive
  // the round trip to Stripe and back in the same tab. Guarded like the other
  // components' storage - it throws outright in some privacy modes.
  function readStash(key) {
    try {
      var raw = window.sessionStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function writeStash(key, value) {
    try {
      window.sessionStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      /* storage unavailable: the purchase will be counted as unattributed */
    }
  }

  function removeStash(key) {
    try {
      window.sessionStorage.removeItem(key);
    } catch (e) {
      /* nothing to do */
    }
  }

  /* ------------------------------------------------------------- helpers */

  function closest(node, selector) {
    if (!node || typeof node.closest !== "function") return null;
    return node.closest(selector);
  }

  function toNumber(value) {
    var n = parseFloat(value);
    return isNaN(n) ? 0 : n;
  }

  function marketingItem(pkg, turnaround, price) {
    return {
      item_name: pkg,
      item_category: "marking",
      item_variant: turnaround,
      price: price,
      quantity: 1,
    };
  }

  /* ------------------------------------------------- 1. begin_checkout */

  function onStripeClick(link) {
    var pkg = link.getAttribute("data-package") || "unknown";
    var turnaround = link.getAttribute("data-turnaround") || "unknown";
    var price = toNumber(link.getAttribute("data-price"));
    var ts = Date.now();

    writeStash(CHECKOUT_KEY, {
      package: pkg,
      turnaround: turnaround,
      price: price,
      ts: ts,
    });
    // A fresh checkout supersedes any earlier purchase in this tab.
    removeStash(PURCHASE_SENT_KEY);

    track(
      "begin_checkout",
      withPage({
        currency: "GBP",
        value: price,
        items: [marketingItem(pkg, turnaround, price)],
      })
    );
  }

  /* ------------------------------------------------------ 2. purchase */

  function isConfirmationPage() {
    var path = window.location.pathname;
    return path === "/confirmation.html" || path === "/confirmation";
  }

  function sendPurchase() {
    var stash = readStash(CHECKOUT_KEY);
    if (stash && typeof stash === "object") {
      var price = toNumber(stash.price);
      var id = "ea-" + stash.ts;
      track(
        "purchase",
        withPage({
          currency: "GBP",
          value: price,
          transaction_id: id,
          items: [
            marketingItem(
              stash.package || "unknown",
              stash.turnaround || "unknown",
              price
            ),
          ],
        })
      );
      removeStash(CHECKOUT_KEY);
      writeStash(PURCHASE_SENT_KEY, id);
      return;
    }
    // Already sent for this tab (the visitor refreshed the thank-you page):
    // GA4 would dedupe a repeated transaction_id, but an "unknown" purchase
    // here would be a phantom, so send nothing.
    if (readStash(PURCHASE_SENT_KEY)) return;
    // Opened cold, or storage unavailable: count it, visibly unattributed.
    // A timestamp id keeps separate cold opens from being deduped into one.
    track(
      "purchase",
      withPage({
        currency: "GBP",
        value: 0,
        transaction_id: "ea-unattributed-" + Date.now(),
        items: [marketingItem("unknown", "unknown", 0)],
      })
    );
  }

  /* -------------------------------------------------- 3. generate_lead */

  function onLead(e) {
    var detail = e && e.detail;
    var type = detail && typeof detail.type === "string" ? detail.type : "unknown";
    track("generate_lead", withPage({ lead_type: type }));
  }

  /* ---------------------------------------------- 4. intro_call_booked */

  var callBooked = false;

  function onMessage(e) {
    if (e.origin !== "https://calendly.com") return;
    var data = e.data;
    if (!data || data.event !== "calendly.event_scheduled") return;
    if (callBooked) return;
    callBooked = true;
    track("intro_call_booked", withPage({ method: "calendly" }));
  }

  /* ------------------------------------------------------- 5. sign_up */

  function onSubmit(e) {
    var form = closest(e.target, "form");
    if (!form) return;
    var action = form.getAttribute("action") || "";
    if (action.indexOf("app.kit.com/forms/") === -1) return;
    track("sign_up", withPage({ method: "newsletter" }));
  }

  /* ----------------------------------------------------- 6. cta_click */

  function onCtaClick(link) {
    if (closest(link, EXCLUDED_CHROME)) return;
    if (link.origin !== window.location.origin) return;
    if (!CTA_TARGETS.hasOwnProperty(link.pathname)) return;
    // Not a link to the page the visitor is already on: tutoring.html's
    // "Enquire Now" buttons are href="#", which resolves to /tutoring.html#,
    // and an in-page anchor does not send anyone towards anything.
    if (link.pathname === window.location.pathname) return;
    var text = (link.textContent || "").replace(/\s+/g, " ").trim();
    track(
      "cta_click",
      withPage({
        cta_text: text.slice(0, MAX_CTA_TEXT),
        cta_target: link.pathname,
      })
    );
  }

  /* ------------------------------------------------------------ wiring */

  function onClick(e) {
    var link = closest(e.target, "a[href]");
    if (!link) return;
    if ((link.getAttribute("href") || "").indexOf("buy.stripe.com") !== -1) {
      onStripeClick(link);
      return;
    }
    onCtaClick(link);
  }

  // Capture phase, so a page script that stops propagation cannot hide a
  // click or a submit from the tracker. Nothing here calls preventDefault.
  document.addEventListener("click", onClick, true);
  document.addEventListener("submit", onSubmit, true);
  document.addEventListener("ea:lead", onLead);
  window.addEventListener("message", onMessage);

  if (isConfirmationPage()) sendPurchase();
})();
