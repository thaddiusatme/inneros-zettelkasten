"""
Automatic note processing with file watching capabilities.
Integrates with existing workflow to provide real-time AI assistance.
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Callable
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    Observer = None
    FileSystemEventHandler = None

from .tagger import AITagger
from .summarizer import AISummarizer
from .connections import AIConnections
from .enhancer import AIEnhancer


class NoteProcessor:
    """Processes notes with AI features and updates metadata."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize note processor with AI components."""
        self.config = config or {}

        # Initialize AI components
        self.tagger = AITagger()
        self.summarizer = AISummarizer()
        self.connections = AIConnections()
        self.enhancer = AIEnhancer()

        # Processing settings
        self.auto_tag = self.config.get("auto_tag", True)
        self.auto_summarize = self.config.get("auto_summarize", True)
        self.auto_enhance = self.config.get("auto_enhance", False)  # More conservative default

        # Callbacks for processing events
        self.callbacks: List[Callable] = []

    def add_callback(self, callback: Callable):
        """Add callback function to be called after processing."""
        self.callbacks.append(callback)

    def process_note(self, file_path: str) -> Dict:
        """
        Process a single note with AI features.
        
        Args:
            file_path: Path to the note file
            
        Returns:
            Processing results dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read file: {e}"}

        results = {
            "file_path": file_path,
            "timestamp": time.time(),
            "processing": {}
        }

        # Extract existing frontmatter
        frontmatter, body = self._extract_frontmatter(content)

        # Auto-tagging
        if self.auto_tag:
            try:
                new_tags = self.tagger.generate_tags(content)
                existing_tags = frontmatter.get("tags", [])

                # Merge tags intelligently
                merged_tags = self._merge_tags(existing_tags, new_tags)

                if merged_tags != existing_tags:
                    frontmatter["tags"] = merged_tags
                    results["processing"]["tags"] = {
                        "added": list(set(merged_tags) - set(existing_tags)),
                        "total": len(merged_tags)
                    }
            except Exception as e:
                results["processing"]["tags"] = {"error": str(e)}

        # Auto-summarization for long notes
        if self.auto_summarize and self.summarizer.should_summarize(content):
            try:
                summary = self.summarizer.generate_summary(content)
                if summary:
                    frontmatter["ai_summary"] = summary
                    results["processing"]["summary"] = {
                        "generated": True,
                        "length": len(summary.split())
                    }
            except Exception as e:
                results["processing"]["summary"] = {"error": str(e)}

        # Enhancement analysis
        if self.auto_enhance:
            try:
                enhancement = self.enhancer.enhance_note(content)
                if enhancement.get("suggestions"):
                    frontmatter["ai_suggestions"] = enhancement["suggestions"][:3]  # Limit suggestions
                    results["processing"]["enhancement"] = {
                        "quality_score": enhancement.get("quality_score", 0),
                        "suggestions_count": len(enhancement["suggestions"])
                    }
            except Exception as e:
                results["processing"]["enhancement"] = {"error": str(e)}

        # Update file if changes were made
        if any(key in results["processing"] for key in ["tags", "summary", "enhancement"]):
            try:
                updated_content = self._rebuild_content(frontmatter, body)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                results["file_updated"] = True
            except Exception as e:
                results["file_update_error"] = str(e)

        # Call registered callbacks
        for callback in self.callbacks:
            try:
                callback(file_path, results)
            except Exception:
                pass  # Don't let callback errors break processing

        return results

    def _extract_frontmatter(self, content: str) -> tuple:
        """Extract YAML frontmatter and body content."""
        import re

        # Check for YAML frontmatter
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(yaml_pattern, content, re.DOTALL)

        if match:
            yaml_content = match.group(1)
            body = match.group(2)

            # Parse YAML (simple parsing for common cases)
            frontmatter = {}
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle lists
                    if value.startswith('[') and value.endswith(']'):
                        # Simple list parsing
                        items = value[1:-1].split(',')
                        frontmatter[key] = [item.strip().strip('"\'') for item in items if item.strip()]
                    else:
                        frontmatter[key] = value.strip('"\'')

            return frontmatter, body
        else:
            return {}, content

    def _merge_tags(self, existing_tags: List[str], new_tags: List[str]) -> List[str]:
        """Intelligently merge existing and new tags."""
        # Convert to sets for easier manipulation
        existing_set = set(existing_tags) if existing_tags else set()
        new_set = set(new_tags) if new_tags else set()

        # Combine and sort
        merged = sorted(list(existing_set | new_set))

        # Limit total tags to prevent bloat
        max_tags = self.config.get("max_tags", 10)
        return merged[:max_tags]

    def _rebuild_content(self, frontmatter: Dict, body: str) -> str:
        """Rebuild content with updated frontmatter."""
        if not frontmatter:
            return body

        yaml_lines = ["---"]

        # Preserve order of common fields
        field_order = ["type", "created", "status", "tags", "ai_summary", "ai_suggestions"]

        # Add ordered fields first
        for field in field_order:
            if field in frontmatter:
                value = frontmatter[field]
                if isinstance(value, list):
                    if value:  # Only add non-empty lists
                        formatted_list = "[" + ", ".join(f'"{item}"' if isinstance(item, str) else str(item) for item in value) + "]"
                        yaml_lines.append(f"{field}: {formatted_list}")
                else:
                    yaml_lines.append(f"{field}: {value}")

        # Add any remaining fields
        for key, value in frontmatter.items():
            if key not in field_order:
                if isinstance(value, list):
                    if value:
                        formatted_list = "[" + ", ".join(f'"{item}"' if isinstance(item, str) else str(item) for item in value) + "]"
                        yaml_lines.append(f"{key}: {formatted_list}")
                else:
                    yaml_lines.append(f"{key}: {value}")

        yaml_lines.append("---")
        yaml_lines.append("")

        return "\n".join(yaml_lines) + body


if HAS_WATCHDOG:
    class NoteWatcher(FileSystemEventHandler):
        """File system event handler for automatic note processing."""

        def __init__(self, processor: NoteProcessor, watch_patterns: List[str] = None):
            """
            Initialize note watcher.
            
            Args:
                processor: NoteProcessor instance
                watch_patterns: File patterns to watch (default: ["*.md"])
            """
            super().__init__()
            self.processor = processor
            self.watch_patterns = watch_patterns or ["*.md"]
            self.processing_queue = set()  # Prevent duplicate processing

        def should_process_file(self, file_path: str) -> bool:
            """Check if file should be processed."""
            path = Path(file_path)

            # Check if it matches our patterns
            for pattern in self.watch_patterns:
                if path.match(pattern):
                    return True

            return False

        def on_modified(self, event):
            """Handle file modification events."""
            if not event.is_directory and self.should_process_file(event.src_path):
                # Debounce rapid changes
                if event.src_path not in self.processing_queue:
                    self.processing_queue.add(event.src_path)

                    # Process after short delay to handle rapid saves
                    import threading
                    def delayed_process():
                        time.sleep(0.5)  # Wait for file to stabilize
                        try:
                            result = self.processor.process_note(event.src_path)
                            print(f"📝 Processed: {Path(event.src_path).name}")
                            if result.get("processing"):
                                changes = []
                                if "tags" in result["processing"]:
                                    tag_info = result["processing"]["tags"]
                                    if "added" in tag_info and tag_info["added"]:
                                        changes.append(f"Added tags: {', '.join(tag_info['added'])}")
                                if "summary" in result["processing"]:
                                    changes.append("Generated summary")
                                if changes:
                                    print(f"   Changes: {'; '.join(changes)}")
                        except Exception as e:
                            print(f"❌ Error processing {event.src_path}: {e}")
                        finally:
                            self.processing_queue.discard(event.src_path)

                    thread = threading.Thread(target=delayed_process)
                    thread.daemon = True
                    thread.start()
else:
    class NoteWatcher:
        """Placeholder class when watchdog is not available."""

        def __init__(self, processor: NoteProcessor, watch_patterns: List[str] = None):
            raise ImportError("watchdog library is required for file watching. Install with: pip install watchdog")


class AutoProcessor:
    """Main class for automatic note processing with file watching."""

    def __init__(self, watch_directories: List[str], config: Optional[Dict] = None):
        """
        Initialize auto processor.
        
        Args:
            watch_directories: Directories to watch for changes
            config: Configuration options
        """
        self.watch_directories = [Path(d) for d in watch_directories]
        self.config = config or {}

        # Initialize processor and watcher
        self.processor = NoteProcessor(config)
        self.watcher = NoteWatcher(self.processor)

        # File system observer
        self.observer = Observer()

    def start_watching(self):
        """Start watching directories for changes."""
        print("🔍 Starting automatic note processing...")

        for directory in self.watch_directories:
            if directory.exists():
                self.observer.schedule(self.watcher, str(directory), recursive=True)
                print(f"   Watching: {directory}")
            else:
                print(f"   Warning: Directory not found: {directory}")

        self.observer.start()
        print("✅ Auto-processing started. Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_watching()

    def stop_watching(self):
        """Stop watching directories."""
        print("\n🛑 Stopping auto-processor...")
        self.observer.stop()
        self.observer.join()
        print("✅ Auto-processor stopped.")

    def process_existing_notes(self, directory: str):
        """Process all existing notes in a directory."""
        dir_path = Path(directory)
        md_files = list(dir_path.rglob("*.md"))

        print(f"📁 Processing {len(md_files)} existing notes in {directory}...")

        processed = 0
        for file_path in md_files:
            try:
                result = self.processor.process_note(str(file_path))
                if result.get("file_updated"):
                    processed += 1
                    print(f"   ✅ Updated: {file_path.name}")
            except Exception as e:
                print(f"   ❌ Error: {file_path.name} - {e}")

        print(f"📊 Processed {processed}/{len(md_files)} files")


def main():
    """CLI entry point for auto-processor."""
    import argparse

    parser = argparse.ArgumentParser(description="Automatic AI-powered note processing")
    parser.add_argument("directories", nargs="+", help="Directories to watch")
    parser.add_argument("--process-existing", action="store_true",
                       help="Process existing notes before watching")
    parser.add_argument("--no-auto-tag", action="store_true",
                       help="Disable automatic tagging")
    parser.add_argument("--no-auto-summarize", action="store_true",
                       help="Disable automatic summarization")
    parser.add_argument("--enable-auto-enhance", action="store_true",
                       help="Enable automatic enhancement suggestions")

    args = parser.parse_args()

    # Build configuration
    config = {
        "auto_tag": not args.no_auto_tag,
        "auto_summarize": not args.no_auto_summarize,
        "auto_enhance": args.enable_auto_enhance
    }

    # Initialize auto processor
    auto_processor = AutoProcessor(args.directories, config)

    # Process existing notes if requested
    if args.process_existing:
        for directory in args.directories:
            auto_processor.process_existing_notes(directory)

    # Start watching
    auto_processor.start_watching()


if __name__ == "__main__":
    main()
