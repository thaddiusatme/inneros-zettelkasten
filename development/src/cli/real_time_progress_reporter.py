"""
TDD Iteration 5 GREEN Phase: Real-Time Progress Reporter
Minimal working implementation for progress reporting

GREEN Phase: Basic progress reporting to pass tests
"""

from typing import Dict, Any, List, Callable, Optional


class RealTimeProgressReporter:
    """
    GREEN Phase: Basic real-time progress reporting
    Minimal implementation for progress reporting tests
    """
    
    def __init__(self):
        self.updates: List[Dict[str, Any]] = []
        self.callback: Optional[Callable] = None
        
    def set_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback function for progress updates"""
        self.callback = callback
        
    def report_progress(self, update: Dict[str, Any]):
        """Report progress update"""
        self.updates.append(update)
        
        # Call callback if set
        if self.callback:
            self.callback(update)
    
    def get_updates(self) -> List[Dict[str, Any]]:
        """Get all progress updates"""
        return self.updates.copy()
    
    def clear_updates(self):
        """Clear all stored updates"""
        self.updates.clear()
    
    def get_latest_update(self) -> Optional[Dict[str, Any]]:
        """Get the most recent progress update"""
        return self.updates[-1] if self.updates else None
