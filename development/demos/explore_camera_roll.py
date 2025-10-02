#!/usr/bin/env python3
"""
Deep exploration of Camera Roll 1 directory to find iPad screenshots
"""

import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def analyze_camera_roll(base_path: Path) -> dict:
    """Thoroughly analyze Camera Roll 1 directory"""
    
    results = {
        'total_files': 0,
        'total_dirs': 0,
        'files_by_year': defaultdict(list),
        'files_by_extension': defaultdict(int),
        'screenshot_candidates': [],
        'all_files': []
    }
    
    print(f"📁 Scanning: {base_path}")
    print("=" * 80)
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(base_path):
        root_path = Path(root)
        results['total_dirs'] += len(dirs)
        
        for file in files:
            # Skip hidden files
            if file.startswith('.'):
                continue
            
            file_path = root_path / file
            results['total_files'] += 1
            
            # Get file info
            try:
                stat = file_path.stat()
                file_info = {
                    'name': file,
                    'path': str(file_path.relative_to(base_path)),
                    'full_path': str(file_path),
                    'size_mb': stat.st_size / (1024 * 1024),
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'extension': file_path.suffix.lower()
                }
                
                results['all_files'].append(file_info)
                
                # Track by extension
                ext = file_path.suffix.lower()
                results['files_by_extension'][ext] += 1
                
                # Determine year from path or filename
                year = None
                if '/2024/' in str(file_path):
                    year = '2024'
                elif '/2025/' in str(file_path):
                    year = '2025'
                elif file.startswith('2024'):
                    year = '2024'
                elif file.startswith('2025'):
                    year = '2025'
                
                if year:
                    results['files_by_year'][year].append(file_info)
                
                # Identify screenshot candidates
                name_lower = file.lower()
                if ext in ['.png', '.jpg', '.jpeg']:
                    # iOS naming patterns
                    if (name_lower.startswith('img_') or 
                        'screenshot' in name_lower or
                        'screen' in name_lower or
                        name_lower.startswith('photo_')):
                        results['screenshot_candidates'].append(file_info)
                
            except Exception as e:
                print(f"⚠️  Error processing {file}: {e}")
    
    return results


def display_results(results: dict):
    """Display comprehensive analysis results"""
    
    print("\n" + "=" * 80)
    print("📊 ANALYSIS RESULTS")
    print("=" * 80)
    
    print(f"\nTotal files: {results['total_files']}")
    print(f"Total subdirectories: {results['total_dirs']}")
    print(f"Screenshot candidates: {len(results['screenshot_candidates'])}")
    
    # Files by year
    print("\n📅 Files by Year:")
    for year in sorted(results['files_by_year'].keys()):
        files = results['files_by_year'][year]
        total_size = sum(f['size_mb'] for f in files)
        print(f"   {year}: {len(files)} files ({total_size:.1f} MB)")
    
    # Files by extension
    print("\n📋 Files by Extension:")
    for ext, count in sorted(results['files_by_extension'].items(), key=lambda x: x[1], reverse=True):
        if ext:
            print(f"   {ext}: {count} files")
    
    # Screenshot candidates
    if results['screenshot_candidates']:
        print(f"\n📸 Screenshot Candidates ({len(results['screenshot_candidates'])} total):")
        
        # Group by year
        by_year = defaultdict(list)
        for sc in results['screenshot_candidates']:
            if '/2024/' in sc['path']:
                by_year['2024'].append(sc)
            elif '/2025/' in sc['path']:
                by_year['2025'].append(sc)
            else:
                by_year['other'].append(sc)
        
        for year in sorted(by_year.keys()):
            screenshots = by_year[year]
            if screenshots:
                print(f"\n   {year} ({len(screenshots)} files):")
                for sc in screenshots[:10]:  # Show first 10
                    print(f"      {sc['name']} ({sc['size_mb']:.2f} MB)")
                if len(screenshots) > 10:
                    print(f"      ... and {len(screenshots) - 10} more")
    
    # Sample file listing
    print(f"\n📝 Sample Files from Camera Roll 1:")
    for file_info in results['all_files'][:20]:
        print(f"   {file_info['name']}")
        print(f"      → {file_info['path']}")
    
    if len(results['all_files']) > 20:
        print(f"   ... and {len(results['all_files']) - 20} more files")
    
    # Device detection
    print(f"\n🔍 Device Detection:")
    
    # Look for iOS patterns
    ios_files = [f for f in results['all_files'] if f['name'].startswith('IMG_') or f['name'].startswith('Photo_')]
    print(f"   iOS-style filenames (IMG_*, Photo_*): {len(ios_files)}")
    
    # Look for iPad-specific patterns
    ipad_screenshots = [f for f in results['screenshot_candidates'] if 'ipad' in f['name'].lower()]
    print(f"   Explicit 'iPad' in filename: {len(ipad_screenshots)}")
    
    # DJI drone photos
    dji_files = [f for f in results['all_files'] if f['name'].startswith('DJI_')]
    print(f"   DJI drone photos: {len(dji_files)}")
    
    # Videos
    video_files = [f for f in results['all_files'] if f['extension'] in ['.mp4', '.mov', '.avi']]
    print(f"   Video files: {len(video_files)}")
    
    print("\n" + "=" * 80)


def main():
    camera_roll_path = Path("/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Camera Roll 1")
    
    print("=" * 80)
    print("🔍 Camera Roll 1 Deep Analysis")
    print("=" * 80)
    
    if not camera_roll_path.exists():
        print(f"\n❌ Path not found: {camera_roll_path}")
        return
    
    results = analyze_camera_roll(camera_roll_path)
    display_results(results)
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
