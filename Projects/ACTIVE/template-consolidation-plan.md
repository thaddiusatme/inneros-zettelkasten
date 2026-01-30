# Project Pre-Plan: Template Consolidation

**Project:** Template Consolidation & Standardization
**Status:** ✅ Completed
**Objective:** Reduce template count, eliminate redundancy, and standardize template frontmatter for better observability.

## 1. Inventory & Clean Up (Immediate)

- [x] **Archive Legacy:** Move `permanent Note Morning Check In Template.md` to `Archive/Templates/` or delete.
- [x] **Archive Redundant:** Move `simple-youtube-trigger.md` and `content-idea-raw.md` to `Archive/Templates/`.

## 2. Consolidation (Development)

### A. Unified Content Idea Template (`project-content-idea.md`)
- [x] Created `knowledge/Templates/Content/idea.md` with standardized frontmatter and unified logic.
- [x] Archived redundant `content-idea.md` and `content-idea-raw.md`.

### B. Unified YouTube Template (`literature-youtube.md`)
- [x] Created `knowledge/Templates/Utility/youtube.md` with API fetching + fallback logic.
- [x] Archived `youtube-video.md` and `simple-youtube-trigger.md`.

## 3. Standardization (Architecture)

### Frontmatter Schema Update
All templates now output the following hidden frontmatter fields:

```yaml
template_id: <unique_slug>  # e.g., core-permanent
template_version: <semver>   # e.g., 1.0.0
```

### Directory Restructure
Organized `knowledge/Templates` into a clean, flat-but-grouped structure:

```text
knowledge/Templates/
  ├── Core/
  │   ├── permanent.md
  │   ├── fleeting.md
  │   ├── literature.md
  │   └── daily.md
  ├── Content/
  │   └── idea.md
  ├── Utility/
  │   ├── chatgpt-prompt.md
  │   └── youtube.md
  └── Reviews/
      ├── weekly.md
      ├── sprint-review.md
      └── sprint-retro.md
```

## 4. Execution Steps

- [x] **Refactor:** Created updated versions in `_Staging`.
- [x] **Deploy:** Moved templates to final subdirectories (`Core`, `Content`, `Utility`, `Reviews`).
- [x] **Cleanup:** Removed `_Staging` and verified `Archive/Templates`.

## 5. Success Criteria

- **Reduction:** Total active templates reduced from 14 to **9**.
- **Observability:** All active templates include `template_id` and `template_version`.
- **Usability:** Clear hierarchy (`Core` vs `Content` vs `Utility`).
