"""RED Phase: Test that Makefile uses venv-based python for lint/type commands.

This test ensures reproducible linting by verifying the Makefile:
1. Defines VENV and PYTHON variables pointing to .venv
2. Uses $(PYTHON) for lint and type targets (not system python3)
3. Has a venv bootstrap target that creates .venv

TDD Iteration 1: DevEx/Makefile venv + reproducible lint
"""

import re
from pathlib import Path

# Path to repo root Makefile
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
MAKEFILE_PATH = REPO_ROOT / "Makefile"


class TestMakefileVenvConfiguration:
    """Verify Makefile uses project-local venv for dev tools."""

    def test_makefile_exists(self):
        """Sanity check: Makefile exists at repo root."""
        assert MAKEFILE_PATH.exists(), f"Makefile not found at {MAKEFILE_PATH}"

    def test_defines_venv_variable(self):
        """Makefile should define VENV variable pointing to .venv."""
        content = MAKEFILE_PATH.read_text()
        # Match: VENV := .venv or VENV ?= .venv
        assert re.search(r"^VENV\s*[:?]?=\s*\.venv", content, re.MULTILINE), (
            "Makefile must define VENV variable (e.g., VENV := .venv)"
        )

    def test_defines_python_variable_using_venv(self):
        """Makefile should define PYTHON variable using $(VENV)/bin/python."""
        content = MAKEFILE_PATH.read_text()
        # Match: PYTHON := $(VENV)/bin/python or similar
        assert re.search(r"^PYTHON\s*[:?]?=\s*\$\(VENV\)/bin/python", content, re.MULTILINE), (
            "Makefile must define PYTHON variable using $(VENV)/bin/python"
        )

    def test_lint_target_uses_venv_python(self):
        """lint target must use $(PYTHON) not bare python3."""
        content = MAKEFILE_PATH.read_text()
        
        # Extract lint target block (from "lint:" to next target or end)
        lint_match = re.search(r"^lint:.*?(?=^[a-z]|\Z)", content, re.MULTILINE | re.DOTALL)
        assert lint_match, "lint target not found in Makefile"
        
        lint_block = lint_match.group(0)
        
        # Should NOT contain bare "python3 -m ruff" or "python3 -m black"
        assert "python3 -m ruff" not in lint_block, (
            "lint target must use $(PYTHON) not bare python3 for ruff"
        )
        assert "python3 -m black" not in lint_block, (
            "lint target must use $(PYTHON) not bare python3 for black"
        )
        
        # Should contain $(PYTHON) -m ruff and $(PYTHON) -m black
        assert "$(PYTHON) -m ruff" in lint_block or "$(PYTHON) -m black" in lint_block, (
            "lint target must use $(PYTHON) for linting tools"
        )

    def test_type_target_uses_venv_python(self):
        """type target must use $(PYTHON) not bare python3."""
        content = MAKEFILE_PATH.read_text()
        
        # Extract type target block
        type_match = re.search(r"^type:.*?(?=^[a-z]|\Z)", content, re.MULTILINE | re.DOTALL)
        assert type_match, "type target not found in Makefile"
        
        type_block = type_match.group(0)
        
        # Should NOT contain bare "python3 -m pyright"
        assert "python3 -m pyright" not in type_block, (
            "type target must use $(PYTHON) not bare python3 for pyright"
        )

    def test_venv_bootstrap_target_exists(self):
        """Makefile should have a target to bootstrap .venv."""
        content = MAKEFILE_PATH.read_text()
        # Match: $(VENV)/bin/activate: or .venv/bin/activate: or venv: target
        has_venv_target = (
            re.search(r"^\$\(VENV\)/bin/activate:", content, re.MULTILINE) or
            re.search(r"^\.venv/bin/activate:", content, re.MULTILINE) or
            re.search(r"^venv:", content, re.MULTILINE)
        )
        assert has_venv_target, (
            "Makefile must have a venv bootstrap target (e.g., $(VENV)/bin/activate:)"
        )

    def test_lint_depends_on_venv(self):
        """lint target should depend on venv being set up."""
        content = MAKEFILE_PATH.read_text()
        # Match: lint: $(VENV)/bin/activate or lint: venv
        lint_deps = re.search(r"^lint:\s*(.+)?$", content, re.MULTILINE)
        assert lint_deps, "lint target not found"
        
        deps = lint_deps.group(1) or ""
        has_venv_dep = (
            "$(VENV)/bin/activate" in deps or
            "venv" in deps or
            ".venv" in deps
        )
        assert has_venv_dep, (
            "lint target must depend on venv (e.g., lint: $(VENV)/bin/activate)"
        )


class TestDevRequirementsFile:
    """Verify dev-requirements.txt exists with pinned tools."""

    DEV_REQUIREMENTS_PATH = REPO_ROOT / "dev-requirements.txt"

    def test_dev_requirements_exists(self):
        """dev-requirements.txt should exist at repo root."""
        assert self.DEV_REQUIREMENTS_PATH.exists(), (
            "dev-requirements.txt not found - needed for reproducible dev tooling"
        )

    def test_dev_requirements_contains_ruff(self):
        """dev-requirements.txt must include ruff."""
        content = self.DEV_REQUIREMENTS_PATH.read_text()
        assert "ruff" in content.lower(), "dev-requirements.txt must include ruff"

    def test_dev_requirements_contains_black(self):
        """dev-requirements.txt must include black."""
        content = self.DEV_REQUIREMENTS_PATH.read_text()
        assert "black" in content.lower(), "dev-requirements.txt must include black"

    def test_dev_requirements_contains_pyright(self):
        """dev-requirements.txt must include pyright."""
        content = self.DEV_REQUIREMENTS_PATH.read_text()
        assert "pyright" in content.lower(), "dev-requirements.txt must include pyright"

    def test_dev_requirements_contains_pytest(self):
        """dev-requirements.txt must include pytest."""
        content = self.DEV_REQUIREMENTS_PATH.read_text()
        assert "pytest" in content.lower(), "dev-requirements.txt must include pytest"
