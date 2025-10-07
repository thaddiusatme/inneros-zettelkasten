"""
Automation Daemon - Main daemon lifecycle management

Manages daemon start/stop/restart operations with APScheduler integration.
Follows ADR-001: <500 LOC, single responsibility, domain separation.
"""

import time
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler

from .scheduler import SchedulerManager
from .health import HealthCheckManager
from .file_watcher import FileWatcher
from .event_handler import AutomationEventHandler
from .config import DaemonConfig


class DaemonState(Enum):
    """Daemon operational states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class DaemonStatus:
    """Daemon status information"""
    state: DaemonState
    scheduler_active: bool
    active_jobs: int
    uptime_seconds: float
    watcher_active: bool = False


class DaemonError(Exception):
    """Daemon-specific errors"""
    pass


class AutomationDaemon:
    """
    Main automation daemon orchestrator.
    
    Manages daemon lifecycle with APScheduler integration for 24/7 operation.
    Provides health monitoring and graceful shutdown capabilities.
    
    Size: ~300 LOC (ADR-001 compliant)
    """
    
    def __init__(self, config: Optional[DaemonConfig] = None):
        """Initialize daemon with scheduler and health monitoring."""
        self._state = DaemonState.STOPPED
        self._scheduler: Optional[BackgroundScheduler] = None
        self._start_time: Optional[float] = None
        self._job_definitions = []  # Store job definitions for restart
        self._config = config or DaemonConfig()
        
        # Initialize manager components
        self.scheduler: Optional[SchedulerManager] = None
        self.health: HealthCheckManager = HealthCheckManager(self)  # Always available
        self.file_watcher: Optional[FileWatcher] = None
        self.event_handler: Optional[AutomationEventHandler] = None
    
    def start(self) -> None:
        """
        Start daemon with scheduler initialization.
        
        Raises:
            DaemonError: If daemon is already running
        """
        if self._state == DaemonState.RUNNING:
            raise DaemonError("Daemon is already running")
        
        self._state = DaemonState.STARTING
        
        try:
            # Create and start BackgroundScheduler
            self._scheduler = BackgroundScheduler()
            self._scheduler.start()
            
            # Initialize scheduler manager with scheduler instance
            self.scheduler = SchedulerManager(self._scheduler, self._on_job_executed)
            # Health manager is already initialized in __init__
            
            # Restore jobs if this is a restart
            for job_def in self._job_definitions:
                self.scheduler.add_job(
                    job_def["id"],
                    job_def["func"],
                    job_def["schedule"]
                )
            
            # Start file watcher if configured and enabled
            if self._config.file_watching and self._config.file_watching.enabled:
                self.file_watcher = FileWatcher(
                    watch_path=Path(self._config.file_watching.watch_path),
                    debounce_seconds=self._config.file_watching.debounce_seconds,
                    ignore_patterns=self._config.file_watching.ignore_patterns
                )
                self.file_watcher.register_callback(self._on_file_event)
                self.file_watcher.start()
                
                # Create event handler for AI processing integration
                self.event_handler = AutomationEventHandler(
                    vault_path=str(self._config.file_watching.watch_path),
                    debounce_seconds=self._config.file_watching.debounce_seconds
                )
            
            self._start_time = time.time()
            self._state = DaemonState.RUNNING
            
        except Exception as e:
            self._state = DaemonState.ERROR
            raise DaemonError(f"Failed to start daemon: {e}")
    
    def stop(self) -> None:
        """
        Graceful shutdown with job cleanup.
        
        Waits for current jobs to complete before shutting down.
        """
        if self._state == DaemonState.STOPPED:
            return
        
        self._state = DaemonState.STOPPING
        
        try:
            # Stop file watcher BEFORE scheduler (reverse start order)
            if self.file_watcher:
                self.file_watcher.stop()
                # Keep reference for status checks, but watcher is stopped
            
            # Save job definitions for potential restart
            if self.scheduler:
                jobs = self.scheduler.list_jobs()
                self._job_definitions = [
                    {
                        "id": job.id,
                        "func": self._scheduler.get_job(job.id).func,
                        "schedule": job.schedule
                    }
                    for job in jobs
                ]
            
            # Shutdown scheduler gracefully (waits for running jobs)
            if self._scheduler:
                self._scheduler.shutdown(wait=True)
                self._scheduler = None
            
            self.scheduler = None
            # Health manager stays available for status checks even when stopped
            self._state = DaemonState.STOPPED
            
        except Exception as e:
            self._state = DaemonState.ERROR
            raise DaemonError(f"Failed to stop daemon: {e}")
    
    def restart(self) -> None:
        """
        Atomic restart without losing scheduled jobs.
        
        Captures current job definitions, performs shutdown, then startup
        with job restoration.
        """
        # Stop will save job definitions
        self.stop()
        # Start will restore job definitions
        self.start()
    
    def status(self) -> DaemonStatus:
        """
        Get current daemon status.
        
        Returns:
            DaemonStatus with state, scheduler status, job counts, and uptime
        """
        scheduler_active = (
            self._scheduler is not None and
            self._scheduler.running
        )
        
        active_jobs = 0
        if self.scheduler and scheduler_active:
            active_jobs = len(self.scheduler.list_jobs())
        
        uptime_seconds = 0.0
        if self._state == DaemonState.RUNNING and self._start_time:
            uptime_seconds = time.time() - self._start_time
        
        watcher_active = (
            self.file_watcher is not None and
            self.file_watcher.is_running()
        )
        
        return DaemonStatus(
            state=self._state,
            scheduler_active=scheduler_active,
            active_jobs=active_jobs,
            uptime_seconds=uptime_seconds,
            watcher_active=watcher_active
        )
    
    def is_healthy(self) -> bool:
        """
        Quick health check.
        
        Returns:
            True if daemon is running and healthy, False otherwise
        """
        if self.health:
            return self.health.get_health_status().is_healthy
        return False
    
    def _on_job_executed(self, job_id: str, success: bool, duration: float) -> None:
        """
        Callback for job execution tracking.
        
        Args:
            job_id: Job identifier
            success: Whether job completed successfully
            duration: Execution time in seconds
        """
        if self.health:
            self.health.record_job_execution(job_id, success, duration)
    
    def _on_file_event(self, file_path: Path, event_type: str) -> None:
        """
        Callback for file watcher events.
        
        Args:
            file_path: Path to file that changed
            event_type: Type of event ('created', 'modified', 'deleted')
        """
        # Process events through event handler if available
        if self.event_handler:
            self.event_handler.process_file_event(file_path, event_type)
