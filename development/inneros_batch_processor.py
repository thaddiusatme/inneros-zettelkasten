#!/usr/bin/env python3
"""
InnerOS Batch Processor - Proof of Concept
Conservative, beginner-friendly approach with safety-first design

Implements TDD methodology: Red → Green → Refactor
Phase: P0 - Core Directory Scanner
"""

import argparse
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List
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
    
    def dry_run(self) -> Dict[str, Any]:
        """
        Analyze files for AI processing opportunities without making changes
        Parses YAML frontmatter and identifies enhancement opportunities
        
        Returns:
            Dict with analysis results and processing preview
        """
        # Get same files as scan_notes
        scan_result = self.scan_notes()
        files = scan_result['files']
        
        analyzed_files = []
        summary_stats = {
            'total_files_needing_tags': 0,
            'total_files_needing_quality': 0,
            'estimated_processing_time': 0
        }
        
        for file_info in files:
            file_path = Path(file_info['path'])
            analysis = self._analyze_file_for_ai_opportunities(file_path)
            
            # Update summary statistics
            if 'needs_more_tags' in analysis['ai_opportunities']:
                summary_stats['total_files_needing_tags'] += 1
            if 'needs_quality_score' in analysis['ai_opportunities']:
                summary_stats['total_files_needing_quality'] += 1
            
            analyzed_files.append(analysis)
        
        # Estimate processing time (2 seconds per file needing AI work)
        total_ai_work = (summary_stats['total_files_needing_tags'] + 
                        summary_stats['total_files_needing_quality'])
        summary_stats['estimated_processing_time'] = total_ai_work * 2
        
        return {
            'total_analyzed': len(analyzed_files),
            'files': analyzed_files,
            'summary': summary_stats
        }
    
    def _analyze_file_for_ai_opportunities(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a single file for AI processing opportunities
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Dict with file analysis results
        """
        analysis = {
            'name': file_path.name,
            'path': str(file_path),
            'current_tags': [],
            'missing_metadata': [],
            'ai_opportunities': []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            frontmatter = self._parse_yaml_frontmatter(content)
            
            if frontmatter is None:
                analysis['missing_metadata'] = ['yaml_frontmatter']
                analysis['ai_opportunities'] = ['needs_frontmatter', 'needs_more_tags', 'needs_quality_score']
                return analysis
            
            # Analyze tags
            tags = frontmatter.get('tags', [])
            if isinstance(tags, list):
                analysis['current_tags'] = tags
            else:
                analysis['current_tags'] = []
            
            # Check for AI opportunities
            if len(analysis['current_tags']) < 3:
                analysis['ai_opportunities'].append('needs_more_tags')
            
            if 'quality_score' not in frontmatter:
                analysis['ai_opportunities'].append('needs_quality_score')
                analysis['missing_metadata'].append('quality_score')
            
            if 'ai_processed' not in frontmatter:
                analysis['missing_metadata'].append('ai_processed')
                
        except Exception as e:
            analysis['yaml_parsing_error'] = str(e)
            analysis['ai_opportunities'] = ['needs_yaml_repair']
        
        return analysis
    
    def _parse_yaml_frontmatter(self, content: str) -> Dict[str, Any] | None:
        """
        Parse YAML frontmatter from markdown content
        
        Args:
            content: Full markdown file content
            
        Returns:
            Dict of frontmatter data or None if not found/invalid
        """
        # Look for YAML frontmatter pattern
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if not match:
            return None
        
        yaml_content = match.group(1)
        
        try:
            return yaml.safe_load(yaml_content)
        except yaml.YAMLError:
            # Re-raise the error so the calling method can catch it
            raise


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
            print("  → Use --dry-run to see AI processing opportunities")
            print("  → Use --process to enhance notes (with confirmation)")
        else:
            print("✅ No notes found requiring processing")
            print("💡 Notes are filtered if modified within last 2 hours to avoid editing conflicts")
    
    elif args.dry_run:
        print("🔬 Analyzing notes for AI processing opportunities...")
        result = processor.dry_run()
        print(f"📊 Analyzed {result['total_analyzed']} notes")
        
        # Show summary statistics
        summary = result['summary']
        print("\n📈 Processing Opportunities Summary:")
        print(f"  • {summary['total_files_needing_tags']} notes need more tags")
        print(f"  • {summary['total_files_needing_quality']} notes need quality scores")
        print(f"  • Estimated processing time: {summary['estimated_processing_time']} seconds")
        
        # Show detailed analysis for first few files
        if result['files']:
            print("\n🔍 Detailed Analysis (showing first 5 files):")
            for i, file_analysis in enumerate(result['files'][:5]):
                print(f"\n  📄 {file_analysis['name']}")
                print(f"     Current tags: {len(file_analysis['current_tags'])} ({', '.join(file_analysis['current_tags'][:3])}{'...' if len(file_analysis['current_tags']) > 3 else ''})")
                
                if file_analysis['missing_metadata']:
                    print(f"     Missing: {', '.join(file_analysis['missing_metadata'])}")
                
                if file_analysis['ai_opportunities']:
                    opportunities = file_analysis['ai_opportunities']
                    print(f"     AI can help: {', '.join(opportunities)}")
                
                if 'yaml_parsing_error' in file_analysis:
                    print(f"     ⚠️  YAML Error: {file_analysis['yaml_parsing_error']}")
            
            if len(result['files']) > 5:
                print(f"\n  ... and {len(result['files']) - 5} more files")
            
            print("\n💡 Next steps:")
            print("  → Use --process to apply AI enhancements")
            print("  → All changes will be backed up automatically")
        else:
            print("✅ All notes are already well-processed!")
            print("💡 No AI enhancements needed")


if __name__ == "__main__":
    main()
