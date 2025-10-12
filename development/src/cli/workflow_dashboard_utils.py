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


class ProgressDisplayManager:
    """
    Manage Rich progress indicators and spinners.
    
    TDD Iteration 2: REFACTOR Phase - Extracted utility for progress display
    
    Responsibilities:
    - Create and manage Rich Progress objects
    - Show/hide progress spinners
    - Track operation duration
    - Format progress messages
    """
    
    def __init__(self):
        """Initialize progress display manager."""
        self.active_progress = None
        self.show_progress = RICH_AVAILABLE
    
    def format_operation_message(self, operation: str, status: str = "running") -> str:
        """
        Format operation status message.
        
        Args:
            operation: Operation name (e.g., "Process Inbox")
            status: Status indicator (running, success, error)
            
        Returns:
            Formatted message string
        """
        status_icons = {
            'running': '⏳',
            'success': '✅',
            'error': '❌'
        }
        icon = status_icons.get(status, '•')
        return f"{icon} {operation}..."


class ActivityLogger:
    """
    Log and track dashboard operations.
    
    TDD Iteration 2: REFACTOR Phase - Foundation for P1.2 Activity Log Panel
    
    Responsibilities:
    - Store operation history
    - Format activity entries
    - Provide last N operations
    - Track timestamps and results
    """
    
    def __init__(self, max_entries: int = 10):
        """
        Initialize activity logger.
        
        Args:
            max_entries: Maximum number of entries to retain
        """
        self.max_entries = max_entries
        self.activities = []
    
    def log_operation(
        self,
        action: str,
        result: str,
        status: str = "success"
    ):
        """
        Log an operation.
        
        Args:
            action: Action performed (e.g., "Process Inbox")
            result: Result description
            status: Operation status (success, error, info)
        """
        import datetime
        entry = {
            'timestamp': datetime.datetime.now(),
            'action': action,
            'result': result,
            'status': status
        }
        self.activities.append(entry)
        
        # Keep only last max_entries
        if len(self.activities) > self.max_entries:
            self.activities = self.activities[-self.max_entries:]
    
    def get_recent_activities(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent activities.
        
        Args:
            count: Number of activities to return
            
        Returns:
            List of activity dictionaries
        """
        return self.activities[-count:]


class AsyncCLIExecutor:
    """
    Execute CLI commands asynchronously with progress indicators.
    
    TDD Iteration 2: GREEN Phase - Minimal async execution
    Enhanced in REFACTOR with ProgressDisplayManager integration
    
    Responsibilities:
    - Non-blocking CLI execution using threading
    - Progress spinner display during operations
    - Success/error result reporting
    - Timeout handling
    """
    
    def __init__(self, timeout: int = 60, progress_manager: Optional['ProgressDisplayManager'] = None):
        """
        Initialize async CLI executor.
        
        Args:
            timeout: Command timeout in seconds (default: 60)
            progress_manager: Optional progress display manager
        """
        self.timeout = timeout
        self.result = None
        self.thread = None
        self.progress_manager = progress_manager or ProgressDisplayManager()
    
    def execute_with_progress(
        self,
        cli_name: str,
        args: List[str],
        vault_path: str = "."
    ) -> Dict[str, Any]:
        """
        Execute CLI command with live progress display.
        
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
        
        # Show what's happening
        operation_name = self._get_operation_name(cli_name, args)
        print(f"\n⏳ {operation_name}...")
        print("   (This may take a moment for large collections)\n")
        
        # Execute in subprocess with live output
        try:
            # Use Popen for streaming output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Collect output while showing progress
            stdout_lines = []
            stderr_lines = []
            
            # Read progress from stderr in real-time
            import select
            import os
            import fcntl
            
            # Make stderr non-blocking
            stderr_fd = process.stderr.fileno()
            flags = fcntl.fcntl(stderr_fd, fcntl.F_GETFL)
            fcntl.fcntl(stderr_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            last_progress = ""
            
            while True:
                # Check if process finished
                if process.poll() is not None:
                    break
                
                # Try to read stderr (progress info)
                try:
                    # Use select to check if data available
                    ready, _, _ = select.select([process.stderr], [], [], 0.1)
                    if ready:
                        chunk = process.stderr.read(1024)
                        if chunk:
                            stderr_lines.append(chunk)
                            # Extract last line for display (progress info)
                            lines = chunk.split('\r')
                            if lines:
                                last_progress = lines[-1].strip()
                                if last_progress:
                                    print(f"\r   {last_progress}", end='', flush=True)
                except (IOError, OSError):
                    # No data available yet
                    time.sleep(0.1)
            
            # Get remaining output
            stdout, stderr = process.communicate(timeout=self.timeout)
            stdout_lines.append(stdout)
            stderr_lines.append(stderr)
            
            # Clear spinner line
            print("\r   " + " " * 50 + "\r", end='', flush=True)
            
            duration = time.time() - start_time
            full_stdout = ''.join(stdout_lines)
            full_stderr = ''.join(stderr_lines)
            
            return {
                'returncode': process.returncode,
                'stdout': full_stdout,
                'stderr': full_stderr,
                'duration': duration,
                'timeout': False
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            if 'process' in locals():
                process.kill()
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': f'Operation timed out after {self.timeout} seconds',
                'duration': duration,
                'timeout': True
            }
    
    def _get_operation_name(self, cli_name: str, args: List[str]) -> str:
        """Get friendly operation name from CLI name and args."""
        if 'process-inbox' in args:
            return "Processing Inbox"
        elif 'status' in args:
            return "Getting Status"
        elif 'weekly-review' in args:
            return "Running Weekly Review"
        elif 'fleeting-health' in args:
            return "Checking Fleeting Health"
        elif 'backup' in args:
            return "Creating Backup"
        return "Running Operation"
