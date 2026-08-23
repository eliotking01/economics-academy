#!/usr/bin/env python3
"""Scaffold everything a new revision-notes topic needs, except the prose.

    python3 scripts/new_topic.py <board> <spec-code> "<Title>"          # dry run
    python3 scripts/new_topic.py <board> <spec-code> "<Title>" --apply  # write

    <board>      a board key from boards.json ("edexcel-a" or "aqa") or a
                 notes directory ("edexcel-theme-2", "aqa-a2-micro")
    <spec-code>  dotted, e.g. 1.2.11 - the first digit picks the group
                 (Theme 1 / AQA micro) and the first two parts pick the unit
    <Title>      the H1, in Title Case as it should appear on the page

WHAT IT WRITES (with --apply; the dry run prints every file and the diff)
-------------------------------------------------------------------------
  notes-data/topics/<dir>/<slug>.json   the page record, copied from the
                                        nearest sibling with every head field
                                        that names the topic rewritten: path,
                                        title (seo/tools/notes_titles.py's
                                        formula), canonical, og/twitter,
                                        the LearningResource and BreadcrumbList
                                        nodes, today's dates
  notes-data/topics/<dir>/<slug>.html   a stub slice: breadcrumb, <h1>,
                                        spec-alert, ONE placeholder section.
                                        Enough for build_notes_pages.py and
                                        the verifiers to accept the page once
                                        its questions-data record exists (the
                                        generated tail needs it); the prose
                                        is yours
  notes-data/hubs/<dir>.html            one <li> in the unit's topic list, in
                                        spec order, and the unit's "N topics"
                                        count bumped - so notes_sequence.py
                                        puts the page in the prev/next chain
  boards-data/boards.json               expectedTopics + 1 for the board -
                                        the one place a count is declared

Then it prints the checklist of what remains manual. It never writes a
published page: that is `python3 scripts/build.py`, after you have checked the
scaffold.

WHAT IT WILL NOT DO
-------------------
A new UNIT (a spec code whose first two parts have no panel on the hub yet)
is refused: the hub panel has a heading, a blurb and a jump-row entry, all of
which are wording, and wording is written by hand. Add the unit panel to the
hub slice first, then run this for its first topic.

A spec code or slug that already exists is refused. Dry run by default, like
every other writer in scripts/.

Standard library only.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import difflib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "seo" / "tools"))
import board_data  # noqa: E402
import notes_sequence  # noqa: E402
import notes_titles  # noqa: E402

SITE = "https://economicsacademy.co.uk"
TOPICS = ROOT / "notes-data" / "topics"
HUBS = ROOT / "notes-data" / "hubs"
BOARDS_JSON = ROOT / "boards-data" / "boards.json"


# ----------------------------------------------------------------- helpers

def kebab(title: str) -> str:
    s = title.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def spec_key(spec: str) -> tuple[int, ...]:
    return tuple(int(p) for p in spec.split("."))


def slug_spec(slug: str) -> str:
    """'1-2-11-foo-bar' -> '1.2.11'."""
    m = re.match(r"^(\d+)-(\d+)-(\d+)-", slug)
    if not m:
        raise ValueError(slug)
    return ".".join(m.groups())


def resolve(board_arg: str, spec: str):
    """(board_key, board, group) for the argument and spec code."""
    boards = board_data.load()
    if board_arg in boards:
        board_key, board = board_arg, boards[board_arg]
        idx = spec_key(spec)[0] - 1
        if not 0 <= idx < len(board["groups"]):
            raise SystemExit(f"{spec}: no group {idx + 1} on {board_key} - "
                             f"it has {len(board['groups'])}")
        group = board["groups"][idx]
    else:
        hit = [(k, b, g) for k, b in boards.items() for g in b["groups"]
               if g["notesDir"] == board_arg]
        if not hit:
            raise SystemExit(f"{board_arg!r} is neither a board key "
                             f"{sorted(boards)} nor a notes directory")
        board_key, board, group = hit[0]
    # Every existing sibling in the directory starts with the same first
    # digit; a new topic must too, or it is in the wrong group.
    digits = {slug_spec(p.stem).split(".")[0]
              for p in (TOPICS / group["notesDir"]).glob("*.json")}
    if digits and spec.split(".")[0] not in digits:
        raise SystemExit(f"{spec} does not start with {sorted(digits)} like "
                         f"every topic in {group['notesDir']}/")
    return board_key, board, group


def sibling_for(notes_dir: str, spec: str) -> pathlib.Path:
    """The nearest existing topic before the new one in spec order, else the
    first one after it - the record and slice the scaffold copies from."""
    records = sorted((TOPICS / notes_dir).glob("*.json"),
                     key=lambda p: spec_key(slug_spec(p.stem)))
    before = [p for p in records if spec_key(slug_spec(p.stem)) < spec_key(spec)]
    return before[-1] if before else records[0]


# ----------------------------------------------------------------- record

def make_record(sib: dict, *, board, group, spec, title, slug, notes_dir,
                today: str) -> dict:
    rec = copy.deepcopy(sib)
    path = f"revision-notes/{notes_dir}/{slug}.html"
    url = f"{SITE}/{path}"
    short = board["names"]["short"]          # "Edexcel" / "AQA"
    title_s, _ = notes_titles.title_for(short, slug, title, spec)
    # The description's "Covers ..." clause is wording about the page and is
    # written by hand; rewrite_notes_meta.py re-runs the formula once it is.
    where = f"({spec})" if short == "Edexcel" else group["label"].lower().split()[0]
    desc = (f"{title} for {short} A-Level Economics {where}. "
            f"Covers TODO, TODO and TODO.")
    h = rec["head"]
    rec["path"] = path
    h["title"] = title_s
    h["description"] = desc
    h["canonical"] = url
    if "og" in h:
        h["og"]["url"] = url
        h["og"]["title"] = title_s
        h["og"]["description"] = desc
    if "twitter" in h:
        h["twitter"]["title"] = title_s
        h["twitter"]["description"] = desc
    for node in h.get("jsonldBeforeIcons", []) + h.get("jsonldAfterStyles", []):
        if node.get("@type") == "LearningResource":
            node["name"] = title
            node["description"] = (f"Free {short} A-Level Economics revision "
                                   f"notes on {title} - TODO.")
            node["url"] = url
            node["datePublished"] = today
            node["dateModified"] = today
            if isinstance(node.get("about"), dict):
                node["about"]["name"] = title
            ea = node.get("educationalAlignment")
            if isinstance(ea, dict) and "targetName" in ea:
                sib_spec = slug_spec(pathlib.Path(sib["path"]).stem)
                ea["targetName"] = ea["targetName"].replace(sib_spec, spec)
        if node.get("@type") == "BreadcrumbList":
            last = node["itemListElement"][-1]
            last["name"] = f"{spec} {title}"
            if "item" in last:
                last["item"] = url
    return rec


# ----------------------------------------------------------------- slice

def make_slice(sib_html: str, *, board, spec, title, slug, notes_dir) -> str:
    """A stub slice built from the sibling's own skeleton.

    Keeps, byte for byte where it can: the breadcrumb (last crumb rewritten)
    and the notes-container opening and close. Replaces the sibling's
    sections with one placeholder section and its spec-alert text with a
    TODO. Nothing after the last section is copied: since the 2026-08-23 tail
    redesign a slice ENDS at its last </section> (plus, on the Edexcel pages
    that carry diagrams, one diagram-gallery paragraph - add that by hand
    when the page has a diagram), and everything below it - related topics,
    quiz, flashcards, past-paper questions, author, services - is generated
    by scripts/notes_extras.py from data.
    """
    short = board["names"]["short"]
    # 1. up to and including the breadcrumb, with the last crumb rewritten
    m = re.search(r"(<nav class=\"breadcrumb\".*?)(<span\s*>[^<]*</span\s*>|<span>[^<]*</span>)"
                  r"(\s*</nav>)", sib_html, re.S)
    if not m:
        raise SystemExit("sibling slice has no breadcrumb to copy")
    head = sib_html[: m.start(2)] + f"<span>{spec} {title}</span>" + m.group(3)
    # 2. the container opening and the indent the sibling uses
    cont = sib_html.find('<div class="notes-container">', m.end())
    if cont == -1:
        raise SystemExit("sibling slice has no div.notes-container")
    line_start = sib_html.rfind("\n", 0, cont) + 1
    pad = sib_html[line_start:cont]
    p2 = pad + "  "
    # 3. the container close, exactly as the sibling ends
    close_at = sib_html.rfind("</div>")
    closing = sib_html[sib_html.rfind("\n", 0, close_at) + 1:]
    body = (
        f"{sib_html[m.end(3):cont]}"
        f'<div class="notes-container">\n'
        f'{p2}<header class="major">\n'
        f'{p2}  <h1>{title}</h1>\n'
        f'{p2}</header>\n'
        f'\n'
        f'{p2}<div class="spec-alert">\n'
        f'{p2}  <strong>Specification Coverage:</strong> {short} unit {spec} -\n'
        f'{p2}  {title}. TODO: one or two sentences on what students should be\n'
        f'{p2}  able to do.\n'
        f'{p2}</div>\n'
        f'\n'
        f'{p2}<section>\n'
        f'{p2}  <h2>TODO first section heading</h2>\n'
        f'{p2}  <p>TODO. Write the notes here; see revision-notes/CLAUDE.md for\n'
        f'{p2}  the component library.</p>\n'
        f'{p2}</section>\n'
        f'{closing}'
    )
    return head + body


# ----------------------------------------------------------------- hub

COUNT_RE = re.compile(r'<span class="resource-index-count">(\d+) topics?</span>')


def hub_with_link(hub_html: str, *, notes_dir, spec, title, slug) -> str:
    """The hub slice with one more <li>, in spec order, and the unit count
    bumped. Refuses a unit that has no panel yet."""
    unit = ".".join(spec.split(".")[:2])
    href = f"/revision-notes/{notes_dir}/{slug}.html"
    if href in hub_html:
        raise SystemExit(f"{notes_dir}.html already links {href}")
    # Every existing <li> in the hub, with its code and span.
    LI = re.compile(r"([ \t]*)<li>\s*<a href=\"/revision-notes/" + re.escape(notes_dir)
                    + r"/([^\"]+)\.html\"\s*>\s*<span class=\"resource-index-code\">"
                    r"([\d.]+)</span>.*?</li>", re.S)
    items = [(m, m.group(3)) for m in LI.finditer(hub_html)]
    in_unit = [(m, code) for m, code in items
               if ".".join(code.split(".")[:2]) == unit]
    if not in_unit:
        raise SystemExit(
            f"unit {unit} has no panel on notes-data/hubs/{notes_dir}.html - a "
            f"new unit needs a heading, a blurb and a jump-row entry, which is "
            f"wording. Add the panel by hand, then re-run for its first topic.")
    before = [(m, c) for m, c in in_unit if spec_key(c) < spec_key(spec)]
    indent = in_unit[0][0].group(1)
    li = (f"{indent}<li>\n"
          f"{indent}  <a href=\"{href}\"\n"
          f"{indent}    ><span class=\"resource-index-code\">{spec}</span>\n"
          f"{indent}    <span class=\"resource-index-title\">{title}</span></a\n"
          f"{indent}  >\n"
          f"{indent}</li>\n")
    if before:
        at = before[-1][0].end()
        # insert after the newline that ends that <li>
        nl = hub_html.find("\n", at) + 1
        out = hub_html[:nl] + li + hub_html[nl:]
        anchor = before[-1][0].start()
    else:
        first = in_unit[0][0]
        out = hub_html[: first.start()] + li + hub_html[first.start():]
        anchor = first.start()
    # Bump the nearest "N topics" above the unit's list.
    counts = [m for m in COUNT_RE.finditer(out) if m.start() < anchor]
    if not counts:
        raise SystemExit(f"no 'N topics' count found above unit {unit} on the hub")
    c = counts[-1]
    n = int(c.group(1)) + 1
    out = out[: c.start()] + f'<span class="resource-index-count">{n} topics</span>' + out[c.end():]
    return out


# ----------------------------------------------------------------- boards.json

def boards_json_bumped(text: str, board_key: str) -> str:
    """expectedTopics + 1 for one board, edited as text so the file's layout
    and commentary keys survive byte for byte everywhere else."""
    start = text.index(f'"{board_key}": {{')
    m = re.compile(r'"expectedTopics": (\d+)').search(text, start)
    if not m:
        raise SystemExit(f"no expectedTopics under {board_key} in boards.json")
    return text[: m.start(1)] + str(int(m.group(1)) + 1) + text[m.end(1):]


# ----------------------------------------------------------------- main

def show_diff(label: str, before: str, after: str, limit: int = 60) -> None:
    diff = list(difflib.unified_diff(before.splitlines(), after.splitlines(),
                                     fromfile=f"{label} (before)",
                                     tofile=f"{label} (after)", lineterm="", n=2))
    print(f"\n--- {label}")
    for line in diff[:limit]:
        print(f"    {line}")
    if len(diff) > limit:
        print(f"    ... ({len(diff) - limit} more lines)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("board", help="board key (edexcel-a, aqa) or notes dir")
    ap.add_argument("spec", help="dotted spec code, e.g. 1.2.11")
    ap.add_argument("title", help="the H1, Title Case")
    ap.add_argument("--apply", action="store_true",
                    help="write the files (default: print the plan)")
    args = ap.parse_args()

    if not re.fullmatch(r"\d+\.\d+\.\d+", args.spec):
        raise SystemExit(f"spec code must be three dotted numbers, got {args.spec!r}")
    board_key, board, group = resolve(args.board, args.spec)
    notes_dir = group["notesDir"]
    slug = f"{args.spec.replace('.', '-')}-{kebab(args.title)}"
    today = dt.date.today().isoformat()

    rec_path = TOPICS / notes_dir / f"{slug}.json"
    html_path = TOPICS / notes_dir / f"{slug}.html"
    hub_path = HUBS / f"{notes_dir}.html"
    for existing in (TOPICS / notes_dir).glob(f"{args.spec.replace('.', '-')}-*.json"):
        raise SystemExit(f"{args.spec} already exists: {existing.relative_to(ROOT)}")
    if rec_path.exists() or html_path.exists():
        raise SystemExit(f"{slug} already exists in {notes_dir}/")

    sib_json = sibling_for(notes_dir, args.spec)
    sib = json.loads(sib_json.read_text(encoding="utf-8"))
    sib_html = sib_json.with_suffix(".html").read_text(encoding="utf-8")

    record = make_record(sib, board=board, group=group, spec=args.spec,
                         title=args.title, slug=slug, notes_dir=notes_dir,
                         today=today)
    record_text = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    slice_text = make_slice(sib_html, board=board, spec=args.spec,
                            title=args.title, slug=slug, notes_dir=notes_dir)
    hub_before = hub_path.read_text(encoding="utf-8")
    hub_after = hub_with_link(hub_before, notes_dir=notes_dir, spec=args.spec,
                              title=args.title, slug=slug)
    boards_before = BOARDS_JSON.read_text(encoding="utf-8")
    boards_after = boards_json_bumped(boards_before, board_key)

    verb = "WRITE" if args.apply else "WOULD WRITE"
    print(f"new topic: {board['names']['display']} {args.spec} \"{args.title}\"")
    print(f"  group     {group['label']}  ({notes_dir}/)")
    print(f"  slug      {slug}")
    print(f"  page      /revision-notes/{notes_dir}/{slug}.html")
    print(f"  template  {sib_json.relative_to(ROOT)} (nearest sibling)")
    print(f"  title     {record['head']['title']}")
    print()
    print(f"  {verb}  {rec_path.relative_to(ROOT)}   ({len(record_text)} bytes, new)")
    print(f"  {verb}  {html_path.relative_to(ROOT)}   ({len(slice_text)} bytes, new)")
    print(f"  {verb}  {hub_path.relative_to(ROOT)}   (+1 <li>, unit count bumped)")
    print(f"  {verb}  boards-data/boards.json   ({board_key}.expectedTopics "
          f"{board['expectedTopics']} -> {board['expectedTopics'] + 1})")

    if not args.apply:
        print("\n=== the new slice ===")
        for line in slice_text.splitlines():
            print(f"    {line}")
        show_diff(f"notes-data/hubs/{notes_dir}.html", hub_before, hub_after)
        show_diff("boards-data/boards.json", boards_before, boards_after)
        print("\n=== record head, the fields that name the topic ===")
        h = record["head"]
        for k in ("title", "description", "canonical"):
            print(f"    {k}: {h[k]}")
        print(f"    LearningResource.name: {h['jsonldBeforeIcons'][0]['name']}")
        print(f"    BreadcrumbList[-1]: {h['jsonldAfterStyles'][0]['itemListElement'][-1]}")

    if args.apply:
        rec_path.write_text(record_text, encoding="utf-8")
        html_path.write_text(slice_text, encoding="utf-8")
        hub_path.write_text(hub_after, encoding="utf-8")
        BOARDS_JSON.write_text(boards_after, encoding="utf-8")
        print("\nwritten.")
        # Prove the sequence sees it before handing over: the hub's links are
        # what notes_sequence.py derives the prev/next chain from.
        seen = {s for s, _ in notes_sequence.hub_topics(notes_dir)}
        if slug not in seen:
            print("WARNING: notes_sequence.hub_topics() does not see the new "
                  "topic - check the hub edit before building")
        else:
            print(f"notes_sequence.py sees {slug} in {notes_dir} "
                  f"({len(seen)} topics on that hub)")
    else:
        print("\ndry run - nothing written. Re-run with --apply to write the four files.")

    print(f"""
=== still manual, in this order ===
 1. Write the notes: notes-data/topics/{notes_dir}/{slug}.html - replace the
    TODO section(s) and the spec-alert sentence. Component library:
    revision-notes/CLAUDE.md. Keep the slice a byte-exact record of the page.
 2. Finish the head in {slug}.json: the description's "Covers ..." clause
    (seo/tools/rewrite_notes_meta.py re-runs the title/description formula
    once the page has its H2s) and the LearningResource description.
 3. Twin row: scripts/notes_twins.py is a written-down table - add the
    (board, slug) pair for this topic's counterpart on the other board, or
    leave it unpaired on purpose (verify_seo.py assertion 13 permits only
    the pairs the table names).
 4. questions-data/{notes_dir}/{args.spec.replace('.', '-')}.json - the practice
    questions. build_notes_pages.py needs it for the page's generated tail
    (the "Practice questions" panel is derived from it) and
    build_past_paper_taxonomy.py asserts questions-data has exactly
    expectedTopics records per board, so build.py FAILS at step 1 until
    this exists. questions-data/CLAUDE.md "Adding one" has the steps. The
    "Carry on with this topic" panels - quiz, flashcards, past-paper
    questions - then appear on the page by themselves; nothing to append.
 5. Optional: flashcards (flashcards-data/CLAUDE.md "Adding one"); tag
    past-paper questions to the slug in past-paper-questions-data/tags.json
    and the page's past-paper line updates itself on the next build.
 6. python3 scripts/build.py, then the suite (/verify). verify_page_shell.py
    and verify_notes_sequence.py derive their counts from boards.json, so
    nothing in a verifier needs editing; verify_boards.py --reseed if it
    complains about expectedTopics (PINNED restates boards.json on purpose).
 7. Commit, then python3 scripts/build.py --sitemap and commit that.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
