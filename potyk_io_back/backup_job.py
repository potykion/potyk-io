"""CLI-вход для potyk-io-backup.timer (обход import side-effects admin.__init__)."""
from __future__ import annotations

from potyk_io_back.admin.backup import main

if __name__ == "__main__":
    raise SystemExit(main())
