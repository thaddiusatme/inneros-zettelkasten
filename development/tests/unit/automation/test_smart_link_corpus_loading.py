"""
TDD RED Phase: Tests for SmartLinkEngineIntegrator vault corpus loading

Issue #58: Smart Link Review Queue CLI - Fix vault corpus loading

The SmartLinkEngineIntegrator currently passes empty corpus {} to find_similar_notes(),
resulting in zero suggestions. These tests verify proper corpus loading.

Test Cases:
1. _load_vault_corpus() loads all markdown files from vault
2. _load_vault_corpus() excludes target note from corpus
3. _load_vault_corpus() handles nested directories
4. process_note_for_links() uses real corpus (not empty)
5. process_note_for_links() finds >0 suggestions for related notes
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestSmartLinkCorpusLoading:
    """Test suite for SmartLinkEngineIntegrator vault corpus loading."""

    def setup_method(self):
        """Create temporary vault with test notes."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)

        # Create test notes
        (self.vault_path / "note1.md").write_text(
            "# Python Programming\nPython is a versatile programming language."
        )
        (self.vault_path / "note2.md").write_text(
            "# JavaScript Basics\nJavaScript is used for web development."
        )
        (self.vault_path / "note3.md").write_text(
            "# Python Web Frameworks\nDjango and Flask are Python web frameworks."
        )

        # Create nested directory with notes
        nested_dir = self.vault_path / "topics"
        nested_dir.mkdir()
        (nested_dir / "databases.md").write_text(
            "# Database Design\nSQL and NoSQL databases for data storage."
        )

    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_vault_corpus_loads_all_markdown_files(self):
        """
        _load_vault_corpus() should load all .md files from vault directory.
        """
        from src.automation.feature_handler_utils import SmartLinkEngineIntegrator
        import logging

        integrator = SmartLinkEngineIntegrator(
            vault_path=self.vault_path, logger=logging.getLogger("test")
        )

        corpus = integrator._load_vault_corpus()

        # Should load all 4 markdown files
        assert len(corpus) >= 4, f"Expected at least 4 notes, got {len(corpus)}"

        # Verify content is loaded
        assert any("Python" in content for content in corpus.values())
        assert any("JavaScript" in content for content in corpus.values())

    def test_load_vault_corpus_excludes_target_note(self):
        """
        _load_vault_corpus() should exclude the target note being analyzed.
        """
        from src.automation.feature_handler_utils import SmartLinkEngineIntegrator
        import logging

        integrator = SmartLinkEngineIntegrator(
            vault_path=self.vault_path, logger=logging.getLogger("test")
        )

        target_file = self.vault_path / "note1.md"
        corpus = integrator._load_vault_corpus(exclude_file=target_file)

        # Should have 3 notes (excluding note1.md)
        assert (
            len(corpus) == 3
        ), f"Expected 3 notes (excluding target), got {len(corpus)}"

        # Target note should not be in corpus
        assert "note1.md" not in corpus
        assert str(target_file) not in corpus

    def test_load_vault_corpus_handles_nested_directories(self):
        """
        _load_vault_corpus() should recursively load from nested directories.
        """
        from src.automation.feature_handler_utils import SmartLinkEngineIntegrator
        import logging

        integrator = SmartLinkEngineIntegrator(
            vault_path=self.vault_path, logger=logging.getLogger("test")
        )

        corpus = integrator._load_vault_corpus()

        # Should include note from nested directory
        assert any("Database" in content for content in corpus.values())

    def test_process_note_uses_real_corpus(self):
        """
        process_note_for_links() should pass real vault corpus to AI,
        not an empty dictionary.
        """
        from src.automation.feature_handler_utils import SmartLinkEngineIntegrator
        import logging

        integrator = SmartLinkEngineIntegrator(
            vault_path=self.vault_path, logger=logging.getLogger("test")
        )

        # Mock AIConnections to capture corpus argument
        mock_ai = MagicMock()
        mock_ai.find_similar_notes.return_value = []
        integrator.ai_connections = mock_ai

        target_file = self.vault_path / "note1.md"
        integrator.process_note_for_links(target_file)

        # Verify find_similar_notes was called with non-empty corpus
        mock_ai.find_similar_notes.assert_called_once()
        call_args = mock_ai.find_similar_notes.call_args

        # Second positional arg or 'note_corpus' kwarg should be non-empty
        if call_args.kwargs:
            corpus = call_args.kwargs.get("note_corpus", {})
        else:
            corpus = call_args.args[1] if len(call_args.args) > 1 else {}

        assert len(corpus) > 0, "Corpus should not be empty"

    def test_process_note_finds_suggestions_for_related_notes(self):
        """
        process_note_for_links() should find >0 suggestions when related notes exist.

        This is the key acceptance test: notes about Python should find
        other Python-related notes as suggestions.
        """
        from src.automation.feature_handler_utils import SmartLinkEngineIntegrator
        import logging

        integrator = SmartLinkEngineIntegrator(
            vault_path=self.vault_path,
            logger=logging.getLogger("test"),
            similarity_threshold=0.3,  # Lower threshold for test
            max_suggestions=10,
        )

        # Mock AIConnections to return related notes
        mock_ai = MagicMock()
        # Simulate finding note3 (Python Web Frameworks) as similar to note1 (Python)
        mock_ai.find_similar_notes.return_value = [
            ("note3.md", 0.85),
        ]
        integrator.ai_connections = mock_ai

        target_file = self.vault_path / "note1.md"
        result = integrator.process_note_for_links(target_file)

        assert result["success"] is True
        assert (
            result["suggestions_count"] > 0
        ), "Should find >0 suggestions for related content"


class TestSmartLinkCorpusCaching:
    """Test suite for corpus caching optimization."""

    def setup_method(self):
        """Create temporary vault."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)

        for i in range(5):
            (self.vault_path / f"note{i}.md").write_text(
                f"# Note {i}\nContent for note {i}."
            )

    def teardown_method(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_corpus_can_be_cached_for_performance(self):
        """
        Corpus loading should support caching to avoid re-reading files.
        """
        from src.automation.feature_handler_utils import SmartLinkEngineIntegrator
        import logging

        integrator = SmartLinkEngineIntegrator(
            vault_path=self.vault_path, logger=logging.getLogger("test")
        )

        # First load
        corpus1 = integrator._load_vault_corpus()

        # Second load should be available (caching is optional optimization)
        corpus2 = integrator._load_vault_corpus()

        assert len(corpus1) == len(corpus2)
