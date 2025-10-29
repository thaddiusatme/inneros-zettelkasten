#!/usr/bin/env python3
"""
Root Directory Analysis - Knowledge Base Cleanup Phase 2

Scans repository root and categorizes files for archival.
Generates decision log with routing recommendations.

Categories:
- Session/State files → Projects/COMPLETED-2025-10/
- Phase docs → Projects/COMPLETED-2025-10/
- Demo scripts → development/demos/ or archive
- Documentation → Keep or Projects/REFERENCE/
- Logs/Metrics → archive or delete
- Standard files → Keep (README, requirements, configs)
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import yaml
import os


class RootDirectoryAnalyzer:
    """Analyze repository root for cleanup recommendations."""
    
    # Files to always preserve
    PRESERVE_FILES = {
        'README.md',
        'INSTALLATION.md',
        'requirements.txt',
        'pyrightconfig.json',
        '.gitignore',
        '.gitignore-distribution',
        '.env.sample',
        'inneros',  # CLI executable
    }
    
    # Directories to exclude from analysis
    EXCLUDE_DIRS = {
        '.git', '.github', '.windsurf', '.vscode', '.obsidian',
        '__pycache__', '.pytest_cache', 'htmlcov',
        '.venv', 'web_ui_env', '.embedding_cache',
        'development', 'Projects', 'knowledge', 'scripts',
        'web_ui', 'knowledge-starter-pack',
        'Workflows', 'Reviews', 'Media', 'backups',
        'Fleeting Notes', 'Literature Notes', 'Permanent Notes',
    }
    
    # Patterns for categorization
    PATTERNS = {
        'session_state': [
            'CURRENT-STATE-', 'NEXT_SESSION_', 'NEXT_CHAT_',
        ],
        'phase_docs': [
            'PHASE-', 'PHASE2-', 'PHASE3-',
        ],
        'completion_docs': [
            '-COMPLETE-SUMMARY', '-COMPLETION-', '-FIX-SUMMARY',
        ],
        'demo_scripts': [
            'DEMO-', 'test_', 'archive_', 'continue_',
        ],
        'documentation': [
            'QUICK-START-', 'QUICK-REFERENCE', 'CLI-REFERENCE',
            'GETTING-STARTED', 'MIGRATION-GUIDE', 'FEATURE-STATUS',
            'CONNECTION-DISCOVERY',
        ],
        'logs': [
            '.log', '-profile.log',
        ],
        'metrics': [
            'orphan-metrics', 'analytics_report', 'watcher.log',
        ],
        'empty_files': [],  # Populated during scan
        'misc': [],  # Catch-all
    }
    
    def __init__(self, root_dir: Path):
        """Initialize analyzer."""
        self.root_dir = root_dir
        self.inventory = {
            'metadata': {
                'scan_date': datetime.now().isoformat(),
                'root_directory': str(root_dir),
                'total_files': 0,
            },
            'categories': {},
            'recommendations': {},
            'summary': {},
        }
    
    def scan(self) -> Dict:
        """Scan root directory and categorize files."""
        files_found = []
        
        # Scan root directory (no recursion)
        for item in self.root_dir.iterdir():
            # Skip directories
            if item.is_dir():
                if item.name not in self.EXCLUDE_DIRS:
                    # Note unexpected directories
                    pass
                continue
            
            # Skip hidden files (except specific ones)
            if item.name.startswith('.') and item.name not in self.PRESERVE_FILES:
                continue
            
            files_found.append(item)
        
        # Categorize files
        categorized = self._categorize_files(files_found)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(categorized)
        
        # Build inventory
        self.inventory['metadata']['total_files'] = len(files_found)
        self.inventory['categories'] = categorized
        self.inventory['recommendations'] = recommendations
        self.inventory['summary'] = self._generate_summary(categorized)
        
        return self.inventory
    
    def _categorize_files(self, files: List[Path]) -> Dict:
        """Categorize files by type."""
        categories = {
            'preserve': [],
            'session_state': [],
            'phase_docs': [],
            'completion_docs': [],
            'demo_scripts': [],
            'documentation': [],
            'logs': [],
            'metrics': [],
            'empty_files': [],
            'misc': [],
        }
        
        for file_path in files:
            filename = file_path.name
            
            # Check if preserve
            if filename in self.PRESERVE_FILES:
                categories['preserve'].append(self._file_info(file_path))
                continue
            
            # Check if empty
            if file_path.stat().st_size == 0:
                categories['empty_files'].append(self._file_info(file_path))
                continue
            
            # Pattern matching
            categorized = False
            for category, patterns in self.PATTERNS.items():
                if category in ['empty_files', 'misc']:
                    continue
                
                for pattern in patterns:
                    if pattern in filename:
                        categories[category].append(self._file_info(file_path))
                        categorized = True
                        break
                
                if categorized:
                    break
            
            # If no pattern matched, it's misc
            if not categorized:
                categories['misc'].append(self._file_info(file_path))
        
        return categories
    
    def _file_info(self, file_path: Path) -> Dict:
        """Extract file metadata."""
        stat = file_path.stat()
        return {
            'name': file_path.name,
            'path': str(file_path),
            'size_bytes': stat.st_size,
            'size_kb': round(stat.st_size / 1024, 2),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }
    
    def _generate_recommendations(self, categories: Dict) -> Dict:
        """Generate archival recommendations for each category."""
        recommendations = {}
        
        # Session state files → COMPLETED
        if categories['session_state']:
            recommendations['session_state'] = {
                'action': 'archive',
                'destination': 'Projects/COMPLETED-2025-10/',
                'reason': 'Historical session tracking files',
                'files': [f['name'] for f in categories['session_state']],
            }
        
        # Phase docs → COMPLETED
        if categories['phase_docs']:
            recommendations['phase_docs'] = {
                'action': 'archive',
                'destination': 'Projects/COMPLETED-2025-10/',
                'reason': 'Phase completion documentation',
                'files': [f['name'] for f in categories['phase_docs']],
            }
        
        # Completion docs → COMPLETED
        if categories['completion_docs']:
            recommendations['completion_docs'] = {
                'action': 'archive',
                'destination': 'Projects/COMPLETED-2025-10/',
                'reason': 'Completion summaries and fix reports',
                'files': [f['name'] for f in categories['completion_docs']],
            }
        
        # Demo scripts → development/demos or archive
        if categories['demo_scripts']:
            recommendations['demo_scripts'] = {
                'action': 'review',
                'destination': 'development/demos/ OR Projects/Archive/',
                'reason': 'Test/demo scripts - decide if still useful',
                'files': [f['name'] for f in categories['demo_scripts']],
            }
        
        # Documentation → Keep or REFERENCE
        if categories['documentation']:
            recommendations['documentation'] = {
                'action': 'keep_or_organize',
                'destination': 'Keep in root OR Projects/REFERENCE/',
                'reason': 'Active documentation - review for relevance',
                'files': [f['name'] for f in categories['documentation']],
            }
        
        # Logs → Delete or archive
        if categories['logs']:
            recommendations['logs'] = {
                'action': 'delete',
                'destination': 'N/A (or backups/ if needed)',
                'reason': 'Log files - generally safe to delete',
                'files': [f['name'] for f in categories['logs']],
            }
        
        # Metrics → Archive or delete
        if categories['metrics']:
            recommendations['metrics'] = {
                'action': 'archive',
                'destination': 'Projects/COMPLETED-2025-10/metrics/',
                'reason': 'Historical metrics - archive for reference',
                'files': [f['name'] for f in categories['metrics']],
            }
        
        # Empty files → Delete
        if categories['empty_files']:
            recommendations['empty_files'] = {
                'action': 'delete',
                'destination': 'N/A',
                'reason': 'Empty placeholder files - safe to delete',
                'files': [f['name'] for f in categories['empty_files']],
            }
        
        # Misc → Review
        if categories['misc']:
            recommendations['misc'] = {
                'action': 'review',
                'destination': 'TBD',
                'reason': 'Uncategorized files - manual review needed',
                'files': [f['name'] for f in categories['misc']],
            }
        
        return recommendations
    
    def _generate_summary(self, categories: Dict) -> Dict:
        """Generate summary statistics."""
        total_files = sum(len(files) for files in categories.values())
        
        return {
            'total_files_scanned': total_files,
            'preserve': len(categories['preserve']),
            'archive_candidates': (
                len(categories['session_state']) +
                len(categories['phase_docs']) +
                len(categories['completion_docs'])
            ),
            'delete_candidates': (
                len(categories['empty_files']) +
                len(categories['logs'])
            ),
            'review_needed': (
                len(categories['demo_scripts']) +
                len(categories['documentation']) +
                len(categories['misc'])
            ),
            'metrics_to_archive': len(categories['metrics']),
        }
    
    def save_report(self, output_path: Path) -> None:
        """Save inventory to YAML."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            yaml.dump(self.inventory, f, default_flow_style=False, sort_keys=False)
        
        print(f"💾 Report saved to: {output_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze repository root for cleanup'
    )
    parser.add_argument(
        '--root-dir',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Repository root directory (default: parent of development/)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output path for YAML report'
    )
    
    args = parser.parse_args()
    
    print("🔍 Root Directory Analysis - InnerOS Zettelkasten")
    print(f"   Scanning: {args.root_dir}")
    print()
    
    # Run analysis
    analyzer = RootDirectoryAnalyzer(root_dir=args.root_dir)
    inventory = analyzer.scan()
    
    # Print summary
    print("📊 Summary")
    print(f"   Total files: {inventory['summary']['total_files_scanned']}")
    print(f"   Preserve: {inventory['summary']['preserve']}")
    print(f"   Archive candidates: {inventory['summary']['archive_candidates']}")
    print(f"   Delete candidates: {inventory['summary']['delete_candidates']}")
    print(f"   Review needed: {inventory['summary']['review_needed']}")
    print(f"   Metrics to archive: {inventory['summary']['metrics_to_archive']}")
    print()
    
    # Save report
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        output_path = Path('.automation/review_queue') / f'root-inventory-{timestamp}.yaml'
    
    analyzer.save_report(output_path)
    
    print("✅ Analysis complete")
    print()
    print("Next steps:")
    print("  1. Review the YAML report")
    print("  2. Create decision log for approved moves")
    print("  3. Execute archival with cleanup_file_mover.py")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
