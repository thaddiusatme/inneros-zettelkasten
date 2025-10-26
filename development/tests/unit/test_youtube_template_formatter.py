"""
Tests for YouTubeTemplateFormatter

TDD Iteration 3 - RED Phase: All tests should FAIL initially
"""

from ai.youtube_template_formatter import YouTubeTemplateFormatter


class TestYouTubeTemplateFormatterBasic:
    """Test basic template formatting functionality."""

    def test_format_quotes_for_markdown(self):
        """
        Test converting quote objects to markdown bullet format.
        
        RED Phase: Should fail - format_quotes_section not implemented
        """
        formatter = YouTubeTemplateFormatter()

        quotes = [
            {
                "text": "AI will transform everything",
                "timestamp": "01:15",
                "relevance_score": 0.88,
                "context": "Discusses AI impact on creators",
                "category": "key-insight"
            },
            {
                "text": "Start building your empire today",
                "timestamp": "05:30",
                "relevance_score": 0.92,
                "context": "Actionable advice for entrepreneurs",
                "category": "actionable"
            }
        ]

        result = formatter.format_quotes_section(quotes)

        # Should include both quotes
        assert "AI will transform everything" in result
        assert "Start building your empire today" in result

        # Should include timestamps
        assert "01:15" in result
        assert "05:30" in result

        # Should include context
        assert "Discusses AI impact" in result
        assert "Actionable advice" in result

        # Should be markdown formatted
        assert ">" in result or "-" in result or "*" in result

    def test_group_quotes_by_category(self):
        """
        Test organizing quotes by category (key-insight, actionable, etc).
        
        RED Phase: Should fail - group_quotes_by_category not implemented
        """
        formatter = YouTubeTemplateFormatter()

        quotes = [
            {"text": "Quote 1", "category": "key-insight", "timestamp": "00:10"},
            {"text": "Quote 2", "category": "actionable", "timestamp": "00:20"},
            {"text": "Quote 3", "category": "key-insight", "timestamp": "00:30"},
            {"text": "Quote 4", "category": "definition", "timestamp": "00:40"},
            {"text": "Quote 5", "category": "actionable", "timestamp": "00:50"}
        ]

        grouped = formatter.group_quotes_by_category(quotes)

        # Should have 3 categories
        assert len(grouped) == 3
        assert "key-insight" in grouped
        assert "actionable" in grouped
        assert "definition" in grouped

        # Should group correctly
        assert len(grouped["key-insight"]) == 2
        assert len(grouped["actionable"]) == 2
        assert len(grouped["definition"]) == 1

        # Should preserve quote data
        assert grouped["key-insight"][0]["text"] == "Quote 1"
        assert grouped["actionable"][0]["text"] == "Quote 2"

    def test_generate_summary_section(self):
        """
        Test formatting summary with themes.
        
        RED Phase: Should fail - format_summary_section not implemented
        """
        formatter = YouTubeTemplateFormatter()

        summary = "This video discusses AI trends and creator economy opportunities in 2026."
        themes = ["AI", "Creator Economy", "Digital Entrepreneurship"]

        result = formatter.format_summary_section(summary, themes)

        # Should include summary text
        assert "AI trends" in result
        assert "creator economy" in result

        # Should include all themes
        assert "AI" in result
        assert "Creator Economy" in result
        assert "Digital Entrepreneurship" in result

        # Should be markdown formatted
        assert "#" in result or "-" in result or "*" in result


class TestYouTubeTemplateFormatterTimestamps:
    """Test timestamp link generation."""

    def test_format_timestamps_as_youtube_links(self):
        """
        Test creating clickable YouTube timestamp links.
        
        Format: [MM:SS](https://youtu.be/VIDEO_ID?t=SECONDS)
        
        RED Phase: Should fail - create_timestamp_link not implemented
        """
        formatter = YouTubeTemplateFormatter()

        # Test MM:SS format
        link1 = formatter.create_timestamp_link("01:15", "dQw4w9WgXcQ")
        assert link1 == "[01:15](https://youtu.be/dQw4w9WgXcQ?t=75)"

        # Test different timestamp
        link2 = formatter.create_timestamp_link("10:30", "abc123xyz")
        assert link2 == "[10:30](https://youtu.be/abc123xyz?t=630)"

        # Test HH:MM:SS format
        link3 = formatter.create_timestamp_link("01:05:30", "test456")
        assert link3 == "[01:05:30](https://youtu.be/test456?t=3930)"

        # Test edge case: 00:00
        link4 = formatter.create_timestamp_link("00:00", "start123")
        assert link4 == "[00:00](https://youtu.be/start123?t=0)"


class TestYouTubeTemplateFormatterIntegration:
    """Test complete template integration."""

    def test_template_complete_integration(self):
        """
        Test full template formatting with all sections.
        
        RED Phase: Should fail - format_template not implemented
        """
        formatter = YouTubeTemplateFormatter()

        quotes_data = {
            "summary": "Video about AI and creator economy in 2026",
            "quotes": [
                {
                    "text": "AI will amplify creators by 10x",
                    "timestamp": "01:15",
                    "relevance_score": 0.88,
                    "context": "Discusses AI impact",
                    "category": "key-insight"
                },
                {
                    "text": "Start your empire today",
                    "timestamp": "05:30",
                    "relevance_score": 0.92,
                    "context": "Actionable entrepreneurship advice",
                    "category": "actionable"
                }
            ],
            "key_themes": ["AI", "Creator Economy", "Entrepreneurship"]
        }

        result = formatter.format_template(
            quotes_data=quotes_data,
            video_id="test123",
            video_title="Test Video"
        )

        # Should return dict with markdown and metadata
        assert "markdown" in result
        assert "metadata" in result

        markdown = result["markdown"]

        # Should include summary section
        assert "AI and creator economy" in markdown

        # Should include themes
        assert "AI" in markdown
        assert "Creator Economy" in markdown

        # Should include quotes
        assert "AI will amplify creators" in markdown
        assert "Start your empire today" in markdown

        # Should include timestamps as links
        assert "youtu.be/test123" in markdown

        # Should have metadata
        assert result["metadata"]["quote_count"] == 2
        assert "key-insight" in result["metadata"]["categories"]
        assert "actionable" in result["metadata"]["categories"]

    def test_preserve_quote_metadata(self):
        """
        Test that scores and context are preserved in output.
        
        RED Phase: Should fail - metadata preservation not implemented
        """
        formatter = YouTubeTemplateFormatter()

        quotes_data = {
            "summary": "Test summary",
            "quotes": [
                {
                    "text": "Important quote",
                    "timestamp": "02:30",
                    "relevance_score": 0.95,
                    "context": "Why this matters for users",
                    "category": "key-insight"
                }
            ],
            "key_themes": ["Test Theme"]
        }

        result = formatter.format_template(
            quotes_data=quotes_data,
            video_id="meta123"
        )

        markdown = result["markdown"]

        # Should preserve relevance score
        assert "0.95" in markdown or "95" in markdown

        # Should preserve context
        assert "Why this matters" in markdown

        # Metadata should include quality info
        assert result["metadata"]["average_score"] >= 0.95

    def test_handle_empty_quotes_gracefully(self):
        """
        Test template works with zero quotes (edge case).
        
        RED Phase: Should fail - empty quote handling not implemented
        """
        formatter = YouTubeTemplateFormatter()

        quotes_data = {
            "summary": "Video summary with no quality quotes found",
            "quotes": [],  # Empty quotes list
            "key_themes": ["General Topic"]
        }

        result = formatter.format_template(
            quotes_data=quotes_data,
            video_id="empty123"
        )

        markdown = result["markdown"]

        # Should still have summary
        assert "Video summary" in markdown

        # Should still have themes
        assert "General Topic" in markdown

        # Should have graceful message about no quotes
        assert "No quotes" in markdown or "no high-quality quotes" in markdown.lower()

        # Metadata should reflect empty state
        assert result["metadata"]["quote_count"] == 0
        assert len(result["metadata"]["categories"]) == 0
