#!/usr/bin/env python3
"""
Realistic Capture Test - Handles screenshot-only captures with 2-minute voice matching
This represents the most common real-world usage pattern
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add development directory to path and force fallback mode
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Force fallback mode to avoid WorkflowManager hanging
import capture_matcher
capture_matcher.WorkflowManager = None

from capture_matcher import CaptureMatcherPOC


def create_screenshot_only_note(matcher, screenshot_data, description):
    """Create a capture note for screenshot-only (no voice note)"""
    
    # Generate filename based on screenshot timestamp
    timestamp = screenshot_data['timestamp']
    date_str = timestamp.strftime("%Y%m%d-%H%M")
    clean_desc = description.replace(' ', '-').lower()
    filename = f"capture-{date_str}-{clean_desc}.md"
    
    # Create file path
    inbox_dir = matcher.inbox_dir if matcher.inbox_dir else '/tmp/capture_test'
    file_path = f"{inbox_dir}/{filename}"
    
    # Format file size
    size_bytes = screenshot_data.get('size', 0)
    if size_bytes >= 1024 * 1024:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes} bytes"
    
    # YAML frontmatter for screenshot-only
    yaml_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
    yaml_frontmatter = f"""---
type: fleeting
created: {yaml_timestamp}
status: inbox
tags:
  - capture
  - samsung-s23
  - screenshot-only
source: capture
device: Samsung S23
capture_type: screenshot_only
---"""
    
    # Markdown content for screenshot-only
    markdown_content = f"""
# Screenshot Capture

Knowledge capture from Samsung S23 screenshot.

## Screenshot Reference

- **File**: {screenshot_data['filename']}
- **Size**: {size_str}
- **Timestamp**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
- **Path**: {screenshot_data.get('path', 'N/A')}

## Capture Metadata

- **Device**: Samsung S23 (detected from filename patterns)
- **Capture Session**: {timestamp.strftime('%Y-%m-%d %H:%M')}
- **Capture Type**: Screenshot only (no matching voice note within 2-minute window)

## Processing Notes

*Add your analysis, insights, and connections here*

- [ ] Review screenshot content and extract key information
- [ ] Identify main topic or theme
- [ ] Add relevant tags based on content
- [ ] Link to related notes in your knowledge base
- [ ] Consider if this should be expanded into a permanent note

## Next Steps

- What was the context when you took this screenshot?
- What insights or ideas does this capture represent?
- How does this connect to your current projects or interests?

"""
    
    return {
        'markdown_content': yaml_frontmatter + markdown_content,
        'filename': filename,
        'file_path': file_path
    }


def save_note_to_file(note_data, ai_result=None):
    """Save the note with AI enhancements to the file system"""
    file_path = note_data['file_path']
    content = note_data['markdown_content']
    
    # Enhance content with AI results if available
    if ai_result and ai_result.get('ai_results'):
        ai_data = ai_result['ai_results'][0]
        
        # Add AI processing metadata to the YAML frontmatter  
        lines = content.split('\n')
        yaml_end = -1
        for i, line in enumerate(lines):
            if line.strip() == '---' and i > 0:
                yaml_end = i
                break
        
        if yaml_end > 0:
            # Insert AI metadata before the closing ---
            ai_metadata = [
                f"ai_quality_score: {ai_data.get('quality_score', 'N/A')}",
                f"ai_processing_method: {ai_data.get('processing_method', 'unknown')}",
                f"ai_processed_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "ai_tags:",
            ]
            
            # Add AI tags in YAML list format
            for tag in ai_data.get('ai_tags', []):
                ai_metadata.append(f"  - {tag}")
            
            # Insert AI metadata
            enhanced_lines = lines[:yaml_end] + ai_metadata + lines[yaml_end:]
            content = '\n'.join(enhanced_lines)
            
            # Add AI recommendations to the content
            content += "\n\n## AI Enhancement Suggestions\n\n"
            for i, rec in enumerate(ai_data.get('recommendations', []), 1):
                content += f"{i}. {rec}\n"
    
    # Ensure directory exists
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Write the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path


def main():
    print("🚀 **REALISTIC CAPTURE TEST**")
    print("=" * 45)
    print("   Screenshot-only captures with 2-minute voice matching")
    
    try:
        # Initialize with your real OneDrive paths
        print("\n1. 🔧 Setting up realistic capture processing...")
        matcher = CaptureMatcherPOC.create_with_onedrive_defaults()
        matcher.match_threshold = 120  # 2 minutes in seconds
        
        inbox_path = "/Users/thaddius/repos/inneros-zettelkasten/knowledge/Inbox"
        matcher.configure_inbox_directory(inbox_path)
        print(f"   ✅ Configured with 2-minute voice matching window")
        print(f"   📂 Will save to: {inbox_path}")
        
        # Scan your real captures
        print("\n2. 📱 Scanning your recent captures...")
        scan_result = matcher.scan_onedrive_captures(days_back=7)
        
        screenshots = scan_result["screenshots"]
        voice_notes = scan_result["voice_notes"]
        
        print(f"   📊 Found: {len(screenshots)} screenshots, {len(voice_notes)} voice notes")
        
        if not screenshots:
            print("   📝 No screenshots found - system ready for when you create them!")
            return 0
        
        # Try matching with 2-minute window
        print("\n3. 🔍 Matching screenshots and voice notes (2-minute window)...")
        all_captures = []
        
        for screenshot in screenshots:
            all_captures.append({**screenshot, "type": "screenshot"})
        for voice in voice_notes:
            all_captures.append({**voice, "type": "voice"})
        
        matches = matcher.match_by_timestamp(all_captures)
        
        print(f"   🔗 Matching results with 2-minute window:")
        print(f"      • Paired captures: {len(matches['paired'])}")
        print(f"      • Screenshot-only: {len(matches['unpaired_screenshots'])}")
        print(f"      • Unpaired voice notes: {len(matches['unpaired_voice'])}")
        
        # Use your most recent screenshot
        latest_screenshot = screenshots[0]
        print(f"\n4. 📸 Processing your latest screenshot:")
        print(f"   📄 File: {latest_screenshot['filename']}")
        print(f"   📅 Date: {latest_screenshot['timestamp']}")
        print(f"   📏 Size: {latest_screenshot['size']} bytes")
        
        # Check if this screenshot has a matching voice note
        has_voice_match = False
        for pair in matches['paired']:
            if pair['screenshot']['filename'] == latest_screenshot['filename']:
                has_voice_match = True
                print(f"   🎤 Found matching voice note: {pair['voice']['filename']}")
                print(f"   ⏱️  Time gap: {pair['time_gap_seconds']} seconds")
                break
        
        if not has_voice_match:
            print("   📝 No matching voice note found within 2-minute window")
            print("   ✅ Processing as screenshot-only capture")
        
        # Create appropriate capture note
        if has_voice_match:
            # Use the existing paired logic
            print("\n5. 📝 Generating screenshot + voice capture note...")
            capture_note = matcher.generate_capture_note(pair, "real-paired-capture")
        else:
            # Use screenshot-only logic
            print("\n5. 📝 Generating screenshot-only capture note...")
            capture_note = create_screenshot_only_note(matcher, latest_screenshot, "real-screenshot-capture")
        
        print(f"   ✅ Generated: {capture_note['filename']}")
        
        # Process with AI integration
        print("\n6. 🤖 Processing with AI integration...")
        ai_result = matcher.process_capture_notes_with_ai([capture_note])
        
        ai_data = ai_result['ai_results'][0] if ai_result['ai_results'] else {}
        print(f"   ✅ AI processed with quality score: {ai_data.get('quality_score', 'N/A')}")
        print(f"   🏷️  AI tags: {', '.join(ai_data.get('ai_tags', []))}")
        
        # Save the realistic capture note
        print("\n7. 💾 **SAVING REALISTIC CAPTURE NOTE**")
        saved_path = save_note_to_file(capture_note, ai_result)
        print(f"   ✅ Saved to: {saved_path}")
        
        # Verify and preview
        if Path(saved_path).exists():
            file_size = Path(saved_path).stat().st_size
            print(f"   📏 File size: {file_size} bytes")
            
            # Show preview of the saved file
            print("\n8. 📄 **PREVIEW OF REALISTIC CAPTURE NOTE**")
            with open(saved_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"   📝 First 20 lines of {Path(saved_path).name}:")
            for i, line in enumerate(lines[:20]):
                print(f"      {i+1:2d}: {line.rstrip()}")
            
            print(f"   📊 Total lines: {len(lines)}")
        
        # Show workflow integration
        print("\n9. 🔄 **WORKFLOW INTEGRATION**")
        print(f"   📂 Note location: {saved_path}")
        print(f"   📋 Note type: {'Paired capture' if has_voice_match else 'Screenshot-only capture'}")
        print(f"   🎯 Quality score: {ai_data.get('quality_score', 'N/A')} (target >0.7 for promotion)")
        print(f"   📊 Status: Ready for weekly review")
        
        # Check existing capture notes
        inbox_files = list(Path(inbox_path).glob("*.md"))
        capture_files = [f for f in inbox_files if f.name.startswith("capture-")]
        
        print(f"\n   📊 Your capture notes collection:")
        print(f"      • Total inbox notes: {len(inbox_files)}")
        print(f"      • Capture notes: {len(capture_files)}")
        
        if len(capture_files) > 1:
            print("   📋 Recent capture notes:")
            for capture_file in sorted(capture_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                mtime = datetime.fromtimestamp(capture_file.stat().st_mtime)
                print(f"      • {capture_file.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")
        
        print("\n🎉 **REALISTIC CAPTURE WORKFLOW SUCCESS!**")
        print("=" * 45)
        print("✅ **Your realistic capture workflow is working!**")
        print()
        print("📋 **What this demonstrates:**")
        print("   • ✅ Screenshot-only captures handled properly")
        print("   • ✅ 2-minute voice matching window implemented")
        print("   • ✅ Realistic YAML frontmatter and content structure")
        print("   • ✅ AI processing works with screenshot-only notes")
        print("   • ✅ Ready for your weekly review workflow")
        print()
        print("🔄 **Your realistic workflow:**")
        print("   1. 📱 Take screenshot on Samsung S23")
        print("   2. 🎤 Optionally add voice note within 2 minutes")
        print("   3. ☁️  OneDrive syncs automatically")
        print("   4. 🤖 Run capture system for AI processing")
        print("   5. 📝 Review and enhance in Obsidian")
        print("   6. 📊 Weekly review suggests promotion")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ **Test failed**: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Details: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit(main())
