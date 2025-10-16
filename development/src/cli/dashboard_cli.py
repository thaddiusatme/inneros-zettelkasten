"""
System Observability Phase 2: Dashboard Launcher - TDD Implementation

Provides unified entry points for dashboard access:
- Web UI dashboard (workflow_dashboard.py)
- Live terminal dashboard (terminal_dashboard.py)

Phase: GREEN - Minimal implementation to pass tests
Target: <200 LOC main file with utility extraction

Architecture:
- DashboardLauncher: Web UI dashboard launcher
- TerminalDashboardLauncher: Live terminal mode launcher
- DashboardOrchestrator: Main orchestration class
- Utilities extracted to dashboard_utils.py

Following patterns from Phase 1 status CLI success.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Import Phase 1 utilities for daemon detection
try:
    from .status_utils import DaemonDetector
    HAVE_STATUS_UTILS = True
except ImportError:
    HAVE_STATUS_UTILS = False


class DashboardLauncher:
    """Launcher for web UI workflow dashboard.
    
    GREEN phase: Minimal implementation.
    """
    
    def __init__(self, vault_path: str = '.'):
        """Initialize dashboard launcher.
        
        Args:
            vault_path: Path to vault root directory
        """
        self.vault_path = vault_path
        self.process: Optional[subprocess.Popen] = None
        
        # Find workflow_dashboard.py
        cli_dir = Path(__file__).parent
        self.dashboard_script = cli_dir / 'workflow_dashboard.py'
    
    def launch(self) -> Dict[str, Any]:
        """Launch workflow dashboard.
        
        Returns:
            Result dictionary with success status and URL
        """
        # Check if already running
        if self.process and self.process.poll() is None:
            return {
                'success': False,
                'message': 'Dashboard already running',
                'url': 'http://localhost:8000'  # Default port
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
                start_new_session=True  # Detach from parent
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


class TerminalDashboardLauncher:
    """Launcher for live terminal dashboard.
    
    GREEN phase: Minimal implementation.
    """
    
    def __init__(self, daemon_url: str = 'http://localhost:8080'):
        """Initialize terminal dashboard launcher.
        
        Args:
            daemon_url: URL of automation daemon
        """
        self.daemon_url = daemon_url
        
        # Find terminal_dashboard.py
        cli_dir = Path(__file__).parent
        self.dashboard_script = cli_dir / 'terminal_dashboard.py'
    
    def launch(self) -> Dict[str, Any]:
        """Launch terminal dashboard.
        
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
                check=False  # Don't raise on non-zero exit
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


class DashboardOrchestrator:
    """Main orchestrator for dashboard commands.
    
    GREEN phase: Minimal implementation.
    """
    
    def __init__(self, vault_path: str = '.'):
        """Initialize dashboard orchestrator.
        
        Args:
            vault_path: Path to vault root directory
        """
        self.vault_path = vault_path
        
        # Initialize launchers
        self.web_launcher = DashboardLauncher(vault_path=vault_path)
        self.terminal_launcher = TerminalDashboardLauncher()
        
        # Initialize daemon detector if available
        self.daemon_detector = DaemonDetector() if HAVE_STATUS_UTILS else None
    
    def run(self, live_mode: bool = False) -> Dict[str, Any]:
        """Run dashboard launcher.
        
        Args:
            live_mode: If True, launch terminal dashboard; else web UI
            
        Returns:
            Result dictionary with success status
        """
        if live_mode:
            # Launch terminal dashboard
            result = self.terminal_launcher.launch()
            result['mode'] = 'live'
            return result
        else:
            # Launch web UI dashboard
            result = self.web_launcher.launch()
            result['mode'] = 'web'
            return result
    
    def check_daemon_status(self) -> Dict[str, Any]:
        """Check if automation daemon is running.
        
        Returns:
            Daemon status dictionary
        """
        if self.daemon_detector:
            is_running, pid = self.daemon_detector.is_running()
            return {
                'running': is_running,
                'available': True,
                'pid': pid
            }
        else:
            return {
                'running': False,
                'available': False,
                'message': 'Status utilities not available'
            }


def main():
    """CLI entry point for dashboard commands."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='InnerOS Dashboard Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  inneros dashboard              Launch web UI dashboard
  inneros dashboard --live       Launch live terminal dashboard
  
Dashboard provides real-time system monitoring and quick workflow actions.
        """
    )
    
    parser.add_argument(
        'vault_path',
        nargs='?',
        default='.',
        help='Path to vault root (default: current directory)'
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Launch live terminal dashboard instead of web UI'
    )
    
    parser.add_argument(
        '--daemon-url',
        default='http://localhost:8080',
        help='Daemon URL for live mode (default: http://localhost:8080)'
    )
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = DashboardOrchestrator(vault_path=args.vault_path)
    
    # Update terminal launcher URL if specified
    if args.live and args.daemon_url:
        orchestrator.terminal_launcher.daemon_url = args.daemon_url
    
    # Run appropriate launcher
    result = orchestrator.run(live_mode=args.live)
    
    # Display results
    if result.get('success'):
        print(f"✅ {result.get('message', 'Dashboard launched')}")
        if result.get('url'):
            print(f"   URL: {result['url']}")
        if result.get('mode') == 'web':
            print("\n   Press Ctrl+C to stop the dashboard")
    else:
        print(f"❌ {result.get('message', 'Failed to launch dashboard')}")
        if result.get('error'):
            sys.exit(1)


if __name__ == '__main__':
    main()
