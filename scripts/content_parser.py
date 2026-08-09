"""Small, dependency-free parsers for this repository's content format."""

import ast
import html
import re


def _without_inline_comment(value):
    quote = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\" and quote:
            escaped = True
            continue
        if char in ('"', "'"):
            quote = None if quote == char else char if quote is None else quote
            continue
        if char == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def _parse_scalar(value):
    value = _without_inline_comment(value.strip())
    if value == "[]":
        return []
    if value in ("null", "~"):
        return None
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    if value[:1] in ('"', "'"):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
    return value


def parse_document(text):
    """Parse the simple YAML-frontmatter subset used by entries and templates."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("document does not start with frontmatter")

    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("frontmatter is not closed") from exc

    fields = {}
    active_list = None
    for raw_line in lines[1:end]:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if raw_line[:1].isspace() and stripped.startswith("- "):
            if active_list is None:
                raise ValueError(f"list item without a field: {raw_line}")
            fields[active_list].append(_parse_scalar(stripped[2:]))
            continue
        if ":" not in raw_line:
            raise ValueError(f"invalid frontmatter line: {raw_line}")
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            fields[key] = []
            active_list = key
        else:
            fields[key] = _parse_scalar(value)
            active_list = None

    return fields, "\n".join(lines[end + 1:]).strip()


def _inline_markdown(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^]]+)]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(markdown_text):
    """Render the headings, paragraphs, and lists used in entry bodies."""
    output = []
    paragraph = []
    in_list = False

    def flush_paragraph():
        if paragraph:
            output.append(f"<p>{_inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            close_list()
        elif line.startswith("### "):
            flush_paragraph()
            close_list()
            output.append(f"<h3>{_inline_markdown(line[4:])}</h3>")
        elif line.startswith("## "):
            flush_paragraph()
            close_list()
            output.append(f"<h2>{_inline_markdown(line[3:])}</h2>")
        elif line.startswith("- "):
            flush_paragraph()
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{_inline_markdown(line[2:])}</li>")
        else:
            paragraph.append(line)

    flush_paragraph()
    close_list()
    return "\n".join(output)
