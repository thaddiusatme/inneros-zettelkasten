#!/usr/bin/env python3
"""
YouTube Processor Real Data Test

Tests the complete YouTubeProcessor pipeline with a real YouTube video:
1. Fetches actual transcript
2. Extracts quotes with AI
3. Formats markdown
4. Creates note file

This validates that all 4 components work together in production.
"""

import sys
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.youtube_processor import YouTubeProcessor

def main():
    """Test YouTubeProcessor with real YouTube video."""
    
    # Test video: Different video to validate variety
    # Using video from latest note
    test_url = "https://www.youtube.com/watch?v=EUG65dIY-2k"
    
    print("=" * 70)
    print("  YouTube Processor - Real Data Test")
    print("=" * 70)
    print()
    print(f"🎥 Processing: {test_url}")
    print()
    
    # Initialize processor
    processor = YouTubeProcessor()
    
    # Process video with user context
    user_context = "I'm interested in AI and digital transformation"
    
    print("⏳ Starting pipeline...")
    print()
    
    try:
        result = processor.process_video(
            url=test_url,
            user_context=user_context,
            max_quotes=5,
            min_quality=0.7
        )
        
        # Display results
        if result["success"]:
            print("✅ PROCESSING COMPLETE!")
            print()
            print("📊 Results:")
            print(f"   Video ID: {result['video_id']}")
            print(f"   Quotes Extracted: {result['quotes_extracted']}")
            print(f"   Note Created: {result['file_path']}")
            print()
            print("⏱️  Performance:")
            print(f"   Transcript Fetch: {result['timing']['fetch']:.2f}s")
            print(f"   Quote Extraction: {result['timing']['extraction']:.2f}s")
            print(f"   Markdown Format: {result['timing']['formatting']:.2f}s")
            print(f"   Total Time: {result['timing']['total']:.2f}s")
            print()
            print("📝 Metadata:")
            print(f"   Type: {result['metadata']['type']}")
            print(f"   Status: {result['metadata']['status']}")
            print(f"   Tags: {', '.join(result['metadata']['tags'])}")
            print()
            print(f"🎉 Success! Note ready in Obsidian at:")
            print(f"   {result['file_path']}")
            
        else:
            print("❌ PROCESSING FAILED")
            print(f"   Error: {result['error']}")
            print(f"   Time: {result['timing']['total']:.2f}s")
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print()
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
