#!/usr/bin/env python3
"""
Quick metadata repair for 5 notes missing type: field.

Infers type from filename patterns:
- youtube-*.md → type: literature
- lit-*.md → type: literature  
- capture-*.md → type: fleeting
- Untitled.md → needs manual inspection
"""

from pathlib import Path
import yaml
import re

VAULT_ROOT = Path(__file__).parent.parent

NOTES_TO_FIX = [
    "knowledge/Inbox/Untitled.md",
    "knowledge/Inbox/YouTube/youtube-20251005-1407-AN7c5S9k5L0.md",
    "knowledge/Inbox/YouTube/youtube-20251005-1344-OYlQyPo-L4g.md",
    "knowledge/Inbox/YouTube/youtube-20251005-1407-GuTcle5edjk.md",
    "knowledge/Inbox/YouTube/youtube-20251005-0957-EUG65dIY-2k.md",
]


def infer_type_from_filename(filename: str) -> str:
    """Infer note type from filename pattern."""
    if filename.startswith('youtube-') or filename.startswith('lit-'):
        return 'literature'
    elif filename.startswith('capture-') or filename.startswith('fleeting-'):
        return 'fleeting'
    elif filename.startswith('perm-'):
        return 'permanent'
    else:
        return None  # Needs manual decision


def add_type_to_note(note_path: Path, note_type: str) -> bool:
    """Add type: field to note frontmatter."""
    try:
        content = note_path.read_text(encoding='utf-8')
        
        # Check if already has type
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        
        if not match:
            # No frontmatter - create it
            frontmatter = {'type': note_type, 'status': 'inbox'}
            new_frontmatter = yaml.dump(frontmatter, default_flow_style=False)
            new_content = f"---\n{new_frontmatter}---\n{content}"
        else:
            # Has frontmatter - update it
            frontmatter_str = match.group(1)
            body = match.group(2)
            
            frontmatter = yaml.safe_load(frontmatter_str) or {}
            
            # Add type if missing
            if not frontmatter.get('type'):
                frontmatter['type'] = note_type
                
                # Add status if missing
                if not frontmatter.get('status'):
                    frontmatter['status'] = 'inbox'
                
                new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
                new_content = f"---\n{new_frontmatter}---\n{body}"
            else:
                print(f"  ⚠️  Already has type: {frontmatter.get('type')}")
                return False
        
        # Write updated content
        note_path.write_text(new_content, encoding='utf-8')
        return True
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    print("🔧 Metadata Repair Script")
    print(f"   Fixing {len(NOTES_TO_FIX)} notes with missing type: field")
    print()
    
    fixed_count = 0
    skipped_count = 0
    
    for note_rel_path in NOTES_TO_FIX:
        note_path = VAULT_ROOT / note_rel_path
        filename = note_path.name
        
        print(f"📝 {filename}")
        
        if not note_path.exists():
            print(f"  ⚠️  File not found")
            skipped_count += 1
            continue
        
        # Infer type
        inferred_type = infer_type_from_filename(filename)
        
        if inferred_type:
            print(f"  → Inferred type: {inferred_type}")
            
            if add_type_to_note(note_path, inferred_type):
                print(f"  ✅ Fixed")
                fixed_count += 1
            else:
                skipped_count += 1
        else:
            print(f"  ⚠️  Cannot infer type - needs manual inspection")
            print(f"     Path: {note_rel_path}")
            skipped_count += 1
        
        print()
    
    print(f"📊 Summary:")
    print(f"   Fixed: {fixed_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Total: {len(NOTES_TO_FIX)}")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
