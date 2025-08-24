---
type: permanent
created: 2025-07-19 19:26
modified: '2025-08-23'
status: active
title: Windsurf Project Manifest
author: myung (and Cascade)
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

## Implementation Status & Next Steps
- ✅ **Standardize YAML frontmatter for all notes** (Template migration system implemented)
- ✅ **End-to-end workflow validation** (Capture → Triage → Promotion → Archive/Delete tested and production-ready)
- ✅ **Audit trail and privacy model** (Full metadata tracking with `visibility: private` default)
- ✅ **Template system with validation** (Templater scripts generate compliant YAML, excluded from pre-commit validation)
- ✅ **Simplified permanent-note filenames** (removed `zettel-` prefix & timestamps; updated links and templates)
- ✅ **Git integration with metadata validation** (Pre-commit hooks ensure schema compliance)

### Ready for Phase 2: LLM Integration
- **Smart Tagging**: Implement AI-assisted tag suggestions during capture
- **Automated Summarization**: LLM-powered content analysis and summary generation
- **Connection Discovery**: Automatic linking between related notes
- **Triage Assistance**: AI-powered promotion recommendations
- **Privacy-Preserving Workflows**: Explore local model integration for sensitive content

### Future Considerations
- Multi-user workflows and sharing capabilities
- Advanced automation triggers and workflows
- Integration with external knowledge sources
- Performance optimization for large note collections

---

_This document is a living artifact. Update as the project evolves._
