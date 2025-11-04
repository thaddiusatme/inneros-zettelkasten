"""
Tests for ConnectionCoordinator extraction from WorkflowManager.

This test suite validates connection discovery coordination functionality.
Includes vault config integration tests (GitHub Issue #45 Phase 2 Priority 3).

Target responsibilities:
- Load and cache note corpus from directories
- Discover semantic connections using AIConnections
- Format connection results for workflow integration
- Provide connection statistics and metrics
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from src.ai.connection_coordinator import ConnectionCoordinator
from src.config.vault_config_loader import get_vault_config


@pytest.fixture
def vault_with_config(tmp_path):
    """
    Fixture providing vault structure with vault configuration.

    Creates knowledge/ subdirectory structure as per vault_config.yaml.
    Used for vault config integration tests (GitHub Issue #45 Phase 2 Priority 3).
    """
    vault = tmp_path / "vault"
    vault.mkdir()

    # Get vault config (creates knowledge/ subdirectory structure)
    config = get_vault_config(str(vault))

    # Ensure vault config directories exist
    config.fleeting_dir.mkdir(parents=True, exist_ok=True)
    config.inbox_dir.mkdir(parents=True, exist_ok=True)
    config.permanent_dir.mkdir(parents=True, exist_ok=True)
    config.literature_dir.mkdir(parents=True, exist_ok=True)

    return {
        "vault": vault,
        "config": config,
        "fleeting_dir": config.fleeting_dir,
        "inbox_dir": config.inbox_dir,
        "permanent_dir": config.permanent_dir,
        "literature_dir": config.literature_dir,
    }


class TestConnectionCoordinatorVaultConfigIntegration:
    """
    Test ConnectionCoordinator uses vault configuration for directory paths.

    RED Phase: This test will fail because current ConnectionCoordinator constructor
    does not accept workflow_manager parameter (GitHub Issue #45 Phase 2 Priority 3).
    """

    def test_connection_coordinator_uses_vault_config_for_directories(
        self, vault_with_config
    ):
        """
        Test that ConnectionCoordinator loads directory paths from vault config.

        Expected RED failure: TypeError about unexpected keyword argument 'workflow_manager'
        because current constructor signature is: __init__(self, base_directory: str, min_similarity: float, max_suggestions: int)

        Target GREEN signature: __init__(self, base_dir: Path, workflow_manager=None, min_similarity: float, max_suggestions: int)
        """
        vault = vault_with_config["vault"]
        config = vault_with_config["config"]

        # Create coordinator with vault config pattern (will fail in RED phase)
        coordinator = ConnectionCoordinator(base_dir=vault, workflow_manager=Mock())

        # Verify coordinator uses vault config paths
        # ConnectionCoordinator uses permanent_dir for default corpus directory
        assert coordinator.base_dir == vault
        assert (vault / "knowledge" / "Permanent Notes") == config.permanent_dir


class TestConnectionCoordinatorCore:
    """Test core connection discovery functionality."""

    @pytest.fixture
    def coordinator(self, vault_with_config):
        """Create ConnectionCoordinator instance with vault config."""
        vault = vault_with_config["vault"]

        # This will fail in RED phase (workflow_manager not accepted yet)
        # Will be fixed in GREEN phase
        return ConnectionCoordinator(base_dir=vault, workflow_manager=Mock())

    def test_initialization(self, coordinator):
        """Test coordinator initializes with correct defaults."""
        assert coordinator.min_similarity == 0.7
        assert coordinator.max_suggestions == 5
        assert coordinator._total_discoveries == 0
        assert coordinator._total_similarity_sum == 0.0

    def test_load_corpus_empty_directory(self, coordinator, vault_with_config):
        """Test loading corpus from empty directory."""
        empty_dir = vault_with_config["permanent_dir"]
        corpus = coordinator.load_corpus(empty_dir)

        assert corpus == {}
        assert str(empty_dir) in coordinator._corpus_cache

    def test_load_corpus_with_notes(self, coordinator, vault_with_config):
        """Test loading corpus from directory with notes."""
        permanent_dir = vault_with_config["permanent_dir"]

        # Create test notes
        note1 = permanent_dir / "note1.md"
        note1.write_text("Content of note 1")

        note2 = permanent_dir / "note2.md"
        note2.write_text("Content of note 2")

        corpus = coordinator.load_corpus(permanent_dir)

        assert len(corpus) == 2
        assert "note1.md" in corpus
        assert "note2.md" in corpus
        assert corpus["note1.md"] == "Content of note 1"
        assert corpus["note2.md"] == "Content of note 2"

    def test_discover_connections_empty_corpus(self, coordinator, vault_with_config):
        """Test connection discovery with empty corpus."""
        permanent_dir = vault_with_config["permanent_dir"]

        connections = coordinator.discover_connections(
            target_content="Test content", corpus_dir=permanent_dir
        )

        assert connections == []

    def test_discover_connections_empty_content(self, coordinator, vault_with_config):
        """Test connection discovery with empty content."""
        connections = coordinator.discover_connections(
            target_content="", corpus_dir=vault_with_config["permanent_dir"]
        )

        assert connections == []

    def test_validate_connections_empty_list(self, coordinator):
        """Test validating empty connections list."""
        validated = coordinator.validate_connections([])
        assert validated == []

    def test_validate_connections_deduplication(self, coordinator):
        """Test connection deduplication keeps highest similarity."""
        connections = [
            {"filename": "note1.md", "similarity": 0.8},
            {"filename": "note1.md", "similarity": 0.9},  # Higher similarity
            {"filename": "note2.md", "similarity": 0.7},
        ]

        validated = coordinator.validate_connections(connections)

        assert len(validated) == 2
        # Should keep note1.md with 0.9 similarity
        note1_entry = [c for c in validated if c["filename"] == "note1.md"][0]
        assert note1_entry["similarity"] == 0.9
        # Should sort by similarity descending
        assert validated[0]["similarity"] >= validated[1]["similarity"]

    def test_get_connection_statistics_initial(self, coordinator):
        """Test statistics before any discoveries."""
        stats = coordinator.get_connection_statistics()

        assert stats["total_discoveries"] == 0
        assert stats["average_similarity"] == 0.0

    def test_clear_cache(self, coordinator, vault_with_config):
        """Test clearing corpus cache."""
        permanent_dir = vault_with_config["permanent_dir"]

        # Load corpus to populate cache
        coordinator.load_corpus(permanent_dir)
        assert len(coordinator._corpus_cache) > 0

        # Clear cache
        coordinator.clear_cache()
        assert len(coordinator._corpus_cache) == 0
