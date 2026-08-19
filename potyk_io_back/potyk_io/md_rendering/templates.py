from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "templates" / "potyk-io"
FOOD_TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "templates" / "potyk-food"


def resolve_page(
    page_path: str, root: Path | None = None, allow_assets: bool = False
) -> Path | None:
    root = root or TEMPLATES_DIR
    page_path = page_path.strip("/")
    if not page_path or ".." in Path(page_path).parts:
        return None

    name = Path(page_path).name
    if name.startswith("_") or name.startswith("."):
        return None

    candidates = [
        root / f"{page_path}.md",
        root / page_path / "index.md",
        root / f"{page_path}.html",
        root / page_path / "menu.html",
    ]
    if allow_assets:
        candidates.append(root / page_path)

    templates_root = root.resolve()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(templates_root)
        except (ValueError, OSError):
            continue
        if resolved.is_file() and not resolved.name.startswith("_"):
            return resolved

    return None
