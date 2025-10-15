"""
Unit tests for PromotionEngine.

RED Phase - ADR-002 Phase 4: PromotionEngine Extraction
All tests expected to FAIL until GREEN phase implementation.

Test Coverage:
- Initialization and configuration
- Single note promotion
- Batch promotion
- Auto-promotion with quality thresholds
- Validation logic
- Integration with WorkflowManager
- Error handling and edge cases
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
import sys

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.promotion_engine import PromotionEngine
from src.ai.note_lifecycle_manager import NoteLifecycleManager
from src.utils.frontmatter import parse_frontmatter, build_frontmatter


class TestPromotionEngineInitialization:
    """Test PromotionEngine initialization and configuration."""
    
    def test_initialization_with_required_dependencies(self, tmp_path):
        """Test PromotionEngine initializes with base_dir and lifecycle_manager."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        
        # Act
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Assert
        assert engine.base_dir == base_dir
        assert engine.lifecycle_manager == lifecycle_manager
        assert engine.inbox_dir == base_dir / "Inbox"
        assert engine.permanent_dir == base_dir / "Permanent Notes"
        assert engine.literature_dir == base_dir / "Literature Notes"
        assert engine.fleeting_dir == base_dir / "Fleeting Notes"
    
    def test_initialization_creates_target_directories(self, tmp_path):
        """Test that PromotionEngine ensures target directories exist."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        
        # Act
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Assert - directories should be created during initialization
        assert (base_dir / "Permanent Notes").exists()
        assert (base_dir / "Literature Notes").exists()
        assert (base_dir / "Fleeting Notes").exists()
    
    def test_initialization_with_optional_config(self, tmp_path):
        """Test PromotionEngine accepts optional configuration."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        config = {
            "default_quality_threshold": 0.8,
            "auto_summarize": True
        }
        
        # Act
        engine = PromotionEngine(base_dir, lifecycle_manager, config=config)
        
        # Assert
        assert engine.config["default_quality_threshold"] == 0.8
        assert engine.config["auto_summarize"] is True


class TestSingleNotePromotion:
    """Test single note promotion functionality."""
    
    def test_promote_note_to_permanent(self, tmp_path):
        """Test promoting a single note to permanent directory."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        inbox_dir = base_dir / "Inbox"
        inbox_dir.mkdir(parents=True)
        
        note_content = """---
type: fleeting
status: inbox
quality_score: 0.85
---

# Test Note
This is a test note ready for promotion.
"""
        note_path = inbox_dir / "test-note.md"
        note_path.write_text(note_content)
        
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        result = engine.promote_note(str(note_path), target_type="permanent")
        
        # Assert
        assert result["success"] is True
        assert result["type"] == "permanent"
        assert not note_path.exists()  # Source removed
        target_path = base_dir / "Permanent Notes" / "test-note.md"
        assert target_path.exists()  # Target created
        
        # Verify metadata updated
        target_content = target_path.read_text()
        metadata, _ = parse_frontmatter(target_content)
        assert metadata["type"] == "permanent"
        assert metadata["status"] == "promoted"
        assert "promoted_date" in metadata
    
    def test_promote_note_to_literature(self, tmp_path):
        """Test promoting a note with source URL to literature directory."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        inbox_dir = base_dir / "Inbox"
        inbox_dir.mkdir(parents=True)
        
        note_content = """---
type: fleeting
status: inbox
quality_score: 0.75
source: https://example.com/article
---

# Literature Note
Content from external source.
"""
        note_path = inbox_dir / "lit-note.md"
        note_path.write_text(note_content)
        
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        result = engine.promote_note(str(note_path), target_type="literature")
        
        # Assert
        assert result["success"] is True
        assert result["type"] == "literature"
        target_path = base_dir / "Literature Notes" / "lit-note.md"
        assert target_path.exists()
    
    def test_promote_note_handles_missing_file(self, tmp_path):
        """Test that promotion handles missing source file gracefully."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        result = engine.promote_note("/nonexistent/note.md", target_type="permanent")
        
        # Assert
        assert "error" in result
        assert "not found" in result["error"].lower()


class TestBatchPromotion:
    """Test batch promotion functionality."""
    
    def test_promote_fleeting_notes_batch_with_quality_threshold(self, tmp_path):
        """Test batch promotion of fleeting notes above quality threshold."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        fleeting_dir = base_dir / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        # Create 3 high-quality notes and 2 low-quality notes
        for i in range(5):
            quality = 0.8 if i < 3 else 0.5  # First 3 are high quality
            note_content = f"""---
type: fleeting
status: inbox
quality_score: {quality}
---

# Note {i}
Content here.
"""
            note_path = fleeting_dir / f"note-{i}.md"
            note_path.write_text(note_content)
        
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        result = engine.promote_fleeting_notes_batch(quality_threshold=0.7)
        
        # Assert
        assert result["batch_mode"] is True
        assert len(result["promoted_notes"]) == 3  # Only high-quality notes
        assert result["processing_time"] > 0
    
    def test_batch_promotion_preview_mode(self, tmp_path):
        """Test batch promotion in preview mode (dry-run)."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        fleeting_dir = base_dir / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        note_content = """---
type: fleeting
status: inbox
quality_score: 0.85
---

# Test Note
"""
        note_path = fleeting_dir / "test.md"
        note_path.write_text(note_content)
        
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        result = engine.promote_fleeting_notes_batch(preview_mode=True)
        
        # Assert
        assert result["preview_mode"] is True
        assert note_path.exists()  # File not moved in preview
        assert len(result["promoted_notes"]) > 0  # Preview shows what would be promoted
    
    def test_batch_promotion_creates_single_backup(self, tmp_path):
        """Test that batch promotion creates one backup for entire batch."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        fleeting_dir = base_dir / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        # Create 2 notes
        for i in range(2):
            note_content = f"""---
type: fleeting
quality_score: 0.85
---

# Note {i}
"""
            (fleeting_dir / f"note-{i}.md").write_text(note_content)
        
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        with patch('src.utils.directory_organizer.DirectoryOrganizer') as mock_organizer:
            mock_instance = Mock()
            mock_instance.create_backup.return_value = Path("/backup/path")
            mock_organizer.return_value = mock_instance
            
            result = engine.promote_fleeting_notes_batch()
            
            # Assert
            assert result["backup_created"] is True
            # Verify backup created only once, not per note
            assert mock_instance.create_backup.call_count == 1


class TestAutoPromotion:
    """Test auto-promotion functionality."""
    
    def test_auto_promote_ready_notes_scans_inbox(self, tmp_path):
        """Test auto-promotion scans inbox for eligible notes."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        inbox_dir = base_dir / "Inbox"
        inbox_dir.mkdir(parents=True)
        
        # Create notes with various quality scores
        notes_data = [
            ("high-quality.md", 0.85, "permanent"),
            ("medium-quality.md", 0.65, "fleeting"),
            ("low-quality.md", 0.4, "fleeting"),
        ]
        
        for filename, quality, note_type in notes_data:
            content = f"""---
type: {note_type}
status: inbox
quality_score: {quality}
---

# {filename}
"""
            (inbox_dir / filename).write_text(content)
        
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        result = engine.auto_promote_ready_notes(quality_threshold=0.7)
        
        # Assert
        assert result["total_candidates"] == 3
        assert result["promoted_count"] == 1  # Only high-quality note
        assert result["skipped_count"] == 2
    
    def test_auto_promote_dry_run_mode(self, tmp_path):
        """Test auto-promotion in dry-run mode."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        inbox_dir = base_dir / "Inbox"
        inbox_dir.mkdir(parents=True)
        
        note_content = """---
type: permanent
status: inbox
quality_score: 0.85
---

# Test
"""
        note_path = inbox_dir / "test.md"
        note_path.write_text(note_content)
        
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        result = engine.auto_promote_ready_notes(dry_run=True)
        
        # Assert
        assert result["dry_run"] is True
        assert "would_promote_count" in result
        assert "preview" in result
        assert note_path.exists()  # File not moved
    
    def test_auto_promote_tracks_by_type(self, tmp_path):
        """Test auto-promotion tracks statistics by note type."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        inbox_dir = base_dir / "Inbox"
        inbox_dir.mkdir(parents=True)
        
        # Create notes of different types
        types_data = [
            ("perm-1.md", "permanent", 0.85),
            ("lit-1.md", "literature", 0.80),
            ("fleet-1.md", "fleeting", 0.75),
        ]
        
        for filename, note_type, quality in types_data:
            content = f"""---
type: {note_type}
status: inbox
quality_score: {quality}
---

# {filename}
"""
            (inbox_dir / filename).write_text(content)
        
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        result = engine.auto_promote_ready_notes(quality_threshold=0.7)
        
        # Assert
        assert "by_type" in result
        assert result["by_type"]["permanent"]["promoted"] == 1
        assert result["by_type"]["literature"]["promoted"] == 1
        assert result["by_type"]["fleeting"]["promoted"] == 1


class TestPromotionValidation:
    """Test promotion validation logic."""
    
    def test_validate_note_for_promotion_checks_quality(self, tmp_path):
        """Test validation rejects notes below quality threshold."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        note_path = tmp_path / "test.md"
        frontmatter = {
            "type": "permanent",
            "quality_score": 0.5
        }
        
        # Act
        is_valid, note_type, error_msg = engine._validate_note_for_promotion(
            note_path, frontmatter, quality_threshold=0.7
        )
        
        # Assert
        assert is_valid is False
        assert "quality" in error_msg.lower()
        assert "threshold" in error_msg.lower()
    
    def test_validate_note_requires_type_field(self, tmp_path):
        """Test validation requires 'type' field in frontmatter."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        note_path = tmp_path / "test.md"
        frontmatter = {"quality_score": 0.85}  # Missing 'type'
        
        # Act
        is_valid, note_type, error_msg = engine._validate_note_for_promotion(
            note_path, frontmatter, quality_threshold=0.7
        )
        
        # Assert
        assert is_valid is False
        assert note_type is None
        assert "type" in error_msg.lower()
    
    def test_validate_note_accepts_valid_note(self, tmp_path):
        """Test validation passes for valid note."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        note_path = tmp_path / "test.md"
        frontmatter = {
            "type": "permanent",
            "quality_score": 0.85
        }
        
        # Act
        is_valid, note_type, error_msg = engine._validate_note_for_promotion(
            note_path, frontmatter, quality_threshold=0.7
        )
        
        # Assert
        assert is_valid is True
        assert note_type == "permanent"
        assert error_msg is None


class TestPromotionEngineIntegration:
    """Test PromotionEngine integration with WorkflowManager."""
    
    def test_workflow_manager_delegates_to_promotion_engine(self, tmp_path):
        """Test WorkflowManager uses PromotionEngine via composition."""
        # This test will verify integration after GREEN phase implementation
        # For now, we're testing the interface we expect
        
        # Arrange
        base_dir = tmp_path / "knowledge"
        inbox_dir = base_dir / "Inbox"
        inbox_dir.mkdir(parents=True)
        
        note_content = """---
type: fleeting
status: inbox
quality_score: 0.85
---

# Test Note
"""
        note_path = inbox_dir / "test.md"
        note_path.write_text(note_content)
        
        # This will be implemented in GREEN phase
        # For now, just testing the expected interface exists
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        result = engine.promote_fleeting_note(str(note_path))
        
        # Assert
        assert "promoted_notes" in result
        assert result["batch_mode"] is False
    
    def test_promotion_engine_integrates_with_directory_organizer(self, tmp_path):
        """Test PromotionEngine uses DirectoryOrganizer for safe operations."""
        # Arrange
        base_dir = tmp_path / "knowledge"
        fleeting_dir = base_dir / "Fleeting Notes"
        fleeting_dir.mkdir(parents=True)
        
        note_content = """---
type: fleeting
quality_score: 0.85
---

# Test
"""
        note_path = fleeting_dir / "test.md"
        note_path.write_text(note_content)
        
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(base_dir, lifecycle_manager)
        
        # Act
        with patch('src.utils.directory_organizer.DirectoryOrganizer') as mock_organizer:
            mock_instance = Mock()
            mock_instance.create_backup.return_value = Path("/backup/path")
            mock_organizer.return_value = mock_instance
            
            result = engine.promote_fleeting_note(str(note_path))
            
            # Assert
            assert result["backup_created"] is True
            mock_organizer.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
