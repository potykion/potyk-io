# AGENTS.md

## Окружение

Агент работает на **Windows**, shell — **PowerShell**. Скрипты, one-liners и запись файлов — с учётом этого (без bash-heredoc; без UTF-8 BOM от `Set-Content -Encoding UTF8` — он ломает CSS/скрипты). Подробности — правило `windows-powershell.mdc`.

## UI / компоненты

Кнопки, поля, модалки, меню и прочий UI — **только из дизайн-системы** (`/admin/design-system`, `forms.css`, `templates/docs/components/`). Не изобретать свой вид контрола под страницу. Подробности — правило `components-design-system.mdc`.

## Спеки и код

Функциональные спеки лежат в `templates/docs/` (на сайте — `/docs`). Их пишет пользователь.

Агент спеки **не создаёт и не правит** по своей инициативе — только код. Трогать `templates/docs/` можно лишь по явной просьбе (или skill «оформление спеки»). Подробности — правило `spec-approval.mdc`.
