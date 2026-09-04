from typing import TypedDict


class InvestMenuItem(TypedDict):
    icon: str
    title: str
    url: str
    login_required: bool


INVEST_MENU_ITEMS: list[InvestMenuItem] = [
    {
        "icon": "📰",
        "title": "Новости",
        "url": "/invest/",
        "login_required": False,
    },
    {
        "icon": "🤝",
        "title": "Сделки",
        "url": "/invest/deals",
        "login_required": True,
    },
    {
        "icon": "📊",
        "title": "Фонды",
        "url": "/invest/funds",
        "login_required": False,
    },
    {
        "icon": "←",
        "title": "potyk-io",
        "url": "/",
        "login_required": False,
    },
]


def is_invest_link_active(url: str, path: str) -> bool:
    normalized = url.rstrip("/") or "/"
    if normalized == "/invest":
        return (
            path.rstrip("/") == "/invest"
            or path.startswith("/invest/Новости")
            or path.startswith("/invest/tickers/")
        )
    if normalized == "/invest/deals":
        return path == "/invest/deals" or path.startswith("/invest/deals/")
    if normalized == "/invest/funds":
        return path == "/invest/funds"
    return path == url
