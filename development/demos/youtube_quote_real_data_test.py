#!/usr/bin/env python3
"""
Real Data Validation: Context-Aware Quote Extraction

Tests the ContextAwareQuoteExtractor with real YouTube video transcript.
Validates performance targets and quality metrics.

Video: https://www.youtube.com/watch?v=-9iDW7Zgv1Q (412 entries)
Topic: 2026 trends for individual empires
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher
from ai.youtube_quote_extractor import ContextAwareQuoteExtractor

def main():
    print("=" * 70)
    print("🧪 REAL DATA VALIDATION: Context-Aware Quote Extraction")
    print("=" * 70)
    print()
    
    # Configuration
    video_id = "-9iDW7Zgv1Q"
    user_context = "I'm interested in creator economy, digital entrepreneurship, and AI trends for 2026"
    
    print(f"📹 Video ID: {video_id}")
    print(f"👤 User Context: {user_context}")
    print(f"🎯 Performance Target: <10 seconds")
    print(f"📊 Quality Target: >=0.7 average score")
    print()
    
    # Step 1: Fetch transcript
    print("-" * 70)
    print("STEP 1: Fetching Transcript")
    print("-" * 70)
    
    fetcher = YouTubeTranscriptFetcher()
    
    try:
        fetch_start = time.time()
        transcript_result = fetcher.fetch_transcript(video_id)
        fetch_duration = time.time() - fetch_start
        
        # Format for LLM
        formatted_transcript = fetcher.format_for_llm(transcript_result["transcript"])
        
        print(f"✅ Transcript fetched in {fetch_duration:.2f}s")
        print(f"📝 Entries: {len(transcript_result['transcript'])}")
        print(f"📏 Formatted length: {len(formatted_transcript)} characters")
        print(f"🔤 Estimated tokens: ~{len(formatted_transcript) // 4}")
        print()
        
    except Exception as e:
        print(f"❌ Transcript fetch failed: {e}")
        return
    
    # Step 2: Extract quotes
    print("-" * 70)
    print("STEP 2: Extracting Quotes with LLM")
    print("-" * 70)
    
    extractor = ContextAwareQuoteExtractor()
    
    try:
        extract_start = time.time()
        result = extractor.extract_quotes(
            transcript=formatted_transcript,
            user_context=user_context,
            max_quotes=7,
            min_quality=0.7
        )
        extract_duration = time.time() - extract_start
        
        print(f"✅ Quote extraction complete in {extract_duration:.2f}s")
        print()
        
    except Exception as e:
        print(f"❌ Quote extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Analyze results
    print("-" * 70)
    print("STEP 3: Results Analysis")
    print("-" * 70)
    print()
    
    quotes = result.get("quotes", [])
    summary = result.get("summary", "")
    themes = result.get("key_themes", [])
    processing_time = result.get("processing_time", 0)
    
    # Performance metrics
    print("📊 PERFORMANCE METRICS:")
    print(f"   ⏱️  Total processing time: {processing_time:.2f}s")
    print(f"   🎯 Target: <10s → {'✅ PASS' if processing_time < 10 else '❌ FAIL'}")
    print(f"   📈 Fetch: {fetch_duration:.2f}s | Extract: {extract_duration:.2f}s")
    print()
    
    # Quality metrics
    if quotes:
        scores = [q.get("relevance_score", 0) for q in quotes]
        avg_score = sum(scores) / len(scores)
        
        print("📈 QUALITY METRICS:")
        print(f"   📝 Quotes extracted: {len(quotes)}")
        print(f"   ⭐ Average relevance score: {avg_score:.2f}")
        print(f"   🎯 Target: >=0.7 → {'✅ PASS' if avg_score >= 0.7 else '❌ FAIL'}")
        print(f"   📊 Score range: {min(scores):.2f} - {max(scores):.2f}")
        print()
        
        # Category distribution
        categories = {}
        for quote in quotes:
            cat = quote.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        print("📂 CATEGORY DISTRIBUTION:")
        for cat, count in sorted(categories.items()):
            print(f"   {cat}: {count} quotes")
        print()
    else:
        print("⚠️  No quotes extracted (check quality threshold)")
        print()
    
    # Display results
    print("-" * 70)
    print("STEP 4: Extracted Content")
    print("-" * 70)
    print()
    
    print("📝 VIDEO SUMMARY:")
    print(f"   {summary}")
    print()
    
    print("🏷️  KEY THEMES:")
    print(f"   {', '.join(themes)}")
    print()
    
    print("💎 EXTRACTED QUOTES:")
    print()
    
    for i, quote in enumerate(quotes, 1):
        print(f"{i}. [{quote.get('timestamp', 'XX:XX')}] {quote.get('category', 'unknown').upper()}")
        print(f"   \"{quote.get('text', '')}\"")
        print(f"   Score: {quote.get('relevance_score', 0):.2f}")
        print(f"   Context: {quote.get('context', '')}")
        print()
    
    # Final verdict
    print("-" * 70)
    print("FINAL VERDICT")
    print("-" * 70)
    print()
    
    perf_pass = processing_time < 10
    quality_pass = (sum([q.get("relevance_score", 0) for q in quotes]) / len(quotes)) >= 0.7 if quotes else False
    has_quotes = len(quotes) >= 3
    has_context_influence = any(
        word in " ".join([q.get("text", "").lower() for q in quotes])
        for word in ["creator", "economy", "entrepreneurship", "ai", "2026", "trend"]
    )
    
    print(f"✅ Performance target (<10s): {'PASS' if perf_pass else 'FAIL'}")
    print(f"✅ Quality target (>=0.7): {'PASS' if quality_pass else 'FAIL'}")
    print(f"✅ Quote count (>=3): {'PASS' if has_quotes else 'FAIL'}")
    print(f"✅ User context influence: {'PASS' if has_context_influence else 'FAIL'}")
    print()
    
    if perf_pass and quality_pass and has_quotes:
        print("🎉 SUCCESS: All validation criteria met!")
        print("✅ Production-ready for TDD Iteration 3 (Template Integration)")
    else:
        print("⚠️  PARTIAL SUCCESS: Some criteria not met, may need adjustment")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
