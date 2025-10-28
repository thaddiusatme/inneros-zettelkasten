"""MetricsEndpoint for HTTP JSON metrics API."""

from datetime import datetime
from typing import Dict, Any

from .metrics_collector import MetricsCollector
from .metrics_storage import MetricsStorage


class MetricsEndpoint:
    """HTTP endpoint for serving metrics data.

    Provides JSON API for current metrics and historical data.
    """

    def __init__(self, collector: MetricsCollector, storage: MetricsStorage):
        """Initialize endpoint with collector and storage.

        Args:
            collector: MetricsCollector instance
            storage: MetricsStorage instance
        """
        self.collector = collector
        self.storage = storage

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics with history.

        Returns:
            Dictionary with status, timestamp, current metrics, and history
        """
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "current": self.collector.get_all_metrics(),
            "history": self.storage.get_last_24h(),
        }
