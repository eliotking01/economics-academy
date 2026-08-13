#!/usr/bin/env python3
"""Prove a CSS change is cascade-neutral, by measuring it in a browser.

    python3 docs/audit/scripts/harness/computed_style_diff.py OLD NEW [PAGE...]
    python3 docs/audit/scripts/harness/computed_style_diff.py OLD NEW --all
    python3 docs/audit/scripts/harness/computed_style_diff.py OLD NEW --selftest

WHY THIS EXISTS
---------------
Wave-norm item (f) moves 322 authored inline `style=` attributes into CSS
classes. An inline style sits above every class selector in the cascade, so
the move is not a rename: a declaration that previously beat everything can
now lose to a rule nobody was thinking about. `compare_trees.py` cannot see
that at all - assertion 4 fires only on LOSSES, and an attribute becoming a
class is a loss of nothing plus a gain of a class, which it reports as an
addition. Assertions 2, 3, 6 and 7 never look at CSS.

DO-NOT-BREAK's standing rule for this is "CSS moves must be proved
cascade-neutral, not assumed". The previous wave proved it by parsing every
rule of two <style> blocks into (media, selector) -> declarations and checking
each was reproduced. That works when the rules move verbatim between
stylesheets. It does not work here, because the SPECIFICITY changes, which is
the entire risk. The only thing that settles a specificity question is the
cascade itself - so this asks the browser.

WHAT IT DOES
------------
Serves each tree from its OWN origin, loads OLD/<page> and NEW/<page> into two
iframes of the same size, waits for fonts, then walks both element trees in
document order and compares EVERY computed property on every element. Same
viewport means px values are comparable.

**ONE ORIGIN PER TREE IS NOT A DETAIL, IT IS THE WHOLE THING.** Every asset
path on this site is root-absolute - `/css/main.css`, `/js/main.js` - which is
DO-NOT-BREAK's own convention. Serving both trees under path prefixes on one
origin therefore sends BOTH iframes to the same `/css/main.css`, so the two
sides render with identical CSS and the probe reports 0 differences no matter
what changed. That is what the first version of this script did, and
`--selftest` is what found it: it appended a declaration to NEW's main.css and
this script could not see it. Two origins means cross-origin iframes, which is
why Chrome is launched with `--disable-web-security`.

A pass is: same element count, same tag at every index, and 0 differing
computed properties. That is a stronger statement than "it looks the same" -
it is "no element on this page resolves any property differently".

WHAT IT DELIBERATELY IGNORES, and why each is not a hole
--------------------------------------------------------
  * The `style` attribute itself, via `element.style`. Of course it differs -
    that is the change. Only the RESOLVED value is compared.
  * Nothing else. Every property getComputedStyle enumerates is compared,
    including the ones that cannot move, because an exclusion list is a place
    for a real difference to hide.

FOUR THINGS ABOUT DRIVING CHROME, all recorded in DO-NOT-BREAK and all still
true here
---------------------------------------------------------------------------
  * `subprocess.run()` cannot be used - Chrome's updater and crash-handler
    children inherit the stdout pipe and it never exits. Poll for the result
    file, then kill the process GROUP, swallowing PermissionError as well as
    ProcessLookupError.
  * A single-threaded http.server deadlocks against Chrome's parallel
    connections. ThreadingHTTPServer.
  * `--virtual-time-budget` freezes the animation clock, so a transition
    reports its FROM value forever. Transitions and animations are disabled in
    both frames before anything is read, and no virtual time is used: the page
    POSTs its own result back when it is done.
  * A probe that cannot fail has proved nothing. `--selftest` injects one
    declaration into NEW's main.css and requires this script to report a
    difference. Run it whenever the answer comes back 0. It has already earned
    its keep once, on the origin bug described above.
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
import subprocess
import sys
import tempfile
import threading
import time

HARNESS = pathlib.Path(__file__).resolve().parent
REPO = HARNESS.parents[3]
sys.path.insert(0, str(REPO / "scripts"))
import build_sitemap  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

DRIVER = """<!doctype html>
<meta charset="utf-8">
<title>computed style diff</title>
<style>
  html,body{margin:0}
  iframe{width:__W__px;height:__H__px;border:0;position:absolute;left:-99999px}
</style>
<body>
<script>
const PAGES = __PAGES__;
const OLD = __OLD_ORIGIN__, NEW = __NEW_ORIGIN__;
const results = [];

function frame(src) {
  return new Promise((resolve, reject) => {
    const f = document.createElement('iframe');
    f.src = src;
    f.onload = () => resolve(f);
    f.onerror = () => reject(new Error('failed to load ' + src));
    document.body.appendChild(f);
  });
}

// A transition mid-flight reports its FROM value, and virtual time never
// advances it. Kill both before reading anything.
function freeze(doc) {
  const s = doc.createElement('style');
  s.textContent = '*,*::before,*::after{transition:none!important;' +
                  'animation:none!important}';
  doc.head.appendChild(s);
}

async function ready(f) {
  const d = f.contentDocument;
  freeze(d);
  if (d.fonts && d.fonts.ready) { try { await d.fonts.ready; } catch (e) {} }
  // Two rAFs: style recalc, then layout.
  await new Promise(r => f.contentWindow.requestAnimationFrame(
    () => f.contentWindow.requestAnimationFrame(r)));
}

function describe(el) {
  let s = el.tagName.toLowerCase();
  if (el.id) s += '#' + el.id;
  if (el.className && typeof el.className === 'string' && el.className.trim())
    s += '.' + el.className.trim().split(/\\s+/).join('.');
  return s;
}

async function one(page) {
  const res = {page: page, diffs: [], elements: 0, props: 0, error: null};
  let a, b;
  try {
    a = await frame(OLD + '/' + page);
    b = await frame(NEW + '/' + page);
    await ready(a); await ready(b);
    if (!a.contentDocument || !b.contentDocument) {
      res.error = 'cross-origin frame not readable - is Chrome running with ' +
                  '--disable-web-security?';
      return res;
    }
    const ea = a.contentDocument.querySelectorAll('*');
    const eb = b.contentDocument.querySelectorAll('*');
    res.elements = ea.length;
    if (ea.length !== eb.length) {
      res.error = 'element count ' + ea.length + ' -> ' + eb.length;
      return res;
    }
    for (let i = 0; i < ea.length; i++) {
      if (ea[i].tagName !== eb[i].tagName) {
        res.diffs.push({at: i, prop: '<tagName>',
                        old: ea[i].tagName, new: eb[i].tagName,
                        where: describe(ea[i])});
        if (res.diffs.length > 200) return res;
        continue;
      }
      const ca = a.contentWindow.getComputedStyle(ea[i]);
      const cb = b.contentWindow.getComputedStyle(eb[i]);
      if (i === 0) res.props = ca.length;
      for (let k = 0; k < ca.length; k++) {
        const p = ca[k];
        const va = ca.getPropertyValue(p), vb = cb.getPropertyValue(p);
        if (va !== vb) {
          res.diffs.push({at: i, prop: p, old: va, new: vb,
                          where: describe(ea[i])});
          if (res.diffs.length > 200) return res;
        }
      }
    }
  } catch (e) {
    res.error = String(e && e.message || e);
  } finally {
    if (a) a.remove();
    if (b) b.remove();
  }
  return res;
}

(async () => {
  for (const p of PAGES) {
    try { results.push(await one(p)); }
    catch (e) { results.push({page: p, diffs: [], elements: 0, props: 0,
                              error: String(e)}); }
  }
  await fetch('/__result', {method: 'POST',
                            body: JSON.stringify(results)});
  document.title = 'done';
})();
</script>
"""


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves exactly one tree, from its root.

    Root, not a path prefix. Every asset path on this site is root-absolute,
    so a prefix would send both iframes to the same /css/main.css - see the
    module docstring.
    """
    root: pathlib.Path = None
    driver_html: str = ""
    result_path: pathlib.Path = None

    def log_message(self, *a):  # quiet
        pass

    def _resolve(self, path: str):
        path = path.split("?")[0].split("#")[0].lstrip("/")
        base = self.root.resolve()
        target = (base / path).resolve()
        if base != target and base not in target.parents:
            return None
        if target.is_dir():
            target = target / "index.html"
        return target

    def end_headers(self):
        # The driver reaches across origins into both frames. Chrome is
        # launched with --disable-web-security, and these say the same thing
        # from the server side so the probe does not depend on that flag alone.
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        if self.path.startswith("/__driver"):
            body = self.driver_html.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        target = self._resolve(self.path)
        if target is None or not target.is_file():
            self.send_error(404)
            return
        data = target.read_bytes()
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json",
            ".woff2": "font/woff2", ".woff": "font/woff",
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml", ".ico": "image/x-icon",
            ".webmanifest": "application/manifest+json",
        }.get(target.suffix.lower(), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        self.result_path.write_bytes(self.rfile.read(n))
        self.send_response(204)
        self.end_headers()


class Server(socketserver.ThreadingTCPServer):
    """ThreadingHTTPServer. A single-threaded one deadlocks against Chrome's
    parallel connections and every page times out - DO-NOT-BREAK, render_nav."""
    allow_reuse_address = True
    daemon_threads = True


def run_chrome(url: str, result: pathlib.Path, timeout: float) -> None:
    profile = tempfile.mkdtemp(prefix="csdiff-chrome-")
    argv = [
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
        "--no-first-run", "--no-default-browser-check",
        "--disable-extensions", "--disable-background-networking",
        "--disable-component-update", "--disable-features=Translate",
        # One origin per tree is what makes root-absolute asset paths resolve
        # inside the right tree; reading across the two frames then needs this.
        # It is why --user-data-dir above is mandatory: Chrome ignores
        # --disable-web-security without one.
        "--disable-web-security",
        # Determinism, both learned from a false positive on two IDENTICAL
        # trees. A vertical scrollbar takes ~15px off the frame's available
        # width, `.container`'s `margin: 0 auto` resolves against that width,
        # and the computed margin then differs for no reason at all. And
        # tutoring.html loads Calendly from the network, whose arrival time
        # decides the page height and therefore whether there is a scrollbar.
        # Hide the one and refuse the other, and both sides become the same
        # measurement twice.
        "--hide-scrollbars",
        "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1",
        f"--user-data-dir={profile}",
        "--window-size=1280,900",
        url,
    ]
    proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True)
    deadline = time.time() + timeout
    try:
        while time.time() < deadline:
            if result.exists() and result.stat().st_size:
                time.sleep(0.3)          # let the write settle
                return
            time.sleep(0.25)
        raise SystemExit(f"Chrome produced no result within {timeout:.0f}s")
    finally:
        # Chrome's updater and crash-handler children inherit the pipe and the
        # process never exits. Kill the GROUP, and swallow both errors.
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(os.getpgid(proc.pid), sig)
            except (ProcessLookupError, PermissionError):
                pass
            time.sleep(0.2)
            if proc.poll() is not None:
                break
        shutil.rmtree(profile, ignore_errors=True)


def published_pages(tree: pathlib.Path) -> list[str]:
    out = subprocess.run(["git", "ls-files", "*.html"], cwd=tree,
                         capture_output=True, text=True, check=True).stdout.split()
    cwd = os.getcwd()
    os.chdir(tree)
    try:
        ex = build_sitemap.excludes()
        pages = [f for f in out if build_sitemap.published(f, ex)]
    finally:
        os.chdir(cwd)
    return [p for p in pages if not p.startswith("templates/")]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("pages", nargs="*",
                    help="repo-relative .html paths; default is every page "
                         "that differs between the trees")
    ap.add_argument("--all", action="store_true",
                    help="every published page in OLD, not just those that differ")
    ap.add_argument("--width", type=int, default=1200)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--max-report", type=int, default=15)
    ap.add_argument("--selftest", action="store_true",
                    help="inject one declaration into a COPY of NEW's "
                         "css/main.css and require this script to see it")
    args = ap.parse_args()

    old = pathlib.Path(args.old).resolve()
    new = pathlib.Path(args.new).resolve()
    for t in (old, new):
        if not (t / "css" / "main.css").exists():
            raise SystemExit(f"{t} does not look like a copy of this repo")

    pages = args.pages
    if not pages:
        allp = published_pages(old)
        if args.all:
            pages = allp
        else:
            pages = [p for p in allp
                     if not (new / p).exists()
                     or (old / p).read_bytes() != (new / p).read_bytes()]
    if not pages:
        print("no pages differ between the trees; nothing to compare")
        return 0

    tmp = None
    if args.selftest:
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="csdiff-selftest-"))
        shutil.copytree(new, tmp / "new", symlinks=True,
                        ignore=shutil.ignore_patterns(".git"))
        new = tmp / "new"
        css = new / "css" / "main.css"
        css.write_text(css.read_text() + "\n.paper-info { letter-spacing: 3px }\n")
        print("--selftest: appended one declaration to NEW's css/main.css")

    result = pathlib.Path(tempfile.mkdtemp(prefix="csdiff-")) / "result.json"

    servers = []
    origins = {}
    for label, root in (("old", old), ("new", new)):
        H = type(f"Handler_{label}", (Handler,), {"root": root,
                                                  "result_path": result})
        srv = Server(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        servers.append(srv)
        origins[label] = f"http://127.0.0.1:{srv.server_address[1]}"

    driver_srv = servers[0]
    driver_srv.RequestHandlerClass.driver_html = (
        DRIVER.replace("__PAGES__", json.dumps(pages))
              .replace("__OLD_ORIGIN__", json.dumps(origins["old"]))
              .replace("__NEW_ORIGIN__", json.dumps(origins["new"]))
              .replace("__W__", str(args.width))
              .replace("__H__", str(args.height)))

    print(f"serving OLD={old} on {origins['old']}")
    print(f"        NEW={new} on {origins['new']}")
    print(f"{len(pages)} page(s) to compare at {args.width}x{args.height}")

    try:
        run_chrome(f"{origins['old']}/__driver", result, args.timeout)
    finally:
        for s in servers:
            s.shutdown()

    data = json.loads(result.read_text())
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)

    bad = 0
    total_diffs = 0
    total_elements = 0
    props = 0
    for row in data:
        total_elements += row["elements"]
        props = max(props, row["props"])
        if row["error"]:
            bad += 1
            print(f"  ERROR  {row['page']}: {row['error']}")
            continue
        if row["diffs"]:
            bad += 1
            total_diffs += len(row["diffs"])
            print(f"  DIFF   {row['page']}: {len(row['diffs'])} computed "
                  f"propert{'y' if len(row['diffs']) == 1 else 'ies'} differ")
            for d in row["diffs"][: args.max_report]:
                print(f"           [{d['at']}] {d['where']}  {d['prop']}: "
                      f"{d['old']!r} -> {d['new']!r}")
            if len(row["diffs"]) > args.max_report:
                print(f"           ... and {len(row['diffs']) - args.max_report} more")

    print(f"\n{len(data)} pages, {total_elements} elements, "
          f"{props} computed properties each, {total_diffs} differences")
    if args.selftest:
        if bad:
            print("SELFTEST PASS: the injected declaration was seen. This "
                  "probe can fail, so a zero from it means something.")
            return 0
        print("SELFTEST FAIL: the injected declaration was NOT seen. Any "
              "zero this probe reports is worthless until that is fixed.",
              file=sys.stderr)
        return 1
    if bad:
        print(f"FAIL: {bad} of {len(data)} pages are not cascade-neutral",
              file=sys.stderr)
        return 1
    print("PASS: every element resolves every property identically")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
