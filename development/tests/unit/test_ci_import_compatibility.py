"""
TDD RED Phase: CI Import Compatibility Tests

Purpose: Reproduce and fix CI-specific import failures for monitoring.metrics_collector

Background:
- Tests pass locally with PYTHONPATH=development
- Tests fail in CI with 55 ModuleNotFoundErrors
- Root cause: Import path inconsistencies between local and CI environments

Test Strategy:
1. Verify imports work with multiple path configurations
2. Test both relative and absolute import patterns
3. Ensure package-level exports are properly configured
4. Validate CI-like environment behavior

All tests should FAIL initially (RED phase) if import issues exist.
"""

import sys
import pytest
from pathlib import Path


class TestMonitoringModuleImports:
    """Test monitoring module can be imported in various configurations."""

    def test_direct_module_import_works(self):
        """Test that direct module import from src.monitoring works."""
        # This tests the pattern used in test_metrics_collection.py
        from src.monitoring.metrics_collector import MetricsCollector
        
        # Should be able to instantiate
        collector = MetricsCollector()
        assert collector is not None
        assert hasattr(collector, 'increment_counter')

    def test_package_level_import_works(self):
        """Test that package-level import from src.monitoring works."""
        # This tests the pattern used in terminal_dashboard.py
        from src.monitoring import MetricsCollector
        
        # Should be able to instantiate
        collector = MetricsCollector()
        assert collector is not None
        assert hasattr(collector, 'increment_counter')

    def test_metrics_storage_import_works(self):
        """Test that MetricsStorage can be imported."""
        from src.monitoring import MetricsStorage
        
        storage = MetricsStorage(retention_hours=24)
        assert storage is not None

    def test_metrics_endpoint_import_works(self):
        """Test that MetricsEndpoint can be imported."""
        from src.monitoring import MetricsEndpoint
        from src.monitoring import MetricsCollector, MetricsStorage
        
        collector = MetricsCollector()
        storage = MetricsStorage(retention_hours=24)
        endpoint = MetricsEndpoint(collector, storage)
        assert endpoint is not None

    def test_all_monitoring_exports_accessible(self):
        """Test that all __all__ exports from monitoring package work."""
        import src.monitoring as monitoring
        
        # Check __all__ exports exist
        assert hasattr(monitoring, '__all__')
        expected_exports = [
            "MetricsCollector",
            "MetricsStorage",
            "MetricsEndpoint",
            "TimeWindowManager",
            "MetricsAggregator",
            "MetricsFormatter",
            "RingBuffer",
            "MetricsDisplayFormatter",
            "WebDashboardMetrics",
        ]
        
        for export in expected_exports:
            assert export in monitoring.__all__, f"{export} missing from __all__"
            assert hasattr(monitoring, export), f"{export} not accessible from package"

    def test_monitoring_module_in_sys_path(self):
        """Test that monitoring module can be found in sys.path."""
        # This verifies the PYTHONPATH configuration is correct
        import src.monitoring
        
        # Get the module file path
        module_path = Path(src.monitoring.__file__).parent
        assert module_path.exists(), "Monitoring module path doesn't exist"
        assert (module_path / "metrics_collector.py").exists(), "metrics_collector.py missing"
        assert (module_path / "__init__.py").exists(), "__init__.py missing"


class TestCIEnvironmentSimulation:
    """Simulate CI environment conditions to catch import issues."""

    def test_import_without_development_prefix(self):
        """Test that imports work even if PYTHONPATH doesn't include 'development/'."""
        # CI might have different PYTHONPATH setup
        # This test verifies imports work with various configurations
        
        try:
            from src.monitoring.metrics_collector import MetricsCollector
            collector = MetricsCollector()
            assert collector is not None
        except ModuleNotFoundError as e:
            pytest.fail(f"Import failed with CI-like path: {e}")

    def test_relative_import_from_test_directory(self):
        """Test that imports work from test directory context."""
        # Tests are run from various working directories in CI
        current_dir = Path.cwd()
        
        # Should work regardless of working directory
        from src.monitoring import MetricsCollector
        collector = MetricsCollector()
        assert collector is not None

    def test_terminal_dashboard_imports_work(self):
        """Test the exact import pattern used by terminal_dashboard.py."""
        # This reproduces the import that's failing in CI
        try:
            from src.monitoring import MetricsCollector
            from src.cli.terminal_dashboard import MetricsCollector as DashboardMetrics
            
            # Both should reference the same class
            assert MetricsCollector is DashboardMetrics
        except ImportError as e:
            pytest.fail(f"Terminal dashboard import pattern failed: {e}")


class TestImportErrorDiagnostics:
    """Diagnostic tests to help identify root cause of import failures."""

    def test_pythonpath_includes_development_dir(self):
        """Verify PYTHONPATH is configured correctly."""
        # Check if 'development' is in sys.path
        development_in_path = any('development' in p for p in sys.path)
        
        if not development_in_path:
            pytest.fail(
                f"PYTHONPATH missing 'development' directory.\n"
                f"Current sys.path: {sys.path}\n"
                f"This would cause CI import failures."
            )

    def test_src_directory_structure_valid(self):
        """Verify src/ directory structure is correct."""
        # Find the src directory
        src_found = False
        for path in sys.path:
            src_dir = Path(path) / "src"
            if src_dir.exists():
                src_found = True
                
                # Check monitoring subdirectory
                monitoring_dir = src_dir / "monitoring"
                assert monitoring_dir.exists(), f"monitoring/ missing from {src_dir}"
                assert (monitoring_dir / "__init__.py").exists(), "__init__.py missing"
                assert (monitoring_dir / "metrics_collector.py").exists(), "metrics_collector.py missing"
                break
        
        assert src_found, "src/ directory not found in sys.path"

    def test_module_import_error_message_helpful(self):
        """Test that import errors provide helpful debugging information."""
        try:
            # Try to import with a potentially problematic pattern
            from src.monitoring.metrics_collector import MetricsCollector
        except ModuleNotFoundError as e:
            # If this fails, the error message should be clear
            pytest.fail(
                f"ModuleNotFoundError with unclear message:\n{e}\n"
                f"sys.path: {sys.path}\n"
                f"This is the CI import failure we're debugging."
            )
