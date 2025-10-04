#!/usr/bin/env python3
"""
TDD Iteration 2 RED Phase: Context-Aware Quote Extractor Tests

Tests for ContextAwareQuoteExtractor class that extracts high-value quotes
from YouTube transcripts using LLM intelligence and user context.

Following TDD methodology proven across 11+ successful iterations.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.youtube_quote_extractor import (
    ContextAwareQuoteExtractor,
    QuoteExtractionError,
    EmptyTranscriptError,
    LLMUnavailableError
)


class TestContextAwareQuoteExtractorBasicFunctionality:
    """Test P0: Core quote extraction functionality"""
    
    def test_extract_quotes_from_transcript(self):
        """
        RED Phase Test 1: Extract 3-7 quotes from valid transcript
        
        Success case: Should return formatted quotes with metadata
        """
        extractor = ContextAwareQuoteExtractor()
        
        sample_transcript = """
        [00:15] AI is transforming how we build software today
        [01:30] The key insight is that context matters more than raw data
        [02:45] Machine learning models need quality training data to succeed
        [04:00] Best practice: Always validate your outputs with real users
        [05:30] Future trends point toward hybrid AI-human workflows
        """
        
        result = extractor.extract_quotes(
            transcript=sample_transcript,
            max_quotes=7,
            min_quality=0.7
        )
        
        # Verify result structure
        assert result is not None
        assert "quotes" in result
        assert "summary" in result
        assert "key_themes" in result
        assert "processing_time" in result
        
        # Verify quotes
        quotes = result["quotes"]
        assert isinstance(quotes, list)
        assert 3 <= len(quotes) <= 7, f"Expected 3-7 quotes, got {len(quotes)}"
        
        # Each quote should have required fields
        for quote in quotes:
            assert "text" in quote
            assert "timestamp" in quote
            assert "relevance_score" in quote
            assert "context" in quote
            assert isinstance(quote["text"], str)
            assert len(quote["text"]) > 0
            assert 0.0 <= quote["relevance_score"] <= 1.0
    
    def test_extract_quotes_with_user_context(self):
        """
        RED Phase Test 2: User context influences quote selection
        
        Quotes should be more relevant when user provides context
        """
        extractor = ContextAwareQuoteExtractor()
        
        sample_transcript = """
        [00:15] AI is transforming software development workflows
        [01:30] Quantum computing is still in early experimental stages
        [02:45] Machine learning requires substantial computational resources
        [04:00] The creator economy is booming with new opportunities
        [05:30] Digital entrepreneurship has low barriers to entry
        """
        
        user_context = "I'm interested in creator economy and digital entrepreneurship"
        
        result = extractor.extract_quotes(
            transcript=sample_transcript,
            user_context=user_context,
            max_quotes=5
        )
        
        # Verify context influenced selection
        quotes = result["quotes"]
        assert len(quotes) > 0
        
        # At least some quotes should mention creator/entrepreneurship themes
        relevant_keywords = ["creator", "economy", "entrepreneurship", "opportunities"]
        quote_texts = " ".join([q["text"].lower() for q in quotes])
        
        matches = sum(1 for keyword in relevant_keywords if keyword in quote_texts)
        assert matches > 0, "User context should influence quote selection"
        
        # Each quote should have context explanation
        for quote in quotes:
            assert "context" in quote
            assert len(quote["context"]) > 0
    
    def test_extract_quotes_without_context(self):
        """
        RED Phase Test 3: Works with no user context (generic mode)
        
        Should extract high-quality quotes based on intrinsic value
        """
        extractor = ContextAwareQuoteExtractor()
        
        sample_transcript = """
        [00:15] The most important lesson: start before you're ready
        [01:30] Data shows 80% of success comes from consistency
        [02:45] Technical implementation details for advanced users only
        [04:00] Revolutionary breakthrough in quantum entanglement achieved
        """
        
        result = extractor.extract_quotes(
            transcript=sample_transcript,
            user_context=None,  # No context provided
            max_quotes=5
        )
        
        # Should still extract valuable quotes
        quotes = result["quotes"]
        assert len(quotes) >= 2, "Should extract quotes even without user context"
        
        # Quotes should prioritize impactful statements
        for quote in quotes:
            assert quote["relevance_score"] >= 0.7


class TestContextAwareQuoteExtractorFormatting:
    """Test P0: Quote formatting and metadata"""
    
    def test_quotes_include_timestamps(self):
        """
        RED Phase Test 4: All quotes preserve MM:SS timestamps
        
        Should maintain temporal reference from original transcript
        """
        extractor = ContextAwareQuoteExtractor()
        
        sample_transcript = """
        [00:15] First important point at 15 seconds
        [01:30] Second key insight at 1 minute 30 seconds
        [10:45] Third major point at 10 minutes 45 seconds
        """
        
        result = extractor.extract_quotes(transcript=sample_transcript)
        
        quotes = result["quotes"]
        assert len(quotes) > 0
        
        # Each quote must have timestamp in MM:SS format
        for quote in quotes:
            timestamp = quote["timestamp"]
            assert isinstance(timestamp, str)
            
            # Should match MM:SS or HH:MM:SS format
            parts = timestamp.split(":")
            assert len(parts) >= 2, f"Invalid timestamp format: {timestamp}"
            
            # Verify it's a valid time format
            assert all(part.isdigit() or part == "XX" for part in parts), \
                f"Timestamp should be numeric or XX:XX: {timestamp}"
    
    def test_quote_quality_scoring(self):
        """
        RED Phase Test 5: Each quote has relevance_score 0.0-1.0
        
        Score indicates quality/relevance of the quote
        """
        extractor = ContextAwareQuoteExtractor()
        
        sample_transcript = """
        [00:15] Groundbreaking research reveals new paradigm in AI safety
        [01:30] Um, yeah, so like, I think maybe it's interesting
        [02:45] Critical insight: context determines everything in ML systems
        """
        
        result = extractor.extract_quotes(transcript=sample_transcript)
        
        quotes = result["quotes"]
        assert len(quotes) > 0
        
        for quote in quotes:
            score = quote["relevance_score"]
            assert isinstance(score, (int, float))
            assert 0.0 <= score <= 1.0, f"Score {score} out of range"
            
        # High-quality quotes should score higher
        high_quality_quotes = [q for q in quotes if "critical" in q["text"].lower() 
                               or "groundbreaking" in q["text"].lower()]
        if high_quality_quotes:
            assert any(q["relevance_score"] >= 0.8 for q in high_quality_quotes)


class TestContextAwareQuoteExtractorFiltering:
    """Test P0: Quote filtering and limiting"""
    
    def test_filter_low_quality_quotes(self):
        """
        RED Phase Test 6: Quotes below min_quality threshold excluded
        
        Only high-quality quotes should be returned
        """
        extractor = ContextAwareQuoteExtractor()
        
        sample_transcript = """
        [00:15] Revolutionary breakthrough in quantum computing achieved
        [01:30] Um, so, like, yeah, interesting stuff here
        [02:45] Critical insight: data quality trumps quantity always
        """
        
        # Set high quality threshold
        result = extractor.extract_quotes(
            transcript=sample_transcript,
            min_quality=0.75
        )
        
        quotes = result["quotes"]
        
        # All returned quotes should meet quality threshold
        for quote in quotes:
            assert quote["relevance_score"] >= 0.75, \
                f"Quote scored {quote['relevance_score']}, below min_quality 0.75"
    
    def test_limit_max_quotes(self):
        """
        RED Phase Test 7: Returns max_quotes or fewer (3-7 target)
        
        Should respect maximum quote limit
        """
        extractor = ContextAwareQuoteExtractor()
        
        # Long transcript with many potential quotes
        sample_transcript = """
        [00:15] First important insight about AI systems
        [01:30] Second key point on machine learning
        [02:45] Third critical observation on data quality
        [04:00] Fourth major breakthrough in NLP
        [05:15] Fifth revolutionary discovery in CV
        [06:30] Sixth groundbreaking research result
        [07:45] Seventh essential principle for ML
        [09:00] Eighth paradigm shift in AI safety
        [10:15] Ninth transformative approach to LLMs
        [11:30] Tenth incredible advancement in robotics
        """
        
        # Request maximum of 5 quotes
        result = extractor.extract_quotes(
            transcript=sample_transcript,
            max_quotes=5
        )
        
        quotes = result["quotes"]
        assert len(quotes) <= 5, f"Expected <=5 quotes, got {len(quotes)}"
        
        # Should return at least 3 for good content
        assert len(quotes) >= 3, f"Expected >=3 quotes from quality content"


class TestContextAwareQuoteExtractorErrorHandling:
    """Test P0: Comprehensive error handling"""
    
    def test_handle_empty_transcript(self):
        """
        RED Phase Test 8: Graceful error for empty transcript
        
        Should raise EmptyTranscriptError with clear message
        """
        extractor = ContextAwareQuoteExtractor()
        
        with pytest.raises(EmptyTranscriptError) as exc_info:
            extractor.extract_quotes(transcript="")
        
        assert "empty" in str(exc_info.value).lower()
        
        # Also test whitespace-only
        with pytest.raises(EmptyTranscriptError):
            extractor.extract_quotes(transcript="   \n\n  ")
    
    def test_handle_ollama_unavailable(self):
        """
        RED Phase Test 9: Fallback when LLM service down
        
        Should raise LLMUnavailableError or return graceful fallback
        """
        extractor = ContextAwareQuoteExtractor()
        
        sample_transcript = "[00:15] Test content for error handling"
        
        # Mock OllamaClient to simulate service unavailability
        with patch.object(extractor, 'ollama_client') as mock_client:
            mock_client.generate_completion.side_effect = ConnectionError("Service unavailable")
            
            with pytest.raises(LLMUnavailableError) as exc_info:
                extractor.extract_quotes(transcript=sample_transcript)
            
            assert "unavailable" in str(exc_info.value).lower() or "llm" in str(exc_info.value).lower()
    
    def test_handle_malformed_llm_json_response(self):
        """
        RED Phase Test 10: Parse quotes even if LLM returns markdown-wrapped or slightly broken JSON
        
        Critical for production reliability - LLMs often wrap JSON in markdown
        """
        extractor = ContextAwareQuoteExtractor()
        
        sample_transcript = "[00:15] Important insight about AI systems"
        
        # Test Case 1: Markdown-wrapped JSON
        markdown_wrapped_response = '''```json
{
    "quotes": [
        {
            "text": "Important insight about AI systems",
            "timestamp": "00:15",
            "relevance_score": 0.85,
            "context": "Key AI concept",
            "category": "key-insight"
        }
    ],
    "summary": "Discussion of AI systems",
    "key_themes": ["ai", "systems"]
}
```'''
        
        with patch.object(extractor, 'ollama_client') as mock_client:
            mock_client.generate_completion.return_value = markdown_wrapped_response
            
            result = extractor.extract_quotes(transcript=sample_transcript)
            
            # Should successfully parse despite markdown wrapping
            assert "quotes" in result
            assert len(result["quotes"]) > 0
            assert result["quotes"][0]["text"] == "Important insight about AI systems"
        
        # Test Case 2: Slightly malformed JSON with trailing comma
        malformed_json = '''{
    "quotes": [{
        "text": "Test quote",
        "timestamp": "00:15",
        "relevance_score": 0.8,
        "context": "Test context",
        "category": "key-insight",
    }],
    "summary": "Test summary",
    "key_themes": ["test"]
}'''
        
        with patch.object(extractor, 'ollama_client') as mock_client:
            mock_client.generate_completion.return_value = malformed_json
            
            # Should attempt to repair and parse
            try:
                result = extractor.extract_quotes(transcript=sample_transcript)
                assert "quotes" in result  # Should succeed if repair works
            except QuoteExtractionError as e:
                # Should raise clear error if repair fails
                assert "json" in str(e).lower() or "parse" in str(e).lower()


class TestContextAwareQuoteExtractorAdvancedFeatures:
    """Test P1: Advanced features (quote categorization, themes)"""
    
    def test_categorize_quotes_by_type(self):
        """
        RED Phase Test 11: Quotes categorized: key-insight, actionable, quote, definition
        
        Helps users understand the nature of each quote
        """
        extractor = ContextAwareQuoteExtractor()
        
        sample_transcript = """
        [00:15] The fundamental definition: AI is the simulation of human intelligence
        [01:30] Action item: Always test your models with real user data
        [02:45] As Einstein said, "Imagination is more important than knowledge"
        [04:00] Critical insight: context determines everything in machine learning
        """
        
        result = extractor.extract_quotes(transcript=sample_transcript)
        
        quotes = result["quotes"]
        assert len(quotes) > 0
        
        # Each quote should have a category
        valid_categories = ["key-insight", "actionable", "quote", "definition"]
        
        for quote in quotes:
            assert "category" in quote, "Quote missing category field"
            assert quote["category"] in valid_categories, \
                f"Invalid category: {quote['category']}"
        
        # Verify categorization makes sense (if we have all types)
        categories = [q["category"] for q in quotes]
        
        # Should have some variety in categories
        unique_categories = set(categories)
        assert len(unique_categories) >= 1, "Should have at least one category type"


# RED Phase Summary
"""
TDD Iteration 2 RED Phase Complete: 11 Failing Tests

Test Coverage:
- P0 Core Functionality: 3 tests (basic extraction, with/without context)
- P0 Formatting: 2 tests (timestamps, quality scoring)
- P0 Filtering: 2 tests (quality threshold, max limit)
- P0 Error Handling: 3 tests (empty, unavailable, malformed JSON)
- P1 Advanced Features: 1 test (quote categorization)

Key Testing Strategies:
- Mock OllamaClient for isolated unit testing
- Test real LLM response patterns (markdown wrapping, malformed JSON)
- Verify user context influences quote selection
- Ensure quality filtering and limiting work correctly
- Comprehensive error handling for production reliability

All tests should FAIL until GREEN Phase implementation.

Next Steps:
1. Run pytest to confirm 11 failures (0 passing)
2. Commit RED phase with descriptive message
3. Begin GREEN Phase implementation in src/ai/youtube_quote_extractor.py

Implementation Hints for GREEN Phase:
- Use OllamaClient similar to AITagger pattern
- Build prompt with few-shot examples (see planning doc)
- Parse LLM JSON response with markdown unwrapping
- Filter quotes by min_quality threshold
- Limit results to max_quotes
- Handle edge cases gracefully (empty transcript, service down, malformed JSON)
"""
