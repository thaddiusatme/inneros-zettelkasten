---
type: bug-report
created: 2025-10-29 09:55
status: active
priority: P0
tags: [ci-cd, test-failures, post-public-repo]
related: [project-todo-v5.md]
---

# CI Test Failures Report - Post-Public Repo Migration

**Date**: 2025-10-29 09:55 PDT
**CI Run**: [#18915166798](https://github.com/thaddiusatme/inneros-zettelkasten/actions/runs/18915166798)
**Duration**: 11m 26s (within 20min timeout ✅)
**Result**: ❌ **296 failed, 1245 passed, 83 skipped, 65 errors**

---

## 🎯 Executive Summary

After making the repository public (removing `knowledge/` folder), CI tests are failing due to:

1. **Missing files** (100 FileNotFoundErrors) - Tests reference removed `knowledge/` content
2. **Missing imports** (110 ModuleNotFoundErrors + 103 ImportErrors) - Module structure issues
3. **Assertion failures** (174) - Logic errors exposed by missing dependencies
4. **API compatibility** (5+ failures) - YouTube API version mismatches

**Good News**: Timeout fix works! Tests completed in 11m26s (was timing out at 10min).

---

## 📊 Failure Categories

### Category 1: Missing Module - `monitoring.metrics_collector` ⚠️ **CRITICAL**
**Count**: 55 errors
**Root Cause**: Module doesn't exist or isn't importable
**Affected Files**:
- Multiple test files trying to import monitoring metrics

**Impact**: Blocks many tests from even starting

**Fix Priority**: **P0 - Blocker**

---

### Category 2: Missing LlamaVisionOCR Import ⚠️ **HIGH**
**Count**: 41+ errors
**Root Cause**: `LlamaVisionOCR` class missing from `src.cli.evening_screenshot_utils`
**Affected Test Files**:
- `test_evening_screenshot_real_data_tdd_3.py` (15 failures)
- `test_enhanced_ai_cli_integration_tdd_iteration_6.py` (15 failures)
- `test_individual_screenshot_processing_tdd_5.py` (11 failures)
- `test_samsung_capture_centralized_storage_tdd_11.py` (9 failures)
- `test_screenshot_batch_individual_files_tdd_8.py` (6 failures)
- `test_evening_screenshot_cli_tdd_4.py` (9 failures)
- `test_evening_screenshot_cli_tdd_2.py` (5 failures)

**Impact**: Blocks 70+ screenshot/OCR-related tests

**Fix Priority**: **P0 - Blocker**

---

### Category 3: Missing knowledge/ Template Files ⚠️ **HIGH**
**Count**: 100 FileNotFoundErrors (estimated from error type count)
**Root Cause**: Tests reference `knowledge/Templates/youtube-video.md` which was removed
**Affected Areas**:
- YouTube template approval tests
- Web UI template tests  
- Weekly review template tests

**Error Pattern**:
```
FileNotFoundError: [Errno 2] No such file or directory: 
'/home/runner/work/inneros-zettelkasten/inneros-zettelkasten/knowledge/Templates/youtube-video.md'
```

**Affected Test Files**:
- `test_youtube_template_approval.py` - Multiple tests
- Web UI tests expecting template files
- Weekly review compatibility tests

**Impact**: Blocks ~65+ template-related test errors

**Fix Priority**: **P1 - High**

---

### Category 4: YouTube API Compatibility Issues ⚠️ **MEDIUM**
**Count**: 5 failures
**Root Cause**: YouTube transcript API version mismatch
**Affected File**: `test_youtube_transcript_fetcher.py`

**Errors**:
1. `AttributeError: 'YouTubeTranscriptApi' object has no attribute 'list'`
2. `ImportError: cannot import name 'RequestBlocked' from 'youtube_transcript_api._errors'`

**Impact**: YouTube transcript functionality tests fail

**Fix Priority**: **P2 - Medium**

---

### Category 5: Enhanced AI Feature Test Failures
**Count**: 23 failures in `test_enhanced_ai_features_tdd_iteration_5.py`
**Root Cause**: Unknown - needs investigation
**Impact**: Advanced tag enhancement tests failing

**Fix Priority**: **P2 - Medium** (investigate after blockers cleared)

---

### Category 6: CLI Integration Failures
**Count**: 21 failures in `test_advanced_tag_enhancement_cli.py`
**Root Cause**: Unknown - likely cascading from Category 1/2
**Impact**: CLI tests failing

**Fix Priority**: **P2 - Medium** (may resolve after P0 fixes)

---

### Category 7: Automation Test Failures
**Count**: 16 failures in `automation/test_youtube_handler.py`
**Root Cause**: Mock objects missing `youtube_handler` attribute
**Error**: `AttributeError: 'MockDaemon' object has no attribute 'youtube_handler'`

**Impact**: YouTube automation tests failing

**Fix Priority**: **P2 - Medium**

---

### Category 8: Assertion Failures
**Count**: 174 AssertionErrors (mixed)
**Root Cause**: Various logic failures, many cascading from import/file errors
**Impact**: Test logic failures across multiple areas

**Fix Priority**: **P3 - Low** (address after structural issues fixed)

---

## 📋 Actionable Todo List

### Phase 1: Critical Blockers (P0) - Unblock Test Execution

- [ ] **TASK 1.1**: Fix `monitoring.metrics_collector` module
  - **Action**: Investigate why module doesn't exist or isn't importable
  - **Files**: Search for monitoring/metrics_collector references
  - **Estimate**: 30 minutes
  - **Blocks**: 55 test errors

- [ ] **TASK 1.2**: Fix `LlamaVisionOCR` import in `evening_screenshot_utils`
  - **Action**: Add missing class or fix import path
  - **Files**: `development/src/cli/evening_screenshot_utils.py`
  - **Estimate**: 1 hour
  - **Blocks**: 70+ screenshot tests

**Phase 1 Goal**: Reduce errors from 361 to ~236 (reduce by 35%)

---

### Phase 2: High Priority (P1) - Fix Template Dependencies

- [ ] **TASK 2.1**: Create test fixtures for template files
  - **Action**: Move templates to `development/tests/fixtures/templates/`
  - **Files**: 
    - Create `youtube-video.md` template fixture
    - Update test imports to use fixtures
  - **Estimate**: 1-2 hours
  - **Fixes**: ~65 template-related errors

- [ ] **TASK 2.2**: Update Web UI tests to use fixture templates
  - **Action**: Refactor web UI tests to mock or use fixtures
  - **Files**: Multiple web UI test files
  - **Estimate**: 1 hour
  - **Fixes**: ~35 web UI test errors

**Phase 2 Goal**: Reduce errors from 236 to ~136 (reduce by 42%)

---

### Phase 3: Medium Priority (P2) - API & Integration Fixes

- [ ] **TASK 3.1**: Fix YouTube API compatibility
  - **Action**: Update test mocks to match current API version
  - **Files**: `test_youtube_transcript_fetcher.py`
  - **Estimate**: 30 minutes
  - **Fixes**: 5 YouTube API failures

- [ ] **TASK 3.2**: Fix Mock Daemon `youtube_handler` attribute
  - **Action**: Add missing attribute to MockDaemon class
  - **Files**: `automation/test_youtube_handler.py`, mock fixtures
  - **Estimate**: 20 minutes
  - **Fixes**: 16 automation test failures

- [ ] **TASK 3.3**: Investigate enhanced AI feature failures
  - **Action**: Review `test_enhanced_ai_features_tdd_iteration_5.py` failures
  - **Files**: Enhanced AI test suite
  - **Estimate**: 1 hour
  - **Fixes**: 23 enhanced AI failures

- [ ] **TASK 3.4**: Investigate CLI integration failures
  - **Action**: Check if resolved by P0/P1 fixes, otherwise debug
  - **Files**: `test_advanced_tag_enhancement_cli.py`
  - **Estimate**: 1 hour (if not auto-resolved)
  - **Fixes**: 21 CLI test failures

**Phase 3 Goal**: Reduce errors from 136 to ~71 (reduce by 48%)

---

### Phase 4: Low Priority (P3) - Assertion Logic Fixes

- [ ] **TASK 4.1**: Review and fix remaining AssertionErrors
  - **Action**: Investigate remaining logic failures
  - **Estimate**: 2-4 hours (spread across multiple sessions)
  - **Fixes**: Remaining 71 assertion failures

**Phase 4 Goal**: Achieve ✅ **All tests passing**

---

## 📈 Success Metrics

### Current State
- ❌ 296 failures (16% pass rate)
- ❌ 65 errors (setup failures)
- ✅ 1245 passing
- ⏭️  83 skipped

### Target State (After All Phases)
- ✅ 0 failures (100% pass rate for non-skipped tests)
- ✅ 0 errors
- ✅ 1600+ passing (estimate after fixing blockers)
- ⏭️  ~80 skipped (slow tests marked in previous fixes)

---

## 🔍 Investigation Commands

### Check specific failure details:
```bash
# Get full logs for a specific test file
gh run view 18915166798 --log 2>&1 | grep "test_enhanced_ai_features"

# Count errors by type
gh run view 18915166798 --log 2>&1 | grep -oE "(ModuleNotFoundError|ImportError|FileNotFoundError)" | sort | uniq -c

# Find all files with specific error
gh run view 18915166798 --log 2>&1 | grep "LlamaVisionOCR"
```

### Run tests locally:
```bash
# Run specific failing test file
PYTHONPATH=development python3 -m pytest development/tests/unit/test_enhanced_ai_features_tdd_iteration_5.py -v

# Run with specific marker
make unit  # Skips slow tests
make unit-all  # Runs everything including slow
```

---

## 🎯 Recommended Approach

**Start with**: Phase 1 (Critical Blockers)
- Fixing the 2 P0 blockers will unblock 125+ tests (35% of failures)
- Quick wins that reveal what's actually broken vs cascading failures

**Then move to**: Phase 2 (Template Dependencies)
- Establishes test fixture pattern for future work
- Fixes 100 failures (28% of total)

**Finally**: Phases 3-4 as time permits
- Many failures may auto-resolve after P0/P1 fixes
- Can be addressed incrementally

---

## 📝 Notes

### What Went Right
- ✅ Timeout fix works (20min sufficient, tests completed in 11m26s)
- ✅ 1245 tests still passing despite major changes
- ✅ Clear failure patterns identified

### Root Cause Analysis
The repository public migration broke tests that:
1. Depended on `knowledge/` directory structure
2. Had incomplete module imports (exposed by CI environment differences)
3. Used outdated API mocks

This is **expected and manageable** post-migration cleanup, not a fundamental architecture problem.

---

## 🔗 Related Documents

- **Parent**: `Projects/ACTIVE/project-todo-v5.md`
- **CI Run**: https://github.com/thaddiusatme/inneros-zettelkasten/actions/runs/18915166798
- **Timeout Fix**: Commits 5e2cd9c, a935616, beb76de

---

**Next Action**: Begin Phase 1 - Task 1.1 (monitoring.metrics_collector fix)
