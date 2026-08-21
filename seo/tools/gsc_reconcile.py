#!/usr/bin/env python3
"""Reconcile a Search Console page-indexing export against the published site.

    python3 seo/tools/gsc_reconcile.py seo/gsc-exports/21-08-2026
    python3 seo/tools/gsc_reconcile.py seo/gsc-exports/21-08-2026 \
            --diff seo/gsc-exports/08-08-2026
    python3 seo/tools/gsc_reconcile.py <dir> --list discovered-currently-not-indexed

WHY THIS EXISTS
---------------
Producing seo/11-gsc-index-audit-2026-08-21.md took a session of hand-analysis:
nine CSVs parsed, reconciled against the real published inventory, ghosts split
from real URLs. The part that took longest and mattered most was noticing that
Google's "noindex" verdict on 26 pages **contradicted what the repo contains** -
the tags had been removed three weeks earlier and Google had not been back.

That is a mechanical check, and it should never be hand-work again. The exports
get re-taken every few weeks; this reads them.

Nothing else in the repo does this job. inventory.py builds the page inventory,
audit.py audits on-page defects, verify_seo.py asserts live markup, and
build_sitemap.py builds the sitemaps - none of them has ever read a GSC export.

WHAT IT ASSERTS
---------------
Every published URL lands in exactly ONE bucket, and the buckets sum to the
inventory. If that fails, the export or the inventory has changed shape and the
numbers in any report built on it are not trustworthy. Non-zero exit.

THE FOUR BUCKETS
----------------
    indexed                 Google has it
    <a GSC reason>          Google has judged it and declined
    unjudged                published, in no export at all - a finding, not a gap
    ghost                   in an export, not a URL this site publishes

CONTRADICTIONS
--------------
Google's verdict is only ever as fresh as its last crawl of that URL, and the
page-indexing report lags Search Console's own Crawl stats by days. So the
`Last crawled` column is the most useful field in the export, and every check
below is really the same question: is Google describing the page as it is now?

Standard library only, in keeping with the rest of seo/tools/. Reads only.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import build_sitemap as bs  # noqa: E402  - the single source of "what is published"

# GSC exports the epoch as the "never crawled" value. It is not a date.
NEVER_CRAWLED = "1970-01-01"

# CSV stem -> bucket name. The indexed export is named for its date, so it is
# matched by prefix rather than listed.
INDEXED_PREFIX = "indexed-pages"
INDEXED = "indexed"

# Reasons where Google is behaving correctly and no fix exists or is wanted.
# Printed with the reconciliation so a reader is not left to guess which of the
# numbers are problems. Sourced from seo/11-*.md section 6.
EXPECTED = {
    "alternate-page-with-proper-canonical-tag":
        "a duplicate correctly pointing at its canonical - a success state",
    "page-with-redirect":
        "GitHub Pages' own http->https and www->apex redirects",
    "duplicate-without-user-selected-canonical":
        "PDFs; no canonical can be declared for a PDF on GitHub Pages",
    "not-found-404":
        "URLs that correctly do not exist; never validate this issue",
}


def load_export(d: Path) -> dict[str, dict[str, str]]:
    """{bucket: {url: last_crawled}} for one export directory."""
    if not d.is_dir():
        sys.exit(f"not a directory: {d}")
    out: dict[str, dict[str, str]] = {}
    for f in sorted(d.glob("*.csv")):
        name = INDEXED if f.stem.startswith(INDEXED_PREFIX) else f.stem
        with f.open(newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        if not rows:
            out[name] = {}
            continue
        if "URL" not in rows[0]:
            print(f"  skipped {f.name}: no URL column "
                  f"(has {', '.join(rows[0])})", file=sys.stderr)
            continue
        urls = {r["URL"].strip(): (r.get("Last crawled") or "").strip()
                for r in rows}
        if len(urls) != len(rows):
            print(f"  WARNING {f.name}: {len(rows) - len(urls)} duplicate URL(s)",
                  file=sys.stderr)
        out[name] = urls
    if not out:
        sys.exit(f"no CSVs found in {d}")
    return out


def inventory() -> tuple[dict[str, dict], dict[str, str]]:
    """Every published URL -> {path, sitemap, is_pdf, noindex}, plus git dates.

    Publish status comes from build_sitemap's own excludes()/published(), so
    this cannot drift from what the sitemap generator believes is public.
    """
    ex = bs.excludes()
    inv: dict[str, dict] = {}
    for path in sorted(bs.git_files()):
        if not bs.published(path, ex):
            continue
        if path.lower().endswith(".pdf"):
            inv[f"{bs.SITE}/{path}"] = {"path": path, "pdf": True,
                                        "noindex": False}
            continue
        if not path.endswith(".html") or path in bs.RUNTIME_PARTIALS:
            continue
        text = (REPO / path).read_text(encoding="utf-8", errors="replace")
        inv[bs.url_for(path)] = {"path": path, "pdf": False,
                                 "noindex": bool(bs.NOINDEX_RE.search(text))}

    # Which sitemap each URL is actually listed in, read from the committed XML
    # rather than recomputed - so a stale sitemap shows up as a difference.
    for f in sorted((REPO / "sitemaps").glob("*.xml")):
        for loc in re.findall(r"<loc>(.*?)</loc>",
                              f.read_text(encoding="utf-8")):
            if loc in inv:
                inv[loc]["sitemap"] = f.name
    for rec in inv.values():
        rec.setdefault("sitemap", "not-in-a-sitemap")

    return inv, last_commit_dates()


def last_commit_dates() -> dict[str, str]:
    """path -> YYYY-MM-DD of its most recent commit.

    One `git log` pass over the whole history. Calling `git log` per file is
    correct but takes minutes on this repo; this takes about a second.
    """
    out = subprocess.run(
        ["git", "-C", str(REPO), "log", "--format=@%cs", "--name-only",
         "--no-renames"],
        capture_output=True, text=True, check=True,
    ).stdout
    dates: dict[str, str] = {}
    day = ""
    for line in out.splitlines():
        if line.startswith("@"):
            day = line[1:]
        elif line.strip() and line.strip() not in dates:
            dates[line.strip()] = day          # first sighting = most recent
    return dates


def bucket_of(url: str, exp: dict[str, dict[str, str]]) -> str | None:
    for name, urls in exp.items():
        if url in urls:
            return name
    return None


# ---------------------------------------------------------------- reporting

def h(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def reconcile(inv, exp) -> tuple[dict[str, list[str]], list[str]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for url in sorted(inv):
        buckets[bucket_of(url, exp) or "unjudged"].append(url)
    published = set(inv)
    ghosts = sorted({u for urls in exp.values() for u in urls} - published)
    return buckets, ghosts


def report_reconciliation(inv, buckets, ghosts) -> None:
    h(f"Published inventory  -  {len(inv)} URLs")
    pages = sum(1 for r in inv.values() if not r["pdf"])
    print(f"  {pages} HTML pages, {len(inv) - pages} PDFs")
    print(f"  {sum(1 for r in inv.values() if r['noindex'])} page(s) carry a "
          f"deliberate noindex and are held out of the sitemaps")

    h("Every published URL, in exactly one bucket")
    print(f"  {'bucket':<45}{'URLs':>6}{'HTML':>7}{'PDF':>6}")
    for name in sorted(buckets, key=lambda n: -len(buckets[n])):
        urls = buckets[name]
        html = sum(1 for u in urls if not inv[u]["pdf"])
        print(f"  {name:<45}{len(urls):>6}{html:>7}{len(urls) - html:>6}")
    print(f"  {'TOTAL':<45}{sum(len(v) for v in buckets.values()):>6}")
    for name, why in EXPECTED.items():
        if buckets.get(name):
            print(f"    note: {name} is expected - {why}")

    idx = len(buckets.get(INDEXED, []))
    html_idx = sum(1 for u in buckets.get(INDEXED, []) if not inv[u]["pdf"])
    html_total = sum(1 for r in inv.values() if not r["pdf"])
    pdf_total = len(inv) - html_total
    print(f"\n  indexed: {idx}/{len(inv)} = {pct(idx, len(inv))} of everything")
    print(f"           {html_idx}/{html_total} = {pct(html_idx, html_total)} "
          f"of HTML pages")
    if pdf_total:
        print(f"           {idx - html_idx}/{pdf_total} = "
              f"{pct(idx - html_idx, pdf_total)} of PDFs")


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "n/a"


def report_by_sitemap(inv, buckets) -> None:
    h("Coverage by sitemap")
    names = sorted(buckets, key=lambda n: (n != INDEXED, n))
    table: dict[str, Counter] = defaultdict(Counter)
    for name, urls in buckets.items():
        for u in urls:
            table[inv[u]["sitemap"]][name] += 1

    head = f"  {'sitemap':<26}{'total':>6}"
    for n in names:
        head += f"{abbrev(n):>13}"
    print(head + f"{'indexed':>10}")
    for sm in sorted(table, key=lambda s: -sum(table[s].values())):
        row = table[sm]
        total = sum(row.values())
        line = f"  {sm:<26}{total:>6}"
        for n in names:
            line += f"{row[n]:>13}"
        print(line + f"{pct(row[INDEXED], total):>10}")


def abbrev(name: str) -> str:
    """Column headings short enough to line up. Order-preserving, lossless
    enough to read - the full names are in the bucket table above."""
    return {
        "indexed": "indexed",
        "discovered-currently-not-indexed": "discovered",
        "crawled-currently-not-indexed": "crawled-NI",
        "excluded-by-noindex-tag": "noindex",
        "duplicate-without-user-selected-canonical": "dup-canon",
        "alternate-page-with-proper-canonical-tag": "alternate",
        "not-found-404": "404",
        "page-with-redirect": "redirect",
        "redirect-error": "redir-err",
        "unjudged": "unjudged",
    }.get(name, name[:12])


def report_unjudged(inv, buckets) -> None:
    urls = buckets.get("unjudged", [])
    h(f"Published but in no export at all  -  {len(urls)}")
    if not urls:
        print("  none")
        return
    print("  Google has formed no view. Deliberate-noindex pages belong here;")
    print("  anything else is either very new or has not been discovered.")
    for u in urls:
        rec = inv[u]
        why = ("deliberate noindex" if rec["noindex"]
               else "expected to be discovered")
        print(f"  {u[len(bs.SITE):]:<70} {why}")


def report_ghosts(exp, ghosts) -> None:
    h(f"In an export, not a URL this site publishes  -  {len(ghosts)}")
    if not ghosts:
        print("  none")
        return
    by = defaultdict(list)
    for u in ghosts:
        by[bucket_of(u, exp)].append(u)
    for name in sorted(by, key=lambda n: -len(by[n])):
        print(f"  {name}  ({len(by[name])})")
        for u in by[name]:
            print(f"      {u}")


def report_contradictions(inv, exp, buckets, commits) -> int:
    """Where Google's verdict disagrees with the repo as it stands today."""
    h("Contradictions  -  where GSC and the repo disagree")
    found = 0

    # 1. GSC says noindex; the file carries no robots meta tag.
    phantom_noindex = [u for u in buckets.get("excluded-by-noindex-tag", [])
                       if not inv[u]["noindex"]]
    bad = phantom_noindex
    found += emit(
        bad, "GSC reports a noindex tag that is NOT in the file",
        "The tag was removed after Google's last crawl. Nothing to fix in the "
        "repo - this needs a recrawl. Search Console offers Validate Fix here "
        "and it will pass.", exp, inv)

    # 2. GSC says 404; the file is published and should return 200.
    bad = [u for u in buckets.get("not-found-404", []) if u in inv]
    found += emit(
        bad, "GSC reports 404 for a URL this site DOES publish",
        "Either the page was restored after the crawl, or something is wrong "
        "with the deploy. Check the URL live before doing anything else.",
        exp, inv)

    # 3. Verdict older than the page. The most common finding, and the reason
    #    the Last crawled column matters more than the verdict itself.
    #    Anything already named by check 1 is skipped rather than listed twice -
    #    a phantom noindex IS a stale verdict, and saying so once is enough.
    already = set(phantom_noindex)
    stale, stale_dupes = [], 0
    for name, urls in buckets.items():
        if name in (INDEXED, "unjudged"):
            continue
        for u in urls:
            crawled = exp[name][u]
            if not crawled or crawled == NEVER_CRAWLED:
                continue                      # never crawled: not stale, unseen
            changed = commits.get(inv[u]["path"], "")
            if not (changed and changed > crawled):
                continue
            if u in already:
                stale_dupes += 1
                continue
            stale.append((u, name, crawled, changed))
    if stale:
        found += 1
        print(f"\n  [{len(stale)}] Verdict is OLDER than the page it describes")
        print("      Google is describing a version of the page that no longer")
        print("      exists. Request Indexing on the ones that matter.")
        if stale_dupes:
            print(f"      ({stale_dupes} more are the phantom-noindex pages "
                  f"above, not repeated here.)")
        for u, name, crawled, changed in sorted(stale,
                                                key=lambda r: r[2])[:40]:
            print(f"      {u[len(bs.SITE):]:<62} {abbrev(name):<11} "
                  f"crawled {crawled}  changed {changed}")
        if len(stale) > 40:
            print(f"      ... and {len(stale) - 40} more "
                  f"(--list to see a full bucket)")

    # 4. GSC has indexed something this site does not publish.
    bad = [u for u in exp.get(INDEXED, {}) if u not in inv]
    found += emit(
        bad, "Indexed, but not a URL this site publishes",
        "Usually a legacy duplicate GitHub Pages still serves at 200 (an "
        "…/index.html twin, or a ?param URL). Harmless if its canonical is "
        "correct - check that it is.", exp, inv)

    if not found:
        print("  none - every GSC verdict is consistent with the repo")
    return found


def emit(urls, title, advice, exp, inv) -> int:
    if not urls:
        return 0
    print(f"\n  [{len(urls)}] {title}")
    for line in advice.split(". "):
        if line:
            print(f"      {line.rstrip('.')}.")
    for u in sorted(urls):
        crawled = exp[bucket_of(u, exp)][u] or "?"
        shown = u[len(bs.SITE):] if u.startswith(bs.SITE) else u
        print(f"      {shown:<70} last crawled {crawled}")
    return 1


def report_diff(inv, new_exp, old_exp) -> None:
    """Where each URL moved between two exports."""
    old = {u: b for b, urls in old_exp.items() for u in urls}
    new = {u: b for b, urls in new_exp.items() for u in urls}
    ABSENT = "(not yet judged)"

    h("Change by bucket")
    print(f"  {'bucket':<45}{'was':>6}{'now':>6}{'delta':>7}"
          f"{'added':>7}{'gone':>6}{'same':>6}")
    for name in sorted(set(old_exp) | set(new_exp)):
        o, n = set(old_exp.get(name, {})), set(new_exp.get(name, {}))
        print(f"  {name:<45}{len(o):>6}{len(n):>6}{len(n) - len(o):>+7}"
              f"{len(n - o):>7}{len(o - n):>6}{len(o & n):>6}")
    print(f"\n  URLs Google knows about: {len(old)} -> {len(new)}"
          f"  ({len(new) - len(old):+})")
    po = sum(1 for u in old if u in inv)
    pn = sum(1 for u in new if u in inv)
    print(f"  ...of which published:   {po} -> {pn}  ({pn - po:+})")
    oi = sum(1 for u in old_exp.get(INDEXED, {}) if u in inv)
    ni = sum(1 for u in new_exp.get(INDEXED, {}) if u in inv)
    print(f"  Published AND indexed:   {oi} -> {ni}  ({ni - oi:+})")

    h("Direction of travel")
    moves = Counter((old.get(u, ABSENT), new.get(u, ABSENT))
                    for u in set(old) | set(new))
    rescued = sum(v for (a, b), v in moves.items()
                  if b == INDEXED and a not in (ABSENT, INDEXED))
    fresh = moves[(ABSENT, INDEXED)]
    print(f"  newly discovered AND indexed  {fresh:>6}")
    print(f"  rescued from a not-indexed state  {rescued:>2}")
    print("  (the second number is the one that shows a fix working;")
    print("   the first only shows Google finding new URLs)")
    print()
    for (a, b), v in sorted(moves.items(), key=lambda kv: -kv[1]):
        if a != b:
            print(f"  {v:>6}  {abbrev(a) if a != ABSENT else a}"
                  f"  ->  {abbrev(b) if b != ABSENT else b}")
    print("  --- unchanged ---")
    for (a, b), v in sorted(moves.items(), key=lambda kv: -kv[1]):
        if a == b:
            print(f"  {v:>6}  {abbrev(a) if a != ABSENT else a}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Reconcile a GSC page-indexing export against the site.")
    ap.add_argument("export", type=Path, help="an export directory of CSVs")
    ap.add_argument("--diff", type=Path, metavar="OLDER",
                    help="an earlier export directory, to compare against")
    ap.add_argument("--list", metavar="BUCKET",
                    help="print every URL in one bucket, then stop")
    args = ap.parse_args()

    exp = load_export(args.export)
    inv, commits = inventory()
    buckets, ghosts = reconcile(inv, exp)

    if args.list:
        urls = buckets.get(args.list)
        if urls is None:
            sys.exit(f"no such bucket: {args.list}\n"
                     f"try: {', '.join(sorted(buckets))}")
        for u in urls:
            print(u)
        return 0

    print(f"export:    {args.export}")
    print(f"inventory: the working tree at "
          f"{subprocess.run(['git', '-C', str(REPO), 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()}")

    report_reconciliation(inv, buckets, ghosts)
    report_by_sitemap(inv, buckets)
    report_unjudged(inv, buckets)
    report_ghosts(exp, ghosts)
    problems = report_contradictions(inv, exp, buckets, commits)

    if args.diff:
        report_diff(inv, exp, load_export(args.diff))

    # The hard assertions: the buckets partition the inventory exactly, and the
    # export itself is well-formed. A URL in two GSC categories at once would
    # otherwise be absorbed silently - bucket_of() takes the first match - and
    # every count downstream would be quietly wrong.
    h("Self-check")
    total = sum(len(v) for v in buckets.values())
    seen = [u for urls in buckets.values() for u in urls]
    multi = {u: [n for n in exp if u in exp[n]]
             for u in {u for urls in exp.values() for u in urls}}
    multi = {u: names for u, names in multi.items() if len(names) > 1}
    if multi:
        print(f"  {len(multi)} URL(s) appear in more than one export CSV:")
        for u, names in sorted(multi.items())[:10]:
            print(f"      {u}\n        {', '.join(names)}")
    ok = True
    for label, cond in (
        (f"buckets sum to the inventory ({total} == {len(inv)})",
         total == len(inv)),
        ("no URL counted twice across buckets", len(set(seen)) == len(seen)),
        ("every published URL accounted for", set(seen) == set(inv)),
        (f"no URL in two GSC categories at once ({len(multi)} found)",
         not multi),
        (f"ghosts + judged == export rows "
         f"({len(ghosts)} + {total - len(buckets.get('unjudged', []))})",
         len(ghosts) + total - len(buckets.get("unjudged", []))
         == len({u for urls in exp.values() for u in urls})),
    ):
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        ok &= bool(cond)

    if not ok:
        print("\nFAIL: the reconciliation does not balance. Any number taken "
              "from this run is unsafe until it does.", file=sys.stderr)
        return 1
    if problems:
        print(f"\n{problems} contradiction class(es) found - see above. "
              f"These are reported, not errors: a stale GSC verdict is normal "
              f"and usually needs a recrawl rather than a change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
