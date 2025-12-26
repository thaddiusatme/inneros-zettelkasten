"""
ADR-002 Phase 6: NoteProcessingCoordinator Tests

RED Phase: Comprehensive test suite for note processing extraction.

This coordinator handles:
- AI-powered note processing (tagging, quality scoring, connections)
- Template placeholder fixing and preprocessing
- Fast mode processing with heuristics
- Dry-run and safe file operations
"""

import pytest
from unittest.mock import Mock
from src.ai.note_processing_coordinator import NoteProcessingCoordinator


class TestNoteProcessingCoordinatorInitialization:
    """Test coordinator initialization and configuration."""

    def test_initialization_with_ai_components(self):
        """Test coordinator initializes with all AI components."""
        coordinator = NoteProcessingCoordinator(
            tagger=Mock(),
            summarizer=Mock(),
            enhancer=Mock(),
            connection_coordinator=Mock(),
        )

        assert coordinator.tagger is not None
        assert coordinator.summarizer is not None
        assert coordinator.enhancer is not None
        assert coordinator.connection_coordinator is not None

    def test_initialization_with_config(self):
        """Test coordinator accepts custom configuration."""
        config = {
            "auto_tag_inbox": False,
            "min_words_for_summary": 300,
            "max_tags_per_note": 5,
        }

        coordinator = NoteProcessingCoordinator(
            tagger=Mock(),
            summarizer=Mock(),
            enhancer=Mock(),
            connection_coordinator=Mock(),
            config=config,
        )

        assert coordinator.config["auto_tag_inbox"] == False
        assert coordinator.config["min_words_for_summary"] == 300
        assert coordinator.config["max_tags_per_note"] == 5


class TestNoteProcessingCore:
    """Test core note processing functionality."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator with mocked AI components."""
        tagger = Mock()
        tagger.generate_tags = Mock(return_value=["ai-generated", "test-tag"])

        enhancer = Mock()
        enhancer.enhance_note = Mock(
            return_value={
                "quality_score": 0.75,
                "suggestions": ["Add more detail", "Include examples"],
            }
        )

        connection_coordinator = Mock()
        connection_coordinator.discover_connections = Mock(
            return_value=[{"filename": "related-note.md", "similarity": 0.85}]
        )

        return NoteProcessingCoordinator(
            tagger=tagger,
            summarizer=Mock(),
            enhancer=enhancer,
            connection_coordinator=connection_coordinator,
        )

    @pytest.fixture
    def sample_note_path(self, tmp_path):
        """Create sample note file for testing."""
        note_path = tmp_path / "test-note.md"
        content = """---
title: Test Note
created: 2025-01-01 12:00
tags: [existing-tag]
status: inbox
---

# Test Note

This is a test note with enough content to test processing.
It has multiple paragraphs and should trigger AI processing.
"""
        note_path.write_text(content)
        return note_path

    def test_process_note_with_ai_full_pipeline(
        self, coordinator, sample_note_path, tmp_path
    ):
        """Test complete AI processing pipeline."""
        # Create a corpus directory for connection discovery
        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir()

        result = coordinator.process_note(str(sample_note_path), corpus_dir=corpus_dir)

        # Should return processing results
        assert "processing" in result
        assert "recommendations" in result
        assert "original_file" in result

        # AI components should be called
        coordinator.tagger.generate_tags.assert_called_once()
        coordinator.enhancer.enhance_note.assert_called_once()
        coordinator.connection_coordinator.discover_connections.assert_called_once()

    def test_process_note_merges_tags_correctly(self, coordinator, sample_note_path):
        """Test that existing and AI-generated tags are merged."""
        result = coordinator.process_note(str(sample_note_path))

        # Should merge existing and new tags
        assert "processing" in result
        assert "tags" in result["processing"]

        # Check tag merging happened
        coordinator.tagger.generate_tags.assert_called_once()

    def test_process_note_calculates_quality_score(self, coordinator, sample_note_path):
        """Test quality score calculation and recommendations."""
        result = coordinator.process_note(str(sample_note_path))

        assert "processing" in result
        assert "quality" in result["processing"]
        assert "score" in result["processing"]["quality"]
        assert result["processing"]["quality"]["score"] == 0.75

    def test_process_note_generates_recommendations(
        self, coordinator, sample_note_path
    ):
        """Test workflow recommendations based on quality."""
        result = coordinator.process_note(str(sample_note_path))

        assert "recommendations" in result
        assert len(result["recommendations"]) > 0

        # High quality (0.75) should suggest promotion
        rec = result["recommendations"][0]
        assert rec["action"] == "promote_to_permanent"
        assert rec["confidence"] == "high"

    def test_process_note_discovers_connections(
        self, coordinator, sample_note_path, tmp_path
    ):
        """Test connection discovery integration."""
        # Create corpus directory for connection discovery
        corpus_dir = tmp_path / "corpus"
        corpus_dir.mkdir()

        result = coordinator.process_note(str(sample_note_path), corpus_dir=corpus_dir)

        assert "processing" in result
        assert "connections" in result["processing"]
        assert "similar_notes" in result["processing"]["connections"]

        # Should recommend adding links
        link_recs = [r for r in result["recommendations"] if r["action"] == "add_links"]
        assert len(link_recs) > 0


class TestFastModeProcessing:
    """Test fast mode processing with heuristics (no AI calls)."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator for fast mode testing."""
        return NoteProcessingCoordinator(
            tagger=Mock(),
            summarizer=Mock(),
            enhancer=Mock(),
            connection_coordinator=Mock(),
        )

    @pytest.fixture
    def sample_note_path(self, tmp_path):
        """Create sample note for fast mode testing."""
        note_path = tmp_path / "fast-test.md"
        content = """---
title: Fast Mode Test
created: 2025-01-01 12:00
tags: [tag1, tag2, tag3]
---

# Fast Mode Test

Short content for fast heuristic processing.
"""
        note_path.write_text(content)
        return note_path

    def test_fast_mode_skips_ai_calls(self, coordinator, sample_note_path):
        """Test fast mode uses heuristics without AI calls."""
        result = coordinator.process_note(str(sample_note_path), fast=True)

        # Should not call AI components
        coordinator.tagger.generate_tags.assert_not_called()
        coordinator.enhancer.enhance_note.assert_not_called()
        coordinator.connection_coordinator.discover_connections.assert_not_called()

    def test_fast_mode_calculates_heuristic_quality(
        self, coordinator, sample_note_path
    ):
        """Test fast mode quality calculation based on word count."""
        result = coordinator.process_note(str(sample_note_path), fast=True)

        assert "processing" in result
        assert "quality" in result["processing"]
        assert "score" in result["processing"]["quality"]

        # Should have some quality score based on heuristics
        assert 0.0 <= result["processing"]["quality"]["score"] <= 1.0

    def test_fast_mode_provides_recommendations(self, coordinator, sample_note_path):
        """Test fast mode still provides basic recommendations."""
        result = coordinator.process_note(str(sample_note_path), fast=True)

        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
        assert result["recommendations"][0]["action"] in [
            "promote_to_permanent",
            "move_to_fleeting",
            "improve_or_archive",
        ]


class TestTemplatePlaceholderFixing:
    """Test template placeholder detection and fixing."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator for template testing."""
        return NoteProcessingCoordinator(
            tagger=Mock(),
            summarizer=Mock(),
            enhancer=Mock(),
            connection_coordinator=Mock(),
        )

    def test_fix_template_placeholders_in_frontmatter(self, coordinator, tmp_path):
        """Test fixing {{date:...}} placeholders in frontmatter."""
        note_path = tmp_path / "template-test.md"
        content = """---
title: Template Test
created: {{date:YYYY-MM-DD HH:mm}}
tags: []
---

Test content
"""
        note_path.write_text(content)

        result = coordinator.process_note(str(note_path))

        # Should indicate template was fixed
        assert result.get("template_fixed") == True

    def test_fix_templater_ejs_patterns(self, coordinator, tmp_path):
        """Test fixing Templater EJS patterns like <% tp.date.now(...) %>."""
        note_path = tmp_path / "ejs-test.md"
        content = """---
title: EJS Test
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
tags: []
---

Test content
"""
        note_path.write_text(content)

        result = coordinator.process_note(str(note_path))

        assert result.get("template_fixed") == True

    def test_preprocess_raw_template_placeholders(self, coordinator, tmp_path):
        """Test preprocessing fixes templates before YAML parsing."""
        note_path = tmp_path / "raw-template.md"
        content = """---
title: Raw Template Test
created: {{date}}
tags: []
---

Content
"""
        note_path.write_text(content)

        result = coordinator.process_note(str(note_path))

        # Should fix and process successfully
        assert "error" not in result
        assert result.get("template_fixed") == True

    def test_no_template_fixes_when_not_needed(self, coordinator, tmp_path):
        """Test no false positives when templates are already valid."""
        note_path = tmp_path / "valid-note.md"
        content = """---
title: Valid Note
created: 2025-01-01 12:00
tags: []
---

Content
"""
        note_path.write_text(content)

        result = coordinator.process_note(str(note_path))

        # Should not indicate template fixing
        assert result.get("template_fixed", False) == False


class TestDryRunMode:
    """Test dry-run mode (no file modifications)."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator for dry-run testing."""
        tagger = Mock()
        tagger.generate_tags = Mock(return_value=["new-tag"])

        enhancer = Mock()
        enhancer.enhance_note = Mock(
            return_value={"quality_score": 0.8, "suggestions": ["Test suggestion"]}
        )

        return NoteProcessingCoordinator(
            tagger=tagger,
            summarizer=Mock(),
            enhancer=enhancer,
            connection_coordinator=Mock(),
        )

    def test_dry_run_does_not_modify_files(self, coordinator, tmp_path):
        """Test dry-run mode prevents file modifications."""
        note_path = tmp_path / "dry-run-test.md"
        original_content = """---
title: Dry Run Test
tags: []
---

Content
"""
        note_path.write_text(original_content)

        result = coordinator.process_note(str(note_path), dry_run=True)

        # File should not be modified
        assert note_path.read_text() == original_content
        assert result.get("file_updated") == False

    def test_dry_run_still_processes_with_ai(self, coordinator, tmp_path):
        """Test dry-run still performs AI processing for preview."""
        note_path = tmp_path / "dry-run-ai.md"
        note_path.write_text(
            """---
title: Test
tags: []
---

Content
"""
        )

        # Note: dry_run defaults fast to True, so we need to explicitly set fast=False
        result = coordinator.process_note(str(note_path), dry_run=True, fast=False)

        # Should still call AI for analysis (unless fast mode)
        assert "processing" in result


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator for error testing."""
        return NoteProcessingCoordinator(
            tagger=Mock(),
            summarizer=Mock(),
            enhancer=Mock(),
            connection_coordinator=Mock(),
        )

    def test_handles_missing_file(self, coordinator):
        """Test handling of non-existent file."""
        result = coordinator.process_note("/nonexistent/path/note.md")

        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_handles_ai_component_errors(self, coordinator, tmp_path):
        """Test graceful handling of AI component failures."""
        # Make AI component raise exception
        coordinator.tagger.generate_tags = Mock(side_effect=Exception("AI error"))

        note_path = tmp_path / "error-test.md"
        note_path.write_text(
            """---
title: Error Test
tags: []
---

Content
"""
        )

        result = coordinator.process_note(str(note_path))

        # Should handle error gracefully
        assert "processing" in result
        assert "tags" in result["processing"]
        assert "error" in result["processing"]["tags"]

    def test_handles_malformed_frontmatter(self, coordinator, tmp_path):
        """Test handling of invalid YAML frontmatter."""
        note_path = tmp_path / "bad-yaml.md"
        content = """---
title: Bad YAML
tags: [unclosed
---

Content
"""
        note_path.write_text(content)

        result = coordinator.process_note(str(note_path))

        # Should either fix or handle gracefully
        assert "error" not in result or "YAML" in result.get("error", "")


class TestIntegrationWithWorkflow:
    """Test integration patterns with WorkflowManager."""

    def test_coordinator_exposes_correct_interface(self):
        """Test coordinator has expected public methods."""
        coordinator = NoteProcessingCoordinator(
            tagger=Mock(),
            summarizer=Mock(),
            enhancer=Mock(),
            connection_coordinator=Mock(),
        )

        # Should have main processing method
        assert hasattr(coordinator, "process_note")
        assert callable(coordinator.process_note)

    def test_coordinator_returns_expected_result_format(self, tmp_path):
        """Test result format matches WorkflowManager expectations."""
        coordinator = NoteProcessingCoordinator(
            tagger=Mock(generate_tags=Mock(return_value=[])),
            summarizer=Mock(),
            enhancer=Mock(
                enhance_note=Mock(
                    return_value={"quality_score": 0.5, "suggestions": []}
                )
            ),
            connection_coordinator=Mock(discover_connections=Mock(return_value=[])),
        )

        note_path = tmp_path / "format-test.md"
        note_path.write_text(
            """---
title: Format Test
tags: []
---

Content
"""
        )

        result = coordinator.process_note(str(note_path))

        # Expected result keys
        assert "original_file" in result
        assert "processing" in result
        assert "recommendations" in result

        # Processing should have expected structure
        if "quality" in result["processing"]:
            assert "score" in result["processing"]["quality"]


class TestTriageRecommendationPersistence:
    """Test persistence of triage_recommendation to frontmatter (Phase 1)."""

    @pytest.fixture
    def coordinator(self):
        """Create coordinator with mocked AI components for triage testing."""
        tagger = Mock()
        tagger.generate_tags = Mock(return_value=["test-tag"])

        enhancer = Mock()
        enhancer.enhance_note = Mock(
            return_value={"quality_score": 0.8, "suggestions": []}
        )

        return NoteProcessingCoordinator(
            tagger=tagger,
            summarizer=Mock(),
            enhancer=enhancer,
            connection_coordinator=Mock(discover_connections=Mock(return_value=[])),
        )

    def test_process_note_persists_triage_recommendation_promote(
        self, coordinator, tmp_path
    ):
        """Test triage_recommendation is written to frontmatter for high quality notes."""
        note_path = tmp_path / "high-quality-note.md"
        note_path.write_text(
            """---
title: High Quality Note
tags: []
---

This is a high quality note with substantial content.
"""
        )

        # Process note (non-dry-run)
        result = coordinator.process_note(str(note_path), dry_run=False)

        # Verify the recommendation was returned
        assert len(result["recommendations"]) > 0
        assert result["recommendations"][0]["action"] == "promote_to_permanent"

        # Verify triage_recommendation is persisted in the file
        updated_content = note_path.read_text()
        assert "triage_recommendation: promote_to_permanent" in updated_content

    def test_process_note_persists_triage_recommendation_fleeting(self, tmp_path):
        """Test triage_recommendation for medium quality notes."""
        # Create coordinator with medium quality score
        enhancer = Mock()
        enhancer.enhance_note = Mock(
            return_value={"quality_score": 0.55, "suggestions": []}
        )

        coordinator = NoteProcessingCoordinator(
            tagger=Mock(generate_tags=Mock(return_value=[])),
            summarizer=Mock(),
            enhancer=enhancer,
            connection_coordinator=Mock(discover_connections=Mock(return_value=[])),
        )

        note_path = tmp_path / "medium-quality-note.md"
        note_path.write_text(
            """---
title: Medium Quality Note
tags: []
---

Medium quality content.
"""
        )

        result = coordinator.process_note(str(note_path), dry_run=False)

        assert result["recommendations"][0]["action"] == "move_to_fleeting"

        updated_content = note_path.read_text()
        assert "triage_recommendation: move_to_fleeting" in updated_content

    def test_process_note_persists_triage_recommendation_improve(self, tmp_path):
        """Test triage_recommendation for low quality notes."""
        # Create coordinator with low quality score
        enhancer = Mock()
        enhancer.enhance_note = Mock(
            return_value={"quality_score": 0.2, "suggestions": []}
        )

        coordinator = NoteProcessingCoordinator(
            tagger=Mock(generate_tags=Mock(return_value=[])),
            summarizer=Mock(),
            enhancer=enhancer,
            connection_coordinator=Mock(discover_connections=Mock(return_value=[])),
        )

        note_path = tmp_path / "low-quality-note.md"
        note_path.write_text(
            """---
title: Low Quality Note
tags: []
---

Short.
"""
        )

        result = coordinator.process_note(str(note_path), dry_run=False)

        assert result["recommendations"][0]["action"] == "improve_or_archive"

        updated_content = note_path.read_text()
        assert "triage_recommendation: improve_or_archive" in updated_content

    def test_triage_recommendation_overwrites_on_reprocess(self, tmp_path):
        """Test triage_recommendation is overwritten on re-processing (idempotent)."""
        enhancer = Mock()
        enhancer.enhance_note = Mock(
            return_value={"quality_score": 0.8, "suggestions": []}
        )

        coordinator = NoteProcessingCoordinator(
            tagger=Mock(generate_tags=Mock(return_value=[])),
            summarizer=Mock(),
            enhancer=enhancer,
            connection_coordinator=Mock(discover_connections=Mock(return_value=[])),
        )

        note_path = tmp_path / "reprocess-note.md"
        # Note already has an old triage_recommendation
        note_path.write_text(
            """---
title: Reprocess Note
tags: []
triage_recommendation: improve_or_archive
---

Content that is now high quality.
"""
        )

        result = coordinator.process_note(str(note_path), dry_run=False)

        # Should overwrite with new recommendation
        updated_content = note_path.read_text()
        assert "triage_recommendation: promote_to_permanent" in updated_content
        # Should NOT have old value
        assert "triage_recommendation: improve_or_archive" not in updated_content

    def test_dry_run_does_not_persist_triage_recommendation(
        self, coordinator, tmp_path
    ):
        """Test dry-run mode does not write triage_recommendation to file."""
        note_path = tmp_path / "dry-run-triage.md"
        original_content = """---
title: Dry Run Triage Test
tags: []
---

Content.
"""
        note_path.write_text(original_content)

        result = coordinator.process_note(str(note_path), dry_run=True)

        # Should still compute recommendation
        assert len(result["recommendations"]) > 0

        # But file should NOT be modified
        updated_content = note_path.read_text()
        assert "triage_recommendation" not in updated_content

    def test_fast_mode_persists_triage_recommendation(self, tmp_path):
        """Test fast mode (heuristic) also persists triage_recommendation."""
        coordinator = NoteProcessingCoordinator(
            tagger=Mock(),
            summarizer=Mock(),
            enhancer=Mock(),
            connection_coordinator=Mock(),
        )

        note_path = tmp_path / "fast-mode-triage.md"
        # Long content for high heuristic score
        note_path.write_text(
            """---
title: Fast Mode Triage Test
tags: [tag1, tag2, tag3]
---

"""
            + "This is substantial content. " * 100
        )

        result = coordinator.process_note(str(note_path), fast=True, dry_run=False)

        # Fast mode should also persist
        updated_content = note_path.read_text()
        assert "triage_recommendation:" in updated_content
