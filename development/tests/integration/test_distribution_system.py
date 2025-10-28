"""
TDD RED PHASE: Distribution System Tests

Tests for the distribution creation pipeline and security audit.
All tests should FAIL initially until implementation is complete.

Test Strategy:
1. Distribution script removes all personal content
2. Distribution script injects sample content
3. Distribution script validates tests pass
4. Security audit detects personal information
5. Security audit detects secrets
6. Security audit generates reports
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import pytest
import json


@pytest.mark.integration
@pytest.mark.fast_integration
class TestDistributionCreation:
    """Tests for create-distribution.sh script.

    Performance: Fast (uses tmp_path, filesystem operations)
    """

    @pytest.fixture
    def temp_source_repo(self):
        """Create a temporary source repository with test content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source"
            source_dir.mkdir()

            # Create personal content directories (should be removed)
            (source_dir / "knowledge" / "Inbox").mkdir(parents=True)
            (source_dir / "knowledge" / "Inbox" / "personal-note.md").write_text(
                "---\ntitle: My Personal Note\n---\nSensitive info"
            )
            (source_dir / "Reviews").mkdir()
            (source_dir / "Reviews" / "daily-2025-10-09.md").write_text(
                "Personal review"
            )
            (source_dir / "Media").mkdir()
            (source_dir / "Media" / "photo.jpg").write_text("binary")
            (source_dir / "backups").mkdir()
            (source_dir / ".automation" / "logs").mkdir(parents=True)
            (source_dir / ".automation" / "logs" / "process.log").write_text("logs")

            # Create development content (should be preserved)
            (source_dir / "development").mkdir()
            (source_dir / "development" / "src").mkdir()
            (source_dir / "development" / "tests").mkdir()
            (source_dir / "requirements.txt").write_text("pytest==7.4.0")
            (source_dir / "README.md").write_text("# InnerOS")

            # Create .gitignore
            (source_dir / ".gitignore").write_text("*.pyc\n__pycache__/")

            # Copy actual scripts from repository root
            repo_root = Path(__file__).parent.parent.parent.parent
            scripts_dir = source_dir / "scripts"
            scripts_dir.mkdir()

            # Copy security-audit.py and create-distribution.sh
            if (repo_root / "scripts" / "security-audit.py").exists():
                shutil.copy(repo_root / "scripts" / "security-audit.py", scripts_dir)
            if (repo_root / "scripts" / "create-distribution.sh").exists():
                shutil.copy(
                    repo_root / "scripts" / "create-distribution.sh", scripts_dir
                )

            yield source_dir

    def test_distribution_script_exists(self):
        """Test that create-distribution.sh exists and is executable"""
        script_path = Path("scripts/create-distribution.sh")
        assert script_path.exists(), "Distribution script does not exist"
        assert os.access(script_path, os.X_OK), "Distribution script is not executable"

    def test_removes_personal_content_directories(self, temp_source_repo):
        """Test that personal directories are completely removed"""
        # This will fail until implementation exists
        result = subprocess.run(
            ["bash", "scripts/create-distribution.sh", str(temp_source_repo)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Check personal directories are removed
        dist_dir = temp_source_repo.parent / "inneros-distribution"
        assert not (dist_dir / "knowledge" / "Inbox").exists()
        assert not (dist_dir / "Reviews").exists()
        assert not (dist_dir / "Media").exists()
        assert not (dist_dir / "backups").exists()
        assert not (dist_dir / ".automation" / "logs").exists()

    def test_preserves_development_content(self, temp_source_repo):
        """Test that development directories and files are preserved"""
        result = subprocess.run(
            ["bash", "scripts/create-distribution.sh", str(temp_source_repo)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Check development content is preserved
        dist_dir = temp_source_repo.parent / "inneros-distribution"
        assert (dist_dir / "development").exists()
        assert (dist_dir / "development" / "src").exists()
        assert (dist_dir / "development" / "tests").exists()
        assert (dist_dir / "requirements.txt").exists()
        assert (dist_dir / "README.md").exists()

    def test_injects_sample_knowledge_pack(self, temp_source_repo):
        """Test that sample knowledge pack is injected"""
        # Create sample pack in source
        sample_dir = temp_source_repo / "knowledge-starter-pack"
        sample_dir.mkdir()
        (sample_dir / "example-permanent.md").write_text("# Example Permanent Note")

        result = subprocess.run(
            ["bash", "scripts/create-distribution.sh", str(temp_source_repo)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Check sample content exists in distribution
        dist_dir = temp_source_repo.parent / "inneros-distribution"
        assert (dist_dir / "knowledge-starter-pack").exists()
        assert (dist_dir / "knowledge-starter-pack" / "example-permanent.md").exists()

    def test_swaps_gitignore_to_distribution_version(self, temp_source_repo):
        """Test that .gitignore is swapped to distribution version"""
        # Create distribution gitignore
        (temp_source_repo / ".gitignore-distribution").write_text(
            "knowledge/\nReviews/\nMedia/\n*.pyc"
        )

        result = subprocess.run(
            ["bash", "scripts/create-distribution.sh", str(temp_source_repo)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Check .gitignore is swapped
        dist_dir = temp_source_repo.parent / "inneros-distribution"
        gitignore_content = (dist_dir / ".gitignore").read_text()
        assert "knowledge/" in gitignore_content
        assert "Reviews/" in gitignore_content

    def test_runs_security_audit(self, temp_source_repo):
        """Test that security audit is executed"""
        result = subprocess.run(
            ["bash", "scripts/create-distribution.sh", str(temp_source_repo)],
            capture_output=True,
            text=True,
        )

        # Script should call security audit
        assert "Security audit" in result.stdout or "security-audit.py" in result.stdout

    def test_validates_tests_pass(self, temp_source_repo):
        """Test that pytest validation runs in distribution"""
        # Create a simple test file
        test_dir = temp_source_repo / "development" / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "test_sample.py").write_text(
            "def test_always_passes():\n    assert True"
        )

        result = subprocess.run(
            ["bash", "scripts/create-distribution.sh", str(temp_source_repo)],
            capture_output=True,
            text=True,
        )

        # Should mention test validation
        assert "test" in result.stdout.lower() or "pytest" in result.stdout.lower()

    def test_creates_distribution_in_correct_location(self, temp_source_repo):
        """Test that distribution is created in ../inneros-distribution"""
        result = subprocess.run(
            ["bash", "scripts/create-distribution.sh", str(temp_source_repo)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        dist_dir = temp_source_repo.parent / "inneros-distribution"
        assert dist_dir.exists()
        assert dist_dir.is_dir()


class TestSecurityAudit:
    """Tests for security-audit.py script"""

    @pytest.fixture
    def temp_audit_dir(self):
        """Create temporary directory for audit testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_dir = Path(tmpdir)
            yield audit_dir

    def test_security_audit_script_exists(self):
        """Test that security-audit.py exists and is executable"""
        script_path = Path("scripts/security-audit.py")
        assert script_path.exists(), "Security audit script does not exist"
        # Python scripts don't need execute permission if called with python

    def test_detects_personal_name_patterns(self, temp_audit_dir):
        """Test that audit detects personal names"""
        # Create file with personal information
        test_file = temp_audit_dir / "test.md"
        test_file.write_text("This note was created by Thaddius")

        result = subprocess.run(
            ["python3", "scripts/security-audit.py", str(temp_audit_dir)],
            capture_output=True,
            text=True,
        )

        # Should detect personal name
        assert result.returncode != 0, "Should fail on personal information"
        assert (
            "thaddius" in result.stdout.lower() or "personal" in result.stdout.lower()
        )

    def test_detects_username_patterns(self, temp_audit_dir):
        """Test that audit detects usernames"""
        test_file = temp_audit_dir / "config.py"
        test_file.write_text("USER = 'thaddiusatme'")

        result = subprocess.run(
            ["python3", "scripts/security-audit.py", str(temp_audit_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert (
            "username" in result.stdout.lower()
            or "thaddiusatme" in result.stdout.lower()
        )

    def test_detects_api_key_patterns(self, temp_audit_dir):
        """Test that audit detects API keys"""
        test_file = temp_audit_dir / ".env"
        test_file.write_text("API_KEY=sk-1234567890abcdef")

        result = subprocess.run(
            ["python3", "scripts/security-audit.py", str(temp_audit_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "api_key" in result.stdout.lower() or "secret" in result.stdout.lower()

    def test_detects_password_patterns(self, temp_audit_dir):
        """Test that audit detects passwords"""
        test_file = temp_audit_dir / "config.json"
        test_file.write_text('{"PASSWORD": "supersecret123"}')

        result = subprocess.run(
            ["python3", "scripts/security-audit.py", str(temp_audit_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "password" in result.stdout.lower()

    def test_detects_token_patterns(self, temp_audit_dir):
        """Test that audit detects tokens"""
        test_file = temp_audit_dir / "auth.py"
        test_file.write_text("TOKEN = 'ghp_1234567890abcdefghij'")

        result = subprocess.run(
            ["python3", "scripts/security-audit.py", str(temp_audit_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "token" in result.stdout.lower()

    def test_passes_clean_directory(self, temp_audit_dir):
        """Test that audit passes for clean content"""
        # Create safe files
        (temp_audit_dir / "README.md").write_text("# InnerOS\n\nA knowledge system")
        (temp_audit_dir / "src").mkdir()
        (temp_audit_dir / "src" / "main.py").write_text("def main():\n    pass")

        result = subprocess.run(
            ["python3", "scripts/security-audit.py", str(temp_audit_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, "Clean content should pass audit"
        assert "pass" in result.stdout.lower() or "clean" in result.stdout.lower()

    def test_generates_audit_report(self, temp_audit_dir):
        """Test that audit generates detailed report"""
        # Create file with violation
        test_file = temp_audit_dir / "test.md"
        test_file.write_text("API_KEY=secret123")

        result = subprocess.run(
            ["python3", "scripts/security-audit.py", str(temp_audit_dir)],
            capture_output=True,
            text=True,
        )

        # Should generate report with file path and violation type
        assert "test.md" in result.stdout or str(test_file) in result.stdout
        assert "violation" in result.stdout.lower() or "found" in result.stdout.lower()

    def test_exits_with_error_code_on_violations(self, temp_audit_dir):
        """Test that audit exits with error code when violations found"""
        test_file = temp_audit_dir / "bad.py"
        test_file.write_text("PASSWORD='secret'")

        result = subprocess.run(
            ["python3", "scripts/security-audit.py", str(temp_audit_dir)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1, "Should exit with code 1 on violations"

    def test_json_output_format(self, temp_audit_dir):
        """Test that audit can output JSON format"""
        test_file = temp_audit_dir / "test.md"
        test_file.write_text("TOKEN=abc123")

        result = subprocess.run(
            [
                "python3",
                "scripts/security-audit.py",
                str(temp_audit_dir),
                "--format=json",
            ],
            capture_output=True,
            text=True,
        )

        # Should be valid JSON
        try:
            data = json.loads(result.stdout)
            assert "violations" in data or "results" in data
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


class TestDistributionIntegration:
    """Integration tests for complete distribution workflow"""

    @pytest.fixture
    def real_distribution(self):
        """Create a real distribution from current repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            dist_dir = Path(tmpdir) / "inneros-distribution"

            # Get repository root
            repo_root = Path(__file__).parent.parent.parent.parent

            # Run distribution script
            result = subprocess.run(
                ["bash", str(repo_root / "scripts" / "create-distribution.sh")],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=60,  # 1 minute timeout
            )

            # Move distribution to temp directory for testing
            actual_dist = repo_root.parent / "inneros-distribution"
            if actual_dist.exists():
                shutil.copytree(actual_dist, dist_dir)
                yield dist_dir
                # Cleanup - remove the actual distribution created
                shutil.rmtree(actual_dist, ignore_errors=True)
            else:
                pytest.fail(
                    f"Distribution not created. Script output: {result.stdout}\nErrors: {result.stderr}"
                )

    def test_end_to_end_distribution_creation(self, real_distribution):
        """Test complete workflow from source to distribution"""
        # Verify distribution structure
        assert real_distribution.exists(), "Distribution directory should exist"
        assert (
            real_distribution / "development"
        ).exists(), "Development directory missing"
        assert (real_distribution / "scripts").exists(), "Scripts directory missing"
        assert (real_distribution / "README.md").exists(), "README.md missing"
        assert (
            real_distribution / "requirements.txt"
        ).exists(), "requirements.txt missing"

        # Verify personal content removed
        assert not (
            real_distribution / "knowledge" / "Inbox"
        ).exists(), "Personal Inbox should be removed"
        assert not (real_distribution / "Reviews").exists(), "Reviews should be removed"
        assert not (real_distribution / "Media").exists(), "Media should be removed"

        # Verify starter pack included
        assert (
            real_distribution / "knowledge-starter-pack"
        ).exists(), "Starter pack missing"
        starter_files = list(
            (real_distribution / "knowledge-starter-pack").glob("*.md")
        )
        assert len(starter_files) > 0, "Starter pack should contain markdown files"

    def test_distribution_tests_pass(self, real_distribution):
        """Test that created distribution passes its own tests

        TDD Iteration 2 optimization: Excludes TDD iteration test files
        to prevent timeout. Target: <120 seconds for test suite completion.
        """
        # Run pytest in distribution directory with optimized timeout
        result = subprocess.run(
            [
                "python3",
                "-m",
                "pytest",
                "development/tests/unit",
                "-v",
                "--tb=short",
                "-x",
            ],
            cwd=real_distribution,
            capture_output=True,
            text=True,
            timeout=120,  # Reduced from 300s after TDD file exclusion
        )

        # Tests should pass or at least be discoverable
        # Exit code 0 = tests passed
        # Exit code 5 = no tests collected (acceptable if distribution has minimal tests)
        assert result.returncode in [
            0,
            5,
        ], f"Tests failed in distribution: {result.stdout}\n{result.stderr}"

    def test_distribution_size_reasonable(self, real_distribution):
        """Test that distribution size is reasonable (no bloat)"""
        # Calculate directory size
        total_size = 0
        file_count = 0

        for dirpath, dirnames, filenames in os.walk(real_distribution):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                try:
                    total_size += filepath.stat().st_size
                    file_count += 1
                except OSError:
                    pass  # Skip files we can't read

        # Convert to MB
        size_mb = total_size / (1024 * 1024)

        # Report size
        print(f"\nDistribution size: {size_mb:.2f} MB ({file_count} files)")

        # Assert reasonable size (< 50MB for clean distribution)
        assert (
            size_mb < 50
        ), f"Distribution too large: {size_mb:.2f} MB (should be < 50 MB)"

        # Also check that it's not suspiciously small (should have at least some content)
        assert size_mb > 0.1, f"Distribution suspiciously small: {size_mb:.2f} MB"
