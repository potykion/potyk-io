---
name: remove-bg
description: >-
  Убирает фон у картинок через rembg (прозрачный PNG). Use when the user asks
  убрать фон, удалить фон, remove background, rembg, или сделать фон
  прозрачным у изображения в static/ или welcome-mats.
---

# Удаление фона (rembg)

## Зависимости

`requirements-dev.txt`: `rembg[cpu]`, `pillow`

```
.venv\Scripts\pip.exe install -r requirements-dev.txt
```

## Скрипт

```
.venv/Scripts/python.exe .cursor/skills/remove-bg/scripts/remove_bg.py <вход> [выход]
```

- Без выхода → `<имя>.png` рядом со входом
- Всегда PNG с альфой; исходник не удаляет
- Модель: `u2net` (в rembg 2.x дефолт — гигабайтный `bria-rmbg`, его не используем)

Несколько файлов: перечислить путями аргументами.

## Workflow

```
- [ ] 1. rembg в .venv
- [ ] 2. Прогнать скрипт
- [ ] 3. Проверить альфу (углы transparent; Read часто рисует альфу чёрным)
- [ ] 4. При замене — удалить исходник без альфы
- [ ] 5. welcome-mats: один файл на коврик в static/potyk-io/img/welcome-mats/
```
