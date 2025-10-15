# ADR-002 Phase 5: Extraction Target Analysis

**Date**: 2025-10-14  
**Status**: Decision Phase  
**Current WorkflowManager**: 2,107 LOC

## Extraction Options Analysis

### Option A: Review/Triage Engine ⭐ **RECOMMENDED**

**Estimated LOC**: ~371 lines (17.6% of WorkflowManager)

**Methods to Extract** (11 total):
1. `scan_review_candidates()` - 30 LOC
2. `_scan_directory_for_candidates()` - 40 LOC
3. `_create_candidate_dict()` - 23 LOC
4. `generate_weekly_recommendations()` - 26 LOC
5. `_initialize_recommendations_result()` - 22 LOC
6. `_process_candidate_for_recommendation()` - 35 LOC
7. `_create_error_recommendation()` - 22 LOC
8. `_update_summary_counts()` - 15 LOC
9. `_extract_weekly_recommendation()` - 38 LOC
10. `generate_fleeting_triage_report()` - 95 LOC
11. `_find_fleeting_notes()` - 25 LOC

**Cohesion Analysis**:
- ✅ High cohesion - all methods work together for review/triage
- ✅ Two main workflows: Weekly Review + Fleeting Triage
- ✅ Clear single responsibility: "Review and Triage Coordination"
- ✅ Independent from promotion, connection, analytics

**Benefits**:
- Largest single extraction remaining
- Brings WorkflowManager from 2,107 → ~1,736 LOC (progress to 68%)
- Natural separation of concerns
- Well-established in production (Phase 5.5 features)
- Clear integration points with existing coordinators

**Integration Points**:
- Uses `process_inbox_note()` from WorkflowManager
- Independent of NoteLifecycleManager, ConnectionCoordinator, AnalyticsCoordinator, PromotionEngine
- Consumed by CLI layer (`workflow_demo.py`)

**Test Coverage**:
- Existing tests in `test_workflow_manager.py` for weekly review
- Existing tests for fleeting triage
- Estimate: 15-18 tests needed for comprehensive coordinator coverage

---

### Option B: Template/Metadata Handler

**Estimated LOC**: ~61 lines (2.9% of WorkflowManager)

**Methods to Extract**:
1. `_preprocess_created_placeholder_in_raw()` - 61 LOC

**Issues**:
- ❌ Much smaller than expected (~250 LOC estimate was incorrect)
- ❌ Only one primary method found
- ❌ Low impact on overall LOC reduction
- ❌ Would only bring progress from 53% → 56%

**Benefits**:
- ✅ Would address 4 failing WorkflowManager tests related to template processing
- ✅ Cleans up scattered functionality

**Decision**: Not recommended due to low LOC impact

---

## Final Recommendation: Review/Triage Engine

**Rationale**:
1. **High Impact**: 371 LOC extraction (17.6% reduction)
2. **Clear Cohesion**: 11 methods with single responsibility
3. **Natural Boundaries**: Well-defined integration points
4. **Progress**: Brings us from 53% → 68% toward <500 LOC goal
5. **Production Proven**: Features already in use (Phase 5.5)

**Proposed Class Name**: `ReviewTriageCoordinator`

**Proposed Methods**:
- `scan_review_candidates()` - Public API
- `generate_weekly_recommendations()` - Public API
- `generate_fleeting_triage_report()` - Public API
- 8 private helper methods for internal logic

**Expected Progress**:
- Before: 2,107 LOC (53% progress to goal)
- After: ~1,736 LOC (68% progress to goal)
- Remaining: 2-3 more phases to reach <500 LOC

**Next Phase Preview**:
After Phase 5, remaining candidates:
- Template/Metadata Handler (~61 LOC)
- Any remaining scattered utility methods
- Final cleanup to reach <500 LOC target

---

## Decision

✅ **Proceed with Review/Triage Engine extraction**

**Branch**: `feat/adr-002-phase-5-review-triage-extraction` (already created)
**Target LOC**: ~371 lines
**Expected Tests**: 15-18 comprehensive tests
**Timeline**: 2-3 hour TDD cycle (RED → GREEN → REFACTOR → COMMIT → LESSONS)
