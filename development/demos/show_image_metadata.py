#!/usr/bin/env python3
"""
Show image file metadata to understand organization options
"""
import os
from pathlib import Path
from datetime import datetime

# Check some real images
images = [
    Path("knowledge/Pasted image 20250920152753.png"),
    Path("knowledge/Fleeting Notes/image.png"),
    Path("knowledge/attachments/2025-10/pasted-screenshot.png")
]

print("📊 Image File Metadata Analysis\n")
print("=" * 70)

for img in images:
    if not img.exists():
        continue
    
    stat = img.stat()
    
    # Get timestamps
    modified = datetime.fromtimestamp(stat.st_mtime)
    created = datetime.fromtimestamp(stat.st_ctime)
    
    print(f"\n📄 {img.name}")
    print(f"   Location: {img.parent}")
    print(f"   Size: {stat.st_size / 1024:.1f} KB")
    print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show what folder it would go in
    folder_modified = f"{modified.year:04d}-{modified.month:02d}"
    folder_created = f"{created.year:04d}-{created.month:02d}"
    
    print(f"   → By modified date: attachments/{folder_modified}/")
    print(f"   → By created date: attachments/{folder_created}/")

print("\n" + "=" * 70)
print("\n💡 Current Implementation:")
print("   Uses capture_date parameter (when you run the save command)")
print("   This gives you control over organization independent of file dates")
print()
print("💡 Alternative:")
print("   Could use file.stat().st_mtime (modification date)")
print("   Would organize by when screenshot was actually taken")
