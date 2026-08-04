MENU_QUICK = [
    {"icon": "🖼️", "title": "potyk.art", "url": "https://www.instagram.com/potyk.art"},
    {"icon": "📜", "title": "/feed", "url": "/feed"},
    {"icon": "📦", "title": "/toc", "url": "/toc"},
    {"icon": "👩‍💻", "title": "github", "url": "https://github.com/potykion/potyk-io"},
]

MENU_GROUPS = [
    {
        "title": "Еда",
        "links": [
            {"icon": "📃", "title": "Рецептики", "url": "https://potyk.io/potyk-food/"},
            {"icon": "🧠", "title": "Размышления", "url": "/thoughts/food"},
            {"icon": "📝", "title": "Отзывы на ресты", "url": "https://yandex.ru/maps/user/potyk-io"},
            {
                "icon": "📊",
                "title": "Корзинка",
                "url": "https://docs.google.com/spreadsheets/d/1qreMshjaTWnI5GhAEc-CIJafXcK9iwUC16RaG7gYCsM/edit?usp=sharing",
            },
            {
                "icon": "📊",
                "title": "Рестики и кафешки",
                "url": "https://docs.google.com/spreadsheets/d/1h56SxxWjZCJmGULhlzVsRvT4KSU4rWoYBEWhQvrecGk/edit?usp=sharing",
            },
            {"icon": "🔗", "title": "potyk-eats", "url": "https://t.me/potyk_eats"},
        ],
    },
    {
        "title": "Музыка/Кино",
        "links": [
            {"icon": "📝", "title": "Музыка в 2к26", "url": "/mu/2026"},
            {
                "icon": "📊",
                "title": "Альбомы: стата",
                "url": "https://docs.google.com/spreadsheets/d/1Dy9fxDgLzxy84PsIAoyappVB9xfTYHls1rn9KNe4gDs/edit?usp=sharing",
            },
            {"icon": "📊", "title": "Кино-подпорочки", "url": "/collections/movies"},
            {"icon": "📝", "title": "Скачать музыку", "url": "/guides/music"},
            {
                "icon": "📺",
                "title": "танцевальное",
                "url": "https://www.youtube.com/playlist?list=PLdb8DVmvU9i5bGINNz10f-ga_bqD41O4q",
            },
            {"icon": "🤝", "title": "Го дружить в RYM", "url": "https://rateyourmusic.com/~potykion"},
        ],
    },
    {
        "title": "Тревел",
        "links": [
            {"icon": "📝", "title": "Хау ту тревел", "url": "/travel/how-to"},
            {"icon": "📝", "title": "Планы", "url": "/travel/plans"},
            {"icon": "📝", "title": "Впечатлы", "url": "/travel/memories"},
        ],
    },
    {
        "title": "Прога",
        "links": [
            {"icon": "👨‍💻", "title": "Резюме", "url": "/n/cv"},
            {
                "icon": "📊",
                "title": "Софт/Сервисы",
                "url": "https://docs.google.com/spreadsheets/d/13xf7UHVDKiCf6rbHeHe2rsgwOlWaNRhUYDqAU5M3ULk/edit?usp=sharing",
            },
            {"icon": "📝", "title": "Мой кодинг", "url": "/code"},
            {"icon": "🔗", "title": "Разговоры с ии", "url": "https://t.me/potyk_ai"},
        ],
    },
    {
        "title": "Алко",
        "links": [
            {"icon": "📊", "title": "Винный погребок", "url": "/collections/wine"},
            {"icon": "📊", "title": "Пив холодильник", "url": "/collections/beer"},
            {
                "icon": "📊",
                "title": "Пиво Россия",
                "url": "https://docs.google.com/spreadsheets/d/1JdhEktmNFFrolieF7O4pkmlic3urTROx8Fq8C2RNWY4/edit?usp=sharing",
            },
        ],
    },
    {
        "title": "Бабло",
        "links": [
            {
                "icon": "📊",
                "title": "Инвестиции",
                "url": "https://docs.google.com/spreadsheets/d/1yXDk5eYpNwTvzPYGVoBTnETeaTwqY3b7uyPzNPwPpng/edit?usp=sharing",
            },
            {"icon": "📊", "title": "Траты", "url": "/fin"},
            {"icon": "📝", "title": "Пассивный доход", "url": "/guides/passive-income"},
        ],
    },
    {
        "title": "Писс ссанина",
        "links": [
            {"icon": "📝", "title": "Кулстори", "url": "/cool-stories"},
            {"icon": "🔗", "title": "потик пишет...", "url": "https://t.me/potyk_writes"},
        ],
    },
    {
        "title": "Отношач",
        "links": [
            {"icon": "🧠", "title": "Размышления", "url": "/thoughts/relationships"},
            {"icon": "📝", "title": "State", "url": "/n/relationships"},
            {"icon": "📝", "title": "Как найти девушку", "url": "/guides/find-gf"},
        ],
    },
    {
        "title": "Селф",
        "links": [
            {"icon": "📝", "title": "Обо мне", "url": "/n"},
            {"icon": "📔", "title": "Днев", "url": "/diary"},
        ],
    },
]


def is_external_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def iter_menu_items() -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for group in MENU_GROUPS:
        for item in group["links"]:
            items.append(
                {
                    "icon": item["icon"],
                    "title": item["title"],
                    "url": item["url"],
                    "group": group["title"],
                }
            )
    return items
