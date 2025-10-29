# RED PHASE: Define expected interface for UndoManager to drive implementation
# Location to implement: ai/link_insertion_engine.py (or new ai/undo_manager.py and re-export)
# Expected methods: __init__(max_history:int=50), record_insertion(dict), undo_last(restore: bool=True)->dict,
# history_size()->int, can_undo()->bool


def test_undo_manager_records_operations(tmp_path):
    from src.ai.link_insertion_engine import (
        UndoManager,
    )  # implemented minimal in Iteration 6

    um = UndoManager(max_history=10)

    backup1 = tmp_path / "note1.md.bak"
    backup2 = tmp_path / "note2.md.bak"

    op1 = {
        "target_file": "note1.md",
        "insertions": [{"text": "[[Link 1]]", "section": "test", "offset": 123}],
        "backup_path": str(backup1),
        "timestamp": "2025-09-25 13:20",
    }
    op2 = {
        "target_file": "note2.md",
        "insertions": [{"text": "[[Link 2]]", "section": "test", "offset": 456}],
        "backup_path": str(backup2),
        "timestamp": "2025-09-25 13:21",
    }

    um.record_insertion(op1)
    um.record_insertion(op2)

    # Expect two operations recorded
    assert um.history_size() == 2
    assert um.can_undo() is True


def test_undo_last_returns_latest_operation(tmp_path):
    from src.ai.link_insertion_engine import (
        UndoManager,
    )  # implemented minimal in Iteration 6

    um = UndoManager(max_history=10)

    opA = {
        "target_file": "a.md",
        "insertions": [{"text": "[[A]]", "section": "alpha", "offset": 10}],
        "backup_path": str(tmp_path / "a.md.bak"),
        "timestamp": "2025-09-25 13:20",
    }
    opB = {
        "target_file": "b.md",
        "insertions": [{"text": "[[B]]", "section": "beta", "offset": 20}],
        "backup_path": str(tmp_path / "b.md.bak"),
        "timestamp": "2025-09-25 13:21",
    }

    um.record_insertion(opA)
    um.record_insertion(opB)

    result = um.undo_last(restore=False)  # no real file restore in unit test

    # Expect the last operation to be undone first (LIFO)
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert result.get("target_file") == "b.md"
    assert um.history_size() == 1


def test_undo_when_empty_is_graceful():
    from src.ai.link_insertion_engine import (
        UndoManager,
    )  # implemented minimal in Iteration 6

    um = UndoManager()
    result = um.undo_last(restore=False)

    assert isinstance(result, dict)
    assert result.get("success") is False
    assert "no operations to undo" in result.get("message", "").lower()
