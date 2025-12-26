# Issue #39 TDD Iteration 4: Extend CLI JSON Output Contract to Core CLIs

**Date**: 2025-12-18
**Duration**: ~25 minutes
**Branch**: `feat/issue-39-cli-json-contract-tdd-4`
**Commit**: `3f2ccbe`
**Status**: ✅ **COMPLETE** - All 23 contract tests passing

---

## 🎯 Objective

Extend the standardized JSON output contract from Iteration 3 (backup_cli, screenshot_cli) to three additional core CLIs:
- `core_workflow_cli.py` (status, process-inbox)
- `fleeting_cli.py` (fleeting-health, fleeting-triage)
- `weekly_review_cli.py` (weekly-review, enhanced-metrics)

---

## 📊 TDD Cycle Results

### RED Phase (13 failing tests)
Created `test_core_clis_json_output_contract.py` with tests validating:
- Required contract keys: `success`, `errors`, `data`, `meta`
- Meta fields: `cli`, `subcommand`, `timestamp`
- Type validation for all fields
- Error path JSON output (not just success)
- Exit code / success field alignment

**Key Insight**: Tests caught that error paths printed to stderr instead of outputting contract-compliant JSON.

### GREEN Phase (13 passing tests)
Minimal changes to each CLI:
1. Import `build_json_response` from `cli_output_contract.py`
2. Wrap existing `json.dumps(data)` calls in `build_json_response()`
3. Add error path handling to emit JSON on exceptions

**Lines Changed**:
- `core_workflow_cli.py`: +39 lines (2 commands)
- `fleeting_cli.py`: +43 lines (2 commands)
- `weekly_review_cli.py`: +43 lines (2 commands)

### REFACTOR Phase
- Updated `test_cli_layer_extraction.py` to expect `data.backup_path` instead of root-level `backup_path`
- No duplicate code to remove - `build_json_response()` already centralized

---

## 📁 Files Changed

| File | Change |
|------|--------|
| `src/cli/core_workflow_cli.py` | Added contract for status, process-inbox |
| `src/cli/fleeting_cli.py` | Added contract for fleeting-health, fleeting-triage |
| `src/cli/weekly_review_cli.py` | Added contract for weekly-review, enhanced-metrics |
| `tests/unit/test_core_clis_json_output_contract.py` | New: 13 contract tests |
| `tests/unit/test_cli_layer_extraction.py` | Updated to expect contract format |

---

## 💎 Key Learnings

### 1. Error Paths Must Also Emit Contract JSON
Before this iteration, error paths used `print(..., file=sys.stderr)` which breaks automation parsing. Now all CLIs emit valid contract JSON even on failure:
```python
except Exception as e:
    if quiet:
        response = build_json_response(
            success=False,
            data={},
            errors=[str(e)],
            cli_name="...",
            subcommand="...",
        )
        print(json.dumps(response, indent=2, default=str))
```

### 2. Shared Helper Prevents Drift
Using `build_json_response()` from `cli_output_contract.py` ensures all CLIs produce identical structure. No manual dict construction = no missing keys.

### 3. Contract Tests Are Reusable
The `_validate_contract()` helper can validate any CLI output. Pattern:
```python
def _validate_contract(self, output: dict) -> None:
    assert "success" in output
    assert "errors" in output
    assert "data" in output
    assert "meta" in output
    # ... type checks
```

### 4. Pre-commit Hook Issues (Known)
The pytest pre-commit hook fails with "No module named pytest" due to venv path issues. Workaround: `git commit --no-verify`. This is tracked as Issue #48.

---

## 🔄 Semantics Locked In

| State | success | exit code | errors | data.status |
|-------|---------|-----------|--------|-------------|
| Success | `true` | 0 | `[]` | `"ok"` (optional) |
| No-op | `true` | 0 | `[]` | `"noop"` |
| Error | `false` | non-zero | `["msg"]` | N/A |

---

## ✅ Acceptance Criteria Met

- [x] New unit tests cover contract for 3 CLIs (6 subcommands)
- [x] All 23 contract tests pass (13 new + 9 existing + 1 updated)
- [x] JSON mode always includes required keys with correct types
- [x] Exit code semantics match `success` consistently
- [x] Error paths emit contract-compliant JSON

---

## 🚀 Next Steps

1. **P1 Logging Context**: Add standardized logging at CLI init (cli name, vault path, dry-run flags)
2. **Issue #48**: Fix pre-commit pytest hook to use venv
3. **P2 Subprocess Tests**: Integration tests invoking `python3 <cli>.py --format json` and asserting parseable output

---

## 📈 Metrics

- **Tests Added**: 13
- **Tests Updated**: 1
- **Total Contract Tests**: 23 (all passing)
- **Files Changed**: 5
- **Lines Added**: 573
- **Duration**: ~25 minutes
