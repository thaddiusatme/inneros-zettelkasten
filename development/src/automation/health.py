"""
Health Check Manager - Health monitoring and metrics collection

Tracks daemon health status, job execution metrics, and performance statistics.
Follows ADR-001: <500 LOC, single responsibility, domain separation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, TYPE_CHECKING

from .health_utils import HealthMetricsCollector

if TYPE_CHECKING:
    from .daemon import AutomationDaemon, DaemonState


@dataclass
class HealthReport:
    """Health check report"""
    is_healthy: bool
    status_code: int
    checks: Dict[str, bool] = field(default_factory=dict)


class HealthCheckManager:
    """
    Health monitoring and metrics collection.
    
    Tracks daemon health, job execution statistics, and performance metrics.
    Provides HTTP-style status codes for monitoring integration.
    
    Size: ~200 LOC (ADR-001 compliant)
    """
    
    def __init__(self, daemon: 'AutomationDaemon'):
        """
        Initialize health check manager.
        
        Args:
            daemon: Parent AutomationDaemon instance
        """
        self._daemon = daemon
        self._metrics_collector = HealthMetricsCollector()
    
    def get_health_status(self) -> HealthReport:
        """
        Comprehensive health check.
        
        Returns:
            HealthReport with health status and component checks
        """
        from .daemon import DaemonState
        
        # Check daemon state
        daemon_running = self._daemon._state == DaemonState.RUNNING
        
        # Check scheduler
        scheduler_healthy = (
            self._daemon._scheduler is not None and
            self._daemon._scheduler.running
        )
        
        # Check file watcher (if configured)
        watcher_healthy = True
        if self._daemon.file_watcher:
            watcher_healthy = self._daemon.file_watcher.is_running()
        
        # Overall health
        is_healthy = daemon_running and scheduler_healthy
        status_code = 200 if is_healthy else 503
        
        checks = {
            "scheduler": scheduler_healthy,
            "daemon": daemon_running,
            "file_watcher": watcher_healthy,
        }
        
        return HealthReport(
            is_healthy=is_healthy,
            status_code=status_code,
            checks=checks
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Performance and operational metrics.
        
        Returns:
            Dictionary with uptime, job counts, and execution statistics
        """
        status = self._daemon.status()
        
        # Get execution statistics from metrics collector
        exec_stats = self._metrics_collector.get_execution_statistics()
        
        metrics = {
            "uptime_seconds": status.uptime_seconds,
            "total_jobs": status.active_jobs,
            "active_jobs": status.active_jobs,
            "total_job_executions": exec_stats["total_executions"],
            "successful_executions": exec_stats["successful_executions"],
            "failed_executions": exec_stats["failed_executions"],
            "success_rate": exec_stats["success_rate"],
        }
        
        return metrics
    
    def record_job_execution(self, job_id: str, success: bool, duration: float) -> None:
        """
        Track job execution history.
        
        Args:
            job_id: Job identifier
            success: Whether job completed successfully
            duration: Execution time in seconds
        """
        # Delegate to metrics collector
        self._metrics_collector.record_execution(job_id, success, duration)
    
    def get_execution_history(self, job_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent execution history.
        
        Args:
            job_id: Optional job ID to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of execution records
        """
        # Delegate to metrics collector
        return self._metrics_collector.get_execution_history(job_id, limit)
    
    def reset_metrics(self) -> None:
        """Reset all execution metrics and history."""
        # Delegate to metrics collector
        self._metrics_collector.reset_metrics()
