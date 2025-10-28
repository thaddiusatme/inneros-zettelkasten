#!/usr/bin/env python3
"""
Unified AI Assistant CLI for InnerOS Zettelkasten
Combines tagging, summarization, and connection discovery
"""

import sys
import argparse
from pathlib import Path
import json
from typing import Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..ai.tagger import AITagger
from ..ai.summarizer import AISummarizer
from ..ai.connections import AIConnections
from ..ai.enhancer import AIEnhancer
from ..ai.ollama_client import OllamaClient


class AIAssistant:
    """Unified AI assistant for note processing."""

    def __init__(self):
        """Initialize AI components."""
        self.client = OllamaClient()
        self.tagger = AITagger()
        self.summarizer = AISummarizer()
        self.connections = AIConnections()
        self.enhancer = AIEnhancer()

        # Check API availability
        self.api_available = self.client.health_check()
        if not self.api_available:
            print("⚠️  Ollama service not available - some features will be limited")

    def process_note(self, file_path: str, output_format: str = "json") -> Dict:
        """Process a single note with all AI features."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read file: {e}"}

        results = {
            "file": file_path,
            "api_available": self.api_available,
            "word_count": len(content.split()),
            "processing_results": {},
        }

        # Generate tags
        print("🏷️  Generating tags...")
        try:
            tags = self.tagger.generate_tags(content)
            results["processing_results"]["tags"] = {
                "success": True,
                "tags": tags,
                "count": len(tags),
            }
        except Exception as e:
            results["processing_results"]["tags"] = {"success": False, "error": str(e)}

        # Generate summary if content is long enough
        if self.summarizer.should_summarize(content):
            print("📝 Generating summary...")
            try:
                abstractive = self.summarizer.generate_summary(content, "abstractive")
                extractive = self.summarizer.generate_extractive_summary(content)

                results["processing_results"]["summary"] = {
                    "success": True,
                    "abstractive": {
                        "content": abstractive,
                        "word_count": len(abstractive.split()) if abstractive else 0,
                    },
                    "extractive": {
                        "content": extractive,
                        "word_count": len(extractive.split()) if extractive else 0,
                    },
                }
            except Exception as e:
                results["processing_results"]["summary"] = {
                    "success": False,
                    "error": str(e),
                }
        else:
            results["processing_results"]["summary"] = {
                "success": False,
                "reason": "Content too short for summarization",
            }

        # Enhance note quality
        print("✨ Analyzing note quality...")
        try:
            enhancement = self.enhancer.enhance_note(content)
            results["processing_results"]["enhancement"] = {
                "success": True,
                "quality_score": enhancement.get("quality_score", 0),
                "suggestions": enhancement.get("suggestions", []),
                "missing_links": enhancement.get("missing_links", []),
            }
        except Exception as e:
            results["processing_results"]["enhancement"] = {
                "success": False,
                "error": str(e),
            }

        return results

    def find_connections(self, file_path: str, corpus_dir: str) -> Dict:
        """Find connections for a note within a corpus."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                target_content = f.read()
        except Exception as e:
            return {"error": f"Failed to read target file: {e}"}

        # Load corpus
        corpus = {}
        corpus_path = Path(corpus_dir)
        for md_file in corpus_path.rglob("*.md"):
            if md_file.name != Path(file_path).name:  # Exclude target file
                try:
                    with open(md_file, "r", encoding="utf-8") as f:
                        rel_path = str(md_file.relative_to(corpus_path))
                        corpus[rel_path] = f.read()
                except Exception:
                    continue

        print(f"🔍 Searching {len(corpus)} notes for connections...")

        try:
            similar_notes = self.connections.find_similar_notes(target_content, corpus)
            suggestions = self.connections.suggest_links(target_content, corpus)

            return {
                "target_file": file_path,
                "corpus_size": len(corpus),
                "similar_notes": [
                    {"file": filename, "similarity": float(score)}
                    for filename, score in similar_notes
                ],
                "link_suggestions": suggestions,
                "api_available": self.api_available,
            }
        except Exception as e:
            return {"error": f"Failed to find connections: {e}"}

    def batch_process(self, directory: str, pattern: str = "*.md") -> Dict:
        """Process multiple notes in batch."""
        dir_path = Path(directory)
        files = list(dir_path.rglob(pattern))

        print(f"📁 Processing {len(files)} files in batch...")

        results = {
            "directory": directory,
            "total_files": len(files),
            "processed": 0,
            "failed": 0,
            "results": [],
        }

        for file_path in files:
            print(f"Processing: {file_path.name}")
            result = self.process_note(str(file_path))

            if "error" in result:
                results["failed"] += 1
            else:
                results["processed"] += 1

            results["results"].append(result)

        return results


def main():
    parser = argparse.ArgumentParser(
        description="AI Assistant for InnerOS Zettelkasten"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process single note
    process_parser = subparsers.add_parser("process", help="Process a single note")
    process_parser.add_argument("file", help="Path to the note file")
    process_parser.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    # Find connections
    connect_parser = subparsers.add_parser(
        "connect", help="Find connections for a note"
    )
    connect_parser.add_argument("file", help="Path to the target note")
    connect_parser.add_argument("corpus", help="Directory containing note corpus")

    # Batch process
    batch_parser = subparsers.add_parser("batch", help="Process multiple notes")
    batch_parser.add_argument("directory", help="Directory to process")
    batch_parser.add_argument("--pattern", default="*.md", help="File pattern to match")
    batch_parser.add_argument("--output", help="Output file for results (JSON)")

    # Status check
    status_parser = subparsers.add_parser("status", help="Check AI service status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    assistant = AIAssistant()

    if args.command == "process":
        result = assistant.process_note(args.file, args.format)

        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            # Text format output
            print(f"📄 Processing: {result['file']}")
            print(f"📊 Word count: {result['word_count']}")
            print(
                f"🔌 API Status: {'✅ Available' if result['api_available'] else '❌ Unavailable'}"
            )
            print()

            # Tags
            tags_result = result["processing_results"].get("tags", {})
            if tags_result.get("success"):
                print(
                    f"🏷️  Tags ({tags_result['count']}): {', '.join(tags_result['tags'])}"
                )
            else:
                print(f"🏷️  Tags: ❌ {tags_result.get('error', 'Failed')}")

            # Summary
            summary_result = result["processing_results"].get("summary", {})
            if summary_result.get("success"):
                abs_summary = summary_result["abstractive"]
                ext_summary = summary_result["extractive"]
                print(f"📝 Abstractive Summary ({abs_summary['word_count']} words):")
                if abs_summary["content"]:
                    print(f"   {abs_summary['content'][:200]}...")
                print(f"📝 Extractive Summary ({ext_summary['word_count']} words):")
                if ext_summary["content"]:
                    print(f"   {ext_summary['content'][:200]}...")
            else:
                print(
                    f"📝 Summary: ❌ {summary_result.get('error', summary_result.get('reason', 'Failed'))}"
                )

            # Enhancement
            enhancement_result = result["processing_results"].get("enhancement", {})
            if enhancement_result.get("success"):
                print(
                    f"✨ Quality Score: {enhancement_result['quality_score']:.1f}/1.0"
                )
                if enhancement_result["suggestions"]:
                    print(
                        f"💡 Suggestions: {len(enhancement_result['suggestions'])} items"
                    )
                if enhancement_result["missing_links"]:
                    print(
                        f"🔗 Missing Links: {len(enhancement_result['missing_links'])} suggestions"
                    )
            else:
                print(f"✨ Enhancement: ❌ {enhancement_result.get('error', 'Failed')}")

    elif args.command == "connect":
        result = assistant.find_connections(args.file, args.corpus)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return

        print(f"🎯 Target: {result['target_file']}")
        print(f"📚 Corpus: {result['corpus_size']} notes")
        print(
            f"🔌 API: {'✅ Available' if result['api_available'] else '❌ Unavailable'}"
        )
        print()

        if result["similar_notes"]:
            print(f"🔗 Similar Notes ({len(result['similar_notes'])}):")
            for note in result["similar_notes"]:
                print(f"   • {note['file']} ({note['similarity']:.1%})")
        else:
            print("🔗 No similar notes found")

        if result["link_suggestions"]:
            print(f"\n💡 Link Suggestions ({len(result['link_suggestions'])}):")
            for suggestion in result["link_suggestions"]:
                print(f"   • [[{suggestion['filename']}]] - {suggestion['reason']}")
        else:
            print("\n💡 No link suggestions found")

    elif args.command == "batch":
        result = assistant.batch_process(args.directory, args.pattern)

        print("📁 Batch Processing Complete")
        print(f"   Total files: {result['total_files']}")
        print(f"   Processed: {result['processed']}")
        print(f"   Failed: {result['failed']}")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"💾 Results saved to: {args.output}")

    elif args.command == "status":
        print("🔍 AI Service Status Check")
        print(
            f"🔌 Ollama API: {'✅ Available' if assistant.api_available else '❌ Unavailable'}"
        )

        if assistant.api_available:
            print(f"🤖 Model: {assistant.client.model}")
            print(f"🌐 Base URL: {assistant.client.base_url}")
            print(f"⏱️  Timeout: {assistant.client.timeout}s")

            # Test basic functionality
            try:
                test_tags = assistant.tagger.generate_tags(
                    "This is a test note about machine learning."
                )
                print(f"🏷️  Tagging: ✅ Working ({len(test_tags)} tags generated)")
            except Exception as e:
                print(f"🏷️  Tagging: ❌ Error - {e}")

            try:
                test_content = "This is a test note. " * 100  # Make it long enough
                test_summary = assistant.summarizer.generate_summary(test_content)
                print("📝 Summarization: ✅ Working")
            except Exception as e:
                print(f"📝 Summarization: ❌ Error - {e}")
        else:
            print("💡 To enable AI features, start Ollama service:")
            print("   ollama serve")


if __name__ == "__main__":
    main()
