---
type: project-manifest
created: 2025-12-20 00:00
updated: 2025-12-20 00:00
status: active
priority: P0
tags: [cli, automation, adr-004, integration-tests, json-contract]
---

# Issue #39: CLI Layer Extraction (ADR-004) — Project Manifest

## Summary

Migrate automation scripts off deprecated `workflow_demo.py` and onto dedicated CLIs (per ADR-004), then harden the new CLI surface for automation reliability by standardizing a JSON output contract and validating it via both unit and subprocess integration tests.

## Problem

InnerOS automation relies on shell scripts and scheduled/daemon execution. Historically these scripts invoked `workflow_demo.py`, which is deprecated and does not match the dedicated CLI architecture. This creates:

- Drift between “developer CLI demos” and “automation-safe entry points”
- Fragile parsing/output (especially for automation) due to inconsistent JSON
- Higher regression risk when scripts or CLIs change

## Goals

- Remove all automation script dependencies on `workflow_demo.py`.
- Ensure automation entry points are dedicated CLIs with stable command signatures.
- Standardize a cross-CLI JSON output contract (`--format json`) for automation parsing.
- Ensure both success and error paths emit contract-compliant JSON.
- Add regression protection via static script analysis tests and subprocess-level CLI tests.

## Non-Goals

- Re-architect the internal workflow engines (WorkflowManager decomposition is separate).
- Improve Smart Link quality, screenshot OCR, or YouTube extraction behavior (separate epics).
- Replace shell scripts with Python daemons (separate daemonization work).

## Stakeholders / Users

- You (daily operator): want reliable “automation wiring” with predictable behavior.
- Automation layer: shell scripts + daemons that require stable CLI contracts.

## Current Status

**Implementation state**: Most of this project is complete across TDD Iterations 1–5, with additional P1 hardening items remaining.

### Completed Deliverables (TDD Iterations)

#### Iteration 1 — CLI migration + missing CLIs

- Added `backup` command to `backup_cli.py`.
- Created `screenshot_cli.py` with `process` subcommand.
- Migrated 5 automation scripts to dedicated CLIs.
- Verified: no automation scripts call `workflow_demo.py`; `make unit` green.

#### Iteration 2 — Regression protection for script → CLI wiring

- Added fast integration tests that statically analyze 5 automation shell scripts.
- Tests ensure:
  - No `workflow_demo.py` usage
  - Expected CLIs referenced
  - ADR-004 marker comments present
  - Scripts exist + executable

#### Iteration 3 — JSON output contract + hygiene

- Implemented standardized JSON output contract for `backup_cli.py` + `screenshot_cli.py`.
- Extracted shared module: `development/src/cli/cli_output_contract.py`.
- Added contract tests.
- Removed accidentally tracked cache file from git.

#### Iteration 4 — Extend JSON contract to core CLIs

- Applied JSON contract to:
  - `core_workflow_cli.py` (status, process-inbox)
  - `fleeting_cli.py` (fleeting-health, fleeting-triage)
  - `weekly_review_cli.py` (weekly-review, enhanced-metrics)
- Ensured error paths emit contract JSON (not stderr-only prints).

#### Iteration 5 — Subprocess contract validation

- Added subprocess tests that invoke real CLI entry points and validate JSON output.
- Fixed 2 CLIs to emit contract JSON on init failures.

## Key Artifacts / Code Locations

- **Shell scripts** (must not call `workflow_demo.py`):
  - `.automation/scripts/health_monitor.sh`
  - `.automation/scripts/weekly_deep_analysis.sh`
  - `.automation/scripts/process_inbox_workflow.sh`
  - `.automation/scripts/automated_screenshot_import.sh`
  - `.automation/scripts/supervised_inbox_processing.sh`

- **Dedicated CLIs**:
  - `development/src/cli/backup_cli.py`
  - `development/src/cli/screenshot_cli.py`
  - `development/src/cli/core_workflow_cli.py`
  - `development/src/cli/fleeting_cli.py`
  - `development/src/cli/weekly_review_cli.py`

- **Shared JSON contract**:
  - `development/src/cli/cli_output_contract.py`

- **Tests**:
  - `development/tests/unit/test_cli_layer_extraction.py`
  - `development/tests/integration/test_automation_scripts_invoke_dedicated_clis.py`
  - `development/tests/unit/test_cli_json_output_contract.py`
  - `development/tests/unit/test_core_clis_json_output_contract.py`
  - `development/tests/integration/test_cli_json_output_contract_subprocess.py`

## JSON Output Contract (Automation-Safe)

All CLIs supporting `--format json` must emit:

- `success`: boolean
- `errors`: list of strings
- `data`: dict payload (command-specific)
- `meta`: dict with:
  - `cli`
  - `subcommand`
  - `timestamp`

Exit code semantics:
- `success=true` → exit `0`
- `success=false` → non-zero exit

## Milestones

### M0 — Migration off `workflow_demo.py` (P0)

- [x] No automation scripts call `workflow_demo.py`.
- [x] Dedicated CLIs exist for all called automation commands.

### M1 — Script wiring regression protection (P0)

- [x] Integration tests statically verify script → CLI wiring.

### M2 — JSON contract standardization (P0)

- [x] Contract module implemented and used by key CLIs.
- [x] Unit tests validate contract in success + failure paths.

### M3 — Subprocess validation (P1)

- [x] Subprocess tests validate real CLI execution and JSON parsing.

### M4 — Remaining hardening (P1, remaining)

- [ ] Standardized logging context across CLIs (cli name, vault, flags).
- [ ] Fix pre-commit pytest hook slowness / wrong-python issue (Issue #48).
- [ ] Update docs to reflect dedicated CLIs as the canonical interface.

## Acceptance Criteria

- [x] Shell scripts under `.automation/scripts/` do not reference `workflow_demo.py`.
- [x] Automation-invoked CLIs accept stable subcommands consistent with ADR-004.
- [x] `--format json` output is contract-compliant on success paths.
- [x] `--format json` output is contract-compliant on failure paths.
- [x] Exit codes match `success` consistently.
- [x] Subprocess tests cover at least the 5 primary automation CLIs.

## Risks / Open Issues

- **Pre-commit hook reliability**: pre-commit pytest issues can slow development and encourage `--no-verify` commits. Tracked as Issue #48.
- **Script runtime drift**: static analysis tests prevent obvious wiring regressions but don’t guarantee the shell scripts succeed end-to-end in the user environment.

## Next Actions

- Decide whether to treat the project as “done” and move the iteration lessons learned to completed archive after merge.
- If continuing:
  - Implement P1 logging context standardization.
  - Address Issue #48 so the development workflow stays fast and trustworthy.

## References

- ADR-004: CLI Layer Extraction
- Issue #39: Migrate automation scripts to dedicated CLIs
- Lessons learned:
  - `Projects/ACTIVE/issue-39-cli-layer-extraction-tdd-iteration-1-lessons-learned.md`
  - `Projects/ACTIVE/issue-39-cli-layer-extraction-tdd-iteration-2-lessons-learned.md`
  - `Projects/ACTIVE/issue-39-cli-layer-extraction-tdd-iteration-3-lessons-learned.md`
  - `Projects/ACTIVE/issue-39-cli-json-contract-tdd-iteration-4-lessons-learned.md`
  - `Projects/ACTIVE/issue-39-cli-json-contract-subprocess-tdd-5-lessons-learned.md`
