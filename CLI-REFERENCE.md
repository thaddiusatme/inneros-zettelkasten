# CLI Reference

All commands run from the repo root with `PYTHONPATH=development`. The `Makefile` wraps the most common ones.

> **Scope**: this reference covers only the surviving CLIs after the May 2026 simplification refactor. The full pre-refactor command set (daemons, YouTube, screenshots, dashboards, RAG, agents) is preserved at git tag `pre-simplification-v1.0`.

---

## Make targets (the daily set)

| Target | What it does |
| --- | --- |
| `make setup` | Bootstrap `.venv` + install `requirements.txt` and `dev-requirements.txt` |
| `make review` | Weekly review preview — what should be promoted/dropped this week |
| `make fleeting` | Health snapshot of `Fleeting Notes/` |
| `make inbox` | Process unprocessed inbox notes (AI tag, quality, link suggestions). **Mutates files.** |
| `make inbox-safe` | Dry-run of `make inbox` — no writes |
| `make smoke` | `review` + `fleeting` back-to-back as a sanity check |
| `make lint` / `make format` | `ruff` + `black` |
| `make type` | `pyright` (warnings only) |
| `make test-fast` | CI subset of unit tests, ~30s |
| `make test-unit` | Full unit suite, ~4 min |
| `make unit` | Strict-markers CI gate |
| `make cov` | Unit tests with coverage report |
| `make integ` | Integration tests |
| `make clean-venv` | Remove `.venv` (run `make setup` again to recreate) |

The Makefile uses `VAULT ?= knowledge` — override with `make review VAULT=/path/to/other/vault`.

---

## `workflow_demo.py` — the main maintenance CLI

```bash
PYTHONPATH=development python3 development/src/cli/workflow_demo.py <vault> [flags]
```

| Flag | Purpose |
| --- | --- |
| `--status` | Quick health snapshot (no arg = default action) |
| `--process-inbox` | AI-process the Inbox/ — auto-tag, quality score, link suggestions |
| `--promote NOTE TYPE` | Promote a note to `permanent`/`literature`/`fleeting` |
| `--weekly-review` | Generate the weekly review checklist |
| `--enhanced-metrics` | Detailed vault metrics |
| `--remediate-orphans` | Find and report orphaned notes (no in- or out-links) |
| `--fleeting-health` | Same as `make fleeting` |
| `--fleeting-triage` | Word-count-based triage suggestions ⚠️ heuristic untrusted, see #110 |
| `--comprehensive-orphaned` | Deeper orphaned-note analysis |
| `--import-csv FILE` | Import notes from a CSV |
| `--import-json FILE` | Import notes from a JSON file |
| `--report` | Generate a workflow report |
| `--backup` | Create a timestamped vault backup |
| `--list-backups` / `--prune-backups` | Manage backup directories |
| `--interactive` | Launch interactive workflow mode |
| `--format {text,json}` | Output format for most actions |
| `--export FILE` | Save report/metrics to file |

**Removed flags** (Phase 6 simplification): `--screenshots`, `--evening-screenshots`, `--process-youtube-*`, `--process-inbox-safe`, `--batch-process-safe`, `--performance-report`, `--integrity-report`, `--start-safe-session`, `--process-in-session`, `--onedrive-path`, `--max-screenshots`. The underlying code is preserved at git tag `pre-simplification-v1.0`.

---

## `analytics_demo.py` — vault analytics

```bash
PYTHONPATH=development python3 development/src/cli/analytics_demo.py <vault> [flags]
```

| Flag | Purpose |
| --- | --- |
| `--interactive` | Interactive analytics browser |
| `--section {overview,distributions,quality,temporal,recommendations,insights}` | Show one section |
| `--format {text,json}` | Output format |
| `--export FILE` | Save to file |

Useful for: tag frequency, note-type distribution, temporal patterns, link density.

---

## `connections_demo.py` — semantic connection discovery

```bash
PYTHONPATH=development python3 development/src/cli/connections_demo.py <vault>
```

Finds semantically related notes that aren't yet linked. Uses `src.ai.connections` (the kept AI core).

---

## `summarizer_demo.py` — long-note summarization

```bash
PYTHONPATH=development python3 development/src/cli/summarizer_demo.py <vault>
```

Generates summaries for long notes using `src.ai.summarizer`.

---

## `enhance_demo.py` — note enhancement

```bash
PYTHONPATH=development python3 development/src/cli/enhance_demo.py <vault>
```

Runs `src.ai.enhancer` to improve note quality (rephrase, structure, link suggestions).

---

## `weekly_review_cli.py` — dedicated weekly review

```bash
PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py --vault <vault> <subcommand>
```

Subcommands:

| Subcommand | Purpose |
| --- | --- |
| `weekly-review [--preview]` | Generate the weekly review |
| `enhanced-metrics [--export FILE]` | Detailed metrics report |

This is what `make review` calls.

---

## `fleeting_cli.py` — dedicated fleeting-note tooling

```bash
PYTHONPATH=development python3 development/src/cli/fleeting_cli.py --vault <vault> <subcommand>
```

Subcommands:

| Subcommand | Purpose |
| --- | --- |
| `fleeting-health [--format json]` | Health snapshot |
| `fleeting-triage` | Triage suggestions ⚠️ see #110 |

This is what `make fleeting` calls.

---

## `notes_cli.py`, `backup_cli.py`, `interactive_cli.py`

Specialized tools that pair with `workflow_demo.py` for specific operations. Run with `--help` for each.

---

## `ai_assistant.py` — unified AI maintenance

Combines tagger, summarizer, connections, and enhancer behind one CLI. Run as a module (uses relative imports):

```bash
PYTHONPATH=development python3 -m src.cli.ai_assistant <subcommand>

# Subcommands: process, connect, batch, status
PYTHONPATH=development python3 -m src.cli.ai_assistant process knowledge/Inbox/note.md
PYTHONPATH=development python3 -m src.cli.ai_assistant status
```

---

## Output contract

CLIs that support `--format json` emit a standard envelope:

```json
{
  "success": true,
  "data": { ... action-specific payload ... },
  "meta": { "cli": "workflow_demo", "version": "..." }
}
```

Exit code matches `success` (`0` on true, `1` on false). Use this for shell-script automation.

---

## What was removed

The following CLIs no longer ship with the active repo. They are preserved at git tag `pre-simplification-v1.0`:

- **Daemons / orchestration**: `inneros_automation_cli.py`, `inneros_up_cli.py`, `inneros_status_cli.py`, `automation_status_cli.py`, `daemon_cli.py`
- **Dashboards / web UI**: `dashboard_cli.py`, `terminal_dashboard.py`, `workflow_dashboard.py`
- **YouTube pipeline**: `process_youtube_cli.py` and friends
- **Screenshot/OCR pipeline**: `screenshot_cli.py`, `evening_screenshot_*.py`, `multi_device_detector.py`, `individual_screenshot_utils.py`, `safe_workflow_*.py`
- **Smart-link review queue**: `smart_link_review_cli.py` (depended on the deprecated automation daemon)
- **Quality scoring epic**: `batch_score_ui.py`

If you need any of them, check out the recovery tag: `git checkout pre-simplification-v1.0`.
