#!/usr/bin/env python3
"""
Llama Vision Capture Test - Enhanced screenshot processing with content analysis

This demonstrates the Llama 3.2 Vision integration for screenshot OCR and content understanding.
Tests both the vision analysis and the enhanced note generation.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add development directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Force fallback mode for testing without full AI setup
import capture_matcher
capture_matcher.WorkflowManager = None

from capture_matcher import CaptureMatcherPOC


def test_vision_integration():
    """Test Llama Vision integration with existing screenshots"""
    
    print("🚀 **LLAMA VISION CAPTURE TEST**")
    print("=" * 60)
    print("   Screenshot OCR and content analysis with Llama 3.2 Vision")
    print()
    
    # Initialize capture matcher with vision enabled
    print("1. 🔧 Initializing Capture Matcher with Llama Vision...")
    try:
        matcher = CaptureMatcherPOC.create_with_onedrive_defaults()
        matcher.configure_inbox_directory("/Users/thaddius/repos/inneros-zettelkasten/knowledge/Inbox")
        
        if matcher.enable_vision:
            print("   ✅ Llama Vision OCR enabled and ready")
        else:
            print("   ⚠️  Llama Vision OCR not available - will demonstrate structure")
    
    except Exception as e:
        print(f"   ❌ Setup failed: {e}")
        return
    
    # Scan for screenshots
    print("\n2. 📱 Scanning for Samsung S23 screenshots...")
    try:
        captures = matcher.scan_onedrive_captures(days_back=7)
        screenshots = captures['screenshots']
        voice_notes = captures['voice_notes']
        
        print(f"   📊 Found: {len(screenshots)} screenshots, {len(voice_notes)} voice notes")
        
        if not screenshots:
            print("   ⚠️  No screenshots found - check OneDrive sync")
            return
            
    except Exception as e:
        print(f"   ❌ Scanning failed: {e}")
        return
    
    # Test vision analysis on latest screenshot
    print("\n3. 🤖 Testing Llama Vision Analysis...")
    latest_screenshot = screenshots[0]  # Most recent
    
    print(f"   📄 Analyzing: {latest_screenshot['filename']}")
    print(f"   📏 Size: {latest_screenshot['size']} bytes")
    print(f"   📅 Timestamp: {latest_screenshot['timestamp']}")
    
    # Get full screenshot path
    screenshot_path = Path(latest_screenshot['path'])
    
    try:
        # Analyze with vision
        vision_result = matcher.analyze_screenshot_with_vision(screenshot_path)
        
        if vision_result:
            print("\n   ✅ **VISION ANALYSIS SUCCESS!**")
            print(f"   📝 Extracted Text: {vision_result['extracted_text'][:100]}...")
            print(f"   📊 Content Type: {vision_result['content_type']}")
            print(f"   🎯 Topics: {vision_result['main_topics']}")
            print(f"   💡 Key Insights: {vision_result['key_insights'][:2]}")  # First 2 insights
            print(f"   🔗 Suggested Connections: {vision_result['suggested_connections']}")
            print(f"   📈 Confidence: {vision_result['confidence_score']:.2f}")
            print(f"   ⏱️  Processing Time: {vision_result['processing_time']:.2f}s")
        else:
            print("   ⚠️  Vision analysis not available or failed")
            print("   📝 Will use standard metadata-only template")
            vision_result = None
            
    except Exception as e:
        print(f"   ❌ Vision analysis error: {e}")
        vision_result = None
    
    # Generate enhanced note with vision data
    print("\n4. 📝 Generating Vision-Enhanced Note...")
    
    try:
        # Create note data structure
        note_data = {
            "screenshot_filename": latest_screenshot['filename'],
            "screenshot_size": f"{latest_screenshot['size'] / 1024:.1f} KB",
            "screenshot_timestamp": latest_screenshot['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
            "screenshot_path": latest_screenshot['path'],
            "capture_session": latest_screenshot['timestamp'].strftime("%Y-%m-%d %H:%M"),
            "capture_type": "screenshot_with_vision" if vision_result else "screenshot_only"
        }
        
        # Add vision analysis data if available
        if vision_result:
            note_data.update({
                "content_summary": vision_result['content_summary'],
                "extracted_text": vision_result['extracted_text'],
                "main_topics_list": "\n".join(f"- {topic}" for topic in vision_result['main_topics']),
                "key_insights_list": "\n".join(f"- {insight}" for insight in vision_result['key_insights']),
                "suggested_connections_list": "\n".join(f"- [[{conn}]]" for conn in vision_result['suggested_connections']) or "- No specific connections suggested",
                "content_type": vision_result['content_type'],
                "confidence_score": f"{vision_result['confidence_score']:.2f}",
                "processing_time": f"{vision_result['processing_time']:.2f}"
            })
            
            # Use vision-enhanced template
            markdown_content = matcher.VISION_ENHANCED_TEMPLATE.format(**note_data)
            template_type = "Vision-Enhanced"
        else:
            # Use fallback template with placeholders
            note_data.update({
                "content_summary": "Vision analysis not available",
                "extracted_text": "[OCR extraction would appear here]",
                "main_topics_list": "- manual-review-needed",
                "key_insights_list": "- Review screenshot manually for insights",
                "suggested_connections_list": "- No automated connections available",
                "content_type": "unknown",
                "confidence_score": "0.00",
                "processing_time": "0.00"
            })
            
            markdown_content = matcher.VISION_ENHANCED_TEMPLATE.format(**note_data)
            template_type = "Standard (Vision Unavailable)"
        
        # Generate filename
        timestamp_str = latest_screenshot['timestamp'].strftime("%Y%m%d-%H%M")
        filename = f"capture-{timestamp_str}-llama-vision-test.md"
        
        # Save note
        note_path = Path(matcher.inbox_dir) / filename
        with open(note_path, 'w') as f:
            # Add YAML frontmatter
            yaml_content = f"""---
type: fleeting
created: {latest_screenshot['timestamp'].strftime("%Y-%m-%d %H:%M")}
status: inbox
tags:
  - capture
  - samsung-s3
  - llama-vision
source: capture
device: Samsung S23
capture_type: vision_enhanced
ai_quality_score: {vision_result['confidence_score'] if vision_result else 0.5}
ai_processing_method: llama-vision
ai_processed_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
ai_tags:
{("".join(f"  - {tag}" + chr(10) for tag in vision_result['main_topics']) if vision_result else "  - screenshot" + chr(10) + "  - manual-review-needed" + chr(10))}---

{markdown_content}"""
            
            f.write(yaml_content)
        
        print(f"   ✅ Generated: {filename}")
        print(f"   📂 Location: {note_path}")
        print(f"   📋 Template: {template_type}")
        print(f"   📏 File size: {note_path.stat().st_size} bytes")
        
    except Exception as e:
        print(f"   ❌ Note generation failed: {e}")
        return
    
    # Display preview
    print("\n5. 📄 **VISION-ENHANCED NOTE PREVIEW**")
    print("-" * 50)
    
    try:
        with open(note_path, 'r') as f:
            lines = f.readlines()
            
        # Show first 25 lines
        for i, line in enumerate(lines[:25], 1):
            print(f"   {i:2d}: {line.rstrip()}")
        
        if len(lines) > 25:
            print(f"   ... ({len(lines) - 25} more lines)")
            
        print(f"\n   📊 Total lines: {len(lines)}")
        
    except Exception as e:
        print(f"   ❌ Preview failed: {e}")
    
    # Summary
    print("\n🎉 **LLAMA VISION INTEGRATION TEST COMPLETE!**")
    print("=" * 60)
    print("✅ **What this demonstrates:**")
    if vision_result:
        print("   • ✅ Llama Vision OCR successfully extracts text from screenshots")
        print("   • ✅ AI content analysis identifies topics and insights")  
        print("   • ✅ Automated connection suggestions for knowledge linking")
        print("   • ✅ Enhanced note template includes all vision analysis")
        print("   • ✅ Integration with existing Samsung S23 capture workflow")
        
        print(f"\n🔥 **Performance:**")
        print(f"   • Processing time: {vision_result['processing_time']:.2f} seconds")
        print(f"   • Confidence score: {vision_result['confidence_score']:.2f}/1.0")
        print(f"   • Topics extracted: {len(vision_result['main_topics'])}")
        print(f"   • Insights generated: {len(vision_result['key_insights'])}")
    else:
        print("   • ⚠️  Llama Vision not available but template structure ready")
        print("   • ✅ Fallback handling works properly")
        print("   • ✅ Standard capture workflow preserved")
        
    print(f"\n🔄 **Your enhanced workflow:**")
    print(f"   1. 📱 Take screenshot on Samsung S23")
    print(f"   2. ☁️  OneDrive syncs automatically")  
    print(f"   3. 🤖 Run capture system with Llama Vision analysis")
    print(f"   4. 📝 Review AI-extracted content and insights")
    print(f"   5. 🔗 Follow connection suggestions to link notes")
    print(f"   6. 📊 Weekly review suggests promotion based on quality")


if __name__ == "__main__":
    test_vision_integration()
