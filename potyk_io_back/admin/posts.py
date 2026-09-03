"""Создание markdown-поста с обложкой в templates/potyk-io/posts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from potyk_io_back.potyk_io.feed.random_notes import VIDEO_COVER_EXTS

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTS_DIR = REPO_ROOT / "templates" / "potyk-io" / "posts"
IMG_DIR = REPO_ROOT / "static" / "potyk-io" / "img" / "posts"
VIDEO_DIR = REPO_ROOT / "static" / "potyk-io" / "video" / "posts"

_RU = {
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
    "х": "h",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


@dataclass
class CreatedPost:
    slug: str
    url: str
    md_path: Path
    cover_url: str


def slugify_title(title: str) -> str:
    lowered = title.strip().casefold()
    chars: list[str] = []
    for ch in lowered:
        if ch in _RU:
            chars.append(_RU[ch])
        elif ch.isascii() and (ch.isalnum() or ch in "-_"):
            chars.append(ch)
        elif ch.isspace() or ch in ".,/\\:+":
            chars.append("-")
        else:
            chars.append("-")
    slug = re.sub(r"-{2,}", "-", "".join(chars)).strip("-_")
    return slug or "post"


def unique_slug(base: str) -> str | None:
    candidate = base
    for i in range(2, 50):
        if not (POSTS_DIR / f"{candidate}.md").exists():
            return candidate
        candidate = f"{base}-{i}"
    return None


def _is_video(ext: str) -> bool:
    return ext.lower() in VIDEO_COVER_EXTS


def create_post(title: str, cover: FileStorage) -> CreatedPost:
    title = (title or "").strip()
    if not title:
        raise ValueError("Укажи название")
    if cover is None or not cover.filename:
        raise ValueError("Выбери файл")

    raw_name = secure_filename(cover.filename) or "cover"
    ext = Path(raw_name).suffix.lower()
    if not ext:
        raise ValueError("У файла нет расширения")

    base = slugify_title(title)
    slug = unique_slug(base)
    if slug is None:
        raise ValueError("Слишком много постов с таким названием")

    media_dir = VIDEO_DIR if _is_video(ext) else IMG_DIR
    media_dir.mkdir(parents=True, exist_ok=True)
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    media_name = f"{slug}{ext}"
    media_path = media_dir / media_name
    if media_path.exists():
        raise ValueError("Файл обложки с таким именем уже есть")

    cover.save(media_path)

    if _is_video(ext):
        cover_url = f"/static/potyk-io/video/posts/{media_name}"
        body_media = (
            f'<video src="{cover_url}" controls playsinline></video>'
        )
    else:
        cover_url = f"/static/potyk-io/img/posts/{media_name}"
        body_media = f"![{title}]({cover_url})"

    today = date.today().isoformat()
    md = (
        f"---\n"
        f"created: {today}\n"
        f"cover: {cover_url}\n"
        f"---\n"
        f"# {title}\n"
        f"\n"
        f"{body_media}\n"
    )
    md_path = POSTS_DIR / f"{slug}.md"
    if md_path.exists():
        media_path.unlink(missing_ok=True)
        raise ValueError("Пост с таким адресом уже есть")

    md_path.write_text(md, encoding="utf-8")
    return CreatedPost(
        slug=slug,
        url=f"/posts/{slug}",
        md_path=md_path,
        cover_url=cover_url,
    )
