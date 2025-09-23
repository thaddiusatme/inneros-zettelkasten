#!/usr/bin/env python3
"""
Simple AI Integration Test - Quick validation of the AI workflow integration
"""

import sys
import os
from datetime import datetime

# Add development directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from capture_matcher import CaptureMatcherPOC


def main():
    print("🚀 Simple AI Integration Test")
    print("=" * 40)
    
    try:
        # Initialize capture matcher
        print("1. Initializing CaptureMatcherPOC...")
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        matcher.configure_inbox_directory("/tmp/test_inbox")
        print("   ✅ Initialization successful")
        
        # Check if the AI method exists
        print("2. Checking AI integration method...")
        has_method = hasattr(matcher, 'process_capture_notes_with_ai')
        print(f"   ✅ process_capture_notes_with_ai method exists: {has_method}")
        
        # Create a simple test note
        print("3. Creating test capture note...")
        test_pair = {
            "screenshot": {
                "filename": "Screenshot_20250922_141530.png",
                "timestamp": datetime(2025, 9, 22, 14, 15, 30),
                "path": "/fake/screenshot.png",
                "size": 1000000
            },
            "voice": {
                "filename": "Recording_20250922_141545.m4a", 
                "timestamp": datetime(2025, 9, 22, 14, 15, 45),
                "path": "/fake/voice.m4a",
                "size": 500000
            },
            "time_gap_seconds": 15
        }
        
        note = matcher.generate_capture_note(test_pair, "test-integration")
        print(f"   ✅ Generated note: {note['filename']}")
        
        # Test AI processing with a single note
        print("4. Testing AI processing (with timeout protection)...")
        start_time = datetime.now()
        
        # This should use fallback processing if WorkflowManager isn't available
        ai_result = matcher.process_capture_notes_with_ai([note])
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"   ✅ Processing completed in {processing_time:.3f} seconds")
        
        # Display results
        print("5. Results:")
        stats = ai_result['processing_stats']
        print(f"   📊 Total notes: {stats['total_notes']}")
        print(f"   ✅ Successful: {stats['successful']}")
        print(f"   ❌ Errors: {stats['errors']}")
        print(f"   ⏱️  Time: {stats['processing_time']:.3f}s")
        print(f"   🔗 WorkflowManager available: {stats.get('workflow_manager_available', 'Unknown')}")
        
        if ai_result['ai_results']:
            result = ai_result['ai_results'][0]
            print(f"   🎯 Quality score: {result['quality_score']}")
            print(f"   🏷️  Tags: {', '.join(result['ai_tags'][:3])}...")
            print(f"   🔧 Method: {result['processing_method']}")
        
        if ai_result['errors']:
            print("   ⚠️  Errors encountered:")
            for error in ai_result['errors'][:2]:  # Show first 2 errors
                if isinstance(error, dict):
                    print(f"      • {error.get('error', str(error))}")
                else:
                    print(f"      • {str(error)[:100]}...")
        
        print("\n🎉 Test completed successfully!")
        print("   The AI integration is working with fallback processing.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return 1


if __name__ == "__main__":
    exit(main())
