/* Turnstile - the Cloudflare bot check in front of the site's two Formspree
 * forms. Loaded ONLY by contact.html and tutoring.html; both are named in
 * verify_page_shell.EXTRA_SCRIPT_PAGES, alongside the api.js tag itself.
 *
 * WHY THIS EXISTS. From ~13 September 2026 both forms took a burst of
 * SQL-injection probes from an automated scanner: one poisoned parameter per
 * request, every other field empty, all seven preferred_days boxes ticked.
 * That shape is a direct POST to the Formspree endpoint, not a browser, so
 * every client-side defence the forms had - the _gotcha honeypot included -
 * was bypassed by construction. A token check is the only defence that runs
 * on Formspree's side: no valid cf-turnstile-response, no submission,
 * whatever the client did. The endpoint IDs were rotated in the same commit.
 *
 * WHY EXPLICIT RENDERING rather than the one-line implicit widget. The
 * tutoring form lives in a modal that is display:none until a button opens
 * it. Turnstile renders on api.js load, and a widget rendered into a
 * zero-layout container is the documented way to get a blank box. So api.js
 * is loaded with ?render=explicit&onload=eaTurnstileReady and the widget is
 * rendered when its container is actually on screen: straight away on
 * contact.html, on modal open on tutoring.html. It also means the 300-second
 * token starts when the visitor reaches the form, not when the page loaded.
 *
 * THE CONTRACT, as data attributes on the .cf-turnstile container:
 *   data-sitekey       the public Site Key (CLAUDE.md rule 8: the SECRET key
 *                      lives in the Formspree dashboard and never in here)
 *   data-ea-note       id of the <p> this file writes its status line into
 *   data-ea-mount      "manual" to wait for eaTurnstile.mount(); anything
 *                      else (or absent) renders on DOMContentLoaded
 *
 * and as two globals:
 *   window.eaTurnstileReady()   api.js's onload callback. Global because
 *                               api.js looks it up by name on window.
 *   window.eaTurnstile          { mount, reset, isTokenError }
 *
 * EVERY SUBMISSION MUST CALL reset(). Tokens are single-use: a second enquiry
 * in the same page visit fails without it. Both pages call it last in their
 * fetch handler's finally block, after re-enabling their own button, because
 * reset() disables the button again while the next token is fetched.
 *
 * PROGRESSIVE ENHANCEMENT. This is the site's one documented exception to the
 * JS-off rule (CLAUDE.md, 2026-09-15). Both forms now need JavaScript; the
 * JS-off route is the <noscript> block beside each form, which gives the
 * email address. Do not extend the exception to any other page.
 *
 * Vanilla, no dependencies, one widget per page by design.
 */

(function () {
  "use strict";

  /* The three visible strings this file owns. The per-page submit-time
     messages stay in their own pages, in that page's punctuation style. */
  var WAITING =
    "Just checking you're not a bot. The send button turns on once that's done.";
  var FAILED =
    "The bot check couldn't load. Reload the page and try again, or email " +
    "eliotkingtuition@gmail.com and I'll pick it up from there.";

  var host = null; // the .cf-turnstile container
  var form = null;
  var submit = null;
  var note = null; // the <p> named by data-ea-note
  var widgetId = null;
  var apiReady = false;
  var wanted = false; // mount() was called before api.js arrived

  /* ------------------------------------------------------------- states */

  function say(text, isError) {
    if (!note) return;
    note.textContent = text;
    note.className = isError
      ? "turnstile-note turnstile-note-error"
      : "turnstile-note";
  }

  function waiting() {
    if (submit) submit.disabled = true;
    say(WAITING, false);
  }

  function ready() {
    if (submit) submit.disabled = false;
    say("", false);
  }

  function failed() {
    if (submit) submit.disabled = true;
    say(FAILED, true);
  }

  /* ------------------------------------------------------------ widget */

  function render() {
    if (widgetId !== null || !window.turnstile || !host) return;
    widgetId = window.turnstile.render(host, {
      sitekey: host.getAttribute("data-sitekey"),
      callback: ready,
      "error-callback": failed,
      "expired-callback": waiting,
      "timeout-callback": waiting,
    });
  }

  function mount() {
    wanted = true;
    if (apiReady) render();
  }

  function reset() {
    if (widgetId === null || !window.turnstile) return;
    window.turnstile.reset(widgetId);
    waiting();
  }

  /* Did Formspree reject this submission over the token rather than over
     anything the visitor typed? Its error payload is JSON; the shape has
     varied, so both the flat and the per-field forms are read, and anything
     unrecognised answers false so the page falls back to its existing
     generic message. Takes the already-read response BODY, not the
     Response - a body can only be read once and the caller may want it. */
  function isTokenError(body) {
    if (!body) return false;
    var text = "";
    if (typeof body === "string") {
      text = body;
    } else {
      if (body.error) text += " " + body.error;
      if (body.message) text += " " + body.message;
      var errors = body.errors;
      if (errors && errors.length) {
        for (var i = 0; i < errors.length; i++) {
          var e = errors[i];
          text += " " + (typeof e === "string" ? e : e.message || e.code || "");
        }
      }
    }
    return /captcha|turnstile|challenge/i.test(text);
  }

  /* ------------------------------------------------------------ globals */

  // api.js calls this by name, so it has to be on window and it has to be
  // defined before api.js executes. This file's <script> tag is a plain
  // blocking one and sits above api.js in the source, which guarantees it.
  window.eaTurnstileReady = function () {
    apiReady = true;
    if (wanted) render();
  };

  window.eaTurnstile = {
    mount: mount,
    reset: reset,
    isTokenError: isTokenError,
  };

  /* --------------------------------------------------------------- init */

  function init() {
    host = document.querySelector(".cf-turnstile");
    if (!host) return;
    form = host.closest("form");
    if (!form) return;
    submit = form.querySelector('[type="submit"]');
    note = document.getElementById(host.getAttribute("data-ea-note"));
    // Disabled from the first frame, not from the first callback: the gap
    // between them is exactly when a keyboard user reaches the button.
    waiting();
    if (host.getAttribute("data-ea-mount") !== "manual") mount();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
