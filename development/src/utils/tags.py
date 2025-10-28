"""
Tag utilities for InnerOS.

Provides a centralized sanitizer to normalize tags consistently across the
codebase. This mirrors and slightly generalizes the repair script's logic
so that runtime workflows and offline repair share behavior.
"""

from __future__ import annotations

from typing import Iterable, List, Any
import re


def clean_tag(tag: str) -> str:
    """Clean a single tag token.

    - Strip surrounding whitespace
    - Remove leading '#'
    - Normalize internal whitespace
    - Lowercase for consistency
    """
    if not isinstance(tag, str):
        return ""
    # remove leading '#', trim and collapse whitespace
    cleaned = tag.strip().lstrip("#").strip()
    # normalize spaces (tags should be single tokens already after splitting)
    cleaned = " ".join(cleaned.split())
    # strip stray brackets/quotes/backticks and trailing punctuation commonly leaked from bad inputs
    cleaned = cleaned.strip("[](){}\"'`")
    cleaned = cleaned.strip(",;:.")
    # lowercase for consistency
    cleaned = cleaned.lower()
    # discard tokens without any alphanumeric character (e.g., '-', '/', ':', '[')
    if not any(c.isalnum() for c in cleaned):
        return ""
    # allow only lowercase alphanumerics plus -, _, /
    if not re.match(r"^[a-z0-9][a-z0-9\-_/]*$", cleaned):
        # if it doesn't match, try to salvage by removing disallowed chars
        cleaned2 = re.sub(r"[^a-z0-9\-_/]", "", cleaned)
        # must still start with alphanumeric and not be empty
        if cleaned2 and re.match(r"^[a-z0-9]", cleaned2):
            cleaned = cleaned2
        else:
            return ""
    return cleaned


def sanitize_tags(tags_input: Any) -> List[str]:
    """Normalize tags to a deduplicated list of clean strings.

    Accepts:
    - list[str] or other iterables of strings
    - str containing comma/semicolon/whitespace separated tags

    Returns:
    - List of cleaned, lowercase tag strings without leading '#'
    - Empty list for invalid input
    """
    tokens: List[str] = []

    if isinstance(tags_input, str):
        # Handle common separators
        normalized = tags_input.replace(",", " ").replace(";", " ")
        tokens = [t for t in normalized.split() if t]
    elif isinstance(tags_input, Iterable):
        # Already a collection; filter to strings only
        tokens = [t for t in tags_input if isinstance(t, str)]
    else:
        return []

    # Clean and filter empties
    cleaned = [clean_tag(t) for t in tokens]
    cleaned = [t for t in cleaned if t]

    # Deduplicate while preserving order
    seen = set()
    deduped: List[str] = []
    for t in cleaned:
        if t not in seen:
            seen.add(t)
            deduped.append(t)

    return deduped
