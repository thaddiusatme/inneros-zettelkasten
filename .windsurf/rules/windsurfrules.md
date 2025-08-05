---
trigger: always_on
type: permanent
created: 2025-08-04 14:58
status: published
tags: [windsurf, rules, inneros, ai-workflow, unified]
visibility: private
---

# InnerOS Windsurf Rules: Unified AI-Enhanced Knowledge Management

> **Version**: 3.0 (Unified)  
> **Updated**: 2025-08-04  
> **Purpose**: Complete guide for AI interactions in InnerOS Zettelkasten development  
> **Manifest**: See `Projects/inneros-manifest.md` for comprehensive project context

## 🎯 Core Session Principles

### **Context-First Development**
**Required Reads (Priority Order):**
1. **Projects/inneros-manifest.md** - Comprehensive project overview and architecture
2. **Projects/project-todo.md** - Current priorities and next development steps  
3. **README.md** - Quick start and AI features documentation
4. **Projects/windsurf-project-changelog.md** - Detailed development history

**Session Actions:**
- Always ground actions in project context, schema, and requirements
- Summarize project goals, structure, and recent changes before proceeding
- If context docs are missing or outdated, prompt user to update
- Reference manifest for technical decisions and architecture guidance
- When in doubt, consult Manifest and Changelog before asking user

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

## 📁 File Organization Rules

### **Markdown Files**
**Pattern**: `**/*.md`

**Requirements:**
- All new notes must start in `Inbox/` with `status: inbox`
- YAML frontmatter is required for all notes
- Use kebab-case for filenames (e.g., `my-note-title.md`)
- Include created timestamp in ISO format (YYYY-MM-DD HH:mm)

**Metadata Schema:**
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
```

### **Directory Structure**
| **Stage** | **Directory** | **Status Values** | **AI Features** |
|-----------|---------------|-------------------|-----------------|
| **Capture** | `Inbox/` | `status: inbox` | Auto-tagging, quality assessment |
| **Process** | `Fleeting Notes/` | `inbox → promoted` | Semantic analysis, connection discovery |
| **Permanent** | `Permanent Notes/` | `draft → published` | Summarization, link prediction, gap analysis |
| **Archive** | `Archive/` | `archived` | Compression, backup, historical analysis |
| **Templates** | `Templates/` | N/A | Dynamic content generation, Templater scripts |

### **Templates**
**Pattern**: `Templates/**`
**Requirements:**
- Include workflow guidance comments in all templates
- Use Templater syntax for dynamic content generation
- Template names should match note types (fleeting.md, permanent.md)
- Never modify templates without updating Changelog

## 🤖 AI Integration Guidelines

### **Current AI Capabilities (Phase 5 Complete)**
- ✅ **Smart Tagging**: Context-aware auto-tagging (3-8 tags/note)
- ✅ **Quality Scoring**: 0-1 scale with actionable feedback
- ✅ **Summarization**: Both abstractive (AI) and extractive methods
- ✅ **Connection Discovery**: Semantic similarity + link suggestions
- ✅ **Weekly Review**: Automated promotion candidates with rationale
- ✅ **Analytics Dashboard**: Temporal analysis, productivity metrics
- ✅ **Enhanced Metrics**: Orphaned/stale note detection

### **AI Usage Patterns**
```bash
# Analytics and insights
python3 src/cli/analytics_demo.py . --interactive

# Weekly review automation  
python3 src/cli/workflow_demo.py . --weekly-review

# Enhanced metrics with orphaned/stale detection
python3 src/cli/workflow_demo.py . --enhanced-metrics

# Connection discovery
python3 src/cli/connections_demo.py .

# System health check
python3 src/cli/workflow_demo.py . --status
```

### **AI Ethics & Transparency**
- **Augment, Don't Replace**: AI enhances human creativity
- **Explainable Decisions**: Every AI action includes rationale
- **User Override**: Always allow human correction
- **Progressive Disclosure**: Simple by default, powerful when needed
- **Use LLM integration points as defined in Manifest**
- **Preserve human decision-making in note promotion**
- **Maintain metadata consistency in automated processes**
- **Log AI-assisted actions for transparency**

## 🔄 Workflow State Management

### **Note Lifecycle**
```
Inbox (status: inbox) → 
Fleeting Notes (promoted) → 
Permanent Notes (published) → 
Archive (archived)
```

### **Inbox Processing Rules**
- `Inbox/` is staging area only - notes move to permanent folders after triage
- Status field drives workflow, not folder location
- Only notes with `status: inbox` require active triage
- AI tagging, quality assessment, connection discovery applied during processing

### **Note Progression Standards**
**States**: `inbox → promoted → draft → published → archived`
**Validation Requirements:**
- Status transitions must be logged
- Metadata must be preserved during moves
- Links must be updated when notes relocate
- Maintain audit trail of all movements

### **Triage Rules**
- Fleeting notes → `Fleeting Notes/` folder
- Permanent notes → `Permanent Notes/` folder
- Reference/actionable → appropriate specialized folder
- MOCs → maintain in root or appropriate category folders

### **AI Workflow Integration**
- **Inbox Processing**: AI tagging, quality assessment, connection discovery
- **Promotion Decisions**: AI recommendations with confidence scores  
- **Weekly Review**: Automated candidate identification with rationale
- **Quality Monitoring**: Continuous assessment and improvement suggestions

## 🏗️ Development Guidelines

### **TDD Methodology**
- Red → Green → Refactor cycles for all new features
- Maintain 100% test coverage for critical paths
- Real user data validation before production deployment
- Performance benchmarking against established targets

### **Code Organization**
- **CLI Tools**: `src/cli/` - User-facing commands and demos
- **AI Engine**: `src/ai/` - Core AI processing and workflows
- **Tests**: `tests/` - Comprehensive unit and integration tests
- **Templates**: `Templates/` - Dynamic content generation

### **Performance Targets**
- **Summarization**: <10s for 1000+ word documents
- **Similarity Analysis**: <5s per comparison
- **Weekly Review**: <5s for 100+ notes
- **Connection Mapping**: <20s for full network analysis
- **Enhanced Metrics**: <5s for 76+ note analysis

## 🔗 Git Integration

### **Pre-Commit Hooks**
- Validate YAML frontmatter integrity
- Check required metadata fields
- Verify link consistency

### **Post-Commit Hooks**
- Auto-update Windsurf Project Changelog.md
- Preserve user notification requirements

### **Commit Standards**
- Include change rationale in commit messages
- Reference affected workflow components  
- Maintain backwards compatibility

## 🎯 Naming Conventions

### **File & Directory Standards**
- **Files**: kebab-case (e.g., `my-note-title.md`)
- **Folders**: Title Case (e.g., `Permanent Notes`)
- **Tags**: lowercase, hyphenated (e.g., `note-taking`, `ai-workflow`)
- **Timestamps**: ISO format (YYYY-MM-DD HH:mm)

## 📝 Content Standards

### **Permanent Notes**
- Should be atomic and evergreen
- Include minimum 2 relevant tags
- Link liberally using `[[double-brackets]]`
- Never delete without explicit user permission
- Quality score target: >0.7 for promotion

### **Fleeting Notes**
- Capture raw ideas quickly
- Include promotion pathway in template
- Preserve original context and timestamp
- Status: inbox until processed

### **Literature Notes**
- Reference source material with citations
- Extract key insights and connections
- Link to related permanent notes
- Include summary for quick reference

### **MOCs (Maps of Content)**
- Serve as navigation hubs for related topics
- Update regularly as content grows
- Include both structural and contextual links
- Provide entry points to knowledge networks

## 🔐 Privacy & Security

### **Privacy by Design**
- **Local AI Only**: All processing on-device, no cloud dependencies
- **Encryption Ready**: Architecture supports encrypted storage
- **User Control**: Explicit sharing, granular permissions
- **Audit Trail**: Complete change history with rollback capability

### **Default Settings**
- All notes default to `visibility: private`
- Respect existing visibility settings
- Future-proof for multi-user scenarios

### **Data Portability**
- **Export Formats**: JSON, Markdown, CSV
- **Import Formats**: Markdown, plain text, Obsidian vaults
- **Migration**: Schema evolution with backward compatibility

### **Compliance Requirements**
- Maintain audit trail for visibility changes
- Document any privacy-related modifications in Changelog

## 🔍 Validation Rules

### **Required on Creation**
- Valid YAML frontmatter with all required fields
- Proper status field (inbox|promoted|draft|published|archived)
- Valid type field (permanent|fleeting|literature|MOC)
- Created timestamp present in ISO format

### **Required on Modification**
- Preserve existing metadata unless explicitly changing
- Update modification timestamps
- Maintain link integrity
- Log changes in appropriate tracking mechanisms

## 🚨 Error Handling & Recovery

### **Error Prevention**
- Always confirm destructive actions with user
- Provide rollback options for structural changes
- Log errors and recovery steps in Changelog
- Maintain system state consistency

### **Recovery Procedures**
- Backup validation before structural changes
- Rollback capabilities for all operations
- Error logging with actionable recovery steps
- System state validation and repair

## 🎯 Current Development Priorities

### **Immediate (This Week)**
1. **Fix Test Suite**: Resolve failing tests (Phase 6 blocker)
2. **Complete Phase 5.5**: Finalize weekly review integration
3. **Web UI Prototype**: Basic Flask/FastAPI dashboard

### **Phase 6 Preparation**
- User authentication and multi-user foundation
- REST API design for external integrations
- Real-time collaboration features
- Web interface for analytics and management

---

## 📊 Success Metrics & Validation

### **Current Status**
- **Notes Processed**: 212 notes, 50K+ words
- **Test Coverage**: Target 100% for critical paths
- **AI Adoption**: Growing percentage of AI-enhanced notes
- **Quality Range**: 0.75-0.85 for high-quality content
- **Performance**: All targets consistently exceeded

### **Quality Gates**
- All tests must pass before deployment
- Performance benchmarks must be met
- User validation required for workflow changes
- Documentation must be updated with every change

---

> **Remember**: These rules ensure AI assistance enhances rather than replaces human decision-making in knowledge management. Every rule serves the ultimate goal of creating an intelligent, user-centered knowledge amplification system.

**Rules Version**: 3.0 (Unified)  
**Last Updated**: 2025-08-04  
**Next Review**: 2025-09-04  
**Integration Status**: Consolidates `.windsurf/rules/ruleset.md` + `.windsurf/rules/windsurfrules.md`
