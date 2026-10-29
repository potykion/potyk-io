"""Оглавление рецептов potyk-food: категории из папок recipes/ + .nav.yml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from potyk_io_back.potyk_io.md_rendering import extract_h1, split_frontmatter
from potyk_io_back.potyk_io.md_rendering.templates import FOOD_TEMPLATES_DIR

RECIPES_DIR = FOOD_TEMPLATES_DIR / "recipes"
_NAV_NAME = ".nav.yml"
_PAGE_SUFFIXES = {".md", ".html"}


@dataclass(frozen=True)
class RecipeLink:
    title: str
    url: str


@dataclass(frozen=True)
class RecipeSubsection:
    title: str
    icon: str
    pages: list[RecipeLink]


@dataclass(frozen=True)
class RecipeSection:
    title: str
    icon: str
    pages: list[RecipeLink] = field(default_factory=list)
    subsections: list[RecipeSubsection] = field(default_factory=list)


def _read_nav(folder: Path) -> dict:
    path = folder / _NAV_NAME
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    except (OSError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def _folder_title(folder: Path) -> str:
    nav = _read_nav(folder)
    title = str(nav.get("title") or "").strip()
    if title:
        return title
    name = folder.name
    if "-" in name and name.split("-", 1)[0].isdigit():
        name = name.split("-", 1)[1]
    return name.replace("-", " ").strip() or folder.name


def _folder_icon(folder: Path) -> str:
    nav = _read_nav(folder)
    return str(nav.get("icon") or "").strip()


def _page_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return path.stem
    if path.suffix.lower() == ".md":
        _, body = split_frontmatter(text)
        return extract_h1(body) or path.stem
    return path.stem


def _page_links(folder: Path, *, url_prefix: str) -> list[RecipeLink]:
    links: list[RecipeLink] = []
    for path in sorted(folder.iterdir(), key=lambda p: p.name.casefold()):
        if not path.is_file():
            continue
        if path.name.startswith((".", "_")):
            continue
        if path.suffix.lower() not in _PAGE_SUFFIXES:
            continue
        if path.name.lower() in {"index.md", "index.html"}:
            continue
        links.append(
            RecipeLink(
                title=_page_title(path),
                url=f"{url_prefix}/{path.stem}",
            )
        )
    links.sort(key=lambda link: link.title.casefold())
    return links


def _child_dirs(folder: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in folder.iterdir()
            if path.is_dir() and not path.name.startswith((".", "_"))
        ),
        key=lambda path: path.name.casefold(),
    )


def load_recipe_sections(*, root: Path | None = None) -> list[RecipeSection]:
    """Категории рецептов: top-level папки recipes/, подкатегории — вложенные."""
    recipes_root = root or RECIPES_DIR
    if not recipes_root.is_dir():
        return []

    sections: list[RecipeSection] = []
    for category in _child_dirs(recipes_root):
        cat_prefix = f"/food/recipes/{category.name}"
        pages = _page_links(category, url_prefix=cat_prefix)
        subsections: list[RecipeSubsection] = []
        for sub in _child_dirs(category):
            sub_pages = _page_links(sub, url_prefix=f"{cat_prefix}/{sub.name}")
            if not sub_pages:
                continue
            subsections.append(
                RecipeSubsection(
                    title=_folder_title(sub),
                    icon=_folder_icon(sub),
                    pages=sub_pages,
                )
            )
        if not pages and not subsections:
            continue
        sections.append(
            RecipeSection(
                title=_folder_title(category),
                icon=_folder_icon(category),
                pages=pages,
                subsections=subsections,
            )
        )
    return sections
