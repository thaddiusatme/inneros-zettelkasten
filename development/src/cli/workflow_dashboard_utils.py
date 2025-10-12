"""
Utility classes for Workflow Dashboard.

TDD Iteration 1: GREEN Phase - Minimal utility implementation
Extract utilities to keep main dashboard under 500 LOC (ADR-001 compliant)

Architecture:
- CLIIntegrator: Handle CLI subprocess calls
- StatusPanelRenderer: Rich panel creation and formatting
"""

import sys
import json
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class TestablePanel:
    """
    Wrapper for Rich Panel that converts to string for tests.
    
    TDD Iteration 2: GREEN Phase - Minimal wrapper for test compatibility
    Provides __rich__() for Rich rendering and __str__() for test assertions.
    """
    def __init__(self, panel, content_str):
        self.panel = panel
        self.content_str = content_str
    
    def __str__(self):
        return self.content_str
    
    def __rich__(self):
        return self.panel


class CLIIntegrator:
    """
    Handle subprocess calls to dedicated CLI tools.
    
    Responsibilities:
    - Execute CLI commands via subprocess
    - Parse JSON output
    - Error handling and retries
    """
    
    def __init__(self, vault_path: str = "."):
        """
        Initialize CLI integrator.
        
        Args:
            vault_path: Path to vault root
        """
        self.vault_path = vault_path
        self.cli_base_path = Path(__file__).parent
    
    def call_cli(self, cli_name: str, args: List[str]) -> Dict[str, Any]:
        """
        Call a CLI tool and parse its output.
        
        Args:
            cli_name: Name of CLI file (e.g., 'core_workflow_cli.py')
            args: CLI arguments list
            
        Returns:
            Dictionary with 'returncode', 'data', 'error' keys
        """
        try:
            cli_path = self.cli_base_path / cli_name
            
            # Build command
            cmd = [sys.executable, str(cli_path), self.vault_path] + args
            
            # Execute CLI
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse JSON output
            data = {}
            if result.returncode == 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                except json.JSONDecodeError:
                    data = {"raw_output": result.stdout}
            
            return {
                'returncode': result.returncode,
                'data': data,
                'error': result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'data': {},
                'error': 'CLI timeout'
            }
        except Exception as e:
            return {
                'returncode': -1,
                'data': {},
                'error': str(e)
            }


class StatusPanelRenderer:
    """
    Render Rich panels for status display.
    
    Responsibilities:
    - Create formatted Rich panels
    - Format metrics and indicators
    - Color-coded health status
    """
    
    def __init__(self):
        """Initialize panel renderer."""
        pass
    
    def create_inbox_panel(
        self,
        inbox_count: int,
        oldest_age_days: Optional[int] = None,
        health_indicator: str = "🟢"
    ) -> Any:
        """
        Create inbox status panel.
        
        Args:
            inbox_count: Number of inbox notes
            oldest_age_days: Age of oldest note in days
            health_indicator: Health indicator emoji
            
        Returns:
            TestablePanel (wraps Rich Panel) or string (if Rich not available)
        """
        metrics_text = self.format_inbox_metrics(inbox_count, oldest_age_days)
        
        if not RICH_AVAILABLE:
            return f"📥 Inbox Status\n{metrics_text}\n{health_indicator}"
        
        # Build content string for TestablePanel
        content_lines = [f"Notes: {inbox_count} {health_indicator}"]
        if oldest_age_days is not None:
            content_lines.append(f"Oldest: {oldest_age_days // 30} months")
        content_lines.append("Action: Process inbox")
        content_str = "\n".join(content_lines)
        
        # Create Panel
        panel = Panel(
            content_str,
            title="📥 Inbox Status",
            border_style="yellow" if inbox_count > 20 else "green"
        )
        
        # Return TestablePanel wrapper (GREEN phase - for test compatibility)
        return TestablePanel(panel, content_str)
    
    def format_inbox_metrics(
        self,
        inbox_count: int,
        oldest_age_days: Optional[int] = None
    ) -> str:
        """
        Format inbox metrics as text.
        
        Args:
            inbox_count: Number of inbox notes
            oldest_age_days: Age of oldest note in days
            
        Returns:
            Formatted metrics string
        """
        lines = [f"Notes: {inbox_count}"]
        
        if oldest_age_days is not None:
            months = oldest_age_days // 30
            lines.append(f"Oldest: {months} months ({oldest_age_days} days)")
        
        return "\n".join(lines)


class AsyncCLIExecutor:
    """
    Execute CLI commands asynchronously with progress indicators.
    
    TDD Iteration 2: GREEN Phase - Minimal async execution
    
    Responsibilities:
    - Non-blocking CLI execution using threading
    - Progress spinner display during operations
    - Success/error result reporting
    - Timeout handling
    """
    
    def __init__(self, timeout: int = 60):
        """
        Initialize async CLI executor.
        
        Args:
            timeout: Command timeout in seconds (default: 60)
        """
        self.timeout = timeout
        self.result = None
        self.thread = None
    
    def execute_with_progress(
        self,
        cli_name: str,
        args: List[str],
        vault_path: str = "."
    ) -> Dict[str, Any]:
        """
        Execute CLI command with progress indicator.
        
        Args:
            cli_name: Name of CLI file (e.g., 'core_workflow_cli.py')
            args: CLI arguments list
            vault_path: Path to vault root
            
        Returns:
            Dictionary with 'returncode', 'stdout', 'stderr', 'duration', 'timeout' keys
        """
        start_time = time.time()
        
        # Build command
        cli_path = Path(__file__).parent / cli_name
        cmd = [sys.executable, str(cli_path), vault_path] + args
        
        # Execute in subprocess (synchronous for minimal GREEN implementation)
        # Threading can be added in REFACTOR phase if needed
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            duration = time.time() - start_time
            
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': duration,
                'timeout': False
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': f'Operation timed out after {self.timeout} seconds',
                'duration': duration,
                'timeout': True
            }
