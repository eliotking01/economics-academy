// nav.js - the site navigation, without jQuery.
//
// Wave 4.10. This replaces js/components/inject-templates.js, which was named
// for a job it stopped doing in Wave 2 Phase 7: the header and footer are
// baked into all 463 pages at build time now, and that file had been reduced
// to nav plumbing that still needed jQuery. Together with jquery.min.js
// (164.1 KB, ~40.3 KB gzipped), jquery.dropotron.min.js (10.7 KB) and
// util.js (12.6 KB), it was 188 KB of source and ~45.9 KB of wire on every
// page, in front of the critical path, to open a menu.
//
// What lives here:
//
//   1. The mobile #navPanel and #titleBar, built from #nav at DOMContentLoaded.
//      This is util.js's navList() plugin, inlined - it was the only one of
//      that file's four exports with a caller anywhere on the site.
//   2. The panel's behaviour: toggle, click or tap outside, Escape (which
//      returns focus to the button), and swipe left.
//   3. A progressive enhancement for the desktop dropdowns. The dropdowns
//      themselves are CSS now (css/main.css, "Desktop dropdowns"), so they
//      work with scripting off, which they never did under dropotron. What
//      this adds is the case CSS cannot serve: a touch device wide enough to
//      get the desktop nav, where :hover is not a thing a finger can do.
//
// The panel markup is byte-for-byte what navList() produced - same classes,
// same indent spans, same order, same hrefs, including the href="#" openers.
// docs/audit/scripts/harness/render_nav.py compares the rendered result
// against the jQuery version and it is identical on 10 pages at 2 viewports.

(function () {
  "use strict";

  var DESKTOP = "(min-width: 768px)";

  // --- the mobile panel's link list ------------------------------------
  //
  // util.js's navList(), inlined and unchanged in what it emits. Depth is
  // the number of <li> ancestors minus one, so the top level is 0. jQuery
  // counted with .parents("li"), which walks to the document root; #nav has
  // no <li> above it, so counting to the root and counting to #nav give the
  // same number.

  function depthOf(a) {
    var n = 0;
    var li = a.closest("li");
    while (li) {
      n++;
      li = li.parentElement ? li.parentElement.closest("li") : null;
    }
    return Math.max(0, n - 1);
  }

  function navList(nav) {
    var frag = document.createDocumentFragment();
    var links = nav.querySelectorAll("a");
    for (var i = 0; i < links.length; i++) {
      var src = links[i];
      var d = depthOf(src);
      var a = document.createElement("a");
      a.className = "link depth-" + d;
      // Wave 4.10: the panel had no "you are here" at all - the desktop bar
      // has carried a highlight since the beginning and the mobile one never
      // did. Read off the SAME truth, the class page_shell.PAGE_MAP writes
      // into the page at build time, rather than re-deriving it from the URL
      // and risking a second, disagreeing rule. Direct parent only: the
      // current <li> contains its whole submenu, so `closest` would mark
      // eleven links instead of one.
      if (src.parentElement && src.parentElement.matches("li.current")) {
        a.className += " current";
      }
      // Copied only when present and non-empty, as navList() did: an <a>
      // with no href must not gain href="".
      var target = src.getAttribute("target");
      if (target) a.setAttribute("target", target);
      var href = src.getAttribute("href");
      if (href) a.setAttribute("href", href);
      var indent = document.createElement("span");
      indent.className = "indent-" + d;
      a.appendChild(indent);
      // textContent, not innerHTML: navList() interpolated jQuery's .text()
      // into an HTML string, so "Glossary & Formulae" was re-parsed on the
      // way in. Building the node avoids the round trip and cannot change
      // what a reader sees.
      a.appendChild(document.createTextNode(src.textContent));
      frag.appendChild(a);
    }
    return frag;
  }

  // --- the mobile panel -------------------------------------------------

  function initPanel(nav) {
    var body = document.body;

    // Remove anything an earlier run left, so this is safe to call twice.
    var old = document.getElementById("navPanel");
    if (old) old.remove();
    old = document.getElementById("titleBar");
    if (old) old.remove();

    // A <button>, not <a href="#navPanel">. The anchor form used to collide
    // with util.js's panel() plugin, whose own anchor handler fired on the
    // same click and cancelled the toggle. That was the bug; this is the fix,
    // and it is kept.
    var titleBar = document.createElement("div");
    titleBar.id = "titleBar";
    var btn = document.createElement("button");
    btn.id = "nav-toggle-btn";
    btn.className = "toggle";
    btn.type = "button";
    btn.setAttribute("aria-label", "Open navigation menu");
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-controls", "navPanel");
    titleBar.appendChild(btn);
    body.appendChild(titleBar);

    // A <nav>, so the panel carries its landmark standalone.
    var panel = document.createElement("nav");
    panel.id = "navPanel";
    panel.setAttribute("role", "navigation");
    panel.setAttribute("aria-label", "Mobile navigation");
    panel.setAttribute("aria-hidden", "true");
    panel.appendChild(navList(nav));
    body.appendChild(panel);

    function open() {
      body.classList.add("navPanel-visible");
      panel.setAttribute("aria-hidden", "false");
      btn.setAttribute("aria-expanded", "true");
      btn.setAttribute("aria-label", "Close navigation menu");
    }

    function close() {
      body.classList.remove("navPanel-visible");
      panel.setAttribute("aria-hidden", "true");
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-label", "Open navigation menu");
    }

    function isOpen() {
      return body.classList.contains("navPanel-visible");
    }

    // stopPropagation, or the body handler below closes the panel on the very
    // click that opened it.
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      if (isOpen()) close();
      else open();
    });

    // Anywhere outside the panel and the bar.
    function outside(e) {
      if (isOpen() && !e.target.closest("#navPanel, #titleBar")) close();
    }
    body.addEventListener("click", outside);
    body.addEventListener("touchend", outside);

    panel.addEventListener("click", function (e) { e.stopPropagation(); });
    panel.addEventListener("touchend", function (e) { e.stopPropagation(); });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen()) {
        close();
        btn.focus();
      }
    });

    // Swipe left to close, 50px.
    var startX = null;
    panel.addEventListener("touchstart", function (e) {
      startX = e.touches[0].pageX;
    }, { passive: true });
    panel.addEventListener("touchmove", function (e) {
      if (startX === null) return;
      if (e.touches[0].pageX - startX < -50) {
        startX = null;
        close();
      }
    }, { passive: true });
    panel.addEventListener("touchend", function () { startX = null; });

    return { close: close };
  }

  // --- desktop dropdowns ------------------------------------------------
  //
  // The opening and closing is CSS: :hover and :focus-within on the <li>,
  // in css/main.css. Two things CSS cannot do, and this does:
  //
  //   * A touch device at >=768px gets the desktop nav and has no hover. The
  //     two openers that exist only to open a submenu are already
  //     <a href="#" role="button">, so tapping one does nothing today. Here
  //     it toggles its submenu, which is what role="button" promises.
  //   * Escape closes an open menu and returns focus to its opener.
  //
  // The class is only ever ADDED to what CSS already does, never required by
  // it, so switching this file off leaves working dropdowns.

  function initDropdowns(nav) {
    var openers = nav.querySelectorAll('a[href="#"]');

    function closeAll(except) {
      var open = nav.querySelectorAll("li.nav-open");
      for (var i = 0; i < open.length; i++) {
        if (open[i] !== except) open[i].classList.remove("nav-open");
      }
    }

    for (var i = 0; i < openers.length; i++) {
      openers[i].addEventListener("click", function (e) {
        if (!window.matchMedia(DESKTOP).matches) return;
        var li = e.currentTarget.closest("li");
        if (!li || !li.querySelector("ul")) return;
        e.preventDefault();
        e.stopPropagation();
        var wasOpen = li.classList.contains("nav-open");
        closeAll(li);
        li.classList.toggle("nav-open", !wasOpen);
      });
    }

    document.addEventListener("click", function (e) {
      if (!e.target.closest("#nav")) closeAll(null);
    });

    nav.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      var li = e.target.closest("li.nav-open") ||
               nav.querySelector("li.nav-open");
      if (!li) return;
      closeAll(null);
      var opener = li.querySelector("a");
      if (opener) opener.focus();
    });
  }

  function init() {
    var nav = document.getElementById("nav");
    if (!nav) return;
    initPanel(nav);
    initDropdowns(nav);
  }

  // The header is in the page already - Wave 2 Phase 7 bakes it in - so there
  // is nothing to fetch and nothing to wait for.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
