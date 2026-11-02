---
name: google-tasks-potyklo
description: >-
  Вытаскивает задачи из Google Tasks из колонки/списка «🤪 potyklo» (и других
  списков). Use when the user asks google tasks, гугл таски, potyklo, колонка
  potyklo, задачи из Google Tasks, или /google-tasks-potyklo.
---

# Google Tasks → 🤪 potyklo

Язык ответа — русский. По умолчанию — **незавершённые** задачи из списка с
`potyklo` в имени (колонка «🤪 potyklo»).

## Скрипт

```powershell
python .cursor/skills/google-tasks-potyklo/scripts/fetch_potyklo_tasks.py
python .cursor/skills/google-tasks-potyklo/scripts/fetch_potyklo_tasks.py --json
python .cursor/skills/google-tasks-potyklo/scripts/fetch_potyklo_tasks.py --list-lists
python .cursor/skills/google-tasks-potyklo/scripts/fetch_potyklo_tasks.py --list "mawa"
```

Зависимость для сетапа: `google-auth-oauthlib` (fetch сам по себе — только stdlib).

```powershell
.venv\Scripts\pip.exe install google-auth-oauthlib google-auth-httplib2
```

Секреты (gitignore `.cursor/secrets/`):

| Файл | Что |
|---|---|
| `google_tasks_client.json` | OAuth Client ID типа **Desktop app** (скачан из Console) |
| `google_tasks_token.json` | refresh token после `setup_auth.py` |

## Auth (один раз)

**Нельзя** брать Tasks scope через `gcloud auth application-default login` —
OAuth-клиент Cloud SDK Google блокирует (`This app is blocked`).

### 1. Desktop OAuth client в Cloud Console

Под аккаунтом `potykion@gmail.com`:

1. Любой личный GCP-проект (или новый).
2. [Enable Tasks API](https://console.cloud.google.com/apis/library/tasks.googleapis.com)
3. **APIs & Services → OAuth consent screen**
   - User type: **External**
   - Publishing status: **Testing**
   - Test users: добавь `potykion@gmail.com`
4. **Credentials → Create credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Download JSON → сохрани как  
     `.cursor/secrets/google_tasks_client.json`

### 2. Локальный consent

```powershell
python .cursor/skills/google-tasks-potyklo/scripts/setup_auth.py
```

Откроется браузер. Если «Google hasn’t verified this app» → Advanced →
Continue (для Testing + test user это норма).  
`This app is blocked` = снова попали на клиент gcloud / не тот JSON.

### 3. Fetch

```powershell
python .cursor/skills/google-tasks-potyklo/scripts/fetch_potyklo_tasks.py
```

## Workflow для агента

```
- [ ] 1. fetch_potyklo_tasks.py
- [ ] 2. Нет client/token → сказать юзеру про Desktop client JSON + setup_auth; не звать gcloud ADC с tasks scope
- [ ] 3. Показать markdown checklist
- [ ] 4. Дальше только по просьбе. Не закрывать/не править таски в Google без явной просьбы
```

## Фолбэк: браузер

Если API ещё не настроено, а юзер **залогинен в Google** в Cursor Browser
(или явно просит скрапить UI):

1. `browser_navigate` → `https://calendar.google.com/calendar/u/0/r/tasks`
2. Колонка с `potyklo` в заголовке
3. Incomplete titles → markdown checklist

## Чего не делать

- Не `gcloud auth application-default login --scopes=…tasks…` (blocked + портит ADC).
- Не коммитить `.cursor/secrets/`.
- Не завершать Google-таски без просьбы.
