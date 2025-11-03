# Next Session Prompt: Vault Config Phase 2 - P0-VAULT-2

Let's create a new branch for the next feature: **Vault Configuration Phase 2 - Priority 1 Module 2 (workflow_reporting_coordinator.py)**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

---

## Updated Execution Plan (focused P0/P1)

**Context**: GitHub Issue #45 - Vault Configuration Centralization. Phase 1 infrastructure complete (vault_config.yaml + loader + 15 passing tests). P0-VAULT-1 (promotion_engine.py) complete in 23 minutes with 16/19 tests passing. Currently migrating Priority 1 core workflow modules from hardcoded `Inbox/` paths to centralized `knowledge/Inbox/` configuration. This fixes confusion where starter pack examples don't match production vault structure.

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` and `.windsurf/guides/tdd-methodology-patterns.md` (critical path: **Priority 1 module migration - workflow_reporting_coordinator.py**).

---

## Current Status

**Completed**:
- ✅ Phase 1: Vault Config Infrastructure (vault_config.yaml + loader + 15 tests, all passing)
  - Branch: `docs/sprint-1-retrospective`, Commit: `08345c4`
  - Duration: 2 hours, 6 files created
- ✅ P0-VAULT-1: `promotion_engine.py` migration (2025-11-02)
  - Branch: `feat/vault-config-phase2-priority1`, Commit: `6caab99`
  - Duration: 23 minutes, 16/19 tests passing
  - 4 hardcoded paths replaced with vault config
  - 1 new integration test + 15 existing tests updated

**In progress**: 
- P0-VAULT-2: `workflow_reporting_coordinator.py` migration
- Target: Lines 50-53 hardcoded directory initialization
- File: `development/src/ai/workflow_reporting_coordinator.py`
- Test file: `development/tests/unit/test_workflow_reporting_coordinator.py`

**Lessons from last iteration**:
- Integration test pattern validates config usage: `assert "knowledge" in str(module.inbox_dir)`
- Property-based API enables single-line changes: `self.inbox_dir = config.inbox_dir`
- Test compatibility requires 15+ test updates (replace `base_dir / "knowledge"` with `tmp_path`)
- Multi-edit tool may leave 2-3 references requiring manual cleanup (lint provides fast feedback)
- Dependency chain visible: 4 tests fail due to NoteLifecycleManager needing migration (defer to later)

---

## P0 — Critical/Unblocker (Priority 1: Core Workflow Module 2)

**Migrate workflow_reporting_coordinator.py to Vault Config** - TDD RED → GREEN → REFACTOR cycle:

**Lines to Replace** (development/src/ai/workflow_reporting_coordinator.py):
```python
# Lines 50-53: Replace hardcoded paths
# OLD:
self.inbox_dir = self.base_dir / "Inbox"
self.fleeting_dir = self.base_dir / "Fleeting Notes"
self.permanent_dir = self.base_dir / "Permanent Notes"
self.archive_dir = self.base_dir / "Archive"

# NEW:
vault_config = get_vault_config(str(self.base_dir))
self.inbox_dir = vault_config.inbox_dir
self.fleeting_dir = vault_config.fleeting_dir
self.permanent_dir = vault_config.permanent_dir
self.archive_dir = vault_config.archive_dir
```

**Import Statement** (Line ~18):
```python
from src.config.vault_config_loader import get_vault_config
```

**References to Update**:
- Line 104: `"Inbox"` → Keep string (dict key for display)
- Line 126: `directory_counts.get("Inbox", 0)` → Keep string (dict lookup)
- Line 206: `directory_counts.get("Inbox", 0)` → Keep string (dict lookup)
- Lines 192, 205: Comments about "Inbox" → Keep as-is (documentation)

**Test Location**: `development/tests/unit/test_workflow_reporting_coordinator.py`

**Acceptance Criteria**:
- ✅ New integration test validates `knowledge/Inbox` usage
- ✅ All existing tests updated for vault config compatibility
- ✅ All coordinator tests pass (zero regressions)
- ✅ Module docstring updated with vault config documentation
- ✅ Commit follows established pattern with detailed message

---

## P1 — Verification & Next Module (Validation + Setup)

**1. Integration Testing**:
- Run full test suite: `cd development && python3 -m pytest tests/unit/test_workflow_reporting_coordinator.py -v`
- Verify directory metrics use correct paths
- Expected: All tests pass (100% success rate)

**2. Smoke Test with Live Vault**:
- Manual verification: Reports show correct directory counts
- Expected: `knowledge/Inbox` scanned correctly

**3. Next Module Setup** (P0-VAULT-3):
- File: `development/src/ai/review_triage_coordinator.py`
- Pattern: Same vault config integration
- Estimate: 25 minutes (following established pattern)

**Acceptance Criteria**:
- ✅ Integration tests pass
- ✅ Live vault verification complete
- ✅ Next module identified and ready

---

## P2 — Documentation & Remaining Modules (Phase 3-4)

**Complete migration and update documentation**:

1. **Phase 3: CLI Tools** (2 modules)
   - `core_workflow_cli.py`
   - `workflow_demo.py`

2. **Phase 4: Remaining Coordinators** (6 modules)
   - `fleeting_note_coordinator.py`
   - `analytics_coordinator.py`
   - Others as identified

3. **Phase 5: Automation Scripts** (10+ scripts)
   - `.automation/scripts/repair_metadata.py`
   - Others as needed

---

## Task Tracker

- [x] **INFRA-PHASE-1**: Vault config infrastructure (complete)
- [x] **P0-VAULT-1**: `promotion_engine.py` migration (complete)
- [In progress] **P0-VAULT-2**: `workflow_reporting_coordinator.py` migration
- [Pending] **P0-VAULT-3**: `review_triage_coordinator.py` migration
- [Pending] **P1-VAULT-4**: `core_workflow_cli.py` migration
- [Pending] **P1-VAULT-5**: `workflow_demo.py` migration
- [Pending] **P2-VAULT-6**: Remaining coordinators (6 modules)
- [Pending] **P2-VAULT-7**: Automation scripts (10+ scripts)
- [Pending] **P2-VAULT-8**: Documentation updates

---

## TDD Cycle Plan

### Red Phase
**Objective**: Write failing test that proves hardcoded paths exist

**Test to Create** (in `test_workflow_reporting_coordinator.py`):
```python
class TestVaultConfigIntegration:
    """Test WorkflowReportingCoordinator integration with vault configuration."""

    def test_coordinator_uses_vault_config_for_directories(self, tmp_path):
        """
        RED PHASE: Verify coordinator uses vault config for directory paths.
        
        Expected to FAIL until GREEN phase replaces hardcoded paths with config.
        """
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        analytics = Mock()  # Mock NoteAnalytics
        
        coordinator = WorkflowReportingCoordinator(tmp_path, analytics)
        
        # Should use knowledge/Inbox, not root-level Inbox
        assert "knowledge" in str(coordinator.inbox_dir)
        assert coordinator.inbox_dir == config.inbox_dir
        assert coordinator.fleeting_dir == config.fleeting_dir
        assert coordinator.permanent_dir == config.permanent_dir
        assert coordinator.archive_dir == config.archive_dir
```

**Expected**: Test FAILS with `AssertionError: 'knowledge' not in '.../Inbox'`

### Green Phase
**Objective**: Minimal implementation to make test pass

**Implementation Steps**:
1. Import vault config at top of `workflow_reporting_coordinator.py`
2. Replace lines 50-53 with vault config properties
3. Verify new test passes
4. Check for regressions (existing tests may fail - expected)

**Expected**: New test passes (1/1), existing tests may fail (normal for GREEN phase)

### Refactor Phase
**Objective**: Fix test compatibility, zero regressions

**Cleanup Tasks**:
1. Update existing test setup to use vault config paths
2. Replace `base_dir / "some/path"` with `config.some_dir`
3. Fix any `base_dir` references from multi-edit
4. Update module docstring with vault config note
5. Verify all tests pass

**Expected**: All tests passing (100%)

---

## Next Action (for this session)

**Immediate task**: TDD Cycle for `workflow_reporting_coordinator.py` migration (P0-VAULT-2)

**Step 1: Setup** (1 min)
- Confirm branch: `feat/vault-config-phase2-priority1` (continue from P0-VAULT-1)
- Confirm vault config available: `development/src/config/vault_config_loader.py`
- Locate target: `development/src/ai/workflow_reporting_coordinator.py` lines 50-53

**Step 2: RED Phase** (5 min)
- Write failing integration test in `test_workflow_reporting_coordinator.py`
- Test validates `knowledge/Inbox` usage for all 4 directories
- Run test: `pytest development/tests/unit/test_workflow_reporting_coordinator.py::TestVaultConfigIntegration -v`
- **Expected**: Test FAILS (AssertionError: 'knowledge' not in path)

**Step 3: GREEN Phase** (10 min)
- Import: `from src.config.vault_config_loader import get_vault_config`
- Replace lines 50-53 with vault config properties
- Run new test: Should PASS
- Run all coordinator tests: Check for regressions
- **Expected**: New test passes, ~10-15 existing tests may fail (normal)

**Step 4: REFACTOR Phase** (8 min)
- Update test fixtures to use vault config
- Fix any remaining hardcoded path references
- Update module docstring
- Verify all tests pass
- **Expected**: 100% tests passing

**Step 5: COMMIT** (2 min)
- Commit message: `feat: migrate workflow_reporting_coordinator to vault config (P0-VAULT-2)

Replace hardcoded Inbox/ paths with config properties
Add integration test validating knowledge/Inbox usage
Update existing tests for vault config compatibility
All coordinator tests passing

Part of GitHub Issue #45 Phase 2 Priority 1`

**Total Time**: ~26 minutes (similar to P0-VAULT-1)

---

## 📋 Reference Materials

### Configuration Files
- `development/vault_config.yaml` - Central configuration
- `development/src/config/vault_config_loader.py` - Loader API
- `development/tests/unit/test_vault_config_loader.py` - 15 tests (all passing)

### Documentation
- `Projects/ACTIVE/vault-config-centralization-plan.md` - Complete migration plan
- `Projects/ACTIVE/vault-config-implementation-summary.md` - Phase 1 summary
- `Projects/ACTIVE/vault-config-p0-vault-1-lessons-learned.md` - Previous iteration lessons
- `Projects/ACTIVE/GITHUB-ISSUE-UPDATE-vault-config.md` - GitHub issue text (updated)

### Git References
- **Current Branch**: `feat/vault-config-phase2-priority1` (continue)
- **Last Commit**: `6caab99` (P0-VAULT-1 complete)
- **Next Commit**: P0-VAULT-2 (workflow_reporting_coordinator.py)

### Target Files
- **Module**: `development/src/ai/workflow_reporting_coordinator.py`
- **Tests**: `development/tests/unit/test_workflow_reporting_coordinator.py`
- **Lines to Update**: 50-53 (directory initialization)

---

## 🎯 Success Metrics

**Phase 2 Complete When**:
- ✅ 3 Priority 1 modules migrated (2/3 complete after this iteration)
- ✅ All tests pass (existing + new)
- ✅ Integration tests verify `knowledge/Inbox` usage
- ✅ Zero hardcoded paths in migrated modules

**This Iteration Success**:
- ⬜ 1 new integration test passes
- ⬜ All existing coordinator tests pass
- ⬜ 4 directory paths migrated
- ⬜ Module docstring updated
- ⬜ Commit follows pattern
- ⬜ Time ~26 minutes

---

## 💡 Key Patterns & Best Practices

### Migration Pattern (Copy from P0-VAULT-1)
```python
# Step 1: Import at top of file
from src.config.vault_config_loader import get_vault_config

# Step 2: In __init__, replace hardcoded paths
# OLD:
self.inbox_dir = self.base_dir / "Inbox"

# NEW:
vault_config = get_vault_config(str(self.base_dir))
self.inbox_dir = vault_config.inbox_dir
```

### Testing Pattern (Proven in P0-VAULT-1)
```python
def test_module_uses_vault_config(tmp_path):
    """Verify module uses vault config for directory paths."""
    from src.config.vault_config_loader import get_vault_config
    
    config = get_vault_config(str(tmp_path))
    module = ModuleName(tmp_path, dependencies)
    
    # Should use knowledge/Inbox
    assert "knowledge" in str(module.inbox_dir)
    assert module.inbox_dir == config.inbox_dir
```

### Test Update Pattern
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

---

**Ready to start P0-VAULT-2 module migration!** 🚀

Would you like me to implement P0-VAULT-2 (`workflow_reporting_coordinator.py` migration) now in small, reviewable commits following this TDD cycle?
