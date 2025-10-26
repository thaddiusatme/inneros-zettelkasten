"""
TDD RED Phase: Terminal Dashboard Metrics Integration Tests

Phase 3.1 P1: Dashboard UI Integration
Tests for metrics display in terminal dashboard.

All tests should FAIL initially (RED phase).
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from src.monitoring import MetricsCollector, MetricsStorage


@pytest.fixture
def vault_dir(tmpdir):
    """Create a minimal Zettelkasten directory structure."""
    vault = Path(tmpdir)
    (vault / "Inbox").mkdir()
    (vault / "Fleeting Notes").mkdir()
    (vault / "Literature Notes").mkdir()
    (vault / "Permanent Notes").mkdir()
    (vault / "Archive").mkdir()
    return vault


class TestTerminalDashboardMetricsDisplay:
    """Test terminal dashboard has metrics support."""

    def test_dashboard_imports_metrics_collector(self):
        """Test that terminal_dashboard imports MetricsCollector."""
        import src.cli.terminal_dashboard as dashboard

        # Should have MetricsCollector imported
        assert hasattr(dashboard, 'MetricsCollector')
        assert dashboard.MetricsCollector is not None

    def test_dashboard_can_create_metrics_display_formatter(self):
        """Test that dashboard can create MetricsDisplayFormatter."""
        import src.cli.terminal_dashboard as dashboard

        collector = dashboard.MetricsCollector()
        storage = dashboard.MetricsStorage()
        display = dashboard.MetricsDisplayFormatter(collector, storage)

        # Should be able to format metrics
        summary = display.format_metrics_summary()
        assert isinstance(summary, str)
        assert "📊 System Metrics" in summary

    def test_dashboard_formatter_displays_counter_metrics(self):
        """Test that MetricsDisplayFormatter shows counters."""
        import src.cli.terminal_dashboard as dashboard

        collector = dashboard.MetricsCollector()
        collector.increment_counter("notes_processed", 5)
        collector.increment_counter("ai_api_calls", 3)

        storage = dashboard.MetricsStorage()
        display = dashboard.MetricsDisplayFormatter(collector, storage)

        summary = display.format_metrics_summary()
        assert "notes_processed" in summary
        assert "5" in summary

    def test_dashboard_formatter_displays_gauge_metrics(self):
        """Test that MetricsDisplayFormatter shows gauges."""
        import src.cli.terminal_dashboard as dashboard

        collector = dashboard.MetricsCollector()
        collector.set_gauge("active_watchers", 2)
        collector.set_gauge("daemon_status", 1)

        storage = dashboard.MetricsStorage()
        display = dashboard.MetricsDisplayFormatter(collector, storage)

        summary = display.format_metrics_summary()
        assert "active_watchers" in summary
        assert "2.00" in summary


class TestWorkflowManagerMetricsInstrumentation:
    """Test WorkflowManager collects metrics during operations."""

    def test_workflow_manager_has_metrics_coordinator(self, vault_dir):
        """Test that WorkflowManager initializes with WorkflowMetricsCoordinator."""
        from src.ai.workflow_manager import WorkflowManager
        from src.ai.workflow_metrics_coordinator import WorkflowMetricsCoordinator

        wm = WorkflowManager(base_directory=str(vault_dir))

        # Should have metrics_coordinator attribute
        assert hasattr(wm, 'metrics_coordinator')
        assert isinstance(wm.metrics_coordinator, WorkflowMetricsCoordinator)

    def test_workflow_manager_increments_notes_processed(self, vault_dir):
        """Test that processing a note increments notes_processed counter."""
        from src.ai.workflow_manager import WorkflowManager

        wm = WorkflowManager(base_directory=str(vault_dir))
        initial_metrics = wm.metrics_coordinator.get_metrics()
        initial_count = initial_metrics.get("counters", {}).get("notes_processed", 0)

        # Process a note (mocked) - mock the coordinator's process_note method
        with patch.object(wm.note_processing_coordinator, 'process_note', return_value={'success': True}):
            wm.process_inbox_note("test_note.md")

        final_metrics = wm.metrics_coordinator.get_metrics()
        final_count = final_metrics.get("counters", {}).get("notes_processed", 0)
        assert final_count == initial_count + 1

    def test_workflow_manager_records_processing_time(self, vault_dir):
        """Test that processing records time in histogram."""
        from src.ai.workflow_manager import WorkflowManager

        wm = WorkflowManager(base_directory=str(vault_dir))
        initial_metrics = wm.metrics_coordinator.get_metrics()
        initial_samples = len(initial_metrics.get("histograms", {}).get("processing_time_ms", []))

        # Process a note (mocked)
        with patch.object(wm.note_processing_coordinator, 'process_note', return_value={'success': True}):
            wm.process_inbox_note("test_note.md")

        final_metrics = wm.metrics_coordinator.get_metrics()
        final_samples = len(final_metrics.get("histograms", {}).get("processing_time_ms", []))
        assert final_samples == initial_samples + 1

        # Should record a positive time value
        times = final_metrics.get("histograms", {}).get("processing_time_ms", [])
        assert times[-1] > 0  # Last recorded time should be positive

    def test_workflow_manager_updates_daemon_status_gauge(self, vault_dir):
        """Test that WorkflowManager updates daemon_status gauge."""
        from src.ai.workflow_manager import WorkflowManager

        wm = WorkflowManager(base_directory=str(vault_dir))

        # Process_inbox_note sets daemon_status to 1
        with patch.object(wm.note_processing_coordinator, 'process_note', return_value={'success': True}):
            wm.process_inbox_note("test_note.md")

        final_metrics = wm.metrics_coordinator.get_metrics()
        status = final_metrics.get("gauges", {}).get("daemon_status", 0)
        assert status == 1


class TestMetricsIntegrationWithDashboard:
    """Test end-to-end metrics integration in dashboard."""

    def test_metrics_refresh_with_dashboard_loop(self):
        """Test that metrics update during dashboard refresh loop."""
        # This will fail - refresh loop doesn't update metrics yet

        collector = MetricsCollector()
        storage = MetricsStorage()

        # Simulate metrics collection
        collector.increment_counter("notes_processed", 1)
        storage.store(collector.get_all_metrics())

        # Dashboard should show stored metrics
        assert len(storage.get_last_24h()) == 1
        latest = storage.get_latest()
        assert latest["metrics"]["counters"]["notes_processed"] == 1

    def test_dashboard_handles_empty_metrics(self):
        """Test that dashboard gracefully handles empty metrics."""
        import src.cli.terminal_dashboard as dashboard

        collector = dashboard.MetricsCollector()

        # No metrics collected yet
        metrics = collector.get_all_metrics()

        # Should have empty structures, not fail
        assert metrics["counters"] == {}
        assert metrics["gauges"] == {}
        assert metrics["histograms"] == {}

        # Formatter should handle empty metrics gracefully
        storage = dashboard.MetricsStorage()
        display = dashboard.MetricsDisplayFormatter(collector, storage)
        summary = display.format_metrics_summary()

        # Should return valid string even with no metrics
        assert isinstance(summary, str)
        assert "📊 System Metrics" in summary
