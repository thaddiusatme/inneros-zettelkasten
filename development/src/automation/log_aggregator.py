"""Log Aggregator for handler activity detection.

Issue #67: Aggregates handler logs for true last-activity reporting in inneros-status.

Design goals:
- Scan multiple handler log files (youtube_handler_*, screenshot_handler_*, etc.)
- Use bounded reading (tail last N lines) to avoid reading multi-MB logs fully
- Find the most recent timestamp and status across all logs
- Return per-handler activity with source log file attribution
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Handler log file patterns
HANDLER_LOG_PATTERN = re.compile(r"^(\w+_handler)_(\d{4}-\d{2}-\d{2})\.log$")

# Log line timestamp pattern: 2025-12-19 14:30:01
TIMESTAMP_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")

# Default tail lines for bounded reading
DEFAULT_TAIL_LINES = 100


class LogAggregator:
    """Aggregates handler logs for activity detection."""

    def __init__(self, logs_dir: Path, tail_lines: int = DEFAULT_TAIL_LINES):
        """Initialize LogAggregator.

        Args:
            logs_dir: Path to the logs directory (.automation/logs)
            tail_lines: Number of lines to read from end of each log file
        """
        self.logs_dir = Path(logs_dir)
        self.tail_lines = tail_lines

    def get_handler_activity(self, handler_name: str) -> Dict[str, Any]:
        """Get the most recent activity for a specific handler.

        Args:
            handler_name: Handler name (e.g., 'youtube_handler')

        Returns:
            Dictionary with last_timestamp, status, source_log, and optional error_snippet
        """
        if not self.logs_dir.exists():
            return {
                "status": "no_data",
                "last_timestamp": None,
                "source_log": None,
                "message": "No log files found - logs directory does not exist",
            }

        # Find all log files for this handler
        log_files = self._find_handler_logs(handler_name)

        if not log_files:
            return {
                "status": "no_data",
                "last_timestamp": None,
                "source_log": None,
                "message": f"No log files found for {handler_name}",
            }

        # Process logs newest first (by filename date)
        log_files.sort(reverse=True)

        best_result: Optional[Dict[str, Any]] = None

        for log_file in log_files:
            result = self._parse_log_file(log_file)
            if result and result.get("last_timestamp"):
                if best_result is None or self._is_newer(
                    result["last_timestamp"], best_result["last_timestamp"]
                ):
                    best_result = result
                    best_result["source_log"] = str(log_file.name)

        if best_result:
            return best_result

        return {
            "status": "no_data",
            "last_timestamp": None,
            "source_log": None,
            "message": f"No valid log entries found for {handler_name}",
        }

    def get_all_handler_activity(self) -> Dict[str, Dict[str, Any]]:
        """Get activity for all handlers found in logs directory.

        Returns:
            Dictionary mapping handler names to their activity status
        """
        if not self.logs_dir.exists():
            return {}

        handlers = self._discover_handlers()
        result: Dict[str, Dict[str, Any]] = {}

        for handler_name in handlers:
            result[handler_name] = self.get_handler_activity(handler_name)

        return result

    def get_overall_last_activity(self) -> Dict[str, Any]:
        """Get the single most recent activity across all handlers.

        Returns:
            Dictionary with handler, last_timestamp, status, source_log
        """
        all_activity = self.get_all_handler_activity()

        if not all_activity:
            return {
                "handler": None,
                "last_timestamp": None,
                "status": "no_data",
                "source_log": None,
            }

        most_recent_handler = None
        most_recent_timestamp = None

        for handler_name, activity in all_activity.items():
            ts = activity.get("last_timestamp")
            if ts and (
                most_recent_timestamp is None
                or self._is_newer(ts, most_recent_timestamp)
            ):
                most_recent_timestamp = ts
                most_recent_handler = handler_name

        if most_recent_handler:
            activity = all_activity[most_recent_handler]
            return {
                "handler": most_recent_handler,
                "last_timestamp": activity.get("last_timestamp"),
                "status": activity.get("status", "unknown"),
                "source_log": activity.get("source_log"),
            }

        return {
            "handler": None,
            "last_timestamp": None,
            "status": "no_data",
            "source_log": None,
        }

    def _find_handler_logs(self, handler_name: str) -> List[Path]:
        """Find all log files for a specific handler."""
        pattern = f"{handler_name}_*.log"
        return list(self.logs_dir.glob(pattern))

    def _discover_handlers(self) -> List[str]:
        """Discover all unique handler names from log files."""
        handlers = set()
        for log_file in self.logs_dir.glob("*_handler_*.log"):
            match = HANDLER_LOG_PATTERN.match(log_file.name)
            if match:
                handlers.add(match.group(1))
        return sorted(handlers)

    def _parse_log_file(self, log_file: Path) -> Optional[Dict[str, Any]]:
        """Parse a log file using bounded reading (tail lines only).

        Returns:
            Dictionary with last_timestamp, status, error_snippet or None if empty/unreadable
        """
        try:
            lines = self._read_tail_lines(log_file)
            if not lines:
                return None

            return self._extract_activity_from_lines(lines)
        except Exception:
            return None

    def _read_tail_lines(self, log_file: Path) -> List[str]:
        """Read only the last N lines of a log file (bounded reading)."""
        try:
            with open(log_file, "rb") as f:
                # Seek to end and read backwards for efficiency on large files
                f.seek(0, 2)  # Seek to end
                file_size = f.tell()

                if file_size == 0:
                    return []

                # Estimate bytes needed (average ~150 bytes per line)
                bytes_to_read = min(file_size, self.tail_lines * 200)
                f.seek(max(0, file_size - bytes_to_read))

                content = f.read().decode("utf-8", errors="ignore")
                lines = content.strip().split("\n")

                # Return only the last N lines
                return lines[-self.tail_lines :]
        except Exception:
            return []

    def _extract_activity_from_lines(
        self, lines: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Extract activity info from log lines.

        Scans lines in reverse to find most recent timestamp and status.
        """
        last_timestamp = None
        status = "unknown"
        error_snippet = None

        # First pass: collect all ERROR lines for snippet extraction
        error_lines = [line for line in lines if "[ERROR]" in line]

        # Process in reverse to find most recent first
        for line in reversed(lines):
            # Extract timestamp
            ts_match = TIMESTAMP_PATTERN.match(line)
            if ts_match and last_timestamp is None:
                last_timestamp = ts_match.group(1)

            # Detect status
            line_upper = line.upper()
            if "SUCCESS" in line_upper:
                status = "success"
                if last_timestamp is None and ts_match:
                    last_timestamp = ts_match.group(1)
                break
            elif "FAILED" in line_upper or "ERROR" in line_upper:
                status = "failed"
                # Extract error snippet from first meaningful ERROR line
                if error_lines:
                    for err_line in error_lines:
                        snippet = self._extract_error_snippet(err_line)
                        # Skip generic "FAILED" messages, prefer descriptive errors
                        if snippet and "failed" not in snippet.lower():
                            error_snippet = snippet
                            break
                    # Fallback to last error if all are generic
                    if error_snippet is None and error_lines:
                        error_snippet = self._extract_error_snippet(error_lines[-1])
                if last_timestamp is None and ts_match:
                    last_timestamp = ts_match.group(1)
                break

        if last_timestamp is None:
            return None

        result: Dict[str, Any] = {
            "last_timestamp": last_timestamp,
            "status": status,
            "source_log": None,
        }

        if error_snippet:
            result["error_snippet"] = error_snippet

        return result

    def _extract_error_snippet(self, line: str) -> str:
        """Extract meaningful error message from log line."""
        # Try to extract message after [ERROR]
        if "[ERROR]" in line:
            parts = line.split("[ERROR]", 1)
            if len(parts) > 1:
                snippet = parts[1].strip()
                # Trim common prefixes
                for prefix in [":", " - "]:
                    if snippet.startswith(prefix):
                        snippet = snippet[len(prefix) :].strip()
                return snippet[:200]  # Limit length
        return line[-200:]  # Fallback: last 200 chars

    def _is_newer(self, ts1: str, ts2: str) -> bool:
        """Compare two timestamps (string comparison works for ISO format)."""
        return ts1 > ts2
