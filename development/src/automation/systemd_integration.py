"""
Systemd Service Integration - TDD Iteration 8

Generates systemd service files and manages installation for production deployment.
Follows ADR-001: <500 LOC, single responsibility, domain separation.

Key Components:
- SystemdServiceGenerator: Creates .service files
- HealthCheckScriptGenerator: Creates health monitoring scripts
- ServiceInstaller: Orchestrates full installation process

Utilities extracted to systemd_utils.py:
- ServiceFileTemplate: Template rendering
- InstallationPathResolver: Path resolution
- SystemctlCommandRunner: Command generation

Size: ~250 LOC (ADR-001 compliant: <500 LOC)
"""

from pathlib import Path
from typing import Dict, Optional

from .systemd_utils import (
    ServiceFileTemplate,
    InstallationPathResolver,
    SystemctlCommandRunner
)


class SystemdServiceGenerator:
    """
    Generate systemd service files for production deployment.
    
    Supports both system mode (requires root) and user mode installations.
    """

    def __init__(
        self,
        daemon_path: str,
        config_path: str,
        user: Optional[str] = None,
        mode: str = "system",
        restart_policy: str = "always",
        restart_sec: int = 10
    ):
        """
        Initialize service file generator.
        
        Args:
            daemon_path: Path to daemon executable
            config_path: Path to configuration file
            user: User to run service as (system mode only)
            mode: 'system' or 'user' installation mode
            restart_policy: Systemd restart policy (always, on-failure, etc.)
            restart_sec: Seconds to wait before restart
        """
        self.daemon_path = daemon_path
        self.config_path = config_path
        self.user = user
        self.mode = mode
        self.restart_policy = restart_policy
        self.restart_sec = restart_sec

    def generate(self) -> str:
        """
        Generate systemd service file content.
        
        Returns:
            String containing complete .service file
        """
        # Determine user/group directives based on mode
        if self.mode == "system" and self.user:
            user_directive = f"User={self.user}"
            group_directive = f"Group={self.user}"
        else:
            user_directive = ""
            group_directive = ""

        # Determine working directory
        if self.mode == "user":
            working_dir = str(Path.home())
        else:
            working_dir = "/var/lib/inneros"

        # Determine WantedBy target
        wants_target = "default.target" if self.mode == "user" else "multi-user.target"

        # Generate service file using extracted template utility
        service_content = ServiceFileTemplate.render(
            daemon_path=self.daemon_path,
            config_path=self.config_path,
            restart_policy=self.restart_policy,
            restart_sec=self.restart_sec,
            user_directive=user_directive,
            group_directive=group_directive,
            working_dir=working_dir,
            wants_target=wants_target
        )

        return service_content


class HealthCheckScriptGenerator:
    """Generate health check scripts for systemd monitoring."""

    def __init__(
        self,
        daemon_host: str = "localhost",
        daemon_port: int = 8080,
        timeout_seconds: int = 5
    ):
        """
        Initialize health check script generator.
        
        Args:
            daemon_host: Host where daemon is running
            daemon_port: Port for health endpoint
            timeout_seconds: HTTP request timeout
        """
        self.daemon_host = daemon_host
        self.daemon_port = daemon_port
        self.timeout_seconds = timeout_seconds

    def generate(self) -> str:
        """
        Generate health check script content.
        
        Returns:
            Bash script that checks daemon health via HTTP endpoint
        """
        script = f"""#!/bin/bash
# InnerOS Daemon Health Check Script
# Used by systemd for monitoring daemon status

HEALTH_URL="http://{self.daemon_host}:{self.daemon_port}/health"
TIMEOUT={self.timeout_seconds}

# Query health endpoint with timeout
response=$(curl --silent --fail --max-time {self.timeout_seconds} "$HEALTH_URL" 2>/dev/null)
exit_code=$?

if [ $exit_code -eq 0 ]; then
    # Check if response indicates healthy status
    if echo "$response" | grep -q '"is_healthy":true'; then
        exit 0
    else
        echo "Daemon responded but reports unhealthy status"
        exit 1
    fi
else
    echo "Failed to connect to daemon health endpoint"
    exit 1
fi
"""
        return script


class ServiceInstaller:
    """
    Orchestrate service installation process.
    
    Handles service file generation, path validation, and installation.
    """

    def __init__(
        self,
        mode: str = "system",
        dry_run: bool = False,
        service_dir_override: Optional[str] = None
    ):
        """
        Initialize service installer.
        
        Args:
            mode: 'system' or 'user' installation mode
            dry_run: If True, show plan without executing
            service_dir_override: Override service directory (for testing)
        """
        self.mode = mode
        self.dry_run = dry_run
        self.service_dir_override = service_dir_override

    def install(
        self,
        daemon_path: str,
        config_path: str,
        user: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Install systemd service.
        
        Args:
            daemon_path: Path to daemon executable
            config_path: Path to configuration file
            user: User to run service as (system mode only)
        
        Returns:
            Dictionary with installation result and steps
        """
        result = {"success": False, "steps": [], "executed": not self.dry_run}

        # Validate paths exist (skip in dry-run mode)
        if not self.dry_run:
            daemon_path_obj = Path(daemon_path)
            config_path_obj = Path(config_path)

            if not daemon_path_obj.exists():
                result["error"] = f"Daemon path not found: {daemon_path}"
                return result

            if not config_path_obj.exists():
                result["error"] = f"Config path not found: {config_path}"
                return result

        # Resolve installation paths
        resolver = InstallationPathResolver(mode=self.mode)
        paths = resolver.resolve()

        # Generate service file
        generator = SystemdServiceGenerator(
            daemon_path=daemon_path,
            config_path=config_path,
            user=user,
            mode=self.mode
        )
        service_content = generator.generate()

        # Determine service file location
        if self.service_dir_override:
            service_path = Path(self.service_dir_override) / "inneros-daemon.service"
        else:
            service_path = Path(paths["service_path"])

        result["steps"].append(f"Generate service file: {service_path}")
        result["steps"].append(f"Service content: {len(service_content)} bytes")

        if not self.dry_run:
            # Create service directory if needed
            service_path.parent.mkdir(parents=True, exist_ok=True)

            # Write service file
            service_path.write_text(service_content)
            result["steps"].append(f"Created service file: {service_path}")

            # Generate systemctl commands
            runner = SystemctlCommandRunner(mode=self.mode)
            result["steps"].append(f"Next: {runner.daemon_reload_command()}")
            result["steps"].append(f"Next: {runner.enable_command('inneros-daemon')}")
            result["steps"].append(f"Next: {runner.start_command('inneros-daemon')}")

        result["success"] = True
        return result
