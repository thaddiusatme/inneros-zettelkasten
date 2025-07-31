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
tags: ["machine-learning", "deep-learning"]
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
            "Fleeting Notes": 10,
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
