from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from potyk_io_back.potyk_io.md_rendering.render import FRONTMATTER_RE, split_frontmatter
from potyk_io_back.potyk_io.md_rendering.templates import TEMPLATES_DIR

TASKS_DIR = TEMPLATES_DIR / "tasks"
DONE_DIR = TASKS_DIR / "done"
SKIP_NAMES = {"README.md", "ЗАДАЧИ СПИСОК.md"}
INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
TASK_STATUSES = ("idea", "draft", "new", "wip", "done")


@dataclass
class InboxEntry:
    project: str
    status: str
    text: str
    created_at: str | None = None
    title: str = ""
    filename: str = ""


def _title_from_text(text: str, fallback: str) -> str:
    stripped = text.strip()
    if not stripped:
        return fallback
    first = stripped.splitlines()[0].lstrip("# ").strip()
    return first or fallback


def is_done_status(status: str) -> bool:
    return status.strip().lower() == "done"


def _is_listed_task(path: Path) -> bool:
    return (
        path.is_file()
        and path.suffix.lower() == ".md"
        and path.name not in SKIP_NAMES
        and not path.name.startswith("_")
    )


def _entry_from_path(path: Path) -> InboxEntry:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
    text = body.strip()
    return InboxEntry(
        project=meta.get("project", ""),
        status=meta.get("status", "").strip(),
        text=text,
        title=_title_from_text(text, path.stem),
        filename=path.name,
    )


def load_local_tasks(*, include_done: bool = False) -> list[InboxEntry]:
    if not TASKS_DIR.is_dir():
        return []

    entries: list[InboxEntry] = []
    paths = [path for path in TASKS_DIR.glob("*.md") if _is_listed_task(path)]
    paths.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    for path in paths:
        entry = _entry_from_path(path)
        if not include_done and is_done_status(entry.status):
            continue
        entries.append(entry)
    return entries


def resolve_task_file(filename: str) -> Path | None:
    name = Path(filename).name
    if not filename or name != filename:
        return None
    path = TASKS_DIR / name
    try:
        path.resolve().relative_to(TASKS_DIR.resolve())
    except ValueError:
        return None
    if not _is_listed_task(path):
        return None
    return path


def get_local_task(filename: str) -> InboxEntry | None:
    path = resolve_task_file(filename)
    if path is None:
        return None
    return _entry_from_path(path)


def _unique_path(directory: Path, name: str) -> Path:
    dest = directory / name
    if not dest.exists():
        return dest
    stem = Path(name).stem
    suffix = Path(name).suffix
    i = 2
    while True:
        dest = directory / f"{stem}-{i}{suffix}"
        if not dest.exists():
            return dest
        i += 1


def set_status_text(raw: str, status: str) -> str:
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return f"---\nstatus: {status}\n---\n{raw}"
    block = match.group(1)
    if re.search(r"(?m)^status\s*:", block):
        block = re.sub(r"(?m)^status\s*:.*$", f"status: {status}", block, count=1)
    else:
        block = f"status: {status}\n{block}"
    return f"---\n{block}\n---\n{raw[match.end():]}"


def update_local_task_status(filename: str, status: str) -> InboxEntry | None:
    path = resolve_task_file(filename)
    if path is None:
        return None
    raw = path.read_text(encoding="utf-8-sig")
    path.write_text(set_status_text(raw, status), encoding="utf-8")
    if is_done_status(status):
        DONE_DIR.mkdir(parents=True, exist_ok=True)
        dest = _unique_path(DONE_DIR, path.name)
        path.rename(dest)
        return _entry_from_path(dest)
    return _entry_from_path(path)


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
