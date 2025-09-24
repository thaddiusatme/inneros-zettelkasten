#!/usr/bin/env python3
"""
Link Suggestion Engine - TDD Iteration 1 (Refactored)
Converts connection discovery results into actionable link suggestions with quality scoring
"""

from dataclasses import dataclass
from typing import List, Any
from pathlib import Path

from .link_suggestion_utils import (
    QualityScore, 
    LinkTextGenerator, 
    LinkQualityAssessor, 
    InsertionContextDetector,
    SuggestionBatchProcessor
)

@dataclass
class LinkSuggestion:
    """Data model for a suggested link between notes"""
    source_note: str
    target_note: str
    suggested_link_text: str
    similarity_score: float
    quality_score: float
    confidence: str  # "high", "medium", "low"
    explanation: str
    insertion_context: str
    suggested_location: str  # "related_concepts", "see_also", "main_content"

class LinkSuggestionEngine:
    """
    Converts connection discovery results into actionable link suggestions
    with intelligent quality scoring and link text generation
    """
    
    def __init__(self, vault_path: str, quality_threshold: float = 0.5, max_suggestions: int = 10):
        """
        Initialize LinkSuggestionEngine
        
        Args:
            vault_path: Path to the vault/knowledge directory
            quality_threshold: Minimum quality score for suggestions  
            max_suggestions: Maximum number of suggestions to return
        """
        self.vault_path = vault_path
        self.quality_threshold = quality_threshold
        self.max_suggestions = max_suggestions
    
    def generate_link_suggestions(self, target_note: str, connections: List[Any], 
                                min_quality: float = None, max_results: int = None) -> List[LinkSuggestion]:
        """
        Generate link suggestions from connection discovery results
        
        Args:
            target_note: The note to generate suggestions for
            connections: List of connection objects from discovery system
            min_quality: Optional minimum quality threshold
            max_results: Optional maximum results to return
            
        Returns:
            List of LinkSuggestion objects sorted by quality score
        """
        suggestions = []
        min_qual = min_quality or self.quality_threshold
        max_res = max_results or self.max_suggestions
        
        for conn in connections:
            # Generate suggestion using extracted utilities
            quality = self.score_link_quality(conn)
            
            # Skip if below quality threshold
            if quality.score < min_qual:
                continue
                
            link_text = self.generate_link_text("", conn.target_file, 
                                              getattr(conn, 'content_overlap', ''))
            
            # Detect insertion context
            location, context = InsertionContextDetector.detect_insertion_point("", "related")
            
            suggestion = LinkSuggestion(
                source_note=getattr(conn, 'source_file', target_note),
                target_note=conn.target_file,
                suggested_link_text=link_text,
                similarity_score=getattr(conn, 'similarity_score', 0.5),
                quality_score=quality.score,
                confidence=quality.confidence,
                explanation=quality.explanation,
                insertion_context=context,
                suggested_location=location
            )
            suggestions.append(suggestion)
        
        # Use batch processor for efficient sorting and filtering
        return SuggestionBatchProcessor.process_batch(suggestions, min_qual, max_res)
    
    def generate_link_text(self, source_content: str, target_content: str, content_overlap: str = "") -> str:
        """
        Generate intelligent link text based on content analysis
        
        Args:
            source_content: Content or title of source note
            target_content: Content or title of target note  
            content_overlap: Shared concepts between notes
            
        Returns:
            Formatted link text like [[concept name]]
        """
        # Use extracted utility for intelligent link text generation
        return LinkTextGenerator.generate_intelligent_link_text(target_content, content_overlap)
    
    def score_link_quality(self, connection: Any) -> QualityScore:
        """
        Assess the quality of a suggested link connection
        
        Args:
            connection: Connection object with similarity and context data
            
        Returns:
            QualityScore with score, confidence, and explanation
        """
        # Extract data from connection object
        similarity_score = getattr(connection, 'similarity_score', 0.5)
        content_overlap = getattr(connection, 'content_overlap', '')
        
        # Use extracted utility for quality assessment
        return LinkQualityAssessor.assess_connection_quality(
            similarity_score=similarity_score,
            content_overlap=content_overlap
        )
