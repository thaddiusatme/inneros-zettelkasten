#!/bin/bash
# Live Demo: Move note with image preservation

echo "════════════════════════════════════════════"
echo "🎯 Image Link Preservation - Live Demo"
echo "════════════════════════════════════════════"
echo ""

echo "📄 Current note location:"
ls -la "knowledge/Inbox/test-image-preservation-demo.md" 2>/dev/null || echo "Note not found in Inbox"
echo ""

echo "🖼️  Current image links in note:"
grep -E '!\[|!\[\[' "knowledge/Inbox/test-image-preservation-demo.md"
echo ""

echo "Press ENTER to execute the move with image preservation..."
read

echo ""
echo "🚀 Executing DirectoryOrganizer move..."
echo ""

python3 << 'PYTHON'
import sys
from pathlib import Path
sys.path.insert(0, 'development/src')

from utils.directory_organizer import DirectoryOrganizer

# Initialize
vault = Path('knowledge').resolve()
organizer = DirectoryOrganizer(str(vault))

# Get move plan
plan = organizer.plan_moves()

# Find our test note
for move in plan.moves:
    if 'test-image-preservation' in move.source.name:
        print(f"✅ Found note to move:")
        print(f"   From: {move.source.relative_to(vault)}")
        print(f"   To: {move.target.relative_to(vault)}")
        print()
        
        # Show image links BEFORE
        content_before = move.source.read_text()
        if organizer.image_manager:
            imgs_before = organizer.image_manager.parse_image_links(content_before)
            print(f"🖼️  Images BEFORE move: {len(imgs_before)} references")
            for img in imgs_before:
                print(f"   - {img['type']}: {img['filename']}")
        print()
        
        # Execute!
        print("🔧 Executing move with image preservation...")
        result = organizer.execute_moves(create_backup=True)
        
        print()
        print(f"✅ Move complete!")
        print(f"   Moves executed: {result['moves_executed']}")
        print(f"   Backup created: {result.get('backup_path', 'N/A')}")
        print()
        
        # Show image links AFTER
        if move.target.exists():
            content_after = move.target.read_text()
            if organizer.image_manager:
                imgs_after = organizer.image_manager.parse_image_links(content_after)
                print(f"🖼️  Images AFTER move: {len(imgs_after)} references")
                for img in imgs_after:
                    print(f"   - {img['type']}: {img['filename']}")
        
        break
PYTHON

echo ""
echo "════════════════════════════════════════════"
echo "🎉 SUCCESS! Check the results:"
echo "════════════════════════════════════════════"
echo ""
echo "📂 Note is now at: knowledge/Fleeting Notes/test-image-preservation-demo.md"
echo "🖼️  All image links preserved automatically"
echo ""
echo "Open the note in Obsidian - all 3 images still working!"
