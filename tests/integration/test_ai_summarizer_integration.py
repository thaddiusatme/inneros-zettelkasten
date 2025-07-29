"""
Integration tests for AI summarizer with real Ollama API.
"""

import pytest
import time
from src.ai.summarizer import AISummarizer
from src.ai.ollama_client import OllamaClient


class TestAISummarizerIntegration:
    """Integration tests for AISummarizer with real API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.summarizer = AISummarizer()
        self.client = OllamaClient()
    
    @pytest.mark.integration
    def test_real_api_health_check(self):
        """Test that Ollama API is available for integration tests."""
        is_healthy = self.client.health_check()
        if not is_healthy:
            pytest.skip("Ollama service is not available")
        assert is_healthy
    
    @pytest.mark.integration
    def test_real_summary_generation_performance(self):
        """Test real summary generation performance."""
        if not self.client.health_check():
            pytest.skip("Ollama service is not available")
        
        # Create a substantial piece of content
        long_content = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, 
        in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of "intelligent agents": 
        any device that perceives its environment and takes actions that maximize 
        its chance of successfully achieving its goals. Colloquially, the term 
        "artificial intelligence" is often used to describe machines that mimic 
        "cognitive" functions that humans associate with the human mind, such as 
        "learning" and "problem solving". As machines become increasingly capable, 
        tasks considered to require "intelligence" are often removed from the 
        definition of AI, a phenomenon known as the AI effect. A quip in Tesler's 
        Theorem says "AI is whatever hasn't been done yet." For instance, optical 
        character recognition is frequently excluded from things considered to be 
        AI, having become a routine technology. Modern machine learning techniques 
        are at the heart of AI. Problems for AI applications include reasoning, 
        knowledge representation, planning, learning, natural language processing, 
        perception, and the ability to move and manipulate objects. General 
        intelligence is among the field's long-term goals. Approaches include 
        statistical methods, computational intelligence, and traditional symbolic AI.
        """ * 3  # Make it longer to ensure it meets the threshold
        
        start_time = time.time()
        summary = self.summarizer.generate_summary(long_content)
        end_time = time.time()
        
        # Performance check
        assert end_time - start_time < 10.0  # Should complete within 10 seconds
        
        # Quality checks
        assert summary is not None
        assert len(summary) > 0
        assert len(summary) < len(long_content)
        assert "artificial intelligence" in summary.lower() or "ai" in summary.lower()
    
    @pytest.mark.integration
    def test_real_extractive_summary_quality(self):
        """Test extractive summary quality with real content."""
        # Use a structured piece of content with clear key points
        content = """
        Machine learning is a method of data analysis that automates analytical model building. 
        It is a branch of artificial intelligence based on the idea that systems can learn from data, 
        identify patterns and make decisions with minimal human intervention.
        
        The process of machine learning is similar to that of data mining. Both systems search 
        through data to look for patterns. However, instead of extracting data for human comprehension 
        – as is the case in data mining applications – machine learning uses that data to detect 
        patterns in data and adjust program actions accordingly.
        
        Machine learning algorithms build a mathematical model based on training data, in order to 
        make predictions or decisions without being explicitly programmed to do so. Machine learning 
        algorithms are used in a wide variety of applications, such as email filtering and computer vision, 
        where it is difficult or infeasible to develop conventional algorithms to perform the needed tasks.
        
        A subset of machine learning is closely related to computational statistics, which focuses on 
        making predictions using computers; but not all machine learning is statistical learning. 
        The study of mathematical optimization delivers methods, theory and application domains to 
        the field of machine learning. Data mining is a related field of study, focusing on 
        exploratory data analysis through unsupervised learning.
        """ * 2  # Make it long enough
        
        summary = self.summarizer.generate_extractive_summary(content)
        
        assert summary is not None
        assert len(summary) > 0
        assert len(summary) < len(content)
        # Should contain key concepts
        key_terms = ["machine learning", "data", "algorithms", "patterns"]
        assert any(term in summary.lower() for term in key_terms)
    
    @pytest.mark.integration
    def test_real_api_with_yaml_frontmatter(self):
        """Test real API integration with YAML frontmatter."""
        if not self.client.health_check():
            pytest.skip("Ollama service is not available")
        
        content_with_yaml = """---
type: literature
created: 2025-01-01
tags: [ai, research, summary]
title: "AI Research Summary"
---

Artificial intelligence research has made significant progress in recent years. 
Deep learning models have achieved remarkable performance in various domains including 
computer vision, natural language processing, and speech recognition. The development 
of transformer architectures has particularly revolutionized the field of NLP, 
enabling models like GPT and BERT to achieve human-level performance on many tasks.

Recent advances in reinforcement learning have also shown promise in complex 
decision-making scenarios. AlphaGo's victory over human champions demonstrated 
the potential of AI in strategic games. Subsequently, AlphaZero generalized 
this approach to multiple games without human knowledge.

The field continues to evolve with new architectures, training techniques, and 
applications emerging regularly. However, challenges remain in areas such as 
explainability, robustness, and ethical AI development.
""" * 2
        
        summary = self.summarizer.generate_summary(content_with_yaml)
        
        assert summary is not None
        assert "---" not in summary  # YAML should be stripped
        assert "type: literature" not in summary
        assert len(summary) > 0
        assert "artificial intelligence" in summary.lower() or "ai" in summary.lower()
    
    @pytest.mark.integration
    def test_real_api_error_handling(self):
        """Test error handling with real API."""
        if not self.client.health_check():
            pytest.skip("Ollama service is not available")
        
        # Test with empty content
        result = self.summarizer.generate_summary("")
        assert result is None
        
        # Test with short content
        short_content = "This is too short."
        result = self.summarizer.generate_summary(short_content)
        assert result is None
