#!/usr/bin/env python3
"""
Simple polling-based file watcher for Obsidian vault
No external dependencies required
"""

import time
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from admin import NoteAdmin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleWatcher:
    """Simple polling-based file watcher"""
    
    def __init__(self, vault_path: str = None, poll_interval: int = 30):
        self.admin = NoteAdmin(vault_path)
        self.poll_interval = poll_interval
        self.known_files = {}
        self.inbox_path = self.admin.inbox_path
        
    def scan_inbox(self):
        """Scan inbox for new or modified files"""
        if not self.inbox_path.exists():
            logger.warning(f"Inbox folder not found: {self.inbox_path}")
            return
        
        current_files = {}
        
        for note_file in self.inbox_path.glob("*.md"):
            if note_file.is_file():
                try:
                    stat = note_file.stat()
                    current_files[str(note_file)] = {
                        'mtime': stat.st_mtime,
                        'size': stat.st_size
                    }
                except OSError:
                    continue
        
        # Check for new files
        for file_path, info in current_files.items():
            if file_path not in self.known_files:
                logger.info(f"New note detected: {Path(file_path).name}")
                self.process_new_note(Path(file_path))
            elif info['mtime'] != self.known_files[file_path]['mtime']:
                logger.info(f"Modified note detected: {Path(file_path).name}")
                self.process_modified_note(Path(file_path))
        
        # Update known files
        self.known_files = current_files
    
    def process_new_note(self, note_path: Path):
        """Process a newly detected note"""
        try:
            success = self.admin._process_note(note_path)
            if success:
                logger.info(f"Successfully processed new note: {note_path.name}")
            else:
                logger.warning(f"Failed to process new note: {note_path.name}")
        except Exception as e:
            logger.error(f"Error processing new note {note_path.name}: {e}")
    
    def process_modified_note(self, note_path: Path):
        """Process a modified note"""
        try:
            success = self.admin._process_note(note_path)
            if success:
                logger.info(f"Successfully re-processed modified note: {note_path.name}")
        except Exception as e:
            logger.error(f"Error re-processing modified note {note_path.name}: {e}")
    
    def start(self):
        """Start the polling watcher"""
        logger.info(f"Starting simple watcher for: {self.inbox_path}")
        logger.info(f"Polling every {self.poll_interval} seconds")
        logger.info("Press Ctrl+C to stop")
        
        # Initial scan
        self.scan_inbox()
        
        try:
            while True:
                time.sleep(self.poll_interval)
                self.scan_inbox()
        except KeyboardInterrupt:
            logger.info("Stopping watcher...")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple polling-based file watcher")
    parser.add_argument("--vault", help="Path to Obsidian vault", default=None)
    parser.add_argument("--interval", type=int, default=30, 
                       help="Polling interval in seconds (default: 30)")
    
    args = parser.parse_args()
    
    watcher = SimpleWatcher(args.vault, args.interval)
    watcher.start()

if __name__ == "__main__":
    main()
