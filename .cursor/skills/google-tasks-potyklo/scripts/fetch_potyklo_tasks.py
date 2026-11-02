#!/usr/bin/env python3
"""Fetch incomplete tasks from a Google Tasks list (default: 🤪 potyklo).

Auth: ``.cursor/secrets/google_tasks_token.json`` from setup_auth.py
(Desktop OAuth client + tasks.readonly). See ../SKILL.md.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
SECRETS = ROOT / ".cursor" / "secrets"
TOKEN_PATH = Path(os.environ.get("GOOGLE_TASKS_TOKEN", str(SECRETS / "google_tasks_token.json")))
# legacy name from aborted gcloud-ADC attempt
LEGACY_ADC = SECRETS / "google_tasks_adc.json"
DEFAULT_LIST = "potyklo"
TASKS_API = "https://tasks.googleapis.com/tasks/v1"
TOKEN_URI = "https://oauth2.googleapis.com/token"


def load_token_file() -> dict[str, Any]:
    path = TOKEN_PATH if TOKEN_PATH.is_file() else LEGACY_ADC
    if not path.is_file():
        sys.exit(
            f"Missing {TOKEN_PATH}\n"
            "Run: python .cursor/skills/google-tasks-potyklo/scripts/setup_auth.py\n"
            "(needs .cursor/secrets/google_tasks_client.json — see SKILL.md)"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("type") and data.get("type") != "authorized_user":
        sys.exit(f"Expected authorized_user in {path}, got type={data.get('type')!r}")
    for key in ("client_id", "client_secret", "refresh_token"):
        if not data.get(key):
            sys.exit(f"Token file missing {key}: {path}")
    return data


def access_token(adc: dict[str, Any]) -> str:
    body = urllib.parse.urlencode(
        {
            "client_id": adc["client_id"],
            "client_secret": adc["client_secret"],
            "refresh_token": adc["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URI,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:500]
        sys.exit(f"Token refresh failed HTTP {e.code}: {err}")
    tok = data.get("access_token")
    if not tok:
        sys.exit(f"No access_token in refresh response: {data!r}")
    return tok


def api_get(token: str, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    qs = f"?{urllib.parse.urlencode(params)}" if params else ""
    req = urllib.request.Request(
        f"{TASKS_API}{path}{qs}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:800]
        if e.code == 403 and "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in body:
            sys.exit(
                "Token has no Tasks scope. Re-run setup_auth.py with a Desktop "
                "OAuth client (not gcloud ADC)."
            )
        sys.exit(f"Tasks API HTTP {e.code}: {body}")


def list_all_pages(
    token: str, path: str, params: dict[str, str], items_key: str = "items"
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    page_token: str | None = None
    while True:
        p = dict(params)
        if page_token:
            p["pageToken"] = page_token
        data = api_get(token, path, p)
        items.extend(data.get(items_key) or [])
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return items


def normalize(s: str) -> str:
    return "".join(ch.lower() for ch in s if ch.isalnum())


def find_tasklist(lists: list[dict[str, Any]], needle: str) -> dict[str, Any]:
    n = normalize(needle)
    for it in lists:
        if normalize(it.get("title") or "") == n:
            return it
    matches = [it for it in lists if n in normalize(it.get("title") or "")]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        titles = ", ".join(repr(m.get("title")) for m in matches)
        sys.exit(f"Ambiguous list {needle!r}: {titles}")
    titles = ", ".join(repr(it.get("title")) for it in lists)
    sys.exit(f"List {needle!r} not found. Available: {titles}")


def task_row(t: dict[str, Any]) -> dict[str, Any]:
    links = []
    for link in t.get("links") or []:
        links.append(
            {
                "type": link.get("type"),
                "link": link.get("link"),
                "desc": link.get("description"),
            }
        )
    return {
        "id": t.get("id"),
        "title": (t.get("title") or "").strip(),
        "notes": (t.get("notes") or "").strip(),
        "due": t.get("due"),
        "status": t.get("status"),
        "updated": t.get("updated"),
        "parent": t.get("parent"),
        "position": t.get("position"),
        "links": links,
        "webViewLink": t.get("webViewLink"),
        "selfLink": t.get("selfLink"),
    }


def print_markdown(list_title: str, tasks: list[dict[str, Any]]) -> None:
    print(f"# {list_title}")
    print()
    if not tasks:
        print("(пусто)")
        return
    for t in tasks:
        title = t["title"] or "(без названия)"
        print(f"- [ ] {title}")
        if t.get("due"):
            print(f"  - due: {t['due']}")
        if t.get("notes"):
            for line in t["notes"].splitlines():
                print(f"  - {line}")
        for link in t.get("links") or []:
            if link.get("link"):
                print(f"  - {link['link']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch Google Tasks from a list")
    ap.add_argument(
        "--list",
        default=DEFAULT_LIST,
        help="List title substring (default: potyklo → matches 🤪 potyklo)",
    )
    ap.add_argument(
        "--include-completed",
        action="store_true",
        help="Include completed tasks",
    )
    ap.add_argument("--json", action="store_true", help="Print JSON instead of markdown")
    ap.add_argument(
        "--list-lists",
        action="store_true",
        help="Only print all task list titles and exit",
    )
    args = ap.parse_args()

    tok_file = load_token_file()
    token = access_token(tok_file)
    lists = list_all_pages(token, "/users/@me/lists", {"maxResults": "100"})

    if args.list_lists:
        for it in lists:
            print(f"{it.get('title')}\t{it.get('id')}")
        return 0

    tasklist = find_tasklist(lists, args.list)
    list_id = tasklist["id"]
    list_title = tasklist.get("title") or args.list

    params = {
        "maxResults": "100",
        "showCompleted": "true" if args.include_completed else "false",
        "showHidden": "false",
    }
    raw = list_all_pages(token, f"/lists/{urllib.parse.quote(list_id)}/tasks", params)
    if not args.include_completed:
        raw = [t for t in raw if t.get("status") != "completed"]
    raw.sort(key=lambda t: t.get("position") or "")

    tasks = [
        task_row(t)
        for t in raw
        if (t.get("title") or "").strip() or (t.get("notes") or "").strip()
    ]

    if args.json:
        print(
            json.dumps(
                {
                    "list": list_title,
                    "listId": list_id,
                    "count": len(tasks),
                    "tasks": tasks,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_markdown(list_title, tasks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
