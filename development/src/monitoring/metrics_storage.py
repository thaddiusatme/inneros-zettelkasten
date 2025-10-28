"""MetricsStorage for time-windowed metrics retention."""

import json
from typing import Dict, List, Any

from .metrics_utils import TimeWindowManager, MetricsAggregator


class MetricsStorage:
    """In-memory storage with time-windowed aggregation.

    Stores metrics with timestamps in a ring buffer,
    retaining only data within the configured window.
    """

    def __init__(self, retention_hours: int = 24):
        """Initialize storage with retention window.

        Args:
            retention_hours: Hours to retain metrics (default: 24)
        """
        self.retention_hours = retention_hours
        self._storage: List[Dict[str, Any]] = []

    def store(self, metrics: Dict[str, Any]) -> None:
        """Store metrics with current timestamp.

        Args:
            metrics: Metrics dictionary to store
        """
        entry = {
            "timestamp": TimeWindowManager.get_current_timestamp(),
            "metrics": metrics,
        }
        self._storage.append(entry)
        self._prune_old_entries()

    def get_latest(self) -> Dict[str, Any]:
        """Get most recent metrics entry.

        Returns:
            Latest metrics with timestamp, or None if empty
        """
        if not self._storage:
            return None
        return self._storage[-1]

    def get_last_24h(self) -> List[Dict[str, Any]]:
        """Get metrics from last 24 hours.

        Returns:
            List of metrics entries within retention window
        """
        self._prune_old_entries()
        return list(self._storage)

    def aggregate_hourly(self) -> List[Dict[str, Any]]:
        """Aggregate metrics by hour.

        Returns:
            List of hourly aggregated metrics
        """
        if not self._storage:
            return []

        # Use utility for grouping
        hourly_groups = MetricsAggregator.group_by_hour(self._storage)

        # Create aggregated entries
        result = []
        for hour, entries in sorted(hourly_groups.items()):
            stats = MetricsAggregator.calculate_hourly_stats(entries)
            result.append(
                {"hour": hour, "metrics": stats["metrics"], "count": stats["count"]}
            )

        return result

    def export_json(self) -> str:
        """Export all metrics as JSON string.

        Returns:
            JSON string of all stored metrics
        """
        return json.dumps(self._storage, indent=2)

    def _prune_old_entries(self) -> None:
        """Remove entries older than retention window."""
        if not self._storage:
            return

        # Use utility for time window checking
        self._storage = [
            entry
            for entry in self._storage
            if TimeWindowManager.is_within_window(
                entry["timestamp"], self.retention_hours
            )
        ]
