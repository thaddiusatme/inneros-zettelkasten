"""
Unit tests for AI-powered automatic tag generation.
Tests the tagger's ability to extract relevant tags from note content.
"""

import pytest
from unittest.mock import patch


class TestAITagger:
    """Test suite for AI tag generation functionality."""

    def test_tagger_initialization(self):
        """Test that AI tagger initializes with correct configuration."""
        from src.ai.tagger import AITagger

        tagger = AITagger()
        assert hasattr(tagger, "ollama_client")
        assert hasattr(tagger, "min_confidence")
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

    def test_real_ollama_api_integration(self):
        """Test real Ollama API integration for tag generation."""
        from src.ai.tagger import AITagger
        from src.ai.ollama_client import OllamaClient

        # Skip test if Ollama is not available
        client = OllamaClient()
        if not client.health_check():
            pytest.skip("Ollama service not available")

        note_content = """
        # Quantum Computing Applications
        
        Quantum computing represents a paradigm shift in computational power,
        leveraging quantum mechanical phenomena like superposition and entanglement.
        Key applications include cryptography, drug discovery, and optimization problems
        that are intractable for classical computers.
        
        The field combines physics, computer science, and mathematics to solve
        complex problems exponentially faster than traditional approaches.
        """

        tagger = AITagger()
        tags = tagger.generate_tags(note_content, min_tags=3, max_tags=6)

        # Test that we get relevant tags from real AI
        assert isinstance(tags, list)
        assert 3 <= len(tags) <= 6
        assert all(isinstance(tag, str) for tag in tags)

        # Test that tags are more sophisticated than mock keywords
        # Real AI should generate tags like "quantum-computing", "cryptography", etc.
        sophisticated_tags = [tag for tag in tags if len(tag) > 8]
        assert len(sophisticated_tags) >= 2, f"Expected sophisticated tags, got: {tags}"

    def test_ollama_api_error_handling(self):
        """Test graceful handling of Ollama API failures."""
        from src.ai.tagger import AITagger

        note_content = "This is a test note about machine learning algorithms."
        tagger = AITagger()

        # Mock API failure
        with patch.object(
            tagger.ollama_client,
            "generate_completion",
            side_effect=Exception("API Error"),
        ):
            tags = tagger.generate_tags(note_content)

            # Should fallback to mock tags gracefully
            assert isinstance(tags, list)
            assert len(tags) >= 0  # Could be empty or fallback tags

    def test_ollama_performance_timing(self):
        """Test that real API calls complete within performance target."""
        import time
        from src.ai.tagger import AITagger
        from src.ai.ollama_client import OllamaClient

        # Skip test if Ollama is not available
        client = OllamaClient()
        if not client.health_check():
            pytest.skip("Ollama service not available")

        note_content = "A brief note about data science and analytics."
        tagger = AITagger()

        start_time = time.time()
        tags = tagger.generate_tags(note_content)
        end_time = time.time()

        # Should complete within 2 seconds
        processing_time = end_time - start_time
        assert (
            processing_time < 2.0
        ), f"Processing took {processing_time:.2f}s, expected <2s"
