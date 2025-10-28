#!/usr/bin/env python3
"""
Demo CLI for AI-powered note summarization.
"""

import sys
import argparse
from pathlib import Path

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.summarizer import AISummarizer


def load_note_content(file_path: str) -> str:
    """Load content from a note file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="AI-powered note summarization demo")
    parser.add_argument("file", help="Path to the note file to summarize")
    parser.add_argument(
        "--type",
        choices=["abstractive", "extractive"],
        default="abstractive",
        help="Type of summary to generate",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=500,
        help="Minimum word count to trigger summarization",
    )
    parser.add_argument(
        "--sentences",
        type=int,
        default=3,
        help="Number of sentences for extractive summary",
    )

    args = parser.parse_args()

    # Load note content
    content = load_note_content(args.file)

    # Initialize summarizer
    summarizer = AISummarizer(min_length=args.min_length)

    print(f"📄 Analyzing: {args.file}")
    print(f"📊 Content length: {len(content.split())} words")
    print(f"🔍 Summary type: {args.type}")
    print("-" * 60)

    # Check if summarization is needed
    if not summarizer.should_summarize(content):
        print(
            "ℹ️  Note is too short for summarization (less than {} words)".format(
                args.min_length
            )
        )
        return

    try:
        print("🤖 Generating summary...")

        if args.type == "extractive":
            summary = summarizer.generate_extractive_summary(
                content, num_sentences=args.sentences
            )
        else:
            summary = summarizer.generate_summary(content, summary_type="abstractive")

        if summary:
            print("✅ Summary generated successfully!")
            print("-" * 60)
            print("📝 SUMMARY:")
            print(summary)
            print("-" * 60)
            print(f"📊 Summary length: {len(summary.split())} words")
            print(
                f"📉 Compression ratio: {len(summary.split()) / len(content.split()):.1%}"
            )
        else:
            print("❌ Failed to generate summary. Check if Ollama is running.")

    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
