#!/usr/bin/env python3
"""
Smart Link Management CLI Utilities - TDD Iteration 2 GREEN Phase
Minimal implementation to pass failing tests
"""

from typing import List
from ai.link_suggestion_engine import LinkSuggestion


def display_suggestion_interactively(
    suggestion: LinkSuggestion, current: int, total: int
) -> str:
    """Display a suggestion interactively and get user choice"""

    # Quality emoji indicators
    quality_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}

    emoji = quality_emoji.get(suggestion.confidence, "⚪")

    print(f"\n{emoji} Suggestion {current}/{total}")
    print(f"Link: {suggestion.suggested_link_text}")
    print(f"Similarity: {suggestion.similarity_score:.1%}")
    print(f"Explanation: {suggestion.explanation}")
    print(f"Insert in: {suggestion.insertion_context}")
    print("\nOptions: [A]ccept, [R]eject, [S]kip")

    choice = get_user_choice_for_suggestion()
    return choice


def get_user_choice_for_suggestion() -> str:
    """Get and validate user choice for suggestion"""
    while True:
        try:
            choice = input("Your choice: ").lower().strip()
            if choice in ["a", "accept"]:
                return "accept"
            elif choice in ["r", "reject"]:
                return "reject"
            elif choice in ["s", "skip"]:
                return "skip"
            else:
                print("Invalid choice. Please enter A, R, or S.")
        except (EOFError, KeyboardInterrupt):
            return "skip"


def display_progress(current: int, total: int, message: str = ""):
    """Display progress during batch operations"""
    percent = (current / total) * 100 if total > 0 else 0
    print(f"Progress: {current}/{total} ({percent:.1f}%) {message}")


def display_batch_progress(current: int, total: int, current_note: str = ""):
    """Display batch processing progress"""
    percent = (current / total) * 100 if total > 0 else 0
    print(f"Processing: {current}/{total} ({percent:.1f}%) - {current_note}")


def filter_suggestions_by_quality(
    suggestions: List[LinkSuggestion], min_quality: float
) -> List[LinkSuggestion]:
    """Filter suggestions by minimum quality threshold"""
    return [s for s in suggestions if s.quality_score >= min_quality]


def display_suggestions_summary(
    suggestions: List[LinkSuggestion],
    processed: int = None,
    accepted: int = None,
    rejected: int = None,
):
    """Display summary of suggestions processing"""
    print("\n📊 Summary:")
    print(f"   Total suggestions: {len(suggestions)}")
    if processed is not None:
        print(f"   Processed: {processed}")
    if accepted is not None:
        print(f"   Accepted: {accepted}")
    if rejected is not None:
        print(f"   Rejected: {rejected}")


def display_dry_run_results(suggestions: List[LinkSuggestion], target_note: str):
    """Display dry-run preview of what would be modified"""
    print(f"\n🔍 DRY RUN - Preview for {target_note}")
    print(f"   {len(suggestions)} links would be added:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion.suggested_link_text}")


def display_cli_error(error_message: str, context: str = ""):
    """Display formatted CLI error message"""
    print(f"❌ Error: {error_message}")
    if context:
        print(f"   Context: {context}")


def process_suggestions_batch(
    suggestions: List[LinkSuggestion], interactive: bool = False
) -> List[dict]:
    """Process a batch of suggestions with progress tracking"""
    results = []

    for i, suggestion in enumerate(suggestions, 1):
        display_progress(i, len(suggestions), f"Processing {suggestion.target_note}")

        if interactive:
            choice = display_suggestion_interactively(suggestion, i, len(suggestions))
            results.append({"suggestion": suggestion, "action": choice})
        else:
            # Auto-accept high quality suggestions in non-interactive mode
            action = "accept" if suggestion.confidence == "high" else "skip"
            results.append({"suggestion": suggestion, "action": action})

    return results
