---
type: session-prompt
created: 2025-10-29 11:45
session: fresh-context
priority: P0
branch: ci-test-fixes-phase-1-blockers
---

# Next Session Prompt: LlamaVisionOCR Import Fix

## The Prompt

Let's continue on branch **ci-test-fixes-phase-1-blockers** for the next feature: **LlamaVisionOCR Import Fix (P0-1.2)**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

## Updated Execution Plan (focused P0 blockers)

**CI Test Failure Recovery - LlamaVisionOCR Missing Import**

I'm following the guidance in `updated-development-workflow.md` and `architectural-constraints.md` (critical path: **unblock 70+ failing screenshot/OCR tests by fixing missing LlamaVisionOCR import**).

### Current Status

**Completed**: 
- ✅ Category 1 Investigation: `monitoring.metrics_collector` module exists, CI config issue (downgraded P0 → P1)
- ✅ Created diagnostic tests: `test_ci_import_compatibility.py` (12 tests, all pass locally)
- ✅ Branch created: `ci-test-fixes-phase-1-blockers`
- ✅ CI failure analysis report updated

**In progress**: 
Task 1.2 - LlamaVisionOCR import fix in `development/src/cli/evening_screenshot_utils.py`

**Lessons from last iteration**: 
- Module existence ≠ CI compatibility - check both local and CI import patterns
- Create diagnostic tests first to confirm module structure
- CI failures may be configuration issues, not missing code
- 12 diagnostic tests caught PYTHONPATH differences between local/CI environments

---

## P0 — Critical Blocker (IMMEDIATE - Unblocks 70+ tests)

**TASK 1.2**: Fix `LlamaVisionOCR` import in evening_screenshot_utils

**Investigation Phase**:
- Search codebase for existing `LlamaVisionOCR` class definition
- Check if class exists in different module (e.g., `src.ai.llama_vision_ocr`)
- Examine import patterns in affected test files:
  - `test_evening_screenshot_real_data_tdd_3.py` (15 failures)
  - `test_enhanced_ai_cli_integration_tdd_iteration_6.py` (15 failures)
  - `test_individual_screenshot_processing_tdd_5.py` (11 failures)
  - `test_samsung_capture_centralized_storage_tdd_11.py` (9 failures)
  - `test_screenshot_batch_individual_files_tdd_8.py` (6 failures)
  - `test_evening_screenshot_cli_tdd_4.py` (9 failures)
  - `test_evening_screenshot_cli_tdd_2.py` (5 failures)

**Implementation Options**:
- **Option A**: Class exists elsewhere - fix import path in `evening_screenshot_utils.py`
- **Option B**: Class was moved/renamed - update to new class name
- **Option C**: Class is missing - create minimal stub or restore from git history
- **Option D**: Class should be imported from OCR module - add proper import chain

**Files to examine**:
- `development/src/cli/evening_screenshot_utils.py` (import location)
- `development/src/ai/` directory (check for vision/OCR related modules)
- Test files listed above (understand expected interface)
- Git history: `git log --all --full-history -- "*llama_vision*"` (check if deleted)

### Acceptance Criteria:
- ✅ `LlamaVisionOCR` class is importable from expected location
- ✅ All 70+ affected test files can import the class
- ✅ Error count reduced from 361 to ~291 (19% reduction)
- ✅ Zero breaking changes to existing passing tests
- ✅ Class interface matches test expectations

---

## P1 — Template Dependencies (DEFERRED - After P0 complete)

**TASK 2.1**: Create test fixtures for template files
- Move templates to `development/tests/fixtures/templates/`
- Create `youtube-video.md` template fixture
- Update 100+ test imports to use fixtures
- **Estimate**: 1-2 hours
- **Fixes**: ~65 template-related errors

**TASK 2.2**: Fix CI PYTHONPATH configuration
- Update `.github/workflows/ci.yml` with correct PYTHONPATH
- Verify `monitoring.metrics_collector` imports work in CI
- Run diagnostic tests in CI environment
- **Estimate**: 30 minutes
- **Fixes**: 55 monitoring import errors

### Acceptance Criteria:
- ✅ Zero tests reference removed `knowledge/` directory
- ✅ CI imports work consistently with local environment
- ✅ Error count reduced from ~291 to ~136 (53% reduction)

---

## P2 — Integration Cleanup (DEFERRED)

**TASK 3.1**: Fix YouTube API compatibility (5 failures)
**TASK 3.2**: Fix MockDaemon youtube_handler attribute (16 failures)
**TASK 3.3**: Investigate enhanced AI feature failures (23 failures)

---

## Task Tracker

- [x] **P0-1.1** - Investigate monitoring.metrics_collector (✅ COMPLETE - downgraded to P1 config issue)
- [In progress] **P0-1.2** - Fix LlamaVisionOCR import (70+ errors) ← **START HERE**
- [Pending] **P1-2.1** - Create test fixtures for templates (65 errors)
- [Pending] **P1-2.2** - Fix CI PYTHONPATH configuration (55 errors)
- [Pending] **P2-3.1** - Fix YouTube API compatibility (5 errors)
- [Pending] **P2-3.2** - Fix MockDaemon youtube_handler (16 errors)

---

## TDD Cycle Plan

### Red Phase:
- Write failing test that reproduces the `LlamaVisionOCR` import error
- Create test demonstrating expected class interface (analyze_screenshot method)
- Document the expected module location and import path
- Test should fail with clear ModuleNotFoundError or ImportError

### Green Phase:
- Minimal implementation based on investigation findings:
  - **If class exists**: Fix import path in evening_screenshot_utils.py
  - **If class missing**: Create minimal LlamaVisionOCR stub with analyze_screenshot method
  - **If moved**: Update import chain to new location
- Implement only methods required to pass import and instantiation tests

### Refactor Phase:
- Verify all 70+ affected test files can import successfully
- Add proper error handling for missing OCR dependencies
- Ensure class follows project architectural patterns
- Add type hints and docstrings

### Commit & Documentation:
- Git commit with detailed explanation of fix
- Update lessons learned: document why class was missing/mislocated
- Update CI failure report with resolution details
- Document prevention strategy for future module imports

---

## Next Action (for this session)

**Immediate task**: Investigate `LlamaVisionOCR` class location and import pattern

1. **Search codebase for class definition**:
   ```bash
   grep -r "class LlamaVisionOCR" development/
   find development/ -name "*llama*" -o -name "*vision*ocr*"
   ```

2. **Check import in evening_screenshot_utils.py**:
   ```bash
   cat development/src/cli/evening_screenshot_utils.py | grep -A5 -B5 "LlamaVisionOCR"
   ```

3. **Examine affected test files to understand expected interface**:
   ```bash
   grep -A10 "LlamaVisionOCR" development/tests/unit/test_evening_screenshot_real_data_tdd_3.py
   ```

4. **Check git history for class movement/deletion**:
   ```bash
   git log --all --full-history -- "*llama_vision*"
   git log --all --full-history -- "*LlamaVisionOCR*"
   ```

**Decision point**: Based on investigation, determine:
- Does class exist? Where?
- Was it deleted? When and why?
- What's the expected interface?
- What import path should work?

**Files to examine**:
- `development/src/cli/evening_screenshot_utils.py` (current import location)
- `development/src/ai/` (likely module location)
- `development/tests/unit/test_evening_screenshot_*.py` (expected interface)

Would you like me to begin with **searching the codebase for LlamaVisionOCR class definition** and determining the root cause of the missing import?

---

## Context References

- **CI Failure Report**: `Projects/ACTIVE/ci-failure-report-2025-10-29.md`
- **Branch**: `ci-test-fixes-phase-1-blockers`
- **Diagnostic Tests**: `development/tests/unit/test_ci_import_compatibility.py` (reference pattern)
- **CI Run**: https://github.com/thaddiusatme/inneros-zettelkasten/actions/runs/18915166798

---

## Success Metrics

**Current**: 361 errors, 296 failures, 1245 passing (71% pass rate)

**After P0-1.2**: ~291 errors, ~226 failures, 1315+ passing (75% pass rate)

**Target State**: 0 errors, 0 failures, 1600+ passing (100% pass rate)
