from __future__ import annotations

import os
import re
import socket
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from flask.helpers import get_debug_flag
from werkzeug.serving import is_running_from_reloader

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "instance" / "main.db"
BACKUP_RETENTION_DAYS = 10

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True)
class BackupResult:
    ok: bool
    message: str
    object_key: str = ""


def pc_name() -> str:
    raw = (
        (os.environ.get("BACKUP_PC_NAME") or "").strip()
        or (os.environ.get("COMPUTERNAME") or "").strip()
        or (os.environ.get("HOSTNAME") or "").strip()
        or socket.gethostname()
    )
    cleaned = _SAFE_NAME.sub("-", raw).strip("-._") or "unknown"
    return cleaned


def _required_env(name: str) -> str:
    value = (os.environ.get(name) or "").strip()
    if not value:
        raise RuntimeError(f"Не задан {name} в .env")
    return value


def _s3_client_and_bucket():
    access_key = _required_env("YC_S3_ACCESS_KEY")
    secret_key = _required_env("YC_S3_SECRET_KEY")
    bucket = _required_env("YC_S3_BUCKET")
    endpoint = (
        os.environ.get("YC_S3_ENDPOINT") or "https://storage.yandexcloud.net"
    ).strip()
    region = (os.environ.get("YC_S3_REGION") or "ru-central1").strip()
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return client, bucket


def rotate_backups(
    *,
    retention_days: int = BACKUP_RETENTION_DAYS,
    name: str | None = None,
) -> BackupResult:
    """Удаляет в бакете бекапы этого ПК старше retention_days."""
    try:
        client, bucket = _s3_client_and_bucket()
    except RuntimeError as exc:
        return BackupResult(ok=False, message=str(exc))

    prefix = f"main-{name or pc_name()}-"
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    deleted = 0

    try:
        paginator = client.get_paginator("list_objects_v2")
        to_delete: list[dict[str, str]] = []
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents") or []:
                key = obj.get("Key") or ""
                last_modified = obj.get("LastModified")
                if not key or last_modified is None:
                    continue
                if last_modified.tzinfo is None:
                    last_modified = last_modified.replace(tzinfo=timezone.utc)
                if last_modified < cutoff:
                    to_delete.append({"Key": key})

        for i in range(0, len(to_delete), 1000):
            chunk = to_delete[i : i + 1000]
            client.delete_objects(
                Bucket=bucket,
                Delete={"Objects": chunk, "Quiet": True},
            )
            deleted += len(chunk)
    except (BotoCoreError, ClientError, OSError) as exc:
        return BackupResult(ok=False, message=f"Ротация не удалась: {exc}")

    return BackupResult(
        ok=True,
        message=f"Ротация: удалено {deleted} (старше {retention_days} дн.)",
    )


def upload_main_db(*, rotate: bool = True) -> BackupResult:
    if not DB_PATH.is_file():
        return BackupResult(ok=False, message=f"Нет файла БД: {DB_PATH}")

    try:
        client, bucket = _s3_client_and_bucket()
    except RuntimeError as exc:
        return BackupResult(ok=False, message=str(exc))

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    object_key = f"main-{pc_name()}-{stamp}.db"

    try:
        client.upload_file(str(DB_PATH), bucket, object_key)
    except (BotoCoreError, ClientError, OSError) as exc:
        return BackupResult(
            ok=False,
            message=f"Бекап не удался: {exc}",
            object_key=object_key,
        )

    message = f"Бекап залит: {bucket}/{object_key}"
    if rotate:
        rot = rotate_backups()
        if rot.ok:
            message = f"{message}; {rot.message}"
        else:
            message = f"{message}; ротация: {rot.message}"

    return BackupResult(ok=True, message=message, object_key=object_key)


def startup_backup_if_local(*, debug: bool | None = None) -> None:
    """Бекап при старте worker'а `flask run --debug` (не parent reloader, не прод)."""
    if debug is None:
        debug = get_debug_flag()
    if not debug or not is_running_from_reloader():
        return
    result = upload_main_db()
    print(f"[backup] {result.message}", flush=True)
