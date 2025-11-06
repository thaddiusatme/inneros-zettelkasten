# Next Session Prompt: CLI Integration Testing - TDD Iteration

## The Prompt

Let's create a new branch for the next feature: **CLI Automation Script Integration Tests**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

### Updated Execution Plan (focused P0/P1)

**Brief Context**: During end-user testing of CLI migration (Issue #39), we discovered that automation scripts fail when calling `safe_workflow_cli.py` due to inconsistent CLI argument patterns. The scripts pass vault path as a positional argument, but `safe_workflow_cli.py` expects a `--vault` flag. This bug was not caught by existing test coverage.

I'm following the guidance in **`.windsurf/rules/updated-development-workflow.md`** and **`architectural-constraints.md`** (critical path: Add integration tests to prevent CLI argument pattern mismatches in automation scripts).

### Current Status

**Completed**: 
- CLI Migration complete (5/5 automation scripts migrated to dedicated CLIs)
- Migration tests passing (5/5) - but only check for CLI path references, not execution success
- CI smoke tests added - but only test `--help`, not actual command patterns
- PR ready: `feat/cli-migration-iteration-2-supervised-inbox`
- Bug discovered and documented: CLI syntax mismatch in automation scripts

**In progress**: 
- Creating comprehensive integration tests to catch CLI argument pattern issues
- Will work in `development/tests/unit/automation/test_automation_script_cli_integration.py`

**Lessons from last iteration**:
1. **Migration tests are incomplete** - checking string references is not enough; must verify actual CLI execution
2. **Smoke tests need enhancement** - `--help` validation doesn't catch argument pattern mismatches
3. **Inconsistent CLI patterns** - `core_workflow_cli.py` uses positional args, `safe_workflow_cli.py` uses flags
4. **Silent failures in automation** - scripts exit with error but no visibility until manual testing
5. **End-user testing crucial** - this bug only appeared when running scripts on actual vault

---

## P0 — Critical/Unblocker (Fix Broken Automation)

### P0_TASK_1: Quick Fix - Update Automation Scripts CLI Syntax
**Fix the immediate bug before comprehensive testing**:
- Update `.automation/scripts/supervised_inbox_processing.sh` to use `--vault` flag for `safe_workflow_cli.py`
- Update `.automation/scripts/weekly_deep_analysis.sh` to use `--vault` flag
- Update `.automation/scripts/process_inbox_workflow.sh` to use `--vault` flag
- Pattern: Change `python3 $CLI "$VAULT_PATH" command` to `python3 $CLI --vault "$VAULT_PATH" command`
- Test all three scripts execute successfully with backup operations

### P0_TASK_2: Commit Fix to Migration Branch
- Commit syntax fixes with message: "fix: Correct safe_workflow_cli.py argument syntax in automation scripts"
- Update PR description to mention bug fix
- Ensure PR includes both migration completion AND syntax fix

**Acceptance Criteria**:
- ✅ All 3 affected automation scripts run without CLI errors
- ✅ Backup operations complete successfully during script execution
- ✅ No "invalid choice" errors in automation logs
- ✅ Fix committed to migration branch before PR merge

---

## P1 — Integration Testing (Prevent Future Regressions)

### P1_TASK_1: Write Failing Integration Tests (RED Phase)
**Create comprehensive test coverage for CLI execution patterns**:
- Create new test file: `development/tests/unit/automation/test_automation_script_cli_integration.py`
- Test 1: `test_automation_scripts_call_clis_with_correct_syntax` - Verify CLI commands in scripts use correct argument patterns
- Test 2: `test_safe_workflow_cli_accepts_vault_flag` - Validate `safe_workflow_cli.py --vault` works
- Test 3: `test_cli_argument_pattern_consistency` - Check all CLIs for consistent argument handling
- Test 4: `test_automation_script_dry_run_execution` - Run scripts in test mode to validate CLI calls succeed
- Migration strategy: Extend existing `test_cli_migration_scripts.py` pattern with actual execution validation

### P1_TASK_2: Implement Tests and Verify Failures (GREEN Phase)
**Make tests pass with correct implementation**:
- Implement test helper: `parse_script_cli_calls()` to extract CLI invocations from bash scripts
- Implement test helper: `validate_cli_syntax()` to check argument patterns match CLI expectations
- Run tests and verify they fail without the fix (RED)
- Apply P0 fix and verify tests pass (GREEN)
- Add test for each affected script: `test_supervised_inbox_cli_syntax`, `test_weekly_analysis_cli_syntax`, `test_process_inbox_cli_syntax`

### P1_TASK_3: Enhance CI Smoke Tests
**Extend `.github/workflows/cli-smoke-tests.yml`**:
- Add test: Run each CLI with common command patterns (not just `--help`)
- Test `safe_workflow_cli.py --vault /tmp backup --dry-run` (if dry-run supported)
- Test `core_workflow_cli.py /tmp status` to validate positional arg
- Test argument variations to catch inconsistencies early
- Add summary report showing argument pattern compatibility

**Acceptance Criteria**:
- ✅ 4+ new integration tests added and passing
- ✅ Tests fail if CLI syntax reverts to broken pattern
- ✅ CI smoke tests validate actual command execution (not just help)
- ✅ Test coverage catches CLI argument pattern mismatches
- ✅ Comprehensive lessons learned document created

---

## P2 — CLI Standardization (Future Improvement)

### P2_TASK_1: Standardize CLI Argument Patterns
- Update `core_workflow_cli.py` to accept `--vault` flag (in addition to positional for backward compatibility)
- Update all CLIs to use consistent `--vault` flag pattern
- Add deprecation warning for positional vault_path usage
- Update all automation scripts to use `--vault` flag consistently

### P2_TASK_2: Create CLI Argument Standards Document
- Document standard argument patterns for all CLIs
- Add to `CLI-REFERENCE.md` under "CLI Development Guidelines"
- Include examples of correct usage for each common argument type
- Add validation checklist for new CLIs

### P2_TASK_3: Add CLI Argument Pattern Linter
- Create pre-commit hook to validate CLI argument consistency
- Add to CI: Check new CLIs follow argument pattern standards
- Fail if new CLI introduces inconsistent patterns

---

## Task Tracker

- [x] P0_TASK_1 - Quick fix automation scripts CLI syntax ✅ COMPLETE
- [x] P0_TASK_2 - Commit fix to migration branch ✅ COMPLETE
- [x] P1_TASK_1 - Write failing integration tests (RED phase) ✅ COMPLETE
- [x] P1_TASK_2 - Implement tests and verify (GREEN phase) ✅ COMPLETE
- [x] P1_TASK_3 - Enhance CI smoke tests ✅ COMPLETE
- [x] REFACTOR - Clean up test helpers, add documentation ✅ COMPLETE
- [x] COMMIT - Commit with comprehensive message and lessons learned ✅ COMPLETE
- [ ] P2_TASK_1 - CLI standardization (future sprint)
- [ ] P2_TASK_2 - Standards document
- [ ] P2_TASK_3 - Argument pattern linter

---

## TDD Cycle Plan

### Red Phase: Write Failing Tests
1. Create `test_automation_script_cli_integration.py` with:
   - `test_supervised_inbox_calls_safe_workflow_with_vault_flag()` - Assert script uses `--vault` flag
   - `test_weekly_analysis_calls_safe_workflow_with_vault_flag()` - Assert correct syntax
   - `test_process_inbox_calls_safe_workflow_with_vault_flag()` - Assert correct syntax
   - `test_cli_argument_patterns_match_cli_implementation()` - Validate consistency across all CLIs

2. For each test:
   - Parse bash script to extract CLI calls
   - Validate argument pattern matches CLI argparse implementation
   - Assert backup commands use `--vault` flag
   - Expected: Tests FAIL initially (proving they catch the bug)

### Green Phase: Minimal Implementation
1. Apply P0 fix to automation scripts (already done in this session)
2. Run tests - should now PASS
3. Verify automation scripts execute successfully
4. Validate backup operations complete during script runs

### Refactor Phase: Clean Up and Document
1. Extract CLI parsing logic into reusable test helper
2. Add docstrings explaining what each test validates
3. Create test fixtures for mock vault paths
4. Add comprehensive comments explaining CLI argument patterns
5. Document lessons learned in `Projects/ACTIVE/cli-integration-testing-tdd-iteration-lessons-learned.md`

---

## Next Action (for this session)

**Immediate**: Create new branch and begin RED phase

```bash
# Create feature branch
git checkout -b feat/cli-integration-tests

# Create test file with failing tests
# File: development/tests/unit/automation/test_automation_script_cli_integration.py
```

**Test Structure** (RED phase):
```python
class TestAutomationScriptCLIIntegration:
    """Integration tests validating automation scripts use correct CLI argument patterns."""
    
    def test_supervised_inbox_calls_safe_workflow_with_vault_flag(self):
        """RED: supervised_inbox_processing.sh should use --vault flag for safe_workflow_cli.py"""
        script_path = REPO_ROOT / ".automation/scripts/supervised_inbox_processing.sh"
        script_contents = script_path.read_text()
        
        # Parse CLI calls from script
        cli_calls = self._parse_cli_calls(script_contents, "safe_workflow_cli.py")
        
        # Assert uses --vault flag, not positional argument
        for call in cli_calls:
            assert "--vault" in call, f"safe_workflow_cli.py call missing --vault flag: {call}"
            assert not re.match(r"safe_workflow_cli\.py\s+['\"]?/.*['\"]?\s+\w+", call), \
                f"safe_workflow_cli.py using positional vault path (should use --vault flag): {call}"
```

**Target Files**:
- `.automation/scripts/supervised_inbox_processing.sh` (already fixed in P0)
- `.automation/scripts/weekly_deep_analysis.sh` (already fixed in P0)
- `.automation/scripts/process_inbox_workflow.sh` (already fixed in P0)
- `development/tests/unit/automation/test_automation_script_cli_integration.py` (new file to create)

---

## Context Files to Reference

**Essential Reading**:
1. `.windsurf/rules/updated-development-workflow.md` - TDD methodology
2. `development/tests/unit/automation/test_cli_migration_scripts.py` - Existing test patterns
3. `.automation/scripts/supervised_inbox_processing.sh` - Example of fixed script
4. `development/src/cli/safe_workflow_cli.py` - CLI implementation to validate against
5. `GITHUB-ISSUE-cli-syntax-bug.md` - Full bug description and context

**Success Pattern**:
- Follow same TDD structure as CLI migration iterations 1-5
- Write tests FIRST that fail
- Apply minimal fix to make tests pass
- Refactor for clarity and maintainability
- Document learnings comprehensively
- Small, focused commits with clear messages

---

## Expected Outcomes

**After RED Phase**:
- 4+ integration tests written and FAILING
- Tests clearly demonstrate the bug would be caught
- Test helpers implemented for CLI parsing and validation

**After GREEN Phase**:
- All tests PASSING
- Automation scripts execute successfully
- Backup operations complete in scripts
- Zero CLI argument errors

**After REFACTOR Phase**:
- Test code clean and maintainable
- Comprehensive docstrings and comments
- Reusable test helpers extracted
- Lessons learned document complete (250+ lines)

**Final Commit Message**:
```
test: Add CLI integration tests for automation scripts (Issue #XX)

Comprehensive integration tests to prevent CLI argument pattern mismatches

Added tests:
- test_supervised_inbox_calls_safe_workflow_with_vault_flag
- test_weekly_analysis_calls_safe_workflow_with_vault_flag  
- test_process_inbox_calls_safe_workflow_with_vault_flag
- test_cli_argument_patterns_match_cli_implementation

Test helpers:
- parse_script_cli_calls() - Extract CLI invocations from bash scripts
- validate_cli_syntax() - Verify argument patterns match CLI implementation

Prevents regression where automation scripts use incorrect CLI argument syntax.
Tests validate actual CLI execution patterns, not just string references.

Closes #XX (CLI syntax mismatch bug)
Part of Issue #39 (CLI migration)
```

---

Would you like me to:
1. Start with RED phase (create failing integration tests)?
2. Begin with quick P0 fix first, then move to tests?
3. Review existing test patterns before writing new tests?

I recommend: **Option 2** - Apply P0 fix first (automation scripts syntax), verify manually, then write comprehensive tests to prevent regression. This ensures your automation works immediately while building robust test coverage for the future.
