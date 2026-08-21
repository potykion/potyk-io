from __future__ import annotations

import re
from dataclasses import dataclass

from potyk_io_back.potyk_io.md_rendering.render import split_frontmatter
from potyk_io_back.potyk_io.md_rendering.templates import TEMPLATES_DIR

TASKS_DIR = TEMPLATES_DIR / "tasks"
SKIP_NAMES = {"README.md", "ЗАДАЧИ СПИСОК.md"}
INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


@dataclass
class InboxEntry:
    project: str
    status: str
    text: str
    created_at: str | None = None
    title: str = ""


def _title_from_text(text: str, fallback: str) -> str:
    stripped = text.strip()
    if not stripped:
        return fallback
    first = stripped.splitlines()[0].lstrip("# ").strip()
    return first or fallback


def load_local_tasks() -> list[InboxEntry]:
    if not TASKS_DIR.is_dir():
        return []

    entries: list[InboxEntry] = []
    paths = [
        path
        for path in TASKS_DIR.glob("*.md")
        if path.name not in SKIP_NAMES and not path.name.startswith("_")
    ]
    paths.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    for path in paths:
        meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
        text = body.strip()
        entries.append(
            InboxEntry(
                project=meta.get("project", ""),
                status=meta.get("status", ""),
                text=text,
                title=_title_from_text(text, path.stem),
            )
        )
    return entries


def _stem_for(item: dict) -> str:
    title = _title_from_text(item.get("text") or "", f"inbox-{item.get('id', 'new')}")
    stem = INVALID_FILENAME.sub("", title).strip(" .")
    return (stem or f"inbox-{item.get('id', 'new')}")[:80]


def already_pulled(item_id: object) -> bool:
    suffix = f"-{item_id}.md"
    return any(path.name.endswith(suffix) for path in TASKS_DIR.glob("*.md"))


def save_prod_items(items: list[dict]) -> tuple[int, int, list[int]]:
    """Write prod issues to local task md files.

    Returns (saved, skipped, synced_ids). synced_ids are issue ids that are
    present locally after this call (newly written or already on disk) and
    should be acknowledged/deleted on prod.
    """
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0
    skipped = 0
    synced_ids: list[int] = []
    for item in items:
        item_id = item.get("id")
        if item_id is not None and already_pulled(item_id):
            skipped += 1
            synced_ids.append(int(item_id))
            continue

        project = (item.get("project") or "potyk-io").strip() or "potyk-io"
        status = (item.get("status") or "new").strip() or "new"
        text = (item.get("text") or "").strip()
        name = f"{_stem_for(item)}-{item_id}.md" if item_id is not None else f"{_stem_for(item)}.md"
        path = TASKS_DIR / name
        if path.exists():
            skipped += 1
            if item_id is not None:
                synced_ids.append(int(item_id))
            continue
        path.write_text(
            f"---\nstatus: {status}\nproject: {project}\n---\n{text}\n",
            encoding="utf-8",
        )
        saved += 1
        if item_id is not None:
            synced_ids.append(int(item_id))
    return saved, skipped, synced_ids
