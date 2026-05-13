# Pre-commit all-files run behaves like full CI and is too slow

## Context

On branch `feat/pre-commit-hooks-tdd-iteration-2`, we attempted to validate pre-commit performance by running:

```bash
pre-commit install
pre-commit run --all-files
```

The command was left running overnight (>8 hours) and still had not completed by the next day. It had to be manually cancelled. No explicit error was reported; the run simply did not finish within a reasonable time window.

This behavior contradicts the goal for Issue #26 (Pre-commit Hooks) where pre-commit should act as a **fast, reliable predictor of CI** for common changes.

## Steps to Reproduce (current configuration)

1. Check out `feat/pre-commit-hooks-tdd-iteration-2`.
2. Ensure dependencies are installed (per `Makefile` / CI):
   - `pip install -r requirements.txt`
   - plus CLI tooling: `ruff`, `black`, `pyright`, `pytest`, etc.
3. Install hooks with `pre-commit install`.
4. Run `pre-commit run --all-files` from the repository root.

## Expected Behavior

- `pre-commit run --all-files` should complete within a **reasonable amount of time** (e.g. minutes, not hours), even if it runs a larger "health check" subset.
- Day-to-day developer workflow should rely on a **fast subset** (lint + targeted tests) via pre-commit, with CI providing stricter gates.

## Actual Behavior

- `pre-commit run --all-files` effectively behaves like running **full CI locally** and does not complete in a practical timeframe on this machine.
- The command ran overnight (>8 hours) without exiting.

## Technical Analysis

Current `.pre-commit-config.yaml` contains three hooks in the "fast subset":

- **Ruff**:
  - Args:
    ```yaml
    args: [
      "check",
      "development/src",
      "development/tests",
      "--select",
      "E,F,W",
      "--ignore",
      "E402,E501,E712,W291,W293,F401,F841",
    ]
    ```
  - Lints the full `development/src` and `development/tests` trees on every run, regardless of which files are actually staged.

- **Black**:
  - Args:
    ```yaml
    args: ["--check", "development/src", "development/tests"]
    ```
  - Walks the full `development/src` and `development/tests` trees for formatting checks.

- **pytest-unit-fast** (local hook):
  - Entry/args:
    ```yaml
    entry: python -m pytest
    args:
      - "-q"
      - "-m"
      - "not slow"
      - "development/tests/unit"
    ```
  - This is effectively the same as `make unit` (`pytest -q -m "not slow" development/tests/unit`), which currently runs ~1800+ tests.

From `ci.yml` and `Makefile` comments:

- `make unit` alone requires ~15 minutes on CI for the current test suite.
- `make lint` (ruff + black) also operates over the full `development/src` and `development/tests` trees.

When invoked via `pre-commit run --all-files`, all of the above run together, plus pre-commit's own overhead, making the command behave like a full CI run and leading to extremely long runtimes.

## Impact

- Developers cannot safely use `pre-commit run --all-files` as a routine health check; it can tie up a session for hours.
- The current configuration undermines the goal of pre-commit as a **fast CI predictor** for Issue #26.
- There is a risk that developers will disable or avoid pre-commit, reducing the value of the DevEx investment.

## Proposed Changes

1. **Clarify intended usage**
   - Document that `pre-commit run` on staged changes, and targeted test commands, are the primary fast workflows.
   - Clearly label `pre-commit run --all-files` as a heavy, CI-like operation to be used sparingly (e.g., before big refactors or periodically as a health check), rather than on every push.

2. **Re-scope lint hooks for better performance**
   - Update `.pre-commit-config.yaml` so that:
     - Ruff and Black **do not hard-code** `development/src` and `development/tests` as positional args.
     - Instead, rely on pre-commit's default behavior to pass only the affected files, while keeping the `--select` / `--ignore` flags in place.
   - Update `development/tests/unit/test_pre_commit_config.py` so tests assert the presence of flags (`--select`, `--ignore`, `--check`) and alignment with CI behavior, **without** requiring full-tree directory arguments.

3. **Reconsider pytest hook behavior**
   - Evaluate moving `pytest-unit-fast` to a separate or manual stage (e.g., a `manual` stage or a dedicated `pre-commit run pytest-unit-fast` usage pattern) rather than triggering it on every commit or `--all-files` run.
   - Keep `pytest-unit-fast` as the recommended pre-push / pre-PR check, but avoid forcing full unit test runs on every commit.

4. **Developer workflow documentation**
   - Update `Projects/ACTIVE/README-ACTIVE.md` (and any DevEx docs) to explain:
     - Recommended commands for fast feedback (e.g., `pre-commit run`, `pre-commit run pytest-unit-fast`, `make unit`).
     - Expected runtimes and tradeoffs for each (fast subset vs. full CI-style runs).
   - Optionally add a `make precommit-fast` target that runs a curated subset of pre-commit hooks (e.g., ruff + black) without pytest.

## Acceptance Criteria

- `pre-commit run` on typical staged changes (1–10 Python files) completes in **≤ 60 seconds** on a representative development machine.
- `pre-commit run --all-files` is documented as a heavy health check and, when used, completes within a **reasonable bounded time** (e.g., < 20–30 minutes for the current repo size).
- The updated test suite (`test_pre_commit_config.py`) enforces the new configuration contract (flags, behavior, and CI alignment) without locking us into full-tree directory args.
- README / DevEx docs clearly describe how to use pre-commit and how it relates to CI (what is "fast", what is "full").
