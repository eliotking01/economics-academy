#!/usr/bin/env python3
"""Prove the committed generated output is current with its source.

    python3 scripts/verify_generated.py
    python3 scripts/verify_generated.py --keep    # leave the worktree to inspect

273 of this repo's files are written by a generator and committed. Nothing
checked that what is committed is what the generator would produce today, so a
change to a data file, a template string or a generator could sit in the repo
for weeks while the pages it should have changed stayed as they were.

WHY THIS IS NOT `--check` ON EACH GENERATOR
-------------------------------------------
PH09b-026 recommended teaching the four generators that lack it the
committed-output comparison `build_sitemap.py` already has. This does the same
job one level up, and does it better here, for four reasons found while
implementing it:

  1. Two generators run Prettier over their own output after writing, so the
     committed file is prettier(render), never render. An in-process comparison
     has to shell out to Prettier anyway to be faithful - at which point it is
     doing what this script does, four times, in four different shapes.
  2. It catches drift in every file a generator touches, not the ones its own
     --check happens to model. The sitemap is the worked example: item 0.1
     rewrote 90 pages, their git lastmod moved, and sitemap.xml went stale. No
     per-generator check would have found that, because no single generator
     owns it. This script does, because it asks git.
  3. One definition of "generated", so a sixth generator is one list entry
     rather than a fifth reimplementation.
  4. It needs no surgery on five working generators, which is the part of this
     change most likely to break something.

The four `--check` flags still validate their inputs, which is useful and
cheap. Their help text now says that is all they do.

HOW IT WORKS
------------
Runs every generator for real inside a throwaway `git worktree` of HEAD, then
asks git what changed. Nothing is written anywhere near your working tree - the
same isolation the audit used for the same question, recorded as DECISIONS.md D6,
and the reason is the same: regenerating in place would silently destroy any
hand-edit to a generated file, which is one of the things this exists to detect.

A clean run means: check out this commit, run every generator, and not one byte
moves.

Standard library only. Needs `node` for the glossary's KaTeX pre-render and
`npx` for Prettier - both already required to run the generators at all.
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Order matters. The taxonomy feeds the question bank, and the sitemap
# enumerates the filesystem, so it can only be right once every page exists.
GENERATORS = [
    "build_past_paper_taxonomy.py",
    "build_past_paper_questions.py",
    "build_questions.py",
    # extract_glossary.py writes glossary-data/terms.json from the notes HTML,
    # and build_glossary.py renders that. Both are generated and committed, so
    # both belong here - and the extractor has to run first or the build would
    # be checked against a stale extraction.
    "extract_glossary.py",
    "build_glossary.py",
    "build_flashcards.py",
    "build_sitemap.py",
]


def git(*args, cwd=ROOT):
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--keep", action="store_true",
                    help="do not delete the worktree, so you can inspect it")
    args = ap.parse_args()

    dirty = git("status", "--porcelain").strip()
    if dirty:
        print("NOTE: your working tree has uncommitted changes. This checks "
              "HEAD, not what you have on disk:", file=sys.stderr)
        for line in dirty.splitlines()[:10]:
            print(f"        {line}", file=sys.stderr)
        print(file=sys.stderr)

    head = git("rev-parse", "--short", "HEAD").strip()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="verify-generated-"))
    wt = tmp / "tree"
    print(f"checking {head} in a throwaway worktree")

    failed = []
    try:
        git("worktree", "add", "--quiet", "--detach", str(wt), "HEAD")

        for name in GENERATORS:
            proc = subprocess.run(
                [sys.executable, f"scripts/{name}"],
                cwd=wt, capture_output=True, text=True,
            )
            status = "ok" if proc.returncode == 0 else f"EXIT {proc.returncode}"
            print(f"  ran {name:34} {status}")
            if proc.returncode != 0:
                failed.append(name)
                tail = (proc.stderr or proc.stdout).strip().splitlines()[-6:]
                for line in tail:
                    print(f"        {line}", file=sys.stderr)

        changed = [l for l in git("status", "--porcelain", cwd=wt).splitlines() if l]

        print()
        # stdout is block-buffered when piped and stderr is not, so without this
        # the failure report lands above the run log in a CI transcript.
        sys.stdout.flush()
        if failed:
            print(f"FAIL: {len(failed)} generator(s) did not run: "
                  f"{', '.join(failed)}", file=sys.stderr)
        if changed:
            print(f"FAIL: {len(changed)} generated file(s) are not current "
                  f"with their source:", file=sys.stderr)
            for line in changed[:40]:
                print(f"  {line}", file=sys.stderr)
            if len(changed) > 40:
                print(f"  ... and {len(changed) - 40} more", file=sys.stderr)
            print("\nRe-run the generator that owns them and commit the result. "
                  "Do not hand-edit generated files.", file=sys.stderr)
        if not failed and not changed:
            print(f"all {len(GENERATORS)} generators ran; 0 files would change")
        return 1 if (failed or changed) else 0
    finally:
        if args.keep:
            print(f"\nworktree kept at {wt}\n  remove with: "
                  f"git worktree remove --force {wt}")
        else:
            subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                           cwd=ROOT, capture_output=True)
            subprocess.run(["git", "worktree", "prune"], cwd=ROOT,
                           capture_output=True)
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
