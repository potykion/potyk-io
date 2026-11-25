# AGENTS.md

## Окружение

Агент работает на **Windows**, shell — **PowerShell**. Скрипты, one-liners и запись файлов — с учётом этого (без bash-heredoc; без UTF-8 BOM от `Set-Content -Encoding UTF8` — он ломает CSS/скрипты). Подробности — правило `windows-powershell.mdc`.

## UI / компоненты

Кнопки, поля, модалки, меню и прочий UI на **Jinja-страницах** — **только из дизайн-системы** (`/admin/design-system`, `forms.css`, `templates/docs/components/`). Не изобретать свой вид контрола под страницу. Подробности — правило `components-design-system.mdc`.

На **Vue SPA** (`potyk-io-front`, префикс `/v2`) — контролы **PrimeVue 4**, не копировать Jinja design-system.

## Спеки и код

Функциональные спеки лежат в `templates/docs/` (на сайте — `/docs`). Их пишет пользователь.

Агент спеки **не создаёт и не правит** по своей инициативе — только код. Трогать `templates/docs/` можно лишь по явной просьбе (или skill «оформление спеки»). Подробности — правило `spec-approval.mdc`.

## Стек

### Backend (`potyk_io_back/`, `main.py`)

- Python + **Flask**
- **SQLAlchemy** + **SQLite** (`instance/main.db`) + **Alembic**
- Auth: **flask-login** (секрет → сессия); `login_required` на закрытых разделах
- Legacy UI: Jinja + HTMX где уже есть

Запуск:

```powershell
python -m flask run --debug
```

### Frontend v2 (`potyk-io-front/`)

- **Vite** + **TypeScript** + **Vue 3**
- **PrimeVue 4** + `@primeuix/themes` (не PrimeVue 5 — платная лицензия)
- **Pinia** + **vue-router**
- Все клиентские роуты под префиксом **`/v2`** (`base: '/v2/'`)
- API под **`/v2/api/*`** (Flask blueprint `v2_bp`), cookie-сессия flask-login (`credentials: 'same-origin'`)
- Dev-proxy Vite: `/v2/api` и `/auth` → `http://127.0.0.1:5000`
- Prod: `npm run build` → Flask раздаёт `potyk-io-front/dist` с `/v2` (тоже `login_required`)

QA:

- `npm run typecheck` — vue-tsc
- `npm run lint` — Biome
- `npm run test` — Vitest
- `npm run qa` — typecheck + lint + test + `npm audit`
- CI (`.github/workflows/deploy.yml`): Frontend QA + tests + build; на `master` после зелёного CI — деплой с `dist` артефактом в `potyk-io-front/dist`

Запуск:

```powershell
cd potyk-io-front
npm install
npm run dev
```

Открывать `http://127.0.0.1:5173/v2/fin` (Flask на `:5000` должен быть запущен).
