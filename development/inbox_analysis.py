#!/usr/bin/env python3
"""
Inbox Analysis Script - Knowledge Base Cleanup Phase 2

Scans knowledge/Inbox/ to identify:
- Orphaned notes (ai_processed: true, status: inbox)
- Notes missing required frontmatter (type:, created:)
- Old unprocessed captures (>6 months)
- High-quality notes ready for promotion (quality_score >= 0.7)

Generates a detailed YAML report for decision-making.
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yaml
import re

# Vault root
VAULT_ROOT = Path(__file__).parent.parent
INBOX_DIR = VAULT_ROOT / "knowledge" / "Inbox"


def parse_frontmatter(content: str) -> Dict:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return {}
    
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def analyze_note(note_path: Path) -> Dict:
    """Analyze a single note and return its metadata + analysis."""
    try:
        content = note_path.read_text(encoding='utf-8')
        frontmatter = parse_frontmatter(content)
        
        # Extract key fields
        status = frontmatter.get('status', 'unknown')
        ai_processed = frontmatter.get('ai_processed', False)
        note_type = frontmatter.get('type', None)
        created = frontmatter.get('created', None)
        quality_score = frontmatter.get('quality_score', 0.0)
        
        # Determine issues
        issues = []
        recommendations = []
        
        # Check for orphaned notes
        if ai_processed and status == 'inbox':
            issues.append('orphaned_note')
            recommendations.append('repair_status_to_promoted')
        
        # Check for missing type
        if not note_type:
            issues.append('missing_type_field')
            recommendations.append('infer_type_from_filename')
        
        # Check age (if created field exists)
        age_days = None
        if created:
            try:
                # Handle various date formats
                created_date = None
                if isinstance(created, str):
                    for fmt in ['%Y-%m-%d %H:%M', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S']:
                        try:
                            created_date = datetime.strptime(created, fmt)
                            break
                        except ValueError:
                            continue
                
                if created_date:
                    age_days = (datetime.now() - created_date).days
                    
                    if age_days > 180 and not ai_processed:
                        issues.append('old_unprocessed')
                        recommendations.append('archive_or_process')
            except Exception:
                pass
        
        # Check if ready for promotion
        if quality_score >= 0.7 and status == 'promoted':
            recommendations.append('auto_promote_candidate')
        
        # Determine category
        if 'orphaned_note' in issues:
            category = 'orphaned'
        elif 'missing_type_field' in issues:
            category = 'needs_metadata_repair'
        elif 'old_unprocessed' in issues:
            category = 'aged_capture'
        elif not issues:
            category = 'active_capture'
        else:
            category = 'needs_review'
        
        return {
            'path': str(note_path.relative_to(VAULT_ROOT)),
            'status': status,
            'ai_processed': ai_processed,
            'type': note_type,
            'quality_score': quality_score,
            'created': str(created) if created else None,
            'age_days': age_days,
            'issues': issues,
            'recommendations': recommendations,
            'category': category,
            'file_size_kb': round(note_path.stat().st_size / 1024, 2)
        }
    
    except Exception as e:
        return {
            'path': str(note_path.relative_to(VAULT_ROOT)),
            'error': str(e),
            'category': 'error'
        }


def analyze_inbox() -> Dict:
    """Scan entire Inbox and generate analysis report."""
    
    if not INBOX_DIR.exists():
        return {'error': f'Inbox directory not found: {INBOX_DIR}'}
    
    all_notes = list(INBOX_DIR.glob('**/*.md'))
    
    # Analyze each note
    analyses = [analyze_note(note) for note in all_notes]
    
    # Group by category
    categories = {}
    for analysis in analyses:
        cat = analysis.get('category', 'unknown')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(analysis)
    
    # Generate summary
    summary = {
        'total_notes': len(all_notes),
        'scan_date': datetime.now().isoformat(),
        'inbox_path': str(INBOX_DIR.relative_to(VAULT_ROOT)),
        'categories': {
            cat: len(notes) for cat, notes in categories.items()
        }
    }
    
    return {
        'summary': summary,
        'categories': categories
    }


def main():
    """Main entry point."""
    print("📊 Analyzing knowledge/Inbox/...")
    print(f"   Path: {INBOX_DIR}")
    print()
    
    result = analyze_inbox()
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return 1
    
    # Print summary
    summary = result['summary']
    print("📈 Summary")
    print(f"   Total notes: {summary['total_notes']}")
    print(f"   Scan date: {summary['scan_date']}")
    print()
    
    print("📂 Categories:")
    for category, count in summary['categories'].items():
        print(f"   {category:.<30} {count:>3} notes")
    print()
    
    # Save detailed report
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = VAULT_ROOT / '.automation' / 'review_queue' / f'inbox-analysis-{timestamp}.yaml'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    
    print(f"💾 Detailed report saved to:")
    print(f"   {output_file.relative_to(VAULT_ROOT)}")
    print()
    
    # Print actionable summary
    categories = result['categories']
    
    if 'orphaned' in categories:
        print(f"⚠️  Found {len(categories['orphaned'])} orphaned notes (ai_processed: true, status: inbox)")
        print("   → Action: Run repair_orphaned_notes.py")
        print()
    
    if 'needs_metadata_repair' in categories:
        print(f"⚠️  Found {len(categories['needs_metadata_repair'])} notes missing type: field")
        print("   → Action: Run metadata_repair.py")
        print()
    
    if 'aged_capture' in categories:
        print(f"📅 Found {len(categories['aged_capture'])} old unprocessed captures (>6 months)")
        print("   → Action: Review for archival")
        print()
    
    if 'active_capture' in categories:
        print(f"✅ Found {len(categories['active_capture'])} active captures (looks good)")
        print()
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
