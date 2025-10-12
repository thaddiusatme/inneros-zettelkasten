#!/usr/bin/env python3
"""
Workflow Dashboard - Interactive Terminal UI for Workflow Operations

TDD Iteration 1: GREEN Phase - Minimal implementation for P0.1 (Inbox Status Panel)
Focus: Integrate core_workflow_cli.py and display inbox status

Architecture:
- WorkflowDashboard: Main orchestrator class
- CLIIntegrator: Handle CLI subprocess calls (in utils)
- StatusPanelRenderer: Rich panel rendering (in utils)

Size Target: <500 LOC (ADR-001 compliant with utilities extracted)
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .workflow_dashboard_utils import CLIIntegrator, StatusPanelRenderer, RICH_AVAILABLE

try:
    from rich.console import Console
except ImportError:
    RICH_AVAILABLE = False


class WorkflowDashboard:
    """
    Interactive Terminal UI Dashboard for Workflow Operations.
    
    Provides real-time status display and quick actions for:
    - Inbox processing
    - Fleeting note health
    - Weekly review
    - System status
    
    TDD Iteration 1: P0.1 - Inbox Status Panel
    """
    
    def __init__(self, vault_path: str = "."):
        """
        Initialize workflow dashboard.
        
        Args:
            vault_path: Path to vault root (defaults to current directory)
        """
        self.vault_path = vault_path
        self.cli_integrator = CLIIntegrator(vault_path=vault_path)
        self.panel_renderer = StatusPanelRenderer()
        
        if RICH_AVAILABLE:
            self.console = Console()
    
    def fetch_inbox_status(self) -> Dict[str, Any]:
        """
        Fetch inbox status via core_workflow_cli.py.
        
        Returns:
            Dictionary with workflow status data or error structure
        """
        result = self.cli_integrator.call_cli(
            'core_workflow_cli.py',
            ['status', '--format', 'json']
        )
        
        if result['returncode'] != 0:
            return {
                'error': True,
                'message': result.get('error', 'Unknown error'),
                'inbox_count': 0,
                'fleeting_count': 0
            }
        
        # Extract workflow status from data
        data = result['data']
        if 'workflow_status' in data:
            return data['workflow_status']
        
        return data
    
    def get_inbox_count(self) -> int:
        """
        Get inbox note count.
        
        Returns:
            Number of notes in inbox
        """
        status = self.fetch_inbox_status()
        return status.get('inbox_count', 0)
    
    def get_inbox_health_indicator(self, inbox_count: int) -> str:
        """
        Get health indicator based on inbox count.
        
        Rules:
        - 🟢 Green: 0-20 notes (healthy)
        - 🟡 Yellow: 21-50 notes (attention needed)
        - 🔴 Red: 51+ notes (critical)
        
        Args:
            inbox_count: Number of inbox notes
            
        Returns:
            Health indicator emoji/color string
        """
        if inbox_count <= 20:
            return "🟢" if not RICH_AVAILABLE else "[green]🟢[/green]"
        elif inbox_count <= 50:
            return "🟡" if not RICH_AVAILABLE else "[yellow]🟡[/yellow]"
        else:
            return "🔴" if not RICH_AVAILABLE else "[red]🔴[/red]"
    
    def render_inbox_panel(self) -> Any:
        """
        Render inbox status panel.
        
        Returns:
            Rich Panel object or formatted string
        """
        status = self.fetch_inbox_status()
        inbox_count = status.get('inbox_count', 0)
        
        # Calculate oldest note age (placeholder for iteration 1)
        oldest_age_days = 240  # Will be calculated in future iteration
        
        # Get health indicator
        health_indicator = self.get_inbox_health_indicator(inbox_count)
        
        # Create panel
        panel = self.panel_renderer.create_inbox_panel(
            inbox_count=inbox_count,
            oldest_age_days=oldest_age_days,
            health_indicator=health_indicator
        )
        
        return panel
    
    def display(self):
        """
        Display the dashboard (minimal for iteration 1).
        
        Shows inbox status panel only in this iteration.
        """
        if not RICH_AVAILABLE:
            print("Error: 'rich' library required for dashboard")
            print("Install with: pip install rich")
            return
        
        panel = self.render_inbox_panel()
        self.console.print(panel)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="InnerOS Workflow Dashboard - Interactive Terminal UI"
    )
    parser.add_argument(
        'vault_path',
        nargs='?',
        default='.',
        help='Path to vault root (default: current directory)'
    )
    
    args = parser.parse_args()
    
    dashboard = WorkflowDashboard(vault_path=args.vault_path)
    dashboard.display()


if __name__ == '__main__':
    main()
