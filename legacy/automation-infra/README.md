# InnerOS Automation System

This directory contains automation scripts and configuration for the InnerOS Zettelkasten + AI workflow system.

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
