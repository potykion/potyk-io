"""Оффлайн-precache для potyk-food (рецепты + shell)."""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from potyk_io_back.potyk_io.md_rendering.templates import FOOD_TEMPLATES_DIR

REPO_ROOT = Path(__file__).resolve().parents[2]
STATIC_ROOT = REPO_ROOT / "static"

SHELL_URLS = [
    "/static/jinja/css/shell.css",
    "/static/jinja/css/side-panel.css",
    "/static/jinja/js/side-panel.js",
    "/static/potyk-io/css/sidebar.css",
    "/static/potyk-io/css/index.css",
    "/static/potyk-io/css/md-content.css",
    "/static/potyk-io/css/food.css",
    "/static/potyk-io/js/recipe-page.js",
    "/static/potyk-io/favicon.ico",
    "/static/potyk-io/favicon-16x16.png",
    "/static/potyk-io/favicon-32x32.png",
    "/static/potyk-io/apple-touch-icon.png",
    "/static/potyk-io/android-chrome-192x192.png",
    "/static/potyk-io/android-chrome-512x512.png",
    "/static/potyk-io/food.webmanifest",
]

CORE_PAGES = [
    "/food",
    "/food/offline",
]


def _food_page_url(path: PurePosixPath) -> str:
    if path.name in ("index.md", "index.html"):
        parent = path.parent.as_posix()
        return "/food" if parent == "." else f"/food/{parent}"
    return f"/food/{path.with_suffix('').as_posix()}"


def _encode_url(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    parts = path.split("/")
    return "/".join(quote(part, safe="") if part else "" for part in parts)


def _recipe_page_urls() -> list[str]:
    recipes = FOOD_TEMPLATES_DIR / "recipes"
    if not recipes.is_dir():
        return []
    urls: list[str] = []
    for path in recipes.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith(("_", ".")):
            continue
        if path.suffix.lower() not in {".md", ".html"}:
            continue
        rel = PurePosixPath(path.relative_to(FOOD_TEMPLATES_DIR).as_posix())
        urls.append(_food_page_url(rel))
    return urls


def _food_image_urls() -> list[str]:
    img_dir = STATIC_ROOT / "potyk-io" / "img" / "food"
    if not img_dir.is_dir():
        return []
    urls: list[str] = []
    for path in img_dir.iterdir():
        if path.is_file() and not path.name.startswith("."):
            urls.append(_encode_url(f"/static/potyk-io/img/food/{path.name}"))
    return urls


def _fingerprint(urls: list[str]) -> str:
    h = hashlib.sha256()
    h.update("\n".join(urls).encode("utf-8"))
    recipes = FOOD_TEMPLATES_DIR / "recipes"
    if recipes.is_dir():
        for path in sorted(recipes.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".md", ".html"}:
                continue
            st = path.stat()
            rel = path.relative_to(FOOD_TEMPLATES_DIR).as_posix()
            h.update(f"{rel}:{st.st_mtime_ns}:{st.st_size}\n".encode("utf-8"))
    index = FOOD_TEMPLATES_DIR / "index.html"
    if index.is_file():
        st = index.stat()
        h.update(f"index.html:{st.st_mtime_ns}:{st.st_size}\n".encode("utf-8"))
    for url in SHELL_URLS:
        disk = STATIC_ROOT / url.removeprefix("/static/")
        if disk.is_file():
            st = disk.stat()
            h.update(f"{url}:{st.st_mtime_ns}:{st.st_size}\n".encode("utf-8"))
    return h.hexdigest()[:12]


def build_offline_manifest() -> dict[str, str | list[str]]:
    urls = [
        *CORE_PAGES,
        *SHELL_URLS,
        *_recipe_page_urls(),
        *_food_image_urls(),
    ]
    # stable unique order
    deduped = sorted(set(urls))
    version = _fingerprint(deduped)
    return {"version": version, "urls": deduped}
