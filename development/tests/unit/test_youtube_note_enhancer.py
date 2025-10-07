"""
TDD Iteration 1: YouTubeNoteEnhancer - RED Phase
Tests for enhancing Templater-created YouTube notes with AI quotes

Following proven TDD patterns from Smart Link Management and Directory Organization.
"""

import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import tempfile
import shutil

# Import will fail initially - this is expected for RED phase
from src.ai.youtube_note_enhancer import (
    YouTubeNoteEnhancer,
    NoteStructure,
    EnhanceResult,
    QuotesData,
)


class TestNoteStructureParsing:
    """Test parsing of Templater-created note structure"""

    @pytest.fixture
    def sample_templater_note(self) -> str:
        """Real structure from Templater template"""
        return """---
type: literature
created: 2025-10-03 09:53
status: inbox
tags: [youtube, video-content]
visibility: private
source: youtube
author: 
video_id: rYCQZ2osLq4
channel: Majorkill
---

# AI Channels Are Taking Over Warhammer 40k Lore

## Video Information
- **Channel**: Majorkill
- **Video URL**: https://www.youtube.com/watch?v=rYCQZ2osLq4
- **Video ID**: `rYCQZ2osLq4`
- **Date Saved**: 2025-10-03

## Why I'm Saving This
This is important in the fight against AI slop

## Key Takeaways
<!-- As you watch, capture key points here -->

### Main Insight
> 

**Timestamp**: 

### Supporting Points
<!-- Add more as you watch -->

## My Thoughts & Applications
"""

    @pytest.fixture
    def sample_quotes_data(self) -> QuotesData:
        """Sample AI-extracted quotes"""
        return QuotesData(
            key_insights=[
                {"timestamp": "00:15", "quote": "AI is transforming content creation", "context": "Introduction"}
            ],
            actionable=[
                {"timestamp": "05:30", "quote": "Focus on quality over quantity", "context": "Strategy"}
            ],
            notable=[
                {"timestamp": "10:00", "quote": "Community feedback is crucial", "context": "Engagement"}
            ],
            definitions=[
                {"timestamp": "02:45", "quote": "AI slop: low-quality AI-generated content", "context": "Terminology"}
            ],
        )

    def test_parse_note_structure_basic(self, sample_templater_note):
        """RED: Parse basic note with all sections present"""
        enhancer = YouTubeNoteEnhancer()
        result = enhancer.parse_note_structure(sample_templater_note)
        
        assert result.has_frontmatter is True
        assert result.has_why_section is True
        assert result.title == "AI Channels Are Taking Over Warhammer 40k Lore"
        assert "youtube" in result.frontmatter_data.get("tags", [])
        assert result.why_section_content == "This is important in the fight against AI slop"

    def test_parse_note_structure_missing_sections(self):
        """RED: Handle note missing 'Why I'm Saving This' section"""
        note_without_why = """---
type: literature
created: 2025-10-03 09:53
---

# Test Video

## Video Information
- URL: test
"""
        enhancer = YouTubeNoteEnhancer()
        result = enhancer.parse_note_structure(note_without_why)
        
        assert result.has_why_section is False
        assert result.insertion_point is not None  # Should still find insertion point

    def test_parse_note_structure_malformed_yaml(self):
        """RED: Gracefully handle malformed YAML frontmatter"""
        malformed_note = """---
type: literature
created: {{date:YYYY-MM-DD HH:mm}}
tags: [unclosed bracket
---

# Test Video
"""
        enhancer = YouTubeNoteEnhancer()
        
        # Should not crash, but return structure with error flag
        result = enhancer.parse_note_structure(malformed_note)
        assert result.has_parse_errors is True
        assert result.error_message is not None

    def test_identify_insertion_point(self, sample_templater_note):
        """RED: Find correct insertion point after 'Why I'm Saving This'"""
        enhancer = YouTubeNoteEnhancer()
        insertion_line = enhancer.identify_insertion_point(sample_templater_note)
        
        # Should be after "Why I'm Saving This" section content
        # but before "Key Takeaways" section
        lines = sample_templater_note.split("\n")
        why_index = next(i for i, line in enumerate(lines) if "## Why I'm Saving This" in line)
        takeaways_index = next(i for i, line in enumerate(lines) if "## Key Takeaways" in line)
        
        assert why_index < insertion_line < takeaways_index


class TestQuoteSectionInsertion:
    """Test insertion of AI quotes into note structure"""

    @pytest.fixture
    def sample_quotes_markdown(self) -> str:
        """Expected quotes section format"""
        return """## Extracted Quotes

### 🎯 Key Insights

> [00:15] "AI is transforming content creation"
> - **Context**: Introduction
> - **Relevance**: High

### 💡 Actionable Insights

> [05:30] "Focus on quality over quantity"
> - **Context**: Strategy
> - **Relevance**: High
"""

    def test_insert_quotes_section_basic(self, sample_quotes_markdown):
        """RED: Insert quotes section at specified line"""
        original = """## Why I'm Saving This
Important content

## Key Takeaways
"""
        enhancer = YouTubeNoteEnhancer()
        result = enhancer.insert_quotes_section(original, sample_quotes_markdown, insertion_line=2)
        
        assert "## Extracted Quotes" in result
        assert result.count("##") == 3  # Original 2 + new quotes section

    def test_insert_quotes_section_preserve_content(self):
        """RED: Ensure all original content preserved after insertion"""
        original = """## Why I'm Saving This
Important content

## Key Takeaways
- Point 1
- Point 2

## My Thoughts
Deep analysis here
"""
        quotes = "## Extracted Quotes\n\nQuote content here\n"
        enhancer = YouTubeNoteEnhancer()
        result = enhancer.insert_quotes_section(original, quotes, insertion_line=2)
        
        # All original sections must be present
        assert "Important content" in result
        assert "Point 1" in result
        assert "Deep analysis here" in result
        assert "## Extracted Quotes" in result

    def test_insert_quotes_section_with_categories(self):
        """RED: Support multiple quote categories"""
        quotes_with_categories = """## Extracted Quotes

### 🎯 Key Insights
Quote 1

### 💡 Actionable Insights
Quote 2

### 📝 Notable Quotes
Quote 3

### 📖 Definitions
Quote 4
"""
        original = "## Why\nContent\n\n## Next"
        enhancer = YouTubeNoteEnhancer()
        result = enhancer.insert_quotes_section(original, quotes_with_categories, insertion_line=2)
        
        assert "🎯 Key Insights" in result
        assert "💡 Actionable Insights" in result
        assert "📝 Notable Quotes" in result
        assert "📖 Definitions" in result


class TestFrontmatterUpdate:
    """Test YAML frontmatter modification"""

    def test_update_frontmatter_add_processing_fields(self):
        """RED: Add ai_processed, processed_at, quote_count fields"""
        note = """---
type: literature
created: 2025-10-03 09:53
status: inbox
---

Content here
"""
        enhancer = YouTubeNoteEnhancer()
        metadata = {
            "ai_processed": True,
            "processed_at": "2025-10-06 17:00",
            "quote_count": 12,
            "processing_time_seconds": 1.45,
        }
        
        result = enhancer.update_frontmatter(note, metadata)
        
        assert "ai_processed: true" in result
        assert "processed_at: 2025-10-06 17:00" in result
        assert "quote_count: 12" in result
        assert "processing_time_seconds: 1.45" in result

    def test_update_frontmatter_preserve_existing(self):
        """RED: Don't overwrite existing frontmatter fields"""
        note = """---
type: literature
created: 2025-10-03 09:53
status: inbox
tags: [youtube, important]
custom_field: custom_value
---

Content
"""
        enhancer = YouTubeNoteEnhancer()
        metadata = {"ai_processed": True}
        
        result = enhancer.update_frontmatter(note, metadata)
        
        # All original fields preserved
        assert "type: literature" in result
        assert "created: 2025-10-03 09:53" in result
        assert "tags: [youtube, important]" in result
        assert "custom_field: custom_value" in result
        # New field added
        assert "ai_processed: true" in result


class TestEndToEndEnhancement:
    """Test complete note enhancement workflow"""

    @pytest.fixture
    def temp_note_dir(self):
        """Create temporary directory for test notes"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_note_path(self, temp_note_dir):
        """Create sample note file"""
        note_content = """---
type: literature
created: 2025-10-03 09:53
status: inbox
tags: [youtube, video-content]
visibility: private
source: youtube
video_id: test123
---

# Test Video Title

## Video Information
- **Channel**: Test Channel
- **Video URL**: https://youtube.com/watch?v=test123

## Why I'm Saving This
This is a test reason for saving

## Key Takeaways
<!-- Notes here -->

## My Thoughts & Applications
<!-- Thoughts here -->
"""
        note_path = temp_note_dir / "test-video.md"
        note_path.write_text(note_content)
        return note_path

    def test_enhance_note_end_to_end(self, sample_note_path):
        """RED: Complete enhancement workflow"""
        quotes_data = QuotesData(
            key_insights=[{"timestamp": "00:15", "quote": "Test insight", "context": "Test"}],
            actionable=[],
            notable=[],
            definitions=[],
        )
        
        enhancer = YouTubeNoteEnhancer()
        result = enhancer.enhance_note(sample_note_path, quotes_data)
        
        assert result.success is True
        assert result.backup_path is not None
        assert result.backup_path.exists()
        
        # Read enhanced note
        enhanced_content = sample_note_path.read_text()
        assert "## Extracted Quotes" in enhanced_content
        assert "ai_processed: true" in enhanced_content
        assert "quote_count:" in enhanced_content

    def test_enhance_note_with_backup(self, sample_note_path):
        """RED: Create backup before modification"""
        original_content = sample_note_path.read_text()
        
        quotes_data = QuotesData(key_insights=[], actionable=[], notable=[], definitions=[])
        enhancer = YouTubeNoteEnhancer()
        result = enhancer.enhance_note(sample_note_path, quotes_data)
        
        # Backup should contain original content
        assert result.backup_path.exists()
        backup_content = result.backup_path.read_text()
        assert backup_content == original_content

    def test_enhance_note_rollback_on_failure(self, sample_note_path):
        """RED: Rollback if insertion fails"""
        original_content = sample_note_path.read_text()
        
        # Pass invalid quotes data to trigger failure
        quotes_data = None
        enhancer = YouTubeNoteEnhancer()
        
        with pytest.raises(Exception):
            enhancer.enhance_note(sample_note_path, quotes_data)
        
        # Note should be unchanged
        current_content = sample_note_path.read_text()
        assert current_content == original_content

    def test_enhance_note_already_processed(self, temp_note_dir):
        """RED: Handle notes with ai_processed=true"""
        processed_note = """---
type: literature
created: 2025-10-03 09:53
ai_processed: true
processed_at: 2025-10-05 10:00
---

# Already Processed

## Extracted Quotes
Already has quotes
"""
        note_path = temp_note_dir / "processed.md"
        note_path.write_text(processed_note)
        
        quotes_data = QuotesData(key_insights=[], actionable=[], notable=[], definitions=[])
        enhancer = YouTubeNoteEnhancer()
        result = enhancer.enhance_note(note_path, quotes_data, force=False)
        
        # Should skip processing
        assert result.success is False
        assert result.skipped is True
        assert "already processed" in result.message.lower()

    def test_enhance_note_file_not_found(self):
        """RED: Error handling for missing file"""
        nonexistent_path = Path("/nonexistent/path/note.md")
        quotes_data = QuotesData(key_insights=[], actionable=[], notable=[], definitions=[])
        
        enhancer = YouTubeNoteEnhancer()
        result = enhancer.enhance_note(nonexistent_path, quotes_data)
        
        assert result.success is False
        assert result.error_type == "FileNotFoundError"
        assert result.error_message is not None


class TestRealTemplaterNoteValidation:
    """Test with actual Templater-created notes from Inbox/"""

    @pytest.fixture
    def temp_note_dir(self):
        """Create temporary directory for test notes"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_enhance_note_real_templater_note(self, temp_note_dir):
        """RED: Process real note structure from user's Inbox"""
        # Use actual structure from lit-20251003-0954 note
        real_note_content = """---
type: literature
created: 2025-10-03 09:53
status: inbox
tags: [youtube, video-content]
visibility: private
source: youtube
author: 
video_id: rYCQZ2osLq4
channel: Majorkill
---

# AI Channels Are Taking Over Warhammer 40k Lore On YouTube

## Video Information
- **Channel**: Majorkill
- **Video URL**: https://www.youtube.com/watch?v=rYCQZ2osLq4
- **Video ID**: `rYCQZ2osLq4`
- **Date Saved**: 2025-10-03
- **Tags**: #youtube #video-content
- **Thumbnail**: ![Video Thumbnail](https://i.ytimg.com/vi/rYCQZ2osLq4/hqdefault.jpg)

## Why I'm Saving This
This is important in the fight against AI slop and finding the line of what is acceptable

## Key Takeaways
<!-- As you watch, capture key points here -->

### Main Insight
> 

**Timestamp**: 

### Supporting Points
<!-- Add more as you watch -->

## My Thoughts & Applications

### How This Connects
<!-- Links to your existing knowledge -->

### Action Items
- [ ] 

## Related Notes
<!-- Add [[wiki-links]] as you make connections -->
"""
        note_path = temp_note_dir / "real-templater-note.md"
        note_path.write_text(real_note_content)
        
        quotes_data = QuotesData(
            key_insights=[
                {"timestamp": "01:23", "quote": "Real quote from video", "context": "Main topic"}
            ],
            actionable=[],
            notable=[],
            definitions=[],
        )
        
        enhancer = YouTubeNoteEnhancer()
        result = enhancer.enhance_note(note_path, quotes_data)
        
        # Verify successful processing
        assert result.success is True
        
        # Verify content preservation
        enhanced = note_path.read_text()
        assert "Majorkill" in enhanced  # Original channel preserved
        assert "Why I'm Saving This" in enhanced  # Original reason preserved
        assert "## Extracted Quotes" in enhanced  # Quotes added
        assert "Real quote from video" in enhanced  # Quote content present
        
        # Verify frontmatter updates
        assert "ai_processed: true" in enhanced
        assert "processed_at:" in enhanced
        assert "quote_count: 1" in enhanced
        
        # Verify all original sections still present
        assert "## Key Takeaways" in enhanced
        assert "## My Thoughts & Applications" in enhanced
        assert "## Related Notes" in enhanced
