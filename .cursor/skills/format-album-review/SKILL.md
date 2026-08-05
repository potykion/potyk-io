---
name: format-album-review
description: >-
  Formats album review markdown files in potyk-mu style with YAML frontmatter,
  title, and Ревью section. Use when the user asks to format an album note,
  оформить альбом, or structure a draft in albums/*.md like an existing review.
---

# Format Album Review

## When to use

User drops a raw draft (link + freeform notes) into `albums/` and asks to оформить it like an existing review (e.g. `albums/nia-archives-emotional-junglst-2026.md`).

## File naming

`albums/{artist-slug}-{album-slug}-{year}.md`

- lowercase, hyphens, no spaces
- artist and album transliterated/latinized from common English names when known
- **Fallback:** if artist/album/year are missing from the draft body, parse them from the filename (`{artist-slug}-{album-slug}-{year}` → Title Case artist/album, numeric year). Multi-word slugs stay joined (`the-garden` → `The Garden`, `bootleg` → `Bootleg`)

## Target structure

```markdown
---
artist: Artist Name
album: Album Title
year: YYYY
yandex: https://music.yandex.ru/album/ID
rym: https://rateyourmusic.com/release/...
listened: YYYY-MM-DD
rate: N
---

# Artist Name — Album Title (YYYY)

## Ревью

[review body]
```

## Rules

1. **Frontmatter**
   - Keys `artist`, `album`, `year`, `yandex`, `rym`, `listened`, `rate` — always present
   - Fill artist/album/year from draft content / link when available; otherwise fall back to filename parsing
   - `listened` — default to today's date as `YYYY-MM-DD` (unless already set in the draft)
   - `yandex`, `rym`, `rate` — fill from draft if the user provided them; otherwise leave empty (`yandex:`, `rym:`, `rate:`) — do not invent URLs/scores or ask unless artist/album/year stay ambiguous even after filename
   - Strip UTM / query params from links; keep clean canonical URLs (`https://music.yandex.ru/album/{id}`, RateYourMusic release URL as given)

2. **Title**
   - Exact pattern: `# {artist} — {album} ({year})` (em dash `—`)

3. **Body**
   - Put all review text under `## Ревью`
   - Preserve the author's voice, slang, typos-as-style, emphasis (`**`, `*`), and emoji
   - Do not rewrite, soften, or expand the review
   - Keep track-by-track numbered lists if present; do not invent track lists if absent
   - Light whitespace cleanup only (blank lines between paragraphs); no content edits

4. **Reference**
   - Match the latest well-formed file in `albums/` when unsure about details

## Workflow

1. Read the draft and one good example from `albums/`
2. Extract artist, album, year, yandex, rym, rate (from draft → else filename fallback for artist/album/year; leave link/score fields empty if missing); set `listened` to today if absent
3. Rewrite the file into the target structure without changing review meaning
4. Leave unrelated album files untouched
