#!/usr/bin/env python3
"""
CLI demonstration of AI-powered content enhancement for zettelkasten notes.

This script provides a command-line interface to test the AI Enhancer functionality
on markdown notes in the zettelkasten system.
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.enhancer import AIEnhancer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="AI Content Enhancement Demo")
    parser.add_argument("file", help="Path to markdown file to analyze")
    parser.add_argument("--model", default="llama3:latest", help="Ollama model to use")
    parser.add_argument(
        "--min-score", type=float, default=0.6, help="Minimum quality score threshold"
    )
    parser.add_argument("--links", action="store_true", help="Show link suggestions")
    parser.add_argument(
        "--structure", action="store_true", help="Show structure suggestions"
    )
    parser.add_argument(
        "--full", action="store_true", help="Show full enhancement report"
    )

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    print("🤖 AI Content Enhancement Analysis")
    print(f"📄 File: {args.file}")
    print(f"🧠 Model: {args.model}")
    print("=" * 50)

    try:
        enhancer = AIEnhancer(model_name=args.model, min_quality_score=args.min_score)

        if args.full:
            # Full enhancement report
            result = enhancer.enhance_note(content)

            print(f"📊 Quality Score: {result['quality_score']:.2f}/1.0")

            if result["suggestions"]:
                print("\n💡 Suggestions:")
                for suggestion in result["suggestions"]:
                    print(f"  • {suggestion}")

            if result["missing_elements"]:
                print("\n⚠️  Missing Elements:")
                for element in result["missing_elements"]:
                    print(f"  • {element['type']}: {element['description']}")

            if args.links and result["link_suggestions"]:
                print("\n🔗 Link Suggestions:")
                for link in result["link_suggestions"]:
                    print(f"  • {link}")

            if args.structure and result["structure_suggestions"]:
                print("\n🏗️  Structure Suggestions:")
                print(f"  Reasoning: {result['structure_suggestions']['reasoning']}")
                print("  Recommended Structure:")
                for heading in result["structure_suggestions"]["recommended_structure"]:
                    print(f"    {heading}")

        else:
            # Basic quality analysis
            analysis = enhancer.analyze_note_quality(content)
            print(f"📊 Quality Score: {analysis['quality_score']:.2f}/1.0")

            if analysis["suggestions"]:
                print("\n💡 Suggestions:")
                for suggestion in analysis["suggestions"]:
                    print(f"  • {suggestion}")

    except Exception as e:
        print(f"Error during analysis: {e}")
        print("Note: Make sure Ollama is running with: ollama serve")
        sys.exit(1)


if __name__ == "__main__":
    main()
