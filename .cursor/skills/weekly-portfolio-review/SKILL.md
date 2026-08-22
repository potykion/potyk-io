---
name: weekly-portfolio-review
description: >-
  Делает недельный (или шире) обзор сделок (invest_deals в SQL) и новостей
  (invest_news) плюс интернет, разбор портфеля со скрина/списка позиций, идеи
  и мысли. Use when the user asks for обзор портфеля, обзор недели, разбор
  сделок, мысли по портфелю, weekly review, или кидает скрин брокерского
  портфеля.
---

# Недельный обзор портфеля / сделок / новостей

## Когда применять

Пользователь просит обзор недели, разбор портфеля, мысли по позициям, или присылает скрин портфеля (Т-Инвестиции и т.п.).

## Вход

1. Скрин / таблица портфеля (если есть)
2. Период: по умолчанию последняя неделя + релевантное «ранее»
3. Vault: `Идеи.md`, `Принципы.md`, `Источники/Деньги не спят/`
4. SQL (`instance/main.db`): `invest_deals`, `invest_deposit_changes`; новости — `invest_news` (см. dns-episode-to-news)
5. Интернет: макро + новости по тикерам портфеля и активным сделкам

## Workflow

```
- [ ] 1. Считать Принципы + Идеи + сделки из invest_deals (open/close)
- [ ] 2. Собрать новости за период (invest_news + ДнС тезисы/макро)
- [ ] 3. Разобрать портфель со скрина
- [ ] 4. Добить интернет (макро + лоссеры/виннеры + дивы)
- [ ] 5. Сверить с Принципами и топами ДнС/Василия
- [ ] 6. Выдать обзор + идеи; опционально сохранить в Обзоры/
```

### 1. Сделки и идеи

**Сделки — только SQL**, не `Сделки/*.md` (legacy). Схема: `potyk_io_back/invest/entities.py` → `InvestDeal`, таблица `invest_deals`. UI: `/invest/deals`.

Перед разбором прочитай сделки из `instance/main.db`:

```python
import sqlite3
from datetime import datetime, timedelta

c = sqlite3.connect("instance/main.db")
c.row_factory = sqlite3.Row

# открытые
open_deals = c.execute("""
    SELECT * FROM invest_deals
    WHERE closed_at IS NULL
    ORDER BY opened_at DESC, id DESC
""").fetchall()

# закрытые за период (подставь date_from / date_to)
closed_deals = c.execute("""
    SELECT * FROM invest_deals
    WHERE closed_at IS NOT NULL
      AND closed_at >= ?
      AND closed_at < ?
    ORDER BY closed_at DESC, id DESC
""", (date_from.isoformat(), date_to.isoformat())).fetchall()

deposit = c.execute("""
    SELECT amount FROM invest_deposit_changes
    ORDER BY date DESC, id DESC LIMIT 1
""").fetchone()
```

На Windows, если `sqlite3` CLI недоступен — только Python (как в dns-episode-to-news).

Поля сделки:

| SQL | Смысл |
|---|---|
| `ticker`, `opened_at` | Что и когда открыли |
| `volume`, `buy_price`, `qty` | Объём % депозита, цена входа, кол-во |
| `entry_level`, `exit_level` | Уровни входа/выхода (если были) |
| `take_profit_raw` / `take_profit_price` | Тейк |
| `stop_loss_raw` / `stop_loss_price` | Стоп |
| `thoughts` | Тезис при входе |
| `closed_at`, `sell_price`, `pnl` | Закрытие и результат ₽ |
| `close_thoughts`, `close_errors` | Вывод / ошибки при закрытии |

Классификация:

| Статус | SQL | Что писать |
|---|---|---|
| **open** | `closed_at IS NULL` | Цена входа vs сейчас (скрин), путь к TP/SL, стоп по Принципам |
| **close** | `closed_at IS NOT NULL` | P/L ₽ и %, урок из `close_thoughts` / `close_errors`, таргеты |
| **idea** | `Идеи.md` | Триггер входа, актуален ли; в SQL идей нет |

Для open-сделок сверяй `stop_loss_price` / `take_profit_price` с текущей ценой из скрина портфеля. `volume` — доля депозита на входе (лимит ≤5% из Принципов).

**Идеи** — по-прежнему `templates/potyk-invest/Идеи.md`.

Брокерские события (фактические покупки/продажи): https://www.tbank.ru/invest/portfolios/events/

### 2. Новости

- Основной источник: `invest_news` в `instance/main.db` (поля: `datetime`, `ticker`, `summary`, `price`, `sentiment`, `action`, `source`)
- За период:

```python
news = c.execute("""
    SELECT datetime, ticker, slug, summary, price, sentiment, action, source
    FROM invest_news
    WHERE datetime >= ? AND datetime < ?
    ORDER BY datetime DESC
""", (date_from.isoformat(), date_to.isoformat())).fetchall()
```

- Приоритет: тикеры из портфеля и открытых сделок (`invest_deals WHERE closed_at IS NULL`)
- Макро-тикеры: `IMOEX`, `КС`, `RGBI`, `BRENT`, `CNY`, `Глобал` (slug часто `ДнС Тезисы`)
- Свежий конспект в `Источники/Деньги не спят/` — если выпуск ещё не разнесён в SQL, читать источник
- `Новости/*.md` — legacy, не использовать как primary

### 3. Портфель со скрина

Вытащить: сумма, P/L общий и дневной, доли классов, по каждой бумаге qty / avg / last / value / share / P/L / day.

Сгруппировать:

- **Плюсы** / **минусы** (по P/L ₽ и %)
- **Сектора** (перекосы)
- **Vs Принципы**: объём ≤5%, горизонт 2нед–2мес, таргеты −10% / +20%, без плеча
- **Vs топы** из последнего ДнС / `Идеи.md`

Флаг: позиции **ниже −10%** без закрытия / плана — явное нарушение стопа из Принципов (если нет осознанного исключения).

### 4. Интернет

WebSearch (и fetch при необходимости):

1. Макро РФ за период: IMOEX, КС, нефть, рубль/CNY, геополитика
2. По крупным лоссерам и виннерам портфеля — причина движения
3. Дивкалендарь: ближайшие отсечки/выплаты по холдингам (ликвидность после выплат)

Не выдумывать цифры: брать из скрина / SQL / vault / свежих источников. Если данных нет — так и писать.

### 5. Выход

Ответ **на русском**, прямой тон. Можно сохранить:

`Обзоры/YYYY-MM-DD Недельный обзор.md`

Структура ответа / файла:

```markdown
# Обзор YYYY-MM-DD

## Коротко
1–3 предложения: вердикт по рынку + портфелю + главная мысль.

## Сделки
- Закрытые / открытые / идеи — факт + мысль

## Новости (SQL + интернет)
- Макро
- По позициям портфеля
- Что упустил SQL / конспект ДнС

## Портфель
- Снимок (сумма, P/L, структура)
- Что работает / что тянет
- Перекосы и vs Принципы
- Позиции под микроскоп (3–7 шт.)

## Идеи и мысли
Нумерованный список actionable: докупить / сократить / ждать уровень / закрыть стоп / идея вне портфеля
```

В «Идеи и мысли» — конкретные уровни и тикеры из контекста (не общие советы «диверсифицируй»).

## Не делать

- Не читать `Сделки/*.md` — сделки только в `invest_deals`
- Не коммитить без просьбы
- Не подменять Принципы своими (если конфликт — указать конфликт)
- Не рекомендовать плечо / деривативы
- Не раздувать текст: мысль → факт → действие
