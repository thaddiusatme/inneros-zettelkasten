"""
TDD RED Phase: Automation Status CLI Tests
Tests automation visibility, daemon detection, log parsing, and daemon control.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.cli.automation_status_cli import (
    AutomationStatusCLI,
    DaemonDetector,
    LogParser,
    DaemonRegistry,
    StatusFormatter,
)


@pytest.fixture
def mock_daemon_registry(tmp_path):
    """Mock daemon registry configuration."""
    registry_path = tmp_path / "daemon_registry.yaml"
    registry_content = """
daemons:
  - name: youtube_watcher
    script_path: .automation/scripts/automated_screenshot_import.sh
    log_path: .automation/logs/youtube_watcher.log
    pid_file: .automation/logs/youtube_watcher.pid
    description: Monitors YouTube content for processing
  
  - name: screenshot_processor
    script_path: .automation/scripts/process_screenshots.py
    log_path: .automation/logs/screenshot_processor.log
    pid_file: .automation/logs/screenshot_processor.pid
    description: Processes Samsung screenshot imports
  
  - name: health_monitor
    script_path: .automation/scripts/health_monitor.py
    log_path: .automation/logs/health_monitor.log
    pid_file: .automation/logs/health_monitor.pid
    description: System health monitoring daemon
"""
    registry_path.write_text(registry_content)
    return registry_path


@pytest.fixture
def mock_log_file(tmp_path):
    """Mock daemon log file with recent entries."""
    log_path = tmp_path / "youtube_watcher.log"
    log_content = """
2025-10-23 19:00:00 - INFO - YouTube watcher daemon started
2025-10-23 19:05:00 - INFO - Processing 3 new videos
2025-10-23 19:05:15 - SUCCESS - Processed 3 videos successfully
2025-10-23 19:05:15 - INFO - Execution completed in 15.3 seconds
"""
    log_path.write_text(log_content)
    return log_path


class TestDaemonDetector:
    """Test daemon process detection."""

    def test_detects_running_daemon_by_name(self):
        """Should detect running daemon by process name."""
        with patch('psutil.process_iter') as mock_process_iter:
            # Mock a running process
            mock_process = Mock()
            mock_process.info = {
                'pid': 12345,
                'name': 'python3',
                'cmdline': ['/usr/bin/python3', '.automation/scripts/automated_screenshot_import.sh']
            }
            mock_process_iter.return_value = [mock_process]

            detector = DaemonDetector()
            status = detector.check_daemon_status('youtube_watcher', '.automation/scripts/automated_screenshot_import.sh')

            assert status['running'] is True
            assert status['pid'] == 12345

    def test_detects_stopped_daemon(self):
        """Should detect when daemon is not running."""
        with patch('psutil.process_iter') as mock_process_iter:
            mock_process_iter.return_value = []

            detector = DaemonDetector()
            status = detector.check_daemon_status('youtube_watcher', '.automation/scripts/automated_screenshot_import.sh')

            assert status['running'] is False
            assert status['pid'] is None

    def test_handles_multiple_daemons(self):
        """Should check status of multiple daemons."""
        with patch('psutil.process_iter') as mock_process_iter:
            # Mock two running processes
            mock_proc1 = Mock()
            mock_proc1.info = {
                'pid': 12345,
                'name': 'python3',
                'cmdline': ['/usr/bin/python3', '.automation/scripts/automated_screenshot_import.sh']
            }
            mock_proc2 = Mock()
            mock_proc2.info = {
                'pid': 12346,
                'name': 'python3',
                'cmdline': ['/usr/bin/python3', '.automation/scripts/health_monitor.py']
            }
            mock_process_iter.return_value = [mock_proc1, mock_proc2]

            detector = DaemonDetector()
            statuses = detector.check_all_daemons([
                ('youtube_watcher', '.automation/scripts/automated_screenshot_import.sh'),
                ('health_monitor', '.automation/scripts/health_monitor.py'),
            ])

            assert len(statuses) == 2
            assert statuses[0]['running'] is True
            assert statuses[1]['running'] is True


class TestLogParser:
    """Test log file parsing."""

    def test_parses_last_run_from_log(self, mock_log_file):
        """Should parse last execution details from log file."""
        parser = LogParser()
        last_run = parser.parse_last_run(mock_log_file)

        assert last_run['status'] == 'success'
        assert '19:05:15' in last_run['timestamp']
        assert last_run['duration'] == '15.3 seconds'

    def test_handles_failed_execution(self, tmp_path):
        """Should detect failed executions."""
        log_path = tmp_path / "failed.log"
        log_content = """
2025-10-23 19:00:00 - INFO - Starting processing
2025-10-23 19:00:05 - ERROR - Failed to connect to API
2025-10-23 19:00:05 - FAILED - Execution failed
"""
        log_path.write_text(log_content)

        parser = LogParser()
        last_run = parser.parse_last_run(log_path)

        assert last_run['status'] == 'failed'
        assert 'Failed to connect to API' in last_run['error_message']

    def test_handles_missing_log_file(self, tmp_path):
        """Should handle missing log file gracefully."""
        parser = LogParser()
        last_run = parser.parse_last_run(tmp_path / "nonexistent.log")

        assert last_run['status'] == 'unknown'
        assert last_run['error_message'] == 'No log file found'

    def test_gets_log_tail(self, mock_log_file):
        """Should retrieve last N lines from log."""
        parser = LogParser()
        tail_lines = parser.get_log_tail(mock_log_file, lines=2)

        assert len(tail_lines) == 2
        assert 'SUCCESS' in tail_lines[0]
        assert 'Execution completed' in tail_lines[1]


class TestDaemonRegistry:
    """Test daemon registry configuration."""

    def test_loads_daemon_registry(self, mock_daemon_registry):
        """Should load daemon configurations from YAML."""
        registry = DaemonRegistry(mock_daemon_registry)
        daemons = registry.get_all_daemons()

        assert len(daemons) == 3
        assert daemons[0]['name'] == 'youtube_watcher'
        assert daemons[1]['name'] == 'screenshot_processor'
        assert daemons[2]['name'] == 'health_monitor'

    def test_gets_daemon_by_name(self, mock_daemon_registry):
        """Should retrieve specific daemon configuration."""
        registry = DaemonRegistry(mock_daemon_registry)
        daemon = registry.get_daemon('youtube_watcher')

        assert daemon['name'] == 'youtube_watcher'
        assert '.automation/scripts/automated_screenshot_import.sh' in daemon['script_path']
        assert daemon['description'] == 'Monitors YouTube content for processing'

    def test_validates_daemon_config(self, tmp_path):
        """Should validate required daemon configuration fields."""
        invalid_registry = tmp_path / "invalid_registry.yaml"
        invalid_content = """
daemons:
  - name: incomplete_daemon
    # Missing required fields
"""
        invalid_registry.write_text(invalid_content)

        with pytest.raises(ValueError, match="Missing required fields"):
            registry = DaemonRegistry(invalid_registry)
            registry.validate()


class TestStatusFormatter:
    """Test status output formatting."""

    def test_formats_running_daemon_status(self):
        """Should format running daemon with green indicator."""
        formatter = StatusFormatter()
        status = {
            'name': 'youtube_watcher',
            'running': True,
            'pid': 12345,
            'last_run': {'status': 'success', 'timestamp': '2025-10-23 19:05:15'}
        }

        output = formatter.format_daemon_status(status)

        assert '🟢' in output
        assert 'youtube_watcher' in output
        assert 'PID: 12345' in output
        assert 'success' in output.lower()

    def test_formats_stopped_daemon_status(self):
        """Should format stopped daemon with red indicator."""
        formatter = StatusFormatter()
        status = {
            'name': 'youtube_watcher',
            'running': False,
            'pid': None,
            'last_run': {'status': 'unknown'}
        }

        output = formatter.format_daemon_status(status)

        assert '🔴' in output
        assert 'youtube_watcher' in output
        assert 'stopped' in output.lower()

    def test_formats_all_daemons_summary(self):
        """Should format summary of all daemon statuses."""
        formatter = StatusFormatter()
        statuses = [
            {'name': 'youtube_watcher', 'running': True, 'pid': 12345},
            {'name': 'screenshot_processor', 'running': False, 'pid': None},
            {'name': 'health_monitor', 'running': True, 'pid': 12346},
        ]

        output = formatter.format_summary(statuses)

        assert '2/3 daemons running' in output
        assert '🟢' in output
        assert '🔴' in output


class TestAutomationStatusCLI:
    """Test main CLI interface."""

    def test_status_command_shows_all_daemons(self, mock_daemon_registry, tmp_path):
        """Should display status of all registered daemons."""
        cli = AutomationStatusCLI(registry_path=mock_daemon_registry, workspace_root=tmp_path)

        with patch('psutil.process_iter') as mock_process_iter:
            mock_process = Mock()
            mock_process.info = {
                'pid': 12345,
                'name': 'python3',
                'cmdline': ['/usr/bin/python3', '.automation/scripts/automated_screenshot_import.sh']
            }
            mock_process_iter.return_value = [mock_process]

            result = cli.status()

            assert result['total_daemons'] == 3
            assert result['running_daemons'] == 1
            assert len(result['daemon_statuses']) == 3

    def test_last_run_command_shows_execution_details(self, mock_daemon_registry, mock_log_file, tmp_path):
        """Should display last execution details for specific daemon."""
        cli = AutomationStatusCLI(registry_path=mock_daemon_registry, workspace_root=tmp_path)

        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_log_file.read_text())):
                result = cli.last_run('youtube_watcher')

                assert result['daemon'] == 'youtube_watcher'
                assert result['status'] == 'success'
                assert 'timestamp' in result

    def test_logs_command_displays_tail(self, mock_daemon_registry, mock_log_file, tmp_path):
        """Should display last N lines of daemon log."""
        cli = AutomationStatusCLI(registry_path=mock_daemon_registry, workspace_root=tmp_path)

        with patch.object(Path, 'exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_log_file.read_text())):
                result = cli.logs('youtube_watcher', lines=3)

                assert result['daemon'] == 'youtube_watcher'
                assert len(result['log_lines']) <= 3

    def test_handles_invalid_daemon_name(self, mock_daemon_registry, tmp_path):
        """Should handle requests for non-existent daemon."""
        cli = AutomationStatusCLI(registry_path=mock_daemon_registry, workspace_root=tmp_path)

        with pytest.raises(ValueError, match="Unknown daemon"):
            cli.last_run('nonexistent_daemon')

    def test_performance_within_5_seconds(self, mock_daemon_registry, tmp_path):
        """Should complete status check within 5 seconds."""
        import time

        cli = AutomationStatusCLI(registry_path=mock_daemon_registry, workspace_root=tmp_path)

        with patch('psutil.process_iter') as mock_process_iter:
            mock_process_iter.return_value = []

            start_time = time.time()
            cli.status()
            duration = time.time() - start_time

            assert duration < 5.0, f"Status check took {duration}s, expected <5s"
