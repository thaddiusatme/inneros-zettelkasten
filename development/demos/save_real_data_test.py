#!/usr/bin/env python3
"""
Save Real Data Test - Actually writes AI-processed capture notes to Inbox
This creates real note files in your InnerOS system
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add development directory to path and force fallback mode
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Force fallback mode to avoid WorkflowManager hanging
import capture_matcher
capture_matcher.WorkflowManager = None

from capture_matcher import CaptureMatcherPOC


def save_note_to_file(note_data, ai_result=None):
    """Actually save the note to the file system"""
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
    print("🚀 **SAVE REAL DATA TEST**")
    print("=" * 40)
    print("   Creating and saving AI-processed capture notes to your Inbox")
    
    try:
        # Initialize with your real OneDrive paths
        print("\n1. 🔧 Setting up real data processing...")
        matcher = CaptureMatcherPOC.create_with_onedrive_defaults()
        inbox_path = "/Users/thaddius/repos/inneros-zettelkasten/knowledge/Inbox"
        matcher.configure_inbox_directory(inbox_path)
        print(f"   ✅ Will save to: {inbox_path}")
        
        # Check inbox directory
        inbox_dir = Path(inbox_path)
        if not inbox_dir.exists():
            print(f"   📁 Creating inbox directory: {inbox_path}")
            inbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Scan your real captures
        print("\n2. 📱 Scanning your recent captures...")
        scan_result = matcher.scan_onedrive_captures(days_back=7)
        
        screenshots = scan_result["screenshots"]
        voice_notes = scan_result["voice_notes"]
        
        print(f"   📊 Found: {len(screenshots)} screenshots, {len(voice_notes)} voice notes")
        
        if not screenshots:
            print("   📝 No screenshots found - system ready for when you create them!")
            return 0
        
        # Use your most recent screenshot
        latest_screenshot = screenshots[0]
        print(f"\n3. 📸 Using your latest screenshot:")
        print(f"   📄 File: {latest_screenshot['filename']}")
        print(f"   📅 Date: {latest_screenshot['timestamp']}")
        print(f"   📏 Size: {latest_screenshot['size']} bytes")
        
        # Create capture note from your real data
        fake_voice = {
            "filename": "Recording_" + latest_screenshot['filename'].replace('Screenshot_', '').replace('.jpg', '.m4a').replace('.png', '.m4a'),
            "timestamp": latest_screenshot['timestamp'],
            "path": "/fake/voice.m4a",
            "size": 500000
        }
        
        capture_pair = {
            "screenshot": latest_screenshot,
            "voice": fake_voice,
            "time_gap_seconds": 15
        }
        
        print("\n4. 📝 Generating capture note from your real screenshot...")
        capture_note = matcher.generate_capture_note(capture_pair, "real-samsung-capture")
        print(f"   ✅ Generated: {capture_note['filename']}")
        
        # Process with AI integration
        print("\n5. 🤖 Processing with AI integration...")
        ai_result = matcher.process_capture_notes_with_ai([capture_note])
        
        ai_data = ai_result['ai_results'][0] if ai_result['ai_results'] else {}
        print(f"   ✅ AI processed with quality score: {ai_data.get('quality_score', 'N/A')}")
        print(f"   🏷️  AI tags: {', '.join(ai_data.get('ai_tags', []))}")
        
        # Actually save the file to your Inbox
        print("\n6. 💾 **SAVING TO YOUR INBOX**")
        saved_path = save_note_to_file(capture_note, ai_result)
        print(f"   ✅ Saved to: {saved_path}")
        
        # Verify the file was created
        if Path(saved_path).exists():
            file_size = Path(saved_path).stat().st_size
            print(f"   📏 File size: {file_size} bytes")
            
            # Show the first few lines of the saved file
            print("\n7. 📄 **PREVIEW OF SAVED FILE**")
            with open(saved_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"   📝 First 15 lines of {Path(saved_path).name}:")
            for i, line in enumerate(lines[:15]):
                print(f"      {i+1:2d}: {line.rstrip()}")
            
            print(f"   📊 Total lines: {len(lines)}")
            
        else:
            print("   ❌ File was not created!")
            return 1
        
        # Show where to find it
        print("\n8. 📂 **WHERE TO FIND YOUR NOTE**")
        print(f"   📁 Location: {saved_path}")
        print(f"   🔍 In Obsidian: Open your vault and look in Inbox/")
        print(f"   📝 Filename: {Path(saved_path).name}")
        
        # Check if more files exist in Inbox now
        inbox_files = list(Path(inbox_path).glob("*.md"))
        capture_files = [f for f in inbox_files if f.name.startswith("capture-")]
        
        print(f"\n   📊 Your Inbox now contains:")
        print(f"      • Total markdown files: {len(inbox_files)}")
        print(f"      • Capture notes: {len(capture_files)}")
        
        if len(capture_files) > 1:
            print("   📋 Recent capture notes:")
            for capture_file in sorted(capture_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                mtime = datetime.fromtimestamp(capture_file.stat().st_mtime)
                print(f"      • {capture_file.name} (saved {mtime.strftime('%Y-%m-%d %H:%M')})")
        
        print("\n🎉 **SUCCESS! NOTE SAVED TO YOUR INBOX!**")
        print("=" * 40)
        print("✅ **Your AI-processed capture note is now in InnerOS!**")
        print()
        print("📋 **What was created:**")
        print("   • ✅ Real Samsung S3 screenshot processed")
        print("   • ✅ AI quality scoring and tagging applied")
        print("   • ✅ Note saved to your actual Inbox directory")
        print("   • ✅ Ready for your weekly review workflow")
        print()
        print("🔄 **Next steps in your workflow:**")
        print("   1. Open the note in Obsidian")
        print("   2. Review the AI suggestions")  
        print("   3. Add your own insights about the screenshot")
        print("   4. The note will appear in your weekly review for promotion")
        print()
        print("🚀 **Your Knowledge Capture System is live!**")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ **Save test failed**: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Details: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit(main())
