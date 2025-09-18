# InnerOS Zettelkasten - Project Todo v3.0

**Last Updated**: 2025-09-18 16:36 PDT  
**Status**: ✅ MAJOR SYSTEMS COMPLETE → Phase 6 Preparation  
**Reference**: `Projects/inneros-manifest-v3.md` for comprehensive context

---

## ✅ Recently Completed Major Systems

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

## 🎯 Active Projects

### 🔴 Image Linking System (System Integrity)

- Problem: Images disappear during AI automation processes
- Goal: Preserve media assets and references through all workflows
- Deliverables:
  - Media reference audit + test coverage
  - Link rewriting/preservation strategy
  - Integration into WorkflowManager operations

### 📚 Reading Intake Pipeline (Phase 5 Extension)

- Approach: Integration-first; reuse Phase 5 AI workflows
- Dependencies: Template system ✅, schema integration ⏳, image linking ⏳
- Deliverables:
  - Schema extension for `source:` and `saved_at`
  - Literature templates with claims/quotes
  - CLI import adapters + triage

---

## 🛣️ Next 2 Weeks Roadmap

1. Image Linking System
   - [ ] Formalize link model (paths, IDs, fallback)
   - [ ] Add tests: copy/move/update scenarios
   - [ ] Implement preservation + rewriting
   - [ ] Integrate with directory organizer and AI workflows

2. Reading Intake Pipeline
   - [ ] Extend YAML validator for `source:` and `saved_at`
   - [ ] Add literature templates + import adapters (CSV/JSON, bookmarks)
   - [ ] CLI: `--import-bookmarks`, `--process-literature`
   - [ ] Performance: <30s per item triage

3. Phase 6 Preparation
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
