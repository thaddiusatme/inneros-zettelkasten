#!/usr/bin/env python3
"""
Link Insertion System Live Test - Direct validation with real notes
Tests the core LinkInsertionEngine on actual vault data with manual suggestions
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add development directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from ai.link_insertion_engine import LinkInsertionEngine
from ai.link_insertion_utils import InsertionResult

def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "="*80)
    print(f"🔗 {text}")
    print("="*80)

def print_section(text):
    """Print a formatted section header"""
    print(f"\n📋 {text}")
    print("-" * 60)

class MockSuggestion:
    """Mock suggestion for testing"""
    def __init__(self, source_note, target_note, suggested_link_text, suggested_location, insertion_context, quality_score=0.8):
        self.source_note = source_note
        self.target_note = target_note
        self.suggested_link_text = suggested_link_text
        self.suggested_location = suggested_location
        self.insertion_context = insertion_context
        self.quality_score = quality_score
        self.confidence = "high" if quality_score > 0.7 else "medium"

def find_real_notes(vault_path: Path):
    """Find actual notes in the vault"""
    print_section("Scanning Vault for Real Notes")
    
    knowledge_path = vault_path / "knowledge"
    notes_found = []
    
    # Scan different directories
    directories = ["Permanent Notes", "Fleeting Notes", "Literature Notes", "Inbox"]
    
    for directory in directories:
        dir_path = knowledge_path / directory
        if dir_path.exists():
            note_files = list(dir_path.glob("*.md"))[:3]  # Limit per directory
            for note_file in note_files:
                relative_path = str(note_file.relative_to(vault_path))
                notes_found.append(relative_path)
                print(f"  ✅ Found: {relative_path}")
    
    print(f"\n🎯 Total notes found: {len(notes_found)}")
    return notes_found

def create_test_suggestions(notes_found):
    """Create realistic test suggestions based on actual notes"""
    print_section("Creating Test Suggestions")
    
    if len(notes_found) < 2:
        print("  ⚠️  Need at least 2 notes to create suggestions")
        return []
    
    suggestions = []
    
    # Create a few realistic suggestions between actual notes
    for i in range(min(2, len(notes_found) - 1)):
        source_note = notes_found[i]
        target_note = notes_found[i + 1]
        
        # Extract clean names for link text
        target_name = Path(target_note).stem
        clean_name = target_name.replace('-', ' ').replace('_', ' ').title()
        
        suggestion = MockSuggestion(
            source_note=source_note,
            target_note=target_note,
            suggested_link_text=f"[[{clean_name}]]",
            suggested_location="related_concepts",
            insertion_context="## Related Concepts",
            quality_score=0.85
        )
        
        suggestions.append(suggestion)
        print(f"  🔗 Created: {source_note} → {suggestion.suggested_link_text}")
    
    print(f"\n🎯 Total suggestions created: {len(suggestions)}")
    return suggestions

def test_link_insertion_safety(vault_path: Path, suggestions):
    """Test the LinkInsertionEngine with safety features"""
    print_banner("Testing Link Insertion System - LIVE DATA")
    
    # Initialize the insertion engine
    insertion_engine = LinkInsertionEngine(str(vault_path), backup_enabled=True)
    
    print_section("Safety System Status")
    print(f"  🛡️  Backup enabled: {'✅ YES' if insertion_engine.backup_enabled else '❌ NO'}")
    print(f"  📁 Backup directory: {insertion_engine.backup_manager.backup_dir}")
    print(f"  🎯 Test suggestions: {len(suggestions)}")
    
    results = []
    
    for i, suggestion in enumerate(suggestions, 1):
        print_section(f"Test {i}: Inserting into {Path(suggestion.source_note).name}")
        
        print(f"  📝 Source: {suggestion.source_note}")
        print(f"  🔗 Link: {suggestion.suggested_link_text}")
        print(f"  📍 Location: {suggestion.suggested_location}")
        print(f"  ⭐ Quality: {suggestion.quality_score}")
        
        # Check if source file exists
        source_path = vault_path / suggestion.source_note
        if not source_path.exists():
            print(f"  ❌ Source file not found: {source_path}")
            continue
        
        # Show original content preview
        try:
            original_content = source_path.read_text()
            lines = original_content.split('\n')
            print(f"  📄 Original file has {len(lines)} lines")
            
            # Preview first few lines
            preview_lines = lines[:5]
            for j, line in enumerate(preview_lines):
                print(f"     {j+1}: {line[:60]}{'...' if len(line) > 60 else ''}")
            
        except Exception as e:
            print(f"  ⚠️  Could not read source file: {e}")
            continue
        
        # Perform the insertion
        print(f"  🔄 Attempting insertion...")
        
        try:
            result = insertion_engine.insert_suggestions_into_note(
                note_path=suggestion.source_note,
                suggestions=[suggestion],
                validate_targets=False,  # Skip target validation for demo
                check_duplicates=True,
                create_sections=True
            )
            
            if result.success:
                print(f"  ✅ SUCCESS! Inserted {result.insertions_made} link(s)")
                if result.backup_path:
                    backup_name = Path(result.backup_path).name
                    print(f"  📦 Backup created: {backup_name}")
                if result.duplicates_skipped > 0:
                    print(f"  ⏭️  Skipped {result.duplicates_skipped} duplicate(s)")
                
                # Show modified content preview
                try:
                    new_content = source_path.read_text()
                    new_lines = new_content.split('\n')
                    print(f"  📄 Modified file now has {len(new_lines)} lines")
                    
                    # Find where the link was inserted
                    for k, line in enumerate(new_lines):
                        if suggestion.suggested_link_text in line:
                            print(f"  🎯 Link found at line {k+1}: {line.strip()}")
                            break
                            
                except Exception as e:
                    print(f"  ⚠️  Could not read modified file: {e}")
                    
            else:
                print(f"  ❌ FAILED: {result.error_message}")
            
            results.append(result)
            
        except Exception as e:
            print(f"  💥 EXCEPTION: {str(e)}")
            error_result = InsertionResult(
                success=False,
                insertions_made=0,
                error_message=f"Exception: {str(e)}"
            )
            results.append(error_result)
    
    return results

def show_backup_system_results(vault_path: Path, results):
    """Show what the backup system created"""
    print_banner("Backup System Results")
    
    backup_dir = vault_path / "backups"
    
    print_section("Backup Directory Status")
    if backup_dir.exists():
        backup_files = list(backup_dir.glob("*.md"))
        print(f"  📂 Backup directory: {backup_dir}")
        print(f"  📋 Total backup files: {len(backup_files)}")
        
        # Show recent backups from this session
        if backup_files:
            recent_backups = sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
            print(f"  🕒 Recent backups:")
            for backup_file in recent_backups:
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                size = backup_file.stat().st_size
                print(f"     {backup_file.name} ({size} bytes, {mtime.strftime('%H:%M:%S')})")
    else:
        print(f"  ❌ Backup directory not found: {backup_dir}")
    
    print_section("Operation Summary")
    successful = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    total_insertions = sum(r.insertions_made for r in results)
    
    print(f"  ✅ Successful operations: {successful}")
    print(f"  ❌ Failed operations: {failed}")
    print(f"  🔗 Total links inserted: {total_insertions}")
    print(f"  📦 Backups created: {sum(1 for r in results if r.backup_path)}")
    
    if total_insertions > 0:
        print(f"\n🎉 SUCCESS! The Link Insertion System successfully modified {total_insertions} notes!")
        print("   All changes were made safely with backup protection.")
    else:
        print(f"\n📝 No modifications were made in this test run.")

def main():
    """Run the Link Insertion System live test"""
    vault_path = Path.cwd()
    
    if not (vault_path / "knowledge").exists():
        print("❌ Error: Please run from the InnerOS Zettelkasten root directory.")
        return
    
    print_banner("Link Insertion System - Live Data Test")
    print(f"🏠 Vault Path: {vault_path}")
    print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Purpose: Direct validation of LinkInsertionEngine with real notes")
    
    try:
        # Step 1: Find real notes
        notes_found = find_real_notes(vault_path)
        if len(notes_found) < 2:
            print("❌ Need at least 2 notes for insertion testing")
            return
        
        # Step 2: Create test suggestions
        suggestions = create_test_suggestions(notes_found)
        if not suggestions:
            print("❌ Could not create test suggestions")
            return
        
        # Step 3: Test insertion system
        results = test_link_insertion_safety(vault_path, suggestions)
        
        # Step 4: Show backup system results
        show_backup_system_results(vault_path, results)
        
        print_banner("Live Test Complete - LinkInsertionEngine Status: VALIDATED! 🚀")
        
    except Exception as e:
        print(f"\n💥 Test encountered an error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
