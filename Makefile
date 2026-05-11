.PHONY: setup lint format type test test-fast test-unit unit unit-all integ cov run review fleeting inbox inbox-safe smoke clean-venv

# Venv configuration - ensures reproducible tooling
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
SYSTEM_PYTHON ?= python3

VAULT ?= knowledge

# ============================================
# USER COMMANDS (daily vault maintenance)
# ============================================

review:
	@echo "📋 Generating weekly review..."
	PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py --vault $(VAULT) weekly-review --preview

fleeting:
	@echo "📊 Checking fleeting notes health..."
	PYTHONPATH=development python3 development/src/cli/fleeting_cli.py --vault $(VAULT) fleeting-health

inbox:
	@echo "📥 Processing unprocessed inbox notes..."
	PYTHONPATH=development python3 -c "from src.ai.batch_inbox_processor import batch_process_unprocessed_inbox; from pathlib import Path; import json, sys; r = batch_process_unprocessed_inbox(Path('$(VAULT)/Inbox')); print(json.dumps(r, indent=2)); sys.exit(1 if r.get('errors', 0) > 0 else 0)"

inbox-safe:
	@echo "📥 [DRY-RUN] Scanning inbox (no changes will be made)..."
	PYTHONPATH=development python3 -c "from src.ai.batch_inbox_processor import batch_process_unprocessed_inbox; from pathlib import Path; import json, sys; r = batch_process_unprocessed_inbox(Path('$(VAULT)/Inbox'), dry_run=True); print(json.dumps(r, indent=2)); sys.exit(1 if r.get('errors', 0) > 0 else 0)"

smoke:
	@echo "🔥 Running usability smoke test..."
	@echo "--- Step 1/2: Weekly review preview ---"
	@$(MAKE) review
	@echo "--- Step 2/2: Fleeting health ---"
	@$(MAKE) fleeting
	@echo "✅ Smoke test complete."

# ============================================
# DEV COMMANDS (for development only)
# ============================================

# Bootstrap venv (idempotent - only creates if missing)
$(VENV)/bin/activate:
	@echo "📦 Creating virtual environment..."
	$(SYSTEM_PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r dev-requirements.txt
	@echo "✅ Virtual environment ready at $(VENV)"

setup: $(VENV)/bin/activate
	@echo "✅ Setup complete. Use 'make lint' to check code."

lint: $(VENV)/bin/activate
	$(PYTHON) -m ruff check development/src development/tests --select E,F,W --ignore E402,E501,E712,W291,W293,F401,F841
	$(PYTHON) -m black --check development/src development/tests

format: $(VENV)/bin/activate
	@echo "🔧 Auto-formatting code..."
	$(PYTHON) -m ruff check --fix development/src development/tests --select E,F,W --ignore E402,E501,E712,W291,W293,F401,F841
	$(PYTHON) -m black development/src development/tests
	@echo "✅ Formatting complete."

type: $(VENV)/bin/activate
	$(PYTHON) -m pyright development/src || true

clean-venv:
	@echo "🧹 Removing virtual environment..."
	rm -rf $(VENV)
	@echo "✅ Virtual environment removed. Run 'make setup' to recreate."

test-fast: $(VENV)/bin/activate
	PYTHONPATH=development $(PYTHON) -m pytest -n auto -q --timeout=300 --tb=short --strict-markers -o addopts= -m "ci and not wip and not slow" development/tests/unit

test-unit: $(VENV)/bin/activate
	PYTHONPATH=development $(PYTHON) -m pytest -n auto -q --timeout=300 -o addopts= -m "not wip and not slow" development/tests/unit

unit: $(VENV)/bin/activate
	PYTHONPATH=development $(PYTHON) -m pytest -q --timeout=300 --tb=short --strict-markers -o addopts= -m "ci and not wip and not slow" development/tests/unit

unit-all: $(VENV)/bin/activate
	PYTHONPATH=development $(PYTHON) -m pytest -q --timeout=300 -o addopts= development/tests/unit

integ: $(VENV)/bin/activate
	PYTHONPATH=development $(PYTHON) -m pytest -q development/tests/integration

cov: $(VENV)/bin/activate
	PYTHONPATH=development $(PYTHON) -m pytest --cov=development/src --cov-report=term-missing -m "not wip" --ignore=development/demos development/tests/unit

test: lint type unit

run:
	PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py weekly-review
