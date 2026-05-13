# Template Reduction Report

**Date:** 2026-01-09
**Scope:** `knowledge/Templates` directory and note usage analysis.

## Executive Summary

We currently have **14 templates** in `knowledge/Templates`. Usage analysis reveals that only **4 core types** (`permanent`, `fleeting`, `daily`, `literature`) account for ~90% of note volume.

There is clear redundancy in "Content Idea" templates and "YouTube" templates. Several templates appear unused or are legacy artifacts. Consolidating these will reduce maintenance overhead and cognitive load during note creation.

## 1. Current Template Inventory (14 Files)

| Template Name | Status / Type | Usage (Approx Notes) | Notes |
| :--- | :--- | :--- | :--- |
| `permanent.md` | **Core** | ~156 | Primary Permanent Note template. |
| `fleeting.md` | **Core** | ~147 | Primary Fleeting Note template. |
| `daily.md` | **Core** | ~52 | Daily Note template. |
| `literature.md` | **Core** | ~37 | General Literature Note template. |
| `youtube-video.md` | **Redundant** | Low | Detailed, API-powered capture. |
| `simple-youtube-trigger.md` | **Redundant** | Low | Minimal trigger for automation. |
| `content-idea.md` | **Redundant** | Low | Full content idea structure. |
| `content-idea-raw.md` | **Redundant** | Low | "Raw" version, very similar logic. |
| `permanent Note Morning Check In Template.md` | **Legacy** | 0 detected | Likely an example note saved as template. |
| `chatgpt-prompt.md` | **Utility** | Low | Specific utility. |
| `sprint-retro.md` | **Process** | Low | Project management. |
| `sprint-review.md` | **Process** | Low | Project management. |
| `weekly-review.md` | **Process** | ~5 | Weekly review structure. |
| `transcript.md` | **Utility** | ~11 | Transcript storage. |

## 2. Usage Analysis Findings

1. **Core Dominance:** `permanent` (156) and `fleeting` (147) are the workhorses.

2. **Redundancy - Content Ideas:**
   - `content-idea-raw.md` and `content-idea.md` share ~80% of their logic (prompts for title/pillar/channel, renaming logic).
   - *Recommendation:* Merge into a single `content-idea.md` with a prompt or logic to choose "Raw" vs "Detailed" mode, or simply standardizing on one robust flow.

3. **Redundancy - YouTube:**
   - `youtube-video.md` is complex (API calls, metadata fetching).
   - `simple-youtube-trigger.md` is simple (renaming + trigger call).
   - *Recommendation:* Consolidate into `literature-youtube.md`. The simple trigger might be obsolete if the detailed one is reliable, OR `simple-youtube-trigger.md` logic should be integrated as a fallback mode in the main template.

4. **Legacy Artifacts:**
   - `permanent Note Morning Check In Template.md`: This seems to be a specific instance of a note rather than a reusable template. It has hardcoded `created: 2025-07-05`.
   - *Recommendation:* Archive or move to a "Examples" folder, remove from active templates.

## 3. Consolidation Strategy

### Goal: Reduce to < 10 Active Templates

**Proposed Taxonomy:**

1. **Core Types:**
   - `core-permanent.md` (Standardized)
   - `core-fleeting.md`
   - `core-literature.md` (General + specialized modes for YouTube/Articles if needed)
   - `core-daily.md`

2. **Project / Content:**
   - `project-content-idea.md` (Merged `content-idea` + `content-idea-raw`)
   - `project-review.md` (Merged `weekly`, `sprint-review`, `sprint-retro` if possible, or keep distinct if workflows differ significantly. `weekly-review` seems distinct enough to keep.)

3. **Utilities:**
   - `util-transcript.md`

### Actionable Steps

1. **Delete** `permanent Note Morning Check In Template.md`.
2. **Merge** `content-idea-raw.md` into `content-idea.md`.
3. **Refine** `youtube-video.md` to be the single source of truth for YouTube capture, potentially renaming to `literature-youtube.md`. Archive `simple-youtube-trigger.md`.
4. **Standardize Frontmatter:** Add `template_id` and `template_version` to all remaining templates to track usage programmatically in the future.

## 4. Automation & CLI Needs

- **Frontmatter Standardization:** We need to ensure every note created by a template has a `template: <name>` field. Currently, we rely on `type:` or `tags:` which is imprecise.
- **Template Versioning:** Adding `template_version: v1.0` allows us to migrate notes later if schemas change.
