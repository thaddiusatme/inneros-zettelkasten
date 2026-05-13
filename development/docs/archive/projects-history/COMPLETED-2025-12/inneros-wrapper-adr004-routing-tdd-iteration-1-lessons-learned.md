# TDD Iteration 1: Route inneros workflow to ADR-004 Dedicated CLIs

**Date**: 2025-12-26  
**Duration**: ~25 minutes  
**Branch**: `feat/inneros-wrapper-adr004-routing-tdd-1`  
**Commit**: `e65b2e0`  
**Issue**: #78

## Problem Solved

The unified wrapper `inneros workflow ...` was still routing to deprecated `workflow_demo.py`, creating drift vs ADR-004 dedicated CLIs. This caused:
- Inconsistent behavior between direct CLI usage and wrapper usage
- Maintenance burden keeping both paths synchronized
- Confusion about which CLI to use

## TDD Cycle Summary

### RED Phase (8 failing tests)
- **Challenge**: Testing a script without `.py` extension requires special module loading
- **Solution**: Used `importlib.machinery.SourceFileLoader` to load `inneros` as a module
- **Key insight**: Patch at actual import location (`src.cli.core_workflow_cli.CoreWorkflowCLI`) not module attribute

### GREEN Phase (8 passing tests)
- **Minimal implementation**: Direct CLI class instantiation and method calls
- **Routing logic**:
  - `--weekly-review`, `--enhanced-metrics` → `WeeklyReviewCLI`
  - `--status`, `--process-inbox`, `--report` → `CoreWorkflowCLI`
- **Flag mapping**: `--dry-run` → `preview=True`, `--export-checklist` → `export_path`

### REFACTOR Phase
- Removed unused `os` import
- Black formatting applied
- Integration test verified real CLI execution

## Key Technical Insights

### 1. Module Loading for Scripts Without Extension
```python
loader = importlib.machinery.SourceFileLoader("inneros", str(inneros_path))
spec = importlib.util.spec_from_loader("inneros", loader)
inneros = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inneros)
```

### 2. Patch Location Matters
When imports happen inside functions, patch at the actual import path:
```python
# Wrong - attribute doesn't exist at module level
with patch("inneros.CoreWorkflowCLI"):

# Correct - patch where the class is actually defined
with patch("src.cli.core_workflow_cli.CoreWorkflowCLI"):
```

### 3. Direct CLI Instantiation vs sys.argv Manipulation
**Before** (fragile):
```python
sys.argv = ["workflow_demo.py"] + args
workflow_main()
```

**After** (clean):
```python
cli = CoreWorkflowCLI(vault_path=vault_path)
return cli.status(output_format=output_format)
```

## Files Changed

| File | Lines | Purpose |
|------|-------|---------|
| `inneros` | ~45 | Replace workflow_demo with dedicated CLIs |
| `test_inneros_wrapper_routing.py` | ~340 | 8 comprehensive routing tests |

## Test Coverage

- **8 tests added**: Routing, exit codes, flag mapping
- **Integration verified**: `./inneros workflow --status` produces correct output
- **Zero regressions**: All existing functionality preserved

## Acceptance Criteria Met

✅ `inneros workflow --status` routes to `CoreWorkflowCLI.status()`  
✅ `inneros workflow --process-inbox` routes to `CoreWorkflowCLI.process_inbox()`  
✅ `inneros workflow --weekly-review` routes to `WeeklyReviewCLI.weekly_review()`  
✅ `inneros workflow --enhanced-metrics` routes to `WeeklyReviewCLI.enhanced_metrics()`  
✅ Exit codes propagate from dedicated CLIs  
✅ `--dry-run` maps to `preview=True`  
✅ `--export-checklist` maps to `export_path`  

## Lessons for Future TDD Iterations

1. **Script testing**: Use `SourceFileLoader` for scripts without `.py` extension
2. **Mock placement**: Always patch at the actual import location, not module-level attributes
3. **Direct CLI calls**: Prefer direct method calls over sys.argv manipulation for cleaner code
4. **Pre-commit hooks**: Run `black` before committing to avoid hook failures

## Next Steps

- [ ] Update docs referencing `inneros workflow` to reflect new routing (P1)
- [ ] Consider deprecation warning if `--interactive` is used (not yet supported)
- [ ] Consider consolidating wrapper scripts (P2)
