from typing import NotRequired, TypedDict


class MenuItem(TypedDict):
    icon: str
    title: str
    url: str
    description: str
    badge: NotRequired[int]


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
                "icon": "✈️",
                "title": "potyk-travel",
                "url": "/travel/",
                "description": "Гайд, планы и воспоминания",
            },
            {
                "icon": "💻",
                "title": "potyk-tech",
                "url": "/tech/",
                "description": "Девайсы, резюме, кодинг",
            },
            {
                "icon": "🎭",
                "title": "potyk-culture",
                "url": "/culture/",
                "description": "",
            },
            {"icon": "📜", "title": "Находки", "url": "/findings", "description": ""},
            {"icon": "📦", "title": "Содержание", "url": "/toc", "description": ""},
        ],
    },
    {
        "title": "ссылочки",
        "links": [
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
            {
                "icon": "❤️",
                "title": "Благотворительность",
                "url": "/charity",
                "description": "",
            },
            {
                "icon": "🎯",
                "title": "Цели 2026",
                "url": "/n/2026-goals",
                "description": "",
            },
            {
                "icon": "🪦",
                "title": "Некролог",
                "url": "/necrolog",
                "description": "",
            },
        ],
    },
    {
        "title": "Всякое",
        "links": [
            {
                "icon": "🛠️",
                "title": "Админка",
                "url": "/admin",
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


_CULTURE_BACK_LINK: MenuItem = {
    "icon": "←",
    "title": "potyk-culture",
    "url": "/culture/",
    "description": "",
}


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


ART_MENU_GROUPS: list[MenuGroup] = [
    {
        "title": "potyk-art",
        "links": _ART_SECTION_LINKS,
    },
    {
        "title": "",
        "links": [_CULTURE_BACK_LINK],
    },
]


PRIKOLS_MENU_GROUPS: list[MenuGroup] = [
    {
        "title": "potyk-prikols",
        "links": _PRIKOLS_SECTION_LINKS,
    },
    {
        "title": "",
        "links": [_CULTURE_BACK_LINK],
    },
]


CINEMA_MENU_GROUPS: list[MenuGroup] = [
    {
        "title": "potyk-cinema",
        "links": _CINEMA_SECTION_LINKS,
    },
    {
        "title": "",
        "links": [_CULTURE_BACK_LINK],
    },
]


READS_MENU_GROUPS: list[MenuGroup] = [
    {
        "title": "potyk-reads",
        "links": _READS_SECTION_LINKS,
    },
    {
        "title": "",
        "links": [_CULTURE_BACK_LINK],
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
                "icon": "🍵",
                "title": "Размышления о чае",
                "url": "/food/thoughts/tea",
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
