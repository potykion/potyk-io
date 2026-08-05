from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-io"


def resolve_page(page_path: str) -> Path | None:
    page_path = page_path.strip("/")
    if not page_path or ".." in Path(page_path).parts:
        return None

    name = Path(page_path).name
    if name.startswith("_") or name.startswith("."):
        return None

    candidates = [
        TEMPLATES_DIR / f"{page_path}.md",
        TEMPLATES_DIR / page_path / "index.md",
        TEMPLATES_DIR / f"{page_path}.html",
        TEMPLATES_DIR / page_path / "menu.html",
    ]

    templates_root = TEMPLATES_DIR.resolve()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(templates_root)
        except (ValueError, OSError):
            continue
        if resolved.is_file() and not resolved.name.startswith("_"):
            return resolved

    return None
