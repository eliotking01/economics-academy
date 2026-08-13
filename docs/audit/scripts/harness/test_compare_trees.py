#!/usr/bin/env python3
"""Break each of compare_trees.py's ten assertions on purpose, and check it notices.

    python3 docs/audit/scripts/harness/test_compare_trees.py
    python3 docs/audit/scripts/harness/test_compare_trees.py --case a4-anchor-stripped
    python3 docs/audit/scripts/harness/test_compare_trees.py --keep

WHY THIS EXISTS
---------------
A verifier that has only ever been green is not evidence of anything. Wave 4
produced two checks that came back green for the wrong reason and were only
found out when someone broke them deliberately - one because the edit meant to
trip it landed in an `alt` attribute, which is not visible text, and one
because the run under test merged a branch instead of comparing against it.
Both were harness bugs, not check bugs.

So two rules are built in here:

  1. **Every mutation asserts that it applied.** `edit()` fails if its search
     text is absent, and fails again if the file did not actually change. A
     case that silently edited nothing would otherwise "prove" an assertion
     fires when it never ran.
  2. **Some cases expect a PASS.** An assertion that fires on everything is as
     useless as one that fires on nothing. `a2-alt-invisible`, `a6-reindent`
     and `a8-family-exempt` exist to pin down what each assertion is
     deliberately blind to - and each is paired with a case proving something
     else catches it.

HOW IT RUNS
-----------
Three throwaway `git worktree` trees of HEAD: OLD, NEW and THIRD. Each case
mutates NEW (and, for assertion 9, THIRD), runs compare_trees.py over the two
trees with `--only`, checks the outcome, then restores NEW with
`git checkout -- . && git clean -fd`.

Standard library only. Roughly two minutes; the four cases that exercise
assertion 10 run NEW's whole verifier suite, which is most of it.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

HARNESS = pathlib.Path(__file__).resolve().parent
REPO = HARNESS.parents[3]
COMPARE = HARNESS / "compare_trees.py"

# Fixtures, each chosen for a property the case depends on.
NOTES = "revision-notes/edexcel-theme-1/1-1-1-economics-as-a-social-science.html"
PPF = "revision-notes/edexcel-theme-1/1-1-4-production-possibility-frontiers.html"
INDEX = "revision-notes/aqa-a2-macro/2-1-3-uses-of-index-numbers.html"
ABOUT = "about.html"


# --------------------------------------------------------------------------
# Mutations that prove they happened
# --------------------------------------------------------------------------

def edit(root: pathlib.Path, rel: str, old: str, new: str) -> None:
    """Replace `old` with `new`, and fail loudly if that did not happen.

    The whole value of this file rests on this function. A case whose search
    string has drifted out of the page must fail here, not quietly make no
    change and let the assertion under test report a pass.
    """
    path = root / rel
    before = path.read_text(encoding="utf-8")
    if old not in before:
        raise AssertionError(f"fixture drift: {old!r} not found in {rel}")
    after = before.replace(old, new, 1)
    if after == before:
        raise AssertionError(f"edit was a no-op in {rel}")
    path.write_text(after, encoding="utf-8")
    if path.read_text(encoding="utf-8") != after:
        raise AssertionError(f"write did not stick: {rel}")


def add_file(root: pathlib.Path, rel: str, body: str) -> None:
    path = root / rel
    if path.exists():
        raise AssertionError(f"{rel} already exists; the case assumes it does not")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    if not path.exists():
        raise AssertionError(f"failed to create {rel}")


def remove_file(root: pathlib.Path, rel: str) -> None:
    path = root / rel
    if not path.exists():
        raise AssertionError(f"{rel} is not there to remove")
    path.unlink()
    if path.exists():
        raise AssertionError(f"failed to remove {rel}")


def copy_page(root: pathlib.Path, src: str, dst: str) -> None:
    body = (root / src).read_text(encoding="utf-8")
    add_file(root, dst, body)


def rename(root: pathlib.Path, src: str, dst: str) -> None:
    """Used to take .git away from a worktree and give it back.

    In a linked worktree `.git` is a FILE holding a gitdir pointer, so this is
    a one-byte-cheap way to make a tree stop being a git tree - which is what
    the a10-needs-a-git-tree case needs, and much cheaper than copying 220 MB.
    """
    a, b = root / src, root / dst
    if not a.exists():
        raise AssertionError(f"{src} is not there to rename")
    a.rename(b)
    if a.exists() or not b.exists():
        raise AssertionError(f"rename {src} -> {dst} did not take")


# --------------------------------------------------------------------------
# The cases
# --------------------------------------------------------------------------
# Each: name, the assertions to run, what must happen, and the mutation.
# `expect` is "FAIL" (compare_trees must exit non-zero) or "PASS" (exit 0).

def case_list():
    return [
        # ---- baseline -----------------------------------------------------
        dict(name="baseline-identical", only="1,2,3,4,5,6,7,8",
             expect="PASS", mutate=lambda o, n, t: None,
             why="two worktrees of the same commit must agree on everything"),

        # ---- 1  URL set ---------------------------------------------------
        dict(name="a1-page-added", only="1", expect="FAIL",
             mutate=lambda o, n, t: copy_page(
                 n, NOTES, "revision-notes/edexcel-theme-1/zz-extra.html"),
             why="a page the build invented is a new URL, and URLs are frozen"),
        dict(name="a1-page-removed", only="1", expect="FAIL",
             mutate=lambda o, n, t: remove_file(n, ABOUT),
             why="a missing page and a moved page look the same to a crawler"),
        # NOT notes-data/, which Wave 2 Phase 3 legitimately excluded on
        # 2026-08-11 - this case then passed and the suite caught its own
        # fixture drift, which is the whole reason for the paired case below.
        dict(name="a1-source-dir-published", only="1", expect="FAIL",
             mutate=lambda o, n, t: add_file(
                 n, "topic-data/edexcel-theme-1/1-1-1.html", "<p>slice</p>\n"),
             why="PH06's named risk: a build's source directory reaching the "
                 "live site because _config.yml was not updated"),
        dict(name="a1-source-dir-excluded", only="1", expect="PASS",
             mutate=lambda o, n, t: (
                 add_file(n, "topic-data/edexcel-theme-1/1-1-1.html",
                          "<p>slice</p>\n"),
                 edit(n, "_config.yml", "  - scripts/",
                      "  - topic-data/\n  - scripts/"),
             ),
             why="the same directory, excluded in the same commit, is invisible "
                 "to the published surface - which is the rule DO-NOT-BREAK sets"),

        # ---- 2  visible text ----------------------------------------------
        dict(name="a2-word-changed", only="2", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, NOTES, "Ready to apply these notes?",
                 "Ready to apply these note?"),
             why="one word of prose is the thing this whole wave may not touch"),
        dict(name="a2-alt-invisible", only="2", expect="PASS",
             mutate=lambda o, n, t: edit(
                 n, PPF, 'alt="Production possibility frontier showing',
                 'alt="PPF showing'),
             why="an alt attribute is NOT visible text. Wave 4 lost two days to "
                 "a test that edited one and called the green a pass"),
        dict(name="a2-alt-caught-by-8", only="8", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, PPF, 'alt="Production possibility frontier showing',
                 'alt="PPF showing'),
             why="the pair to the case above: what assertion 2 cannot see, "
                 "assertion 8 can"),

        # ---- 3  LaTeX ------------------------------------------------------
        dict(name="a3-latex-whitespace", only="3", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, INDEX, r"\times 100 = 100 \)", r"\times 100  = 100 \)"),
             why="whitespace inside a formula is meaning; assertion 2 collapses "
                 "it away, which is the only reason assertion 3 exists"),
        dict(name="a3-latex-invisible-to-2", only="2", expect="PASS",
             mutate=lambda o, n, t: edit(
                 n, INDEX, r"\times 100 = 100 \)", r"\times 100  = 100 \)"),
             why="proves the hole assertion 3 fills is a real one"),

        # ---- 4  markup -----------------------------------------------------
        dict(name="a4-anchor-stripped", only="4", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, NOTES,
                 '<a href="/marking.html" class="button alt">Get Essays Marked</a>',
                 "Get Essays Marked"),
             why="CLAUDE.md's recorded failure mode: a scripted rewrite that "
                 "destroys an <a> and changes not one character of visible text"),
        dict(name="a4-anchor-invisible-to-2", only="2", expect="PASS",
             mutate=lambda o, n, t: edit(
                 n, NOTES,
                 '<a href="/marking.html" class="button alt">Get Essays Marked</a>',
                 "Get Essays Marked"),
             why="the same edit, and assertion 2 sees nothing at all"),
        dict(name="a4-spec-alert-factored-out", only="4", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, NOTES, '<div class="spec-alert">', "<div>"),
             why="DO-NOT-BREAK's hardest entry to resist undoing. Dropping the "
                 "class keeps every word on the page, so only the class counter "
                 "catches it"),

        # ---- 5  <head> ------------------------------------------------------
        dict(name="a5-description-changed", only="5", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, ABOUT, "Eliot King is a First-Class BSc Economics graduate",
                 "Eliot King is a first class BSc Economics graduate"),
             why="a re-derived meta description is a content change wearing a "
                 "formatting change's clothes"),
        dict(name="a5-invisible-to-2", only="2", expect="PASS",
             mutate=lambda o, n, t: edit(
                 n, ABOUT, "Eliot King is a First-Class BSc Economics graduate",
                 "Eliot King is a first class BSc Economics graduate"),
             why="<meta content> is not visible text either"),
        dict(name="a5-allowlisted", only="5", expect="PASS",
             allowlist={ABOUT: {"meta:description": "test fixture"}},
             mutate=lambda o, n, t: edit(
                 n, ABOUT, "Eliot King is a First-Class BSc Economics graduate",
                 "Eliot King is a first class BSc Economics graduate"),
             why="an exception with a written reason is permitted; that is what "
                 "makes the empty allowlist mean something"),
        dict(name="a5-allowlist-needs-a-reason", only="5", expect="ERROR",
             allowlist={ABOUT: {"meta:description": "   "}},
             mutate=lambda o, n, t: None,
             why="an entry with no reason is an exemption, not an exception, "
                 "and is rejected before any comparison runs"),

        # ---- 6  JSON-LD -----------------------------------------------------
        dict(name="a6-value-changed", only="6", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, NOTES, '"@type": "BreadcrumbList"', '"@type": "ItemList"'),
             why="structured data is what Google reads; it is never incidental"),
        dict(name="a6-reindent-is-fine", only="6", expect="PASS",
             mutate=lambda o, n, t: edit(
                 n, NOTES, '        "@type": "BreadcrumbList",',
                 '            "@type":     "BreadcrumbList",'),
             why="indentation will legitimately change when a generator writes "
                 "the block. Meaning must not"),
        dict(name="a6-reindent-caught-by-8", only="8", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, NOTES, '        "@type": "BreadcrumbList",',
                 '            "@type":     "BreadcrumbList",'),
             why="assertion 6 forgives the reindent; assertion 8 still reports "
                 "the file moved, so nothing is invisible"),

        # ---- 7  internal links ----------------------------------------------
        # WAS href="/tutoring.html" and SILENTLY STOPPED PROVING ANYTHING on
        # 2026-08-11, when Wave 2 Phase 7 (ecbf683) baked the header into all
        # 463 pages: the nav carries a second /tutoring.html link, edit()
        # replaces the first occurrence only, and internal_links() returns a
        # SET - so the target never left it and assertion 7 was right to
        # report no loss. The case went red on 2026-08-13 and was found to
        # have been vacuous for two waves. The MCQ teaser link is the fixture
        # now: exactly one on the page, and no nav item points at it.
        dict(name="a7-link-lost", only="7", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, NOTES,
                 'href="/practice-questions/edexcel-theme-1/'
                 '1-1-1-economics-as-a-social-science.html"',
                 'href="https://example.com/"'),
             why="links may be added and never lost. 5 other pages link to "
                 "that target, so removing this one cannot trip the orphan "
                 "limit instead and pass for the wrong reason"),
        dict(name="a7-broken-target", only="7", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, NOTES, '<div class="notes-cta">',
                 '<div class="notes-cta"><a href="/no-such-page.html">x</a>'),
             why="an added link is allowed; an added link to nothing is not"),
        dict(name="a7-orphan-limit", only="7", expect="FAIL",
             mutate=lambda o, n, t: copy_page(
                 n, NOTES, "revision-notes/edexcel-theme-1/zz-orphan.html"),
             why="461 of 463 pages are reachable without JavaScript today; a "
                 "third unreachable page is a regression, not a rounding error"),

        # ---- 8  bytes --------------------------------------------------------
        dict(name="a8-unrelated-file-moved", only="8", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, "css/main.css",
                 "/* The two @import rules", "/*  The two @import rules"),
             why="the build must be a no-op everywhere it is not wanted"),
        dict(name="a8-family-exempt", only="8", expect="PASS",
             family=["css/main.css"],
             mutate=lambda o, n, t: edit(
                 n, "css/main.css",
                 "/* The two @import rules", "/*  The two @import rules"),
             why="and inside the family being migrated, a change is the point"),

        # ---- 9  idempotence ---------------------------------------------------
        dict(name="a9-second-build-differs", only="9", expect="FAIL", twice=True,
             mutate=lambda o, n, t: edit(
                 t, ABOUT, "<title>", "<title >"),
             why="PH09b-025 turned up three times in Wave 4 alone. Anything "
                 "that writes a file gets hashed across runs"),
        dict(name="a9-second-build-identical", only="9", expect="PASS", twice=True,
             mutate=lambda o, n, t: None,
             why="two builds of the same input are the same bytes"),
        dict(name="a9-not-run-says-so", only="9", expect="PASS",
             must_print="NOT RUN",
             mutate=lambda o, n, t: None,
             why="without a second tree the assertion did not run, and a "
                 "skipped assertion must never read as a passed one"),

        # ---- 10  the existing suite --------------------------------------------
        dict(name="a10-css-load-order", only="10", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, ABOUT,
                 '<link rel="stylesheet" href="/css/fontawesome-all.min.css" />',
                 ""),
             why="THE Wave 2 failure mode: a generated <head> emitting the same "
                 "links in a different order breaks contact and tutoring "
                 "silently, with no error and no failed request"),
        dict(name="a10-verifier-deleted", only="10", expect="FAIL",
             mutate=lambda o, n, t: remove_file(n, "scripts/verify_links.py"),
             why="the suite is run from NEW, so deleting a check must fail "
                 "rather than shrink the suite"),
        dict(name="a10-needs-a-git-tree", only="10", expect="FAIL",
             must_print="not a git tree",
             mutate=lambda o, n, t: rename(n, ".git", ".git-off"),
             teardown=lambda o, n, t: rename(n, ".git-off", ".git"),
             why="7 of the 14 enumerate through `git ls-files`. Running the "
                 "other 7 and calling it a pass is the exact shape of the two "
                 "Wave 4 checks that were green for the wrong reason"),
        dict(name="a10-sitemap-stale", only="10", expect="FAIL",
             mutate=lambda o, n, t: edit(
                 n, "sitemap.xml", "<sitemapindex", "<sitemapindex "),
             why="build_sitemap.py --check prints 'nothing written' on BOTH "
                 "paths. The pass signal is the exit code, and this is the "
                 "case that proves the harness reads it"),

        # ---- the verdict must not depend on the display cap ---------------
        # Found on 2026-08-13: `--max-report 0` made six of the ten assertions
        # print PASS over a real failure, because the capped DETAIL LINE was
        # what set the status. Assertion 6 reported PASS and "179 files
        # differ" in the same breath. One case per affected assertion, each
        # reusing a mutation proved to fail above, so a regression here cannot
        # be mistaken for fixture drift.
        dict(name="cap0-a3-still-fails", only="3", expect="FAIL",
             args=["--max-report", "0"],
             mutate=lambda o, n, t: edit(
                 n, INDEX, r"\times 100 = 100 \)", r"\times 100  = 100 \)"),
             why="a3 at cap 0: the verdict is not a side effect of printing"),
        dict(name="cap0-a4-still-fails", only="4", expect="FAIL",
             args=["--max-report", "0"],
             mutate=lambda o, n, t: edit(
                 n, NOTES,
                 '<a href="/marking.html" class="button alt">Get Essays Marked</a>',
                 "Get Essays Marked"),
             why="a4 at cap 0"),
        dict(name="cap0-a6-still-fails", only="6", expect="FAIL",
             args=["--max-report", "0"],
             mutate=lambda o, n, t: edit(
                 n, NOTES, '"inLanguage": "en-GB"', '"inLanguage": "en"'),
             why="a6 at cap 0 - the assertion and the mutation that exposed "
                 "this, wave-norm(1/11)"),
        dict(name="cap0-a7-still-fails", only="7", expect="FAIL",
             args=["--max-report", "0"],
             mutate=lambda o, n, t: edit(
                 n, NOTES,
                 'href="/practice-questions/edexcel-theme-1/'
                 '1-1-1-economics-as-a-social-science.html"',
                 'href="https://example.com/"'),
             why="a7 at cap 0"),
        dict(name="cap0-a8-still-fails", only="8", expect="FAIL",
             args=["--max-report", "0"],
             mutate=lambda o, n, t: edit(
                 n, PPF, 'alt="Production possibility frontier showing',
                 'alt="PPF showing'),
             why="a8 at cap 0. It was already correct, by way of an '... and "
                 "N more' line rather than by design; it now goes through the "
                 "same method as the other nine"),
        dict(name="cap0-a9-still-fails", only="9", expect="FAIL",
             args=["--max-report", "0"], twice=True,
             mutate=lambda o, n, t: edit(
                 t, ABOUT, "<title>", "<title >"),
             why="a9 at cap 0"),
        dict(name="cap0-clean-still-passes", only="1,2,3,4,5,6,7,8",
             args=["--max-report", "0"], expect="PASS",
             mutate=lambda o, n, t: None,
             why="the pair to the six above. Making the verdict independent "
                 "of the cap must not make an unchanged tree fail"),
    ]


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

def git(*args, cwd=REPO):
    return subprocess.run(["git", *args], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout


def restore(tree: pathlib.Path) -> None:
    subprocess.run(["git", "checkout", "--", "."], cwd=tree,
                   capture_output=True, check=True)
    subprocess.run(["git", "clean", "-fdq"], cwd=tree,
                   capture_output=True, check=True)
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=tree,
                           capture_output=True, text=True, check=True).stdout
    if dirty.strip():
        raise AssertionError(f"{tree} did not restore cleanly:\n{dirty}")


def run_case(case, old, new, third, tmp) -> tuple[bool, str]:
    allow_path = HARNESS / "intentional-changes.json"
    if case.get("allowlist") is not None:
        allow_path = tmp / f"allow-{case['name']}.json"
        allow_path.write_text(
            json.dumps({"changes": case["allowlist"]}), encoding="utf-8")

    case["mutate"](old, new, third)

    cmd = [sys.executable, str(COMPARE), str(old), str(new),
           "--only", case["only"], "--allowlist", str(allow_path)]
    if case["only"] != "10":
        cmd.append("--no-verifiers")
    for f in case.get("family", []):
        cmd += ["--family", f]
    cmd += case.get("args", [])
    if case.get("twice"):
        cmd += ["--twice", str(third)]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = proc.stdout + proc.stderr

    want = case["expect"]
    if want == "PASS":
        ok = proc.returncode == 0
    elif want == "FAIL":
        ok = proc.returncode == 1
    else:  # ERROR - rejected before comparing
        ok = proc.returncode not in (0, 1)

    if ok and case.get("must_print"):
        ok = case["must_print"] in out
        if not ok:
            out += f"\n(expected {case['must_print']!r} in the output)"
    return ok, out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--case", action="append", help="run only these cases")
    ap.add_argument("--keep", action="store_true", help="keep the worktrees")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print compare_trees.py's output for every case")
    args = ap.parse_args()

    cases = case_list()
    if args.case:
        wanted = set(args.case)
        cases = [c for c in cases if c["name"] in wanted]
        missing = wanted - {c["name"] for c in cases}
        if missing:
            raise SystemExit(f"no such case: {', '.join(sorted(missing))}")

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="harness-test-"))
    old, new, third = tmp / "old", tmp / "new", tmp / "third"
    head = git("rev-parse", "--short", "HEAD").strip()
    print(f"three throwaway worktrees of {head}\n")

    failures = []
    try:
        for tree in (old, new, third):
            git("worktree", "add", "--quiet", "--detach", str(tree), "HEAD")

        for case in cases:
            try:
                ok, out = run_case(case, old, new, third, tmp)
            except AssertionError as exc:
                ok, out = False, f"the case's own mutation failed: {exc}"
            finally:
                # Anything the mutation did that `git checkout` cannot undo -
                # today, only taking .git away from the worktree.
                if case.get("teardown"):
                    case["teardown"](old, new, third)
            print(f"  {'ok  ' if ok else 'FAIL'}  {case['name']:32} "
                  f"expect {case['expect']:5} on assertion(s) {case['only']}")
            if not ok:
                failures.append(case["name"])
            if args.verbose or not ok:
                for line in out.strip().splitlines():
                    print(f"          {line}")
                print(f"          why: {case['why']}")
            restore(new)
            restore(third)

        print()
        sys.stdout.flush()
        if failures:
            print(f"FAIL: {len(failures)} of {len(cases)} cases: "
                  f"{', '.join(failures)}", file=sys.stderr)
            return 1
        print(f"all {len(cases)} cases behaved as expected")
        return 0
    finally:
        for name in ("allow-",):
            for p in tmp.glob(f"{name}*"):
                p.unlink()
        if args.keep:
            print(f"\nworktrees kept at {tmp}")
        else:
            for tree in (old, new, third):
                subprocess.run(["git", "worktree", "remove", "--force", str(tree)],
                               cwd=REPO, capture_output=True)
            subprocess.run(["git", "worktree", "prune"], cwd=REPO,
                           capture_output=True)
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
