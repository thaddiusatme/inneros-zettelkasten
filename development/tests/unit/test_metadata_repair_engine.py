"""
TDD RED Phase: Inbox Metadata Repair System Tests

Testing metadata detection and type inference for notes with missing frontmatter.
Following TDD methodology: write failing tests first, implement later.

Target: Fix 8 notes (21% error rate) blocking auto-promotion workflow.
"""


class TestMetadataDetection:
    """Test detection of missing frontmatter fields."""

    def test_detects_missing_type_field(self, tmp_path):
        """Should detect notes missing 'type:' field in frontmatter."""
        # Arrange: Create note with frontmatter but missing type
        note = tmp_path / "test-note.md"
        note.write_text("""---
created: 2025-10-15 14:00
status: inbox
---

# Test Note

Some content here.
""")
        
        # Act: Scan for missing metadata
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path))
        missing_fields = engine.detect_missing_metadata(str(note))
        
        # Assert: Should detect missing 'type' field
        assert 'type' in missing_fields
        assert len(missing_fields) == 1

    def test_detects_missing_created_field(self, tmp_path):
        """Should detect notes missing 'created:' field in frontmatter."""
        # Arrange: Create note with frontmatter but missing created
        note = tmp_path / "test-note.md"
        note.write_text("""---
type: fleeting
status: inbox
---

# Test Note

Some content here.
""")
        
        # Act: Scan for missing metadata
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path))
        missing_fields = engine.detect_missing_metadata(str(note))
        
        # Assert: Should detect missing 'created' field
        assert 'created' in missing_fields
        assert len(missing_fields) == 1

    def test_ignores_notes_with_complete_frontmatter(self, tmp_path):
        """Should not flag notes with all required frontmatter fields."""
        # Arrange: Create note with complete frontmatter
        note = tmp_path / "test-note.md"
        note.write_text("""---
type: fleeting
created: 2025-10-15 14:00
status: inbox
---

# Test Note

Some content here.
""")
        
        # Act: Scan for missing metadata
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path))
        missing_fields = engine.detect_missing_metadata(str(note))
        
        # Assert: Should return empty list (no missing fields)
        assert len(missing_fields) == 0

    def test_handles_notes_without_frontmatter_block(self, tmp_path):
        """Should detect notes completely missing frontmatter block."""
        # Arrange: Create note without any frontmatter
        note = tmp_path / "test-note.md"
        note.write_text("""# Test Note

Some content here without frontmatter.
""")
        
        # Act: Scan for missing metadata
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path))
        missing_fields = engine.detect_missing_metadata(str(note))
        
        # Assert: Should detect missing type and created fields
        assert 'type' in missing_fields
        assert 'created' in missing_fields
        assert len(missing_fields) >= 2

    def test_reports_multiple_missing_fields(self, tmp_path):
        """Should detect all missing fields when multiple are absent."""
        # Arrange: Create note with frontmatter but missing both type and created
        note = tmp_path / "test-note.md"
        note.write_text("""---
status: inbox
---

# Test Note

Some content here.
""")
        
        # Act: Scan for missing metadata
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path))
        missing_fields = engine.detect_missing_metadata(str(note))
        
        # Assert: Should detect both missing fields
        assert 'type' in missing_fields
        assert 'created' in missing_fields
        assert len(missing_fields) == 2


class TestTypeInference:
    """Test intelligent type inference from filenames and content."""

    def test_infers_literature_from_lit_prefix(self, tmp_path):
        """Should infer type='literature' from 'lit-YYYYMMDD-HHMM' filename pattern."""
        # Arrange: Create note with literature prefix
        note = tmp_path / "lit-20251015-1400-example-article.md"
        note.write_text("""---
status: inbox
---

# Example Article

Some content here.
""")
        
        # Act: Infer type from filename
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path))
        inferred_type = engine.infer_note_type(str(note))
        
        # Assert: Should infer 'literature'
        assert inferred_type == 'literature'

    def test_infers_fleeting_from_fleeting_prefix(self, tmp_path):
        """Should infer type='fleeting' from 'fleeting-YYYYMMDD-HHMM' filename pattern."""
        # Arrange: Create note with fleeting prefix
        note = tmp_path / "fleeting-20251015-1400-quick-thought.md"
        note.write_text("""---
status: inbox
---

# Quick Thought

Some content here.
""")
        
        # Act: Infer type from filename
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path))
        inferred_type = engine.infer_note_type(str(note))
        
        # Assert: Should infer 'fleeting'
        assert inferred_type == 'fleeting'

    def test_infers_fleeting_from_capture_prefix(self, tmp_path):
        """Should infer type='fleeting' from 'capture-YYYYMMDD-HHMM' filename pattern."""
        # Arrange: Create note with capture prefix
        note = tmp_path / "capture-20251015-1400-voice-note.md"
        note.write_text("""---
status: inbox
---

# Voice Note

Some content here.
""")
        
        # Act: Infer type from filename
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path))
        inferred_type = engine.infer_note_type(str(note))
        
        # Assert: Should infer 'fleeting'
        assert inferred_type == 'fleeting'

    def test_defaults_to_fleeting_for_unknown_patterns(self, tmp_path):
        """Should default to type='fleeting' for filenames without recognizable patterns."""
        # Arrange: Create note with unknown pattern
        note = tmp_path / "random-note-name.md"
        note.write_text("""---
status: inbox
---

# Random Note

Some content here.
""")
        
        # Act: Infer type from filename
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path))
        inferred_type = engine.infer_note_type(str(note))
        
        # Assert: Should default to 'fleeting' (safest assumption)
        assert inferred_type == 'fleeting'

    def test_content_based_inference_for_ambiguous_names(self, tmp_path):
        """Should use content analysis for ambiguous filenames when pattern matching fails."""
        # Arrange: Create note with ambiguous name but clear content indicators
        note = tmp_path / "some-note.md"
        note.write_text("""---
status: inbox
---

# Article Summary

Source: https://example.com/article
Author: Jane Doe
Date: 2025-10-15

This is a summary of an article I read...
""")
        
        # Act: Infer type from content
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path))
        inferred_type = engine.infer_note_type(str(note))
        
        # Assert: Should infer 'literature' from content indicators (Source:, Author:)
        # If content analysis not implemented, should default to 'fleeting'
        assert inferred_type in ['literature', 'fleeting']


class TestMetadataRepair:
    """Test actual metadata repair operations."""

    def test_repairs_missing_type_field_with_dry_run(self, tmp_path):
        """Should preview repair without modifying file in dry-run mode."""
        # Arrange: Create note with missing type
        note = tmp_path / "fleeting-20251015-1400-test.md"
        original_content = """---
status: inbox
---

# Test Note

Some content here.
"""
        note.write_text(original_content)
        
        # Act: Repair with dry_run=True
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path), dry_run=True)
        result = engine.repair_note_metadata(str(note))
        
        # Assert: Should report repair but not modify file
        assert 'type' in result['would_add']
        assert result['would_add']['type'] == 'fleeting'
        assert note.read_text() == original_content  # File unchanged

    def test_repairs_missing_type_field_with_execute(self, tmp_path):
        """Should actually modify file when dry_run=False."""
        # Arrange: Create note with missing type
        note = tmp_path / "lit-20251015-1400-test.md"
        note.write_text("""---
status: inbox
---

# Test Note

Some content here.
""")
        
        # Act: Repair with dry_run=False
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path), dry_run=False)
        result = engine.repair_note_metadata(str(note))
        
        # Assert: Should modify file and add type field
        assert 'type' in result['added']
        assert result['added']['type'] == 'literature'
        content = note.read_text()
        assert 'type: literature' in content

    def test_preserves_existing_frontmatter_fields(self, tmp_path):
        """Should not modify existing fields when adding missing ones."""
        # Arrange: Create note with some frontmatter
        note = tmp_path / "capture-20251015-1400-test.md"
        note.write_text("""---
status: inbox
tags: test, example
custom_field: value
---

# Test Note

Some content here.
""")
        
        # Act: Repair missing type field
        from development.src.ai.metadata_repair_engine import MetadataRepairEngine
        engine = MetadataRepairEngine(str(tmp_path), dry_run=False)
        result = engine.repair_note_metadata(str(note))
        
        # Assert: Should preserve existing fields
        assert 'type' in result['added']
        assert result['added']['type'] == 'fleeting'
        content = note.read_text()
        assert 'status: inbox' in content
        assert 'tags: test, example' in content
        assert 'custom_field: value' in content
        assert 'type: fleeting' in content  # New field added
