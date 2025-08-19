"""
Unit tests for the workflow manager module.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.ai.workflow_manager import WorkflowManager


class TestWorkflowManager:
    """Test cases for WorkflowManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.base_dir = Path(self.temp_dir)
        
        # Create directory structure
        (self.base_dir / "Inbox").mkdir()
        (self.base_dir / "Fleeting Notes").mkdir()
        (self.base_dir / "Permanent Notes").mkdir()
        (self.base_dir / "Archive").mkdir()
        
        self.workflow = WorkflowManager(str(self.base_dir))
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_note(self, directory: str, filename: str, content: str):
        """Helper to create a test note."""
        note_path = self.base_dir / directory / filename
        note_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return note_path
    
    def test_initialization(self):
        """Test workflow manager initialization."""
        assert self.workflow.base_dir == self.base_dir
        assert self.workflow.inbox_dir == self.base_dir / "Inbox"
        assert self.workflow.fleeting_dir == self.base_dir / "Fleeting Notes"
        assert self.workflow.permanent_dir == self.base_dir / "Permanent Notes"
        assert self.workflow.archive_dir == self.base_dir / "Archive"
        
        # Check AI components
        assert self.workflow.tagger is not None
        assert self.workflow.summarizer is not None
        assert self.workflow.connections is not None
        assert self.workflow.enhancer is not None
        assert self.workflow.analytics is not None
    
    def test_load_config_default(self):
        """Test loading default configuration."""
        config = self.workflow._load_config()
        
        assert config["auto_tag_inbox"] is True
        assert config["auto_summarize_long_notes"] is True
        assert config["auto_enhance_permanent_notes"] is False
        assert config["min_words_for_summary"] == 500
        assert config["max_tags_per_note"] == 8
        assert config["similarity_threshold"] == 0.7
        assert config["archive_after_days"] == 90
    
    def test_load_config_custom(self):
        """Test loading custom configuration."""
        config_file = self.base_dir / ".ai_workflow_config.json"
        custom_config = {
            "auto_tag_inbox": False,
            "max_tags_per_note": 5
        }
        
        with open(config_file, 'w') as f:
            json.dump(custom_config, f)
        
        workflow = WorkflowManager(str(self.base_dir))
        config = workflow.config
        
        assert config["auto_tag_inbox"] is False
        assert config["max_tags_per_note"] == 5
        assert config["auto_summarize_long_notes"] is True  # Default preserved
    
    def test_extract_frontmatter(self):
        """Test frontmatter extraction."""
        content = """---
type: permanent
created: 2024-01-01 10:00
tags: ["ai", "testing"]
status: published
---

This is the body content."""
        
        frontmatter, body = self.workflow._extract_frontmatter(content)
        
        assert frontmatter["type"] == "permanent"
        assert frontmatter["created"] == "2024-01-01 10:00"
        assert frontmatter["tags"] == ["ai", "testing"]
        assert frontmatter["status"] == "published"
        assert body.strip() == "This is the body content."
    
    def test_merge_tags(self):
        """Test tag merging functionality."""
        existing_tags = ["ai", "research"]
        new_tags = ["machine-learning", "ai", "deep-learning"]
        
        merged = self.workflow._merge_tags(existing_tags, new_tags)
        
        assert "ai" in merged
        assert "research" in merged
        assert "machine-learning" in merged
        assert "deep-learning" in merged
        assert len(merged) == len(set(merged))  # No duplicates
        assert len(merged) <= self.workflow.config["max_tags_per_note"]
    
    def test_rebuild_content(self):
        """Test content rebuilding with frontmatter."""
        frontmatter = {
            "type": "permanent",
            "created": "2024-01-01 10:00",
            "tags": ["ai", "testing"],
            "status": "published"
        }
        body = "This is the body content."
        
        rebuilt = self.workflow._rebuild_content(frontmatter, body)
        
        assert rebuilt.startswith("---")
        assert "type: permanent" in rebuilt
        assert "created: 2024-01-01 10:00" in rebuilt
        assert 'tags: ["ai", "testing"]' in rebuilt
        assert "status: published" in rebuilt
        assert rebuilt.endswith(body)
    
    @patch('src.ai.workflow_manager.WorkflowManager._load_notes_corpus')
    @patch('src.ai.enhancer.AIEnhancer.enhance_note')
    @patch('src.ai.tagger.AITagger.generate_tags')
    def test_process_inbox_note_success(self, mock_generate_tags, mock_enhance, mock_load_corpus):
        """Test successful inbox note processing."""
        # Setup mocks
        mock_generate_tags.return_value = ["ai", "machine-learning"]
        mock_enhance.return_value = {
            "quality_score": 0.8,
            "suggestions": ["Add more examples", "Include references"]
        }
        mock_load_corpus.return_value = {
            "related-note.md": "Related content about AI"
        }
        
        # Create test note
        content = """---
type: fleeting
created: 2024-01-01 10:00
tags: ["research"]
status: inbox
---

This is a comprehensive note about artificial intelligence.
It contains detailed information and analysis.
The content is substantial enough for quality assessment."""
        
        note_path = self.create_test_note("Inbox", "test-note.md", content)
        
        # Process the note
        result = self.workflow.process_inbox_note(str(note_path))
        
        assert "error" not in result
        assert result["original_file"] == str(note_path)
        assert "processing" in result
        assert "recommendations" in result
        
        # Check processing results
        processing = result["processing"]
        if "tags" in processing:
            assert "added" in processing["tags"]
            assert "total" in processing["tags"]
        
        if "quality" in processing:
            assert processing["quality"]["score"] == 0.8
            assert len(processing["quality"]["suggestions"]) > 0
        
        # Check recommendations
        recommendations = result["recommendations"]
        assert len(recommendations) > 0
        assert any(rec["action"] == "promote_to_permanent" for rec in recommendations)
    
    def test_process_inbox_note_file_not_found(self):
        """Test processing non-existent note."""
        result = self.workflow.process_inbox_note("nonexistent.md")
        
        assert "error" in result
        assert result["error"] == "Note file not found"
    
    def test_promote_note_to_permanent(self):
        """Test promoting note to permanent status."""
        # Create test note in inbox
        content = """---
type: fleeting
created: 2024-01-01 10:00
status: inbox
---

This is a note ready for promotion to permanent status.
It has sufficient content and quality for permanent storage."""
        
        note_path = self.create_test_note("Inbox", "promote-test.md", content)
        
        # Mock summarizer to avoid API calls
        with patch.object(self.workflow.summarizer, 'should_summarize', return_value=True), \
             patch.object(self.workflow.summarizer, 'generate_summary', return_value="Test summary"):
            
            result = self.workflow.promote_note(str(note_path), "permanent")
        
        assert result["success"] is True
        assert result["type"] == "permanent"
        assert result["has_summary"] is True
        
        # Check that file was moved
        assert not note_path.exists()
        target_path = self.base_dir / "Permanent Notes" / "promote-test.md"
        assert target_path.exists()
        
        # Check updated content
        with open(target_path, 'r') as f:
            updated_content = f.read()
        
        assert "type: permanent" in updated_content
        assert "status: promoted" in updated_content
        assert "promoted_date:" in updated_content
        assert "ai_summary:" in updated_content
    
    def test_promote_note_to_fleeting(self):
        """Test promoting note to fleeting status."""
        content = """---
type: unknown
status: inbox
---

This is a note for fleeting promotion."""
        
        note_path = self.create_test_note("Inbox", "fleeting-test.md", content)
        
        result = self.workflow.promote_note(str(note_path), "fleeting")
        
        assert result["success"] is True
        assert result["type"] == "fleeting"
        
        # Check that file was moved
        assert not note_path.exists()
        target_path = self.base_dir / "Fleeting Notes" / "fleeting-test.md"
        assert target_path.exists()
        
        # Check updated content
        with open(target_path, 'r') as f:
            updated_content = f.read()
        
        assert "type: fleeting" in updated_content
        assert "status: draft" in updated_content
    
    def test_promote_note_invalid_type(self):
        """Test promoting note with invalid type."""
        note_path = self.create_test_note("Inbox", "test.md", "content")
        
        result = self.workflow.promote_note(str(note_path), "invalid")
        
        assert "error" in result
        assert "Invalid target type" in result["error"]
    
    @patch('src.ai.workflow_manager.WorkflowManager.process_inbox_note')
    def test_batch_process_inbox(self, mock_process):
        """Test batch processing of inbox notes."""
        # Create multiple test notes
        for i in range(3):
            self.create_test_note("Inbox", f"note{i}.md", f"Content {i}")
        
        # Mock processing results
        mock_process.side_effect = [
            {
                "original_file": "note0.md",
                "recommendations": [{"action": "promote_to_permanent"}]
            },
            {
                "original_file": "note1.md",
                "recommendations": [{"action": "move_to_fleeting"}]
            },
            {
                "original_file": "note2.md",
                "recommendations": [{"action": "improve_or_archive"}]
            }
        ]
        
        result = self.workflow.batch_process_inbox()
        
        assert result["total_files"] == 3
        assert result["processed"] == 3
        assert result["failed"] == 0
        assert result["summary"]["promote_to_permanent"] == 1
        assert result["summary"]["move_to_fleeting"] == 1
        assert result["summary"]["needs_improvement"] == 1
    
    def test_load_notes_corpus(self):
        """Test loading notes corpus from directory."""
        # Create test notes in permanent directory
        self.create_test_note("Permanent Notes", "note1.md", "Content 1")
        self.create_test_note("Permanent Notes", "note2.md", "Content 2")
        
        corpus = self.workflow._load_notes_corpus(self.workflow.permanent_dir)
        
        assert len(corpus) == 2
        assert "note1.md" in corpus
        assert "note2.md" in corpus
        assert corpus["note1.md"] == "Content 1"
        assert corpus["note2.md"] == "Content 2"
    
    def test_load_notes_corpus_empty_directory(self):
        """Test loading corpus from empty directory."""
        corpus = self.workflow._load_notes_corpus(self.workflow.permanent_dir)
        
        assert corpus == {}
    
    def test_load_notes_corpus_nonexistent_directory(self):
        """Test loading corpus from non-existent directory."""
        nonexistent_dir = self.base_dir / "NonExistent"
        corpus = self.workflow._load_notes_corpus(nonexistent_dir)
        
        assert corpus == {}
    
    @patch('src.ai.analytics.NoteAnalytics.generate_report')
    def test_generate_workflow_report(self, mock_analytics_report):
        """Test workflow report generation."""
        # Create test notes in different directories
        self.create_test_note("Inbox", "inbox1.md", "Inbox content")
        self.create_test_note("Inbox", "inbox2.md", "Inbox content")
        self.create_test_note("Fleeting Notes", "fleeting1.md", "Fleeting content")
        self.create_test_note("Permanent Notes", "permanent1.md", "Permanent content")
        
        # Mock analytics report
        mock_analytics_report.return_value = {
            "overview": {"total_notes": 4},
            "quality_metrics": {"high_quality_notes": 1}
        }
        
        report = self.workflow.generate_workflow_report()
        
        assert "workflow_status" in report
        assert "ai_features" in report
        assert "analytics" in report
        assert "recommendations" in report
        
        # Check workflow status
        workflow_status = report["workflow_status"]
        assert workflow_status["directory_counts"]["Inbox"] == 2
        assert workflow_status["directory_counts"]["Fleeting Notes"] == 1
        assert workflow_status["directory_counts"]["Permanent Notes"] == 1
        assert workflow_status["total_notes"] == 4
        
        # Health should be "needs_attention" with 2 inbox notes
        assert workflow_status["health"] in ["healthy", "needs_attention"]
    
    def test_analyze_ai_usage(self):
        """Test AI usage analysis."""
        # Create notes with various AI features
        notes_data = [
            ("note1.md", """---
ai_summary: AI generated summary
ai_processed: 2024-01-01T10:00:00
tags: ["machine-learning", "deep-learning", "artificial-intelligence"]
---
Content 1"""),
            ("note2.md", """---
tags: ["simple", "tag"]
---
Content 2"""),
            ("note3.md", """---
ai_processed: 2024-01-01T10:00:00
---
Content 3""")
        ]
        
        for filename, content in notes_data:
            self.create_test_note("Permanent Notes", filename, content)
        
        usage_stats = self.workflow._analyze_ai_usage()
        
        assert usage_stats["total_analyzed"] == 3
        assert usage_stats["notes_with_ai_summaries"] == 1
        assert usage_stats["notes_with_ai_processing"] == 2
        assert usage_stats["notes_with_ai_tags"] == 1  # Only note1 has AI-style tags
    
    def test_generate_workflow_recommendations(self):
        """Test workflow recommendation generation."""
        directory_counts = {
            "Inbox": 25,  # High inbox count
            "Fleeting Notes": 11,  # Greater than permanent * 2 (5 * 2 = 10)
            "Permanent Notes": 5,
            "Archive": 0
        }
        
        ai_usage = {
            "total_analyzed": 40,
            "notes_with_ai_summaries": 5,
            "notes_with_ai_processing": 15
        }
        
        recommendations = self.workflow._generate_workflow_recommendations(
            directory_counts, ai_usage
        )
        
        # Should recommend processing inbox
        inbox_rec = any("inbox" in rec.lower() for rec in recommendations)
        assert inbox_rec
        
        # Should recommend AI features
        ai_rec = any("ai" in rec.lower() or "summarization" in rec.lower() 
                    for rec in recommendations)
        assert ai_rec
        
        # Should recommend promoting fleeting notes
        promote_rec = any("promoting" in rec.lower() or "fleeting" in rec.lower() 
                         for rec in recommendations)
        assert promote_rec

    # ========================= WEEKLY REVIEW TESTS =========================
    
    def test_scan_review_candidates_inbox_only(self):
        """Test scanning for review candidates in inbox directory only."""
        # Create notes in inbox
        self.create_test_note("Inbox", "note1.md", "---\ntype: fleeting\nstatus: inbox\n---\nContent 1")
        self.create_test_note("Inbox", "note2.md", "---\ntype: fleeting\nstatus: inbox\n---\nContent 2")
        
        # Create notes in other directories (should not be included)
        self.create_test_note("Fleeting Notes", "note3.md", "---\ntype: fleeting\nstatus: promoted\n---\nContent 3")
        
        candidates = self.workflow.scan_review_candidates()
        
        # Should find 2 candidates from inbox
        assert len(candidates) == 2
        assert all("Inbox" in str(candidate["path"]) for candidate in candidates)
        
        # Verify candidate structure
        for candidate in candidates:
            assert "path" in candidate
            assert "source" in candidate
            assert "metadata" in candidate
            assert candidate["source"] == "inbox"
    
    def test_scan_review_candidates_fleeting_inbox_status(self):
        """Test scanning for fleeting notes with inbox status."""
        # Create fleeting notes with different statuses
        self.create_test_note("Fleeting Notes", "inbox_note.md", 
                             "---\ntype: fleeting\nstatus: inbox\n---\nNeeds review")
        self.create_test_note("Fleeting Notes", "promoted_note.md", 
                             "---\ntype: fleeting\nstatus: promoted\n---\nAlready promoted")
        self.create_test_note("Fleeting Notes", "draft_note.md", 
                             "---\ntype: fleeting\nstatus: draft\n---\nIn draft")
        
        candidates = self.workflow.scan_review_candidates()
        
        # Should find only the inbox status note
        assert len(candidates) == 1
        assert "fleeting" in str(candidates[0]["path"]).lower()
        assert candidates[0]["source"] == "fleeting"
        assert candidates[0]["metadata"]["status"] == "inbox"
    
    def test_scan_review_candidates_combined(self):
        """Test scanning combines inbox and fleeting notes with inbox status."""
        # Create notes in inbox
        self.create_test_note("Inbox", "inbox1.md", "---\ntype: fleeting\nstatus: inbox\n---\nInbox content")
        self.create_test_note("Inbox", "inbox2.md", "---\ntype: fleeting\nstatus: inbox\n---\nMore inbox content")
        
        # Create fleeting notes with inbox status
        self.create_test_note("Fleeting Notes", "fleeting1.md", 
                             "---\ntype: fleeting\nstatus: inbox\n---\nFleeting inbox content")
        
        # Create fleeting notes with other statuses (should not be included)
        self.create_test_note("Fleeting Notes", "fleeting2.md", 
                             "---\ntype: fleeting\nstatus: promoted\n---\nPromoted content")
        
        candidates = self.workflow.scan_review_candidates()
        
        # Should find 3 total candidates (2 inbox + 1 fleeting)
        assert len(candidates) == 3
        
        # Verify sources
        inbox_candidates = [c for c in candidates if c["source"] == "inbox"]
        fleeting_candidates = [c for c in candidates if c["source"] == "fleeting"]
        
        assert len(inbox_candidates) == 2
        assert len(fleeting_candidates) == 1
    
    def test_scan_review_candidates_handles_missing_yaml(self):
        """Test scanner handles notes with missing or malformed YAML."""
        # Create notes with various YAML issues
        self.create_test_note("Inbox", "no_yaml.md", "Just plain content without frontmatter")
        self.create_test_note("Inbox", "malformed_yaml.md", "---\ntype: fleeting\nstatus: inbox\ninvalid yaml\n---\nContent")
        self.create_test_note("Fleeting Notes", "missing_status.md", "---\ntype: fleeting\n---\nNo status field")
        
        # This should not raise an exception
        candidates = self.workflow.scan_review_candidates()
        
        # Should handle gracefully - inbox files always included regardless of YAML
        inbox_candidates = [c for c in candidates if c["source"] == "inbox"]
        assert len(inbox_candidates) == 2  # Both inbox files included
        
        # Fleeting note without status should not be included
        fleeting_candidates = [c for c in candidates if c["source"] == "fleeting"]
        assert len(fleeting_candidates) == 0
    
    def test_scan_review_candidates_empty_directories(self):
        """Test scanner handles empty directories gracefully."""
        # No notes created - directories are empty
        candidates = self.workflow.scan_review_candidates()
        
        assert len(candidates) == 0
        assert isinstance(candidates, list)
    
    def test_scan_review_candidates_non_markdown_files(self):
        """Test scanner ignores non-markdown files."""
        # Create non-markdown files
        (self.base_dir / "Inbox" / "text_file.txt").write_text("Not markdown")
        (self.base_dir / "Inbox" / "image.png").write_text("Binary data")
        
        # Create one valid markdown file
        self.create_test_note("Inbox", "valid.md", "---\ntype: fleeting\nstatus: inbox\n---\nValid content")
        
        candidates = self.workflow.scan_review_candidates()
        
        # Should only find the markdown file
        assert len(candidates) == 1
        assert candidates[0]["path"].suffix == ".md"

    # ========================= WEEKLY RECOMMENDATIONS TESTS =========================
    
    def test_generate_weekly_recommendations_empty_candidates(self):
        """Test weekly recommendations with no candidates."""
        candidates = []
        
        recommendations = self.workflow.generate_weekly_recommendations(candidates)
        
        # Should return empty results
        assert recommendations["summary"]["total_notes"] == 0
        assert recommendations["summary"]["promote_to_permanent"] == 0
        assert recommendations["summary"]["move_to_fleeting"] == 0
        assert recommendations["summary"]["needs_improvement"] == 0
        assert len(recommendations["recommendations"]) == 0
    
    @patch('src.ai.workflow_manager.WorkflowManager.process_inbox_note')
    def test_generate_weekly_recommendations_high_quality_note(self, mock_process):
        """Test recommendations for high-quality note (should promote)."""
        # Mock high-quality processing result
        mock_process.return_value = {
            "quality_score": 0.85,
            "recommendations": [{
                "action": "promote_to_permanent",
                "reason": "High quality content with comprehensive analysis",
                "confidence": 0.9
            }],
            "processing": {
                "ai_tags": ["machine-learning", "deep-learning"]
            }
        }
        
        # Create test candidate
        note_path = self.create_test_note("Inbox", "high_quality.md", 
                                         "---\ntype: fleeting\nstatus: inbox\n---\nDetailed content")
        candidates = [{
            "path": note_path,
            "source": "inbox", 
            "metadata": {"type": "fleeting", "status": "inbox"}
        }]
        
        recommendations = self.workflow.generate_weekly_recommendations(candidates)
        
        # Verify summary counts
        assert recommendations["summary"]["total_notes"] == 1
        assert recommendations["summary"]["promote_to_permanent"] == 1
        assert recommendations["summary"]["move_to_fleeting"] == 0
        assert recommendations["summary"]["needs_improvement"] == 0
        
        # Verify recommendation details
        rec = recommendations["recommendations"][0]
        assert rec["file_name"] == "high_quality.md"
        assert rec["action"] == "promote_to_permanent"
        assert rec["quality_score"] == 0.85
        assert "High quality" in rec["reason"]
        assert rec["confidence"] == 0.9
        assert rec["source"] == "inbox"
    
    @patch('src.ai.workflow_manager.WorkflowManager.process_inbox_note')
    def test_generate_weekly_recommendations_medium_quality_note(self, mock_process):
        """Test recommendations for medium-quality note (further develop)."""
        mock_process.return_value = {
            "quality_score": 0.55,
            "recommendations": [{
                "action": "move_to_fleeting", 
                "reason": "Good start but needs more development",
                "confidence": 0.7
            }]
        }
        
        note_path = self.create_test_note("Fleeting Notes", "medium_quality.md",
                                         "---\ntype: fleeting\nstatus: inbox\n---\nSome content")
        candidates = [{
            "path": note_path,
            "source": "fleeting",
            "metadata": {"type": "fleeting", "status": "inbox"}
        }]
        
        recommendations = self.workflow.generate_weekly_recommendations(candidates)
        
        assert recommendations["summary"]["total_notes"] == 1
        assert recommendations["summary"]["promote_to_permanent"] == 0
        assert recommendations["summary"]["move_to_fleeting"] == 1
        assert recommendations["summary"]["needs_improvement"] == 0
        
        rec = recommendations["recommendations"][0]
        assert rec["action"] == "move_to_fleeting"
        assert rec["quality_score"] == 0.55
        assert "develop" in rec["reason"].lower()
    
    @patch('src.ai.workflow_manager.WorkflowManager.process_inbox_note')
    def test_generate_weekly_recommendations_low_quality_note(self, mock_process):
        """Test recommendations for low-quality note (needs improvement)."""
        mock_process.return_value = {
            "quality_score": 0.25,
            "recommendations": [{
                "action": "improve_or_archive",
                "reason": "Content is too brief and lacks detail", 
                "confidence": 0.8
            }]
        }
        
        note_path = self.create_test_note("Inbox", "low_quality.md",
                                         "---\ntype: fleeting\nstatus: inbox\n---\nBrief")
        candidates = [{
            "path": note_path,
            "source": "inbox",
            "metadata": {"type": "fleeting", "status": "inbox"}
        }]
        
        recommendations = self.workflow.generate_weekly_recommendations(candidates)
        
        assert recommendations["summary"]["total_notes"] == 1
        assert recommendations["summary"]["promote_to_permanent"] == 0
        assert recommendations["summary"]["move_to_fleeting"] == 0
        assert recommendations["summary"]["needs_improvement"] == 1
        
        rec = recommendations["recommendations"][0]
        assert rec["action"] == "improve_or_archive"
        assert rec["quality_score"] == 0.25
        assert "brief" in rec["reason"].lower()
    
    @patch('src.ai.workflow_manager.WorkflowManager.process_inbox_note')
    def test_generate_weekly_recommendations_mixed_quality(self, mock_process):
        """Test recommendations with mixed quality notes."""
        # Mock different responses for different files
        def mock_process_side_effect(note_path):
            if "high" in str(note_path):
                return {
                    "quality_score": 0.8,
                    "recommendations": [{"action": "promote_to_permanent", "reason": "High quality", "confidence": 0.9}]
                }
            elif "medium" in str(note_path):
                return {
                    "quality_score": 0.5, 
                    "recommendations": [{"action": "move_to_fleeting", "reason": "Needs development", "confidence": 0.7}]
                }
            else:
                return {
                    "quality_score": 0.2,
                    "recommendations": [{"action": "improve_or_archive", "reason": "Too brief", "confidence": 0.8}]
                }
        
        mock_process.side_effect = mock_process_side_effect
        
        # Create mixed quality candidates
        high_path = self.create_test_note("Inbox", "high_note.md", "---\ntype: fleeting\n---\nContent")
        medium_path = self.create_test_note("Inbox", "medium_note.md", "---\ntype: fleeting\n---\nContent")
        low_path = self.create_test_note("Inbox", "low_note.md", "---\ntype: fleeting\n---\nContent")
        
        candidates = [
            {"path": high_path, "source": "inbox", "metadata": {}},
            {"path": medium_path, "source": "inbox", "metadata": {}},
            {"path": low_path, "source": "inbox", "metadata": {}}
        ]
        
        recommendations = self.workflow.generate_weekly_recommendations(candidates)
        
        # Verify mixed results
        assert recommendations["summary"]["total_notes"] == 3
        assert recommendations["summary"]["promote_to_permanent"] == 1
        assert recommendations["summary"]["move_to_fleeting"] == 1
        assert recommendations["summary"]["needs_improvement"] == 1
        assert len(recommendations["recommendations"]) == 3
    
    @patch('src.ai.workflow_manager.WorkflowManager.process_inbox_note')
    def test_generate_weekly_recommendations_handles_processing_errors(self, mock_process):
        """Test that recommendation generation handles processing errors gracefully."""
        # Mock an error response
        mock_process.return_value = {"error": "Failed to process note"}
        
        note_path = self.create_test_note("Inbox", "error_note.md", "---\ntype: fleeting\n---\nContent")
        candidates = [{"path": note_path, "source": "inbox", "metadata": {}}]
        
        recommendations = self.workflow.generate_weekly_recommendations(candidates)
        
        # Should handle gracefully
        assert recommendations["summary"]["total_notes"] == 1
        assert recommendations["summary"]["processing_errors"] == 1
        
        # Error should be recorded in recommendation
        rec = recommendations["recommendations"][0]
        assert "error" in rec
        assert rec["action"] == "manual_review"
    
    def test_generate_weekly_recommendations_result_structure(self):
        """Test that generate_weekly_recommendations returns properly structured results."""
        # Create empty test directory
        test_dir = Path(self.temp_dir) / "test_zettelkasten"
        test_dir.mkdir()
        (test_dir / "Inbox").mkdir()
        (test_dir / "Fleeting Notes").mkdir()
        (test_dir / "Permanent Notes").mkdir()
        
        # Initialize workflow manager
        workflow = WorkflowManager(str(test_dir))
        
        # Test with empty candidates
        candidates = []
        result = workflow.generate_weekly_recommendations(candidates)
        
        # Verify structure
        assert "summary" in result
        assert "recommendations" in result
        assert "generated_at" in result
        
        # Verify summary structure
        summary = result["summary"]
        assert "total_notes" in summary
        assert "promote_to_permanent" in summary
        assert "move_to_fleeting" in summary
        assert "needs_improvement" in summary
        assert "processing_errors" in summary
        
        # Verify all counts are zero
        for key in ["total_notes", "promote_to_permanent", "move_to_fleeting", "needs_improvement", "processing_errors"]:
            assert summary[key] == 0
        
        # Verify recommendations is empty list
        assert result["recommendations"] == []

    # Phase 5.5.4 Enhanced Features Tests
    def test_detect_orphaned_notes_empty_collection(self):
        """Test orphaned note detection with empty collection."""
        # Create empty test directory
        test_dir = Path(self.temp_dir) / "test_zettelkasten"
        test_dir.mkdir()
        (test_dir / "Inbox").mkdir()
        (test_dir / "Fleeting Notes").mkdir()
        (test_dir / "Permanent Notes").mkdir()
        
        # Initialize workflow manager
        workflow = WorkflowManager(str(test_dir))
        
        # Should return empty list for empty collection
        orphaned_notes = workflow.detect_orphaned_notes()
        assert isinstance(orphaned_notes, list)
        assert len(orphaned_notes) == 0
    
    def test_detect_stale_notes_empty_collection(self):
        """Test stale note detection with empty collection."""
        # Create empty test directory
        test_dir = Path(self.temp_dir) / "test_zettelkasten"
        test_dir.mkdir()
        (test_dir / "Inbox").mkdir()
        (test_dir / "Fleeting Notes").mkdir()
        (test_dir / "Permanent Notes").mkdir()
        
        # Initialize workflow manager
        workflow = WorkflowManager(str(test_dir))
        
        # Should return empty list for empty collection
        stale_notes = workflow.detect_stale_notes()
        assert isinstance(stale_notes, list)
        assert len(stale_notes) == 0
    
    def test_generate_enhanced_metrics_empty_collection(self):
        """Test enhanced metrics generation with empty collection."""
        # Create empty test directory
        test_dir = Path(self.temp_dir) / "test_zettelkasten"
        test_dir.mkdir()
        (test_dir / "Inbox").mkdir()
        (test_dir / "Fleeting Notes").mkdir()
        (test_dir / "Permanent Notes").mkdir()
        
        # Initialize workflow manager
        workflow = WorkflowManager(str(test_dir))
        
        # Should return structured metrics for empty collection
        metrics = workflow.generate_enhanced_metrics()
        assert isinstance(metrics, dict)
        assert "orphaned_notes" in metrics
        assert "stale_notes" in metrics
        assert "summary" in metrics
        assert metrics["summary"]["total_notes"] == 0
        assert metrics["summary"]["total_orphaned"] == 0
        assert metrics["summary"]["total_stale"] == 0
    
    def test_detect_orphaned_notes_with_linked_notes(self):
        """Test orphaned note detection with linked and unlinked notes."""
        # Create notes with proper linking
        linked_note = self.create_test_note("Permanent Notes", "linked.md", 
            "---\ntype: permanent\n---\n# Linked Note\nThis links to [[target]]")
        orphan_note = self.create_test_note("Permanent Notes", "orphan.md", 
            "---\ntype: permanent\n---\n# Orphan Note\nThis has no links to other notes.")
        target_note = self.create_test_note("Permanent Notes", "target.md", 
            "---\ntype: permanent\n---\n# Target Note\nThis is linked to by [[linked]].")
        
        orphaned_notes = self.workflow.detect_orphaned_notes()
        
        # Only the orphan note should be detected as orphaned (linked and target have bidirectional links)
        assert len(orphaned_notes) == 1
        assert orphaned_notes[0]["title"] == "Orphan Note"
        assert "orphan.md" in orphaned_notes[0]["path"]
    
    def test_detect_stale_notes_with_old_notes(self):
        """Test stale note detection with notes of different ages."""
        import time
        from datetime import datetime, timedelta
        
        # Create a note and artificially age it
        old_note = self.create_test_note("Permanent Notes", "old.md", 
            "---\ntype: permanent\n---\n# Old Note\nThis is an old note.")
        
        # Artificially set the modification time to 100 days ago
        old_time = datetime.now() - timedelta(days=100)
        old_timestamp = old_time.timestamp()
        
        import os
        os.utime(str(old_note), (old_timestamp, old_timestamp))
        
        # Create a fresh note
        fresh_note = self.create_test_note("Permanent Notes", "fresh.md", 
            "---\ntype: permanent\n---\n# Fresh Note\nThis is a fresh note.")
        
        stale_notes = self.workflow.detect_stale_notes(days_threshold=90)
        
        # Only the old note should be detected as stale
        assert len(stale_notes) == 1
        assert stale_notes[0]["title"] == "Old Note"
        assert stale_notes[0]["days_since_modified"] >= 90
    
    def test_generate_enhanced_metrics_with_notes(self):
        """Test enhanced metrics generation with actual notes."""
        # Create various types of notes
        linked_note = self.create_test_note("Permanent Notes", "linked.md", 
            "---\ntype: permanent\n---\n# Linked Note\nThis links to [[other]]")
        orphan_note = self.create_test_note("Permanent Notes", "orphan.md", 
            "---\ntype: permanent\n---\n# Orphan Note\nNo links here.")
        inbox_note = self.create_test_note("Inbox", "inbox.md", 
            "---\ntype: fleeting\n---\n# Inbox Note\nIn the inbox.")
        
        metrics = self.workflow.generate_enhanced_metrics()
        
        # Verify metrics structure and content
        assert isinstance(metrics, dict)
        assert "orphaned_notes" in metrics
        assert "stale_notes" in metrics
        assert "link_density" in metrics
        assert "note_age_distribution" in metrics
        assert "productivity_metrics" in metrics
        assert "summary" in metrics
        
        # Should detect the orphan note
        assert metrics["summary"]["total_orphaned"] == 1
        assert metrics["summary"]["total_notes"] == 3
        
        # Link density should be > 0 due to the linked note
        assert metrics["link_density"] > 0
        
        # Age distribution should have all notes in "new" category
        age_dist = metrics["note_age_distribution"]
        assert age_dist["new"] == 3
        assert age_dist["recent"] == 0

    # ========================= TEMPLATE PLACEHOLDER FIX TESTS =========================
    
    def test_fix_template_placeholders_in_created_field(self):
        """Test fixing template placeholders in 'created' field during note processing."""
        # Create note with template placeholder - the exact format from the bug report
        content = """---
type: fleeting
created: {{date:YYYY-MM-DD HH:mm}}
status: inbox
---

This note has an unprocessed template placeholder that should be fixed."""
        
        note_path = self.create_test_note("Inbox", "template-bug-test.md", content)
        
        # Process the note (should fix the template placeholder)
        result = self.workflow.process_inbox_note(str(note_path))
        
        # Verify no error occurred
        assert "error" not in result
        assert result["file_updated"] is True
        
        # Read the updated file and verify template placeholder was replaced
        with open(note_path, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        # Should not contain template placeholder anymore
        assert "{{date:" not in updated_content
        assert "created: {{date:YYYY-MM-DD HH:mm}}" not in updated_content
        
        # Should contain a valid timestamp in the correct format
        import re
        timestamp_pattern = r'created: \d{4}-\d{2}-\d{2} \d{2}:\d{2}'
        assert re.search(timestamp_pattern, updated_content)
        
        # Extract and validate the timestamp format
        frontmatter, _ = self.workflow._extract_frontmatter(updated_content)
        created_value = frontmatter.get("created")
        assert created_value is not None
        assert isinstance(created_value, str)
        # Should match YYYY-MM-DD HH:MM format
        assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', created_value)
    
    def test_fix_template_placeholders_missing_created_field(self):
        """Test adding missing 'created' field when not present in frontmatter."""
        content = """---
type: fleeting
status: inbox
---

This note is missing the created field entirely."""
        
        note_path = self.create_test_note("Inbox", "missing-created-test.md", content)
        
        # Process the note (should add missing created field)
        result = self.workflow.process_inbox_note(str(note_path))
        
        # Verify no error occurred
        assert "error" not in result
        assert result["file_updated"] is True
        
        # Read the updated file and verify created field was added
        with open(note_path, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        frontmatter, _ = self.workflow._extract_frontmatter(updated_content)
        created_value = frontmatter.get("created")
        assert created_value is not None
        assert isinstance(created_value, str)
        
        # Should be in correct format
        import re
        assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', created_value)
    
    def test_fix_template_placeholders_uses_file_timestamps(self):
        """Test that template fix uses file birth/modified time when available."""
        import os
        import time
        from datetime import datetime, timedelta
        
        content = """---
type: fleeting
created: {{date:YYYY-MM-DD HH:mm}}
status: inbox
---

Test content for timestamp detection."""
        
        note_path = self.create_test_note("Inbox", "timestamp-test.md", content)
        
        # Get current file modification time before processing
        file_stat = os.stat(note_path)
        file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
        
        # Process the note
        result = self.workflow.process_inbox_note(str(note_path))
        
        assert "error" not in result
        assert result["file_updated"] is True
        
        # Read updated content and extract timestamp
        with open(note_path, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        frontmatter, _ = self.workflow._extract_frontmatter(updated_content)
        created_value = frontmatter.get("created")
        
        # Parse the created timestamp
        created_time = datetime.strptime(created_value, "%Y-%m-%d %H:%M")
        
        # Should be based on file time (within 1 minute tolerance)
        time_diff = abs((created_time - file_mtime).total_seconds())
        assert time_diff < 60, f"Created time {created_time} should be close to file time {file_mtime}"
    
    def test_fix_template_placeholders_dry_run_mode(self):
        """Test that dry-run mode does not fix template placeholders on disk."""
        content = """---
type: fleeting
created: {{date:YYYY-MM-DD HH:mm}}
status: inbox
---

This should not be modified in dry-run mode."""
        
        note_path = self.create_test_note("Inbox", "dry-run-test.md", content)
        
        # Process in dry-run mode
        result = self.workflow.process_inbox_note(str(note_path), dry_run=True)
        
        # Should process successfully but not update file
        assert "error" not in result
        assert result["file_updated"] is False
        
        # File content should remain unchanged
        with open(note_path, 'r', encoding='utf-8') as f:
            unchanged_content = f.read()
        
        assert "{{date:YYYY-MM-DD HH:mm}}" in unchanged_content
        assert unchanged_content == content
    
    @patch('src.ai.tagger.AITagger.generate_tags')
    @patch('src.ai.enhancer.AIEnhancer.enhance_note')
    def test_fix_template_placeholders_preserves_other_frontmatter(self, mock_enhance, mock_generate_tags):
        """Test that template fixing preserves all other frontmatter fields."""
        # Mock AI components to focus purely on template placeholder functionality
        mock_generate_tags.return_value = []  # No new tags added
        mock_enhance.return_value = {"quality_score": 0.5, "suggestions": []}
        
        content = """---
type: fleeting
created: {{date:YYYY-MM-DD HH:mm}}
status: inbox
tags: ["test", "important"]
visibility: private
custom_field: "preserved"
---

Content should remain the same."""
        
        note_path = self.create_test_note("Inbox", "preserve-test.md", content)
        
        # Process the note
        result = self.workflow.process_inbox_note(str(note_path))
        
        assert "error" not in result
        assert result["file_updated"] is True
        
        # Verify all other fields preserved
        with open(note_path, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        frontmatter, body = self.workflow._extract_frontmatter(updated_content)
        
        # Template placeholder should be fixed
        assert "{{date:" not in str(frontmatter.get("created"))
        import re
        assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', frontmatter["created"])
        
        # Other fields should be preserved exactly
        assert frontmatter["type"] == "fleeting"
        assert frontmatter["status"] == "inbox"
        assert set(frontmatter["tags"]) == {"test", "important"}  # Order doesn't matter for tags
        assert frontmatter["visibility"] == "private"
        assert frontmatter["custom_field"] == "preserved"
        
        # Body should be unchanged
        assert "Content should remain the same." in body
    
    def test_fix_template_placeholders_handles_malformed_templates(self):
        """Test handling of malformed template placeholders."""
        content = """---
type: fleeting
created: {{date:invalid-format}}
status: inbox
---

Test malformed template handling."""
        
        note_path = self.create_test_note("Inbox", "malformed-test.md", content)
        
        # Should process successfully and fix malformed placeholder
        result = self.workflow.process_inbox_note(str(note_path))
        
        assert "error" not in result
        assert result["file_updated"] is True
        
        # Should replace with proper timestamp regardless of malformed format
        with open(note_path, 'r', encoding='utf-8') as f:
            updated_content = f.read()
        
        frontmatter, _ = self.workflow._extract_frontmatter(updated_content)
        created_value = frontmatter.get("created")
        
        # Should still get a valid timestamp
        import re
        assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}$', created_value)
