#!/usr/bin/env python3
"""
Clickable Links Capture Test - Generates capture notes with clickable file links
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

# Add development directory to path and force fallback mode
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Force fallback mode to avoid WorkflowManager hanging
import capture_matcher
capture_matcher.WorkflowManager = None

from capture_matcher import CaptureMatcherPOC


def create_clickable_file_link(file_path, link_text="Open File"):
    """Create a clickable file:// link with proper URL encoding"""
    # URL encode the path for special characters and spaces
    encoded_path = quote(file_path)
    return f"[{link_text}](file://{encoded_path})"


def create_finder_link(file_path, link_text="Show in Finder"):
    """Create a clickable link to show file in Finder"""
    # Get the directory path
    dir_path = str(Path(file_path).parent)
    encoded_dir = quote(dir_path)
    return f"[{link_text}](file://{encoded_dir}/)"


def create_enhanced_screenshot_section(screenshot_data):
    """Create screenshot section with clickable links"""
    file_path = screenshot_data.get('path', 'N/A')
    
    # Format file size
    size_bytes = screenshot_data.get('size', 0)
    if size_bytes >= 1024 * 1024:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes} bytes"
    
    # Create clickable links
    screenshot_link = create_clickable_file_link(file_path, "📸 Open Screenshot")
    finder_link = create_finder_link(file_path, "📂 Show in Finder")
    
    return f"""## Screenshot Reference

- **File**: {screenshot_data['filename']}
- **Size**: {size_str}
- **Timestamp**: {screenshot_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
- **Path**: `{file_path}`
- **Actions**: {screenshot_link} | {finder_link}"""


def create_enhanced_voice_section(voice_data, is_real=True):
    """Create voice section with clickable links (if real voice note)"""
    if not is_real:
        return """## Voice Note Reference

- **Status**: No matching voice note found within 2-minute window
- **Note**: Voice notes must be recorded within 2 minutes of screenshot for automatic pairing"""
    
    file_path = voice_data.get('path', 'N/A')
    
    # Format file size
    size_bytes = voice_data.get('size', 0)
    if size_bytes >= 1024 * 1024:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes} bytes"
    
    # Create clickable links
    voice_link = create_clickable_file_link(file_path, "🎤 Play Voice Note")
    finder_link = create_finder_link(file_path, "📂 Show in Finder")
    
    return f"""## Voice Note Reference

- **File**: {voice_data['filename']}
- **Size**: {size_str}
- **Timestamp**: {voice_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
- **Path**: `{file_path}`
- **Actions**: {voice_link} | {finder_link}"""


def create_enhanced_capture_note(matcher, screenshot_data, voice_data=None, description="screenshot-capture"):
    """Create a capture note with clickable file links"""
    
    # Generate filename based on screenshot timestamp
    timestamp = screenshot_data['timestamp']
    date_str = timestamp.strftime("%Y%m%d-%H%M")
    clean_desc = description.replace(' ', '-').lower()
    filename = f"capture-{date_str}-{clean_desc}.md"
    
    # Create file path
    inbox_dir = matcher.inbox_dir if matcher.inbox_dir else '/tmp/capture_test'
    file_path = f"{inbox_dir}/{filename}"
    
    # YAML frontmatter
    yaml_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
    capture_type = "paired" if voice_data else "screenshot_only"
    
    yaml_frontmatter = f"""---
type: fleeting
created: {yaml_timestamp}
status: inbox
tags:
  - capture
  - samsung-s23
  - {capture_type}
source: capture
device: Samsung S23
capture_type: {capture_type}"""
    
    if voice_data:
        time_gap = abs((voice_data['timestamp'] - screenshot_data['timestamp']).total_seconds())
        yaml_frontmatter += f"\ntime_gap_seconds: {int(time_gap)}"
    
    yaml_frontmatter += "\n---"
    
    # Create enhanced sections with clickable links
    screenshot_section = create_enhanced_screenshot_section(screenshot_data)
    voice_section = create_enhanced_voice_section(voice_data, is_real=voice_data is not None)
    
    # Metadata section
    metadata_section = f"""## Capture Metadata

- **Device**: Samsung S23 (detected from filename patterns)
- **Capture Session**: {timestamp.strftime('%Y-%m-%d %H:%M')}
- **Capture Type**: {'Screenshot + Voice Note' if voice_data else 'Screenshot only (no matching voice note within 2-minute window)'}"""
    
    if voice_data:
        time_gap = abs((voice_data['timestamp'] - screenshot_data['timestamp']).total_seconds())
        metadata_section += f"\n- **Time Gap**: {int(time_gap)} seconds between screenshot and voice note"
    
    # Processing section
    processing_section = """## Processing Notes

*Add your analysis, insights, and connections here*

### Content Analysis Checklist
- [ ] Review screenshot content and extract key information
- [ ] Listen to voice note (if available) and transcribe key points
- [ ] Identify main topic or theme
- [ ] Add relevant tags based on content
- [ ] Link to related notes in your knowledge base
- [ ] Consider if this should be expanded into a permanent note

### Context Questions
- What was the context when you took this screenshot?
- What insights or ideas does this capture represent?
- How does this connect to your current projects or interests?
- What action items or follow-ups are needed?"""
    
    # Combine all sections
    content_title = "# Screenshot + Voice Capture" if voice_data else "# Screenshot Capture"
    content_subtitle = "Knowledge capture from Samsung S23 screenshot and voice note pair." if voice_data else "Knowledge capture from Samsung S23 screenshot."
    
    markdown_content = f"""{yaml_frontmatter}
{content_title}

{content_subtitle}

{screenshot_section}

{voice_section}

{metadata_section}

{processing_section}

"""
    
    return {
        'markdown_content': markdown_content,
        'filename': filename,
        'file_path': file_path
    }


def main():
    print("🚀 **CLICKABLE LINKS CAPTURE TEST**")
    print("=" * 45)
    print("   Generate capture notes with clickable file links")
    
    try:
        # Initialize with your real OneDrive paths
        print("\n1. 🔧 Setting up enhanced capture processing...")
        matcher = CaptureMatcherPOC.create_with_onedrive_defaults()
        matcher.match_threshold = 120  # 2 minutes
        
        inbox_path = "/Users/thaddius/repos/inneros-zettelkasten/knowledge/Inbox"
        matcher.configure_inbox_directory(inbox_path)
        print("   ✅ Configured with clickable link generation")
        
        # Scan your real captures
        print("\n2. 📱 Scanning your recent captures...")
        scan_result = matcher.scan_onedrive_captures(days_back=7)
        
        screenshots = scan_result["screenshots"]
        voice_notes = scan_result["voice_notes"]
        
        print(f"   📊 Found: {len(screenshots)} screenshots, {len(voice_notes)} voice notes")
        
        if not screenshots:
            print("   📝 No screenshots found!")
            return 0
        
        # Use your latest screenshot
        latest_screenshot = screenshots[0]
        print(f"\n3. 📸 Processing screenshot with clickable links:")
        print(f"   📄 File: {latest_screenshot['filename']}")
        print(f"   📂 Path: {latest_screenshot['path'][:60]}...")
        
        # Check for matching voice note
        matching_voice = None
        for voice in voice_notes:
            time_diff = abs((voice['timestamp'] - latest_screenshot['timestamp']).total_seconds())
            if time_diff <= 120:  # 2 minutes
                matching_voice = voice
                print(f"   🎤 Found matching voice: {voice['filename']} ({int(time_diff)}s gap)")
                break
        
        if not matching_voice:
            print("   📝 No matching voice note (processing as screenshot-only)")
        
        # Create enhanced capture note
        print("\n4. 📝 Generating enhanced capture note with clickable links...")
        capture_note = create_enhanced_capture_note(
            matcher, 
            latest_screenshot, 
            matching_voice, 
            "enhanced-with-links"
        )
        
        print(f"   ✅ Generated: {capture_note['filename']}")
        
        # Process with AI integration
        print("\n5. 🤖 Processing with AI integration...")
        ai_result = matcher.process_capture_notes_with_ai([capture_note])
        
        ai_data = ai_result['ai_results'][0] if ai_result['ai_results'] else {}
        print(f"   ✅ AI processed with quality score: {ai_data.get('quality_score', 'N/A')}")
        
        # Save with AI enhancements
        print("\n6. 💾 **SAVING ENHANCED CAPTURE NOTE**")
        
        # Add AI metadata to YAML
        content = capture_note['markdown_content']
        lines = content.split('\n')
        yaml_end = -1
        for i, line in enumerate(lines):
            if line.strip() == '---' and i > 0:
                yaml_end = i
                break
        
        if yaml_end > 0 and ai_data:
            ai_metadata = [
                f"ai_quality_score: {ai_data.get('quality_score', 'N/A')}",
                f"ai_processing_method: {ai_data.get('processing_method', 'unknown')}",
                f"ai_processed_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "ai_tags:",
            ]
            
            for tag in ai_data.get('ai_tags', []):
                ai_metadata.append(f"  - {tag}")
            
            enhanced_lines = lines[:yaml_end] + ai_metadata + lines[yaml_end:]
            content = '\n'.join(enhanced_lines)
            
            # Add AI recommendations
            content += "\n## AI Enhancement Suggestions\n\n"
            for i, rec in enumerate(ai_data.get('recommendations', []), 1):
                content += f"{i}. {rec}\n"
        
        # Save to file
        Path(capture_note['file_path']).parent.mkdir(parents=True, exist_ok=True)
        with open(capture_note['file_path'], 'w', encoding='utf-8') as f:
            f.write(content)
        
        saved_path = capture_note['file_path']
        print(f"   ✅ Saved to: {saved_path}")
        
        # Show clickable links preview
        print("\n7. 🔗 **CLICKABLE LINKS PREVIEW**")
        
        screenshot_link = create_clickable_file_link(latest_screenshot['path'], "📸 Open Screenshot")
        finder_link = create_finder_link(latest_screenshot['path'], "📂 Show in Finder")
        
        print(f"   🔗 Screenshot links generated:")
        print(f"      • {screenshot_link}")
        print(f"      • {finder_link}")
        
        if matching_voice:
            voice_link = create_clickable_file_link(matching_voice['path'], "🎤 Play Voice Note")
            print(f"   🔗 Voice note links generated:")
            print(f"      • {voice_link}")
        
        file_size = Path(saved_path).stat().st_size
        print(f"\n   📏 File size: {file_size} bytes")
        
        print("\n🎉 **CLICKABLE LINKS SUCCESS!**")
        print("=" * 45)
        print("✅ **Your capture note now has clickable file links!**")
        print()
        print("🔗 **How to use the links:**")
        print("   • Click '📸 Open Screenshot' to view the image")
        print("   • Click '📂 Show in Finder' to see the file location")
        print("   • Click '🎤 Play Voice Note' to hear audio (if available)")
        print()
        print("📋 **Link formats used:**")
        print("   • file://path/to/file - Opens in default app")
        print("   • file://path/to/folder/ - Opens folder in Finder")
        print("   • URL encoding handles spaces and special characters")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ **Test failed**: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Details: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit(main())
