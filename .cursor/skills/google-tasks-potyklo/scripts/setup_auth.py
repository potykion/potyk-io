#!/usr/bin/env python3
"""One-time OAuth for Google Tasks (Desktop client).

Requires ``.cursor/secrets/google_tasks_client.json`` — OAuth 2.0 Client ID
of type **Desktop app** from Google Cloud Console (Tasks API enabled,
consent screen in Testing, test user = your Gmail).

Writes refreshable token to ``.cursor/secrets/google_tasks_token.json``.

gcloud's own OAuth client is blocked by Google for Tasks scopes — do not use
``gcloud auth application-default login --scopes=…tasks…``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SECRETS = ROOT / ".cursor" / "secrets"
CLIENT = SECRETS / "google_tasks_client.json"
TOKEN = SECRETS / "google_tasks_token.json"
SCOPES = ["https://www.googleapis.com/auth/tasks.readonly"]


def main() -> int:
    SECRETS.mkdir(parents=True, exist_ok=True)
    if not CLIENT.is_file():
        print(
            f"Missing {CLIENT}\n\n"
            "1. https://console.cloud.google.com/apis/library/tasks.googleapis.com — Enable\n"
            "2. APIs & Services → OAuth consent screen → External → Testing\n"
            "   Add test user: potykion@gmail.com\n"
            "3. Credentials → Create OAuth client ID → Desktop app\n"
            "4. Download JSON → save as .cursor/secrets/google_tasks_client.json\n"
        )
        return 1

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print(
            "Install: .venv\\Scripts\\pip.exe install google-auth-oauthlib google-auth-httplib2"
        )
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT), SCOPES)
    # port=0 → random free port; opens system browser
    creds = flow.run_local_server(port=0, prompt="consent")
    data = {
        "type": "authorized_user",
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri or "https://oauth2.googleapis.com/token",
        "scopes": list(creds.scopes or SCOPES),
    }
    TOKEN.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved {TOKEN}")
    print("Test: python .cursor/skills/google-tasks-potyklo/scripts/fetch_potyklo_tasks.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
