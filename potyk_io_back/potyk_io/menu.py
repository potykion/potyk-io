from typing import TypedDict


class MenuItem(TypedDict):
    icon: str
    title: str
    url: str
    description: str


class MenuGroup(TypedDict):
    title: str
    links: list[MenuItem]


class MenuFeedItem(TypedDict):
    icon: str
    title: str
    url: str
    description: str
    group: str


MENU_GROUPS: list[MenuGroup] = [
    {
        "title": "Проекты",
        "links": [
            {
                "icon": "✍️",
                "title": "Написать мне",
                "url": "/inbox/send",
                "description": "",
            },
            {
                "icon": "💰",
                "title": "potyk-fin",
                "url": "/fin",
                "description": "Простой учет расходов и сберижений",
            },
            {
                "icon": "💰",
                "title": "potyk-invest",
                "url": "/invest",
                "description": "Новостюшки про рашн фондю",
            },
            {
                "icon": "🍕",
                "title": "potyk-food",
                "url": "/food",
                "description": "Ворую рецепты",
            },
            {
                "icon": "🎵",
                "title": "potyk-mu",
                "url": "/mu/",
                "description": "",
            },
            {"icon": "📜", "title": "Находки", "url": "/findings", "description": ""},
            {"icon": "📦", "title": "Содержание", "url": "/toc", "description": ""},
            {
                "icon": "📥",
                "title": "Инбокс",
                "url": "/inbox",
                "description": "",
            },
        ],
    },
    {
        "title": "ссылочки",
        "links": [
            {
                "icon": "🖼️",
                "title": "potyk.art",
                "url": "https://www.instagram.com/potyk.art",
                "description": "Рисую чертей по фану",
            },
            {
                "icon": "👩‍💻",
                "title": "github",
                "url": "https://github.com/potykion/potyk-io",
                "description": "",
            },
            {
                "icon": "🔗",
                "title": "Бесконечный потик",
                "url": "https://t.me/potyk_eternal",
                "description": "Обещаю, это последний мой тг канал",
            },
            {
                "icon": "📁",
                "title": "Папочка с моими старыми тг каналами",
                "url": "https://t.me/addlist/jMUGZkWRI-85ZjJi",
                "description": "Ох, ребята, перечитываю канальчик и да, пиздато всё-таки вышло, не надо забрасывать свой фристайл",
            },
        ],
    },
    {
        "title": "Еда",
        "links": [
            {
                "icon": "🧠",
                "title": "Размышления",
                "url": "/thoughts/food",
                "description": "",
            },
            {
                "icon": "📝",
                "title": "Отзывы на ресты",
                "url": "https://yandex.ru/maps/user/potyk-io",
                "description": "",
            },
            {
                "icon": "📊",
                "title": "Корзинка",
                "url": "https://docs.google.com/spreadsheets/d/1qreMshjaTWnI5GhAEc-CIJafXcK9iwUC16RaG7gYCsM/edit?usp=sharing",
                "description": "Всякие вкусные и не очень продукты",
            },
            {
                "icon": "📊",
                "title": "Рестики и кафешки",
                "url": "https://docs.google.com/spreadsheets/d/1h56SxxWjZCJmGULhlzVsRvT4KSU4rWoYBEWhQvrecGk/edit?usp=sharing",
                "description": "",
            },
        ],
    },
    {
        "title": "Кино",
        "links": [
            {
                "icon": "📊",
                "title": "Кино-подпорочки",
                "url": "/collections/movies",
                "description": "",
            },
        ],
    },
    {
        "title": "Тревел",
        "links": [
            {
                "icon": "✈️",
                "title": "Тревел",
                "url": "/travel",
                "description": "Гайд, планы и воспоминания",
            },
        ],
    },
    {
        "title": "Прога",
        "links": [
            {"icon": "👨‍💻", "title": "Резюме", "url": "/n/cv", "description": ""},
            {
                "icon": "📊",
                "title": "Софт/Сервисы",
                "url": "https://docs.google.com/spreadsheets/d/13xf7UHVDKiCf6rbHeHe2rsgwOlWaNRhUYDqAU5M3ULk/edit?usp=sharing",
                "description": "",
            },
            {"icon": "📝", "title": "Мой кодинг", "url": "/code", "description": ""},

        ],
    },
    {
        "title": "Алко",
        "links": [
            {
                "icon": "📊",
                "title": "Винный погребок",
                "url": "/collections/wine",
                "description": "",
            },
            {
                "icon": "📊",
                "title": "Пив холодильник",
                "url": "/collections/beer",
                "description": "",
            },
            {
                "icon": "📊",
                "title": "Пиво Россия",
                "url": "https://docs.google.com/spreadsheets/d/1JdhEktmNFFrolieF7O4pkmlic3urTROx8Fq8C2RNWY4/edit?usp=sharing",
                "description": "",
            },
        ],
    },
    {
        "title": "Отношач",
        "links": [
            {
                "icon": "🧠",
                "title": "Размышления",
                "url": "/thoughts/relationships",
                "description": "",
            },
            {
                "icon": "📝",
                "title": "State",
                "url": "/n/relationships",
                "description": "",
            },
            {
                "icon": "📝",
                "title": "Как найти девушку",
                "url": "/guides/find-gf",
                "description": "",
            },
        ],
    },
    {
        "title": "Селф",
        "links": [
            {"icon": "📝", "title": "Обо мне", "url": "/n", "description": ""},
            {"icon": "📔", "title": "Днев", "url": "/diary", "description": ""},
            {
                "icon": "📝",
                "title": "Кулстори",
                "url": "/cool-stories",
                "description": "",
            },
        ],
    },
]


FOOD_MENU_GROUPS: list[MenuGroup] = [
    {
        "title": "potyk-food",
        "links": [
            {
                "icon": "🧪",
                "title": "Эксперименты",
                "url": "/food/experiments",
                "description": "",
            },
            {
                "icon": "🍳",
                "title": "Рецепты",
                "url": "/food",
                "description": "",
            },
            {
                "icon": "🍽️",
                "title": "Рестораны",
                "url": "/food/rest",
                "description": "",
            },
            {
                "icon": "🍷",
                "title": "Дегустации",
                "url": "/food/tasting",
                "description": "",
            },
            {
                "icon": "←",
                "title": "potyk-io",
                "url": "/",
                "description": "",
            },
        ],
    }
]


def is_external_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def iter_menu_items() -> list[MenuFeedItem]:
    items: list[MenuFeedItem] = []
    for group in MENU_GROUPS:
        for item in group["links"]:
            items.append(
                {
                    "icon": item["icon"],
                    "title": item["title"],
                    "url": item["url"],
                    "description": item["description"],
                    "group": group["title"],
                }
            )
    return items
