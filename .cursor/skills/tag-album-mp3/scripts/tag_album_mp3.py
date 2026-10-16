# -*- coding: utf-8 -*-
"""Rename yt-dlp album MP3s and write ID3 tags from a YouTube playlist.

Example (PowerShell):
  python .cursor/skills/tag-album-mp3/scripts/tag_album_mp3.py `
    --dir "C:\\path\\to\\album" `
    --playlist "https://www.youtube.com/playlist?list=..." `
    --artist "Machine Girl" --album "The Ugly Art" --year 2026 `
    --cover "https://.../maxresdefault.jpg"
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

from mutagen.id3 import (
    APIC,
    ID3,
    TALB,
    TDRC,
    TIT2,
    TPE1,
    TRCK,
    TYER,
    error as ID3Error,
)
from mutagen.mp3 import MP3

ID_RE = re.compile(r"\[([^\]]+)\]\.mp3$", re.IGNORECASE)
NUM_RE = re.compile(r"^(\d{2})\. (.+)\.mp3$", re.IGNORECASE)
WIN_BAD = '<>:"/\\|?*？'


def safe_filename(title: str) -> str:
    out = "".join("_" if c in WIN_BAD else c for c in title).rstrip(" .")
    if not out or set(out) <= {"_", "¿"}:
        return "Question Marks"
    return out


def fetch_playlist(playlist_url: str, ytdlp: str) -> tuple[str, list[tuple[int, str, str]]]:
    cmd = [
        ytdlp,
        "--flat-playlist",
        "--print",
        "%(playlist_index)s|%(title)s|%(id)s|%(playlist_title)s",
        playlist_url,
    ]
    out = subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace")
    tracks: list[tuple[int, str, str]] = []
    album = ""
    for line in out.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        parts = line.split("|", 3)
        if len(parts) < 4:
            continue
        idx_s, title, vid, pl_title = parts
        album = album or pl_title
        tracks.append((int(idx_s), title, vid))
    if not tracks:
        raise SystemExit("empty playlist / yt-dlp returned nothing")
    return album, tracks


def load_cover(cover: str | None, dest_dir: Path) -> bytes:
    if not cover:
        local = dest_dir / "cover.jpg"
        if local.exists():
            return local.read_bytes()
        raise SystemExit("need --cover URL/path or cover.jpg in album folder")
    path = Path(cover)
    if path.exists():
        data = path.read_bytes()
    else:
        req = urllib.request.Request(cover, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=60).read()
        (dest_dir / "cover.jpg").write_bytes(data)
    return data


def tag_file(path: Path, *, title: str, artist: str, album: str, year: str, num: int, total: int, cover: bytes) -> None:
    audio = MP3(path, ID3=ID3)
    audio.delete()
    audio = MP3(path, ID3=ID3)
    try:
        audio.add_tags()
    except ID3Error:
        pass
    audio.tags.add(TIT2(encoding=3, text=title))
    audio.tags.add(TPE1(encoding=3, text=artist))
    audio.tags.add(TALB(encoding=3, text=album))
    audio.tags.add(TYER(encoding=3, text=year))
    audio.tags.add(TDRC(encoding=3, text=year))
    audio.tags.add(TRCK(encoding=3, text=f"{num}/{total}"))
    audio.tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover))
    audio.save(v2_version=3)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", required=True, type=Path, help="folder with .mp3")
    ap.add_argument("--playlist", required=True, help="YouTube playlist URL")
    ap.add_argument("--artist", required=True)
    ap.add_argument("--album", default="", help="default: playlist title")
    ap.add_argument("--year", required=True, help="YYYY of THIS release (reissue year if reissue)")
    ap.add_argument("--cover", default=None, help="cover URL or local path")
    ap.add_argument("--ytdlp", default="yt-dlp", help="yt-dlp binary (or path to yt-dlp.exe)")
    args = ap.parse_args()

    dest_dir: Path = args.dir
    if not dest_dir.is_dir():
        raise SystemExit(f"not a directory: {dest_dir}")

    pl_album, tracks = fetch_playlist(args.playlist, args.ytdlp)
    album = args.album or pl_album
    total = len(tracks)
    cover = load_cover(args.cover, dest_dir)

    by_id: dict[str, Path] = {}
    already: dict[int, Path] = {}
    for p in dest_dir.glob("*.mp3"):
        m = ID_RE.search(p.name)
        if m:
            by_id[m.group(1)] = p
            continue
        m2 = NUM_RE.match(p.name)
        if m2:
            already[int(m2.group(1))] = p

    missing: list[str] = []
    for num, title, vid in tracks:
        wanted = dest_dir / f"{num:02d}. {safe_filename(title)}.mp3"
        if num in already:
            src = already[num]
            if src.resolve() != wanted.resolve():
                if wanted.exists():
                    raise SystemExit(f"collision: {wanted.name}")
                src.rename(wanted)
            path = wanted
        elif vid in by_id:
            src = by_id[vid]
            if src.resolve() != wanted.resolve():
                if wanted.exists():
                    raise SystemExit(f"collision: {wanted.name}")
                src.rename(wanted)
            path = wanted
        else:
            missing.append(f"{num:02d}. {title} [{vid}]")
            continue
        tag_file(
            path,
            title=title,
            artist=args.artist,
            album=album,
            year=args.year,
            num=num,
            total=total,
            cover=cover,
        )
        print(f"ok {num:02d}/{total} {path.name}")

    if missing:
        print("\nmissing:", file=sys.stderr)
        for line in missing:
            print(" ", line, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
