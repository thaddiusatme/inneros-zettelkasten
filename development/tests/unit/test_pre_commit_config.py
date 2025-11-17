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
