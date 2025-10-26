from pathlib import Path

import pytest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.ai.workflow_manager import WorkflowManager


def test_workflow_manager_uses_default_path(monkeypatch, tmp_path):
    # create dummy vault structure
    vault_dir = tmp_path / "vault"
    for d in ["Inbox", "Fleeting Notes", "Permanent Notes"]:
        (vault_dir / d).mkdir(parents=True)

    monkeypatch.setenv("INNEROS_VAULT_PATH", str(vault_dir))

    # should not raise
    wm = WorkflowManager()
    assert wm.base_dir == vault_dir.resolve()


def test_workflow_manager_raises_when_no_path(monkeypatch):
    monkeypatch.delenv("INNEROS_VAULT_PATH", raising=False)
    with pytest.raises(ValueError):
        WorkflowManager()
