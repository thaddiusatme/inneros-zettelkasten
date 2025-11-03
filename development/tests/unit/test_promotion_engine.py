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
from unittest.mock import Mock, patch
import sys

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.promotion_engine import PromotionEngine
from src.ai.note_lifecycle_manager import NoteLifecycleManager
from src.utils.frontmatter import parse_frontmatter


class TestPromotionEngineInitialization:
    """Test PromotionEngine initialization and configuration."""

    def test_initialization_with_required_dependencies(self, tmp_path):
        """Test PromotionEngine initializes with base_dir and lifecycle_manager."""
        # Arrange
        lifecycle_manager = Mock(spec=NoteLifecycleManager)

        # Act - Pass root directory (vault config will add knowledge/)
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Assert - Should use vault config paths (knowledge/Inbox, etc.)
        assert engine.base_dir == tmp_path
        assert engine.lifecycle_manager == lifecycle_manager
        assert "knowledge" in str(engine.inbox_dir)
        assert "knowledge" in str(engine.permanent_dir)
        assert "knowledge" in str(engine.literature_dir)
        assert "knowledge" in str(engine.fleeting_dir)

    def test_initialization_creates_target_directories(self, tmp_path):
        """Test that PromotionEngine ensures target directories exist."""
        # Arrange
        lifecycle_manager = Mock(spec=NoteLifecycleManager)

        # Act - Pass root directory
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Assert - directories should be created during initialization (in knowledge/)
        assert engine.permanent_dir.exists()
        assert engine.literature_dir.exists()
        assert engine.fleeting_dir.exists()

    def test_initialization_with_optional_config(self, tmp_path):
        """Test PromotionEngine accepts optional configuration."""
        # Arrange
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        config = {"default_quality_threshold": 0.8, "auto_summarize": True}

        # Act - Pass root directory
        engine = PromotionEngine(tmp_path, lifecycle_manager, config=config)

        # Assert
        assert engine.config["default_quality_threshold"] == 0.8
        assert engine.config["auto_summarize"] is True


class TestSingleNotePromotion:
    """Test single note promotion functionality."""

    def test_promote_note_to_permanent(self, tmp_path):
        """Test promoting a single note to permanent directory."""
        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        inbox_dir = config.inbox_dir
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

        # Use real NoteLifecycleManager for actual file operations
        lifecycle_manager = NoteLifecycleManager(tmp_path)
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        result = engine.promote_note(str(note_path), target_type="permanent")

        # Assert
        assert result["success"] is True
        assert result["type"] == "permanent"
        assert not note_path.exists()  # Source removed
        target_path = config.permanent_dir / "test-note.md"
        assert target_path.exists()  # Target created

        # Verify metadata updated
        target_content = target_path.read_text()
        metadata, _ = parse_frontmatter(target_content)
        assert metadata["type"] == "permanent"
        assert metadata["status"] == "promoted"
        assert "promoted_date" in metadata

    def test_promote_note_to_literature(self, tmp_path):
        """Test promoting a note with source URL to literature directory."""
        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        inbox_dir = config.inbox_dir
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

        # Use real NoteLifecycleManager for actual file operations
        lifecycle_manager = NoteLifecycleManager(tmp_path)
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        result = engine.promote_note(str(note_path), target_type="literature")

        # Assert
        assert result["success"] is True
        assert result["type"] == "literature"
        target_path = config.literature_dir / "lit-note.md"
        assert target_path.exists()

    def test_promote_note_handles_missing_file(self, tmp_path):
        """Test that promotion handles missing source file gracefully."""
        # Arrange
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        result = engine.promote_note("/nonexistent/note.md", target_type="permanent")

        # Assert
        assert "error" in result
        assert "not found" in result["error"].lower()


class TestBatchPromotion:
    """Test batch promotion functionality."""

    def test_promote_fleeting_notes_batch_with_quality_threshold(self, tmp_path):
        """Test batch promotion of fleeting notes above quality threshold."""
        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        fleeting_dir = config.fleeting_dir
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
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        result = engine.promote_fleeting_notes_batch(quality_threshold=0.7)

        # Assert
        assert result["batch_mode"] is True
        assert len(result["promoted_notes"]) == 3  # Only high-quality notes
        assert result["processing_time"] > 0

    def test_batch_promotion_preview_mode(self, tmp_path):
        """Test batch promotion in preview mode (dry-run)."""
        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        fleeting_dir = config.fleeting_dir
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
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        result = engine.promote_fleeting_notes_batch(preview_mode=True)

        # Assert
        assert result["preview_mode"] is True
        assert note_path.exists()  # File not moved in preview
        assert len(result["promoted_notes"]) > 0  # Preview shows what would be promoted

    def test_batch_promotion_creates_single_backup(self, tmp_path):
        """Test that batch promotion creates one backup for entire batch."""
        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        fleeting_dir = config.fleeting_dir
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
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        with patch(
            "src.utils.directory_organizer.DirectoryOrganizer"
        ) as mock_organizer:
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
        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        inbox_dir = config.inbox_dir
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

        # Use real NoteLifecycleManager for actual file operations
        lifecycle_manager = NoteLifecycleManager(tmp_path)
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        result = engine.auto_promote_ready_notes(quality_threshold=0.7)

        # Assert
        assert result["total_candidates"] == 3
        assert result["promoted_count"] == 1  # Only high-quality note
        assert result["skipped_count"] == 2

    def test_auto_promote_dry_run_mode(self, tmp_path):
        """Test auto-promotion in dry-run mode."""
        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        inbox_dir = config.inbox_dir
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
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        result = engine.auto_promote_ready_notes(dry_run=True)

        # Assert
        assert result["dry_run"] is True
        assert "would_promote_count" in result
        assert "preview" in result
        assert note_path.exists()  # File not moved

    def test_auto_promote_tracks_by_type(self, tmp_path):
        """Test auto-promotion tracks statistics by note type."""
        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        inbox_dir = config.inbox_dir
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

        # Use real NoteLifecycleManager for actual file operations
        lifecycle_manager = NoteLifecycleManager(tmp_path)
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        result = engine.auto_promote_ready_notes(quality_threshold=0.7)

        # Assert
        assert "by_type" in result
        assert result["by_type"]["permanent"]["promoted"] == 1
        assert result["by_type"]["literature"]["promoted"] == 1
        assert result["by_type"]["fleeting"]["promoted"] == 1

    def test_auto_promote_scans_subdirectories(self, tmp_path):
        """
        RED PHASE TEST: Auto-promotion should scan subdirectories recursively.

        This test validates that notes in Inbox/YouTube/ (or any subdirectory)
        are included in auto-promotion candidates. Current implementation uses
        glob("*.md") which only scans root Inbox/, missing 17 YouTube notes.

        Expected to FAIL until glob() is replaced with rglob() in GREEN phase.
        """
        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        inbox_dir = config.inbox_dir
        youtube_dir = inbox_dir / "YouTube"
        youtube_dir.mkdir(parents=True)

        # Create root-level note (should be found with current implementation)
        root_note = """---
type: fleeting
status: promoted
quality_score: 0.8
---

# Root Level Note
"""
        (inbox_dir / "root-note.md").write_text(root_note)

        # Create subdirectory notes (SHOULD be found, but currently MISSED)
        subdirectory_notes = [
            ("youtube-1.md", "literature", 0.85),
            ("youtube-2.md", "literature", 0.75),
            ("youtube-3.md", "fleeting", 0.80),
        ]

        for filename, note_type, quality in subdirectory_notes:
            content = f"""---
type: {note_type}
status: promoted
quality_score: {quality}
---

# {filename}
"""
            (youtube_dir / filename).write_text(content)

        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        result = engine.auto_promote_ready_notes(dry_run=True, quality_threshold=0.7)

        # Assert - Should find ALL 4 notes (1 root + 3 subdirectory)
        assert result["total_candidates"] == 4, (
            f"Expected 4 candidates (1 root + 3 subdirectory), "
            f"got {result['total_candidates']}. "
            "Current implementation only scans root Inbox/, missing subdirectories."
        )
        assert (
            result["would_promote_count"] == 4
        ), f"Expected 4 promotions, got {result['would_promote_count']}"

        # Verify preview includes subdirectory notes
        assert len(result["preview"]) == 4
        preview_notes = [note["note"] for note in result["preview"]]
        assert "root-note.md" in preview_notes
        assert "youtube-1.md" in preview_notes
        assert "youtube-2.md" in preview_notes
        assert "youtube-3.md" in preview_notes


class TestPromotionValidation:
    """Test promotion validation logic."""

    def test_validate_note_for_promotion_checks_quality(self, tmp_path):
        """Test validation rejects notes below quality threshold."""
        # Arrange
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        note_path = tmp_path / "test.md"
        frontmatter = {"type": "permanent", "quality_score": 0.5}

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
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(tmp_path, lifecycle_manager)

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
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        note_path = tmp_path / "test.md"
        frontmatter = {"type": "permanent", "quality_score": 0.85}

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

        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        inbox_dir = config.inbox_dir
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
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        result = engine.promote_fleeting_note(str(note_path))

        # Assert
        assert "promoted_notes" in result
        assert result["batch_mode"] is False

    def test_promotion_engine_integrates_with_directory_organizer(self, tmp_path):
        """Test PromotionEngine uses DirectoryOrganizer for safe operations."""
        # Arrange - Use vault config paths
        from src.config.vault_config_loader import get_vault_config
        
        config = get_vault_config(str(tmp_path))
        fleeting_dir = config.fleeting_dir
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
        engine = PromotionEngine(tmp_path, lifecycle_manager)

        # Act
        with patch(
            "src.utils.directory_organizer.DirectoryOrganizer"
        ) as mock_organizer:
            mock_instance = Mock()
            mock_instance.create_backup.return_value = Path("/backup/path")
            mock_organizer.return_value = mock_instance

            result = engine.promote_fleeting_note(str(note_path))

            # Assert
            assert result["backup_created"] is True
            mock_organizer.assert_called_once()


class TestVaultConfigIntegration:
    """Test PromotionEngine integration with vault configuration."""

    def test_promotion_engine_uses_vault_config_for_directories(self, tmp_path):
        """
        RED PHASE: Verify PromotionEngine uses vault config for directory paths.
        
        This test validates that PromotionEngine gets directory paths from
        vault_config.yaml (knowledge/Inbox) instead of hardcoded paths (Inbox/).
        
        Expected to FAIL until GREEN phase replaces hardcoded paths with config.
        """
        # Arrange
        from src.config.vault_config_loader import get_vault_config
        
        base_dir = tmp_path / "knowledge"
        base_dir.mkdir()
        
        # Get expected paths from vault config
        config = get_vault_config(str(tmp_path))
        
        lifecycle_manager = Mock(spec=NoteLifecycleManager)
        engine = PromotionEngine(tmp_path, lifecycle_manager)
        
        # Act & Assert - Should use knowledge/Inbox, not root-level Inbox
        assert "knowledge" in str(engine.inbox_dir), (
            f"Expected inbox_dir to contain 'knowledge', got {engine.inbox_dir}"
        )
        assert engine.inbox_dir == config.inbox_dir, (
            f"Expected {config.inbox_dir}, got {engine.inbox_dir}"
        )
        assert engine.permanent_dir == config.permanent_dir, (
            f"Expected {config.permanent_dir}, got {engine.permanent_dir}"
        )
        assert engine.literature_dir == config.literature_dir, (
            f"Expected {config.literature_dir}, got {engine.literature_dir}"
        )
        assert engine.fleeting_dir == config.fleeting_dir, (
            f"Expected {config.fleeting_dir}, got {engine.fleeting_dir}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
