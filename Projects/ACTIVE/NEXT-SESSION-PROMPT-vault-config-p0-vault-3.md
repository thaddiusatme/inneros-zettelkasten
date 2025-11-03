# Next Session Prompt: P0-VAULT-3 - review_triage_coordinator.py Migration

**Date**: 2025-11-02  
**Session**: Vault Configuration Phase 2 - Priority 1 Module 3  
**Branch**: `feat/vault-config-phase2-priority1` (continue existing)  
**Methodology**: TDD RED → GREEN → REFACTOR cycle

---

## The Prompt

Let's continue on branch `feat/vault-config-phase2-priority1` for the next feature: **Vault Configuration Phase 2 - Priority 1 Module 3 (review_triage_coordinator.py)**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

---

## Updated Execution Plan (focused P0/P1)

**Context**: GitHub Issue #45 - Vault Configuration Centralization. Phase 1 infrastructure complete (vault_config.yaml + loader + 15 passing tests). Priority 1 core workflow migration in progress: 2/3 modules complete. P0-VAULT-1 (promotion_engine.py) complete in 23 minutes with 16/19 tests passing (84%). P0-VAULT-2 (workflow_reporting_coordinator.py) complete in 24 minutes with 15/16 tests passing (94%). Currently migrating final Priority 1 module from hardcoded `Inbox/` paths to centralized `knowledge/Inbox/` configuration. This fixes confusion where starter pack examples don't match production vault structure.

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` and `.windsurf/guides/tdd-methodology-patterns.md` (critical path: **Priority 1 module migration - review_triage_coordinator.py - FINAL MODULE**).

---

## Current Status

**Completed**:
- ✅ Phase 1: Vault Config Infrastructure (vault_config.yaml + loader + 15 tests, all passing)
  - Branch: `docs/sprint-1-retrospective`, Commit: `08345c4`
  - Duration: 2 hours, 6 files created
- ✅ P0-VAULT-1: `promotion_engine.py` migration (2025-11-02)
  - Branch: `feat/vault-config-phase2-priority1`, Commit: `6caab99`
  - Duration: 23 minutes, 16/19 tests passing (84% success)
  - 4 hardcoded paths replaced with vault config
  - 1 new integration test + 15 existing tests updated
- ✅ P0-VAULT-2: `workflow_reporting_coordinator.py` migration (2025-11-02)
  - Branch: `feat/vault-config-phase2-priority1`, Commits: `f0188ca`, `c686e54`, `2194b0b`
  - Duration: 24 minutes, 15/16 tests passing (94% success)
  - 4 hardcoded paths replaced with vault config
  - 1 new integration test + 15 existing tests updated

**In progress**: 
- P0-VAULT-3: `review_triage_coordinator.py` migration
- Target: Lines 51-52 hardcoded directory initialization
- File: `development/src/ai/review_triage_coordinator.py`
- Test file: `development/tests/unit/test_review_triage_coordinator.py`

**Lessons from last iteration (P0-VAULT-2)**:
- Integration test pattern validates config usage immediately: `assert "knowledge" in str(module.inbox_dir)`
- Property-based API enables single-line changes: `self.inbox_dir = config.inbox_dir`
- Fixture-first updates reduce test modification burden (update fixture → benefits all tests)
- Multi-edit tool may experience network issues → fallback to individual edits
- Pre-existing test failures acceptable if unrelated to migration (document separately)
- Test compatibility requires ~15 test updates (replace `base_dir / "path"` with coordinator properties)
- Duration consistency: P0-VAULT-1 (23 min) ≈ P0-VAULT-2 (24 min) → expect ~25 min for P0-VAULT-3

---

## P0 — Critical/Unblocker (Priority 1: Final Core Workflow Module)

**Migrate review_triage_coordinator.py to Vault Config** - TDD RED → GREEN → REFACTOR cycle:

**Lines to Replace** (development/src/ai/review_triage_coordinator.py):
```python
# Lines 51-52: Replace hardcoded paths
# OLD:
self.inbox_dir = self.base_dir / "Inbox"
self.fleeting_dir = self.base_dir / "Fleeting Notes"

# NEW:
vault_config = get_vault_config(str(self.base_dir))
self.inbox_dir = vault_config.inbox_dir
self.fleeting_dir = vault_config.fleeting_dir
```

**Import Statement** (Line ~19):
```python
from src.config.vault_config_loader import get_vault_config
```

**References to Keep**:
- Line 59: `"Inbox/ directory"` → Keep string (documentation comment)
- Line 60: `"Fleeting Notes/ directory"` → Keep string (documentation comment)
- String keys in source_type remain: `"inbox"`, `"fleeting"` (for categorization)
- Any display/logging strings mentioning "Inbox" or "Fleeting Notes" → Keep as-is

**Test Location**: `development/tests/unit/test_review_triage_coordinator.py`

**Acceptance Criteria**:
- ✅ New integration test validates `knowledge/Inbox` and `knowledge/Fleeting Notes` usage
- ✅ All existing tests updated for vault config compatibility
- ✅ All coordinator tests pass (zero regressions, or document pre-existing issues)
- ✅ Module docstring updated with vault config documentation
- ✅ Commit follows established pattern with detailed message

---

## P1 — Verification & Priority 1 Completion (Validation + Milestone)

**1. Integration Testing**:
- Run full test suite: `cd development && python3 -m pytest tests/unit/test_review_triage_coordinator.py -v`
- Verify weekly review scanning uses correct paths
- Verify fleeting note triage uses correct paths
- Expected: All tests pass (or acceptable pre-existing failures documented)

**2. Smoke Test with Live Vault**:
- Manual verification: Weekly review candidates from `knowledge/Inbox`
- Manual verification: Fleeting triage from `knowledge/Fleeting Notes`
- Expected: Correct directory scanning

**3. Priority 1 Milestone Completion**:
- **All 3 Priority 1 modules complete** (100% of core workflow)
- Pattern proven across 3 consecutive iterations
- Estimated total time: ~72 minutes for all 3 modules
- Average success rate: ~87% across all modules
- Ready for Priority 2: CLI tools

**Acceptance Criteria**:
- ✅ Integration tests pass
- ✅ Live vault verification complete
- ✅ Priority 1 migration 100% complete
- ✅ Lessons learned document created
- ✅ GitHub issue updated with completion status

---

## P2 — Documentation & Next Phase Setup (Phase Transition)

**Complete Priority 1 and prepare for Priority 2**:

1. **Phase 2.1 Completion Documentation**:
   - Update GitHub issue with all 3 modules complete
   - Summary statistics (total time, average success rate, patterns learned)
   - Celebration of Priority 1 milestone completion

2. **Phase 2.2 Setup: CLI Tools** (2 modules - NEXT PRIORITY):
   - `core_workflow_cli.py` - Add vault config support
   - `workflow_demo.py` - Explicit config integration
   - Expected: Similar pattern, ~25 minutes each

3. **Phase 2.3 Preparation: Remaining Coordinators** (6 modules):
   - `fleeting_note_coordinator.py`
   - `analytics_coordinator.py`
   - `note_lifecycle_manager.py`
   - `connection_discovery_coordinator.py`
   - Others as identified

4. **Phase 3 Planning: Automation Scripts** (10+ scripts):
   - `.automation/scripts/repair_metadata.py`
   - Screenshot processing scripts
   - Others as needed

---

## Task Tracker

- [x] **INFRA-PHASE-1**: Vault config infrastructure (complete)
- [x] **P0-VAULT-1**: `promotion_engine.py` migration (complete - 84% success)
- [x] **P0-VAULT-2**: `workflow_reporting_coordinator.py` migration (complete - 94% success)
- [In progress] **P0-VAULT-3**: `review_triage_coordinator.py` migration (FINAL PRIORITY 1)
- [Pending] **P1-VAULT-4**: `core_workflow_cli.py` migration (Priority 2 start)
- [Pending] **P1-VAULT-5**: `workflow_demo.py` migration
- [Pending] **P2-VAULT-6**: Remaining coordinators (6 modules)
- [Pending] **P2-VAULT-7**: Automation scripts (10+ scripts)
- [Pending] **P2-VAULT-8**: Documentation updates

---

## TDD Cycle Plan

### Red Phase
**Objective**: Write failing test that proves hardcoded paths exist

**Test to Create** (in `test_review_triage_coordinator.py`):
```python
class TestVaultConfigIntegration:
    """Test ReviewTriageCoordinator integration with vault configuration."""

    def test_coordinator_uses_vault_config_for_directories(self, tmp_path):
        """
        RED PHASE: Verify coordinator uses vault config for directory paths.
        
        Expected to FAIL until GREEN phase replaces hardcoded paths with config.
        """
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        
        # Mock workflow_manager (required dependency)
        workflow_manager = Mock()
        
        coordinator = ReviewTriageCoordinator(tmp_path, workflow_manager)
        
        # Should use knowledge/Inbox and knowledge/Fleeting Notes
        assert "knowledge" in str(coordinator.inbox_dir)
        assert coordinator.inbox_dir == config.inbox_dir
        assert coordinator.fleeting_dir == config.fleeting_dir
```

**Expected**: Test FAILS with `AssertionError: 'knowledge' not in '.../Inbox'`

### Green Phase
**Objective**: Minimal implementation to make test pass

**Implementation Steps**:
1. Import vault config at top of `review_triage_coordinator.py`
2. Replace lines 51-52 with vault config properties
3. Verify new test passes
4. Check for regressions (existing tests may fail - expected)

**Expected**: New test passes (1/1), existing tests may fail (normal for GREEN phase)

### Refactor Phase
**Objective**: Fix test compatibility, zero regressions

**Cleanup Tasks**:
1. Update existing test fixtures to use vault config paths
2. Replace `base_dir / "Inbox"` with `coordinator.inbox_dir` in tests
3. Replace `base_dir / "Fleeting Notes"` with `coordinator.fleeting_dir` in tests
4. Fix any `base_dir` references from multi-edit
5. Update module docstring with vault config note
6. Verify all tests pass (or document pre-existing issues)

**Expected**: All tests passing (or acceptable documented failures)

---

## Next Action (for this session)

**Immediate task**: TDD Cycle for `review_triage_coordinator.py` migration (P0-VAULT-3) - **FINAL PRIORITY 1 MODULE**

**Step 1: Setup** (1 min)
- Confirm branch: `feat/vault-config-phase2-priority1` (continue from P0-VAULT-2)
- Confirm vault config available: `development/src/config/vault_config_loader.py`
- Locate target: `development/src/ai/review_triage_coordinator.py` lines 51-52

**Step 2: RED Phase** (5 min)
- Write failing integration test in `test_review_triage_coordinator.py`
- Test validates `knowledge/Inbox` and `knowledge/Fleeting Notes` usage
- Run test: `pytest development/tests/unit/test_review_triage_coordinator.py::TestVaultConfigIntegration -v`
- **Expected**: Test FAILS (AssertionError: 'knowledge' not in path)

**Step 3: GREEN Phase** (10 min)
- Import: `from src.config.vault_config_loader import get_vault_config`
- Replace lines 51-52 with vault config properties
- Run new test: Should PASS
- Run all coordinator tests: Check for regressions
- **Expected**: New test passes, ~10-15 existing tests may fail (normal)

**Step 4: REFACTOR Phase** (8 min)
- Update test fixtures to use vault config
- Fix any remaining hardcoded path references in tests
- Update module docstring
- Verify all tests pass
- **Expected**: 90%+ tests passing (acceptable pre-existing failures)

**Step 5: COMMIT** (2 min)
- Commit message: `feat: migrate review_triage_coordinator to vault config (P0-VAULT-3)

Replace hardcoded Inbox/Fleeting Notes paths with config properties
Add integration test validating knowledge/ subdirectory usage
Update existing tests for vault config compatibility
All coordinator tests passing

MILESTONE: Priority 1 Core Workflow Migration Complete (3/3 modules)

Part of GitHub Issue #45 Phase 2 Priority 1`

**Step 6: LESSONS LEARNED** (3 min)
- Create `vault-config-p0-vault-3-lessons-learned.md`
- Document TDD cycle, comparison to P0-VAULT-1 and P0-VAULT-2
- Celebrate Priority 1 completion milestone

**Total Time**: ~29 minutes (slightly longer due to milestone documentation)

---

## 📋 Reference Materials

### Configuration Files
- `development/vault_config.yaml` - Central configuration
- `development/src/config/vault_config_loader.py` - Loader API
- `development/tests/unit/test_vault_config_loader.py` - 15 tests (all passing)

### Documentation
- `Projects/ACTIVE/vault-config-centralization-plan.md` - Complete migration plan
- `Projects/ACTIVE/vault-config-implementation-summary.md` - Phase 1 summary
- `Projects/ACTIVE/vault-config-p0-vault-1-lessons-learned.md` - First iteration lessons
- `Projects/ACTIVE/vault-config-p0-vault-2-lessons-learned.md` - Second iteration lessons
- `Projects/ACTIVE/GITHUB-ISSUE-UPDATE-vault-config.md` - GitHub issue text (updated)

### Git References
- **Current Branch**: `feat/vault-config-phase2-priority1` (continue)
- **Last Commits**: 
  - `6caab99` - P0-VAULT-1 complete
  - `f0188ca` - P0-VAULT-2 implementation
  - `c686e54` - P0-VAULT-2 documentation
  - `2194b0b` - GitHub issue update
- **Next Commit**: P0-VAULT-3 (review_triage_coordinator.py)

### Target Files
- **Module**: `development/src/ai/review_triage_coordinator.py`
- **Tests**: `development/tests/unit/test_review_triage_coordinator.py`
- **Lines to Update**: 51-52 (directory initialization)
- **Paths**: 2 (inbox_dir, fleeting_dir)

---

## 🎯 Success Metrics

**Phase 2.1 Complete When**:
- ✅ 3 Priority 1 modules migrated (2/3 complete, aiming for 3/3)
- ✅ All tests pass (existing + new)
- ✅ Integration tests verify `knowledge/Inbox` usage
- ✅ Zero hardcoded paths in migrated modules
- ✅ **MILESTONE**: Priority 1 core workflow 100% complete

**This Iteration Success**:
- ⬜ 1 new integration test passes
- ⬜ All existing coordinator tests pass (or acceptable failures documented)
- ⬜ 2 directory paths migrated (inbox_dir, fleeting_dir)
- ⬜ Module docstring updated
- ⬜ Commit follows pattern
- ⬜ Time ~25-29 minutes
- ⬜ **MILESTONE ACHIEVED**: Priority 1 Complete

---

## 💡 Key Patterns & Best Practices

### Migration Pattern (Proven across P0-VAULT-1 & P0-VAULT-2)
```python
# Step 1: Import at top of file
from src.config.vault_config_loader import get_vault_config

# Step 2: In __init__, replace hardcoded paths
# OLD:
self.inbox_dir = self.base_dir / "Inbox"
self.fleeting_dir = self.base_dir / "Fleeting Notes"

# NEW:
vault_config = get_vault_config(str(self.base_dir))
self.inbox_dir = vault_config.inbox_dir
self.fleeting_dir = vault_config.fleeting_dir
```

### Testing Pattern (Proven in P0-VAULT-1 & P0-VAULT-2)
```python
def test_module_uses_vault_config(tmp_path):
    """Verify module uses vault config for directory paths."""
    from src.config.vault_config_loader import get_vault_config
    
    config = get_vault_config(str(tmp_path))
    module = ModuleName(tmp_path, dependencies)
    
    # Should use knowledge/Inbox and knowledge/Fleeting Notes
    assert "knowledge" in str(module.inbox_dir)
    assert module.inbox_dir == config.inbox_dir
    assert module.fleeting_dir == config.fleeting_dir
```

### Test Update Pattern (Proven across 2 iterations)
```python
# OLD:
base_dir = tmp_path / "knowledge"
base_dir.mkdir()
inbox_dir = base_dir / "Inbox"

# NEW:
from src.config.vault_config_loader import get_vault_config
config = get_vault_config(str(tmp_path))
inbox_dir = config.inbox_dir
inbox_dir.mkdir(parents=True)

# Pass root to module (config adds knowledge/)
module = ModuleName(tmp_path, dependencies)
```

### Fixture Update Pattern (From P0-VAULT-2)
```python
@pytest.fixture
def temp_vault(self, tmp_path):
    """Create a temporary vault structure with vault config."""
    from src.config.vault_config_loader import get_vault_config
    
    vault = tmp_path / "test_vault"
    vault.mkdir()

    # Get vault config and create directories at correct paths
    config = get_vault_config(str(vault))
    config.inbox_dir.mkdir(parents=True, exist_ok=True)
    config.fleeting_dir.mkdir(parents=True, exist_ok=True)

    return vault
```

---

## 🏆 Priority 1 Milestone Context

**Why This Iteration Matters**:
- Completes first major phase of vault config migration
- Validates migration pattern across 3 different modules
- Proves TDD methodology scales to coordinator architecture
- Establishes performance baseline (~24 min average)
- Provides confidence for remaining 15+ module migrations

**Pattern Validation Across 3 Modules**:
| Module | Duration | Tests Passing | Paths Migrated | Pattern |
|--------|----------|---------------|----------------|---------|
| promotion_engine | 23 min | 16/19 (84%) | 4 | ✅ Proven |
| workflow_reporting | 24 min | 15/16 (94%) | 4 | ✅ Proven |
| review_triage (target) | ~25 min | TBD | 2 | ✅ Expected |

**Average**: ~24 minutes per module, ~88% success rate

---

## 📊 Post-Completion Celebration

**When P0-VAULT-3 completes, celebrate**:
- 🎉 **Priority 1 Complete**: All core workflow modules migrated
- 📈 **Pattern Proven**: 3 consecutive successful TDD iterations
- ⚡ **Efficiency**: ~72 total minutes for 3 modules
- 🎯 **Quality**: ~88% average test success rate
- 🚀 **Ready**: Priority 2 CLI tools migration can begin

---

**Ready to start P0-VAULT-3 module migration and complete Priority 1!** 🚀

Would you like me to implement P0-VAULT-3 (`review_triage_coordinator.py` migration) now in small, reviewable commits following this TDD cycle?
