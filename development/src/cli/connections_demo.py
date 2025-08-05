#!/usr/bin/env python3
"""
Demo CLI for AI-powered connection discovery.
"""

import sys
import os
import argparse
from pathlib import Path
import glob

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..ai.connections import AIConnections


def load_note_corpus(directory: str) -> dict:
    """Load all markdown files from a directory."""
    corpus = {}
    md_files = glob.glob(os.path.join(directory, "**/*.md"), recursive=True)
    
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Use relative path as key
                rel_path = os.path.relpath(file_path, directory)
                corpus[rel_path] = content
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
    
    return corpus


def load_single_note(file_path: str) -> str:
    """Load content from a single note file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="AI-powered connection discovery demo")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Similar notes command
    similar_parser = subparsers.add_parser("similar", help="Find notes similar to a target note")
    similar_parser.add_argument("target", help="Path to the target note file")
    similar_parser.add_argument("corpus_dir", help="Directory containing note corpus")
    similar_parser.add_argument("--threshold", type=float, default=0.7,
                               help="Similarity threshold (0.0-1.0)")
    similar_parser.add_argument("--max-results", type=int, default=5,
                               help="Maximum number of results")
    
    # Link suggestions command
    links_parser = subparsers.add_parser("links", help="Suggest links for a note")
    links_parser.add_argument("target", help="Path to the target note file")
    links_parser.add_argument("corpus_dir", help="Directory containing note corpus")
    links_parser.add_argument("--threshold", type=float, default=0.7,
                             help="Similarity threshold (0.0-1.0)")
    
    # Connection map command
    map_parser = subparsers.add_parser("map", help="Build connection map for all notes")
    map_parser.add_argument("corpus_dir", help="Directory containing note corpus")
    map_parser.add_argument("--threshold", type=float, default=0.7,
                           help="Similarity threshold (0.0-1.0)")
    map_parser.add_argument("--output", help="Output file for connection map (JSON)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize connections system
    connections = AIConnections(
        similarity_threshold=args.threshold,
        max_suggestions=getattr(args, 'max_results', 5)
    )
    
    if args.command == "similar":
        print(f"🎯 Finding notes similar to: {args.target}")
        print(f"📁 Searching in: {args.corpus_dir}")
        print(f"🎚️  Threshold: {args.threshold}")
        print("-" * 60)
        
        # Load target note and corpus
        target_content = load_single_note(args.target)
        corpus = load_note_corpus(args.corpus_dir)
        
        print(f"📚 Loaded {len(corpus)} notes from corpus")
        print("🤖 Finding similar notes...")
        
        try:
            similar_notes = connections.find_similar_notes(target_content, corpus)
            
            if similar_notes:
                print(f"✅ Found {len(similar_notes)} similar notes:")
                print("-" * 60)
                for i, (filename, similarity) in enumerate(similar_notes, 1):
                    print(f"{i}. {filename}")
                    print(f"   Similarity: {similarity:.1%}")
                    print()
            else:
                print("ℹ️  No similar notes found above the threshold.")
                
        except Exception as e:
            print(f"❌ Error finding similar notes: {e}")
    
    elif args.command == "links":
        print(f"🔗 Suggesting links for: {args.target}")
        print(f"📁 Searching in: {args.corpus_dir}")
        print(f"🎚️  Threshold: {args.threshold}")
        print("-" * 60)
        
        # Load target note and corpus
        target_content = load_single_note(args.target)
        corpus = load_note_corpus(args.corpus_dir)
        
        print(f"📚 Loaded {len(corpus)} notes from corpus")
        print("🤖 Generating link suggestions...")
        
        try:
            suggestions = connections.suggest_links(target_content, corpus)
            
            if suggestions:
                print(f"✅ Generated {len(suggestions)} link suggestions:")
                print("-" * 60)
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. [[{suggestion['filename']}]]")
                    print(f"   Reason: {suggestion['reason']}")
                    print()
            else:
                print("ℹ️  No link suggestions found above the threshold.")
                
        except Exception as e:
            print(f"❌ Error generating link suggestions: {e}")
    
    elif args.command == "map":
        print(f"🗺️  Building connection map for: {args.corpus_dir}")
        print(f"🎚️  Threshold: {args.threshold}")
        print("-" * 60)
        
        # Load corpus
        corpus = load_note_corpus(args.corpus_dir)
        print(f"📚 Loaded {len(corpus)} notes from corpus")
        print("🤖 Building connection map...")
        
        try:
            connection_map = connections.build_connection_map(corpus)
            
            # Display summary
            total_connections = sum(len(connections) for connections in connection_map.values())
            connected_notes = sum(1 for connections in connection_map.values() if connections)
            
            print(f"✅ Connection map built successfully!")
            print("-" * 60)
            print(f"📊 Statistics:")
            print(f"   Total notes: {len(corpus)}")
            print(f"   Connected notes: {connected_notes}")
            print(f"   Total connections: {total_connections}")
            print(f"   Average connections per note: {total_connections / len(corpus):.1f}")
            print()
            
            # Show top connected notes
            sorted_notes = sorted(connection_map.items(), key=lambda x: len(x[1]), reverse=True)
            print("🔗 Most connected notes:")
            for filename, connections in sorted_notes[:5]:
                if connections:
                    print(f"   {filename}: {len(connections)} connections")
            
            # Save to file if requested
            if args.output:
                import json
                # Convert to JSON-serializable format
                json_map = {
                    filename: [(conn[0], float(conn[1])) for conn in connections]
                    for filename, connections in connection_map.items()
                }
                with open(args.output, 'w') as f:
                    json.dump(json_map, f, indent=2)
                print(f"\n💾 Connection map saved to: {args.output}")
                
        except Exception as e:
            print(f"❌ Error building connection map: {e}")


if __name__ == "__main__":
    main()
