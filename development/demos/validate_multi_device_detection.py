#!/usr/bin/env python3
"""
Real Data Validation: Multi-Device Screenshot Detection
Tests MultiDeviceDetector with actual Samsung S23 and iPad screenshots
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from development.src.cli.multi_device_detector import MultiDeviceDetector, DeviceType


def validate_samsung_screenshots():
    """Validate Samsung S23 screenshot detection with real files"""
    print("=" * 80)
    print("📱 Samsung S23 Screenshot Validation")
    print("=" * 80)
    
    samsung_path = Path("/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Samsung Gallery/DCIM/Screenshots")
    
    if not samsung_path.exists():
        print(f"❌ Samsung path not found: {samsung_path}")
        return False
    
    detector = MultiDeviceDetector()
    screenshots = sorted(samsung_path.glob("Screenshot_*.jpg"))[:5]  # Test first 5
    
    if not screenshots:
        print(f"❌ No Samsung screenshots found in {samsung_path}")
        return False
    
    print(f"\n✅ Found {len(screenshots)} Samsung screenshots to test\n")
    
    success_count = 0
    for screenshot in screenshots:
        print(f"📄 Testing: {screenshot.name}")
        
        # Test device detection
        device_type = detector.detect_device(screenshot)
        if device_type == DeviceType.SAMSUNG_S23:
            print(f"   ✅ Device detected: {device_type.value}")
            success_count += 1
        else:
            print(f"   ❌ Wrong device type: {device_type.value}")
            continue
        
        # Test timestamp extraction
        timestamp = detector.extract_timestamp(screenshot)
        if timestamp:
            print(f"   ✅ Timestamp: {timestamp}")
        else:
            print(f"   ❌ Failed to extract timestamp")
            continue
        
        # Test metadata extraction
        metadata = detector.extract_metadata(screenshot)
        print(f"   ✅ Device: {metadata['device_name']}")
        if 'app_name' in metadata:
            print(f"   ✅ App: {metadata['app_name']}")
        print()
    
    print(f"✅ Samsung validation: {success_count}/{len(screenshots)} successful")
    return success_count == len(screenshots)


def validate_ipad_screenshots():
    """Validate iPad screenshot detection with real files"""
    print("\n" + "=" * 80)
    print("📱 iPad Screenshot Validation")
    print("=" * 80)
    
    ipad_path = Path("/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Camera Roll 1")
    
    if not ipad_path.exists():
        print(f"❌ iPad path not found: {ipad_path}")
        return False
    
    detector = MultiDeviceDetector()
    screenshots = sorted(ipad_path.glob("**/*_iOS.png"))[:5]  # Test first 5
    
    if not screenshots:
        print(f"❌ No iPad screenshots found in {ipad_path}")
        return False
    
    print(f"\n✅ Found {len(screenshots)} iPad screenshots to test\n")
    
    success_count = 0
    for screenshot in screenshots:
        print(f"📄 Testing: {screenshot.name}")
        print(f"   Location: {screenshot.parent.relative_to(ipad_path)}")
        
        # Test device detection
        device_type = detector.detect_device(screenshot)
        if device_type == DeviceType.IPAD:
            print(f"   ✅ Device detected: {device_type.value}")
            success_count += 1
        else:
            print(f"   ❌ Wrong device type: {device_type.value}")
            continue
        
        # Test timestamp extraction
        timestamp = detector.extract_timestamp(screenshot)
        if timestamp:
            print(f"   ✅ Timestamp: {timestamp}")
        else:
            print(f"   ❌ Failed to extract timestamp")
            continue
        
        # Test metadata extraction
        metadata = detector.extract_metadata(screenshot)
        print(f"   ✅ Device: {metadata['device_name']}")
        print(f"   ✅ No app_name (iPad doesn't provide this)")
        print()
    
    print(f"✅ iPad validation: {success_count}/{len(screenshots)} successful")
    return success_count == len(screenshots)


def validate_mixed_batch():
    """Validate processing mixed Samsung + iPad batch"""
    print("\n" + "=" * 80)
    print("🔀 Mixed Device Batch Validation")
    print("=" * 80)
    
    samsung_path = Path("/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Samsung Gallery/DCIM/Screenshots")
    ipad_path = Path("/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Camera Roll 1")
    
    detector = MultiDeviceDetector()
    
    # Collect mixed screenshots
    mixed_screenshots = []
    if samsung_path.exists():
        mixed_screenshots.extend(sorted(samsung_path.glob("Screenshot_*.jpg"))[:2])
    if ipad_path.exists():
        mixed_screenshots.extend(sorted(ipad_path.glob("**/*_iOS.png"))[:2])
    
    if not mixed_screenshots:
        print("❌ No screenshots found for mixed batch test")
        return False
    
    print(f"\n✅ Testing {len(mixed_screenshots)} screenshots from multiple devices\n")
    
    # Sort by timestamp
    screenshots_with_timestamps = []
    for screenshot in mixed_screenshots:
        timestamp = detector.extract_timestamp(screenshot)
        if timestamp:
            screenshots_with_timestamps.append((screenshot, timestamp))
    
    screenshots_with_timestamps.sort(key=lambda x: x[1])
    
    print("📅 Screenshots sorted by timestamp (oldest first):\n")
    for screenshot, timestamp in screenshots_with_timestamps:
        device_type = detector.detect_device(screenshot)
        print(f"   {timestamp} | {device_type.value:12} | {screenshot.name}")
    
    print(f"\n✅ Mixed batch validation successful: {len(screenshots_with_timestamps)} screenshots sorted")
    return True


def main():
    """Run all validation tests"""
    print("🔍 Multi-Device Screenshot Detection - Real Data Validation\n")
    
    results = {
        'Samsung S23': validate_samsung_screenshots(),
        'iPad': validate_ipad_screenshots(),
        'Mixed Batch': validate_mixed_batch()
    }
    
    print("\n" + "=" * 80)
    print("📊 Validation Summary")
    print("=" * 80)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(results.values())
    print(f"\n{'✅ All validations passed!' if all_passed else '❌ Some validations failed'}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
