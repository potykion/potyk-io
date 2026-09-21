from typing import NotRequired, TypedDict


class MenuItem(TypedDict):
    icon: str
    title: str
    url: str
    description: str
    badge: NotRequired[int]
    lock: NotRequired[bool]


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
                "icon": "💰",
                "title": "Бабло",
                "url": "/money/",
                "description": "Учёт и инвестиции",
            },
            {
                "icon": "🍕",
                "title": "Жрачка",
                "url": "/food",
                "description": "Ворую рецепты",
            },
            {
                "icon": "✈️",
                "title": "Тревел",
                "url": "/travel/",
                "description": "Гайд, планы и воспоминания",
            },
            {
                "icon": "💻",
                "title": "Тех",
                "url": "/tech/",
                "description": "Девайсы, резюме, кодинг",
            },
            {
                "icon": "🎭",
                "title": "Культур",
                "url": "/culture/",
                "description": "",
            },
            {"icon": "📜", "title": "Находки", "url": "/findings", "description": ""},
            {"icon": "📦", "title": "Содержание", "url": "/toc", "description": ""},
            {
                "icon": "🪞",
                "title": "Личное",
                "url": "/self/",
                "description": "Дневник и отношения",
                "lock": True,
            },
            {
                "icon": "🐙",
                "title": "Ишьюс",
                "url": "https://github.com/potykion/potyk-io/issues",
                "description": "",
            },
            {
                "icon": "🛠️",
                "title": "Админка",
                "url": "/admin",
                "description": "",
                "lock": True,
            },
        ],
    },
]


SELF_MENU_GROUPS: list[MenuGroup] = [
    {
        "title": "potyk-self",
        "links": [
            {
                "icon": "📓",
                "title": "Дневник",
                "url": "/self/diary",
                "description": "",
            },
            {
                "icon": "📖",
                "title": "Кулстори",
                "url": "/self/cool-stories",
                "description": "",
            },
            {
                "icon": "💭",
                "title": "Размышления",
                "url": "/self/thoughts/relationships",
                "description": "",
            },
            {
                "icon": "💞",
                "title": "State",
                "url": "/self/n/relationships",
                "description": "",
            },
            {
                "icon": "🧭",
                "title": "Как найти девушку",
                "url": "/self/guides/find-gf",
                "description": "",
            },
        ],
    },
    {
        "title": "",
        "links": [
            {
                "icon": "←",
                "title": "potyk-io",
                "url": "/",
                "description": "",
            },
        ],
    },
]


TECH_MENU_GROUPS: list[MenuGroup] = [
    {
        "title": "potyk-tech",
        "links": [
            {
                "icon": "📱",
                "title": "Мои девайсы",
                "url": "/tech/devices",
                "description": "",
            },
            {
                "icon": "🍎",
                "title": "Айос после андроида",
                "url": "/tech/ios-after-android",
                "description": "",
            },
            {
                "icon": "👨‍💻",
                "title": "Резюме",
                "url": "/tech/cv",
                "description": "",
            },
            {
                "icon": "📊",
                "title": "Софт/Сервисы",
                "url": "https://docs.google.com/spreadsheets/d/13xf7UHVDKiCf6rbHeHe2rsgwOlWaNRhUYDqAU5M3ULk/edit?usp=sharing",
                "description": "",
            },
            {
                "icon": "📝",
                "title": "Мой кодинг",
                "url": "/tech/my-code",
                "description": "",
            },
            {
                "icon": "🤖",
                "title": "Стейт оф ИИ",
                "url": "/tech/ai",
                "description": "",
            },
            {
                "icon": "🧠",
                "title": "ИИ-кодинг",
                "url": "/tech/ai-coding",
                "description": "",
            },
        ],
    },
    {
        "title": "",
        "links": [
            {
                "icon": "←",
                "title": "potyk-io",
                "url": "/",
                "description": "",
            },
        ],
    },
]


_FIN_SECTION_LINKS: list[MenuItem] = [
    {
        "icon": "📒",
        "title": "Учёт",
        "url": "/fin/",
        "description": "Простой учет расходов и сбережений",
    },
]


_INVEST_SECTION_LINKS: list[MenuItem] = [
    {
        "icon": "📰",
        "title": "Новости",
        "url": "/invest/",
        "description": "",
    },
    {
        "icon": "🤝",
        "title": "Сделки",
        "url": "/invest/deals",
        "description": "",
    },
    {
        "icon": "📊",
        "title": "Фонды",
        "url": "/invest/funds",
        "description": "",
    },
    {
        "icon": "🔗",
        "title": "Зависимости",
        "url": "/invest/dependencies",
        "description": "",
    },
    {
        "icon": "💸",
        "title": "Пассивный доход",
        "url": "/invest/passive-income",
        "description": "",
    },
    {
        "icon": "📈",
        "title": "Трейдинг",
        "url": "/invest/trading",
        "description": "",
    },
]


MONEY_MENU_GROUPS: list[MenuGroup] = [
    {
        "title": "Учет",
        "links": _FIN_SECTION_LINKS,
    },
    {
        "title": "Инвест",
        "links": _INVEST_SECTION_LINKS,
    },
    {
        "title": "",
        "links": [
            {
                "icon": "←",
                "title": "potyk-io",
                "url": "/",
                "description": "",
            },
        ],
    },
]


_CULTURE_OWN_LINKS: list[MenuItem] = [
    {
        "icon": "🎭",
        "title": "Театр",
        "url": "/culture/teatr",
        "description": "",
    },
    {
        "icon": "🌐",
        "title": "Интернет",
        "url": "/culture/internet",
        "description": "",
    },
    {
        "icon": "📺",
        "title": "ТВ / Нулевые",
        "url": "/culture/tv-nulevye",
        "description": "",
    },
]


_MU_SECTION_LINKS: list[MenuItem] = [
    {
        "icon": "🎵",
        "title": "Статьи",
        "url": "/mu/",
        "description": "",
    },
    {
        "icon": "🎤",
        "title": "Исполнители",
        "url": "/mu/artists/",
        "description": "",
    },
    {
        "icon": "📜",
        "title": "Лор",
        "url": "/mu/lore",
        "description": "",
    },
    {
        "icon": "📊",
        "title": "Альбомы: стата",
        "url": "https://docs.google.com/spreadsheets/d/1Dy9fxDgLzxy84PsIAoyappVB9xfTYHls1rn9KNe4gDs/edit?usp=sharing",
        "description": "",
    },
    {
        "icon": "📺",
        "title": "танцевальное по лайту",
        "url": "https://www.youtube.com/playlist?list=PLdb8DVmvU9i5bGINNz10f-ga_bqD41O4q",
        "description": "",
    },
    {
        "icon": "🤝",
        "title": "Го дружить в RYM",
        "url": "https://rateyourmusic.com/~potykion",
        "description": "",
    },
]


_CINEMA_SECTION_LINKS: list[MenuItem] = [
    {
        "icon": "🎬",
        "title": "Подборки",
        "url": "/cinema/",
        "description": "",
    },
    {
        "icon": "📺",
        "title": "Где смотреть кино",
        "url": "/cinema/where-to-watch",
        "description": "",
    },
    {
        "icon": "🇻🇳",
        "title": "Вьетнамское кино",
        "url": "/cinema/vietnamese-cinema",
        "description": "",
    },
]


_ART_SECTION_LINKS: list[MenuItem] = [
    {
        "icon": "🖼️",
        "title": "Главная",
        "url": "/art/",
        "description": "Рисую чертей по фану",
    },
    {
        "icon": "🖼️",
        "title": "Инста",
        "url": "https://www.instagram.com/potyk.art",
        "description": "Рисую чертей по фану",
    },
]


_READS_SECTION_LINKS: list[MenuItem] = [
    {
        "icon": "📚",
        "title": "Главная",
        "url": "/reads/",
        "description": "",
    },
]


_PRIKOLS_SECTION_LINKS: list[MenuItem] = [
    {
        "icon": "🤡",
        "title": "Главная",
        "url": "/prikols/",
        "description": "Музей приколов",
    },
]


CULTURE_MENU_GROUPS: list[MenuGroup] = [
    {
        "title": "potyk-culture",
        "links": _CULTURE_OWN_LINKS,
    },
    {
        "title": "Музыка",
        "links": _MU_SECTION_LINKS,
    },
    {
        "title": "Кино",
        "links": _CINEMA_SECTION_LINKS,
    },
    {
        "title": "Чтение",
        "links": _READS_SECTION_LINKS,
    },
    {
        "title": "Арт",
        "links": _ART_SECTION_LINKS,
    },
    {
        "title": "Приколы",
        "links": _PRIKOLS_SECTION_LINKS,
    },
    {
        "title": "",
        "links": [
            {
                "icon": "←",
                "title": "potyk-io",
                "url": "/",
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
                "icon": "🍳",
                "title": "Рецепты",
                "url": "/food",
                "description": "",
            },
            {
                "icon": "🧪",
                "title": "Эксперименты",
                "url": "/food/experiments",
                "description": "",
            },
        ],
    },
    {
        "title": "Рестораны",
        "links": [
            {
                "icon": "🍽️",
                "title": "Рестораны",
                "url": "/food/rest",
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
                "title": "База",
                "url": "https://docs.google.com/spreadsheets/d/1h56SxxWjZCJmGULhlzVsRvT4KSU4rWoYBEWhQvrecGk/edit?usp=sharing",
                "description": "",
            },
            {
                "icon": "☕",
                "title": "Эстетика кофеен",
                "url": "/food/thoughts/coffee",
                "description": "",
            },
        ],
    },
    {
        "title": "Пробуем",
        "links": [
            {
                "icon": "🥪",
                "title": "Размышления о сэндвичах",
                "url": "/food/thoughts/sandwich",
                "description": "",
            },
            {
                "icon": "🍽️",
                "title": "Еда и я",
                "url": "/food/thoughts/food",
                "description": "",
            },
            {
                "icon": "🍵",
                "title": "Размышления о чае",
                "url": "/food/thoughts/tea",
                "description": "",
            },
            {
                "icon": "🧉",
                "title": "Чайный пьяница",
                "url": "/food/ethereal-feed/tea",
                "description": "",
            },
            {
                "icon": "🧋",
                "title": "Бабл-ти",
                "url": "/food/thoughts/bubble-tea",
                "description": "",
            },
            {
                "icon": "🍬",
                "title": "Сладости",
                "url": "/food/tasting/sweets",
                "description": "",
            },
            {
                "icon": "📊",
                "title": "Корзинка",
                "url": "https://docs.google.com/spreadsheets/d/1qreMshjaTWnI5GhAEc-CIJafXcK9iwUC16RaG7gYCsM/edit?usp=sharing",
                "description": "Всякие вкусные и не очень продукты",
            },
        ],
    },
    {
        "title": "Алко",
        "links": [
            {
                "icon": "🍷",
                "title": "Винный погребок",
                "url": "/food/tasting/wine",
                "description": "",
            },
            {
                "icon": "🍺",
                "title": "Пив холодильник",
                "url": "/food/tasting/beer",
                "description": "",
            },
            {
                "icon": "🍺",
                "title": "Пиво Россия",
                "url": "https://docs.google.com/spreadsheets/d/1JdhEktmNFFrolieF7O4pkmlic3urTROx8Fq8C2RNWY4/edit?usp=sharing",
                "description": "",
            },
        ],
    },
    {
        "title": "",
        "links": [
            {
                "icon": "←",
                "title": "potyk-io",
                "url": "/",
                "description": "",
            },
        ],
    },
]


def admin_menu_groups(*, local: bool, inbox_badge: int | None = None) -> list[MenuGroup]:
    links: list[MenuItem] = [
        {
            "icon": "📥",
            "title": "Инбокс",
            "url": "/inbox",
            "description": "",
        },
        {
            "icon": "✍️",
            "title": "Создание поста",
            "url": "/admin/posts/new",
            "description": "",
        },
        {
            "icon": "📝",
            "title": "Разбор заметок",
            "url": "/admin/notes-review",
            "description": "",
        },
        {
            "icon": "🎬",
            "title": "Кино",
            "url": "/admin/cinema",
            "description": "",
        },
        {
            "icon": "🍽",
            "title": "Рестораны",
            "url": "/admin/restaurants",
            "description": "",
        },
    ]
    if inbox_badge:
        links[0]["badge"] = inbox_badge
    if local:
        links.append(
            {
                "icon": "⬆",
                "title": "Коммит и пуш",
                "url": "/admin/commit",
                "description": "",
            }
        )
    return [
        {
            "title": "Админка",
            "links": links,
        },
        {
            "title": "Ссылки",
            "links": [
                {
                    "icon": "📊",
                    "title": "Яндекс Метрика",
                    "url": "https://metrika.yandex.ru/overview?id=82960681",
                    "description": "",
                },
                {
                    "icon": "👩‍💻",
                    "title": "GitHub",
                    "url": "https://github.com/potykion/potyk-io",
                    "description": "",
                },
            ],
        },
        {
            "title": "",
            "links": [
                {
                    "icon": "←",
                    "title": "potyk-io",
                    "url": "/",
                    "description": "",
                },
            ],
        },
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
