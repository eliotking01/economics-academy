#!/usr/bin/env python3
"""Probe every URL variant of every page, and every PDF, over pooled connections.

Split out of crawl.py because urllib opens a fresh TCP+TLS connection per
request. At ~2,300 variant probes that cost ~13s per page against this host -
over an hour of connection setup for a few minutes of actual data. http.client
with one keep-alive connection per (scheme, host) does the same work in a few
minutes and is markedly gentler on the server: 3 connections instead of 2,300.

For each page it records which of these return 200 / 301 / 404:

    /path/            /path/index.html          (directory pages)
    /path.html        /path                     (extensionless duplicate)
    https://www.…     http://…                  (host and protocol)

Politeness is unchanged: ~2 requests/second, same User-Agent, retry on 429/5xx.

Usage:
    python3 seo/tools/probe_variants.py
    python3 seo/tools/probe_variants.py --no-pdfs --limit 20
"""

from __future__ import annotations

import argparse
import csv
import http.client
import ssl
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import build as build_inventory, url_for  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
UA = "EconomicsAcademy-SEO-Audit/1.0 (+https://economicsacademy.co.uk; site owner audit)"
DELAY = 0.5
APEX = "economicsacademy.co.uk"
WWW = "www.economicsacademy.co.uk"

KINDS = ("dir", "dir_index", "html", "extensionless", "www", "http")


def ssl_context() -> ssl.SSLContext:
    """python.org builds ship without a CA bundle; fall back to the system one."""
    ctx = ssl.create_default_context()
    if ctx.cert_store_stats()["x509_ca"] == 0:
        for b in ("/etc/ssl/cert.pem", "/opt/homebrew/etc/openssl@3/cert.pem"):
            if Path(b).exists():
                ctx.load_verify_locations(cafile=b)
                break
        else:
            raise SystemExit("No CA bundle found.")
    return ctx


class Pool:
    """One persistent connection per (scheme, host), reopened if the server closes it."""

    def __init__(self):
        self.ctx = ssl_context()
        self.conns: dict[tuple[str, str], http.client.HTTPConnection] = {}
        self.last = 0.0
        self.requests = 0

    def _conn(self, scheme: str, host: str) -> http.client.HTTPConnection:
        key = (scheme, host)
        if key not in self.conns:
            self.conns[key] = (
                http.client.HTTPSConnection(host, timeout=20, context=self.ctx)
                if scheme == "https"
                else http.client.HTTPConnection(host, timeout=20)
            )
        return self.conns[key]

    def head(self, scheme: str, host: str, path: str, retries: int = 3) -> tuple[int, str]:
        wait = DELAY - (time.monotonic() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.monotonic()

        for attempt in range(retries):
            c = self._conn(scheme, host)
            try:
                c.request("HEAD", path, headers={"User-Agent": UA, "Accept": "*/*"})
                r = c.getresponse()
                r.read()
                self.requests += 1
                loc = r.getheader("Location", "") or ""
                if r.status == 429 or r.status >= 500:
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt * 2)
                        continue
                return r.status, loc
            except Exception:  # noqa: BLE001 - stale keep-alive, reset, timeout
                try:
                    c.close()
                except Exception:  # noqa: BLE001
                    pass
                self.conns.pop((scheme, host), None)
                if attempt < retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                return 0, ""
        return 0, ""

    def close(self):
        for c in self.conns.values():
            try:
                c.close()
            except Exception:  # noqa: BLE001
                pass


def variants_for(page: str) -> dict[str, tuple[str, str, str]]:
    """(scheme, host, path) per variant kind, for one repo path."""
    if page == "index.html":
        return {
            "dir": ("https", APEX, "/"),
            "dir_index": ("https", APEX, "/index.html"),
            "www": ("https", WWW, "/"),
            "http": ("http", APEX, "/"),
        }
    if page.endswith("/index.html"):
        d = "/" + page[: -len("index.html")]
        return {
            "dir": ("https", APEX, d),
            "dir_index": ("https", APEX, d + "index.html"),
            "extensionless": ("https", APEX, d.rstrip("/")),
            "www": ("https", WWW, d),
            "http": ("http", APEX, d),
        }
    p = "/" + page
    return {
        "html": ("https", APEX, p),
        "extensionless": ("https", APEX, p[: -len(".html")]),
        "dir_index": ("https", APEX, p[: -len(".html")] + "/index.html"),
        "www": ("https", WWW, p),
        "http": ("http", APEX, p),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="seo/01-variants.csv")
    ap.add_argument("--pdfs-out", default="seo/01-pdfs.csv")
    ap.add_argument("--no-pdfs", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    inv = build_inventory()
    pages = sorted(inv["indexable"] + inv["deliberate_noindex"])
    if args.limit:
        pages = pages[: args.limit]

    pool = Pool()
    t0 = time.monotonic()
    rows = []
    print(f"== variant probe: {len(pages)} pages", file=sys.stderr, flush=True)
    for i, page in enumerate(pages, 1):
        row = {"page": page, "canonical_url": url_for(page)}
        for kind in KINDS:
            v = variants_for(page).get(kind)
            if not v:
                row[f"{kind}_status"] = ""
                row[f"{kind}_location"] = ""
                continue
            scheme, host, path = v
            status, loc = pool.head(scheme, host, path)
            row[f"{kind}_status"] = status
            row[f"{kind}_location"] = loc
        rows.append(row)
        if i % 25 == 0 or i == len(pages):
            el = time.monotonic() - t0
            print(f"  [{i:>4}/{len(pages)}] {el:6.0f}s elapsed, "
                  f"{pool.requests} requests, {i/el*60:.0f} pages/min",
                  file=sys.stderr, flush=True)

    out = REPO / args.out
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)", file=sys.stderr, flush=True)

    if not args.no_pdfs:
        pdfs = inv["pdf_paths"][: args.limit] if args.limit else inv["pdf_paths"]
        print(f"== PDF probe: {len(pdfs)} files", file=sys.stderr, flush=True)
        prows = []
        for i, p in enumerate(pdfs, 1):
            status, loc = pool.head("https", APEX, "/" + p)
            prows.append({"path": p, "url": f"https://{APEX}/{p}",
                          "status": status, "location": loc})
            if i % 50 == 0 or i == len(pdfs):
                print(f"  [{i:>4}/{len(pdfs)}]", file=sys.stderr, flush=True)
        pout = REPO / args.pdfs_out
        with pout.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(prows[0].keys()))
            w.writeheader()
            w.writerows(prows)
        print(f"wrote {pout} ({len(prows)} rows)", file=sys.stderr, flush=True)

    pool.close()
    print(f"total requests: {pool.requests} over {len(pool.conns)} pooled connections",
          file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
