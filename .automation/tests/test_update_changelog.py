import os
import sys
import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from update_changelog import (
    filter_paths, format_entry, update_changelog, call_local_llm, 
    SYMBOLS, IGNORED_PREFIXES, IGNORED_FILES
)


class TestFilterPaths:
    def test_filter_markdown_files(self):
        """Test that only markdown files are included."""
        diff_lines = [
            "A\tInbox/note.md",
            "M\tPermanent Notes/idea.md", 
            "D\tsome-file.txt",
            "A\tREADME.md"
        ]
        results = list(filter_paths(diff_lines))
        assert len(results) == 3
        assert ("A", "Inbox/note.md") in results
        assert ("M", "Permanent Notes/idea.md") in results
        assert ("A", "README.md") in results

    def test_filter_ignores_templates(self):
        """Test that Templates/ files are ignored."""
        diff_lines = [
            "A\tTemplates/fleeting.md",
            "M\tTemplates/permanent.md",
            "A\tInbox/note.md"
        ]
        results = list(filter_paths(diff_lines))
        assert len(results) == 1
        assert ("A", "Inbox/note.md") in results

    def test_filter_ignores_automation(self):
        """Test that .automation/ files are ignored."""
        diff_lines = [
            "A\t.automation/scripts/test.md",
            "M\t.automation/README.md",
            "A\tInbox/note.md"
        ]
        results = list(filter_paths(diff_lines))
        assert len(results) == 1
        assert ("A", "Inbox/note.md") in results

    def test_filter_ignores_changelog(self):
        """Test that the changelog file itself is ignored."""
        diff_lines = [
            "M\tWindsurf Project Changelog.md",
            "A\tInbox/note.md"
        ]
        results = list(filter_paths(diff_lines))
        assert len(results) == 1
        assert ("A", "Inbox/note.md") in results


class TestFormatEntry:
    def test_format_added_file(self):
        """Test formatting of added files."""
        result = format_entry("A", "Inbox/new-idea.md")
        assert result == "- ✚ Added  Inbox/new-idea.md"

    def test_format_modified_file(self):
        """Test formatting of modified files."""
        result = format_entry("M", "Permanent Notes/note.md")
        assert result == "- ✹ Edited Permanent Notes/note.md"

    def test_format_deleted_file(self):
        """Test formatting of deleted files."""
        result = format_entry("D", "Archive/old.md")
        assert result == "- ✖ Deleted Archive/old.md"

    def test_format_unknown_status(self):
        """Test formatting of unknown status codes."""
        result = format_entry("X", "some-file.md")
        assert result == "- X      some-file.md"


class TestUpdateChangelog:
    def test_create_new_changelog(self):
        """Test creating a new changelog file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            changelog_path = Path(tmpdir) / "test_changelog.md"
            
            # Patch the CHANGELOG constant
            with patch('update_changelog.CHANGELOG', changelog_path):
                entries = ["- ✚ Added  test.md"]
                update_changelog(entries)
                
                content = changelog_path.read_text()
                assert "# Windsurf Project Changelog" in content
                assert "- ✚ Added  test.md" in content

    def test_append_to_existing_date(self):
        """Test appending entries to existing date section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            changelog_path = Path(tmpdir) / "test_changelog.md"
            
            # Create existing changelog with today's date
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            existing_content = f"""# Windsurf Project Changelog

### {today}
- ✚ Added  existing.md

### 2025-01-01
- ✹ Edited old.md
"""
            changelog_path.write_text(existing_content)
            
            with patch('update_changelog.CHANGELOG', changelog_path):
                entries = ["- ✹ Edited new.md"]
                update_changelog(entries)
                
                content = changelog_path.read_text()
                lines = content.splitlines()
                
                # Find today's section and verify both entries are present
                today_index = next(i for i, line in enumerate(lines) if line == f"### {today}")
                section_lines = lines[today_index + 1:today_index + 3]
                assert "- ✚ Added  existing.md" in section_lines
                assert "- ✹ Edited new.md" in section_lines

    def test_no_duplicate_entries(self):
        """Test that duplicate entries are not added."""
        with tempfile.TemporaryDirectory() as tmpdir:
            changelog_path = Path(tmpdir) / "test_changelog.md"
            
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            existing_content = f"""# Windsurf Project Changelog

### {today}
- ✚ Added  test.md
"""
            changelog_path.write_text(existing_content)
            
            with patch('update_changelog.CHANGELOG', changelog_path):
                entries = ["- ✚ Added  test.md"]  # Same entry
                update_changelog(entries)
                
                content = changelog_path.read_text()
                # Should only appear once
                assert content.count("- ✚ Added  test.md") == 1


class TestCallLocalLLM:
    def test_llm_disabled_by_default(self):
        """Test that LLM is disabled when env var not set."""
        entries = ["- ✚ Added  test.md"]
        result = call_local_llm(entries)
        assert result is None

    @patch.dict(os.environ, {'INNEROS_USE_LLM': '1'})
    @patch('requests.post')
    def test_llm_success_ollama_format(self, mock_post):
        """Test successful LLM call with Ollama response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "- ✚ Added  enhanced-note.md\n- ✹ Edited improved-idea.md"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        entries = ["- ✚ Added  test.md", "- ✹ Edited idea.md"]
        result = call_local_llm(entries)
        
        assert result == ["- ✚ Added  enhanced-note.md", "- ✹ Edited improved-idea.md"]

    @patch.dict(os.environ, {'INNEROS_USE_LLM': '1'})
    @patch('requests.post')
    def test_llm_failure_fallback(self, mock_post):
        """Test that LLM failures return None for fallback."""
        mock_post.side_effect = Exception("Connection failed")
        
        entries = ["- ✚ Added  test.md"]
        result = call_local_llm(entries)
        
        assert result is None

    @patch.dict(os.environ, {'INNEROS_USE_LLM': '1'})
    @patch('requests.post')
    def test_llm_invalid_response_format(self, mock_post):
        """Test handling of invalid LLM response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "This is not a valid changelog format"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        entries = ["- ✚ Added  test.md"]
        result = call_local_llm(entries)
        
        assert result is None  # No valid changelog lines found


if __name__ == "__main__":
    pytest.main([__file__])
