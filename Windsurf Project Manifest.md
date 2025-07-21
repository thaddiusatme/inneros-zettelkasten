---
title: Windsurf Project Manifest
author: myung (and Cascade)
created: 2025-07-19 19:26
status: draft
---

# Windsurf Project Manifest

## Project Overview & Goals
This document serves as the context-engineering foundation and project manifest for the Zettelkasten + AI workflow improvements in the `innerOS` directory. The goal is to minimize friction from idea to note, blend manual and AI-assisted processes, and future-proof the system for privacy and multi-user scenarios.

## Workflow Diagram (Described)
1. **Capture Fleeting Note** → Templater Script
2. **Summarize (Local Model)** & **Suggest Tags (LLM Tagger)**
3. **Create/Update Permanent Note**
4. **Literature Pipeline:** Import reference → Extract highlights → Create literature note → Tag/Link
5. **Linking & Refinement:** LLM workspace, surface related notes, add "See Also" links, smart auto-linking
6. **Daily Journal Loop:** Morning prompt, reflection, daily insights (local model), smart connections
7. **Downstream Uses:** Content bank, GPT training data, social post generator, SOP drafts

## Note Types & Templates
- **Fleeting Notes:** Quick capture, minimal structure, triage checklist for promotion
- **Permanent Notes:** Atomic ideas, clear metadata, "Core Idea," "Why It Matters," "Links"
- **Literature Notes:** Reference highlights, context, source links
- **Reference/MOC Notes:** Maps of Content for navigation and structure

### Example Metadata Schema (YAML/Markdown)
```markdown
---
type: permanent | fleeting | literature | MOC
created: YYYY-MM-DD HH:mm
status: inbox | promoted | draft | published
tags: [#permanent, #zettelkasten, ...]
visibility: private | shared | team
---
```

## Automation & AI Integration Points
- **Templater Scripts:** Automate file naming, folder sorting, metadata insertion
- **LLM Hooks:** Summarization, tag suggestion, smart linking, triage checklists
- **Promotion Flow:** Automated checklist for fleeting → permanent note, with optional LLM assistance

## Privacy & Multi-user Considerations
- All notes default to private; add `visibility` metadata field for future sharing/compliance
- No overwriting of original notes—preserve all edits, enable audit trail if possible
- Document privacy principles and compliance roadmap in this manifest

## Next Steps & Open Questions
- ✅ Standardize YAML frontmatter for all notes (Template migration system implemented)
- Define clear LLM entry points and automation triggers
- Explore privacy-preserving multi-user workflows
- Collect feedback and iterate on schema and workflow
- Test and deploy template migration system to convert legacy templates

---

_This document is a living artifact. Update as the project evolves._
