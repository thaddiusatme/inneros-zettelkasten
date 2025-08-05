---
type: permanent
created: 2025-08-04 13:50
status: published
tags: [windsurf, rules, inneros, ai-workflow]
visibility: private
---

# InnerOS Windsurf Rules: AI-Enhanced Knowledge Management

> **Updated**: 2025-08-04  
> **Purpose**: Guide AI interactions for InnerOS Zettelkasten development  
> **Manifest**: See `Projects/inneros-manifest.md` for complete project context

## 🎯 Core Session Principles

### **Context-First Development**
**Required Reads (in order):**
1. **inneros-manifest.md** - Comprehensive project overview and architecture
2. **project-todo.md** - Current priorities and next development steps
3. **README.md** - Quick start and AI features documentation
4. **windsurf-project-changelog.md** - Detailed development history

**Session Actions:**
- Always ground actions in project context, schema, and requirements
- Summarize project goals, structure, and recent changes before proceeding
- If context docs are missing or outdated, prompt user to update
- Reference manifest for technical decisions and architecture guidance

### **Data Preservation & Ethics**
- Never overwrite or destructively edit notes unless explicitly instructed
- Always retain metadata and maintain complete audit trail
- Backup considerations before any structural changes
- Respect privacy and visibility tags at all times
- Preserve user decision-making in AI workflows

### **Workflow Compliance**
- Follow note promotion and triage flows as defined in templates and manifest
- Use Templater scripts and LLM/AI integration points as described in manifest
- Respect all privacy and visibility tags (private/shared/team/public)
- Maintain backward compatibility with existing workflows

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
required_fields:
  - "type: permanent | fleeting | literature | MOC"
  - "created: YYYY-MM-DD HH:mm"
  - "status: inbox | promoted | draft | published | archived"
  - "visibility: private | shared | team | public"

optional_fields:
  - "tags: [kebab-case, hierarchical]"
  - "linked_notes: [[note-name]]"
  - "quality_score: 0.0-1.0"
  - "ai_tags: [auto-generated, contextual]"
```

### **Directory Structure**
| **Stage** | **Directory** | **Purpose** | **AI Features** |
|-----------|---------------|-------------|-----------------|
| **Capture** | `Inbox/` | New note staging | Auto-tagging, quality assessment |
| **Process** | `Fleeting Notes/` | Quick ideas | Semantic analysis, connection discovery |
| **Permanent** | `Permanent Notes/` | Evergreen knowledge | Summarization, link prediction |
| **Archive** | `Archive/` | Historical content | Compression, backup analysis |
| **Templates** | `Templates/` | Dynamic creation | Templater scripts, workflow guidance |

## 🤖 AI Integration Guidelines

### **Current AI Capabilities (Phase 5)**
- **Smart Tagging**: Context-aware auto-tagging (3-8 tags/note)
- **Quality Scoring**: 0-1 scale with actionable feedback
- **Summarization**: Abstractive (AI) and extractive methods
- **Connection Discovery**: Semantic similarity + link suggestions
- **Weekly Review**: Automated promotion candidates with rationale
- **Analytics Dashboard**: Temporal analysis, productivity metrics

### **AI Usage Patterns**
```bash
# Analytics and insights
python3 src/cli/analytics_demo.py . --interactive

# Weekly review automation
python3 src/cli/workflow_demo.py . --weekly-review

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

## 🔄 Workflow State Management

### **Note Lifecycle**
```
Inbox (status: inbox) → 
Fleeting Notes (promoted) → 
Permanent Notes (published) → 
Archive (archived)
```

### **Triage Rules**
- Only notes with `status: inbox` require active triage
- Fleeting notes → `Fleeting Notes/` folder
- Permanent notes → `Permanent Notes/` folder
- Reference/actionable → appropriate specialized folder
- Maintain audit trail of all movements

### **AI Workflow Integration**
- **Inbox Processing**: AI tagging, quality assessment, connection discovery
- **Promotion Decisions**: AI recommendations with confidence scores
- **Weekly Review**: Automated candidate identification with rationale
- **Quality Monitoring**: Continuous assessment and improvement suggestions

## 🛠️ Development Guidelines

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

## 🔐 Privacy & Security

### **Privacy by Design**
- **Local AI Only**: All processing on-device, no cloud dependencies
- **Encryption Ready**: Architecture supports encrypted storage
- **User Control**: Explicit sharing, granular permissions
- **Audit Trail**: Complete change history with rollback capability

### **Data Portability**
- **Export Formats**: JSON, Markdown, CSV
- **Import Formats**: Markdown, plain text, Obsidian vaults
- **Migration**: Schema evolution with backward compatibility

## 📊 Validation Rules

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

## 🚀 Next Development Focus

### **Immediate Priorities**
1. **Fix Test Suite**: Resolve 13 failing tests (Phase 6 blocker)
2. **Complete Phase 5.5**: Finalize weekly review integration
3. **Web UI Prototype**: Basic Flask/FastAPI dashboard

### **Phase 6 Preparation**
- User authentication and multi-user foundation
- REST API design for external integrations
- Real-time collaboration features
- Web interface for analytics and management

---

> **Remember**: These rules ensure AI assistance enhances rather than replaces human decision-making in knowledge management.

**Rules Version**: 2.1  
**Last Updated**: 2025-08-04  
**Next Review**: 2025-09-04
