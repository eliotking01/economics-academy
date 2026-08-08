#!/usr/bin/env python3
"""Lighthouse baseline for the six representative page types, by median.

Run against the LIVE site, not a local server. The largest performance finding
on this site is a serialised third-party request chain - main.css @imports a
Google Fonts stylesheet, which then fetches woff2 from a second origin. A
localhost run has none of that latency and would understate it by design.

Three runs per URL, median taken per metric. A single Lighthouse run is too
noisy to act on: simulated throttling varies by 10-20% run to run, which is
larger than most of the differences this pass is trying to measure.

The point of committing this rather than running the CLI by hand is that the
after-measurement has to use an identical method for the before/after to mean
anything. Same URLs, same run count, same flags, same Lighthouse major version.

    python3 seo/tools/run_lighthouse.py --out <dir>
    python3 seo/tools/run_lighthouse.py --out <dir> --runs 3
    python3 seo/tools/run_lighthouse.py --out <dir> --only homepage

Writes <dir>/<label>-<n>.json raw reports and prints a markdown table of
medians. Requires Node and Chrome; installs Lighthouse on demand via npx.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from pathlib import Path

SITE = "https://economicsacademy.co.uk"

# One page per type, chosen so every distinct loading pattern on the site is
# covered exactly once. The notes page is deliberately the densest one - it is
# the only sample that loads MathJax, so it is the only one that can show the
# layout shift MathJax causes.
PAGES = [
    ("homepage", "/"),
    ("section-hub", "/revision-notes/"),
    ("notes-topic", "/revision-notes/aqa-a2-macro/2-1-3-uses-of-index-numbers.html"),
    ("practice-questions",
     "/practice-questions/edexcel-theme-1/1-1-1-economics-as-a-social-science.html"),
    ("past-paper-questions",
     "/past-paper-questions/edexcel/1-2-3-price-income-cross-elasticities-of-demand/"),
    ("flashcards", "/flashcards/edexcel-a/theme-1/"),
]

# Lighthouse 12 defaults to mobile form factor and simulated throttling, but
# both are named explicitly so a future default change cannot silently make the
# after-run incomparable to the before-run.
LH_VERSION = "lighthouse@12"
LH_FLAGS = [
    "--only-categories=performance",
    "--form-factor=mobile",
    "--screenEmulation.mobile",
    "--throttling-method=simulate",
    "--output=json",
    "--quiet",
    "--chrome-flags=--headless=new --no-sandbox --disable-gpu",
]

# audit id -> column heading. numericValue is in ms except CLS, which is unitless.
METRICS = [
    ("largest-contentful-paint", "LCP"),
    ("cumulative-layout-shift", "CLS"),
    ("total-blocking-time", "TBT"),
    ("first-contentful-paint", "FCP"),
    ("speed-index", "SI"),
]


def run_one(url: str, out: Path) -> dict | None:
    cmd = ["npx", "--yes", LH_VERSION, url, *LH_FLAGS, f"--output-path={out}"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not out.exists():
        print(f"    FAILED: {proc.stderr.strip().splitlines()[-1:] or proc.stdout[-300:]}",
              file=sys.stderr)
        return None
    return json.loads(out.read_text())


def summarise(report: dict) -> dict:
    audits = report["audits"]
    row = {"score": report["categories"]["performance"]["score"]}
    for aid, label in METRICS:
        row[label] = audits.get(aid, {}).get("numericValue")
    # Transfer size of everything the page pulled, and the render-blocking list.
    total = audits.get("total-byte-weight", {}).get("numericValue")
    row["bytes"] = total
    blocking = audits.get("render-blocking-resources", {})
    row["blocking_ms"] = blocking.get("numericValue")
    row["blocking"] = [
        (i.get("url", ""), i.get("totalBytes"), i.get("wastedMs"))
        for i in blocking.get("details", {}).get("items", [])
    ]
    chains = audits.get("critical-request-chains", {})
    row["chain_len"] = (chains.get("details", {}) or {}).get("longestChain", {}).get("length")
    row["chain_ms"] = (chains.get("details", {}) or {}).get("longestChain", {}).get("duration")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="directory for raw JSON reports")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--only", help="run a single label from PAGES")
    args = ap.parse_args()

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    pages = [p for p in PAGES if not args.only or p[0] == args.only]

    results: dict[str, dict] = {}
    for label, path in pages:
        url = SITE + path
        print(f"\n{label}  {url}", file=sys.stderr)
        rows = []
        for n in range(1, args.runs + 1):
            print(f"  run {n}/{args.runs}", file=sys.stderr)
            rep = run_one(url, outdir / f"{label}-{n}.json")
            if rep:
                rows.append(summarise(rep))
        if not rows:
            continue
        med: dict = {"url": path, "runs": len(rows)}
        for key in ("score", "LCP", "CLS", "TBT", "FCP", "SI", "bytes",
                    "blocking_ms", "chain_len", "chain_ms"):
            vals = [r[key] for r in rows if r.get(key) is not None]
            med[key] = statistics.median(vals) if vals else None
        # Blocking resource list is structural, not numeric - take the last run's.
        med["blocking"] = rows[-1]["blocking"]
        results[label] = med

    print("\n\n| Page | Perf | LCP | CLS | TBT | FCP | SI | Weight |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for label, m in results.items():
        def ms(v):
            return f"{v/1000:.2f} s" if v is not None else "-"
        print(f"| {label} | {int(m['score']*100) if m['score'] is not None else '-'} "
              f"| {ms(m['LCP'])} | {m['CLS']:.3f} | {int(m['TBT'])} ms "
              f"| {ms(m['FCP'])} | {ms(m['SI'])} "
              f"| {m['bytes']/1024:.0f} KB |")

    print("\n\nRender-blocking resources and critical chain:")
    for label, m in results.items():
        print(f"\n{label}  (chain {m['chain_len']} deep, {m['chain_ms']:.0f} ms)"
              if m["chain_ms"] else f"\n{label}")
        for u, b, w in m["blocking"]:
            print(f"    {w:6.0f} ms  {b/1024:7.1f} KB  {u}")

    (outdir / "medians.json").write_text(json.dumps(results, indent=2))
    print(f"\nMedians written to {outdir / 'medians.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
