---
name: shell-no-approval
description: >-
  Добавить shell-команду в Cursor terminalAllowlist, чтобы Agent запускал её
  без UI Pending approval. Use when user says «без подтверждения», «без апрува»,
  «не спрашивай», «auto-approve», «allowlist», «Pending approval», или просит
  сделать так, чтобы конкретная команда/скрипт запускалась без подтверждения.
---

# Shell без UI-подтверждения

Как сделать так, чтобы Cursor Agent **не** показывал Pending approval / Run на shell-команду.

## Главное правило

Cursor в Allowlist mode матчит `terminalAllowlist` по **бинарю** (первое слово команды), не по длинному префиксу с аргументами и не по пути к `.py`/`.ps1`.

| Не работает | Работает |
|---|---|
| `"powershell -File .cursor/skills/deploy/scripts/"` | `"powershell"` / `"powershell.exe"` |
| `".venv/Scripts/python .cursor/scripts/weeek_fetch_task.py"` | `".venv/Scripts/python"` / `".venv\\Scripts\\python"` |
| `autoRun.allow_instructions` («Always auto-approve…») | бинарь в `terminalAllowlist` |

`autoRun.allow_instructions` — только намёк Auto-review, **не** enforcement.

## Цепочки через `;`

Cursor парсит `cmd1; cmd2; cmd3` в **несколько** команд. Апрув не нужен только если **каждый** бинарь в allowlist.

Пример — почему лезла карточка при уже заallowlist’енных ruff/mypy:

```shell
.venv/Scripts/ruff check --fix a.py; .venv/Scripts/pytest tests -q; .venv/Scripts/mypy
```

Не хватало `.venv/Scripts/pytest`. Аналогично `Remove-Item` в хвосте цепочки валит весь вызов.

Правила для агента:

- В allowlist должны быть **все** бинари цепочки.
- Предпочтительнее **отдельные** Shell-вызовы (ruff / pytest / mypy по одному), а не `;` — проще дебажить апрув.

## Workflow: добавить команду без апрува

1. Возьми **реальную** команду, которой агент будет звать инструмент (как в скилле/чате).
2. Выдели бинарь = первое слово / путь к exe до аргументов.
3. Добавь в `.cursor/permissions.json` → `terminalAllowlist` (и зеркало в `~/.cursor/permissions.json` при необходимости).
4. Для Windows venv дублируй слэши: `.venv/Scripts/…` и `.venv\\Scripts\\…`; при сомнении добавь и `.exe`.
5. Чистый JSON без `//` комментариев.
6. Если карточка ещё лезет → **Reload Window**, повтори команду.

**Куда писать** (оба читаются, массивы склеиваются):

1. Репо: `.cursor/permissions.json` (коммитим)
2. Юзер: `~/.cursor/permissions.json`

`terminalAllowlist` в `permissions.json` **заменяет** IDE allowlist для terminal и форсит Allowlist mode.

## Примеры

### Deploy (powershell)

Команда:

```shell
powershell -File .cursor/skills/deploy/scripts/trigger_pipeline.ps1 -Pipeline deploy-ALL -Branch master -Push
```

В allowlist: `"powershell"`, `"powershell.exe"`, `"pwsh"`, `"pwsh.exe"`.

### Weeek fetch

Команда:

```shell
.venv/Scripts/python .cursor/scripts/weeek_fetch_task.py {id}
```

В allowlist: `".venv/Scripts/python"`, `".venv\\Scripts\\python"`, при необходимости `".venv/Scripts/python.exe"`.

То же покрывает `weeek_fetch_column.py` / `weeek_move_task.py` — бинарь тот же.

### mypy / ruff / black / pytest

```shell
.venv/Scripts/mypy
.venv/Scripts/ruff check --fix path/to/file.py
.venv/Scripts/black path/to/file.py
.venv/Scripts/pytest path/to/test.py -q
```

Цепочка `ruff; black; mypy` — **три** бинаря, все должны быть в allowlist (часто забывают `black`).

В allowlist: `".venv/Scripts/mypy"`, `".venv/Scripts/ruff"`, `".venv/Scripts/black"`, `".venv/Scripts/pytest"`, плюс `/.venv\\Scripts\\…/` и голые `"mypy"` / `"ruff"` / `"black"` / `"pytest"` / `*.exe`.

### Git commit (UTF-8, без Pending approval)

**Предпочтительно** — один вызов через хелпер (бинарь уже `powershell`):

```shell
powershell -File .cursor/scripts/git_commit_utf8.ps1 -Message "feat: hello" -Add path1.py,path2.py
```

Или только коммит (после отдельного `git add`):

```shell
powershell -File .cursor/scripts/git_commit_utf8.ps1 -Message "feat: hello`n`nRefs: https://app.weeek.net/ws/54307/task/8105"
```

Не пиши на cmdline `git commit --trailer "Co-authored-by: … <email>"` — `<>` парсер Cursor часто считает **redirect** и валит allowlist. Хелпер кладёт `Co-authored-by` в файл сообщения.

### Git commit вручную (длинная `;`-цепочка)

Если без хелпера — в allowlist должны быть **все** куски:

- `"git"` (покрывает `git add` / `commit` / `status` / `log` / `diff`)
- `"New-Object"`
- `"[System.IO.File]::WriteAllText"`
- `"Remove-Item"`

И **без** `--trailer` с `<>` на командной строке — `Co-authored-by` внутрь `$msg`.

## Проверка в логах

`%APPDATA%\Cursor\logs\...\anysphere.cursor-agent-exec\*.log`:

- `auto-approved shell command` + `allCommandsAllowlisted:true` — ок
- `requesting shell approval` + `unapproved_commands` — бинарь не в allowlist или файл не подхватился

## Поведение агента

Когда пользователь просит «сделай X без подтверждения» / «добавь в allowlist»:

1. Примени этот скилл (шаги выше).
2. Обнови `.cursor/permissions.json` (и `~/.cursor` при необходимости).
3. Кратко скажи, какой бинарь добавлен.
4. Коммит — только если пользователь явно попросил.
