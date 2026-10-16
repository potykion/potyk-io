---
name: tag-album-mp3
description: >-
  Renames and ID3-tags raw album MP3s (usually yt-dlp downloads with [videoId]
  in filenames): strip brackets, set track/title/artist/album/year/cover from a
  YouTube Music playlist. Use when the user asks to оформить альбом as mp3s,
  проставить метаданные/теги, rename playlist downloads, or points at a folder
  of raw .mp3 plus a youtube.com/playlist link — not for potyk-mu markdown reviews
  (use format-album-review).
---

# Tag Album MP3s

## When to use

User has a folder of raw `.mp3` (typically `Title [youtubeId].mp3` from yt-dlp) and a YouTube / YouTube Music playlist URL. Goal: clean filenames + full ID3 tags.

**Not this skill:** markdown reviews in `albums/*.md` → `format-album-review`.

## Inputs

Required:

- Path to folder with `.mp3`
- Playlist URL (`youtube.com/playlist?list=...`)

Optional (prefer if given — do not invent alternatives):

- Cover image URL or local file
- Artist / album / year overrides
- Explicit note that this is a **reissue** (use reissue year, not original)

## Metadata rules

| Field | Source |
| --- | --- |
| Track order + titles | `yt-dlp --flat-playlist` playlist index/title/id |
| Artist | Playlist uploader / album artist; else user; common default from release page |
| Album | Playlist title (or user override) |
| Year | Year of **this** release the playlist represents. Reissue → reissue year (e.g. 2026), not the original. If ambiguous, ask once. |
| Cover | 1) user URL/file 2) playlist thumbnail (`i9.ytimg.com/s_p/{listId}/maxresdefault.jpg` or yt-dlp playlist thumb) 3) only then other sources. Do not stall on Cover Art Archive / Bandcamp if a usable URL exists. |
| Track total | Playlist length (`N` in `track/N`) |

Match files to playlist rows by **YouTube video id** in `[...]`, not by fuzzy title (titles often differ in `?` / casing / fullwidth punct).

## Filename rules

Target: `{NN}. {Title}.mp3` (zero-padded index from playlist).

1. Strip trailing ` [videoId]` (and any other `[...]` junk before `.mp3`).
2. Windows-illegal in **filenames** only: `<>:"/\|?*` and fullwidth `？` → replace with `_` or drop; keep the real title in ID3 (`TIT2`).
3. Prefer readable fallbacks for titles that become empty/ugly after sanitizing (e.g. `?¿?` → `Question Marks.mp3`, ID3 stays `?¿?`).
4. Leave non-mp3 tools (`yt-dlp.exe`, README, etc.) untouched.
5. Missing playlist tracks: report; do not invent files.

## ID3 tags (mutagen)

Install if needed: `pip install mutagen --user`.

Set (ID3v2.3 save is fine):

- `TIT2` title
- `TPE1` artist
- `TALB` album
- `TYER` + `TDRC` year (`YYYY`)
- `TRCK` as `{n}/{total}`
- `APIC` front cover JPEG (`type=3`)

Wipe prior tags on each file before writing a clean set.

Reusable script: [scripts/tag_album_mp3.py](scripts/tag_album_mp3.py) — run with folder + playlist; optional `--cover`, `--artist`, `--album`, `--year`.

## Workflow

1. List folder `.mp3`; note `[id]` suffixes.
2. `yt-dlp --flat-playlist --print "%(playlist_index)s|%(title)s|%(id)s|%(playlist_title)s|%(playlist_uploader)s" URL`
3. Resolve artist / album / year (reissue vs original).
4. Get cover (user URL first).
5. Run tag script or equivalent Python: rename by id → tag.
6. Verify 1–2 files: title/artist/album/year/track + APIC present.
7. Delete any temporary `_tag_*.py` left in the music folder; keep `cover.jpg` only if useful (optional — tags already embed art).

## Environment

Windows + PowerShell. No bash heredocs. Prefer a short `.py` script over broken `python -c` quoting. Paths may contain Cyrillic (`Рабочий стол`).

## Anti-patterns

- Using original album year when user/playlist is a reissue
- Blocking on “perfect” square art when user already gave a cover URL
- Putting `?` in Windows filenames
- Matching tracks only by title string
- Editing `format-album-review` / `albums/*.md` as part of this task
