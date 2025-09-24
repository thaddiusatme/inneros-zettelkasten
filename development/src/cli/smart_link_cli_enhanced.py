#!/usr/bin/env python3
"""
Smart Link Management CLI - Enhanced Utilities (REFACTOR Phase)
Extracted utilities for production-ready CLI experience
"""

import sys
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ai.link_suggestion_engine import LinkSuggestion


@dataclass
class CLITheme:
    """CLI theming and formatting configuration"""
    # Quality indicators
    quality_high = "🟢"
    quality_medium = "🟡" 
    quality_low = "🔴"
    
    # Status indicators  
    success = "✅"
    warning = "⚠️"
    error = "❌"
    info = "ℹ️"
    progress = "🔄"
    
    # Separators
    line_separator = "-" * 60
    section_separator = "=" * 60


class InteractiveSuggestionPresenter:
    """Enhanced presentation layer for interactive suggestion review"""
    
    def __init__(self, theme: CLITheme = None):
        self.theme = theme or CLITheme()
    
    def display_suggestion_with_context(self, suggestion: LinkSuggestion, 
                                      current: int, total: int, 
                                      show_detailed: bool = True) -> str:
        """Display suggestion with rich context and formatting"""
        
        # Quality emoji mapping
        quality_emoji = {
            "high": self.theme.quality_high,
            "medium": self.theme.quality_medium,
            "low": self.theme.quality_low
        }
        
        emoji = quality_emoji.get(suggestion.confidence, "⚪")
        
        print(f"\n{emoji} Link Suggestion {current}/{total}")
        print(self.theme.line_separator)
        
        # Core suggestion info
        print(f"📄 Target: {suggestion.target_note}")
        print(f"🔗 Link Text: {suggestion.suggested_link_text}")
        print(f"📊 Quality: {suggestion.quality_score:.1%} ({suggestion.confidence})")
        print(f"🎯 Similarity: {suggestion.similarity_score:.1%}")
        
        if show_detailed:
            print(f"💭 Explanation: {suggestion.explanation}")
            print(f"📍 Insert Location: {suggestion.insertion_context}")
            print(f"📂 Section: {suggestion.suggested_location}")
        
        print(f"\n🎛️  Options: [A]ccept • [R]eject • [S]kip • [D]etails • [Q]uit")
        
        return self._get_user_choice()
    
    def _get_user_choice(self) -> str:
        """Get and validate user choice with enhanced options"""
        while True:
            try:
                choice = input("Your choice: ").lower().strip()
                
                if choice in ['a', 'accept']:
                    return 'accept'
                elif choice in ['r', 'reject']:
                    return 'reject' 
                elif choice in ['s', 'skip']:
                    return 'skip'
                elif choice in ['d', 'details']:
                    return 'details'
                elif choice in ['q', 'quit']:
                    return 'quit'
                else:
                    print("⚠️  Invalid choice. Options: A(ccept), R(eject), S(kip), D(etails), Q(uit)")
                    
            except (EOFError, KeyboardInterrupt):
                print(f"\n{self.theme.info} Interrupted - skipping current suggestion")
                return 'skip'


class BatchProcessingReporter:
    """Enhanced reporting for batch processing operations"""
    
    def __init__(self, theme: CLITheme = None):
        self.theme = theme or CLITheme()
        self.start_time = None
        self.processed_count = 0
        
    def start_batch(self, total_items: int, batch_name: str = "Processing"):
        """Initialize batch processing with progress tracking"""
        self.start_time = time.time()
        self.total_items = total_items
        self.batch_name = batch_name
        self.processed_count = 0
        
        print(f"\n{self.theme.progress} Starting {batch_name}")
        print(f"📊 Total items: {total_items}")
        print(self.theme.section_separator)
    
    def update_progress(self, current: int, item_name: str = "", 
                       action: str = "processing"):
        """Update progress with rich formatting"""
        self.processed_count = current
        percent = (current / self.total_items) * 100 if self.total_items > 0 else 0
        
        # Calculate ETA
        if self.start_time and current > 0:
            elapsed = time.time() - self.start_time
            rate = current / elapsed
            remaining = (self.total_items - current) / rate if rate > 0 else 0
            eta_str = f" • ETA: {remaining:.0f}s" if remaining > 0 else ""
        else:
            eta_str = ""
        
        # Progress bar
        bar_width = 20
        filled = int(bar_width * (current / self.total_items)) if self.total_items > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        
        print(f"\r[{bar}] {current}/{self.total_items} ({percent:.1f}%){eta_str} - {action} {item_name}", end="", flush=True)
    
    def finish_batch(self, results_summary: Dict[str, int]):
        """Complete batch processing with summary"""
        if self.start_time:
            total_time = time.time() - self.start_time
            rate = self.processed_count / total_time if total_time > 0 else 0
            
            print(f"\n\n{self.theme.success} {self.batch_name} Complete!")
            print(self.theme.line_separator)
            print(f"⏱️  Total Time: {total_time:.1f}s")
            print(f"⚡ Processing Rate: {rate:.1f} items/sec")
            
            # Results breakdown
            for key, value in results_summary.items():
                emoji = self._get_result_emoji(key)
                print(f"{emoji} {key.title()}: {value}")
    
    def _get_result_emoji(self, result_type: str) -> str:
        """Get emoji for different result types"""
        emoji_map = {
            'accepted': '✅',
            'rejected': '❌', 
            'skipped': '⏭️',
            'processed': '📝',
            'errors': '🚫'
        }
        return emoji_map.get(result_type.lower(), '📊')


class CLIOutputFormatter:
    """Enhanced output formatting with consistent styling"""
    
    def __init__(self, theme: CLITheme = None):
        self.theme = theme or CLITheme()
    
    def display_header(self, title: str, subtitle: str = "", 
                      config_info: Dict[str, Any] = None):
        """Display formatted CLI header with configuration"""
        print(f"\n{self.theme.success} {title}")
        if subtitle:
            print(f"📝 {subtitle}")
        
        if config_info:
            print(self.theme.line_separator)
            for key, value in config_info.items():
                icon = self._get_config_icon(key)
                print(f"{icon} {key.title()}: {value}")
        
        print(self.theme.section_separator)
    
    def display_suggestions_summary(self, suggestions: List[LinkSuggestion], 
                                  show_quality_breakdown: bool = True):
        """Display comprehensive suggestions summary"""
        if not suggestions:
            print(f"{self.theme.info} No suggestions to display")
            return
        
        print(f"\n📊 Link Suggestions Summary")
        print(self.theme.line_separator)
        print(f"📈 Total Suggestions: {len(suggestions)}")
        
        if show_quality_breakdown:
            # Quality distribution
            quality_counts = {'high': 0, 'medium': 0, 'low': 0}
            for s in suggestions:
                quality_counts[s.confidence] = quality_counts.get(s.confidence, 0) + 1
            
            print(f"🟢 High Quality: {quality_counts['high']}")
            print(f"🟡 Medium Quality: {quality_counts['medium']}")  
            print(f"🔴 Low Quality: {quality_counts['low']}")
            
            # Average quality
            avg_quality = sum(s.quality_score for s in suggestions) / len(suggestions)
            print(f"📊 Average Quality: {avg_quality:.1%}")
    
    def display_dry_run_preview(self, suggestions: List[LinkSuggestion], 
                               target_note: str):
        """Display dry-run preview with detailed formatting"""
        print(f"\n{self.theme.warning} DRY RUN MODE - Preview Only")
        print(f"📄 Target Note: {target_note}")
        print(f"🔗 Links to be added: {len(suggestions)}")
        print(self.theme.line_separator)
        
        for i, suggestion in enumerate(suggestions, 1):
            quality_icon = {
                'high': '🟢', 'medium': '🟡', 'low': '🔴'
            }.get(suggestion.confidence, '⚪')
            
            print(f"{i:2d}. {quality_icon} {suggestion.suggested_link_text}")
            print(f"     📍 {suggestion.insertion_context}")
            print(f"     📊 Quality: {suggestion.quality_score:.1%}")
    
    def display_error_with_context(self, error_msg: str, context: str = "", 
                                 suggestions: List[str] = None):
        """Display error with helpful context and suggestions"""
        print(f"\n{self.theme.error} Error: {error_msg}")
        
        if context:
            print(f"📍 Context: {context}")
        
        if suggestions:
            print(f"{self.theme.info} Suggestions:")
            for suggestion in suggestions:
                print(f"   • {suggestion}")
    
    def _get_config_icon(self, config_key: str) -> str:
        """Get appropriate icon for configuration keys"""
        icon_map = {
            'min_quality': '🎚️',
            'max_results': '📊',
            'target': '📄',
            'corpus_dir': '📁',
            'interactive': '🎮',
            'dry_run': '🔍'
        }
        return icon_map.get(config_key.lower().replace('-', '_'), '⚙️')


class SmartLinkCLIOrchestrator:
    """Main orchestrator for enhanced CLI experience"""
    
    def __init__(self):
        self.theme = CLITheme()
        self.presenter = InteractiveSuggestionPresenter(self.theme)
        self.reporter = BatchProcessingReporter(self.theme) 
        self.formatter = CLIOutputFormatter(self.theme)
    
    def execute_interactive_workflow(self, suggestions: List[LinkSuggestion],
                                   target_note: str, dry_run: bool = False) -> Dict[str, Any]:
        """Execute complete interactive workflow with enhanced UX"""
        
        # Display header and configuration
        config = {
            'target': target_note,
            'suggestions': len(suggestions),
            'dry_run': dry_run
        }
        self.formatter.display_header(
            "Smart Link Management", 
            "Interactive Suggestion Review",
            config
        )
        
        # Show summary
        self.formatter.display_suggestions_summary(suggestions)
        
        # Handle dry-run mode
        if dry_run:
            self.formatter.display_dry_run_preview(suggestions, target_note)
            return {'mode': 'dry_run', 'suggestions': suggestions}
        
        # Interactive processing
        results = {
            'accepted': 0,
            'rejected': 0, 
            'skipped': 0,
            'actions': []
        }
        
        for i, suggestion in enumerate(suggestions, 1):
            choice = self.presenter.display_suggestion_with_context(
                suggestion, i, len(suggestions)
            )
            
            if choice == 'quit':
                print(f"\n{self.theme.info} User requested early exit")
                break
            elif choice == 'accept':
                results['accepted'] += 1
            elif choice == 'reject':
                results['rejected'] += 1
            else:  # skip
                results['skipped'] += 1
            
            results['actions'].append({
                'suggestion': suggestion,
                'action': choice
            })
        
        # Final summary
        self.formatter.display_header(
            "Processing Complete",
            f"Processed {len(results['actions'])}/{len(suggestions)} suggestions"
        )
        
        return results
