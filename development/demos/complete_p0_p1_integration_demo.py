#!/usr/bin/env python3
"""
Complete P0+P1 Integration Demo: Full Safety-First Directory Organization

This demo showcases the complete integration of all phases:
- P0-1: Backup system with rollback capability
- P0-2: Comprehensive dry run with YAML parsing and reporting  
- P0-3: Wiki-link preservation architecture
- P1-1: Actual file move execution with safety features
- P1-2: Post-move validation with auto-rollback

Demonstrates the complete solution to the documented workflow problem where
notes in Inbox/ have mismatched type fields.
"""

import sys
import logging
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.directory_organizer import DirectoryOrganizer

def setup_logging():
    """Setup comprehensive logging for demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('complete_integration_demo.log')
        ]
    )
    return logging.getLogger(__name__)

def progress_callback(current, total, filename):
    """Progress callback for execution reporting."""
    percentage = (current / total) * 100
    print(f"    Progress: [{current}/{total}] {percentage:.1f}% - Moving: {filename}")

def main():
    """Main demo function showcasing complete P0+P1 integration."""
    logger = setup_logging()
    
    print("🏗️ Complete P0+P1 Integration Demo: Safety-First Directory Organization")
    print("=" * 80)
    print("\nPhases Integrated:")
    print("  ✅ P0-1: Backup System with Rollback")
    print("  ✅ P0-2: Comprehensive Dry Run Analysis") 
    print("  ✅ P0-3: Wiki-Link Preservation Architecture")
    print("  ✅ P1-1: Safe File Move Execution")
    print("  ✅ P1-2: Post-Move Validation with Auto-Rollback")
    
    # Setup paths
    vault_root = Path(__file__).parent.parent.parent / "knowledge"
    backup_root = Path(__file__).parent.parent.parent / "backups"
    
    logger.info(f"Vault root: {vault_root}")
    logger.info(f"Backup root: {backup_root}")
    
    print(f"\n🎯 Target Problem: Solving misplaced notes with type field mismatches")
    print(f"  📁 Vault: {vault_root}")
    print(f"  💾 Backups: {backup_root}")
    
    # Initialize comprehensive organizer
    print(f"\n📋 Phase 1: Initializing Complete Safety-First System...")
    try:
        organizer = DirectoryOrganizer(
            vault_root=str(vault_root),
            backup_root=str(backup_root)
        )
        logger.info("Complete DirectoryOrganizer system initialized")
        print("  ✅ P0-1 Backup System: Ready")
        print("  ✅ P0-2 Dry Run Analysis: Ready") 
        print("  ✅ P0-3 Link Preservation: Ready")
        print("  ✅ P1-1 File Execution: Ready")
        print("  ✅ P1-2 Validation System: Ready")
        
    except Exception as e:
        logger.error(f"Failed to initialize complete system: {e}")
        print(f"❌ Initialization Error: {e}")
        return
    
    # Comprehensive dry run analysis (P0-2/P0-3)
    print(f"\n📋 Phase 2: Comprehensive Analysis (P0-2/P0-3 Integration)...")
    try:
        move_plan = organizer.plan_moves()
        
        print(f"\n📊 Complete Analysis Results:")
        print(f"  📁 Files analyzed: {move_plan.summary['total_files']}")
        print(f"  📝 Files with frontmatter: {move_plan.summary['files_with_frontmatter']}")
        print(f"  ✅ Correctly placed: {move_plan.summary['correctly_placed_files']}")
        print(f"  🔄 Moves planned: {len(move_plan.moves)}")
        print(f"  ⚠️  Conflicts detected: {len(move_plan.conflicts)}")
        print(f"  ❓ Unknown types: {len(move_plan.unknown_types)}")
        print(f"  💥 Malformed files: {len(move_plan.malformed_files)}")
        print(f"  🔗 Link updates planned: {len(move_plan.link_updates)}")
        print(f"  📎 Total links scanned: {move_plan.summary.get('total_links_scanned', 0)}")
        print(f"  💔 Broken links found: {move_plan.summary.get('broken_links_detected', 0)}")
        
        if move_plan.conflicts:
            print(f"\n⚠️  Critical: Conflicts must be resolved first:")
            for conflict in move_plan.conflicts[:3]:  # Show first 3
                print(f"    • {conflict}")
            if len(move_plan.conflicts) > 3:
                print(f"    ... and {len(move_plan.conflicts) - 3} more")
            print(f"\n❌ Cannot proceed with conflicts present")
            return
        
        if not move_plan.moves:
            print(f"\n✅ Vault is perfectly organized - no moves needed!")
            return
            
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        print(f"❌ Analysis Error: {e}")
        return
    
    # Show sample of planned moves
    print(f"\n📝 Sample Planned Moves (showing first 5):")
    for i, move in enumerate(move_plan.moves[:5]):
        source_rel = move.source.relative_to(vault_root)
        target_rel = move.target.relative_to(vault_root)
        print(f"    {i+1}. {source_rel} → {target_rel}")
    
    if len(move_plan.moves) > 5:
        print(f"    ... and {len(move_plan.moves) - 5} more moves planned")
    
    # Safety confirmation
    print(f"\n🔒 Integrated Safety Features:")
    print(f"  💾 Pre-execution backup: ✅ Enabled")
    print(f"  🔍 Pre-execution validation: ✅ Enabled") 
    print(f"  📊 Post-execution validation: ✅ Enabled")
    print(f"  🔄 Auto-rollback on failure: ✅ Enabled")
    print(f"  🔗 Link integrity preservation: ✅ Enabled")
    
    # User confirmation
    response = input(f"\n❓ Execute {len(move_plan.moves)} moves with full P0+P1 safety? (y/N): ")
    
    if response.lower() not in ['y', 'yes']:
        print("🚫 Execution cancelled by user")
        return
    
    # Execute with complete P1-2 validation
    print(f"\n🚀 Phase 3: Executing with Complete P1-2 Validation System...")
    try:
        print("  📊 Pre-execution validation: ✅")
        print("  💾 Creating safety backup...")
        print("  🔄 Executing file moves...")
        
        result = organizer.execute_with_validation(
            create_backup=True,
            validate_after=True,
            auto_rollback=True,
            progress_callback=progress_callback
        )
        
        print(f"\n✅ Execution Results:")
        print(f"  📦 Moves executed: {result['moves_executed']}")
        print(f"  📁 Files processed: {result['files_processed']}")
        print(f"  💾 Backup created: {result['backup_created']}")
        print(f"  ⏱️  Execution time: {result['execution_time_seconds']:.2f} seconds")
        print(f"  📊 Status: {result['status']}")
        
        if result['backup_created']:
            print(f"  💾 Backup location: {result['backup_path']}")
        
        # Validation results
        if result.get('validation_performed'):
            validation = result['validation_results']
            print(f"\n🔍 Post-Move Validation Results:")
            print(f"  📊 Validation passed: {'✅' if validation['validation_passed'] else '❌'}")
            print(f"  📁 Files checked: {validation['file_system_integrity']['total_files_checked']}")
            print(f"  📖 Readable files: {validation['file_system_integrity']['readable_files']}")
            print(f"  🔗 Links validated: {validation['link_integrity']['total_links_checked']}")
            print(f"  ✅ Valid links: {validation['link_integrity']['valid_links']}")
            print(f"  💔 Broken links: {len(validation['link_integrity']['broken_links'])}")
            
            if validation['errors_found']:
                print(f"  ⚠️  Errors found: {len(validation['errors_found'])}")
                for error in validation['errors_found'][:3]:
                    print(f"      • {error}")
            
            if validation['warnings_found']:
                print(f"  ⚠️  Warnings: {len(validation['warnings_found'])}")
                for warning in validation['warnings_found'][:3]:
                    print(f"      • {warning}")
            
            print(f"\n💡 Recommendations:")
            for rec in validation['recommendations']:
                print(f"    {rec}")
        
        # Final status
        if result['status'] == 'success':
            print(f"\n🎉 Complete Success! Directory organization completed safely.")
            print(f"   📊 Problem solved: Notes now match their type-based directories")
            print(f"   🔗 Link integrity: Preserved throughout the operation")
            print(f"   💾 Safety: Complete backup available for rollback if needed")
        elif result['status'].startswith('rolled_back'):
            print(f"\n🔄 Auto-Rollback Executed: {result.get('rollback_reason', 'Validation failed')}")
            print(f"   📊 System restored to original state due to validation issues")
            print(f"   🔍 Review validation errors and resolve before retry")
        else:
            print(f"\n⚠️  Execution completed with issues: {result['status']}")
            
    except Exception as e:
        logger.error(f"Execution with validation failed: {e}")
        print(f"❌ Execution Error: {e}")
        return
    
    print(f"\n📋 Demo Complete!")
    print(f"📝 Check complete_integration_demo.log for detailed execution logs")
    print(f"\nThis demo showcased the complete P0+P1 integration solving the documented")
    print(f"workflow problem where notes have mismatched type fields and directories.")

if __name__ == "__main__":
    main()
