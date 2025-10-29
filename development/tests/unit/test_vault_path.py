import tempfile
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.utils.vault_path import get_default_vault_path


def test_env_var_resolution(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("INNEROS_VAULT_PATH", tmpdir)
        assert get_default_vault_path() == Path(tmpdir).resolve()


def test_yaml_config_resolution(tmp_path, monkeypatch):
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    config_file = tmp_path / ".inneros.yaml"
    config_file.write_text('vault_path: "{}"\n'.format(vault_dir))

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INNEROS_VAULT_PATH", raising=False)

    assert get_default_vault_path() == vault_dir.resolve()


def test_home_config_resolution(tmp_path, monkeypatch):
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    config_file = tmp_path / ".inneros.json"
    config_file.write_text('{"vault_path": "%s"}' % vault_dir)

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("INNEROS_VAULT_PATH", raising=False)

    # ensure we are not in tmp_path so only HOME config is considered
    with tempfile.TemporaryDirectory() as other:
        monkeypatch.chdir(other)
        assert get_default_vault_path() == vault_dir.resolve()


def test_no_resolution(monkeypatch):
    monkeypatch.delenv("INNEROS_VAULT_PATH", raising=False)
    with tempfile.TemporaryDirectory() as cwd:
        monkeypatch.chdir(cwd)
        assert get_default_vault_path() is None
