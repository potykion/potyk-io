from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


def _is_youtube(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host in {"youtube.com", "youtu.be", "m.youtube.com", "music.youtube.com"}


def fetch_title(url: str) -> str:
    """Подтягивает title через YouTube oEmbed; иначе возвращает url."""
    if not _is_youtube(url):
        return url

    oembed = f"https://www.youtube.com/oembed?url={quote(url, safe='')}&format=json"
    req = Request(oembed, headers={"User-Agent": "potyk-io-findings", "Accept": "application/json"})
    try:
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
        return url

    title = (data.get("title") or "").strip() if isinstance(data, dict) else ""
    return title or url
