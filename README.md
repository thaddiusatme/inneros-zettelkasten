    # innerOS — Zettelkasten + AI Workflow

    Welcome to the `innerOS` workspace! This vault is designed for frictionless idea capture, structured Zettelkasten note-taking, and AI-assisted workflows, with privacy and future collaboration in mind.

    ## Key Documents
    - **Windsurf Project Manifest.md** — Project overview, workflow, schema, privacy/compliance, and next steps.
    - **Windsurf Project Changelog.md** — Tracks major changes, schema updates, and workflow improvements.
    - **Windsurf Project Instructions.md** — Ensures every new session references the Manifest and Changelog for context.

    ## Directory Structure
    - `Inbox/` — Staging area for new, unsorted notes. All new notes (fleeting, reference, actionable) start here with `status: inbox` in YAML.
    - `Fleeting Notes/` — Quick idea capture, triaged for promotion. Only notes with proper YAML frontmatter and `status: inbox` are in the active fleeting workflow.
    - `Permanent Notes/` — Atomic, evergreen notes with rich metadata and links.
    - `Templates/` — Templater scripts for note creation and automation, now updated with workflow guidance comments.
    - Additional folders: `Content Pipeline/`, `Protocols/`, `Reviews/`, etc.

    ## Note Schema (YAML/Markdown Example)
    ```markdown
    ---
    type: permanent | fleeting | literature | MOC
    created: YYYY-MM-DD HH:mm
    status: inbox | promoted | draft | published
    tags: [permanent, zettelkasten, ...]
    visibility: private | shared | team
    ---
    ```
    - **status: inbox** in YAML is the primary indicator for notes needing triage, regardless of folder location.
    - The `Inbox/` folder is a temporary staging area, not a workflow state.

    ## How Inbox Works
    - All new notes are created in the `Inbox/` folder with `status: inbox` in YAML.
    - During triage (weekly or as needed), notes are moved to their permanent location:
        - Fleeting notes → `Fleeting Notes/`
        - Permanent notes → `Permanent Notes/`
        - Reference/actionable notes → appropriate folder
    - Only notes with `status: inbox` in YAML are considered active for triage, regardless of folder.
    - The `fleeting.md` template (and others) now include workflow guidance comments to reinforce this process.

    ## AI & Automation
    - Templater scripts automate file naming, sorting, and metadata, now with workflow guidance.
    - LLM/AI integration points for summarization, tagging, linking, and triage (see Manifest).

    ## Privacy & Collaboration
    - All notes default to private. Future-proofed for multi-user and compliance needs.
    - Manifest and Changelog document all conventions and changes.

    ## Version Control
    This repository is version controlled with Git to:
    - Track changes to notes, templates, and workflow documentation (see recent changelog entries for template and workflow alignment)
    - Enable safe experimentation with new workflows and organization
    - Facilitate collaboration while maintaining change history
    - Provide backup and restore capabilities
    - Support branching for experimental features or major reorganizations

    Key Git files:
    - `.gitignore` — Excludes temporary files, system files, and optional private content
    - `.git/hooks/pre-commit` — Validates metadata in staged markdown files before committing.
    - `.git/hooks/post-commit` — Automatically updates `Windsurf Project Changelog.md` with the commit message after a successful commit.

    ## Getting Started
    1. Read the Manifest and Changelog for project context.
    2. Use provided templates for new notes.
    3. Follow the triage flow for fleeting → permanent note promotion.
    4. Update the Changelog with major changes.

    ---

    _This README is a quickstart guide. For full project context, always consult the Manifest and Changelog._
