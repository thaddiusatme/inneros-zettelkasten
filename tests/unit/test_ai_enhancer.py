"""
Unit tests for AI-powered content enhancement and note improvement suggestions.
Tests the enhancer's ability to analyze notes and provide actionable improvement recommendations.
"""

import pytest
from unittest.mock import Mock, patch


class TestAIEnhancer:
    """Test suite for AI content enhancement functionality."""
    
    def test_enhancer_initialization(self):
        """Test that AI enhancer initializes with correct configuration."""
        from src.ai.enhancer import AIEnhancer
        
        enhancer = AIEnhancer()
        assert hasattr(enhancer, 'ollama_client')
        assert hasattr(enhancer, 'min_quality_score')
        assert enhancer.min_quality_score == 0.6
    
    def test_analyze_note_quality_basic(self):
        """Test basic note quality analysis for a well-structured note."""
        from src.ai.enhancer import AIEnhancer
        
        note_content = """
        # Quantum Computing Applications
        
        Quantum computing leverages quantum mechanical phenomena to process information in fundamentally different ways than classical computers.
        
        ## Key Applications
        - Cryptography: Breaking RSA encryption using Shor's algorithm
        - Drug discovery: Simulating molecular interactions for pharmaceutical development
        - Optimization: Solving complex logistics problems exponentially faster
        
        ## Technical Considerations
        Current quantum computers face challenges with quantum decoherence and error rates, limiting practical applications to specialized domains.
        
        ## Related Concepts
        - [[quantum-superposition]]
        - [[quantum-entanglement]]
        - [[quantum-error-correction]]
        """
        
        enhancer = AIEnhancer()
        analysis = enhancer.analyze_note_quality(note_content)
        
        assert isinstance(analysis, dict)
        assert 'quality_score' in analysis
        assert 'suggestions' in analysis
        assert 'missing_elements' in analysis
        assert 0 <= analysis['quality_score'] <= 1
        assert isinstance(analysis['suggestions'], list)
    
    def test_suggest_missing_links(self):
        """Test AI can suggest relevant missing internal links."""
        from src.ai.enhancer import AIEnhancer
        
        note_content = """
        # Machine Learning Workflow
        
        The machine learning workflow involves several critical steps from data collection to model deployment.
        
        ## Process Steps
        1. Data preprocessing and feature engineering
        2. Model selection and training
        3. Model evaluation using cross-validation
        4. Hyperparameter tuning
        5. Deployment and monitoring
        
        This process requires careful attention to data quality and model performance metrics.
        """
        
        enhancer = AIEnhancer()
        suggestions = enhancer.suggest_missing_links(note_content)
        
        assert isinstance(suggestions, list)
        # Should suggest relevant links like [[cross-validation]], [[feature-engineering]], etc.
        assert all(isinstance(link, str) for link in suggestions)
        assert all(link.startswith('[[') and link.endswith(']]') for link in suggestions)
    
    def test_identify_content_gaps(self):
        """Test AI can identify missing content sections or explanations."""
        from src.ai.enhancer import AIEnhancer
        
        # Note missing practical examples and technical details
        note_content = """
        # Neural Networks
        
        Neural networks are computational models inspired by biological neural systems.
        
        ## Basic Structure
        They consist of layers of interconnected nodes (neurons) that process information.
        """
        
        enhancer = AIEnhancer()
        gaps = enhancer.identify_content_gaps(note_content)
        
        assert isinstance(gaps, list)
        assert len(gaps) > 0  # Should identify missing elements
        assert all(isinstance(gap, dict) for gap in gaps)
        assert all('type' in gap and 'description' in gap for gap in gaps)
    
    def test_suggest_improved_structure(self):
        """Test AI can suggest better note structure and organization."""
        from src.ai.enhancer import AIEnhancer
        
        # Poorly structured note
        note_content = """
        Python is a programming language. It has many libraries like numpy and pandas. 
        Machine learning uses python. Data science also uses python. 
        You can do web development with django and flask. Python is easy to learn.
        """
        
        enhancer = AIEnhancer()
        structure_suggestions = enhancer.suggest_improved_structure(note_content)
        
        assert isinstance(structure_suggestions, dict)
        assert 'recommended_structure' in structure_suggestions
        assert 'reasoning' in structure_suggestions
        assert isinstance(structure_suggestions['recommended_structure'], list)
    
    def test_enhance_note_with_ai_suggestions(self):
        """Test end-to-end enhancement with mock AI responses."""
        from src.ai.enhancer import AIEnhancer
        
        note_content = """
        # Docker Containerization
        
        Docker is a platform for developing, shipping, and running applications in containers.
        
        ## Benefits
        - Consistent environments
        - Isolation
        - Scalability
        """
        
        enhancer = AIEnhancer()
        
        # Test with mock to avoid real API calls in unit tests
        with patch.object(enhancer, '_generate_ollama_analysis') as mock_generate:
            mock_generate.return_value = {
                'quality_score': 0.75,
                'suggestions': [
                    'Add practical Docker commands section',
                    'Include docker-compose example',
                    'Link to [[microservices]] and [[kubernetes]] concepts'
                ],
                'missing_elements': [
                    {'type': 'examples', 'description': 'Missing practical docker commands'},
                    {'type': 'links', 'description': 'No links to orchestration concepts'}
                ]
            }
            
            result = enhancer.enhance_note(note_content)
            
            assert isinstance(result, dict)
            assert result['quality_score'] == 0.75
            assert len(result['suggestions']) == 3
            assert len(result['missing_elements']) == 2
    
    def test_handle_empty_content_gracefully(self):
        """Test enhancer handles empty or minimal content gracefully."""
        from src.ai.enhancer import AIEnhancer
        
        enhancer = AIEnhancer()
        
        # Test empty content
        result = enhancer.analyze_note_quality("")
        assert result['quality_score'] == 0.0
        assert len(result['suggestions']) > 0
        assert 'missing_elements' in result
        
        # Test minimal content
        result = enhancer.analyze_note_quality("# Test")
        assert result['quality_score'] < 0.3
        assert any('content' in str(suggestion).lower() for suggestion in result['suggestions'])
    
    def test_yaml_frontmatter_preservation(self):
        """Test that YAML frontmatter is preserved during enhancement."""
        from src.ai.enhancer import AIEnhancer
        
        note_content = """---
type: permanent
created: 2024-01-15 10:30
status: published
tags: [docker, containers]
---

# Docker Containerization
Docker content here...
"""
        
        enhancer = AIEnhancer()
        
        with patch.object(enhancer, '_generate_ollama_analysis') as mock_generate:
            mock_generate.return_value = {
                'quality_score': 0.8,
                'suggestions': ['Add more examples'],
                'missing_elements': []
            }
            
            result = enhancer.enhance_note(note_content)
            
            # Ensure YAML frontmatter is preserved (enhanced_content is None for now)
            # This test is for future when enhanced_content will be populated
            assert result.get('enhanced_content') is None  # Currently not implemented
    
    def test_performance_timing(self):
        """Test that enhancement operations complete within reasonable time."""
        import time
        from src.ai.enhancer import AIEnhancer
        
        note_content = """
        # Test Note
        This is a test note with sufficient content to analyze properly.
        It contains multiple paragraphs and some structure to ensure the AI has enough context to work with when providing enhancement suggestions.
        
        ## Section 1
        Content for section 1 goes here with some technical details.
        
        ## Section 2  
        Content for section 2 continues the theme with additional context.
        """
        
        enhancer = AIEnhancer()
        
        start_time = time.time()
        with patch.object(enhancer, '_generate_ollama_analysis') as mock_generate:
            mock_generate.return_value = {'quality_score': 0.7, 'suggestions': [], 'missing_elements': []}
            result = enhancer.analyze_note_quality(note_content)
        
        elapsed_time = time.time() - start_time
        
        # Should complete quickly even with mocked calls
        assert elapsed_time < 1.0  # Mock should be instant
        assert result is not None
