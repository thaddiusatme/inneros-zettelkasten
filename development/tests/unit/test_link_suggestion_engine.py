#!/usr/bin/env python3
"""
Test suite for LinkSuggestionEngine - TDD Iteration 1
Converts connection discovery results into actionable link suggestions
"""

import pytest
import tempfile
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
import sys
import os

# Add development directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from ai.link_suggestion_engine import LinkSuggestionEngine, LinkSuggestion, QualityScore

@dataclass
class MockConnection:
    """Mock connection for testing"""
    source_file: str
    target_file: str
    similarity_score: float
    content_overlap: str = ""

class TestLinkSuggestionEngine:
    """Test suite for LinkSuggestionEngine core functionality"""
    
    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault structure for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)
            
            # Create note structure
            (vault_path / "Permanent Notes").mkdir()
            (vault_path / "Fleeting Notes").mkdir()
            
            # Create test notes
            ai_note = vault_path / "Permanent Notes" / "ai-concepts.md"
            ai_note.write_text("""---
type: permanent
tags: [ai, machine-learning, concepts]
---
# AI Concepts

This note covers fundamental artificial intelligence concepts including
machine learning algorithms and neural networks.

## Core Concepts
- Deep learning fundamentals
- Neural network architectures
""")
            
            ml_note = vault_path / "Permanent Notes" / "machine-learning-basics.md" 
            ml_note.write_text("""---
type: permanent
tags: [machine-learning, algorithms]
---
# Machine Learning Basics

Introduction to machine learning algorithms and their applications.

## Key Topics
- Supervised learning
- Unsupervised learning
- Deep neural networks
""")
            
            yield vault_path
    
    @pytest.fixture
    def suggestion_engine(self, temp_vault):
        """Create LinkSuggestionEngine instance"""
        return LinkSuggestionEngine(vault_path=str(temp_vault))
    
    def test_engine_initialization(self, temp_vault):
        """Test LinkSuggestionEngine initializes correctly"""
        engine = LinkSuggestionEngine(vault_path=str(temp_vault))
        assert engine.vault_path == str(temp_vault)
        assert hasattr(engine, 'quality_threshold')
        assert hasattr(engine, 'max_suggestions')
    
    def test_generate_link_suggestions_basic(self, suggestion_engine, temp_vault):
        """Test basic link suggestion generation from connections"""
        # Arrange - Mock connections from connection discovery
        connections = [
            MockConnection(
                source_file="Permanent Notes/ai-concepts.md",
                target_file="Permanent Notes/machine-learning-basics.md", 
                similarity_score=0.85,
                content_overlap="machine learning, neural networks"
            )
        ]
        
        # Act - Generate suggestions
        suggestions = suggestion_engine.generate_link_suggestions(
            target_note="Permanent Notes/ai-concepts.md",
            connections=connections
        )
        
        # Assert - Should generate actionable suggestions
        assert len(suggestions) > 0
        suggestion = suggestions[0]
        assert isinstance(suggestion, LinkSuggestion)
        assert suggestion.target_note == "Permanent Notes/machine-learning-basics.md"
        assert suggestion.similarity_score == 0.85
        assert suggestion.suggested_link_text != ""
        assert 0.0 <= suggestion.quality_score <= 1.0
    
    def test_link_text_generation(self, suggestion_engine):
        """Test intelligent link text generation"""
        # Test cases for different note types and contexts
        test_cases = [
            {
                "source": "AI Concepts",
                "target": "Machine Learning Basics", 
                "context": "machine learning, algorithms",
                "expected_pattern": "machine learning"
            },
            {
                "source": "Zettelkasten Method",
                "target": "Note Taking Systems",
                "context": "note taking, knowledge management", 
                "expected_pattern": "note taking"
            }
        ]
        
        for case in test_cases:
            link_text = suggestion_engine.generate_link_text(
                source_content=case["source"],
                target_content=case["target"],
                content_overlap=case["context"]
            )
            
            assert link_text != ""
            assert case["expected_pattern"].lower() in link_text.lower()
            assert link_text.startswith("[[")
            assert link_text.endswith("]]")
    
    def test_quality_scoring_algorithm(self, suggestion_engine):
        """Test link suggestion quality scoring"""
        test_connections = [
            # High quality - strong semantic overlap
            MockConnection(
                source_file="ai-concepts.md",
                target_file="machine-learning.md",
                similarity_score=0.95,
                content_overlap="machine learning algorithms neural networks"
            ),
            # Medium quality - moderate overlap
            MockConnection(
                source_file="note-taking.md", 
                target_file="knowledge-management.md",
                similarity_score=0.70,
                content_overlap="knowledge systems"
            ),
            # Low quality - weak connection
            MockConnection(
                source_file="random-topic.md",
                target_file="unrelated-note.md", 
                similarity_score=0.45,
                content_overlap="common words"
            )
        ]
        
        for connection in test_connections:
            quality = suggestion_engine.score_link_quality(connection)
            
            assert isinstance(quality, QualityScore)
            assert 0.0 <= quality.score <= 1.0
            assert quality.confidence in ["high", "medium", "low"]
            assert quality.explanation != ""
            
            # Quality should correlate with similarity score
            if connection.similarity_score > 0.8:
                assert quality.confidence == "high"
            elif connection.similarity_score > 0.6:
                assert quality.confidence in ["medium", "high"]
            else:
                assert quality.confidence in ["low", "medium"]
    
    def test_suggestion_filtering_by_quality(self, suggestion_engine):
        """Test filtering suggestions by quality threshold"""
        mixed_quality_connections = [
            MockConnection("note1.md", "high-quality.md", 0.95),
            MockConnection("note2.md", "medium-quality.md", 0.70),
            MockConnection("note3.md", "low-quality.md", 0.40),
        ]
        
        # Test with high threshold
        high_threshold_suggestions = suggestion_engine.generate_link_suggestions(
            target_note="test-note.md",
            connections=mixed_quality_connections,
            min_quality=0.8
        )
        
        # Should only return high-quality suggestions
        assert len(high_threshold_suggestions) == 1
        assert high_threshold_suggestions[0].similarity_score >= 0.8
        
        # Test with low threshold
        low_threshold_suggestions = suggestion_engine.generate_link_suggestions(
            target_note="test-note.md", 
            connections=mixed_quality_connections,
            min_quality=0.3
        )
        
        # Should return all suggestions above threshold
        assert len(low_threshold_suggestions) >= 2
    
    def test_suggestion_explanation_generation(self, suggestion_engine):
        """Test generation of human-readable explanations for suggestions"""
        connection = MockConnection(
            source_file="ai-concepts.md",
            target_file="machine-learning.md",
            similarity_score=0.87,
            content_overlap="neural networks, algorithms, deep learning"
        )
        
        suggestions = suggestion_engine.generate_link_suggestions(
            target_note="ai-concepts.md",
            connections=[connection]
        )
        
        suggestion = suggestions[0]
        assert suggestion.explanation != ""
        assert "similar" in suggestion.explanation.lower() or "related" in suggestion.explanation.lower()
        assert any(term in suggestion.explanation.lower() for term in ["concept", "topic", "content"])
    
    def test_suggestion_insertion_context_detection(self, suggestion_engine, temp_vault):
        """Test detection of appropriate insertion points for links"""
        # Create note with specific structure
        structured_note = temp_vault / "structured-note.md"
        structured_note.write_text("""---
type: permanent
---
# Structured Note

## Main Content
This is the main content area.

## Related Concepts
Some existing related concepts.

## See Also
Existing see also references.
""")
        
        connection = MockConnection(
            source_file="structured-note.md",
            target_file="related-note.md",
            similarity_score=0.80
        )
        
        suggestions = suggestion_engine.generate_link_suggestions(
            target_note="structured-note.md",
            connections=[connection]
        )
        
        suggestion = suggestions[0]
        assert hasattr(suggestion, 'suggested_location')
        assert suggestion.suggested_location in ["related_concepts", "see_also", "main_content"]
        assert suggestion.insertion_context != ""
    
    def test_batch_suggestion_generation(self, suggestion_engine):
        """Test efficient batch processing of multiple connections"""
        large_connection_set = [
            MockConnection(f"source-{i}.md", f"target-{i}.md", 0.5 + (i * 0.1) % 0.5)
            for i in range(20)
        ]
        
        suggestions = suggestion_engine.generate_link_suggestions(
            target_note="batch-test.md",
            connections=large_connection_set,
            max_results=10
        )
        
        # Should efficiently process and return top suggestions
        assert len(suggestions) <= 10
        
        # Should be sorted by quality (highest first)
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i].quality_score >= suggestions[i + 1].quality_score
    
    def test_link_suggestion_data_model(self):
        """Test LinkSuggestion dataclass structure"""
        suggestion = LinkSuggestion(
            source_note="source.md",
            target_note="target.md", 
            suggested_link_text="[[example link]]",
            similarity_score=0.85,
            quality_score=0.78,
            confidence="high",
            explanation="Strong semantic relationship",
            insertion_context="## Related Concepts",
            suggested_location="related_concepts"
        )
        
        # Test all required fields are present
        assert suggestion.source_note == "source.md"
        assert suggestion.target_note == "target.md"
        assert suggestion.suggested_link_text == "[[example link]]"
        assert suggestion.similarity_score == 0.85
        assert suggestion.quality_score == 0.78
        assert suggestion.confidence == "high"
        assert suggestion.explanation == "Strong semantic relationship"
        assert suggestion.insertion_context == "## Related Concepts"
        assert suggestion.suggested_location == "related_concepts"
    
    def test_integration_with_existing_connections(self, suggestion_engine, temp_vault):
        """Test integration with connection discovery output format"""
        # Mock the format that comes from existing connection discovery
        connection_discovery_output = {
            "source": "Permanent Notes/ai-concepts.md",
            "target": "Permanent Notes/machine-learning.md",
            "similarity": 0.87,
            "context": "shared semantic concepts"
        }
        
        # Should be able to process connection discovery format
        mock_connection = MockConnection(
            source_file=connection_discovery_output["source"],
            target_file=connection_discovery_output["target"],
            similarity_score=connection_discovery_output["similarity"]
        )
        
        suggestions = suggestion_engine.generate_link_suggestions(
            target_note=connection_discovery_output["source"],
            connections=[mock_connection]
        )
        
        assert len(suggestions) > 0
        assert suggestions[0].similarity_score == 0.87

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
