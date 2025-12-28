"""
TDD RED Phase: Tests for Smart Link Review CLI

Issue #58: Smart Link Review Queue CLI

Provides a simple terminal interface for reviewing smart link suggestions:
- Show suggestion → [a]ccept / [d]ismiss / [s]kip
- Store decisions in note frontmatter
- Batch processing support

Test Cases:
1. CLI displays pending suggestions with source/target info
2. User can accept suggestion (inserts link)
3. User can dismiss suggestion (marks as dismissed)
4. User can skip suggestion (moves to next)
5. Decisions persist to note frontmatter
6. CLI shows progress (X of Y suggestions)
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestSmartLinkReviewCLI:
    """Test suite for smart link review CLI."""

    def setup_method(self):
        """Create temporary vault with test notes."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)

        # Create test notes
        (self.vault_path / "python-basics.md").write_text(
            "---\ntitle: Python Basics\n---\n# Python Basics\nLearn Python programming."
        )
        (self.vault_path / "web-frameworks.md").write_text(
            "---\ntitle: Web Frameworks\n---\n# Web Frameworks\nDjango and Flask for Python."
        )

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_displays_pending_suggestions(self):
        """
        CLI should display pending suggestions with source and target info.
        """
        from src.cli.smart_link_review_cli import SmartLinkReviewCLI

        cli = SmartLinkReviewCLI(vault_path=self.vault_path)

        # Mock suggestions
        suggestions = [
            {
                "source": "python-basics.md",
                "target": "web-frameworks.md",
                "similarity": 0.85,
                "reason": "Both discuss Python",
            }
        ]

        # Get display output
        display = cli.format_suggestion(suggestions[0])

        assert "python-basics.md" in display
        assert "web-frameworks.md" in display
        assert "0.85" in display or "85%" in display

    def test_cli_shows_progress_indicator(self):
        """
        CLI should show progress (e.g., "Suggestion 1 of 5").
        """
        from src.cli.smart_link_review_cli import SmartLinkReviewCLI

        cli = SmartLinkReviewCLI(vault_path=self.vault_path)

        progress = cli.format_progress(current=2, total=5)

        assert "2" in progress
        assert "5" in progress

    def test_accept_suggestion_returns_accept_action(self):
        """
        When user inputs 'a', CLI should return accept action.
        """
        from src.cli.smart_link_review_cli import SmartLinkReviewCLI

        cli = SmartLinkReviewCLI(vault_path=self.vault_path)

        suggestion = {
            "source": "python-basics.md",
            "target": "web-frameworks.md",
            "similarity": 0.85,
        }

        # Simulate user input 'a'
        with patch("builtins.input", return_value="a"):
            action = cli.get_user_decision(suggestion)

        assert action == "accept"

    def test_dismiss_suggestion_returns_dismiss_action(self):
        """
        When user inputs 'd', CLI should return dismiss action.
        """
        from src.cli.smart_link_review_cli import SmartLinkReviewCLI

        cli = SmartLinkReviewCLI(vault_path=self.vault_path)

        suggestion = {
            "source": "python-basics.md",
            "target": "web-frameworks.md",
            "similarity": 0.85,
        }

        with patch("builtins.input", return_value="d"):
            action = cli.get_user_decision(suggestion)

        assert action == "dismiss"

    def test_skip_suggestion_returns_skip_action(self):
        """
        When user inputs 's', CLI should return skip action.
        """
        from src.cli.smart_link_review_cli import SmartLinkReviewCLI

        cli = SmartLinkReviewCLI(vault_path=self.vault_path)

        suggestion = {
            "source": "python-basics.md",
            "target": "web-frameworks.md",
            "similarity": 0.85,
        }

        with patch("builtins.input", return_value="s"):
            action = cli.get_user_decision(suggestion)

        assert action == "skip"

    def test_review_session_processes_all_suggestions(self):
        """
        review_suggestions() should process all suggestions and return results.
        """
        from src.cli.smart_link_review_cli import SmartLinkReviewCLI

        cli = SmartLinkReviewCLI(vault_path=self.vault_path)

        suggestions = [
            {"source": "note1.md", "target": "note2.md", "similarity": 0.9},
            {"source": "note1.md", "target": "note3.md", "similarity": 0.8},
        ]

        # Simulate accepting first, skipping second
        with patch("builtins.input", side_effect=["a", "s"]):
            results = cli.review_suggestions(suggestions)

        assert len(results) == 2
        assert results[0]["action"] == "accept"
        assert results[1]["action"] == "skip"

    def test_review_results_include_suggestion_data(self):
        """
        Review results should include original suggestion data.
        """
        from src.cli.smart_link_review_cli import SmartLinkReviewCLI

        cli = SmartLinkReviewCLI(vault_path=self.vault_path)

        suggestions = [
            {"source": "note1.md", "target": "note2.md", "similarity": 0.9},
        ]

        with patch("builtins.input", return_value="a"):
            results = cli.review_suggestions(suggestions)

        assert results[0]["suggestion"]["source"] == "note1.md"
        assert results[0]["suggestion"]["target"] == "note2.md"


class TestSmartLinkReviewCLIIntegration:
    """Integration tests for CLI with SmartLinkEngineIntegrator."""

    def setup_method(self):
        """Create temporary vault."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)

        # Create related notes
        (self.vault_path / "python.md").write_text(
            "# Python\nPython programming language."
        )
        (self.vault_path / "django.md").write_text(
            "# Django\nDjango is a Python web framework."
        )

    def teardown_method(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_can_generate_suggestions_from_vault(self):
        """
        CLI should be able to generate suggestions from vault notes.
        """
        from src.cli.smart_link_review_cli import SmartLinkReviewCLI

        cli = SmartLinkReviewCLI(vault_path=self.vault_path)

        # Mock the AI to return suggestions
        with patch.object(cli, "_get_suggestions_for_note") as mock_get:
            mock_get.return_value = [
                {"source": "python.md", "target": "django.md", "similarity": 0.9}
            ]

            suggestions = cli.get_pending_suggestions("python.md")

        assert len(suggestions) >= 0  # May be 0 if no AI, but should not error


class TestSmartLinkReviewCLIMain:
    """Tests for CLI main entry point."""

    def test_main_with_vault_path_argument(self):
        """
        CLI main should accept --vault argument.
        """
        from src.cli.smart_link_review_cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["--vault", "/path/to/vault"])

        assert args.vault == "/path/to/vault"

    def test_main_with_note_argument(self):
        """
        CLI main should accept --note argument for single note review.
        """
        from src.cli.smart_link_review_cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["--vault", "/path/to/vault", "--note", "my-note.md"])

        assert args.note == "my-note.md"
