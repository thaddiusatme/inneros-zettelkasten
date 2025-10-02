#!/usr/bin/env python3
"""
Samsung Screenshot Individual Processing - LIVE Demo

Creates individual capture notes directly in your actual knowledge base
so you can see the TDD Iteration 5 Individual Processing System results.

This will create real notes in: knowledge/Inbox/capture-YYYYMMDD-HHMM-*.md
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.evening_screenshot_processor import EveningScreenshotProcessor
from src.cli.individual_screenshot_utils import (
    ContextualFilenameGenerator,
    RichContextAnalyzer,
    TemplateNoteRenderer,
    IndividualProcessingOrchestrator,
    SmartLinkIntegrator
)

def find_recent_samsung_screenshots():
    """Find some recent Samsung screenshots for processing"""
    
    onedrive_path = Path.home() / "OneDrive" / "backlog" / "Pictures" / "Screenshots"
    
    if not onedrive_path.exists():
        print(f"❌ OneDrive path not found: {onedrive_path}")
        return [], None
    
    print(f"🔍 Searching for Samsung screenshots in: {onedrive_path}")
    
    # Find Samsung screenshots
    screenshot_files = list(onedrive_path.glob("Screenshot_*_*_*.jpg"))
    screenshot_files.extend(list(onedrive_path.glob("Screenshot_*_*_*.png")))
    
    # Sort by modification time (most recent first)
    screenshot_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    recent_screenshots = screenshot_files[:3]  # Take 3 most recent
    
    print(f"📊 Found {len(screenshot_files)} total Samsung screenshots")
    print(f"🎯 Selected {len(recent_screenshots)} most recent for processing:")
    
    for i, screenshot in enumerate(recent_screenshots, 1):
        mod_time = datetime.fromtimestamp(screenshot.stat().st_mtime)
        print(f"   {i}. {screenshot.name} (modified: {mod_time.strftime('%Y-%m-%d %H:%M')})")
    
    return recent_screenshots, str(onedrive_path)


def run_live_individual_processing():
    """Run individual processing that creates notes in your actual knowledge base"""
    
    # Use your actual knowledge base
    knowledge_path = Path(__file__).parent.parent.parent / "knowledge"
    
    print(f"🎯 Samsung Screenshot Individual Processing - LIVE Demo")
    print(f"📁 Target Knowledge Base: {knowledge_path}")
    print(f"📁 Notes will be created in: {knowledge_path / 'Inbox'}")
    
    # Find screenshots
    screenshots, onedrive_path = find_recent_samsung_screenshots()
    
    if not screenshots:
        print("❌ No Samsung screenshots found for processing")
        return
    
    # Initialize the processor
    processor = EveningScreenshotProcessor(onedrive_path, str(knowledge_path))
    
    print(f"\n🚀 Processing {len(screenshots)} screenshots with Individual Processing System...")
    
    # Count existing capture notes before processing
    inbox_path = knowledge_path / "Inbox"
    existing_captures = list(inbox_path.glob("capture-*.md"))
    print(f"📊 Existing capture notes: {len(existing_captures)}")
    
    start_time = time.time()
    
    try:
        # Use our TDD Iteration 5 individual processing
        result = processor.individual_orchestrator.process_screenshots_individually_optimized(screenshots)
        
        processing_time = time.time() - start_time
        
        print(f"\n✅ Individual Processing Complete!")
        print(f"   📊 Screenshots Processed: {result['total_processed']}")
        print(f"   📝 Individual Notes Created: {result['individual_notes_created']}")
        print(f"   ⏱️  Processing Time: {processing_time:.2f}s")
        print(f"   🚀 Screenshots/Second: {result['total_processed'] / processing_time:.2f}")
        
        # Show new capture notes
        new_captures = list(inbox_path.glob("capture-*.md"))
        newly_created = [note for note in new_captures if note not in existing_captures]
        
        print(f"\n📄 Newly Created Individual Notes ({len(newly_created)}):")
        for note in newly_created:
            print(f"   📝 {note.name}")
            
            # Show preview of each note
            with open(note, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Find title
                title_line = next((line for line in lines if line.startswith('#')), "No title")
                
                # Check structure
                has_yaml = content.startswith('---')
                has_screenshot_ref = '![' in content or 'Screenshot' in content
                has_device_info = 'Samsung Galaxy S23' in content
                
                print(f"      📖 {title_line}")
                print(f"      ✅ YAML: {has_yaml} | Screenshot: {has_screenshot_ref} | Device: {has_device_info}")
                print(f"      📊 Size: {len(content)} chars")
        
        # Show where to find them
        print(f"\n📁 You can now find your individual capture notes at:")
        print(f"   📂 {inbox_path}")
        
        # Offer to show content of one note
        if newly_created:
            show_content = input(f"\n👀 Show full content of {newly_created[0].name}? (y/N): ")
            if show_content.lower() == 'y':
                print(f"\n📄 Content of {newly_created[0].name}:")
                print("=" * 60)
                with open(newly_created[0], 'r') as f:
                    print(f.read())
                print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False


def analyze_individual_notes_in_inbox():
    """Analyze all capture notes in your Inbox to show the individual processing format"""
    
    knowledge_path = Path(__file__).parent.parent.parent / "knowledge"
    inbox_path = knowledge_path / "Inbox"
    
    capture_notes = list(inbox_path.glob("capture-*.md"))
    
    print(f"\n📊 Analysis of All Capture Notes in Inbox ({len(capture_notes)} total):")
    
    # Group by creation date
    by_date = {}
    for note in capture_notes:
        # Extract date from filename
        parts = note.name.split('-')
        if len(parts) >= 3:
            date_part = parts[1]  # YYYYMMDD
            if date_part not in by_date:
                by_date[date_part] = []
            by_date[date_part].append(note)
    
    for date, notes in sorted(by_date.items(), reverse=True):
        formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        print(f"\n📅 {formatted_date} ({len(notes)} notes):")
        
        for note in notes:
            # Quick analysis
            with open(note, 'r') as f:
                content = f.read()
            
            # Extract key info
            is_individual = 'individual-processing' in content
            has_device = 'Samsung Galaxy S23' in content
            size = len(content)
            
            status = "🆕 Individual" if is_individual else "📋 Other"
            device = "📱 S23" if has_device else "❓"
            
            print(f"   {status} {device} {note.name} ({size} chars)")


def main():
    """Main demo execution"""
    try:
        # Run the live individual processing
        success = run_live_individual_processing()
        
        if success:
            # Analyze all capture notes
            analyze_individual_notes_in_inbox()
            
            print(f"\n🎉 Live Demo Complete!")
            print(f"📁 Check your knowledge/Inbox/ folder for the new individual capture notes")
            print(f"🔍 Look for files matching: capture-YYYYMMDD-HHMM-*.md")
            
        else:
            print(f"\n❌ Demo failed - check error messages above")
            
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
