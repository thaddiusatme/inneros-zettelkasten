"""
Interactive CLI Components - Extracted Utility Classes for Reusable User Experience

This module contains extracted CLI interaction patterns from Samsung Screenshot Evening Workflow
TDD Iteration 4 REFACTOR phase, designed for reuse across multiple CLI applications.

Classes:
- InteractiveProgressReporter: Enhanced progress reporting with precise ETA calculations
- UserInteractionManager: User input, confirmation, and interaction patterns
- CLIErrorHandler: Standardized error messaging and troubleshooting guidance
- PerformanceReporter: Consistent performance metrics display across CLI tools

REFACTOR Design Principles:
- Reusable across different CLI applications
- Consistent user experience patterns
- Enhanced precision for production use
- Integration with existing InnerOS CLI ecosystem
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional


class InteractiveProgressReporter:
    """
    Enhanced progress reporting with precise ETA calculations and professional UI
    
    REFACTOR IMPROVEMENTS:
    - Improved ETA calculation precision to meet 15% tolerance requirement
    - Enhanced visual progress indicators with emoji consistency
    - Configurable update frequency to reduce console noise
    - Memory-efficient tracking for large batch operations
    """
    
    def __init__(self, update_frequency: float = 0.5):
        """
        Initialize enhanced progress reporter
        
        Args:
            update_frequency: Minimum seconds between progress updates (reduces console spam)
        """
        self.logger = logging.getLogger(__name__)
        self.start_time = None
        self.current_step = 0
        self.total_steps = 0
        self.last_update_time = 0
        self.update_frequency = update_frequency
        self.eta_history = []  # Track ETA accuracy for improvement
        
    def start_progress(self, total_steps: int, description: str = "Processing"):
        """Start enhanced progress tracking with professional formatting"""
        self.start_time = time.time()
        self.total_steps = total_steps
        self.current_step = 0
        self.last_update_time = self.start_time
        self.eta_history = []
        
        print(f"\n🚀 {description}")
        print(f"   📝 Total items: {total_steps}")
        print(f"   ⏰ Started: {time.strftime('%H:%M:%S')}")
        print("   " + "─" * 50)
    
    def update_progress(self, step: int, item_description: str = "", force_update: bool = False):
        """
        Update progress with enhanced ETA precision
        
        Args:
            step: Current step number (1-based)
            item_description: Optional description of current item
            force_update: Force update regardless of frequency limit
        """
        current_time = time.time()
        self.current_step = step
        
        # Rate limiting for console updates (unless forced)
        if not force_update and (current_time - self.last_update_time) < self.update_frequency:
            return
            
        if self.total_steps > 0 and self.start_time:
            elapsed = current_time - self.start_time
            percentage = (step / self.total_steps) * 100
            
            # Enhanced ETA calculation with advanced smoothing for 15% tolerance
            if step > 0:
                # Calculate base ETA
                avg_time_per_item = elapsed / step
                remaining_items = self.total_steps - step
                raw_eta = remaining_items * avg_time_per_item
                
                # Advanced ETA smoothing with exponential weighted moving average
                self.eta_history.append(raw_eta)
                if len(self.eta_history) > 10:  # Increased history for better smoothing
                    self.eta_history.pop(0)
                
                # Exponential weighted moving average for better precision
                if len(self.eta_history) == 1:
                    smoothed_eta = raw_eta
                else:
                    # More recent ETAs get higher weight
                    weights = [0.1, 0.15, 0.2, 0.25, 0.3]  # Recent values weighted more heavily
                    if len(self.eta_history) >= 5:
                        weighted_sum = sum(eta * weight for eta, weight in zip(self.eta_history[-5:], weights))
                        weight_sum = sum(weights)
                        smoothed_eta = weighted_sum / weight_sum
                    else:
                        smoothed_eta = sum(self.eta_history) / len(self.eta_history)
                
                # Format ETA display
                eta_minutes = int(smoothed_eta // 60)
                eta_seconds = int(smoothed_eta % 60)
                eta_display = f"{eta_minutes}m {eta_seconds}s" if eta_minutes > 0 else f"{eta_seconds}s"
                
                # Progress bar visualization
                bar_width = 30
                filled_width = int((step / self.total_steps) * bar_width)
                progress_bar = "█" * filled_width + "░" * (bar_width - filled_width)
                
                print(f"   📊 [{progress_bar}] {percentage:.1f}% ({step}/{self.total_steps}) ETA: {eta_display}")
                if item_description:
                    print(f"      🔍 {item_description}")
            else:
                print(f"   📊 Starting... ({step}/{self.total_steps})")
        
        self.last_update_time = current_time
    
    def complete_progress(self) -> Dict[str, Any]:
        """Complete progress tracking with final metrics and accuracy report"""
        if not self.start_time:
            return {}
            
        duration = time.time() - self.start_time
        rate = self.current_step / duration if duration > 0 else 0
        
        print("   " + "─" * 50)
        print(f"   ✅ Completed: {self.current_step} items in {duration:.1f}s")
        print(f"   📈 Processing rate: {rate:.2f} items/second")
        print(f"   🏁 Finished: {time.strftime('%H:%M:%S')}")
        
        return {
            "duration": duration,
            "items_processed": self.current_step,
            "rate": rate,
            "eta_accuracy": self._calculate_eta_accuracy()
        }
    
    def _calculate_eta_accuracy(self) -> float:
        """Calculate ETA prediction accuracy for continuous improvement"""
        if len(self.eta_history) < 2:
            return 1.0
        
        # Simple accuracy metric based on ETA variance
        eta_variance = max(self.eta_history) - min(self.eta_history)
        avg_eta = sum(self.eta_history) / len(self.eta_history)
        
        if avg_eta == 0:
            return 1.0
            
        accuracy = max(0, 1 - (eta_variance / avg_eta))
        return accuracy


class UserInteractionManager:
    """
    Standardized user interaction patterns for CLI applications
    
    REFACTOR IMPROVEMENTS:
    - Consistent confirmation patterns across all CLI tools
    - Enhanced input validation with retry logic
    - Professional error handling with graceful degradation
    - Integration with existing InnerOS user experience patterns
    """
    
    def __init__(self):
        """Initialize user interaction manager"""
        self.logger = logging.getLogger(__name__)
    
    def confirm_action(self, message: str, default: bool = False) -> bool:
        """
        Get user confirmation with professional formatting
        
        Args:
            message: Confirmation message to display
            default: Default response if user just presses Enter
            
        Returns:
            True if user confirms, False otherwise
        """
        default_text = "[Y/n]" if default else "[y/N]"
        
        try:
            print(f"\n❓ {message}")
            response = input(f"   Continue? {default_text}: ").strip().lower()
            
            if not response:
                return default
            
            return response in ['y', 'yes', 'true', '1']
            
        except (KeyboardInterrupt, EOFError):
            print("\n   ⚠️  Operation cancelled by user")
            return False
    
    def get_user_choice(self, message: str, choices: List[str], default: int = 0) -> str:
        """
        Get user choice from multiple options
        
        Args:
            message: Question to ask user
            choices: List of available choices
            default: Default choice index
            
        Returns:
            Selected choice string
        """
        print(f"\n❓ {message}")
        
        for i, choice in enumerate(choices):
            marker = "→" if i == default else " "
            print(f"   {marker} {i+1}. {choice}")
        
        try:
            while True:
                response = input(f"\n   Select option (1-{len(choices)}, default {default+1}): ").strip()
                
                if not response:
                    return choices[default]
                
                try:
                    choice_index = int(response) - 1
                    if 0 <= choice_index < len(choices):
                        return choices[choice_index]
                    else:
                        print(f"   ❌ Please enter a number between 1 and {len(choices)}")
                except ValueError:
                    print("   ❌ Please enter a valid number")
                    
        except (KeyboardInterrupt, EOFError):
            print("\n   ⚠️  Operation cancelled by user")
            return choices[default]
    
    def display_warning(self, message: str, details: List[str] = None):
        """Display professional warning message with optional details"""
        print(f"\n⚠️  Warning: {message}")
        
        if details:
            for detail in details:
                print(f"   • {detail}")


class CLIErrorHandler:
    """
    Standardized error handling and troubleshooting guidance for CLI applications
    
    REFACTOR IMPROVEMENTS:
    - Consistent error message formatting across all CLI tools
    - Enhanced troubleshooting steps with actionable guidance
    - Integration with existing InnerOS error handling patterns
    - Automatic error logging with context preservation
    """
    
    def __init__(self):
        """Initialize CLI error handler"""
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error_type: str, error_message: str, 
                    troubleshooting_steps: List[str] = None, 
                    context: Dict[str, Any] = None):
        """
        Handle error with professional formatting and troubleshooting guidance
        
        Args:
            error_type: Type/category of error
            error_message: Main error message
            troubleshooting_steps: List of actionable troubleshooting steps
            context: Additional context for debugging
        """
        print(f"\n❌ Error: {error_type}")
        print(f"   {error_message}")
        
        if troubleshooting_steps:
            print(f"\n🔧 Troubleshooting Steps:")
            for i, step in enumerate(troubleshooting_steps, 1):
                print(f"   {i}. {step}")
        
        if context:
            print(f"\n📊 Error Context:")
            for key, value in context.items():
                print(f"   • {key}: {value}")
        
        # Log error for debugging
        self.logger.error(f"{error_type}: {error_message}", extra={
            'troubleshooting_steps': troubleshooting_steps,
            'context': context
        })
    
    def handle_validation_error(self, field_name: str, field_value: str, 
                              requirements: List[str]):
        """Handle validation errors with specific field guidance"""
        self.handle_error(
            error_type="Validation Error",
            error_message=f"Invalid value for {field_name}: '{field_value}'",
            troubleshooting_steps=[
                f"Verify {field_name} meets the following requirements:"
            ] + [f"  • {req}" for req in requirements]
        )


class PerformanceReporter:
    """
    Consistent performance metrics reporting for CLI applications
    
    REFACTOR IMPROVEMENTS:
    - Standardized performance metric display across all CLI tools
    - Enhanced memory usage tracking and reporting
    - Professional formatting with clear success/failure indicators
    - Integration with existing InnerOS performance monitoring
    """
    
    def __init__(self):
        """Initialize performance reporter"""
        self.logger = logging.getLogger(__name__)
    
    def report_performance_metrics(self, result: Dict[str, Any], 
                                 targets: Dict[str, Any] = None) -> None:
        """
        Report performance metrics with professional formatting
        
        Args:
            result: Performance results dictionary
            targets: Optional performance targets for comparison
        """
        print(f"\n📊 Performance Metrics:")
        print("   " + "─" * 40)
        
        # Processing time metrics
        processing_time = result.get('processing_time', 0)
        if targets and 'processing_time' in targets:
            target_time = targets['processing_time']
            target_met = processing_time <= target_time
            status = "✅" if target_met else "❌"
            print(f"   ⏱️  Processing time: {processing_time:.2f}s {status}")
            print(f"      Target: ≤{target_time}s")
        else:
            print(f"   ⏱️  Processing time: {processing_time:.2f}s")
        
        # Processing rate metrics
        items_processed = result.get('items_processed', 0)
        if processing_time > 0 and items_processed > 0:
            rate = items_processed / processing_time
            print(f"   📈 Processing rate: {rate:.2f} items/second")
        
        # Memory metrics (if available)
        memory_metrics = result.get('memory_metrics', {})
        if memory_metrics:
            growth = memory_metrics.get('memory_growth_mb', 0)
            if targets and 'memory_growth' in targets:
                target_growth = targets['memory_growth']
                growth_ok = growth <= target_growth
                status = "✅" if growth_ok else "❌"
                print(f"   🧠 Memory growth: {growth:.1f}MB {status}")
                print(f"      Target: ≤{target_growth}MB")
            else:
                print(f"   🧠 Memory growth: {growth:.1f}MB")
        
        print("   " + "─" * 40)
        
        # Log metrics for analysis
        self.logger.info("Performance metrics reported", extra={
            'processing_time': processing_time,
            'items_processed': items_processed,
            'memory_metrics': memory_metrics,
            'targets_met': self._check_targets_met(result, targets)
        })
    
    def _check_targets_met(self, result: Dict[str, Any], targets: Dict[str, Any]) -> Dict[str, bool]:
        """Check which performance targets were met"""
        if not targets:
            return {}
        
        targets_met = {}
        
        if 'processing_time' in targets:
            targets_met['processing_time'] = result.get('processing_time', float('inf')) <= targets['processing_time']
        
        if 'memory_growth' in targets:
            memory_growth = result.get('memory_metrics', {}).get('memory_growth_mb', float('inf'))
            targets_met['memory_growth'] = memory_growth <= targets['memory_growth']
        
        return targets_met
