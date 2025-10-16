"""
Utility classes for Terminal UI Dashboard.

TDD Iteration 7: Terminal UI Dashboard
REFACTOR phase - Extracted utility classes.

Architecture:
- StatusFormatter: Format health data for display
- HealthPoller: Handle HTTP polling logic
- TableRenderer: Rich table creation and formatting
- DashboardOrchestrator: Coordinate dashboard lifecycle
"""

import json
import time
import urllib.request
from urllib.error import HTTPError, URLError
from typing import Dict, Any, Optional, Callable

try:
    from rich.table import Table
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class HealthPoller:
    """
    Handle HTTP polling of daemon health endpoint.
    
    Responsibilities:
    - HTTP request management
    - Error handling and retries
    - Response parsing
    """
    
    def __init__(self, base_url: str, timeout: int = 5):
        """
        Initialize health poller.
        
        Args:
            base_url: Base URL of daemon (e.g., 'http://localhost:8080')
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.health_url = f"{base_url}/health"
    
    def fetch(self) -> Dict[str, Any]:
        """
        Fetch current health status.
        
        Returns:
            Health data dictionary or error structure
        """
        try:
            with urllib.request.urlopen(self.health_url, timeout=self.timeout) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
                
        except HTTPError as e:
            # 503 still contains valid JSON data
            if e.code == 503:
                try:
                    data = json.loads(e.read().decode('utf-8'))
                    return data
                except:
                    pass
            return self._create_error_response(f'HTTP {e.code}: {e.reason}', e.code)
            
        except URLError as e:
            return self._create_error_response(f'Connection error: {e.reason}', 0)
            
        except Exception as e:
            return self._create_error_response(str(e), 0)
    
    def _create_error_response(self, message: str, status_code: int) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            'error': True,
            'message': message,
            'daemon': {'is_healthy': False, 'status_code': status_code},
            'handlers': {}
        }


class StatusFormatter:
    """
    Format health data for terminal display.
    
    Responsibilities:
    - Color-coded status indicators
    - Metric formatting
    - Human-readable output
    """
    
    @staticmethod
    def format_indicator(is_healthy: bool) -> str:
        """
        Format status indicator with color coding.
        
        Args:
            is_healthy: Health status boolean
            
        Returns:
            Formatted status string with emoji and color
        """
        if not RICH_AVAILABLE:
            return "✓" if is_healthy else "✗"
        
        if is_healthy:
            return "[green]🟢 Healthy[/green]"
        else:
            return "[red]🔴 Unhealthy[/red]"
    
    @staticmethod
    def format_metrics(handler_data: Dict[str, Any]) -> str:
        """
        Format handler metrics for display.
        
        Args:
            handler_data: Handler health/metrics dictionary
            
        Returns:
            Formatted metrics string
        """
        parts = []
        
        # Events processed
        events = handler_data.get('events_processed', 0)
        parts.append(f"Events: {events}")
        
        # Average processing time
        if 'avg_processing_time' in handler_data:
            avg_time = handler_data['avg_processing_time']
            parts.append(f"Avg: {avg_time:.2f}s")
        
        return ", ".join(parts)
    
    @staticmethod
    def format_daemon_metrics(daemon_data: Dict[str, Any]) -> str:
        """
        Format daemon metrics for display.
        
        Args:
            daemon_data: Daemon health dictionary
            
        Returns:
            Formatted metrics string
        """
        status_code = daemon_data.get('status_code', 0)
        return f"HTTP {status_code}"


class TableRenderer:
    """
    Create and render Rich tables from health data.
    
    Responsibilities:
    - Table structure creation
    - Row formatting
    - Title and styling
    - Metrics display (Phase 3.1)
    """
    
    def __init__(self, formatter: StatusFormatter, metrics_collector=None):
        """
        Initialize table renderer.
        
        Args:
            formatter: StatusFormatter instance
            metrics_collector: Optional MetricsCollector for metrics display
        """
        self.formatter = formatter
        self.metrics_collector = metrics_collector
    
    def create_status_table(self, health_data: Dict[str, Any]) -> Optional['Table']:
        """
        Create Rich Table from health data.
        
        Args:
            health_data: Health status dictionary
            
        Returns:
            Rich Table instance or None if Rich not available
        """
        if not RICH_AVAILABLE:
            return None
        
        table = Table(
            title="InnerOS Automation Daemon Status",
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Status", style="white")
        table.add_column("Metrics", style="yellow")
        
        # Add daemon row
        self._add_daemon_row(table, health_data)
        
        # Add handler rows
        self._add_handler_rows(table, health_data)
        
        return table
    
    def _add_daemon_row(self, table: 'Table', health_data: Dict[str, Any]):
        """Add daemon status row to table."""
        daemon = health_data.get('daemon', {})
        is_healthy = daemon.get('is_healthy', False)
        
        status_str = self.formatter.format_indicator(is_healthy)
        metrics_str = self.formatter.format_daemon_metrics(daemon)
        
        table.add_row("Daemon", status_str, metrics_str)
    
    def _add_handler_rows(self, table: 'Table', health_data: Dict[str, Any]):
        """Add handler status rows to table."""
        handlers = health_data.get('handlers', {})
        
        for handler_name, handler_data in handlers.items():
            # Determine handler health
            handler_healthy = handler_data.get('is_healthy', False)
            if isinstance(handler_healthy, str):
                handler_healthy = handler_healthy != 'N/A'
            
            # Format row data
            handler_status = self.formatter.format_indicator(handler_healthy)
            handler_metrics = self.formatter.format_metrics(handler_data)
            
            table.add_row(f"  {handler_name}", handler_status, handler_metrics)
    
    def create_metrics_table(self) -> Optional['Table']:
        """
        Create Rich Table from metrics collector data.
        Phase 3.1: Real-time metrics display
        
        Returns:
            Rich Table instance with metrics or None if no metrics collector
        """
        if not RICH_AVAILABLE or not self.metrics_collector:
            return None
        
        table = Table(
            title="📊 System Metrics",
            show_header=True,
            header_style="bold green"
        )
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Type", style="magenta")
        table.add_column("Value", style="yellow")
        
        # Get all metrics
        metrics = self.metrics_collector.get_all_metrics()
        
        # Add counter metrics
        for name, value in metrics.get("counters", {}).items():
            table.add_row(name, "counter", f"{value:,}")
        
        # Add gauge metrics
        for name, value in metrics.get("gauges", {}).items():
            table.add_row(name, "gauge", f"{value:.2f}")
        
        # Add histogram metrics (show avg/min/max)
        for name, values in metrics.get("histograms", {}).items():
            if values:
                avg = sum(values) / len(values)
                min_val = min(values)
                max_val = max(values)
                table.add_row(
                    name,
                    "histogram",
                    f"avg: {avg:.1f}ms (min: {min_val:.0f}, max: {max_val:.0f})"
                )
        
        return table


class DashboardOrchestrator:
    """
    Coordinate dashboard lifecycle and updates.
    
    Responsibilities:
    - Polling coordination
    - Display refresh management
    - Error handling and recovery
    """
    
    def __init__(
        self,
        poller: HealthPoller,
        renderer: TableRenderer,
        refresh_interval: int = 1
    ):
        """
        Initialize dashboard orchestrator.
        
        Args:
            poller: HealthPoller instance
            renderer: TableRenderer instance
            refresh_interval: Seconds between refreshes
        """
        self.poller = poller
        self.renderer = renderer
        self.refresh_interval = refresh_interval
    
    def run(self, on_update: Callable[[Any], None]):
        """
        Run dashboard polling loop.
        
        Args:
            on_update: Callback to update display with table/panel
        """
        try:
            while True:
                # Fetch current status
                health_data = self.poller.fetch()
                
                # Create display content
                if health_data.get('error'):
                    # Error panel for connection issues
                    if RICH_AVAILABLE:
                        from rich.panel import Panel
                        error_text = Text(
                            f"⚠️  {health_data.get('message', 'Unknown error')}",
                            style="bold red"
                        )
                        content = Panel(error_text, title="Connection Error")
                    else:
                        content = f"ERROR: {health_data.get('message')}"
                else:
                    # Status table for healthy connection
                    status_table = self.renderer.create_status_table(health_data)
                    metrics_table = self.renderer.create_metrics_table()
                    
                    # Combine tables if metrics available
                    if RICH_AVAILABLE and metrics_table:
                        from rich.console import Group
                        content = Group(status_table, metrics_table)
                    else:
                        content = status_table
                
                # Update display
                on_update(content)
                
                # Wait before next refresh
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            # Graceful shutdown on Ctrl+C
            pass
