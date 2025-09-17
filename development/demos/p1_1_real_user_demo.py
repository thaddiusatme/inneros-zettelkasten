#!/usr/bin/env python3
"""
P1-1 Real User Demo: Test Directory Organization on Actual Misplaced Files

This demo demonstrates our P1-1 Actual File Moves system solving the real
documented workflow problem where notes in Inbox/ have mismatched type fields.

Real Problem Examples:
- fleeting-20250806-1520-bug-images-dissapear.md.md: type: permanent but in Inbox/
- lit-20250818-1957-prompt.md: type: literature but in Inbox/

Safety Features Demonstrated:
- Backup creation before operations
- Dry run analysis and validation
- Safe execution with rollback capability
- Progress reporting and comprehensive logging
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
            logging.FileHandler('p1_1_demo.log')
        ]
    )
    return logging.getLogger(__name__)

def scan_misplaced_files(vault_path):
    """Scan for files with type mismatches in Inbox."""
    logger = logging.getLogger(__name__)
    
    inbox_path = Path(vault_path) / "Inbox"
    misplaced_files = []
    
    logger.info(f"Scanning {inbox_path} for type mismatches...")
    
    for md_file in inbox_path.glob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # Extract frontmatter
            if content.startswith("---"):
                frontmatter_end = content.find("---", 3)
                if frontmatter_end > 0:
                    frontmatter = content[3:frontmatter_end]
                    file_type = None
                    
                    for line in frontmatter.split('\n'):
                        if line.startswith('type:'):
                            file_type = line.split(':', 1)[1].strip().lower()
                            break
                    
                    if file_type in ['permanent', 'literature', 'fleeting']:
                        misplaced_files.append({
                            'file': md_file,
                            'type': file_type,
                            'should_be_in': f"{file_type.title()} Notes"
                        })
                        logger.info(f"Found misplaced: {md_file.name} (type: {file_type})")
        
        except Exception as e:
            logger.warning(f"Could not process {md_file.name}: {e}")
    
    return misplaced_files

def progress_callback(current, total, filename):
    """Progress callback for execution reporting."""
    percentage = (current / total) * 100
    print(f"  Progress: [{current}/{total}] {percentage:.1f}% - Moving: {filename}")

def main():
    """Main demo function."""
    logger = setup_logging()
    
    print("🧪 P1-1 Real User Demo: Safety-First Directory Organization")
    print("=" * 70)
    
    # Setup paths
    vault_root = Path(__file__).parent.parent.parent / "knowledge"
    backup_root = Path(__file__).parent.parent.parent / "backups"
    
    logger.info(f"Vault root: {vault_root}")
    logger.info(f"Backup root: {backup_root}")
    
    # Step 1: Scan for misplaced files
    print("\n📋 Step 1: Scanning for misplaced files...")
    misplaced_files = scan_misplaced_files(vault_root)
    
    if not misplaced_files:
        print("✅ No misplaced files found - all files are properly organized!")
        return
    
    print(f"\n🎯 Found {len(misplaced_files)} misplaced files:")
    for item in misplaced_files:
        print(f"  • {item['file'].name} → should be in {item['should_be_in']}/")
    
    # Step 2: Initialize organizer and run dry run
    print("\n📋 Step 2: Initializing Safety-First Directory Organizer...")
    try:
        organizer = DirectoryOrganizer(
            vault_root=str(vault_root),
            backup_root=str(backup_root)
        )
        logger.info("DirectoryOrganizer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize organizer: {e}")
        print(f"❌ Error: {e}")
        return
    
    print("\n📋 Step 3: Performing comprehensive dry run analysis...")
    try:
        # Use the full P0-2/P0-3 integrated dry run system
        move_plan = organizer.plan_moves()
        
        print(f"\n📊 Dry Run Results (P0-2/P0-3 Integration):")
        print(f"  • Total moves planned: {len(move_plan.moves)}")
        print(f"  • Conflicts detected: {len(move_plan.conflicts)}")
        print(f"  • Unknown types: {len(move_plan.unknown_types)}")
        print(f"  • Malformed files: {len(move_plan.malformed_files)}")
        print(f"  • Link updates planned: {len(move_plan.link_updates)}")
        
        # Show link preservation stats
        if hasattr(move_plan, 'summary'):
            summary = move_plan.summary
            if 'total_links_scanned' in summary:
                print(f"  • Links scanned: {summary['total_links_scanned']}")
            if 'broken_links_detected' in summary:
                print(f"  • Broken links found: {summary['broken_links_detected']}")
        
        if move_plan.moves:
            print(f"\n📝 Planned Moves:")
            for move in move_plan.moves:
                source_rel = move.source.relative_to(vault_root)
                target_rel = move.target.relative_to(vault_root)
                print(f"  • {source_rel} → {target_rel}")
        
        if move_plan.conflicts:
            print(f"\n⚠️  Conflicts Detected:")
            for conflict in move_plan.conflicts:
                print(f"  • {conflict}")
            print("\n❌ Cannot proceed with execution due to conflicts")
            return
        
    except Exception as e:
        logger.error(f"Dry run failed: {e}")
        print(f"❌ Dry run error: {e}")
        return
    
    # Step 4: Ask user confirmation
    if move_plan.moves:
        print(f"\n🔒 Safety Features:")
        print(f"  • Backup will be created before operations")
        print(f"  • Rollback available if any issues occur")
        print(f"  • Progress tracking throughout execution")
        print(f"  • Individual move validation and error handling")
        
        response = input(f"\n❓ Execute {len(move_plan.moves)} file moves? (y/N): ")
        
        if response.lower() not in ['y', 'yes']:
            print("🚫 Execution cancelled by user")
            return
        
        # Step 5: Execute moves with full safety
        print(f"\n🚀 Step 4: Executing file moves with safety-first approach...")
        try:
            result = organizer.execute_moves(
                create_backup=True,
                validate_first=True,
                rollback_on_error=True,
                progress_callback=progress_callback
            )
            
            print(f"\n✅ Execution completed successfully!")
            print(f"📊 Results:")
            print(f"  • Moves executed: {result['moves_executed']}")
            print(f"  • Files processed: {result['files_processed']}")
            print(f"  • Backup created: {result['backup_created']}")
            print(f"  • Execution time: {result['execution_time_seconds']:.2f} seconds")
            print(f"  • Status: {result['status']}")
            
            if result['backup_created']:
                print(f"  • Backup path: {result['backup_path']}")
            
            # Validation results
            validation = result.get('validation_results', {})
            print(f"\n📋 Validation Summary:")
            print(f"  • Total moves planned: {validation.get('total_moves_planned', 0)}")
            print(f"  • Conflicts detected: {validation.get('conflicts_detected', 0)}")
            print(f"  • Unknown types: {validation.get('unknown_types', 0)}")
            print(f"  • Malformed files: {validation.get('malformed_files', 0)}")
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            print(f"❌ Execution error: {e}")
            print(f"🔄 Rollback should have been triggered automatically")
            return
    else:
        print("✅ All files are already properly organized!")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"📝 Check p1_1_demo.log for detailed logging")

if __name__ == "__main__":
    main()
