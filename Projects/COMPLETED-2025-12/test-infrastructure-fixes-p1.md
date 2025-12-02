# Test Infrastructure Fixes (P1) - TDD Iteration 1

**Branch**: `fix/test-infrastructure-collection-p1`  
**Priority**: P1 (Blocking Full CI Enforcement)  
**Status**: 🔴 RED PHASE  
**Date Started**: 2025-10-27

## 🎯 Objective

Fix pre-existing test collection issues to enable full CI enforcement without `continue-on-error: true`.

## 📊 Current State

### RED Phase Test Results (5/5 Failing ✅)

```bash
cd development && python -m pytest tests/unit/test_test_infrastructure.py -v

FAILED test_all_tests_can_be_collected - Found 6 collection errors
FAILED test_psutil_dependency_available - psutil not installed
FAILED test_evening_screenshot_utils_exports - Missing OneDriveScreenshotDetector
FAILED test_automation_modules_exist - repair_orphaned_notes module not found
FAILED test_no_duplicate_test_files - test_cli_imports.py exists in 2 locations
```

### Identified Issues

#### 1. Missing psutil Dependency ⚠️
**Files Affected**:
- `src/cli/automation_status_cli.py` (line 6)
- `src/cli/real_data_performance_validator.py` (line 12)

**Fix**: Add `psutil>=5.9.0` to `requirements.txt`

#### 2. Evening Screenshot Import Errors ⚠️
**Files Affected**:
- `tests/unit/test_evening_screenshot_processor_tdd_1.py`
- `tests/unit/test_evening_screenshot_processor_green_phase.py`

**Issue**: Importing non-existent classes from `evening_screenshot_utils.py`:
- `OneDriveScreenshotDetector`
- `ScreenshotOCRProcessor`
- `DailyNoteGenerator`
- `SmartLinkIntegrator`
- `SafeScreenshotManager`

**Fix Options**:
1. Skip these tests with `@pytest.mark.skip` (quick fix for CI)
2. Implement stub classes (medium fix)
3. Complete the implementation (long-term fix, separate project)

#### 3. Missing Automation Module ⚠️
**File Affected**: `tests/unit/automation/test_repair_orphaned_notes.py`

**Issue**: Imports `src.automation.repair_orphaned_notes` which doesn't exist

**Fix Options**:
1. Skip the test (quick fix)
2. Create stub module (medium fix)
3. Implement the feature (long-term, separate project)

#### 4. Duplicate Test Files ⚠️
**Conflict**:
- `/tests/unit/test_cli_imports.py`
- `/tests/unit/cli/test_cli_imports.py`

**Issue**: pytest can't handle duplicate test file names in different directories

**Fix**: Rename or consolidate to eliminate duplication

## 🎯 TDD Cycle Plan

### RED Phase ✅ COMPLETE
- [x] Created `test_test_infrastructure.py` with 5 comprehensive tests
- [x] All 5 tests failing as expected
- [x] Documented all issues in this manifest

### GREEN Phase (Next)
- [ ] Add `psutil>=5.9.0` to `requirements.txt`
- [ ] Skip evening_screenshot tests with clear markers
- [ ] Skip repair_orphaned_notes test with clear marker
- [ ] Resolve duplicate test_cli_imports.py
- [ ] Verify all 5 tests pass

### REFACTOR Phase
- [ ] Add comprehensive docstrings explaining skipped tests
- [ ] Update CI workflow (remove `continue-on-error: true`)
- [ ] Verify full CI enforcement works
- [ ] Clean up any temporary workarounds

### COMMIT Phase
- [ ] Git commit with detailed message
- [ ] Update PR #7 with fixes
- [ ] Verify CI passes

### LESSONS Phase
- [ ] Document lessons learned
- [ ] Update project-todo-v4.md
- [ ] Create follow-up tasks for skipped implementations

## 🎯 Success Criteria

- [ ] `make unit` runs without collection errors (exit code 0)
- [ ] All unit tests pass or are properly skipped (no collection failures)
- [ ] CI workflow enforces unit tests (no `continue-on-error`)
- [ ] PR #7 updated and CI passes with full enforcement

## 📋 Follow-up Tasks (Post-Iteration)

These issues need separate TDD iterations:

1. **Evening Screenshot Processor Implementation**
   - Priority: P2
   - Estimated: 2-3 TDD iterations
   - Blocked by: User requirements clarification

2. **Repair Orphaned Notes Feature**
   - Priority: P3
   - Estimated: 1-2 TDD iterations
   - May be deprecated if not needed

## 📊 Performance Targets

- Test collection: <5 seconds
- Full unit test suite: <60 seconds (current: varies)
- CI workflow: <5 minutes total

## 🔗 Related Documentation

- `.windsurf/rules/updated-development-workflow.md` - TDD methodology
- `Projects/ACTIVE/project-todo-v4.md` - Current execution plan
- `.github/workflows/ci.yml` - CI workflow configuration
- `.github/workflows/ci-lite.yml` - Fast checks workflow

---

**Next Action**: Move to GREEN phase - fix issues to make tests pass
