#!/usr/bin/env python3
"""
Debug: See what LLM actually returns
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher
from ai.ollama_client import OllamaClient

# Fetch transcript
fetcher = YouTubeTranscriptFetcher()
transcript_result = fetcher.fetch_transcript("-9iDW7Zgv1Q")
formatted = fetcher.format_for_llm(transcript_result["transcript"])

print(f"Transcript length: {len(formatted)} characters")
print(f"Estimated tokens: ~{len(formatted) // 4}")
print()

# Build a simple prompt
prompt = f"""You are extracting quotes from a YouTube transcript.

TRANSCRIPT:
{formatted[:2000]}... (truncated for testing)

Extract 3 quotes in JSON format:
{{
    "quotes": [
        {{"text": "quote here", "timestamp": "MM:SS", "relevance_score": 0.85}}
    ]
}}
"""

print("Testing LLM with truncated transcript...")
print(f"Prompt length: {len(prompt)} characters")
print()

client = OllamaClient()
try:
    response = client.generate_completion(
        prompt=prompt,
        system_prompt="You are a helpful assistant.",
        max_tokens=500
    )
    print(f"✅ Response received: {len(response)} characters")
    print()
    print("RESPONSE:")
    print(response[:500] if len(response) > 500 else response)
except Exception as e:
    print(f"❌ Error: {e}")
