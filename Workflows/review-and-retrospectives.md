---
title: Review & Retrospectives SOP
created: 2025-08-14 00:00
status: active
type: SOP
---

# 🗓️ Review & Retrospectives (Daily/Weekly/Sprint)

Minimalist, on-demand reviews with clear naming, YAML schema, and simple automation.

## Cadence
- Daily: optional, use when helpful
- Weekly: run every 7 days or as needed
- Sprint: create Review + Retrospective per sprint (IDs start at 001)

## Naming
- Daily: `daily-YYYY-MM-DD`
- Weekly: `weekly-review-YYYY-MM-DD`
- Sprint Review: `sprint-<ID>-review` (e.g., `sprint-001-review`)
- Sprint Retrospective: `sprint-<ID>-retro` (e.g., `sprint-001-retro`)

## Minimal YAML Schema
- `type: review`
- `scope: daily | weekly | sprint-review | sprint-retrospective`
- `sprint_id: 001` (only for sprint docs)
- `created: YYYY-MM-DD HH:mm` (America/Los_Angeles)
- `status: draft | published`
- `tags: ["#review", "#daily|#weekly|#sprint|#retrospective"]`
- `tz: America/Los_Angeles`

## Templates
Located in `knowledge/Templates/`:
- `Core/daily.md`
- `Reviews/weekly.md`
- `Reviews/sprint-review.md`
- `Reviews/sprint-retro.md`

All templates use Obsidian Templater to:
- Name the file to the convention above
- Move it into `Reviews/`
- Stamp `created` with the current timestamp (Templater `<% tp.date.now(...) %>`)

## MVP Metrics (record in-note only)
- Content published
- Leads created
- Days of consistency (streak)
- Sentiment (1–5)

## Minimal Content Pipeline Maintenance (Sprint Review)
- Review backlog health (5 min)
- Prune stale ideas (5 min)
- Tag/link high-potential items (5 min)

## CLI Usage
- Weekly checklist (AI-powered):
  - Generate: `inneros workflow --weekly-review`
  - Export: `inneros workflow --weekly-review --export-checklist Reviews/weekly-review-YYYY-MM-DD.md`
- Enhanced metrics (orphaned/stale):
  - `inneros workflow --enhanced-metrics`

Notes:
- Daily/Sprint docs are created via templates (on-demand)
- Actions are tracked in-note only (not synced externally)
- Link new review docs from relevant MOCs (optional but recommended)
