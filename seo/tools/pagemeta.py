#!/usr/bin/env python3
"""Shared HTML parsing for the SEO tools.

One parser, used by both the live crawler and the offline audit, so a defect
cannot appear in one and not the other because two regexes disagreed.

html.parser only: bs4 and lxml are not installed here and there is no dependency
install step, matching scripts/verify_html.py and scripts/verify_links.py.

Two things this gets right that a regex does not:

  - Tags split across lines. Prettier wraps <link rel="canonical" ...> and
    <title> over several lines throughout this repo, so any line-oriented grep
    silently misses them.
  - Whitespace. A wrapped <title> contains newlines and runs of spaces that
    HTML collapses; comparing it to og:title without normalising produces 92
    false "mismatches" on this site. Titles are normalised on the way out.
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser

# Text-bearing elements whose contents are not page copy.
SKIP_TEXT = {"script", "style", "svg", "noscript", "head", "title"}


def norm_space(s: str) -> str:
    """Collapse whitespace the way an HTML renderer would."""
    return " ".join(s.split())


class PageParser(HTMLParser):
    """Collect SEO-relevant head tags, links, headings and a word count."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonical = ""
        self.robots = ""
        self.title = ""
        self.description = ""
        self.og_url = ""
        self.og_title = ""
        self.og_description = ""
        self.twitter_title = ""
        self.twitter_description = ""
        self.lang = ""
        self.h1: list[str] = []
        self.headings: list[tuple[str, str]] = []
        self.links: list[str] = []          # href values, verbatim
        self.srcs: list[str] = []
        self.jsonld: list[str] = []
        self.words = 0
        self.text_parts: list[str] = []
        self._stack: list[str] = []
        self._grab: str | None = None
        self._buf: list[str] = []

    # -- tags ------------------------------------------------------------- #
    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        self._stack.append(tag)

        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "link":
            if "canonical" in a.get("rel", "").lower().split():
                self.canonical = a.get("href", "").strip()
        elif tag == "meta":
            name = a.get("name", "").lower()
            prop = a.get("property", "").lower()
            content = a.get("content", "").strip()
            if name == "robots":
                self.robots = content
            elif name == "description":
                self.description = content
            elif name == "twitter:title":
                self.twitter_title = content
            elif name == "twitter:description":
                self.twitter_description = content
            elif prop == "og:url":
                self.og_url = content
            elif prop == "og:title":
                self.og_title = content
            elif prop == "og:description":
                self.og_description = content
        elif tag == "a":
            href = a.get("href", "").strip()
            if href:
                self.links.append(href)
        elif tag == "script":
            # Order matters: a JSON-LD block is a <script> too, and checking src
            # first would swallow every one of them.
            if a.get("type", "").lower() == "application/ld+json":
                self._grab, self._buf = "jsonld", []
            elif a.get("src", "").strip():
                self.srcs.append(a["src"].strip())
        elif tag in ("img", "iframe", "source"):
            src = a.get("src", "").strip()
            if src:
                self.srcs.append(src)
        elif tag == "title":
            self._grab, self._buf = "title", []
        elif tag in ("h1", "h2", "h3"):
            self._grab, self._buf = tag, []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_endtag(self, tag):
        if self._grab == "title" and tag == "title":
            self.title = norm_space("".join(self._buf))
            self._grab = None
        elif self._grab in ("h1", "h2", "h3") and tag == self._grab:
            text = norm_space("".join(self._buf))
            self.headings.append((tag, text))
            if tag == "h1":
                self.h1.append(text)
            self._grab = None
        elif self._grab == "jsonld" and tag == "script":
            self.jsonld.append("".join(self._buf))
            self._grab = None
        while self._stack:
            if self._stack.pop() == tag:
                break

    def handle_data(self, data):
        if self._grab:
            self._buf.append(data)
            return
        if any(t in SKIP_TEXT for t in self._stack):
            return
        parts = data.split()
        if parts:
            self.words += len(parts)
            self.text_parts.extend(parts)

    # -- derived ----------------------------------------------------------- #
    @property
    def text(self) -> str:
        return " ".join(self.text_parts)

    def invalid_jsonld(self) -> list[str]:
        bad = []
        for b in self.jsonld:
            try:
                json.loads(b)
            except Exception as e:  # noqa: BLE001
                bad.append(str(e))
        return bad

    def jsonld_types(self) -> list[str]:
        out = []
        for b in self.jsonld:
            try:
                d = json.loads(b)
            except Exception:  # noqa: BLE001
                continue
            for item in (d if isinstance(d, list) else [d]):
                if isinstance(item, dict) and "@type" in item:
                    t = item["@type"]
                    out.extend(t if isinstance(t, list) else [t])
        return out


def parse_html(source: str | bytes) -> PageParser:
    if isinstance(source, bytes):
        source = source.decode("utf-8", errors="replace")
    p = PageParser()
    try:
        p.feed(source)
        p.close()
    except Exception:  # noqa: BLE001 - a malformed page must not abort a sweep
        pass
    return p


def shingles(text: str, n: int = 8) -> set[str]:
    """Word n-grams, for near-duplicate detection."""
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
