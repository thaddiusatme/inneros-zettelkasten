"""
System Status Utilities - TDD REFACTOR Phase

Extracted utility classes for system observability.
Follows proven pattern from v2.1 auto-promotion and Smart Link Management.

Utilities:
- DaemonDetector: Process detection via PID file and ps aux
- CronParser: Crontab parsing and #DISABLED# marker detection
- LogTimestampReader: Activity timestamp extraction
- InboxAnalyzer: Quality-based note counting
- TimeFormatter: Human-readable timestamp formatting

Phase: REFACTOR - Utility extraction for modularity
ADR-001 Compliance: Main file <200 LOC, utilities well-organized
"""

import os
import subprocess
import yaml
from typing import Dict, Tuple, Optional, List
from datetime import datetime
from pathlib import Path


class DaemonDetector:
    """Detects automation daemon process status.
    
    Methods:
    - is_running(): Check if daemon is active
    - get_pid(): Get daemon process ID
    """
    
    def __init__(self, pid_file_path: Optional[Path] = None):
        """Initialize daemon detector.
        
        Args:
            pid_file_path: Custom PID file location (defaults to ~/.inneros/daemon.pid)
        """
        self.pid_file = pid_file_path or (Path.home() / ".inneros" / "daemon.pid")
    
    def is_running(self) -> Tuple[bool, Optional[int]]:
        """Check if daemon is running.
        
        Returns:
            Tuple of (is_running, pid)
        """
        # Try PID file first
        if self.pid_file.exists():
            try:
                pid = int(self.pid_file.read_text().strip())
                # Verify process exists
                os.kill(pid, 0)  # Signal 0 = existence check
                return True, pid
            except (ValueError, ProcessLookupError, OSError):
                # PID file stale
                return False, None
        
        # Fallback: search ps aux
        pid = self._search_process_list()
        if pid:
            return True, pid
        
        return False, None
    
    def _search_process_list(self) -> Optional[int]:
        """Search ps aux for daemon process.
        
        Returns:
            PID if found, None otherwise
        """
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            for line in result.stdout.splitlines():
                if "automation/daemon.py" in line or "run_daemon.py" in line:
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            return int(parts[1])
                        except ValueError:
                            continue
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        return None


class CronParser:
    """Parses crontab for automation job status.
    
    Methods:
    - get_status(): Parse crontab and return status
    - is_disabled(): Check if automation is disabled
    """
    
    def get_status(self) -> Dict:
        """Parse crontab for job status.
        
        Returns:
            Dictionary with:
            - automation_disabled: bool
            - enabled_jobs_count: int
            - disabled_jobs_count: int
            - schedule_info: List[Dict]
        """
        try:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return self._empty_status()
            
            return self._parse_crontab_content(result.stdout)
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            return {
                **self._empty_status(),
                'error': str(e)
            }
    
    def _parse_crontab_content(self, content: str) -> Dict:
        """Parse crontab content for job information.
        
        Args:
            content: Raw crontab output
            
        Returns:
            Parsed status dictionary
        """
        lines = content.splitlines()
        disabled_count = 0
        enabled_count = 0
        schedule_info = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for disabled jobs
            if '#DISABLED#' in line:
                disabled_count += 1
                clean_line = line.replace('#DISABLED#', '').strip()
                if clean_line and not clean_line.startswith('#'):
                    schedule_info.append({'schedule': clean_line, 'enabled': False})
                continue
            
            # Skip comments
            if line.startswith('#'):
                continue
            
            # Active job
            enabled_count += 1
            schedule_info.append({'schedule': line, 'enabled': True})
        
        # Automation disabled if we have disabled markers or no enabled jobs
        automation_disabled = disabled_count > 0 or enabled_count == 0
        
        return {
            'automation_disabled': automation_disabled,
            'enabled_jobs_count': enabled_count,
            'disabled_jobs_count': disabled_count,
            'schedule_info': schedule_info
        }
    
    def _empty_status(self) -> Dict:
        """Return empty/disabled status.
        
        Returns:
            Status indicating no cron jobs
        """
        return {
            'automation_disabled': True,
            'enabled_jobs_count': 0,
            'disabled_jobs_count': 0,
            'schedule_info': []
        }


class LogTimestampReader:
    """Reads activity timestamps from log files.
    
    Methods:
    - get_last_activity(): Get most recent log timestamp
    """
    
    def __init__(self, logs_subpath: str = ".automation/logs"):
        """Initialize log reader.
        
        Args:
            logs_subpath: Path to logs directory relative to vault root
        """
        self.logs_subpath = logs_subpath
    
    def get_last_activity(self, vault_root: str) -> Optional[datetime]:
        """Get timestamp of most recent activity.
        
        Args:
            vault_root: Path to vault root directory
            
        Returns:
            Datetime of last activity, None if no logs
        """
        logs_dir = Path(vault_root) / self.logs_subpath
        
        if not logs_dir.exists():
            return None
        
        log_files = list(logs_dir.glob("*.log"))
        
        if not log_files:
            return None
        
        # Get most recent by modification time
        most_recent = max(log_files, key=lambda f: f.stat().st_mtime)
        
        return datetime.fromtimestamp(most_recent.stat().st_mtime)


class InboxAnalyzer:
    """Analyzes inbox notes for quality and promotion readiness.
    
    Methods:
    - get_status(): Count notes and quality scores
    """
    
    def __init__(self, quality_threshold: float = 0.7):
        """Initialize inbox analyzer.
        
        Args:
            quality_threshold: Minimum quality score for promotion readiness
        """
        self.quality_threshold = quality_threshold
    
    def get_status(self, vault_root: str) -> Dict:
        """Count inbox notes and quality metrics.
        
        Args:
            vault_root: Path to vault root directory
            
        Returns:
            Dictionary with total_notes, high_quality_count, promotion_ready
        """
        inbox_dir = Path(vault_root) / "Inbox"
        
        if not inbox_dir.exists():
            return self._empty_status()
        
        md_files = list(inbox_dir.glob("*.md"))
        total_notes = len(md_files)
        
        if total_notes == 0:
            return self._empty_status()
        
        high_quality_count = self._count_high_quality_notes(md_files)
        promotion_ready = (high_quality_count / total_notes * 100) if total_notes > 0 else 0.0
        
        return {
            'total_notes': total_notes,
            'high_quality_count': high_quality_count,
            'promotion_ready': round(promotion_ready, 1)
        }
    
    def _count_high_quality_notes(self, files: List[Path]) -> int:
        """Count notes meeting quality threshold.
        
        Args:
            files: List of markdown file paths
            
        Returns:
            Count of high-quality notes
        """
        count = 0
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                quality_score = self._extract_quality_score(content)
                
                if quality_score and quality_score >= self.quality_threshold:
                    count += 1
                    
            except (IOError, yaml.YAMLError):
                continue
        
        return count
    
    def _extract_quality_score(self, content: str) -> Optional[float]:
        """Extract quality score from YAML frontmatter.
        
        Args:
            content: File content
            
        Returns:
            Quality score if found, None otherwise
        """
        if not content.startswith('---'):
            return None
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        
        try:
            metadata = yaml.safe_load(parts[1])
            if metadata and isinstance(metadata, dict):
                return metadata.get('quality_score')
        except yaml.YAMLError:
            pass
        
        return None
    
    def _empty_status(self) -> Dict:
        """Return empty status.
        
        Returns:
            Status for empty inbox
        """
        return {
            'total_notes': 0,
            'high_quality_count': 0,
            'promotion_ready': 0.0
        }


class TimeFormatter:
    """Formats timestamps into human-readable strings.
    
    Methods:
    - format_time_ago(): Convert datetime to "X hours ago" format
    """
    
    @staticmethod
    def format_time_ago(timestamp: datetime) -> str:
        """Format timestamp as human-readable 'time ago' string.
        
        Args:
            timestamp: Datetime to format
            
        Returns:
            Human-readable string (e.g., "2 hours ago", "just now")
        """
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
