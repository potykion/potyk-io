import html as html_module
import re
from html.parser import HTMLParser

MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", re.DOTALL | re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE
)


class HtmlPreviewTruncator(HTMLParser):
    def __init__(self, limit: int):
        super().__init__(convert_charrefs=False)
        self.limit = limit
        self.count = 0
        self.parts: list[str] = []
        self.open_tags: list[str] = []
        self.done = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.done:
            return
        attr_html = "".join(
            f" {name}"
            if value is None
            else f' {name}="{html_module.escape(value, quote=True)}"'
            for name, value in attrs
        )
        self.parts.append(f"<{tag}{attr_html}>")
        if tag not in {"br", "hr", "img", "meta", "input", "source", "wbr"}:
            self.open_tags.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if self.done:
            return
        self.parts.append(f"</{tag}>")
        for i in range(len(self.open_tags) - 1, -1, -1):
            if self.open_tags[i] == tag:
                del self.open_tags[i:]
                break

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.done:
            return
        attr_html = "".join(
            f" {name}"
            if value is None
            else f' {name}="{html_module.escape(value, quote=True)}"'
            for name, value in attrs
        )
        self.parts.append(f"<{tag}{attr_html} />")

    def handle_data(self, data: str) -> None:
        if self.done:
            return
        remaining = self.limit - self.count
        if len(data) <= remaining:
            self.parts.append(html_module.escape(data))
            self.count += len(data)
            return
        self.parts.append(html_module.escape(data[:remaining]) + "…")
        self.count = self.limit
        self.done = True
        while self.open_tags:
            self.parts.append(f"</{self.open_tags.pop()}>")

    def handle_entityref(self, name: str) -> None:
        if self.done:
            return
        if self.count >= self.limit:
            self.parts.append("…")
            self.done = True
            while self.open_tags:
                self.parts.append(f"</{self.open_tags.pop()}>")
            return
        self.parts.append(f"&{name};")
        self.count += 1

    def handle_charref(self, name: str) -> None:
        if self.done:
            return
        if self.count >= self.limit:
            self.parts.append("…")
            self.done = True
            while self.open_tags:
                self.parts.append(f"</{self.open_tags.pop()}>")
            return
        self.parts.append(f"&#{name};")
        self.count += 1


def main_inner_html(page_html: str) -> str:
    match = MAIN_RE.search(page_html)
    if not match:
        return ""
    return SCRIPT_STYLE_RE.sub("", match.group(1)).strip()


def html_text(fragment: str) -> str:
    text = TAG_RE.sub(" ", fragment)
    text = html_module.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def truncate_html(fragment: str, limit: int) -> str:
    truncator = HtmlPreviewTruncator(limit)
    truncator.feed(fragment)
    truncator.close()
    return "".join(truncator.parts)


def demote_headings(html: str, levels: int = 1) -> str:
    """Shift heading levels down (h1→h2, h2→h3, …), capped at h6."""
    for n in range(6, 0, -1):
        html = re.sub(
            rf"(</?)h{n}\b",
            rf"\1h{min(n + levels, 6)}",
            html,
            flags=re.IGNORECASE,
        )
    return html
