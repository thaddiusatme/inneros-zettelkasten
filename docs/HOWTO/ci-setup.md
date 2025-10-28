# CI Setup Guide

**Last Updated**: 2025-10-27  
**Status**: Production Ready (Post v0.1.0-beta)

## Overview

The CI workflow (`.github/workflows/ci.yml`) provides automated quality gates for all pull requests and pushes to main/develop branches. This ensures code quality is maintained post-beta release.

## What Gets Checked

### 1. Linting (Ruff + Black)
- **Ruff**: Fast Python linter checking for errors (E), warnings (F), and code quality (W)
- **Black**: Code formatter ensuring consistent style
- **Exit Code**: CI fails if any lint errors found

### 2. Type Checking (Pyright)
- Static type analysis for Python code
- Currently set to `continue-on-error: true` (optional)
- Will be enforced once type coverage improves

### 3. Unit Tests
- All tests in `development/tests/unit/`
- Must pass with exit code 0
- Coverage report uploaded as artifact

## Running Locally

Before pushing, run the same checks locally:

```bash
# Full test suite (what CI runs)
make test

# Individual stages
make lint    # Ruff + Black
make type    # Pyright (optional)
make unit    # Unit tests only
```

## CI Workflow Triggers

The CI workflow runs on:
- Pull requests targeting `main` or `develop`
- Direct pushes to `main` or `develop`

## Debugging CI Failures

### Lint Errors
```bash
# See exact errors
make lint

# Auto-fix formatting
python3 -m black development/src development/tests
```

### Type Errors
```bash
# Run locally (requires pyright)
make type

# Type errors are warnings only for now
```

### Test Failures
```bash
# Run specific test file
PYTHONPATH=development pytest development/tests/unit/test_file.py -v

# Run with coverage
make cov
```

## GitHub Actions Configuration

### Runner: macOS-latest
- Matches developer environment (macOS)
- Python 3.13 installed via setup-python action
- Uses pip cache for faster runs

### Dependencies
Installed via `requirements.txt` + additional dev tools:
- `ruff` - Fast linter
- `black` - Code formatter  
- `pyright` - Type checker
- `pytest` + `pytest-cov` - Testing framework

## Status Badges

Add to README.md:
```markdown
![CI Status](https://github.com/thaddiusatme/inneros-zettelkasten/workflows/CI%20-%20Quality%20Gates/badge.svg)
```

## Troubleshooting

### "No module named X" errors
- Check `requirements.txt` includes all dependencies
- Verify virtual environment activated in CI steps

### Timeout Issues
- Most jobs complete in < 5 minutes
- Contact maintainer if consistent timeouts occur

### Permission Errors
- Ensure `.github/workflows/` directory has proper permissions
- Check GitHub Actions are enabled in repo settings

## Next Steps (P1 Enhancements)

1. **Nightly Coverage Job**: Scheduled coverage reports with trend analysis
2. **CodeQL Security Scanning**: Automated vulnerability detection
3. **Pre-commit Hooks**: Local validation before commit
4. **Branch Protection**: Require CI pass before merge

## References

- **Makefile**: Defines `test`, `lint`, `type`, `unit` targets
- **Rules**: `.windsurf/rules/updated-development-workflow.md`
- **Workflow**: `.github/workflows/ci.yml`
