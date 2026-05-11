#!/usr/bin/env python3
"""
Organize Mustapha's Harissa campaign content from Inbox to dedicated directory.
Uses the production-ready DirectoryOrganizer with safety-first principles.
"""

import os
import sys
import re
from pathlib import Path

# Add development path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'development'))

from src.utils.directory_organizer import DirectoryOrganizer

def identify_harissa_campaign_files(inbox_path):
    """Identify files related to the Mustapha's Harissa campaign."""
    
    # Keywords that indicate Harissa campaign content
    campaign_keywords = [
        'moroccan', 'harissa', 'preserved', 'lemons', 'tagines', 'couscous',
        'marrakech', 'ras el hanout', 'spice', 'olive oil', 'pantry', 'staples',
        'mustapha', 'jar', 'farmers', 'roots', 'traditions', 'ethnic',
        'content calendar', 'perplexity'
    ]
    
    campaign_files = []
    inbox_files = list(Path(inbox_path).glob('*.md'))
    
    for file_path in inbox_files:
        filename_lower = file_path.name.lower()
        
        # Check if filename contains campaign keywords
        for keyword in campaign_keywords:
            if keyword in filename_lower:
                campaign_files.append(file_path)
                break
    
    # Also include perplexity directories and JSONL files
    perplexity_paths = list(Path(inbox_path).glob('perplexity*'))
    campaign_files.extend(perplexity_paths)
    
    return campaign_files

def main():
    # Paths
    vault_path = Path(__file__).parent / 'knowledge'
    inbox_path = vault_path / 'Inbox'
    target_path = vault_path / 'Content Pipeline' / 'mustaphas-harissa-campaign'
    
    print("🏺 Mustapha's Harissa Campaign Content Organization")
    print("=" * 60)
    
    # Initialize DirectoryOrganizer
    organizer = DirectoryOrganizer(str(vault_path))
    
    # Create target directory if it doesn't exist
    target_path.mkdir(exist_ok=True)
    print(f"📁 Target directory: {target_path}")
    
    # Identify campaign files
    campaign_files = identify_harissa_campaign_files(inbox_path)
    
    print(f"\n🔍 Found {len(campaign_files)} campaign-related files:")
    for i, file_path in enumerate(campaign_files, 1):
        print(f"  {i:2d}. {file_path.name}")
    
    if not campaign_files:
        print("No campaign files found!")
        return
    
    # Confirm with user
    response = input(f"\n📦 Move {len(campaign_files)} files to {target_path.name}? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Create backup first (safety-first principle)
    print("\n💾 Creating safety backup...")
    backup_path = organizer.create_backup()
    print(f"✅ Backup created: {backup_path}")
    
    # Move files
    print(f"\n🚚 Moving files to {target_path.name}...")
    moved_count = 0
    failed_files = []
    
    for file_path in campaign_files:
        try:
            target_file = target_path / file_path.name
            
            # Handle directory moves (like perplexity_outputs)
            if file_path.is_dir():
                import shutil
                shutil.move(str(file_path), str(target_file))
            else:
                file_path.rename(target_file)
            
            print(f"  ✅ {file_path.name}")
            moved_count += 1
            
        except Exception as e:
            print(f"  ❌ {file_path.name}: {e}")
            failed_files.append((file_path, e))
    
    # Report results
    print(f"\n📊 Results:")
    print(f"  ✅ Successfully moved: {moved_count}")
    print(f"  ❌ Failed to move: {len(failed_files)}")
    
    if failed_files:
        print(f"\n⚠️  Failed files:")
        for file_path, error in failed_files:
            print(f"    {file_path.name}: {error}")
    
    print(f"\n🎉 Campaign content organized in: {target_path}")
    print(f"💾 Backup available at: {backup_path}")

if __name__ == "__main__":
    main()
