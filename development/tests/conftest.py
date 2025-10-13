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
    
    Marker Strategy:
    - tests/unit/ → @pytest.mark.fast (fast unit tests)
    - tests/integration/ → @pytest.mark.integration (slower integration tests)
    - tests/ (root) → @pytest.mark.smoke (basic smoke tests)
    
    This enables filtering:
    - pytest -m fast  # Run only fast unit tests
    - pytest -m "not integration"  # Skip slow integration tests
    - pytest -m smoke  # Run smoke tests
    """
    for item in items:
        test_path = Path(item.fspath)
        relative_path = test_path.relative_to(Path(__file__).parent)
        
        # Auto-apply markers based on directory
        if "integration" in relative_path.parts:
            item.add_marker(pytest.mark.integration)
        elif "unit" in relative_path.parts:
            item.add_marker(pytest.mark.fast)
        else:
            # Tests in root tests/ directory are smoke tests
            item.add_marker(pytest.mark.smoke)
