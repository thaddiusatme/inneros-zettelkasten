# Next Session Prompt: Vault Configuration Module Migration

**Date**: 2025-11-02  
**Previous Session**: Sprint 1 Retrospective + Vault Config Infrastructure (✅ Complete)  
**GitHub Issue**: Vault Config Centralization (Phase 2-4)  
**Current Branch**: `docs/sprint-1-retrospective`  
**Next Branch**: `feat/vault-config-migration`

---

## The Prompt


Let's create a new branch for the next feature: **Vault Configuration Module Migration - Phase 2 Priority 1 Modules**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

### Updated Execution Plan (focused P0/P1)

**Context**: GitHub Issue #45 - Vault Configuration Centralization. Phase 1 infrastructure complete (vault_config.yaml + loader + 15 passing tests). Currently 15+ modules have hardcoded `Inbox/` paths instead of using `knowledge/Inbox/`. This causes confusion for users and breaks starter pack examples. Phase 2 migrates core modules to centralized config.

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` and `.windsurf/guides/tdd-methodology-patterns.md` (critical path: **Priority 1 module migration - promotion_engine, workflow_reporting_coordinator, review_triage_coordinator**).

### Current Status

**Completed**:
- ✅ Sprint 1 Retrospective (retrospective, patterns, Sprint 2 recommendations)
- ✅ Vault Config Phase 1: Infrastructure (GitHub Issue #45)
  - `vault_config.yaml` with `vault.root: knowledge` (58 lines)
  - `vault_config_loader.py` with property-based API (252 lines)  
  - 15 unit tests, all passing, 0.07s execution
  - `get_vault_config()`, `get_inbox_dir()` convenience functions
  - Complete documentation: plan, implementation summary, manifest
  - Branch: `docs/sprint-1-retrospective`, Commit: `08345c4`

**In progress**: 
- Phase 2: Module migration - Priority 1 (Critical Path)
- Target modules in `development/src/ai/`: `promotion_engine.py`, `workflow_reporting_coordinator.py`, `review_triage_coordinator.py`

**Lessons from last iteration**:
- Infrastructure-first TDD prevents downstream rework (15 tests → 100% confidence)
- Property-based API (`.inbox_dir`) beats methods for clarity and brevity
- Singleton + `@lru_cache` = zero-config performance optimization
- Backwards compatibility via defaults = zero breaking changes for existing code
- Integration test pattern: `assert "knowledge" in str(module.inbox_dir)` validates migration

---

## P0 — Critical/Unblocker (Priority 1: Core Workflow Modules)

**Migrate 3 Core Modules to Vault Config** - TDD RED → GREEN → REFACTOR cycle:

1. **`promotion_engine.py`** (development/src/ai/promotion_engine.py)
   - **Lines 60-66**: Replace hardcoded `self.inbox_dir = self.base_dir / "Inbox"`
   - Import: `from src.config import get_vault_config`
   - Initialize: `config = get_vault_config(str(self.base_dir))`
   - Update: `self.inbox_dir = config.inbox_dir`, `self.permanent_dir = config.permanent_dir`, etc.
   - Test location: `development/tests/unit/test_promotion_engine.py`
   - Expected: 4 existing tests + 1 new integration test = 5 passing

2. **`workflow_reporting_coordinator.py`** (development/src/ai/coordinators/workflow_reporting_coordinator.py)
   - Replace: `self.inbox_dir = self.base_dir / "Inbox"` with vault config
   - Update: All directory references (inbox, permanent, literature, fleeting)
   - Test: Verify report metrics scan `knowledge/Inbox` not root `Inbox/`
   - Expected: All coordinator tests pass + reports show correct directory counts

3. **`review_triage_coordinator.py`** (development/src/ai/coordinators/review_triage_coordinator.py)  
   - Replace: Hardcoded `"Inbox"` and `"Fleeting Notes"` paths
   - Update: Use `config.inbox_dir` and `config.fleeting_dir` throughout
   - Test: Weekly review scan finds notes in correct locations
   - Expected: Review tests pass + live weekly review works on production vault

**Acceptance Criteria**:
- ✅ 3 modules migrated following TDD cycle (RED test → GREEN implementation → REFACTOR cleanup)
- ✅ All existing module tests pass (zero regressions)
- ✅ New integration tests validate `knowledge/Inbox` usage: `assert "knowledge" in str(module.inbox_dir)`
- ✅ Live workflow verification: auto-promotion on `knowledge/Inbox` succeeds
- ✅ Code review: No `Inbox/`, `Permanent Notes/` string literals remain in migrated files

---

## P1 — CLI Tools & Verification (User-Facing Updates)

**Migrate CLI tools and verify workflows**:

1. **`core_workflow_cli.py`** - Add vault config support
   - Add vault config initialization in `__init__`
   - Maintain existing auto-detection logic as fallback
   - Update directory resolution to use config
   - Test CLI commands point to correct paths

2. **`workflow_demo.py`** - Explicit vault config integration
   - Replace hardcoded auto-detection with config usage
   - Update help text to mention `knowledge/` structure
   - Verify demo commands work correctly
   - Manual smoke test with `--dry-run`

3. **Integration Testing**:
   - Run auto-promotion on live `knowledge/Inbox`
   - Verify reports show correct directory metrics
   - Test CLI commands with production vault
   - Confirm no path resolution errors

**Acceptance Criteria**:
- ✅ CLI tools use vault config
- ✅ All CLI commands work with `knowledge/` structure
- ✅ Help text updated and accurate
- ✅ Integration tests pass
- ✅ Manual verification complete

---

## P2 — Documentation & Remaining Modules (Phase 3-4)

**Complete migration and update documentation**:

1. **Phase 3: Coordinators** (6 modules)
   - `fleeting_note_coordinator.py`
   - `analytics_coordinator.py`
   - `safe_image_processing_coordinator.py`
   - Others as identified

2. **Phase 4: Automation Scripts** (10+ scripts)
   - `.automation/scripts/repair_metadata.py`
   - `.automation/scripts/validate_metadata.py`
   - Others as needed

3. **Documentation Updates**:
   - `README.md` - Vault structure examples
   - `CLI-REFERENCE.md` - Path examples
   - `knowledge/GETTING-STARTED.md` - Directory references
   - `knowledge-starter-pack/README.md` - Structure guide

---

## Task Tracker

- [x] **INFRA-PHASE-1**: Vault config infrastructure (vault_config.yaml + loader + 15 tests)
- [In progress] **P0-VAULT-1**: Migrate `promotion_engine.py` to vault config
- [Pending] **P0-VAULT-2**: Migrate `workflow_reporting_coordinator.py` to vault config
- [Pending] **P0-VAULT-3**: Migrate `review_triage_coordinator.py` to vault config
- [Pending] **P1-VAULT-4**: Migrate `core_workflow_cli.py` with vault config support
- [Pending] **P1-VAULT-5**: Migrate `workflow_demo.py` with explicit config integration
- [Pending] **P1-VAULT-6**: Integration tests + live vault verification
- [Pending] **P2-VAULT-7**: Remaining coordinators (6 modules)
- [Pending] **P2-VAULT-8**: Automation scripts (10+ scripts)
- [Pending] **P2-VAULT-9**: Documentation updates (README, CLI-REFERENCE, GETTING-STARTED)

---

## TDD Cycle Plan

### Red Phase
**Objective**: Write failing tests that verify modules use `knowledge/Inbox`

1. **Test Setup**:
   - Create integration test for `promotion_engine.py`
   - Test should verify `config.inbox_dir` points to `knowledge/Inbox`
   - Test should fail initially (module still uses hardcoded path)

2. **Test Cases**:
   ```python
   def test_promotion_engine_uses_vault_config():
       """Verify PromotionEngine uses vault config for directory paths."""
       config = get_vault_config()
       engine = PromotionEngine(base_dir=".")
       
       # Should use knowledge/Inbox, not root-level Inbox
       assert "knowledge" in str(engine.inbox_dir)
       assert engine.inbox_dir == config.inbox_dir
   ```

3. **Expected Failures**:
   - Test fails because `promotion_engine.py` uses `self.base_dir / "Inbox"`
   - Path assertion fails (doesn't contain "knowledge")

### Green Phase
**Objective**: Minimal implementation to make tests pass

1. **Import vault config**:
   ```python
   from src.config import get_vault_config
   ```

2. **Update directory initialization** in each module:
   ```python
   # OLD:
   self.inbox_dir = self.base_dir / "Inbox"
   self.permanent_dir = self.base_dir / "Permanent Notes"
   
   # NEW:
   config = get_vault_config(str(self.base_dir))
   self.inbox_dir = config.inbox_dir
   self.permanent_dir = config.permanent_dir
   ```

3. **Verify tests pass**:
   - All existing tests still pass (backwards compatibility)
   - New integration tests pass (vault config used)

### Refactor Phase
**Objective**: Clean up, optimize, document

1. **Code cleanup**:
   - Remove any remaining hardcoded paths
   - Ensure consistent config usage pattern
   - Add docstring comments about vault config

2. **Test enhancement**:
   - Add parametrized tests for different vault structures
   - Verify error handling for missing config

3. **Documentation**:
   - Update module docstrings
   - Add migration notes to lessons learned

---

## Next Action (for this session)

**Immediate task**: TDD Cycle for `promotion_engine.py` migration (P0-VAULT-1)

**Step 1: Setup** (1 min)

- Create branch: `feat/vault-config-phase2-priority1` from `docs/sprint-1-retrospective`
- Confirm vault config available: `development/src/config/vault_config_loader.py` exists
- Locate target: `development/src/ai/promotion_engine.py` lines 60-66

**Step 2: RED Phase** (5 min)

- Write failing integration test in `development/tests/unit/test_promotion_engine.py`:

  ```python
  def test_promotion_engine_uses_vault_config():
      """Verify PromotionEngine uses knowledge/Inbox from vault config."""
      engine = PromotionEngine(base_dir=".")
      assert "knowledge" in str(engine.inbox_dir)  # Should fail - uses root Inbox/
      config = get_vault_config()
      assert engine.inbox_dir == config.inbox_dir
  ```

- Run: `pytest development/tests/unit/test_promotion_engine.py::test_promotion_engine_uses_vault_config -v`
- **Expected**: Test FAILS (AssertionError: 'knowledge' not in 'Inbox')

**Step 3: GREEN Phase** (10 min)

- Import at top of `promotion_engine.py`: `from src.config import get_vault_config`
- Replace lines 60-66 directory initialization:

  ```python
  config = get_vault_config(str(self.base_dir))
  self.inbox_dir = config.inbox_dir
  self.permanent_dir = config.permanent_dir
  self.literature_dir = config.literature_dir
  self.fleeting_dir = config.fleeting_dir
  ```

- Run: `pytest development/tests/unit/test_promotion_engine.py -v`
- **Expected**: 5 tests pass (4 existing + 1 new integration test)

**Step 4: REFACTOR Phase** (5 min)

- Update module docstring: mention vault config usage
- Search/replace any remaining hardcoded `"Inbox"` strings
- Verify all tests still pass: `pytest development/tests/unit/test_promotion_engine.py -v`

**Step 5: COMMIT** (2 min)

- Commit message: `feat: migrate promotion_engine to vault config (P0-VAULT-1)

- Replace hardcoded Inbox/ paths with config.inbox_dir
- Add integration test validating knowledge/Inbox usage  
- All 5 tests passing (4 existing + 1 new)
- Part of GitHub Issue #45 Phase 2 Priority 1`

**Total Time**: ~23 minutes for first module

Would you like me to implement P0-VAULT-1 (`promotion_engine.py` migration) now in small, reviewable commits following this TDD cycle?

---

## 📋 Reference Materials

### Configuration Files
- `development/vault_config.yaml` - Central configuration
- `development/src/config/vault_config_loader.py` - Loader API
- `development/tests/unit/test_vault_config_loader.py` - 15 tests (all passing)

### Documentation
- `Projects/ACTIVE/vault-config-centralization-plan.md` - Complete migration plan
- `Projects/ACTIVE/vault-config-implementation-summary.md` - Phase 1 summary
- `Projects/ACTIVE/vault-config-centralization-manifest.md` - Project manifest
- `Projects/ACTIVE/GITHUB-ISSUE-UPDATE-vault-config.md` - GitHub issue text

### Git References
- **Current Branch**: `docs/sprint-1-retrospective`
- **Last Commit**: `08345c4` (Phase 1 complete)
- **Next Branch**: `feat/vault-config-migration` (to be created)

### Modules to Migrate (Priority Order)
1. **Priority 1** (Critical): promotion_engine, workflow_reporting, review_triage
2. **Priority 2** (User-facing): core_workflow_cli, workflow_demo
3. **Priority 3** (Moderate): fleeting_note_coordinator, analytics, safe_image_processing
4. **Priority 4** (Production): automation scripts

---

## 🎯 Success Metrics

**Phase 2 Complete When**:
- ✅ 3 Priority 1 modules migrated
- ✅ 2 Priority 2 CLI tools migrated
- ✅ All tests pass (existing + new)
- ✅ Integration tests verify `knowledge/Inbox` usage
- ✅ Live vault workflows functional
- ✅ No hardcoded `"Inbox"` paths in migrated modules

**Time Estimate**: 2-3 hours for Phase 2

---

## 💡 Key Patterns & Best Practices

### Migration Pattern
```python
# Step 1: Import at top of file
from src.config import get_vault_config

# Step 2: In __init__, replace hardcoded paths
# OLD:
self.inbox_dir = self.base_dir / "Inbox"

# NEW:
config = get_vault_config(str(self.base_dir))
self.inbox_dir = config.inbox_dir
```

### Testing Pattern
```python
def test_module_uses_vault_config():
    """Verify module uses vault config for directory paths."""
    config = get_vault_config()
    module = ModuleName(base_dir=".")
    
    # Should use knowledge/Inbox
    assert "knowledge" in str(module.inbox_dir)
    assert module.inbox_dir == config.inbox_dir
```

### Backwards Compatibility
- Config has sensible defaults if file missing
- Path objects work with existing string operations
- No breaking changes to public APIs

---

**Ready to start Phase 2 module migration!** 🚀
