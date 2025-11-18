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

1. **Iteration 3 – Performance tuning and CI alignment (tracked in #48)**  
   - Implement the configuration and test changes described in Issue #48 so that pre-commit lints operate on changed files while CI continues to run full-tree checks.  
   - Decide how `pytest-unit-fast` should be invoked (e.g., pre-push/manual vs every commit).

2. **Iteration 4 – Extended checks (optional)**  
   - Add a type-check hook (e.g., Pyright) under a separate stage or manual invocation.  
   - Consider hooks for security scanning (e.g., `pip-audit`) if they can be scoped and kept fast.

> Suggestion: Keep #26 **open** but mark Iterations 1–2 (baseline hooks + CI alignment + performance investigation) as **complete**, and use #48 to drive performance-focused configuration changes.

---

## ⚠️ Performance Incident – `pre-commit run --all-files` (2025-11-17)

**Context**: On branch `feat/pre-commit-hooks-tdd-iteration-2`, running `pre-commit run --all-files` as part of Iteration 2 performance validation was left running overnight and still had not completed by the next day. The process had to be manually cancelled.

### Reproduction (current state)

1. Branch: `feat/pre-commit-hooks-tdd-iteration-2`  
2. Ensure dependencies are installed (per `Makefile` / CI): `pip install -r requirements.txt` plus `ruff`, `black`, `pyright`, `pytest`, etc.  
3. Install hooks: `pre-commit install`  
4. Run: `pre-commit run --all-files`

Observed behavior on this machine:

- Command ran overnight (>8 hours) without completing.
- No explicit error was reported; the run simply did not finish within a reasonable time window.

### Technical Analysis / Likely Root Cause

Current `.pre-commit-config.yaml` (Iteration 2) has three hooks in the fast subset:

- **Ruff**:
  - Runs:
    - `ruff check development/src development/tests --select E,F,W --ignore E402,E501,E712,W291,W293,F401,F841`
  - Always lints the full `development/src` and `development/tests` trees, regardless of how many files are actually staged.

- **Black**:
  - Runs:
    - `black --check development/src development/tests`
  - Also walks the full `development/src` and `development/tests` trees on every run.

- **pytest-unit-fast**:
  - Runs:
    - `python -m pytest -q -m "not slow" development/tests/unit`
  - This is effectively the same as `make unit` (fast subset of tests, but still ~1800+ tests).

From CI configuration and prior measurements:

- `ci.yml` and `Makefile` indicate that `make unit` alone requires ~15 minutes on CI (Ubuntu) for the current test suite.
- `make lint` (ruff + black) also operates over the full `development/src` and `development/tests` trees.

Putting these together:

- `pre-commit run --all-files` currently triggers:
  - Full-tree ruff lint (`check development/src development/tests ...`).
  - Full-tree black check (`--check development/src development/tests`).
  - Full `pytest -m "not slow" development/tests/unit` run.
- This is effectively **“full CI (lint + unit tests)” via pre-commit**, plus pre-commit’s own environment setup and caching overhead.
- On this machine, the combined cost appears to exceed a practical runtime threshold; leaving it overnight gave the appearance of a stuck process even though each individual command is finite.

### Impact on DevEx and Iteration 2 Goals

- The command we suggested for performance validation (`pre-commit run --all-files`) is **too heavy** to be treated as a normal, recommended workflow for this repo.
- For a large test suite (~1800+ tests) and full lint over the entire tree, `pre-commit run --all-files` behaves like running full CI locally and can tie up a development session for hours.
- This undermines the Iteration 2 goal of making pre-commit a **fast, reliable predictor of CI** for common changes.

### Proposed New GitHub Issue – “Pre-commit all-files run behaves like full CI and is too slow”

**Problem statement**:

> On InnerOS, `pre-commit run --all-files` currently invokes full-tree ruff + black and the entire `pytest -m "not slow" development/tests/unit` suite. This makes pre-commit behave like full CI locally and can take hours (or appear to hang), which is unacceptable for the intended “fast subset” developer workflow.

**Suggested scope / acceptance criteria for the new issue**:

1. **Clarify intended usage**
   - Document that `pre-commit run` on staged changes is the primary “fast subset” workflow.
   - Clearly label `pre-commit run --all-files` as a heavy, CI-like operation that should be used sparingly (e.g., before big refactors, not on every push).

2. **Re-scope lint hooks for better performance**
   - Update `.pre-commit-config.yaml` so:
     - Ruff and Black **do not hard-code** `development/src` and `development/tests` in their args.
     - Instead, let pre-commit pass the affected file list and keep only flags like `--select` / `--ignore` in the args.
   - Update `TestPreCommitConfig` to assert flags and behavior, not exact directory args, so lint runs remain aligned with `make lint` but only touch changed files in the common case.

3. **Reconsider pytest hook behavior**
   - Evaluate moving `pytest-unit-fast` to an optional/manual stage (e.g., `manual` stage or a dedicated command like `pre-commit run pytest-unit-fast`).
   - Keep `pytest-unit-fast` as the recommended **pre-push** or **pre-PR** check, but avoid forcing it on every commit or on `--all-files` runs.

4. **Developer workflow documentation**
   - Update `README-ACTIVE.md` (and any DevEx docs) to explain:
     - Recommended commands: `pre-commit run`, `pre-commit run pytest-unit-fast`, and `make unit`.
     - Expected runtimes for each (fast subset vs. full CI-style runs).
   - Optionally add a `make precommit-fast` target that runs a curated pre-commit subset (e.g., ruff + black) without pytest.

**Outcome**:

- Developers can safely rely on `pre-commit run` for fast feedback on staged changes.
- `pre-commit run --all-files` is explicitly treated as a rare, “full repo health check” tool rather than a default workflow.
- The configuration and tests for pre-commit hooks remain aligned with CI while avoiding CI-level runtimes on every local run.
