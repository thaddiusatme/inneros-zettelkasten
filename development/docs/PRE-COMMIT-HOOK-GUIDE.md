# Pre-commit Hook Guide - CLI Pattern Linter

## Overview

The CLI pattern linter pre-commit hook automatically validates CLI argument patterns before each commit, preventing non-compliant code from entering the repository.

**Benefits**:
- ✅ Instant feedback on CLI pattern violations
- ✅ Prevents commits with non-compliant CLIs
- ✅ Enforces standards documented in `CLI-ARGUMENT-STANDARDS.md`
- ✅ Catches issues before code review
- ✅ Maintains codebase quality automatically

---

## Installation

### Quick Install

```bash
./development/scripts/install-pre-commit-hook.sh
```

This will:
1. Back up any existing pre-commit hook
2. Install the CLI linter hook
3. Make the hook executable
4. Display configuration instructions

### Manual Install

```bash
# Copy hook to .git/hooks
cp development/scripts/pre-commit-hook.sh .git/hooks/pre-commit

# Make executable
chmod +x .git/hooks/pre-commit
```

---

## How It Works

### Automatic Execution

The hook runs automatically when you execute:

```bash
git commit -m "your message"
```

### What Gets Checked

The hook only validates files that are:
1. **Staged for commit** (via `git add`)
2. **Python files** (*.py)
3. **Located in** `development/src/cli/`

Other files are ignored, so the hook won't slow down non-CLI commits.

### Validation Checks

For each CLI file, the hook validates:

1. **--vault Flag Presence** (workflow CLIs only)
   - Ensures workflow CLIs have `--vault` flag
   - Reports if missing

2. **Help Text Completeness**
   - `ArgumentParser` must have `description`
   - `ArgumentParser` must have `epilog` with examples

3. **Argument Naming Conventions**
   - Use lowercase-with-hyphens (`--dry-run`)
   - Not underscores (`--dry_run` ❌)
   - Not camelCase (`--dryRun` ❌)

4. **Boolean Flag Patterns**
   - Boolean flags use `action='store_true'` or `action='store_false'`
   - Not `type=bool` (confusing behavior)

---

## Example Output

### Clean Commit (No Violations)

```bash
$ git commit -m "Add new feature"
🔍 Checking CLI argument patterns...
  Checking: my_workflow_cli.py
  ✓ No violations
✓ All CLI files pass argument pattern checks
[feat/my-feature abc1234] Add new feature
 1 file changed, 25 insertions(+)
```

### Blocked Commit (Violations Found)

```bash
$ git commit -m "Add incomplete CLI"
🔍 Checking CLI argument patterns...
  Checking: my_cli.py
  ✗ Violations found

============================================================
File: development/src/cli/my_cli.py
============================================================

⚠️  Found 2 violations:

1. [missing_description]
   ArgumentParser should have description
   💡 Add: ArgumentParser(description='...')

2. [missing_epilog]
   ArgumentParser should have epilog with examples
   💡 Add: ArgumentParser(epilog='Examples:\n  ...')

Summary:
  Total checks: 4
  Violations: 2
  Compliance: 50.0%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ Commit blocked: CLI argument pattern violations found
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please fix the violations above, or:
  • Review the CLI Argument Standards: development/docs/CLI-ARGUMENT-STANDARDS.md
  • Run linter manually: python development/scripts/cli_pattern_linter.py <file>
  • Bypass hook (not recommended): git commit --no-verify
```

---

## Bypassing the Hook

### When to Bypass

You should **rarely** bypass the hook. Valid reasons include:
- Emergency hotfix where standards will be fixed in follow-up PR
- WIP commit that will be squashed before merge
- False positive (report issue and bypass temporarily)

### How to Bypass

Use the `--no-verify` flag:

```bash
git commit --no-verify -m "WIP: incomplete CLI"
```

**⚠️ Warning**: Bypassing the hook may introduce technical debt.

---

## Configuration

### Config File Location

Create `.cli-lint-config.json` in repository root:

```bash
touch .cli-lint-config.json
```

### Sample Configuration

```json
{
  "enabled": true,
  "checks": {
    "vault_flag": true,
    "help_text": true,
    "naming": true,
    "boolean_flags": true
  },
  "excluded_files": [
    "development/src/cli/legacy_cli.py"
  ]
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable hook entirely |
| `checks.vault_flag` | boolean | `true` | Check for --vault flag |
| `checks.help_text` | boolean | `true` | Validate help text completeness |
| `checks.naming` | boolean | `true` | Check naming conventions |
| `checks.boolean_flags` | boolean | `true` | Validate boolean flag patterns |
| `excluded_files` | array | `[]` | List of files to skip (relative paths) |

### Disable Hook Temporarily

```json
{
  "enabled": false
}
```

Then commit the config:

```bash
git add .cli-lint-config.json
git commit -m "chore: temporarily disable CLI linter"
```

**Remember to re-enable** after your work is complete!

---

## Troubleshooting

### Hook Not Running

**Check installation**:

```bash
ls -l .git/hooks/pre-commit
# Should show: -rwxr-xr-x ... pre-commit
```

**Reinstall if needed**:

```bash
./development/scripts/install-pre-commit-hook.sh
```

### Hook Reports False Positives

**Run linter manually** to investigate:

```bash
python development/scripts/cli_pattern_linter.py development/src/cli/your_file.py
```

**Report issue**:
1. Create GitHub issue with false positive example
2. Temporarily bypass with `--no-verify`
3. Fix in follow-up PR once linter is updated

### Linter Script Not Found

**Ensure linter exists**:

```bash
ls -l development/scripts/cli_pattern_linter.py
# Should exist and be executable
```

**If missing**, pull latest from main branch:

```bash
git fetch origin
git checkout origin/main -- development/scripts/cli_pattern_linter.py
```

### Hook Slows Down Commits

The hook is designed to be fast:
- Only checks staged CLI files
- Skips non-CLI files
- Uses efficient AST parsing
- Typical execution: <1 second

**If slow**, check:
1. Number of staged CLI files (should be small per commit)
2. Python version (3.8+ recommended)
3. Disk I/O performance

---

## Uninstallation

### Remove Hook

```bash
rm .git/hooks/pre-commit
```

### Restore Previous Hook

If you had a hook before installation:

```bash
mv .git/hooks/pre-commit.backup .git/hooks/pre-commit
```

---

## Development

### Testing the Hook

Run the test suite:

```bash
cd development
pytest tests/unit/automation/test_pre_commit_hook.py -v
```

**Tests validate**:
- Installation process
- Execution on clean files
- Blocking on violations
- File filtering (CLI files only)
- Output formatting
- Configuration respect

### Modifying the Hook

**Hook location**: `development/scripts/pre-commit-hook.sh`

**After modifications**:

1. Reinstall hook
2. Run tests
3. Test manually with sample commits

```bash
# Reinstall
./development/scripts/install-pre-commit-hook.sh

# Test
pytest tests/unit/automation/test_pre_commit_hook.py

# Manual test
echo "test change" >> development/src/cli/test_file.py
git add development/src/cli/test_file.py
git commit -m "test hook"
git reset HEAD~1  # Undo test commit
```

---

## Best Practices

### For Developers

1. **Fix violations immediately** when hook blocks commit
2. **Don't bypass habitually** - hook is there to help
3. **Use `--no-verify` sparingly** and document why
4. **Report false positives** so linter can be improved
5. **Keep CLI standards doc handy** for reference

### For Teams

1. **Install hook** on all developer machines
2. **Include hook check** in CI/CD pipeline
3. **Document exceptions** in .cli-lint-config.json
4. **Review bypassed commits** in code review
5. **Update standards doc** as patterns evolve

### For Maintainers

1. **Keep linter updated** with new patterns
2. **Add tests** for new validation rules
3. **Monitor false positive rate** (should be ~0%)
4. **Document hook behavior** in team onboarding
5. **Version hook** alongside CLI standards doc

---

## Related Documentation

- **CLI Argument Standards**: `development/docs/CLI-ARGUMENT-STANDARDS.md`
- **Linter Documentation**: `development/scripts/cli_pattern_linter.py`
- **Test Suite**: `development/tests/unit/automation/test_pre_commit_hook.py`

---

## Support

**Questions or Issues**:
1. Check this guide first
2. Review CLI standards documentation
3. Run linter manually for details
4. Create GitHub issue with:
   - Hook output
   - File being checked
   - Expected vs actual behavior

---

**Last Updated**: 2025-11-07  
**Hook Version**: 1.0.0  
**Requires**: Python 3.8+, cli_pattern_linter.py
