---
name: youtube-recipe
description: >-
  Тянет title и description с YouTube (oEmbed + yt-dlp) и оформляет ролик
  как рецепт/идею potyk-food. Use when user sends a YouTube watch/shorts/youtu.be
  link for a recipe or food idea, asks to clip a YouTube recipe, or mentions
  oEmbed / yt-dlp for food content.
---

# YouTube → рецепт / идея

Не просить пользователя вставлять название и описание ролика вручную — стянуть самому.

Дальше оформление — по skill `oformlenie-recepta` (шаблон, ideas/ или recipes/, оглавление).

## 1. Название — oEmbed

```
GET https://www.youtube.com/oembed?url=<URL>&format=json
```

- `title` — название ролика
- `author_name` — канал (по желанию)
- `thumbnail_url` — превью (не класть в md как титульное фото рецепта без нужды)

Работает для `youtube.com/watch`, `/shorts/`, `youtu.be`.

**oEmbed не отдаёт description.**

## 2. Описание — yt-dlp

PowerShell (без `python -c` с кавычками):

```powershell
yt-dlp --print "%(title)s" --print "%(description)s" "https://www.youtube.com/shorts/XXXX"
```

Или во временный файл, если вывод длинный:

```powershell
yt-dlp --print "%(description)s" "URL" | Out-File -Encoding utf8NoBOM _tmp_yt_desc.txt
```

На Windows PowerShell 5 `utf8NoBOM` может отсутствовать — тогда читать stdout напрямую или писать через .NET UTF8 без BOM.

Если yt-dlp падает («not available on this app» и т.п.) — fallback:

1. `WebFetch` на `https://www.youtube.com/watch?v=<id>` (shorts тоже резолвятся в watch)
2. Либо описание уже в чате от пользователя — взять оттуда, не долбить повторно

## 3. Что вытащить из description

- Ингредиенты (списки, секции marinade / sauce)
- Шаги приготовления (если есть; иначе в «Приготовление» честно написать, что шагов в описании нет — смотреть ролик)
- Хэштеги и маркетинговый мусор выкинуть

## 4. Файл

- Имя: английский kebab-case (`kung-pao-chicken.md`)
- Куда: обычно `templates/potyk-food/ideas/` пока это идея; в `recipes/` — когда пользователь говорит оформить как рецепт
- Ссылка на ролик — в `## Ссылки` в конце
- Русский `#` заголовок по смыслу (англ. имя можно в скобках)
