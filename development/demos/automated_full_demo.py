#!/usr/bin/env python3
"""
Automated End-to-End Demo: Both Automation Methods
Shows CLI processing and explains how daemon automation works
"""

import sys
from pathlib import Path
import time
import subprocess
from datetime import datetime

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent))

REPO_ROOT = Path(__file__).parent.parent.parent
DEMO_NOTE = REPO_ROOT / f"knowledge/Inbox/YouTube/demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def create_test_note():
    """Create a test note"""
    print_section("STEP 1: Creating YouTube Note")
    
    content = """---
type: literature
created: 2025-10-21 15:30
status: draft
ready_for_processing: true
tags: [youtube, demo, neural-networks]
visibility: private
source: youtube
video_id: aircAruvnKk
video_url: https://www.youtube.com/watch?v=aircAruvnKk
channel: 3Blue1Brown
author: Grant Sanderson
---

# But what is a neural network? | Automated Demo

## Why I'm Saving This
Excellent visual explanation of neural networks. Grant's animations make
complex mathematical concepts intuitive.

## Key Takeaways
<!-- AI will extract quotes here -->
"""
    
    DEMO_NOTE.write_text(content)
    print(f"✅ Created: {DEMO_NOTE.name}")
    print(f"📍 Location: {DEMO_NOTE}")
    print("\n📋 Initial State:")
    print("   status: draft")
    print("   ready_for_processing: true ← Already approved for demo")
    print("   ai_processed: (not set)")
    
    return DEMO_NOTE

def show_method_overview():
    """Explain the automation methods"""
    print_section("AUTOMATION METHODS OVERVIEW")
    
    print("You have THREE working automation methods:\n")
    
    print("1. 🤖 FILE WATCHER DAEMON (Primary - Fully Automatic)")
    print("   • Watches for file changes automatically")
    print("   • Processes within 5 seconds of approval")
    print("   • Start with: python3 -m src.automation.daemon start")
    print("   • Status: ✅ Built and operational")
    print()
    
    print("2. 🌐 HTTP API SERVER (For Webhooks/External Tools)")
    print("   • REST API with async processing queue")
    print("   • POST /api/youtube/process endpoint")
    print("   • Start with: python3 run_youtube_api_server.py")
    print("   • Status: ✅ Built and operational")
    print()
    
    print("3. 🔧 CLI PROCESSING (For Testing/Manual)")
    print("   • Direct command-line processing")
    print("   • Great for testing and debugging")
    print("   • This is what we'll demonstrate now")
    print("   • Status: ✅ Built and operational")
    print()

def process_note(note_path):
    """Process the note using CLI method"""
    print_section("STEP 2: Processing Note (CLI Method)")
    
    print("Processing will:")
    print("  1. ✅ Validate approval status")
    print("  2. 🔄 Update status: draft → processing")
    print("  3. 📡 Fetch English transcript from YouTube")
    print("  4. 🤖 Extract key quotes using AI")
    print("  5. 💾 Archive transcript with bidirectional links")
    print("  6. 🔄 Update status: processing → processed")
    print("  7. ✅ Mark as ai_processed: true")
    print()
    print("⏳ Starting processing (typically 15-20 seconds)...")
    print()
    
    # Run the processing script
    dev_dir = Path(__file__).parent.parent
    process = subprocess.run(
        [sys.executable, "process_single_youtube_note.py", str(note_path)],
        cwd=dev_dir,
        capture_output=True,
        text=True
    )
    
    print(process.stdout)
    if process.stderr:
        print("Errors:", process.stderr)
    
    return process.returncode == 0

def show_results(note_path):
    """Show the processing results"""
    print_section("STEP 3: Results & Analysis")
    
    content = note_path.read_text()
    lines = content.split('\n')
    
    # Find frontmatter
    print("📄 Final Frontmatter:")
    print("━" * 80)
    in_frontmatter = False
    count = 0
    for line in lines:
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            count += 1
            if count == 2:
                print("---")
                break
        if in_frontmatter or count == 1:
            print(line)
    print("━" * 80)
    print()
    
    # Extract key metrics
    print("📊 Processing Metrics:")
    print("━" * 80)
    for line in lines[1:30]:  # Check first 30 lines
        if any(key in line for key in ['status:', 'ai_processed:', 'quote_count:', 
                                        'processing_time', 'transcript_file:']):
            print(f"   {line}")
    print("━" * 80)
    print()
    
    # Show quotes if available
    if '### 🎯 Extracted Quotes' in content:
        print("🎯 Sample of Extracted Quotes:")
        print("━" * 80)
        in_quotes = False
        quote_lines = 0
        for line in lines:
            if '### 🎯 Extracted Quotes' in line:
                in_quotes = True
            elif in_quotes:
                print(line)
                quote_lines += 1
                if quote_lines > 15:  # Show first 15 lines
                    print("   ... (additional quotes in note)")
                    break
        print("━" * 80)
        print()

def explain_daemon_method():
    """Explain how the daemon would work"""
    print_section("HOW THE DAEMON METHOD WORKS")
    
    print("In production, the FILE WATCHER DAEMON automates everything:\n")
    
    print("User Workflow:")
    print("  1. Create YouTube note from template")
    print("     └─ status: draft, ready_for_processing: false")
    print()
    print("  2. Add your thoughts and context")
    print("     └─ Take your time, no rush")
    print()
    print("  3. Check the approval checkbox")
    print("     └─ Obsidian updates: ready_for_processing: true")
    print()
    print("  4. [AUTOMATIC] Daemon detects change (0-5 seconds)")
    print("     └─ Processes automatically")
    print()
    print("  5. [AUTOMATIC] Processing completes")
    print("     └─ Quotes inserted, transcript archived")
    print()
    print("  6. Done! ✅")
    print()
    
    print("To start the daemon:")
    print("  cd development")
    print("  python3 -m src.automation.daemon start")
    print()

def main():
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "YouTube Automation: Complete Demo" + " " * 25 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Show overview
    show_method_overview()
    
    # Create test note
    note_path = create_test_note()
    
    print("\n⏸️  Demo will process the note in 3 seconds...")
    time.sleep(3)
    
    # Process the note
    success = process_note(note_path)
    
    if success:
        # Show results
        show_results(note_path)
        
        # Explain daemon
        explain_daemon_method()
        
        print_section("🎉 DEMO COMPLETE!")
        print("Summary:")
        print("  ✅ Created YouTube note")
        print("  ✅ Processed with AI (CLI method demonstrated)")
        print("  ✅ Extracted quotes and archived transcript")
        print()
        print("The daemon and API methods work the same way, just automatically!")
        print()
        print(f"📁 Test note: {note_path}")
        print("   (You can delete this test note or keep it for reference)")
        print()
        
        return 0
    else:
        print("\n❌ Processing failed. Check error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
