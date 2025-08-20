# InnerOS Zettelkasten - Project Todo v2.0
 
**Last Updated**: 2025-08-20 16:32 PDT  
**Status**: Phase 5 Complete → Knowledge Graph Enhancement & Phase 6 Prep  
**Reference**: `Projects/inneros-manifest-v2.md` for comprehensive context
 
> **Latest Progress**: Phase 5 AI features **PRODUCTION READY** ✅. Knowledge graph analysis complete with specific connectivity improvement plan. Focus shifts to network enhancement and Phase 6 multi-user foundations.
 
---
 
## 🎯 Current Sprint: Knowledge Graph Enhancement + Bug Fixes

#### ✅ Completed (2025-08-20)
- Engine-level mitigation for template 'created' placeholder in `WorkflowManager.process_inbox_note()` (raw-frontmatter preprocessing)
- Unit tests added for placeholder patterns (`{{date}}`, EJS) and strict dry-run no-write behavior (fast + AI paths)
- Branch pushed: `fix/template-placeholders-content-pipeline`
- Docs updated: `Projects/inneros-manifest-v2.md` decision log, `Projects/project-todo-v2.md` Bug 1 status

### 🔴 Critical - Bug Fixes & System Issues (Immediate)
 
#### Bug 1: YAML `created` Property Not Processing 🔴 **BLOCKING TEMPLATE FUNCTIONALITY**
- [ ] **Investigate Templater `{{date}}` Processing Failure**
  - **File**: `knowledge/Inbox/fleeting-20250806-1520-bug-images-dissapear.md.md`
  - **Issue**: Line 3 shows `created: {{date:YYYY-MM-DD HH:mm}}` instead of actual timestamp
  - **Expected**: `created: 2025-08-06 15:20` format
  - **Impact**: Template automation broken, metadata inconsistent

- [x] **Mitigation Implemented (Engine-Level)**: Preprocess 'created' placeholders in raw frontmatter within `WorkflowManager.process_inbox_note()` to ensure parseable YAML and ISO timestamp normalization (non-destructive; respects dry-run)

- [x] **Unit Tests Added**: Comprehensive tests for placeholder patterns (`{{date}}`, EJS forms) and dry-run no-write behavior across fast/AI paths

- **Status Note**: Engine-level mitigation unblocks parsing reliability, but the Templater plugin fix remains required before template-based workflows are considered fully reliable.

- [ ] **Fix Template Processing Chain**
  - [ ] Verify Templater plugin is active and configured correctly
  - [ ] Test template processing with simple date generation
  - [ ] Update template syntax if Templater version changed
  - [ ] Add fallback date generation for template failures

- [ ] **Follow-up (Automation & CI)**: Enhance `.automation/scripts/repair_metadata.py` with placeholder repair, ISO normalization, `--dry-run`, backups, and changelog update
- [ ] **Follow-up (Validation)**: Add CI validator to fail on templater tokens in YAML across `knowledge/`

#### Bug 2: Image Reference/Linking System Design Issue 🔴 **SYSTEM INTEGRITY**
- [ ] **Investigate Image Handling in AI Automation**
  - **Issue**: "Images are referenced and link to each other seems to break on AI automation"
  - **Scope**: System design issue affecting image persistence and linking
  - **Impact**: Knowledge graph integrity, media asset management
 
- [ ] **Diagnostic and Resolution Plan**
  - [ ] Audit current image storage pattern (`Media/` directory vs inline references)
  - [ ] Test image link preservation during AI processing workflows
  - [ ] Identify if issue is in AI enhancement, note promotion, or template processing
  - [ ] Design robust image reference system that survives automation
  - [ ] Create unit tests for image link integrity during AI workflows
 
#### Bug 3: Malformed Tag Parsing and Metadata Anomalies 🔴 **DATA QUALITY**
- [ ] **Quantify Scope**: Run validator/scan on `knowledge/Inbox/` and `knowledge/Fleeting Notes/` to find malformed tags
  - [x] Centralize sanitization: Implement `sanitize_tags()` (used by weekly review flow)
  - [ ] Integrate sanitization into `WorkflowManager.process_inbox_note()`
  - [ ] **Harden Repair Script**: Update `.automation/scripts/repair_metadata.py` to normalize tags and scrub malformed YAML keys
  - [ ] **Add Tests**: Sanitizer edge cases, repair transforms, CLI weekly-review output validation
  - [ ] **Dry-Run Repair**: Execute repair in dry-run mode with report; review findings
  - [ ] **Apply Repair Safely**: Run with backups enabled; verify changes
  - [x] **Verify Weekly Review**: Re-run weekly review `--dry-run` to confirm clean tags and fast-mode behavior
  - Note: Numeric-only tags policy pending decision
 
#### Template System Enhancement 🟡 **HIGH IMPACT**
- [ ] **Expand Template Library**
  - [ ] Audit current templates for reliability and coverage gaps
  - [ ] Design templates for new Reading Intake Pipeline project
  - [ ] Add specialized templates for literature notes with claims/quotes
  - [ ] Create import adapter templates for CSV/JSON processing
  - [ ] Ensure all templates use reliable date/time generation

### 📚 Reading Intake Pipeline - Phase 5 Extension

> ⚠️ INTEGRATION APPROACH UPDATED  
> **Reference**: `Projects/reading-intake-integration-analysis.md`  
> **Status**: Critical gaps identified in original proposal → Integrated approach adopted

#### **🔴 Critical Path Dependencies (Must Fix First)**
- [ ] **Template Processing Bug**: Fix `{{date:YYYY-MM-DD HH:mm}}` syntax failure
  - **Blocking Issue**: Same syntax proposed in Reading Pipeline templates
  - **File**: `knowledge/Inbox/fleeting-20250806-1520-bug-images-dissapear.md.md`
  - **Impact**: All new template work blocked until resolved

- [ ] **Image Reference System**: Resolve design issue breaking during AI automation
  - **Scope**: System integrity issue affecting knowledge graph
  - **Priority**: Critical for media asset management

- [ ] **Schema Integration**: Extend existing YAML validation for new `source:` field
  - **Approach**: Compatible extension, not replacement
  - **Test Coverage**: Maintain all 66/66 tests passing

#### **Phase 1: Foundation Alignment (Week 1 - Aug 11-15)**
- [ ] **Metadata Schema Alignment**
  - [ ] Use existing fields: `type: fleeting`, `created:`, `status: inbox`
  - [ ] Add compatible `source:` field extension (not `note_type:`)
  - [ ] Maintain existing AI fields: `quality_score`, `ai_tags`
  - [ ] Test schema changes with existing AI workflows

- [ ] **File Naming Compliance**
  - [ ] Use kebab-case: `fleeting-20250810-1200-article-slug.md`
  - [ ] NOT: `FN {date} {slug}.md` (violates .windsurfrules.md)
  - [ ] Align with existing directory structure expectations

- [ ] **Template Creation**
  - [ ] Fix core template processing first
  - [ ] Create `Templates/fleeting-reading.md` (compatible)
  - [ ] Create `Templates/literature.md` with claims/quotes
  - [ ] Test with real date generation (not placeholder)

#### **Phase 2: AI Workflow Integration (Week 2 - Aug 18-22)**
- [ ] **Import System Design**
  - [ ] Create `ReadingIntakeManager` extending existing `WorkflowManager`
  - [ ] Leverage existing quality scoring (0-1 scale) during import
  - [ ] Use existing smart tagging system for imported content
  - [ ] Integrate with existing connection discovery

- [ ] **CLI Extension**
  - [ ] Add flags to existing `workflow_demo.py`: `--import-reading`, `--upgrade-literature`
  - [ ] NOT separate CLI tool - extend existing system
  - [ ] Include in existing weekly review automation
  - [ ] Maintain performance: <30 seconds per item

#### **Phase 3: Advanced Features (Week 3 - Aug 25-29)**
- [ ] **Literature Note Enhancement**
  - [ ] Create compatible templates with claims/quotes sections
  - [ ] Quality thresholds using existing scoring system (>0.7 for promotion)
  - [ ] Bidirectional linking integration
  - [ ] Connection to existing MOC strategy

- [ ] **Import Adapters**
  - [ ] CSV/JSON → compatible fleeting notes
  - [ ] Bookmarks HTML → structured source metadata
  - [ ] Social media formats → normalized schema
  - [ ] All integrated with existing AI processing

#### **🎯 Success Criteria (Revised)**
- **No Parallel Systems**: All features extend existing Phase 5 workflows
- **Test Coverage**: Maintain 66/66 tests passing throughout
- **AI Leverage**: Use existing $50K investment in quality scoring, tagging, weekly review
- **Compliance**: Follows .windsurfrules.md and existing YAML schema
- **Performance**: <30 seconds per item using existing AI infrastructure

### **🔴 Critical - Network Connectivity (Next 1-2 Weeks)**

#### **High-Priority Bridge Reinforcement**
- [ ] **AI ↔ Pharmacy Bridge** 🟡 **DEPRIORITIZED (parking lot)**
  - [ ] Add explicit link from "Perplexity AI Pharmacy Research" to embeddings strategy note
  - [ ] Connect "Pharmacy Scraper Classification Module" to evaluation methodology
  - [ ] Link scraping pipeline design notes to AI processing workflow
  - **Success Metric**: 2-3 bidirectional links established

- [ ] **AI/TDD ↔ Weekly Review Bridge** 🔴 **CRITICAL FOR WORKFLOW**
  - [ ] Link "Weekly Review Manifest/Checklist" to TDD/automation cluster
  - [ ] Connect Phase 5.5 features to MOC discovery workflow
  - [ ] Establish back-links to relevant MOCs for discoverability
  - **Success Metric**: Workflow integration complete

- [ ] **Entrepreneurship ↔ AI Delivery Bridge** 🔴 **CRITICAL FOR MONETIZATION**
  - [ ] Connect "Upwork as Revenue" to concrete demo artifacts
  - [ ] Link "Freelancing Plan" to scraper module and dashboard deliverables  
  - [ ] Connect Upwork strategy notes to "Project – Pharmacy Scraper MOC"
  - **Success Metric**: Portfolio artifacts clearly connected to strategy

#### **Strategic Bridge Notes (Create New)**
- [ ] **"How AI Prompting Supports TDD and Weekly Review Automation"** 🟡 **HIGH VALUE**
  - [ ] Document connection between AI methods and engineering workflows
  - [ ] Link to both AI/Prompting cluster and TDD/automation cluster
  - [ ] Include concrete examples from Phase 5 development
  - [ ] Position as high-value conceptual hub

- [ ] **"LLM Outage Handling Pattern"** 🟢 **STRATEGIC**
  - [ ] Document graceful fallback strategies from Phase 5 experience
  - [ ] Link to relevant tool notes and case studies
  - [ ] Include performance impact analysis

- [ ] **"Voice-to-Clarity Workflow Pattern"** 🟢 **STRATEGIC**
  - [ ] Document voice processing → note clarity pipeline
  - [ ] Link to AI tools and practical examples
  - [ ] Connect to productivity workflow notes

### **🟡 Orphaned Note Remediation Feature (Phase 5.5.6)**

- **Objective**: Make orphan detection and remediation a repeatable, CLI-driven workflow that excludes Content Pipeline/Idea Backlog notes and validates impact via metrics.

- **Success Criteria**:
  - [ ] ≥50% reduction in orphaned notes (workflow scope) on first pass
  - [ ] <5s detection on 100+ notes
  - [ ] 0 content/idea notes included when exclusions are set

- **Deliverables**:
  - [ ] CLI: `--list-orphans`, `--remediate-orphans`, `--scope {workflow,comprehensive}`, `--exclude "<patterns>"`, `--format json`
  - [ ] WorkflowManager: `list_orphans(...)`, `remediate_orphans(...)`
  - [ ] Link editor utility: safe "See also" insertion + MOC backlinks
  - [ ] Remediation plan export (markdown)
  - [ ] Documentation updates: CLI-REFERENCE and SOP in `Workflows/sops-and-workflows.md`

- **Milestones (5–7 days)**:
  - [ ] Day 1: Requirements + test scaffolding
  - [ ] Day 2: Detection packaging (`--list-orphans`, `--scope`, `--exclude`) + unit tests
  - [ ] Day 3: Plan formatter + JSON/text export + docs draft
  - [ ] Day 4–5: Interactive remediation flow + AI suggestions + link editor utility
  - [ ] Day 6: Validation metrics (pre/post graph) + integration tests
  - [ ] Day 7: Final documentation + demo run on repo

- **Developer UX**:

```bash
# List orphans (text)
inneros workflow . --list-orphans

# JSON with exclusions
inneros workflow . --list-orphans --format json --exclude "Content Pipeline|Idea Backlog"

# Export remediation plan (markdown)
inneros workflow . --list-orphans --exclude "Content Pipeline|Idea Backlog" --export orphan-remediation.md

# Interactive remediation
inneros workflow . --remediate-orphans --interactive --exclude "Content Pipeline|Idea Backlog"
```

### **🟡 High Impact - Singleton Remediation**

#### **Peripheral Note Integration**
 - [ ] **Convert "Pasted image…" References** 
  - [ ] Identify all pasted image references in knowledge graph
  - [ ] Convert to annotated notes with contextual descriptions
  - [ ] Add upward links to relevant MOCs and lateral links to concepts

- [ ] **Integrate "Support SOP System Map"**
  - [ ] Add contextual link explaining relevance to workflow
  - [ ] Connect to Operations or Process MOC
  - [ ] Add lateral link to related system documentation

- [ ] **Enhance Dated Diary-Style Notes**
  - [ ] Convert single-linked progress notes to "progress snapshots"
  - [ ] Add upward links to relevant MOCs (Projects, Career, etc.)
  - [ ] Add sideways links to nearest concept or artifact notes
  - **Target**: Convert 5+ singletons to well-connected notes

#### **Mini-Cluster Integration**
- [ ] **Claude News Bot/Carousel Integration**
  - [ ] Add to AI & Prompting MOC under "Tools in Practice" section
  - [ ] Link to usage pattern notes or case studies
  - [ ] Connect to automation workflow examples

- [ ] **Voice/Prompting Utilities Integration**  
  - [ ] Create systematic links to AI & Prompting MOC
  - [ ] Add case study links where tools were applied
  - [ ] Document in "AI Tools Index" (see below)

### **🟢 Strategic - MOC Infrastructure**

#### **Cross-MOC Navigation Enhancement**
- [ ] **Projects MOC → AI and Prompting MOC**
  - [ ] Add section: "AI Methods Used Per Project"
  - [ ] Link each project to specific AI techniques employed
  - [ ] Include performance/outcome data where available

- [ ] **Career & Entrepreneurship MOC ↔ Projects MOC** 
  - [ ] Add "Portfolio Artifacts" bidirectional section
  - [ ] Link strategy notes to concrete deliverables
  - [ ] Add "Client-Ready Demos" section with project links

- [ ] **Add "What to do next" Sections**
  - [ ] Audit all existing MOCs for action orientation
  - [ ] Add "Open Tasks" or "TODO" links in each MOC
  - [ ] Connect to weekly review workflow for guided task selection

#### **Tools and Discovery Infrastructure**
- [ ] **Create "AI Tools Index"**
  - [ ] Design as child of AI & Prompting MOC  
  - [ ] List Claude/Whisper/Perplexity usage notes with case study links
  - [ ] Include performance data and best practices
  - [ ] Link to pattern notes and workflow examples

- [ ] **Enhance Bidirectional Linking**
  - [ ] Add relationship descriptors between key note pairs
  - [ ] Focus on high-traffic connection points first
  - [ ] Document link rationale for future reference

---

## 🔄 Ongoing Maintenance & Validation

### **Daily Tasks**
- [ ] **Triage Inbox**: Run `python3 src/cli/workflow_demo.py . --process-inbox`
- [ ] **Health Check**: Run `python3 quick_demo.py` for system validation
- [ ] **Connection Opportunities**: Watch for new notes that could strengthen identified bridges

### **Weekly Tasks**  
- [ ] **Run Enhanced Metrics**: `python3 src/cli/workflow_demo.py . --enhanced-metrics`
- [ ] **Connection Discovery**: `python3 src/cli/connections_demo.py .` 
- [ ] **Weekly Review**: `python3 src/cli/workflow_demo.py . --weekly-review --export-checklist weekly-review.md`
- [ ] **Progress Assessment**: Track connectivity improvements using analytics dashboard

### **Validation Commands**
```bash
# Network health assessment
python3 src/cli/workflow_demo.py . --enhanced-metrics

# Connection opportunity discovery  
python3 src/cli/connections_demo.py .

# Weekly review with connectivity focus
python3 src/cli/workflow_demo.py . --weekly-review --export-checklist weekly-review-$(date +%Y-%m-%d).md

# Comprehensive analytics
python3 src/cli/analytics_demo.py . --interactive
```

---

## 🚀 Phase 6 Preparation (Upcoming)

### **6.1 Multi-User Foundation** 
- [ ] **Authentication Scaffolding**
  - [ ] Research authentication options (local-first preferred)
  - [ ] Design user identity model
  - [ ] Plan permission system architecture

- [ ] **Visibility/Audit Extensions**
  - [ ] Extend current visibility tags for multi-user scenarios
  - [ ] Design per-user action logging
  - [ ] Plan share state transitions (private/shared/team/public)

### **6.2 Web Interface Foundation**
- [ ] **Technology Selection**
  - [ ] Choose web framework: Flask vs FastAPI vs Django
  - [ ] Select database for multi-user data (if needed)
  - [ ] Choose frontend approach: React vs Vue vs Svelte vs server-side

- [ ] **Basic Dashboard Prototype**
  - [ ] Analytics dashboard displaying current CLI insights
  - [ ] Web interface for weekly review checklist
  - [ ] Basic navigation for knowledge graph exploration

### **6.3 API Design**
- [ ] **Read-Only Endpoints**
  - [ ] Note metadata and analytics API
  - [ ] Search and connection discovery endpoints
  - [ ] Health and status monitoring endpoints

- [ ] **Mutation Endpoints** (Opt-in)
  - [ ] Note creation and editing behind permissions
  - [ ] Status transition API with audit trail
  - [ ] Batch operations for workflow management

---

## 📊 Success Metrics & Progress Tracking

### **Connectivity Goals (2-Week Target)**
- **Orphaned Notes**: Reduce by ≥50% (baseline from enhanced metrics)
- **Average Links/Note**: Increase by +1 (baseline from connection discovery)
- **Bridge Strength**: Establish 3 key bridges with 2-3 links each
- **Singleton Integration**: Convert 5+ peripheral notes to well-connected
- **MOC Enhancement**: Add "What to do next" sections to all MOCs

### **Phase 5 Foundation (Maintained)**
- **Test Coverage**: 66/66 tests passing ✅
- **Performance**: All targets exceeded ✅  
- **AI Features**: Production ready ✅
- **CLI Tools**: Full functionality ✅

### **Validation Approach**
- **Weekly Metrics**: Track orphaned note count, link density trends
- **Connection Discovery**: Use CLI tools to identify new opportunities
- **User Experience**: Test navigation between key knowledge areas
- **Analytics Dashboard**: Monitor workflow health and productivity gains

---

## 🎯 Quick Actions (Next Session Priorities)

### **🔴 Immediate (Today)**
1. Run `/bug-triage-workflow` for Template Processing Failure (Bug 1) and begin fix
2. Run Baseline Metrics: `python3 src/cli/workflow_demo.py . --enhanced-metrics` for progress tracking
3. Create Bridge Note: "How AI Prompting Supports TDD and Weekly Review Automation"

### **🟡 This Week**
1. **Entrepreneurship↔Artifacts Bridge**: Link strategy notes to portfolio items
2. **AI Tools Index**: Create under AI & Prompting MOC
3. **Singleton Conversion**: Pick 3-5 peripheral notes and add meaningful connections

### **🟢 Next Week**
1. **Pattern Notes**: Create LLM Outage Handling and Voice-to-Clarity workflows  
2. **Cross-MOC Navigation**: Add bidirectional sections between major MOCs
3. **Phase 6 Planning**: Technology selection and architecture design

---

## 📁 Reference Files

### **Primary Documentation**
- `Projects/inneros-manifest-v2.md` - Comprehensive project context and goals
- `Projects/windsurf-project-changelog.md` - Detailed development history  
- `.windsurf/windsurfrules.md` (v3.0) - Unified development and workflow rules
- `README.md` - Quick start and overview

### **Key CLI Demonstrations**
- `python3 quick_demo.py` - System health and feature validation
- `python3 src/cli/analytics_demo.py . --interactive` - Comprehensive analytics
- `python3 demo_user_journeys.py` - End-to-end workflow simulation

---

## 🎉 Completed Phases

### **✅ Phase 5: AI-Enhanced Knowledge Management (COMPLETE)**
- **5.1**: Local AI infrastructure (Ollama + Llama 3.1 8B)
- **5.2**: Smart tagging system with graceful fallbacks  
- **5.3**: Content enhancement (quality scoring, summarization, connections)
- **5.4**: Analytics dashboard and workflow management
- **5.5**: Weekly review automation with checklist export

### **✅ Infrastructure & Validation (COMPLETE)**
- **Technical Requirements**: 66/66 tests passing, import resolution
- **CLI Functionality**: All 8 tools working, performance validated
- **Production Ready**: Real user data tested (212 notes, 50K words)
- **Templates & Workflow**: Reliable note creation and processing

---

## 🔄 Backlog (Future Phases)

### **Phase 7: Production & Distribution**
- Installation packages and distribution strategy
- Performance optimization for 1000+ note collections  
- Monitoring and alerting systems
- Configuration management for different environments

### **Phase 8: Advanced Features**
- Mobile integration with voice-to-note capabilities
- Multi-modal AI (text, images, audio)
- Advanced reasoning and inference
- Plugin architecture for extensibility

---

> **Success Philosophy**: Every action should either strengthen knowledge connections, improve AI-human collaboration, or advance toward multi-user capabilities. Focus on high-impact changes that compound over time.

**Version**: 2.0  
**Next Review**: Weekly during connectivity enhancement phase  
**Status**: Active Development → Knowledge Graph Enhancement
