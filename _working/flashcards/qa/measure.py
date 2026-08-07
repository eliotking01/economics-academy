#!/usr/bin/env python3
"""Measure, for every card, whether its face content fits without scrolling.

One real page load per deck per width: the driver walks every card in the
deck, writes it into the real .fc-front/.fc-back nodes and records
scrollHeight against clientHeight. Faithful because it is the shipped CSS and
the shipped faceHTML.

    python3 -m http.server 8899
    python3 _working/flashcards/qa/measure.py --tag before

Writes _working/flashcards/qa/measure-<tag>.json and prints a summary.
"""

import argparse
import json
import pathlib
import re
import subprocess
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE = "http://localhost:8899"
FRAME = "/_working/flashcards/qa/frame.html"
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
(function () {
  function faceHTML(item, which) {
    var label = '<span class="fc-face-label">' +
      (which === "front" ? "Question" : "Answer") + "</span>";
    if (which === "front") return label + item.front;
    var extras = "";
    if (item.formulaHtml) {
      extras += '<span class="fc-formula">' + item.formulaHtml + "</span>";
    }
    if (item.svgRef) {
      extras += '<img class="fc-diagram" src="' + item.svgRef + '" alt="" ' +
        'width="800" height="600" />';
    }
    return label + extras + item.back;
  }

  function run(data) {
    var root = document.querySelector("[data-flashcards]");
    var front = root.querySelector(".fc-front");
    var back = root.querySelector(".fc-back");
    var rows = [];
    data.cards.forEach(function (item) {
      front.innerHTML = faceHTML(item, "front");
      back.innerHTML = faceHTML(item, "back");
      rows.push({
        id: item.id,
        type: item.cardType,
        frontScroll: front.scrollHeight,
        frontClient: front.clientHeight,
        backScroll: back.scrollHeight,
        backClient: back.clientHeight
      });
    });
    window.parent.postMessage(
      { qa: "measure", rows: JSON.stringify(rows) }, "*");
  }

  var tries = 0;
  function go() {
    var root = document.querySelector("[data-flashcards]");
    if (!root || !root.querySelector(".fc-front")) {
      if (tries++ < 400) return setTimeout(go, 25);
      return;
    }
    fetch(root.getAttribute("data-src")).then(function (r) {
      return r.json();
    }).then(run);
  }
  go();
})();
</script>
"""


def harness(deck):
    src = ROOT / DECK_PAGES[deck]
    out = HERE / (deck + "-measure.html")
    html = src.read_text(encoding="utf-8")
    out.write_text(html.replace("</body>", DRIVER + "</body>"),
                   encoding="utf-8")
    return f"/_working/flashcards/qa/{deck}-measure.html"


def dump(url):
    proc = subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
         "--window-size=1400,1200", "--virtual-time-budget=20000",
         "--dump-dom", url],
        check=True, capture_output=True, text=True,
    )
    match = re.search(r'<pre id="qa-measure">(.*?)</pre>', proc.stdout,
                      re.S)
    if not match:
        return []
    import html as htmlmod
    return json.loads(htmlmod.unescape(match.group(1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="latest")
    args = ap.parse_args()

    result = {}
    for deck in DECK_PAGES:
        page = harness(deck)
        for label, (w, h) in WIDTHS.items():
            query = urllib.parse.urlencode({"w": w, "h": h, "src": page})
            rows = dump(f"{BASE}{FRAME}?{query}")
            for row in rows:
                entry = result.setdefault(row["id"], {"deck": deck,
                                                      "type": row["type"]})
                entry[label] = {
                    "front": [row["frontScroll"], row["frontClient"]],
                    "back": [row["backScroll"], row["backClient"]],
                }
            print(f"  {deck:22} {label:8} {len(rows):4} cards")

    out = HERE / f"measure-{args.tag}.json"
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")

    for label in WIDTHS:
        over = {"front": [], "back": []}
        for cid, entry in result.items():
            if label not in entry:
                continue
            for side in ("front", "back"):
                scroll, client = entry[label][side]
                if scroll > client + 1:
                    over[side].append((scroll - client, cid))
        print(f"\n{label}: {len(over['back'])} backs and "
              f"{len(over['front'])} fronts overflow "
              f"(of {len(result)} cards)")
        for side in ("front", "back"):
            worst = sorted(over[side], reverse=True)[:8]
            for excess, cid in worst:
                print(f"    {side:6} +{excess:4}px  {cid}")
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
