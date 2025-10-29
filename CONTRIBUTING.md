# Contributing to InnerOS Zettelkasten

Thank you for your interest in contributing! This document provides guidelines and best practices for contributing to this project.

## 🎯 Quick Start

1. **Fork & Clone**: Fork the repo and clone your fork
2. **Set up Environment**: Run setup commands (see below)
3. **Create Branch**: Use descriptive branch names
4. **Make Changes**: Follow our coding standards
5. **Test**: Ensure all tests pass
6. **Submit PR**: Use our PR template

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+ (3.13 recommended)
- Git
- GitHub account

### Initial Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/inneros-zettelkasten.git
cd inneros-zettelkasten

# Create virtual environment
cd development
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r ../requirements.txt
pip install ruff black pyright pytest pytest-cov

# Verify setup
cd ..
make test  # Should pass all checks
```

## 📋 Development Workflow

### 1. Create a Branch

Use descriptive branch names following these patterns:

- `feat/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/what-changed` - Documentation updates
- `chore/task-description` - Maintenance tasks
- `test/what-testing` - Test additions/fixes

### 2. Follow TDD Methodology

We use Test-Driven Development (TDD). See `.windsurf/rules/updated-development-workflow.md` for detailed guidance.

**TDD Cycle**:
1. **RED**: Write failing tests first
2. **GREEN**: Implement minimal code to pass
3. **REFACTOR**: Improve code quality
4. **COMMIT**: Document changes
5. **LESSONS**: Record insights

### 3. Code Quality Standards

#### Linting & Formatting
```bash
make lint   # Run ruff + black checks
make type   # Run pyright type checking
```

All code must pass:
- **ruff**: Linting (E, F, W rules)
- **black**: Code formatting
- **pyright**: Type checking (optional but encouraged)

#### Testing
```bash
make unit   # Run unit tests
make cov    # Run with coverage report
```

Requirements:
- All new features must have tests
- Maintain or improve coverage
- Tests must be fast (<5s per test file)

### 4. Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Test changes
- `chore`: Maintenance
- `refactor`: Code restructuring

**Example**:
```
feat(workflow): Add orphaned note detection

- Implement bidirectional link graph analysis
- Add detection for notes with zero connections  
- Include CLI integration with export options

Closes #42
```

## 🧪 Testing Guidelines

### Writing Tests

```python
"""
Test module docstring explaining what's being tested.
"""

def test_feature_does_something_specific():
    """Test that feature behaves correctly in normal case."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = feature_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

### Test Organization
- Unit tests in `development/tests/unit/`
- Integration tests in `development/tests/integration/`
- Use descriptive test names
- One assertion per test when possible
- Mock external dependencies

## 📝 Pull Request Process

### Before Submitting

- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make lint`)
- [ ] Coverage maintained/improved
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### PR Checklist

Our PR template includes:

**Type of Change**:
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Testing**:
- [ ] Unit tests added/updated
- [ ] All tests passing locally
- [ ] Coverage report reviewed

**Quality**:
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated

### Review Process

1. **Automated Checks**: CI must pass (lint, type, tests)
2. **Code Review**: At least one approval required
3. **Discussion**: Address all comments
4. **Merge**: Squash and merge when approved

## 🏗️ Architecture Guidelines

### File Organization

```
development/
├── src/
│   ├── ai/           # AI/LLM integrations
│   ├── automation/   # Background tasks
│   └── cli/          # Command-line tools
├── tests/
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
└── venv/             # Virtual environment
```

### Code Style

- **Functions**: Snake_case, descriptive names
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Private**: Leading underscore `_private_method()`
- **Line Length**: 100 characters (black default)

### Dependencies

- Keep `requirements.txt` minimal
- Pin versions for stability
- Document why each dependency is needed
- Prefer standard library when possible

## 🐛 Reporting Bugs

Use our bug report template (`.github/ISSUE_TEMPLATE/bug_report.md`):

1. Clear, descriptive title
2. Steps to reproduce
3. Expected vs actual behavior
4. Environment details
5. Logs/screenshots if applicable

## 💡 Suggesting Features

Use our feature request template:

1. Problem statement
2. Proposed solution
3. Alternatives considered
4. Additional context

## 📚 Additional Resources

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [CLI-REFERENCE.md](CLI-REFERENCE.md) - Command reference
- [.windsurf/rules/](. windsurf/rules/) - Development methodology

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Unprofessional conduct

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## ❓ Questions?

- Open a GitHub issue with the "question" label
- Check existing issues and discussions
- Review documentation in `docs/` directory

---

**Thank you for contributing to InnerOS Zettelkasten!** Your efforts help make this a better tool for everyone.
