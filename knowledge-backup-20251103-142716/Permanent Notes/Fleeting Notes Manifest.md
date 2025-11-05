---
author: myung (and Cascade)
created: 2025-07-20 22:42
references:
- ../Automation Project Manifest.md
status: published
tags:
- fleeting
- '#manifest'
title: Fleeting Notes Project Manifest
type: permanent
visibility: private
---

# Fleeting Notes Project Manifest

## Purpose
This manifest documents the workflow, schema, automation, and triage process for all fleeting notes in InnerOS. It references the main [Automation Project Manifest](../Automation Project Manifest.md) and adapts its conventions for the fleeting note lifecycle.

## Workflow Overview

### Inbox Tag vs. Inbox Folder
- **`status: inbox` (and `inbox` tag)**: Used in YAML frontmatter of fleeting notes to indicate the note needs triage and is active in the workflow.
- **`Inbox/` folder**: Physical directory for new, unsorted notes that have not yet been processed or classified. This is a staging area, not the main workflow.

### Recommended Process
1. **Capture**: All new notes (fleeting, reference, or actionable) start in the `Inbox/` folder with `status: inbox` in YAML.
2. **Sort/Process**: During your triage session, move each note to its appropriate destination:
   - If it's a fleeting note, move to `Fleeting Notes/` and ensure it has `status: inbox` in YAML.
   - If it's a reference, file in the correct folder.
   - If it's actionable, convert to a project/task note.
3. **Triage**: Regularly review all fleeting notes with `status: inbox` (regardless of folder), using the Manifest Table for at-a-glance status.
4. **Promotion**: When ready, fleeting notes are promoted to permanent notes (with updated metadata and links).
5. **Archive/Delete**: Old or irrelevant fleeting notes are archived or deleted, with audit trail maintained in this manifest.

## Note Schema (YAML Example)
```yaml
---
type: fleeting
created: YYYY-MM-DD HH:mm
status: inbox | promoted | archived
tags: [fleeting, inbox, ...]
visibility: private | shared
---
```

## Automation & Integration Points
- **Auto-Manifest Table**: This manifest includes a table of all fleeting notes, updated manually or via script.
- **Triage Checklist**: Each note includes a “Convert to permanent?” checkbox.
- **Metadata Validation**: All fleeting notes are validated against the schema above.
- **Promotion Flow**: Templater/AI can suggest when to promote or archive notes.

## Privacy & Compliance
- All fleeting notes default to `visibility: private`.
- No destructive edits—archived/deleted notes are logged in this manifest.

## Manifest Table

| Title/Link | Created | Status | Tags | Next Step |
|------------|---------|--------|------|-----------|
| [AI Notebook Strategy](fleeting-2025-05-19-ai-notebook-strategy.md) | 2025-05-19 15:45 | inbox | ai, workflow, productivity | Review for promotion |
| [Obsidian Template Trouble](fleeting-2025-05-19-obsidian-template-trouble.md) | 2025-05-19 16:20 | inbox | obsidian, templates, troubleshooting | Archive after template fixes |
| [Zettelkasten Entry Logic](fleeting-2025-05-19-zettelkasten-entry-logic.md) | 2025-05-19 14:30 | inbox | zettelkasten, workflow | Consider promoting to permanent |
| [Context Window Metaphor](fleeting-2025-07-04-context-window-metaphor-printing-paper.md) | 2025-07-04 00:59 | inbox | fleeting, inbox | Develop metaphor further |
| [Automated Voice Memo Routing](Automated%20Voice%20Memo%20Routing%20for%20Group%20or%20Person%20Comms.md) | 2025-07-08 21:55 | inbox | project, automation, productivity | Promote to project note |
| [Freelancing for Work](fleeting-2025-07-09-freelancing-for-work.md) | 2025-07-09 15:49 | inbox | fleeting, inbox | Expand into action plan |
| [Diablo 2 Druid Alt](fleeting-2025-07-11-diablo-2-druid-alt.md) | 2025-07-11 21:55 | inbox | fleeting, inbox, diablo2r | Archive (gaming note) |
| [TDD Context Code Review](fleeting-2025-07-20-tdd-context-code-review-step.md) | 2025-07-20 18:35 | inbox | fleeting, inbox | Promote to permanent |
| [Test Note](fleeting-2025-07-20-test.md) | 2025-07-20 18:53 | inbox | fleeting, inbox | Template example - archive |

*Last updated: 2025-07-20 22:54*
