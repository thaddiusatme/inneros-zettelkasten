#!/usr/bin/env python3
"""
YouTube Production Monitoring - REFACTOR phase with logging and helpers

Provides:
- MonitoringCounters: Track success/failure/skipped metrics
- backup_status_store: Create timestamped backups before apply
- get_health_status: Simple health check for service mode
- Rotating file logging for production operations
- Helper functions for timestamp formatting and file paths
"""

import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any

# Configure logger with rotating file handler
logger = logging.getLogger(__name__)


def setup_rotating_log(log_dir: Path, max_bytes: int = 10485760, backup_count: int = 5):
    """
    Configure rotating file handler for production logging

    Args:
        log_dir: Directory for log files
        max_bytes: Maximum log file size before rotation (default 10MB)
        backup_count: Number of backup files to keep (default 5)
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "youtube_automation.log"

    handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _format_timestamp() -> str:
    """Helper: Generate timestamp string in YYYYMMDDHHMMSS format"""
    return datetime.now().strftime("%Y%m%d%H%M%S")


def _get_metrics_path(vault_path: Path) -> Path:
    """Helper: Get standard metrics file path"""
    return vault_path / ".automation" / "metrics" / "youtube_metrics.json"


def _get_backup_dir(vault_path: Path) -> Path:
    """Helper: Get standard backup directory path"""
    return vault_path / "backups" / "youtube"


class MonitoringCounters:
    """
    Track processing metrics for production monitoring

    Minimal implementation to pass tests:
    - Initialize zeroed counters
    - Increment methods
    - Persist to JSON
    """

    def __init__(self):
        """Initialize all counters to zero"""
        self.total_processed = 0
        self.successful = 0
        self.failed = 0
        self.skipped = 0

    def increment_success(self):
        """Increment success counter"""
        self.successful += 1
        self.total_processed += 1

    def increment_failure(self):
        """Increment failure counter"""
        self.failed += 1
        self.total_processed += 1

    def increment_skipped(self):
        """Increment skipped counter"""
        self.skipped += 1
        self.total_processed += 1

    def write_metrics(self, metrics_file: Path):
        """
        Persist metrics to JSON file

        Args:
            metrics_file: Path to write metrics JSON
        """
        metrics_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "total_processed": self.total_processed,
            "successful": self.successful,
            "failed": self.failed,
            "skipped": self.skipped,
            "timestamp": datetime.now().isoformat(),
        }

        with open(metrics_file, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(
            f"Metrics written: {self.total_processed} total, "
            f"{self.successful} success, {self.failed} failed"
        )


def backup_status_store(status_file: Path, backup_dir: Path) -> Optional[Path]:
    """
    Create timestamped backup of status store

    Args:
        status_file: Path to status JSON file
        backup_dir: Directory to store backups

    Returns:
        Path to backup file, or None if source doesn't exist
    """
    if not status_file.exists():
        logger.debug(f"Status file does not exist, skipping backup: {status_file}")
        return None

    # Create backup directory if needed
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamped filename using helper
    timestamp = _format_timestamp()
    backup_path = backup_dir / f"status_{timestamp}.json"

    # Copy file
    shutil.copy2(status_file, backup_path)
    logger.info(f"Status backup created: {backup_path.name}")

    return backup_path


def get_health_status(metrics_file: Path) -> Dict[str, Any]:
    """
    Get health status for service monitoring

    Args:
        metrics_file: Path to metrics JSON file

    Returns:
        Health status dict with 'status' and optional 'last_run'
    """
    if not metrics_file.exists():
        logger.debug(f"Metrics file not found: {metrics_file}")
        return {"status": "unknown"}

    try:
        with open(metrics_file) as f:
            last_run = json.load(f)

        logger.debug(
            f"Health check: {last_run['total_processed']} processed, "
            f"{last_run['successful']} successful"
        )
        return {"status": "ok", "last_run": last_run}
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to read metrics file: {e}")
        return {"status": "unknown"}
