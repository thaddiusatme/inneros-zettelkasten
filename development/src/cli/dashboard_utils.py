"""
System Observability Phase 2: Dashboard Launcher Utilities

Extracted utility classes for dashboard management:
- WebDashboardLauncher: Launch web UI dashboard subprocess
- LiveDashboardLauncher: Launch terminal dashboard subprocess
- OutputFormatter: Format CLI output messages

Phase: REFACTOR - Production-ready utilities extracted from main file
Following patterns from Phase 1 status_utils.py success.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class WebDashboardLauncher:
    """Utility for launching web UI workflow dashboard.
    
    REFACTOR phase: Extracted from DashboardLauncher.
    """
    
    def __init__(self, vault_path: str = '.'):
        """Initialize web dashboard launcher.
        
        Args:
            vault_path: Path to vault root directory
        """
        self.vault_path = vault_path
        self.process: Optional[subprocess.Popen] = None
        
        # Find workflow_dashboard.py
        cli_dir = Path(__file__).parent
        self.dashboard_script = cli_dir / 'workflow_dashboard.py'
    
    def is_running(self) -> bool:
        """Check if dashboard is currently running.
        
        Returns:
            True if running, False otherwise
        """
        return self.process is not None and self.process.poll() is None
    
    def launch(self) -> Dict[str, Any]:
        """Launch workflow dashboard subprocess.
        
        Returns:
            Result dictionary with success status and URL
        """
        # Check if already running
        if self.is_running():
            return {
                'success': False,
                'message': 'Dashboard already running',
                'url': 'http://localhost:8000'
            }
        
        # Check if dashboard script exists
        if not self.dashboard_script.exists():
            return {
                'success': False,
                'error': True,
                'message': f'Dashboard script not found: {self.dashboard_script}'
            }
        
        try:
            # Launch dashboard as subprocess
            self.process = subprocess.Popen(
                [sys.executable, str(self.dashboard_script), self.vault_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Check if process started successfully
            if self.process.poll() is not None:
                return {
                    'success': False,
                    'error': True,
                    'message': 'Dashboard process exited immediately (possible port conflict)'
                }
            
            return {
                'success': True,
                'process': self.process,
                'url': 'http://localhost:8000',
                'message': 'Dashboard launched successfully'
            }
            
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': True,
                'message': f'Dashboard not found: {e}'
            }
        except PermissionError as e:
            return {
                'success': False,
                'error': True,
                'message': f'Permission denied: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': True,
                'message': f'Failed to launch dashboard: {e}'
            }


class LiveDashboardLauncher:
    """Utility for launching live terminal dashboard.
    
    REFACTOR phase: Extracted from TerminalDashboardLauncher.
    """
    
    def __init__(self, daemon_url: str = 'http://localhost:8080'):
        """Initialize live dashboard launcher.
        
        Args:
            daemon_url: URL of automation daemon
        """
        self.daemon_url = daemon_url
        
        # Find terminal_dashboard.py
        cli_dir = Path(__file__).parent
        self.dashboard_script = cli_dir / 'terminal_dashboard.py'
    
    def launch(self) -> Dict[str, Any]:
        """Launch terminal dashboard subprocess.
        
        Returns:
            Result dictionary with success status
        """
        # Check if dashboard script exists
        if not self.dashboard_script.exists():
            return {
                'success': False,
                'error': True,
                'message': f'Terminal dashboard script not found: {self.dashboard_script}'
            }
        
        try:
            # Launch terminal dashboard with blocking subprocess
            result = subprocess.run(
                [sys.executable, str(self.dashboard_script), '--url', self.daemon_url],
                check=False
            )
            
            return {
                'success': True,
                'message': 'Terminal dashboard stopped',
                'exit_code': result.returncode
            }
            
        except KeyboardInterrupt:
            return {
                'success': True,
                'message': 'Dashboard stopped by user'
            }
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': True,
                'message': f'Dashboard not found: {e}'
            }
        except PermissionError as e:
            return {
                'success': False,
                'error': True,
                'message': f'Permission denied: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': True,
                'message': f'Failed to launch terminal dashboard: {e}'
            }


class OutputFormatter:
    """Format CLI output messages.
    
    REFACTOR phase: Extracted formatting logic.
    """
    
    @staticmethod
    def format_success(result: Dict[str, Any]) -> str:
        """Format success message.
        
        Args:
            result: Result dictionary from launcher
            
        Returns:
            Formatted success message
        """
        message = f"✅ {result.get('message', 'Dashboard launched')}"
        
        if result.get('url'):
            message += f"\n   URL: {result['url']}"
        
        if result.get('mode') == 'web':
            message += "\n\n   Press Ctrl+C to stop the dashboard"
        
        return message
    
    @staticmethod
    def format_error(result: Dict[str, Any]) -> str:
        """Format error message.
        
        Args:
            result: Result dictionary from launcher
            
        Returns:
            Formatted error message
        """
        return f"❌ {result.get('message', 'Failed to launch dashboard')}"
