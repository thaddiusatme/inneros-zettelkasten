"""
Unit tests for the analytics module.
"""

import sys
import os

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, "src")
sys.path.insert(0, src_dir)

import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from ai.analytics import NoteAnalytics, NoteStats


class TestNoteAnalytics:
    """Test cases for NoteAnalytics class."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.notes_dir = Path(self.temp_dir)
        self.analytics = NoteAnalytics(str(self.notes_dir))

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def create_test_note(self, filename: str, content: str):
        """Helper to create a test note."""
        note_path = self.notes_dir / filename
        note_path.parent.mkdir(parents=True, exist_ok=True)

        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content)

        return note_path

    def test_initialization(self):
        """Test analytics initialization."""
        assert self.analytics.notes_dir == self.notes_dir
        assert self.analytics.ai_tagger is not None
        assert self.analytics.ai_summarizer is not None
        assert self.analytics.ai_connections is not None

    def test_extract_frontmatter_with_yaml(self):
        """Test YAML frontmatter extraction."""
        content = """---
type: permanent
created: 2024-01-01 10:00
tags: ["ai", "testing"]
status: published
---

This is the body content."""

        frontmatter, body = self.analytics._extract_frontmatter(content)

        assert frontmatter["type"] == "permanent"
        assert frontmatter["created"] == "2024-01-01 10:00"
        assert frontmatter["tags"] == ["ai", "testing"]
        assert frontmatter["status"] == "published"
        assert body.strip() == "This is the body content."

    def test_extract_frontmatter_without_yaml(self):
        """Test content without frontmatter."""
        content = "This is just plain content without frontmatter."

        frontmatter, body = self.analytics._extract_frontmatter(content)

        assert frontmatter == {}
        assert body == content

    def test_parse_date_valid_formats(self):
        """Test date parsing with various formats."""
        test_cases = [
            ("2024-01-01 10:00", "%Y-%m-%d %H:%M"),
            ("2024-01-01", "%Y-%m-%d"),
            ("2024-01-01T10:00:00", "%Y-%m-%dT%H:%M:%S"),
            ("2024-01-01 10:00:00", "%Y-%m-%d %H:%M:%S"),
        ]

        for date_str, expected_format in test_cases:
            result = self.analytics._parse_date(date_str)
            assert result is not None
            assert isinstance(result, datetime)

    def test_parse_date_invalid(self):
        """Test date parsing with invalid formats."""
        invalid_dates = ["invalid-date", "", None, "2024/01/01"]

        for date_str in invalid_dates:
            result = self.analytics._parse_date(date_str)
            assert result is None

    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        # High quality note
        frontmatter = {
            "type": "permanent",
            "created": "2024-01-01",
            "status": "published",
        }
        score = self.analytics._calculate_quality_score(1000, 5, 3, frontmatter)
        assert score > 0.8

        # Medium quality note
        frontmatter = {"type": "fleeting"}
        score = self.analytics._calculate_quality_score(200, 2, 1, frontmatter)
        assert 0.3 < score < 0.7

        # Low quality note
        score = self.analytics._calculate_quality_score(50, 0, 0, {})
        assert score < 0.3

    def test_analyze_note_complete(self):
        """Test complete note analysis."""
        content = """---
type: permanent
created: 2024-01-01 10:00
tags: ["ai", "testing", "analytics"]
status: published
ai_summary: This is an AI-generated summary
---

This is a comprehensive note about artificial intelligence and testing.
It contains multiple paragraphs with detailed information.
The note includes several [[internal-links]] to other notes.
It also has enough content to warrant a quality analysis.

Here's another paragraph with more content to increase word count.
This helps test the word counting functionality of the analytics system.
"""

        note_path = self.create_test_note("test-note.md", content)
        stats = self.analytics._analyze_note(note_path)

        assert stats is not None
        assert stats.filename == "test-note.md"
        assert stats.word_count > 50
        assert stats.tag_count == 3
        assert stats.link_count == 1
        assert stats.note_type == "permanent"
        assert stats.status == "published"
        assert stats.has_summary is True
        assert stats.quality_score > 0.5
        assert stats.creation_date is not None
        assert stats.last_modified is not None

    def test_analyze_note_minimal(self):
        """Test analysis of minimal note."""
        content = "Just a simple note without frontmatter."

        note_path = self.create_test_note("minimal.md", content)
        stats = self.analytics._analyze_note(note_path)

        assert stats is not None
        assert stats.filename == "minimal.md"
        assert (
            stats.word_count == 6
        )  # "Just a simple note without frontmatter." = 6 words
        assert stats.tag_count == 0
        assert stats.link_count == 0
        assert stats.note_type == "unknown"
        assert stats.status == "unknown"
        assert stats.has_summary is False
        assert stats.quality_score < 0.3

    def test_scan_notes_multiple_files(self):
        """Test scanning multiple note files."""
        # Create multiple test notes
        notes_data = [
            (
                "note1.md",
                """---
type: permanent
tags: ["test"]
---
Content for note 1 with some text.""",
            ),
            (
                "note2.md",
                """---
type: fleeting
---
Shorter content.""",
            ),
            (
                "subdir/note3.md",
                """---
type: literature
tags: ["research", "academic"]
---
Academic content with more detailed information and analysis.""",
            ),
        ]

        for filename, content in notes_data:
            self.create_test_note(filename, content)

        notes = self.analytics.scan_notes()

        assert len(notes) == 3
        filenames = [note.filename for note in notes]
        assert "note1.md" in filenames
        assert "note2.md" in filenames
        assert "note3.md" in filenames

    def test_generate_report_empty_directory(self):
        """Test report generation with no notes."""
        report = self.analytics.generate_report()

        assert "error" in report
        assert report["error"] == "No notes found"

    def test_generate_report_with_notes(self):
        """Test comprehensive report generation."""
        # Create test notes
        notes_data = [
            (
                "high-quality.md",
                """---
type: permanent
created: 2024-01-01 10:00
tags: ["ai", "machine-learning", "research"]
status: published
ai_summary: High quality note summary
---
This is a high-quality permanent note with comprehensive content.
It includes multiple paragraphs, proper tagging, and internal links.
The content is well-structured and provides valuable information.
It has sufficient length and depth to be considered high quality.
""",
            ),
            (
                "medium-quality.md",
                """---
type: fleeting
tags: ["idea"]
---
This is a medium quality fleeting note.
It has some content but needs development.
""",
            ),
            (
                "low-quality.md",
                """---
type: unknown
---
Short note.""",
            ),
        ]

        for filename, content in notes_data:
            self.create_test_note(filename, content)

        report = self.analytics.generate_report()

        # Check overview
        assert "overview" in report
        overview = report["overview"]
        assert overview["total_notes"] == 3
        assert overview["total_words"] > 0
        assert overview["average_words_per_note"] > 0
        assert 0 <= overview["average_quality_score"] <= 1
        assert overview["notes_with_ai_summaries"] == 1

        # Check distributions
        assert "distributions" in report
        distributions = report["distributions"]
        assert "permanent" in distributions["note_types"]
        assert "fleeting" in distributions["note_types"]

        # Check quality metrics
        assert "quality_metrics" in report
        quality = report["quality_metrics"]
        assert quality["high_quality_notes"] >= 0
        assert quality["medium_quality_notes"] >= 0
        assert quality["low_quality_notes"] >= 0

        # Check recommendations
        assert "recommendations" in report
        assert isinstance(report["recommendations"], list)

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        # Create notes with various quality levels
        notes = [
            NoteStats(
                "high.md", 800, 5, 3, None, None, "permanent", "published", True, 0.9
            ),
            NoteStats(
                "medium.md", 300, 2, 1, None, None, "fleeting", "draft", False, 0.6
            ),
            NoteStats("low.md", 50, 0, 0, None, None, "unknown", "inbox", False, 0.2),
            NoteStats(
                "untagged.md",
                200,
                0,
                2,
                None,
                None,
                "permanent",
                "published",
                False,
                0.5,
            ),
            NoteStats(
                "long-no-summary.md",
                1000,
                3,
                2,
                None,
                None,
                "permanent",
                "published",
                False,
                0.7,
            ),
        ]

        recommendations = self.analytics._generate_recommendations(notes)

        # Should recommend improving low quality notes
        low_quality_rec = any("low-quality" in rec for rec in recommendations)
        assert low_quality_rec

        # Should recommend adding tags
        tagging_rec = any("tags" in rec for rec in recommendations)
        assert tagging_rec

        # Should recommend AI summaries for long notes
        summary_rec = any("summaries" in rec for rec in recommendations)
        assert summary_rec

    def test_export_report(self):
        """Test report export functionality."""
        # Create a test note
        self.create_test_note(
            "test.md",
            """---
type: permanent
---
Test content.""",
        )

        output_file = self.notes_dir / "report.json"
        result = self.analytics.export_report(str(output_file))

        assert output_file.exists()
        assert f"Report exported to {output_file}" in result

        # Verify JSON content
        import json

        with open(output_file, "r") as f:
            report_data = json.load(f)

        assert "overview" in report_data
        assert "distributions" in report_data

    def test_create_connection_graph(self):
        """Test connection graph creation (placeholder)."""
        result = self.analytics.create_connection_graph("test_graph.png")

        # Should return error message when matplotlib is not available
        assert "error" in result or "message" in result
        assert "output_file" in result
        assert result["output_file"] == "test_graph.png"


class TestNoteStats:
    """Test cases for NoteStats dataclass."""

    def test_note_stats_creation(self):
        """Test NoteStats creation."""
        stats = NoteStats(
            filename="test.md",
            word_count=500,
            tag_count=3,
            link_count=2,
            creation_date=datetime.now(),
            last_modified=datetime.now(),
            note_type="permanent",
            status="published",
            has_summary=True,
            quality_score=0.8,
        )

        assert stats.filename == "test.md"
        assert stats.word_count == 500
        assert stats.tag_count == 3
        assert stats.link_count == 2
        assert stats.note_type == "permanent"
        assert stats.status == "published"
        assert stats.has_summary is True
        assert stats.quality_score == 0.8

    def test_note_stats_optional_fields(self):
        """Test NoteStats with optional None fields."""
        stats = NoteStats(
            filename="test.md",
            word_count=100,
            tag_count=0,
            link_count=0,
            creation_date=None,
            last_modified=None,
            note_type="unknown",
            status="inbox",
            has_summary=False,
            quality_score=0.3,
        )

        assert stats.creation_date is None
        assert stats.last_modified is None
        assert stats.has_summary is False
