---
name: update-index-toc
description: Rebuilds a folder's index.md as a TOC of all pages in that folder (titles + links). Use when the user asks to update/fill an index, TOC, оглавление, or points at a content folder like travel/plans, travel/memories, cool-stories.
---

# Update folder index TOC

When the user names a folder, rebuild that folder's `index.md` as a table of contents of its pages.

## Workflow

1. Resolve the target folder (relative to repo root or absolute path).
2. Read existing `index.md` if present (keep H1 + intro notes that are not page links).
3. Collect pages: all `*.md` and `*.html` in the folder **except** `index.md` / `index.html`. Do **not** recurse into subfolders unless the user asks.
4. For each page, resolve a **title** (see below).
5. Write/update `index.md`: preserved header + bullet list of links.
6. Briefly report what was added/removed/renamed.

## Title rules

Priority:

1. First markdown H1 (`# Title`) — skip `##` and deeper.
2. Else first HTML `<h1>...</h1>`.
3. Else `<title>...</title>`.
4. Else infer from filename / context in Russian, e.g.:
   - `china.md` → `Китай`
   - `egypt.md` → `Египет`
   - `vietnam.md` → `Вьетнам`
   - `msk.md` → `Мск` (if no H1)
   - unknown slug → humanize: `cool-place` → `Cool place`, or a short Russian gloss if obvious

Include empty stub files (title from rule 4).

## Link rules

- Link path = path from **repo root** to the page, **without** extension:
  - `travel/plans/cheby.md` → `/travel/plans/cheby`
  - `cool-stories/floating.md` → `/cool-stories/floating`
  - `travel/memories/vrn-26.html` → `/travel/memories/vrn-26`
- Prefer leading `/`. If the existing index already uses a consistent style without leading `/` (e.g. `cool-stories/floating`), match that style for the whole list.
- Never leave `.md` / `.html` in TOC links.

## Index shape

```markdown
# Existing or inferred H1

- optional intro bullet(s) that are not page links (keep if already there)
- [Title](/folder/slug)
- [Title](/folder/other)
```

- If `index.md` is missing: create it. H1 = folder name humanized, or a sensible Russian label if clear (`cool-stories` → `Кулстори`, `plans` → `` `/plans` ``, `memories` → `Воспоминания / впечатления о поездках` when that folder is `travel/memories`).
- Preserve non-link intro lines under the H1.
- Replace the old page-link list with the new full TOC (don't leave stale links to deleted files).

## Order

1. Keep the order of pages that already appear in the index.
2. Append newly discovered pages, sorted by title (locale-aware if easy, else alphabetical).
3. If the user asks for a specific order (e.g. by year descending), follow that instead.

## Examples

**User:** обнови index в `travel/plans`  
→ rebuild `travel/plans/index.md` from all files there (including empty `china.md` → Китай).

**User:** заполни toc для `cool-stories`  
→ rebuild `cool-stories/index.md` from `floating`, `trust`, `urologist`, `masha`, …

**User:** `/update-index-toc travel/memories`  
→ same workflow for that folder.
