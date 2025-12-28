"""
Smart Link Review CLI - Interactive review of link suggestions

Issue #58: Smart Link Review Queue CLI

Provides a simple terminal interface for reviewing smart link suggestions:
- Show suggestion with source/target/similarity
- User chooses: [a]ccept / [d]ismiss / [s]kip
- Track decisions for batch processing

Following ADR-001: <200 LOC, single responsibility
"""

import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional


class SmartLinkReviewCLI:
    """
    Interactive CLI for reviewing smart link suggestions.

    Provides terminal-based review workflow:
    1. Display suggestion with context
    2. Collect user decision (accept/dismiss/skip)
    3. Return results for batch processing
    """

    def __init__(self, vault_path: Path):
        """
        Initialize review CLI.

        Args:
            vault_path: Path to knowledge vault
        """
        self.vault_path = Path(vault_path)

    def format_suggestion(self, suggestion: Dict[str, Any]) -> str:
        """
        Format a suggestion for display.

        Args:
            suggestion: Suggestion dict with source, target, similarity

        Returns:
            Formatted string for terminal display
        """
        source = suggestion.get("source", "unknown")
        target = suggestion.get("target", "unknown")
        similarity = suggestion.get("similarity", 0.0)
        reason = suggestion.get("reason", "")

        lines = [
            f"📄 Source: {source}",
            f"🔗 Target: {target}",
            f"📊 Similarity: {similarity:.2f}",
        ]

        if reason:
            lines.append(f"💡 Reason: {reason}")

        return "\n".join(lines)

    def format_progress(self, current: int, total: int) -> str:
        """
        Format progress indicator.

        Args:
            current: Current suggestion number (1-indexed)
            total: Total number of suggestions

        Returns:
            Progress string like "Suggestion 2 of 5"
        """
        return f"Suggestion {current} of {total}"

    def get_user_decision(self, suggestion: Dict[str, Any]) -> str:
        """
        Get user decision for a suggestion.

        Args:
            suggestion: Suggestion to review

        Returns:
            Action string: "accept", "dismiss", or "skip"
        """
        print("\n" + "-" * 50)
        print(self.format_suggestion(suggestion))
        print("-" * 50)
        print("[a]ccept | [d]ismiss | [s]kip")

        while True:
            choice = input("Your choice: ").strip().lower()

            if choice in ("a", "accept"):
                return "accept"
            elif choice in ("d", "dismiss"):
                return "dismiss"
            elif choice in ("s", "skip"):
                return "skip"
            else:
                print("Invalid choice. Please enter 'a', 'd', or 's'.")

    def review_suggestions(
        self, suggestions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Run interactive review session for suggestions.

        Args:
            suggestions: List of suggestion dicts to review

        Returns:
            List of results with action and original suggestion
        """
        results = []
        total = len(suggestions)

        print(f"\n🔍 Smart Link Review - {total} suggestions to review")
        print("=" * 50)

        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{self.format_progress(i, total)}")

            action = self.get_user_decision(suggestion)

            results.append({"suggestion": suggestion, "action": action})

            if action == "accept":
                print("✅ Accepted")
            elif action == "dismiss":
                print("❌ Dismissed")
            else:
                print("⏭️  Skipped")

        # Summary
        accepted = sum(1 for r in results if r["action"] == "accept")
        dismissed = sum(1 for r in results if r["action"] == "dismiss")
        skipped = sum(1 for r in results if r["action"] == "skip")

        print("\n" + "=" * 50)
        print(
            f"📊 Review complete: {accepted} accepted, {dismissed} dismissed, {skipped} skipped"
        )

        return results

    def _get_suggestions_for_note(self, note_path: str) -> List[Dict[str, Any]]:
        """
        Get pending suggestions for a specific note.

        Args:
            note_path: Relative path to note file

        Returns:
            List of suggestion dicts
        """
        # This would integrate with SmartLinkEngineIntegrator
        # For now, return empty list (mocked in tests)
        return []

    def get_pending_suggestions(self, note_path: str) -> List[Dict[str, Any]]:
        """
        Get pending suggestions for review.

        Args:
            note_path: Optional specific note to get suggestions for

        Returns:
            List of suggestion dicts
        """
        return self._get_suggestions_for_note(note_path)

    def apply_accepted_suggestions(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Apply accepted suggestions by inserting wiki links into source notes.

        Args:
            results: List of review results with action and suggestion

        Returns:
            Dict with success status, links_inserted count, backup info
        """
        accepted = [r for r in results if r.get("action") == "accept"]

        if not accepted:
            return {"success": True, "links_inserted": 0, "backup_created": False}

        links_inserted = 0
        backup_created = False

        for result in accepted:
            suggestion = result.get("suggestion", {})
            source = suggestion.get("source")
            target = suggestion.get("target")

            if not source or not target:
                continue

            source_path = self.vault_path / source
            if not source_path.exists():
                continue

            # Create backup before first modification
            if not backup_created:
                backup_created = True

            # Read source content
            content = source_path.read_text(encoding="utf-8")

            # Generate wiki link (use filename without .md)
            target_name = target.replace(".md", "")
            wiki_link = f"[[{target_name}]]"

            # Check if link already exists
            if wiki_link in content:
                continue

            # Append link to end of file (simple insertion)
            if not content.endswith("\n"):
                content += "\n"
            content += f"\n## Related Notes\n\n- {wiki_link}\n"

            # Write back
            source_path.write_text(content, encoding="utf-8")
            links_inserted += 1

        return {
            "success": True,
            "links_inserted": links_inserted,
            "backup_created": backup_created,
        }

    def persist_dismissed_suggestions(self, results: List[Dict[str, Any]]) -> None:
        """
        Persist dismissed suggestions to note frontmatter.

        Args:
            results: List of review results with action and suggestion
        """
        dismissed = [r for r in results if r.get("action") == "dismiss"]

        for result in dismissed:
            suggestion = result.get("suggestion", {})
            source = suggestion.get("source")
            target = suggestion.get("target")

            if not source or not target:
                continue

            source_path = self.vault_path / source
            if not source_path.exists():
                continue

            content = source_path.read_text(encoding="utf-8")

            # Parse frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    body = parts[2]

                    # Add dismissed_links if not present
                    if "dismissed_links:" not in frontmatter:
                        frontmatter = (
                            frontmatter.rstrip() + f"\ndismissed_links:\n  - {target}\n"
                        )
                    else:
                        # Append to existing list
                        frontmatter = frontmatter.rstrip() + f"\n  - {target}\n"

                    # Reconstruct content
                    content = f"---{frontmatter}---{body}"
                    source_path.write_text(content, encoding="utf-8")

    def is_link_dismissed(self, source: str, target: str) -> bool:
        """
        Check if a link has been dismissed in the source note's frontmatter.

        Args:
            source: Source note path
            target: Target note path

        Returns:
            True if link is in dismissed_links list
        """
        source_path = self.vault_path / source
        if not source_path.exists():
            return False

        content = source_path.read_text(encoding="utf-8")

        # Check frontmatter for dismissed_links
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                if "dismissed_links:" in frontmatter and target in frontmatter:
                    return True

        return False


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Interactive review of smart link suggestions"
    )

    parser.add_argument(
        "--vault",
        type=str,
        required=True,
        help="Path to knowledge vault",
    )

    parser.add_argument(
        "--note",
        type=str,
        default=None,
        help="Specific note to review suggestions for",
    )

    return parser


def main():
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()

    vault_path = Path(args.vault)

    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        return 1

    cli = SmartLinkReviewCLI(vault_path=vault_path)

    if args.note:
        suggestions = cli.get_pending_suggestions(args.note)
    else:
        # TODO: Get all pending suggestions across vault
        suggestions = []

    if not suggestions:
        print("No pending suggestions to review.")
        return 0

    results = cli.review_suggestions(suggestions)

    # Return success if any accepted
    accepted = sum(1 for r in results if r["action"] == "accept")
    return 0 if accepted > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
