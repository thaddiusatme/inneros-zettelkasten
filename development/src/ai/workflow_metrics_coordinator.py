"""
Workflow Metrics Coordinator

ADR-002 Phase 13: Metrics coordination extraction for ADR-001 compliance.
Coordinates workflow-level metrics collection and reporting.

Responsibilities:
- Workflow operation metrics (notes processed, timing)
- Daemon health status tracking
- Metrics aggregation and reporting
- Integration with terminal/web dashboards

Single Responsibility: Workflow metrics collection and coordination
"""

from src.monitoring import MetricsCollector, MetricsStorage
from typing import Dict, Any


class WorkflowMetricsCoordinator:
    """
    Coordinates metrics collection for WorkflowManager operations.
    
    ADR-002 Pattern: Extracted from WorkflowManager to maintain <500 LOC limit.
    Follows coordinator pattern established in Phases 1-12.
    """
    
    def __init__(self):
        """Initialize metrics coordinator with collector and storage."""
        self.collector = MetricsCollector()
        self.storage = MetricsStorage()
    
    def record_note_processing(self, elapsed_ms: float, success: bool = True):
        """
        Record metrics for a note processing operation.
        
        Args:
            elapsed_ms: Processing time in milliseconds
            success: Whether processing succeeded
        """
        if success:
            self.collector.increment_counter("notes_processed")
        else:
            self.collector.increment_counter("notes_failed")
        
        self.collector.record_histogram("processing_time_ms", elapsed_ms)
        self.collector.set_gauge("daemon_status", 1)  # 1 = running
    
    def record_batch_operation(self, operation_name: str, count: int, elapsed_ms: float):
        """
        Record metrics for batch operations.
        
        Args:
            operation_name: Name of the operation (e.g., "weekly_review")
            count: Number of items processed
            elapsed_ms: Total batch processing time
        """
        self.collector.increment_counter(f"batch_{operation_name}_count", count)
        self.collector.record_histogram(f"batch_{operation_name}_time_ms", elapsed_ms)
    
    def record_ai_api_call(self, api_name: str, elapsed_ms: float):
        """
        Record AI API call metrics.
        
        Args:
            api_name: Name of the API (e.g., "ollama", "openai")
            elapsed_ms: API call duration
        """
        self.collector.increment_counter("ai_api_calls")
        self.collector.increment_counter(f"ai_api_{api_name}_calls")
        self.collector.record_histogram(f"ai_api_{api_name}_time_ms", elapsed_ms)
    
    def set_daemon_status(self, status: int):
        """
        Update daemon health status.
        
        Args:
            status: 0 = stopped, 1 = running, 2 = error
        """
        self.collector.set_gauge("daemon_status", status)
    
    def set_active_watchers(self, count: int):
        """
        Update active file watcher count.
        
        Args:
            count: Number of active file watchers
        """
        self.collector.set_gauge("active_watchers", count)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics snapshot.
        
        Returns:
            Dictionary with counters, gauges, and histograms
        """
        return self.collector.get_all_metrics()
    
    def store_snapshot(self):
        """Store current metrics snapshot to storage."""
        self.storage.store(self.collector.get_all_metrics())
    
    def get_metrics_history(self) -> list:
        """
        Get metrics history for last 24 hours.
        
        Returns:
            List of metric snapshots with timestamps
        """
        return self.storage.get_last_24h()
    
    def export_metrics_json(self) -> str:
        """
        Export metrics as JSON string.
        
        Returns:
            JSON string with current metrics and history
        """
        return self.storage.export_json()
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        self.collector = MetricsCollector()
