#!/usr/bin/env python3
"""
Smart Date Detection Demo
Shows automatic date extraction from Samsung/iPad filenames
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.image_attachment_manager import ImageAttachmentManager

print("🎯 Smart Date Detection Demo")
print("=" * 70)
print()

# Test filenames
test_cases = [
    # Samsung screenshots
    ("Screenshot_20250915_140530_Chrome.jpg", "Samsung screenshot from Sept 15, 2025 at 14:05:30"),
    ("Screenshot_20251002_083000_Messenger.jpg", "Samsung screenshot from Oct 2, 2025 at 08:30:00"),
    
    # iPad screenshots
    ("20241215_093000000_iOS.png", "iPad screenshot from Dec 15, 2024 at 09:30:00"),
    
    # Regular images (will use file date)
    ("vacation-photo.jpg", "Regular photo (uses file modification date)"),
    ("pasted-image.png", "Pasted image (uses file modification date)"),
]

# Create manager
manager = ImageAttachmentManager(base_path=Path("knowledge"))

print("📅 Date Extraction Examples:\n")

for filename, description in test_cases:
    # Create temporary file to test
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as tmp:
        tmp_path = Path(tmp.name)
        tmp_path.write_text("fake image")
        
        # Rename to test filename
        test_path = tmp_path.parent / filename
        tmp_path.rename(test_path)
        
        try:
            # Extract date
            capture_date = manager._extract_capture_date(test_path)
            device = manager._detect_device_from_filename(filename)
            
            # Show results
            print(f"📸 {filename}")
            print(f"   Description: {description}")
            print(f"   Detected date: {capture_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Device type: {device or 'unknown (generic)'}")
            print(f"   → Would save to: attachments/{capture_date.year:04d}-{capture_date.month:02d}/")
            
            if device:
                dest_filename = f"{device}-{capture_date.strftime('%Y%m%d-%H%M%S')}{Path(filename).suffix}"
                print(f"   → Filename: {dest_filename}")
            else:
                print(f"   → Filename: {filename} (original)")
            
            print()
            
        finally:
            # Cleanup
            test_path.unlink()

print("=" * 70)
print()
print("✅ Smart Date Detection Features:")
print("   1. ✅ Samsung: Extracts from Screenshot_YYYYMMDD_HHMMSS_*.jpg")
print("   2. ✅ iPad: Extracts from YYYYMMDD_HHMMSS000_iOS.png")
print("   3. ✅ Fallback: Uses file modification date for other images")
print()
print("🎯 Result: Fully automatic - no manual date entry needed!")
