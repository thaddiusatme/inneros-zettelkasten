"""
Automation Daemon - Main daemon lifecycle management

Manages daemon start/stop/restart operations with APScheduler integration.
Follows ADR-001: <500 LOC, single responsibility, domain separation.

Logging Infrastructure (TDD Iteration 2 P1.4):
- Daily log files: .automation/logs/daemon_YYYY-MM-DD.log
- Format: YYYY-MM-DD HH:MM:SS [LEVEL] module: message
- Logs: lifecycle events (INFO), errors (ERROR with stack traces)
- Production-ready debugging with full audit trail
"""

import time
import logging
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
from .feature_handlers import ScreenshotEventHandler, SmartLinkEventHandler


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
    
    Logging: Daily log files with lifecycle events and error tracking.
    
    Size: 290 LOC (ADR-001 compliant: <500 LOC)
    """
    
    def __init__(self, config: Optional[DaemonConfig] = None):
        """Initialize daemon with scheduler and health monitoring."""
        self._state = DaemonState.STOPPED
        self._scheduler: Optional[BackgroundScheduler] = None
        self._start_time: Optional[float] = None
        self._job_definitions = []  # Store job definitions for restart
        self._config = config or DaemonConfig()
        
        # Initialize logging first
        self._setup_logging()
        
        # Initialize manager components
        self.scheduler: Optional[SchedulerManager] = None
        self.health: HealthCheckManager = HealthCheckManager(self)  # Always available
        self.file_watcher: Optional[FileWatcher] = None
        self.event_handler: Optional[AutomationEventHandler] = None
        
        # Feature-specific handlers
        self.screenshot_handler: Optional[ScreenshotEventHandler] = None
        self.smart_link_handler: Optional[SmartLinkEventHandler] = None
    
    def start(self) -> None:
        """
        Start daemon with scheduler initialization.
        
        Raises:
            DaemonError: If daemon is already running
        """
        if self._state == DaemonState.RUNNING:
            raise DaemonError("Daemon is already running")
        
        self._state = DaemonState.STARTING
        self.logger.info("Starting AutomationDaemon...")
        
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
                watch_path = self._config.file_watching.watch_path
                self.logger.info(f"Starting file watcher: {watch_path}")
                self.file_watcher = FileWatcher(
                    watch_path=Path(watch_path),
                    debounce_seconds=self._config.file_watching.debounce_seconds,
                    ignore_patterns=self._config.file_watching.ignore_patterns
                )
                self.file_watcher.register_callback(self._on_file_event)
                self.file_watcher.start()
                
                # Create event handler for AI processing integration
                self.event_handler = AutomationEventHandler(
                    vault_path=str(watch_path),
                    debounce_seconds=self._config.file_watching.debounce_seconds
                )
                
                # Initialize and register feature-specific handlers
                self._setup_feature_handlers(Path(watch_path))
            
            self._start_time = time.time()
            self._state = DaemonState.RUNNING
            self.logger.info("Daemon started successfully")
            
        except Exception as e:
            self._state = DaemonState.ERROR
            self.logger.error(f"Failed to start daemon: {e}", exc_info=True)
            raise DaemonError(f"Failed to start daemon: {e}")
    
    def stop(self) -> None:
        """
        Graceful shutdown with job cleanup.
        
        Waits for current jobs to complete before shutting down.
        """
        if self._state == DaemonState.STOPPED:
            return
        
        self._state = DaemonState.STOPPING
        self.logger.info("Stopping AutomationDaemon...")
        
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
            self.logger.info("Daemon stopped successfully")
            
        except Exception as e:
            self._state = DaemonState.ERROR
            self.logger.error(f"Failed to stop daemon: {e}", exc_info=True)
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
    
    def _setup_feature_handlers(self, vault_path: Path) -> None:
        """
        Initialize and register feature-specific handlers.
        
        Args:
            vault_path: Path to vault for handler initialization
        """
        # Ensure file_watcher is initialized
        if not self.file_watcher:
            self.logger.warning("File watcher not initialized, skipping feature handlers")
            return
        
        # Initialize screenshot handler if configured
        if self._config.screenshot_handler and self._config.screenshot_handler.enabled:
            onedrive_path = self._config.screenshot_handler.onedrive_path
            if onedrive_path:
                self.logger.info(f"Initializing screenshot handler: {onedrive_path}")
                self.screenshot_handler = ScreenshotEventHandler(onedrive_path)
                self.file_watcher.register_callback(self.screenshot_handler.process)
                self.logger.info("Screenshot handler registered successfully")
        
        # Initialize smart link handler if configured
        if self._config.smart_link_handler and self._config.smart_link_handler.enabled:
            self.logger.info(f"Initializing smart link handler: {vault_path}")
            self.smart_link_handler = SmartLinkEventHandler(str(vault_path))
            self.file_watcher.register_callback(self.smart_link_handler.process)
            self.logger.info("Smart link handler registered successfully")
    
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
    
    def _setup_logging(self) -> None:
        """
        Setup logging infrastructure with daily log files.
        
        Creates .automation/logs/ directory and configures file handler
        with standard format: YYYY-MM-DD HH:MM:SS [LEVEL] module: message
        
        Following proven pattern from EventHandler logging (TDD Iteration 2 P1.3).
        """
        # Create log directory
        log_dir = Path('.automation/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create daily log file
        log_file = log_dir / f'daemon_{time.strftime("%Y-%m-%d")}.log'
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Configure file handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(handler)
