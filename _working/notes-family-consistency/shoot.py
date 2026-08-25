#!/usr/bin/env python3
"""Screenshot the three redesigned pages for the Gate 1 evidence pack.

Serves the repo on a threaded local server (a single-threaded http.server
deadlocks against Chrome's parallel connections - docs/audit/DO-NOT-BREAK.md),
drives headless Chrome one capture at a time with a hard timeout, and kills
the process group afterwards (Chrome's updater children inherit the pipe and
hang a plain subprocess.run - same register).

360px captures use the iframe wrapper trick: headless Chrome will not open a
window narrower than ~500px, so the page is loaded inside a centred 360px
iframe in a 600px window and the shot is cropped to the iframe with Pillow.
"""
import http.server
import os
import pathlib
import signal
import socketserver
import subprocess
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "_working/notes-family-consistency/shots"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 8931

PAGES = {
    "micro": "/revision-notes/microeconomics-diagrams.html",
    "macro": "/revision-notes/macroeconomics-diagrams.html",
    "topic-1-2-2": "/revision-notes/edexcel-theme-1/1-2-2-demand.html",
    "hub-theme-1": "/revision-notes/edexcel-theme-1/",
}

FULL_H = 14000
TOP_H = 1400


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, *a):
        pass


def chrome(args, timeout=15):
    # Chrome writes the shot ~1-2s after its --timeout=5000 stop but does
    # not exit; 15s covers the write, then the process group is killed.
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1",
         f"--user-data-dir=/tmp/ea-shoot-profile"] + args,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def wrapper_for(url, height):
    name = f"wrap-{abs(hash((url, height)))}.html"
    p = OUT / name
    p.write_text(
        "<!doctype html><html><head><meta charset='utf-8'></head>"
        "<body style='margin:0;background:#888'>"
        f"<iframe src='{url}' style='display:block;margin:0 auto;border:0;"
        f"width:360px;height:{height}px'></iframe></body></html>",
        encoding="utf-8")
    return f"http://127.0.0.1:{PORT}/_working/notes-family-consistency/shots/{name}"


def crop_center(png, width):
    from PIL import Image
    im = Image.open(png)
    x = (im.width - width) // 2
    im.crop((x, 0, x + width, im.height)).save(png)


def nojs_copy(path, key):
    """A copy of the page with every <script> stripped - '--blink-settings'
    is silently ignored by headless=new (rc 0, no screenshot written), so
    "JS off" is a served variant with no scripts instead."""
    import re
    text = (ROOT / path.lstrip("/")).read_text(encoding="utf-8")
    text = re.sub(r"<script\b.*?</script>", "", text, flags=re.S)
    name = f"nojs-{key}.html"
    (OUT / name).write_text(text, encoding="utf-8")
    return f"/_working/notes-family-consistency/shots/{name}"


def shot(name, path, width, height, js, out):
    if not js:
        path = nojs_copy(path, name)
    url = f"http://127.0.0.1:{PORT}{path}"
    # Real clock (--timeout), not --virtual-time-budget: under virtual time
    # Chrome painted one committed shot with the filter bar at a fraction of
    # its measured geometry, and freezes colour transitions at their FROM
    # value - the same class of lie docs/audit's render_nav.py records.
    if width == 360:
        url = wrapper_for(url, height)
        chrome([f"--window-size=600,{height}",
                f"--screenshot={out}", "--timeout=5000", url])
        crop_center(out, 360)
    else:
        chrome([f"--window-size={width},{height}",
                f"--screenshot={out}", "--timeout=5000", url])
    print("wrote", pathlib.Path(out).name)


def pdf(path, out):
    url = f"http://127.0.0.1:{PORT}{path}"
    chrome([f"--print-to-pdf={out}", "--no-pdf-header-footer",
            "--timeout=5000", url])
    print("wrote", pathlib.Path(out).name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    only = sys.argv[1:] or list(PAGES)
    for key in only:
        path = PAGES[key]
        full = FULL_H if key in ("micro", "macro") else 8000
        shot(key, path, 1280, TOP_H, True, OUT / f"{key}-1280-top.png")
        shot(key, path, 1280, full, True, OUT / f"{key}-1280-full.png")
        shot(key, path, 360, TOP_H, True, OUT / f"{key}-360-top.png")
        shot(key, path, 360, full, True, OUT / f"{key}-360-full.png")
        if key in ("micro", "macro"):
            shot(key, path, 1280, TOP_H, False, OUT / f"{key}-1280-nojs.png")
            shot(key, path, 360, TOP_H, False, OUT / f"{key}-360-nojs.png")
    pdf(PAGES["micro"], OUT / "micro-print.pdf")
    for w in list(OUT.glob("wrap-*.html")) + list(OUT.glob("nojs-*.html")):
        w.unlink()
    srv.shutdown()


if __name__ == "__main__":
    main()
