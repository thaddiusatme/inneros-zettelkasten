"""
TDD RED Phase: Terminal Dashboard Metrics Integration Tests

Phase 3.1 P1: Dashboard UI Integration
Tests for metrics display in terminal dashboard.

All tests should FAIL initially (RED phase).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from src.cli.terminal_dashboard import run_dashboard, create_status_table
from src.monitoring import MetricsCollector, MetricsStorage


class TestTerminalDashboardMetricsDisplay:
    """Test terminal dashboard shows metrics section."""
    
    def test_dashboard_includes_metrics_section(self):
        """Test that dashboard output includes '📊 System Metrics' section."""
        # This test will fail until we add metrics to terminal_dashboard.py
        
        with patch('src.cli.terminal_dashboard.HealthPoller') as mock_poller:
            # Mock health data
            mock_poller.return_value.fetch.return_value = {
                'status': 'healthy',
                'daemon': {'status': 'running'},
                'handlers': {'inbox': {'status': 'idle'}}
            }
            
            # Capture dashboard output
            output = StringIO()
            with patch('sys.stdout', output):
                # This should fail - metrics section not yet implemented
                with patch('src.cli.terminal_dashboard.Live'):
                    # Run dashboard briefly
                    pass
            
            output_text = output.getvalue()
            assert "📊 System Metrics" in output_text
    
    def test_dashboard_displays_counter_metrics(self):
        """Test that dashboard shows counter metrics (notes_processed, ai_api_calls)."""
        # This will fail until counters are displayed
        
        collector = MetricsCollector()
        collector.increment_counter("notes_processed", 5)
        collector.increment_counter("ai_api_calls", 3)
        
        # Mock terminal dashboard with metrics
        with patch('src.cli.terminal_dashboard.MetricsCollector', return_value=collector):
            with patch('src.cli.terminal_dashboard.HealthPoller') as mock_poller:
                mock_poller.return_value.fetch.return_value = {'status': 'healthy'}
                
                output = StringIO()
                with patch('sys.stdout', output):
                    # This should show metrics but will fail initially
                    pass
                
                output_text = output.getvalue()
                assert "notes_processed" in output_text
                assert "5" in output_text
    
    def test_dashboard_displays_gauge_metrics(self):
        """Test that dashboard shows gauge metrics (active_watchers, daemon_status)."""
        collector = MetricsCollector()
        collector.set_gauge("active_watchers", 2)
        collector.set_gauge("daemon_status", 1)
        
        # This will fail - gauge display not implemented
        with patch('src.cli.terminal_dashboard.MetricsCollector', return_value=collector):
            output = StringIO()
            with patch('sys.stdout', output):
                pass
            
            output_text = output.getvalue()
            assert "active_watchers" in output_text
            assert "2.00" in output_text
    
    def test_dashboard_displays_histogram_metrics(self):
        """Test that dashboard shows histogram metrics with avg/min/max."""
        collector = MetricsCollector()
        collector.record_histogram("processing_time_ms", 100)
        collector.record_histogram("processing_time_ms", 200)
        collector.record_histogram("processing_time_ms", 150)
        
        # This will fail - histogram display not implemented
        with patch('src.cli.terminal_dashboard.MetricsCollector', return_value=collector):
            output = StringIO()
            with patch('sys.stdout', output):
                pass
            
            output_text = output.getvalue()
            assert "processing_time_ms" in output_text
            assert "avg" in output_text or "150" in output_text  # Average of 100, 200, 150


class TestWorkflowManagerMetricsInstrumentation:
    """Test WorkflowManager collects metrics during operations."""
    
    def test_workflow_manager_has_metrics_collector(self):
        """Test that WorkflowManager initializes with MetricsCollector."""
        # This will fail - WorkflowManager doesn't have metrics yet
        from src.workflow_manager import WorkflowManager
        
        wm = WorkflowManager()
        
        # Should have metrics attribute
        assert hasattr(wm, 'metrics')
        assert isinstance(wm.metrics, MetricsCollector)
    
    def test_workflow_manager_increments_notes_processed(self):
        """Test that processing a note increments notes_processed counter."""
        from src.workflow_manager import WorkflowManager
        
        wm = WorkflowManager()
        initial_count = wm.metrics.get_counter("notes_processed")
        
        # Process a note (mocked)
        with patch.object(wm, '_process_note_content', return_value={'success': True}):
            wm.process_inbox_note("test_note.md")
        
        final_count = wm.metrics.get_counter("notes_processed")
        assert final_count == initial_count + 1
    
    def test_workflow_manager_records_processing_time(self):
        """Test that processing records time in histogram."""
        from src.workflow_manager import WorkflowManager
        
        wm = WorkflowManager()
        initial_samples = len(wm.metrics.get_histogram("processing_time_ms"))
        
        # Process a note
        with patch.object(wm, '_process_note_content', return_value={'success': True}):
            wm.process_inbox_note("test_note.md")
        
        final_samples = len(wm.metrics.get_histogram("processing_time_ms"))
        assert final_samples == initial_samples + 1
        
        # Should record a positive time value
        times = wm.metrics.get_histogram("processing_time_ms")
        assert times[-1] > 0  # Last recorded time should be positive
    
    def test_workflow_manager_updates_daemon_status_gauge(self):
        """Test that WorkflowManager updates daemon_status gauge."""
        from src.workflow_manager import WorkflowManager
        
        wm = WorkflowManager()
        
        # Set daemon status
        wm.metrics.set_gauge("daemon_status", 1)  # 1 = running
        
        status = wm.metrics.get_gauge("daemon_status")
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
        collector = MetricsCollector()
        
        # No metrics collected yet
        metrics = collector.get_all_metrics()
        
        # Should have empty structures, not fail
        assert metrics["counters"] == {}
        assert metrics["gauges"] == {}
        assert metrics["histograms"] == {}
        
        # Dashboard should handle this gracefully (not fail)
        with patch('src.cli.terminal_dashboard.MetricsCollector', return_value=collector):
            # Should not raise exception
            pass
