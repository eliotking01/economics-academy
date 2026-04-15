#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent

TITLE_RE = re.compile(r"^Theme\s+([\d.]+):\s+(.+?)\s*$")
SECTION_RE = re.compile(r"^\s*(\d+)\s*\\?\.\s+(.+?)\s*$")
ORDERED_RE = re.compile(r"^(\s*)(\d+)\s*\\?\.\s+(.*)$")
UNORDERED_RE = re.compile(r"^(\s*)-\s+(.*)$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")
DIAGRAM_RE = re.compile(r"^\s*\\?\*?\(?(Hand-draw Diagram[^)]*|Hand-draw Diagram.*?)\)?\\?\*?\s*\\?\s*$", re.IGNORECASE)
WHOLE_BOLD_RE = re.compile(r"^\s*\*\*(.+?)\*\*\s*\\?\s*$")
STRONG_LABEL_RE = re.compile(r"^\s*\*\*([^*]+?)\*\*:\s*(.+?)\s*$")
PLAIN_LABEL_RE = re.compile(r"^\s*([A-Z][A-Za-z /&()'-]{1,40}):\s*(.+?)\s*$")
FLEX_LABEL_RE = re.compile(r"^\s*(?:\*\*)?([^:*]+?)(?:\*\*)?:\s*(.+?)\s*$")

MATHJAX_HINT_RE = re.compile(
    r"Hand-draw Diagram|\\\(|\\\[|\bFormula\b|\bMC\s*=\s*MR\b|\bMR\s*=\s*0\b|\bQm\b|\bQopt\b|\bPmax\b|\bPmin\b|\bMSC\b|\bMPC\b|\bMSB\b|\bMPB\b|½|<sub>|</sub>",
    re.IGNORECASE,
)

KEY_DEFINITION_LABELS = {
    "definition",
    "externality",
    "market failure",
    "government failure",
    "non-excludability",
    "non-rivalry",
    "adverse selection",
    "moral hazard",
}

SPEC_STOP_TERMS = {
    "definition",
    "definitions",
    "example",
    "examples",
    "purpose",
    "purposes",
    "effect",
    "effects",
    "mechanism",
    "mechanisms",
    "consequence",
    "consequences",
    "result",
    "results",
    "rule",
    "rules",
    "why",
    "what it is",
    "types",
    "new equilibrium",
    "diagram analysis",
    "key takeaways",
    "exam focus",
    "exam preparation",
    "key exam tips",
}

SPEC_BAD_TERM_RE = re.compile(
    r"^(?:P\d*|Q\d*|Pe|Qe|Pc|Pp|Pmax|Pmin|Qm|Qopt|MC|MR|AR|AC|MPC|MSC|MPB|MSB|S\d*|D|and|before|after)$",
    re.IGNORECASE,
)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"&", " and ", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def clean_line(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = text.replace("\\*", "*").replace("\\.", ".")
    text = text.rstrip("\\").strip()
    return text


def format_inline(text: str) -> str:
    text = clean_line(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def detect_mathjax(raw_text: str) -> bool:
    return bool(MATHJAX_HINT_RE.search(raw_text))


def is_blank(line: str) -> bool:
    return not line.strip()


def is_comment(line: str) -> bool:
    return line.strip().startswith("<!--")


def is_exam_heading(text: str) -> bool:
    return "exam focus" in text.lower() or "exam preparation" in text.lower()


def get_theme_title(subject: str, theme: str) -> str:
    index_path = ROOT / "revision-notes" / f"{subject}-theme-{theme}" / "index.html"
    if not index_path.exists():
        return f"Edexcel Theme {theme}"

    text = index_path.read_text(encoding="utf-8")
    match = re.search(r"<h2>\s*(Edexcel Theme .*?)\s*</h2>", text, re.DOTALL)
    if not match:
        return f"Edexcel Theme {theme}"
    return " ".join(match.group(1).split())


def dedupe_keep_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def normalise_phrase(text: str) -> str:
    text = clean_line(re.sub(r"<[^>]+>", "", text))
    text = re.sub(r"\s+", " ", text).strip(" .;,:-")
    return text


def markdown_to_text(text: str) -> str:
    text = clean_line(text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.replace("**", "").replace("__", "").replace("*", "").replace("_", "")
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\\([()[\].*])", r"\1", text)
    return normalise_phrase(text)


def strip_list_prefix(text: str) -> str:
    text = clean_line(text)
    text = re.sub(r"^\s*-\s+", "", text)
    text = re.sub(r"^\s*\d+\s*\\?\.\s+", "", text)
    return text.strip()


def spec_source_lines(lines: list[str]) -> list[str]:
    source: list[str] = []
    for line in lines:
        if DIAGRAM_RE.match(clean_line(line)):
            break
        source.append(line)
    return source


def merge_wrapped_spec_lines(lines: list[str]) -> list[str]:
    merged: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if buffer:
            merged.append(" ".join(part.strip().rstrip("\\") for part in buffer if part.strip()))
            buffer = []

    for index, line in enumerate(lines):
        cleaned = clean_line(line)
        if not cleaned or is_comment(cleaned):
            flush()
            continue
        if DIAGRAM_RE.match(cleaned) or is_table_start(lines, index) or match_list_item(line):
            flush()
            merged.append(line)
            continue
        buffer.append(line)

    flush()
    return merged


def extract_spec_terms(lines: list[str]) -> list[str]:
    terms: list[str] = []

    for line in lines:
        cleaned = clean_line(line)
        if not cleaned or is_comment(cleaned):
            continue

        strong_label = STRONG_LABEL_RE.match(cleaned)
        if strong_label:
            label = normalise_phrase(strong_label.group(1))
            if label and label.lower() not in SPEC_STOP_TERMS and len(label) <= 50:
                terms.append(label)

        plain_label = PLAIN_LABEL_RE.match(cleaned)
        if plain_label:
            label = normalise_phrase(plain_label.group(1))
            if label and label.lower() not in SPEC_STOP_TERMS and len(label) <= 50:
                terms.append(label)

        for match in re.finditer(r"\*\*(.+?)\*\*", cleaned):
            bold = normalise_phrase(match.group(1))
            if (
                bold
                and bold.lower() not in SPEC_STOP_TERMS
                and 2 <= len(bold) <= 60
                and len(bold.split()) <= 5
                and not SPEC_BAD_TERM_RE.match(bold)
                and not re.fullmatch(r"[A-Z0-9()<>/=+\- ]+", bold)
            ):
                terms.append(bold)

    return dedupe_keep_order(terms)


def join_list_naturally(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def heading_to_phrase(heading: str) -> str:
    heading = clean_line(heading)
    lower = heading.lower()

    replacements = [
        ("what is ", ""),
        ("the problem of ", ""),
        ("the free market problem & ", ""),
        ("the free market problem and ", ""),
        ("exam focus: ", ""),
    ]
    for old, new in replacements:
        if lower.startswith(old):
            heading = heading[len(old) :]
            lower = heading.lower()
            break

    return heading[0].lower() + heading[1:] if heading else heading


def extract_bullet_leads(lines: list[str], limit: int = 4) -> list[str]:
    bullets: list[str] = []
    for line in lines:
        match = match_list_item(line)
        if not match:
            continue
        text = markdown_to_text(match[2])
        strong_label = STRONG_LABEL_RE.match(strip_list_prefix(line))
        if strong_label:
            label = markdown_to_text(strong_label.group(1))
            if label and label.lower() not in SPEC_STOP_TERMS:
                bullets.append(label)
                continue
        plain_label = PLAIN_LABEL_RE.match(strip_list_prefix(line))
        if plain_label:
            label = markdown_to_text(plain_label.group(1))
            if label and label.lower() not in SPEC_STOP_TERMS:
                bullets.append(label)
                continue
        if text:
            lead = text.split(".")[0]
            lead_key = lead.strip(" :;,-").lower()
            if lead_key not in SPEC_STOP_TERMS and not SPEC_BAD_TERM_RE.match(lead):
                bullets.append(lead)
        if len(bullets) >= limit:
            break
    return dedupe_keep_order(bullets[:limit])


def extract_meaningful_summary(lines: list[str]) -> str | None:
    for line in lines:
        cleaned = clean_line(line)
        if not cleaned or is_comment(cleaned):
            continue
        if DIAGRAM_RE.match(cleaned):
            continue
        match = match_list_item(cleaned)
        if match:
            text = markdown_to_text(match[2])
        else:
            text = markdown_to_text(cleaned)

        label_match = FLEX_LABEL_RE.match(strip_list_prefix(cleaned))
        if label_match:
            label = markdown_to_text(label_match.group(1)).lower()
            value = markdown_to_text(label_match.group(2))
            if label in {"purpose", "effect", "mechanism", "consequence", "result", "why", "objective"} and value:
                return value
            if label == "example":
                continue

        plain_label = PLAIN_LABEL_RE.match(strip_list_prefix(cleaned))
        if plain_label:
            label = markdown_to_text(plain_label.group(1)).lower()
            value = markdown_to_text(plain_label.group(2))
            if label in {"purpose", "effect", "mechanism", "consequence", "result", "why", "objective"} and value:
                return value
            if label == "example":
                continue

        if text.lower().startswith("example:"):
            continue
        if text and not re.match(r"^(draw|mark|label|show|shade|highlight)\b", text.lower()):
            return text
    return None


def summarise_section_for_spec(heading: str, lines: list[str]) -> str | None:
    lines = merge_wrapped_spec_lines(spec_source_lines(lines))
    heading_phrase = heading_to_phrase(heading)
    heading_lower = heading_phrase.lower()
    terms = extract_spec_terms(lines)
    bullet_leads = extract_bullet_leads(lines)
    summary = extract_meaningful_summary(lines)

    if summary and summary.endswith("to"):
        summary = None

    if "definition" in heading_lower:
        chosen = terms[:4]
        if chosen:
            return f"the key definitions and concepts around {join_list_naturally(chosen)}"
        return f"the key definitions in {heading_phrase}"

    if any(keyword in heading_lower for keyword in ["reason", "cause", "factor", "determinant", "component", "characteristic", "types", "objectives"]):
        chosen = bullet_leads[:4] or terms[:4]
        if chosen:
            return f"{heading_phrase}, including {join_list_naturally(chosen)}"
        return heading_phrase

    if any(keyword in heading_lower for keyword in ["problem", "consequence", "result"]):
        chosen = terms[:4] or bullet_leads[:4]
        if chosen:
            return f"{heading_phrase}, including {join_list_naturally(chosen)}"
        if summary:
            if summary[0].isupper():
                summary = summary[0].lower() + summary[1:]
            return f"{heading_phrase}, including {summary}"
        return heading_phrase

    if any(keyword in heading_lower for keyword in ["intervention", "solution", "strategy", "methods"]):
        chosen = bullet_leads[:4] or terms[:4]
        if chosen:
            return f"{heading_phrase}, including {join_list_naturally(chosen)}"
        if summary:
            return f"{heading_phrase}, especially {summary[0].lower() + summary[1:]}"
        return heading_phrase

    if "government provision" in heading_lower and summary and "taxation" in summary.lower():
        return f"{heading_phrase}, including public funding through taxation"

    if summary and summary.lower().startswith("to ") and terms:
        return f"{heading_phrase}, including its purpose and {join_list_naturally(terms[:2])}"

    if terms and summary and len(summary.split()) > 16:
        return f"{heading_phrase}, including {join_list_naturally(terms[:4])}"

    if summary:
        if summary[0].isupper():
            summary = summary[0].lower() + summary[1:]
        return f"{heading_phrase}, including {summary}"

    chosen = bullet_leads[:4] or terms[:4]
    if chosen:
        return f"{heading_phrase}, including {join_list_naturally(chosen)}"
    return heading_phrase


def build_specification_coverage(code: str, title: str, sections: list[tuple[str, list[str]]]) -> str:
    non_exam_sections = [(heading, lines) for heading, lines in sections if heading != "Exam Preparation"]
    clauses: list[str] = []

    for heading, lines in non_exam_sections[:4]:
        clause = summarise_section_for_spec(heading, lines)
        if clause:
            clauses.append(clause)

    clauses = dedupe_keep_order(clauses)
    if clauses:
        joined = "; ".join(clauses[:-1])
        if len(clauses) == 1:
            body = clauses[0]
        elif len(clauses) == 2:
            body = f"{clauses[0]}, and {clauses[1]}"
        else:
            body = f"{joined}; and {clauses[-1]}"
        return (
            f"Edexcel unit {code} - {title}. Students should be able to understand "
            f"and explain {body}."
        )

    return (
        f"Edexcel unit {code} - {title}. Students should be able to understand "
        f"the key ideas, analysis, and evaluation points needed for this topic."
    )


def match_list_item(line: str):
    ordered = ORDERED_RE.match(line)
    if ordered:
        return ("ol", len(ordered.group(1).replace("\t", "    ")), ordered.group(3).strip())
    unordered = UNORDERED_RE.match(line)
    if unordered:
        return ("ul", len(unordered.group(1).replace("\t", "    ")), unordered.group(2).strip())
    return None


def is_table_start(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    if "|" not in lines[index]:
        return False
    return bool(TABLE_SEPARATOR_RE.match(lines[index + 1]))


def next_content_index(lines: list[str], index: int) -> int:
    i = index
    while i < len(lines) and (is_blank(lines[i]) or is_comment(lines[i])):
        i += 1
    return i


def render_table(table_lines: list[str]) -> str:
    rows = [line.strip() for line in table_lines if line.strip()]
    header = [format_inline(cell.strip()) for cell in rows[0].strip("|").split("|")]
    body_rows = []
    for row in rows[2:]:
        cells = [format_inline(cell.strip()) for cell in row.strip("|").split("|")]
        body_rows.append(cells)

    parts = [
        '<div class="table-container">',
        '<table class="concept-table">',
        "<thead>",
        "<tr>",
    ]
    for cell in header:
        parts.append(f"<th>{cell}</th>")
    parts.extend(["</tr>", "</thead>"])
    if body_rows:
        parts.append("<tbody>")
        for row in body_rows:
            parts.append("<tr>")
            for cell in row:
                parts.append(f"<td>{cell}</td>")
            parts.append("</tr>")
        parts.append("</tbody>")
    parts.extend(["</table>", "</div>"])
    return "\n".join(parts)


def render_list(lines: list[str], start: int) -> tuple[str, int]:
    first = match_list_item(lines[start])
    if not first:
        raise ValueError("render_list called on a non-list line")

    list_type, base_indent, _ = first
    tag = "ol" if list_type == "ol" else "ul"
    parts = [f"<{tag}>"]
    current_item: list[str] | None = None
    i = start

    while i < len(lines):
        if is_comment(lines[i]):
            i += 1
            continue

        match = match_list_item(lines[i])
        if not match:
            if is_blank(lines[i]):
                j = next_content_index(lines, i + 1)
                if j < len(lines):
                    nested = match_list_item(lines[j])
                    if nested and nested[1] >= base_indent:
                        i = j
                        continue
                break
            if current_item is not None:
                current_item.append(format_inline(lines[i].strip()))
                i += 1
                continue
            break

        item_type, indent, text = match
        if indent < base_indent or item_type != list_type:
            break
        if indent > base_indent:
            nested_html, i = render_list(lines, i)
            if current_item is None:
                current_item = [nested_html]
            else:
                current_item.append(nested_html)
            continue

        if current_item is not None:
            parts.append(f"<li>{' '.join(current_item)}</li>")
        current_item = [format_inline(text)]
        i += 1

    if current_item is not None:
        parts.append(f"<li>{' '.join(current_item)}</li>")
    parts.append(f"</{tag}>")
    return "\n".join(parts), i


def render_paragraph(text: str) -> str:
    text = clean_line(text)
    strong_label = STRONG_LABEL_RE.match(text)
    if strong_label:
        label = strong_label.group(1).strip()
        remainder = format_inline(strong_label.group(2).strip())
        if label.lower() in KEY_DEFINITION_LABELS:
            return f'<p><span class="key-definition">{label}:</span> {remainder}</p>'
        return f"<p><strong>{label}:</strong> {remainder}</p>"

    plain_label = PLAIN_LABEL_RE.match(text)
    if plain_label and plain_label.group(1).lower() in KEY_DEFINITION_LABELS:
        label = plain_label.group(1).strip()
        remainder = format_inline(plain_label.group(2).strip())
        return f'<p><span class="key-definition">{label}:</span> {remainder}</p>'

    return f"<p>{format_inline(text)}</p>"


def render_diagram_placeholder(title: str, instruction_lines: list[str]) -> str:
    title = clean_line(title)
    parts = ['<div class="application">', "<h4>Diagram Placeholder</h4>"]
    parts.append(f"<p>{format_inline(title)}.</p>" if not title.endswith(".") else f"<p>{format_inline(title)}</p>")

    if instruction_lines:
        rendered = render_blocks(instruction_lines)
        if rendered:
            parts.append(rendered)
    parts.append("</div>")
    return "\n".join(parts)


def collect_diagram_block(lines: list[str], start: int) -> tuple[str, int]:
    marker = clean_line(lines[start])
    marker = marker.strip("*").strip("(").strip(")").strip()
    instructions: list[str] = []
    i = start + 1

    while i < len(lines):
        if is_comment(lines[i]):
            i += 1
            continue

        if is_blank(lines[i]):
            j = next_content_index(lines, i + 1)
            if j >= len(lines):
                i = j
                break
            upcoming = clean_line(lines[j])
            if (
                match_list_item(lines[j])
                and match_list_item(lines[j])[0] == "ul"
                and not ORDERED_RE.match(lines[j])
            ):
                break
            if WHOLE_BOLD_RE.match(upcoming) or STRONG_LABEL_RE.match(upcoming):
                break
            if is_table_start(lines, j) or DIAGRAM_RE.match(upcoming):
                break
            instructions.append("")
            i += 1
            continue

        if match_list_item(lines[i]):
            match = match_list_item(lines[i])
            if match and match[0] == "ul" and match[1] == 0:
                break
        instructions.append(lines[i])
        i += 1

    return render_diagram_placeholder(marker, instructions), i


def render_blocks(lines: list[str]) -> str:
    parts: list[str] = []
    i = 0
    while i < len(lines):
        if is_comment(lines[i]) or is_blank(lines[i]):
            i += 1
            continue

        line = lines[i]
        clean = clean_line(line)

        if is_table_start(lines, i):
            table_lines = [lines[i], lines[i + 1]]
            i += 2
            while i < len(lines) and "|" in lines[i] and not is_blank(lines[i]):
                table_lines.append(lines[i])
                i += 1
            parts.append(render_table(table_lines))
            continue

        if DIAGRAM_RE.match(clean):
            html, i = collect_diagram_block(lines, i)
            parts.append(html)
            continue

        whole_bold = WHOLE_BOLD_RE.match(clean)
        if whole_bold:
            label = clean_line(whole_bold.group(1))
            if re.match(r"^[A-Z]\.\s+", label):
                parts.append(f"<h4>{format_inline(re.sub(r'^[A-Z]\.\s+', '', label))}</h4>")
            else:
                parts.append(f"<h4>{format_inline(label)}</h4>")
            i += 1
            continue

        if re.match(r"^[A-Z]\.\s+.+$", clean):
            parts.append(f"<h4>{format_inline(re.sub(r'^[A-Z]\.\s+', '', clean))}</h4>")
            i += 1
            continue

        list_match = match_list_item(line)
        if list_match:
            html, i = render_list(lines, i)
            parts.append(html)
            continue

        paragraph_lines = [clean]
        i += 1
        while i < len(lines):
            if is_comment(lines[i]) or is_blank(lines[i]):
                break
            next_clean = clean_line(lines[i])
            if (
                is_table_start(lines, i)
                or DIAGRAM_RE.match(next_clean)
                or match_list_item(lines[i])
                or WHOLE_BOLD_RE.match(next_clean)
                or re.match(r"^[A-Z]\.\s+.+$", next_clean)
            ):
                break
            paragraph_lines.append(next_clean)
            i += 1
        parts.append(render_paragraph(" ".join(paragraph_lines)))

    return "\n".join(parts)


def render_exam_tip(lines: list[str]) -> str:
    lines = [line for line in lines if not is_comment(line)]
    list_lines = [line for line in lines if not is_blank(line)]
    if not list_lines:
        return '<div class="exam-tip"></div>'

    if any(match_list_item(line) for line in list_lines):
        body = render_blocks(lines)
        return f'<div class="exam-tip">\n{body}\n</div>'

    items: list[str] = []
    current: list[str] = []
    for line in lines:
        if is_blank(line):
            if current:
                items.append(" ".join(clean_line(part) for part in current))
                current = []
            continue
        current.append(line)
    if current:
        items.append(" ".join(clean_line(part) for part in current))

    item_html = "\n".join(f"<li>{format_inline(item)}</li>" for item in items if item.strip())
    return f"<div class=\"exam-tip\">\n<ul>\n{item_html}\n</ul>\n</div>"


def split_sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = clean_line(line)

        if stripped == "Key Exam Tips:":
            if current_heading is not None:
                sections.append((current_heading, current_lines))
            current_heading = "Exam Preparation"
            current_lines = []
            continue

        match = SECTION_RE.match(stripped)
        if match:
            heading = clean_line(match.group(2))
            if is_exam_heading(heading):
                heading = "Exam Preparation"
            if current_heading is not None:
                sections.append((current_heading, current_lines))
            current_heading = heading
            current_lines = []
            continue

        if current_heading is None:
            continue
        current_lines.append(line)

    if current_heading is not None:
        sections.append((current_heading, current_lines))
    return sections


def build_html(
    code: str,
    title: str,
    sections: list[tuple[str, list[str]]],
    include_mathjax: bool,
    subject: str,
) -> str:
    theme = code.split(".")[0]
    output_title = f"{code} {title}"
    breadcrumb_title = output_title
    theme_title = get_theme_title(subject, theme)
    specification_coverage = build_specification_coverage(code, title, sections)

    section_html: list[str] = []
    for heading, lines in sections:
        if heading == "Exam Preparation":
            inner = render_exam_tip(lines)
        else:
            inner = render_blocks(lines)
        section_html.append(
            "\n".join(
                [
                    "<section>",
                    f"<h3>{format_inline(heading)}</h3>",
                    inner,
                    "</section>",
                ]
            )
        )

    mathjax_block = ""
    if include_mathjax:
        mathjax_block = """

    <!-- MathJax Configuration -->
    <script>
      window.MathJax = {
        tex: {
          inlineMath: [
            ["$", "$"],
            ["\\\\(", "\\\\)"],
          ],
          displayMath: [
            ["$$", "$$"],
            ["\\\\[", "\\\\]"],
          ],
          processEscapes: true,
          autoload: {
            color: [],
            ams: ["boldsymbol"],
          },
        },
        options: {
          skipHtmlTags: ["script", "noscript", "style", "textarea", "pre"],
        },
      };
    </script>
    <script
      src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
      async
    ></script>"""

    return f"""<!doctype html>
<html lang="en">
  <head>
    <!-- Google tag (gtag.js) -->
    <script
      async
      src="https://www.googletagmanager.com/gtag/js?id=G-YVCNRW4QH6"
    ></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag() {{
        dataLayer.push(arguments);
      }}
      gtag("js", new Date());

      gtag("config", "G-YVCNRW4QH6");
    </script>
    <meta charset="utf-8" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1, user-scalable=no"
    />
    <title>
      {output_title} | Edexcel A-Level Economics Revision Notes | Economics
      Academy
    </title>
    <meta
      name="description"
      content="Comprehensive revision notes for Edexcel A-Level Economics Theme {code} on {title.lower()}. Generated from raw notes for Economics Academy."
    />
    <link rel="stylesheet" href="/css/main.css" />
    <link rel="stylesheet" href="/css/pages/revision-notes-textbook.css" />
    <link
      href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;1,400&family=Open+Sans:wght@400;600;700&display=swap"
      rel="stylesheet"
    />{mathjax_block}
  </head>
  <body class="homepage is-preload">
    <div id="page-wrapper">
      <!-- Header -->
      <div id="header-placeholder"></div>

      <!-- Main Content -->
      <section id="main" class="revision-notes-content">
        <div class="container">
          <nav class="breadcrumb">
            <a href="/revision-notes/index.html">Revision Notes</a>
            <span class="separator">›</span>
            <a href="/revision-notes/{subject}-theme-{theme}/index.html"
              >{theme_title}</a
            >
            <span class="separator">›</span>
            <span>{breadcrumb_title}</span>
          </nav>
          <div class="notes-container">
            <header class="major">
              <h2>{output_title}</h2>
            </header>

            <div class="spec-alert">
              <strong>Specification Coverage:</strong> {specification_coverage}
            </div>

            {"\n\n".join(section_html)}
          </div>
        </div>
      </section>

      <!-- Footer -->
      <div id="footer-placeholder"></div>
    </div>

    <!-- Scripts -->
    <script src="/js/jquery.min.js"></script>
    <script src="/js/jquery.dropotron.min.js"></script>
    <script src="/js/components/inject-templates.js"></script>
    <script src="/js/browser.min.js"></script>
    <script src="/js/breakpoints.min.js"></script>
    <script src="/js/util.js"></script>
    <script src="/js/main.js"></script>
  </body>
</html>
"""


def resolve_paths(topic: str, subject: str) -> tuple[Path, Path]:
    topic = topic[:-3] if topic.endswith(".md") else topic
    input_path = ROOT / "raw-notes" / subject / f"{topic}.md"
    if not input_path.exists():
        raise FileNotFoundError(f"Raw notes file not found: {input_path}")

    first_line = input_path.read_text(encoding="utf-8").splitlines()[0].strip()
    match = TITLE_RE.match(first_line)
    if not match:
        raise ValueError(f"Could not parse title line in {input_path}")

    code = match.group(1)
    title = match.group(2)
    theme = code.split(".")[0]
    output_dir = ROOT / "revision-notes" / f"{subject}-theme-{theme}"
    output_name = f"{code.replace('.', '-')}-{slugify(title)}.html"
    return input_path, output_dir / output_name


def convert(topic: str, subject: str = "edexcel", dry_run: bool = False) -> Path:
    input_path, output_path = resolve_paths(topic, subject)
    raw_text = input_path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()

    title_match = TITLE_RE.match(lines[0].strip())
    if not title_match:
        raise ValueError(f"Could not parse raw note title: {input_path}")

    code = title_match.group(1)
    title = title_match.group(2)
    sections = split_sections(lines[1:])
    include_mathjax = detect_mathjax(raw_text)
    html = build_html(code, title, sections, include_mathjax, subject)

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

    return output_path


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert raw-notes markdown files into revision-notes HTML pages."
    )
    parser.add_argument("topic", help="Topic code, e.g. 1.4.1 or 2.2.1.md")
    parser.add_argument(
        "--subject",
        default="edexcel",
        help="Subject folder under raw-notes/ and revision-notes/ (default: edexcel)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and resolve paths without writing the output file.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        output_path = convert(args.topic, subject=args.subject, dry_run=args.dry_run)
    except Exception as exc:  # pragma: no cover - CLI reporting
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Dry run successful. Output would be: {output_path}")
    else:
        print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
