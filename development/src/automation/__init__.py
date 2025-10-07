"""
Automation Daemon Module

24/7 background daemon service for InnerOS knowledge processing automation.
Following Phase 3 requirements from automation-monitoring-requirements.md.

Components:
- AutomationDaemon: Main daemon lifecycle management
- SchedulerManager: APScheduler integration for job scheduling
- HealthCheckManager: Health monitoring and metrics collection
- ConfigurationLoader: YAML configuration loading and validation

Architecture follows ADR-001:
- All classes <500 LOC
- Domain separation (Scheduler/Health/Config/Lifecycle)
- No god classes
- Single responsibility per class
"""

from .daemon import AutomationDaemon, DaemonState, DaemonStatus, DaemonError
from .scheduler import SchedulerManager, JobInfo
from .health import HealthCheckManager, HealthReport
from .config import ConfigurationLoader, DaemonConfig, JobConfig

__all__ = [
    "AutomationDaemon",
    "DaemonState",
    "DaemonStatus",
    "DaemonError",
    "SchedulerManager",
    "JobInfo",
    "HealthCheckManager",
    "HealthReport",
    "ConfigurationLoader",
    "DaemonConfig",
    "JobConfig",
]
