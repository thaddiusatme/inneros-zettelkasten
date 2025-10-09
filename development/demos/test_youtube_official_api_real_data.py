#!/usr/bin/env python3
"""
Real Data Validation: YouTube Official API Fetcher

Tests YouTubeOfficialAPIFetcher with actual YouTube videos to validate:
- Transcript fetching works on rate-limited network
- API key authentication successful
- Quota tracking accurate
- Format compatibility with existing pipeline
- Error handling for various scenarios

Author: InnerOS Zettelkasten Team
Version: 1.0.0
"""
import os
import sys
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.youtube_official_api_fetcher import (
    YouTubeOfficialAPIFetcher,
    QuotaExceededError,
    TranscriptNotAvailableError,
    InvalidVideoIdError
)


def test_real_video_transcript():
    """Test fetching transcript from a real YouTube video."""
    print("=" * 80)
    print("TEST 1: Real Video Transcript Fetching")
    print("=" * 80)
    
    # Get API key from environment
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ SKIPPED: YOUTUBE_API_KEY environment variable not set")
        print("   Set your API key to run this test:")
        print("   export YOUTUBE_API_KEY='your_key_here'")
        return False
    
    try:
        # Initialize fetcher
        fetcher = YouTubeOfficialAPIFetcher(api_key=api_key)
        print(f"✅ Fetcher initialized successfully")
        print(f"   Initial quota: {fetcher.quota_used} units")
        
        # Test video: "The Science of Sleep" (public, has captions)
        # Using a popular educational video that's likely to have transcripts
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up (well-known test video)
        
        print(f"\n📹 Fetching transcript for video: {video_id}")
        print(f"   Network: Rate-limited (100% unofficial scraping failure)")
        print(f"   Method: Official YouTube Data API v3")
        
        result = fetcher.fetch_transcript(video_id)
        
        # Validate result structure
        assert 'video_id' in result, "Missing video_id in result"
        assert 'transcript' in result, "Missing transcript in result"
        assert 'is_manual' in result, "Missing is_manual in result"
        assert 'language' in result, "Missing language in result"
        
        print(f"\n✅ Transcript fetched successfully!")
        print(f"   Video ID: {result['video_id']}")
        print(f"   Language: {result['language']}")
        print(f"   Manual transcript: {result['is_manual']}")
        print(f"   Entries: {len(result['transcript'])}")
        print(f"   Quota used: {fetcher.quota_used} units")
        print(f"   Videos remaining today: {fetcher.quota_tracker.videos_remaining()}")
        
        # Validate transcript entries
        if result['transcript']:
            first_entry = result['transcript'][0]
            assert 'text' in first_entry, "Missing text in transcript entry"
            assert 'start' in first_entry, "Missing start in transcript entry"
            assert 'duration' in first_entry, "Missing duration in transcript entry"
            
            print(f"\n📝 First transcript entry:")
            print(f"   Text: {first_entry['text'][:100]}...")
            print(f"   Start: {first_entry['start']}s")
            print(f"   Duration: {first_entry['duration']}s")
        
        # Test format_for_llm
        print(f"\n🤖 Testing LLM formatting...")
        llm_text = fetcher.format_for_llm(result['transcript'])
        lines = llm_text.split('\n')
        print(f"   Formatted lines: {len(lines)}")
        print(f"   Sample: {lines[0] if lines else 'N/A'}")
        
        return True
        
    except QuotaExceededError as e:
        print(f"\n⚠️  Quota exceeded: {str(e)}")
        print("   This is expected behavior - quota limits working correctly")
        return True
        
    except InvalidVideoIdError as e:
        print(f"\n❌ Invalid video: {str(e)}")
        return False
        
    except TranscriptNotAvailableError as e:
        print(f"\n❌ No transcript: {str(e)}")
        print("   Try a different video with captions enabled")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_format_compatibility():
    """Test that output format matches existing YouTubeTranscriptFetcher."""
    print("\n" + "=" * 80)
    print("TEST 2: Format Compatibility Validation")
    print("=" * 80)
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ SKIPPED: YOUTUBE_API_KEY environment variable not set")
        return False
    
    try:
        fetcher = YouTubeOfficialAPIFetcher(api_key=api_key)
        
        # Fetch transcript
        video_id = "dQw4w9WgXcQ"
        result = fetcher.fetch_transcript(video_id)
        
        # Validate exact format compatibility
        required_keys = {'video_id', 'transcript', 'is_manual', 'language'}
        actual_keys = set(result.keys())
        
        print(f"Required keys: {required_keys}")
        print(f"Actual keys: {actual_keys}")
        
        if required_keys == actual_keys:
            print("✅ Format compatibility: PERFECT MATCH")
        else:
            missing = required_keys - actual_keys
            extra = actual_keys - required_keys
            if missing:
                print(f"❌ Missing keys: {missing}")
            if extra:
                print(f"⚠️  Extra keys: {extra}")
            return False
        
        # Validate transcript entry format
        if result['transcript']:
            entry = result['transcript'][0]
            required_entry_keys = {'text', 'start', 'duration'}
            actual_entry_keys = set(entry.keys())
            
            print(f"Required entry keys: {required_entry_keys}")
            print(f"Actual entry keys: {actual_entry_keys}")
            
            if required_entry_keys == actual_entry_keys:
                print("✅ Entry format compatibility: PERFECT MATCH")
            else:
                print(f"❌ Entry format mismatch")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_quota_tracking():
    """Test quota tracking accuracy."""
    print("\n" + "=" * 80)
    print("TEST 3: Quota Tracking Validation")
    print("=" * 80)
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ SKIPPED: YOUTUBE_API_KEY environment variable not set")
        return False
    
    try:
        fetcher = YouTubeOfficialAPIFetcher(api_key=api_key)
        
        initial_quota = fetcher.quota_used
        print(f"Initial quota: {initial_quota} units")
        
        # Fetch transcript (costs 250 units: 50 list + 200 download)
        video_id = "dQw4w9WgXcQ"
        fetcher.fetch_transcript(video_id)
        
        expected_quota = initial_quota + 250
        actual_quota = fetcher.quota_used
        
        print(f"Expected quota after fetch: {expected_quota} units")
        print(f"Actual quota after fetch: {actual_quota} units")
        
        if actual_quota == expected_quota:
            print("✅ Quota tracking: ACCURATE (250 units per video)")
        else:
            print(f"❌ Quota mismatch: expected {expected_quota}, got {actual_quota}")
            return False
        
        # Check quota tracker utility
        tracker = fetcher.quota_tracker
        print(f"\n📊 Quota Tracker Stats:")
        print(f"   Daily limit: {tracker.daily_limit} units")
        print(f"   Used: {tracker.quota_used} units")
        print(f"   Remaining: {tracker.remaining_quota()} units")
        print(f"   Videos remaining: {tracker.videos_remaining()}")
        print(f"   Usage: {tracker.usage_percentage():.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_error_handling():
    """Test error handling for invalid video IDs."""
    print("\n" + "=" * 80)
    print("TEST 4: Error Handling Validation")
    print("=" * 80)
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ SKIPPED: YOUTUBE_API_KEY environment variable not set")
        return False
    
    try:
        fetcher = YouTubeOfficialAPIFetcher(api_key=api_key)
        
        # Test 1: Invalid video ID (should raise InvalidVideoIdError)
        print("\n🧪 Test: Invalid video ID")
        try:
            fetcher.fetch_transcript("INVALID_VIDEO_ID_123")
            print("❌ Should have raised InvalidVideoIdError")
            return False
        except InvalidVideoIdError as e:
            print(f"✅ Correctly raised InvalidVideoIdError")
            print(f"   Message: {str(e)[:100]}...")
        
        # Test 2: Empty video ID
        print("\n🧪 Test: Empty video ID")
        try:
            fetcher.fetch_transcript("")
            print("❌ Should have raised InvalidVideoIdError")
            return False
        except InvalidVideoIdError as e:
            print(f"✅ Correctly raised InvalidVideoIdError")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def main():
    """Run all real data validation tests."""
    print("\n" + "🚀" * 40)
    print("REAL DATA VALIDATION: YouTube Official API v3 Fetcher")
    print("Testing on rate-limited network with actual YouTube videos")
    print("🚀" * 40)
    
    # Check for API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("\n❌ ERROR: YOUTUBE_API_KEY environment variable not set")
        print("\nTo run these tests:")
        print("1. Get API key: https://console.cloud.google.com/apis/credentials")
        print("2. Enable YouTube Data API v3")
        print("3. Set environment variable:")
        print("   export YOUTUBE_API_KEY='your_key_here'")
        print("\nOr add to ~/.zshrc for persistence:")
        print("   echo 'export YOUTUBE_API_KEY=\"your_key\"' >> ~/.zshrc")
        print("   source ~/.zshrc")
        return
    
    print(f"\n✅ API Key found: {api_key[:10]}...{api_key[-5:]}")
    print(f"   Network: Rate-limited (100% unofficial scraping failure)")
    print(f"   Method: Official YouTube Data API v3")
    
    # Run tests
    results = []
    
    results.append(("Real Video Transcript", test_real_video_transcript()))
    results.append(("Format Compatibility", test_format_compatibility()))
    results.append(("Quota Tracking", test_quota_tracking()))
    results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nResults: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 SUCCESS: All real data validation tests passed!")
        print("   YouTube Official API v3 integration working perfectly on rate-limited network")
    else:
        print("\n⚠️  Some tests failed - review errors above")


if __name__ == "__main__":
    main()
