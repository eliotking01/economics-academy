#!/usr/bin/env python3
"""Ten assertions over two copies of this site. Wave 2 Phase 0.

    python3 scripts/compare_trees.py OLD NEW [options]

WHAT THIS IS FOR
----------------
Wave 2 moves 190 hand-written pages onto a shared `page_shell.py`. The rule
that makes that safe is in DO-NOT-BREAK.md: **migration is byte-identical,
improvements come after**. This script is what turns that rule from an
intention into a gate. A page family does not migrate until all ten assertions
pass for every page in it.

OLD and NEW are two directory trees, each a whole copy of the repo - typically
`main` in a `git worktree` and a scratch tree the new generator has written
into. Nothing here writes to either tree.

THE TEN ASSERTIONS (PH06-html-architecture.md section 3, Phase 0)
-----------------------------------------------------------------
  1  URL set identical         pages, PDFs and every other published asset
  2  Visible text zero-diff    per file, not in aggregate
  3  LaTeX spans byte-exact    2 collapses whitespace; this does not
  4  Markup integrity          no element type may drop, no href/src may vanish
  5  <head> field equality     unless allowlisted with a written reason
  6  JSON-LD semantic equality key order irrelevant, list order significant
  7  Internal links preserved  old subset of new, 0 broken, at most 2 orphans
  8  Non-migrated bytes equal  everything outside --family, byte for byte
  9  Idempotence               a second build must be byte-identical (--twice)
 10  Existing verifiers pass   run NEW's own suite, in NEW

Each assertion exists because the one before it is blind to something:

  * 2 is blind to a stripped <a>, which changes no text at all - hence 4.
    That is the failure mode CLAUDE.md records: "scripted paragraph rebuilds
    have silently destroyed <a> tags here before".
  * 2 collapses whitespace, which would hide a change inside a formula -
    hence 3.
  * 4 counts tags, so it cannot see a <head> field whose *value* changed -
    hence 5 and 6.
  * 5 and 6 look only at pages that exist in both trees - hence 1.
  * All of the above look only at HTML - hence 8, which proves the build is a
    no-op everywhere it is not wanted.

WHY IT READS EACH TREE'S OWN _config.yml
----------------------------------------
`exclude` is the only thing keeping working files off the live site, and it
REPLACES Jekyll's defaults rather than adding to them. A build step means new
source directories in the repo, and this repo publishes by default - so
"notes-data/ published by accident" is a named risk in PH06's own risk table.
Reading each tree's own list is what makes assertion 1 catch it: a new source
directory that was not excluded shows up as added URLs. Excluding it in the
same commit makes assertion 1 pass, which is exactly the intended behaviour.

The parser is copied from `build_sitemap.excludes()` rather than the list being
restated, per DO-NOT-BREAK: "copy that pattern rather than adding skip lists".

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
  * No globs in the allowlist. A pattern would let one entry excuse a family,
    and the point of assertion 5 is that an empty allowlist means nothing may
    change. Eighteen pages with an og:description exception are eighteen
    entries, each with its own reason.
  * No writes, to either tree, ever.
  * No network, unless --prettier is passed, which nothing in CI does.

Standard library only. It lives in `scripts/` from 2026-08-13, per PH06
section 3, now that every family has migrated.

IT IS NOT A WORKFLOW STEP, AND THAT WAS MEASURED RATHER THAN ASSUMED.
PROGRESS.md carried "move it into scripts/ AND add it to the workflow" as one
task. The first half is done; the second does not work, for a reason that is
structural rather than fixable by configuration:

**Assertion 8 fails on any commit that changes any file** unless `--family`
names it, because that is precisely its job - "everything outside the
migrating family is byte-identical". Run with no `--family` over HEAD~1 ->
HEAD it flags every file the commit touched, including a docs-only commit.
Measured on 2026-08-13: assertions 1-7 and 10 passed, 8 failed on 2 changed
files, 9 skipped for want of a --twice tree. **A blanket step would be red on
every commit, and a check that is always red protects nothing** - the same
argument that kept verify_liquid.py out of CI until PH00-011 was fixed.

What IS in the workflow is `scripts/test_compare_trees.py`, which needs no
second tree: 39 cases that break each assertion on purpose. DO-NOT-BREAK says
the suite "is what makes it evidence", and it had silently rotted to 31 of 32
before anyone ran it deliberately. That is the failure a CI step can catch.

Making the comparison itself a per-commit gate needs a declaration mechanism
for assertions 1, 3, 5, 6 and 7 - the `Text-Change:`/`Markup-Change:` trailer
pattern, extended - which is a design decision, not a configuration one. It
is written up in PROGRESS.md as a decision for Eliot rather than being
invented here.
"""

from __future__ import annotations

import argparse
import collections
import difflib
import json
import os
import pathlib
import re
import subprocess
import sys
import unicodedata

HARNESS = pathlib.Path(__file__).resolve().parent
# MOVED to scripts/ on 2026-08-13, per PH06 section 3 - "the harness lives in
# _audit/ during the audit and moves to scripts/ when the first family
# migrates, so it becomes a permanent verifier rather than a one-off". All the
# families have migrated.
#
# The comment this replaces said the new value would be `parents[1]`. It is
# `parents[0]`: HARNESS is the DIRECTORY holding this file, so from
# docs/audit/scripts/harness it was parents[3] and from scripts/ it is the
# parent itself. Off by one, and the guard below is what would have caught it.
REPO = HARNESS.parents[0]
if not (REPO / "scripts" / "build_sitemap.py").exists():  # pragma: no cover
    raise SystemExit(
        f"cannot find the repo root from {HARNESS}; expected "
        f"{REPO / 'scripts' / 'build_sitemap.py'} to exist. If this script has "
        f"moved, fix REPO."
    )

# verify_text_integrity.TextExtractor is assertion 2's definition of visible
# text, and it is reused rather than reimplemented so that the harness and the
# workflow step cannot drift apart on what counts as a word.
sys.path.insert(0, str(REPO / "scripts"))
import build_sitemap  # noqa: E402
import verify_text_integrity  # noqa: E402

SITE = "https://economicsacademy.co.uk"

# Not part of either tree's published surface, and not comparable: .git holds
# two different histories, __pycache__ is a build artefact of whichever Python
# ran last, and .DS_Store is the Finder.
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}
# ".git" is in BOTH lists on purpose. In a linked `git worktree` - which is how
# both sides of this comparison are normally produced - `.git` is a FILE
# holding a gitdir pointer, not a directory. That difference is what made
# asset_census.py report 0 of everything inside a worktree instead of failing
# (PROGRESS.md, "Three counts checked before Wave 2"), and it made assertion 8
# fail on its first run here for the same reason.
SKIP_NAMES = {".DS_Store", ".git"}

# Fetched at runtime by inject-templates.js. Served, but no URL anyone lands
# on, so they are compared as assets rather than as pages - and their visible
# text still goes through assertion 2, because every nav label on all 463 pages
# comes from them.
RUNTIME_PARTIALS = {"templates/header.html", "templates/footer.html"}


# --------------------------------------------------------------------------
# Enumeration
# --------------------------------------------------------------------------

def all_files(root: pathlib.Path) -> list[str]:
    """Every file in the tree, repo-relative, sorted. Assertions 8 and 9."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        base = pathlib.Path(dirpath)
        for name in sorted(filenames):
            if name in SKIP_NAMES:
                continue
            out.append((base / name).relative_to(root).as_posix())
    return sorted(out)


def excludes_of(root: pathlib.Path) -> list[str]:
    """This tree's own _config.yml exclude list.

    Same parser as build_sitemap.excludes(), taking a root rather than
    assuming the repo it lives in - the whole point here is to compare two
    trees that may disagree about what is published.
    """
    cfg = root / "_config.yml"
    if not cfg.exists():
        return []
    out, inside = [], False
    for line in cfg.read_text(encoding="utf-8").splitlines():
        if re.match(r"^exclude:\s*$", line):
            inside = True
            continue
        if inside:
            if re.match(r"^\S", line):
                break
            m = re.match(r"^\s+-\s+(\S+)", line)
            if m:
                out.append(m.group(1))
    return out


def published_of(root: pathlib.Path) -> list[str]:
    """Every file GitHub Pages would serve from this tree.

    build_sitemap.published() applies the exclude list and Jekyll's underscore
    rule. Jekyll also skips any path segment beginning with a dot, which
    verify_published_surface.py models and build_sitemap does not need to.
    """
    ex = excludes_of(root)
    return [
        f for f in all_files(root)
        if build_sitemap.published(f, ex)
        and not any(seg.startswith(".") for seg in f.split("/"))
    ]


def url_of(path: str) -> str:
    """Canonical URL form: the trailing-slash directory, never /index.html."""
    if path == "index.html":
        return f"{SITE}/"
    if path.endswith("/index.html"):
        return f"{SITE}/{path[: -len('index.html')]}"
    return f"{SITE}/{path}"


def url_variants(path: str) -> set[str]:
    """Both root-absolute forms a page can be requested at."""
    out = {"/" + path}
    if path == "index.html":
        out.add("/")
    elif path.endswith("/index.html"):
        out.add("/" + path[: -len("index.html")])
    return out


def classify(published: list[str]) -> dict[str, set[str]]:
    pages, pdfs, assets = set(), set(), set()
    for f in published:
        if f.endswith(".html") and f not in RUNTIME_PARTIALS:
            pages.add(url_of(f))
        elif f.lower().endswith(".pdf"):
            pdfs.add(f"{SITE}/{f}")
        else:
            assets.add(f"{SITE}/{f}")
    return {"pages": pages, "PDFs": pdfs, "assets": assets}


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------

TAG = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)\b")
REF = re.compile(r'(?:href|src)="([^"]+)"')
CLASS_ATTR = re.compile(r'class="([^"]*)"')
ANCHOR = re.compile(r"<a\b[^>]*?\shref=\"([^\"]+)\"", re.I | re.S)
LATEX = re.compile(r"\\\((.*?)\\\)|\\\[(.*?)\\\]", re.S)
LDJSON = re.compile(
    r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', re.S | re.I
)
HEAD_BLOCK = re.compile(r"<head\b[^>]*>(.*?)</head>", re.S | re.I)
HTML_TAG = re.compile(r"<html\b([^>]*)>", re.I)
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
META = re.compile(r"<meta\b([^>]*?)/?>", re.I)
LINK = re.compile(r"<link\b([^>]*?)/?>", re.I)
ATTR = re.compile(r'([\w:.-]+)\s*=\s*"([^"]*)"')

# Classes counted individually by assertion 4. The first two are DO-NOT-BREAK's
# load-bearing board differentiation: P5 measured stripping them as raising
# Edexcel/AQA page similarity from 6 pairs >=0.80 to 26, and a template
# migration is exactly the operation that would helpfully factor them out.
# Neither changes any visible text when it moves into a shared layout, so
# assertion 2 would not see it. This does.
WATCHED_CLASSES = (
    "spec-alert",
    "notes-cta",
    "key-definition",
    "diagram-figure",
    "formula-box",
    "worked-example",
    "exam-tip",
    "concept-table",
    "calculation-table",
    "breadcrumb",
)


def visible_text(source: str) -> str:
    return verify_text_integrity.extract(source)


def latex_spans(source: str) -> list[str]:
    """Every \\( ... \\) and \\[ ... \\] span, whitespace intact.

    Assertion 2 collapses whitespace, so a change inside a formula could
    survive it. `$...$` is deliberately not matched: inlineMath still lists it
    (PH08-039), but currency figures would make it pure noise.
    """
    out = []
    for m in LATEX.finditer(source):
        out.append(m.group(1) if m.group(1) is not None else m.group(2))
    return out


def markup_profile(source: str) -> tuple[collections.Counter, collections.Counter]:
    counts = collections.Counter(TAG.findall(source))
    classes = collections.Counter()
    for m in CLASS_ATTR.finditer(source):
        for cls in m.group(1).split():
            classes[cls] += 1
    for cls in WATCHED_CLASSES:
        counts[f"class:{cls}"] = classes.get(cls, 0)
    return counts, collections.Counter(REF.findall(source))


def head_fields(source: str) -> dict[str, list[str]]:
    """The <head> fields assertion 5 holds fixed, in document order.

    Values are lists rather than strings so that a page which writes a field
    twice - PH06-029 found 18 that disagree with themselves - is compared as
    the pair it actually is, instead of silently taking the first.
    """
    fields: dict[str, list[str]] = collections.defaultdict(list)

    m = HTML_TAG.search(source)
    if m:
        for k, v in ATTR.findall(m.group(1)):
            if k.lower() == "lang":
                fields["lang"].append(v)

    head = HEAD_BLOCK.search(source)
    block = head.group(1) if head else source

    for t in TITLE.findall(block):
        fields["title"].append(t.strip())

    for raw in META.findall(block):
        a = {k.lower(): v for k, v in ATTR.findall(raw)}
        key = a.get("name") or a.get("property")
        if not key:
            continue
        key = key.lower()
        if key in ("description", "robots") or key.startswith(("og:", "twitter:")):
            fields[key if ":" in key else f"meta:{key}"].append(a.get("content", ""))

    for raw in LINK.findall(block):
        a = {k.lower(): v for k, v in ATTR.findall(raw)}
        if a.get("rel", "").lower() == "canonical":
            fields["canonical"].append(a.get("href", ""))

    return dict(fields)


def jsonld_blocks(source: str) -> tuple[list[str], list[str]]:
    """Normalised JSON-LD blocks, plus any that would not parse.

    Keys are sorted, so re-indentation and key reordering are invisible. List
    order is kept, because `itemListElement` order is the breadcrumb.
    """
    blocks, errors = [], []
    for m in LDJSON.finditer(source):
        raw = m.group(1)
        try:
            blocks.append(
                json.dumps(json.loads(raw), sort_keys=True,
                           ensure_ascii=False, separators=(",", ":"))
            )
        except (ValueError, TypeError) as exc:
            errors.append(str(exc))
            blocks.append(f"<<unparseable>> {exc}")
    return blocks, errors


def resolve(href: str, from_path: str) -> str | None:
    """One href as a root-absolute site path, or None if it leaves the site."""
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:")):
        return None
    href = href.split("#")[0].split("?")[0]
    if not href:
        return None
    if not href.startswith("/"):
        href = os.path.normpath(
            os.path.join("/" + os.path.dirname(from_path), href)
        ).replace(os.sep, "/")
    return href


def internal_links(source: str, path: str) -> set[str]:
    out = set()
    for href in ANCHOR.findall(source):
        target = resolve(href, path)
        if target:
            out.add(target)
    return out


# --------------------------------------------------------------------------
# Result plumbing
# --------------------------------------------------------------------------

class Result:
    def __init__(self, number: int, name: str):
        self.number = number
        self.name = name
        self.status = "PASS"
        self.summary = ""
        self.details: list[str] = []

    def fail(self, line: str) -> None:
        self.status = "FAIL"
        self.details.append(line)

    def capped(self, n: int, cap: int, line: str) -> None:
        """The nth failure of this assertion. Verdict now; detail only if n <= cap.

        THE VERDICT MUST NOT DEPEND ON THE DISPLAY CAP, and for six of the ten
        assertions it used to. Each wrote

            bad += 1
            if bad <= cfg.max_report:
                r.fail(...)

        so the DETAIL LINE was what set the status. At `--max-report 0` they
        recorded nothing and printed PASS - with the differing count sitting
        in the summary directly underneath the word PASS. Found on 2026-08-13
        running assertion 6 over a real 179-file change, which reported PASS
        and "179 files differ" together.

        Assertions 2 and 8 escaped only by accident: each already had an
        "... and N more" line that fires unconditionally. Those lines stay,
        because they carry the residual count, but they are no longer what
        makes those two correct.
        """
        self.status = "FAIL"
        if n <= cap:
            self.details.append(line)

    def skip(self, why: str) -> None:
        self.status = "SKIP"
        self.summary = why

    def note(self, line: str) -> None:
        self.details.append(line)


class Tree:
    """One side of the comparison, with its files read once."""

    def __init__(self, root: pathlib.Path):
        self.root = root.resolve()
        self.files = all_files(self.root)
        self.fileset = set(self.files)
        self.published = published_of(self.root)
        self.excludes = excludes_of(self.root)
        self._text: dict[str, str] = {}

    def html(self) -> list[str]:
        return [f for f in self.published if f.endswith(".html")]

    def read(self, rel: str) -> str:
        if rel not in self._text:
            self._text[rel] = (self.root / rel).read_text(
                encoding="utf-8", errors="replace"
            )
        return self._text[rel]

    def read_bytes(self, rel: str) -> bytes:
        return (self.root / rel).read_bytes()


# --------------------------------------------------------------------------
# The ten assertions
# --------------------------------------------------------------------------

def a1_urls(old: Tree, new: Tree, cfg) -> Result:
    r = Result(1, "URL set identical")
    if old.excludes != new.excludes:
        r.note("_config.yml exclude lists differ between the trees:")
        for line in difflib.unified_diff(old.excludes, new.excludes,
                                         "OLD", "NEW", lineterm="", n=0):
            r.note(f"    {line}")
    o, n = classify(old.published), classify(new.published)
    total = 0
    for kind in ("pages", "PDFs", "assets"):
        total += len(o[kind])
        gone = sorted(o[kind] - n[kind])
        added = sorted(n[kind] - o[kind])
        if gone or added:
            r.fail(f"{kind}: {len(gone)} removed, {len(added)} added")
            for u in gone[: cfg.max_report]:
                r.note(f"    REMOVED {u}")
            for u in added[: cfg.max_report]:
                r.note(f"    ADDED   {u}")
    r.summary = (f"{len(o['pages'])} pages, {len(o['PDFs'])} PDFs, "
                 f"{len(o['assets'])} assets")
    return r


def a2_text(old: Tree, new: Tree, cfg, shared: list[str]) -> Result:
    r = Result(2, "Visible text zero-diff, per file")
    differing = 0
    nfc_only = 0
    for path in shared:
        a, b = visible_text(old.read(path)), visible_text(new.read(path))
        if a == b:
            continue
        if unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b):
            # Renders identically; a real change all the same, so it is said
            # out loud rather than passed silently.
            nfc_only += 1
            r.note(f"    NFC-only difference: {path}")
            continue
        differing += 1
        r.capped(differing, cfg.max_report, f"{path}")
        if differing <= cfg.max_report:
            for line in list(difflib.unified_diff(
                    a.split(" "), b.split(" "), lineterm="", n=4))[:20]:
                r.note(f"      {line}")
    if differing > cfg.max_report:
        r.fail(f"... and {differing - cfg.max_report} more files")
    r.summary = f"{len(shared)} files compared, {differing} differ"
    if nfc_only:
        r.summary += f", {nfc_only} differ by Unicode normalisation only"
    return r


def a3_latex(old: Tree, new: Tree, cfg, shared: list[str]) -> Result:
    r = Result(3, "LaTeX spans byte-exact")
    total = 0
    bad = 0
    for path in shared:
        a, b = latex_spans(old.read(path)), latex_spans(new.read(path))
        total += len(a)
        if a != b:
            bad += 1
            r.capped(bad, cfg.max_report,
                     f"{path}: {len(a)} spans -> {len(b)}")
            if bad <= cfg.max_report:
                for line in list(difflib.unified_diff(
                        a, b, lineterm="", n=1))[:12]:
                    r.note(f"      {line}")
    r.summary = f"{total} spans across {len(shared)} files, {bad} files differ"
    return r


def a4_markup(old: Tree, new: Tree, cfg, shared: list[str]) -> Result:
    r = Result(4, "Markup integrity")
    losses = 0
    gains = 0
    for path in shared:
        (oc, orefs) = markup_profile(old.read(path))
        (nc, nrefs) = markup_profile(new.read(path))
        for tag in sorted(set(oc) | set(nc)):
            was, now = oc.get(tag, 0), nc.get(tag, 0)
            if now < was:
                losses += 1
                r.capped(losses, cfg.max_report,
                         f"{path}: <{tag}> {was} -> {now}")
            elif now > was:
                gains += 1
        for ref in sorted(orefs):
            if orefs[ref] > nrefs.get(ref, 0):
                losses += 1
                r.capped(losses, cfg.max_report, f"{path}: lost {ref!r}")
    r.summary = (f"{losses} losses, {gains} additions "
                 f"(additions are not failures)")
    return r


def _flat(values: list[str]) -> list[str]:
    return [" ".join(v.split()) for v in values]


def a5_head(old: Tree, new: Tree, cfg, shared: list[str], allow: dict) -> Result:
    r = Result(5, "<head> field equality")
    bad = 0
    ws_only = 0
    used = set()
    for path in shared:
        a, b = head_fields(old.read(path)), head_fields(new.read(path))
        for key in sorted(set(a) | set(b)):
            if a.get(key, []) == b.get(key, []):
                continue
            # A <title> Prettier wrapped across two lines and the same title on
            # one line are the same title: HTML collapses whitespace inside a
            # text node, and so does every crawler. Comparing the raw bytes
            # here compares formatting rather than the field. Said out loud
            # rather than passed silently, because a check that quietly
            # forgives things stops meaning anything.
            if _flat(a.get(key, [])) == _flat(b.get(key, [])):
                ws_only += 1
                r.note(f"    whitespace only: {path} [{key}]")
                continue
            reason = allow.get(path, {}).get(key)
            if reason:
                used.add((path, key))
                r.note(f"    ALLOWED {path} [{key}]: {reason}")
                continue
            bad += 1
            r.capped(bad, cfg.max_report,
                     f"{path} [{key}]: {a.get(key, [])!r} -> "
                     f"{b.get(key, [])!r}")
    declared = {(p, k) for p, fields in allow.items() for k in fields}
    for p, k in sorted(declared - used):
        r.note(f"    declared but unchanged: {p} [{k}]")
    r.summary = f"{len(shared)} files, {bad} undeclared changes"
    if ws_only:
        r.summary += f", {ws_only} differing by whitespace only"
    if declared:
        r.summary += f", {len(declared)} allowlisted"
    return r


def a6_jsonld(old: Tree, new: Tree, cfg, shared: list[str]) -> Result:
    r = Result(6, "JSON-LD semantic equality")
    total = 0
    bad = 0
    unparseable = 0
    for path in shared:
        a, aerr = jsonld_blocks(old.read(path))
        b, berr = jsonld_blocks(new.read(path))
        total += len(a)
        if berr or aerr:
            unparseable += 1
            r.fail(f"{path}: unparseable JSON-LD "
                   f"(OLD {len(aerr)}, NEW {len(berr)})")
            continue
        if a != b:
            bad += 1
            r.capped(bad, cfg.max_report,
                     f"{path}: {len(a)} blocks -> {len(b)}")
            if bad <= cfg.max_report:
                for line in list(difflib.unified_diff(
                        a, b, lineterm="", n=0))[:8]:
                    r.note(f"      {line[:300]}")
    r.summary = f"{total} blocks across {len(shared)} files, {bad} files differ"
    if unparseable:
        r.summary += f", {unparseable} unparseable"
    return r


def a7_links(old: Tree, new: Tree, cfg, shared: list[str]) -> Result:
    r = Result(7, "Internal links preserved or improved")
    lost = 0
    added = 0
    for path in shared:
        a = internal_links(old.read(path), path)
        b = internal_links(new.read(path), path)
        missing = a - b
        added += len(b - a)
        if missing:
            lost += len(missing)
            for t in sorted(missing):
                r.capped(lost, cfg.max_report, f"{path}: lost link to {t}")

    resolvable: set[str] = set()
    for f in new.published:
        if f.endswith(".html"):
            resolvable |= url_variants(f)
        else:
            resolvable.add("/" + f)

    pages = [f for f in new.published
             if f.endswith(".html") and f not in RUNTIME_PARTIALS]
    inbound: collections.Counter = collections.Counter()
    broken: collections.Counter = collections.Counter()
    for f in pages:
        for target in internal_links(new.read(f), f):
            inbound[target] += 1
            if target not in resolvable:
                broken[target] += 1
    if broken:
        r.fail(f"NEW has {sum(broken.values())} broken internal targets")
        for t, n in broken.most_common(cfg.max_report):
            r.note(f"      {n:4d}  {t}")

    orphans = [f for f in pages
               if not any(inbound.get(v, 0) for v in url_variants(f))]
    if len(orphans) > cfg.max_orphans:
        r.fail(f"NEW has {len(orphans)} orphan pages, limit {cfg.max_orphans}")
        for f in orphans[: cfg.max_report]:
            r.note(f"      {f}")

    r.summary = (f"{lost} links lost, {added} added; NEW: "
                 f"{sum(broken.values())} broken, {len(orphans)} orphans")
    return r


def a8_bytes(old: Tree, new: Tree, cfg) -> Result:
    r = Result(8, "Non-migrated files byte-identical")
    families = tuple(cfg.family)
    outside = [f for f in sorted(old.fileset | new.fileset)
               if not in_family(f, families)]
    bad = 0
    for f in outside:
        if f not in old.fileset:
            bad += 1
            r.capped(bad, cfg.max_report, f"only in NEW: {f}")
            continue
        if f not in new.fileset:
            bad += 1
            r.capped(bad, cfg.max_report, f"only in OLD: {f}")
            continue
        if old.read_bytes(f) != new.read_bytes(f):
            if cfg.prettier and f.endswith(".html") and \
                    prettier(old.root / f) == prettier(new.root / f):
                r.note(f"    identical after Prettier: {f}")
                continue
            bad += 1
            r.capped(bad, cfg.max_report, f"bytes differ: {f}")
    if bad > cfg.max_report:
        r.fail(f"... and {bad - cfg.max_report} more")
    r.summary = (f"{len(outside)} files outside "
                 f"{len(families)} migrating family/families, {bad} differ")
    return r


def a9_idempotent(new: Tree, cfg) -> Result:
    r = Result(9, "Idempotence: a second build is byte-identical")
    if not cfg.twice:
        r.skip("no --twice tree given; assertion NOT run")
        return r
    second = Tree(pathlib.Path(cfg.twice))
    bad = 0
    for f in sorted(new.fileset | second.fileset):
        if f not in new.fileset or f not in second.fileset:
            bad += 1
            r.capped(bad, cfg.max_report, f"present in only one build: {f}")
            continue
        if new.read_bytes(f) != second.read_bytes(f):
            bad += 1
            r.capped(bad, cfg.max_report, f"second build differs: {f}")
    r.summary = f"{len(new.files)} files, {bad} differ between two builds"
    return r


# Run inside NEW, against NEW's own copy of each script - a migration changes
# scripts/ too, so the suite that matters is the one the tree ships. This is
# the workflow's fast suite minus verify_text_integrity and
# verify_markup_integrity, which compare two git REFS rather than two trees;
# assertions 2 and 4 are the tree-shaped equivalents and are stricter, since
# they cover all 465 published HTML files rather than 192.
#
# SEVEN OF THESE FOURTEEN NEED NEW TO BE A GIT TREE, measured rather than
# assumed: verify_icons, verify_image_dimensions, verify_css_load_order,
# verify_seo, verify_liquid, verify_published_surface and build_sitemap all
# enumerate through `git ls-files`, and the last also reads every <lastmod>
# from `git log`. DO-NOT-BREAK records why - every enumeration tool in this
# repo works that way. So assertion 10 requires a git tree and FAILS without
# one. It does not skip: running 7 of 14 and printing a pass is precisely the
# "green for the wrong reason" this harness exists to prevent, and a scratch
# build tree should be a `git worktree` regardless, which is what
# verify_generated.py already does.
#
# build_sitemap.py --check is the one that has bitten repeatedly: it prints
# "nothing written" on BOTH paths, so the pass signal is the exit code, never
# the line.
VERIFIERS = [
    ("scripts/verify_html.py", []),
    ("scripts/verify_links.py", []),
    ("scripts/verify_glossary.py", []),
    ("scripts/verify_past_paper_tags.py", []),
    ("scripts/verify_diagram_geometry.py", []),
    ("scripts/verify_icons.py", []),
    ("scripts/verify_image_dimensions.py", []),
    ("scripts/verify_css_load_order.py", []),
    ("scripts/check_glossary_capitalisation.py", ["--check"]),
    ("scripts/strip_source_attributions.py", []),
    ("scripts/verify_liquid.py", []),
    ("scripts/verify_published_surface.py", []),
    ("scripts/build_sitemap.py", ["--check"]),
    ("seo/tools/verify_seo.py", []),
]


def a10_verifiers(new: Tree, cfg) -> Result:
    r = Result(10, "Existing verifiers still pass, in NEW")
    if cfg.no_verifiers:
        r.skip("--no-verifiers given; assertion NOT run")
        return r
    if not (new.root / ".git").exists():
        r.fail("NEW is not a git tree, and 7 of these 14 verifiers enumerate "
               "through `git ls-files`")
        r.note("    Build into a worktree instead:  git worktree add "
               "--detach <dir> HEAD")
        r.summary = "0/14 verifiers run"
        return r
    ran = passed = 0
    for script, extra in VERIFIERS:
        if not (new.root / script).exists():
            r.fail(f"{script} is missing from NEW")
            continue
        proc = subprocess.run(
            [sys.executable, script, *extra],
            cwd=new.root, capture_output=True, text=True,
        )
        ran += 1
        if proc.returncode == 0:
            passed += 1
        else:
            r.fail(f"{script} {' '.join(extra)} exited {proc.returncode}")
            tail = (proc.stderr or proc.stdout).strip().splitlines()[-6:]
            for line in tail:
                r.note(f"      {line}")
    r.summary = f"{passed}/{ran} verifiers pass"
    return r


# --------------------------------------------------------------------------
# Support
# --------------------------------------------------------------------------

def in_family(path: str, families: tuple[str, ...]) -> bool:
    for f in families:
        if path == f or path.startswith(f):
            return True
    return False


_PRETTIER_CACHE: dict[pathlib.Path, str] = {}


def prettier(path: pathlib.Path) -> str:
    """Prettier 3.9.6's rendering of one file, for --prettier only.

    PH06 section 3 asks for this so that assertion 8 or 9 cannot fail on
    formatting where a generator runs Prettier over its own output. It is off
    by default and never used in CI: it is the one thing here that needs the
    network, and no assertion needs it today. Only files that already differ
    are put through it, so the cost is paid per difference, not per file.
    """
    if path not in _PRETTIER_CACHE:
        proc = subprocess.run(
            ["npx", "prettier@3.9.6", "--parser", "html", str(path)],
            capture_output=True, text=True,
        )
        _PRETTIER_CACHE[path] = proc.stdout if proc.returncode == 0 else f"ERR{path}"
    return _PRETTIER_CACHE[path]


def load_allowlist(path: pathlib.Path) -> dict:
    """{page: {field: reason}} - the only permitted <head> field changes.

    A reason is required, and it is printed on every run. An entry with an
    empty reason is rejected: "identical unless deliberately changed" is only
    a real constraint if the deliberate part is written down.
    """
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    changes = data.get("changes", {})
    for page, fields in changes.items():
        for field, reason in fields.items():
            if not str(reason).strip():
                # Exit 2, not 1. A malformed allowlist is a usage error, the
                # same class argparse uses 2 for, and it must not be
                # mistakable for "an assertion failed" - which is exit 1 and
                # means something entirely different about the site.
                print(
                    f"{path}: {page} [{field}] has no reason. Every entry "
                    f"needs one - that is what makes it an exception rather "
                    f"than an exemption.", file=sys.stderr,
                )
                raise SystemExit(2)
    return changes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("old", help="tree as it is today")
    ap.add_argument("new", help="tree the build produced")
    ap.add_argument("--family", action="append", default=[], metavar="PREFIX",
                    help="path prefix being migrated; assertion 8 exempts it. "
                         "Repeatable. With none given, every file must be "
                         "byte-identical.")
    ap.add_argument("--twice", metavar="DIR",
                    help="a second build of NEW, for assertion 9")
    ap.add_argument("--allowlist", default=str(HARNESS / "intentional-changes.json"),
                    help="allowlist for assertion 5")
    ap.add_argument("--only", metavar="N,N",
                    help="run only these assertions, e.g. --only 2,3,4")
    ap.add_argument("--max-report", type=int, default=20,
                    help="cap the detail lines per assertion (default 20)")
    ap.add_argument("--max-orphans", type=int, default=2,
                    help="orphan pages permitted in NEW (default 2, today's "
                         "value: 461 of 463 are reachable without JavaScript)")
    ap.add_argument("--prettier", action="store_true",
                    help="re-compare differing HTML through Prettier 3.9.6. "
                         "Needs the network. Nothing in CI uses it.")
    ap.add_argument("--no-verifiers", action="store_true",
                    help="skip assertion 10, which runs NEW's own suite")
    cfg = ap.parse_args(argv)

    wanted = ({int(x) for x in cfg.only.split(",")} if cfg.only
              else set(range(1, 11)))

    old = Tree(pathlib.Path(cfg.old))
    new = Tree(pathlib.Path(cfg.new))
    allow = load_allowlist(pathlib.Path(cfg.allowlist))

    shared = sorted(set(old.html()) & set(new.html()))

    print(f"OLD  {old.root}   {len(old.files)} files, "
          f"{len(old.published)} published")
    print(f"NEW  {new.root}   {len(new.files)} files, "
          f"{len(new.published)} published")
    if cfg.family:
        print(f"migrating: {', '.join(cfg.family)}")
    print()

    results = []
    if 1 in wanted:
        results.append(a1_urls(old, new, cfg))
    if 2 in wanted:
        results.append(a2_text(old, new, cfg, shared))
    if 3 in wanted:
        results.append(a3_latex(old, new, cfg, shared))
    if 4 in wanted:
        results.append(a4_markup(old, new, cfg, shared))
    if 5 in wanted:
        results.append(a5_head(old, new, cfg, shared, allow))
    if 6 in wanted:
        results.append(a6_jsonld(old, new, cfg, shared))
    if 7 in wanted:
        results.append(a7_links(old, new, cfg, shared))
    if 8 in wanted:
        results.append(a8_bytes(old, new, cfg))
    if 9 in wanted:
        results.append(a9_idempotent(new, cfg))
    if 10 in wanted:
        results.append(a10_verifiers(new, cfg))

    for r in results:
        print(f"{r.status:4}  {r.number:>2}  {r.name}")
        if r.summary:
            print(f"          {r.summary}")
        for line in r.details[: cfg.max_report * 3]:
            print(f"          {line}")

    failed = [r for r in results if r.status == "FAIL"]
    skipped = [r for r in results if r.status == "SKIP"]

    print()
    sys.stdout.flush()
    if failed:
        print(f"FAIL: {len(failed)} of {len(results)} assertions failed: "
              f"{', '.join(str(r.number) for r in failed)}", file=sys.stderr)
        print("The family does not migrate until all ten pass.", file=sys.stderr)
        return 1
    if skipped:
        # Said loudly on purpose. A skipped assertion is not a passed one, and
        # a suite that reports "all green" while two of ten never ran is how a
        # check comes to protect nothing.
        print(f"{len(results) - len(skipped)} assertions pass, "
              f"{len(skipped)} NOT RUN: "
              f"{', '.join(str(r.number) for r in skipped)}")
        return 0
    print(f"all {len(results)} assertions pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
