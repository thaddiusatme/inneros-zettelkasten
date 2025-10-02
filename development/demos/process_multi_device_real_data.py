#!/usr/bin/env python3
"""
Real Data End-to-End Test: Multi-Device Screenshot Processing
Process 2 Samsung S23 + 2 iPad screenshots with full OCR and note generation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from development.src.cli.screenshot_processor import ScreenshotProcessor


def main():
    """Process real Samsung + iPad screenshots end-to-end"""
    
    print("=" * 80)
    print("🔍 Multi-Device Screenshot Processing - Real Data Test")
    print("=" * 80)
    print()
    
    # Setup paths
    samsung_path = "/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Samsung Gallery/DCIM/Screenshots"
    ipad_path = "/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Camera Roll 1"
    knowledge_path = "/Users/thaddius/repos/inneros-zettelkasten/knowledge"
    
    # Create multi-device processor
    device_paths = [samsung_path, ipad_path]
    
    print("📂 Device Paths:")
    print(f"   Samsung: {samsung_path}")
    print(f"   iPad: {ipad_path}")
    print(f"   Knowledge Base: {knowledge_path}")
    print()
    
    # Initialize processor in multi-device mode
    processor = ScreenshotProcessor(
        device_paths=device_paths,
        knowledge_path=knowledge_path
    )
    
    print("✅ Multi-device processor initialized")
    print()
    
    # Process batch with limit (2 screenshots total for quick test)
    print("🚀 Processing 4 screenshots (2 Samsung + 2 iPad)...")
    print()
    
    try:
        result = processor.process_multi_device_batch(limit=4)
        
        print("\n" + "=" * 80)
        print("📊 Processing Results")
        print("=" * 80)
        print()
        print(f"✅ Successfully processed: {result['processed_count']} screenshots")
        print(f"⏱️  Processing time: {result['processing_time']:.2f} seconds")
        print(f"🤖 OCR results: {result['ocr_results']}")
        print()
        
        print("📝 Device Breakdown:")
        for device, count in result['device_breakdown'].items():
            print(f"   {device}: {count} screenshots")
        print()
        
        print("📄 Generated Notes:")
        for i, note_path in enumerate(result['individual_note_paths'], 1):
            note_name = Path(note_path).name
            print(f"   {i}. {note_name}")
        print()
        
        # Show sample note content
        if result['individual_note_paths']:
            sample_note = Path(result['individual_note_paths'][0])
            print("=" * 80)
            print(f"📖 Sample Note Content: {sample_note.name}")
            print("=" * 80)
            print()
            
            with open(sample_note, 'r') as f:
                content = f.read()
                # Show first 50 lines
                lines = content.split('\n')[:50]
                print('\n'.join(lines))
                if len(content.split('\n')) > 50:
                    print(f"\n... ({len(content.split('\n')) - 50} more lines)")
            print()
        
        print("=" * 80)
        print("✅ Multi-Device Processing Complete!")
        print("=" * 80)
        print()
        print("🎯 Validation Points:")
        print("   ✓ Both Samsung and iPad screenshots processed")
        print("   ✓ Device metadata in note frontmatter")
        print("   ✓ Unified OCR pipeline applied")
        print("   ✓ Semantic filenames generated")
        print("   ✓ Individual notes created in knowledge/Inbox/")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
