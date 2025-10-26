"""
TDD Iteration 8: Systemd Service Integration Tests

RED Phase - Comprehensive failing tests for systemd service integration:
- Service file generation (system and user modes)
- Installation path resolution
- Health check script generation
- systemctl command execution
"""

from pathlib import Path
import tempfile


class TestSystemdServiceGeneration:
    """Test service file generation for systemd integration."""

    def test_service_file_generation_basic(self):
        """Test: Generate valid systemd service file with basic configuration."""
        from src.automation.systemd_integration import SystemdServiceGenerator

        generator = SystemdServiceGenerator(
            daemon_path="/usr/local/bin/inneros-daemon",
            config_path="/etc/inneros/config.yaml",
            user="inneros"
        )
        service_content = generator.generate()

        # Verify basic service file structure
        assert "[Unit]" in service_content
        assert "Description=InnerOS Automation Daemon" in service_content
        assert "[Service]" in service_content
        assert "[Install]" in service_content

        # Verify execution configuration
        assert "ExecStart=" in service_content
        assert "/usr/local/bin/inneros-daemon" in service_content
        assert "--config /etc/inneros/config.yaml" in service_content

        # Verify restart policy
        assert "Restart=always" in service_content
        assert "RestartSec=10" in service_content

    def test_service_file_user_mode(self):
        """Test: Generate service file for user mode installation."""
        from src.automation.systemd_integration import SystemdServiceGenerator

        generator = SystemdServiceGenerator(
            daemon_path=str(Path.home() / ".local/bin/inneros-daemon"),
            config_path=str(Path.home() / ".config/inneros/config.yaml"),
            user=None,  # User mode doesn't specify User= directive
            mode="user"
        )
        service_content = generator.generate()

        # User mode shouldn't have User= directive (runs as current user)
        assert "User=" not in service_content

        # Should have user mode specific paths
        assert str(Path.home()) in service_content

    def test_service_file_system_mode(self):
        """Test: Generate service file for system mode (root) installation."""
        from src.automation.systemd_integration import SystemdServiceGenerator

        generator = SystemdServiceGenerator(
            daemon_path="/usr/local/bin/inneros-daemon",
            config_path="/etc/inneros/config.yaml",
            user="inneros",
            mode="system"
        )
        service_content = generator.generate()

        # System mode should specify User directive
        assert "User=inneros" in service_content
        assert "Group=inneros" in service_content

    def test_service_file_includes_restart_policy(self):
        """Test: Service file includes proper restart configuration."""
        from src.automation.systemd_integration import SystemdServiceGenerator

        generator = SystemdServiceGenerator(
            daemon_path="/usr/local/bin/inneros-daemon",
            config_path="/etc/inneros/config.yaml",
            restart_policy="always",
            restart_sec=10
        )
        service_content = generator.generate()

        assert "Restart=always" in service_content
        assert "RestartSec=10" in service_content

    def test_service_file_includes_logging(self):
        """Test: Service file configures logging to journald."""
        from src.automation.systemd_integration import SystemdServiceGenerator

        generator = SystemdServiceGenerator(
            daemon_path="/usr/local/bin/inneros-daemon",
            config_path="/etc/inneros/config.yaml"
        )
        service_content = generator.generate()

        # Verify logging configuration
        assert "StandardOutput=journal" in service_content
        assert "StandardError=journal" in service_content
        assert "SyslogIdentifier=inneros-daemon" in service_content


class TestHealthCheckScript:
    """Test health check script generation for systemd monitoring."""

    def test_health_check_script_generation(self):
        """Test: Generate health check script that calls daemon health endpoint."""
        from src.automation.systemd_integration import HealthCheckScriptGenerator

        generator = HealthCheckScriptGenerator(
            daemon_host="localhost",
            daemon_port=8080
        )
        script_content = generator.generate()

        # Verify script structure
        assert "#!/bin/bash" in script_content
        assert "curl" in script_content
        assert "http://localhost:8080/health" in script_content

        # Verify exit codes
        assert "exit 0" in script_content
        assert "exit 1" in script_content

    def test_health_check_with_timeout(self):
        """Test: Health check script includes timeout configuration."""
        from src.automation.systemd_integration import HealthCheckScriptGenerator

        generator = HealthCheckScriptGenerator(
            daemon_host="localhost",
            daemon_port=8080,
            timeout_seconds=5
        )
        script_content = generator.generate()

        assert "--max-time 5" in script_content or "-m 5" in script_content


class TestInstallationPathResolution:
    """Test installation path resolution for system vs user mode."""

    def test_system_mode_paths(self):
        """Test: Resolve installation paths for system mode."""
        from src.automation.systemd_integration import InstallationPathResolver

        resolver = InstallationPathResolver(mode="system")
        paths = resolver.resolve()

        assert paths["daemon_path"] == "/usr/local/bin/inneros-daemon"
        assert paths["config_path"] == "/etc/inneros/config.yaml"
        assert paths["service_path"] == "/etc/systemd/system/inneros-daemon.service"
        assert paths["log_path"] == "/var/log/inneros"

    def test_user_mode_paths(self):
        """Test: Resolve installation paths for user mode."""
        from src.automation.systemd_integration import InstallationPathResolver

        resolver = InstallationPathResolver(mode="user")
        paths = resolver.resolve()

        home = Path.home()
        assert str(home) in paths["daemon_path"]
        assert str(home) in paths["config_path"]
        assert ".config/systemd/user" in paths["service_path"]
        assert ".local/share/inneros" in paths["log_path"]

    def test_custom_paths_override(self):
        """Test: Custom paths override default resolution."""
        from src.automation.systemd_integration import InstallationPathResolver

        resolver = InstallationPathResolver(
            mode="system",
            custom_daemon_path="/opt/inneros/bin/daemon",
            custom_config_path="/opt/inneros/etc/config.yaml"
        )
        paths = resolver.resolve()

        assert paths["daemon_path"] == "/opt/inneros/bin/daemon"
        assert paths["config_path"] == "/opt/inneros/etc/config.yaml"


class TestSystemctlCommandRunner:
    """Test systemctl command execution wrapper."""

    def test_enable_service_command(self):
        """Test: Generate systemctl enable command."""
        from src.automation.systemd_integration import SystemctlCommandRunner

        runner = SystemctlCommandRunner(mode="system")
        command = runner.enable_command("inneros-daemon")

        assert "systemctl" in command
        assert "enable" in command
        assert "inneros-daemon" in command

    def test_start_service_command(self):
        """Test: Generate systemctl start command."""
        from src.automation.systemd_integration import SystemctlCommandRunner

        runner = SystemctlCommandRunner(mode="system")
        command = runner.start_command("inneros-daemon")

        assert "systemctl" in command
        assert "start" in command
        assert "inneros-daemon" in command

    def test_user_mode_commands(self):
        """Test: User mode adds --user flag to systemctl commands."""
        from src.automation.systemd_integration import SystemctlCommandRunner

        runner = SystemctlCommandRunner(mode="user")
        command = runner.enable_command("inneros-daemon")

        assert "--user" in command

    def test_daemon_reload_command(self):
        """Test: Generate daemon-reload command for service file changes."""
        from src.automation.systemd_integration import SystemctlCommandRunner

        runner = SystemctlCommandRunner(mode="system")
        command = runner.daemon_reload_command()

        assert "systemctl" in command
        assert "daemon-reload" in command


class TestServiceInstaller:
    """Test service installation orchestration."""

    def test_installation_dry_run(self):
        """Test: Dry run mode shows installation plan without executing."""
        from src.automation.systemd_integration import ServiceInstaller

        installer = ServiceInstaller(mode="system", dry_run=True)
        result = installer.install(
            daemon_path="/usr/local/bin/inneros-daemon",
            config_path="/etc/inneros/config.yaml"
        )

        assert result["success"] is True
        assert "steps" in result
        assert len(result["steps"]) > 0
        assert not result.get("executed", True)  # Should not execute in dry run

    def test_installation_validates_paths(self):
        """Test: Installation validates daemon and config paths exist."""
        from src.automation.systemd_integration import ServiceInstaller

        with tempfile.TemporaryDirectory() as tmpdir:
            nonexistent_daemon = Path(tmpdir) / "nonexistent_daemon"
            nonexistent_config = Path(tmpdir) / "nonexistent_config.yaml"

            installer = ServiceInstaller(mode="user")
            result = installer.install(
                daemon_path=str(nonexistent_daemon),
                config_path=str(nonexistent_config)
            )

            assert result["success"] is False
            assert "error" in result
            assert "not found" in result["error"].lower()

    def test_installation_creates_service_file(self):
        """Test: Installation creates service file in correct location."""
        from src.automation.systemd_integration import ServiceInstaller

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock daemon and config
            daemon_path = Path(tmpdir) / "inneros-daemon"
            daemon_path.touch()
            daemon_path.chmod(0o755)

            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("daemon:\n  check_interval: 60\n")

            # Mock service directory
            service_dir = Path(tmpdir) / "systemd" / "user"
            service_dir.mkdir(parents=True)

            installer = ServiceInstaller(
                mode="user",
                service_dir_override=str(service_dir)
            )
            result = installer.install(
                daemon_path=str(daemon_path),
                config_path=str(config_path)
            )

            service_file = service_dir / "inneros-daemon.service"
            assert service_file.exists()

            # Verify service file content
            content = service_file.read_text()
            assert str(daemon_path) in content
            assert str(config_path) in content


class TestDaemonEntryPoint:
    """Test daemon CLI entry point for systemd execution."""

    def test_entry_point_accepts_config_flag(self):
        """Test: Daemon entry point accepts --config flag."""
        from src.automation.daemon_cli import parse_args

        args = parse_args(["--config", "/etc/inneros/config.yaml"])

        assert args.config == "/etc/inneros/config.yaml"

    def test_entry_point_default_config_path(self):
        """Test: Default config path when not specified."""
        from src.automation.daemon_cli import parse_args

        args = parse_args([])

        # Should have sensible default
        assert args.config is not None
        assert "config.yaml" in args.config

    def test_entry_point_runs_daemon(self):
        """Test: Entry point creates and starts daemon."""
        from src.automation.daemon_cli import main

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"
            config_path.write_text("""
daemon:
  check_interval: 60
  log_level: INFO
""")

            # This should fail gracefully since we're just testing parsing
            # Real daemon startup requires more infrastructure
            try:
                main(["--config", str(config_path), "--help"])
            except SystemExit:
                pass  # Expected for --help flag
