#!/usr/bin/env python3
"""Quick test with your actual YouTube video"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher

# Your video URL: https://www.youtube.com/watch?v=-9iDW7Zgv1Q
video_id = "-9iDW7Zgv1Q"

print("🎬 Testing YouTube Transcript Fetcher with your video...\n")

fetcher = YouTubeTranscriptFetcher()
result = fetcher.fetch_transcript(video_id)

print(f"✅ SUCCESS!")
print(f"Video ID: {result['video_id']}")
print(f"Language: {result['language']}")
print(f"Manual transcript: {result['is_manual']}")
print(f"Total entries: {len(result['transcript'])}")
print(f"\nFirst 5 entries:")
for i, entry in enumerate(result['transcript'][:5], 1):
    timestamp = fetcher.format_timestamp(entry['start'])
    print(f"  [{timestamp}] {entry['text']}")

print(f"\n📄 LLM Format (first 300 chars):")
llm_text = fetcher.format_for_llm(result['transcript'])
print(llm_text[:300] + "...")

print(f"\n🎯 This transcript can now be processed by your LLM workflow!")
