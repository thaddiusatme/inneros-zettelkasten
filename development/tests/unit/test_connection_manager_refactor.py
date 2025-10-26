"""
RED Phase Tests for ConnectionManager Refactoring

These tests define the expected behavior of ConnectionManager after refactoring.
All tests should FAIL initially (ImportError) - this is the RED phase.

Tests focus on:
- Semantic similarity using embeddings
- Link prediction and suggestion
- Parallel execution opportunities
- Feedback collection for user decisions
"""

import pytest
from unittest.mock import Mock

# This import will FAIL - class doesn't exist yet (RED phase)
from src.ai.connection_manager import ConnectionManager


@pytest.fixture
def mock_base_dir(tmp_path):
    """Create temporary vault structure for testing."""
    vault = tmp_path / "test_vault"
    vault.mkdir()
    (vault / "Inbox").mkdir()
    (vault / "Fleeting Notes").mkdir()
    (vault / "Permanent Notes").mkdir()
    return vault


@pytest.fixture
def sample_config():
    """Standard config for testing."""
    return {
        'connections': {
            'similarity_threshold': 0.7,
            'max_suggestions': 5
        }
    }


@pytest.fixture
def sample_notes(tmp_path):
    """Create sample notes for connection discovery."""
    vault = tmp_path / "test_vault"
    perm_dir = vault / "Permanent Notes"
    perm_dir.mkdir(parents=True, exist_ok=True)

    # Create related notes about machine learning
    (perm_dir / "ml-basics.md").write_text("""---
type: permanent
tags: [machine-learning, basics]
---
# ML Basics
Understanding machine learning fundamentals.
""")

    (perm_dir / "neural-networks.md").write_text("""---
type: permanent
tags: [machine-learning, neural-networks]
---
# Neural Networks
Deep learning and neural network architectures.
""")

    # Create unrelated note
    (perm_dir / "cooking-recipes.md").write_text("""---
type: permanent
tags: [cooking, recipes]
---
# Cooking Recipes
Collection of favorite recipes.
""")

    return vault


class TestConnectionDiscoverySemanticSimilarity:
    """Test connection discovery using semantic embeddings."""

    def test_discover_links_uses_semantic_similarity(
        self, mock_base_dir, sample_config, sample_notes
    ):
        """Test connection discovery uses embedding-based semantic similarity."""
        # Arrange
        mock_embeddings = Mock()
        mock_embeddings.get_similar.return_value = [
            {'note': 'neural-networks.md', 'score': 0.85},
            {'note': 'ml-basics.md', 'score': 0.78}
        ]

        conn = ConnectionManager(mock_base_dir, sample_config, mock_embeddings)

        # Create test note about machine learning
        test_note = sample_notes / "Inbox" / "new-ml-note.md"
        test_note.write_text("# New ML Note\nAbout deep learning algorithms.")

        # Act
        suggestions = conn.discover_links(str(test_note))

        # Assert - Semantic similarity used
        mock_embeddings.get_similar.assert_called_once()

        # Assert - Related notes suggested
        assert len(suggestions) == 2
        assert suggestions[0]['target'] == 'neural-networks.md'
        assert suggestions[0]['score'] == 0.85
        assert suggestions[1]['target'] == 'ml-basics.md'


class TestConnectionLinkPrediction:
    """Test link prediction and suggestion ranking."""

    def test_predict_links_ranks_by_relevance(
        self, mock_base_dir, sample_config
    ):
        """Test link predictions are ranked by relevance score."""
        # Arrange
        mock_embeddings = Mock()
        mock_embeddings.get_similar.return_value = [
            {'note': 'note-a.md', 'score': 0.95},
            {'note': 'note-b.md', 'score': 0.82},
            {'note': 'note-c.md', 'score': 0.65},  # Below threshold
        ]

        conn = ConnectionManager(mock_base_dir, sample_config, mock_embeddings)

        # Act
        predictions = conn.predict_links('test.md')

        # Assert - Filtered by threshold (0.7)
        assert len(predictions) == 2

        # Assert - Sorted by score descending
        assert predictions[0]['score'] > predictions[1]['score']
        assert predictions[0]['target'] == 'note-a.md'
        assert predictions[1]['target'] == 'note-b.md'

        # Assert - Below threshold excluded
        assert not any(p['target'] == 'note-c.md' for p in predictions)


class TestConnectionFeedbackCollection:
    """Test feedback collection for user link decisions."""

    def test_record_link_acceptance_saves_feedback(
        self, mock_base_dir, sample_config
    ):
        """Test user acceptance of link suggestions is recorded."""
        # Arrange
        conn = ConnectionManager(mock_base_dir, sample_config, Mock())

        # Act
        conn.record_link_decision(
            source='note-a.md',
            target='note-b.md',
            accepted=True,
            similarity_score=0.85,
            reason='semantic_similarity'
        )

        # Assert - Feedback stored
        feedback = conn.get_feedback_history()
        assert len(feedback) > 0

        # Assert - Decision recorded correctly
        decision = feedback[0]
        assert decision['source'] == 'note-a.md'
        assert decision['target'] == 'note-b.md'
        assert decision['accepted'] == True
        assert decision['similarity_score'] == 0.85

    def test_record_link_rejection_saves_feedback(
        self, mock_base_dir, sample_config
    ):
        """Test user rejection of link suggestions is recorded."""
        # Arrange
        conn = ConnectionManager(mock_base_dir, sample_config, Mock())

        # Act
        conn.record_link_decision(
            source='note-a.md',
            target='note-c.md',
            accepted=False,
            similarity_score=0.72,
            reason='not_relevant'
        )

        # Assert - Rejection recorded
        feedback = conn.get_feedback_history()
        decision = feedback[0]
        assert decision['accepted'] == False
        assert decision['reason'] == 'not_relevant'


class TestConnectionParallelExecution:
    """Test connection discovery can run in parallel with analytics."""

    def test_discover_links_is_independent_of_analytics(
        self, mock_base_dir, sample_config
    ):
        """Test ConnectionManager has no Analytics dependencies (parallel safe)."""
        # Arrange
        conn = ConnectionManager(mock_base_dir, sample_config, Mock())

        # Assert - No Analytics attributes
        assert not hasattr(conn, 'analytics_manager')
        assert not hasattr(conn, 'quality_score')

        # Assert - __init__ signature verification
        import inspect
        sig = inspect.signature(ConnectionManager.__init__)
        param_names = list(sig.parameters.keys())

        # Should NOT have analytics_manager parameter
        assert 'analytics_manager' not in param_names
        assert 'analytics' not in param_names


class TestConnectionDryRun:
    """Test dry run mode for connection discovery."""

    def test_dry_run_discovers_links_without_writing(
        self, mock_base_dir, sample_config
    ):
        """Test dry_run=True discovers links without writing to files."""
        # Arrange
        mock_embeddings = Mock()
        mock_embeddings.get_similar.return_value = [
            {'note': 'related.md', 'score': 0.88}
        ]

        conn = ConnectionManager(mock_base_dir, sample_config, mock_embeddings)

        # Act
        suggestions = conn.discover_links('test.md', dry_run=True)

        # Assert - Suggestions returned
        assert len(suggestions) > 0

        # Assert - No files written
        # (dry run should not modify any note files)
        feedback_files = list(mock_base_dir.glob('**/*feedback*.json'))
        assert len(feedback_files) == 0


class TestConnectionBidirectionalLinking:
    """Test bidirectional link analysis."""

    def test_analyze_bidirectional_links_detects_orphans(
        self, mock_base_dir, sample_config
    ):
        """Test bidirectional analysis identifies one-way links."""
        # Arrange
        perm_dir = mock_base_dir / "Permanent Notes"
        perm_dir.mkdir(parents=True, exist_ok=True)

        # Note A links to B, but B doesn't link back
        (perm_dir / "note-a.md").write_text("# A\n\n[[note-b]] is related.")
        (perm_dir / "note-b.md").write_text("# B\n\nNo backlink to A.")

        conn = ConnectionManager(mock_base_dir, sample_config, Mock())

        # Act
        analysis = conn.analyze_bidirectional_links()

        # Assert - One-way link detected
        assert 'one_way_links' in analysis
        assert len(analysis['one_way_links']) > 0

        # Assert - Suggestion to add backlink
        one_way = analysis['one_way_links'][0]
        assert one_way['source'] == 'note-a.md'
        assert one_way['target'] == 'note-b.md'
        assert 'suggest_backlink' in one_way or one_way.get('bidirectional') == False
