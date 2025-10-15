---
type: planning
created: 2025-10-15 10:24
status: active
priority: P0
tags: [epic-planning, architecture, next-steps]
---

# Next Epic Planning - October 15, 2025

**Current State**: ADR-002 Complete (Phases 1-12) ✅  
**WorkflowManager**: 812 LOC (within architectural limits) ✅  
**Test Status**: 53/55 passing (96%) ✅  
**Branch**: `feat/adr-002-phase-12b-fleeting-note-coordinator`

---

## 🎉 Recent Victory: ADR-002 Complete!

### What We Just Finished
- **All 12 coordinators extracted** from WorkflowManager god class
- **1,585 LOC reduction** (2,397 → 812 LOC)
- **4,250 LOC** properly organized into specialized coordinators
- **ConfigurationCoordinator anti-pattern** identified and reverted
- **Clean architecture restored** to Phase 11 pattern

### Key Lesson Learned
> "Phase 11 was already optimal" - ConfigurationCoordinator added 1,250 LOC overhead for zero benefit

---

## 🎯 Epic Options (Priority Order)

### Option 1: 🟢 MERGE & STABILIZE (Recommended First)
**Duration**: 2-4 hours  
**Value**: Locks in architectural gains, enables future work

**Tasks**:
1. ✅ Fix 2 failing test assertions (30 min)
   - `test_promote_note_to_permanent` - Summary generation expectation
   - `test_promote_note_to_fleeting` - Status field expectation
2. ✅ Fix SafeImageProcessingCoordinator lint warnings (30 min)
   - Add runtime checks for Optional callbacks
   - Or document that callbacks are set post-init
3. ✅ Update documentation (1 hour)
   - Update project-todo-v3.md with current 812 LOC reality
   - Archive ADR-002 as complete
   - Update README with new architecture
4. ✅ Merge to main (1 hour)
   - Final validation
   - Create release notes
   - Tag as v2.0 (architectural milestone)

**Success Criteria**:
- 55/55 tests passing (100%)
- Zero lint warnings
- Documentation accurate
- Clean main branch for next epic

**Why First**: Don't start new work on unstable foundation

---

### Option 2: 🔴 P0 - Note Lifecycle Auto-Promotion
**Duration**: 4-6 hours  
**Value**: Completes workflow automation - "I really want auto-promotion, to enable flow"

**Current Status**: PBI-001 complete (status update bug fixed)

**Remaining Work**:
- **PBI-002**: Complete Directory Integration (90 min)
  - Add literature_dir initialization
  - Enhance promote_note() for all types
  - DirectoryOrganizer integration
  
- **PBI-004**: Auto-Promotion System ⭐ (2-3 hours)
  - Implement `auto_promote_ready_notes(min_quality=0.7)`
  - Preview mode shows candidates
  - Execute mode moves files + sets status: published
  - CLI integration: `--auto-promote --quality 0.7 --preview`

- **PBI-003**: Execute Safe File Moves (30 min)
  - 30 misplaced files ready to move
  - Backup + validation

- **PBI-005**: Repair Orphaned Notes (60 min)
  - Fix 77 notes with ai_processed: true, status: inbox

**Impact**:
- **Before**: Manual promotion bottleneck, 77 notes stuck
- **After**: Quality-gated auto-promotion, true workflow flow

**Dependencies**: Merge & Stabilize complete

---

### Option 3: 🟡 P1 - Source Code Reorganization
**Duration**: 4-6 weeks (gradual)  
**Value**: Developer experience, code discoverability

**Problem**:
- `src/ai/` - 56 Python files (impossible to navigate)
- `src/cli/` - 44 Python files (cognitive overload)
- 20+ minutes to find related code

**Goal**: Domain-driven organization, <2 minute code discovery (90% improvement)

**80/20 Approach**:
1. Split `ai/` into 7 domains (40% of value, 2 hours)
2. Split `cli/` into 7 features (30% of value, 2 hours)
3. Consolidate utilities (20% of value, 1 hour)
4. Create `models/` package (10% of value, 1 hour)

**Proof of Concept** (Week 1):
- Extract `ai/connections/` (12 files)
- Extract `ai/tags/` (10 files)
- Validate tests pass
- Go/No-Go decision

**Dependencies**: Can start anytime (low risk with test coverage)

---

### Option 4: 🔵 P1 - Distribution System
**Duration**: 2-3 weeks  
**Value**: Makes InnerOS installable by others

**Current State**: Only works in development environment

**Goal**: pip-installable package with proper CLI entry points

**Phases**:
1. Package structure (setup.py, pyproject.toml)
2. CLI entry points (inneros command)
3. Configuration management
4. Installation documentation
5. Release automation

**Dependencies**: Code organization helps but not required

---

### Option 5: 🟣 P2 - Quality Audit Bug Fixes
**Duration**: 2-3 hours  
**Value**: Fixes 5 known bugs

**Status**: Currently deferred (bugs in monolithic CLI)

**Bugs**:
1. Connection Discovery import error (5 min)
2. Enhanced Metrics KeyError (10 min)
3. Fleeting Health AttributeError (60 min)
4. Orphaned Notes KeyError (5 min)
5. YouTube Processing failures (30 min)

**Decision Point**: 
- Fix now in current architecture?
- Or wait for ADR-004 CLI extraction (dedicated CLIs)?

**Recommendation**: Fix critical bugs now, defer others to CLI extraction

---

## 🎯 Recommended Sequence

### Immediate (This Session):
1. **Cleanup Projects/ACTIVE** (15 min)
   - Run cleanup script
   - Move 20 completed files to archive
   - Result: 43 → ~15 files

2. **Choose Next Epic** (Decision point)

### Short-term Sprint Options:

**Option A: Conservative Path** (Recommended)
1. Merge & Stabilize (2-4 hours)
2. Note Lifecycle Auto-Promotion (4-6 hours)
3. Quality Audit Critical Bugs (1 hour)
→ **Total: 1-2 days for complete workflow automation**

**Option B: Developer Experience Path**
1. Merge & Stabilize (2-4 hours)
2. Source Code Reorganization POC (4 hours)
3. Go/No-Go decision
→ **Total: 1 day for improved code navigation**

**Option C: Distribution Path**
1. Merge & Stabilize (2-4 hours)
2. Distribution System Phase 1 (8 hours)
→ **Total: 2 days for pip-installable package**

---

## 💡 Recommendation: Conservative Path (Option A)

**Why**:
1. **User Priority**: "I really want auto-promotion, to enable flow"
2. **Completes Workflow**: Auto-promotion is the missing piece
3. **Quick Wins**: 1-2 days total, immediate value
4. **Foundation Ready**: All infrastructure exists (DirectoryOrganizer, quality scoring, etc.)
5. **Clears Backlog**: Fixes 77 orphaned notes, 30 misplaced files

**After Auto-Promotion Complete**:
- InnerOS becomes true flow system
- Weekly review more effective
- Knowledge capture → processing → promotion fully automated
- Foundation for streaming demo (show auto-promotion in action)

**Then Consider**: Distribution System for wider sharing

---

## 📊 Success Metrics by Epic

### Merge & Stabilize
- ✅ 55/55 tests passing (100%)
- ✅ Zero lint warnings
- ✅ Documentation accurate
- ✅ v2.0 tagged

### Note Lifecycle Auto-Promotion
- ✅ Auto-promotion working with quality threshold
- ✅ 77 orphaned notes repaired
- ✅ 30 misplaced files moved
- ✅ Weekly review shows accurate triage
- ✅ Zero manual intervention required

### Source Code Reorganization
- ✅ <12 files per directory
- ✅ <2 min code discovery (90% improvement)
- ✅ All tests passing
- ✅ Domain-driven structure

### Distribution System
- ✅ pip install inneros-zettelkasten works
- ✅ inneros CLI command available
- ✅ Configuration documented
- ✅ Installation guide complete

---

## 🚀 Next Steps (Decision Required)

**Immediate**: Run cleanup script

**Then Choose Path**:
- [ ] **Conservative** (Auto-promotion) - Enables flow
- [ ] **Developer** (Code reorg) - Improves DX
- [ ] **Distribution** (Package) - Enables sharing

**Your Call**: Which epic delivers most value for your current workflow needs?

---

## 📝 Notes

**Branch Strategy**:
- Current: `feat/adr-002-phase-12b-fleeting-note-coordinator`
- Merge: Create `release/v2.0-adr-002-complete` branch
- Next: Create new epic branch after merge

**Test Strategy**:
- Keep 96%+ passing rate
- Fix assertions as we go
- Add regression tests for new features

**Documentation Strategy**:
- Archive completed work immediately
- Keep ACTIVE/ lean (10-15 files max)
- Update README with each epic completion

