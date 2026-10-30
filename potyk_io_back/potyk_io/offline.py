"""Оффлайн-precache публичных разделов potyk.io."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote

from potyk_io_back.potyk_io.md_rendering.templates import FOOD_TEMPLATES_DIR, TEMPLATES_DIR

REPO_ROOT = Path(__file__).resolve().parents[2]
STATIC_ROOT = REPO_ROOT / "static"
TEMPLATES_ROOT = REPO_ROOT / "templates"

TRAVEL_TEMPLATES_DIR = TEMPLATES_ROOT / "potyk-travel"
TECH_TEMPLATES_DIR = TEMPLATES_ROOT / "potyk-tech"
CULTURE_TEMPLATES_DIR = TEMPLATES_ROOT / "potyk-culture"
MU_TEMPLATES_DIR = TEMPLATES_ROOT / "potyk-mu"
DOCS_TEMPLATES_DIR = TEMPLATES_ROOT / "docs"

SHELL_URLS = [
    "/static/jinja/css/shell.css",
    "/static/jinja/css/side-panel.css",
    "/static/jinja/css/forms.css",
    "/static/jinja/js/side-panel.js",
    "/static/potyk-io/css/sidebar.css",
    "/static/potyk-io/css/index.css",
    "/static/potyk-io/css/index_v2.css",
    "/static/potyk-io/css/card-grid.css",
    "/static/potyk-io/css/md-content.css",
    "/static/potyk-io/css/food.css",
    "/static/potyk-io/css/travel.css",
    "/static/potyk-io/css/culture.css",
    "/static/potyk-io/css/docs-tree.css",
    "/static/potyk-io/css/findings.css",
    "/static/potyk-io/js/recipe-page.js",
    "/static/potyk-io/js/content-card-fit-title.js",
    "/static/potyk-io/img/potyk-io-logo.png",
    "/static/potyk-io/img/globe.gif",
    "/static/potyk-io/img/money/fin-cover.png",
    "/static/potyk-io/favicon.ico",
    "/static/potyk-io/favicon-16x16.png",
    "/static/potyk-io/favicon-32x32.png",
    "/static/potyk-io/apple-touch-icon.png",
    "/static/potyk-io/android-chrome-192x192.png",
    "/static/potyk-io/android-chrome-512x512.png",
    "/static/potyk-io/site.webmanifest",
    "/static/potyk-io/food.webmanifest",
]

CORE_PAGES = [
    "/",
    "/food",
    "/food/offline",
    "/travel",
    "/tech",
    "/culture",
    "/mu",
    "/findings",
    "/prikols",
    "/docs",
    "/money",
    "/invest",
    "/invest/funds",
    "/invest/dependencies",
    "/invest/passive-income",
    "/invest/trading",
    "/invest/lore",
]

# Blueprint index routes often 308 → trailing slash; precache both.
_SLASH_INDEX_URLS = (
    "/travel",
    "/tech",
    "/culture",
    "/mu",
    "/prikols",
    "/docs",
    "/money",
    "/invest",
)

_SKIP_FILE_NAMES = {
    "page.html",
    "tree.html",
    "README.md",
    "menu.html",
    "_base.html",
    "_sidebar.html",
    "_grid.html",
}
_SKIP_DIR_NAMES = {
    ".obsidian",
    "_obsidian",
    "_TEMPLATES",
    "_templates",
    "partials",
    "templates",
}
_STATIC_REF_RE = re.compile(
    r"""(?:src|href)=["'](/static/[^"'?#]+)["']"""
    r"""|!\[[^\]]*]\((/static/[^)\s]+)\)"""
    r"""|\[[^\]]*]\((/static/[^)\s]+)\)"""
)
_SKIP_STATIC_SUFFIXES = {".exe", ".zip", ".7z"}


def _section_page_url(prefix: str, path: PurePosixPath) -> str:
    prefix = prefix.rstrip("/") or ""
    if path.name in ("index.md", "index.html"):
        parent = path.parent.as_posix()
        if parent == ".":
            return prefix or "/"
        return f"{prefix}/{parent}"
    return f"{prefix}/{path.with_suffix('').as_posix()}"


def _encode_url(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return "/".join(quote(part, safe="") if part else "" for part in path.split("/"))


def _path_is_skipped(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    if any(part in _SKIP_DIR_NAMES or part.startswith(".") for part in parts[:-1]):
        return True
    name = path.name
    if name.startswith(("_", ".")) or name in _SKIP_FILE_NAMES:
        return True
    return False


def _rglob_page_urls(root: Path, prefix: str) -> list[str]:
    if not root.is_dir():
        return []
    urls = [prefix.rstrip("/") or "/"]
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if _path_is_skipped(path, root):
            continue
        if path.suffix.lower() not in {".md", ".html"}:
            continue
        rel = PurePosixPath(path.relative_to(root).as_posix())
        urls.append(_section_page_url(prefix, rel))
    return urls


def _docs_folder_urls() -> list[str]:
    root = DOCS_TEMPLATES_DIR
    if not root.is_dir():
        return []
    urls: list[str] = []
    for path in root.rglob("*"):
        if not path.is_dir() or path == root:
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in _SKIP_DIR_NAMES or part.startswith(".") for part in rel_parts):
            continue
        urls.append(f"/docs/{path.relative_to(root).as_posix()}")
    return urls


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
        urls.append(_section_page_url("/food", rel))
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


def _iter_content_files() -> list[Path]:
    roots = [
        TEMPLATES_DIR / "index.html",
        FOOD_TEMPLATES_DIR,
        TRAVEL_TEMPLATES_DIR,
        TECH_TEMPLATES_DIR,
        CULTURE_TEMPLATES_DIR,
        MU_TEMPLATES_DIR,
        DOCS_TEMPLATES_DIR,
        TEMPLATES_ROOT / "potyk-prikols",
        TEMPLATES_ROOT / "potyk-money",
        TEMPLATES_ROOT / "potyk-invest" / "passive-income.md",
        TEMPLATES_ROOT / "potyk-invest" / "trading.md",
        TEMPLATES_ROOT / "potyk-invest" / "lore.md",
        TEMPLATES_ROOT / "potyk-invest" / "funds.html",
        TEMPLATES_ROOT / "potyk-invest" / "dependencies.html",
        TEMPLATES_ROOT / "potyk-io" / "findings.html",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if _path_is_skipped(path, root):
                continue
            if path.suffix.lower() not in {".md", ".html"}:
                continue
            files.append(path)
    return files


def _extract_static_urls(text: str) -> list[str]:
    urls: list[str] = []
    for match in _STATIC_REF_RE.finditer(text):
        raw = next(g for g in match.groups() if g)
        path = unquote(raw.split("?")[0].split("#")[0])
        if Path(path).suffix.lower() in _SKIP_STATIC_SUFFIXES:
            continue
        if "yt-dlp" in path.lower():
            continue
        urls.append(_encode_url(path))
    return urls


def _content_static_urls() -> list[str]:
    urls: list[str] = []
    for path in _iter_content_files():
        try:
            text = path.read_text(encoding="utf-8-sig")
        except OSError:
            continue
        urls.extend(_extract_static_urls(text))
    # device covers from frontmatter often use cover: /static/...
    devices = TECH_TEMPLATES_DIR / "devices"
    if devices.is_dir():
        for path in devices.rglob("*.md"):
            if _path_is_skipped(path, TECH_TEMPLATES_DIR):
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except OSError:
                continue
            for line in text.splitlines()[:40]:
                if "cover:" not in line:
                    continue
                _, _, value = line.partition(":")
                value = value.strip().strip("\"'")
                if value.startswith("/static/"):
                    urls.append(_encode_url(value))
    return urls


def _fingerprint(urls: list[str]) -> str:
    h = hashlib.sha256()
    h.update("\n".join(urls).encode("utf-8"))
    for url in urls:
        if not url.startswith("/static/"):
            continue
        disk = STATIC_ROOT / url.removeprefix("/static/")
        if disk.is_file():
            st = disk.stat()
            h.update(f"{url}:{st.st_mtime_ns}:{st.st_size}\n".encode("utf-8"))
    return h.hexdigest()[:12]


def _with_slash_variants(urls: list[str]) -> list[str]:
    out: set[str] = set(urls)
    for url in _SLASH_INDEX_URLS:
        out.add(url)
        out.add(url + "/")
    return sorted(out)


def _encode_list(urls: list[str]) -> list[str]:
    return [
        _encode_url(u) if any(ord(ch) > 127 for ch in u) else u for u in urls
    ]


def build_shell_urls() -> list[str]:
    """Лёгкий набор для install SW — без массового обхода разделов."""
    return sorted(set(_encode_list(["/", *SHELL_URLS])))


def build_offline_manifest() -> dict[str, str | list[str]]:
    shell = build_shell_urls()
    urls = _with_slash_variants(
        _encode_list(
            [
                *CORE_PAGES,
                *SHELL_URLS,
                *_recipe_page_urls(),
                *_food_image_urls(),
                *_rglob_page_urls(TRAVEL_TEMPLATES_DIR, "/travel"),
                *_rglob_page_urls(TECH_TEMPLATES_DIR, "/tech"),
                *_rglob_page_urls(CULTURE_TEMPLATES_DIR, "/culture"),
                *_rglob_page_urls(MU_TEMPLATES_DIR, "/mu"),
                *_rglob_page_urls(DOCS_TEMPLATES_DIR, "/docs"),
                *_docs_folder_urls(),
                *_content_static_urls(),
            ]
        )
    )
    # version только от shell — иначе каждый правленый md сбрасывал бы SW-кэш
    version = _fingerprint(shell)
    return {"version": version, "shell": shell, "urls": urls}
