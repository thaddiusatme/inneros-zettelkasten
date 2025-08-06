# Development Directory

## 🛠️ InnerOS Zettelkasten - Development Environment

This directory contains all development artifacts, source code, tests, and technical documentation for the InnerOS Zettelkasten AI-enhanced knowledge management system.

## 📁 Directory Structure

```
development/
├── src/                    # Python source code (AI, workflows, CLI)
├── tests/                  # Comprehensive test suites
├── docs/                   # Technical documentation
├── demos/                  # CLI demonstration tools
├── pytest.ini             # Test configuration
└── requirements.txt       # Python dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Ollama (for AI features)
- Git

### Installation
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests (from development directory)
python3 -m pytest tests/

# Or run tests from project root
PYTHONPATH=development python3 -m pytest development/tests/

# Run demos using new unified CLI (from project root)
../inneros analytics --interactive
../inneros workflow --status

# Or run demos directly (from development directory)
python3 src/cli/analytics_demo.py ../knowledge/ --interactive
```

## 🔧 Development Workflow

1. **TDD First**: Always write tests before code
2. **Run Tests**: `python3 -m pytest tests/`
3. **Check Coverage**: `python3 -m pytest --cov=src tests/`
4. **Validate CLI**: Test CLI tools work from this directory

## 📊 Key Components

- **AI Engine**: `src/ai/` - Core AI processing and workflows
- **CLI Tools**: `src/cli/` - User-facing commands and demos
- **Tests**: `tests/` - Unit, integration, and end-to-end tests

## 🎯 Development Guidelines

See `../.windsurf/windsurfrules.md` for comprehensive development rules and guidelines.
