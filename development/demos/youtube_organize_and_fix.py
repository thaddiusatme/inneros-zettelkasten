#!/usr/bin/env python3
"""
YouTube Notes Organization & Frontmatter Fix Script

Migrates YouTube notes to Inbox/YouTube/ subdirectory and fixes empty video_id frontmatter.

Features:
- Identifies YouTube notes via 'source: youtube' in frontmatter
- Moves notes to knowledge/Inbox/YouTube/
- Extracts video_id from body content when frontmatter is empty
- Updates frontmatter with extracted video_id
- Generates comprehensive migration report
- Dry-run mode for safe testing

Usage:
    python3 youtube_organize_and_fix.py --dry-run  # Test without changes
    python3 youtube_organize_and_fix.py            # Execute migration
"""

import sys
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.frontmatter import parse_frontmatter, build_frontmatter


class YouTubeMigrationReport:
    """Tracks migration statistics and generates reports"""
    
    def __init__(self):
        self.files_found = 0
        self.files_moved = 0
        self.frontmatter_fixed = 0
        self.already_in_youtube = 0
        self.errors = []
        self.processed_files = []
    
    def add_success(self, filename: str, moved: bool, fixed: bool):
        """Record successful processing"""
        self.processed_files.append({
            'file': filename,
            'moved': moved,
            'frontmatter_fixed': fixed,
            'status': 'success'
        })
        if moved:
            self.files_moved += 1
        if fixed:
            self.frontmatter_fixed += 1
    
    def add_error(self, filename: str, error: str):
        """Record processing error"""
        self.errors.append({'file': filename, 'error': error})
        self.processed_files.append({
            'file': filename,
            'status': 'error',
            'error': error
        })
    
    def generate_report(self) -> str:
        """Generate human-readable migration report"""
        report = []
        report.append("=" * 70)
        report.append("YOUTUBE NOTES MIGRATION REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY:")
        report.append(f"  YouTube notes found: {self.files_found}")
        report.append(f"  Files moved to Inbox/YouTube/: {self.files_moved}")
        report.append(f"  Frontmatter fields fixed: {self.frontmatter_fixed}")
        report.append(f"  Already in YouTube subdirectory: {self.already_in_youtube}")
        report.append(f"  Errors encountered: {len(self.errors)}")
        report.append("")
        
        # Processed files
        if self.processed_files:
            report.append("PROCESSED FILES:")
            for item in self.processed_files:
                status_icon = "✅" if item['status'] == 'success' else "❌"
                actions = []
                if item.get('moved'):
                    actions.append("MOVED")
                if item.get('frontmatter_fixed'):
                    actions.append("FIXED")
                action_str = ", ".join(actions) if actions else "NO CHANGES"
                report.append(f"  {status_icon} {item['file']}: {action_str}")
        
        # Errors
        if self.errors:
            report.append("")
            report.append("ERRORS:")
            for error in self.errors:
                report.append(f"  ❌ {error['file']}: {error['error']}")
        
        report.append("")
        report.append("=" * 70)
        return "\n".join(report)


class YouTubeNoteMigrator:
    """Handles YouTube note migration and frontmatter fixing"""
    
    VIDEO_ID_PATTERN = r'Video ID[*:\s]+`?([a-zA-Z0-9_-]+)`?'
    
    def __init__(self, vault_path: Path, dry_run: bool = False):
        self.vault_path = vault_path
        self.inbox_path = vault_path / 'knowledge' / 'Inbox'
        self.youtube_path = self.inbox_path / 'YouTube'
        self.dry_run = dry_run
        self.report = YouTubeMigrationReport()
    
    def find_youtube_notes(self) -> List[Path]:
        """Find all YouTube notes in Inbox (recursive)"""
        youtube_notes = []
        
        # First, collect all markdown files
        print("  Collecting markdown files...")
        all_md_files = list(self.inbox_path.rglob('*.md'))
        print(f"  Found {len(all_md_files)} total markdown files")
        
        print("  Scanning for YouTube notes...")
        for i, md_file in enumerate(all_md_files, 1):
            if i % 10 == 0:
                print(f"    Progress: {i}/{len(all_md_files)}", end='\r')
            
            try:
                content = md_file.read_text(encoding='utf-8')
                frontmatter, _ = parse_frontmatter(content)
                
                if frontmatter.get('source') == 'youtube':
                    youtube_notes.append(md_file)
            except Exception as e:
                print(f"\n  Warning: Could not parse {md_file.name}: {e}")
        
        print(f"    Progress: {len(all_md_files)}/{len(all_md_files)} - Complete!")
        return youtube_notes
    
    def extract_video_id_from_body(self, content: str) -> Optional[str]:
        """Extract video_id from note body content"""
        match = re.search(self.VIDEO_ID_PATTERN, content)
        if match:
            return match.group(1)
        return None
    
    def needs_frontmatter_fix(self, frontmatter: Dict) -> bool:
        """Check if video_id frontmatter needs fixing"""
        video_id = frontmatter.get('video_id')
        return not video_id or video_id.strip() == ''
    
    def process_note(self, note_path: Path) -> Tuple[bool, bool]:
        """
        Process a single YouTube note.
        
        Returns:
            (moved, frontmatter_fixed) tuple
        """
        moved = False
        frontmatter_fixed = False
        
        try:
            # Read note content
            content = note_path.read_text(encoding='utf-8')
            frontmatter, body = parse_frontmatter(content)
            
            # Check if frontmatter needs fixing
            needs_fix = self.needs_frontmatter_fix(frontmatter)
            
            if needs_fix:
                # Extract video_id from body
                video_id = self.extract_video_id_from_body(content)
                
                if video_id:
                    print(f"  → Extracted video_id: {video_id}")
                    if not self.dry_run:
                        # Update frontmatter
                        frontmatter['video_id'] = video_id
                        updated_content = build_frontmatter(frontmatter, body)
                        note_path.write_text(updated_content, encoding='utf-8')
                    frontmatter_fixed = True
                else:
                    print(f"  ⚠️  Could not extract video_id from body")
            
            # Check if file needs moving
            if not note_path.parent.name == 'YouTube':
                target_path = self.youtube_path / note_path.name
                
                # Check for filename conflicts
                if target_path.exists():
                    print(f"  ⚠️  Target already exists: {target_path.name}")
                    return moved, frontmatter_fixed
                
                print(f"  → Moving to Inbox/YouTube/")
                if not self.dry_run:
                    # Ensure YouTube directory exists
                    self.youtube_path.mkdir(parents=True, exist_ok=True)
                    # Move file
                    shutil.move(str(note_path), str(target_path))
                moved = True
            else:
                self.report.already_in_youtube += 1
            
            return moved, frontmatter_fixed
            
        except Exception as e:
            raise Exception(f"Processing failed: {e}")
    
    def run(self):
        """Execute migration"""
        print("\n" + "=" * 70)
        print("YOUTUBE NOTES MIGRATION & FRONTMATTER FIX")
        print("=" * 70)
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No changes will be made\n")
        else:
            print("\n✅ LIVE MODE - Changes will be applied\n")
        
        # Find YouTube notes
        print("Scanning for YouTube notes...")
        youtube_notes = self.find_youtube_notes()
        self.report.files_found = len(youtube_notes)
        
        print(f"Found {len(youtube_notes)} YouTube notes\n")
        
        if not youtube_notes:
            print("No YouTube notes found. Nothing to migrate.")
            return self.report
        
        # Process each note
        for note_path in youtube_notes:
            print(f"\nProcessing: {note_path.name}")
            
            try:
                moved, fixed = self.process_note(note_path)
                self.report.add_success(note_path.name, moved, fixed)
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.report.add_error(note_path.name, str(e))
        
        # Print final report
        print("\n" + self.report.generate_report())
        
        return self.report


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate YouTube notes to subdirectory and fix frontmatter'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--vault-path',
        type=Path,
        default=Path.cwd(),
        help='Path to vault root (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Validate vault path
    if not (args.vault_path / 'knowledge' / 'Inbox').exists():
        print(f"❌ Error: knowledge/Inbox not found at {args.vault_path}")
        print("   Please run this script from the vault root or specify --vault-path")
        sys.exit(1)
    
    # Run migration
    migrator = YouTubeNoteMigrator(args.vault_path, dry_run=args.dry_run)
    migrator.run()


if __name__ == '__main__':
    main()
