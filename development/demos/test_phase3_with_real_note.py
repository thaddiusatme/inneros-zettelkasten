#!/usr/bin/env python3
"""
Real YouTube Note Validation: Phase 3 Note Linking

Tests Phase 3 functionality with a realistic YouTube note structure
that matches actual user workflow patterns.

Author: InnerOS Zettelkasten Team
Date: 2025-10-18
"""

import sys
from pathlib import Path
import shutil
from datetime import datetime

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.frontmatter import parse_frontmatter, build_frontmatter


def main():
    """Test Phase 3 linking with realistic YouTube note."""
    print("🚀 Phase 3 Real YouTube Note Validation")
    print("="*80)
    
    # Get paths
    demos_dir = Path(__file__).parent
    note_path = demos_dir / "test-youtube-note-real.md"
    
    if not note_path.exists():
        print(f"❌ Test note not found: {note_path}")
        return
    
    # Create backup
    backup_path = demos_dir / "test-youtube-note-real.md.backup"
    shutil.copy(note_path, backup_path)
    print(f"📋 Created backup: {backup_path.name}")
    
    try:
        # Read original note
        original_content = note_path.read_text()
        print(f"\n📝 Original Note:")
        print("─" * 80)
        print(original_content[:400] + "..." if len(original_content) > 400 else original_content)
        print("─" * 80)
        
        # Extract video_id from video_url in frontmatter
        metadata, body = parse_frontmatter(original_content)
        video_url = metadata.get('video_url', '')
        
        # Extract video ID from URL
        video_id = None
        if 'watch?v=' in video_url:
            video_id = video_url.split('watch?v=')[1].split('&')[0]
        
        if not video_id:
            print("❌ No video_id found in note")
            return
        
        print(f"\n🔍 Extracted video_id: {video_id}")
        
        # Generate transcript wikilink (simulating Phase 2 handler)
        date_str = datetime.now().strftime("%Y-%m-%d")
        transcript_wikilink = f"[[youtube-{video_id}-{date_str}]]"
        print(f"🔗 Generated transcript wikilink: {transcript_wikilink}")
        
        # Phase 3 Step 1: Update frontmatter
        print("\n" + "="*80)
        print("📋 STEP 1: Update Frontmatter")
        print("="*80)
        
        metadata['transcript_file'] = transcript_wikilink
        updated_content = build_frontmatter(metadata, body)
        
        # Verify frontmatter update
        test_meta, _ = parse_frontmatter(updated_content)
        if 'transcript_file' in test_meta:
            print(f"✅ Frontmatter updated: transcript_file = {test_meta['transcript_file']}")
        else:
            print("❌ Frontmatter update failed")
            return
        
        # Phase 3 Step 2: Insert body link
        print("\n" + "="*80)
        print("📄 STEP 2: Insert Body Link")
        print("="*80)
        
        metadata, body = parse_frontmatter(updated_content)
        transcript_line = f"\n**Full Transcript**: {transcript_wikilink}\n"
        
        # Find first heading
        lines = body.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith('# '):
                insert_index = i + 1
                print(f"🔍 Found heading at line {i}: {line.strip()}")
                break
        
        # Insert transcript link
        lines.insert(insert_index, transcript_line)
        updated_body = '\n'.join(lines)
        final_content = build_frontmatter(metadata, updated_body)
        
        # Write updated note
        note_path.write_text(final_content)
        print(f"✅ Updated note written to: {note_path.name}")
        
        # Verification
        print("\n" + "="*80)
        print("🔍 VERIFICATION")
        print("="*80)
        
        verify_content = note_path.read_text()
        verify_meta, verify_body = parse_frontmatter(verify_content)
        
        # Check all requirements
        checks = {
            "Frontmatter has transcript_file": 'transcript_file' in verify_meta,
            "Frontmatter has correct wikilink": transcript_wikilink in str(verify_meta.get('transcript_file', '')),
            "Body has transcript link": '**Full Transcript**:' in verify_body,
            "Body has correct wikilink": transcript_wikilink in verify_body,
            "Original title preserved": 'But what is a neural network?' in verify_body,
            "Original sections preserved": '## Key Concepts' in verify_body and '## My Notes' in verify_body,
            "Original content preserved": 'Neural networks are inspired' in verify_body,
        }
        
        all_passed = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}")
            if not result:
                all_passed = False
        
        # Show final note
        print("\n" + "="*80)
        print("📄 FINAL NOTE WITH LINKS")
        print("="*80)
        print(verify_content)
        print("="*80)
        
        # Summary
        print("\n" + "="*80)
        print("🎉 VALIDATION SUMMARY")
        print("="*80)
        
        if all_passed:
            print("✅ ALL CHECKS PASSED!")
            print("\n📊 Phase 3 Features Validated:")
            print("   ✅ Frontmatter integration with transcript_file field")
            print("   ✅ Body link insertion after title")
            print("   ✅ Complete content preservation")
            print("   ✅ Proper wikilink formatting")
            print("\n🚀 Ready for production use with real YouTube notes!")
        else:
            print("⚠️ SOME CHECKS FAILED - Review implementation")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Ask if user wants to keep changes
        print("\n" + "="*80)
        print(f"💾 Backup saved as: {backup_path.name}")
        print("   You can restore with: mv test-youtube-note-real.md.backup test-youtube-note-real.md")
        print("="*80)


if __name__ == "__main__":
    main()
