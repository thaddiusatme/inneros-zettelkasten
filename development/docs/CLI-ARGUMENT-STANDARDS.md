# CLI Argument Standards

**Purpose**: Comprehensive standards for CLI argument patterns, naming conventions, backward compatibility, and testing requirements. This document serves as the definitive guide for all CLI development in InnerOS Zettelkasten.

**Last Updated**: 2025-11-07  
**Status**: Production Standard

---

## Table of Contents

1. [Standard Argument Naming Conventions](#standard-argument-naming-conventions)
2. [Required vs Optional Arguments](#required-vs-optional-arguments)
3. [Backward Compatibility Guidelines](#backward-compatibility-guidelines)
4. [Help Text Formatting](#help-text-formatting)
5. [Error Message Standards](#error-message-standards)
6. [CLI Testing Requirements](#cli-testing-requirements)
7. [CLI Examples by Type](#cli-examples-by-type)

---

## Standard Argument Naming Conventions

All CLI tools must follow consistent naming patterns for arguments. This ensures predictable interfaces and reduces cognitive load for users.

## Core Patterns

### Vault Path Argument (REQUIRED for workflow CLIs)

**Standard Pattern**: `--vault` flag (recommended)

```python
import argparse

def create_parser():
    parser = argparse.ArgumentParser()
    
    # Standard --vault flag pattern
    parser.add_argument(
        "--vault",
        dest="vault_path_flag",
        help="Path to the Zettelkasten vault root directory (recommended)",
    )
    
    # Optional: positional argument for backward compatibility
    parser.add_argument(
        "vault_path",
        nargs="?",
        help="Path to vault (DEPRECATED: use --vault flag instead)",
    )
    
    return parser
```

**Implementation Examples**:

- ✅ `core_workflow_cli.py` - Uses `--vault` flag with positional fallback
- ✅ `safe_workflow_cli.py` - Standard `--vault` flag pattern

### Common Argument Names

| Argument | Pattern | Purpose | Example |
|----------|---------|---------|---------|
| Vault path | `--vault PATH` | Vault root directory | `--vault /path/to/vault` |
| Output format | `--format {normal,json}` | Control output format | `--format json` |
| Dry run | `--dry-run` | Preview without changes | `--dry-run` |
| Export | `--export PATH` | Export to file | `--export report.json` |
| Progress | `--progress` | Show progress | `--progress` |
| Verbose | `--verbose` or `-v` | Verbose output | `-v` or `--verbose` |

### Naming Rules

1. **Use lowercase with hyphens**: `--dry-run`, `--export-path`, `--quality-threshold`
2. **Boolean flags use action="store_true"**: No value required
3. **Path arguments use metavar**: `--export PATH` (shows in help)
4. **Choices use explicit list**: `choices=["normal", "json"]`

---

## Required vs Optional Arguments

Clear distinction between required and optional arguments improves usability and error messages.

## Argument Categories

### Required Arguments

**Positional arguments** for essential operation parameters:

```python
# Example: Note path is required for promotion
parser.add_argument("note_path", help="Path to note to promote")
parser.add_argument(
    "target_type",
    choices=["permanent", "literature"],
    help="Target type for promotion",
)
```

### Optional Arguments with Defaults

**Flags and options** with sensible defaults:

```python
# Format flag with default
parser.add_argument(
    "--format",
    choices=["normal", "json"],
    default="normal",
    help="Output format (default: normal)",
)

# Quality threshold with default
parser.add_argument(
    "--quality-threshold",
    type=float,
    default=0.7,
    help="Minimum quality score (0.0-1.0, default: 0.7)",
)
```

### Optional Flags

**Boolean flags** for optional behavior:

```python
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Preview changes without modifying files",
)

parser.add_argument(
    "--progress",
    action="store_true",
    help="Show progress during processing",
)
```

## Validation Best Practices

1. **Validate early**: Check required args before processing
2. **Provide defaults**: All optional args should have sensible defaults
3. **Type conversion**: Use `type=` parameter for automatic conversion
4. **Choices validation**: Use `choices=` for restricted options

---

## Backward Compatibility Guidelines

Maintaining backward compatibility during transitions prevents breaking existing automation scripts and user workflows.

## Deprecation Strategy

### Phase 1: Add New Pattern (Dual Support)

Support both old and new patterns simultaneously:

```python
def create_parser():
    parser = argparse.ArgumentParser()
    
    # NEW: Recommended --vault flag
    parser.add_argument(
        "--vault",
        dest="vault_path_flag",
        help="Path to vault (recommended)",
    )
    
    # OLD: Positional argument (deprecated but supported)
    parser.add_argument(
        "vault_path",
        nargs="?",
        help="Path to vault (DEPRECATED: use --vault flag instead)",
    )
    
    return parser
```

### Phase 2: Add Deprecation Warning

Warn users about deprecated patterns:

```python
def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle both patterns with deprecation warning
    vault_path = args.vault_path_flag or args.vault_path or "."
    
    if args.vault_path and not args.vault_path_flag:
        print("⚠️  DEPRECATION WARNING: Positional vault_path is deprecated.")
        print("    Use --vault flag instead: --vault /path/to/vault")
        print("    Positional argument support will be removed in future version.")
        print()
    
    # Continue with normal operation
    cli = MyCLI(vault_path)
```

### Phase 3: Migration Timeline

1. **Week 1-2**: Deploy dual support (both patterns work)
2. **Week 3-6**: Show deprecation warnings
3. **Week 7-8**: Update documentation and automation scripts
4. **Week 9+**: Remove old pattern (after validation)

## Migration Checklist

- [ ] Add new pattern alongside old pattern
- [ ] Add deprecation warning for old pattern
- [ ] Update automation scripts to use new pattern
- [ ] Update documentation with examples
- [ ] Validate both patterns work correctly
- [ ] Monitor for usage of old pattern
- [ ] Remove old pattern after 4+ weeks

---

## Help Text Formatting

Consistent help text improves discoverability and usability.

## Structure

### Main Program Help

```python
parser = argparse.ArgumentParser(
    description="Core Workflow CLI - Essential workflow operations",
    epilog="""
Examples:
  # Show workflow status
  python core_workflow_cli.py --vault /path/to/vault status
  
  # Process all inbox notes
  python core_workflow_cli.py --vault /path/to/vault process-inbox
  
  # Promote a note
  python core_workflow_cli.py --vault /path/to/vault promote note.md permanent
    """,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
```

### Subcommand Help

```python
# Status command
status_parser = subparsers.add_parser(
    "status",
    help="Show workflow status",
    description="Display current workflow status including note counts and AI feature adoption",
)
```

### Argument Help

```python
parser.add_argument(
    "--quality-threshold",
    type=float,
    default=0.7,
    help="Minimum quality score (0.0-1.0) required for auto-promotion (default: 0.7)",
)
```

## Help Text Rules

1. **Be concise but complete**: One line summary + details if needed
2. **Show defaults**: Always indicate default values
3. **Use examples**: Provide usage examples in epilog
4. **Indicate deprecation**: Mark deprecated args clearly
5. **Specify ranges**: Show valid ranges for numeric args

---

## Error Message Standards

Error messages should be actionable and user-friendly.

## Error Message Structure

```text
❌ ERROR: [Brief description of what went wrong]

   [More detailed explanation if needed]
   
   💡 SUGGESTION: [Actionable fix user can take]
   
   Example:
     [Concrete example of correct usage]
```

## Implementation Pattern

```python
def validate_vault_path(vault_path: str) -> None:
    """Validate vault path exists and is accessible."""
    path = Path(vault_path)
    
    if not path.exists():
        print(f"❌ ERROR: Vault path does not exist: {vault_path}")
        print()
        print("   The specified vault directory was not found.")
        print()
        print("   💡 SUGGESTION: Check the path and try again")
        print()
        print("   Example:")
        print("     python cli.py --vault /path/to/vault command")
        print()
        sys.exit(1)
    
    if not path.is_dir():
        print(f"❌ ERROR: Vault path is not a directory: {vault_path}")
        print()
        print("   💡 SUGGESTION: Provide a directory path, not a file")
        print()
        sys.exit(1)
```

## Error Message Guidelines

1. **Use clear symbols**: ❌ for errors, ⚠️ for warnings, 💡 for suggestions
2. **Explain the problem**: What went wrong and why
3. **Provide solutions**: Always suggest next steps
4. **Show examples**: Concrete examples of correct usage
5. **Exit cleanly**: Use appropriate exit codes (1 for errors)

---

## CLI Testing Requirements

All CLIs must have comprehensive test coverage including both unit tests and integration tests.

## Testing Levels

### Unit Tests

Test individual CLI functions and argument parsing:

```python
import pytest
import argparse

def test_parser_accepts_vault_flag():
    """Test that parser accepts --vault flag"""
    from src.cli.core_workflow_cli import create_parser
    
    parser = create_parser()
    
    # Should parse without error
    args = parser.parse_args(["--vault", "/tmp/test", "status"])
    
    assert args.vault_path_flag == "/tmp/test"
    assert args.command == "status"
```

### Integration Tests

Test actual CLI execution using subprocess:

```python
import subprocess
import sys
from pathlib import Path

def test_cli_help_output():
    """Test CLI help output is correct"""
    cli_path = Path(__file__).parent.parent / "src" / "cli" / "core_workflow_cli.py"
    
    result = subprocess.run(
        [sys.executable, str(cli_path), "--help"],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert "--vault" in result.stdout
    assert "status" in result.stdout  # Subcommand visible
```

### Smoke Tests

Validate basic CLI functionality in CI:

```python
def test_cli_status_command_executes():
    """Smoke test: status command runs without error"""
    cli_path = Path(__file__).parent.parent / "src" / "cli" / "core_workflow_cli.py"
    
    result = subprocess.run(
        [sys.executable, str(cli_path), "--vault", ".", "status"],
        capture_output=True,
        text=True,
    )
    
    # Should complete without error
    assert result.returncode == 0
```

## Test Coverage Requirements

- **Unit tests**: 100% coverage of argument parsing logic
- **Integration tests**: All major commands tested end-to-end
- **Smoke tests**: Fast validation in CI pipeline
- **Backward compat**: Test both old and new argument patterns

## Test Organization

```text
development/tests/
├── unit/
│   └── cli/
│       └── test_core_workflow_cli.py
├── integration/
│   └── test_cli_integration.py
└── smoke/
    └── test_cli_smoke.py
```

---

## CLI Examples by Type

Different CLI types follow specific patterns. Use these templates for new CLIs.

## Workflow CLI Pattern

**Example**: `core_workflow_cli.py`

```python
#!/usr/bin/env python3
"""Core Workflow CLI - Essential workflow operations"""

import sys
import argparse
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.workflow_manager import WorkflowManager

class CoreWorkflowCLI:
    def __init__(self, vault_path: str = "."):
        self.vault_path = vault_path
        self.workflow_manager = WorkflowManager(base_directory=vault_path)
    
    def status(self, output_format: str = "normal") -> int:
        """Show workflow status"""
        # Implementation
        return 0

def create_parser():
    parser = argparse.ArgumentParser(
        description="Core Workflow CLI"
    )
    
    # Standard --vault flag
    parser.add_argument("--vault", dest="vault_path_flag")
    parser.add_argument("vault_path", nargs="?")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command")
    
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--format", choices=["normal", "json"], default="normal")
    
    return parser

def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle vault path with deprecation warning
    vault_path = args.vault_path_flag or args.vault_path or "."
    
    if args.vault_path and not args.vault_path_flag:
        print("⚠️  DEPRECATION WARNING: Use --vault flag")
        print()
    
    # Execute command
    cli = CoreWorkflowCLI(vault_path)
    
    if args.command == "status":
        return cli.status(args.format)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Analysis CLI Pattern

**Example**: Analysis and reporting tools

```python
def create_parser():
    parser = argparse.ArgumentParser(
        description="Analysis CLI - Generate reports and metrics"
    )
    
    # Vault path
    parser.add_argument("--vault", required=True)
    
    # Report type
    parser.add_argument(
        "--report-type",
        choices=["summary", "detailed", "metrics"],
        default="summary",
    )
    
    # Export option
    parser.add_argument("--export", metavar="PATH", help="Export to file")
    
    # Output format
    parser.add_argument("--format", choices=["normal", "json"], default="normal")
    
    return parser
```

## Backup CLI Pattern

**Example**: `safe_workflow_cli.py` backup commands

```python
def create_backup_parser(subparsers):
    backup_parser = subparsers.add_parser(
        "backup",
        help="Create timestamped backup of vault",
    )
    
    backup_parser.add_argument(
        "--format",
        choices=["normal", "json"],
        default="normal",
        help="Output format",
    )
    
    return backup_parser
```

---

## Quick Reference

### Checklist for New CLI

- [ ] Use `--vault` flag for vault path (required for workflow CLIs)
- [ ] Support both `--vault` and positional for backward compatibility
- [ ] Add deprecation warning for positional vault_path
- [ ] Use standard argument names (`--format`, `--dry-run`, `--export`)
- [ ] Provide comprehensive help text with examples
- [ ] Implement actionable error messages
- [ ] Write unit tests for argument parsing
- [ ] Write integration tests for command execution
- [ ] Add smoke tests for CI pipeline
- [ ] Update this document with new patterns

### References

- **Implementation examples**: `core_workflow_cli.py`, `safe_workflow_cli.py`
- **Test examples**: `tests/unit/automation/test_cli_argument_standardization.py`
- **Integration tests**: `tests/integration/test_cli_integration.py`

---

**Last Updated**: 2025-11-07  
**Maintainer**: InnerOS Development Team  
**Version**: 1.0.0
