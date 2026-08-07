/* Past paper question search - the reusable search/filter/results component.
 *
 * Used twice: standalone on /past-paper-questions/, and embedded on every
 * generated topic page with that topic pre-filtered. Same file, same markup,
 * same behaviour; only the data-prefilter-topic attribute differs.
 *
 * Progressive enhancement. The controls ship hidden and are revealed only once
 * this script has the data, so a reader without JavaScript is never shown a
 * search box that cannot work. Topic pages carry their questions as real HTML
 * inside the results container; this script replaces that markup with the same
 * markup rendered from JSON, so crawlers and no-JS readers keep the content.
 *
 * Vanilla, no jQuery, ES5 to match js/components/quiz.js. One fetch, cached.
 *
 * Why no Fuse.js: fuse.js v7 ships only .cjs and .mjs, so using it would force
 * an ES module into a site whose scripts are all classic, for a dataset of a
 * few hundred short records. The matcher below is a bounded-edit-distance
 * token index - enough for real typos ("quantitive easing"), small enough to
 * read, and dependency-free like the rest of this repo.
 */
(function () {
  "use strict";

  var PAGE_SIZE = 20;
  var DEBOUNCE_MS = 200;

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

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
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

  /* Every phrasing of a mark tariff a student might type. Without these,
   * "25 marks" tokenises to ["25","marks"] and "marks" matches nothing. */
  function markTokens(marks) {
    return [
      String(marks),
      marks + "m",
      marks + "mark",
      marks + "marks",
      marks + "marker",
      marks + "markers",
      "marks",
      "mark",
    ];
  }

  /* What of a question's text is worth searching.
   *
   * The displayed text is the paper's wording verbatim, source citation and
   * all. The citation is provenance, not economics, and indexing it produces
   * matches a student would call wrong: the URL
   * ".../tesla-holds-us-ev-market-losing-federal-tax-credit/" made a monopoly
   * and efficiency question a hit for "tax". Citations come out of the
   * haystack; nothing changes on screen.
   */
  function searchableText(s) {
    return String(s)
      .replace(/\(Sources?\b[^)]*\)/gi, " ")
      .replace(/https?:\/\/\S+/g, " ");
  }

  function buildIndex(data) {
    var topics = data.topics;
    var groups = {};
    var boards = {};
    data.boards.forEach(function (b) {
      boards[b.board] = b;
      b.groups.forEach(function (g) {
        groups[g.slug] = g;
        groupLabels[g.slug] = g.label;
      });
    });

    return data.questions.map(function (q) {
      var paper = data.papers[q.p];
      var parts = [searchableText(q.questionText)];

      q.topics.forEach(function (slug) {
        var t = topics[slug];
        if (t) parts.push(t.title, t.shortTitle, t.spec, t.unitName);
      });
      q.groups.forEach(function (slug) {
        var g = groups[slug];
        if (g) parts.push(g.label, g.name);
      });
      if (boards[q.board]) parts.push(boards[q.board].name);
      parts.push(q.keywords.join(" "));
      parts.push(
        "paper " + paper.paper,
        paper.paperName,
        paper.series,
        String(paper.year),
        paper.series + " " + paper.year,
        "section " + q.section,
        paper.board,
        // The qualification comes from the PAPER, not the board: Edexcel now
        // spans 9EC0 and 8EC0, so the board-level string would label every AS
        // question "A Level". "AS" and "A Level" are both indexed so either
        // spelling of the query finds the right set.
        paper.qualification,
        paper.levelLabel,
      );
      parts.push(markTokens(q.marks).join(" "));

      var hay = normalise(parts.join(" "));
      var tokens = tokenise(hay);
      var seen = {};
      var unique = [];
      tokens.forEach(function (t) {
        if (!seen[t]) {
          seen[t] = true;
          unique.push(t);
        }
      });

      return {
        q: q,
        paper: paper,
        hay: hay.replace(/[^a-z0-9]+/g, " "),
        tokens: unique,
      };
    });
  }

  /* AND across query tokens: every token must hit something, which is what a
   * reader expects from "monopoly 25 marks". Exact substring scores highest,
   * a word-start match next, a fuzzy match last. */
  function score(record, queryTokens) {
    var total = 0;
    for (var i = 0; i < queryTokens.length; i++) {
      var qt = queryTokens[i];
      var hit = 0;

      if (record.hay.indexOf(" " + qt) !== -1 || record.hay.indexOf(qt) === 0) {
        hit = 3;
      } else if (record.hay.indexOf(qt) !== -1) {
        hit = 2;
      } else {
        var max = allowedEdits(qt);
        if (max > 0) {
          for (var j = 0; j < record.tokens.length; j++) {
            if (withinDistance(qt, record.tokens[j], max)) {
              hit = 1;
              break;
            }
          }
        }
      }

      if (hit === 0) return -1;
      total += hit;
    }
    return total;
  }

  // ---------------------------------------------------------------- render

  /* Section labels by slug, filled by buildIndex. Card rendering needs them and
   * is called with only the topics table, so they live here. */
  var groupLabels = {};

  function cardHtml(record, topics) {
    var q = record.q;
    var paper = record.paper;
    var msUrl = paper.markSchemeUrl + "#page=" + q.msPage;

    // The qualification badge sits second, straight after the board, because an
    // A Level student who revises from an AS question without noticing gets a
    // distorted picture of the demand. Must stay identical to render_card() in
    // scripts/build_past_paper_questions.py.
    var badges = [
      '<span class="ppq-badge ppq-badge-board">' +
        escapeHtml(paper.boardName) +
        "</span>",
      '<span class="ppq-badge ppq-badge-level ppq-badge-level-' +
        escapeHtml(paper.level) +
        '">' +
        escapeHtml(paper.levelLabel) +
        "</span>",
      '<span class="ppq-badge ppq-badge-paper">Paper ' +
        paper.paper +
        "</span>",
      '<span class="ppq-badge">' +
        escapeHtml(paper.series + " " + paper.year) +
        "</span>",
      '<span class="ppq-badge ppq-badge-marks">' + q.marks + " marks</span>",
    ];
    q.groups.forEach(function (slug) {
      var g = groupLabels[slug];
      badges.push(
        '<span class="ppq-badge ppq-badge-theme">' +
          escapeHtml(g || slug) +
          "</span>",
      );
    });

    var topicLinks = q.topics
      .map(function (slug) {
        var t = topics[slug];
        if (!t) return "";
        var label = escapeHtml(t.spec + " " + t.shortTitle);
        return t.hasPage
          ? '<a href="' + escapeHtml(t.url) + '">' + label + "</a>"
          : "<span>" + label + "</span>";
      })
      .filter(Boolean)
      .join(" &middot; ");

    // Question paper first: a student who wants to attempt this under exam
    // conditions needs the question as it was printed, before anything else.
    var actions = [
      '<a class="ppq-action" href="' +
        escapeHtml(paper.questionPaperUrl + "#page=" + q.qpPage) +
        '" target="_blank" rel="noopener noreferrer">Question paper &mdash; p.' +
        q.qpPage +
        "</a>",
    ];
    if (q.ctxPage) {
      actions.push(
        '<a class="ppq-action" href="' +
          escapeHtml(paper.questionPaperUrl + "#page=" + q.ctxPage) +
          '" target="_blank" rel="noopener noreferrer">View the extract &mdash; p.' +
          q.ctxPage +
          "</a>",
      );
    }
    actions.push(
      '<a class="ppq-action" href="' +
        escapeHtml(msUrl) +
        '" target="_blank" rel="noopener noreferrer">Mark scheme &mdash; p.' +
        q.msPage +
        "</a>",
    );
    var first = topics[q.topics[0]];
    if (first) {
      actions.push(
        '<a class="ppq-action" href="' +
          escapeHtml(first.notesUrl) +
          '">Revision notes: ' +
          escapeHtml(first.spec) +
          "</a>",
      );
    }
    // Slot for a future model answer. Kept out of the DOM entirely while null
    // so nothing has to be hidden with CSS.
    if (q.modelAnswer) {
      actions.push(
        '<a class="ppq-action ppq-action-model" href="' +
          escapeHtml(q.modelAnswer) +
          '">Model answer</a>',
      );
    }

    var choice = q.choiceGroup
      ? '<p class="ppq-choice">One of two options in Section ' +
        escapeHtml(q.section) +
        " &mdash; candidates answered this <em>or</em> the other.</p>"
      : "";

    return (
      '<article class="ppq-card" id="' +
      escapeHtml(q.id) +
      '">' +
      '<div class="ppq-badges">' +
      badges.join("") +
      "</div>" +
      '<p class="ppq-question">' +
      escapeHtml(q.questionText) +
      "</p>" +
      choice +
      (topicLinks ? '<p class="ppq-topics">' + topicLinks + "</p>" : "") +
      '<div class="ppq-actions">' +
      actions.join("") +
      "</div>" +
      "</article>"
    );
  }

  // ---------------------------------------------------------------- component

  function init(root, data) {
    var index = buildIndex(data);
    var topics = data.topics;

    var els = {
      controls: root.querySelector("[data-ppq-controls]"),
      query: root.querySelector("[data-ppq-query]"),
      count: root.querySelector("[data-ppq-count]"),
      results: root.querySelector("[data-ppq-results]"),
      empty: root.querySelector("[data-ppq-empty]"),
      more: root.querySelector("[data-ppq-more]"),
      clear: root.querySelector("[data-ppq-clear]"),
      sort: root.querySelector("[data-ppq-sort]"),
    };

    var filters = {};
    var selects = root.querySelectorAll("[data-ppq-filter]");
    Array.prototype.forEach.call(selects, function (sel) {
      filters[sel.getAttribute("data-ppq-filter")] = sel;
    });

    // A topic or theme page fixes one filter and hides its control, so the
    // reader cannot silently filter their way out of the page they are on.
    var preTopic = root.getAttribute("data-prefilter-topic") || "";
    var preBoard = root.getAttribute("data-prefilter-board") || "";
    var preGroup = root.getAttribute("data-prefilter-group") || "";

    var shown = PAGE_SIZE;
    var matches = [];

    function optionList(sel, values, labeller) {
      var html =
        '<option value="">' + sel.getAttribute("data-ppq-all") + "</option>";
      values.forEach(function (v) {
        html +=
          '<option value="' +
          escapeHtml(v) +
          '">' +
          escapeHtml(labeller(v)) +
          "</option>";
      });
      sel.innerHTML = html;
    }

    function populate() {
      var papers = [];
      var years = [];
      var marks = [];
      var sections = [];
      var levels = [];
      data.questions.forEach(function (q) {
        var p = data.papers[q.p];
        if (papers.indexOf(p.paper) === -1) papers.push(p.paper);
        if (years.indexOf(p.year) === -1) years.push(p.year);
        if (marks.indexOf(q.marks) === -1) marks.push(q.marks);
        if (sections.indexOf(q.section) === -1) sections.push(q.section);
        if (levels.indexOf(p.level) === -1) levels.push(p.level);
      });
      papers.sort();
      years.sort().reverse();
      marks.sort(function (a, b) {
        return a - b;
      });
      sections.sort();
      // "a-level" before "as-level" happens to be alphabetical, and is also the
      // order a student expects: the qualification most of them are sitting
      // comes first.
      levels.sort();

      if (filters.paper)
        optionList(filters.paper, papers, function (v) {
          return "Paper " + v;
        });
      if (filters.year)
        optionList(filters.year, years, function (v) {
          return String(v);
        });
      if (filters.marks)
        optionList(filters.marks, marks, function (v) {
          return v + " marks";
        });
      if (filters.section)
        optionList(filters.section, sections, function (v) {
          return "Section " + v;
        });
      if (filters.level)
        optionList(filters.level, levels, function (v) {
          return v === "as-level" ? "AS Level only" : "A Level only";
        });
      if (filters.board)
        optionList(
          filters.board,
          data.boards.map(function (b) {
            return b.board;
          }),
          function (v) {
            var b = data.boards.filter(function (x) {
              return x.board === v;
            })[0];
            return b ? b.name : v;
          },
        );
      if (filters.group) {
        // Only the sections of the board in play, so an Edexcel page never
        // offers "Microeconomics" and vice versa.
        var groupList = [];
        data.boards.forEach(function (b) {
          if (preBoard && b.board !== preBoard) return;
          b.groups.forEach(function (g) {
            groupList.push(g);
          });
        });
        optionList(
          filters.group,
          groupList.map(function (g) {
            return g.slug;
          }),
          function (v) {
            var g = groupList.filter(function (x) {
              return x.slug === v;
            })[0];
            return g ? g.label + ": " + g.name : v;
          },
        );
      }
      if (filters.topic) {
        var slugs = Object.keys(topics)
          .filter(function (s) {
            return !preBoard || topics[s].board === preBoard;
          })
          .sort(function (a, b) {
            return topics[a].spec.localeCompare(topics[b].spec, "en", {
              numeric: true,
            });
          });
        optionList(filters.topic, slugs, function (s) {
          return topics[s].spec + " " + topics[s].shortTitle;
        });
      }
    }

    function passesFilters(record) {
      var q = record.q;
      var p = record.paper;
      if (preTopic && q.topics.indexOf(preTopic) === -1) return false;
      if (preBoard && q.board !== preBoard) return false;
      if (preGroup && q.groups.indexOf(preGroup) === -1) return false;
      if (
        filters.paper &&
        filters.paper.value &&
        String(p.paper) !== filters.paper.value
      )
        return false;
      if (
        filters.year &&
        filters.year.value &&
        String(p.year) !== filters.year.value
      )
        return false;
      if (
        filters.marks &&
        filters.marks.value &&
        String(q.marks) !== filters.marks.value
      )
        return false;
      if (
        filters.section &&
        filters.section.value &&
        q.section !== filters.section.value
      )
        return false;
      if (
        filters.board &&
        filters.board.value &&
        q.board !== filters.board.value
      )
        return false;
      // Empty value means both qualifications, which is the default.
      if (
        filters.level &&
        filters.level.value &&
        p.level !== filters.level.value
      )
        return false;
      if (
        filters.group &&
        filters.group.value &&
        q.groups.indexOf(filters.group.value) === -1
      )
        return false;
      if (
        filters.topic &&
        filters.topic.value &&
        q.topics.indexOf(filters.topic.value) === -1
      )
        return false;
      return true;
    }

    function run() {
      var queryTokens = tokenise(els.query ? els.query.value : "");
      var scored = [];

      for (var i = 0; i < index.length; i++) {
        if (!passesFilters(index[i])) continue;
        var s = queryTokens.length ? score(index[i], queryTokens) : 0;
        if (s < 0) continue;
        scored.push({ record: index[i], score: s });
      }

      var mode = els.sort ? els.sort.value : "relevance";
      scored.sort(function (a, b) {
        if (mode === "marks") return b.record.q.marks - a.record.q.marks;
        if (
          mode === "newest" ||
          (mode === "relevance" && !queryTokens.length)
        ) {
          if (b.record.paper.year !== a.record.paper.year)
            return b.record.paper.year - a.record.paper.year;
          return a.record.q.questionNumber > b.record.q.questionNumber ? 1 : -1;
        }
        return b.score - a.score;
      });

      matches = scored;
      shown = PAGE_SIZE;
      render();
    }

    function render() {
      var slice = matches.slice(0, shown);
      var html = "";
      for (var i = 0; i < slice.length; i++) {
        html += cardHtml(slice[i].record, topics);
      }
      els.results.innerHTML = html;

      if (els.count) {
        els.count.textContent =
          matches.length === 0
            ? "No questions match"
            : matches.length === 1
              ? "1 question"
              : matches.length + " questions";
      }
      if (els.empty) els.empty.hidden = matches.length !== 0;
      if (els.more) {
        // Clamped, so the label cannot count below zero even if the button is
        // somehow clicked while it should be hidden.
        var remaining = Math.max(0, matches.length - shown);
        els.more.hidden = remaining === 0;
        els.more.textContent = "Show more (" + remaining + " remaining)";
      }
    }

    // ---- wiring

    var timer = null;
    if (els.query) {
      els.query.addEventListener("input", function () {
        if (timer) clearTimeout(timer);
        timer = setTimeout(run, DEBOUNCE_MS);
      });
      // Enter must not submit and reload the page; results are already live.
      els.query.addEventListener("keydown", function (e) {
        if (e.key === "Enter") e.preventDefault();
      });
    }
    Array.prototype.forEach.call(selects, function (sel) {
      sel.addEventListener("change", run);
    });
    if (els.sort) els.sort.addEventListener("change", run);
    if (els.more)
      els.more.addEventListener("click", function () {
        shown = Math.min(shown + PAGE_SIZE, matches.length);
        render();
      });
    if (els.clear)
      els.clear.addEventListener("click", function () {
        if (els.query) els.query.value = "";
        Array.prototype.forEach.call(selects, function (sel) {
          sel.value = "";
        });
        if (els.sort) els.sort.value = "relevance";
        run();
        if (els.query) els.query.focus();
      });
    if (els.controls) {
      els.controls.addEventListener("submit", function (e) {
        e.preventDefault();
      });
    }

    /* ?topic=<slug> and ?theme=<n> preset a filter without locking it.
     *
     * This is how the 38 topics that have questions but not enough for their
     * own page are still linked to from their revision notes: the notes page
     * points at /past-paper-questions/?topic=<slug> and the reader lands on a
     * filtered view they can widen. Unlike data-prefilter-*, the control stays
     * visible and changeable.
     */
    function applyQueryString() {
      var query = window.location.search;
      if (!query || query.length < 2) return;
      query
        .slice(1)
        .split("&")
        .forEach(function (pair) {
          var bits = pair.split("=");
          var key = decodeURIComponent(bits[0]);
          var value = decodeURIComponent((bits[1] || "").replace(/\+/g, " "));
          var sel = filters[key];
          if (!sel || !value) return;
          // Only accept a value the control actually offers, so a stale or
          // hand-edited URL cannot leave the page showing an empty result set
          // with no visible reason why.
          for (var i = 0; i < sel.options.length; i++) {
            if (sel.options[i].value === value) {
              sel.value = value;
              return;
            }
          }
        });
    }

    populate();
    applyQueryString();
    // A control is meaningless on a page already fixed to that value.
    function hideField(sel) {
      if (!sel) return;
      var wrap = sel.closest(".ppq-field");
      if (wrap) wrap.hidden = true;
    }
    if (preTopic) {
      hideField(filters.topic);
      hideField(filters.board);
      hideField(filters.group);
    }
    if (preBoard) hideField(filters.board);
    if (preGroup) hideField(filters.group);
    if (els.controls) els.controls.hidden = false;
    root.classList.add("is-enhanced");
    run();
  }

  // ---------------------------------------------------------------- boot

  function boot() {
    var roots = document.querySelectorAll("[data-question-search]");
    if (!roots.length) return;

    var url =
      roots[0].getAttribute("data-src") ||
      "/past-paper-questions/questions.json";

    fetch(url)
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (data) {
        Array.prototype.forEach.call(roots, function (root) {
          init(root, data);
        });
      })
      .catch(function () {
        // Leave the page exactly as served: the static question list and the
        // links to the PDFs all still work without this script.
        Array.prototype.forEach.call(roots, function (root) {
          var note = root.querySelector("[data-ppq-error]");
          if (note) note.hidden = false;
        });
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
