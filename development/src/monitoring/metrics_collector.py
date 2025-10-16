"""MetricsCollector for system metrics tracking."""

from typing import Dict, List, Any


class MetricsCollector:
    """Collects system metrics: counters, gauges, and histograms.
    
    Tracks three metric types:
    - Counters: Cumulative values (e.g., notes_processed)
    - Gauges: Current state values (e.g., active_watchers)
    - Histograms: Value distributions (e.g., processing_time_ms)
    """
    
    def __init__(self):
        """Initialize empty metric storage."""
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric.
        
        Args:
            name: Counter name
            value: Amount to increment (default: 1)
        """
        if name not in self._counters:
            self._counters[name] = 0
        self._counters[name] += value
    
    def get_counter(self, name: str) -> int:
        """Get current counter value.
        
        Args:
            name: Counter name
            
        Returns:
            Current counter value
        """
        return self._counters.get(name, 0)
    
    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge metric to specific value.
        
        Args:
            name: Gauge name
            value: New value
        """
        self._gauges[name] = value
    
    def get_gauge(self, name: str) -> float:
        """Get current gauge value.
        
        Args:
            name: Gauge name
            
        Returns:
            Current gauge value
        """
        return self._gauges.get(name, 0.0)
    
    def record_histogram(self, name: str, value: float) -> None:
        """Record a value in histogram distribution.
        
        Args:
            name: Histogram name
            value: Value to record
        """
        if name not in self._histograms:
            self._histograms[name] = []
        self._histograms[name].append(value)
    
    def get_histogram(self, name: str) -> List[float]:
        """Get histogram values.
        
        Args:
            name: Histogram name
            
        Returns:
            List of recorded values
        """
        return self._histograms.get(name, [])
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get complete snapshot of all metrics.
        
        Returns:
            Dictionary with counters, gauges, and histograms
        """
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: list(v) for k, v in self._histograms.items()}
        }
