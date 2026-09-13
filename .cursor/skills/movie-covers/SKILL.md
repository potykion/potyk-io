---
name: movie-covers
description: >-
  Скачивает обложки фильмов potyk-cinema с CDN Кинопоиска по kp id, кладёт
  файлы в static/potyk-io/img/movies/ и обновляет movies.cover (миграция или
  админка). Use when the user asks обложки фильмов, covers cinema, постеры
  без cover, стянуть обложки, или заполнить cover по ссылке на Кинопоиск.
---

# Обложки фильмов (potyk-cinema)

## Контекст

| Что | Где |
|---|---|
| Модель | `potyk_io_back/potyk_io/collections/movies.py` → `Movie.cover` |
| БД | `instance/main.db`, таблица `movies` |
| Статика | `static/potyk-io/img/movies/` |
| URL в БД | `/static/potyk-io/img/movies/<slug>.jpg` |
| id фильма | из URL: `https://www.kinopoisk.ru/film/<id>/` (также `/series/<id>/`) |
| Заглушка | `/static/potyk-io/img/movies/cover-placeholder.svg` |

`cover` — путь к локальному файлу, не внешняя ссылка.

## CDN Кинопоиска

Постер по id (без API-ключа):

```
https://st.kp.yandex.net/images/film_iphone/iphone360_{id}.jpg
```

Альтернатива крупнее: `.../images/film_big/{id}.jpg`.  
Проверено: оба отдают `200` + `image/jpeg`. User-Agent желателен.

## Имена файлов

- Предпочтительно английский kebab-case (`requiem-for-a-dream.jpg`), как у существующих webp/jpg.
- Если нет `title_en` — транслит `title_ru`.
- Конфликт имён — суффикс `-2`, `-3`, …
- Расширение: `.jpg` (как отдаёт CDN). Старые файлы могут быть `.webp` / `.png` — не трогать.

## Workflow: заполнить все без обложки

```
- [ ] 1. SELECT movies WHERE cover IS NULL OR cover = ''
- [ ] 2. Скачать постеры в static/potyk-io/img/movies/
- [ ] 3. Alembic-миграция: UPDATE movies SET cover = ... WHERE id = ... AND (cover IS NULL OR cover = '')
- [ ] 4. down_revision = текущий alembic head; python -m alembic upgrade head (из .venv)
- [ ] 5. Проверить: missing = 0; файлы на диске есть
```

### Скрипт скачивания (эталон)

```python
import re, sqlite3, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent  # корень репо
OUT = ROOT / "static/potyk-io/img/movies"
DB = ROOT / "instance/main.db"

TRANSLIT = str.maketrans({
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z",
    "и":"i","й":"y","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r",
    "с":"s","т":"t","у":"u","ф":"f","х":"kh","ц":"ts","ч":"ch","ш":"sh",
    "щ":"shch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya",
})

def slugify(text: str) -> str:
    s = "".join(
        ch.translate(TRANSLIT) if "а" <= ch.lower() <= "я" or ch.lower() == "ё"
        else (ch if ch.isascii() and (ch.isalnum() or ch in "-_") else "-")
        for ch in text.lower().strip()
    )
    return re.sub(r"-+", "-", s).strip("-") or "movie"

def cover_url(kp_id: str) -> str:
    return f"https://st.kp.yandex.net/images/film_iphone/iphone360_{kp_id}.jpg"

# 1) выбрать id, title_ru, title_en без cover
# 2) slug = slugify(title_en or title_ru); уникализировать
# 3) urllib.request.urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30)
# 4) отбросить ответ < ~1000 байт; иначе OUT / f"{slug}.jpg"
# 5) cover path = f"/static/potyk-io/img/movies/{slug}.jpg"
```

### Миграция

Образец: `migrations/versions/a0b1c2d3e4f5_movie_covers_fill.py`.

```python
COVERS = {"367": "/static/potyk-io/img/movies/requiem-for-a-dream.jpg", ...}

def upgrade() -> None:
    bind = op.get_bind()
    for movie_id, cover in COVERS.items():
        bind.execute(
            sa.text(
                "UPDATE movies SET cover = :cover "
                "WHERE id = :id AND (cover IS NULL OR cover = '')"
            ),
            {"id": movie_id, "cover": cover},
        )
```

Файлы jpg коммитятся вместе с миграцией.

## Один фильм / правка в коде

1. Извлечь id из `kinopoisk` URL (`/film/(\d+)/` или `/series/(\d+)/`).
2. Скачать в `static/.../img/movies/<slug>.jpg`.
3. Проставить `Movie.cover = "/static/potyk-io/img/movies/<slug>.jpg"`.

В админке обложка подтягивается автоматически — см. раздел «Админка: автообложка» выше.

## Админка: автообложка

В форме «Добавить фильм» (`/cinema/admin`):

1. Превью в браузере — сразу по CDN URL из id в ссылке КП (см. `cover_cdn_url`).
2. При POST без `cover` — `download_cover()` в `potyk_io_back/cinema/covers.py` пишет файл в static и путь в `Movie.cover` (если cover ещё пустой).
3. Коллекция обязательна; дефолт `watch_later`.

Название/год с страницы КП HTML **не** парсить: отдаёт заглушку без og:title. Нужен неофициальный API с ключом или ручной ввод.

## Не делать

- Не писать в `cover` внешний URL CDN (ломается / hotlink).
- Не перезаписывать уже заполненный `cover` без явной просьбы.
- Не удалять существующие webp/png обложки.
