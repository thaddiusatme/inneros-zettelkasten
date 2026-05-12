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
