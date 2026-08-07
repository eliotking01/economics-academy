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
 *   data-gl-results       <section>, empty at rest; ranked matches move into it
 *   data-gl-echo          <span> inside the empty state, filled with the query
 *
 * Entries carry data-term (the term, lowercased) and data-groups (space
 * separated slugs). The searchable text is read from the DOM, so the page and
 * the index cannot drift.
 *
 * Search matches the TERM ONLY - see SEARCH_FIELDS. Two behaviours follow from
 * that and are deliberate:
 *
 *   - Results are ranked by match quality rather than left in A-Z order, so
 *     "demand" puts Demand first. Ranking needs the order to change, so during
 *     a search the matches are lifted out of their letter sections into one
 *     flat list and the A-Z strip is hidden. Clearing the box puts them back.
 *   - A concept that is not itself a term name returns nothing, so the empty
 *     state says what is searched rather than just "no results".
 */
(function () {
  "use strict";

  // ---------------------------------------------------------------- text

  /* Accents are stripped as well as case folded, so "laissez-faire" is found by
   * typing it without the accent it does not have and by typing one it does. */
  function normalise(s) {
    var out = String(s)
      .toLowerCase()
      .replace(/[‘’]/g, "'")
      .replace(/[“”]/g, '"')
      .replace(/[–—−]/g, "-");
    return out.normalize
      ? out.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      : out;
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

  // ---------------------------------------------------------------- scoring

  /* Which text the query is matched against.
   *
   * TERM ONLY, deliberately. Matching definitions too meant that searching
   * "demand" buried the entry called Demand under every definition that
   * mentions the word in passing - which is most of them.
   *
   * The record still carries definition tokens, and scoring reads its field
   * list rather than a hard-coded one, so an "also search definitions" toggle
   * is a change to this constant and nothing else. Not built: nobody has asked
   * for it, and a term-only glossary search is the behaviour students expect.
   */
  var SEARCH_FIELDS = ["term"];

  function fieldTokens(record, fields) {
    if (fields.length === 1 && fields[0] === "term") return record.termTokens;
    var out = [];
    for (var i = 0; i < fields.length; i++) {
      out = out.concat(record[fields[i] + "Tokens"] || []);
    }
    return out;
  }

  /* Rank tiers, best first. A record's rank is the WEAKEST tier any of its
   * query tokens managed, so "price elast" cannot rank above an exact hit on
   * the strength of its first word alone.
   *
   *   0  exact       the whole term is the query
   *   1  prefix      the term starts with the query
   *   2  word start  some word in the term starts with the query
   *   3  contains    the query appears somewhere in the term
   *   4  fuzzy       within the allowed edit distance - "elasitcity"
   *
   * -1 means no match at all: every query token must hit something, or the
   * record is out. Ties are broken alphabetically by the caller, which sorts on
   * the record's position in a page already ordered A-Z.
   */
  var NO_MATCH = -1;

  function score(record, query, queryTokens, fields) {
    if (!query) return 0;
    var haystack =
      fields.length === 1 && fields[0] === "term"
        ? record.termText
        : fieldTokens(record, fields).join(" ");
    if (haystack === query) return 0;
    if (haystack.indexOf(query) === 0) return 1;

    var tokens = fieldTokens(record, fields);
    var rank = 2;
    for (var i = 0; i < queryTokens.length; i++) {
      var q = queryTokens[i];
      var tier = NO_MATCH;
      for (var j = 0; j < tokens.length; j++) {
        if (tokens[j] === q || tokens[j].indexOf(q) === 0) {
          tier = 2;
          break;
        }
      }
      if (tier === NO_MATCH && q.length > 3 && haystack.indexOf(q) !== -1) {
        tier = 3;
      }
      if (tier === NO_MATCH) {
        var max = allowedEdits(q);
        for (var k = 0; max > 0 && k < tokens.length; k++) {
          if (withinDistance(tokens[k], q, max)) {
            tier = 4;
            break;
          }
        }
      }
      if (tier === NO_MATCH) return NO_MATCH;
      if (tier > rank) rank = tier;
    }
    return rank;
  }

  // ---------------------------------------------------------------- index

  /* One record per entry, in document order - which is already A-Z, so a stable
   * sort by rank leaves alphabetical order inside each tier for free.
   *
   * home is the list an entry lives in at rest. A ranked search lifts the
   * matches out into one flat list; restoring appends them to home in record
   * order, which is the order the page had them in. */
  function buildIndex(root) {
    var nodes = root.querySelectorAll("[data-term]");
    var records = [];
    Array.prototype.forEach.call(nodes, function (node, i) {
      var term = node.getAttribute("data-term") || "";
      var body = node.querySelector(".gl-text, .gl-formula-name");
      var text = body ? body.textContent : "";
      records.push({
        node: node,
        order: i,
        groups: (node.getAttribute("data-groups") || "").split(/\s+/),
        termText: normalise(term),
        termTokens: tokenise(term),
        definitionTokens: tokenise(text),
        section: node.closest(".gl-letter, .gl-formulae"),
        /* Formulae live in a grid of their own and are never reordered; only
         * the A-Z entries are movable. */
        movable: node.className.indexOf("gl-entry") !== -1,
        home: node.parentNode,
      });
    });
    return records;
  }

  // ---------------------------------------------------------------- component

  function init(root) {
    var form = root.querySelector("[data-gl-controls]");
    var input = root.querySelector("[data-gl-query]");
    var select = root.querySelector("[data-gl-filter]");
    var count = root.querySelector("[data-gl-count]");
    var empty = root.querySelector("[data-gl-empty]");
    var clears = root.querySelectorAll("[data-gl-clear]");
    var results = root.querySelector("[data-gl-results]");
    var resultsList = results ? results.querySelector(".gl-list") : null;
    var atoz = root.querySelector(".gl-atoz");
    var echo = root.querySelector("[data-gl-echo]");
    var records = buildIndex(root);
    var total = records.length;

    if (!records.length) return;

    /* Put every movable entry back where the page had it. Records are in
     * document order, so appending them in turn restores that order exactly. */
    function restore() {
      records.forEach(function (r) {
        if (r.movable && r.node.parentNode !== r.home)
          r.home.appendChild(r.node);
      });
    }

    function apply() {
      var raw = input ? input.value : "";
      var q = normalise(raw.trim());
      var group = select ? select.value : "";
      var tokens = q ? tokenise(q) : [];
      var ranked = [];
      var shown = 0;

      records.forEach(function (r) {
        var ok = !group || r.groups.indexOf(group) !== -1;
        var rank = 0;
        if (ok && q) {
          rank = score(r, q, tokens, SEARCH_FIELDS);
          if (rank === NO_MATCH) ok = false;
        }
        r.node.hidden = !ok;
        if (ok) {
          shown++;
          if (q && r.movable) ranked.push({ r: r, rank: rank });
        }
      });

      /* With a query the A-Z ordering is what we are trying to get away from,
       * so the matches move into one flat list, best first. Without one the
       * page goes back to being an A-Z glossary. */
      if (q && resultsList) {
        ranked.sort(function (a, b) {
          return a.rank - b.rank || a.r.order - b.r.order;
        });
        ranked.forEach(function (x) {
          resultsList.appendChild(x.r.node);
        });
      } else {
        restore();
      }
      if (results) results.hidden = !q || ranked.length === 0;
      if (atoz) atoz.hidden = !!q;

      /* A letter heading with nothing under it reads as a bug, so hide any
       * section whose entries are all filtered out. During a ranked search the
       * letter sections are empty by construction and all go. */
      var sections = root.querySelectorAll(".gl-letter, .gl-formulae");
      Array.prototype.forEach.call(sections, function (sec) {
        var live = sec.querySelectorAll("[data-term]:not([hidden])");
        sec.hidden = live.length === 0;
      });

      if (count) {
        if (!q && !group) {
          count.textContent = total + " entries";
        } else if (shown === 0) {
          count.textContent = "No entries match";
        } else {
          count.textContent = shown + " of " + total + " entries shown";
        }
      }
      if (echo) echo.textContent = raw.trim();
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
      a.setAttribute(
        "aria-disabled",
        section && section.hidden ? "true" : "false",
      );
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
