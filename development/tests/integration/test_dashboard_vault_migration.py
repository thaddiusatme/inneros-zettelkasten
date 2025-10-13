"""
RED Phase Validation Tests - TDD Iteration 4
Testing Infrastructure Week 1, Day 3, TDD Iteration 4

This file contains RED phase tests that verify:
1. Pytest marker infrastructure exists
2. Dashboard integration tests use vault factories
3. Dashboard tests are fully isolated from production vault
4. Performance remains optimal after migration

Expected: ALL TESTS SHOULD FAIL initially
Goal: Drive marker infrastructure and dashboard test isolation

Performance Baseline: 1.02s (already fast, but uses production vault)
Performance Target: <2s with full isolation
Isolation Target: Zero production vault dependencies
"""

import time
from pathlib import Path
import pytest


class TestMarkerInfrastructure:
    """
    RED Phase tests verifying pytest marker system.
    
    These tests drive creation of fast_integration and slow_integration
    markers in pytest.ini.
    """
    
    def test_fast_integration_marker_defined_in_pytest_ini(self):
        """
        RED: pytest.ini must define fast_integration marker
        
        Marker enables developers to run fast tests only:
        pytest -m fast_integration  # Target: <10s
        """
        pytest_ini = Path(__file__).parent.parent.parent / "pytest.ini"
        assert pytest_ini.exists(), "pytest.ini not found"
        
        content = pytest_ini.read_text()
        
        # Check for marker definition
        has_fast_marker = "fast_integration" in content
        has_marker_description = "Integration tests <5s" in content or "fast" in content.lower()
        
        # This SHOULD FAIL in RED phase (marker not yet defined)
        assert has_fast_marker, (
            "pytest.ini missing 'fast_integration' marker. "
            "Add to [tool:pytest] markers section:\n"
            "  fast_integration: Integration tests <5s (isolated, no external APIs)"
        )
        assert has_marker_description, (
            "fast_integration marker needs descriptive documentation"
        )
    
    def test_slow_integration_marker_defined_in_pytest_ini(self):
        """
        RED: pytest.ini must define slow_integration marker
        
        Marker categorizes tests with external API dependencies:
        pytest -m slow_integration  # May take minutes
        """
        pytest_ini = Path(__file__).parent.parent.parent / "pytest.ini"
        content = pytest_ini.read_text()
        
        # Check for marker definition
        has_slow_marker = "slow_integration" in content
        has_marker_description = "external API" in content.lower() or "slow" in content.lower()
        
        # This SHOULD FAIL in RED phase (marker not yet defined)
        assert has_slow_marker, (
            "pytest.ini missing 'slow_integration' marker. "
            "Add to [tool:pytest] markers section:\n"
            "  slow_integration: Integration tests with external API dependencies"
        )
        assert has_marker_description, (
            "slow_integration marker needs descriptive documentation"
        )


class TestDashboardVaultIsolation:
    """
    RED Phase tests verifying dashboard test isolation.
    
    These tests drive migration from production vault to vault factories.
    """
    
    def test_dashboard_integration_uses_vault_factory(self):
        """
        RED: Dashboard tests must use vault factory, not production vault
        
        Verify test_dashboard_vault_integration.py imports and uses
        vault factory instead of test_dir.parent / 'knowledge'
        """
        test_file = Path(__file__).parent / "test_dashboard_vault_integration.py"
        content = test_file.read_text()
        
        # Check for vault factory import
        has_factory_import = "from tests.fixtures.vault_factory import" in content
        
        # Check for production vault path pattern
        has_production_path = "test_dir.parent / 'knowledge'" in content or \
                              'test_dir.parent / "knowledge"' in content
        
        # This SHOULD FAIL in RED phase (uses production vault)
        assert has_factory_import, (
            "test_dashboard_vault_integration.py missing vault factory import. "
            "Add: from tests.fixtures.vault_factory import create_small_vault"
        )
        assert not has_production_path, (
            f"test_dashboard_vault_integration.py still references production vault. "
            f"Replace 'test_dir.parent / 'knowledge'' with vault factory."
        )
    
    def test_dashboard_tests_use_tmp_path_fixture(self):
        """
        RED: Dashboard tests must use tmp_path for full isolation
        
        Verify actual_vault_path fixture is replaced with vault_path
        fixture that uses tmp_path.
        """
        test_file = Path(__file__).parent / "test_dashboard_vault_integration.py"
        content = test_file.read_text()
        
        # Check for tmp_path usage
        has_tmp_path = "tmp_path" in content
        has_create_vault_call = "create_small_vault(tmp_path)" in content or \
                                "create_minimal_vault(tmp_path)" in content
        
        # This SHOULD FAIL in RED phase (doesn't use tmp_path)
        assert has_tmp_path, (
            "Dashboard tests must use tmp_path for isolation. "
            "Update vault_path fixture to accept tmp_path parameter."
        )
        assert has_create_vault_call, (
            "Dashboard tests must call create_small_vault(tmp_path) "
            "for isolated test vault creation."
        )
    
    def test_dashboard_has_fast_integration_marker(self):
        """
        RED: Dashboard tests must have @pytest.mark.fast_integration
        
        Enables selective execution: pytest -m fast_integration
        """
        test_file = Path(__file__).parent / "test_dashboard_vault_integration.py"
        content = test_file.read_text()
        
        # Check for marker decorator
        has_marker = "@pytest.mark.fast_integration" in content or \
                     "@pytest.mark.integration" in content
        
        # This SHOULD FAIL in RED phase (marker not yet applied)
        assert "@pytest.mark.fast_integration" in content, (
            "test_dashboard_vault_integration.py missing @pytest.mark.fast_integration. "
            "Add decorator to test classes: @pytest.mark.fast_integration"
        )


class TestIntegrationTestCategorization:
    """
    RED Phase tests verifying all integration tests are categorized.
    """
    
    def test_all_integration_tests_have_performance_markers(self):
        """
        RED: All integration tests must be marked fast or slow
        
        Verifies that existing integration tests have appropriate markers.
        """
        integration_dir = Path(__file__).parent
        test_files = list(integration_dir.glob("test_*.py"))
        
        # Files that should be checked (exclude this validation file)
        test_files_to_check = [
            f for f in test_files 
            if f.name not in ["test_dashboard_vault_migration.py", 
                             "test_vault_factory_migration.py"]
        ]
        
        unmarked_files = []
        for test_file in test_files_to_check:
            content = test_file.read_text()
            has_fast = "@pytest.mark.fast_integration" in content
            has_slow = "@pytest.mark.slow_integration" in content
            
            if not (has_fast or has_slow):
                unmarked_files.append(test_file.name)
        
        # This SHOULD FAIL in RED phase (markers not yet applied)
        assert len(unmarked_files) == 0, (
            f"Found {len(unmarked_files)} integration test files without markers: "
            f"{', '.join(unmarked_files)}. "
            f"Apply @pytest.mark.fast_integration or @pytest.mark.slow_integration"
        )


class TestPerformanceValidation:
    """
    RED Phase tests verifying performance targets are met.
    """
    
    def test_fast_integration_suite_executes_under_10_seconds(self):
        """
        RED: Fast integration tests must complete in <10s
        
        Validates that pytest -m fast_integration meets performance target.
        """
        import subprocess
        
        # Run fast integration tests
        start = time.time()
        result = subprocess.run(
            ["pytest", "-m", "fast_integration", "-q"],
            cwd=Path(__file__).parent.parent.parent,
            env={**dict(__import__('os').environ), "PYTHONPATH": "development"},
            capture_output=True,
            text=True
        )
        elapsed = time.time() - start
        
        # This might FAIL in RED phase if marker system incomplete
        assert result.returncode == 0, (
            f"Fast integration tests failed:\n{result.stdout}\n{result.stderr}"
        )
        assert elapsed < 10.0, (
            f"Fast integration suite took {elapsed:.2f}s (target: <10s). "
            f"Need to optimize or recategorize tests."
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
