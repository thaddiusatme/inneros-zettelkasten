.PHONY: setup lint format type test test-fast test-unit unit unit-all integ cov run review fleeting inbox inbox-safe smoke clean-venv backup

# Venv configuration - ensures reproducible tooling
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
SYSTEM_PYTHON ?= python3

VAULT ?= knowledge

# ============================================
# USER COMMANDS (daily vault maintenance)
# ============================================

INNEROS := PYTHONPATH=development python3 development/src/cli/inneros.py

review:
	@echo "📋 Generating weekly review..."
	$(INNEROS) --vault $(VAULT) review --preview

fleeting:
	@echo "📊 Checking fleeting notes health..."
	$(INNEROS) --vault $(VAULT) fleeting health

backup:
	@echo "📦 Creating vault backup..."
	$(INNEROS) --vault $(VAULT) backup

inbox: backup
	@echo "📥 Processing unprocessed inbox notes..."
	$(INNEROS) --vault $(VAULT) inbox

inbox-safe:
	@echo "📥 [DRY-RUN] Scanning inbox (no changes will be made)..."
	$(INNEROS) --vault $(VAULT) inbox --dry-run

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
	@if grep -rn "sys\.path\.insert\|sys\.path\.append" development/src/ --include="*.py" 2>/dev/null | grep -v "^Binary"; then \
		echo "❌ sys.path mutation banned in development/src/ — use PYTHONPATH=development or pip install -e development/"; \
		exit 1; \
	fi

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
	$(INNEROS) --vault $(VAULT) review
