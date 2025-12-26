# Prompt — Phases 4–5: Batch inbox processing (`make inbox` / `make inbox-safe`)

## The prompt

Let's create a new branch for the next feature: **persist-processing-results-phase-4-5-batch-inbox**.

We want to perform **TDD** with **Red → Green → Refactor**, followed by **git commit** and **lessons learned documentation**. This equals one iteration.

### Updated Execution Plan (focused P0/P1)

- **Brief context / current priorities**: Parent sprint is **Make InnerOS Usable**. Phases 1–3 persist per-note results. Now we need a single daily entry point (`make inbox`) to batch-process unprocessed Inbox notes.
- **Guidance I’m following**:
  - `.windsurf/rules/updated-development-workflow.md` (TDD + test tiers)
  - `.windsurf/rules/architectural-constraints.md` (avoid new CLI sprawl unless necessary)
  - `.windsurf/rules/privacy-security.md` (no leaking secrets; safe defaults)
- **Critical path / current blocker**: There’s no one-command daily Inbox processing loop; users must manually run per-note commands.

### Current Status

- **Completed**:
  - Phase 1: Persist `triage_recommendation`.
- **Pending (depends on Phases 2–3)**:
  - Phase 2: Persist `suggested_links`.
  - Phase 3: Append/replace `## Suggested Connections` section.
  - Phase 4: Batch processing over `Inbox/` with skip logic.
  - Phase 5: Make targets + docs updates.

### Lessons from last iteration

- Batch workflows must be idempotent and safe on rerun.
- Avoid re-processing notes that already have persisted outputs.

---

## P0 — Critical/Unblocker (P0)

### Main P0 task: Implement batch inbox processing

- **Implementation detail 1**: Determine "unprocessed" notes:
  - include notes where `ai_processed` missing OR `triage_recommendation` missing.
  - skip notes where both are present.
- **Implementation detail 2**: Process `.md` files in `Inbox/` (recursive if needed) using existing workflow path.
- **Implementation detail 3**: Output summary with triage breakdown and error details.

### Secondary P0 task: Dry-run safe mode

- `make inbox-safe` must not write any files.
- It should show what WOULD be processed and what WOULD be written.

### Acceptance Criteria

- `make inbox` processes all eligible notes and persists outputs.
- `make inbox-safe` performs the same scan but performs no writes.
- JSON output is available for automation (`--format json`).

---

## P1 — CLI/UX cohesion (P1)

- Prefer extending `development/src/cli/core_workflow_cli.py` rather than creating a brand new CLI, unless forced.
- Ensure exit codes: 0 success, 1 if any errors.

---

## P2 — Future improvements (P2)

- Add progress bar / improved terminal UX.
- Add configurable ignore patterns.
- Add batch size / concurrency controls (only if safe).

---

## Task Tracker

- **[In progress]** Phase 4 — Batch inbox processing
- **[Pending]** Phase 5 — Make targets + docs updates

---

## TDD Cycle Plan

### Red Phase

- Add unit tests for batch selection + skip logic.
- Add integration test using `tmp_path` vault fixture:
  - mix of processed/unprocessed notes
  - ensure only the right set is modified

### Green Phase

- Implement batch command:
  - either extend `core_workflow_cli.py` with `inbox` subcommand, or implement minimal `inbox_cli.py` if required.
- Add Makefile targets:
  - `make inbox`
  - `make inbox-safe`

### Refactor Phase

- Extract note-scanning/eligibility logic into a small utility function.
- Keep CLI output formatting clean (normal vs JSON).

---

## Next Action (for this session)

1. Inspect existing batch processing entry points (`WorkflowManager.batch_process_inbox`, safe batch APIs).
2. Implement `make inbox` / `make inbox-safe` end-to-end with tests.
3. Commit and document lessons learned.

Would you like me to implement Phase 4/5 now in small, reviewable commits?
