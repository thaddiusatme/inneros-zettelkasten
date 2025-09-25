"""
TDD Iteration 5 GREEN Phase: Performance Metrics Collector
Minimal working implementation for comprehensive metrics collection

GREEN Phase: Basic metrics collection to pass tests
"""

import time
import psutil
from typing import Dict, Any


class PerformanceMetricsCollector:
    """
    GREEN Phase: Basic performance metrics collection
    Minimal implementation for metrics collection tests
    """
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.start_time = time.time()
        
    def record_metrics(self, metrics: Dict[str, Any]):
        """Record performance metrics"""
        self.metrics.update(metrics)
        
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """
        GREEN Phase: Get comprehensive metrics
        Returns all required metrics for test validation
        """
        # Ensure all required metrics are present
        default_metrics = {
            "total_processing_time": 0.0,
            "average_note_processing_time": 0.0,
            "peak_memory_usage": 0,
            "cpu_usage_average": 0.0,
            "io_operations_count": 0,
            "successful_notes": 0,
            "failed_notes": 0,
            "error_rate": 0.0
        }
        
        # Update with recorded metrics
        default_metrics.update(self.metrics)
        
        return default_metrics
    
    def start_collection(self):
        """Start metrics collection"""
        self.start_time = time.time()
        self.metrics.clear()
        
    def stop_collection(self):
        """Stop metrics collection"""
        if "total_processing_time" not in self.metrics:
            self.metrics["total_processing_time"] = time.time() - self.start_time
    
    def get_current_memory_mb(self) -> float:
        """Get current memory usage in MB"""
        return psutil.virtual_memory().used / (1024 * 1024)
    
    def get_current_cpu_percent(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent()
