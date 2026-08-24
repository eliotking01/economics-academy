/* Site-wide search - the header magnifier and its overlay. DRAFT for the
 * site-search mock; the shipped file will be js/components/site-search.js.
 *
 * Progressive enhancement. The header's baked control is an <a> to
 * /revision-notes/ - a real destination with scripting off - and this script
 * upgrades every .site-search-open control to open the overlay instead. The
 * overlay DOM is built here at first open, so no page carries hidden markup.
 *
 * The index (/search-index.json, ~113 KB raw / ~31 KB gzipped) is fetched
 * ONCE, lazily, the first time the overlay opens - never on page load. Its
 * compact schema is documented in scripts/build_search_index.py; the two
 * files must move together.
 *
 * The matcher follows js/components/question-search.js: the same
 * normalisation, alphanumeric tokens, and its bounded-edit-distance fuzzy
 * fallback. Vanilla, no dependencies, ES5 like the other components.
 *
 * GA4: one standard `search` event with `search_term`, fired when a result
 * is chosen - not per keystroke - and only if gtag exists (same no-op
 * pattern as track.js). Nothing personal, nothing without consent.
 */
(function () {
  "use strict";

  var DEBOUNCE_MS = 80;
  var INDEX_URL = "/search-index.json";
  var GROUP_CAPS = { notes: 6, glossary: 5, practice: 5, pages: 4 };
  var GROUP_ORDER = ["notes", "glossary", "practice", "pages"];
  var GROUP_LABELS = {
    notes: "Revision notes",
    glossary: "Glossary",
    practice: "Practice & flashcards",
    pages: "Pages",
  };

  // The empty state and the failed-fetch state both offer these, so the
  // overlay is never a blank box.
  var QUICK_LINKS = [
    ["Revision notes", "/revision-notes/"],
    ["Practice questions", "/practice-questions/"],
    ["Flashcards", "/flashcards/"],
    ["Past papers", "/past-papers/"],
    ["Glossary & formulae", "/revision-notes/glossary/"],
  ];

  // Words so common they would veto honest matches under AND ("how much is
  // marking" must find the marking page). Dropped from the query unless the
  // whole query is made of them.
  var STOPWORDS = {
    a: 1, an: 1, the: 1, is: 1, are: 1, was: 1, be: 1, do: 1, does: 1,
    how: 1, what: 1, much: 1, many: 1, i: 1, my: 1, me: 1, it: 1, its: 1,
    to: 1, of: 1, for: 1, in: 1, on: 1, at: 1, with: 1, and: 1, or: 1,
    can: 1, you: 1, your: 1,
  };

  // ---------------------------------------------------------------- text
  // Identical conventions to question-search.js.

  function normalise(s) {
    return String(s)
      .toLowerCase()
      .replace(/[‘’]/g, "'")
      .replace(/[“”]/g, '"')
      .replace(/[–—−]/g, "-");
  }

  function tokenise(s) {
    return normalise(s)
      .replace(/[^a-z0-9]+/g, " ")
      .split(" ")
      .filter(function (t) {
        return t.length > 0;
      });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

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

  function allowedEdits(token) {
    if (token.length < 4) return 0;
    if (token.length < 7) return 1;
    return 2;
  }

  // ---------------------------------------------------------------- rows
  // Expand the compact index (see scripts/build_search_index.py) into flat
  // result rows. Static per-row-kind search words live HERE, once, instead
  // of 400 times in the payload.

  function makeRow(group, title, url, meta, extra) {
    var hayTitle = " " + tokenise(title).join(" ") + " ";
    var hayRest = " " + tokenise(meta + " " + extra).join(" ") + " ";
    return {
      group: group,
      title: title,
      url: url,
      meta: meta,
      hayTitle: hayTitle,
      hayRest: hayRest,
      tokens: tokenise(title + " " + meta + " " + extra),
    };
  }

  function buildRows(data) {
    var rows = [];
    var dot = " · ";
    var i;

    for (i = 0; i < data.topics.length; i++) {
      var t = data.topics[i]; // [di, slug, spec, title, short, headings, ppq]
      var dir = data.dirs[t[0]]; // [notesDir, board, module, boardSlug]
      var short = t[4] || t[3];
      var boardMeta = dir[1] + dot + dir[2];

      rows.push(makeRow(
        "notes", t[3],
        "/revision-notes/" + dir[0] + "/" + t[1] + ".html",
        boardMeta + dot + t[2],
        t[4] + " " + t[5] + " revision notes"));

      rows.push(makeRow(
        "practice", t[2] + " " + short,
        "/practice-questions/" + dir[0] + "/" + t[1] + ".html",
        "Practice questions" + dot + boardMeta,
        t[3] + " quiz mcq multiple choice test"));

      if (t[6]) {
        rows.push(makeRow(
          "practice", t[2] + " " + short,
          "/past-paper-questions/" + dir[3] + "/" + t[1] + "/",
          "Past paper questions" + dot + dir[1],
          t[3] + " real exam"));
      }
    }

    for (i = 0; i < data.decks.length; i++) {
      var deck = data.decks[i]; // [deckTitle, url, di]
      var ddir = data.dirs[deck[2]];
      rows.push(makeRow(
        "practice", deck[0], deck[1],
        "Flashcards" + dot + ddir[1] + dot + ddir[2],
        "flashcards cards deck revise"));
    }

    for (i = 0; i < data.glossary.length; i++) {
      var g = data.glossary[i]; // [title, id, boards, kind, definition]
      var links = [];
      if (g[2] & 1) links.push(["Edexcel", "/revision-notes/glossary/edexcel-a/#" + g[1]]);
      if (g[2] & 2) links.push(["AQA", "/revision-notes/glossary/aqa/#" + g[1]]);
      var row = makeRow(
        "glossary", g[0], links[0][1],
        g[3] ? "Formula" : "Glossary",
        g[3] ? "formula formulae equation calculate" : "definition");
      row.def = g[4];
      row.links = links;
      // The definition is searchable at low weight, so "free rider" style
      // phrasings inside a definition still surface the term.
      row.hayDef = " " + tokenise(g[4]).join(" ") + " ";
      rows.push(row);
    }

    for (i = 0; i < data.pages.length; i++) {
      var p = data.pages[i]; // [title, url, metaLabel, synonyms]
      rows.push(makeRow("pages", p[0], p[1], p[2], p[3]));
    }

    return rows;
  }

  // -------------------------------------------------------------- scoring

  /* AND across query tokens, like question-search.js. Where a token hits
   * decides its weight: a word start in the title beats a title substring,
   * beats a word start in the meta/extra text, beats a definition substring.
   * A row where any token misses everywhere is out. Fuzzy matching is a
   * second pass, run only when the strict pass finds nothing at all -
   * otherwise "marking" would rank fuzzy "Making" pages above the real
   * marking page. */
  function scoreRow(row, queryTokens, fuzzy) {
    var total = 0;
    for (var i = 0; i < queryTokens.length; i++) {
      var qt = queryTokens[i];
      var hit = 0;
      if (row.hayTitle.indexOf(" " + qt) !== -1) hit = 5;
      else if (row.hayTitle.indexOf(qt) !== -1) hit = 3;
      else if (row.hayRest.indexOf(" " + qt) !== -1) hit = 2;
      else if (row.hayRest.indexOf(qt) !== -1) hit = 1;
      else if (row.hayDef && row.hayDef.indexOf(qt) !== -1) hit = 1;
      else if (fuzzy) {
        var max = allowedEdits(qt);
        if (max > 0) {
          for (var j = 0; j < row.tokens.length; j++) {
            if (withinDistance(qt, row.tokens[j], max)) {
              hit = 1;
              break;
            }
          }
        }
      }
      if (hit === 0) return -1;
      total += hit;
    }
    // An exact title is the thing itself.
    if (row.hayTitle === " " + queryTokens.join(" ") + " ") total += 20;
    return total;
  }

  function search(rows, query) {
    var tokens = tokenise(query);
    var kept = [];
    for (var i = 0; i < tokens.length; i++) {
      if (!STOPWORDS[tokens[i]]) kept.push(tokens[i]);
    }
    if (kept.length) tokens = kept;
    if (!tokens.length) return { groups: {}, exact: null, any: false };

    var byGroup = { notes: [], glossary: [], practice: [], pages: [] };
    var exact = null;
    var joined = " " + tokens.join(" ") + " ";
    var passes = [false, true]; // strict first; fuzzy only if it found nothing
    for (var p = 0; p < passes.length; p++) {
      for (var r = 0; r < rows.length; r++) {
        var s = scoreRow(rows[r], tokens, passes[p]);
        if (s < 0) continue;
        byGroup[rows[r].group].push({ row: rows[r], score: s });
        // The float: the query IS a glossary term (or formula name).
        if (rows[r].group === "glossary" && rows[r].hayTitle === joined) {
          if (!exact || s > exact.score) exact = { row: rows[r], score: s };
        }
      }
      if (byGroup.notes.length || byGroup.glossary.length ||
          byGroup.practice.length || byGroup.pages.length) break;
    }
    var any = false;
    for (var g = 0; g < GROUP_ORDER.length; g++) {
      var list = byGroup[GROUP_ORDER[g]];
      list.sort(function (a, b) {
        if (b.score !== a.score) return b.score - a.score;
        if (a.row.title.length !== b.row.title.length)
          return a.row.title.length - b.row.title.length;
        return a.row.title < b.row.title ? -1 : 1;
      });
      if (list.length) any = true;
    }
    return { groups: byGroup, exact: exact, any: any, tokens: tokens };
  }

  // ------------------------------------------------------------ rendering

  /* Wrap each query token's first occurrence in <mark>. Runs on the plain
   * title, then escapes around the marks, so markup can never be injected. */
  function highlight(text, tokens) {
    if (!tokens || !tokens.length) return escapeHtml(text);
    var low = normalise(text);
    var spans = [];
    for (var i = 0; i < tokens.length; i++) {
      var at = low.indexOf(tokens[i]);
      if (at === -1) continue;
      spans.push([at, at + tokens[i].length]);
    }
    if (!spans.length) return escapeHtml(text);
    spans.sort(function (a, b) { return a[0] - b[0]; });
    var merged = [spans[0]];
    for (var j = 1; j < spans.length; j++) {
      var lastSpan = merged[merged.length - 1];
      if (spans[j][0] <= lastSpan[1]) {
        lastSpan[1] = Math.max(lastSpan[1], spans[j][1]);
      } else {
        merged.push(spans[j]);
      }
    }
    var out = "";
    var pos = 0;
    for (var k = 0; k < merged.length; k++) {
      out += escapeHtml(text.slice(pos, merged[k][0]));
      out += "<mark>" + escapeHtml(text.slice(merged[k][0], merged[k][1])) + "</mark>";
      pos = merged[k][1];
    }
    return out + escapeHtml(text.slice(pos));
  }

  function quickLinksHtml() {
    var out = '<nav class="site-search__quick" aria-label="Popular sections">';
    for (var i = 0; i < QUICK_LINKS.length; i++) {
      out += '<a class="site-search__quick-link" href="' + QUICK_LINKS[i][1] +
        '">' + escapeHtml(QUICK_LINKS[i][0]) + "</a>";
    }
    return out + "</nav>";
  }

  // ---------------------------------------------------------------- state

  var overlay = null;
  var input = null;
  var resultsEl = null;
  var statusEl = null;
  var opener = null; // the control that opened the overlay, for focus return
  var rows = null; // built once the index arrives
  var fetchState = "idle"; // idle | loading | ready | failed
  var options = []; // flat list of rendered option rows, in DOM order
  var active = -1; // index into options for aria-activedescendant
  var timer = null;
  var lastQuery = "";

  function track(query) {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", "search", {
      search_term: query.slice(0, 100),
      page_path: window.location.pathname,
    });
  }

  // ---------------------------------------------------------------- DOM

  function buildOverlay() {
    if (overlay) return;
    overlay = document.createElement("div");
    overlay.className = "site-search";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.setAttribute("aria-label", "Search this site");
    overlay.hidden = true;
    overlay.innerHTML =
      '<div class="site-search__panel">' +
      '<div class="site-search__bar">' +
      '<span class="icon solid fa-search site-search__glass" aria-hidden="true"></span>' +
      '<input class="site-search__input" type="text" role="combobox"' +
      ' aria-expanded="true" aria-controls="site-search-results"' +
      ' aria-autocomplete="list" aria-label="Search this site"' +
      ' autocomplete="off" autocorrect="off" autocapitalize="off"' +
      ' spellcheck="false" enterkeyhint="go"' +
      ' placeholder="Search topics, definitions, resources…">' +
      '<button type="button" class="site-search__close">Cancel</button>' +
      "</div>" +
      '<div class="site-search__status" role="status"></div>' +
      '<div class="site-search__results" id="site-search-results"' +
      ' role="listbox" aria-label="Search results"></div>' +
      '<p class="site-search__hint" aria-hidden="true">' +
      "<kbd>↑</kbd> <kbd>↓</kbd> to move · " +
      "<kbd>Enter</kbd> to open · <kbd>Esc</kbd> to close</p>" +
      "</div>";
    document.body.appendChild(overlay);

    input = overlay.querySelector(".site-search__input");
    resultsEl = overlay.querySelector(".site-search__results");
    statusEl = overlay.querySelector(".site-search__status");

    // Backdrop click closes; clicks inside the panel do not. The overlay
    // itself is the backdrop - the panel is its only child.
    overlay.addEventListener("mousedown", function (e) {
      if (e.target === overlay) close();
    });
    overlay.querySelector(".site-search__close")
      .addEventListener("click", close);

    input.addEventListener("input", function () {
      if (timer) clearTimeout(timer);
      timer = setTimeout(run, DEBOUNCE_MS);
    });

    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        move(1);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        move(-1);
      } else if (e.key === "Enter") {
        e.preventDefault();
        choose(active >= 0 ? active : 0);
      }
    });

    overlay.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        e.preventDefault();
        close();
        return;
      }
      // Focus trap: Tab cycles through the overlay's own focusables.
      if (e.key !== "Tab") return;
      var focusables = overlay.querySelectorAll("input, button, a[href]");
      if (!focusables.length) return;
      var first = focusables[0];
      var last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });

    // One delegated handler covers every rendered result, whenever rendered.
    resultsEl.addEventListener("click", function (e) {
      var a = e.target.closest("a");
      if (a) track(input.value);
    });
  }

  // ------------------------------------------------------------ the index

  function loadIndex() {
    if (fetchState !== "idle") return;
    fetchState = "loading";
    var src = document.body.getAttribute("data-search-index") || INDEX_URL;
    fetch(src)
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (data) {
        rows = buildRows(data);
        fetchState = "ready";
        run();
      })
      .catch(function () {
        fetchState = "failed";
        run();
      });
  }

  // ------------------------------------------------------------ rendering

  function setStatus(html) {
    statusEl.innerHTML = html;
  }

  function optionHtml(row, id, tokens, activeNow) {
    return (
      '<a class="site-search__option" id="' + id + '" role="option"' +
      ' href="' + escapeHtml(row.url) + '"' +
      (activeNow ? ' aria-selected="true"' : ' aria-selected="false"') +
      ' tabindex="-1">' +
      '<span class="site-search__option-title">' +
      highlight(row.title, tokens) + "</span>" +
      '<span class="site-search__option-meta">' + escapeHtml(row.meta) +
      "</span></a>"
    );
  }

  function render(result) {
    options = [];
    active = -1;
    var query = input.value.trim();

    if (fetchState === "failed") {
      setStatus(
        "Search couldn’t load. Check your connection and try again, " +
        "or jump straight to a section:");
      resultsEl.innerHTML = quickLinksHtml();
      return;
    }
    if (fetchState !== "ready") {
      setStatus("Loading…");
      resultsEl.innerHTML = "";
      return;
    }
    if (!query || !result || !result.tokens || !result.tokens.length) {
      setStatus("Try a topic, a term, or a page — or jump straight in:");
      resultsEl.innerHTML = quickLinksHtml();
      return;
    }
    if (!result.any) {
      setStatus(
        "Nothing for ‘" + escapeHtml(query) + "’ — try a " +
        "topic name or a glossary term.");
      resultsEl.innerHTML = quickLinksHtml();
      return;
    }

    setStatus("");
    var html = "";
    var n = 0;

    // The float: the query IS a glossary term, so its definition is shown
    // whole at the very top - one entry, not the group promoted.
    if (result.exact) {
      var ex = result.exact.row;
      var linksHtml = "";
      for (var l = 0; l < ex.links.length; l++) {
        linksHtml += (l ? " · " : "") +
          '<a class="site-search__def-link" href="' +
          escapeHtml(ex.links[l][1]) + '">' +
          escapeHtml(ex.links[l][0]) + "</a>";
      }
      html +=
        '<div class="site-search__definition">' +
        '<a class="site-search__option site-search__def-head" role="option"' +
        ' id="ss-opt-' + n + '" aria-selected="false" tabindex="-1" href="' +
        escapeHtml(ex.url) + '">' +
        '<span class="site-search__option-title">' +
        escapeHtml(ex.title) + "</span>" +
        '<span class="site-search__option-meta">' +
        escapeHtml(ex.meta) + "</span></a>" +
        '<p class="site-search__def-text">' + escapeHtml(ex.def) + "</p>" +
        '<p class="site-search__def-links">In the glossary: ' + linksHtml +
        "</p></div>";
      options.push(ex);
      n++;
    }

    for (var g = 0; g < GROUP_ORDER.length; g++) {
      var name = GROUP_ORDER[g];
      var list = result.groups[name] || [];
      // The floated entry is not repeated inside its group.
      if (result.exact) {
        list = list.filter(function (item) {
          return item.row !== result.exact.row;
        });
      }
      if (!list.length) continue;
      var cap = GROUP_CAPS[name];
      html += '<div class="site-search__group" role="group" aria-label="' +
        GROUP_LABELS[name] + '">' +
        '<p class="site-search__group-label" aria-hidden="true">' +
        GROUP_LABELS[name] + "</p>";
      for (var i = 0; i < list.length && i < cap; i++) {
        html += optionHtml(list[i].row, "ss-opt-" + n, result.tokens, false);
        options.push(list[i].row);
        n++;
      }
      html += "</div>";
    }

    resultsEl.innerHTML = html;
  }

  function run() {
    var query = input.value.trim();
    lastQuery = query;
    render(fetchState === "ready" && query ? search(rows, query) : null);
  }

  // ---------------------------------------------------------- navigation

  function move(delta) {
    if (!options.length) return;
    var next = active + delta;
    if (next < 0) next = options.length - 1;
    if (next >= options.length) next = 0;
    setActive(next);
  }

  function setActive(index) {
    var prev = document.getElementById("ss-opt-" + active);
    if (prev) prev.setAttribute("aria-selected", "false");
    active = index;
    var el = document.getElementById("ss-opt-" + active);
    if (el) {
      el.setAttribute("aria-selected", "true");
      input.setAttribute("aria-activedescendant", el.id);
      if (el.scrollIntoView) el.scrollIntoView({ block: "nearest" });
    }
  }

  function choose(index) {
    if (!options[index]) return;
    track(input.value);
    window.location.href = options[index].url;
  }

  // ------------------------------------------------------------ open/close

  function open(from) {
    buildOverlay();
    opener = from || document.activeElement;
    overlay.hidden = false;
    document.documentElement.classList.add("site-search-locked");
    input.value = "";
    input.removeAttribute("aria-activedescendant");
    loadIndex();
    run();
    input.focus();
  }

  function close() {
    if (!overlay || overlay.hidden) return;
    overlay.hidden = true;
    document.documentElement.classList.remove("site-search-locked");
    if (opener && opener.focus) opener.focus();
    opener = null;
  }

  // ---------------------------------------------------------------- boot

  function isEditable(el) {
    if (!el) return false;
    var tag = (el.tagName || "").toLowerCase();
    return tag === "input" || tag === "textarea" || tag === "select" ||
      el.isContentEditable;
  }

  function init() {
    // Upgrade every baked search control. Delegated, so the button nav.js
    // may add to #titleBar later is covered by the same handler.
    document.addEventListener("click", function (e) {
      var control = e.target.closest(".site-search-open");
      if (!control) return;
      e.preventDefault();
      open(control);
    });

    // "/" opens search from anywhere, unless the reader is typing.
    document.addEventListener("keydown", function (e) {
      if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
      if (isEditable(e.target)) return;
      if (overlay && !overlay.hidden) return;
      e.preventDefault();
      open(null);
    });

    // The mobile title bar is built by nav.js at DOMContentLoaded; this
    // runs after it (later in the script tail), so the bar exists by now.
    var titleBar = document.getElementById("titleBar");
    if (titleBar) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "site-search-open site-search__bar-toggle";
      btn.setAttribute("aria-label", "Search this site");
      var icon = document.createElement("span");
      icon.className = "icon solid fa-search";
      icon.setAttribute("aria-hidden", "true");
      btn.appendChild(icon);
      titleBar.appendChild(btn);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // The mock drives the overlay directly (auto-open, canned queries).
  window.__siteSearch = { open: open, close: close, run: run };
})();
