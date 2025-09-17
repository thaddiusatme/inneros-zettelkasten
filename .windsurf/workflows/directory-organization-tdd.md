---
description: Safety-First Directory Organization - TDD Implementation Workflow
---

# Safety-First Directory Organization - TDD Implementation

This workflow guides systematic implementation of the directory organization project using Test-Driven Development methodology.

## Prerequisites

1. Review project specification in `Projects/project-todo-v2.md`
2. Ensure current working directory is `/Users/thaddius/repos/inneros-zettelkasten`
3. Verify Python development environment is active

## Phase 1: P0 Safety Infrastructure

### Step 1: User Story P0-1 - Backup System

#### TDD Red Phase
```bash
# Create failing test first
mkdir -p development/tests/unit/utils
touch development/tests/unit/utils/test_directory_organizer.py

# Write failing test for backup system
pytest development/tests/unit/utils/test_directory_organizer.py::test_create_timestamped_backup -v
```

Expected: Test should fail (backup system not implemented yet)

#### TDD Green Phase
```bash
# Create minimal implementation
mkdir -p development/src/utils
touch development/src/utils/directory_organizer.py

# Implement just enough to pass the test
pytest development/tests/unit/utils/test_directory_organizer.py::test_create_timestamped_backup -v
```

Expected: Test should pass with minimal implementation

#### TDD Refactor Phase
```bash
# Improve code quality and architecture
# Add error handling, documentation, type hints
pytest development/tests/unit/utils/ -v
```

Expected: All tests pass with clean implementation

#### Git Commit
```bash
git add -A
git commit -m "feat(directory): backup system with rollback

- Add timestamped backup creation to /backups/knowledge-YYYYMMDD-HHMMSS/
- Implement rollback capability
- Full test coverage for backup operations
- Preserves all files, hidden files, and symlinks

Addresses User Story P0-1"
```

### Step 2: User Story P0-2 - Dry Run System

#### TDD Red Phase
```bash
# Add failing test for dry run functionality
pytest development/tests/unit/utils/test_directory_organizer.py::test_dry_run_preview -v
```

#### TDD Green Phase
```bash
# Implement dry run with JSON/Markdown output
pytest development/tests/unit/utils/test_directory_organizer.py::test_dry_run_preview -v
```

#### TDD Refactor Phase
```bash
# Ensure no file mutations in dry run mode
pytest development/tests/unit/utils/ -v
```

#### Git Commit
```bash
git commit -m "feat(directory): dry run preview system

- Add JSON/Markdown table output for proposed moves
- Guarantee zero file mutations in dry run mode
- Journal logging with file hashes
- Preview current_path → target_path mappings

Addresses User Story P0-2"
```

### Step 3: User Story P0-3 - Link Preservation Engine

#### TDD Red Phase
```bash
# Add failing tests for link scanning and preservation
pytest development/tests/unit/utils/test_directory_organizer.py::test_scan_wiki_links -v
```

#### TDD Green Phase
```bash
# Implement link scanning for all variants: [[Note]], [[Note|alias]], [[Note#Heading]], ![[Embed]]
pytest development/tests/unit/utils/test_directory_organizer.py::test_scan_wiki_links -v
```

#### TDD Refactor Phase
```bash
# Validate before/after link updates
pytest development/tests/unit/utils/ -v
```

#### Git Commit
```bash
git commit -m "feat(directory): link preservation engine

- Scan all wiki-link variants: [[Note]], [[Note|alias]], [[Note#Heading]], ![[Embed]]
- Update references when files move directories
- Dry run shows before/after link preview
- Validation ensures 0 broken links

Addresses User Story P0-3"
```

## Phase 2: P1 Core Logic (After P0 Complete)

### Step 4: User Story P1-1 - Directory Organizer

Follow same TDD pattern:
- Red: Failing test for type-based file movement
- Green: Implement movement logic (permanent → Permanent Notes/, etc.)
- Refactor: Handle unknown types, error cases
- Commit: `feat(directory): type-based file organizer`

### Step 5: User Story P1-2 - Validation System

Follow same TDD pattern:
- Red: Failing test for post-move validation
- Green: Implement link integrity checking
- Refactor: Add auto-rollback on validation failure
- Commit: `feat(directory): post-move validation with rollback`

## Phase 3: P2 Integration (After P1 Complete)

### Steps 6-7: Weekly Review & Maintenance

Follow same TDD pattern for remaining user stories.

## Safety Checklist (Every Step)

- [ ] Backup created before any file operations
- [ ] Dry run executed and reviewed
- [ ] All tests passing
- [ ] No file destruction, only moves
- [ ] Link integrity maintained
- [ ] Rollback tested and working

## Lessons Learned Template

After each user story, document in `Projects/`:
```markdown
## User Story [ID] - [Name] - Lessons Learned

### What Worked Well
- [List successes]

### Challenges Encountered  
- [List difficulties and solutions]

### Code Quality Insights
- [Architecture/design observations]

### Next Iteration Improvements
- [What to do differently next time]
```

## Emergency Rollback

If any issues occur:
```bash
# Use backup system created in P0-1
python3 development/src/utils/directory_organizer.py --rollback /backups/knowledge-YYYYMMDD-HHMMSS/
```

## Validation Commands

```bash
# Run full test suite
PYTHONPATH=development pytest development/tests/ -v

# Check link integrity
python3 development/src/utils/directory_organizer.py --validate-links

# Generate project status report  
python3 development/src/cli/workflow_demo.py . --enhanced-metrics
```
