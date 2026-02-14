"""
RED Phase tests for GitHub Issue #92: Test suite speed improvements.

Tests verify:
1. Tiered timeout configuration (unit=10s, integration=60s, smoke=300s)
2. Ollama network guard (skip when unavailable, opt-in with -m network)
3. Default addopts exclude network tests
4. Makefile targets exist and are correct
"""

import configparser
import re
import subprocess
from pathlib import Path

import pytest

# Paths
DEVELOPMENT_DIR = Path(__file__).parent.parent.parent.parent
DEVELOPMENT_PYTEST_INI = DEVELOPMENT_DIR / "pytest.ini"
ROOT_PYTEST_INI = DEVELOPMENT_DIR.parent / "pytest.ini"
CONFTEST_PATH = DEVELOPMENT_DIR / "tests" / "conftest.py"
MAKEFILE_PATH = DEVELOPMENT_DIR / "Makefile"

VENV_PYTEST = DEVELOPMENT_DIR.parent / ".venv" / "bin" / "pytest"


class TestTieredTimeouts:
    """P0: Verify tiered timeout configuration in development/pytest.ini."""

    def test_development_pytest_ini_has_timeout_for_fast_marker(self):
        """Unit tests (@fast) should have a 10s timeout, not the global 300s."""
        content = DEVELOPMENT_PYTEST_INI.read_text()
        # Should contain a timeout override for fast-marked tests
        # pytest-timeout supports per-marker timeout via marker: @pytest.mark.timeout(10)
        # But project-wide config uses [pytest] timeout = X
        # We need evidence that fast tests get 10s, not 300s
        assert "timeout" in content.lower(), "No timeout configuration found"
        # Must NOT still be using the 300s global default as the only timeout
        # The development pytest.ini should define its own timeout
        config = configparser.ConfigParser()
        config.read(str(DEVELOPMENT_PYTEST_INI))
        timeout_val = config.get("pytest", "timeout", fallback=None)
        assert timeout_val is not None, "development/pytest.ini must define a timeout"
        assert (
            int(timeout_val) <= 60
        ), f"Default timeout should be <=60s for dev speed, got {timeout_val}s"

    def test_root_pytest_ini_timeout_not_overriding_development(self):
        """Root pytest.ini's 300s timeout must not override development/ tiered config."""
        root_config = configparser.ConfigParser()
        root_config.read(str(ROOT_PYTEST_INI))
        root_timeout = int(root_config.get("pytest", "timeout", fallback="300"))

        dev_config = configparser.ConfigParser()
        dev_config.read(str(DEVELOPMENT_PYTEST_INI))
        dev_timeout = int(dev_config.get("pytest", "timeout", fallback="0"))

        assert dev_timeout > 0, "development/pytest.ini must define its own timeout"
        assert (
            dev_timeout < root_timeout
        ), f"Dev timeout ({dev_timeout}s) should be less than root ({root_timeout}s)"


class TestOllamaNetworkGuard:
    """P0: Verify Ollama-dependent tests are guarded with @pytest.mark.network."""

    def test_summarizer_integration_has_network_marker(self):
        """test_ai_summarizer_integration.py must have @pytest.mark.network."""
        integration_dir = DEVELOPMENT_DIR / "tests" / "integration"
        summarizer_test = integration_dir / "test_ai_summarizer_integration.py"
        assert summarizer_test.exists(), "Summarizer integration test file not found"

        content = summarizer_test.read_text()
        assert (
            "pytest.mark.network" in content
        ), "test_ai_summarizer_integration.py must be marked with @pytest.mark.network"

    def test_connections_integration_has_network_marker(self):
        """test_ai_connections_integration.py must have @pytest.mark.network."""
        integration_dir = DEVELOPMENT_DIR / "tests" / "integration"
        connections_test = integration_dir / "test_ai_connections_integration.py"
        assert connections_test.exists(), "Connections integration test file not found"

        content = connections_test.read_text()
        assert (
            "pytest.mark.network" in content
        ), "test_ai_connections_integration.py must be marked with @pytest.mark.network"

    def test_conftest_has_ollama_available_fixture(self):
        """conftest.py must provide an ollama_available skip fixture."""
        content = CONFTEST_PATH.read_text()
        assert (
            "ollama_available" in content
        ), "conftest.py must define an 'ollama_available' fixture"

    def test_ollama_fixture_uses_short_timeout(self):
        """The ollama_available fixture must use a short (<=2s) connection timeout."""
        content = CONFTEST_PATH.read_text()
        # Should have a socket or requests timeout of 2s or less
        assert "ollama_available" in content, "Fixture not found"
        # Look for timeout value in the fixture implementation
        # Accept patterns like: timeout=2, timeout=1, socket.setdefaulttimeout(2)
        has_short_timeout = bool(re.search(r"timeout\s*[\(=:]\s*[12]\s*\)?", content))
        assert (
            has_short_timeout
        ), "ollama_available fixture must use a <=2s connection timeout"


class TestDefaultAddoptsExcludeNetwork:
    """P0: Default test runs must exclude network-dependent tests."""

    def test_development_addopts_excludes_network(self):
        """development/pytest.ini addopts must include 'not network' filter."""
        content = DEVELOPMENT_PYTEST_INI.read_text()
        # The addopts line should contain 'not network'
        assert (
            "not network" in content
        ), "development/pytest.ini addopts must exclude network tests by default"

    def test_collect_only_excludes_ollama_tests(self):
        """Running pytest --collect-only should not include Ollama integration tests."""
        if not VENV_PYTEST.exists():
            pytest.skip("venv pytest not found")

        result = subprocess.run(
            [
                str(VENV_PYTEST),
                "--collect-only",
                "-q",
                str(DEVELOPMENT_DIR / "tests" / "integration"),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(DEVELOPMENT_DIR),
        )
        # Ollama tests should NOT appear in default collection
        collected = result.stdout
        assert (
            "test_ai_summarizer_integration" not in collected
        ), "Ollama summarizer tests should be excluded from default collection"
        assert (
            "test_ai_connections_integration" not in collected
        ), "Ollama connections tests should be excluded from default collection"


class TestMakefileTargets:
    """P1: Makefile with developer-friendly test targets."""

    def test_makefile_exists(self):
        """development/Makefile must exist."""
        assert MAKEFILE_PATH.exists(), "development/Makefile not found"

    def test_makefile_has_test_fast_target(self):
        """Makefile must have a test-fast target."""
        content = MAKEFILE_PATH.read_text()
        assert "test-fast:" in content, "Makefile missing 'test-fast' target"

    def test_makefile_has_test_unit_target(self):
        """Makefile must have a test-unit target."""
        content = MAKEFILE_PATH.read_text()
        assert "test-unit:" in content, "Makefile missing 'test-unit' target"

    def test_makefile_has_test_integration_target(self):
        """Makefile must have a test-integration target."""
        content = MAKEFILE_PATH.read_text()
        assert (
            "test-integration:" in content
        ), "Makefile missing 'test-integration' target"

    def test_makefile_has_test_all_target(self):
        """Makefile must have a test-all target."""
        content = MAKEFILE_PATH.read_text()
        assert "test-all:" in content, "Makefile missing 'test-all' target"

    def test_makefile_test_fast_excludes_slow_and_network(self):
        """test-fast target must exclude slow and network tests."""
        content = MAKEFILE_PATH.read_text()
        # Find the test-fast recipe line
        assert "not slow" in content, "test-fast must exclude slow tests"
        assert "not network" in content, "test-fast must exclude network tests"
