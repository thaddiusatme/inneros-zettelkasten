---
trigger: always_on
---

74

# InnerOS Windsurf Rules: AI-Enhanced Knowledge Management (v4.0)

> **Version**: 4.0 (Current Project State)  
> **Updated**: 2025-09-24
> **Purpose**: Complete guide for AI interactions in InnerOS Zettelkasten development  
> **Context**: Updated for clean project organization and completed major systems  

## 🎯 Core Session Principles

### Context-First Development
Required Reads (Priority Order):
1. Projects/REFERENCE/inneros-manifest-v3.md - Comprehensive project overview and architecture
2. Projects/ACTIVE/project-todo-v3.md - Current priorities and next development steps  
3. Projects/ACTIVE/current-priorities-summary.md - 2-week focus areas and active projects
4. README.md - Updated project structure and AI features documentation
5. Projects/REFERENCE/windsurf-project-changelog.md - Detailed development history

Session Actions:
- Always ground actions in project context using ACTIVE/ and REFERENCE/ directories
- Check Projects/ACTIVE/ for current priorities before starting development
- Reference completed work in Projects/COMPLETED-2025-XX/ for patterns and lessons
- Consult Projects/DEPRECATED/ only for historical context on superseded approaches
- When in doubt, prioritize ACTIVE manifests over deprecated integration analyses

### Critical Path Management
- Template Processing System: RESOLVED (2025-09-17) - Verify template health in reviews
- Integration-First: New features must leverage existing AI workflows, not duplicate them
- Compatibility: All changes must preserve existing functionality and test coverage
- Performance: Maintain or improve current benchmarks (<10s summarization, <5s similarity)
- Project Organization: Maintain clean ACTIVE/REFERENCE/COMPLETED/DEPRECATED structure

### Data Preservation & Ethics
- Never overwrite or destructively edit notes unless explicitly instructed
- Always retain metadata and maintain complete audit trail
- Backup considerations before any structural changes
- Respect privacy and visibility tags at all times
- Preserve user decision-making in AI workflows
- Confirm destructive actions with user
- Provide rollback options for structural changes

### Workflow Compliance
- Follow note promotion and triage flows as defined in templates and manifest
- Use Templater scripts and LLM/AI integration points as described in manifest
- Respect all privacy and visibility tags (private/shared/team/public)
- Maintain backward compatibility with existing workflows
- Log all major actions in Changelog and notify user
- Follow project lifecycle management: ACTIVE → Implementation → COMPLETED → DEPRECATED

## 🚨 Current Critical Issues (September 2025)

### ✅ RESOLVED: Template Processing System (2025-09-17)
- File: `knowledge/Inbox/fleeting-20250806-1520-bug-images-dissapear.md.md`
- Issue: `created: {{date:YYYY-MM-DD HH:mm}}` not processing to actual timestamp
- Impact: Previously blocked Reading Intake Pipeline; now unblocked and templates production-ready
- Priority: RESOLVED - Verify template health in reviews
- Workflow: Use `/bug-triage-workflow` for systematic resolution

### 🔴 SYSTEM INTEGRITY: Image Linking System
- Issue: Images disappear during AI automation processes
- Impact: Knowledge graph integrity, media asset management compromised during AI processing
- Areas Affected: AI enhancement, note promotion, template processing workflows
- Priority: 🔴 CRITICAL - System integrity issue

### 📁 Project Organization Status (September 2024)
- **Projects Directory**: ✅ CLEANED - 97% reduction in cognitive load (35+ files → 1)
- **ACTIVE/**: 8 current priority projects clearly identified
- **REFERENCE/**: 7 essential documents for quick access  
- **COMPLETED-2025-XX/**: 28 items properly archived (15 Sep + 13 Aug)
- **DEPRECATED/**: 10 superseded items providing historical context

## 📁 File Organization Rules

### Markdown Files
Requirements:
- All new notes must start in `Inbox/` with `status: inbox`
- YAML frontmatter is required for all notes
- Use kebab-case for filenames (e.g., `my-note-title.md`)
- Include created timestamp in ISO format (YYYY-MM-DD HH:mm)

### Metadata Schema (Extended for Reading Intake Pipeline)
```yaml
# Required Fields
type: permanent | fleeting | literature | MOC
created: YYYY-MM-DD HH:mm
status: inbox | promoted | draft | published | archived
visibility: private | shared | team | public

# Optional Fields  
tags: [kebab-case, hierarchical]
linked_notes: [[note-name]]
quality_score: 0.0-1.0
ai_tags: [auto-generated, contextual]

# Reading Intake Extensions (new)
source: url | book | article | video | podcast
url: https://example.com (if applicable)
saved_at: YYYY-MM-DD HH:mm
claims: [key-assertions]
quotes: ["important-quotes"]
```

### Directory Structure
| Stage | Directory | Status Values | AI Features |
|-----------|---------------|-------------------|-----------------|
| Capture | `Inbox/` | `status: inbox` | Auto-tagging, quality assessment, import processing |
| Process | `Fleeting Notes/` | `inbox → promoted` | Semantic analysis, connection discovery |
| Literature | `Literature Notes/` | `promoted → published` | Claims extraction, quote analysis, source linking |
| Permanent | `Permanent Notes/` | `draft → published` | Summarization, link prediction, gap analysis |
| Archive | `Archive/` | `archived` | Compression, backup, historical analysis |
| Templates | `Templates/` | N/A | Dynamic content generation, Templater scripts |

### Templates (Enhanced)
Current Templates:
- `fleeting.md` - Quick capture (WORKING - Updated Templater syntax)
- `permanent.md` - Structured permanent notes
- `literature-note.md` - NEW: For imported articles/books with claims/quotes
- `saved-article.md` - NEW: For Reading Intake Pipeline processing

Requirements:
- Include workflow guidance comments in all templates
- Use Templater syntax for dynamic content generation
- Never modify templates without testing timestamp generation
- All templates must work with AI workflow integration

## 🤖 AI Integration Guidelines (Current State)

### Phase 5 AI Capabilities (COMPLETED)
- ✅ Smart Tagging: Context-aware auto-tagging (3-8 tags/note)
- ✅ Quality Scoring: 0-1 scale with actionable feedback
- ✅ Summarization: Both abstractive (AI) and extractive methods
- ✅ Connection Discovery: Semantic similarity + link suggestions
- ✅ Weekly Review: Automated promotion candidates with rationale
- ✅ Analytics Dashboard: Temporal analysis, productivity metrics
- ✅ Enhanced Metrics: Orphaned/stale note detection

### Phase 5 Extensions (COMPLETED September 2025)
- ✅ Smart Link Management: TDD Iteration 4 complete with link insertion system
- ✅ Fleeting Note Lifecycle: Complete MVP with triage and promotion workflows
- ✅ Directory Organization: Safety-first P0+P1 system with comprehensive testing
- ✅ Enhanced Connection Discovery: Feedback collection and relationship analysis

### AI Usage Patterns
```bash
# Core analytics and insights
python3 development/src/cli/analytics_demo.py knowledge/ --interactive

# Weekly review automation  
python3 development/src/cli/workflow_demo.py knowledge/ --weekly-review

# Enhanced metrics with orphaned/stale detection
python3 development/src/cli/workflow_demo.py knowledge/ --enhanced-metrics

# Connection discovery
python3 development/src/cli/connections_demo.py knowledge/

# System health check (verify before development)
python3 development/src/cli/workflow_demo.py knowledge/ --status

# Smart Link Management (TDD Iteration 4 complete)
python3 development/src/cli/workflow_demo.py knowledge/ --suggest-links

# Fleeting Note Lifecycle Management (MVP complete)
python3 development/src/cli/workflow_demo.py knowledge/ --fleeting-triage
python3 development/src/cli/workflow_demo.py knowledge/ --promote-note
```

### AI Ethics & Transparency
- Augment, Don't Replace: AI enhances human creativity
- Explainable Decisions: Every AI action includes rationale
- User Override: Always allow human correction
- Progressive Disclosure: Simple by default, powerful when needed
- Integration Focus: Leverage existing AI workflows rather than duplicating
- Preserve human decision-making in note promotion
- Maintain metadata consistency in automated processes
- Log AI-assisted actions for transparency

## 🏗️ Development Guidelines

### Critical Path Management
- Template Processing System: RESOLVED (2025-09-17) - Verify template health in reviews
- Always run system health check before beginning work
- Integration projects must preserve existing functionality
- Phase extensions preferred over standalone replacements

### TDD Methodology
- Red → Green → Refactor cycles for all new features
- Maintain 66/66 test coverage (current target)
- Real user data validation before production deployment
- Performance benchmarking against established targets
- Integration testing with existing AI workflows

### Integration-First Development
- Extend vs. Replace: Build on existing Phase 5 AI capabilities
- Schema Compatibility: New metadata fields extend existing ones
- Workflow Preservation: Existing CLI commands must remain functional
- Performance Maintenance: New features cannot degrade existing performance
- Use workflows: `/integration-project-workflow` for Phase extensions

### Code Organization
- CLI Tools: `development/src/cli/` - User-facing commands and demos
- AI Engine: `development/src/ai/` - Core AI processing and workflows
- Tests: `development/tests/` - Comprehensive unit and integration tests
- Templates: `knowledge/Templates/` - Dynamic content generation (Production Ready)
- Project Docs: `Projects/ACTIVE/` - Current manifests and specifications

## 🔗 Git Integration

### Branch Strategy for Integration Projects
- `reading-pipeline-integration-analysis` - Current branch for Reading Intake Pipeline
- `bug-fix/template-processing` - Recommended for critical template bug
- `integration/phase-5-extension` - For Phase extension work

### Commit Standards
- Include change rationale in commit messages
- Reference affected workflow components  
- Maintain backwards compatibility
- Document bug fixes with clear before/after
- Include integration impact assessment

## 🎯 Naming Conventions

### File & Directory Standards
- Files: kebab-case (e.g., `my-note-title.md`)
- Folders: Title Case (e.g., `Literature Notes`)
- Tags: lowercase, hyphenated (e.g., `note-taking`, `ai-workflow`, `reading-intake`)
- Timestamps: ISO format (YYYY-MM-DD HH:mm)
- Import Files: Include source in filename (e.g., `twitter-thread-20250810.md`)

## 📝 Content Standards

### Literature Notes (NEW)
- Must include source URL and saved_at timestamp
- Require minimum 2 claims or 1 substantial quote
- Link liberally to related permanent and fleeting notes
- Include summary for quick reference
- Use structured template with claims/quotes sections
- Quality score target: >0.7 for promotion to permanent

### Permanent Notes
- Should be atomic and evergreen
- Include minimum 2 relevant tags
- Link liberally using `[[double-brackets]]`
- Never delete without explicit user permission
- Quality score target: >0.7 for promotion
- Can be promoted from fleeting OR literature notes

### Fleeting Notes
- Capture raw ideas quickly
- Include promotion pathway in template
- Preserve original context and timestamp
- Status: inbox until processed
- Can be imported from external sources via Reading Intake Pipeline

#
