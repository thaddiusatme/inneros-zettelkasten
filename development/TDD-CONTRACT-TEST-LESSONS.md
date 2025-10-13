# TDD Contract Testing: Preventing Interface Mismatches

**Date**: 2025-10-12  
**Bug Prevented**: WorkflowManager ↔ CoreWorkflowCLI key mismatch  
**Test Suite**: `tests/unit/test_workflow_cli_contract.py`

## The Bug That Was Fixed

### What Happened
```python
# WorkflowManager returned:
{"total_files": 60, "processed": 44, "failed": 16}

# CoreWorkflowCLI expected:
results.get('successful', 0)  # ❌ Key doesn't exist → 0
results.get('total', 0)       # ❌ Key doesn't exist → 0
results.get('failed', 0)      # ✅ Correct key → 16

# Result: Dashboard showed "Total: 0, Processed: 0, Failed: 16"
```

### Root Cause
**No contract test** between backend (WorkflowManager) and frontend (CoreWorkflowCLI).  
When the interface changed, the CLI wasn't updated.

## TDD Solution: Contract Tests

### Test Suite Structure
```
tests/unit/test_workflow_cli_contract.py
├── TestWorkflowManagerCLIContract
│   ├── test_batch_process_inbox_returns_expected_keys  (RED)
│   ├── test_cli_process_inbox_uses_correct_keys       (RED) ← Would have caught bug
│   ├── test_cli_handles_empty_inbox                   (GREEN)
│   └── test_cli_json_output_preserves_keys            (GREEN)
├── TestCLIDisplayFormatting
│   └── test_process_inbox_display_with_all_failures   (REFACTOR)
└── TestKeyConsistencyAcrossCommands
    └── test_all_commands_use_standard_keys            (META)
```

### How It Would Have Prevented The Bug

**Test: `test_cli_process_inbox_uses_correct_keys`**
```python
def test_cli_process_inbox_uses_correct_keys(self, cli, mock_workflow_manager):
    """This test would have FAILED with the original bug."""
    
    # Arrange: Mock WorkflowManager to return ACTUAL structure
    mock_workflow_manager.batch_process_inbox.return_value = {
        "total_files": 60,  # Not "total"
        "processed": 44,    # Not "successful"
        "failed": 16,
        "results": []
    }
    
    # Act: Process inbox
    output = cli.process_inbox(output_format='normal')
    
    # Assert: CLI MUST display the correct values
    assert "Processed: 44" in output  # ❌ WOULD FAIL (showed 0)
    assert "Total: 60" in output      # ❌ WOULD FAIL (showed 0)
    assert "Failed: 16" in output     # ✅ PASSES
```

## Test Results

```bash
$ pytest tests/unit/test_workflow_cli_contract.py -v

tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_batch_process_inbox_returns_expected_keys PASSED
tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_cli_process_inbox_uses_correct_keys PASSED
tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_cli_handles_empty_inbox PASSED
tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_cli_json_output_preserves_keys PASSED
tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_generate_workflow_report_contract PASSED
tests/unit/test_workflow_cli_contract.py::TestCLIDisplayFormatting::test_process_inbox_display_with_all_failures PASSED
tests/unit/test_workflow_cli_contract.py::TestKeyConsistencyAcrossCommands::test_all_commands_use_standard_keys PASSED

============ 7 passed in 1.26s ============
```

## Key TDD Principles Applied

### 1. **Contract Testing**
Tests the interface/contract between components, not internal implementation.

```python
# Good: Tests the contract
assert "total_files" in result

# Bad: Tests internal implementation
assert result._internal_counter == 60
```

### 2. **RED → GREEN → REFACTOR**

**RED Phase** (Write failing test first):
```python
def test_cli_uses_correct_keys(self):
    # This test FAILS because CLI uses wrong keys
    assert "Processed: 44" in output  # FAILS: Shows "Processed: 0"
```

**GREEN Phase** (Make it pass):
```python
# Fix: Use correct keys from WorkflowManager
print(f"Processed: {results.get('processed', 0)}")  # Now PASSES
```

**REFACTOR Phase** (Improve code quality):
```python
# Future: Extract keys to constants
from constants import WORKFLOW_KEYS
print(f"Processed: {results.get(WORKFLOW_KEYS.PROCESSED, 0)}")
```

### 3. **Document The Contract**
Tests serve as **executable documentation** of the interface:

```python
def test_batch_process_inbox_returns_expected_keys(self):
    """
    WorkflowManager.batch_process_inbox() MUST return:
    - total_files: int  (total number of files)
    - processed: int    (successfully processed count)
    - failed: int       (failed processing count)
    - results: list     (individual results)
    """
```

### 4. **Test Edge Cases**
```python
def test_process_inbox_display_with_all_failures(self):
    """Edge case: What if ALL notes fail?"""
    mock_workflow_manager.batch_process_inbox.return_value = {
        "total_files": 60,
        "processed": 0,      # All failed
        "failed": 16,        # Only 16 attempted before timeout
        "results": []
    }
    # Should still show "Total: 60" not "Total: 0"
```

## Future Improvements

### Refactor: Shared Constants Module
```python
# src/constants.py (NEW FILE)
class WorkflowKeys:
    """Shared constants for WorkflowManager ↔ CLI contract."""
    TOTAL_FILES = "total_files"
    PROCESSED = "processed"
    FAILED = "failed"
    RESULTS = "results"

# workflow_manager.py
from constants import WorkflowKeys
return {
    WorkflowKeys.TOTAL_FILES: total,
    WorkflowKeys.PROCESSED: processed_count,
    ...
}

# core_workflow_cli.py
from constants import WorkflowKeys
print(f"Total: {results.get(WorkflowKeys.TOTAL_FILES, 0)}")
```

**Benefits**:
1. ✅ Single source of truth for key names
2. ✅ Typos caught at import time
3. ✅ IDE autocomplete for key names
4. ✅ Easy to update all usages at once

### Add Contract Validation
```python
def validate_batch_process_result(result: dict) -> None:
    """Runtime validation of WorkflowManager contract."""
    required_keys = {"total_files", "processed", "failed", "results"}
    missing = required_keys - set(result.keys())
    if missing:
        raise ValueError(f"Contract violation: missing keys {missing}")
```

## Lessons Learned

### ✅ DO
- **Write contract tests** for all component interfaces
- **Test with realistic data** (not just happy path)
- **Document contracts** in test docstrings
- **Use mocks** to isolate interface testing

### ❌ DON'T
- **Assume interfaces won't change** without tests
- **Test internal implementation** details
- **Skip edge cases** (empty data, all failures, etc.)
- **Write tests after the fact** (write them first!)

## Integration with CI/CD

Add to `.github/workflows/test.yml`:
```yaml
- name: Run Contract Tests
  run: |
    pytest tests/unit/test_workflow_cli_contract.py -v
    if [ $? -ne 0 ]; then
      echo "❌ CONTRACT VIOLATION DETECTED"
      echo "Interface between WorkflowManager and CLI has broken"
      exit 1
    fi
```

## Summary

**Problem**: Interface mismatch between backend and CLI  
**Solution**: Contract tests that verify the interface  
**Result**: Bug would have been caught immediately  
**Time Saved**: Hours of debugging → seconds of test failure feedback  

**TDD FTW!** 🎯
