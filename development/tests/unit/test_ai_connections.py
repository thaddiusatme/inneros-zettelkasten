"""
Unit tests for AI-powered connection discovery and semantic similarity.
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
from ai.connections import AIConnections


class TestAIConnections:
    """Test cases for AIConnections class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.connections = AIConnections()
    
    def test_init_default_config(self):
        """Test connections initialization with default config."""
        connections = AIConnections()
        assert connections.ollama_client is not None
        assert connections.similarity_threshold == 0.7
        assert connections.max_suggestions == 5
    
    def test_init_custom_config(self):
        """Test connections initialization with custom config."""
        config = {"model": "custom-model"}
        connections = AIConnections(
            similarity_threshold=0.8, 
            max_suggestions=10, 
            config=config
        )
        assert connections.similarity_threshold == 0.8
        assert connections.max_suggestions == 10
    
    def test_extract_content_with_yaml(self):
        """Test content extraction with YAML frontmatter."""
        note_content = """---
type: permanent
tags: [ai, research]
---

This is the main content of the note.
It discusses artificial intelligence research.
"""
        result = self.connections._extract_content(note_content)
        expected = "This is the main content of the note.\nIt discusses artificial intelligence research."
        assert result.strip() == expected
    
    def test_extract_content_without_yaml(self):
        """Test content extraction without YAML frontmatter."""
        note_content = "This is content without YAML frontmatter."
        result = self.connections._extract_content(note_content)
        assert result == note_content
    
    def test_normalize_text(self):
        """Test text normalization for similarity comparison."""
        text = "This is a TEST with UPPERCASE and punctuation!!!"
        result = self.connections._normalize_text(text)
        assert result == "this is a test with uppercase and punctuation"
    
    def test_normalize_text_empty(self):
        """Test text normalization with empty input."""
        assert self.connections._normalize_text("") == ""
        assert self.connections._normalize_text("   ") == ""
    
    @patch('ai.connections.AIConnections._calculate_semantic_similarity')
    def test_find_similar_notes_success(self, mock_similarity):
        """Test finding similar notes successfully."""
        target_note = "This note is about machine learning and AI."
        note_corpus = {
            "note1.md": "Deep learning is a subset of machine learning.",
            "note2.md": "Cooking recipes for Italian pasta dishes.",
            "note3.md": "Artificial intelligence applications in healthcare."
        }
        
        # Mock similarity scores
        mock_similarity.side_effect = [0.85, 0.2, 0.75]
        
        result = self.connections.find_similar_notes(target_note, note_corpus)
        
        assert len(result) == 2  # Only notes above threshold (0.7)
        assert result[0] == ("note1.md", 0.85)
        assert result[1] == ("note3.md", 0.75)
    
    @patch('ai.connections.AIConnections._calculate_semantic_similarity')
    def test_find_similar_notes_no_matches(self, mock_similarity):
        """Test finding similar notes with no matches above threshold."""
        target_note = "This note is about quantum physics."
        note_corpus = {
            "note1.md": "Cooking recipes for pasta.",
            "note2.md": "Travel guide to Japan."
        }
        
        mock_similarity.side_effect = [0.1, 0.15]
        
        result = self.connections.find_similar_notes(target_note, note_corpus)
        
        assert len(result) == 0
    
    @patch('ai.connections.AIConnections._calculate_semantic_similarity')
    def test_find_similar_notes_max_suggestions(self, mock_similarity):
        """Test that max_suggestions limit is respected."""
        target_note = "AI research note."
        note_corpus = {f"note{i}.md": f"AI content {i}" for i in range(10)}
        
        # All notes have high similarity
        mock_similarity.return_value = 0.9
        
        result = self.connections.find_similar_notes(target_note, note_corpus)
        
        assert len(result) <= self.connections.max_suggestions
    
    def test_suggest_links_empty_corpus(self):
        """Test link suggestions with empty note corpus."""
        target_note = "This is a test note."
        result = self.connections.suggest_links(target_note, {})
        assert result == []
    
    @patch('ai.connections.AIConnections.find_similar_notes')
    def test_suggest_links_success(self, mock_find_similar):
        """Test successful link suggestions."""
        target_note = "Machine learning research."
        note_corpus = {"note1.md": "AI content", "note2.md": "ML algorithms"}
        
        mock_find_similar.return_value = [
            ("note1.md", 0.85),
            ("note2.md", 0.78)
        ]
        
        result = self.connections.suggest_links(target_note, note_corpus)
        
        expected = [
            {"filename": "note1.md", "similarity": 0.85, "reason": "High semantic similarity (85%)"},
            {"filename": "note2.md", "similarity": 0.78, "reason": "High semantic similarity (78%)"}
        ]
        assert result == expected
    
    @patch('ai.connections.AIConnections._generate_ollama_embedding')
    def test_calculate_semantic_similarity_success(self, mock_embedding):
        """Test semantic similarity calculation."""
        text1 = "Machine learning algorithms"
        text2 = "Deep learning neural networks"
        
        # Mock embeddings (simplified vectors)
        mock_embedding.side_effect = [
            [0.1, 0.2, 0.3, 0.4],
            [0.15, 0.25, 0.35, 0.45]
        ]
        
        result = self.connections._calculate_semantic_similarity(text1, text2)
        
        # Should return a similarity score between 0 and 1
        assert 0 <= result <= 1
        assert isinstance(result, float)
    
    @patch('ai.connections.AIConnections._generate_ollama_embedding')
    def test_calculate_semantic_similarity_api_error(self, mock_embedding):
        """Test semantic similarity with API error."""
        text1 = "Test text 1"
        text2 = "Test text 2"
        
        mock_embedding.side_effect = Exception("API Error")
        
        result = self.connections._calculate_semantic_similarity(text1, text2)
        
        # Should fall back to simple text similarity
        assert 0 <= result <= 1
    
    def test_simple_text_similarity_identical(self):
        """Test simple text similarity with identical texts."""
        text = "This is a test sentence."
        result = self.connections._simple_text_similarity(text, text)
        assert result == 1.0
    
    def test_simple_text_similarity_different(self):
        """Test simple text similarity with different texts."""
        text1 = "machine learning artificial intelligence"
        text2 = "cooking recipes italian food"
        result = self.connections._simple_text_similarity(text1, text2)
        assert 0 <= result < 0.5  # Should be low similarity
    
    def test_simple_text_similarity_partial_overlap(self):
        """Test simple text similarity with partial overlap."""
        text1 = "machine learning algorithms"
        text2 = "machine learning applications"
        result = self.connections._simple_text_similarity(text1, text2)
        assert 0.5 <= result < 1.0  # Should have moderate similarity
    
    def test_generate_ollama_embedding_success(self):
        """Test Ollama embedding generation."""
        # Mock the embedding cache to return our test embedding
        with patch.object(self.connections, 'embedding_cache') as mock_cache:
            mock_cache.get_or_generate_embedding.return_value = [0.1, 0.2, 0.3, 0.4]
            
            text = "Test text for embedding"
            result = self.connections._generate_ollama_embedding(text)
            
            assert result == [0.1, 0.2, 0.3, 0.4]
            mock_cache.get_or_generate_embedding.assert_called_once_with(text)
    
    def test_generate_ollama_embedding_api_down(self):
        """Test Ollama embedding when API is down."""
        # Mock the embedding cache to raise an exception (simulating API failure)
        with patch.object(self.connections, 'embedding_cache') as mock_cache:
            mock_cache.get_or_generate_embedding.side_effect = Exception("Failed to generate embedding: Ollama service is not available")
            
            text = "Test text"
            
            with pytest.raises(Exception, match="Failed to generate embedding"):
                self.connections._generate_ollama_embedding(text)
    
    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity with identical vectors."""
        vector = [1, 2, 3, 4]
        result = self.connections._cosine_similarity(vector, vector)
        assert abs(result - 1.0) < 1e-10  # Should be 1.0
    
    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity with orthogonal vectors."""
        vector1 = [1, 0, 0, 0]
        vector2 = [0, 1, 0, 0]
        result = self.connections._cosine_similarity(vector1, vector2)
        assert abs(result - 0.0) < 1e-10  # Should be 0.0
    
    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector."""
        vector1 = [1, 2, 3]
        vector2 = [0, 0, 0]
        result = self.connections._cosine_similarity(vector1, vector2)
        assert result == 0.0
    
    def test_build_connection_map_empty_corpus(self):
        """Test connection map building with empty corpus."""
        result = self.connections.build_connection_map({})
        assert result == {}
    
    @patch('ai.connections.AIConnections.find_similar_notes')
    def test_build_connection_map_success(self, mock_find_similar):
        """Test successful connection map building."""
        note_corpus = {
            "note1.md": "AI content",
            "note2.md": "ML content", 
            "note3.md": "Cooking content"
        }
        
        # Mock different similarity results for each note
        mock_find_similar.side_effect = [
            [("note2.md", 0.8)],  # note1 similar to note2
            [("note1.md", 0.8)],  # note2 similar to note1
            []  # note3 has no similar notes
        ]
        
        result = self.connections.build_connection_map(note_corpus)
        
        expected = {
            "note1.md": [("note2.md", 0.8)],
            "note2.md": [("note1.md", 0.8)],
            "note3.md": []
        }
        assert result == expected
