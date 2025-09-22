#!/usr/bin/env python3
"""
InnerOS Batch Processor - Proof of Concept
Conservative, beginner-friendly approach with safety-first design

Implements TDD methodology: Red → Green → Refactor
Phase: P0 - Core Directory Scanner
"""

import argparse
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta


class BatchProcessor:
    """
    Simple batch processor for InnerOS Zettelkasten notes
    Focuses on safety and manual control over automation
    """
    
    def __init__(self, base_dir: str = "."):
        """
        Initialize batch processor with target directories
        
        Args:
            base_dir: Base directory containing knowledge/ folder
        """
        self.base_dir = Path(base_dir)
        self.target_dirs = [
            self.base_dir / "knowledge" / "Inbox",
            self.base_dir / "knowledge" / "Fleeting Notes"
        ]
    
    def scan_notes(self) -> Dict[str, Any]:
        """
        Scan target directories for processable markdown files
        Filters out recently modified files (< 2 hours) to avoid editing conflicts
        
        Returns:
            Dict with 'total_count' and 'files' list containing file details
        """
        files = []
        cutoff_time = datetime.now() - timedelta(hours=2)
        
        for target_dir in self.target_dirs:
            if not target_dir.exists():
                continue
                
            # Find all .md files in this directory
            for md_file in target_dir.glob("*.md"):
                # Skip recently modified files
                modified_time = datetime.fromtimestamp(md_file.stat().st_mtime)
                if modified_time > cutoff_time:
                    continue
                
                # Collect file information
                file_info = {
                    'name': md_file.name,
                    'path': str(md_file),
                    'size': md_file.stat().st_size,
                    'modified': modified_time.isoformat()
                }
                files.append(file_info)
        
        return {
            'total_count': len(files),
            'files': files
        }


def main():
    """Command line interface for batch processor"""
    parser = argparse.ArgumentParser(
        description="InnerOS Batch Processor - Safe AI-powered note enhancement"
    )
    parser.add_argument(
        '--scan', 
        action='store_true',
        help='Scan directories and show what would be processed'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true', 
        help='Show detailed processing plan without making changes'
    )
    parser.add_argument(
        '--process',
        action='store_true',
        help='Actually process notes (requires confirmation)'
    )
    
    args = parser.parse_args()
    
    if not any([args.scan, args.dry_run, args.process]):
        parser.print_help()
        return
    
    processor = BatchProcessor()
    
    if args.scan:
        print("🔍 Scanning for processable notes...")
        result = processor.scan_notes()
        print(f"📊 Found {result['total_count']} notes ready for processing")
        
        if result['files']:
            print("\n📋 Files to process:")
            for file_info in result['files']:
                # Extract directory name for context
                path_parts = file_info['path'].split('/')
                directory = path_parts[-2] if len(path_parts) > 1 else "unknown"
                size_kb = file_info['size'] / 1024
                print(f"  • {file_info['name']} ({directory}/) - {size_kb:.1f}KB")
            
            print("\n💡 Next steps:")
            print("  → Use --dry-run to see processing details")
            print("  → Use --process to enhance notes (with confirmation)")
        else:
            print("✅ No notes found requiring processing")
            print("💡 Notes are filtered if modified within last 2 hours to avoid editing conflicts")


if __name__ == "__main__":
    main()
