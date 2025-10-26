"""Utility functions for metrics collection and aggregation.

Extracted utilities following ADR-001 modular architecture pattern.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class TimeWindowManager:
    """Manages time windows for metrics retention and aggregation."""

    @staticmethod
    def is_within_window(timestamp: str, hours: int) -> bool:
        """Check if timestamp is within retention window.
        
        Args:
            timestamp: ISO format timestamp string
            hours: Retention window in hours
            
        Returns:
            True if timestamp is within window
        """
        entry_time = datetime.fromisoformat(timestamp)
        cutoff = datetime.now() - timedelta(hours=hours)
        return entry_time > cutoff

    @staticmethod
    def get_hour_key(timestamp: str) -> str:
        """Get hour bucket key for aggregation.
        
        Args:
            timestamp: ISO format timestamp string
            
        Returns:
            Hour key in format "YYYY-MM-DD HH:00"
        """
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:00")

    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in ISO format.
        
        Returns:
            Current timestamp string
        """
        return datetime.now().isoformat()


class MetricsAggregator:
    """Aggregates metrics for analysis and reporting."""

    @staticmethod
    def group_by_hour(entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group metrics entries by hour.
        
        Args:
            entries: List of timestamped metric entries
            
        Returns:
            Dictionary mapping hour keys to entry lists
        """
        hourly_groups: Dict[str, List[Dict[str, Any]]] = {}

        for entry in entries:
            hour_key = TimeWindowManager.get_hour_key(entry["timestamp"])
            if hour_key not in hourly_groups:
                hourly_groups[hour_key] = []
            hourly_groups[hour_key].append(entry)

        return hourly_groups

    @staticmethod
    def calculate_hourly_stats(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for hourly metrics.
        
        Args:
            entries: List of metric entries in same hour
            
        Returns:
            Aggregated statistics
        """
        if not entries:
            return {"count": 0, "metrics": {}}

        # For minimal implementation, return first entry's metrics
        # Future: Add sum, avg, min, max calculations
        return {
            "count": len(entries),
            "metrics": entries[0]["metrics"] if entries else {}
        }


class MetricsFormatter:
    """Formats metrics for display and export."""

    @staticmethod
    def format_counter(name: str, value: int) -> str:
        """Format counter metric for display.
        
        Args:
            name: Counter name
            value: Counter value
            
        Returns:
            Formatted string
        """
        return f"{name}: {value:,}"

    @staticmethod
    def format_gauge(name: str, value: float) -> str:
        """Format gauge metric for display.
        
        Args:
            name: Gauge name
            value: Gauge value
            
        Returns:
            Formatted string
        """
        return f"{name}: {value:.2f}"

    @staticmethod
    def format_histogram_summary(name: str, values: List[float]) -> str:
        """Format histogram summary for display.
        
        Args:
            name: Histogram name
            values: List of recorded values
            
        Returns:
            Formatted summary string
        """
        if not values:
            return f"{name}: (no data)"

        count = len(values)
        avg = sum(values) / count
        min_val = min(values)
        max_val = max(values)

        return f"{name}: count={count}, avg={avg:.1f}, min={min_val:.1f}, max={max_val:.1f}"


class RingBuffer:
    """Efficient ring buffer for time-windowed storage.
    
    Optimizes memory usage for metrics retention.
    """

    def __init__(self, max_size: Optional[int] = None):
        """Initialize ring buffer.
        
        Args:
            max_size: Maximum entries to retain (None for unlimited)
        """
        self.max_size = max_size
        self._buffer: List[Any] = []

    def append(self, item: Any) -> None:
        """Add item to buffer.
        
        Args:
            item: Item to add
        """
        self._buffer.append(item)
        if self.max_size and len(self._buffer) > self.max_size:
            self._buffer.pop(0)

    def filter(self, predicate) -> List[Any]:
        """Filter buffer items.
        
        Args:
            predicate: Filter function
            
        Returns:
            Filtered list
        """
        return [item for item in self._buffer if predicate(item)]

    def get_all(self) -> List[Any]:
        """Get all buffer items.
        
        Returns:
            List of all items
        """
        return list(self._buffer)

    def clear(self) -> None:
        """Clear all buffer items."""
        self._buffer.clear()

    def __len__(self) -> int:
        """Get buffer size."""
        return len(self._buffer)
