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
        "icon": "🎤",
        "title": "Исполнители",
        "url": "/mu/artists/",
    },
    {
        "icon": "📊",
        "title": "Альбомы: стата",
        "url": "https://docs.google.com/spreadsheets/d/1Dy9fxDgLzxy84PsIAoyappVB9xfTYHls1rn9KNe4gDs/edit?usp=sharing",
    },
    {
        "icon": "📺",
        "title": "танцевальное по лайту",
        "url": "https://www.youtube.com/playlist?list=PLdb8DVmvU9i5bGINNz10f-ga_bqD41O4q",
    },
    {
        "icon": "🤝",
        "title": "Го дружить в RYM",
        "url": "https://rateyourmusic.com/~potykion",
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
