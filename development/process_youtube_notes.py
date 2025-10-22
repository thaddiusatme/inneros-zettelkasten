#!/usr/bin/env python3
"""
Quick script to process YouTube notes directly
Bypasses CLI issues and uses the core handler
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

# Process notes
notes_to_process = [
    "../knowledge/Inbox/YouTube/lit-20251018-0845-andrej-karpathy-we-re-summoning-ghosts-not-building-animals.md.md",
    "../knowledge/Inbox/YouTube/lit-20251018-0924-andrej-karpathy-we-re-summoning-ghosts-not-building-animals.md.md"
]

print("=" * 80)
print("🚀 Processing YouTube Notes Directly")
print("=" * 80)

for note_path in notes_to_process:
    path = Path(__file__).parent / note_path
    if not path.exists():
        print(f"\n⏭️  Skipping (not found): {path.name}")
        continue
    
    print(f"\n📝 Processing: {path.name}")
    
    # Read and check frontmatter
    content = path.read_text()
    
    # Check for required fields
    has_source = 'source: youtube' in content
    has_video_id = 'video_id:' in content
    has_video_url = 'video_url:' in content
    
    print(f"   ✅ source: youtube" if has_source else "   ❌ Missing: source: youtube")
    print(f"   ✅ video_id present" if has_video_id else "   ❌ Missing: video_id")
    print(f"   ✅ video_url present" if has_video_url else "   ❌ Missing: video_url")
    
    if not has_video_url:
        print(f"\n   ⚠️  Add video_url to frontmatter first!")
        continue
    
    # Extract video_url for processing
    for line in content.split('\n'):
        if line.startswith('video_url:'):
            video_url = line.split(':', 1)[1].strip()
            print(f"   🔗 Found URL: {video_url}")
            break
    
    print(f"\n   ℹ️  Ready to process - use YouTube CLI or daemon")

print("\n" + "=" * 80)
print("✅ Analysis Complete")
print("=" * 80)
print("\nTo process these notes:")
print("1. Make sure both have 'video_url' in frontmatter")
print("2. Run: cd development && python3 -m src.automation.daemon start")
print("   OR")
print("3. Save the note again (triggers file watcher when daemon running)")
print("=" * 80)
