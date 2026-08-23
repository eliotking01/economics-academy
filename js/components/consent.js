/* Consent - the analytics cookie bar, loaded on every page.
 *
 * Google Analytics is behind a hard gate, not Consent Mode: the <head> of
 * every page defines window.eaLoadAnalytics() (page_shell.GTAG) and calls it
 * only if localStorage["ea-consent"] is "yes". Until a visitor says yes the
 * analytics script is never requested and no analytics cookie is set. This
 * file is the part that asks.
 *
 *   - No stored choice: build the bar, show it on the first scroll or after a
 *     short delay (whichever comes first), so it does not jump in on first
 *     paint mid-read. It sits at the bottom of the viewport, never overlays
 *     or dims anything, and the page stays fully usable behind it. While it
 *     is showing the body gets bottom padding equal to the bar's height so
 *     nothing can be hidden underneath it - the footer links included.
 *   - "That's fine": store "yes", remove the bar, call window.eaLoadAnalytics()
 *     - the same function the <head> calls, so there is one loader, not two.
 *     track.js and flashcards.js test for window.gtag before every event and
 *     simply start working from this point on.
 *   - "No thanks": store "no", remove the bar. It is never shown again.
 *   - Either answer is permanent until changed on /privacy.html, where
 *     #consent-change (a <button>, hidden until this file un-hides it)
 *     clears the stored value and shows the bar again straight away, with
 *     focus on its first button.
 *
 * localStorage is read and written inside try/catch, like quiz.js and
 * flashcards.js: Safari private mode and a blocked storage policy throw,
 * and the right answer then is "ask again next time, send nothing".
 *
 * Accessibility: real <button> elements, role="region" aria-label="Cookies",
 * the site's :focus-visible outline, no animation under
 * prefers-reduced-motion (css/main.css, "Cookie consent bar"). With
 * JavaScript off there is no bar and no analytics, which is the correct
 * outcome rather than a failure.
 *
 * Vanilla, no globals of its own, part of page_shell.SCRIPT_TAIL.
 */

(function () {
  "use strict";

  var KEY = "ea-consent";
  var SHOW_DELAY_MS = 1500;
  var COPY =
    "We'd like to use one analytics cookie to see which pages students " +
    "find useful. Nothing personal is collected either way.";

  var bar = null;

  /* ------------------------------------------------------------ storage */

  function stored() {
    try {
      return window.localStorage.getItem(KEY);
    } catch (e) {
      return null;
    }
  }

  function store(value) {
    try {
      if (value === null) {
        window.localStorage.removeItem(KEY);
      } else {
        window.localStorage.setItem(KEY, value);
      }
    } catch (e) {
      /* Storage unavailable: the bar will ask again next time. */
    }
  }

  /* ---------------------------------------------------------------- bar */

  function build() {
    if (bar) return bar;
    bar = document.createElement("div");
    bar.id = "consent";
    bar.className = "consent";
    bar.setAttribute("role", "region");
    bar.setAttribute("aria-label", "Cookies");

    var inner = document.createElement("div");
    inner.className = "consent-inner";

    var text = document.createElement("p");
    text.className = "consent-text";
    text.textContent = COPY;

    var actions = document.createElement("div");
    actions.className = "consent-actions";
    actions.appendChild(button("yes", "That's fine"));
    actions.appendChild(button("no", "No thanks"));

    var more = document.createElement("a");
    more.className = "consent-more";
    more.href = "/privacy.html";
    more.textContent = "More in our privacy policy ";
    var arrow = document.createElement("span");
    arrow.setAttribute("aria-hidden", "true");
    arrow.textContent = "→";
    more.appendChild(arrow);
    actions.appendChild(more);

    inner.appendChild(text);
    inner.appendChild(actions);
    bar.appendChild(inner);
    bar.addEventListener("click", onChoice);
    document.body.appendChild(bar);
    return bar;
  }

  function button(value, label) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "consent-button";
    b.setAttribute("data-consent", value);
    b.textContent = label;
    return b;
  }

  // Keep the page's last lines reachable while the bar is up: pad the body
  // by the bar's rendered height, and keep that true across resizes.
  function reserveSpace() {
    if (bar && bar.parentNode) {
      document.body.style.paddingBottom = bar.offsetHeight + "px";
    }
  }

  function show(focusFirst) {
    build();
    if (!bar.classList.contains("is-visible")) {
      // Two frames, so the transition runs from the off-screen position on
      // browsers that would otherwise coalesce the insert and the class.
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          if (bar) bar.classList.add("is-visible");
          reserveSpace();
        });
      });
      window.addEventListener("resize", reserveSpace);
    }
    if (focusFirst) {
      var first = bar.querySelector("button");
      if (first) first.focus();
    }
  }

  function hide() {
    if (!bar) return;
    window.removeEventListener("resize", reserveSpace);
    document.body.style.paddingBottom = "";
    if (bar.parentNode) bar.parentNode.removeChild(bar);
    bar = null;
  }

  function onChoice(event) {
    var target = event.target;
    while (target && target !== bar && !target.getAttribute("data-consent")) {
      target = target.parentNode;
    }
    if (!target || target === bar) return;
    var choice = target.getAttribute("data-consent");
    store(choice);
    hide();
    if (choice === "yes" && typeof window.eaLoadAnalytics === "function") {
      window.eaLoadAnalytics();
    }
  }

  /* ----------------------------------------------------- first visit */

  function askLater() {
    var asked = false;
    function ask() {
      if (asked) return;
      asked = true;
      window.removeEventListener("scroll", ask);
      show(false);
    }
    window.addEventListener("scroll", ask, { passive: true });
    window.setTimeout(ask, SHOW_DELAY_MS);
  }

  /* ------------------------------------------------ privacy.html control */

  function wireChangeControl() {
    var control = document.getElementById("consent-change");
    if (!control) return;
    var wrap = document.getElementById("consent-change-wrap");
    if (wrap) wrap.hidden = false;
    control.addEventListener("click", function () {
      store(null);
      show(true);
    });
  }

  function init() {
    wireChangeControl();
    var choice = stored();
    if (choice !== "yes" && choice !== "no") askLater();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
