#!/usr/bin/env python3
"""
Manual organization of Mustapha's Harissa campaign files.
Based on the file analysis, move specific identified files.
"""

import os
import shutil
from pathlib import Path

def main():
    # Paths
    vault_path = Path('/Users/thaddius/repos/inneros-zettelkasten')
    inbox_path = vault_path / 'knowledge' / 'Inbox'
    target_path = vault_path / 'knowledge' / 'Content Pipeline' / 'mustaphas-harissa-campaign'
    
    # Create target directory
    target_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created target directory: {target_path}")
    
    # List of all campaign files identified
    campaign_files = [
        # Main content articles
        'Busy weeknight trick that makes plain chicken taste like Marrakech.md',
        'Cooking vs finishing oils in Moroccan cuisine.md',
        'Everyday uses for preserved lemons beyond tagines.md',
        'Family friendly ways to introduce Moroccan flavors to picky eaters.md',
        'From Marrakech to your kitchen, a batch diary.md',
        'Honoring cultural food traditions while modernizing recipes.md',
        'How Moroccan pantry staples cut cooking time in half.md',
        'How ras el hanout varies across Morocco.md',
        'If your harissa has fillers it is not real harissa.md',
        'Ingredient deep dive what makes Moroccan olive oil unique.md',
        'Map the jar where key staples are grown.md',
        'Meet the farmers who make your preserved lemons possible.md',
        'Moroccan food at home is not hard, you are just missing this shortcut.md',
        'Myths vs reality Moroccan food is more than couscous and tagines.md',
        'One spoon equals instant Moroccan dinner.md',
        'Pantry math 3 ingredients equals Moroccan comfort bowl.md',
        'Preserved lemons, the magic ingredient you are sleeping on.md',
        'Quick swaps when you do not have the right spice.md',
        'Respect the roots cooking Moroccan flavors without appropriation.md',
        'Small scale co ops and how they keep traditions alive.md',
        'Step by step build confidence with your first Moroccan dish.md',
        'The 10 minute Moroccan meal hack no one talks about.md',
        'The one Moroccan staple chefs hide in everything.md',
        'The story behind the peppers in your jar.md',
        'This overlooked Moroccan spice blend changes everything.md',
        'Transform everyday proteins with one step.md',
        'Why clean label matters in ethnic pantry staples.md',
        'Why your harissa tastes flat and how to fix it.md',
        'You are using olive oil wrong, here is what Moroccans know.md',
        'You do not need 12 spices, just this one jar.md',
        
        # Content planning
        'Content Calendar -Mustapwha v1.md',
        'Content Calendar Planning.md',
        
        # Research data
        'perplexity-deep-research-briefs-20250827.jsonl'
    ]
    
    # Directories to move
    campaign_dirs = [
        'perplexity_outputs_dryrun',
        'perplexity_outputs_real'
    ]
    
    moved_count = 0
    failed_files = []
    
    print(f"\n🚚 Moving {len(campaign_files)} files and {len(campaign_dirs)} directories...")
    
    # Move individual files
    for filename in campaign_files:
        source_file = inbox_path / filename
        target_file = target_path / filename
        
        try:
            if source_file.exists():
                shutil.move(str(source_file), str(target_file))
                print(f"  ✅ {filename}")
                moved_count += 1
            else:
                print(f"  ⚠️  File not found: {filename}")
        except Exception as e:
            print(f"  ❌ {filename}: {e}")
            failed_files.append((filename, e))
    
    # Move directories
    for dirname in campaign_dirs:
        source_dir = inbox_path / dirname
        target_dir = target_path / dirname
        
        try:
            if source_dir.exists():
                shutil.move(str(source_dir), str(target_dir))
                print(f"  ✅ {dirname}/ (directory)")
                moved_count += 1
            else:
                print(f"  ⚠️  Directory not found: {dirname}")
        except Exception as e:
            print(f"  ❌ {dirname}: {e}")
            failed_files.append((dirname, e))
    
    # Report results
    print(f"\n📊 Results:")
    print(f"  ✅ Successfully moved: {moved_count}")
    print(f"  ❌ Failed to move: {len(failed_files)}")
    
    if failed_files:
        print(f"\n⚠️  Failed files/directories:")
        for item, error in failed_files:
            print(f"    {item}: {error}")
    
    print(f"\n🎉 Campaign content organized in: {target_path}")
    print(f"\n📂 You can now find all Mustapha's Harissa campaign content in:")
    print(f"   knowledge/Content Pipeline/mustaphas-harissa-campaign/")

if __name__ == "__main__":
    main()
