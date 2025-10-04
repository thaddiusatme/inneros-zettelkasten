"""
Context-Aware Quote Extraction from YouTube Transcripts

Extracts high-value quotes from video transcripts using LLM intelligence
and user context to prioritize relevance.

TDD Iteration 2: GREEN Phase - Complete implementation
"""

import json
import re
import time
from typing import Dict, Any, Optional, List
from .ollama_client import OllamaClient

# Import requests for error handling
try:
    import requests
    RequestsConnectionError = requests.exceptions.ConnectionError
except (ImportError, AttributeError):
    # Fallback if requests not available
    RequestsConnectionError = ConnectionError


# Custom Exceptions
class QuoteExtractionError(Exception):
    """Base exception for quote extraction failures"""
    pass


class EmptyTranscriptError(QuoteExtractionError):
    """Raised when transcript is empty or invalid"""
    pass


class LLMUnavailableError(QuoteExtractionError):
    """Raised when LLM service is unavailable"""
    pass


class ContextAwareQuoteExtractor:
    """
    Extracts high-quality quotes from YouTube transcripts using AI.
    
    Uses LLM intelligence to:
    - Identify impactful quotes from transcript
    - Score quotes by relevance and quality
    - Consider user context for personalized selection
    - Categorize quotes by type (insight, actionable, quote, definition)
    
    Target Performance:
    - <10 seconds processing time
    - 3-7 high-quality quotes per video
    - Quality scores >= 0.7 average
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize quote extractor with configuration.
        
        Args:
            config: Optional configuration for Ollama client
        """
        self.ollama_client = OllamaClient(config=config)
    
    def extract_quotes(
        self,
        transcript: str,
        user_context: Optional[str] = None,
        max_quotes: int = 7,
        min_quality: float = 0.7
    ) -> Dict[str, Any]:
        """
        Extract high-value quotes from transcript.
        
        Args:
            transcript: Formatted transcript with timestamps
            user_context: Optional user context to guide quote selection
            max_quotes: Maximum number of quotes to return (3-7 recommended)
            min_quality: Minimum quality score threshold (0.0-1.0)
            
        Returns:
            Dict containing:
                - quotes: List of quote dicts (text, timestamp, score, context, category)
                - summary: 2-3 sentence video overview
                - key_themes: List of main themes
                - processing_time: Time taken in seconds
                
        Raises:
            EmptyTranscriptError: If transcript is empty or invalid
            LLMUnavailableError: If LLM service is unavailable
            QuoteExtractionError: For other extraction failures
        """
        start_time = time.time()
        
        # Validate transcript
        if not transcript or not transcript.strip():
            raise EmptyTranscriptError("Transcript is empty or contains only whitespace")
        
        try:
            # Build prompt with user context and few-shot examples
            prompt = self._build_prompt(transcript, user_context, max_quotes)
            
            # Generate completion with LLM
            response = self.ollama_client.generate_completion(
                prompt=prompt,
                system_prompt="You are an expert at extracting high-value quotes from content.",
                max_tokens=2000
            )
            
            # Parse LLM response (handle markdown wrapping and malformed JSON)
            result = self._parse_llm_response(response)
            
            # Filter quotes by quality threshold
            filtered_quotes = self._filter_quotes_by_quality(
                result.get("quotes", []),
                min_quality
            )
            
            # Limit to max_quotes
            limited_quotes = filtered_quotes[:max_quotes]
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            return {
                "quotes": limited_quotes,
                "summary": result.get("summary", ""),
                "key_themes": result.get("key_themes", []),
                "processing_time": processing_time
            }
            
        except (ConnectionError, RequestsConnectionError) as e:
            raise LLMUnavailableError(f"LLM service unavailable: {str(e)}")
        except json.JSONDecodeError as e:
            raise QuoteExtractionError(f"Failed to parse LLM JSON response: {str(e)}")
        except Exception as e:
            if "unavailable" in str(e).lower() or "connection" in str(e).lower():
                raise LLMUnavailableError(f"LLM service unavailable: {str(e)}")
            raise QuoteExtractionError(f"Quote extraction failed: {str(e)}")
    
    def _build_prompt(
        self,
        transcript: str,
        user_context: Optional[str],
        max_quotes: int
    ) -> str:
        """
        Build LLM prompt with few-shot examples and edge case handling.
        
        Args:
            transcript: Formatted transcript text
            user_context: Optional user context
            max_quotes: Maximum quotes to extract
            
        Returns:
            Formatted prompt string
        """
        context_text = user_context or "User wants to capture key insights and actionable takeaways"
        
        prompt = f"""You are an expert at extracting high-value quotes from YouTube video transcripts.

USER'S CONTEXT FOR WATCHING THIS VIDEO:
{context_text}

YOUR TASK:
Analyze this transcript and extract 3-{max_quotes} quotes that would be MOST VALUABLE 
for someone who watched this video for the reason described above.

QUALITY CRITERIA:
- Must be verbatim from transcript (no paraphrasing)
- Must be self-contained and meaningful
- Must align with user's learning goals
- Prefer actionable insights over generic statements
- Prefer unique/surprising insights over obvious ones

TRANSCRIPT WITH TIMESTAMPS:
{transcript}

EXAMPLE OUTPUT (Few-Shot Learning):
{{
    "text": "AI will amplify individual creators by 10x in the next few years",
    "timestamp": "01:15",
    "relevance_score": 0.88,
    "context": "Directly addresses creator economy trends that user is interested in",
    "category": "actionable"
}}

IMPORTANT EDGE CASES:
- If timestamp is unclear or missing, use "XX:XX"
- If no high-quality quotes found (all below threshold), return empty quotes array
- NEVER fabricate quotes - only use verbatim text from transcript
- If unsure about relevance, err on the side of lower score

RETURN FORMAT (JSON):
{{
    "summary": "2-3 sentence video overview",
    "quotes": [
        {{
            "text": "exact quote text",
            "timestamp": "MM:SS",
            "relevance_score": 0.0-1.0,
            "context": "why this matters for user",
            "category": "key-insight|actionable|quote|definition"
        }}
    ],
    "key_themes": ["theme1", "theme2", "theme3"]
}}

Focus on quality over quantity. 3 great quotes > 7 mediocre quotes."""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM JSON response, handling markdown wrapping and malformed JSON.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            Parsed JSON dict
            
        Raises:
            QuoteExtractionError: If parsing fails after repair attempts
        """
        # Remove markdown code block wrapping if present
        cleaned = response.strip()
        
        # Handle ```json ... ``` wrapping
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]  # Remove ```json
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]  # Remove ```
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]  # Remove trailing ```
        
        cleaned = cleaned.strip()
        
        # Attempt to parse JSON
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Attempt repair: remove trailing commas
            repaired = re.sub(r',(\s*[}\]])', r'\1', cleaned)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError as e:
                raise QuoteExtractionError(
                    f"Failed to parse JSON response after repair attempts: {str(e)}"
                )
    
    def _filter_quotes_by_quality(
        self,
        quotes: List[Dict[str, Any]],
        min_quality: float
    ) -> List[Dict[str, Any]]:
        """
        Filter quotes by minimum quality threshold.
        
        Args:
            quotes: List of quote dicts
            min_quality: Minimum relevance_score threshold
            
        Returns:
            Filtered list of quotes meeting quality threshold
        """
        return [
            quote for quote in quotes
            if quote.get("relevance_score", 0.0) >= min_quality
        ]
