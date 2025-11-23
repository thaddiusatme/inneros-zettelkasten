# GitHub Issue Update – Automation Helper Entrypoint (Epic #50)

**Date**: 2025-11-22  
**Issue**: #50 – Automation CLIs & visibility (Option A: helper script + entrypoints)  
**Branch**: `feature/automation-helper-script-entrypoints`

---

## 📝 Summary

**Objective**: Implement a thin automation helper entrypoint that routes to existing automation CLIs (daemon + AI workflows) so day‑to‑day commands are memorable and easy to script.

This iteration focused purely on the **helper layer**, building on the existing, tested CLIs:

- `daemon_cli.py` (daemon start/stop/status)
- `inneros_ai_inbox_sweep_cli.py` (AI inbox sweep)
- `inneros_ai_repair_metadata_cli.py` (AI inbox metadata repair)

---

## ✅ Work Completed (TDD Iteration 1)

### 1. New Helper CLI Module

- **File**: `development/src/cli/inneros_automation_cli.py`
- Provides a single entrypoint (Python-level today, packaging‑ready for `console_scripts` later):
  - `inneros-automation daemon start|stop|status`
  - `inneros-automation ai inbox-sweep [--repo-root ...] [--format ...]`
  - `inneros-automation ai repair-metadata [--repo-root ...] [--execute] [--format ...]`
- Implementation details:
  - Uses `argparse`-style `main(argv)` signature but keeps parsing minimal:
    - First token = top‑level group (`daemon` or `ai`).
    - Second token = subcommand (`start|stop|status`, `inbox-sweep`, `repair-metadata`).
  - Routes via `python3 -m` to dedicated CLIs:
    - `python3 -m src.cli.daemon_cli ...`
    - `python3 -m src.cli.inneros_ai_inbox_sweep_cli ...`
    - `python3 -m src.cli.inneros_ai_repair_metadata_cli ...`
  - All additional flags are forwarded transparently:
    - `--repo-root`, `--execute`, `--format`, etc.
  - Exit codes are **passed through** from the underlying process so automation can rely on success/failure.

### 2. TDD Test Suite for Routing and Exit Codes

- **File**: `development/tests/unit/cli/test_inneros_automation_cli.py`
- 6 focused tests verifying:
  - **Daemon routing**:
    - `daemon start|stop|status` → `python3 -m src.cli.daemon_cli <subcommand>`.
    - Different return codes (0 vs non‑zero) from the underlying CLI are propagated.
  - **AI inbox sweep routing**:
    - `ai inbox-sweep --repo-root REPO --format json` → `python3 -m src.cli.inneros_ai_inbox_sweep_cli ...`.
    - Asserts that `--repo-root` and `--format` are forwarded with correct values.
  - **AI repair metadata routing**:
    - `ai repair-metadata --repo-root REPO --execute --format text` → `python3 -m src.cli.inneros_ai_repair_metadata_cli ...`.
    - Asserts presence of `--repo-root`, `--execute`, and `--format text`.
  - **Unknown commands**:
    - Unknown top‑level commands return non‑zero and do **not** attempt to call subprocess.
- Tests monkeypatch `subprocess.run` to inspect the built command and control `returncode` without depending on the internals of the underlying CLIs.

> Status: `pytest development/tests/unit/cli/test_inneros_automation_cli.py -q` → **6/6 tests passing**.

### 3. Lessons Learned Document

- **File**: `Projects/ACTIVE/automation-helper-entrypoint-tdd-iteration-1-lessons-learned.md`
- Captures:
  - Why a thin helper is safer than another “god CLI”.
  - Benefits of routing via `python3 -m src.cli.<module>` as a stable packaging contract.
  - Importance of explicit exit‑code propagation for future cron/CI usage.

---

## 📊 Impact on Epic #50

- Delivers the **core helper entrypoint** for P0:
  - A single place to run daemon management and the two FR3 AI workflows.
- Keeps ADR‑004 intact: helper does only routing + argument pass‑through; all business logic stays in dedicated CLIs.
- Helper is **console_scripts‑ready**: a future package can expose it as `inneros-automation` without refactoring.

---

## 🚧 Notes / Follow‑Ups

- Pre‑commit CLI pattern linter currently fails in this worktree because `development/scripts/cli_pattern_linter.py` is missing here (hook can’t import the linter script). The helper itself is tested and green; once the linter script is mirrored into this worktree or the hook is updated, the commit should pass without `--no-verify`.

- Proposed next steps for #50:
  1. **Wire helper into docs** (`CLI-REFERENCE.md` + automation runbook) so examples use the helper entrypoint instead of raw Python invocations.
  2. **Add a thin shell wrapper** (`inneros-automation` or `inneros.sh`) that calls `python3 -m src.cli.inneros_automation_cli ...` for local ergonomics.
  3. **Extend helper** with additional AI workflow shortcuts (triage, connection discovery) once those CLIs stabilize.
