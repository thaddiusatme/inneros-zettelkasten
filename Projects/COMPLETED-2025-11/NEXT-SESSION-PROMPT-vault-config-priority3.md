# Next Session Prompt - Vault Config Priority 3 (Remaining Coordinators)

## The Prompt

Let's continue on branch `feat/vault-config-phase2-priority1` for Priority 3 coordinator migrations. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

### Updated Execution Plan (Priority 3 Focus)

**Context**: Vault configuration centralization (GitHub Issue #45) - migrating remaining coordinators to use `vault_config.yaml` instead of hardcoded directory paths. We've successfully completed Priority 1 (3 core workflow modules) and Priority 2 (2 CLI tools) with proven patterns. Now applying the coordinator pattern to remaining modules.

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` and `.windsurf/guides/tdd-methodology-patterns.md` (critical path: coordinator migration using proven pattern from Priority 1).

### Current Status

**Completed**:
- ✅ **Priority 1 Complete** (3/3 modules): promotion_engine, workflow_reporting_coordinator, review_triage_coordinator
- ✅ **Priority 2 Complete** (2/2 modules): core_workflow_cli, workflow_demo
- ✅ **Total**: 5 modules migrated, 7/13 acceptance criteria met (54%)
- ✅ **Branch**: `feat/vault-config-phase2-priority1` (5 commits ready)
- ✅ **Test Success**: Average 95% across all modules, Priority 2 achieved 100%

**In Progress**:
- Starting Priority 3 - Remaining Coordinators (6 modules)
- First module: `fleeting_note_coordinator.py`
- Location: `development/src/ai/fleeting_note_coordinator.py`

**Lessons from Last Iteration (P0-VAULT-5)**:
1. **Targeted fixes work for deprecated code** - workflow_demo.py completed in 15 min (40% faster)
2. **100% test success achievable** - 3/3 tests passing with minimal changes
3. **Pattern diversity proven** - full integration, CLI independence, and targeted fix all successful
4. **Ready to scale** - Priority 1 & 2 complete validates coordinator pattern for Priority 3

---

## P0 — Critical/Unblocker (Priority 3 Start)

**P0-VAULT-6**: Migrate `fleeting_note_coordinator.py` to vault configuration

**Implementation Details**:
1. Add vault config import: `from src.config.vault_config_loader import get_vault_config`
2. Load vault config in `__init__`: `vault_config = get_vault_config(str(base_dir))`
3. Replace constructor parameters with vault config properties:
   - `fleeting_dir` → `vault_config.fleeting_dir`
   - `inbox_dir` → `vault_config.inbox_dir`
   - `permanent_dir` → `vault_config.permanent_dir`
   - `literature_dir` → `vault_config.literature_dir`
4. Update module docstring to document vault config integration
5. Keep `process_callback` parameter (delegates to WorkflowManager)

**Current Constructor** (lines 30-49):
```python
def __init__(
    self,
    fleeting_dir: Path,
    inbox_dir: Path,
    permanent_dir: Path,
    literature_dir: Path,
    process_callback: Optional[Callable] = None,
    default_quality_threshold: float = 0.7,
):
```

**Target Pattern** (from review_triage_coordinator.py):
```python
def __init__(self, base_dir: Path, workflow_manager):
    self.base_dir = Path(base_dir)
    self.workflow_manager = workflow_manager
    
    # Load vault configuration for directory paths
    vault_config = get_vault_config(str(self.base_dir))
    self.fleeting_dir = vault_config.fleeting_dir
    self.inbox_dir = vault_config.inbox_dir
    self.permanent_dir = vault_config.permanent_dir
    self.literature_dir = vault_config.literature_dir
```

**Acceptance Criteria**:
- RED: Integration test fails initially (validates vault config usage)
- GREEN: All tests pass after implementation (target: 90%+ success rate)
- REFACTOR: Test fixtures updated, legacy directories created for WorkflowManager compatibility
- COMMIT: Implementation + tests committed separately from docs
- DOCS: Lessons learned document created following P0-VAULT-1 through P0-VAULT-5 format

---

## P1 — Remaining Coordinators (Priority 3 Continuation)

**P1-VAULT-7**: `analytics_coordinator.py` - Migrate analytics and metrics coordination
- Expected complexity: Similar to Priority 1 coordinators
- Estimated time: ~25 minutes
- Pattern: Standard coordinator pattern (proven)

**P1-VAULT-8**: `connection_coordinator.py` - Migrate connection discovery coordination
- Directory paths: permanent_dir, literature_dir, fleeting_dir
- Migration strategy: Same as Priority 1 pattern
- Expected: ~25 minutes, 90%+ test success

**P1-VAULT-9**: `lifecycle_coordinator.py` (if exists) or next coordinator
- Apply proven coordinator pattern
- Maintain backward compatibility during WorkflowManager migration

**Migration Strategy** (Proven from Priority 1):
1. Create integration test first (RED phase)
2. Add vault config import and load in `__init__`
3. Replace directory parameters with vault config properties
4. Update test fixtures to use vault config paths
5. Create legacy directories for WorkflowManager compatibility
6. Verify 90%+ test success (GREEN phase)
7. Document in lessons learned (REFACTOR phase)

**Acceptance Criteria**:
- All 6 remaining coordinators migrated by end of Priority 3
- Average test success rate >90% maintained
- Zero breaking changes to existing functionality
- All lessons learned documents created

---

## P2 — Future Improvements (Priority 4 Preview)

**P2-VAULT**: Automation scripts migration (10+ scripts)
- Scripts in `.automation/scripts/`
- Pattern TBD based on script structure

**P2-INTEGRATION**: WorkflowManager migration
- Enables removal of legacy directory creation in tests
- Unlocks 100% vault config usage across codebase

**P2-DOCS**: Documentation consolidation
- Update ARCHITECTURE.md with vault config patterns
- Consolidate lessons learned into migration guide

---

## Task Tracker

- [x] P0-VAULT-1: promotion_engine.py (Priority 1)
- [x] P0-VAULT-2: workflow_reporting_coordinator.py (Priority 1)
- [x] P0-VAULT-3: review_triage_coordinator.py (Priority 1 complete)
- [x] P0-VAULT-4: core_workflow_cli.py (Priority 2 Module 1)
- [x] P0-VAULT-5: workflow_demo.py (Priority 2 Module 2 complete)
- [In Progress] **P0-VAULT-6: fleeting_note_coordinator.py** (Priority 3 Module 1) ← START HERE
- [Pending] P1-VAULT-7: analytics_coordinator.py (Priority 3 Module 2)
- [Pending] P1-VAULT-8: connection_coordinator.py (Priority 3 Module 3)
- [Pending] P1-VAULT-9: Next coordinator (Priority 3 Module 4)
- [Pending] P1-VAULT-10: Next coordinator (Priority 3 Module 5)
- [Pending] P1-VAULT-11: Next coordinator (Priority 3 Module 6)

---

## TDD Cycle Plan (P0-VAULT-6)

### Red Phase: Write Failing Integration Test
**Objective**: Create test that validates vault config directory usage

**Test File**: `development/tests/unit/test_fleeting_note_coordinator.py` (create if doesn't exist)

**Test to Write**:
```python
class TestFleetingNoteCoordinatorVaultConfigIntegration:
    def test_coordinator_uses_vault_config_directories(self, tmp_path):
        """
        RED PHASE: Verify FleetingNoteCoordinator uses vault config for directory paths.
        
        Expected to FAIL until GREEN phase replaces hardcoded directory parameters.
        Should use knowledge/Fleeting Notes, knowledge/Inbox, etc. from vault_config.
        """
        # Arrange: Create vault config structure
        config = get_vault_config(str(tmp_path))
        
        # Act: Initialize coordinator with base_dir only
        coordinator = FleetingNoteCoordinator(
            base_dir=tmp_path,
            workflow_manager=Mock()  # Mock workflow manager
        )
        
        # Assert: Coordinator uses vault config paths
        assert coordinator.fleeting_dir == config.fleeting_dir
        assert coordinator.inbox_dir == config.inbox_dir
        assert "knowledge" in str(coordinator.fleeting_dir)
```

**Expected Failure**: Constructor signature mismatch (currently takes 4 directory parameters)

### Green Phase: Minimal Implementation
**Objective**: Make tests pass with minimal code changes

**Changes Required**:
1. **Import vault config** (line ~20):
   ```python
   from src.config.vault_config_loader import get_vault_config
   ```

2. **Update constructor** (lines 30-60):
   ```python
   def __init__(
       self,
       base_dir: Path,
       workflow_manager,
       process_callback: Optional[Callable] = None,
       default_quality_threshold: float = 0.7,
   ):
       self.base_dir = Path(base_dir)
       self.workflow_manager = workflow_manager
       
       # Load vault configuration for directory paths
       vault_config = get_vault_config(str(self.base_dir))
       self.fleeting_dir = vault_config.fleeting_dir
       self.inbox_dir = vault_config.inbox_dir
       self.permanent_dir = vault_config.permanent_dir
       self.literature_dir = vault_config.literature_dir
       
       self.process_callback = process_callback
       self.default_quality_threshold = default_quality_threshold
   ```

3. **Update docstring** (lines 1-13):
   - Add vault config integration note
   - Document GitHub Issue #45
   - Note knowledge/ subdirectory usage

**Expected Result**: Integration tests pass, existing tests may need fixture updates

### Refactor Phase: Test Updates & Cleanup
**Objective**: Update all tests to use vault config, maintain backward compatibility

**Test Updates Required**:
1. Find existing test file for fleeting_note_coordinator
2. Update `setUp` methods to use vault config paths
3. Create legacy directories for WorkflowManager (temporary compatibility)
4. Run full test suite to verify no regressions

**Cleanup Opportunities**:
- Consolidate any duplicate directory path logic
- Remove any remaining hardcoded "Fleeting Notes" strings
- Verify consistent knowledge/ subdirectory usage

**Expected Result**: 
- 90%+ test success rate
- All integration tests passing
- No breaking changes
- Clean commit ready

---

## Next Action (For This Session)

**Immediate Task**: Start P0-VAULT-6 RED phase

1. **Locate/create test file**: 
   - Check if `development/tests/unit/test_fleeting_note_coordinator.py` exists
   - Create if needed, following pattern from `test_review_triage_coordinator.py`

2. **Write failing integration test**:
   - Test vault config directory usage
   - Expected failure: constructor signature mismatch
   - File: `development/tests/unit/test_fleeting_note_coordinator.py`

3. **Run test to confirm RED**:
   ```bash
   cd development
   python3 -m pytest tests/unit/test_fleeting_note_coordinator.py::TestFleetingNoteCoordinatorVaultConfigIntegration -v
   ```

4. **Proceed to GREEN phase** once RED confirmed

---

## Success Metrics (Priority 3)

**Per Module**:
- Duration: ~25 minutes average (proven from Priority 1)
- Test success: 90%+ (target based on Priority 1 average)
- Pattern: Coordinator pattern (proven across 3 modules)

**Overall Priority 3**:
- Total modules: 6 coordinators
- Total time: ~150 minutes (6 × 25 min)
- Expected success rate: 90%+ average
- Zero breaking changes required

**Milestone**: 
- Priority 3 complete = 11/13 acceptance criteria met (85%)
- Ready for Priority 4 (automation scripts)
- Major milestone toward Phase 2 completion

---

## Reference Files

**Pattern Source** (Priority 1 success):
- `development/src/ai/review_triage_coordinator.py` (100% success, proven pattern)
- `development/tests/unit/test_review_triage_coordinator.py` (17/17 tests)
- `Projects/ACTIVE/vault-config-p0-vault-3-lessons-learned.md` (documentation)

**Current Module**:
- `development/src/ai/fleeting_note_coordinator.py` (target)
- `development/tests/unit/test_fleeting_note_coordinator.py` (to create/update)

**Documentation**:
- `Projects/ACTIVE/GITHUB-ISSUE-UPDATE-vault-config.md` (progress tracking)
- `.windsurf/rules/updated-development-workflow.md` (TDD guidelines)
- `.windsurf/guides/tdd-methodology-patterns.md` (proven patterns)

---

**Ready to Start**: Would you like me to begin P0-VAULT-6 RED phase by creating the failing integration test in `development/tests/unit/test_fleeting_note_coordinator.py` now in small, reviewable commits?

**Branch**: `feat/vault-config-phase2-priority1` (continue on same branch)  
**Estimated Session Duration**: 25-30 minutes for P0-VAULT-6 complete  
**Confidence**: ✅ VERY HIGH (proven pattern, 5/5 previous modules successful)
