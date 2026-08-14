#!/usr/bin/env python3
"""Measure what a diagram image actually renders at, and what swapping it costs.

    python3 docs/audit/scripts/harness/measure_diagram_render.py

WHY THIS EXISTS RATHER THAN A STATIC CHECK

`verify_image_dimensions.py` compares a declared size against the file. It
cannot see what the browser DOES with that size, and the CSS that decides it is
one line three files away. Wave 5.3 was priced off a rendered-width comparison
that turned out to have read the wrong element, so this is the same
relationship `render_nav.py` and `computed_style_diff.py` have to the ten
assertions: the only thing that can see the answer is a real browser.

WHAT IT FOUND, 2026-08-14

PH08-047's closing section says a swapped SVG renders "798 px of white against
1,118 px for the two PNGs beside it" on `3-4-4-oligopoly.html`, and D46 and
PH08-047 step 3 are both written on top of that. **It does not reproduce.**
Measured at viewports 980, 1100, 1280, 1440, 1680 and 1920, the SVG and both
PNGs on that page render at **exactly 800 px each**, because
`css/pages/revision-notes-textbook.css:622` caps `.diagram-figure` at
`max-width: 800px`.

**The 1,118 is the `.notes-container`, not the PNG.** The ancestor chain reads
`img.diagram-image=800 -> figure.diagram-figure=800 -> section=1022 ->
div.notes-container=1120`. The figure that was compared to the SVG was the
image's great-grandparent.

So there is no 29% shrinkage and no width decision. PH08-047 step 3's
prescription - declare the viewBox - is correct, and is also the ONLY
declaration `verify_image_dimensions.py` accepts, because these SVGs carry no
absolute `width`/`height` and the checker falls back to the viewBox.

**The real cost is HEIGHT, in the opposite direction.** Swapping the two PNGs on
that page for their same-named SVGs at 800x600:

    collusion             500.8px -> 605.5px   +104.7
    kinked-demand-curve   512.8px -> 605.5px   + 92.7

Width is unchanged; every diagram gets taller, because every SVG viewBox is 4:3
and the PNGs are mostly near 1.5 - the aspect changes on 77 of 78 pairs (D46).
The widest PNGs grow hardest: `price-discrimination` at 3.372 aspect would go
from about 231 px tall to 583 px. There is no layout shift, since the
dimensions are declared; the pages simply get longer.

METHOD

Serve the repo from 127.0.0.1 (every asset path on this site is root-absolute,
so a path-prefixed origin sends the page to the wrong /css/main.css - that is
computed_style_diff.py's first recorded lesson). The target page is intercepted
and served with a probe script appended, which POSTs getBoundingClientRect for
every diagram image back to the server. Nothing in the repo is modified.

Chrome is driven per DO-NOT-BREAK: Popen in its own session, poll for the
result, kill the process GROUP swallowing PermissionError as well as
ProcessLookupError. No subprocess.run. No --virtual-time-budget: it freezes the
animation clock, and while that does not matter for a static rect read, the
register is explicit that measurements taken under it have been wrong before.
ThreadingHTTPServer, because a single-threaded one deadlocks against Chrome's
parallel connections.
"""

from __future__ import annotations

import http.server
import json
import os
import pathlib
import re
import signal
import socketserver
import shutil
import subprocess
import sys
import tempfile
import threading
import time

# HARNESS is the directory holding this file, so the repo root is parents[3]:
# docs/audit/scripts/harness -> scripts -> audit -> docs -> REPO. The guard
# below is what catches that being wrong, which is why it is here - the same
# mistake was made once in compare_trees.py's own relocation comment.
HARNESS = pathlib.Path(__file__).resolve().parent
REPO = HARNESS.parents[3]
if not (REPO / "css" / "pages" / "revision-notes-textbook.css").exists():
    raise SystemExit(f"cannot find the repo root from {HARNESS} — fix REPO")

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PROBE = """
<script>
(function(){
  function go(){
    var out = [];
    document.querySelectorAll('img').forEach(function(img){
      var s = img.getAttribute('src') || '';
      if (s.indexOf('/images/diagrams/') !== 0) return;
      var r = img.getBoundingClientRect();
      out.push({
        src: s,
        declaredW: img.getAttribute('width'),
        declaredH: img.getAttribute('height'),
        naturalW: img.naturalWidth,
        naturalH: img.naturalHeight,
        renderedW: Math.round(r.width * 10) / 10,
        renderedH: Math.round(r.height * 10) / 10,
        parentW: Math.round(img.parentElement.getBoundingClientRect().width * 10) / 10,
        chain: (function(){
          var a = [], e = img;
          while (e && e.tagName !== 'BODY') {
            a.push(e.tagName.toLowerCase() + '.' + (e.className || '').split(' ')[0]
                   + '=' + Math.round(e.getBoundingClientRect().width));
            e = e.parentElement;
          }
          return a;
        })()
      });
    });
    var body = JSON.stringify({viewport: window.innerWidth, images: out});
    var x = new XMLHttpRequest();
    x.open('POST', '/__result', true);
    x.setRequestHeader('Content-Type', 'application/json');
    x.send(body);
  }
  if (document.readyState === 'complete') { setTimeout(go, 400); }
  else { window.addEventListener('load', function(){ setTimeout(go, 400); }); }
})();
</script>
"""


def make_handler(target: str, swap: dict[str, str], sink: list):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(REPO), **kw)

        def log_message(self, *a):
            pass

        def do_POST(self):
            if self.path == "/__result":
                n = int(self.headers.get("Content-Length", 0))
                sink.append(json.loads(self.rfile.read(n)))
                self.send_response(204)
                self.end_headers()
            else:
                self.send_error(404)

        def do_GET(self):
            if self.path.split("?")[0] != target:
                return super().do_GET()
            html = (REPO / target.lstrip("/")).read_text(encoding="utf-8")
            for old, new in swap.items():
                html = html.replace(old, new)
            html = html.replace("</body>", PROBE + "</body>")
            data = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


def measure(target: str, width: int, swap: dict[str, str] | None = None) -> dict:
    sink: list = []
    httpd = socketserver.ThreadingTCPServer(
        ("127.0.0.1", 0), make_handler(target, swap or {}, sink))
    httpd.allow_reuse_address = True
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    profile = pathlib.Path(tempfile.mkdtemp(prefix="diagram-render-"))
    p = subprocess.Popen(
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
         f"--window-size={width},1400", "--force-device-scale-factor=1",
         f"--user-data-dir={profile}",
         "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1",
         f"--screenshot={profile}/shot.png",
         f"http://127.0.0.1:{port}{target}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

    deadline = time.time() + 30
    while time.time() < deadline and not sink:
        time.sleep(0.2)
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    httpd.shutdown()
    shutil.rmtree(profile, ignore_errors=True)
    if not sink:
        raise SystemExit(f"no result from {target} at {width}px — probe failed")
    return sink[0]


PAGE = "/revision-notes/edexcel-theme-3/3-4-4-oligopoly.html"


def report(label: str, result: dict) -> None:
    print(f"\n--- {label}  (viewport {result['viewport']}px)")
    for i in result["images"]:
        kind = "SVG" if i["src"].endswith(".svg") else "PNG"
        print(f"  {kind}  declared {i['declaredW']}x{i['declaredH']:<5}"
              f" natural {i['naturalW']}x{i['naturalH']:<5}"
              f" RENDERED {i['renderedW']:>7}px   (container {i['parentW']}px)"
              f"  {i['src'].split('/')[-1]}")


if __name__ == "__main__":
    # 1. THE WIDTH CLAIM. This page ships with game-theory as an SVG at 800x600
    #    beside two PNGs, which is the exact comparison PH08-047 reports. All
    #    three render the same width at every desktop viewport.
    for vw in (1920, 1680, 1440, 1280, 1100, 980):
        r = measure(PAGE, vw)
        widths = {i["src"].split("/")[-1]: i["renderedW"] for i in r["images"]}
        print(f"viewport {r['viewport']:>5}  " +
              "  ".join(f"{k}={v}" for k, v in widths.items()))

    # 2. WHERE 1,118 CAME FROM. The image's great-grandparent, not the image.
    print("\nancestor chain of the first diagram image at viewport 1440:")
    for step in measure(PAGE, 1440)["images"][0]["chain"]:
        print("   ", step)

    # 3. THE REAL COST. Swap both PNGs for their same-named SVGs, declared at
    #    the viewBox - the only declaration verify_image_dimensions.py accepts
    #    for an SVG with no absolute width. Nothing in the repo is modified;
    #    the substitution happens in the response body.
    swap = {}
    for stem, w, h in (("collusion", 2616, 1610), ("kinked-demand-curve", 2584, 1630)):
        swap[f'src="/images/diagrams/{stem}.png"'] = \
            f'src="/images/diagrams/svg/{stem}.svg"'
        swap[f'                  width="{w}"\n                  height="{h}"\n'] = \
            '                  width="800"\n                  height="600"\n'
    before, after = measure(PAGE, 1440), measure(PAGE, 1440, swap)
    print(f"\n{'file':<26}{'W before':>10}{'H before':>10}{'W after':>10}"
          f"{'H after':>10}{'dH':>9}")
    for b, a in zip(before["images"], after["images"]):
        print(f"{b['src'].split('/')[-1]:<26}{b['renderedW']:>10}{b['renderedH']:>10}"
              f"{a['renderedW']:>10}{a['renderedH']:>10}"
              f"{a['renderedH'] - b['renderedH']:>+9.1f}")
    print("\nWidth is unchanged and every diagram gets taller. That is the "
          "constraint on Wave 5.3,\nand it is not the one PH08-047 recorded.")
