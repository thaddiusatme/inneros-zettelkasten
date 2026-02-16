"""
LLM Batch Scorer - Issue #90

Provides batch scoring of notes using LLM with checkpoint/resume support
and rate limiting to avoid overwhelming the Ollama service.

Architecture:
- CheckpointManager: Handles persistence and recovery of scoring progress
- OllamaRateLimiter: Prevents overwhelming Ollama with too many requests
- LLMBatchScorer: Orchestrates batch scoring with checkpoint and rate limiting
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .enhancer import AIEnhancer


class CheckpointManager:
    """Manages checkpoint persistence for batch scoring operations."""

    def __init__(
        self, checkpoint_dir: Path, filename: str = ".llm_scoring_checkpoint.json"
    ):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory to store checkpoint file
            filename: Name of the checkpoint file
        """
        self.checkpoint_path = checkpoint_dir / filename

    def load(self) -> Dict[str, Any]:
        """Load checkpoint from disk, or return empty state."""
        if self.checkpoint_path.exists():
            try:
                return json.loads(self.checkpoint_path.read_text())
            except (json.JSONDecodeError, IOError):
                return {"scored_notes": {}, "timestamp": None}
        return {"scored_notes": {}, "timestamp": None}

    def save(self, scored_notes: Dict[str, Dict[str, Any]]) -> None:
        """Save checkpoint to disk."""
        checkpoint = {
            "scored_notes": scored_notes,
            "timestamp": datetime.now().isoformat(),
        }
        self.checkpoint_path.write_text(json.dumps(checkpoint, indent=2))

    def get_scored_notes(self) -> Dict[str, Dict[str, Any]]:
        """Get dictionary of already-scored notes."""
        return self.load().get("scored_notes", {})

    def clear(self) -> None:
        """Remove checkpoint file."""
        if self.checkpoint_path.exists():
            self.checkpoint_path.unlink()


class OllamaRateLimiter:
    """Rate limiter for Ollama API requests to prevent overloading."""

    def __init__(self, requests_per_minute: int = 30):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.request_count = 0
        self._last_request_time: Optional[float] = None
        self._min_interval = 60.0 / requests_per_minute

    def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limits."""
        if self._last_request_time is not None:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)

        self._last_request_time = time.time()

    def record_request(self) -> None:
        """Record that a request was made."""
        self.request_count += 1
        self._last_request_time = time.time()


class LLMBatchScorer:
    """
    Batch scorer for notes using LLM with checkpoint/resume support.

    Designed for scoring large vaults (2,500+ notes) with:
    - Checkpoint persistence for interruption recovery
    - Rate limiting to avoid overwhelming Ollama
    - Progress tracking and ETA estimation
    """

    def __init__(
        self,
        vault_path: Path,
        requests_per_minute: int = 30,
        enhancer: Optional[AIEnhancer] = None,
    ):
        """
        Initialize batch scorer.

        Args:
            vault_path: Path to the vault directory
            requests_per_minute: Rate limit for Ollama requests
            enhancer: Optional AIEnhancer instance (creates one if not provided)
        """
        self.vault_path = Path(vault_path)
        self.rate_limiter = OllamaRateLimiter(requests_per_minute)
        self.enhancer = enhancer or AIEnhancer()
        self._checkpoint_callbacks: List[Callable] = []

    def find_all_notes(self) -> List[Path]:
        """Find all markdown notes in the vault."""
        notes = []
        exclude_dirs = {
            ".git",
            ".obsidian",
            "node_modules",
            ".venv",
            "venv",
            "__pycache__",
        }

        for md_file in self.vault_path.rglob("*.md"):
            if not any(excluded in md_file.parts for excluded in exclude_dirs):
                notes.append(md_file)

        return sorted(notes)

    def estimate_completion_time(self, use_llm: bool = True) -> Dict[str, Any]:
        """
        Estimate time to complete batch scoring.

        Args:
            use_llm: Whether LLM mode is being used

        Returns:
            Dictionary with total_notes, estimated_seconds, estimated_time
        """
        notes = self.find_all_notes()
        total_notes = len(notes)

        if use_llm:
            # LLM mode: ~3 seconds per note average
            seconds_per_note = 3.0
        else:
            # Heuristic mode: ~0.001 seconds per note
            seconds_per_note = 0.001

        estimated_seconds = total_notes * seconds_per_note

        # Format human-readable time
        if estimated_seconds < 60:
            estimated_time = f"{int(estimated_seconds)}s"
        elif estimated_seconds < 3600:
            minutes = int(estimated_seconds / 60)
            seconds = int(estimated_seconds % 60)
            estimated_time = f"{minutes}m {seconds}s"
        else:
            hours = int(estimated_seconds / 3600)
            minutes = int((estimated_seconds % 3600) / 60)
            estimated_time = f"{hours}h {minutes}m"

        return {
            "total_notes": total_notes,
            "estimated_seconds": estimated_seconds,
            "estimated_time": estimated_time,
            "mode": "llm" if use_llm else "heuristic",
        }

    def score_batch(
        self,
        use_llm: bool = True,
        checkpoint_dir: Optional[Path] = None,
        resume: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Score all notes in the vault.

        Args:
            use_llm: Use LLM for deep analysis (slower but more detailed)
            checkpoint_dir: Directory to store checkpoint file
            resume: If True, resume from existing checkpoint
            progress_callback: Optional callback(processed, total, current_file)

        Returns:
            Dictionary with scoring results and statistics
        """
        notes = self.find_all_notes()
        checkpoint_path = self._get_checkpoint_path(checkpoint_dir)

        # Load existing checkpoint if resuming
        scored_notes: Dict[str, Dict[str, Any]] = {}
        if resume and checkpoint_path.exists():
            checkpoint = json.loads(checkpoint_path.read_text())
            scored_notes = checkpoint.get("scored_notes", {})

        results = []
        errors = []

        for i, note_path in enumerate(notes):
            note_name = note_path.name

            # Skip already scored notes if resuming
            if note_name in scored_notes:
                results.append(scored_notes[note_name])
                continue

            try:
                # Rate limit for LLM mode
                if use_llm:
                    self.rate_limiter.wait_if_needed()

                result = self._score_single_note(note_path, use_llm)
                results.append(result)
                scored_notes[note_name] = result

                # Save checkpoint after each note
                self._save_checkpoint(
                    {
                        "scored_notes": scored_notes,
                        "timestamp": datetime.now().isoformat(),
                    },
                    checkpoint_path,
                )

                if use_llm:
                    self.rate_limiter.record_request()

            except Exception as e:
                errors.append({"note": note_name, "error": str(e)})

            if progress_callback:
                progress_callback(i + 1, len(notes), note_name)

        # Calculate aggregate statistics
        quality_scores = [
            r.get("quality_score", 0) for r in results if "quality_score" in r
        ]
        coherence_scores = [
            r.get("coherence_score", 0) for r in results if "coherence_score" in r
        ]

        return {
            "total_scored": len(results),
            "total_errors": len(errors),
            "errors": errors,
            "average_quality": (
                sum(quality_scores) / len(quality_scores) if quality_scores else 0
            ),
            "average_coherence": (
                sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0
            ),
            "results": results,
        }

    def _score_single_note(self, note_path: Path, use_llm: bool) -> Dict[str, Any]:
        """Score a single note."""
        content = note_path.read_text(encoding="utf-8")
        result = self.enhancer.analyze_note_quality_deep(content, use_llm=use_llm)
        result["path"] = str(note_path)
        result["name"] = note_path.name
        return result

    def _get_checkpoint_path(self, checkpoint_dir: Optional[Path] = None) -> Path:
        """Get path for checkpoint file."""
        base_dir = checkpoint_dir or self.vault_path
        return base_dir / ".llm_scoring_checkpoint.json"

    def _save_checkpoint(self, checkpoint: Dict[str, Any], path: Path) -> None:
        """Save checkpoint to disk."""
        path.write_text(json.dumps(checkpoint, indent=2))
