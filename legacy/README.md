# Legacy — Deprecated Code & Assets

> **Status**: Frozen. Code in this directory is **not maintained** and may not run.
> **Reason**: Removed from the active codebase during the simplification refactor (see `Projects/ACTIVE/SIMPLIFICATION-PLAN.md`).
> **Recovery anchor**: git tag `pre-simplification-v1.0` on `main` contains the full pre-refactor state.

---

## Why this exists

InnerOS was simplified from a multi-purpose AI platform back to its core: an AI-augmented Zettelkasten. Code that doesn't serve that core lives here, preserved but inert.

## Contents

### `youtube-templater-scripts/`

Obsidian Templater JavaScript scripts that powered the YouTube transcript → note workflow. Moved here in Phase 2 of the refactor because YouTube automation is no longer maintained.

| File | Purpose |
|---|---|
| `fetch_youtube_metadata.js` | Pulls video metadata via YouTube API |
| `process_current_youtube_note.js` | Processes the open YouTube note |
| `simple_youtube_trigger.js` | Templater trigger script |
| `trigger_youtube_processing.js` | Full pipeline trigger |
| `test_hello.js`, `test_script.js` | Smoke tests |
| `README-YOUTUBE-PROCESSING.md`, `README.md` | Original docs |

To revive: copy back into the Obsidian vault's templater scripts folder and restore the Python YouTube code from tag `pre-simplification-v1.0`.

---

## Coming in Phase 3

Phase 3 of the simplification refactor will move additional code here:

- `agent-rag/` — AI Agent RAG (ReAct loop, vector store, embedding service, librarian agent)
- `youtube/` — Python YouTube transcript automation, daemons, official API
- `screenshots/` — OneDrive screenshot watchers, OCR, evening processor
- `daemons/` — health monitor, screenshot processor, youtube watcher, smart link daemon
- `web-ui/` — dashboard prototypes
- `quality-scoring-epic/` — LLM deep quality scoring work (issue #86, #88 line)

---

*Do not import from `legacy/` in active code. If something here is needed, it should be properly resurrected and re-tested.*
