#!/usr/bin/env python3
"""
RED PHASE: Failing tests for YouTube production monitoring and safety features

Tests for:
- MonitoringCounters: Initialize, increment, persist metrics
- Status backup: Create timestamped backups before apply operations
- Health endpoint: Simple health check for service mode
"""

import json
from datetime import datetime


class TestMonitoringCounters:
    """Test MonitoringCounters class for production metrics tracking"""

    def test_initializes_zeroed_counters(self):
        """Test that MonitoringCounters initializes with zero values"""
        # This should fail - MonitoringCounters doesn't exist yet
        from src.automation.youtube_monitoring import MonitoringCounters

        counters = MonitoringCounters()

        assert counters.total_processed == 0
        assert counters.successful == 0
        assert counters.failed == 0
        assert counters.skipped == 0

    def test_increments_success_counter(self):
        """Test incrementing success counter"""
        from src.automation.youtube_monitoring import MonitoringCounters

        counters = MonitoringCounters()
        counters.increment_success()

        assert counters.successful == 1
        assert counters.total_processed == 1

    def test_increments_failure_counter(self):
        """Test incrementing failure counter"""
        from src.automation.youtube_monitoring import MonitoringCounters

        counters = MonitoringCounters()
        counters.increment_failure()

        assert counters.failed == 1
        assert counters.total_processed == 1

    def test_increments_skipped_counter(self):
        """Test incrementing skipped counter"""
        from src.automation.youtube_monitoring import MonitoringCounters

        counters = MonitoringCounters()
        counters.increment_skipped()

        assert counters.skipped == 1
        assert counters.total_processed == 1

    def test_writes_metrics_json(self, tmp_path):
        """Test persisting metrics to JSON file"""
        from src.automation.youtube_monitoring import MonitoringCounters

        counters = MonitoringCounters()
        counters.increment_success()
        counters.increment_success()
        counters.increment_failure()

        metrics_file = tmp_path / "metrics.json"
        counters.write_metrics(metrics_file)

        assert metrics_file.exists()
        with open(metrics_file) as f:
            data = json.load(f)

        assert data['total_processed'] == 3
        assert data['successful'] == 2
        assert data['failed'] == 1
        assert data['skipped'] == 0
        assert 'timestamp' in data

    def test_metrics_json_has_timestamp(self, tmp_path):
        """Test that metrics JSON includes ISO timestamp"""
        from src.automation.youtube_monitoring import MonitoringCounters

        counters = MonitoringCounters()
        metrics_file = tmp_path / "metrics.json"
        counters.write_metrics(metrics_file)

        with open(metrics_file) as f:
            data = json.load(f)

        # Verify timestamp is valid ISO format
        timestamp = datetime.fromisoformat(data['timestamp'])
        assert isinstance(timestamp, datetime)


class TestStatusBackup:
    """Test status backup functionality before apply operations"""

    def test_creates_timestamped_backup(self, tmp_path):
        """Test creating timestamped backup of status store"""
        # This should fail - backup_status_store doesn't exist yet
        from src.automation.youtube_monitoring import backup_status_store

        status_file = tmp_path / "youtube_status.json"
        status_file.write_text('{"test": "data"}')
        backup_dir = tmp_path / "backups"

        backup_path = backup_status_store(status_file, backup_dir)

        assert backup_path.exists()
        assert backup_path.parent == backup_dir
        # Verify timestamped format: status_YYYYMMDDHHMMSS.json
        assert backup_path.stem.startswith('status_')
        assert len(backup_path.stem) == len('status_YYYYMMDDHHMMSS')

    def test_backup_preserves_content(self, tmp_path):
        """Test that backup contains exact copy of status store"""
        from src.automation.youtube_monitoring import backup_status_store

        status_file = tmp_path / "youtube_status.json"
        test_data = {"videos": ["abc123"], "last_run": "2025-01-01T00:00:00"}
        status_file.write_text(json.dumps(test_data))
        backup_dir = tmp_path / "backups"

        backup_path = backup_status_store(status_file, backup_dir)

        with open(backup_path) as f:
            backed_up = json.load(f)

        assert backed_up == test_data

    def test_backup_creates_directory_if_missing(self, tmp_path):
        """Test that backup creates backup directory if it doesn't exist"""
        from src.automation.youtube_monitoring import backup_status_store

        status_file = tmp_path / "youtube_status.json"
        status_file.write_text('{"test": "data"}')
        backup_dir = tmp_path / "backups" / "nested"  # Doesn't exist

        backup_path = backup_status_store(status_file, backup_dir)

        assert backup_dir.exists()
        assert backup_path.exists()

    def test_backup_handles_missing_status_file(self, tmp_path):
        """Test graceful handling when status file doesn't exist"""
        from src.automation.youtube_monitoring import backup_status_store

        status_file = tmp_path / "nonexistent.json"
        backup_dir = tmp_path / "backups"

        # Should return None or raise specific exception
        result = backup_status_store(status_file, backup_dir)

        assert result is None or not result.exists()


class TestHealthEndpoint:
    """Test simple health check endpoint for service mode"""

    def test_health_check_returns_ok(self, tmp_path):
        """Test health check returns 200 with last run summary"""
        # This should fail - get_health_status doesn't exist yet
        from src.automation.youtube_monitoring import get_health_status

        metrics_file = tmp_path / "metrics.json"
        metrics_data = {
            'total_processed': 5,
            'successful': 4,
            'failed': 1,
            'timestamp': datetime.now().isoformat()
        }
        metrics_file.write_text(json.dumps(metrics_data))

        health = get_health_status(metrics_file)

        assert health['status'] == 'ok'
        assert health['last_run']['total_processed'] == 5
        assert health['last_run']['successful'] == 4
        assert health['last_run']['failed'] == 1

    def test_health_check_handles_missing_metrics(self, tmp_path):
        """Test health check when metrics file doesn't exist"""
        from src.automation.youtube_monitoring import get_health_status

        metrics_file = tmp_path / "nonexistent.json"

        health = get_health_status(metrics_file)

        assert health['status'] == 'unknown'
        assert 'last_run' not in health or health['last_run'] is None


class TestIntegrationWithCLI:
    """Test integration of monitoring with YouTube CLI"""

    def test_batch_process_increments_counters(self, tmp_path):
        """Test that batch processing has counters object integrated"""
        from src.cli.youtube_cli import YouTubeCLI
        from src.automation.youtube_monitoring import MonitoringCounters

        # Create minimal vault structure
        vault_path = tmp_path / "vault"
        vault_path.mkdir()

        cli = YouTubeCLI(str(vault_path))

        # Verify counters are initialized
        assert isinstance(cli.processor.counters, MonitoringCounters)
        assert cli.processor.counters.total_processed == 0

        # Manually increment to test integration
        cli.processor.counters.increment_success()
        assert cli.processor.counters.total_processed == 1
        assert cli.processor.counters.successful == 1

    def test_cli_creates_backup_before_apply(self, tmp_path):
        """Test that CLI creates status backup before apply operations"""
        from src.cli.youtube_cli import YouTubeCLI

        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        status_file = vault_path / "youtube_status.json"
        status_file.write_text('{"test": "data"}')
        backup_dir = vault_path / "backups"

        cli = YouTubeCLI(str(vault_path))

        # Process should create backup
        cli.batch_process(preview=False)

        # Verify backup was created
        assert backup_dir.exists()
        backups = list(backup_dir.glob("status_*.json"))
        assert len(backups) >= 1
