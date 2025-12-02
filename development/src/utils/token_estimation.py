"""Shared token estimation utilities for GPT OSS 20B workflows.

This module provides a small, stable API for estimating token counts from
plain text. It is intentionally conservative and deterministic so callers
like AIHS Mode A and the ADR-010 daily content pull pipeline can enforce
explicit token budgets without depending on a specific tokenizer
implementation.

The initial implementation uses a calibrated character-based heuristic
aligned with ADR 9/10/11 guidance:

- We assume ~4 characters per token for English technical prose.
- Callers are expected to keep combined content within an 8k–10k token
  band and reserve additional headroom for instructions and output.

The heuristic can be upgraded (for example to use an actual tokenizer) as
long as the public API and basic behavioural expectations tested in
``test_token_estimation_adr11_tdd_1.py`` remain stable.
"""

from typing import Iterable

# Approximate characters-per-token ratio for GPT OSS 20B style models.
# This mirrors the existing ``chars // 4`` heuristic used elsewhere in the
# codebase while giving us a single place to refine the constant.
_ESTIMATED_CHARS_PER_TOKEN: float = 4.0


def estimate_tokens(text: str) -> int:
    """Estimate tokens for a single text fragment.

    Parameters
    ----------
    text:
        Input text to estimate.

    Returns
    -------
    int
        Non-negative integer token estimate based on a simple
        characters-per-token heuristic.
    """

    if not text:
        return 0

    length = len(text)
    if length <= 0:
        return 0

    # Integer division keeps the estimate stable and deterministic.
    return int(length // _ESTIMATED_CHARS_PER_TOKEN)


def estimate_tokens_for_bodies(bodies: Iterable[str]) -> int:
    """Estimate tokens for a collection of text bodies.

    This helper is designed to be the shared entrypoint for batch token
    estimation across pipelines. It simply sums the primitive estimator
    over each body so callers can reason about per-item contributions and
    total budgets consistently.
    """

    total = 0
    for body in bodies:
        total += estimate_tokens(body)
    return total
