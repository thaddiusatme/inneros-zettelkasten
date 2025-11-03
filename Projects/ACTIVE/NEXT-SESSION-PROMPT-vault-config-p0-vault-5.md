# Next Session Prompt - Priority 2: CLI Tools Module 2

Here's your next session prompt with fresh context:

---

## The Prompt

Let's continue on branch `feat/vault-config-phase2-priority1` for the next feature: **Vault Configuration Phase 2 - Priority 2 Module 2 (workflow_demo.py)**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

---

## Updated Execution Plan (Priority 2: CLI Tools - Final Module)

**Context**: GitHub Issue #45 - Vault Configuration Centralization. Phase 1 infrastructure complete (vault_config.yaml + loader + 15 passing tests). **Priority 1 COMPLETE**: All 3 core workflow modules migrated (93% avg success, ~25 min per module). **Priority 2 Module 1 COMPLETE**: `core_workflow_cli.py` migrated (93.75% success). Now migrating final Priority 2 CLI tool: `workflow_demo.py` (main CLI entry point) from hardcoded paths to centralized configuration. This completes Priority 2 and enables consistent `knowledge/` subdirectory usage across all CLI tools.

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` and `.windsurf/guides/tdd-methodology-patterns.md` (critical path: **Priority 2 CLI tools migration - workflow_demo.py - MODULE 2 OF 2 - FINAL CLI MODULE**).

---

## Current Status

**Completed**:
- ✅ Phase 1: Vault Config Infrastructure (vault_config.yaml + loader + 15 tests, all passing)
  - Branch: `docs/sprint-1-retrospective`, Commit: `08345c4` 
  - Duration: 2 hours, 6 files created
- ✅ **PRIORITY 1 COMPLETE** (3/3 core workflow modules):
  - P0-VAULT-1: `promotion_engine.py` (23 min, 16/19 tests, 84% success) - Commit: `6caab99` 
  - P0-VAULT-2: `workflow_reporting_coordinator.py` (24 min, 15/16 tests, 94% success) - Commits: `f0188ca`, `c686e54`, `2194b0b` 
  - P0-VAULT-3: `review_triage_coordinator.py` (27 min, 17/17 tests, **100% success** 🎉) - Commits: `626c04f`, `6e19193` 
  - **Average**: 25 min/module, 93% success rate, pattern validated
- ✅ **PRIORITY 2 MODULE 1 COMPLETE**:
  - P0-VAULT-4: `core_workflow_cli.py` (30 min, 15/16 tests, 93.75% success) - Commits: `b27d742`, `0a2ccc3`
  - **Pattern Established**: CLI independence (loads own vault config)
  - **CLI-Specific Strategy**: Backward compatibility with unmigrated WorkflowManager

**In progress**:
- P0-VAULT-5: `workflow_demo.py` migration (Priority 2 Module 2 - FINAL CLI TOOL)
- Target: Main CLI entry point path handling and vault config integration
- File: `development/src/cli/workflow_demo.py` 
- Test file: `development/tests/unit/test_workflow_demo.py` (location TBD)

**Lessons from last iteration (P0-VAULT-4)**:
- **CLI Independence Pattern Works**: CLIs load their own vault config (don't rely on WorkflowManager)
- **Backward Compatibility Essential**: Create legacy directories for unmigrated components
- **93.75% Success Achievable**: 15/16 tests passing despite WorkflowManager not migrated
- **Property-Based API**: `cli.inbox_dir` prevents string concatenation errors
- **Test File Creation**: No existing tests meant clean vault config integration
- **Single Expected Failure**: WorkflowManager.repair_inbox_metadata() uses hardcoded paths (not CLI issue)
- **Duration Accurate**: CLI tools take ~30 min (slightly longer than coordinators due to complexity)
- **Integration Tests Critical**: Validate knowledge/ subdirectory usage explicitly

---

## P0 — Critical/Unblocker (Priority 2 Module 2: Final CLI Tool)

**Migrate workflow_demo.py to Vault Config** - TDD RED → GREEN → REFACTOR cycle:

**Files to Investigate First**:
```bash
# Read the main CLI entry point to identify hardcoded paths
development/src/cli/workflow_demo.py

# Check for existing test structure
find development/tests -name "*workflow_demo*" -type f
```

**Expected Path Patterns** (to be confirmed):
```python
# Likely patterns to replace (based on P0-VAULT-4 experience):
# - Path construction: base_dir / "Inbox"
# - Argument defaults: default="Inbox/"
# - Display strings: "Processing Inbox/ directory..."
# - Command path handling: Multiple commands may reference directories
# - Export paths: output_dir / "reports"

# NEW pattern (proven from P0-VAULT-4):
vault_config = get_vault_config(str(base_dir))
inbox_dir = vault_config.inbox_dir
fleeting_dir = vault_config.fleeting_dir
# Use config properties throughout all commands
```

**Import Statement** (to add):
```python
from src.config.vault_config_loader import get_vault_config
```

**CLI Independence Pattern** (proven from P0-VAULT-4):
- CLI loads its own vault config in `__init__`
- Stores directory properties as instance variables
- Uses these properties instead of WorkflowManager's paths
- Maintains backward compatibility with legacy directories in tests

**Acceptance Criteria**:
- ✅ New integration test validates CLI uses `knowledge/Inbox` paths
- ✅ All existing workflow_demo tests updated for vault config compatibility
- ✅ All workflow_demo tests pass (target: >90% success rate, ideally 100%)
- ✅ CLI help text updated if paths mentioned
- ✅ Module docstring documents vault config integration
- ✅ Commit follows established pattern with detailed message
- ✅ Duration: ~30 minutes (consistent with P0-VAULT-4)

---

## P1 — Verification & Priority 2 Completion (Testing + Milestone)

**1. Integration Testing**:
```bash
# Run workflow_demo module tests
cd development && python3 -m pytest tests/unit/test_workflow_demo.py -v

# Verify CLI commands work with vault config
# Expected: All commands properly resolve knowledge/Inbox paths
```

**2. CLI-Specific Validation**:
- Verify all subcommands handle config paths correctly
- Check --help output doesn't reference old paths
- Validate export/output paths use config
- Test command composition (multiple commands in sequence)

**3. Priority 2 Completion Celebration**:
- **Milestone**: ALL CLI tools migrated (2/2 complete)
- Document CLI-specific patterns vs coordinator patterns
- Prepare summary for Priority 3 kick-off
- Update project tracking documents

**Acceptance Criteria**:
- ✅ Integration tests pass for all workflow_demo commands
- ✅ Manual CLI verification complete (no hardcoded path references)
- ✅ Priority 2 COMPLETE: Both CLI tools migrated
- ✅ Lessons learned captures workflow_demo-specific insights
- ✅ Pattern documented for Priority 3 (remaining coordinators)

---

## P2 — Documentation & Phase Planning (Future Priorities)

**Complete Priority 2 Module 2 Documentation**:
1. Create `vault-config-p0-vault-5-lessons-learned.md` 
2. Document workflow_demo CLI patterns vs core_workflow_cli patterns
3. Update GitHub issue with Priority 2 COMPLETE status
4. Celebrate 50% → 58% progress milestone (5/12 → 7/12 criteria)

**Prepare for Priority 3** (6 Remaining Coordinators):
- **Module List**:
  - `fleeting_note_coordinator.py`
  - `analytics_coordinator.py`
  - `note_processing_coordinator.py`
  - `safe_image_processing_coordinator.py`
  - `orphan_remediation_coordinator.py`
  - `batch_processing_coordinator.py`
- **Estimated Time**: ~150 minutes (6 × 25 min avg)
- **Pattern**: Same as Priority 1 (proven coordinator pattern)

**Long-term Roadmap**:
- **Priority 3**: 6 remaining coordinators (~150 min, ~2.5 hours)
- **Priority 4**: Automation scripts (10+ scripts, pattern TBD)
- **Priority 5**: Documentation consolidation
- **Final**: GitHub Issue #45 completion and merge to main

---

## Task Tracker

- [x] **INFRA-PHASE-1**: Vault config infrastructure (complete)
- [x] **P0-VAULT-1**: `promotion_engine.py` migration (84% success)
- [x] **P0-VAULT-2**: `workflow_reporting_coordinator.py` migration (94% success)
- [x] **P0-VAULT-3**: `review_triage_coordinator.py` migration (100% success) ✨ **PRIORITY 1 COMPLETE**
- [x] **P0-VAULT-4**: `core_workflow_cli.py` migration (93.75% success)
- [In progress] **P0-VAULT-5**: `workflow_demo.py` migration (Priority 2 Module 2 - FINAL CLI)
- [Pending] **P2-VAULT-6**: `fleeting_note_coordinator.py` migration (Priority 3 start)
- [Pending] **P2-VAULT-7**: `analytics_coordinator.py` migration (Priority 3)
- [Pending] **P2-VAULT-8**: `note_processing_coordinator.py` migration (Priority 3)
- [Pending] **P2-VAULT-9**: `safe_image_processing_coordinator.py` migration (Priority 3)
- [Pending] **P2-VAULT-10**: `orphan_remediation_coordinator.py` migration (Priority 3)
- [Pending] **P2-VAULT-11**: `batch_processing_coordinator.py` migration (Priority 3)
- [Pending] **P3-VAULT-12+**: Automation scripts (10+ scripts, Priority 4)

---

## TDD Cycle Plan

### Red Phase
**Objective**: Write failing test proving workflow_demo uses hardcoded paths

**Test to Create** (in `test_workflow_demo.py` or new file):
```python
class TestVaultConfigIntegration:
    """Test workflow_demo integration with vault configuration."""
    
    def test_workflow_demo_uses_vault_config_for_directory_paths(self, tmp_path):
        """
        RED PHASE: Verify workflow_demo uses vault config for directory resolution.
        
        Expected to FAIL until GREEN phase replaces hardcoded paths.
        """
        from src.config.vault_config_loader import get_vault_config
        from src.cli.workflow_demo import WorkflowDemo  # adjust import based on actual structure
        
        config = get_vault_config(str(tmp_path))
        demo = WorkflowDemo(vault_path=tmp_path)  # adjust initialization
        
        # Should use knowledge/Inbox from config
        assert hasattr(demo, 'inbox_dir'), "workflow_demo should have inbox_dir property"
        assert "knowledge" in str(demo.inbox_dir)  # adjust property name
        assert demo.inbox_dir == config.inbox_dir
```

**Expected**: Test FAILS with `AssertionError: workflow_demo should have inbox_dir property` or similar

### Green Phase
**Objective**: Minimal implementation to make test pass

**Implementation Steps**:
1. Add vault config import to `workflow_demo.py` 
2. In initialization, load vault config and store directory properties
3. Replace any hardcoded path construction with `vault_config.inbox_dir` (and other paths)
4. Update path references in command methods to use stored properties
5. Verify new integration test passes
6. Check for regressions (expected: ~50-90% initial pass rate based on P0-VAULT-4 experience)

**Expected**: New test passes, existing tests may need fixture updates (normal for GREEN)

### Refactor Phase
**Objective**: Fix all tests, achieve >90% success rate (target: 100%)

**Cleanup Tasks**:
1. Locate or create test file for workflow_demo
2. Update test fixtures to use vault config paths
3. Replace `base_dir / "Inbox"` patterns in test assertions
4. Fix argument default value tests (if applicable)
5. Update display/help text tests (if path strings present)
6. Create legacy directories for WorkflowManager compatibility (TODO markers)
7. Update module docstring with vault config documentation
8. Verify all tests pass (target: >90%, ideally 100%)

**Expected**: All (or nearly all) tests passing, zero vault config regressions

---

## Next Action (for this session)

**Immediate task**: TDD Cycle for `workflow_demo.py` migration (P0-VAULT-5) - **PRIORITY 2 MODULE 2 - FINAL CLI TOOL**

**Step 1: Investigation** (5 min)
- Read `development/src/cli/workflow_demo.py` to identify structure and hardcoded paths
- Identify which commands/methods use directory paths
- Check for existing test file location
- Map out all path references (likely more than core_workflow_cli.py)

**Step 2: RED Phase** (5 min)
- Create or locate test file for workflow_demo
- Write failing integration test validating CLI uses `knowledge/Inbox` paths
- Run test: `pytest development/tests/unit/test_workflow_demo.py::TestVaultConfigIntegration -v` 
- **Expected**: Test FAILS (AssertionError or attribute error)

**Step 3: GREEN Phase** (10 min)
- Import: `from src.config.vault_config_loader import get_vault_config` 
- In `__init__` or initialization: Load vault config, store directory properties
- Replace identified hardcoded paths with vault config properties
- Run new test: Should PASS
- Run all workflow_demo tests: Check for regressions (~50-90% pass rate expected)

**Step 4: REFACTOR Phase** (10 min)
- Update test fixtures systematically
- Fix path-related assertions in existing tests
- Update CLI-specific tests (commands, help text, output formatting)
- Create legacy directories for WorkflowManager compatibility
- Verify all tests pass (target: >90%, stretch: 100%)

**Step 5: COMMIT** (2 min)
- Commit message: `feat: migrate workflow_demo to vault config (P0-VAULT-5)` 
- Include: paths migrated, test results, Priority 2 Module 2 complete, FINAL CLI TOOL

**Step 6: LESSONS LEARNED** (5 min)
- Create `vault-config-p0-vault-5-lessons-learned.md` 
- Document workflow_demo-specific patterns vs core_workflow_cli patterns
- Celebrate Priority 2 COMPLETE milestone
- Note transition preparation for Priority 3

**Step 7: PRIORITY 2 CELEBRATION** (3 min)
- Update GitHub issue tracking (Priority 2 COMPLETE)
- Document CLI migration patterns summary
- Prepare Priority 3 kickoff notes

**Total Time**: ~40 minutes (slightly longer due to main CLI entry point complexity)

---

## 📋 Reference Materials

### Configuration Files
- `development/vault_config.yaml` - Central configuration
- `development/src/config/vault_config_loader.py` - Loader API
- `development/tests/unit/test_vault_config_loader.py` - 15 tests (all passing)

### Documentation
- `Projects/ACTIVE/vault-config-centralization-plan.md` - Complete migration plan
- `Projects/ACTIVE/vault-config-p0-vault-4-lessons-learned.md` - Latest CLI iteration (93.75% success)
- `Projects/ACTIVE/GITHUB-ISSUE-UPDATE-vault-config.md` - GitHub issue tracking (updated)

### Git References
- **Current Branch**: `feat/vault-config-phase2-priority1` (continue - DO NOT CREATE NEW BRANCH)
- **Latest Commits**:
  - `b27d742` - P0-VAULT-4 implementation (core_workflow_cli)
  - `0a2ccc3` - P0-VAULT-4 documentation
  - `8c76d7b` - GitHub issue tracking update
- **Next Commit**: P0-VAULT-5 (workflow_demo.py)

### Target Files
- **Module**: `development/src/cli/workflow_demo.py` (to investigate)
- **Tests**: Find existing test file or create new one
- **Pattern**: Same CLI independence as P0-VAULT-4, adapted for main entry point

---

## 💡 Success Pattern (Proven across 4 modules)

### CLI Migration Pattern (from P0-VAULT-4)
```python
# Step 1: Import at top of file
from src.config.vault_config_loader import get_vault_config

# Step 2: In initialization, replace hardcoded paths
# OLD (don't rely on WorkflowManager):
# (access via self.workflow_manager.inbox_dir)

# NEW (CLI independence):
vault_config = get_vault_config(str(self.vault_path))
self.inbox_dir = vault_config.inbox_dir
self.fleeting_dir = vault_config.fleeting_dir
```

### Testing Pattern (with Backward Compatibility)
```python
def test_cli_uses_vault_config(tmp_path):
    """Verify CLI uses vault config for paths."""
    from src.config.vault_config_loader import get_vault_config
    
    config = get_vault_config(str(tmp_path))
    cli = CLIClass(vault_path=tmp_path)
    
    assert "knowledge" in str(cli.inbox_dir)
    assert cli.inbox_dir == config.inbox_dir
```

### Test Fixture Update Pattern
```python
# OLD:
vault = Path(tmpdir)
inbox = vault / "Inbox"
inbox.mkdir()

# NEW (with backward compatibility):
vault = Path(tmpdir)
config = get_vault_config(str(vault))
config.inbox_dir.mkdir(parents=True, exist_ok=True)

# Legacy directories for WorkflowManager compatibility (TODO: remove)
(vault / "Permanent Notes").mkdir(parents=True, exist_ok=True)
(vault / "Literature Notes").mkdir(parents=True, exist_ok=True)
(vault / "Fleeting Notes").mkdir(parents=True, exist_ok=True)
```

---

## 🎯 Success Metrics

**This Iteration Target**:
- ⬜ 1 new integration test passes
- ⬜ >90% existing tests pass (stretch: 100% like P0-VAULT-3)
- ⬜ workflow_demo paths migrated to vault config
- ⬜ Module docstring updated
- ⬜ Duration: ~30-40 minutes (main CLI entry point buffer)

**Priority 2 Milestone** (after this module complete):
- ⬜ **PRIORITY 2 COMPLETE**: Both CLI tools migrated (2/2) 🎉
- ⬜ CLI-specific patterns documented and proven
- ⬜ Ready for Priority 3 (6 remaining coordinators)
- ⬜ Progress: 50% → 58% (7/12 acceptance criteria met)

---

Would you like me to implement **P0-VAULT-5 (workflow_demo.py migration)** now in small, reviewable commits following the proven TDD cycle?
