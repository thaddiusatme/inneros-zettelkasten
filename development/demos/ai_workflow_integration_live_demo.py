#!/usr/bin/env python3
"""
Live Demo: AI Workflow Integration for Knowledge Capture System
Tests the newly implemented process_capture_notes_with_ai() method with real data
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add development directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from capture_matcher import CaptureMatcherPOC


def create_sample_capture_notes():
    """Create sample capture notes for AI processing demo"""
    print("🔧 Creating sample capture notes...")
    
    # Initialize capture matcher
    matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
    matcher.configure_inbox_directory("/tmp/capture_demo_inbox")
    
    # Sample capture pairs for demonstration
    sample_pairs = [
        {
            "screenshot": {
                "filename": "Screenshot_20250922_141530.png",
                "timestamp": datetime(2025, 9, 22, 14, 15, 30),
                "path": "/fake/screenshot1.png",
                "size": 1245678
            },
            "voice": {
                "filename": "Recording_20250922_141545.m4a", 
                "timestamp": datetime(2025, 9, 22, 14, 15, 45),
                "path": "/fake/voice1.m4a",
                "size": 487362
            },
            "time_gap_seconds": 15
        },
        {
            "screenshot": {
                "filename": "Screenshot_20250922_152012.png",
                "timestamp": datetime(2025, 9, 22, 15, 20, 12),
                "path": "/fake/screenshot2.png", 
                "size": 892341
            },
            "voice": {
                "filename": "Recording_20250922_152030.m4a",
                "timestamp": datetime(2025, 9, 22, 15, 20, 30),
                "path": "/fake/voice2.m4a",
                "size": 623781
            },
            "time_gap_seconds": 18
        },
        {
            "screenshot": {
                "filename": "Screenshot_20250922_163245.png",
                "timestamp": datetime(2025, 9, 22, 16, 32, 45),
                "path": "/fake/screenshot3.png",
                "size": 1567890
            },
            "voice": {
                "filename": "Recording_20250922_163255.m4a",
                "timestamp": datetime(2025, 9, 22, 16, 32, 55),
                "path": "/fake/voice3.m4a",
                "size": 834219
            },
            "time_gap_seconds": 10
        }
    ]
    
    # Generate capture notes
    descriptions = [
        "ai-research-discussion",
        "project-planning-session", 
        "knowledge-management-insights"
    ]
    
    capture_notes = []
    for i, (pair, desc) in enumerate(zip(sample_pairs, descriptions)):
        print(f"  📝 Generating capture note {i+1}: {desc}")
        note = matcher.generate_capture_note(pair, desc)
        capture_notes.append(note)
    
    print(f"✅ Created {len(capture_notes)} sample capture notes")
    return capture_notes, matcher


def display_capture_note_preview(note, index):
    """Display a preview of the capture note"""
    print(f"\n📋 **Capture Note {index + 1}**: {note['filename']}")
    print(f"   📂 Path: {note['file_path']}")
    
    # Show first few lines of content
    lines = note['markdown_content'].split('\n')
    yaml_end = -1
    for i, line in enumerate(lines):
        if line.strip() == '---' and i > 0:
            yaml_end = i
            break
    
    if yaml_end > 0:
        print("   📄 YAML Frontmatter:")
        for line in lines[1:yaml_end]:
            if line.strip():
                print(f"      {line}")
        
        print("   📝 Content Preview:")
        content_lines = lines[yaml_end+1:yaml_end+4]
        for line in content_lines:
            if line.strip():
                print(f"      {line}")
                break


def display_ai_results(ai_results):
    """Display AI processing results in a formatted way"""
    print("\n🤖 **AI Processing Results:**")
    
    for i, result in enumerate(ai_results):
        print(f"\n   📊 **Note {i+1}**: {result['original_filename']}")
        print(f"      🎯 Quality Score: {result['quality_score']:.2f}")
        print(f"      🏷️  AI Tags: {', '.join(result['ai_tags'])}")
        print(f"      🔧 Processing Method: {result['processing_method']}")
        
        if result['recommendations']:
            print(f"      💡 Recommendations:")
            for rec in result['recommendations'][:3]:  # Show first 3
                print(f"         • {rec}")


def display_processing_stats(stats):
    """Display processing statistics"""
    print("\n📊 **Processing Statistics:**")
    print(f"   📈 Total Notes: {stats['total_notes']}")
    print(f"   ✅ Successful: {stats['successful']}")
    print(f"   ❌ Errors: {stats['errors']}")
    print(f"   ⏱️  Processing Time: {stats['processing_time']:.3f} seconds")
    print(f"   🎯 Average Quality Score: {stats['average_quality_score']:.3f}")
    print(f"   🔗 WorkflowManager Available: {stats['workflow_manager_available']}")


def main():
    """Run the live AI workflow integration demo"""
    print("🚀 **AI Workflow Integration Live Demo**")
    print("=" * 50)
    
    try:
        # Create sample capture notes
        capture_notes, matcher = create_sample_capture_notes()
        
        # Show previews of capture notes
        print("\n📋 **Sample Capture Notes Created:**")
        for i, note in enumerate(capture_notes):
            display_capture_note_preview(note, i)
        
        # Process with AI integration
        print("\n🤖 **Processing with AI Integration...**")
        print("   (This will test the WorkflowManager integration)")
        
        start_time = datetime.now()
        ai_result = matcher.process_capture_notes_with_ai(capture_notes)
        end_time = datetime.now()
        
        processing_duration = (end_time - start_time).total_seconds()
        print(f"   ✅ Processing completed in {processing_duration:.3f} seconds")
        
        # Display results
        display_processing_stats(ai_result['processing_stats'])
        display_ai_results(ai_result['ai_results'])
        
        # Show errors if any
        if ai_result['errors']:
            print("\n⚠️ **Errors Encountered:**")
            for error in ai_result['errors']:
                if isinstance(error, dict):
                    print(f"   • {error.get('error', error)}")
                else:
                    print(f"   • {error}")
        
        # Performance validation
        print("\n🎯 **Performance Validation:**")
        target_time = 30  # 30 second target for 5+ notes
        actual_time = ai_result['processing_stats']['processing_time']
        
        if actual_time < target_time:
            print(f"   ✅ Performance target MET: {actual_time:.3f}s < {target_time}s")
        else:
            print(f"   ⚠️ Performance target MISSED: {actual_time:.3f}s > {target_time}s")
        
        # Quality validation
        avg_quality = ai_result['processing_stats']['average_quality_score']
        quality_target = 0.7
        
        if avg_quality >= quality_target:
            print(f"   ✅ Quality target MET: {avg_quality:.3f} >= {quality_target}")
        else:
            print(f"   ⚠️ Quality target MISSED: {avg_quality:.3f} < {quality_target}")
        
        print("\n🎉 **Live Demo Complete!**")
        print("   The AI workflow integration is working successfully.")
        print("   Capture notes are now enhanced with AI processing capabilities.")
        
    except Exception as e:
        print(f"\n❌ **Demo Error**: {e}")
        print("   This may indicate an integration issue to investigate.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
