#!/usr/bin/env python3
"""Serve a tree the way GitHub Pages does, closely enough for a local A/B.

    python3 seo/tools/serve_like_pages.py DIR PORT

`python3 -m http.server` is HTTP/1.0 with no keep-alive and no compression.
That is harmless when both sides of an A/B fetch the same things from it,
and misleading the moment one side starts serving something the other side
fetched from a CDN: Lighthouse's simulator charges a fresh TCP connection
per HTTP/1.0 request and the full uncompressed byte count, so self-hosting
the fonts measured SLOWER locally than fetching them from fonts.gstatic.com
over h3 - an artefact of the server, not of the change (2026-08-23).

This one is HTTP/1.1 with keep-alive, gzips the text types on the fly
(HTML, CSS, JS, JSON, SVG, XML, manifest) and knows woff2/webp/webmanifest.
Still not the real thing - no HTTP/2, no CDN edge - but the same for both
sides, and the differences it cannot model (connection reuse across origins,
compression) no longer favour one side. Standard library only.
"""

from __future__ import annotations

import gzip
import http.server
import mimetypes
import pathlib
import socketserver
import sys

mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("application/json", ".json")

COMPRESS = {".html", ".css", ".js", ".json", ".svg", ".xml", ".webmanifest", ".txt"}


class Handler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # quiet
        pass

    def do_GET(self):
        path = pathlib.Path(self.translate_path(self.path.split("?")[0]))
        if path.is_dir():
            path = path / "index.html"
        if not path.is_file():
            self.send_error(404)
            return
        ctype = self.guess_type(str(path))
        data = path.read_bytes()
        gz = (path.suffix.lower() in COMPRESS
              and "gzip" in self.headers.get("Accept-Encoding", ""))
        if gz:
            data = gzip.compress(data, 6)
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        if gz:
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Vary", "Accept-Encoding")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "max-age=600")
        self.end_headers()
        self.wfile.write(data)


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> int:
    root, port = sys.argv[1], int(sys.argv[2])
    handler = lambda *a, **k: Handler(*a, directory=root, **k)  # noqa: E731
    with Server(("127.0.0.1", port), handler) as srv:
        print(f"serving {root} on http://127.0.0.1:{port} (HTTP/1.1, gzip)")
        srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
