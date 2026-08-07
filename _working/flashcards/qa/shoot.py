#!/usr/bin/env python3
"""Screenshot real flashcard faces, in the real page, at real widths.

QA tool for the flashcards content pass. Not published (_working/ is
Jekyll-excluded). Serve the repo root first:

    python3 -m http.server 8899

Then:

    python3 _working/flashcards/qa/shoot.py edexcel-a-1-4-1-eval-01 --side back
    python3 _working/flashcards/qa/shoot.py --deck edexcel-a-theme-1 --long 6

Output lands in _working/flashcards/qa/shots/<tag>/.

Two things make this faithful, and both were arrived at the hard way:

1. The page under test is the REAL built deck page, with a driver script
   appended. The driver waits for js/components/flashcards.js to build the
   player, then writes one chosen card into the real .fc-front/.fc-back nodes
   using the same faceHTML rules the player uses, flips it if asked, and hides
   the chrome above the stage. So the CSS, the DOM and the card HTML are the
   shipped ones.

2. The page is loaded inside an IFRAME of the target width. Chrome's
   --window-size does NOT control the layout viewport for a page carrying a
   viewport meta tag on this machine (390 came out as 485, and 741 with
   --force-device-scale-factor) - so media queries fired at the wrong width and
   mobile screenshots were silently cropped desktop renders. An iframe's
   viewport is exactly its CSS width, so `--hide-scrollbars` plus a sized
   iframe gives a true 390px mobile viewport. Verified: frame reports 390.
"""

import argparse
import json
import pathlib
import re
import subprocess
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
SHOTS = HERE / "shots"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE = "http://localhost:8899"
FRAME = "/_working/flashcards/qa/frame.html"

# label -> (css width, css height)
WIDTHS = {"mobile": (390, 1000), "desktop": (1280, 900)}

DECK_PAGES = {
    "edexcel-a-theme-1": "flashcards/edexcel-a/theme-1/index.html",
    "edexcel-a-theme-2": "flashcards/edexcel-a/theme-2/index.html",
    "edexcel-a-theme-3": "flashcards/edexcel-a/theme-3/index.html",
    "edexcel-a-theme-4": "flashcards/edexcel-a/theme-4/index.html",
    "aqa-micro": "flashcards/aqa/micro/index.html",
    "aqa-macro": "flashcards/aqa/macro/index.html",
}

DRIVER = """
<script>
/* QA driver - not part of the site. */
(function () {
  var params = new URLSearchParams(window.location.search);
  var wanted = params.get("card");
  var side = params.get("side") || "front";
  var bare = params.get("bare") !== "0";
  if (!wanted) return;

  function faceHTML(item, which) {
    var label = '<span class="fc-face-label">' +
      (which === "front" ? "Question" : "Answer") + "</span>";
    if (which === "front") return label + item.front;
    var extras = "";
    if (item.formulaHtml) {
      extras += '<span class="fc-formula">' + item.formulaHtml + "</span>";
    }
    if (item.svgRef) {
      extras += '<img class="fc-diagram" src="' + item.svgRef + '" alt="' +
        item.svgAlt.replace(/"/g, "&quot;") + '" width="800" height="600" />';
    }
    return label + extras + item.back;
  }

  function paint(data) {
    var item = null;
    for (var i = 0; i < data.cards.length; i++) {
      if (data.cards[i].id === wanted) { item = data.cards[i]; break; }
    }
    var root = document.querySelector("[data-flashcards]");
    var front = root.querySelector(".fc-front");
    var back = root.querySelector(".fc-back");
    var card = root.querySelector(".fc-card");
    if (!item || !front) {
      document.body.setAttribute("data-qa-miss", "1");
      document.title = "QA MISS " + wanted;
      return;
    }
    front.innerHTML = faceHTML(item, "front");
    back.innerHTML = faceHTML(item, "back");
    if (side === "back") {
      card.classList.add("is-flipped");
      front.setAttribute("aria-hidden", "true");
      back.setAttribute("aria-hidden", "false");
    }
    if (bare) {
      /* Hide the chrome above the stage so the card sits at the top of the
       * screenshot. The card keeps its real column width. */
      var hide = ["#header-placeholder", "#footer-placeholder", ".fc-intro",
                  ".fc-toolbar", ".fc-progress", ".fc-topics", ".fc-samples",
                  ".fc-about", ".fc-hero", ".fc-deck-meta", ".fc-cta",
                  ".breadcrumbs", ".fc-print-note", "h1"];
      hide.forEach(function (sel) {
        Array.prototype.forEach.call(
          document.querySelectorAll(sel), function (n) {
            n.style.display = "none";
          });
      });
    }
    /* Report the scroll overflow of the visible face, so the shooter can
     * flag cards whose answer does not fit without scrolling. */
    var face = side === "back" ? back : front;
    document.title = "QA " + wanted + " scrollH=" + face.scrollHeight +
      " clientH=" + face.clientHeight;
    document.body.setAttribute("data-qa-ready", "1");
  }

  var tries = 0;
  function go() {
    var root = document.querySelector("[data-flashcards]");
    if (!root || !root.querySelector(".fc-front")) {
      if (tries++ < 200) return setTimeout(go, 25);
      return;
    }
    fetch(root.getAttribute("data-src")).then(function (r) {
      return r.json();
    }).then(paint);
  }
  go();
})();
</script>
"""


def harness(deck):
    src = ROOT / DECK_PAGES[deck]
    out = HERE / (deck + ".html")
    html = src.read_text(encoding="utf-8")
    out.write_text(html.replace("</body>", DRIVER + "</body>"),
                   encoding="utf-8")


def build_index():
    index, cards = {}, {}
    for deck in DECK_PAGES:
        path = ROOT / "flashcards" / "data" / f"{deck}.json"
        for card in json.loads(path.read_text(encoding="utf-8"))["cards"]:
            index[card["id"]] = deck
            cards[card["id"]] = card
    return index, cards


def frame_url(page_url, width, height):
    query = urllib.parse.urlencode({"w": width, "h": height, "src": page_url})
    return f"{BASE}{FRAME}?{query}"


def shoot(url, path, width, height):
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
         f"--window-size={width + 40},{height + 40}",
         "--virtual-time-budget=8000",
         f"--screenshot={path}", url],
        check=True, capture_output=True,
    )
    # The frame sits at the top-left; crop the slack off.
    subprocess.run(["sips", "-c", str(height), str(width), str(path)],
                   check=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cards", nargs="*")
    ap.add_argument("--deck")
    ap.add_argument("--long", type=int, default=0,
                    help="also shoot the N longest backs in --deck")
    ap.add_argument("--side", default="both",
                    choices=["front", "back", "both"])
    ap.add_argument("--width", default="both",
                    choices=["mobile", "desktop", "both"])
    ap.add_argument("--tag", default="latest")
    args = ap.parse_args()

    index, cards = build_index()
    todo = list(args.cards)
    if args.long:
        pool = [c for cid, c in cards.items() if index[cid] == args.deck]
        pool.sort(key=lambda c: len(re.sub("<[^>]+>", "", c["back"])),
                  reverse=True)
        todo += [c["id"] for c in pool[:args.long]]

    sides = ["front", "back"] if args.side == "both" else [args.side]
    widths = (list(WIDTHS) if args.width == "both" else [args.width])
    made, seen = [], set()
    for cid in todo:
        if cid not in index:
            print(f"  ! unknown card {cid}")
            continue
        deck = index[cid]
        if deck not in seen:
            harness(deck)
            seen.add(deck)
        page = f"/_working/flashcards/qa/{deck}.html?card={cid}"
        for side in sides:
            for label in widths:
                w, h = WIDTHS[label]
                out = SHOTS / args.tag / f"{cid}-{side}-{label}.png"
                shoot(frame_url(f"{page}&side={side}", w, h), out, w, h)
                made.append(out)
    for path in made:
        print(path.relative_to(ROOT))
    if not made:
        sys.exit("nothing shot")


if __name__ == "__main__":
    main()
