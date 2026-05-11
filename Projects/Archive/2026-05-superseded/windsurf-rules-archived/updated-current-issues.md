---
trigger: manual
---

---
type: issues-tracker
updated: 2025-10-17
priority: medium
tags: [bugs, technical-debt, known-issues]
---

# Current Issues & Technical Debt

> **Last Updated**: 2025-10-17 20:15 PDT  
> **Status**: Minimal technical debt, all critical issues resolved

---

## 🟢 Active Issues (3 items)

### Issue #1: Connection Discovery Import Error (P2, 5 min)
**File**: Unknown (from Quality Audit Oct 2025)  
**Error**: Import error in connection discovery module  
**Impact**: Low (feature still works)  
**Fix**: Simple import path correction  
**Priority**: P2 (cosmetic)

### Issue #2: Code Organization (P1, 4-6 weeks gradual)
**Files**: `development/src/ai/` (56 files), `development/src/cli/` (44 files)  
**Problem**: Flat directory structure, 20+ minutes to find related code  
**Impact**: Developer experience, code discoverability  
**Solution**: Domain-driven reorganization (7 domains each)  
**Priority**: P1 (quality of life)  
**Status**: Planned, manifest exists

### Issue #3: 4 Minor Quality Audit Bugs (P2, 2 hours)
**Source**: October 2025 quality audit  
**Status**: Deferred (currently in monolithic CLI, low impact)  
**Details**: TBD when resuming work  
**Priority**: P2 (nice to have)

---

## 🔴 Critical Issues (0 items)

✅ **All critical issues resolved as of Oct 17, 2025**

Previously resolved:
- ~~Note lifecycle status bug~~ → Fixed Oct 14 (PBI-001)
- ~~Auto-promotion missing~~ → Implemented Oct 15 (PBI-004)
- ~~Inbox metadata missing type field~~ → Fixed Oct 15 (8 notes repaired)
- ~~Dashboard metrics missing~~ → Implemented Oct 16 (Phase 3.2 P1)
- ~~System status visibility~~ → Implemented Oct 15 (status CLI)

---

## 🟡 Architectural Debt (1 item)

### WorkflowManager Size Exception (Documented, Stable)
**File**: development/src/ai/workflow_manager.py  
**Current Size**: 812 LOC  
**Limit**: 500 LOC (ADR-001)  
**Status**: ✅ Exception granted (ADR-003)  
**Reason**: Central orchestrator, pure delegation logic  
**Action**: Monitor only, no immediate refactoring needed  

**Historical Context**:
- Was 2,397 LOC (Jun 2025)
- Reduced to 812 LOC via ADR-002 (12 coordinator extractions)
- 66% reduction achieved
- All business logic extracted
- Remaining code is pure delegation

---

## ✅ Recently Resolved (Oct 2025)

### Critical Bugs Fixed

**Oct 14-15: Note Lifecycle Status Management** ✅
- Bug: Notes processed by AI but status remained "inbox"
- Impact: 77 notes stuck, manual intervention required
- Fix: NoteLifecycleManager extraction (ADR-002)
- Result: Status transitions working, auto-promotion enabled

**Oct 15: Inbox Metadata Missing Type Field** ✅
- Bug: 8 notes missing required type field, blocking auto-promotion
- Impact: 21% error rate in auto-promotion
- Fix: MetadataRepairEngine implementation
- Result: All inbox notes now promotable

**Oct 16: Analytics Template Type Errors** ✅
- Bug: Analytics route crashed with string recommendations
- Fix: Type safety improvements (16 tests)
- Result: Analytics page stable

**Oct 16: Weekly Review Performance** ✅
- Bug: Weekly review timed out (>30s)
- Fix: Simplified scanning, removed expensive AI calls
- Result: 30x faster (<1s)

### Architectural Improvements

**Oct 10-11: ADR-004 CLI Layer Extraction** ✅
- Debt: 2,074 LOC monolithic workflow_demo.py
- Action: Extracted 10 dedicated CLIs
- Result: Clean architecture, 100% test coverage maintained

**Oct 7-14: ADR-002 WorkflowManager Decomposition** ✅
- Debt: 2,397 LOC god class (479% over limit)
- Action: Extracted 12 coordinators (Phases 1-12)
- Result: 812 LOC (66% reduction), clean delegation pattern

---

## 📊 Health Metrics

**Test Coverage**: ✅ Excellent
- 72+ tests passing (100%)
- Fast test suite: 1.35s for integration
- Zero known test failures

**Architectural Compliance**: ✅ Good
- 1 documented exception (ADR-003)
- All other files within limits
- Clean separation of concerns

**Code Organization**: ⚠️ Needs Improvement
- ai/ and cli/ directories flat (56+44 files)
- Code discovery time: 20+ minutes
- Solution planned: Domain-driven reorganization

**Performance**: ✅ Excellent
- Status command: <5s
- Integration tests: 1.35s
- AI processing: <10s
- Dashboard: 2s auto-refresh

---

## 🎯 Debt Reduction Strategy

### Immediate (P0): None
All P0 issues resolved Oct 2025.

### Short Term (P1, Next 1-2 months):
1. **Source Code Reorganization** (4-6 weeks gradual)
   - Split ai/ into 7 domains
   - Split cli/ into 7 features
   - 90% improvement in code discovery

### Medium Term (P2, Next 3-6 months):
1. **Quality Audit Bug Fixes** (2-3 hours)
   - Connection Discovery import error
   - 4 minor bugs from October audit

2. **Distribution System** (2-3 weeks)
   - pip-installable package
   - CLI entry points (inneros command)
   - Installation documentation

### Long Term (P3, Future):
1. **Model Migration** (gpt-oss:20b upgrade)
2. **Enhanced AI Features** (advanced analytics)
3. **Multi-user Support** (Phase 2+)

---

## 🚨 Known Limitations

### By Design:
- **CLI-first**: No web UI for primary workflows (dashboard is monitoring only)
- **Local-only**: No cloud sync (by design, privacy-first)
- **Single-user**: No multi-user support (Phase 1)
- **Python-based**: Requires Python 3.11+ environment

### Technical:
- **Flask not auto-starting**: Dashboard requires manual launch
- **Virtual environment required**: Must activate .venv before running
- **Ollama dependency**: AI features require Ollama installed

### Documentation:
- **Installation guide**: Needs update for new CLI commands
- **User onboarding**: No guided setup flow
- **CLI reference**: Some new commands not yet documented

---

## 📝 Issue Tracking Process

### How to Add New Issues:
1. Identify bug or technical debt
2. Add to appropriate section above
3. Include: File, Impact, Priority, Status
4. Update "Last Updated" timestamp
5. Create GitHub issue for P0/P1 items

### How to Resolve Issues:
1. Complete fix/implementation
2. Move to "Recently Resolved" section
3. Document fix details and results
4. Update "Last Updated" timestamp

### Priority Definitions:
- **P0 Critical**: Blocks core functionality, fix immediately
- **P1 High**: Important feature/quality, fix within 2 weeks
- **P2 Medium**: Nice to have, fix when convenient
- **P3 Low**: Future enhancement, backlog

---

## 🔍 Monitoring & Prevention

### Architectural Safeguards:
- ✅ ADR-001: File size limits (500 LOC)
- ✅ ADR-002: God class prevention pattern
- ✅ ADR-004: CLI layer extraction complete
- ✅ Test-first development (TDD methodology)

### Regular Reviews:
- Monthly architectural health check
- Quarterly code organization review
- Per-epic technical debt assessment
- Post-completion lessons learned documentation

---

**Issues Last Reviewed**: 2025-10-17 20:15 PDT  
**Next Review Due**: After completing next epic  
**Critical Issues**: 0 ✅  
**Active Issues**: 3 (all P1/P2)