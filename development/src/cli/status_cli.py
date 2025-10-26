"""System Status CLI - TDD Implementation

Provides system observability through status command.
Detects daemon status, cron jobs, activity, and inbox state.

Phase: REFACTOR - Clean implementation using extracted utilities
Target: <150 LOC main file, utilities in status_utils.py

Architecture:
- StatusDetector: Facade for utility classes
- ActivityReader: Facade for LogTimestampReader
- InboxStatusReader: Facade for InboxAnalyzer
- StatusFormatter: Display formatting with TimeFormatter
- get_system_status(): Orchestration function
"""

import os
from typing import Dict, Tuple, Optional
from datetime import datetime

from .status_utils import (
    DaemonDetector,
    CronParser,
    LogTimestampReader,
    InboxAnalyzer,
    TimeFormatter
)


class StatusDetector:
    """Facade for daemon and cron detection utilities.
    
    REFACTOR phase: Delegates to DaemonDetector and CronParser.
    """

    def __init__(self):
        """Initialize status detector with utility instances."""
        self.daemon_detector = DaemonDetector()
        self.cron_parser = CronParser()

    def detect_daemon_status(self) -> Tuple[bool, Optional[int]]:
        """Detect if automation daemon is running.
        
        Returns:
            Tuple of (is_running, pid)
        """
        return self.daemon_detector.is_running()

    def parse_cron_status(self) -> Dict:
        """Parse crontab for automation job status.
        
        Returns:
            Dictionary with automation status and job counts
        """
        return self.cron_parser.get_status()


class ActivityReader:
    """Facade for log timestamp reading utility.
    
    REFACTOR phase: Delegates to LogTimestampReader.
    """

    def __init__(self):
        """Initialize activity reader with utility instance."""
        self.log_reader = LogTimestampReader()

    def get_last_activity(self, vault_root: str) -> Optional[datetime]:
        """Get timestamp of most recent automation activity.
        
        Args:
            vault_root: Path to vault root directory
            
        Returns:
            Datetime of last activity, None if no logs exist
        """
        return self.log_reader.get_last_activity(vault_root)


class InboxStatusReader:
    """Facade for inbox analysis utility.
    
    REFACTOR phase: Delegates to InboxAnalyzer.
    """

    def __init__(self):
        """Initialize inbox status reader with utility instance."""
        self.inbox_analyzer = InboxAnalyzer(quality_threshold=0.7)

    def get_inbox_status(self, vault_root: str) -> Dict:
        """Count inbox notes and quality scores.
        
        Args:
            vault_root: Path to vault root directory
            
        Returns:
            Dictionary with total_notes, high_quality_count, promotion_ready
        """
        return self.inbox_analyzer.get_status(vault_root)


class StatusFormatter:
    """Formats status information for terminal display.
    
    REFACTOR phase: Uses TimeFormatter utility for timestamps.
    """

    def __init__(self):
        """Initialize status formatter."""
        pass

    def format_status(self, status_data: Dict) -> str:
        """Format status dictionary into beautiful terminal output.
        
        Args:
            status_data: Complete status information
            
        Returns:
            Formatted string with emoji indicators and next steps
        """
        lines = []
        lines.append("\n📊 InnerOS System Status\n" + "=" * 50)

        # Daemon status
        daemon_info = status_data.get('daemon', {})
        daemon_running = daemon_info.get('running', False)
        daemon_pid = daemon_info.get('pid')

        if daemon_running:
            lines.append(f"🟢 Daemon: Running (PID: {daemon_pid})")
        else:
            lines.append("🔴 Daemon: Stopped")

        # Cron status
        cron_info = status_data.get('cron', {})
        cron_disabled = cron_info.get('automation_disabled', True)
        enabled_jobs = cron_info.get('enabled_jobs_count', 0)

        if cron_disabled:
            lines.append("⚠️  Cron: Disabled")
        else:
            lines.append(f"🟢 Cron: Enabled ({enabled_jobs} jobs)")

        # Activity status
        activity_info = status_data.get('activity', {})
        last_activity = activity_info.get('last_activity')

        if last_activity:
            time_ago = TimeFormatter.format_time_ago(last_activity)
            lines.append(f"📅 Last Activity: {time_ago}")
        else:
            lines.append("📅 Last Activity: No logs found")

        # Inbox status
        inbox_info = status_data.get('inbox', {})
        total_notes = inbox_info.get('total_notes', 0)
        high_quality = inbox_info.get('high_quality_count', 0)

        lines.append(f"📥 Inbox: {total_notes} notes ({high_quality} ready for promotion)")

        # Next steps
        lines.append("\n💡 Next Steps:")
        if not daemon_running:
            lines.append("   • Start daemon: inneros daemon start")
        if cron_disabled:
            lines.append("   • Enable automation: crontab -e (remove #DISABLED#)")
        if high_quality > 0:
            lines.append(f"   • Promote {high_quality} high-quality notes")

        return "\n".join(lines)


def get_system_status(vault_root: Optional[str] = None) -> Dict:
    """Orchestrate complete system status check.
    
    REFACTOR phase: Clean implementation using utility facades.
    
    Args:
        vault_root: Path to vault root (defaults to current directory)
        
    Returns:
        Complete status dictionary with all subsystem information
    """
    if vault_root is None:
        vault_root = os.getcwd()

    # Initialize detectors
    status_detector = StatusDetector()
    activity_reader = ActivityReader()
    inbox_reader = InboxStatusReader()

    # Gather all status information
    daemon_running, daemon_pid = status_detector.detect_daemon_status()
    cron_status = status_detector.parse_cron_status()
    last_activity = activity_reader.get_last_activity(vault_root)
    inbox_status = inbox_reader.get_inbox_status(vault_root)

    # Compile complete status
    return {
        'daemon': {
            'running': daemon_running,
            'pid': daemon_pid
        },
        'cron': cron_status,
        'activity': {
            'last_activity': last_activity
        },
        'inbox': inbox_status
    }
