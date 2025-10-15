"""
Tests for ConnectionCoordinator - Extracted from WorkflowManager god class.

ADR-002 Phase 2: Connection discovery responsibility extraction.
Following proven NoteLifecycleManager TDD pattern.

Extracts:
- _load_notes_corpus() from WorkflowManager
- Connection discovery orchestration using AIConnections
- Result formatting for workflow integration

RED Phase Tests (Expected to fail initially):
- Test corpus loading and caching
- Test connection discovery with AIConnections integration
- Test result formatting
- Test error handling for missing/invalid data
"""

import pytest
from pathlib import Path
import tempfile
import shutil

# Import will fail initially - this is expected in RED phase
try:
    from src.ai.connection_coordinator import ConnectionCoordinator
except ImportError:
    ConnectionCoordinator = None


class TestConnectionCoordinatorCore:
    """Core functionality tests for ConnectionCoordinator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.permanent_dir = self.test_dir / "Permanent Notes"
        self.permanent_dir.mkdir(parents=True)
        
        # Create sample permanent notes for corpus
        self._create_note(
            self.permanent_dir / "ai-basics.md",
            """---
title: AI Basics
tags: [ai, machine-learning]
---

# AI Basics

Artificial intelligence is the simulation of human intelligence by machines.
Machine learning is a subset of AI that learns from data.
"""
        )
        
        self._create_note(
            self.permanent_dir / "neural-networks.md",
            """---
title: Neural Networks
tags: [ai, deep-learning, neural-networks]
---

# Neural Networks

Neural networks are computing systems inspired by biological neural networks.
Deep learning uses multiple layers of neural networks.
"""
        )
        
        self._create_note(
            self.permanent_dir / "python-basics.md",
            """---
title: Python Basics
tags: [programming, python]
---

# Python Basics

Python is a high-level programming language.
It's widely used for data science and web development.
"""
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def _create_note(self, path: Path, content: str):
        """Helper to create a test note."""
        path.write_text(content)
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_discover_connections_finds_similar_notes(self):
        """Test discovering connections between a note and corpus."""
        manager = ConnectionCoordinator(str(self.test_dir))
        
        target_content = """---
title: Machine Learning Tutorial
---

Machine learning algorithms learn patterns from data.
Neural networks are a popular approach to machine learning.
"""
        
        # Should find ai-basics.md and neural-networks.md as related
        connections = manager.discover_connections(
            target_content,
            corpus_dir=self.permanent_dir
        )
        
        assert len(connections) > 0
        assert any("ai-basics.md" in conn["filename"] for conn in connections)
        assert all("similarity" in conn for conn in connections)
        assert all(conn["similarity"] >= 0.0 for conn in connections)
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_discover_connections_respects_quality_threshold(self):
        """Test connection quality filtering."""
        manager = ConnectionCoordinator(
            str(self.test_dir),
            min_similarity=0.8  # High threshold
        )
        
        target_content = """---
title: Completely Different Topic
---

This note discusses gardening and plant care.
Growing vegetables requires proper soil and sunlight.
"""
        
        # Should find few or no connections due to low similarity
        connections = manager.discover_connections(
            target_content,
            corpus_dir=self.permanent_dir
        )
        
        # Either empty or only high-quality matches
        assert all(conn["similarity"] >= 0.8 for conn in connections)
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_load_corpus_caches_notes(self):
        """Test corpus loading and caching."""
        manager = ConnectionCoordinator(str(self.test_dir))
        
        # Load corpus
        corpus = manager.load_corpus(self.permanent_dir)
        
        assert len(corpus) == 3
        assert "ai-basics.md" in corpus
        assert "neural-networks.md" in corpus
        assert "python-basics.md" in corpus
        
        # Verify content loaded
        assert "Artificial intelligence" in corpus["ai-basics.md"]
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_validate_connections_filters_duplicates(self):
        """Test connection validation removes duplicates."""
        manager = ConnectionCoordinator(str(self.test_dir))
        
        # Simulate duplicate connections
        connections = [
            {"filename": "ai-basics.md", "similarity": 0.85},
            {"filename": "neural-networks.md", "similarity": 0.75},
            {"filename": "ai-basics.md", "similarity": 0.80},  # Duplicate
        ]
        
        validated = manager.validate_connections(connections)
        
        # Should keep only highest similarity for duplicates
        assert len(validated) == 2
        ai_basics_connections = [c for c in validated if c["filename"] == "ai-basics.md"]
        assert len(ai_basics_connections) == 1
        assert ai_basics_connections[0]["similarity"] == 0.85


class TestConnectionCoordinatorIntegration:
    """Integration tests with existing AI components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.permanent_dir = self.test_dir / "Permanent Notes"
        self.permanent_dir.mkdir(parents=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_connection_manager_uses_ai_connections(self):
        """Test ConnectionCoordinator integrates with AIConnections."""
        manager = ConnectionCoordinator(str(self.test_dir))
        
        # Verify AIConnections is initialized
        assert manager.connections is not None
        assert hasattr(manager.connections, 'find_similar_notes')
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_discover_connections_handles_empty_corpus(self):
        """Test graceful handling of empty corpus."""
        manager = ConnectionCoordinator(str(self.test_dir))
        
        target_content = "Some content"
        connections = manager.discover_connections(
            target_content,
            corpus_dir=self.permanent_dir  # Empty directory
        )
        
        assert connections == []
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_discover_connections_handles_invalid_content(self):
        """Test error handling for invalid input."""
        manager = ConnectionCoordinator(str(self.test_dir))
        
        # Empty content
        connections = manager.discover_connections("", corpus_dir=self.permanent_dir)
        assert connections == []
        
        # None content
        connections = manager.discover_connections(None, corpus_dir=self.permanent_dir)
        assert connections == []


class TestConnectionCoordinatorMetrics:
    """Tests for connection statistics and metrics."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.permanent_dir = self.test_dir / "Permanent Notes"
        self.permanent_dir.mkdir(parents=True)
        
        # Create notes
        (self.permanent_dir / "note1.md").write_text("AI and machine learning")
        (self.permanent_dir / "note2.md").write_text("Deep learning networks")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_get_connection_statistics(self):
        """Test connection statistics generation."""
        manager = ConnectionCoordinator(str(self.test_dir))
        
        # Discover some connections
        target = "Machine learning with neural networks"
        connections = manager.discover_connections(target, corpus_dir=self.permanent_dir)
        
        # Get statistics
        stats = manager.get_connection_statistics()
        
        assert "total_discoveries" in stats
        assert "average_similarity" in stats
        assert stats["total_discoveries"] >= 0
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_clear_connection_cache(self):
        """Test cache clearing functionality."""
        manager = ConnectionCoordinator(str(self.test_dir))
        
        # Load corpus (should cache)
        corpus1 = manager.load_corpus(self.permanent_dir)
        
        # Clear cache
        manager.clear_cache()
        
        # Reload corpus
        corpus2 = manager.load_corpus(self.permanent_dir)
        
        assert corpus1 == corpus2  # Same content but reloaded


class TestConnectionCoordinatorConfiguration:
    """Tests for ConnectionCoordinator configuration."""
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_custom_similarity_threshold(self):
        """Test custom similarity threshold configuration."""
        manager = ConnectionCoordinator(
            ".",
            min_similarity=0.9  # Very high threshold
        )
        
        assert manager.min_similarity == 0.9
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_custom_max_suggestions(self):
        """Test custom max suggestions configuration."""
        manager = ConnectionCoordinator(
            ".",
            max_suggestions=10
        )
        
        assert manager.max_suggestions == 10
    
    @pytest.mark.skipif(ConnectionCoordinator is None, reason="ConnectionCoordinator not implemented yet")
    def test_default_configuration(self):
        """Test default configuration values."""
        manager = ConnectionCoordinator(".")
        
        # Should have sensible defaults
        assert manager.min_similarity > 0.0
        assert manager.max_suggestions > 0
