#!/usr/bin/env python3
"""Phase 1 crawler for economicsacademy.co.uk.

Two passes, deliberately separate:

  1. LINK CRAWL   from / following internal links.
  2. INVENTORY    fetch every URL derived from the filesystem.

They differ, and the difference is the point. The site's header and footer are
fetched at runtime by js/components/inject-templates.js, so a link crawl that
does not execute JavaScript sees only the links written into each page's static
HTML. Comparing the two sets shows what a non-rendering crawler can reach.

Then a VARIANT PROBE per page records which of /path/, /path/index.html,
/path.html, /path, http:// and www. return 200 / 301 / 404. That establishes the
real duplication surface on GitHub Pages rather than assuming it.

Politeness: ~2 requests/second, custom User-Agent, retry with backoff on 429 and
5xx. Stdlib only, matching the repo's existing scripts/verify_*.py convention.

Usage:
    python3 seo/tools/crawl.py                    # full: crawl + inventory + variants
    python3 seo/tools/crawl.py --no-variants      # skip the variant probe
    python3 seo/tools/crawl.py --limit 25         # smoke test
    python3 seo/tools/crawl.py --out seo/01-crawl.csv
"""

from __future__ import annotations

import argparse
import csv
import gzip
import html
import json
import re
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import build as build_inventory, url_for, SITE  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
UA = "EconomicsAcademy-SEO-Audit/1.0 (+https://economicsacademy.co.uk; site owner audit)"
DELAY = 0.5          # seconds between requests -> ~2 req/sec
TIMEOUT = 30
RETRIES = 3

ASSET_RE = re.compile(r"\.(css|js|png|jpe?g|gif|svg|ico|webmanifest|woff2?|ttf|xml|json|txt)$", re.I)


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #

class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Capture redirects rather than follow them, so we can record the chain."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _ssl_context() -> ssl.SSLContext:
    """A context that can actually verify economicsacademy.co.uk.

    python.org builds ship without a CA bundle until "Install Certificates.command"
    is run, so ssl.create_default_context() fails with CERTIFICATE_VERIFY_FAILED
    on a perfectly valid certificate. Fall back to the macOS system bundle, which
    is what curl uses. Verification is never disabled - a crawler that ignores
    TLS errors cannot tell a real redirect from a hijacked one.
    """
    ctx = ssl.create_default_context()
    if ctx.cert_store_stats()["x509_ca"] == 0:
        for bundle in ("/etc/ssl/cert.pem",
                       "/usr/local/etc/openssl@3/cert.pem",
                       "/opt/homebrew/etc/openssl@3/cert.pem"):
            if Path(bundle).exists():
                ctx.load_verify_locations(cafile=bundle)
                break
        else:
            raise SystemExit(
                "No CA bundle found. Run "
                "'/Applications/Python 3.12/Install Certificates.command'."
            )
    return ctx


_ctx = _ssl_context()
_opener_manual = urllib.request.build_opener(
    NoRedirect, urllib.request.HTTPSHandler(context=_ctx)
)
_last_request = [0.0]
_lock = threading.Lock()


def _throttle() -> None:
    with _lock:
        wait = DELAY - (time.monotonic() - _last_request[0])
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.monotonic()


def fetch(url: str, method: str = "GET", follow: bool = False) -> dict:
    """One request. Returns status, headers, body and (if follow) the chain."""
    chain: list[tuple[str, int, str]] = []
    current = url
    opener = _opener_manual
    for _hop in range(10):
        for attempt in range(RETRIES):
            _throttle()
            req = urllib.request.Request(current, method=method)
            req.add_header("User-Agent", UA)
            req.add_header("Accept-Encoding", "gzip")
            try:
                with opener.open(req, timeout=TIMEOUT) as resp:
                    raw = resp.read()
                    if resp.headers.get("Content-Encoding") == "gzip":
                        raw = gzip.decompress(raw)
                    return {
                        "url": url, "final_url": current, "status": resp.status,
                        "headers": dict(resp.headers), "body": raw,
                        "chain": chain, "error": "",
                    }
            except urllib.error.HTTPError as e:
                if e.code in (301, 302, 303, 307, 308):
                    loc = e.headers.get("Location", "")
                    nxt = urljoin(current, loc)
                    chain.append((current, e.code, nxt))
                    if not follow:
                        return {
                            "url": url, "final_url": nxt, "status": e.code,
                            "headers": dict(e.headers), "body": b"",
                            "chain": chain, "error": "",
                        }
                    current = nxt
                    break
                if e.code == 429 or e.code >= 500:
                    if attempt < RETRIES - 1:
                        time.sleep(2 ** attempt * 2)
                        continue
                return {
                    "url": url, "final_url": current, "status": e.code,
                    "headers": dict(e.headers), "body": b"", "chain": chain,
                    "error": "",
                }
            except Exception as e:  # noqa: BLE001 - network, DNS, timeout
                if attempt < RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {
                    "url": url, "final_url": current, "status": 0,
                    "headers": {}, "body": b"", "chain": chain, "error": str(e),
                }
        else:
            break
    return {"url": url, "final_url": current, "status": 0, "headers": {},
            "body": b"", "chain": chain, "error": "redirect loop"}


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

class PageParser(HTMLParser):
    """Collect the SEO-relevant head tags, links and visible text.

    Uses html.parser for the same reason scripts/verify_html.py does: bs4 and
    lxml are not installed and this repo has no dependency install step.
    """

    SKIP_TEXT = {"script", "style", "svg", "noscript", "head", "title"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonical = ""
        self.robots = ""
        self.title = ""
        self.description = ""
        self.og_url = ""
        self.og_title = ""
        self.h1: list[str] = []
        self.links: list[str] = []
        self.jsonld: list[str] = []
        self.words = 0
        self._stack: list[str] = []
        self._grab = None
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        self._stack.append(tag)
        if tag == "link":
            rel = a.get("rel", "").lower()
            if "canonical" in rel.split():
                self.canonical = a.get("href", "").strip()
        elif tag == "meta":
            name = a.get("name", "").lower()
            prop = a.get("property", "").lower()
            content = a.get("content", "").strip()
            if name == "robots":
                self.robots = content
            elif name == "description":
                self.description = content
            elif prop == "og:url":
                self.og_url = content
            elif prop == "og:title":
                self.og_title = content
        elif tag == "a":
            href = a.get("href", "").strip()
            if href:
                self.links.append(href)
        elif tag == "title":
            self._grab, self._buf = "title", []
        elif tag == "h1":
            self._grab, self._buf = "h1", []
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._grab, self._buf = "jsonld", []

    def handle_endtag(self, tag):
        if self._grab == "title" and tag == "title":
            self.title = " ".join("".join(self._buf).split())
            self._grab = None
        elif self._grab == "h1" and tag == "h1":
            self.h1.append(" ".join("".join(self._buf).split()))
            self._grab = None
        elif self._grab == "jsonld" and tag == "script":
            self.jsonld.append("".join(self._buf))
            self._grab = None
        while self._stack and self._stack.pop() != tag:
            pass

    def handle_data(self, data):
        if self._grab:
            self._buf.append(data)
            return
        if any(t in self.SKIP_TEXT for t in self._stack):
            return
        self.words += len(data.split())


def parse(body: bytes) -> PageParser:
    p = PageParser()
    try:
        p.feed(body.decode("utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 - a malformed page must not abort the crawl
        pass
    return p


def norm(url: str) -> str:
    """Absolute, scheme/host-normalised, fragment stripped."""
    s = urlsplit(url)
    if not s.scheme:
        return url
    return urlunsplit((s.scheme, s.netloc, s.path, s.query, ""))


def internal(url: str) -> bool:
    return urlsplit(url).netloc in ("economicsacademy.co.uk", "www.economicsacademy.co.uk")


# --------------------------------------------------------------------------- #
# Passes
# --------------------------------------------------------------------------- #

def link_crawl(seeds: list[str], limit: int | None) -> tuple[dict, dict]:
    """BFS over static HTML links only (no JS execution)."""
    seen: dict[str, dict] = {}
    inbound: dict[str, int] = defaultdict(int)
    queue = list(seeds)
    while queue:
        if limit and len(seen) >= limit:
            break
        url = queue.pop(0)
        url = norm(url)
        if url in seen or not internal(url):
            continue
        if ASSET_RE.search(urlsplit(url).path) or urlsplit(url).path.lower().endswith(".pdf"):
            continue
        r = fetch(url, follow=False)
        seen[url] = r
        if r["status"] == 200 and r["body"]:
            p = parse(r["body"])
            r["parsed"] = p
            for href in p.links:
                if href.startswith(("mailto:", "tel:", "javascript:", "#", "data:")):
                    continue
                nxt = norm(urljoin(url, href))
                if not internal(nxt):
                    continue
                inbound[nxt] += 1
                path = urlsplit(nxt).path
                if ASSET_RE.search(path) or path.lower().endswith(".pdf"):
                    continue
                if nxt not in seen:
                    queue.append(nxt)
        print(f"  [crawl {len(seen):>4}] {r['status']} {url}", file=sys.stderr, flush=True)
    return seen, dict(inbound)


VARIANT_SUFFIXES = ("dir", "dir_index", "html", "extensionless", "http", "www")


def variants_for(page_path: str) -> dict[str, str]:
    """The URL variants worth probing for one repo path."""
    if page_path == "index.html":
        base = "/"
        return {"dir": f"{SITE}/", "dir_index": f"{SITE}/index.html",
                "http": "http://economicsacademy.co.uk/",
                "www": "https://www.economicsacademy.co.uk/"}
    if page_path.endswith("/index.html"):
        d = "/" + page_path[: -len("index.html")]
        return {
            "dir": f"{SITE}{d}",
            "dir_index": f"{SITE}{d}index.html",
            "extensionless": f"{SITE}{d.rstrip('/')}",
            "http": f"http://economicsacademy.co.uk{d}",
            "www": f"https://www.economicsacademy.co.uk{d}",
        }
    p = "/" + page_path
    return {
        "html": f"{SITE}{p}",
        "extensionless": f"{SITE}{p[:-len('.html')]}",
        "dir_index": f"{SITE}{p[:-len('.html')]}/index.html",
        "http": f"http://economicsacademy.co.uk{p}",
        "www": f"https://www.economicsacademy.co.uk{p}",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="seo/01-crawl.csv")
    ap.add_argument("--variants-out", default="seo/01-variants.csv")
    ap.add_argument("--json-out", default="seo/01-crawl.json")
    ap.add_argument("--pdfs-out", default="seo/01-pdfs.csv")
    ap.add_argument("--no-variants", action="store_true")
    ap.add_argument("--no-pdfs", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    inv = build_inventory()
    pages = inv["indexable"] + inv["deliberate_noindex"]
    inventory_urls = [url_for(p) for p in sorted(pages)]

    print(f"== pass 1: link crawl from {SITE}/", file=sys.stderr, flush=True)
    crawled, inbound = link_crawl([f"{SITE}/"], args.limit)

    print(f"== pass 2: inventory fetch ({len(inventory_urls)} URLs)", file=sys.stderr, flush=True)
    todo = [u for u in inventory_urls if u not in crawled]
    if args.limit:
        todo = todo[: args.limit]
    for i, u in enumerate(todo, 1):
        r = fetch(u, follow=False)
        if r["status"] == 200 and r["body"]:
            r["parsed"] = parse(r["body"])
        crawled[u] = r
        print(f"  [inv {i:>4}/{len(todo)}] {r['status']} {u}", file=sys.stderr, flush=True)

    # ------------------------------------------------------------------ rows
    rows = []
    reached_by_link_crawl = set(crawled) - set(todo)
    for url, r in sorted(crawled.items()):
        p = r.get("parsed")
        chain = " -> ".join(f"{c[1]}:{c[2]}" for c in r["chain"])
        rows.append({
            "url": url,
            "status": r["status"],
            "redirect_chain": chain,
            "final_url": r["final_url"],
            "canonical": p.canonical if p else "",
            "canonical_is_self": (p.canonical == url) if p and p.canonical else "",
            "meta_robots": p.robots if p else "",
            "title": p.title if p else "",
            "title_len": len(p.title) if p else 0,
            "description": p.description if p else "",
            "description_len": len(p.description) if p else 0,
            "og_url": p.og_url if p else "",
            "og_title": p.og_title if p else "",
            "h1_count": len(p.h1) if p else 0,
            "h1": " | ".join(p.h1) if p else "",
            "word_count": p.words if p else 0,
            "outbound_links": len(p.links) if p else 0,
            "inbound_links": inbound.get(url, 0),
            "jsonld_blocks": len(p.jsonld) if p else 0,
            "found_by_link_crawl": url in reached_by_link_crawl,
            "error": r["error"],
        })

    out = REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)", file=sys.stderr, flush=True)

    # --------------------------------------------------------------- variants
    vrows = []
    if not args.no_variants:
        targets = pages[: args.limit] if args.limit else pages
        print(f"== pass 3: variant probe ({len(targets)} pages)", file=sys.stderr, flush=True)
        for i, page in enumerate(sorted(targets), 1):
            vs = variants_for(page)
            row = {"page": page, "canonical_url": url_for(page)}
            for kind in VARIANT_SUFFIXES:
                u = vs.get(kind)
                if not u:
                    row[f"{kind}_url"] = ""
                    row[f"{kind}_status"] = ""
                    continue
                r = fetch(u, method="HEAD", follow=False)
                if r["status"] == 405 or r["status"] == 0:
                    r = fetch(u, follow=False)
                row[f"{kind}_url"] = u
                row[f"{kind}_status"] = r["status"]
                if r["chain"]:
                    row[f"{kind}_status"] = f"{r['status']}->{r['chain'][-1][2]}"
            vrows.append(row)
            print(f"  [var {i:>4}/{len(targets)}] {page}", file=sys.stderr, flush=True)

        vout = REPO / args.variants_out
        with vout.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(vrows[0].keys()))
            w.writeheader()
            w.writerows(vrows)
        print(f"wrote {vout} ({len(vrows)} rows)", file=sys.stderr, flush=True)

    # ------------------------------------------------------------------- PDFs
    # Phase 4 puts these in a sitemap, and a sitemap may only contain URLs that
    # return 200, so every one is checked rather than sampled.
    prows = []
    if not args.no_pdfs:
        pdfs = [p for p in inv["pdf_paths"]]
        if args.limit:
            pdfs = pdfs[: args.limit]
        print(f"== pass 4: PDF status ({len(pdfs)} files)", file=sys.stderr, flush=True)
        for i, p in enumerate(sorted(pdfs), 1):
            u = f"{SITE}/{p}"
            r = fetch(u, method="HEAD", follow=False)
            if r["status"] in (0, 405):
                r = fetch(u, follow=False)
            prows.append({
                "path": p, "url": u, "status": r["status"],
                "content_type": r["headers"].get("Content-Type", ""),
                "content_length": r["headers"].get("Content-Length", ""),
                "error": r["error"],
            })
            print(f"  [pdf {i:>4}/{len(pdfs)}] {r['status']} {p}",
                  file=sys.stderr, flush=True)
        pout = REPO / args.pdfs_out
        with pout.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(prows[0].keys()))
            w.writeheader()
            w.writerows(prows)
        print(f"wrote {pout} ({len(prows)} rows)", file=sys.stderr, flush=True)

    jout = REPO / args.json_out
    jout.write_text(json.dumps({
        "crawl": rows,
        "variants": vrows,
        "pdfs": prows,
        "link_crawl_reached": sorted(reached_by_link_crawl),
        "inventory_only": sorted(todo),
        "inbound": inbound,
    }, indent=2), encoding="utf-8")
    print(f"wrote {jout}", file=sys.stderr, flush=True)

    # ---------------------------------------------------------------- summary
    print("\n== summary ==", file=sys.stderr, flush=True)
    print(f"URLs fetched            : {len(rows)}", file=sys.stderr, flush=True)
    print(f"reached by link crawl   : {len(reached_by_link_crawl)}", file=sys.stderr, flush=True)
    print(f"inventory-only          : {len(todo)}", file=sys.stderr, flush=True)
    c = Counter(r["status"] for r in rows)
    for k, v in sorted(c.items()):
        print(f"  status {k:<4}          : {v}", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
