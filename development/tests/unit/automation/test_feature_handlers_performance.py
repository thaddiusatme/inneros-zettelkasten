"""
TDD Iteration 3 RED Phase: Feature Handler Performance Monitoring

Tests for performance tracking and alerting:
- Processing time metrics tracking
- Performance threshold validation
- Degradation detection and alerting
- Metrics export and reporting
- Health check integration
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import json

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.automation.feature_handlers import ScreenshotEventHandler, SmartLinkEventHandler


class TestProcessingTimeMetrics:
    """Test processing time tracking and metrics"""
    
    def test_screenshot_handler_tracks_processing_time(self):
        """Handler should track processing time for each event"""
        config_dict = {'onedrive_path': '/test/path'}
        handler = ScreenshotEventHandler(config=config_dict)
        
        # Mock file event
        test_file = Path('/test/Screenshot_20251007_120000.jpg')
        
        with patch.object(handler.processor_integrator, 'process_screenshot', return_value={'success': True}):
            handler.process(test_file, 'created')
        
        # Should have timing metrics
        metrics = handler.metrics_tracker.get_metrics()
        assert 'processing_times' in metrics
        assert len(metrics['processing_times']) > 0
        assert metrics['processing_times'][0] > 0  # Some time elapsed
    
    def test_smart_link_handler_tracks_processing_time(self):
        """SmartLinkHandler should track processing time for link suggestions"""
        handler = SmartLinkEventHandler()
        
        test_file = Path('/test/note.md')
        
        with patch.object(handler.link_integrator, 'process_note_for_links', return_value={'success': True, 'suggestions_count': 3}):
            handler.process(test_file, 'created')
        
        metrics = handler.metrics_tracker.get_metrics()
        assert 'processing_times' in metrics
        assert len(metrics['processing_times']) > 0
    
    def test_metrics_tracker_calculates_average_processing_time(self):
        """ProcessingMetricsTracker should calculate rolling average"""
        from src.automation.feature_handler_utils import ProcessingMetricsTracker
        
        tracker = ProcessingMetricsTracker()
        
        # Record several processing times
        tracker.record_processing_time(1.5)
        tracker.record_processing_time(2.0)
        tracker.record_processing_time(2.5)
        
        avg_time = tracker.get_average_processing_time()
        assert abs(avg_time - 2.0) < 0.1  # Average should be ~2.0
    
    def test_metrics_tracker_calculates_max_processing_time(self):
        """Should track maximum processing time"""
        from src.automation.feature_handler_utils import ProcessingMetricsTracker
        
        tracker = ProcessingMetricsTracker()
        tracker.record_processing_time(1.0)
        tracker.record_processing_time(5.0)
        tracker.record_processing_time(2.0)
        
        max_time = tracker.get_max_processing_time()
        assert max_time == 5.0
    
    def test_metrics_tracker_maintains_rolling_window(self):
        """Should maintain rolling window of last N events (e.g., 10)"""
        from src.automation.feature_handler_utils import ProcessingMetricsTracker
        
        tracker = ProcessingMetricsTracker(window_size=10)
        
        # Record 15 events
        for i in range(15):
            tracker.record_processing_time(float(i))
        
        times = tracker.get_processing_times()
        assert len(times) == 10  # Only last 10 retained
        assert times[0] == 5.0  # Oldest in window
        assert times[-1] == 14.0  # Most recent


class TestPerformanceThresholds:
    """Test performance threshold validation and alerting"""
    
    def test_screenshot_handler_warns_when_exceeding_threshold(self, caplog):
        """Should log warning when processing exceeds 10-second threshold"""
        import logging
        caplog.set_level(logging.WARNING)
        
        config_dict = {
            'onedrive_path': '/test/path',
            'processing_timeout': 5  # 5 second threshold
        }
        handler = ScreenshotEventHandler(config=config_dict)
        
        test_file = Path('/test/Screenshot_20251007_120000.jpg')
        
        # Mock slow processing
        with patch.object(handler.processor_integrator, 'process_screenshot', return_value={'success': True}):
            # Manually set processing time to exceed threshold
            with patch('time.time', side_effect=[0, 10.0]):  # Start=0, End=10 (exceeds 5s threshold)
                handler.process(test_file, 'created')
        
        # Should have logged warning
        assert any('exceeded threshold' in record.message.lower() for record in caplog.records)
    
    def test_smart_link_handler_warns_when_exceeding_threshold(self, caplog):
        """SmartLinkHandler should warn when exceeding 5-second threshold"""
        import logging
        caplog.set_level(logging.WARNING)
        
        handler = SmartLinkEventHandler()
        test_file = Path('/test/note.md')
        
        # Mock slow processing
        with patch.object(handler.link_integrator, 'process_note_for_links', return_value={'success': True, 'suggestions_count': 3}):
            # Manually set processing time to exceed 5s threshold
            with patch('time.time', side_effect=[0, 8.0]):  # Start=0, End=8 (exceeds 5s threshold)
                handler.process(test_file, 'created')
        
        assert any('exceeded threshold' in record.message.lower() for record in caplog.records)
    
    def test_performance_degraded_flag_set_on_threshold_violation(self):
        """Should set performance_degraded flag when threshold exceeded"""
        config_dict = {'onedrive_path': '/test/path', 'processing_timeout': 5}
        handler = ScreenshotEventHandler(config=config_dict)
        
        # Simulate slow processing that exceeds threshold
        with patch.object(handler.processor_integrator, 'process_screenshot', return_value={'success': True}):
            with patch('time.time', side_effect=[0, 10.0]):  # 10s exceeds 5s threshold
                test_file = Path('/test/Screenshot_20251007_120000.jpg')
                handler.process(test_file, 'created')
        
        health_status = handler.get_health_status()
        assert health_status['performance_degraded'] is True
    
    def test_slow_processing_events_counter_incremented(self):
        """Should increment slow_processing_events counter on threshold violations"""
        config_dict = {'onedrive_path': '/test/path', 'processing_timeout': 5}
        handler = ScreenshotEventHandler(config=config_dict)
        
        # Process multiple slow events
        with patch.object(handler.processor_integrator, 'process_screenshot', return_value={'success': True}):
            for i in range(3):
                # Each iteration: start=0, end=10 (exceeds 5s threshold)
                with patch('time.time', side_effect=[0, 10.0]):
                    test_file = Path(f'/test/Screenshot_{i}.jpg')
                    handler.process(test_file, 'created')
        
        metrics = handler.metrics_tracker.get_metrics()
        assert metrics['slow_processing_events'] == 3


class TestMetricsExport:
    """Test structured metrics export functionality"""
    
    def test_export_metrics_json_format(self):
        """Should export metrics in structured JSON format"""
        from src.automation.feature_handler_utils import ProcessingMetricsTracker
        
        tracker = ProcessingMetricsTracker()
        tracker.record_processing_time(2.0)
        tracker.record_processing_time(3.0)
        tracker.record_success('test.jpg', 'screenshot', ocr_success=True)
        
        metrics_json = tracker.export_metrics_json()
        metrics = json.loads(metrics_json)
        
        # Should have key metrics
        assert 'avg_processing_time' in metrics
        assert 'max_processing_time' in metrics
        assert 'total_events' in metrics
        assert 'success_rate' in metrics
    
    def test_export_includes_performance_thresholds(self):
        """Exported metrics should include threshold information"""
        config_dict = {'onedrive_path': '/test/path', 'processing_timeout': 10}
        handler = ScreenshotEventHandler(config=config_dict)
        
        # Process events
        with patch.object(handler.processor_integrator, 'process_screenshot',
                         return_value={'success': True, 'processing_time': 5.0}):
            test_file = Path('/test/Screenshot_20251007.jpg')
            handler.process(test_file, 'created')
        
        metrics_json = handler.export_metrics()
        metrics = json.loads(metrics_json)
        
        assert 'performance_threshold' in metrics
        assert metrics['performance_threshold'] == 10
        assert 'threshold_violations' in metrics
    
    def test_export_includes_handler_type_and_timestamp(self):
        """Exported metrics should include handler type and timestamp"""
        handler = SmartLinkEventHandler()
        
        metrics_json = handler.export_metrics()
        metrics = json.loads(metrics_json)
        
        assert 'handler_type' in metrics
        assert metrics['handler_type'] == 'smart_link'
        assert 'timestamp' in metrics
        assert metrics['timestamp'] is not None
    
    def test_export_metrics_prometheus_format(self):
        """Should support Prometheus-compatible metric export"""
        from src.automation.feature_handler_utils import ProcessingMetricsTracker
        
        tracker = ProcessingMetricsTracker()
        tracker.record_processing_time(2.5)
        tracker.record_success('test.jpg', 'screenshot')
        
        prometheus_output = tracker.export_prometheus_format()
        
        # Should have Prometheus metric format
        assert 'inneros_handler_processing_seconds' in prometheus_output
        assert 'inneros_handler_events_total' in prometheus_output
        assert 'inneros_handler_success_rate' in prometheus_output


class TestHealthCheckIntegration:
    """Test performance metrics integration with health checks"""
    
    def test_health_check_includes_performance_metrics(self):
        """Health check should include performance metrics"""
        config_dict = {'onedrive_path': '/test/path'}
        handler = ScreenshotEventHandler(config=config_dict)
        
        # Process some events
        with patch.object(handler.processor_integrator, 'process_screenshot',
                         return_value={'success': True, 'processing_time': 3.0}):
            test_file = Path('/test/Screenshot_20251007.jpg')
            handler.process(test_file, 'created')
        
        health = handler.get_health_status()
        
        assert 'avg_processing_time' in health
        assert 'performance_degraded' in health
        assert health['avg_processing_time'] > 0
    
    def test_health_status_healthy_when_performance_good(self):
        """Health status should be healthy when performance within thresholds"""
        config_dict = {'onedrive_path': '/test/path'}
        handler = ScreenshotEventHandler(config=config_dict)
        
        # Fast processing
        with patch.object(handler.processor_integrator, 'process_screenshot',
                         return_value={'success': True, 'processing_time': 2.0}):
            test_file = Path('/test/Screenshot_20251007.jpg')
            handler.process(test_file, 'created')
        
        health = handler.get_health_status()
        assert health['status'] == 'healthy'
        assert health['performance_degraded'] is False
    
    def test_health_status_degraded_when_performance_poor(self):
        """Health status should indicate degradation when performance poor"""
        config_dict = {'onedrive_path': '/test/path', 'processing_timeout': 5}
        handler = ScreenshotEventHandler(config=config_dict)
        
        # Multiple slow events
        with patch.object(handler.processor_integrator, 'process_screenshot', return_value={'success': True}):
            for i in range(5):
                # Each event exceeds threshold
                with patch('time.time', side_effect=[0, 10.0]):  # 10s exceeds 5s threshold
                    test_file = Path(f'/test/Screenshot_{i}.jpg')
                    handler.process(test_file, 'created')
        
        health = handler.get_health_status()
        assert health['status'] == 'degraded'
        assert health['performance_degraded'] is True


class TestPerformanceOverhead:
    """Test that performance tracking has minimal overhead"""
    
    def test_timing_overhead_less_than_1ms(self):
        """Performance tracking overhead should be <1ms per event"""
        from src.automation.feature_handler_utils import ProcessingMetricsTracker
        
        tracker = ProcessingMetricsTracker()
        
        # Measure overhead of tracking
        start = time.perf_counter()
        for _ in range(100):
            tracker.record_processing_time(1.0)
        elapsed = time.perf_counter() - start
        
        overhead_per_event = elapsed / 100
        assert overhead_per_event < 0.001  # <1ms per event
    
    def test_metrics_export_is_fast(self):
        """Metrics export should be fast (<10ms)"""
        from src.automation.feature_handler_utils import ProcessingMetricsTracker
        
        tracker = ProcessingMetricsTracker()
        
        # Record many events
        for i in range(100):
            tracker.record_processing_time(float(i) / 10)
            tracker.record_success(f'file{i}.jpg', 'screenshot')
        
        # Export should be fast
        start = time.perf_counter()
        metrics_json = tracker.export_metrics_json()
        elapsed = time.perf_counter() - start
        
        assert elapsed < 0.01  # <10ms
        assert len(metrics_json) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
