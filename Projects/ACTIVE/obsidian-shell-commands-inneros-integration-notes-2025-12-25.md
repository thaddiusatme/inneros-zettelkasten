---
created: 2025-12-25 18:15
type: project
status: active
visibility: private
tags: [obsidian, shell-commands, automation, cli, youtube]
---

# Obsidian Shell Commands ↔ InnerOS CLI Integration Notes

## Outcome

Trigger InnerOS note processing from Obsidian (Command Palette / hotkey) against the **currently active note**, with:

- Core workflow processing (general note enhancement + recommendations)
- YouTube transcript + quote extraction **only for YouTube notes**, writing results back into the same note

## Working assumptions

- Vault root: `/Users/thaddius/repos/inneros-zettelkasten/knowledge`
- Python venv: `/Users/thaddius/repos/inneros-zettelkasten/.venv/bin/python`

## Final “known-good” commands

### Core processing only (active note)

```bash
NOTE={{file_path:absolute}}

"/Users/thaddius/repos/inneros-zettelkasten/.venv/bin/python" \
  "/Users/thaddius/repos/inneros-zettelkasten/development/src/cli/core_workflow_cli.py" \
  "/Users/thaddius/repos/inneros-zettelkasten/knowledge" \
  process-note \
  "$NOTE"
```

### Core processing + conditional YouTube processing (active note)

This requires frontmatter:

- `source: youtube`
- `ready_for_processing: true`

```bash
NOTE={{file_path:absolute}}
LOG=/tmp/inneros-obsidian-process.log

{
  echo "=== RUN $(date) ==="
  echo "NOTE=$NOTE"

  "/Users/thaddius/repos/inneros-zettelkasten/.venv/bin/python" \
    "/Users/thaddius/repos/inneros-zettelkasten/development/src/cli/core_workflow_cli.py" \
    "/Users/thaddius/repos/inneros-zettelkasten/knowledge" \
    process-note \
    "$NOTE"

  if grep -qE '^source:\s*youtube\s*$' "$NOTE" && grep -qE '^ready_for_processing:\s*true\s*$' "$NOTE"; then
    echo "--- YOUTUBE STEP ---"
    "/Users/thaddius/repos/inneros-zettelkasten/.venv/bin/python" \
      "/Users/thaddius/repos/inneros-zettelkasten/development/src/cli/youtube_cli.py" \
      --vault "/Users/thaddius/repos/inneros-zettelkasten/knowledge" \
      process-note \
      "$NOTE"
  else
    echo "--- YOUTUBE STEP SKIPPED (not youtube or not ready) ---"
  fi
} >> "$LOG" 2>&1
```

To inspect logs:

```bash
tail -n 200 /tmp/inneros-obsidian-process.log
```

## Key intricacies (what tripped us up)

### 1) Shell Commands variable expansion is not bash expansion

- Obsidian Shell Commands uses `{{...}}` variables.
- Running a command in Terminal with `{{file_path:absolute}}` will pass it literally.

Diagnostic command:

```bash
echo NOTE={{file_path:absolute}}
```

If this prints empty (`NOTE=`), the plugin did not resolve the active file path (often due to focus / no active note / wrong context).

### 2) Argument ordering for `core_workflow_cli.py`

`core_workflow_cli.py` expects:

1. `vault_path` (positional)
2. subcommand (`process-note`)
3. subcommand args (note path)

Incorrect ordering produces:

- `argument command: invalid choice: '/Users/.../knowledge'`

### 3) The YouTube step must be given the vault path

`youtube_cli.py` should be run with:

- `--vault /Users/.../knowledge`

Otherwise it may not find expected prompt/config paths.

### 4) YouTube processing was blocked by the core workflow’s `ai_processed` flag

Initially, the YouTube note enhancer treated `ai_processed` as meaning “already processed”, which prevented quote insertion after core processing ran.

Fix applied:

- YouTube enhancer now uses **YouTube-specific** frontmatter flags:
  - `youtube_ai_processed`
  - `youtube_processed_at`
  - `youtube_quote_count`
  - `youtube_processing_time_seconds`

This decouples core processing from YouTube quote insertion.

### 5) YouTube URL extraction expectations

YouTube notes often had:

- `video_id` but no `url` in frontmatter

Fixes:

- Template updated to include `url: ${youtubeUrl}`
- Validator updated to construct URL from `video_id` when needed

## Metadata + migration work

### Template

`knowledge/Templates/youtube-video.md` updated:

- Added `url: ${youtubeUrl}` to frontmatter

### Backfill tool

Script created:

- `development/scripts/backfill_youtube_note_frontmatter.py`

Scope:

- Only scans `knowledge/Inbox/YouTube/*.md`

Behavior:

- Dry-run by default
- `--apply` creates backups under:
  - `knowledge/backups/youtube-frontmatter-backfill-<timestamp>/`

Example apply:

```bash
"/Users/thaddius/repos/inneros-zettelkasten/.venv/bin/python" \
  "/Users/thaddius/repos/inneros-zettelkasten/development/scripts/backfill_youtube_note_frontmatter.py" \
  "/Users/thaddius/repos/inneros-zettelkasten/knowledge" \
  --apply
```

## Current state

- Core processing from Obsidian works and modifies the active note.
- YouTube transcript fetch + quote insertion works when:
  - note has `source: youtube`
  - note has `ready_for_processing: true`
  - YouTube step is run with `--vault .../knowledge`

## Next improvements

- Make Obsidian notifications reflect success/failure per step (core vs YouTube).
- Decide if YouTube processing should always run for `source: youtube` regardless of `ready_for_processing`.
- Investigate unusual `quality_score` values (e.g. negative scores observed in one note).
