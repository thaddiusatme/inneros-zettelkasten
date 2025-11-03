# InnerOS Automation System

This directory contains automation scripts and configuration for the InnerOS Zettelkasten + AI workflow system.

## Vault Configuration Integration

**All automation scripts are compatible with the centralized vault configuration system** introduced in Phase 2 of GitHub Issue #45.

### How Scripts Use Vault Configuration

Scripts automatically handle the `knowledge/` subdirectory structure through two integration patterns:

1. **Python Scripts**: Import from `development/src` which uses vault config internally
   - Paths like `knowledge/Inbox/`, `knowledge/Permanent Notes/` resolved automatically
   - No hardcoded paths - all paths relative to repository root
   - Compatible with vault config `VaultConfig.get_inbox_path()`, etc.

2. **Shell Scripts**: Call Python CLI tools or use relative paths from repo root
   - All cron jobs execute with `cd` to repo root first
   - Scripts accept path arguments for flexibility
   - No environment variables required (INBOX_DIR, etc.)

### Migration Status

**✅ Zero migration required** - All 20 automation scripts verified compatible (as of 2025-11-03):

- 8 Python scripts: Use `development/src` imports (vault config aware)
- 12 Shell scripts: Use relative paths or call compatible CLI tools
- 4 Cron jobs: All configured correctly with repo root context
- 0 Issues found: No hardcoded paths, fully compatible

**See**: `Projects/ACTIVE/p1-vault-12-script-verification-report.md` for detailed verification results.

### Path Structure

Scripts work with this directory layout:

```text
knowledge/
  ├── Inbox/                    # Quick captures, pending triage
  ├── Fleeting Notes/           # In-progress ideas
  ├── Permanent Notes/          # Processed knowledge
  ├── Literature Notes/         # Source summaries
  └── Archive/                  # Completed/deprecated notes
```

### Best Practices for Custom Scripts

When creating new automation scripts:

1. **Python Scripts**: Import from `development/src` for vault config access

   ```python
   from development.src.utils.vault_config import VaultConfig
   
   vault = VaultConfig()
   inbox_path = vault.get_inbox_path()  # Returns: knowledge/Inbox
   ```

2. **Shell Scripts**: Use relative paths from repo root

   ```bash
   cd "$(git rev-parse --show-toplevel)"
   INBOX_DIR="knowledge/Inbox"
   ```

3. **Cron Jobs**: Always `cd` to repo root before execution

   ```bash
   cd "/path/to/inneros-zettelkasten" && ./script.sh
   ```

## Directory Structure

- `scripts/`: Python automation scripts
- `hooks/`: Git hooks for validation and automation
- `config/`: Configuration files
- `logs/`: Automation logs
- `reports/`: Generated reports

## Components

### 1. Metadata Validation

The system validates YAML frontmatter in markdown files according to the schema defined in the project manifest.

#### Configuration

The validation parameters are defined in `config/metadata_config.yaml`. You can modify this file to adjust:

- Valid note types
- Valid statuses
- Valid visibility options
- Required fields
- Type-specific required fields
- Date formats

#### Usage

The validation script is automatically run as a pre-commit hook when committing changes to Git. It checks all staged markdown files for valid metadata.

You can also run the validation script manually:

```bash
python3 .automation/scripts/validate_metadata.py path/to/your/note.md
```

### 2. Git Hooks

The system uses Git hooks to automate validation and other tasks:

- `pre-commit`: Validates metadata in markdown files before committing

## Adding New Automation Components

To add new automation components:

1. Add scripts to the `scripts/` directory
2. Update configuration in the `config/` directory
3. Create or modify Git hooks in the `hooks/` directory
4. Document changes in the Windsurf Project Changelog

## Best Practices

- All scripts should be non-destructive and preserve original content
- Use configuration files for adjustable parameters
- Log all actions to the `logs/` directory
- Generate reports in the `reports/` directory
- Document all changes in the Windsurf Project Changelog
