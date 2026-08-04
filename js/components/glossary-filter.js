/* Glossary filter - /revision-notes/glossary/<board>/
 *
 * Progressive enhancement over a page that is already complete. Every
 * definition and formula is real HTML in the document; this only hides the ones
 * that do not match. With JavaScript off the controls never appear, the A to Z
 * still works, and the browser's own find-on-page still finds everything.
 *
 * No dependency and no build. The text half - normalise, tokenise,
 * escapeHtml, withinDistance, allowedEdits - is copied verbatim from
 * js/components/question-search.js, which is tested by
 * scripts/test_question_search.js. Those functions are data-agnostic; the rest
 * of that file is bound to the past-paper schema, so this is a sibling rather
 * than a shared module. Duplication over abstraction is the house idiom here.
 *
 * Markup contract, all data-* so no class name carries behaviour:
 *
 *   data-glossary-search  root, wraps the controls and every entry
 *   data-gl-controls      <form>, ships hidden and is revealed on boot
 *   data-gl-query         <input type="search">, debounced
 *   data-gl-filter        <select> of topic slugs, matched against data-groups
 *   data-gl-clear         reset button; may appear more than once
 *   data-gl-count         <p role="status" aria-live="polite">
 *   data-gl-empty         shown when nothing matches
 *
 * Entries carry data-term (the term, lowercased) and data-groups (space
 * separated slugs). The searchable text is read from the DOM, so the page and
 * the index cannot drift.
 */
(function () {
  "use strict";

  // ---------------------------------------------------------------- text

  function normalise(s) {
    return String(s)
      .toLowerCase()
      .replace(/[‘’]/g, "'")
      .replace(/[“”]/g, '"')
      .replace(/[–—−]/g, "-");
  }

  /* Tokens are alphanumeric only, so "25-marker" and "25 marker" and "25marker"
   * all reduce to comparable pieces and punctuation never blocks a match. */
  function tokenise(s) {
    return normalise(s)
      .replace(/[^a-z0-9]+/g, " ")
      .split(" ")
      .filter(function (t) {
        return t.length > 0;
      });
  }

  /* Bounded Levenshtein: returns true when a and b are within max edits.
   * Bailing out on the row minimum keeps this cheap on long non-matches. */
  function withinDistance(a, b, max) {
    var la = a.length;
    var lb = b.length;
    if (Math.abs(la - lb) > max) return false;
    if (a === b) return true;

    var prev = [];
    var curr = [];
    var i, j;
    for (j = 0; j <= lb; j++) prev[j] = j;

    for (i = 1; i <= la; i++) {
      curr[0] = i;
      var best = curr[0];
      for (j = 1; j <= lb; j++) {
        var cost = a.charAt(i - 1) === b.charAt(j - 1) ? 0 : 1;
        curr[j] = Math.min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost);
        if (curr[j] < best) best = curr[j];
      }
      if (best > max) return false;
      for (j = 0; j <= lb; j++) prev[j] = curr[j];
    }
    return prev[lb] <= max;
  }

  /* Typo tolerance scaled to word length. One edit is a slip; two edits on a
   * short word is usually a different word. */
  function allowedEdits(token) {
    if (token.length < 4) return 0;
    if (token.length < 7) return 1;
    return 2;
  }

  // ---------------------------------------------------------------- index

  /* One record per entry. The term is weighted above the definition: a student
   * typing "demand" wants the entry called Demand first, not the forty
   * definitions that mention demand in passing. */
  function buildIndex(root) {
    var nodes = root.querySelectorAll("[data-term]");
    var records = [];
    Array.prototype.forEach.call(nodes, function (node) {
      var term = node.getAttribute("data-term") || "";
      var body = node.querySelector(".gl-text, .gl-formula-name");
      var text = body ? body.textContent : "";
      records.push({
        node: node,
        groups: (node.getAttribute("data-groups") || "").split(/\s+/),
        termTokens: tokenise(term),
        allTokens: tokenise(term + " " + text),
        section: node.closest(".gl-letter, .gl-formulae"),
      });
    });
    return records;
  }

  /* AND across the query's tokens: every token must hit something, or the
   * record is out. Exact and prefix hits on the term score highest. */
  function matches(record, queryTokens) {
    for (var i = 0; i < queryTokens.length; i++) {
      var q = queryTokens[i];
      var max = allowedEdits(q);
      var hit = false;
      for (var j = 0; j < record.allTokens.length && !hit; j++) {
        var t = record.allTokens[j];
        if (t === q || t.indexOf(q) === 0) hit = true;
        else if (q.length > 3 && t.indexOf(q) !== -1) hit = true;
        else if (max > 0 && withinDistance(t, q, max)) hit = true;
      }
      if (!hit) return false;
    }
    return true;
  }

  // ---------------------------------------------------------------- component

  function init(root) {
    var form = root.querySelector("[data-gl-controls]");
    var input = root.querySelector("[data-gl-query]");
    var select = root.querySelector("[data-gl-filter]");
    var count = root.querySelector("[data-gl-count]");
    var empty = root.querySelector("[data-gl-empty]");
    var clears = root.querySelectorAll("[data-gl-clear]");
    var records = buildIndex(root);
    var total = records.length;

    if (!records.length) return;

    function apply() {
      var q = input ? input.value.trim() : "";
      var group = select ? select.value : "";
      var tokens = q ? tokenise(q) : [];
      var shown = 0;

      records.forEach(function (r) {
        var ok = true;
        if (group && r.groups.indexOf(group) === -1) ok = false;
        if (ok && tokens.length && !matches(r, tokens)) ok = false;
        r.node.hidden = !ok;
        if (ok) shown++;
      });

      /* A letter heading with nothing under it reads as a bug, so hide any
       * section whose entries are all filtered out. */
      var sections = root.querySelectorAll(".gl-letter, .gl-formulae");
      Array.prototype.forEach.call(sections, function (sec) {
        var live = sec.querySelectorAll("[data-term]:not([hidden])");
        sec.hidden = live.length === 0;
      });

      if (count) {
        if (!q && !group) {
          count.textContent = total + " entries";
        } else {
          count.textContent =
            shown + " of " + total + " entries" + (shown === 0 ? "" : " shown");
        }
      }
      if (empty) empty.hidden = shown !== 0;
      updateAtoZ(root);
    }

    var timer = null;
    if (input) {
      input.addEventListener("input", function () {
        if (timer) clearTimeout(timer);
        timer = setTimeout(apply, 180);
      });
      /* Enter would submit and reload, losing the filter. */
      input.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter") ev.preventDefault();
      });
    }
    if (select) select.addEventListener("change", apply);
    if (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
      });
    }
    Array.prototype.forEach.call(clears, function (btn) {
      btn.addEventListener("click", function () {
        if (input) input.value = "";
        if (select) select.value = "";
        apply();
        if (input) input.focus();
      });
    });

    if (form) form.hidden = false;
    root.classList.add("is-enhanced");
    apply();
    preset(root, select, input, apply);
  }

  /* Grey out the letters that currently have nothing under them, so the strip
   * tells the truth while a filter is active. */
  function updateAtoZ(root) {
    var nav = root.querySelector(".gl-atoz");
    if (!nav) return;
    var links = nav.querySelectorAll("a");
    Array.prototype.forEach.call(links, function (a) {
      var id = a.getAttribute("href").slice(1);
      var section = document.getElementById(id);
      a.setAttribute("aria-disabled", section && section.hidden ? "true" : "false");
    });
  }

  /* ?q= and ?topic= so a link can open the glossary already filtered - used by
   * the internal links from the notes pages. */
  function preset(root, select, input, apply) {
    var params = new URLSearchParams(window.location.search);
    var changed = false;
    var topic = params.get("topic");
    var q = params.get("q");
    if (topic && select) {
      var opts = select.querySelectorAll("option");
      for (var i = 0; i < opts.length; i++) {
        if (opts[i].value === topic) {
          select.value = topic;
          changed = true;
          break;
        }
      }
    }
    if (q && input) {
      input.value = q;
      changed = true;
    }
    if (changed) apply();
  }

  function boot() {
    var roots = document.querySelectorAll("[data-glossary-search]");
    Array.prototype.forEach.call(roots, init);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
