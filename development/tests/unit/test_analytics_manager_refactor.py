"""
RED Phase Tests for AnalyticsManager Refactoring

These tests define the expected behavior of AnalyticsManager after refactoring.
All tests should FAIL initially (ImportError) - this is the RED phase.

Tests focus on:
- Pure metrics calculation (NO AI dependencies)
- Exception raising (ValueError, FileNotFoundError)
- Quality score calculation
- Orphaned and stale note detection
- Workflow report generation
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# This import will FAIL - class doesn't exist yet (RED phase)
from src.ai.analytics_manager import AnalyticsManager


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
        'quality_thresholds': {
            'excellent': 0.8,
            'good': 0.6,
            'needs_improvement': 0.4
        }
    }


@pytest.fixture
def sample_note_with_quality(tmp_path):
    """Create a sample note with known quality metrics."""
    note_path = tmp_path / "test_vault" / "Inbox" / "quality-note.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = """---
type: fleeting
created: 2025-10-01 10:00
status: inbox
tags: [test, refactoring, architecture]
---

# Quality Test Note

This is a sample note with exactly 500 words of content for quality assessment.
It has multiple [[wiki-link-1]] and [[wiki-link-2]] demonstrating proper structure.

""" + " ".join(["word"] * 490)  # Pad to ~500 words
    
    note_path.write_text(content)
    return note_path


class TestAnalyticsQualityAssessment:
    """Test Analytics quality score calculation."""
    
    def test_assess_quality_calculates_correct_score(
        self, mock_base_dir, sample_config, sample_note_with_quality
    ):
        """Test quality score calculation with known metrics."""
        # Arrange
        analytics = AnalyticsManager(mock_base_dir, sample_config)
        
        # Act
        result = analytics.assess_quality(str(sample_note_with_quality))
        
        # Assert - Quality score in good range (has tags, links, frontmatter, content)
        assert result['success'] == True
        assert 'quality_score' in result
        assert 0.7 <= result['quality_score'] <= 0.9
        
        # Assert - Metrics calculated correctly
        assert result['word_count'] >= 490
        assert result['tag_count'] == 3
        assert result['link_count'] == 2
        assert result['has_frontmatter'] == True


class TestAnalyticsExceptionHandling:
    """Test Analytics raises appropriate exceptions."""
    
    def test_assess_quality_raises_value_error_on_empty_path(
        self, mock_base_dir, sample_config
    ):
        """Test Analytics raises ValueError on empty note_path."""
        # Arrange
        analytics = AnalyticsManager(mock_base_dir, sample_config)
        
        # Act & Assert
        with pytest.raises(ValueError, match="note_path cannot be empty"):
            analytics.assess_quality('')
    
    def test_assess_quality_raises_file_not_found_on_missing_note(
        self, mock_base_dir, sample_config
    ):
        """Test Analytics raises FileNotFoundError on missing note."""
        # Arrange
        analytics = AnalyticsManager(mock_base_dir, sample_config)
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            analytics.assess_quality('nonexistent.md')


class TestAnalyticsOrphanedNoteDetection:
    """Test Analytics orphaned note detection."""
    
    def test_detect_orphaned_notes_builds_link_graph(
        self, mock_base_dir, sample_config
    ):
        """Test orphaned note detection builds link graph from wiki-links."""
        # Arrange
        # Create 5 notes: 2 connected, 3 orphaned
        notes_dir = mock_base_dir / "Permanent Notes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        
        # Connected notes
        (notes_dir / "note-a.md").write_text("# Note A\n\n[[note-b]] is related.")
        (notes_dir / "note-b.md").write_text("# Note B\n\n[[note-a]] is related.")
        
        # Orphaned notes (no links)
        (notes_dir / "orphan-1.md").write_text("# Orphan 1\n\nNo links here.")
        (notes_dir / "orphan-2.md").write_text("# Orphan 2\n\nIsolated note.")
        (notes_dir / "orphan-3.md").write_text("# Orphan 3\n\nAlone.")
        
        analytics = AnalyticsManager(mock_base_dir, sample_config)
        
        # Act
        orphans = analytics.detect_orphaned_notes()
        
        # Assert - 3 orphaned notes detected
        assert len(orphans) == 3
        
        # Assert - Orphan names present
        orphan_names = [o['note'] for o in orphans]
        assert 'orphan-1.md' in orphan_names
        assert 'orphan-2.md' in orphan_names
        assert 'orphan-3.md' in orphan_names
        
        # Assert - Connected notes NOT in orphans
        assert 'note-a.md' not in orphan_names
        assert 'note-b.md' not in orphan_names


class TestAnalyticsStaleNoteDetection:
    """Test Analytics stale note detection."""
    
    def test_detect_stale_notes_checks_modification_time(
        self, mock_base_dir, sample_config
    ):
        """Test stale note detection based on modification time."""
        # Arrange
        notes_dir = mock_base_dir / "Fleeting Notes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        
        # Create recent note
        recent_note = notes_dir / "recent.md"
        recent_note.write_text("# Recent Note")
        
        # Create stale note (simulate old modification time)
        stale_note = notes_dir / "stale.md"
        stale_note.write_text("# Stale Note")
        
        # Simulate stale note being >90 days old
        old_time = (datetime.now() - timedelta(days=100)).timestamp()
        import os
        os.utime(stale_note, (old_time, old_time))
        
        analytics = AnalyticsManager(mock_base_dir, sample_config)
        
        # Act
        stale_notes = analytics.detect_stale_notes(days_threshold=90)
        
        # Assert - Stale note detected
        assert len(stale_notes) >= 1
        
        # Assert - Stale note has correct metadata
        stale_paths = [s['note'] for s in stale_notes]
        assert 'stale.md' in stale_paths
        
        # Find the stale note entry
        stale_entry = next(s for s in stale_notes if 'stale.md' in s['note'])
        assert stale_entry['days_since_modified'] > 90


class TestAnalyticsWorkflowReporting:
    """Test Analytics workflow report generation."""
    
    def test_generate_workflow_report_aggregates_metrics(
        self, mock_base_dir, sample_config
    ):
        """Test workflow report aggregates metrics across vault."""
        # Arrange
        # Create mixed note types
        inbox_dir = mock_base_dir / "Inbox"
        fleeting_dir = mock_base_dir / "Fleeting Notes"
        permanent_dir = mock_base_dir / "Permanent Notes"
        
        for dir in [inbox_dir, fleeting_dir, permanent_dir]:
            dir.mkdir(parents=True, exist_ok=True)
        
        # Create notes in different stages
        (inbox_dir / "inbox-1.md").write_text("---\ntype: fleeting\nstatus: inbox\n---\n# Inbox 1")
        (inbox_dir / "inbox-2.md").write_text("---\ntype: fleeting\nstatus: inbox\n---\n# Inbox 2")
        (fleeting_dir / "fleeting-1.md").write_text("---\ntype: fleeting\nstatus: promoted\n---\n# Fleeting 1")
        (permanent_dir / "permanent-1.md").write_text("---\ntype: permanent\nstatus: published\n---\n# Permanent 1")
        
        analytics = AnalyticsManager(mock_base_dir, sample_config)
        
        # Act
        report = analytics.generate_workflow_report()
        
        # Assert - Total notes counted
        assert report['total_notes'] >= 4
        
        # Assert - Notes by type aggregated
        assert 'notes_by_type' in report
        assert report['notes_by_type'].get('fleeting', 0) >= 3
        assert report['notes_by_type'].get('permanent', 0) >= 1
        
        # Assert - Notes by status aggregated
        assert 'notes_by_status' in report
        assert report['notes_by_status'].get('inbox', 0) >= 2
        assert report['notes_by_status'].get('promoted', 0) >= 1


class TestAnalyticsReviewCandidates:
    """Test Analytics review candidate identification."""
    
    def test_scan_review_candidates_identifies_promotion_ready(
        self, mock_base_dir, sample_config
    ):
        """Test scan identifies high-quality fleeting notes for promotion."""
        # Arrange
        fleeting_dir = mock_base_dir / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True, exist_ok=True)
        
        # High-quality fleeting note (many tags, links, content)
        high_quality = fleeting_dir / "high-quality.md"
        high_quality.write_text("""---
type: fleeting
status: promoted
tags: [tag1, tag2, tag3, tag4, tag5]
---

# High Quality Note

This note has substantial content with many [[link-1]] and [[link-2]] and [[link-3]].

""" + " ".join(["word"] * 400))
        
        # Low-quality fleeting note (minimal content)
        low_quality = fleeting_dir / "low-quality.md"
        low_quality.write_text("---\ntype: fleeting\n---\n# Low\n\nShort.")
        
        analytics = AnalyticsManager(mock_base_dir, sample_config)
        
        # Act
        candidates = analytics.scan_review_candidates()
        
        # Assert - High-quality note appears in candidates
        candidate_paths = [c['note'] for c in candidates]
        assert any('high-quality.md' in p for p in candidate_paths)


class TestAnalyticsAIDependencies:
    """Test Analytics has NO AI dependencies (architecture verification)."""
    
    def test_analytics_has_no_ai_dependencies(
        self, mock_base_dir, sample_config
    ):
        """Test AnalyticsManager does NOT accept or use AI components."""
        # Arrange & Act
        analytics = AnalyticsManager(mock_base_dir, sample_config)
        
        # Assert - No AI-related attributes
        assert not hasattr(analytics, 'ai_tagger')
        assert not hasattr(analytics, 'ai_enhancer')
        assert not hasattr(analytics, 'ai_summarizer')
        
        # Assert - __init__ signature verification
        import inspect
        sig = inspect.signature(AnalyticsManager.__init__)
        param_names = list(sig.parameters.keys())
        
        # Should only have: self, base_dir, config
        # NOT: tagger, enhancer, summarizer, or any AI components
        assert 'tagger' not in param_names
        assert 'enhancer' not in param_names
        assert 'summarizer' not in param_names
        assert 'ai_tagger' not in param_names
        assert 'ai_enhancer' not in param_names
