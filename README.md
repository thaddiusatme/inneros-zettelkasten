# innerOS — Zettelkasten + AI Workflow

Welcome to the `innerOS` workspace! This vault is designed for frictionless idea capture, structured Zettelkasten note-taking, and AI-assisted workflows, with privacy and future collaboration in mind.

## Key Documents
- **Windsurf Project Manifest.md** — Project overview, workflow, schema, privacy/compliance, and next steps.
- **Windsurf Project Changelog.md** — Tracks major changes, schema updates, and workflow improvements.
- **Windsurf Project Instructions.md** — Ensures every new session references the Manifest and Changelog for context.

## Directory Structure
- `Fleeting Notes/` — Quick idea capture, triaged for promotion.
- `Permanent Notes/` — Atomic, evergreen notes with rich metadata and links.
- `Templates/` — Templater scripts for note creation and automation.
- Additional folders: `Content Pipeline/`, `Protocols/`, `Reviews/`, etc.

## Note Schema (YAML/Markdown Example)
```markdown
---
type: permanent | fleeting | literature | MOC
created: YYYY-MM-DD HH:mm
status: inbox | promoted | draft | published
tags: [#permanent, #zettelkasten, ...]
visibility: private | shared | team
---
```

## AI & Automation
- Templater scripts automate file naming, sorting, and metadata.
- LLM/AI integration points for summarization, tagging, linking, and triage (see Manifest).

## Privacy & Collaboration
- All notes default to private. Future-proofed for multi-user and compliance needs.
- Manifest and Changelog document all conventions and changes.

## Getting Started
1. Read the Manifest and Changelog for project context.
2. Use provided templates for new notes.
3. Follow the triage flow for fleeting → permanent note promotion.
4. Update the Changelog with major changes.

---

_This README is a quickstart guide. For full project context, always consult the Manifest and Changelog._
