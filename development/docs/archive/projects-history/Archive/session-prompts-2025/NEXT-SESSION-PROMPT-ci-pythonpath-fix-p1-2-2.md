---
type: session-prompt
created: 2025-10-29
task: P1-2.2
branch: ci-test-fixes-phase-1-blockers
priority: P1-High
---

# Next Session Prompt: CI Test Fixes - PYTHONPATH Configuration (P1-2.2)

Continue work on branch `ci-test-fixes-phase-1-blockers`. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

## Updated Execution Plan (CI Test Fixes Phase 1)

**CI Run**: https://github.com/thaddiusatme/inneros-zettelkasten/actions/runs/18915166798  
**Current Error Count**: ~226 errors projected (down from 361, 37% reduction achieved)

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` (critical path: CI PYTHONPATH configuration for 17+ ImportError failures).

## Current Status

### Completed
- ✅ **P0-1.1**: monitoring.metrics_collector investigation (commit investigation phase)
  - Module exists locally, CI config issue identified
  - Priority downgraded: P0 → P1 (configuration, not missing code)
  
- ✅ **P0-1.2**: LlamaVisionOCR import fix (commit `38f623b`)
  - Added `llama_vision_ocr` to `src/ai/__init__.py` exports
  - Fixed import path in `src/cli/screenshot_utils.py:151`
  - **Impact**: 70+ tests unblocked, 19% error reduction (361 → 291 errors)
  
- ✅ **P1-2.1**: Template fixtures infrastructure (commit `a30703e`)
  - Created `development/tests/fixtures/templates/` with 13 templates
  - Built `template_loader.py` utility (3 functions)
  - Migrated `test_templates_auto_inbox.py` to use fixtures
  - **Impact**: 65+ tests unblocked, 22% error reduction (291 → 226 projected)

### In Progress
**P1-2.2**: Fix monitoring.metrics_collector CI PYTHONPATH

### Lessons from Last Iterations

**P0-1.2 (LlamaVisionOCR)**:
- Module existence ≠ availability without `__all__` export
- TDD diagnostic power: 5-min investigation → 20-min solution
- Minimal fixes maximize impact: 2-line changes unblocked 70+ tests
- Root cause first: Understanding WHY prevented band-aids

**P1-2.1 (Template Fixtures)**:
- Fixture infrastructure scales well with existing patterns
- Format diversity matters: YAML + Templater both supported
- TDD for infrastructure: Tests = clear acceptance criteria
- Selective migration: Not all refs need updating (understand context)
- Pre-existing failures provide value: Confirms migration working

---

## P0 — Critical Blockers (All Complete ✅)

**Status**: P0 phase complete. Both critical import blockers resolved.

**Achievements**:
- 135+ tests unblocked
- 37% error reduction (361 → 226)
- 2 complete TDD iterations in 65 minutes

---

## P1 — Systematic Test Infrastructure (High Priority)

### P1-2.2: Fix metrics_collector CI PYTHONPATH (CURRENT TASK)

**Impact**: 17+ ImportError failures  
**Root Cause**: CI environment can't find `monitoring.metrics_collector` module

**Background**:
- Module exists at `development/src/monitoring/metrics_collector.py`
- All 12 diagnostic tests pass locally with PYTHONPATH=development
- CI workflow doesn't set PYTHONPATH correctly
- Created diagnostic tests in P0-1.1: `test_ci_import_compatibility.py`

**Implementation Strategy**:

1. **Identify CI Workflow Files**:
   - `.github/workflows/ci.yml` (main CI workflow)
   - `.github/workflows/ci-lite.yml` (lightweight CI)
   - Check which workflow runs pytest

2. **Update Workflow PYTHONPATH**:
   ```yaml
   - name: Run tests
     env:
       PYTHONPATH: development
     run: |
       pytest development/tests/
   ```

3. **Alternative Approach** (if needed):
   - Add `conftest.py` at test root to set path
   - Or: Update imports to use relative paths
   - Reference: Existing `development/src/` structure

4. **Verify Fix**:
   - Push changes to branch
   - Trigger CI run
   - Confirm metrics_collector imports work
   - Verify 17+ tests now pass

### P1-2.3: Module Import Standardization

**Impact**: 50+ ModuleNotFoundErrors  
**Strategy**: Apply P0-1.2 lessons to other missing exports

**Investigation Needed**:
- Grep for common import errors in CI logs
- Check which modules missing from `__all__` lists
- Create diagnostic tests like `test_llama_vision_ocr_import_fix.py`

### P1-2.4: Web UI Test Fixtures

**Impact**: ~35 web UI test errors  
**Strategy**: Similar to template fixtures approach

**Acceptance Criteria**:
- ✅ CI workflow updated with PYTHONPATH=development
- ✅ metrics_collector ImportError resolved (17+ → 0)
- ✅ Diagnostic tests pass in CI environment
- ✅ Error count reduced by 7%+ (~226 → ~210)
- ✅ Documentation updated with CI configuration standards

---

## P2 — Test Logic Fixes (Future Sessions)

### P2-3.1: Fix AttributeError Failures
**Count**: ~50 failures  
**Examples**: Missing methods in implementation classes

### P2-3.2: Fix AssertionError Failures
**Count**: ~80 failures  
**Examples**: Sorting issues, data structure mismatches

### P2-3.3: API Compatibility Fixes
**Count**: 5+ failures  
**Example**: YouTube transcript API version mismatch

---

## Task Tracker

- [x] P0-1.1 - monitoring.metrics_collector investigation
- [x] P0-1.2 - LlamaVisionOCR import fix (commit `38f623b`)
- [x] P1-2.1 - Template fixtures infrastructure (commit `a30703e`)
- [ ] **P1-2.2 - CI PYTHONPATH configuration** ← **CURRENT SESSION**
- [ ] P1-2.3 - Module import standardization
- [ ] P1-2.4 - Web UI test fixtures
- [ ] P2-3.1 - AttributeError fixes
- [ ] P2-3.2 - AssertionError fixes

---

## TDD Cycle Plan

### Red Phase

**Objective**: Verify diagnostic tests fail in CI but pass locally

**Steps**:
1. Review existing diagnostic tests from P0-1.1:
   ```bash
   PYTHONPATH=development python3 -m pytest \
     development/tests/unit/test_ci_import_compatibility.py -v
   # Local result: 12/12 passing ✅
   ```

2. Check current CI run status:
   - Error: `ModuleNotFoundError: No module named 'monitoring'`
   - Affected: 17+ tests trying to import metrics_collector
   - CI environment: Missing PYTHONPATH configuration

3. Document expected failure state:
   - Tests pass locally with PYTHONPATH=development
   - Tests fail in CI without PYTHONPATH
   - Need to replicate local environment in CI

**Expected State**: CI tests failing, local tests passing (confirms PYTHONPATH issue)

### Green Phase

**Minimal Implementation**:

1. **Identify Workflow File**:
   ```bash
   ls -la .github/workflows/
   # Find: ci.yml, ci-lite.yml
   # Determine which runs pytest
   ```

2. **Update CI Workflow**:
   ```yaml
   # .github/workflows/ci.yml (or ci-lite.yml)
   jobs:
     test:
       steps:
         - name: Run pytest
           env:
             PYTHONPATH: development  # Add this line
           run: |
             pytest development/tests/ -v --tb=short
   ```

3. **Commit and Push**:
   ```bash
   git add .github/workflows/ci.yml
   git commit -m "fix(P1-2.2): Set PYTHONPATH=development in CI workflow"
   git push origin ci-test-fixes-phase-1-blockers
   ```

4. **Trigger CI Run**:
   - Push triggers automatic CI run
   - Or manually trigger via GitHub Actions UI
   - Monitor run for metrics_collector imports

5. **Verify Results**:
   ```bash
   # Check CI logs for:
   # - metrics_collector imports succeeding
   # - test_ci_import_compatibility.py passing
   # - Error count reduction
   ```

**Expected State**: CI tests passing, 17+ ImportErrors resolved

### Refactor Phase

**Cleanup Opportunities**:

1. **Document CI Configuration Standards**:
   - Create `.github/workflows/README.md`
   - Document PYTHONPATH requirements
   - Explain why development/ must be in path

2. **Add Configuration Validation**:
   - Add step to CI that validates PYTHONPATH
   - Fail fast if configuration missing
   - Example:
     ```yaml
     - name: Validate environment
       run: |
         python3 -c "import sys; assert 'development' in sys.path"
     ```

3. **Update Other Workflows** (if multiple):
   - Check ci-lite.yml
   - Check any test-specific workflows
   - Ensure consistency across all workflows

4. **Create Reusable Action** (optional):
   - Extract PYTHONPATH setup to reusable action
   - Use across multiple workflows
   - Reduces duplication

5. **Update Test Documentation**:
   - Document CI-specific test requirements
   - Add troubleshooting guide for import errors
   - Reference diagnostic tests as debugging tool

---

## Next Action (for this session)

### Immediate Steps (in order):

1. **Review Diagnostic Tests** (5 minutes):
   ```bash
   # Verify local tests still pass
   PYTHONPATH=development python3 -m pytest \
     development/tests/unit/test_ci_import_compatibility.py -v
   # Expected: 12/12 passing
   ```

2. **Identify CI Workflow** (5 minutes):
   ```bash
   # Find workflow files
   ls -la .github/workflows/
   
   # Check which one runs pytest
   grep -n "pytest" .github/workflows/*.yml
   ```

3. **Update Workflow File** (5 minutes):
   - Add `PYTHONPATH: development` to env section
   - Ensure it's in correct job/step
   - Validate YAML syntax

4. **Commit and Push** (5 minutes):
   ```bash
   git add .github/workflows/ci.yml
   git commit -m "fix(P1-2.2): Set PYTHONPATH=development in CI workflow
   
   ROOT CAUSE: CI environment doesn't include development/ in Python path
   IMPACT: 17+ tests fail with ModuleNotFoundError for monitoring module
   FIX: Add PYTHONPATH=development to pytest step environment
   
   Related: P1-2.2, diagnostic tests in test_ci_import_compatibility.py"
   
   git push origin ci-test-fixes-phase-1-blockers
   ```

5. **Monitor CI Run** (10-15 minutes):
   - Watch CI run progress
   - Check for metrics_collector import success
   - Verify error count reduction
   - Document results

### Reference Files

- **CI Report**: `Projects/ACTIVE/ci-failure-report-2025-10-29.md`
- **Previous Lessons**: 
  - `Projects/ACTIVE/llama-vision-ocr-import-fix-lessons-learned.md`
  - `Projects/ACTIVE/template-fixtures-p1-2-1-lessons-learned.md`
- **Diagnostic Tests**: `development/tests/unit/test_ci_import_compatibility.py`
- **Workflow Files**: `.github/workflows/ci.yml`, `.github/workflows/ci-lite.yml`

---

## Success Metrics (End of Session)

**Target Error Reduction**: ~226 → ~210 errors (7% reduction)

**Measurable Outcomes**:
- ✅ PYTHONPATH configuration added to CI workflow
- ✅ metrics_collector ImportError resolved (17+ → 0)
- ✅ CI run completes successfully with updated config
- ✅ Diagnostic tests pass in CI environment
- ✅ Error count verifiably reduced by 7%+
- ✅ Zero breaking changes to existing passing tests
- ✅ CI configuration documented

**Commit Message Template**:
```
fix(P1-2.2): Set PYTHONPATH=development in CI workflow

ROOT CAUSE: CI environment doesn't include development/ directory in
Python path, causing ImportError for monitoring.metrics_collector and
potentially other modules

SOLUTION:
- Added PYTHONPATH=development to pytest step environment
- Ensures CI environment matches local development setup
- Allows imports from development/src/* to work correctly

IMPACT:
- ✅ ImportError reduced: 17+ → 0 (100% resolution)
- ✅ Error count reduced: ~226 → ~210 (7% decrease)
- ✅ CI environment now matches local development
- ✅ Diagnostic tests pass in CI (12/12)

VERIFICATION:
- Diagnostic tests: test_ci_import_compatibility.py (12/12 passing in CI)
- Workflow updated: .github/workflows/ci.yml
- CI run: [URL to successful run]

Duration: [XX] minutes via configuration fix
Related: P1-2.2, ci-test-fixes-phase-1-blockers branch
Docs: [lessons learned file if created]
```

---

## Would You Like Me To

Begin by reviewing the diagnostic tests locally and identifying which CI workflow file needs to be updated with PYTHONPATH configuration?
