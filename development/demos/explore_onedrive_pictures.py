#!/usr/bin/env python3
"""
Explore OneDrive Pictures directory structure to find screenshot locations
"""

import os
from pathlib import Path
from collections import defaultdict


def explore_directory_structure(base_path: Path, max_depth: int = 3) -> dict:
    """
    Recursively explore directory structure and categorize files
    
    Args:
        base_path: Root directory to explore
        max_depth: Maximum depth to traverse
        
    Returns:
        Dictionary with directory structure and file statistics
    """
    structure = {
        'directories': [],
        'files_by_type': defaultdict(list),
        'screenshot_candidates': [],
        'total_files': 0,
        'total_dirs': 0
    }
    
    def scan_dir(path: Path, depth: int = 0):
        if depth > max_depth:
            return
        
        try:
            items = sorted(path.iterdir())
        except PermissionError:
            print(f"⚠️  Permission denied: {path}")
            return
        except Exception as e:
            print(f"⚠️  Error reading {path}: {e}")
            return
        
        for item in items:
            # Skip hidden files and system files
            if item.name.startswith('.'):
                continue
            
            if item.is_dir():
                structure['total_dirs'] += 1
                rel_path = item.relative_to(base_path)
                structure['directories'].append({
                    'path': str(rel_path),
                    'depth': depth,
                    'full_path': str(item)
                })
                # Recurse into subdirectory
                scan_dir(item, depth + 1)
                
            elif item.is_file():
                structure['total_files'] += 1
                ext = item.suffix.lower()
                
                # Categorize by extension
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    structure['files_by_type']['images'].append(str(item.relative_to(base_path)))
                    
                    # Check if filename suggests it's a screenshot
                    name_lower = item.name.lower()
                    if any(keyword in name_lower for keyword in ['screenshot', 'screen', 'capture', 'img_']):
                        structure['screenshot_candidates'].append({
                            'path': str(item.relative_to(base_path)),
                            'name': item.name,
                            'size_kb': item.stat().st_size // 1024,
                            'directory': str(item.parent.relative_to(base_path))
                        })
                elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
                    structure['files_by_type']['videos'].append(str(item.relative_to(base_path)))
                elif ext in ['.m4a', '.mp3', '.wav']:
                    structure['files_by_type']['audio'].append(str(item.relative_to(base_path)))
    
    scan_dir(base_path)
    return structure


def analyze_screenshot_directories(structure: dict) -> dict:
    """Analyze which directories contain the most screenshot candidates"""
    dir_counts = defaultdict(int)
    
    for candidate in structure['screenshot_candidates']:
        directory = candidate['directory']
        dir_counts[directory] += 1
    
    return dict(sorted(dir_counts.items(), key=lambda x: x[1], reverse=True))


def main():
    pictures_path = Path("/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures")
    
    print("=" * 80)
    print("🔍 OneDrive Pictures Directory Explorer")
    print("=" * 80)
    
    if not pictures_path.exists():
        print(f"\n❌ Path not found: {pictures_path}")
        return
    
    print(f"\n📁 Scanning: {pictures_path}")
    print("⏳ This may take a moment...\n")
    
    # Explore directory structure
    structure = explore_directory_structure(pictures_path, max_depth=4)
    
    # Display results
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total directories: {structure['total_dirs']}")
    print(f"Total files: {structure['total_files']}")
    print(f"Screenshot candidates: {len(structure['screenshot_candidates'])}")
    
    # Display file type breakdown
    print(f"\n📋 File Types:")
    for file_type, files in structure['files_by_type'].items():
        print(f"   {file_type.capitalize()}: {len(files)}")
    
    # Display directory tree
    print(f"\n🌲 Directory Tree (depth 0-2):")
    depth_0_dirs = [d for d in structure['directories'] if d['depth'] == 0]
    for dir_info in depth_0_dirs[:20]:  # Limit to first 20
        print(f"   📁 {dir_info['path']}/")
        
        # Show depth 1 subdirectories
        depth_1_dirs = [d for d in structure['directories'] 
                       if d['depth'] == 1 and d['path'].startswith(dir_info['path'])]
        for subdir in depth_1_dirs[:5]:  # Limit subdirs
            rel_path = subdir['path'].replace(dir_info['path'] + '/', '')
            print(f"      └── 📁 {rel_path}/")
    
    if len(depth_0_dirs) > 20:
        print(f"   ... and {len(depth_0_dirs) - 20} more directories")
    
    # Analyze screenshot locations
    if structure['screenshot_candidates']:
        print(f"\n📸 Screenshot Candidate Locations:")
        dir_analysis = analyze_screenshot_directories(structure)
        
        for directory, count in list(dir_analysis.items())[:10]:
            print(f"   {count:4d} files in: {directory}")
        
        # Show sample filenames from top directories
        print(f"\n📝 Sample Screenshot Filenames:")
        shown_dirs = set()
        for candidate in structure['screenshot_candidates'][:15]:
            if candidate['directory'] not in shown_dirs or len(shown_dirs) < 3:
                print(f"   {candidate['name']}")
                print(f"      → {candidate['directory']}")
                shown_dirs.add(candidate['directory'])
    
    # Special focus: Look for Samsung and iOS patterns
    print(f"\n🔍 Device-Specific Patterns:")
    
    samsung_screenshots = [c for c in structure['screenshot_candidates'] 
                          if 'Screenshot_' in c['name'] and 'Samsung' in c['directory']]
    print(f"   Samsung S23 Screenshots: {len(samsung_screenshots)}")
    if samsung_screenshots:
        print(f"      Location: {samsung_screenshots[0]['directory']}")
    
    ios_screenshots = [c for c in structure['screenshot_candidates'] 
                      if c['name'].startswith('IMG_') or 'Camera Roll' in c['directory']]
    print(f"   iOS Screenshots: {len(ios_screenshots)}")
    if ios_screenshots:
        unique_dirs = set(c['directory'] for c in ios_screenshots)
        for dir_path in list(unique_dirs)[:3]:
            count = sum(1 for c in ios_screenshots if c['directory'] == dir_path)
            print(f"      {count} files in: {dir_path}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
