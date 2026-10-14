"""Девайсы potyk-tech: карточки из markdown (type + cover)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from potyk_io_back.potyk_io.md_rendering import extract_h1, split_frontmatter, unquote_meta

DEVICES_TEMPLATES_DIR = (
    Path(__file__).resolve().parents[2] / "templates" / "potyk-tech" / "devices"
)

# Порядок секций на /tech/devices; type в frontmatter → заголовок + id якоря.
DEVICE_TYPE_SECTIONS: tuple[tuple[str, str, str], ...] = (
    ("ebook", "Электронные книги", "электронные-книги"),
    ("phone", "Телефоны", "телефоны"),
    ("watch", "Часики", "часики"),
    ("headphones", "Наушники", "наушники"),
    ("mouse", "Мыши", "мыши"),
    ("keyboard", "Клавиатуры", "клавиатуры"),
)


@dataclass(frozen=True)
class DeviceCard:
    title: str
    cover: str
    url: str
    type: str


@dataclass(frozen=True)
class DeviceSection:
    type: str
    title: str
    anchor: str
    devices: list[DeviceCard]


def _device_paths(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        (
            path
            for path in root.glob("*.md")
            if path.is_file() and not path.name.startswith(("_", "."))
        ),
        key=lambda path: path.stem.casefold(),
    )


def load_devices(*, root: Path | None = None) -> list[DeviceCard]:
    """Список девайсов с type и cover из YAML frontmatter."""
    devices_root = root or DEVICES_TEMPLATES_DIR
    devices: list[DeviceCard] = []
    for path in _device_paths(devices_root):
        meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
        device_type = unquote_meta(meta.get("type", "")).strip().lower()
        cover = unquote_meta(meta.get("cover", "")).strip()
        if not device_type or not cover:
            continue
        title = unquote_meta(meta.get("title", "")) or extract_h1(body) or path.stem
        devices.append(
            DeviceCard(
                title=title,
                cover=cover,
                url=f"/tech/devices/{path.stem}",
                type=device_type,
            )
        )
    return devices


def load_device_sections(*, root: Path | None = None) -> list[DeviceSection]:
    """Секции каталога: только типы с хотя бы одним девайсом, в фиксированном порядке."""
    by_type: dict[str, list[DeviceCard]] = {}
    for device in load_devices(root=root):
        by_type.setdefault(device.type, []).append(device)

    sections: list[DeviceSection] = []
    for type_key, title, anchor in DEVICE_TYPE_SECTIONS:
        cards = by_type.get(type_key)
        if not cards:
            continue
        cards.sort(key=lambda card: card.title.casefold())
        sections.append(
            DeviceSection(type=type_key, title=title, anchor=anchor, devices=cards)
        )
    return sections
