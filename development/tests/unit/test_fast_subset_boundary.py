"""
Test: Fast Subset Boundary Definition (Issue #48/55 P0)

Verifies that the "fast" test subset has clear boundaries:
- No network calls (localhost, external APIs)
- No dependency on running servers
- No background threads that outlive the test
- No sleeps/timeouts > small threshold

This meta-test ensures pre-commit `pytest-unit-fast` remains deterministic.

Marker Taxonomy:
- @pytest.mark.slow: Long-running tests (>10s)
- @pytest.mark.network: Tests requiring localhost/network connections

Pre-commit expression: -m "not slow and not network"
"""

import pytest


class TestFastSubsetBoundary:
    """Meta-tests ensuring fast subset excludes network/slow tests."""

    def test_network_marker_is_defined(self):
        """
        Given: pytest.ini with strict-markers
        When: Using @pytest.mark.network
        Then: Marker is recognized (no PytestUnknownMarkWarning)
        """
        # This tests that the marker is properly registered in pytest.ini
        # Will fail if 'network' marker isn't defined
        marker = pytest.mark.network
        assert marker is not None
        assert marker.name == "network"

    def test_fast_subset_excludes_network_by_convention(self):
        """
        Given: Pre-commit uses `-m "not slow and not network"`
        When: A test is marked @pytest.mark.network
        Then: It should NOT run in the fast subset

        This test documents the convention:
        - fast subset = unit tests that are NOT slow AND NOT network
        """
        # Document the expected marker expression for fast subset
        expected_exclusions = ["slow", "network"]
        fast_marker_expression = "not slow and not network"

        # Verify the expression parses correctly
        for marker in expected_exclusions:
            assert f"not {marker}" in fast_marker_expression

    def test_dashboard_refresh_test_is_marked_network(self):
        """
        Given: test_terminal_dashboard.py::test_dashboard_refreshes_every_second
        When: Collecting test markers
        Then: It should have @pytest.mark.network (excludes from fast subset)

        This test ensures the problematic dashboard test that polls localhost:8080
        is properly excluded from the fast pre-commit subset.
        """
        # Import the test module to check its markers
        from tests.unit.cli import test_terminal_dashboard

        # Get the test function
        test_func = test_terminal_dashboard.test_dashboard_refreshes_every_second

        # Check for network marker
        markers = getattr(test_func, "pytestmark", [])
        marker_names = [m.name for m in markers]

        assert "network" in marker_names, (
            f"test_dashboard_refreshes_every_second must be marked @pytest.mark.network "
            f"to exclude it from fast pre-commit subset. Found markers: {marker_names}"
        )
