# Knowledge Base Cleanup Inventory — October 2025

## Purpose & References

- Aligns with [`updated-file-organization.md`](../..//.windsurf/rules/updated-file-organization.md)
- Automation checkpoints per [`automation-monitoring-requirements.md`](../..//.windsurf/rules/automation-monitoring-requirements.md)
- TDD Iteration Objective: Produce inventory log feeding `tests/automation/test_cleanup_inventory.py`

## P0 Scope (Critical)

1. **Documentation Consolidation**  
   - Projects/ACTIVE  
   - Projects/COMPLETED-*  
   - development/docs/
2. **Automation Asset Mapping**  
   - `.automation/` (scripts, cron, review_queue)  
   - `development/src/automation/` (engines, daemons, demos)
3. **Inbox Pipeline Health**  
   - Ensure knowledge/Inbox/ contains ≤10 actionable captures

## Inventory Checklist

- [x] Collect redundant docs across ACTIVE, COMPLETED-*, development/docs (see table below)
- [ ] Catalog automation scripts/demos and desired destinations
- [ ] Verify backups/rollback paths before moves (DirectoryOrganizer compliance)
- [ ] Draft decision log entries (source → target → rationale)
- [ ] Confirm Projects/ACTIVE/ holds ≤10 items post-cleanup

## Inventory Tables

### Documentation Sources

| Source File | Current Location | Proposed Destination | Decision Owner | Status | Notes |
|-------------|-----------------|----------------------|----------------|--------|-------|
| youtube-checkbox-approval-pbi-001-lessons-learned.md | Projects/ACTIVE | Projects/COMPLETED-2025-10/youtube-checkbox-approval-pbi-001-lessons-learned.md | Cascade ↔ Thaddius (2025-10-22) | Planned | Completed lessons doc; duplicate of archived iterations |
| youtube-checkbox-approval-pbi-003-status-sync-lessons-learned.md | Projects/ACTIVE | Projects/COMPLETED-2025-10/youtube-checkbox-approval-pbi-003-status-sync-lessons-learned.md | Cascade ↔ Thaddius (2025-10-22) | Planned | Should live with PBI series in completed archive |
| youtube-checkbox-approval-pbi-004-complete-lessons-learned.md | Projects/ACTIVE | Projects/COMPLETED-2025-10/youtube-checkbox-approval-pbi-004-complete-lessons-learned.md | Cascade ↔ Thaddius (2025-10-22) | Planned | Wrap-up already in archive manifest |
| CURRENT-SESSION-STATUS-2025-10-21.md | Projects/ACTIVE | Projects/COMPLETED-2025-10/current-session-status-2025-10-21.md | Cascade ↔ Thaddius (2025-10-22) | Planned | Session log for past day; should join completed session records |
| YOUTUBE-INTEGRATION-MAINTENANCE.md | development/docs | Projects/REFERENCE/youtube-integration-maintenance.md | Cascade ↔ Thaddius (2025-10-22) | Planned | Promote maintenance doc to canonical reference |

### Automation Assets

| Asset | Current Location | Desired Destination | Trigger Type (Event/Schedule) | Monitoring Needs | Notes |
|-------|------------------|---------------------|-------------------------------|------------------|-------|
| audit_design_flaws.sh | .automation/scripts/audit_design_flaws.sh | development/src/automation/tools/audit_design_flaws.sh | Schedule (nightly) | Cron output forwarded to automation dashboards | Drives design smell regression reports before weekly review |
| automated_screenshot_import.sh | .automation/scripts/automated_screenshot_import.sh | development/src/automation/tools/automated_screenshot_import.sh | Event (Samsung OCR completion) | Cron-log + webhook heartbeat | Feeds evening screenshot processor with OCR handoff |
| cleanup_harissa_scripts.py | .automation/scripts/cleanup_harissa_scripts.py | development/src/automation/tools/cleanup_harissa_scripts.py | Schedule (weekly) | Structured logging → monitoring dashboard | Ensures campaign assets remain quarantined from primary knowledge dirs |
| review_queue/fleeting_triage_*.md | .automation/review_queue/ | Projects/REFERENCE/review-queue/automation-reports/ | Event (triage CLI run) | CLI exit codes surfaced via daemon status | Reference copies fuel retrospectives; retain YYYY-MM-DD timestamped reports |

### Inbox Exceptions

| Note | Reason | Action (Promote/Archive) | Status | Follow-up |
|------|--------|--------------------------|--------|-----------|
| *(to fill)* |  |  |  |  |

## Decision Log Template

```yaml
- Item: <file or asset>
  - Source: <current path>
  - Destination: <target path>
  - Rationale: <why the move/cleanup is required>
  - Dependencies: <automation, ai workflow, monitoring>
  - Action Owner: <name/timestamp>
  - Status: planned | in-progress | complete
```

## Immediate Next Steps

1. Draft RED phase test stub at `tests/automation/test_cleanup_inventory.py`
2. Populate top 5 redundant documents in documentation table
3. Outline automation asset moves referencing daemon integration requirements
4. Schedule follow-up to cap Inbox/ count (≤10 items) and log exceptions above
