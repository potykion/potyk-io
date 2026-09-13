"""Download movie covers from Kinopoisk CDN into static/."""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MOVIES_IMG_DIR = REPO_ROOT / "static" / "potyk-io" / "img" / "movies"
COVER_URL_PREFIX = "/static/potyk-io/img/movies/"

_TRANSLIT = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def movie_id_from_kinopoisk(url: str) -> str | None:
    match = re.search(r"/(?:film|series)/(\d+)/?", url)
    return match.group(1) if match else None


def cover_cdn_url(kp_id: str) -> str:
    return f"https://st.kp.yandex.net/images/film_iphone/iphone360_{kp_id}.jpg"


def slugify_title(text: str) -> str:
    out: list[str] = []
    for ch in text.lower().strip():
        if ch in _TRANSLIT:
            out.append(_TRANSLIT[ch])
        elif "a" <= ch <= "z" or "0" <= ch <= "9":
            out.append(ch)
        elif ch in " -_./":
            out.append("-")
    slug = re.sub(r"-+", "-", "".join(out)).strip("-")
    return slug or "movie"


def _unique_slug(base: str) -> str:
    MOVIES_IMG_DIR.mkdir(parents=True, exist_ok=True)
    used = {p.stem for p in MOVIES_IMG_DIR.iterdir() if p.is_file()}
    slug = base
    n = 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    return slug


def download_cover(
    kp_id: str,
    *,
    title_ru: str,
    title_en: str | None = None,
) -> str | None:
    """Скачивает постер в static; возвращает URL-путь или None при ошибке."""
    base = slugify_title(title_en or title_ru or kp_id)
    slug = _unique_slug(base)
    filename = f"{slug}.jpg"
    dest = MOVIES_IMG_DIR / filename
    url = cover_cdn_url(kp_id)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; potyk-io/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
    if len(data) < 1000:
        return None
    dest.write_bytes(data)
    return f"{COVER_URL_PREFIX}{filename}"
