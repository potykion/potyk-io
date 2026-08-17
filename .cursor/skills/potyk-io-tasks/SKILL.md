---
name: potyk-io-tasks
description: >-
  Выполняет задачи из templates/potyk-io/tasks со статусом new: читает README,
  делает каждую задачу, переносит в done, ведёт отдельный PyCharm changelist
  на задачу. Use when the user asks to сделать задачи, взять new, выполнить
  tasks, разобрать tasks/, или указывает на templates/potyk-io/tasks.
---

# Задачи potyk-io

Язык ответа — русский. Перед работой прочитай `templates/potyk-io/tasks/README.md` и этот скилл. Ченжлисты — по `.cursor/skills/pycharm-changelist/SKILL.md`.

## README (кратко)

Свойства в YAML frontmatter:

- `project`: `potyk-io` / `task-man` / `potyk-fin`
- `status`:
  - `idea` / `draft` — не брать
  - `new` — можно в работу
  - `wip` — уже в процессе
  - `done` — выполнено

Выполненные задачи **перемещаем** в `templates/potyk-io/tasks/done/`.

## Workflow

1. Прочитай `templates/potyk-io/tasks/README.md`.
2. Собери `templates/potyk-io/tasks/*.md` (не `done/`, не `.obsidian`) с `status: new`.
3. Каждую задачу — **отдельно**, до конца, потом следующую.
4. Для каждой:
   1. Прочитай файл целиком. Имя changelist = **имя файла** (`Fix-menu-mobile.md`).
   2. Создай/обнови Local Changelist (см. pycharm-changelist).
   3. Сделай задачу в коде/контенте. Не коммить, пока не попросили.
   4. Поставь `status: done`, **перенеси** файл в `templates/potyk-io/tasks/done/` (не копируй).
   5. Перенеси все свои файлы этой задачи в её changelist, включая новый путь в `done/` и untracked.
5. В ответе: список задач (было → стало) + что сделано по каждой.

## Changelist

- **Имя** = имя файла задачи: `Feat-hashtags.md`
- **Comment** = conventional commit со scope + Refs на файл:

```text
feat(hashtags): кликабельные хештеги ведут в поиск

Refs: templates/potyk-io/tasks/done/Feat-hashtags.md
```

После переноса в `done/` Refs указывает на актуальный путь. Несколько задач в чате — несколько changelist, active остаётся `Changes`.

## Что не трогать

- `status: idea` / `draft` / `wip` / `done`
- чужие незакоммиченные файлы и чужие changelist
- `tasks/.obsidian/`
