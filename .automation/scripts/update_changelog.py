#!/usr/bin/env python3
"""Auto-update Windsurf Project Changelog.md with optional LLM formatting.

This script is designed to be called from a *pre-commit* hook. It inspects the
staged changes (`git diff --cached`) and appends a concise, human-readable
summary to `Windsurf Project Changelog.md` at the repo root.

Only Markdown files are considered. Template notes (`Templates/`) and the
changelog file itself are ignored to avoid infinite update loops.

The format appended looks like:

```
### 2025-07-25
- ✚ Added  Inbox/idea-x.md
- ✹ Edited Permanent Notes/note-y.md
- ✖ Deleted Archive/old-z.md
```

If the date section already exists in the changelog, new lines are appended to
that section instead of duplicating the heading.

LLM Integration:
Set INNEROS_USE_LLM=1 to enable local LLM formatting. The script will attempt
to call a local model server (Ollama or OpenAI-compatible) to generate more
natural changelog entries. Falls back to deterministic formatting on failure.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Symbols for change types
SYMBOLS = {"A": "✚ Added ", "M": "✹ Edited", "D": "✖ Deleted"}

# Get repo root (two levels up from this script)
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent  # /.automation/ -> repo root
CHANGELOG = ROOT_DIR / "Windsurf Project Changelog.md"

IGNORED_PREFIXES = ["Templates/", ".automation/"]  # skip self + templates
IGNORED_FILES = {CHANGELOG.name}


def run_git_diff() -> List[str]:
    """Return lines of `git diff --cached --name-status` output."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status", "--diff-filter=ACMD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().splitlines()
    except subprocess.CalledProcessError as exc:
        print("update_changelog.py: git diff failed", file=sys.stderr)
        sys.exit(exc.returncode)


def filter_paths(diff_lines: List[str]):
    """Yield tuples of (status, path) filtered for markdown files we care about."""
    for line in diff_lines:
        if not line:  # skip empty
            continue
        status, *path_parts = line.split("\t")
        path = "\t".join(path_parts)  # in case tabs in filenames
        if not path.endswith(".md"):
            continue
        if any(path.startswith(prefix) for prefix in IGNORED_PREFIXES):
            continue
        if os.path.basename(path) in IGNORED_FILES:
            continue
        yield status, path


def format_entry(status: str, path: str) -> str:
    symbol = SYMBOLS.get(status, status)
    return f"- {symbol:<6} {path}"


def call_local_llm(entries: List[str]) -> Optional[List[str]]:
    """Call local LLM to format changelog entries.
    
    Returns formatted lines if successful, None if failed/disabled.
    Requires INNEROS_USE_LLM=1 and a local model server.
    """
    if not entries or os.getenv("INNEROS_USE_LLM") != "1":
        return None
    
    llm_url = os.getenv("INNEROS_LLM_URL", "http://localhost:11434/api/generate")
    
    # Build prompt with current entries as examples
    prompt = (
        "You are an assistant that formats git change records into InnerOS changelog lines.\n"
        "Use these symbols: ✚ Added, ✹ Edited, ✖ Deleted\n\n"
        "Input changes:\n" + "\n".join(entries) + "\n\n"
        "Output only the formatted markdown lines, one per line."
    )
    
    # Try Ollama format first
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0}
    }
    
    try:
        import requests
        resp = requests.post(llm_url, json=payload, timeout=15)
        resp.raise_for_status()
        
        # Parse Ollama response
        if "response" in resp.json():
            text = resp.json()["response"]
        else:
            # Try OpenAI-compatible format
            text = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extract lines that look like changelog entries
        lines = [l.strip() for l in text.splitlines() 
                if l.strip() and (l.strip().startswith("- ✚") or 
                                 l.strip().startswith("- ✹") or 
                                 l.strip().startswith("- ✖"))]
        
        return lines if lines else None
        
    except Exception as e:
        print(f"LLM call failed, using deterministic format: {e}", file=sys.stderr)
        return None


def update_changelog(entries: List[str]):
    if not entries:
        return  # nothing to do

    today = datetime.now().strftime("%Y-%m-%d")
    heading = f"### {today}"

    if not CHANGELOG.exists():
        CHANGELOG.write_text("# Windsurf Project Changelog\n\n", encoding="utf-8")

    # Read existing content
    with CHANGELOG.open("r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    # Look for existing heading
    try:
        index = lines.index(heading)
        # Insert after heading line while preserving order
        insertion_point = index + 1
        for entry in entries:
            if entry not in lines:  # avoid duplicates in repeated pre-commit runs
                lines.insert(insertion_point, entry)
                insertion_point += 1
    except ValueError:
        # Heading not found; append new section at top (after title)
        insertion_point = 1 if lines and lines[0].startswith("#") else 0
        lines[insertion_point:insertion_point] = ["", heading] + entries + [""]

    # Write back
    with CHANGELOG.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")


def main():
    diff_lines = run_git_diff()
    entries = [format_entry(s, p) for s, p in filter_paths(diff_lines)]
    
    # Try LLM formatting if enabled
    if os.getenv("INNEROS_USE_LLM") == "1":
        llm_entries = call_local_llm(entries)
        if llm_entries:
            entries = llm_entries
            print(f"Using LLM-formatted entries ({len(llm_entries)} lines)", file=sys.stderr)
        else:
            print("LLM formatting failed, using deterministic format", file=sys.stderr)
    
    update_changelog(entries)


if __name__ == "__main__":
    main()
