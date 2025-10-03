# InnerOS Zettelkasten - Project Todo v3.0

**Last Updated**: 2025-10-03 09:06 PDT  
**Status**: 🔴 Critical Bug Documented → Image Linking System Implementation Urgent  
**Reference**: `Projects/inneros-manifest-v3.md` for comprehensive context

---

## ✅ Recently Completed Major Systems

### ✅ TDD Iteration 9: Multi-Device Screenshot Support (Oct 2025)

- Samsung S23 + iPad unified processing pipeline
- 31/31 tests passing (11 unit + 6 integration + real data)
- Device-aware metadata in note frontmatter
- Zero regressions, 100% real data validation
- Volume: 1,502 total screenshots (Samsung 1,476 + iPad 26)

### ✅ TDD Iteration 8: Individual Screenshot Files (Oct 2025)

- Individual file generation per screenshot (vs daily batch notes)
- Semantic filenames: `capture-YYYYMMDD-HHMM-keywords.md`
- Real data validation: 3 Samsung S23 screenshots processed
- 6/6 tests passing, performance: 96s per screenshot (real OCR)

### ✅ Fleeting Note Lifecycle Management MVP (Phase 5.6)

- Health, triage, and promotion workflows delivered
- CLI: `--fleeting-health`, `--fleeting-triage`, `--promote-note`
- Comprehensive tests and lessons learned docs

### ✅ Safety-First Directory Organization (P0 + P1)

- Backup + rollback, dry-run planning, link preservation
- Safe execution with post-move validation
- Real-world validation with conflict prevention

### ✅ Template Processing System

- Templater syntax fixed across templates
- Production repair script + comprehensive testing
- Reading Intake Pipeline unblocked

---

## 🎯 Active Projects (RESCOPED)

### 🔴 Image Linking System (HIGHEST PRIORITY - System Integrity)

- **Problem**: Images disappear during AI automation processes
- **Impact**: Critical system integrity issue affecting media preservation
- **Goal**: Preserve media assets and references through all workflows
- **Status**: 🔍 CRITICAL BUG DOCUMENTED - Immediate implementation required
- **Active Bug Report**: `Projects/ACTIVE/BUG-20251003-0906-screenshot-image-linking.md` ✅
- **Deliverables**:
  - MediaAssetManager utility class for image copying
  - Relative path generation for repository-local images
  - Media reference audit + comprehensive test coverage
  - Link rewriting/preservation strategy
  - Integration into WorkflowManager operations
  - Integration with DirectoryOrganizer for safe file moves
  - **Manifest**: `Projects/ACTIVE/image-linking-system-bug-fix-manifest.md` ✅

### 🟡 Knowledge Capture System - POC PHASE

- **Goal**: Transform mobile screenshots + voice notes into connected Zettelkasten knowledge
- **Innovation**: Temporal pairing of screenshot + voice context eliminates annotation burden
- **Real Workflow**: Samsung S23 captures → OneDrive sync → timestamp matching → knowledge integration
- **POC Focus**: Validate screenshot + voice note pairing accuracy (>90% target)
- **Deliverables**:
  - **POC Manifest**: `Projects/capture-matcher-poc-manifest.md` ✅
  - **Full System Manifest**: `Projects/knowledge-capture-system-manifest.md` ✅
  - Capture matcher script with OneDrive integration
  - 1-week real-world validation with success metrics
  - Go/No-Go decision for full system development

### 🟡 Automated Background Daemon (Core Infrastructure)

- **Goal**: Transform InnerOS into always-running, autonomous knowledge processing system
- **Approach**: Extract existing AutoProcessor into standalone daemon service  
- **Dependencies**: Current AI workflow system ✅, system service configuration ⏳
- **Deliverables**:
  - Background daemon with file watching and scheduling
  - System service configuration (macOS LaunchD/Linux systemd)
  - Automated maintenance tasks (weekly review, orphan detection)
  - **Manifest**: `Projects/automated-background-daemon-manifest.md` ✅

### 📚 Reading Intake Pipeline (Phase 5 Extension)

- **Approach**: Integration-first; reuse Phase 5 AI workflows
- **Dependencies**: Template system ✅, schema integration ⏳, image linking ⏳
- **Deliverables**:
  - Schema extension for `source:` and `saved_at`
  - Literature templates with claims/quotes
  - CLI import adapters + triage
  - [ ] **User journey flowchart** (NEEDS REVIEW: `Projects/reading-intake-user-journey-flowchart.md`)

---

## 🛣️ Next 2 Weeks Roadmap

1. **Image Linking System** (Priority 1 - CRITICAL) 🔴
   - [ ] Create branch: `feat/image-linking-system-tdd-10`
   - [ ] Media reference audit across all workflows
   - [ ] Formalize link model (paths, IDs, fallback strategies)
   - [ ] Add comprehensive tests: copy/move/update scenarios
   - [ ] Implement preservation + rewriting logic
   - [ ] Integrate with DirectoryOrganizer and WorkflowManager
   - [ ] Real data validation with existing notes containing images

2. **Knowledge Capture System - POC** (Priority 2) 🔥
   - [ ] Create branch: `feat/visual-capture-poc-tdd-1`
   - [ ] Voice note detection from OneDrive
   - [ ] Screenshot + voice temporal pairing (±60s)
   - [ ] Combined capture note template
   - [ ] 1-week real-world validation
   - [ ] Go/No-Go decision based on >90% pairing accuracy

3. **Smart Link Management — Iteration 6** (Priority 3)
   - [ ] Create branch: `feat/smart-link-management-undo-tdd-6`
   - [ ] Add failing tests for `UndoManager` and CLI `--undo`
   - [ ] Implement minimal undo stack with backup integration
   - [ ] Plan bidirectional link consistency and atomic operations

4. **Automated Background Daemon** (Priority 4)
   - [ ] Extract AutoProcessor into daemon controller
   - [ ] Add APScheduler for automated maintenance tasks
   - [ ] Create daemon control CLI (`inneros daemon --start/stop/status`)
   - [ ] Design macOS LaunchD service configuration
   - [ ] Test background processing and scheduling

5. **Reading Intake Pipeline** (Priority 5)
   - [ ] Extend YAML validator for `source:` and `saved_at`
   - [ ] Add literature templates + import adapters (CSV/JSON, bookmarks)
   - [ ] CLI: `--import-bookmarks`, `--process-literature`
   - [ ] Performance: <30s per item triage

6. **Phase 6 Preparation** (Background)
   - [ ] Define multi-user data model and permissions
   - [ ] API surface (read-only) and events design
   - [ ] UI scaffolding plan (analytics dashboard)

---

## 📋 Tracking

- Tests must remain 66/66 passing (baseline) or expand with new features
- Performance targets must be preserved or improved
- Maintain backward compatibility and workflow integrity

---

## 🔁 Backlog (Future Phases)

### YouTube Transcript AI Processing System ⭐ HIGH PRIORITY
**Status**: 📋 PLANNING - Complete manifest ready for implementation  
**Manifest**: `Projects/ACTIVE/youtube-transcript-ai-processing-manifest.md` ✅  
**Impact**: Transforms major workflow input (YouTube videos) into AI-enhanced knowledge

**User Story**: "Watch YouTube → Add 1-2 sentence insight → LLM auto-extracts relevant quotes with timestamps"

**Implementation Plan** (4 TDD Iterations):
1. **TDD Iteration 1**: Transcript fetching (`youtube-transcript-api`, no API key)
2. **TDD Iteration 2**: Context-aware quote extraction (user insight guides LLM)
3. **TDD Iteration 3**: Template integration & storage (update youtube-video.md notes)
4. **TDD Iteration 4**: CLI + automation (on-demand + background daemon)

**Key Features**:
- Only 2 prompts maintained (URL + insight)
- Automated + on-demand processing modes
- Quality-based + user-guided quote selection
- Timestamps preserved for video reference
- 83-90% time savings vs manual transcription

**Integration Investigation** (Backlog):
- [ ] Investigate existing Connection Discovery integration for transcript → wiki-link automation
- [ ] Evaluate existing WorkflowManager patterns for quality scoring
- [ ] Review AutoProcessor daemon for background processing patterns

**Future Enhancements** (Post-MVP):
- YouTube Data API v3 for enhanced metadata
- Multi-language transcript support
- Playlist batch processing
- Chapter detection and summarization

### Phase 7
- Packaging, distribution, monitoring, configuration

### Phase 8
- Mobile/voice integrations, multi-modal AI, plugin architecture

---

Version: 3.0  
Next Review: Weekly during Phase 6 preparation  
Status: Active Development → Knowledge Graph & Multi-User Foundations
