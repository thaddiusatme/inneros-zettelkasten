#!/usr/bin/env python3
"""
Samsung Screenshot Individual Processing - Real Data Demo

Demonstrates the complete TDD Iteration 5 Individual Processing System
with actual Samsung S3 screenshots and real OCR integration.

Real Data Validation:
- Actual Samsung screenshot file detection
- Real OCR processing with llama_vision_ocr.py
- Individual note generation with contextual descriptions
- Template-based structure following capture-* format
- Performance validation against <10 minute targets
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.evening_screenshot_processor import EveningScreenshotProcessor
from src.cli.individual_screenshot_utils import (
    ContextualFilenameGenerator,
    RichContextAnalyzer,
    TemplateNoteRenderer,
    IndividualProcessingOrchestrator,
    SmartLinkIntegrator
)

def find_samsung_screenshots():
    """Find actual Samsung screenshots in common OneDrive locations"""
    
    # Common OneDrive paths for Samsung screenshots
    possible_paths = [
        Path.home() / "OneDrive" / "Pictures" / "Screenshots",
        Path.home() / "OneDrive" / "Desktop" / "Screenshots", 
        Path.home() / "OneDrive" / "Documents" / "Screenshots",
        Path.home() / "Pictures" / "Screenshots",
        Path.home() / "Desktop" / "Screenshots",
        # Add common Samsung naming pattern searches
        Path.home() / "OneDrive",  # Will search recursively
    ]
    
    samsung_screenshots = []
    
    print("🔍 Searching for Samsung screenshots...")
    
    for base_path in possible_paths:
        if not base_path.exists():
            print(f"   ❌ Path not found: {base_path}")
            continue
            
        print(f"   🔍 Searching: {base_path}")
        
        # Search for Samsung screenshot naming pattern: Screenshot_YYYYMMDD_HHMMSS_AppName.jpg
        if base_path.name == "OneDrive":
            # Recursive search in OneDrive
            screenshot_files = list(base_path.rglob("Screenshot_*_*_*.jpg"))
            screenshot_files.extend(list(base_path.rglob("Screenshot_*_*_*.png")))
        else:
            # Direct search in specific directories
            screenshot_files = list(base_path.glob("Screenshot_*_*_*.jpg"))
            screenshot_files.extend(list(base_path.glob("Screenshot_*_*_*.png")))
        
        for screenshot in screenshot_files:
            # Validate Samsung naming pattern
            if screenshot.name.startswith("Screenshot_") and len(screenshot.name.split("_")) >= 4:
                samsung_screenshots.append(screenshot)
                print(f"   ✅ Found Samsung screenshot: {screenshot.name}")
    
    print(f"\n📊 Total Samsung screenshots found: {len(samsung_screenshots)}")
    return samsung_screenshots[:5]  # Limit to 5 for demo


def create_demo_knowledge_base():
    """Create a temporary knowledge base for testing"""
    temp_dir = tempfile.mkdtemp(prefix="samsung_individual_demo_")
    knowledge_path = Path(temp_dir) / "knowledge"
    knowledge_path.mkdir(parents=True)
    (knowledge_path / "Inbox").mkdir()
    
    print(f"📁 Created demo knowledge base: {knowledge_path}")
    return knowledge_path


def test_individual_processing_utilities():
    """Test the extracted utility classes with mock data"""
    print("\n🧪 Testing Individual Processing Utilities...")
    
    # Test ContextualFilenameGenerator
    print("\n1️⃣ Testing ContextualFilenameGenerator...")
    filename_generator = ContextualFilenameGenerator()
    
    test_descriptions = [
        ("GitHub Repository: Advanced AI Automation Tools", "Open source repository for AI automation"),
        ("Tutorial: React Native Development Best Practices", "Development tutorial for mobile applications"),
        ("Machine Learning Tutorial - Advanced Neural Networks", "Comprehensive tutorial covering deep learning")
    ]
    
    for ocr_text, summary in test_descriptions:
        description = filename_generator.extract_intelligent_description(ocr_text, summary)
        print(f"   📝 '{ocr_text[:50]}...' → '{description}'")
    
    # Test RichContextAnalyzer
    print("\n2️⃣ Testing RichContextAnalyzer...")
    context_analyzer = RichContextAnalyzer()
    
    mock_screenshot = Path("Screenshot_20250925_143022_Chrome.jpg")
    rich_context = context_analyzer.analyze_screenshot_with_rich_context(mock_screenshot)
    
    print(f"   📱 Device: {rich_context['device_metadata']['device_type']}")
    print(f"   📱 App: {rich_context['device_metadata']['app_name']}")
    print(f"   📊 Topics: {len(rich_context['key_topics'])} topics")
    print(f"   💡 Insights: {len(rich_context['contextual_insights'])} insights")
    
    # Test TemplateNoteRenderer
    print("\n3️⃣ Testing TemplateNoteRenderer...")
    template_renderer = TemplateNoteRenderer()
    
    note_content = template_renderer.generate_template_based_note_content(
        mock_screenshot, rich_context, "capture-20250925-1430-chrome-browser.md"
    )
    
    print(f"   📄 Generated note content: {len(note_content)} characters")
    print(f"   ✅ Contains YAML frontmatter: {'---' in note_content}")
    print(f"   ✅ Contains screenshot reference: {'![' in note_content}")
    print(f"   ✅ Contains metadata sections: {'## Capture Metadata' in note_content}")


def run_real_data_demo(screenshots, knowledge_path):
    """Run the complete individual processing demo with real screenshots"""
    print(f"\n🚀 Running Real Data Demo with {len(screenshots)} screenshots...")
    
    if not screenshots:
        print("❌ No Samsung screenshots found. Creating mock demo...")
        return run_mock_demo(knowledge_path)
    
    # Initialize the processor with real paths
    onedrive_path = str(screenshots[0].parent)
    processor = EveningScreenshotProcessor(onedrive_path, str(knowledge_path))
    
    print(f"📱 OneDrive Path: {onedrive_path}")
    print(f"📁 Knowledge Path: {knowledge_path}")
    
    # Test individual processing with real screenshots
    start_time = time.time()
    
    try:
        print("\n📊 Processing Individual Screenshots...")
        
        # Use the individual processing orchestrator
        result = processor.individual_orchestrator.process_screenshots_individually_optimized(screenshots)
        
        processing_time = time.time() - start_time
        
        print(f"\n✅ Individual Processing Results:")
        print(f"   📊 Total Processed: {result['total_processed']}")
        print(f"   📝 Individual Notes Created: {result['individual_notes_created']}")
        print(f"   ⏱️  Processing Time: {processing_time:.2f}s")
        print(f"   🚀 Screenshots/Second: {result['total_processed'] / processing_time:.2f}")
        print(f"   🎯 Performance Target Met: {processing_time < 600} (<10 minutes)")
        
        # Show optimization metrics
        if 'optimization_metrics' in result:
            metrics = result['optimization_metrics']
            print(f"\n📈 Optimization Metrics:")
            print(f"   🔄 Description Generation: {metrics['description_generation_time']:.2f}s")
            print(f"   📄 Template Rendering: {metrics['template_rendering_time']:.2f}s") 
            print(f"   💾 File I/O: {metrics['file_io_time']:.2f}s")
        
        # List generated files
        inbox_path = knowledge_path / "Inbox"
        generated_notes = list(inbox_path.glob("capture-*.md"))
        
        print(f"\n📁 Generated Individual Notes ({len(generated_notes)}):")
        for note in generated_notes:
            print(f"   📄 {note.name}")
            
            # Show note content preview
            with open(note, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"      📖 Title: {[line for line in lines if line.startswith('#')][0] if any(line.startswith('#') for line in lines) else 'No title'}")
                print(f"      📊 Size: {len(content)} characters")
                print(f"      🏷️  Contains tags: {'tags:' in content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        print(f"⚠️  Falling back to mock demo...")
        return run_mock_demo(knowledge_path)


def run_mock_demo(knowledge_path):
    """Run mock demo when real screenshots aren't available"""
    print("\n🎭 Running Mock Demo (No real screenshots found)...")
    
    # Create mock screenshot files for demonstration
    mock_screenshots = []
    screenshot_names = [
        "Screenshot_20250925_143022_Chrome.jpg",
        "Screenshot_20250925_143045_Obsidian.jpg",
        "Screenshot_20250925_143118_GitHub.jpg"
    ]
    
    temp_onedrive = knowledge_path.parent / "mock_onedrive"
    temp_onedrive.mkdir()
    
    for name in screenshot_names:
        mock_file = temp_onedrive / name
        mock_file.write_text("Mock screenshot content")
        mock_screenshots.append(mock_file)
    
    print(f"📁 Created {len(mock_screenshots)} mock screenshots")
    
    # Initialize processor with mock data
    processor = EveningScreenshotProcessor(str(temp_onedrive), str(knowledge_path))
    
    start_time = time.time()
    
    # Run individual processing
    result = processor.individual_orchestrator.process_screenshots_individually_optimized(mock_screenshots)
    
    processing_time = time.time() - start_time
    
    print(f"\n✅ Mock Processing Results:")
    print(f"   📊 Total Processed: {result['total_processed']}")
    print(f"   📝 Individual Notes Created: {result['individual_notes_created']}")
    print(f"   ⏱️  Processing Time: {processing_time:.2f}s")
    print(f"   🎯 Performance Target Met: {processing_time < 600}")
    
    return True


def analyze_results(knowledge_path):
    """Analyze the generated individual notes"""
    print("\n📊 Analyzing Generated Individual Notes...")
    
    inbox_path = knowledge_path / "Inbox"
    capture_notes = list(inbox_path.glob("capture-*.md"))
    
    if not capture_notes:
        print("❌ No capture notes found")
        return
    
    print(f"📄 Found {len(capture_notes)} individual capture notes")
    
    for note in capture_notes:
        print(f"\n📄 Analyzing: {note.name}")
        
        with open(note, 'r') as f:
            content = f.read()
        
        # Analyze structure
        has_frontmatter = content.startswith('---')
        has_title = any(line.startswith('#') for line in content.split('\n'))
        has_screenshot_ref = '![' in content
        has_metadata_section = '## Capture Metadata' in content
        has_ai_analysis = '## AI Vision Analysis' in content
        
        print(f"   ✅ YAML Frontmatter: {has_frontmatter}")
        print(f"   ✅ Title Section: {has_title}")
        print(f"   ✅ Screenshot Reference: {has_screenshot_ref}")
        print(f"   ✅ Metadata Section: {has_metadata_section}")
        print(f"   ✅ AI Analysis Section: {has_ai_analysis}")
        print(f"   📊 Content Size: {len(content)} characters")
        
        # Check YAML frontmatter details
        if has_frontmatter:
            frontmatter_end = content.find('---', 3)
            if frontmatter_end > 0:
                frontmatter = content[4:frontmatter_end]
                print(f"   🏷️  Contains type field: {'type:' in frontmatter}")
                print(f"   🏷️  Contains status field: {'status:' in frontmatter}")
                print(f"   🏷️  Contains tags field: {'tags:' in frontmatter}")
                print(f"   📱 Contains device_type: {'device_type:' in frontmatter}")


def main():
    """Main demo execution"""
    print("🎯 Samsung Screenshot Individual Processing - Real Data Demo")
    print("=" * 60)
    
    try:
        # Step 1: Test utility classes
        test_individual_processing_utilities()
        
        # Step 2: Find real Samsung screenshots
        screenshots = find_samsung_screenshots()
        
        # Step 3: Create demo knowledge base
        knowledge_path = create_demo_knowledge_base()
        
        # Step 4: Run the complete individual processing demo
        success = run_real_data_demo(screenshots, knowledge_path)
        
        # Step 5: Analyze results
        if success:
            analyze_results(knowledge_path)
        
        print(f"\n🎉 Demo completed! Results saved to: {knowledge_path}")
        print(f"📁 You can explore the generated individual notes in: {knowledge_path / 'Inbox'}")
        
        # Optional: Clean up
        response = input("\n🗑️  Clean up demo files? (y/N): ")
        if response.lower() == 'y':
            shutil.rmtree(knowledge_path.parent)
            print("✅ Demo files cleaned up")
        else:
            print(f"📁 Demo files preserved at: {knowledge_path.parent}")
            
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
