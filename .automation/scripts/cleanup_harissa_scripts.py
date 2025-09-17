#!/usr/bin/env python3
"""
Clean up Harissa organization scripts by moving them to proper directory.
"""

import shutil
from pathlib import Path

def main():
    # Paths
    root_path = Path('/Users/thaddius/repos/inneros-zettelkasten')
    target_scripts_dir = root_path / '.automation' / 'scripts'
    
    # Scripts to move
    scripts_to_move = [
        'organize_harissa_content.py',
        'manual_organize_harissa.py'
    ]
    
    print("🧹 Cleaning up Harissa organization scripts")
    print("=" * 50)
    
    # Ensure target directory exists
    target_scripts_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Target directory: {target_scripts_dir}")
    
    moved_count = 0
    
    for script_name in scripts_to_move:
        source_file = root_path / script_name
        target_file = target_scripts_dir / script_name
        
        try:
            if source_file.exists():
                shutil.move(str(source_file), str(target_file))
                print(f"  ✅ Moved {script_name}")
                moved_count += 1
            else:
                print(f"  ⚠️  File not found: {script_name}")
        except Exception as e:
            print(f"  ❌ Error moving {script_name}: {e}")
    
    print(f"\n📊 Results:")
    print(f"  ✅ Successfully moved: {moved_count} scripts")
    print(f"\n🎉 Organization scripts now located in:")
    print(f"   .automation/scripts/")
    
    # Also clean up this cleanup script
    cleanup_script = root_path / 'cleanup_harissa_scripts.py'
    if cleanup_script.exists():
        try:
            cleanup_target = target_scripts_dir / 'cleanup_harissa_scripts.py'
            shutil.move(str(cleanup_script), str(cleanup_target))
            print(f"  ✅ Moved cleanup_harissa_scripts.py (self-cleanup)")
        except Exception as e:
            print(f"  ⚠️  Could not self-clean: {e}")

if __name__ == "__main__":
    main()
