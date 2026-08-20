#!/usr/bin/env python3
"""Drive the real flashcard player and assert its behaviour end to end.

    python3 -m http.server 8899
    python3 _working/flashcards/qa/functional.py

Covers Phase 3 item 4: flip, shuffle, again/got-it and the re-queue, session
summary, localStorage reset, keyboard shortcuts, swipe, reduced motion, and
that SVG diagram cards still render.

**Each group runs in its own fresh page load.** A single long script sharing
one page was tried first and produced four false failures: the groups inherited
each other's queue position and Leitner boxes, and once an earlier group had
run the queue out, the summary was showing - at which point the keydown handler
deliberately ignores every key but ArrowLeft, so the later keyboard and swipe
checks could not pass. The player was correct; the harness was not. One load
per group removes the cross-talk entirely, at the cost of a few seconds.

Results come back by postMessage because --dump-dom only serialises the
top-level document.
"""

import html as htmlmod
import json
import pathlib
import re
import subprocess
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE = "http://localhost:8899"
FRAME = "/_working/flashcards/qa/frame.html"
DECK_PAGE = "flashcards/edexcel-a/theme-2/index.html"

PRELUDE = r"""
<script>
window.__qa = (function () {
  var results = [];
  function check(name, cond, detail) {
    results.push({ name: name, pass: !!cond, detail: detail || "" });
  }
  function press(key) {
    document.dispatchEvent(new KeyboardEvent("keydown",
      { key: key, bubbles: true }));
  }
  function touch(node, type, x) {
    var t = { clientX: x, clientY: 100 };
    var ev = new Event(type, { bubbles: true });
    ev.touches = type === "touchend" ? [] : [t];
    ev.changedTouches = [t];
    node.dispatchEvent(ev);
  }
  function tool(root, text) {
    var found = null;
    Array.prototype.forEach.call(root.querySelectorAll(".fc-tool"),
      function (b) { if (b.textContent === text) found = b; });
    return found;
  }
  function num(root, which) {
    var parts = root.querySelector(".fc-progress-label")
      .textContent.split(" of ");
    return parseInt(which === "pos" ? parts[0].replace(/\D/g, "") : parts[1], 10);
  }
  function done() {
    window.parent.postMessage(
      { qa: "measure", rows: JSON.stringify(results) }, "*");
  }
  return { check: check, press: press, touch: touch, tool: tool,
           num: num, done: done, results: results };
})();
</script>
"""

GROUPS = {
    "flip": r"""
    var card = root.querySelector(".fc-card");
    var front = root.querySelector(".fc-front");
    var back = root.querySelector(".fc-back");
    var rate = root.querySelector(".fc-rate");
    qa.check("player mounted", !!card && !!front && !!back);
    qa.check("enhanced class set", root.classList.contains("is-enhanced"));
    qa.check("starts unflipped", !card.classList.contains("is-flipped"));
    card.click();
    qa.check("click flips", card.classList.contains("is-flipped"));
    qa.check("aria-expanded tracks flip",
      card.getAttribute("aria-expanded") === "true");
    qa.check("answer revealed to assistive tech",
      back.getAttribute("aria-hidden") === "false" &&
      front.getAttribute("aria-hidden") === "true");
    qa.check("rate buttons appear when flipped", rate.hidden === false);
    card.click();
    qa.check("click flips back", !card.classList.contains("is-flipped"));
    qa.check("rate buttons hide again", rate.hidden === true);
    """,

    "keyboard-nav": r"""
    var card = root.querySelector(".fc-card");
    qa.press(" ");
    qa.check("space flips", card.classList.contains("is-flipped"));
    qa.press(" ");
    qa.check("space flips back", !card.classList.contains("is-flipped"));
    var pos = qa.num(root, "pos");
    qa.press("ArrowRight");
    qa.check("ArrowRight advances", qa.num(root, "pos") === pos + 1,
      pos + " -> " + qa.num(root, "pos"));
    qa.press("ArrowLeft");
    qa.check("ArrowLeft goes back", qa.num(root, "pos") === pos);
    """,

    "keyboard-rate": r"""
    var card = root.querySelector(".fc-card");
    var pos = qa.num(root, "pos");
    qa.press("2");
    qa.check("key '2' is ignored until the card is flipped",
      qa.num(root, "pos") === pos);
    card.click();
    qa.press("2");
    qa.check("key '2' rates got-it and advances",
      qa.num(root, "pos") === pos + 1, pos + " -> " + qa.num(root, "pos"));
    var len = qa.num(root, "total");
    card.click();
    qa.press("1");
    qa.check("key '1' rates again and re-queues",
      qa.num(root, "total") === len + 1, len + " -> " + qa.num(root, "total"));
    """,

    "requeue": r"""
    var card = root.querySelector(".fc-card");
    var again = root.querySelector(".fc-again");
    var got = root.querySelector(".fc-got");
    var total = qa.num(root, "total");
    card.click();
    again.click();
    qa.check("'again' re-queues the card (queue grows by one)",
      qa.num(root, "total") === total + 1,
      total + " -> " + qa.num(root, "total"));
    var afterAgain = qa.num(root, "total");
    card.click();
    got.click();
    qa.check("'got it' does not re-queue",
      qa.num(root, "total") === afterAgain,
      afterAgain + " -> " + qa.num(root, "total"));
    var keys = Object.keys(window.localStorage);
    var v2 = keys.filter(function (k) { return k.indexOf("ea-flashcards:v2:") === 0; });
    var v1 = keys.filter(function (k) { return k.indexOf("ea-flashcards:v1:") === 0; });
    qa.check("progress saved under the v2 prefix", v2.length > 0, v2.join(","));
    qa.check("no v1 keys written", v1.length === 0, v1.join(","));
    var deckKey = v2.filter(function (k) { return k.indexOf(":deck:") !== -1; })[0];
    var state = JSON.parse(window.localStorage.getItem(deckKey));
    var boxes = Object.keys(state.cards).map(function (id) { return state.cards[id].box; });
    qa.check("'got it' promotes to box 1", boxes.indexOf(1) !== -1, boxes.join(","));
    qa.check("both ratings recorded", boxes.length === 2, boxes.length + " records");
    """,

    "swipe": r"""
    var stage = root.querySelector(".fc-stage");
    var pos = qa.num(root, "pos");
    qa.touch(stage, "touchstart", 300);
    qa.touch(stage, "touchend", 200);
    qa.check("swipe left advances", qa.num(root, "pos") === pos + 1,
      pos + " -> " + qa.num(root, "pos"));
    qa.touch(stage, "touchstart", 200);
    qa.touch(stage, "touchend", 300);
    qa.check("swipe right goes back", qa.num(root, "pos") === pos);
    qa.touch(stage, "touchstart", 300);
    qa.touch(stage, "touchend", 280);
    qa.check("a short drag is not a swipe", qa.num(root, "pos") === pos);
    """,

    "shuffle": r"""
    var len = qa.num(root, "total");
    var firstNotes = root.querySelector(".fc-meta a").getAttribute("href");
    qa.press("ArrowRight");
    qa.press("ArrowRight");
    qa.tool(root, "Shuffle").click();
    qa.check("shuffle keeps every card", qa.num(root, "total") === len,
      len + " -> " + qa.num(root, "total"));
    qa.check("shuffle returns to card 1", qa.num(root, "pos") === 1,
      "at " + qa.num(root, "pos"));
    """,

    "summary": r"""
    var guard = 0;
    while (root.querySelector(".fc-summary").hidden && guard++ < 500) {
      qa.press("ArrowRight");
    }
    var summary = root.querySelector(".fc-summary");
    qa.check("session summary shows at the end of the queue",
      summary.hidden === false, "after " + guard + " steps");
    qa.check("summary reports a percentage", /%/.test(summary.textContent));
    qa.check("summary reports the Leitner boxes",
      /still learning/.test(summary.textContent) &&
      /mastered/.test(summary.textContent));
    qa.check("summary offers 'Study again'",
      !!qa.tool(summary, "Study again"));
    qa.tool(summary, "Study again").click();
    qa.check("'Study again' restarts the deck",
      summary.hidden === true && qa.num(root, "pos") === 1);
    """,

    "print": r"""
    qa.tool(root, "Print this deck").click();
    var sheet = root.querySelector("[data-fc-printsheet]");
    qa.check("print sheet filled with every card",
      sheet.querySelectorAll(".fc-print-item").length === window.__deckSize,
      sheet.querySelectorAll(".fc-print-item").length + " of " + window.__deckSize);
    qa.check("print sheet is unhidden", sheet.hidden === false);
    qa.check("printing class applied", root.classList.contains("is-printing"));
    qa.check("print sheet carries the new bullet lists",
      sheet.querySelectorAll(".fc-print-back ul li").length > 0,
      sheet.querySelectorAll(".fc-print-back ul li").length + " <li>");
    qa.check("print sheet carries multi-paragraph backs",
      sheet.querySelectorAll(".fc-print-back p").length >
      sheet.querySelectorAll(".fc-print-item").length,
      sheet.querySelectorAll(".fc-print-back p").length + " <p> over " +
      sheet.querySelectorAll(".fc-print-item").length + " cards");
    var imgs = sheet.querySelectorAll(".fc-print-back img.fc-diagram");
    var okSrc = imgs.length > 0;
    Array.prototype.forEach.call(imgs, function (im) {
      if (!/^\/images\/diagrams\/svg\/.+\.svg$/.test(im.getAttribute("src")))
        okSrc = false;
      if (!im.getAttribute("alt")) okSrc = false;
    });
    qa.check("diagram cards reference SVGs with alt text", okSrc,
      imgs.length + " diagrams");
    """,

    "ga4-events": r"""
    /* gtag never loads in headless, and track() no-ops without it, so stub it
     * and record what the player would have sent. */
    var sent = [];
    window.gtag = function (kind, name, params) { sent.push([name, params]); };
    var card = root.querySelector(".fc-card");
    card.click();
    root.querySelector(".fc-got").click();
    card.click();
    root.querySelector(".fc-again").click();
    qa.tool(root, "Print this deck").click();
    var names = sent.map(function (e) { return e[0]; });
    qa.check("card_flip fires", names.indexOf("card_flip") !== -1, names.join(","));
    qa.check("card_rated fires", names.indexOf("card_rated") !== -1);
    qa.check("deck_print fires", names.indexOf("deck_print") !== -1);
    var flip = sent.filter(function (e) { return e[0] === "card_flip"; })[0][1];
    qa.check("card_flip carries board/theme/deck_id/card_id/card_type",
      !!(flip.board && flip.theme && flip.deck_id && flip.card_id && flip.card_type),
      JSON.stringify(flip));
    var rated = sent.filter(function (e) { return e[0] === "card_rated"; });
    qa.check("card_rated carries the rating and the new box",
      rated.length === 2 && rated[0][1].rating === "got_it" &&
      rated[1][1].rating === "again" && rated[1][1].box === 1,
      JSON.stringify(rated.map(function (r) { return r[1].rating + "/" + r[1].box; })));
    /* deck_start fires at init, before the stub existed - prove it is wired by
     * restarting, which calls the same tracked path. */
    sent.length = 0;
    qa.tool(root, "Restart").click();
    qa.check("deck_start fires on restart, with cards_due",
      sent.length > 0 && sent[0][0] === "deck_start" &&
      typeof sent[0][1].cards_due === "number", JSON.stringify(sent[0]));
    var guard = 0;
    while (root.querySelector(".fc-summary").hidden && guard++ < 500) {
      qa.press("ArrowRight");
    }
    var complete = sent.filter(function (e) { return e[0] === "deck_complete"; });
    qa.check("deck_complete fires with cards_seen and pct_got_it",
      complete.length > 0 && "cards_seen" in complete[0][1] &&
      "pct_got_it" in complete[0][1], JSON.stringify(complete[0] || null));
    """,

    "reduced-motion": r"""
    var card = root.querySelector(".fc-card");
    var inner = root.querySelector(".fc-card-inner");
    var back = root.querySelector(".fc-back");
    var front = root.querySelector(".fc-front");
    qa.check("prefers-reduced-motion is being emulated",
      window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    var s = getComputedStyle(inner);
    qa.check("flip transition disabled",
      s.transitionDuration === "0s" || s.transitionProperty === "none",
      s.transitionProperty + " " + s.transitionDuration);
    qa.check("3D flattened", s.transformStyle === "flat", s.transformStyle);
    qa.check("answer hidden by opacity before the flip",
      getComputedStyle(back).opacity === "0");
    card.click();
    qa.check("answer crossfades in on flip",
      getComputedStyle(back).opacity === "1" &&
      getComputedStyle(front).opacity === "0");
    qa.check("card is not rotated under reduced motion",
      getComputedStyle(inner).transform === "none",
      getComputedStyle(inner).transform);
    /* The grid-cell height fix must still apply, or answers clip. */
    qa.check("faces still share one grid cell (no fixed-height scroll)",
      back.scrollHeight <= back.clientHeight + 1,
      back.scrollHeight + " vs " + back.clientHeight);
    """,

    "storage-reset": r"""
    var card = root.querySelector(".fc-card");
    card.click();
    root.querySelector(".fc-got").click();
    var index = JSON.parse(window.localStorage.getItem("ea-flashcards:v2:index"));
    qa.check("key index records the deck", Array.isArray(index) &&
      index.indexOf("ea-flashcards:v2:deck:edexcel-a-theme-2") !== -1,
      JSON.stringify(index));
    index.forEach(function (k) { window.localStorage.removeItem(k); });
    window.localStorage.removeItem("ea-flashcards:v2:index");
    qa.check("a global reset clears every flashcard key",
      Object.keys(window.localStorage).filter(function (k) {
        return k.indexOf("ea-flashcards") === 0;
      }).length === 0);
    """,
}

RUNNER = """
<script>
(function () {
  var qa = window.__qa;
  var tries = 0;
  function go() {
    var root = document.querySelector("[data-flashcards]");
    if (!root || !root.querySelector(".fc-front") ||
        !root.querySelector(".fc-progress-label").textContent) {
      if (tries++ < 400) return setTimeout(go, 25);
      return;
    }
    fetch(root.getAttribute("data-src")).then(function (r) {
      return r.json();
    }).then(function (d) {
      window.__deckSize = d.cards.length;
      try {
        __BODY__
      } catch (e) {
        qa.check("group crashed", false, String(e));
      }
      qa.done();
    });
  }
  go();
})();
</script>
"""


def run_group(name, body, reduced_motion=False):
    src = ROOT / DECK_PAGE
    page = HERE / f"functional-{name}.html"
    html = src.read_text(encoding="utf-8")
    script = PRELUDE + RUNNER.replace("__BODY__", body)
    page.write_text(html.replace("</body>", script + "</body>"),
                    encoding="utf-8")

    query = urllib.parse.urlencode(
        {"w": 1280, "h": 900, "src": f"/_working/flashcards/qa/{page.name}"})
    args = [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
            "--window-size=1400,1000", "--virtual-time-budget=25000"]
    if reduced_motion:
        args.append("--force-prefers-reduced-motion")
    args += ["--dump-dom", f"{BASE}{FRAME}?{query}"]
    proc = subprocess.run(args, check=True, capture_output=True, text=True)
    match = re.search(r'<pre id="qa-measure">(.*?)</pre>', proc.stdout, re.S)
    if not match:
        return [{"name": f"{name}: no results returned", "pass": False,
                 "detail": ""}]
    return json.loads(htmlmod.unescape(match.group(1)))


def main():
    failed, total = 0, 0
    for name, body in GROUPS.items():
        print(f"\n{name}")
        for row in run_group(name, body, reduced_motion=(name == "reduced-motion")):
            total += 1
            if not row["pass"]:
                failed += 1
            detail = f"   [{row['detail']}]" if row["detail"] else ""
            print(f"  {'PASS' if row['pass'] else 'FAIL'}  "
                  f"{row['name']}{detail}")
    print(f"\n{total - failed}/{total} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
