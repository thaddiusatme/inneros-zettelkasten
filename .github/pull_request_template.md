# Pull Request

## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code quality improvement (refactoring, lint fixes, etc.)

## Related Issues

<!-- Link to related issues. Use "Fixes #123" or "Closes #123" for auto-closing -->

Fixes #

## Testing

### Local Testing Checklist

- [ ] `make lint` passes (ruff + black)
- [ ] `make type` passes (pyright) or explains type issues
- [ ] `make unit` passes (all unit tests)
- [ ] `make test` full suite passes

### Test Coverage

<!-- Describe what tests were added/updated -->

- [ ] Added new tests for new functionality
- [ ] Updated existing tests for changed functionality
- [ ] Test coverage maintained or improved

## Code Quality

### TDD Compliance (if applicable)

- [ ] RED Phase: Tests written first (failing tests)
- [ ] GREEN Phase: Minimal implementation to pass tests
- [ ] REFACTOR Phase: Code cleanup and optimization
- [ ] Zero regressions: Existing tests still pass

### Documentation

- [ ] Code comments added/updated where needed
- [ ] Documentation updated (README, HOWTO, ADRs, etc.)
- [ ] Docstrings added/updated for new functions/classes

## Safety Checks

- [ ] No hardcoded credentials or sensitive data
- [ ] No breaking changes to existing APIs (or documented if necessary)
- [ ] Backward compatibility maintained (or migration path provided)
- [ ] No new warnings introduced

## Checklist for Reviewers

<!-- Reviewers: Please verify these items -->

- [ ] Code follows project style guidelines
- [ ] Changes are well-tested and documented
- [ ] No obvious security vulnerabilities
- [ ] CI checks pass (automated in GitHub Actions)
- [ ] Commit messages follow convention

## Screenshots/Output (if applicable)

<!-- Add screenshots or command output demonstrating the changes -->

```
# Example: Output from make test
```

## Additional Notes

<!-- Any additional context, concerns, or questions for reviewers -->

---

**Post-v0.1.0-beta Quality Gates:** This PR must pass all CI checks before merging.
