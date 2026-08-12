#!/usr/bin/env python3
"""Render a tree in headless Chrome and record what the navigation actually is.

    python3 docs/audit/scripts/harness/render_nav.py TREE out.json
    python3 docs/audit/scripts/harness/render_nav.py --compare old.json new.json
    python3 docs/audit/scripts/harness/render_nav.py --selftest TREE

Wave 4.10, generalising what Wave 2 Phase 7 did in a scratch script and did
not keep. `compare_trees.py`'s ten assertions are deliberately blind to
behaviour: they read committed bytes. Phase 7 moved the nav out of a runtime
fetch and 4.10 rewrites the script that builds it, and in both cases the
question the assertions cannot answer is the only one that matters - does the
same menu, with the same links, still appear in a browser.

So this serves the tree over HTTP and drives real Chrome at it.

    nav       every <a> in #nav: href, visible text, nesting depth, role,
              and which <li> carries class="current"
    panel     every <a> in the mobile #navPanel. That panel is BUILT BY
              SCRIPT, so it exists only in a rendered page - which is exactly
              why a bytes comparison cannot see this wave at all
    titleBar  the toggle button's tag, id, class and aria-*
    footer    every <a> in the footer, and the skip link
    counts    element tallies that would move if a rewrite dropped something

**How the probe gets in.** Chrome 132 removed `--headless=old` and with it
`--repl`, so there is no stdlib way to evaluate an expression in the page:
`--dump-dom` returns markup and nothing else. The server therefore injects the
probe into every HTML response, byte-identical on both sides, and the probe
writes its result into a `<pre id="__probe">` that `--dump-dom` then hands
back. Base64, so no HTML escaping can touch it. Phase 7 injected its
PerformanceObserver the same way and for the same reason.

**Threaded server, deliberately.** http.server's default serialises requests,
so a page that fetches while it renders deadlocks against its own server and
the capture times out with an empty nav.

**Two viewports, because the two navs are different DOM.** #nav is
display:none below 768px and #navPanel is only visible below it. One width
would leave half the wave unchecked.

Standard library only, plus Chrome, which macOS ships.
"""

from __future__ import annotations

import argparse
import base64
import http.server
import io
import json
import os
import pathlib
import re
import signal
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# One page per family, plus the two commercial pages and the past-papers hub
# that earns more than anything on the site outside the homepage (PH03-049).
# The nav is one file baked 463 times, so a regression on any of these is a
# regression on its whole family.
PAGES = [
    "/",                                          # root, hand-written
    "/tutoring.html",                             # root, commercial
    "/past-papers/ocr/",                          # past-papers hub, hand-written
    "/revision-notes/",                           # notes-other, hand-written
    "/revision-notes/edexcel-theme-1/",           # notes hub, generated
    "/revision-notes/edexcel-theme-1/1-1-1-economics-as-a-social-science.html",
    "/revision-notes/glossary/edexcel-a/",        # glossary, generated
    "/practice-questions/edexcel-theme-1/",       # questions, generated
    "/past-paper-questions/",                     # ppq master, generated
    "/flashcards/edexcel-a/theme-1/",             # flashcards, generated
]

VIEWPORTS = [1400, 390]

PROBE_JS = r"""
(function () {
  function txt(el) { return el.textContent.replace(/\s+/g, " ").trim(); }
  function depth(a) {
    var d = 0, n = a.closest("li");
    while (n) { d++; n = n.parentElement.closest("li"); }
    return d;
  }
  function links(root, extra) {
    return [].slice.call(root.querySelectorAll("a")).map(function (a) {
      var o = { href: a.getAttribute("href"), text: txt(a) };
      if (extra) extra(a, o);
      return o;
    });
  }
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  // Visible to a reader, not merely present. Implementation-independent on
  // purpose: dropotron detaches the submenu into a body-level .dropotron <ul>
  // on hover, a CSS or hand-written dropdown reveals it in place, and this
  // question has the same answer either way.
  function shown(el) {
    if (!el.getClientRects().length) return false;
    var s = getComputedStyle(el);
    return s.visibility !== "hidden" && parseFloat(s.opacity || "1") > 0.01;
  }
  function visibleMenuLinks() {
    var out = [];
    [].slice.call(document.querySelectorAll("#nav ul ul a, .dropotron a, .nav-submenu a"))
      .forEach(function (a) {
        if (shown(a)) out.push({ href: a.getAttribute("href"), text: txt(a) });
      });
    return out;
  }
  function fire(el, type, init) {
    el.dispatchEvent(new MouseEvent(type, Object.assign(
      { bubbles: true, cancelable: true, view: window }, init || {})));
  }
  function touch(el, type, x) {
    var t;
    try {
      t = new Touch({ identifier: 1, target: el, pageX: x, clientX: x,
                      pageY: 100, clientY: 100 });
    } catch (e) { return false; }          // Touch is unavailable: say so
    el.dispatchEvent(new TouchEvent(type, {
      bubbles: true, cancelable: true, touches: type === "touchend" ? [] : [t],
      targetTouches: type === "touchend" ? [] : [t], changedTouches: [t],
    }));
    return true;
  }
  function panelState(tag) {
    var panel = document.querySelector("#navPanel");
    var btn = document.querySelector("#titleBar button, #titleBar a.toggle");
    return {
      step: tag,
      bodyClass: document.body.classList.contains("navPanel-visible"),
      ariaHidden: panel ? panel.getAttribute("aria-hidden") : null,
      ariaExpanded: btn ? btn.getAttribute("aria-expanded") : null,
      btnLabel: btn ? btn.getAttribute("aria-label") : null,
      // The panel slides in from translateX(-275px). Read the COMPUTED
      // transform, not getBoundingClientRect().left: under
      // --virtual-time-budget the rect keeps reporting -275 whether the panel
      // is open or shut, so a rect-based test would have passed on a panel
      // that never moved. The computed value is resolved from the cascade and
      // is honest.
      panelTransform: panel ? getComputedStyle(panel).transform : null,
      focusIsToggle: !!btn && document.activeElement === btn,
    };
  }

  // Desktop: open ONE top-level item and record what became visible.
  //
  // One per page load, deliberately. dropotron responds to the first
  // synthetic hover of a page and ignores every one after it - measured:
  // hovering items 1, 2 and 3 in sequence leaves the first menu open and
  // never opens the other two, in any order, with any wait. So a loop would
  // silently report "no dropdown" for items 2 and 3 and the comparison would
  // then pass by being blind rather than by being right. OPENER is
  // substituted per Chrome run.
  async function desktop() {
    var idx = OPENER;
    var items = [].slice.call(document.querySelectorAll("#nav > ul > li"))
      .filter(function (li) { return li.querySelector("ul"); });
    if (idx < 0 || idx >= items.length) {
      return { openers: items.length, skipped: true };
    }
    var li = items[idx], a = li.querySelector("a");
    var before = visibleMenuLinks().length;
    fire(a, "mouseover"); fire(li, "mouseover");
    fire(a, "mouseenter"); fire(li, "mouseenter");
    fire(a, "pointerenter");
    a.focus();
    await wait(1500);
    return {
      openers: items.length,
      opener: txt(a),
      closedBefore: before,
      open: visibleMenuLinks(),
    };
  }

  // Mobile: the six behaviours the assertions cannot see.
  async function mobile() {
    var steps = [panelState("rest")];
    var btn = document.querySelector("#titleBar button, #titleBar a.toggle");
    var panel = document.querySelector("#navPanel");
    if (!btn || !panel) return steps;

    btn.click();                    await wait(800); steps.push(panelState("after-toggle-open"));
    var esc = new KeyboardEvent("keydown", { key: "Escape", bubbles: true, cancelable: true });
    document.dispatchEvent(esc);    await wait(800); steps.push(panelState("after-escape"));

    btn.click();                    await wait(800); steps.push(panelState("reopened"));
    fire(document.body, "click");   await wait(800); steps.push(panelState("after-click-outside"));

    btn.click();                    await wait(800); steps.push(panelState("reopened-2"));
    var ok = touch(panel, "touchstart", 200) &&
             touch(panel, "touchmove", 100) &&
             touch(panel, "touchend", 100);
    await wait(800);
    var s = panelState("after-swipe-left"); s.touchSupported = ok;
    steps.push(s);
    return steps;
  }

  async function run() {
    var nav = document.querySelector("#nav");
    var panel = document.querySelector("#navPanel");
    var bar = document.querySelector("#titleBar");
    var btn = bar ? bar.querySelector("button, a") : null;
    var foot = document.querySelector("#footer") || document.querySelector("footer");
    var skip = document.querySelector("a.skip-to-content");
    var out = {
      nav: nav ? links(nav, function (a, o) {
        o.depth = depth(a);
        o.role = a.getAttribute("role");
      }) : null,
      navCurrent: nav ? [].slice.call(nav.querySelectorAll("li.current"))
        .map(function (li) { return li.getAttribute("data-page"); }) : null,
      navDisplay: nav ? getComputedStyle(nav).display : null,
      panel: panel ? links(panel, function (a, o) {
        o.cls = a.getAttribute("class");
        var s = a.querySelector("span");
        o.indent = s ? s.className : null;
      }) : null,
      panelAttrs: panel ? {
        tag: panel.tagName,
        role: panel.getAttribute("role"),
        label: panel.getAttribute("aria-label"),
        hidden: panel.getAttribute("aria-hidden"),
      } : null,
      titleBar: btn ? {
        tag: btn.tagName,
        id: btn.id,
        cls: btn.getAttribute("class"),
        label: btn.getAttribute("aria-label"),
        expanded: btn.getAttribute("aria-expanded"),
        controls: btn.getAttribute("aria-controls"),
      } : null,
      skipLink: skip ? { href: skip.getAttribute("href"), text: txt(skip) } : null,
      footer: foot ? links(foot) : null,
      counts: {
        a: document.querySelectorAll("a").length,
        img: document.querySelectorAll("img").length,
        script: document.querySelectorAll("script[src]").length,
        li: document.querySelectorAll("li").length,
      },
    };
    // The interaction phase runs LAST and its results are recorded
    // separately, so a change in behaviour can never be confused with a
    // change in the nav's rest state.
    //
    // Transitions are switched off first, and that is not tidiness. Chrome's
    // animation clock does not advance under --virtual-time-budget, so
    // getComputedStyle during a running transition keeps returning the FROM
    // value: the panel reported transform: translateX(-275px) open and shut
    // alike, and getBoundingClientRect().left reported -275 in both states
    // too. A test that cannot return a second value is not a test. With
    // transitions off the computed value is the one the cascade settles on,
    // which is the question actually being asked. Injected identically into
    // both sides, and after the rest snapshot, which reads no geometry.
    var kill = document.createElement("style");
    kill.id = "__noanim";
    kill.textContent = "*,*::before,*::after{transition:none !important;" +
                       "animation:none !important}";
    document.head.appendChild(kill);
    await wait(50);

    out.interact = window.innerWidth >= 768 ? await desktop() : await mobile();

    var pre = document.createElement("pre");
    pre.id = "__probe";
    pre.textContent = btoa(unescape(encodeURIComponent(JSON.stringify(out))));
    document.documentElement.appendChild(pre);
  }
  // The nav script runs at DOMContentLoaded; main.js clears is-preload 100 ms
  // after load. Wait past both, and let --virtual-time-budget fast-forward it.
  window.addEventListener("load", function () { window.setTimeout(run, 400); });
})();
"""

MARK = re.compile(r'<pre id="__probe">([A-Za-z0-9+/=\s]*)</pre>')


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves the tree, and appends the probe to every HTML response.

    `opener` is the index of the desktop dropdown this run should open, or -1
    for none. It is a per-run constant rather than a query parameter so that
    the URL Chrome is given is exactly the URL a reader would visit.
    """

    opener = -1

    def log_message(self, *a):  # noqa: D102 - silence the access log
        pass

    def send_head(self):
        path = pathlib.Path(self.translate_path(self.path))
        if path.is_dir():
            idx = path / "index.html"
            if idx.is_file() and not self.path.endswith("/"):
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            path = idx
        if path.suffix != ".html" or not path.is_file():
            return super().send_head()
        body = path.read_bytes()
        probe = f"var OPENER = {self.opener};\n" + PROBE_JS
        body += b"<script>" + probe.encode() + b"</script>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        return io.BytesIO(body)


class Threaded(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def serve(root: pathlib.Path, opener: int = -1) -> tuple[Threaded, int]:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    class Bound(Handler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(root), **kw)

    Bound.opener = opener
    httpd = Threaded(("127.0.0.1", port), Bound)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def render(url: str, width: int, profile: str, deadline: float = 45.0) -> dict:
    """One Chrome run, one page, one viewport.

    **Do not use subprocess.run() here, however much it wants to be used.**
    Chrome writes the DOM and then does not exit: its updater and
    crash-handler children inherit the stdout pipe, so waiting for EOF waits
    for those, and `--dump-dom` hangs on a `data:text/html,<h1>hi</h1>` URL as
    readily as on a real page. It is intermittent, which is worse - four
    captures succeeded before the first hang here. So: write stdout to a file,
    poll the file for the probe, then kill the whole process group.
    """
    cmd = [
        CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
        "--no-first-run", "--no-default-browser-check", "--disable-extensions",
        "--disable-crash-reporter", "--disable-component-update",
        "--disable-background-networking", "--disable-sync",
        # Every external origin fails DNS immediately instead of timing out.
        # Deterministic, offline, and byte-identical on both sides: the site
        # contacts 4 third-party origins (asset_census 9) and none of them has
        # anything to do with the navigation.
        "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1",
        "--run-all-compositor-stages-before-draw",
        "--disable-features=LazyImageLoading",
        "--virtual-time-budget=8000",
        f"--window-size={width},900",
        f"--user-data-dir={profile}",
        "--dump-dom", url,
    ]
    with tempfile.NamedTemporaryFile("w+", suffix=".html") as sink:
        p = subprocess.Popen(cmd, stdout=sink, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        found = None
        end = time.time() + deadline
        while time.time() < end:
            time.sleep(0.25)
            sink.flush()
            text = pathlib.Path(sink.name).read_text(errors="replace")
            m = MARK.search(text)
            if m:
                found = m.group(1)
                break
            if p.poll() is not None and "</html>" in text:
                break
        # Kill the group so the updater and crash-handler children go too,
        # then the process itself. PermissionError happens when one member of
        # the group has been adopted by launchd and cannot be signalled - that
        # is not a reason to abandon the capture, and swallowing only
        # ProcessLookupError made this fail intermittently, on the second of
        # two identical runs.
        for kill in (lambda: os.killpg(p.pid, signal.SIGKILL), p.kill):
            try:
                kill()
            except (ProcessLookupError, PermissionError):
                pass
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        if not found:
            raise RuntimeError(f"no probe result for {url} @{width}px "
                               f"after {deadline:.0f}s")
    return json.loads(base64.b64decode(found).decode())


# The page the desktop dropdowns are opened on. One page is enough: the nav is
# one template baked into 463 files and check 9 proves the copies identical, so
# a dropdown that opens here opens everywhere. It is a generated notes hub
# rather than a root page so the capture also exercises the baked block.
DROPDOWN_PAGE = "/revision-notes/edexcel-theme-1/"
DROPDOWN_OPENERS = 3   # Revision Notes, Practice Questions, Past Papers


def capture(tree: pathlib.Path, pages=PAGES, dropdowns: bool = True) -> dict:
    out: dict = {}
    httpd, port = serve(tree)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            for page in pages:
                for w in VIEWPORTS:
                    key = f"{page}@{w}"
                    out[key] = render(f"http://127.0.0.1:{port}{page}", w,
                                      f"{tmp}/w{w}")
                    print(f"  captured {key}", file=sys.stderr)
    finally:
        httpd.shutdown()

    if not dropdowns:
        return out
    # A fresh server per opener, because the index is baked into the injected
    # probe and dropotron only answers the first synthetic hover of a page.
    for idx in range(DROPDOWN_OPENERS):
        httpd, port = serve(tree, opener=idx)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                key = f"{DROPDOWN_PAGE}@1400#dropdown{idx}"
                out[key] = render(f"http://127.0.0.1:{port}{DROPDOWN_PAGE}",
                                  1400, f"{tmp}/d{idx}")
                print(f"  captured {key}", file=sys.stderr)
        finally:
            httpd.shutdown()
    return out


def compare(a: dict, b: dict) -> int:
    keys = sorted(set(a) | set(b))
    bad = 0
    for k in keys:
        if k not in a or k not in b:
            print(f"DIFF {k}: present in only one capture")
            bad += 1
            continue
        if a[k] == b[k]:
            continue
        bad += 1
        print(f"DIFF {k}")
        for field in sorted(set(a[k]) | set(b[k])):
            if a[k].get(field) != b[k].get(field):
                print(f"    {field}")
                print(f"      OLD {json.dumps(a[k].get(field))[:500]}")
                print(f"      NEW {json.dumps(b[k].get(field))[:500]}")
    print(f"{len(keys)} page/viewport captures, {bad} differing")
    return 1 if bad else 0


def selftest(tree: pathlib.Path) -> int:
    """Prove the comparison can fail.

    A comparison that has only ever returned SAME has not been tested. This
    captures one page, retypes one nav label in a scratch copy of the tree,
    captures again, and requires the two to differ. Wave 2 Phase 7 did the
    same by hand; doing it in code means it is done every time.
    """
    import shutil
    one = ["/revision-notes/edexcel-theme-1/"]
    before = capture(tree, one, dropdowns=False)
    with tempfile.TemporaryDirectory() as tmp:
        scratch = pathlib.Path(tmp) / "tree"
        shutil.copytree(tree, scratch, symlinks=True,
                        ignore=shutil.ignore_patterns(".git"))
        page = scratch / "revision-notes/edexcel-theme-1/index.html"
        src = page.read_text(encoding="utf-8")
        if ">Past Papers</a>" not in src:
            print("selftest: anchor text not found; update the selftest")
            return 2
        page.write_text(src.replace(">Past Papers</a>", ">Past Paper</a>", 1),
                        encoding="utf-8")
        after = capture(scratch, one, dropdowns=False)
    rc = compare(before, after)
    if rc == 0:
        print("SELFTEST FAILED: retyping a nav label produced no difference")
        return 1
    print("selftest ok: the comparison detects a one-character nav change")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--compare", nargs=2, metavar=("OLD", "NEW"))
    ap.add_argument("--selftest", metavar="TREE")
    ap.add_argument("tree", nargs="?")
    ap.add_argument("out", nargs="?")
    args = ap.parse_args()

    if args.compare:
        a = json.loads(pathlib.Path(args.compare[0]).read_text())
        b = json.loads(pathlib.Path(args.compare[1]).read_text())
        return compare(a, b)

    if not pathlib.Path(CHROME).exists():
        print(f"error: no Chrome at {CHROME}", file=sys.stderr)
        return 2

    if args.selftest:
        return selftest(pathlib.Path(args.selftest).resolve())

    if not args.tree or not args.out:
        ap.error("give TREE and OUT, or --compare OLD NEW, or --selftest TREE")
    data = capture(pathlib.Path(args.tree).resolve())
    pathlib.Path(args.out).write_text(json.dumps(data, indent=1, sort_keys=True))
    print(f"{len(data)} captures -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
