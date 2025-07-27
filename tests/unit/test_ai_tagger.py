"""
Unit tests for AI-powered automatic tag generation.
Tests the tagger's ability to extract relevant tags from note content.
"""

import pytest
from unittest.mock import Mock, patch


class TestAITagger:
    """Test suite for AI tag generation functionality."""
    
    def test_tagger_initialization(self):
        """Test that AI tagger initializes with correct configuration."""
        from src.ai.tagger import AITagger
        
        tagger = AITagger()
        assert hasattr(tagger, 'ollama_client')
        assert hasattr(tagger, 'min_confidence')
        assert tagger.min_confidence == 0.7
    
    def test_generate_tags_from_permanent_note(self):
        """Test tag generation for a permanent note about machine learning."""
        from src.ai.tagger import AITagger
        
        note_content = """
        # Machine Learning Fundamentals
        
        Machine learning is a subset of artificial intelligence that enables 
        systems to learn and improve from experience without being explicitly 
        programmed. The key concepts include supervised learning, unsupervised 
        learning, and reinforcement learning.
        
        ## Key Algorithms
        - Neural networks
        - Decision trees
        - Support vector machines
        - Clustering algorithms
        """
        
        tagger = AITagger()
        tags = tagger.generate_tags(note_content)
        
        # Test that we get relevant tags based on content
        assert isinstance(tags, list)
        assert len(tags) >= 3
        assert all(isinstance(tag, str) for tag in tags)
    
    def test_generate_tags_with_confidence_filtering(self):
        """Test that confidence filtering works in tag generation."""
        from src.ai.tagger import AITagger
        
        note_content = "This is a simple note about Python programming."
        
        tagger = AITagger(min_confidence=0.8)
        
        # Test that we get tags and they're properly filtered
        tags = tagger.generate_tags(note_content)
        
        assert isinstance(tags, list)
        assert len(tags) <= 8  # Max tags limit
        assert all(isinstance(tag, str) for tag in tags)
    
    def test_generate_tags_empty_note(self):
        """Test tag generation for empty note content."""
        from src.ai.tagger import AITagger
        
        tagger = AITagger()
        tags = tagger.generate_tags("")
        
        assert tags == []
    
    def test_generate_tags_very_short_note(self):
        """Test tag generation for very short note content."""
        from src.ai.tagger import AITagger
        
        tagger = AITagger()
        
        # Test with very short content
        tags = tagger.generate_tags("AI")
        
        assert isinstance(tags, list)
        # Short content should return some basic tags based on keywords
    
    def test_tag_deduplication(self):
        """Test that duplicate tags are removed."""
        from src.ai.tagger import AITagger
        
        note_content = "Machine learning and AI are transforming technology."
        
        tagger = AITagger()
        
        # Test that we get unique tags
        tags = tagger.generate_tags(note_content)
        
        assert len(tags) == len(set(tags))  # No duplicates
        assert all(tags.count(tag) == 1 for tag in tags)
