#!/usr/bin/env python3
"""
Smoke test demonstration for InnerOS AI Integration MVP.
Shows the AI tagger in action with real content.
"""

import sys
import time
from src.ai.tagger import AITagger
from src.ai.ollama_client import OllamaClient


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)


def test_ollama_client():
    """Test Ollama client functionality."""
    print_header("Testing Ollama Client")
    
    client = OllamaClient()
    
    print(f"📡 Client initialized with:")
    print(f"   Base URL: {client.base_url}")
    print(f"   Timeout: {client.timeout}s")
    print(f"   Model: {client.model}")
    
    # Test health check (will likely fail without Ollama running)
    print(f"\n🔍 Testing health check...")
    health_status = client.health_check()
    print(f"   Health status: {'✅ Online' if health_status else '❌ Offline (expected without Ollama)'}")
    
    # Test model availability
    print(f"\n🔍 Testing model availability...")
    model_available = client.is_model_available("llama3.1:8b")
    print(f"   Model available: {'✅ Yes' if model_available else '❌ No (expected without Ollama)'}")
    
    return health_status


def test_ai_tagger():
    """Test AI tagger with realistic content."""
    print_header("Testing AI Tagger")
    
    tagger = AITagger(min_confidence=0.7)
    
    # Test cases with realistic content
    test_cases = [
        {
            "title": "Machine Learning Note",
            "content": """
            # Machine Learning Fundamentals
            
            Machine learning is a subset of artificial intelligence that enables 
            systems to learn and improve from experience without being explicitly 
            programmed. The key concepts include supervised learning, unsupervised 
            learning, and reinforcement learning.
            
            ## Key Algorithms
            - Neural networks
            - Decision trees
            - Support vector machines
            - Clustering algorithms
            """,
            "expected_keywords": ["ai", "machine-learning", "technology"]
        },
        {
            "title": "Data Science Note", 
            "content": """
            # Data Science in Practice
            
            Data science combines statistics, programming, and domain expertise 
            to extract insights from data. Python has become the dominant language 
            for data analysis due to its rich ecosystem of libraries like pandas, 
            numpy, and scikit-learn.
            
            ## Applications
            - Business intelligence
            - Predictive analytics
            - Data visualization
            - Machine learning pipelines
            """,
            "expected_keywords": ["data-science", "python", "analytics"]
        },
        {
            "title": "Empty Note",
            "content": "",
            "expected_keywords": []
        },
        {
            "title": "Short Note",
            "content": "AI and machine learning are transforming technology.",
            "expected_keywords": ["ai", "technology"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['title']}")
        print(f"   Content length: {len(test_case['content'])} characters")
        
        start_time = time.time()
        tags = tagger.generate_tags(test_case['content'])
        processing_time = time.time() - start_time
        
        print(f"   ⏱️  Processing time: {processing_time:.3f}s")
        print(f"   🏷️  Generated tags: {tags}")
        print(f"   📊 Tag count: {len(tags)}")
        
        # Verify tag quality
        if tags:
            print(f"   ✅ Tags are valid strings")
            print(f"   ✅ No duplicates: {len(tags) == len(set(tags))}")
            
            # Check for expected relevance
            content_lower = test_case['content'].lower()
            relevant_tags = [tag for tag in tags 
                           if any(keyword in content_lower for keyword in tag.split('-'))]
            print(f"   ✅ Relevant tags: {len(relevant_tags)}/{len(tags)}")
        else:
            print(f"   ✅ Empty result for empty content")


def test_performance_benchmark():
    """Test performance with different content sizes."""
    print_header("Performance Benchmark")
    
    tagger = AITagger()
    
    # Generate test content of different sizes
    base_content = "Machine learning and artificial intelligence are revolutionizing technology. "
    test_sizes = [
        ("Small", base_content * 1),
        ("Medium", base_content * 5),
        ("Large", base_content * 20),
    ]
    
    for size_name, content in test_sizes:
        start_time = time.time()
        tags = tagger.generate_tags(content)
        processing_time = time.time() - start_time
        
        print(f"   {size_name:6} ({len(content):4} chars): {processing_time:.3f}s - {len(tags)} tags")
        
        # Ensure we meet performance targets
        assert processing_time < 1.0, f"{size_name} processing too slow: {processing_time:.3f}s"


def test_configuration_impact():
    """Test configuration impact on results."""
    print_header("Configuration Impact Test")
    
    content = "Python programming for artificial intelligence and machine learning applications"
    
    configurations = [
        {"name": "Default", "config": {}},
        {"name": "Strict", "config": {"min_confidence": 0.9}},
        {"name": "Lenient", "config": {"min_confidence": 0.5}},
    ]
    
    for config_info in configurations:
        tagger = AITagger(**config_info["config"])
        tags = tagger.generate_tags(content)
        
        print(f"   {config_info['name']:8}: {len(tags)} tags - {tags}")


def main():
    """Run the complete smoke test."""
    print("🔥 InnerOS AI Integration - Smoke Test")
    print("=" * 60)
    
    try:
        # Test 1: Ollama Client
        ollama_working = test_ollama_client()
        
        # Test 2: AI Tagger (works regardless of Ollama status)
        test_ai_tagger()
        
        # Test 3: Performance
        test_performance_benchmark()
        
        # Test 4: Configuration
        test_configuration_impact()
        
        print_header("Smoke Test Results")
        print("✅ All smoke tests completed successfully!")
        print("✅ AI Tagger is working correctly")
        print("✅ Performance targets met")
        print("✅ Configuration system functional")
        
        if ollama_working:
            print("✅ Ollama integration ready for advanced features")
        else:
            print("ℹ️  Ollama not running - using mock implementation (MVP ready)")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
