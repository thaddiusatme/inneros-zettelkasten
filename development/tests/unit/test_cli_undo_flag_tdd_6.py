import sys


def test_cli_undo_flag_triggers_undo(monkeypatch, capsys):
    # Import CLI module
    from src.cli import connections_demo

    # Seed undo manager with a fake operation
    connections_demo._UNDO_MANAGER.record_insertion(
        {
            "target_file": "some.md",
            "insertions": [{"text": "[[X]]", "section": "end"}],
            "backup_path": "/tmp/some.md.bak",
        }
    )

    # Auto-confirm undo
    monkeypatch.setattr("builtins.input", lambda prompt="": "y")

    # Simulate CLI invocation
    monkeypatch.setattr(sys, "argv", ["prog", "suggest-links", "any.md", ".", "--undo"])

    result = connections_demo.main()

    # Validate behavior
    out = capsys.readouterr().out
    assert "Undo last link insertion" in out
    assert isinstance(result, dict)
    assert result.get("success") is True
    assert result.get("backup_path") == "/tmp/some.md.bak"
