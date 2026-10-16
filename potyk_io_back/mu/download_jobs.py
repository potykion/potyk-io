"""Фоновые джобы скачивания альбома: состояние на диске + поллинг."""
from __future__ import annotations

import json
import os
import shutil
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from potyk_io_back.mu.download_album import (
    DownloadError,
    DownloadProgress,
    PlaylistTrack,
    build_zip,
    download_playlist_mp3s,
    fetch_cover_bytes,
    rename_and_tag,
    safe_zip_stem,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
JOBS_DIR = REPO_ROOT / "instance" / "mu_dl_jobs"
JOB_TTL_SEC = 60 * 60

_write_lock = threading.Lock()
_last_write_at: dict[str, float] = {}
_last_write_key: dict[str, str] = {}


ProgressCb = Callable[["JobProgress"], None]


@dataclass
class JobProgress:
    stage: str  # queued | download | tag | zip | done | error
    message: str = ""
    current: int | None = None
    total: int | None = None
    file_percent: float | None = None
    overall_percent: float = 0
    error: str | None = None
    download_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class JobRecord:
    id: str
    progress: JobProgress
    zip_path: str | None = None
    work_dir: str | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            **self.progress.to_dict(),
            "zip_ready": bool(self.zip_path and Path(self.zip_path).is_file()),
        }


def _job_dir(job_id: str) -> Path:
    return JOBS_DIR / job_id


def _state_path(job_id: str) -> Path:
    return _job_dir(job_id) / "state.json"


def _write_state(record: JobRecord, *, force: bool = False) -> None:
    """Атомарная запись state.json с ретраями (Windows WinError 5)."""
    d = _job_dir(record.id)
    d.mkdir(parents=True, exist_ok=True)
    record.updated_at = time.time()
    payload = {
        "id": record.id,
        "progress": record.progress.to_dict(),
        "zip_path": record.zip_path,
        "work_dir": record.work_dir,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }
    text = json.dumps(payload, ensure_ascii=False)
    path = _state_path(record.id)
    tmp = d / f"state.{os.getpid()}.{threading.get_ident()}.tmp"

    with _write_lock:
        if not force:
            key = (
                f"{record.progress.stage}|{int(record.progress.overall_percent)}|"
                f"{record.progress.message}|{record.progress.error}"
            )
            now = time.time()
            last_t = _last_write_at.get(record.id, 0)
            last_k = _last_write_key.get(record.id)
            # не чаще 4 раз/сек и не дублируем одинаковый статус
            if key == last_k and now - last_t < 0.25:
                return
            if now - last_t < 0.15 and record.progress.stage == "download":
                return

        last_err: Exception | None = None
        for attempt in range(8):
            try:
                tmp.write_text(text, encoding="utf-8")
                os.replace(tmp, path)
                _last_write_at[record.id] = time.time()
                _last_write_key[record.id] = (
                    f"{record.progress.stage}|{int(record.progress.overall_percent)}|"
                    f"{record.progress.message}|{record.progress.error}"
                )
                return
            except OSError as exc:
                last_err = exc
                time.sleep(0.02 * (attempt + 1))
                try:
                    if tmp.exists():
                        tmp.unlink()
                except OSError:
                    pass
        if last_err:
            raise last_err


def read_job(job_id: str) -> JobRecord | None:
    path = _state_path(job_id)
    if not path.is_file():
        return None
    try:
        with _write_lock:
            data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    prog = data.get("progress") or {}
    return JobRecord(
        id=data["id"],
        progress=JobProgress(
            stage=prog.get("stage") or "queued",
            message=prog.get("message") or "",
            current=prog.get("current"),
            total=prog.get("total"),
            file_percent=prog.get("file_percent"),
            overall_percent=float(prog.get("overall_percent") or 0),
            error=prog.get("error"),
            download_name=prog.get("download_name"),
        ),
        zip_path=data.get("zip_path"),
        work_dir=data.get("work_dir"),
        created_at=float(data.get("created_at") or 0),
        updated_at=float(data.get("updated_at") or 0),
    )


def cleanup_job(job_id: str) -> None:
    d = _job_dir(job_id)
    if d.is_dir():
        shutil.rmtree(d, ignore_errors=True)
    _last_write_at.pop(job_id, None)
    _last_write_key.pop(job_id, None)


def cleanup_stale_jobs() -> None:
    if not JOBS_DIR.is_dir():
        return
    now = time.time()
    for child in JOBS_DIR.iterdir():
        if not child.is_dir():
            continue
        state = child / "state.json"
        try:
            mtime = state.stat().st_mtime if state.is_file() else child.stat().st_mtime
        except OSError:
            continue
        if now - mtime > JOB_TTL_SEC:
            shutil.rmtree(child, ignore_errors=True)


def _set_progress(record: JobRecord, progress: JobProgress, *, force: bool = False) -> None:
    record.progress = progress
    _write_state(record, force=force)


def _run_job(
    job_id: str,
    *,
    url: str,
    artist: str,
    album: str,
    year: str,
    cover_url: str,
    tracks: list[PlaylistTrack],
) -> None:
    record = read_job(job_id)
    if record is None:
        return

    def on_progress(p: JobProgress, *, force: bool = False) -> None:
        _set_progress(record, p, force=force)

    work_dir = _job_dir(job_id) / "work"
    work_dir.mkdir(parents=True, exist_ok=True)
    record.work_dir = str(work_dir)
    _write_state(record, force=True)

    try:
        artist = artist.strip() or "Unknown"
        album = album.strip() or "Album"
        year = year.strip()
        if not tracks:
            raise DownloadError("Нет треков")

        total = len(tracks)
        track_tuples = [(t.index, t.title, t.video_id) for t in tracks]

        cover = None
        if cover_url.strip():
            on_progress(
                JobProgress(
                    stage="download",
                    message="Обложка…",
                    total=total,
                    overall_percent=3,
                ),
                force=True,
            )
            cover = fetch_cover_bytes(cover_url)

        def dl_cb(p: DownloadProgress) -> None:
            overall = 5.0
            if p.total and p.current:
                overall = 5 + 75 * (
                    ((p.current - 1) + (p.file_percent or 0) / 100.0) / p.total
                )
            on_progress(
                JobProgress(
                    stage="download",
                    message=p.message,
                    current=p.current,
                    total=p.total or total,
                    file_percent=p.file_percent,
                    overall_percent=min(80.0, max(5.0, overall)),
                )
            )

        on_progress(
            JobProgress(
                stage="download",
                message="Запускаю yt-dlp…",
                total=total,
                overall_percent=5,
            ),
            force=True,
        )
        download_playlist_mp3s(url, work_dir, on_progress=dl_cb, track_total=total)

        on_progress(
            JobProgress(
                stage="tag",
                message="Теги и имена файлов…",
                total=total,
                overall_percent=82,
            ),
            force=True,
        )

        def tag_cb(current: int, title: str) -> None:
            pct = 82 + 13 * (current / max(total, 1))
            on_progress(
                JobProgress(
                    stage="tag",
                    message=f"Тег {current}/{total}: {title}",
                    current=current,
                    total=total,
                    overall_percent=min(95.0, pct),
                ),
                force=True,
            )

        files = rename_and_tag(
            work_dir,
            track_tuples,
            artist=artist,
            album=album,
            year=year,
            cover=cover,
            on_track=tag_cb,
        )

        on_progress(
            JobProgress(
                stage="zip",
                message="Собираю архив…",
                total=total,
                overall_percent=96,
            ),
            force=True,
        )
        zip_name = f"{safe_zip_stem(artist, album)}.zip"
        zip_path = _job_dir(job_id) / zip_name
        build_zip(files, zip_path)
        record.zip_path = str(zip_path)
        _write_state(record, force=True)

        on_progress(
            JobProgress(
                stage="done",
                message="Готово",
                current=total,
                total=total,
                overall_percent=100,
                download_name=zip_name,
            ),
            force=True,
        )
    except DownloadError as exc:
        on_progress(
            JobProgress(
                stage="error",
                message="Ошибка",
                error=str(exc),
                overall_percent=record.progress.overall_percent,
            ),
            force=True,
        )
    except Exception as exc:
        on_progress(
            JobProgress(
                stage="error",
                message="Ошибка",
                error=str(exc),
                overall_percent=record.progress.overall_percent,
            ),
            force=True,
        )


def start_download_job(
    *,
    url: str,
    artist: str,
    album: str,
    year: str,
    cover_url: str,
    tracks: list[PlaylistTrack],
) -> str:
    cleanup_stale_jobs()
    job_id = uuid.uuid4().hex
    record = JobRecord(
        id=job_id,
        progress=JobProgress(stage="queued", message="В очереди…", overall_percent=0),
    )
    _write_state(record, force=True)
    thread = threading.Thread(
        target=_run_job,
        kwargs={
            "job_id": job_id,
            "url": url,
            "artist": artist,
            "album": album,
            "year": year,
            "cover_url": cover_url,
            "tracks": tracks,
        },
        name=f"mu-dl-{job_id[:8]}",
        daemon=True,
    )
    thread.start()
    return job_id
