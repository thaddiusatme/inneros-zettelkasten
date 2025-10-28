# Product Backlog Item (PBI) Planning Session

**Date**: 2025-10-14  
**Session Type**: Strategic Alignment & Sprint Planning  
**Participants**: User + AI Assistant  
**Context**: Note Lifecycle Status Management Fix

---

## 📊 Current State Assessment

### ✅ What's Working (Foundation Complete)
1. **Architecture Clean** (ADR-001 + ADR-004 complete)
   - WorkflowManager refactored into 4 focused managers
   - 10 dedicated CLIs extracted (avg 400 LOC each)
   - Zero monolithic code remaining
   
2. **Directory Organization System** (P0+P1 complete Sept 2025)
   - DirectoryOrganizer with backup/rollback
   - Link preservation validated
   - 30 files identified for safe moves (dry-run complete)

3. **Testing Infrastructure** (300x faster)
   - Fast unit tests (<2s)
   - Integration tests with vault factories
   - Contract tests prevent interface mismatches

### 🔴 Critical Gap Identified (Oct 13, 2025)
**Problem**: 77 notes stuck in `Inbox/` with `ai_processed: true` but `status: inbox`

**Root Cause**: `process_inbox_note()` adds AI metadata but never updates status field

**Impact**: 
- Weekly review shows same notes repeatedly
- Cannot distinguish processed from unprocessed notes
- Entire workflow automation chain blocked

---

## 🎯 Strategic Questions for Alignment

### Question 1: Sequencing Priority
**Option A**: Fix code first (status update), then move files  
**Option B**: Move files first (30 notes), then fix code  
**Option C**: Parallel tracks (move + fix simultaneously)

**Current Recommendation**: **Option A** (Fix code first)
- Reason: Code fix is 30 minutes, moves can happen anytime
- Benefit: Tests prevent regressions before touching files
- Risk mitigation: Status updates validate correctly before bulk operations

**Your preference?** ⬜ A  ⬜ B  ⬜ C  ⬜ Other: _______________

---

### Question 2: Testing Strategy
**Option A**: Unit tests only (offline-safe, <2s)  
**Option B**: Unit + integration tests (with temp vault)  
**Option C**: Unit + integration + real vault smoke test

**Current Recommendation**: **Option B** (Unit + integration)
- Reason: Proven fast with vault factories (1.35s)
- Benefit: Complete confidence without touching production
- Coverage: Tests status update, timestamp, idempotence

**Your preference?** ⬜ A  ⬜ B  ⬜ C

---

### Question 3: Scope for This Sprint
**Minimal (P0 only)**: Status update fix + tests (30-60 min)  
**Standard (P0+P1)**: + literature_dir init + promote_note() enhancement (2-3 hours)  
**Complete (P0+P1+P2)**: + auto_promote_ready_notes() + CLI (4-5 hours)

**Current Recommendation**: **Standard (P0+P1)**
- Reason: P0 alone leaves directory integration incomplete
- Benefit: Enables all three note types (permanent/literature/fleeting)
- Natural stopping point: Complete directory integration

**Your preference?** ⬜ Minimal  ⬜ Standard  ⬜ Complete

---

## 📋 Recommended PBI Breakdown

### Epic: Note Lifecycle Status Management
**Goal**: Enable automatic status progression through workflow stages

---

### PBI-001: Fix Status Update Bug (P0 - CRITICAL)
**Priority**: P0 - Blocks all workflow automation  
**Estimate**: 30-60 minutes  
**Value**: Unblocks 77 stuck notes, enables weekly review

**User Stories**:
- As a user processing inbox notes, I want `status: promoted` set after AI processing so notes don't get stuck in inbox
- As a maintainer, I want offline-safe unit tests so CI catches regressions without network calls

**Acceptance Criteria**:
- [ ] `process_inbox_note()` sets `status: promoted` and `processed_date` timestamp
- [ ] Unit test: Status updates persist to disk (offline-safe, <2s)
- [ ] Unit test: Status only updates on success (error path leaves `status: inbox`)
- [ ] Unit test: Idempotent (re-running doesn't create duplicate timestamps)
- [ ] Integration test: Real vault with temp note validates end-to-end

**Technical Tasks**:
1. Add status update in `workflow_manager.py::process_inbox_note()` (3 lines)
2. Write failing unit test (RED phase)
3. Implement minimal fix (GREEN phase)
4. Add timestamp and error handling (REFACTOR phase)
5. Run full test suite, verify zero regressions
6. Git commit with clear message

**Definition of Done**:
- Code merged to branch `fix/note-lifecycle-status-management`
- All tests passing (unit + integration)
- Lessons learned documented
- Ready for P1 work

---

### PBI-002: Complete Directory Integration (P1 - HIGH)
**Priority**: P1 - Enables literature notes workflow  
**Estimate**: 1-2 hours  
**Value**: All three note types fully supported

**User Stories**:
- As a literature reader, I want `Literature Notes/` directory initialized so promotion works
- As a user promoting notes, I want `promote_note()` to handle all three types consistently

**Acceptance Criteria**:
- [ ] `self.literature_dir` initialized in `WorkflowManager.__init__()`
- [ ] `promote_note()` accepts `target_type` parameter: `permanent | literature | fleeting`
- [ ] All promotions set `status: published` and `promoted_date`
- [ ] DirectoryOrganizer integration provides backup/rollback for all types
- [ ] Unit tests for each promotion path
- [ ] Integration test validates moves preserve links

**Technical Tasks**:
1. Add `self.literature_dir` to `__init__()` (2 lines)
2. Refactor `promote_note()` to route by type (20 lines)
3. Add status update logic for all paths
4. Write tests for each note type
5. Validate with DirectoryOrganizer integration test

**Definition of Done**:
- All directory paths consistently defined
- Promotion works for permanent/literature/fleeting
- Tests validate all three pathways
- Documentation updated

---

### PBI-003: Execute Safe File Moves (P1 - OPERATIONAL)
**Priority**: P1 - Clean up existing state  
**Estimate**: 30 minutes execution + review  
**Value**: 30 notes moved to correct directories

**User Stories**:
- As a user, I want misplaced notes moved to their correct directories based on frontmatter
- As an operator, I want backup + validation so I can rollback if needed

**Acceptance Criteria**:
- [ ] Preview command shows detailed move plan (30 files, 0 conflicts)
- [ ] Execution creates backup at `~/backups/knowledge/knowledge-YYYYMMDD-HHMMSS/`
- [ ] All 30 files moved to correct directories based on `type:` field
- [ ] Post-move validation passes (file system + link integrity)
- [ ] JSON output saved for documentation

**Technical Tasks**:
1. Run preview command to inspect moves
2. Execute `DirectoryOrganizer.execute_with_validation()`
3. Review JSON output and validate moves in file browser
4. Document backup path and validation results
5. Optional: Fix 1-2 malformed YAML files if time permits

**Definition of Done**:
- 30 files in correct directories
- Backup preserved for rollback if needed
- Validation results documented
- No broken links introduced

---

### PBI-004: Auto-Promotion System (P2 - ENHANCEMENT)
**Priority**: P2 - Nice to have, enables full automation  
**Estimate**: 2-3 hours  
**Value**: Automatic promotion of high-quality notes

**User Stories**:
- As an operator, I want `auto_promote_ready_notes()` to move high-quality notes automatically
- As a CLI user, I want `--auto-promote` command with quality threshold and preview

**Acceptance Criteria**:
- [ ] `auto_promote_ready_notes(min_quality=0.7, preview=False)` method implemented
- [ ] Selects notes with `status: promoted` and quality >= threshold
- [ ] Preview mode shows candidates with reasons (type, quality score, connections)
- [ ] Execute mode moves files and sets `status: published`
- [ ] CLI integration: `python3 core_workflow_cli.py . auto-promote --quality 0.7 --preview`
- [ ] Offline-safe (uses existing metadata, no AI calls)

**Technical Tasks**:
1. Implement `auto_promote_ready_notes()` method
2. Add quality threshold filtering
3. Integrate with `promote_note()` for safe moves
4. Add CLI command to core_workflow_cli.py
5. Write unit tests for filtering logic
6. Write integration test for end-to-end flow

**Definition of Done**:
- Auto-promotion works with quality threshold
- Preview shows clear promotion rationale
- CLI command documented and tested
- Weekly review can recommend auto-promotion

---

### PBI-005: Repair Orphaned Notes (P3 - CLEANUP)
**Priority**: P3 - Technical debt cleanup  
**Estimate**: 1 hour  
**Value**: Fix 77 existing orphaned notes

**User Stories**:
- As a maintainer, I want a repair script to fix orphaned notes (ai_processed: true, status: inbox)
- As an operator, I want validation to confirm repairs are correct

**Acceptance Criteria**:
- [ ] Script identifies 77 orphaned notes
- [ ] Updates status to `promoted` for all with `ai_processed: true`
- [ ] Adds `processed_date` based on file modification time
- [ ] Dry-run mode shows changes before applying
- [ ] Validation confirms all repairs successful

**Technical Tasks**:
1. Create `repair_orphaned_status.py` script
2. Scan vault for `ai_processed: true` + `status: inbox`
3. Update status and add timestamp
4. Add dry-run and verbose logging
5. Run on real vault with backup

**Definition of Done**:
- 77 orphaned notes repaired
- Script documented and added to maintenance toolkit
- Future notes won't become orphaned (due to PBI-001 fix)

---

## 🎯 Recommended Sprint Plan

### Sprint Goal
Fix critical status update bug and complete directory integration to enable full note lifecycle automation.

### Sprint Scope (4-6 hours total)
- **PBI-001**: Fix Status Update Bug (P0) - 60 min
- **PBI-002**: Complete Directory Integration (P1) - 90 min
- **PBI-003**: Execute Safe File Moves (P1) - 30 min
- **PBI-005**: Repair Orphaned Notes (P3) - 60 min

**Deferred to Next Sprint**:
- **PBI-004**: Auto-Promotion System (P2) - 2-3 hours

### Sprint Structure (TDD Iteration Pattern)
Each PBI follows RED → GREEN → REFACTOR → COMMIT → DOCUMENT

**Iteration 1** (PBI-001): Status Update Fix
- RED: Write failing unit test for status update
- GREEN: Add 3 lines to set status and timestamp
- REFACTOR: Add error handling and idempotence
- COMMIT: "fix: Update status to promoted after AI processing"
- DOCUMENT: Lessons learned

**Iteration 2** (PBI-002): Directory Integration
- RED: Write tests for literature promotion
- GREEN: Add literature_dir initialization
- REFACTOR: Enhance promote_note() for all types
- COMMIT: "feat: Add complete directory integration for all note types"
- DOCUMENT: API changes

**Iteration 3** (PBI-003): File Moves
- VERIFY: Preview detailed move plan
- EXECUTE: Run with full validation
- VALIDATE: Confirm moves and backup
- COMMIT: "chore: Move 30 notes to correct directories"
- DOCUMENT: Move results and backup path

**Iteration 4** (PBI-005): Repair Script
- RED: Test script on sample notes
- GREEN: Implement repair logic
- REFACTOR: Add dry-run and logging
- COMMIT: "feat: Add repair script for orphaned status"
- DOCUMENT: Repair results

---

## 📊 Success Metrics

### Before Sprint
- Notes with `status: inbox`: 77 (stuck)
- Notes with `status: promoted`: <5
- Notes in correct directories: ~80%
- Weekly review effectiveness: Low (shows same notes)

### After Sprint (Target)
- Notes with `status: inbox`: ~10 (new captures only)
- Notes with `status: promoted`: 10-20 (processed, awaiting promotion)
- Notes with `status: published`: 60-70 (in correct directories)
- Notes in correct directories: 100%
- Weekly review effectiveness: High (accurate triage)

### Quality Gates
- ✅ All tests passing (unit + integration)
- ✅ Zero regressions in existing workflows
- ✅ Backup created and validated for file moves
- ✅ Documentation complete (lessons learned, API changes)
- ✅ CI-ready (offline-safe tests <2s)

---

## 🤔 Decision Points for You

### 1. Sprint Scope Selection
**Which scope feels right for this sprint?**
- [ ] **Minimal** (PBI-001 only) - 60 min, quick win
- [ ] **Standard** (PBI-001 + PBI-002) - 2.5 hours, complete foundation
- [ ] **Extended** (PBI-001 + PBI-002 + PBI-003 + PBI-005) - 4-6 hours, clean slate ⭐ RECOMMENDED
- [ ] **Full** (All PBIs including auto-promotion) - 7-9 hours

### 2. Testing Preference
**How thorough should tests be?**
- [ ] Unit tests only (fast iteration)
- [ ] Unit + integration (recommended) ⭐
- [ ] Unit + integration + smoke tests (maximum confidence)

### 3. File Moves Timing
**When should we execute the 30 file moves?**
- [ ] Before code changes (clean slate first)
- [ ] After code changes (validate fix works first) ⭐ RECOMMENDED
- [ ] Skip for now (focus on code only)

### 4. Documentation Level
**How detailed should documentation be?**
- [ ] Minimal (commit messages only)
- [ ] Standard (lessons learned per iteration) ⭐ RECOMMENDED
- [ ] Comprehensive (lessons + API docs + migration guide)

---

## 🚀 Immediate Next Actions

Based on your answers above, we'll:

1. **Create branch**: `fix/note-lifecycle-status-management`
2. **Start with PBI-001**: Fix status update bug (RED phase)
3. **Follow TDD cycle**: RED → GREEN → REFACTOR for each PBI
4. **Track progress**: Update this document as we complete PBIs
5. **Document learnings**: Capture lessons learned per iteration

---

## 📝 Sprint Tracking Template

### Iteration Status
- [ ] **PBI-001**: Status Update Fix - 🔴 Not Started
- [ ] **PBI-002**: Directory Integration - 🔴 Not Started
- [ ] **PBI-003**: File Moves - 🔴 Not Started
- [ ] **PBI-005**: Repair Script - 🔴 Not Started

### Progress Indicators
- 🔴 Not Started
- 🟡 In Progress (RED phase)
- 🟢 Tests Passing (GREEN phase)
- 🔵 Refactored & Committed
- ✅ Complete with Documentation

---

## 💬 Your Input Needed

**Please respond with your preferences for:**
1. Sprint scope (Minimal/Standard/Extended/Full)
2. Testing level (Unit only / Unit+Integration / Full coverage)
3. File moves timing (Before code / After code / Skip)
4. Documentation level (Minimal / Standard / Comprehensive)

**Or simply say**: "Start with recommended approach" and we'll proceed with:
- Extended scope (PBI-001 through PBI-005)
- Unit + integration tests
- File moves after code fixes
- Standard documentation

---

## ✅ DECISION RECORDED (Oct 14, 2025 17:06 PDT)

**User Decision**: "I really want auto-promotion, to enable flow"

### Sprint Scope: FULL ✅
- ✅ **PBI-001**: Status Update Bug Fix (P0) - 60 min
- ✅ **PBI-002**: Complete Directory Integration (P1) - 90 min  
- ✅ **PBI-004**: Auto-Promotion System (P2) ⭐ - 2-3 hours
- ✅ **PBI-003**: Execute Safe File Moves (P1) - 30 min
- ✅ **PBI-005**: Repair Orphaned Notes (P3) - 60 min

**Total Timeline**: 6-8 hours  
**Testing Level**: Unit + Integration (recommended)  
**File Moves Timing**: After code fixes (recommended)  
**Documentation Level**: Standard (lessons learned per iteration)

### Sprint Goal Confirmed
Transform InnerOS from semi-automated tool → **true flow system** with quality-gated auto-promotion enabling hands-off knowledge processing.

### Success Criteria
- All 77 stuck notes resolved
- Auto-promotion operational (quality threshold: 0.7)
- Zero regressions in existing workflows
- Complete TDD coverage (unit + integration)
- Documentation complete

---

**Ready to begin when you are!** 🚀
