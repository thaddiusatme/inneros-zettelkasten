#!/usr/bin/env python3
"""
InnerOS Batch Processor - Proof of Concept
Conservative, beginner-friendly approach with safety-first design

Implements TDD methodology: Red → Green → Refactor
Phase: P0 - Core Directory Scanner
"""

import argparse
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Import our production-ready backup system
try:
    from src.utils.directory_organizer import DirectoryOrganizer, BackupError
    from src.ai.workflow_manager import WorkflowManager
except ImportError:
    # Handle import during testing or standalone execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from utils.directory_organizer import DirectoryOrganizer, BackupError
    from ai.workflow_manager import WorkflowManager


class BatchProcessor:
    """
    Simple batch processor for InnerOS Zettelkasten notes
    Focuses on safety and manual control over automation
    """
    
    def __init__(self, base_dir: str = "."):
        """
        Initialize batch processor with target directories and backup system
        
        Args:
            base_dir: Base directory containing knowledge/ folder
        """
        self.base_dir = Path(base_dir)
        
        # Find knowledge directory (handle development/ execution)
        knowledge_path = self.base_dir / "knowledge"
        if not knowledge_path.exists():
            # Handle case where we're running from development/ directory
            sibling_knowledge = Path("../knowledge").resolve()
            if sibling_knowledge.exists():
                knowledge_path = sibling_knowledge
        
        self.target_dirs = [
            knowledge_path / "Inbox",
            knowledge_path / "Fleeting Notes"
        ]
        
        # Initialize production-ready backup system
        self.backup_system = DirectoryOrganizer(
            vault_root=str(knowledge_path)
            # backup_root defaults to ~/backups/{vault_name}/ when None
        )
        
        # Initialize AI workflow manager for processing
        self.workflow_manager = WorkflowManager(str(knowledge_path))
    
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
    
    # === BACKUP SYSTEM INTEGRATION ===
    
    def create_backup(self) -> str:
        """
        Create timestamped backup before processing operations
        
        Returns:
            str: Path to created backup directory
            
        Raises:
            BackupError: If backup creation fails
        """
        return self.backup_system.create_backup()
    
    def rollback(self, backup_path: str) -> None:
        """
        Rollback to previous backup state
        
        Args:
            backup_path: Path to backup directory to restore from
            
        Raises:
            BackupError: If rollback fails
        """
        self.backup_system.rollback(backup_path)
    
    def process_notes(self, create_backup: bool = True, limit: int | None = None) -> Dict[str, Any]:
        """
        Process notes with AI enhancement
        Creates backup first if requested for safety
        
        Args:
            create_backup: Whether to create backup before processing
            limit: Maximum number of notes to process
            
        Returns:
            Dict with processing results
        """
        start_time = datetime.now()
        
        result = {
            'processed_count': 0,
            'backup_created': False,
            'backup_path': None,
            'ai_enhanced_files': [],
            'errors': [],
            'processing_time': 0.0
        }
        
        if create_backup:
            try:
                backup_path = self.create_backup()
                result['backup_created'] = True
                result['backup_path'] = backup_path
                print(f"✅ Backup created: {backup_path}")
            except BackupError as e:
                raise BackupError(f"Cannot proceed without backup: {e}")
        
        # Get files that need processing
        scan_result = self.scan_notes()
        files_to_process = scan_result['files']
        
        # Apply limit if specified
        if limit is not None:
            files_to_process = files_to_process[:limit]
        
        # Process each file with AI enhancement
        for file_info in files_to_process:
            try:
                file_path = file_info['path']
                
                # Use WorkflowManager to process the note
                ai_result = self.workflow_manager.process_inbox_note(file_path)
                
                if "error" not in ai_result:
                    result['processed_count'] += 1
                    
                    # Extract enhancement details
                    enhanced_info = {
                        'name': file_info['name'],
                        'path': file_path,
                        'tags_added': [],
                        'quality_score': ai_result.get('quality_score', 0.0)
                    }
                    
                    # Check if tags were added
                    if 'processing' in ai_result and 'tags' in ai_result['processing']:
                        tags_info = ai_result['processing']['tags']
                        if isinstance(tags_info, dict) and 'added' in tags_info:
                            enhanced_info['tags_added'] = tags_info['added']
                    
                    result['ai_enhanced_files'].append(enhanced_info)
                else:
                    result['errors'].append({
                        'file': file_info['name'],
                        'error': ai_result['error']
                    })
                    
            except Exception as e:
                result['errors'].append({
                    'file': file_info['name'],
                    'error': str(e)
                })
        
        # Calculate processing time
        end_time = datetime.now()
        result['processing_time'] = (end_time - start_time).total_seconds()
        
        return result


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
    parser.add_argument(
        '--backup',
        action='store_true', 
        help='Create backup of knowledge directory'
    )
    parser.add_argument(
        '--rollback',
        type=str,
        metavar='BACKUP_PATH',
        help='Rollback to specified backup directory'
    )
    parser.add_argument(
        '--ai-process',
        action='store_true',
        help='Process notes with AI enhancement (includes backup)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        metavar='N',
        help='Limit processing to N files (useful for testing)'
    )
    
    args = parser.parse_args()
    
    if not any([args.scan, args.dry_run, args.process, args.backup, args.rollback, args.ai_process]):
        parser.print_help()
        return
    
    processor = BatchProcessor()
    
    if args.backup:
        print("💾 Creating backup of knowledge directory...")
        try:
            backup_path = processor.create_backup()
            print("✅ Backup created successfully!")
            print(f"📂 Location: {backup_path}")
            print(f"\n💡 To rollback: python {sys.argv[0]} --rollback '{backup_path}'")
        except BackupError as e:
            print(f"❌ Backup failed: {e}")
            return
    
    elif args.rollback:
        backup_path = args.rollback
        print("⚠️  WARNING: This will replace your current knowledge directory!")
        print(f"📂 Rollback source: {backup_path}")
        
        confirmation = input("\n🤔 Are you sure you want to rollback? (yes/no): ").lower().strip()
        if confirmation not in ['yes', 'y']:
            print("❌ Rollback cancelled")
            return
            
        try:
            processor.rollback(backup_path)
            print("✅ Rollback completed successfully!")
            print("🔄 Your knowledge directory has been restored to the backup state")
        except BackupError as e:
            print(f"❌ Rollback failed: {e}")
            return
    
    elif args.scan:
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
            
            print("💡 Next steps:")
            print("  → Use --ai-process to apply AI enhancements")
            print("  → All changes will be backed up automatically")
        else:
            print("✅ All notes are already well-processed!")
            print("💡 No AI enhancements needed")
    
    elif args.ai_process:
        print("🤖 Processing notes with AI enhancement...")
        limit = args.limit if hasattr(args, 'limit') and args.limit else None
        
        try:
            result = processor.process_notes(create_backup=True, limit=limit)
            
            # Display results
            print(f"✅ AI processing completed!")
            print(f"📊 Processed {result['processed_count']} notes")
            print(f"⏱️  Processing time: {result['processing_time']:.1f} seconds")
            
            if result['backup_created']:
                print(f"💾 Backup: {result['backup_path']}")
            
            # Show enhanced files
            if result['ai_enhanced_files']:
                print(f"\n🔍 Enhanced Files:")
                for enhanced in result['ai_enhanced_files']:
                    tags_count = len(enhanced['tags_added']) if enhanced['tags_added'] else 0
                    quality = enhanced['quality_score']
                    print(f"  • {enhanced['name']}")
                    print(f"    Quality: {quality:.2f} | Tags added: {tags_count}")
            
            # Show errors if any
            if result['errors']:
                print(f"\n⚠️  Errors ({len(result['errors'])}):")
                for error in result['errors'][:3]:  # Show first 3 errors
                    print(f"  • {error['file']}: {error['error']}")
                if len(result['errors']) > 3:
                    print(f"  ... and {len(result['errors']) - 3} more errors")
                    
            print(f"\n💡 Rollback command: python {sys.argv[0]} --rollback '{result['backup_path']}'")
            
        except Exception as e:
            print(f"❌ AI processing failed: {e}")
            return
