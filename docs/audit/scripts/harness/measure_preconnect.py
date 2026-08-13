#!/usr/bin/env python3
"""Does moving the font preconnect earlier in <head> buy anything measurable?

    python3 docs/audit/scripts/harness/measure_preconnect.py
    python3 docs/audit/scripts/harness/measure_preconnect.py --browser --runs 9

THE ANSWER IS NO, AND THE EVIDENCE IS THE STATIC HALF, NOT THE BROWSER HALF.
---------------------------------------------------------------------------
Measured 2026-08-13 over all 463 published pages: **every one of them carries
its preconnect inside the first 1,184 bytes of the GZIPPED response**, early
lineage or late. TCP's initial congestion window is ten segments, about
14,600 bytes, so on 439 of 463 pages the entire document - head and body -
arrives in the first round trip, and on the other 24 the overflow is body.

Both preconnect positions are therefore in the same burst of bytes. The
preload scanner meets them in the same pass. Moving the hint ~4,000 bytes
earlier in a document that is delivered whole cannot change when the
connection starts, and the ~600 bytes it would save are not a boundary
anything crosses.

**THE BROWSER PROBE BELOW FAILED AND ITS NUMBERS MUST NOT BE CITED.** It was
run in three configurations - unthrottled, and with the document throttled to
20,000 and 4,000 B/s - and in all three it could not distinguish `none` from
`early`: no preconnect at all measured the same as having one, and on one
configuration measured FASTER. By the rule stated below, that means the
instrument measured nothing, so it cannot support a claim about early versus
late either. It is kept because it records what does not work, and because
the next person will otherwise spend the same hour on it.

WHY THIS EXISTS
---------------
DO-NOT-BREAK.md, "The build step": the site carries TWO preconnect lineages.
273 pages put the Google Fonts preconnect pair BEFORE `<title>`; 190 put it
after the favicons, ~4,000 bytes later. The register says earlier is better
for the preload scanner, calls the early families right and the late ones the
laggards, and then forbids acting on that: **do not align them without
measuring LCP.**

This is that measurement. It exists so the item can be decided on evidence
rather than on the plausible-sounding sentence, in either direction.

WHAT IT MEASURES, AND WHY NOT LCP ALONE
---------------------------------------
LCP is what the register names, and it is included - but it is downstream of
the thing being changed and noisy enough to hide it. What a preconnect
actually does is start the TCP+TLS handshake to an origin sooner, so the
direct measurement is **when the connection to fonts.googleapis.com begins**,
from PerformanceResourceTiming. If moving the hint earlier does anything at
all, it does it there first, and by more than it ever could to LCP.

THREE VARIANTS OF ONE PAGE, WHICH IS THE WHOLE DESIGN
-----------------------------------------------------
    early    the preconnect pair before <title>      (the 273-page lineage)
    late     the preconnect pair after the favicons  (the 190-page lineage)
    none     no preconnect at all

`none` is not a curiosity, it is what makes the other two readable. A probe
reporting "early and late are the same" is worthless until the same probe is
shown to report a difference when there genuinely is one - PROGRESS.md
records a CLS probe that returned 0.0000 for a deliberate 200px shift, and
4.11's rule that a zero is believed only after the same instrument has been
made to return non-zero. If `none` is indistinguishable from `early` too,
this probe measured nothing and its output must be discarded.

FOUR THINGS THE HARNESS ALREADY LEARNED THE HARD WAY, ALL OBEYED HERE
----------------------------------------------------------------------
  * NO --virtual-time-budget. Chrome's clock does not advance under it, so
    no paint timing is ever generated. That is exactly how the CLS probe came
    back 0.0000. This runs in real time and waits.
  * A single-threaded http.server DEADLOCKS against Chrome's parallel
    connections. ThreadingHTTPServer.
  * subprocess.run() cannot drive Chrome - it does not exit, because its
    updater and crash-handler children inherit the stdout pipe. Poll for the
    result, then kill the process GROUP, swallowing PermissionError as well
    as ProcessLookupError.
  * The result comes back by POST, because --dump-dom is a snapshot and the
    numbers arrive after it.

Standard library only. Needs Google Chrome and real network access to
fonts.googleapis.com - it is a one-off measurement, not a CI step.
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import pathlib
import re
import shutil
import signal
import socketserver
import statistics
import subprocess
import sys
import tempfile
import threading
import time

HARNESS = pathlib.Path(__file__).resolve().parent
REPO = HARNESS.parents[3]

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# A page from the LATE lineage, so `early` is produced by moving its pair up
# rather than by comparing two different pages. Comparing about.html against a
# ppq page would measure the pages, not the lineage.
SOURCE = "about.html"

PRECONNECT = (
    '    <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
)

PROBE = """
<script>
(function () {
  var lcp = 0;
  try {
    new PerformanceObserver(function (l) {
      var e = l.getEntries();
      lcp = e[e.length - 1].startTime;
    }).observe({ type: "largest-contentful-paint", buffered: true });
  } catch (e) {}
  function send() {
    var out = { variant: VARIANT, lcp: lcp, fonts: {} };
    performance.getEntriesByType("resource").forEach(function (r) {
      var host = null;
      if (r.name.indexOf("fonts.googleapis.com") >= 0) host = "googleapis";
      else if (r.name.indexOf("fonts.gstatic.com") >= 0) host = "gstatic";
      if (!host || out.fonts[host]) return;
      out.fonts[host] = {
        // startTime is when the browser DECIDED to fetch; connectStart is
        // when the socket work began. A preconnect moves both earlier.
        startTime: r.startTime,
        connectStart: r.connectStart,
        connectEnd: r.connectEnd,
        responseEnd: r.responseEnd
      };
    });
    var nav = performance.getEntriesByType("navigation")[0];
    out.domInteractive = nav ? nav.domInteractive : null;
    fetch("/__result", { method: "POST", body: JSON.stringify(out) });
  }
  // Late enough that the font requests have finished, and in real time -
  // there is no virtual clock to fast-forward here, by design.
  addEventListener("load", function () { setTimeout(send, 2500); });
})();
</script>
"""


class Threaded(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def serve(root: pathlib.Path, sink: list, throttle: int = 0) -> tuple[Threaded, int]:
    """throttle: bytes per second for the DOCUMENT, 0 for unthrottled.

    WITHOUT THIS THE PROBE CANNOT SEE THE EFFECT AT ALL, and that is the
    finding rather than a workaround. Over localhost the whole page arrives
    in one read, so the preload scanner meets the hint at byte 513 and the
    hint at byte 5,105 in the same instant - the first run of this script
    returned `none` FASTER than `early`, which is backwards, because it was
    measuring nothing but noise.

    Throttling the document makes those 4,600 bytes take real time, which is
    the only condition under which the position of the hint can matter. It is
    a deliberately UNREALISTIC condition - see the summary this prints - and
    it exists to prove the instrument can separate the variants, so that a
    null result at realistic speed means something.
    """
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(root), **k)

        def copyfile(self, source, outputfile):
            if not throttle or not self.path.endswith(".html"):
                return super().copyfile(source, outputfile)
            chunk = max(256, throttle // 50)
            while True:
                block = source.read(chunk)
                if not block:
                    break
                outputfile.write(block)
                outputfile.flush()
                time.sleep(len(block) / throttle)

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            try:
                sink.append(json.loads(self.rfile.read(n)))
            except ValueError:
                pass
            self.send_response(204)
            self.end_headers()

        def log_message(self, *a):
            pass

    srv = Threaded(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def variants(tmp: pathlib.Path) -> None:
    """Three copies of one page, differing only in where the pair sits."""
    src = (REPO / SOURCE).read_text(encoding="utf-8")
    assert src.count(PRECONNECT) == 1, "the preconnect pair is not verbatim in " + SOURCE
    stripped = src.replace(PRECONNECT, "")

    title = stripped.find("    <title")
    assert title > 0
    early = stripped[:title] + PRECONNECT + stripped[title:]

    for name, body in (("early", early), ("late", src), ("none", stripped)):
        out = body.replace("</body>", PROBE.replace("VARIANT", f'"{name}"') + "</body>")
        (tmp / f"{name}.html").write_text(out, encoding="utf-8")

    # every asset the page asks for, served from the real tree
    for d in ("css", "js", "images", "webfonts"):
        if (REPO / d).exists():
            (tmp / d).symlink_to(REPO / d)
    for f in ("favicon.ico", "apple-touch-icon.png", "site.webmanifest"):
        if (REPO / f).exists():
            (tmp / f).symlink_to(REPO / f)


def load(port: int, name: str, sink: list, timeout: float = 25.0) -> dict | None:
    profile = tempfile.mkdtemp(prefix="preconnect-")
    before = len(sink)
    p = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
         "--no-default-browser-check", "--disable-extensions",
         f"--user-data-dir={profile}",
         # NO --virtual-time-budget. See the module docstring.
         f"http://127.0.0.1:{port}/{name}.html"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    got = None
    deadline = time.time() + timeout
    while time.time() < deadline:
        if len(sink) > before:
            got = sink[-1]
            break
        time.sleep(0.15)
    for kill in (lambda: os.killpg(os.getpgid(p.pid), signal.SIGKILL), p.kill):
        try:
            kill()
        except (ProcessLookupError, PermissionError, OSError):
            pass
    p.wait(timeout=5)
    shutil.rmtree(profile, ignore_errors=True)
    return got


def static_analysis() -> None:
    """Where the preconnect sits in the COMPRESSED stream, on every page.

    This is the measurement that settles the question, and it needs no
    browser. What a preconnect can save is bounded by how much later the
    browser learns about it, and the browser learns about the whole first
    burst at once.
    """
    import gzip
    sys.path.insert(0, str(REPO / "scripts"))
    import build_sitemap
    ex = build_sitemap.excludes()
    files = [f for f in subprocess.run(
        ["git", "ls-files", "*.html"], cwd=REPO,
        capture_output=True, text=True).stdout.split()
        if build_sitemap.published(f, ex)
        and f not in ("templates/header.html", "templates/footer.html")]

    IW = 14600  # RFC 6928 initial window, 10 segments
    fits = late = 0
    worst = 0
    for f in files:
        raw = (REPO / f).read_bytes()
        if len(gzip.compress(raw, 6)) <= IW:
            fits += 1
        text = raw.decode("utf-8", "replace")
        pre = text.find('rel="preconnect"')
        if pre > text.find("<title"):
            late += 1
        worst = max(worst, len(gzip.compress(raw[:pre], 6)))

    print(f"{len(files)} published pages, {late} on the late lineage\n")
    print(f"  documents fitting entirely in the ~{IW:,} B initial congestion "
          f"window: {fits}")
    print(f"  the LATEST any preconnect sits, in compressed bytes:  {worst:,} B")
    print(f"\n  Both lineages put the hint inside the first burst on every "
          f"page, so the\n  preload scanner meets it at the same instant "
          f"either way. There is no\n  round trip between the two positions "
          f"to save.\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--browser", action="store_true",
                    help="also run the Chrome probe. IT DOES NOT WORK - see "
                         "the module docstring - and is kept as a record")
    ap.add_argument("--runs", type=int, default=9,
                    help="loads per variant (default 9)")
    ap.add_argument("--throttle", type=int, default=0, metavar="BYTES_PER_SEC",
                    help="throttle the HTML document. 0 (default) is "
                         "realistic delivery and is expected to show no "
                         "difference; a low value proves the probe can see "
                         "one when the bytes genuinely arrive apart")
    args = ap.parse_args()

    static_analysis()
    if not args.browser:
        return 0

    print("--browser: running the probe that FAILED its own sensitivity "
          "check. Read the\ndocstring before believing any number below.\n")
    if not pathlib.Path(CHROME).exists():
        print(f"Chrome not found at {CHROME}", file=sys.stderr)
        return 2

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="preconnect-tree-"))
    sink: list = []
    try:
        variants(tmp)
        srv, port = serve(tmp, sink, args.throttle)
        print(f"serving {tmp} on :{port}"
              + (f", document throttled to {args.throttle} B/s" if args.throttle else ", unthrottled") + "\n")

        results: dict[str, list[dict]] = {"early": [], "late": [], "none": []}
        # interleaved, not blocked: three runs of `early` back to back would
        # share a warm DNS cache the other variants did not have
        for i in range(args.runs):
            for name in ("early", "late", "none"):
                got = load(port, name, sink)
                if got:
                    results[name].append(got)
                print(f"  run {i + 1} {name:6} "
                      f"{'ok' if got else 'NO RESULT'}", flush=True)
        srv.shutdown()

        print(f"\n{'variant':8} {'n':>3}  "
              f"{'googleapis connectStart':>24}  {'gstatic connectStart':>21}  "
              f"{'LCP':>9}")
        summary = {}
        for name in ("early", "late", "none"):
            rows = results[name]
            if not rows:
                print(f"{name:8}   0  no results")
                continue
            def med(f):
                vals = [f(r) for r in rows if f(r) is not None]
                return statistics.median(vals) if vals else None
            ga = med(lambda r: r["fonts"].get("googleapis", {}).get("connectStart"))
            gs = med(lambda r: r["fonts"].get("gstatic", {}).get("connectStart"))
            lcp = med(lambda r: r.get("lcp") or None)
            summary[name] = (ga, gs, lcp)
            fmt = lambda v: f"{v:.1f} ms" if v is not None else "n/a"
            print(f"{name:8} {len(rows):3}  {fmt(ga):>24}  {fmt(gs):>21}  {fmt(lcp):>9}")

        print("\nREADING THIS")
        if "early" in summary and "late" in summary and "none" in summary:
            e, l, n = summary["early"][0], summary["late"][0], summary["none"][0]
            if None not in (e, l, n):
                print(f"  early vs late : {abs(e - l):7.1f} ms  <- the change being decided")
                print(f"  early vs none : {abs(e - n):7.1f} ms  <- the probe's own sensitivity")
                if abs(e - n) < 1.0:
                    print("  THE PROBE MEASURED NOTHING. `none` should differ from "
                          "`early`;\n  it does not, so no conclusion about early "
                          "vs late may be drawn.")
                elif abs(e - l) < abs(e - n) / 4:
                    print("  The lineages are indistinguishable, on an instrument "
                          "that DOES\n  separate having the hint from not having "
                          "it. That is a real null.")
        json.dump(results, open(tmp / "raw.json", "w"), indent=1)
        print(f"\nraw: {tmp}/raw.json")
        return 0
    finally:
        pass


if __name__ == "__main__":
    raise SystemExit(main())
