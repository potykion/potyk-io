---
name: new-potyk-section
description: >-
  Создаёт новый раздел potyk-* по аналогии с potyk-art / potyk-mu / potyk-travel:
  папка templates, blueprint, пункт в глобальном меню, меню раздела.
  Use when the user asks for новый раздел, создать potyk-*, section like art/mu,
  или указывает на этот skill.
---

# Новый раздел potyk-*

## Когда использовать

Нужен новый публичный раздел сайта (`potyk-<slug>`), как у существующих: art, mu, travel, food.

## Выбор типа

| Тип | Когда | Ориентир |
|-----|--------|----------|
| **A — лёгкий** | Лендинг / галерея / заглушка; без markdown-vault | `potyk-art` |
| **B — markdown vault** | Много `.md` страниц, catch-all URL | `potyk-travel` (проще, чем mu) |
| **C — внутри potyk-io** | Без отдельного пакета, префикс вроде `/food` | `potyk-food` |

По умолчанию для «просто раздел» — **тип A**. Для vault с заметками — **B**.

## Тип A (как potyk-art) — чеклист

Slug = короткое латинское имя (`cinema`, `reads`). URL = `/<slug>/`. Title бренда = `potyk-<slug>`.

1. **`templates/potyk-<slug>/index.html`**
   - `extends "potyk-io/_base.html"`
   - `{% block title %}potyk-<slug>{% endblock %}`
   - В `{% block main %}` минимум `<h1>potyk-<slug></h1>` (+ контент при необходимости)
2. **`potyk_io_back/<slug>/pres.py`**
   - `Blueprint("<slug>", __name__, url_prefix="/<slug>")`
   - `context_processor`: `menu_groups`, `section_brand_title="potyk-<slug>"`, `section_brand_url="/<slug>"`
   - `GET /` → `render_template("potyk-<slug>/index.html", ...)`
3. **`potyk_io_back/<slug>/__init__.py`** — реэкспорт `*_bp`
4. **`potyk_io_back/potyk_io/menu.py`**
   - `*_MENU_GROUPS` для сайдбара раздела (как `ART_MENU_GROUPS`): пункты раздела + «← potyk-io» → `/`
   - пункт в `MENU_GROUPS` → группа «Проекты» (`title: potyk-<slug>`, `url: /<slug>/`)
5. **`main.py`** — import + `app.register_blueprint(*_bp)` **до** `potyk_io_bp` (у него catch-all)
6. Опционально: `docs/potyk-<slug>.md` (поведение) — аппрув не нужен

Минимальный `pres.py`:

```python
from flask import Blueprint, render_template

from potyk_io_back.potyk_io.menu import SLUG_MENU_GROUPS  # заменить SLUG

slug_bp = Blueprint("slug", __name__, url_prefix="/slug")


@slug_bp.context_processor
def slug_nav_context():
    return {
        "menu_groups": SLUG_MENU_GROUPS,
        "section_brand_title": "potyk-slug",
        "section_brand_url": "/slug",
    }


@slug_bp.get("/")
def index():
    return render_template("potyk-slug/index.html")
```

## Тип B (как potyk-travel) — чеклист

1. **`templates/potyk-<slug>/`**: `_base.html`, `_sidebar.html`, `index.html`, `page.html` + контент `.md`
2. **`potyk_io_back/<slug>/`**: `__init__.py`, `menu.py` (`*_MENU_ITEMS` + `is_*_link_active`), `pres.py`
3. В `pres.py`: `*_TEMPLATES_DIR`, blueprint, context_processor, index, catch-all `/<path:page_path>` через `resolve_page` / `render_body_html` / `send_file` (скопировать с travel)
4. `main.py` + пункт в `MENU_GROUPS`
5. Опционально спека в `docs/` (без аппрува)

## Тип C (как potyk-food)

Отдельный blueprint не нужен: маршруты и переключение меню по `request.path.startswith("/...")` в `potyk_io/pres.py` + `*_MENU_GROUPS`. Использовать только если раздел логично «внутри» potyk-io.

## Не делать

- Не регистрировать blueprint **после** `potyk_io_bp` — чужие URL перехватит catch-all
- Не класть skill в `~/.cursor/skills-cursor/`
- Не оставлять устаревшие ссылки в `MENU_GROUPS` после переноса страниц в новый раздел
- Не писать в спеку детали реализации (эндпоинты, имена модулей) — skill «оформление спеки»

## После создания

Кратко сообщить пути и URL.
