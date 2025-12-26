# Prompt — Phase 1: Persist `triage_recommendation`

## The prompt

Let's create a new branch for the next feature: **persist-processing-results-phase-1-triage-recommendation**.

We want to perform **TDD** with **Red → Green → Refactor**, followed by **git commit** and **lessons learned documentation**. This equals one iteration.

### Updated Execution Plan (focused P0/P1)

- **Brief context / current priorities**: Parent sprint is **Make InnerOS Usable**. This feature removes the "groundhog day" effect by persisting actionable outputs from `process-note`.
- **Guidance I’m following**:
  - `.windsurf/rules/updated-development-workflow.md` (TDD + test tier discipline)
  - `.windsurf/rules/architectural-constraints.md` (avoid god classes / extract utilities)
  - `.windsurf/guides/tdd-methodology-patterns.md` (fast Red/Green cycles)
- **Critical path / current blocker**: `process-note` computes recommendations + connections but only partially persists outputs (Phase 1 persisted `triage_recommendation`; links/sections still not persisted).

### Current Status

- **Completed**:
  - Identified actual pipeline: `core_workflow_cli process-note` → `WorkflowManager.safe_process_inbox_note` → `NoteProcessingCoordinator.process_note`.
  - Confirmed current persistence: writes `tags`, `ai_processed` (timestamp), `quality_score` (frontmatter only).
  - Implemented Phase 1 persistence of `triage_recommendation` in `development/src/ai/note_processing_coordinator.py::process_note`.
  - Code committed: `0a7d3b3`
  - Lessons learned: `Projects/COMPLETED-2025-12/persist-triage-recommendation-phase-1-lessons-learned.md`

### Lessons from last iteration

- Treat `ai_processed` as an ISO timestamp string (not boolean).
- Keep persistence logic idempotent/overwrite-based to tolerate re-processing.

---

## P0 — Critical/Unblocker (P0)

### Main P0 task: Persist `triage_recommendation`

- **Implementation detail 1**: Derive `triage_recommendation` from the primary recommendation action produced by existing quality gating logic.
- **Implementation detail 2**: Persist the field to frontmatter (Dataview-queryable) and **overwrite** it on each run.
- **Implementation detail 3**: Maintain backwards compatibility (notes without this field still work).

### Acceptance Criteria

- `triage_recommendation` is written to frontmatter after `process-note` runs.
- Value is one of:
  - `promote_to_permanent`
  - `move_to_fleeting`
  - `improve_or_archive`
  - absent/null when inconclusive

---

## P1 — Next Priority Theme (P1)

- Defer to Phase 2/3 prompt: persist `suggested_links` + body section.

---

## Task Tracker

- **[Completed]** Phase 1 — Persist `triage_recommendation`
- **[Pending]** Phase 2 — Persist `suggested_links`
- **[Pending]** Phase 3 — Append/replace `## Suggested Connections` section
- **[Pending]** Phase 4 — Batch inbox processing + `make inbox`

---

## TDD Cycle Plan

### Red Phase

- Add unit test(s) in `development/tests/unit/test_note_processing_coordinator.py`:
  - `test_process_note_persists_triage_recommendation`
  - Assert: after `process_note()` runs (non-dry-run), the file frontmatter contains `triage_recommendation` equal to the expected action.

### Green Phase

- Implement minimal logic in `development/src/ai/note_processing_coordinator.py`:
  - Select a triage action from `results["recommendations"]`.
  - Write `frontmatter["triage_recommendation"] = <action>` before `safe_write(...)`.

### Refactor Phase

- Extract a tiny helper (if needed) for selecting the "primary" recommendation.
- Keep `NoteProcessingCoordinator` within size limits; if helpers expand, propose extracting a `src/utils/triage.py`.

---

## Next Action

- Phase 1 is complete (commit `0a7d3b3`).
- Next: proceed to Phase 2/3 prompt: `Projects/ACTIVE/prompt-phase-2-3-persist-links-and-body-section.md`.
