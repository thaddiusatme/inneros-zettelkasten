# InnerOS Zettelkasten - Project Todo v3.0

**Last Updated**: 2025-10-01 19:40 PDT  
**Status**: ✅ TDD Iteration 8 Complete → Multi-Device Support Ready  
**Reference**: `Projects/inneros-manifest-v3.md` for comprehensive context

---

## ✅ Recently Completed Major Systems

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

### 🔴 TDD Iteration 9: Multi-Device Screenshot Support (HIGHEST PRIORITY)

- **Goal**: Extend Samsung S23 processing to support iPad screenshots in unified workflow
- **Status**: 📋 MANIFEST COMPLETE → Ready for implementation
- **Approach**: TDD methodology (RED → GREEN → REFACTOR → COMMIT)
- **Deliverables**:
  - **Manifest**: `Projects/ACTIVE/multi-device-screenshot-support-tdd-iteration-9-manifest.md` ✅
  - Device detection system (Samsung S23 + iPad patterns)
  - Multi-device scanner with unified processing
  - 10+ comprehensive tests (device detection, timestamp extraction, integration)
  - Real data validation: Samsung + iPad screenshots
- **Timeline**: 3 days (1 RED, 1 GREEN, 1 REFACTOR/COMMIT)
- **Volume**: Samsung (1,476) + iPad (26) = 1,502 total screenshots

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

### 🔴 Image Linking System (System Integrity)

- **Problem**: Images disappear during AI automation processes
- **Goal**: Preserve media assets and references through all workflows
- **Deliverables**:
  - Media reference audit + test coverage
  - Link rewriting/preservation strategy
  - Integration into WorkflowManager operations

### 📚 Reading Intake Pipeline (Phase 5 Extension)

- **Approach**: Integration-first; reuse Phase 5 AI workflows
- **Dependencies**: Template system ✅, schema integration ⏳, image linking ⏳
- **Deliverables**:
  - Schema extension for `source:` and `saved_at`
  - Literature templates with claims/quotes
  - CLI import adapters + triage
  - [ ] **User journey flowchart** (NEEDS REVIEW: `Projects/reading-intake-user-journey-flowchart.md`)

-
## 🛣️ Next 2 Weeks Roadmap

1. **Smart Link Management — Iteration 6 (Undo & Bidirectional)** (Priority 1)
   - [ ] Create branch: `feat/smart-link-management-undo-tdd-6`
   - [ ] Add failing tests for `UndoManager` and CLI `--undo`
   - [ ] Implement minimal undo stack with backup integration
   - [ ] Plan bidirectional link consistency and atomic operations

2. **Automated Background Daemon** (Priority 2)
   - [ ] Extract AutoProcessor into daemon controller
   - [ ] Add APScheduler for automated maintenance tasks
   - [ ] Create daemon control CLI (`inneros daemon --start/stop/status`)
   - [ ] Design macOS LaunchD service configuration
   - [ ] Test background processing and scheduling

3. **Image Linking System** (Priority 3)
   - [ ] Formalize link model (paths, IDs, fallback)
   - [ ] Add tests: copy/move/update scenarios
   - [ ] Implement preservation + rewriting
   - [ ] Integrate with directory organizer and AI workflows

4. **Reading Intake Pipeline** (Priority 4)
   - [ ] Extend YAML validator for `source:` and `saved_at`
   - [ ] Add literature templates + import adapters (CSV/JSON, bookmarks)
   - [ ] CLI: `--import-bookmarks`, `--process-literature`
   - [ ] Performance: <30s per item triage

4. **Phase 6 Preparation** (Background)
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

- Phase 7: Packaging, distribution, monitoring, configuration
- Phase 8: Mobile/voice integrations, multi-modal AI, plugin architecture

---

Version: 3.0  
Next Review: Weekly during Phase 6 preparation  
Status: Active Development → Knowledge Graph & Multi-User Foundations
