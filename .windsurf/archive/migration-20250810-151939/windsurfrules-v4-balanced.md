---
trigger: always_on
type: permanent
created: 2025-08-10 13:38
status: published
tags: [windsurf, rules, inneros, ai-workflow, v4]
visibility: private
---

# InnerOS Windsurf Rules: AI-Enhanced Knowledge Management (v4.0)

> **Version**: 4.0 (Current Project State)  
> **Updated**: 2025-08-10  
> **Purpose**: Complete guide for AI interactions in InnerOS Zettelkasten development  
> **Context**: Includes Reading Intake Pipeline integration and critical bug management  

## 🎯 Core Session Principles

### **Context-First Development**
**Required Reads (Priority Order):**
1. **Projects/inneros-manifest-v2.md** - Comprehensive project overview and architecture
2. **Projects/project-todo-v2.md** - Current priorities and next development steps  
3. **Projects/reading-intake-integration-analysis.md** - Integration analysis and solution architecture
4. **README.md** - Quick start and AI features documentation
5. **Projects/windsurf-project-changelog.md** - Detailed development history

**Session Actions:**
- Always ground actions in project context, schema, and requirements
- Summarize project goals, structure, and recent changes before proceeding
- Check for critical bugs and dependencies before starting development
- Reference integration analysis for Phase extension projects
- When in doubt, consult Manifest and Integration Analysis before asking user

### **Critical Path Management**
- **Template Processing Bug**: CRITICAL BLOCKER - Must be resolved before new feature development
- **Integration-First**: New features must leverage existing AI workflows, not duplicate them
- **Compatibility**: All changes must preserve existing functionality and test coverage
- **Performance**: Maintain or improve current benchmarks (<10s summarization, <5s similarity)

### **Data Preservation & Ethics**
- Never overwrite or destructively edit notes unless explicitly instructed
- Always retain metadata and maintain complete audit trail
- Backup considerations before any structural changes
- Respect privacy and visibility tags at all times
- Preserve user decision-making in AI workflows
- Confirm destructive actions with user
- Provide rollback options for structural changes

### **Workflow Compliance**
- Follow note promotion and triage flows as defined in templates and manifest
- Use Templater scripts and LLM/AI integration points as described in manifest
- Respect all privacy and visibility tags (private/shared/team/public)
- Maintain backward compatibility with existing workflows
- Log all major actions in Changelog and notify user

## 🚨 Current Critical Issues (August 2025)

### **🔴 BLOCKING BUG: Template Processing Failure**
- **File**: `knowledge/Inbox/fleeting-20250806-1520-bug-images-dissapear.md.md`
- **Issue**: `created: {{date:YYYY-MM-DD HH:mm}}` not processing to actual timestamp
- **Impact**: Template automation broken, blocking Reading Intake Pipeline development
- **Priority**: MUST BE RESOLVED FIRST before any new feature work
- **Workflow**: Use `/bug-triage-workflow` for systematic resolution

### **🔴 SYSTEM INTEGRITY: Image Linking System**
- **Issue**: Images disappear during AI automation processes
- **Impact**: Knowledge graph integrity, media asset management compromised
- **Areas Affected**: AI enhancement, note promotion, template processing
- **Investigation**: System design issue requiring comprehensive solution

### **📋 Active Project: Reading Intake Pipeline**
- **Status**: Phase 5 extension (not standalone project)
- **Dependency**: BLOCKED by template processing bug
- **Integration**: Leverages existing AI workflows (quality scoring, tagging, weekly review)
- **Timeline**: Sprint 0 (Aug 11-15), MVP (Aug 18), Full System (Aug 29)
- **Workflow**: Use `/reading-intake-pipeline` and `/integration-project-workflow`

## 📁 File Organization Rules

### **Markdown Files**
**Requirements:**
- All new notes must start in `Inbox/` with `status: inbox`
- YAML frontmatter is required for all notes
- Use kebab-case for filenames (e.g., `my-note-title.md`)
- Include created timestamp in ISO format (YYYY-MM-DD HH:mm)

### **Metadata Schema (Extended for Reading Intake Pipeline)**
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

### **Directory Structure**
| **Stage** | **Directory** | **Status Values** | **AI Features** |
|-----------|---------------|-------------------|-----------------|
| **Capture** | `Inbox/` | `status: inbox` | Auto-tagging, quality assessment, import processing |
| **Process** | `Fleeting Notes/` | `inbox → promoted` | Semantic analysis, connection discovery |
| **Literature** | `Literature Notes/` | `promoted → published` | Claims extraction, quote analysis, source linking |
| **Permanent** | `Permanent Notes/` | `draft → published` | Summarization, link prediction, gap analysis |
| **Archive** | `Archive/` | `archived` | Compression, backup, historical analysis |
| **Templates** | `Templates/` | N/A | Dynamic content generation, Templater scripts |

### **Templates (Enhanced)**
**Current Templates:**
- `fleeting.md` - Quick capture (REQUIRES FIX for timestamp processing)
- `permanent.md` - Structured permanent notes
- `literature-note.md` - NEW: For imported articles/books with claims/quotes
- `saved-article.md` - NEW: For Reading Intake Pipeline processing

**Requirements:**
- Include workflow guidance comments in all templates
- Use Templater syntax for dynamic content generation
- Never modify templates without testing timestamp generation
- All templates must work with AI workflow integration

## 🤖 AI Integration Guidelines (Current State)

### **Phase 5 AI Capabilities (COMPLETED)**
- ✅ **Smart Tagging**: Context-aware auto-tagging (3-8 tags/note)
- ✅ **Quality Scoring**: 0-1 scale with actionable feedback
- ✅ **Summarization**: Both abstractive (AI) and extractive methods
- ✅ **Connection Discovery**: Semantic similarity + link suggestions
- ✅ **Weekly Review**: Automated promotion candidates with rationale
- ✅ **Analytics Dashboard**: Temporal analysis, productivity metrics
- ✅ **Enhanced Metrics**: Orphaned/stale note detection

### **Phase 5 Extensions (IN DEVELOPMENT)**
- 🔄 **Reading Intake Pipeline**: Literature note workflow automation
- 🔄 **Template System Enhancement**: Improved reliability and new templates
- 🔄 **Import Adapters**: CSV/JSON, bookmarks, Twitter, YouTube, RSS

### **AI Usage Patterns**
```bash
# Core analytics and insights
python3 src/cli/analytics_demo.py . --interactive

# Weekly review automation  
python3 src/cli/workflow_demo.py . --weekly-review

# Enhanced metrics with orphaned/stale detection
python3 src/cli/workflow_demo.py . --enhanced-metrics

# Connection discovery
python3 src/cli/connections_demo.py .

# System health check (verify before development)
python3 src/cli/workflow_demo.py . --status

# NEW: Reading Intake Pipeline (once template bug fixed)
# python3 src/cli/workflow_demo.py . --import-bookmarks file.html
# python3 src/cli/workflow_demo.py . --process-literature
```

### **AI Ethics & Transparency**
- **Augment, Don't Replace**: AI enhances human creativity
- **Explainable Decisions**: Every AI action includes rationale
- **User Override**: Always allow human correction
- **Progressive Disclosure**: Simple by default, powerful when needed
- **Integration Focus**: Leverage existing AI workflows rather than duplicating
- **Preserve human decision-making in note promotion**
- **Maintain metadata consistency in automated processes**
- **Log AI-assisted actions for transparency**

## 🔄 Workflow State Management

### **Note Lifecycle (Enhanced)**
```
Saved Article/Import → 
Inbox (status: inbox) → 
Literature Notes (promoted) OR Fleeting Notes (promoted) → 
Permanent Notes (published) → 
Archive (archived)
```

### **Reading Intake Integration**
- **Import Sources**: Bookmarks, RSS, Twitter, YouTube, articles
- **Processing Pipeline**: Import → Triage → Literature/Fleeting → Permanent
- **AI Enhancement**: Uses existing quality scoring, tagging, weekly review
- **Template Integration**: Specialized literature note templates
- **Performance Target**: <30 seconds per item triage

### **Inbox Processing Rules**
- `Inbox/` is staging area for all imports and quick captures
- Status field drives workflow, not folder location
- Only notes with `status: inbox` require active triage
- AI tagging, quality assessment, connection discovery applied during processing
- Literature notes require claims/quotes extraction for promotion
- Reading intake items get source/url/saved_at metadata

## 🏗️ Development Guidelines

### **Critical Path Management**
- **NEVER start new feature development while template processing bug exists**
- **Always run system health check before beginning work**
- **Integration projects must preserve existing functionality**
- **Phase extensions preferred over standalone replacements**

### **TDD Methodology**
- Red → Green → Refactor cycles for all new features
- Maintain 66/66 test coverage (current target)
- Real user data validation before production deployment
- Performance benchmarking against established targets
- Integration testing with existing AI workflows

### **Integration-First Development**
- **Extend vs. Replace**: Build on existing Phase 5 AI capabilities
- **Schema Compatibility**: New metadata fields extend existing ones
- **Workflow Preservation**: Existing CLI commands must remain functional
- **Performance Maintenance**: New features cannot degrade existing performance
- **Use workflows**: `/integration-project-workflow` for Phase extensions

### **Code Organization**
- **CLI Tools**: `src/cli/` - User-facing commands and demos
- **AI Engine**: `src/ai/` - Core AI processing and workflows
- **Tests**: `tests/` - Comprehensive unit and integration tests
- **Templates**: `Templates/` - Dynamic content generation (FIX REQUIRED)

### **Performance Targets**
- **Summarization**: <10s for 1000+ word documents ✅
- **Similarity Analysis**: <5s per comparison ✅
- **Weekly Review**: <5s for 100+ notes ✅
- **Connection Mapping**: <20s for full network analysis ✅
- **Enhanced Metrics**: <5s for 76+ note analysis ✅
- **Reading Intake**: <30s per item triage (TARGET)

## 🔗 Git Integration

### **Branch Strategy for Integration Projects**
- `reading-pipeline-integration-analysis` - Current branch for Reading Intake Pipeline
- `bug-fix/template-processing` - Recommended for critical template bug
- `integration/phase-5-extension` - For Phase extension work

### **Commit Standards**
- Include change rationale in commit messages
- Reference affected workflow components  
- Maintain backwards compatibility
- Document bug fixes with clear before/after
- Include integration impact assessment

## 📝 Content Standards

### **Literature Notes (NEW)**
- Must include source URL and saved_at timestamp
- Require minimum 2 claims or 1 substantial quote
- Link liberally to related permanent and fleeting notes
- Include summary for quick reference
- Use structured template with claims/quotes sections
- Quality score target: >0.7 for promotion to permanent

### **Permanent Notes**
- Should be atomic and evergreen
- Include minimum 2 relevant tags
- Link liberally using `[[double-brackets]]`
- Never delete without explicit user permission
- Quality score target: >0.7 for promotion
- Can be promoted from fleeting OR literature notes

### **Fleeting Notes**
- Capture raw ideas quickly
- Include promotion pathway in template
- Preserve original context and timestamp
- Status: inbox until processed
- Can be imported from external sources via Reading Intake Pipeline

### **MOCs (Maps of Content)**
- Serve as navigation hubs for related topics
- Update regularly as content grows
- Include both structural and contextual links
- Provide entry points to knowledge networks
- Include literature and reading intake notes in relevant MOCs

## 🎯 Current Development Priorities (August 2025)

### **🔴 CRITICAL PATH (This Week)**
1. **Fix Template Processing Bug**: Resolve `{{date:YYYY-MM-DD HH:mm}}` processing failure
   - **Priority**: BLOCKING - Must be resolved before any new feature work
   - **Impact**: Template automation, Reading Intake Pipeline, user workflow
   - **Workflow**: Use `/bug-triage-workflow` for systematic approach

2. **Image Linking System Resolution**: Address AI automation impact on image references
   - **Priority**: CRITICAL - System integrity issue
   - **Impact**: Knowledge graph, media management, AI workflow reliability
   - **Investigation**: System design analysis required

### **🟡 HIGH PRIORITY (Next Week)**
3. **Reading Intake Pipeline Foundation**: Begin Phase 5 extension development
   - **Dependency**: BLOCKED by template processing bug
   - **Approach**: Phase 5 extension leveraging existing AI workflows
   - **Workflow**: Use `/reading-intake-pipeline` and `/integration-project-workflow`

4. **Template System Enhancement**: Improve reliability and add literature templates
   - **Focus**: Robust timestamp processing, new literature note templates
   - **Integration**: Must work with Reading Intake Pipeline

### **🟢 MEDIUM PRIORITY (Later)**
5. **Phase 6 Preparation**: Multi-user collaboration foundation
   - **Depends**: Complete Phase 5 extensions first
   - **Components**: User authentication, REST API, real-time collaboration
   - **Timeline**: After Reading Intake Pipeline completion

## 📊 Success Metrics & Validation

### **Current Status (August 2025)**
- **Notes Processed**: 212+ notes, 50K+ words
- **Test Coverage**: 66/66 tests passing (maintain this target)
- **AI Adoption**: Growing percentage of AI-enhanced notes
- **Quality Range**: 0.75-0.85 for high-quality content
- **Performance**: All targets consistently exceeded

### **Quality Gates**
- All tests must pass before deployment
- Performance benchmarks must be met or exceeded
- User validation required for workflow changes
- Template functionality must be verified
- Integration compatibility must be maintained
- Documentation must be updated with every change

### **Reading Intake Pipeline Success Criteria**
- **Performance**: <30 seconds per item triage
- **Quality**: 70% Literature notes have 2+ links + 1 claim
- **Productivity**: 5+ Permanent notes promoted per week via reading intake
- **Error Rate**: <1% on importer jobs
- **Integration**: Zero disruption to existing AI workflows

## 🔧 Specialized Workflows

Your InnerOS system includes specialized workflows for common development scenarios:

### **Available Workflow Commands**
- `/reading-intake-pipeline` - Complete development workflow for Reading Intake Pipeline
- `/bug-triage-workflow` - Critical bug identification and triage methodology
- `/integration-project-workflow` - Phase extension project development approach
- `/tdd-git-workflow` - Test-driven development with Git best practices

### **When to Use Workflows**
- **Reading Intake Pipeline**: Any work on literature note automation or import systems
- **Bug Triage**: When encountering critical bugs that block development
- **Integration Project**: When extending existing phases rather than creating new ones
- **TDD Git**: For all development work requiring systematic test-first approach

---

## 📚 Integration Philosophy Summary

> **Remember**: These rules ensure AI assistance enhances rather than replaces human decision-making in knowledge management. Every rule serves the ultimate goal of creating an intelligent, user-centered knowledge amplification system that grows through integration rather than replacement.

**Key Principles:**
- **Integration over Replacement**: Extend Phase 5 capabilities rather than duplicating
- **Compatibility First**: Preserve all existing functionality during enhancements  
- **Critical Path Awareness**: Template processing bug blocks all template-dependent features
- **Performance Excellence**: Maintain established benchmarks while adding new capabilities
- **User-Centered Design**: AI augments human creativity and decision-making

---

**Rules Version**: 4.0 (Current Project State)  
**Last Updated**: 2025-08-10  
**Next Review**: 2025-09-10  
**Integration Status**: Includes Reading Intake Pipeline context, critical bug awareness, and Phase extension methodology
