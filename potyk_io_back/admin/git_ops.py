"""Список незакоммиченного, коммит и пуш в remote текущей ветки."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class GitResult:
    ok: bool
    message: str
    files: list[str]


def _run(args: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def list_uncommitted() -> list[str]:
    proc = _run(["git", "status", "--porcelain", "-u"])
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "git status failed").strip())
    files: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        # XY PATH or XY ORIG -> PATH for renames
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path.strip())
    return files


def commit_and_push(message: str = "Посты и файлы из админки.") -> GitResult:
    try:
        files = list_uncommitted()
    except RuntimeError as exc:
        return GitResult(ok=False, message=str(exc), files=[])

    if not files:
        return GitResult(ok=True, message="Нечего коммитить — всё чисто.", files=[])

    add = _run(["git", "add", "-A"])
    if add.returncode != 0:
        return GitResult(
            ok=False,
            message=(add.stderr or add.stdout or "git add не удался").strip(),
            files=files,
        )

    commit = _run(["git", "commit", "-m", message])
    if commit.returncode != 0:
        err = (commit.stderr or commit.stdout or "git commit не удался").strip()
        return GitResult(ok=False, message=err, files=files)

    push = _run(["git", "push"], timeout=180)
    if push.returncode != 0:
        err = (push.stderr or push.stdout or "git push не удался").strip()
        return GitResult(
            ok=False,
            message=f"Коммит создан, но push не прошёл: {err}",
            files=[],
        )

    return GitResult(
        ok=True,
        message="Закоммичено и запушено.",
        files=[],
    )
