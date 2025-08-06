"""
Unit tests for AI-powered note summarization.
"""

import sys
import os

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

import pytest
from unittest.mock import Mock, patch, MagicMock
from ai.summarizer import AISummarizer


class TestAISummarizer:
    """Test cases for AISummarizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.summarizer = AISummarizer()
    
    def test_init_default_config(self):
        """Test summarizer initialization with default config."""
        summarizer = AISummarizer()
        assert summarizer.ollama_client is not None
        assert summarizer.min_length == 500
        assert summarizer.max_summary_ratio == 0.3
    
    def test_init_custom_config(self):
        """Test summarizer initialization with custom config."""
        config = {"model": "custom-model", "timeout": 60}
        summarizer = AISummarizer(min_length=300, max_summary_ratio=0.5, config=config)
        assert summarizer.min_length == 300
        assert summarizer.max_summary_ratio == 0.5
    
    def test_should_summarize_short_content(self):
        """Test that short content is not summarized."""
        short_content = "This is a short note with less than 500 words."
        assert not self.summarizer.should_summarize(short_content)
    
    def test_should_summarize_long_content(self):
        """Test that long content should be summarized."""
        long_content = " ".join(["word"] * 600)  # 600 words
        assert self.summarizer.should_summarize(long_content)
    
    def test_should_summarize_empty_content(self):
        """Test that empty content is not summarized."""
        assert not self.summarizer.should_summarize("")
        assert not self.summarizer.should_summarize("   ")
    
    def test_strip_yaml_frontmatter(self):
        """Test YAML frontmatter removal."""
        content_with_yaml = """---
type: permanent
created: 2025-01-01
tags: [test]
---

This is the actual content of the note.
It should be preserved after stripping YAML.
"""
        expected = "This is the actual content of the note.\nIt should be preserved after stripping YAML."
        result = self.summarizer._strip_yaml_frontmatter(content_with_yaml)
        assert result.strip() == expected
    
    def test_strip_yaml_frontmatter_no_yaml(self):
        """Test content without YAML frontmatter."""
        content = "This is content without YAML frontmatter."
        result = self.summarizer._strip_yaml_frontmatter(content)
        assert result == content
    
    def test_count_words(self):
        """Test word counting functionality."""
        text = "This is a test with exactly seven words."
        assert self.summarizer._count_words(text) == 8
    
    def test_count_words_empty(self):
        """Test word counting with empty text."""
        assert self.summarizer._count_words("") == 0
        assert self.summarizer._count_words("   ") == 0
    
    @patch('ai.summarizer.AISummarizer._generate_ollama_summary')
    def test_generate_summary_success(self, mock_ollama):
        """Test successful summary generation."""
        long_content = " ".join(["word"] * 600)
        mock_ollama.return_value = "This is a concise summary of the content."
        
        result = self.summarizer.generate_summary(long_content)
        
        assert result == "This is a concise summary of the content."
        mock_ollama.assert_called_once()
    
    @patch('ai.summarizer.AISummarizer._generate_ollama_summary')
    def test_generate_summary_short_content(self, mock_ollama):
        """Test summary generation with short content."""
        short_content = "This is too short to summarize."
        
        result = self.summarizer.generate_summary(short_content)
        
        assert result is None
        mock_ollama.assert_not_called()
    
    @patch('ai.summarizer.AISummarizer._generate_ollama_summary')
    def test_generate_summary_api_failure(self, mock_ollama):
        """Test summary generation when API fails."""
        long_content = " ".join(["word"] * 600)
        mock_ollama.side_effect = Exception("API Error")
        
        result = self.summarizer.generate_summary(long_content)
        
        assert result is None
    
    @patch('ai.summarizer.AISummarizer._generate_ollama_summary')
    def test_generate_summary_with_metadata(self, mock_ollama):
        """Test summary generation with metadata context."""
        content_with_yaml = """---
type: literature
created: 2025-01-01
tags: [research, ai]
---

""" + " ".join(["content"] * 600)
        
        mock_ollama.return_value = "Research summary about AI."
        
        result = self.summarizer.generate_summary(content_with_yaml)
        
        assert result == "Research summary about AI."
        # Verify YAML was stripped before processing
        mock_ollama.assert_called_once()
        call_args = mock_ollama.call_args[0][0]
        assert "---" not in call_args
        assert "type: literature" not in call_args
    
    def test_generate_extractive_summary_short_content(self):
        """Test extractive summarization with short content."""
        short_content = "This is a short note."
        result = self.summarizer.generate_extractive_summary(short_content)
        assert result is None
    
    def test_generate_extractive_summary_long_content(self):
        """Test extractive summarization with long content."""
        # Create content with clear sentences
        sentences = [
            "This is the first important sentence.",
            "This is a less important filler sentence.",
            "This is another crucial point about the topic.",
            "More filler content that is not as relevant.",
            "This concludes the main argument effectively."
        ]
        long_content = " ".join(sentences * 20)  # Make it long enough
        
        result = self.summarizer.generate_extractive_summary(long_content)
        
        assert result is not None
        assert len(result) < len(long_content)
        # Should contain some of the original content
        assert any(word in result.lower() for word in ["important", "crucial", "concludes"])
    
    def test_generate_ollama_summary_success(self):
        """Test Ollama API summary generation."""
        with patch.object(self.summarizer.ollama_client, 'health_check', return_value=True), \
             patch.object(self.summarizer.ollama_client, 'generate', return_value="Generated summary from Ollama.") as mock_generate:
            
            content = " ".join(["word"] * 600)
            result = self.summarizer._generate_ollama_summary(content)
            
            assert result == "Generated summary from Ollama."
            mock_generate.assert_called_once()
    
    def test_generate_ollama_summary_api_down(self):
        """Test Ollama summary when API is down."""
        with patch.object(self.summarizer.ollama_client, 'health_check', return_value=False):
            content = " ".join(["word"] * 600)
            
            with pytest.raises(Exception, match="Ollama service is not available"):
                self.summarizer._generate_ollama_summary(content)
    
    def test_generate_ollama_summary_api_error(self):
        """Test Ollama summary with API error."""
        with patch.object(self.summarizer.ollama_client, 'health_check', return_value=True), \
             patch.object(self.summarizer.ollama_client, 'generate', side_effect=Exception("API Error")):
            
            content = " ".join(["word"] * 600)
            
            with pytest.raises(Exception, match="Failed to generate summary"):
                self.summarizer._generate_ollama_summary(content)
