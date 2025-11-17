# GitHub Issue Update – Pre-commit Hooks / DevEx Hardening (Issue #26)

**Date**: 2025-11-16  
**Issue**: #26 – Pre-commit Hooks  
**Branch**: `feat/pre-commit-hooks-tdd-iteration-1` (local iteration branch; may be merged under a different name)  

---

## 📝 Summary

**Objective**: Reduce CI surprises and tighten DevEx by adding a pre-commit hook pipeline that runs fast style and test checks locally, aligned with the existing Makefile and CI commands.

This iteration focused on:

- Defining a **test-enforced contract** for `.pre-commit-config.yaml`.
- Implementing a minimal but useful pre-commit configuration with:
  - `ruff` linting.
  - `black` formatting (check-only).
  - A fast pytest subset for unit tests ("not slow" marker).

---

## ✅ Work Completed (TDD Iteration 1)

### 1. New Test Suite for Pre-commit Config

File: `development/tests/unit/test_pre_commit_config.py`

Implemented `TestPreCommitConfig` to enforce expectations about the pre-commit setup:

- Locates the **repository root** by searching for `pytest.ini` and stepping up from `development/`, so `.pre-commit-config.yaml` is expected at the project root.
- `_load_config()`:
  - Asserts `.pre-commit-config.yaml` exists at the repo root.
  - Parses it as YAML and verifies it defines a `repos` list.

Two key tests:

- `test_has_required_repos_and_hooks`:
  - Requires a `ruff` hook (via repo URL containing `ruff` or hook `id == "ruff"`).
  - Requires a `black` hook (via PSF Black repo or hook `id == "black"`).
  - Requires a local fast pytest hook with `id == "pytest-unit-fast"`.

- `test_pytest_hook_uses_not_slow_marker_and_unit_directory`:
  - Asserts the `pytest-unit-fast` hook args include the `not slow` marker.
  - Asserts the hook targets `development/tests/unit` (matching the existing `make unit` target).

> Status: `pytest development/tests/unit/test_pre_commit_config.py -q` → **2/2 tests passing**.

---

### 2. Minimal `.pre-commit-config.yaml`

File: `.pre-commit-config.yaml` (repo root)

Configuration implemented:

- **Ruff** (linting):

  - Repo: `https://github.com/astral-sh/ruff-pre-commit`
  - Hook `id: ruff` with args:
    - `check development/src development/tests`
  - Mirrors the existing `make lint` behavior which already runs `ruff` over these paths.

- **Black** (formatting, check-only):

  - Repo: `https://github.com/psf/black`
  - Hook `id: black` with args:
    - `--check development/src development/tests`
  - Ensures style drift is caught without auto-reformatting on commit.

- **Fast pytest subset**:

  - Local hook `id: pytest-unit-fast`
  - `entry: python -m pytest`
  - Args:
    - `-q`
    - `-m "not slow"`
    - `development/tests/unit`
  - Aligns with `make unit`:
    - Uses the `not slow` marker from `pytest.ini`.
    - Scopes to `development/tests/unit` for faster feedback.

Behavior validated via the new tests; full `pre-commit run --all-files` was attempted but cancelled due to first-run cost on a large repo (hook installation + scanning all files). Normal day-to-day usage will primarily run on staged files and be much faster.

---

## 📊 Impact on Issue #26

This iteration **does not fully exhaust all possible hooks**, but it establishes a solid baseline:

- ✅ **Contract-based tests** now enforce the presence and shape of the pre-commit configuration.
- ✅ `.pre-commit-config.yaml` is in place with Ruff, Black (check-only), and a fast pytest subset aligned with existing Make targets and markers.
- ✅ Developers can install and run hooks locally (`pre-commit install`, `pre-commit run pytest-unit-fast`) to catch lint/style/unit-test issues before CI.

Remaining improvements for future iterations:

- Consider adding an **optional type-check hook** (e.g., `pyright`) under a separate or manual hook so it doesn’t slow every commit.
- Evaluate adding **path filters** or additional skip logic if hooks are still too slow on large change sets.
- Optionally integrate a small Make target (e.g., `make precommit`) that wraps `pre-commit run --all-files` or a curated subset.

---

## 🚀 Next Steps Proposed for the Issue

1. **Iteration 2 – Performance tuning and CI alignment**  
   - Measure typical runtime of `pre-commit` on staged changes.  
   - Refine hook args or file sets if needed.  
   - Confirm CI workflows use the same commands (or strict supersets) as pre-commit.

2. **Iteration 3 – Extended checks (optional)**  
   - Add a type-check hook (e.g., Pyright) under a separate stage or manual invocation.  
   - Consider hooks for security scanning (e.g., `pip-audit`) if they can be scoped and kept fast.

> Suggestion: Keep #26 **open** but mark “Iteration 1 (baseline hooks + tests)” as **complete**, and track performance tuning / extra hooks as follow-up subtasks.
