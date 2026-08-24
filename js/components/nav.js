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
//   1. The mobile drawer (2026-08-24, PR #26). The menu itself is the baked
//      #mobileNav block in every header - grouped links in native <details>,
//      complete with scripting off. This file only ENHANCES it: builds the
//      fixed title bar, burger and backdrop, turns the in-flow block into
//      the sliding drawer, opens the current page's group, traps focus while
//      open (inert on everything else) and returns it to the burger on
//      close. If this file never runs, the phone visitor still has the whole
//      menu - which the old panel, generated from #nav at runtime, did not
//      give them.
//   2. A progressive enhancement for the desktop dropdowns. The dropdowns
//      themselves are CSS (css/main.css, "Desktop dropdowns"), so they
//      work with scripting off. What this adds is the case CSS cannot serve:
//      a touch device wide enough to get the desktop nav, where :hover is
//      not a thing a finger can do.

(function () {
  "use strict";

  var DESKTOP = "(min-width: 768px)";

  // --- the mobile drawer --------------------------------------------------

  function initDrawer() {
    var body = document.body;
    var mnav = document.getElementById("mobileNav");
    if (!mnav) return;
    var root = mnav.querySelector(".mnav-root");

    // Remove anything an earlier run left, so this is safe to call twice.
    var old = document.getElementById("titleBar");
    if (old) old.remove();
    old = document.getElementById("navBackdrop");
    if (old) old.remove();
    old = mnav.querySelector(".mnav-head");
    if (old) old.remove();
    body.classList.remove("navPanel-visible");

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
    btn.setAttribute("aria-controls", "mobileNav");
    titleBar.appendChild(btn);
    var wordmark = document.createElement("a");
    wordmark.className = "titleBar-wordmark";
    wordmark.href = "/";
    wordmark.textContent = "Economics Academy";
    titleBar.appendChild(wordmark);
    body.appendChild(titleBar);

    var backdrop = document.createElement("div");
    backdrop.id = "navBackdrop";
    body.appendChild(backdrop);

    // The drawer head: "Menu" and a close control (fa-plus rotated by CSS -
    // no new glyph in the subset).
    var head = document.createElement("div");
    head.className = "mnav-head";
    var label = document.createElement("span");
    label.className = "mnav-head-label";
    label.textContent = "Menu";
    var closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "mnav-close";
    closeBtn.setAttribute("aria-label", "Close menu");
    var glyph = document.createElement("span");
    glyph.className = "icon solid fa-plus";
    glyph.setAttribute("aria-hidden", "true");
    closeBtn.appendChild(glyph);
    head.appendChild(label);
    head.appendChild(closeBtn);
    mnav.insertBefore(head, mnav.firstChild);

    // The drawer must live at body level: the focus trap below makes
    // #page-wrapper inert while the drawer is open, and the baked block
    // starts INSIDE the wrapper - left there, the trap would inert the
    // drawer itself and every link in it would be dead. The old panel was
    // a body child for the same reason. track.js excludes #mobileNav from
    // cta_click alongside the other chrome.
    body.appendChild(mnav);

    // The static block's own "Menu" summary hands over to the burger; the
    // root details stays open so the sheet is the drawer's content.
    if (root) root.open = true;

    // Current page, from the baked data-mnav-current marker
    // (page_shell._block(), the same single truth as the desktop bar's
    // li.current): open its group, and say so to assistive tech.
    var currentGroup = mnav.querySelector("details[data-mnav-current]");
    if (currentGroup) currentGroup.open = true;
    var currentLink = mnav.querySelector("a[data-mnav-current]");
    if (currentLink) currentLink.setAttribute("aria-current", "page");

    // `inert`, not aria-hidden="true". The drawer is moved off-canvas by
    // transform, never display:none - the slide has to be animatable - so
    // without inert its links would stay in the tab order the whole time,
    // and ARIA 1.2 makes aria-hidden="true" over focusable descendants a
    // conformance failure. inert does both jobs. REVIEW-NOTES.md item 1.
    mnav.setAttribute("inert", "");
    body.classList.add("mnav-enhanced");

    // Focus trap: while the drawer is open, everything else at body level
    // goes inert, so Tab can only reach the drawer and the title bar.
    function setPageInert(on) {
      var children = body.children;
      for (var i = 0; i < children.length; i++) {
        var el = children[i];
        if (el === mnav || el === titleBar || el === backdrop) continue;
        if (el.tagName === "SCRIPT" || el.tagName === "STYLE") continue;
        if (on) el.setAttribute("inert", "");
        else el.removeAttribute("inert");
      }
    }

    function open() {
      body.classList.add("navPanel-visible");
      mnav.removeAttribute("inert");
      setPageInert(true);
      btn.setAttribute("aria-expanded", "true");
      btn.setAttribute("aria-label", "Close navigation menu");
      closeBtn.focus();
    }

    function close() {
      body.classList.remove("navPanel-visible");
      mnav.setAttribute("inert", "");
      setPageInert(false);
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-label", "Open navigation menu");
      btn.focus();
    }

    function isOpen() {
      return body.classList.contains("navPanel-visible");
    }

    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      if (isOpen()) close();
      else open();
    });

    closeBtn.addEventListener("click", function () {
      close();
    });

    backdrop.addEventListener("click", function () {
      close();
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen()) close();
    });

    // Swipe left to close, 50px.
    var startX = null;
    mnav.addEventListener("touchstart", function (e) {
      startX = e.touches[0].pageX;
    }, { passive: true });
    mnav.addEventListener("touchmove", function (e) {
      if (startX === null) return;
      if (e.touches[0].pageX - startX < -50) {
        startX = null;
        close();
      }
    }, { passive: true });
    mnav.addEventListener("touchend", function () { startX = null; });

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
    initDrawer();
    var nav = document.getElementById("nav");
    if (nav) initDropdowns(nav);
  }

  // The header is in the page already - Wave 2 Phase 7 bakes it in - so there
  // is nothing to fetch and nothing to wait for.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
