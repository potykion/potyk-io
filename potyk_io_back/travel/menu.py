from typing import TypedDict

from potyk_io_back.potyk_io.menu import normalize_menu_path


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
    return normalize_menu_path(url) == normalize_menu_path(path)
