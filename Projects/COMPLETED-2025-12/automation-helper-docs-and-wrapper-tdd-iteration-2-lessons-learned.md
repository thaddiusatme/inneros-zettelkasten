# Automation Helper Docs & Wrapper – TDD Iteration 2 (Docs Focus)

**Date**: 2025-11-22  
**Branch**: `feature/automation-helper-docs-and-wrapper`  
**Epic**: #50 Automation CLIs & visibility  
**Scope**: P0 docs + ergonomics for automation helper entrypoint (no behavior changes)

---

## 🎯 Goals

- Make the **automation helper entrypoint discoverable and canonical**.
- Align **CLI reference** and **automation HOWTO** with the new helper pattern.
- Keep the iteration **docs-only** (no behavioral drift from tested helper CLI).

---

## ✅ What Changed This Iteration

### 1) CLI-REFERENCE.md – Automation Helper Section

- Updated overview to describe **three interaction modes**:
  - Dedicated CLIs (ADR‑004)
  - Automation Helper (new)
  - Legacy `inneros` wrapper
- Added **Automation Helper** section:
  - Describes `python3 -m src.cli.inneros_automation_cli` as a thin router.
  - Documents routing behavior:
    - `daemon start|stop|status` → `src.cli.daemon_cli` (via `python3 -m src.cli.daemon_cli ...`).
    - `ai inbox-sweep` → `src.cli.inneros_ai_inbox_sweep_cli`.
    - `ai repair-metadata` → `src.cli.inneros_ai_repair_metadata_cli`.
  - Shows **development examples** and **future console_scripts** shape (`inneros-automation ...`).
  - Explicitly documents forwarded flags:
    - `--repo-root PATH`
    - `--execute`
    - `--format {text,json}`
- Clarified that the **legacy `inneros` wrapper** is for analytics/notes/legacy workflow; new automation flows should use **dedicated CLIs + automation helper**.

### 2) docs/HOWTO/automation-user-guide.md – Helper as Preferred Manual Control

- Added **“Preferred Manual Control: Automation Helper CLI”** section near the top.
- Positioning:
  - `.automation/scripts/*.sh` remain canonical for **scheduled automation** (cron/systemd).
  - The **automation helper CLI** is canonical for **manual run & debug**.
- Added copy‑pasteable examples for:
  - Manual daemon management:
    - `python3 -m src.cli.inneros_automation_cli daemon start`
    - `python3 -m src.cli.inneros_automation_cli daemon status`
  - Manual AI inbox sweep + metadata repair, with realistic `--repo-root` and `--format` usage.
  - Future `inneros-automation` console entrypoint equivalents.

---

## 🧪 Tests (GREEN Phase)

Although this iteration is docs-only, we still ran a quick smoke subset:

- `cd development && pytest tests/unit/cli/test_automation_status_cli.py -q`
  - **Result**: 18/18 tests passing (no regressions).

No helper behavior was modified in this iteration; tests serve as a guardrail that automation status/daemon wiring still behaves as expected.

---

## 🔍 Red → Green → Refactor Summary

### RED (Spec / Expectations)

- Defined desired documentation behavior (from issue spec + previous iteration):
  - Helper must be **discoverable** in CLI reference.
  - Helper must be **preferred** entrypoint in at least one automation HOWTO.
  - Examples must be **realistic and copy‑pasteable**, including `--repo-root`, `--execute`, `--format`.
  - Docs must acknowledge future `console_scripts` shape (`inneros-automation ...`) to avoid future churn.

### GREEN (Minimal Docs Implementation)

- Implemented smallest possible doc changes:
  - One clearly scoped section in `CLI-REFERENCE.md`.
  - One clearly scoped section in `docs/HOWTO/automation-user-guide.md`.
- Kept wording tightly aligned to the **actual helper implementation and tests** from `test_inneros_automation_cli.py`.

### REFACTOR (Docs Architecture / Clarity)

- Ensured **conceptual separation**:
  - **Dedicated CLIs**: core behavior & business logic.
  - **Automation Helper**: routing + ergonomics.
  - **Legacy wrapper**: back‑compat, not the long‑term automation story.
- Reused wording patterns from existing dashboard/status docs so that automation helper feels like a natural part of the CLI ecosystem.

---

## 💡 Key Learnings

1. **Thin helper + strong docs = leverage**
   - The helper itself is intentionally tiny; most of its user value is unlocked by **good documentation and examples**.
   - For UX‑critical CLIs (automation, dashboards, status), docs can be a full TDD iteration on their own.

2. **Docs should match test contracts, not assumptions**
   - Reading `test_inneros_automation_cli.py` first made it trivial to avoid drift:
     - Route targets (`src.cli.daemon_cli`, `inneros_ai_inbox_sweep_cli`, `inneros_ai_repair_metadata_cli`).
     - Exact flags we guarantee to forward (`--repo-root`, `--execute`, `--format`).
   - This keeps docs and code aligned with a single source of truth.

3. **Manual vs scheduled automation needs different entrypoints**
   - Scripts (`.automation/scripts/*.sh`) are perfect for **scheduling** and staged rollout.
   - The helper CLI is better for **ad‑hoc control, debugging, and CI hooks**.
   - Making that distinction explicit in docs prevents confusion later when more daemons/handlers are added.

4. **Future‑proofing with console_scripts framing pays off**
   - Writing docs in terms of `inneros-automation ...` now will reduce churn when packaging arrives.
   - The helper’s routing contract (`python3 -m src.cli.<module>`) maps cleanly to console entrypoints, so no refactor is required—only packaging glue.

---

## 📎 Files Touched

- `CLI-REFERENCE.md`
  - Added Automation Helper section and updated overview.
- `docs/HOWTO/automation-user-guide.md`
  - Added section making the helper the preferred manual automation entrypoint.
- `Projects/ACTIVE/automation-helper-docs-and-wrapper-tdd-iteration-2-lessons-learned.md`
  - This document.

---

## ✅ Iteration Outcome

- **P0 docs acceptance criteria met**:
  - Helper documented in CLI reference with concrete daemon + AI examples and key arguments.
  - At least one automation HOWTO now presents the helper as the preferred manual entrypoint.
- **No behavior changes** to the helper or underlying CLIs in this iteration.
- Branch `feature/automation-helper-docs-and-wrapper` is ready for review and integration with the previous helper entrypoint iteration.
