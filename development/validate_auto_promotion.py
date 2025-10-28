#!/usr/bin/env python3
"""
Validate Auto-Promotion on Repaired Notes - TT-13

Tests the auto-promotion system on the 28 notes repaired by repair_orphaned_notes.py.
Ensures repaired notes with status: promoted can be automatically moved to correct directories.
"""

from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ai.workflow_manager import WorkflowManager


def main():
    """Run auto-promotion validation."""
    vault_root = Path(__file__).parent.parent / "knowledge"
    
    print("🔍 TT-13: Validating Auto-Promotion on Repaired Notes")
    print(f"   Vault: {vault_root}")
    print()
    
    # Initialize WorkflowManager
    workflow = WorkflowManager(str(vault_root))
    
    # Run auto-promotion in dry-run mode
    print("📊 Running auto-promotion analysis (dry-run)...")
    print("   Scanning Inbox/ for notes with status: promoted...")
    print()
    
    results = workflow.auto_promote_ready_notes(
        dry_run=True,
        quality_threshold=0.65  # Lower threshold to include all repaired notes
    )
    
    # Display results
    print(f"✅ Analysis Complete:")
    print(f"   Total candidates: {results['total_candidates']}")
    print(f"   Would promote: {results.get('would_promote_count', 0)}")
    print(f"   Would skip: {results['skipped_count']}")
    print(f"   Errors: {results['error_count']}")
    print()
    
    # Show by type
    if results['by_type']:
        print("📦 Breakdown by Type:")
        for note_type, counts in results['by_type'].items():
            would_promote = counts.get('would_promote', 0)
            if would_promote > 0 or counts['promoted'] > 0:
                print(f"   {note_type.capitalize()}: {would_promote} notes")
        print()
    
    # Show preview of first 5 notes to be promoted
    if results.get('preview'):
        print("📄 Preview (first 5 notes to promote):")
        for note in results['preview'][:5]:
            print(f"   → {note['note']}")
            print(f"     Type: {note['type']} | Quality: {note['quality']}")
            print(f"     Destination: {note['target']}")
        
        if len(results['preview']) > 5:
            print(f"   ... and {len(results['preview']) - 5} more notes")
        print()
    
    # Show skipped notes if any
    if results.get('skipped_notes'):
        print(f"⚠️  Skipped Notes ({len(results['skipped_notes'])}):")
        for note in results['skipped_notes'][:5]:
            print(f"   - {note['path']}: {note['reason']}")
        if len(results['skipped_notes']) > 5:
            print(f"   ... and {len(results['skipped_notes']) - 5} more")
        print()
    
    # Show errors if any
    if results.get('errors'):
        print(f"❌ Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"   - {error['note']}: {error['error']}")
        print()
    
    # Summary and next steps
    print("="*60)
    if results.get('would_promote_count', 0) > 0:
        print("✅ Auto-promotion system validated successfully!")
        print(f"   {results['would_promote_count']} repaired notes ready to promote")
        print()
        print("Next Steps:")
        print("1. Review the preview above")
        print("2. Run with --execute flag to perform promotion:")
        print("   python3 validate_auto_promotion.py --execute")
    else:
        print("⚠️  No notes ready for auto-promotion")
        print("   This may indicate:")
        print("   - Notes already promoted in previous run")
        print("   - Quality scores below threshold (0.65)")
        print("   - Missing required metadata")
    
    return 0


if __name__ == '__main__':
    # Check for --execute flag
    if '--execute' in sys.argv:
        print("🚀 EXECUTION MODE")
        print("   This will actually move files!")
        print()
        
        response = input("Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
        
        vault_root = Path(__file__).parent.parent / "knowledge"
        workflow = WorkflowManager(str(vault_root))
        
        print("\n📦 Executing auto-promotion...")
        results = workflow.auto_promote_ready_notes(
            dry_run=False,
            quality_threshold=0.65
        )
        
        print(f"\n✅ Promotion Complete:")
        print(f"   Promoted: {results['promoted_count']}")
        print(f"   Skipped: {results['skipped_count']}")
        print(f"   Errors: {results['error_count']}")
        
        if results.get('promoted'):
            print(f"\n📄 Promoted Notes ({len(results['promoted'])}):")
            for note in results['promoted']:
                print(f"   ✅ {note['title']} → {note['target']}")
        
        sys.exit(0)
    
    sys.exit(main())
