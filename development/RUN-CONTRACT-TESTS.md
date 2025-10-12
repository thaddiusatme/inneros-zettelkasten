# Quick Reference: Running Contract Tests

## Run Contract Tests
```bash
cd development

# Run just the contract tests
pytest tests/unit/test_workflow_cli_contract.py -v

# Run with coverage report
pytest tests/unit/test_workflow_cli_contract.py --cov=src/cli/core_workflow_cli --cov-report=term

# Watch mode (auto-run on file changes)
ptw tests/unit/test_workflow_cli_contract.py -- -v
```

## Expected Output
```
tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_batch_process_inbox_returns_expected_keys PASSED
tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_cli_process_inbox_uses_correct_keys PASSED
tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_cli_handles_empty_inbox PASSED
tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_cli_json_output_preserves_keys PASSED
tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_generate_workflow_report_contract PASSED
tests/unit/test_workflow_cli_contract.py::TestCLIDisplayFormatting::test_process_inbox_display_with_all_failures PASSED
tests/unit/test_workflow_cli_contract.py::TestKeyConsistencyAcrossCommands::test_all_commands_use_standard_keys PASSED

============ 7 passed in 1.26s ============
```

## When to Run

### Before Committing
```bash
# Quick check
pytest tests/unit/test_workflow_cli_contract.py -q

# Only if all pass, commit:
git add .
git commit -m "feat: update workflow processing"
```

### After Changing WorkflowManager
```bash
# Did you change batch_process_inbox() return structure?
pytest tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_batch_process_inbox_returns_expected_keys -v

# Did you change generate_workflow_report() return structure?
pytest tests/unit/test_workflow_cli_contract.py::TestWorkflowManagerCLIContract::test_generate_workflow_report_contract -v
```

### After Changing CoreWorkflowCLI
```bash
# Did you update how CLI displays data?
pytest tests/unit/test_workflow_cli_contract.py::TestCLIDisplayFormatting -v
```

## Interpreting Failures

### Scenario 1: Backend Contract Changed
```
FAILED test_batch_process_inbox_returns_expected_keys
AssertionError: WorkflowManager MUST return 'total_files' key
```
**Action**: Update test if intentional, or fix WorkflowManager if unintentional.

### Scenario 2: CLI Not Using Correct Keys
```
FAILED test_cli_process_inbox_uses_correct_keys
AssertionError: assert "Processed: 44" in output
```
**Action**: Fix CLI to use correct keys from WorkflowManager.

### Scenario 3: Display Format Wrong
```
FAILED test_process_inbox_display_with_all_failures
AssertionError: assert "Total: 60" in output
```
**Action**: Fix CLI display logic to show correct values.

## Pre-Push Hook (Optional)

Create `.git/hooks/pre-push`:
```bash
#!/bin/bash
echo "🧪 Running contract tests before push..."
cd development
pytest tests/unit/test_workflow_cli_contract.py -q

if [ $? -ne 0 ]; then
    echo "❌ Contract tests failed! Push blocked."
    echo "Fix the interface mismatch before pushing."
    exit 1
fi

echo "✅ Contract tests passed!"
```

Make it executable:
```bash
chmod +x .git/hooks/pre-push
```

## Integration with Test Suite

These tests are part of the unit test suite:
```bash
# Run all unit tests (includes contract tests)
pytest tests/unit/ -v

# Run only contract-related tests
pytest tests/unit/ -k "contract" -v
```

## Coverage Targets

Contract tests should maintain **100% coverage** of:
- `CoreWorkflowCLI.process_inbox()`
- `CoreWorkflowCLI.status()`
- `CoreWorkflowCLI.report()`

Check coverage:
```bash
pytest tests/unit/test_workflow_cli_contract.py \
  --cov=src/cli/core_workflow_cli \
  --cov-report=html

# Open coverage report
open htmlcov/index.html
```
