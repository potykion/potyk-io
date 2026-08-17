import re
import subprocess
from datetime import date, datetime
from pathlib import Path

MONTHS_RU = (
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)

DAY_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})$")
WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")
MONTH_RE = re.compile(r"^(\d{4})-(\d{2})$")
YEAR_RE = re.compile(r"^(\d{4})$")
ISO_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")

REPO_ROOT = Path(__file__).resolve().parents[3]


def parse_iso_date(value: str) -> date | None:
    value = value.strip().strip("'\"")
    match = ISO_DATE_RE.match(value)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def created_from_meta(meta: dict[str, str]) -> date | None:
    for key in ("created", "date"):
        raw = meta.get(key)
        if not raw:
            continue
        parsed = parse_iso_date(raw)
        if parsed:
            return parsed
    return None


def created_from_filename(stem: str) -> date | None:
    if DAY_RE.match(stem):
        return date.fromisoformat(stem)
    week = WEEK_RE.match(stem)
    if week:
        try:
            return date.fromisocalendar(int(week.group(1)), int(week.group(2)), 1)
        except ValueError:
            return None
    month = MONTH_RE.match(stem)
    if month:
        try:
            return date(int(month.group(1)), int(month.group(2)), 1)
        except ValueError:
            return None
    year = YEAR_RE.match(stem)
    if year:
        return date(int(year.group(1)), 1, 1)
    return None


def created_from_git(path: Path) -> date | None:
    try:
        rel = path.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return None
    result = subprocess.run(
        [
            "git",
            "log",
            "--follow",
            "--diff-filter=A",
            "--format=%aI",
            "--",
            rel.as_posix(),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return None
    return parse_iso_date(lines[-1])


def created_from_fs(path: Path) -> date:
    return datetime.fromtimestamp(path.stat().st_ctime).date()


def resolve_created(
    path: Path,
    meta: dict[str, str],
    *,
    use_git: bool = False,
) -> date:
    """created из frontmatter, иначе из имени, иначе git (если просили) / ctime файла."""
    from_meta = created_from_meta(meta)
    if from_meta:
        return from_meta
    from_name = created_from_filename(path.stem)
    if from_name:
        return from_name
    if use_git:
        from_git = created_from_git(path)
        if from_git:
            return from_git
    return created_from_fs(path)


def format_created_ru(value: date) -> str:
    return f"{value.day} {MONTHS_RU[value.month - 1]} {value.year}"


def collect_git_add_dates() -> dict[str, date]:
    result = subprocess.run(
        [
            "git",
            "log",
            "--reverse",
            "--pretty=format:COMMIT %aI",
            "--name-only",
            "--",
            "templates/potyk-io",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    dates: dict[str, date] = {}
    current: date | None = None
    for raw in result.stdout.splitlines():
        line = raw.strip().replace("\\", "/")
        if not line:
            continue
        if line.startswith("COMMIT "):
            current = parse_iso_date(line[7:])
            continue
        if current and line.endswith(".md") and line not in dates:
            dates[line] = current
    return dates


def insert_created_frontmatter(text: str, created: date) -> str:
    from potyk_io_back.potyk_io.md_rendering.render import FRONTMATTER_RE, split_frontmatter

    meta, _ = split_frontmatter(text)
    if "created" in meta:
        return text
    line = f"created: {created.isoformat()}"
    match = FRONTMATTER_RE.match(text)
    if not match:
        rest = text if text.startswith("\n") else f"\n{text}"
        return f"---\n{line}\n---{rest}"
    inner = match.group(1)
    new_fm = f"---\n{line}\n{inner}\n---"
    suffix = text[match.end() :]
    if suffix and not suffix.startswith("\n"):
        new_fm += "\n"
    return new_fm + suffix


def backfill_created(path: Path, git_dates: dict[str, date] | None = None) -> bool:
    from potyk_io_back.potyk_io.md_rendering.render import split_frontmatter

    text = path.read_text(encoding="utf-8-sig")
    meta, _ = split_frontmatter(text)
    if "created" in meta:
        return False
    created = created_from_meta(meta) or created_from_filename(path.stem)
    if created is None and git_dates is not None:
        rel = path.resolve().relative_to(REPO_ROOT).as_posix()
        created = git_dates.get(rel)
    if created is None:
        created = created_from_git(path) or created_from_fs(path)
    updated = insert_created_frontmatter(text, created)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8", newline="\n")
    return True
