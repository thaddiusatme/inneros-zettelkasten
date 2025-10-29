"""
Pytest configuration for test suite with auto-marker tagging
"""

import sys
from pathlib import Path
import pytest

# Add src directory to Python path
development_dir = Path(__file__).parent.parent
src_dir = development_dir / "src"
sys.path.insert(0, str(development_dir))
sys.path.insert(0, str(src_dir))


def pytest_collection_modifyitems(config, items):
    """
    Auto-apply pytest markers based on test directory location.

    Marker Strategy (Week 1 + Week 2):
    - tests/unit/ → @pytest.mark.fast (fast unit tests, <1s per test)
    - tests/integration/ → @pytest.mark.integration (integration tests, <5s per test)
    - tests/smoke/ → @pytest.mark.smoke + @pytest.mark.slow (nightly, minutes)
    - tests/performance/ → @pytest.mark.performance (benchmarks)

    This enables filtering:
    - pytest -m "fast or integration"  # Fast development cycle (1.56s)
    - pytest -m "not slow"  # All fast tests (skip smoke, <30s)
    - pytest -m smoke  # Run smoke tests only (5-10 min)

    Week 1 Achievement: 300x faster integration tests via vault factories
    Week 2: Smoke tests for real vault validation (nightly, not blocking)
    """
    for item in items:
        test_path = Path(item.fspath)

        # Try to get relative path, but handle tests outside tests/ directory
        try:
            relative_path = test_path.relative_to(Path(__file__).parent)
        except ValueError:
            # Test is outside development/tests/ directory (e.g., demos/)
            # Use the full path for marker detection
            relative_path = test_path

        # Convert to string for easier checking
        path_str = str(relative_path)

        # Auto-apply markers based on directory
        if "smoke" in path_str or "smoke" in relative_path.parts:
            # Smoke tests: Real vault validation (nightly)
            item.add_marker(pytest.mark.smoke)
            item.add_marker(pytest.mark.slow)
        elif "integration" in path_str or "integration" in relative_path.parts:
            # Integration tests: Fast with vault factories
            item.add_marker(pytest.mark.integration)
        elif "unit" in path_str or "unit" in relative_path.parts:
            # Unit tests: Pure logic, mocked dependencies
            item.add_marker(pytest.mark.fast)
        elif "performance" in path_str or "performance" in relative_path.parts:
            # Performance tests: Benchmarks and profiling
            item.add_marker(pytest.mark.performance)
        else:
            # Tests in root tests/ directory or demos/ get fast marker
            item.add_marker(pytest.mark.fast)
