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
        "icon": "📜",
        "title": "Лор",
        "url": "/mu/lore",
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
        "title": "potyk-culture",
        "url": "/culture/",
    },
]


def is_mu_link_active(url: str, path: str) -> bool:
    if url.startswith(("http://", "https://")):
        return False
    normalized_url = url.rstrip("/") or "/"
    normalized_path = path.rstrip("/") or "/"
    if normalized_url == "/mu":
        return normalized_path == "/mu"
    return normalized_path == normalized_url or normalized_path.startswith(f"{normalized_url}/")
