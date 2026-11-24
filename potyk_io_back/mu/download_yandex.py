"""Скачать альбом Яндекс Музыки через yandex-music-api → mp3 + ID3 → zip."""
from __future__ import annotations

import os
import re
import time
from collections.abc import Callable
from pathlib import Path

from yandex_music import Client
from yandex_music.exceptions import YandexMusicError

from potyk_io_back.mu.download_album import (
    DownloadError,
    DownloadProgress,
    PlaylistMeta,
    PlaylistTrack,
    _tag_mp3,
    safe_filename,
)

ALBUM_ID_RE = re.compile(
    r"(?:music\.yandex\.(?:ru|com|by|kz)|music\.yandex\.ua)/album/(\d+)",
    re.I,
)
TOKEN_ENV = "YANDEX_MUSIC_TOKEN"


def parse_album_id(url: str) -> int | None:
    url = (url or "").strip()
    if not url:
        return None
    m = ALBUM_ID_RE.search(url)
    if m:
        return int(m.group(1))
    if url.isdigit():
        return int(url)
    return None


def _token() -> str:
    token = (os.environ.get(TOKEN_ENV) or "").strip()
    if not token:
        raise DownloadError(f"Не задан {TOKEN_ENV} в .env")
    return token


def _client() -> Client:
    try:
        return Client(_token()).init()
    except YandexMusicError as exc:
        raise DownloadError(f"Яндекс Музыка: {exc}") from exc
    except Exception as exc:
        raise DownloadError(f"Не удалось авторизоваться в Яндекс Музыке: {exc}") from exc


def cover_url_from_uri(cover_uri: str | None, size: str = "1000x1000") -> str:
    uri = (cover_uri or "").strip()
    if not uri:
        return ""
    if "%%" in uri:
        uri = uri.replace("%%", size)
    if uri.startswith("//"):
        return "https:" + uri
    if uri.startswith("http://") or uri.startswith("https://"):
        return uri
    return "https://" + uri


def fetch_album_meta(url: str) -> PlaylistMeta:
    album_id = parse_album_id(url)
    if album_id is None:
        raise DownloadError(
            "Нужна ссылка на альбом Яндекс Музыки "
            "(например https://music.yandex.ru/album/44831600)"
        )

    client = _client()
    try:
        album = client.albums_with_tracks(album_id)
    except YandexMusicError as exc:
        raise DownloadError(f"Не удалось получить альбом: {exc}") from exc

    if album is None:
        raise DownloadError(f"Альбом {album_id} не найден")

    artist = ", ".join(
        a.name for a in (album.artists or []) if getattr(a, "name", None)
    ) or "Unknown"
    album_title = (album.title or "").strip() or "Album"
    year = str(album.year) if album.year else ""
    cover_url = cover_url_from_uri(album.cover_uri)

    tracks: list[PlaylistTrack] = []
    index = 0
    for volume in album.volumes or []:
        for track in volume:
            if track is None:
                continue
            index += 1
            title = (track.title or "").strip() or f"Track {index}"
            version = getattr(track, "version", None)
            if version:
                title = f"{title} ({version})"
            # номер из track_position, если есть; иначе порядковый
            num = index
            if track.albums:
                pos = getattr(track.albums[0], "track_position", None)
                if pos is not None and getattr(pos, "index", None):
                    num = int(pos.index)
            tid = str(track.id)
            tracks.append(PlaylistTrack(index=num, title=title, video_id=tid))

    if not tracks:
        raise DownloadError("В альбоме нет треков")

    # если индексы с дисков пересекаются — перенумеруем подряд
    if len({t.index for t in tracks}) != len(tracks):
        tracks = [
            PlaylistTrack(index=i, title=t.title, video_id=t.video_id)
            for i, t in enumerate(tracks, start=1)
        ]
    else:
        tracks.sort(key=lambda t: t.index)

    return PlaylistMeta(
        url=(url or "").strip() or f"https://music.yandex.ru/album/{album_id}",
        album=album_title,
        artist=artist,
        year=year,
        cover_url=cover_url,
        track_count=len(tracks),
        tracks=tracks,
    )


_TRACK_DOWNLOAD_TIMEOUT = 60
_TRACK_DOWNLOAD_TRIES = 3
# (codec, bitrate) — fallback если 192 mp3 недоступен
_DOWNLOAD_VARIANTS: tuple[tuple[str, int], ...] = (
    ("mp3", 192),
    ("mp3", 128),
    ("mp3", 320),
)


def _download_track_with_retries(
    ym_track: object,
    dest: Path,
    meta_track: PlaylistTrack,
    *,
    on_heartbeat: Callable[[str], None] | None = None,
) -> None:
    last_err: Exception | None = None
    for attempt in range(1, _TRACK_DOWNLOAD_TRIES + 1):
        if dest.exists():
            try:
                dest.unlink()
            except OSError:
                pass
        for codec, bitrate in _DOWNLOAD_VARIANTS:
            if on_heartbeat:
                on_heartbeat(
                    f"Трек {meta_track.index}: {meta_track.title} "
                    f"({codec} {bitrate}, попытка {attempt})"
                )
            try:
                ym_track.download(  # type: ignore[attr-defined]
                    str(dest),
                    codec=codec,
                    bitrate_in_kbps=bitrate,
                    timeout=_TRACK_DOWNLOAD_TIMEOUT,
                )
                if dest.is_file() and dest.stat().st_size >= 1024:
                    return
                last_err = DownloadError("пустой файл")
            except YandexMusicError as exc:
                last_err = exc
            except Exception as exc:  # noqa: BLE001 — сеть/таймаут
                last_err = exc
        if attempt < _TRACK_DOWNLOAD_TRIES:
            time.sleep(1.5 * attempt)

    raise DownloadError(
        f"Не скачался трек {meta_track.index} «{meta_track.title}»: {last_err}"
    )


def download_album_tracks(
    *,
    album_url: str,
    dest_dir: Path,
    tracks: list[PlaylistTrack],
    on_progress: Callable[[DownloadProgress], None] | None = None,
) -> list[tuple[PlaylistTrack, Path]]:
    """Скачивает треки по id из meta/form. Возвращает [(track, path), ...]."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    album_id = parse_album_id(album_url)
    if album_id is None:
        raise DownloadError("Некорректный URL альбома")

    client = _client()
    try:
        album = client.albums_with_tracks(album_id)
    except YandexMusicError as exc:
        raise DownloadError(f"Не удалось получить альбом: {exc}") from exc
    if album is None:
        raise DownloadError(f"Альбом {album_id} не найден")

    by_id: dict[str, object] = {}
    for volume in album.volumes or []:
        for track in volume:
            if track is not None and track.id is not None:
                by_id[str(track.id)] = track

    total = len(tracks)
    result: list[tuple[PlaylistTrack, Path]] = []

    def emit(current: int, message: str, file_percent: float | None = None) -> None:
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

    for i, meta_track in enumerate(tracks, start=1):
        ym_track = by_id.get(meta_track.video_id)
        if ym_track is None:
            raise DownloadError(
                f"Трек {meta_track.index}: id {meta_track.video_id} не найден в альбоме"
            )
        emit(i, f"Трек {i}/{total}: {meta_track.title}", 0)
        dest = dest_dir / f"{meta_track.index:02d}. {safe_filename(meta_track.title)}.mp3"

        def _hb(msg: str, _i: int = i) -> None:
            emit(_i, msg, 0)

        _download_track_with_retries(
            ym_track, dest, meta_track, on_heartbeat=_hb
        )
        emit(i, f"Трек {i}/{total}: {meta_track.title}", 100)
        result.append((meta_track, dest))

    if not result:
        raise DownloadError("Не скачалось ни одного трека")
    return result


def tag_downloaded_tracks(
    pairs: list[tuple[PlaylistTrack, Path]],
    *,
    artist: str,
    album: str,
    year: str,
    cover: bytes | None,
    on_track: Callable[[int, str], None] | None = None,
) -> list[Path]:
    total = len(pairs)
    files: list[Path] = []
    for i, (meta_track, path) in enumerate(pairs, start=1):
        _tag_mp3(
            path,
            title=meta_track.title,
            artist=artist,
            album=album,
            year=year,
            num=meta_track.index,
            total=total,
            cover=cover,
        )
        files.append(path)
        if on_track:
            on_track(i, meta_track.title)
    return files
