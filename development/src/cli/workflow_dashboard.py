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

# Use absolute import for direct script execution
from src.cli.workflow_dashboard_utils import (
    CLIIntegrator, 
    StatusPanelRenderer, 
    AsyncCLIExecutor, 
    TestablePanel,
    RICH_AVAILABLE
)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
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
        self.async_executor = AsyncCLIExecutor()
        
        # Keyboard shortcut mapping (TDD Iteration 2)
        self.key_commands = {
            'p': {'cli': 'core_workflow_cli.py', 'args': ['process-inbox'], 'desc': 'Process Inbox'},
            'w': {'cli': 'weekly_review_cli.py', 'args': ['weekly-review'], 'desc': 'Weekly Review'},
            'f': {'cli': 'fleeting_cli.py', 'args': ['fleeting-health'], 'desc': 'Fleeting Health'},
            's': {'cli': 'core_workflow_cli.py', 'args': ['status', '--format', 'json'], 'desc': 'System Status'},
            'b': {'cli': 'safe_workflow_cli.py', 'args': ['backup'], 'desc': 'Create Backup'},
            'q': {'exit': True, 'desc': 'Quit Dashboard'}
        }
        
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
    
    def handle_key_press(self, key: str) -> Dict[str, Any]:
        """
        Handle keyboard shortcut press.
        
        TDD Iteration 2: P0.2 - Keyboard Navigation
        Enhanced in REFACTOR with improved error messages
        
        Args:
            key: Key pressed (single character, lowercase)
            
        Returns:
            Dictionary with 'success', 'exit', 'error', 'message' keys
        """
        key = key.lower()
        
        # Check if key is valid
        if key not in self.key_commands:
            # Enhanced error message with actionable guidance (REFACTOR phase)
            valid_keys = ', '.join(sorted(self.key_commands.keys()))
            return {
                'error': True,
                'message': (
                    f"Invalid key '{key}'. "
                    f"Valid shortcuts: [{valid_keys.upper()}]. "
                    f"Press [?] for help (planned for P2.3)."
                )
            }
        
        command = self.key_commands[key]
        
        # Handle quit
        if command.get('exit'):
            return {'exit': True, 'success': True}
        
        # Execute CLI command
        result = self.async_executor.execute_with_progress(
            cli_name=command['cli'],
            args=command['args'],
            vault_path=self.vault_path
        )
        
        return {
            'success': result['returncode'] == 0,
            'returncode': result['returncode'],
            'stdout': result['stdout'],
            'stderr': result['stderr']
        }
    
    def render_quick_actions_panel(self) -> Any:
        """
        Render quick actions panel with keyboard shortcuts.
        
        TDD Iteration 2: P0.2 - Quick Actions Panel
        
        Returns:
            Rich Panel object or formatted string
        """
        if not RICH_AVAILABLE:
            lines = ["⚡ Quick Actions:"]
            for key, cmd in self.key_commands.items():
                lines.append(f"  [{key.upper()}] {cmd['desc']}")
            return "\n".join(lines)
        
        # Build panel content as string for GREEN phase (will enhance in REFACTOR)
        lines = ["⚡ Quick Actions:\n"]
        shortcuts = list(self.key_commands.items())
        for i in range(0, len(shortcuts), 3):
            row_items = shortcuts[i:i+3]
            row_text = "  ".join(
                f"[{k.upper()}] {cmd['desc']}" 
                for k, cmd in row_items
            )
            lines.append(row_text)
        
        lines.append("\nPress any key to execute action...")
        content_str = "\n".join(lines)
        
        # Return TestablePanel (converts to string for tests, renders as Panel for Rich)
        panel = Panel(
            content_str,
            title="⚡ Quick Actions",
            border_style="cyan"
        )
        return TestablePanel(panel, content_str)
    
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
