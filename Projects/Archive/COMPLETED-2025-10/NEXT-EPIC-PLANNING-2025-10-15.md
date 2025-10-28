---
type: planning
created: 2025-10-15 10:24
status: active
priority: P0
tags: [epic-planning, architecture, next-steps]
---

# Next Epic Planning - October 15, 2025

**Last Updated**: 2025-10-15 19:16 PDT

**Current State**: ADR-002 Complete (Phases 1-12) ✅  
**WorkflowManager**: 812 LOC (within architectural limits) ✅  
**Test Status**: 34/34 passing (100%) ✅ - Auto-promotion complete  
**Branch**: `main` (v2.1-auto-promotion released)

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

### Option 0: 🔍 System Observability Integration (P0, 6 hours) ⭐ **RECOMMENDED**
**Duration**: 6 hours (2h + 1h + 1h + 2h phases)  
**Value**: Critical usability - know what's running, when, and if it's working  
**File**: `system-observability-integration-manifest.md`

**The Problem You Discovered**:
> "I don't have much visibility on what's running or not? When it ran? If it's currently running too."

**What Already Exists** (discovered 2025-10-15):
- ✅ **Workflow Dashboard** (392 LOC, 21 tests) - Production ready
- ✅ **Terminal Dashboard** (136 LOC) - Live daemon monitoring
- ✅ **Automation Daemon** (511 LOC) - APScheduler + health checks
- ✅ **Health System** (145 LOC) - Metrics collection
- ✅ **~1,184 LOC** of production infrastructure you forgot existed!

**The Gap**:
- ❌ No unified CLI entry point (`inneros status`)
- ❌ Can't tell if daemon running or automation active
- ❌ Cron jobs disabled 6 days (last activity: Oct 9)
- ❌ Zero documentation on accessing dashboards

**4 Phases** (Integration, not development):
1. **Phase 1** (2h, P0): Status Command - `inneros status` shows everything
2. **Phase 2** (1h, P1): Dashboard Launcher - `inneros dashboard`
3. **Phase 3** (1h, P1): Daemon Controls - `inneros daemon start/stop/status`
4. **Phase 4** (2h, P2): Automation Toggle - `inneros automation enable/disable`

**Success Criteria**:
- ✅ Single command shows system state (<5s)
- ✅ Reuses 100% existing code
- ✅ Adds <300 LOC thin CLI wrappers
- ✅ Immediate usability improvement

**Why P0 First**:
- Unblocks daily usage (can't use what you can't see)
- Quick win: 2 hours → complete visibility
- No new development, just integration
- Foundation for all other work

---

### Option 1: 🟢 MERGE & STABILIZE (Completed)
**Duration**: 2-4 hours  
**Status**: ✅ **COMPLETED** (2025-10-15)

**What Was Completed**:
1. ✅ All test assertions fixed
2. ✅ SafeImageProcessingCoordinator lint warnings resolved
3. ✅ Documentation updated
4. ✅ Merged to main as **v2.1-auto-promotion**
5. ✅ 34/34 tests passing (100%)
6. ✅ Real data validation: 8 notes promoted, 0 errors

**Outcome**: Clean foundation ready for next work

---

### Option 2: ✅ COMPLETED - Note Lifecycle Auto-Promotion
**Duration**: 4-6 hours  
**Status**: ✅ **PRODUCTION READY** (Completed 2025-10-15)

**Completed Work**:
- ✅ **PBI-004**: Auto-Promotion System ⭐
  - Implemented `auto_promote_ready_notes(min_quality=0.7)`
  - Dry-run preview mode working
  - Execute mode moves files + updates status
  - CLI integration: `auto-promote --dry-run --quality-threshold 0.7`
  - **34/34 tests passing (100%)**
  
- ✅ **PBI-005**: Metadata Repair System
  - Inbox metadata repair complete (resolved orphaned notes issue)
  - 9 notes repaired successfully
  
- ✅ **Real Data Validation**
  - 8 notes promoted successfully
  - 0 errors encountered
  - <1 second execution time (10x better than target)

**Deferred** (Not needed):
- ~~PBI-002~~: Directory integration already complete
- ~~PBI-003~~: Misplaced files resolved by real data execution
- ~~PBI-005~~: Orphaned notes already fixed by metadata repair

**Impact Achieved**:
- ✅ Quality-gated auto-promotion operational
- ✅ True workflow flow enabled
- ✅ Zero manual intervention required

**Status**: ✅ Complete and merged to main

---

### Option 3: 🎬 YouTube Integration (P1, 5-7 hours)
**Duration**: 5-7 hours  
**Value**: Unified workflow for video knowledge capture  
**File**: `youtube-auto-promotion-integration-manifest.md`

**Features**:
- User approval workflow (`ready_to_process` flag)
- AI processing preserves user notes
- Quality scoring for video content
- Auto-promotion to `Literature Notes/YouTube/`
- Migration for 37 existing YouTube notes

**6 Phases**: Metadata → YouTube Processor → Auto-Promotion → Migration → CLI → Testing

**Why After Observability**: Need to see automation working first

---

### Option 4: 🟡 P1 - Source Code Reorganization
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

