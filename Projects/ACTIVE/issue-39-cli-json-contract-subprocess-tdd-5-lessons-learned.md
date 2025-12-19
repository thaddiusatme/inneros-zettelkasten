# Issue #39 P2: Subprocess Integration Tests for CLI JSON Output Contract

## TDD Iteration 5 Lessons Learned

**Date**: 2025-12-18
**Duration**: ~30 minutes
**Branch**: `feat/issue-39-cli-json-contract-subprocess-tdd-5`
**Status**: ✅ **COMPLETE** - 16/16 tests passing

---

## 🎯 Objective

Add subprocess-level integration tests that catch "it works in unit tests but breaks when invoked as a real CLI" scenarios by running actual CLI entrypoints via `subprocess.run()`.

---

## 🏆 TDD Success Metrics

| Phase | Result |
|-------|--------|
| **RED** | Created 16 tests covering 5 CLIs + error paths + cross-cutting validation |
| **GREEN** | Fixed 2 CLIs (backup_cli.py, core_workflow_cli.py) to emit contract JSON on init failures |
| **REFACTOR** | Added error path tests, consolidated JSONContractValidator helper |
| **COMMIT** | `0be3d52` - 3 files changed, 560 insertions |

---

## 📊 Tests Added

### Per-CLI Contract Validation
- **TestBackupCLIJsonContract**: `backup`, `prune-backups` commands
- **TestScreenshotCLIJsonContract**: `process --dry-run` command
- **TestCoreWorkflowCLIJsonContract**: `status`, `process-inbox` commands
- **TestFleetingCLIJsonContract**: `fleeting-health`, `fleeting-triage` commands
- **TestWeeklyReviewCLIJsonContract**: `weekly-review`, `enhanced-metrics` commands

### Error Path Tests
- **test_backup_cli_with_nonexistent_vault_emits_contract_json**
- **test_core_workflow_cli_with_invalid_vault_emits_contract_json**

### Cross-Cutting Validation
- **test_all_clis_have_consistent_meta_structure** (parametrized, 5 CLIs)

---

## 🐛 Bugs Found & Fixed

### Bug 1: backup_cli.py - No JSON on Init Failure
- **Symptom**: Empty stdout when vault initialization failed in JSON mode
- **Root Cause**: Exception handler printed to stderr without emitting contract JSON
- **Fix**: Added `build_json_response()` call in exception handler when `--format json`

### Bug 2: core_workflow_cli.py - Same Issue
- **Symptom**: No contract JSON emitted when CLI initialization failed
- **Fix**: Separated init from execution, added contract JSON on both failure paths

---

## 💡 Key Insights

### 1. Subprocess Tests Catch Real Integration Issues
Unit tests mock the CLI internals. Subprocess tests catch:
- Missing imports that only manifest at runtime
- Argument parsing bugs not covered by unit tests
- Non-JSON output leaking to stdout (logging, print statements)

### 2. Error Paths Need Explicit Testing
The happy path tests all passed immediately (CLIs were already compliant). The error path tests revealed real bugs where contract JSON wasn't emitted on failures.

### 3. WorkflowManager Creates Missing Directories
Test design lesson: Using `/tmp/does_not_exist` doesn't cause failures because WorkflowManager creates missing directories. Need truly invalid paths like `/nonexistent/...` that can't be created.

### 4. JSONContractValidator Helper is Reusable
The helper class validates:
- JSON parseability
- Required keys: `success`, `errors`, `data`, `meta`
- Required meta keys: `cli`, `subcommand`, `timestamp`
- Type correctness for all fields

---

## 📁 Files Changed

| File | Changes |
|------|---------|
| `development/tests/integration/test_cli_json_output_contract_subprocess.py` | **NEW** - 16 subprocess tests |
| `development/src/cli/backup_cli.py` | Contract JSON on init failure |
| `development/src/cli/core_workflow_cli.py` | Contract JSON on init/exec failures |

---

## 📈 Performance

- **16 tests in 12.13s** (~0.76s/test average)
- Subprocess overhead is unavoidable but acceptable
- No AI calls required (uses dry-run, preview, empty vaults)

---

## 🔜 Next Steps

1. **Consider adding error path tests for remaining CLIs** (fleeting_cli, weekly_review_cli, screenshot_cli)
2. **Merge to main** when ready
3. **Issue #48**: Fix pre-commit pytest hook (uses wrong Python)

---

## 📚 References

- **Contract Spec**: `development/src/cli/cli_output_contract.py`
- **Previous Iteration**: `issue-39-cli-layer-extraction-tdd-iteration-4-lessons-learned.md`
- **TDD Workflow**: `.windsurf/rules/updated-development-workflow.md`
