#!/usr/bin/env python3
"""Let a verifier rewrite one of its own pinned literals, and show the diff.

    import reseed_util
    reseed_util.rewrite(__file__, "EXPECTED", repr(17))
    reseed_util.rewrite(__file__, "PINNED", reseed_util.format_dict(flat))

WHY THIS EXISTS
---------------
Several verifiers pin a literal on purpose - DO-NOT-BREAK's "a count going
DOWN fails too; an improvement is welcome and must be declared" - and until
2026-08-23 a deliberate change meant running the script with --show, reading
the new table off the terminal and pasting it over the old one by hand. That
is archaeology, and the hand-paste is where a comment or a trailing comma goes
wrong. `--reseed` on those scripts now calls rewrite(): it locates the
top-level assignment by name with the `ast` module, replaces exactly those
source lines with the new literal, writes the file, and prints a unified diff
so the change is reviewed rather than trusted. Nothing else in the file moves.

The literal being rewritten must not carry comments INSIDE it - they would be
lost. Each reseedable table keeps its commentary above the assignment, and
says so.

Standard library only.
"""

from __future__ import annotations

import ast
import difflib
import json
import pathlib
import sys


def locate(source: str, name: str) -> tuple[int, int]:
    """(first_line, last_line), 1-based inclusive, of `NAME = <literal>`."""
    tree = ast.parse(source)
    for node in tree.body:
        if (isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == name):
            return node.lineno, node.end_lineno
        if (isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == name):
            return node.lineno, node.end_lineno
    raise SystemExit(f"reseed: no top-level assignment to {name}")


def rewrite(path, name: str, new_literal: str, *, annotation: str = "") -> bool:
    """Replace `NAME = ...` in `path` with `NAME = {new_literal}`.

    `new_literal` is source text (use repr(), or format_dict() below, so the
    result is valid Python). Returns True if the file changed. Prints the diff
    either way, so a no-op reseed says so.
    """
    path = pathlib.Path(path)
    before = path.read_text(encoding="utf-8")
    first, last = locate(before, name)
    lines = before.split("\n")
    head = f"{name}{annotation} = "
    new_lines = (head + new_literal).split("\n")
    after_lines = lines[: first - 1] + new_lines + lines[last:]
    after = "\n".join(after_lines)
    # Prove the result still parses before writing anything.
    ast.parse(after)
    diff = list(difflib.unified_diff(
        before.split("\n"), after.split("\n"),
        fromfile=f"{path.name} (before)", tofile=f"{path.name} (reseeded)",
        lineterm="", n=2))
    if not diff:
        print(f"reseed: {name} in {path.name} is already current; nothing written")
        return False
    path.write_text(after, encoding="utf-8")
    print(f"reseed: rewrote {name} in {path.name}:")
    for line in diff:
        print(f"  {line}")
    return True


def literal(v) -> str:
    """One value as Python source. Strings get double quotes (json.dumps, so
    the reseeded file matches the repo's existing style rather than repr's
    single quotes); everything else is repr()."""
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    return repr(v)


def format_dict(d: dict, indent: int = 4) -> str:
    """A dict literal, one `key: value,` per line, keys in the given order."""
    pad = " " * indent
    body = "".join(f"{pad}{literal(k)}: {literal(v)},\n" for k, v in d.items())
    return "{\n" + body + "}"


def format_tuple_dict(d: dict, indent: int = 4, width: int = 16) -> str:
    """As format_dict, for a dict whose values are tuples, keys left-aligned."""
    pad = " " * indent
    body = "".join(f"{pad}{literal(k) + ':':<{width}} {v!r},\n"
                   for k, v in d.items())
    return "{\n" + body + "}"


if __name__ == "__main__":
    print(__doc__)
    sys.exit(0)
