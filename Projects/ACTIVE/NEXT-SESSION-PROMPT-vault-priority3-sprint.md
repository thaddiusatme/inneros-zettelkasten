# Next Session: Vault Configuration Priority 3 - Analytics Coordinator Migration

Let's create a new branch for the next feature: **Vault Config P1-VAULT-7 (analytics_coordinator.py)**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

## Updated Execution Plan (Priority 3 Coordinators Sprint)

**Context**: Vault configuration centralization at 55% complete (6/11 modules). Priority 1-2 fully migrated (5/5 modules, 100%). Starting Priority 3 coordinators with proven TDD pattern from P0-VAULT-6.

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` and the proven pattern from `Projects/ACTIVE/vault-config-p0-vault-6-lessons-learned.md` (critical path: Complete Priority 3 coordinators to enable automation scripts migration).

## Current Status

**Completed**:

- ✅ P0-VAULT-1 through P0-VAULT-6 (6 modules, 77/80 tests passing)
- ✅ Priority 1 (Core Workflow): 3/3 complete
- ✅ Priority 2 (CLI Tools): 2/2 complete
- ✅ Priority 3: 1/6 coordinators (fleeting_note_coordinator.py)

**In progress**:

- 🔄 P1-VAULT-7: `analytics_coordinator.py` migration
- File: `development/src/ai/coordinators/analytics_coordinator.py`

**Lessons from last iteration** (P0-VAULT-6):


- Complete TDD cycle (RED → GREEN → REFACTOR) works exceptionally well
- Test-first approach catches integration issues early
- Systematic refactoring (3 separate commits) improves code quality
- 100% test success rate (22/22) validates thorough approach
- ~60 minutes per coordinator when following proven pattern

## P0 — Critical/Unblocker (Complete Priority 3 Sprint)

**P1-VAULT-7**: Migrate `analytics_coordinator.py` to use vault config

- Import `get_vault_config()` from `development/src/config/vault_config_loader.py`
- Replace hardcoded `"Inbox/"` paths with `config.inbox_dir`
- Update `__init__` to accept optional `vault_config_path` parameter
- Add vault config integration tests (3-5 new tests)
- Verify existing 15+ tests still pass with zero regressions

**P1-VAULT-8**: Migrate `connection_coordinator.py`

- Follow same pattern as P1-VAULT-7
- Update path references to use vault config
- Maintain test coverage

**P1-VAULT-9**: Migrate `safe_image_processing_coordinator.py`

- Follow established pattern
- Focus on OneDrive → Inbox path configurations

**Acceptance Criteria**:


- All 5 Priority 3 coordinators migrated to vault config
- 95%+ test success rate maintained (target: 100%)
- Zero regressions in existing functionality
- Each migration documented with lessons learned
- GitHub Issue #45 updated to show Priority 3: 6/6 (100%)

## P1 — Enable Automation Scripts Migration (After Priority 3)

**P2-VAULT-12**: Begin Priority 4 automation scripts

- Update `.automation/scripts/repair_metadata.py`
- Update `.automation/scripts/validate_metadata.py`
- Batch process remaining 8+ scripts

**Update GitHub Issue #45**:

- Mark Priority 3 checkboxes as complete
- Update acceptance criteria progress
- Add commit references and test results

**Acceptance Criteria**:


- Priority 3 section shows 6/6 (100%)
- Acceptance criteria updated to 4/8 or 5/8
- Clear path to Priority 4 documented

## P2 — Documentation & Cleanup (Post-Migration)

**Documentation Updates**:

- Update `README.md` with vault config usage examples
- Update `CLI-REFERENCE.md` to show config paths
- Update starter pack templates

**Integration Testing**:

- Manual testing with live vault
- Verify all workflows use `knowledge/Inbox`
- End-to-end smoke tests

**GitHub Issue Closure**:


- Complete Phase 3: Testing & Verification
- Complete Phase 4: Documentation
- Close Issue #45 with completion summary

## Task Tracker

- [In progress] P1-VAULT-7: analytics_coordinator.py
- [Pending] P1-VAULT-8: connection_coordinator.py
- [Pending] P1-VAULT-9: safe_image_processing_coordinator.py
- [Pending] P1-VAULT-10: Additional coordinator
- [Pending] P1-VAULT-11: Additional coordinator
- [Pending] GitHub Issue #45 update (Priority 3 complete)

## TDD Cycle Plan

**Red Phase**: Create failing tests for analytics_coordinator vault config integration

- Test that coordinator accepts `vault_config_path` parameter
- Test that coordinator uses `config.inbox_dir` instead of hardcoded paths
- Test that coordinator handles missing/invalid config gracefully
- Verify existing tests fail with new config requirement

**Green Phase**: Minimal implementation to pass all tests

- Import `get_vault_config()` and integrate into `__init__`
- Replace hardcoded `"Inbox/"` with `config.inbox_dir`
- Add config loading with fallback to default paths
- Ensure all 15+ existing tests pass + 3-5 new tests

**Refactor Phase**: Extract utilities and improve code quality


- Extract config loading helper if pattern emerges
- Improve error messages for config failures
- Add type hints for config parameter
- Update docstrings to document config behavior

## Next Action (for this session)

**Start P1-VAULT-7**: Migrate `analytics_coordinator.py` to vault config

1. **Create branch**: `feat/vault-config-p1-vault-7-analytics-coordinator`
2. **RED Phase**: Write failing tests in `development/tests/ai/coordinators/test_analytics_coordinator.py`
    - Add test for vault config integration
    - Add test for inbox path resolution
    - Run tests to verify they fail appropriately
3. **GREEN Phase**: Implement minimal changes to pass tests
    - Import and integrate vault config
    - Replace hardcoded paths
    - Verify all tests pass
4. **REFACTOR Phase**: Improve code quality (if needed)
5. **COMMIT**: Create detailed commit with test results
6. **DOCUMENT**: Create `vault-config-p1-vault-7-lessons-learned.md`

**Expected Duration**: ~60 minutes based on P0-VAULT-6 pattern

Would you like me to implement the RED phase for `analytics_coordinator.py` now in small, reviewable commits?
