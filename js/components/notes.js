/* Notes - the topic pages' enhancements, loaded (defer) only by the 166
 * generated revision-notes topic pages, as their family's extra script.
 *
 * Progressive enhancement throughout: every element this file shows is also
 * CREATED by it, so a page with JavaScript off carries no dead control -
 * the mock this was promoted from (_working/notes-redesign/) proved the
 * no-JS page identical minus these. Nothing here delivers content.
 *
 *   - Reading progress: a 3px bar across the top of the viewport, skipped
 *     entirely under prefers-reduced-motion.
 *   - Back to top: appears after two screens of scroll; smooth scroll is
 *     gated on the same media query.
 *   - Contents-rail scrollspy: highlights the current section's link in the
 *     "On this page" rail (the rail itself is CSS-placed; this only adds
 *     the .is-current class).
 *   - Mark as revised: one button after the last section, state in
 *     localStorage under "ea-revised:<pathname>" - the flashcards' "saved
 *     on this device" idiom. Reads and writes are inside try/catch, like
 *     quiz.js and consent.js: Safari private mode and a blocked storage
 *     policy throw, and the right answer then is a button that still
 *     toggles for the session and simply forgets.
 *   - Diagram lightbox: upgrades each generated <a class="diagram-zoom">
 *     (a working open-the-PNG link without JS) to a native <dialog>, which
 *     brings Esc, backdrop click and focus handling for free.
 */
(function () {
  "use strict";
  var main = document.querySelector("main.revision-notes-content");
  if (!main) return;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Reading progress bar */
  if (!reduced) {
    var bar = document.createElement("div");
    bar.className = "topic-progress";
    bar.setAttribute("aria-hidden", "true");
    document.body.appendChild(bar);
    var onScroll = function () {
      var doc = document.documentElement;
      var max = doc.scrollHeight - window.innerHeight;
      bar.style.transform =
        "scaleX(" + (max > 0 ? Math.min(1, doc.scrollTop / max) : 0) + ")";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* Back to top */
  var top = document.createElement("button");
  top.type = "button";
  top.className = "topic-top";
  top.setAttribute("aria-label", "Back to top");
  top.textContent = "↑";
  document.body.appendChild(top);
  top.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" });
  });
  var toggleTop = function () {
    top.classList.toggle("is-visible", window.scrollY > window.innerHeight * 2);
  };
  window.addEventListener("scroll", toggleTop, { passive: true });
  toggleTop();

  /* Contents rail scrollspy */
  var links = main.querySelectorAll(".topic-contents__list a[href^='#']");
  if ("IntersectionObserver" in window && links.length) {
    var byId = {};
    Array.prototype.forEach.call(links, function (a) {
      byId[a.hash.slice(1)] = a;
    });
    var current = null;
    var spy = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            if (current) current.classList.remove("is-current");
            current = byId[e.target.id];
            if (current) current.classList.add("is-current");
          }
        });
      },
      { rootMargin: "0px 0px -70% 0px" }
    );
    Object.keys(byId).forEach(function (id) {
      var h = document.getElementById(id);
      if (h) spy.observe(h);
    });
  }

  /* Mark as revised */
  var lastSection = null;
  var sections = main.querySelectorAll(".notes-container > section");
  if (sections.length) lastSection = sections[sections.length - 1];
  if (lastSection) {
    var key = "ea-revised:" + location.pathname;
    var wrap = document.createElement("div");
    wrap.className = "topic-revised";
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "topic-revised__button";
    var note = document.createElement("p");
    note.className = "topic-revised__note";
    note.textContent = "Saved on this device, like your flashcard progress.";
    var render = function (done) {
      btn.setAttribute("aria-pressed", done ? "true" : "false");
      btn.textContent = done ? "✓ Revised" : "Mark as revised";
    };
    var read = function () {
      try {
        return localStorage.getItem(key) !== null;
      } catch (e) {
        return false;
      }
    };
    btn.addEventListener("click", function () {
      var done = read();
      try {
        if (done) localStorage.removeItem(key);
        else localStorage.setItem(key, new Date().toISOString().slice(0, 10));
      } catch (e) {}
      render(!done);
    });
    render(read());
    wrap.appendChild(btn);
    wrap.appendChild(note);
    lastSection.parentNode.insertBefore(wrap, lastSection.nextSibling);
  }

  /* Diagram lightbox on the generated .diagram-zoom links */
  if (window.HTMLDialogElement) {
    var zooms = main.querySelectorAll("a.diagram-zoom");
    Array.prototype.forEach.call(zooms, function (a) {
      a.addEventListener("click", function (ev) {
        ev.preventDefault();
        var dlg = document.createElement("dialog");
        dlg.className = "diagram-dialog";
        var img = a.querySelector("img");
        var big = document.createElement("img");
        big.src = a.getAttribute("href");
        big.alt = img ? img.alt : "";
        var close = document.createElement("button");
        close.type = "button";
        close.className = "diagram-dialog__close";
        close.textContent = "Close";
        close.addEventListener("click", function () {
          dlg.close();
        });
        dlg.addEventListener("close", function () {
          dlg.remove();
        });
        dlg.addEventListener("click", function (e) {
          if (e.target === dlg) dlg.close();
        });
        dlg.appendChild(big);
        dlg.appendChild(close);
        main.appendChild(dlg);
        dlg.showModal();
      });
    });
  }
})();
