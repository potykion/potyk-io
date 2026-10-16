"""Скачать YouTube-плейлист через yt-dlp, проставить ID3 и собрать zip."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
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

REPO_ROOT = Path(__file__).resolve().parents[2]
YTDLP_EXE = REPO_ROOT / "static" / "potyk-mu" / "yt-dlp.exe"
WIN_BAD = '<>:"/\\|?*？'
ID_RE = re.compile(r"\[([^\]]+)\]\.mp3$", re.IGNORECASE)
LIST_ID_RE = re.compile(r"[?&]list=([a-zA-Z0-9_-]+)")
ITEM_RE = re.compile(r"Downloading item (\d+) of (\d+)", re.I)
PCT_RE = re.compile(r"\[download\]\s+([\d.]+)%")
DEST_RE = re.compile(r"Destination:\s*(.+)$", re.I)
EXTRACT_RE = re.compile(r"\[ExtractAudio\]", re.I)


@dataclass
class PlaylistTrack:
    index: int
    title: str
    video_id: str


def parse_track_title(raw: str) -> str:
    """`GODFLESH - Wake` → `Wake`; без разделителя — как есть."""
    title = (raw or "").strip()
    if not title:
        return title
    for sep in (" - ", " – ", " — "):
        if sep in title:
            tail = title.rsplit(sep, 1)[-1].strip()
            if tail:
                return tail
    return title


_YEAR_IN_PARENS_RE = re.compile(r"^(?P<body>.*)\((?P<year>(?:19|20)\d{2})\)\s*$")


def parse_album_title_and_year(raw: str) -> tuple[str, str | None]:
    """`Album (1996)` → (`Album`, `1996`); иначе год None, название как есть."""
    title = (raw or "").strip() or "Album"
    m = _YEAR_IN_PARENS_RE.match(title)
    if not m:
        return title, None
    body = m.group("body").rstrip(" :–—-").strip()
    year = m.group("year")
    return (body or title), year


def _year_from_yyyymmdd(value: str | None) -> str:
    if not value:
        return ""
    m = re.match(r"((?:19|20)\d{2})", str(value).strip())
    return m.group(1) if m else ""


@dataclass
class PlaylistMeta:
    url: str
    album: str
    artist: str
    year: str
    cover_url: str
    track_count: int
    tracks: list[PlaylistTrack]


@dataclass
class DownloadProgress:
    """Прогресс скачивания yt-dlp (один файл / позиция в плейлисте)."""

    message: str
    current: int | None = None
    total: int | None = None
    file_percent: float | None = None


class DownloadError(Exception):
    pass


def _ytdlp_bin() -> str:
    if YTDLP_EXE.is_file():
        return str(YTDLP_EXE)
    found = shutil.which("yt-dlp")
    if found:
        return found
    raise DownloadError("yt-dlp.exe не найден в static/potyk-mu/")


def _ytdlp_base() -> list[str]:
    cmd = [_ytdlp_bin()]
    if shutil.which("node"):
        cmd.extend(["--js-runtimes", "node"])
    return cmd


def _run(cmd: list[str], *, timeout: int = 120) -> str:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise DownloadError("yt-dlp завис по таймауту") from exc
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise DownloadError(err or f"yt-dlp exit {proc.returncode}")
    return proc.stdout


def playlist_list_id(url: str) -> str | None:
    m = LIST_ID_RE.search(url)
    return m.group(1) if m else None


def safe_filename(title: str) -> str:
    out = "".join("_" if c in WIN_BAD else c for c in title).rstrip(" .")
    if not out or set(out) <= {"_", "¿"}:
        return "Question Marks"
    return out


def safe_zip_stem(artist: str, album: str) -> str:
    raw = f"{artist} - {album}".strip(" -")
    return safe_filename(raw) or "album"


def _pick_cover_url(data: dict, list_id: str | None) -> str:
    thumbs = data.get("thumbnails") or []
    if thumbs:
        best = max(thumbs, key=lambda t: (t.get("height") or 0) * (t.get("width") or 0))
        url = best.get("url") or ""
        if url:
            return url
    if list_id and list_id.startswith("OLAK"):
        return f"https://i9.ytimg.com/s_p/{list_id}/maxresdefault.jpg"
    entries = [e for e in (data.get("entries") or []) if e]
    if entries:
        vid = entries[0].get("id")
        if vid:
            return f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
    return ""


def fetch_playlist_meta(url: str) -> PlaylistMeta:
    url = (url or "").strip()
    if not url or "list=" not in url:
        raise DownloadError("Нужна ссылка на плейлист (с list=...)")

    raw = _run(
        [
            *_ytdlp_base(),
            "--flat-playlist",
            "-J",
            "--no-download",
            url,
        ],
        timeout=180,
    )
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DownloadError("Не удалось разобрать ответ yt-dlp") from exc

    entries = [e for e in (data.get("entries") or []) if e]
    raw_album = (data.get("title") or "").strip() or "Album"
    album, year_from_title = parse_album_title_and_year(raw_album)
    artist = (
        (data.get("uploader") or data.get("channel") or "").strip() or "Unknown"
    )
    list_id = playlist_list_id(url) or data.get("id")
    cover_url = _pick_cover_url(data, list_id)

    tracks: list[PlaylistTrack] = []
    for i, entry in enumerate(entries, start=1):
        vid = (entry.get("id") or "").strip()
        raw_title = (entry.get("title") or "").strip() or f"Track {i}"
        title = parse_track_title(raw_title)
        if not vid:
            continue
        tracks.append(PlaylistTrack(index=i, title=title, video_id=vid))

    if year_from_title:
        year = year_from_title
    else:
        # yt-dlp отдаёт modified_date плейлиста (YYYYMMDD); отдельного created нет
        year = _year_from_yyyymmdd(data.get("modified_date"))
        if not year and data.get("epoch"):
            try:
                from datetime import datetime, timezone

                year = str(
                    datetime.fromtimestamp(int(data["epoch"]), tz=timezone.utc).year
                )
            except (TypeError, ValueError, OSError):
                year = ""

    return PlaylistMeta(
        url=url,
        album=album,
        artist=artist,
        year=year,
        cover_url=cover_url,
        track_count=len(tracks),
        tracks=tracks,
    )


def fetch_cover_bytes(cover_url: str) -> bytes | None:
    cover_url = (cover_url or "").strip()
    if not cover_url:
        return None
    req = urllib.request.Request(cover_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except Exception as exc:
        raise DownloadError(f"Не скачалась обложка: {exc}") from exc
    if not data:
        raise DownloadError("Пустая обложка")
    return data


def _tag_mp3(
    path: Path,
    *,
    title: str,
    artist: str,
    album: str,
    year: str,
    num: int,
    total: int,
    cover: bytes | None,
) -> None:
    audio = MP3(path, ID3=ID3)
    audio.delete()
    audio = MP3(path, ID3=ID3)
    try:
        audio.add_tags()
    except ID3Error:
        pass
    assert audio.tags is not None
    audio.tags.add(TIT2(encoding=3, text=title))
    audio.tags.add(TPE1(encoding=3, text=artist))
    audio.tags.add(TALB(encoding=3, text=album))
    if year:
        audio.tags.add(TYER(encoding=3, text=year))
        audio.tags.add(TDRC(encoding=3, text=year))
    audio.tags.add(TRCK(encoding=3, text=f"{num}/{total}"))
    if cover:
        mime = "image/jpeg"
        if cover[:8] == b"\x89PNG\r\n\x1a\n":
            mime = "image/png"
        audio.tags.add(
            APIC(encoding=3, mime=mime, type=3, desc="Cover", data=cover)
        )
    audio.save(v2_version=3)


def _tracks_from_flat(url: str) -> list[tuple[int, str, str]]:
    out = _run(
        [
            *_ytdlp_base(),
            "--flat-playlist",
            "--print",
            "%(playlist_index)s|%(title)s|%(id)s",
            url,
        ],
        timeout=180,
    )
    tracks: list[tuple[int, str, str]] = []
    for line in out.splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        idx_s, title, vid = line.split("|", 2)
        try:
            tracks.append((int(idx_s), title, vid))
        except ValueError:
            continue
    if not tracks:
        raise DownloadError("В плейлисте нет треков")
    return tracks


def download_playlist_mp3s(
    url: str,
    dest_dir: Path,
    *,
    on_progress: Callable[[DownloadProgress], None] | None = None,
    track_total: int | None = None,
) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(dest_dir / "%(playlist_index)02d. %(title)s [%(id)s].%(ext)s")
    cmd = [
        *_ytdlp_base(),
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--yes-playlist",
        "--newline",
        "-o",
        outtmpl,
        url,
    ]
    def emit(
        *,
        current: int | None,
        total: int | None,
        file_percent: float | None,
        message: str,
    ) -> None:
        if on_progress is None:
            return
        on_progress(
            DownloadProgress(
                message=message,
                current=current,
                total=total,
                file_percent=file_percent,
            )
        )

    emit(current=None, total=track_total, file_percent=None, message="Запускаю yt-dlp…")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
    except OSError as exc:
        raise DownloadError(f"Не запустился yt-dlp: {exc}") from exc

    assert proc.stdout is not None
    current_item: int | None = None
    total_items = track_total
    last_name = ""
    err_tail: list[str] = []

    for raw_line in proc.stdout:
        line = raw_line.strip()
        if not line:
            continue
        err_tail.append(line)
        if len(err_tail) > 40:
            err_tail.pop(0)

        m_item = ITEM_RE.search(line)
        if m_item:
            current_item = int(m_item.group(1))
            total_items = int(m_item.group(2))
            emit(
                current=current_item,
                total=total_items,
                file_percent=0,
                message=f"Трек {current_item}/{total_items}",
            )
            continue

        m_pct = PCT_RE.search(line)
        if m_pct:
            pct = float(m_pct.group(1))
            msg = f"Трек {current_item}/{total_items}" if current_item and total_items else "Скачивание"
            if last_name:
                msg = f"{msg}: {last_name}"
            msg = f"{msg} — {pct:.0f}%"
            emit(
                current=current_item,
                total=total_items,
                file_percent=pct,
                message=msg,
            )
            continue

        m_dest = DEST_RE.search(line)
        if m_dest:
            last_name = Path(m_dest.group(1).strip()).name
            continue

        if EXTRACT_RE.search(line):
            msg = (
                f"Трек {current_item}/{total_items}: конвертация в mp3"
                if current_item and total_items
                else "Конвертация в mp3"
            )
            emit(
                current=current_item,
                total=total_items,
                file_percent=100,
                message=msg,
            )

    code = proc.wait(timeout=60 * 60)
    if code != 0:
        err = "\n".join(err_tail).strip()
        raise DownloadError(err or f"yt-dlp exit {code}")


def rename_and_tag(
    dest_dir: Path,
    tracks: list[tuple[int, str, str]],
    *,
    artist: str,
    album: str,
    year: str,
    cover: bytes | None,
    on_track: Callable[[int, str], None] | None = None,
) -> list[Path]:
    by_id: dict[str, Path] = {}
    for p in dest_dir.glob("*.mp3"):
        m = ID_RE.search(p.name)
        if m:
            by_id[m.group(1)] = p

    total = len(tracks)
    result: list[Path] = []
    missing: list[str] = []
    done = 0
    for num, title, vid in tracks:
        src = by_id.get(vid)
        if src is None:
            missing.append(f"{num:02d}. {title} [{vid}]")
            continue
        dest = dest_dir / f"{num:02d}. {safe_filename(title)}.mp3"
        if src.resolve() != dest.resolve():
            if dest.exists():
                dest.unlink()
            src.rename(dest)
        _tag_mp3(
            dest,
            title=title,
            artist=artist,
            album=album,
            year=year,
            num=num,
            total=total,
            cover=cover,
        )
        result.append(dest)
        done += 1
        if on_track:
            on_track(done, title)

    if not result:
        raise DownloadError(
            "Не скачалось ни одного трека"
            + (f": {missing[0]}" if missing else "")
        )
    return result


def build_zip(files: list[Path], zip_path: Path) -> Path:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, arcname=f.name)
    return zip_path


def download_tag_zip(
    *,
    url: str,
    artist: str,
    album: str,
    year: str,
    cover_url: str,
) -> tuple[Path, Path]:
    """Синхронный путь (без джобы). Возвращает (zip_path, work_dir)."""
    artist = artist.strip() or "Unknown"
    album = album.strip() or "Album"
    year = year.strip()
    tracks = _tracks_from_flat(url)
    cover = fetch_cover_bytes(cover_url) if cover_url.strip() else None

    work_dir = Path(tempfile.mkdtemp(prefix="potyk-mu-dl-"))
    try:
        download_playlist_mp3s(url, work_dir, track_total=len(tracks))
        files = rename_and_tag(
            work_dir,
            tracks,
            artist=artist,
            album=album,
            year=year,
            cover=cover,
        )
        zip_path = work_dir / f"{safe_zip_stem(artist, album)}.zip"
        build_zip(files, zip_path)
        return zip_path, work_dir
    except Exception:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise
