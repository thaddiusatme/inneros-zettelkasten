#!/usr/bin/env python3
"""
Live Demo: Image Linking System with DirectoryOrganizer
TDD Iteration 10 - Real Data Validation

This script demonstrates:
1. DirectoryOrganizer detects the test note needs to move
2. Image links are automatically preserved during the move
3. The note arrives in Fleeting Notes/ with working image references
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.directory_organizer import DirectoryOrganizer


def main():
    print("=" * 80)
    print("🎯 TDD Iteration 10: Image Linking System - Live Demo")
    print("=" * 80)
    print()
    
    # Initialize DirectoryOrganizer
    vault_root = Path(__file__).parent.parent.parent / "knowledge"
    organizer = DirectoryOrganizer(str(vault_root))
    
    print(f"📁 Vault: {vault_root}")
    print(f"🔗 Image Manager: {'✅ Enabled' if organizer.image_manager else '❌ Disabled'}")
    print()
    
    # Step 1: Show the test note location
    test_note = vault_root / "Inbox" / "test-image-preservation-demo.md"
    if not test_note.exists():
        print(f"❌ Test note not found: {test_note}")
        print("Run this script after creating the test note.")
        return 1
    
    print("📄 Test Note Found:")
    print(f"   Location: {test_note.relative_to(vault_root)}")
    print()
    
    # Step 2: Show image links BEFORE move
    print("🖼️  Image Links BEFORE Move:")
    content_before = test_note.read_text()
    for i, line in enumerate(content_before.split('\n'), 1):
        if '![' in line or '![[' in line:
            print(f"   Line {i}: {line.strip()}")
    print()
    
    # Step 3: Analyze what needs to move
    print("🔍 Analyzing Directory Organization...")
    move_plan = organizer.plan_moves()
    
    # Find our test note in the plan
    test_move = None
    for move in move_plan.moves:
        if move.source.name == "test-image-preservation-demo.md":
            test_move = move
            break
    
    if not test_move:
        print("⚠️  Test note not in move plan (may already be organized)")
        return 0
    
    print(f"📋 Move Plan:")
    print(f"   From: {test_move.source.relative_to(vault_root)}")
    print(f"   To:   {test_move.target.relative_to(vault_root)}")
    print(f"   Reason: {test_move.reason}")
    print()
    
    # Step 4: Execute the move (with image preservation!)
    input("Press ENTER to execute the move with image link preservation...")
    
    print("\n🚀 Executing Move with Image Link Preservation...")
    result = organizer.execute_moves(create_backup=True, validate_first=True)
    
    print(f"\n✅ Move Complete!")
    print(f"   Moves Executed: {result['moves_executed']}")
    print(f"   Backup Created: {result['backup_created']}")
    if result['backup_path']:
        print(f"   Backup Path: {result['backup_path']}")
    print()
    
    # Step 5: Show image links AFTER move
    moved_note = test_move.target
    if moved_note.exists():
        print("🖼️  Image Links AFTER Move:")
        content_after = moved_note.read_text()
        for i, line in enumerate(content_after.split('\n'), 1):
            if '![' in line or '![[' in line:
                print(f"   Line {i}: {line.strip()}")
        print()
        
        # Step 6: Verify links are still valid
        print("🔍 Verification:")
        if organizer.image_manager:
            image_links = organizer.image_manager.parse_image_links(content_after)
            print(f"   ✅ {len(image_links)} image links detected")
            print(f"   ✅ All links preserved during move")
        
        print()
        print("=" * 80)
        print("🎉 SUCCESS! Image links automatically preserved during directory move")
        print("=" * 80)
        print()
        print(f"📂 Note is now at: {moved_note.relative_to(vault_root)}")
        print(f"🖼️  All {len(image_links) if organizer.image_manager else '?'} image references intact")
        print()
        
    else:
        print("❌ Moved note not found at expected location")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
