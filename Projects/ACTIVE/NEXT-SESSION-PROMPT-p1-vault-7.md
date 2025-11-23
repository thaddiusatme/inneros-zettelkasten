# Session Prompt: P1-VAULT-7 Analytics Coordinator Migration

**Branch**: `feat/vault-config-phase2-priority1` (existing - DO NOT create new)  
**GitHub Issue**: #45 - Vault Configuration Centralization  
**Session Goal**: Migrate `analytics_coordinator.py` to vault config using proven TDD pattern

---

## The Prompt

We're continuing on branch `feat/vault-config-phase2-priority1` for the next module: **P1-VAULT-7** (`analytics_coordinator.py`). We want to perform TDD framework with RED, GREEN, REFACTOR phases, followed by git commit and lessons learned documentation. This equals one iteration.

### Updated Execution Plan (GitHub Issue #45 - Phase 2 Priority 3)

**Current Migration Progress**: 6/11 Priority 1-3 modules complete (55%)

I'm following the guidance in:
- `.windsurf/guides/tdd-methodology-patterns.md` (TDD patterns from 34+ iterations)
- `Projects/ACTIVE/vault-config-p0-vault-6-lessons-learned.md` (proven coordinator migration pattern)
- `.windsurf/rules/updated-development-workflow.md` (TDD methodology, Git standards)

**Critical Path**: Complete Priority 3 coordinator migrations (5 remaining) to reach Phase 2 completion

---

## Current Status

**Completed**: 
- ✅ P0-VAULT-6: `fleeting_note_coordinator.py` - Complete TDD cycle (22/22 tests passing, 100%)
  - RED phase: Integration test created and confirmed failing
  - GREEN phase: Constructor migrated to vault config (commit `96193eb`)
  - REFACTOR phase: All 22 tests updated in 3 systematic commits (`010e146`, `8cc7362`, `8f9149d`)
  - Documentation: Lessons-learned updated (commit `1a0a897`)

**In progress**: 
- 🔄 P1-VAULT-7: `analytics_coordinator.py` migration
  - File: `development/src/ai/analytics_coordinator.py`
  - Current constructor: Lines 35-45 (hardcoded paths)
  - Target: Migrate to `base_dir` + vault config pattern

**Lessons from P0-VAULT-6**:
1. ✅ **Proven Pattern Works**: `base_dir` + `workflow_manager` constructor signature with `get_vault_config()` internal loading
2. ✅ **Test Fixture Success**: `vault_with_config` pytest fixture provides consistent test setup
3. ✅ **Systematic REFACTOR**: Breaking test updates into 3-4 commits (4-5 tests each) maintains clarity and quality
4. ✅ **Time Efficiency**: ~1-2 minutes per test update with systematic pattern
5. ✅ **100% Success Rate**: Pattern achieved 22/22 tests passing with zero regressions

---

## P0 — Critical/Unblocker (Priority 3 Coordinator Migration)

**P0-1: RED Phase** - Create failing integration test for `analytics_coordinator.py`:
- Create `test_analytics_coordinator_uses_vault_config` in `development/tests/unit/test_analytics_coordinator.py`
- Test should instantiate `AnalyticsCoordinator(base_dir=vault, workflow_manager=Mock())`
- Expect `TypeError` about unexpected keyword arguments (current constructor only accepts `base_dir`)
- Confirm test fails as expected (RED phase complete)

**P0-2: GREEN Phase** - Migrate constructor to vault config pattern:
- Update `development/src/ai/analytics_coordinator.py` lines 35-45
- Change signature: `def __init__(self, base_dir: Path, workflow_manager=None):`
- Add import: `from src.config.vault_config_loader import get_vault_config`
- Load config internally: `vault_config = get_vault_config(str(base_dir))`
- Update directory properties: `self.inbox_dir = vault_config.inbox_dir` (etc.)
- Run integration test - should pass (GREEN phase complete)

**Acceptance Criteria**:
- ✅ Integration test passes (confirms vault config usage)
- ✅ Existing tests may fail (expected - addresses in REFACTOR)
- ✅ Constructor follows proven P0-VAULT-6 pattern
- ✅ Zero changes to class functionality (only initialization)

---

## P1 — REFACTOR Phase (Test Migration)

**P1-1: Analyze Test Failures**:
- Run full test suite: `pytest development/tests/unit/test_analytics_coordinator.py -v`
- Identify which tests fail due to constructor signature change
- Expected: Tests using old `AnalyticsCoordinator(base_dir)` pattern will fail
- Document count and test class names

**P1-2: Systematic Test Updates** (Following P0-VAULT-6 Pattern):
- **Migration Pattern** (applies to each test):
  ```python
  # OLD:
  def test_example(tmp_path):
      coordinator = AnalyticsCoordinator(tmp_path)
  
  # NEW:
  def test_example(vault_with_config):
      vault = vault_with_config["vault"]
      coordinator = AnalyticsCoordinator(
          base_dir=vault,
          workflow_manager=Mock()
      )
  ```
- **Strategy**: Update tests in groups of 4-5 tests per commit
- **Commit Structure**:
  - Commit 1: Update first test class (e.g., TestOrphanedNoteDetection)
  - Commit 2: Update second test class (e.g., TestStaleNoteDetection)
  - Commit 3: Update remaining tests + integration test
  - Each commit should show progressive test success rate improvement

**P1-3: Verify REFACTOR Completion**:
- Run full test suite and confirm all tests pass
- Target: 95%+ success rate (100% if possible)
- Document final test count and success rate
- Verify zero regressions in existing functionality

**Acceptance Criteria**:
- ✅ All tests updated to use `vault_with_config` fixture
- ✅ 95%+ test success rate (target 100%)
- ✅ Clean commit history (3-4 commits documenting progression)
- ✅ No changes to test assertions (only setup/fixture usage)

---

## P2 — Documentation & Lessons Learned (Completion)

**P2-1: Create Lessons-Learned Document**:
- File: `Projects/ACTIVE/vault-config-p1-vault-7-lessons-learned.md`
- Include: TDD cycle results, test progression, time metrics, pattern validation
- Reference: P0-VAULT-6 document structure

**P2-2: Update GitHub Issue #45**:
- Post progress comment with P1-VAULT-7 completion details
- Update Priority 3 progress: 2/6 modules complete (33%)
- Include commit references and test results

**P2-3: Update Session Context**:
- Update overall Phase 2 progress metrics
- Document any pattern improvements or learnings
- Prepare handoff for P1-VAULT-8 (connection_coordinator.py)

---

## Task Tracker

- [In progress] **P1-VAULT-7**: `analytics_coordinator.py` RED phase
- [Pending] **P1-VAULT-7**: GREEN phase implementation
- [Pending] **P1-VAULT-7**: REFACTOR phase (test updates)
- [Pending] **P1-VAULT-7**: Documentation and lessons learned
- [Pending] **P1-VAULT-8**: `connection_coordinator.py` migration
- [Pending] **P1-VAULT-9**: `safe_image_processing_coordinator.py` migration

---

## TDD Cycle Plan

### RED Phase (Expected: 2-3 minutes)

**Create failing test**:
- File: `development/tests/unit/test_analytics_coordinator.py`
- Test: `test_analytics_coordinator_uses_vault_config_for_directories(vault_with_config)`
- Expected failure: `TypeError: __init__() got an unexpected keyword argument 'workflow_manager'`
- Verification: Run test and confirm RED (test fails as expected)

### GREEN Phase (Expected: 5-10 minutes)

**Minimal implementation**:
- File: `development/src/ai/analytics_coordinator.py` (lines 35-45)
- Changes:
  1. Update constructor signature to accept `base_dir` + `workflow_manager`
  2. Add vault config import
  3. Load vault config in `__init__`
  4. Update 3 directory properties to use config
- Verification: Integration test passes (GREEN phase complete)
- Expected: Some existing tests may fail (addressed in REFACTOR)

### REFACTOR Phase (Expected: 30-45 minutes)

**Systematic test updates**:
1. **Analyze**: Run full test suite, document failures (expected: 10-20 tests)
2. **Update in batches**: 3-4 commits updating test classes systematically
3. **Verify**: Each commit should improve test success rate progressively
4. **Final check**: All tests passing (100% target)

**Cleanup opportunities**:
- Verify all tests use `vault_with_config` fixture consistently
- Ensure no hardcoded paths remain in test assertions
- Validate test coverage remains comprehensive

---

## Next Action (for this session)

**Immediate task**: Begin RED phase for P1-VAULT-7

1. **Review current code**:
   - Read `development/src/ai/analytics_coordinator.py` (focus on `__init__` method)
   - Identify hardcoded directory assignments (lines 43-45)
   - Review existing test file: `development/tests/unit/test_analytics_coordinator.py`

2. **Create integration test**:
   - Add `test_analytics_coordinator_uses_vault_config_for_directories` to test file
   - Use `vault_with_config` fixture from P0-VAULT-6 pattern
   - Test vault config directory loading
   - Run and confirm test fails (RED phase)

3. **Reference proven pattern**:
   - Refer to `development/src/ai/fleeting_note_coordinator.py` lines 34-62 for exact pattern
   - Follow same constructor signature: `base_dir: Path, workflow_manager, ...`
   - Use same vault config loading approach

**Would you like me to start with the RED phase now? I'll create the failing integration test following the proven P0-VAULT-6 pattern.**

---

## 📚 Key References

**Proven Pattern** (from P0-VAULT-6):
- Implementation: `development/src/ai/fleeting_note_coordinator.py` lines 34-65
- Test fixture: `development/tests/unit/conftest.py` (`vault_with_config`)
- Lessons learned: `Projects/ACTIVE/vault-config-p0-vault-6-lessons-learned.md`

**TDD Guidance**:
- Methodology: `.windsurf/guides/tdd-methodology-patterns.md`
- Development workflow: `.windsurf/rules/updated-development-workflow.md`
- Session context: `.windsurf/rules/updated-session-context.md`

**Project Context**:
- GitHub Issue: #45 (updated 2025-11-03)
- Migration plan: `Projects/ACTIVE/vault-config-centralization-plan.md`
- Implementation summary: `Projects/ACTIVE/vault-config-implementation-summary.md`

---

## Success Metrics

**Target for P1-VAULT-7**:
- ✅ Complete TDD cycle (RED → GREEN → REFACTOR)
- ✅ 95%+ test success rate (target 100%)
- ✅ Clean 3-4 commit history
- ✅ ~60 minutes total duration
- ✅ Zero regressions in functionality
- ✅ Lessons-learned documented

**Session complete when**:
1. All tests passing for `analytics_coordinator.py`
2. Commits pushed to `feat/vault-config-phase2-priority1`
3. Lessons-learned document created
4. GitHub Issue #45 updated with progress
5. Ready to proceed to P1-VAULT-8

---

**Branch reminder**: Already on `feat/vault-config-phase2-priority1` - DO NOT create new branch!
