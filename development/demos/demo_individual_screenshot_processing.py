#!/usr/bin/env python3
"""
Demo: Individual Screenshot Processing with Real Data

Tests TDD Iteration 8 implementation with actual Samsung S23 screenshots
from OneDrive, demonstrating individual file generation vs daily note batch.
"""

import sys
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.screenshot_processor import ScreenshotProcessor


def main():
    """Demonstrate individual screenshot processing with real data"""
    
    # Configuration
    onedrive_base = Path.home() / "Library/CloudStorage/OneDrive-Personal"
    onedrive_screenshots = onedrive_base / "backlog/Pictures/Samsung Gallery/DCIM/Screenshots"
    knowledge_base = Path(__file__).parent.parent.parent / "knowledge"
    
    print("=" * 80)
    print("🧪 TDD ITERATION 8: Individual Screenshot Processing Demo")
    print("=" * 80)
    
    # Check OneDrive path
    if not onedrive_screenshots.exists():
        print(f"\n❌ OneDrive screenshots directory not found:")
        print(f"   Expected: {onedrive_screenshots}")
        print(f"\n💡 Attempting alternate paths...")
        
        # Try alternate OneDrive paths
        alternate_paths = [
            Path.home() / "OneDrive/Pictures/Screenshots",
            Path.home() / "OneDrive/Screenshots",
            Path.home() / "Pictures/Screenshots",
        ]
        
        for alt_path in alternate_paths:
            if alt_path.exists():
                onedrive_screenshots = alt_path
                print(f"   ✅ Found: {onedrive_screenshots}")
                break
        else:
            print(f"\n❌ Could not find OneDrive screenshots directory")
            print(f"\n📋 Please update the path in this script:")
            print(f"   Edit: {__file__}")
            print(f"   Line: onedrive_screenshots = Path('your/path/here')")
            return
    
    print(f"\n📁 Configuration:")
    print(f"   OneDrive: {onedrive_screenshots}")
    print(f"   Knowledge: {knowledge_base}")
    
    # Initialize processor
    try:
        processor = ScreenshotProcessor(
            onedrive_path=str(onedrive_screenshots),
            knowledge_path=str(knowledge_base)
        )
    except Exception as e:
        print(f"\n❌ Failed to initialize processor: {e}")
        return
    
    # Scan for screenshots
    print(f"\n🔍 Scanning for Samsung screenshots (last 7 days)...")
    try:
        all_screenshots = processor.scan_todays_screenshots(limit=None, force=False)
        
        if not all_screenshots:
            print(f"\n⚠️  No new Samsung screenshots found in last 7 days")
            print(f"\n💡 Tips:")
            print(f"   - Take a screenshot on Samsung S23")
            print(f"   - Ensure OneDrive sync is working")
            print(f"   - Check screenshot naming: Screenshot_YYYYMMDD_HHMMSS_AppName.jpg")
            print(f"   - Or use --force to reprocess existing screenshots")
            return
        
        print(f"\n✅ Found {len(all_screenshots)} unprocessed screenshots")
        
        # Show preview
        print(f"\n📸 Screenshots to process:")
        for i, screenshot in enumerate(all_screenshots[:5], 1):
            print(f"   {i}. {screenshot.name}")
        if len(all_screenshots) > 5:
            print(f"   ... and {len(all_screenshots) - 5} more")
        
    except Exception as e:
        print(f"\n❌ Scan failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Ask for confirmation
    print(f"\n" + "=" * 80)
    limit_input = input(f"How many screenshots to process? (1-{len(all_screenshots)}, or 'all'): ").strip()
    
    if limit_input.lower() == 'all':
        limit = None
    else:
        try:
            limit = int(limit_input)
            if limit < 1 or limit > len(all_screenshots):
                print(f"❌ Invalid number. Using default: 3")
                limit = min(3, len(all_screenshots))
        except ValueError:
            print(f"❌ Invalid input. Using default: 3")
            limit = min(3, len(all_screenshots))
    
    # Process screenshots
    print(f"\n" + "=" * 80)
    print(f"🚀 Processing screenshots with INDIVIDUAL FILE GENERATION...")
    print(f"=" * 80)
    
    try:
        result = processor.process_batch(limit=limit, force=False)
        
        # Display results
        print(f"\n" + "=" * 80)
        print(f"✅ PROCESSING COMPLETE")
        print(f"=" * 80)
        
        print(f"\n📊 Results:")
        print(f"   Processed: {result['processed_count']} screenshots")
        print(f"   Processing time: {result['processing_time']:.2f}s")
        print(f"   Average per screenshot: {result['processing_time'] / result['processed_count']:.2f}s")
        
        if result['individual_note_paths']:
            print(f"\n📝 Individual Notes Created:")
            for i, note_path in enumerate(result['individual_note_paths'], 1):
                note_name = Path(note_path).name
                print(f"   {i}. {note_name}")
            
            print(f"\n💡 Note Pattern: capture-YYYYMMDD-HHMM-keywords.md")
            print(f"   ✅ Each screenshot has its own file")
            print(f"   ✅ Semantic filenames for easy searching")
            print(f"   ✅ Individual tracking per screenshot")
        
        # Show file locations
        if result['individual_note_paths']:
            first_note = Path(result['individual_note_paths'][0])
            print(f"\n📂 Files created in: {first_note.parent}")
            print(f"\n🔍 Open in Obsidian to view!")
        
        # Performance comparison
        print(f"\n⚡ Performance vs Target:")
        target_time = result['processed_count'] * 45  # 45s per screenshot target
        actual_time = result['processing_time']
        speedup = target_time / actual_time if actual_time > 0 else 0
        print(f"   Target: <{target_time}s (45s per screenshot)")
        print(f"   Actual: {actual_time:.2f}s")
        print(f"   Speedup: {speedup:.1f}x faster! 🚀")
        
    except Exception as e:
        print(f"\n❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n" + "=" * 80)
    print(f"✅ Demo Complete!")
    print(f"=" * 80)


if __name__ == "__main__":
    main()
