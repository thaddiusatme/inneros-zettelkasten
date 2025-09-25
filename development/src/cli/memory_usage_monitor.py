"""
TDD Iteration 5 GREEN Phase: Memory Usage Monitor
Minimal working implementation for memory tracking and validation

GREEN Phase: Simple implementation to pass failing tests
"""

import psutil
import time
from typing import Dict, Any
from contextlib import contextmanager


class MemoryUsageMonitor:
    """
    GREEN Phase: Basic memory usage monitoring
    Minimal implementation to pass memory validation tests
    """
    
    def __init__(self):
        self.peak_memory_mb = 0
        self.initial_memory_mb = 0
        self.current_memory_mb = 0
        self.monitoring_active = False
        
    def get_current_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        memory_bytes = psutil.virtual_memory().used
        memory_mb = memory_bytes / (1024 * 1024)
        self.current_memory_mb = memory_mb
        return memory_mb
    
    def get_peak_memory_usage_mb(self) -> float:
        """Get peak memory usage during monitoring"""
        return self.peak_memory_mb
    
    @contextmanager
    def track_memory_usage(self):
        """
        GREEN Phase: Context manager for memory tracking
        Minimal implementation to pass memory limit tests
        """
        self.initial_memory_mb = self.get_current_memory_usage_mb()
        self.peak_memory_mb = self.initial_memory_mb
        self.monitoring_active = True
        
        try:
            yield self
            
            # Update peak memory during monitoring
            current_memory = self.get_current_memory_usage_mb()
            if current_memory > self.peak_memory_mb:
                self.peak_memory_mb = current_memory
                
        finally:
            self.monitoring_active = False
            
    def start_monitoring(self):
        """Start continuous memory monitoring"""
        self.initial_memory_mb = self.get_current_memory_usage_mb()
        self.peak_memory_mb = self.initial_memory_mb
        self.monitoring_active = True
        
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring_active = False
        
    def update_peak_memory(self):
        """Update peak memory usage"""
        if self.monitoring_active:
            current_memory = self.get_current_memory_usage_mb()
            if current_memory > self.peak_memory_mb:
                self.peak_memory_mb = current_memory
