"""
Systemd Service Integration Utilities - TDD Iteration 8 REFACTOR

Extracted utility classes for systemd service management:
- ServiceFileTemplate: Template management
- InstallationPathResolver: Path resolution logic
- SystemctlCommandRunner: Command generation

Follows ADR-001: <500 LOC, modular utility extraction.

Size: ~150 LOC (ADR-001 compliant: <500 LOC)
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


# Service file template constant
SERVICE_FILE_TEMPLATE = """[Unit]
Description=InnerOS Automation Daemon
Documentation=https://github.com/YOUR-USERNAME/inneros-zettelkasten
After=network.target

[Service]
Type=simple
ExecStart={daemon_path} --config {config_path}
Restart={restart_policy}
RestartSec={restart_sec}
StandardOutput=journal
StandardError=journal
SyslogIdentifier=inneros-daemon
{user_directive}
{group_directive}
WorkingDirectory={working_dir}

[Install]
WantedBy={wants_target}
"""


@dataclass
class SystemdPaths:
    """Resolved installation paths for systemd service."""

    daemon_path: str
    config_path: str
    service_path: str
    log_path: str


class ServiceFileTemplate:
    """
    Service file template management with variable substitution.

    Centralizes template logic for easy maintenance and testing.
    """

    @staticmethod
    def render(
        daemon_path: str,
        config_path: str,
        restart_policy: str,
        restart_sec: int,
        user_directive: str,
        group_directive: str,
        working_dir: str,
        wants_target: str,
    ) -> str:
        """
        Render service file from template.

        Args:
            daemon_path: Path to daemon executable
            config_path: Path to configuration file
            restart_policy: Systemd restart policy
            restart_sec: Restart delay in seconds
            user_directive: User= directive (empty for user mode)
            group_directive: Group= directive (empty for user mode)
            working_dir: Working directory for daemon
            wants_target: WantedBy target (multi-user.target or default.target)

        Returns:
            Rendered service file content
        """
        return SERVICE_FILE_TEMPLATE.format(
            daemon_path=daemon_path,
            config_path=config_path,
            restart_policy=restart_policy,
            restart_sec=restart_sec,
            user_directive=user_directive,
            group_directive=group_directive,
            working_dir=working_dir,
            wants_target=wants_target,
        )


class InstallationPathResolver:
    """Resolve installation paths for system vs user mode."""

    def __init__(
        self,
        mode: str = "system",
        custom_daemon_path: Optional[str] = None,
        custom_config_path: Optional[str] = None,
    ):
        """
        Initialize path resolver.

        Args:
            mode: 'system' or 'user' installation mode
            custom_daemon_path: Override default daemon path
            custom_config_path: Override default config path
        """
        self.mode = mode
        self.custom_daemon_path = custom_daemon_path
        self.custom_config_path = custom_config_path

    def resolve(self) -> Dict[str, str]:
        """
        Resolve all installation paths based on mode.

        Returns:
            Dictionary with daemon_path, config_path, service_path, log_path
        """
        if self.mode == "system":
            return self._resolve_system_paths()
        else:
            return self._resolve_user_paths()

    def _resolve_system_paths(self) -> Dict[str, str]:
        """Resolve paths for system mode installation."""
        return {
            "daemon_path": self.custom_daemon_path or "/usr/local/bin/inneros-daemon",
            "config_path": self.custom_config_path or "/etc/inneros/config.yaml",
            "service_path": "/etc/systemd/system/inneros-daemon.service",
            "log_path": "/var/log/inneros",
        }

    def _resolve_user_paths(self) -> Dict[str, str]:
        """Resolve paths for user mode installation."""
        home = Path.home()
        return {
            "daemon_path": self.custom_daemon_path
            or str(home / ".local/bin/inneros-daemon"),
            "config_path": self.custom_config_path
            or str(home / ".config/inneros/config.yaml"),
            "service_path": str(home / ".config/systemd/user/inneros-daemon.service"),
            "log_path": str(home / ".local/share/inneros/logs"),
        }


class SystemctlCommandRunner:
    """Generate systemctl commands for service management."""

    def __init__(self, mode: str = "system"):
        """
        Initialize systemctl command runner.

        Args:
            mode: 'system' or 'user' mode for systemctl commands
        """
        self.mode = mode
        self.user_flag = "--user" if mode == "user" else ""

    def enable_command(self, service_name: str) -> str:
        """Generate systemctl enable command."""
        return self._build_command("enable", service_name)

    def start_command(self, service_name: str) -> str:
        """Generate systemctl start command."""
        return self._build_command("start", service_name)

    def stop_command(self, service_name: str) -> str:
        """Generate systemctl stop command."""
        return self._build_command("stop", service_name)

    def daemon_reload_command(self) -> str:
        """Generate daemon-reload command."""
        return f"systemctl {self.user_flag} daemon-reload".strip()

    def status_command(self, service_name: str) -> str:
        """Generate systemctl status command."""
        return self._build_command("status", service_name)

    def _build_command(self, action: str, service_name: str) -> str:
        """Build systemctl command with consistent formatting."""
        return f"systemctl {self.user_flag} {action} {service_name}".strip()
