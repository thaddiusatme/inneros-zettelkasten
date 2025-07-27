---
trigger: always_on
---

# .windsurfrules
# innerOS Zettelkasten + AI Workflow Rules

# CORE SESSION PRINCIPLES
session:
  context_first:
    required_reads:
      - "Windsurf Project Manifest.md"
      - "Windsurf Project Changelog.md" 
      - "README.md"
    actions:
      - "Always ground actions in project context, schema, and requirements"
      - "Summarize project goals, structure, and recent changes before proceeding"
      - "If context docs are missing or outdated, prompt user to update"

  data_preservation:
    - "Never overwrite or destructively edit notes unless explicitly instructed"
    - "Always retain metadata and maintain audit trail"
    - "Backup considerations before structural changes"

  workflow_compliance:
    - "Follow note promotion and triage flows as defined in templates and manifest"
    - "Use Templater scripts and LLM/AI integration points as described"
    - "Respect all privacy and visibility tags"

  user_alignment:
    - "When in doubt, consult Manifest and Changelog before asking user"
    - "Log all major actions in Changelog and notify user"

# FILE ORGANIZATION RULES
files:
  markdown:
    pattern: "**/*.md"
    requirements:
      - "All new notes must start in Inbox/ with status: inbox"
      - "YAML frontmatter is required for all notes"
      - "Use kebab-case for filenames (e.g., my-note-title.md)"
      - "Include created timestamp in ISO format (YYYY-MM-DD HH:mm)"
    
    metadata_schema:
      required_fields:
        - "type: permanent | fleeting | literature | MOC"
        - "created: YYYY-MM-DD HH:mm"
        - "status: inbox | promoted | draft | published"
        - "visibility: private | shared | team"
      optional_fields:
        - "tags: [contextual, hierarchical]"
        - "linked_notes: [[note-references]]"

  templates:
    pattern: "Templates/**"
    requirements:
      - "Include workflow guidance comments in all templates"
      - "Use Templater syntax for dynamic content generation" 
      - "Template names should match note types (fleeting.md, permanent.md)"
      - "Never modify templates without updating Changelog"

# WORKFLOW STATE MANAGEMENT
workflow:
  inbox_processing:
    - "Inbox/ is staging area only - notes move to permanent folders after triage"
    - "Status field drives workflow, not folder location"
    - "Only notes with status: inbox require active triage"
    
  note_progression:
    states: "inbox → promoted → draft → published"
    validation:
      - "Status transitions must be logged"
      - "Metadata must be preserved during moves"
      - "Links must be updated when notes relocate"

  triage_rules:
    - "Fleeting notes → Fleeting Notes/ folder"
    - "Permanent notes → Permanent Notes/ folder" 
    - "Reference/actionable → appropriate specialized folder"
    - "Maintain audit trail of all movements"

# NAMING CONVENTIONS
naming:
  files: "kebab-case"
  folders: "Title Case"
  tags: "lowercase, hyphenated"
  timestamps: "ISO format (YYYY-MM-DD HH:mm)"

# CONTENT STANDARDS
content:
  permanent_notes:
    - "Should be atomic and evergreen"
    - "Include minimum 2 relevant tags"
    - "Link liberally using [[double-brackets]]"
    - "Never delete without explicit user permission"
    
  fleeting_notes:
    - "Capture raw ideas quickly"
    - "Include promotion pathway in template"
    - "Preserve original context and timestamp"

# GIT INTEGRATION
git:
  hooks:
    pre_commit:
      - "Validate YAML frontmatter integrity"
      - "Check required metadata fields"
      - "Verify link consistency"
    
    post_commit:
      - "Auto-update Windsurf Project Changelog.md"
      - "Preserve user notification requirements"
  
  commit_standards:
    - "Include change rationale in commit messages"
    - "Reference affected workflow components"
    - "Maintain backwards compatibility"

# PRIVACY & COLLABORATION
privacy:
  defaults:
    - "All notes default to visibility: private"
    - "Respect existing visibility settings"
    - "Future-proof for multi-user scenarios"
  
  compliance:
    - "Maintain audit trail for visibility changes"
    - "Document any privacy-related modifications in Changelog"

# AI & AUTOMATION INTEGRATION
ai_workflows:
  - "Use LLM integration points as defined in Manifest"
  - "Preserve human decision-making in note promotion"
  - "Maintain metadata consistency in automated processes"
  - "Log AI-assisted actions for transparency"

# ERROR HANDLING & RECOVERY
error_handling:
  - "Always confirm destructive actions with user"
  - "Provide rollback options for structural changes"
  - "Log errors and recovery steps in Changelog"
  - "Maintain system state consistency"

# VALIDATION RULES
validation:
  required_on_creation:
    - "Valid YAML frontmatter"
    - "Proper status field (inbox|promoted|draft|published)"
    - "Valid type field (permanent|fleeting|literature|MOC)"
    - "Created timestamp present"
  
  required_on_modification:
    - "Preserve existing metadata unless explicitly changing"
    - "Update modification timestamps"
    - "Maintain link integrity"
    - "Log changes in appropriate tracking mechanisms"