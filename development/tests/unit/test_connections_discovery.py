"""
Spec tests for the connections_discovery module (#120).

Verifies the public API surface of the consolidated module:
- AIConnections and ConnectionCoordinator importable from connections_discovery
- Core behaviours preserved from the old connections.py / connection_coordinator.py
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "src")
sys.path.insert(0, src_dir)

from ai.connections_discovery import AIConnections, ConnectionCoordinator


# ---------------------------------------------------------------------------
# AIConnections — interface
# ---------------------------------------------------------------------------


class TestAIConnectionsInterface:
    def test_importable(self):
        assert AIConnections is not None

    def test_init_defaults(self):
        c = AIConnections()
        assert c.similarity_threshold == 0.7
        assert c.max_suggestions == 5

    def test_init_custom(self):
        c = AIConnections(similarity_threshold=0.9, max_suggestions=3)
        assert c.similarity_threshold == 0.9
        assert c.max_suggestions == 3

    def test_has_find_similar_notes(self):
        assert callable(getattr(AIConnections, "find_similar_notes", None))

    def test_has_suggest_links(self):
        assert callable(getattr(AIConnections, "suggest_links", None))

    def test_has_build_connection_map(self):
        assert callable(getattr(AIConnections, "build_connection_map", None))


# ---------------------------------------------------------------------------
# AIConnections — behaviour
# ---------------------------------------------------------------------------


class TestAIConnectionsBehaviour:
    def setup_method(self):
        self.c = AIConnections()

    def test_extract_content_strips_frontmatter(self):
        note = "---\ntype: permanent\n---\n\nReal content here."
        result = self.c._extract_content(note)
        assert "Real content here." in result
        assert "type: permanent" not in result

    def test_extract_content_no_frontmatter(self):
        note = "Plain content, no yaml."
        assert self.c._extract_content(note) == note

    def test_normalize_text_lowercases_and_strips(self):
        assert self.c._normalize_text("  Hello World  ") == "hello world"

    def test_normalize_text_empty(self):
        assert self.c._normalize_text("") == ""

    def test_simple_text_similarity_identical(self):
        score = self.c._simple_text_similarity("alpha beta gamma", "alpha beta gamma")
        assert score == 1.0

    def test_simple_text_similarity_no_overlap(self):
        score = self.c._simple_text_similarity("alpha beta", "gamma delta")
        assert score == 0.0

    def test_cosine_similarity_identical_vectors(self):
        v = [1.0, 0.0, 0.0]
        assert self.c._cosine_similarity(v, v) == pytest.approx(1.0)

    def test_cosine_similarity_zero_vector(self):
        assert self.c._cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0

    def test_find_similar_notes_returns_list(self):
        corpus = {"note_a.md": "content about AI", "note_b.md": "other content"}
        with patch.object(self.c, "_calculate_semantic_similarity", return_value=0.9):
            results = self.c.find_similar_notes("content about AI", corpus)
        assert isinstance(results, list)

    def test_suggest_links_empty_corpus(self):
        results = self.c.suggest_links("some content", {})
        assert results == []

    def test_build_connection_map_empty_corpus(self):
        result = self.c.build_connection_map({})
        assert result == {}


# ---------------------------------------------------------------------------
# ConnectionCoordinator — interface
# ---------------------------------------------------------------------------


class TestConnectionCoordinatorInterface:
    def test_importable(self):
        assert ConnectionCoordinator is not None

    def test_has_load_corpus(self):
        assert callable(getattr(ConnectionCoordinator, "load_corpus", None))

    def test_has_discover_connections(self):
        assert callable(getattr(ConnectionCoordinator, "discover_connections", None))

    def test_has_validate_connections(self):
        assert callable(getattr(ConnectionCoordinator, "validate_connections", None))

    def test_has_get_connection_statistics(self):
        assert callable(
            getattr(ConnectionCoordinator, "get_connection_statistics", None)
        )

    def test_has_clear_cache(self):
        assert callable(getattr(ConnectionCoordinator, "clear_cache", None))


# ---------------------------------------------------------------------------
# ConnectionCoordinator — behaviour
# ---------------------------------------------------------------------------


class TestConnectionCoordinatorBehaviour:
    def setup_method(self):
        self.coord = ConnectionCoordinator(base_directory="/tmp/test_vault")

    def test_init_sets_base_directory(self):
        assert self.coord.base_directory == "/tmp/test_vault"

    def test_init_default_similarity(self):
        assert self.coord.min_similarity == 0.7

    def test_init_custom_similarity(self):
        coord = ConnectionCoordinator(base_directory="/tmp", min_similarity=0.5)
        assert coord.min_similarity == 0.5

    def test_load_corpus_missing_directory(self, tmp_path):
        coord = ConnectionCoordinator(base_directory=str(tmp_path))
        corpus = coord.load_corpus(tmp_path / "nonexistent")
        assert corpus == {}

    def test_load_corpus_reads_md_files(self, tmp_path):
        (tmp_path / "a.md").write_text("content a")
        (tmp_path / "b.md").write_text("content b")
        coord = ConnectionCoordinator(base_directory=str(tmp_path))
        corpus = coord.load_corpus(tmp_path)
        assert len(corpus) == 2

    def test_validate_connections_filters_low_score(self):
        coord = ConnectionCoordinator(base_directory="/tmp", min_similarity=0.7)
        connections = [
            {"filename": "a.md", "similarity": 0.9},
            {"filename": "b.md", "similarity": 0.5},
        ]
        valid = coord.validate_connections(connections)
        assert len(valid) == 1
        assert valid[0]["filename"] == "a.md"

    def test_get_connection_statistics_empty(self):
        stats = self.coord.get_connection_statistics()
        assert isinstance(stats, dict)

    def test_clear_cache(self):
        self.coord.clear_cache()  # should not raise
