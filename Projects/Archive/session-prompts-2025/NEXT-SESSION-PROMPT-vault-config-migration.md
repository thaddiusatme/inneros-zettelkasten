# Next Session Prompt: Vault Configuration Module Migration

**Date**: 2025-11-02  
**Previous Session**: Sprint 1 Retrospective + Vault Config Infrastructure (✅ Complete)  
**GitHub Issue**: Vault Config Centralization (Phase 2-4)  
**Current Branch**: `docs/sprint-1-retrospective`  
**Next Branch**: `feat/vault-config-migration`

---

## The Prompt

Let's create a new branch for the next feature: **Vault Configuration Module Migration (Phase 2)**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

### Updated Execution Plan (focused P0/P1)

**Context**: Completed Sprint 1 Retrospective successfully. Created centralized vault configuration infrastructure (Phase 1) to point all automations to `knowledge/Inbox` instead of root-level `Inbox/`. Now migrating core modules to use the new configuration system.

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` and `.windsurf/guides/tdd-methodology-patterns.md` (critical path: **Module migration to vault config for production readiness**).

### Current Status

**Completed**:
- ✅ Sprint 1 Retrospective (3 docs: retrospective, patterns, Sprint 2 recs)
- ✅ Vault Config Phase 1: Infrastructure complete
  - `vault_config.yaml` created (58 lines)
  - `vault_config_loader.py` implemented (252 lines)
  - 15 tests written and passing (0.07s execution)
  - Migration plan documented (315 lines)
  - Implementation summary written (300 lines)
  - Project manifest created
  - Commit: `08345c4`

**In progress**: 
- Phase 2: Module migration to use `knowledge/Inbox` consistently
- Starting with Priority 1 modules: `promotion_engine.py`, `workflow_reporting_coordinator.py`, `review_triage_coordinator.py`

**Lessons from last iteration**:
- Test-driven infrastructure creation prevents rework
- Property-based API (`config.inbox_dir`) cleaner than method calls
- Singleton pattern with `@lru_cache` provides performance without complexity
- Backwards compatibility critical - default config ensures no breaking changes
- Comprehensive tests (15 passing) give confidence for module migration

---

## P0 — Critical/Unblocker (Phase 2: Core Module Migration)

**Migrate Priority 1 Modules to Vault Config**:

1. **`promotion_engine.py`** - Auto-promotion uses correct inbox
   - Replace: `self.inbox_dir = self.base_dir / "Inbox"`
   - With: `config = get_vault_config(str(self.base_dir))`, `self.inbox_dir = config.inbox_dir`
   - Update all directory path initializations (inbox, permanent, literature, fleeting)
   - Verify 4 unit tests still pass
   - Add integration test confirming `knowledge/Inbox` used

2. **`workflow_reporting_coordinator.py`** - Reports scan correct directories
   - Replace: `self.inbox_dir = self.base_dir / "Inbox"`
   - With: `config = get_vault_config(str(self.base_dir))`, `self.inbox_dir = config.inbox_dir`
   - Update all directory references
   - Verify report metrics accurate for production vault

3. **`review_triage_coordinator.py`** - Weekly reviews scan correct inbox
   - Replace: `self.inbox_dir = self.base_dir / "Inbox"`
   - With: `config = get_vault_config(str(self.base_dir))`, `self.inbox_dir = config.inbox_dir`
   - Update fleeting and inbox directory references
   - Verify review scan test passes

**Acceptance Criteria**:
- ✅ All 3 Priority 1 modules migrated to vault config
- ✅ All existing tests pass (no regressions)
- ✅ New integration test confirms `knowledge/Inbox` usage
- ✅ Auto-promotion workflow verified on live vault
- ✅ Code review shows no hardcoded `"Inbox"` paths in migrated modules

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

- [x] **Phase 1**: Vault config infrastructure complete
- [In progress] **P0-VAULT-1**: Migrate `promotion_engine.py`
- [Pending] **P0-VAULT-2**: Migrate `workflow_reporting_coordinator.py`
- [Pending] **P0-VAULT-3**: Migrate `review_triage_coordinator.py`
- [Pending] **P1-VAULT-4**: Migrate `core_workflow_cli.py`
- [Pending] **P1-VAULT-5**: Migrate `workflow_demo.py`
- [Pending] **P1-VAULT-6**: Integration testing & verification

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

**Immediate task**: Create new branch and start Priority 1 module migration

1. **Create branch**: `feat/vault-config-migration` from `docs/sprint-1-retrospective`
2. **Start with `promotion_engine.py`**:
   - Location: `development/src/ai/promotion_engine.py`
   - Current: Lines 60-66 (directory initialization)
   - Action: Replace hardcoded paths with vault config
3. **Write/update tests**:
   - Location: `development/tests/unit/test_promotion_engine.py`
   - Add integration test for config usage
4. **Verify**:
   - Run: `python3 -m pytest development/tests/unit/test_promotion_engine.py -v`
   - Confirm 4 existing tests + new integration test pass

Would you like me to implement the `promotion_engine.py` migration now in small, reviewable commits following the TDD cycle (RED → GREEN → REFACTOR)?

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
