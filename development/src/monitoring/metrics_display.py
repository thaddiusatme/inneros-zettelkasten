"""Metrics display utilities for dashboard integration.

Provides formatted metrics output for terminal and web dashboards.
"""

from typing import Dict, List, Any, Optional
from .metrics_collector import MetricsCollector
from .metrics_storage import MetricsStorage
from .metrics_utils import MetricsFormatter


class MetricsDisplayFormatter:
    """Formats metrics for terminal dashboard display."""
    
    def __init__(self, collector: MetricsCollector, storage: MetricsStorage):
        """Initialize formatter with collector and storage.
        
        Args:
            collector: MetricsCollector instance
            storage: MetricsStorage instance
        """
        self.collector = collector
        self.storage = storage
        self.formatter = MetricsFormatter()
    
    def format_metrics_summary(self) -> str:
        """Format metrics summary for terminal display.
        
        Returns:
            Formatted string with metrics overview
        """
        metrics = self.collector.get_all_metrics()
        
        lines = ["📊 System Metrics", ""]
        
        # Format counters
        if metrics.get("counters"):
            lines.append("Counters:")
            for name, value in metrics["counters"].items():
                lines.append(f"  • {self.formatter.format_counter(name, value)}")
            lines.append("")
        
        # Format gauges
        if metrics.get("gauges"):
            lines.append("Gauges:")
            for name, value in metrics["gauges"].items():
                lines.append(f"  • {self.formatter.format_gauge(name, value)}")
            lines.append("")
        
        # Format histograms
        if metrics.get("histograms"):
            lines.append("Processing Times:")
            for name, values in metrics["histograms"].items():
                lines.append(f"  • {self.formatter.format_histogram_summary(name, values)}")
            lines.append("")
        
        return "\n".join(lines)
    
    def format_metrics_table_data(self) -> List[List[str]]:
        """Format metrics as table rows for Rich display.
        
        Returns:
            List of table rows [metric_name, type, value]
        """
        metrics = self.collector.get_all_metrics()
        rows = []
        
        # Add counters
        for name, value in metrics.get("counters", {}).items():
            rows.append([name, "counter", f"{value:,}"])
        
        # Add gauges
        for name, value in metrics.get("gauges", {}).items():
            rows.append([name, "gauge", f"{value:.2f}"])
        
        # Add histogram summaries
        for name, values in metrics.get("histograms", {}).items():
            if values:
                avg = sum(values) / len(values)
                rows.append([name, "histogram", f"avg: {avg:.1f}ms ({len(values)} samples)"])
        
        return rows
    
    def get_metrics_json(self) -> Dict[str, Any]:
        """Get metrics in JSON format for web dashboard.
        
        Returns:
            Dictionary with current metrics and history
        """
        return {
            "current": self.collector.get_all_metrics(),
            "history": self.storage.get_last_24h(),
            "hourly": self.storage.aggregate_hourly()
        }


class WebDashboardMetrics:
    """Metrics integration for web dashboard."""
    
    def __init__(self, collector: MetricsCollector, storage: MetricsStorage):
        """Initialize web dashboard metrics.
        
        Args:
            collector: MetricsCollector instance
            storage: MetricsStorage instance
        """
        self.collector = collector
        self.storage = storage
    
    def get_metrics_html(self) -> str:
        """Generate HTML metrics card for web dashboard.
        
        Returns:
            HTML string with metrics display
        """
        metrics = self.collector.get_all_metrics()
        
        html_parts = [
            '<div class="metrics-card">',
            '<h3>📊 System Metrics</h3>',
        ]
        
        # Counters
        if metrics.get("counters"):
            html_parts.append('<div class="metrics-section">')
            html_parts.append('<h4>Counters</h4>')
            html_parts.append('<ul>')
            for name, value in metrics["counters"].items():
                html_parts.append(f'<li><strong>{name}:</strong> {value:,}</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')
        
        # Gauges
        if metrics.get("gauges"):
            html_parts.append('<div class="metrics-section">')
            html_parts.append('<h4>Gauges</h4>')
            html_parts.append('<ul>')
            for name, value in metrics["gauges"].items():
                html_parts.append(f'<li><strong>{name}:</strong> {value:.2f}</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')
        
        # Histograms
        if metrics.get("histograms"):
            html_parts.append('<div class="metrics-section">')
            html_parts.append('<h4>Processing Times</h4>')
            html_parts.append('<ul>')
            for name, values in metrics["histograms"].items():
                if values:
                    avg = sum(values) / len(values)
                    html_parts.append(
                        f'<li><strong>{name}:</strong> '
                        f'avg {avg:.1f}ms ({len(values)} samples)</li>'
                    )
            html_parts.append('</ul>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def get_metrics_api_response(self) -> Dict[str, Any]:
        """Get metrics as API response for AJAX polling.
        
        Returns:
            Dictionary with metrics and metadata
        """
        from datetime import datetime
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "metrics": self.collector.get_all_metrics(),
            "recent_count": len(self.storage.get_last_24h())
        }
