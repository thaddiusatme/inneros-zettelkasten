"""
Tests for CI Pipeline Integration - CLI Pattern Linter in GitHub Actions

RED Phase: These tests validate that a GitHub Actions workflow exists to run
the CLI pattern linter on all PRs, providing automated compliance checking
at the CI level.

The workflow should:
1. Run on pull requests and pushes to main/develop
2. Run linter on all CLI files (--all flag)
3. Use JSON output for structured reporting
4. Fail build if violations found (--fail-on-violations)
5. Provide clear status in PR checks

Test Strategy:
- Validate workflow file exists
- Check workflow syntax and structure
- Verify linter invocation is correct
- Validate trigger conditions
- Check job configuration

These tests will FAIL until the CI workflow is implemented.
"""

import yaml
from pathlib import Path
from typing import Dict, Any

import pytest

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[4]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"


class TestCIWorkflowFile:
    """Test CLI linter workflow file exists and has correct structure."""

    WORKFLOW_FILE = "cli-pattern-linter.yml"

    def test_workflow_file_exists(self):
        """RED: CLI linter workflow file should exist.
        
        File should be at: .github/workflows/cli-pattern-linter.yml
        
        This test will FAIL until workflow file is created.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        assert workflow_path.exists(), (
            f"Workflow file should exist at {workflow_path}"
        )
        
        # Should be YAML format
        assert workflow_path.suffix == '.yml', (
            "Workflow file should have .yml extension"
        )

    def test_workflow_file_valid_yaml(self):
        """RED: Workflow file should be valid YAML.
        
        Must parse without errors and contain required GitHub Actions keys.
        
        This test will FAIL until valid YAML structure is created.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        # Parse YAML
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        assert workflow is not None, "Workflow file should contain valid YAML"
        assert isinstance(workflow, dict), "Workflow should be a YAML dictionary"

    def test_workflow_has_name(self):
        """RED: Workflow should have descriptive name.
        
        Name should clearly indicate it's for CLI pattern linting.
        
        This test will FAIL until workflow name is set.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        assert 'name' in workflow, "Workflow should have a name"
        
        name = workflow['name'].lower()
        assert 'cli' in name and ('lint' in name or 'pattern' in name), (
            "Workflow name should mention CLI and linting/patterns"
        )


class TestCIWorkflowTriggers:
    """Test workflow triggers are configured correctly."""

    WORKFLOW_FILE = "cli-pattern-linter.yml"

    def test_workflow_triggers_on_pull_request(self):
        """RED: Workflow should trigger on pull requests.
        
        Should run on PRs to main and develop branches.
        
        This test will FAIL until PR trigger is configured.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        # Note: YAML parsers may convert 'on:' to boolean True
        # Check for both 'on' and True as keys
        triggers_key = 'on' if 'on' in workflow else (True if True in workflow else None)
        assert triggers_key is not None, "Workflow should have 'on' trigger section"
        
        triggers = workflow[triggers_key]
        assert 'pull_request' in triggers, "Workflow should trigger on pull_request"
        
        # Check branch targeting
        pr_config = triggers['pull_request']
        if isinstance(pr_config, dict) and 'branches' in pr_config:
            branches = pr_config['branches']
            assert 'main' in branches or 'develop' in branches, (
                "PR trigger should include main or develop branches"
            )

    def test_workflow_triggers_on_push(self):
        """RED: Workflow should trigger on pushes to main branches.
        
        Should run on direct pushes to main/develop.
        
        This test will FAIL until push trigger is configured.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        # Note: YAML parsers may convert 'on:' to boolean True
        triggers_key = 'on' if 'on' in workflow else (True if True in workflow else None)
        triggers = workflow.get(triggers_key, {}) if triggers_key else {}
        assert 'push' in triggers, "Workflow should trigger on push"
        
        # Check branch targeting
        push_config = triggers['push']
        if isinstance(push_config, dict) and 'branches' in push_config:
            branches = push_config['branches']
            assert 'main' in branches or 'develop' in branches, (
                "Push trigger should include main or develop branches"
            )

    def test_workflow_allows_manual_trigger(self):
        """RED: Workflow should support manual triggering.
        
        workflow_dispatch allows running workflow manually from GitHub UI.
        
        This test will FAIL until workflow_dispatch is configured.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        # Note: YAML parsers may convert 'on:' to boolean True
        triggers_key = 'on' if 'on' in workflow else (True if True in workflow else None)
        triggers = workflow.get(triggers_key, {}) if triggers_key else {}
        assert 'workflow_dispatch' in triggers, (
            "Workflow should support workflow_dispatch for manual triggering"
        )


class TestCIWorkflowJobs:
    """Test workflow jobs configuration."""

    WORKFLOW_FILE = "cli-pattern-linter.yml"

    def test_workflow_has_linter_job(self):
        """RED: Workflow should have a job for linting.
        
        Job should be named clearly (e.g., 'lint-cli-patterns').
        
        This test will FAIL until job is defined.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        assert 'jobs' in workflow, "Workflow should have jobs section"
        
        jobs = workflow['jobs']
        assert isinstance(jobs, dict), "Jobs should be a dictionary"
        assert len(jobs) > 0, "Workflow should have at least one job"
        
        # Check if any job has CLI linting related name
        job_names = list(jobs.keys())
        has_lint_job = any('lint' in name.lower() or 'cli' in name.lower() 
                          for name in job_names)
        assert has_lint_job, "Should have a job for CLI linting"

    def test_linter_job_runs_on_ubuntu(self):
        """RED: Linter job should run on Ubuntu.
        
        Ubuntu is standard for Python CI jobs.
        
        This test will FAIL until runs-on is configured.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get('jobs', {})
        # Get first job (assuming single job workflow)
        job = list(jobs.values())[0] if jobs else {}
        
        assert 'runs-on' in job, "Job should specify runs-on"
        assert 'ubuntu' in job['runs-on'], "Job should run on Ubuntu"

    def test_linter_job_has_timeout(self):
        """RED: Linter job should have reasonable timeout.
        
        Prevents hanging jobs from consuming CI resources.
        
        This test will FAIL until timeout is set.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get('jobs', {})
        job = list(jobs.values())[0] if jobs else {}
        
        assert 'timeout-minutes' in job, "Job should have timeout-minutes"
        
        timeout = job['timeout-minutes']
        assert isinstance(timeout, int), "Timeout should be integer"
        assert timeout <= 10, "Linter should complete within 10 minutes"


class TestCIWorkflowSteps:
    """Test workflow steps configuration."""

    WORKFLOW_FILE = "cli-pattern-linter.yml"

    def test_workflow_checks_out_code(self):
        """RED: Workflow should check out repository code.
        
        First step should use actions/checkout.
        
        This test will FAIL until checkout step is added.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get('jobs', {})
        job = list(jobs.values())[0] if jobs else {}
        steps = job.get('steps', [])
        
        assert len(steps) > 0, "Job should have steps"
        
        # Check for checkout step
        has_checkout = any('checkout' in str(step.get('uses', '')).lower() 
                          for step in steps)
        assert has_checkout, "Workflow should checkout code"

    def test_workflow_sets_up_python(self):
        """RED: Workflow should set up Python.
        
        Should use actions/setup-python with appropriate version.
        
        This test will FAIL until Python setup step is added.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get('jobs', {})
        job = list(jobs.values())[0] if jobs else {}
        steps = job.get('steps', [])
        
        # Check for Python setup step
        has_python_setup = any('setup-python' in str(step.get('uses', '')).lower() 
                               for step in steps)
        assert has_python_setup, "Workflow should set up Python"

    def test_workflow_installs_dependencies(self):
        """RED: Workflow should install Python dependencies.
        
        Should install requirements.txt for linter to work.
        
        This test will FAIL until dependency install step is added.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get('jobs', {})
        job = list(jobs.values())[0] if jobs else {}
        steps = job.get('steps', [])
        
        # Check for pip install step
        has_install = any(
            'pip install' in str(step.get('run', '')).lower()
            or 'requirements.txt' in str(step.get('run', '')).lower()
            for step in steps
        )
        assert has_install, "Workflow should install dependencies"

    def test_workflow_runs_linter_with_correct_flags(self):
        """RED: Workflow should run linter with --all and --fail-on-violations.
        
        Command should be:
        python development/scripts/cli_pattern_linter.py --all --format json --fail-on-violations
        
        This test will FAIL until linter step is correctly configured.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get('jobs', {})
        job = list(jobs.values())[0] if jobs else {}
        steps = job.get('steps', [])
        
        # Find linter step
        linter_steps = [
            step for step in steps
            if 'cli_pattern_linter' in str(step.get('run', '')).lower()
        ]
        
        assert len(linter_steps) > 0, "Workflow should run cli_pattern_linter.py"
        
        linter_step = linter_steps[0]
        run_cmd = linter_step.get('run', '')
        
        assert '--all' in run_cmd, "Linter should use --all flag"
        assert '--fail-on-violations' in run_cmd, (
            "Linter should use --fail-on-violations flag"
        )
        assert '--format json' in run_cmd or '--format=json' in run_cmd, (
            "Linter should use JSON format for CI"
        )


class TestCIWorkflowIntegration:
    """Test overall workflow integration."""

    WORKFLOW_FILE = "cli-pattern-linter.yml"

    def test_workflow_provides_helpful_job_name(self):
        """RED: Job should have descriptive name visible in PR checks.
        
        Name appears in GitHub PR check status.
        
        This test will FAIL until job name is set.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get('jobs', {})
        job = list(jobs.values())[0] if jobs else {}
        
        assert 'name' in job, "Job should have a name"
        
        job_name = job['name'].lower()
        assert len(job_name) > 5, "Job name should be descriptive"
        assert 'cli' in job_name or 'lint' in job_name or 'pattern' in job_name, (
            "Job name should describe CLI linting"
        )

    def test_workflow_step_names_are_clear(self):
        """RED: Workflow steps should have clear names.
        
        Names help debugging when CI fails.
        
        This test will FAIL until step names are added.
        """
        workflow_path = WORKFLOWS_DIR / self.WORKFLOW_FILE
        
        if not workflow_path.exists():
            pytest.skip("Workflow file doesn't exist yet")
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get('jobs', {})
        job = list(jobs.values())[0] if jobs else {}
        steps = job.get('steps', [])
        
        # All steps should have names
        unnamed_steps = [step for step in steps if 'name' not in step]
        assert len(unnamed_steps) == 0, (
            f"All steps should have names. Found {len(unnamed_steps)} unnamed steps."
        )
        
        # Names should be descriptive
        for step in steps:
            name = step.get('name', '')
            assert len(name) > 5, f"Step name should be descriptive: '{name}'"
