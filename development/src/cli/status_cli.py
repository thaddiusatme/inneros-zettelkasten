"""
System Status CLI - TDD Implementation

Provides system observability through status command.
Detects daemon status, cron jobs, activity, and inbox state.

Phase: GREEN - Minimal implementation for passing tests
Target: 8/8 tests passing

Architecture:
- StatusDetector: Daemon and cron detection
- ActivityReader: Log timestamp extraction
- InboxStatusReader: Note counting and quality assessment
- StatusFormatter: Display formatting
- get_system_status(): Orchestration function
"""

import os
import subprocess
import yaml
from typing import Dict, Tuple, Optional
from datetime import datetime
from pathlib import Path


class StatusDetector:
    """Detects daemon and cron job status.
    
    RED phase: Empty implementation - tests will fail.
    """
    
    def __init__(self):
        """Initialize status detector."""
        pass
    
    def detect_daemon_status(self) -> Tuple[bool, Optional[int]]:
        """Detect if automation daemon is running.
        
        Returns:
            Tuple of (is_running, pid)
            - is_running: True if daemon process active
            - pid: Process ID if running, None otherwise
        """
        # Check for PID file first
        pid_file = Path.home() / ".inneros" / "daemon.pid"
        
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                # Check if process is actually running
                os.kill(pid, 0)  # Signal 0 just checks existence
                return True, pid
            except (ValueError, ProcessLookupError, OSError):
                # PID file exists but process is dead
                return False, None
        
        # Fallback: Check ps aux for daemon process
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=2
            )
            for line in result.stdout.splitlines():
                if "automation/daemon.py" in line or "run_daemon.py" in line:
                    # Extract PID (second column)
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            pid = int(parts[1])
                            return True, pid
                        except ValueError:
                            pass
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        return False, None
    
    def parse_cron_status(self) -> Dict:
        """Parse crontab for automation job status.
        
        Returns:
            Dictionary with:
            - automation_disabled: True if #DISABLED# markers found
            - enabled_jobs_count: Number of active cron jobs
            - schedule_info: Cron schedule details
        """
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                # No crontab installed
                return {
                    'automation_disabled': True,
                    'enabled_jobs_count': 0,
                    'schedule_info': []
                }
            
            crontab_content = result.stdout
            lines = crontab_content.splitlines()
            
            disabled_count = 0
            enabled_count = 0
            schedule_info = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    # Check if it's a disabled job
                    if '#DISABLED#' in line:
                        disabled_count += 1
                        # Extract schedule info from disabled job
                        clean_line = line.replace('#DISABLED#', '').strip()
                        if clean_line and not clean_line.startswith('#'):
                            schedule_info.append({'schedule': clean_line, 'enabled': False})
                    continue
                
                # Active job
                enabled_count += 1
                schedule_info.append({'schedule': line, 'enabled': True})
            
            # Automation is disabled if we have disabled markers or no enabled jobs
            automation_disabled = disabled_count > 0 or enabled_count == 0
            
            return {
                'automation_disabled': automation_disabled,
                'enabled_jobs_count': enabled_count,
                'disabled_jobs_count': disabled_count,
                'schedule_info': schedule_info
            }
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            # Error running crontab
            return {
                'automation_disabled': True,
                'enabled_jobs_count': 0,
                'error': str(e)
            }


class ActivityReader:
    """Reads activity timestamps from logs.
    
    RED phase: Empty implementation - tests will fail.
    """
    
    def __init__(self):
        """Initialize activity reader."""
        pass
    
    def get_last_activity(self, vault_root: str) -> Optional[datetime]:
        """Get timestamp of most recent automation activity.
        
        Args:
            vault_root: Path to vault root directory
            
        Returns:
            Datetime of last activity, None if no logs exist
        """
        logs_dir = Path(vault_root) / ".automation" / "logs"
        
        if not logs_dir.exists():
            return None
        
        # Find all log files
        log_files = list(logs_dir.glob("*.log"))
        
        if not log_files:
            return None
        
        # Get most recent based on modification time
        most_recent_file = max(log_files, key=lambda f: f.stat().st_mtime)
        
        # Return modification time as datetime
        return datetime.fromtimestamp(most_recent_file.stat().st_mtime)


class InboxStatusReader:
    """Reads inbox status and quality metrics.
    
    RED phase: Empty implementation - tests will fail.
    """
    
    def __init__(self):
        """Initialize inbox status reader."""
        pass
    
    def get_inbox_status(self, vault_root: str) -> Dict:
        """Count inbox notes and quality scores.
        
        Args:
            vault_root: Path to vault root directory
            
        Returns:
            Dictionary with:
            - total_notes: Total count in Inbox/
            - high_quality_count: Notes with quality_score >= 0.7
            - promotion_ready: Percentage ready for promotion
        """
        inbox_dir = Path(vault_root) / "Inbox"
        
        if not inbox_dir.exists():
            return {
                'total_notes': 0,
                'high_quality_count': 0,
                'promotion_ready': 0.0
            }
        
        # Count markdown files
        md_files = list(inbox_dir.glob("*.md"))
        total_notes = len(md_files)
        
        if total_notes == 0:
            return {
                'total_notes': 0,
                'high_quality_count': 0,
                'promotion_ready': 0.0
            }
        
        # Count high quality notes (quality_score >= 0.7)
        high_quality_count = 0
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # Extract YAML frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        metadata = yaml.safe_load(frontmatter)
                        
                        if metadata and isinstance(metadata, dict):
                            quality_score = metadata.get('quality_score', 0)
                            if quality_score >= 0.7:
                                high_quality_count += 1
            except (IOError, yaml.YAMLError):
                # Skip files we can't read
                continue
        
        promotion_ready = (high_quality_count / total_notes * 100) if total_notes > 0 else 0.0
        
        return {
            'total_notes': total_notes,
            'high_quality_count': high_quality_count,
            'promotion_ready': round(promotion_ready, 1)
        }


class StatusFormatter:
    """Formats status information for terminal display.
    
    RED phase: Empty implementation - tests will fail.
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
            time_ago = self._format_time_ago(last_activity)
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
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as human-readable 'time ago' string."""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"


def get_system_status(vault_root: Optional[str] = None) -> Dict:
    """Orchestrate complete system status check.
    
    GREEN phase: Minimal implementation to pass tests.
    
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
