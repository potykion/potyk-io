"""Remove image background with rembg; write transparent PNG."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image
from rembg import new_session, remove

# rembg 2.x defaults to bria-rmbg (~1GB). Pin a small model.
_SESSION = new_session("u2net")


def out_path_for(src: Path, explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit
    return src.with_suffix(".png")


def remove_bg(src: Path, dst: Path) -> None:
    img = Image.open(src).convert("RGBA")
    result = remove(img, session=_SESSION)
    assert isinstance(result, Image.Image)
    bbox = result.getbbox()
    if bbox:
        pad = 2
        x0, y0, x1, y1 = bbox
        result = result.crop(
            (
                max(0, x0 - pad),
                max(0, y0 - pad),
                min(result.width, x1 + pad),
                min(result.height, y1 + pad),
            )
        )
    dst.parent.mkdir(parents=True, exist_ok=True)
    result.save(dst, format="PNG", optimize=True)
    print(f"{src} -> {dst} ({dst.stat().st_size} bytes, {result.size[0]}x{result.size[1]})")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "Usage: remove_bg.py <input> [output.png] | remove_bg.py <input>...",
            file=sys.stderr,
        )
        return 2

    args = [Path(a) for a in argv[1:]]
    if len(args) == 2 and args[1].suffix.lower() == ".png" and not args[1].exists():
        remove_bg(args[0], args[1])
        return 0

    for src in args:
        if not src.is_file():
            print(f"skip (not a file): {src}", file=sys.stderr)
            continue
        remove_bg(src, out_path_for(src))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
