import html as html_module
import re
from urllib.parse import quote

HASHTAG_RE = re.compile(r"(?<![&/\w])#([0-9A-Za-zА-Яа-яЁё_-]+)")
HEADING_PREFIX_RE = re.compile(r"^(#{1,6}[ \t]+)")
FENCE_RE = re.compile(r"^(```|~~~)")


def _repl(match: re.Match[str]) -> str:
    tag = match.group(1)
    href = "/search?q=" + quote("#" + tag, safe="")
    label = html_module.escape("#" + tag)
    return f'<a class="hashtag" href="{href}">{label}</a>'


def _linkify_outside_code(line: str) -> str:
    parts = line.split("`")
    for i in range(0, len(parts), 2):
        parts[i] = HASHTAG_RE.sub(_repl, parts[i])
    return "`".join(parts)


def linkify_hashtags(text: str) -> str:
    """Turn #тег into search links. Skip fenced/inline code and ATX heading marks."""
    out: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if FENCE_RE.match(stripped):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        heading = HEADING_PREFIX_RE.match(line)
        if heading:
            prefix = line[: heading.end()]
            rest = line[heading.end() :]
            out.append(prefix + _linkify_outside_code(rest))
            continue
        out.append(_linkify_outside_code(line))
    return "".join(out)
