#!/usr/bin/env python3
"""
InnerOS Zettelkasten Administrative Layer
Python scripts for managing note administration and AI processing
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List, Optional
import logging

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai.tagger import AITagger
from ai.ollama_client import OllamaClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NoteAdmin:
    """Administrative layer for managing notes and AI processing"""
    
    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else Path.cwd()
        self.inbox_path = self.vault_path / "Inbox"
        self.ai_tagger = AITagger()
        logger.info(f"Initialized NoteAdmin for vault: {self.vault_path}")
    
    def process_inbox(self, dry_run: bool = False) -> List[str]:
        """Process all new notes in Inbox folder"""
        if not self.inbox_path.exists():
            logger.warning(f"Inbox folder not found: {self.inbox_path}")
            return []
        
        processed_notes = []
        
        for note_file in self.inbox_path.glob("*.md"):
            if note_file.is_file():
                logger.info(f"Processing: {note_file.name}")
                
                if not dry_run:
                    self._process_note(note_file)
                
                processed_notes.append(str(note_file))
        
        logger.info(f"Processed {len(processed_notes)} notes from inbox")
        return processed_notes
    
    def _process_note(self, note_path: Path) -> bool:
        """Process a single note file"""
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate tags
            tags = self.ai_tagger.generate_tags(content)
            
            if tags:
                logger.info(f"Generated tags for {note_path.name}: {tags}")
                # TODO: Update note with new tags
                return True
            
        except Exception as e:
            logger.error(f"Error processing {note_path.name}: {e}")
        
        return False
    
    def batch_tag(self, folder: str = None) -> List[str]:
        """Re-tag all notes in specified folder"""
        target_path = self.vault_path / folder if folder else self.vault_path
        
        if not target_path.exists():
            logger.error(f"Folder not found: {target_path}")
            return []
        
        tagged_notes = []
        
        for note_file in target_path.rglob("*.md"):
            if note_file.is_file() and not note_file.name.startswith('.'):
                logger.info(f"Re-tagging: {note_file.relative_to(self.vault_path)}")
                if self._process_note(note_file):
                    tagged_notes.append(str(note_file))
        
        return tagged_notes
    
    def find_connections(self, note_path: str = None) -> dict:
        """Find semantically similar notes"""
        logger.info("Finding connections between notes...")
        # TODO: Implement semantic similarity search
        return {}
    
    def summarize_note(self, note_path: str) -> Optional[str]:
        """Generate summary for a specific note"""
        note_file = Path(note_path)
        if not note_file.exists():
            logger.error(f"Note not found: {note_path}")
            return None
        
        try:
            with open(note_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # TODO: Implement summarization
            logger.info(f"Generated summary for: {note_file.name}")
            return "Summary placeholder"
            
        except Exception as e:
            logger.error(f"Error summarizing {note_file.name}: {e}")
            return None
    
    def watch_inbox(self):
        """Watch inbox folder for new files (blocking)"""
        logger.info(f"Watching inbox folder: {self.inbox_path}")
        logger.info("Press Ctrl+C to stop watching")
        
        try:
            while True:
                self.process_inbox()
                time.sleep(10)  # Check every 10 seconds
        except KeyboardInterrupt:
            logger.info("Stopped watching inbox")

def main():
    parser = argparse.ArgumentParser(description="InnerOS Zettelkasten Administrative Tools")
    parser.add_argument("--vault", help="Path to Obsidian vault", default=None)
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process inbox
    inbox_parser = subparsers.add_parser("process-inbox", help="Process all new notes in inbox")
    inbox_parser.add_argument("--dry-run", action="store_true", help="Show what would be processed")
    
    # Batch tagging
    batch_parser = subparsers.add_parser("batch-tag", help="Re-tag notes in folder")
    batch_parser.add_argument("--folder", help="Folder to process (default: entire vault)")
    
    # Find connections
    conn_parser = subparsers.add_parser("find-connections", help="Find related notes")
    conn_parser.add_argument("--note", help="Specific note to find connections for")
    
    # Summarize
    sum_parser = subparsers.add_parser("summarize", help="Generate summary for note")
    sum_parser.add_argument("note", help="Path to note file")
    
    # Watch inbox
    watch_parser = subparsers.add_parser("watch", help="Watch inbox for new files")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    admin = NoteAdmin(args.vault)
    
    if args.command == "process-inbox":
        processed = admin.process_inbox(dry_run=args.dry_run)
        print(f"Processed {len(processed)} notes")
    
    elif args.command == "batch-tag":
        tagged = admin.batch_tag(args.folder)
        print(f"Re-tagged {len(tagged)} notes")
    
    elif args.command == "find-connections":
        connections = admin.find_connections(args.note)
        print(f"Found {len(connections)} connections")
    
    elif args.command == "summarize":
        summary = admin.summarize_note(args.note)
        if summary:
            print(summary)
    
    elif args.command == "watch":
        admin.watch_inbox()

if __name__ == "__main__":
    main()
