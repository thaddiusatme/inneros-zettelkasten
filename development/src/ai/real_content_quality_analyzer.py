#!/usr/bin/env python3
"""
Real Content Quality Analyzer - TDD Iteration 3 GREEN Phase
Analyzes content quality for real connection discovery
"""

from .connection_integration_utils import ConnectionQualityAnalyzer
from .link_suggestion_utils import QualityScore


class RealContentQualityAnalyzer:
    """Analyzes quality of connections using real content analysis"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.analyzer = ConnectionQualityAnalyzer()
    
    def analyze_connection_quality(self, content1: str, content2: str) -> QualityScore:
        """
        Analyze connection quality between two content strings
        
        Args:
            content1: First content string
            content2: Second content string
            
        Returns:
            QualityScore with score, confidence, and explanation
        """
        return self.analyzer.analyze_connection_quality(content1, content2)
