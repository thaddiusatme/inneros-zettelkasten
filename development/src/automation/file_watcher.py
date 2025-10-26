"""
File Watcher - File system monitoring with watchdog integration

Monitors knowledge/Inbox/ directory for new captures and triggers processing.
Follows ADR-001: <200 LOC, single responsibility, domain separation.

GREEN Phase: Minimal watchdog implementation for file system monitoring.
"""

import threading
import fnmatch
from pathlib import Path
from typing import Callable, Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class FileWatcherError(Exception):
    """File watcher specific errors"""
    pass


class FileWatcher:
    """
    File system monitor using watchdog for event-driven file processing.
    
    Monitors a directory for file changes and triggers registered callbacks
    with debouncing and path filtering capabilities.
    
    Size: ~150 LOC (ADR-001 compliant)
    """

    def __init__(
        self,
        watch_path: Path,
        debounce_seconds: float = 2.0,
        ignore_patterns: Optional[List[str]] = None
    ):
        """
        Initialize file watcher.
        
        Args:
            watch_path: Directory to monitor
            debounce_seconds: Delay before triggering callback (default 2s)
            ignore_patterns: List of patterns to ignore (e.g., [".obsidian/*", "*.tmp"])
        """
        self.watch_path = Path(watch_path)
        self.debounce_seconds = debounce_seconds
        self.ignore_patterns = ignore_patterns or [".obsidian/*", "*.tmp", ".*"]

        self._observer: Optional[Observer] = None
        self._callbacks: List[Callable[[Path, str], None]] = []
        self._debounce_timers: Dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def register_callback(self, callback: Callable[[Path, str], None]) -> None:
        """
        Register callback to be invoked on file events.
        
        Args:
            callback: Function(file_path, event_type) called on events
        """
        self._callbacks.append(callback)

    def start(self) -> None:
        """
        Start file watching.
        
        Raises:
            FileWatcherError: If watch path doesn't exist or watcher already running
        """
        if not self.watch_path.exists():
            raise FileWatcherError(f"Watch path does not exist: {self.watch_path}")

        if self._observer is not None and self._observer.is_alive():
            raise FileWatcherError("File watcher is already running")

        # Create event handler
        event_handler = _FileEventHandler(self)

        # Create and start observer
        self._observer = Observer()
        self._observer.schedule(event_handler, str(self.watch_path), recursive=True)
        self._observer.start()

    def stop(self) -> None:
        """Stop file watching gracefully."""
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

        # Cancel any pending debounce timers
        with self._lock:
            for timer in self._debounce_timers.values():
                timer.cancel()
            self._debounce_timers.clear()

    def is_running(self) -> bool:
        """Check if watcher is actively monitoring."""
        return self._observer is not None and self._observer.is_alive()

    def _should_ignore(self, file_path: Path) -> bool:
        """
        Check if file should be ignored based on glob patterns.
        
        Supports standard glob patterns:
        - *.tmp: Extension matching
        - .obsidian/*: Directory patterns
        - .*: Hidden files
        - **/*.bak: Recursive patterns
        """
        path_str = str(file_path)
        file_name = file_path.name

        # Check each ignore pattern using fnmatch for proper glob support
        for pattern in self.ignore_patterns:
            # Handle directory-specific patterns
            if "/" in pattern:
                # Match against full path for directory patterns
                if fnmatch.fnmatch(path_str, f"*{pattern}") or pattern in path_str:
                    return True
            # Handle filename patterns
            elif fnmatch.fnmatch(file_name, pattern):
                return True

        return False

    def _trigger_callbacks(self, file_path: Path, event_type: str) -> None:
        """
        Trigger registered callbacks with debouncing.
        
        Args:
            file_path: Path to file that changed
            event_type: Type of event ('created', 'modified', 'deleted')
        """
        # Check if should ignore
        if self._should_ignore(file_path):
            return

        # Debounce logic
        file_key = str(file_path)

        with self._lock:
            # Cancel existing timer for this file
            if file_key in self._debounce_timers:
                self._debounce_timers[file_key].cancel()

            # Create new timer
            timer = threading.Timer(
                self.debounce_seconds,
                self._execute_callbacks,
                args=(file_path, event_type)
            )
            self._debounce_timers[file_key] = timer
            timer.start()

    def _execute_callbacks(self, file_path: Path, event_type: str) -> None:
        """Execute all registered callbacks."""
        # Remove timer from tracking
        with self._lock:
            file_key = str(file_path)
            if file_key in self._debounce_timers:
                del self._debounce_timers[file_key]

        # Call all registered callbacks
        for callback in self._callbacks:
            try:
                callback(file_path, event_type)
            except Exception as e:
                # Log error but continue (don't crash watcher)
                print(f"Error in file watcher callback: {e}")


class _FileEventHandler(FileSystemEventHandler):
    """
    Internal event handler for watchdog.
    
    Translates watchdog events to FileWatcher callbacks.
    """

    def __init__(self, watcher: FileWatcher):
        """Initialize with parent watcher reference."""
        super().__init__()
        self.watcher = watcher

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if not event.is_directory:
            self.watcher._trigger_callbacks(Path(event.src_path), "created")

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory:
            self.watcher._trigger_callbacks(Path(event.src_path), "modified")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events."""
        if not event.is_directory:
            self.watcher._trigger_callbacks(Path(event.src_path), "deleted")
