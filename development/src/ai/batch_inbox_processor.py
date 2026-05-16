# Compatibility shim — batch_inbox_processor functions now live in batch.py
from .batch import (
    is_note_eligible_for_processing,
    scan_eligible_notes,
    process_single_note,
    batch_process_unprocessed_inbox,
)

__all__ = [
    "is_note_eligible_for_processing",
    "scan_eligible_notes",
    "process_single_note",
    "batch_process_unprocessed_inbox",
]
