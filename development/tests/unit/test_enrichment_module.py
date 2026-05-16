"""
Characterization tests for the enrichment.py consolidated module (Issue #120).

Verifies that all 5 public classes from the former individual files are
accessible from src.ai.enrichment with their key methods intact.

Pre-existing failures (do not regress):
  - test_metadata_repair_engine.py: all 13 tests fail due to wrong import path
    in the test file (from development.src.ai...) — not our bug to fix here.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.ai.enrichment import (
    AIEnhancementManager,
    AIEnhancer,
    AISummarizer,
    AITagger,
    MetadataRepairEngine,
)


class TestAITaggerPublicInterface:
    def test_instantiates_with_defaults(self):
        tagger = AITagger()
        assert tagger.min_confidence == 0.7

    def test_returns_empty_list_for_empty_content(self):
        tagger = AITagger()
        assert tagger.generate_tags("") == []
        assert tagger.generate_tags("   ") == []

    def test_generate_tags_with_confidence_returns_tuples(self):
        tagger = AITagger()
        result = tagger.generate_tags_with_confidence(
            "python machine learning algorithms"
        )
        assert isinstance(result, list)
        for tag, conf in result:
            assert isinstance(tag, str)
            assert isinstance(conf, float)


class TestAISummarizerPublicInterface:
    def test_instantiates_with_defaults(self):
        summarizer = AISummarizer()
        assert summarizer.min_length == 500

    def test_should_summarize_returns_false_for_short_content(self):
        summarizer = AISummarizer()
        assert summarizer.should_summarize("short note") is False

    def test_should_summarize_returns_true_for_long_content(self):
        summarizer = AISummarizer(min_length=5)
        assert summarizer.should_summarize("word " * 10) is True

    def test_generate_summary_returns_none_for_short_content(self):
        summarizer = AISummarizer()
        result = summarizer.generate_summary("too short")
        assert result is None

    def test_generate_extractive_summary_returns_string(self):
        summarizer = AISummarizer(min_length=5)
        long_content = "This is a sentence. " * 20
        result = summarizer.generate_extractive_summary(long_content)
        assert result is None or isinstance(result, str)


class TestAIEnhancerPublicInterface:
    def test_instantiates_with_defaults(self):
        enhancer = AIEnhancer()
        assert enhancer.min_quality_score == 0.6

    def test_analyze_note_quality_returns_dict_for_empty_content(self):
        enhancer = AIEnhancer()
        result = enhancer.analyze_note_quality("")
        assert isinstance(result, dict)
        assert "quality_score" in result
        assert result["quality_score"] == 0.0

    def test_analyze_note_quality_has_required_keys(self):
        enhancer = AIEnhancer()
        result = enhancer.analyze_note_quality("")
        assert "suggestions" in result
        assert "missing_elements" in result


class TestAIEnhancementManagerPublicInterface:
    def test_instantiates_with_required_args(self, tmp_path):
        manager = AIEnhancementManager(base_dir=tmp_path, config={})
        assert manager.base_dir == tmp_path

    def test_enhance_note_dry_run_skips_ai_calls(self, tmp_path):
        note = tmp_path / "note.md"
        note.write_text("---\ntype: fleeting\n---\nSome content here.\n")
        manager = AIEnhancementManager(base_dir=tmp_path, config={})
        result = manager.enhance_note(str(note), dry_run=True)
        assert isinstance(result, dict)
        assert result.get("skipped") is True


class TestMetadataRepairEnginePublicInterface:
    def test_instantiates(self, tmp_path):
        engine = MetadataRepairEngine(inbox_dir=str(tmp_path))
        assert engine.dry_run is True

    def test_has_detect_missing_metadata_method(self, tmp_path):
        engine = MetadataRepairEngine(inbox_dir=str(tmp_path))
        assert callable(engine.detect_missing_metadata)

    def test_has_repair_note_method(self, tmp_path):
        engine = MetadataRepairEngine(inbox_dir=str(tmp_path))
        assert callable(engine.repair_note_metadata)
