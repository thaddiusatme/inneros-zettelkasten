# TDD Iteration 1: Automation Helper Entrypoint – Lessons Learned

**Date**: 2025-11-22  
**Branch**: `feature/automation-helper-script-entrypoints`  
**Epic**: #50 – Automation CLIs & Visibility (Option A: helper script + entrypoints)

## 🎯 Objective

Provide a single, ergonomic automation entrypoint that routes to the day‑to‑day commands developers actually use:

- Daemon management (start/stop/status)
- AI inbox sweep
- AI inbox metadata repair

while preserving the ADR‑004 pattern (thin CLIs over well‑tested workflows) and keeping the design compatible with future `console_scripts` packaging.

## ✅ TDD Outcomes

### RED Phase

- New test module: `development/tests/unit/cli/test_inneros_automation_cli.py`.
- Defined behavior for a new helper module `src.cli.inneros_automation_cli`:
  - `daemon start|stop|status` → `python3 -m src.cli.daemon_cli ...`
  - `ai inbox-sweep` → `python3 -m src.cli.inneros_ai_inbox_sweep_cli ...`
  - `ai repair-metadata` → `python3 -m src.cli.inneros_ai_repair_metadata_cli ...`
- Tests verify:
  - Correct module routing via `python3 -m ...`.
  - Argument forwarding (`--repo-root`, `--execute`, `--format`).
  - Exit‑code propagation from the underlying CLI.

### GREEN Phase

- New implementation: `development/src/cli/inneros_automation_cli.py`.
- `main(argv)` routes on the first token:
  - `daemon ...` → `_handle_daemon([...])`.
  - `ai ...` → `_handle_ai([...])`.
- `daemon` handler:
  - Builds `['python3', '-m', 'src.cli.daemon_cli', subcommand]` and calls `_run_subprocess`.
- `ai` handler:
  - `inbox-sweep` → `['python3', '-m', 'src.cli.inneros_ai_inbox_sweep_cli', *forwarded]`.
  - `repair-metadata` → `['python3', '-m', 'src.cli.inneros_ai_repair_metadata_cli', *forwarded]`.
- `_run_subprocess(cmd)` is a tiny wrapper around `subprocess.run(check=False)` returning `returncode`.
- Unknown commands/subcommands return non‑zero without attempting subprocess calls.

**Test status:**

```bash
pytest development/tests/unit/cli/test_inneros_automation_cli.py -q
# 6 passed in ~0.02s
```

### REFACTOR Phase

- Kept the helper intentionally small and focused:
  - `main` only does high‑level dispatch.
  - `_handle_daemon`, `_handle_ai`, and `_run_subprocess` isolate responsibilities.
- No additional abstraction introduced yet; we’ll only generalize once we add a third/fourth AI workflow.

## 💡 Key Learnings

1. **Subprocess boundary as a stable contract**
   - Using `python3 -m src.cli.<module>` keeps the helper agnostic of internal function signatures.
   - This aligns with future `console_scripts` mappings: the helper’s behavior can be re‑exposed as `inneros-automation` without rewriting its internals.

2. **Exit‑code propagation is non‑negotiable for automation**
   - Explicit tests for non‑zero exit codes (e.g. status/repair returning 5/3) ensure the helper never “swallows” failures.
   - This is critical if we later hang CI or cron automation off this helper.

3. **Thin helper, rich CLIs**
   - The helper does **routing + argument pass‑through only**.
   - All actual work and validation logic stays inside the dedicated CLIs (`daemon_cli`, `inneros_ai_inbox_sweep_cli`, `inneros_ai_repair_metadata_cli`).
   - This matches ADR‑004 and keeps risk low: adding a new entrypoint is cheap and safe.

4. **Test style: monkeypatch `subprocess.run` instead of CLI internals**
   - Patching at the subprocess boundary made it easy to assert exact argument lists and exit codes without coupling to the internal API of each CLI.
   - This keeps the helper’s tests stable even if the underlying CLIs refactor their internals.

## 📁 Files Touched

- **New** `development/src/cli/inneros_automation_cli.py`
  - Main helper entrypoint for automation routing.
- **New** `development/tests/unit/cli/test_inneros_automation_cli.py`
  - 6 focused tests covering daemon routing, AI routing, argument forwarding, and exit‑code propagation.

## 🚀 Impact on Epic #50

- Provides the core building block for a **single automation helper entrypoint**.
- Developers get memorable commands like:
  - `inneros-automation daemon status`
  - `inneros-automation ai inbox-sweep --repo-root . --format json`
  - `inneros-automation ai repair-metadata --repo-root . --execute --format text`
- Design is ready for future packaging as `console_scripts` without rework.

## 🔜 Next Iteration Ideas

- Add a thin shell wrapper (e.g. `inneros.sh` or `development/inneros-automation`) that invokes `python3 -m src.cli.inneros_automation_cli ...` for even shorter commands during development.
- Extend the helper with additional AI workflows once they stabilize (triage, connection discovery) using the same routing pattern.
- Wire the helper into `CLI-REFERENCE.md` and automation runbooks as the primary way to start/stop daemons and run AI inbox tasks.
