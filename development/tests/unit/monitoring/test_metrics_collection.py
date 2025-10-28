"""
TDD RED Phase: Comprehensive test suite for metrics collection system.

Tests cover:
- MetricsCollector: counter, gauge, histogram operations
- MetricsStorage: time-windowed storage and aggregation
- MetricsEndpoint: HTTP JSON endpoint

All tests should FAIL initially (RED phase).
"""

import json
from datetime import datetime

from src.monitoring.metrics_collector import MetricsCollector
from src.monitoring.metrics_storage import MetricsStorage
from src.monitoring.metrics_endpoint import MetricsEndpoint


class TestMetricsCollector:
    """Test MetricsCollector counter/gauge/histogram operations."""

    def test_increment_counter_creates_new_counter(self):
        """Test that incrementing a counter creates it if it doesn't exist."""
        collector = MetricsCollector()
        collector.increment_counter("notes_processed")

        assert collector.get_counter("notes_processed") == 1

    def test_increment_counter_accumulates_values(self):
        """Test that multiple increments accumulate correctly."""
        collector = MetricsCollector()
        collector.increment_counter("ai_api_calls", 1)
        collector.increment_counter("ai_api_calls", 3)
        collector.increment_counter("ai_api_calls", 2)

        assert collector.get_counter("ai_api_calls") == 6

    def test_set_gauge_updates_current_value(self):
        """Test that setting a gauge updates to current value."""
        collector = MetricsCollector()
        collector.set_gauge("active_watchers", 5)
        assert collector.get_gauge("active_watchers") == 5

        collector.set_gauge("active_watchers", 3)
        assert collector.get_gauge("active_watchers") == 3

    def test_record_histogram_stores_distribution(self):
        """Test that histogram records value distribution."""
        collector = MetricsCollector()
        collector.record_histogram("processing_time_ms", 100)
        collector.record_histogram("processing_time_ms", 250)
        collector.record_histogram("processing_time_ms", 150)

        histogram = collector.get_histogram("processing_time_ms")
        assert len(histogram) == 3
        assert 100 in histogram
        assert 250 in histogram
        assert 150 in histogram

    def test_get_all_metrics_returns_complete_snapshot(self):
        """Test that get_all_metrics returns all metric types."""
        collector = MetricsCollector()
        collector.increment_counter("notes_processed", 10)
        collector.set_gauge("daemon_status", 1)
        collector.record_histogram("processing_time_ms", 200)

        metrics = collector.get_all_metrics()

        assert "counters" in metrics
        assert "gauges" in metrics
        assert "histograms" in metrics
        assert metrics["counters"]["notes_processed"] == 10
        assert metrics["gauges"]["daemon_status"] == 1
        assert 200 in metrics["histograms"]["processing_time_ms"]


class TestMetricsStorage:
    """Test MetricsStorage time-windowed storage and aggregation."""

    def test_store_adds_metrics_with_timestamp(self):
        """Test that store adds metrics with current timestamp."""
        storage = MetricsStorage(retention_hours=24)

        metrics = {
            "counters": {"notes_processed": 10},
            "gauges": {"daemon_status": 1},
            "histograms": {"processing_time_ms": [100, 200]},
        }

        storage.store(metrics)

        stored = storage.get_latest()
        assert stored is not None
        assert stored["metrics"] == metrics
        assert "timestamp" in stored

    def test_aggregate_hourly_groups_by_hour(self):
        """Test that hourly aggregation groups metrics correctly."""
        storage = MetricsStorage(retention_hours=24)

        # Store metrics at different times (without mocking for simplicity)
        storage.store({"counters": {"notes_processed": 10}})
        storage.store({"counters": {"notes_processed": 15}})

        hourly = storage.aggregate_hourly()
        assert len(hourly) >= 1
        assert "hour" in hourly[0]
        assert "metrics" in hourly[0]

    def test_get_last_24h_filters_by_time_window(self):
        """Test that get_last_24h only returns recent metrics."""
        # Use short retention window for testing
        storage = MetricsStorage(retention_hours=0)  # 0 hours = immediate pruning

        # Store metric and immediately check it's pruned
        storage.store({"counters": {"old_metric": 1}})

        # With 0 hour retention, get_last_24h should prune everything
        recent = storage.get_last_24h()
        assert len(recent) == 0  # All pruned due to 0 retention

    def test_export_json_returns_valid_json_string(self):
        """Test that export_json produces valid JSON."""
        storage = MetricsStorage(retention_hours=24)
        storage.store({"counters": {"notes_processed": 10}})

        json_str = storage.export_json()

        # Should be valid JSON
        data = json.loads(json_str)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["metrics"]["counters"]["notes_processed"] == 10


class TestMetricsEndpoint:
    """Test MetricsEndpoint HTTP handler."""

    def test_get_metrics_returns_json_response(self):
        """Test that /metrics endpoint returns JSON."""
        collector = MetricsCollector()
        storage = MetricsStorage(retention_hours=24)
        endpoint = MetricsEndpoint(collector, storage)

        collector.increment_counter("notes_processed", 5)
        storage.store(collector.get_all_metrics())

        response = endpoint.get_metrics()

        assert response["status"] == "success"
        assert "current" in response
        assert "history" in response
        assert response["current"]["counters"]["notes_processed"] == 5

    def test_get_metrics_includes_timestamp(self):
        """Test that metrics response includes timestamp."""
        collector = MetricsCollector()
        storage = MetricsStorage(retention_hours=24)
        endpoint = MetricsEndpoint(collector, storage)

        response = endpoint.get_metrics()

        assert "timestamp" in response
        # Timestamp should be ISO format string
        datetime.fromisoformat(response["timestamp"])
