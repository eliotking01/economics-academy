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

  // ---------------------------------------------------------------- options

  /* The board-shaped filters - Qualification, Theme / area, Paper section and
   * Topic - mean different things on each board, so their option lists are
   * built per board. With a board in play the list is that board's values,
   * flat, exactly as the pre-filtered pages have always shown it. With no
   * board the values sit under <optgroup>s labelled with the board names from
   * data.boards - never hard-coded - so the two numbering systems share one
   * dropdown without interleaving: before this, the master page's Topic list
   * held 151 topics with 28 spec codes appearing twice and nothing saying
   * which board each belonged to.
   *
   * Pure functions of the data, so scripts/test_question_search.js can
   * exercise them without a DOM. Each returns a list whose entries are either
   * plain values or {label, values} groups; optionList() renders both.
   */

  /* One {name, values} entry per board that has any values, in
   * data.boards order. */
  function valuesByBoard(data, valuesFor) {
    var lists = [];
    data.boards.forEach(function (b) {
      var values = valuesFor(b.board);
      if (values.length) lists.push({ name: b.name, values: values });
    });
    return lists;
  }

  /* Topic and Theme / area: every value belongs to exactly one board, so with
   * no board in play the whole list is grouped, one <optgroup> per board. A
   * list only one board populates comes back flat - a lone group label would
   * be noise. */
  function groupedByBoard(data, board, valuesFor) {
    if (board) return valuesFor(board);
    var lists = valuesByBoard(data, valuesFor);
    if (lists.length === 1) return lists[0].values;
    return lists.map(function (l) {
      return { label: l.name, values: l.values };
    });
  }

  /* Paper section and Qualification: most values exist on every board and
   * stay flat; one that only some boards have (Edexcel's Section C, AS Level)
   * is listed under its board's name, so nothing implies the other board
   * offers it. */
  function sharedThenBoardSpecific(data, board, valuesFor) {
    if (board) return valuesFor(board);
    var lists = valuesByBoard(data, valuesFor);
    if (lists.length === 1) return lists[0].values;
    var shared = lists[0].values.filter(function (v) {
      return lists.every(function (l) {
        return l.values.indexOf(v) !== -1;
      });
    });
    var out = shared.slice();
    lists.forEach(function (l) {
      var own = l.values.filter(function (v) {
        return shared.indexOf(v) === -1;
      });
      if (own.length) out.push({ label: l.name, values: own });
    });
    return out;
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

    // Group slug -> record (for labels) and -> board (for adopting a board
    // from a chosen theme or area).
    var groupsBySlug = {};
    var groupBoard = {};
    data.boards.forEach(function (b) {
      b.groups.forEach(function (g) {
        groupsBySlug[g.slug] = g;
        groupBoard[g.slug] = b.board;
      });
    });

    // Only the master page lets the Board select drive the other dropdowns.
    // A pre-filtered page fixed its board at build time and keeps exactly the
    // behaviour it shipped with: flat lists, no optgroups, no narrowing.
    var cascades = !!filters.board && !preBoard && !preTopic;

    /* The board narrowing the board-shaped selects. A pre-filtered page fixes
     * it (a topic implies its board); the master page reads the Board select,
     * which starts empty - "Both boards". */
    function effectiveBoard() {
      if (preBoard) return preBoard;
      if (preTopic && topics[preTopic]) return topics[preTopic].board;
      return filters.board && filters.board.value ? filters.board.value : "";
    }

    var shown = PAGE_SIZE;
    var matches = [];

    function optionList(sel, values, labeller) {
      var prev = sel.value;
      function option(v) {
        return (
          '<option value="' +
          escapeHtml(v) +
          '">' +
          escapeHtml(labeller(v)) +
          "</option>"
        );
      }
      var html =
        '<option value="">' + sel.getAttribute("data-ppq-all") + "</option>";
      values.forEach(function (v) {
        if (v && v.values) {
          html += '<optgroup label="' + escapeHtml(v.label) + '">';
          v.values.forEach(function (w) {
            html += option(w);
          });
          html += "</optgroup>";
        } else {
          html += option(v);
        }
      });
      sel.innerHTML = html;
      // The cascade rebuilds lists the reader may already have chosen from:
      // keep their choice when the new list still offers it, otherwise fall
      // back to "All ..." rather than leaving the select pointing at nothing.
      if (prev) {
        sel.value = prev;
        if (sel.value !== prev) sel.value = "";
      }
    }

    // ---- the board-shaped lists, one small derivation each

    function levelsFor(board) {
      var levels = [];
      data.questions.forEach(function (q) {
        if (board && q.board !== board) return;
        var level = data.papers[q.p].level;
        if (levels.indexOf(level) === -1) levels.push(level);
      });
      // "a-level" before "as-level" happens to be alphabetical, and is also the
      // order a student expects: the qualification most of them are sitting
      // comes first.
      return levels.sort();
    }

    function sectionsFor(board) {
      var sections = [];
      data.questions.forEach(function (q) {
        if (board && q.board !== board) return;
        if (sections.indexOf(q.section) === -1) sections.push(q.section);
      });
      return sections.sort();
    }

    // Only the sections of the board in play, so an Edexcel page never
    // offers "Microeconomics" and vice versa.
    function groupSlugsFor(board) {
      var slugs = [];
      data.boards.forEach(function (b) {
        if (board && b.board !== board) return;
        b.groups.forEach(function (g) {
          slugs.push(g.slug);
        });
      });
      return slugs;
    }

    function topicSlugsFor(board) {
      // A chosen Theme / area narrows Topic to its own topics; each topic
      // sits under exactly one group. Only the visible control narrows -
      // never data-prefilter-group, so a theme page's Topic list keeps
      // offering the whole board, as it always has.
      var group = filters.group && cascades ? filters.group.value : "";
      return Object.keys(topics)
        .filter(function (s) {
          if (board && topics[s].board !== board) return false;
          if (group && topics[s].group !== group) return false;
          return true;
        })
        .sort(function (a, b) {
          return topics[a].spec.localeCompare(topics[b].spec, "en", {
            numeric: true,
          });
        });
    }

    /* The four selects the Board choice reshapes. Runs once on every page,
     * and again on the master page whenever the board in play changes -
     * optionList() keeps any still-valid choice. Paper, Marks, Year and Sort
     * are deliberately not here: they are the same shape on both boards, and
     * a dropdown that reshuffles when you touch a different one is its own
     * kind of confusing. */
    function populateBoardShaped() {
      var board = effectiveBoard();
      if (filters.level)
        optionList(
          filters.level,
          sharedThenBoardSpecific(data, board, levelsFor),
          function (v) {
            return v === "as-level" ? "AS Level only" : "A Level only";
          },
        );
      if (filters.group)
        optionList(
          filters.group,
          groupedByBoard(data, board, groupSlugsFor),
          function (v) {
            var g = groupsBySlug[v];
            return g ? g.label + ": " + g.name : v;
          },
        );
      if (filters.section)
        optionList(
          filters.section,
          sharedThenBoardSpecific(data, board, sectionsFor),
          function (v) {
            return "Section " + v;
          },
        );
      if (filters.topic)
        optionList(
          filters.topic,
          groupedByBoard(data, board, topicSlugsFor),
          function (s) {
            return topics[s].spec + " " + topics[s].shortTitle;
          },
        );
    }

    /* A topic or theme belongs to exactly one board (an invariant
     * scripts/test_question_search.js pins), so choosing one while the Board
     * select still says "Both boards" decides the board, and the other
     * dropdowns narrow to match. */
    function adoptBoard(name, value) {
      if (!cascades || !value || filters.board.value) return;
      var board = "";
      if (name === "topic" && topics[value]) board = topics[value].board;
      else if (name === "group") board = groupBoard[value] || "";
      if (board) filters.board.value = board;
    }

    function populate() {
      var papers = [];
      var years = [];
      var marks = [];
      data.questions.forEach(function (q) {
        var p = data.papers[q.p];
        if (papers.indexOf(p.paper) === -1) papers.push(p.paper);
        if (years.indexOf(p.year) === -1) years.push(p.year);
        if (marks.indexOf(q.marks) === -1) marks.push(q.marks);
      });
      papers.sort();
      years.sort().reverse();
      marks.sort(function (a, b) {
        return a - b;
      });

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
      populateBoardShaped();
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
      sel.addEventListener("change", function () {
        if (cascades) {
          var name = sel.getAttribute("data-ppq-filter");
          adoptBoard(name, sel.value);
          if (name === "board" || name === "group" || name === "topic")
            populateBoardShaped();
        }
        run();
      });
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
        // With no board in play any more, the grouped "Both boards" lists
        // come back in full.
        if (cascades) populateBoardShaped();
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
    // A ?topic= or ?theme= link decides the board just as a click on the
    // control would, and the lists narrow to that board before first paint.
    // Order matters: the cascade runs AFTER the query string is applied, so
    // it can never empty a select the URL just set - and optionList() keeps
    // any value still valid on the adopted board.
    if (cascades) {
      if (filters.topic) adoptBoard("topic", filters.topic.value);
      if (filters.group) adoptBoard("group", filters.group.value);
      populateBoardShaped();
    }
    // The panel is already on screen and already the right height - the page
    // shipped it that way, with the fields this page fixes marked hidden in the
    // HTML. All that is left is to make it usable.
    setControlsEnabled(root, true);
    root.classList.add("is-enhanced");
    run();
  }

  // ---------------------------------------------------------------- enabling

  // The filter panel ships visible and disabled, so it occupies its final
  // height from first paint and nothing moves when the data lands. It used to
  // ship `hidden` and be revealed here, after a 414 KB fetch, which measured
  // CLS 0.253 - the worst Core Web Vital on the site. PH08-035.
  //
  // Enabled only once the data is in, because until then the selects have no
  // options and the search index does not exist, so the controls would look
  // ready and do nothing.
  function setControlsEnabled(root, on) {
    var controls = root.querySelector("[data-ppq-controls]");
    if (!controls) return;
    var fields = controls.querySelectorAll("input, select, button");
    Array.prototype.forEach.call(fields, function (el) {
      el.disabled = !on;
    });
    if (on) controls.removeAttribute("aria-busy");
    else controls.setAttribute("aria-busy", "true");
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
        // links to the PDFs all still work without this script. The controls
        // stay disabled - they shipped that way and there is no index to drive
        // them - and the error note says so. Showing the note is the only
        // change, so this path causes no layout shift either.
        Array.prototype.forEach.call(roots, function (root) {
          setControlsEnabled(root, false);
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
