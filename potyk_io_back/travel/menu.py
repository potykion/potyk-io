from typing import TypedDict


class TravelMenuItem(TypedDict):
    icon: str
    title: str
    url: str


TRAVEL_MENU_ITEMS: list[TravelMenuItem] = [
    {
        "icon": "✈️",
        "title": "potyk-travel",
        "url": "/travel/",
    },
    {
        "icon": "📝",
        "title": "Гайд",
        "url": "/travel/how-to",
    },
    {
        "icon": "📔",
        "title": "Воспоминания",
        "url": "/travel/memories",
    },
    {
        "icon": "🗺️",
        "title": "Планы",
        "url": "/travel/plans",
    },
    {
        "icon": "←",
        "title": "potyk-io",
        "url": "/",
    },
]


def is_travel_link_active(url: str, path: str) -> bool:
    normalized = url.rstrip("/") or "/"
    if normalized == "/travel":
        return path.rstrip("/") == "/travel"
    return path == url or path.startswith(f"{url.rstrip('/')}/")
