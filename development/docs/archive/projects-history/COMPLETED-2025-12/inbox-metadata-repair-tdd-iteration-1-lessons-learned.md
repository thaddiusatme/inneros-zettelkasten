---
type: retrospective
created: 2025-11-16 17:58
status: complete
priority: P0
tags: [tdd, metadata-repair, inbox, lessons-learned]
iteration: 1
project: inbox-metadata-repair-system
---

# TDD Iteration 1 Lessons Learned: Inbox Status Normalization

**Branch**: `feat/inbox-metadata-repair-tdd-iteration-1`  
**Scope**: Normalize `status` for inbox metadata repair and prove integration with auto-promotion.

---

## What I Implemented

- Added `TestInboxMetadataRepairIntegration`:
  - Broken inbox notes with only `quality_score` now gain:
    - `type` (inferred from filename/content)
    - `created` (timestamp)
    - `status: inbox`
  - Second repair run is idempotent (`repairs_made == 0`).
  - Valid notes with complete metadata are unchanged byte-for-byte.
  - Dry-run mode previews repairs without touching disk.
  - Auto-promotion dry-run is blocked before repair (missing `type`) and clean after repair (`error_count == 0`, `would_promote_count == 2`).

- Extended `MetadataRepairEngine`:
  - `detect_missing_metadata` now treats `status` as required alongside `type` and `created`.
  - `repair_note_metadata` adds `status: "inbox"` only when missing.
  - Existing frontmatter fields (including any existing `status`) are preserved.

---

## What Worked Well

- **TDD layering**: Instead of overloading the low-level engine tests, I added a small, high-leverage integration suite that encodes P0 behavior (status normalization + auto-promote unblock) from the `WorkflowManager` side.
- **Minimal GREEN change**: A tiny change to detection/repair (`status` in and out) was enough to flip the new suite from RED to GREEN.
- **Safety preserved**:
  - Dry-run behavior stayed intact.
  - Existing metadata is never overwritten.
  - Idempotence is enforced via both stats and content checks.

---

## Things to Watch / Next Iterations

- There is an older RED-phase test file (`test_metadata_repair_engine.py`) still wired to `from development.src...`; fixing that import is a separate cleanup iteration and not part of this focused change.
- Future iterations can:
  - Add more “broken → repaired” mappings (e.g., mismatched `type` vs directory) as new tests, then extend the engine minimally.
  - Tighten type inference rules using real-data examples from the 8 historical blocked notes.

---

## Summary

This iteration established a concrete contract for inbox metadata repair at the `WorkflowManager` level (status, type, created, idempotence, auto-promotion-ready) and implemented the smallest engine change needed to satisfy it, keeping ADR-002 boundaries intact.
