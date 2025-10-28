#!/usr/bin/env python3
"""Run cleanup workflow end-to-end on real vault.

This demonstrates the complete cleanup workflow:
1. Generate inventory from vault
2. Generate decision log from inventory
3. Display pending decisions
4. (Manual approval step would go here)
5. Execute approved moves
6. Display audit trail
"""

import sys
from pathlib import Path

# Add development to path
sys.path.insert(0, str(Path(__file__).parent))

from src.automation.cleanup_workflow_demo import run_cleanup_workflow_demo


def main():
    """Run cleanup workflow on real vault."""
    
    # Vault root is parent of development/
    vault_root = Path(__file__).parent.parent
    
    print("=" * 80)
    print("🧹 CLEANUP WORKFLOW - REAL VAULT RUN")
    print("=" * 80)
    print(f"\n📁 Vault Root: {vault_root}")
    print("\n⚠️  NOTE: This uses mocked DirectoryOrganizer (no real file moves).")
    print("         The workflow generates inventory → decision log → execution report.\n")
    
    print("🚀 Starting inventory scan...\n")
    
    try:
        # Run the workflow
        result = run_cleanup_workflow_demo(vault_root=vault_root)
        
        # Display results
        print("\n" + "=" * 80)
        print("✅ WORKFLOW COMPLETE")
        print("=" * 80)
        
        print(f"\n📊 Workflow Status: {result['workflow_status']}")
        print(f"📝 Moves Executed: {result['moves_executed']}")
        print(f"📄 Files Processed: {result['files_processed']}")
        
        # Display audit trail
        audit_trail = result.get('audit_trail', {})
        print(f"\n🔍 Audit Trail:")
        print(f"   Total Moves: {audit_trail.get('total_moves', 0)}")
        print(f"   Completed: {audit_trail.get('completed_moves', 0)}")
        print(f"   Failed: {audit_trail.get('failed_moves', 0)}")
        
        # Display backup info
        backup_path = result.get('backup_path')
        if backup_path:
            print(f"\n💾 Backup Path: {backup_path}")
        
        # Display execution report location
        execution_report = result.get('execution_report', {})
        print(f"\n📋 Check .automation/review_queue/ for detailed YAML reports")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
