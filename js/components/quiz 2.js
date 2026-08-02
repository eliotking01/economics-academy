/* Practice questions - progressive enhancement for /practice-questions/ pages.
 *
 * The page is complete without this file: every stem, option and model answer
 * is in the static HTML, and the model answers are native <details>. All this
 * script adds is instant feedback, a running score, an end-of-quiz summary,
 * retry with a reshuffled order, and a best/last score in localStorage.
 *
 * Vanilla, no jQuery, loaded with defer. Nothing here fetches anything.
 *
 * Every element it reveals already occupies its space in the layout, so
 * enhancement shifts nothing on the page.
 */

(function () {
  "use strict";

  var STORE_PREFIX = "ea-quiz:v1:";
  var INDEX_KEY = STORE_PREFIX + "index";

  /* ------------------------------------------------------------- storage */

  // localStorage throws outright in some privacy modes, so every call is
  // guarded. A page whose storage is unavailable still works; it just
  // forgets. The probe write is what actually catches Safari's private mode.
  var storage = (function () {
    try {
      var probe = STORE_PREFIX + "probe";
      window.localStorage.setItem(probe, "1");
      window.localStorage.removeItem(probe);
      return window.localStorage;
    } catch (e) {
      return null;
    }
  })();

  function readJSON(key) {
    if (!storage) return null;
    try {
      var raw = storage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function writeJSON(key, value) {
    if (!storage) return false;
    try {
      storage.setItem(key, JSON.stringify(value));
      return true;
    } catch (e) {
      return false;
    }
  }

  function remember(key) {
    var index = readJSON(INDEX_KEY);
    if (!Array.isArray(index)) index = [];
    if (index.indexOf(key) === -1) {
      index.push(key);
      writeJSON(INDEX_KEY, index);
    }
  }

  function forget(key) {
    if (!storage) return;
    try {
      storage.removeItem(key);
    } catch (e) {
      /* nothing to do */
    }
    var index = readJSON(INDEX_KEY);
    if (Array.isArray(index)) {
      var at = index.indexOf(key);
      if (at !== -1) {
        index.splice(at, 1);
        writeJSON(INDEX_KEY, index);
      }
    }
  }

  /* --------------------------------------------------------------- setup */

  // .quiz-page is a question page; .practice-questions-page is the hub or a
  // board index. They look nothing alike and load different stylesheets, but
  // both read the same localStorage.
  var page = document.querySelector(".quiz-page, .practice-questions-page");
  if (!page) return;

  /* --------------------------------------------------------- index pages

     A hub or board index has no questions on it, only cards. Fill in the
     last score for any topic the student has already attempted, then stop.
     The span is empty in the markup and collapses when empty, so writing
     into it moves nothing. */

  var lastEls = page.querySelectorAll("[data-quiz-last]");
  if (lastEls.length) {
    Array.prototype.forEach.call(lastEls, function (el) {
      var saved = readJSON(STORE_PREFIX + el.getAttribute("data-quiz-last"));
      if (saved && typeof saved.last === "number") {
        el.textContent = "Last attempt: " + saved.last + "/" + saved.of;
      }
    });
  }

  /* Unit accordion on a board index. Same behaviour as the inline script on
     the notes board indexes: the whole card is clickable, the heading is a
     real <button> so it works from the keyboard, and clicks originating on
     the button are ignored by the card handler so one tap does not toggle
     twice. */

  Array.prototype.forEach.call(page.querySelectorAll(".topic-item"), function (item) {
    var button = item.querySelector(".topic-toggle");
    var panel = item.querySelector(".subtopic-list");
    var icon = item.querySelector(".toggle-icon");
    if (!button || !panel) return;

    function toggle() {
      var isOpen = panel.style.display === "block";
      panel.style.display = isOpen ? "none" : "block";
      button.setAttribute("aria-expanded", isOpen ? "false" : "true");
      if (icon) icon.textContent = isOpen ? "+" : "-";
    }

    button.addEventListener("click", function (event) {
      event.stopPropagation();
      toggle();
    });

    item.addEventListener("click", function (event) {
      // Let a topic link navigate without collapsing the panel under it.
      if (event.target.closest("a")) return;
      toggle();
    });
  });

  var list = page.querySelector(".quiz-list");
  var items = list ? Array.prototype.slice.call(list.querySelectorAll(".quiz-item")) : [];
  if (!items.length) return;

  var total = items.length;
  var first = items[0];
  var storeKey =
    STORE_PREFIX +
    (first.getAttribute("data-board") || "unknown") +
    ":" +
    (first.getAttribute("data-spec") || "unknown");

  var scoreEl = page.querySelector("[data-quiz-score]");
  var bestEl = page.querySelector("[data-quiz-best]");
  var barEl = page.querySelector("[data-quiz-bar]");
  var summaryEl = page.querySelector("[data-quiz-summary]");
  var summaryHeading = page.querySelector("[data-quiz-summary-heading]");
  var summaryText = page.querySelector("[data-quiz-summary-text]");
  var retryBtn = page.querySelector("[data-quiz-retry]");
  var resetBtn = page.querySelector("[data-quiz-reset]");

  var answered = 0;
  var correct = 0;

  /* ------------------------------------------------------------ rendering */

  function plural(n, word) {
    return n + " " + word + (n === 1 ? "" : "s");
  }

  function renderDashboard() {
    if (scoreEl) {
      scoreEl.textContent =
        answered === 0
          ? total + " questions in this set"
          : answered + " of " + total + " answered · " + correct + " correct";
    }
    if (barEl) {
      barEl.style.width = (answered / total) * 100 + "%";
    }
  }

  function renderBest() {
    if (!bestEl) return;
    var saved = readJSON(storeKey);
    if (!saved || typeof saved.best !== "number") {
      bestEl.textContent = "";
      if (resetBtn) resetBtn.classList.remove("is-available");
      return;
    }
    var text = "Best score: " + saved.best + "/" + saved.of;
    if (typeof saved.last === "number") {
      text += " · last attempt: " + saved.last + "/" + saved.of;
    }
    if (saved.lastAt) {
      text += " (" + saved.lastAt + ")";
    }
    bestEl.textContent = text;
    if (resetBtn) resetBtn.classList.add("is-available");
  }

  function save() {
    if (!storage) return;
    var saved = readJSON(storeKey) || {};
    var best = typeof saved.best === "number" ? Math.max(saved.best, correct) : correct;
    writeJSON(storeKey, {
      best: best,
      of: total,
      last: correct,
      lastAt: new Date().toISOString().slice(0, 10)
    });
    remember(storeKey);
    renderBest();
  }

  function verdict(score) {
    var share = score / total;
    if (share === 1) return "Full marks. Nothing left to fix on this topic.";
    if (share >= 0.8) return "A strong set. Read the model answers for the ones you missed.";
    if (share >= 0.5)
      return "A reasonable start. The model answers below name the specific mistake behind each wrong option.";
    return "Worth going back to the notes before you try again — then retake this set.";
  }

  function finish() {
    if (!summaryEl) return;
    if (summaryHeading) {
      summaryHeading.textContent = "You scored " + correct + " out of " + total;
    }
    if (summaryText) {
      summaryText.textContent = verdict(correct);
    }
    summaryEl.hidden = false;
    save();
  }

  /* --------------------------------------------------------- interaction */

  function answer(item, chosen) {
    if (item.classList.contains("is-answered")) return;

    var key = item.getAttribute("data-answer");
    var right = chosen === key;

    item.classList.add("is-answered", right ? "is-correct" : "is-incorrect");

    var options = item.querySelectorAll(".quiz-option");
    Array.prototype.forEach.call(options, function (option) {
      var input = option.querySelector("input[type='radio']");
      if (!input) return;
      // Radios stay enabled but non-interactive, so the chosen answer is
      // still announced and still reachable by keyboard for review.
      input.setAttribute("readonly", "readonly");
      if (input.value === key) {
        option.classList.add("is-correct");
      } else if (input.value === chosen) {
        option.classList.add("is-chosen-wrong");
      }
    });

    var feedback = item.querySelector("[data-quiz-feedback]");
    if (feedback) {
      feedback.textContent = right
        ? "Correct — " + key + " is right."
        : "Not quite — you chose " + chosen + ", the answer is " + key + ".";
      feedback.classList.add(right ? "is-correct" : "is-incorrect");
      feedback.hidden = false;
    }

    // Getting it wrong is the moment the explanation is worth reading, so
    // open it. A correct answer leaves the <details> for the student to open.
    var model = item.querySelector(".quiz-model");
    if (model && !right) model.open = true;

    answered += 1;
    if (right) correct += 1;
    renderDashboard();

    if (answered === total) finish();
  }

  function reset(item) {
    item.classList.remove("is-answered", "is-correct", "is-incorrect");

    Array.prototype.forEach.call(item.querySelectorAll(".quiz-option"), function (option) {
      option.classList.remove("is-correct", "is-chosen-wrong");
      var input = option.querySelector("input[type='radio']");
      if (input) {
        input.removeAttribute("readonly");
        input.checked = false;
      }
    });

    var feedback = item.querySelector("[data-quiz-feedback]");
    if (feedback) {
      feedback.textContent = "";
      feedback.classList.remove("is-correct", "is-incorrect");
      feedback.hidden = true;
    }

    var model = item.querySelector(".quiz-model");
    if (model) model.open = false;
  }

  function renumber() {
    Array.prototype.forEach.call(list.querySelectorAll(".quiz-item"), function (item, i) {
      var number = item.querySelector(".quiz-number");
      if (number) number.textContent = i + 1 + ".";
    });
  }

  function shuffle() {
    var order = Array.prototype.slice.call(list.querySelectorAll(".quiz-item"));
    for (var i = order.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var swap = order[i];
      order[i] = order[j];
      order[j] = swap;
    }
    var fragment = document.createDocumentFragment();
    order.forEach(function (item) {
      fragment.appendChild(item);
    });
    list.appendChild(fragment);
    renumber();
  }

  function retry() {
    items.forEach(reset);
    answered = 0;
    correct = 0;
    shuffle();
    if (summaryEl) summaryEl.hidden = true;
    renderDashboard();
    var top = list.querySelector(".quiz-item");
    if (top) {
      top.scrollIntoView({ behavior: "smooth", block: "start" });
      var firstInput = top.querySelector("input[type='radio']");
      if (firstInput) firstInput.focus({ preventScroll: true });
    }
  }

  /* ------------------------------------------------------------- wire up */

  list.addEventListener("change", function (event) {
    var input = event.target;
    if (!input || input.type !== "radio") return;
    var item = input.closest ? input.closest(".quiz-item") : null;
    if (item) answer(item, input.value);
  });

  // A readonly radio still toggles on click, so block the interaction on a
  // question that has already been answered.
  list.addEventListener("click", function (event) {
    var item = event.target.closest ? event.target.closest(".quiz-item") : null;
    if (item && item.classList.contains("is-answered")) {
      var option = event.target.closest(".quiz-option");
      if (option) event.preventDefault();
    }
  });

  if (retryBtn) retryBtn.addEventListener("click", retry);

  if (resetBtn) {
    resetBtn.addEventListener("click", function () {
      forget(storeKey);
      renderBest();
      resetBtn.classList.remove("is-available");
    });
  }

  // Radios can survive a soft reload with their checked state intact, which
  // would leave the page showing answers the score knows nothing about.
  items.forEach(reset);
  renderDashboard();
  renderBest();
})();
