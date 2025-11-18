"""TDD RED Phase: Pre-commit configuration tests (Issue #26).

This suite encodes expectations for .pre-commit-config.yaml so that
local pre-commit hooks match CI-style gates:
- Ruff linting
- Black formatting
- A fast pytest subset for unit tests (not slow)
"""

from pathlib import Path

import yaml


class TestPreCommitConfig:
    """Tests for the pre-commit configuration at the repo root."""

    def _find_repo_root(self) -> Path:
        """Locate the repository root by searching for pytest.ini."""
        start = Path(__file__).resolve()
        for parent in [start] + list(start.parents):
            if (parent / "pytest.ini").exists():
                # If pytest.ini is under the development/ directory, treat its
                # parent as the repository root so .pre-commit-config.yaml
                # lives at the actual project root.
                if parent.name == "development":
                    return parent.parent
                return parent

        # Fallback: assume tests live under development/ and root is parent
        return start.parent

    def _load_config(self):
        """Load and parse .pre-commit-config.yaml from the repo root."""
        root = self._find_repo_root()
        config_path = root / ".pre-commit-config.yaml"
        assert (
            config_path.exists()
        ), "Expected .pre-commit-config.yaml at repository root for pre-commit hooks"

        content = config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(content)

        assert isinstance(config, dict), "Pre-commit config should be a YAML mapping"
        assert "repos" in config, "Pre-commit config must define a 'repos' list"

        return config

    def _build_hooks_by_id(self, repos):
        """Build a mapping from hook id to hook config for easier assertions."""
        hooks_by_id = {}
        for repo in repos:
            for hook in repo.get("hooks", []):
                hook_id = hook.get("id")
                if hook_id:
                    hooks_by_id[hook_id] = hook
        return hooks_by_id

    def _collect_run_commands(self, workflow: dict) -> str:
        """Collect all shell commands from a GitHub Actions workflow for inspection."""
        commands = []
        for job in workflow.get("jobs", {}).values():
            for step in job.get("steps", []):
                run = step.get("run")
                if isinstance(run, str):
                    commands.append(run)
        return "\n".join(commands)

    def test_has_required_repos_and_hooks(self):
        """Config should define ruff, black, and a fast pytest hook."""
        config = self._load_config()
        repos = config["repos"]

        found_ruff = False
        found_black = False
        found_pytest_fast = False

        for repo in repos:
            repo_url = repo.get("repo", "")
            hooks = repo.get("hooks", [])

            # Ruff: either via repo URL or a hook with id 'ruff'
            if "ruff" in repo_url or any(h.get("id") == "ruff" for h in hooks):
                found_ruff = True

            # Black: either via PSF black repo or hook id 'black'
            if "psf/black" in repo_url or any(h.get("id") == "black" for h in hooks):
                found_black = True

            # Fast pytest subset hook: enforce a stable id
            if any(h.get("id") == "pytest-unit-fast" for h in hooks):
                found_pytest_fast = True

        assert found_ruff, "Pre-commit config must include a ruff hook"
        assert found_black, "Pre-commit config must include a black hook"
        assert (
            found_pytest_fast
        ), "Pre-commit config must include a fast pytest hook with id 'pytest-unit-fast'"

    def test_pytest_hook_uses_not_slow_marker_and_unit_directory(self):
        """Fast pytest hook should run unit tests with 'not slow' marker in development/tests/unit."""
        config = self._load_config()
        repos = config["repos"]

        pytest_hook = None
        for repo in repos:
            for hook in repo.get("hooks", []):
                if hook.get("id") == "pytest-unit-fast":
                    pytest_hook = hook
                    break
            if pytest_hook is not None:
                break

        assert pytest_hook is not None, "pytest-unit-fast hook must be defined in pre-commit config"

        args = pytest_hook.get("args", [])
        joined_args = " ".join(args)

        assert (
            "not slow" in joined_args
        ), "pytest-unit-fast should run with '-m \"not slow\"' or equivalent to skip slow tests"
        assert (
            "development/tests/unit" in joined_args
        ), "pytest-unit-fast should target development/tests/unit for fast unit coverage"

    def test_fast_pre_commit_hooks_align_with_ci_commands(self):
        """Fast pre-commit hooks should mirror Make targets and CI-lite/CI commands.

        This encodes Issue #26 Iteration 2 contract:
        - Pre-commit ruff/black/pytest-unit-fast form the fast subset for local dev.
        - CI workflows run the same or stricter commands via Make targets.
        """
        config = self._load_config()
        repos = config["repos"]

        hooks_by_id = self._build_hooks_by_id(repos)

        ruff_hook = hooks_by_id.get("ruff")
        black_hook = hooks_by_id.get("black")
        pytest_fast_hook = hooks_by_id.get("pytest-unit-fast")

        assert ruff_hook is not None, "Expected ruff hook in pre-commit fast subset"
        assert black_hook is not None, "Expected black hook in pre-commit fast subset"
        assert pytest_fast_hook is not None, "Expected pytest-unit-fast hook in pre-commit fast subset"

        ruff_args = ruff_hook.get("args", [])
        # Ruff should lint development/src and development/tests with the same
        # select/ignore configuration used by `make lint` (CI source of truth).
        assert ruff_args[:3] == [
            "check",
            "development/src",
            "development/tests",
        ], "ruff pre-commit hook should run `ruff check` on development/src and development/tests"
        joined_ruff_args = " ".join(ruff_args)
        assert (
            "--select" in ruff_args and "E,F,W" in joined_ruff_args
        ), "ruff pre-commit hook should use the same --select E,F,W configuration as `make lint`"
        assert (
            "--ignore" in ruff_args
            and "E402,E501,E712,W291,W293,F401,F841" in joined_ruff_args
        ), "ruff pre-commit hook should use the same --ignore codes as `make lint` to match CI behaviour"

        black_args = black_hook.get("args", [])
        assert black_args[:3] == [
            "--check",
            "development/src",
            "development/tests",
        ], "black pre-commit hook should run in --check mode on development/src and development/tests"

        pytest_args = pytest_fast_hook.get("args", [])
        joined_pytest_args = " ".join(pytest_args)
        assert (
            "not slow" in joined_pytest_args
        ), "pytest-unit-fast should continue to use the 'not slow' marker for fast feedback"
        assert (
            "development/tests/unit" in joined_pytest_args
        ), "pytest-unit-fast should remain scoped to development/tests/unit as the fast subset"
        assert (
            "development/tests " not in joined_pytest_args
        ), "pytest-unit-fast should not drift toward running the full development/tests tree in pre-commit"

        root = self._find_repo_root()
        ci_lite_path = root / ".github" / "workflows" / "ci-lite.yml"
        ci_main_path = root / ".github" / "workflows" / "ci.yml"

        assert ci_lite_path.exists(), "Expected .github/workflows/ci-lite.yml for fast CI checks"
        assert ci_main_path.exists(), "Expected .github/workflows/ci.yml for full CI checks"

        ci_lite = yaml.safe_load(ci_lite_path.read_text(encoding="utf-8"))
        ci_main = yaml.safe_load(ci_main_path.read_text(encoding="utf-8"))

        ci_lite_commands = self._collect_run_commands(ci_lite)
        ci_main_commands = self._collect_run_commands(ci_main)

        # CI-lite should run the same lint commands as the pre-commit fast subset.
        assert (
            "make lint" in ci_lite_commands
        ), "CI-Lite workflow should run `make lint` so ruff/black match pre-commit behaviour"

        # Full CI should run lint + unit tests (and optionally type checking) as the stricter superset.
        assert (
            "make lint" in ci_main_commands
        ), "Main CI workflow should also run `make lint` for parity with pre-commit"
        assert (
            "make unit" in ci_main_commands
        ), "Main CI workflow should run `make unit` as the stricter superset of pytest-unit-fast"
        assert (
            "make type" in ci_lite_commands or "make type" in ci_main_commands
        ), "CI workflows should include optional type checking via `make type` as a stricter gate than pre-commit"
