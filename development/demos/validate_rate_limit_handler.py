#!/usr/bin/env python3
"""
Rate Limit Handler Validation Script

Tests the YouTube rate limit handler with real network conditions.
Provides metrics on retry behavior and success rates.

Usage:
    python3 development/demos/validate_rate_limit_handler.py [video_id]
    
Example:
    python3 development/demos/validate_rate_limit_handler.py dQw4w9WgXcQ
"""

import sys
import time
import yaml
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.automation.youtube_rate_limit_handler import YouTubeRateLimitHandler
from src.ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher


def load_config():
    """Load rate limit configuration from daemon_config.yaml"""
    config_path = Path(__file__).parent.parent / 'daemon_config.yaml'
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return None
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    rate_limit_config = config.get('youtube_handler', {}).get('rate_limit', {})
    
    if not rate_limit_config:
        print("⚠️  No rate_limit config found in youtube_handler section")
        return None
    
    return rate_limit_config


def test_rate_limit_handler(video_id: str, config: dict):
    """Test rate limit handler with a real video ID"""
    print("\n" + "="*60)
    print("🧪 RATE LIMIT HANDLER VALIDATION")
    print("="*60)
    
    print(f"\n📋 Configuration:")
    print(f"   • Video ID: {video_id}")
    print(f"   • Max Retries: {config['max_retries']}")
    print(f"   • Base Delay: {config['base_delay']}s")
    print(f"   • Max Delay: {config['max_delay']}s")
    print(f"   • Backoff Multiplier: {config['backoff_multiplier']}")
    
    # Initialize handler
    handler = YouTubeRateLimitHandler(config)
    fetcher = YouTubeTranscriptFetcher()
    
    print(f"\n🔄 Attempting to fetch transcript...")
    start_time = time.time()
    
    try:
        # Attempt fetch with retry logic
        result = handler.fetch_with_retry(
            video_id,
            lambda vid: fetcher.fetch_transcript(vid)
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ SUCCESS!")
        print(f"   • Transcript fetched successfully")
        print(f"   • Total time: {elapsed:.2f}s")
        print(f"   • Transcript entries: {len(result['transcript'])}")
        
    except Exception as e:
        elapsed = time.time() - start_time
        
        print(f"\n❌ FAILED after {elapsed:.2f}s")
        print(f"   • Error type: {type(e).__name__}")
        print(f"   • Error message: {str(e)[:200]}")
    
    # Display metrics
    metrics = handler.metrics
    stats = handler.get_retry_statistics()
    
    print(f"\n📊 Metrics:")
    print(f"   • Total Attempts: {metrics['total_attempts']}")
    print(f"   • Succeeded: {metrics['succeeded']}")
    print(f"   • Rate Limited: {metrics['rate_limited']}")
    print(f"   • Failed: {metrics['failed']}")
    print(f"   • Permanent Failures: {metrics['permanent_failures']}")
    
    print(f"\n📈 Statistics:")
    print(f"   • Success Rate: {stats['success_rate']:.1%}")
    print(f"   • Retry Rate: {stats['retry_rate']:.1%}")
    print(f"   • Failure Rate: {stats['failure_rate']:.1%}")
    print(f"   • Avg Attempts: {stats['avg_attempts']:.2f}")
    
    print("\n" + "="*60)
    
    return metrics, stats


def main():
    """Main validation function"""
    # Default test video (Rick Astley - Never Gonna Give You Up)
    # This is a well-known public video that should have transcripts
    default_video_id = "dQw4w9WgXcQ"
    
    video_id = sys.argv[1] if len(sys.argv) > 1 else default_video_id
    
    print("🎬 YouTube Rate Limit Handler Validation")
    print(f"📍 Testing with video ID: {video_id}")
    
    # Load configuration
    config = load_config()
    if not config:
        print("\n❌ Failed to load configuration. Exiting.")
        return 1
    
    # Run validation test
    try:
        metrics, stats = test_rate_limit_handler(video_id, config)
        
        # Provide recommendations based on results
        print("\n💡 Recommendations:")
        
        if stats['retry_rate'] > 0.5:
            print("   ⚠️  High retry rate detected (>50%)")
            print("   → Consider increasing base_delay or max_delay")
            print("   → Current network may be rate-limited")
        elif stats['retry_rate'] > 0.2:
            print("   ℹ️  Moderate retry rate (20-50%)")
            print("   → Current configuration appears adequate")
        else:
            print("   ✅ Low retry rate (<20%)")
            print("   → Excellent network conditions or no rate limiting")
        
        if stats['failure_rate'] > 0:
            print(f"\n   ⚠️  {stats['failure_rate']:.1%} failure rate")
            print("   → Review error logs for root cause")
            print("   → May need to increase max_retries")
        
        print("\n🧪 Validation complete!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
