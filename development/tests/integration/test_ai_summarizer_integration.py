"""
Integration tests for AI summarizer with real Ollama API.
"""

import sys
import os

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

import pytest
import time
from ai.summarizer import AISummarizer
from ai.ollama_client import OllamaClient


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

Machine learning algorithms have become increasingly sophisticated, with neural 
networks capable of learning complex patterns from vast datasets. Convolutional 
neural networks have proven particularly effective for image recognition tasks, 
while recurrent neural networks excel at sequential data processing.

The emergence of large language models has transformed natural language processing. 
These models, trained on massive text corpora, demonstrate remarkable capabilities 
in text generation, translation, and comprehension. The attention mechanism, 
introduced in transformer architectures, has been instrumental in these advances.

Future research directions include improving model efficiency, developing more 
interpretable AI systems, and addressing bias and fairness concerns. The integration 
of AI with other technologies like quantum computing and edge devices promises 
to unlock new possibilities and applications across various industries.

Ethical considerations around AI development have gained prominence, with researchers 
and policymakers working to establish guidelines for responsible AI deployment. 
The goal is to harness AI's potential while mitigating risks and ensuring 
beneficial outcomes for society.

The application of AI across industries has been transformative. In healthcare, 
AI-powered diagnostic systems can detect diseases with remarkable accuracy, 
often surpassing human specialists. Medical imaging analysis, drug discovery, 
and personalized treatment plans represent just a few areas where AI is making 
significant impacts. Machine learning algorithms can identify patterns in 
complex medical data that would be impossible for humans to detect.

In autonomous vehicles, AI systems must process vast amounts of sensory data 
in real-time to make critical driving decisions. Computer vision algorithms 
analyze camera feeds, while sensor fusion techniques combine data from multiple 
sources including radar, lidar, and GPS. The challenge lies in creating robust 
systems that can handle unexpected scenarios and edge cases safely.

Natural language processing has enabled sophisticated chatbots and virtual 
assistants that can understand context, intent, and nuance in human communication. 
These systems leverage large transformer models trained on diverse text corpora 
to generate human-like responses. The development of few-shot and zero-shot 
learning capabilities has further enhanced their versatility and applicability.

The computational requirements for training large AI models have led to 
innovations in hardware and distributed computing. Graphics processing units 
(GPUs) and specialized AI chips have become essential for handling the massive 
parallel computations required for deep learning. Cloud computing platforms 
now offer specialized AI services that democratize access to powerful AI 
capabilities for researchers and developers worldwide.

Data quality and availability remain crucial factors in AI system performance. 
The concept of 'garbage in, garbage out' is particularly relevant in machine 
learning, where biased or incomplete training data can lead to flawed models. 
Data preprocessing, augmentation, and careful curation are essential steps 
in developing reliable AI systems that generalize well to real-world scenarios."""
        
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
