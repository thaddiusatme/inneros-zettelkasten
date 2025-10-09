#!/usr/bin/env python3
"""
Quick test to verify YouTube Data API v3 key is working.

Tests basic API access and captions endpoint.
"""

import os
import sys

def test_api_key():
    """Test YouTube Data API v3 key"""
    
    print("🔑 Testing YouTube Data API v3 Key...")
    print("=" * 60)
    
    # Check if API key is set
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("❌ YOUTUBE_API_KEY environment variable not set")
        print("\nRun this first:")
        print("  export YOUTUBE_API_KEY='your-api-key-here'")
        return 1
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test with a simple API call
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        print("\n📡 Building YouTube API client...")
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        print("✅ API client built successfully")
        
        # Test with a well-known video (Rick Astley - Never Gonna Give You Up)
        test_video_id = "dQw4w9WgXcQ"
        
        print(f"\n🎬 Testing captions.list for video: {test_video_id}")
        
        captions_response = youtube.captions().list(
            part='snippet',
            videoId=test_video_id
        ).execute()
        
        print(f"✅ API call successful!")
        print(f"\n📊 Response:")
        print(f"   • Items found: {len(captions_response.get('items', []))}")
        
        if captions_response.get('items'):
            for item in captions_response['items']:
                snippet = item['snippet']
                print(f"   • Caption track: {snippet['language']} ({snippet['trackKind']})")
        else:
            print("   ⚠️  No captions found for this video")
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! YouTube Data API v3 is working!")
        print("\nYou can now proceed with TDD implementation.")
        return 0
        
    except ImportError:
        print("\n❌ google-api-python-client not installed")
        print("\nInstall with:")
        print("  pip install google-api-python-client")
        return 1
        
    except HttpError as e:
        print(f"\n❌ API Error: {e.status_code}")
        print(f"   Reason: {e.reason}")
        
        if e.status_code == 403:
            print("\n💡 Possible issues:")
            print("   • API key not enabled for YouTube Data API v3")
            print("   • API key restrictions blocking access")
            print("   • Quota exceeded")
        elif e.status_code == 400:
            print("\n💡 Possible issues:")
            print("   • Invalid API key format")
            print("   • API key restrictions")
        
        return 1
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}")
        print(f"   {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(test_api_key())
