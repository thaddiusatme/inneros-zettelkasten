"""
Health Utilities - Metrics collection and execution tracking

Extracted utilities for health monitoring, following ADR-001 single responsibility.
Provides reusable execution tracking, performance calculations, and error analysis.
"""

import time
from typing import Dict, Any, List, Optional


class HealthMetricsCollector:
    """
    Utilities for health metrics collection and analysis.
    
    Provides reusable helper methods for:
    - Execution history tracking
    - Performance statistics calculations
    - Error rate analysis
    - Success rate computation
    
    Size: ~100 LOC (ADR-001 compliant)
    """

    def __init__(self):
        """Initialize metrics collector with empty state."""
        self._execution_history: List[Dict[str, Any]] = []
        self._total_executions = 0
        self._successful_executions = 0
        self._failed_executions = 0

    def record_execution(self, job_id: str, success: bool, duration: float) -> None:
        """
        Record job execution metrics.
        
        Args:
            job_id: Job identifier
            success: Whether job completed successfully
            duration: Execution time in seconds
        """
        self._total_executions += 1

        if success:
            self._successful_executions += 1
        else:
            self._failed_executions += 1

        # Store execution record
        self._execution_history.append({
            "job_id": job_id,
            "success": success,
            "duration": duration,
            "timestamp": time.time(),
        })

        # Keep only last 1000 executions to prevent unbounded growth
        if len(self._execution_history) > 1000:
            self._execution_history = self._execution_history[-1000:]

    def get_execution_statistics(self) -> Dict[str, Any]:
        """
        Calculate execution statistics.
        
        Returns:
            Dictionary with total, successful, failed counts and success rate
        """
        stats = {
            "total_executions": self._total_executions,
            "successful_executions": self._successful_executions,
            "failed_executions": self._failed_executions,
        }

        # Calculate success rate
        if self._total_executions > 0:
            stats["success_rate"] = self._successful_executions / self._total_executions
        else:
            stats["success_rate"] = 0.0

        return stats

    def get_execution_history(self, job_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent execution history.
        
        Args:
            job_id: Optional job ID to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of execution records (most recent first)
        """
        history = self._execution_history

        # Filter by job_id if specified
        if job_id:
            history = [rec for rec in history if rec["job_id"] == job_id]

        # Return most recent records
        return history[-limit:]

    def calculate_error_rate(self) -> float:
        """
        Calculate current error rate.
        
        Returns:
            Error rate as percentage (0.0 to 1.0)
        """
        if self._total_executions == 0:
            return 0.0

        return self._failed_executions / self._total_executions

    def get_average_duration(self, job_id: Optional[str] = None) -> Optional[float]:
        """
        Calculate average execution duration.
        
        Args:
            job_id: Optional job ID to filter by
            
        Returns:
            Average duration in seconds, or None if no executions
        """
        history = self._execution_history

        # Filter by job_id if specified
        if job_id:
            history = [rec for rec in history if rec["job_id"] == job_id]

        if not history:
            return None

        total_duration = sum(rec["duration"] for rec in history)
        return total_duration / len(history)

    def reset_metrics(self) -> None:
        """Reset all execution metrics and history."""
        self._execution_history.clear()
        self._total_executions = 0
        self._successful_executions = 0
        self._failed_executions = 0

    @property
    def total_executions(self) -> int:
        """Get total execution count."""
        return self._total_executions

    @property
    def successful_executions(self) -> int:
        """Get successful execution count."""
        return self._successful_executions

    @property
    def failed_executions(self) -> int:
        """Get failed execution count."""
        return self._failed_executions
