# InnerOS Zettelkasten – Project Manifest v2.0

> DEPRECATED — superseded by `Projects/inneros-manifest-v3.md` (2025-09-18).  
> Please use the v3 manifest for current state and priorities.

**Owner**: Thaddius • Assistant: Cascade  
**Source of Truth**: `.windsurf/windsurfrules.md` (v3.0)

---

## 🎯 Vision & Purpose

InnerOS Zettelkasten is a **local-first, AI-augmented knowledge system** that preserves human decision-making while automating analysis, triage, and connectivity discovery. This system transforms isolated note-taking into an intelligent network that learns, connects, and surfaces insights automatically.

**Core Promise**: "Capture any thought in under 15 seconds, and let AI transform it into connected knowledge that compounds over time."

---

## 🏗️ Current Architecture Status

### **Knowledge Graph Analysis (2025-08-10)**
- **Strong Foundation**: Healthy "hub + clusters" structure with effective MOCs (AI/Prompting, Projects, Concepts, Books, Career & Entrepreneurship)
- **Core Density**: Reasonably dense center with strong workflow/AI backbone connecting engineering/TDD with prompting practice
- **Identified Gaps**: Peripheral singletons, weak bridges between key domains, isolated mini-clusters need integration

### **Technology Stack**
- **AI Engine**: Ollama (Llama 3.1 8B) with semantic embeddings
- **Storage**: Markdown + YAML frontmatter (schema-validated)
- **Processing**: Python 3.9+ with async capabilities, 66/66 tests passing
- **Interface**: CLI (production) → Web Dashboard (Phase 6)
- **Analytics**: Network analysis, quality scoring (0-1 scale), temporal insights

---

## 🔗 Immediate Connectivity Improvement Plan

### **High-Priority Bridge Reinforcement**
1. **AI ↔ Pharmacy Bridge**: Strengthen "Perplexity AI Pharmacy Research" and "Pharmacy Scraper Classification Module" with explicit links to embeddings, scraping pipeline design, evaluation strategy
2. **AI/TDD ↔ Weekly Review Bridge**: Link "Weekly Review Manifest/Checklist" into TDD/automation cluster and back to MOCs
3. **Entrepreneurship ↔ AI Delivery Bridge**: Connect "Upwork as Revenue," "Freelancing Plan," Upwork videos to concrete deliverables (scrapers, dashboards, demos) and "Project – Pharmacy Scraper MOC"

### **Strategic Bridge Notes (Create New)**
- **"How AI Prompting Supports TDD and Weekly Review Automation"**: High-value conceptual hub linking AI methods to engineering workflows
- **"LLM Outage Handling Pattern"** and **"Voice-to-Clarity Workflow Pattern"**: Lightweight pattern notes linking tools/experiments

### **Singleton Remediation (Immediate)**
- **Peripheral Notes**: "Pasted image…," "Support SOP System Map," dated diary-style notes need upward (MOC) and lateral links
- **Mini-Clusters**: Claude News Bot/Carousel, voice/prompting utilities need integration into AI & Prompting MOC with "Tools in Practice" section
- **Progress Snapshots**: Convert single-linked dated progress notes into bidirectional connections

### **Cross-MOC Navigation Enhancement**
- Projects MOC → AI and Prompting MOC (methods used per project)
- Career & Entrepreneurship MOC ↔ Projects MOC (portfolio artifacts bidirectional)
- Add "What to do next" sections in every MOC linking to open tasks/TODOs

---

## 🤖 AI Capabilities (Phase 5 Complete)

### **Production Features**
- ✅ **Smart Tagging**: Context-aware auto-tagging (3-8 tags/note), kebab-case
- ✅ **Quality Scoring**: 0-1 scale with actionable feedback
- ✅ **Summarization**: Abstractive (AI) + extractive methods, YAML-aware
- ✅ **Connection Discovery**: Embedding-based similarity, link suggestions
- ✅ **Weekly Review**: Automated candidate identification with rationale
- ✅ **Enhanced Metrics**: Orphaned/stale detection, link density, productivity insights

### **Performance Benchmarks (Validated)**
- **Summarization**: <10s for 1000+ word documents
- **Similarity Analysis**: <5s per comparison
- **Weekly Review**: <5s for 100+ notes
- **Enhanced Metrics**: <5s for 76+ note analysis
- **Connection Mapping**: <20s for full network analysis

### **Key CLI Commands**
```bash
# Analytics dashboard
python3 src/cli/analytics_demo.py . --interactive

# Workflow management
python3 src/cli/workflow_demo.py . --status | --process-inbox | --weekly-review | --enhanced-metrics

# Connection discovery
python3 src/cli/connections_demo.py .

# Validation tools
python3 src/cli/workflow_demo.py . --enhanced-metrics
python3 src/cli/connections_demo.py .
python3 src/cli/workflow_demo.py . --weekly-review --export-checklist weekly-review.md
```

---

## 📁 Information Architecture

### **Directory Workflow**
| **Stage** | **Directory** | **Status** | **AI Features** |
|-----------|---------------|------------|-----------------|
| **Capture** | `Inbox/` | `status: inbox` | Auto-tagging, quality assessment |
| **Process** | `Fleeting Notes/` | `inbox → promoted` | Semantic analysis, connection discovery |
| **Permanent** | `Permanent Notes/` | `draft → published` | Summarization, link prediction |
| **Archive** | `Archive/` | `archived` | Compression, historical analysis |

#### Templates (Obsidian Templater)
- `knowledge/Templates/fleeting.md` — quick capture with automated rename/move.
- `knowledge/Templates/permanent.md` — structured permanent notes.
- `knowledge/Templates/literature.md` — literature/reference notes.
- `knowledge/Templates/daily.md`, `weekly-review.md`, `sprint-review.md`, `sprint-retro.md` — rituals.
- `knowledge/Templates/chatgpt-prompt.md` — Single-prompt ChatGPT prompt note generator.

Usage:
- Requires Obsidian Templater. EJS syntax is used (e.g., `<% tp.date.now("YYYY-MM-DD HH:mm") %>`).
- Prompts once for a feature/branch name, then renames file to `Inbox/prompt-YYYYMMDD-HHmm.md`.
- Starts with `type: fleeting`, `status: inbox`; tags include `prompt, chatgpt, inbox`.

### **YAML Schema (Required)**
```yaml
type: permanent | fleeting | literature | MOC
created: YYYY-MM-DD HH:mm
status: inbox | promoted | draft | published | archived
visibility: private | shared | team | public
tags: [kebab-case, hierarchical]
linked_notes: [[note-name]]
quality_score: 0.0-1.0  # AI-generated
ai_tags: [auto-generated, contextual]
```

### **MOC Strategy**
- **Central Hubs**: AI/Prompting, Concepts, Projects, Books, Career & Entrepreneurship
- **Navigation**: Cross-MOC bidirectional linking with relationship descriptors
- **Action Orientation**: "What to do next" sections linking to tasks/TODOs

---

## 📚 Reading Intake Pipeline - Phase 5 Extension (Immediate)

> **Integration Status**: Critical gaps identified with original proposal  
> **Approach**: Extend existing Phase 5 AI workflows rather than create parallel systems  
> **Reference**: `Projects/reading-intake-integration-analysis.md`

### **Strategic Positioning**
Transform the Reading Intake Pipeline from a standalone project into a **Phase 5 AI workflow extension** that leverages our existing $50K investment in quality scoring, smart tagging, connection discovery, and weekly review automation.

### **Integration Goals**
- **Schema Compatibility**: Extend existing YAML frontmatter with `source:` field
- **AI Leverage**: Use existing quality scoring (0-1 scale) and smart tagging systems
- **Workflow Integration**: Extend existing 5-state lifecycle (inbox→promoted→draft→published→archived)
- **CLI Extension**: Add import commands to existing `workflow_demo.py`
- **Template Alignment**: Use fixed template processing with InnerOS naming conventions

### **Technical Implementation (Aligned)**
```yaml
# Compatible Schema Extension
---
type: fleeting                    # Existing field
created: 2025-08-10 12:00        # Existing field (fixed template bug)
status: inbox                    # Existing workflow state
source:                          # NEW - Reading Pipeline extension
  url: "https://example.com/post"
  title: "Article Title"
  author: "Author Name"
  published_at: "2025-08-07"
  duration: 540
tags: [ai, workflows]            # Existing field
visibility: private              # Existing field
quality_score: 0.0              # Existing AI feature
ai_tags: []                      # Existing AI feature
---
```

### **Critical Path Dependencies**
1. **Template Processing Bug Fix**: Must resolve `{{date}}` syntax failure before implementation
2. **Schema Validation Extension**: Add `source:` field validation to existing systems
3. **AI Workflow Integration**: Ensure import process uses existing quality scoring and tagging

### **Implementation Timeline (Revised)**
- **Week 1** (Aug 11-15): Template bug fix + schema alignment + compatible templates
- **Week 2** (Aug 18-22): Import adapters extending WorkflowManager + CLI integration
- **Week 3** (Aug 25-29): Literature templates + weekly review integration + full testing

### **Success Criteria**
- **All 66/66 tests remain passing** after integration
- **Leverages existing AI capabilities** (no parallel systems)
- **Maintains .windsurfrules.md compliance** (kebab-case naming)
- **Performance**: <30 seconds per item using existing AI processing

---

## 🚀 Phase 6 Roadmap (Multi-User & UI)

### **6.1 Multi-User Foundations**
- Authentication scaffolding, user identity model (local-first)
- Visibility/Audit extensions: per-user actions, share states
- Team workflows: collaborative inbox processing, review queues

### **6.2 API & Integrations**
- Read-only REST API for analytics and note metadata
- Mutation endpoints behind role/visibility checks (opt-in)
- Webhooks/local events for status transitions

### **6.3 Advanced Visualization**
- Interactive knowledge graph (local web UI) with community detection
- Network metrics surfacing (degree, betweenness, clustering)
- Visual exploration tools and report exports

### **6.4 Web UI (Analytics Dashboard)**
- Health dashboards: orphaned/stale, AI adoption, productivity
- Customizable reports; export as Markdown/PDF
- Web interface for weekly review checklist

---

## 🔐 Ethics, Privacy & Governance

### **Privacy by Design**
- **Local AI Only**: All processing on-device; no external transmission without explicit opt-in
- **Non-destructive**: AI augments, never overwrites without approval
- **Visibility Respect**: Tags honored in all automation; logged transitions
- **Explainability**: Every AI recommendation includes rationale and confidence

### **TDD & Quality Assurance**
- Red → Green → Refactor required for new features
- Pre-commit hooks validate YAML and links
- All structural/template changes require README + Changelog updates
- Rollback plans for migrations; never destructive without confirmation

---

## 📊 Success Metrics & Current Status

### **Phase 5 Achievements (2025-08-10)**
- **Notes Processed**: 212 notes, 50K+ words successfully validated
- **Test Coverage**: 66/66 tests passing, production-ready AI features
- **Performance**: All targets exceeded consistently
- **Quality Range**: 0.75-0.85 for high-quality promoted content

### **Connectivity Targets (Next 2 Weeks)**
- Reduce orphaned notes by ≥50%
- Increase average links/note by +1
- Strengthen 3 key bridges (AI↔Pharmacy, AI/TDD↔Weekly Review, Entrepreneurship↔Artifacts)
- Create 2 strategic bridge notes
- Integrate 5+ singleton notes into main network

### **Phase 6 Goals**
- Support 5+ concurrent users
- Real-time collaboration without conflicts
- Interactive knowledge graph exploration
- Comprehensive permission system

---

## 🔄 Operations & Rituals

### **Daily**
- Triage `Inbox/`, process fleeting → permanent
- Run `--process-inbox` and health check
- Quick analytics validation

### **Weekly** 
- Run `--weekly-review`, act on checklist, export results
- Connection discovery sweep: `python3 src/cli/connections_demo.py .`
- Update sprint priorities based on insights

### **Monthly**
- Validate rules/template compliance
- Audit transitions, update README & Changelog
- Review and update this Manifest (Decision Log)
- Assess connectivity improvements and network health

---

## 🎯 Immediate Actions (Next Session)

### **🔴 Critical - Knowledge Graph Enhancement**
1. Create bridge note: "How AI Prompting Supports TDD and Weekly Review Automation"
2. Reinforce AI↔Pharmacy links (add 2 explicit connections)
3. Link Entrepreneurship/Freelancing notes to concrete deliverables

### **🟡 High Impact - Infrastructure**
1. Add "AI Tools Index" under AI & Prompting MOC
2. Convert 3-5 peripheral singletons to well-connected notes
3. Add "What to do next" sections to all MOCs

### **🟢 Strategic - Documentation**
1. Link this manifest from README.md and Home Note
2. Run enhanced metrics and connection discovery for validation
3. Export weekly review checklist for connectivity action items

---

## 🛠️ Technical Dependencies

### **Current Stack**
- Python 3.9+, Ollama (Llama 3.1 8B)
- Optional: matplotlib, networkx, watchdog (graceful fallbacks)
- Tests: pytest with comprehensive coverage

### **Phase 6 Requirements**
- Web framework: Flask/FastAPI/Django (TBD)
- Database: Multi-user data storage (TBD) 
- Frontend: React/Vue/Svelte (TBD)

---

## 📝 Decision Log (Newest First)

- **2025-08-20**: Implemented engine-level mitigation for template 'created' placeholder via raw-frontmatter preprocessing in `WorkflowManager.process_inbox_note()`; added comprehensive unit tests for placeholder patterns and dry-run no-write behavior; hardened `AIEnhancer.suggest_improved_structure()` to validate LLM responses and fall back deterministically.
- **2025-08-10**: Created v2.0 Manifest with knowledge graph analysis integration; set immediate connectivity improvement targets and Phase 6 scaffolding priorities
- **2025-08-04**: Established v1.0 Manifest aligned with unified rules; completed Phase 5 technical foundation

---

> **Remember**: This system amplifies human knowledge work through AI augmentation while preserving human decision-making and creative control. Every improvement serves the goal of creating connected, discoverable, and actionable knowledge networks.

**Manifest Version**: 2.0  
**Next Review**: 2025-09-10  
**Status**: Production Ready → Connectivity Enhancement Phase
