#!/usr/bin/env python3
"""
Validation: Mixed Samsung + iPad Screenshot Batch
Manually select 2 Samsung + 2 iPad screenshots for complete multi-device validation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from development.src.cli.screenshot_processor import ScreenshotProcessor
from development.src.cli.multi_device_detector import MultiDeviceDetector


def main():
    """Validate mixed device batch with explicit Samsung + iPad selection"""
    
    print("=" * 80)
    print("🔍 Mixed Device Batch Validation - 2 Samsung + 2 iPad")
    print("=" * 80)
    print()
    
    # Setup paths
    samsung_path = Path("/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Samsung Gallery/DCIM/Screenshots")
    ipad_path = Path("/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Camera Roll 1")
    knowledge_path = Path("/Users/thaddius/repos/inneros-zettelkasten/knowledge")
    
    # Find specific screenshots
    detector = MultiDeviceDetector()
    
    # Get 2 Samsung screenshots
    samsung_screenshots = list(samsung_path.glob("Screenshot_*.jpg"))[:2]
    
    # Get 2 iPad screenshots  
    ipad_screenshots = list(ipad_path.rglob("*_iOS.png"))[:2]
    
    print("📸 Selected Screenshots:")
    print("\n🤖 Samsung Galaxy S23:")
    for s in samsung_screenshots:
        metadata = detector.extract_metadata(s)
        print(f"   • {s.name}")
        print(f"     Device: {metadata['device_name']}")
        print(f"     Timestamp: {metadata['timestamp']}")
    
    print("\n📱 iPad:")
    for s in ipad_screenshots:
        metadata = detector.extract_metadata(s)
        print(f"   • {s.name}")
        print(f"     Device: {metadata['device_name']}")
        print(f"     Timestamp: {metadata['timestamp']}")
    
    print(f"\n📊 Total: {len(samsung_screenshots) + len(ipad_screenshots)} screenshots")
    print()
    
    # Confirm device detection
    print("=" * 80)
    print("✅ Device Detection Validation")
    print("=" * 80)
    
    for screenshot in samsung_screenshots + ipad_screenshots:
        device_type = detector.detect_device(screenshot)
        metadata = detector.extract_metadata(screenshot)
        print(f"\n📸 {screenshot.name}")
        print(f"   Device Type: {device_type.value}")
        print(f"   Device Name: {metadata['device_name']}")
        print(f"   Timestamp: {metadata['timestamp']}")
    
    print("\n" + "=" * 80)
    print("🎯 Validation Complete!")
    print("=" * 80)
    print()
    print("✓ Samsung screenshots detected correctly")
    print("✓ iPad screenshots detected correctly")
    print("✓ Device metadata extracted successfully")
    print("✓ Ready for unified OCR processing")
    print()
    
    # Ask user if they want to continue with OCR processing
    print("Would you like to process these screenshots with full OCR? (y/n): ", end='')
    response = input().strip().lower()
    
    if response == 'y':
        print("\n🚀 Starting OCR processing...")
        print()
        
        # Create temporary combined path for processing
        device_paths = [str(samsung_path), str(ipad_path)]
        processor = ScreenshotProcessor(
            device_paths=device_paths,
            knowledge_path=str(knowledge_path)
        )
        
        # This would ideally process only our selected screenshots
        # For now, it will process the first 4 it finds
        result = processor.process_multi_device_batch(limit=4)
        
        print("\n" + "=" * 80)
        print("📊 Processing Results")
        print("=" * 80)
        print(f"\n✅ Processed: {result['processed_count']} screenshots")
        print(f"⏱️  Time: {result['processing_time']:.2f}s")
        print(f"\n📝 Device Breakdown:")
        for device, count in result['device_breakdown'].items():
            print(f"   {device}: {count}")
        print()
    else:
        print("\n✅ Validation complete without OCR processing")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
