# TDD Iteration 1: DevEx/Makefile venv + reproducible lint

**Date**: 2025-12-16
**Duration**: ~20 minutes
**Branch**: `feat/devex-makefile-venv`
**Commit**: `3f5033f`
**Status**: ✅ **COMPLETE** - All acceptance criteria met

## Problem Statement

`make lint` failed on macOS with `No module named ruff` because the Makefile used bare `python3` which resolved to Homebrew's Python 3.14, which had no dev tools installed globally.

## Solution

Created a project-local `.venv` with pinned dev tooling, making `make lint` reproducible regardless of system python version.

## TDD Cycle Summary

### RED Phase (9 failing tests)

Created `development/tests/unit/devex/test_makefile_venv.py` with 12 tests:
- `TestMakefileVenvConfiguration`: 7 tests for Makefile structure
- `TestDevRequirementsFile`: 5 tests for pinned dependencies

### GREEN Phase (12/12 passing)

Minimal implementation:
1. Created `dev-requirements.txt` with pinned versions (ruff, black, pyright, pytest)
2. Added Makefile variables: `VENV := .venv`, `PYTHON := $(VENV)/bin/python`
3. Added `$(VENV)/bin/activate:` bootstrap target (idempotent)
4. Updated `lint:` and `type:` to depend on venv and use `$(PYTHON)`

### REFACTOR Phase

Extended venv usage to all dev commands for consistency:
- `unit`, `unit-all`, `integ`, `cov` now use `$(PYTHON)`
- All dev targets depend on `$(VENV)/bin/activate`

## Deliverables

| File | Lines | Purpose |
|------|-------|---------|
| `Makefile` | +19/-17 | Venv variables, bootstrap target, updated commands |
| `dev-requirements.txt` | +12 | Pinned dev tooling |
| `development/tests/unit/devex/test_makefile_venv.py` | +110 | TDD test suite |

## Key Decisions

1. **Separate dev-requirements.txt**: Keeps dev tools separate from runtime deps
2. **Idempotent bootstrap**: `$(VENV)/bin/activate:` only runs if venv missing
3. **User commands unchanged**: `up/down/status/review/fleeting` still use system python (intentional - they should work without dev setup)
4. **SYSTEM_PYTHON variable**: Allows override via `make setup SYSTEM_PYTHON=python3.11`

## Acceptance Criteria Met

- ✅ On a clean machine, `make setup && make lint` succeeds without global installs
- ✅ `make lint` uses `.venv` regardless of system python version
- ✅ Running `make lint` before setup auto-bootstraps venv

## Discovered Issues

**Pre-commit hooks also broken**: The existing `.git/hooks/pre-commit` uses system python and fails for the same reason. This is a follow-up task (P1) - consider updating pre-commit to use the venv or removing the hooks.

## Next Steps

1. **P1-USABILITY**: Add `make smoke` for core daily command validation
2. **P1-HOOKS**: Update pre-commit hooks to use venv (or document `--no-verify` workaround)
3. **Merge**: Create PR and merge to main

## Key Learnings

1. **TDD for DevEx works well**: Tests caught exactly what we needed to implement
2. **Idempotent targets**: Using file existence (`$(VENV)/bin/activate:`) as dependency makes setup idempotent
3. **Separation of concerns**: User commands vs dev commands can have different python requirements
4. **Pre-commit hooks are fragile**: They depend on the same tooling and need the same fix
