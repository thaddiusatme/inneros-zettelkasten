"""
Notes CLI: Create new review notes (daily, weekly, sprint review, sprint retro)
with prefilled YAML frontmatter and minimal bodies.

Usage examples:
  python3 src/cli/notes_cli.py . new daily --open --git
  python3 src/cli/notes_cli.py . new weekly --open --git
  python3 src/cli/notes_cli.py . new sprint-review --sprint-id 012 --open --git
  python3 src/cli/notes_cli.py . new sprint-retro --sprint-id 012 --open --git
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Ensure project root src/ is importable like other CLIs
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.frontmatter import build_frontmatter  # type: ignore
from src.utils.io import safe_write  # type: ignore


@dataclass
class EditorPrefs:
    cmd: str | None


def _detect_repo_and_roots(user_path: Path) -> tuple[Path, Path]:
    """Detect repository root and preferred Reviews directory.
    Returns (repo_root, reviews_dir).
    - Prefers an existing 'Reviews/' next to repo root.
    - Falls back to creating 'Reviews/' under the provided path.
    - If 'knowledge/Reviews' exists, uses that.
    """
    p = user_path.resolve()

    # If path points to 'knowledge' root, prefer its parent as repo root
    if (p / "Inbox").exists() and p.name == "knowledge":
        repo_root = p.parent
    else:
        # If passed repo root (contains knowledge) use it
        repo_root = p
        if (
            not (repo_root / "knowledge").exists()
            and (p / "knowledge" / "Inbox").exists()
        ):
            repo_root = p
        # If passed knowledge/<subdir>, climb up to repo root
        if (
            p.name in ("Inbox", "Fleeting Notes", "Permanent Notes")
            and (p.parent / "knowledge").exists()
        ):
            repo_root = p.parent.parent

    # Preferred reviews dir resolution
    if (repo_root / "Reviews").exists():
        reviews_dir = repo_root / "Reviews"
    elif (repo_root / "knowledge" / "Reviews").exists():
        reviews_dir = repo_root / "knowledge" / "Reviews"
    else:
        # Default to repo_root/Reviews
        reviews_dir = repo_root / "Reviews"

    return repo_root, reviews_dir


def _iso_week_id(dt: datetime) -> str:
    iso_year, iso_week, _ = dt.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _current_week_bounds(today: datetime) -> tuple[datetime, datetime]:
    # Monday start (weekday: Monday=0)
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _open_in_editor(path: Path, editor_arg: str | None) -> None:
    try:
        if editor_arg:
            subprocess.run([editor_arg, str(path)], check=False)
            return
        # Respect VISUAL/EDITOR
        visual = os.environ.get("VISUAL")
        editor = os.environ.get("EDITOR")
        if visual:
            subprocess.run([visual, str(path)], check=False)
            return
        if editor:
            subprocess.run([editor, str(path)], check=False)
            return
        # macOS fallback: VS Code if available, else open
        if shutil.which("code"):
            subprocess.run(["code", "-g", str(path)], check=False)
            return
        # Generic open (macOS)
        if sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            # Last resort: print path
            print(f"→ Open file manually: {path}")
    except Exception as e:
        print(f"⚠️  Failed to open editor: {e}")


def _git_commit(repo_root: Path, file_path: Path, message: str) -> None:
    try:
        # Ensure we're in a git repo
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
        )
        if result.returncode != 0:
            print("⚠️  Not a git repository. Skipping commit.")
            return
        subprocess.run(
            ["git", "-C", str(repo_root), "add", str(file_path.relative_to(repo_root))],
            check=False,
        )
        subprocess.run(
            ["git", "-C", str(repo_root), "commit", "-m", message], check=False
        )
    except Exception as e:
        print(f"⚠️  Git commit failed: {e}")


def _unique_path(base_path: Path) -> Path:
    if not base_path.exists():
        return base_path
    # append -HHmm if exists
    suffix = datetime.now().strftime("-%H%M")
    return base_path.with_name(base_path.stem + suffix + base_path.suffix)


def _daily_frontmatter() -> dict:
    return {
        "type": "review",
        "scope": "daily",
        "created": _now_str(),
        "status": "promoted",
        "tags": ["daily", "zettelkasten", "scrum"],
        "visibility": "private",
        "week_id": _iso_week_id(datetime.now()),
    }


def _weekly_frontmatter() -> dict:
    week_id = _iso_week_id(datetime.now())
    start, end = _current_week_bounds(datetime.now())
    return {
        "type": "review",
        "scope": "weekly",
        "week_id": week_id,
        "period_start": start.strftime("%Y-%m-%d"),
        "period_end": end.strftime("%Y-%m-%d"),
        "status": "promoted",
        "tags": ["weekly", "review", "retrospective", "scrum"],
        "visibility": "private",
    }


def _sprint_review_frontmatter(sprint_id: str) -> dict:
    return {
        "type": "review",
        "scope": "sprint-review",
        "sprint_id": sprint_id,
        "created": _now_str(),
        "status": "draft",
        "tags": ["review", "sprint"],
        "tz": "America/Los_Angeles",
    }


def _sprint_retro_frontmatter(sprint_id: str) -> dict:
    return {
        "type": "review",
        "scope": "sprint-retrospective",
        "sprint_id": sprint_id,
        "created": _now_str(),
        "status": "draft",
        "tags": ["retrospective", "sprint"],
        "tz": "America/Los_Angeles",
    }


DAILY_BODY = """
# Daily Note — {date}

## Focus
- <1 to 3 bullets for today’s single theme>

## Standup
- Yesterday:
- Today:
- Blockers:

## Links Added
- [[note-id-or-title]] short why it matters

## Wins
- <fast wins and tiny proofs>

## Next
- <top 3 actions, smallest viable steps>

## Journal
- <freeform>

## EOD Micro Retro
- What moved the needle:
- What felt hard:
- What to change tomorrow:
""".lstrip()


WEEKLY_BODY = """
# Weekly Review — {week_id}

## Highlights
- <3 to 5 outcomes, not activities>

## Metrics
- Notes created: <n>
- Orphans before → after: <n> → <n>
- Link density avg: <n>
- Stale notes touched: <n>
- Focus days this week: <n>

## Bridges Created
- [[note-a]] ↔ [[note-b]] why the link matters
- [[note-c]] ↔ [[note-d]]

## What Went Well
-

## What I Will Improve
-

## Next Week Goals
- Outcome 1:
- Outcome 2:
- Outcome 3:

## Sprint Reflection
- Did scope match capacity
- Top blocker pattern
- Experiment to try next sprint
""".lstrip()


SPRINT_REVIEW_BODY = """
# 🚀 Sprint {sprint_id} Review — {date}

## 📈 MVP Metrics
- Content published:
- Leads created:
- Days of consistency (streak):
- Sentiment (1–5):

## ✅ What Shipped
-

## 🔍 KPIs & Outcomes
-

## 🧭 Highlights & Notable Learnings
-

## 🧹 Minimal Content Pipeline Maintenance
- Review backlog health (5 min)
- Prune stale ideas (5 min)
- Tag/link high-potential items (5 min)

## 🎯 Next Sprint Candidates
- [ ]

## 📌 Actions (in-note only)
- [ ]
""".lstrip()


SPRINT_RETRO_BODY = """
# 🔁 Sprint {sprint_id} Retrospective — {date}

## ✅ What Went Well
-

## ⚠️ What Didn’t Go Well
-

## 🔧 What To Improve (Process/Tools)
-

## 📈 MVP Metrics
- Content published:
- Leads created:
- Days of consistency (streak):
- Sentiment (1–5):

## 🧭 Decisions & Rationale
-

## 📌 Actions (in-note only)
- [ ]
""".lstrip()


def _build_note(frontmatter: dict, body: str) -> str:
    return build_frontmatter(frontmatter, body)


def _create_daily(reviews_dir: Path) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    base = reviews_dir / f"daily-{today}.md"
    path = _unique_path(base)
    fm = _daily_frontmatter()
    body = DAILY_BODY.format(date=today)
    content = _build_note(fm, body)
    safe_write(path, content)
    return path


def _create_weekly(reviews_dir: Path) -> Path:
    week_id = _iso_week_id(datetime.now())
    base = reviews_dir / f"weekly-{week_id}.md"
    path = _unique_path(base)
    fm = _weekly_frontmatter()
    body = WEEKLY_BODY.format(week_id=week_id)
    content = _build_note(fm, body)
    safe_write(path, content)
    return path


def _create_sprint_review(reviews_dir: Path, sprint_id: str) -> Path:
    base = reviews_dir / f"sprint-{sprint_id}-review.md"
    path = _unique_path(base)
    fm = _sprint_review_frontmatter(sprint_id)
    body = SPRINT_REVIEW_BODY.format(
        sprint_id=sprint_id, date=datetime.now().strftime("%Y-%m-%d")
    )
    content = _build_note(fm, body)
    safe_write(path, content)
    return path


def _create_sprint_retro(reviews_dir: Path, sprint_id: str) -> Path:
    base = reviews_dir / f"sprint-{sprint_id}-retro.md"
    path = _unique_path(base)
    fm = _sprint_retro_frontmatter(sprint_id)
    body = SPRINT_RETRO_BODY.format(
        sprint_id=sprint_id, date=datetime.now().strftime("%Y-%m-%d")
    )
    content = _build_note(fm, body)
    safe_write(path, content)
    return path


def main():

    parser = argparse.ArgumentParser(
        description="Notes CLI — Create new review notes with frontmatter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 src/cli/notes_cli.py . new daily --open --git
  python3 src/cli/notes_cli.py . new weekly --open --git
  python3 src/cli/notes_cli.py . new sprint-review --sprint-id 012 --open --git
  python3 src/cli/notes_cli.py . new sprint-retro --sprint-id 012 --open --git
        """,
    )

    parser.add_argument("path", help="Path to repository root or knowledge root")

    sub = parser.add_subparsers(dest="command", required=True)
    new_p = sub.add_parser("new", help="Create a new note")

    kind = new_p.add_mutually_exclusive_group(required=True)
    kind.add_argument("--daily", action="store_true", help="Create daily review note")
    kind.add_argument("--weekly", action="store_true", help="Create weekly review note")
    kind.add_argument(
        "--sprint-review", action="store_true", help="Create sprint review note"
    )
    kind.add_argument(
        "--sprint-retro", action="store_true", help="Create sprint retrospective note"
    )

    new_p.add_argument("--sprint-id", help="Sprint ID for sprint notes (e.g., 001)")
    new_p.add_argument(
        "--dir", dest="reviews_dir", help="Override Reviews directory path"
    )
    new_p.add_argument(
        "--open",
        dest="open_in_editor",
        action="store_true",
        help="Open the created note in your editor",
    )
    new_p.add_argument(
        "--editor",
        dest="editor",
        help="Editor command to use (overrides $VISUAL/$EDITOR)",
    )
    new_p.add_argument(
        "--git",
        dest="git_commit",
        action="store_true",
        help="git add + commit after creation",
    )

    args = parser.parse_args()

    user_path = Path(args.path) if Path(args.path).exists() else Path.cwd()

    repo_root, default_reviews_dir = _detect_repo_and_roots(user_path)
    reviews_dir = Path(args.reviews_dir) if args.reviews_dir else default_reviews_dir
    reviews_dir.mkdir(parents=True, exist_ok=True)

    # Create note
    created: Path
    if args.daily:
        created = _create_daily(reviews_dir)
        commit_message = (
            f"docs(reviews): add daily review {created.stem.replace('daily-','')}"
        )
    elif args.weekly:
        created = _create_weekly(reviews_dir)
        commit_message = (
            f"docs(reviews): add weekly review {created.stem.replace('weekly-','')}"
        )
    elif args.sprint_review:
        if not args.sprint_id:
            print("❌ --sprint-id is required for sprint-review")
            sys.exit(1)
        created = _create_sprint_review(reviews_dir, args.sprint_id)
        commit_message = f"docs(reviews): add sprint {args.sprint_id} review"
    else:
        if not args.sprint_id:
            print("❌ --sprint-id is required for sprint-retro")
            sys.exit(1)
        created = _create_sprint_retro(reviews_dir, args.sprint_id)
        commit_message = f"docs(reviews): add sprint {args.sprint_id} retrospective"

    print(f"✅ Created: {created}")

    # Open in editor if requested
    if args.open_in_editor:
        _open_in_editor(created, args.editor)

    # Git commit if requested
    if args.git_commit:
        _git_commit(repo_root, created, commit_message)


if __name__ == "__main__":
    main()
