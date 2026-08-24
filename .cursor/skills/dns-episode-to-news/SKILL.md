---
name: dns-episode-to-news
description: >-
  Разбирает конспект выпуска «Деньги не спят» (ДнС) на новости в SQL
  (invest_news) через alembic-миграцию; тикеры берёт из instance/main.db
  (invest_tickers), недостающие добавляет в ту же миграцию. Use when the user
  mentions ДнС, Деньги не спят, новый выпуск, конспект DNS, или просит
  разнести выпуск по новостям/тикерам.
---

# ДнС → новости в SQL

## Когда применять

Пользователь даёт путь к конспекту в `templates/potyk-invest/Источники/Деньги не спят/` и просит разнести выпуск по новостям.

## Вход

1. Файл источника, напр. `Источники/Деньги не спят/YYYY-MM-DD ДнС <название>.md`
2. Локальная БД: `instance/main.db` — таблица `invest_tickers`
3. Схема новостей: `potyk_io_back/invest/entities.py` → `InvestNews`
4. Образцы миграций: `migrations/versions/e1f2a3b4c5d6_dns_2026_08_21.py`, `d0e1f2a3b4c5_seed_findings_from_md.py`

## Workflow

Скопируй чеклист и отмечай:

```
- [ ] 1. Разобрать конспект на блоки (тикер / макро)
- [ ] 2. Сопоставить с тикерами в invest_tickers (instance/main.db)
- [ ] 3. Запланировать недостающие тикеры (+ русское name)
- [ ] 4. Дописать name существующим без него (UPDATE в миграции)
- [ ] 5. Создать alembic-миграцию с NEWS_ROWS (+ NEW_TICKERS при необходимости)
- [ ] 6. Проверить slug/source/summary и уникальность slug
```

### 1. Разбор конспекта

Каждый блок обычно: имя → `тек`/цена → тезисы → `сентимент` 🟢/🟡/🔴.

Макро-блоки (не акции):

| В конспекте | ticker (SQL) | slug-суффикс |
|---|---|---|
| imoex | `IMOEX` | `ДнС IMOEX` |
| ртс | `RTSI` | `ДнС RTS` |
| глобал | `Глобал` | `ДнС Тезисы` |
| rgbi | `RGBI` | `ДнС RGBI ОФЗ` |
| кс | `КС` | `ДнС КС` |
| cny / валюта | `CNY` | `ДнС CNY` |
| нефть | `BRENT` | `ДнС BRENT` |
| золото | `GLD` | `ДнС GLD` |
| биток / btc | `BTC` | `ДнС BTC` |

Акции — по тикеру MOEX. Informal → ticker:

| Конспект | ticker |
|---|---|
| сбер | SBER |
| втб | VTBR |
| домрф | DOMRF |
| озон | OZON |
| яндекс | YDEX |
| совком / совкомбанк | SVCB |
| ирао | IRAO |
| новатек | NVTK |
| сургут / сургутнефтегаз преф | SNGSP |
| транснефть | TRNFP |
| алроса | ALRS |
| магнит | MGNT |
| гмк | GMKN |
| moex / мосбиржа | MOEX |
| head / хед / хх | HEAD |
| cian / циан | CNRU |
| tatnp / татнефть преф | TATNP |
| t / т | T |
| ммк / magn | MAGN |
| пози | POSI |
| x5 | X5 |
| русал | RUAL |
| эн+ / энп | ENGP |

Не путать **MGNT (Магнит)** и **MAGN (ММК)**.

### 2. Тикеры из SQL

Перед разбором прочитай `invest_tickers` из `instance/main.db`:

```python
import sqlite3
c = sqlite3.connect("instance/main.db")
rows = c.execute("SELECT ticker, name, asset_type, sector FROM invest_tickers ORDER BY ticker").fetchall()
```

- `ticker` — код в новости (поле `invest_news.ticker`)
- `name` — русское имя для UI (`TICKER name`)
- Если тикера нет — добавить в `NEW_TICKERS` миграции

Новый тикер — минимальная строка по аналогии с соседями:

```python
{
    "ticker": "BTC",
    "name": "Биткоин",
    "asset_type": "Рынок",  # или Акция / Фонд
    "sector": "",
    "dependencies": [],
    "fee": None,
    "management_company": "",
}
```

Секторы: Фин, ИТ, Нефтянка, Металл, Магаз, Товары, Комм, Газ, Драг, Материалы, Недвига, Телеком, Хп, Алюм, Транспорт, Мир, Индекс.

Обновление `name` (было `ENGP` → `Эн+`) — `UPDATE` в той же миграции, не трогая остальные тикеры.

### 3. Новости → миграция

Файл: `migrations/versions/<revision>_dns_YYYY_MM_DD.py`  
`down_revision` = текущий head alembic.

Каждая новость — dict в `NEWS_ROWS`:

```python
{
    "slug": "2026-08-21 ДнС SBER",
    "datetime": datetime(2026, 8, 21, 20, 0, 0),
    "ticker": "SBER",
    "source": "днс-2026-08-21",  # stem файла источника без .md
    "summary": "налог на банки?",
    "price": "273",
    "sentiment": "🟡",
    "action": "наблюдать",
    "content": "",
}
```

Правила:

- **slug** — `YYYY-MM-DD ДнС <код>`; дата из имени источника; для макро — как раньше (`Тезисы`, `RGBI ОФЗ`, `КС`); для CNRU slug historically `ДнС CIAN`
- **source** — имя файла конспекта без `.md` (не wiki-ссылка)
- **ticker** — код из `invest_tickers.ticker`, не `name`
- **summary** — сжатый смысл (1–3 фразы). **Не дублировать текущую цену** — она только в `price`. Уровни/таргеты в summary оставлять
- **price** — из `тек`; нет цены → `""`
- **sentiment** — 🟢/🟡/🔴 из конспекта
- **datetime** — дата выпуска, время `20:00:00` если неизвестно
- **action** — по умолчанию `"наблюдать"`
- **content** — обычно `""`

`upgrade()`:

1. `bulk_insert` недостающих тикеров (с проверкой `SELECT 1 … WHERE ticker =`)
2. `UPDATE name` где нужно
3. `bulk_insert` в `invest_news`

`downgrade()`: удалить новости по slug из `NEWS_SLUGS`; откатить добавленные тикеры и переименования.

### 4. Проверка

- На каждый блок конспекта есть строка в `NEWS_ROWS`
- Все `ticker` есть в БД или в `NEW_TICKERS`
- `slug` уникальны (не конфликтуют с существующими в `invest_news`)
- После миграции: `flask db upgrade` (или `alembic upgrade head`)

### 5. Чтение БД на Windows

Если `sqlite3` CLI недоступен — Python:

```python
python -c "import sqlite3; c=sqlite3.connect('instance/main.db'); print(c.execute('SELECT ticker,name FROM invest_tickers').fetchall())"
```

## Не делать

- Не создавать `.md` в `Новости/` и `Тикеры/` — данные только в SQL
- Не коммитить без просьбы
- Не переименовывать тикеры вне выпуска, если пользователь не просил «все»
- Не путать MGNT/MAGN, SNGSP/SNGS, TATNP/TATN, CNRU/CIAN
