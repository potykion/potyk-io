---
name: daily-top-stocks
description: >-
  Грузит дневные доходности акций TQBR за месяц в SQL (invest_daily_returns)
  и показывает топ на /invest/stocks. Use when the user asks топ акций дня,
  дневные доходности, обновить доходности за месяц, daily top stocks,
  или /daily-top-stocks.
---

# Дневные доходности акций → SQL

Язык ответа — русский. Данные пишутся в **`invest_daily_returns`** (все ао/ап
TQBR с TRENDCLSPR за день: ticker, pct, value, volume, close, sector).
На сайте топ-10 с порогом оборота 100 млн ₽ — на `/invest/stocks` (вкладка
«Доходности»).

## Скрипт

```powershell
python .cursor/skills/daily-top-stocks/scripts/daily_top.py --month 10
python .cursor/skills/daily-top-stocks/scripts/daily_top.py --year 2026 --month 11
```

Источник: MOEX ISS (без токена). Сектор — `invest_tickers` + fallback в
`potyk_io_back/invest/daily_top.py`. Месяц перезаписывается целиком.

## Workflow для агента

```
- [ ] 1. Уточнить месяц/год
- [ ] 2. Запустить daily_top.py (нужна миграция invest_dret_95002c)
- [ ] 3. Открыть /invest/stocks?ym=YYYY-MM
- [ ] 4. Не коммитить instance/main.db без просьбы
```

## Не делать

- Не тянуть свечи через T-Invest MCP по одной бумаге
- Не писать отдельный JSON-кэш — только SQL
