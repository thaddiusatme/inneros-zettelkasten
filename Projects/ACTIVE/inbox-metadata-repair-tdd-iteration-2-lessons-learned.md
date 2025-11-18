---
type: retrospective
created: 2025-11-16 19:50
status: complete
priority: P0
tags: [tdd, metadata-repair, inbox, lessons-learned]
iteration: 2
project: inbox-metadata-repair-system
---

# TDD Iteration 2 Lessons Learned: Real-Data Fixtures & Auto-Promotion Validation

**Branch**: `feat/inbox-metadata-repair-tdd-iteration-2`  
**Scope**: Model the 8 historically blocked Inbox notes as fixtures, and prove that
`MetadataRepairEngine` + `WorkflowManager.auto_promote_ready_notes()` behave
correctly end-to-end on those real patterns.

---

## What I Implemented

- **Real-data fixtures for the 8 blocked notes**
  - Added `development/tests/fixtures/inbox_metadata_real/` containing broken-state
    `.md` files for:
    - `voice-note-prompts-for-knowledge-capture.md`
    - `Study link between price risk and trust in decision-making.md`
    - `sprint 2 8020.md`
    - `newsletter-generator-prompt.md`
    - `zettelkasten-voice-prompts-v1.md`
    - `Progress-8-26.md`
    - `enhanced-connections-live-data-analysis-report.md`
    - `voice-prompts-quick-reference-card.md`
  - All fixtures intentionally omit `type` and `created`, but preserve realistic
    `quality_score` values from the real-data validation report.

- **New integration suite for real fixtures**
  - File: `development/tests/integration/test_inbox_metadata_repair_real_notes.py`
  - `test_repair_and_auto_promote_real_blocked_notes_end_to_end` asserts that:
    - Before repair:
      - `auto_promote_ready_notes(dry_run=True)` sees 8 candidates.
      - All 8 are skipped with type-related validation errors
        (`error_count == 8`, `skipped_count == 8`, no previews).
    - After `repair_inbox_metadata(execute=True)`:
      - Each note has `type`, `created`, and `status: inbox`.
      - Types match expectations derived from the manifest:
        - `newsletter-generator-prompt.md` → `type: literature`.
        - All other fixtures → `type: fleeting`.
      - `created` is present and matches `YYYY-MM-DD HH:MM`.
      - A second repair run is idempotent (`repairs_made == 0`).
    - Auto-promotion dry-run after repair:
      - `total_candidates == 8`, `error_count == 0`, `skipped_count == 0`.
      - `would_promote_count == 8` and `preview` entries show the expected
        `type`, `target` directory, and `quality` per note.

- **Status**
  - `pytest development/tests/integration/test_inbox_metadata_repair_real_notes.py -v` → **2/2 tests passing**.
  - No additional changes were required to `MetadataRepairEngine` or
    `PromotionEngine`; Iteration 2 is primarily a **validation & coverage**
    iteration using real data.

---

## What Worked Well

- **Real fixtures gave high confidence**: Encoding the exact filenames and
  quality scores from the manifest made it clear that the existing repair logic
  already handles the real-world blocked notes, not just synthetic examples.
- **Tight assertions without over-coupling**:
  - Tests assert concrete expectations (types, preview targets, timestamp
    format) without duplicating engine internals.
  - Newsletter prompts are validated as `literature`, while the remaining notes
    are treated as `fleeting`, matching actual auto-promotion behavior.
- **Zero production changes for this iteration**:
  - Iteration 1’s implementation was strong enough that Iteration 2 could focus
    on fixtures and integration tests only, keeping the GREEN phase trivial.

---

## Things to Watch / Next Iterations

- **Mismatched type vs directory**
  - The current repair flow fixes missing fields but does not yet address cases
    where `type` disagrees with the current directory location. That belongs in
    a future normalization pass.
- **Broader edge cases**
  - The 8 fixtures cover the original high-impact failures, but there may be
    additional edge patterns in the vault (e.g., unusual imports, partial
    frontmatter) that deserve targeted tests.
- **CLI ergonomics**
  - The next iteration could add a user-facing `--repair-metadata` CLI path
    that surfaces the same stats used in these tests (notes scanned, repairs
    made, previews vs execute) in a human-friendly report.

---

## Summary

Iteration 2 closes the loop on the original problem statement for #25 by
proving that inbox metadata repair and auto-promotion are **boringly reliable**
for the exact 8 historically blocked notes. The system now has:

- Synthetic integration tests for core behavior (Iteration 1), and
- Real-data integration tests for the original 8 failures (Iteration 2).

Future work on #25 can focus on deeper normalization and CLI UX rather than
basic correctness for the known blocked cases.
