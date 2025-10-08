#!/usr/bin/env python3
"""
Daemon Installation Script - TDD Iteration 8

Installs InnerOS Automation Daemon as systemd service.
Supports both user mode (no root required) and system mode installations.

Usage:
    # User mode (recommended for single-user setups)
    python3 install_daemon.py --user
    
    # System mode (requires root, for multi-user servers)
    sudo python3 install_daemon.py --system --user inneros

ADR-001 compliant: <500 LOC
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from automation.systemd_integration import (
    SystemdServiceGenerator,
    HealthCheckScriptGenerator,
    ServiceInstaller
)
from automation.systemd_utils import (
    InstallationPathResolver,
    SystemctlCommandRunner
)


def print_banner():
    """Print installation banner."""
    print("=" * 70)
    print("  InnerOS Automation Daemon - Systemd Service Installation")
    print("=" * 70)
    print()


def validate_environment(mode: str) -> bool:
    """
    Validate installation environment.
    
    Args:
        mode: 'system' or 'user'
    
    Returns:
        True if environment is valid
    """
    # Check if running as root for system mode
    if mode == "system" and os.geteuid() != 0:
        print("❌ System mode installation requires root privileges")
        print("   Run with: sudo python3 install_daemon.py --system")
        return False
    
    # Check if systemd is available
    if not Path("/usr/bin/systemctl").exists():
        print("❌ systemd not found - this system doesn't use systemd")
        return False
    
    return True


def main():
    """Main installation orchestrator."""
    print_banner()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Install InnerOS Automation Daemon as systemd service"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--user",
        action="store_true",
        help="Install in user mode (no root required, recommended)"
    )
    group.add_argument(
        "--system",
        action="store_true",
        help="Install in system mode (requires root)"
    )
    
    parser.add_argument(
        "--user-name",
        type=str,
        default=None,
        help="User to run daemon as (system mode only)"
    )
    
    parser.add_argument(
        "--daemon-path",
        type=str,
        default=None,
        help="Override daemon executable path"
    )
    
    parser.add_argument(
        "--config-path",
        type=str,
        default=None,
        help="Override configuration file path"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show installation plan without executing"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    mode = "system" if args.system else "user"
    
    print(f"📦 Installation Mode: {mode.upper()}")
    if args.dry_run:
        print("   (Dry run - no changes will be made)")
    print()
    
    # Validate environment
    if not validate_environment(mode):
        return 1
    
    # Resolve installation paths
    resolver = InstallationPathResolver(
        mode=mode,
        custom_daemon_path=args.daemon_path,
        custom_config_path=args.config_path
    )
    paths = resolver.resolve()
    
    print("📁 Installation Paths:")
    print(f"   Daemon:  {paths['daemon_path']}")
    print(f"   Config:  {paths['config_path']}")
    print(f"   Service: {paths['service_path']}")
    print(f"   Logs:    {paths['log_path']}")
    print()
    
    # Check if paths exist
    daemon_path = Path(paths['daemon_path'])
    config_path = Path(paths['config_path'])
    
    if not args.dry_run:
        if not daemon_path.exists():
            print(f"❌ Daemon executable not found: {daemon_path}")
            print("   Create daemon entry point first")
            return 1
        
        if not config_path.exists():
            print(f"⚠️  Config file not found: {config_path}")
            print("   Creating example configuration...")
            
            # Create config directory
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write example config
            example_config = """# InnerOS Automation Daemon Configuration
daemon:
  check_interval: 60
  log_level: INFO

# File watching configuration
file_watching:
  enabled: true
  watch_path: ~/knowledge/Inbox
  debounce_seconds: 2.0
  ignore_patterns:
    - "*.tmp"
    - ".git/*"

# Screenshot handler (optional)
screenshot_handler:
  enabled: false
  onedrive_path: ~/OneDrive/Screenshots
  knowledge_path: ~/knowledge/Media/Pasted Images

# Smart link handler (optional)
smart_link_handler:
  enabled: false
  vault_path: ~/knowledge
  similarity_threshold: 0.75
"""
            config_path.write_text(example_config)
            print(f"   ✅ Created: {config_path}")
            print()
    
    # Install service
    print("🚀 Installing systemd service...")
    
    installer = ServiceInstaller(
        mode=mode,
        dry_run=args.dry_run
    )
    
    result = installer.install(
        daemon_path=str(daemon_path),
        config_path=str(config_path),
        user=args.user_name
    )
    
    if not result["success"]:
        print(f"❌ Installation failed: {result.get('error', 'Unknown error')}")
        return 1
    
    # Print installation steps
    print("\n📋 Installation Steps:")
    for step in result["steps"]:
        print(f"   {step}")
    print()
    
    if args.dry_run:
        print("✅ Dry run complete - no changes were made")
        print("\nRun without --dry-run to perform actual installation")
        return 0
    
    # Generate systemctl commands
    runner = SystemctlCommandRunner(mode=mode)
    
    print("🎯 Next Steps:")
    print(f"   1. Reload systemd: {runner.daemon_reload_command()}")
    print(f"   2. Enable service: {runner.enable_command('inneros-daemon')}")
    print(f"   3. Start service:  {runner.start_command('inneros-daemon')}")
    print(f"   4. Check status:   {runner.status_command('inneros-daemon')}")
    print()
    
    # Offer to run commands automatically
    try:
        response = input("Would you like to run these commands now? [y/N]: ")
        if response.lower() == 'y':
            import subprocess
            
            print("\n🔄 Executing systemctl commands...")
            
            # Daemon reload
            cmd = runner.daemon_reload_command().split()
            subprocess.run(cmd, check=True)
            print("   ✅ Reloaded systemd")
            
            # Enable service
            cmd = runner.enable_command('inneros-daemon').split()
            subprocess.run(cmd, check=True)
            print("   ✅ Enabled inneros-daemon")
            
            # Start service
            cmd = runner.start_command('inneros-daemon').split()
            subprocess.run(cmd, check=True)
            print("   ✅ Started inneros-daemon")
            
            print("\n🎉 Installation complete! Daemon is now running.")
            print(f"   View status: {runner.status_command('inneros-daemon')}")
            print(f"   View logs:   journalctl {runner.user_flag} -u inneros-daemon -f".strip())
            
        else:
            print("✅ Service installed. Run the commands above to start the daemon.")
    
    except KeyboardInterrupt:
        print("\n\n✅ Service installed. Run the commands above to start the daemon.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
