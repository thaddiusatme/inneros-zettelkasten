# GitHub Issue: Persist `process-note` Outputs (Phase 4–5)

> **Copy this to create a GitHub issue when `gh auth login` is configured**

---

## Title

Add batch inbox processing: `make inbox` / `make inbox-safe`

## Labels

Recommended (adjust if label names differ in GitHub):

`enhancement`, `priority:p0`, `size:medium`

## Body

### Summary

There is no single daily entry point to batch-process Inbox notes and persist `process-note` outputs. This creates workflow friction and prevents daily adoption.

This issue adds:

- `make inbox` to process eligible notes and persist outputs
- `make inbox-safe` to dry-run scan + preview without writes

### Dependencies

- Phase 1 completed: `triage_recommendation` persisted (commit `0a7d3b3`)
- Assumes Phases 2–3 are implemented (persist `suggested_links` + body section), but the batch runner can start by persisting whatever Phase 1+ provides.

### Requirements

#### Phase 4: Batch inbox processing

- Determine “unprocessed” notes:
  - Include notes where `ai_processed` missing OR `triage_recommendation` missing
  - Skip notes where both are present
- Process `.md` files under `Inbox/` (recursive if needed)
- Use existing workflow path (do not fork a second pipeline)
- Output a summary:
  - total scanned
  - total processed
  - triage breakdown by action
  - errors with file paths

#### Phase 5: Make targets + docs

- Add Makefile targets:
  - `make inbox`
  - `make inbox-safe`
- Ensure exit codes:
  - 0 success
  - 1 if any errors
- JSON output available for automation (`--format json`)

### Acceptance Criteria

- [ ] `make inbox` processes all eligible notes and persists outputs
- [ ] `make inbox-safe` performs the same scan but performs no writes
- [ ] Skip logic works reliably and is idempotent on re-run
- [ ] Tests cover selection + skip logic and a tmp_path integration scenario

### Implementation Notes

- Prefer extending `development/src/cli/core_workflow_cli.py` rather than creating a new CLI.
- Extract scanning/eligibility logic into a small utility if it grows.

### Related Docs

- Prompt: `Projects/ACTIVE/prompt-phase-4-5-batch-inbox-processing.md`
- Phase 2–3 prompt: `Projects/ACTIVE/prompt-phase-2-3-persist-links-and-body-section.md`

---

## Create Command

```bash
gh issue create \
  --title "Add batch inbox processing: make inbox / make inbox-safe" \
  --label "enhancement,priority:p0,size:medium" \
  --body-file Projects/ACTIVE/github-issue-persist-processing-results-phase-4-5-batch-inbox.md
