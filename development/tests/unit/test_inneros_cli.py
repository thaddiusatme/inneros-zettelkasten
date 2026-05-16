"""
Spec tests for the unified inneros CLI (#121).

Verifies the public interface of src/cli/inneros.py:
- Single entry point replaces backup_cli, fleeting_cli, weekly_review_cli
- Top-level subcommands: backup, fleeting, review, inbox
- All original subcommand flags preserved
- Makefile targets continue to work via the new entry point
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import argparse

import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "src")
sys.path.insert(0, src_dir)

from cli.inneros import create_parser, main


# ---------------------------------------------------------------------------
# Parser — top-level structure
# ---------------------------------------------------------------------------


class TestInnerosParserStructure:
    def setup_method(self):
        self.parser = create_parser()

    def test_parser_importable(self):
        assert create_parser is not None

    def test_main_callable(self):
        assert callable(main)

    def test_parser_has_vault_argument(self):
        args = self.parser.parse_args(["--vault", "/tmp/vault", "backup"])
        assert args.vault == "/tmp/vault"

    def test_parser_has_verbose_flag(self):
        args = self.parser.parse_args(["--vault", "/tmp", "--verbose", "backup"])
        assert args.verbose is True

    def test_parser_accepts_backup_command(self):
        args = self.parser.parse_args(["--vault", "/tmp", "backup"])
        assert args.command == "backup"

    def test_parser_accepts_fleeting_command(self):
        args = self.parser.parse_args(["--vault", "/tmp", "fleeting", "health"])
        assert args.command == "fleeting"

    def test_parser_accepts_review_command(self):
        args = self.parser.parse_args(["--vault", "/tmp", "review"])
        assert args.command == "review"

    def test_parser_accepts_inbox_command(self):
        args = self.parser.parse_args(["--vault", "/tmp", "inbox"])
        assert args.command == "inbox"


# ---------------------------------------------------------------------------
# backup subcommand
# ---------------------------------------------------------------------------


class TestBackupSubcommand:
    def setup_method(self):
        self.parser = create_parser()

    def test_backup_default_no_subcommand(self):
        args = self.parser.parse_args(["--vault", "/tmp", "backup"])
        assert args.command == "backup"

    def test_backup_prune_subcommand(self):
        args = self.parser.parse_args(["--vault", "/tmp", "backup", "prune"])
        assert args.subcommand == "prune"

    def test_backup_prune_has_keep_flag(self):
        args = self.parser.parse_args(
            ["--vault", "/tmp", "backup", "prune", "--keep", "5"]
        )
        assert args.keep == 5

    def test_backup_prune_keep_defaults_to_3(self):
        args = self.parser.parse_args(["--vault", "/tmp", "backup", "prune"])
        assert args.keep == 3

    def test_backup_prune_has_dry_run_flag(self):
        args = self.parser.parse_args(
            ["--vault", "/tmp", "backup", "prune", "--dry-run"]
        )
        assert args.dry_run is True


# ---------------------------------------------------------------------------
# fleeting subcommand
# ---------------------------------------------------------------------------


class TestFleetingSubcommand:
    def setup_method(self):
        self.parser = create_parser()

    def test_fleeting_health_subcommand(self):
        args = self.parser.parse_args(["--vault", "/tmp", "fleeting", "health"])
        assert args.command == "fleeting"
        assert args.subcommand == "health"

    def test_fleeting_triage_subcommand(self):
        args = self.parser.parse_args(["--vault", "/tmp", "fleeting", "triage"])
        assert args.command == "fleeting"
        assert args.subcommand == "triage"

    def test_fleeting_health_has_format_flag(self):
        args = self.parser.parse_args(
            ["--vault", "/tmp", "fleeting", "health", "--format", "json"]
        )
        assert args.format == "json"

    def test_fleeting_triage_has_quality_threshold(self):
        args = self.parser.parse_args(
            ["--vault", "/tmp", "fleeting", "triage", "--quality-threshold", "0.8"]
        )
        assert args.quality_threshold == pytest.approx(0.8)

    def test_fleeting_triage_has_fast_flag(self):
        args = self.parser.parse_args(
            ["--vault", "/tmp", "fleeting", "triage", "--fast"]
        )
        assert args.fast is True


# ---------------------------------------------------------------------------
# review subcommand
# ---------------------------------------------------------------------------


class TestReviewSubcommand:
    def setup_method(self):
        self.parser = create_parser()

    def test_review_default(self):
        args = self.parser.parse_args(["--vault", "/tmp", "review"])
        assert args.command == "review"

    def test_review_has_preview_flag(self):
        args = self.parser.parse_args(["--vault", "/tmp", "review", "--preview"])
        assert args.preview is True

    def test_review_metrics_subcommand(self):
        args = self.parser.parse_args(["--vault", "/tmp", "review", "metrics"])
        assert args.subcommand == "metrics"

    def test_review_has_format_flag(self):
        args = self.parser.parse_args(["--vault", "/tmp", "review", "--format", "json"])
        assert args.format == "json"

    def test_review_export_flag(self):
        args = self.parser.parse_args(["--vault", "/tmp", "review", "--export"])
        assert args.export is True


# ---------------------------------------------------------------------------
# inbox subcommand
# ---------------------------------------------------------------------------


class TestInboxSubcommand:
    def setup_method(self):
        self.parser = create_parser()

    def test_inbox_default(self):
        args = self.parser.parse_args(["--vault", "/tmp", "inbox"])
        assert args.command == "inbox"

    def test_inbox_has_dry_run_flag(self):
        args = self.parser.parse_args(["--vault", "/tmp", "inbox", "--dry-run"])
        assert args.dry_run is True

    def test_inbox_dry_run_defaults_false(self):
        args = self.parser.parse_args(["--vault", "/tmp", "inbox"])
        assert args.dry_run is False

    def test_inbox_has_format_flag(self):
        args = self.parser.parse_args(["--vault", "/tmp", "inbox", "--format", "json"])
        assert args.format == "json"


# ---------------------------------------------------------------------------
# main() dispatch — each command calls the right handler
# ---------------------------------------------------------------------------


class TestMainDispatch:
    def test_main_backup_dispatches(self, tmp_path):
        with patch("cli.inneros._run_backup") as mock:
            main(["--vault", str(tmp_path), "backup"])
            mock.assert_called_once()

    def test_main_fleeting_health_dispatches(self, tmp_path):
        with patch("cli.inneros._run_fleeting") as mock:
            main(["--vault", str(tmp_path), "fleeting", "health"])
            mock.assert_called_once()

    def test_main_review_dispatches(self, tmp_path):
        with patch("cli.inneros._run_review") as mock:
            main(["--vault", str(tmp_path), "review"])
            mock.assert_called_once()

    def test_main_inbox_dispatches(self, tmp_path):
        with patch("cli.inneros._run_inbox") as mock:
            main(["--vault", str(tmp_path), "inbox"])
            mock.assert_called_once()

    def test_main_returns_int(self, tmp_path):
        with patch("cli.inneros._run_backup", return_value=0):
            result = main(["--vault", str(tmp_path), "backup"])
        assert isinstance(result, int)

    def test_main_backup_exits_0_on_success(self, tmp_path):
        with patch("cli.inneros._run_backup", return_value=0):
            result = main(["--vault", str(tmp_path), "backup"])
        assert result == 0

    def test_main_exits_nonzero_on_error(self, tmp_path):
        with patch("cli.inneros._run_backup", return_value=1):
            result = main(["--vault", str(tmp_path), "backup"])
        assert result != 0


# ---------------------------------------------------------------------------
# Backward-compat shims — old CLIs still importable
# ---------------------------------------------------------------------------


class TestBackwardCompatShims:
    def test_backup_cli_still_importable(self):
        from cli.backup_cli import main as backup_main

        assert callable(backup_main)

    def test_fleeting_cli_still_importable(self):
        from cli.fleeting_cli import main as fleeting_main

        assert callable(fleeting_main)

    def test_weekly_review_cli_still_importable(self):
        from cli.weekly_review_cli import main as review_main

        assert callable(review_main)
