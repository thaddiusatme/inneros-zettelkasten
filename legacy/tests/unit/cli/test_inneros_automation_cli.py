"""TDD RED Phase tests for inneros automation helper CLI.

These tests define the expected behavior of a thin helper entrypoint that
routes high-level automation commands to dedicated CLIs:

- daemon start|stop|status -> src.cli.daemon_cli (via python -m)
- ai inbox-sweep           -> src.cli.inneros_ai_inbox_sweep_cli
- ai repair-metadata       -> src.cli.inneros_ai_repair_metadata_cli

The helper is expected to:
- Parse top-level subcommands (daemon/ai and their subcommands).
- Invoke the appropriate Python module via subprocess.run([...]).
- Forward key arguments like --repo-root, --execute, --format.
- Propagate the underlying process exit code.
"""

from typing import List

import pytest

pytestmark = pytest.mark.ci


class DummyResult:
    """Simple stand-in object for subprocess.run return value.

    We only care about the `returncode` attribute for exit code propagation.
    """

    def __init__(self, returncode: int) -> None:
        self.returncode = returncode


@pytest.mark.parametrize("subcommand", ["start", "stop", "status"])
def test_daemon_commands_route_to_daemon_cli_and_propagate_exit_code(
    subcommand: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """daemon <subcommand> should call python -m src.cli.daemon_cli and
    propagate its exit code.
    """

    from src.cli import inneros_automation_cli as helper

    captured_args: List[str] = []

    def fake_run(cmd, check: bool = False):  # type: ignore[no-untyped-def]
        nonlocal captured_args
        captured_args = list(cmd)
        # Simulate distinct non-zero exit for status to prove propagation
        code = 0 if subcommand in {"start", "stop"} else 5
        return DummyResult(returncode=code)

    monkeypatch.setattr(helper, "subprocess", pytest.importorskip("subprocess"))
    monkeypatch.setattr(helper.subprocess, "run", fake_run, raising=True)

    exit_code = helper.main(["daemon", subcommand])

    # Command prefix must target the daemon CLI module
    assert captured_args[:3] == ["python3", "-m", "src.cli.daemon_cli"]
    # Subcommand should be forwarded as-is
    assert captured_args[3:] == [subcommand]

    # Exit code must match the underlying result
    expected_exit = 0 if subcommand in {"start", "stop"} else 5
    assert exit_code == expected_exit


def test_ai_inbox_sweep_routes_to_inbox_sweep_cli_with_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ai inbox-sweep should route to inneros_ai_inbox_sweep_cli with
    --repo-root and --format forwarded, and propagate exit code.
    """

    from src.cli import inneros_automation_cli as helper

    captured_args: List[str] = []

    def fake_run(cmd, check: bool = False):  # type: ignore[no-untyped-def]
        nonlocal captured_args
        captured_args = list(cmd)
        return DummyResult(returncode=0)

    monkeypatch.setattr(helper, "subprocess", pytest.importorskip("subprocess"))
    monkeypatch.setattr(helper.subprocess, "run", fake_run, raising=True)

    repo_root = "/tmp/example-repo"
    exit_code = helper.main(
        ["ai", "inbox-sweep", "--repo-root", repo_root, "--format", "json"]
    )

    # Should execute the dedicated inbox sweep CLI via python -m
    assert captured_args[:3] == [
        "python3",
        "-m",
        "src.cli.inneros_ai_inbox_sweep_cli",
    ]

    # --repo-root should be forwarded with its value
    assert "--repo-root" in captured_args
    repo_index = captured_args.index("--repo-root")
    assert captured_args[repo_index + 1] == repo_root

    # --format should be forwarded with its value
    assert "--format" in captured_args
    fmt_index = captured_args.index("--format")
    assert captured_args[fmt_index + 1] == "json"

    # Exit code should be passed through
    assert exit_code == 0


def test_ai_repair_metadata_routes_and_forwards_execute_and_format(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ai repair-metadata should route to inneros_ai_repair_metadata_cli and
    forward --repo-root, --execute, and --format flags, propagating exit code.
    """

    from src.cli import inneros_automation_cli as helper

    captured_args: List[str] = []

    def fake_run(cmd, check: bool = False):  # type: ignore[no-untyped-def]
        nonlocal captured_args
        captured_args = list(cmd)
        return DummyResult(returncode=3)

    monkeypatch.setattr(helper, "subprocess", pytest.importorskip("subprocess"))
    monkeypatch.setattr(helper.subprocess, "run", fake_run, raising=True)

    repo_root = "/tmp/repair-repo"
    exit_code = helper.main(
        [
            "ai",
            "repair-metadata",
            "--repo-root",
            repo_root,
            "--execute",
            "--format",
            "text",
        ]
    )

    # Should execute the dedicated metadata repair CLI via python -m
    assert captured_args[:3] == [
        "python3",
        "-m",
        "src.cli.inneros_ai_repair_metadata_cli",
    ]

    # --repo-root should be forwarded with its value
    assert "--repo-root" in captured_args
    repo_index = captured_args.index("--repo-root")
    assert captured_args[repo_index + 1] == repo_root

    # --execute should be present as a flag
    assert "--execute" in captured_args

    # --format should be forwarded with its value
    assert "--format" in captured_args
    fmt_index = captured_args.index("--format")
    assert captured_args[fmt_index + 1] == "text"

    # Non-zero exit code from underlying CLI must be propagated
    assert exit_code == 3


def test_unknown_top_level_command_returns_non_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unknown top-level commands should not attempt to call subprocess and
    should return a non-zero exit code.
    """

    from src.cli import inneros_automation_cli as helper

    # Guardrail: if this ever starts calling subprocess for unknown commands,
    # this test will fail and force an explicit decision.
    monkeypatch.setattr(
        helper, "subprocess", pytest.importorskip("subprocess"), raising=True
    )

    exit_code = helper.main(["unknown-command"])  # type: ignore[arg-type]

    assert exit_code != 0
