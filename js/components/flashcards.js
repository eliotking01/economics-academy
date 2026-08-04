/* Flashcards - progressive enhancement for /flashcards/ deck pages.
 *
 * The generated page is complete without this file: sample cards, the topic
 * list and every link are static HTML. This script fetches the deck's JSON
 * payload (the only other component that fetches is question-search.js, and
 * the boot pattern here is copied from it), builds the interactive player
 * into [data-fc-mount], and adds .is-enhanced to the root so the samples
 * hand over.
 *
 * Spaced repetition is a three-box Leitner system per deck, persisted in
 * localStorage under "ea-flashcards:v1:" with the same guarded-storage
 * helpers as quiz.js. Box 1 is due every session, box 2 every second, box 3
 * every third. "Again" sends a card back to box 1 and requeues it later in
 * the same session; "Got it" promotes it.
 *
 * Analytics: the site's first custom GA4 events - deck_start, card_flip,
 * card_rated, deck_complete, deck_print - all through track(), which no-ops
 * silently when gtag is absent.
 *
 * Vanilla, no jQuery, loaded with defer.
 */

(function () {
  "use strict";

  var STORE_PREFIX = "ea-flashcards:v1:";
  var INDEX_KEY = STORE_PREFIX + "index";
  var BOX_INTERVALS = { 1: 1, 2: 2, 3: 3 };
  var REQUEUE_GAP = 5;

  /* ------------------------------------------------------------- storage */

  // Copied from quiz.js: localStorage throws outright in some privacy
  // modes, so every call is guarded and the probe write catches Safari's
  // private mode. A page whose storage is unavailable still works; it just
  // forgets between visits.
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

  /* ----------------------------------------------------------- analytics */

  function track(name, params) {
    if (typeof window.gtag === "function") {
      window.gtag("event", name, params || {});
    }
  }

  /* ------------------------------------------------------------- helpers */

  function el(tag, className, html) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (html) node.innerHTML = html;
    return node;
  }

  function shuffle(list) {
    for (var i = list.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var swap = list[i];
      list[i] = list[j];
      list[j] = swap;
    }
    return list;
  }

  function queryTopic() {
    var match = /[?&]topic=([^&]+)/.exec(window.location.search);
    return match ? decodeURIComponent(match[1]) : "";
  }

  /* -------------------------------------------------------------- player */

  function init(root, data) {
    var deckKey = STORE_PREFIX + "deck:" + data.deckId;
    var mount = root.querySelector("[data-fc-mount]");
    if (!mount) return;

    var state = readJSON(deckKey);
    if (!state || typeof state !== "object" || !state.cards) {
      state = { session: 0, cards: {} };
    }
    state.session += 1;
    writeJSON(deckKey, state);
    remember(deckKey);

    var baseParams = {
      board: data.board,
      theme: data.theme,
      deck_id: data.deckId,
    };

    /* ---- deck state for this visit */

    var topicFilter = queryTopic();
    var queue = [];
    var position = 0;
    var flipped = false;
    var seen = {};
    var gotCount = 0;
    var ratedCount = 0;
    var startedAt = null;
    var flippedIds = {};

    function cardState(id) {
      return state.cards[id] || null;
    }

    function isDue(card) {
      var record = cardState(card.id);
      if (!record) return true;
      var interval = BOX_INTERVALS[record.box] || 1;
      return state.session - record.seen >= interval;
    }

    function pool() {
      var cards = data.cards;
      if (!topicFilter) return cards.slice();
      return cards.filter(function (card) {
        return card.subtopic === topicFilter;
      });
    }

    function buildQueue() {
      var cards = pool();
      var due = cards.filter(isDue);
      queue = due.length ? due : cards.slice();
      position = 0;
      flipped = false;
      seen = {};
      gotCount = 0;
      ratedCount = 0;
      startedAt = new Date().getTime();
      return due.length;
    }

    /* ---- DOM */

    var toolbar = el("div", "fc-toolbar");
    var topicSelect = document.createElement("select");
    topicSelect.setAttribute("data-fc-topic", "");
    var allOption = document.createElement("option");
    allOption.value = "";
    allOption.textContent = "All topics (" + data.cards.length + " cards)";
    topicSelect.appendChild(allOption);
    data.topics.forEach(function (topic) {
      var option = document.createElement("option");
      option.value = topic.subtopic;
      option.textContent = topic.title + " (" + topic.count + ")";
      if (topic.subtopic === topicFilter) option.selected = true;
      topicSelect.appendChild(option);
    });
    var topicLabel = el("label", null, "Topic ");
    topicLabel.appendChild(topicSelect);
    toolbar.appendChild(topicLabel);

    var shuffleButton = el("button", "fc-tool", "Shuffle");
    shuffleButton.type = "button";
    var restartButton = el("button", "fc-tool", "Restart");
    restartButton.type = "button";
    var printButton = el("button", "fc-tool", "Print this deck");
    printButton.type = "button";
    toolbar.appendChild(shuffleButton);
    toolbar.appendChild(restartButton);
    toolbar.appendChild(printButton);

    var progress = el("div", "fc-progress");
    var progressLabel = el("p", "fc-progress-label");
    var bar = el("div", "fc-bar");
    var barFill = el("div", "fc-bar-fill");
    bar.appendChild(barFill);
    progress.appendChild(progressLabel);
    progress.appendChild(bar);

    var stage = el("div", "fc-stage");
    var card = el("button", "fc-card");
    card.type = "button";
    card.setAttribute("aria-expanded", "false");
    card.setAttribute(
      "aria-label",
      "Flashcard. Activate to flip between question and answer."
    );
    var cardInner = el("span", "fc-card-inner");
    var front = el("span", "fc-face fc-front");
    var back = el("span", "fc-face fc-back");
    back.setAttribute("aria-live", "polite");
    back.setAttribute("aria-hidden", "true");
    cardInner.appendChild(front);
    cardInner.appendChild(back);
    card.appendChild(cardInner);

    var hint = el(
      "p",
      "fc-hint",
      "Space or click flips &middot; arrow keys move &middot; " +
        "1 = again &middot; 2 = got it"
    );

    var nav = el("div", "fc-nav");
    var prevButton = el("button", "fc-step", "&larr; Previous");
    prevButton.type = "button";
    var rate = el("div", "fc-rate");
    rate.hidden = true;
    var againButton = el("button", "fc-again", "Again");
    againButton.type = "button";
    var gotButton = el("button", "fc-got", "Got it");
    gotButton.type = "button";
    rate.appendChild(againButton);
    rate.appendChild(gotButton);
    var nextButton = el("button", "fc-step", "Next &rarr;");
    nextButton.type = "button";
    nav.appendChild(prevButton);
    nav.appendChild(rate);
    nav.appendChild(nextButton);

    var meta = el("p", "fc-meta");
    stage.appendChild(card);
    stage.appendChild(hint);
    stage.appendChild(nav);
    stage.appendChild(meta);

    var summary = el("div", "fc-summary");
    summary.hidden = true;

    var printsheet = el("div", "fc-printsheet");
    printsheet.setAttribute("data-fc-printsheet", "");
    printsheet.hidden = true;

    mount.appendChild(toolbar);
    mount.appendChild(progress);
    mount.appendChild(stage);
    mount.appendChild(summary);
    mount.appendChild(printsheet);

    /* ---- rendering */

    function faceHTML(item, side) {
      var label =
        '<span class="fc-face-label">' +
        (side === "front" ? "Question" : "Answer") +
        "</span>";
      if (side === "front") return label + item.front;
      var extras = "";
      if (item.formulaHtml) {
        extras += '<span class="fc-formula">' + item.formulaHtml + "</span>";
      }
      if (item.svgRef) {
        extras +=
          '<img class="fc-diagram" src="' +
          item.svgRef +
          '" alt="' +
          item.svgAlt.replace(/"/g, "&quot;") +
          '" width="800" height="600" />';
      }
      return label + extras + item.back;
    }

    function currentCard() {
      return queue[position] || null;
    }

    function renderCard() {
      var item = currentCard();
      if (!item) {
        showSummary();
        return;
      }
      summary.hidden = true;
      stage.style.display = "";
      progress.style.display = "";
      flipped = false;
      card.classList.remove("is-flipped");
      card.setAttribute("aria-expanded", "false");
      back.setAttribute("aria-hidden", "true");
      front.setAttribute("aria-hidden", "false");
      front.innerHTML = faceHTML(item, "front");
      back.innerHTML = faceHTML(item, "back");
      rate.hidden = true;
      seen[item.id] = true;
      progressLabel.textContent =
        "Card " + (position + 1) + " of " + queue.length;
      barFill.style.width =
        Math.round(((position + 1) / queue.length) * 100) + "%";
      meta.innerHTML =
        item.specCode +
        " &middot; " +
        item.cardType +
        " &middot; " +
        item.difficulty +
        ' &middot; <a href="' +
        item.notesUrl +
        '">Read the notes</a>';
    }

    function flip() {
      var item = currentCard();
      if (!item) return;
      flipped = !flipped;
      card.classList.toggle("is-flipped", flipped);
      card.setAttribute("aria-expanded", flipped ? "true" : "false");
      back.setAttribute("aria-hidden", flipped ? "false" : "true");
      front.setAttribute("aria-hidden", flipped ? "true" : "false");
      rate.hidden = !flipped;
      if (flipped && !flippedIds[item.id]) {
        flippedIds[item.id] = true;
        track("card_flip", {
          board: baseParams.board,
          theme: baseParams.theme,
          deck_id: baseParams.deck_id,
          card_id: item.id,
          card_type: item.cardType,
        });
      }
    }

    function step(delta) {
      if (!queue.length) return;
      position += delta;
      if (position < 0) position = 0;
      if (position >= queue.length) {
        showSummary();
        return;
      }
      renderCard();
    }

    function rateCard(got) {
      var item = currentCard();
      if (!item || !flipped) return;
      var record = cardState(item.id) || { box: 0, seen: 0 };
      record.box = got ? Math.min(3, (record.box || 0) + 1) : 1;
      record.seen = state.session;
      state.cards[item.id] = record;
      writeJSON(deckKey, state);
      ratedCount += 1;
      if (got) gotCount += 1;
      track("card_rated", {
        board: baseParams.board,
        theme: baseParams.theme,
        deck_id: baseParams.deck_id,
        card_id: item.id,
        rating: got ? "got_it" : "again",
        box: record.box,
      });
      if (!got) {
        var at = Math.min(queue.length, position + 1 + REQUEUE_GAP);
        queue.splice(at, 0, item);
      }
      step(1);
    }

    function showSummary() {
      stage.style.display = "none";
      progress.style.display = "none";
      var total = ratedCount;
      var pct = total ? Math.round((gotCount / total) * 100) : 0;
      var boxes = { learning: 0, improving: 0, mastered: 0 };
      pool().forEach(function (item) {
        var record = cardState(item.id);
        if (!record || record.box <= 1) boxes.learning += 1;
        else if (record.box === 2) boxes.improving += 1;
        else boxes.mastered += 1;
      });
      summary.innerHTML =
        "<h2>Session complete</h2>" +
        "<p>You rated " +
        total +
        " card" +
        (total === 1 ? "" : "s") +
        " and knew <strong>" +
        pct +
        "%</strong> first time.</p>" +
        "<p>This deck on this device: <strong>" +
        boxes.learning +
        "</strong> still learning &middot; <strong>" +
        boxes.improving +
        "</strong> improving &middot; <strong>" +
        boxes.mastered +
        "</strong> mastered. Cards you marked ‘Again’ will come " +
        "back sooner.</p>";
      var again = el("div", "fc-nav");
      var goAgain = el("button", "fc-tool", "Study again");
      goAgain.type = "button";
      goAgain.addEventListener("click", restart);
      again.appendChild(goAgain);
      summary.appendChild(again);
      summary.hidden = false;
      track("deck_complete", {
        board: baseParams.board,
        theme: baseParams.theme,
        deck_id: baseParams.deck_id,
        cards_seen: total,
        pct_got_it: pct,
        duration_seconds: startedAt
          ? Math.round((new Date().getTime() - startedAt) / 1000)
          : 0,
      });
    }

    function restart() {
      var due = buildQueue();
      renderCard();
      track("deck_start", {
        board: baseParams.board,
        theme: baseParams.theme,
        deck_id: baseParams.deck_id,
        cards_due: due,
      });
    }

    /* ---- print */

    function fillPrintsheet() {
      if (printsheet.childNodes.length) return;
      var heading = el("h2", null, root.getAttribute("data-deck-label"));
      printsheet.appendChild(heading);
      data.cards.forEach(function (item) {
        var block = el("div", "fc-print-item");
        block.appendChild(el("div", "fc-print-front", item.front));
        block.appendChild(el("div", "fc-print-back", faceHTML(item, "back")));
        printsheet.appendChild(block);
      });
    }

    function printDeck() {
      fillPrintsheet();
      printsheet.hidden = false;
      root.classList.add("is-printing");
      track("deck_print", baseParams);
      window.print();
    }

    /* ---- events */

    card.addEventListener("click", flip);
    prevButton.addEventListener("click", function () {
      step(-1);
    });
    nextButton.addEventListener("click", function () {
      step(1);
    });
    againButton.addEventListener("click", function () {
      rateCard(false);
    });
    gotButton.addEventListener("click", function () {
      rateCard(true);
    });
    restartButton.addEventListener("click", restart);
    shuffleButton.addEventListener("click", function () {
      shuffle(queue);
      position = 0;
      renderCard();
    });
    printButton.addEventListener("click", printDeck);
    window.addEventListener("beforeprint", fillPrintsheet);
    window.addEventListener("afterprint", function () {
      printsheet.hidden = true;
      root.classList.remove("is-printing");
    });

    topicSelect.addEventListener("change", function () {
      topicFilter = topicSelect.value;
      restart();
    });

    document.addEventListener("keydown", function (event) {
      var target = event.target;
      var name = target && target.tagName;
      if (name === "INPUT" || name === "SELECT" || name === "TEXTAREA") return;
      if (summary.hidden === false && event.key !== "ArrowLeft") return;
      if (event.key === " " || event.key === "Spacebar") {
        if (target === card) return; // the button click already flips
        event.preventDefault();
        flip();
      } else if (event.key === "ArrowRight") {
        step(1);
      } else if (event.key === "ArrowLeft") {
        step(-1);
      } else if (event.key === "1") {
        rateCard(false);
      } else if (event.key === "2") {
        rateCard(true);
      }
    });

    var touchX = null;
    var touchY = null;
    stage.addEventListener("touchstart", function (event) {
      if (event.touches.length !== 1) return;
      touchX = event.touches[0].clientX;
      touchY = event.touches[0].clientY;
    });
    stage.addEventListener("touchend", function (event) {
      if (touchX === null) return;
      var dx = event.changedTouches[0].clientX - touchX;
      var dy = event.changedTouches[0].clientY - touchY;
      touchX = null;
      touchY = null;
      if (Math.abs(dx) > 44 && Math.abs(dy) < 60) {
        step(dx < 0 ? 1 : -1);
      }
    });

    /* ---- go */

    root.classList.add("is-enhanced");
    var due = buildQueue();
    renderCard();
    track("deck_start", {
      board: baseParams.board,
      theme: baseParams.theme,
      deck_id: baseParams.deck_id,
      cards_due: due,
    });
  }

  /* ---------------------------------------------------------------- boot */

  function boot() {
    var roots = document.querySelectorAll("[data-flashcards]");
    if (!roots.length) return;
    var url = roots[0].getAttribute("data-src");
    if (!url) return;
    fetch(url)
      .then(function (response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
      })
      .then(function (data) {
        Array.prototype.forEach.call(roots, function (root) {
          init(root, data);
        });
      })
      .catch(function () {
        // The static page stands on its own: samples stay visible.
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
