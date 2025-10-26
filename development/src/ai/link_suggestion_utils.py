#!/usr/bin/env python3
"""
Link Suggestion Utilities - Extracted from LinkSuggestionEngine for reusability
Contains modular utilities for link text generation and quality assessment
"""

from dataclasses import dataclass
from typing import List, Any
import re


@dataclass
class QualityScore:
    """Data model for link quality assessment"""
    score: float  # 0.0 to 1.0
    confidence: str  # "high", "medium", "low"
    explanation: str


class LinkTextGenerator:
    """Utility class for generating intelligent link text from note metadata"""

    @staticmethod
    def generate_from_file_path(file_path: str) -> str:
        """
        Generate link text from file path
        
        Args:
            file_path: Path to target note file
            
        Returns:
            Clean, readable link text
        """
        # Remove .md extension and path
        if file_path.endswith('.md'):
            name = file_path.replace('.md', '').split('/')[-1]
        else:
            name = file_path.split('/')[-1]

        # Convert hyphens/underscores to spaces and title case
        name = name.replace('-', ' ').replace('_', ' ')

        # Remove timestamps and common prefixes
        name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', name)  # Remove date prefixes
        name = re.sub(r'^(fleeting|permanent|lit|zettel)-', '', name)  # Remove type prefixes

        return name.title().strip()

    @staticmethod
    def generate_from_semantic_overlap(overlap_terms: str, min_term_length: int = 3) -> str:
        """
        Generate semantically meaningful link text from content overlap
        
        Args:
            overlap_terms: Space-separated terms showing content overlap
            min_term_length: Minimum length for meaningful terms
            
        Returns:
            Semantic link text based on shared concepts
        """
        if not overlap_terms:
            return ""

        terms = overlap_terms.split()
        # Filter for meaningful terms (longer than min_term_length)
        meaningful_terms = [term for term in terms if len(term) >= min_term_length]

        if len(meaningful_terms) >= 2:
            # Use first 2-3 most meaningful terms
            return ' '.join(meaningful_terms[:3]).title()
        elif meaningful_terms:
            return meaningful_terms[0].title()
        else:
            return ""

    @classmethod
    def generate_intelligent_link_text(cls, file_path: str, content_overlap: str = "") -> str:
        """
        Generate intelligent link text using multiple strategies
        
        Args:
            file_path: Target note file path
            content_overlap: Semantic overlap between notes
            
        Returns:
            Best available link text with [[brackets]]
        """
        # Try semantic approach first
        if content_overlap:
            semantic_text = cls.generate_from_semantic_overlap(content_overlap)
            if semantic_text:
                return f"[[{semantic_text}]]"

        # Fall back to file path approach
        file_text = cls.generate_from_file_path(file_path)
        return f"[[{file_text}]]"


class LinkQualityAssessor:
    """Utility class for assessing link suggestion quality with confidence scoring"""

    # Quality thresholds
    HIGH_QUALITY_THRESHOLD = 0.8
    MEDIUM_QUALITY_THRESHOLD = 0.6

    @classmethod
    def assess_connection_quality(cls, similarity_score: float,
                                content_overlap: str = "",
                                note_types: tuple = None) -> QualityScore:
        """
        Assess quality of a connection with multiple factors
        
        Args:
            similarity_score: Semantic similarity score (0.0-1.0)
            content_overlap: Shared content between notes
            note_types: Tuple of (source_type, target_type) for type compatibility
            
        Returns:
            QualityScore with score, confidence level, and explanation
        """
        base_score = similarity_score

        # Boost score for rich content overlap
        if content_overlap and len(content_overlap.split()) >= 3:
            base_score = min(1.0, base_score + 0.1)

        # Boost score for compatible note types
        if note_types and cls._are_compatible_types(note_types[0], note_types[1]):
            base_score = min(1.0, base_score + 0.05)

        # Determine confidence and explanation
        if base_score >= cls.HIGH_QUALITY_THRESHOLD:
            confidence = "high"
            explanation = cls._generate_high_quality_explanation(similarity_score, content_overlap)
        elif base_score >= cls.MEDIUM_QUALITY_THRESHOLD:
            confidence = "medium"
            explanation = cls._generate_medium_quality_explanation(similarity_score, content_overlap)
        else:
            confidence = "low"
            explanation = cls._generate_low_quality_explanation(similarity_score)

        return QualityScore(
            score=base_score,
            confidence=confidence,
            explanation=explanation
        )

    @staticmethod
    def _are_compatible_types(source_type: str, target_type: str) -> bool:
        """Check if note types are compatible for linking"""
        # Compatible type combinations for Zettelkasten
        compatible_pairs = {
            ('permanent', 'permanent'),
            ('permanent', 'literature'),
            ('literature', 'permanent'),
            ('fleeting', 'permanent'),
            ('permanent', 'fleeting'),
        }

        return (source_type, target_type) in compatible_pairs

    @staticmethod
    def _generate_high_quality_explanation(similarity: float, overlap: str) -> str:
        """Generate explanation for high-quality connections"""
        if overlap and len(overlap.split()) >= 3:
            return f"Strong semantic similarity ({similarity:.1%}) with rich content overlap"
        else:
            return f"Strong semantic similarity ({similarity:.1%}) between note contents"

    @staticmethod
    def _generate_medium_quality_explanation(similarity: float, overlap: str) -> str:
        """Generate explanation for medium-quality connections"""
        if overlap:
            return f"Moderate semantic relationship ({similarity:.1%}) with shared concepts"
        else:
            return f"Moderate semantic relationship ({similarity:.1%}) detected"

    @staticmethod
    def _generate_low_quality_explanation(similarity: float) -> str:
        """Generate explanation for low-quality connections"""
        return f"Weak connection ({similarity:.1%}) - manual review recommended"


class InsertionContextDetector:
    """Utility for detecting appropriate insertion points in notes"""

    # Common section patterns in Zettelkasten notes
    SECTION_PATTERNS = {
        'related_concepts': [
            r'## Related Concepts?',
            r'## Related',
            r'## See Also',
            r'## Connections?'
        ],
        'see_also': [
            r'## See Also',
            r'## References?',
            r'## Links?',
            r'## Further Reading'
        ],
        'main_content': [
            r'## [^#\n]+',  # Any second-level heading
            r'# [^#\n]+',   # Main title
        ]
    }

    @classmethod
    def detect_insertion_point(cls, note_content: str, link_type: str = "related") -> tuple:
        """
        Detect best insertion point for a link in note content
        
        Args:
            note_content: Full content of the target note
            link_type: Type of link relationship ("related", "reference", "concept")
            
        Returns:
            Tuple of (suggested_location, insertion_context)
        """
        lines = note_content.split('\n')

        # Look for existing related sections first
        for section_type, patterns in cls.SECTION_PATTERNS.items():
            for pattern in patterns:
                for i, line in enumerate(lines):
                    if re.match(pattern, line.strip(), re.IGNORECASE):
                        return section_type, line.strip()

        # If no specific sections found, suggest creating one
        if cls._has_structured_content(lines):
            return "related_concepts", "## Related Concepts"
        else:
            return "main_content", "# Main Content"

    @staticmethod
    def _has_structured_content(lines: List[str]) -> bool:
        """Check if note has structured content with headings"""
        heading_count = sum(1 for line in lines if line.strip().startswith('#'))
        return heading_count >= 2


class SuggestionBatchProcessor:
    """Utility for efficient batch processing of link suggestions"""

    @staticmethod
    def sort_by_quality(suggestions: List[Any]) -> List[Any]:
        """Sort suggestions by quality score (highest first)"""
        return sorted(suggestions, key=lambda x: x.quality_score, reverse=True)

    @staticmethod
    def filter_by_threshold(suggestions: List[Any], min_quality: float) -> List[Any]:
        """Filter suggestions below quality threshold"""
        return [s for s in suggestions if s.quality_score >= min_quality]

    @staticmethod
    def limit_results(suggestions: List[Any], max_results: int) -> List[Any]:
        """Limit number of suggestions returned"""
        return suggestions[:max_results]

    @classmethod
    def process_batch(cls, suggestions: List[Any],
                     min_quality: float = 0.0,
                     max_results: int = 10) -> List[Any]:
        """
        Complete batch processing pipeline
        
        Args:
            suggestions: Raw list of suggestions
            min_quality: Minimum quality threshold
            max_results: Maximum results to return
            
        Returns:
            Processed, filtered, and sorted suggestions
        """
        # Filter by quality
        filtered = cls.filter_by_threshold(suggestions, min_quality)

        # Sort by quality
        sorted_suggestions = cls.sort_by_quality(filtered)

        # Limit results
        return cls.limit_results(sorted_suggestions, max_results)
