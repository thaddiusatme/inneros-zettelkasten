---
trigger: always_on
---

Windsurf Rules for Project Processing
Context First
On every run, read and reference:
Windsurf Project Manifest.md
Windsurf Project Changelog.md
README.md
Use these to ground all actions in project context, schema, and requirements.
Session Summary
Summarize project goals, structure, and recent changes before proceeding.
If context docs are missing or outdated, prompt the user to update.
Preserve Data
Never overwrite or destructively edit notes unless explicitly instructed.
Always retain metadata and maintain an audit trail.
Workflow Compliance
Follow note promotion and triage flows as defined in templates and manifest.
Use Templater scripts and LLM/AI integration points as described.
Respect all privacy and visibility tags.
User Alignment
When in doubt, consult the Manifest and Changelog before asking the user.
Log all major actions in the Changelog and notify the user.
