#!/usr/bin/env python3
"""Rebuild every generated page, in the right order, with one command.

    python3 scripts/build.py              # content generators + bake + shell check
    python3 scripts/build.py --sitemap    # AFTER committing: rebuild the sitemap
    python3 scripts/build.py --check      # dry-run / verify mode, writes nothing

WHY THIS EXISTS
---------------
The generator sequence was written down in at least four places and the copies
disagreed: the root CLAUDE.md said five generators, .claude/commands/
rebuild-nav.md said five, notes-data/CLAUDE.md gave a three-step variant and
verify_generated.py knew eight. A session following any one of the short lists
would rebuild some of the site and leave the rest stale - exactly the drift
verify_generated.py was written to catch after the fact. This runs the ONE list,
`scripts/site_layout.GENERATORS`, and the docs point here instead of restating
it.

WHAT A RUN DOES
---------------
  1. Every content generator, in order, in place (the 446 generated pages).
  2. bake_templates.py --apply          the 17 hand-written pages' header,
                                        footer and script tail.
  3. verify_page_shell.py               proves the shell reached every page
                                        (check 9 is the one that matters).
  4. One final line saying what changed and what to do next.

THE SITEMAP IS SEPARATE, AND THAT IS NOT AN OVERSIGHT
----------------------------------------------------
build_sitemap.py takes every <lastmod> from `git log -1 -- <path>`, so run
before the commit it bakes in stale dates and needs a second commit to fix.
This has happened. So the default run does NOT touch the sitemap and ends by
telling you to commit and then run `--sitemap`. The post-commit hook in
.githooks/ does the same thing automatically, if enabled.

--check runs each step in its own dry-run/verify mode where one exists
(build_flashcards.py has none and is skipped with a note) and writes nothing.
It is NOT a substitute for verify_generated.py, which is the only check that
proves the committed tree is what the generators produce; it says so at the
end.

Standard library only, plus node/npx for the generators that need them - and
if npx is missing the first generator that needs it stops with
prettier_util's message rather than writing unformatted pages.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import site_layout  # noqa: E402

# Generators that have a --check flag of their own. build_flashcards.py does
# not; under --check it is skipped and the skip is printed.
HAS_CHECK = {
    "build_notes_pages.py",           # compares rendered output against disk
    "build_past_paper_taxonomy.py",   # validates inputs, writes nothing
    "build_past_paper_questions.py",  # validates inputs, writes nothing
    "build_questions.py",             # validates inputs, writes nothing
    "extract_glossary.py",            # validates and reports, writes nothing
    "build_glossary.py",              # validates inputs, writes nothing
}


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def changed_files() -> set[str]:
    """Tracked files that differ from the index or are untracked."""
    out = git("status", "--porcelain", "--untracked-files=all")
    files = set()
    for line in out.splitlines():
        if not line.strip():
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.add(path)
    return files


def run(label: str, argv: list[str]) -> int:
    """Run one step, streaming its output indented. Returns the exit code."""
    print(f"\n--- {label}")
    print(f"    $ {' '.join(argv)}")
    sys.stdout.flush()
    t0 = time.monotonic()
    proc = subprocess.run(argv, cwd=ROOT, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.rstrip("\n").splitlines():
        print(f"    {line}")
    dt = time.monotonic() - t0
    status = "ok" if proc.returncode == 0 else f"EXIT {proc.returncode}"
    print(f"    [{status}, {dt:.1f}s]")
    return proc.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sitemap", action="store_true",
                    help="rebuild sitemap.xml + sitemaps/*.xml. Run this "
                         "AFTER committing the page changes, never before.")
    ap.add_argument("--check", action="store_true",
                    help="dry-run / verify mode everywhere a script supports "
                         "it; writes nothing")
    args = ap.parse_args()
    py = sys.executable

    if args.sitemap:
        return sitemap(args.check, py)

    before = changed_files()
    failed: list[str] = []

    # 1. the content generators, in order
    for name in site_layout.CONTENT_GENERATORS:
        argv = [py, f"scripts/{name}"]
        if args.check:
            if name not in HAS_CHECK:
                print(f"\n--- {name}: no --check mode, skipped under --check")
                continue
            argv.append("--check")
        if run(name, argv) != 0:
            failed.append(name)
            # A generator that stopped (npx missing, a validation error) has
            # left nothing useful for the ones after it to build on.
            break

    # 2. the 17 hand-written pages
    if not failed:
        argv = [py, "scripts/bake_templates.py"] + ([] if args.check else ["--apply"])
        if run("bake_templates.py" + (" (dry run)" if args.check else " --apply"),
               argv) != 0:
            failed.append("bake_templates.py")

    # 3. prove the shell reached every page
    if not failed:
        if run("verify_page_shell.py", [py, "scripts/verify_page_shell.py"]) != 0:
            failed.append("verify_page_shell.py")

    # 4. the one line that matters
    print()
    if failed:
        print(f"BUILD FAILED at {failed[0]} - nothing after it was run. "
              f"Fix that, then re-run python3 scripts/build.py.")
        return 1

    after = changed_files()
    if args.check:
        print("CHECK COMPLETE - nothing written. This proved the inputs are "
              "valid; it does NOT prove the committed pages are current.")
        print("For that: python3 scripts/verify_generated.py")
        return 0

    new = sorted(after - before)
    if new:
        sample = ", ".join(new[:5]) + (f" ... (+{len(new) - 5})" if len(new) > 5 else "")
        print(f"BUILD COMPLETE - {len(new)} file(s) changed: {sample}")
    else:
        print("BUILD COMPLETE - 0 files changed; everything was already "
              "current.")
    print("Now commit, then run: python3 scripts/build.py --sitemap")
    return 0


def sitemap(check: bool, py: str) -> int:
    dirty = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and not l[3:].startswith(("sitemap.xml", "sitemaps/"))]
    if dirty and not check:
        print("NOTE: the working tree has uncommitted changes. build_sitemap.py "
              "takes every <lastmod> from git, so any page below that is not "
              "yet committed gets a stale date:", file=sys.stderr)
        for line in dirty[:10]:
            print(f"      {line}", file=sys.stderr)
        print("      Commit first, then re-run --sitemap. Continuing anyway.\n",
              file=sys.stderr)
    argv = [py, f"scripts/{site_layout.SITEMAP_GENERATOR}"] + (["--check"] if check else [])
    rc = run(site_layout.SITEMAP_GENERATOR + (" --check" if check else ""), argv)
    print()
    if check:
        return rc   # build_sitemap --check prints SITEMAP OK / SITEMAP STALE itself
    if rc != 0:
        print("SITEMAP BUILD FAILED - see above.")
        return 1
    print("SITEMAP REBUILT - commit sitemap.xml and sitemaps/ as their own "
          "commit. (It must run AFTER the content commit, which is why it is "
          "a separate step.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
