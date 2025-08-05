"""
Integration tests for AI connections with real Ollama API.
"""

import pytest
import time
from src.ai.connections import AIConnections
from src.ai.ollama_client import OllamaClient


class TestAIConnectionsIntegration:
    """Integration tests for AIConnections with real API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.connections = AIConnections()
        self.client = OllamaClient()
    
    @pytest.mark.integration
    def test_real_api_health_check(self):
        """Test that Ollama API is available for integration tests."""
        is_healthy = self.client.health_check()
        if not is_healthy:
            pytest.skip("Ollama service is not available")
        assert is_healthy
    
    @pytest.mark.integration
    def test_real_similarity_calculation_performance(self):
        """Test real similarity calculation performance."""
        if not self.client.health_check():
            pytest.skip("Ollama service is not available")
        
        text1 = "Machine learning is a subset of artificial intelligence that focuses on algorithms."
        text2 = "Deep learning uses neural networks to process data and make predictions."
        
        start_time = time.time()
        similarity = self.connections._calculate_semantic_similarity(text1, text2)
        end_time = time.time()
        
        # Performance check
        assert end_time - start_time < 5.0  # Should complete within 5 seconds
        
        # Quality checks
        assert 0 <= similarity <= 1
        assert isinstance(similarity, float)
        # These texts should have some similarity (both about ML/AI)
        assert similarity > 0.3
    
    @pytest.mark.integration
    def test_real_find_similar_notes_quality(self):
        """Test finding similar notes with real semantic analysis."""
        if not self.client.health_check():
            pytest.skip("Ollama service is not available")
        
        target_note = """
        Machine learning algorithms are designed to automatically improve through experience.
        They build mathematical models based on training data to make predictions or decisions
        without being explicitly programmed for the task.
        """
        
        note_corpus = {
            "ai_note.md": """
            Artificial intelligence encompasses machine learning, deep learning, and neural networks.
            These technologies enable computers to perform tasks that typically require human intelligence.
            """,
            "cooking_note.md": """
            Italian pasta recipes require fresh ingredients and proper cooking techniques.
            The key to good pasta is using high-quality flour and timing the cooking perfectly.
            """,
            "ml_algorithms.md": """
            Supervised learning algorithms learn from labeled training data to make predictions.
            Common algorithms include linear regression, decision trees, and support vector machines.
            """,
            "travel_note.md": """
            Traveling to Japan requires careful planning and understanding of local customs.
            The best time to visit is during spring for cherry blossoms or fall for autumn colors.
            """
        }
        
        similar_notes = self.connections.find_similar_notes(target_note, note_corpus)
        
        # Should find AI and ML related notes as similar
        assert len(similar_notes) >= 2
        similar_filenames = [note[0] for note in similar_notes]
        assert "ai_note.md" in similar_filenames
        assert "ml_algorithms.md" in similar_filenames
        
        # Should not find cooking or travel notes as highly similar
        assert "cooking_note.md" not in similar_filenames
        assert "travel_note.md" not in similar_filenames
        
        # Similarity scores should be reasonable
        for filename, score in similar_notes:
            assert 0.5 <= score <= 1.0  # Should be high similarity
    
    @pytest.mark.integration
    def test_real_link_suggestions_quality(self):
        """Test link suggestions with real semantic analysis."""
        if not self.client.health_check():
            pytest.skip("Ollama service is not available")
        
        target_note = """
        Natural language processing (NLP) is a subfield of artificial intelligence
        that focuses on the interaction between computers and human language.
        It involves developing algorithms that can understand, interpret, and generate human language.
        """
        
        note_corpus = {
            "transformers.md": """
            Transformer models have revolutionized natural language processing.
            BERT and GPT are examples of transformer-based models that achieve state-of-the-art results.
            """,
            "computer_vision.md": """
            Computer vision enables machines to interpret and understand visual information.
            Convolutional neural networks are commonly used for image recognition tasks.
            """,
            "nlp_applications.md": """
            NLP applications include machine translation, sentiment analysis, and chatbots.
            These systems process human language to extract meaning and generate responses.
            """,
            "cooking_recipes.md": """
            Traditional Italian cooking emphasizes fresh ingredients and simple preparation methods.
            Pasta, risotto, and pizza are staples of Italian cuisine.
            """
        }
        
        suggestions = self.connections.suggest_links(target_note, note_corpus)
        
        # Should suggest NLP-related notes
        assert len(suggestions) >= 2
        suggested_files = [s["filename"] for s in suggestions]
        assert "transformers.md" in suggested_files
        assert "nlp_applications.md" in suggested_files
        
        # Should not suggest unrelated notes
        assert "cooking_recipes.md" not in suggested_files
        
        # Check suggestion quality
        for suggestion in suggestions:
            assert suggestion["similarity"] >= 0.5
            assert "similarity" in suggestion["reason"]
            assert isinstance(suggestion["similarity"], float)
    
    @pytest.mark.integration
    def test_real_connection_map_building(self):
        """Test building connection map with real semantic analysis."""
        if not self.client.health_check():
            pytest.skip("Ollama service is not available")
        
        note_corpus = {
            "ml_basics.md": """
            Machine learning is a method of data analysis that automates analytical model building.
            It uses algorithms that iteratively learn from data to find hidden insights.
            """,
            "deep_learning.md": """
            Deep learning is a subset of machine learning that uses neural networks with multiple layers.
            It's particularly effective for image recognition and natural language processing.
            """,
            "data_science.md": """
            Data science combines statistics, programming, and domain expertise to extract insights from data.
            It involves data collection, cleaning, analysis, and visualization.
            """,
            "cooking_tips.md": """
            Good cooking requires understanding flavor profiles and proper technique.
            Fresh ingredients and proper seasoning are essential for delicious meals.
            """
        }
        
        start_time = time.time()
        connection_map = self.connections.build_connection_map(note_corpus)
        end_time = time.time()
        
        # Performance check
        assert end_time - start_time < 20.0  # Should complete within 20 seconds
        
        # Quality checks
        assert len(connection_map) == len(note_corpus)
        
        # ML and deep learning should be connected
        ml_connections = connection_map.get("ml_basics.md", [])
        dl_connections = connection_map.get("deep_learning.md", [])
        
        # Should find some connections between related notes
        ml_connected_files = [conn[0] for conn in ml_connections]
        assert "deep_learning.md" in ml_connected_files or "data_science.md" in ml_connected_files
        
        # Cooking should have weaker connections to technical notes (lower similarity scores)
        cooking_connections = connection_map.get("cooking_tips.md", [])
        cooking_connected_files = [conn[0] for conn in cooking_connections]
        technical_files = ["ml_basics.md", "deep_learning.md", "data_science.md"]
        technical_connections = [conn for conn in cooking_connections if conn[0] in technical_files]
        
        # If there are technical connections, they should have lower similarity scores
        if technical_connections:
            max_tech_similarity = max(conn[1] for conn in technical_connections)
            assert max_tech_similarity < 0.8  # Technical connections should be weaker than strong related topics
    
    @pytest.mark.integration
    def test_real_api_with_yaml_frontmatter(self):
        """Test real API integration with YAML frontmatter."""
        if not self.client.health_check():
            pytest.skip("Ollama service is not available")
        
        note_with_yaml = """---
type: permanent
created: 2025-01-01
tags: [ai, machine-learning]
---

Artificial intelligence and machine learning are transforming various industries.
From healthcare to finance, AI applications are becoming increasingly prevalent.
"""
        
        note_corpus = {
            "ai_applications.md": """---
type: literature
tags: [ai, applications]
---

AI applications in healthcare include medical imaging, drug discovery, and patient diagnosis.
These technologies are improving patient outcomes and reducing costs.
"""
        }
        
        similar_notes = self.connections.find_similar_notes(note_with_yaml, note_corpus)
        
        # Should find similarity despite YAML frontmatter
        assert len(similar_notes) > 0
        assert similar_notes[0][0] == "ai_applications.md"
        assert similar_notes[0][1] > 0.5  # Should have good similarity
