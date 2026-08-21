from typing import TypedDict


class MuMenuItem(TypedDict):
    icon: str
    title: str
    url: str


MU_MENU_ITEMS: list[MuMenuItem] = [
    {
        "icon": "🎵",
        "title": "potyk-mu",
        "url": "/mu/",
    },
    {
        "icon": "←",
        "title": "potyk-io",
        "url": "/",
    },
]


def is_mu_link_active(url: str, path: str) -> bool:
    normalized = url.rstrip("/") or "/"
    if normalized == "/mu":
        return path.rstrip("/") == "/mu" or path.startswith("/mu/")
    return path == url
