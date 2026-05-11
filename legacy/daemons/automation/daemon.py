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
from .agent_handler import AgentEventHandler
from .config import DaemonConfig
from .pid_lock import PIDLock, PIDLockError
from .feature_handlers import (
    ScreenshotEventHandler,
    SmartLinkEventHandler,
    YouTubeFeatureHandler,
)


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

        # Initialize PID lock for process management
        self._pid_lock: Optional[PIDLock] = None

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
        self.youtube_handler: Optional[YouTubeFeatureHandler] = None
        self.agent_handler: Optional[AgentEventHandler] = None

    @property
    def state(self) -> DaemonState:
        """Get current daemon state."""
        return self._state

    def start(self) -> None:
        """
        Start daemon with scheduler initialization.

        Raises:
            DaemonError: If daemon is already running or another instance holds the lock
        """
        if self._state == DaemonState.RUNNING:
            raise DaemonError("Daemon is already running")

        self._state = DaemonState.STARTING
        self.logger.info("Starting AutomationDaemon...")

        try:
            # Acquire PID lock to prevent duplicate daemons
            self._pid_lock = PIDLock(Path(self._config.pid_file))
            try:
                self._pid_lock.acquire()
                self.logger.info(f"Acquired PID lock: {self._config.pid_file}")
            except PIDLockError as e:
                self._state = DaemonState.ERROR
                self.logger.error(f"Failed to acquire PID lock: {e}")
                raise DaemonError(f"Daemon already running: {e}")
            # Create and start BackgroundScheduler
            self._scheduler = BackgroundScheduler()
            self._scheduler.start()

            # Initialize scheduler manager with scheduler instance
            self.scheduler = SchedulerManager(self._scheduler, self._on_job_executed)
            # Health manager is already initialized in __init__

            # Restore jobs if this is a restart
            for job_def in self._job_definitions:
                self.scheduler.add_job(
                    job_def["id"], job_def["func"], job_def["schedule"]
                )

            # Start file watcher if configured and enabled
            if self._config.file_watching and self._config.file_watching.enabled:
                watch_path = self._config.file_watching.watch_path
                self.logger.info(f"Starting file watcher: {watch_path}")
                self.file_watcher = FileWatcher(
                    watch_path=Path(watch_path),
                    debounce_seconds=self._config.file_watching.debounce_seconds,
                    ignore_patterns=self._config.file_watching.ignore_patterns,
                )
                self.file_watcher.register_callback(self._on_file_event)
                self.file_watcher.start()

                # Create event handler for AI processing integration
                self.event_handler = AutomationEventHandler(
                    vault_path=str(watch_path),
                    debounce_seconds=self._config.file_watching.debounce_seconds,
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
                        "schedule": job.schedule,
                    }
                    for job in jobs
                ]

            # Shutdown scheduler gracefully (waits for running jobs)
            if self._scheduler:
                self._scheduler.shutdown(wait=True)
                self._scheduler = None

            self.scheduler = None
            # Health manager stays available for status checks even when stopped

            # Release PID lock
            if self._pid_lock:
                self._pid_lock.release()
                self.logger.info("Released PID lock")
                self._pid_lock = None

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
        scheduler_active = self._scheduler is not None and self._scheduler.running

        active_jobs = 0
        if self.scheduler and scheduler_active:
            active_jobs = len(self.scheduler.list_jobs())

        uptime_seconds = 0.0
        if self._state == DaemonState.RUNNING and self._start_time:
            uptime_seconds = time.time() - self._start_time

        watcher_active = (
            self.file_watcher is not None and self.file_watcher.is_running()
        )

        return DaemonStatus(
            state=self._state,
            scheduler_active=scheduler_active,
            active_jobs=active_jobs,
            uptime_seconds=uptime_seconds,
            watcher_active=watcher_active,
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

    def get_daemon_health(self) -> dict:
        """
        Aggregate daemon and handler health for monitoring endpoints.

        Returns:
            Dictionary including daemon checks and handler-specific health
        """
        report = self.health.get_health_status() if self.health else None
        daemon_info = {
            "is_healthy": bool(report.is_healthy) if report else False,
            "status_code": int(report.status_code) if report else 503,
            "checks": dict(report.checks) if report else {},
        }

        handlers: dict = {}
        if self.screenshot_handler is not None:
            if hasattr(self.screenshot_handler, "get_health_status"):
                handlers["screenshot"] = self.screenshot_handler.get_health_status()
            elif hasattr(self.screenshot_handler, "get_health"):
                handlers["screenshot"] = self.screenshot_handler.get_health()

        if self.smart_link_handler is not None:
            if hasattr(self.smart_link_handler, "get_health_status"):
                handlers["smart_link"] = self.smart_link_handler.get_health_status()
            elif hasattr(self.smart_link_handler, "get_health"):
                handlers["smart_link"] = self.smart_link_handler.get_health()

        if self.youtube_handler is not None:
            if hasattr(self.youtube_handler, "get_health_status"):
                handlers["youtube"] = self.youtube_handler.get_health_status()
            elif hasattr(self.youtube_handler, "get_health"):
                handlers["youtube"] = self.youtube_handler.get_health()

        if self.agent_handler is not None:
            # Simple health check for now since AgentHandler doesn't have complex metrics yet
            handlers["agent"] = {"status": "enabled", "type": "agent_handler"}

        return {"daemon": daemon_info, "handlers": handlers}

    def export_handler_metrics(self) -> dict:
        """
        Export metrics for each configured handler as structured dictionaries.

        Returns:
            Dictionary keyed by handler type with metrics content
        """
        import json

        metrics: dict = {}

        if self.screenshot_handler is not None and hasattr(
            self.screenshot_handler, "export_metrics"
        ):
            try:
                ss_json = self.screenshot_handler.export_metrics()
                metrics["screenshot"] = json.loads(ss_json)
            except Exception:
                metrics["screenshot"] = {}

        if self.smart_link_handler is not None and hasattr(
            self.smart_link_handler, "export_metrics"
        ):
            try:
                sl_json = self.smart_link_handler.export_metrics()
                metrics["smart_link"] = json.loads(sl_json)
            except Exception:
                metrics["smart_link"] = {}

        if self.youtube_handler is not None and hasattr(
            self.youtube_handler, "export_metrics"
        ):
            try:
                yt_json = self.youtube_handler.export_metrics()
                metrics["youtube"] = json.loads(yt_json)
            except Exception:
                metrics["youtube"] = {}

        return metrics

    def export_prometheus_metrics(self) -> str:
        """
        Export aggregated Prometheus metrics from all handlers.

        Returns:
            String in Prometheus exposition format with metrics from all enabled handlers
        """
        sections = []

        # Aggregate metrics from screenshot handler
        if self.screenshot_handler is not None:
            if hasattr(self.screenshot_handler, "metrics_tracker"):
                tracker = self.screenshot_handler.metrics_tracker
                if hasattr(tracker, "export_prometheus_format"):
                    prom_text = tracker.export_prometheus_format()
                    if prom_text:
                        sections.append("# Screenshot Handler Metrics")
                        sections.append(prom_text)

        # Aggregate metrics from smart link handler
        if self.smart_link_handler is not None:
            if hasattr(self.smart_link_handler, "metrics_tracker"):
                tracker = self.smart_link_handler.metrics_tracker
                if hasattr(tracker, "export_prometheus_format"):
                    prom_text = tracker.export_prometheus_format()
                    if prom_text:
                        sections.append("# Smart Link Handler Metrics")
                        sections.append(prom_text)

        # Aggregate metrics from YouTube handler
        if self.youtube_handler is not None:
            if hasattr(self.youtube_handler, "metrics_tracker"):
                tracker = self.youtube_handler.metrics_tracker
                if hasattr(tracker, "export_prometheus_format"):
                    prom_text = tracker.export_prometheus_format()
                    if prom_text:
                        sections.append("# YouTube Handler Metrics")
                        sections.append(prom_text)

        return "\n\n".join(sections) if sections else ""

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

    def _build_handler_config_dict(
        self, handler_type: str, vault_path: Optional[Path] = None
    ) -> Optional[dict]:
        """
        Build configuration dictionary for a handler from DaemonConfig.

        Args:
            handler_type: 'screenshot', 'smart_link', or 'youtube'
            vault_path: Optional vault path for smart link/youtube handlers

        Returns:
            Config dict if handler is enabled, None otherwise
        """
        if handler_type == "screenshot":
            sh_cfg = self._config.screenshot_handler
            if sh_cfg and sh_cfg.enabled and sh_cfg.onedrive_path:
                return {
                    "onedrive_path": sh_cfg.onedrive_path,
                    "knowledge_path": sh_cfg.knowledge_path,
                    "ocr_enabled": sh_cfg.ocr_enabled,
                    "processing_timeout": sh_cfg.processing_timeout,
                }

        elif handler_type == "smart_link":
            sl_cfg = self._config.smart_link_handler
            if sl_cfg and sl_cfg.enabled:
                # Resolve vault path with fallback chain
                resolved_vault = vault_path
                if resolved_vault is None:
                    if sl_cfg.vault_path:
                        resolved_vault = Path(sl_cfg.vault_path)
                    elif (
                        self._config.file_watching
                        and self._config.file_watching.watch_path
                    ):
                        resolved_vault = Path(self._config.file_watching.watch_path)
                    else:
                        resolved_vault = Path.cwd()

                return {
                    "vault_path": sl_cfg.vault_path or str(resolved_vault),
                    "similarity_threshold": sl_cfg.similarity_threshold,
                    "max_suggestions": sl_cfg.max_suggestions,
                    "auto_insert": sl_cfg.auto_insert,
                }

        elif handler_type == "youtube":
            yt_cfg = self._config.youtube_handler
            if yt_cfg and yt_cfg.enabled:
                # Resolve vault path with fallback chain
                resolved_vault = vault_path
                if resolved_vault is None:
                    if yt_cfg.vault_path:
                        resolved_vault = Path(yt_cfg.vault_path)
                    elif (
                        self._config.file_watching
                        and self._config.file_watching.watch_path
                    ):
                        resolved_vault = Path(self._config.file_watching.watch_path)
                    else:
                        resolved_vault = Path.cwd()

                return {
                    "vault_path": yt_cfg.vault_path or str(resolved_vault),
                    "max_quotes": yt_cfg.max_quotes,
                    "min_quality": yt_cfg.min_quality,
                    "processing_timeout": yt_cfg.processing_timeout,
                }

        elif handler_type == "agent":
            ah_cfg = self._config.agent_handler
            if ah_cfg and ah_cfg.enabled:
                return {
                    "enabled": ah_cfg.enabled,
                    "watch_path": ah_cfg.watch_path,
                    "processing_timeout": ah_cfg.processing_timeout,
                }

        return None

    def _setup_feature_handlers(self, vault_path: Optional[Path] = None) -> None:
        """
        Initialize and register feature-specific handlers.

        Args:
            vault_path: Path to vault for handler initialization
        """
        # Ensure file_watcher is initialized
        if not self.file_watcher:
            self.logger.warning(
                "File watcher not initialized, skipping feature handlers"
            )
            return

        # Initialize screenshot handler if configured
        sh_config = self._build_handler_config_dict("screenshot")
        if sh_config:
            self.logger.info(
                f"Initializing screenshot handler: {sh_config['onedrive_path']}"
            )
            self.screenshot_handler = ScreenshotEventHandler(config=sh_config)
            self.file_watcher.register_callback(self.screenshot_handler.process)
            self.logger.info("Screenshot handler registered successfully")

        # Initialize smart link handler if configured
        sl_config = self._build_handler_config_dict("smart_link", vault_path)
        if sl_config:
            self.logger.info(
                f"Initializing smart link handler: {sl_config['vault_path']}"
            )
            self.smart_link_handler = SmartLinkEventHandler(config=sl_config)
            self.file_watcher.register_callback(self.smart_link_handler.process)
            self.logger.info("Smart link handler registered successfully")

        # Initialize YouTube handler if configured
        yt_config = self._build_handler_config_dict("youtube", vault_path)
        if yt_config:
            self.logger.info(f"Initializing YouTube handler: {yt_config['vault_path']}")
            self.youtube_handler = YouTubeFeatureHandler(config=yt_config)
            self.file_watcher.register_callback(self.youtube_handler.process)
            self.logger.info("YouTube handler registered successfully")

        # Initialize agent handler if configured
        ah_config = self._build_handler_config_dict("agent", vault_path)
        if ah_config:
            self.logger.info(f"Initializing agent handler: {ah_config['watch_path']}")
            self.agent_handler = AgentEventHandler(config=ah_config)
            self.file_watcher.register_callback(self.agent_handler.process)
            self.logger.info("Agent handler registered successfully")

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
        log_dir = Path(".automation/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create daily log file
        log_file = log_dir / f'daemon_{time.strftime("%Y-%m-%d")}.log'

        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Configure file handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        self.logger.addHandler(handler)


def main():
    """Main entry point for daemon module execution."""
    import sys
    import signal

    # Create daemon instance
    daemon = AutomationDaemon()

    # Handle shutdown gracefully
    def handle_shutdown(signum, frame):
        print("Shutting down daemon...")
        daemon.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        # Start daemon
        daemon.start()
        print("Daemon started successfully")

        # Keep daemon running
        while daemon.state == DaemonState.RUNNING:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Daemon interrupted by user")
        daemon.stop()
    except Exception as e:
        print(f"Daemon error: {e}")
        daemon.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
