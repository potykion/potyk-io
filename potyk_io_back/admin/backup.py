from __future__ import annotations

import os
import re
import socket
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / "instance" / "main.db"

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


def upload_main_db() -> BackupResult:
    if not DB_PATH.is_file():
        return BackupResult(ok=False, message=f"Нет файла БД: {DB_PATH}")

    try:
        access_key = _required_env("YC_S3_ACCESS_KEY")
        secret_key = _required_env("YC_S3_SECRET_KEY")
        bucket = _required_env("YC_S3_BUCKET")
    except RuntimeError as exc:
        return BackupResult(ok=False, message=str(exc))

    endpoint = (
        os.environ.get("YC_S3_ENDPOINT") or "https://storage.yandexcloud.net"
    ).strip()
    region = (os.environ.get("YC_S3_REGION") or "ru-central1").strip()

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    object_key = f"main-{pc_name()}-{stamp}.db"

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    try:
        client.upload_file(str(DB_PATH), bucket, object_key)
    except (BotoCoreError, ClientError, OSError) as exc:
        return BackupResult(
            ok=False,
            message=f"Бекап не удался: {exc}",
            object_key=object_key,
        )

    return BackupResult(
        ok=True,
        message=f"Бекап залит: {bucket}/{object_key}",
        object_key=object_key,
    )
