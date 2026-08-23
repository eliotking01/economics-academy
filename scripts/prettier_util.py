#!/usr/bin/env python3
"""The one place Prettier is invoked, and the one place its version lives.

    from prettier_util import format_files, format_text, PRETTIER_VERSION

WHY THIS EXISTS
---------------
Three generators - build_glossary.py, build_flashcards.py and
build_past_paper_questions.py - run Prettier over their own output so that
generating twice is byte-identical. Until 2026-08-23 each had its own copy of
the subprocess call, each pinned "prettier@3.9.6" as its own string literal
(page_shell.py made a fourth), and each silently returned False on failure and
printed a one-line WARNING that scrolled past. A machine without `npx`
therefore produced unformatted pages, a green run, and a red
verify_generated.py in CI later, with nothing local to say why.

This helper FAILS LOUDLY instead. A missing `npx`/`node`, or a Prettier run
that errors, raises PrettierError with a message that says what is missing and
how to fix it. The generators let it propagate, so a build without Node stops
at the first page it cannot format rather than writing 100 it formatted
differently.

The version is declared here and nowhere else. package.json at the repo root
pins the same number as a devDependency - that file is documentation-as-
lockfile, not an install step; the site itself has no runtime dependency and
the generators keep using `npx --yes prettier@<version>`, which fetches and
caches the pinned build on first use. .prettierrc records the settings the
generated output conforms to (Prettier's defaults, written down so "no config"
stops being a trap), and .prettierignore lists what must never be formatted.

Standard library only. Needs `npx` on PATH at call time, which CI provides via
actions/setup-node.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

PRETTIER_VERSION = "3.9.6"
PRETTIER_SPEC = f"prettier@{PRETTIER_VERSION}"


class PrettierError(SystemExit):
    """Prettier could not run. Raised as SystemExit so an uncaught one stops
    the generator with the message on stderr and exit status 1, rather than a
    traceback that buries the sentence that matters."""


def _missing_npx_message() -> str:
    return (
        f"Prettier {PRETTIER_VERSION} could not run: `npx` is not on PATH.\n"
        f"\n"
        f"The generators format their HTML output with "
        f"`npx --yes {PRETTIER_SPEC}` so that two runs are byte-identical.\n"
        f"Without it the pages would be written unformatted, the run would look\n"
        f"green, and scripts/verify_generated.py would fail in CI later with\n"
        f"nothing local to say why. So this stops here instead.\n"
        f"\n"
        f"Fix: install Node.js 20 or later (https://nodejs.org), which ships npx.\n"
        f"No `npm install` is needed - npx fetches the pinned version itself.\n"
        f"package.json at the repo root records the same pin."
    )


def format_files(paths, cwd: pathlib.Path | None = None) -> int:
    """Run Prettier --write over the given files. Returns how many it was given.

    Raises PrettierError (a SystemExit) if npx is missing or Prettier exits
    non-zero. Never returns False; a caller that could carry on without
    formatting is exactly the caller this helper exists to stop.
    """
    paths = [str(p) for p in paths]
    if not paths:
        return 0
    if shutil.which("npx") is None:
        raise PrettierError(_missing_npx_message())
    try:
        proc = subprocess.run(
            ["npx", "--yes", PRETTIER_SPEC, "--write", "--log-level", "warn"]
            + paths,
            cwd=str(cwd or ROOT), capture_output=True, text=True,
        )
    except OSError as e:   # npx present but unrunnable
        raise PrettierError(
            f"Prettier {PRETTIER_VERSION} could not run: {e}\n"
            f"`npx` is on PATH but failed to start. Check the Node install.")
    if proc.returncode != 0:
        tail = "\n".join((proc.stderr or proc.stdout).strip().splitlines()[-12:])
        raise PrettierError(
            f"Prettier {PRETTIER_VERSION} exited {proc.returncode} formatting "
            f"{len(paths)} file(s).\n"
            f"Nothing else was written after this point. Prettier's output:\n"
            f"{tail}\n"
            f"\n"
            f"If this is the first run on this machine, npx may have failed to\n"
            f"fetch the package - check the network and re-run. A syntax error\n"
            f"in the generated HTML also lands here; the path is named above.")
    if proc.stderr.strip():
        # --log-level warn: anything here is a warning about a file, worth
        # seeing, not worth stopping for.
        print(proc.stderr.rstrip(), file=sys.stderr)
    return len(paths)


def format_text(text: str, parser: str = "html", tmp: pathlib.Path | None = None) -> str:
    """Format one string through Prettier and return the result.

    Used by page_shell.py's --selftest L2 column. Writes `text` to a temp file
    (default: ROOT/.prettier_util.tmp.<parser>), formats it in place, reads it
    back, deletes it. Same failure contract as format_files().
    """
    tmp = tmp or (ROOT / f".prettier_util.tmp.{parser}")
    tmp.write_text(text, encoding="utf-8")
    try:
        if shutil.which("npx") is None:
            raise PrettierError(_missing_npx_message())
        proc = subprocess.run(
            ["npx", "--yes", PRETTIER_SPEC, "--parser", parser, str(tmp)],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        if proc.returncode != 0:
            tail = "\n".join((proc.stderr or proc.stdout).strip().splitlines()[-12:])
            raise PrettierError(
                f"Prettier {PRETTIER_VERSION} exited {proc.returncode} on a "
                f"{parser} string:\n{tail}")
        return proc.stdout
    finally:
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    print(f"prettier {PRETTIER_VERSION}  (npx: {shutil.which('npx') or 'NOT FOUND'})")
