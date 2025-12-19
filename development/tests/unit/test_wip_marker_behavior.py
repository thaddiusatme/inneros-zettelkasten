import subprocess
import sys
from pathlib import Path
import textwrap


def test_pytest_default_excludes_wip(tmp_path):
    development_root = Path(__file__).resolve().parents[2]
    test_file = tmp_path / "test_tmp_wip.py"
    test_file.write_text(
        textwrap.dedent(
            """\
            import pytest


            def test_passes():
                assert True


            @pytest.mark.wip
            def test_wip_fails():
                assert False
            """
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-c",
            "pytest.ini",
            "--rootdir",
            ".",
            str(test_file),
        ],
        cwd=development_root,
        capture_output=True,
        text=True,
        timeout=60,
    )

    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, combined
    assert "deselected" in combined


def test_pytest_addopts_override_includes_wip(tmp_path):
    development_root = Path(__file__).resolve().parents[2]
    test_file = tmp_path / "test_tmp_wip.py"
    test_file.write_text(
        textwrap.dedent(
            """\
            import pytest


            def test_passes():
                assert True


            @pytest.mark.wip
            def test_wip_fails():
                assert False
            """
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-c",
            "pytest.ini",
            "--rootdir",
            ".",
            "-o",
            "addopts=",
            str(test_file),
        ],
        cwd=development_root,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode != 0
