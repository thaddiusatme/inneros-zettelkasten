---
title: Windsurf Project Instructions
author: myung (and Cascade)
created: 2025-07-19 19:28
status: active
---

# Windsurf Project Instructions

## Always-Read Project Context for Windsurf

Before starting any new conversation or automation in this workspace, Windsurf (or any AI assistant) should:

1. **Read and reference the following documents:**
    - `Windsurf Project Manifest.md` (project goals, schema, workflow, privacy)
    - `Windsurf Project Changelog.md` (current state, recent changes)

2. **Use these documents to understand:**
    - The project’s scope, requirements, and privacy/compliance needs
    - The current note-taking workflow, automation, and AI integration points
    - The clarified inbox workflow: `status: inbox` in YAML is the workflow indicator; `Inbox/` folder is a staging area only; templates (e.g., fleeting.md) now include workflow guidance
    - Any recent updates or changes that may affect the workflow

3. **If these documents are missing or outdated:**
    - Prompt the user to review or update them before proceeding with major changes

---

_This ensures every session starts with the right context and keeps the project aligned with your evolving needs._

## Windsurf Rules for Project Processing

1. **Context First**
   - On every run, read and reference:
     - `Windsurf Project Manifest.md`
     - `Windsurf Project Changelog.md`
     - `README.md`
   - Use these to ground all actions in project context, schema, and requirements.

2. **Session Summary**
   - Summarize project goals, structure, and recent changes before proceeding.
   - If context docs are missing or outdated, prompt the user to update.

3. **Preserve Data**
   - Never overwrite or destructively edit notes unless explicitly instructed.
   - Always retain metadata and maintain an audit trail.

4. **Workflow Compliance**
   - Follow note promotion and triage flows as defined in templates and manifest.
   - Use Templater scripts and LLM/AI integration points as described.
   - Respect all privacy and visibility tags.

5. **User Alignment**
   - When in doubt, consult the Manifest and Changelog before asking the user.
   - Log all major actions in the Changelog and notify the user.

---
