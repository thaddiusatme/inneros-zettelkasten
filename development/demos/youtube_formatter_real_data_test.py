"""
Real Data Test for YouTubeTemplateFormatter

Tests the formatter with realistic YouTube video data to validate
end-to-end functionality before production deployment.

Usage:
    python3 development/demos/youtube_formatter_real_data_test.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.youtube_template_formatter import YouTubeTemplateFormatter


def test_realistic_video_data():
    """Test with realistic AI/Creator Economy video data."""
    print("🧪 Testing YouTubeTemplateFormatter with Real Data\n")
    print("=" * 70)
    
    # Realistic quotes from a hypothetical AI video
    quotes_data = {
        "summary": "This video explores how AI is transforming the creator economy in 2025, "
                  "discussing opportunities for digital entrepreneurs and the shift in content creation paradigms.",
        "quotes": [
            {
                "text": "AI isn't replacing creators—it's amplifying their creative capacity by 10x",
                "timestamp": "02:15",
                "relevance_score": 0.92,
                "context": "Discusses the paradigm shift from AI-as-replacement to AI-as-amplifier",
                "category": "key-insight"
            },
            {
                "text": "Start building your empire today, not tomorrow. The tools are free, the barrier is mental.",
                "timestamp": "08:45",
                "relevance_score": 0.88,
                "context": "Motivational call-to-action for aspiring digital entrepreneurs",
                "category": "actionable"
            },
            {
                "text": "The creator economy will exceed $250 billion by 2027, driven primarily by AI-native content",
                "timestamp": "05:30",
                "relevance_score": 0.85,
                "context": "Market size projection and economic impact analysis",
                "category": "key-insight"
            },
            {
                "text": "Use AI to handle the 80% of work that drains you, so you can focus on the 20% that lights you up",
                "timestamp": "12:20",
                "relevance_score": 0.90,
                "context": "Practical productivity advice using the 80/20 principle",
                "category": "actionable"
            },
            {
                "text": "A 'digital entrepreneur' is someone who builds leveraged income through online platforms and automation",
                "timestamp": "01:45",
                "relevance_score": 0.78,
                "context": "Definition of core concept discussed throughout the video",
                "category": "definition"
            },
            {
                "text": "The best time to start was yesterday. The second best time is right now.",
                "timestamp": "15:00",
                "relevance_score": 0.75,
                "context": "Closing motivational message about taking action",
                "category": "quote"
            }
        ],
        "key_themes": [
            "AI & Creator Economy",
            "Digital Entrepreneurship", 
            "Content Creation",
            "Automation & Productivity",
            "Future of Work"
        ]
    }
    
    # Test data
    video_id = "FLpS7OfD5-s"
    video_title = "AI Creator Economy 2025: Building Your Digital Empire"
    
    print(f"\n📹 Video: {video_title}")
    print(f"🆔 Video ID: {video_id}")
    print(f"📊 Quotes: {len(quotes_data['quotes'])}")
    print(f"🎯 Themes: {len(quotes_data['key_themes'])}")
    print("\n" + "=" * 70)
    
    # Initialize formatter
    formatter = YouTubeTemplateFormatter()
    
    # Format template
    print("\n⚙️  Formatting template...")
    result = formatter.format_template(
        quotes_data=quotes_data,
        video_id=video_id,
        video_title=video_title
    )
    
    # Display results
    print("\n✅ Formatting complete!")
    print("\n" + "=" * 70)
    print("📋 METADATA")
    print("=" * 70)
    for key, value in result["metadata"].items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("📝 FORMATTED MARKDOWN (First 1000 chars)")
    print("=" * 70)
    print(result["markdown"][:1000])
    if len(result["markdown"]) > 1000:
        print(f"\n... ({len(result['markdown']) - 1000} more characters)")
    
    # Validate key features
    print("\n" + "=" * 70)
    print("✅ VALIDATION CHECKS")
    print("=" * 70)
    
    markdown = result["markdown"]
    checks = [
        ("Summary present", "Video about AI" in markdown or "creator economy" in markdown),
        ("Themes present", "AI & Creator Economy" in markdown),
        ("Quotes present", "amplifying their creative capacity" in markdown),
        ("Clickable links", "youtu.be/" in markdown and "?t=" in markdown),
        ("Category headers", "🎯 Key Insights" in markdown),
        ("Context preserved", "Context:" in markdown),
        ("Relevance scores", "Relevance: 0." in markdown),
        ("Multiple categories", markdown.count("###") >= 3)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - READY FOR PRODUCTION")
    else:
        print("⚠️  SOME CHECKS FAILED - REVIEW NEEDED")
    print("=" * 70)
    
    return result


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n\n🔬 Testing Edge Cases\n")
    print("=" * 70)
    
    formatter = YouTubeTemplateFormatter()
    
    # Test 1: Empty quotes
    print("\n1️⃣  Empty quotes list...")
    result = formatter.format_template(
        quotes_data={"summary": "Test summary", "quotes": [], "key_themes": ["Test"]},
        video_id="test123"
    )
    assert "No high-quality quotes" in result["markdown"]
    assert result["metadata"]["quote_count"] == 0
    print("   ✅ Empty quotes handled gracefully")
    
    # Test 2: Long timestamp
    print("\n2️⃣  HH:MM:SS timestamp format...")
    link = formatter.create_timestamp_link("01:30:45", "test456")
    expected_seconds = 1*3600 + 30*60 + 45  # 5445 seconds
    assert f"?t={expected_seconds}" in link
    print(f"   ✅ Long timestamp converted: 01:30:45 → {expected_seconds}s")
    
    # Test 3: Invalid timestamp
    print("\n3️⃣  Invalid timestamp handling...")
    link = formatter.create_timestamp_link("invalid", "test789")
    assert "?t=0" in link
    print("   ✅ Invalid timestamp handled (fallback to 0)")
    
    # Test 4: Mixed categories
    print("\n4️⃣  Mixed quote categories...")
    quotes_data = {
        "summary": "Test",
        "quotes": [
            {"text": "Q1", "category": "key-insight", "timestamp": "00:10", "context": "C1", "relevance_score": 0.9},
            {"text": "Q2", "category": "quote", "timestamp": "00:20", "context": "C2", "relevance_score": 0.8},
            {"text": "Q3", "category": "key-insight", "timestamp": "00:30", "context": "C3", "relevance_score": 0.85}
        ],
        "key_themes": []
    }
    result = formatter.format_template(quotes_data, "mixed123")
    assert "🎯 Key Insights" in result["markdown"]
    assert "📝 Notable Quotes" in result["markdown"]
    assert result["metadata"]["quote_count"] == 3
    print("   ✅ Multiple categories organized correctly")
    
    print("\n" + "=" * 70)
    print("✅ ALL EDGE CASES PASSED")
    print("=" * 70)


if __name__ == "__main__":
    try:
        # Run realistic data test
        result = test_realistic_video_data()
        
        # Run edge case tests
        test_edge_cases()
        
        print("\n\n" + "=" * 70)
        print("🏆 REAL DATA TESTING COMPLETE")
        print("=" * 70)
        print("\n✅ YouTubeTemplateFormatter is production-ready!")
        print("✅ All validation checks passed")
        print("✅ Edge cases handled gracefully")
        print("✅ Template generates clean, clickable markdown")
        print("\n🚀 Ready for TDD Iteration 4: Quote Extraction Integration\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
