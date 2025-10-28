#!/usr/bin/env python3
"""
Terminal UI Dashboard for InnerOS Automation Daemon Monitoring.

TDD Iteration 7: Terminal UI Dashboard
Real-time monitoring with live-updating display.

Architecture:
- Polls HTTP /health endpoint every second
- Renders status using Rich library
- Color-coded indicators (🟢 healthy, 🔴 unhealthy)
- Shows daemon + handler metrics
- Modular design with utility classes

Size: ~100 LOC (ADR-001 compliant, utilities extracted)
"""

from typing import Dict, Any, Optional

from .terminal_dashboard_utils import (
    HealthPoller,
    StatusFormatter,
    TableRenderer,
    DashboardOrchestrator,
    RICH_AVAILABLE,
)

# Phase 3.1: Import metrics for dashboard integration
from src.monitoring import MetricsCollector

try:
    from rich.console import Console
    from rich.live import Live
except ImportError:
    RICH_AVAILABLE = False


# Backward compatibility functions for tests
def fetch_health_status(url: str) -> Dict[str, Any]:
    """
    Fetch health status from daemon HTTP endpoint.

    Args:
        url: Base URL of daemon (e.g., 'http://localhost:8080')

    Returns:
        Health data dictionary or error structure
    """
    poller = HealthPoller(url)
    return poller.fetch()


def format_status_indicator(is_healthy: bool) -> str:
    """
    Format status indicator with color coding.

    Args:
        is_healthy: Health status boolean

    Returns:
        Formatted status string with emoji and color
    """
    return StatusFormatter.format_indicator(is_healthy)


def create_status_table(health_data: Dict[str, Any]) -> Optional[Any]:
    """
    Create Rich Table from health data.

    Args:
        health_data: Health status dictionary

    Returns:
        Rich Table instance or None if Rich not available
    """
    formatter = StatusFormatter()
    renderer = TableRenderer(formatter)
    return renderer.create_status_table(health_data)


def run_dashboard(
    url: str = "http://localhost:8080",
    refresh_interval: int = 1,
    metrics_collector=None,
):
    """
    Run live-updating terminal dashboard.

    Args:
        url: Base URL of daemon
        refresh_interval: Seconds between refreshes
        metrics_collector: Optional MetricsCollector for metrics display
    """
    if not RICH_AVAILABLE:
        print("Error: 'rich' library required for dashboard")
        print("Install with: pip install rich")
        return

    # Phase 3.1: Initialize metrics if not provided
    if metrics_collector is None:
        metrics_collector = MetricsCollector()

    # Initialize components
    poller = HealthPoller(url)
    formatter = StatusFormatter()
    renderer = TableRenderer(formatter, metrics_collector=metrics_collector)
    orchestrator = DashboardOrchestrator(poller, renderer, refresh_interval)

    # Setup display
    console = Console()

    try:
        with Live(console=console, refresh_per_second=1) as live:
            orchestrator.run(lambda content: live.update(content))
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped by user[/yellow]")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="InnerOS Automation Daemon Terminal Dashboard"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8080",
        help="Daemon HTTP server URL (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--refresh",
        type=int,
        default=1,
        help="Refresh interval in seconds (default: 1)",
    )

    args = parser.parse_args()

    print(f"Starting dashboard monitoring {args.url}")
    print("Press Ctrl+C to stop\n")

    run_dashboard(url=args.url, refresh_interval=args.refresh)


if __name__ == "__main__":
    main()
