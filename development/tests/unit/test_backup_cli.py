#!/usr/bin/env python3
"""
ADR-004 Iteration 5: Backup CLI Tests (RED PHASE)

Test suite for backup_cli.py - dedicated CLI for backup management operations.
Extracts --prune-backups command from workflow_demo.py.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestBackupCLI:
    """
    RED PHASE: Tests for backup_cli.py (currently failing - module doesn't exist)
    
    Commands to test:
    - prune-backups: Remove old backup directories (keeping N most recent)
    """

    def setup_method(self):
        """Set up test environment with backup directories."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)

        # Create main vault directory structure
        (self.base_dir / "Inbox").mkdir()
        (self.base_dir / "Permanent Notes").mkdir()
        (self.base_dir / "Media").mkdir()

        # Create test backup directories (simulating old backups)
        backup_root = Path.home() / "backups" / self.base_dir.name
        backup_root.mkdir(parents=True, exist_ok=True)

        # Create 5 mock backups with timestamps
        import time
        for i in range(5):
            backup_name = f"backup-202510{10+i:02d}-{12+i:02d}0000"
            backup_dir = backup_root / backup_name
            backup_dir.mkdir(exist_ok=True)
            (backup_dir / "test.txt").write_text(f"Backup {i}")
            time.sleep(0.1)  # Ensure distinct timestamps

        self.backup_root = backup_root

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if hasattr(self, 'backup_root') and self.backup_root.exists():
            shutil.rmtree(self.backup_root, ignore_errors=True)

    def test_backup_cli_import(self):
        """TEST 1: Verify backup_cli module can be imported (RED PHASE)."""
        try:
            from src.cli import backup_cli
            assert backup_cli is not None
        except ImportError as e:
            pytest.fail(f"backup_cli module should exist and be importable: {e}")

    def test_prune_backups_command_execution(self):
        """TEST 2: Verify prune-backups command executes successfully."""
        from src.cli.backup_cli import BackupCLI

        cli = BackupCLI(vault_path=str(self.base_dir))

        # Execute prune-backups command (keep 3 most recent)
        exit_code = cli.prune_backups(
            keep=3,
            dry_run=False,
            output_format='normal'
        )

        # Should execute without errors
        assert exit_code == 0

    def test_prune_backups_dry_run(self):
        """TEST 3: Verify prune-backups dry-run mode works correctly."""
        from src.cli.backup_cli import BackupCLI

        cli = BackupCLI(vault_path=str(self.base_dir))

        # Get initial backup count
        initial_backups = len(list(self.backup_root.glob("backup-*")))

        # Execute prune-backups in dry-run mode
        exit_code = cli.prune_backups(
            keep=2,
            dry_run=True,
            output_format='normal'
        )

        # Should execute without errors
        assert exit_code == 0

        # Backups should NOT be deleted in dry-run mode
        final_backups = len(list(self.backup_root.glob("backup-*")))
        assert final_backups == initial_backups, "Dry-run should not delete backups"

    def test_prune_backups_json_output(self):
        """TEST 4: Verify JSON output format for prune-backups command."""
        from src.cli.backup_cli import BackupCLI
        import json
        from io import StringIO

        cli = BackupCLI(vault_path=str(self.base_dir))

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            # Execute command with JSON format
            exit_code = cli.prune_backups(
                keep=3,
                dry_run=True,
                output_format='json'
            )

            # Get output
            output = captured_output.getvalue()

            # Should be valid JSON
            data = json.loads(output)
            assert isinstance(data, dict)
            assert "to_prune" in data or "backups" in data
            assert exit_code == 0

        finally:
            sys.stdout = sys.__stdout__

    def test_argparse_integration(self):
        """TEST 5: Verify CLI has proper argparse command structure."""
        from src.cli.backup_cli import create_parser

        parser = create_parser()

        # Should have program name
        assert parser.prog is not None

        # Test parsing prune-backups command
        args = parser.parse_args(['prune-backups', '--keep', '5'])
        assert args.command == 'prune-backups'
        assert args.keep == 5

    def test_directory_organizer_integration(self):
        """TEST 6: Verify CLI uses DirectoryOrganizer for backup operations."""
        from src.cli.backup_cli import BackupCLI
        from src.utils.directory_organizer import DirectoryOrganizer

        cli = BackupCLI(vault_path=str(self.base_dir))

        # Verify it's using DirectoryOrganizer
        assert hasattr(cli, 'organizer'), \
            "BackupCLI should have DirectoryOrganizer instance"
        assert isinstance(cli.organizer, DirectoryOrganizer), \
            "BackupCLI should use DirectoryOrganizer for backup management"
