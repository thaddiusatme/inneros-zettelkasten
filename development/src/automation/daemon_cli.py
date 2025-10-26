"""
Daemon CLI Entry Point - TDD Iteration 8

Command-line interface for InnerOS Automation Daemon.
Supports systemd execution with --config flag for production deployment.

Usage:
    inneros-daemon --config /etc/inneros/config.yaml
    inneros-daemon --help

Follows ADR-001: <500 LOC, single responsibility.

Size: ~100 LOC (ADR-001 compliant: <500 LOC)
"""

import sys
import argparse
import signal
from pathlib import Path
from typing import List, Optional

# Add development/src to path for imports when running directly
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from automation.daemon import AutomationDaemon
from automation.config import ConfigurationLoader


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Optional list of arguments (for testing)
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="InnerOS Automation Daemon - 24/7 knowledge workflow automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start daemon with config file
  inneros-daemon --config /etc/inneros/config.yaml
  
  # User mode installation
  inneros-daemon --config ~/.config/inneros/config.yaml
  
  # Default config location
  inneros-daemon
"""
    )

    parser.add_argument(
        "--config",
        type=str,
        default=str(Path.home() / ".config/inneros/config.yaml"),
        help="Path to configuration file (default: ~/.config/inneros/config.yaml)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="InnerOS Automation Daemon v1.0.0 (TDD Iteration 8)"
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main daemon entry point.
    
    Args:
        args: Optional command-line arguments (for testing)
    
    Returns:
        Exit code (0 = success, 1 = error)
    """
    # Parse arguments
    parsed_args = parse_args(args)

    # Load configuration
    config_path = Path(parsed_args.config)

    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}", file=sys.stderr)
        print(f"\nCreate a config file at {config_path} with:", file=sys.stderr)
        print("  daemon:", file=sys.stderr)
        print("    check_interval: 60", file=sys.stderr)
        print("    log_level: INFO", file=sys.stderr)
        return 1

    try:
        loader = ConfigurationLoader()
        config = loader.load_config(config_path)
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}", file=sys.stderr)
        return 1

    # Create and start daemon
    try:
        daemon = AutomationDaemon(config=config)

        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            print("\n🛑 Received shutdown signal, stopping daemon...")
            daemon.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start daemon
        print("🚀 Starting InnerOS Automation Daemon...")
        print(f"📁 Config: {config_path}")
        daemon.start()

        print("✅ Daemon started successfully")
        print("💡 Press Ctrl+C to stop")

        # Keep main thread alive
        signal.pause()

    except KeyboardInterrupt:
        print("\n🛑 Interrupted, stopping daemon...")
        if daemon:
            daemon.stop()
        return 0

    except Exception as e:
        print(f"❌ Daemon failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
